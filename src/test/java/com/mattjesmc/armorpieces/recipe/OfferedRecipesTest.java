package com.mattjesmc.armorpieces.recipe;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.mattjesmc.armorpieces.config.ServerConfigFixture;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.registry.ModItems;
import java.util.List;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.RecipeMap;
import net.minecraft.world.item.crafting.ShapedRecipe;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * The server owner's {@code parts} switch at the two tables: a template recipe for a part that is
 * switched off is not a recipe, and a template for one lays in the smithing slot and crafts
 * nothing. The switch's own rules are {@code PartsSwitchTest}'s; this is where they reach.
 */
class OfferedRecipesTest {
    /** A template recipe the mod ships, and the part it makes a template for. */
    private static final String TEMPLATE = "template_visor";
    private static final String PART = "armorpieces_knightly:visor";

    @BeforeAll
    static void world() {
        Bench.data();
    }

    @AfterEach
    void reset() {
        ServerConfigFixture.reset();
    }

    private static RecipeHolder<ShapedRecipe> shipped() {
        return new RecipeHolder<>(
            ResourceKey.create(Registries.RECIPE, Identifier.fromNamespaceAndPath("armorpieces", TEMPLATE)),
            Bench.recipe(TEMPLATE, ShapedRecipe.class));
    }

    @Test
    void aTemplateRecipeSaysWhatItMakesATemplateFor() {
        final Holder<?> makes = OfferedRecipes.makes(shipped().value());
        assertNotNull(makes, TEMPLATE + " makes no template");
        assertEquals(PART, makes.unwrapKey().orElseThrow().identifier().toString());
        assertNull(OfferedRecipes.makes(Bench.recipe("advanced_smithing_table", ShapedRecipe.class)),
            "a recipe for a block is nothing of ours");
        assertNull(OfferedRecipes.makes(Bench.recipe("apply_crest", SmithingDecorationRecipe.class)),
            "a smithing recipe is not asked");
    }

    @Test
    void aServerThatSwitchedNothingOffKeepsTheMapItWasGiven() {
        final RecipeMap loaded = RecipeMap.create(List.of(shipped()));
        assertSame(loaded, OfferedRecipes.keep(loaded, Bench.data().full()));
    }

    @Test
    void aTemplateRecipeForASwitchedOffPartIsDropped() {
        ServerConfigFixture.configure("""
            { "parts": { "disabled": ["%s"] } }
            """.formatted(PART));
        final RecipeMap kept = OfferedRecipes.keep(RecipeMap.create(List.of(shipped())), Bench.data().full());
        assertTrue(kept.values().isEmpty(), "the recipe survived the switch");

        ServerConfigFixture.configure("""
            { "parts": { "disabled": ["armorpieces_court:circlet"] } }
            """);
        assertEquals(1,
            OfferedRecipes.keep(RecipeMap.create(List.of(shipped())), Bench.data().full()).values().size(),
            "a switch about another part dropped this one");
    }

    @Test
    void aTemplateForASwitchedOffPartCraftsNothingAtTheSmithingTable() {
        final Holder<ArmorDecoration> part = Bench.part(DecorationAnchor.CREST);
        final ItemStack template = ModItems.templateFor(DecorationAnchor.CREST, part);
        final var input = Bench.input(template, Bench.stack(Items.IRON_HELMET),
            Bench.providing(Items.IRON_INGOT, "minecraft:iron"));
        final SmithingDecorationRecipe apply = Bench.recipe("apply_crest", SmithingDecorationRecipe.class);
        assertTrue(apply.matches(input, Bench.level()), "the three right stacks did not match before the switch");

        ServerConfigFixture.configure("""
            { "parts": { "disabled": ["%s"] } }
            """.formatted(part.unwrapKey().orElseThrow().identifier()));
        assertFalse(apply.matches(input, Bench.level()), "a switched-off part was applied");

        ServerConfigFixture.configure("""
            { "parts": { "mod_parts": false } }
            """);
        assertFalse(apply.matches(input, Bench.level()), "the mod's own part was applied with mod_parts off");
    }
}
