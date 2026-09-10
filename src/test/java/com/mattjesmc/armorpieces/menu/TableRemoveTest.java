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
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.component.DataComponents;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * Remove: the one thing this table does that a smithing table cannot.
 *
 * <p>A smithing table has no ingredient that means "nothing", so a filled socket there stays filled
 * until something replaces it. Five things come off here and nowhere else - a whole part out of its
 * socket, one fitting out of the part sitting in it, the piece's trim, its skin, and the garment it
 * is wearing - and which of them is decided entirely by what is picked. Nothing is refunded.
 *
 * <p>The last test is the one that matters. Remove is drawn as a lit button, and
 * {@link AdvancedSmithingMenu#canRemove} is what lights it; a table whose button lights on one place
 * and empties another is the bug that costs, and it is invisible to every test that asks the two
 * questions separately. So the sweep asks them together, on a piece with something in every one of
 * its places and nothing in some of them, and holds the two to each other.
 */
class TableRemoveTest {
    @BeforeAll
    static void world() {
        GameBootstrap.content();
    }

    // ---- a socket ------------------------------------------------------------------------------

    @Test
    void theSelectedSocketIsTheOneEmptied() {
        final Table table = Table.opened().laying(dressed());
        assertTrue(table.row(2), "the collar could not be picked");

        assertTrue(table.menu().canRemove(), "the collar's part was not offered for removal");
        assertTrue(table.remove(), "the collar's part was not removed");

        assertNull(table.menu().selectedDecorations().get(DecorationAnchor.COLLAR),
            "the collar is still filled");
        assertNotNull(table.menu().selectedDecorations().get(DecorationAnchor.VAMBRACES),
            "the vambraces were emptied too");
    }

    /**
     * The last part off a piece takes the component with it, rather than leaving an empty map
     * behind: the piece is the undecorated item again, byte for byte, and stacks with one.
     */
    @Test
    void theLastPartOffTakesTheComponentWithIt() {
        final ItemStack plain = Table.armor(EquipmentSlot.HEAD);
        final Table table = Table.opened()
            .laying(Table.wearing(DecorationAnchor.CREST, Table.part(DecorationAnchor.CREST)));
        table.row(0);

        assertTrue(table.remove(), "the crest was not removed");

        assertFalse(table.display(0).has(ModDataComponents.DECORATIONS),
            "an empty decorations component was left on the piece");
        assertTrue(ItemStack.matches(plain, table.display(0)),
            "what is left is not the plain helmet it started as: " + table.display(0).getComponents());
    }

    // ---- one fitting ---------------------------------------------------------------------------

    @Test
    void onePlaceEmptiesOneFittingAndLeavesThePart() {
        final Table table = Table.opened().laying(dressed());
        assertTrue(table.place(2, 0), "the collar's guard could not be picked");

        assertTrue(table.menu().canRemove(), "a filled guard was not offered for removal");
        assertTrue(table.remove(), "the guard was not emptied");

        final DecorationEntry collar = table.menu().selectedDecorations().get(DecorationAnchor.COLLAR);
        assertNotNull(collar, "emptying a fitting took the whole part off");
        assertNull(collar.fitting(Table.fitting("guard")), "the guard still holds something");
    }

    @Test
    void aFittingWithNothingInItIsNotOffered() {
        final Table table = Table.opened().laying(dressed());
        assertTrue(table.place(2, 1), "the collar's inlay could not be picked");

        assertFalse(table.menu().canRemove(), "an empty inlay was offered for removal");
        assertFalse(table.remove(), "an empty inlay was emptied again");
    }

    // ---- the piece's own row ---------------------------------------------------------------------

    @Test
    void thePiecesOwnRowTakesTheTrimOff() {
        final Table table = Table.opened().laying(dressed());
        assertTrue(table.row(4), "the piece's own row could not be picked");

        assertTrue(table.menu().canRemove(), "a trimmed piece was not offered its trim back");
        assertTrue(table.remove(), "the trim was not removed");

        assertFalse(table.display(1).has(DataComponents.TRIM), "the trim is still on the piece");
        assertTrue(table.display(1).has(ModDataComponents.SKIN), "the skin came off with the trim");
    }

    /**
     * The skin's place is the first of that row, and taking a skin off is the strongest of the
     * three: it was the only thing this mod had put on the piece, so what is left is vanilla armor.
     */
    @Test
    void theFirstPlaceTakesTheSkinOffAndLeavesVanillaArmor() {
        final ItemStack plain = Table.armor(EquipmentSlot.CHEST);
        final Table table = Table.opened().laying(Table.skinned(plain, "plate"));
        assertTrue(table.place(4, 0), "the skin's place could not be picked");

        assertTrue(table.menu().canRemove(), "a skinned piece was not offered its skin back");
        assertTrue(table.remove(), "the skin was not removed");

        assertTrue(ItemStack.matches(plain, table.display(1)),
            "what is left is not vanilla armor: " + table.display(1).getComponents());
    }

    @Test
    void theSecondPlaceTakesTheGarmentOff() {
        final Table table = Table.opened().laying(dressed());
        assertTrue(table.place(4, 1), "the garment's place could not be picked");

        assertTrue(table.menu().canRemove(), "a clothed piece was not offered its garment back");
        assertTrue(table.remove(), "the garment was not removed");

        assertFalse(table.display(1).has(ModDataComponents.CLOTH), "the garment is still on the piece");
        assertTrue(table.display(1).has(ModDataComponents.SKIN), "the skin came off with the garment");
        assertTrue(table.display(1).has(DataComponents.TRIM), "the trim came off with the garment");
    }

    // ---- the refusals ----------------------------------------------------------------------------

    @Test
    void aPieceBeingWorkedOnAsAWholeHasNothingToRemove() {
        final Table table = Table.opened().laying(dressed());

        assertFalse(table.menu().canRemove(), "a piece picked as a whole offered something");
        assertFalse(table.remove(), "a piece picked as a whole was emptied");
    }

    @Test
    void anEmptySocketAndAnUntrimmedPieceAreBothRefused() {
        final Table bare = Table.opened().laying(Table.armor(EquipmentSlot.CHEST));

        assertTrue(bare.row(0), "the pauldrons row could not be picked");
        assertFalse(bare.menu().canRemove(), "an empty socket offered something");
        assertFalse(bare.remove(), "an empty socket was emptied");

        assertTrue(bare.row(4), "the piece's own row could not be picked");
        assertFalse(bare.menu().canRemove(), "an untrimmed, unskinned piece offered something");
        assertFalse(bare.remove(), "an untrimmed, unskinned piece was emptied");
    }

    // ---- the two questions, asked together --------------------------------------------------------

    /**
     * Every place the button lights on is a place Remove empties, and every place it empties is one
     * it lit on - over every row and every place of a piece with something in some of them and
     * nothing in the rest. The mapping from a place to what it takes off is written once; this is
     * what holds the button to it.
     */
    @Test
    void everyPlaceRemoveEmptiesIsOneItSaidItWould() {
        final ItemStack piece = dressed();
        final List<String> disagreed = new ArrayList<>();

        final Table table = Table.opened().laying(piece);
        final int rows = table.menu().rowCount();
        for (int row = 0; row < rows; row++) {
            // On the piece as it starts, not as the last Remove left it: a row whose part has just
            // been taken off offers no places at all, and reading the bound afterwards would walk
            // straight past the places this sweep exists to visit.
            table.laying(1, piece.copy());
            final int places = table.menu().placesAt(row);
            for (int place = -1; place < places; place++) {
                table.laying(1, piece.copy());
                pick(table, row, place);
                final String where = "row " + row + " place " + place;
                assertEquals(row, table.menu().selectedRow(), where + " was not picked");
                assertEquals(place, table.menu().selectedFitting(), where + " was not picked");

                final boolean lit = table.menu().canRemove();
                final boolean emptied = table.remove();
                final boolean changed = !ItemStack.matches(piece, table.display(1));
                if (lit != emptied || emptied != changed) {
                    disagreed.add(where + ": the button said " + lit + ", Remove said " + emptied
                        + ", and the piece " + (changed ? "changed" : "did not change"));
                }
            }
        }
        assertTrue(disagreed.isEmpty(), () -> "Remove and the button that lights it disagree:\n  "
            + String.join("\n  ", disagreed));
    }

    private static void pick(final Table table, final int row, final int place) {
        if (place < 0) {
            table.row(row);
        } else {
            table.place(row, place);
        }
    }

    // ---- the piece --------------------------------------------------------------------------------

    /**
     * A chestplate with something in every kind of place and nothing in several: two parts, one of
     * their four fittings filled, an empty socket, a trim, a skin and a garment.
     */
    private static ItemStack dressed() {
        ItemStack piece = Table.armor(EquipmentSlot.CHEST);
        piece = Table.wearing(piece, DecorationAnchor.COLLAR,
            Table.part(DecorationAnchor.COLLAR, "guard", "inlay"));
        piece = Table.setting(piece, DecorationAnchor.COLLAR, Table.fitting("guard"),
            Table.metal("minecraft:iron"));
        piece = Table.wearing(piece, DecorationAnchor.VAMBRACES,
            Table.part(DecorationAnchor.VAMBRACES, "gemstone"));
        piece = Table.trimmed(piece);
        piece = Table.skinned(piece, "plate");
        piece = Table.clothed(piece, "tabard");
        assertEquals(2, piece.getOrDefault(ModDataComponents.DECORATIONS, ArmorDecorations.EMPTY)
            .entries().size(), "the piece this class is about is not what it says it is");
        return piece;
    }
}
