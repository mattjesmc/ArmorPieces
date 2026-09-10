package com.mattjesmc.armorpieces.data;

import com.mattjesmc.armorpieces.GameBootstrap;
import com.mattjesmc.armorpieces.cloth.Cloth;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.loot.LootGroup;
import com.mattjesmc.armorpieces.skin.ArmorSkin;
import com.mojang.serialization.Codec;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Stream;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.MappedRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.RegistryDataLoader;
import net.minecraft.resources.RegistryValidator;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.packs.PackLocationInfo;
import net.minecraft.server.packs.PackResources;
import net.minecraft.server.packs.PackType;
import net.minecraft.server.packs.PathPackResources;
import net.minecraft.server.packs.repository.PackSource;
import net.minecraft.server.packs.repository.ServerPacksSource;
import net.minecraft.server.packs.resources.MultiPackResourceManager;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.tags.TagLoader;

/**
 * Every registry file this repository ships, read by the game's own loader.
 *
 * <p>The tests before this one build a world by hand - three parts in a {@link net.minecraft.core.MappedRegistry}
 * - which is the right shape for a question about the codec and the wrong one for a question about
 * the CONTENT. Sixty-six parts, nine skins, two cloths, four fittings and three loot groups ship in
 * this jar, and another eighty across the packs beside it; none of them was ever decoded outside a
 * running game. So this fixture points {@link RegistryDataLoader} - the same call a dedicated server
 * makes when it loads a datapack - at {@code src/main/resources} and at {@code packs/*}{@code /datapack},
 * and hands the result to whoever wants to ask a question of it.
 *
 * <p>Three layers have to be there first and each fails differently. {@link GameBootstrap#once()} is
 * the vanilla one; {@link GameBootstrap#types()} registers the effect and fitting TYPES, without
 * which a part naming {@code armorpieces:glide} is an unknown dispatch key rather than an effect;
 * and the parent lookups below are what a codec reaching outside these five registries resolves
 * against - {@code #armorpieces:gemstones} is a tag of vanilla's TRIM_MATERIAL, which is itself a
 * datapack registry and so is absent from {@link BuiltInRegistries}. The answer is vanilla's own
 * built-in datapack ({@link ServerPacksSource#createVanillaPackSource()}), stacked underneath this
 * repository's packs and loaded in the same pass.
 *
 * <p>Still not a game: no world, no server, no client, no loot table, no tag file resolved. A tag
 * here is a {@link net.minecraft.core.HolderSet.Named} nobody has filled, which is exactly what a
 * tag is before {@code /reload} - see {@link com.mattjesmc.armorpieces.loot.MemberSet}. Anything
 * needing members belongs in the gate's tier 2.
 */
public final class ShippedData {
    /** Gradle runs a test with the project directory as its working directory. */
    public static final Path ROOT = Path.of("").toAbsolutePath();

    /** The mod's own datapack, as it sits in the jar. */
    public static final Path MOD = ROOT.resolve("src").resolve("main").resolve("resources");

    private static final Path PACKS = ROOT.resolve("packs");

    /**
     * The vanilla datapack registries that have to be loaded in the same pass.
     *
     * <p>{@link Registries#TRIM_MATERIAL} because a shipped file of ours points at it - a material
     * fitting holds a {@code HolderSet} of them. {@link Registries#DAMAGE_TYPE} because the ITEMS do:
     * {@link #bakeItemComponents} runs vanilla's own initializers, and {@code Item.Properties
     * .fireResistant} asks for {@code #minecraft:is_fire} by name, which is a tag of a registry that
     * has to exist before an item can have a default component at all.
     *
     * <p>{@link Registries#TRIM_PATTERN} because a VANILLA file points at it: every
     * {@code minecraft:*_armor_trim_smithing_template_smithing_trim} recipe in the built-in pack
     * names a pattern, and {@code menu/Table} reads the whole stacked pack's recipes into a real
     * recipe manager. A load without it refuses those recipes with "Registry does not exist".
     *
     * <p>{@link Registries#BANNER_PATTERN} because a garment's design is banner layers, and a layer
     * holds a pattern by reference: {@code ClothBakeTest} asks what two different designs are filed
     * under, and a direct holder has no registered name to be filed by.
     */
    private static final Set<ResourceKey<? extends Registry<?>>> NEEDED = Set.of(
        Registries.TRIM_MATERIAL, Registries.TRIM_PATTERN, Registries.DAMAGE_TYPE,
        Registries.BANNER_PATTERN);

