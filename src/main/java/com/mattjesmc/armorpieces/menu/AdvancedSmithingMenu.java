package com.mattjesmc.armorpieces.menu;

import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.registry.ModBlocks;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.registry.ModMenus;
import java.util.List;
import java.util.Optional;
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
 *   <li><b>Taking a part off.</b> A socket's cross button empties that socket. The smithing table
 *       has no ingredient that means "nothing", so a filled socket there stays filled until another
 *       part replaces it; this is the one place a part comes off. Nothing is refunded - the template
 *       was spent putting it on, as a trim's template is.</li>
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

    /** Slot positions, shared with the screen so the background art and the slots agree. */
    public static final int DISPLAY_X = 8;
    public static final int DISPLAY_Y = 17;
    public static final int ROW_HEIGHT = 18;
    public static final int TEMPLATE_X = 44;
    public static final int MATERIAL_X = 62;
    public static final int INPUT_Y = 93;
    public static final int INVENTORY_Y = 130;

    // ---- button ids, sent as vanilla container-button clicks ------------------------------------
    /** {@code SELECT + i} selects display slot {@code i}. */
    public static final int BUTTON_SELECT = 0;
    public static final int BUTTON_APPLY = 4;
    /** {@code REMOVE + anchor.ordinal()} empties that socket on the selected piece. */
    public static final int BUTTON_REMOVE = 8;

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
        final int anchorIndex = buttonId - BUTTON_REMOVE;
        if (anchorIndex >= 0 && anchorIndex < DecorationAnchor.values().length) {
            return this.remove(DecorationAnchor.values()[anchorIndex]);
        }
        return false;
    }

    private boolean select(final int index) {
        if (this.display.getItem(index).isEmpty() || this.selected.get() == index) {
            return false;
        }
        this.selected.set(index);
        this.refresh();
        return true;
    }

    /**
     * Empties one socket of the selected piece. Both sides run this; it needs nothing the client
     * lacks, and the piece is a plain component edit - see {@link ArmorDecorations#without}.
     */
    private boolean remove(final DecorationAnchor anchor) {
        final int index = this.selected.get();
        final ItemStack piece = this.selectedStack();
        if (piece.isEmpty()) {
            return false;
        }
        final ArmorDecorations decorations = piece.get(ModDataComponents.DECORATIONS);
        if (decorations == null) {
            return false;
        }
        final Optional<ArmorDecorations> remaining = decorations.without(anchor);
        if (remaining.isEmpty()) {
            return false;
        }
        final ItemStack edited = piece.copy();
        if (remaining.get().isEmpty()) {
            // Down to nothing: drop the component rather than keep an empty map, so the piece is
            // byte-for-byte the undecorated item again and stacks with one.
            edited.remove(ModDataComponents.DECORATIONS);
        } else {
            edited.set(ModDataComponents.DECORATIONS, remaining.get());
        }
        this.display.setItem(index, edited);
        return true;
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
            .map(recipe -> recipe.value().assemble(input))
            .filter(result -> !result.isEmpty() && fitsSlot(result, DISPLAY_SLOTS.get(index)))
            .orElse(ItemStack.EMPTY);
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
        this.refresh();
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
        if (this.level instanceof ServerLevel) {
            final ItemStack result = this.findResult();
            if (!ItemStack.matches(result, this.preview.getItem(0))) {
                this.preview.setItem(0, result);
            }
        }
        this.updateListener.run();
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
