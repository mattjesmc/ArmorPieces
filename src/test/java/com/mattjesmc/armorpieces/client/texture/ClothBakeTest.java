package com.mattjesmc.armorpieces.client.texture;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.mattjesmc.armorpieces.GameBootstrap;
import com.mattjesmc.armorpieces.client.texture.ClothTextureManager.Image;
import com.mattjesmc.armorpieces.client.texture.ClothTextureManager.Panel;
import com.mattjesmc.armorpieces.cloth.Cloth;
import com.mattjesmc.armorpieces.cloth.ClothValue;
import com.mattjesmc.armorpieces.data.ShippedData;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.fitting.builtin.BannerFitting;
import com.mattjesmc.armorpieces.skin.SkinBake;
import com.mojang.blaze3d.platform.NativeImage;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Stream;
import javax.imageio.ImageIO;
import net.minecraft.client.renderer.Sheets;
import net.minecraft.client.resources.model.sprite.SpriteId;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.packs.PackLocationInfo;
import net.minecraft.server.packs.PackResources;
import net.minecraft.server.packs.PackType;
import net.minecraft.server.packs.PathPackResources;
import net.minecraft.server.packs.repository.PackSource;
import net.minecraft.server.packs.resources.MultiPackResourceManager;
import net.minecraft.server.packs.resources.Resource;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.util.ARGB;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.block.entity.BannerPattern;
import net.minecraft.world.level.block.entity.BannerPatternLayers;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

/**
 * The third texture manager's arithmetic: what a piece of armor with a garment on it actually looks
 * like, texel by texel.
 *
 * <p>{@code DecorationBakeTest} closed the same question for a part - one greyscale master through a
 * trim palette - and this is its counterpart for cloth, which is the only one of the three bakes
 * that does not start from a master of its own. A cloth ships a CUT MASK (alpha says where the
 * garment is, red says how it folds), the colour comes off a banner the player made at a loom, and
 * what the armor underneath supplies is neither the silhouette nor the colour but the LIGHT. Four
 * tier-3 frames photographed that - tunic and tabard, over plain iron and over a skin - and nothing
 * below them had ever asked a question about it.
 *
 * <p>The rules being pinned here are the ones a frame cannot tell you it has broken, because a
 * frame only ever says "something moved":
 *
 * <ul>
 *   <li><b>the cut is judged per FACE, not per texel.</b> A garment is worn on the armor, so where
 *       the armor paints nothing there is nothing to hang it on - except on a face the armor uses
 *       nowhere at all, which is the top of the chest box on every vanilla material, and which is
 *       exactly where a tunic's shoulders and a tabard's straps live. Get this backwards and a
 *       tabard loses its straps, or a hem grows over a hole in the plate;</li>
 *   <li><b>only the sprite's ALPHA is read.</b> Vanilla multiplies a banner sprite by its dye; here
 *       the shading is already the mask's and the armor's, and the two base sprites do not even
 *       agree what white is - a banner's is 224 grey and a shield's 145 - so sampling the colour
 *       would make every garment a shade of slate;</li>
 *   <li><b>the value is the mask's own plus the armor's light</b>, through the same three-stop ramp
 *       a dyed inlay goes through, which is what makes a dyed cloth and a dyed fitting beside it
 *       shade identically;</li>
 *   <li><b>a bake is filed under a HASH of the design</b>, because a banner is a colour and up to
 *       six patterns and that is not a path - and two designs sharing a key would put one player's
 *       heraldry on another's back.</li>
 * </ul>
 *
 * <p>Everything here runs on images the test paints itself, except the sweep at the end, which
 * composites every garment the mod actually ships. There is no Python port to hold this to - the
 * site and the Blockbench plugin preview parts and skins, not garments - so the reference is the
 * rules, stated one per test.
 */
class ClothBakeTest {
    /**
     * The six faces of the torso box on vanilla's 64x32 armor net, in the order
     * {@link ClothTextureManager#paintedFaces} reports them.
     *
     * <p>Restated here rather than read off the class under test on purpose: a test that asks the
     * mod where its own faces are cannot notice the day they move.
     */
    private static final int[] FRONT = {20, 20, 8, 12};
    private static final int[] BACK = {32, 20, 8, 12};
    private static final int[] LEFT = {28, 20, 4, 12};
    private static final int[] RIGHT = {16, 20, 4, 12};
    private static final int[] TOP = {20, 16, 8, 4};
    private static final int[] BOTTOM = {28, 16, 8, 4};

    /** The net every mask and every armor texture here is stated on. */
    private static final int GRID_WIDTH = 64;
    private static final int GRID_HEIGHT = 32;

    /**
     * A 64-wide base is brought up to 256, so one texel of the net is a 4x4 block of the bake. Every
     * assertion below is written on the net and reads the top-left corner of its block.
     */
    private static final int SCALE = 4;

    @BeforeAll
    static void world() {
        // First line of the class, and its only job is to be first: an argument is evaluated before
        // the call it is passed to, so a fixture method that initialises Items or a registry on its
        // way past would fail the whole JVM's class initialisation instead of one test.
        GameBootstrap.content();
    }

    // ---- the cut ----------------------------------------------------------------------------------

