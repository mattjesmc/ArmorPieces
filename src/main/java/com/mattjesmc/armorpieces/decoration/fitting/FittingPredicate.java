package com.mattjesmc.armorpieces.decoration.fitting;

import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mattjesmc.armorpieces.decoration.fitting.builtin.DyeFitting;
import com.mattjesmc.armorpieces.decoration.fitting.builtin.MaterialFitting;
import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.Optional;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderSet;
import net.minecraft.core.RegistryCodecs;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.item.equipment.trim.TrimMaterial;

/**
 * A test on what a part's fitting holds - the condition an effect can be gated on.
 *
 * <pre>{@code
 * { "fitting": "armorpieces:gemstone", "material": "minecraft:emerald" }
 * { "fitting": "armorpieces:gemstone", "material": "#armorpieces:gemstones" }
 * { "fitting": "armorpieces:inlay", "dye": "red" }
 * { "fitting": "armorpieces:banner" }
 * }</pre>
 *
 * <p>The fitting must be filled; beyond that, {@code material} narrows a material fitting to a
 * material or a tag of them, and {@code dye} narrows a dye fitting to one colour. Neither is
 * required, so "while there is any gem" is the shortest form. The two are alternatives rather than
 * a conjunction - no value is both a trim material and a dye colour - and a file carrying both is
 * refused at load rather than left to never fire. A fitting type from another mod matches on presence
 * alone, which is the most this class can say about a value whose shape it does not know.
 *
 * <p>Naming {@code MaterialFitting} and {@code DyeFitting} here is the one reach into {@code builtin}
 * from outside it, and it is what a narrowing costs: a value is opaque by design (see
 * {@link FittingValue}), so a test on what is IN a fitting has to know a shape, and the shapes worth
 * knowing are the two this mod ships. Everything else about a value stays opaque, which is why the
 * effect package never needs the same reach.
 *
 * @param fitting  which of the part's fittings to look in.
 * @param material for a {@code armorpieces:material} fitting, which materials count.
 * @param dye      for a {@code armorpieces:dye} fitting, which colour counts.
 */
public record FittingPredicate(
    Holder<Fitting> fitting,
    Optional<HolderSet<TrimMaterial>> material,
    Optional<DyeColor> dye
) {
    public static final Codec<FittingPredicate> CODEC = RecordCodecBuilder.<FittingPredicate>create(
        i -> i.group(
                Fitting.CODEC.fieldOf("fitting").forGetter(FittingPredicate::fitting),
                RegistryCodecs.homogeneousList(Registries.TRIM_MATERIAL).optionalFieldOf("material").forGetter(FittingPredicate::material),
                DyeColor.CODEC.optionalFieldOf("dye").forGetter(FittingPredicate::dye)
            )
            .apply(i, FittingPredicate::new)
    ).comapFlatMap(FittingPredicate::validate, predicate -> predicate);

    /** Both narrowings at once is a predicate that can never be true, so it is a broken file. */
    private static DataResult<FittingPredicate> validate(final FittingPredicate predicate) {
        return predicate.material.isPresent() && predicate.dye.isPresent()
            ? DataResult.error(() -> "A fitting predicate takes either material or dye, not both")
            : DataResult.success(predicate);
    }

    public boolean test(final DecorationEntry entry) {
        final FittingValue value = entry.fitting(this.fitting);
        if (value == null) {
            return false;
        }
        if (this.material.isPresent()
            && !(value instanceof MaterialFitting.Value m && this.material.get().contains(m.material()))) {
            return false;
        }
        return this.dye.isEmpty()
            || value instanceof DyeFitting.Value d && d.colour() == this.dye.get();
    }
}
