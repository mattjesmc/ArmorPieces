package com.mattjesmc.armorpieces.loot;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.mattjesmc.armorpieces.GameBootstrap;
import com.mattjesmc.armorpieces.cloth.Cloth;
import com.mattjesmc.armorpieces.config.ServerConfigFixture;
import com.mattjesmc.armorpieces.data.ShippedData;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.DecorationLoot;
import com.mattjesmc.armorpieces.skin.ArmorSkin;
import com.mojang.serialization.JsonOps;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import net.fabricmc.fabric.api.loot.v3.LootTableEvents;
import net.fabricmc.fabric.api.loot.v3.LootTableSource;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.RegistryOps;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.storage.loot.LootPool;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.level.storage.loot.entries.LootItem;
import net.minecraft.world.level.storage.loot.providers.number.ConstantValue;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * What the mod actually WRITES into a loot table: {@link DecorationLootTables}, run as the game runs
 * it, and the built table read back as JSON.
 *
 * <p>Nothing had ever asked this in a JVM. The tier-2 scenarios roll the tables on a real server and
 * measure the share a group's members get, which is the right question about odds and the wrong one
 * about shape - by the time a chest has been opened ten thousand times, "one pool, rolled once, with
 * one {@code random_chance} on it" has already been assumed rather than checked. That shape is the
 * whole design (see {@link LootGroup}): it is what keeps the odds a property of the TABLE, so that a
 * ninety-first part changes which part is found and never how often, and it is what keeps two of
 * ours out of one chest. A second pool, or a condition per entry, would pass every roll test in the
 * suite by looking like slightly different luck.
 *
 * <p>Three worlds are asked, and each is asked what only it can answer:
 *
 * <ul>
 *   <li><b>Everything this repository ships</b>, swept: every table any group or any {@code loot}
 *       row names gets the shape above, one entry per member, and a report that agrees with the
 *       pool that was built.</li>
 *   <li><b>A pack the test writes</b>, where the numbers are the test's own: two groups overlapping
 *       on one table pin the rules that only show up in an overlap - the highest chance wins, a
 *       member offered twice is one entry at the best weight, and a group naming a tag nobody
 *       installed offers nothing.</li>
 *   <li><b>That same pack under a server owner's config</b>: the off switch, the multiplier, and
 *       every field of a group override. All of it reaches a chest only through this class, and none
 *       of it was covered anywhere.</li>
 * </ul>
 *
 * <p>The built table is read as JSON rather than through the object, because a {@link LootTable}
 * keeps its pools to itself and because the JSON is the form a person can be shown when an assertion
 * fails. It is also the form the game would write, which is the point.
 */
class LootTablesTest {
    /** The namespace of the pack this test writes, and of the tables only it names. */
    private static final String NS = "loot_gate_test";

    /** Named by both fixture groups: the overlap, and everything the overlap decides. */
    private static final String VAULT = NS + ":chests/vault";
    /** Named by one fixture group, at a chance of 1. */
    private static final String ALWAYS = NS + ":chests/always";
    /** Named by the group whose tag nothing defines. */
    private static final String GHOST = NS + ":chests/ghost";
    /** Named by nobody at all - what a server owner's {@code add} reaches. */
    private static final String ADDED = NS + ":chests/added";

    /** In alpha's tag only. */
    private static final String BROOCH = "armorpieces:brooch";
    /** In both fixture tags: the member offered twice. */
    private static final String CIRCLET = "armorpieces:circlet";
    /** In beta's tag only. */
    private static final String GORGET = "armorpieces:gorget";

    private static ShippedData.Loaded shipped;
    private static ShippedData.Loaded fixture;

    @TempDir
    static Path packDir;

    private static boolean hooked;

