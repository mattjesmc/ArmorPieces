package com.mattjesmc.armorpieces.decoration.effect.builtin;

import com.mattjesmc.armorpieces.decoration.effect.DecorationEffect;
import com.mattjesmc.armorpieces.decoration.effect.DecorationEffectContext;
import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.function.BiConsumer;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;

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
 */
public record AttributeEffect(
    Identifier id,
    Holder<Attribute> attribute,
    double amount,
    AttributeModifier.Operation operation
) implements DecorationEffect.Attributes {
    public static final MapCodec<AttributeEffect> CODEC = RecordCodecBuilder.mapCodec(
        i -> i.group(
                Identifier.CODEC.fieldOf("id").forGetter(AttributeEffect::id),
                BuiltInRegistries.ATTRIBUTE.holderByNameCodec().fieldOf("attribute").forGetter(AttributeEffect::attribute),
                Codec.DOUBLE.fieldOf("amount").forGetter(AttributeEffect::amount),
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
        out.accept(this.attribute, new AttributeModifier(this.id, this.amount, this.operation));
    }
}
