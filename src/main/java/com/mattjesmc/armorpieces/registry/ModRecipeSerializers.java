package com.mattjesmc.armorpieces.registry;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.recipe.DisabledRecipe;
import com.mattjesmc.armorpieces.recipe.SmithingClothRecipe;
import com.mattjesmc.armorpieces.recipe.SmithingDecorationRecipe;
import com.mattjesmc.armorpieces.recipe.SmithingFittingRecipe;
import com.mattjesmc.armorpieces.recipe.SmithingSkinRecipe;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;

/**
 * Recipe serializers.
 *
 * <p>For the four smithing recipes only the serializer is registered, not a recipe TYPE:
 * {@link SmithingDecorationRecipe} implements {@code SmithingRecipe}, whose {@code getType()} is
 * {@code RecipeType.SMITHING}. Riding vanilla's type is what puts these recipes in the smithing
 * table's own lookup with no mixin, and gets them into the recipe book beside trims for free.
 * {@link DisabledRecipe} is the opposite case - it must be in NO station's lookup - so it registers
 * a type of its own.
 */
public final class ModRecipeSerializers {
    private ModRecipeSerializers() {}

    public static void register() {
        DisabledRecipe.register();
        Registry.register(
            BuiltInRegistries.RECIPE_SERIALIZER,
            Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "smithing_decoration"),
            SmithingDecorationRecipe.SERIALIZER
        );
        Registry.register(
            BuiltInRegistries.RECIPE_SERIALIZER,
            Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "smithing_fitting"),
            SmithingFittingRecipe.SERIALIZER
        );
        Registry.register(
            BuiltInRegistries.RECIPE_SERIALIZER,
            Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "smithing_skin"),
            SmithingSkinRecipe.SERIALIZER
        );
        Registry.register(
            BuiltInRegistries.RECIPE_SERIALIZER,
            Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "smithing_cloth"),
            SmithingClothRecipe.SERIALIZER
        );
        ArmorPieces.LOGGER.info("[Armor Pieces] Registered recipe serializers.");
    }
}
