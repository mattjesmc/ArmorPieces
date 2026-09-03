package com.mattjesmc.armorpieces.decoration;

import java.util.EnumMap;
import java.util.HashMap;
import java.util.Map;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.BannerItem;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.equipment.trim.TrimMaterial;

/**
 * The item that stands for a material - the ingot behind "gold", the emerald behind "emerald", the
 * lapis behind "blue" - for the advanced smithing table's rows, where a slot has to show at a glance
 * what a part or a fitting was made of.
 *
 * <p>A trim material is not an item and has no field naming one: it is a palette and a name, and
 * what puts it on a piece is whatever carries {@code provides_trim_material}. So the mapping is read
 * back out of the items themselves rather than declared anywhere - every item is asked what material
 * it provides, and the first to answer for a material is that material's face. That is what makes a
 * datapack's new material show an icon without saying anything: it ships the item that provides it,
 * and the item is found. A material nothing provides has no icon, and callers fall back to its
 * colour.
 *
 * <p>Dyes and banners are looked up the same way and for the same reason - the fitting values that
 * hold them are a {@link DyeColor}, not an item.
 *
 * <p>Built once, on first use, from the item registry, which is static and frozen by then. Keyed by
 * {@link ResourceKey} rather than by holder because the holder a material travels in belongs to
 * whichever registry access asked for it, and two of those are not the same object.
 */
public final class MaterialIcons {
    private MaterialIcons() {
    }

    /** The item that provides {@code material}, or empty if nothing does. */
    public static ItemStack forTrimMaterial(final Holder<TrimMaterial> material) {
        return material.unwrapKey().map(key -> stack(Lookup.MATERIALS.get(key))).orElse(ItemStack.EMPTY);
    }

    /** The dye of this colour, or empty. */
    public static ItemStack forDye(final DyeColor colour) {
        return stack(Lookup.DYES.get(colour));
    }

    /** The banner of this colour, or empty. */
    public static ItemStack forBanner(final DyeColor colour) {
        return stack(Lookup.BANNERS.get(colour));
    }

    private static ItemStack stack(final Item item) {
        return item == null ? ItemStack.EMPTY : new ItemStack(item);
    }

    /** Held apart so the one pass over the item registry happens on first use and only once. */
    private static final class Lookup {
        private static final Map<ResourceKey<TrimMaterial>, Item> MATERIALS = new HashMap<>();
        private static final Map<DyeColor, Item> DYES = new EnumMap<>(DyeColor.class);
        private static final Map<DyeColor, Item> BANNERS = new EnumMap<>(DyeColor.class);

        static {
            for (final Item item : BuiltInRegistries.ITEM) {
                final ItemStack stack = item.getDefaultInstance();
                final Holder<TrimMaterial> material = stack.get(DataComponents.PROVIDES_TRIM_MATERIAL);
                if (material != null) {
                    material.unwrapKey().ifPresent(key -> MATERIALS.putIfAbsent(key, item));
                }
                final DyeColor dye = stack.get(DataComponents.DYE);
                if (dye != null) {
                    DYES.putIfAbsent(dye, item);
                }
                if (item instanceof BannerItem banner) {
                    BANNERS.putIfAbsent(banner.getColor(), item);
                }
            }
        }
    }
}
