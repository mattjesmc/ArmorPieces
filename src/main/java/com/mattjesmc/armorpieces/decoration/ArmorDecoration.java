package com.mattjesmc.armorpieces.decoration;

import com.mattjesmc.armorpieces.decoration.effect.DecorationEffect;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import net.minecraft.core.Holder;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.ComponentSerialization;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.RegistryFileCodec;
import net.minecraft.util.ExtraCodecs;
import net.minecraft.world.item.equipment.trim.ArmorTrim;

/**
 * A decorative part - the datapack-defined half of the system, and the direct counterpart to vanilla's
 * {@link net.minecraft.world.item.equipment.trim.TrimPattern}.
 *
 * <p>Lives in the {@code armorpieces:armor_decoration} dynamic registry, so a datapack adds a part by
 * dropping {@code data/<ns>/armorpieces/armor_decoration/<name>.json}. Nothing here is compiled in:
 * the geometry is looked up from resources by {@link #assetId}, the texture is derived from the same
 * id plus the material's suffix, and the recipe that applies it is itself a datapack file. A new part
 * is therefore three JSON files and a PNG, with no Java at all.
 *
 * @param assetId    names both halves of the part's appearance, exactly as a trim pattern's asset id
 *                   does. Geometry is read from {@code assets/<ns>/armorpieces/decoration/<path>.json};
 *                   the texture from {@code assets/<ns>/textures/entity/decoration/<path>_<material>.png}.
 *                   Splitting on the material suffix is what makes a part inherit the trim material
 *                   palette for free - see {@link DecorationEntry#texture()}.
 * @param description the part's name in tooltips. Styled with the material's colour when shown, so it
 *                   reads "Gold Plume" the way "Gold Sentry" does.
 * @param anchors    the sockets this part is allowed to occupy. Validated when a recipe applies it, so
 *                   a datapack cannot bolt a plume onto a boot. Usually one entry; a part designed to
 *                   work in several places (a spike that suits both crest and spurs) may list more.
 * @param effects    what the part DOES while it is worn, if anything. Empty for every part this mod
 *                   ships and for every part that is only meant to look like something, which is the
 *                   normal case - the field exists so that a part is allowed to be more than paint,
 *                   not so that it has to be. Each entry names a type from
 *                   {@code armorpieces:decoration_effect_type}, a registry any mod may add to; see
 *                   {@link com.mattjesmc.armorpieces.decoration.effect.DecorationEffects}.
 *
 * <p>There is deliberately no "flat overlay" field here, though the shape of the system invites one.
 * Painted-on detail that follows the armor's surface is precisely what a vanilla TRIM PATTERN already
 * is, and trim patterns are themselves datapack-extensible - so a second, weaker way to do the same
 * thing would only split where a pack author looks. Parts are for geometry; trims are for paint.
 */
public record ArmorDecoration(
    Identifier assetId,
    Component description,
    Set<DecorationAnchor> anchors,
    List<DecorationEffect> effects
) {
    public static final Codec<ArmorDecoration> DIRECT_CODEC = RecordCodecBuilder.create(
        i -> i.group(
                Identifier.CODEC.fieldOf("asset_id").forGetter(ArmorDecoration::assetId),
                ComponentSerialization.CODEC.fieldOf("description").forGetter(ArmorDecoration::description),
                ExtraCodecs.nonEmptyList(DecorationAnchor.CODEC.listOf())
                    .xmap(Set::copyOf, List::copyOf)
                    .fieldOf("anchors").forGetter(ArmorDecoration::anchors),
                DecorationEffect.LIST_CODEC.optionalFieldOf("effects", List.of()).forGetter(ArmorDecoration::effects)
            )
            .apply(i, ArmorDecoration::new)
    );
    /**
     * Effects travel with the part, and they have to.
     *
     * <p>They are behaviour, and behaviour runs on the server - so the tempting economy here is to
     * strip them on the wire. It would be wrong. Vanilla decides whether an entity may start gliding
     * inside {@code LivingEntity.canGlide}, which runs on BOTH sides: the client that does not know
     * its chestplate carries a glider never asks to take off, and the effect silently does nothing.
     * The same will be true of any future hook the client evaluates. So the client is told, and the
     * cost is the ordinary one every mod-added registry pays - a client without the mod that
     * registered an effect type cannot read the part, exactly as it could not draw it.
     */
    public static final StreamCodec<RegistryFriendlyByteBuf, ArmorDecoration> DIRECT_STREAM_CODEC = StreamCodec.composite(
        Identifier.STREAM_CODEC,
        ArmorDecoration::assetId,
        ComponentSerialization.STREAM_CODEC,
        ArmorDecoration::description,
        DecorationAnchor.STREAM_CODEC.apply(ByteBufCodecs.collection(HashSet::new)),
        ArmorDecoration::anchors,
        ByteBufCodecs.fromCodecWithRegistries(DecorationEffect.LIST_CODEC),
        ArmorDecoration::effects,
        ArmorDecoration::new
    );
    public static final Codec<Holder<ArmorDecoration>> CODEC =
        RegistryFileCodec.create(ArmorPiecesRegistries.ARMOR_DECORATION, DIRECT_CODEC);
    public static final StreamCodec<RegistryFriendlyByteBuf, Holder<ArmorDecoration>> STREAM_CODEC =
        ByteBufCodecs.holder(ArmorPiecesRegistries.ARMOR_DECORATION, DIRECT_STREAM_CODEC);

    public ArmorDecoration {
        anchors = Set.copyOf(anchors);
        effects = List.copyOf(effects);
    }

    /** Whether this part may be applied to the given socket. The recipe's guard rail. */
    public boolean fits(final DecorationAnchor anchor) {
        return this.anchors.contains(anchor);
    }

    /**
     * The part's name tinted with its material's colour, mirroring
     * {@link net.minecraft.world.item.equipment.trim.TrimPattern#copyWithStyle} so a decoration's
     * tooltip line is visually indistinguishable from a trim's - which is the point, since to the
     * player they are the same feature. See {@link ArmorTrim} for the line this parallels.
     */
    public Component copyWithStyle(final Holder<net.minecraft.world.item.equipment.trim.TrimMaterial> material) {
        return this.description.copy().withStyle(material.value().description().getStyle());
    }
}
