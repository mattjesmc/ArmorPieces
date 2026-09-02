package com.mattjesmc.armorpieces.loot;

import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.decoration.fitting.FittingValue;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.List;
import java.util.Map;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponents;
import net.minecraft.util.ProblemReporter;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.equipment.Equippable;
import net.minecraft.world.item.equipment.trim.TrimMaterial;
import net.minecraft.world.level.storage.loot.LootContext;
import net.minecraft.world.level.storage.loot.ValidationContext;
import net.minecraft.world.level.storage.loot.functions.LootItemConditionalFunction;
import net.minecraft.world.level.storage.loot.predicates.LootItemCondition;

/**
 * {@code armorpieces:set_decoration} - a loot function that puts a part on a piece of armor, so a
 * table can hand out a helmet already wearing a gold circlet with an emerald in it rather than the
 * template that would make one.
 *
 * <pre>
 * { "function": "armorpieces:set_decoration",
 *   "socket": "brow", "part": "armorpieces:circlet", "material": "minecraft:gold",
 *   "fittings": { "armorpieces:gemstone": "minecraft:emerald" } }
 * </pre>
 *
 * <p>Applies to whatever stack the entry produced, the way {@code set_enchantments} does: the stack
 * has to be armor for the socket's slot, and the part has to fit the socket, or the stack is passed
 * through untouched - the same two rules the smithing recipe enforces, checked here at load as
 * well, so a mismatch is a line in the log rather than a chest that quietly holds plain armor.
 * Whatever the socket held before is replaced outright; a table is a fresh piece of armor, not a
 * player re-applying a part, so nothing carries over.
 *
 * <p>The fittings map is read through {@link DecorationEntry#FITTINGS_CODEC}, the same codec the
 * armor's own component uses, so a value is written here exactly as it would be in
 * {@code /give} - a material id for a gem or a metal, a dye colour for an inlay, a banner's
 * layers for a banner.
 */
public final class SetDecorationFunction extends LootItemConditionalFunction {
    public static final MapCodec<SetDecorationFunction> MAP_CODEC = RecordCodecBuilder.mapCodec(
        i -> commonFields(i).and(i.group(
                DecorationAnchor.CODEC.fieldOf("socket").forGetter(f -> f.socket),
                ArmorDecoration.CODEC.fieldOf("part").forGetter(f -> f.part),
                TrimMaterial.CODEC.fieldOf("material").forGetter(f -> f.material),
                DecorationEntry.FITTINGS_CODEC.optionalFieldOf("fittings", Map.of()).forGetter(f -> f.fittings)
            ))
            .apply(i, SetDecorationFunction::new)
    );

    private final DecorationAnchor socket;
    private final Holder<ArmorDecoration> part;
    private final Holder<TrimMaterial> material;
    private final Map<Holder<Fitting>, FittingValue> fittings;

    private SetDecorationFunction(
        final List<LootItemCondition> predicates,
        final DecorationAnchor socket,
        final Holder<ArmorDecoration> part,
        final Holder<TrimMaterial> material,
        final Map<Holder<Fitting>, FittingValue> fittings
    ) {
        super(predicates);
        this.socket = socket;
        this.part = part;
        this.material = material;
        this.fittings = fittings;
    }

    @Override
    public MapCodec<SetDecorationFunction> codec() {
        return MAP_CODEC;
    }

    @Override
    protected ItemStack run(final ItemStack stack, final LootContext context) {
        final Equippable equippable = stack.get(DataComponents.EQUIPPABLE);
        if (equippable == null || equippable.slot() != this.socket.slot() || !this.part.value().fits(this.socket)) {
            return stack;
        }
        final ArmorDecorations existing = stack.getOrDefault(ModDataComponents.DECORATIONS, ArmorDecorations.EMPTY);
        stack.set(ModDataComponents.DECORATIONS,
            existing.with(this.socket, new DecorationEntry(this.material, this.part, this.fittings)));
        return stack;
    }

    /**
     * The part-fits-socket rule and the fitting list are both knowable at load, so they are said
     * then. Whether the STACK is the right armor is not - the entry decides that at roll time.
     */
    @Override
    public void validate(final ValidationContext context) {
        super.validate(context);
        if (!this.part.value().fits(this.socket)) {
            context.reportProblem(new Problem(
                "part " + name(this.part) + " does not fit socket " + this.socket.getSerializedName()));
        }
        for (final Holder<Fitting> fitting : this.fittings.keySet()) {
            if (!this.part.value().fittings().contains(fitting)) {
                context.reportProblem(new Problem(
                    "part " + name(this.part) + " has no fitting " + name(fitting)));
            }
        }
    }

    private static String name(final Holder<?> holder) {
        return holder.unwrapKey().map(key -> key.identifier().toString()).orElse("<inline>");
    }

    private record Problem(String description) implements ProblemReporter.Problem {}
}
