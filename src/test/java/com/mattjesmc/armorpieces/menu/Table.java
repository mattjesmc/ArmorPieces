package com.mattjesmc.armorpieces.menu;

import static org.junit.jupiter.api.Assertions.assertFalse;

import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.GameBootstrap;
import com.mattjesmc.armorpieces.cloth.Cloth;
import com.mattjesmc.armorpieces.cloth.ClothValue;
import com.mattjesmc.armorpieces.data.ShippedData;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.decoration.fitting.FittingValue;
import com.mattjesmc.armorpieces.decoration.fitting.builtin.MaterialFitting;
import com.mattjesmc.armorpieces.identity.Tolerant;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.skin.ArmorSkin;
import com.mattjesmc.armorpieces.skin.ArmorSkinValue;
import com.mojang.serialization.JsonOps;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.Registries;
import net.minecraft.core.HolderLookup;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.FileToIdConverter;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.RegistryOps;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.profiling.InactiveProfiler;
import net.minecraft.world.entity.EntityEquipment;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.flag.FeatureFlags;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.RecipeManager;
import net.minecraft.world.item.crafting.RecipeMap;
import net.minecraft.world.item.equipment.Equippable;
import net.minecraft.world.item.equipment.trim.ArmorTrim;
import net.minecraft.world.item.equipment.trim.TrimMaterial;
import net.minecraft.world.item.equipment.trim.TrimPattern;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.entity.BannerPatternLayers;

/**
 * The advanced smithing table, standing in a level that answers exactly one question.
 *
 * <p>Everything the table decides - which piece is being worked on, which row of it, what Remove
 * takes off, where a fitting lands, what a shift-click does - is decided over the stacks in its own
 * slots. None of it is a game. But a menu is not a rule object either: it is built out of an
 * {@link Inventory}, which belongs to a {@link Player}, who stands in a {@link net.minecraft.world.level.Level},
 * and the constructor reads that level for the two ingredient tests its template and material slots
 * use. So the fixture supplies the smallest thing that is honestly those: a level, a player and an
 * inventory ALLOCATED WITHOUT RUNNING A CONSTRUCTOR - the trick
 * {@link com.mattjesmc.armorpieces.decoration.effect.Wearer} uses for its zombie, and the one a save
 * file uses when it reads an entity back - with only the fields the menu touches filled in.
 *
 * <p>Three of them, and that is the fixture's whole claim: the level's recipe manager, the player's
 * level, and the player's inventory. Anything a future change reads that is not one of those is a
 * {@link NullPointerException} in a test rather than a silent pass.
 *
 * <h2>The recipes are real, and there are more of them than this mod ships</h2>
 *
 * <p>{@link #recipes()} reads EVERY recipe out of the same stacked datapack the registries came from
 * - vanilla's built-in pack and this mod's - and hands them to a real {@link RecipeManager}. That is
 * what makes Apply worth asking about at all: the menu's own note says the table runs "this mod's
 * socket and fitting recipes, but also a vanilla trim or a netherite upgrade", and a fixture holding
 * only this mod's sixty-three could not tell the difference. It is also what the two slot tests
 * stand on, since a {@link net.minecraft.world.item.crafting.RecipePropertySet} is built out of the
 * loaded recipes and nothing else.
 *
 * <h2>What is still out of reach</h2>
 *
 * <p>The client half. The menu asks {@code level instanceof ServerLevel} in three places and takes
 * the other branch on a client - Apply reports what the server last said rather than looking it up -
 * and there is no honest way to stand a {@code ClientLevel} here. That branch stays in tier 3, where
 * a real client opens the screen.
 */
final class Table {
    private static List<RecipeHolder<?>> shipped;
    private static RecipeManager recipes;

    private final AdvancedSmithingMenu menu;
    private final Customer player;
    private final Inventory inventory;

