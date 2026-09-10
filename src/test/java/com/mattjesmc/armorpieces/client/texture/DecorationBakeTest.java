package com.mattjesmc.armorpieces.client.texture;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mattjesmc.armorpieces.decoration.fitting.FittingColour;
import com.mojang.blaze3d.platform.NativeImage;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.TreeSet;
import java.util.stream.Stream;
import javax.imageio.ImageIO;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.packs.PackLocationInfo;
import net.minecraft.server.packs.PackResources;
import net.minecraft.server.packs.PackType;
import net.minecraft.server.packs.PathPackResources;
import net.minecraft.server.packs.repository.PackSource;
import net.minecraft.server.packs.resources.MultiPackResourceManager;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.util.ARGB;
import net.minecraft.world.item.DyeColor;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

/**
 * Holds the client's own recolour to {@code tools/preview_material.py}, and pins the rules it bakes by.
 *
 * <p>A part ships ONE greyscale master and the game colours it for every material at load time, so
 * what a player sees is arithmetic rather than art: {@link DecorationPalette} turns a material's
 * eight-stop palette into a 256-entry ramp, {@link DecorationTextureManager#recolour} indexes it by
 * the master's own red channel, and {@link DecorationTextureManager#applyMask} lays a filled
 * fitting's mask over the result. Every part in every material in every combination of fittings is
 * that, and nothing else.
 *
 * <p>The same arithmetic is ported to Python, because the Blockbench plugin and the site preview a
 * part outside a running client, and a port nobody checks is a port that drifts - which is exactly
 * what {@link com.mattjesmc.armorpieces.skin.SkinBakeTest} exists to stop happening to skins. This
 * is that bargain for decorations: {@code python tools/preview_material.py --reference} writes down
 * what the port produces - the ramps, the static ramps a dye and a static layer go through, and a
 * digest of the finished picture for every part the mod ships - and this reads it back. A failure
 * here means an author is judging a colour the game will not draw.
 *
 * <p>The vanilla palettes come off the test classpath, out of the game jar the build already depends
 * on, so this needs no asset cache and nothing extracted. Everything the reference does not cover -
 * a palette that is not a palette, a material with no palette at all, a mask over a transparent
 * master - is asserted below over images the test paints itself, because none of them can be
 * expressed as a shipped part.
 */
class DecorationBakeTest {
    private static final Path REFERENCE = Path.of("docs", "plans", "decoration-bake-reference.json");
    private static final Path DECORATIONS = Path.of(
        "src", "main", "resources", "assets", "armorpieces", "textures", "entity", "decoration");
    private static final Path PART_DATA = Path.of(
        "src", "main", "resources", "data", "armorpieces", "armorpieces", "armor_decoration");
    private static final String PALETTES = "/assets/minecraft/textures/trims/color_palettes/";
    private static final String KEY = PALETTES + "trim_palette.png";

    /** Read once: 132 cases would otherwise re-parse the same file 132 times. */
    private static JsonObject reference;

    private static synchronized JsonObject reference() {
        Assumptions.assumeTrue(Files.exists(REFERENCE),
            REFERENCE + " is missing - regenerate it with python tools/preview_material.py --reference");
        if (reference == null) {
            try (Reader reader = new InputStreamReader(Files.newInputStream(REFERENCE), StandardCharsets.UTF_8)) {
                reference = JsonParser.parseReader(reader).getAsJsonObject();
            } catch (final IOException e) {
                throw new AssertionError("could not read " + REFERENCE, e);
            }
        }
        return reference;
    }

    // ---- the port ---------------------------------------------------------------------------------

    @Test
    void theMidStopIsTheOneTheToolPorted() {
        assertEquals(DecorationPalette.MID_STOP, reference().get("mid_stop").getAsFloat(), 1.0e-6,
            "MID_STOP - a reference written under a different one describes another arithmetic");
    }

    static Stream<Arguments> materials() {
        return reference().getAsJsonObject("materials").entrySet().stream()
            .map(entry -> Arguments.of(entry.getKey(), entry.getValue().getAsJsonObject()));
    }

    /** Every trim material's ramp, built from the game's own palette, against the port's copy of it. */
    @ParameterizedTest(name = "{0}")
    @MethodSource("materials")
    void everyMaterialsRampIsTheOneTheToolDraws(final String material, final JsonObject expected) {
        final DecorationPalette ramp = materialRamp(material);
        assertNotNull(ramp, material + " has no palette in the game jar");
        assertRamp(ramp, expected, material);
    }

