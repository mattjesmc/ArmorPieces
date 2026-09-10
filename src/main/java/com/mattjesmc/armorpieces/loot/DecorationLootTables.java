package com.mattjesmc.armorpieces.loot;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.cloth.Cloth;
import com.mattjesmc.armorpieces.cloth.ClothValue;
import com.mattjesmc.armorpieces.config.ArmorPiecesServerConfig;
import com.mattjesmc.armorpieces.config.ArmorPiecesServerConfig.GroupOverride;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.DecorationLoot;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.registry.ModItems;
import com.mattjesmc.armorpieces.skin.ArmorSkin;
import com.mattjesmc.armorpieces.skin.ArmorSkinValue;
import com.mattjesmc.armorpieces.identity.Tolerant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.IntFunction;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.loot.v3.LootTableEvents;
import net.fabricmc.fabric.api.loot.v3.LootTableSource;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderLookup;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.storage.loot.LootPool;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.level.storage.loot.entries.LootItem;
import net.minecraft.world.level.storage.loot.entries.LootPoolEntryContainer;
import net.minecraft.world.level.storage.loot.functions.SetComponentsFunction;
import net.minecraft.world.level.storage.loot.predicates.LootItemRandomChanceCondition;
import net.minecraft.world.level.storage.loot.providers.number.ConstantValue;
import org.jspecify.annotations.Nullable;

/**
 * Puts parts, skins, cloths and fitting templates into loot tables: the {@code loot} list on a data
 * file and the {@link LootGroup} files, made real. All four template families are found the same
 * way, through the same pool; a fitting is the one that has only the group route.
 *
 * <p>Runs as each loot table is loaded, on world start and on {@code /reload} alike. The registries
 * are there to walk because loot tables are the last thing loaded: they are built against the full
 * registry access, dynamic registries included, and the event hands that access over.
 *
 * <p><b>One pool per table, rolled once, with ONE {@code random_chance} on the pool.</b> Everything
 * that reaches the table - by naming it on its own data file, or by being tagged into a group that
 * names it - is an entry in that single pool, and the weights decide which one is placed. Two
 * consequences, and they are the design:
 *
 * <ul>
 *   <li><b>The odds are a property of the table.</b> "An end city treasure chest holds a part one
 *       time in six" stays true as parts are added; a ninety-first part changes WHICH part is found,
 *       never how often. The rejected alternative, a chance per entry, gives the table
 *       {@code 1-∏(1-c)} - measured at 0.28 over four entries on {@code pillager_outpost}, and
 *       climbing to near-certainty once a whole theme's worth of parts names one table.</li>
 *   <li><b>A chest never holds two of ours.</b> One roll over one pool, however many groups and
 *       rows fed it.</li>
 * </ul>
 *
 * <p>Where the chance comes from, when several sources name one table: the highest of them. A table
 * in a generous group and a mean one is generous, and the mean group's members simply ride along.
 * A member offered twice - tagged into two groups, or tagged and named on its own file - is ONE
 * entry at the best weight it was offered, never two.
 *
 * <p>The table's own pools are untouched throughout: a chest that would have held a diamond still
 * holds it, with or without a template beside it.
 *
 * <p>Nothing here is specific to the mod's own parts. A pack's part that names a table, or that is
 * tagged into a group, is added the same way - which is the whole reason this is done in Java: a
 * datapack can replace a vanilla table but cannot add to one, and two packs that both replace
 * {@code chests/ancient_city} cannot both win.
 *
 * <h2>The server's say</h2>
 *
 * <p>Everything above is what the PACKS asked for. What is actually written is that, put through
 * {@link ArmorPiecesServerConfig} - a group switched off, its chance or weight replaced, tables
 * added to it or taken from it, and one multiplier over all of it. The invariants survive
 * untouched, because the config only ever moves the numbers this class was going to use: it is
 * still one pool, still one roll, and the chance is still a property of the table.
 *
 * <p>Every decision made here is recorded as a {@link LootReport}, which is what
 * {@code /armorpieces loot explain} reads. Nothing reads it back to build anything.
 */
public final class DecorationLootTables {
    private DecorationLootTables() {}