    private static List<HolderLookup.RegistryLookup<?>> parents;
    private static ResourceManager assets;
    private static final java.util.Set<Loaded> bound = java.util.Collections.newSetFromMap(new java.util.IdentityHashMap<>());
    private static final java.util.Set<Loaded> baked = java.util.Collections.newSetFromMap(new java.util.IdentityHashMap<>());
    private static Loaded mod;
    private static Loaded everything;

    private ShippedData() {
    }

    /**
     * One load's result: the five registries it filled, and a provider that can also see everything
     * they point at.
     *
     * @param registries what the loader produced - the mod's five, and vanilla's trim materials.
     * @param data       the datapack the load read, still open, so a tag can be read from the same
     *                   stack of packs the registries came out of.
     * @param roots      the pack directories under this repository that went into it, in order.
     * @param full       those five PLUS the parent lookups. Serialization has to go through this
     *                   one: a fitting holds a {@code HolderSet<TrimMaterial>}, and an ops that
     *                   cannot name TRIM_MATERIAL refuses to encode it - and would refuse for a
     *                   registry the loader never touched, which is not the failure a test is for.
     */
    public record Loaded(
        RegistryAccess.Frozen registries,
        HolderLookup.Provider full,
        ResourceManager data,
        List<Path> roots
    ) {
        public <T> Registry<T> registry(final ResourceKey<? extends Registry<? extends T>> key) {
            return this.registries.lookupOrThrow(key);
        }

        /**
         * The five loaded registries and every built-in one, as a single access - the shape
         * {@link net.minecraft.tags.TagLoader#loadTagsForExistingRegistries} wants, and the nearest
         * thing here to what a server holds while it reloads.
         */
        public RegistryAccess everyRegistry() {
            final Map<ResourceKey<? extends Registry<?>>, Registry<?>> byKey = new LinkedHashMap<>();
            RegistryAccess.fromRegistryOfRegistries(BuiltInRegistries.REGISTRY).registries()
                .forEach(entry -> byKey.put(entry.key(), entry.value()));
            this.registries.registries().forEach(entry -> byKey.put(entry.key(), entry.value()));
            // Not frozen: freezing validates that every tag a registry has HEARD OF has members,
            // and a bare bootstrap creates a handful of empty ones (the tool-material and mineable
            // tags an item's components name). They are vanilla's, they are empty because no world
            // has reloaded, and they are nothing to do with this repository's files.
            return new RegistryAccess.ImmutableRegistryAccess(List.copyOf(byKey.values()));
        }
    }

    /** The mod's own data, alone - the content of the jar this repository builds. */
    public static synchronized Loaded mod() {
        if (mod == null) {
            mod = load(List.of(MOD));
        }
        return mod;
    }

    /**
     * The mod plus every pack in {@code packs/}, loaded together the way a player would install
     * them. A pack's parts name the mod's fittings, so a pack cannot be loaded on its own.
     */
    public static synchronized Loaded everything() {
        if (everything == null) {
            final List<Path> roots = new ArrayList<>();
            roots.add(MOD);
            roots.addAll(packs().values());
            everything = load(roots);
        }
        return everything;
    }

    /**
     * The mod plus ONE pack written by the test itself, loaded together - the shape of a player who
     * installed a pack this repository does not ship.
     *
     * <p>Not cached, because the caller owns the directory: two tests handing in two temporary packs
     * are two different worlds, and a cached one would be the first test's. A load is around a
     * second, which is the price of asking what a datapack load does to a file that is not ours.
     *
     * @param datapack a directory holding {@code pack.mcmeta} and {@code data/}.
     */
    public static Loaded withPack(final Path datapack) {
        return load(List.of(MOD, datapack));
    }

    /**
     * The art half: the mod's own assets and every pack's resource pack, stacked as a client would
     * have them. Vanilla's assets are NOT under this - nothing here reads one, and the vanilla
     * client pack is the one part of the game that is not in the common jar.
     *
     * <p>Left open for the life of the test JVM on purpose: it holds file handles, and closing it
     * would mean the second question about a part costs another walk of the tree.
     */
    public static synchronized ResourceManager clientResources() {
        if (assets == null) {
            final List<PackResources> packs = new ArrayList<>();
            packs.add(pack(MOD));
            packs().values().forEach(datapack ->
                packs.add(pack(datapack.getParent().resolve("resourcepack"))));
            assets = new MultiPackResourceManager(PackType.CLIENT_RESOURCES, packs);
        }
        return assets;
    }

