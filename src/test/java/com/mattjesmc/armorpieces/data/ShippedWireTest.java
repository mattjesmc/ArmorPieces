package com.mattjesmc.armorpieces.data;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.mattjesmc.armorpieces.GameBootstrap;
import com.mattjesmc.armorpieces.cloth.Cloth;
import com.mattjesmc.armorpieces.cloth.ClothValue;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.decoration.fitting.FittingValue;
import com.mattjesmc.armorpieces.decoration.fitting.builtin.BannerFitting;
import com.mattjesmc.armorpieces.decoration.fitting.builtin.DyeFitting;
import com.mattjesmc.armorpieces.decoration.fitting.builtin.MaterialFitting;
import com.mattjesmc.armorpieces.identity.Tolerant;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.registry.ModItems;
import com.mattjesmc.armorpieces.skin.ArmorSkin;
import com.mattjesmc.armorpieces.skin.ArmorSkinValue;
import com.mojang.serialization.Dynamic;
import io.netty.buffer.ByteBufUtil;
import io.netty.buffer.Unpooled;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.NbtOps;
import net.minecraft.nbt.Tag;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.equipment.trim.TrimMaterial;
import net.minecraft.world.level.block.entity.BannerPatternLayers;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * The other half of {@link ShippedDataTest}: <b>every shipped element, over the wire</b>.
 *
 * <p>Nothing tested the wire before this. Every codec test beside it asks a question of the SAVED
 * form - JSON or NBT, a field a writer drops, a value that reads back as a different one - and the
 * saved form is only half of what a piece has to survive. The other half is the sync: a decorated
 * helmet is written into a packet by the server and read out of one by the client, through a
 * completely separate set of codecs that no test had ever run.
 *
 * <p>That gap has history. The 0.4.0 cycle spent three {@code runClient} runs on a sub-predicate
 * that a file wrote bare and the client decoded full-id - a sync-encode bug, found by a client
 * disconnecting, which is how a wire bug is always found: the reader stops at a different byte from
 * the one the writer stopped at, and the connection dies with a stack trace about something else.
 * A {@link RegistryFriendlyByteBuf} round trip is that same failure, asserted in milliseconds.
 *
 * <p>So every check here is one of three:
 *
 * <ul>
 *   <li><b>the buffer is drained</b> - the reader consumed exactly what the writer wrote, which is
 *       the misalignment that disconnects a client;</li>
 *   <li><b>the payload is the same size</b> - what came back off the wire writes as many bytes as
 *       were read, which is the field a codec reads and does not write. The size rather than the
 *       bytes themselves, because a part's sockets and a piece's decorations are unordered
 *       collections ({@code Set.copyOf}, {@code Map.copyOf}) whose iteration order is not part of
 *       the value, so the wire may reshuffle them. The SAVED form may not, and does not - see
 *       {@link ArmorDecorations#CODEC}, which writes sockets in anchor order for that reason;</li>
 *   <li><b>the value survives</b> - it equals what went in, on everything the wire carries.</li>
 * </ul>
 *
 * <p>Tier 1 in {@code docs/plans/testing.md}: the JVM, no game. {@link ShippedData} is the load, and
 * the registries it filled are what the buffer is handed - a holder travels as its registry id, so a
 * buffer that could not name the registry would test nothing but the fallback path.
 */
class ShippedWireTest {
    /** An id nothing in this repository defines - what a save written against an uninstalled pack says. */
    private static final String ABSENT = "armorpieces_absent:tusks";

    /** A socket key this version has no name for, as a later version's save would carry. */
    private static final String UNKNOWN_SOCKET = "wristbands";

    private static ShippedData.Loaded loaded;
    private static RegistryAccess registries;
    private static List<Holder.Reference<TrimMaterial>> materials;

    @BeforeAll
    static void world() {
        // Items and components, because the last test here sends a whole ItemStack.
        GameBootstrap.content();
        loaded = ShippedData.everything();
        // A material fitting's `materials` is a HolderSet, and every one this repository ships is a
        // TAG: reading it at all needs the tag bound, which is what a server does on /reload.
        ShippedData.bindTags(loaded);
        // And the items' own defaults, without which no ItemStack can be built at all.
        ShippedData.bakeItemComponents(loaded);
        // The five loaded registries and every built-in one. It has to be THIS access rather than a
        // fresh one: a holder travels as its id in the buffer's own registry, and an ops built from
        // a registry the loader never touched refuses to encode a HolderSet that points into it.
        registries = loaded.everyRegistry();
        materials = loaded.registry(Registries.TRIM_MATERIAL).listElements().toList();
        assertFalse(materials.isEmpty(), "no trim materials loaded - a decoration has no colour to be");
    }

    // ---- the registries ------------------------------------------------------------------------

    /**
     * Every part, both ways a part can travel.
     *
     * <p>By ID is the ordinary case - the client has the same registry, so a socket costs a varint.
     * DIRECTLY is the other branch of {@link net.minecraft.network.codec.ByteBufCodecs#holder}, taken
     * for a holder the buffer's registry cannot name, and it is the branch that carries the whole
     * definition: the description, the sockets, the fittings, the effects and the loot.
     */
    @Test
    void everyPartTravels() {
        final Registry<ArmorDecoration> parts = loaded.registry(ArmorPiecesRegistries.ARMOR_DECORATION);
        assertFalse(parts.keySet().isEmpty(), "no parts loaded");
        parts.listElements().forEach(part -> {
            final String what = name(part);
            assertSame(part, wire(ArmorDecoration.STREAM_CODEC, part, what),
                what + ": a part that travelled by id did not come back as its own registry entry");
            assertEquals(onTheWire(part.value()),
                wire(ArmorDecoration.DIRECT_STREAM_CODEC, part.value(), what), what);
            assertEquals(onTheWire(part.value()),
                wire(ArmorDecoration.STREAM_CODEC, Holder.direct(part.value()), what).value(),
                what + ": sent whole rather than by id");
        });
    }

    /**
     * Lineage is not synced, and this is the assertion that says so on purpose.
     *
     * <p>{@code former_ids} and {@code uid} exist to rebind a SAVE, and saves are read on the server.
     * The wire uses the six-field constructor, so a part sent whole comes back with an empty lineage -
     * which is correct, and would look exactly like a dropped field to anyone reading the test above.
     */
    @Test
    void lineageStaysOnTheServer() {
        final Registry<ArmorDecoration> parts = loaded.registry(ArmorPiecesRegistries.ARMOR_DECORATION);
        final Optional<Holder.Reference<ArmorDecoration>> withLineage = parts.listElements()
            .filter(part -> part.value().uid().isPresent() || !part.value().formerIds().isEmpty())
            .findFirst();
        if (withLineage.isEmpty()) {
            return;  // no part has been minted a uid yet; nothing to say
        }
        final ArmorDecoration part = withLineage.get().value();
        final ArmorDecoration back = wire(ArmorDecoration.DIRECT_STREAM_CODEC, part, name(withLineage.get()));
        assertTrue(back.uid().isEmpty() && back.formerIds().isEmpty(),
            "the wire has started carrying lineage - which is not wrong, but the save format and "
                + "docs/plans/compatibility.md both say the client never sees it");
        assertNotEquals(part, back, "the part above was chosen for having a lineage to lose");
    }

    @Test
    void everySkinTravels() {
        final Registry<ArmorSkin> skins = loaded.registry(ArmorPiecesRegistries.ARMOR_SKIN);
        assertFalse(skins.keySet().isEmpty(), "no skins loaded");
        skins.listElements().forEach(skin -> {
            final String what = name(skin);
            assertSame(skin, wire(ArmorSkin.STREAM_CODEC, skin, what), what);
            assertEquals(onTheWire(skin.value()),
                wire(ArmorSkin.DIRECT_STREAM_CODEC, skin.value(), what), what);
        });
    }

    @Test
    void everyClothTravels() {
        final Registry<Cloth> cloths = loaded.registry(ArmorPiecesRegistries.CLOTH);
        assertFalse(cloths.keySet().isEmpty(), "no cloths loaded");
        cloths.listElements().forEach(cloth -> {
            final String what = name(cloth);
            assertSame(cloth, wire(Cloth.STREAM_CODEC, cloth, what), what);
            assertEquals(onTheWire(cloth.value()),
                wire(Cloth.DIRECT_STREAM_CODEC, cloth.value(), what), what);
        });
    }

    /**
     * Fittings travel by id, and their definitions as NBT through their own dispatch codec - so this
     * is also the only place a fitting's {@code HolderSet} of materials is written to a buffer and
     * read back. A tag that came back as a different {@code HolderSet} would silently widen or narrow
     * what the smithing table accepts on the client.
     */
    @Test
    void everyFittingTravels() {
        final Registry<Fitting> fittings = loaded.registry(ArmorPiecesRegistries.FITTING);
        assertFalse(fittings.keySet().isEmpty(), "no fittings loaded");
        fittings.listElements().forEach(fitting -> {
            final String what = name(fitting);
            assertSame(fitting, wire(Fitting.STREAM_CODEC, fitting, what), what);
            assertEquals(fitting.value(),
                wire(Fitting.STREAM_CODEC, Holder.direct(fitting.value()), what).value(),
                what + ": sent whole rather than by id");
        });
    }

    // ---- what an item actually carries ---------------------------------------------------------

    /**
     * A filled socket, for every part this repository ships, with every fitting the part declares set
     * to something a smithing table could really have put there.
     */
    @Test
    void everyPartTravelsInASocket() {
        final Holder<TrimMaterial> material = materials.get(0);
        loaded.registry(ArmorPiecesRegistries.ARMOR_DECORATION).listElements().forEach(part -> {
            final DecorationEntry entry = new DecorationEntry(material, part, filled(part.value()));
            assertEquals(entry, wire(DecorationEntry.STREAM_CODEC, entry, name(part)), name(part));
        });
    }

    /** And once per material, since the material is vanilla's holder and travels by its own codec. */
    @Test
    void everyMaterialTravelsInASocket() {
        final Holder.Reference<ArmorDecoration> part =
            loaded.registry(ArmorPiecesRegistries.ARMOR_DECORATION).listElements().findFirst().orElseThrow();
        materials.forEach(material -> {
            final DecorationEntry entry = new DecorationEntry(material, part, Map.of());
            final String what = material.key().identifier().toString();
            assertEquals(entry, wire(DecorationEntry.STREAM_CODEC, entry, what), what);
        });
    }

    /**
     * The whole {@code armorpieces:decorations} component: every socket that has a part, plus one
     * socket this version has no name for.
     *
     * <p>The unresolved half is the point. It travels as raw NBT rather than being dropped, because
     * the tooltip that tells a player a pack is missing is drawn on the CLIENT and because a creative
     * client hands stacks back to the server - one that had been sent a hole would write one, and the
     * player would lose the part for good on a round trip through their own inventory.
     */
    @Test
    void theDecorationsComponentTravels() {
        final ArmorDecorations decorations = everySocketFilled();
        assertFalse(decorations.entries().isEmpty(), "no socket could be filled");
        assertEquals(decorations,
            wire(ModDataComponents.DECORATIONS.streamCodec(), decorations, "armorpieces:decorations"));
    }

    /**
     * The four tolerant components, resolved and not.
     *
     * <p>Through {@link DataComponentType#streamCodec()} rather than the codec constant, so what is
     * asserted is what the component was actually REGISTERED with - a component wired to the wrong
     * codec passes every test that names the codec directly.
     */
    @Test
    void theFourTolerantComponentsTravel() {
        final Holder.Reference<ArmorDecoration> part =
            loaded.registry(ArmorPiecesRegistries.ARMOR_DECORATION).listElements().findFirst().orElseThrow();
        final Holder.Reference<Fitting> fitting =
            loaded.registry(ArmorPiecesRegistries.FITTING).listElements().findFirst().orElseThrow();
        final Holder.Reference<ArmorSkin> skin =
            loaded.registry(ArmorPiecesRegistries.ARMOR_SKIN).listElements().findFirst().orElseThrow();
        final Holder.Reference<Cloth> cloth =
            loaded.registry(ArmorPiecesRegistries.CLOTH).listElements().findFirst().orElseThrow();

        tolerant(ModDataComponents.DECORATION, Tolerant.of(part), "armorpieces:decoration");
        tolerant(ModDataComponents.FITTING, Tolerant.of(fitting), "armorpieces:fitting");
        tolerant(ModDataComponents.SKIN, Tolerant.of(new ArmorSkinValue(skin)), "armorpieces:skin");
        tolerant(ModDataComponents.CLOTH, Tolerant.of(ClothValue.of(cloth)), "armorpieces:cloth");
    }

    /**
     * And the same four holding something this installation cannot name.
     *
     * <p>A bare holder is saved as its id, which is a STRING at the root of the raw NBT rather than a
     * compound - so this is also the assertion that the tolerant wire form can carry a root tag that
     * is not a map. A component that could not travel unresolved would take its item down on the
     * client instead of drawing the "pack not installed" line.
     */
    @Test
    void theFourTolerantComponentsTravelUnresolved() {
        tolerant(ModDataComponents.DECORATION, Tolerant.unresolved(raw(ABSENT)), "armorpieces:decoration");
        tolerant(ModDataComponents.FITTING, Tolerant.unresolved(raw(ABSENT)), "armorpieces:fitting");
        tolerant(ModDataComponents.SKIN, Tolerant.unresolved(raw(ABSENT)), "armorpieces:skin");
        tolerant(ModDataComponents.CLOTH,
            Tolerant.unresolved(raw(Map.of("cloth", ABSENT))), "armorpieces:cloth");
    }

    /**
     * The thing itself: a decorated, skinned helmet and a clothed chestplate as {@link ItemStack}s,
     * through vanilla's own stack codec - which is what a player's inventory is sent as, and what
     * a bad component codec takes down with it.
     *
     * <p>Templates too, and each of them holding a piece nothing defines, because that is the stack a
     * player is left with after a pack is uninstalled and the one that has to survive the trip.
     */
    @Test
    void aDecoratedStackTravels() {
        final Holder.Reference<ArmorSkin> skin =
            loaded.registry(ArmorPiecesRegistries.ARMOR_SKIN).listElements().findFirst().orElseThrow();
        final Holder.Reference<Cloth> cloth =
            loaded.registry(ArmorPiecesRegistries.CLOTH).listElements().findFirst().orElseThrow();
        final Holder.Reference<ArmorDecoration> part =
            loaded.registry(ArmorPiecesRegistries.ARMOR_DECORATION).listElements().findFirst().orElseThrow();

        final ItemStack helmet = new ItemStack(Items.DIAMOND_HELMET);
        helmet.set(ModDataComponents.DECORATIONS, everySocketFilled());
        helmet.set(ModDataComponents.SKIN, Tolerant.of(new ArmorSkinValue(skin)));
        stack(helmet, "a decorated, skinned helmet");

        final ItemStack chestplate = new ItemStack(Items.DIAMOND_CHESTPLATE);
        chestplate.set(ModDataComponents.CLOTH, Tolerant.of(new ClothValue(
            cloth, DyeColor.RED, BannerPatternLayers.EMPTY)));
        stack(chestplate, "a clothed chestplate");

        final ItemStack template = new ItemStack(ModItems.template(part.value().primaryAnchor()));
        template.set(ModDataComponents.DECORATION, Tolerant.of(part));
        stack(template, "a part template");

        final ItemStack orphaned = new ItemStack(ModItems.template(DecorationAnchor.values()[0]));
        orphaned.set(ModDataComponents.DECORATION, Tolerant.unresolved(raw(ABSENT)));
        stack(orphaned, "a template whose part is not installed");

        final ItemStack strandedHelmet = new ItemStack(Items.DIAMOND_HELMET);
        strandedHelmet.set(ModDataComponents.DECORATIONS,
            new ArmorDecorations(Map.of(), Map.of(UNKNOWN_SOCKET, raw(Map.of("decoration", ABSENT)))));
        stack(strandedHelmet, "a helmet wearing a part this version cannot name");
    }

    // ---- the machinery -------------------------------------------------------------------------

    /** Encode, decode, and hand back what came out - having asserted the two things the wire owes. */
    private static <T> T wire(
        final StreamCodec<? super RegistryFriendlyByteBuf, T> codec, final T value, final String what
    ) {
        final RegistryFriendlyByteBuf out = buffer();
        codec.encode(out, value);
        final byte[] written = bytes(out);
        final T back = codec.decode(out);
        assertEquals(0, out.readableBytes(),
            what + ": the reader stopped " + out.readableBytes() + " bytes short of what the writer "
                + "wrote - this is the misalignment that disconnects a client");

        final RegistryFriendlyByteBuf again = buffer();
        codec.encode(again, back);
        assertEquals(written.length, bytes(again).length,
            what + ": what came back off the wire writes a payload of a different size - a field is "
                + "read and not written, or written and not read");
        return back;
    }

    /** One tolerant component, through the codec it was actually registered with. */
    private static <T> void tolerant(
        final DataComponentType<Tolerant<T>> type, final Tolerant<T> value, final String what
    ) {
        assertEquals(value, wire(type.streamCodec(), value, what), what);
    }

    /** One whole stack, through vanilla's own codec - the trip an inventory makes. */
    private static void stack(final ItemStack value, final String what) {
        final RegistryFriendlyByteBuf out = buffer();
        ItemStack.STREAM_CODEC.encode(out, value);
        final ItemStack back = ItemStack.STREAM_CODEC.decode(out);
        assertEquals(0, out.readableBytes(), what + ": the stack's reader stopped short of its writer");
        assertTrue(ItemStack.matches(value, back),
            what + ": came back as a different stack\n  sent: " + value.getComponents()
                + "\n  back: " + back.getComponents());
    }

    private static RegistryFriendlyByteBuf buffer() {
        return new RegistryFriendlyByteBuf(Unpooled.buffer(), registries);
    }

    private static byte[] bytes(final RegistryFriendlyByteBuf buffer) {
        return ByteBufUtil.getBytes(buffer, buffer.readerIndex(), buffer.readableBytes());
    }

    /** Every socket some part fits, filled, plus one socket this version has no name for. */
    private static ArmorDecorations everySocketFilled() {
        final Registry<ArmorDecoration> parts = loaded.registry(ArmorPiecesRegistries.ARMOR_DECORATION);
        final Holder<TrimMaterial> material = materials.get(0);
        final Map<DecorationAnchor, DecorationEntry> entries = new LinkedHashMap<>();
        for (final DecorationAnchor anchor : DecorationAnchor.values()) {
            parts.listElements()
                .filter(part -> part.value().fits(anchor))
                .findFirst()
                .ifPresent(part -> entries.put(anchor,
                    new DecorationEntry(material, part, filled(part.value()))));
        }
        return new ArmorDecorations(entries, Map.of(UNKNOWN_SOCKET, raw(Map.of("decoration", ABSENT))));
    }

    /** Each of a part's fittings holding a value of the kind its type reads off an item. */
    private static Map<Holder<Fitting>, FittingValue> filled(final ArmorDecoration part) {
        final Map<Holder<Fitting>, FittingValue> values = new LinkedHashMap<>();
        part.fittings().forEach(fitting -> {
            final Optional<FittingValue> value = sample(fitting.value());
            assertTrue(value.isPresent(),
                part.assetId() + " lists a fitting type this test has no sample value for, so its "
                    + "fittings are travelling empty - add one to sample()");
            value.ifPresent(held -> values.put(fitting, held));
        });
        return values;
    }

    /**
     * A value each shipped fitting type could really be holding. Deliberately built here rather than
     * taken from {@link Fitting#accept} with an item: what is being tested is the wire, and an item
     * that a fitting happens to refuse would quietly send an empty map instead of failing.
     */
    private static Optional<FittingValue> sample(final Fitting fitting) {
        if (fitting instanceof MaterialFitting material) {
            return material.materials().stream().findFirst().map(MaterialFitting.Value::new);
        }
        if (fitting instanceof DyeFitting) {
            return Optional.of(new DyeFitting.Value(DyeColor.RED));
        }
        if (fitting instanceof BannerFitting) {
            return Optional.of(new BannerFitting.Value(DyeColor.RED, BannerPatternLayers.EMPTY));
        }
        return Optional.empty();
    }

    /** A bare id, as a save writes a holder it could not resolve. */
    private static Dynamic<Tag> raw(final String id) {
        return new Dynamic<>(NbtOps.INSTANCE, NbtOps.INSTANCE.createString(id));
    }

    /** An object, as a save writes an entry it could not resolve. */
    private static Dynamic<Tag> raw(final Map<String, String> fields) {
        final Map<Tag, Tag> map = new LinkedHashMap<>();
        fields.forEach((key, value) ->
            map.put(NbtOps.INSTANCE.createString(key), NbtOps.INSTANCE.createString(value)));
        return new Dynamic<>(NbtOps.INSTANCE, NbtOps.INSTANCE.createMap(map));
    }

    /** The part as the wire carries it: everything but the lineage, which the server keeps. */
    private static ArmorDecoration onTheWire(final ArmorDecoration part) {
        return new ArmorDecoration(part.assetId(), part.description(), part.anchors(),
            part.fittings(), part.effects(), part.loot());
    }

    private static ArmorSkin onTheWire(final ArmorSkin skin) {
        return new ArmorSkin(skin.assetId(), skin.description(), skin.loot());
    }

    private static Cloth onTheWire(final Cloth cloth) {
        return new Cloth(cloth.assetId(), cloth.sheet(), cloth.description(), cloth.loot());
    }

    private static String name(final Holder.Reference<?> holder) {
        return holder.key().identifier().toString();
    }
}
