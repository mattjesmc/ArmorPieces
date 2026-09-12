package com.mattjesmc.armorpieces.pack;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.pack.PackProblem.Bucket;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;

/**
 * Everything wrong with the packs this installation has, and the only place it is remembered.
 *
 * <p>Static, and for the reason {@link com.mattjesmc.armorpieces.identity.Rebind} is: most of what is
 * filed here is filed from inside a CODEC, which has no way to be handed a service. The two are
 * deliberately the same shape - one line per distinct problem, a running count, a listener for
 * whoever wants to tell a player - because they answer the two halves of the same question. Rebind
 * says what this world names and this installation does not have; this says what this installation
 * has and could not use.
 *
 * <p><b>One line per distinct problem, ever.</b> A pack with a broken part is read once, but a
 * missing asset is asked for on every frame that draws it, and a log that says so sixty times a
 * second is a log nobody reads. So the first sighting logs and every later one only counts.
 *
 * <p><b>Cleared when the server stops, not when it reloads.</b> A datapack REGISTRY is read exactly
 * once, when the world loads - {@code /reload} does not touch it (measured; see
 * {@link com.mattjesmc.armorpieces.identity.Compatibility}) - so a problem found at load is still
 * true after a reload, and clearing it there would quietly empty the report an operator is reading.
 */
public final class PackProblems {
    /** Distinct problem to how many times it was seen. Concurrent: the load is a parallel one. */
    private static final Map<PackProblem, AtomicInteger> PROBLEMS = new ConcurrentHashMap<>();

    /** Told the first time each distinct problem is seen, so somebody can be warned. */
    private static volatile Consumer<PackProblem> listener = problem -> {};

    private PackProblems() {}

    /** The element loaded without the piece of it that was wrong. */
    public static void workedAround(final String subject, final String detail) {
        note(new PackProblem(Bucket.WORKED_AROUND, subject, detail));
    }

    /** The element could not be read at all, and is not installed. */
    public static void skipped(final String subject, final String detail) {
        note(new PackProblem(Bucket.SKIPPED, subject, detail));
    }

    /** It loaded, it is legal, and it cannot do what it was meant to. */
    public static void reported(final String subject, final String detail) {
        note(new PackProblem(Bucket.REPORTED, subject, detail));
    }

    private static void note(final PackProblem problem) {
        final boolean[] first = {false};
        final AtomicInteger count = PROBLEMS.computeIfAbsent(problem, key -> {
            first[0] = true;
            ArmorPieces.LOGGER.warn("[Armor Pieces] {} ({}): {}",
                problem.subject(), problem.bucket().label(), problem.detail());
            return new AtomicInteger();
        });
        count.incrementAndGet();
        if (first[0]) {
            // Outside computeIfAbsent: the listener touches the server, and a mapping function that
            // does anything but compute is how a ConcurrentHashMap deadlocks.
            listener.accept(problem);
        }
    }

    /** Sets who is told the first time a distinct problem is seen. */
    public static void onNewProblem(final Consumer<PackProblem> onProblem) {
        listener = onProblem;
    }

    /** Every problem and how often it was seen, worst bucket first, then commonest. For the command. */
    public static List<Map.Entry<PackProblem, Integer>> all() {
        return PROBLEMS.entrySet().stream()
            .map(entry -> Map.entry(entry.getKey(), entry.getValue().get()))
            .sorted((a, b) -> {
                final int bucket = a.getKey().bucket().compareTo(b.getKey().bucket());
                return bucket != 0 ? bucket : b.getValue().compareTo(a.getValue());
            })
            .toList();
    }

    /** How many distinct problems in each bucket. Buckets with none are absent. */
    public static Map<Bucket, Integer> counts() {
        final Map<Bucket, Integer> byBucket = new EnumMap<>(Bucket.class);
        PROBLEMS.keySet().forEach(problem ->
            byBucket.merge(problem.bucket(), 1, Integer::sum));
        return byBucket;
    }

    public static boolean any() {
        return !PROBLEMS.isEmpty();
    }

    public static int count() {
        return PROBLEMS.size();
    }

    /** Forgets everything. Called when a server stops, so the next world starts with a clean report. */
    public static void clear() {
        PROBLEMS.clear();
    }

    /**
     * The one line at the end of a load that says whether anything is wrong, and where to look.
     *
     * <p>Logged even when nothing is wrong, because "every pack loaded cleanly" is the sentence a
     * pack author wants after fixing something, and a report that only ever appears when it is bad
     * news leaves them unable to tell success from a check that did not run.
     */
    public static void summarise(final String where) {
        if (PROBLEMS.isEmpty()) {
            ArmorPieces.LOGGER.info("[Armor Pieces] Every installed pack loaded cleanly ({}).", where);
            return;
        }
        final Map<Bucket, Integer> byBucket = counts();
        ArmorPieces.LOGGER.warn(
            "[Armor Pieces] {} problem(s) in the installed packs ({}): {} skipped, {} worked around, "
                + "{} reported. Nothing was refused and the world is loaded; run /armorpieces packs "
                + "for the list.",
            PROBLEMS.size(), where,
            byBucket.getOrDefault(Bucket.SKIPPED, 0),
            byBucket.getOrDefault(Bucket.WORKED_AROUND, 0),
            byBucket.getOrDefault(Bucket.REPORTED, 0));
    }
}
