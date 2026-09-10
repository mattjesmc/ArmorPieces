package com.mattjesmc.armorpieces.decoration.effect;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonParser;
import com.mattjesmc.armorpieces.GameBootstrap;
import com.mattjesmc.armorpieces.data.ShippedData;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mattjesmc.armorpieces.decoration.effect.builtin.ConditionalEffect;
import com.mattjesmc.armorpieces.decoration.effect.builtin.WearerConditionEffect;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.decoration.fitting.FittingPredicate;
import com.mattjesmc.armorpieces.decoration.fitting.builtin.MaterialFitting;
import com.mojang.serialization.JsonOps;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import net.minecraft.core.Holder;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.contents.TranslatableContents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * The two conditions a part can carry, and the one thing they are hard to get right about.
 *
 * <p>A gate has to implement EVERY hook, because it cannot know which one the effect it wraps needs -
 * so {@code if_fitting} and {@code if_wearer} are each ten forwarding methods written by hand, and a
 * hook whose forwarding is subtly wrong is invisible: the part still loads, still describes itself,
 * still reaches the right hook, and simply does the wrong thing in play. The two that are easiest to
 * get backwards are here by name. {@code allowDamage} is a VETO - a gate that does not hold must
 * answer "allowed", not "refused", or a condition nobody met would make its wearer invulnerable - and
 * {@code allowsGliding} is a GRANT, where the same non-holding gate must answer no.
 *
 * <p>{@link WearerConditionEffect} additionally has a reading rather than a rule: vanilla's entity
 * predicate needs a server level, so off a server the condition is false and the effect it wraps does
 * nothing. That is why it may not gate a glider - the client asks that question too - and it is what
 * a test JVM sees, so it is asserted here as the behaviour it is.
 *
 * <p>The codecs, the load-time refusals and {@code reaches} are {@code DecorationEffectsTest}'s; what
 * is asserted here is what the gates DO once they are loaded.
 */
class EffectGateTest {
    /**
     * A gate reads neither the damage source nor the amount - it forwards them - so nothing here
     * builds one. A damage type is a datapack registry this fixture does not load, and a
     * {@link NullPointerException} out of this would be a finding rather than a flaw in the test.
     */
    private static final DamageSource NO_SOURCE = null;

    @BeforeAll
    static void world() {
        GameBootstrap.content();
    }

    // ---- if_fitting --------------------------------------------------------------------------

    @Test
    void aFittingGateForwardsEveryHookWhileItHolds() {
        final Spy.Tick tick = new Spy.Tick();
        final Spy.Hit hit = new Spy.Hit(true);
        final Spy.Wings wings = new Spy.Wings(true);
        final Spy.Worn worn = new Spy.Worn();
        final DecorationEffectContext context = withGem();

        assertTrue(gate(tick).applies(context), "a gate whose fitting holds a gem says it is not applying");
        gate(tick).tick(context);
        assertEquals(1, tick.count(), "the tick was not forwarded through a gate that holds");
        assertTrue(gate(hit).allowDamage(context, NO_SOURCE, 1.0F),
            "the wrapped effect allowed the damage and the gate refused it");
        assertEquals(1, hit.count(), "the damage question was not forwarded");
        assertTrue(gate(wings).allowsGliding(context), "the wrapped glider was not heard through the gate");
        gate(worn).onEquip(context);
        gate(worn).onUnequip(context);
        assertEquals(List.of("equip", "unequip"), worn.calls, "the lifecycle was not forwarded");
    }

    @Test
    void aFittingGateForwardsNothingWhileItDoesNotHold() {
        final Spy.Tick tick = new Spy.Tick();
        final Spy.Hit hit = new Spy.Hit(false);
        final Spy.Wings wings = new Spy.Wings(true);
        final Spy.Worn worn = new Spy.Worn();
        final DecorationEffectContext context = withoutGem();

        assertFalse(gate(tick).applies(context), "a gate with an empty fitting claims to be applying");
        gate(tick).tick(context);
        assertEquals(0, tick.count(), "the tick was forwarded through a gate that does not hold");
        gate(worn).onEquip(context);
        gate(worn).onUnequip(context);
        assertEquals(List.of(), worn.calls, "the lifecycle was forwarded through a gate that does not hold");
        assertEquals(0, wings.count(), "nothing should have asked the glider anything yet");
    }

    /**
     * Damage is a veto: a condition nobody has met must let the blow through, and the effect that
     * would have stopped it is not even asked.
     */
    @Test
    void aFittingGateThatDoesNotHoldAllowsTheDamage() {
        final Spy.Hit dodge = new Spy.Hit(false);
        final ConditionalEffect gate = gate(dodge);

        assertFalse(gate.allowDamage(withGem(), NO_SOURCE, 4.0F),
            "the gem was in and the dodge did not stop the blow");
        assertTrue(gate.allowDamage(withoutGem(), NO_SOURCE, 4.0F),
            "an unmet condition made its wearer invulnerable");
        assertEquals(1, dodge.count(), "the effect behind an unmet condition was asked anyway");
    }

