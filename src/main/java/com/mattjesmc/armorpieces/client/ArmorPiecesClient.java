package com.mattjesmc.armorpieces.client;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.client.fitting.FittingRenderers;
import com.mattjesmc.armorpieces.client.geometry.DecorationGeometryManager;
import com.mattjesmc.armorpieces.client.texture.DecorationTextureManager;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.fabricmc.fabric.api.client.rendering.v1.LivingEntityRenderLayerRegistrationCallback;
import net.fabricmc.fabric.api.resource.ResourceManagerHelper;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.client.renderer.entity.state.HumanoidRenderState;
import net.minecraft.server.packs.PackType;

@Environment(EnvType.CLIENT)
public class ArmorPiecesClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        ResourceManagerHelper.get(PackType.CLIENT_RESOURCES)
            .registerReloadListener(DecorationGeometryManager.instance());
        // Indexes which parts ship a master and which ship hand-authored per-material overrides, and
        // reads the trim palettes every pack declares. Colouring itself happens on first use.
        ResourceManagerHelper.get(PackType.CLIENT_RESOURCES)
            .registerReloadListener(DecorationTextureManager.instance());

        // The one fitting type that draws rather than colours. A mod's own goes through the same door.
        FittingRenderers.registerBuiltins();

        // Attach the decoration layer to every renderer that draws a humanoid, rather than to a fixed
        // list of entity types. Players, armor stands, zombies, skeletons, piglins and any modded mob
        // built on HumanoidModel all pick it up, which matches where armor itself can be worn.
        LivingEntityRenderLayerRegistrationCallback.EVENT.register((entityType, renderer, helper, context) -> {
            if (renderer.getModel() instanceof HumanoidModel<?>) {
                helper.register(createLayer(renderer));
            }
        });

        ArmorPieces.LOGGER.info("[Armor Pieces] Client ready.");
    }

    /**
     * Builds the layer for one renderer.
     *
     * <p>Isolated so the unchecked cast has one home and one explanation. The event hands out
     * {@code LivingEntityRenderer<?, ?, ?>}, so the compiler cannot see that a renderer whose model
     * is a {@code HumanoidModel} also has a {@code HumanoidRenderState} - but the two are declared
     * together on {@code HumanoidModel<S extends HumanoidRenderState>}, so the instanceof check above
     * is what makes this sound.
     */
    @SuppressWarnings("unchecked")
    private static <S extends HumanoidRenderState, M extends HumanoidModel<S>>
        ArmorDecorationLayer<S, M> createLayer(final LivingEntityRenderer<?, ?, ?> renderer) {
        return new ArmorDecorationLayer<>(
            (net.minecraft.client.renderer.entity.RenderLayerParent<S, M>) renderer);
    }
}