    static Stream<Arguments> staticColours() {
        return reference().getAsJsonObject("static").entrySet().stream()
            .map(entry -> Arguments.of(entry.getKey(), entry.getValue().getAsJsonObject()));
    }

    /**
     * The ramp built around a fixed colour, which is what a static layer's ivory and a dyed inlay
     * both go through. Every dye, and every colour the shipped static layers actually use.
     */
    @ParameterizedTest(name = "{0}")
    @MethodSource("staticColours")
    void everyStaticColoursRampIsTheOneTheToolDraws(final String colour, final JsonObject expected) {
        assertRamp(DecorationPalette.ofStaticColour(rgb(colour)), expected, colour);
    }

    /**
     * The port carries the dyes' colours as a table, because it has no game to ask. This is the ask:
     * a dye whose colour moved would preview one colour and render another.
     */
    @Test
    void theToolsDyeColoursAreTheGamesOwn() {
        final JsonObject statics = reference().getAsJsonObject("static");
        final List<String> missing = new ArrayList<>();
        for (final DyeColor dye : DyeColor.values()) {
            final String colour = String.format("#%06x", dye.getTextureDiffuseColor() & 0x00FFFFFF);
            if (!statics.has(colour)) {
                missing.add(dye.getSerializedName() + " is " + colour + " in the game");
            }
        }
        assertTrue(missing.isEmpty(), () -> "dye colours the port does not have:\n  "
            + String.join("\n  ", missing)
            + "\n  fix DYES in tools/preview_material.py, then regenerate the reference");
    }

    static Stream<Arguments> cases() {
        final List<Arguments> cases = new ArrayList<>();
        for (final JsonElement element : reference().getAsJsonArray("cases")) {
            final JsonObject one = element.getAsJsonObject();
            cases.add(Arguments.of(label(one), one));
        }
        return cases.stream();
    }

    /**
     * One part, composited exactly as the client bakes it, texel for texel against the port.
     *
     * <p>Three sweeps: every part in iron with nothing set, every part that has a mask in gold with
     * all of them filled, and the one part that is a master, a static layer and two masks at once
     * through every material there is.
     */
    @ParameterizedTest(name = "{0}")
    @MethodSource("cases")
    void everyPartComesOutTheSamePicture(final String label, final JsonObject expected) throws IOException {
        try (NativeImage master = read(DECORATIONS.resolve(expected.get("master").getAsString()))) {
            // The master first and by name: a repainted master changes the answer with nothing being
            // wrong, and that should not read as the arithmetic having drifted.
            assertEquals(expected.get("master_sha1").getAsString(), digest(master),
                () -> expected.get("master").getAsString() + " has been repainted since the reference "
                    + "was written - regenerate it with python tools/preview_material.py --reference");

            final JsonElement statics = expected.get("static");
            NativeImage staticLayer = null;
            try {
                if (!statics.isJsonNull()) {
                    staticLayer = read(DECORATIONS.resolve(statics.getAsString()));
                }
                final String material = expected.get("material").getAsString();
                try (NativeImage out = DecorationTextureManager.recolour(
                    master, staticLayer, materialRamp(material))) {
                    for (final JsonElement element : expected.getAsJsonArray("masks")) {
                        final JsonObject mask = element.getAsJsonObject();
                        try (NativeImage sheet = read(DECORATIONS.resolve(mask.get("mask").getAsString()))) {
                            DecorationTextureManager.applyMask(
                                out, master, sheet, ramp(mask.get("value").getAsString()));
                        }
                    }
                    assertEquals(expected.get("width").getAsInt(), out.getWidth(), "width");
                    assertEquals(expected.get("height").getAsInt(), out.getHeight(), "height");
                    assertEquals(expected.get("sha1").getAsString(), digest(out),
                        () -> label + " is not the picture tools/preview_material.py makes of it");
                }
            } finally {
                if (staticLayer != null) {
                    staticLayer.close();
                }
            }
        }
    }

