package com.mattjesmc.armorpieces.decoration.effect.builtin;

import com.mattjesmc.armorpieces.decoration.effect.DecorationEffect;
import com.mattjesmc.armorpieces.decoration.effect.DecorationEffectContext;
import com.mattjesmc.armorpieces.decoration.effect.WearerPredicate;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.function.BiConsumer;
import net.minecraft.core.Holder;
import net.minecraft.network.chat.Component;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.item.equipment.trim.TrimMaterial;

/**
 * {@code armorpieces:if_wearer} - another effect, run only while the WEARER answers a question.
 *
 * <pre>{@code
 * { "type": "armorpieces:if_wearer",
 *   "if": { "equipment": { "mainhand": { "items": "minecraft:air" } } },
 *   "then": { "type": "armorpieces:attribute", "id": "armorpieces:claws_bite",
 *             "attribute": "minecraft:attack_damage", "amount": 1.0 } }
 * }</pre>
 *
 * <p>The sibling of {@link ConditionalEffect}, and the two say different kinds of thing:
 * {@code if_fitting} asks about the PART - the gem set in the circlet - and this asks about the
 * person wearing it. Between them a part can be made to matter without any Java at all. They nest in
 * either order, because each wraps any effect including the other.
 *
 * <h2>The two tiers, and why the second is refused rather than allowed to half-work</h2>
 *
 * <p>{@link DecorationEffect.Attributes} is applied on equipment change and then left in place until
 * the next one. A modifier that depended on where its wearer was standing would therefore be computed
 * once, in the place they happened to be standing, and stay that way - wrong, and invisibly so. There
 * are exactly two honest answers to that, and this takes both:
 *
 * <ul>
 *   <li><b>Equipment conditions are made legal by widening the reconcile.</b> The dispatcher now
 *       re-runs the armor slots' attribute pass when a HAND changes too, so a condition about what
 *       the wearer holds or wears is reconciled at every moment it can change. The rule the hook
 *       documents is unbroken: still pure, now over the part and the wearer's equipment.</li>
 *   <li><b>Everything else is refused at load</b> when it reaches an attribute effect, with a message
 *       naming the tests that were the problem. It stays legal on {@code Ticking}, {@code Damage} and
 *       {@code Lifecycle}, which are re-asked at the moment they run and so cannot go stale.</li>
 * </ul>
 *
 * <p>{@link DecorationEffect.Gliding} is refused outright, for a different reason: vanilla asks
 * {@code canGlide} on the client as well, and vanilla's entity predicate needs a server level to
 * evaluate. A gated glider would answer "no" on the client and never take off, so the file is refused
 * instead. {@code if_fitting} has no such problem - a fitting is in the component the client already
 * has - and remains the way to gate a glider.
 */
public record WearerConditionEffect(WearerPredicate condition, DecorationEffect effect) implements
    DecorationEffect.Ticking,
    DecorationEffect.Damage,
    DecorationEffect.Attributes,
    DecorationEffect.Gliding,
    DecorationEffect.Lifecycle {

    public static final MapCodec<WearerConditionEffect> CODEC = RecordCodecBuilder.<WearerConditionEffect>mapCodec(
        i -> i.group(
                WearerPredicate.CODEC.fieldOf("if").forGetter(WearerConditionEffect::condition),
                DecorationEffect.CODEC.fieldOf("then").forGetter(WearerConditionEffect::effect)
            )
            .apply(i, WearerConditionEffect::new)
    ).validate(WearerConditionEffect::validate);

    /**
     * The load-time rules above. A refusal here fails the part file, which is the point: a condition
     * that cannot be honoured should stop the pack rather than silently do half of what it says.
     */
    private static DataResult<WearerConditionEffect> validate(final WearerConditionEffect gate) {
        if (gate.effect.reaches(Gliding.class)) {
            return DataResult.error(() ->
                "armorpieces:if_wearer cannot gate a gliding effect: gliding is asked on the client too, "
                    + "where an entity predicate cannot be evaluated. Use armorpieces:if_fitting, "
                    + "which asks about the part rather than the world.");
        }
        if (gate.effect.reaches(Attributes.class) && !gate.condition.isEquipmentOnly()) {
            return DataResult.error(() ->
                "armorpieces:if_wearer may only test equipment"
                    + " when it gates an attribute effect, because attribute modifiers are reconciled on "
                    + "equipment change and would otherwise go stale; found "
                    + String.join(", ", gate.condition.beyondEquipment()));
        }
        return DataResult.success(gate);
    }

    @Override
    public MapCodec<? extends DecorationEffect> codec() {
        return CODEC;
    }

    /** A gate implements every hook; what it can actually reach is whatever it wraps. */
    @Override
    public boolean reaches(final Class<? extends DecorationEffect> hook) {
        return this.effect.reaches(hook);
    }

    @Override
    public boolean applies(final DecorationEffectContext context) {
        return this.holds(context) && this.effect.applies(context);
    }

    @Override
    public Component description(final Holder<TrimMaterial> material) {
        return Component.translatable("effect.armorpieces.if_wearer", this.effect.description(material));
    }

    private boolean holds(final DecorationEffectContext context) {
        return this.condition.test(context);
    }

    @Override
    public void tick(final DecorationEffectContext context) {
        if (this.effect instanceof Ticking ticking && this.holds(context)) {
            ticking.tick(context);
        }
    }

    @Override
    public boolean allowDamage(final DecorationEffectContext context, final DamageSource source, final float amount) {
        return !(this.effect instanceof Damage damage && this.holds(context))
            || damage.allowDamage(context, source, amount);
    }

    @Override
    public void afterDamage(
        final DecorationEffectContext context,
        final DamageSource source,
        final float amount,
        final float dealt,
        final boolean blocked
    ) {
        if (this.effect instanceof Damage damage && this.holds(context)) {
            damage.afterDamage(context, source, amount, dealt, blocked);
        }
    }

    @Override
    public void collectAttributes(
        final DecorationEffectContext context,
        final BiConsumer<Holder<Attribute>, AttributeModifier> out
    ) {
        if (this.effect instanceof Attributes attributes && this.holds(context)) {
            attributes.collectAttributes(context, out);
        }
    }

    /** What the condition could have granted, so that the reconcile can take it back off again. */
    @Override
    public void collectPossibleAttributes(
        final DecorationEffectContext context,
        final BiConsumer<Holder<Attribute>, AttributeModifier> out
    ) {
        if (this.effect instanceof Attributes attributes) {
            attributes.collectPossibleAttributes(context, out);
        }
    }

    /** Refused at load, so this is never reached; answering false is the safe reading regardless. */
    @Override
    public boolean allowsGliding(final DecorationEffectContext context) {
        return false;
    }

    @Override
    public void onEquip(final DecorationEffectContext context) {
        if (this.effect instanceof Lifecycle lifecycle && this.holds(context)) {
            lifecycle.onEquip(context);
        }
    }

    @Override
    public void onUnequip(final DecorationEffectContext context) {
        if (this.effect instanceof Lifecycle lifecycle && this.holds(context)) {
            lifecycle.onUnequip(context);
        }
    }
}