    @BeforeAll
    static void world() throws IOException {
        // First line, and it has to be: an argument is evaluated before the call it is passed to, so
        // a fixture method that touched Items on its way past would initialise BuiltInRegistries in
        // an unbootstrapped JVM and take every later test in this JVM down with it.
        GameBootstrap.content();

        shipped = ShippedData.everything();
        ShippedData.bindTags(shipped);
        fixture = ShippedData.withPack(writePack(packDir));
        ShippedData.bindTags(fixture);

        // Through the event, not through the method: that MODIFY is where this hangs is half of what
        // makes the mod's loot happen at all, and register() is the only place that says so. Once
        // per JVM - a second listener would build every pool twice.
        if (!hooked) {
            DecorationLootTables.register();
            hooked = true;
        }
    }

    /**
     * Every test here is its own load of its own packs, which in a game is a boundary the mod clears
     * its reports at - and this JVM has no such boundary, so it stands at one on purpose.
     *
     * <p>Writing this found the thing the boundary was missing. A report was only ever dropped at the
     * START of a datapack reload, and a reload is not the only way one JVM sees two sets of packs: a
     * single-player client opens a world, quits to the menu and opens another, and the second world's
     * tables were explained partly by the first world's. {@link DecorationLootTables#register} clears
     * on {@code SERVER_STOPPED} too now, and this is the same clearing, by hand.
     */
    @BeforeEach
    void aLoadOfItsOwn() {
        DecorationLootTables.forget();
    }

    @AfterEach
    void aServerWhoseOwnerTouchedNothing() {
        ServerConfigFixture.reset();
    }

    // ---------------------------------------------------------------- the shape, over what ships

    /**
     * The design, over every table this repository reaches: ONE pool, rolled ONCE, holding one entry
     * per member, under at most one {@code random_chance}.
     *
     * <p>Swept rather than sampled because the rule is about tables the mod does not choose - a pack
     * names what it likes - and because the interesting tables are exactly the ones several sources
     * reached, which is not knowable from any one file.
     */
    @Test
    void everyTableTheModTouchesGetsOnePoolRolledOnce() {
        final Set<String> tables = tablesNamedBy(shipped);
        assertFalse(tables.isEmpty(), "this repository ships loot; no table was named by anything");

        final List<String> wrong = new ArrayList<>();
        for (final String table : tables) {
            final Built built = modify(shipped, table);
            try {
                final JsonObject pool = onlyPool(built);
                assertEquals("1.0", pool.get("rolls").getAsString(),
                    "rolled more than once, so one chest could hold two of ours");

                final List<JsonObject> entries = entries(pool);
                assertFalse(entries.isEmpty(), "a pool with no entries was added");
                assertEquals(entries.size(), distinct(entries).size(),
                    "the same member is in the pool twice: " + entries);

                final LootReport report = built.report();
                assertNotNull(report, "a pool was added and nothing was recorded about it");
                assertEquals(entries.size(), report.members(),
                    "the report and the pool disagree about how many members reached this table");
                assertEquals(chanceOf(pool), report.chance(), 1.0e-6f,
                    "the report and the pool disagree about the odds");
                assertFalse(report.sources().isEmpty(), "a table was reached by nothing");

                for (final JsonObject entry : entries) {
                    assertEquals("minecraft:item", entry.get("type").getAsString());
                    assertTrue(entry.get("name").getAsString().startsWith("armorpieces:"),
                        "something other than one of our templates: " + entry);
                    assertTrue(weight(entry) >= 1, "a non-positive weight: " + entry);
                }
            } catch (final AssertionError failed) {
                wrong.add(table + ": " + failed.getMessage() + "\n    " + built.json());
            }
        }
        assertTrue(wrong.isEmpty(), () -> "tables the mod built wrongly:\n  " + String.join("\n  ", wrong));
    }

    /** A table nobody named is not touched, and nothing is recorded about it. */
    @Test
    void aTableNoPackNamesIsLeftAlone() {
        final Built built = modify(shipped, NS + ":chests/nothing_names_this");
        assertTrue(pools(built.json()).isEmpty(), "a pool was added to a table nothing named");
        assertNull(built.report(), "a table nothing was added to was reported on anyway");
    }

