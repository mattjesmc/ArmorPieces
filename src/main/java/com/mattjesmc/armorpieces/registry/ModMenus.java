package com.mattjesmc.armorpieces.registry;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.menu.AdvancedSmithingMenu;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import net.minecraft.world.flag.FeatureFlags;
import net.minecraft.world.inventory.MenuType;

/** Menu types. One: the advanced smithing table's. */
public final class ModMenus {
    public static MenuType<AdvancedSmithingMenu> ADVANCED_SMITHING;

    private ModMenus() {}

    public static void register() {
        // A plain MenuType rather than Fabric's extended one: the menu carries no opening data. The
        // client builds it from the container id and the inventory alone, and everything else - the
        // four display stacks, the selection, whether Apply has a result - arrives through the
        // ordinary slot and data-slot sync.
        ADVANCED_SMITHING = Registry.register(
            BuiltInRegistries.MENU,
            Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "advanced_smithing"),
            new MenuType<>(AdvancedSmithingMenu::new, FeatureFlags.VANILLA_SET));
        ArmorPieces.LOGGER.info("[Armor Pieces] Registered menu types.");
    }
}
