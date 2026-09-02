package com.mattjesmc.armorpieces.client.fitting;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import java.util.HashMap;
import java.util.Map;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.minecraft.resources.Identifier;
import org.jspecify.annotations.Nullable;

/**
 * Renderers by fitting type - the client-side front door for a fitting type that draws.
 *
 * <pre>{@code
 * // in your ClientModInitializer:
 * FittingRenderers.register(Identifier.fromNamespaceAndPath("examplemod", "glow"), new GlowFittingRenderer());
 * }</pre>
 *
 * <p>Keyed by the TYPE's id, not the fitting's: a renderer knows how to draw every fitting of its
 * kind, whatever pack the fitting came from. A type without a renderer is drawn by nothing beyond
 * its mask, which for a {@link Fitting.Masked} is everything.
 */
@Environment(EnvType.CLIENT)
public final class FittingRenderers {
    private static final Map<Identifier, FittingRenderer> RENDERERS = new HashMap<>();

    private FittingRenderers() {}

    /** Registers the renderer for a fitting type. Replacing one is allowed; the last registration wins. */
    public static void register(final Identifier type, final FittingRenderer renderer) {
        RENDERERS.put(type, renderer);
    }

    static void register(final String path, final FittingRenderer renderer) {
        register(Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, path), renderer);
    }

    /** The renderer for this fitting's type, or {@code null} if its type has none. */
    public static @Nullable FittingRenderer get(final Fitting fitting) {
        final Identifier type = ArmorPiecesRegistries.FITTING_TYPES.getKey(fitting.codec());
        return type == null ? null : RENDERERS.get(type);
    }

    /** This mod's own: the banner. */
    public static void registerBuiltins() {
        register("banner", new BannerFittingRenderer());
    }
}
