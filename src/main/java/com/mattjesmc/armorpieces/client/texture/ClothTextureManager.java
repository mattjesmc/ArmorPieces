package com.mattjesmc.armorpieces.client.texture;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.cloth.Cloth;
import com.mattjesmc.armorpieces.cloth.ClothValue;
import com.mattjesmc.armorpieces.decoration.fitting.builtin.BannerFitting;
import com.mattjesmc.armorpieces.skin.SkinBake;
import com.mojang.blaze3d.platform.NativeImage;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.fabricmc.fabric.api.resource.SimpleSynchronousResourceReloadListener;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.Sheets;
import net.minecraft.client.renderer.texture.DynamicTexture;
import net.minecraft.client.resources.model.sprite.SpriteId;
import net.minecraft.resources.Identifier;
import net.minecraft.server.packs.resources.Resource;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.util.ARGB;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.block.entity.BannerPatternLayers;
import org.jspecify.annotations.Nullable;

/**
 * Composites a garment into the texture a piece of armor draws with - the third of the mod's texture
 * managers and deliberately a relative of the other two, but the only one that does not START from a
 * greyscale master of its own.
 *
 * <p>{@link DecorationTextureManager} recolours a part's master through a trim palette;
 * {@link ArmorSkinTextureManager} recolours a skin's master through a ramp derived from the armor.
 * Here the master is a CUT MASK - alpha says where the cloth is, value says how it folds - and the
 * colour comes from a banner the player made at a loom. What the armor supplies is neither the
 * silhouette nor the colour but the LIGHT.
 *
 * <p>The result is one texture: the armor's own pixels where the mask is transparent, the garment
 * where it is not. That is what makes the layering free - the cloth is over the skin because the
 * skin is the pixels it composites onto, under the trim because the trim is a later pass, and under
 * every part because parts draw after the whole equipment stack. No new render pass exists.
 *
 * <h2>The five steps, per texel</h2>
 *
 * <ol>
 *   <li><b>the base</b> - the texture the layer was about to draw with, upsampled nearest, so the
 *       armor is exactly what it was where there is no cloth;</li>
 *   <li><b>the cut</b> - where the mask is transparent, stop; and on a face the armor uses, where
 *       the ARMOR is transparent, stop as well, because a garment is worn on the armor and there is
 *       nothing there to hang it on. The mask says how far the garment reaches; the armor says how
 *       far it can, except on a face it has no use for at all - see {@link #paintedFaces};</li>
 *   <li><b>the colour</b> - the banner's design where the texel is on one of the two torso panels,
 *       the base dye everywhere else the mask covers;</li>
 *   <li><b>the value</b> - the mask's own, plus the armor's lighting at that texel;</li>
 *   <li><b>the ramp</b> - {@link DecorationPalette#ofStaticColour}, which is the same three-stop rule
 *       a dye fitting and a horn's ivory go through, so a dyed cloth and a dyed inlay beside it shade
 *       identically.</li>
 * </ol>
 *
 * <h2>The lighting, which is the point</h2>
 *
 * <p>{@link SkinBake#lightmap} measures a texture's deviation from the middle of its own range,
 * normalised by that range. It was written so a skin's flat pattern would pick up vanilla's rivets
 * and edges, and it does the same for a flat banner: iron's studs and diamond's facets read THROUGH
 * the cloth, while gold's bright sheet and netherite's dark one contribute the same amount of shape
 * rather than their own contrast. The mix is {@link #ARMOR_LIGHT}, a little under a skin's, because
 * a garment sits further off the plate than a repaint of it does.
 *
 * <p>What it is measured FROM is the form the player actually sees: a skinned piece's own greyscale
 * master, or else the material's vanilla equipment texture. Both are plain resources, which is why
 * nothing has to be shared between the managers for this - only the base pixels are, and only when
 * the layer being composited onto is itself a bake. The same image is what the garment is CLIPPED to,
 * and the two jobs want the same picture: the thing the cloth is worn on.
 *
 * <h2>Resolution</h2>
 *
 * <p>The bake runs at {@link #WIDTH} texels wide however wide the armor texture is. A shield pattern
 * is painted for 12x22 and the chest front is 8x12: on the vanilla grid a bordure survives and a
 * charge turns to mush. The armor's own texels are upsampled nearest, so the plate still reads at
 * vanilla resolution, and the design gets four times the room. Nothing downstream has an opinion,
 * because a model's UVs are fractions.
 */