    /**
     * What was added to each table on the current set of packs.
     *
     * <p>Concurrent because loot tables are loaded off the reload executor and nothing promises the
     * event fires on one thread.
     */
    private static final Map<ResourceKey<LootTable>, LootReport> REPORTS = new ConcurrentHashMap<>();

    public static void register() {
        LootTableEvents.MODIFY.register(DecorationLootTables::modify);
        // A report describes one load of one set of packs. Clearing at the START of a reload means
        // a table a pack stopped shipping stops being explained, rather than lingering as an answer
        // about a world that no longer exists.
        ServerLifecycleEvents.START_DATA_PACK_RELOAD.register((server, resources) -> forget());
        // And a reload is not the only way one JVM sees two sets of packs: a single-player client
        // opens a world, quits to the menu and opens another without ever reloading, and the loot
        // tables are built afresh for the second one. Without this, a table the first world's packs
        // reached is still explained in the second - by a report naming a group that world may not
        // even have. Found by LootTablesTest, which is a JVM with no reload in it at all.
        ServerLifecycleEvents.SERVER_STOPPED.register(server -> forget());
    }

    /**
     * Drops everything recorded about the packs that were loaded. Called at every boundary between
     * one set of packs and the next; package-private so {@code LootTablesTest} can stand at the same
     * boundary, since a test JVM has none of its own.
     */
    static void forget() {
        REPORTS.clear();
        offNoticed = false;
    }

    /** What the mod added to {@code table}, or null if it added nothing. */
    public static @Nullable LootReport report(final ResourceKey<LootTable> table) {
        return REPORTS.get(table);
    }

    /** Every table the mod added to, in no particular order. */
    public static Collection<LootReport> reports() {
        return List.copyOf(REPORTS.values());
    }

    private static void modify(
        final ResourceKey<LootTable> key,
        final LootTable.Builder table,
        final LootTableSource source,
        final HolderLookup.Provider registries
    ) {
        final ArmorPiecesServerConfig config = ArmorPiecesServerConfig.get();
        if (!config.enabled()) {
            // The off switch, said once per load rather than per table.
            offNoticeOnce();
            return;
        }

        final HolderLookup.RegistryLookup<ArmorDecoration> parts =
            registries.lookup(ArmorPiecesRegistries.ARMOR_DECORATION).orElse(null);
        if (parts == null) {
            // Never expected: loot loads after the dynamic registries. Said once rather than per
            // table, and not thrown, since the tables themselves are fine.
            warnOnce();
            return;
        }
        final List<Holder.Reference<ArmorSkin>> skins = all(registries, ArmorPiecesRegistries.ARMOR_SKIN);
        final List<Holder.Reference<Cloth>> cloths = all(registries, ArmorPiecesRegistries.CLOTH);

        final Offers offers = new Offers();
        final List<LootReport.Source> sources = new ArrayList<>();

        // 1. The exact route: a table named on the part's, skin's or cloth's own data file. One
        //    part, one table, its own chance and weight - which is what a hand-placed "wings in end
        //    cities" is, and what a pack writes when it wants no group at all.
        final Direct direct = new Direct();
        for (final Holder.Reference<ArmorDecoration> part : parts.listElements().toList()) {
            for (final DecorationLoot drop : part.value().loot()) {
                if (drop.table().equals(key)) {
                    offers.offer(part, drop.chance(), drop.weight(), partEntry(part));
                    direct.saw(drop);
                }
            }
        }
        for (final Holder.Reference<ArmorSkin> skin : skins) {
            for (final DecorationLoot drop : skin.value().loot()) {
                if (drop.table().equals(key)) {
                    offers.offer(skin, drop.chance(), drop.weight(), skinEntry(skin));
                    direct.saw(drop);
                }
            }
        }
        for (final Holder.Reference<Cloth> cloth : cloths) {
            for (final DecorationLoot drop : cloth.value().loot()) {
                if (drop.table().equals(key)) {
                    offers.offer(cloth, drop.chance(), drop.weight(), clothEntry(cloth));
                    direct.saw(drop);
                }
            }
        }
        direct.describe(sources);

        // 2. The route that scales: a group naming this table, and everything tagged into it - as
        //    the pack wrote it, or as the server config would rather have it.
        for (final Holder.Reference<LootGroup> holder : all(registries, ArmorPiecesRegistries.LOOT_GROUP)) {
            final LootGroup group = holder.value();
            final GroupOverride override = config.override(holder.key());
            if (override != null && !override.enabled()) {
                continue;
            }
            final Optional<Float> chance = chanceFor(group, override, key);
            if (chance.isEmpty()) {
                continue;
            }
            final float c = chance.get();
            final int weight = override == null ? group.weight() : override.weight().orElse(group.weight());
            int offered = 0;
            // Resolved HERE and not when the file was read: a tag no installed pack defines is an
            // empty list and the group simply offers nothing, where an eagerly bound one would have
            // taken the world down long before this. See MemberSet.
            for (final Holder<ArmorDecoration> part : group.parts().resolve(registries)) {
                offers.offer(part, c, weight, partEntry(part));
                offered++;
            }
            for (final Holder<ArmorSkin> skin : group.skins().resolve(registries)) {
                offers.offer(skin, c, weight, skinEntry(skin));
                offered++;
            }
            for (final Holder<Cloth> cloth : group.cloths().resolve(registries)) {
                offers.offer(cloth, c, weight, clothEntry(cloth));
                offered++;
            }
            for (final Holder<Fitting> fitting : group.fittings().resolve(registries)) {
                offers.offer(fitting, c, weight, fittingEntry(fitting));
                offered++;
            }
            if (offered > 0) {
                sources.add(new LootReport.Source(holder.key().identifier().toString(), c, weight, offered,
                    override != null && !override.isTrivial()));
            }
        }

        if (offers.isEmpty()) {
            return;
        }
        final float chance = config.scale(offers.chance);
        if (chance <= 0.0f) {
            // A multiplier of zero is a legitimate way to say "none of this", and an entry that can
            // never be rolled is worse than no pool at all: it would still show in the built table.
            return;
        }
        table.withPool(offers.pool(chance));
        REPORTS.put(key, new LootReport(key, sources, offers.size(), offers.chance, chance));
        ArmorPieces.LOGGER.debug(
            "[Armor Pieces] Added {} template(s) to loot table {} at chance {}",
            offers.size(), key.identifier(), chance);
    }

