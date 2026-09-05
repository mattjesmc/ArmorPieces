package com.mattjesmc.armorpieces.client.mixin;

import com.mattjesmc.armorpieces.client.ArmorDecorationLayer;
import com.mattjesmc.armorpieces.config.ArmorPiecesConfig;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.player.PlayerModel;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.player.AvatarRenderer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Puts the arm's own parts on the first-person hand.
 *
 * <p>The hand you hold up in first person is not a separate model: {@code renderHand} takes the very
 * {@code PlayerModel} the entity renderer uses, resets its pose, hides everything but the one arm
 * and its sleeve, and submits that arm. What it does NOT do is go through
 * {@link net.minecraft.client.renderer.entity.LivingEntityRenderer#render}, and render layers are
 * submitted from inside that - so no layer runs here at all. Vanilla armor is absent from the
 * first-person hand for the same reason ours was.
 *
 * <p>A mixin rather than anything cleaner because there is no seam: the hand is drawn by a private
 * method on the renderer with no event, no layer list and no callback of any kind between the two
 * lines that pose the arm and submit it.
 *
 * <h2>Why the transform needs no first-person arithmetic</h2>
 *
 * <p>Injecting at the TAIL leaves the pose stack exactly where {@code renderHand} left it - in the
 * arm's PARENT frame, since {@code submitModelPart} applies a part's own pivot and rotation
 * internally without touching the stack. That is the same relationship the entity pass has when
 * {@link ArmorDecorationLayer} runs, so entering the socket's frame is the same two lines there and
 * here, and a vambrace lands on the forearm in first person because it lands on the forearm at all.
 * Whatever {@code ItemInHandRenderer} did to the stack before this - the swing, the eat bob, the
 * block-hit jab - is upstream of both and carries the part along with the limb.
 *
 * <h2>What is drawn</h2>
 *
 * <p>The chestplate's sockets, and only the attachment on the arm actually being drawn.
 * {@link DecorationAnchor} is a closed enum, so the two arm-parented sockets - pauldrons and
 * vambraces - are provably all there are, and both belong to the chestplate; the head, body and legs
 * are off screen. Passing the limb also picks the correct half of a mirrored pair rather than
 * drawing both on one arm.
 */
@Mixin(AvatarRenderer.class)
public class AvatarRendererMixin {
    @Inject(
        method = "renderHand(Lcom/mojang/blaze3d/vertex/PoseStack;"
            + "Lnet/minecraft/client/renderer/SubmitNodeCollector;ILnet/minecraft/resources/Identifier;"
            + "Lnet/minecraft/client/model/geom/ModelPart;Z)V",
        at = @At("TAIL"))
    private void armorpieces$firstPersonParts(
        final PoseStack poseStack,
        final SubmitNodeCollector collector,
        final int lightCoords,
        final Identifier skin,
        final ModelPart arm,
        final boolean sleeves,
        final CallbackInfo callback
    ) {
        if (!ArmorPiecesConfig.get().firstPersonParts()) {
            return;
        }

        // The hand is the local player's by construction - ItemInHandRenderer draws no other - and
        // the method is handed a skin and a bare ModelPart, neither of which can name a wearer.
        final LocalPlayer player = Minecraft.getInstance().player;
        if (player == null) {
            return;
        }
        final ItemStack chest = player.getItemBySlot(EquipmentSlot.CHEST);
        if (chest.isEmpty()) {
            return;
        }

        final PlayerModel model = ((AvatarRenderer<?>) (Object) this).getModel();
        final DecorationAnchor.HumanoidPart limb = arm == model.leftArm
            ? DecorationAnchor.HumanoidPart.LEFT_ARM
            : DecorationAnchor.HumanoidPart.RIGHT_ARM;

        // No overlay and no outline: the hand pass has neither a hurt flash nor a glowing outline to
        // inherit, which is what the render state would have supplied in the entity pass.
        ArmorDecorationLayer.submitForSlot(
            poseStack, collector, lightCoords, OverlayTexture.NO_OVERLAY, 0,
            model, chest, EquipmentSlot.CHEST, limb);
    }
}
