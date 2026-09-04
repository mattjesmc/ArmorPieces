package com.mattjesmc.armorpieces.skin;

import com.mojang.serialization.Codec;
import java.util.function.Consumer;
import net.minecraft.ChatFormatting;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponentGetter;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.CommonComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipProvider;

/**
 * The payload of {@code armorpieces:skin} - the skin a piece of armor is wearing, and, on a skin
 * template, the skin that template applies. One component for both, because a skin is one thing
 * either way: the template hands it over and the armor keeps it.
 *
 * <p>A record around a {@code Holder<ArmorSkin>} rather than the holder itself, and for one reason:
 * a component payload can carry its own tooltip line, and a holder cannot. It serialises exactly as
 * the bare holder would - {@code "armorpieces:skin": "armorpieces:plate"} - so nothing about
 * {@code /give} or a loot table's {@code set_components} is any longer for the wrapper.
 *
 * <p>The line is only shown on ARMOR. {@link TooltipProvider#addToTooltip} is handed the whole
 * stack's components, and the template says which skin it is in its own NAME already - "Plate Skin
 * Smithing Template" - so a second line under it would only repeat itself.
 */
public record ArmorSkinValue(Holder<ArmorSkin> skin) implements TooltipProvider {
    public static final Codec<ArmorSkinValue> CODEC =
        ArmorSkin.CODEC.xmap(ArmorSkinValue::new, ArmorSkinValue::skin);
    public static final StreamCodec<RegistryFriendlyByteBuf, ArmorSkinValue> STREAM_CODEC =
        ArmorSkin.STREAM_CODEC.map(ArmorSkinValue::new, ArmorSkinValue::skin);

    private static final Component SKINNED_TITLE =
        Component.translatable("item.armorpieces.skinned").withStyle(ChatFormatting.GRAY);

    /** The skin's own name, as the registry entry gives it. */
    public Component description() {
        return this.skin.value().description();
    }

    @Override
    public void addToTooltip(
        final Item.TooltipContext context,
        final Consumer<Component> consumer,
        final TooltipFlag flag,
        final DataComponentGetter components
    ) {
        if (components.get(DataComponents.EQUIPPABLE) == null) {
            return;
        }
        consumer.accept(SKINNED_TITLE);
        consumer.accept(CommonComponents.space().append(this.description()));
    }
}
