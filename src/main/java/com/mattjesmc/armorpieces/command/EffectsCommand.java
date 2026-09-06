package com.mattjesmc.armorpieces.command;

import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mattjesmc.armorpieces.decoration.effect.DecorationEffect;
import com.mattjesmc.armorpieces.decoration.effect.DecorationEffectContext;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;

/**
 * {@code /armorpieces effects [<wearer>]} - what the parts somebody is wearing are actually doing.
 *
 * <p>The same problem {@code /armorpieces loot} answers on the loot side: the system worked and was
 * invisible. A part's behaviour is a line in a datapack file the player never sees, its numbers may
 * depend on the material it was made in, and - since {@code if_fitting} and {@code if_wearer} - on
 * what is set in the part and on what the wearer is holding, standing in or doing. A player looking
 * at armor that is not helping them has no way to tell whether the part is wrong, the material is
 * wrong, or their hands are full.
 *
 * <p>So this prints, per socket, the part and one line per effect, marked with whether it is
 * contributing AT THIS MOMENT - which is the only part of the answer a tooltip cannot give, since a
 * tooltip has no wearer to ask. The lines themselves are the same
 * {@link DecorationEffect#description} the tooltip shows, so the two never disagree.
 *
 * <p>Tuning what an effect gives is deliberately not here. A server owner changes numbers in
 * {@code config/armorpieces-server.json}; this is the window onto them, not a second way to set them.
 */
public final class EffectsCommand {
    /** The slots a {@link DecorationAnchor} can name, head to toe. */
    private static final List<EquipmentSlot> ARMOR_SLOTS =
        List.of(EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET);

    private EffectsCommand() {}

    /** The {@code effects} node, for the {@code /armorpieces} root that {@link StageCommand} builds. */
    public static LiteralArgumentBuilder<CommandSourceStack> node() {
        return Commands.literal("effects")
            .executes(ctx -> report(ctx.getSource(), self(ctx.getSource())))
            .then(Commands.argument("wearer", EntityArgument.entity())
                .executes(ctx -> report(ctx.getSource(), living(EntityArgument.getEntity(ctx, "wearer")))));
    }

    /** The caller, who is usually the person asking why their boots do nothing. */
    private static LivingEntity self(final CommandSourceStack source) throws CommandSyntaxException {
        return source.getPlayerOrException();
    }

    /**
     * Any living entity will do - an armor stand is the usual second answer, since a stand can wear
     * a decorated set and is how a pack author looks at one without putting it on.
     */
    private static LivingEntity living(final Entity entity) throws CommandSyntaxException {
        if (entity instanceof LivingEntity wearer) {
            return wearer;
        }
        throw EntityArgument.NO_ENTITIES_FOUND.create();
    }

    /**
     * One wearer's effects, socket by socket.
     *
     * @return the number of effects contributing right now, so a command block can branch on it.
     */
    private static int report(final CommandSourceStack source, final LivingEntity wearer) {
        // Collected before anything is printed, because the header counts what follows it and a
        // report that leads with its total is the one worth reading.
        final List<Component> lines = new ArrayList<>();
        int listed = 0;
        int active = 0;
        for (final EquipmentSlot slot : ARMOR_SLOTS) {
            final ItemStack stack = wearer.getItemBySlot(slot);
            final ArmorDecorations decorations = stack.get(ModDataComponents.DECORATIONS);
            if (decorations == null || decorations.isEmpty()) {
                continue;
            }
            // Anchor order rather than map order, so the report reads top-down the body exactly as
            // the tooltip does. A socket riding on the wrong piece is skipped here for the same
            // reason the dispatcher skips it: it does nothing, so saying what it does would be a lie.
            for (final DecorationAnchor anchor : DecorationAnchor.values()) {
                final DecorationEntry entry = decorations.entries().get(anchor);
                if (entry == null || anchor.slot() != slot) {
                    continue;
                }
                final List<DecorationEffect> effects = entry.decoration().value().effects();
                if (effects.isEmpty()) {
                    continue;
                }
                lines.add(Component.translatable("commands.armorpieces.effects.part",
                    anchor.getSerializedName(),
                    entry.decoration().value().copyWithStyle(entry.material())));
                final DecorationEffectContext context =
                    new DecorationEffectContext(wearer, anchor, stack, entry);
                for (final DecorationEffect effect : effects) {
                    final boolean applies = effect.applies(context);
                    lines.add(Component.translatable(
                        applies
                            ? "commands.armorpieces.effects.line"
                            : "commands.armorpieces.effects.line.inactive",
                        effect.description(entry.material())));
                    listed++;
                    if (applies) {
                        active++;
                    }
                }
            }
        }

        final int total = listed;
        final int contributing = active;
        if (total == 0) {
            source.sendSuccess(() -> Component.translatable(
                "commands.armorpieces.effects.none", wearer.getDisplayName()), false);
            return 0;
        }
        source.sendSuccess(() -> Component.translatable(
            "commands.armorpieces.effects.header", wearer.getDisplayName(), total, contributing), false);
        for (final Component line : lines) {
            source.sendSuccess(() -> line, false);
        }
        return contributing;
    }
}
