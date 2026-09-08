package com.mattjesmc.armorpieces.cloth;

import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.DecorationLoot;
import com.mattjesmc.armorpieces.decoration.fitting.builtin.BannerFitting;
import com.mattjesmc.armorpieces.identity.Identified;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.List;
import java.util.Optional;
import net.minecraft.core.Holder;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.ComponentSerialization;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.RegistryFileCodec;

/**
 * A cloth - the fourth kind of template, and the fourth thing that can be said about one piece of
 * armor: a PIECE is geometry hung on the body, a TRIM is vanilla's accent painted over the armor's
 * texture, a SKIN is the armor's own texture, and a cloth is a garment worn over that texture,
 * dyed and patterned at a loom.
 *
 * <p>Where it sits is the whole design. A cloth is composited INTO the armor's own texture, so it is
 * the armor model: it moves with the armor, clips nothing, and needs no rig of its own. And the
 * layering falls out for free - over the skin, because the skin is the pixels it is composited onto;
 * under every part, because parts are an appended render layer that draws after the whole equipment
 * stack; under the trim, because the trim is a later pass in the same method.
 *
 * <p>Lives in the {@code armorpieces:cloth} dynamic registry, so a datapack adds a garment by
 * dropping {@code data/<ns>/armorpieces/cloth/<name>.json}. As with a part or a skin, nothing about
 * it is compiled in: the art is one greyscale CUT MASK per sheet found from {@link #assetId}, and
 * the recipe that hands out its template is itself a datapack file.
 *
 * <p><b>The colour comes from a banner, not from the cloth.</b> A cloth ships no colour at all - the
 * mask says where the garment is and how it folds, and everything the player chose arrives on the
 * banner laid in the smithing table's addition slot. Two files per cloth, therefore, rather than two
 * per material: an armor material this mod has never heard of wears it for free, because the only
 * thing wanted from it is a texture it already ships.
 *
 * @param assetId    names both masks:
 *                   {@code assets/<ns>/textures/entity/cloth/<path>/humanoid.png} and
 *                   {@code .../humanoid_leggings.png}. A cloth with no mask for a sheet is not an
 *                   error: it is a garment that does not reach that far - which is how a tabard is
 *                   short and a tunic is long.
 * @param sheet      which of vanilla's two pattern sprite sets the panels sample, the same choice
 *                   {@link BannerFitting} offers and for the same reason: a design painted for a
 *                   20x40 flag and one painted for a 12x22 plate do not read the same stretched over
 *                   an 8x12 torso panel. {@code shield} is the closer proportion and the default.
 * @param description the cloth's name in tooltips and on its template.
 * @param loot       where the cloth's template turns up in the world, if anywhere - the same list a
 *                   part and a skin carry, read by the same code.
 */
public record Cloth(
    Identifier assetId,
    BannerFitting.Sheet sheet,
    Component description,
    List<DecorationLoot> loot,
    List<Identifier> formerIds,
    Optional<String> uid
) implements Identified {
    public static final Codec<Cloth> DIRECT_CODEC = RecordCodecBuilder.create(
        i -> i.group(
                Identifier.CODEC.fieldOf("asset_id").forGetter(Cloth::assetId),
                BannerFitting.Sheet.CODEC
                    .optionalFieldOf("sheet", BannerFitting.Sheet.SHIELD).forGetter(Cloth::sheet),
                ComponentSerialization.CODEC.fieldOf("description").forGetter(Cloth::description),
                DecorationLoot.LIST_CODEC.optionalFieldOf("loot", List.of()).forGetter(Cloth::loot),
                Identifier.CODEC.listOf()
                    .optionalFieldOf("former_ids", List.of()).forGetter(Cloth::formerIds),
                Codec.STRING.optionalFieldOf("uid").forGetter(Cloth::uid)
            )
            .apply(i, Cloth::new)
    );

    /** Synced for the reason skins are: the client is what bakes this, off an item component. */
    public static final StreamCodec<RegistryFriendlyByteBuf, Cloth> DIRECT_STREAM_CODEC = StreamCodec.composite(
        Identifier.STREAM_CODEC,
        Cloth::assetId,
        ByteBufCodecs.idMapper(i -> BannerFitting.Sheet.values()[i], BannerFitting.Sheet::ordinal),
        Cloth::sheet,
        ComponentSerialization.STREAM_CODEC,
        Cloth::description,
        DecorationLoot.STREAM_CODEC.apply(ByteBufCodecs.list()),
        Cloth::loot,
        Cloth::new
    );

    public static final Codec<Holder<Cloth>> CODEC =
        RegistryFileCodec.create(ArmorPiecesRegistries.CLOTH, DIRECT_CODEC);
    public static final StreamCodec<RegistryFriendlyByteBuf, Holder<Cloth>> STREAM_CODEC =
        ByteBufCodecs.holder(ArmorPiecesRegistries.CLOTH, DIRECT_STREAM_CODEC);

    public Cloth {
        loot = List.copyOf(loot);
        formerIds = List.copyOf(formerIds);
    }

    /** A garment that has never moved and has no lineage of its own - and the shape the wire uses. */
    public Cloth(
        final Identifier assetId,
        final BannerFitting.Sheet sheet,
        final Component description,
        final List<DecorationLoot> loot
    ) {
        this(assetId, sheet, description, loot, List.of(), Optional.empty());
    }

    /** {@code <ns>:textures/entity/cloth/<cloth>/<sheet>.png} - the cut mask for one sheet. */
    public Identifier mask(final String sheet) {
        return this.assetId.withPath(path -> "textures/entity/cloth/" + path + "/" + sheet + ".png");
    }
}