    /**
     * The table's own pools survive. A chest that would have held a diamond still holds it - the mod
     * ADDS a pool and rewrites nothing, which is what lets it reach a table two datapacks are already
     * fighting over.
     */
    @Test
    void theTablesOwnPoolsAreUntouched() {
        final LootTable.Builder table = LootTable.lootTable().withPool(
            LootPool.lootPool().setRolls(ConstantValue.exactly(1.0f))
                .add(LootItem.lootTableItem(Items.DIAMOND)));
        final Built built = modify(fixture, VAULT, table);

        final List<JsonObject> pools = pools(built.json());
        assertEquals(2, pools.size(), "the table's own pool and ours: " + built.json());
        assertEquals("minecraft:diamond",
            entries(pools.get(0)).get(0).get("name").getAsString(),
            "ours was written over the table's own pool rather than after it");
    }

    // ------------------------------------------------------- the rules, on a pack the test wrote

    /**
     * Two groups on one table: the higher chance is the one written, and the meaner group's members
     * ride along on it. Both are named in the report, at the number each asked for.
     */
    @Test
    void theHighestChanceAnySourceAskedForIsTheOneWritten() {
        final Built built = modify(fixture, VAULT);
        final LootReport report = report(built);

        assertEquals(0.4f, chanceOf(onlyPool(built)), 1.0e-6f,
            "alpha asked for 0.4 and beta for 0.2; the table is alpha's");
        assertEquals(0.4f, report.packChance(), 1.0e-6f);
        assertFalse(report.scaled(), "nothing in the config touched this");
        assertEquals(Set.of(NS + ":alpha", NS + ":beta"), sourceNames(report),
            "both groups reached the table, so both have to be explainable");
        assertEquals(0.2f, source(report, NS + ":beta").chance(), 1.0e-6f,
            "a source below the final number is one whose members ride along, and says so");
    }

    /**
     * A member two groups both offer is ONE entry, at the best weight it was offered - never two
     * entries, which would quietly double its share of the roll.
     */
    @Test
    void aMemberOfferedTwiceIsOneEntryAtTheBestWeight() {
        final Built built = modify(fixture, VAULT);
        final List<JsonObject> entries = entries(onlyPool(built));

        assertEquals(3, entries.size(), "brooch, circlet and gorget, with circlet offered twice: " + entries);
        assertEquals(3, report(built).members());
        assertEquals(1, entries.stream().filter(e -> holds(e, CIRCLET)).count(),
            "the member both groups offer is in the pool twice: " + entries);
        assertEquals(3, weight(entry(entries, CIRCLET)),
            "alpha offered it at weight 3 and beta at 1; the best weight is the one that stands");
        assertEquals(1, weight(entry(entries, GORGET)), "beta's own member keeps beta's weight");
    }

    /** At a chance of 1 the condition is left off: "always" is readable in the built table. */
    @Test
    void aChanceOfOneIsWrittenAsNoConditionAtAll() {
        final Built built = modify(fixture, ALWAYS);
        final JsonObject pool = onlyPool(built);

        assertFalse(pool.has("conditions"),
            "a random_chance of 1 is the identity, and vanilla rolls it anyway: " + pool);
        assertEquals(1.0f, report(built).chance(), 1.0e-6f);
        assertEquals(2, entries(pool).size(), "beta's two members");
    }

    /**
     * A group naming a tag no installed pack defines offers nothing, and the table is left alone.
     *
     * <p>{@link AbsentTagGroupTest} is the same case one step earlier - that the world LOADS at all.
     * This is what the player then finds in the chest: not an empty pool, not a pool that rolls and
     * produces air, but a table the mod never touched.
     */
    @Test
    void aGroupWhoseTagNobodyInstalledReachesNoTable() {
        final Built built = modify(fixture, GHOST);
        assertTrue(pools(built.json()).isEmpty(),
            "a group with no members still added a pool: " + built.json());
        assertNull(built.report(), "and reported that it had");
    }

