package com.mattjesmc.armorpieces.item;

import java.util.function.Consumer;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.CommonComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;

/**
 * The smithing template that sets a second material into a part - a gem into a circlet's stone, a
 * dye into a sash, a banner onto a back banner.
 *
 * <p>One item, not one per fitting, and the reason is the smithing table's third slot: the ITEM put
 * there decides which fitting it fills. A gem can only go where gems go, a dye where dye goes, and a
 * banner where a banner goes, so the template never has to say. That is what keeps the fitting list
 * open - a pack's new fitting is reachable from this same template the moment a part lists it - and
 * it is also why there is a template at all rather than none: a smithing recipe with an empty
 * template slot is legal, but the recipe book would never show it, and a player would never find it.
 *
 * <p>Applies to armor that already wears a part with a fitting for the item; the recipe itself
 * decides that, see {@link com.mattjesmc.armorpieces.recipe.SmithingFittingRecipe}.
 */
public class FittingTemplateItem extends Item {
    public FittingTemplateItem(final Properties properties) {
        super(properties);
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
        consumer.accept(CommonComponents.space()
            .append(Component.translatable("item.armorpieces.fitting_template.applies_to").withStyle(ChatFormatting.BLUE)));
        consumer.accept(Component.translatable("item.armorpieces.template.ingredients").withStyle(ChatFormatting.GRAY));
        consumer.accept(CommonComponents.space()
            .append(Component.translatable("item.armorpieces.fitting_template.ingredients").withStyle(ChatFormatting.BLUE)));
    }
}
