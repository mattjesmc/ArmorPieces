package com.mattjesmc.armorpieces.client.texture;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.decoration.fitting.FittingColour;
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
 * Resolves the texture a decorative part draws with, colouring it for the material - and for
 * whatever is set in its fittings - on demand.
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
 * <p>Fittings ride the same machinery. A masked fitting is one more greyscale sheet beside the
 * master, {@code <part>_<fitting>.png}, and while the fitting is filled its opaque pixels are
 * coloured through whatever the fitting asked for - a second material's palette, or a dye's colour
 * through the static ramp - on top of the recoloured master. An empty fitting costs nothing: the
 * mask is not read and the bake is the one it always was.
 *
 * <p>Resolution order for a part and a material suffix:
 *
 * <ol>
 *   <li>{@code <part>_<suffix>.png}, if a pack supplies one - the hand-authored override still wins,
 *       so a part that genuinely needs bespoke art per material can have it. With fittings filled
 *       the override serves as the base the masks are laid over;</li>
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
     * A fitting's mask lives at the same kind of name, {@code <part>_<fitting>.png}, and the same
     * trade applies: a fitting named after a trim material would shadow that material's override.
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
     * One filled masked fitting, as the baker needs it: which mask sheet to read, and how to colour
     * what it covers.
     *
     * @param name   the fitting id's path - the mask is {@code <part>_<name>.png}.
     * @param colour what the fitting asked for, see {@link FittingColour}.
     */
    public record Mask(String name, FittingColour colour) {}

    /** The texture for a part in a material with nothing set in its fittings. */
    public Identifier resolve(final Identifier assetId, final String suffix) {
        return this.resolve(assetId, suffix, List.of());
    }

    /**
     * The texture to draw this part in this material with these fittings, baking it on first use.
     *
     * <p>Called from the render layer, so everything expensive is cached: a bake happens once per
     * part per material per combination of filled fittings per resource reload, and every later
     * frame is a map lookup. The combinations are lazy, so a part with two fittings costs the
     * combinations actually worn, not the product of everything that could be.
     *
     * @param masks in layer order - a later mask paints over an earlier one where they overlap.
     */
    public Identifier resolve(final Identifier assetId, final String suffix, final List<Mask> masks) {
        final Identifier override = file(assetId, "_" + suffix);
        final boolean hasOverride = this.available.contains(override);
        if (hasOverride && masks.isEmpty()) {
            return override;
        }
        if (!hasOverride && !this.available.contains(file(assetId, ""))) {
            // Neither a master nor an override. Return the override path so the failure shows up as
            // the missing-texture checker, which is the honest answer and the one a pack author can
            // actually diagnose.
            return override;
        }
        final Identifier baked = bakedId(assetId, suffix, masks);
        final Identifier cached = this.resolved.get(baked);
        if (cached != null) {
            return cached;
        }
        final Identifier result = bake(assetId, suffix, masks, hasOverride ? override : null, baked) ? baked : override;
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

    private boolean bake(
        final Identifier assetId,
        final String suffix,
        final List<Mask> masks,
        final @Nullable Identifier override,
        final Identifier target
    ) {
        final ResourceManager manager = Minecraft.getInstance().getResourceManager();
        NativeImage master = null;
        NativeImage statics = null;
        final List<NativeImage> maskImages = new ArrayList<>(masks.size());
        try {
            final NativeImage out;
            if (override != null) {
                // Hand-authored art per material is already coloured; the masks lay over it as they
                // would over a recoloured master.
                master = readImage(manager, override);
                if (master == null) {
                    return false;
                }
                out = copy(master);
            } else {
                master = readImage(manager, file(assetId, ""));
                if (master == null) {
                    return false;
                }
                statics = readImage(manager, file(assetId, STATIC_SUFFIX));
                out = recolour(master, statics, palette(manager, suffix));
            }
            for (final Mask mask : masks) {
                final Identifier sheet = file(assetId, "_" + mask.name());
                // A fitting the part declares but ships no mask for is a fitting that changes nothing
                // visible. Legitimate for a pack that only wants the gem's effect, so not an error.
                final NativeImage image = this.available.contains(sheet) ? readImage(manager, sheet) : null;
                if (image != null) {
                    maskImages.add(image);
                    applyMask(out, master, image, ramp(manager, mask.colour()));
                }
            }
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
            maskImages.forEach(DecorationTextureManager::close);
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

    /**
     * Lays one fitting's mask over the image in place. The mask's own value is the shading - it is a
     * greyscale sheet painted like the master, so a gem can be cut differently from the metal it
     * replaces - and the master's alpha is still the silhouette: a mask pixel where the master is
     * transparent is skipped, exactly as a static pixel there would be.
     *
     * <p>A null ramp means a palette fitting named a material with no palette; the mask then shows
     * at its own greys, the same honest answer the master gives for such a material.
     */
    private static void applyMask(
        final NativeImage out,
        final NativeImage master,
        final NativeImage mask,
        final @Nullable DecorationPalette ramp
    ) {
        final int width = Math.min(out.getWidth(), mask.getWidth());
        final int height = Math.min(out.getHeight(), mask.getHeight());
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                final int m = mask.getPixel(x, y);
                if (ARGB.alpha(m) == 0) {
                    continue;
                }
                final int alpha = ARGB.alpha(master.getPixel(x, y));
                if (alpha == 0) {
                    continue;
                }
                final int luminance = ARGB.red(m);
                final int rgb = ramp != null ? ramp.rgb(luminance) : m;
                out.setPixel(x, y, (alpha << 24) | (rgb & 0x00FFFFFF));
            }
        }
    }

    private @Nullable DecorationPalette ramp(final ResourceManager manager, final FittingColour colour) {
        return switch (colour) {
            case FittingColour.Palette p -> palette(manager, p.suffix());
            case FittingColour.Solid s -> DecorationPalette.ofStaticColour(s.rgb());
        };
    }

    private static NativeImage copy(final NativeImage source) {
        final NativeImage out = new NativeImage(source.getWidth(), source.getHeight(), false);
        out.copyFrom(source);
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

    /**
     * Where a baked texture is registered. Namespaced under this mod so it collides with nothing,
     * and naming every filled fitting so that each combination is its own texture.
     */
    private static Identifier bakedId(final Identifier assetId, final String suffix, final List<Mask> masks) {
        final StringBuilder path = new StringBuilder("coloured/")
            .append(assetId.getNamespace()).append('/').append(assetId.getPath()).append('_').append(suffix);
        for (final Mask mask : masks) {
            path.append('.').append(mask.name().replace('/', '.')).append('-');
            switch (mask.colour()) {
                case FittingColour.Palette p -> path.append(p.suffix());
                case FittingColour.Solid s -> path.append('x').append(Integer.toHexString(s.rgb() & 0x00FFFFFF));
            }
        }
        return Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, path.toString());
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
