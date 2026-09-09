package com.mattjesmc.armorpieces.data;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.mattjesmc.armorpieces.cloth.Cloth;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationLoot;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.identity.Identified;
import com.mattjesmc.armorpieces.loot.LootGroup;
import com.mattjesmc.armorpieces.skin.ArmorSkin;
import com.mojang.serialization.Codec;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Stream;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import org.junit.jupiter.api.Test;

/**
 * The row the gate's plan calls owed: <b>every shipped part, skin, cloth, fitting and loot group,
 * decoded and encoded back</b>.
 *
 * <p>Sixty-six parts ship in this jar and were never read outside a running game. The codec tests
 * beside this one each hold ONE trap - a config that writes {@code {}}, a table entry that loses its
 * alternative, a tag that takes its loot table down - and every one of those was found by playing
 * the game rather than by building it. The same class of defect in a shipped FILE (a field the
 * writer drops, a fitting id nothing defines, a part with no socket) costs a game cycle to find in
 * exactly the same way, and this is that cycle spent once, in three seconds, on all of them.
 *
 * <p>{@link ShippedData} is the load. What is asserted here is what the load cannot say by itself:
 * that it read everything the tree holds, that every value survives a trip through its own codec,
 * and that the cross-registry references resolve.
 */
class ShippedDataTest {
    /**
     * The registry name in {@code data/<ns>/armorpieces/<here>/} - the loader's own convention.
     *
     * <p>A method, not a constant: reading {@link ArmorPiecesRegistries} initialises it, and that
     * class registers a Fabric registry in its own initialiser - which cannot happen before the
     * game is bootstrapped, and a constant here would be built when JUnit merely LOADS this class.
     */
    private static Map<ResourceKey<? extends Registry<?>>, String> directories() {
        return Map.of(
            ArmorPiecesRegistries.ARMOR_DECORATION, "armor_decoration",
            ArmorPiecesRegistries.ARMOR_SKIN, "armor_skin",
            ArmorPiecesRegistries.CLOTH, "cloth",
            ArmorPiecesRegistries.FITTING, "fitting",
            ArmorPiecesRegistries.LOOT_GROUP, "loot_group");
    }

    // ---- the load read everything ------------------------------------------------------------

    /**
     * A loader that fails on one file throws, so the danger is not a broken file but an INVISIBLE
     * one: a part in a directory the loader does not read is not an error, it is a part that is not
     * in the game. Counted against the tree rather than against a number, so a part added tomorrow
     * needs no edit here.
     */
    @Test
    void everyFileInTheTreeIsAnEntryInARegistry() {
        final ShippedData.Loaded loaded = ShippedData.mod();
        directories().forEach((key, directory) -> {
            final List<Identifier> onDisk = files(ShippedData.MOD, directory);
            final Registry<?> registry = loaded.registry(key);
            assertEquals(Set.copyOf(onDisk), registry.keySet(),
                () -> directory + ": the files under src/main/resources and the registry the loader "
                    + "filled from them are not the same set");
        });
    }

    /** The mod is not empty, and this is the assertion that says so if a whole directory vanishes. */
    @Test
    void theModShipsItsContent() {
        final ShippedData.Loaded loaded = ShippedData.mod();
        assertTrue(loaded.registry(ArmorPiecesRegistries.ARMOR_DECORATION).size() >= 60,
            "the mod ships sixty-six parts; a load this small means the loader missed a directory");
        assertFalse(loaded.registry(ArmorPiecesRegistries.ARMOR_SKIN).keySet().isEmpty(), "no skins loaded");
        assertFalse(loaded.registry(ArmorPiecesRegistries.CLOTH).keySet().isEmpty(), "no cloths loaded");
        assertFalse(loaded.registry(ArmorPiecesRegistries.FITTING).keySet().isEmpty(), "no fittings loaded");
        assertFalse(loaded.registry(ArmorPiecesRegistries.LOOT_GROUP).keySet().isEmpty(), "no loot groups loaded");
    }

    // ---- the round trip ------------------------------------------------------------------------

    @Test
    void everyShippedElementSurvivesItsOwnCodec() {
        roundTripEverything(ShippedData.mod());
    }

    /**
     * And again with every pack in {@code packs/} installed beside the mod, which is how a player
     * has them. A pack's part names the mod's fittings, so this is also the only place those
     * references are resolved across a namespace boundary.
     */
    @Test
    void everyPacksElementSurvivesItsOwnCodec() {
        final Map<String, Path> packs = ShippedData.packs();
        if (packs.isEmpty()) {
            return;  // a checkout without the packs is a valid checkout
        }
        final ShippedData.Loaded loaded = ShippedData.everything();
        roundTripEverything(loaded);
        // And the packs actually got in: the whole point of loading them together.
        assertTrue(loaded.registry(ArmorPiecesRegistries.ARMOR_DECORATION).size()
                > ShippedData.mod().registry(ArmorPiecesRegistries.ARMOR_DECORATION).size(),
            () -> "the packs " + packs.keySet() + " added no parts, so nothing here was tested");
    }

