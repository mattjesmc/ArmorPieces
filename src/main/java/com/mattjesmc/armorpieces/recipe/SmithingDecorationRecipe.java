package com.mattjesmc.armorpieces.recipe;

import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.List;
import java.util.Optional;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponents;
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
import net.minecraft.world.item.equipment.Equippable;
import net.minecraft.world.item.equipment.trim.TrimMaterial;
import net.minecraft.world.level.Level;

/**
 * Applies one decorative part to one socket at a smithing table - the counterpart to vanilla's
 * {@link net.minecraft.world.item.crafting.SmithingTrimRecipe}, and modelled on it closely enough
 * that a player never has to learn a second interaction.
 *
 * <p>Template + armor + material, exactly as trimming works. The socket comes from the recipe (and
 * so, in practice, from the template ITEM the recipe accepts); the part comes from the
 * {@link ModDataComponents#DECORATION} component on the template STACK.
 *
 * <p>Reading the part off the stack instead of naming it in the recipe is what collapses the file
 * count to a constant. Ten of these recipes ship - one per socket - and they cover every part that
 * will ever exist, including ones a datapack invents tomorrow: the pack defines the part and hands
 * out a template carrying it, and this recipe applies it without having been told it exists. Under
 * the older per-part recipes, a new part meant a new recipe for every socket it fitted.
 *
 * <p>Keeping the {@link #anchor} on the recipe (rather than deriving it from the part) still lets one
 * modelled part serve several sockets - a spike that lists both {@code crest} and {@code spurs} is
 * reachable from either template - while leaving the socket unambiguous at craft time, so the
 * smithing table never has to ask the player where to put it.
 */
public class SmithingDecorationRecipe extends SimpleSmithingRecipe {
    public static final MapCodec<SmithingDecorationRecipe> MAP_CODEC = RecordCodecBuilder.mapCodec(
        i -> i.group(
                Recipe.CommonInfo.MAP_CODEC.forGetter(o -> o.commonInfo),
                Ingredient.CODEC.fieldOf("template").forGetter(o -> o.template),
                Ingredient.CODEC.fieldOf("base").forGetter(o -> o.base),
                Ingredient.CODEC.fieldOf("addition").forGetter(o -> o.addition),
                DecorationAnchor.CODEC.fieldOf("anchor").forGetter(o -> o.anchor)
            )
            .apply(i, SmithingDecorationRecipe::new)
    );
    public static final StreamCodec<RegistryFriendlyByteBuf, SmithingDecorationRecipe> STREAM_CODEC = StreamCodec.composite(
        Recipe.CommonInfo.STREAM_CODEC, o -> o.commonInfo,
        Ingredient.CONTENTS_STREAM_CODEC, o -> o.template,
        Ingredient.CONTENTS_STREAM_CODEC, o -> o.base,
        Ingredient.CONTENTS_STREAM_CODEC, o -> o.addition,
        DecorationAnchor.STREAM_CODEC, o -> o.anchor,
        SmithingDecorationRecipe::new
    );
    public static final RecipeSerializer<SmithingDecorationRecipe> SERIALIZER =
        new RecipeSerializer<>(MAP_CODEC, STREAM_CODEC);

    private final Ingredient template;
    private final Ingredient base;
    private final Ingredient addition;
    private final DecorationAnchor anchor;

    public SmithingDecorationRecipe(
        final Recipe.CommonInfo commonInfo,
        final Ingredient template,
        final Ingredient base,
        final Ingredient addition,
        final DecorationAnchor anchor
    ) {
        super(commonInfo);
        this.template = template;
        this.base = base;
        this.addition = addition;
        this.anchor = anchor;
    }

