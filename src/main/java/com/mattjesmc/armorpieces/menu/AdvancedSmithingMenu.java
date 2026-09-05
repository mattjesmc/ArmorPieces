package com.mattjesmc.armorpieces.menu;

import com.mattjesmc.armorpieces.cloth.ClothValue;
import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.recipe.SmithingClothRecipe;
import com.mattjesmc.armorpieces.recipe.SmithingFittingRecipe;
import com.mattjesmc.armorpieces.registry.ModBlocks;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.registry.ModMenus;
import com.mattjesmc.armorpieces.skin.ArmorSkinValue;
import java.util.List;
import java.util.Optional;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.component.DataComponents;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerLevelAccess;
import net.minecraft.world.inventory.DataSlot;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipePropertySet;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.item.crafting.SmithingRecipe;
import net.minecraft.world.item.crafting.SmithingRecipeInput;
import net.minecraft.world.item.equipment.Equippable;
import net.minecraft.world.level.Level;
import org.jspecify.annotations.Nullable;

/**
 * The advanced smithing table's menu: four pieces of armor on display, one of them selected, its
 * sockets listed, and a template-and-material pair that runs the ordinary smithing recipe on it.
 *
 * <p>Three things the vanilla smithing table cannot do, and nothing it can do differently:
 *
 * <ul>
 *   <li><b>Taking a part off.</b> Remove empties whatever is selected: a whole part out of its
 *       socket, one fitting out of the part sitting in it, the piece's trim, its skin, or the cloth
 *       it is wearing. The
 *       smithing table has no ingredient that means "nothing", so a filled socket there stays
 *       filled until another part replaces it; this is the one place any of the four comes off.
 *       Nothing is refunded - the template was spent putting it on, as a trim's template is.</li>
 *   <li><b>Saying where.</b> A row of the selected piece can be worked on rather than the piece as
 *       a whole, and then a fitting goes into that socket alone instead of into every part on the
 *       piece that takes it. See {@link #assemble}.</li>
 *   <li><b>Seeing the set.</b> The four display slots are worn together by the preview stand, so a
 *       crest is judged against the spaulders below it rather than alone.</li>
 *   <li><b>Working on a piece in place.</b> Apply writes the result back into the display slot
 *       instead of into a result slot, so a helmet takes a part, then a stone, then another part
 *       without being picked up in between.</li>
 * </ul>
 *
 * <p>Apply itself is deliberately NOT a new rule. The template and material slots plus the selected
 * piece are handed to the recipe manager as a {@link SmithingRecipeInput}, exactly as the smithing
 * table hands its three slots, and whatever recipe matches is what runs: this mod's socket and
 * fitting recipes, but also a vanilla trim or a netherite upgrade, and NOT a recipe a pack has turned
 * off. A second implementation of "what may be applied" would drift from the first; reusing the
 * lookup means the two tables can never disagree.
 *
 * <p>The client cannot run that lookup - recipes do not travel to it - so the server publishes the
 * result itself, in a hidden slot ({@link #PREVIEW_SLOT}) that is synced like any other and never
 * drawn or clicked: the stand wears it in place of the selected piece, so what Apply would do is
 * seen before it is done, exactly as the smithing table's stand previews its result slot. Apply is
 * lit while that slot holds something. Selection and removal need no recipe and run on both sides,
 * which is what makes them feel instant; the server's copy is still the one that counts.
 *
 * <p>No block entity, no persistence: like every vanilla crafting station, everything in the table
 * goes back to the player when the menu closes.
 */
public class AdvancedSmithingMenu extends AbstractContainerMenu {
    /** The four display slots, in the order the inventory lists armor: head to toe. */
    public static final List<EquipmentSlot> DISPLAY_SLOTS =
        List.of(EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET);
    private static final List<Identifier> DISPLAY_SLOT_ICONS = List.of(
        Identifier.withDefaultNamespace("container/slot/helmet"),
        Identifier.withDefaultNamespace("container/slot/chestplate"),
        Identifier.withDefaultNamespace("container/slot/leggings"),
        Identifier.withDefaultNamespace("container/slot/boots"));

