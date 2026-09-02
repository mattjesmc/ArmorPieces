package com.mattjesmc.armorpieces.decoration.fitting.builtin;

import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.decoration.fitting.FittingColour;
import com.mattjesmc.armorpieces.decoration.fitting.FittingValue;
import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.Optional;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderSet;
import net.minecraft.core.RegistryCodecs;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.ComponentSerialization;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.equipment.EquipmentAsset;
import net.minecraft.world.item.equipment.trim.TrimMaterial;

/**
 * {@code armorpieces:material} - a region of the part coloured by a second trim material.
 *
 * <pre>{@code
 * { "type": "armorpieces:material",
 *   "description": { "translate": "fitting.armorpieces.gemstone" },
 *   "materials": "#armorpieces:gemstones" }
 * }</pre>
 *
 * <p>The mod's {@code gemstone} and {@code guard} are both this type, differing only in the tag: gems
 * for one, metals for the other. That split is what lets the smithing table route an emerald and an
 * ingot to different places on the same circlet without asking, and a pack that wants a fitting
 * taking ANY trim material writes {@code "#minecraft:trim_materials"}.
 *
 * <p>The item that fills it is whatever provides the material - the same emerald, the same ingot that
 * would trim the armor - so a datapack's new trim material is a valid gem or guard the moment its
 * tag says so, with no item of ours involved. And the colour it gives is the material's own vanilla
 * palette, resolved against the armor exactly as the part's first material is, so a gold guard on a
 * gold helmet darkens the way gold trim on gold armor does.
 */
public record MaterialFitting(Component description, HolderSet<TrimMaterial> materials) implements Fitting.Masked {
    public static final MapCodec<MaterialFitting> CODEC = RecordCodecBuilder.mapCodec(
        i -> i.group(
                ComponentSerialization.CODEC.fieldOf("description").forGetter(MaterialFitting::description),
                RegistryCodecs.homogeneousList(Registries.TRIM_MATERIAL).fieldOf("materials").forGetter(MaterialFitting::materials)
            )
            .apply(i, MaterialFitting::new)
    );

    /** The second material, as vanilla's own holder - see {@code DecorationEntry} for why not a type of ours. */
    public record Value(Holder<TrimMaterial> material) implements FittingValue {
        public static final Codec<Value> CODEC = TrimMaterial.CODEC.xmap(Value::new, Value::material);

        @Override
        public Component name() {
            return this.material.value().description();
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
        final Holder<TrimMaterial> material = stack.get(DataComponents.PROVIDES_TRIM_MATERIAL);
        if (material == null || !this.materials.contains(material)) {
            return Optional.empty();
        }
        return Optional.of(new Value(material));
    }

    @Override
    public boolean holds(final FittingValue value) {
        return value instanceof Value;
    }

    @Override
    public FittingColour colour(final FittingValue value, final ResourceKey<EquipmentAsset> asset) {
        return new FittingColour.Palette(((Value) value).material().value().assets().assetId(asset).suffix());
    }
}