    /**
     * Where the mask is transparent the armor is exactly what it was - which is what makes the
     * layering free: the garment is composited into the texture the layer was already going to draw
     * with, so there is no second pass and nothing to order.
     */
    @Test
    void whereTheMaskIsTransparentTheArmorIsExactlyWhatItWas() {
        final Image armor = plate();
        try (NativeImage mask = mask(cut -> {
        })) {
            final NativeImage out = ClothTextureManager.composite(mask, armor, armor, null, 0xFF0000);
            try (out) {
                for (int gy = 0; gy < GRID_HEIGHT; gy++) {
                    for (int gx = 0; gx < GRID_WIDTH; gx++) {
                        assertEquals(armor.pixels()[gy * GRID_WIDTH + gx], at(out, gx, gy),
                            "a garment that covers nothing changes nothing, at " + gx + "," + gy);
                    }
                }
            }
        }
    }

    /**
     * The armor's own texels are upsampled NEAREST, so the plate still reads at vanilla resolution
     * while the design gets four times the room. A shield pattern is painted for 12x22 and the chest
     * front is 8x12: on the vanilla grid a charge turns to mush.
     */
    @Test
    void theArmorIsUpsampledNearestAndTheDesignGetsTheRoom() {
        final Image armor = plate();
        try (NativeImage mask = mask(cut -> {
        })) {
            try (NativeImage out = ClothTextureManager.composite(mask, armor, armor, null, 0xFF0000)) {
                assertEquals(GRID_WIDTH * SCALE, out.getWidth(), "a 64-wide armor texture bakes at 256");
                assertEquals(GRID_HEIGHT * SCALE, out.getHeight(), "and keeps its aspect");
                final int texel = armor.pixels()[20 * GRID_WIDTH + 20];
                for (int dy = 0; dy < SCALE; dy++) {
                    for (int dx = 0; dx < SCALE; dx++) {
                        assertEquals(texel, out.getPixel(20 * SCALE + dx, 20 * SCALE + dy),
                            "one armor texel is one 4x4 block, not an interpolation of its neighbours");
                    }
                }
            }
        }
        // A texture that is already at the bake's width is left at its own resolution rather than
        // being blown up past it - a high-resolution pack pays nothing here.
        final Image wide = new Image(new int[256 * 128], 256, 128);
        try (NativeImage mask = mask(cut -> {
        })) {
            try (NativeImage out = ClothTextureManager.composite(mask, wide, null, null, 0xFF0000)) {
                assertEquals(256, out.getWidth(), "a 256-wide armor texture is baked as it is");
            }
        }
    }

    /**
     * On a face the armor USES, the garment stops where the armor does. That is what gives the
     * neck's notch and the hem's taper without counting rows into a mask by hand - and it gives them
     * from whatever the piece actually is, vanilla's cut or a skin's, which are not the same cut.
     */
    @Test
    void onAFaceTheArmorUsesTheGarmentStopsWhereTheArmorDoes() {
        final int[] pixels = platePixels();
        // A hole in the middle of the breast - a neckline, or a skin that cuts higher than vanilla.
        pixels[22 * GRID_WIDTH + 23] = 0;
        final Image armor = new Image(pixels, GRID_WIDTH, GRID_HEIGHT);
        try (NativeImage mask = mask(cut -> {
            fill(cut, FRONT, 0xFF808080);
        })) {
            try (NativeImage out = ClothTextureManager.composite(mask, armor, armor, null, 0xFF0000)) {
                assertEquals(0, at(out, 23, 22),
                    "there is nothing there to hang a garment on, so the garment stops");
                assertNotEquals(0, at(out, 24, 22), "and hangs on the plate beside the hole");
            }
        }
    }

    /**
     * On a face the armor uses NOWHERE the rule is off, and deliberately. Vanilla paints nothing on
     * the top of the chest box - a breastplate has no lid - and a tunic's shoulders and a tabard's
     * straps live exactly there. An empty face is not a hole to respect, it is room to use.
     *
     * <p>This is the one that a per-texel clip would get wrong invisibly: the straps would simply
     * not be there, and a frame diff would call it "something moved".
     */
    @Test
    void onAFaceTheArmorLeavesEmptyTheGarmentDrapesOverIt() {
        final Image armor = plate();
        try (NativeImage mask = mask(cut -> {
            fill(cut, TOP, 0xFF808080);
        })) {
            try (NativeImage out = ClothTextureManager.composite(mask, armor, armor, null, 0xFF0000)) {
                assertNotEquals(0, at(out, 21, 17), "the shoulders carry the garment over an empty lid");
            }
        }
        // And the rule is about the face, not about the texel: with the lid painted, the same mask
        // over the same hole in it is clipped like anywhere else.
        final int[] painted = platePixels();
        fill(painted, TOP, 0xFF606060);
        painted[17 * GRID_WIDTH + 21] = 0;
        final Image lidded = new Image(painted, GRID_WIDTH, GRID_HEIGHT);
        try (NativeImage mask = mask(cut -> {
            fill(cut, TOP, 0xFF808080);
        })) {
            try (NativeImage out = ClothTextureManager.composite(mask, lidded, lidded, null, 0xFF0000)) {
                assertEquals(0, at(out, 21, 17), "a face the armor does use is clipped to it");
            }
        }
    }

