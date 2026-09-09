package com.mattjesmc.armorpieces;

import net.minecraft.SharedConstants;
import net.minecraft.server.Bootstrap;

/**
 * Brings up as much of the game as a codec needs, once per test JVM.
 *
 * <p>Two layers have to be there before a codec that names a registry can even be built, and each
 * fails differently. {@code fabric-loader-junit} (a test dependency in build.gradle) runs the tests
 * under Knot with the mixins applied, which is what lets Fabric's registry API reach
 * {@code BuiltInRegistries}; without it a class that registers a dynamic registry cannot initialise
 * at all. {@link Bootstrap} then fills the built-in registries themselves - vanilla refuses to
 * register into them before it has been called, with "Not bootstrapped".
 *
 * <p>Neither is a game: no world, no server, no client. Anything needing a loaded datapack or a
 * registry access belongs in the gate's tier 2, not here.
 */
public final class GameBootstrap {
    private static boolean done;

    private GameBootstrap() {
    }

    private static boolean components;

    /**
     * The mod's item components, once per JVM.
     *
     * <p>Separate from {@link #once()} because it is a different layer: bootstrapping fills VANILLA's
     * registries, and this registers into one of them. A second call would throw, so the flag is not
     * an optimisation.
     */
    public static synchronized void components() {
        if (components) {
            return;
        }
        once();
        com.mattjesmc.armorpieces.registry.ModDataComponents.register();
        components = true;
    }

    private static boolean types;

    /**
     * The mod's effect and fitting TYPES, once per JVM.
     *
     * <p>A third layer, and the one a datapack test cannot do without: both registries hold
     * {@link com.mojang.serialization.MapCodec}s, which is to say code, so a part naming
     * {@code armorpieces:glide} or a fitting naming {@code armorpieces:material} is an unknown
     * dispatch key until the mod has put that key on the shelf. The flag is not an optimisation -
     * {@link net.minecraft.core.Registry#register} throws on a second registration of the same id.
     */
    public static synchronized void types() {
        if (types) {
            return;
        }
        once();
        com.mattjesmc.armorpieces.decoration.effect.DecorationEffects.register();
        com.mattjesmc.armorpieces.decoration.fitting.Fittings.register();
        types = true;
    }

    private static boolean content;

    /**
     * Everything this mod puts into a BUILT-IN registry: its components, its block and items, its
     * recipe serializers, its menu, and the two loot pieces. The order is
     * {@link com.mattjesmc.armorpieces.ArmorPieces#onInitialize()}'s own, and for its reasons -
     * a template item reads the decoration component, so components come first.
     *
     * <p>What this is FOR: a datapack file may name any of them. {@code data/minecraft/tags/block/
     * mineable/axe.json} names the advanced smithing table, and a tag whose member does not exist is
     * not a smaller tag - the whole tag is dropped. So a test that reads this repository's tags
     * without this has vanilla's game, not this mod's, and fails on the mod's own files.
     *
     * <p>Still nothing that needs a game: every call below writes into a registry. The parts of
     * {@code onInitialize} that subscribe to an event or read a config are not here.
     */
    public static synchronized void content() {
        if (content) {
            return;
        }
        types();
        components();
        com.mattjesmc.armorpieces.registry.ModBlocks.register();
        com.mattjesmc.armorpieces.registry.ModItems.register();
        com.mattjesmc.armorpieces.registry.ModRecipeSerializers.register();
        com.mattjesmc.armorpieces.registry.ModMenus.register();
        com.mattjesmc.armorpieces.registry.ModLootFunctions.register();
        com.mattjesmc.armorpieces.registry.ModLootEntries.register();
        content = true;
    }

    /** Idempotent: {@link Bootstrap#bootStrap()} is itself a no-op the second time, this is cheaper. */
    public static synchronized void once() {
        if (done) {
            return;
        }
        SharedConstants.tryDetectVersion();
        Bootstrap.bootStrap();
        done = true;
    }
}
