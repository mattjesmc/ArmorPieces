package com.mattjesmc.armorpieces.block;

import com.mattjesmc.armorpieces.menu.AdvancedSmithingMenu;
import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.MenuProvider;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ContainerLevelAccess;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;

/**
 * The block that opens {@link AdvancedSmithingMenu}: a smithing table that can also take a part OFF,
 * and shows a whole set on a stand while it works.
 *
 * <p>Shaped exactly like {@code SmithingTableBlock}: no block entity, no state, a menu provider and a
 * right-click. What the table holds while it is open lives in the menu and goes back to the player
 * when it closes, which is the vanilla crafting-station contract and the reason a table left
 * mid-operation never eats anything.
 */
public class AdvancedSmithingTableBlock extends Block {
    public static final MapCodec<AdvancedSmithingTableBlock> CODEC = simpleCodec(AdvancedSmithingTableBlock::new);
    private static final Component CONTAINER_TITLE = Component.translatable("container.armorpieces.advanced_smithing");

    public AdvancedSmithingTableBlock(final BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    public MapCodec<AdvancedSmithingTableBlock> codec() {
        return CODEC;
    }

    @Override
    protected MenuProvider getMenuProvider(final BlockState state, final Level level, final BlockPos pos) {
        return new SimpleMenuProvider(
            (containerId, inventory, player) ->
                new AdvancedSmithingMenu(containerId, inventory, ContainerLevelAccess.create(level, pos)),
            CONTAINER_TITLE);
    }

    @Override
    protected InteractionResult useWithoutItem(
        final BlockState state,
        final Level level,
        final BlockPos pos,
        final Player player,
        final BlockHitResult hitResult
    ) {
        if (!level.isClientSide()) {
            player.openMenu(state.getMenuProvider(level, pos));
        }
        return InteractionResult.SUCCESS;
    }
}
