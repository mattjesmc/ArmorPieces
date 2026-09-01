package com.mattjesmc.armorpieces.decoration;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.Holder;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.equipment.EquipmentAsset;
import net.minecraft.world.item.equipment.trim.MaterialAssetGroup;
import net.minecraft.world.item.equipment.trim.TrimMaterial;

/**
 * One decorative part in one socket, in one material - the value half of the
 * {@link ArmorDecorations} map, and the exact analogue of a whole {@link
 * net.minecraft.world.item.equipment.trim.ArmorTrim}.
 *
 * <p>The material is vanilla's own {@link TrimMaterial} holder, not a parallel type of ours. That
 * single decision is what "fully integrated with the trims and materials" cashes out to: every trim
 * material that exists - the vanilla eleven, and any a datapack adds tomorrow - is already a valid
 * decoration material, with its palette, its display name, its colour and its per-armor darker
 * variants inherited rather than re-declared. A part is coloured by the same ingot that colours a
 * trim, and looks like it belongs.
 */
public record DecorationEntry(Holder<TrimMaterial> material, Holder<ArmorDecoration> decoration) {
    public static final Codec<DecorationEntry> CODEC = RecordCodecBuilder.create(
        i -> i.group(
                TrimMaterial.CODEC.fieldOf("material").forGetter(DecorationEntry::material),
                ArmorDecoration.CODEC.fieldOf("decoration").forGetter(DecorationEntry::decoration)
            )
            .apply(i, DecorationEntry::new)
    );
    public static final StreamCodec<RegistryFriendlyByteBuf, DecorationEntry> STREAM_CODEC = StreamCodec.composite(
        TrimMaterial.STREAM_CODEC, DecorationEntry::material,
        ArmorDecoration.STREAM_CODEC, DecorationEntry::decoration,
        DecorationEntry::new
    );

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

}
