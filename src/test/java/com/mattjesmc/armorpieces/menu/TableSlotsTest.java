package com.mattjesmc.armorpieces.menu;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.mattjesmc.armorpieces.GameBootstrap;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.registry.ModItems;
import java.util.List;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * The slots of the advanced smithing table: what each one takes, and where a shift-click sends it.
 *
 * <p>The mod's own crafting station, and until now the only thing that had ever driven it was a
 * person clicking - tier 3 opens the screen and clicks slots, tier 2 never opens an inventory at
 * all. Every rule below is decided over the stacks in the table's own slots and needs no world, so
 * it is asked here, in a second, rather than in a client run.
 *
 * <p>Two of them are worth stating before they are asserted. A display slot is typed by the item's
 * {@code equippable} component rather than by a list of armor, which is what admits another mod's
 * helmet on the same terms as vanilla's; and the two input slots test items with the SAME
 * {@link net.minecraft.world.item.crafting.RecipePropertySet} the vanilla smithing table uses, which
 * is what keeps the two tables lighting up for the same things - a datapack's smithing recipe
 * included. Both are claims about vanilla's own items, so both are asserted against vanilla's.
 */
class TableSlotsTest {
    @BeforeAll
    static void world() {
        GameBootstrap.content();
    }

    // ---- the four display slots ----------------------------------------------------------------

    /** Head to toe, and a piece only ever goes in the slot it would be worn in. */
    @Test
    void aDisplaySlotTakesOnlyArmorThatEquipsInIt() {
        final Table table = Table.opened();
        for (int index = 0; index < AdvancedSmithingMenu.DISPLAY_SLOTS.size(); index++) {
            final EquipmentSlot worn = AdvancedSmithingMenu.DISPLAY_SLOTS.get(index);
            final int belongs = index;
            for (int other = 0; other < AdvancedSmithingMenu.DISPLAY_SLOTS.size(); other++) {
                final int at = other;
                assertEquals(belongs == at,
                    display(table, other).mayPlace(Table.armor(worn)),
                    () -> worn + " armor is " + (belongs == at ? "refused by" : "taken by")
                        + " the " + AdvancedSmithingMenu.DISPLAY_SLOTS.get(at) + " slot");
            }
        }
    }

    /** Anything with no {@code equippable} at all belongs in none of them. */
    @Test
    void whatIsNotWornGoesInNoDisplaySlot() {
        final Table table = Table.opened();
        for (final Item item : List.of(Items.DIAMOND, Items.IRON_SWORD, Items.STICK)) {
            for (int index = 0; index < AdvancedSmithingMenu.DISPLAY_SLOTS.size(); index++) {
                final int at = index;
                assertFalse(display(table, index).mayPlace(Table.stack(item)),
                    () -> item + " was taken by display slot " + at);
            }
        }
    }

    /** One piece to a slot: the table shows a set, not a stack of helmets. */
    @Test
    void aDisplaySlotHoldsOneThing() {
        final Table table = Table.opened();
        for (int index = 0; index < AdvancedSmithingMenu.DISPLAY_SLOTS.size(); index++) {
            assertEquals(1, display(table, index).getMaxStackSize(),
                "a display slot would hold more than one piece");
        }
    }

    // ---- the two input slots -------------------------------------------------------------------

    /**
     * The template slot takes what the smithing table's does - this mod's four templates AND
     * vanilla's, because both slots ask the same recipe property set.
     */
    @Test
    void theTemplateSlotTakesEveryTemplateASmithingRecipeNames() {
        final Table table = Table.opened();
        final List<ItemStack> templates = List.of(
            Table.stack(ModItems.template(DecorationAnchor.CREST)),
            Table.stack(ModItems.fittingTemplate()),
            Table.stack(ModItems.skinTemplate()),
            Table.stack(ModItems.clothTemplate()),
            Table.stack(Items.NETHERITE_UPGRADE_SMITHING_TEMPLATE),
            Table.stack(Items.COAST_ARMOR_TRIM_SMITHING_TEMPLATE));
        for (final ItemStack template : templates) {
            assertTrue(slot(table, AdvancedSmithingMenu.TEMPLATE_SLOT).mayPlace(template),
                () -> "the table refuses " + template.getItem() + " as a template");
        }
        assertFalse(slot(table, AdvancedSmithingMenu.TEMPLATE_SLOT).mayPlace(Table.stack(Items.DIAMOND)),
            "the table takes a diamond as a template");
    }

