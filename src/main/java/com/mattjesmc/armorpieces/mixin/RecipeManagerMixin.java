package com.mattjesmc.armorpieces.mixin;

import com.mattjesmc.armorpieces.recipe.OfferedRecipes;
import net.minecraft.core.HolderLookup;
import net.minecraft.world.item.crafting.RecipeManager;
import net.minecraft.world.item.crafting.RecipeMap;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/**
 * Hands the recipes a datapack reload just read to {@link OfferedRecipes} before the manager keeps
 * them, so a template recipe for a part the server has switched off is never a recipe at all.
 *
 * <p>{@code apply} is the one door: the map it is given becomes {@code this.recipes}, and everything
 * after - {@code finalizeRecipeLoading}, the recipe book, {@code /recipe} - reads that field. The
 * manager's own {@code registries} is the lookup the recipes were decoded against, tags included,
 * which is what a {@code #tag} in the config resolves through.
 */
@Mixin(RecipeManager.class)
public abstract class RecipeManagerMixin {
    @Shadow
    @Final
    private HolderLookup.Provider registries;

    @ModifyVariable(
        method = "apply(Lnet/minecraft/world/item/crafting/RecipeMap;Lnet/minecraft/server/packs/resources/ResourceManager;Lnet/minecraft/util/profiling/ProfilerFiller;)V",
        at = @At("HEAD"),
        argsOnly = true
    )
    private RecipeMap armorpieces$keepOffered(final RecipeMap loaded) {
        return OfferedRecipes.keep(loaded, this.registries);
    }
}