    /**
     * A {@code loot} row on a part's own file is its own source, separate from any group's, and the
     * row's own weight travels with it.
     *
     * <p>The numbers are {@code banner.json}'s, on the mod alone: it names the outpost at 0.15 and
     * weight 2, and the {@code knightly} group names the same table at 0.1. If that file changes,
     * this changes with it - which is the point of pinning it, since the direct route is the one a
     * pack author reaches for when they want one piece in one chest.
     */
    @Test
    void aPartsOwnLootRowIsItsOwnSource() {
        final Built built = modify(ShippedData.mod(), "minecraft:chests/pillager_outpost");
        final LootReport report = report(built);

        final LootReport.Source direct = source(report, LootReport.DIRECT);
        assertEquals(0.15f, direct.chance(), 1.0e-6f, "banner.json names the outpost at 0.15");
        assertEquals(2, direct.weight(), "and at weight 2");
        assertTrue(sourceNames(report).contains("armorpieces:knightly"),
            "the group names it too, and both routes are supposed to be explainable");
        assertEquals(0.15f, chanceOf(onlyPool(built)), 1.0e-6f,
            "the part's row is the more generous of the two, so it is the table's number");
        assertEquals(2, weight(entry(entries(onlyPool(built)), "armorpieces:banner")),
            "the row's weight is what the entry carries");
    }

    // ------------------------------------------------------------------- what the server owner says

    /** The off switch: nothing is added to any table, and nothing is reported. */
    @Test
    void theOffSwitchAddsNothingAnywhere() {
        ServerConfigFixture.configure("""
            { "enabled": false }
            """);
        final Built built = modify(fixture, VAULT);
        assertTrue(pools(built.json()).isEmpty(), "loot is off and a pool was added anyway");
        assertNull(built.report());
    }

    /** The multiplier moves the odds and says so, without touching what the packs asked for. */
    @Test
    void theMultiplierScalesTheChanceAndTheReportKeepsBoth() {
        ServerConfigFixture.configure("""
            { "chance_multiplier": 0.5 }
            """);
        final Built built = modify(fixture, VAULT);
        final LootReport report = report(built);

        assertEquals(0.2f, chanceOf(onlyPool(built)), 1.0e-6f, "0.4 halved");
        assertEquals(0.4f, report.packChance(), 1.0e-6f, "what the packs asked for is still knowable");
        assertEquals(0.2f, report.chance(), 1.0e-6f);
        assertTrue(report.scaled(), "which is what /armorpieces loot explain says out loud");
        assertEquals(3, entries(onlyPool(built)).size(), "the members are not the multiplier's business");
    }

    /**
     * A multiplier of zero is "none of this", and the pool is left off entirely rather than written
     * with a chance that can never roll - which would still show in the built table.
     */
    @Test
    void aMultiplierOfZeroLeavesNoPoolBehind() {
        ServerConfigFixture.configure("""
            { "chance_multiplier": 0.0 }
            """);
        final Built built = modify(fixture, VAULT);
        assertTrue(pools(built.json()).isEmpty(), "an unrollable pool was written: " + built.json());
        assertNull(built.report());
    }

    /** Above 1 is allowed and clamped where it is used: a table cannot be more than certain. */
    @Test
    void aGenerousMultiplierIsClampedToCertain() {
        ServerConfigFixture.configure("""
            { "chance_multiplier": 10.0 }
            """);
        final Built built = modify(fixture, VAULT);
        assertEquals(1.0f, report(built).chance(), 1.0e-6f);
        assertFalse(onlyPool(built).has("conditions"), "certain is written as no condition");
    }

    /** A group switched off contributes nothing; the others are untouched. */
    @Test
    void aGroupSwitchedOffDropsOutAndTheRestStand() {
        ServerConfigFixture.configure("""
            { "groups": { "%s:beta": { "enabled": false } } }
            """.formatted(NS));
        final Built built = modify(fixture, VAULT);
        final LootReport report = report(built);

        assertEquals(Set.of(NS + ":alpha"), sourceNames(report), "beta was switched off");
        assertEquals(0.4f, chanceOf(onlyPool(built)), 1.0e-6f, "and alpha's number was already the table's");
        assertEquals(2, entries(onlyPool(built)).size(), "alpha's two members, and no third");
        assertTrue(entries(onlyPool(built)).stream().noneMatch(e -> holds(e, GORGET)),
            "the member only beta offered went with beta");
        assertTrue(pools(modify(fixture, ALWAYS).json()).isEmpty(),
            "and the table only beta named is gone entirely");
    }

