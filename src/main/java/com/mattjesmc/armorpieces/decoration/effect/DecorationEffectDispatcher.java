package com.mattjesmc.armorpieces.decoration.effect;

import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import java.util.ArrayList;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Set;
import java.util.function.BiConsumer;
import java.util.function.BiPredicate;
import net.fabricmc.fabric.api.entity.event.v1.EntityElytraEvents;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerEntityEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.item.ItemStack;

/**
 * Where a {@link DecorationEffect} actually runs: the one place that knows how to walk from a living
 * entity to the parts it is wearing, and the only subscriber this mod has to the game's own events.
 *
 * <p>Every hook is dispatched from a Fabric API event rather than a mixin. That is not squeamishness
 * - it is the same argument the render layer makes for sitting beside {@code HumanoidArmorLayer}
 * instead of inside it. These events are the supported seams, they compose with every other mod that
 * uses them, and a decoration effect therefore cannot break an unrelated mod by winning a race for an
 * injection point.
 *
 * <h2>What it costs to wear nothing</h2>
 *
 * <p>The traversal is four {@code getItemBySlot} calls and, for anything actually decorated, one map
 * lookup per socket. An entity wearing plain armor pays four empty-stack checks; an entity wearing
 * decorated but effectless armor - which is eighteen of the nineteen parts this mod ships, all but
 * {@code pinions} - pays a list emptiness check
 * on top and never builds a context. The per-tick path additionally keeps to a tracked set of
 * wearers rather than sweeping the world, so an ordinary server with no effectful parts loaded does
 * no work at all beyond the damage and glide checks, which are already O(1) per event.
 */
public final class DecorationEffectDispatcher {
    /** The slots a {@link DecorationAnchor} can name. Iterating these rather than all eight skips hands, body and saddle. */
    private static final List<EquipmentSlot> ARMOR_SLOTS =
        List.of(EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET);

    /**
     * Entities known to be wearing something decorated, so the tick hook does not sweep the world.
     *
     * <p>Identity-keyed, said explicitly rather than left to the default: two living entities are
     * never equal in any useful sense, and this is what a set of them means anyway.
     *
     * <p>Membership is maintained from both ends - {@link ServerEntityEvents#ENTITY_LOAD} catches an
     * entity that arrives already dressed (a mob spawned with equipment, a player logging back in),
     * {@link ServerEntityEvents#EQUIPMENT_CHANGE} catches everything after that. Being in the set is
     * a hint rather than a promise: the tick re-reads the wearer's live equipment, so a stale entry
     * costs four slot checks and a missing entry is the only thing that would be wrong.
     */
    private static final Set<LivingEntity> WEARERS = Collections.newSetFromMap(new IdentityHashMap<>());

    /** Reused so the tick allocates nothing. An effect may kill its wearer, which mutates {@link #WEARERS} mid-sweep. */
    private static final List<LivingEntity> SWEEP_BUFFER = new ArrayList<>();

    private DecorationEffectDispatcher() {}

    public static void register() {
        ServerEntityEvents.ENTITY_LOAD.register((entity, level) -> {
            if (entity instanceof LivingEntity wearer && isDecorated(wearer)) {
                WEARERS.add(wearer);
            }
        });
        ServerEntityEvents.ENTITY_UNLOAD.register((entity, level) -> {
            if (entity instanceof LivingEntity wearer) {
                WEARERS.remove(wearer);
            }
        });
        ServerEntityEvents.EQUIPMENT_CHANGE.register(DecorationEffectDispatcher::onEquipmentChange);
        ServerTickEvents.END_SERVER_TICK.register(server -> tickWearers());
        ServerLifecycleEvents.SERVER_STOPPED.register(server -> WEARERS.clear());

        ServerLivingEntityEvents.ALLOW_DAMAGE.register((entity, source, amount) ->
            // The first effect to refuse wins, and the rest are not asked - a dodge that has already
            // moved its wearer out of the way has settled the question.
            !anyWorn(entity, DecorationEffect.Damage.class,
                (effect, context) -> !effect.allowDamage(context, source, amount)));
        ServerLivingEntityEvents.AFTER_DAMAGE.register((entity, source, amount, dealt, blocked) ->
            forEachWorn(entity, DecorationEffect.Damage.class,
                (effect, context) -> effect.afterDamage(context, source, amount, dealt, blocked)));

        // Deliberately NOT gated on the server: vanilla asks LivingEntity.canGlide on both sides, and
        // a client that answers "no" never asks to take off in the first place. See the note on
        // ArmorDecoration.DIRECT_STREAM_CODEC for why the client is in a position to answer at all.
        EntityElytraEvents.CUSTOM.register((entity, tickElytra) ->
            anyWorn(entity, DecorationEffect.Gliding.class,
                (effect, context) -> effect.allowsGliding(context)));
    }

    // ---- Traversal ------------------------------------------------------------------------------

    /**
     * Runs {@code action} for every worn effect implementing {@code hook}.
     *
     * <p>Public because it is the honest way for another mod to ask what an entity is wearing that
     * does X, without re-deriving the walk from equipment slot to socket to part - including the
     * detail that a socket riding on the wrong piece is skipped rather than honoured.
     */
    public static <T extends DecorationEffect> void forEachWorn(
        final LivingEntity wearer,
        final Class<T> hook,
        final BiConsumer<T, DecorationEffectContext> action
    ) {
        anyWorn(wearer, hook, (effect, context) -> {
            action.accept(effect, context);
            return false;
        });
    }

