package com.mattjesmc.armorpieces.client.item;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.awt.image.BufferedImage;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.stream.Stream;
import javax.imageio.ImageIO;
import net.minecraft.util.ARGB;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.MethodSource;

/**
 * Holds the skin template's icon to the card it is set in.
 *
 * <p>The icon is drawn in the game now rather than generated into the resources, which is what lets
 * a PACK'S skin have one - see {@link SkinTemplateItemModel}. The cost of that is that nobody looks
 * at the file any more, so the two things a swatch has to get right are checked here instead: that
 * it lands inside the card's recess and nowhere else, and that it is LEVELLED - a skin drawn in a
 * narrow band of greys must still come out spanning the card's full range, or fourteen skins are one
 * icon fourteen times.
 */
class SkinTemplateIconTest {
    private static final Path SKINS =
        Path.of("src", "main", "resources", "assets", "armorpieces", "textures", "entity", "skin");

    /** The card's own colours, as {@code tools/gen_template_icons.py} draws the other twelve. */
    private static final int OUTLINE = 0xFF2B251C;
    private static final int RECESS = 0xFF363128;
    /** The band a swatch is levelled into. */
    private static final int SWATCH_LO = 0x4A;
    private static final int SWATCH_HI = 0xE8;
    /** The swatch is 8 wide and 10 tall, centred in the 10x10 recess at (3, 3). */
    private static final int SWATCH_X = 4;
    private static final int SWATCH_Y = 3;
    private static final int SWATCH_WIDTH = 8;
    private static final int SWATCH_HEIGHT = 10;

    static Stream<String> skins() throws IOException {
        Assumptions.assumeTrue(Files.isDirectory(SKINS), SKINS + " is missing");
        try (Stream<Path> entries = Files.list(SKINS)) {
            return entries.filter(dir -> Files.isRegularFile(dir.resolve("humanoid.png")))
                .map(dir -> dir.getFileName().toString())
                .toList()
                .stream();
        }
    }

    @ParameterizedTest
    @MethodSource("skins")
    void iconIsTheCardWithThisSkinInIt(final String skin) throws IOException {
        final int[] icon = drawn(skin);
        assertEquals(SkinTemplateIcon.SIZE * SkinTemplateIcon.SIZE, icon.length, "icon size");

        // The card is untouched everywhere the swatch is not: its outline, and the two recess
        // columns the 8-wide swatch does not reach.
        assertEquals(OUTLINE, icon[1 * SkinTemplateIcon.SIZE + 1], "card outline");
        assertEquals(RECESS, icon[SWATCH_Y * SkinTemplateIcon.SIZE + 3], "recess left of the swatch");
        assertEquals(RECESS, icon[SWATCH_Y * SkinTemplateIcon.SIZE + 12], "recess right of the swatch");

        // Every drawn texel is opaque and grey, and together they span the card's whole band. A skin
        // whose chest is one flat value is the one case that cannot span it, and there is none.
        int low = 255;
        int high = 0;
        int drawnTexels = 0;
        for (int row = 0; row < SWATCH_HEIGHT; row++) {
            for (int col = 0; col < SWATCH_WIDTH; col++) {
                final int pixel = icon[(SWATCH_Y + row) * SkinTemplateIcon.SIZE + SWATCH_X + col];
                if (pixel == RECESS) {
                    continue;
                }
                assertEquals(255, ARGB.alpha(pixel), skin + ": swatch texel is not opaque");
                assertEquals(ARGB.red(pixel), ARGB.green(pixel), skin + ": swatch texel is not grey");
                assertEquals(ARGB.red(pixel), ARGB.blue(pixel), skin + ": swatch texel is not grey");
                low = Math.min(low, ARGB.red(pixel));
                high = Math.max(high, ARGB.red(pixel));
                drawnTexels++;
            }
        }
        // Not "most of it": chainmail is vanilla's weave, and vanilla draws its chest front with
        // 39 of these 80 texels. What matters is that the recess is not left empty.
        assertTrue(drawnTexels > 0, skin + ": nothing of the chest's front is drawn");
        assertEquals(SWATCH_LO, low, skin + ": darkest swatch texel");
        assertEquals(SWATCH_HI, high, skin + ": lightest swatch texel");
    }

    private static int[] drawn(final String skin) throws IOException {
        final BufferedImage sheet = ImageIO.read(SKINS.resolve(skin).resolve("humanoid.png").toFile());
        final int[] pixels = new int[sheet.getWidth() * sheet.getHeight()];
        for (int y = 0; y < sheet.getHeight(); y++) {
            for (int x = 0; x < sheet.getWidth(); x++) {
                pixels[y * sheet.getWidth() + x] = sheet.getRGB(x, y);
            }
        }
        return SkinTemplateIcon.draw(pixels, sheet.getWidth(), sheet.getHeight());
    }
}
