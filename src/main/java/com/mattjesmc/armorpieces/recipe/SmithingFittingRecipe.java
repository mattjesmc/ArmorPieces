package com.mattjesmc.armorpieces.recipe;

import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.decoration.fitting.FittingValue;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.List;
import java.util.Optional;
import net.minecraft.core.Holder;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.PlacementInfo;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.SimpleSmithingRecipe;
import net.minecraft.world.item.crafting.SmithingRecipeInput;
import net.minecraft.world.item.crafting.display.RecipeDisplay;
import net.minecraft.world.item.crafting.display.SlotDisplay;
import net.minecraft.world.item.crafting.display.SmithingRecipeDisplay;
import net.minecraft.world.level.Level;
import org.jspecify.annotations.Nullable;

/**
 * Sets a second material into the parts an armor piece already wears - the second smithing step,
 * after {@link SmithingDecorationRecipe} has put the part on.
 *
 * <p>Fitting template + decorated armor + the thing to set. Which fitting takes it is decided by the
 * thing: every part on the piece is asked, in its own fitting order, whether one of its fittings
 * accepts the item, and the first that does receives it. A gem lands in the circlet's stone, an
 * ingot in a pauldron's guard, a dye in the sash, a banner on the back banner - and two parts that
 * both take gems both get the one gem, which is the coherent answer for a single smithing step and
 * the reason the template does not have to name a socket.
 *
 * <p>The template may name a FITTING, though, as {@code armorpieces:fitting} on its stack, and then
 * the question is narrower: only that fitting on each part is offered the item. That is a component
 * and not four items for the reason the part is a component on a socket template - fittings are
 * data in a registry a pack adds to, and a pack's {@code plume} fitting gets its own template from
 * a recipe alone. The bare template, with no fitting named, still routes everything, so a world
 * made before there were named templates keeps working with the one it has. See
 * {@link com.mattjesmc.armorpieces.item.FittingTemplateItem}.
 *
 * <p>ONE apply recipe file covers every fitting there will ever be, for the same reason one apply
 * recipe per socket covers every part: nothing about a fitting is named here, and a template
 * ingredient matches the item whatever component it carries. The {@code addition} ingredient in the
 * file only narrows what the table lights up for; the routing is the fittings' own
 * {@link Fitting#accept}, and the template's component.
 *
 * <p>Matches nothing when nothing would change - the same gem into the same stone - so the
 * ingredients are not consumed for no effect, exactly as vanilla trimming refuses to re-apply an
 * identical trim.
 *
 * <p>The same rule, run backwards, is how a fitting is taken out again: the item decides where it
 * goes, and NO item decides nothing goes anywhere. A second recipe file names the template and the
 * armor and leaves {@code addition} out, and the table then empties the fittings on the piece -
 * every one under the bare template, the named one alone under a named template - so the gem comes
 * out of the stone, or the banner off the back, and nothing else. That costs the template, as
 * vanilla charges a template for every smithing step. It is the one way a fitting is ever emptied:
 * putting the part on again through its socket template carries what was set over, see
 * {@link SmithingDecorationRecipe}.
 */
public class SmithingFittingRecipe extends SimpleSmithingRecipe {
    public static final MapCodec<SmithingFittingRecipe> MAP_CODEC = RecordCodecBuilder.mapCodec(
        i -> i.group(
                Recipe.CommonInfo.MAP_CODEC.forGetter(o -> o.commonInfo),
                Ingredient.CODEC.fieldOf("template").forGetter(o -> o.template),
                Ingredient.CODEC.fieldOf("base").forGetter(o -> o.base),
                // Absent, not empty: a recipe with no addition matches an empty third slot, as
                // vanilla's own smithing codec allows, and that is the clearing recipe.
                Ingredient.CODEC.optionalFieldOf("addition").forGetter(o -> o.addition)
            )
            .apply(i, SmithingFittingRecipe::new)
    );
    public static final StreamCodec<RegistryFriendlyByteBuf, SmithingFittingRecipe> STREAM_CODEC = StreamCodec.composite(
        Recipe.CommonInfo.STREAM_CODEC, o -> o.commonInfo,
        Ingredient.CONTENTS_STREAM_CODEC, o -> o.template,
        Ingredient.CONTENTS_STREAM_CODEC, o -> o.base,
        Ingredient.OPTIONAL_CONTENTS_STREAM_CODEC, o -> o.addition,
        SmithingFittingRecipe::new
    );
    public static final RecipeSerializer<SmithingFittingRecipe> SERIALIZER =
        new RecipeSerializer<>(MAP_CODEC, STREAM_CODEC);

