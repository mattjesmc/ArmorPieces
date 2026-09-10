package com.mattjesmc.armorpieces.client.geometry;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.GameBootstrap;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.packs.PackLocationInfo;
import net.minecraft.server.packs.PackResources;
import net.minecraft.server.packs.PackType;
import net.minecraft.server.packs.PathPackResources;
import net.minecraft.server.packs.repository.PackSource;
import net.minecraft.server.packs.resources.MultiPackResourceManager;
import net.minecraft.server.packs.resources.PreparableReloadListener;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.util.profiling.InactiveProfiler;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * How a part's shape gets from a resource pack into the render layer: {@link
 * DecorationGeometryManager}, driven through a real reload over real packs.
 *
 * <p>The loader is the seam that makes shapes data. It scans {@code assets/<any
 * namespace>/armorpieces/decoration/*.json}, bakes what it finds once per reload, and hands the
 * render layer a map lookup - so a pack adds a piece by dropping a file, and overrides one of ours by
 * using the same id. Every one of those sentences is a string built at load time, which is to say:
 * not a compile error, not a load error, and not a warning if it stops being true. A directory
 * renamed one level up costs every part in the mod its shape, and the symptom is a player wearing
 * armor that has quietly stopped being decorated.
 *
 * <p>Four rules, and the reasons they are separate:
 *
 * <ul>
 *   <li><b>The file's own path is the id.</b> Namespace and all - that is what lets a pack's part be
 *       {@code a_pack:plume} without registering anything.</li>
 *   <li><b>The pack stack decides, and the last pack wins.</b> A resource pack overriding one of the
 *       mod's shapes is the ordinary way to reskin a piece, and it must not need the mod's
 *       cooperation.</li>
 *   <li><b>One broken file costs that part and nothing else.</b> A third-party pack with a typo in it
 *       should not take the player's whole resource pack down, which is what an exception escaping a
 *       reload does.</li>
 *   <li><b>A variant is baked once and forgotten on reload.</b> {@code get(id, without)} is called
 *       per frame per worn piece; it must be a lookup, and it must not survive the reload that
 *       changed the shape it was cut from.</li>
 * </ul>
 *
 * <p>The reload is vanilla's own - {@link PreparableReloadListener#reload} with both executors on the
 * calling thread - rather than a call to {@code apply}, so the scan, the codec and the bake all run
 * the way they do in a game and the path above is really the path being asserted. The manager is a
 * singleton and every test here begins by loading its own packs into it, which is what keeps them
 * independent of each other.
 */
class DecorationGeometryManagerTest {

    /**
     * Nothing here is a registry, but everything here is a class beside one.
     *
     * <p>Fabric's loot API mixes into {@code SimpleJsonResourceReloadListener.scanDirectory}, so a
     * reload initialises {@code LootDataType} - and an un-bootstrapped game fails that initialiser
     * once and then answers every later question with a {@code NoClassDefFoundError} naming whatever
     * innocent class asked next. One line, and it is the difference between this suite and 25 failures
     * that name the wrong thing.
     */
    @BeforeAll
    static void game() {
        GameBootstrap.once();
    }

    /** A shape with two bones, one hanging under the other - the fixture nearly every test loads. */
    private static final String PLUME = """
        {"texture_width": 32, "texture_height": 32,
         "bones": [{"name": "base", "pivot": [0, 0, 0],
                    "cubes": [{"origin": [0, 0, 0], "size": [1, 2, 1]}],
                    "children": [{"name": "tip", "pivot": [0, -2, 0],
                                  "cubes": [{"origin": [0, 0, 0], "size": [1, 2, 1], "uv": [4, 0]}]}]}]}
        """;

    @Test
    void everyFileUnderThePartsDirectoryIsFoundUnderItsOwnId(@TempDir final Path pack) throws IOException {
        geometry(pack, "a_pack", "plume", PLUME);
        geometry(pack, "a_pack", "nested/crest", PLUME);
        geometry(pack, "another_pack", "plume", PLUME);
        // Something under the same namespace that is not a part's shape. The scan is a directory and
        // an extension, so a pack's other JSON must not arrive as a part nobody can name.
        write(pack.resolve("assets/a_pack/armorpieces/skin/plume.json"), PLUME);
        load(pack);

        assertNotNull(instance().get(id("a_pack", "plume")), "a pack's own part");
        assertNotNull(instance().get(id("a_pack", "nested/crest")),
            "a part in a folder keeps the folder in its id");
        assertNotNull(instance().get(id("another_pack", "plume")),
            "the same name under another namespace is another part");
        assertNull(instance().get(id("a_pack", "skin/plume")), "and nothing else in the pack is a shape");
    }

    @Test
    void theLastPackToNameAnIdIsTheOneDrawn(
        @TempDir final Path first, @TempDir final Path second
    ) throws IOException {
        geometry(first, ArmorPieces.MOD_ID, "plume", PLUME);
        // The same id from a pack higher in the stack, with a bone the mod's own does not have. This
        // is a player's resource pack reshaping a piece of the mod, and it needs no cooperation here.
        geometry(second, ArmorPieces.MOD_ID, "plume", """
            {"bones": [{"name": "banner", "cubes": [{"origin": [0, 0, 0], "size": [6, 6, 1]}]}]}
            """);
        load(first, second);

        final ModelPart drawn = instance().get(id(ArmorPieces.MOD_ID, "plume"));
        assertNotNull(drawn, "the part is still there");
        assertTrue(drawn.hasChild("banner"), "the pack on top is what is drawn");
        assertFalse(drawn.hasChild("base"), "and the one underneath is not");
    }

    @Test
    void aFileThatCannotBeReadCostsThatPartAndNoOther(@TempDir final Path pack) throws IOException {
        geometry(pack, "a_pack", "good", PLUME);
        write(pack.resolve("assets/a_pack/armorpieces/decoration/torn.json"), "{\"bones\": [");
        // Readable JSON that is not a geometry: the codec's own refusal rather than the parser's.
        geometry(pack, "a_pack", "empty", """
            {"bones": []}
            """);
        load(pack);

        assertNotNull(instance().get(id("a_pack", "good")), "the part beside the broken ones");
        assertNull(instance().get(id("a_pack", "torn")), "a file that is not JSON");
        assertNull(instance().get(id("a_pack", "empty")), "a file that is JSON and not a geometry");
    }

    /**
     * The bake's own guard, which no file can reach.
     *
     * <p>{@code apply} catches a {@link RuntimeException} out of one part's bake and keeps the rest,
     * and that is worth having: losing one part is recoverable and aborting a reload is not. What is
     * worth writing down is that the codec makes it nearly unreachable from a pack - a geometry that
     * decodes at all has a name, three floats per coordinate and a positive sheet, and vanilla's
     * builders bake even nonsense numbers without complaint (a zero-sized box, a NaN, a box off the
     * sheet). So the fixture here is built as a record rather than parsed, which is the only way to
     * hand the loader a definition that throws, and it goes in through {@code apply} directly.
     */
    @Test
    void aShapeThatCannotBeBakedIsSkippedAndItsNeighboursKept() {
        final DecorationGeometry cannot = new DecorationGeometry(32, 32, List.of(new DecorationGeometry.Bone(
            null, DecorationGeometry.Vec3f.ZERO, DecorationGeometry.Vec3f.ZERO, false,
            List.of(new DecorationGeometry.Cube(DecorationGeometry.Vec3f.ZERO,
                new DecorationGeometry.Vec3f(1, 1, 1), 0, 0, 0.0F, false)),
            List.of())));

        instance().apply(
            Map.of(id("a_pack", "broken"), cannot, id("a_pack", "fine"), parse(PLUME)),
            empty(),
            InactiveProfiler.INSTANCE);

        assertNull(instance().get(id("a_pack", "broken")), "the part whose numbers vanilla refused");
        assertNotNull(instance().get(id("a_pack", "fine")), "and the reload still happened");
    }

    @Test
    void aPartNoPackSuppliesIsNullRatherThanAFailure(@TempDir final Path pack) throws IOException {
        geometry(pack, "a_pack", "plume", PLUME);
        load(pack);
        // Null is a legitimate answer: a datapack may name a part whose resource-pack half is not
        // installed, and a part may be overlay-only. The render layer draws what it has.
        assertNull(instance().get(id("a_pack", "nobody_ships_this")), "a shape nothing supplies");
        assertNull(instance().get(id("a_pack", "nobody_ships_this"), Set.of("base")),
            "and the same asked with a bone left out");
    }

    // ---- what a filled fitting asks for ------------------------------------------------------------

    @Test
    void aVariantLeavesTheBoneOutAndIsBakedOnlyOnce(@TempDir final Path pack) throws IOException {
        geometry(pack, "a_pack", "plume", PLUME);
        load(pack);
        final Identifier plume = id("a_pack", "plume");

        final ModelPart whole = instance().get(plume);
        final ModelPart without = instance().get(plume, Set.of("base"));
        assertNotNull(without, "the variant bakes");
        assertTrue(whole.hasChild("base"), "the part itself has the bone");
        assertFalse(without.hasChild("base"), "and the variant does not");
        assertNotSame(whole, without, "which makes it a different model");

        // Per frame per worn piece, so the second ask must be a lookup. A variant rebaked every frame
        // is a model tree allocated 60 times a second per player in view.
        assertSame(without, instance().get(plume, Set.of("base")), "asked again, the same object");
        assertSame(without, instance().get(plume, new java.util.HashSet<>(Set.of("base"))),
            "and the same for an equal set that is not the same object");
    }

    @Test
    void leavingNothingOutIsThePartItself(@TempDir final Path pack) throws IOException {
        geometry(pack, "a_pack", "plume", PLUME);
        load(pack);
        final Identifier plume = id("a_pack", "plume");
        // A piece with no filled fitting takes this path every frame; it must not bake a second copy
        // of every part in the game to answer it.
        assertSame(instance().get(plume), instance().get(plume, Set.of()),
            "an empty set is the part, not a variant of it");
    }

    @Test
    void aReloadForgetsTheVariantsItBaked(@TempDir final Path pack, @TempDir final Path changed)
        throws IOException {
        geometry(pack, "a_pack", "plume", PLUME);
        load(pack);
        final Identifier plume = id("a_pack", "plume");
        final ModelPart before = instance().get(plume, Set.of("base"));

        geometry(changed, "a_pack", "plume", PLUME);
        load(changed);
        // A variant is cut from a definition, so one kept across a reload is a piece drawn from the
        // resource pack the player just turned off.
        assertNotSame(before, instance().get(plume, Set.of("base")),
            "the variant is cut from the shape the new pack supplies");
    }

    @Test
    void theLoaderNamesItselfSoTheReloadCanBeOrdered() {
        assertEquals(Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "decoration_geometry"),
            instance().getFabricId(), "the id Fabric orders reload listeners by");
    }

    // ---- packs on disk -----------------------------------------------------------------------------

    private static DecorationGeometryManager instance() {
        return DecorationGeometryManager.instance();
    }

    private static Identifier id(final String namespace, final String path) {
        return Identifier.fromNamespaceAndPath(namespace, path);
    }

    private static DecorationGeometry parse(final String json) {
        return DecorationGeometry.CODEC
            .parse(com.mojang.serialization.JsonOps.INSTANCE, com.google.gson.JsonParser.parseString(json))
            .getOrThrow(message -> new AssertionError(message));
    }

    /** One geometry file, where the loader's own scan says a part's shape lives. */
    private static void geometry(
        final Path root, final String namespace, final String path, final String json
    ) throws IOException {
        write(root.resolve("assets/" + namespace + "/armorpieces/decoration/" + path + ".json"), json);
    }

    private static void write(final Path file, final String content) throws IOException {
        Files.createDirectories(file.getParent());
        Files.writeString(file, content, StandardCharsets.UTF_8);
    }

    /** Runs a real reload of the singleton over these packs, lowest first. */
    private static void load(final Path... roots) {
        final List<PackResources> packs = new ArrayList<>();
        for (final Path root : roots) {
            packs.add(pack(root));
        }
        reload(new MultiPackResourceManager(PackType.CLIENT_RESOURCES, packs));
    }

    private static void reload(final ResourceManager resources) {
        instance().reload(
            new PreparableReloadListener.SharedState(resources),
            Runnable::run,
            new PreparableReloadListener.PreparationBarrier() {
                @Override
                public <T> CompletableFuture<T> wait(final T value) {
                    return CompletableFuture.completedFuture(value);
                }
            },
            Runnable::run
        ).join();
    }

    private static ResourceManager empty() {
        return new MultiPackResourceManager(PackType.CLIENT_RESOURCES, List.of());
    }

    private static PackResources pack(final Path root) {
        final String name = root.getFileName().toString();
        return new PathPackResources(
            new PackLocationInfo(name, Component.literal(name), PackSource.BUILT_IN, Optional.empty()),
            root);
    }
}
