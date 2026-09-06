package com.mattjesmc.armorpieces.decoration.effect;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.mattjesmc.armorpieces.GameBootstrap;
import com.mojang.serialization.JsonOps;
import java.util.Set;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * A sub-predicate is the same test whichever way its name is spelled.
 *
 * <p>The fourth 0.4.0 trap, and the only one that showed up as a disconnect. Which tests a wearer
 * condition asks decides where it is legal - an {@code equipment} test may gate an attribute effect
 * because a hand change re-reconciles the armor slots, and anything else may not - so the names are
 * read off the written object. A file writes {@code equipment}; but a part in a WORLD datapack is
 * re-encoded for the registry sync, and vanilla writes sub-predicate keys as FULL ids, so the CLIENT
 * decodes {@code minecraft:equipment} for the same file. Comparing the bare name accepted the file
 * on the server and refused it on the client: "Failed to load registries", client disconnected,
 * server fine, and the mod's own pack never showed it because the client reads those elements
 * locally.
 *
 * <p>So both spellings have to mean one thing, which is what this asserts. Any name compared across
 * that boundary needs the same treatment.
 */
class WearerPredicateTest {
    @BeforeAll
    static void bootstrap() {
        GameBootstrap.once();  // vanilla's EntityPredicate reaches into the built-in registries
    }

    private static WearerPredicate parse(final String json) {
        final JsonElement element = JsonParser.parseString(json);
        return WearerPredicate.CODEC.parse(JsonOps.INSTANCE, element).getOrThrow();
    }

    @Test
    void aBareNameAndAFullIdAreTheSameTest() {
        final WearerPredicate bare = parse("{\"equipment\": {\"mainhand\": {}}}");
        final WearerPredicate full = parse("{\"minecraft:equipment\": {\"mainhand\": {}}}");

        assertEquals(Set.of(WearerPredicate.EQUIPMENT), bare.tests(),
            "a file writing the short name should be read as the full id");
        assertEquals(bare.tests(), full.tests(),
            "the same file, re-encoded for the registry sync, has to read as the same test");
        assertTrue(bare.isEquipmentOnly());
        assertTrue(full.isEquipmentOnly(),
            "this is the one that failed on the client and passed on the server");
    }

    @Test
    void aTestBeyondEquipmentIsNamedTheWayItWasWritten() {
        final WearerPredicate located = parse("{\"location\": {}}");

        assertFalse(located.isEquipmentOnly());
        assertEquals(Set.of("location"), located.beyondEquipment(),
            "the message tells an author about the name they typed, not the namespaced one");
    }

    @Test
    void anEmptyPredicateAsksNothingAndIsLegalAnywhere() {
        final WearerPredicate nothing = parse("{}");

        assertEquals(Set.of(), nothing.tests());
        assertTrue(nothing.isEquipmentOnly(), "no test at all cannot be a test that is not allowed");
    }
}
