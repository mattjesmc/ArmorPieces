package com.mattjesmc.armorpieces.recipe;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.mojang.serialization.JsonOps;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.PlacementInfo;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeType;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * The recipe a datapack overrides a file WITH, to turn that file off.
 *
 * <p>Three claims, and each is about something not happening. It matches nothing, so no station ever
 * produces from it; it has no display, so the recipe book and any viewer that reads displays never
 * show it; and it is its own {@link RecipeType}, so no station's lookup even asks. A regression in
 * any of them is silent by construction - a disabled recipe that quietly came back on would look
 * exactly like a working mod.
 */
class DisabledRecipeTest {
    /**
     * The game, before anything else. A bare {@code Items.IRON_HELMET} in an argument is evaluated
     * BEFORE the call it is passed to, so a fixture method cannot bootstrap on its way past: the
     * first touch of {@link net.minecraft.core.registries.BuiltInRegistries} in a JVM that has not
     * been bootstrapped fails its class initialiser, and every later test in that JVM then fails
     * with a {@link NoClassDefFoundError} about a class that is not the problem.
     */
    @BeforeAll
    static void world() {
        Bench.data();
    }

    /** Registered by {@code ModRecipeSerializers}, which the fixture's load runs. */
    private static Identifier id() {
        Bench.data();
        return Identifier.fromNamespaceAndPath(com.mattjesmc.armorpieces.ArmorPieces.MOD_ID, "disabled");
    }

    @Test
    void itMatchesNothingAndProducesNothing() {
        final var input = Bench.input(
            Bench.stack(Items.DIAMOND), Bench.stack(Items.IRON_HELMET), Bench.stack(Items.IRON_INGOT));

        assertFalse(DisabledRecipe.INSTANCE.matches(input, Bench.NO_LEVEL), "it matched something");
        assertSame(ItemStack.EMPTY, DisabledRecipe.INSTANCE.assemble(input), "it produced something");
    }

    @Test
    void itIsInvisibleToTheRecipeBook() {
        assertTrue(DisabledRecipe.INSTANCE.display().isEmpty(), "it has a display to be filed under");
        assertSame(PlacementInfo.NOT_PLACEABLE, DisabledRecipe.INSTANCE.placementInfo(), "it can be placed");
        assertTrue(DisabledRecipe.INSTANCE.isSpecial(), "it is not special, so the book would list it");
        assertFalse(DisabledRecipe.INSTANCE.showNotification(), "unlocking it would toast the player");
    }

    /** Its own type, so it is in no station's lookup to be asked and refused on every craft. */
    @Test
    void noStationEverAsksIt() {
        assertSame(DisabledRecipe.TYPE, DisabledRecipe.INSTANCE.getType(), "it rides another type");
        assertNotSame(RecipeType.SMITHING, DisabledRecipe.INSTANCE.getType(),
            "it is in the smithing table's lookup, to be asked and refused on every craft");
        assertTrue(BuiltInRegistries.RECIPE_TYPE.containsKey(id()), "the type is not registered");
        assertTrue(BuiltInRegistries.RECIPE_SERIALIZER.containsKey(id()), "the serializer is not registered");
    }

    /**
     * The codec ignores every field but {@code type}, which is the contract the Blockbench plugin
     * disables a recipe by: it swaps the type and KEEPS the pattern, key and result, so the author's
     * choices survive the round trip and switching it back on is the reverse swap.
     */
    @Test
    void itSwallowsTheFieldsOfTheRecipeItReplaces() {
        final JsonElement json = JsonParser.parseString("""
            {
              "type": "armorpieces:disabled",
              "pattern": ["XX", "XX"],
              "key": {"X": "minecraft:diamond"},
              "result": {"id": "minecraft:diamond_block"}
            }
            """);

        final Recipe<?> parsed = Recipe.CODEC
            .parse(Bench.data().full().createSerializationContext(JsonOps.INSTANCE), json)
            .getOrThrow(message -> new AssertionError("a disabled recipe with a body was refused: " + message));

        assertSame(DisabledRecipe.INSTANCE, parsed, "it decoded to something else");
    }
}
