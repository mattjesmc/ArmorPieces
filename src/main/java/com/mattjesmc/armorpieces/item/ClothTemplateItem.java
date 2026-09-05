package com.mattjesmc.armorpieces.item;

import com.mattjesmc.armorpieces.cloth.ClothValue;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import java.util.function.Consumer;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.CommonComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;

/**
 * The smithing template that puts a garment on a piece of armor - one item for every cloth there
 * will ever be, with the cloth itself riding on the stack as {@link ModDataComponents#CLOTH}.
 *
 * <p>The same trade the socket templates, the fitting template and the skin template make, for the
 * same reason: cloths are data in a registry a datapack adds to, so an item per cloth would close a
 * list that is meant to be open.
 *
 * <p>What goes in the third slot IS named here, and it is the one template of the four that can name
 * it: a banner. Everything the player chose about the garment - its colour and up to six layers of
 * pattern - is on that banner, made at a loom, which is already the best pattern editor the game
 * has. It is consumed, as it is for a shield.
 */
public class ClothTemplateItem extends Item {
    public ClothTemplateItem(final Properties properties) {
        super(properties);
    }

    /** "Tunic Cloth Smithing Template", from the cloth's own description. */
    @Override
    public Component getName(final ItemStack stack) {
        final ClothValue cloth = stack.get(ModDataComponents.CLOTH);
        if (cloth == null) {
            return super.getName(stack);
        }
        return Component.translatable(
            "item.armorpieces.decoration_template",
            cloth.cloth().value().description(),
            super.getName(stack));
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
            Component.translatable("item.armorpieces.cloth_template.applies_to").withStyle(ChatFormatting.BLUE)));
        consumer.accept(Component.translatable("item.armorpieces.template.ingredients").withStyle(ChatFormatting.GRAY));
        consumer.accept(CommonComponents.space().append(
            Component.translatable("item.armorpieces.cloth_template.ingredients").withStyle(ChatFormatting.BLUE)));
    }
}
