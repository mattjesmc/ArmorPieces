package com.mattjesmc.armorpieces.decoration.effect.builtin;

import com.mattjesmc.armorpieces.decoration.effect.DecorationEffect;
import com.mattjesmc.armorpieces.decoration.effect.DecorationEffectContext;
import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.tags.TagKey;
import net.minecraft.util.ExtraCodecs;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.entity.LivingEntity;

/**
 * {@code armorpieces:blink} - a chance to be somewhere else when the blow lands.
 *
 * <pre>{@code
 * { "type": "armorpieces:blink",
 *   "chance": 0.25,
 *   "radius": 6.0,
 *   "damage_types": "minecraft:is_projectile" }
 * }</pre>
 *
 * <p>The worked example for {@link DecorationEffect.Damage}, and the one that shows why that hook is
 * a veto rather than a number: the arrow is not softened, it misses, because the thing it was aimed
 * at is eight blocks away by the time it arrives. Rolling the chance BEFORE looking for a landing
 * spot matters - if a failed search also consumed the roll, the effect would quietly get weaker in
 * exactly the cramped places a player most wants it.
 *
 * <p>Stateless on purpose. No cooldown is tracked, so nothing has to be attached to the entity, saved
 * or cleaned up; the chance alone decides, and a part that wants to dodge rarely says so with a low
 * number. {@link #radius} is the half-width of the box searched, not a guaranteed distance -
 * {@code randomTeleport} refuses unsafe destinations, so a blink underground lands short or does not
 * happen at all.
 *
 * @param damageTypes which damage this answers. Defaults to projectiles, which is the reading of
 *                    "dodge" that makes sense: you cannot sidestep drowning.
 */
public record BlinkEffect(
    float chance,
    double radius,
    TagKey<DamageType> damageTypes,
    int attempts
) implements DecorationEffect.Damage {
    public static final MapCodec<BlinkEffect> CODEC = RecordCodecBuilder.mapCodec(
        i -> i.group(
                ExtraCodecs.floatRange(0.0F, 1.0F).optionalFieldOf("chance", 0.25F).forGetter(BlinkEffect::chance),
                Codec.doubleRange(1.0, 64.0).optionalFieldOf("radius", 8.0).forGetter(BlinkEffect::radius),
                TagKey.codec(Registries.DAMAGE_TYPE)
                    .optionalFieldOf("damage_types", DamageTypeTags.IS_PROJECTILE)
                    .forGetter(BlinkEffect::damageTypes),
                ExtraCodecs.intRange(1, 64).optionalFieldOf("attempts", 16).forGetter(BlinkEffect::attempts)
            )
            .apply(i, BlinkEffect::new)
    );

    @Override
    public MapCodec<? extends DecorationEffect> codec() {
        return CODEC;
    }

    @Override
    public boolean allowDamage(final DecorationEffectContext context, final DamageSource source, final float amount) {
        final ServerLevel level = context.serverLevel();
        if (level == null || !source.is(this.damageTypes)) {
            return true;
        }
        final RandomSource random = context.random();
        if (random.nextFloat() >= this.chance) {
            return true;
        }

        final LivingEntity wearer = context.wearer();
        final double fromX = wearer.getX();
        final double fromY = wearer.getY();
        final double fromZ = wearer.getZ();
        for (int attempt = 0; attempt < this.attempts; attempt++) {
            final double x = fromX + (random.nextDouble() - 0.5) * 2.0 * this.radius;
            final double z = fromZ + (random.nextDouble() - 0.5) * 2.0 * this.radius;
            // A shallower vertical spread than horizontal: a dodge should read as stepping aside, not
            // as being flung onto the roof. Clamped into the world so the search cannot waste an
            // attempt on a height that does not exist.
            final double y = Mth.clamp(
                fromY + (random.nextDouble() - 0.5) * 8.0, level.getMinY() + 1, level.getMaxY() - 1);
            if (wearer.randomTeleport(x, y, z, false)) {
                level.sendParticles(ParticleTypes.PORTAL, fromX, fromY + wearer.getBbHeight() / 2.0, fromZ,
                    32, 0.4, 0.6, 0.4, 0.0);
                level.sendParticles(ParticleTypes.PORTAL, wearer.getX(), wearer.getY() + wearer.getBbHeight() / 2.0,
                    wearer.getZ(), 32, 0.4, 0.6, 0.4, 0.0);
                level.playSound(null, fromX, fromY, fromZ,
                    SoundEvents.ENDERMAN_TELEPORT, SoundSource.PLAYERS, 1.0F, 1.0F);
                level.playSound(null, wearer.getX(), wearer.getY(), wearer.getZ(),
                    SoundEvents.ENDERMAN_TELEPORT, SoundSource.PLAYERS, 1.0F, 1.0F);
                return false;
            }
        }
        // Rolled the dodge and found nowhere to go. The hit lands - which is the right answer, and the
        // reason a cramped corridor is a real counter to this part rather than a free reroll.
        return true;
    }
}
