package com.mattjesmc.armorpieces.decoration.fitting.builtin;

import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.decoration.fitting.FittingColour;
import com.mattjesmc.armorpieces.decoration.fitting.FittingValue;
import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.Optional;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.ComponentSerialization;
import net.minecraft.network.chat.Style;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.equipment.EquipmentAsset;

/**
 * {@code armorpieces:dye} - a region of the part coloured by a dye.
 *
 * <pre>{@code
 * { "type": "armorpieces:dye",
 *   "description": { "translate": "fitting.armorpieces.inlay" } }
 * }</pre>
 *
 * <p>For the parts of a part that are not metal: a sash's cloth, an inlaid line of enamel, a plume.
 * Sixteen dyes rather than eleven trim materials, and colours - true red, true blue - that no ore
 * palette reaches. The region shades around the dye's colour with the same rule the static layer
 * uses for a horn's ivory, so a dyed region and a static one sit beside each other without a seam.
 *
 * <p>Reads the dye colour off the item's {@code minecraft:dye} component rather than testing for a
 * dye item, so anything that vanilla considers a dye - and anything a mod marks as one - fills it.
 */
public record DyeFitting(Component description) implements Fitting.Masked {
    public static final MapCodec<DyeFitting> CODEC = RecordCodecBuilder.mapCodec(
        i -> i.group(
                ComponentSerialization.CODEC.fieldOf("description").forGetter(DyeFitting::description)
            )
            .apply(i, DyeFitting::new)
    );

    public record Value(DyeColor colour) implements FittingValue {
        public static final Codec<Value> CODEC = DyeColor.CODEC.xmap(Value::new, Value::colour);

        @Override
        public Component name() {
            return Component.translatable("color.minecraft." + this.colour.getName())
                .withStyle(Style.EMPTY.withColor(this.colour.getTextColor()));
        }
    }

    @Override
    public MapCodec<? extends Fitting> codec() {
        return CODEC;
    }

    @Override
    public Codec<? extends FittingValue> valueCodec() {
        return Value.CODEC;
    }

    @Override
    public Optional<FittingValue> accept(final ItemStack stack) {
        final DyeColor colour = stack.get(DataComponents.DYE);
        return colour == null ? Optional.empty() : Optional.of(new Value(colour));
    }

    @Override
    public boolean holds(final FittingValue value) {
        return value instanceof Value;
    }

    @Override
    public FittingColour colour(final FittingValue value, final ResourceKey<EquipmentAsset> asset) {
        // The diffuse colour is what a dyed block's texture is tinted with; it is the dye as the
        // player knows it, where the text colour is a legibility compromise.
        return new FittingColour.Solid(((Value) value).colour().getTextureDiffuseColor() & 0x00FFFFFF);
    }
}