    /**
     * An override's chance replaces the group's for every table it names, including the ones the
     * group file gave a chance of their own: the server owner's number is the last word.
     */
    @Test
    void anOverridesChanceIsTheLastWord() {
        ServerConfigFixture.configure("""
            { "groups": { "%s:alpha": { "chance": 0.05 } } }
            """.formatted(NS));

        final Built vault = modify(fixture, VAULT);
        assertEquals(0.2f, chanceOf(onlyPool(vault)), 1.0e-6f,
            "alpha was cut below beta, so beta's 0.2 is the table's now");
        assertEquals(3, entries(onlyPool(vault)).size(), "both groups still offer their members");
        assertTrue(source(vault.report(), NS + ":alpha").overridden(),
            "an overridden source has to say so, or explain is misleading");
        assertFalse(source(vault.report(), NS + ":beta").overridden(),
            "and one the owner said nothing about has to not");

        ServerConfigFixture.configure("""
            { "groups": { "%s:beta": { "chance": 0.05 } } }
            """.formatted(NS));
        assertEquals(0.05f, chanceOf(onlyPool(modify(fixture, ALWAYS))), 1.0e-6f,
            "and it replaces even the chance a table wrote for itself - beta's file said 1.0");
    }

    /** An override's weight replaces the group's, and travels to the members it offers. */
    @Test
    void anOverridesWeightReachesTheEntries() {
        ServerConfigFixture.configure("""
            { "groups": { "%s:alpha": { "weight": 9 } } }
            """.formatted(NS));
        final List<JsonObject> entries = entries(onlyPool(modify(fixture, VAULT)));

        assertEquals(9, weight(entry(entries, BROOCH)), "alpha's own member carries the new weight");
        assertEquals(9, weight(entry(entries, CIRCLET)),
            "and the shared one takes the best of the two, which is now alpha's");
        assertEquals(1, weight(entry(entries, GORGET)), "beta's member is not alpha's business");
    }

    /** A table the owner removed is out however the pack named it. */
    @Test
    void aRemovedTableIsOutHoweverThePackNamedIt() {
        ServerConfigFixture.configure("""
            { "groups": { "%s:beta": { "remove": ["%s"] } } }
            """.formatted(NS, VAULT));
        final Built built = modify(fixture, VAULT);

        assertEquals(Set.of(NS + ":alpha"), sourceNames(built.report()));
        assertEquals(0.4f, chanceOf(onlyPool(built)), 1.0e-6f, "alpha's number, alone now");
        assertEquals(2, entries(onlyPool(built)).size(), "only alpha's members are left");
        assertEquals(2, entries(onlyPool(modify(fixture, ALWAYS))).size(),
            "and beta's other table is untouched");
    }

    /**
     * A table the owner ADDED reaches a group that never named it - the way a modded container joins
     * a theme with no datapack at all - and the three ways its chance can be decided are the order
     * they are decided in: the added entry's own, then the override's, then the group's.
     */
    @Test
    void anAddedTableTakesTheFirstChanceThatIsOffered() {
        ServerConfigFixture.configure("""
            { "groups": { "%s:alpha": { "add": ["%s"] } } }
            """.formatted(NS, ADDED));
        assertEquals(0.4f, chanceOf(onlyPool(modify(fixture, ADDED))), 1.0e-6f,
            "a bare id takes the group's own chance");

        ServerConfigFixture.configure("""
            { "groups": { "%s:alpha": { "chance": 0.5, "add": ["%s"] } } }
            """.formatted(NS, ADDED));
        assertEquals(0.5f, chanceOf(onlyPool(modify(fixture, ADDED))), 1.0e-6f,
            "and the override's, when the owner gave the group one");

        ServerConfigFixture.configure("""
            { "groups": { "%s:alpha": { "chance": 0.5,
                                        "add": [{"table": "%s", "chance": 0.75}] } } }
            """.formatted(NS, ADDED));
        final Built built = modify(fixture, ADDED);
        assertEquals(0.75f, chanceOf(onlyPool(built)), 1.0e-6f,
            "and the entry's own beats both, which is how one table stays generous");
        assertEquals(2, entries(onlyPool(built)).size(), "alpha's members, in a table alpha never named");
        assertTrue(source(built.report(), NS + ":alpha").overridden());
    }

