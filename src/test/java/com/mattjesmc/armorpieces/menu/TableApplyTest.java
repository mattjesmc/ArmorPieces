package com.mattjesmc.armorpieces.menu;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.mattjesmc.armorpieces.GameBootstrap;
import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mattjesmc.armorpieces.decoration.fitting.builtin.MaterialFitting;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.registry.ModItems;
import java.util.Optional;
import net.minecraft.core.component.DataComponents;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemStackTemplate;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.SmithingRecipeInput;
import net.minecraft.world.item.crafting.SmithingTransformRecipe;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * Apply: the smithing table's own craft, run on the piece standing in the table.
 *
 * <p>Deliberately NOT a new rule. The template slot, the material slot and the selected piece go to
 * the recipe manager as a {@link SmithingRecipeInput}, exactly as the smithing table hands its three
 * slots, and whatever matched is what runs - this mod's four recipes, and equally a vanilla trim or
 * a netherite upgrade. A second implementation of "what may be applied" would drift from the first,
 * so the fixture holds a real recipe manager with the whole stacked datapack in it and this class
 * asks vanilla's recipes here too.
 *
 * <p>Two things ARE the table's own, and both are asserted below. The result is written back into
 * the display slot rather than into a result slot, so a piece takes a part, then a stone, then
 * another part without being picked up in between. And a fitting goes where the table says: the
 * smithing table has nowhere to say more than "this item", so a gem lands in every part on the piece
 * that has a place for one, while here a picked socket - or a picked place - narrows the same rule
 * to that one. The template's own choice still beats both, because a template naming a fitting is
 * the more specific statement.
 *
 * <p>What the client does with all this stays in tier 3: it has no recipes, so it reads the hidden
 * preview slot the server publishes instead of looking anything up, and there is no honest way to
 * stand a client level in a test JVM.
 */
class TableApplyTest {
    @BeforeAll
    static void world() {
        GameBootstrap.content();
    }

    // ---- the craft ------------------------------------------------------------------------------

    @Test
    void applyPutsThePartInItsSocketAndSpendsBoth() {
        final Table table = crest();

        assertTrue(table.menu().canApply(), "the table found no recipe for a crest template and an ingot");
        assertTrue(table.apply(), "Apply did nothing");

        final DecorationEntry crest = table.menu().selectedDecorations().get(DecorationAnchor.CREST);
        assertNotNull(crest, "nothing landed in the crest socket");
        assertEquals(Table.material("minecraft:iron"), crest.material(), "the part is in another material");
        assertTrue(table.inTemplateSlot().isEmpty(), "the template was not spent");
        assertTrue(table.inMaterialSlot().isEmpty(), "the material was not spent");
    }

    /** The hidden slot holds what Apply would make, and Apply is lit exactly while it holds it. */
    @Test
    void theHiddenSlotIsWhatApplyWouldMake() {
        final Table table = crest();
        final ItemStack promised = table.menu().previewStack().copy();
        assertFalse(promised.isEmpty(), "nothing was promised");

        table.apply();

        assertTrue(ItemStack.matches(promised, table.display(0)),
            "what Apply made is not what it promised");
    }

    @Test
    void withNothingToDoApplyIsDark() {
        final Table table = Table.opened().laying(Table.armor(EquipmentSlot.HEAD));
        assertFalse(table.menu().canApply(), "an empty template slot lit Apply");
        assertFalse(table.apply(), "Apply worked with nothing in the slots");

        table.template(ModItems.templateFor(DecorationAnchor.CREST, Table.part(DecorationAnchor.CREST)));
        assertFalse(table.menu().canApply(), "a template with no material lit Apply");

        table.material(Table.stack(Items.STICK));
        assertFalse(table.menu().canApply(), "a stick lit Apply");
    }

    /** A crest is refused on boots by the recipe's own base ingredient, and so refused here. */
    @Test
    void aTemplateForAnotherSlotFindsNoRecipe() {
        final Table table = Table.opened()
            .laying(Table.armor(EquipmentSlot.FEET))
            .template(ModItems.templateFor(DecorationAnchor.CREST, Table.part(DecorationAnchor.CREST)))
            .material(Table.providing(Items.IRON_INGOT, "minecraft:iron"));

        assertFalse(table.menu().canApply(), "a crest was offered to a pair of boots");
    }