    private static void roundTripEverything(final ShippedData.Loaded loaded) {
        roundTrip(loaded, ArmorPiecesRegistries.FITTING, Fitting.DIRECT_CODEC);
        roundTrip(loaded, ArmorPiecesRegistries.ARMOR_DECORATION, ArmorDecoration.DIRECT_CODEC);
        roundTrip(loaded, ArmorPiecesRegistries.ARMOR_SKIN, ArmorSkin.DIRECT_CODEC);
        roundTrip(loaded, ArmorPiecesRegistries.CLOTH, Cloth.DIRECT_CODEC);
        roundTrip(loaded, ArmorPiecesRegistries.LOOT_GROUP, LootGroup.DIRECT_CODEC);
    }

    private static <T> void roundTrip(
        final ShippedData.Loaded loaded,
        final ResourceKey<? extends Registry<? extends T>> key,
        final Codec<T> codec
    ) {
        final Registry<T> registry = loaded.registry(key);
        for (final Map.Entry<ResourceKey<T>, T> entry : registry.entrySet()) {
            final T back;
            try {
                back = ShippedData.roundTrip(loaded, codec, entry.getValue());
            } catch (final AssertionError failed) {
                throw new AssertionError(entry.getKey().identifier() + " " + failed.getMessage(), failed);
            }
            assertEquals(entry.getValue(), back,
                () -> entry.getKey().identifier() + " is not what it was after a trip through its own "
                    + "codec - a field is dropped on the way out");
        }
    }

    // ---- what the references mean ---------------------------------------------------------------

    /** A part's fittings are holders, and a holder that never bound would throw on first use. */
    @Test
    void everyPartsFittingsAreBound() {
        final ShippedData.Loaded loaded = ShippedData.everything();
        for (final Map.Entry<ResourceKey<ArmorDecoration>, ArmorDecoration> entry
                : loaded.registry(ArmorPiecesRegistries.ARMOR_DECORATION).entrySet()) {
            for (final Holder<Fitting> fitting : entry.getValue().fittings()) {
                assertTrue(fitting.isBound(),
                    () -> entry.getKey().identifier() + " names a fitting nothing defines: " + fitting);
                assertNotNull(fitting.value().description(),
                    () -> entry.getKey().identifier() + "'s fitting has no name");
            }
        }
    }

    /** Sockets come from an enum, so the codec proves the value - what it cannot prove is that there is one. */
    @Test
    void everyPartHasASocket() {
        final ShippedData.Loaded loaded = ShippedData.everything();
        for (final Map.Entry<ResourceKey<ArmorDecoration>, ArmorDecoration> entry
                : loaded.registry(ArmorPiecesRegistries.ARMOR_DECORATION).entrySet()) {
            final Set<DecorationAnchor> anchors = entry.getValue().anchors();
            assertFalse(anchors.isEmpty(), () -> entry.getKey().identifier() + " fits nowhere");
            // primaryAnchor throws on an empty set; call it, because loot and the creative tab do.
            assertTrue(anchors.contains(entry.getValue().primaryAnchor()));
        }
    }

    /**
     * Loot is the one field on a part that names something outside the mod entirely - a vanilla
     * table by id - and a chance outside 0..1 or a weight of zero is a file that loads and then
     * behaves as nobody meant.
     */
    @Test
    void everyLootLineIsSaneAndCanBeRolled() {
        final ShippedData.Loaded loaded = ShippedData.everything();
        final List<DecorationLoot> lines = new ArrayList<>();
        loaded.registry(ArmorPiecesRegistries.ARMOR_DECORATION).stream()
            .forEach(part -> lines.addAll(part.loot()));
        loaded.registry(ArmorPiecesRegistries.ARMOR_SKIN).stream()
            .forEach(skin -> lines.addAll(skin.loot()));
        loaded.registry(ArmorPiecesRegistries.CLOTH).stream()
            .forEach(cloth -> lines.addAll(cloth.loot()));
        for (final DecorationLoot line : lines) {
            assertTrue(line.chance() > 0.0f && line.chance() <= 1.0f,
                () -> line + " has a chance nothing can be found at");
            assertTrue(line.weight() > 0, () -> line + " has a weight of nothing");
        }
    }

