package com.mattjesmc.armorpieces.client.screen;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mattjesmc.armorpieces.decoration.MaterialIcons;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.decoration.fitting.FittingValue;
import com.mattjesmc.armorpieces.menu.AdvancedSmithingMenu;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.registry.ModItems;
import com.mattjesmc.armorpieces.skin.ArmorSkinValue;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.components.AbstractButton;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.client.gui.narration.NarrationElementOutput;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.input.InputWithModifiers;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.client.renderer.entity.layers.HumanoidArmorLayer;
import net.minecraft.client.renderer.entity.state.ArmorStandRenderState;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.TextColor;
import net.minecraft.util.ARGB;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.EntityTypes;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.equipment.trim.ArmorTrim;
import org.joml.Quaternionf;
import org.joml.Quaternionfc;
import org.joml.Vector3f;
import org.joml.Vector3fc;
import org.jspecify.annotations.Nullable;

/**
 * The advanced smithing table's screen: display slots and their select buttons down the left, the
 * selected piece's rows in the middle, the stand full height down the right.
 *
 * <p>Every decision about what may happen lives in {@link AdvancedSmithingMenu}; this class draws
 * what the menu holds and turns clicks into the menu's button ids, sent as vanilla container-button
 * clicks the way the loom and stonecutter send theirs.
 *
 * <p>The rows sit in a box that belongs to the piece being worked on: it is always the size of the
 * longest list a piece can have - the chestplate's four sockets and its trim - so it does not jump
 * as pieces are picked, and a neck runs out of its left edge into the armor slot holding that piece,
 * in the slot's own grey and at its own height, so the box reads as that slot opened up. The neck
 * moves with the selection, so the box is drawn here rather than baked into the sheet.
 *
 * <p>A row is one socket of the selected piece, or - last, under them - the piece's own row: its
 * trim, and beside it its skin. The rows are not
 * slots (a part in a socket is not an item to be picked up) so they are drawn by hand: the part as
 * the socket template that carries it, then one place per fitting the part declares, empty or
 * filled. The columns are fixed, so the parts line up down the box. Every
 * filled icon wears a half-size second icon in its corner naming what it is made of - the ingot
 * behind a gold pauldron, the emerald in its stone - which is the one thing a template icon alone
 * never said. The socket a row means is in its tooltip, not written beside it: the icons say it
 * better than a column of words would.
 *
 * <p>An empty place is not drawn as an empty slot. A grid of frames only said that the rows have
 * columns, which the columns already said; what it never said was what could go in one. So the frame
 * is spent on the one thing being worked on - it is the selection, in place of a border drawn over
 * it - and an empty place instead shows a hint of the template that would fill it, the way the
 * vanilla smithing table shows a faint template in its own empty template slot. The hint is that
 * template's own icon with its card taken off and its armor knocked out of it, leaving the socket's
 * amber in a grey ground; it is generated from the icon, see {@code tools/gen_template_icons.py}.
 *
 * <p>Clicking an icon works on it, and that is what Apply and Remove then act on: a fitting goes
 * into the selected socket rather than into every part that takes one, and Remove empties the
 * selected socket, fitting or trim. Clicking the part works on the row as a whole, which is what a
 * button beside every row used to be for; the row's own ground lights the width of the box instead,
 * which says the same thing and gives the icons back the column that button stood in. Selection
 * lives in the menu, not here, so the two sides never disagree about what is being worked on. The
 * template slot under the stand wears the hint of whatever is picked while it stands empty, so the
 * question the picking raises - what do I put in - is answered in the slot the answer goes into.
 *
 * <p>The stand is a render state rather than an entity, as the smithing table's preview is, and it
 * is drawn by the same renderer and layers that draw a stand in the world, so parts and fittings
 * appear exactly as they will be worn. Dragging across it turns it, which the smithing table's
 * fixed angle never allowed and which the back socket needs.
 */