    /** Gliding is a grant: the same unmet condition must answer no. */
    @Test
    void aFittingGateThatDoesNotHoldRefusesToGlide() {
        final Spy.Wings wings = new Spy.Wings(true);
        final ConditionalEffect gate = gate(wings);

        assertTrue(gate.allowsGliding(withGem()), "the gem was in and the part would not fly");
        assertFalse(gate.allowsGliding(withoutGem()), "an unmet condition granted flight");
        assertEquals(1, wings.count(), "the glider behind an unmet condition was asked anyway");
    }

    /**
     * A gate over an effect that does not implement the hook being asked forwards nothing and says
     * the harmless thing - which is what lets a gate be written once for every hook there is.
     */
    @Test
    void aGateOverAnEffectThatDoesNotReachTheHookAnswersHarmlessly() {
        final ConditionalEffect gate = gate(new Spy.Tick());
        final DecorationEffectContext context = withGem();

        assertTrue(gate.allowDamage(context, NO_SOURCE, 1.0F),
            "a gate over a ticking effect refused a blow");
        assertFalse(gate.allowsGliding(context), "a gate over a ticking effect granted flight");
        gate.onEquip(context);
        gate.onUnequip(context);
    }

    /** The line a player reads is the gate's own, wrapped around the line of what it gates. */
    @Test
    void aGateDescribesItselfAroundWhatItGates() {
        final Component line = gate(new Spy.Tick()).description(Wearer.material("minecraft:iron"));

        assertTrue(line.getContents() instanceof TranslatableContents,
            "the gate's line is not a translatable one");
        assertEquals("effect.armorpieces.if_fitting",
            ((TranslatableContents) line.getContents()).getKey(), "the gate's line lost its own key");
        assertEquals(1, ((TranslatableContents) line.getContents()).getArgs().length,
            "the gate's line does not carry the line of what it gates");
    }

    // ---- if_wearer ---------------------------------------------------------------------------

    /**
     * Off a server the condition is false, so nothing behind it runs - and the effect is not asked,
     * rather than asked and ignored.
     */
    @Test
    void aWearerGateHoldsNothingWithoutAServer() {
        final Spy.Tick tick = new Spy.Tick();
        final Spy.Hit dodge = new Spy.Hit(false);
        final Spy.Worn worn = new Spy.Worn();
        final DecorationEffectContext context = withGem();

        assertFalse(wearerGate(tick).applies(context), "a wearer condition claims to apply with no server");
        wearerGate(tick).tick(context);
        assertEquals(0, tick.count(), "a wearer condition ran its effect with nothing to evaluate it");
        assertTrue(wearerGate(dodge).allowDamage(context, NO_SOURCE, 1.0F),
            "a wearer condition that cannot be evaluated stopped a blow");
        wearerGate(worn).onEquip(context);
        assertEquals(List.of(), worn.calls, "a wearer condition announced an equip it could not judge");
    }

    /**
     * And it never grants gliding, whatever it wraps: the load-time rule refuses such a part, and the
     * answer here is the safe reading of the same thing rather than a second copy of the rule.
     */
    @Test
    void aWearerGateNeverGrantsGliding() {
        final Spy.Wings wings = new Spy.Wings(true);

        assertFalse(wearerGate(wings).allowsGliding(withGem()),
            "a wearer condition granted flight on a side that cannot evaluate it");
        assertEquals(0, wings.count(), "the glider was asked before the refusal");
    }

    // ---- the fixtures ------------------------------------------------------------------------

    /** {@code if_fitting}: is there anything at all in the gemstone fitting? */
    private static ConditionalEffect gate(final DecorationEffect effect) {
        return new ConditionalEffect(
            new FittingPredicate(gemstone(), Optional.empty(), Optional.empty()), effect);
    }

    /** {@code if_wearer}: is the wearer's main hand empty? - the shipped claws' own condition. */
    private static WearerConditionEffect wearerGate(final DecorationEffect effect) {
        final WearerPredicate barehanded = WearerPredicate.CODEC
            .parse(ShippedData.mod().full().createSerializationContext(JsonOps.INSTANCE),
                JsonParser.parseString("{\"equipment\": {\"mainhand\": {\"items\": \"minecraft:air\"}}}"))
            .getOrThrow();
        return new WearerConditionEffect(barehanded, effect);
    }

    private static Holder<Fitting> gemstone() {
        return Wearer.fitting("gemstone");
    }

    /** The occasion, with an emerald in the fitting the gate looks in. */
    private static DecorationEffectContext withGem() {
        return context(entry().withFitting(gemstone(), new MaterialFitting.Value(Wearer.material("minecraft:emerald"))));
    }

    /** The same occasion with the fitting empty. */
    private static DecorationEffectContext withoutGem() {
        return context(entry());
    }

    private static DecorationEntry entry() {
        final Holder<ArmorDecoration> circlet =
            Wearer.part(Set.of(DecorationAnchor.BROW), List.of(gemstone()));
        return new DecorationEntry(Wearer.material("minecraft:gold"), circlet);
    }

    private static DecorationEffectContext context(final DecorationEntry entry) {
        final ItemStack helmet = Wearer.piece(DecorationAnchor.BROW, entry);
        final Wearer wearer = Wearer.zombie().wearing(EquipmentSlot.HEAD, helmet);
        return new DecorationEffectContext(wearer.entity(), DecorationAnchor.BROW, helmet, entry);
    }
}