    /**
     * A part that ships after the reference was written is a part nothing here has ever coloured.
     * Mechanical on purpose: coverage of this tier cannot be somebody remembering to add a row.
     */
    @Test
    void theReferenceCoversEveryPartTheModShips() throws IOException {
        final Set<String> covered = new TreeSet<>();
        reference().getAsJsonArray("cases")
            .forEach(element -> covered.add(element.getAsJsonObject().get("part").getAsString()));

        final Set<String> shipped = new TreeSet<>();
        try (Stream<Path> files = Files.list(PART_DATA)) {
            for (final Path file : files.filter(path -> path.toString().endsWith(".json")).toList()) {
                try (Reader reader = new InputStreamReader(Files.newInputStream(file), StandardCharsets.UTF_8)) {
                    final JsonObject part = JsonParser.parseReader(reader).getAsJsonObject();
                    final Identifier asset = Identifier.parse(part.get("asset_id").getAsString());
                    if (asset.getNamespace().equals("armorpieces")) {
                        shipped.add(asset.getPath());
                    }
                }
            }
        }
        shipped.removeAll(covered);
        assertTrue(shipped.isEmpty(), () -> "parts no reference case colours: " + shipped
            + "\n  regenerate it with python tools/preview_material.py --reference");
    }

    // ---- the ramp's own shape ---------------------------------------------------------------------

    /**
     * The three stops, taken by position rather than by matching greys: darkest, the one vanilla's
     * trim art centres on, lightest. Eight stops put MID_STOP exactly on index five, so this asks
     * for the material's own colour rather than for an interpolation of it.
     */
    @Test
    void theRampIsTheDarkestStop_theFifthOfEight_andTheLightest() {
        final int[] colours = {
            0xFF101010, 0xFF202020, 0xFF303030, 0xFF404040,
            0xFF505050, 0xFF606060, 0xFF707070, 0xFF808080};
        try (NativeImage key = greys(8); NativeImage palette = row(colours)) {
            final DecorationPalette ramp = DecorationPalette.of(key, palette);
            assertNotNull(ramp);
            assertEquals(colours[0], ramp.rgb(0), "the darkest stop is luminance 0");
            assertEquals(colours[5], ramp.rgb(127), "the mid stop is 5/7 of the way along");
            assertEquals(colours[7], ramp.rgb(255), "the lightest stop is luminance 255");
        }
    }

    /** The key orders the palette, so the same eight stops read the same way round either way. */
    @Test
    void aPaletteWrittenLightestFirstReadsTheSame() {
        final int[] colours = {
            0xFF101010, 0xFF202020, 0xFF303030, 0xFF404040,
            0xFF505050, 0xFF606060, 0xFF707070, 0xFF808080};
        final int[] backwards = new int[colours.length];
        final int[] keyGreys = new int[colours.length];
        for (int i = 0; i < colours.length; i++) {
            backwards[i] = colours[colours.length - 1 - i];
            keyGreys[i] = grey((colours.length - 1 - i) * 255 / (colours.length - 1));
        }
        try (NativeImage key = greys(8);
             NativeImage palette = row(colours);
             NativeImage reversedKey = row(keyGreys);
             NativeImage reversed = row(backwards)) {
            assertRampsEqual(DecorationPalette.of(key, palette), DecorationPalette.of(reversedKey, reversed));
        }
    }

    /** Row-major, so a palette shipped as one row and one shipped as two read identically. */
    @Test
    void aPaletteInTwoRowsReadsAsOne() {
        final int[] colours = {
            0xFF101010, 0xFF202020, 0xFF303030, 0xFF404040,
            0xFF505050, 0xFF606060, 0xFF707070, 0xFF808080};
        try (NativeImage key = greys(8);
             NativeImage palette = row(colours);
             NativeImage keyGrid = grid(greyRow(8), 4);
             NativeImage grid = grid(colours, 4)) {
            assertRampsEqual(DecorationPalette.of(key, palette), DecorationPalette.of(keyGrid, grid));
        }
    }

    /**
     * What is not a palette gives no ramp, and the part is then drawn at its own greys. A pack that
     * registered a material and shipped a stray file gets an untinted part, not a crash.
     */
    @Test
    void whatIsNotAPaletteIsNoPalette() {
        try (NativeImage oneStop = row(new int[] {0xFF808080});
             NativeImage oneKey = row(new int[] {grey(0)});
             NativeImage flatKey = row(new int[] {grey(64), grey(64), grey(64)});
             NativeImage threeColours = row(new int[] {0xFF101010, 0xFF404040, 0xFF808080})) {
            assertNull(DecorationPalette.of(oneKey, oneStop), "one stop is not a ramp");
            assertNull(DecorationPalette.of(flatKey, threeColours), "a key with no order is not a key");
        }
    }

