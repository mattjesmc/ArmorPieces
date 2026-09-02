package com.mattjesmc.armorpieces.recipe;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mojang.serialization.MapCodec;
import java.util.List;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.Identifier;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.PlacementInfo;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeBookCategories;
import net.minecraft.world.item.crafting.RecipeBookCategory;
import net.minecraft.world.item.crafting.RecipeInput;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.item.crafting.display.RecipeDisplay;
import net.minecraft.world.level.Level;

/**
 * A recipe that loads and does nothing: {@code {"type": "armorpieces:disabled"}}.
 *
 * <p>A datapack cannot delete a file this mod ships, and overriding a recipe with something that
 * fails to parse is a log full of errors and a recipe that may still be there. What a pack can do
 * is override the file with a recipe that is valid and inert, and this is that recipe. It has no
 * fields, matches no input, places nothing, and has no display, so the recipe book and any recipe
 * viewer that reads displays never see it. Overriding {@code recipe/template_circlet.json} with it
 * makes the circlet loot-only; overriding {@code recipe/apply_fitting.json} turns fittings off on a
 * server. Every recipe the mod has - template, apply, fitting, clear - can be switched off the same
 * way, and it works just as well on any other mod's file.
 *
 * <p>The codec ignores every field but {@code type}, deliberately: the Blockbench plugin disables a
 * recipe by swapping the type and keeping the pattern, key and result, so the choices survive the
 * round trip and switching it back on is the reverse swap.
 *
 * <p>Its own {@link RecipeType} rather than riding a vanilla one, because a vanilla type would put
 * it in that station's lookup to be asked and refused on every craft. Under its own type nothing
 * ever asks.
 */
public final class DisabledRecipe implements Recipe<RecipeInput> {
    public static final DisabledRecipe INSTANCE = new DisabledRecipe();

    public static final RecipeType<DisabledRecipe> TYPE = new RecipeType<>() {
        @Override
        public String toString() {
            return ArmorPieces.MOD_ID + ":disabled";
        }
    };
    public static final MapCodec<DisabledRecipe> MAP_CODEC = MapCodec.unit(INSTANCE);
    public static final StreamCodec<RegistryFriendlyByteBuf, DisabledRecipe> STREAM_CODEC = StreamCodec.unit(INSTANCE);
    public static final RecipeSerializer<DisabledRecipe> SERIALIZER = new RecipeSerializer<>(MAP_CODEC, STREAM_CODEC);

    private DisabledRecipe() {}

    public static void register() {
        final Identifier id = Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "disabled");
        Registry.register(BuiltInRegistries.RECIPE_TYPE, id, TYPE);
        Registry.register(BuiltInRegistries.RECIPE_SERIALIZER, id, SERIALIZER);
    }

    @Override
    public boolean matches(final RecipeInput input, final Level level) {
        return false;
    }

    @Override
    public ItemStack assemble(final RecipeInput input) {
        return ItemStack.EMPTY;
    }

    @Override
    public boolean isSpecial() {
        return true;
    }

    @Override
    public boolean showNotification() {
        return false;
    }

    @Override
    public String group() {
        return "";
    }

    @Override
    public RecipeSerializer<DisabledRecipe> getSerializer() {
        return SERIALIZER;
    }

    @Override
    public RecipeType<DisabledRecipe> getType() {
        return TYPE;
    }

    @Override
    public PlacementInfo placementInfo() {
        return PlacementInfo.NOT_PLACEABLE;
    }

    /** No display: this is what keeps it out of the recipe book. */
    @Override
    public List<RecipeDisplay> display() {
        return List.of();
    }

    /** Never consulted, since there is no display to file under it; any category will do. */
    @Override
    public RecipeBookCategory recipeBookCategory() {
        return RecipeBookCategories.CRAFTING_MISC;
    }
}
