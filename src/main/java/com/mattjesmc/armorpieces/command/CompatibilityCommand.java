package com.mattjesmc.armorpieces.command;

import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import com.mattjesmc.armorpieces.identity.Moved;
import com.mattjesmc.armorpieces.identity.Rebind;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.chunk.LevelChunk;

/**
 * {@code /armorpieces missing}, {@code prune} and {@code upgrade} - the three things an operator can
 * do about content a save names and this installation does not have.
 *
 * <p>Nothing here is needed for the system to be safe. A piece nothing can resolve is already kept,
 * already invisible, already harmless and already comes back the day its pack is installed; these are
 * for the person who wants to know what is going on, or to decide otherwise.
 *
 * <ul>
 *   <li>{@code missing} is the shopping list. It names every id this session could not resolve, which
 *       is how a server owner finds out which pack to install rather than guessing from a player's
 *       description of a helmet.</li>
 *   <li>{@code prune} is the <b>only</b> thing in this mod that destroys a saved piece, and it is
 *       deliberately hard to do by accident: an operator, naming who it applies to, and a dry run
 *       first that shows exactly what would go.</li>
 *   <li>{@code upgrade} forces the lazy port to happen now for the part of the world that is loaded,
 *       and says plainly what it cannot reach.</li>
 * </ul>
 */
public final class CompatibilityCommand {
    private CompatibilityCommand() {}

    /** The {@code missing} node, for the {@code /armorpieces} root that {@link StageCommand} builds. */
    public static LiteralArgumentBuilder<CommandSourceStack> missingNode() {
        return Commands.literal("missing").executes(ctx -> missing(ctx.getSource()));
    }

    /** The {@code prune} node. Dry by default; {@code confirm} is what actually drops anything. */
    public static LiteralArgumentBuilder<CommandSourceStack> pruneNode() {
        return Commands.literal("prune")
            .then(Commands.argument("targets", EntityArgument.entities())
                .executes(ctx -> prune(ctx.getSource(), EntityArgument.getEntities(ctx, "targets"), false))
                .then(Commands.literal("confirm")
                    .executes(ctx ->
                        prune(ctx.getSource(), EntityArgument.getEntities(ctx, "targets"), true))));
    }

    /** The {@code upgrade} node. */
    public static LiteralArgumentBuilder<CommandSourceStack> upgradeNode() {
        return Commands.literal("upgrade").executes(ctx -> upgrade(ctx.getSource()));
    }

    /**
     * What this world is waiting for.
     *
     * @return the number of distinct ids nothing can resolve, so a command block can branch on it.
     */
    private static int missing(final CommandSourceStack source) {
        final List<Map.Entry<Rebind.Miss, Integer>> misses = Rebind.misses();
        if (misses.isEmpty()) {
            source.sendSuccess(() -> Component.translatable("commands.armorpieces.missing.none")
                .withStyle(ChatFormatting.GREEN), false);
            return 0;
        }
        source.sendSuccess(() -> Component.translatable(
            "commands.armorpieces.missing.header", misses.size()).withStyle(ChatFormatting.YELLOW), false);
        for (final Map.Entry<Rebind.Miss, Integer> miss : misses) {
            // The pack, where the shipped index can place the id - this is the shopping list, and an
            // id an operator has to search for is half a list. Translated on the receiving client,
            // not here: a dedicated server's Language holds vanilla's keys and none of ours.
            final Component pack = Moved.pack(miss.getKey().id())
                .map(name -> Component.literal("  ").append(name).withStyle(ChatFormatting.YELLOW))
                .orElseGet(Component::empty);
            source.sendSuccess(() -> Component.literal(" ")
                .append(Component.literal(miss.getKey().id()).withStyle(ChatFormatting.WHITE))
                .append(pack)
                .append(Component.literal("  x" + miss.getValue()).withStyle(ChatFormatting.DARK_GRAY))
                .append(Component.literal("  " + miss.getKey().registry().identifier().getPath())
                    .withStyle(ChatFormatting.DARK_GRAY)), false);
        }
        source.sendSuccess(() -> Component.translatable("commands.armorpieces.missing.advice")
            .withStyle(ChatFormatting.GRAY), false);
        // Only ever a count of what has been LOOKED AT. Saying so stops a reading of "nothing else
        // is wrong" that the number cannot support.
        source.sendSuccess(() -> Component.translatable("commands.armorpieces.missing.caveat")
            .withStyle(ChatFormatting.DARK_GRAY), false);
        return misses.size();
    }