    /** And the material slot takes what a smithing recipe would accept as its addition. */
    @Test
    void theMaterialSlotTakesWhatARecipeWouldAddWithIt() {
        final Table table = Table.opened();
        for (final Item item : List.of(Items.IRON_INGOT, Items.NETHERITE_INGOT, Items.EMERALD)) {
            assertTrue(slot(table, AdvancedSmithingMenu.MATERIAL_SLOT).mayPlace(Table.stack(item)),
                () -> "the table refuses " + item + " as a material");
        }
        assertFalse(slot(table, AdvancedSmithingMenu.MATERIAL_SLOT).mayPlace(Table.stack(Items.STICK)),
            "the table takes a stick as a material");
    }

    // ---- the slot that is not a slot -------------------------------------------------------------

    /**
     * What Apply would make travels to the client in a slot, and that slot is never drawn, never
     * filled and never taken from. It exists so the stand can wear the result before it is made.
     */
    @Test
    void thePreviewIsNeverDrawnFilledOrTaken() {
        final Table table = Table.opened().laying(Table.armor(EquipmentSlot.HEAD));
        final Slot preview = slot(table, AdvancedSmithingMenu.PREVIEW_SLOT);

        assertFalse(preview.isActive(), "the preview slot is drawn");
        assertFalse(preview.mayPlace(Table.armor(EquipmentSlot.HEAD)), "the preview slot takes items");
        assertFalse(preview.mayPickup(table.player()), "the preview can be picked up");
    }

    // ---- shift-clicking ---------------------------------------------------------------------------

    /** Armor goes to its own display slot, wherever in the bag it was. */
    @Test
    void armorShiftedInGoesToTheSlotItIsWornIn() {
        for (final EquipmentSlot worn : AdvancedSmithingMenu.DISPLAY_SLOTS) {
            final Table table = Table.opened();
            final ItemStack piece = Table.armor(worn);
            table.inventory().setItem(9, piece);

            table.menu().quickMoveStack(table.player(), firstInventorySlot());

            final int index = AdvancedSmithingMenu.DISPLAY_SLOTS.indexOf(worn);
            assertFalse(table.display(index).isEmpty(),
                () -> worn + " armor did not reach its display slot");
            assertTrue(table.inventory().getItem(9).isEmpty(), "it is still in the bag as well");
        }
    }

    @Test
    void aTemplateShiftedInGoesToTheTemplateSlotAndAMaterialToTheMaterialSlot() {
        final Table table = Table.opened();
        table.inventory().setItem(9, Table.stack(ModItems.template(DecorationAnchor.CREST)));
        table.menu().quickMoveStack(table.player(), firstInventorySlot());
        assertSame(ModItems.template(DecorationAnchor.CREST), table.inTemplateSlot().getItem(),
            "the template did not reach the template slot");

        table.inventory().setItem(9, Table.stack(Items.IRON_INGOT));
        table.menu().quickMoveStack(table.player(), firstInventorySlot());
        assertSame(Items.IRON_INGOT, table.inMaterialSlot().getItem(),
            "the ingot did not reach the material slot");
    }