    private final Ingredient template;
    private final Ingredient base;
    private final Optional<Ingredient> addition;

    public SmithingFittingRecipe(
        final Recipe.CommonInfo commonInfo,
        final Ingredient template,
        final Ingredient base,
        final Optional<Ingredient> addition
    ) {
        super(commonInfo);
        this.template = template;
        this.base = base;
        this.addition = addition;
    }

    /**
     * The ingredient test, then the real one: does any fitting on the piece take this item, and
     * would taking it change anything. Done here rather than in {@link #assemble} so a piece with
     * nowhere for the item to go shows an empty result slot instead of a match that produces nothing.
     */
    @Override
    public boolean matches(final SmithingRecipeInput input, final Level level) {
        return super.matches(input, level) && !assemble(input).isEmpty();
    }

    @Override
    public ItemStack assemble(final SmithingRecipeInput input) {
        return applyFitting(input.base(), input.addition(), input.template().get(ModDataComponents.FITTING));
    }

    /**
     * The application itself, static and public so a command or a loot function fits a piece through
     * the same rules the table does.
     *
     * <p>{@code only} is the fitting the template names, or null for the bare template. Named, it is
     * the one fitting on each part that is offered the item, or emptied; null, every fitting is, in
     * the part's order, as it always was.
     *
     * <p>Returns {@link ItemStack#EMPTY} when the item fits nothing on the piece, or when everything
     * it fits already holds it. With no item at all - an empty {@code additionItem} - the fittings
     * are emptied instead, and the result is again {@link ItemStack#EMPTY} if none held anything.
     */
    public static ItemStack applyFitting(
        final ItemStack baseItem,
        final ItemStack additionItem,
        final @Nullable Holder<Fitting> only
    ) {
        return applyFitting(baseItem, additionItem, only, null);
    }

    /**
     * The same application, narrowed to one socket.
     *
     * <p>{@code onlyAnchor} is the socket the advanced smithing table is working on, or null for
     * every socket on the piece, which is what the table itself and every other caller ask for. The
     * routing is otherwise untouched: the item still decides which fitting of that part takes it,
     * and an item that fits nothing there is still no recipe at all.
     *
     * <p>This exists because the smithing table has nowhere to say which part it means and the
     * advanced table does - a row is selected there. Narrowing here rather than in the menu keeps
     * the rule in one place; see {@code AdvancedSmithingMenu#assemble}.
     */
    public static ItemStack applyFitting(
        final ItemStack baseItem,
        final ItemStack additionItem,
        final @Nullable Holder<Fitting> only,
        final @Nullable DecorationAnchor onlyAnchor
    ) {
        final ArmorDecorations existing = baseItem.get(ModDataComponents.DECORATIONS);
        if (existing == null || existing.isEmpty()) {
            return ItemStack.EMPTY;
        }

        final ArmorDecorations result = additionItem.isEmpty()
            ? clearFittings(existing, only, onlyAnchor)
            : setFitting(existing, additionItem, only, onlyAnchor);
        if (result == existing) {
            return ItemStack.EMPTY;
        }

        final ItemStack fitted = baseItem.copyWithCount(1);
        fitted.set(ModDataComponents.DECORATIONS, result);
        return fitted;
    }

