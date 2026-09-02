package com.mattjesmc.armorpieces.client.screen;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.decoration.fitting.FittingValue;
import com.mattjesmc.armorpieces.menu.AdvancedSmithingMenu;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.registry.ModItems;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.components.AbstractButton;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.ImageButton;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.client.gui.components.WidgetSprites;
import net.minecraft.client.gui.narration.NarrationElementOutput;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.input.InputWithModifiers;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.client.renderer.entity.layers.HumanoidArmorLayer;
import net.minecraft.client.renderer.entity.state.ArmorStandRenderState;
import net.minecraft.core.Holder;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.EntityTypes;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import org.joml.Quaternionf;
import org.joml.Quaternionfc;
import org.joml.Vector3f;
import org.joml.Vector3fc;

/**
 * The advanced smithing table's screen: display slots and their select buttons down the left, the
 * selected piece's sockets in the middle, the stand on the right.
 *
 * <p>Every decision about what may happen lives in {@link AdvancedSmithingMenu}; this class draws
 * what the menu holds and turns clicks into the menu's button ids, sent as vanilla container-button
 * clicks the way the loom and stonecutter send theirs. The socket rows are not slots - a part in a
 * socket is not an item to be picked up - so they are drawn by hand: the socket's name, the socket
 * template carrying the part as its icon, and a cross that empties it.
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
    private static final Identifier SELECT_SPRITE = sprite("widget/select");
    private static final Identifier SELECT_HIGHLIGHTED_SPRITE = sprite("widget/select_highlighted");
    private static final Identifier SELECT_SELECTED_SPRITE = sprite("widget/select_selected");
    private static final WidgetSprites REMOVE_SPRITES = new WidgetSprites(
        Identifier.withDefaultNamespace("widget/cross_button"),
        Identifier.withDefaultNamespace("widget/cross_button_highlighted"));

    private static final int IMAGE_WIDTH = 200;
    private static final int IMAGE_HEIGHT = 212;
    private static final int LABEL_COLOR = -12566464;
    private static final int HINT_COLOR = -8355712;

    // ---- layout, relative to the panel's top-left ----------------------------------------------
    private static final int SELECT_X = 27;
    private static final int SELECT_WIDTH = 12;
    private static final int ROW_X = 44;
    private static final int ROW_ICON_X = 96;
    private static final int ROW_REMOVE_X = 116;
    private static final int ROW_WIDTH = 84;
    private static final int APPLY_X = 84;
    private static final int APPLY_Y = 92;
    private static final int APPLY_WIDTH = 42;
    private static final int APPLY_HEIGHT = 18;
    private static final int STAND_LEFT = 132;
    private static final int STAND_TOP = 17;
    private static final int STAND_RIGHT = 192;
    private static final int STAND_BOTTOM = 111;

    // ---- the stand ----------------------------------------------------------------------------
    private static final float STAND_SCALE = 38.0F;
    private static final float STAND_DEFAULT_ROTATION = 210.0F;
    private static final Vector3fc STAND_TRANSLATION = new Vector3f(0.0F, 1.0F, 0.0F);
    private static final Quaternionfc STAND_ANGLE = new Quaternionf().rotationXYZ(0.43633232F, 0.0F, (float) Math.PI);
    private static final float DRAG_DEGREES_PER_PIXEL = 2.0F;

    private static final Component APPLY = Component.translatable("container.armorpieces.advanced_smithing.apply");
    private static final Component REMOVE = Component.translatable("container.armorpieces.advanced_smithing.remove");
    private static final Component SELECT = Component.translatable("container.armorpieces.advanced_smithing.select");
    private static final Component HINT = Component.translatable("container.armorpieces.advanced_smithing.hint");
    private static final Component EMPTY_SOCKET = Component.translatable("container.armorpieces.advanced_smithing.empty")
        .withStyle(ChatFormatting.GRAY);

    private final ArmorStandRenderState standPreview = new ArmorStandRenderState();
    private final List<SelectButton> selectButtons = new ArrayList<>();
    private final List<ImageButton> removeButtons = new ArrayList<>();
    private final List<DecorationAnchor> removeAnchors = new ArrayList<>();
    private Button applyButton;
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

    private static Identifier sprite(final String path) {
        return Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, path);
    }

    @Override
    protected void init() {
        super.init();
        this.selectButtons.clear();
        this.removeButtons.clear();
        this.removeAnchors.clear();
        for (int i = 0; i < AdvancedSmithingMenu.DISPLAY_SLOTS.size(); i++) {
            final SelectButton button = new SelectButton(
                i,
                this.leftPos + SELECT_X,
                this.topPos + AdvancedSmithingMenu.DISPLAY_Y - 1 + i * AdvancedSmithingMenu.ROW_HEIGHT);
            this.selectButtons.add(this.addRenderableWidget(button));
        }
        for (int i = 0; i < AdvancedSmithingMenu.DISPLAY_SLOTS.size(); i++) {
            final int row = i;
            final ImageButton button = new ImageButton(
                this.leftPos + ROW_REMOVE_X,
                this.rowY(row) + 2,
                14,
                14,
                REMOVE_SPRITES,
                b -> this.removeRow(row),
                REMOVE);
            button.setTooltip(Tooltip.create(REMOVE));
            button.visible = false;
            this.removeButtons.add(this.addRenderableWidget(button));
            this.removeAnchors.add(null);
        }
        this.applyButton = this.addRenderableWidget(Button.builder(APPLY, b -> this.apply())
            .bounds(this.leftPos + APPLY_X, this.topPos + APPLY_Y, APPLY_WIDTH, APPLY_HEIGHT)
            .build());
        this.menuChanged();
    }

    private int rowY(final int row) {
        return this.topPos + AdvancedSmithingMenu.DISPLAY_Y + row * AdvancedSmithingMenu.ROW_HEIGHT;
    }

    // ---- reacting to the menu -------------------------------------------------------------------

    /** Re-reads the menu: the stand's clothes, which rows exist and whether Apply is lit. */
    private void menuChanged() {
        if (this.minecraft == null || this.applyButton == null) {
            return;
        }
        this.updateStand();
        this.updateRows();
        this.applyButton.active = this.menu.canApply();
    }

    @Override
    protected void containerTick() {
        super.containerTick();
        // Data slots arrive without a slot change, so the parts of the screen that read them are
        // refreshed every tick rather than only on the listener.
        this.updateRows();
        this.applyButton.active = this.menu.canApply();
    }

    private void updateStand() {
        this.standPreview.headEquipment = ItemStack.EMPTY;
        this.standPreview.headItem.clear();
        this.standPreview.chestEquipment = ItemStack.EMPTY;
        this.standPreview.legsEquipment = ItemStack.EMPTY;
        this.standPreview.feetEquipment = ItemStack.EMPTY;
        for (int i = 0; i < AdvancedSmithingMenu.DISPLAY_SLOTS.size(); i++) {
            final ItemStack stack = this.menu.displayStack(i);
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

    private void updateRows() {
        final List<DecorationAnchor> anchors = this.menu.selectedAnchors();
        final ArmorDecorations decorations =
            this.menu.selectedStack().getOrDefault(ModDataComponents.DECORATIONS, ArmorDecorations.EMPTY);
        for (int row = 0; row < this.removeButtons.size(); row++) {
            final DecorationAnchor anchor = row < anchors.size() ? anchors.get(row) : null;
            final boolean filled = anchor != null && decorations.get(anchor) != null;
            this.removeAnchors.set(row, anchor);
            this.removeButtons.get(row).visible = filled;
        }
        for (int i = 0; i < this.selectButtons.size(); i++) {
            this.selectButtons.get(i).active = !this.menu.displayStack(i).isEmpty();
        }
    }

    // ---- sending clicks -------------------------------------------------------------------------

    private void select(final int index) {
        if (this.menu.clickMenuButton(this.minecraft.player, AdvancedSmithingMenu.BUTTON_SELECT + index)) {
            this.minecraft.gameMode.handleInventoryButtonClick(this.menu.containerId, AdvancedSmithingMenu.BUTTON_SELECT + index);
            this.menuChanged();
        }
    }

    private void removeRow(final int row) {
        final DecorationAnchor anchor = this.removeAnchors.get(row);
        if (anchor == null) {
            return;
        }
        final int id = AdvancedSmithingMenu.BUTTON_REMOVE + anchor.ordinal();
        if (this.menu.clickMenuButton(this.minecraft.player, id)) {
            this.minecraft.gameMode.handleInventoryButtonClick(this.menu.containerId, id);
            this.menuChanged();
        }
    }

    private void apply() {
        // The client cannot run the recipe; clickMenuButton there answers with the server's last
        // verdict, so the click is only sent when it will land.
        if (this.menu.clickMenuButton(this.minecraft.player, AdvancedSmithingMenu.BUTTON_APPLY)) {
            this.minecraft.gameMode.handleInventoryButtonClick(this.menu.containerId, AdvancedSmithingMenu.BUTTON_APPLY);
        }
    }

    // ---- drawing --------------------------------------------------------------------------------

    @Override
    public void extractBackground(final GuiGraphicsExtractor graphics, final int mouseX, final int mouseY, final float a) {
        super.extractBackground(graphics, mouseX, mouseY, a);
        graphics.blit(RenderPipelines.GUI_TEXTURED, BACKGROUND, this.leftPos, this.topPos, 0.0F, 0.0F,
            this.imageWidth, this.imageHeight, 256, 256);
        this.extractRows(graphics);
        this.standPreview.bodyRot = this.standRotation;
        graphics.entity(this.standPreview, STAND_SCALE, STAND_TRANSLATION, STAND_ANGLE, null,
            this.leftPos + STAND_LEFT, this.topPos + STAND_TOP, this.leftPos + STAND_RIGHT, this.topPos + STAND_BOTTOM);
    }

    /** The socket list: a name, a framed icon and (as a widget) a cross per socket of the selected piece. */
    private void extractRows(final GuiGraphicsExtractor graphics) {
        final List<DecorationAnchor> anchors = this.menu.selectedAnchors();
        if (anchors.isEmpty()) {
            graphics.textWithWordWrap(this.font, HINT, this.leftPos + ROW_X, this.topPos + AdvancedSmithingMenu.DISPLAY_Y + 3,
                ROW_WIDTH, HINT_COLOR);
            return;
        }
        final ArmorDecorations decorations =
            this.menu.selectedStack().getOrDefault(ModDataComponents.DECORATIONS, ArmorDecorations.EMPTY);
        for (int row = 0; row < anchors.size(); row++) {
            final DecorationAnchor anchor = anchors.get(row);
            final int y = this.rowY(row);
            graphics.text(this.font, socketName(anchor), this.leftPos + ROW_X, y + 4, LABEL_COLOR, false);
            graphics.blitSprite(RenderPipelines.GUI_TEXTURED, SLOT_SPRITE, this.leftPos + ROW_ICON_X - 1, y - 1, 18, 18);
            final DecorationEntry entry = decorations.get(anchor);
            if (entry != null) {
                // The icon is the socket template carrying this part - the very item that put it
                // there, and the one the creative tab and the recipe book show for it.
                graphics.item(ModItems.templateFor(anchor, entry.decoration()), this.leftPos + ROW_ICON_X, y);
            }
        }
    }

    @Override
    public void extractRenderState(final GuiGraphicsExtractor graphics, final int mouseX, final int mouseY, final float a) {
        super.extractRenderState(graphics, mouseX, mouseY, a);
        this.extractRowTooltip(graphics, mouseX, mouseY);
    }

    /** The tooltip for a hovered socket icon: the part in its material, then what its fittings hold. */
    private void extractRowTooltip(final GuiGraphicsExtractor graphics, final int mouseX, final int mouseY) {
        if (!this.menu.getCarried().isEmpty()) {
            return;
        }
        final List<DecorationAnchor> anchors = this.menu.selectedAnchors();
        final ArmorDecorations decorations =
            this.menu.selectedStack().getOrDefault(ModDataComponents.DECORATIONS, ArmorDecorations.EMPTY);
        for (int row = 0; row < anchors.size(); row++) {
            final int y = AdvancedSmithingMenu.DISPLAY_Y + row * AdvancedSmithingMenu.ROW_HEIGHT;
            if (!this.isHovering(ROW_ICON_X, y, 16, 16, mouseX, mouseY)) {
                continue;
            }
            final DecorationEntry entry = decorations.get(anchors.get(row));
            final List<Component> lines = new ArrayList<>();
            if (entry == null) {
                lines.add(EMPTY_SOCKET);
            } else {
                lines.add(entry.decoration().value().copyWithStyle(entry.material()));
                for (final Holder<Fitting> fitting : entry.decoration().value().fittings()) {
                    final FittingValue value = entry.fitting(fitting);
                    if (value != null) {
                        lines.add(Component.translatable("item.armorpieces.fitting", fitting.value().description(), value.name())
                            .withStyle(ChatFormatting.GRAY));
                    }
                }
            }
            lines.add(Component.translatable("anchor.armorpieces." + anchors.get(row).getSerializedName() + ".applies_to")
                .withStyle(ChatFormatting.DARK_GRAY));
            graphics.setComponentTooltipForNextFrame(this.font, lines, mouseX, mouseY);
            return;
        }
    }

    private static Component socketName(final DecorationAnchor anchor) {
        return Component.translatable("anchor.armorpieces." + anchor.getSerializedName());
    }

    // ---- turning the stand ----------------------------------------------------------------------

    private boolean overStand(final double x, final double y) {
        return this.isHovering(STAND_LEFT, STAND_TOP, STAND_RIGHT - STAND_LEFT, STAND_BOTTOM - STAND_TOP, x, y);
    }

    @Override
    public boolean mouseClicked(final MouseButtonEvent event, final boolean doubleClick) {
        if (event.button() == 0 && this.menu.getCarried().isEmpty() && this.overStand(event.x(), event.y())) {
            this.draggingStand = true;
            return true;
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
     * The button beside a display slot. Three looks - plain, hovered, selected - chosen at draw time
     * from the menu's selection rather than from a flag of its own, so it can never disagree with
     * the list beside it.
     */
    private final class SelectButton extends AbstractButton {
        private final int index;

        SelectButton(final int index, final int x, final int y) {
            super(x, y, SELECT_WIDTH, AdvancedSmithingMenu.ROW_HEIGHT, SELECT);
            this.index = index;
            this.setTooltip(Tooltip.create(SELECT));
        }

        @Override
        public void onPress(final InputWithModifiers input) {
            AdvancedSmithingScreen.this.select(this.index);
        }

        @Override
        protected void extractContents(final GuiGraphicsExtractor graphics, final int mouseX, final int mouseY, final float a) {
            final Identifier sprite;
            if (AdvancedSmithingScreen.this.menu.selected() == this.index) {
                sprite = SELECT_SELECTED_SPRITE;
            } else if (this.isActive() && this.isHoveredOrFocused()) {
                sprite = SELECT_HIGHLIGHTED_SPRITE;
            } else {
                sprite = SELECT_SPRITE;
            }
            graphics.blitSprite(RenderPipelines.GUI_TEXTURED, sprite, this.getX(), this.getY(), this.width, this.height,
                this.isActive() ? 1.0F : 0.5F);
        }

        @Override
        protected void updateWidgetNarration(final NarrationElementOutput output) {
            this.defaultButtonNarrationText(output);
        }
    }
}
