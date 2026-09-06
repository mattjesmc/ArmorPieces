package com.mattjesmc.armorpieces.decoration.effect.builtin;

import com.mattjesmc.armorpieces.decoration.effect.DecorationEffect;
import com.mattjesmc.armorpieces.decoration.effect.DecorationEffectContext;
import com.mattjesmc.armorpieces.decoration.effect.MaterialValue;
import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.function.BiConsumer;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.item.component.ItemAttributeModifiers;
import net.minecraft.world.item.equipment.trim.TrimMaterial;

/**
 * {@code armorpieces:attribute} - one attribute modifier, for as long as the part is worn.
 *
 * <pre>{@code
 * { "type": "armorpieces:attribute",
 *   "id": "mypack:gorget_armor",
 *   "attribute": "minecraft:armor",
 *   "amount": 1.0,
 *   "operation": "add_value" }
 * }</pre>
 *
 * <p>The fields are vanilla's, in vanilla's order and with vanilla's names, because this is the same
 * value an item's own {@code minecraft:attribute_modifiers} carries - the difference is only where it
 * is attached. A pack that wants a part to make its wearer tougher, faster or luckier writes this and
 * no Java at all.
 *
 * <p>{@code id} only has to be unique within the part: the dispatcher re-ids what it receives into
 * the socket the part is worn in, so the same part in two sockets stacks rather than overwriting
 * itself. Two DIFFERENT parts in the same socket that pick the same id are a pack authoring mistake
 * and will overwrite - which is exactly what vanilla does with two items claiming one modifier id.
 *
 * <p>There is no slot field, unlike vanilla's version of this value. The socket already fixes which
 * piece the modifier rides on, and a modifier that applied while the piece sat in a chest would be a
 * different feature.
 *
 * <p>{@code amount} is the field that may scale with the material - see {@link MaterialValue} - so a
 * netherite gorget that gives more armor than an iron one is one part with one number written twice,
 * not two parts.
 *
 * @param amount how much, as a plain number or a per-material one.
 */
public record AttributeEffect(
    Identifier id,
    Holder<Attribute> attribute,
    MaterialValue<Double> amount,
    AttributeModifier.Operation operation
) implements DecorationEffect.Attributes {
    public static final MapCodec<AttributeEffect> CODEC = RecordCodecBuilder.mapCodec(
        i -> i.group(
                Identifier.CODEC.fieldOf("id").forGetter(AttributeEffect::id),
                BuiltInRegistries.ATTRIBUTE.holderByNameCodec().fieldOf("attribute").forGetter(AttributeEffect::attribute),
                MaterialValue.codec(Codec.DOUBLE).fieldOf("amount").forGetter(AttributeEffect::amount),
                AttributeModifier.Operation.CODEC
                    .optionalFieldOf("operation", AttributeModifier.Operation.ADD_VALUE)
                    .forGetter(AttributeEffect::operation)
            )
            .apply(i, AttributeEffect::new)
    );

    @Override
    public MapCodec<? extends DecorationEffect> codec() {
        return CODEC;
    }

    @Override
    public void collectAttributes(
        final DecorationEffectContext context,
        final BiConsumer<Holder<Attribute>, AttributeModifier> out
    ) {
        out.accept(this.attribute,
            new AttributeModifier(this.id, this.amount.get(context.material()), this.operation));
    }

    /**
     * Vanilla's own modifier line - "+1 Armor" - down to the number format and the plus/take split,
     * because what this contributes is the same value an item's {@code attribute_modifiers} carries
     * and a player should not have to learn a second way of reading it.
     */
    @Override
    public Component description(final Holder<TrimMaterial> material) {
        final double value = this.amount.get(material);
        final double shown = this.operation == AttributeModifier.Operation.ADD_VALUE ? value : value * 100.0;
        return Component.translatable(
            "attribute.modifier." + (value < 0.0 ? "take" : "plus") + "." + this.operation.id(),
            ItemAttributeModifiers.ATTRIBUTE_MODIFIER_FORMAT.format(Math.abs(shown)),
            Component.translatable(this.attribute.value().getDescriptionId()));
    }
}
