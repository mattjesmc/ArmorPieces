package com.mattjesmc.armorpieces.data;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.recipe.SmithingClothRecipe;
import com.mattjesmc.armorpieces.recipe.SmithingDecorationRecipe;
import com.mattjesmc.armorpieces.recipe.SmithingFittingRecipe;
import com.mattjesmc.armorpieces.recipe.SmithingSkinRecipe;
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
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.RegistryOps;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.crafting.Recipe;
import org.junit.jupiter.api.Test;

/**
 * Every recipe this repository ships, read through the game's own recipe codec.
 *
 * <p>A recipe is the only way most of this mod is reached in survival, and it is the file with the
 * most ways to be quietly wrong: the type dispatches through a serializer this mod registers, the
 * ingredients are item tags, and the RESULT carries a component naming a part - so a recipe can
 * name a piece that no longer exists and still load, handing out a template of nothing. None of
 * that is visible until a player stands at the table.
 *
 * <p>Four of the five serializers this mod adds are exercised by simply decoding what ships
 * (twelve decoration recipes, two skin, two cloth, two fitting), which is why there is no
 * hand-written case for them here: the shipped files ARE the case, and unlike a hand-written one
 * they cannot drift from what players have.
 */
class ShippedRecipesTest {
    /** The mod's components that name a piece, and the registry each names it in. */
    private static Map<String, ResourceKey<? extends Registry<?>>> pieceComponents() {
        return Map.of(
            "armorpieces:decoration", ArmorPiecesRegistries.ARMOR_DECORATION,
            "armorpieces:skin", ArmorPiecesRegistries.ARMOR_SKIN,
            "armorpieces:cloth", ArmorPiecesRegistries.CLOTH);
    }

    @Test
    void everyRecipeDecodes() {
        final ShippedData.Loaded loaded = ShippedData.everything();
        ShippedData.bindTags(loaded);  // an Ingredient names an item tag and binds it as it reads
        final RegistryOps<JsonElement> ops =
            loaded.full().createSerializationContext(com.mojang.serialization.JsonOps.INSTANCE);
        final Map<Identifier, Path> files = files(loaded);
        assertFalse(files.isEmpty(), "this repository ships recipes; none were found");

        final List<String> broken = new ArrayList<>();
        files.forEach((id, file) -> {
            try {
                final JsonElement json = read(file);
                final Recipe<?> recipe = Recipe.CODEC.parse(ops, json)
                    .getOrThrow(message -> new AssertionError(message));
                // And back out again: a serializer that drops a field on encode is the trap the
                // config codecs were caught by, and a recipe has no equals() to catch it with.
                final JsonElement again = Recipe.CODEC.encodeStart(ops, recipe)
                    .getOrThrow(message -> new AssertionError("cannot be written back: " + message));
                final Recipe<?> reread = Recipe.CODEC.parse(ops, again)
                    .getOrThrow(message -> new AssertionError("what it wrote is unreadable: " + message));
                final JsonElement third = Recipe.CODEC.encodeStart(ops, reread)
                    .getOrThrow(message -> new AssertionError(message));
                if (!again.equals(third)) {
                    broken.add(id + ": writes differently every time\n    " + again + "\n    " + third);
                }
            } catch (final AssertionError | RuntimeException failed) {
                broken.add(id + " (" + file + "): " + failed.getMessage());
            }
        });
        assertTrue(broken.isEmpty(), () -> "recipes the game would refuse:\n  "
            + String.join("\n  ", broken));
    }

    /** The four smithing types this mod adds are all actually used by what ships. */
    @Test
    void everySmithingSerializerIsExercisedByAShippedRecipe() {
        final ShippedData.Loaded loaded = ShippedData.everything();
        ShippedData.bindTags(loaded);  // an Ingredient names an item tag and binds it as it reads
        final RegistryOps<JsonElement> ops =
            loaded.full().createSerializationContext(com.mojang.serialization.JsonOps.INSTANCE);
        final Map<Class<?>, Integer> counts = new LinkedHashMap<>();
        files(loaded).values().forEach(file -> {
            final Recipe<?> recipe = Recipe.CODEC.parse(ops, read(file))
                .getOrThrow(message -> new AssertionError(file + ": " + message));
            counts.merge(recipe.getClass(), 1, Integer::sum);
        });
        for (final Class<?> type : List.of(SmithingDecorationRecipe.class, SmithingSkinRecipe.class,
                                           SmithingClothRecipe.class, SmithingFittingRecipe.class)) {
            assertTrue(counts.getOrDefault(type, 0) > 0,
                () -> "no shipped recipe uses " + type.getSimpleName() + ", so nothing here tests it;"
                    + " what shipped was " + counts);
        }
    }