    public static final int DISPLAY_SLOT_START = 0;
    public static final int TEMPLATE_SLOT = 4;
    public static final int MATERIAL_SLOT = 5;
    /** What Apply would produce, server-written, never shown as a slot. See the class comment. */
    public static final int PREVIEW_SLOT = 6;
    private static final int INV_SLOT_START = 7;
    private static final int INV_SLOT_END = 34;
    private static final int USE_ROW_SLOT_START = 34;
    private static final int USE_ROW_SLOT_END = 43;

    /**
     * Slot positions, shared with the screen so the background art and the slots agree. The sheet
     * itself is drawn from these same numbers - see {@code tools/gen_smithing_gui.py}.
     */
    public static final int DISPLAY_X = 8;
    /**
     * Where the piece being worked on stands instead: out of the column and hard against the box,
     * in the gap its own select arrow had. The arrow is dropped while it is there - the piece has
     * already been picked, and the slot standing in the arrow's place says so better than an arrow
     * pointing at it did. The other three keep theirs, so another piece is always one click away.
     */
    public static final int DISPLAY_SELECTED_X = 34;
    public static final int DISPLAY_Y = 20;
    /** Two more than a slot is tall, so a row's ground shows above and below what stands on it. */
    public static final int ROW_HEIGHT = 20;
    /** The smithing table's own two slots, under the stand in the right-hand column. */
    public static final int TEMPLATE_X = 187;
    public static final int MATERIAL_X = 205;
    public static final int INPUT_Y = 151;
    public static final int INVENTORY_Y = 138;

    /** The most rows a piece can list: four sockets - the chestplate's - and the trim under them. */
    public static final int MAX_ROWS = 5;
    /** The most fitting slots a row has room for. Shipped parts declare at most two. */
    public static final int MAX_FITTINGS = 3;

    // ---- button ids, sent as vanilla container-button clicks ------------------------------------
    /** {@code SELECT + i} selects display slot {@code i}. */
    public static final int BUTTON_SELECT = 0;
    public static final int BUTTON_APPLY = 4;
    /** Empties whatever is selected - a socket, one fitting on it, the trim, the skin or the cloth. */
    public static final int BUTTON_REMOVE = 5;
    /** {@code SELECT_ROW + row} works on that row of the selected piece, part and all. */
    public static final int BUTTON_SELECT_ROW = 8;
    /** {@code SELECT_FITTING + row * MAX_FITTINGS + slot} works on one fitting of one row. */
    public static final int BUTTON_SELECT_FITTING = 16;

    /** The smithing table's own sound cue, {@code Level.levelEvent} id. */
    private static final int SMITHING_TABLE_USE_EVENT = 1044;

    private final ContainerLevelAccess access;
    private final Level level;
    private final RecipePropertySet templateItemTest;
    private final RecipePropertySet additionItemTest;
    private final SimpleContainer display = new SimpleContainer(DISPLAY_SLOTS.size()) {
        @Override
        public void setChanged() {
            super.setChanged();
            AdvancedSmithingMenu.this.slotsChanged(this);
        }
    };
    private final SimpleContainer inputs = new SimpleContainer(2) {
        @Override
        public void setChanged() {
            super.setChanged();
            AdvancedSmithingMenu.this.slotsChanged(this);
        }
    };
    /**
     * Apply's result, kept apart from the two input containers so that writing it does not re-run
     * the lookup that produced it. Its change hook only wakes the screen.
     */
    private final SimpleContainer preview = new SimpleContainer(1) {
        @Override
        public void setChanged() {
            super.setChanged();
            AdvancedSmithingMenu.this.updateListener.run();
        }
    };
    /** Index into {@link #DISPLAY_SLOTS} of the piece being worked on, or -1 for none. */
    private final DataSlot selected = DataSlot.standalone();
    /**
     * Which row of the selected piece is being worked on - a socket, or the trim row under them -
     * or -1 while the piece is being worked on as a whole.
     */
    private final DataSlot selectedRow = DataSlot.standalone();
    /**
     * Which fitting of that row, as an index into the part's own fitting order, or -1 for the part
     * itself. Only ever set together with a socket row.
     */
    private final DataSlot selectedFitting = DataSlot.standalone();
    private Runnable updateListener = () -> {};

    public AdvancedSmithingMenu(final int containerId, final Inventory inventory) {
        this(containerId, inventory, ContainerLevelAccess.NULL);
    }

