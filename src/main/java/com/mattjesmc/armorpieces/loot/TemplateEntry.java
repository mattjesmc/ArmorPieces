package com.mattjesmc.armorpieces.loot;

import com.mattjesmc.armorpieces.cloth.Cloth;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.registry.ModItems;
import com.mattjesmc.armorpieces.skin.ArmorSkin;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderGetter;
import net.minecraft.util.ProblemReporter;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.storage.loot.LootContext;
import net.minecraft.world.level.storage.loot.ValidationContext;
import net.minecraft.world.level.storage.loot.entries.LootPoolEntry;
import net.minecraft.world.level.storage.loot.entries.LootPoolSingletonContainer;
import net.minecraft.world.level.storage.loot.functions.LootItemFunction;
import net.minecraft.world.level.storage.loot.predicates.LootItemCondition;

/**
 * {@code armorpieces:template} - a loot pool entry that hands out the template for SOME member of a
 * tag, so a table written by somebody else can offer "a knightly part" without naming one.
 *
 * <pre>
 * { "type": "armorpieces:template", "parts": "#armorpieces:knightly" }
 * { "type": "armorpieces:template", "skins": "#mypack:northern", "cloths": "#mypack:northern",
 *   "weight": 3 }
 * </pre>
 *
 * <p>This is the reverse direction of {@link DecorationLootTables}. That one is the mod reaching
 * into everyone's tables; this is a table reaching back, and until now it could only do so by
 * naming an exact part on a {@code minecraft:item} entry with {@code set_components}. Two things
 * were wrong with that and both are the reason this exists:
 *
 * <ul>
 *   <li><b>A named part that is not installed is a hard failure.</b> A modpack's loot table breaks
 *       against a pack the player did not install, which is the worst way for content to be
 *       optional. A TAG is the reference that survives - see {@link MemberSet} for how, since a
 *       tag has to be looked up late rather than bound as the file is read - and when it resolves
 *       to nothing the entry is <b>skipped</b>: it drops out of the pool the same way a failed
 *       condition does, taking its weight with it, rather than winning its share of the roll and
 *       producing nothing.</li>
 *   <li><b>Naming one part is not what a table usually means.</b> "A knightly part" is a category,
 *       and writing the category out by hand goes stale the moment the pack adds a part.</li>
 * </ul>
 *
 * <p>All four families may be named at once, and one member is drawn from the union with every
 * candidate equally likely - so the weight between a part and a skin is how many of each are tagged,
 * which is the same rule the mod's own pool uses. Weighting the families against each other is what
 * two entries are for.
 *
 * <p>Unlike the mod's own pool this entry says nothing about how often: it is an ordinary entry in
 * somebody else's pool and their conditions and rolls decide that, as they should.
 */
public class TemplateEntry extends LootPoolSingletonContainer {
    public static final MapCodec<TemplateEntry> MAP_CODEC = RecordCodecBuilder.mapCodec(
        i -> i.group(
                MemberSet.<ArmorDecoration>codec(ArmorPiecesRegistries.ARMOR_DECORATION)
                    .optionalFieldOf("parts", MemberSet.empty()).forGetter(e -> e.parts),
                MemberSet.<ArmorSkin>codec(ArmorPiecesRegistries.ARMOR_SKIN)
                    .optionalFieldOf("skins", MemberSet.empty()).forGetter(e -> e.skins),
                MemberSet.<Cloth>codec(ArmorPiecesRegistries.CLOTH)
                    .optionalFieldOf("cloths", MemberSet.empty()).forGetter(e -> e.cloths),
                MemberSet.<Fitting>codec(ArmorPiecesRegistries.FITTING)
                    .optionalFieldOf("fittings", MemberSet.empty()).forGetter(e -> e.fittings)
            )
            .and(singletonFields(i))
            .apply(i, TemplateEntry::new)
    );

    private final MemberSet<ArmorDecoration> parts;
    private final MemberSet<ArmorSkin> skins;
    private final MemberSet<Cloth> cloths;
    private final MemberSet<Fitting> fittings;

    private TemplateEntry(
        final MemberSet<ArmorDecoration> parts,
        final MemberSet<ArmorSkin> skins,
        final MemberSet<Cloth> cloths,
        final MemberSet<Fitting> fittings,
        final int weight,
        final int quality,
        final List<LootItemCondition> conditions,
        final List<LootItemFunction> functions
    ) {
        super(weight, quality, conditions, functions);
        this.parts = parts;
        this.skins = skins;
        this.cloths = cloths;
        this.fittings = fittings;
    }

    @Override
    public MapCodec<TemplateEntry> codec() {
        return MAP_CODEC;
    }

    @Override
    protected void createItemStack(final Consumer<ItemStack> output, final LootContext context) {
        final List<ItemStack> candidates = this.candidates(context.getLevel().registryAccess());
        if (candidates.isEmpty()) {
            return;
        }
        output.accept(candidates.get(context.getRandom().nextInt(candidates.size())));
    }

    /**
     * Drops out of the pool entirely when nothing is tagged, rather than staying in it and handing
     * out air. This is what makes an absent pack cost the table nothing at all: the other entries
     * share the roll exactly as they would if this entry had never been written.
     */
    @Override
    public boolean expand(final LootContext context, final Consumer<LootPoolEntry> output) {
        return !this.candidates(context.getLevel().registryAccess()).isEmpty()
            && super.expand(context, output);
    }

    /**
     * Named nothing at all is an authoring mistake and is said so. A tag that resolves to nothing is
     * said too - once, as a warning, with the table still loading - because an entry that silently
     * never fires is the thing hardest to find by playing.
     */
    @Override
    public void validate(final ValidationContext context) {
        super.validate(context);
        if (!this.parts.named() && !this.skins.named() && !this.cloths.named() && !this.fittings.named()) {
            context.reportProblem(new Problem(
                "armorpieces:template names no parts, skins, cloths or fittings"));
            return;
        }
        if (context.allowsReferences() && this.candidates(context.resolver()).isEmpty()) {
            context.reportProblem(new Problem("armorpieces:template has no members installed: "
                + this.parts.describe() + " " + this.skins.describe()
                + " " + this.cloths.describe() + " " + this.fittings.describe()));
        }
    }

    /**
     * Every template this entry could hand out, as the stack it would hand out - built through
     * {@link ModItems} so a found template is the same stack the creative tab and the smithing table
     * would have produced.
     *
     * <p>Resolved on every call rather than cached, because a tag is a live thing: the whole point
     * of {@link MemberSet} is that what it holds is decided by the packs, late.
     */
    private List<ItemStack> candidates(final HolderGetter.Provider registries) {
        final List<ItemStack> stacks = new ArrayList<>();
        for (final Holder<ArmorDecoration> part : this.parts.resolve(registries)) {
            stacks.add(ModItems.templateFor(part.value().primaryAnchor(), part));
        }
        for (final Holder<ArmorSkin> skin : this.skins.resolve(registries)) {
            stacks.add(ModItems.skinTemplateFor(skin));
        }
        for (final Holder<Cloth> cloth : this.cloths.resolve(registries)) {
            stacks.add(ModItems.clothTemplateFor(cloth));
        }
        for (final Holder<Fitting> fitting : this.fittings.resolve(registries)) {
            stacks.add(ModItems.fittingTemplateFor(fitting));
        }
        return stacks;
    }

    private record Problem(String description) implements ProblemReporter.Problem {}
}
