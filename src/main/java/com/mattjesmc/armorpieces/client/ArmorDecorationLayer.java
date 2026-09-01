package com.mattjesmc.armorpieces.client;

import com.mattjesmc.armorpieces.client.geometry.DecorationGeometryManager;
import com.mattjesmc.armorpieces.client.texture.DecorationTextureManager;
import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mojang.blaze3d.vertex.PoseStack;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.entity.state.HumanoidRenderState;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.core.component.DataComponents;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.equipment.Equippable;
import net.minecraft.world.item.equipment.EquipmentAsset;
import net.minecraft.world.item.equipment.EquipmentAssets;

/**
 * Draws the decorative parts on worn armor.
 *
 * <p>A separate layer from vanilla's {@code HumanoidArmorLayer} rather than a mixin into it, because
 * the two do genuinely different things: that layer paints textures onto the armor model, and this
 * one hangs extra geometry off the body. Sitting beside it also means decorations survive on armor
 * this mod has never heard of - any equippable in the right slot can carry them.
 *
 * <p>Each part is drawn in the local frame of the humanoid part its socket names, so a crest rides
 * the head when the head turns and pauldrons swing with the arms, with no animation code: the parent
 * part's own pose is the animation.
 */
@Environment(EnvType.CLIENT)
public class ArmorDecorationLayer<S extends HumanoidRenderState, M extends HumanoidModel<S>>
    extends RenderLayer<S, M> {

    /**
     * Stands in for the equipment asset when a decorated item declares none.
     *
     * <p>{@link net.minecraft.world.item.equipment.trim.MaterialAssetGroup#assetId} only consults its
     * override map, so any key absent from it yields the material's base texture - which is the right
     * answer here. A key in our own namespace is used rather than borrowing a vanilla one so that a
     * datapack adding, say, a {@code minecraft:leather} override can never accidentally repaint these.
     */
    private static final ResourceKey<EquipmentAsset> NO_ASSET = ResourceKey.create(
        EquipmentAssets.ROOT_ID,
        Identifier.fromNamespaceAndPath(com.mattjesmc.armorpieces.ArmorPieces.MOD_ID, "none")
    );

    public ArmorDecorationLayer(final RenderLayerParent<S, M> renderer) {
        super(renderer);
    }

    @Override
    public void submit(
        final PoseStack poseStack,
        final SubmitNodeCollector collector,
        final int lightCoords,
        final S state,
        final float yRot,
        final float xRot
    ) {
        if (state.isInvisible) {
            return;
        }
        this.submitForSlot(poseStack, collector, lightCoords, state, state.headEquipment, EquipmentSlot.HEAD);
        this.submitForSlot(poseStack, collector, lightCoords, state, state.chestEquipment, EquipmentSlot.CHEST);
        this.submitForSlot(poseStack, collector, lightCoords, state, state.legsEquipment, EquipmentSlot.LEGS);
        this.submitForSlot(poseStack, collector, lightCoords, state, state.feetEquipment, EquipmentSlot.FEET);
    }

    private void submitForSlot(
        final PoseStack poseStack,
        final SubmitNodeCollector collector,
        final int lightCoords,
        final S state,
        final ItemStack itemStack,
        final EquipmentSlot slot
    ) {
        final ArmorDecorations decorations = itemStack.get(ModDataComponents.DECORATIONS);
        if (decorations == null || decorations.isEmpty()) {
            return;
        }

        // The armor's own asset id decides which material variant a part uses, so gold decoration on
        // gold armor darkens exactly as a gold trim on gold armor does.
        final Equippable equippable = itemStack.get(DataComponents.EQUIPPABLE);
        final ResourceKey<EquipmentAsset> assetKey =
            equippable == null ? NO_ASSET : equippable.assetId().orElse(NO_ASSET);
        final int overlayCoords = LivingEntityRenderer.getOverlayCoords(state, 0.0F);

        for (final var mapping : decorations.entries().entrySet()) {
            final DecorationAnchor anchor = mapping.getKey();
            // A component can be written by a command as easily as by the recipe, so a socket that
            // does not belong to the piece it is riding on is possible. Skip it rather than draw a
            // crest out of a boot.
            if (anchor.slot() != slot) {
                continue;
            }
            this.submitDecoration(poseStack, collector, lightCoords, overlayCoords, state, anchor, mapping.getValue(), assetKey);
        }
    }

    private void submitDecoration(
        final PoseStack poseStack,
        final SubmitNodeCollector collector,
        final int lightCoords,
        final int overlayCoords,
        final S state,
        final DecorationAnchor anchor,
        final DecorationEntry entry,
        final ResourceKey<EquipmentAsset> assetKey
    ) {
        final Identifier assetId = entry.decoration().value().assetId();
        final ModelPart geometry = DecorationGeometryManager.instance().get(assetId);
        if (geometry == null) {
            // A datapack named a part whose resource pack half is not installed. Not an error worth
            // a log line every frame, and the rest of the armor still draws.
            return;
        }

        // One greyscale master, coloured for this material on first use and cached from then on.
        final var renderType = RenderTypes.armorCutoutNoCull(
            DecorationTextureManager.instance().resolve(assetId, entry.materialSuffix(assetKey)));
        final M model = this.getParentModel();

        for (final DecorationAnchor.Attachment attachment : anchor.attachments()) {
            poseStack.pushPose();
            // Enter the parent part's frame: its animated translation and rotation, exactly as
            // ModelPart.render would apply before drawing its own cubes.
            resolvePart(model, attachment.part()).translateAndRotate(poseStack);
            // Offsets are authored in model units, so they divide by 16 the way translateAndRotate does.
            poseStack.translate(attachment.x() / 16.0F, attachment.y() / 16.0F, attachment.z() / 16.0F);
            if (attachment.mirror()) {
                // A negative uniform scale; PoseStack.scale flips the normal matrix to match and keeps
                // its normals trusted, and armorCutoutNoCull does not backface-cull, so the mirrored
                // half of a pair lights and draws identically to the original.
                poseStack.scale(-1.0F, 1.0F, 1.0F);
            }
            collector.submitModelPart(geometry, poseStack, renderType, lightCoords, overlayCoords, null, -1, null, state.outlineColor);
            poseStack.popPose();
        }
    }

    private static ModelPart resolvePart(final HumanoidModel<?> model, final DecorationAnchor.HumanoidPart part) {
        return switch (part) {
            case HEAD -> model.head;
            case BODY -> model.body;
            case LEFT_ARM -> model.leftArm;
            case RIGHT_ARM -> model.rightArm;
            case LEFT_LEG -> model.leftLeg;
            case RIGHT_LEG -> model.rightLeg;
        };
    }
}
