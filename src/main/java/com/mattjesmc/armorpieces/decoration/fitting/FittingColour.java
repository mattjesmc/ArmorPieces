package com.mattjesmc.armorpieces.decoration.fitting;

/**
 * How a masked fitting colours its region of the part - the answer a {@link Fitting.Masked} gives
 * the client's texture baker, stated in terms the baker already understands.
 *
 * <p>Two shapes and no more, because the baker already has exactly two ways to colour a pixel: through
 * a trim material's palette (the way the part's own metal is coloured) or around a fixed colour (the
 * way the static layer's ivory and cloth are). A fitting that names one of these gets the same ramp,
 * the same shading rules and the same darker-variant handling as the rest of the part, with no
 * client code of its own. Sealed on purpose: a third way to colour a pixel would be a change to the
 * baker, not to a fitting.
 *
 * <p>This type is common code even though only the client acts on it, so that a fitting - which is
 * common code, since the server validates and stores it - can describe its colour without a client
 * class on its classpath.
 */
public sealed interface FittingColour {
    /**
     * Coloured through a trim material palette, named by its sprite suffix ({@code gold},
     * {@code gold_darker}, {@code emerald}) exactly as the part's own material is.
     */
    record Palette(String suffix) implements FittingColour {}

    /** Coloured around one fixed colour, {@code 0xRRGGBB}, shaded by the mask's own values. */
    record Solid(int rgb) implements FittingColour {}
}
