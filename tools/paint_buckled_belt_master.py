"""
Paint the grayscale master, the static leather layer and the guard mask for the "buckled_belt" part.

Kept as a script rather than a checked-in binary so the shape stays editable and reviewable. Like
the brooch, sash, tassets, spurs and greaves painters this one does not merely claim that CUBES
matches the shipped geometry, it reads
assets/armorpieces/armorpieces/decoration/buckled_belt.json at run time and asserts it
(check_geometry) - and unlike those five it asserts the ORIGINS too, because on this part every
sentence below is a clearance and a clearance is a position. Output goes to
tools/decoration_masters/buckled_belt.png, buckled_belt_static.png and buckled_belt_guard.png,
which sync_decoration_masters.py installs.

Master convention: luminance carries shading, alpha carries silhouette. This master is 100% opaque:
a strap has no fringe, and parts draw with armorCutoutNoCull, so a hole punched through a 0.9-thick
band would show the inside of the band rather than the leggings behind it. The punched holes on the
free end are therefore VALUE, not alpha - one dark pixel each.

WHAT THIS PART IS

The `belt` socket had one part on it, the Sash, and the Sash is a diagonal statement: a band, a
gathered knot at the left hip and a strap hanging to knee height on two rotated bones. This is the
opposite and is meant to be. It is horizontal, it is even, it is symmetric about x = 0 except for
four painted pixels, and it is over in three units of height. Nothing on it rotates, nothing hangs,
nothing reaches past the waist. If it reads as "a belt" and no more, it is finished.

The one idea it does carry that the Sash does not is the SPLIT: the strap is leather and keeps its
own colour through a static layer, the buckle is metal and takes a second trim material through the
`armorpieces:guard` fitting. So one part shows two materials at once with no fitting filled at all -
leather against the base metal - and three when the guard is filled. The Sash divides the same way
round the other way: its strap is a dye `inlay` and its buckle is the `guard`, so a Sash with both
fittings filled shows none of its base material. This one always shows leather and always shows the
base material somewhere, which is a different bargain rather than the same one restated.

THE CUBES, IN PART-LOCAL UNITS AND IN THE BODY'S

`belt` is a SINGLE, non-mirrored attachment - Attachment.of(BODY, 0, 10, 0) - so the layer's
scale(-1, 1, 1) never runs, one master serves one draw, and `west` and `east` are genuinely
different faces rather than the same face twice. Part-local (0, 0, 0) is body-local (0, 10, 0), so
body y = part y + 10. +Y is DOWN.

    cube      part-local origin  size          body-frame extents
    front     (-5.5, -1, -3.5)   (11, 2, 0.9)  x -5.5..5.5  y  9..11    z -3.5..-2.6
    back      (-5.5, -1,  2.6)   (11, 2, 0.9)  x -5.5..5.5  y  9..11    z  2.6.. 3.5
    side_l    ( 4.6, -1, -2.6)   (0.9, 2, 5.2) x  4.6..5.5  y  9..11    z -2.6.. 2.6
    side_r    (-5.5, -1, -2.6)   (0.9, 2, 5.2) x -5.5..-4.6 y  9..11    z -2.6.. 2.6
    buckle    (-1.5, -1.5, -4.5) (3, 3, 1)     x -1.5..1.5  y  8.5..11.5 z -4.5..-3.5

Four bars butted into a closed rectangular ring, and one plate on the front of it. The ring's outer
wall is x = +/-5.5 and z = +/-3.5 all the way round, which is exactly 1.5 units outside the naked
body box (x +/-4, z +/-2) on every side: a strap of constant standoff, which is what makes it read
as even. Its inner wall is 0.9 in from that.

WHAT CLEARS WHAT, AND WHY 0.9 IS NOT 1.0

Three surfaces cover `body` at the waist, and this part is authored against all three:

  * naked body box      x +/-4.0   z +/-2.0
  * leggings shell 0.5  x +/-4.5   z +/-2.5   <- the piece this socket belongs to
  * chestplate shell 1.0 x +/-5.0  z +/-3.0   <- the outermost, and OPTIONAL

The brief this part was authored to says nothing of it may be buried inside the leggings shell, and
it is not: the ring's inner wall at x +/-4.6 / z +/-2.6 clears the leggings by exactly a tenth of a
unit on all four sides. That tenth is the whole reason the strap is 0.9 thick rather than 1.0.
Landing the inner wall ON the shell at 4.5 would have bought a whole number and cost a z-fight: the
strap's inner face and the leggings' outer face would be coincident and opposed, the decoration
layer draws AFTER the armor layer, and at equal depth the later draw wins - so a strap threaded onto
a player wearing no chestplate would flicker its own dark INNER texels onto the leggings. A tenth of
a unit of air is cheaper than that, and it is the same tenth the greaves spend clearing the boots
shell. The outer wall then falls on 5.5 and 3.5, which are whole, and the hero face is 11 whole
texels rather than 11.2 over 12 - the fractional dimension is spent where nothing looks at it.

Against the chestplate the ring straddles rather than clears: x 4.6..5.5 puts 0.4 of the strap inside
a chestplate's shell and 0.5 outside it. That is deliberate and is the right way round for a LEGGINGS
decoration - the shell that may not be worn is the one allowed to swallow part of the shape, and the
shell that is always worn with it is the one cleared outright. Every face inside the chestplate is
painted as strap rather than as INNER for the same reason: with no chestplate on, all of it shows.

The one dimension that is fractional and is looked at is the side bars' 5.2 of depth, which is not a
choice - it is what is left between the two bars once their inner walls are at z = +/-2.6. It nets
to six texels covering 5.2 units, so the sixth column of the outboard flank is sampled over only its
first fifth. The flank is painted as a monotone front-to-back falloff precisely so that costs
nothing: no feature of the composition sits in that column to be clipped.

VERTICALLY: 2 UNITS, AND WHAT IS ABOVE AND BELOW IT

The band is body y 9..11, two units centred on the anchor at y = 10, which is thinner than the Sash's
three and is most of why the two do not read alike. Below it:

  * the leggings shell's bottom cap is at y 12.5 and the chestplate's at 13 - both a clear unit and a
    half below the band, so the belt never fights the hem of the piece it hangs on;
  * the shipped `tassets` part's topmost face is at body y 11.75 (its first lame's origin is
    y = -2.25 on an anchor at leg y = 2, and the leg pivot is entity y = 12). The band's underside at
    y = 11 clears it by 0.75. That is the tightest number under this part and it is not tight;
  * as a curiosity rather than a hazard, the tassets' outboard wall lands on entity x = 4.6, the same
    plane as this strap's inboard wall. The two never share a y, so the coincidence is arithmetic
    only - but a later part on `belt` that comes down past y 11.75 should know the plane is taken.

Above it, the shipped `wing_roots` part on the `back` socket hangs a 3 x 3 x 3 box down to body
y 9.5 over z 2..5, and this part's back bar runs through the bottom half unit of it: trace_geometry
reports OVERLAP 3.00 x 0.50 x 0.90. It is not avoidable and it is not new - the Sash overlaps the
same box by 3.00 x 1.50 x 2.00, three times as much - and a belt passing over the hem of a
back-plate is what a belt does. Moving the band down to 9.5 would trade the overlap for a
part-to-part COPLANAR, which trace_geometry rates as the worse of the two, and it would eat the
tassets clearance as well.

THE BUCKLE, AND THE ONE COINCIDENT PAIR ON THE PART

3 x 3 x 1, at front centre, sitting flush on the band's front face at z = -3.5 and standing one unit
proud of it. Square because the brief asked for a square buckle, three because the band is two: a
frame half a unit proud of the strap above and below is what a buckle frame does, and four would be
the buckle wearing the belt.

Its `south` face at z = -3.5 is coincident with the band's `north` face at the same plane, opposed.
That is the only coincident pair on the part and it is unconditionally invisible: the buckle's own
`north` face at z = -4.5 is a whole unit in front of both and covers the pair exactly, so no camera
reaches them from the front, the band covers them from behind, and they are edge-on from everywhere
else. The alternative - burying the buckle a fraction into the band, which is what the Sash does -
buys nothing here and costs a fractional depth whose net rows no longer line up with the
proud/buried boundary. Both faces are painted at INNER anyway, which is what a buried face gets in
this repo.

At three by three the frame is a lit ring around a single dark pixel and there is no tongue, because
there is nowhere to put one: four columns is the minimum for frame-aperture-tongue-frame and the
Sash already spent them. A detail at this size is a value against its neighbour (the brooch's rivet
paid for that lesson), and one bright ring against one dark centre is a buckle. Anything more would
be the part being interesting, which is the one thing it is not for.

THE THREE SHEETS

  * the MASTER shades everything. Its strap values are deliberately kept in 60..205 rather than run
    out to 250: strap pixels are read through the LEATHER static ramp, whose mid stop is at master
    127, so a face painted at 240 would be most of the way to white and the leather would read as
    tan canvas. The buckle's values run 26..250, because those go through a trim material's own ramp
    and a metal wants the whole of it.
  * the STATIC layer is opaque LEATHER over every pixel of the four bars and transparent over the
    buckle. A transparent static pixel is exactly what lets the material ramp through, so the buckle
    takes the base trim material while the strap ignores it.
  * the GUARD mask is the buckle's six face rectangles, copied out of the master by
    fitting_mask.write_mask - same shading, second material. With the fitting empty the mask is
    ignored and the buckle shows the base material; filled, it shows the metal that was set into it.
    The strap is in neither the mask nor the material, and is the same leather in all three cases.

FACE LAYOUT AND ORIENTATION

The face rectangles come from paint_circlet_master.faces(): row one (v .. v+d) holds up then down,
each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west, south with widths
d, w, d, w. The two thin d-wide faces come FIRST and THIRD.

Orientation inside each rectangle is the table PLAN.md records as measured, not recalled, written in
MIN X and MAX Z rather than "inboard" and "back" because this part has cubes on both sides of x = 0:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x              max z
    down            +y  (underside)      min x              max z
    west            +x                   min z              min y (top)
    east            -x                   max z              min y (top)
    north           -z  (front)          min x              min y (top)
    south           +z  (back)           max x              min y (top)

The consequence that shapes this painter is the HIP RUN. Looking at the left hip from +x you see
three faces in a row, and they belong to three different cubes: the front bar's `west` end cap
(z -3.5..-2.6, one texel), side_l's `west` flank (z -2.6..2.6, six texels) and the back bar's `west`
end cap (z 2.6..3.5, one texel). They are coplanar at x = 5.5 and adjacent, not overlapping - a
mitre, not a seam - so the eight texels have to shade as ONE run or the corners appear as steps.
hip() is that run, indexed 0..7 from front to back, and every one of the eight patches asks it for
its value rather than carrying its own constant. On the right hip the same eight are `east` faces
and their columns count from max z, so the index is reversed and nothing else changes.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image

from fitting_mask import write_mask

ROOT = Path(__file__).resolve().parent.parent
GEO = (ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces"
       / "decoration" / "buckled_belt.json")
OUT = ROOT / "tools" / "decoration_masters" / "buckled_belt.png"
OUT_STATIC = ROOT / "tools" / "decoration_masters" / "buckled_belt_static.png"
OUT_GUARD = ROOT / "tools" / "decoration_masters" / "buckled_belt_guard.png"

TEX_W, TEX_H = 64, 32

# origin, size (w, h, d) and uv (u, v), mirroring buckled_belt.json in that file's own order. The
# origins are here and asserted because the module docstring's clearances are statements about them:
# 0.9 is a tenth off the leggings shell, 4.6 is that tenth, and 2 units of height is 0.75 off the
# tassets. A size table alone would let all three drift silently.
CUBES = {
    "front":  ((-5.5, -1, -3.5),   (11, 2, 0.9),  (0, 0)),
    "back":   ((-5.5, -1, 2.6),    (11, 2, 0.9),  (0, 4)),
    "side_l": ((4.6, -1, -2.6),    (0.9, 2, 5.2), (0, 8)),
    "side_r": ((-5.5, -1, -2.6),   (0.9, 2, 5.2), (16, 8)),
    "buckle": ((-1.5, -1.5, -4.5), (3, 3, 1),     (32, 8)),
}

STRAP_CUBES = ("front", "back", "side_l", "side_r")

random.seed(17)  # deterministic output - regenerating must not churn the PNG

# ---- the strap ---------------------------------------------------------------------------------
# Read through LEATHER's static ramp, whose mid stop is master 127 and whose light stop is only
# halfway to white. These stay in the middle of the range on purpose; see the docstring.
STRAP = 156     # a strap face in the light: `north` at the front, `south` at the back
TOP = 202       # the band's top face, the one surface a standing figure lights fully
UNDER = 60      # the band's underside
FLANK = 146     # the hip run at its front end, where it turns away from the light
INNER = 72      # buried: an inboard wall, a butt joint, the back of the buckle

RIM = 22        # the chamfer along the band's top edge
FALL = 26       # top-to-bottom falloff down a standing face - two rows, so this is the whole drop
ROUND = 18      # lateral falloff towards the ends of a bar, which rounds a flat slab
DEPTH = 34      # the front-to-back falloff along the eight texels of a hip run
LAP = 14        # the free end of the strap, lying over the band it came round
HOLE = 76       # a punched hole - one pixel is the whole hole, so it goes deep
KEEP = 26       # the keeper loop the free end is threaded under

# ---- the buckle --------------------------------------------------------------------------------
# Read through a trim material's own ramp, so these run the full width of it.
FRAME = 226     # the buckle's frame
FRAME_LIT = 250 # the top bar of the frame, catching the light square on
FRAME_DIM = 162 # the bottom bar, in the frame's own shadow
APERTURE = 26   # the opening the strap threads through
BUCKLE_UP = 244
BUCKLE_DOWN = 44

# The colour master value 127 maps to, through DecorationPalette.ofStaticColour: dark is half of it,
# light is halfway from it to white. This is vanilla's own undyed-leather-armour tint, which is the
# colour a player already reads as "leather" without being told.
LEATHER = (0xA0, 0x65, 0x40)


def net(size):
    """A cube's box-UV net in whole pixels. Rounds UP - the ring's 0.9 walls net to one texel and
    the side bars' 5.2 of depth to six. See the module docstring on what the sixth costs."""
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


