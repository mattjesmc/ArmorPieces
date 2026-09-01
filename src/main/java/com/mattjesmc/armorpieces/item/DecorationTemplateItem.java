package com.mattjesmc.armorpieces.item;

import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
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
 * A smithing template for one socket - the player-facing handle on the whole system, and the reason
 * decorations are obtainable rather than merely craftable-if-you-read-the-wiki.
 *
 * <p>There is one of these items per {@link DecorationAnchor} and no more, which is the whole trick:
 * the anchor set is already the one closed, compiled-in part of the mod (a socket is a place on the
 * body, not data - see {@link DecorationAnchor}), so registering an item per anchor closes nothing
 * that was open. The PART is carried on the stack as {@link ModDataComponents#DECORATION}, so a
 * datapack adds a new part and a new template variant appears with no item registration, no model and
 * no code - exactly as a new potion type needs no new item.
 *
 * <p>Consequences worth stating, because they are the point:
 *
 * <ul>
 *   <li>the socket is fixed by the ITEM, so a crest template can only ever produce a crest, and the
 *       smithing recipe needs no per-part file - ten recipes cover every part that will ever exist;</li>
 *   <li>one socket holds one part ({@code ArmorDecorations} is keyed by anchor), so applying a second
 *       crest replaces the first rather than stacking two plumes on one helmet;</li>
 *   <li>loot tables can hand out "a helmet-top template" by item and pick the part with a
 *       {@code set_components} function, with no code on our side.</li>
 * </ul>
 */
public class DecorationTemplateItem extends Item {
    private final DecorationAnchor anchor;

    public DecorationTemplateItem(final DecorationAnchor anchor, final Properties properties) {
        super(properties);
        this.anchor = anchor;
    }

    /** The socket this template applies to. Fixed by the item, never by the stack. */
    public DecorationAnchor anchor() {
        return this.anchor;
    }

    /**
     * "Feathering Crest Smithing Template" rather than ten identical "Crest Smithing Template"s in a
     * row. The part's own {@code description} supplies the first half, so a datapack part is named by
     * its own translation key and needs no entry of ours.
     */
    @Override
    public Component getName(final ItemStack stack) {
        final Holder<ArmorDecoration> decoration = stack.get(ModDataComponents.DECORATION);
        if (decoration == null) {
            return super.getName(stack);
        }
        return Component.translatable(
            "item.armorpieces.decoration_template", decoration.value().description(), super.getName(stack));
    }

    /**
     * The vanilla smithing-template tooltip, line for line: what it goes on, and what colours it.
     * Deliberately identical in shape to a trim template's, because to a player this IS a trim
     * template - a different thing in the same slot of the same table.
     */
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
            .append(Component.translatable("anchor.armorpieces." + this.anchor.getSerializedName() + ".applies_to")
                .withStyle(ChatFormatting.BLUE)));
        consumer.accept(Component.translatable("item.armorpieces.template.ingredients").withStyle(ChatFormatting.GRAY));
        consumer.accept(CommonComponents.space()
            .append(Component.translatable("item.armorpieces.template.trim_materials").withStyle(ChatFormatting.BLUE)));
    }
}
