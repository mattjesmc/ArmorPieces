package com.mattjesmc.armorpieces.item;

import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import java.util.function.Consumer;
import net.minecraft.ChatFormatting;
import net.minecraft.core.Holder;
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
 * <p>One item, and the fitting it is for rides on the stack as {@link ModDataComponents#FITTING},
 * exactly as the part rides on a socket template as {@code armorpieces:decoration}. The shape is the
 * same for the same reason: fittings are data, in a registry a pack adds to, so a template per
 * fitting cannot be an item per fitting without closing the list. A pack that defines a
 * {@code plume} fitting gets a plume template by writing a recipe whose result carries the
 * component, and no Java; the item model picks its look by the same component, with a texture for
 * each of the four fittings this mod ships and the plain card for any other.
 *
 * <p>The ITEM in the third slot still decides where it goes. A named template only narrows the
 * question: with a fitting named, the item is offered to that fitting alone on every part the piece
 * wears; with none named - the bare template, which every world made before there were named ones
 * still holds - every fitting on every part is offered it in turn, as before. So a gemstone template
 * and a ruby do nothing to a sash and fill a circlet's stone, and a named template with the third
 * slot empty empties only its own fitting where the bare one empties them all. The routing is in
 * {@link com.mattjesmc.armorpieces.recipe.SmithingFittingRecipe}; nothing here but the name and
 * the tooltip reads the component.
 *
 * <p>Why a template at all, rather than none: a smithing recipe with an empty template slot is
 * legal, but the recipe book would never show it, and a player would never find it.
 */
public class FittingTemplateItem extends Item {
    public FittingTemplateItem(final Properties properties) {
        super(properties);
    }

    /** "Gemstone Fitting Smithing Template", from the fitting's own description; bare, just the item's name. */
    @Override
    public Component getName(final ItemStack stack) {
        final Holder<Fitting> fitting = stack.get(ModDataComponents.FITTING);
        if (fitting == null) {
            return super.getName(stack);
        }
        return Component.translatable(
            "item.armorpieces.decoration_template", fitting.value().description(), super.getName(stack));
    }

    /**
     * The vanilla smithing-template tooltip shape: what it goes on, and what goes in. A named
     * template says its fitting and what that fitting takes; the bare one says every kind at once.
     */
    @Override
    public void appendHoverText(
        final ItemStack stack,
        final TooltipContext context,
        final TooltipDisplay display,
        final Consumer<Component> consumer,
        final TooltipFlag flag
    ) {
        final Holder<Fitting> fitting = stack.get(ModDataComponents.FITTING);
        final Component appliesTo = fitting == null
            ? Component.translatable("item.armorpieces.fitting_template.applies_to")
            : Component.translatable("item.armorpieces.fitting_template.applies_to.named", fitting.value().description());
        final Component ingredients = fitting == null
            ? Component.translatable("item.armorpieces.fitting_template.ingredients")
            : fitting.value().ingredients();
        consumer.accept(CommonComponents.EMPTY);
        consumer.accept(Component.translatable("item.armorpieces.template.applies_to").withStyle(ChatFormatting.GRAY));
        consumer.accept(CommonComponents.space().append(appliesTo.copy().withStyle(ChatFormatting.BLUE)));
        consumer.accept(Component.translatable("item.armorpieces.template.ingredients").withStyle(ChatFormatting.GRAY));
        consumer.accept(CommonComponents.space().append(ingredients.copy().withStyle(ChatFormatting.BLUE)));
    }
}
