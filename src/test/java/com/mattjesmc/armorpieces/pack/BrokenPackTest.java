package com.mattjesmc.armorpieces.pack;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.mattjesmc.armorpieces.data.ShippedData;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.Lifecycle;
import com.mojang.serialization.JsonOps;
import net.minecraft.core.Holder;
import net.minecraft.core.MappedRegistry;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.RegistryOps;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * A pack with mistakes in it, loaded by the game's own loader, one mistake at a time.
 *
 * <p>Every case here is measured behaviour from 2026-09-11 turned upside down. Before
 * {@code docs/plans/pack-mistakes.md} was built, each of these files made
 * {@code RegistryDataLoader} throw {@code ReportedException: Registry Loading} - which is not a part
 * that fails to load, it is a WORLD that does not open, with this mod's own sixty-six parts gone
 * along with the pack's. A player who mistyped one socket name lost every piece of every pack they
 * had installed, and on a dedicated server the process exited, because the throw lands on the
 * background executor whose handler answers a {@code ReportedException} with {@code System.exit(-1)}.
 *
 * <p>So the load itself is half of every assertion below: if any of these packs is refused, the line
 * that reads the registry never runs.
 *
 * <p><b>What this tier cannot cover.</b> The file that cannot be read AT ALL - broken markup, no
 * {@code asset_id} - is skipped by {@code RegistryLoadTaskMixin}, and a mixin is not applied in a
 * plain test JVM. The rule it applies is {@link PackSkips}, which {@link PackSkipsTest} covers here;
 * that it is wired to the loader at all is the gate's tier-2 {@code broken-pack} boot check, which
 * starts a real server with a real broken pack in it.
 */
class BrokenPackTest {
    private static final String NAMESPACE = "broken_pack_test";

    /** A part with nothing wrong with it, in the same pack as each mistake. */
    private static final String GOOD = """
        { "asset_id": "armorpieces:brooch",
          "description": {"translate": "decoration.armorpieces.brooch"},
          "anchors": ["crest"] }
        """;

    @BeforeEach
    void forgetEarlierProblems() {
        // The report is static, as the thing it reports on is - see PackProblems. One test's pack is
        // not another's, so each starts from nothing.
        PackProblems.clear();
    }

    private static Path pack(final Path dir, final Map<String, String> parts) throws IOException {
        final Path into = dir.resolve("data").resolve(NAMESPACE).resolve("armorpieces")
            .resolve("armor_decoration");
        Files.createDirectories(into);
        for (final Map.Entry<String, String> part : parts.entrySet()) {
            Files.writeString(into.resolve(part.getKey() + ".json"), part.getValue(), StandardCharsets.UTF_8);
        }
        Files.writeString(dir.resolve("pack.mcmeta"),
            "{\"pack\":{\"description\":\"broken on purpose\",\"pack_format\":107}}",
            StandardCharsets.UTF_8);
        return dir;
    }

    /** Loads the mod plus a pack holding one broken part and one good one, and hands back the broken. */
    private static ArmorDecoration loadBeside(final Path dir, final String broken) throws IOException {
        final ShippedData.Loaded loaded =
            ShippedData.withPack(pack(dir, Map.of("broken", broken, "good", GOOD)));
        assertNotNull(part(loaded, "good"),
            "the good part in the same pack was lost, which is the failure this whole plan is about");
        final ArmorDecoration mod = loaded.registry(ArmorPiecesRegistries.ARMOR_DECORATION)
            .getValue(ResourceKey.create(ArmorPiecesRegistries.ARMOR_DECORATION,
                Identifier.fromNamespaceAndPath("armorpieces", "brooch")));
        assertNotNull(mod, "the MOD's own parts were lost along with the pack's");
        return part(loaded, "broken");
    }

    private static ArmorDecoration part(final ShippedData.Loaded loaded, final String name) {
        return loaded.registry(ArmorPiecesRegistries.ARMOR_DECORATION).getValue(
            ResourceKey.create(ArmorPiecesRegistries.ARMOR_DECORATION,
                Identifier.fromNamespaceAndPath(NAMESPACE, name)));
    }

    private static List<PackProblem> problems() {
        return PackProblems.all().stream().map(Map.Entry::getKey).toList();
    }

    private static void assertReports(final String about) {
        assertTrue(problems().stream().anyMatch(problem -> problem.detail().contains(about)),
            () -> "nothing in the report mentions " + about + "; the report holds " + problems());
    }

