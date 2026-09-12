package com.mattjesmc.armorpieces.pack;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.mattjesmc.armorpieces.GameBootstrap;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import java.util.LinkedHashMap;
import java.util.Map;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * The rule {@code RegistryLoadTaskMixin} applies, without a game to apply it in.
 *
 * <p>The mixin is two lines - "is this registry mine, then {@link PackSkips#rescue}" - precisely so
 * that the part with a decision in it can be read and tested here. What it decides is which of a
 * load's failures stop the world: ours are taken out of the map the loader throws over, everybody
 * else's are left exactly where they were.
 *
 * <p>That it is wired to the loader at all is the gate's tier-2 {@code broken-pack} boot check. A
 * mixin is not applied in a plain test JVM, and a test that pretended otherwise would be testing its
 * own fake.
 */
class PackSkipsTest {
    @BeforeEach
    void clean() {
        GameBootstrap.once();
        PackProblems.clear();
    }

    private static ResourceKey<?> element(
        final ResourceKey<? extends net.minecraft.core.Registry<?>> registry,
        final String id
    ) {
        return ResourceKey.create(cast(registry), Identifier.parse(id));
    }

    @SuppressWarnings("unchecked")
    private static <T> ResourceKey<? extends net.minecraft.core.Registry<T>> cast(
        final ResourceKey<? extends net.minecraft.core.Registry<?>> registry
    ) {
        return (ResourceKey<? extends net.minecraft.core.Registry<T>>) registry;
    }

    @Test
    void oursAreTakenOutAndEverybodyElseIsLeftAlone() {
        final Map<ResourceKey<?>, Exception> errors = new LinkedHashMap<>();
        final ResourceKey<?> ours = element(ArmorPiecesRegistries.ARMOR_DECORATION, "coral:kelp_mantle");
        final ResourceKey<?> alsoOurs = element(ArmorPiecesRegistries.ARMOR_SKIN, "coral:nacre");
        final ResourceKey<?> theirs = element(Registries.BIOME, "othermod:tundra");
        errors.put(ours, new IllegalStateException("Failed to parse coral:kelp_mantle from pack coral"));
        errors.put(alsoOurs, new IllegalStateException("Failed to parse coral:nacre from pack coral"));
        errors.put(theirs, new IllegalStateException("some other mod's problem"));

        assertEquals(1, PackSkips.rescue(ArmorPiecesRegistries.ARMOR_DECORATION, errors),
            "exactly the one element of that registry should have been rescued");
        assertFalse(errors.containsKey(ours), "an error left in the map is still a world that will not open");
        assertTrue(errors.containsKey(alsoOurs), "a different registry of ours is a different call");
        assertTrue(errors.containsKey(theirs),
            "another mod's registry is not ours to declare survivable - it has to stay fatal");
        assertTrue(PackProblems.all().stream().anyMatch(entry ->
                entry.getKey().subject().contains("coral:kelp_mantle")
                    && entry.getKey().bucket() == PackProblem.Bucket.SKIPPED),
            () -> "the skipped element was not reported: " + PackProblems.all());
    }

    @Test
    void nothingToRescueIsNoWork() {
        assertEquals(0, PackSkips.rescue(ArmorPiecesRegistries.ARMOR_DECORATION, new LinkedHashMap<>()));
        assertFalse(PackProblems.any(), "an empty load filed a problem out of nowhere");
    }

    /**
     * The reason has to carry both ends of the chain: vanilla's outer message names the file and its
     * pack, and the cause under it is the thing the author has to change.
     */
    @Test
    void theReasonNamesTheFileAndTheCause() {
        final String why = PackSkips.why(new IllegalStateException(
            "Failed to parse coral:kelp_mantle from pack coral",
            new IllegalArgumentException("Unknown element name:nose")));
        assertTrue(why.contains("from pack coral"), why);
        assertTrue(why.contains("nose"), why);
    }

    /** A cause that repeats what was said above it says it once. */
    @Test
    void theReasonDoesNotSayOneThingTwice() {
        final String why = PackSkips.why(
            new IllegalStateException("broken", new IllegalArgumentException("broken")));
        assertEquals(1, why.split("broken", -1).length - 1, why);
    }
}
