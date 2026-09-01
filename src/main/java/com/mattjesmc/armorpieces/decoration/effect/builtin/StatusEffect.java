package com.mattjesmc.armorpieces.decoration.effect.builtin;

import com.mattjesmc.armorpieces.decoration.effect.DecorationEffect;
import com.mattjesmc.armorpieces.decoration.effect.DecorationEffectContext;
import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.util.ExtraCodecs;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;

/**
 * {@code armorpieces:mob_effect} - a status effect held for as long as the part is worn.
 *
 * <pre>{@code
 * { "type": "armorpieces:mob_effect",
 *   "effect": "minecraft:night_vision",
 *   "amplifier": 0 }
 * }</pre>
 *
 * <p>Refreshed on a cadence rather than granted infinitely, which is how conduit power and a beacon
 * behave and is what makes taking the armor off actually end the effect: the instance is short, and
 * it simply stops being renewed. The cost of that is a visible tail of a couple of seconds after
 * unequipping, which is the same tail a beacon has and reads as the effect fading rather than as a
 * bug.
 *
 * <p>Adding goes through {@code addEffect}, so a stronger instance from a potion is never trampled by
 * a weaker one from a part - vanilla's own precedence rules decide, and this behaves like every other
 * source of the same effect.
 *
 * @param ambient        true by default, so the wearer gets the faded HUD border a beacon gives
 *                       rather than the solid one a potion gives.
 * @param showParticles  false by default: a permanent effect that spat particles every tick would be
 *                       unwearable.
 */
public record StatusEffect(
    Holder<MobEffect> effect,
    int amplifier,
    boolean ambient,
    boolean showParticles,
    boolean showIcon
) implements DecorationEffect.Ticking {
    /** How long each granted instance lasts, and how often it is renewed. Three seconds, renewed every one. */
    private static final int DURATION_TICKS = 60;
    private static final int REFRESH_TICKS = 20;

    public static final MapCodec<StatusEffect> CODEC = RecordCodecBuilder.mapCodec(
        i -> i.group(
                BuiltInRegistries.MOB_EFFECT.holderByNameCodec().fieldOf("effect").forGetter(StatusEffect::effect),
                ExtraCodecs.intRange(0, 255).optionalFieldOf("amplifier", 0).forGetter(StatusEffect::amplifier),
                Codec.BOOL.optionalFieldOf("ambient", true).forGetter(StatusEffect::ambient),
                Codec.BOOL.optionalFieldOf("show_particles", false).forGetter(StatusEffect::showParticles),
                Codec.BOOL.optionalFieldOf("show_icon", true).forGetter(StatusEffect::showIcon)
            )
            .apply(i, StatusEffect::new)
    );

    @Override
    public MapCodec<? extends DecorationEffect> codec() {
        return CODEC;
    }

    @Override
    public void tick(final DecorationEffectContext context) {
        if (context.wearer().tickCount % REFRESH_TICKS != 0) {
            return;
        }
        context.wearer().addEffect(new MobEffectInstance(
            this.effect, DURATION_TICKS, this.amplifier, this.ambient, this.showParticles, this.showIcon));
    }
}