    /** Off the torso box the garment is trimmed to whatever is there - a mask that strays onto an
     * arm is trimmed to the sleeve. */
    @Test
    void offTheTorsoBoxTheGarmentIsTrimmedToWhatIsThere() {
        final Image armor = plate();
        try (NativeImage mask = mask(cut -> {
            // (48, 24) is on the arm box, which this armor paints nothing on at all.
            cut[24 * GRID_WIDTH + 48] = 0xFF808080;
        })) {
            try (NativeImage out = ClothTextureManager.composite(mask, armor, armor, null, 0xFF0000)) {
                assertEquals(0, at(out, 48, 24), "a stray mask texel off the torso finds nothing to hang on");
            }
        }
    }

    /**
     * With no armor to measure - a piece whose material has no texture this manager could find - the
     * garment is drawn with its own folds and no armor form, rather than not at all.
     */
    @Test
    void withNoArmorTheGarmentIsItsOwnFoldsAlone() {
        final Image armor = plate();
        try (NativeImage mask = mask(cut -> {
            fill(cut, TOP, 0xFF808080);
            cut[24 * GRID_WIDTH + 48] = 0xFF808080;
        })) {
            try (NativeImage out = ClothTextureManager.composite(mask, armor, null, null, 0xFF0000)) {
                assertEquals(DecorationPalette.ofStaticColour(0xFF0000).rgb(0x80), at(out, 21, 17),
                    "the mask's own value, and nothing added to it");
                assertNotEquals(0, at(out, 48, 24), "and no clip, because there is nothing to clip to");
            }
        }
    }

    /** The six faces, as {@link ClothTextureManager#paintedFaces} reports them. */
    @Test
    void theFacesReportedAreTheOnesTheArmorPaintsAnythingOnAtAll() {
        final int[] pixels = new int[GRID_WIDTH * GRID_HEIGHT];
        fill(pixels, FRONT, 0xFF808080);
        // One texel is enough to make a face used - the rule is "paints anything at all".
        pixels[BOTTOM[1] * GRID_WIDTH + BOTTOM[0]] = 0xFF808080;
        assertArrayEquals(
            new boolean[] {true, false, false, false, false, true},
            ClothTextureManager.paintedFaces(new Image(pixels, GRID_WIDTH, GRID_HEIGHT)),
            "front, back, left, right, top, bottom");
    }

    /** A point on no face of the torso box is clipped whatever the armor paints. */
    @Test
    void aPointOnNoFaceIsClippedAnyway() {
        final boolean[] nothingPainted = new boolean[6];
        assertTrue(ClothTextureManager.clipped(nothingPainted, 48.0F, 24.0F), "the arm box");
        assertTrue(ClothTextureManager.clipped(nothingPainted, 4.0F, 4.0F), "the head");
        assertEquals(false, ClothTextureManager.clipped(nothingPainted, 21.0F, 17.0F),
            "the top of the chest box, which this armor uses nowhere");
    }

    // ---- the value --------------------------------------------------------------------------------

    /**
     * The garment's shade is the mask's own value plus the armor's lighting at that texel, and the
     * colour is that shade through {@link DecorationPalette#ofStaticColour} - the same three-stop
     * ramp a dye fitting and a horn's ivory go through, which is why a dyed cloth and a dyed inlay
     * beside it shade identically.
     */
    @Test
    void theValueIsTheMasksOwnPlusTheArmorsLight() {
        final Image armor = plate();
        final byte[] light = SkinBake.lightmap(armor.pixels(), ClothTextureManager.ARMOR_LIGHT);
        try (NativeImage mask = mask(cut -> {
            fill(cut, FRONT, 0xFF808080);
        })) {
            try (NativeImage out = ClothTextureManager.composite(mask, armor, armor, null, 0xC08040)) {
                final DecorationPalette ramp = DecorationPalette.ofStaticColour(0xC08040);
                int lit = 0;
                for (int gy = FRONT[1]; gy < FRONT[1] + FRONT[3]; gy++) {
                    for (int gx = FRONT[0]; gx < FRONT[0] + FRONT[2]; gx++) {
                        final int shade = 0x80 + light[gy * GRID_WIDTH + gx];
                        assertEquals(ramp.rgb(shade) | 0xFF000000, at(out, gx, gy),
                            "the ramp at the mask's value plus the armor's light, at " + gx + "," + gy);
                        if (light[gy * GRID_WIDTH + gx] != 0) {
                            lit++;
                        }
                    }
                }
                assertTrue(lit > 0, "the armor under this test has to actually vary, or it proves nothing");
            }
        }
    }

    /**
     * The shade is clamped rather than allowed to wrap. A white mask over the brightest rivet on a
     * gold plate is a garment in the light, not a black one.
     */
    @Test
    void theValueIsClampedAtBothEnds() {
        final int[] pixels = new int[GRID_WIDTH * GRID_HEIGHT];
        fill(pixels, FRONT, 0xFF101010);
        // One very bright texel and one very dark one, so the lightmap has something to say.
        pixels[20 * GRID_WIDTH + 20] = 0xFFFFFFFF;
        pixels[21 * GRID_WIDTH + 20] = 0xFF000000;
        final Image armor = new Image(pixels, GRID_WIDTH, GRID_HEIGHT);
        try (NativeImage mask = mask(cut -> {
            cut[20 * GRID_WIDTH + 20] = 0xFFFFFFFF;
            cut[20 * GRID_WIDTH + 21] = 0xFF000000;
        })) {
            try (NativeImage out = ClothTextureManager.composite(mask, armor, armor, null, 0xC08040)) {
                final DecorationPalette ramp = DecorationPalette.ofStaticColour(0xC08040);
                assertEquals(ramp.rgb(255) | 0xFF000000, at(out, 20, 20), "the light end holds at 255");
                assertEquals(ramp.rgb(0) | 0xFF000000, at(out, 21, 20), "the dark end holds at 0");
            }
        }
    }

