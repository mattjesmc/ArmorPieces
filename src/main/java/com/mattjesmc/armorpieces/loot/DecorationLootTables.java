package com.mattjesmc.armorpieces.loot;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.cloth.Cloth;
import com.mattjesmc.armorpieces.cloth.ClothValue;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.DecorationLoot;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.registry.ModItems;
import com.mattjesmc.armorpieces.skin.ArmorSkin;
import com.mattjesmc.armorpieces.skin.ArmorSkinValue;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.IntFunction;
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
 */
public final class DecorationLootTables {
    private DecorationLootTables() {}

    public static void register() {
        LootTableEvents.MODIFY.register(DecorationLootTables::modify);
    }

    private static void modify(
        final ResourceKey<LootTable> key,
        final LootTable.Builder table,
        final LootTableSource source,
        final HolderLookup.Provider registries
    ) {
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

        // 1. The exact route: a table named on the part's, skin's or cloth's own data file. One
        //    part, one table, its own chance and weight - which is what a hand-placed "wings in end
        //    cities" is, and what a pack writes when it wants no group at all.
        for (final Holder.Reference<ArmorDecoration> part : parts.listElements().toList()) {
            for (final DecorationLoot drop : part.value().loot()) {
                if (drop.table().equals(key)) {
                    offers.offer(part, drop.chance(), drop.weight(), partEntry(part));
                }
            }
        }
        for (final Holder.Reference<ArmorSkin> skin : skins) {
            for (final DecorationLoot drop : skin.value().loot()) {
                if (drop.table().equals(key)) {
                    offers.offer(skin, drop.chance(), drop.weight(), skinEntry(skin));
                }
            }
        }
        for (final Holder.Reference<Cloth> cloth : cloths) {
            for (final DecorationLoot drop : cloth.value().loot()) {
                if (drop.table().equals(key)) {
                    offers.offer(cloth, drop.chance(), drop.weight(), clothEntry(cloth));
                }
            }
        }

        // 2. The route that scales: a group naming this table, and everything tagged into it.
        for (final Holder.Reference<LootGroup> holder : all(registries, ArmorPiecesRegistries.LOOT_GROUP)) {
            final LootGroup group = holder.value();
            final Optional<Float> chance = group.chanceFor(key);
            if (chance.isEmpty()) {
                continue;
            }
            final float c = chance.get();
            for (final Holder<ArmorDecoration> part : group.parts()) {
                offers.offer(part, c, group.weight(), partEntry(part));
            }
            for (final Holder<ArmorSkin> skin : group.skins()) {
                offers.offer(skin, c, group.weight(), skinEntry(skin));
            }
            for (final Holder<Cloth> cloth : group.cloths()) {
                offers.offer(cloth, c, group.weight(), clothEntry(cloth));
            }
            for (final Holder<Fitting> fitting : group.fittings()) {
                offers.offer(fitting, c, group.weight(), fittingEntry(fitting));
            }
        }

        if (offers.isEmpty()) {
            return;
        }
        table.withPool(offers.pool());
        ArmorPieces.LOGGER.debug(
            "[Armor Pieces] Added {} template(s) to loot table {} at chance {}",
            offers.size(), key.identifier(), offers.chance);
    }

    /** The socket template that carries this part - exactly the stack the creative tab holds. */
    private static IntFunction<LootPoolEntryContainer.Builder<?>> partEntry(final Holder<ArmorDecoration> part) {
        return weight -> LootItem.lootTableItem(ModItems.template(part.value().primaryAnchor()))
            .setWeight(weight)
            .apply(SetComponentsFunction.setComponent(ModDataComponents.DECORATION, part));
    }

    private static IntFunction<LootPoolEntryContainer.Builder<?>> skinEntry(final Holder<ArmorSkin> skin) {
        return weight -> LootItem.lootTableItem(ModItems.skinTemplate())
            .setWeight(weight)
            .apply(SetComponentsFunction.setComponent(ModDataComponents.SKIN, new ArmorSkinValue(skin)));
    }

    private static IntFunction<LootPoolEntryContainer.Builder<?>> clothEntry(final Holder<Cloth> cloth) {
        return weight -> LootItem.lootTableItem(ModItems.clothTemplate())
            .setWeight(weight)
            .apply(SetComponentsFunction.setComponent(ModDataComponents.CLOTH, ClothValue.of(cloth)));
    }

    /**
     * The fitting template naming one fitting. Only ever reached from a group - see
     * {@link LootGroup#fittings()} for why a fitting has no {@code loot} field of its own.
     */
    private static IntFunction<LootPoolEntryContainer.Builder<?>> fittingEntry(final Holder<Fitting> fitting) {
        return weight -> LootItem.lootTableItem(ModItems.fittingTemplate())
            .setWeight(weight)
            .apply(SetComponentsFunction.setComponent(ModDataComponents.FITTING, fitting));
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

        LootPool.Builder pool() {
            final LootPool.Builder pool = LootPool.lootPool().setRolls(ConstantValue.exactly(1.0f));
            // At 1 the condition is the identity and vanilla would roll it anyway; leaving it off
            // keeps "always" readable in the built table.
            if (this.chance < 1.0f) {
                pool.when(LootItemRandomChanceCondition.randomChance(this.chance));
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
}
