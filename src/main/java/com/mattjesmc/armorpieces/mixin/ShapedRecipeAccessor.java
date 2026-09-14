package com.mattjesmc.armorpieces.mixin;

import net.minecraft.world.item.ItemStackTemplate;
import net.minecraft.world.item.crafting.ShapedRecipe;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * The result a shaped recipe would make, as the TEMPLATE it holds rather than a stack. Read while
 * the recipes load, when a stack cannot be made yet: an item's default components are bound to the
 * level's registries after the reload listeners run, and {@code assemble} would throw
 * "Components not bound yet". See {@code OfferedRecipes}.
 */
@Mixin(ShapedRecipe.class)
public interface ShapedRecipeAccessor {
    @Accessor("result")
    ItemStackTemplate armorpieces$result();
}
