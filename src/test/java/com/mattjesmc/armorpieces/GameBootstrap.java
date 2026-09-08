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
