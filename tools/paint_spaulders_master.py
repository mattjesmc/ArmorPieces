"""
Paint the grayscale master for the "spaulders" part.

Kept as a script rather than a checked-in binary so the shape stays editable and reviewable: the
CUBES table below is the same cube list as
assets/armorpieces/armorpieces/decoration/spaulders.json, and a change to one is meant to be a
change to the other. Output goes to tools/decoration_masters/spaulders.png, which
sync_decoration_masters.py installs for the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

Like the circlet and the horns and unlike the feathering, this master is 100% opaque. A plate has no
fringe to carve away, and parts draw with armorCutoutNoCull, so a hole punched anywhere would show
the *inside* of the plate rather than the sky behind it. Every pixel here is value.

What this part needs that the horns did not:

  * It is a stack of three plates, and "three plates" is a texture statement more than a geometry
    one. The geometry gives two 15-degree angular breaks; what actually makes a lame read as a lame
    is the pair of rows at its free lower edge - a shadowed row where it tucks under the plate above
    and a bright rim row along the edge that hangs free. Those two rows are the whole idiom, and
    they are applied identically to lame1 and lame2 so the pair reads as a repeating course.

  * Every plate has one unit of itself buried inside the plate above (that is what closes the
    rotated joints), so the top row of every lame's side faces is never seen. Those rows are painted
    at INNER anyway, the way the horns' buried faces were, in case PAULDRONS moves in pass B.

The face rectangles come from paint_circlet_master.faces(), copied verbatim: row one (v .. v+d)
holds up then down, each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west,
south with widths d, w, d, w. Note the row-two order: the two thin d-wide faces come FIRST and THIRD.

The *orientation* inside each rectangle matters here in a way it did not for the horns, because this
part is shaded front-to-back as well as top-to-bottom. It was measured, not recalled - a ramp was
painted into one rectangle at a time and read off the render against a marker cube at a known
coordinate:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        inboard (min x)    back  (max z)
    down            +y  (underside)      inboard (min x)    back  (max z)
    west            +x  (outboard)       front   (min z)    top   (min y)
    east            -x  (inboard)        back    (max z)    top   (min y)
    north           -z  (front)          inboard (min x)    top   (min y)
    south           +z  (back)           outboard(max x)    top   (min y)

Blockbench's face names are used throughout, and they are the ones the flip gives: bb = (-geo_x,
24 - geo_y, geo_z), so Blockbench's `west` is the geo +x face - the one pointing away from the body
for a left-side part - and `east` is the one against the chest. That is what lets one master serve
both shoulders: after the layer's scale(-1, 1, 1) the geo +x face of the mirrored copy still points
outboard, so lit-outboard / shadowed-inboard survives the mirror and the pair reads as a pair.
"""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tools" / "decoration_masters" / "spaulders.png"

TEX_W, TEX_H = 64, 32

# size (w, h, d) and uv (u, v), mirroring spaulders.json. The cap is the plate over the shoulder;
# lame1 and lame2 are the two flaring plates below it, each rotated a further 16 / 14 degrees
# outboard and each burying its top unit in the plate above.
CUBES = {
    "cap":   ((5, 2, 5), (0, 0)),
    "lame1": ((2, 3, 5), (20, 0)),
    "lame2": ((2, 3, 5), (34, 0)),
}

random.seed(53)  # deterministic output - regenerating must not churn the PNG

# Light from above, from the front, and from outboard: the same standing-figure key the horns use.
UP = 246        # the cap's top plate, the one face seen from every angle
WEST = 214      # outboard, away from the body - the lames' hero face
NORTH = 168     # front edge
SOUTH = 128     # back edge
EAST = 62       # inboard, in the slot between the plate and the chestplate
DOWN = 34       # the free underside of the bottom lame
INNER = 84      # buried in another cube of the part or in the sleeve - painted anyway

Z_FALL = 34         # front-to-back falloff across a face's depth
X_GAIN = 18         # inboard-to-outboard brightening across a face's width
PLATE_SHADOW = 52   # the row where a lame tucks under the plate above it
RIM = 24            # the free lower edge of a lame, catching the light off its own break
LAME_GAIN = 8       # each lame down the chain is tilted further outboard, so it takes more sky
RIVET = 30          # a mounting stud

# Calibrated against the ramp rather than guessed. the material ramp interpolates
# dark -> mid over master values 0..127 and mid -> light over 128..255, so a master confined to the
# top half only ever uses half of a material's ramp - the mistake the circlet's first cut made.
# Here the inboard faces and the undersides sit in the 34..84 band and the lames' rim rows saturate,
# so the visible pixels alone run the whole ramp.


def faces(size, uv):
    """Per-face pixel rectangles (x, y, w, h) for one box-UV cube. See the module docstring."""
    w, h, d = size
    u, v = uv
    return {
        "up":    (u + d, v, w, d),
        "down":  (u + d + w, v, w, d),
        "east":  (u, v + d, d, h),
        "north": (u + d, v + d, w, h),
        "west":  (u + d + w, v + d, d, h),
        "south": (u + d + w + d, v + d, w, h),
    }


def put(img, x: int, y: int, lum: int, alpha: int = 255) -> None:
    if 0 <= x < TEX_W and 0 <= y < TEX_H:
        img.putpixel((x, y), (max(0, min(255, lum)), alpha))


