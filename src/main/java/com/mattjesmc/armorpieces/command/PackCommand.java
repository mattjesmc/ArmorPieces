package com.mattjesmc.armorpieces.command;

import com.mattjesmc.armorpieces.pack.PackProblem;
import com.mattjesmc.armorpieces.pack.PackProblems;
import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import java.util.List;
import java.util.Map;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;

/**
 * {@code /armorpieces packs} - what the installed packs got wrong, and what the mod did about it.
 *
 * <p>The other half of {@code /armorpieces missing}. That one says what this world NAMES and this
 * installation does not have; this says what this installation HAS and could not use. Both are
 * reports rather than repairs, and for the same reason: nothing here refused to load, so there is
 * nothing to undo - only a list of things that are not doing what somebody meant them to.
 *
 * <p>Written for the person who can act on it, which is usually the pack's author and sometimes the
 * server owner who installed it. So each line names the file rather than the Java, and says which of
 * the three things happened to it: skipped, worked around, or merely reported. See
 * {@code docs/plans/pack-mistakes.md}.
 */
public final class PackCommand {
    /** More than this and the chat is the problem rather than the report; the log has them all. */
    private static final int MOST_LINES = 30;

    private PackCommand() {}

    /** The {@code packs} node, for the {@code /armorpieces} root that {@link StageCommand} builds. */
    public static LiteralArgumentBuilder<CommandSourceStack> node() {
        return Commands.literal("packs").executes(ctx -> report(ctx.getSource()));
    }

    /** @return how many distinct problems there are, so a command block can branch on it. */
    private static int report(final CommandSourceStack source) {
        final List<Map.Entry<PackProblem, Integer>> problems = PackProblems.all();
        if (problems.isEmpty()) {
            source.sendSuccess(() -> Component.translatable("commands.armorpieces.packs.none")
                .withStyle(ChatFormatting.GREEN), false);
            return 0;
        }
        source.sendSuccess(() -> Component.translatable(
            "commands.armorpieces.packs.header", problems.size()).withStyle(ChatFormatting.YELLOW), false);
        for (final Map.Entry<PackProblem, Integer> entry : problems.stream().limit(MOST_LINES).toList()) {
            final PackProblem problem = entry.getKey();
            source.sendSuccess(() -> Component.literal(" ")
                .append(Component.literal(problem.bucket().label())
                    .withStyle(colour(problem.bucket())))
                .append(Component.literal("  " + problem.subject()).withStyle(ChatFormatting.WHITE))
                .append(entry.getValue() > 1
                    ? Component.literal("  x" + entry.getValue()).withStyle(ChatFormatting.DARK_GRAY)
                    : Component.empty()), false);
            source.sendSuccess(() -> Component.literal("   " + problem.detail())
                .withStyle(ChatFormatting.GRAY), false);
        }
        if (problems.size() > MOST_LINES) {
            source.sendSuccess(() -> Component.translatable(
                "commands.armorpieces.packs.more", problems.size() - MOST_LINES)
                .withStyle(ChatFormatting.DARK_GRAY), false);
        }
        source.sendSuccess(() -> Component.translatable("commands.armorpieces.packs.advice")
            .withStyle(ChatFormatting.GRAY), false);
        return problems.size();
    }

    private static ChatFormatting colour(final PackProblem.Bucket bucket) {
        return switch (bucket) {
            case SKIPPED -> ChatFormatting.RED;
            case WORKED_AROUND -> ChatFormatting.GOLD;
            case REPORTED -> ChatFormatting.YELLOW;
        };
    }
}