def face_rects(name):
    _, size, uv = CUBES[name]
    return faces(size, uv)


def put(img, x: int, y: int, lum: int, alpha: int = 255) -> None:
    if 0 <= x < TEX_W and 0 <= y < TEX_H:
        img.putpixel((x, y), (max(0, min(255, lum)), alpha))


def fill(img, rect, lum: int, jitter: int = 3) -> None:
    x0, y0, w, h = rect
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            put(img, x, y, lum + random.randint(-jitter, jitter))


def ramp(i: int, n: int) -> float:
    """Position along a face axis, 0.0 at column/row 0 and 1.0 at the far end."""
    return 0.0 if n <= 1 else i / (n - 1)


def bar_lateral(i: int, w: int) -> int:
    """How much a column of an eleven-wide bar loses to being off centre.

    A flat slab reads as a flat slab. The band is a strap wrapped round a torso, so its front and
    back faces are brightest where they face the camera squarely and fall away towards the hips -
    which is also the value the hip run picks up at the mitre, so the whole ring shades as one loop
    rather than as four boxes."""
    return round(ROUND * abs(i - (w - 1) / 2) / ((w - 1) / 2))


# ---- the hip run -------------------------------------------------------------------------------
# Eight texels from the front of the hip to the back, spread over three cubes: the front bar's end
# cap (0), side_l's or side_r's flank (1..6), the back bar's end cap (7). One function so the two
# mitres do not step.
HIP_TEXELS = 8