    /**
     * Every texel the garment covers comes out opaque, whatever was under it. The bake is what the
     * armor layer draws with, and a half-transparent garment texel would show the body through the
     * chestplate.
     */
    @Test
    void everyGarmentTexelIsOpaque() {
        // A base with nothing in it at all: the garment still has to be solid where it lands.
        final Image empty = new Image(new int[GRID_WIDTH * GRID_HEIGHT], GRID_WIDTH, GRID_HEIGHT);
        try (NativeImage mask = mask(cut -> {
            fill(cut, FRONT, 0xFF000000);
        })) {
            try (NativeImage out = ClothTextureManager.composite(mask, empty, null, null, 0x000000)) {
                assertEquals(255, ARGB.alpha(at(out, 21, 21)),
                    "a garment texel is opaque even where its colour is black and the armor is a hole");
            }
        }
    }

    // ---- the colour -------------------------------------------------------------------------------

    /**
     * The design is carried on the two torso panels and nowhere else: the flanks, the shoulders and
     * the hem's underside take the base dye alone, because a charge stretched round a rib is a
     * smear.
     */
    @Test
    void theTwoPanelsCarryTheDesignAndEverythingElseTheBaseDye() {
        final Panel panel = solid(0x00FF00);
        try (NativeImage mask = mask(cut -> {
            fill(cut, FRONT, 0xFF808080);
            fill(cut, BACK, 0xFF808080);
            fill(cut, LEFT, 0xFF808080);
            fill(cut, TOP, 0xFF808080);
        })) {
            try (NativeImage out = ClothTextureManager.composite(mask, plate(), null, panel, 0xFF0000)) {
                final int design = DecorationPalette.ofStaticColour(0x00FF00).rgb(0x80) | 0xFF000000;
                final int dye = DecorationPalette.ofStaticColour(0xFF0000).rgb(0x80) | 0xFF000000;
                assertEquals(design, at(out, 21, 21), "the front panel");
                assertEquals(design, at(out, 33, 21), "the back panel, the same way round as the front");
                assertEquals(dye, at(out, 29, 21), "a flank");
                assertEquals(dye, at(out, 21, 17), "a shoulder");
            }
        }
    }

    /**
     * Where the design has a hole the base dye shows through. A banner's own base pass fills the
     * flag, so this is what a pack's half-painted sprite gets: cloth, not a window.
     */
    @Test
    void aHoleInTheDesignFallsBackToTheBaseDye() {
        final int[] pixels = new int[12 * 22];
        pixels[0] = 0xFF00FF00;
        final Panel panel = new Panel(pixels, 12, 22);
        try (NativeImage mask = mask(cut -> {
            fill(cut, FRONT, 0xFF808080);
        })) {
            try (NativeImage out = ClothTextureManager.composite(mask, plate(), null, panel, 0xFF0000)) {
                assertEquals(DecorationPalette.ofStaticColour(0x00FF00).rgb(0x80) | 0xFF000000,
                    at(out, 20, 20), "the one painted corner of the design");
                assertEquals(DecorationPalette.ofStaticColour(0xFF0000).rgb(0x80) | 0xFF000000,
                    at(out, 26, 26), "and the base dye everywhere it did not reach");
            }
        }
    }

    /** The design is stretched over the panel, so a 12x22 sprite covers the whole 8x12 face. */
    @Test
    void theDesignIsStretchedOverTheWholePanel() {
        final int[] pixels = new int[12 * 22];
        // The right-hand half green, the left-hand half blue: the seam has to land inside the face.
        for (int y = 0; y < 22; y++) {
            for (int x = 0; x < 12; x++) {
                pixels[y * 12 + x] = x < 6 ? 0xFF0000FF : 0xFF00FF00;
            }
        }
        final Panel panel = new Panel(pixels, 12, 22);
        try (NativeImage mask = mask(cut -> {
            fill(cut, FRONT, 0xFF808080);
        })) {
            try (NativeImage out = ClothTextureManager.composite(mask, plate(), null, panel, 0xFF0000)) {
                assertEquals(DecorationPalette.ofStaticColour(0x0000FF).rgb(0x80) | 0xFF000000,
                    at(out, 20, 21), "the left of the face is the left of the design");
                assertEquals(DecorationPalette.ofStaticColour(0x00FF00).rgb(0x80) | 0xFF000000,
                    at(out, 27, 21), "and the right is the right - not one texel of it repeated");
            }
        }
    }

    // ---- the design -------------------------------------------------------------------------------

