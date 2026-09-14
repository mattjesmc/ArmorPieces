package com.mattjesmc.armorpieces.recipe;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.cloth.Cloth;
import com.mattjesmc.armorpieces.data.ShippedData;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.skin.ArmorSkin;
import com.mojang.serialization.JsonOps;
import java.io.IOException;
import java.util.stream.Stream;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.SmithingRecipeInput;
import net.minecraft.world.item.equipment.trim.TrimMaterial;

/**
 * The smithing table, without a game: the recipes this mod ships, the stacks a player would lay in
 * the three slots, and the content to build them from.
 *
 * <p>Everything the four recipes of this mod decide is decided in {@code matches} and
 * {@code assemble} over three {@link ItemStack}s - no world, no player, no menu - so the rules can
 * be asked here rather than in a game. {@link ShippedData} supplies the content half (the parts,
 * skins, cloths, fittings and trim materials this repository ships, read by the loader a server
 * uses) and the recipe files are read out of {@code src/main/resources} by name, so a test is
 * written against the recipe players actually get rather than one built in Java beside it.
 *
 * <p>Two things this fixture knows that a reader should not have to re-derive:
 *
 * <ul>
 *   <li><b>{@code matches} never touches the level.</b> Vanilla's {@code SmithingRecipe.matches}
 *       tests the three ingredients and nothing else, and no override in this mod reads it either,
 *       so {@link #NO_LEVEL} is what every call here passes. The day one of them does need a level,
 *       that is a {@link NullPointerException} in a test rather than a surprise on a server.</li>
 *   <li><b>A trim material has to come out of the load.</b> An item's default components are baked
 *       against vanilla's own lookup ({@link ShippedData#bakeItemComponents}), so the holder an iron
 *       ingot carries by default belongs to a different registry instance than the one a fitting's
 *       {@code materials} set was resolved against, and a set membership test between them is false
 *       where a game's would be true. {@link #providing} is the honest stack: the item as a server
 *       holds it, with the material of the registry the fittings came from.</li>
 * </ul>
 */
final class Bench {
    /**
     * What {@code matches} is given for a level. See the class note: nothing reads it, and a
     * {@link NullPointerException} here would be a finding rather than a flaw in the test.
     */
    static final net.minecraft.world.level.Level NO_LEVEL = null;

    private Bench() {
    }

    /** The mod's own data, with every item's components baked so a stack can be built at all. */
    static ShippedData.Loaded data() {
        final ShippedData.Loaded loaded = ShippedData.mod();
        // Binds the tags too, which an Ingredient reads as it decodes.
        ShippedData.bakeItemComponents(loaded);
        return loaded;
    }

    /**
     * A level that answers one question - {@code registryAccess()}, with the registries the content
     * came from - for the one rule in a recipe that reads the level: the server's
     * {@link com.mattjesmc.armorpieces.config.PartsSwitch}, which resolves a {@code #tag} through
     * it. Allocated, never constructed, the way {@code menu/Table} stands its level up; a test
     * that has switched nothing off keeps passing {@link #NO_LEVEL}.
     */
    static net.minecraft.world.level.Level level() {
        final ServerLevel level = allocate(ServerLevel.class);
        inject(level, "registryAccess", data().registries());
        return level;
    }

    /** An instance with every field null and no constructor run - the serialization trick. */
    private static <T> T allocate(final Class<T> type) {
        try {
            final Class<?> unsafeClass = Class.forName("sun.misc.Unsafe");
            final java.lang.reflect.Field held = unsafeClass.getDeclaredField("theUnsafe");
            held.setAccessible(true);
            final Object unsafe = held.get(null);
            return type.cast(unsafeClass.getMethod("allocateInstance", Class.class).invoke(unsafe, type));
        } catch (final ReflectiveOperationException failed) {
            throw new AssertionError("a " + type.getSimpleName() + " could not be allocated", failed);
        }
    }

