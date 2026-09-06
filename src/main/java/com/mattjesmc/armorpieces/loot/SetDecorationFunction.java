package com.mattjesmc.armorpieces.loot;

import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.decoration.fitting.FittingValue;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderGetter;
import net.minecraft.core.component.DataComponents;
import net.minecraft.util.ProblemReporter;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.equipment.Equippable;
import net.minecraft.world.item.equipment.trim.TrimMaterial;
import net.minecraft.world.level.storage.loot.LootContext;
import net.minecraft.world.level.storage.loot.ValidationContext;
import net.minecraft.world.level.storage.loot.functions.LootItemConditionalFunction;
import net.minecraft.world.level.storage.loot.predicates.LootItemCondition;
import org.jspecify.annotations.Nullable;

/**
 * {@code armorpieces:set_decoration} - a loot function that puts a part on a piece of armor, so a
 * table can hand out a helmet already wearing a gold circlet with an emerald in it rather than the
 * template that would make one.
 *
 * <pre>
 * { "function": "armorpieces:set_decoration",
 *   "socket": "brow", "part": "armorpieces:circlet", "material": "minecraft:gold",
 *   "fittings": { "armorpieces:gemstone": "minecraft:emerald" } }
 *
 * { "function": "armorpieces:set_decoration",
 *   "socket": "brow", "part": "#armorpieces:knightly", "material": "minecraft:iron" }
 * </pre>
 *
 * <p>Applies to whatever stack the entry produced, the way {@code set_enchantments} does: the stack
 * has to be armor for the socket's slot, and the part has to fit the socket, or the stack is passed
 * through untouched - the same two rules the smithing recipe enforces, checked here at load as
 * well, so a mismatch is a line in the log rather than a chest that quietly holds plain armor.
 * Whatever the socket held before is replaced outright; a table is a fresh piece of armor, not a
 * player re-applying a part, so nothing carries over.
 *
 * <p><b>{@code part} takes one part, a list, or a tag</b>, and one member that fits the socket is
 * drawn at random. A tag is the form that survives a pack not being installed - an empty tag leaves
 * the armor plain instead of failing the table to parse - and is the same argument
 * {@link TemplateEntry} makes for the reference going the other way. Members that do not fit the
 * socket are simply not drawn, so one function can name a whole theme and let the socket sort it
 * out.
 *
 * <p>The fittings map is read through {@link DecorationEntry#FITTINGS_CODEC}, the same codec the
 * armor's own component uses, so a value is written here exactly as it would be in
 * {@code /give} - a material id for a gem or a metal, a dye colour for an inlay, a banner's
 * layers for a banner. A map beside a tag only says something useful when every member of the tag
 * has that fitting, which is what {@link #validate} checks.
 */
public final class SetDecorationFunction extends LootItemConditionalFunction {
    public static final MapCodec<SetDecorationFunction> MAP_CODEC = RecordCodecBuilder.mapCodec(
        i -> commonFields(i).and(i.group(
                DecorationAnchor.CODEC.fieldOf("socket").forGetter(f -> f.socket),
                // Accepts a bare id, a list, or a tag - so every file written against the single-part
                // form reads exactly as it did. A tag is resolved late; see MemberSet.
                MemberSet.<ArmorDecoration>codec(ArmorPiecesRegistries.ARMOR_DECORATION)
                    .fieldOf("part").forGetter(f -> f.parts),
                TrimMaterial.CODEC.fieldOf("material").forGetter(f -> f.material),
                DecorationEntry.FITTINGS_CODEC.optionalFieldOf("fittings", Map.of()).forGetter(f -> f.fittings)
            ))
            .apply(i, SetDecorationFunction::new)
    );

    private final DecorationAnchor socket;
    private final MemberSet<ArmorDecoration> parts;
    private final Holder<TrimMaterial> material;
    private final Map<Holder<Fitting>, FittingValue> fittings;

    private SetDecorationFunction(
        final List<LootItemCondition> predicates,
        final DecorationAnchor socket,
        final MemberSet<ArmorDecoration> parts,
        final Holder<TrimMaterial> material,
        final Map<Holder<Fitting>, FittingValue> fittings
    ) {
        super(predicates);
        this.socket = socket;
        this.parts = parts;
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
        if (equippable == null || equippable.slot() != this.socket.slot()) {
            return stack;
        }
        final Holder<ArmorDecoration> part = this.draw(context);
        if (part == null) {
            return stack;
        }
        final ArmorDecorations existing = stack.getOrDefault(ModDataComponents.DECORATIONS, ArmorDecorations.EMPTY);
        stack.set(ModDataComponents.DECORATIONS,
            existing.with(this.socket, new DecorationEntry(this.material, part, this.fittings)));
        return stack;
    }

    /** One of the named parts that fits the socket, or null if none of them does. */
    private @Nullable Holder<ArmorDecoration> draw(final LootContext context) {
        final List<Holder<ArmorDecoration>> fitting = this.fitting(context.getLevel().registryAccess());
        if (fitting.isEmpty()) {
            return null;
        }
        return fitting.get(context.getRandom().nextInt(fitting.size()));
    }

    private List<Holder<ArmorDecoration>> fitting(final HolderGetter.Provider registries) {
        final List<Holder<ArmorDecoration>> fits = new ArrayList<>();
        for (final Holder<ArmorDecoration> candidate : this.parts.resolve(registries)) {
            if (candidate.value().fits(this.socket)) {
                fits.add(candidate);
            }
        }
        return fits;
    }

    /**
     * The part-fits-socket rule and the fitting list are both knowable at load, so they are said
     * then. Whether the STACK is the right armor is not - the entry decides that at roll time.
     *
     * <p>A TAG that is empty or whose members all miss the socket is said as a problem too, because
     * the point of writing one is that it holds something: a silent no-op is the failure this
     * function's log lines exist to prevent. It is still only a warning, and the table still loads.
     */
    @Override
    public void validate(final ValidationContext context) {
        super.validate(context);
        if (!context.allowsReferences()) {
            return;
        }
        final List<Holder<ArmorDecoration>> fitting = this.fitting(context.resolver());
        if (fitting.isEmpty()) {
            context.reportProblem(new Problem(
                "no part in " + this.parts.describe() + " fits socket " + this.socket.getSerializedName()));
            return;
        }
        for (final Holder<Fitting> fit : this.fittings.keySet()) {
            for (final Holder<ArmorDecoration> part : fitting) {
                if (!part.value().fittings().contains(fit)) {
                    context.reportProblem(new Problem(
                        "part " + name(part) + " has no fitting " + name(fit)));
                }
            }
        }
    }

    private static String name(final Holder<?> holder) {
        return holder.unwrapKey().map(key -> key.identifier().toString()).orElse("<inline>");
    }

    private record Problem(String description) implements ProblemReporter.Problem {}
}