    /**
     * A second helmet has nowhere to go - the one display slot that takes it is full - so it does
     * what a stack with no home does in every menu: it crosses to the other half of the bag.
     */
    @Test
    void aPieceWithNoSlotLeftMovesWithinTheBag() {
        final Table table = Table.opened().laying(Table.armor(EquipmentSlot.HEAD));
        table.inventory().setItem(9, Table.armor(EquipmentSlot.HEAD));

        table.menu().quickMoveStack(table.player(), firstInventorySlot());

        assertEquals(1, table.display(0).getCount(), "the table now holds two helmets");
        assertTrue(table.inventory().contains(stack -> stack.is(Items.IRON_HELMET)),
            "the second helmet left the bag for nowhere");
        assertFalse(table.inventory().getItem(0).isEmpty(),
            "it did not cross to the hotbar, which is where a stack with no home goes");
    }

    @Test
    void shiftingAPieceOutOfTheTablePutsItInTheBag() {
        final Table table = Table.opened().laying(Table.armor(EquipmentSlot.CHEST));

        table.menu().quickMoveStack(table.player(), AdvancedSmithingMenu.DISPLAY_SLOT_START + 1);

        assertTrue(table.display(1).isEmpty(), "the chestplate is still on the table");
        assertTrue(table.inventory().contains(stack -> stack.is(Items.IRON_CHESTPLATE)),
            "the chestplate did not reach the bag");
    }

    /** The result of a craft that has not happened is not a thing to take. */
    @Test
    void whatApplyWouldMakeCannotBeShiftedOut() {
        final Table table = Table.opened()
            .laying(Table.armor(EquipmentSlot.HEAD))
            .template(ModItems.templateFor(DecorationAnchor.CREST, Table.part(DecorationAnchor.CREST)))
            .material(Table.providing(Items.IRON_INGOT, "minecraft:iron"));
        assertFalse(table.menu().previewStack().isEmpty(), "nothing was previewed to try to take");

        assertTrue(table.menu().quickMoveStack(table.player(), AdvancedSmithingMenu.PREVIEW_SLOT).isEmpty(),
            "the preview was handed out");
        assertFalse(table.menu().previewStack().isEmpty(), "the preview was taken off the table");
    }

    // ---- closing ------------------------------------------------------------------------------

    /**
     * Nothing is kept. The table has no block entity, so everything in it leaves the moment the
     * screen closes - the two containers a player filled through vanilla's own {@code clearContainer},
     * and the preview by being emptied first, since it was never theirs and is in neither container.
     *
     * <p>Where a stack GOES is vanilla's rule and not this menu's: {@code clearContainer} hands
     * things back only to a {@code ServerPlayer}, which this fixture's customer is not. What is
     * asserted here is the half the menu decides - that all three are emptied - and a menu that
     * forgot the preview would keep it, since no container clear reaches it.
     */
    @Test
    void closingLeavesNothingOnTheTable() {
        final Table table = Table.opened()
            .laying(Table.armor(EquipmentSlot.HEAD))
            .template(ModItems.templateFor(DecorationAnchor.CREST, Table.part(DecorationAnchor.CREST)))
            .material(Table.providing(Items.IRON_INGOT, "minecraft:iron"));
        assertFalse(table.menu().previewStack().isEmpty(), "the table previewed nothing to lose");

        table.menu().removed(table.player());

        assertTrue(table.display(0).isEmpty(), "the helmet stayed on the table");
        assertTrue(table.inTemplateSlot().isEmpty(), "the template stayed on the table");
        assertTrue(table.inMaterialSlot().isEmpty(), "the material stayed on the table");
        assertTrue(table.menu().previewStack().isEmpty(), "the preview stayed on the table");
    }

    // ---- reading the table ---------------------------------------------------------------------

    private static Slot display(final Table table, final int index) {
        return slot(table, AdvancedSmithingMenu.DISPLAY_SLOT_START + index);
    }

    private static Slot slot(final Table table, final int index) {
        return table.menu().getSlot(index);
    }

    /** The first menu slot that belongs to the player's own bag - inventory slot 9. */
    private static int firstInventorySlot() {
        return AdvancedSmithingMenu.PREVIEW_SLOT + 1;
    }
}
