package com.mattjesmc.armorpieces.client.texture;

import com.mojang.blaze3d.platform.NativeImage;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.minecraft.util.ARGB;
import org.jspecify.annotations.Nullable;

/**
 * One material's colour ramp, flattened to a 256-entry table keyed by a master's luminance.
 *
 * <p>This is the whole reason a part no longer ships a texture per material. Vanilla has always
 * worked this way for trims - a trim pattern is ONE greyscale PNG, and {@code paletted_permutations}
 * in {@code atlases/armor_trims.json} stitches every pattern-by-material sprite at load time by
 * remapping that greyscale through each material's eight-stop palette. Decorations were the odd one
 * out, shipping the cross product on disk. They now do what vanilla does, through the same palettes.
 *
 * <p><b>Why the ramp has three stops and not eight.</b> Vanilla's sprite source substitutes only
 * colours matching a key stop EXACTLY, which works because trim patterns are authored in precisely
 * those eight greys. Decoration masters are not: they are smoothly shaded, using 54-146 distinct
 * luminance levels each. Interpolating across all eight stops instead is the obvious repair, but it
 * is wrong, and measurably so - vanilla's own trim art has a mean palette index of 4.98 out of 0-7,
 * with the two darkest stops accounting for 1.5% of its pixels because they are outline colours, not
 * shading. Spreading a master evenly over all eight stops therefore lands it around index 3.5 and
 * renders every part far darker than the trim it is supposed to sit beside.
 *
 * <p>So the ramp keeps the three-stop shape the parts were authored against, with each stop taken
 * from the material's own palette rather than from a hand-sampled table: the darkest stop, the stop
 * vanilla's trim art centres on, and the lightest. Measured against the 288 textures the mod used to
 * ship, that reproduces them to within 15.6/255 mean channel error and 8.4/255 mean brightness,
 * where an even spread drifts by 24.6 and 22.6. Same palettes, same look, one file per part.
 */
@Environment(EnvType.CLIENT)
final class DecorationPalette {
    /**
     * Where the ramp's MID stop sits between the palette's darkest and lightest, as a fraction.
     *
     * <p>5/7 because vanilla's trim art centres on palette index 4.98 of 0-7 (measured over the 18
     * shipped humanoid trim patterns), and a decoration is meant to read as the same metal as a trim
     * beside it. Expressed as a fraction rather than an index so a palette that is not eight stops
     * long still maps sensibly.
     */
    private static final float MID_STOP = 5.0F / 7.0F;

    /** Indexed by a master pixel's luminance; values are opaque ARGB. Alpha comes from the master. */
    private final int[] byLuminance;

    private DecorationPalette(final int[] byLuminance) {
        this.byLuminance = byLuminance;
    }

    /** The colour a master pixel of this luminance takes. */
    int rgb(final int luminance) {
        return this.byLuminance[luminance];
    }

    /**
     * Builds a ramp from a palette key and a material palette, the same pair vanilla's atlas uses.
     *
     * <p>The key is what orders the palette: stops are paired with it by index and sorted by their
     * key grey, so a palette file written lightest-first and one written darkest-first both come out
     * the same way round. Only the ordering is taken from the key - see the class note on why the
     * three stops are then picked by position rather than by matching greys exactly.
     *
     * @return null if the two images do not describe at least two usable stops, which means the pack
     *     supplied something that is not a palette; the caller then leaves the part untinted.
     */
    static @Nullable DecorationPalette of(final NativeImage key, final NativeImage palette) {
        final int stops = Math.min(pixelCount(key), pixelCount(palette));
        if (stops < 2) {
            return null;
        }

        final int[] greys = new int[stops];
        final int[] colours = new int[stops];
        for (int i = 0; i < stops; i++) {
            greys[i] = ARGB.red(pixel(key, i));
            colours[i] = pixel(palette, i);
        }
        sortByGreyAscending(greys, colours);
        if (greys[0] == greys[stops - 1]) {
            return null;
        }

        return new DecorationPalette(ramp(
            colours[0],
            stopAt(colours, (stops - 1) * MID_STOP),
            colours[stops - 1]));
    }

