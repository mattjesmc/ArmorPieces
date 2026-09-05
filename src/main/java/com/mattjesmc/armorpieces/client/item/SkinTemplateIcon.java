package com.mattjesmc.armorpieces.client.item;

import com.mojang.blaze3d.platform.NativeImage;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.minecraft.resources.Identifier;
import net.minecraft.server.packs.resources.Resource;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.util.ARGB;

/**
 * A skin template's icon, drawn from the skin itself.
 *
 * <p>A skin is the armor's own surface, so a swatch of that surface is not a symbol for the thing,
 * it IS the thing: the icon is the top ten rows of the skin's own chest front, greyed, levelled into
 * the template card's range and set in the card's recess. It cannot drift from what the player will
 * be wearing, and - the reason this is Java and not a script - a skin added by a PACK gets its icon
 * by existing, which no shipped PNG could do. See {@link SkinTemplateIconSource}, which stitches
 * these onto the item atlas, and {@link SkinTemplateItemModel}, which picks between them.
 *
 * <p>Drawing them by hand was tried and thrown out. Thirteen emblems in one palette at 10x10 come
 * out as thirteen grey lattices, and the ones whose identity is a CULTURE rather than a construction
 * cannot be drawn at that size at all - a spangenhelm needs more texels than the recess has.
 *
 * <p>The card and its palette are the same art {@code tools/gen_template_icons.py} draws the socket
 * templates' icons with, and the two must stay the same card: a hotbar holding a crest template and
 * a skin template should show one family of things.
 */
@Environment(EnvType.CLIENT)
public final class SkinTemplateIcon {
    /** Where a skin's sheets live, and so where the skins that exist are found. */
    private static final String DIRECTORY = "textures/entity/skin";
    /** The sheet the swatch is cut from: the body, which is the one with a chest on it. */
    private static final String BODY_SHEET = "/humanoid.png";

    /**
     * The chest's front face on the humanoid grid - 8 wide, 12 tall at (20, 20).
     *
     * <p>Written here rather than derived, because the grid is vanilla's and cannot move without
     * every armor texture in the game moving with it. {@code tools/skin_sheets.py} is the same
     * rectangle on the authoring side, read out of the model rather than typed.
     */
    private static final int CHEST_X = 20;
    private static final int CHEST_Y = 20;
    private static final int CHEST_WIDTH = 8;
    /**
     * Ten of the face's twelve rows: the collar, the shoulders and the breast, which is where a skin
     * says most about itself - the hem is under a belt half the time. Ten because the recess is ten
     * tall, so NOTHING is resampled: a scaled sheet is a blurred sheet, and at sixteen pixels blur is
     * the one thing a swatch cannot afford.
     */
    private static final int SWATCH_ROWS = 10;

    /**
     * The band the card's own art occupies, from the armor's shadow to its lit edge. Every swatch is
     * levelled into it: a master that lives in the middle of the ramp would otherwise come out as ten
     * shades of one grey, and fourteen of those are one icon fourteen times.
     */
    private static final int SWATCH_LO = 0x4A;
    private static final int SWATCH_HI = 0xE8;

    private static final int TRANSPARENT = 0x00000000;
    private static final int OUTLINE = 0xFF2B251C;
    private static final int FACE = 0xFF9A8F7A;
    private static final int LIT = 0xFFC6BBA4;
    private static final int RECESS = 0xFF363128;

    /**
     * The card, as {@code gen_template_icons.py} draws it: {@code o} outline, {@code h} the lit top
     * edge, {@code f} the face, {@code r} the 10x10 recess at rows 3..12, columns 3..12.
     */
    private static final String[] CARD = {
        "................",
        ".oooooooooooooo.",
        ".ohhhhhhhhhhhho.",
        ".ohrrrrrrrrrrfo.",
        ".ohrrrrrrrrrrfo.",
        ".ohrrrrrrrrrrfo.",
        ".ohrrrrrrrrrrfo.",
        ".ohrrrrrrrrrrfo.",
        ".ohrrrrrrrrrrfo.",
        ".ohrrrrrrrrrrfo.",
        ".ohrrrrrrrrrrfo.",
        ".ohrrrrrrrrrrfo.",
        ".ohrrrrrrrrrrfo.",
        ".offffffffffffo.",
        ".oooooooooooooo.",
        "................",
    };

    private static final int RECESS_ORIGIN = 3;
    private static final int RECESS_SIZE = 10;
    /** The icon's own size, which is the card's. */
    public static final int SIZE = 16;

    /**
     * The skins the last atlas build actually stitched an icon for.
     *
     * <p>The one piece of state here, and it is what lets {@link SkinTemplateItemModel} bake against
     * sprites it knows exist. The order is not a coincidence: the item atlas is built before item
     * models are baked, because a model needs its sprites, so the source has always run by the time
     * the model asks. Written on the atlas thread and read on a baking thread, hence volatile.
     */
    private static volatile Set<Identifier> stitched = Set.of();

    private SkinTemplateIcon() {}

    /** @see #stitched */
    public static Set<Identifier> stitched() {
        return stitched;
    }

    /** Called by the sprite source with what it just put on the atlas. @see #stitched */
    static void stitched(final Set<Identifier> skins) {
        stitched = Set.copyOf(skins);
    }

