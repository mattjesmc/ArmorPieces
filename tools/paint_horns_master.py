"""
Paint the grayscale master AND the static colour layer for the "horns" part.

Kept as a script rather than a checked-in binary so the shape stays editable and reviewable: the
CUBES table below is the same cube list as
assets/armorpieces/armorpieces/decoration/horns.json, and a change to one is meant to be a change to
the other. Output goes to tools/decoration_masters/horns.png and horns_static.png, which
sync_decoration_masters.py installs for the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette. This part is 100% opaque -
a horn has no fringe to carve away, and parts draw with armorCutoutNoCull, so a hole punched anywhere
would show the *inside* of the horn rather than the sky behind it.

**This is the first part with a static layer, and it is the reason the layer exists.** A horn is
keratin. Painted entirely through a material ramp it becomes a metal ornament in the shape of a horn,
which is most of why the shape this replaced read as a wing: nothing about a solid gold blade says
"horn" no matter what curve it is bent on. So the shaft is ivory, held constant across all sixteen
materials, and the material shows only where the fiction says metal actually is:

  * the **boss** - the socket bolted through the helmet wall, hardware in its entirety;
  * a **ferrule** one row wide around horn1, a collar banding the shaft a third of the way up;
  * the **cap** over horn3's last two axial rows, the metal tip a mounted horn is finished with.

Three zones, spread base / middle / tip, so the material reads along the whole length rather than
pooling at one end. The static layer supplies colour only - the master's value channel still shades
it - so the growth rings and the face lighting below apply to ivory and metal alike.

The shape is a bull/ibex arc rather than the rake it replaces, and the numbers that define it were
checked against the body before being written:

  * **Cross-section is square and tapers hard** - 3x3, 2x2, 1x1. The part this replaces was 2 wide by
    3 deep, and a section deeper front-to-back than it is wide is a blade in the sagittal plane.
  * **Depth is confined to z -2..2**, the head box's own depth, against the old 7.8 units of spread.
    This is the single largest reason the silhouette changed: length that goes backwards reads as
    sweep, and sweep reads as wing.
  * **The arc curls inward.** Z rotation runs cumulative 37, 19, -13 - out, up, then past vertical
    so the tip leans back over the skull. A monotonic splay would be a spike.
  * **Tip at head (7.97, -14.36, 0.75)**: 5.4 above the helmet top against the old 6.2, and the pair
    spans 17.9 against the shoulders' 18. Both ceilings are the ones the feathering established -
    a horn that reaches the crest's height competes with it for the top of the silhouette.

The boss is 3 tall and not 4 for the reason it always was: a 4-tall boss puts its up face on head
y = -9, which is the helmet's own top plane, and coplanar faces z-fight.

The face layout was measured, not recalled - see paint_circlet_master.faces(): row one (v .. v+d)
holds up then down, each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west,
south with widths d, w, d, w. Note the row-two order: the two thin d-wide faces come FIRST and THIRD.

One horn is drawn twice, the second with scale(-1, 1, 1). bb = (-geo_x, 24 - geo_y, geo_z), so
Blockbench's `west` is the geo +x face - the one facing away from the head - and `east` is the one
facing the skull. After the mirror that is still true, so the outward face can be the lit one on both
sides and the pair reads as a pair.
"""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tools" / "decoration_masters" / "horns.png"
OUT_STATIC = ROOT / "tools" / "decoration_masters" / "horns_static.png"

TEX_W, TEX_H = 64, 32

# size (w, h, d), uv (u, v), and the axial height of the cube's `up` face, mirroring horns.json.
# `h` runs along the horn's own axis, so a side face's rows ARE the axial direction: row 0 is the
# tip-ward end of that cube. axial_top is that row's position on the shared axis, measured up from
# the boss's underside at the temple. Each segment overhangs one unit into the one below it, which is
# what keeps the rotated joints closed, so the axial spans overlap by one: the chain advances h - 1
# per segment and the whole horn is 10 units of axis, which the geometry's traced reach confirms.
CUBES = {
    "boss":  ((3, 3, 4), (0, 0), 3),     # the socket, straddling the helmet wall - 1 unit buried
    "horn1": ((3, 4, 3), (14, 0), 6),    # first segment, 37 deg outboard and 6 deg back
    "horn2": ((2, 3, 2), (26, 0), 8),    # second, cumulative 19 / 12 - the arc turning up
    "horn3": ((1, 3, 1), (34, 0), 10),   # the tip, cumulative -13 / 13 - past vertical, curling in
}

random.seed(41)  # deterministic output - regenerating must not churn the PNG

# Light from above and from outboard, which is where a horn on a standing figure is lit from: the
# outward face is the bright one, the two flanks fall off front to back, and the face against the
# skull sits in its shadow.
UP = 248        # the tip-ward cap of a segment
DOWN = 30       # the base-ward cap; only the boss's is ever seen, from below
WEST = 226      # outward, away from the head - the lit face
NORTH = 172     # front
SOUTH = 138     # back
EAST = 74       # inward, against the skull
INNER = 90      # buried in another cube or in the helmet - painted anyway, in case an anchor moves

RING = -70      # a growth ring, cut into whatever face value it lands on
LIP = 24        # the row immediately tip-ward of a ring, catching the light off the groove's edge
RIVET = 26      # the boss's mounting stud

