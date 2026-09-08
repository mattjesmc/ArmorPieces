package com.mattjesmc.armorpieces.identity;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.Registry;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import org.jspecify.annotations.Nullable;

/**
 * The index that finds a piece an id no longer names, and the tally of the ones nothing can find.
 *
 * <p>A saved item names its part by id. When that id no longer resolves - the pack moved it, renamed
 * it, or is simply not installed - this is what is asked next, in the order
 * {@code docs/plans/compatibility.md} sets out: the id first (which has already failed by the time
 * anything here is called), then {@link Identified#formerIds()}, then {@link Identified#uid()}, and
 * only then is the entry kept as raw data and counted here as missing.
 *
 * <p><b>Why an index and not a lookup.</b> Component decode is handed a {@code HolderGetter}, which
 * answers "what is at this id" and nothing else. Both remaining questions run the other way - "which
 * piece USED to be at this id", "which piece carries this uid" - and answering them needs the whole
 * registry enumerated. So the registry is walked once when it loads and the two reverse maps are kept
 * here.
 *
 * <p><b>Why static, and why that is safe.</b> A codec has no way to be handed a service. The index is
 * rebuilt from the authoritative registry every time one is loaded, which on a server is world load
 * and every {@code /reload}, and on a client is joining a world. Reading a saved item can only happen
 * after one of those. The maps are replaced wholesale rather than mutated, so a decode running while
 * a reload finishes sees one consistent index or the other.
 *
 * <p>Only the three content registries are indexed. Fittings are not: a fitting's TYPE is code, its
 * values are few and defined by the mod, and it has never moved - so a fitting a save cannot resolve
 * is kept as raw data (which is what stops the item being destroyed) but is not rebound.
 */
public final class Rebind {
    /** Registry key to the reverse map for that registry. Replaced wholesale, never mutated. */
    private static volatile Map<ResourceKey<? extends Registry<?>>, Map<String, Holder<?>>> index = Map.of();

    /** Every id this session could not resolve at all, and how often it was seen. */
    private static final Map<Miss, AtomicInteger> MISSES = new ConcurrentHashMap<>();

    /** Told the first time each distinct id goes missing, so somebody can be warned. */
    private static volatile Consumer<Miss> listener = miss -> {};

    private Rebind() {}

    /** One id that nothing installed can name, and the registry it was looked for in. */
    public record Miss(ResourceKey<? extends Registry<?>> registry, String id) {}

    /**
     * Walks the three content registries and builds the reverse maps.
     *
     * <p>Called from world load, {@code /reload} and the client's join. A registry the provider does
     * not hold is skipped rather than failing: a lookup built for datagen or a test need not have all
     * three.
     */
    public static void rebuild(final HolderLookup.Provider registries) {
        final Map<ResourceKey<? extends Registry<?>>, Map<String, Holder<?>>> built = new HashMap<>();
        index(built, registries, ArmorPiecesRegistries.ARMOR_DECORATION);
        index(built, registries, ArmorPiecesRegistries.ARMOR_SKIN);
        index(built, registries, ArmorPiecesRegistries.CLOTH);
        index = Map.copyOf(built);
    }

    /** Forgets the index, so a codec run outside a world rebinds nothing rather than using a stale map. */
    public static void clear() {
        index = Map.of();
    }

    private static <T extends Identified> void index(
        final Map<ResourceKey<? extends Registry<?>>, Map<String, Holder<?>>> into,
        final HolderLookup.Provider registries,
        final ResourceKey<Registry<T>> key
    ) {
        final Optional<? extends HolderLookup.RegistryLookup<T>> lookup = registries.lookup(key);
        if (lookup.isEmpty()) {
            return;
        }
        final Map<String, Holder<?>> map = new HashMap<>();
        lookup.get().listElements().forEach(entry -> {
            final T value = entry.value();
            for (final Identifier former : value.formerIds()) {
                // putIfAbsent, not put: two packs claiming one former id is a collision the additive
                // checker exists to catch, and the first one wins rather than the last one loaded.
                map.putIfAbsent(formerKey(former), entry);
            }
            value.uid().ifPresent(uid -> map.putIfAbsent(uidKey(uid), entry));
        });
        if (!map.isEmpty()) {
            into.put(key, map);
        }
    }