    /**
     * Drops every unresolvable socket from what the targets are wearing and carrying.
     *
     * @param confirmed false for the dry run, which changes nothing and prints what would go
     * @return how many sockets were dropped, or would be
     */
    private static int prune(
        final CommandSourceStack source,
        final Collection<? extends Entity> targets,
        final boolean confirmed
    ) {
        final List<Component> lines = new ArrayList<>();
        int sockets = 0;
        int stacks = 0;
        for (final Entity target : targets) {
            for (final ItemStack stack : carried(target)) {
                final ArmorDecorations worn = stack.get(ModDataComponents.DECORATIONS);
                if (worn == null || worn.unresolvedCount() == 0) {
                    continue;
                }
                stacks++;
                sockets += worn.unresolvedCount();
                lines.add(Component.literal(" ")
                    .append(stack.getHoverName())
                    .append(Component.literal(" - " + String.join(", ", worn.unresolvedNames()))
                        .withStyle(ChatFormatting.DARK_GRAY)));
                if (confirmed) {
                    stack.set(ModDataComponents.DECORATIONS, worn.pruned());
                }
            }
        }
        if (sockets == 0) {
            source.sendSuccess(() -> Component.translatable("commands.armorpieces.prune.none"), false);
            return 0;
        }
        lines.forEach(line -> source.sendSuccess(() -> line, false));
        final int droppedSockets = sockets;
        final int droppedStacks = stacks;
        if (confirmed) {
            source.sendSuccess(() -> Component.translatable(
                "commands.armorpieces.prune.done", droppedSockets, droppedStacks)
                .withStyle(ChatFormatting.RED), true);
        } else {
            source.sendSuccess(() -> Component.translatable(
                "commands.armorpieces.prune.dry", droppedSockets, droppedStacks)
                .withStyle(ChatFormatting.YELLOW), false);
        }
        return sockets;
    }

    /**
     * Everything on an entity that an unresolvable socket could be sitting in - every equipment slot,
     * and a player's whole inventory besides. An armor stand is a legitimate target: a stand wearing a
     * set is how a pack author looks at one.
     */
    private static Iterable<ItemStack> carried(final Entity target) {
        final List<ItemStack> stacks = new ArrayList<>();
        if (target instanceof LivingEntity living) {
            for (final EquipmentSlot slot : EquipmentSlot.values()) {
                stacks.add(living.getItemBySlot(slot));
            }
        }
        if (target instanceof ServerPlayer player) {
            for (int slot = 0; slot < player.getInventory().getContainerSize(); slot++) {
                stacks.add(player.getInventory().getItem(slot));
            }
        }
        return stacks;
    }

    /**
     * Writes the loaded world back, so anything the tolerant decode rebound is saved in its new form
     * now rather than whenever its chunk next happens to be written.
     *
     * <p>What it can reach is chunks near players. It says so, because the alternative - implying the
     * whole world was done - would leave an owner believing a pack is safe to uninstall when a chest
     * three thousand blocks away still names it. Nothing is at risk either way: an item that was never
     * upgraded is still kept, still safe and still rebindable; it is simply not yet carrying the
     * lineage that would survive the NEXT move.
     */
    private static int upgrade(final CommandSourceStack source) {
        final int radius = source.getServer().getPlayerList().getViewDistance();
        int chunks = 0;
        for (final ServerLevel level : source.getServer().getAllLevels()) {
            for (final ServerPlayer player : level.players()) {
                final ChunkPos centre = player.chunkPosition();
                for (int x = centre.x() - radius; x <= centre.x() + radius; x++) {
                    for (int z = centre.z() - radius; z <= centre.z() + radius; z++) {
                        final LevelChunk chunk = level.getChunkSource().getChunkNow(x, z);
                        if (chunk != null) {
                            chunk.markUnsaved();
                            chunks++;
                        }
                    }
                }
            }
        }
        // Player data is written on logout whatever happens, so worn and carried armor needs nothing
        // from this - it is the world's containers that this is for.
        final int marked = chunks;
        source.sendSuccess(() -> Component.translatable("commands.armorpieces.upgrade.done", marked), true);
        source.sendSuccess(() -> Component.translatable("commands.armorpieces.upgrade.caveat")
            .withStyle(ChatFormatting.GRAY), false);
        return marked;
    }
}