    private Table(final RecipeManager known) {
        final Server level = allocate(Server.class);
        inject(level, "recipes", known);
        this.player = allocate(Customer.class);
        inject(this.player, "level", level);
        this.inventory = new Inventory(this.player, new EntityEquipment());
        inject(this.player, "inventory", this.inventory);
        this.menu = new AdvancedSmithingMenu(1, this.inventory);
    }

    /** An empty table, open, with nothing selected, in a world holding the recipes that ship. */
    static Table opened() {
        content();
        return new Table(recipes());
    }

    /**
     * The same, in a world that also knows {@code extra} - a recipe nobody ships.
     *
     * <p>For the rules that are about what the table does with a recipe rather than about the
     * recipes themselves: everything shipped assembles a piece of armor out of a piece of armor, so
     * the guard against a result that could not go back in the slot it came from has nothing here to
     * be shown by.
     */
    static Table offering(final RecipeHolder<?> extra) {
        final ShippedData.Loaded loaded = content();
        final List<RecipeHolder<?>> all = new ArrayList<>(shipped(loaded));
        all.add(extra);
        return new Table(new Recipes(loaded.full(), all));
    }

    // ---- driving it --------------------------------------------------------------------------

    AdvancedSmithingMenu menu() {
        return this.menu;
    }

    Player player() {
        return this.player;
    }

    Inventory inventory() {
        return this.inventory;
    }

    /**
     * Lays a piece in the display slot its own armor slot belongs to, through the slot rather than
     * into the container, so the menu hears about it exactly as it would from a click.
     */
    Table laying(final ItemStack piece) {
        return this.laying(displayIndexOf(piece), piece);
    }

    /** Lays anything in a display slot by index - including something that does not belong there. */
    Table laying(final int index, final ItemStack piece) {
        this.menu.getSlot(AdvancedSmithingMenu.DISPLAY_SLOT_START + index).set(piece);
        return this;
    }

    /** Takes whatever is in a display slot back out. */
    Table taking(final int index) {
        return this.laying(index, ItemStack.EMPTY);
    }

    Table template(final ItemStack stack) {
        this.menu.getSlot(AdvancedSmithingMenu.TEMPLATE_SLOT).set(stack);
        return this;
    }

    Table material(final ItemStack stack) {
        this.menu.getSlot(AdvancedSmithingMenu.MATERIAL_SLOT).set(stack);
        return this;
    }

    /** One button, by the id the screen would send. */
    boolean click(final int button) {
        return this.menu.clickMenuButton(this.player, button);
    }

    boolean select(final int index) {
        return this.click(AdvancedSmithingMenu.BUTTON_SELECT + index);
    }

    /** Works on one row of the selected piece, part and all. */
    boolean row(final int row) {
        return this.click(AdvancedSmithingMenu.BUTTON_SELECT_ROW + row);
    }

    /** Works on one place of one row - a fitting, or the skin or cloth of the piece's own row. */
    boolean place(final int row, final int fitting) {
        return this.click(AdvancedSmithingMenu.BUTTON_SELECT_FITTING
            + row * AdvancedSmithingMenu.MAX_FITTINGS + fitting);
    }

    boolean apply() {
        return this.click(AdvancedSmithingMenu.BUTTON_APPLY);
    }

    boolean remove() {
        return this.click(AdvancedSmithingMenu.BUTTON_REMOVE);
    }

    // ---- what is in it -----------------------------------------------------------------------

    ItemStack display(final int index) {
        return this.menu.displayStack(index);
    }

    ItemStack selected() {
        return this.menu.selectedStack();
    }

    ItemStack inTemplateSlot() {
        return this.menu.getSlot(AdvancedSmithingMenu.TEMPLATE_SLOT).getItem();
    }

    ItemStack inMaterialSlot() {
        return this.menu.getSlot(AdvancedSmithingMenu.MATERIAL_SLOT).getItem();
    }

