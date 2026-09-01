package com.mattjesmc.armorpieces.decoration;

import com.mojang.serialization.Codec;
import java.util.List;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.equipment.ArmorType;

/**
 * The decorative interfaces an armor piece exposes - the fixed sockets a decorative part can occupy.
 *
 * <p>This enum is the one part of the system that is deliberately NOT datapack-extensible, and the
 * reason is worth stating: an anchor is not data, it is a <i>place on the humanoid body</i>. Its
 * meaning is a parent {@link HumanoidPart} plus a transform, and a datapack that invented a new one
 * would be inventing a body part the model does not have. Parts, materials, geometry, textures and
 * recipes are all open (see {@link ArmorDecoration}); the sockets they plug into are closed. That
 * split is what keeps "expandable" from meaning "able to render into nowhere".
 *
 * <p>Anchors that read as a mirrored pair - pauldrons, vambraces, tassets, knees, spurs, greaves -
 * are ONE anchor with two {@link Attachment}s rather than a left and a right. A player applying
 * spaulders means both
 * shoulders; making them buy two smithing operations for one visual idea would be a worse system,
 * and it would let a half-decorated pair exist for no expressive gain.
 */
public enum DecorationAnchor implements StringRepresentable {
    // ---- Helmet -----------------------------------------------------------------------------
    /** Top of the skull, pointing up. The plume/feathering socket. */
    CREST("crest", ArmorType.HELMET,
        Attachment.of(HumanoidPart.HEAD, 0.0F, -8.0F, 0.0F)),
    /** Across the forehead, on the front face of the head. Circlets, visor ornaments. */
    BROW("brow", ArmorType.HELMET,
        Attachment.of(HumanoidPart.HEAD, 0.0F, -4.0F, -4.0F)),
    /** Both temples, mirrored. Horns, wings, ear guards. */
    HORNS("horns", ArmorType.HELMET,
        Attachment.of(HumanoidPart.HEAD, 4.0F, -5.0F, 0.0F),
        Attachment.mirrored(HumanoidPart.HEAD, -4.0F, -5.0F, 0.0F)),

    // ---- Chestplate -------------------------------------------------------------------------
    /** Both shoulders, mirrored, riding on the arms so they swing with them. Spaulders. */
    PAULDRONS("pauldrons", ArmorType.CHESTPLATE,
        Attachment.of(HumanoidPart.LEFT_ARM, 1.0F, 0.0F, 0.0F),
        Attachment.mirrored(HumanoidPart.RIGHT_ARM, -1.0F, 0.0F, 0.0F)),
    /** Upper back. Cape clasps, banner mounts, wing roots. */
    BACK("back", ArmorType.CHESTPLATE,
        Attachment.of(HumanoidPart.BODY, 0.0F, 2.0F, 2.0F)),
    /** Base of the throat, on the front of the chest. Gorgets, brooches, medallions. */
    COLLAR("collar", ArmorType.CHESTPLATE,
        Attachment.of(HumanoidPart.BODY, 0.0F, 1.0F, -2.0F)),
    /**
     * Both forearms, mirrored, riding on the arms. Vambraces, bracers, wrist wraps.
     *
     * <p>The chestplate owns this because the chestplate is what covers the arm. Offset x = 1 is the
     * arm box's own X centre - the box spans local -1..3 - which is the same choice {@link
     * #PAULDRONS} makes at the shoulder; y = 6 is the forearm, four units below the elbow and clear
     * of the pauldron's reach.
     */
    VAMBRACES("vambraces", ArmorType.CHESTPLATE,
        Attachment.of(HumanoidPart.LEFT_ARM, 1.0F, 6.0F, 0.0F),
        Attachment.mirrored(HumanoidPart.RIGHT_ARM, -1.0F, 6.0F, 0.0F)),