    /** As {@link #forEachWorn}, but stops at the first effect whose test passes. */
    public static <T extends DecorationEffect> boolean anyWorn(
        final LivingEntity wearer,
        final Class<T> hook,
        final BiPredicate<T, DecorationEffectContext> test
    ) {
        for (final EquipmentSlot slot : ARMOR_SLOTS) {
            if (forStack(wearer, slot, wearer.getItemBySlot(slot), hook, test)) {
                return true;
            }
        }
        return false;
    }

    /**
     * The whole traversal, for one piece.
     *
     * <p>Taking the stack as an argument rather than reading it off the entity is what lets equipment
     * changes run the same walk over the piece being taken OFF, which is how attribute modifiers get
     * removed by exactly the code that added them.
     */
    private static <T extends DecorationEffect> boolean forStack(
        final LivingEntity wearer,
        final EquipmentSlot slot,
        final ItemStack stack,
        final Class<T> hook,
        final BiPredicate<T, DecorationEffectContext> test
    ) {
        if (stack.isEmpty()) {
            return false;
        }
        final ArmorDecorations decorations = stack.get(ModDataComponents.DECORATIONS);
        if (decorations == null || decorations.isEmpty()) {
            return false;
        }
        for (final var mapping : decorations.entries().entrySet()) {
            final DecorationAnchor anchor = mapping.getKey();
            // The same guard the render layer keeps: a component can be written by a command, so a
            // socket that does not belong to this piece is possible. A crest in a boot draws nothing,
            // and by the same token it does nothing.
            if (anchor.slot() != slot) {
                continue;
            }
            final DecorationEntry entry = mapping.getValue();
            final List<DecorationEffect> effects = entry.decoration().value().effects();
            if (effects.isEmpty()) {
                continue;
            }
            DecorationEffectContext context = null;
            for (final DecorationEffect effect : effects) {
                if (!hook.isInstance(effect)) {
                    continue;
                }
                if (context == null) {
                    context = new DecorationEffectContext(wearer, anchor, stack, entry);
                }
                if (test.test(hook.cast(effect), context)) {
                    return true;
                }
            }
        }
        return false;
    }

    private static boolean isDecorated(final LivingEntity wearer) {
        for (final EquipmentSlot slot : ARMOR_SLOTS) {
            final ArmorDecorations decorations = wearer.getItemBySlot(slot).get(ModDataComponents.DECORATIONS);
            if (decorations != null && !decorations.isEmpty()) {
                return true;
            }
        }
        return false;
    }

    // ---- The hooks that need bookkeeping --------------------------------------------------------

    private static void tickWearers() {
        if (WEARERS.isEmpty()) {
            return;
        }
        SWEEP_BUFFER.addAll(WEARERS);
        for (final LivingEntity wearer : SWEEP_BUFFER) {
            if (wearer.isRemoved() || !wearer.isAlive() || !(wearer.level() instanceof ServerLevel)) {
                WEARERS.remove(wearer);
                continue;
            }
            forEachWorn(wearer, DecorationEffect.Ticking.class, DecorationEffect.Ticking::tick);
        }
        SWEEP_BUFFER.clear();
    }

    /**
     * Equipping and unequipping, which is also where attribute modifiers are reconciled.
     *
     * <p>The event hands over both stacks, which is the whole reason no side table is needed: the
     * modifiers to remove are recomputed from the piece coming off, and they land on the same ids
     * they were added under because {@link DecorationEffect.Attributes} is required to be a pure
     * function of the part. Modifiers are added TRANSIENTLY, so they are never written to disk and a
     * crash cannot leave a player permanently buffed by a part they no longer own - the equip that
     * happens when the entity next loads puts them back.
     */
    private static void onEquipmentChange(
        final LivingEntity entity,
        final EquipmentSlot slot,
        final ItemStack previous,
        final ItemStack current
    ) {
        if (!ARMOR_SLOTS.contains(slot) || !(entity.level() instanceof ServerLevel)) {
            return;
        }
        forStack(entity, slot, previous, DecorationEffect.Attributes.class, (effect, context) -> {
            effect.collectAttributes(context, (attribute, modifier) -> {
                final AttributeInstance instance = entity.getAttribute(attribute);
                if (instance != null) {
                    instance.removeModifier(scopedId(context.anchor(), modifier.id()));
                }
            });
            return false;
        });
        forStack(entity, slot, previous, DecorationEffect.Lifecycle.class, (effect, context) -> {
            effect.onUnequip(context);
            return false;
        });

        forStack(entity, slot, current, DecorationEffect.Attributes.class, (effect, context) -> {
            effect.collectAttributes(context, (attribute, modifier) -> {
                final AttributeInstance instance = entity.getAttribute(attribute);
                if (instance != null) {
                    final Identifier id = scopedId(context.anchor(), modifier.id());
                    instance.removeModifier(id);
                    instance.addTransientModifier(
                        new AttributeModifier(id, modifier.amount(), modifier.operation()));
                }
            });
            return false;
        });
        forStack(entity, slot, current, DecorationEffect.Lifecycle.class, (effect, context) -> {
            effect.onEquip(context);
            return false;
        });

        if (isDecorated(entity)) {
            WEARERS.add(entity);
        } else {
            WEARERS.remove(entity);
        }
    }

    /**
     * The id a modifier is actually applied under: the effect's own id, prefixed with the socket.
     *
     * <p>Attribute modifiers are keyed by id, so one part worn in two sockets - a spike that lists
     * both {@code crest} and {@code spurs} - would otherwise contribute one modifier that silently
     * replaced itself instead of two that stack. Prefixing is done here rather than left to the
     * effect so that a third-party effect gets the same guarantee without having to know about it.
     */
    private static Identifier scopedId(final DecorationAnchor anchor, final Identifier base) {
        return Identifier.fromNamespaceAndPath(
            base.getNamespace(), anchor.getSerializedName() + "/" + base.getPath());
    }
}