    /**
     * The static ramp's rule, stated rather than fitted: half the colour, the colour, halfway to
     * white. It is what lets a horn's keratin keep its own colour while the ferrule beside it takes
     * the metal, with the same shading on both.
     */
    @Test
    void theStaticRampIsHalfTheColour_theColour_andHalfwayToWhite() {
        final DecorationPalette ramp = DecorationPalette.ofStaticColour(0xC08040);
        assertEquals(0xFF604020, ramp.rgb(0), "the dark stop is half the colour");
        assertEquals(0xFFC08040, ramp.rgb(127), "the colour itself is the mid stop");
        assertEquals(0xFFE0C0A0, ramp.rgb(255), "the light stop is halfway to white");
    }

    // ---- the two rules the bake never breaks -------------------------------------------------------

    /**
     * The master is the silhouette and the only silhouette: its alpha travels through untouched, and
     * a static pixel or a mask pixel outside it draws nothing. Anything else and a fitting could
     * widen the part that wears it.
     */
    @Test
    void theMasterIsTheSilhouette() {
        try (NativeImage master = row(new int[] {0x00FFFFFF, 0x80808080, 0xFF404040});
             NativeImage statics = row(new int[] {0xFF00FF00, 0x00FF0000, 0x00FF0000});
             NativeImage mask = row(new int[] {0xFFC0C0C0, 0x00000000, 0x00000000})) {
            try (NativeImage out = DecorationTextureManager.recolour(master, statics, null)) {
                assertEquals(0, out.getPixel(0, 0), "a transparent master pixel stays empty");
                assertEquals(0x80, ARGB.alpha(out.getPixel(1, 0)), "the master's alpha is kept");
                DecorationTextureManager.applyMask(out, master, mask, DecorationPalette.ofStaticColour(0xFF0000));
                assertEquals(0, out.getPixel(0, 0), "a mask pixel outside the silhouette is skipped");
            }
        }
    }

    /**
     * A material a pack registered without shipping a palette leaves the part at the master's own
     * greys - shading intact, tint missing - rather than dropping it. A mask with no ramp does the
     * same with its own.
     */
    @Test
    void withNoRampTheGreysShowThrough() {
        try (NativeImage master = row(new int[] {0xFF404040, 0xFF808080});
             NativeImage mask = row(new int[] {0x00000000, 0xFFC0C0C0})) {
            try (NativeImage out = DecorationTextureManager.recolour(master, null, null)) {
                assertEquals(0xFF404040, out.getPixel(0, 0), "an unpalettable material keeps the master");
                DecorationTextureManager.applyMask(out, master, mask, null);
                assertEquals(0xFFC0C0C0, out.getPixel(1, 0), "an unpalettable fitting keeps the mask");
            }
        }
    }

    /**
     * A static pixel takes its own colour's ramp at the MASTER's value: the master keeps saying where
     * the light is, the static layer only says what colour is there.
     */
    @Test
    void aStaticPixelIsItsOwnColourAtTheMastersValue() {
        try (NativeImage master = row(new int[] {0xFF404040, 0xFFFFFFFF});
             NativeImage statics = row(new int[] {0xFFC08040, 0xFFC08040});
             NativeImage palette = row(new int[] {0xFF000080, 0xFF0000FF});
             NativeImage key = greys(2)) {
            final DecorationPalette metal = DecorationPalette.of(key, palette);
            try (NativeImage out = DecorationTextureManager.recolour(master, statics, metal)) {
                final DecorationPalette expected = DecorationPalette.ofStaticColour(0xC08040);
                assertEquals(expected.rgb(0x40), out.getPixel(0, 0), "the static colour, shaded by the master");
                assertEquals(expected.rgb(0xFF), out.getPixel(1, 0), "and again at the master's own value");
            }
        }
    }

    /** Masks are laid over in the order the part lists them, later over earlier where they overlap. */
    @Test
    void aLaterMaskPaintsOverAnEarlierOne() {
        try (NativeImage master = row(new int[] {0xFF808080});
             NativeImage first = row(new int[] {0xFF808080});
             NativeImage second = row(new int[] {0xFF808080})) {
            try (NativeImage out = DecorationTextureManager.recolour(master, null, null)) {
                DecorationTextureManager.applyMask(out, master, first, DecorationPalette.ofStaticColour(0xFF0000));
                DecorationTextureManager.applyMask(out, master, second, DecorationPalette.ofStaticColour(0x0000FF));
                assertEquals(DecorationPalette.ofStaticColour(0x0000FF).rgb(0x80), out.getPixel(0, 0));
            }
        }
    }

