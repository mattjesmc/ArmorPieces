package com.mattjesmc.armorpieces.decoration;

import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.decoration.fitting.FittingValue;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.LinkedHashMap;
import java.util.Map;
import net.minecraft.core.Holder;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.equipment.EquipmentAsset;
import net.minecraft.world.item.equipment.trim.MaterialAssetGroup;
import net.minecraft.world.item.equipment.trim.TrimMaterial;
import org.jspecify.annotations.Nullable;

/**
 * One decorative part in one socket, in one material, with whatever sits in its fittings - the value
 * half of the {@link ArmorDecorations} map, and the exact analogue of a whole {@link
 * net.minecraft.world.item.equipment.trim.ArmorTrim}.
 *
 * <p>The material is vanilla's own {@link TrimMaterial} holder, not a parallel type of ours. That
 * single decision is what "fully integrated with the trims and materials" cashes out to: every trim
 * material that exists - the vanilla eleven, and any a datapack adds tomorrow - is already a valid
 * decoration material, with its palette, its display name, its colour and its per-armor darker
 * variants inherited rather than re-declared. A part is coloured by the same ingot that colours a
 * trim, and looks like it belongs.
 *
 * <p>The fittings are the part's second materials: the gem set in the circlet, the dye in the sash.
 * Keyed by the fitting itself, valued by whatever that fitting stores, and read through the
 * fitting's own codec so that the entry never has to know the shape of a value - see
 * {@link Fitting#valueCodec()}. On disk an entry with no fittings is exactly the entry that existed
 * before fittings did, because the field is optional, which is why every item decorated so far still
 * reads. On the wire it is not: the stream codec has no optional fields and writes the map either
 * way, so an unfitted part costs an empty compound it did not cost before. That is a cost paid
 * between this mod's own client and server in the same version, where nothing has to interoperate
 * across the change.
 *
 * @param fittings what is set in each of the part's fittings. Only fittings the part declares mean
 *                 anything; a key the part does not list is carried but never drawn.
 */
public record DecorationEntry(
    Holder<TrimMaterial> material,
    Holder<ArmorDecoration> decoration,
    Map<Holder<Fitting>, FittingValue> fittings
) {
    /**
     * Each value is decoded through the codec its key's fitting supplies - the one map codec shape
     * that lets a mod's fitting type store a value this mod cannot name.
     */
    public static final Codec<Map<Holder<Fitting>, FittingValue>> FITTINGS_CODEC =
        Codec.dispatchedMap(Fitting.CODEC, fitting -> fitting.value().valueCodec());

    public static final Codec<DecorationEntry> CODEC = RecordCodecBuilder.create(
        i -> i.group(
                TrimMaterial.CODEC.fieldOf("material").forGetter(DecorationEntry::material),
                ArmorDecoration.CODEC.fieldOf("decoration").forGetter(DecorationEntry::decoration),
                FITTINGS_CODEC.optionalFieldOf("fittings", Map.of()).forGetter(DecorationEntry::fittings)
            )
            .apply(i, DecorationEntry::new)
    );
    public static final StreamCodec<RegistryFriendlyByteBuf, DecorationEntry> STREAM_CODEC = StreamCodec.composite(
        TrimMaterial.STREAM_CODEC, DecorationEntry::material,
        ArmorDecoration.STREAM_CODEC, DecorationEntry::decoration,
        // Through NBT: the values are of open shape, so their stream codec is their codec.
        ByteBufCodecs.fromCodecWithRegistries(FITTINGS_CODEC), DecorationEntry::fittings,
        DecorationEntry::new
    );

    public DecorationEntry {
        fittings = Map.copyOf(fittings);
    }

    /** A part with nothing in its fittings - the entry a socket that was empty gets. */
    public DecorationEntry(final Holder<TrimMaterial> material, final Holder<ArmorDecoration> decoration) {
        this(material, decoration, Map.of());
    }

    /**
     * This part in this material, keeping from {@code previous} - whatever the socket held before -
     * everything sitting in a fitting the new part also declares. The entry the apply recipe writes.
     *
     * <p>A socket is re-applied for two ordinary reasons: to change a part's material, and to swap
     * the part. Building a bare entry for either would destroy what is set in it, so re-applying the
     * circlet in gold would take the emerald with it - and, since the bare entry differs from the old
     * one, the no-op guard would not even refuse the craft. What the incoming part has a place for
     * survives; what it does not goes with the part it belonged to, since a value under a fitting the
     * part does not declare is never drawn or listed again.
     *
     * <p>The order is the new part's own fitting order, not the old entry's, so the tooltip reads the
     * same as it would for a piece fitted from scratch.
     */
    public static DecorationEntry applying(
        final Holder<TrimMaterial> material,
        final Holder<ArmorDecoration> decoration,
        final @Nullable DecorationEntry previous
    ) {
        if (previous == null || previous.fittings.isEmpty()) {
            return new DecorationEntry(material, decoration);
        }
        final var kept = new LinkedHashMap<Holder<Fitting>, FittingValue>();
        for (final Holder<Fitting> fitting : decoration.value().fittings()) {
            final FittingValue value = previous.fittings.get(fitting);
            if (value != null) {
                kept.put(fitting, value);
            }
        }
        return new DecorationEntry(material, decoration, kept);
    }

    /**
     * The suffix naming this material's art for this particular armor piece, exactly as a trim's
     * sprite suffix is resolved.
     *
     * <p>Going through {@link MaterialAssetGroup#assetId} rather than just the material's base name
     * is what buys the darker-variant behaviour for free - gold decoration on gold armor picks
     * {@code gold_darker} exactly as a gold trim on gold armor does, so a part never vanishes into
     * the piece it sits on.
     *
     * <p>A suffix rather than a finished texture path, because a part no longer HAS a texture per
     * material: it ships one greyscale master that is coloured through the material's own vanilla
     * palette at load time. Choosing between that, a hand-authored per-material override and the
     * palette to colour with is the client's business - see
     * {@code com.mattjesmc.armorpieces.client.texture.DecorationTextureManager}.
     */
    public String materialSuffix(final ResourceKey<EquipmentAsset> equipmentAsset) {
        return this.material.value().assets().assetId(equipmentAsset).suffix();
    }

    /** What is set in {@code fitting}, or {@code null} if it is empty. */
    public @Nullable FittingValue fitting(final Holder<Fitting> fitting) {
        return this.fittings.get(fitting);
    }

    /** This entry with {@code fitting} set to {@code value}, replacing whatever it held. */
    public DecorationEntry withFitting(final Holder<Fitting> fitting, final FittingValue value) {
        final var copy = new LinkedHashMap<>(this.fittings);
        copy.put(fitting, value);
        return new DecorationEntry(this.material, this.decoration, copy);
    }

    /** This entry with {@code fitting} emptied. */
    public DecorationEntry withoutFitting(final Holder<Fitting> fitting) {
        if (!this.fittings.containsKey(fitting)) {
            return this;
        }
        final var copy = new LinkedHashMap<>(this.fittings);
        copy.remove(fitting);
        return new DecorationEntry(this.material, this.decoration, copy);
    }
}
