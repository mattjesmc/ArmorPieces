package com.mattjesmc.armorpieces.registry;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.cloth.ClothValue;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.identity.Tolerant;
import com.mattjesmc.armorpieces.skin.ArmorSkinValue;
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
    public static DataComponentType<Tolerant<Holder<ArmorDecoration>>> DECORATION;

    /**
     * The fitting a fitting template is for, carried on the TEMPLATE stack - the same trade as
     * {@link #DECORATION}, made for the same reason: fittings are data, so a template per fitting is
     * one item and one component, and a pack's new fitting gets its template from a recipe that sets
     * this. Absent on the bare template, which offers the item to every fitting as it always has.
     */
    public static DataComponentType<Tolerant<Holder<Fitting>>> FITTING;

    /**
     * The skin - the armor's own texture - carried by BOTH the skin template that applies it and the
     * armor wearing it. One component for both, because a skin is one thing either way: unlike a
     * part, which is a template's choice on the way in and a socket's occupant afterwards, a skin
     * neither has a place to sit in nor anything to sit beside.
     *
     * <p>On the armor it is the only thing a skinned piece carries, and that is the invariant this
     * component exists to keep: {@code minecraft:equippable} is left exactly as vanilla wrote it, so
     * a skinned piece with this mod stripped out is plain armor again, and a trim over it still
     * darkens on matching material because the trim is still keyed on vanilla's own asset id. The
     * substitution is made at render time and nowhere else - see
     * {@code com.mattjesmc.armorpieces.client.mixin.EquipmentLayerRendererMixin}.
     */
    public static DataComponentType<Tolerant<ArmorSkinValue>> SKIN;

    /**
     * The cloth - a garment worn over the armor's texture - carried by BOTH the cloth template
     * that applies it and the armor wearing it, as the skin is.
     *
     * <p>On a template only the garment is set and the two colour fields sit at their defaults,
     * which is what makes the template's serialised form a bare {@code {"cloth": "..."}} and so
     * what the item model's select matches on. On the armor the colour and the pattern layers are
     * filled in from the banner that was laid beside it - see
     * {@link com.mattjesmc.armorpieces.recipe.SmithingClothRecipe}.
     *
     * <p>It keeps the same invariant {@link #SKIN} does, and by the same means: nothing about
     * {@code minecraft:equippable} is touched, the garment is composited into the armor's texture
     * at render time and nowhere else, and a clothed piece with this mod stripped out is plain
     * armor again.
     */
    public static DataComponentType<Tolerant<ClothValue>> CLOTH;

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
            DataComponentType.<Tolerant<Holder<ArmorDecoration>>>builder()
                .persistent(ArmorDecoration.TOLERANT_CODEC)
                .networkSynchronized(ArmorDecoration.TOLERANT_STREAM_CODEC)
                .build()
        );
        FITTING = Registry.register(
            BuiltInRegistries.DATA_COMPONENT_TYPE,
            Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "fitting"),
            DataComponentType.<Tolerant<Holder<Fitting>>>builder()
                .persistent(Fitting.TOLERANT_CODEC)
                .networkSynchronized(Fitting.TOLERANT_STREAM_CODEC)
                .build()
        );

        SKIN = Registry.register(
            BuiltInRegistries.DATA_COMPONENT_TYPE,
            Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "skin"),
            DataComponentType.<Tolerant<ArmorSkinValue>>builder()
                .persistent(ArmorSkinValue.TOLERANT_CODEC)
                .networkSynchronized(ArmorSkinValue.TOLERANT_STREAM_CODEC)
                .build()
        );

        CLOTH = Registry.register(
            BuiltInRegistries.DATA_COMPONENT_TYPE,
            Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "cloth"),
            DataComponentType.<Tolerant<ClothValue>>builder()
                .persistent(ClothValue.TOLERANT_CODEC)
                .networkSynchronized(ClothValue.TOLERANT_STREAM_CODEC)
                .build()
        );

        // Vanilla only asks the ITEM for its tooltip lines, and vanilla armor has never heard of us -
        // so DECORATIONS being a TooltipProvider is not by itself enough to make a decorated helmet
        // list what it is wearing. This registers the component as a provider for every item, which is
        // the only way to get the line onto an item we did not register. Placed after the trim line so
        // decorations read as a continuation of it rather than as a competing feature.
        ItemComponentTooltipProviderRegistry.addAfter(DataComponents.TRIM, DECORATIONS);
        // The skin goes above the parts and below the trim: the three lines then read outward from
        // the armor itself - what the plate IS, what is painted on it, what is bolted to it. The
        // line only shows on armor; the template says its skin in its own name. See ArmorSkinValue.
        ItemComponentTooltipProviderRegistry.addAfter(DataComponents.TRIM, SKIN);
        // The cloth sits between the skin and the parts, which is where it sits on the body: what
        // the plate IS, what is painted on it, what is worn over it, what is bolted on top.
        ItemComponentTooltipProviderRegistry.addAfter(DataComponents.TRIM, CLOTH);

        ArmorPieces.LOGGER.info("[Armor Pieces] Registered data components.");
    }
}
