package com.mattjesmc.armorpieces.recipe;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.cloth.ClothValue;
import com.mattjesmc.armorpieces.config.ArmorPiecesServerConfig;
import com.mattjesmc.armorpieces.config.PartsSwitch;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.identity.Tolerant;
import com.mattjesmc.armorpieces.mixin.ShapedRecipeAccessor;
import com.mattjesmc.armorpieces.mixin.ShapelessRecipeAccessor;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.skin.ArmorSkinValue;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.component.DataComponentMap;
import net.minecraft.core.component.DataComponentPatch;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.world.item.ItemStackTemplate;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.RecipeMap;
import net.minecraft.world.item.crafting.ShapedRecipe;
import net.minecraft.world.item.crafting.ShapelessRecipe;
import org.jspecify.annotations.Nullable;

/**
 * The recipes a server keeps, once its {@link PartsSwitch} has been asked: every template recipe
 * whose product the server does not offer is dropped as the recipes load.
 *
 * <p>A template recipe is an ordinary shaped or shapeless recipe - paper round a centre item - whose
 * result carries a part, skin, cloth or fitting as a component
 * ({@code "components": {"armorpieces:decoration": "armorpieces:bandolier"}}). The smithing
 * recipes refuse a switched-off template in {@code matches}, and that alone would leave a player
 * crafting a template that then does nothing; so the crafting recipe goes too, and with it the
 * recipe book entry, the toast and the {@code /recipe} grant, because the server never has it.
 * {@link DisabledRecipe} is the pack AUTHOR's way of taking a recipe out; this is the server owner's,
 * and it needs no file.
 *
 * <p>Only shaped and shapeless recipes are read, and only through the result TEMPLATE they hold -
 * the item and the component patch, never a stack. A stack cannot be made while the recipes load:
 * an item's default components are bound to the level's registries after the reload listeners
 * run, and {@code assemble} throws "Components not bound yet" (met on 2026-09-13, on the first
 * world load; the JVM tests bake the components first and never saw it). A special recipe is not
 * asked: what it makes depends on what is in it.
 *
 * <p>Applied by {@code RecipeManagerMixin} to the map a datapack reload just read, before the
 * manager keeps it - the same moment the loot tables are built from the same config, so one
 * {@code /reload} moves both.
 */
public final class OfferedRecipes {
    private OfferedRecipes() {
    }

    /**
     * {@code loaded} without the template recipes the server does not offer. The same map back when
     * the switch has nothing to say, so a server that has touched nothing pays nothing.
     */
    public static RecipeMap keep(final RecipeMap loaded, final HolderLookup.Provider registries) {
        final PartsSwitch offered = ArmorPiecesServerConfig.get().parts();
        if (!offered.restricts()) {
            return loaded;
        }
        final List<RecipeHolder<?>> kept = new ArrayList<>();
        int dropped = 0;
        for (final RecipeHolder<?> holder : loaded.values()) {
            final Holder<?> makes = makes(holder.value());
            if (makes != null && !offered.offers(makes, registries)) {
                dropped++;
                ArmorPieces.LOGGER.debug("[Armor Pieces] Recipe {} makes a template for {}, which this server does not offer; dropped.",
                    holder.id().identifier(), makes.unwrapKey().map(key -> key.identifier().toString()).orElse("?"));
                continue;
            }
            kept.add(holder);
        }
        if (dropped == 0) {
            return loaded;
        }
        ArmorPieces.LOGGER.info("[Armor Pieces] {} template recipe(s) dropped: their parts are switched off in {}.",
            dropped, "config/" + ArmorPieces.MOD_ID + "-server.json");
        return RecipeMap.create(kept);
    }

    /**
     * The part, skin, cloth or fitting {@code recipe} makes a template FOR, or null if it makes
     * nothing of ours - or is not a recipe that can be asked without a grid.
     */
    public static @Nullable Holder<?> makes(final Recipe<?> recipe) {
        final ItemStackTemplate result;
        if (recipe instanceof ShapedRecipe shaped) {
            result = ((ShapedRecipeAccessor) shaped).armorpieces$result();
        } else if (recipe instanceof ShapelessRecipe shapeless) {
            result = ((ShapelessRecipeAccessor) shapeless).armorpieces$result();
        } else {
            return null;
        }
        // The patch alone, with nothing to fall back on: what a template recipe carries is always
        // written on the result, never an item default, and asking the item would bind components.
        final DataComponentPatch written = result.components();
        final Holder<ArmorDecoration> part = resolved(written, ModDataComponents.DECORATION);
        if (part != null) {
            return part;
        }
        final ArmorSkinValue skin = resolved(written, ModDataComponents.SKIN);
        if (skin != null) {
            return skin.skin();
        }
        final ClothValue cloth = resolved(written, ModDataComponents.CLOTH);
        if (cloth != null) {
            return cloth.cloth();
        }
        return resolved(written, ModDataComponents.FITTING);
    }

    private static <T> @Nullable T resolved(
        final DataComponentPatch patch,
        final DataComponentType<Tolerant<T>> type
    ) {
        final Tolerant<T> value = patch.get(DataComponentMap.EMPTY, type);
        return value == null ? null : value.orNull();
    }
}
