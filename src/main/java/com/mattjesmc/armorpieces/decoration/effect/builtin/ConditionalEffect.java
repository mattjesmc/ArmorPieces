package com.mattjesmc.armorpieces.decoration.effect.builtin;

import com.mattjesmc.armorpieces.decoration.effect.DecorationEffect;
import com.mattjesmc.armorpieces.decoration.effect.DecorationEffectContext;
import com.mattjesmc.armorpieces.decoration.fitting.FittingPredicate;
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
 * {@code armorpieces:if_fitting} - another effect, run only while a fitting holds what it asks for.
 *
 * <pre>{@code
 * { "type": "armorpieces:if_fitting",
 *   "if": { "fitting": "armorpieces:gemstone", "material": "minecraft:emerald" },
 *   "then": { "type": "armorpieces:mob_effect", "effect": "minecraft:hero_of_the_village" } }
 * }</pre>
 *
 * <p>This is where a gem stops being paint. An emerald in the circlet that does something an emerald
 * circlet does not is one of these wrapped around any other effect, including another of these -
 * "if emerald AND if red inlay" nests. It implements every hook and forwards each to the inner effect
 * when the condition holds, so the inner effect neither knows nor cares that it is gated.
 *
 * <p>Sound for {@link Attributes} because the condition is a pure function of the entry, which is
 * what that hook demands: a fitting changes only at the smithing table, which replaces the stack and
 * so re-runs the equipment reconcile. {@link WearerConditionEffect} is the same shape asking about the
 * WEARER instead, and is the one that had to grow rules about which hooks it may reach; this one has
 * none, because what it tests cannot change without the stack changing.
 */
public record ConditionalEffect(FittingPredicate condition, DecorationEffect effect) implements
    DecorationEffect.Ticking,
    DecorationEffect.Damage,
    DecorationEffect.Attributes,
    DecorationEffect.Gliding,
    DecorationEffect.Lifecycle {

    public static final MapCodec<ConditionalEffect> CODEC = RecordCodecBuilder.mapCodec(
        i -> i.group(
                FittingPredicate.CODEC.fieldOf("if").forGetter(ConditionalEffect::condition),
                DecorationEffect.CODEC.fieldOf("then").forGetter(ConditionalEffect::effect)
            )
            .apply(i, ConditionalEffect::new)
    );

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
        return Component.translatable("effect.armorpieces.if_fitting", this.effect.description(material));
    }

    private boolean holds(final DecorationEffectContext context) {
        return this.condition.test(context.entry());
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

    /** What the fitting could have granted, so that the reconcile can take it back off again. */
    @Override
    public void collectPossibleAttributes(
        final DecorationEffectContext context,
        final BiConsumer<Holder<Attribute>, AttributeModifier> out
    ) {
        if (this.effect instanceof Attributes attributes) {
            attributes.collectPossibleAttributes(context, out);
        }
    }

    @Override
    public boolean allowsGliding(final DecorationEffectContext context) {
        return this.effect instanceof Gliding gliding && this.holds(context) && gliding.allowsGliding(context);
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
