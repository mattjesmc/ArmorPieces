package com.mattjesmc.armorpieces.skin;

import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.DecorationLoot;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.List;
import net.minecraft.core.Holder;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.ComponentSerialization;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.RegistryFileCodec;

/**
 * An armor skin - the third kind of template, and the third thing that can be said about one piece
 * of armor: a PIECE is geometry hung on the body, a TRIM is vanilla's accent painted over the
 * armor's texture, and a skin is <em>the armor's own texture</em>. Nothing here changes a
 * silhouette; the model, the trims and every part carry on exactly as they did.
 *
 * <p>Lives in the {@code armorpieces:armor_skin} dynamic registry, so a datapack adds a skin by
 * dropping {@code data/<ns>/armorpieces/armor_skin/<name>.json}. As with a part, nothing about it is
 * compiled in: the art is two greyscale sheets found from {@link #assetId}, and the recipe that
 * hands out its template is itself a datapack file.
 *
 * <p><b>The colour comes from the armor, not from the skin.</b> A skin ships ONE greyscale master
 * pair - {@code humanoid} and {@code humanoid_leggings}, 64x32 each, on the vanilla grid - and the
 * client recolours it through a ramp derived from the material's own vanilla texture, mixing that
 * texture's lighting back over the master. See {@link SkinBake} for the arithmetic and
 * {@code com.mattjesmc.armorpieces.client.texture.ArmorSkinTextureManager} for where it is run. Two
 * files per skin, therefore, rather than two per material - and an armor material this mod has never
 * heard of is skinned for free, because the only thing wanted from it is a texture it already ships.
 *
 * @param assetId    names both sheets: {@code assets/<ns>/textures/entity/skin/<path>/humanoid.png}
 *                   and {@code .../humanoid_leggings.png}. A pack may also ship a hand-authored
 *                   {@code .../humanoid_<material>.png} beside them, which wins over the bake for
 *                   that one material - the same escape hatch a part has.
 * @param description the skin's name in tooltips and on its template.
 * @param loot       where the skin's template turns up in the world, if anywhere - the same list a
 *                   part carries, read by the same code. A skin template in a chest is a whole look
 *                   for a whole suit, so the weights should be lower than a part's and the tables
 *                   fewer.
 *
 * <p>Deliberately NO material list and no per-material art: a skin that had to name the materials it
 * suits would go stale the moment a mod added one, and the ramp is derived rather than authored
 * precisely so that it cannot. Which armor may be skinned at all is a property of the ARMOR - it has
 * to say what reforges it - and is settled by
 * {@link com.mattjesmc.armorpieces.recipe.SmithingSkinRecipe}, not here.
 */
public record ArmorSkin(Identifier assetId, Component description, List<DecorationLoot> loot) {
    public static final Codec<ArmorSkin> DIRECT_CODEC = RecordCodecBuilder.create(
        i -> i.group(
                Identifier.CODEC.fieldOf("asset_id").forGetter(ArmorSkin::assetId),
                ComponentSerialization.CODEC.fieldOf("description").forGetter(ArmorSkin::description),
                DecorationLoot.LIST_CODEC.optionalFieldOf("loot", List.of()).forGetter(ArmorSkin::loot)
            )
            .apply(i, ArmorSkin::new)
    );

    /**
     * Synced for the reason parts are: the client draws this. It resolves a {@code Holder<ArmorSkin>}
     * straight off an item component to find the sheets to bake, and a client that could not name
     * the skin its own armor wears would render it unskinned.
     */
    public static final StreamCodec<RegistryFriendlyByteBuf, ArmorSkin> DIRECT_STREAM_CODEC = StreamCodec.composite(
        Identifier.STREAM_CODEC,
        ArmorSkin::assetId,
        ComponentSerialization.STREAM_CODEC,
        ArmorSkin::description,
        DecorationLoot.STREAM_CODEC.apply(ByteBufCodecs.list()),
        ArmorSkin::loot,
        ArmorSkin::new
    );

    public static final Codec<Holder<ArmorSkin>> CODEC =
        RegistryFileCodec.create(ArmorPiecesRegistries.ARMOR_SKIN, DIRECT_CODEC);
    public static final StreamCodec<RegistryFriendlyByteBuf, Holder<ArmorSkin>> STREAM_CODEC =
        ByteBufCodecs.holder(ArmorPiecesRegistries.ARMOR_SKIN, DIRECT_STREAM_CODEC);

    public ArmorSkin {
        loot = List.copyOf(loot);
    }

    /** {@code <ns>:textures/entity/skin/<skin>/<sheet><suffix>.png} - the master, or an override. */
    public Identifier sheet(final String sheet, final String suffix) {
        return this.assetId.withPath(path -> "textures/entity/skin/" + path + "/" + sheet + suffix + ".png");
    }
}