    /**
     * A template recipe hands out a stack whose component names a piece. If that id has moved - the
     * split moved fifty of them - the recipe still loads and the table still works, and what the
     * player takes away is a template bound to nothing.
     *
     * <p>Read out of the raw JSON on purpose: decoding it would go through
     * {@link com.mattjesmc.armorpieces.identity.Tolerant}, whose whole job is to make exactly this
     * survive. Tolerance is right for a SAVE and wrong for a file this repository ships.
     */
    @Test
    void everyRecipeResultNamesAPieceThatExists() {
        final ShippedData.Loaded loaded = ShippedData.everything();
        final List<String> missing = new ArrayList<>();
        files(loaded).forEach((id, file) -> {
            final JsonObject result = read(file).getAsJsonObject().getAsJsonObject("result");
            if (result == null || !result.has("components")) {
                return;
            }
            final JsonObject components = result.getAsJsonObject("components");
            pieceComponents().forEach((component, key) -> {
                if (!components.has(component)) {
                    return;
                }
                // Two shapes, and both ship: a skin component is the bare id, a cloth component is
                // an object holding it. Either way what is wanted is the string.
                final JsonElement value = components.get(component);
                final List<JsonElement> ids = new ArrayList<>();
                if (value.isJsonPrimitive()) {
                    ids.add(value);
                } else if (value.isJsonObject()) {
                    value.getAsJsonObject().entrySet().stream()
                        .map(Map.Entry::getValue)
                        .filter(JsonElement::isJsonPrimitive)
                        .forEach(ids::add);
                }
                ids.forEach(named -> {
                    final Identifier piece = Identifier.tryParse(named.getAsString());
                    if (piece == null || !defines(loaded, key, piece)) {
                        missing.add(id + " hands out " + component + " " + named
                            + ", which nothing defines");
                    }
                });
            });
        });
        assertTrue(missing.isEmpty(), () -> "recipes that hand out nothing:\n  "
            + String.join("\n  ", missing));
    }

    @SuppressWarnings("unchecked")
    private static boolean defines(
        final ShippedData.Loaded loaded,
        final ResourceKey<? extends Registry<?>> key,
        final Identifier id
    ) {
        return loaded.registry((ResourceKey<? extends Registry<Object>>) key).containsKey(id);
    }

    // ---- the tree --------------------------------------------------------------------------

    /** Every {@code data/<ns>/recipe/**}{@code .json} under this repository's own packs. */
    private static Map<Identifier, Path> files(final ShippedData.Loaded loaded) {
        final Map<Identifier, Path> found = new LinkedHashMap<>();
        for (final Path root : loaded.roots()) {
            final Path data = root.resolve("data");
            if (!Files.isDirectory(data)) {
                continue;
            }
            try (Stream<Path> namespaces = Files.list(data)) {
                for (final Path namespace : namespaces.toList()) {
                    final Path directory = namespace.resolve(Registries.elementsDirPath(Registries.RECIPE));
                    if (!Files.isDirectory(directory)) {
                        continue;
                    }
                    try (Stream<Path> walk = Files.walk(directory)) {
                        walk.filter(path -> path.toString().endsWith(".json")).forEach(path ->
                            found.put(Identifier.fromNamespaceAndPath(
                                namespace.getFileName().toString(),
                                directory.relativize(path).toString()
                                    .replace('\\', '/').replaceAll("\\.json$", "")), path));
                    }
                }
            } catch (final IOException failed) {
                throw new UncheckedIOException(failed);
            }
        }
        return found;
    }

    private static JsonElement read(final Path file) {
        try {
            return JsonParser.parseString(Files.readString(file, StandardCharsets.UTF_8));
        } catch (final IOException failed) {
            throw new UncheckedIOException(failed);
        }
    }
}