    /** Removal is applied after addition, so a table in both is removed. */
    @Test
    void aTableInBothAddAndRemoveIsRemoved() {
        ServerConfigFixture.configure("""
            { "groups": { "%s:alpha": { "add": ["%s"], "remove": ["%s"] } } }
            """.formatted(NS, ADDED, ADDED));
        assertTrue(pools(modify(fixture, ADDED).json()).isEmpty(),
            "add and remove disagreed and addition won");
    }

    // ------------------------------------------------------------------------------- the fixtures

    /**
     * The pack: two groups that overlap on one table, and one whose tag nothing defines.
     *
     * <p>Written rather than borrowed from what ships because every number this class asserts is in
     * it. A shipped group is content - it moves when the content moves - and a rule pinned to it
     * would be a rule that has to be re-read every time a part is added.
     */
    private static Path writePack(final Path dir) throws IOException {
        final Path tags = dir.resolve("data").resolve(NS).resolve("tags")
            .resolve("armorpieces").resolve("armor_decoration");
        Files.createDirectories(tags);
        write(tags.resolve("alpha.json"), """
            { "values": ["%s", "%s"] }
            """.formatted(BROOCH, CIRCLET));
        write(tags.resolve("beta.json"), """
            { "values": ["%s", "%s"] }
            """.formatted(CIRCLET, GORGET));

        final Path groups = dir.resolve("data").resolve(NS).resolve("armorpieces").resolve("loot_group");
        Files.createDirectories(groups);
        // Alpha is the GENEROUS one, and it is also the one the loader reads first. That is
        // deliberate: with the generous group last, "the highest chance wins" and "the last chance
        // read wins" produce the same table, and every assertion below would hold for both.
        write(groups.resolve("alpha.json"), """
            { "chance": 0.4, "weight": 3,
              "tables": ["%s"],
              "parts": "#%s:alpha" }
            """.formatted(VAULT, NS));
        write(groups.resolve("beta.json"), """
            { "chance": 0.2, "weight": 1,
              "tables": ["%s", {"table": "%s", "chance": 1.0}],
              "parts": "#%s:beta" }
            """.formatted(VAULT, ALWAYS, NS));
        write(groups.resolve("ghost.json"), """
            { "chance": 0.5,
              "tables": ["%s"],
              "parts": "#%s:nothing_defines_this" }
            """.formatted(GHOST, NS));
        return dir;
    }

    private static void write(final Path file, final String json) throws IOException {
        Files.writeString(file, json, StandardCharsets.UTF_8);
    }

    // ------------------------------------------------------------------------------ the machinery

    /** One table, built: the JSON the game would write, and what the mod recorded about it. */
    private record Built(JsonObject json, @Nullable LootReport report) {}

    private static Built modify(final ShippedData.Loaded loaded, final String table) {
        return modify(loaded, table, LootTable.lootTable());
    }

    /**
     * Runs the mod over one loot table exactly as a loading server does: the Fabric event, the
     * table's builder, and the registries the load produced.
     */
    private static Built modify(
        final ShippedData.Loaded loaded, final String table, final LootTable.Builder builder
    ) {
        final ResourceKey<LootTable> key =
            ResourceKey.create(Registries.LOOT_TABLE, Identifier.parse(table));
        LootTableEvents.MODIFY.invoker()
            .modifyLootTable(key, builder, LootTableSource.VANILLA, loaded.full());
        final RegistryOps<JsonElement> ops =
            loaded.full().createSerializationContext(JsonOps.INSTANCE);
        final JsonElement json = LootTable.DIRECT_CODEC.encodeStart(ops, builder.build())
            .getOrThrow(message -> new AssertionError(
                "the table the mod built cannot be written down: " + message));
        return new Built(json.getAsJsonObject(), DecorationLootTables.report(key));
    }

