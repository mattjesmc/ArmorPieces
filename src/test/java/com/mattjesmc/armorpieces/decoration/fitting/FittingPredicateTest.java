package com.mattjesmc.armorpieces.decoration.fitting;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.mattjesmc.armorpieces.GameBootstrap;
import com.mattjesmc.armorpieces.data.ShippedData;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.JsonOps;
import net.minecraft.resources.RegistryOps;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * Whether an effect gated on a fitting actually FIRES: {@link FittingPredicate#test}, over sockets
 * written exactly as {@code /give} writes them.
 *
 * <p>{@code armorpieces:if_fitting} is how a part says "this does something only while there is an
 * emerald in it" - the circlet's hero of the village, and the shape every pack is meant to copy. The
 * codec and the gate around it were already covered ({@code DecorationEffectsTest}: it round-trips,
 * and it reaches only what it wraps); the question nobody had asked in a JVM is the one a player
 * feels, which is whether the gate says yes to the gem that is in the socket and no to the one that
 * is not. Until now that was verified by equipping armor in a running game - the gate's tier 2
 * {@code effects} scenario - which is minutes for an answer that is a pure function of two values.
 *
 * <p>The narrowings are the whole surface, and each has a way of being quietly wrong:
 *
 * <ul>
 *   <li><b>presence alone</b> - the shortest form, "while there is any gem", which must still be
 *       false for a socket holding nothing;</li>
 *   <li><b>a material, or a tag of them</b> - the tag being the form that lets a pack say "any
 *       gemstone" without listing them;</li>
 *   <li><b>a dye colour</b>, for the other kind of fitting this mod ships;</li>
 *   <li>and <b>a narrowing meeting the wrong SHAPE of value</b>: a fitting value is opaque by
 *       design, so a material test on a dyed inlay is not an error, it is simply false - and a
 *       predicate that answered yes there would fire an effect on every colour.</li>
 * </ul>
 *
 * <p>The last one is also the load-time rule: material and dye at once can never be true, so it is
 * refused as a broken file rather than left to never fire.
 */
class FittingPredicateTest {
    /** A circlet with an emerald in its gemstone socket - the mod's own documented example. */
    private static final String EMERALD = """
        { "material": "minecraft:gold", "decoration": "armorpieces:circlet",
          "fittings": { "armorpieces:gemstone": "minecraft:emerald" } }
        """;
    /** The same socket holding something else in the gemstone tag. */
    private static final String DIAMOND = """
        { "material": "minecraft:gold", "decoration": "armorpieces:circlet",
          "fittings": { "armorpieces:gemstone": "minecraft:diamond" } }
        """;
    /** The gemstone socket empty. */
    private static final String BARE = """
        { "material": "minecraft:gold", "decoration": "armorpieces:circlet" }
        """;
    /** A bandolier with a red inlay and an iron guard: a dye value and a material value at once. */
    private static final String DYED = """
        { "material": "minecraft:iron", "decoration": "armorpieces:bandolier",
          "fittings": { "armorpieces:inlay": "red", "armorpieces:guard": "minecraft:iron" } }
        """;

    private static ShippedData.Loaded loaded;
    private static RegistryOps<JsonElement> ops;

    @BeforeAll
    static void world() {
        GameBootstrap.content();
        loaded = ShippedData.mod();
        // A predicate narrowing to #armorpieces:gemstones binds that tag as it reads.
        ShippedData.bindTags(loaded);
        ops = loaded.full().createSerializationContext(JsonOps.INSTANCE);
    }

    /** The shortest form: the socket has to be filled, and that is all it asks. */
    @Test
    void presenceAloneIsTheShortestForm() {
        final FittingPredicate anyGem = predicate("""
            { "fitting": "armorpieces:gemstone" }
            """);
        assertTrue(anyGem.test(entry(EMERALD)));
        assertTrue(anyGem.test(entry(DIAMOND)), "any gem means any gem");
        assertFalse(anyGem.test(entry(BARE)), "an empty socket is the one thing presence must refuse");
    }

    /** A fitting the socket does not hold at all is false, not an error. */
    @Test
    void aFittingThatIsNotThereIsSimplyFalse() {
        assertFalse(predicate("""
            { "fitting": "armorpieces:inlay" }
            """).test(entry(EMERALD)), "the circlet has no inlay to look in");
    }

    /** One material narrows to that material and nothing else. */
    @Test
    void aMaterialNarrowsToThatMaterial() {
        final FittingPredicate emerald = predicate("""
            { "fitting": "armorpieces:gemstone", "material": "minecraft:emerald" }
            """);
        assertTrue(emerald.test(entry(EMERALD)), "the circlet's hero of the village, in one call");
        assertFalse(emerald.test(entry(DIAMOND)), "a different gem is a different effect");
        assertFalse(emerald.test(entry(BARE)));
    }

    /**
     * A tag narrows to a set - the form a pack writes when the answer is "any gemstone", and the one
     * that keeps working as gemstones are added.
     */
    @Test
    void aTagNarrowsToASet() {
        final FittingPredicate anyGemstone = predicate("""
            { "fitting": "armorpieces:gemstone", "material": "#armorpieces:gemstones" }
            """);
        assertTrue(anyGemstone.test(entry(EMERALD)));
        assertTrue(anyGemstone.test(entry(DIAMOND)));

        assertFalse(predicate("""
            { "fitting": "armorpieces:gemstone", "material": "#armorpieces:guard_metals" }
            """).test(entry(EMERALD)), "an emerald is not a guard metal");
    }

    /** A dye colour narrows a dye fitting, and only to the colour named. */
    @Test
    void aDyeNarrowsToOneColour() {
        assertTrue(predicate("""
            { "fitting": "armorpieces:inlay", "dye": "red" }
            """).test(entry(DYED)));
        assertFalse(predicate("""
            { "fitting": "armorpieces:inlay", "dye": "blue" }
            """).test(entry(DYED)), "the inlay is red");
    }

    /**
     * A narrowing that meets the wrong SHAPE of value is false rather than a crash or a yes.
     *
     * <p>This is what {@link FittingValue} being opaque costs and buys at once. A pack's own fitting
     * type holds a value this mod cannot read, and the only honest thing to say about it is
     * presence; the two shapes this mod does know are told apart by asking, so a material test on a
     * dyed socket - and a dye test on a metal one - simply does not match.
     */
    @Test
    void aNarrowingThatMeetsTheWrongShapeOfValueIsFalse() {
        assertFalse(predicate("""
            { "fitting": "armorpieces:inlay", "material": "minecraft:iron" }
            """).test(entry(DYED)), "an inlay holds a colour, not a metal");
        assertFalse(predicate("""
            { "fitting": "armorpieces:guard", "dye": "red" }
            """).test(entry(DYED)), "a guard holds a metal, not a colour");
        assertTrue(predicate("""
            { "fitting": "armorpieces:guard", "material": "minecraft:iron" }
            """).test(entry(DYED)), "and the right shape on the same socket still matches");
    }

    /**
     * Both narrowings at once can never be true, so the file is refused at load rather than shipped
     * as an effect that never fires - the failure that is hardest to find by playing.
     */
    @Test
    void materialAndDyeAtOnceIsARefusedFile() {
        final DataResult<FittingPredicate> refused = FittingPredicate.CODEC.parse(ops,
            JsonParser.parseString("""
                { "fitting": "armorpieces:gemstone", "material": "minecraft:emerald", "dye": "red" }
                """));
        assertTrue(refused.isError(), "a predicate that can never be true has to be refused");
        assertTrue(refused.error().orElseThrow().message().contains("either material or dye"),
            () -> "the refusal has to say what is wrong; it said: "
                + refused.error().orElseThrow().message());
    }

    // ------------------------------------------------------------------------------ the machinery

    private static FittingPredicate predicate(final String json) {
        return FittingPredicate.CODEC.parse(ops, JsonParser.parseString(json))
            .getOrThrow(message -> new AssertionError("the predicate would not load: " + message));
    }

    /** One socket, read the way a saved item's is. */
    private static DecorationEntry entry(final String json) {
        return DecorationEntry.CODEC.parse(ops, JsonParser.parseString(json))
            .getOrThrow(message -> new AssertionError("the socket would not load: " + message));
    }
}
