package com.mattjesmc.armorpieces.pack;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import net.minecraft.core.Registry;
import net.minecraft.resources.ResourceKey;
import org.jspecify.annotations.Nullable;

/**
 * Turning a registry load's fatal errors into skipped files - the rule, with the mixin left as a seam.
 *
 * <p>{@code RegistryDataLoader} collects every element that could not be read into one map and throws
 * over it at the end of the load, so one unreadable file in one pack stops the world from opening and
 * takes every other pack's content with it. {@code RegistryLoadTaskMixin} is where that map is reached;
 * what is done with it is here, in ordinary Java, so that it can be read and tested without a game.
 *
 * <p>Only entries belonging to the five registries this mod loads are touched. The map is the whole
 * load's - vanilla's worldgen and every other mod's registries write into the same one - and an error
 * left in it is still fatal, exactly as it was.
 */
public final class PackSkips {
    private PackSkips() {}

    /**
     * Takes one registry's failures out of the load's error map and files them as skipped.
     *
     * @param registry the registry whose failures are to be rescued.
     * @param errors   the load's error map, mutated: an entry removed here is one the game will not
     *                 throw over.
     * @return how many elements were skipped.
     */
    public static int rescue(
        final ResourceKey<? extends Registry<?>> registry,
        final Map<ResourceKey<?>, Exception> errors
    ) {
        if (errors.isEmpty()) {
            return 0;
        }
        // Collected before removing: the map is written by every registry's task as it finishes, so
        // it is read once and mutated by key afterwards rather than through its own iterator.
        final List<ResourceKey<?>> ours = new ArrayList<>();
        errors.keySet().forEach(element -> {
            if (element.isFor(registry)) {
                ours.add(element);
            }
        });
        for (final ResourceKey<?> element : ours) {
            PackProblems.skipped(element.identifier().toString(), why(errors.remove(element))
                + " The file was left out and everything else loaded. Nothing that already names "
                + "this id is lost - it comes back the moment the file can be read.");
        }
        return ours.size();
    }

    /**
     * The reason, as deep as it goes.
     *
     * <p>Both ends of the chain are worth keeping and they say different things: vanilla's own outer
     * message names the file and the pack it came out of ("Failed to parse x:y from pack z"), and the
     * cause under it is the thing an author has to change - the missing field, the unknown socket, the
     * column the JSON broke at. A cause whose message is already contained in the one above it is
     * dropped, because the commonest chain says the same sentence twice.
     */
    public static String why(final @Nullable Exception failure) {
        if (failure == null) {
            return "could not be read.";
        }
        final StringBuilder said = new StringBuilder(
            failure.getMessage() == null ? failure.getClass().getSimpleName() : failure.getMessage());
        Throwable cause = failure.getCause();
        while (cause != null && cause != cause.getCause()) {
            final String message = cause.getMessage();
            if (message != null && said.indexOf(message) < 0) {
                said.append(" - ").append(message);
            }
            cause = cause.getCause();
        }
        return said.append('.').toString();
    }
}
