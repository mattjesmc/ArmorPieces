package com.mattjesmc.armorpieces.registry;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.loot.SetDecorationFunction;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;

/**
 * The loot functions the mod adds. One: {@code armorpieces:set_decoration}, which puts a part on a
 * piece of armor a table hands out. Parts themselves reach tables another way - by naming them on
 * the part's data file - so this is for the rarer case of finding decorated armor rather than a
 * template. See {@link SetDecorationFunction}.
 */
public final class ModLootFunctions {
    private ModLootFunctions() {}

    public static void register() {
        Registry.register(
            BuiltInRegistries.LOOT_FUNCTION_TYPE,
            Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "set_decoration"),
            SetDecorationFunction.MAP_CODEC);
    }
}
