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
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.item.equipment.trim.TrimMaterial;

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
 * on the tick path. Every hook below RUNS on the server, but the effects themselves are still sent
 * to the client in {@link ArmorDecoration#DIRECT_STREAM_CODEC}, because vanilla evaluates
 * {@code canGlide} on both sides - see the note there.
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

    // ---- What an effect can be asked about itself -----------------------------------------------

    /**
     * Whether this effect can ever reach {@code hook} - {@code instanceof}, except through a wrapper.
     *
     * <p>A gate like {@code if_fitting} implements EVERY hook, because it cannot know which one the
     * effect it wraps needs; that is right for dispatch and wrong for every other question, since
     * asking a gate whether it contributes attributes would always say yes. Wrappers override this to
     * forward to what they wrap, so "does this part change an attribute" has an honest answer however
     * deeply the effect is nested - which is what the load-time rules on
     * {@link com.mattjesmc.armorpieces.decoration.effect.builtin.WearerConditionEffect} and the
     * tooltip both ask.
     */
    default boolean reaches(final Class<? extends DecorationEffect> hook) {
        return hook.isInstance(this);
    }

    /**
     * Whether the effect is contributing anything at this moment, for the benefit of a reader.
     *
     * <p>Nothing dispatches on this - a gate decides for itself, per hook, whether to forward - so an
     * effect that answers it wrongly changes no behaviour. It exists because a condition is invisible
     * otherwise: {@code /armorpieces effects} prints a worn part's effects and marks the ones that
     * are not doing anything right now, which is the difference between a player believing a part is
     * broken and seeing that they are holding the wrong thing.
     */
    default boolean applies(final DecorationEffectContext context) {
        return true;
    }

    /**
     * One line saying what this effect contributes, for the piece's tooltip and for
     * {@code /armorpieces effects}.
     *
     * <p>The material is passed because a value may scale with it ({@link MaterialValue}), so the
     * line a player reads is the number that part in that material actually gives - not the range it
     * could give.
     *
     * <p>The default is the effect type's own id as a translation key, {@code effect.<ns>.<path>},
     * falling back to the id itself when no pack ships a language file for it. That is the honest
     * answer for a third-party effect this mod knows nothing about, and a mod that wants a real line
     * either ships the key or overrides this.
     */
    default Component description(final Holder<TrimMaterial> material) {
        final Identifier id = ArmorPiecesRegistries.DECORATION_EFFECT_TYPES.getKey(this.codec());
        return id == null
            ? Component.literal("?")
            : Component.translatableWithFallback(id.toLanguageKey("effect"), id.toString());
    }

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
     * pure function of the part, its material, its socket and THE WEARER'S EQUIPMENT - a modifier that
     * depends on the world or on chance will be silently wrong, because it is computed once and left
     * in place.
     *
     * <p>Equipment is in that list because the dispatcher reconciles the armor slots again whenever a
     * hand changes, which is what makes a claw that only bites bare-handed expressible without
     * weakening the rule. Everything else a wearer might be doing - where they are, how much health
     * they have, whether they are sneaking - is still outside it, and
     * {@link com.mattjesmc.armorpieces.decoration.effect.builtin.WearerConditionEffect} refuses such a
     * condition at load rather than letting it half-work.
     *
     * <p>The dispatcher re-ids every modifier it receives into the socket it came from, so the same
     * part worn in two sockets contributes two modifiers rather than one that overwrites itself. The
     * id an effect chooses only has to be unique within the effect.
     */
    interface Attributes extends DecorationEffect {
        void collectAttributes(DecorationEffectContext context, BiConsumer<Holder<Attribute>, AttributeModifier> out);

        /**
         * Every modifier this effect COULD contribute, conditions ignored - what the dispatcher takes
         * back off when it reconciles.
         *
         * <p>A conditional modifier is added while its condition holds and has to come off when it
         * stops holding, at which point {@link #collectAttributes} no longer offers it and a removal
         * would have nothing to name. Removing by this instead means a gate takes back exactly what it
         * could have given. Only ids reach the removal, so an effect whose VALUE varies has nothing to
         * do here; only one whose PRESENCE varies overrides it, which in practice means the gates.
         */
        default void collectPossibleAttributes(
            final DecorationEffectContext context,
            final BiConsumer<Holder<Attribute>, AttributeModifier> out
        ) {
            this.collectAttributes(context, out);
        }
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
