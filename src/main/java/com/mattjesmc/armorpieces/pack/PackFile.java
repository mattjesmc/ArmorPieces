package com.mattjesmc.armorpieces.pack;

import java.util.Optional;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import org.jspecify.annotations.Nullable;

/**
 * Which pack file is being read on this thread right now.
 *
 * <p>It exists for one sentence. A codec that drops a socket it cannot name knows what it dropped and
 * has no idea WHERE FROM: a {@code Codec} is handed a {@code DynamicOps} and a value, never an id and
 * never a pack. A warning that says "an anchor named `nose` was dropped" is not something a pack
 * author can act on; "armorpieces_coral:coral_crown, from pack coral: dropped the anchor `nose`" is.
 *
 * <p>So the mixin over {@code RegistryLoadTask$PendingRegistration} - the one place in the game where
 * an element's key and the {@link net.minecraft.server.packs.resources.Resource} it came out of are
 * both in hand - writes them here for the length of that one decode, and every warning raised
 * underneath, however deep in a codec, can name the file.
 *
 * <p>A thread local rather than a field because the load is parallel: {@code ParallelMapTransform}
 * decodes a registry's files across the whole executor, so two packs' files are genuinely being read
 * at the same moment. Set and cleared around one decode, never nested - an element is read by one
 * thread from start to finish.
 */
public final class PackFile {
    private record Reading(Identifier element, @Nullable String pack) {
        @Override
        public String toString() {
            return this.pack == null ? this.element.toString()
                : this.element + ", from pack " + this.pack;
        }
    }

    private static final ThreadLocal<Reading> CURRENT = new ThreadLocal<>();

    /** What a warning calls a file when nothing told us which one it was. */
    private static final String UNKNOWN = "a pack file";

    private PackFile() {}

    /** Called by the mixin as an element's own decode begins. */
    public static void reading(final ResourceKey<?> element, final @Nullable String pack) {
        CURRENT.set(new Reading(element.identifier(), pack));
    }

    /** Called by the mixin as that decode ends, however it ended. */
    public static void done() {
        CURRENT.remove();
    }

    /** The file being read, named the way a warning should name it. Never null, never empty. */
    public static String current() {
        final Reading reading = CURRENT.get();
        return reading == null ? UNKNOWN : reading.toString();
    }

    /** The id of the element being read, if one is. */
    public static Optional<Identifier> currentId() {
        final Reading reading = CURRENT.get();
        return reading == null ? Optional.empty() : Optional.of(reading.element());
    }
}
