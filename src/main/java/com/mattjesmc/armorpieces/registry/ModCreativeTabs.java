package com.mattjesmc.armorpieces.registry;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import net.fabricmc.fabric.api.creativetab.v1.FabricCreativeModeTab;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;

/**
 * The creative tab, built by WALKING THE REGISTRY rather than from a hardcoded list.
 *
 * <p>That is the part that matters: the contents are derived from the loaded
 * {@code armorpieces:armor_decoration} registry crossed with each part's declared anchors, so a part
 * added by a datapack appears in creative - and in the search tab, and under {@code /give} - the
 * moment the pack is loaded, with nothing registered on our side. A hardcoded tab would have made
 * "fully expandable" quietly false for anyone who does not play in survival.
 *
 * <p>Grouped by socket, not by part, so the tab reads head-to-toe and a player looking for "something
 * for the shoulders" finds every option together.
 */
public final class ModCreativeTabs {
    public static final ResourceKey<CreativeModeTab> DECORATIONS = ResourceKey.create(
        Registries.CREATIVE_MODE_TAB, Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "decorations"));

    private ModCreativeTabs() {}

    public static void register() {
        Registry.register(
            BuiltInRegistries.CREATIVE_MODE_TAB,
            DECORATIONS,
            FabricCreativeModeTab.builder()
                .title(Component.translatable("itemGroup.armorpieces.decorations"))
                .icon(() -> new ItemStack(ModItems.template(DecorationAnchor.CREST)))
                .displayItems((parameters, output) -> parameters.holders()
                    .lookup(ArmorPiecesRegistries.ARMOR_DECORATION)
                    .ifPresent(lookup -> {
                        for (final DecorationAnchor anchor : DecorationAnchor.values()) {
                            lookup.listElements()
                                .filter(decoration -> decoration.value().fits(anchor))
                                .forEach(decoration -> output.accept(ModItems.templateFor(anchor, decoration)));
                        }
                    }))
                .build());
        ArmorPieces.LOGGER.info("[Armor Pieces] Registered creative tab.");
    }
}
