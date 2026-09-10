package com.mattjesmc.armorpieces.command;

import com.mattjesmc.armorpieces.config.ArmorPiecesServerConfig;
import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.loot.DecorationLootTables;
import com.mattjesmc.armorpieces.loot.LootGroup;
import com.mattjesmc.armorpieces.loot.LootReport;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import net.minecraft.commands.CommandBuildContext;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.ResourceOrIdArgument;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.storage.loot.LootParams;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.level.storage.loot.parameters.LootContextParamSets;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
import org.jspecify.annotations.Nullable;

/**
 * {@code /armorpieces loot} - what this mod is doing to the world's loot tables, and what a server
 * owner has changed about it.
 *
 * <p>The mod's loot works by adding one pool to somebody else's table as it loads (see
 * {@link DecorationLootTables}), and the result of that is invisible from inside the game: the pool
 * is buried in a built table, the odds on it come from several files at once, and for a modded pack
 * the table ids are unguessable in the first place. "Inject into any modded container" is true and
 * was unusable, and these four subcommands are the difference.
 *
 * <ul>
 *   <li>{@code list [filter]} - the loot table ids this world actually loaded, marking the ones the
 *       mod adds to. The answer to "what is this modded chest called".</li>
 *   <li>{@code explain <table>} - what was added to one table and why: every group and file that
 *       offered a member, at what chance and weight, and the number that ended up on the pool.</li>
 *   <li>{@code groups} - the loaded {@link LootGroup} files with the server config's say applied,
 *       so a group that has been turned off or re-tuned says so.</li>
 *   <li>{@code roll <table> [rolls]} - rolls the table and counts what came out of this mod. The
 *       measurement, where the other three are the theory.</li>
 * </ul>
 *
 * <p>There is deliberately no {@code reload} here. {@link ArmorPiecesServerConfig} is re-read at the
 * start of every datapack reload, so plain {@code /reload} picks up an edit to it and there is no
 * second command to remember - and no way to have the config in force disagree with the tables that
 * were built from it.
 */
public final class LootCommand {
    /** Rolls of a loot table when no count is given: enough for a chance of 0.05 to show up. */
    private static final int DEFAULT_ROLLS = 1000;
    /** Rolling is cheap, but a million rolls of a table with functions is a noticeable pause. */
    private static final int MAX_ROLLS = 100_000;
    /** Table ids printed by {@code list} before it stops and says how many are left. */
    private static final int MAX_LISTED = 100;

    private LootCommand() {}

    /** The {@code loot} node, for the {@code /armorpieces} root that {@link StageCommand} builds. */
    public static LiteralArgumentBuilder<CommandSourceStack> node(final CommandBuildContext context) {
        return Commands.literal("loot")
            .then(Commands.literal("list")
                .executes(ctx -> list(ctx.getSource(), ""))
                .then(Commands.argument("filter", StringArgumentType.greedyString())
                    .executes(ctx -> list(ctx.getSource(), StringArgumentType.getString(ctx, "filter")))))
            .then(Commands.literal("explain")
                .then(Commands.argument("table", ResourceOrIdArgument.lootTable(context))
                    .executes(ctx -> explain(ctx.getSource(), ResourceOrIdArgument.getLootTable(ctx, "table")))))
            .then(Commands.literal("groups")
                .executes(ctx -> groups(ctx.getSource())))
            .then(Commands.literal("roll")
                .then(Commands.argument("table", ResourceOrIdArgument.lootTable(context))
                    .executes(ctx -> roll(ctx.getSource(),
                        ResourceOrIdArgument.getLootTable(ctx, "table"), DEFAULT_ROLLS))
                    .then(Commands.argument("rolls", IntegerArgumentType.integer(1, MAX_ROLLS))
                        .executes(ctx -> roll(ctx.getSource(),
                            ResourceOrIdArgument.getLootTable(ctx, "table"),
                            IntegerArgumentType.getInteger(ctx, "rolls"))))));
    }

    // ---- list -----------------------------------------------------------------------------------

