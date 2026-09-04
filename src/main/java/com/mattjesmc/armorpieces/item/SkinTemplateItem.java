package com.mattjesmc.armorpieces.item;

import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.skin.ArmorSkinValue;
import java.util.function.Consumer;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.CommonComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;

/**
 * The smithing template that reskins a piece of armor - one item for every skin there will ever be,
 * with the skin itself riding on the stack as {@link ModDataComponents#SKIN}.
 *
 * <p>The same trade the socket templates and the fitting template make, for the same reason: skins
 * are data in a registry a datapack adds to, so an item per skin would close a list that is meant to
 * be open. A pack that ships a {@code carapace} skin gets a carapace template out of a recipe whose
 * result carries the component, with no Java and no item registration.
 *
 * <p>What goes in the third slot is not named here either, and cannot be: it is the piece's own
 * REFORGING material - an iron ingot for iron, a diamond for diamond - which only the piece can say.
 * The tooltip therefore promises "the armor's own material" rather than a list, and
 * {@link com.mattjesmc.armorpieces.recipe.SmithingSkinRecipe} asks the armor.
 */
public class SkinTemplateItem extends Item {
    public SkinTemplateItem(final Properties properties) {
        super(properties);
    }

    /** "Plate Skin Smithing Template", from the skin's own description; bare, just the item's name. */
    @Override
    public Component getName(final ItemStack stack) {
        final ArmorSkinValue skin = stack.get(ModDataComponents.SKIN);
        if (skin == null) {
            return super.getName(stack);
        }
        return Component.translatable(
            "item.armorpieces.decoration_template", skin.description(), super.getName(stack));
    }

    /** The vanilla smithing-template tooltip shape: what it goes on, and what goes in. */
    @Override
    public void appendHoverText(
        final ItemStack stack,
        final TooltipContext context,
        final TooltipDisplay display,
        final Consumer<Component> consumer,
        final TooltipFlag flag
    ) {
        consumer.accept(CommonComponents.EMPTY);
        consumer.accept(Component.translatable("item.armorpieces.template.applies_to").withStyle(ChatFormatting.GRAY));
        consumer.accept(CommonComponents.space().append(
            Component.translatable("item.armorpieces.skin_template.applies_to").withStyle(ChatFormatting.BLUE)));
        consumer.accept(Component.translatable("item.armorpieces.template.ingredients").withStyle(ChatFormatting.GRAY));
        consumer.accept(CommonComponents.space().append(
            Component.translatable("item.armorpieces.skin_template.ingredients").withStyle(ChatFormatting.BLUE)));
    }
}