    /**
     * Bind every tag in the loaded packs into the registries, once, the way {@code /reload} does.
     *
     * <p>Needed by anything that reads a file naming a tag EAGERLY - {@code Ingredient} is the one
     * that matters, so no recipe can be decoded without this: {@code "base": "#minecraft:chest_armor"}
     * throws "Tags not bound" against a game that has never loaded a datapack. It is deliberately
     * not part of the load itself, because the question "does this decode with no tags bound at all"
     * is the one {@link com.mattjesmc.armorpieces.loot.MemberSet} exists to answer yes to.
     */
    /**
     * Bind every item's default components, once, the way a server does at the end of a datapack load.
     *
     * <p>Needed by anything that builds an {@link net.minecraft.world.item.ItemStack} at all: an
     * item's components are no longer fixed at registration, they are BAKED from a registry provider
     * ({@code DataComponentInitializers}), because a default may point into a datapack registry -
     * an emerald's {@code minecraft:provides_trim_material} names a trim material, which is loaded
     * data. Until the bake has run every item holder answers {@code Components not bound yet}, and
     * {@code new ItemStack(Items.DIAMOND_HELMET)} throws a {@link NullPointerException} saying so.
     *
     * <p>After the tags, because the bake reads registries that a tag may point into, and after
     * {@link GameBootstrap#content()} - which the load does - so that this mod's own items are in
     * the list rather than only vanilla's.
     */
    public static synchronized void bakeItemComponents(final Loaded loaded) {
        if (!baked.add(loaded)) {
            return;
        }
        bindTags(loaded);
        BuiltInRegistries.DATA_COMPONENT_INITIALIZERS
            .build(net.minecraft.data.registries.VanillaRegistries.createLookup())
            .forEach(net.minecraft.core.component.DataComponentInitializers.PendingComponents::apply);
    }

    public static synchronized void bindTags(final Loaded loaded) {
        if (!bound.add(loaded)) {
            return;
        }
        // Registry by registry, with the overload that binds in place. The whole-game path
        // (loadTagsForExistingRegistries) is refused here - "Invalid method used for tag loading" -
        // because Fabric's registry sync wraps it for a server that is starting, and this is not one.
        loaded.everyRegistry().registries().forEach(entry -> bind(loaded.data(), entry.value()));
    }

    @SuppressWarnings("unchecked")
    private static <T> void bind(final ResourceManager resources, final Registry<T> registry) {
        if (!(registry instanceof MappedRegistry<T> mapped)) {
            return;
        }
        final TagLoader.ElementLookup<Holder<T>> lookup =
            (TagLoader.ElementLookup<Holder<T>>) TagLoader.ElementLookup.fromFrozenRegistry(registry);
        final Map<net.minecraft.tags.TagKey<T>, List<Holder<T>>> tags =
            TagLoader.loadTagsForRegistry(resources, registry.key(), lookup);
        // Two ways in, and the registry's own state picks which. In a Fabric environment the
        // built-in registries are still OPEN at the end of mod init, which is where a test JVM
        // stops: those take bindTags, and only take effect once frozen - a registry that is open
        // answers every tag with "Tags not bound" however the members were handed to it. The five
        // the loader just built are already shut, and those take the reload path a server uses.
        // Either way the freeze comes AFTER the members, since freezing checks that every tag the
        // registry has heard of has some.
        try {
            mapped.bindTags(tags);
            mapped.freeze();
        } catch (final IllegalStateException frozen) {
            if (!"Registry is already frozen".equals(frozen.getMessage())) {
                throw frozen;
            }
            mapped.prepareTagReload(new TagLoader.LoadResult<>(registry.key(), tags)).apply();
        }
    }

    /** The datapack half of every pack beside the mod, by pack name. Empty is a valid answer. */
    public static Map<String, Path> packs() {
        final Map<String, Path> found = new LinkedHashMap<>();
        if (!Files.isDirectory(PACKS)) {
            return found;
        }
        try (Stream<Path> entries = Files.list(PACKS)) {
            entries.sorted().forEach(pack -> {
                final Path datapack = pack.resolve("datapack");
                if (Files.isDirectory(datapack.resolve("data"))) {
                    found.put(pack.getFileName().toString(), datapack);
                }
            });
        } catch (final IOException failed) {
            throw new UncheckedIOException(failed);
        }
        return found;
    }