    /**
     * Every loaded loot table id containing {@code filter}, a {@code +} against the ones the mod
     * adds to.
     *
     * <p>Read from the reloadable registries rather than from any list of ours, which is the whole
     * point: a modded pack's table ids are in there and nowhere else.
     */
    private static int list(final CommandSourceStack source, final String filter) {
        final HolderLookup.RegistryLookup<LootTable> tables =
            source.getServer().reloadableRegistries().lookup().lookup(Registries.LOOT_TABLE).orElse(null);
        if (tables == null) {
            source.sendFailure(Component.translatable("commands.armorpieces.loot.no_tables"));
            return 0;
        }
        final String needle = filter.toLowerCase(Locale.ROOT);
        final List<ResourceKey<LootTable>> matched = tables.listElementIds()
            .filter(key -> key.identifier().toString().contains(needle))
            .sorted(Comparator.comparing(key -> key.identifier().toString()))
            .toList();

        final long total = tables.listElementIds().count();
        final long ours = matched.stream().filter(key -> DecorationLootTables.report(key) != null).count();
        source.sendSuccess(() -> Component.translatable(
            "commands.armorpieces.loot.list.header", matched.size(), total, ours), false);
        matched.stream().limit(MAX_LISTED).forEach(key -> source.sendSuccess(() -> Component.translatable(
            DecorationLootTables.report(key) == null
                ? "commands.armorpieces.loot.list.line"
                : "commands.armorpieces.loot.list.line.ours",
            key.identifier().toString()), false));
        if (matched.size() > MAX_LISTED) {
            source.sendSuccess(() -> Component.translatable(
                "commands.armorpieces.loot.list.more", matched.size() - MAX_LISTED), false);
        }
        return matched.size();
    }

    // ---- explain --------------------------------------------------------------------------------

    /** What the mod put in one table, from every source that asked, and the number it settled on. */
    private static int explain(final CommandSourceStack source, final Holder<LootTable> table) {
        final ResourceKey<LootTable> key = table.unwrapKey().orElse(null);
        final LootReport report = key == null ? null : DecorationLootTables.report(key);
        final String name = key == null ? "<inline>" : key.identifier().toString();
        if (report == null) {
            source.sendSuccess(() -> Component.translatable("commands.armorpieces.loot.explain.none", name), false);
            offNotice(source);
            return 0;
        }

        source.sendSuccess(() -> Component.translatable("commands.armorpieces.loot.explain.header",
            name, report.members(), percent(report.chance())), false);
        for (final LootReport.Source line : report.sources()) {
            source.sendSuccess(() -> Component.translatable(
                line.overridden()
                    ? "commands.armorpieces.loot.explain.source.overridden"
                    : "commands.armorpieces.loot.explain.source",
                line.name(), line.members(), percent(line.chance()), line.weight()), false);
        }
        if (report.scaled()) {
            source.sendSuccess(() -> Component.translatable("commands.armorpieces.loot.explain.scaled",
                percent(report.packChance()), percent(report.chance())), false);
        }
        return report.members();
    }

    // ---- groups ---------------------------------------------------------------------------------

    /** Every loaded group, with what the server config has to say about each. */
    private static int groups(final CommandSourceStack source) {
        final HolderLookup.RegistryLookup<LootGroup> lookup =
            source.registryAccess().lookup(ArmorPiecesRegistries.LOOT_GROUP).orElse(null);
        final List<Holder.Reference<LootGroup>> loaded = lookup == null
            ? List.of()
            : lookup.listElements().sorted(Comparator.comparing(h -> h.key().identifier().toString())).toList();
        if (loaded.isEmpty()) {
            source.sendSuccess(() -> Component.translatable("commands.armorpieces.loot.groups.none"), false);
            return 0;
        }

        final ArmorPiecesServerConfig config = ArmorPiecesServerConfig.get();
        source.sendSuccess(() -> Component.translatable(
            "commands.armorpieces.loot.groups.header", loaded.size()), false);
        for (final Holder.Reference<LootGroup> holder : loaded) {
            final LootGroup group = holder.value();
            final ArmorPiecesServerConfig.GroupOverride override = config.override(holder.key());
            final int members = group.memberCount(source.registryAccess());
            final float chance = override == null ? group.chance() : override.chance().orElse(group.chance());
            final int weight = override == null ? group.weight() : override.weight().orElse(group.weight());
            // Counted rather than added up: a removed table the group never named would otherwise
            // make the total lie.
            final Set<ResourceKey<LootTable>> reached = new LinkedHashSet<>();
            group.tables().forEach(entry -> reached.add(entry.table()));
            if (override != null) {
                override.add().forEach(entry -> reached.add(entry.table()));
                reached.removeAll(override.remove());
            }
            final int tables = reached.size();
            source.sendSuccess(() -> Component.translatable("commands.armorpieces.loot.groups.line",
                holder.key().identifier().toString(), percent(chance), weight, tables, members), false);
            if (override != null && !override.enabled()) {
                source.sendSuccess(() -> Component.translatable("commands.armorpieces.loot.groups.off"), false);
            } else if (override != null && !override.isTrivial()) {
                source.sendSuccess(() -> Component.translatable("commands.armorpieces.loot.groups.overridden"), false);
            }
        }
        offNotice(source);
        if (config.chanceMultiplier() != 1.0f) {
            source.sendSuccess(() -> Component.translatable(
                "commands.armorpieces.loot.multiplier", format(config.chanceMultiplier())), false);
        }
        return loaded.size();
    }

