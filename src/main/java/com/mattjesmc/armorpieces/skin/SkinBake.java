package com.mattjesmc.armorpieces.skin;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Colouring a skin's greyscale master with an armor material's own palette - the whole of the
 * arithmetic, and nothing else. No resources, no textures, no client: pixels in, pixels out, so that
 * this can be held to the same numbers the tool that draws the skins is held to.
 *
 * <p>It is the same trade {@code DecorationTextureManager} makes for a part - one greyscale master,
 * baked per material at load - but the ramp is DERIVED rather than read out of a palette file, and
 * that is the point of the whole feature:
 *
 * <ol>
 *   <li><b>Eight shades, out of the material's own texture.</b> Every opaque texel of
 *       {@code humanoid} and {@code humanoid_leggings} for that material, pooled and sorted by
 *       luminance; eight stops spaced along the 5th-to-95th percentile of that range, each taking
 *       the median colour of the texels nearest it. Not the median of each octile, which is how this
 *       was first written down: an armor texture spends most of its texels on one or two values, so
 *       four of the eight octiles came back the same colour and half the ramp was flat.</li>
 *   <li><b>Deepened to {@link #MIN_SPAN}.</b> Iron's eight shades span forty-six levels of luma;
 *       baked straight, a master drawn across its whole range would be flattened right back down to
 *       iron's, which is the very thing a skin exists to fix. So the lightest shade stays exactly
 *       where the material put it and the darker ones are pushed down, in place, until the eight of
 *       them span {@link #MIN_SPAN}. Each keeps its hue and its saturation - it is scaled toward
 *       black, not desaturated - so the material still reads as itself.</li>
 *   <li><b>Vanilla's own lighting mixed back over the master.</b> A master is a PATTERN: it says
 *       where the flutes and the scales and the quilting are. What it cannot say is that the top of
 *       a shoulder catches the light, that a plate has an edge, that there is shadow under an
 *       overhang - and vanilla's textures carry all of it. So the material's deviation from the
 *       middle of its own range is added to the master's value before the table is read, normalised
 *       by that material's own spread so netherite's dark sheet and gold's bright one contribute the
 *       same amount of SHAPE rather than their own contrast.</li>
 * </ol>
 *
 * <p>What it buys: a skinned iron helmet still reads as IRON beside an unskinned one, because every
 * colour in it is one iron really uses; and a modded armor material is skinned for free, because the
 * only thing wanted from it is a texture it already ships. No palette file exists to fall out of
 * date.
 *
 * <p>The reference implementation is {@code tools/bake_skin.py}, which is what the skins were drawn
 * against in Blockbench; {@code docs/plans/skin-bake-reference.json} is what the two are held to.
 * Where the arithmetic looks over-specified - half-to-even rounding, truncating percentile indices,
 * the median of a bucket sorted by RGB - it is because the two implementations have to agree texel
 * for texel or a skin looks one way in Blockbench and another in game.
 *
 * <p>Pixels are ARGB ints throughout, which is what {@code NativeImage} deals in.
 */
public final class SkinBake {
    /** How many shades are taken out of a material. The master is drawn against these. */
    public static final int SHADES = 8;
    /** The least luma the eight shades may span before the darker ones are pushed down. */
    public static final int MIN_SPAN = 100;
    /** Deepening never drives the darkest shade below this, so nothing bakes to pure black. */
    public static final int FLOOR = 12;
    /** How much of vanilla's own lighting is mixed back over the master. 0 is the pattern alone. */
    public static final float LIGHT_MIX = 0.35f;

    private SkinBake() {}

    // ---- the ramp -------------------------------------------------------------------------------

    /**
     * The eight shades of one material, dark first, every one of them a colour it really uses.
     *
     * @param sheets the material's own vanilla textures as ARGB pixel arrays - both of them, pooled,
     *               because one ramp per MATERIAL is what keeps the leggings from drifting away from
     *               the body they are worn under. Transparent texels are ignored.
     * @return eight RGB colours, or null if the material paints nothing at all.
     */
    public static int[] ramp(final List<int[]> sheets) {
        final List<Integer> opaque = new ArrayList<>();
        for (final int[] sheet : sheets) {
            for (final int pixel : sheet) {
                if (alpha(pixel) != 0) {
                    opaque.add(pixel);
                }
            }
        }
        if (opaque.isEmpty()) {
            return null;
        }

        final double[] values = new double[opaque.size()];
        for (int i = 0; i < values.length; i++) {
            values[i] = luma(opaque.get(i));
        }
        Arrays.sort(values);
        double lo = values[(int) (0.05 * (values.length - 1))];
        double hi = values[(int) (0.95 * (values.length - 1))];
        if (hi <= lo) {
            lo = values[0];
            hi = values[values.length - 1];
        }

        // Every colour the material uses, bucketed by its rounded luma. The bucket's MEDIAN is taken
        // rather than its mean so the shade is a colour the texture actually contains.
        final Map<Integer, List<Integer>> byValue = new HashMap<>();
        for (final int pixel : opaque) {
            byValue.computeIfAbsent(round(luma(pixel)), key -> new ArrayList<>()).add(pixel & 0x00FFFFFF);
        }
        final int[] keys = byValue.keySet().stream().mapToInt(Integer::intValue).sorted().toArray();

        final int[] shades = new int[SHADES];
        for (int i = 0; i < SHADES; i++) {
            final double target = lo + (hi - lo) * i / (SHADES - 1);
            int nearest = keys[0];
            double best = Math.abs(keys[0] - target);
            for (final int key : keys) {
                // Keys ascend, so a strict improvement leaves the SMALLER value holding a tie -
                // which is the tie-break the reference implementation makes.
                final double distance = Math.abs(key - target);
                if (distance < best) {
                    best = distance;
                    nearest = key;
                }
            }
            final List<Integer> bucket = new ArrayList<>(byValue.get(nearest));
            bucket.sort(SkinBake::compareRgb);
            shades[i] = bucket.get(bucket.size() / 2);
        }
        return deepen(shades);
    }

    /**
     * The darker shades pushed down until the eight of them span {@link #MIN_SPAN} luma. The
     * lightest is left exactly where the material put it: the highlight of a skinned piece is
     * literally the material's own, and only the form below it is given room.
     */
    public static int[] deepen(final int[] shades) {
        final double hi = luma(shades[SHADES - 1]);
        final double lo = luma(shades[0]);
        if (hi - lo >= MIN_SPAN || hi <= lo) {
            return shades;
        }
        final double scale = Math.min(MIN_SPAN / (hi - lo), (hi - FLOOR) / (hi - lo));
        final int[] out = new int[SHADES];
        for (int i = 0; i < SHADES; i++) {
            final double value = luma(shades[i]);
            if (value <= 0) {
                out[i] = shades[i];
                continue;
            }
            final double factor = Math.max(0.0, hi - (hi - value) * scale) / value;
            out[i] = rgb(
                clamp(round(red(shades[i]) * factor), 0, 255),
                clamp(round(green(shades[i]) * factor), 0, 255),
                clamp(round(blue(shades[i]) * factor), 0, 255));
        }
        return out;
    }

    /**
     * A 256-entry lookup from a master's value to the material's colour.
     *
     * <p>The eight shades sit at the centres of their eight bands and are interpolated between, and
     * the ends are flat: the extremes of the master's range reach the material's own darkest and
     * lightest texel rather than stopping an eighth short of them.
     */
    public static int[] table(final int[] shades) {
        final double[] stops = new double[SHADES];
        for (int i = 0; i < SHADES; i++) {
            stops[i] = (i + 0.5) * 256.0 / SHADES;
        }
        final int[] out = new int[256];
        for (int value = 0; value < 256; value++) {
            if (value <= stops[0]) {
                out[value] = shades[0];
                continue;
            }
            if (value >= stops[SHADES - 1]) {
                out[value] = shades[SHADES - 1];
                continue;
            }
            for (int i = 0; i < SHADES - 1; i++) {
                if (stops[i] <= value && value <= stops[i + 1]) {
                    final double t = (value - stops[i]) / (stops[i + 1] - stops[i]);
                    out[value] = rgb(
                        round(red(shades[i]) + (red(shades[i + 1]) - red(shades[i])) * t),
                        round(green(shades[i]) + (green(shades[i + 1]) - green(shades[i])) * t),
                        round(blue(shades[i]) + (blue(shades[i + 1]) - blue(shades[i])) * t));
                    break;
                }
            }
        }
        return out;
    }

    // ---- the lighting ---------------------------------------------------------------------------

    /**
     * Vanilla's lighting for one sheet of one material: a signed amount to add to each master texel
     * before the table is read.
     *
     * <p>Measured from the MIDDLE of the material's own range rather than its median - an armor
     * texture sits at one end of its own range, so a median-centred map would only ever brighten -
     * and normalised by that material's own spread, which is what makes iron, gold and netherite
     * contribute the same amount of shape. A texel vanilla does not paint contributes nothing.
     *
     * @return one entry per pixel of {@code sheet}, in the same order; all zeroes if it is empty.
     */
    public static byte[] lightmap(final int[] sheet, final float mix) {
        final byte[] out = new byte[sheet.length];
        final double[] values = new double[sheet.length];
        int count = 0;
        for (final int pixel : sheet) {
            if (alpha(pixel) != 0) {
                values[count++] = luma(pixel);
            }
        }
        if (count == 0) {
            return out;
        }
        final double[] sorted = Arrays.copyOf(values, count);
        Arrays.sort(sorted);
        final double lo = sorted[(int) (0.05 * (count - 1))];
        final double hi = sorted[(int) (0.95 * (count - 1))];
        final double middle = (lo + hi) / 2;
        final double spread = Math.max(1.0, hi - lo);
        for (int i = 0; i < sheet.length; i++) {
            if (alpha(sheet[i]) == 0) {
                continue;
            }
            final double offset = Math.max(-0.5, Math.min(0.5, (luma(sheet[i]) - middle) / spread));
            out[i] = (byte) round(mix * 255 * offset);
        }
        return out;
    }

    /** The lighting map at the mix the skins were drawn against. */
    public static byte[] lightmap(final int[] sheet) {
        return lightmap(sheet, LIGHT_MIX);
    }

    // ---- the bake -------------------------------------------------------------------------------

    /**
     * One master sheet through one material's table. The master's alpha is the silhouette and is
     * kept as it is; its VALUE chooses the colour, lit by {@code light} where there is one.
     *
     * @param light one entry per pixel, or null to bake the pattern alone.
     */
    public static int[] bake(final int[] master, final int[] table, final byte[] light) {
        final int[] out = new int[master.length];
        for (int i = 0; i < master.length; i++) {
            final int pixel = master[i];
            final int alpha = alpha(pixel);
            if (alpha == 0) {
                continue;
            }
            final int red = red(pixel);
            final int green = green(pixel);
            final int blue = blue(pixel);
            // A grey texel is its own value; anything else is weighed the way the ramp weighed the
            // material, so a master that is not quite grey still lands where it looks like it should.
            int value = red == green && green == blue ? red : round(luma(pixel));
            if (light != null && i < light.length) {
                value += light[i];
            }
            out[i] = (alpha << 24) | (table[clamp(value, 0, 255)] & 0x00FFFFFF);
        }
        return out;
    }

    // ---- pixels ---------------------------------------------------------------------------------

    public static double luma(final int argb) {
        return 0.299 * red(argb) + 0.587 * green(argb) + 0.114 * blue(argb);
    }

    public static int alpha(final int argb) {
        return argb >>> 24 & 0xFF;
    }

    public static int red(final int argb) {
        return argb >> 16 & 0xFF;
    }

    public static int green(final int argb) {
        return argb >> 8 & 0xFF;
    }

    public static int blue(final int argb) {
        return argb & 0xFF;
    }

    private static int rgb(final int red, final int green, final int blue) {
        return red << 16 | green << 8 | blue;
    }

    private static int compareRgb(final int left, final int right) {
        if (red(left) != red(right)) {
            return Integer.compare(red(left), red(right));
        }
        if (green(left) != green(right)) {
            return Integer.compare(green(left), green(right));
        }
        return Integer.compare(blue(left), blue(right));
    }

    /**
     * Half-to-even, which is what the reference implementation's language rounds with. Half-up would
     * differ on one texel here and there, and "here and there" is exactly what a digest catches.
     */
    private static int round(final double value) {
        return (int) Math.rint(value);
    }

    private static int clamp(final int value, final int min, final int max) {
        return Math.max(min, Math.min(max, value));
    }
}
