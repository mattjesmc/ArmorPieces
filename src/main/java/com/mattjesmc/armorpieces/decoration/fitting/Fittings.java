package com.mattjesmc.armorpieces.decoration.fitting;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.fitting.builtin.BannerFitting;
import com.mattjesmc.armorpieces.decoration.fitting.builtin.DyeFitting;
import com.mattjesmc.armorpieces.decoration.fitting.builtin.MaterialFitting;
import com.mojang.serialization.MapCodec;
import net.minecraft.core.Registry;
import net.minecraft.resources.Identifier;

/**
 * The public front door for fitting types: where a mod registers one, and where this mod registers
 * the three it ships.
 *
 * <h2>Registering one from another mod</h2>
 *
 * <pre>{@code
 * public record GlowFitting(Component description) implements Fitting.Masked {
 *     public static final MapCodec<GlowFitting> CODEC = ...;
 *     ...
 * }
 *
 * // in your ModInitializer:
 * Fittings.register(Identifier.fromNamespaceAndPath("examplemod", "glow"), GlowFitting.CODEC);
 * }</pre>
 *
 * <p>and then, in any pack, a fitting of that type -
 * {@code data/examplemod/armorpieces/fitting/lantern.json}:
 *
 * <pre>{@code
 * { "type": "examplemod:glow", "description": { "translate": "fitting.examplemod.lantern" } }
 * }</pre>
 *
 * <p>- which any part may then list under {@code "fittings"}. A masked fitting is complete at that
 * point; the mask PNG beside the part's master is the only art. A fitting that draws geometry of its
 * own also registers a renderer on the client, see
 * {@code com.mattjesmc.armorpieces.client.fitting.FittingRenderers}.
 *
 * <p>A pack with no Java is not shut out: the three built-ins cover a region coloured by any set of
 * trim materials, a region coloured by dye, and a bone that takes a banner, each configured from the
 * fitting's JSON alone.
 */
public final class Fittings {
    private Fittings() {}

    /**
     * Registers a fitting type, making {@code id} usable as a {@code "type"} in any fitting file.
     * Call it from a {@code ModInitializer}; registering an id twice throws, as every registry does.
     */
    public static <T extends Fitting> MapCodec<T> register(final Identifier id, final MapCodec<T> codec) {
        Registry.register(ArmorPiecesRegistries.FITTING_TYPES, id, codec);
        return codec;
    }

    private static <T extends Fitting> MapCodec<T> register(final String path, final MapCodec<T> codec) {
        return register(Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, path), codec);
    }

    /**
     * The built-ins. Three, and between them the two ways a fitting can appear: {@code material} and
     * {@code dye} are masks over the part's own texture, {@code banner} replaces a bone with the
     * banner renderer. The four fittings this mod ships are instances of these - gemstone and guard
     * are both {@code material} with different tags.
     */
    public static void register() {
        register("material", MaterialFitting.CODEC);
        register("dye", DyeFitting.CODEC);
        register("banner", BannerFitting.CODEC);
        ArmorPieces.LOGGER.info(
            "[Armor Pieces] Registered {} fitting types.", ArmorPiecesRegistries.FITTING_TYPES.size());
    }
}