def hip(t: int, j: int, rows: int) -> int:
    """The value of one texel of a hip run: t counts front to back, j is the row from the top."""
    lum = FLANK - round(DEPTH * t / (HIP_TEXELS - 1)) - round(FALL * ramp(j, rows))
    return lum + (RIM if j == 0 else 0)


def paint_front(img) -> None:
    """The front of the band. Eleven texels of `north`, which is the face a player meets head on and
    the only place on this part where anything is written.

    Reading the eleven columns from min x (the wearer's RIGHT, screen left in third person):

        0 1 2   the free end of the strap, lying over the band it has come round. Dropped LAP below
                the band so the lap has an edge without a modelled step, and holes punched at 0 and
                2 on the lower row. A hole is one pixel, so it goes HOLE deep and the run around it
                drops its top chamfer entirely: at this size a hole only reads if what surrounds it
                is plainly duller than the rest of the band, which is the brooch's rivet lesson.
        3       the keeper loop, the one thing the free end is threaded under. It is the only column
                that stands proud, and KEEP is small on purpose.
        4 5 6   under the buckle, which spans x -1.5..1.5. Painted as plain band anyway: it costs
                nothing, and if the BELT anchor is ever nudged it is a strap that appears rather
                than a black stripe.
        7..10   band, and nothing on it.

    So the story runs one way - buckle at centre, keeper beside it, then the punched tail running off
    to the wearer's right - and the Sash puts its holes on the same side, which is the closest thing
    this socket has to a convention.

    `up` and `down` are one texel deep, the whole 0.9 of the band, and both are entirely free: the
    buckle stands in FRONT of this cube at z -4.5..-3.5, not on top of it, so nothing here is
    covered. `south` at z = -2.6 faces the tenth of a unit of air between the band and the leggings
    shell and is the one wholly buried face on the cube."""
    _, size, uv = CUBES["front"]
    w, h, d = net(size)
    f = faces(size, uv)
    tail, holes, keeper, under_buckle = (0, 1, 2), (0, 2), (3,), (4, 5, 6)
    assert under_buckle == (4, 5, 6), "the buckle spans x -1.5..1.5, which is columns 4, 5 and 6"

    x0, y0, fw, fh = f["north"]          # 11 x 2, col 0 = min x, row 0 = top
    for j in range(fh):
        for i in range(fw):
            lum = STRAP - round(FALL * ramp(j, fh)) - bar_lateral(i, fw)
            if i in tail:
                lum -= LAP
                if i in holes and j == fh - 1:
                    lum -= HOLE
            else:
                if j == 0:
                    lum += RIM
                if i in keeper:
                    lum += KEEP
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["up"]             # 11 wide x 1 deep, wholly exposed
    for i in range(fw):
        put(img, x0 + i, y0, TOP - bar_lateral(i, fw) + random.randint(-3, 3))

    x0, y0, fw, fh = f["down"]           # same layout, the underside
    for i in range(fw):
        put(img, x0 + i, y0, UNDER - bar_lateral(i, fw) // 2 + random.randint(-3, 3))

    # The two end caps are texel 0 of their hip run - the front of each mitre, and the brightest of
    # the eight. One texel wide because the band is 0.9 thick.
    for name in ("east", "west"):
        x0, y0, fw, fh = f[name]
        for j in range(fh):
            put(img, x0, y0 + j, hip(0, j, fh) + random.randint(-3, 3))

    fill(img, f["south"], INNER)         # faces the tenth of air in front of the leggings shell


def paint_back(img) -> None:
    """The back of the band, and the reason it is painted at all: in third person the back of a
    player is the face that is actually looked at.

    It carries nothing. No keeper, no holes, no seam - the free end and the hardware are at the
    front, and a belt seen from behind is a strap. What keeps eleven by two from reading as a slab is
    four gradients and nothing else: the chamfer on the top row, the fall to the bottom row, the
    lateral round towards the hips, and the grain jitter every value here gets. That is the whole
    composition and it is meant to be.

    It is the mirror of the front bar in depth as well as in content - its proud unit is at max z
    rather than min z - but because the band is only 0.9 thick and nets to a single depth texel,
    none of the row-order care the Sash's two bars needed applies: there is one depth row on `up` and
    on `down` and one depth column on each cap, so there is no end to get the wrong way round.
    `north` at z = 2.6 is the buried face here, where the front bar's `south` was."""
    _, size, uv = CUBES["back"]
    w, h, d = net(size)
    f = faces(size, uv)

    x0, y0, fw, fh = f["south"]          # 11 x 2, col 0 = MAX x, row 0 = top
    for j in range(fh):
        for i in range(fw):
            lum = STRAP - round(FALL * ramp(j, fh)) - bar_lateral(i, fw)
            if j == 0:
                lum += RIM
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["up"]
    for i in range(fw):
        put(img, x0 + i, y0, TOP - 10 - bar_lateral(i, fw) + random.randint(-3, 3))

    x0, y0, fw, fh = f["down"]
    for i in range(fw):
        put(img, x0 + i, y0, UNDER - bar_lateral(i, fw) // 2 + random.randint(-3, 3))

    # Texel 7 of each hip run - the back end of the mitre, and the darkest of the eight.
    for name in ("east", "west"):
        x0, y0, fw, fh = f[name]
        for j in range(fh):
            put(img, x0, y0 + j, hip(HIP_TEXELS - 1, j, fh) + random.randint(-3, 3))

    fill(img, f["north"], INNER)         # faces the air behind the leggings shell


def paint_side(img, name, outboard, first_texel_is_front) -> None:
    """One of the ring's two side bars, 0.9 x 2 x 5.2, spanning front bar to back bar at the hip.

    Six of the eight texels of a hip run live here, and they ask hip() for their values so the two
    mitres with the end caps are continuous. `first_texel_is_front` is the only thing that differs
    between the two bars: side_l's outboard face is `west`, whose columns count from min z, so texel
    1 is column 0; side_r's is `east`, whose columns count from max z, so texel 1 is column 5.

    These are the part's least-seen cubes and they are painted properly anyway, for the Sash's
    reason: the chestplate's 1.0 arm sleeve occupies body x 3..9 down to y 13, which is every unit of
    room outboard of the torso at belt height, so at rest an arm hangs in front of each of them. The
    arms swing through most of a walk cycle and are raised often, and a face that is only right at
    rest is wrong for most of the time it is looked at.

    The inboard flank faces the tenth of a unit of air over the leggings shell and is INNER. Both end
    caps are INNER too, and these are the butt joints of the ring: side_l's `north` at z = -2.6 is
    exactly covered by the front bar, which spans the full width there, and its `south` by the back
    bar. Two coincident opposed faces at each of the four corners, and all eight are behind a solid
    unit of the bar in front of them from every direction that could see them.

    `up` and `down` are one texel wide by six deep and wholly free - nothing on this part or on the
    body is above or below the hip at this standoff. Their rows run BACK to FRONT, which is the
    reverse of the flank's columns, so the texel index is 6 - j and not j + 1."""
    _, size, uv = CUBES[name]
    w, h, d = net(size)
    f = faces(size, uv)
    inboard = "east" if outboard == "west" else "west"

    x0, y0, fw, fh = f[outboard]         # 6 wide (depth) x 2 tall
    for j in range(fh):
        for i in range(fw):
            t = (i + 1) if first_texel_is_front else (HIP_TEXELS - 2 - i)
            put(img, x0 + i, y0 + j, hip(t, j, fh) + random.randint(-3, 3))

    fill(img, f[inboard], INNER)         # over the leggings shell, a tenth of a unit off it

    for face, base, swing in (("up", TOP, -18), ("down", UNDER, 10)):
        x0, y0, fw, fh = f[face]         # 1 wide (x) x 6 deep, rows run back to front
        for j in range(fh):
            t = HIP_TEXELS - 2 - j       # row 0 is max z, which is texel 6
            put(img, x0, y0 + j,
                base + round(swing * t / (HIP_TEXELS - 1)) + random.randint(-3, 3))

    fill(img, f["north"], INNER)         # butted into the front bar
    fill(img, f["south"], INNER)         # butted into the back bar


def paint_buckle(img) -> None:
    """The plate at front centre: a lit frame around one dark pixel, and nothing else.

    Its `north` is 3 x 3 and that is the whole budget. Three columns is one short of
    frame-aperture-tongue-frame, so there is no tongue; what there is is a ring whose top bar is the
    brightest thing on the part and whose centre is the darkest, 250 against 26, and at three by
    three that contrast IS the buckle. The bottom bar is dropped to FRAME_DIM so the frame reads as
    lit from above rather than as an outline.

    Every face but `south` is free. The plate stands a full unit proud of the band in z and half a
    unit proud of it in y, so `up`, `down` and both flanks are outside everything - which is what
    earns a 3-tall plate on a 2-tall band: the half unit top and bottom is where the frame gets to
    be a frame rather than a patch of paint on the strap.

    `south` is the coincident face described in the module docstring. It is INNER, and it is behind a
    solid unit of its own plate from the only direction that could see it."""
    _, size, uv = CUBES["buckle"]
    w, h, d = net(size)
    f = faces(size, uv)

    x0, y0, fw, fh = f["north"]          # 3 x 3, col 0 = min x, row 0 = top
    rows = (
        (FRAME, FRAME_LIT, FRAME),                    # the top bar of the frame
        (FRAME - 26, APERTURE, FRAME - 26),           # the two side bars and the opening
        (FRAME_DIM, FRAME_DIM - 22, FRAME_DIM),       # the bottom bar, in the frame's shadow
    )
    for j, row in enumerate(rows):
        for i, lum in enumerate(row):
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["up"]             # 3 wide x 1 deep - the whole unit of proud plate
    for i in range(fw):
        put(img, x0 + i, y0, BUCKLE_UP - (0 if i == 1 else 14) + random.randint(-3, 3))

    x0, y0, fw, fh = f["down"]
    for i in range(fw):
        put(img, x0 + i, y0, BUCKLE_DOWN + (8 if i == 1 else 0) + random.randint(-3, 3))

    for name in ("east", "west"):        # 1 wide (depth) x 3 tall, both wholly outside the band
        x0, y0, fw, fh = f[name]
        for j in range(fh):
            put(img, x0, y0 + j,
                FRAME - 40 - round(FALL * ramp(j, fh)) + (RIM if j == 0 else 0)
                + random.randint(-3, 3))

    fill(img, f["south"], INNER)         # coincident with the band's `north`, and behind the plate


def check_geometry() -> None:
    """CUBES must be the cube list of the shipped geometry, in order, ORIGINS INCLUDED.

    Painting a texture for a shape the model no longer has is invisible to every other check in this
    pipeline: both halves stay internally consistent while the rectangles slide off the faces they
    were drawn for. The origins are asserted as well as the sizes because on this part they are the
    argument - 0.9 and 4.6 are one statement about the leggings shell, 2 units of height are another
    about the tassets, and a size table alone would let a moved cube keep both sentences true on
    paper and false on the model."""
    doc = json.loads(GEO.read_text(encoding="utf-8"))
    found = []

    def walk(bone):
        for c in bone.get("cubes", []):
            found.append((tuple(c["origin"]), tuple(c["size"]), tuple(c["uv"])))
        for child in bone.get("children", []):
            walk(child)

    for bone in doc["bones"]:
        walk(bone)

    assert (doc["texture_width"], doc["texture_height"]) == (TEX_W, TEX_H), \
        f"{GEO.name} is {doc['texture_width']}x{doc['texture_height']}, this master is {TEX_W}x{TEX_H}"
    assert found == list(CUBES.values()), \
        f"CUBES disagrees with {GEO.name}: {found} vs {list(CUBES.values())}"

    # The three clearances the docstring is made of, read back off the geometry rather than trusted.
    (bx, by, bz), (bw, bh, bd), _ = CUBES["front"]
    assert bz + bd == -2.6 and CUBES["side_l"][0][0] == 4.6, \
        "the ring's inner wall must clear the leggings shell (x 4.5, z 2.5) by a tenth of a unit"
    assert by + 10 == 9 and by + bh + 10 == 11, \
        "the band must be body y 9..11: 0.75 clear of the tassets and 1.5 clear of the leggings hem"
    assert CUBES["buckle"][0][2] + CUBES["buckle"][1][2] == bz, \
        "the buckle must sit flush on the band's front face at z = -3.5"


def check_layout():
    """Every face rectangle must sit inside the texture and no two may overlap - a silent overlap
    would paint one cube's shading onto another's face and only show up on a model in game."""
    claimed = {}
    for name in CUBES:
        for face, (x, y, w, h) in face_rects(name).items():
            assert 0 <= x and x + w <= TEX_W, f"{name}.{face} runs off the texture in u"
            assert 0 <= y and y + h <= TEX_H, f"{name}.{face} runs off the texture in v"
            for py in range(y, y + h):
                for px in range(x, x + w):
                    prev = claimed.get((px, py))
                    assert prev is None, f"{name}.{face} overlaps {prev} at {(px, py)}"
                    claimed[(px, py)] = f"{name}.{face}"
    return claimed


def write_static(master: Image.Image) -> int:
    """The static layer: opaque LEATHER over every strap pixel, transparent over the buckle.

    A transparent static pixel takes the trim material's ramp; an opaque one takes its own colour
    through the static ramp with the master's value as the shading. So this one file is the whole of
    the leather/metal split, and it is derived from the master's own alpha rather than painted, which
    is what makes it impossible for the two to disagree about the silhouette."""
    static = Image.new("RGBA", (TEX_W, TEX_H), (0, 0, 0, 0))
    source = master.convert("LA")
    count = 0
    for name in STRAP_CUBES:
        for x0, y0, w, h in face_rects(name).values():
            for y in range(y0, y0 + h):
                for x in range(x0, x0 + w):
                    if source.getpixel((x, y))[1]:
                        static.putpixel((x, y), (*LEATHER, 255))
                        count += 1
    OUT_STATIC.parent.mkdir(parents=True, exist_ok=True)
    static.save(OUT_STATIC)
    print(f"wrote {OUT_STATIC} ({count} opaque px, {'#%02x%02x%02x' % LEATHER})")
    return count


def main() -> None:
    check_geometry()
    claimed = check_layout()
    img = Image.new("LA", (TEX_W, TEX_H), (0, 0))
    paint_front(img)
    paint_back(img)
    # The two side bars differ only in which sign of x is outboard, and that decides two things:
    # which flank face is the free one, and which end of it is the front of the hip run.
    paint_side(img, "side_l", "west", True)
    paint_side(img, "side_r", "east", False)
    paint_buckle(img)

    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque == set(claimed), "painted pixels do not match the UV rectangles"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)})")

    strap = {p for name in STRAP_CUBES for x0, y0, w, h in face_rects(name).values()
             for p in ((x, y) for y in range(y0, y0 + h) for x in range(x0, x0 + w))}
    strap_lums = [img.getpixel(p)[0] for p in sorted(strap)]
    assert max(strap_lums) <= 210, \
        f"a strap value of {max(strap_lums)} runs the leather ramp towards white; keep it under 210"

    write_static(img)

    # One fitting. The buckle alone is the guard and takes a metal; the strap is leather in every
    # material and is in neither the mask nor the base ramp.
    write_mask(img, face_rects("buckle").values(), OUT_GUARD)


if __name__ == "__main__":
    main()