    /**
     * A loot group's own numbers, and its tables: the group is what decides how much of this mod a
     * world hands out, and every one of those tables is a vanilla id typed by hand.
     */
    @Test
    void everyLootGroupIsSane() {
        final ShippedData.Loaded loaded = ShippedData.everything();
        for (final Map.Entry<ResourceKey<LootGroup>, LootGroup> entry
                : loaded.registry(ArmorPiecesRegistries.LOOT_GROUP).entrySet()) {
            final LootGroup group = entry.getValue();
            assertFalse(group.tables().isEmpty(),
                () -> entry.getKey().identifier() + " names no table, so nothing it holds is ever found");
            assertTrue(group.chance() > 0.0f,
                () -> entry.getKey().identifier() + " is found at a chance of zero");
            final Set<ResourceKey<?>> seen = new HashSet<>();
            for (final LootGroup.TableEntry table : group.tables()) {
                assertTrue(seen.add(table.table()),
                    () -> entry.getKey().identifier() + " names " + table.table().identifier() + " twice, "
                        + "and the second chance is the one that is ignored");
                assertEquals("minecraft", table.table().identifier().getNamespace(),
                    () -> entry.getKey().identifier() + " names a table outside vanilla: "
                        + table.table().identifier() + " - if that pack is absent the line does nothing");
                assertTrue(group.chanceFor(table.table()).isPresent());
            }
        }
    }

    // ---- identity ---------------------------------------------------------------------------

    /**
     * The lineage rule, held across the mod AND every pack at once - which is where it can actually
     * be broken, since a uid is minted per repository and a pack is a second author.
     */
    @Test
    void noUidIsUsedTwiceAnywhere() {
        final ShippedData.Loaded loaded = ShippedData.everything();
        final Map<String, Identifier> owners = new HashMap<>();
        identified(loaded).forEach((id, thing) -> thing.uid().ifPresent(uid -> {
            final Identifier first = owners.put(uid, id);
            assertTrue(first == null || first.equals(id),
                () -> "the uid " + uid + " is on two pieces: " + first + " and " + id
                    + " - a save cannot be rebound to both");
        }));
    }

    /**
     * A piece that says it used to be called something else must not collide with what IS - a save
     * naming that id would bind to the live piece and never reach the rebind at all.
     *
     * <p>With one exemption, and it is the point of the exemption rather than a hole in the rule:
     * {@code packs/legacy} is GENERATED from exactly these former ids, and re-defines them on
     * purpose so that a world built before the split keeps the pieces it had. So an id the restore
     * pack brings back is not a collision; an id any OTHER pack brings back is.
     */
    @Test
    void noFormerIdIsAlsoALiveId() {
        final ShippedData.Loaded loaded = ShippedData.everything();
        final Map<Identifier, Identified> live = identified(loaded);
        final Set<Identifier> restored = restorePack();
        live.forEach((id, thing) -> thing.formerIds().forEach(former ->
            assertFalse(live.containsKey(former) && !former.equals(id) && !restored.contains(former),
                () -> id + " claims the former id " + former + ", which is a piece that still exists "
                    + "- a save naming it would be rebound away from the piece it means")));
    }

    /** Every id {@code packs/legacy} defines: the ids the split moved, handed back by design. */
    private static Set<Identifier> restorePack() {
        final Path legacy = ShippedData.packs().get("legacy");
        if (legacy == null) {
            return Set.of();
        }
        final Set<Identifier> ids = new HashSet<>();
        for (final String directory : List.of("armor_decoration", "armor_skin", "cloth")) {
            ids.addAll(files(legacy, directory));
        }
        return ids;
    }

    private static Map<Identifier, Identified> identified(final ShippedData.Loaded loaded) {
        final Map<Identifier, Identified> all = new HashMap<>();
        List.<ResourceKey<? extends Registry<? extends Identified>>>of(
            ArmorPiecesRegistries.ARMOR_DECORATION,
            ArmorPiecesRegistries.ARMOR_SKIN,
            ArmorPiecesRegistries.CLOTH
        ).forEach(key -> loaded.registry(key).entrySet()
            .forEach(entry -> all.put(entry.getKey().identifier(), entry.getValue())));
        return all;
    }

    // ---- the tree --------------------------------------------------------------------------

    /** Every {@code .json} under {@code data/<ns>/armorpieces/<directory>/}, as the id it will get. */
    private static List<Identifier> files(final Path root, final String directory) {
        final Path data = root.resolve("data");
        if (!Files.isDirectory(data)) {
            return List.of();
        }
        final List<Identifier> found = new ArrayList<>();
        try (Stream<Path> namespaces = Files.list(data)) {
            for (final Path namespace : namespaces.toList()) {
                final Path where = namespace.resolve("armorpieces").resolve(directory);
                if (!Files.isDirectory(where)) {
                    continue;
                }
                try (Stream<Path> walk = Files.walk(where)) {
                    walk.filter(path -> path.getFileName().toString().endsWith(".json")).forEach(path -> {
                        final String relative = where.relativize(path).toString()
                            .replace('\\', '/').replaceAll("\\.json$", "");
                        found.add(Identifier.fromNamespaceAndPath(
                            namespace.getFileName().toString(), relative));
                    });
                }
            }
        } catch (final IOException failed) {
            throw new UncheckedIOException(failed);
        }
        return found;
    }
}
