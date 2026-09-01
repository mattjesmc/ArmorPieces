package com.mattjesmc.armorpieces.registry;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.item.DecorationTemplateItem;
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
 * The mod's items: exactly one smithing template per {@link DecorationAnchor}, and nothing else.
 *
 * <p>The count is bounded by the anchor enum on purpose. Registering an item per PART would make the
 * part list compiled-in and undo the whole datapack story; registering one per SOCKET costs the same
 * ten registrations forever, because the socket list is closed anyway. Which part a template applies
 * is carried on the stack - see {@link DecorationTemplateItem}.
 */
public final class ModItems {
    private static final Map<DecorationAnchor, DecorationTemplateItem> TEMPLATES =
        new EnumMap<>(DecorationAnchor.class);

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
        ArmorPieces.LOGGER.info("[Armor Pieces] Registered {} decoration templates.", TEMPLATES.size());
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