    /**
     * Builds a ramp around a single colour, for the parts of a master that are not metal.
     *
     * <p>Reproduces the authoring tool's rule exactly - the static colour is the ramp's MID stop, the
     * dark stop is half of it and the light stop is halfway to white - so a horn's keratin, a sash's
     * cloth and a plume's feather keep the shading painted into the master while ignoring the
     * material entirely. Symmetric on purpose: vanilla's hand-made palettes sit at no consistent
     * ratio to their own mid stop, so there is nothing to match, and a stated rule is something an
     * author can predict where a fitted one would not be.
     */
    static DecorationPalette ofStaticColour(final int rgb) {
        final int r = ARGB.red(rgb);
        final int g = ARGB.green(rgb);
        final int b = ARGB.blue(rgb);
        return new DecorationPalette(ramp(
            rgb(Math.round(r * 0.5F), Math.round(g * 0.5F), Math.round(b * 0.5F)),
            rgb(r, g, b),
            rgb(
                Math.round(r + (255 - r) * 0.5F),
                Math.round(g + (255 - g) * 0.5F),
                Math.round(b + (255 - b) * 0.5F))));
    }

    /**
     * The three-stop ramp as a lookup table, with the mid stop at luminance 127.
     *
     * <p>Shared by both ramps above so a static region and a metal one shade identically, which is
     * what lets a horn's ferrule sit against its keratin without a seam.
     */
    private static int[] ramp(final int dark, final int mid, final int light) {
        final int[] table = new int[256];
        for (int v = 0; v < 256; v++) {
            table[v] = v <= 127
                ? lerp(dark, mid, v / 127.0F)
                : lerp(mid, light, (v - 127) / 128.0F);
        }
        return table;
    }

    /** The colour at a fractional position along the palette, interpolating between its stops. */
    private static int stopAt(final int[] colours, final float position) {
        final int low = (int) position;
        final int high = Math.min(low + 1, colours.length - 1);
        return lerp(colours[low], colours[high], position - low);
    }

    private static int pixelCount(final NativeImage image) {
        return image.getWidth() * image.getHeight();
    }

    /** Row-major, so a palette laid out as 8x1 and one laid out as 4x2 read the same. */
    private static int pixel(final NativeImage image, final int index) {
        return image.getPixel(index % image.getWidth(), index / image.getWidth());
    }

    /** Insertion sort: a palette is eight stops, and this keeps the pairing between the arrays. */
    private static void sortByGreyAscending(final int[] greys, final int[] colours) {
        for (int i = 1; i < greys.length; i++) {
            final int grey = greys[i];
            final int colour = colours[i];
            int j = i - 1;
            while (j >= 0 && greys[j] > grey) {
                greys[j + 1] = greys[j];
                colours[j + 1] = colours[j];
                j--;
            }
            greys[j + 1] = grey;
            colours[j + 1] = colour;
        }
    }

    /**
     * Straight linear interpolation in sRGB, matching the authoring tool rather than being
     * perceptually correct. The stops are close together, so the difference is invisible, and
     * matching the tool means the shipped look does not shift under anyone's feet.
     */
    private static int lerp(final int a, final int b, final float t) {
        return rgb(
            Math.round(ARGB.red(a) + (ARGB.red(b) - ARGB.red(a)) * t),
            Math.round(ARGB.green(a) + (ARGB.green(b) - ARGB.green(a)) * t),
            Math.round(ARGB.blue(a) + (ARGB.blue(b) - ARGB.blue(a)) * t));
    }

    private static int rgb(final int r, final int g, final int b) {
        return 0xFF000000 | (r << 16) | (g << 8) | b;
    }
}