    // ---- Leggings ---------------------------------------------------------------------------
    /** Waistline, at the bottom of the torso. Belts, sashes, buckles. */
    BELT("belt", ArmorType.LEGGINGS,
        Attachment.of(HumanoidPart.BODY, 0.0F, 10.0F, 0.0F)),
    /** Both hips, mirrored, riding on the legs. Tassets, thigh plates. */
    TASSETS("tassets", ArmorType.LEGGINGS,
        Attachment.of(HumanoidPart.LEFT_LEG, 0.0F, 2.0F, 0.0F),
        Attachment.mirrored(HumanoidPart.RIGHT_LEG, 0.0F, 2.0F, 0.0F)),
    /**
     * Both knees, mirrored, on the front of the legs. Poleyns, knee cops, garters.
     *
     * <p>The gap the other nine leave: {@link #TASSETS} sits at the hip at y = 2 and {@link #GREAVES}
     * at the shin at y = 8, and the knee between them had nowhere to go. y = 6 sits between those two
     * anchors and z = -2 puts it on the leg box's front face, the same plane the greave uses.
     *
     * <p>What the anchor does NOT buy is empty space. The parts on those two sockets leave 0.13 units
     * between them at their closest, and this anchor sits inside the tassets' third lame rather than
     * below it - so a knee part chooses which neighbour to lap rather than clearing both. That is a
     * property of the shipped parts, not of the socket, but any part authored here has to face it.
     */
    KNEES("knees", ArmorType.LEGGINGS,
        Attachment.of(HumanoidPart.LEFT_LEG, 0.0F, 6.0F, -2.0F),
        Attachment.mirrored(HumanoidPart.RIGHT_LEG, 0.0F, 6.0F, -2.0F)),

    // ---- Boots ------------------------------------------------------------------------------
    /** Both heels, mirrored, at the back of the ankle. Spurs. */
    SPURS("spurs", ArmorType.BOOTS,
        Attachment.of(HumanoidPart.LEFT_LEG, 0.0F, 10.0F, 2.0F),
        Attachment.mirrored(HumanoidPart.RIGHT_LEG, 0.0F, 10.0F, 2.0F)),
    /** Both shins, mirrored, on the front of the lower leg. Greave plates, wing-boots. */
    GREAVES("greaves", ArmorType.BOOTS,
        Attachment.of(HumanoidPart.LEFT_LEG, 0.0F, 8.0F, -2.0F),
        Attachment.mirrored(HumanoidPart.RIGHT_LEG, 0.0F, 8.0F, -2.0F));

    public static final Codec<DecorationAnchor> CODEC = StringRepresentable.fromEnum(DecorationAnchor::values);
    public static final StreamCodec<io.netty.buffer.ByteBuf, DecorationAnchor> STREAM_CODEC =
        ByteBufCodecs.idMapper(i -> values()[i], DecorationAnchor::ordinal);

    private final String id;
    private final ArmorType armorType;
    private final List<Attachment> attachments;

    DecorationAnchor(final String id, final ArmorType armorType, final Attachment... attachments) {
        this.id = id;
        this.armorType = armorType;
        this.attachments = List.of(attachments);
    }

    /** Which armor piece owns this socket. A part can only be applied to a base item of this type. */
    public ArmorType armorType() {
        return this.armorType;
    }

    public EquipmentSlot slot() {
        return this.armorType.getSlot();
    }

    /** Where on the body this socket draws - one entry, or two for a mirrored pair. */
    public List<Attachment> attachments() {
        return this.attachments;
    }

    @Override
    public String getSerializedName() {
        return this.id;
    }

    /** The anchors belonging to one armor piece, in declaration order. */
    public static List<DecorationAnchor> forArmorType(final ArmorType armorType) {
        return java.util.Arrays.stream(values()).filter(a -> a.armorType == armorType).toList();
    }

    /**
     * One place a part is drawn: a parent model part, an offset from that part's pivot, and whether
     * the geometry is mirrored across X to make it read as the other side of a pair.
     *
     * <p>Offsets are in entity-model space, so +Y points DOWN. That is why {@link #CREST} sits at
     * y = -8 (the top of the 8-tall head box) and {@link #BELT} at y = +10 (the bottom of the torso).
     */
    public record Attachment(HumanoidPart part, float x, float y, float z, boolean mirror) {
        public static Attachment of(final HumanoidPart part, final float x, final float y, final float z) {
            return new Attachment(part, x, y, z, false);
        }

        public static Attachment mirrored(final HumanoidPart part, final float x, final float y, final float z) {
            return new Attachment(part, x, y, z, true);
        }
    }

    /**
     * The humanoid model parts an anchor can hang from, named side-neutrally so this enum stays out
     * of the client package - {@code DecorationAnchor} is read by the recipe and the tooltip on the
     * server too, and must not drag {@code HumanoidModel} onto the server classpath.
     */
    public enum HumanoidPart {
        HEAD, BODY, LEFT_ARM, RIGHT_ARM, LEFT_LEG, RIGHT_LEG
    }
}
