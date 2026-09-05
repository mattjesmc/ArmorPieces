package com.mattjesmc.armorpieces.cloth;

import com.mattjesmc.armorpieces.decoration.MaterialIcons;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.function.Consumer;
import net.minecraft.ChatFormatting;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponentGetter;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.CommonComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.Style;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipProvider;
import net.minecraft.world.level.block.entity.BannerPatternLayers;

/**
 * The payload of {@code armorpieces:cloth} - the garment a piece of armor is wearing and the design
 * on it, and, on a cloth template, the garment that template applies. One component for both, as a
 * skin manages with one: what the template carries is this same value with nothing set but the
 * garment, because the design arrives later, off the banner in the smithing table's addition slot.
 *
 * <p>That default is load-bearing and not only tidiness. A template's value serialises to
 * {@code {"cloth": "armorpieces:tunic"}} exactly - the two colour fields are written only when they
 * differ from their defaults - which is the form the item model's {@code minecraft:select} matches
 * on, the same way the fitting template's does. A worn piece carries a base colour and layers, so it
 * matches no case and falls back, which is right: the fallback is a template icon and a worn piece
 * is not a template.
 *
 * <p>{@link #base} and {@link #patterns} together are what a banner item carries, and are read off
 * one by {@link com.mattjesmc.armorpieces.recipe.SmithingClothRecipe}. They are stored rather than a
 * reference to the banner because the banner is consumed, as it is for a shield.
 *
 * <p>The tooltip line is only shown on ARMOR, for the reason a skin's is: the template says its
 * garment in its own name already.
 */
public record ClothValue(Holder<Cloth> cloth, DyeColor base, BannerPatternLayers patterns)
    implements TooltipProvider {

    public static final Codec<ClothValue> CODEC = RecordCodecBuilder.create(
        i -> i.group(
                Cloth.CODEC.fieldOf("cloth").forGetter(ClothValue::cloth),
                DyeColor.CODEC.optionalFieldOf("base", DyeColor.WHITE).forGetter(ClothValue::base),
                BannerPatternLayers.CODEC
                    .optionalFieldOf("patterns", BannerPatternLayers.EMPTY).forGetter(ClothValue::patterns)
            )
            .apply(i, ClothValue::new)
    );

    public static final StreamCodec<RegistryFriendlyByteBuf, ClothValue> STREAM_CODEC = StreamCodec.composite(
        Cloth.STREAM_CODEC,
        ClothValue::cloth,
        DyeColor.STREAM_CODEC,
        ClothValue::base,
        BannerPatternLayers.STREAM_CODEC,
        ClothValue::patterns,
        ClothValue::new
    );

    private static final Component CLOTH_TITLE =
        Component.translatable("item.armorpieces.clothed").withStyle(ChatFormatting.GRAY);

    /** The bare garment, as a template carries it: no colour, no layers. */
    public static ClothValue of(final Holder<Cloth> cloth) {
        return new ClothValue(cloth, DyeColor.WHITE, BannerPatternLayers.EMPTY);
    }

    /**
     * The banner this garment was made from, patterns and all - not stored, rebuilt from the two
     * fields that are, which is all a banner is.
     *
     * <p>For anywhere a cloth has to be shown as a THING rather than as a name: the advanced table's
     * badge under its place, where every other place shows what its occupant is made of.
     */
    public ItemStack banner() {
        final ItemStack banner = MaterialIcons.forBanner(this.base);
        if (!banner.isEmpty() && !this.patterns.equals(BannerPatternLayers.EMPTY)) {
            banner.set(DataComponents.BANNER_PATTERNS, this.patterns);
        }
        return banner;
    }

    /** The garment's own name, as the registry entry gives it, in the colour it is dyed. */
    public Component description() {
        return this.cloth.value().description().copy()
            .withStyle(Style.EMPTY.withColor(this.base.getTextColor()));
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
        consumer.accept(CLOTH_TITLE);
        consumer.accept(CommonComponents.space().append(this.description()));
    }
}
