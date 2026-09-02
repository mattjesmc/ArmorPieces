"""
Paint the grayscale master for the "scale_skirt" part, and the mask for its `guard` fitting.

Like the pelt, puttees, greaves and tassets painters this does not merely claim that CUBES matches
the shipped geometry, it reads assets/armorpieces/armorpieces/decoration/scale_skirt.json at run
time and asserts it (check_geometry) - down to the origins, the pivots and the four bone rotations,
because on this part the origins are the lap and the rotations are what keeps four nearly-parallel
plates from sharing a plane. Output goes to tools/decoration_masters/scale_skirt.png and
scale_skirt_guard.png, which sync_decoration_masters.py installs for the game to colour per trim
material.

Master convention: luminance carries shading, alpha carries silhouette.

This master is 100% opaque, for the greaves' and the pelt's reason. A scalloped hem is exactly what
a scale skirt wants and it does not get one: parts draw with armorCutoutNoCull, so a notch cut in
the front face of a row shows the lit INSIDE of that row's back face, not the thigh behind it. The
hem here is the geometry's own overhang and the value under it.

===========================================================================================
THE TIDAL IDIOM, as head_fins sets it. Quoted, not re-derived - see paint_head_fins_master.py for
the full statement and the reasoning. The three clauses this part is built out of:

1. A SCALE ROW is one cube, and the scales are value across its face. Along the row a scale is TWO
   texels, a lit leading one and the dimmer one the next scale laps; between rows the pattern is
   offset by ONE texel so the boundaries stagger like brickwork instead of ruling a grid; and the
   notch is always SMALLER than the step between a lapped row and a free one, so the eye reads rows
   first and scales second. Row exposures are unequal on purpose.

2. AN EDGE IS A LINE, NEVER A FACE. On this part the edge is the vertical corner where the front of
   the thigh turns into its flank: the last column of `north` and the first column of `west` meet
   there at 90 degrees, and those two columns carry the part's brightest value while everything
   either side of them falls away. That is what CORNER and the two PROFILE tables are for.

3. THE FITTING TAKES THE FIELD; THE FRAME KEEPS THE SMITH'S METAL. Here the field is the three
   scale rows and the frame is the `band` they hang from, so `armorpieces:guard` - a second trim
   material - masks row1, row2 and row3 and leaves the band alone. Scales in bronze on an iron
   binding, and the smithed material still means something because the binding is still made of it.
   The head fins say the same sentence with a dye and a membrane.
===========================================================================================

What this part is, and what that costs the painter:

  * `tassets` is a MIRRORED pair - Attachment.of(LEFT_LEG, 0, 2, 0) plus Attachment.mirrored on the
    right - so the layer's scale(-1, 1, 1) runs on the right-hand copy and ONE master serves both.
    `west` is geo +x, outboard on both legs; `east` is geo -x, inboard on both, and every `east`
    face here is inside the wearer's own thigh.

  * THE LEG SHELLS ARE 0.4 AND 0.9, NOT 0.5 AND 1.0. createBaseArmorMesh re-adds both legs at
    g.extend(-0.1F), so in leg-local terms the leggings' thigh is x -2.4..2.4, y -0.4..12.4,
    z -2.4..2.4 and the boots' is the same box at 0.9. Two shipped painters still carry the old
    +-2.5 and are wrong; every number below is against 2.4. The naked thigh is x -2..2, y 0..12,
    z -2..2, and the leggings TORSO shell - which rides BODY, not this bone - covers leg-local
    x -6.3..2.5, y -12.4..0.4, z -2.4..2.4.

  * The geometry, in numbers. Part-local first (the frame the JSON is authored in, +Y DOWN), then
    leg-local, which is part-local + (0, 2, 0) - the bone frame trace_geometry reports in. All four
    extents are rotated hulls; each cube hangs from its own bone, pivoted ON THE LEG'S AXIS at
    x = 0, and rolled a few degrees about z.

        cube    part-local x      part-local y      part-local z     leg-local y     roll
        band   -0.90 .. 3.00    -2.50 .. -1.22    -3.00 .. 0.35    -0.50 .. 0.78    -2
        row1   -0.60 .. 2.99    -1.85 ..  0.13    -2.90 .. 0.40     0.15 .. 2.13    -3
        row2   -0.73 .. 2.94    -0.44 ..  1.72    -2.70 .. 0.60     1.56 .. 3.72    -6
        row3   -0.85 .. 2.77     0.87 ..  2.90    -2.30 .. 1.00     2.87 .. 4.90    -4

    THE ROLL IS NOT DECORATION. Four plates stacked down a thigh, all axis-aligned, would put eight
    faces in two planes and every one of them a candidate for z-fighting with its neighbour and with
    the leggings shell; the mod's cubes cannot rotate, so a plate that is not parallel to the plate
    above it has to hang from a bone that is not parallel either. -2, -3, -6, -4 are four different
    angles for that reason first. What they buy on top of it is the skirt's line: the pivots sit on
    the leg's own axis, so a negative roll lifts each row's OUTBOARD end and the four hems step up
    towards the hip instead of ruling four horizontal lines across the thigh.

  * THE LAP IS THE ORIGINS. All three scale rows are the SAME CUBE - 3.5 x 1.8 x 3.3 - and differ
    only in where they are put. Each is 0.13 less proud outboard and 0.20 to 0.40 less proud forward
    than the row above it, so every row's lower edge overhangs the row beneath:

        surface   outboard x   proud of the thigh at 2.40   front z   proud of the thigh at -2.40
        band          3.00              0.60                 -3.00              0.60
        row1          2.99              0.59                 -2.90              0.50
        row2          2.94              0.54                 -2.70              0.30
        row3          2.77              0.37                 -2.30             -0.10

    row3's front face is the one surface on the part that is INSIDE the leggings shell, by 0.10, and
    that is deliberate: below leg-local 3.7 the front of the leg belongs to `knees`, so the bottom
    row is a flank row and its `north` face is painted as the buried thing it is. Everything else
    stands clear, and no face of this part lies in a shell plane - trace_geometry reports no
    COPLANAR - which is what the fractional origins are for. 2.99 must not be tidied to 3.00.

  * WHERE THE ROWS LAND, which is the constraint this part was designed around. The leg column is
    crowded in three directions at once and this part is squeezed by all three.

      - BELOW. The shipped poleyns reach UP to leg-local y 3.70 (at z -3.90..-2.90) and 4.20 (at
        z -4.65..-2.65), so the knee's claim on the front of the leg starts far higher than the
        `knees` anchor at y 6 suggests. An exact separating-axis test over the oriented boxes puts
        this part's closest approach to the poleyns at 0.200 - row2 to the upper poleyn, in z - and
        to the shipped garters at 0.494. The hem stops at leg-local 4.90, which is 0.25 above the
        garter's highest cube and 1.10 above the knee anchor.
      - OUTBOARD. The shipped sash's `tail` hangs at leg-local x 3.10..5.10, and it rides BODY, so
        trace_geometry's cross-part pass cannot see it at all - it only measures parts that share
        this bone. The widest thing here is the band at exactly 3.00, which clears that tail by
        0.10. The sash's knot, `belt#5`, reaches leg-local x 2.35 at y -4.50..0.40 and the band does
        run into it by 0.65 in x - the same 0.65 the shipped pelt's thong takes and twice the
        shipped tassets' 0.35, on a pair of parts that separate the moment the leg swings.
      - ABOVE. The band's top edge is at leg-local -0.50, inside the leggings TORSO shell's y range
        but outboard of its x = 2.5 wall over the band's last half unit. So the band's `up` face is
        under the torso at rest and out from under it on every stride - the tassets' finding,
        arriving on a binding - and it is painted as a dimmed ledge rather than as filler.

    trace_geometry reports one OVERLAP, row3 into the heel wings' `vane_upper`. That is the hull
    test over-reporting a rotated cube: the exact separating-axis distance between the two oriented
    boxes is 1.714, and the same test puts greaves at 2.295, puttees at 2.866 and spurs at 2.629.
    Nothing on this leg is closer than the poleyn's 0.200.

  * WHAT IS ACTUALLY SEEN. Four faces of this part draw and the other twenty do not. `north` is the
    front of the thigh and `west` its flank; between them they are the whole read, eight columns of
    scale wrapping a corner. `down` is the overhang under each row - four texels of shadow that is
    the only place the lap is geometry rather than value - and the band's `up` is the ledge above.
    `east` is inside the thigh, `south` is at z 0.35..1.00 and therefore inside the leggings shell's
    back wall at 2.40, and every row's `up` is under the row above it. Those are INNER.

  * EXPOSURE. Each row cube is 1.8 tall and unwraps to TWO texel rows of about 0.99 each. The row
    above laps roughly the upper one, so texel row 0 is the lapped half and texel row 1 the free
    half - which is the puttees' arrangement, and it is why LAP and FREE are a hundred and twenty
    apart. Measured hem to hem the exposures are 1.10, 0.95 and 1.20 leg-local units: three
    different numbers, per idiom point 1's last clause.

The face rectangles come from paint_circlet_master.faces(), over `net()`ed sizes the way the sash
and garters painters do it - every cube here has a fractional dimension. Row one (v .. v+d) holds up
then down, each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west, south with
widths d, w, d, w - the two thin d-wide faces FIRST and THIRD.

Orientation inside each rectangle is the table the greaves painter records as measured, not
recalled:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x              max z
    down            +y  (underside)      min x              max z
    west            +x  (outboard)       min z  (front)     min y (top)
    east            -x  (inboard)        max z  (back)      min y (top)
    north           -z  (front)          min x  (inboard)   min y (top)
    south           +z  (back)           max x  (outboard)  min y (top)

So `north` reads inboard to outboard left to right and `west` reads front to back: the two faces
meet at the corner between north's LAST column and west's FIRST, and `run()` below is what turns
that into one continuous eight-column scale field instead of two fields that happen to touch.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image

from fitting_mask import write_mask

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "scale_skirt.json"
OUT = ROOT / "tools" / "decoration_masters" / "scale_skirt.png"
GUARD = OUT.with_name("scale_skirt_guard.png")

TEX_W, TEX_H = 64, 32

# size (w, h, d) and uv (u, v), mirroring scale_skirt.json in that file's own walk order - the root
# bone `skirt` carries no cubes, so the order is its four children: the binding, then the three
# scale rows down the thigh.
CUBES = {
    "band": ((3.86, 1.15, 3.35), (48, 0)),
    "row1": ((3.5, 1.8, 3.3), (0, 0)),
    "row2": ((3.5, 1.8, 3.3), (16, 0)),
    "row3": ((3.5, 1.8, 3.3), (32, 0)),
}

# origin, and the pivot + rotation of the bone the cube hangs from. Every pivot is on the leg's own
# axis at x = 0, which is what turns the roll into a hem that steps up towards the hip.
PLACEMENT = {
    "band": ((-0.9, 0, -3), (0, -2.4, 0), (0, 0, -2)),
    "row1": ((-0.6, 0, -2.9), (0, -1.7, 0), (0, 0, -3)),
    "row2": ((-0.73, 0, -2.7), (0, -0.15, 0), (0, 0, -6)),
    "row3": ((-0.85, 0, -2.3), (0, 1.05, 0), (0, 0, -4)),
}

# The fitting takes the field: the three scale rows whole, every face of them, so no cube boundary
# can show a colour seam. The band keeps the trim material. Idiom point 3.
FIELD = ("row1", "row2", "row3")

random.seed(197)  # deterministic output - regenerating must not churn the PNG

# Calibrated against the ramp, not guessed: the material ramp interpolates dark -> mid over master
# values 0..127 and mid -> light over 128..255, so a master confined to one half only ever uses half
# of a material's ramp. Of this master's 384 texels only about seventy are ever reachable by a
# camera - the four `north` and four `west` faces, the hems and the band's ledge - and those run the
# whole ramp, because the lap read is made of nothing but the distance between LAP and FREE.
CORNER = 236    # the two columns either side of the front-to-flank corner, on a free row
EDGE = 232      # the free lower texel row of the bottom scale row: the hem, idiom point 2
RIM = 204       # the band's own face - the frame, and the only thing here that is not scale
FREE = 204      # the free lower half of a scale row, at the peak of the lateral profile
LAP = 138       # the lapped upper half of a scale row, in the shadow of the row above it
LEDGE = 150     # the band's `up` face, which the torso shell walks off twice a stride
HEM = 78        # the underside of a row where it overhangs the row beneath
BURIED = 54     # row3's `north`, which is 0.10 inside the leggings shell on purpose
INNER = 26      # buried - inside the thigh, behind a row, or inside the shell's back wall

# The Tidal scale row - idiom point 1. Two texels to a scale, staggered one texel per row, and the
# notch SMALLER than the 120 between LAP and FREE so that rows read before scales. head_fins learned
# that the hard way: at a notch of 46 against a row step of 16 its gill plate rendered as a
# chessboard.
SCALE_STEP = (0, -34)

# The lateral profile, applied as a MULTIPLIER rather than an offset so the dark rows keep their own
# shape instead of being flattened into INNER by a subtraction sized for the light ones - the
# shading of a leg is proportional, not additive. `north` runs inboard to outboard and `west` front
# to back, so the two peaks meet AT THE CORNER and the highlight is one vertical line down the part
# rather than two faces that happen to be bright. Idiom point 2.
NORTH_PROFILE = (0.66, 0.82, 0.94, 1.00)   # inboard .. the corner
WEST_PROFILE = (1.00, 0.91, 0.79, 0.67)    # the corner .. behind the flank

GRAIN = 3


def net(size):
    """A cube's box-UV net in whole pixels. Rounds up, the way Blockbench does - a row is 1.8 tall
    on purpose and unwraps to two rows, a lapped one and a free one."""
    return tuple(int(math.ceil(v - 1e-9)) for v in size)


def faces(size, uv):
    """Per-face pixel rectangles (x, y, w, h) for one box-UV cube. See the module docstring."""
    w, h, d = net(size)
    u, v = uv
    return {
        "up":    (u + d, v, w, d),
        "down":  (u + d + w, v, w, d),
        "east":  (u, v + d, d, h),
        "north": (u + d, v + d, w, h),
        "west":  (u + d + w, v + d, d, h),
        "south": (u + d + w + d, v + d, w, h),
    }


def rects(name):
    size, uv = CUBES[name]
    return faces(size, uv)


def scale(col: int, row: int) -> int:
    """The Tidal scale field, idiom point 1: a scale is two texels along the row, and consecutive
    rows are offset by one, so the boundaries stagger like brickwork instead of ruling a grid."""
    return SCALE_STEP[(col + row) % 2]


def run(face: str, col: int) -> int:
    """The column's index in the ONE scale field that wraps the thigh's corner. `north` is columns
    0..3, inboard to outboard; `west` continues at 4..7, corner to back. Without this the two faces
    carry two independent fields and the corner - the part's brightest line - falls between two
    scales that have no reason to line up."""
    return col if face == "north" else 4 + col


def put(img, x: int, y: int, lum: int, alpha: int = 255) -> None:
    if 0 <= x < TEX_W and 0 <= y < TEX_H:
        img.putpixel((x, y), (max(0, min(255, lum)), alpha))


def fill(img, rect, lum: int, jitter: int = GRAIN) -> None:
    x0, y0, w, h = rect
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            put(img, x, y, lum + random.randint(-jitter, jitter))


def ramp(i: int, n: int) -> float:
    """Position along a face axis, 0.0 at column/row 0 and 1.0 at the far end."""
    return 0.0 if n <= 1 else i / (n - 1)


def scale_face(img, rect, face: str, phase: int, free: int, lap: int, corner: bool = True,
               hemline: bool = False) -> None:
    """One face of a scale row: four columns of the wrapping field, two texel rows.

    Row 0 is the half the row above laps and row 1 is the free half, so the pair reads dark over
    light and the boundary between two rows is a shadow line rather than a rule. `phase` is the
    cube's index down the skirt and shifts the stagger by one texel per row of geometry, which is
    what carries the brickwork across a cube boundary and not merely within one."""
    x0, y0, fw, fh = rect
    profile = NORTH_PROFILE if face == "north" else WEST_PROFILE
    for j in range(fh):
        for i in range(fw):
            base = lap if j == 0 else (EDGE if hemline else free)
            lum = round((base + scale(run(face, i), j + phase)) * profile[i])
            if corner and j == fh - 1 and ((face == "north" and i == fw - 1)
                                           or (face == "west" and i == 0)):
                lum = CORNER          # the one line where the front of the thigh turns into a flank
            put(img, x0 + i, y0 + j, lum + random.randint(-GRAIN, GRAIN))


def paint_row(img, key: str, phase: int, free: int, lap: int, hem: int, buried: bool = False,
              hemline: bool = False) -> None:
    """One scale row: 3.5 x 1.8 x 3.3 on its own bone, rolled a few degrees about z.

    Only three of its six faces ever draw. `north` and `west` carry the wrapping scale field;
    `down` is the overhang, four by four texels of the shadow the row throws on the row beneath -
    and it is the ONLY place on this part where the lap is geometry rather than value, so it is
    painted as a real shadow that lightens towards the free front-outboard corner rather than as a
    flat dark fill.

    `buried` is row3, whose `north` face is 0.10 inside the leggings shell because below leg-local
    3.7 the front of the leg belongs to the knee. It is painted at BURIED rather than given a scale
    field it could never show - which is also why row3 is the row that carries `hemline`: with its
    front face gone, its `west` free row is the only hem this part has, and idiom point 2 wants that
    edge to be a lit LINE. The scale shins carry the same flag on the same row, at the ankle."""
    f = rects(key)

    if buried:
        fill(img, f["north"], BURIED)
    else:
        scale_face(img, f["north"], "north", phase, free, lap, hemline=hemline)
    scale_face(img, f["west"], "west", phase, free, lap, hemline=hemline)

    x0, y0, fw, fh = f["down"]           # 4 wide (x) x 4 deep, col 0 = inboard, row 0 = BACK
    for j in range(fh):
        for i in range(fw):
            # The overhang is deepest at the front-outboard corner, where the row above steps in by
            # 0.13 outboard and up to 0.40 forward; at the back and inboard the two rows are flush
            # and there is nothing to shadow.
            lit = ramp(i, fw) * 0.5 + ramp(j, fh) * 0.5
            put(img, x0 + i, y0 + j, hem + round(38 * lit) + random.randint(-GRAIN, GRAIN))

    fill(img, f["up"], INNER)            # under the row above, or under the band
    fill(img, f["east"], INNER)          # inside the thigh
    fill(img, f["south"], INNER)         # inside the leggings shell's back wall at z = 2.40


def paint_band(img) -> None:
    """The binding the skirt hangs from: 3.86 x 1.15 x 3.35, the proudest thing on the part at
    x = 3.00 and z = -3.00, and the only cube the `guard` fitting does not take.

    It exists for the fitting, exactly as the pelt's thong does. A second material covering the
    whole skirt would leave the smithed one nothing to be, and a binding painted as a band on row1's
    own face would have been recoloured along with the scales it was drawn over; a cube of its own
    is the only version of this that survives the mask. So it is smooth - no scale field, jitter and
    all - and pitched near the top of the range, because after the mask is applied its texels are
    the only ones still speaking for the material the part was smithed in.

    Its `up` face is the one surface here that is buried at rest and NOT buried in motion: the
    leggings TORSO shell reaches leg-local y 0.4 and covers x <= 2.5, and it rides BODY, so it walks
    out from over this band twice a cycle. Dimmed ledge, not filler."""
    f = rects("band")

    x0, y0, fw, fh = f["north"]          # 4 x 2, col 0 = inboard, row 0 = top
    for j in range(fh):
        for i in range(fw):
            lum = round((RIM - (26 if j == 0 else 0)) * NORTH_PROFILE[i])
            if j == fh - 1 and i == fw - 1:
                lum = CORNER
            put(img, x0 + i, y0 + j, lum + random.randint(-GRAIN, GRAIN))

    x0, y0, fw, fh = f["west"]           # 4 x 2, col 0 = front (the corner), row 0 = top
    for j in range(fh):
        for i in range(fw):
            lum = round((RIM - (26 if j == 0 else 0)) * WEST_PROFILE[i])
            if j == fh - 1 and i == 0:
                lum = CORNER
            put(img, x0 + i, y0 + j, lum + random.randint(-GRAIN, GRAIN))

    x0, y0, fw, fh = f["up"]             # 4 wide (x) x 4 deep, col 0 = inboard, row 0 = BACK
    for j in range(fh):
        for i in range(fw):
            # Free where it is outboard of the torso shell's x = 2.5 wall (the last column) or
            # forward of its z = -2.4 one (the last row).
            free = i == fw - 1 or j == fh - 1
            put(img, x0 + i, y0 + j,
                (LEDGE + round(24 * ramp(j, fh)) if free else INNER + 12)
                + random.randint(-GRAIN, GRAIN))

    x0, y0, fw, fh = f["down"]           # 4 wide x 4 deep; sits on row1 but for a 0.10 fringe
    for j in range(fh):
        for i in range(fw):
            fringe = i == fw - 1 or j == fh - 1
            put(img, x0 + i, y0 + j, (HEM + 14 if fringe else INNER) + random.randint(-GRAIN, GRAIN))

    fill(img, f["east"], INNER)          # inside the thigh
    fill(img, f["south"], INNER)         # inside the leggings shell's back wall


def check_geometry() -> None:
    """CUBES and PLACEMENT must be the cube list, the origins and the bone frames of the shipped
    geometry, in order. Painting a texture for a shape the model no longer has is invisible to every
    other check in this pipeline: both halves stay internally consistent while the rectangles slide
    off the faces they were drawn for. The origins are asserted because on this part they ARE the
    lap - three identical cubes differing only in where they sit - and the rotations because a lost
    roll would put four plates back in two planes without moving one texel."""
    doc = json.loads(GEO.read_text(encoding="utf-8"))
    found = []

    def walk(bone):
        pivot = tuple(bone.get("pivot", [0, 0, 0]))
        rot = tuple(bone.get("rotation", [0, 0, 0]))
        for c in bone.get("cubes", []):
            found.append(((tuple(c["size"]), tuple(c["uv"])), (tuple(c["origin"]), pivot, rot)))
        for child in bone.get("children", []):
            walk(child)

    for bone in doc["bones"]:
        walk(bone)

    assert (doc["texture_width"], doc["texture_height"]) == (TEX_W, TEX_H), \
        f"{GEO.name} is {doc['texture_width']}x{doc['texture_height']}, this master is {TEX_W}x{TEX_H}"
    assert [c for c, _ in found] == list(CUBES.values()), \
        f"CUBES disagrees with {GEO.name}: {[c for c, _ in found]} vs {list(CUBES.values())}"
    assert [p for _, p in found] == list(PLACEMENT.values()), \
        f"PLACEMENT disagrees with {GEO.name}: {[p for _, p in found]} vs {list(PLACEMENT.values())}"


def check_layout() -> dict:
    """Every face rectangle must sit inside the texture and no two may overlap - a silent overlap
    would paint one cube's shading onto another's face and only show up on a model in game."""
    claimed = {}
    for name in CUBES:
        for face, (x, y, w, h) in rects(name).items():
            assert 0 <= x and x + w <= TEX_W, f"{name}.{face} runs off the texture in u"
            assert 0 <= y and y + h <= TEX_H, f"{name}.{face} runs off the texture in v"
            for py in range(y, y + h):
                for px in range(x, x + w):
                    prev = claimed.get((px, py))
                    assert prev is None, f"{name}.{face} overlaps {prev} at {(px, py)}"
                    claimed[(px, py)] = f"{name}.{face}"
    return claimed


def main() -> None:
    check_geometry()
    claimed = check_layout()
    img = Image.new("LA", (TEX_W, TEX_H), (0, 0))
    paint_band(img)
    # The three rows step down the thigh and each one is a shade under the one above it, because a
    # skirt is lit from the hip; and each carries the next phase of the stagger, which is what
    # carries the brickwork over a cube boundary.
    paint_row(img, "row1", 0, FREE, LAP, HEM + 10)
    paint_row(img, "row2", 1, FREE - 16, LAP - 8, HEM + 4)
    paint_row(img, "row3", 2, FREE - 30, LAP - 14, HEM, buried=True, hemline=True)

    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque == set(claimed), "painted pixels do not match the UV rectangles"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)})")

    write_mask(img, [r for name in FIELD for r in rects(name).values()], GUARD)


if __name__ == "__main__":
    main()
