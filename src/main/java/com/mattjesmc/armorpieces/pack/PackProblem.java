package com.mattjesmc.armorpieces.pack;

/**
 * One thing wrong with an installed pack, in the words an author can act on.
 *
 * @param bucket  what the mod did about it - see {@link Bucket}.
 * @param subject what it was wrong WITH: an element and the pack it came from, a recipe id, an
 *                asset. Never a class name and never a stack frame; the reader of this is somebody
 *                editing JSON, not somebody reading Java.
 * @param detail  what happened, and where possible what to do: "dropped the anchor `nose`, which is
 *                not a socket" rather than "invalid enum constant".
 */
public record PackProblem(Bucket bucket, String subject, String detail) {
    /**
     * The three things that can be done about a mistake, and the order of how bad they are.
     *
     * <p>This is the contract of {@code docs/plans/pack-mistakes.md}: every mistake belongs to
     * exactly one of these, and none of them stops a world from opening.
     */
    public enum Bucket {
        /** The element loaded without the part that was wrong: a dropped anchor, fitting, effect. */
        WORKED_AROUND("worked around"),
        /** The element could not be read at all and was left out. Its id is simply not installed. */
        SKIPPED("skipped"),
        /** Legal, loaded, and cannot do what it was meant to. Nothing to repair - only to say. */
        REPORTED("reported");

        private final String label;

        Bucket(final String label) {
            this.label = label;
        }

        public String label() {
            return this.label;
        }
    }

    @Override
    public String toString() {
        return this.subject + ": " + this.detail;
    }
}
