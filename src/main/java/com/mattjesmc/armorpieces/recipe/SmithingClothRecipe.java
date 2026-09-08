package com.mattjesmc.armorpieces.recipe;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.cloth.ClothValue;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
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
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.BannerItem;
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
import net.minecraft.world.item.equipment.Equippable;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BannerPatternLayers;
import org.jspecify.annotations.Nullable;

/**
 * Puts a garment on a piece of armor at a smithing table: the cloth template, the armor, and - in
 * the addition slot - a BANNER.
 *
 * <p>The addition slot names a material on every other recipe in this mod. A cloth's colour is not a
 * material, so here the slot is free to mean the design: the base colour and up to six pattern
 * layers, made at a loom and read straight off the banner's own components, exactly as a shield
 * reads them. The banner is consumed, as it is for a shield.
 *
 * <p><b>Which armor may wear one</b> is {@link #CLOTHABLE}, a tag rather than a list in Java, and
 * the mod puts CHEST ARMOR in it and nothing else. A garment is the chestplate's because a garment
 * is the OUTFIT's and the chestplate is what carries the outfit: the cloth reaches two sheets - the
 * torso and the arms from the chestplate's own, the hem past the waist from the leggings' leg boxes
 * - and the renderer reads both off this one component, on this one slot. See
 * {@link com.mattjesmc.armorpieces.client.mixin.EquipmentLayerRendererMixin}.
 *
 * <p>So LEG ARMOR is refused, and that is a change of mind rather than a limitation: the hem used to
 * be a second garment on a second item, which is a second smithing operation and a piece
 * half-wearing a garment as a new thing a player could get wrong. Nothing on the leggings is read
 * any more, so accepting a cloth onto them would produce a component that draws nothing. Head and
 * foot armor are refused for the older reason - a helmet renders on the humanoid sheet too, but its
 * model samples none of the torso's texels, and refusing is more honest than baking a texture
 * nothing draws.
 *
 * <p>Unlike a skin this asks the armor for no reforging material, because it takes none: the cloth
 * is worn over the armor rather than forged into it, and the banner is already the cost. What it
 * does still require is {@code minecraft:equippable} with an asset - the layer the cloth is
 * composited onto is that asset's, and armor without one has nothing to composite onto.
 *
 * <p>With the addition slot EMPTY the same recipe takes the cloth off again, the shape
 * {@link SmithingFittingRecipe} established and {@link SmithingSkinRecipe} kept. It costs the
 * template, as vanilla charges a template for every smithing step.
 */
