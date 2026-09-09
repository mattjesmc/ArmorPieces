package com.mattjesmc.armorpieces.data;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;
import net.minecraft.core.Registry;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.core.Holder;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.tags.TagKey;
import net.minecraft.tags.TagLoader;
import org.junit.jupiter.api.Test;

/**
 * A tag nobody can resolve is not an error. That is the whole problem.
 *
 * <p>{@link com.mattjesmc.armorpieces.loot.MemberSet} exists because a tag has to be allowed to be
 * missing - a group saying "one of the knightly parts, if that pack is here" must not take its loot
 * table down when the pack is absent. The price of that tolerance is paid here: a typo in
 * {@code court.json}, a part renamed and not renamed in the tag beside it, or a tag file in the
 * wrong directory, all load in silence and hand out nothing. Three loot groups, an item tag the
 * smithing table gates on and two trim-material tags the fittings are built from all fail this way.
 *
 * <p>So every tag file this repository ships is read the way the game reads it - through
 * {@link TagLoader}, over the same stacked packs the registries were loaded from - and then held to
 * two things the loader itself will not say out loud: that the tag has members at all, and that
 * every id it names is one the game can find.
 */
class ShippedTagsTest {
    @Test
    void everyShippedTagLoadsAndIsNotEmpty() {
        final ShippedData.Loaded loaded = ShippedData.everything();
        final RegistryAccess access = loaded.everyRegistry();
        final Map<Identifier, Ours> ours = shipped(loaded, access);
        assertFalse(ours.isEmpty(), "this repository ships tag files; none were found");

        // One load per registry this repository writes tags for, rather than the whole-game reload:
        // that one also holds VANILLA to every tag its own code names, which is not our business
        // here and fails on a bare bootstrap for reasons that have nothing to do with this mod.
        final Map<ResourceKey<? extends Registry<?>>, Map<Identifier, Integer>> sizes =
            new LinkedHashMap<>();
        ours.values().forEach(tag -> sizes.computeIfAbsent(tag.registry(),
            key -> members(loaded.data(), access.lookupOrThrow(cast(key)))));

        final List<String> problems = new ArrayList<>();
        ours.forEach((id, tag) -> {
            final Integer size = sizes.get(tag.registry()).get(id);
            if (size == null || size == 0) {
                problems.add(id + " (" + tag.registry().identifier() + ") is empty: every id in "
                    + tag.file() + " was dropped, or the file is not where the game looks");
            }
        });
        assertTrue(problems.isEmpty(), () -> "tags that hand out nothing:\n  "
            + String.join("\n  ", problems));
    }

    /**
     * And every id a tag names is one that exists. A missing member is dropped with a line in a log
     * nobody reads, so the tag stays valid and simply holds one part fewer - which is exactly how a
     * loot group comes to be a fifth smaller than it says.
     */
    @Test
    void everyIdATagNamesExists() {
        final ShippedData.Loaded loaded = ShippedData.everything();
        final RegistryAccess access = loaded.everyRegistry();
        final Map<Identifier, Ours> ours = shipped(loaded, access);
        final List<String> missing = new ArrayList<>();
        ours.forEach((id, tag) -> {
            final Registry<?> registry = access.lookupOrThrow(cast(tag.registry()));
            for (final String entry : tag.entries()) {
                if (entry.startsWith("#")) {
                    final Identifier other = Identifier.parse(entry.substring(1));
                    if (!ours.containsKey(other)) {
                        // A nested tag from another pack is legitimate; one of ours has to be ours.
                        continue;
                    }
                    continue;
                }
                final Identifier member = Identifier.parse(entry);
                if (!registry.containsKey(member)) {
                    missing.add(tag.file() + " names " + member + ", which no pack defines");
                }
            }
        });
        assertTrue(missing.isEmpty(), () -> "tag members that do not exist:\n  "
            + String.join("\n  ", missing));
    }

    // ---- reading the files ---------------------------------------------------------------------

    /** One tag file this repository ships: which registry it is for, and what it lists. */
    private record Ours(ResourceKey<? extends Registry<?>> registry, Path file, List<String> entries) {
    }