    /** Where a piece belongs: the display slot for the armor slot it equips in. */
    static int displayIndexOf(final ItemStack piece) {
        final Equippable equippable = piece.get(DataComponents.EQUIPPABLE);
        final int index = equippable == null
            ? -1
            : AdvancedSmithingMenu.DISPLAY_SLOTS.indexOf(equippable.slot());
        assertFalse(index < 0, () -> piece + " does not equip in any of the table's display slots");
        return index;
    }

    // ---- the stacks a player brings ----------------------------------------------------------

    /** Plain iron armor for a slot, with the default components a server would have baked on. */
    static ItemStack armor(final EquipmentSlot slot) {
        content();
        return new ItemStack(switch (slot) {
            case HEAD -> Items.IRON_HELMET;
            case CHEST -> Items.IRON_CHESTPLATE;
            case LEGS -> Items.IRON_LEGGINGS;
            case FEET -> Items.IRON_BOOTS;
            default -> throw new IllegalArgumentException("no armor goes in " + slot);
        });
    }

    /** One of something, with its default components. */
    static ItemStack stack(final Item item) {
        content();
        return new ItemStack(item);
    }

    /**
     * {@code item}, providing {@code material} - the addition slot of every recipe that takes one.
     *
     * <p>Set rather than trusted, for the reason {@code recipe/Bench} states: an item's default
     * components are baked against vanilla's own lookup, so the holder an iron ingot carries belongs
     * to a different registry instance than the one a fitting's material set was resolved against,
     * and a set membership between them is false where a game's would be true.
     */
    static ItemStack providing(final Item item, final String material) {
        final ItemStack stack = stack(item);
        stack.set(DataComponents.PROVIDES_TRIM_MATERIAL, material(material));
        return stack;
    }

    /** A piece of armor wearing one part in one socket, in iron. */
    static ItemStack wearing(final DecorationAnchor anchor, final Holder<ArmorDecoration> part) {
        return wearing(armor(anchor.slot()), anchor, part);
    }

    /** {@code piece}, with one more socket filled - the shape of a piece that has been worked on. */
    static ItemStack wearing(
        final ItemStack piece, final DecorationAnchor anchor, final Holder<ArmorDecoration> part
    ) {
        final Map<DecorationAnchor, DecorationEntry> entries =
            new LinkedHashMap<>(piece.getOrDefault(ModDataComponents.DECORATIONS, ArmorDecorations.EMPTY).entries());
        entries.put(anchor, new DecorationEntry(material("minecraft:iron"), part));
        final ItemStack decorated = piece.copy();
        decorated.set(ModDataComponents.DECORATIONS, new ArmorDecorations(entries));
        return decorated;
    }

    /**
     * {@code piece} with one fitting of one of its parts filled - what the second smithing step
     * leaves behind, written straight into the component because how it got there is not the
     * question here.
     */
    static ItemStack setting(
        final ItemStack piece,
        final DecorationAnchor anchor,
        final Holder<Fitting> fitting,
        final FittingValue value
    ) {
        final ArmorDecorations worn = piece.getOrDefault(ModDataComponents.DECORATIONS, ArmorDecorations.EMPTY);
        final DecorationEntry entry = worn.get(anchor);
        if (entry == null) {
            throw new AssertionError("nothing is in the " + anchor.getSerializedName() + " socket to fit");
        }
        final ItemStack fitted = piece.copy();
        fitted.set(ModDataComponents.DECORATIONS, worn.with(anchor, entry.withFitting(fitting, value)));
        return fitted;
    }

    /** What a guard or a gemstone holds: a trim material. */
    static FittingValue metal(final String material) {
        return new MaterialFitting.Value(material(material));
    }

    /** The piece with a trim on it - any trim; nothing here asks which. */
    static ItemStack trimmed(final ItemStack piece) {
        final ItemStack copy = piece.copy();
        copy.set(DataComponents.TRIM, new ArmorTrim(material("minecraft:iron"), Holder.direct(
            new TrimPattern(Identifier.withDefaultNamespace("coast"), Component.literal("Coast"), false))));
        return copy;
    }