@Environment(EnvType.CLIENT)
public final class ClothTextureManager implements SimpleSynchronousResourceReloadListener {
    private static final Identifier ID =
        Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "cloth_textures");

    /** Where a cloth's cut masks live, and the only directory this class indexes. */
    private static final String DIRECTORY = "textures/entity/cloth";
    /** The two sheets a cloth can be cut from - the same two a skin knows about. */
    private static final String BODY_SHEET = "humanoid";
    private static final String LEGGINGS_SHEET = "humanoid_leggings";

    /** How much of the armor's own lighting is mixed into the garment. A skin uses 0.35. */
    public static final float ARMOR_LIGHT = 0.30F;
    /** The width every bake is brought up to, so a pattern has room. See the class note. */
    private static final int WIDTH = 256;
    /** The grid the net rectangles below are stated on - vanilla's armor sheet. */
    private static final int GRID_WIDTH = 64;
    private static final int GRID_HEIGHT = 32;

    /**
     * The two faces that carry the design, on the grid above: the front and back of the torso box.
     *
     * <p>The same rectangles on both sheets, because vanilla lays the chestplate's body box and the
     * leggings' waist box out at the same place in their own nets - which is also why a tunic's two
     * halves line up. See {@code tools/skin_sheets.py}, which is where the masks are cut from.
     */
    private static final int[] FRONT = {20, 20, 8, 12};
    private static final int[] BACK = {32, 20, 8, 12};

    /**
     * Every face of the torso box, in the order {@link #paintedFaces} reports them: the two panels
     * above, then the flanks, then the top and the underside.
     *
     * <p>The last two are why this table exists at all. Vanilla paints NOTHING on the top or the
     * bottom of the chest box - a breastplate has no lid - and a face the armor paints nothing on is
     * not a hole in it: it is a face the armor has no use for, and a garment draped over the
     * shoulders has every use for. So the clip is judged per face rather than per texel.
     */
    private static final int[] LEFT = {28, 20, 4, 12};
    private static final int[] RIGHT = {16, 20, 4, 12};
    private static final int[] TOP = {20, 16, 8, 4};
    private static final int[] BOTTOM = {28, 16, 8, 4};
    private static final int[][] FACES = {FRONT, BACK, LEFT, RIGHT, TOP, BOTTOM};

    /** The flag every banner pattern is painted for: 20 wide, 40 tall, 1 deep, net at (0, 0). */
    private static final int[] FLAG = {20, 40, 1};
    /** The plate every shield pattern is painted for. */
    private static final int[] PLATE = {12, 22, 1};
    /** Both of vanilla's pattern sheets are 64x64, and a rect below is scaled off that. */
    private static final float SPRITE_SHEET = 64.0F;

    /**
     * How many bakes are kept. Unlike a part or a skin the key space here is UNBOUNDED - a player may
     * wear any banner - so this is the one cache in the mod that evicts. A crowd in one livery is one
     * bake; a crowd in thirty different ones is thirty, and the thirty-first costs the oldest.
     */
    private static final int CACHE_SIZE = 64;

    private static final ClothTextureManager INSTANCE = new ClothTextureManager();

    /** Every cut mask any pack supplies. Membership only - the bytes are read on demand. */
    private volatile Set<Identifier> available = Set.of();

    /**
     * Baked texture id to whether the bake succeeded, in access order so the eldest goes first. A
     * failed bake is remembered too: it is what stops a missing mask being read once a frame.
     */
    private final LinkedHashMap<Identifier, Boolean> resolved =
        new LinkedHashMap<>(16, 0.75F, true) {
            @Override
            protected boolean removeEldestEntry(final Map.Entry<Identifier, Boolean> eldest) {
                if (size() <= CACHE_SIZE) {
                    return false;
                }
                if (Boolean.TRUE.equals(eldest.getValue())) {
                    Minecraft.getInstance().getTextureManager().release(eldest.getKey());
                }
                return true;
            }
        };

    private ClothTextureManager() {}

    public static ClothTextureManager instance() {
        return INSTANCE;
    }

    /**
     * The texture to draw a clothed piece's layer with, or null to leave the layer's own texture
     * alone - which is the honest answer for a garment that does not reach this sheet.
     *
     * <p>Called from the render layer, so everything expensive is cached: a bake happens once per
     * garment per design per armor texture per resource reload, and every later frame is a map
     * lookup.
     *
     * @param sheetName {@code humanoid} or {@code humanoid_leggings} - the layer type's own name,
     *                  which is also the name of the cut mask to use.
     * @param target    the texture this layer was about to draw with, and the pixels the garment is
     *                  composited onto. May itself be a bake - a skinned piece's - in which case its
     *                  pixels come from {@link ArmorSkinTextureManager} rather than from a pack.
     * @param shading   the image the armor's lighting is measured from: the skin's own master where
     *                  there is a skin, else the material's vanilla texture. Null for neither, and
     *                  the garment is then drawn with its own folds and no armor form.
     */
    public @Nullable Identifier resolve(
        final ClothValue value,
        final String sheetName,
        final Identifier target,
        final @Nullable Identifier shading
    ) {
        if (!BODY_SHEET.equals(sheetName) && !LEGGINGS_SHEET.equals(sheetName)) {
            // A baby's sheet, a wolf's, a horse's. A cloth is cut out of the humanoid grid and has
            // nothing to say about any other, so the layer's own texture stands.
            return null;
        }
        final Cloth cloth = value.cloth().value();
        if (!this.available.contains(cloth.mask(sheetName))) {
            return null;
        }
        final Identifier baked = bakedId(value, sheetName, target);
        final Boolean cached = this.resolved.get(baked);
        if (cached != null) {
            return cached ? baked : null;
        }
        final boolean ok = bake(value, sheetName, target, shading, baked);
        this.resolved.put(baked, ok);
        return ok ? baked : null;
    }

    @Override
    public void onResourceManagerReload(final ResourceManager manager) {
        releaseBaked();
        this.available = Set.copyOf(
            manager.listResources(DIRECTORY, path -> path.getPath().endsWith(".png")).keySet());
    }

    @Override
    public Identifier getFabricId() {
        return ID;
    }

    // ---- baking ---------------------------------------------------------------------------------

    private boolean bake(
        final ClothValue value,
        final String sheetName,
        final Identifier target,
        final @Nullable Identifier shading,
        final Identifier baked
    ) {
        final ResourceManager manager = Minecraft.getInstance().getResourceManager();
        NativeImage mask = null;
        try {
            mask = readImage(manager, value.cloth().value().mask(sheetName));
            if (mask == null) {
                return false;
            }
            final Image base = base(manager, target);
            if (base == null) {
                return false;
            }

            final int scale = Math.max(1, Math.round((float) WIDTH / base.width()));
            final int width = base.width() * scale;
            final int height = base.height() * scale;

            final Image armor = shading == null ? null : image(manager, shading);
            final byte[] lightmap = armor == null ? null : SkinBake.lightmap(armor.pixels(), ARMOR_LIGHT);
            final boolean[] painted = armor == null ? null : paintedFaces(armor);

            final Panel panel = panel(manager, value);
            final Map<Integer, DecorationPalette> ramps = new HashMap<>();

            final NativeImage out = new NativeImage(width, height, false);
            for (int y = 0; y < height; y++) {
                for (int x = 0; x < width; x++) {
                    final int bx = x / scale;
                    final int by = y / scale;
                    final int under = base.pixels()[by * base.width() + bx];

                    final int mx = x * mask.getWidth() / width;
                    final int my = y * mask.getHeight() / height;
                    final int m = mask.getPixel(mx, my);
                    if (ARGB.alpha(m) == 0) {
                        out.setPixel(x, y, under);
                        continue;
                    }

                    // The texel's place on the 64x32 net, in fractions, so a panel is sampled at the
                    // bake's resolution rather than the armor texture's.
                    final float gx = x * (float) GRID_WIDTH / width;
                    final float gy = y * (float) GRID_HEIGHT / height;
                    final int colour = panel == null
                        ? value.base().getTextureDiffuseColor() & 0x00FFFFFF
                        : panel.sample(gx, gy, value.base().getTextureDiffuseColor() & 0x00FFFFFF);

                    int shade = ARGB.red(m);
                    if (armor != null) {
                        final int ax = x * armor.width() / width;
                        final int ay = y * armor.height() / height;
                        final int texel = ay * armor.width() + ax;
                        // A garment is worn ON the armor, so on a face the armor USES, where the
                        // armor paints nothing there is nothing to hang the cloth on and it stops
                        // too. That is what gives the neck's notch and the hem's taper without
                        // counting rows into a mask by hand, and it gives them from whatever the
                        // piece actually is - vanilla's cut, or a skin's, which is not the same cut.
                        //
                        // On a face the armor uses NOWHERE the rule is off, and deliberately: the top
                        // of the chest box is empty on every vanilla material because a breastplate
                        // has no lid, and a tunic's shoulders and a tabard's straps live exactly
                        // there. An empty face is not a hole to respect, it is room to use.
                        if (clipped(painted, gx, gy) && ARGB.alpha(armor.pixels()[texel]) == 0) {
                            out.setPixel(x, y, under);
                            continue;
                        }
                        shade += lightmap[texel];
                    }
                    final DecorationPalette ramp =
                        ramps.computeIfAbsent(colour, DecorationPalette::ofStaticColour);
                    out.setPixel(x, y, 0xFF000000 | (ramp.rgb(clamp(shade)) & 0x00FFFFFF));
                }
            }

            final Minecraft client = Minecraft.getInstance();
            client.getTextureManager().release(baked);
            client.getTextureManager().register(baked, new DynamicTexture(baked::toString, out));
            return true;
        } catch (final RuntimeException e) {
            ArmorPieces.LOGGER.error(
                "[Armor Pieces] Could not put cloth {} on {}", value.cloth().value().assetId(), target, e);
            return false;
        } finally {
            close(mask);
        }
    }

    /**
     * The pixels the garment is composited onto.
     *
     * <p>Two places they can come from, and the second is the only coupling between two of the
     * managers: a skinned piece's layer texture is a bake rather than a file, so the skin manager is
     * asked for the pixels it made. Everything else is a resource.
     */
    private static @Nullable Image base(final ResourceManager manager, final Identifier target) {
        final ArmorSkinTextureManager.Baked skin = ArmorSkinTextureManager.instance().baked(target);
        if (skin != null) {
            return new Image(skin.pixels(), skin.width(), skin.height());
        }
        return image(manager, target);
    }

    // ---- the design -----------------------------------------------------------------------------

    /**
     * Which faces of the torso box the armor paints anything at all on - the six of {@link #FACES},
     * in order. Measured once per bake, since it is a property of the armor and not of the texel.
     */
    private static boolean[] paintedFaces(final Image armor) {
        final boolean[] painted = new boolean[FACES.length];
        for (int i = 0; i < FACES.length; i++) {
            final int[] rect = FACES[i];
            for (int y = rect[1]; y < rect[1] + rect[3] && !painted[i]; y++) {
                for (int x = rect[0]; x < rect[0] + rect[2]; x++) {
                    final int ax = x * armor.width() / GRID_WIDTH;
                    final int ay = y * armor.height() / GRID_HEIGHT;
                    if (ARGB.alpha(armor.pixels()[ay * armor.width() + ax]) != 0) {
                        painted[i] = true;
                        break;
                    }
                }
            }
        }
        return painted;
    }

    /**
     * Whether the cloth at this point on the net is trimmed to the armor: yes on a face the armor
     * uses, no on one it leaves entirely empty, and yes off the torso box altogether - a mask that
     * strays onto an arm is trimmed to the sleeve that is there.
     */
    private static boolean clipped(final boolean[] painted, final float gx, final float gy) {
        for (int i = 0; i < FACES.length; i++) {
            if (within(FACES[i], gx, gy)) {
                return painted[i];
            }
        }
        return true;
    }

    private static boolean within(final int[] rect, final float gx, final float gy) {
        return gx >= rect[0] && gx < rect[0] + rect[2] && gy >= rect[1] && gy < rect[1] + rect[3];
    }

    /**
     * The banner's design, composited once into the rectangle its sprites are painted for, ready to
     * be stretched over the two torso panels.
     *
     * <p>Done in PATTERN space rather than per output texel because a design is a handful of passes
     * over a 12x22 rect and the panels are two 32x48 ones: compositing once and sampling twice is
     * both the cheaper and the more obviously correct order.
     */
    private static @Nullable Panel panel(final ResourceManager manager, final ClothValue value) {
        final boolean banner = value.cloth().value().sheet() == BannerFitting.Sheet.BANNER;
        final int[] box = banner ? FLAG : PLATE;
        final int width = box[0];
        final int height = box[1];
        final int[] pixels = new int[width * height];

        // The base pass first, then one pass per layer, exactly as vanilla draws a banner - except
        // that here they are composited rather than submitted, and the result is a texture.
        boolean any = pass(manager, pixels, width, height, box,
            banner ? Sheets.BANNER_PATTERN_BASE : Sheets.SHIELD_PATTERN_BASE, value.base());
        final BannerPatternLayers layers = value.patterns();
        for (final BannerPatternLayers.Layer layer : layers.layers()) {
            any |= pass(manager, pixels, width, height, box,
                banner ? Sheets.getBannerSprite(layer.pattern()) : Sheets.getShieldSprite(layer.pattern()),
                layer.color());
        }
        return any ? new Panel(pixels, width, height) : null;
    }

    /**
     * One pass of one sprite in one colour, over the north face of the box the sprite was painted
     * for - the face whose design is the right way round.
     *
     * <p>BOTH panels take this same face. A banner's back is mirrored because a banner is one sheet
     * of cloth read from behind; a tabard is two panels, each read from outside, and heraldry on both
     * of them faces the viewer.
     *
     * <p><b>Only the sprite's ALPHA is read.</b> Vanilla multiplies the sprite's colour by the dye,
     * which is right for a flag - the sprite carries the cloth's own weave, and the base sprite
     * carries how dark that cloth is. Here it is wrong twice over: the shading of this garment is
     * already the mask's and the armor's, and a third source fighting them is not shading but noise;
     * and the two base sprites disagree about what white is - a banner's is 224 grey and a shield's
     * is 145, so sampling the shield sheet would make every garment a shade of slate. Measured over
     * the pattern sprites, dropping the colour costs nothing anyway: every one of them lives between
     * luma 219 and 255, and everything that actually varies - gradients, soft edges - is in the alpha
     * this still blends by.
     *
     * @return whether the sprite was there to read at all.
     */
    private static boolean pass(
        final ResourceManager manager,
        final int[] pixels,
        final int width,
        final int height,
        final int[] box,
        final SpriteId spriteId,
        final DyeColor colour
    ) {
        final Image sprite = image(manager, spriteId.texture().withPath(path -> "textures/" + path + ".png"));
        if (sprite == null) {
            return false;
        }
        // The face rectangle on the sprite's own sheet: the net puts the north face one depth in from
        // the left and one down from the top. Scaled off 64 so a pack's larger sprite still works.
        final float unit = sprite.width() / SPRITE_SHEET;
        final int x0 = Math.round(box[2] * unit);
        final int y0 = Math.round(box[2] * unit);
        final int faceWidth = Math.round(box[0] * unit);
        final int faceHeight = Math.round(box[1] * unit);
        final int tint = colour.getTextureDiffuseColor() & 0x00FFFFFF;

        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                final int sx = x0 + x * faceWidth / width;
                final int sy = y0 + y * faceHeight / height;
                if (sx < 0 || sy < 0 || sx >= sprite.width() || sy >= sprite.height()) {
                    continue;
                }
                final int alpha = ARGB.alpha(sprite.pixels()[sy * sprite.width() + sx]);
                if (alpha == 0) {
                    continue;
                }
                pixels[y * width + x] = alpha == 255
                    ? 0xFF000000 | tint
                    : 0xFF000000 | blend(pixels[y * width + x], tint, alpha);
            }
        }
        return true;
    }

    /** The composited design, and where on the net it is stretched to. */
    private record Panel(int[] pixels, int width, int height) {
        /**
         * The design at a point on the 64x32 net, or {@code fallback} where that point is not on one
         * of the two panels - the sides, the shoulders and the hem underside, which carry the base
         * colour alone.
         */
        int sample(final float gx, final float gy, final int fallback) {
            final int[] rect = ClothTextureManager.within(FRONT, gx, gy) ? FRONT
                : ClothTextureManager.within(BACK, gx, gy) ? BACK : null;
            if (rect == null) {
                return fallback;
            }
            final int px = clamp((int) ((gx - rect[0]) / rect[2] * this.width), this.width - 1);
            final int py = clamp((int) ((gy - rect[1]) / rect[3] * this.height), this.height - 1);
            final int pixel = this.pixels[py * this.width + px];
            return pixel == 0 ? fallback : pixel & 0x00FFFFFF;
        }

        private static int clamp(final int value, final int max) {
            return Math.max(0, Math.min(max, value));
        }
    }

    // ---- plumbing -------------------------------------------------------------------------------

    /** An image as the bake wants it: pixels in a flat array, so nothing is read twice. */
    private record Image(int[] pixels, int width, int height) {}

    /**
     * Where a bake is registered. The design is HASHED rather than spelled out: a banner is a colour
     * and up to six patterns, which is not a path, and two different designs must not collide. The
     * garment, the sheet and the armor stay readable in the path, which is what a log line needs.
     */
    private static Identifier bakedId(final ClothValue value, final String sheetName, final Identifier target) {
        final StringBuilder key = new StringBuilder(target.toString()).append('|').append(value.base().getName());
        for (final BannerPatternLayers.Layer layer : value.patterns().layers()) {
            key.append('|')
                .append(layer.pattern().getRegisteredName())
                .append('=')
                .append(layer.color().getName());
        }
        final Identifier cloth = value.cloth().value().assetId();
        return Identifier.fromNamespaceAndPath(
            ArmorPieces.MOD_ID,
            DIRECTORY + "/" + cloth.getNamespace() + "/" + cloth.getPath() + "/" + sheetName + "/"
                + UUID.nameUUIDFromBytes(key.toString().getBytes(StandardCharsets.UTF_8)) + ".png");
    }

    private static @Nullable Image image(final ResourceManager manager, final Identifier id) {
        NativeImage image = null;
        try {
            image = readImage(manager, id);
            if (image == null) {
                return null;
            }
            final int width = image.getWidth();
            final int height = image.getHeight();
            final int[] pixels = new int[width * height];
            for (int y = 0; y < height; y++) {
                for (int x = 0; x < width; x++) {
                    pixels[y * width + x] = image.getPixel(x, y);
                }
            }
            return new Image(pixels, width, height);
        } finally {
            close(image);
        }
    }

    private static @Nullable NativeImage readImage(final ResourceManager manager, final Identifier id) {
        final Optional<Resource> resource = manager.getResource(id);
        if (resource.isEmpty()) {
            return null;
        }
        try (InputStream stream = resource.get().open()) {
            return NativeImage.read(stream);
        } catch (final IOException e) {
            ArmorPieces.LOGGER.error("[Armor Pieces] Could not read {}", id, e);
            return null;
        }
    }

    private static void close(final @Nullable NativeImage image) {
        if (image != null) {
            image.close();
        }
    }

    private static int clamp(final int value) {
        return Math.max(0, Math.min(255, value));
    }

    /** {@code over} at {@code alpha} on top of {@code under}, both opaque RGB. */
    private static int blend(final int under, final int over, final int alpha) {
        final int keep = 255 - alpha;
        return (ARGB.red(over) * alpha + ARGB.red(under) * keep) / 255 << 16
            | (ARGB.green(over) * alpha + ARGB.green(under) * keep) / 255 << 8
            | (ARGB.blue(over) * alpha + ARGB.blue(under) * keep) / 255;
    }

    private void releaseBaked() {
        final Minecraft client = Minecraft.getInstance();
        final List<Identifier> registered = new ArrayList<>(this.resolved.keySet());
        for (final Identifier id : registered) {
            if (Boolean.TRUE.equals(this.resolved.get(id))) {
                client.getTextureManager().release(id);
            }
        }
        this.resolved.clear();
    }
}
