package com.mattjesmc.armorpieces.pack;

import com.mojang.datafixers.util.Pair;
import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.DynamicOps;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Stream;

/**
 * List fields that survive one bad entry.
 *
 * <p>The whole of the difference this makes: {@code "anchors": ["crest", "nose"]} is a part on the
 * crest with a warning about {@code nose}, where {@code Codec.listOf()} makes it a part that does not
 * load - and, because {@code RegistryDataLoader} collects element failures and throws at the end of
 * the load, a WORLD that does not open. See {@code docs/plans/pack-mistakes.md} for what that costs
 * today, measured.
 *
 * <p>The bargain is the same one {@link com.mattjesmc.armorpieces.identity.Tolerant} strikes on the
 * item side: the cost of a mistake should be proportional to it. One unreadable entry costs that
 * entry. What it deliberately does NOT do is hide the mistake - every drop is a line in
 * {@link PackProblems}, named by the file {@link PackFile} says is being read.
 *
 * <p>Not applied to a field whose absence leaves nothing behind. A part with no {@code asset_id} has
 * nothing to draw, so it is skipped whole rather than loaded as an invisible part; a part with no
 * anchors left IS loaded, because it can still be named, held and rebound the day its pack is fixed,
 * and {@link com.mattjesmc.armorpieces.pack.PackAudit} says it can never be worn.
 */
public final class Lenient {
    private Lenient() {}

    /**
     * A list codec that drops the entries it cannot read.
     *
     * <p>Fails only when the field is not a list at all - {@code "anchors": "crest"} is a mistake
     * with no salvage in it, since there is no entry to keep and no way to guess what was meant.
     *
     * @param element what one entry is read with.
     * @param what    the entry's name in a warning, singular: "anchor", "fitting", "effect".
     */
    public static <T> Codec<List<T>> list(final Codec<T> element, final String what) {
        return new Codec<>() {
            @Override
            public <U> DataResult<Pair<List<T>, U>> decode(final DynamicOps<U> ops, final U input) {
                final DataResult<Stream<U>> entries = ops.getStream(input);
                final Optional<Stream<U>> stream = entries.result();
                if (stream.isEmpty()) {
                    return DataResult.error(() -> "the " + what + " list is not a list: "
                        + entries.error().map(DataResult.Error::message).orElse("unreadable"));
                }
                final List<T> kept = new ArrayList<>();
                stream.get().forEach(entry -> {
                    final DataResult<Pair<T, U>> one = element.decode(ops, entry);
                    final Optional<Pair<T, U>> read = one.result();
                    if (read.isPresent()) {
                        kept.add(read.get().getFirst());
                        return;
                    }
                    PackProblems.workedAround(PackFile.current(), "dropped one " + what + " that "
                        + "could not be read - " + one.error().map(DataResult.Error::message)
                            .orElse("no reason given") + ". The rest of the file still loaded.");
                });
                // Deliberately success even when everything was dropped: an empty list is a legal
                // value of every field this is used for, and the report already says what went.
                return DataResult.success(Pair.of(List.copyOf(kept), ops.empty()));
            }

            @Override
            public <U> DataResult<U> encode(final List<T> value, final DynamicOps<U> ops, final U prefix) {
                // Writing is strict on purpose. Nothing unreadable can be in the value by now, and a
                // lenient encoder would be a way to lose data on the way OUT, which is the one
                // direction this mod never tolerates - see Tolerant.
                return element.listOf().encode(value, ops, prefix);
            }

            @Override
            public String toString() {
                return "Lenient[" + element + "]";
            }
        };
    }
}