    private static String formerKey(final Identifier id) {
        return "id/" + id;
    }

    private static String uidKey(final String uid) {
        return "uid/" + uid;
    }

    /**
     * The piece that used to answer to {@code id}, if one declares it.
     *
     * @param registry which content registry to look in
     */
    public static <T> Optional<Holder<T>> byFormerId(
        final ResourceKey<? extends Registry<? extends T>> registry,
        final Identifier id
    ) {
        return lookup(registry, formerKey(id));
    }

    /** The piece carrying this lineage identifier, if one does. */
    public static <T> Optional<Holder<T>> byUid(
        final ResourceKey<? extends Registry<? extends T>> registry,
        final String uid
    ) {
        return lookup(registry, uidKey(uid));
    }

    /**
     * Both, in the order the plan sets: a declared former id beats a uid.
     *
     * <p>That order matters when an author renames a piece AND a different piece inherits the uid
     * through a fork: the declaration is a statement of intent by whoever owns the id, and intent
     * wins over inference.
     */
    public static <T> Optional<Holder<T>> find(
        final ResourceKey<? extends Registry<? extends T>> registry,
        final @Nullable Identifier id,
        final @Nullable String uid
    ) {
        if (id != null) {
            final Optional<Holder<T>> byFormer = byFormerId(registry, id);
            if (byFormer.isPresent()) {
                return byFormer;
            }
        }
        return uid == null ? Optional.empty() : byUid(registry, uid);
    }

    @SuppressWarnings("unchecked")
    private static <T> Optional<Holder<T>> lookup(
        final ResourceKey<? extends Registry<? extends T>> registry,
        final String key
    ) {
        final Map<String, Holder<?>> map = index.get(registry);
        if (map == null) {
            return Optional.empty();
        }
        return Optional.ofNullable((Holder<T>) map.get(key));
    }

    /**
     * Records that something named {@code id} and nothing could find it.
     *
     * <p>One log line per distinct id per session, never per item and never per tick - a chest of
     * fifty decorated helmets is one line, not fifty. The running count is what
     * {@code /armorpieces missing} prints.
     */
    public static void miss(final ResourceKey<? extends Registry<?>> registry, final String id) {
        final Miss miss = new Miss(registry, id);
        final boolean[] first = {false};
        final AtomicInteger count = MISSES.computeIfAbsent(miss, key -> {
            first[0] = true;
            ArmorPieces.LOGGER.warn(
                "[Armor Pieces] {} is not installed - armor wearing it keeps it but cannot show it."
                    + " Install the pack that provides it, or run /armorpieces missing.", id);
            return new AtomicInteger();
        });
        count.incrementAndGet();
        if (first[0]) {
            // Outside computeIfAbsent: the listener touches the server, and a mapping function that
            // does anything but compute is how a ConcurrentHashMap deadlocks.
            listener.accept(miss);
        }
    }

    /** Sets who is told when an id goes missing for the first time this session. */
    public static void onNewMiss(final Consumer<Miss> onMiss) {
        listener = onMiss;
    }

    /** Everything this session could not resolve, commonest first. For the command. */
    public static List<Map.Entry<Miss, Integer>> misses() {
        return MISSES.entrySet().stream()
            .map(e -> Map.<Miss, Integer>entry(e.getKey(), e.getValue().get()))
            .sorted((a, b) -> Integer.compare(b.getValue(), a.getValue()))
            .toList();
    }

    /** Whether anything at all has failed to resolve. */
    public static boolean anyMissing() {
        return !MISSES.isEmpty();
    }

    /** Forgets the tally. Called when a world is left, so a second world starts with a clean count. */
    public static void forgetMisses() {
        MISSES.clear();
    }

    /** The three registries this indexes, for the command and the tests to enumerate. */
    public static List<ResourceKey<? extends Registry<?>>> indexed() {
        return List.of(
            ArmorPiecesRegistries.ARMOR_DECORATION,
            ArmorPiecesRegistries.ARMOR_SKIN,
            ArmorPiecesRegistries.CLOTH);
    }
}
