package com.mattjesmc.armorpieces.client.fitting;

import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.decoration.fitting.FittingValue;
import com.mojang.blaze3d.vertex.PoseStack;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.SubmitNodeCollector;

/**
 * Draws a filled fitting that is more than a mask - the client half of a fitting type that
 * replaces geometry rather than colouring it.
 *
 * <p>Most fittings never need one: a {@link Fitting.Masked} is baked into the part's texture and
 * drawn by the part's own pass. A renderer is for the banner and its kind, where what is drawn is
 * not a recolour of the part but layers with their own sprites. It is called once per attachment
 * of the part, after the part's own pass, inside the same frame - so a renderer that walks the
 * part's bones draws in the right place without knowing which socket it is in or which limb is
 * swinging.
 *
 * <p>Registered against the fitting TYPE in {@link FittingRenderers}, from a client initializer.
 */
@Environment(EnvType.CLIENT)
public interface FittingRenderer {
    void submit(Context context);

    /**
     * Everything a renderer is handed.
     *
     * @param poseStack     already in the part's frame: the limb's pose, the socket offset and the
     *                      mirror for a paired attachment are applied. Push before changing it.
     * @param collector     where to submit. Use {@code order(n)} for passes that must stack.
     * @param geometry      the part's FULL baked geometry, every bone present, so the renderer can
     *                      find the one it draws in place of. The part's own pass omitted it.
     * @param fitting       the fitting being drawn; the renderer knows its concrete type.
     * @param value         what is set in it; likewise.
     */
    record Context(
        PoseStack poseStack,
        SubmitNodeCollector collector,
        int lightCoords,
        int overlayCoords,
        int outlineColor,
        ModelPart geometry,
        Fitting fitting,
        FittingValue value
    ) {}
}