    /** The piece wearing one of the mod's own skins. */
    static ItemStack skinned(final ItemStack piece, final String skin) {
        final ItemStack copy = piece.copy();
        copy.set(ModDataComponents.SKIN, Tolerant.of(new ArmorSkinValue(skin(skin))));
        return copy;
    }

    /** The piece wearing one of the mod's own garments, in a plain banner's colour. */
    static ItemStack clothed(final ItemStack piece, final String cloth) {
        final ItemStack copy = piece.copy();
        copy.set(ModDataComponents.CLOTH, Tolerant.of(
            new ClothValue(cloth(cloth), DyeColor.RED, BannerPatternLayers.EMPTY)));
        return copy;
    }

    // ---- the content -------------------------------------------------------------------------

    /**
     * A part that fits {@code anchor} and declares exactly {@code fittings}, in that order.
     *
     * <p>Found rather than named, for {@code recipe/Bench}'s reason: a part id is the one thing in
     * this repository that has actually moved, while "a collar part whose guard comes before its
     * inlay" is a shape the content is meant to keep.
     */
    static Holder<ArmorDecoration> part(final DecorationAnchor anchor, final String... fittings) {
        final List<Holder<Fitting>> wanted = Arrays.stream(fittings).map(Table::fitting).toList();
        return loaded().registry(ArmorPiecesRegistries.ARMOR_DECORATION).listElements()
            .sorted(Comparator.comparing(part -> part.key().identifier().toString()))
            .<Holder<ArmorDecoration>>map(part -> part)
            .filter(part -> part.value().fits(anchor))
            .filter(part -> part.value().fittings().equals(wanted))
            .findFirst()
            .orElseThrow(() -> new AssertionError("no shipped part fits " + anchor.getSerializedName()
                + " with fittings " + List.of(fittings) + "; the content this test is about is gone"));
    }

