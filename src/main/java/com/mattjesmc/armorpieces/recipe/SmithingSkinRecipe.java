package com.mattjesmc.armorpieces.recipe;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.skin.ArmorSkinValue;
import com.mattjesmc.armorpieces.identity.Tolerant;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.Identifier;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
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
import net.minecraft.world.item.enchantment.Repairable;
import net.minecraft.world.item.equipment.Equippable;
import net.minecraft.world.level.Level;
import org.jspecify.annotations.Nullable;

/**
 * Reskins a piece of armor at a smithing table: the skin template, the armor, and - in the addition
 * slot - the piece's own REFORGING material.
 *
 * <p>Re-skinning is re-forging, and it costs the metal the piece is made of: an iron ingot for iron,
 * a diamond for diamond, a turtle scute for the turtle helmet. The colour of a skin was never a
 * choice - it comes out of the material's own texture - so the slot that names a material on every
 * other recipe in this mod is free to mean this instead.
 *
 * <p><b>The rule is not a table this mod maintains.</b> Every armor item carries
 * {@code minecraft:repairable}, a {@link Repairable} with {@code isValidRepairItem} on it, so
 * {@link #matches} asks the BASE STACK ITSELF what reforges it - and the answer is right for armor
 * this mod has never heard of, which is the same property the render layer has and got the same way.
 * Two consequences worth stating: an armor item carrying no {@code repairable} component cannot be
 * skinned at all, which is an honest refusal rather than a guess; and the {@code addition}
 * ingredient in the recipe file is only there so the recipe book has a cycle of items to show. The
 * real constraint is here, exactly as {@link SmithingFittingRecipe} keeps its own routing in
 * {@code matches} rather than in {@code assemble}.
 *
 * <p>One material is excluded, and it is excluded by DATA rather than by name: anything in
 * {@link #UNSKINNABLE} refuses a skin. The mod puts vanilla chainmail in that tag. Chainmail's whole
 * identity is the weave, and it has no metal of its own - vanilla repairs it with an iron ingot - so
 * even the reforging cost would be borrowed. Nothing is lost by it: the {@code chainmail} weave is
 * itself a skin every other material can wear.
 *
 * <p>With the addition slot EMPTY the same recipe takes the skin off again, which is the shape
 * {@link SmithingFittingRecipe} already established: a second recipe file naming only the template
 * and the base. It costs the template, as vanilla charges a template for every smithing step.
 */
