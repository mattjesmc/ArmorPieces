package com.mattjesmc.armorpieces.registry;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.loot.TemplateEntry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;

/**
 * The loot pool entry types the mod adds. One: {@code armorpieces:template}, which lets somebody
 * else's loot table offer a member of a tag of ours - see {@link TemplateEntry} for why a tag rather
 * than a named part.
 *
 * <p>Registered in the initializer like every other type a datapack may name, since a loot table
 * naming an entry type that does not exist yet fails to parse.
 */
public final class ModLootEntries {
    private ModLootEntries() {}

    public static void register() {
        Registry.register(
            BuiltInRegistries.LOOT_POOL_ENTRY_TYPE,
            Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "template"),
            TemplateEntry.MAP_CODEC);
    }
}
