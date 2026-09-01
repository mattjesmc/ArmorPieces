package com.mattjesmc.armorpieces.registry;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import net.fabricmc.fabric.api.item.v1.ItemComponentTooltipProviderRegistry;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;

/** Item data components. */
public final class ModDataComponents {
    /**
     * Every decorative part on one armor piece, keyed by socket.
     *
     * <p>Deliberately a component of our own beside {@code minecraft:trim} rather than an extension
     * of it. Two consequences, both wanted: a piece can carry a trim AND decorations at once, and a
     * decorated piece degrades gracefully - strip this mod and the armor is still a valid, still
     * trimmed item rather than one carrying a component nothing can read.
     */
    public static DataComponentType<ArmorDecorations> DECORATIONS;

    /**
     * The part a smithing template applies, carried on the TEMPLATE stack rather than baked into a
     * template item.
     *
     * <p>This one component is what keeps the mod expandable now that templates are real items. The
     * item fixes the socket (there is one template item per anchor, and the anchor set is closed);
     * this component fixes the part, and the part registry is datapack-driven. So a pack adds a part
     * and its template exists immediately - obtainable by recipe, by loot table or from the creative
     * tab - with no item registered and no code run. It is the same trade vanilla makes for potions:
     * one item, open contents.
     */
    public static DataComponentType<Holder<ArmorDecoration>> DECORATION;

    private ModDataComponents() {}

    public static void register() {
        DECORATIONS = Registry.register(
            BuiltInRegistries.DATA_COMPONENT_TYPE,
            Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "decorations"),
            DataComponentType.<ArmorDecorations>builder()
                .persistent(ArmorDecorations.CODEC)                  // survives save/load
                .networkSynchronized(ArmorDecorations.STREAM_CODEC)  // the client draws it, so it must travel
                .build()
        );
        DECORATION = Registry.register(
            BuiltInRegistries.DATA_COMPONENT_TYPE,
            Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "decoration"),
            DataComponentType.<Holder<ArmorDecoration>>builder()
                .persistent(ArmorDecoration.CODEC)
                .networkSynchronized(ArmorDecoration.STREAM_CODEC)
                .build()
        );

        // Vanilla only asks the ITEM for its tooltip lines, and vanilla armor has never heard of us -
        // so DECORATIONS being a TooltipProvider is not by itself enough to make a decorated helmet
        // list what it is wearing. This registers the component as a provider for every item, which is
        // the only way to get the line onto an item we did not register. Placed after the trim line so
        // decorations read as a continuation of it rather than as a competing feature.
        ItemComponentTooltipProviderRegistry.addAfter(DataComponents.TRIM, DECORATIONS);

        ArmorPieces.LOGGER.info("[Armor Pieces] Registered data components.");
    }
}