    @Test
    void aSocketThatDoesNotExistCostsThatSocket(@TempDir final Path dir) throws IOException {
        final ArmorDecoration broken = loadBeside(dir, """
            { "asset_id": "armorpieces:brooch",
              "description": {"translate": "decoration.armorpieces.brooch"},
              "anchors": ["crest", "nose"] }
            """);
        assertNotNull(broken, "a part naming one socket that does not exist did not load at all");
        assertEquals(java.util.Set.of(DecorationAnchor.CREST), broken.anchors(),
            "the sockets that DO exist have to survive the one that does not");
        assertReports("anchor");
    }

    @Test
    void everySocketWrongIsAPartWithNone(@TempDir final Path dir) throws IOException {
        final ArmorDecoration broken = loadBeside(dir, """
            { "asset_id": "armorpieces:brooch",
              "description": {"translate": "decoration.armorpieces.brooch"},
              "anchors": ["nose"] }
            """);
        // Loaded rather than skipped on purpose: the id resolves, so an item wearing it keeps
        // working and the part comes back whole the day the file is fixed. That it can never be
        // applied is PackAudit's line to say, which needs a server - tier 2.
        assertNotNull(broken, "a part whose every socket is misspelled still has to load");
        assertTrue(broken.anchors().isEmpty(), "no socket in the file was real, so none can be kept");
        assertReports("anchor");
    }

    /**
     * A fitting id nothing defines: the part loads, and that one fitting can never be filled.
     *
     * <p>Read through the codec and the stand-in rule rather than through a whole load, because the
     * two halves of this one are a load apart. A cross-registry reference is resolved at the END of a
     * load, when the fitting registry freezes, and an id nothing defined fails that freeze - so what
     * saves the world is {@link MissingFittings#fill}, called from a mixin at the head of the freeze,
     * and a mixin is not applied in a test JVM.
     *
     * <p>The registry here is built the way the LOADER builds one, and that detail is the whole test.
     * A reference the loader could not resolve is not an absent key: it is an <i>intent</i>, a holder
     * already in the registry with nothing bound to it, which is why {@code containsKey} answers true
     * for exactly the ids this is here to fill. Measured on a real server on 2026-09-11, where a
     * {@code containsKey} guard skipped every stand-in and the freeze failed anyway.
     */
    @Test
    void aFittingNothingDefinesGetsAStandIn() {
        final ShippedData.Loaded mod = ShippedData.mod();
        // An ItemStack cannot be built until the items' default components have been baked - see
        // ShippedData - and "accepts nothing" is a claim about an item.
        ShippedData.bakeItemComponents(mod);
        final RegistryOps<JsonElement> ops = RegistryOps.create(JsonOps.INSTANCE, mod.full());
        // The read is what writes the id down; it fails here, because the mod's own registry is long
        // frozen and has no such fitting - which is exactly the state fill() is for.
        read(ops, """
            { "asset_id": "armorpieces:brooch",
              "description": {"translate": "decoration.armorpieces.brooch"},
              "anchors": ["collar"],
              "fittings": ["%s:no_such_fitting"] }
            """.formatted(NAMESPACE));

        final MappedRegistry<Fitting> fittings =
            new MappedRegistry<>(ArmorPiecesRegistries.FITTING, Lifecycle.stable());
        final ResourceKey<Fitting> key = ResourceKey.create(ArmorPiecesRegistries.FITTING,
            Identifier.fromNamespaceAndPath(NAMESPACE, "no_such_fitting"));
        // The dangling reference, made the way the loader makes one: a holder in the registry with
        // nothing bound to it, waiting for a file that never comes.
        final Holder<Fitting> dangling = fittings.createRegistrationLookup().getOrThrow(key);
        assertFalse(dangling.isBound(), "the fixture is wrong: that was supposed to be an intent");

        assertEquals(1, MissingFittings.fill(fittings), "the dangling id should have been filled once");
        assertTrue(dangling.isBound(),
            "the part is already built and holds THIS holder - a stand-in registered beside it "
                + "leaves the part with a landmine");
        assertTrue(dangling.value().accept(new ItemStack(Items.DIAMOND)).isEmpty(),
            "a stand-in has to accept NOTHING - it is a hole that cannot be filled, not a free fitting");
        // The point of all of it: the registry can now be frozen, which is what the load does next.
        fittings.freeze();
        assertReports("no installed pack defines it");
        assertEquals(0, MissingFittings.fill(fittings), "the ids are forgotten once they are filled");
    }