# The ivory darkens toward the point rather than brightening, which is the opposite of what the part
# this replaces did and is what horn actually does - the growing end is the pale one. Applied over
# the full 10 units of axis, and only to the keratin: the three metal zones get METAL_GAIN instead,
# so the ferrule and the cap sit at the bright end of their material's ramp and read as metal against
# the shaft rather than as a stain on it.
KERATIN_FADE = -34
METAL_GAIN = 22

# Read as the mid stop of its own ramp by DecorationPalette.ofStaticColour, so this is the value
# the master's 127 maps to; 50% of it is the shadow and halfway to white is the highlight. A warm
# off-white a shade deeper than bone, so the shading has somewhere to go in both directions.
KERATIN = (0xC9, 0xBC, 0x9E)

# Axial rows that are metal rather than keratin. The boss is metal in its entirety and is not listed.
FERRULE = 4          # one row of horn1, a collar a third of the way up the shaft
CAP_FROM = 8         # horn3 from here to the point - its last two axial rows


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


def axial(top: int, row: int) -> float:
    """Where a side face's row sits on the horn's shared axis. Row 0 is the tip-ward end."""
    return top - row - 0.5


def is_metal(name: str, a: float) -> bool:
    """Whether the axial position on this cube is one of the three material zones."""
    if name == "boss":
        return True
    if name == "horn1":
        return int(a) == FERRULE
    if name == "horn3":
        return a >= CAP_FROM
    return False


def ring_shift(a: float) -> int:
    """The ring cut at this axial position: the groove itself, or the lit row just above it.

    Period 3, phased to land mid-segment rather than at a joint, where the step already reads. Cut
    deep - at 1 to 3 pixels of face width there is no room for a subtle groove. Metal zones do not
    call this: a ferrule is turned, not grown.
    """
    if int(a) % 3 == 1:
        return RING
    if int(a) % 3 == 2:
        return LIP
    return 0


def shade(name: str, base: int, a: float) -> int:
    """One row's value: its face's base, its ring, and the gradient for whichever material it is."""
    if is_metal(name, a):
        return base + round(METAL_GAIN * a / 10.0)
    return base + ring_shift(a) + round(KERATIN_FADE * a / 10.0)


def put(img, x: int, y: int, lum: int, alpha: int = 255) -> None:
    if 0 <= x < TEX_W and 0 <= y < TEX_H:
        img.putpixel((x, y), (max(0, min(255, lum)), alpha))


def put_static(img, x: int, y: int, metal: bool) -> None:
    """The static layer is keratin where the fiction says horn and transparent where it says metal,
    since a transparent static pixel is exactly what lets the material ramp through."""
    if 0 <= x < TEX_W and 0 <= y < TEX_H and not metal:
        img.putpixel((x, y), (KERATIN[0], KERATIN[1], KERATIN[2], 255))


def fill_cap(img, static, rect, name: str, lum: int, a: float, jitter: int = 5) -> None:
    """A cube's up or down face - one axial position across the whole rectangle."""
    x0, y0, w, h = rect
    metal = is_metal(name, a)
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            put(img, x, y, lum + random.randint(-jitter, jitter))
            put_static(static, x, y, metal)


def paint_side(img, static, rect, name: str, base: int, top: int) -> None:
    """One of the four faces running along the horn's axis: rings across, gradient toward the tip."""
    x0, y0, w, h = rect
    for j in range(h):
        a = axial(top, j)
        lum = shade(name, base, a)
        metal = is_metal(name, a)
        for i in range(w):
            put(img, x0 + i, y0 + j, lum + random.randint(-4, 4))
            put_static(static, x0 + i, y0 + j, metal)


def paint_segment(img, static, name: str, inner_east: bool = False) -> None:
    size, uv, top = CUBES[name]
    f = faces(size, uv)
    # The two caps sit at the ends of this cube's own axial span, not at the shared axis's ends.
    fill_cap(img, static, f["up"], name, shade(name, UP, top), top)
    fill_cap(img, static, f["down"], name, DOWN if name == "boss" else INNER,
             top - size[1], jitter=4)
    paint_side(img, static, f["east"], name, INNER if inner_east else EAST, top)
    paint_side(img, static, f["north"], name, NORTH, top)
    paint_side(img, static, f["west"], name, WEST, top)
    paint_side(img, static, f["south"], name, SOUTH, top)


def paint_boss_rivet(img) -> None:
    """A stud on the boss's outward face, so the socket reads as hardware bolted through the helmet
    rather than as the horn simply growing thicker. One stud, centred: the face is 4 wide by 3 tall,
    and two would leave no unmarked pixel between them. The boss is metal throughout, so the stud
    needs no static entry - it is already the one thing on the part that should be."""
    size, uv, _ = CUBES["boss"]
    x0, y0, _, _ = faces(size, uv)["west"]
    for i in (1, 2):
        put(img, x0 + i, y0 + 1, WEST + RIVET + random.randint(-3, 3))


def main() -> None:
    img = Image.new("LA", (TEX_W, TEX_H), (0, 0))
    static = Image.new("RGBA", (TEX_W, TEX_H), (0, 0, 0, 0))
    # The boss's inward face is inside the head box, a unit behind the helmet wall; the three horn
    # segments' inward faces clear the helmet and are seen head-on from the front.
    paint_segment(img, static, "boss", inner_east=True)
    paint_boss_rivet(img)
    paint_segment(img, static, "horn1")
    paint_segment(img, static, "horn2")
    paint_segment(img, static, "horn3")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    static.save(OUT_STATIC)
    print(f"wrote {OUT}")
    print(f"wrote {OUT_STATIC}")


if __name__ == "__main__":
    main()
