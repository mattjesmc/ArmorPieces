package com.mattjesmc.armorpieces.client.texture;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mattjesmc.armorpieces.ArmorPieces;
import com.mojang.blaze3d.platform.NativeImage;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.fabricmc.fabric.api.resource.SimpleSynchronousResourceReloadListener;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.texture.DynamicTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.server.packs.resources.Resource;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.util.ARGB;
import org.jspecify.annotations.Nullable;

/**
 * Resolves the texture a decorative part draws with, colouring it for the material on demand.
 *
 * <p>A part used to ship one PNG per trim material - sixteen files each, 288 across the mod, and a
 * flat wall for anyone adding a seventeenth material, because the texture path is built from the
 * PART's namespace and so a material mod would have had to ship art into every part author's
 * namespace. That is now gone. A part ships ONE greyscale master (plus an optional static layer),
 * and this class recolours it through the material's own vanilla palette at load time, exactly as
 * {@code paletted_permutations} does for trim patterns.
 *
 * <p>What that buys, and it is the whole point: a mod that adds a trim material has to ship a
 * palette and register it in {@code atlases/armor_trims.json} ANYWAY, or its material would not
 * render on a vanilla trim either. This class reads that same file - through
 * {@link ResourceManager#getResourceStack}, so every pack's permutations are merged rather than the
 * last one winning - and so a new material colours every decoration that exists, including ones from
 * mods it has never heard of, with no additional assets at all.
 *
 * <p>Resolution order for a part and a material suffix:
 *
 * <ol>
 *   <li>{@code <part>_<suffix>.png}, if a pack supplies one - the hand-authored override still wins,
 *       so a part that genuinely needs bespoke art per material can have it;</li>
 *   <li>{@code <part>.png} recoloured through the material's palette - the normal path;</li>
 *   <li>the override path anyway, so a part with neither fails visibly rather than silently.</li>
 * </ol>
 */
