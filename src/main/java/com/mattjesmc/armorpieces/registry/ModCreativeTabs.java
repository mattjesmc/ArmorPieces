package com.mattjesmc.armorpieces.registry;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.config.PartsSwitch;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import java.util.function.Predicate;
import net.fabricmc.fabric.api.creativetab.v1.FabricCreativeModeTab;
import net.minecraft.core.Holder;
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
 *
 * <p>Less what the server has switched off ({@link PartsSwitch}): the tab is where a player is
 * OFFERED a part, and a server that does not offer one should not offer it here either. The tab is
 * rebuilt on the next join after the setting changes; a {@code /reload} moves the loot and the
 * recipes at once but the client keeps the tab it built.
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
                        // What the server offers. The tab is built here on the client, so this is
                        // the server's word as last told to it (PartsSwitchPayload), or this JVM's
                        // own file off any server. A switched-off member is simply not listed.
                        final PartsSwitch offered = PartsSwitch.shown();
                        final Predicate<Holder<?>> shown = member -> offered.offers(member, parameters.holders());
                        // First, before any part: the one block, since a player who has found the
                        // tab is looking for the place the rest of it is used.
                        output.accept(new ItemStack(ModBlocks.advancedSmithingTableItem()));
                        for (final DecorationAnchor anchor : DecorationAnchor.values()) {
                            lookup.listElements()
                                .filter(decoration -> decoration.value().fits(anchor))
                                .filter(shown)
                                .forEach(decoration -> output.accept(ModItems.templateFor(anchor, decoration)));
                        }
                        // Last, after every part: a fitting template per fitting in the registry -
                        // gemstone, guard, inlay, banner, and any a pack adds - then the bare one that
                        // fits anything into whatever the piece already wears.
                        parameters.holders()
                            .lookup(ArmorPiecesRegistries.FITTING)
                            .ifPresent(fittings -> fittings.listElements()
                                .filter(shown)
                                .forEach(fitting -> output.accept(ModItems.fittingTemplateFor(fitting))));
                        output.accept(new ItemStack(ModItems.fittingTemplate()));
                        // Then the skins, which are not parts at all: one template per entry of
                        // armorpieces:armor_skin, a pack's included, walked the same way.
                        parameters.holders()
                            .lookup(ArmorPiecesRegistries.ARMOR_SKIN)
                            .ifPresent(skins -> skins.listElements()
                                .filter(shown)
                                .forEach(skin -> output.accept(ModItems.skinTemplateFor(skin))));
                        // Then the cloths, walked the same way again. Last of all, because a garment
                        // is the outermost thing a piece can wear that is not a part.
                        parameters.holders()
                            .lookup(ArmorPiecesRegistries.CLOTH)
                            .ifPresent(cloths -> cloths.listElements()
                                .filter(shown)
                                .forEach(cloth -> output.accept(ModItems.clothTemplateFor(cloth))));
                    }))
                .build());
        ArmorPieces.LOGGER.info("[Armor Pieces] Registered creative tab.");
    }
}