public class SmithingClothRecipe extends SimpleSmithingRecipe {
    /**
     * Armor a cloth may be worn over. Chest armor ships in it and nothing else, and a pack that wants
     * some other chestplate in it edits the tag rather than this file. Membership is necessary and
     * not sufficient: {@link #isClothable} still asks the slot, because only the chest slot is read
     * when the garment is drawn.
     */
    public static final TagKey<Item> CLOTHABLE = TagKey.create(
        Registries.ITEM, Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "clothable_armor"));

    public static final MapCodec<SmithingClothRecipe> MAP_CODEC = RecordCodecBuilder.mapCodec(
        i -> i.group(
                Recipe.CommonInfo.MAP_CODEC.forGetter(o -> o.commonInfo),
                Ingredient.CODEC.fieldOf("template").forGetter(o -> o.template),
                Ingredient.CODEC.fieldOf("base").forGetter(o -> o.base),
                // Absent, not empty: a recipe with no addition matches an empty third slot, and that
                // is the recipe that takes a cloth off.
                Ingredient.CODEC.optionalFieldOf("addition").forGetter(o -> o.addition)
            )
            .apply(i, SmithingClothRecipe::new)
    );
    public static final StreamCodec<RegistryFriendlyByteBuf, SmithingClothRecipe> STREAM_CODEC = StreamCodec.composite(
        Recipe.CommonInfo.STREAM_CODEC, o -> o.commonInfo,
        Ingredient.CONTENTS_STREAM_CODEC, o -> o.template,
        Ingredient.CONTENTS_STREAM_CODEC, o -> o.base,
        Ingredient.OPTIONAL_CONTENTS_STREAM_CODEC, o -> o.addition,
        SmithingClothRecipe::new
    );
    public static final RecipeSerializer<SmithingClothRecipe> SERIALIZER =
        new RecipeSerializer<>(MAP_CODEC, STREAM_CODEC);

    private final Ingredient template;
    private final Ingredient base;
    private final Optional<Ingredient> addition;

    public SmithingClothRecipe(
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
     * The ingredient test, then the real one: the result has to differ from what is already there.
     * Here rather than in {@link #assemble} so a banner held against a piece already wearing that
     * very design shows an empty result slot instead of matching and producing nothing.
     */
    @Override
    public boolean matches(final SmithingRecipeInput input, final Level level) {
        return super.matches(input, level) && !assemble(input).isEmpty();
    }

    @Override
    public ItemStack assemble(final SmithingRecipeInput input) {
        return applyCloth(input.base(), input.addition(), Tolerant.get(input.template(), ModDataComponents.CLOTH));
    }

    /**
     * The application itself, static and public so the advanced table, a command or a loot function
     * clothes a piece through the same rules the smithing table does.
     *
     * <p>{@code cloth} is what the template carries, or null for a template with no cloth on it - a
     * stack conjured by {@code /give} without the component - which applies nothing. Only the GARMENT
     * is taken from it; the colour and the layers come off the banner, because that is where the
     * player put them.
     *
     * <p>With an EMPTY {@code banner} the piece is stripped instead: there is nothing to apply, and
     * the absence is the instruction, exactly as an empty third slot empties a fitting.
     *
     * @return the clothed piece, or {@link ItemStack#EMPTY} when this would change nothing - the same
     *         garment in the same design again, a bare piece being stripped, an addition that is not
     *         a banner, or armor that cannot wear cloth.
     */
    public static ItemStack applyCloth(
        final ItemStack baseItem,
        final ItemStack banner,
        final @Nullable ClothValue cloth
    ) {
        final ClothValue current = Tolerant.get(baseItem, ModDataComponents.CLOTH);
        if (banner.isEmpty()) {
            // Taking a garment off is not asked whether the piece may WEAR one: a piece that has one
            // is proof enough, and a pack that changes its mind about what may be clothed must not
            // strand what it already clothed.
            if (current == null) {
                return ItemStack.EMPTY;
            }
            final ItemStack stripped = baseItem.copyWithCount(1);
            stripped.remove(ModDataComponents.CLOTH);
            return stripped;
        }
        if (!isClothable(baseItem) || cloth == null || !(banner.getItem() instanceof BannerItem item)) {
            return ItemStack.EMPTY;
        }
        final ClothValue worn = new ClothValue(
            cloth.cloth(),
            item.getColor(),
            banner.getOrDefault(DataComponents.BANNER_PATTERNS, BannerPatternLayers.EMPTY));
        if (Objects.equals(worn, current)) {
            return ItemStack.EMPTY;
        }
        final ItemStack clothed = baseItem.copyWithCount(1);
        clothed.set(ModDataComponents.CLOTH, Tolerant.of(worn));
        return clothed;
    }

    /**
     * Whether this stack is armor a cloth may be worn over: something in {@link #CLOTHABLE} that is
     * actually equippable and carries an equipment asset to composite onto.
     */
    public static boolean isClothable(final ItemStack baseItem) {
        final Equippable equippable = baseItem.get(DataComponents.EQUIPPABLE);
        if (equippable == null || equippable.assetId().isEmpty()) {
            return false;
        }
        return equippable.slot() == EquipmentSlot.CHEST && baseItem.is(CLOTHABLE);
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
    public RecipeSerializer<SmithingClothRecipe> getSerializer() {
        return SERIALIZER;
    }

    @Override
    protected PlacementInfo createPlacementInfo() {
        return PlacementInfo.createFromOptionals(
            List.of(Optional.of(this.template), Optional.of(this.base), this.addition));
    }

    /** The recipe book preview: the base as it went in, for the reason the other three recipes give. */
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