    // ---- roll -----------------------------------------------------------------------------------

    /**
     * Rolls {@code table} {@code rolls} times as a chest at the caller's feet and counts what came
     * out of this mod: templates by what they carry, decorated armor by its item and parts.
     * Everything else the table drops is one line, so the mod's share of the chest is visible too.
     *
     * <p>The chest parameter set, because the shipped parts live in chests and it is the set a
     * table needs least; a table wanting more (a mob's, say) has its conditions fail and drops
     * nothing, which the count then shows.
     */
    private static int roll(final CommandSourceStack source, final Holder<LootTable> table, final int rolls) {
        final LootParams params = new LootParams.Builder(source.getLevel())
            .withParameter(LootContextParams.ORIGIN, source.getPosition())
            .create(LootContextParamSets.CHEST);
        final Map<Component, Integer> counts = new LinkedHashMap<>();
        int fromMod = 0;
        int other = 0;
        for (int i = 0; i < rolls; i++) {
            for (final ItemStack stack : table.value().getRandomItems(params)) {
                final Component key = lootKey(stack);
                if (key == null) {
                    other += stack.getCount();
                    continue;
                }
                counts.merge(key, stack.getCount(), Integer::sum);
                fromMod += stack.getCount();
            }
        }

        final String name = table.unwrapKey().map(key -> key.identifier().toString()).orElse("<inline>");
        final int total = fromMod;
        source.sendSuccess(() -> Component.translatable("commands.armorpieces.loot.roll.header", name, rolls, total), false);
        counts.entrySet().stream()
            .sorted(Map.Entry.<Component, Integer>comparingByValue(Comparator.reverseOrder()))
            .forEach(entry -> source.sendSuccess(() -> Component.translatable(
                "commands.armorpieces.loot.roll.line",
                entry.getKey(), entry.getValue(), String.format("%.1f", 100.0 * entry.getValue() / rolls)), false));
        final int rest = other;
        source.sendSuccess(() -> Component.translatable("commands.armorpieces.loot.roll.other", rest), false);
        return fromMod;
    }

    /**
     * What to count a dropped stack as, or null if it is nothing of this mod's.
     *
     * <p>All four template families are recognised, not only the part's. Counting one family and
     * dropping the other three into "everything else" is a measurement that quietly disagrees with
     * what {@code explain} says the table holds.
     */
    private static @Nullable Component lootKey(final ItemStack stack) {
        if (stack.has(ModDataComponents.DECORATION)
            || stack.has(ModDataComponents.SKIN)
            || stack.has(ModDataComponents.CLOTH)
            || stack.has(ModDataComponents.FITTING)) {
            // A template's name already says what it carries: "Circlet Brow Smithing Template".
            return stack.getHoverName();
        }
        final ArmorDecorations worn = stack.get(ModDataComponents.DECORATIONS);
        if (worn != null && !worn.isEmpty()) {
            final Component parts = worn.entries().values().stream()
                .map(entry -> entry.decoration().value().copyWithStyle(entry.material()))
                .reduce((a, b) -> Component.empty().append(a).append(Component.literal(", ")).append(b))
                .orElse(Component.empty());
            return Component.empty()
                .append(stack.getHoverName())
                .append(Component.literal(" wearing "))
                .append(parts);
        }
        return null;
    }

    // ---- feedback -------------------------------------------------------------------------------

    /** Says the mod's loot is switched off, since every other line here would otherwise read as a lie. */
    private static void offNotice(final CommandSourceStack source) {
        if (!ArmorPiecesServerConfig.get().enabled()) {
            source.sendSuccess(() -> Component.translatable("commands.armorpieces.loot.off"), false);
        }
    }

    private static String percent(final float chance) {
        return String.format(Locale.ROOT, "%.1f%%", 100.0f * chance);
    }

    private static String format(final float value) {
        return String.format(Locale.ROOT, "%.2f", value);
    }
}
