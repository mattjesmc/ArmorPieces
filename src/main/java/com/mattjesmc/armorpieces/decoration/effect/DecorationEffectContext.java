package com.mattjesmc.armorpieces.decoration.effect;

import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import net.minecraft.core.Holder;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.equipment.trim.TrimMaterial;
import net.minecraft.world.level.Level;
import org.jspecify.annotations.Nullable;

/**
 * Everything a {@link DecorationEffect} is told about the occasion it is running on: who is wearing
 * it, on which piece, in which socket, and in which material.
 *
 * <p>Carrying the whole {@link DecorationEntry} rather than just the part is what lets an effect
 * scale with its MATERIAL - a netherite plume that dodges more often than an iron one is a single
 * lookup on {@link #material()}, with no second registry entry and no second part. The material a
 * decoration wears is vanilla's own {@code TrimMaterial}, so an effect can key off materials a
 * datapack invents tomorrow as easily as off the vanilla eleven.
 *
 * <p>The {@link #stack} is the LIVE worn stack, not a copy: an effect that damages it - a glider that
 * wears out - writes straight to the piece the wearer has on.
 *
 * @param wearer  the entity wearing the piece. Not necessarily a player: armor stands, zombies and
 *                any modded humanoid can carry decorations, so an effect that assumes a player must
 *                check.
 * @param anchor  the socket, which also fixes the {@link #slot()} the piece occupies.
 * @param stack   the worn piece itself.
 * @param entry   the part and its material.
 */
public record DecorationEffectContext(
    LivingEntity wearer,
    DecorationAnchor anchor,
    ItemStack stack,
    DecorationEntry entry
) {
    /** The part. */
    public Holder<ArmorDecoration> decoration() {
        return this.entry.decoration();
    }

    /** The trim material the part was made in. */
    public Holder<TrimMaterial> material() {
        return this.entry.material();
    }

    /** Which armor slot the decorated piece is in. Fixed by the socket. */
    public EquipmentSlot slot() {
        return this.anchor.slot();
    }

    /** The world the wearer is in, whichever side this hook is running on. */
    public Level level() {
        return this.wearer.level();
    }

    /**
     * The server view of {@link #level()}, or {@code null} on the client.
     *
     * <p>Null is only reachable from {@link DecorationEffect.Gliding}, which vanilla evaluates on
     * both sides; every other hook is dispatched from a server event and can use this directly.
     */
    public @Nullable ServerLevel serverLevel() {
        return this.wearer.level() instanceof ServerLevel serverLevel ? serverLevel : null;
    }

    /** The wearer's own randomness, so an effect's rolls are reproducible with the entity's. */
    public RandomSource random() {
        return this.wearer.getRandom();
    }
}