    /**
     * The five registries, in the order {@link ArmorPiecesRegistries#register()} declares them:
     * fittings before the parts that name them, loot groups last because a group reads the other
     * three. {@link RegistryValidator#none()} because emptiness is legal here - a pack may ship
     * skins and no parts.
     *
     * <p>A method rather than a constant on purpose. Every value in it touches
     * {@link ArmorPiecesRegistries}, whose own static initialiser registers a Fabric registry, and
     * that cannot run before {@link GameBootstrap#once()} has - so a constant would be initialised
     * when this class is LOADED, which is before any test has had the chance to boot the game.
     */
    private static List<RegistryDataLoader.RegistryData<?>> registries() {
        // content(), not types(): a shipped file may name this mod's own block or item - a tag does
        // - and a member that does not exist takes the whole tag with it.
        GameBootstrap.content();
        // Vanilla's trim materials, read with vanilla's own codec out of the vanilla pack below.
        // A material fitting holds a HolderSet of them, and they have to be loaded IN THIS PASS
        // rather than handed in as a parent lookup: a tag resolved against a parent belongs to the
        // loader's own wrapper for that lookup, and an ops built afterwards cannot name that owner,
        // so the fitting would decode and then refuse to encode. Taken from vanilla's own list
        // rather than rebuilt, and taken one entry rather than whole: the rest of that list is
        // worldgen, which needs registries this pass has no reason to load.
        final List<RegistryDataLoader.RegistryData<?>> all = new ArrayList<>(
            RegistryDataLoader.SYNCHRONIZED_REGISTRIES.stream()
                .filter(data -> NEEDED.contains(data.key()))
                .toList());
        all.addAll(List.of(
            new RegistryDataLoader.RegistryData<>(
                ArmorPiecesRegistries.FITTING, Fitting.DIRECT_CODEC, RegistryValidator.none()),
            new RegistryDataLoader.RegistryData<>(
                ArmorPiecesRegistries.ARMOR_DECORATION, ArmorDecoration.DIRECT_CODEC, RegistryValidator.none()),
            new RegistryDataLoader.RegistryData<>(
                ArmorPiecesRegistries.ARMOR_SKIN, ArmorSkin.DIRECT_CODEC, RegistryValidator.none()),
            new RegistryDataLoader.RegistryData<>(
                ArmorPiecesRegistries.CLOTH, Cloth.DIRECT_CODEC, RegistryValidator.none()),
            new RegistryDataLoader.RegistryData<>(
                ArmorPiecesRegistries.LOOT_GROUP, LootGroup.DIRECT_CODEC, RegistryValidator.none())));
        return List.copyOf(all);
    }

    private static Loaded load(final List<Path> roots) {
        final List<RegistryDataLoader.RegistryData<?>> what = registries();
        // Vanilla's built-in datapack first, exactly as a server stacks it: the game's own
        // trim materials are in it, and a fitting that names a tag of them is meaningless without.
        final List<PackResources> packs = new ArrayList<>();
        packs.add(ServerPacksSource.createVanillaPackSource());
        roots.stream().map(ShippedData::pack).forEach(packs::add);
        // Not closed: the manager is the datapack, and a tag is read out of the same one later.
        final MultiPackResourceManager resources =
            new MultiPackResourceManager(PackType.SERVER_DATA, packs);
        final RegistryAccess.Frozen loaded =
            RegistryDataLoader.load(resources, parents(), what, Runnable::run).join();
        final HolderLookup.Provider full = HolderLookup.Provider.create(Stream.concat(
            parents().stream(),
            loaded.registries().map(RegistryAccess.RegistryEntry::value)));
        return new Loaded(loaded, full, resources, List.copyOf(roots));
    }

    /**
     * Everything a shipped file may point at that is not loaded in the pass itself: items,
     * attributes, mob effects and the rest of {@link BuiltInRegistries}, which are code and are
     * there the moment the game is bootstrapped.
     */
    private static synchronized List<HolderLookup.RegistryLookup<?>> parents() {
        if (parents == null) {
            GameBootstrap.once();
            parents = RegistryAccess.fromRegistryOfRegistries(BuiltInRegistries.REGISTRY).registries()
                .<HolderLookup.RegistryLookup<?>>map(RegistryAccess.RegistryEntry::value)
                .toList();
        }
        return parents;
    }

    private static PackResources pack(final Path root) {
        final String name = ROOT.relativize(root).toString().replace('\\', '/');
        return new PathPackResources(
            new PackLocationInfo(name, Component.literal(name), PackSource.BUILT_IN, Optional.empty()),
            root);
    }

    /**
     * Encode, decode, and hand back what came out. The assertion every content test makes, and the
     * one that catches the class of bug the 0.4.0 game cycles were spent on: a codec that silently
     * drops a field on the way out reads back as a different value.
     */
    public static <T> T roundTrip(final Loaded loaded, final Codec<T> codec, final T value) {
        final var ops = loaded.full().createSerializationContext(com.mojang.serialization.JsonOps.INSTANCE);
        final var json = codec.encodeStart(ops, value)
            .getOrThrow(message -> new AssertionError("could not be encoded: " + message));
        return codec.parse(ops, json)
            .getOrThrow(message -> new AssertionError("encoded to something unreadable: " + message
                + "\n" + json));
    }
}