@Environment(EnvType.CLIENT)
public class AdvancedSmithingScreen extends AbstractContainerScreen<AdvancedSmithingMenu> {
    private static final Identifier BACKGROUND =
        Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "textures/gui/container/advanced_smithing.png");
    private static final Identifier SLOT_SPRITE = Identifier.withDefaultNamespace("container/slot");
    /** Where the hints live, ours beside vanilla's own. */
    private static final String SLOT_HINTS = "container/slot/";
    /** The trim row borrows the smithing table's hint: it is the same template, asked for twice. */
    private static final Identifier TRIM_HINT =
        Identifier.withDefaultNamespace(SLOT_HINTS + "smithing_template_armor_trim");
    /** The skin's place, beside the trim: the skin template's own icon, knocked out. */
    private static final Identifier SKIN_HINT =
        Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, SLOT_HINTS + "skin_template");
    /**
     * The fittings with a hint of their own, mirroring the cases in {@code items/fitting_template.json}:
     * a pack's own fitting is asked for with the plain card there and with the plain hint here.
     */
    private static final Set<String> FITTING_HINTS = Set.of("gemstone", "guard", "inlay", "banner");
    /**
     * The mark that picks something: the arrow the realms list uses for the same word - "select" -
     * and nothing behind it. A plate under it, vanilla's or ours, always ends a pixel from the frame
     * of whatever it stands beside and reads as a misfit; the arrow alone sits in the gap and points
     * at what it opens.
     *
     * <p>The sprite is authored at double size, so it is drawn at half scale to get its 7 by 11
     * arrow back at one pixel to one pixel. Hovered has a variant of its own, and unavailable is
     * the plain one at half alpha.
     */
    private static final Identifier SELECT_SPRITE =
        Identifier.withDefaultNamespace("transferable_list/select");
    private static final Identifier SELECT_HIGHLIGHTED_SPRITE =
        Identifier.withDefaultNamespace("transferable_list/select_highlighted");
    private static final int ARROW_SHEET = 32;
    private static final int ARROW_U = 10;
    private static final int ARROW_V = 5;
    private static final int ARROW_WIDTH = 14;
    private static final int ARROW_HEIGHT = 22;
    private static final int ARROW_X = 2;
    private static final int ARROW_Y = 3;

    private static final int IMAGE_WIDTH = 242;
    private static final int IMAGE_HEIGHT = 220;
    private static final int HINT_COLOR = 0xFF808080;
    /** The vanilla container palette, for the one panel that is drawn rather than baked. */
    private static final int SUNKEN_COLOR = 0xFF373737;
    private static final int RAISED_COLOR = 0xFFFFFFFF;
    /** The box's ground: a slot's own grey, since the box is the piece's slot carried inwards. */
    private static final int BOX_COLOR = 0xFF8B8B8B;
    /** A picked row's ground, a step above the box's, showing around the slots that stand on it. */
    private static final int ROW_SELECTED_COLOR = 0xFFD4D4D4;
    private static final int PIP_BORDER_COLOR = 0xFF000000;

    // ---- layout, relative to the panel's top-left ----------------------------------------------
    /** Centred in the gap between the armor slot and the box, which is what the arrow spans. */
    private static final int SELECT_X = 33;
    private static final int SELECT_WIDTH = 11;
    private static final int SELECT_HEIGHT = 18;
    private static final int ICON_PITCH = 18;
    private static final int ICON_SIZE = 16;
    private static final int BADGE_SIZE = 8;
    /** Wider than a slot, so a picked row's ground shows between the slots as well as around them. */
    private static final int COLUMN_PITCH = 20;

    /**
     * The box the rows live in, and the tab that reaches back under the piece button. The gap
     * between the two is what the tab crosses, so it is wide enough for the crossing to be seen.
     */
    private static final int BOX_LEFT = 52;
    private static final int BOX_RIGHT = 167;
    private static final int BOX_TOP = 15;
    private static final int BOX_BOTTOM = 120;
    /** Column 0 of a row is its part, or its trim; the rest are that part's fittings. */
    private static final int COLUMN_X = 60;

    private static final int BUTTON_HEIGHT = 18;
    private static final int APPLY_Y = 175;
    private static final int REMOVE_Y = 195;
    private static final int STAND_LEFT = 173;
    private static final int STAND_TOP = 16;
    private static final int STAND_RIGHT = 235;
    private static final int STAND_BOTTOM = 147;
    private static final int COLUMN_WIDTH = STAND_RIGHT - STAND_LEFT;

    // ---- the stand ----------------------------------------------------------------------------
    private static final float STAND_SCALE = 48.0F;
    private static final float STAND_DEFAULT_ROTATION = 210.0F;
    private static final Vector3fc STAND_TRANSLATION = new Vector3f(0.0F, 1.0F, 0.0F);
    private static final Quaternionfc STAND_ANGLE = new Quaternionf().rotationXYZ(0.43633232F, 0.0F, (float) Math.PI);
    private static final float DRAG_DEGREES_PER_PIXEL = 2.0F;

    private static final Component APPLY = Component.translatable("container.armorpieces.advanced_smithing.apply");
    private static final Component REMOVE = Component.translatable("container.armorpieces.advanced_smithing.remove");
    private static final Component REMOVE_HINT =
        Component.translatable("container.armorpieces.advanced_smithing.remove.hint");
    private static final Component SELECT = Component.translatable("container.armorpieces.advanced_smithing.select");
    private static final Component HINT = Component.translatable("container.armorpieces.advanced_smithing.hint");
    private static final Component TRIM = Component.translatable("container.armorpieces.advanced_smithing.trim");
    private static final Component SKIN = Component.translatable("container.armorpieces.advanced_smithing.skin");
    private static final Component EMPTY_SOCKET = Component.translatable("container.armorpieces.advanced_smithing.empty")
        .withStyle(ChatFormatting.GRAY);

    private final ArmorStandRenderState standPreview = new ArmorStandRenderState();
    private final List<SelectButton> pieceButtons = new ArrayList<>();
    private Button applyButton;
    private Button removeButton;
    private float standRotation = STAND_DEFAULT_ROTATION;
    private boolean draggingStand;

    public AdvancedSmithingScreen(final AdvancedSmithingMenu menu, final Inventory inventory, final Component title) {
        super(menu, inventory, title, IMAGE_WIDTH, IMAGE_HEIGHT);
        this.standPreview.entityType = EntityTypes.ARMOR_STAND;
        this.standPreview.showBasePlate = false;
        this.standPreview.showArms = true;
        this.standPreview.xRot = 25.0F;
        this.standPreview.bodyRot = this.standRotation;
        menu.registerUpdateListener(this::menuChanged);
    }

    @Override
    protected void init() {
        super.init();
        this.pieceButtons.clear();
        for (int i = 0; i < AdvancedSmithingMenu.DISPLAY_SLOTS.size(); i++) {
            final int index = i;
            this.pieceButtons.add(this.addRenderableWidget(new SelectButton(
                this.leftPos + SELECT_X, this.bandY(i), SELECT, () -> this.select(index))));
        }
        this.applyButton = this.addRenderableWidget(Button.builder(APPLY, b -> this.apply())
            .bounds(this.leftPos + STAND_LEFT, this.topPos + APPLY_Y, COLUMN_WIDTH, BUTTON_HEIGHT)
            .build());
        this.removeButton = this.addRenderableWidget(Button.builder(REMOVE, b -> this.remove())
            .bounds(this.leftPos + STAND_LEFT, this.topPos + REMOVE_Y, COLUMN_WIDTH, BUTTON_HEIGHT)
            .tooltip(Tooltip.create(REMOVE_HINT))
            .build());
        this.menuChanged();
    }

    /** The top of row {@code row}'s 16-pixel content, in screen coordinates. */
    private int rowY(final int row) {
        return this.topPos + AdvancedSmithingMenu.DISPLAY_Y + row * AdvancedSmithingMenu.ROW_HEIGHT;
    }

    /** The top of row {@code row}'s full 18-pixel band - its frame, its button - in screen coordinates. */
    private int bandY(final int row) {
        return this.rowY(row) - 1;
    }

    /**
     * The left edge of column {@code column} of a row, relative to the panel. Column 0 is the part
     * or the trim and the rest are its fittings - the same numbering the places are counted in
     * everywhere else here, so a row is drawn and hit in one order.
     */
    private static int columnX(final int column) {
        return COLUMN_X + column * COLUMN_PITCH;
    }

    // ---- reacting to the menu -------------------------------------------------------------------

    /** Re-reads the menu: the stand's clothes, which rows exist and whether the buttons are lit. */
    private void menuChanged() {
        if (this.minecraft == null || this.applyButton == null) {
            return;
        }
        this.updateStand();
        this.updateWidgets();
    }

    @Override
    protected void containerTick() {
        super.containerTick();
        // Data slots arrive without a slot change, so the parts of the screen that read them are
        // refreshed every tick rather than only on the listener.
        this.updateWidgets();
    }

    private void updateStand() {
        this.standPreview.headEquipment = ItemStack.EMPTY;
        this.standPreview.headItem.clear();
        this.standPreview.chestEquipment = ItemStack.EMPTY;
        this.standPreview.legsEquipment = ItemStack.EMPTY;
        this.standPreview.feetEquipment = ItemStack.EMPTY;
        final ItemStack preview = this.menu.previewStack();
        for (int i = 0; i < AdvancedSmithingMenu.DISPLAY_SLOTS.size(); i++) {
            // The selected piece is shown as Apply would leave it while the two slots hold a
            // matching recipe, so the part, the stone or the trim is judged before it is paid for.
            final ItemStack stack = i == this.menu.selected() && !preview.isEmpty()
                ? preview
                : this.menu.displayStack(i);
            if (stack.isEmpty()) {
                continue;
            }
            switch (AdvancedSmithingMenu.DISPLAY_SLOTS.get(i)) {
                case HEAD -> {
                    // A carved pumpkin or a skull is a block on the head, not armor over it; the
                    // smithing table's preview makes the same split.
                    if (HumanoidArmorLayer.shouldRender(stack, EquipmentSlot.HEAD)) {
                        this.standPreview.headEquipment = stack.copy();
                    } else {
                        this.minecraft.getItemModelResolver()
                            .updateForTopItem(this.standPreview.headItem, stack, ItemDisplayContext.HEAD, null, null, 0);
                    }
                }
                case CHEST -> this.standPreview.chestEquipment = stack.copy();
                case LEGS -> this.standPreview.legsEquipment = stack.copy();
                case FEET -> this.standPreview.feetEquipment = stack.copy();
                default -> { }
            }
        }
    }

    private void updateWidgets() {
        for (int i = 0; i < this.pieceButtons.size(); i++) {
            final SelectButton button = this.pieceButtons.get(i);
            button.active = !this.menu.displayStack(i).isEmpty();
            // The picked piece has left the column and stands in its arrow's place, so the arrow
            // would only be pointing at where that piece used to be.
            button.visible = this.menu.selected() != i;
        }
        this.applyButton.active = this.menu.canApply();
        // Always there, beside Apply, and dark until something is picked that it could take off -
        // a button that appears and disappears is a button the eye has to find twice.
        this.removeButton.active = this.menu.canRemove();
    }

    // ---- sending clicks -------------------------------------------------------------------------

    private void send(final int buttonId) {
        if (this.menu.clickMenuButton(this.minecraft.player, buttonId)) {
            this.minecraft.gameMode.handleInventoryButtonClick(this.menu.containerId, buttonId);
            this.menuChanged();
        }
    }

    private void select(final int index) {
        this.send(AdvancedSmithingMenu.BUTTON_SELECT + index);
    }

    /** Works on one row of the selected piece, or on one fitting slot of it. */
    private void selectRow(final int row, final int fitting) {
        this.send(fitting < 0
            ? AdvancedSmithingMenu.BUTTON_SELECT_ROW + row
            : AdvancedSmithingMenu.BUTTON_SELECT_FITTING + row * AdvancedSmithingMenu.MAX_FITTINGS + fitting);
    }

    private void remove() {
        this.send(AdvancedSmithingMenu.BUTTON_REMOVE);
    }

    private void apply() {
        // The client cannot run the recipe; clickMenuButton there answers with the server's last
        // verdict, so the click is only sent when it will land.
        this.send(AdvancedSmithingMenu.BUTTON_APPLY);
    }

    // ---- drawing --------------------------------------------------------------------------------

    @Override
    public void extractBackground(final GuiGraphicsExtractor graphics, final int mouseX, final int mouseY, final float a) {
        super.extractBackground(graphics, mouseX, mouseY, a);
        graphics.blit(RenderPipelines.GUI_TEXTURED, BACKGROUND, this.leftPos, this.topPos, 0.0F, 0.0F,
            this.imageWidth, this.imageHeight, 256, 256);
        this.extractDisplaySlots(graphics);
        this.extractTemplateHint(graphics);
        this.extractBox(graphics);
        this.extractRows(graphics);
        this.standPreview.bodyRot = this.standRotation;
        graphics.entity(this.standPreview, STAND_SCALE, STAND_TRANSLATION, STAND_ANGLE, null,
            this.leftPos + STAND_LEFT, this.topPos + STAND_TOP, this.leftPos + STAND_RIGHT, this.topPos + STAND_BOTTOM);
    }

    /**
     * The four armor slots' frames. They are not baked into the sheet, because the piece being
     * worked on does not stay in the column - it stands out beside the box - and a well left behind
     * on the art would be a hole where that piece used to be. The menu is asked where each slot is
     * rather than told, so a frame can never end up somewhere its slot is not.
     */
    private void extractDisplaySlots(final GuiGraphicsExtractor graphics) {
        for (int i = 0; i < AdvancedSmithingMenu.DISPLAY_SLOTS.size(); i++) {
            final Slot slot = this.menu.getSlot(AdvancedSmithingMenu.DISPLAY_SLOT_START + i);
            graphics.blitSprite(RenderPipelines.GUI_TEXTURED, SLOT_SPRITE,
                this.leftPos + slot.x - 1, this.topPos + slot.y - 1, ICON_PITCH, ICON_PITCH);
        }
    }

    /**
     * The empty template slot wearing the hint of the place being worked on: pick a socket and the
     * slot shows the socket's template, pick a fitting and it shows that fitting's, so the thing to
     * go looking for is named in the slot it has to be dropped into. It goes under the slot's
     * contents, which is where a hint belongs: the moment a template is put in, the template is
     * what is seen.
     */
    private void extractTemplateHint(final GuiGraphicsExtractor graphics) {
        final Identifier hint = this.selectedHint();
        if (hint == null || !this.menu.getSlot(AdvancedSmithingMenu.TEMPLATE_SLOT).getItem().isEmpty()) {
            return;
        }
        graphics.blitSprite(RenderPipelines.GUI_TEXTURED, hint,
            this.leftPos + AdvancedSmithingMenu.TEMPLATE_X, this.topPos + AdvancedSmithingMenu.INPUT_Y,
            ICON_SIZE, ICON_SIZE);
    }

    /**
     * The hint of the place being worked on - the same one that place is drawn with while it is
     * empty - or null while nothing is picked.
     */
    private @Nullable Identifier selectedHint() {
        final int row = this.menu.selectedRow();
        if (row < 0 || row >= this.menu.rowCount()) {
            return null;
        }
        final int fitting = this.menu.selectedFitting();
        if (this.menu.isTrimRow(row)) {
            return fitting < 0 ? TRIM_HINT : SKIN_HINT;
        }
        if (fitting < 0) {
            return socketHint(this.menu.anchorAt(row));
        }
        final List<Holder<Fitting>> fittings = this.menu.fittingsAt(row);
        return fitting < fittings.size() ? fittingHint(fittings.get(fitting)) : null;
    }

    /**
     * The box the rows sit in, and the neck that joins it to the piece it belongs to.
     *
     * <p>The box is a slot: a slot's grey, sunken on its top and left and raised on its bottom and
     * right, the way every recessed area in a vanilla container is. Which slot it is, is the point -
     * the neck runs from the right edge of the armor slot being worked on, at exactly that slot's
     * height and continuing its own two frame lines, so the two read as one shape and the box is
     * plainly that piece's insides. The button that picked the piece stands on the neck, drawn over
     * it a moment later.
     *
     * <p>The box's size never changes, so it does not jump as pieces are picked; only the neck
     * moves, down to whichever slot is being worked on.
     */
    private void extractBox(final GuiGraphicsExtractor graphics) {
        final int left = this.leftPos + BOX_LEFT;
        final int right = this.leftPos + BOX_RIGHT;
        final int top = this.topPos + BOX_TOP;
        final int bottom = this.topPos + BOX_BOTTOM;
        graphics.fill(left + 1, top + 1, right, bottom, BOX_COLOR);

        final int piece = this.menu.selected();
        // The armor slot's own frame rows, so the neck picks its two lines up where the slot ends.
        final int tabTop = piece < 0 ? 0 : this.rowY(piece) - 1;
        final int tabBottom = tabTop + ICON_PITCH - 1;
        if (piece >= 0) {
            // From the slot's raised right edge, over it, so nothing is left standing between them.
            final int tabLeft = this.leftPos + AdvancedSmithingMenu.DISPLAY_SELECTED_X + ICON_SIZE;
            graphics.fill(tabLeft, tabTop + 1, left + 1, tabBottom, BOX_COLOR);
            graphics.fill(tabLeft, tabTop, left + 1, tabTop + 1, SUNKEN_COLOR);
            graphics.fill(tabLeft, tabBottom, left + 1, tabBottom + 1, RAISED_COLOR);
        }

        graphics.fill(left, top, right + 1, top + 1, SUNKEN_COLOR);
        if (piece < 0) {
            graphics.fill(left, top, left + 1, bottom + 1, SUNKEN_COLOR);
        } else {
            // The left edge opens where the neck leaves it, so the two read as one shape.
            graphics.fill(left, top, left + 1, tabTop, SUNKEN_COLOR);
            graphics.fill(left, tabBottom + 1, left + 1, bottom + 1, SUNKEN_COLOR);
        }
        graphics.fill(left, bottom, right + 1, bottom + 1, RAISED_COLOR);
        graphics.fill(right, top, right + 1, bottom + 1, RAISED_COLOR);
    }

    /** One line per socket of the selected piece, then its trim: a band of icons, and its button. */
    private void extractRows(final GuiGraphicsExtractor graphics) {
        final int rows = this.menu.rowCount();
        if (rows == 0) {
            graphics.textWithWordWrap(this.font, HINT, this.leftPos + columnX(0),
                this.topPos + AdvancedSmithingMenu.DISPLAY_Y + 3, BOX_RIGHT - 5 - columnX(0), HINT_COLOR);
            return;
        }
        for (int row = 0; row < rows; row++) {
            final int y = this.rowY(row);
            final boolean trim = this.menu.isTrimRow(row);
            final List<Holder<Fitting>> fittings = this.menu.fittingsAt(row);
            // The row's ground, under everything that stands on it and running the full width of
            // the box. With no button beside the rows, this band is what says which row is being
            // worked on, and a band that stopped after the last icon would say it at a different
            // width in every row.
            if (this.menu.selectedRow() == row) {
                graphics.fill(this.leftPos + BOX_LEFT + 1, y - 2,
                    this.leftPos + BOX_RIGHT, y + ICON_SIZE + 2, ROW_SELECTED_COLOR);
            }
            // Which place of this row is being worked on, as a column index - 0 the part or the
            // trim, the rest its fittings - or -1 when the row is not the selected one. It is the
            // frame that says so, so each place is told whether it is the one.
            final int picked = this.menu.selectedRow() == row ? this.menu.selectedFitting() + 1 : -1;
            final DecorationEntry entry = this.menu.entryAt(row);
            final int part = this.leftPos + columnX(0);
            if (trim) {
                this.extractTrimSlot(graphics, part, y, picked == 0);
                this.extractSkinSlot(graphics, this.leftPos + columnX(1), y, picked == 1);
            } else {
                // The icon is the socket template carrying this part - the very item that put it
                // there, and the one the creative tab and the recipe book show for it.
                this.extractSlot(graphics, part, y, socketHint(this.menu.anchorAt(row)), picked == 0,
                    entry == null ? ItemStack.EMPTY : ModItems.templateFor(this.menu.anchorAt(row), entry.decoration()),
                    entry == null ? ItemStack.EMPTY : MaterialIcons.forTrimMaterial(entry.material()),
                    entry == null ? 0 : colourOf(entry.material().value().description()));
            }
            for (int slot = 0; slot < fittings.size(); slot++) {
                final Holder<Fitting> fitting = fittings.get(slot);
                final FittingValue value = entry == null ? null : entry.fitting(fitting);
                this.extractSlot(graphics, this.leftPos + columnX(slot + 1), y,
                    fittingHint(fitting), picked == slot + 1,
                    value == null ? ItemStack.EMPTY : ModItems.fittingTemplateFor(fitting),
                    value == null ? ItemStack.EMPTY : value.icon(),
                    value == null ? 0 : colourOf(value.name()));
            }
        }
    }

    /** The hint for an empty socket: the template that fills it, one per anchor. */
    private static Identifier socketHint(final DecorationAnchor anchor) {
        return Identifier.fromNamespaceAndPath(
            ArmorPieces.MOD_ID, SLOT_HINTS + anchor.getSerializedName() + "_template");
    }

    /** The hint for an empty fitting place, chosen as the fitting template's own model chooses. */
    private static Identifier fittingHint(final Holder<Fitting> fitting) {
        final String name = fitting.unwrapKey()
            .map(key -> key.identifier())
            .filter(id -> ArmorPieces.MOD_ID.equals(id.getNamespace()) && FITTING_HINTS.contains(id.getPath()))
            .map(id -> "fitting_template_" + id.getPath())
            .orElse("fitting_template");
        return Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, SLOT_HINTS + name);
    }

    /** The trim's place: the piece as it would be with no parts on it, so only the trim shows. */
    private void extractTrimSlot(
        final GuiGraphicsExtractor graphics,
        final int x,
        final int y,
        final boolean selected
    ) {
        final ItemStack piece = this.menu.selectedStack();
        final ArmorTrim trim = piece.get(DataComponents.TRIM);
        if (trim == null) {
            this.extractSlot(graphics, x, y, TRIM_HINT, selected, ItemStack.EMPTY, ItemStack.EMPTY, 0);
            return;
        }
        final ItemStack bare = piece.copy();
        bare.remove(ModDataComponents.DECORATIONS);
        this.extractSlot(graphics, x, y, TRIM_HINT, selected, bare,
            MaterialIcons.forTrimMaterial(trim.material()),
            colourOf(trim.material().value().description()));
    }

    /**
     * The skin's place, beside the trim on the same row: the template that would put this skin on,
     * which is the very item the creative tab and the recipe book show for it.
     *
     * <p>No badge under it, unlike every other place here. A skin has no second material to show -
     * its colour comes out of the armor it is on - and the piece standing on the right is already
     * wearing the answer.
     */
    private void extractSkinSlot(
        final GuiGraphicsExtractor graphics,
        final int x,
        final int y,
        final boolean selected
    ) {
        final ArmorSkinValue skin = this.menu.selectedSkin();
        this.extractSlot(graphics, x, y, SKIN_HINT, selected,
            skin == null ? ItemStack.EMPTY : ModItems.skinTemplateFor(skin.skin()),
            ItemStack.EMPTY, 0);
    }

    /**
     * One place of a row: what is in it, and - a half-size icon in the corner - what that is made
     * of. The badge falls back to a chip of the material's own colour for a material nothing in the
     * game provides, which is the only way a datapack's material can arrive.
     *
     * <p>The frame is drawn only around the place being worked on, so it marks the target of Apply
     * and Remove; an empty place shows {@code hint}, the template it wants worn faintly, and a place
     * that is neither stands on the box's own grey with nothing around it.
     */
    private void extractSlot(
        final GuiGraphicsExtractor graphics,
        final int x,
        final int y,
        final Identifier hint,
        final boolean selected,
        final ItemStack icon,
        final ItemStack badge,
        final int badgeColour
    ) {
        if (selected) {
            graphics.blitSprite(RenderPipelines.GUI_TEXTURED, SLOT_SPRITE, x, y - 1, ICON_PITCH, ICON_PITCH);
        }
        if (icon.isEmpty()) {
            graphics.blitSprite(RenderPipelines.GUI_TEXTURED, hint, x + 1, y, ICON_SIZE, ICON_SIZE);
            return;
        }
        graphics.item(icon, x + 1, y);
        final int badgeX = x + 1 + ICON_SIZE - BADGE_SIZE;
        final int badgeY = y + ICON_SIZE - BADGE_SIZE;
        if (!badge.isEmpty()) {
            graphics.pose().pushMatrix();
            graphics.pose().translate((float) badgeX, (float) badgeY);
            graphics.pose().scale(0.5F, 0.5F);
            graphics.item(badge, 0, 0);
            graphics.pose().popMatrix();
        } else if (badgeColour != 0) {
            graphics.fill(badgeX, badgeY, badgeX + BADGE_SIZE, badgeY + BADGE_SIZE, PIP_BORDER_COLOR);
            graphics.fill(badgeX + 1, badgeY + 1, badgeX + BADGE_SIZE - 1, badgeY + BADGE_SIZE - 1, badgeColour);
        }
    }

    private static int colourOf(final Component text) {
        final TextColor colour = text.getStyle().getColor();
        return colour == null ? 0 : 0xFF000000 | colour.getValue();
    }

    @Override
    public void extractRenderState(final GuiGraphicsExtractor graphics, final int mouseX, final int mouseY, final float a) {
        super.extractRenderState(graphics, mouseX, mouseY, a);
        this.extractRowTooltip(graphics, mouseX, mouseY);
    }

    /** The tooltip for a hovered icon: what is in it, and what that slot is for. */
    private void extractRowTooltip(final GuiGraphicsExtractor graphics, final int mouseX, final int mouseY) {
        if (!this.menu.getCarried().isEmpty()) {
            return;
        }
        final Icon hit = this.iconAt(mouseX, mouseY);
        if (hit == null) {
            return;
        }
        final int row = hit.row();
        final int slot = hit.slot();
        final DecorationEntry entry = this.menu.entryAt(row);
        final List<Component> lines = new ArrayList<>();
        if (slot > 0 && this.menu.isSkinPlace(row, slot - 1)) {
            final ArmorSkinValue skin = this.menu.selectedSkin();
            lines.add(skin == null ? EMPTY_SOCKET : skin.description());
            lines.add(SKIN.copy().withStyle(ChatFormatting.DARK_GRAY));
        } else if (slot > 0) {
            final Holder<Fitting> fitting = this.menu.fittingsAt(row).get(slot - 1);
            final FittingValue value = entry == null ? null : entry.fitting(fitting);
            if (value == null) {
                lines.add(fitting.value().description());
                lines.add(EMPTY_SOCKET);
            } else {
                lines.add(Component.translatable(
                    "item.armorpieces.fitting", fitting.value().description(), value.name()));
            }
            lines.add(fitting.value().ingredients().copy().withStyle(ChatFormatting.DARK_GRAY));
        } else if (this.menu.isTrimRow(row)) {
            final ArmorTrim trim = this.menu.selectedStack().get(DataComponents.TRIM);
            lines.add(trim == null ? EMPTY_SOCKET : trim.pattern().value().copyWithStyle(trim.material()));
            lines.add(TRIM.copy().withStyle(ChatFormatting.DARK_GRAY));
        } else {
            final DecorationAnchor anchor = this.menu.anchorAt(row);
            if (entry == null) {
                lines.add(socketName(anchor));
                lines.add(EMPTY_SOCKET);
            } else {
                lines.add(entry.decoration().value().copyWithStyle(entry.material()));
            }
            lines.add(Component.translatable("anchor.armorpieces." + anchor.getSerializedName() + ".applies_to")
                .withStyle(ChatFormatting.DARK_GRAY));
        }
        graphics.setComponentTooltipForNextFrame(this.font, lines, mouseX, mouseY);
    }

    private static Component socketName(final DecorationAnchor anchor) {
        return Component.translatable("anchor.armorpieces." + anchor.getSerializedName());
    }

    // ---- clicking the rows and turning the stand -------------------------------------------------

    /**
     * The row and icon under the cursor as {@code {row, slot}} - slot 0 being the part or the trim
     * and the rest its fittings - or null. The strips are laid out from the menu's own row and
     * fitting lists, so this asks the same questions the drawing did.
     */
    private @Nullable Icon iconAt(final double mouseX, final double mouseY) {
        for (int row = 0; row < this.menu.rowCount(); row++) {
            final int slots = 1 + this.menu.placesAt(row);
            final int y = AdvancedSmithingMenu.DISPLAY_Y + row * AdvancedSmithingMenu.ROW_HEIGHT;
            for (int slot = 0; slot < slots; slot++) {
                if (this.isHovering(columnX(slot) + 1, y, ICON_SIZE, ICON_SIZE, mouseX, mouseY)) {
                    return new Icon(row, slot);
                }
            }
        }
        return null;
    }

    /** One icon of one row: {@code slot} 0 is the part or the trim, the rest are its fittings. */
    private record Icon(int row, int slot) {}

    private boolean overStand(final double x, final double y) {
        return this.isHovering(STAND_LEFT, STAND_TOP, STAND_RIGHT - STAND_LEFT, STAND_BOTTOM - STAND_TOP, x, y);
    }

    @Override
    public boolean mouseClicked(final MouseButtonEvent event, final boolean doubleClick) {
        if (event.button() == 0 && this.menu.getCarried().isEmpty()) {
            final Icon hit = this.iconAt(event.x(), event.y());
            if (hit != null) {
                this.selectRow(hit.row(), hit.slot() - 1);
                return true;
            }
            if (this.overStand(event.x(), event.y())) {
                this.draggingStand = true;
                return true;
            }
        }
        return super.mouseClicked(event, doubleClick);
    }

    @Override
    public boolean mouseDragged(final MouseButtonEvent event, final double dx, final double dy) {
        if (this.draggingStand) {
            this.standRotation = (this.standRotation + (float) dx * DRAG_DEGREES_PER_PIXEL) % 360.0F;
            return true;
        }
        return super.mouseDragged(event, dx, dy);
    }

    @Override
    public boolean mouseReleased(final MouseButtonEvent event) {
        if (this.draggingStand) {
            this.draggingStand = false;
            return true;
        }
        return super.mouseReleased(event);
    }

    /**
     * A button that picks a piece out of the column. An arrow and nothing else, in two looks -
     * plain and hovered - and gone once its piece is picked, since the piece then stands where the
     * arrow was. Its bounds are wider than the arrow, so it is easier to hit than to see.
     */
    private final class SelectButton extends AbstractButton {
        private final Runnable onPress;

        SelectButton(final int x, final int y, final Component name, final Runnable onPress) {
            super(x, y, SELECT_WIDTH, SELECT_HEIGHT, name);
            this.onPress = onPress;
            this.setTooltip(Tooltip.create(name));
        }

        @Override
        public void onPress(final InputWithModifiers input) {
            this.onPress.run();
        }

        @Override
        protected void extractContents(final GuiGraphicsExtractor graphics, final int mouseX, final int mouseY, final float a) {
            final boolean hovered = this.isActive() && this.isHoveredOrFocused();
            final Identifier sprite = hovered ? SELECT_HIGHLIGHTED_SPRITE : SELECT_SPRITE;
            final int colour = ARGB.white(this.isActive() ? 1.0F : 0.5F);
            graphics.pose().pushMatrix();
            graphics.pose().translate((float) (this.getX() + ARROW_X), (float) (this.getY() + ARROW_Y));
            graphics.pose().scale(0.5F, 0.5F);
            graphics.blitSprite(RenderPipelines.GUI_TEXTURED, sprite, ARROW_SHEET, ARROW_SHEET,
                ARROW_U, ARROW_V, 0, 0, ARROW_WIDTH, ARROW_HEIGHT, colour);
            graphics.pose().popMatrix();
        }

        @Override
        protected void updateWidgetNarration(final NarrationElementOutput output) {
            this.defaultButtonNarrationText(output);
        }
    }
}
