package com.mattjesmc.armorpieces.client.mixin;

import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import com.llamalad7.mixinextras.sugar.Local;
import com.mattjesmc.armorpieces.client.texture.ArmorSkinTextureManager;
import com.mattjesmc.armorpieces.client.texture.ClothTextureManager;
import com.mattjesmc.armorpieces.cloth.ClothValue;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.skin.ArmorSkinValue;
import java.util.List;
import net.minecraft.client.renderer.entity.layers.EquipmentLayerRenderer;
import net.minecraft.client.resources.model.EquipmentClientInfo;
import net.minecraft.resources.Identifier;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

/**
 * Draws a skinned or clothed piece of armor with a texture of ours instead of the material's own -
 * the one place either is applied, and the mod's only mixin.
 *
 * <p>The alternative was to rewrite the piece's {@code minecraft:equippable} component and point its
 * asset id at art of ours, which needs no mixin at all. It was rejected for two things it would
 * cost, both real:
 *
 * <ul>
 *   <li>a skinned piece would render WRONG with the mod removed, breaking the invariant the rest of
 *       the mod keeps - strip Armor Pieces and the armor is still a valid, still trimmed item;</li>
 *   <li>a trim's {@code _darker} override is keyed on the equipment asset, so a gold trim on gold
 *       armor would stop darkening the moment the asset id was ours, and the fix for that would be
 *       to override vanilla's own trim material files, which is worse than the problem.</li>
 * </ul>
 *
 * <p>Substituting the TEXTURE alone keeps both. The asset id vanilla was given is still the one it
 * uses for the trim sprite a few lines further down this same method, and the component on the stack
 * is one that a game without this mod simply ignores.
 *
 * <p>Which layer is replaced: the one that is the armor's own shell. Most armor declares a single
 * layer and that is it. Leather declares two - a tinted shell and an untinted overlay carrying the
 * stitching and the straps - and there the skin takes the tinted one, so a dyed piece is still dyed
 * and the buckles stay where vanilla drew them. A layer that is neither is left alone.
 *
 * <h2>The cloth, which rides the same substitution</h2>
 *
 * <p>A garment is composited INTO the texture rather than drawn as a pass of its own, which is what
 * puts it over the skin, under the trim (a later pass in this very method) and under every part
 * (an appended render layer, which draws after all of this) at no cost. See
 * {@link ClothTextureManager}.
 *
 * <p>It goes on the LAST layer, not the shell, and the reason is leather: the shell there is
 * multiplied by the piece's dye at draw time, so a garment composited into it would come out brown
 * on undyed leather and purple on blue. The last layer is leather's untinted overlay and is the sole
 * layer everywhere else, so it is drawn untinted in both cases. The shading still comes from the
 * shell, which is where the armor's form actually is.
 *
 * <p>Both may apply to one layer - single-layer armor that is skinned AND clothed - and then the
 * order here is the order on the body: the skin decides what the plate is, and the cloth is laid
 * over what the skin produced.
 */
@Mixin(EquipmentLayerRenderer.class)
public class EquipmentLayerRendererMixin {
    /**
     * Replaces the texture this layer was about to be drawn with.
     *
     * <p>Placed on the memoized lookup's result rather than on the lookup itself: that cache is keyed
     * on the layer alone and knows nothing of the stack being drawn, so it must stay vanilla's.
     */
    @ModifyExpressionValue(
        method = "renderLayers(Lnet/minecraft/client/resources/model/EquipmentClientInfo$LayerType;"
            + "Lnet/minecraft/resources/ResourceKey;Lnet/minecraft/client/model/Model;Ljava/lang/Object;"
            + "Lnet/minecraft/world/item/ItemStack;Lcom/mojang/blaze3d/vertex/PoseStack;"
            + "Lnet/minecraft/client/renderer/SubmitNodeCollector;ILnet/minecraft/resources/Identifier;II)V",
        at = @At(
            value = "INVOKE",
            target = "Ljava/util/function/Function;apply(Ljava/lang/Object;)Ljava/lang/Object;",
            ordinal = 0))
    private Object armorpieces$texture(
        final Object original,
        final @Local(argsOnly = true) EquipmentClientInfo.LayerType layerType,
        final @Local(argsOnly = true) ItemStack itemStack,
        final @Local List<EquipmentClientInfo.Layer> layers,
        final @Local EquipmentClientInfo.Layer layer
    ) {
        if (!(original instanceof Identifier texture)) {
            return original;
        }
        final ArmorSkinValue skin = itemStack.get(ModDataComponents.SKIN);
        final ClothValue cloth = itemStack.get(ModDataComponents.CLOTH);
        if (skin == null && cloth == null) {
            return original;
        }
        final String sheet = layerType.getSerializedName();

        Identifier result = texture;
        if (skin != null && isShell(layer, layers)) {
            final Identifier skinned =
                ArmorSkinTextureManager.instance().resolve(skin.skin().value(), sheet, texture);
            if (skinned != null) {
                result = skinned;
            }
        }
        if (cloth != null && layer.equals(layers.getLast())) {
            // The armor's form, as the player actually sees it: a skinned piece's own greyscale
            // master IS the form, and an unskinned one's is in the material's vanilla texture.
            final Identifier shading = skin != null
                ? skin.skin().value().sheet(sheet, "")
                : shellTexture(layers, layerType);
            final Identifier clothed =
                ClothTextureManager.instance().resolve(cloth, sheet, result, shading);
            if (clothed != null) {
                result = clothed;
            }
        }
        return result;
    }

    /** The shell layer's own texture - what the armor's lighting is measured from. */
    private static Identifier shellTexture(
        final List<EquipmentClientInfo.Layer> layers,
        final EquipmentClientInfo.LayerType layerType
    ) {
        for (final EquipmentClientInfo.Layer candidate : layers) {
            if (candidate.dyeable().isPresent()) {
                return candidate.getTextureLocation(layerType);
            }
        }
        return layers.getFirst().getTextureLocation(layerType);
    }

    /**
     * Whether this layer is the armor's own shell - the thing a skin replaces - rather than
     * something laid over it.
     *
     * <p>A dyeable layer always is: dye is applied to the armor itself, and vanilla's own two-layer
     * leather is exactly that shell plus an overlay. An asset with no dyeable layer at all is a
     * single-layer material, and its one layer is the shell.
     */
    private static boolean isShell(
        final EquipmentClientInfo.Layer layer,
        final List<EquipmentClientInfo.Layer> layers
    ) {
        if (layer.dyeable().isPresent()) {
            return true;
        }
        for (final EquipmentClientInfo.Layer other : layers) {
            if (other.dyeable().isPresent()) {
                return false;
            }
        }
        return true;
    }
}