    /**
     * Every tag file under a pack root of ours, found the way the game finds them: a registry's tag
     * directory is {@link Registries#tagsDirPath}, so the walk is driven by the registries that
     * exist rather than by guessing at directory names.
     */
    private static Map<Identifier, Ours> shipped(
        final ShippedData.Loaded loaded, final RegistryAccess access
    ) {
        final Map<Identifier, Ours> found = new LinkedHashMap<>();
        final List<ResourceKey<? extends Registry<?>>> keys = access.registries()
            .<ResourceKey<? extends Registry<?>>>map(RegistryAccess.RegistryEntry::key)
            .toList();
        for (final Path root : loaded.roots()) {
            final Path data = root.resolve("data");
            if (!Files.isDirectory(data)) {
                continue;
            }
            try (Stream<Path> namespaces = Files.list(data)) {
                for (final Path namespace : namespaces.toList()) {
                    for (final ResourceKey<? extends Registry<?>> key : keys) {
                        // tagsDirPath already carries the "tags/" prefix, and for a registry
                        // outside minecraft its namespace too: tags/armorpieces/armor_decoration.
                        Path directory = namespace;
                        for (final String segment : Registries.tagsDirPath(key).split("/")) {
                            directory = directory.resolve(segment);
                        }
                        if (!Files.isDirectory(directory)) {
                            continue;
                        }
                        collect(namespace.getFileName().toString(), key, directory, found);
                    }
                }
            } catch (final IOException failed) {
                throw new UncheckedIOException(failed);
            }
        }
        return found;
    }

    private static void collect(
        final String namespace,
        final ResourceKey<? extends Registry<?>> key,
        final Path directory,
        final Map<Identifier, Ours> into
    ) {
        try (Stream<Path> walk = Files.walk(directory)) {
            for (final Path file : walk.filter(path -> path.toString().endsWith(".json")).toList()) {
                final String path = directory.relativize(file).toString()
                    .replace('\\', '/').replaceAll("\\.json$", "");
                into.put(Identifier.fromNamespaceAndPath(namespace, path),
                    new Ours(key, file, entries(file)));
            }
        } catch (final IOException failed) {
            throw new UncheckedIOException(failed);
        }
    }

    /** The ids a tag file lists, in either of the two forms a value may take. */
    private static List<String> entries(final Path file) {
        try {
            final JsonElement json = JsonParser.parseString(Files.readString(file, StandardCharsets.UTF_8));
            final JsonArray values = json.getAsJsonObject().getAsJsonArray("values");
            final List<String> entries = new ArrayList<>();
            if (values == null) {
                return entries;
            }
            for (final JsonElement value : values) {
                if (value.isJsonPrimitive()) {
                    entries.add(value.getAsString());
                } else if (value.isJsonObject()) {
                    final JsonObject object = value.getAsJsonObject();
                    // {"id": ..., "required": false} says the author knows it may be absent.
                    if (object.has("required") && !object.get("required").getAsBoolean()) {
                        continue;
                    }
                    entries.add(object.get("id").getAsString());
                }
            }
            return entries;
        } catch (final IOException failed) {
            throw new UncheckedIOException(failed);
        }
    }

    /** How many members each tag of one registry ended up with, by tag id - the game's own read. */
    private static <T> Map<Identifier, Integer> members(
        final ResourceManager resources, final Registry<T> registry
    ) {
        @SuppressWarnings("unchecked")
        final TagLoader.ElementLookup<Holder<T>> lookup =
            (TagLoader.ElementLookup<Holder<T>>) TagLoader.ElementLookup.fromFrozenRegistry(registry);
        final Map<TagKey<T>, List<Holder<T>>> tags =
            TagLoader.loadTagsForRegistry(resources, registry.key(), lookup);
        final Map<Identifier, Integer> sizes = new LinkedHashMap<>();
        tags.forEach((key, members) -> sizes.put(key.location(), members.size()));
        return sizes;
    }

    @SuppressWarnings("unchecked")
    private static <T> ResourceKey<? extends Registry<T>> cast(final ResourceKey<? extends Registry<?>> key) {
        return (ResourceKey<? extends Registry<T>>) key;
    }
}