    /**
     * Every skin any pack ships art for, by asset id - {@code armorpieces:plate} for the pair under
     * {@code assets/armorpieces/textures/entity/skin/plate/}.
     *
     * <p>Keyed by ASSET id and not by the registry id a datapack gives a skin, because the art is
     * what an icon can be drawn from and the art is what this finds. A skin whose data file has not
     * loaded yet still gets a sprite; one that names art nobody ships correctly gets none, and falls
     * back to the generic card.
     */
    public static Map<Identifier, Resource> sheets(final ResourceManager manager) {
        final Map<Identifier, Resource> found = new TreeMap<>(Identifier::compareTo);
        manager.listResources(DIRECTORY, path -> path.getPath().endsWith(BODY_SHEET))
            .forEach((path, resource) -> found.put(assetId(path), resource));
        return found;
    }

    /** {@code ns:textures/entity/skin/plate/humanoid.png} -> {@code ns:plate}. */
    private static Identifier assetId(final Identifier sheet) {
        final String path = sheet.getPath();
        return sheet.withPath(
            path.substring(DIRECTORY.length() + 1, path.length() - BODY_SHEET.length()));
    }

    /**
     * The sprite one skin's icon is stitched under: {@code ns:item/skin_template_plate}.
     *
     * <p>In the skin's OWN namespace, so two packs' skins of the same name cannot collide on the
     * atlas, and so a pack that would rather draw its icon by hand can simply ship that file - a
     * sprite source loses to a real texture of the same name.
     */
    public static Identifier sprite(final Identifier assetId) {
        return assetId.withPath(path -> "item/skin_template_" + path);
    }

    /**
     * The card with this skin's swatch in its recess.
     *
     * <p>The caller owns the image that comes back; the sheet is left alone.
     */
    public static NativeImage draw(final NativeImage sheet) {
        final int[] pixels = new int[sheet.getWidth() * sheet.getHeight()];
        for (int y = 0; y < sheet.getHeight(); y++) {
            for (int x = 0; x < sheet.getWidth(); x++) {
                pixels[y * sheet.getWidth() + x] = sheet.getPixel(x, y);
            }
        }
        final int[] drawn = draw(pixels, sheet.getWidth(), sheet.getHeight());
        final NativeImage icon = new NativeImage(SIZE, SIZE, false);
        for (int y = 0; y < SIZE; y++) {
            for (int x = 0; x < SIZE; x++) {
                icon.setPixel(x, y, drawn[y * SIZE + x]);
            }
        }
        return icon;
    }

    /**
     * The same drawing on plain pixels, which is where the arithmetic actually lives.
     *
     * <p>Split out for the reason {@code SkinBake} is: an image that is an int array can be tested
     * without a graphics context, and an icon that comes out wrong is a thing you want a test for
     * rather than a screenshot.
     *
     * @param sheet  a skin's {@code humanoid} sheet as ARGB, row by row
     * @return the 16x16 icon, ARGB, row by row
     */
    public static int[] draw(final int[] sheet, final int width, final int height) {
        final int[] icon = new int[SIZE * SIZE];
        for (int y = 0; y < CARD.length; y++) {
            final String row = CARD[y];
            for (int x = 0; x < row.length(); x++) {
                icon[y * SIZE + x] = switch (row.charAt(x)) {
                    case 'o' -> OUTLINE;
                    case 'h' -> LIT;
                    case 'f' -> FACE;
                    case 'r' -> RECESS;
                    default -> TRANSPARENT;
                };
            }
        }
        levelledSwatch(sheet, width, height, icon);
        return icon;
    }

    /**
     * The swatch, levelled and composited into the recess.
     *
     * <p>A texel the skin leaves transparent keeps the recess grey, so a chest with a cut in it reads
     * as a cut rather than as a hole in the card.
     */
    private static void levelledSwatch(
        final int[] sheet,
        final int width,
        final int height,
        final int[] icon
    ) {
        if (width < CHEST_X + CHEST_WIDTH || height < CHEST_Y + SWATCH_ROWS) {
            return;
        }
        int low = 255;
        int high = 0;
        for (int row = 0; row < SWATCH_ROWS; row++) {
            for (int col = 0; col < CHEST_WIDTH; col++) {
                final int pixel = sheet[(CHEST_Y + row) * width + CHEST_X + col];
                if (ARGB.alpha(pixel) == 0) {
                    continue;
                }
                final int value = luminance(pixel);
                low = Math.min(low, value);
                high = Math.max(high, value);
            }
        }
        final int span = Math.max(1, high - low);
        final int originX = RECESS_ORIGIN + (RECESS_SIZE - CHEST_WIDTH) / 2;
        final int originY = RECESS_ORIGIN + (RECESS_SIZE - SWATCH_ROWS) / 2;
        for (int row = 0; row < SWATCH_ROWS; row++) {
            for (int col = 0; col < CHEST_WIDTH; col++) {
                final int pixel = sheet[(CHEST_Y + row) * width + CHEST_X + col];
                if (ARGB.alpha(pixel) == 0) {
                    continue;
                }
                final int level = SWATCH_LO
                    + Math.round((luminance(pixel) - low) / (float) span * (SWATCH_HI - SWATCH_LO));
                icon[(originY + row) * SIZE + originX + col] = ARGB.color(255, level, level, level);
            }
        }
    }

    /**
     * A master is greyscale, so any channel would do - but a pack's sheet is not checked by anything
     * this side of the game, and a coloured one should still level sensibly rather than by its red.
     */
    private static int luminance(final int pixel) {
        return Math.round(0.299F * ARGB.red(pixel)
            + 0.587F * ARGB.green(pixel)
            + 0.114F * ARGB.blue(pixel));
    }
}