    // ---- where a bake is filed ---------------------------------------------------------------------

    /**
     * The baked id is the cache key, so two different-looking bakes sharing one would put a red inlay
     * on a piece somebody dyed blue - and it is also a resource location, which refuses most
     * punctuation. Every combination the shipped fittings can be in, over every part, is asked for
     * both at once.
     */
    @Test
    void everyBakeIsFiledSomewhereLegalAndSomewhereOfItsOwn() throws IOException {
        final List<DecorationTextureManager.Mask> guardGold = List.of(
            new DecorationTextureManager.Mask("guard", new FittingColour.Palette("gold")));
        final List<DecorationTextureManager.Mask> guardIron = List.of(
            new DecorationTextureManager.Mask("guard", new FittingColour.Palette("iron")));
        final List<DecorationTextureManager.Mask> inlayRed = List.of(
            new DecorationTextureManager.Mask("inlay", new FittingColour.Solid(0xB02E26)));
        final List<DecorationTextureManager.Mask> both = List.of(
            guardGold.getFirst(), inlayRed.getFirst());
        final List<List<DecorationTextureManager.Mask>> combinations =
            List.of(List.of(), guardGold, guardIron, inlayRed, both, List.of(inlayRed.getFirst(), guardGold.getFirst()));

        final Set<Identifier> seen = new HashSet<>();
        final List<String> collisions = new ArrayList<>();
        for (final String part : parts()) {
            final Identifier assetId = Identifier.fromNamespaceAndPath("armorpieces", part);
            for (final String material : List.of("iron", "gold", "iron_darker")) {
                for (final List<DecorationTextureManager.Mask> masks : combinations) {
                    // Illegal punctuation would throw out of here rather than assert.
                    final Identifier baked = DecorationTextureManager.bakedId(assetId, material, masks);
                    if (!seen.add(baked)) {
                        collisions.add(baked + " is claimed twice");
                    }
                }
            }
        }
        assertTrue(collisions.isEmpty(), () -> String.join("\n  ", collisions));
        assertEquals(
            DecorationTextureManager.bakedId(
                Identifier.fromNamespaceAndPath("armorpieces", "sash"), "iron", both),
            DecorationTextureManager.bakedId(
                Identifier.fromNamespaceAndPath("armorpieces", "sash"), "iron", both),
            "the same bake is filed in the same place, or nothing is ever cached");
        assertNotEquals(
            DecorationTextureManager.bakedId(
                Identifier.fromNamespaceAndPath("armorpieces", "sash"), "iron", both),
            DecorationTextureManager.bakedId(
                Identifier.fromNamespaceAndPath("armorpieces_hunt", "sash"), "iron", both),
            "two packs' parts of one name are two bakes");
    }

    // ---- where a material's palette comes from ------------------------------------------------------

    /**
     * The atlas is read as a STACK, so two mods that each add a material both keep theirs.
     *
     * <p>This is the promise the whole one-master design rests on: a material mod ships a palette and
     * wires it into {@code atlases/armor_trims.json} because its own trims need that anyway, and every
     * decoration in the game then has a colour for it, with no art from anybody. Taking the top
     * resource instead would have quietly broken the second mod installed - which looks like "their
     * material does not work with this mod" and is impossible to tell from a missing file.
     *
     * <p>Two packs written here, each adding one material, plus a third palette that no atlas mentions
     * to prove the convention path still answers for a material that registered without wiring itself
     * in. No game, no vanilla assets: a palette is eight pixels and this paints its own.
     */
    @Test
    void everyPacksMaterialsSurviveTheAtlas(@TempDir final Path first, @TempDir final Path second)
        throws IOException {
        final int[] shiny = {0xFF202020, 0xFF303030, 0xFF404040, 0xFF505050,
            0xFF606060, 0xFF707070, 0xFF808080, 0xFF909090};
        final int[] dull = {0xFF102010, 0xFF203020, 0xFF304030, 0xFF405040,
            0xFF506050, 0xFF607060, 0xFF708070, 0xFF809080};
        final int[] plain = {0xFF100010, 0xFF200020, 0xFF300030, 0xFF400040,
            0xFF500050, 0xFF600060, 0xFF700070, 0xFF800080};

        // Each pack's own palette lives where only its atlas entry can find it, so the convention
        // path cannot quietly answer for a mapping that was lost.
        atlas(first, "shiny");
        palette(first, "minecraft", "trims/color_palettes/trim_palette", greyRow(8));
        palette(first, "a_pack", "palettes/shiny", shiny);
        atlas(second, "dull");
        palette(second, "a_pack", "palettes/dull", dull);
        palette(second, "minecraft", "trims/color_palettes/plain", plain);

        final ResourceManager manager = new MultiPackResourceManager(
            PackType.CLIENT_RESOURCES, List.of(pack(first), pack(second)));
        final DecorationTextureManager textures = DecorationTextureManager.instance();
        textures.loadPaletteMapping(manager);

        assertRampIs(shiny, textures.palette(manager, "shiny"), "the first pack's material");
        assertRampIs(dull, textures.palette(manager, "dull"), "the second pack's material");
        assertRampIs(plain, textures.palette(manager, "plain"),
            "a palette no atlas names, found by convention");
        assertNull(textures.palette(manager, "nothing_shipped_this"),
            "a material with no palette anywhere leaves the part untinted");
    }

