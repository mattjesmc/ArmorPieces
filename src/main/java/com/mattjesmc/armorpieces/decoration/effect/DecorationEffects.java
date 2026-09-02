package com.mattjesmc.armorpieces.decoration.effect;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.effect.builtin.AttributeEffect;
import com.mattjesmc.armorpieces.decoration.effect.builtin.BlinkEffect;
import com.mattjesmc.armorpieces.decoration.effect.builtin.ConditionalEffect;
import com.mattjesmc.armorpieces.decoration.effect.builtin.GlideEffect;
import com.mattjesmc.armorpieces.decoration.effect.builtin.StatusEffect;
import com.mojang.serialization.MapCodec;
import net.minecraft.core.Registry;
import net.minecraft.resources.Identifier;

/**
 * The public front door for effects: where a mod registers an effect TYPE, and where this mod
 * registers the handful it ships.
 *
 * <h2>Registering one from another mod</h2>
 *
 * <pre>{@code
 * public record BlinkAway(float chance) implements DecorationEffect.Damage {
 *     public static final MapCodec<BlinkAway> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
 *         Codec.FLOAT.fieldOf("chance").forGetter(BlinkAway::chance)
 *     ).apply(i, BlinkAway::new));
 *
 *     public MapCodec<? extends DecorationEffect> codec() { return CODEC; }
 *
 *     public boolean allowDamage(DecorationEffectContext ctx, DamageSource src, float amount) {
 *         ...
 *     }
 * }
 *
 * // in your ModInitializer, any time during initialization:
 * DecorationEffects.register(Identifier.fromNamespaceAndPath("examplemod", "blink_away"), BlinkAway.CODEC);
 * }</pre>
 *
 * <p>and then, in that mod's own datapack - or in anybody's:
 *
 * <pre>{@code
 * {
 *   "asset_id": "examplemod:arc_core",
 *   "description": { "translate": "decoration.examplemod.arc_core" },
 *   "anchors": ["back"],
 *   "effects": [ { "type": "examplemod:blink_away", "chance": 0.25 } ]
 * }
 * }</pre>
 *
 * <p>Note what the registering mod does NOT have to do: it does not register an item, a recipe, a
 * model or a render layer, and it does not touch this mod's code. The part itself was already
 * datapack-only; this adds the one thing that could not be, which is behaviour.
 *
 * <p>A PACK that ships no Java at all is not shut out either - the four built-in behaviours below are
 * general-purpose enough to cover most of what a part would want to do, a fifth registration gates
 * any of them on what a fitting holds, and every one of them is configured entirely from the part's
 * JSON.
 *
 * <p>The registry is a static one rather than a datapack registry, for the same reason vanilla's
 * effect-type registries are: it holds codecs, which are code, and code does not load from a pack.
 */
public final class DecorationEffects {
    private DecorationEffects() {}

    /**
     * Registers an effect type, making {@code id} usable as a {@code "type"} on any part in any pack.
     *
     * <p>Call it from a {@code ModInitializer}. Registering the same id twice throws, as every
     * Minecraft registry does.
     *
     * @return the codec, so a caller can keep the registration on one line.
     */
    public static <T extends DecorationEffect> MapCodec<T> register(final Identifier id, final MapCodec<T> codec) {
        Registry.register(ArmorPiecesRegistries.DECORATION_EFFECT_TYPES, id, codec);
        return codec;
    }

    /** Convenience for the common case of an id in this mod's namespace. */
    private static <T extends DecorationEffect> MapCodec<T> register(final String path, final MapCodec<T> codec) {
        return register(Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, path), codec);
    }

    /**
     * The built-ins.
     *
     * <p>Four behaviours, reaching four of the five hooks with no Java: an attribute modifier and a
     * status effect (the two things most parts would want), a dodge (the one that proves a part can
     * refuse a hit), and a glider (the one that proves a part can change how the wearer moves).
     * {@link DecorationEffect.Lifecycle} is the hook none of them reach, and deliberately so: what it
     * is for is state living outside the item, which is the one thing a JSON field cannot describe.
     * {@code if_fitting} is a fifth registration but not a fifth behaviour - it gates the others.
     *
     * <p>Nineteen of the twenty parts this mod ships use none of them and stay purely cosmetic,
     * which is a choice about this mod's content rather than a limit of the system. The twentieth is
     * {@code pinions} - an elytra cut down and bolted to a back bracket - and it exists so that this
     * registry has one worked example inside the mod rather than only in a test pack: the part is
     * still two files and a PNG, and the only thing that makes it fly is a
     * {@code "type": "armorpieces:glide"} entry any pack could have written.
     */
    public static void register() {
        register("attribute", AttributeEffect.CODEC);
        register("mob_effect", StatusEffect.CODEC);
        register("blink", BlinkEffect.CODEC);
        register("glide", GlideEffect.CODEC);
        // Not a fifth behaviour but a gate on the other four: runs its effect only while one of the
        // part's fittings holds what it asks for, which is how a gem comes to mean something.
        register("if_fitting", ConditionalEffect.CODEC);
        ArmorPieces.LOGGER.info(
            "[Armor Pieces] Registered {} decoration effect types.", ArmorPiecesRegistries.DECORATION_EFFECT_TYPES.size());
    }
}