    /** Sets one field, wherever in the hierarchy it is declared. Final instance fields included. */
    private static void inject(final Object target, final String name, final Object value) {
        for (Class<?> type = target.getClass(); type != null; type = type.getSuperclass()) {
            try {
                final java.lang.reflect.Field field = type.getDeclaredField(name);
                field.setAccessible(true);
                field.set(target, value);
                return;
            } catch (final NoSuchFieldException notHere) {
                // Declared further up, or nowhere.
            } catch (final IllegalAccessException refused) {
                throw new AssertionError("could not set " + name, refused);
            }
        }
        throw new AssertionError("no field called " + name + " on " + target.getClass().getName()
            + " - vanilla has renamed what this fixture fills in");
    }

    // ---- the recipes -------------------------------------------------------------------------

    /**
     * One recipe this mod ships, by file name - {@code recipe("apply_crest", ...)}.
     *
     * <p>Read from the tree rather than constructed, because the ingredients are the half of a
     * recipe a test cannot invent: {@code "base": "#minecraft:head_armor"} is what decides that a
     * crest is refused on boots, and a hand-built recipe would assert about a file nobody has.
     */
    static <T extends Recipe<?>> T recipe(final String name, final Class<T> type) {
        final ShippedData.Loaded loaded = data();
        // The mod's own recipes, or a built-in pack's: the split moved every template recipe into
        // the pack that owns its piece, and a test about a visor's template should not know which.
        final Path file = ShippedData.jarRoots().stream()
            .flatMap(root -> {
                final Path data = root.resolve("data");
                try (Stream<Path> namespaces = Files.isDirectory(data) ? Files.list(data) : Stream.<Path>empty()) {
                    return namespaces.map(ns -> ns.resolve(Registries.elementsDirPath(Registries.RECIPE))
                        .resolve(name + ".json")).toList().stream();
                } catch (final IOException failed) {
                    throw new UncheckedIOException(failed);
                }
            })
            .filter(Files::isRegularFile)
            .findFirst()
            .orElse(null);
        assertTrue(file != null, () -> "this jar no longer ships a recipe called " + name);
        final JsonElement json;
        try {
            json = JsonParser.parseString(Files.readString(file, StandardCharsets.UTF_8));
        } catch (final IOException failed) {
            throw new UncheckedIOException(failed);
        }
        final Recipe<?> parsed = Recipe.CODEC
            .parse(loaded.full().createSerializationContext(JsonOps.INSTANCE), json)
            .getOrThrow(message -> new AssertionError(file + ": " + message));
        assertTrue(type.isInstance(parsed),
            () -> name + " is a " + parsed.getClass().getSimpleName() + ", not a " + type.getSimpleName());
        return type.cast(parsed);
    }

    /** The three slots, in the table's own order. */
    static SmithingRecipeInput input(
        final ItemStack template, final ItemStack base, final ItemStack addition
    ) {
        return new SmithingRecipeInput(template, base, addition);
    }

    // ---- the content ------------------------------------------------------------------------

    /**
     * A part that fits {@code anchor} and declares exactly {@code fittings}, in that order.
     *
     * <p>Found rather than named, because a part id is the one thing in this repository that has
     * actually moved - the pack split moved fifty of them - while "a collar part whose guard is
     * offered an item before its inlay" is a shape the content is meant to keep. The order matters:
     * it is the routing rule {@link SmithingFittingRecipe} runs.
     */
    static Holder<ArmorDecoration> part(final DecorationAnchor anchor, final String... fittings) {
        final List<Holder<Fitting>> wanted = java.util.Arrays.stream(fittings)
            .map(Bench::fitting)
            .toList();
        return parts()
            .filter(part -> part.value().fits(anchor))
            .filter(part -> part.value().fittings().equals(wanted))
            .findFirst()
            .orElseThrow(() -> new AssertionError("no shipped part fits " + anchor.getSerializedName()
                + " with fittings " + List.of(fittings) + "; the content this test is about is gone"));
    }