@Environment(EnvType.CLIENT)
public final class DecorationTextureManager implements SimpleSynchronousResourceReloadListener {
    private static final Identifier ID =
        Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "decoration_textures");

    private static final String DIRECTORY = "textures/entity/decoration";
    /**
     * Reserved: a part's non-metal companion layer. A trim material whose suffix is literally
     * {@code static} would collide with it, which is a trade the two-file split accepts in exchange
     * for never having to guess whether a coloured pixel meant "keep this colour" or "this is art".
     */
    private static final String STATIC_SUFFIX = "_static";

    private static final Identifier ARMOR_TRIMS_ATLAS =
        Identifier.fromNamespaceAndPath("minecraft", "atlases/armor_trims.json");
    private static final Identifier DEFAULT_PALETTE_KEY =
        Identifier.fromNamespaceAndPath("minecraft", "trims/color_palettes/trim_palette");
    private static final String PALETTED_PERMUTATIONS = "paletted_permutations";

    private static final DecorationTextureManager INSTANCE = new DecorationTextureManager();

    /** Every decoration PNG any pack supplies. Membership only - the bytes are read on demand. */
    private volatile Set<Identifier> available = Set.of();
    /** Material suffix to palette sprite, merged across every pack's armor trim atlas. */
    private volatile Map<String, Identifier> palettePaths = Map.of();
    private volatile Identifier paletteKeyPath = DEFAULT_PALETTE_KEY;

    /** Baked texture id to the id actually rendered with; also negative-caches a failed bake. */
    private final Map<Identifier, Identifier> resolved = new HashMap<>();
    /** What we handed to the texture manager, so a reload can hand it back. */
    private final List<Identifier> registered = new ArrayList<>();
    private final Map<String, Optional<DecorationPalette>> palettes = new HashMap<>();

    private DecorationTextureManager() {}

    public static DecorationTextureManager instance() {
        return INSTANCE;
    }

    /**
     * The texture to draw this part in this material with, baking it on first use.
     *
     * <p>Called from the render layer, so everything expensive is cached: a bake happens once per
     * part per material per resource reload, and every later frame is a map lookup.
     */
    public Identifier resolve(final Identifier assetId, final String suffix) {
        final Identifier override = file(assetId, "_" + suffix);
        if (this.available.contains(override)) {
            return override;
        }
        if (!this.available.contains(file(assetId, ""))) {
            // Neither a master nor an override. Return the override path so the failure shows up as
            // the missing-texture checker, which is the honest answer and the one a pack author can
            // actually diagnose.
            return override;
        }
        final Identifier baked = bakedId(assetId, suffix);
        final Identifier cached = this.resolved.get(baked);
        if (cached != null) {
            return cached;
        }
        final Identifier result = bake(assetId, suffix, baked) ? baked : override;
        this.resolved.put(baked, result);
        return result;
    }

    @Override
    public void onResourceManagerReload(final ResourceManager manager) {
        releaseBaked();
        this.palettes.clear();
        this.available = Set.copyOf(
            manager.listResources(DIRECTORY, path -> path.getPath().endsWith(".png")).keySet());
        loadPaletteMapping(manager);
    }

    @Override
    public Identifier getFabricId() {
        return ID;
    }

    // ---- baking ---------------------------------------------------------------------------------

    private boolean bake(final Identifier assetId, final String suffix, final Identifier target) {
        final ResourceManager manager = Minecraft.getInstance().getResourceManager();
        NativeImage master = null;
        NativeImage statics = null;
        try {
            master = readImage(manager, file(assetId, ""));
            if (master == null) {
                return false;
            }
            statics = readImage(manager, file(assetId, STATIC_SUFFIX));
            final NativeImage out = recolour(master, statics, palette(manager, suffix));
            final Minecraft client = Minecraft.getInstance();
            client.getTextureManager().release(target);
            client.getTextureManager().register(target, new DynamicTexture(target::toString, out));
            this.registered.add(target);
            return true;
        } catch (final RuntimeException e) {
            ArmorPieces.LOGGER.error("[Armor Pieces] Could not colour decoration {} for {}", assetId, suffix, e);
            return false;
        } finally {
            close(master);
            close(statics);
        }
    }

    /**
     * The master, recoloured. Alpha always comes from the master, which stays the single source of
     * truth for the silhouette: a static pixel outside it is not drawn.
     *
     * <p>A null palette means the pack registered a material but shipped no palette for it. The part
     * is then drawn at the master's own greys rather than being dropped - shading intact, tint
     * missing, which reads as an unfinished material instead of a broken mod.
     */
    private static NativeImage recolour(
        final NativeImage master,
        final @Nullable NativeImage statics,
        final @Nullable DecorationPalette palette
    ) {
        final int width = master.getWidth();
        final int height = master.getHeight();
        final NativeImage out = new NativeImage(width, height, false);
        // A part uses a handful of static colours over thousands of pixels, so their ramps are built
        // once and shared rather than per pixel.
        final Map<Integer, DecorationPalette> staticRamps = new HashMap<>();

        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                final int source = master.getPixel(x, y);
                final int alpha = ARGB.alpha(source);
                if (alpha == 0) {
                    out.setPixel(x, y, 0);
                    continue;
                }
                final int luminance = ARGB.red(source);

                Integer staticColour = null;
                if (statics != null && x < statics.getWidth() && y < statics.getHeight()) {
                    final int s = statics.getPixel(x, y);
                    if (ARGB.alpha(s) != 0) {
                        staticColour = s & 0x00FFFFFF;
                    }
                }

                final int rgb;
                if (staticColour != null) {
                    rgb = staticRamps
                        .computeIfAbsent(staticColour, DecorationPalette::ofStaticColour)
                        .rgb(luminance);
                } else if (palette != null) {
                    rgb = palette.rgb(luminance);
                } else {
                    rgb = source;
                }
                out.setPixel(x, y, (alpha << 24) | (rgb & 0x00FFFFFF));
            }
        }
        return out;
    }

    // ---- palettes -------------------------------------------------------------------------------

    private @Nullable DecorationPalette palette(final ResourceManager manager, final String suffix) {
        return this.palettes.computeIfAbsent(suffix, s -> Optional.ofNullable(loadPalette(manager, s)))
            .orElse(null);
    }

    private @Nullable DecorationPalette loadPalette(final ResourceManager manager, final String suffix) {
        // The atlas is authoritative, because it is what vanilla's own trims go through. The
        // convention path is the safety net for a material that registered without wiring itself
        // into the atlas - its trims would be broken too, but its decorations need not be.
        Identifier sprite = this.palettePaths.get(suffix);
        if (sprite == null) {
            sprite = Identifier.fromNamespaceAndPath("minecraft", "trims/color_palettes/" + suffix);
        }
        NativeImage key = null;
        NativeImage palette = null;
        try {
            key = readImage(manager, sprite(this.paletteKeyPath));
            palette = readImage(manager, sprite(sprite));
            if (key == null || palette == null) {
                return null;
            }
            return DecorationPalette.of(key, palette);
        } finally {
            close(key);
            close(palette);
        }
    }

    /**
     * Reads every pack's armor trim atlas and merges the suffix-to-palette mappings.
     *
     * <p>Deliberately reads the resource STACK rather than the top resource: vanilla concatenates
     * atlas sources across packs, which is how two material mods coexist, and taking only the
     * winning pack here would have quietly broken the second one.
     */
    private void loadPaletteMapping(final ResourceManager manager) {
        final Map<String, Identifier> found = new HashMap<>();
        Identifier keyPath = DEFAULT_PALETTE_KEY;
        for (final Resource resource : manager.getResourceStack(ARMOR_TRIMS_ATLAS)) {
            try (InputStream stream = resource.open()) {
                final JsonElement root = JsonParser.parseReader(new InputStreamReader(stream));
                if (!root.isJsonObject()) {
                    continue;
                }
                final JsonElement sources = root.getAsJsonObject().get("sources");
                if (sources == null || !sources.isJsonArray()) {
                    continue;
                }
                for (final JsonElement element : (JsonArray) sources) {
                    if (!element.isJsonObject()) {
                        continue;
                    }
                    final JsonObject source = element.getAsJsonObject();
                    final JsonElement type = source.get("type");
                    if (type == null || !type.getAsString().endsWith(PALETTED_PERMUTATIONS)) {
                        continue;
                    }
                    final JsonElement key = source.get("palette_key");
                    if (key != null) {
                        keyPath = identifier(key.getAsString());
                    }
                    final JsonElement permutations = source.get("permutations");
                    if (permutations != null && permutations.isJsonObject()) {
                        for (final var entry : permutations.getAsJsonObject().entrySet()) {
                            found.put(entry.getKey(), identifier(entry.getValue().getAsString()));
                        }
                    }
                }
            } catch (final IOException | RuntimeException e) {
                ArmorPieces.LOGGER.warn("[Armor Pieces] Could not read trim palettes from {}", ARMOR_TRIMS_ATLAS, e);
            }
        }
        this.palettePaths = Map.copyOf(found);
        this.paletteKeyPath = keyPath;
    }

    // ---- plumbing -------------------------------------------------------------------------------

    private void releaseBaked() {
        final Minecraft client = Minecraft.getInstance();
        for (final Identifier id : this.registered) {
            client.getTextureManager().release(id);
        }
        this.registered.clear();
        this.resolved.clear();
    }

    /** {@code <ns>:textures/entity/decoration/<part><suffix>.png}. */
    private static Identifier file(final Identifier assetId, final String suffix) {
        return assetId.withPath(path -> DIRECTORY + "/" + path + suffix + ".png");
    }

    /** A sprite id as an atlas names it, turned into the file it actually lives in. */
    private static Identifier sprite(final Identifier spriteId) {
        return spriteId.withPath(path -> "textures/" + path + ".png");
    }

    /** Where a baked texture is registered. Namespaced under this mod so it collides with nothing. */
    private static Identifier bakedId(final Identifier assetId, final String suffix) {
        return Identifier.fromNamespaceAndPath(
            ArmorPieces.MOD_ID,
            "coloured/" + assetId.getNamespace() + "/" + assetId.getPath() + "_" + suffix);
    }

    /** Parsed by hand rather than through a codec: an atlas value is a bare id, and may omit its namespace. */
    private static Identifier identifier(final String raw) {
        final int colon = raw.indexOf(':');
        return colon < 0
            ? Identifier.fromNamespaceAndPath("minecraft", raw)
            : Identifier.fromNamespaceAndPath(raw.substring(0, colon), raw.substring(colon + 1));
    }

    private static @Nullable NativeImage readImage(final ResourceManager manager, final Identifier id) {
        final Optional<Resource> resource = manager.getResource(id);
        if (resource.isEmpty()) {
            return null;
        }
        try (InputStream stream = resource.get().open()) {
            return NativeImage.read(stream);
        } catch (final IOException e) {
            ArmorPieces.LOGGER.error("[Armor Pieces] Could not read decoration texture {}", id, e);
            return null;
        }
    }

    private static void close(final @Nullable NativeImage image) {
        if (image != null) {
            image.close();
        }
    }
}
