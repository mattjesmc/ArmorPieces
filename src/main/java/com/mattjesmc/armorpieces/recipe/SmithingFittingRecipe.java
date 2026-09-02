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
 * <p>ONE recipe file covers every fitting there will ever be, for the same reason one apply recipe
 * per socket covers every part: nothing about a fitting is named here. The {@code addition}
 * ingredient in the file only narrows what the table lights up for; the routing is the fittings'
 * own {@link Fitting#accept}.
 *
 * <p>Matches nothing when nothing would change - the same gem into the same stone - so the
 * ingredients are not consumed for no effect, exactly as vanilla trimming refuses to re-apply an
 * identical trim.
 *
 * <p>The same rule, run backwards, is how a fitting is taken out again: the item decides where it
 * goes, and NO item decides nothing goes anywhere. A second recipe file names the template and the
 * armor and leaves {@code addition} out, and the table then empties every fitting on the piece - the
 * gem comes out of the stone, the banner off the back. That costs the template, as vanilla charges a
 * template for every smithing step. It is the one way a fitting is ever emptied: putting the part on
 * again through its socket template carries what was set over, see {@link SmithingDecorationRecipe}.
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
        return super.matches(input, level) && !applyFitting(input.base(), input.addition()).isEmpty();
    }

    @Override
    public ItemStack assemble(final SmithingRecipeInput input) {
        return applyFitting(input.base(), input.addition());
    }

    /**
     * The application itself, static and public so a command or a loot function fits a piece through
     * the same rules the table does.
     *
     * <p>Returns {@link ItemStack#EMPTY} when the item fits nothing on the piece, or when everything
     * it fits already holds it. With no item at all - an empty {@code additionItem} - every fitting
     * on the piece is emptied instead, and the result is again {@link ItemStack#EMPTY} if none held
     * anything.
     */
    public static ItemStack applyFitting(final ItemStack baseItem, final ItemStack additionItem) {
        final ArmorDecorations existing = baseItem.get(ModDataComponents.DECORATIONS);
        if (existing == null || existing.isEmpty()) {
            return ItemStack.EMPTY;
        }

        final ArmorDecorations result = additionItem.isEmpty()
            ? clearFittings(existing)
            : setFitting(existing, additionItem);
        if (result == existing) {
            return ItemStack.EMPTY;
        }

        final ItemStack fitted = baseItem.copyWithCount(1);
        fitted.set(ModDataComponents.DECORATIONS, result);
        return fitted;
    }

    /** {@code existing} with {@code additionItem} set into every part that takes it; {@code existing} itself if none does. */
    private static ArmorDecorations setFitting(final ArmorDecorations existing, final ItemStack additionItem) {
        ArmorDecorations result = existing;
        for (final var mapping : existing.entries().entrySet()) {
            final DecorationAnchor anchor = mapping.getKey();
            final DecorationEntry entry = mapping.getValue();
            // The part's own order decides which fitting is offered the item first, and the first to
            // accept it is the only one on that part that gets it.
            for (final Holder<Fitting> fitting : entry.decoration().value().fittings()) {
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
     * {@code existing} with every fitting on every part emptied; {@code existing} itself if none held
     * anything. All of them at once, because with nothing in the third slot there is nothing to route
     * by - the item is what names a fitting, and its absence names them all.
     */
    private static ArmorDecorations clearFittings(final ArmorDecorations existing) {
        ArmorDecorations result = existing;
        for (final var mapping : existing.entries().entrySet()) {
            final DecorationEntry entry = mapping.getValue();
            if (!entry.fittings().isEmpty()) {
                result = result.with(mapping.getKey(), new DecorationEntry(entry.material(), entry.decoration()));
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