    /**
     * How often {@code table} offers a member of {@code group}, with the server's say applied, or
     * empty if the table is not in the group at all.
     *
     * <p>The order is the rule: a table the server REMOVED is out however the pack named it; a table
     * the server ADDED takes the chance it was added with, then the override's, then the group's;
     * and a table the pack named takes the override's chance if there is one, since the server
     * owner's number is the last word on how generous their world is.
     */
    private static Optional<Float> chanceFor(
        final LootGroup group,
        final @Nullable GroupOverride override,
        final ResourceKey<LootTable> table
    ) {
        if (override == null) {
            return group.chanceFor(table);
        }
        if (override.remove().contains(table)) {
            return Optional.empty();
        }
        for (final LootGroup.TableEntry added : override.add()) {
            if (added.table().equals(table)) {
                return Optional.of(added.chance().orElseGet(() -> override.chance().orElse(group.chance())));
            }
        }
        return group.chanceFor(table).map(packChance -> override.chance().orElse(packChance));
    }

    /** The socket template that carries this part - exactly the stack the creative tab holds. */
    private static IntFunction<LootPoolEntryContainer.Builder<?>> partEntry(final Holder<ArmorDecoration> part) {
        return weight -> LootItem.lootTableItem(ModItems.template(part.value().primaryAnchor()))
            .setWeight(weight)
            .apply(SetComponentsFunction.setComponent(ModDataComponents.DECORATION, Tolerant.of(part)));
    }

    private static IntFunction<LootPoolEntryContainer.Builder<?>> skinEntry(final Holder<ArmorSkin> skin) {
        return weight -> LootItem.lootTableItem(ModItems.skinTemplate())
            .setWeight(weight)
            .apply(SetComponentsFunction.setComponent(ModDataComponents.SKIN, Tolerant.of(new ArmorSkinValue(skin))));
    }