    @Test
    void anEffectThatCannotBeReadCostsThatEffect(@TempDir final Path dir) throws IOException {
        final ArmorDecoration broken = loadBeside(dir, """
            { "asset_id": "armorpieces:brooch",
              "description": {"translate": "decoration.armorpieces.brooch"},
              "anchors": ["crest"],
              "effects": [{"type": "%s:no_such_effect"}] }
            """.formatted(NAMESPACE));
        assertNotNull(broken, "a part naming an effect type no mod registers did not load");
        assertTrue(broken.effects().isEmpty(), "the unreadable effect had to go");
        assertReports("effect");
    }

    @Test
    void aLootRowThatCannotBeReadCostsThatRow(@TempDir final Path dir) throws IOException {
        final ArmorDecoration broken = loadBeside(dir, """
            { "asset_id": "armorpieces:brooch",
              "description": {"translate": "decoration.armorpieces.brooch"},
              "anchors": ["crest"],
              "loot": [{"table": "minecraft:chests/simple_dungeon", "chance": 0.2},
                       {"table": "minecraft:chests/stronghold_corridor", "chance": 12.0}] }
            """);
        assertNotNull(broken, "a part with one impossible chance did not load");
        assertEquals(1, broken.loot().size(), "the row that reads has to survive the row that does not");
        assertReports("loot row");
    }

    @Test
    void aPartWithNoNameIsNamedByItsId(@TempDir final Path dir) throws IOException {
        final ArmorDecoration broken = loadBeside(dir, """
            { "asset_id": "armorpieces:brooch", "anchors": ["crest"] }
            """);
        assertNotNull(broken, "a part with no description did not load");
        assertFalse(broken.description().getString().isBlank(),
            "a part with no description still has to have something to draw in a tooltip");
        assertReports("description");
    }

    /**
     * The two shapes of mistake that have no salvage in them, read by the codec alone.
     *
     * <p>{@code "anchors": "crest"} is not a list with a bad entry, it is not a list - there is
     * nothing to keep and nothing to guess; a part with no {@code asset_id} has nothing to draw.
     * Both fail the element, and in a game {@code RegistryLoadTaskMixin} then skips it by name and
     * the world opens. That last step is tier 2's to assert.
     *
     * <p>Deliberately NOT run through {@link ShippedData#withPack}: a registry load that fails throws
     * on Minecraft's background executor, whose uncaught handler answers a {@code ReportedException}
     * with {@code System.exit(-1)}, and a test that does that takes the whole suite's JVM with it -
     * measured, as a Gradle worker dying with {@code EOFException} and no report at all.
     */
    @Test
    void whatHasNoSalvageFailsTheElement() {
        final RegistryOps<JsonElement> ops = RegistryOps.create(JsonOps.INSTANCE, ShippedData.mod().full());
        assertTrue(read(ops, """
            { "asset_id": "armorpieces:brooch",
              "description": {"translate": "decoration.armorpieces.brooch"},
              "anchors": "crest" }
            """).error().isPresent(), "`anchors` given a string decoded to something; it has no salvage");
        assertTrue(read(ops, """
            { "description": {"translate": "decoration.armorpieces.brooch"}, "anchors": ["crest"] }
            """).error().isPresent(), "a part with no asset_id decoded; it has nothing to draw");
    }

    /**
     * Every warning has to name the file it is about.
     *
     * <p>A pack author reading "an anchor named `nose` was dropped" has been told nothing they can
     * open and edit. {@link PackFile} is what carries the id and the pack down into the codec - in a
     * game it is written by {@code PendingRegistrationMixin}, and here by hand, which is the same
     * contract seen from the other side.
     */
    @Test
    void aWarningNamesTheFileAndThePack() {
        final RegistryOps<JsonElement> ops = RegistryOps.create(JsonOps.INSTANCE, ShippedData.mod().full());
        PackFile.reading(ResourceKey.create(ArmorPiecesRegistries.ARMOR_DECORATION,
            Identifier.fromNamespaceAndPath(NAMESPACE, "coral_crown")), "coral");
        try {
            read(ops, """
                { "asset_id": "armorpieces:brooch",
                  "description": {"translate": "decoration.armorpieces.brooch"},
                  "anchors": ["crest", "nose"] }
                """);
        } finally {
            PackFile.done();
        }
        assertTrue(problems().stream().anyMatch(problem ->
                problem.subject().contains(NAMESPACE + ":coral_crown")
                    && problem.subject().contains("coral")),
            () -> "the warning does not name the file it came from: " + problems());
    }

    private static DataResult<ArmorDecoration> read(final RegistryOps<JsonElement> ops, final String json) {
        return ArmorDecoration.DIRECT_CODEC.parse(ops, JsonParser.parseString(json));
    }
}