    /** Every loot table any group or any {@code loot} row in {@code loaded} names. */
    private static Set<String> tablesNamedBy(final ShippedData.Loaded loaded) {
        final Set<String> tables = new LinkedHashSet<>();
        loaded.registry(ArmorPiecesRegistries.ARMOR_DECORATION).stream()
            .map(ArmorDecoration::loot).forEach(rows -> rows.forEach(row -> tables.add(id(row))));
        loaded.registry(ArmorPiecesRegistries.ARMOR_SKIN).stream()
            .map(ArmorSkin::loot).forEach(rows -> rows.forEach(row -> tables.add(id(row))));
        loaded.registry(ArmorPiecesRegistries.CLOTH).stream()
            .map(Cloth::loot).forEach(rows -> rows.forEach(row -> tables.add(id(row))));
        loaded.registry(ArmorPiecesRegistries.LOOT_GROUP).stream()
            .forEach(group -> group.tables()
                .forEach(entry -> tables.add(entry.table().identifier().toString())));
        return tables;
    }

    private static String id(final DecorationLoot row) {
        return row.table().identifier().toString();
    }

    private static List<JsonObject> pools(final JsonObject table) {
        if (!table.has("pools")) {
            return List.of();
        }
        final JsonArray pools = table.getAsJsonArray("pools");
        final List<JsonObject> out = new ArrayList<>(pools.size());
        pools.forEach(pool -> out.add(pool.getAsJsonObject()));
        return out;
    }

    /** The one pool the mod added, and the assertion that it added exactly one. */
    private static JsonObject onlyPool(final Built built) {
        final List<JsonObject> pools = pools(built.json());
        assertEquals(1, pools.size(),
            "one pool per table is the whole design; got " + pools.size() + ": " + built.json());
        return pools.get(0);
    }

    private static List<JsonObject> entries(final JsonObject pool) {
        final List<JsonObject> out = new ArrayList<>();
        pool.getAsJsonArray("entries").forEach(entry -> out.add(entry.getAsJsonObject()));
        return out;
    }

    private static Set<String> distinct(final List<JsonObject> entries) {
        return entries.stream().map(JsonObject::toString).collect(Collectors.toCollection(LinkedHashSet::new));
    }

    /** The odds on the pool: the {@code random_chance} it carries, or 1 when it carries none. */
    private static float chanceOf(final JsonObject pool) {
        if (!pool.has("conditions")) {
            return 1.0f;
        }
        final JsonArray conditions = pool.getAsJsonArray("conditions");
        assertEquals(1, conditions.size(), "one chance per pool, not one per entry: " + pool);
        final JsonObject condition = conditions.get(0).getAsJsonObject();
        assertEquals("minecraft:random_chance", condition.get("condition").getAsString());
        return condition.get("chance").getAsFloat();
    }

    private static int weight(final JsonObject entry) {
        return entry.has("weight") ? entry.get("weight").getAsInt() : 1;
    }

    /** Whether this entry is the template for {@code member} - the id is in the component it sets. */
    private static boolean holds(final JsonObject entry, final String member) {
        return entry.toString().contains("\"" + member + "\"");
    }

    private static JsonObject entry(final List<JsonObject> entries, final String member) {
        return entries.stream().filter(e -> holds(e, member)).findFirst()
            .orElseThrow(() -> new AssertionError(member + " is not in the pool: " + entries));
    }

    private static LootReport report(final Built built) {
        assertNotNull(built.report(), "nothing was recorded about a table a pool was added to");
        return built.report();
    }

    private static Set<String> sourceNames(final @Nullable LootReport report) {
        assertNotNull(report);
        return report.sources().stream().map(LootReport.Source::name)
            .collect(Collectors.toCollection(LinkedHashSet::new));
    }

    private static LootReport.Source source(final @Nullable LootReport report, final String name) {
        assertNotNull(report);
        final Optional<LootReport.Source> found =
            report.sources().stream().filter(s -> s.name().equals(name)).findFirst();
        assertTrue(found.isPresent(), name + " did not reach the table; sources: " + sourceNames(report));
        return found.get();
    }
}