def fill(img, rect, lum: int, jitter: int = 4) -> None:
    x0, y0, w, h = rect
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            put(img, x, y, lum + random.randint(-jitter, jitter))


def ramp(i: int, n: int) -> float:
    """Position along a face axis, 0.0 at column/row 0 and 1.0 at the far end."""
    return 0.0 if n <= 1 else i / (n - 1)


def paint_cap(img) -> None:
    """The plate over the shoulder. Its `up` face is the one a player sees from any angle at all,
    so it carries the full front-to-back and inboard-to-outboard gradient and the mounting studs;
    the four side faces are 2 rows tall, of which only the upper one clears the sleeve."""
    size, uv = CUBES["cap"]
    w, h, d = size
    f = faces(size, uv)

    x0, y0, fw, fh = f["up"]
    for j in range(fh):                       # 0 = back .. fh-1 = front
        front = ramp(j, fh)
        for i in range(fw):                   # 0 = inboard .. fw-1 = outboard
            out = ramp(i, fw)
            lum = UP - round(Z_FALL * 0.5 * (1.0 - front)) - round(X_GAIN * (1.0 - out))
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))
    # Two studs down the inboard column, where the cap would be strapped to the chest harness.
    # They sit on the darkest column of the face on purpose: at this scale a highlight only reads
    # against something dark, which is the same reason the horns' rivet sits inside its ring.
    for j in (1, 3):
        put(img, x0, y0 + j,
            UP - round(Z_FALL * 0.5 * (1.0 - ramp(j, fh))) - X_GAIN + RIVET + random.randint(-3, 3))

    x0, y0, fw, fh = f["west"]                # outboard edge; fully clear of the sleeve
    for j in range(fh):
        for i in range(fw):                   # 0 = front .. fw-1 = back
            lum = WEST - round(Z_FALL * ramp(i, fw)) - (0 if j == 0 else 30)
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["north"]               # front edge; the lower row is behind the sleeve
    for j in range(fh):
        for i in range(fw):                   # 0 = inboard .. fw-1 = outboard
            lum = NORTH + round(X_GAIN * ramp(i, fw)) - (0 if j == 0 else 46)
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["south"]               # back edge
    for j in range(fh):
        for i in range(fw):                   # 0 = outboard .. fw-1 = inboard
            lum = SOUTH + round(X_GAIN * (1.0 - ramp(i, fw))) - (0 if j == 0 else 46)
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["east"]                # inboard; seen only through the half-unit slot
    for j in range(fh):
        for i in range(fw):                   # 0 = back .. fw-1 = front
            lum = EAST + round(20 * ramp(i, fw)) - (0 if j == 0 else 24)
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    fill(img, f["down"], INNER)               # inside the sleeve


def paint_lame(img, name: str, step: int, bottom: bool) -> None:
    """One of the two flaring plates. Row 0 of every side face is the unit buried in the plate
    above; row 1 is the band that tucks under it, and the last row is the free lower edge."""
    size, uv = CUBES[name]
    w, h, d = size
    f = faces(size, uv)
    gain = LAME_GAIN * step

    fill(img, f["up"], INNER)                 # buried in the plate above

    if bottom:
        x0, y0, fw, fh = f["down"]            # the free underside of the whole assembly
        for j in range(fh):
            for i in range(fw):
                put(img, x0 + i, y0 + j, DOWN + round(16 * ramp(j, fh)) + random.randint(-3, 3))
    else:
        fill(img, f["down"], INNER)           # buried in the lame below

    x0, y0, fw, fh = f["west"]                # the hero face
    for j in range(fh):
        for i in range(fw):                   # 0 = front .. fw-1 = back
            if j == 0:
                lum = INNER
            else:
                base = WEST + gain + (RIM if j == h - 1 else -PLATE_SHADOW)
                lum = base - round(Z_FALL * ramp(i, fw))
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))
    # Rivets along the shadowed band, two per lame, where the plate laps the one above it.
    for i in (1, 3):
        put(img, x0 + i, y0 + 1,
            WEST + gain - PLATE_SHADOW - round(Z_FALL * ramp(i, fw)) + RIVET + random.randint(-3, 3))

    x0, y0, fw, fh = f["north"]               # front edge of the plate
    for j in range(fh):
        for i in range(fw):                   # 0 = inboard .. fw-1 = outboard
            if j == 0:
                lum = INNER
            else:
                lum = NORTH + gain + round(X_GAIN * ramp(i, fw)) + (RIM if j == h - 1 else -30)
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["south"]               # back edge of the plate
    for j in range(fh):
        for i in range(fw):                   # 0 = outboard .. fw-1 = inboard
            if j == 0:
                lum = INNER
            else:
                lum = SOUTH + gain + round(X_GAIN * (1.0 - ramp(i, fw))) + (RIM if j == h - 1 else -30)
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["east"]                # against the arm; the flare lifts its lower rows clear
    for j in range(fh):
        for i in range(fw):                   # 0 = back .. fw-1 = front
            if j == 0:
                lum = INNER
            else:
                lum = EAST + round(20 * ramp(i, fw)) + (10 if j == h - 1 else 0)
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))


def main() -> None:
    img = Image.new("LA", (TEX_W, TEX_H), (0, 0))
    paint_cap(img)
    paint_lame(img, "lame1", 0, bottom=False)
    paint_lame(img, "lame2", 1, bottom=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
