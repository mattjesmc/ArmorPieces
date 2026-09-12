package com.mattjesmc.armorpieces.mixin;

import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.pack.MissingFittings;
import com.mattjesmc.armorpieces.pack.PackSkips;
import java.util.Map;
import net.minecraft.core.Registry;
import net.minecraft.core.WritableRegistry;
import net.minecraft.resources.RegistryDataLoader;
import net.minecraft.resources.RegistryLoadTask;
import net.minecraft.resources.ResourceKey;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * One unreadable file in one pack costs that file, not the world.
 *
 * <p><b>What it is fixing, measured 2026-09-11.</b> {@code RegistryDataLoader} reads every element of
 * a datapack registry, files the ones that failed into {@code loadingErrors}, and throws a
 * {@code ReportedException} over that map at the end of the load. So a truncated JSON file, a missing
 * {@code description}, an anchor spelled {@code nose} - any one of them, in any one file of any
 * installed pack - takes down {@code armorpieces:armor_decoration} entirely, this mod's own parts
 * included, and the world does not open. Worse, the throw happens on the background executor, whose
 * uncaught handler answers a {@code ReportedException} with {@code System.exit(-1)}: a dedicated
 * server does not print an error and carry on, it ends. The whole table is in
 * {@code docs/plans/pack-mistakes.md}.
 *
 * <p><b>Where it intervenes.</b> {@code registerElements} is where a load's failures become entries in
 * that map, and every element of a registry has been through it by the time it returns. What happens
 * to them is {@link PackSkips#rescue}, in ordinary Java: an entry belonging to one of this mod's five
 * registries is taken back out and reported, and the element is simply absent - which is the same
 * state as its pack not being installed, one the mod already handles end to end
 * ({@link com.mattjesmc.armorpieces.identity.Tolerant}: the item keeps the part as raw data and gets
 * it back the day the file is fixed).
 *
 * <p>Deliberately narrow. The map is the whole load's, shared by every registry being read, and an
 * error left in it is fatal exactly as it was - this mod has no business deciding that another mod's
 * broken biome is survivable. It serves the network loader too, by being on the shared base class: a
 * client that cannot read a synced element drops that element instead of being disconnected.
 */
@Mixin(RegistryLoadTask.class)
public abstract class RegistryLoadTaskMixin<T> {
    @Shadow
    @Final
    protected RegistryDataLoader.RegistryData<T> data;

    @Shadow
    @Final
    protected Map<ResourceKey<?>, Exception> loadingErrors;

    @Shadow
    @Final
    private WritableRegistry<T> registry;

    /**
     * A fitting a part named and nothing defined, given something to point at.
     *
     * <p>The head of the freeze is the last moment the registry can be written to and the first at
     * which every part has been read, which is what makes it the only place this can be done. Why it
     * has to be done at all - a reference that will not resolve fails the freeze, and a registry that
     * fails to freeze is dropped from the load entirely - is written out in {@link MissingFittings}.
     */
    @SuppressWarnings("unchecked")
    @Inject(method = "freezeRegistry", at = @At("HEAD"))
    private void armorpieces$fillMissingFittings(
        final Map<ResourceKey<?>, Exception> errors,
        final CallbackInfoReturnable<Boolean> info
    ) {
        if (ArmorPiecesRegistries.FITTING.equals(this.data.key())) {
            MissingFittings.fill((WritableRegistry<Fitting>) this.registry);
        }
    }

    @Inject(method = "registerElements", at = @At("RETURN"))
    private void armorpieces$keepTheRestOfTheWorld(final CallbackInfo info) {
        final ResourceKey<? extends Registry<T>> registry = this.data.key();
        if (ArmorPiecesRegistries.isOurs(registry)) {
            PackSkips.rescue(registry, this.loadingErrors);
        }
    }
}