    /**
     * Only the sprite's ALPHA is read. Vanilla multiplies a banner sprite by the dye, which is right
     * for a flag - the sprite carries the cloth's own weave - and wrong twice over here: the shading
     * of this garment is already the mask's and the armor's, and the two base sprites disagree about
     * what white is, a banner's being 224 grey and a shield's 145.
     */
    @Test
    void onlyTheSpritesAlphaIsRead() {
        final int[] bright = new int[12 * 22];
        final int[] dim = new int[12 * 22];
        ClothTextureManager.paint(bright, 12, 22, plateBox(), sprite(0xFFFFFFFF), DyeColor.RED);
        ClothTextureManager.paint(dim, 12, 22, plateBox(), sprite(0xFF404040), DyeColor.RED);
        assertArrayEquals(bright, dim, "a grey sprite and a white one of the same shape are one design");
        assertEquals(0xFF000000 | (DyeColor.RED.getTextureDiffuseColor() & 0x00FFFFFF), bright[0],
            "and what is painted is the dye, not the sprite");
    }

    /**
     * The face taken off the sprite sheet is the NORTH one - the face whose design is the right way
     * round - which the net puts one depth in from the left and one down from the top.
     *
     * <p>Both panels take that same face. A banner's back is mirrored because a banner is one sheet
     * of cloth read from behind; a tabard is two panels, each read from outside, and heraldry on
     * both of them faces the viewer.
     */
    @Test
    void theNorthFaceIsTheOneTaken() {
        final int[] pixels = new int[12 * 22];
        ClothTextureManager.paint(pixels, 12, 22, plateBox(), sprite(0xFFFFFFFF), DyeColor.RED);
        for (final int pixel : pixels) {
            assertNotEquals(0, pixel, "the north face is opaque all over, so the design is too");
        }
        // The same sheet with the north face alone erased: a pass reading anywhere else would still
        // find plenty of paint, and this is the assertion that says it does not.
        final Image erased = sprite(0xFFFFFFFF);
        for (int y = 1; y < 23; y++) {
            for (int x = 1; x < 13; x++) {
                erased.pixels()[y * 64 + x] = 0;
            }
        }
        final int[] nothing = new int[12 * 22];
        ClothTextureManager.paint(nothing, 12, 22, plateBox(), erased, DyeColor.RED);
        assertArrayEquals(new int[12 * 22], nothing, "and nothing outside it is ever sampled");
    }

    /** A pack's bigger sprite sheet is scaled off 64, so a 128-wide sheet paints the same design. */
    @Test
    void aBiggerPacksSpriteIsScaledOffSixtyFour() {
        final int[] small = new int[12 * 22];
        final int[] large = new int[12 * 22];
        ClothTextureManager.paint(small, 12, 22, plateBox(), sprite(0xFFFFFFFF), DyeColor.RED);

        final int[] pixels = new int[128 * 128];
        for (int y = 2; y < 46; y++) {
            for (int x = 2; x < 26; x++) {
                pixels[y * 128 + x] = 0xFFFFFFFF;
            }
        }
        ClothTextureManager.paint(large, 12, 22, plateBox(), new Image(pixels, 128, 128), DyeColor.RED);
        assertArrayEquals(small, large, "the same design at twice the resolution is the same design");
    }

    /**
     * A soft edge blends onto whatever the earlier pass left there, and the more opaque it is the
     * more of the new colour it takes. This is the only place a garment's colour is mixed at all -
     * everything else in this class is one colour or another.
     */
    @Test
    void aSoftEdgeBlendsOntoWhatIsAlreadyThere() {
        final int under = DyeColor.BLUE.getTextureDiffuseColor() & 0x00FFFFFF;
        final int over = DyeColor.YELLOW.getTextureDiffuseColor() & 0x00FFFFFF;

        final int half = pass(under, 128, DyeColor.YELLOW);
        final int most = pass(under, 220, DyeColor.YELLOW);
        for (final String channel : List.of("red", "green", "blue")) {
            final int shift = "red".equals(channel) ? 16 : "green".equals(channel) ? 8 : 0;
            final int u = (under >> shift) & 0xFF;
            final int o = (over >> shift) & 0xFF;
            final int h = (half >> shift) & 0xFF;
            final int m = (most >> shift) & 0xFF;
            assertTrue(h >= Math.min(u, o) && h <= Math.max(u, o),
                "a half-opaque edge is between the two colours in " + channel);
            assertTrue(Math.abs(m - o) <= Math.abs(h - o),
                "and a nearly opaque one is nearer the new colour in " + channel);
        }
        assertEquals(0xFF000000 | over, pass(under, 255, DyeColor.YELLOW),
            "a fully opaque texel replaces outright rather than blending with itself");
        assertEquals(0xFF000000 | under, pass(under, 0, DyeColor.YELLOW),
            "and a transparent one is not a pass at all");
    }

    /**
     * A garment samples the sprite sheet its cloth NAMES, and the design is composited once into the
     * rectangle those sprites are painted for: a flag is 20x40 and a shield's plate 12x22.
     *
     * <p>Done in pattern space rather than per output texel because a design is a handful of passes
     * over a small rect and the panels are two big ones - compositing once and sampling twice is
     * both the cheaper and the more obviously correct order.
     */
    @Test
    void aGarmentSamplesTheSheetItsClothNames(@TempDir final Path root) throws IOException {
        sprite(root, Sheets.BANNER_PATTERN_BASE, 0xFF00FF00);
        sprite(root, Sheets.SHIELD_PATTERN_BASE, 0xFF0000FF);
        final ResourceManager manager = new MultiPackResourceManager(
            PackType.CLIENT_RESOURCES, List.of(pack(root)));

        final Panel flag = ClothTextureManager.panel(
            manager, bare(direct("a_pack", "cape", BannerFitting.Sheet.BANNER)));
        assertNotNull(flag, "a banner-sheet garment reads the banner sprites");
        assertEquals(20, flag.width(), "a flag is 20 wide");
        assertEquals(40, flag.height(), "and 40 tall");

        final Panel plate = ClothTextureManager.panel(manager, bare(cloth("tunic")));
        assertNotNull(plate, "a shield-sheet garment reads the shield sprites");
        assertEquals(12, plate.width(), "a shield's plate is 12 wide");
        assertEquals(22, plate.height(), "and 22 tall");
    }

