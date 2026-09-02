package com.mattjesmc.armorpieces.decoration.fitting;

import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import java.util.Optional;
import java.util.Set;
import java.util.function.Function;
import net.minecraft.core.Holder;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.RegistryFileCodec;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.equipment.EquipmentAsset;

/**
 * A place on a part that takes a second thing: the stone in a circlet, the metal rim of a pauldron,
 * the cloth of a sash, the field of a banner.
 *
 * <p>A part is coloured by one trim material, and that has always been the whole of its appearance.
 * A fitting is the part's second material. Each one names a region of the part - a mask beside the
 * master, or a bone of the geometry - and a kind of item that may fill it, and the smithing table
 * offers an item to every part on the piece, filling the first fitting on each that accepts it: a gem
 * to the gemstone, an ingot to the guard, a dye to the inlay, a banner to the banner. The item
 * decides, so one template covers every fitting that will ever exist.
 *
 * <h2>Two registries, on the same split as effects</h2>
 *
 * <p>Fittings themselves are DATA, in the {@code armorpieces:fitting} dynamic registry: a pack drops
 * {@code data/<ns>/armorpieces/fitting/<name>.json} and a part lists the id in its {@code fittings}.
 * The four this mod ships ({@code gemstone}, {@code guard}, {@code inlay}, {@code banner}) are files a
 * pack can override or add beside - a pack that wants a "pommel" fitting taking any metal, or a
 * "plume" taking dye, writes a JSON and no Java.
 *
 * <p>Fitting TYPES - how a kind of fitting reads an item and colours a region - are code, in the
 * static {@code armorpieces:fitting_type} registry of {@link MapCodec}s, exactly as effect types are.
 * Three ship: a trim material behind a mask, a dye behind a mask, and a banner on a bone. A mod adds
 * a fourth through {@link Fittings#register}, and from then on any pack can name it.
 *
 * <h2>What a fitting type has to say</h2>
 *
 * <p>Two things the SERVER needs: which items fill it ({@link #accept}), and how to read and write
 * what it holds ({@link #valueCodec}). And one thing the CLIENT needs, which is how to draw it. For
 * that there are two doors: {@link Masked}, for the common case of a region of the part's texture
 * coloured at bake time, which needs no client code at all; and, for a fitting that draws its own
 * geometry, a renderer registered against the type on the client - see
 * {@code com.mattjesmc.armorpieces.client.fitting.FittingRenderers} - with {@link #replacedBones}
 * naming what it takes over from the part.
 */
public interface Fitting {
    /** {@code {"type": "<ns>:<fitting type>", ...}}, dispatched through the type registry. */
    Codec<Fitting> DIRECT_CODEC = ArmorPiecesRegistries.FITTING_TYPES
        .byNameCodec()
        .dispatch(Fitting::codec, Function.identity());
    Codec<Holder<Fitting>> CODEC = RegistryFileCodec.create(ArmorPiecesRegistries.FITTING, DIRECT_CODEC);
    /**
     * Fittings travel by id, and their definitions by NBT: a fitting holds a {@code HolderSet} of
     * materials and a display name, neither of which is worth a hand-written stream codec.
     */
    StreamCodec<RegistryFriendlyByteBuf, Holder<Fitting>> STREAM_CODEC =
        ByteBufCodecs.holder(ArmorPiecesRegistries.FITTING, ByteBufCodecs.fromCodecWithRegistries(DIRECT_CODEC));

    /** This fitting's type - its entry in {@code armorpieces:fitting_type}. Names it in JSON. */
    MapCodec<? extends Fitting> codec();

    /** The fitting's name in tooltips: "Gemstone", "Guard", "Inlay", "Banner". */
    Component description();

    /**
     * Reads and writes the value this fitting stores on an item. Looked up by the entry through the
     * fitting the value belongs to, which is what lets values be of any shape - see
     * {@link FittingValue}.
     */
    Codec<? extends FittingValue> valueCodec();

    /**
     * What this fitting takes from an item, or empty if the item does not fill it.
     *
     * <p>This is the routing rule the smithing table runs: every part on the piece is offered the
     * item, and on each the first fitting to accept it is the one that gets it. It must read only the
     * stack - a fitting that consulted the world here would make the recipe book lie.
     */
    Optional<FittingValue> accept(ItemStack stack);

    /**
     * Whether a value is of the kind this fitting stores. The guard against a component written by
     * hand that pairs a fitting with a value it cannot draw.
     */
    boolean holds(FittingValue value);

    /**
     * Bones of the part's geometry this fitting draws in place of, while it is filled.
     *
     * <p>Empty for a masked fitting, which colours the part's own texture and replaces nothing. A
     * fitting with its own renderer names what it takes over - the banner names its cloth - so the
     * part's normal pass omits those bones rather than drawing under the fitting and fighting it for
     * depth.
     */
    default Set<String> replacedBones() {
        return Set.of();
    }

    /**
     * A fitting that is a region of the part's texture, coloured at bake time.
     *
     * <p>The region is a mask: {@code <part>_<fitting>.png} beside the master, greyscale like it,
     * opaque where the fitting is. While the fitting is empty the mask is ignored and the master
     * shows through, so a part looks exactly as it did before it had fittings. While it is filled,
     * every mask pixel takes the mask's own value through the colour this method returns. Alpha is
     * still the master's - a mask pixel outside the silhouette is not drawn.
     *
     * <p>Implementing this is all a masked fitting has to do on the client. The baker does the rest.
     */
    interface Masked extends Fitting {
        /**
         * How to colour the mask for this value on this armor.
         *
         * @param asset the armor's equipment asset, for a material that darkens on its own metal -
         *              gold on gold - exactly as the part's own material does.
         */
        FittingColour colour(FittingValue value, ResourceKey<EquipmentAsset> asset);
    }
}
