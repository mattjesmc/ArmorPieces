package com.mattjesmc.armorpieces.pack;

import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.decoration.fitting.builtin.MaterialFitting;
import com.mojang.datafixers.util.Pair;
import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.DynamicOps;
import java.util.HashSet;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderSet;
import net.minecraft.core.RegistrationInfo;
import net.minecraft.core.WritableRegistry;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;

/**
 * A part naming a fitting nothing defines, kept from taking the world down with it.
 *
 * <p>This is the one mistake in a pack that a codec cannot answer on its own, and the reason is worth
 * writing down. A cross-registry reference is not resolved when it is READ: the loader hands out a
 * placeholder holder, because the fitting a part names may be in a file that has not been read yet.
 * The reference is checked at the end, when the fitting registry is frozen, and an id nothing ever
 * defined fails the freeze - {@code Unbound values in registry armorpieces:fitting} - which is fatal
 * in a way none of the rest of this package can intercept: a registry that will not freeze is
 * DROPPED from the result, so removing the error would be worse than the error.
 *
 * <p>So the reference is made to resolve. Every id a part names is remembered as it is read, and just
 * before the fitting registry freezes, each one nothing defined is registered as a {@link #standIn}:
 * a real fitting, of a type that already exists, that accepts nothing. The world opens, the part keeps
 * its other fittings, the socket that named the missing one can never be filled, and the report says
 * so by name. Install the pack that defines the fitting and the stand-in is never made.
 *
 * <p>Why a stand-in rather than dropping the reference: by freeze time the part is already built and
 * already registered, holding that very holder. Binding it is the only move left that does not leave
 * a landmine in a field twenty-four call sites iterate.
 */
public final class MissingFittings {
    /** Every fitting id a part named this load, and nothing else - inline fittings are not ids. */
    private static final Map<Identifier, Boolean> REFERENCED = new ConcurrentHashMap<>();

    private MissingFittings() {}

    /**
     * {@link Fitting#CODEC}, with the id it read written down.
     *
     * <p>Only the string form is recorded: a fitting written out inline in a part's file is a value,
     * not a reference, and can never dangle.
     */
    public static final Codec<Holder<Fitting>> TRACKED = new Codec<>() {
        @Override
        public <U> DataResult<Pair<Holder<Fitting>, U>> decode(final DynamicOps<U> ops, final U input) {
            ops.getStringValue(input).result()
                .map(Identifier::tryParse)
                .ifPresent(id -> REFERENCED.put(id, Boolean.TRUE));
            return Fitting.CODEC.decode(ops, input);
        }

        @Override
        public <U> DataResult<U> encode(final Holder<Fitting> value, final DynamicOps<U> ops, final U prefix) {
            return Fitting.CODEC.encode(value, ops, prefix);
        }

        @Override
        public String toString() {
            return "TrackedFitting";
        }
    };

    /**
     * Registers a stand-in for every id named this load that nothing defined, and forgets the rest.
     *
     * <p>Called from {@code RegistryLoadTaskMixin} at the head of the fitting registry's freeze,
     * which is the last moment the registry can be written to and the first at which every part has
     * been read.
     *
     * @return how many stand-ins were needed. Zero on every correctly written set of packs.
     */
    public static int fill(final WritableRegistry<Fitting> registry) {
        final Set<Identifier> named = new HashSet<>(REFERENCED.keySet());
        REFERENCED.clear();
        int filled = 0;
        for (final Identifier id : named) {
            final ResourceKey<Fitting> key = ResourceKey.create(ArmorPiecesRegistries.FITTING, id);
            // Bound, not merely present. An id a part named is ALREADY in the registry by now - as
            // an intent, the placeholder the loader hands out for a reference it cannot resolve yet
            // - so containsKey answers true for exactly the ids this is here to fill. Measured on a
            // real server, 2026-09-11: with containsKey the stand-in was never made and the freeze
            // still failed. register() binds that very intent rather than adding a second entry,
            // which is how the loader itself fills a forward reference.
            if (registry.get(key).map(Holder::isBound).orElse(false)) {
                continue;
            }
            registry.register(key, standIn(id), RegistrationInfo.BUILT_IN);
            filled++;
            PackProblems.workedAround(id.toString(),
                "is named by a part and no installed pack defines it. The part still loads and its "
                    + "other fittings still work; this one can never be filled. Install the pack that "
                    + "provides the fitting, or correct the id in the part's `fittings`.");
        }
        return filled;
    }

    /** What a part gets instead: a material fitting no material matches, so no item ever fills it. */
    private static Fitting standIn(final Identifier id) {
        return new MaterialFitting(
            Component.literal(id.toString()), HolderSet.direct(), Optional.empty());
    }
}
