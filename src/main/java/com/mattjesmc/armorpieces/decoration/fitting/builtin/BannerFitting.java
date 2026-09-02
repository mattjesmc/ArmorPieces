package com.mattjesmc.armorpieces.decoration.fitting.builtin;

import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.decoration.fitting.FittingValue;
import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.Optional;
import java.util.Set;
import net.minecraft.core.Direction;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.ComponentSerialization;
import net.minecraft.network.chat.Style;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.item.BannerItem;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BannerPatternLayers;

/**
 * {@code armorpieces:banner} - a bone of the part that wears a banner's design.
 *
 * <pre>{@code
 * { "type": "armorpieces:banner",
 *   "description": { "translate": "fitting.armorpieces.banner" },
 *   "bone": "banner",
 *   "sheet": "shield",
 *   "front": "south" }
 * }</pre>
 *
 * <p>The one fitting that is not a mask. A banner is layers of pattern in colour, and vanilla draws
 * those as passes over a model with the pattern sprites - the way a shield wears a banner - so this
 * fitting hands a bone of the part to that same machinery. Apply a banner made at a loom and the
 * bone takes its base colour and every layer; the banner is consumed, as it is for a shield.
 *
 * <ul>
 *   <li>{@code bone} - the geometry bone that becomes the cloth. The part's normal pass leaves it out
 *       while the fitting is filled, so its own faces never fight the pattern for depth. Defaults to
 *       {@code banner}, so a part only has to name a bone that.</li>
 *   <li>{@code sheet} - {@code banner} or {@code shield}: which set of pattern sprites to sample. A
 *       banner's designs are painted for a 20x40 flag and a shield's for a 12x22 plate, and a cloth
 *       nearer the second reads better from it.</li>
 *   <li>{@code front} - the face of the cloth that shows the design the right way round. A banner
 *       worn on the back is read from behind, so its outward face is {@code south}; a tabard on the
 *       chest would say {@code north}.</li>
 * </ul>
 *
 * <p>The drawing lives on the client, in {@code BannerFittingRenderer}, registered against this
 * type - this class only says what is stored and which bone is spoken for.
 */
public record BannerFitting(Component description, String bone, Sheet sheet, Direction front) implements Fitting {
    public static final MapCodec<BannerFitting> CODEC = RecordCodecBuilder.mapCodec(
        i -> i.group(
                ComponentSerialization.CODEC.fieldOf("description").forGetter(BannerFitting::description),
                Codec.STRING.optionalFieldOf("bone", "banner").forGetter(BannerFitting::bone),
                Sheet.CODEC.optionalFieldOf("sheet", Sheet.BANNER).forGetter(BannerFitting::sheet),
                Direction.CODEC.optionalFieldOf("front", Direction.SOUTH).forGetter(BannerFitting::front)
            )
            .apply(i, BannerFitting::new)
    );

    /** Which of vanilla's two pattern sprite sets the cloth samples. */
    public enum Sheet implements StringRepresentable {
        BANNER("banner"),
        SHIELD("shield");

        public static final Codec<Sheet> CODEC = StringRepresentable.fromEnum(Sheet::values);

        private final String name;

        Sheet(final String name) {
            this.name = name;
        }

        @Override
        public String getSerializedName() {
            return this.name;
        }
    }

    /** A banner, as its item carries it: the base colour and the pattern layers. */
    public record Value(DyeColor base, BannerPatternLayers layers) implements FittingValue {
        public static final Codec<Value> CODEC = RecordCodecBuilder.create(
            i -> i.group(
                    DyeColor.CODEC.fieldOf("base").forGetter(Value::base),
                    BannerPatternLayers.CODEC.optionalFieldOf("patterns", BannerPatternLayers.EMPTY).forGetter(Value::layers)
                )
                .apply(i, Value::new)
        );

        @Override
        public Component name() {
            return Component.translatable("block.minecraft." + this.base.getName() + "_banner")
                .withStyle(Style.EMPTY.withColor(this.base.getTextColor()));
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
        if (!(stack.getItem() instanceof BannerItem banner)) {
            return Optional.empty();
        }
        return Optional.of(new Value(
            banner.getColor(),
            stack.getOrDefault(DataComponents.BANNER_PATTERNS, BannerPatternLayers.EMPTY)));
    }

    @Override
    public boolean holds(final FittingValue value) {
        return value instanceof Value;
    }

    @Override
    public Set<String> replacedBones() {
        return Set.of(this.bone);
    }
}