    public AdvancedSmithingMenu(final int containerId, final Inventory inventory, final ContainerLevelAccess access) {
        super(ModMenus.ADVANCED_SMITHING, containerId);
        this.access = access;
        this.level = inventory.player.level();
        // The same tests the smithing table's slots run, so the two tables light up for the same
        // items - including a datapack's smithing recipe neither has heard of.
        this.templateItemTest = this.level.recipeAccess().propertySet(RecipePropertySet.SMITHING_TEMPLATE);
        this.additionItemTest = this.level.recipeAccess().propertySet(RecipePropertySet.SMITHING_ADDITION);

        for (int i = 0; i < DISPLAY_SLOTS.size(); i++) {
            this.addSlot(new DisplaySlot(this.display, i, DISPLAY_X, DISPLAY_Y + i * ROW_HEIGHT));
        }
        this.addSlot(new Slot(this.inputs, 0, TEMPLATE_X, INPUT_Y) {
            @Override
            public boolean mayPlace(final ItemStack stack) {
                return AdvancedSmithingMenu.this.templateItemTest.test(stack);
            }
        });
        this.addSlot(new Slot(this.inputs, 1, MATERIAL_X, INPUT_Y) {
            @Override
            public boolean mayPlace(final ItemStack stack) {
                return AdvancedSmithingMenu.this.additionItemTest.test(stack);
            }
        });
        // Off-screen and inactive: never drawn, never hovered, never a click target - a slot only
        // so that the vanilla slot sync carries it to the client.
        this.addSlot(new Slot(this.preview, 0, -1000, -1000) {
            @Override
            public boolean mayPlace(final ItemStack stack) {
                return false;
            }

            @Override
            public boolean mayPickup(final Player player) {
                return false;
            }

            @Override
            public boolean isActive() {
                return false;
            }
        });
        this.addStandardInventorySlots(inventory, 8, INVENTORY_Y);

        this.addDataSlot(this.selected).set(-1);
        this.addDataSlot(this.selectedRow).set(-1);
        this.addDataSlot(this.selectedFitting).set(-1);
    }

    // ---- what the screen reads ------------------------------------------------------------------

    /** Index of the selected display slot, or -1 while none holds a piece. */
    public int selected() {
        return this.selected.get();
    }

    /** The piece being worked on, or empty. */
    public ItemStack selectedStack() {
        final int index = this.selected.get();
        return index < 0 ? ItemStack.EMPTY : this.display.getItem(index);
    }

    /** The sockets of the selected piece, head to toe; empty while nothing is selected. */
    public List<DecorationAnchor> selectedAnchors() {
        final int index = this.selected.get();
        return index < 0 || this.display.getItem(index).isEmpty()
            ? List.of()
            : DecorationAnchor.forSlot(DISPLAY_SLOTS.get(index));
    }

    /**
     * The rows the selected piece lists: one per socket, then the piece's own row under them - its
     * trim, and beside it its skin and its cloth. Zero while nothing is selected - that last row
     * belongs to a piece, not to the empty table.
     */
    public int rowCount() {
        final List<DecorationAnchor> anchors = this.selectedAnchors();
        return anchors.isEmpty() ? 0 : anchors.size() + 1;
    }

    /**
     * How many places {@code row} has BESIDE its first - the columns drawn to the right of the part
     * or the trim.
     *
     * <p>For a socket row that is the part's own fittings. For the trim row it is the piece's OWN
     * things rather than any socket's: what is painted over its texture (the trim), what its texture
     * is (the skin), and - on a chestplate - what is worn over it (the cloth). Putting them there
     * rather than each in a row of its own is what keeps a chestplate's four sockets and all three of
     * these inside one box, and it costs no width: a socket row already draws three columns.
     *
     * <p>The cloth's place is the only one here that is not on every piece, because a cloth is not:
     * it is cut out of the torso box, which is the chestplate's. A helmet with an empty place it can
     * never fill would be a promise the table cannot keep - see {@link #hasClothPlace}.
     */
    public int placesAt(final int row) {
        return this.isTrimRow(row)
            ? this.hasClothPlace() ? 2 : 1
            : this.fittingsAt(row).size();
    }

