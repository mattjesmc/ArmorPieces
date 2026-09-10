package com.mattjesmc.armorpieces.menu;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.mattjesmc.armorpieces.GameBootstrap;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import java.util.List;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * What the advanced smithing table is working on: which piece, which row of it, and which place of
 * that row.
 *
 * <p>This is the whole of what the table adds to a smithing table besides Remove - "saying where" -
 * and every one of the three is a number that both sides keep in a {@code DataSlot}. Apply reads
 * them to narrow a fitting, Remove reads them to know what to empty, and the screen reads them to
 * draw. A wrong one is not a crash: it is a button that lights on one row and works on another,
 * which is exactly the bug this class exists to make expensive.
 *
 * <p>The rows a piece lists are its own sockets - {@link DecorationAnchor#forSlot} - and then one
 * more underneath for the things the PIECE wears rather than any socket: its trim, its skin, and, if
 * it is armor a garment can go on, its cloth. That last row is where most of the arithmetic below
 * lives, because it is the one row whose width depends on what the piece is.
 */
class TableSelectionTest {
    @BeforeAll
    static void world() {
        GameBootstrap.content();
    }

    // ---- the selection follows the pieces ------------------------------------------------------

    @Test
    void anEmptyTableIsWorkingOnNothing() {
        final Table table = Table.opened();

        assertEquals(-1, table.menu().selected(), "an empty table selected a piece");
        assertTrue(table.selected().isEmpty(), "an empty table has a selected stack");
        assertEquals(0, table.menu().rowCount(), "an empty table lists rows");
        assertEquals(List.of(), table.menu().selectedAnchors(), "an empty table lists sockets");
    }

    /** The first piece laid in is the one being worked on: nobody should have to pick it. */
    @Test
    void theFirstPieceLaidInSelectsItself() {
        final Table table = Table.opened().laying(Table.armor(EquipmentSlot.LEGS));

        assertEquals(2, table.menu().selected(), "the leggings did not select themselves");
    }

    /** And the second does not take it away from the first. */
    @Test
    void aSecondPieceDoesNotStealTheSelection() {
        final Table table = Table.opened()
            .laying(Table.armor(EquipmentSlot.LEGS))
            .laying(Table.armor(EquipmentSlot.HEAD));

        assertEquals(2, table.menu().selected(), "laying a helmet in moved the selection");
    }

    /** Taking the selected piece out moves the selection to whatever is left, never to nothing. */
    @Test
    void takingTheSelectedPieceOutMovesTheSelectionToWhatIsLeft() {
        final Table table = Table.opened()
            .laying(Table.armor(EquipmentSlot.HEAD))
            .laying(Table.armor(EquipmentSlot.FEET));
        assertEquals(0, table.menu().selected(), "the helmet was not selected to start with");

        table.taking(0);

        assertEquals(3, table.menu().selected(), "the selection did not follow to the boots");
    }

    @Test
    void takingTheLastPieceOutLeavesNothingSelected() {
        final Table table = Table.opened().laying(Table.armor(EquipmentSlot.HEAD)).taking(0);

        assertEquals(-1, table.menu().selected(), "an empty table is still working on something");
    }

    @Test
    void anEmptySlotCannotBePickedAndWhatIsPickedCannotBePickedAgain() {
        final Table table = Table.opened().laying(Table.armor(EquipmentSlot.HEAD));

        assertFalse(table.select(1), "an empty display slot was picked");
        assertFalse(table.select(0), "the piece already being worked on was picked again");
        assertTrue(table.select(0) == table.select(0), "picking is not idempotent");
    }

    @Test
    void pickingAnotherPieceForgetsTheRowPickedOnTheLast() {
        final Table table = Table.opened()
            .laying(chestplate())
            .laying(Table.armor(EquipmentSlot.HEAD));
        assertTrue(table.place(2, 0), "the collar's guard could not be picked");

        assertTrue(table.select(0), "the helmet could not be picked");

        assertEquals(-1, table.menu().selectedRow(), "the row picked on the chestplate stood");
        assertEquals(-1, table.menu().selectedFitting(), "the place picked on the chestplate stood");
    }

    /** The piece being worked on stands out of the column, and the others stay in it. */
    @Test
    void thePieceBeingWorkedOnStandsOutOfTheColumn() {
        final Table table = Table.opened()
            .laying(Table.armor(EquipmentSlot.HEAD))
            .laying(Table.armor(EquipmentSlot.FEET));

        assertEquals(AdvancedSmithingMenu.DISPLAY_SELECTED_X,
            table.menu().getSlot(AdvancedSmithingMenu.DISPLAY_SLOT_START).x,
            "the selected piece stayed in the column");
        assertEquals(AdvancedSmithingMenu.DISPLAY_X,
            table.menu().getSlot(AdvancedSmithingMenu.DISPLAY_SLOT_START + 3).x,
            "an unselected piece left the column");

        table.select(3);

        assertEquals(AdvancedSmithingMenu.DISPLAY_X,
            table.menu().getSlot(AdvancedSmithingMenu.DISPLAY_SLOT_START).x,
            "the piece that was put down did not go back in the column");
        assertEquals(AdvancedSmithingMenu.DISPLAY_SELECTED_X,
            table.menu().getSlot(AdvancedSmithingMenu.DISPLAY_SLOT_START + 3).x,
            "the piece picked up did not come out of the column");
    }

    // ---- the rows a piece lists ------------------------------------------------------------------

    /**
     * Every piece lists its own sockets and one row of its own under them - and no piece lists more
     * rows than the button ids leave room for.
     */
    @Test
    void everyPieceListsItsOwnSocketsAndOneRowOfItsOwn() {
        for (final EquipmentSlot worn : AdvancedSmithingMenu.DISPLAY_SLOTS) {
            final Table table = Table.opened().laying(Table.armor(worn));
            final List<DecorationAnchor> sockets = DecorationAnchor.forSlot(worn);

            assertEquals(sockets, table.menu().selectedAnchors(),
                () -> "the " + worn + " piece lists the wrong sockets");
            assertEquals(sockets.size() + 1, table.menu().rowCount(),
                () -> "the " + worn + " piece does not list its own row under its sockets");
            assertTrue(table.menu().rowCount() <= AdvancedSmithingMenu.MAX_ROWS,
                () -> "the " + worn + " piece lists more rows than the buttons carry");
        }
    }

    /** The last row is the piece's own, and it names no socket. */
    @Test
    void theRowUnderTheSocketsIsThePiecesOwn() {
        final Table table = Table.opened().laying(chestplate());
        final List<DecorationAnchor> sockets = table.menu().selectedAnchors();

        for (int row = 0; row < sockets.size(); row++) {
            final int at = row;
            assertFalse(table.menu().isTrimRow(row), () -> "socket row " + at + " is the piece's own");
            assertEquals(sockets.get(row), table.menu().anchorAt(row),
                () -> "row " + at + " names another socket");
        }
        assertTrue(table.menu().isTrimRow(sockets.size()), "the last row is not the piece's own");
        assertNull(table.menu().anchorAt(sockets.size()), "the piece's own row names a socket");
    }

    /** A socket row's places are the part's own fittings, and an empty socket has none. */
    @Test
    void aSocketRowsPlacesAreThePartsOwnFittings() {
        final Table table = Table.opened().laying(chestplate());

        assertEquals(0, table.menu().placesAt(0), "an empty socket offers places");
        assertNull(table.menu().entryAt(0), "an empty socket holds something");
        assertEquals(2, table.menu().placesAt(2), "the collar's two fittings are not two places");
        assertEquals(List.of(Table.fitting("guard"), Table.fitting("inlay")),
            table.menu().fittingsAt(2), "the collar's places are not its part's own fittings");
        assertEquals(1, table.menu().placesAt(3), "the vambraces' one fitting is not one place");
    }

    /**
     * A part with more fittings than a row has room for is cut to what the buttons can address.
     * Nothing shipped has four; a pack could, and the row must not run off the end of its ids.
     */
    @Test
    void noRowOffersMorePlacesThanTheButtonsCarry() {
        final ItemStack crowded = Table.wearing(DecorationAnchor.COLLAR,
            Table.partWith(DecorationAnchor.COLLAR, "guard", "inlay", "gemstone", "banner"));
        final Table table = Table.opened().laying(crowded);

        assertEquals(AdvancedSmithingMenu.MAX_FITTINGS, table.menu().placesAt(2),
            "a part with four fittings was given four places");
        assertEquals(AdvancedSmithingMenu.MAX_FITTINGS, table.menu().fittingsAt(2).size(),
            "the row lists more fittings than it has places");
    }

    // ---- the piece's own row ---------------------------------------------------------------------

    /**
     * The piece's own row carries the trim, the skin beside it, and the cloth beside that - and the
     * cloth's place only exists on armor a garment can go on.
     */
    @Test
    void onlyAPieceAGarmentGoesOnHasAPlaceForOne() {
        final Table chest = Table.opened().laying(Table.armor(EquipmentSlot.CHEST));
        assertEquals(2, chest.menu().placesAt(4), "a chestplate has no place for a garment");
        assertTrue(chest.menu().isClothPlace(4, 1), "the chestplate's second place is not the cloth's");

        final Table head = Table.opened().laying(Table.armor(EquipmentSlot.HEAD));
        assertEquals(1, head.menu().placesAt(3), "a helmet was offered a place for a garment");
        assertFalse(head.menu().isClothPlace(3, 1), "a helmet has a cloth place after all");
    }

    /**
     * And a piece already wearing one keeps its place for it however the tag has since narrowed -
     * otherwise a garment applied under an older pack could never be taken off.
     */
    @Test
    void aPieceStillWearingAGarmentKeepsThePlaceForIt() {
        final Table table = Table.opened()
            .laying(Table.clothed(Table.armor(EquipmentSlot.HEAD), "tabard"));

        assertEquals(2, table.menu().placesAt(3), "the helmet's garment has nowhere to be taken off");
        assertTrue(table.menu().isClothPlace(3, 1), "the place it has is not the garment's");
    }

    /** The skin's place is the first of the piece's own row, and only of that row. */
    @Test
    void theSkinsPlaceIsTheFirstOfThePiecesOwnRow() {
        final Table table = Table.opened().laying(chestplate());

        assertTrue(table.menu().isSkinPlace(4, 0), "the piece's own first place is not the skin's");
        assertFalse(table.menu().isSkinPlace(4, 1), "the skin has two places");
        assertFalse(table.menu().isSkinPlace(2, 0), "a socket row's first place is the skin's");
        assertFalse(table.menu().isClothPlace(2, 1), "a socket row's second place is the cloth's");
    }

    /** What the piece's own row reads back: the skin and the garment it is wearing. */
    @Test
    void thePiecesOwnRowKnowsWhatItIsWearing() {
        final Table bare = Table.opened().laying(Table.armor(EquipmentSlot.CHEST));
        assertNull(bare.menu().selectedSkin(), "a bare piece is wearing a skin");
        assertNull(bare.menu().selectedCloth(), "a bare piece is wearing a garment");

        final Table dressed = Table.opened().laying(
            Table.clothed(Table.skinned(Table.armor(EquipmentSlot.CHEST), "plate"), "tabard"));
        assertNotNull(dressed.menu().selectedSkin(), "the skin it is wearing was not read");
        assertSame(Table.skin("plate"), dressed.menu().selectedSkin().skin(), "another skin was read");
        assertNotNull(dressed.menu().selectedCloth(), "the garment it is wearing was not read");
        assertSame(Table.cloth("tabard"), dressed.menu().selectedCloth().cloth(), "another garment was read");
    }

    // ---- picking a row -----------------------------------------------------------------------------

    /**
     * Every row and every place has a button id of its own, and the table decodes each back to the
     * pair it names. The arithmetic is a division and a remainder over {@link
     * AdvancedSmithingMenu#MAX_FITTINGS}, and swapping them is a table that empties the wrong socket.
     */
    @Test
    void everyRowAndPlaceHasAButtonIdOfItsOwn() {
        final Table table = Table.opened().laying(crowdedChestplate());

        for (int row = 0; row < table.menu().rowCount(); row++) {
            assertTrue(table.row(row), "row " + row + " could not be picked");
            assertEquals(row, table.menu().selectedRow(), "the wrong row was picked");
            assertEquals(-1, table.menu().selectedFitting(), "picking a row picked a place too");

            for (int place = 0; place < table.menu().placesAt(row); place++) {
                assertTrue(table.place(row, place),
                    "place " + place + " of row " + row + " could not be picked");
                assertEquals(row, table.menu().selectedRow(),
                    "picking a place moved to another row");
                assertEquals(place, table.menu().selectedFitting(),
                    "picking a place picked another place");
            }
        }
    }

    /** A row the piece has not got, and a place the row has not got, are both refused. */
    @Test
    void aRowOrPlaceThePieceHasNotGotIsRefused() {
        final Table table = Table.opened().laying(Table.armor(EquipmentSlot.FEET));
        assertEquals(3, table.menu().rowCount(), "the boots do not list three rows");

        assertFalse(table.row(3), "the boots were given a fourth row");
        assertFalse(table.place(0, 0), "an empty socket was given a place");
        assertFalse(table.place(2, 1), "the boots were given a place for a garment");
        assertEquals(-1, table.menu().selectedRow(), "a refused pick still changed the row");
    }

    /** The socket being worked on is the row's, and the piece's own row is nobody's socket. */
    @Test
    void theSocketBeingWorkedOnIsTheRowsOwn() {
        final Table table = Table.opened().laying(chestplate());

        assertNull(table.menu().selectedAnchor(), "a piece picked as a whole is working on a socket");
        table.row(2);
        assertEquals(DecorationAnchor.COLLAR, table.menu().selectedAnchor(), "the wrong socket");
        table.row(4);
        assertNull(table.menu().selectedAnchor(), "the piece's own row is a socket");
    }

    // ---- what a change to the piece does to the selection ------------------------------------------

    /**
     * A place the part in that row no longer has is dropped, with the piece standing still. Left
     * alone it would aim Apply and Remove at a fitting that is not there.
     */
    @Test
    void aPlaceTheNewPartCannotSupportIsDropped() {
        final Table table = Table.opened().laying(chestplate());
        assertTrue(table.place(2, 1), "the collar's inlay could not be picked");

        // The same socket, a part with one fitting instead of two - what Apply leaves behind.
        table.laying(1, Table.wearing(Table.armor(EquipmentSlot.CHEST), DecorationAnchor.COLLAR,
            Table.partWith(DecorationAnchor.COLLAR, "guard")));

        assertEquals(2, table.menu().selectedRow(), "the row was dropped as well");
        assertEquals(-1, table.menu().selectedFitting(), "the place the part no longer has stood");
    }

    @Test
    void aRowOnAPieceThatLeavesTheTableIsDropped() {
        final Table table = Table.opened().laying(chestplate());
        assertTrue(table.row(3), "the vambraces row could not be picked");

        table.taking(1);

        assertEquals(-1, table.menu().selectedRow(), "a row of a piece that is gone still stands");
        assertEquals(-1, table.menu().selectedFitting(), "a place of a piece that is gone still stands");
    }

    // ---- the pieces ----------------------------------------------------------------------------

    /** A chestplate with a two-fitting part in its collar and a one-fitting part in its vambraces. */
    private static ItemStack chestplate() {
        return Table.wearing(
            Table.wearing(DecorationAnchor.COLLAR, Table.part(DecorationAnchor.COLLAR, "guard", "inlay")),
            DecorationAnchor.VAMBRACES, Table.part(DecorationAnchor.VAMBRACES, "gemstone"));
    }

    /** The same, with every socket filled, so every row of it has places to sweep. */
    private static ItemStack crowdedChestplate() {
        return Table.wearing(
            Table.wearing(chestplate(), DecorationAnchor.PAULDRONS, Table.part(DecorationAnchor.PAULDRONS)),
            DecorationAnchor.BACK, Table.part(DecorationAnchor.BACK));
    }
}
