package com.mattjesmc.armorpieces.client.mixin;

import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import org.jspecify.annotations.Nullable;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * Lets the client forget which parameters the creative tabs were last built for.
 *
 * <p>{@code CreativeModeTabs.tryRebuildTabContents} rebuilds every tab only when the feature flags,
 * the operator bit or the registries changed since the last build. The server's {@code parts}
 * switch is none of those, so when a new one arrives ({@code PartsSwitchPayload}) the cache is
 * cleared here and the next look at the creative screen builds the tab against it.
 */
@Mixin(CreativeModeTabs.class)
public interface CreativeModeTabsAccessor {
    @Accessor("CACHED_PARAMETERS")
    static void armorpieces$setCachedParameters(final CreativeModeTab.@Nullable ItemDisplayParameters parameters) {
        throw new AssertionError("replaced by the accessor");
    }
}