    /**
     * Whether the selected piece has a cloth place at all: armor a cloth may be put on, or armor
     * already wearing one.
     *
     * <p>The second half is what keeps a piece from stranding its own garment. Which armor may wear
     * cloth is a TAG, so a pack can narrow it after the fact, and a piece clothed under the old tag
     * must still be able to take it off - the same rule
     * {@link SmithingClothRecipe#applyCloth} keeps for the empty-addition recipe.
     */
    private boolean hasClothPlace() {
        final ItemStack piece = this.selectedStack();
        return SmithingClothRecipe.isClothable(piece) || piece.has(ModDataComponents.CLOTH);
    }

    /** Whether the place {@code fitting} of {@code row} is the skin's - column 1 of the trim row. */
    public boolean isSkinPlace(final int row, final int fitting) {
        return fitting == 0 && this.isTrimRow(row);
    }

    /** Whether the place {@code fitting} of {@code row} is the cloth's - column 2 of the trim row. */
    public boolean isClothPlace(final int row, final int fitting) {
        return fitting == 1 && this.isTrimRow(row) && this.hasClothPlace();
    }

    /** Whether the place being worked on is the skin's. */
    public boolean isSkinSelected() {
        return this.isSkinPlace(this.selectedRow.get(), this.selectedFitting.get());
    }

    /** The skin the selected piece wears, or {@code null}. */
    public @Nullable ArmorSkinValue selectedSkin() {
        return this.selectedStack().get(ModDataComponents.SKIN);
    }

    /** The cloth the selected piece wears, or {@code null}. */
    public @Nullable ClothValue selectedCloth() {
        return this.selectedStack().get(ModDataComponents.CLOTH);
    }

    /** Whether {@code row} is the trim row - the last one, under the sockets. */
    public boolean isTrimRow(final int row) {
        final List<DecorationAnchor> anchors = this.selectedAnchors();
        return !anchors.isEmpty() && row == anchors.size();
    }

    /** The socket {@code row} names, or {@code null} for the trim row and for no row at all. */
    public @Nullable DecorationAnchor anchorAt(final int row) {
        final List<DecorationAnchor> anchors = this.selectedAnchors();
        return row >= 0 && row < anchors.size() ? anchors.get(row) : null;
    }

    /** The parts on the selected piece. */
    public ArmorDecorations selectedDecorations() {
        return this.selectedStack().getOrDefault(ModDataComponents.DECORATIONS, ArmorDecorations.EMPTY);
    }

    /** What sits in {@code row}'s socket, or {@code null} if it is empty or is not a socket. */
    public @Nullable DecorationEntry entryAt(final int row) {
        final DecorationAnchor anchor = this.anchorAt(row);
        return anchor == null ? null : this.selectedDecorations().get(anchor);
    }

    /**
     * The fittings {@code row}'s part declares, in its own order - the slots the row draws beside
     * the part. Empty for an empty socket and for the trim row, and never longer than
     * {@link #MAX_FITTINGS}, which is what bounds the button ids.
     */
    public List<Holder<Fitting>> fittingsAt(final int row) {
        final DecorationEntry entry = this.entryAt(row);
        if (entry == null) {
            return List.of();
        }
        final List<Holder<Fitting>> fittings = entry.decoration().value().fittings();
        return fittings.size() <= MAX_FITTINGS ? fittings : fittings.subList(0, MAX_FITTINGS);
    }

    /** The row being worked on, or -1. */
    public int selectedRow() {
        return this.selectedRow.get();
    }

    /** The fitting of that row being worked on, or -1 for the row's part itself. */
    public int selectedFitting() {
        return this.selectedFitting.get();
    }

    /** The socket being worked on, or {@code null} while a whole piece or the trim row is. */
    public @Nullable DecorationAnchor selectedAnchor() {
        return this.anchorAt(this.selectedRow.get());
    }

    /**
     * Whether Remove would take something off. A socket row with a part in it, a fitting with
     * something set in it, or the trim row on a trimmed piece; nothing else.
     */
    public boolean canRemove() {
        final int row = this.selectedRow.get();
        if (row < 0 || row >= this.rowCount()) {
            return false;
        }
        if (this.isTrimRow(row)) {
            return this.selectedStack().has(pieceRowComponent(this.selectedFitting.get()));
        }
        final DecorationEntry entry = this.entryAt(row);
        if (entry == null) {
            return false;
        }
        final int fitting = this.selectedFitting.get();
        if (fitting < 0) {
            return true;
        }
        final List<Holder<Fitting>> fittings = this.fittingsAt(row);
        return fitting < fittings.size() && entry.fitting(fittings.get(fitting)) != null;
    }