    private static IntFunction<LootPoolEntryContainer.Builder<?>> clothEntry(final Holder<Cloth> cloth) {
        return weight -> LootItem.lootTableItem(ModItems.clothTemplate())
            .setWeight(weight)
            .apply(SetComponentsFunction.setComponent(ModDataComponents.CLOTH, Tolerant.of(ClothValue.of(cloth))));
    }

    /**
     * The fitting template naming one fitting. Only ever reached from a group - see
     * {@link LootGroup#fittings()} for why a fitting has no {@code loot} field of its own.
     */
    private static IntFunction<LootPoolEntryContainer.Builder<?>> fittingEntry(final Holder<Fitting> fitting) {
        return weight -> LootItem.lootTableItem(ModItems.fittingTemplate())
            .setWeight(weight)
            .apply(SetComponentsFunction.setComponent(ModDataComponents.FITTING, Tolerant.of(fitting)));
    }

    /** Every entry of one of the mod's registries, or none at all if it is somehow absent. */
    private static <T> List<Holder.Reference<T>> all(
        final HolderLookup.Provider registries,
        final ResourceKey<net.minecraft.core.Registry<T>> key
    ) {
        return registries.lookup(key)
            .map(lookup -> lookup.listElements().toList())
            .orElse(List.of());
    }

    /**
     * The exact route, gathered for the report. Every row on every file is its own chance and its
     * own weight, so what {@code explain} can honestly say about them as a group is how many there
     * were and the best numbers among them.
     */
    private static final class Direct {
        private int rows;
        private float chance;
        private int weight;

        void saw(final DecorationLoot drop) {
            this.rows++;
            this.chance = Math.max(this.chance, drop.chance());
            this.weight = Math.max(this.weight, drop.weight());
        }

        void describe(final List<LootReport.Source> sources) {
            if (this.rows > 0) {
                sources.add(new LootReport.Source(LootReport.DIRECT, this.chance, this.weight, this.rows, false));
            }
        }
    }

    /**
     * The one pool being built for one table, and the rule for what happens when the same thing is
     * offered twice: the highest chance any source asked for, and one entry per member at the best
     * weight it was offered. Insertion-ordered so the pool is written the same way every load.
     */
    private static final class Offers {
        private final Map<Holder<?>, Offer> members = new LinkedHashMap<>();
        private float chance;

        void offer(
            final Holder<?> member,
            final float chance,
            final int weight,
            final IntFunction<LootPoolEntryContainer.Builder<?>> entry
        ) {
            this.chance = Math.max(this.chance, chance);
            final Offer existing = this.members.get(member);
            if (existing == null || weight > existing.weight) {
                this.members.put(member, new Offer(weight, entry));
            }
        }

        boolean isEmpty() {
            return this.members.isEmpty();
        }

        int size() {
            return this.members.size();
        }

        /**
         * @param chance the odds actually to be written - the packs' number after the server's, not
         *               {@link #chance}, which is only what they asked for.
         */
        LootPool.Builder pool(final float chance) {
            final LootPool.Builder pool = LootPool.lootPool().setRolls(ConstantValue.exactly(1.0f));
            // At 1 the condition is the identity and vanilla would roll it anyway; leaving it off
            // keeps "always" readable in the built table.
            if (chance < 1.0f) {
                pool.when(LootItemRandomChanceCondition.randomChance(chance));
            }
            for (final Offer offer : this.members.values()) {
                pool.add(offer.entry.apply(offer.weight));
            }
            return pool;
        }

        private record Offer(int weight, IntFunction<LootPoolEntryContainer.Builder<?>> entry) {}
    }

    private static boolean warned;

    private static void warnOnce() {
        if (!warned) {
            warned = true;
            ArmorPieces.LOGGER.warn(
                "[Armor Pieces] Loot tables loaded without the {} registry; no part will be found in the world.",
                ArmorPiecesRegistries.ARMOR_DECORATION.identifier());
        }
    }

    private static boolean offNoticed;

    private static void offNoticeOnce() {
        if (!offNoticed) {
            offNoticed = true;
            ArmorPieces.LOGGER.info(
                "[Armor Pieces] Loot is off in the server config; no template will be found in the world.");
        }
    }
}
