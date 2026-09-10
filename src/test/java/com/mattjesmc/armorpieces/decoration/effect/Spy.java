package com.mattjesmc.armorpieces.decoration.effect;

import com.mojang.serialization.MapCodec;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.network.chat.Component;
import net.minecraft.core.Holder;
import net.minecraft.resources.Identifier;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import java.util.function.BiConsumer;
import net.minecraft.world.item.equipment.trim.TrimMaterial;

/**
 * An effect that does nothing but remember being asked.
 *
 * <p>Every rule the dispatcher has is about WHICH effect is reached, with which context, and in what
 * order - never about what the effect then does. So the effects here have no behaviour at all: each
 * implements exactly one hook, records the contexts it was handed, and answers a verdict the test
 * sets. One hook each is the point, since "an effect that only reacts to damage is never visited on
 * the tick path" is a rule that an effect implementing everything could not show.
 *
 * <p>None of these is registered as an effect TYPE, and none needs to be: a type is what turns JSON
 * into an instance, and these are built in Java. {@link #codec()} therefore answers with a codec
 * nothing will ever read, and {@link #description(Holder)} is overridden so the default - which asks
 * the registry what this effect is called - is never reached.
 */
abstract class Spy implements DecorationEffect {
    /** Every context this effect was given, in the order it was given them. */
    final List<DecorationEffectContext> seen = new ArrayList<>();

    /** How many times it was reached. */
    int count() {
        return this.seen.size();
    }

    /** The last context it was given - what a test about the context itself reads. */
    DecorationEffectContext last() {
        if (this.seen.isEmpty()) {
            throw new AssertionError("this effect was never reached");
        }
        return this.seen.getLast();
    }

    @Override
    public MapCodec<? extends DecorationEffect> codec() {
        return MapCodec.unit(this);
    }

    @Override
    public Component description(final Holder<TrimMaterial> material) {
        return Component.literal(this.getClass().getSimpleName());
    }

    /** Runs on the tick, and nothing else. */
    static final class Tick extends Spy implements DecorationEffect.Ticking {
        @Override
        public void tick(final DecorationEffectContext context) {
            this.seen.add(context);
        }
    }

    /** Sees damage, and refuses it or does not, as the test says. */
    static final class Hit extends Spy implements DecorationEffect.Damage {
        private final boolean allow;

        Hit(final boolean allow) {
            this.allow = allow;
        }

        @Override
        public boolean allowDamage(
            final DecorationEffectContext context, final DamageSource source, final float amount
        ) {
            this.seen.add(context);
            return this.allow;
        }

        @Override
        public void afterDamage(
            final DecorationEffectContext context,
            final DamageSource source,
            final float amount,
            final float dealt,
            final boolean blocked
        ) {
            this.seen.add(context);
        }
    }

    /** Lets its wearer glide, or says it would if it could. */
    static final class Wings extends Spy implements DecorationEffect.Gliding {
        private final boolean allows;

        Wings(final boolean allows) {
            this.allows = allows;
        }

        @Override
        public boolean allowsGliding(final DecorationEffectContext context) {
            this.seen.add(context);
            return this.allows;
        }
    }

    /**
     * An attribute effect whose PRESENCE varies, and which can be switched between one reconcile and
     * the next without the item changing.
     *
     * <p>Which is the shape of every gate: {@code if_fitting} and {@code if_wearer} both offer a
     * modifier through {@code collectPossibleAttributes} whether or not they are granting it, so that
     * the reconcile can take back what has just stopped applying. A real gate here would not do -
     * {@code if_fitting} reads the item, so its answer cannot change while the item does not, and
     * {@code if_wearer} cannot be true at all without a server. This one flips on command, which is
     * exactly the moment the rule exists for: the wearer picked up a sword, and the claws stopped
     * biting.
     */
    static final class Gated extends Spy implements DecorationEffect.Attributes {
        /** The id the modifier is offered under, before the dispatcher scopes it to a socket. */
        static final Identifier ID = Identifier.fromNamespaceAndPath("armorpieces", "gated");

        /** Whether the condition holds right now. */
        boolean granting = true;

        private final double amount;

        Gated(final double amount) {
            this.amount = amount;
        }

        private Holder<Attribute> attribute() {
            // Fully qualified: inside an effect, `Attributes` is the HOOK, not vanilla's list of them.
            return net.minecraft.world.entity.ai.attributes.Attributes.ARMOR;
        }

        @Override
        public void collectAttributes(
            final DecorationEffectContext context, final BiConsumer<Holder<Attribute>, AttributeModifier> out
        ) {
            this.seen.add(context);
            if (this.granting) {
                out.accept(this.attribute(),
                    new AttributeModifier(ID, this.amount, AttributeModifier.Operation.ADD_VALUE));
            }
        }

        @Override
        public void collectPossibleAttributes(
            final DecorationEffectContext context, final BiConsumer<Holder<Attribute>, AttributeModifier> out
        ) {
            out.accept(this.attribute(),
                new AttributeModifier(ID, this.amount, AttributeModifier.Operation.ADD_VALUE));
        }
    }

    /** Notices being put on and taken off, keeping the two apart. */
    static final class Worn extends Spy implements DecorationEffect.Lifecycle {
        final List<String> calls = new ArrayList<>();

        @Override
        public void onEquip(final DecorationEffectContext context) {
            this.seen.add(context);
            this.calls.add("equip");
        }

        @Override
        public void onUnequip(final DecorationEffectContext context) {
            this.seen.add(context);
            this.calls.add("unequip");
        }
    }
}