    /** Whether the server found a smithing recipe for the current template, material and piece. */
    public boolean canApply() {
        return !this.preview.getItem(0).isEmpty();
    }

    /** What Apply would make of the selected piece, or empty. The stand wears it while it is there. */
    public ItemStack previewStack() {
        return this.preview.getItem(0);
    }

    public ItemStack displayStack(final int index) {
        return this.display.getItem(index);
    }

    /** Called whenever a display or input slot changes, on the side the listener was registered. */
    public void registerUpdateListener(final Runnable listener) {
        this.updateListener = listener;
    }

    // ---- buttons --------------------------------------------------------------------------------

    @Override
    public boolean clickMenuButton(final Player player, final int buttonId) {
        if (buttonId >= BUTTON_SELECT && buttonId < BUTTON_SELECT + DISPLAY_SLOTS.size()) {
            return this.select(buttonId - BUTTON_SELECT);
        }
        if (buttonId == BUTTON_APPLY) {
            return this.apply();
        }
        if (buttonId == BUTTON_REMOVE) {
            return this.remove();
        }
        if (buttonId >= BUTTON_SELECT_ROW && buttonId < BUTTON_SELECT_ROW + MAX_ROWS) {
            return this.selectRow(buttonId - BUTTON_SELECT_ROW, -1);
        }
        final int fittingId = buttonId - BUTTON_SELECT_FITTING;
        if (fittingId >= 0 && fittingId < MAX_ROWS * MAX_FITTINGS) {
            return this.selectRow(fittingId / MAX_FITTINGS, fittingId % MAX_FITTINGS);
        }
        return false;
    }

    private boolean select(final int index) {
        if (this.display.getItem(index).isEmpty() || this.selected.get() == index) {
            return false;
        }
        this.selected.set(index);
        // A row belongs to the piece it was picked on; the new piece starts with none picked, so
        // Apply is back to treating it as a whole and Remove has nothing to act on.
        this.selectedRow.set(-1);
        this.selectedFitting.set(-1);
        this.refresh();
        return true;
    }

    /**
     * Works on one row of the selected piece, and on one fitting of it when {@code fitting} is not
     * -1. This is what Apply routes a fitting by and what Remove empties, so it is refused for a row
     * the piece does not have, or a fitting the part in it does not declare.
     */
    private boolean selectRow(final int row, final int fitting) {
        if (row < 0 || row >= this.rowCount() || fitting >= this.placesAt(row)) {
            return false;
        }
        if (this.selectedRow.get() == row && this.selectedFitting.get() == fitting) {
            return false;
        }
        this.selectedRow.set(row);
        this.selectedFitting.set(fitting);
        this.refresh();
        return true;
    }

    /**
     * Empties whatever is selected. Both sides run this; it needs nothing the client lacks, and the
     * piece is a plain component edit either way - see {@link ArmorDecorations#without}.
     *
     * <p>Five things can be taken off, and the selection says which: a whole part out of its
     * socket, one fitting out of the part sitting in it, the piece's trim, its skin, or the cloth it
     * wears. The trim is here for the reason removal is here at all - a smithing table has no
     * ingredient meaning "nothing", so this is the one place a trim comes off - and nothing is
     * refunded, exactly as with a part.
     */
    private boolean remove() {
        final int index = this.selected.get();
        final int row = this.selectedRow.get();
        final ItemStack piece = this.selectedStack();
        if (piece.isEmpty() || row < 0 || row >= this.rowCount()) {
            return false;
        }
        final ItemStack edited = this.isTrimRow(row)
            ? without(piece, pieceRowComponent(this.selectedFitting.get()))
            : this.withoutPart(piece, row);
        if (edited.isEmpty()) {
            return false;
        }
        this.display.setItem(index, edited);
        return true;
    }

    /**
     * What place {@code fitting} of the piece's own row takes off - and the ONE place that mapping is
     * written, because {@link #canRemove} and {@link #remove} both read it and a table whose button
     * lights for one place and empties another is exactly the bug that costs.
     *
     * <p>{@code -1} is the row itself, and on this row the row itself is the trim.
     */
    private static DataComponentType<?> pieceRowComponent(final int fitting) {
        return switch (fitting) {
            case 0 -> ModDataComponents.SKIN;
            case 1 -> ModDataComponents.CLOTH;
            default -> DataComponents.TRIM;
        };
    }