    /**
     * Adds two checks to the vanilla ingredient test, both here rather than in {@link #assemble} so a
     * bad combination shows an EMPTY result slot instead of matching and then producing nothing - the
     * failure that reads to a player as a broken table.
     *
     * <p>The socket must belong to the slot the base item equips (a crest goes on a head), and the
     * part the template carries must declare that socket. The second is the datapack guard rail: a
     * pack can hand out a crest template carrying a part meant for the heels, and it simply will not
     * craft.
     *
     * <p>A template with no part on it - a stack conjured by {@code /give} without the component -
     * matches nothing, which is the honest answer: there is no part to apply.
     */
    @Override
    public boolean matches(final SmithingRecipeInput input, final Level level) {
        if (!super.matches(input, level)) {
            return false;
        }
        final Holder<ArmorDecoration> decoration = input.template().get(ModDataComponents.DECORATION);
        return decoration != null
            && decoration.value().fits(this.anchor)
            && fitsSlot(input.base(), this.anchor);
    }

    @Override
    public ItemStack assemble(final SmithingRecipeInput input) {
        final Holder<ArmorDecoration> decoration = input.template().get(ModDataComponents.DECORATION);
        if (decoration == null) {
            return ItemStack.EMPTY;
        }
        return applyDecoration(input.base(), input.addition(), decoration, this.anchor);
    }

    private static boolean fitsSlot(final ItemStack baseItem, final DecorationAnchor anchor) {
        final Equippable equippable = baseItem.get(DataComponents.EQUIPPABLE);
        return equippable != null && equippable.slot() == anchor.slot();
    }

    /**
     * The application itself, kept static and public so anything else that needs to decorate a stack
     * - a creative command, a loot function, a datagen preview - goes through one implementation
     * rather than re-deriving the rules.
     *
     * <p>Whatever the socket already had set in its fittings carries over, so far as the incoming
     * part has places for it - see {@link DecorationEntry#applying}. Re-applying a part is how a
     * player changes its metal, and a step that quietly ate the gem set in it would be a trap.
     *
     * <p>Returns {@link ItemStack#EMPTY} when the operation would be a no-op, matching vanilla
     * trimming: re-applying the identical part in the identical material must not consume the
     * ingredients. With the fittings carried over, that guard covers a fitted part too - before, an
     * entry rebuilt empty always differed from the fitted one it replaced, so the craft went through
     * and the fittings were the price.
     */
    public static ItemStack applyDecoration(
        final ItemStack baseItem,
        final ItemStack materialItem,
        final Holder<ArmorDecoration> decoration,
        final DecorationAnchor anchor
    ) {
        final Holder<TrimMaterial> material = materialItem.get(DataComponents.PROVIDES_TRIM_MATERIAL);
        if (material == null || !decoration.value().fits(anchor) || !fitsSlot(baseItem, anchor)) {
            return ItemStack.EMPTY;
        }

        final ArmorDecorations existing = baseItem.getOrDefault(ModDataComponents.DECORATIONS, ArmorDecorations.EMPTY);
        final DecorationEntry newEntry = DecorationEntry.applying(material, decoration, existing.get(anchor));
        if (newEntry.equals(existing.get(anchor))) {
            return ItemStack.EMPTY;
        }

        final ItemStack decorated = baseItem.copyWithCount(1);
        decorated.set(ModDataComponents.DECORATIONS, existing.with(anchor, newEntry));
        return decorated;
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
        return Optional.of(this.addition);
    }

    @Override
    public RecipeSerializer<SmithingDecorationRecipe> getSerializer() {
        return SERIALIZER;
    }

    @Override
    protected PlacementInfo createPlacementInfo() {
        return PlacementInfo.create(List.of(this.template, this.base, this.addition));
    }

    /**
     * The recipe book preview. Shows the undecorated base rather than a decorated demo: vanilla's
     * {@code SmithingTrimDemoSlotDisplay} bakes a trim into a preview stack, and there is no such
     * vanilla display type for decorations. Rendering the base honestly beats inventing a preview
     * that could disagree with what the table actually produces.
     */
    @Override
    public List<RecipeDisplay> display() {
        final SlotDisplay baseDisplay = this.base.display();
        return List.of(
            new SmithingRecipeDisplay(
                this.template.display(),
                baseDisplay,
                this.addition.display(),
                baseDisplay,
                new SlotDisplay.ItemSlotDisplay(Items.SMITHING_TABLE)
            )
        );
    }
}