    /** The bare template's routing: every fitting on every part is asked. */
    public static ItemStack applyFitting(final ItemStack baseItem, final ItemStack additionItem) {
        return applyFitting(baseItem, additionItem, null);
    }

    /** Whether the template's choice, if it made one, lets this fitting be touched. */
    private static boolean offered(final Holder<Fitting> fitting, final @Nullable Holder<Fitting> only) {
        return only == null || only.equals(fitting);
    }

    /** {@code existing} with {@code additionItem} set into every part that takes it; {@code existing} itself if none does. */
    private static ArmorDecorations setFitting(
        final ArmorDecorations existing,
        final ItemStack additionItem,
        final @Nullable Holder<Fitting> only,
        final @Nullable DecorationAnchor onlyAnchor
    ) {
        ArmorDecorations result = existing;
        for (final var mapping : existing.entries().entrySet()) {
            final DecorationAnchor anchor = mapping.getKey();
            if (onlyAnchor != null && onlyAnchor != anchor) {
                continue;
            }
            final DecorationEntry entry = mapping.getValue();
            // The part's own order decides which fitting is offered the item first, and the first to
            // accept it is the only one on that part that gets it. A named template offers it to its
            // own fitting alone, so the order only matters for the bare one.
            for (final Holder<Fitting> fitting : entry.decoration().value().fittings()) {
                if (!offered(fitting, only)) {
                    continue;
                }
                final Optional<FittingValue> value = fitting.value().accept(additionItem);
                if (value.isEmpty()) {
                    continue;
                }
                if (!value.get().equals(entry.fitting(fitting))) {
                    result = result.with(anchor, entry.withFitting(fitting, value.get()));
                }
                break;
            }
        }
        return result;
    }

    /**
     * {@code existing} with the fittings emptied - every one on every part under the bare template,
     * the named one alone under a named template; {@code existing} itself if none held anything.
     * Everything at once for the bare template because with nothing in the third slot there is
     * nothing to route by: the item is what names a fitting, and its absence names them all. A
     * named template has said which, and takes out only that.
     */
    private static ArmorDecorations clearFittings(
        final ArmorDecorations existing,
        final @Nullable Holder<Fitting> only,
        final @Nullable DecorationAnchor onlyAnchor
    ) {
        ArmorDecorations result = existing;
        for (final var mapping : existing.entries().entrySet()) {
            final DecorationEntry entry = mapping.getValue();
            if (entry.fittings().isEmpty() || (onlyAnchor != null && onlyAnchor != mapping.getKey())) {
                continue;
            }
            if (only == null) {
                result = result.with(mapping.getKey(), new DecorationEntry(entry.material(), entry.decoration()));
            } else if (entry.fitting(only) != null) {
                result = result.with(mapping.getKey(), entry.withoutFitting(only));
            }
        }
        return result;
    }

    @Override
    public Optional<Ingredient> templateIngredient() {
        return Optional.of(this.template);
    }

    @Override
    public Ingredient baseIngredient() {
        return this.base;
    }

    @Override
    public Optional<Ingredient> additionIngredient() {
        return this.addition;
    }

    @Override
    public RecipeSerializer<SmithingFittingRecipe> getSerializer() {
        return SERIALIZER;
    }

    @Override
    protected PlacementInfo createPlacementInfo() {
        return PlacementInfo.createFromOptionals(List.of(Optional.of(this.template), Optional.of(this.base), this.addition));
    }

    /** The recipe book preview: the base as it went in, for the reason {@link SmithingDecorationRecipe} gives. */
    @Override
    public List<RecipeDisplay> display() {
        final SlotDisplay baseDisplay = this.base.display();
        return List.of(
            new SmithingRecipeDisplay(
                this.template.display(),
                baseDisplay,
                Ingredient.optionalIngredientToDisplay(this.addition),
                baseDisplay,
                new SlotDisplay.ItemSlotDisplay(Items.SMITHING_TABLE)
            )
        );
    }
}