    /**
     * The piece is worked on where it stands: a second part goes on without it ever being picked up,
     * which is the whole reason the result is written back into the display slot.
     */
    @Test
    void aPieceIsWorkedOnWhereItStands() {
        final Table table = crest();
        assertTrue(table.apply(), "the crest did not go on");

        table.template(ModItems.templateFor(DecorationAnchor.BROW, Table.part(DecorationAnchor.BROW)))
            .material(Table.providing(Items.IRON_INGOT, "minecraft:iron"));
        assertTrue(table.apply(), "the brow did not go on the same helmet");

        final ArmorDecorations worn = table.menu().selectedDecorations();
        assertNotNull(worn.get(DecorationAnchor.CREST), "the crest was lost putting the brow on");
        assertNotNull(worn.get(DecorationAnchor.BROW), "the brow did not go on");
    }

    // ---- somebody else's recipes ------------------------------------------------------------------

    /** A vanilla trim is a craft at this table too - the same lookup, so the same answer. */
    @Test
    void aVanillaTrimIsACraftHereToo() {
        final Table table = Table.opened()
            .laying(Table.armor(EquipmentSlot.HEAD))
            .template(Table.stack(Items.COAST_ARMOR_TRIM_SMITHING_TEMPLATE))
            .material(Table.providing(Items.IRON_INGOT, "minecraft:iron"));

        assertTrue(table.menu().canApply(), "the table refuses a vanilla trim");
        assertTrue(table.apply(), "the trim was not applied");
        assertTrue(table.display(0).has(DataComponents.TRIM), "the helmet came away untrimmed");
    }

    /** And so is a netherite upgrade, which is the other shape of vanilla smithing. */
    @Test
    void aNetheriteUpgradeIsACraftHereToo() {
        final Table table = Table.opened()
            .laying(Table.stack(Items.DIAMOND_HELMET))
            .template(Table.stack(Items.NETHERITE_UPGRADE_SMITHING_TEMPLATE))
            .material(Table.stack(Items.NETHERITE_INGOT));

        assertTrue(table.menu().canApply(), "the table refuses a netherite upgrade");
        assertTrue(table.apply(), "the upgrade was not applied");
        assertTrue(table.display(0).is(Items.NETHERITE_HELMET), "the helmet was not upgraded");
    }

    /**
     * A result that could not go back in the slot it came from is no result at all. Nothing shipped
     * can make one - every smithing recipe there is turns armor into the same armor - so the recipe
     * that shows it is written here, and asserted to be one that really does match.
     */
    @Test
    void aResultThatIsNotArmorHasNowhereToGo() {
        final SmithingTransformRecipe melts = meltsAHelmet();
        assertTrue(melts.matches(
                new SmithingRecipeInput(Table.stack(Items.STICK), Table.armor(EquipmentSlot.HEAD),
                    Table.stack(Items.DIAMOND)), null),
            "the recipe this test is about does not match its own inputs");

        final Table table = Table
            .offering(new RecipeHolder<>(ResourceKey.create(Registries.RECIPE,
                Identifier.fromNamespaceAndPath("armorpieces", "test_melts_a_helmet")), melts))
            .laying(Table.armor(EquipmentSlot.HEAD))
            .template(Table.stack(Items.STICK))
            .material(Table.stack(Items.DIAMOND));

        assertFalse(table.menu().canApply(), "the table offered to turn a helmet into a diamond");
        assertFalse(table.apply(), "it did it anyway");
        assertTrue(table.display(0).is(Items.IRON_HELMET), "the helmet is gone");
    }

    // ---- where a fitting goes ----------------------------------------------------------------------

    /**
     * With the piece being worked on as a whole, the recipe's own routing stands: one gem, and every
     * part on the piece that has a place for one gets it in a single step.
     */
    @Test
    void aGemReachesEveryPartWhileThePieceIsWorkedOnAsAWhole() {
        final Table table = gemmed();

        assertTrue(table.apply(), "the gem did not go on");

        assertEquals(emerald(), fitting(table, DecorationAnchor.COLLAR, "gemstone"),
            "the collar's stone is empty");
        assertEquals(emerald(), fitting(table, DecorationAnchor.VAMBRACES, "gemstone"),
            "the vambraces' stone is empty");
    }

    /** Picking a socket narrows the same step to that socket - what the smithing table cannot say. */
    @Test
    void pickingASocketSendsTheGemToThatSocketAlone() {
        final Table table = gemmed();
        assertTrue(table.row(2), "the collar could not be picked");

        assertTrue(table.apply(), "the gem did not go on");

        assertEquals(emerald(), fitting(table, DecorationAnchor.COLLAR, "gemstone"),
            "the collar's stone is empty");
        assertNull(fitting(table, DecorationAnchor.VAMBRACES, "gemstone"),
            "the gem reached the vambraces as well");
    }