    /**
     * The base pass first and one pass per layer over it, exactly as vanilla draws a banner - except
     * that here they are composited rather than submitted, and the result is a texture.
     */
    @Test
    void theBasePassIsFirstAndEveryLayerGoesOverIt(@TempDir final Path root) throws IOException {
        // Not simply the first pattern in the registry: vanilla's own "base" pattern draws with the
        // base sprite, so a layer of it would be written to the same file as the base pass and this
        // would be asking one sprite two questions.
        final Holder.Reference<BannerPattern> pattern = ShippedData.mod().registries()
            .lookupOrThrow(Registries.BANNER_PATTERN).listElements()
            .filter(entry -> !Sheets.getShieldSprite(entry).texture()
                .equals(Sheets.SHIELD_PATTERN_BASE.texture()))
            .findFirst().orElseThrow();
        sprite(root, Sheets.SHIELD_PATTERN_BASE, 0xFFFFFFFF);
        // The layer covers the left half of the plate's north face and nothing else.
        sprite(root, Sheets.getShieldSprite(pattern), 0xFFFFFFFF, 1, 1, 6, 22);
        final ResourceManager manager = new MultiPackResourceManager(
            PackType.CLIENT_RESOURCES, List.of(pack(root)));

        final Panel panel = ClothTextureManager.panel(manager, new ClothValue(
            cloth("tunic"), DyeColor.YELLOW,
            new BannerPatternLayers(List.of(new BannerPatternLayers.Layer(pattern, DyeColor.BLACK)))));

        assertNotNull(panel);
        assertEquals(0xFF000000 | (DyeColor.BLACK.getTextureDiffuseColor() & 0x00FFFFFF),
            panel.pixels()[0], "the layer is painted over the base where it reaches");
        assertEquals(0xFF000000 | (DyeColor.YELLOW.getTextureDiffuseColor() & 0x00FFFFFF),
            panel.pixels()[11], "and the base colour is what is left everywhere else");
    }

    /**
     * A design with no sprites behind it at all is NO panel, not an empty one - and a garment with no
     * panel is drawn in its base dye rather than in whatever a blank rectangle would have been.
     */
    @Test
    void aDesignWithNoSpritesToReadIsNoPanel(@TempDir final Path root) throws IOException {
        Files.createDirectories(root.resolve("assets"));
        final ResourceManager manager = new MultiPackResourceManager(
            PackType.CLIENT_RESOURCES, List.of(pack(root)));
        assertNull(ClothTextureManager.panel(manager, bare(cloth("tunic"))),
            "no base sprite, no design");
    }

    // ---- where a bake is filed ---------------------------------------------------------------------

    /**
     * The baked id is the cache key, so two designs sharing one would put somebody else's heraldry
     * on this player's back - and it is also a resource location, which refuses most punctuation. A
     * design is a colour and up to six patterns, which is not a path, so it is hashed; the garment,
     * the sheet and the armor stay readable because that is what a log line needs.
     */
    @Test
    void everyBakeIsFiledSomewhereLegalAndSomewhereOfItsOwn() {
        final List<Holder<Cloth>> garments = List.of(cloth("tunic"), cloth("tabard"));
        final List<BannerPatternLayers> designs = designs();
        final List<Identifier> targets = List.of(
            Identifier.parse("minecraft:textures/entity/equipment/humanoid/iron.png"),
            Identifier.parse("minecraft:textures/entity/equipment/humanoid/gold.png"),
            Identifier.parse("armorpieces:textures/entity/skin/baked/plate_iron.png"));

        final Set<Identifier> seen = new HashSet<>();
        final List<String> collisions = new ArrayList<>();
        for (final Holder<Cloth> garment : garments) {
            for (final DyeColor base : List.of(DyeColor.RED, DyeColor.BLUE)) {
                for (final BannerPatternLayers design : designs) {
                    for (final Identifier target : targets) {
                        for (final String sheet : List.of("humanoid", "humanoid_leggings")) {
                            // Illegal punctuation throws out of here rather than asserting.
                            final Identifier baked = ClothTextureManager.bakedId(
                                new ClothValue(garment, base, design), sheet, target);
                            if (!seen.add(baked)) {
                                collisions.add(baked + " is claimed twice");
                            }
                        }
                    }
                }
            }
        }
        assertTrue(collisions.isEmpty(), () -> String.join("\n  ", collisions));

        final ClothValue value = new ClothValue(garments.getFirst(), DyeColor.RED, designs.getLast());
        final Identifier iron = Identifier.parse("minecraft:textures/entity/equipment/humanoid/iron.png");
        assertEquals(
            ClothTextureManager.bakedId(value, "humanoid", iron),
            ClothTextureManager.bakedId(value, "humanoid", iron),
            "the same garment is filed in the same place, or nothing is ever cached");
    }

