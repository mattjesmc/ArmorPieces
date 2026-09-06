package com.mattjesmc.armorpieces.decoration.effect;

import com.mojang.datafixers.util.Either;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.List;
import java.util.function.Function;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.equipment.trim.TrimMaterial;

/**
 * A number an effect uses, which may depend on the material the part was made in.
 *
 * <pre>{@code
 * "amount": 1.0
 *
 * "amount": { "default": 1.0,
 *             "by_material": [ { "material": "#armorpieces:precious", "value": 1.5 },
 *                              { "material": "minecraft:netherite", "value": 2.0 } ] }
 * }</pre>
 *
 * <p>{@link DecorationEffectContext#material()} has been on the context since the first effect
 * shipped, and its javadoc says exactly what it is for - "a netherite plume that dodges more often
 * than an iron one is a single lookup, with no second registry entry and no second part". This is
 * that lookup, written once as a value type so that every effect gets it in the same spelling rather
 * than each inventing a field of its own.
 *
 * <p>A material a pack invents tomorrow is covered by the tag it joins, which is why the cases are a
 * LIST rather than a map: tags overlap, and a list has an order, so the rule is one sentence - the
 * first case whose material matches wins, and a part in a material no case names gets
 * {@code default}. A map would have needed a precedence rule nobody could see in the file.
 *
 * <p>A missing tag is not an error here. The case simply never matches, which is the same promise
 * {@code MemberSet} makes on the loot side: a reference to a tag has to survive the tag's members -
 * or the tag itself - not being installed, or a pack cannot safely name another pack's materials.
 *
 * @param base  the value for a material no case matches.
 * @param cases the exceptions, in the order they are tried.
 */
public record MaterialValue<T>(T base, List<Case<T>> cases) {
    /**
     * One exception: a material, or a tag of them, and the value it takes.
     *
     * @param material {@code minecraft:netherite} for one material, {@code #armorpieces:precious}
     *                 for a tag of them.
     */
    public record Case<T>(Either<TagKey<TrimMaterial>, ResourceKey<TrimMaterial>> material, T value) {
        /** {@code #ns:path} is a tag, anything else a single material - vanilla's own spelling. */
        public static final Codec<Either<TagKey<TrimMaterial>, ResourceKey<TrimMaterial>>> MATERIAL_CODEC =
            Codec.either(
                TagKey.hashedCodec(Registries.TRIM_MATERIAL),
                ResourceKey.codec(Registries.TRIM_MATERIAL));

        public static <T> Codec<Case<T>> codec(final Codec<T> values) {
            return RecordCodecBuilder.create(
                i -> i.group(
                        MATERIAL_CODEC.fieldOf("material").forGetter(Case::material),
                        values.fieldOf("value").forGetter(Case::value)
                    )
                    .apply(i, Case::new)
            );
        }

        public boolean matches(final Holder<TrimMaterial> material) {
            return this.material.map(material::is, material::is);
        }
    }

    public MaterialValue {
        cases = List.copyOf(cases);
    }

    /** The bare form: one number, whatever the material. */
    public static <T> MaterialValue<T> of(final T base) {
        return new MaterialValue<>(base, List.of());
    }

    /**
     * A field that takes either a number or the map above.
     *
     * <p>Built on {@link Codec#either} rather than {@code withAlternative}, and the difference is
     * the whole reason to say so here: {@code withAlternative} always ENCODES with its first codec,
     * so a scaled value written by an editor and read back would silently lose its cases. An
     * {@code Either} encodes on the side it holds, and {@link #asEither} puts a value with no cases
     * back on the bare side, so a file that said {@code 1.0} still says {@code 1.0} after a save.
     *
     * @param values the codec for one number - the same bounded codec the field would have used
     *               unscaled, so a range still applies to every case.
     */
    public static <T> Codec<MaterialValue<T>> codec(final Codec<T> values) {
        final Codec<MaterialValue<T>> scaled = RecordCodecBuilder.create(
            i -> i.group(
                    values.fieldOf("default").forGetter(MaterialValue::base),
                    Case.codec(values).listOf().optionalFieldOf("by_material", List.of())
                        .forGetter(MaterialValue::cases)
                )
                .apply(i, MaterialValue::new)
        );
        return Codec.either(values, scaled).xmap(
            either -> either.map(MaterialValue::of, Function.identity()),
            MaterialValue::asEither);
    }

    private Either<T, MaterialValue<T>> asEither() {
        return this.cases.isEmpty() ? Either.left(this.base) : Either.right(this);
    }

    /** The value for one material: the first case that matches it, or {@link #base}. */
    public T get(final Holder<TrimMaterial> material) {
        for (final Case<T> option : this.cases) {
            if (option.matches(material)) {
                return option.value();
            }
        }
        return this.base;
    }
}