    /** And picking one place of a row narrows it to that fitting. */
    @Test
    void pickingAPlaceSendsTheItemToThatFittingAlone() {
        final Table table = collared();
        assertTrue(table.place(2, 0), "the collar's guard could not be picked");

        assertTrue(table.apply(), "the ingot did not go on");

        assertEquals(new MaterialFitting.Value(Table.material("minecraft:iron")),
            fitting(table, DecorationAnchor.COLLAR, "guard"), "the guard is empty");
    }

    /**
     * A place the item cannot fill leaves Apply dark, even though the recipe matched: the recipe is
     * about the item, and the narrowing is about where it may go.
     */
    @Test
    void aPlaceTheItemCannotFillLeavesApplyDark() {
        final Table table = collared();
        assertTrue(table.menu().canApply(), "an ingot found no recipe at all");

        assertTrue(table.place(2, 1), "the collar's inlay could not be picked");

        assertFalse(table.menu().canApply(), "an ingot was offered to a dye's inlay");
        assertFalse(table.apply(), "the ingot went into the inlay");
    }

    /** The template's own choice beats the picked place: it is the more specific statement. */
    @Test
    void aTemplateThatNamesAFittingBeatsThePickedPlace() {
        final Table table = collared()
            .template(ModItems.fittingTemplateFor(Table.fitting("guard")));
        assertTrue(table.place(2, 1), "the collar's inlay could not be picked");

        assertTrue(table.menu().canApply(), "a template naming the guard was refused");
        assertTrue(table.apply(), "the ingot did not go on");

        assertEquals(new MaterialFitting.Value(Table.material("minecraft:iron")),
            fitting(table, DecorationAnchor.COLLAR, "guard"),
            "the template's own fitting is not where the ingot went");
    }

    // ---- the tables --------------------------------------------------------------------------------

    /** A helmet, a crest template and an ingot: the plainest craft this mod has. */
    private static Table crest() {
        return Table.opened()
            .laying(Table.armor(EquipmentSlot.HEAD))
            .template(ModItems.templateFor(DecorationAnchor.CREST, Table.part(DecorationAnchor.CREST)))
            .material(Table.providing(Items.IRON_INGOT, "minecraft:iron"));
    }

    /** A chestplate wearing two parts that each have a stone, with a bare template and an emerald. */
    private static Table gemmed() {
        return Table.opened()
            .laying(Table.wearing(
                Table.wearing(DecorationAnchor.COLLAR, Table.part(DecorationAnchor.COLLAR, "gemstone")),
                DecorationAnchor.VAMBRACES, Table.part(DecorationAnchor.VAMBRACES, "gemstone")))
            .template(Table.stack(ModItems.fittingTemplate()))
            .material(Table.providing(Items.EMERALD, "minecraft:emerald"));
    }

    /** A chestplate wearing a part whose guard comes before its inlay, with a bare template and an ingot. */
    private static Table collared() {
        return Table.opened()
            .laying(Table.wearing(DecorationAnchor.COLLAR, Table.part(DecorationAnchor.COLLAR, "guard", "inlay")))
            .template(Table.stack(ModItems.fittingTemplate()))
            .material(Table.providing(Items.IRON_INGOT, "minecraft:iron"));
    }

    /** A recipe nobody ships: a helmet, a stick and a diamond make a diamond. */
    private static SmithingTransformRecipe meltsAHelmet() {
        return new SmithingTransformRecipe(
            new Recipe.CommonInfo(true),
            Optional.of(Ingredient.of(Items.STICK)),
            Ingredient.of(Items.IRON_HELMET),
            Optional.of(Ingredient.of(Items.DIAMOND)),
            new ItemStackTemplate(Items.DIAMOND));
    }

    // ---- reading the piece ---------------------------------------------------------------------------

    private static Object fitting(final Table table, final DecorationAnchor anchor, final String fitting) {
        final DecorationEntry entry = table.display(Table.displayIndexOf(table.selected()))
            .getOrDefault(ModDataComponents.DECORATIONS, ArmorDecorations.EMPTY).get(anchor);
        assertNotNull(entry, () -> "nothing is in the " + anchor.getSerializedName() + " socket");
        return entry.fitting(Table.fitting(fitting));
    }

    private static MaterialFitting.Value emerald() {
        return new MaterialFitting.Value(Table.material("minecraft:emerald"));
    }
}