    /**
     * Two packs' garments of one name are two bakes. The design is hashed but the garment is not:
     * its whole id is in the path, namespace and all.
     */
    @Test
    void twoPacksGarmentsOfOneNameAreTwoBakes() {
        final Identifier iron = Identifier.parse("minecraft:textures/entity/equipment/humanoid/iron.png");
        assertNotEquals(
            ClothTextureManager.bakedId(bare(direct("armorpieces", "tunic")), "humanoid", iron),
            ClothTextureManager.bakedId(bare(direct("armorpieces_hunt", "tunic")), "humanoid", iron),
            "a pack that ships its own tunic does not take over the mod's");
    }

    // ---- every garment the mod ships -----------------------------------------------------------------

    static Stream<Arguments> garments() {
        final List<Arguments> cases = new ArrayList<>();
        for (final Holder.Reference<Cloth> entry : clothRegistry().listElements().toList()) {
            for (final String sheet : List.of("humanoid", "humanoid_leggings")) {
                cases.add(Arguments.of(entry.key().identifier() + " " + sheet, entry, sheet));
            }
        }
        return cases.stream();
    }

    /**
     * Every garment the mod ships, composited onto a plate - the coverage rule of this tier, and
     * mechanical on purpose, so a third garment cannot ship having been baked by nobody.
     *
     * <p>What it can assert about art it has never seen is the two things that are true of every
     * cut: the garment lands somewhere, and it lands NOWHERE the mask did not ask for. A mask that
     * was saved at the wrong size, or with its alpha flattened, fails one or the other.
     */
    @ParameterizedTest(name = "{0}")
    @MethodSource("garments")
    void everyShippedGarmentCutsSomethingAndOnlyWhatItAskedFor(
        final String label, final Holder.Reference<Cloth> garment, final String sheet
    ) throws IOException {
        final Identifier id = garment.value().mask(sheet);
        try (NativeImage mask = read(ShippedData.clientResources(), id)) {
            assertNotNull(mask, id + " is not in the mod's assets");
            assertEquals(GRID_WIDTH, mask.getWidth(), id + " is cut for a 64-wide net");
            assertEquals(GRID_HEIGHT, mask.getHeight(), id + " is cut for a 32-tall net");

            final Image armor = plate();
            try (NativeImage out = ClothTextureManager.composite(mask, armor, armor, null, 0xC08040)) {
                int drawn = 0;
                for (int gy = 0; gy < GRID_HEIGHT; gy++) {
                    for (int gx = 0; gx < GRID_WIDTH; gx++) {
                        final int under = armor.pixels()[gy * GRID_WIDTH + gx];
                        if (at(out, gx, gy) == under) {
                            continue;
                        }
                        drawn++;
                        assertNotEquals(0, ARGB.alpha(mask.getPixel(gx, gy)),
                            label + " drew at " + gx + "," + gy + ", where its own mask is transparent");
                        assertEquals(255, ARGB.alpha(at(out, gx, gy)),
                            label + " drew a see-through texel at " + gx + "," + gy);
                    }
                }
                assertTrue(drawn > 0, label + " covers nothing at all - the mask is empty or flat");
            }
        }
    }

    // ---- the fixture ---------------------------------------------------------------------------------

    /** A garment, its dye and its design, over an armor texture: everything a bake is keyed on. */
    private static ClothValue bare(final Holder<Cloth> cloth) {
        return ClothValue.of(cloth);
    }

    private static Holder<Cloth> cloth(final String path) {
        return clothRegistry().getOrThrow(
            net.minecraft.resources.ResourceKey.create(
                ArmorPiecesRegistries.CLOTH, Identifier.fromNamespaceAndPath("armorpieces", path)));
    }

    /** A garment nobody registered - for the questions that are about the id and not the registry. */
    private static Holder<Cloth> direct(final String namespace, final String path) {
        return direct(namespace, path, BannerFitting.Sheet.SHIELD);
    }

    private static Holder<Cloth> direct(
        final String namespace, final String path, final BannerFitting.Sheet sheet
    ) {
        return Holder.direct(new Cloth(
            Identifier.fromNamespaceAndPath(namespace, path),
            sheet,
            Component.literal(path),
            List.of()));
    }

    /** One sprite sheet, opaque all over, where the game would look for it. */
    private static void sprite(final Path root, final SpriteId id, final int colour) throws IOException {
        sprite(root, id, colour, 0, 0, 64, 64);
    }

    /** One sprite sheet, opaque inside the given rectangle of its own 64x64 net and nowhere else. */
    private static void sprite(
        final Path root, final SpriteId id, final int colour,
        final int x0, final int y0, final int width, final int height
    ) throws IOException {
        final Identifier texture = id.texture().withPath(path -> "textures/" + path + ".png");
        final Path file = root.resolve(
            "assets/" + texture.getNamespace() + "/" + texture.getPath());
        Files.createDirectories(file.getParent());
        final BufferedImage image = new BufferedImage(64, 64, BufferedImage.TYPE_INT_ARGB);
        for (int y = y0; y < y0 + height; y++) {
            for (int x = x0; x < x0 + width; x++) {
                image.setRGB(x, y, colour);
            }
        }
        ImageIO.write(image, "png", file.toFile());
    }