    private static void assertRampIs(final int[] stops, final DecorationPalette ramp, final String what) {
        assertNotNull(ramp, what + " has no ramp");
        assertEquals(stops[0], ramp.rgb(0), what + " at its darkest");
        assertEquals(stops[5], ramp.rgb(127), what + " at its mid stop");
        assertEquals(stops[7], ramp.rgb(255), what + " at its lightest");
    }

    /** One pack's armor trim atlas, naming one material's palette the way vanilla's own does. */
    private static void atlas(final Path root, final String material) throws IOException {
        final Path file = root.resolve("assets/minecraft/atlases/armor_trims.json");
        Files.createDirectories(file.getParent());
        Files.writeString(file, """
            {"sources": [{"type": "minecraft:paletted_permutations",
              "textures": ["trims/models/armor/coast"],
              "palette_key": "trims/color_palettes/trim_palette",
              "permutations": {"%s": "a_pack:palettes/%s"}}]}
            """.formatted(material, material), StandardCharsets.UTF_8);
    }

    private static void palette(
        final Path root, final String namespace, final String path, final int[] stops
    ) throws IOException {
        final Path file = root.resolve("assets/" + namespace + "/textures/" + path + ".png");
        Files.createDirectories(file.getParent());
        final BufferedImage image = new BufferedImage(stops.length, 1, BufferedImage.TYPE_INT_ARGB);
        for (int x = 0; x < stops.length; x++) {
            image.setRGB(x, 0, stops[x]);
        }
        ImageIO.write(image, "png", file.toFile());
    }

    private static PackResources pack(final Path root) {
        final String name = root.getFileName().toString();
        return new PathPackResources(
            new PackLocationInfo(name, Component.literal(name), PackSource.BUILT_IN, Optional.empty()),
            root);
    }

    // ---- fixture -----------------------------------------------------------------------------------

    private static String label(final JsonObject one) {
        final StringBuilder label = new StringBuilder(one.get("part").getAsString())
            .append(" in ").append(one.get("material").getAsString());
        one.getAsJsonArray("masks").forEach(element -> {
            final JsonObject mask = element.getAsJsonObject();
            label.append(" + ").append(mask.get("mask").getAsString())
                .append('=').append(mask.get("value").getAsString());
        });
        return label.toString();
    }

    /** Every part the mod's own datapack declares, by the path its texture lives at. */
    private static List<String> parts() throws IOException {
        final List<String> parts = new ArrayList<>();
        try (Stream<Path> files = Files.list(PART_DATA)) {
            for (final Path file : files.filter(path -> path.toString().endsWith(".json")).toList()) {
                try (Reader reader = new InputStreamReader(Files.newInputStream(file), StandardCharsets.UTF_8)) {
                    parts.add(Identifier.parse(JsonParser.parseReader(reader).getAsJsonObject()
                        .get("asset_id").getAsString()).getPath());
                }
            }
        }
        return parts;
    }

    /** What a fitting's value colours its mask through: a dye is a colour, anything else is a material. */
    private static DecorationPalette ramp(final String value) {
        final DyeColor dye = DyeColor.byName(value, null);
        return dye != null
            ? DecorationPalette.ofStaticColour(dye.getTextureDiffuseColor() & 0x00FFFFFF)
            : materialRamp(value);
    }

