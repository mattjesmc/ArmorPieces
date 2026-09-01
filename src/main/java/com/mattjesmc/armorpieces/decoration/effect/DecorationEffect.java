package com.mattjesmc.armorpieces.decoration.effect;

import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import java.util.List;
import java.util.function.BiConsumer;
import java.util.function.Function;
import net.minecraft.core.Holder;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;

/**
 * A behaviour a decorative part carries - the gameplay half of a part, and the one half of it that
 * cannot be data.
 *
 * <p>Everything else about a part is JSON ({@link ArmorDecoration}): its shape, its texture, its
 * name, the sockets it fits. Behaviour is code, so this is a registry of CODE keyed by id -
 * {@code armorpieces:decoration_effect_type} - in the exact shape vanilla uses for the same problem
 * in {@code BuiltInRegistries.ENCHANTMENT_ENTITY_EFFECT_TYPE}: the registry holds
 * {@link MapCodec}s, and the dispatch codec below turns {@code {"type": "<ns>:<effect>", ...}} into
 * an instance. A mod registers its effect type in its initializer (see {@link DecorationEffects}),
 * and from that moment a datapack - anyone's datapack, including one shipped by a third pack - can
 * name it on a part.
 *
 * <h2>Why the hooks are a closed set and the effects are not</h2>
 *
 * <p>This mirrors, deliberately, the split that {@link DecorationAnchor} already makes. An anchor is
 * closed because it is a <i>place on the body</i>, and a pack inventing one would be inventing a body
 * part the model does not have. A hook is closed for the same kind of reason: it is a <i>moment in
 * the server loop that this mod actually reaches</i>, and a hook nothing dispatches is a hook that
 * never fires. What plugs into those moments - the effects themselves - is wide open, and that is
 * where every interesting thing lives.
 *
 * <p>The hooks are the nested interfaces below. An effect implements as many as it needs and none it
 * does not; dispatch is by {@code instanceof}, so an effect that only reacts to damage costs nothing
 * on the tick path. All of them run SERVER-SIDE only, which is also why effects are deliberately
 * absent from {@link ArmorDecoration#DIRECT_STREAM_CODEC} - see the note there.
 */
public interface DecorationEffect {
    /**
     * {@code {"type": "<ns>:<effect>", ...}}, dispatched through the type registry - the same shape,
     * and the same construction, as every vanilla dispatched codec (loot functions, enchantment
     * effects, density functions).
     */
    Codec<DecorationEffect> CODEC = ArmorPiecesRegistries.DECORATION_EFFECT_TYPES
        .byNameCodec()
        .dispatch(DecorationEffect::codec, Function.identity());

    /** The list as it appears in a part's {@code effects} field. Empty is the norm - parts are cosmetic by default. */
    Codec<List<DecorationEffect>> LIST_CODEC = CODEC.listOf();

    /** This effect's entry in {@code armorpieces:decoration_effect_type}. Names it in JSON. */
    MapCodec<? extends DecorationEffect> codec();

    // ---- The hooks ------------------------------------------------------------------------------

    /**
     * Runs every server tick while the decorated piece is worn.
     *
     * <p>The broadest hook and the one that pays for most things: a passive buff, a particle trail,
     * an extra pull downwards while gliding, durability that drains faster than vanilla's. Ticking
     * effects are the only reason the dispatcher tracks wearers at all, so an effect that does not
     * implement this is never visited on the tick path.
     */
    interface Ticking extends DecorationEffect {
        void tick(DecorationEffectContext context);
    }

    /**
     * Sees damage aimed at the wearer, and may refuse it.
     *
     * <p>{@link #allowDamage} runs before the hit resolves and returning {@code false} cancels it
     * outright - the hook a "dodge" is written against, where the part teleports its wearer out of
     * the way of an arrow and the arrow then hits nothing. Cancelling is all-or-nothing on purpose:
     * the underlying event is a veto, not a damage pipeline, so an effect that wants to *reduce*
     * damage should register an armor or armor-toughness modifier through {@link Attributes} instead,
     * where vanilla's own formula does the arithmetic.
     *
     * <p>{@link #afterDamage} runs once the hit has landed, for effects that answer a blow rather
     * than avoid it.
     */
    interface Damage extends DecorationEffect {
        /** {@code false} cancels the damage entirely. The first effect to refuse wins; the rest are not asked. */
        default boolean allowDamage(final DecorationEffectContext context, final DamageSource source, final float amount) {
            return true;
        }

        /** @param dealt what the wearer actually lost, after armor, resistance and absorption. */
        default void afterDamage(
            final DecorationEffectContext context,
            final DamageSource source,
            final float amount,
            final float dealt,
            final boolean blocked
        ) {}
    }

    /**
     * Contributes attribute modifiers for as long as the piece is worn.
     *
     * <p>Applied and removed on equipment change rather than re-derived per tick, so this must be a
     * pure function of the part, its material and its socket - a modifier that depends on the world
     * or on chance will be silently wrong, because it is computed once and left in place.
     *
     * <p>The dispatcher re-ids every modifier it receives into the socket it came from, so the same
     * part worn in two sockets contributes two modifiers rather than one that overwrites itself. The
     * id an effect chooses only has to be unique within the effect.
     */
    interface Attributes extends DecorationEffect {
        void collectAttributes(DecorationEffectContext context, BiConsumer<Holder<Attribute>, AttributeModifier> out);
    }

    /**
     * Lets the wearer glide, whatever is in the chest slot.
     *
     * <p>Rides Fabric's custom-elytra event, so a part that grants gliding grants the real thing -
     * the same launch, the same physics, the same firework rockets - rather than an imitation. What
     * makes such a part balanced instead of strictly better than an elytra is what it does in
     * {@link Ticking}: pull down harder, or spend durability faster.
     */
    interface Gliding extends DecorationEffect {
        boolean allowsGliding(DecorationEffectContext context);
    }

    /**
     * Notified when the decorated piece is put on or taken off - including the implicit equip an
     * entity performs when it loads into the world wearing something.
     *
     * <p>For effects that own state outside the item: a summoned companion, a scoreboard flag, a
     * client packet. Anything that is merely a number while worn wants {@link Attributes} instead,
     * which the dispatcher already reconciles on exactly these two moments.
     */
    interface Lifecycle extends DecorationEffect {
        default void onEquip(final DecorationEffectContext context) {}

        default void onUnequip(final DecorationEffectContext context) {}
    }
}
