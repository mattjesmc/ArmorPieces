package com.mattjesmc.armorpieces.skin;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;
import javax.imageio.ImageIO;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.MethodSource;

/**
 * Holds {@link SkinBake} to the same numbers {@code tools/bake_skin.py} produces.
 *
 * <p>The skins are DRAWN against the Python bake - in Blockbench, through the authoring bridge, with
 * its material previews on screen - and they are WORN through the Java one. Two implementations of
 * one piece of arithmetic will drift, and the drift would show up as a skin that looked one way
 * while it was being drawn and another in game, which is the hardest kind of bug to see and the
 * easiest to avoid: {@code python tools/bake_skin.py --reference} writes down what the arithmetic
 * produces - the eight shades, samples down the 256-entry table, and a digest of each material's
 * whole lighting map - and this reads that file back.
 *
 * <p>A failure here is not a style disagreement. It means a skinned helmet renders differently from
 * the sheet its author approved.
 *
 * <p>The vanilla textures come off the test classpath, out of the game jar the build already
 * depends on, so this needs no asset cache and nothing extracted.
 */
class SkinBakeTest {
    private static final Path REFERENCE = Path.of("docs", "plans", "skin-bake-reference.json");
    private static final String EQUIPMENT = "/assets/minecraft/textures/entity/equipment/";
    private static final List<String> SHEETS = List.of("humanoid", "humanoid_leggings");

    /** Every material the reference file was generated for, and the whole of what it says about it. */
    static Stream<org.junit.jupiter.params.provider.Arguments> materials() throws IOException {
        Assumptions.assumeTrue(Files.exists(REFERENCE),
            REFERENCE + " is missing - regenerate it with python tools/bake_skin.py --reference");
        final JsonObject root;
        try (InputStream stream = Files.newInputStream(REFERENCE)) {
            root = JsonParser.parseReader(new InputStreamReader(stream, StandardCharsets.UTF_8)).getAsJsonObject();
        }
        // The constants are part of the agreement: a reference file written under a different mix or
        // a different span describes an arithmetic this class does not implement.
        assertEquals(SkinBake.SHADES, root.get("shades").getAsInt(), "shades");
        assertEquals(SkinBake.MIN_SPAN, root.get("min_span").getAsInt(), "min_span");
        assertEquals(SkinBake.LIGHT_MIX, root.get("light_mix").getAsFloat(), 1.0e-6, "light_mix");

        final JsonObject materials = root.getAsJsonObject("materials");
        return materials.entrySet().stream()
            .map(entry -> org.junit.jupiter.params.provider.Arguments.of(
                entry.getKey(), entry.getValue().getAsJsonObject()));
    }

    @ParameterizedTest(name = "{0}")
    @MethodSource("materials")
    void bakesAsTheToolDoes(final String material, final JsonObject expected) throws IOException {
        final List<int[]> sheets = new ArrayList<>(2);
        final Map<String, int[]> bySheet = new java.util.LinkedHashMap<>();
        for (final String sheet : SHEETS) {
            final int[] pixels = read(EQUIPMENT + sheet + "/" + material + ".png");
            if (pixels != null) {
                sheets.add(pixels);
                bySheet.put(sheet, pixels);
            }
        }
        Assumptions.assumeFalse(sheets.isEmpty(), "no vanilla texture for " + material + " on the classpath");

        final int[] shades = SkinBake.ramp(sheets);
        assertNotNull(shades, material + ": no ramp");
        final JsonArray ramp = expected.getAsJsonArray("ramp");
        for (int i = 0; i < SkinBake.SHADES; i++) {
            assertEquals(ramp.get(i).getAsString(), hex(shades[i]), material + ": shade " + i);
        }

        final int[] table = SkinBake.table(shades);
        for (final var entry : expected.getAsJsonObject("table").entrySet()) {
            final int value = Integer.parseInt(entry.getKey());
            assertEquals(entry.getValue().getAsString(), hex(table[value]),
                material + ": table[" + value + "]");
        }

        final JsonObject lightmaps = expected.getAsJsonObject("lightmap");
        for (final var entry : lightmaps.entrySet()) {
            final int[] pixels = bySheet.get(entry.getKey());
            assertNotNull(pixels, material + ": no " + entry.getKey() + " sheet to light from");
            final byte[] map = SkinBake.lightmap(pixels);
            final JsonObject digest = entry.getValue().getAsJsonObject();
            final String where = material + " " + entry.getKey();

            assertEquals(digest.get("sha1").getAsString(), sha1(map), where + ": lightmap");
            int nonzero = 0;
            int min = 0;
            int max = 0;
            for (final byte value : map) {
                nonzero += value != 0 ? 1 : 0;
                min = Math.min(min, value);
                max = Math.max(max, value);
            }
            assertEquals(digest.get("nonzero").getAsInt(), nonzero, where + ": lit texels");
            assertEquals(digest.get("min").getAsInt(), min, where + ": darkest");
            assertEquals(digest.get("max").getAsInt(), max, where + ": brightest");

            final int width = width(EQUIPMENT + entry.getKey() + "/" + material + ".png");
            for (final var sample : digest.getAsJsonArray("samples")) {
                final JsonArray xyv = sample.getAsJsonArray();
                final int x = xyv.get(0).getAsInt();
                final int y = xyv.get(1).getAsInt();
                assertEquals(xyv.get(2).getAsInt(), map[y * width + x], where + ": texel " + x + "," + y);
            }
        }
    }

    /** The digest the tool takes: every value in reading order, comma-separated, as text. */
    private static String sha1(final byte[] map) {
        final StringBuilder text = new StringBuilder(map.length * 3);
        for (int i = 0; i < map.length; i++) {
            if (i > 0) {
                text.append(',');
            }
            text.append(map[i]);
        }
        final MessageDigest digest;
        try {
            digest = MessageDigest.getInstance("SHA-1");
        } catch (final NoSuchAlgorithmException e) {
            throw new IllegalStateException(e);
        }
        final StringBuilder out = new StringBuilder(40);
        for (final byte b : digest.digest(text.toString().getBytes(StandardCharsets.UTF_8))) {
            out.append(String.format("%02x", b));
        }
        return out.toString();
    }

    private static String hex(final int rgb) {
        return String.format("%02x%02x%02x", SkinBake.red(rgb), SkinBake.green(rgb), SkinBake.blue(rgb));
    }

    private static int[] read(final String resource) throws IOException {
        final BufferedImage image = image(resource);
        if (image == null) {
            return null;
        }
        final int[] out = new int[image.getWidth() * image.getHeight()];
        image.getRGB(0, 0, image.getWidth(), image.getHeight(), out, 0, image.getWidth());
        return out;
    }

    private static int width(final String resource) throws IOException {
        final BufferedImage image = image(resource);
        return image == null ? 0 : image.getWidth();
    }

    private static BufferedImage image(final String resource) throws IOException {
        try (InputStream stream = SkinBakeTest.class.getResourceAsStream(resource)) {
            return stream == null ? null : ImageIO.read(stream);
        }
    }
}