    private static PackResources pack(final Path root) {
        final String name = root.getFileName().toString();
        return new PathPackResources(
            new PackLocationInfo(name, Component.literal(name), PackSource.BUILT_IN, Optional.empty()),
            root);
    }

    private static Registry<Cloth> clothRegistry() {
        return ShippedData.mod().registry(ArmorPiecesRegistries.CLOTH);
    }

    /** Nothing, one layer, and two layers of the same pattern in different colours. */
    private static List<BannerPatternLayers> designs() {
        final Registry<BannerPattern> patterns =
            ShippedData.mod().registries().lookupOrThrow(Registries.BANNER_PATTERN);
        final List<Holder.Reference<BannerPattern>> two =
            patterns.listElements().limit(2).toList();
        return List.of(
            BannerPatternLayers.EMPTY,
            new BannerPatternLayers(List.of(
                new BannerPatternLayers.Layer(two.getFirst(), DyeColor.WHITE))),
            new BannerPatternLayers(List.of(
                new BannerPatternLayers.Layer(two.getFirst(), DyeColor.BLACK))),
            new BannerPatternLayers(List.of(
                new BannerPatternLayers.Layer(two.getLast(), DyeColor.WHITE))),
            new BannerPatternLayers(List.of(
                new BannerPatternLayers.Layer(two.getFirst(), DyeColor.WHITE),
                new BannerPatternLayers.Layer(two.getLast(), DyeColor.BLACK))),
            new BannerPatternLayers(List.of(
                new BannerPatternLayers.Layer(two.getLast(), DyeColor.BLACK),
                new BannerPatternLayers.Layer(two.getFirst(), DyeColor.WHITE))));
    }

    /** The plate a shield pattern is painted for: 12 wide, 22 tall, 1 deep. */
    private static int[] plateBox() {
        return new int[] {12, 22, 1};
    }

    /** A 64x64 sprite sheet in one colour, opaque everywhere. */
    private static Image sprite(final int colour) {
        final int[] pixels = new int[64 * 64];
        java.util.Arrays.fill(pixels, colour);
        return new Image(pixels, 64, 64);
    }

    /** One texel of one pass at one alpha, over a colour an earlier pass left there. */
    private static int pass(final int under, final int alpha, final DyeColor colour) {
        final int[] pixels = new int[12 * 22];
        java.util.Arrays.fill(pixels, 0xFF000000 | under);
        final int[] sprite = new int[64 * 64];
        java.util.Arrays.fill(sprite, (alpha << 24) | 0x00FFFFFF);
        ClothTextureManager.paint(pixels, 12, 22, plateBox(), new Image(sprite, 64, 64), colour);
        return pixels[0];
    }

    /** A design of one colour, at the size a shield pattern is painted for. */
    private static Panel solid(final int colour) {
        final int[] pixels = new int[12 * 22];
        java.util.Arrays.fill(pixels, 0xFF000000 | colour);
        return new Panel(pixels, 12, 22);
    }

    /**
     * A piece of armor as vanilla paints one: the two panels and the two flanks, and nothing on the
     * lid or the sole. The greys vary from texel to texel so the lightmap has something to measure -
     * a flat plate would make {@link #theValueIsTheMasksOwnPlusTheArmorsLight} vacuous.
     */
    private static int[] platePixels() {
        final int[] pixels = new int[GRID_WIDTH * GRID_HEIGHT];
        for (final int[] face : List.of(FRONT, BACK, LEFT, RIGHT)) {
            for (int y = face[1]; y < face[1] + face[3]; y++) {
                for (int x = face[0]; x < face[0] + face[2]; x++) {
                    final int grey = 40 + ((x * 7 + y * 13) % 5) * 40;
                    pixels[y * GRID_WIDTH + x] = 0xFF000000 | (grey << 16) | (grey << 8) | grey;
                }
            }
        }
        return pixels;
    }

    private static Image plate() {
        return new Image(platePixels(), GRID_WIDTH, GRID_HEIGHT);
    }

    /** A cut mask on the net, painted by the caller. */
    private static NativeImage mask(final java.util.function.Consumer<int[]> paint) {
        final int[] pixels = new int[GRID_WIDTH * GRID_HEIGHT];
        paint.accept(pixels);
        final NativeImage image = new NativeImage(GRID_WIDTH, GRID_HEIGHT, false);
        for (int y = 0; y < GRID_HEIGHT; y++) {
            for (int x = 0; x < GRID_WIDTH; x++) {
                image.setPixel(x, y, pixels[y * GRID_WIDTH + x]);
            }
        }
        return image;
    }

    private static void fill(final int[] pixels, final int[] rect, final int colour) {
        for (int y = rect[1]; y < rect[1] + rect[3]; y++) {
            for (int x = rect[0]; x < rect[0] + rect[2]; x++) {
                pixels[y * GRID_WIDTH + x] = colour;
            }
        }
    }

    /** One texel of the net, read off the bake it was blown up into. */
    private static int at(final NativeImage out, final int gx, final int gy) {
        return out.getPixel(gx * SCALE, gy * SCALE);
    }

    private static NativeImage read(final ResourceManager manager, final Identifier id) throws IOException {
        final Optional<Resource> resource = manager.getResource(id);
        assertTrue(resource.isPresent(), id + " is not in the mod's assets");
        try (InputStream stream = resource.get().open()) {
            return NativeImage.read(stream);
        }
    }
}