public class SmithingSkinRecipe extends SimpleSmithingRecipe {
    /**
     * Armor that refuses a skin, whatever repairs it. A tag rather than a list in Java so a pack can
     * disagree in either direction - add its own unskinnable armor, or take chainmail out.
     */
    public static final TagKey<Item> UNSKINNABLE = TagKey.create(
        Registries.ITEM, Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "unskinnable_armor"));

    public static final MapCodec<SmithingSkinRecipe> MAP_CODEC = RecordCodecBuilder.mapCodec(
        i -> i.group(
                Recipe.CommonInfo.MAP_CODEC.forGetter(o -> o.commonInfo),
                Ingredient.CODEC.fieldOf("template").forGetter(o -> o.template),
                Ingredient.CODEC.fieldOf("base").forGetter(o -> o.base),
                // Absent, not empty: a recipe with no addition matches an empty third slot, and that
                // is the recipe that takes a skin off.
                Ingredient.CODEC.optionalFieldOf("addition").forGetter(o -> o.addition)
            )
            .apply(i, SmithingSkinRecipe::new)
    );
    public static final StreamCodec<RegistryFriendlyByteBuf, SmithingSkinRecipe> STREAM_CODEC = StreamCodec.composite(
        Recipe.CommonInfo.STREAM_CODEC, o -> o.commonInfo,
        Ingredient.CONTENTS_STREAM_CODEC, o -> o.template,
        Ingredient.CONTENTS_STREAM_CODEC, o -> o.base,
        Ingredient.OPTIONAL_CONTENTS_STREAM_CODEC, o -> o.addition,
        SmithingSkinRecipe::new
    );
    public static final RecipeSerializer<SmithingSkinRecipe> SERIALIZER =
        new RecipeSerializer<>(MAP_CODEC, STREAM_CODEC);

    private final Ingredient template;
    private final Ingredient base;
    private final Optional<Ingredient> addition;

    public SmithingSkinRecipe(
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
     * The ingredient test, then the two real ones: the addition has to reforge THIS piece, and the
     * result has to differ from what is already there. Both here rather than in {@link #assemble} so
     * an iron ingot held against a diamond helmet shows an empty result slot rather than matching and
     * producing nothing.
     */
    @Override
    public boolean matches(final SmithingRecipeInput input, final Level level) {
        return super.matches(input, level) && !assemble(input).isEmpty();
    }

    @Override
    public ItemStack assemble(final SmithingRecipeInput input) {
        return applySkin(input.base(), input.addition(), Tolerant.get(input.template(), ModDataComponents.SKIN));
    }

    /**
     * The application itself, static and public so the advanced table, a command or a loot function
     * skins a piece through the same rules the smithing table does.
     *
     * <p>{@code skin} is what the template carries, or null for a template with no skin on it - a
     * stack conjured by {@code /give} without the component - which applies nothing.
     *
     * <p>With an EMPTY {@code reforgingItem} the piece is unskinned instead: there is nothing to
     * apply, and the absence is the instruction, exactly as an empty third slot empties a fitting.
     *
     * @return the reskinned piece, or {@link ItemStack#EMPTY} when this would change nothing - the
     *         same skin again, an unskinned piece being unskinned, armor the addition does not
     *         reforge, or armor that refuses skins outright.
     */
    public static ItemStack applySkin(
        final ItemStack baseItem,
        final ItemStack reforgingItem,
        final @Nullable ArmorSkinValue skin
    ) {
        final ArmorSkinValue current = Tolerant.get(baseItem, ModDataComponents.SKIN);
        if (reforgingItem.isEmpty()) {
            // Taking a skin off is not asked whether the piece may WEAR one: a piece that has one is
            // proof enough, and a pack that changes its mind about what may be skinned must not
            // strand what it already skinned.
            if (current == null) {
                return ItemStack.EMPTY;
            }
            final ItemStack stripped = baseItem.copyWithCount(1);
            stripped.remove(ModDataComponents.SKIN);
            return stripped;
        }
        if (!isSkinnable(baseItem) || skin == null || Objects.equals(skin, current)
            || !reforges(baseItem, reforgingItem)) {
            return ItemStack.EMPTY;
        }
        final ItemStack skinned = baseItem.copyWithCount(1);
        skinned.set(ModDataComponents.SKIN, Tolerant.of(skin));
        return skinned;
    }

    /**
     * Whether this stack is armor a skin may be put on: worn armor that says what repairs it, and
     * not in {@link #UNSKINNABLE}.
     *
     * <p>The {@code repairable} test is not only about the recipe's cost. A skin repaints the armor's
     * own texture, and a piece with no reforging material is a piece the mod has no honest price for.
     */
    public static boolean isSkinnable(final ItemStack baseItem) {
        final Equippable equippable = baseItem.get(DataComponents.EQUIPPABLE);
        if (equippable == null || equippable.assetId().isEmpty() || !isArmorSlot(equippable)) {
            return false;
        }
        return baseItem.has(DataComponents.REPAIRABLE) && !baseItem.is(UNSKINNABLE);
    }

    /**
     * Whether the piece is worn in one of the four armor slots. A saddle is equippable and
     * repairable too, and there is no humanoid sheet to skin on it.
     */
    private static boolean isArmorSlot(final Equippable equippable) {
        return switch (equippable.slot()) {
            case HEAD, CHEST, LEGS, FEET -> true;
            default -> false;
        };
    }

    /** Whether the addition is a material that repairs this very piece. The armor is asked. */
    public static boolean reforges(final ItemStack baseItem, final ItemStack reforgingItem) {
        final Repairable repairable = baseItem.get(DataComponents.REPAIRABLE);
        return repairable != null && repairable.isValidRepairItem(reforgingItem);
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
    public RecipeSerializer<SmithingSkinRecipe> getSerializer() {
        return SERIALIZER;
    }

    @Override
    protected PlacementInfo createPlacementInfo() {
        return PlacementInfo.createFromOptionals(
            List.of(Optional.of(this.template), Optional.of(this.base), this.addition));
    }

    /** The recipe book preview: the base as it went in, for the reason the other two recipes give. */
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