    /** A part of this fixture's own making, with as many fittings as it is given. */
    static Holder<ArmorDecoration> partWith(final DecorationAnchor anchor, final String... fittings) {
        return Holder.direct(new ArmorDecoration(
            Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "test_part"),
            Component.literal("Test Part"),
            java.util.Set.of(anchor),
            Arrays.stream(fittings).map(Table::fitting).toList(),
            List.of(),
            List.of()));
    }

    static Holder<Fitting> fitting(final String path) {
        return element(ArmorPiecesRegistries.FITTING, Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, path));
    }

    static Holder<ArmorSkin> skin(final String path) {
        return element(ArmorPiecesRegistries.ARMOR_SKIN, Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, path));
    }

    static Holder<Cloth> cloth(final String path) {
        return element(ArmorPiecesRegistries.CLOTH, Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, path));
    }

    static Holder<TrimMaterial> material(final String id) {
        return element(Registries.TRIM_MATERIAL, Identifier.parse(id));
    }

    private static <T> Holder<T> element(final ResourceKey<? extends Registry<T>> key, final Identifier id) {
        final Registry<T> registry = loaded().registry(key);
        return registry.get(id)
            .<Holder<T>>map(holder -> holder)
            .orElseThrow(() -> new AssertionError("nothing this repository ships is called " + id));
    }

    private static ShippedData.Loaded loaded() {
        return ShippedData.mod();
    }

    /**
     * The mod in a registry, its items in the game, and the tags bound.
     *
     * <p>All three are needed before a single stack can be built: the menu is a registered menu
     * type, a display slot reads an item's {@code equippable} component, and an ingredient names an
     * item tag and binds it as it reads.
     */
    private static synchronized ShippedData.Loaded content() {
        GameBootstrap.content();
        final ShippedData.Loaded loaded = loaded();
        ShippedData.bakeItemComponents(loaded);
        return loaded;
    }

    // ---- the recipes -------------------------------------------------------------------------

    /**
     * Every recipe in the stacked datapack, in one manager, once per JVM.
     *
     * <p>Vanilla's own are in it as well as this mod's, because the table's rule is that it runs
     * whatever the recipe manager matched: a netherite upgrade and a vanilla trim have to be
     * askable here or the claim is untested.
     */
    private static synchronized RecipeManager recipes() {
        if (recipes == null) {
            final ShippedData.Loaded loaded = content();
            recipes = new Recipes(loaded.full(), shipped(loaded));
        }
        return recipes;
    }

    /** Every recipe in the datapack, parsed once and kept, since two managers may want them. */
    private static synchronized List<RecipeHolder<?>> shipped(final ShippedData.Loaded loaded) {
        if (shipped == null) {
            shipped = read(loaded);
        }
        return shipped;
    }

    private static List<RecipeHolder<?>> read(final ShippedData.Loaded loaded) {
        final RegistryOps<JsonElement> ops = loaded.full().createSerializationContext(JsonOps.INSTANCE);
        final FileToIdConverter files = FileToIdConverter.registry(Registries.RECIPE);
        final List<RecipeHolder<?>> found = new ArrayList<>();
        files.listMatchingResources(loaded.data()).forEach((path, resource) -> {
            final Identifier id = files.fileToId(path);
            try (BufferedReader reader = resource.openAsReader()) {
                final Recipe<?> recipe = Recipe.CODEC.parse(ops, JsonParser.parseReader(reader))
                    .getOrThrow(message -> new AssertionError(id + ": " + message));
                found.add(new RecipeHolder<>(ResourceKey.create(Registries.RECIPE, id), recipe));
            } catch (final IOException failed) {
                throw new UncheckedIOException(failed);
            }
        });
        assertFalse(found.isEmpty(), "no recipes were found in the datapack the registries came from");
        return found;
    }

    /**
     * A recipe manager holding a fixed set of recipes.
     *
     * <p>{@code apply} is what a datapack reload calls with the recipes it read, and
     * {@code finalizeRecipeLoading} is what builds the property sets the two input slots test items
     * against - the pair a server runs, in the order it runs them.
     */
    private static final class Recipes extends RecipeManager {
        Recipes(final HolderLookup.Provider registries, final List<RecipeHolder<?>> loaded) {
            super(registries);
            this.apply(RecipeMap.create(loaded), null, InactiveProfiler.INSTANCE);
            this.finalizeRecipeLoading(FeatureFlags.DEFAULT_FLAGS);
        }
    }

    // ---- a level and a player that were never constructed --------------------------------------

    /**
     * A server level that exists to answer one question: what the recipes are.
     *
     * <p>Never constructed - see the class note - so the super call below is there to compile and
     * nothing else. {@code isClientSide} is false because a field nobody set is false, which is the
     * honest reading of "this is the server's copy of the menu".
     */
    private static final class Server extends ServerLevel {
        private RecipeManager recipes;

        private Server() {
            super(null, null, null, null, null, null, false, 0L, List.of(), false);
            throw new AssertionError("the fixture's level is allocated, never constructed");
        }

        @Override
        public RecipeManager recipeAccess() {
            return this.recipes;
        }
    }

    /** Somebody standing at the table. Never constructed either; they own a level and a bag. */
    private static final class Customer extends Player {
        private Customer() {
            super(null, null);
            throw new AssertionError("the fixture's player is allocated, never constructed");
        }

        @Override
        public GameType gameMode() {
            return GameType.SURVIVAL;
        }
    }

    /** An instance with every field null and no constructor run - the serialization trick. */
    private static <T> T allocate(final Class<T> type) {
        try {
            final Class<?> unsafeClass = Class.forName("sun.misc.Unsafe");
            final Field held = unsafeClass.getDeclaredField("theUnsafe");
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
                final Field field = type.getDeclaredField(name);
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
}