    /**
     * The piece without one of the three things its own row carries, or empty if it did not have it.
     *
     * <p>Worth stating what taking the skin off means, since it is the strongest of the three: the
     * piece is then vanilla armor again, byte for byte, because the skin was the only thing this mod
     * put on it. The smithing table can do all three too - the template, the armor, an empty third
     * slot - and this is the place each costs nothing.
     */
    private static ItemStack without(final ItemStack piece, final DataComponentType<?> component) {
        if (!piece.has(component)) {
            return ItemStack.EMPTY;
        }
        final ItemStack edited = piece.copy();
        edited.remove(component);
        return edited;
    }

    /**
     * The piece with the selected row's part - or the selected fitting of it - taken off, or empty
     * if there was nothing there to take.
     */
    private ItemStack withoutPart(final ItemStack piece, final int row) {
        final DecorationAnchor anchor = this.anchorAt(row);
        final ArmorDecorations decorations = piece.get(ModDataComponents.DECORATIONS);
        if (anchor == null || decorations == null) {
            return ItemStack.EMPTY;
        }
        final int fitting = this.selectedFitting.get();
        if (fitting >= 0) {
            final DecorationEntry entry = decorations.get(anchor);
            final List<Holder<Fitting>> fittings = this.fittingsAt(row);
            if (entry == null || fitting >= fittings.size()) {
                return ItemStack.EMPTY;
            }
            final DecorationEntry emptied = entry.withoutFitting(fittings.get(fitting));
            if (emptied == entry) {
                return ItemStack.EMPTY;
            }
            final ItemStack edited = piece.copy();
            edited.set(ModDataComponents.DECORATIONS, decorations.with(anchor, emptied));
            return edited;
        }
        final Optional<ArmorDecorations> remaining = decorations.without(anchor);
        if (remaining.isEmpty()) {
            return ItemStack.EMPTY;
        }
        final ItemStack edited = piece.copy();
        if (remaining.get().isEmpty()) {
            // Down to nothing: drop the component rather than keep an empty map, so the piece is
            // byte-for-byte the undecorated item again and stacks with one.
            edited.remove(ModDataComponents.DECORATIONS);
        } else {
            edited.set(ModDataComponents.DECORATIONS, remaining.get());
        }
        return edited;
    }

    /**
     * The smithing table's craft, with the selected piece as the base and the result written back
     * over it. Server only, since only the server has recipes; the client returns whether the
     * server last said Apply would work, so the screen sends the click exactly when it would land.
     */
    private boolean apply() {
        if (!(this.level instanceof ServerLevel)) {
            return this.canApply();
        }
        final int index = this.selected.get();
        final ItemStack result = this.findResult();
        if (result.isEmpty()) {
            return false;
        }
        this.display.setItem(index, result);
        this.shrinkInput(0);
        this.shrinkInput(1);
        this.access.execute((level, pos) -> level.levelEvent(SMITHING_TABLE_USE_EVENT, pos, 0));
        return true;
    }

    private void shrinkInput(final int slot) {
        final ItemStack stack = this.inputs.getItem(slot);
        if (!stack.isEmpty()) {
            stack.shrink(1);
            this.inputs.setItem(slot, stack);
        }
    }

    /**
     * What Apply would produce right now, or empty. The lookup the smithing table runs, on the same
     * three stacks it would see. The result must still fit the display slot it replaces - a recipe
     * that turned a helmet into something that is not one has nowhere to go here.
     */
    private ItemStack findResult() {
        final int index = this.selected.get();
        final ItemStack base = this.selectedStack();
        if (base.isEmpty() || !(this.level instanceof ServerLevel serverLevel)) {
            return ItemStack.EMPTY;
        }
        final SmithingRecipeInput input =
            new SmithingRecipeInput(this.inputs.getItem(0), base, this.inputs.getItem(1));
        return serverLevel.recipeAccess()
            .getRecipeFor(RecipeType.SMITHING, input, serverLevel)
            .map(recipe -> this.assemble(recipe.value(), input))
            .filter(result -> !result.isEmpty() && fitsSlot(result, DISPLAY_SLOTS.get(index)))
            .orElse(ItemStack.EMPTY);
    }