    /** Every part the mod ships, in id order, so a test always picks the same one. */
    private static java.util.stream.Stream<Holder<ArmorDecoration>> parts() {
        return data().registry(ArmorPiecesRegistries.ARMOR_DECORATION).listElements()
            .sorted(java.util.Comparator.comparing(part -> part.key().identifier().toString()))
            .<Holder<ArmorDecoration>>map(part -> part);
    }

    static Holder<Fitting> fitting(final String path) {
        return element(ArmorPiecesRegistries.FITTING, path);
    }

    static Holder<ArmorSkin> skin(final String path) {
        return element(ArmorPiecesRegistries.ARMOR_SKIN, path);
    }

    static Holder<Cloth> cloth(final String path) {
        return element(ArmorPiecesRegistries.CLOTH, path);
    }

    /**
     * A trim material out of the load - the registry the fittings' own material sets were resolved
     * against. Named with a bare path for vanilla's ({@code "iron"}), which is where they all live.
     */
    static Holder<TrimMaterial> material(final String id) {
        final Identifier named = Identifier.parse(id);
        final Registry<TrimMaterial> registry = data().registry(Registries.TRIM_MATERIAL);
        return registry.get(named)
            .<Holder<TrimMaterial>>map(holder -> holder)
            .orElseThrow(() -> new AssertionError("no trim material " + named + " was loaded"));
    }

    private static <T> Holder<T> element(final ResourceKey<? extends Registry<T>> key, final String path) {
        final Identifier id = ShippedData.shipped(key, path);
        final Registry<T> registry = data().registry(key);
        return registry.get(id)
            .<Holder<T>>map(holder -> holder)
            .orElseThrow(() -> new AssertionError("this mod no longer ships " + id));
    }

    // ---- the stacks -------------------------------------------------------------------------

    /** One of something, with the default components a server would have baked onto it. */
    static ItemStack stack(final Item item) {
        data();
        return new ItemStack(item);
    }

    /**
     * {@code item}, providing {@code material} - the addition slot of every recipe that takes a
     * material, and the item a material fitting is offered.
     *
     * <p>The component is set rather than trusted: see the class note. The item is still the real
     * one, because the ingredient a recipe file names is an item tag and an iron ingot has to be in
     * {@code #minecraft:trim_materials} for the table to light up at all.
     */
    static ItemStack providing(final Item item, final String material) {
        final ItemStack stack = stack(item);
        stack.set(DataComponents.PROVIDES_TRIM_MATERIAL, material(material));
        return stack;
    }

    /** What a stack holds under {@code armorpieces:decorations}, asserted to be there. */
    static com.mattjesmc.armorpieces.decoration.ArmorDecorations decorations(final ItemStack stack) {
        final var value = stack.get(com.mattjesmc.armorpieces.registry.ModDataComponents.DECORATIONS);
        assertNotNull(value, () -> stack + " carries no decorations");
        return value;
    }

    /** The entry in one socket of {@code stack}, asserted to be there. */
    static com.mattjesmc.armorpieces.decoration.DecorationEntry entry(
        final ItemStack stack, final DecorationAnchor anchor
    ) {
        final var entry = decorations(stack).get(anchor);
        assertNotNull(entry, () -> "nothing is in the " + anchor.getSerializedName() + " socket of " + stack);
        return entry;
    }

    /** The empty third slot - the shape of a clearing recipe's input. */
    static ItemStack nothing() {
        return ItemStack.EMPTY;
    }

    /** A banner of {@code colour} carrying {@code layers}, as a player would bring one to the table. */
    static ItemStack banner(
        final net.minecraft.world.item.DyeColor colour,
        final Optional<net.minecraft.world.level.block.entity.BannerPatternLayers> layers
    ) {
        final ItemStack stack = stack(Items.BANNER.pick(colour));
        layers.ifPresent(value -> stack.set(DataComponents.BANNER_PATTERNS, value));
        return stack;
    }
}