    /** The material's ramp, built out of the game jar's own palette exactly as the client builds it. */
    private static DecorationPalette materialRamp(final String material) {
        try (NativeImage key = classpath(KEY); NativeImage palette = classpath(PALETTES + material + ".png")) {
            return DecorationPalette.of(key, palette);
        }
    }

    private static void assertRamp(final DecorationPalette ramp, final JsonObject expected, final String what) {
        expected.getAsJsonObject("samples").entrySet().forEach(sample -> assertEquals(
            sample.getValue().getAsString(),
            String.format("%06x", ramp.rgb(Integer.parseInt(sample.getKey())) & 0x00FFFFFF),
            () -> what + " at luminance " + sample.getKey()));
        final byte[] all = new byte[256 * 3];
        for (int v = 0; v < 256; v++) {
            final int colour = ramp.rgb(v);
            all[v * 3] = (byte) ARGB.red(colour);
            all[v * 3 + 1] = (byte) ARGB.green(colour);
            all[v * 3 + 2] = (byte) ARGB.blue(colour);
        }
        assertEquals(expected.get("sha1").getAsString(), sha1(all),
            () -> what + "'s whole ramp is not the one tools/preview_material.py builds");
    }

    private static void assertRampsEqual(final DecorationPalette one, final DecorationPalette other) {
        assertNotNull(one);
        assertNotNull(other);
        for (int v = 0; v < 256; v++) {
            assertEquals(one.rgb(v), other.rgb(v), "luminance " + v);
        }
    }

    /** The picture as one string: sha1 over its RGBA bytes, row-major, as the Python half writes them. */
    private static String digest(final NativeImage image) {
        final byte[] bytes = new byte[image.getWidth() * image.getHeight() * 4];
        int at = 0;
        for (int y = 0; y < image.getHeight(); y++) {
            for (int x = 0; x < image.getWidth(); x++) {
                final int pixel = image.getPixel(x, y);
                bytes[at++] = (byte) ARGB.red(pixel);
                bytes[at++] = (byte) ARGB.green(pixel);
                bytes[at++] = (byte) ARGB.blue(pixel);
                bytes[at++] = (byte) ARGB.alpha(pixel);
            }
        }
        return sha1(bytes);
    }

    private static String sha1(final byte[] bytes) {
        try {
            final StringBuilder hex = new StringBuilder();
            for (final byte b : MessageDigest.getInstance("SHA-1").digest(bytes)) {
                hex.append(String.format("%02x", b));
            }
            return hex.toString();
        } catch (final NoSuchAlgorithmException impossible) {
            throw new AssertionError(impossible);
        }
    }

    private static int rgb(final String hash) {
        return Integer.parseInt(hash.substring(1), 16);
    }

    private static NativeImage read(final Path path) throws IOException {
        try (InputStream stream = Files.newInputStream(path)) {
            return NativeImage.read(stream);
        }
    }

    private static NativeImage classpath(final String resource) {
        try (InputStream stream = DecorationBakeTest.class.getResourceAsStream(resource)) {
            Assumptions.assumeTrue(stream != null, resource + " is not on the test classpath");
            return NativeImage.read(stream);
        } catch (final IOException e) {
            throw new AssertionError("could not read " + resource, e);
        }
    }

    /** One row of ARGB pixels, which is how vanilla lays a palette out. */
    private static NativeImage row(final int[] colours) {
        final NativeImage image = new NativeImage(colours.length, 1, false);
        for (int x = 0; x < colours.length; x++) {
            image.setPixel(x, 0, colours[x]);
        }
        return image;
    }

    /** The same pixels wrapped into rows of {@code width}, to prove the reading is row-major. */
    private static NativeImage grid(final int[] colours, final int width) {
        final NativeImage image = new NativeImage(width, colours.length / width, false);
        for (int i = 0; i < colours.length; i++) {
            image.setPixel(i % width, i / width, colours[i]);
        }
        return image;
    }

    /** An ordering key: {@code stops} greys spread evenly from black to white. */
    private static NativeImage greys(final int stops) {
        return row(greyRow(stops));
    }

    private static int[] greyRow(final int stops) {
        final int[] greys = new int[stops];
        for (int i = 0; i < stops; i++) {
            greys[i] = grey(i * 255 / (stops - 1));
        }
        return greys;
    }

    private static int grey(final int value) {
        return 0xFF000000 | (value << 16) | (value << 8) | value;
    }
}
