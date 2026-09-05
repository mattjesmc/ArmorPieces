package com.mattjesmc.armorpieces.registry;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.cloth.Cloth;
import com.mattjesmc.armorpieces.cloth.ClothValue;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.item.ClothTemplateItem;
import com.mattjesmc.armorpieces.item.DecorationTemplateItem;
import com.mattjesmc.armorpieces.item.FittingTemplateItem;
import com.mattjesmc.armorpieces.item.SkinTemplateItem;
import com.mattjesmc.armorpieces.skin.ArmorSkin;
import com.mattjesmc.armorpieces.skin.ArmorSkinValue;
import java.util.EnumMap;
import java.util.Map;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;

/**
 * The mod's items: exactly one smithing template per {@link DecorationAnchor}, plus the one fitting
 * template, the one skin template and the one cloth template, and nothing else.
 *
 * <p>The count is bounded by the anchor enum on purpose. Registering an item per PART would make the
 * part list compiled-in and undo the whole datapack story; registering one per SOCKET costs the same
 * twelve registrations forever - thirteen items with the fitting template - because the socket list
 * is closed anyway. Which part a template applies
 * is carried on the stack - see {@link DecorationTemplateItem}.
 *
 * <p>The fitting template is one item for every fitting there will ever be, because the ITEM placed
 * beside it decides where it goes - see {@link FittingTemplateItem}. The skin template is one item
 * for every skin, for the plainer reason that skins are a datapack registry - see
 * {@link SkinTemplateItem}; the cloth template is one item for every cloth, for the same reason
 * again - see {@link ClothTemplateItem}.
 */
public final class ModItems {
    private static final Map<DecorationAnchor, DecorationTemplateItem> TEMPLATES =
        new EnumMap<>(DecorationAnchor.class);
    private static FittingTemplateItem fittingTemplate;
    private static SkinTemplateItem skinTemplate;
    private static ClothTemplateItem clothTemplate;

    private ModItems() {}

    public static void register() {
        for (final DecorationAnchor anchor : DecorationAnchor.values()) {
            final ResourceKey<Item> key = ResourceKey.create(
                Registries.ITEM,
                Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, anchor.getSerializedName() + "_template"));
            final DecorationTemplateItem item = new DecorationTemplateItem(
                anchor, new Item.Properties().setId(key).rarity(Rarity.UNCOMMON));
            TEMPLATES.put(anchor, Registry.register(BuiltInRegistries.ITEM, key, item));
        }
        final ResourceKey<Item> fittingKey = ResourceKey.create(
            Registries.ITEM, Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "fitting_template"));
        fittingTemplate = Registry.register(
            BuiltInRegistries.ITEM,
            fittingKey,
            new FittingTemplateItem(new Item.Properties().setId(fittingKey).rarity(Rarity.UNCOMMON)));
        final ResourceKey<Item> skinKey = ResourceKey.create(
            Registries.ITEM, Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "skin_template"));
        skinTemplate = Registry.register(
            BuiltInRegistries.ITEM,
            skinKey,
            new SkinTemplateItem(new Item.Properties().setId(skinKey).rarity(Rarity.UNCOMMON)));
        final ResourceKey<Item> clothKey = ResourceKey.create(
            Registries.ITEM, Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "cloth_template"));
        clothTemplate = Registry.register(
            BuiltInRegistries.ITEM,
            clothKey,
            new ClothTemplateItem(new Item.Properties().setId(clothKey).rarity(Rarity.UNCOMMON)));
        ArmorPieces.LOGGER.info(
            "[Armor Pieces] Registered {} decoration templates and the fitting, skin and cloth templates.",
            TEMPLATES.size());
    }

    /** The template that sets a second material into a part already on the armor. */
    public static FittingTemplateItem fittingTemplate() {
        return fittingTemplate;
    }

    /**
     * A fitting template naming one fitting - the stack a recipe with the component in its result
     * produces. The one place it is built, so the creative tab and a command agree.
     */
    public static ItemStack fittingTemplateFor(final Holder<Fitting> fitting) {
        final ItemStack stack = new ItemStack(fittingTemplate);
        stack.set(ModDataComponents.FITTING, fitting);
        return stack;
    }

    /** The template that reskins a piece of armor. */
    public static SkinTemplateItem skinTemplate() {
        return skinTemplate;
    }

    /**
     * A skin template naming one skin - the stack a recipe with the component in its result
     * produces, and the one the creative tab and a loot table hand out.
     */
    public static ItemStack skinTemplateFor(final Holder<ArmorSkin> skin) {
        final ItemStack stack = new ItemStack(skinTemplate);
        stack.set(ModDataComponents.SKIN, new ArmorSkinValue(skin));
        return stack;
    }

    /** The template that puts a garment on a piece of armor. */
    public static ClothTemplateItem clothTemplate() {
        return clothTemplate;
    }

    /**
     * A cloth template naming one garment, with no design on it yet - the design arrives off the
     * banner at the table. The one place it is built, so the creative tab, a recipe and a loot table
     * agree on what a valid cloth template looks like.
     */
    public static ItemStack clothTemplateFor(final Holder<Cloth> cloth) {
        final ItemStack stack = new ItemStack(clothTemplate);
        stack.set(ModDataComponents.CLOTH, ClothValue.of(cloth));
        return stack;
    }

    /** The template item for a socket. Never null - every anchor has one by construction. */
    public static DecorationTemplateItem template(final DecorationAnchor anchor) {
        return TEMPLATES.get(anchor);
    }

    /**
     * A ready-to-use template stack. The one place a template is built, so the creative tab, a
     * command and anything else agree on what a valid template looks like.
     */
    public static ItemStack templateFor(final DecorationAnchor anchor, final Holder<ArmorDecoration> decoration) {
        final ItemStack stack = new ItemStack(template(anchor));
        stack.set(ModDataComponents.DECORATION, decoration);
        return stack;
    }
}
