package com.mattjesmc.armorpieces.loot;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.mattjesmc.armorpieces.GameBootstrap;
import com.mattjesmc.armorpieces.data.ShippedData;
import com.mojang.serialization.JsonOps;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.resources.RegistryOps;
import net.minecraft.util.ProblemReporter;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.level.storage.loot.ValidationContext;
import net.minecraft.world.level.storage.loot.parameters.LootContextParamSets;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * The two pieces this mod puts into <b>somebody else's</b> loot table, read and validated the way a
 * datapack's file is: {@code armorpieces:template}, the entry that hands out the template for some
 * member of a tag, and {@code armorpieces:set_decoration}, the function that puts a part on the
 * armor an entry already produced.
 *
 * <p>Both exist for one reason and it is the reason they need a test of their own: a modpack's table
 * must be able to name our content without naming a PIECE. A named part that is not installed fails
 * the whole file, which is the worst way for content to be optional, so both take a tag and resolve
 * it late - and the price of late resolution is that a mistake is invisible until the table is
 * rolled. What answers that price is {@code validate}, which runs as the pack loads and says, in the
 * log, what could never come out of this entry. Nothing had ever run it.
 *
 * <p>So the assertions here are in two halves, and the pair is the point:
 *
 * <ul>
 *   <li>a tag nobody installed <b>loads</b> - the table parses, the pack is fine, the other entries
 *       are untouched;</li>
 *   <li>and it is <b>said out loud</b> - a problem naming what was empty, rather than a chest that
 *       quietly hands out nothing for the rest of the world's life.</li>
 * </ul>
 *
 * <p>What is NOT here is the roll: {@link TemplateEntry#expand} and
 * {@link SetDecorationFunction#run} both go through {@code context.getLevel()}, which is a server,
 * and a server is the gate's tier 2 - where the {@code foreign-table} scenario pushes a table and
 * takes what comes out of it. This is everything the load can be held to before that.
 */
class ForeignTableTest {
    private static ShippedData.Loaded loaded;
    private static RegistryOps<JsonElement> ops;

    @BeforeAll
    static void world() {
        GameBootstrap.content();
        loaded = ShippedData.mod();
        ShippedData.bindTags(loaded);
        // The entry builds the STACKS it could hand out to answer whether it could hand out
        // anything, and an item with no baked components cannot be built at all.
        ShippedData.bakeItemComponents(loaded);
        ops = loaded.full().createSerializationContext(JsonOps.INSTANCE);
    }

    // ------------------------------------------------------------------ armorpieces:template

    /** The shape the feature is for: a table asking for "a knightly part" without naming one. */
    @Test
    void aTableMayAskForAMemberOfATagWithoutNamingOne() {
        final LootTable table = table("""
            { "type": "minecraft:chest",
              "pools": [ { "rolls": 1, "entries": [
                { "type": "armorpieces:template", "parts": "#armorpieces:knightly" } ] } ] }
            """);
        assertEquals(List.of(), problems(table));
    }

    /** All four families at once, and the ordinary entry fields alongside them. */
    @Test
    void oneEntryMayNamePartsSkinsClothsAndFittings() {
        final LootTable table = table("""
            { "type": "minecraft:chest",
              "pools": [ { "rolls": 1, "entries": [
                { "type": "armorpieces:template",
                  "parts": "#armorpieces:court",
                  "skins": ["armorpieces:plate"],
                  "cloths": ["armorpieces:tunic"],
                  "fittings": "#armorpieces:common",
                  "weight": 3 } ] } ] }
            """);
        assertEquals(List.of(), problems(table));
    }

    /**
     * A table that names a tag nobody installed still LOADS - and is then told what is wrong with it.
     *
     * <p>This is the whole bargain of {@link MemberSet}. The alternative, refusing the file, is the
     * failure a player meets when they install one pack of a line and not another; the danger of not
     * refusing it is an entry that silently never fires, which is the thing hardest to find by
     * playing. Both halves are asserted here because either alone is the wrong design.
     */
    @Test
    void aTagNobodyInstalledLoadsAndIsSaidOutLoud() {
        final LootTable table = table("""
            { "type": "minecraft:chest",
              "pools": [ { "rolls": 1, "entries": [
                { "type": "armorpieces:template", "parts": "#armorpieces:no_pack_defines_this" } ] } ] }
            """);
        assertSaid(table, "has no members installed");
    }

    /** Naming no family at all is an authoring mistake, and a different one. */
    @Test
    void anEntryThatNamesNothingIsAnAuthoringMistake() {
        final LootTable table = table("""
            { "type": "minecraft:chest",
              "pools": [ { "rolls": 1, "entries": [ { "type": "armorpieces:template" } ] } ] }
            """);
        assertSaid(table, "names no parts, skins, cloths or fittings");
    }

    // ------------------------------------------------------------ armorpieces:set_decoration

    /** The documented example: a helmet that comes out of the chest already wearing a circlet. */
    @Test
    void aFunctionMayDressTheArmorAnEntryProduced() {
        final LootTable table = table("""
            { "type": "minecraft:chest",
              "pools": [ { "rolls": 1, "entries": [
                { "type": "minecraft:item", "name": "minecraft:golden_helmet",
                  "functions": [ { "function": "armorpieces:set_decoration",
                    "socket": "brow", "part": "armorpieces:circlet", "material": "minecraft:gold",
                    "fittings": { "armorpieces:gemstone": "minecraft:emerald" } } ] } ] } ] }
            """);
        assertEquals(List.of(), problems(table));
    }

    /**
     * A part that cannot go in the socket named is said at load, not discovered by a player holding
     * a plain helmet - the stack would simply have been passed through untouched.
     */
    @Test
    void aPartThatDoesNotFitTheSocketIsSaidAtLoad() {
        final LootTable table = table("""
            { "type": "minecraft:chest",
              "pools": [ { "rolls": 1, "entries": [
                { "type": "minecraft:item", "name": "minecraft:iron_chestplate",
                  "functions": [ { "function": "armorpieces:set_decoration",
                    "socket": "back", "part": "armorpieces:circlet",
                    "material": "minecraft:iron" } ] } ] } ] }
            """);
        assertSaid(table, "fits socket back");
    }

    /** And so is a fitting the part has not got - the map would have been thrown away in silence. */
    @Test
    void aFittingThePartHasNotGotIsSaidAtLoad() {
        final LootTable table = table("""
            { "type": "minecraft:chest",
              "pools": [ { "rolls": 1, "entries": [
                { "type": "minecraft:item", "name": "minecraft:golden_helmet",
                  "functions": [ { "function": "armorpieces:set_decoration",
                    "socket": "brow", "part": "armorpieces:circlet", "material": "minecraft:gold",
                    "fittings": { "armorpieces:guard": "minecraft:iron" } } ] } ] } ] }
            """);
        assertSaid(table, "has no fitting armorpieces:guard");
    }

    /**
     * A tag on the function's own {@code part} field: one member that fits the socket is enough, and
     * the ones that do not are simply never drawn.
     *
     * <p>{@code crest} is chosen because the knightly theme has crests in it. If that stops being
     * true this fails with the sentence that says so, which is the right way for a content change to
     * reach a test.
     */
    @Test
    void aTagIsEnoughIfOneOfItsMembersFitsTheSocket() {
        final LootTable table = table("""
            { "type": "minecraft:chest",
              "pools": [ { "rolls": 1, "entries": [
                { "type": "minecraft:item", "name": "minecraft:iron_helmet",
                  "functions": [ { "function": "armorpieces:set_decoration",
                    "socket": "crest", "part": "#armorpieces:knightly",
                    "material": "minecraft:iron" } ] } ] } ] }
            """);
        assertEquals(List.of(), problems(table));
    }

    // --------------------------------------------------------------------------- both, written back

    /**
     * Both pieces survive being written back out. A loot table is read far more often than it is
     * written, but {@code /armorpieces} prints one and the toolkit's bridge pushes one, and a codec
     * that drops a field on the way out is the trap this repository has already paid for twice.
     */
    @Test
    void bothSurviveBeingWrittenBackOut() {
        final String source = """
            { "type": "minecraft:chest",
              "pools": [ { "rolls": 1, "entries": [
                { "type": "armorpieces:template", "parts": "#armorpieces:knightly",
                  "fittings": ["armorpieces:gemstone"], "weight": 4 },
                { "type": "minecraft:item", "name": "minecraft:golden_helmet",
                  "functions": [ { "function": "armorpieces:set_decoration",
                    "socket": "brow", "part": "armorpieces:circlet", "material": "minecraft:gold",
                    "fittings": { "armorpieces:gemstone": "minecraft:emerald" } } ] } ] } ] }
            """;
        final JsonElement once = encode(table(source));
        final JsonElement twice = encode(table(once.toString()));
        assertEquals(once, twice, "a table written from what it wrote is not the same table");
        assertTrue(once.toString().contains("\"weight\":4"),
            "the entry's own weight did not survive: " + once);
        assertTrue(once.toString().contains("minecraft:emerald"),
            "the fitting the function sets did not survive: " + once);
    }

    // ------------------------------------------------------------------------------ the machinery

    /** Reads a loot table the way a datapack's file is read, and fails loudly if it will not. */
    private static LootTable table(final String json) {
        return LootTable.DIRECT_CODEC.parse(ops, JsonParser.parseString(json))
            .getOrThrow(message -> new AssertionError("the table would not load: " + message));
    }

    private static JsonElement encode(final LootTable table) {
        return LootTable.DIRECT_CODEC.encodeStart(ops, table)
            .getOrThrow(message -> new AssertionError("the table cannot be written back: " + message));
    }

    /**
     * Everything the game would say about this table as the pack loads: the same
     * {@link ValidationContext} a server builds, holding the registries the load produced, so a tag
     * is resolved exactly as it would be in the world.
     */
    private static List<String> problems(final LootTable table) {
        final ProblemReporter.Collector collector = new ProblemReporter.Collector();
        table.validate(new ValidationContext(collector, LootContextParamSets.CHEST, loaded.full()));
        final List<String> said = new ArrayList<>();
        collector.forEach((path, problem) -> said.add(problem.description()));
        return said;
    }

    private static void assertSaid(final LootTable table, final String expected) {
        final List<String> said = problems(table);
        assertTrue(said.stream().anyMatch(problem -> problem.contains(expected)),
            "the load said nothing about \"" + expected + "\"; it said: " + said);
    }
}