    /**
     * The matched recipe's own result, except that a fitting goes where the table says it goes.
     *
     * <p>{@link SmithingFittingRecipe} routes by the item alone, because the smithing table has
     * nowhere to say more: a gem lands in the gemstone of every part on the piece that has one. This
     * table does have somewhere to say more - the row that is selected - so it narrows the same rule
     * to that socket, and to that one fitting when a fitting slot is what is picked. Nothing else
     * about the recipe changes: it is still the recipe manager that decided a recipe matched, and a
     * pack that turned this one off has turned it off here.
     *
     * <p>Narrowed only while a socket row is selected. With the piece selected as a whole - which is
     * how it starts - the recipe's own routing stands, and one gem still fits every part that takes
     * one.
     */
    private ItemStack assemble(final SmithingRecipe recipe, final SmithingRecipeInput input) {
        final DecorationAnchor anchor = this.selectedAnchor();
        if (anchor == null || !(recipe instanceof SmithingFittingRecipe)) {
            return recipe.assemble(input);
        }
        // The template's own choice wins over the selected slot: it is the more specific statement
        // of the two, and a template that names a fitting is asking for exactly that one.
        Holder<Fitting> only = input.template().get(ModDataComponents.FITTING);
        if (only == null) {
            final int fitting = this.selectedFitting.get();
            final List<Holder<Fitting>> fittings = this.fittingsAt(this.selectedRow.get());
            only = fitting >= 0 && fitting < fittings.size() ? fittings.get(fitting) : null;
        }
        return SmithingFittingRecipe.applyFitting(input.base(), input.addition(), only, anchor);
    }

    private static boolean fitsSlot(final ItemStack stack, final EquipmentSlot slot) {
        final Equippable equippable = stack.get(DataComponents.EQUIPPABLE);
        return equippable != null && equippable.slot() == slot;
    }

    // ---- bookkeeping ----------------------------------------------------------------------------

    @Override
    public void slotsChanged(final Container container) {
        super.slotsChanged(container);
        // The selection follows the pieces: the first one placed selects itself, and taking the
        // selected one out moves the selection to whatever is left, so the list is never showing a
        // piece that is not there.
        final int current = this.selected.get();
        if (current < 0 || this.display.getItem(current).isEmpty()) {
            this.selected.set(this.firstDisplayed());
        }
        this.clampSelection();
        this.refresh();
    }

    /**
     * Drops a row or fitting selection the piece no longer supports - it was on a piece that has
     * been taken out, or on a part that has just been swapped for one with fewer fittings. Left
     * standing, it would aim Apply and Remove at something that is not there.
     */
    private void clampSelection() {
        final int row = this.selectedRow.get();
        if (row < 0) {
            return;
        }
        if (row >= this.rowCount()) {
            this.selectedRow.set(-1);
            this.selectedFitting.set(-1);
        } else if (this.selectedFitting.get() >= this.placesAt(row)) {
            this.selectedFitting.set(-1);
        }
    }

    private int firstDisplayed() {
        for (int i = 0; i < DISPLAY_SLOTS.size(); i++) {
            if (!this.display.getItem(i).isEmpty()) {
                return i;
            }
        }
        return -1;
    }

    /** Re-evaluates Apply on the server and lets the screen know something moved. */
    private void refresh() {
        this.layOutDisplaySlots();
        if (this.level instanceof ServerLevel) {
            final ItemStack result = this.findResult();
            if (!ItemStack.matches(result, this.preview.getItem(0))) {
                this.preview.setItem(0, result);
            }
        }
        this.updateListener.run();
    }

    /**
     * Puts the display slots where the selection says they go: the piece being worked on out beside
     * the box, the rest in the column. See {@link #DISPLAY_SELECTED_X}.
     *
     * <p>A slot's position is final, so moving one means putting another in its place, at the same
     * index and over the same container - the slot's identity to everything but the eye. Only the
     * client draws slots, but both sides run this: a menu whose halves disagree about anything is a
     * menu that will be debugged later.
     */
    private void layOutDisplaySlots() {
        for (int i = 0; i < DISPLAY_SLOTS.size(); i++) {
            final int index = DISPLAY_SLOT_START + i;
            final int x = i == this.selected.get() ? DISPLAY_SELECTED_X : DISPLAY_X;
            if (this.slots.get(index).x != x) {
                final Slot moved = new DisplaySlot(this.display, i, x, DISPLAY_Y + i * ROW_HEIGHT);
                moved.index = index;
                this.slots.set(index, moved);
            }
        }
    }

