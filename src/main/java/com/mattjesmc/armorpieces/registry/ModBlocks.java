package com.mattjesmc.armorpieces.registry;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.block.AdvancedSmithingTableBlock;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;

/**
 * The mod's blocks: the advanced smithing table, and nothing else.
 *
 * <p>One block, registered by hand rather than through a helper, because a helper for one entry is
 * a promise of more and there is no plan for more. Everything a part IS stays data; the table is the
 * one thing a player stands in front of.
 */
public final class ModBlocks {
    public static final ResourceKey<Block> ADVANCED_SMITHING_TABLE_KEY = ResourceKey.create(
        Registries.BLOCK, Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "advanced_smithing_table"));

    private static Block advancedSmithingTable;
    private static Item advancedSmithingTableItem;

    private ModBlocks() {}

    public static void register() {
        // The same material line as the vanilla smithing table, so it mines, sounds and burns alike.
        advancedSmithingTable = Registry.register(
            BuiltInRegistries.BLOCK,
            ADVANCED_SMITHING_TABLE_KEY,
            new AdvancedSmithingTableBlock(BlockBehaviour.Properties.of()
                .setId(ADVANCED_SMITHING_TABLE_KEY)
                .mapColor(MapColor.WOOD)
                .strength(2.5F)
                .sound(SoundType.WOOD)
                .ignitedByLava()));
        final ResourceKey<Item> itemKey = ResourceKey.create(Registries.ITEM, ADVANCED_SMITHING_TABLE_KEY.identifier());
        advancedSmithingTableItem = Registry.register(
            BuiltInRegistries.ITEM,
            itemKey,
            new BlockItem(advancedSmithingTable, new Item.Properties().setId(itemKey).useBlockDescriptionPrefix()));
        ArmorPieces.LOGGER.info("[Armor Pieces] Registered the advanced smithing table.");
    }

    public static Block advancedSmithingTable() {
        return advancedSmithingTable;
    }

    public static Item advancedSmithingTableItem() {
        return advancedSmithingTableItem;
    }
}
