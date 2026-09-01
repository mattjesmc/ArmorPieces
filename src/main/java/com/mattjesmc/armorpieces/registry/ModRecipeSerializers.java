package com.mattjesmc.armorpieces.registry;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.recipe.SmithingDecorationRecipe;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;

/**
 * Recipe serializers.
 *
 * <p>Only the serializer is registered, not a recipe TYPE: {@link SmithingDecorationRecipe}
 * implements {@code SmithingRecipe}, whose {@code getType()} is {@code RecipeType.SMITHING}. Riding
 * vanilla's type is what puts these recipes in the smithing table's own lookup with no mixin, and
 * gets them into the recipe book beside trims for free.
 */
public final class ModRecipeSerializers {
    private ModRecipeSerializers() {}

    public static void register() {
        Registry.register(
            BuiltInRegistries.RECIPE_SERIALIZER,
            Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "smithing_decoration"),
            SmithingDecorationRecipe.SERIALIZER
        );
        ArmorPieces.LOGGER.info("[Armor Pieces] Registered recipe serializers.");
    }
}
