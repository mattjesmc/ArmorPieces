package com.mattjesmc.armorpieces.decoration.effect.builtin;

import com.mattjesmc.armorpieces.decoration.effect.DecorationEffect;
import com.mattjesmc.armorpieces.decoration.effect.DecorationEffectContext;
import com.mattjesmc.armorpieces.decoration.effect.MaterialValue;
import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.Holder;
import net.minecraft.network.chat.Component;
import net.minecraft.util.ExtraCodecs;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.equipment.trim.TrimMaterial;
import net.minecraft.world.level.gameevent.GameEvent;

/**
 * {@code armorpieces:glide} - the part lets its wearer fly, and makes them pay for it.
 *
 * <pre>{@code
 * { "type": "armorpieces:glide",
 *   "sink": 0.02,
 *   "wear_interval": 5 }
 * }</pre>
 *
 * <p>Two hooks, and the pairing is the point. {@link DecorationEffect.Gliding} grants the real thing:
 * vanilla's own launch, physics and rocket boosting, because this rides the same check an elytra
 * does rather than imitating it. {@link DecorationEffect.Ticking} is then what keeps a shoulder-wing
 * from being strictly better than the elytra it was cut from - {@code sink} is extra downward
 * acceleration every tick, which shortens a glide without touching how it steers, and
 * {@code wear_interval} is how often the piece takes a point of damage, against vanilla's twenty
 * ticks.
 *
 * <p>Defaults are chosen so an unconfigured entry is already a worse elytra rather than an equal one.
 * At {@code sink} 0.02 a glide loses height roughly twice as fast as vanilla's, and at
 * {@code wear_interval} 5 the piece wears four times as quickly.
 *
 * <p>The wear is spent on the decorated piece itself, whichever socket the part is in, so a back-worn
 * pair of wings consumes the chestplate carrying them. That is deliberate: the part is not a separate
 * item and cannot break separately, so what it costs has to be the armor's own durability.
 *
 * @param sink         blocks per tick per tick of extra downward pull while gliding. Zero leaves
 *                     vanilla's glide untouched; a plain number or one that scales with the material,
 *                     see {@link MaterialValue}.
 * @param wearInterval ticks between one point of damage to the piece. Zero never wears it.
 */
public record GlideEffect(MaterialValue<Double> sink, int wearInterval) implements
    DecorationEffect.Gliding, DecorationEffect.Ticking {
    public static final MapCodec<GlideEffect> CODEC = RecordCodecBuilder.mapCodec(
        i -> i.group(
                MaterialValue.codec(Codec.doubleRange(0.0, 1.0))
                    .optionalFieldOf("sink", MaterialValue.of(0.02))
                    .forGetter(GlideEffect::sink),
                ExtraCodecs.NON_NEGATIVE_INT.optionalFieldOf("wear_interval", 5).forGetter(GlideEffect::wearInterval)
            )
            .apply(i, GlideEffect::new)
    );

    @Override
    public MapCodec<? extends DecorationEffect> codec() {
        return CODEC;
    }

    /**
     * Runs on both sides, and is a pure question about equipment - which is what lets the client
     * answer it. A worn-out piece stops granting flight one point before it breaks, matching the rule
     * vanilla applies to a damaged elytra.
     */
    @Override
    public boolean allowsGliding(final DecorationEffectContext context) {
        return !context.stack().nextDamageWillBreak();
    }

    /** Nothing about a glider reduces to a number a tooltip could show, so it says what it is. */
    @Override
    public Component description(final Holder<TrimMaterial> material) {
        return Component.translatable("effect.armorpieces.glide");
    }

    @Override
    public void tick(final DecorationEffectContext context) {
        final LivingEntity wearer = context.wearer();
        if (!wearer.isFallFlying()) {
            return;
        }
        final double sink = this.sink.get(context.material());
        if (sink > 0.0) {
            wearer.setDeltaMovement(wearer.getDeltaMovement().add(0.0, -sink, 0.0));
        }
        if (this.wearInterval > 0 && wearer.tickCount % this.wearInterval == 0) {
            context.stack().hurtAndBreak(1, wearer, context.slot());
            // The same game event vanilla fires for an elytra, so sculk sensors and wardens hear a
            // glider whatever it is bolted to.
            wearer.gameEvent(GameEvent.ELYTRA_GLIDE);
        }
    }
}
