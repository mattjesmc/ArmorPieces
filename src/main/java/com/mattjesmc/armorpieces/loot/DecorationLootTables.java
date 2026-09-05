package com.mattjesmc.armorpieces.loot;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.cloth.Cloth;
import com.mattjesmc.armorpieces.cloth.ClothValue;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.DecorationLoot;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.registry.ModItems;
import com.mattjesmc.armorpieces.skin.ArmorSkin;
import com.mattjesmc.armorpieces.skin.ArmorSkinValue;
import java.util.List;
import net.fabricmc.fabric.api.loot.v3.LootTableEvents;
import net.fabricmc.fabric.api.loot.v3.LootTableSource;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderLookup;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.storage.loot.LootPool;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.level.storage.loot.entries.LootItem;
import net.minecraft.world.level.storage.loot.functions.SetComponentsFunction;
import net.minecraft.world.level.storage.loot.predicates.LootItemRandomChanceCondition;
import net.minecraft.world.level.storage.loot.providers.number.ConstantValue;

/**
 * Puts parts and skins into loot tables: the {@code loot} list on a part's or a skin's data file,
 * made real.
 *
 * <p>Runs as each loot table is loaded, on world start and on {@code /reload} alike, and walks the
 * whole {@code armorpieces:armor_decoration} registry looking for parts that name the table. The
 * registry is there to walk because loot tables are the last thing loaded: they are built against
 * the full registry access, dynamic registries included, and the event hands that access over.
 *
 * <p>What it adds is one pool per table, rolled once, with an entry per part - the part's socket
 * template carrying the part as {@code armorpieces:decoration}, exactly the stack the creative tab
 * holds, so the thing found in the chest is the thing the smithing table takes. Each entry has its
 * own weight and its own {@code random_chance} condition; see {@link DecorationLoot} for what the
 * two numbers mean under this shape. The table's own pools are untouched: a chest that would have
 * held a diamond still holds it, with or without a part beside it.
 *
 * <p>Skins ride in the same pool, from the same {@code loot} list and through the same two numbers -
 * a skin is found the way a part is, and it costs no code of its own to be. One pool rather than two
 * because the pool rolls ONCE: a chest that offered a part and a skin from separate pools could hand
 * out both, and a skin template is a whole look for a whole suit rather than one more trinket.
 *
 * <p>Nothing here is specific to the mod's own parts. A pack's part that names a table is added to
 * it the same way, which is the whole reason this is done in Java: a datapack can replace a vanilla
 * table but cannot add to one, and two packs that both replace {@code chests/ancient_city} cannot
 * both win.
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

        LootPool.Builder pool = null;
        int entries = 0;
        for (final Holder.Reference<ArmorDecoration> part : parts.listElements().toList()) {
            for (final DecorationLoot drop : part.value().loot()) {
                if (!drop.table().equals(key)) {
                    continue;
                }
                if (pool == null) {
                    pool = LootPool.lootPool().setRolls(ConstantValue.exactly(1.0f));
                }
                pool.add(LootItem.lootTableItem(ModItems.template(part.value().primaryAnchor()))
                    .setWeight(drop.weight())
                    .when(LootItemRandomChanceCondition.randomChance(drop.chance()))
                    .apply(SetComponentsFunction.setComponent(ModDataComponents.DECORATION, part)));
                entries++;
            }
        }
        // Skins, into the same pool, from the same field. A skin registry that is somehow absent is
        // not worth a second warning: the parts' one has already been given.
        for (final Holder.Reference<ArmorSkin> skin : registries.lookup(ArmorPiecesRegistries.ARMOR_SKIN)
            .map(lookup -> lookup.listElements().toList())
            .orElse(List.of())) {
            for (final DecorationLoot drop : skin.value().loot()) {
                if (!drop.table().equals(key)) {
                    continue;
                }
                if (pool == null) {
                    pool = LootPool.lootPool().setRolls(ConstantValue.exactly(1.0f));
                }
                pool.add(LootItem.lootTableItem(ModItems.skinTemplate())
                    .setWeight(drop.weight())
                    .when(LootItemRandomChanceCondition.randomChance(drop.chance()))
                    .apply(SetComponentsFunction.setComponent(
                        ModDataComponents.SKIN, new ArmorSkinValue(skin))));
                entries++;
            }
        }
        // Cloths, into the same pool again, from the same field.
        for (final Holder.Reference<Cloth> cloth : registries.lookup(ArmorPiecesRegistries.CLOTH)
            .map(lookup -> lookup.listElements().toList())
            .orElse(List.of())) {
            for (final DecorationLoot drop : cloth.value().loot()) {
                if (!drop.table().equals(key)) {
                    continue;
                }
                if (pool == null) {
                    pool = LootPool.lootPool().setRolls(ConstantValue.exactly(1.0f));
                }
                pool.add(LootItem.lootTableItem(ModItems.clothTemplate())
                    .setWeight(drop.weight())
                    .when(LootItemRandomChanceCondition.randomChance(drop.chance()))
                    .apply(SetComponentsFunction.setComponent(
                        ModDataComponents.CLOTH, ClothValue.of(cloth))));
                entries++;
            }
        }
        if (pool != null) {
            table.withPool(pool);
            ArmorPieces.LOGGER.debug(
                "[Armor Pieces] Added {} template(s) to loot table {}", entries, key.identifier());
        }
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