    @Override
    public boolean stillValid(final Player player) {
        return stillValid(this.access, player, ModBlocks.advancedSmithingTable());
    }

    /**
     * Hands everything back. Guarded on the side, not on the block: vanilla routes this through the
     * level access, which is nothing when the menu was opened by {@code /armorpieces table} rather
     * than a block, and "nothing" there means the stacks in the display and input slots are lost
     * on close. The preview is dropped first, since it was never the player's.
     */
    @Override
    public void removed(final Player player) {
        super.removed(player);
        this.preview.removeItemNoUpdate(0);
        if (!this.level.isClientSide()) {
            this.clearContainer(player, this.display);
            this.clearContainer(player, this.inputs);
        }
    }

    /**
     * Shift-click routing. Out of the table's own slots into the inventory; out of the inventory
     * into the first table slot that takes the item - a display slot for armor, then the template
     * and material slots - and failing that between the two inventory halves as every menu does.
     */
    @Override
    public ItemStack quickMoveStack(final Player player, final int slotIndex) {
        ItemStack moved = ItemStack.EMPTY;
        final Slot slot = this.slots.get(slotIndex);
        if (slot == null || !slot.hasItem()) {
            return moved;
        }
        final ItemStack stack = slot.getItem();
        moved = stack.copy();
        if (slotIndex == PREVIEW_SLOT) {
            return ItemStack.EMPTY;
        }
        if (slotIndex < INV_SLOT_START) {
            if (!this.moveItemStackTo(stack, INV_SLOT_START, USE_ROW_SLOT_END, true)) {
                return ItemStack.EMPTY;
            }
        } else if (!this.moveIntoTable(stack)) {
            if (slotIndex < INV_SLOT_END) {
                if (!this.moveItemStackTo(stack, USE_ROW_SLOT_START, USE_ROW_SLOT_END, false)) {
                    return ItemStack.EMPTY;
                }
            } else if (!this.moveItemStackTo(stack, INV_SLOT_START, INV_SLOT_END, false)) {
                return ItemStack.EMPTY;
            }
        }
        if (stack.isEmpty()) {
            slot.setByPlayer(ItemStack.EMPTY);
        } else {
            slot.setChanged();
        }
        if (stack.getCount() == moved.getCount()) {
            return ItemStack.EMPTY;
        }
        slot.onTake(player, stack);
        return moved;
    }

    private boolean moveIntoTable(final ItemStack stack) {
        for (int i = 0; i < DISPLAY_SLOTS.size(); i++) {
            final Slot displaySlot = this.slots.get(DISPLAY_SLOT_START + i);
            if (displaySlot.mayPlace(stack) && !displaySlot.hasItem()
                && this.moveItemStackTo(stack, DISPLAY_SLOT_START + i, DISPLAY_SLOT_START + i + 1, false)) {
                return true;
            }
        }
        if (this.slots.get(TEMPLATE_SLOT).mayPlace(stack)
            && this.moveItemStackTo(stack, TEMPLATE_SLOT, TEMPLATE_SLOT + 1, false)) {
            return true;
        }
        return this.slots.get(MATERIAL_SLOT).mayPlace(stack)
            && this.moveItemStackTo(stack, MATERIAL_SLOT, MATERIAL_SLOT + 1, false);
    }

    /**
     * One display slot: takes exactly one item, and only one that equips in its armor slot. Typed
     * by the item's {@code equippable} component, as the inventory's own armor slots are, so modded
     * armor and vanilla armor are admitted by the same rule.
     */
    private static final class DisplaySlot extends Slot {
        private final EquipmentSlot equipmentSlot;
        private final Identifier icon;

        DisplaySlot(final Container container, final int index, final int x, final int y) {
            super(container, index, x, y);
            this.equipmentSlot = DISPLAY_SLOTS.get(index);
            this.icon = DISPLAY_SLOT_ICONS.get(index);
        }

        @Override
        public boolean mayPlace(final ItemStack stack) {
            return fitsSlot(stack, this.equipmentSlot);
        }

        @Override
        public int getMaxStackSize() {
            return 1;
        }

        @Override
        public @Nullable Identifier getNoItemIcon() {
            return this.icon;
        }
    }
}
