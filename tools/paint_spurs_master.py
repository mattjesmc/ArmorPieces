"""
Paint the grayscale master for the "spurs" part.

Like paint_brooch_master.py, paint_sash_master.py and paint_tassets_master.py this does not merely
claim that CUBES matches the shipped geometry, it reads
assets/armorpieces/armorpieces/decoration/spurs.json at run time and asserts it (check_geometry).
Output goes to tools/decoration_masters/spurs.png, which sync_decoration_masters.py installs for
the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

**This is the first master since the feathering to spend alpha, and the first ever to spend it on a
shape rather than a fringe.** The circlet's finding still holds for the strap and for everything
bolted to it - a metal strap has no fray, parts draw with armorCutoutNoCull, and a hole punched in a
two-pixel band would show the inside of the band - so four of the five cubes are 100% opaque and
entirely value. The rowel is the exception the rule was waiting for: a star wheel cannot be modelled
at one-unit resolution and it can be *cut*, and behind a rowel there is nothing but air, so a punched
hole shows exactly what a real rowel's gullets show. ROWEL_STAR below is the whole silhouette; the
geometry is a plain 1 x 3 x 3 slab and would read as a tab welded to the fork without it.

**A three-by-three wheel has one ring of cells, so the cut chooses itself.** At 5 x 5 there were two
rings and the question was which of them to bite; here the ring is the eight cells around a single
centre, and the only bite that survives a 90-degree rotation is the four corners. That is not a
consolation prize - the four-point molette is the commonest rowel there is - and it costs four cells
of nine, which at this size is the same share of the box the eight-tooth star cost at the last one.
The alternative was leaving the slab square, and a square is what the alpha exists to prevent.

**What the cut no longer has to buy is clearance, and that is the model's doing rather than the
master's.** Swept over +-85 degrees of leg swing the deepest point of each cube is band **22.12**,
neck **22.48**, tang **23.62**, rowel **24.08**, fork **24.80** - every one of them above vanilla's
own 1.0 boots shell at **25.34**, and all but the fork above the naked leg's **24.17**. The wheel
used to be this part's floor problem and the corner bites were half of the fix; now the wheel is the
second shallowest thing on the part and the cut is a drawing argument and nothing else.

**The one bite that is load-bearing structurally is the front-bottom corner.** The rowel's underside
and the tang's top face lie in the same bone-local plane, y = -0.25, over a one-by-one patch at
z 3.5..4.5 - the only pair of coincident faces anywhere in the part, and normally the thing to go and
fix in the model. That patch is the star's cut front-bottom corner, so the rowel never draws there
and the two faces never fight. It is worth stating plainly because it is fragile: fill that corner in
and the part acquires a z-fighting patch that no assertion in this file would catch.

What this part is, and what that costs the painter:

  * `spurs` is a MIRRORED pair - Attachment.of(LEFT_LEG, 0, 10, 2) plus Attachment.mirrored on the
    right - so the layer's scale(-1, 1, 1) runs on the right-hand copy and ONE master serves both.
    That survives the flip only because the face-name mapping does: `west` is geo +x, outboard on
    both legs, and `east` is geo -x, inboard on both.

  * The hero face is `west`. A rowel spins on a lateral axle, so its disc lies in the y-z plane and
    the star is only ever seen from the SIDE - which is also the angle from which one player looks at
    another. From directly behind, the wheel is a 1 x 3 line. That inverts the sash's and the
    tassets' priorities, where `north`/`south` carried the part: here `north` and `south` on the
    rowel are one pixel each, the tips of the front and back teeth, and hold nothing else at all.

  * The second face worth painting properly is the fork's `south`, a 2 x 3 back wall standing in
    clear air at geo z = 9.08 with the wheel poking a unit past it. The old three-cube part had
    nothing at the back but a rim; this one has a block, and a block seen from behind is a face.

  * It rides the LEG bone, so burial in the boot shell is free and permanent. Every INNER pixel here
    is one of exactly four things: inside the 1.0 boots shell, inside the heel band, inside the tang,
    or inside the fork. None of them uncover - unlike the tassets, which had to paint one row as
    flank because the torso shell rides a different bone.

**Nothing on this part buries by whole pixels any more, so burial is decided by area.** The tang's y
planes are bone-local -0.25 and 0.75, the fork's are -1.5 and 1.5, the rowel's are -3.25 and -0.25,
the neck's are -1 and 1: four cubes on four different half-unit grids, which is what a sub-assembly
built to look right rather than to land on the integer lattice looks like from the texture side. A
face pixel is therefore called INNER when *most* of its area is inside another solid. The coverage
fractions that actually occur are 1.00, 0.90, 0.75, 0.50, 0.25 and 0, so the rule only ever has to
break the 0.50 ties, and it breaks them toward *shown*: a pixel that is half proud is half seen, and
a seen half must not be black.

The face rectangles come from paint_circlet_master.faces(), copied verbatim: row one (v .. v+d)
holds up then down, each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west,
south with widths d, w, d, w.

Orientation inside each rectangle is the table PLAN.md records as measured, not recalled:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x              max z
    down            +y  (underside)      min x              max z
    west            +x  (outboard)       min z  (front)     min y (top)
    east            -x  (inboard)        max z  (back)      min y (top)
    north           -z  (front)          min x  (inboard)   min y (top)
    south           +z  (back)           max x  (outboard)  min y (top)

The rowel leans on that table harder than any part so far, because a punched silhouette has to agree
with itself across six faces: the four one-pixel rims are the four edges of the same star, and each
one reads the star along a different axis and in a different direction. Get one of them backwards and
the tooth tips stop lining up with the teeth they belong to, which is a bug no layout check can see.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "spurs.json"
OUT = ROOT / "tools" / "decoration_masters" / "spurs.png"

TEX_W, TEX_H = 64, 32

# size (w, h, d) and uv (u, v), mirroring spurs.json in that file's own order. Geo extents at rest
# (left-hand copy; the right one is the mirror image), from the swept-envelope script:
#   band  - the heel strap, on the unrotated heel bone; geo x 1.75..5.75, y 19.50..21.50,
#           z 1.50..3.50. It straddles the boots shell's back wall at z = 3 (1.5 buried, 0.5 proud)
#           and hangs 0.85 past the shell's outer wall at x = 4.9, which is the half of it that
#           actually shows.
#   neck  - the shank, on a bone canted +10 degrees so the wheel rides higher than the strap;
#           geo x 2.00..4.00, y 19.27..21.76, z 1.65..4.95. Its front two depth units are inside the
#           band; its back one is all that shows of it, and the tang goes into the bottom of that.
#   fork  - the block the wheel is set into; geo x 2.00..4.00, y 18.07..21.54, z 5.60..9.08. Two
#           wide against the rowel's one, so it closes over the wheel's lower front from both sides.
#   rowel - the star wheel, 1 thick; geo x 2.50..3.50, y 16.17..19.65, z 6.28..9.76. It stands 1.9
#           above the fork's roof and 0.68 past its back wall, and the rest of it is inside the fork.
#   tang  - the flat member that carries the fork back off the strap; geo x 1.50..4.50,
#           y 19.47..21.15, z 3.85..7.96. Three wide against the neck's and the fork's two, so its
#           outboard and inboard half-units run proud of both cubes it is socketed into.
# Part envelope geo x 1.50..5.75, y 16.17..21.76, z 1.50..9.76, reach 9.43 from the anchor. The pair
# spans 11.50 across the figure and the twin's nearest cube is the tang, 3.00 clear of ours at the
# midline. trace_geometry reports no coplanar face against the naked body or any of the four shells;
# the part's one shared plane is internal, and is the module docstring's subject.
CUBES = {
    "band":  ((4, 2, 2), (0, 0)),
    "neck":  ((2, 2, 3), (12, 0)),
    "fork":  ((2, 3, 3), (22, 0)),
    "rowel": ((1, 3, 3), (32, 0)),
    "tang":  ((3, 1, 4), (40, 0)),
}

# The rowel's silhouette, indexed [y row][z column] with row 0 at the top and column 0 at the FRONT
# (the boot end). A 3 x 3 square with its four corners bitten out, which leaves the axle cell and
# four teeth on the orthogonals - a four-point molette. Five of nine pixels: four ninths of the box
# is air, and that air is what stops the wheel reading as the tab the geometry actually is.
#
# Three of the four bites are real air. The fourth, [2][0], is inside the fork, and it is the one
# that keeps the rowel's underside out of the tang's top plane at y = -0.25.
ROWEL_STAR = [
    ". X .",
    "X X X",
    ". X .",
]
STAR = [row.split() for row in ROWEL_STAR]
LAST = len(STAR) - 1

random.seed(53)  # deterministic output - regenerating must not churn the PNG

# Calibrated against the ramp, not guessed. the material ramp interpolates dark -> mid over
# master values 0..127 and mid -> light over 128..255, so a master confined to one half only ever
# uses half of a material's ramp. The visible pixels here run the fork's shadowed inboard wall to the
# lit tips of the wheel's teeth.
UP = 236        # a top face standing proud of the boot
FACE = 198      # a back face - what a third-person camera sees
FLANK = 176     # an outboard face, the profile the part is designed for
IN = 100        # an inboard face: it looks across at the other boot and lives in its shadow
INNER = 44      # buried - in the boots shell, in the band, in the tang or in the fork
DOWN = 40       # an underside
SLOT = 74       # exposed, but only ever seen down the one-unit gap between the shank and the fork

RIM = 26        # the lit chamfer along a free top edge
STUD = 240      # the one bright pixel on the strap end
ENDBLOCK = 148  # the strap end itself, dropped well below the strap so the stud has a neighbour
FALL = 22       # top-to-bottom falloff down a standing face

# The rowel, painted as a wheel rather than as a star. At 5 x 5 there was room for four values -
# teeth, spoke roots, web, boss - and the lesson learned there was that spreading them evenly turned
# the hub into a checkerboard: the contrast that carries the form is rim-against-hub, not cell against
# neighbouring cell. At 3 x 3 with the corners gone there are only two kinds of cell left, so that
# lesson is not so much applied as enforced. The teeth carry the rim, the single centre cell is the
# axle boss, and the whole reading is the 104 points between them.
W_TOOTH, W_BOSS = 250, 146   # `west`, the hero disc
E_TOOTH, E_BOSS = 148, 82    # `east`, the disc facing the other boot
RIM_UP, RIM_BACK, RIM_FRONT = 226, 190, 106  # the three one-pixel tooth tips that are not buried


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


def fill(img, rect, lum: int, jitter: int = 3) -> None:
    x0, y0, w, h = rect
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            put(img, x, y, lum + random.randint(-jitter, jitter))


def ramp(i: int, n: int) -> float:
    """Position along a face axis, 0.0 at column/row 0 and 1.0 at the far end."""
    return 0.0 if n <= 1 else i / (n - 1)


def paint_band(img) -> None:
    """The heel strap. Four wide, two tall, two deep, straddling the boots shell's back wall so that
    1.5 of its depth is buried and 0.5 stands proud.

    Which of its faces are seen is decided by two planes and nothing else: the shell's back at
    geo z = 3 and the shell's outer wall at geo x = 4.9. The strap's outboard unit (column 3 of any
    x-indexed face) hangs past that wall along its whole length and is visible from every angle; its
    back depth unit (row 0 of `up` and `down`, since those rows run back to front) is the half unit
    that clears the shell. Everything else is inside the boot. The tang's front cap now stands 0.35
    behind the strap's back face - close enough to screen the middle of `south` from dead astern, not
    close enough to bury a single pixel of it, so `south` is painted as though nothing were there.

    The strap end carries the part's only painted detail: a dark end block with one bright stud on
    its top-back corner. The brooch's rule applies at exactly this size - the stud is 240 against 146
    below it and 196 beside it, because at two by two a detail is not a value, it is a value against
    its neighbour, and the generic top-edge chamfer every other column gets would have erased it."""
    size, uv = CUBES["band"]
    f = faces(size, uv)

    x0, y0, fw, fh = f["south"]          # 4 wide x 2 tall, col 0 = OUTBOARD, row 0 = top
    for j in range(fh):
        for i in range(fw):
            if i == 0:
                lum = ENDBLOCK + (14 if j == 0 else -18)      # the strap end, no chamfer
            else:
                lum = FACE + (RIM if j == 0 else -30) - round(10 * ramp(i - 1, fw - 1))
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["west"]           # 2 deep x 2 tall, col 0 = front, row 0 = top
    for j in range(fh):
        for i in range(fw):
            if i == fw - 1 and j == 0:
                lum = STUD                                    # the buckle stud, back-top corner
            else:
                lum = FLANK + (RIM if j == 0 else -FALL) - round(16 * ramp(i, fw))
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["east"]           # 2 deep x 2 tall, col 0 = BACK, so the free one is col 0
    for j in range(fh):
        for i in range(fw):
            lum = (IN - round(FALL * ramp(j, fh))) if i == 0 else INNER
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["up"]             # 4 wide (x) x 2 deep, rows run BACK to front
    for j in range(fh):
        for i in range(fw):
            outboard = i == fw - 1
            if j == 0:
                lum = (ENDBLOCK + 60) if outboard else UP     # the proud half unit
            else:
                lum = (ENDBLOCK + 4) if outboard else INNER   # buried, except past x = 4.9
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["down"]           # 4 wide x 2 deep, rows run back to front
    for j in range(fh):
        for i in range(fw):
            free = j == 0 or i == fw - 1
            put(img, x0 + i, y0 + j,
                ((DOWN + 14 - 8 * j) if free else INNER) + random.randint(-3, 3))

    x0, y0, fw, fh = f["north"]          # 4 wide x 2 tall, col 0 = inboard; only col 3 clears the shell
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j,
                ((IN + 20 - round(FALL * ramp(j, fh))) if i == fw - 1 else INNER)
                + random.randint(-3, 3))


def paint_neck(img) -> None:
    """The shank, on a bone canted +10 degrees so the wheel sits higher than the strap it grows out
    of. Three depth units: index 0 and 1 are inside the band, index 2 is the only one that shows.

    It is two wide and it no longer straddles anything - the fork does that now, three units further
    back - so what the extra width buys here is a shank thick enough to socket the tang into. That is
    also what it costs. The tang runs through the shank's back-bottom at bone-local y -0.25..0.75,
    which is three quarters of the lower row of `west`, of `east` and of `south`, and takes those
    pixels to INNER. The shank is down to two lit flank pixels and a two-pixel cap, and that is the
    honest count: between the strap's back face at geo z = 3.5 and the fork's front at z = 5.6 there
    is about a unit of shank in the open and the tang is lying in half of it.

    `up` and `down` are 2 wide by 3 deep and their rows run BACK to front, so the exposed row - the
    one behind the strap - is row 0, not row 2. The tang's top face is 0.25 below the shank's roof
    and its underside 0.25 above the shank's floor, so it takes nothing from either."""
    size, uv = CUBES["neck"]
    f = faces(size, uv)

    x0, y0, fw, fh = f["west"]           # 3 deep x 2 tall, col 0 = front (in the band), col 2 = free
    for j in range(fh):
        for i in range(fw):
            lum = (FLANK + 24) if (i == fw - 1 and j == 0) else INNER
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["east"]           # 3 deep x 2 tall, col 0 = BACK, the exposed one
    for j in range(fh):
        for i in range(fw):
            lum = (IN + 4) if (i == 0 and j == 0) else INNER
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["up"]             # 2 wide (x) x 3 deep, rows run BACK to front
    for j in range(fh):
        for i in range(fw):
            lum = (UP - 22 + 12 * i) if j == 0 else INNER
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["down"]           # 2 wide x 3 deep, rows run back to front
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j,
                ((DOWN + 12) if j == 0 else INNER) + random.randint(-3, 3))

    x0, y0, fw, fh = f["south"]          # 2 wide x 2 tall, col 0 = OUTBOARD; the tang enters row 1
    for j in range(fh):
        for i in range(fw):
            lum = (ENDBLOCK - 16 * i) if j == 0 else INNER
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    fill(img, f["north"], INNER)         # the front cap, entirely inside the band


def paint_fork(img) -> None:
    """The block the wheel is set into: two wide, three tall, three deep, standing in clear air three
    units behind the boot. Two wide against the rowel's one, and deliberately so - the fork closes
    over the wheel's lower front from both sides, which is what stops a 1-thick plate looking glued
    on, and it is why the fork's x planes are 2.00 / 4.00 and the rowel's are 2.50 / 3.50.

    Nothing of it is inside the boot; the only thing that buries any of it is the tang, which runs
    through its front-bottom at bone-local y -0.25..0.75, z 2.5..4.5 and is half a unit wider than
    the fork on each side. So the INNER pixels are the middle row of `north` and, on `west` and
    `east`, the middle row of the two columns nearest the front. Three quarters of each of those
    pixels is inside the tang, which is the near side of the tie the module docstring describes.

    `south` is the face this cube exists to give the part: 2 x 3 of clear back wall at geo z = 9.08
    with the wheel standing a unit proud of it, and what a player behind another player sees. `up`
    carries the wheel slot - the rowel comes through rows 0 and 1 over the inner half of both
    columns, so those two rows drop 66 below the free row at the front. `north` looks forward into
    the one-unit gap between the shank and this block, and gets SLOT for it."""
    size, uv = CUBES["fork"]
    f = faces(size, uv)

    x0, y0, fw, fh = f["south"]          # 2 wide x 3 tall, col 0 = OUTBOARD, row 0 = top
    for j in range(fh):
        for i in range(fw):
            lum = FACE + (RIM if j == 0 else 0) - round(FALL * ramp(j, fh)) - 16 * i
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["west"]           # 3 deep x 3 tall, col 0 = front; the tang takes row 1, cols 0-1
    for j in range(fh):
        for i in range(fw):
            if j == 1 and i <= 1:
                lum = INNER
            else:
                lum = (FLANK + (RIM if j == 0 else 0)
                       - round(FALL * ramp(j, fh)) + round(12 * ramp(i, fw)))
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["east"]           # 3 deep x 3 tall, col 0 = BACK, so the tang takes cols 1-2
    for j in range(fh):
        for i in range(fw):
            if j == 1 and i >= 1:
                lum = INNER
            else:
                lum = IN + 8 - round(FALL * ramp(j, fh)) - round(10 * ramp(i, fw))
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["north"]          # 2 wide x 3 tall, col 0 = inboard; the tang takes row 1
    for j in range(fh):
        for i in range(fw):
            lum = INNER if j == 1 else SLOT + 10 * i - round(14 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["up"]             # 2 wide (x) x 3 deep, rows run BACK to front
    for j in range(fh):
        for i in range(fw):
            lum = (UP - 66 if j <= 1 else UP) + 10 * i    # rows 0-1 are the wheel slot
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["down"]           # 2 wide x 3 deep, rows run back to front
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j, DOWN + 16 - 6 * j + 6 * i + random.randint(-3, 3))


def paint_tang(img) -> None:
    """The flat member that carries the fork back off the strap: three wide, one thick, four deep.

    It is the only cube of the part wider than two, and the width is the whole point. Its middle unit
    is swallowed - inside the shank at row 3, inside the fork at rows 0 and 1 - while its outboard
    and inboard half-units run proud of both cubes along the entire length. So the burial mask on
    `up` and `down` is the same three pixels, column 1 of rows 0, 1 and 3, and every other pixel of
    those two faces is at least half in the open. Row 2 of column 1 is the exception in the other
    direction: it is the one square unit of the tang's top that nothing covers, at the bottom of the
    gap between the shank and the fork, and it gets SLOT.

    `west` and `east` are four-pixel strips at geo x = 4.50 and x = 1.50, outboard and inboard of
    everything they pass through and covered by none of it. In profile - the angle this part is
    designed for - the outboard strip is the line that reads the spur as one object rather than as a
    strap and a wheel that happen to be near each other, which is why it gets FLANK and a ramp rather
    than a flat fill.

    The caps are three pixels each and lose their middles: `north` at bone-local z = 0.5 is inside
    the shank, `south` at z = 4.5 is inside the fork. What survives on each is a pair of tabs half a
    unit wide, and `south`'s pair is genuinely seen - they sit at geo z = 7.96, flanking the fork."""
    size, uv = CUBES["tang"]
    f = faces(size, uv)

    x0, y0, fw, fh = f["up"]             # 3 wide (x) x 4 deep, col 0 = inboard, rows run BACK to front
    for j in range(fh):
        for i in range(fw):
            if i == 1:
                lum = SLOT if j == 2 else INNER
            else:
                lum = UP - 30 + 14 * i - round(18 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["down"]           # 3 wide x 4 deep, the same mask, rows run back to front
    for j in range(fh):
        for i in range(fw):
            if i == 1:
                lum = (DOWN - 8) if j == 2 else INNER
            else:
                lum = DOWN + 12 + 6 * i - round(8 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["west"]           # 4 deep x 1 tall, col 0 = front - the profile line
    for i in range(fw):
        put(img, x0 + i, y0, FLANK + 12 - round(20 * ramp(i, fw)) + random.randint(-3, 3))

    x0, y0, fw, fh = f["east"]           # 4 deep x 1 tall, col 0 = BACK
    for i in range(fw):
        put(img, x0 + i, y0, IN + 6 - round(16 * ramp(i, fw)) + random.randint(-3, 3))

    x0, y0, fw, fh = f["north"]          # 3 wide x 1 tall, col 0 = inboard; col 1 is in the shank
    for i in range(fw):
        put(img, x0 + i, y0,
            (INNER if i == 1 else SLOT - 16 + 12 * i) + random.randint(-3, 3))

    x0, y0, fw, fh = f["south"]          # 3 wide x 1 tall, col 0 = OUTBOARD; col 1 is in the fork
    for i in range(fw):
        put(img, x0 + i, y0,
            (INNER if i == 1 else FACE - 52 - 10 * i) + random.randint(-3, 3))


def star_at(row: int, col: int) -> bool:
    """Is the rowel opaque at [y row][z column], with column 0 at the FRONT?"""
    return STAR[row][col] == "X"


def in_fork(row: int, col: int) -> bool:
    """Is the whole of this cell inside the fork? The fork spans bone-local y -1.5..1.5, z 2.5..5.5
    and the rowel spans y -3.25..-0.25, z 3.5..6.5, so the cells wholly enclosed are the bottom row's
    front two - the bitten corner and the bottom tooth. The row above them is a quarter enclosed and
    stays lit, which is the area rule from the module docstring doing its one piece of work."""
    return row == LAST and col < LAST


def rowel_value(row: int, col: int, tooth: int, boss: int) -> int:
    """Which value a cell carries: the centre is the axle boss, the four orthogonals are teeth, and
    anything the fork has closed over is INNER whichever of the two it would have been."""
    if in_fork(row, col):
        return INNER
    return boss if (row, col) == (1, 1) else tooth


def paint_rowel(img) -> None:
    """The star wheel. Its two 3 x 3 discs are `west` and `east`; its four rims are one pixel wide
    and three of the four carry a lit tooth tip. The fourth is `down`, whose tooth is inside the
    fork, so it is painted INNER and the rim value it would otherwise have had does not exist in this
    file.

    The alpha is the same star on all six faces, read along a different axis on each:

        west  [row][col]        col 0 = front       - the hero disc
        east  [row][2 - col]    col 0 = back        - mirrored, because east counts z backwards
        up    row -> [0][2 - r] row 0 = back        - the star's top edge
        down  row -> [2][2 - r] row 0 = back        - its bottom edge
        north row -> [r][0]     row 0 = top         - its front edge
        south row -> [r][2]     row 0 = top         - its back edge

    Each of those four rims resolves to exactly one opaque pixel, at r = 1, and that is the whole
    check on the mapping being right: a rim read backwards or off by a row would still yield one
    pixel, but at r = 0 or r = 2, and the tooth would appear to grow out of the wheel's shoulder.

    The value scheme is rim against hub and nothing else. The teeth are the brightest thing on the
    part because they are the rim and the rim is what catches light, and the single boss cell drops
    104 below them on `west`. What the wheel reads as from the side is three teeth radiating out of
    the fork with a dark axle between them, which is what a wheel in a slotted fork looks like."""
    size, uv = CUBES["rowel"]
    f = faces(size, uv)

    x0, y0, fw, fh = f["west"]           # 3 deep x 3 tall, col 0 = front, row 0 = top
    for j in range(fh):
        for i in range(fw):
            if not star_at(j, i):
                continue
            lum = rowel_value(j, i, W_TOOTH, W_BOSS)
            if lum != INNER:
                lum -= round(30 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["east"]           # 3 deep x 3 tall, col 0 = BACK - the star runs the other way
    for j in range(fh):
        for i in range(fw):
            col = fw - 1 - i
            if not star_at(j, col):
                continue
            lum = rowel_value(j, col, E_TOOTH, E_BOSS)
            if lum != INNER:
                lum -= round(16 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["up"]             # 1 wide x 3 deep, rows run BACK to front
    for r in range(fh):
        if star_at(0, fh - 1 - r):
            put(img, x0, y0 + r, RIM_UP + random.randint(-4, 4))

    x0, y0, fw, fh = f["down"]           # 1 wide x 3 deep, rows run back to front - inside the fork
    for r in range(fh):
        if star_at(LAST, fh - 1 - r):
            put(img, x0, y0 + r, INNER + random.randint(-4, 4))

    x0, y0, fw, fh = f["north"]          # 1 wide x 3 tall, the front edge, facing the boot
    for r in range(fh):
        if star_at(r, 0):
            put(img, x0, y0 + r, RIM_FRONT + random.randint(-4, 4))

    x0, y0, fw, fh = f["south"]          # 1 wide x 3 tall, the back edge, seen in third person
    for r in range(fh):
        if star_at(r, LAST):
            put(img, x0, y0 + r, RIM_BACK + random.randint(-4, 4))


def expected_opaque() -> set:
    """The exact set of pixels this master is allowed to leave opaque.

    The five masters before this one could assert `opaque == every claimed rectangle`, because they
    were 100% opaque. This one cannot, and the weaker check - "opaque is a subset of the rectangles"
    - would pass just as happily on a rowel that had lost half its teeth. So the cut is enumerated
    here, from the same STAR table the painter draws from, and the cut and the drawing are compared
    against each other at the end of main()."""
    keep = set()
    for name, (size, uv) in CUBES.items():
        f = faces(size, uv)
        if name != "rowel":
            for (x, y, w, h) in f.values():
                keep |= {(x + i, y + j) for j in range(h) for i in range(w)}
            continue
        x, y, w, h = f["west"]
        keep |= {(x + i, y + j) for j in range(h) for i in range(w) if star_at(j, i)}
        x, y, w, h = f["east"]
        keep |= {(x + i, y + j) for j in range(h) for i in range(w) if star_at(j, w - 1 - i)}
        x, y, w, h = f["up"]
        keep |= {(x, y + r) for r in range(h) if star_at(0, h - 1 - r)}
        x, y, w, h = f["down"]
        keep |= {(x, y + r) for r in range(h) if star_at(LAST, h - 1 - r)}
        x, y, w, h = f["north"]
        keep |= {(x, y + r) for r in range(h) if star_at(r, 0)}
        x, y, w, h = f["south"]
        keep |= {(x, y + r) for r in range(h) if star_at(r, LAST)}
    return keep


def check_geometry() -> None:
    """CUBES must be the cube list of the shipped geometry, in order. Painting a texture for a shape
    the model no longer has is invisible to every other check in this pipeline: both halves stay
    internally consistent while the rectangles slide off the faces they were drawn for."""
    doc = json.loads(GEO.read_text(encoding="utf-8"))
    found = []

    def walk(bone):
        for c in bone.get("cubes", []):
            found.append((tuple(c["size"]), tuple(c["uv"])))
        for child in bone.get("children", []):
            walk(child)

    for bone in doc["bones"]:
        walk(bone)

    assert (doc["texture_width"], doc["texture_height"]) == (TEX_W, TEX_H), \
        f"{GEO.name} is {doc['texture_width']}x{doc['texture_height']}, this master is {TEX_W}x{TEX_H}"
    assert found == list(CUBES.values()), \
        f"CUBES disagrees with {GEO.name}: {found} vs {list(CUBES.values())}"


def check_layout() -> dict:
    """Every face rectangle must sit inside the texture and no two may overlap - a silent overlap
    would paint one cube's shading onto another's face and only show up on a model in game."""
    claimed = {}
    for name, (size, uv) in CUBES.items():
        for face, (x, y, w, h) in faces(size, uv).items():
            assert 0 <= x and x + w <= TEX_W, f"{name}.{face} runs off the texture in u"
            assert 0 <= y and y + h <= TEX_H, f"{name}.{face} runs off the texture in v"
            for py in range(y, y + h):
                for px in range(x, x + w):
                    prev = claimed.get((px, py))
                    assert prev is None, f"{name}.{face} overlaps {prev} at {(px, py)}"
                    claimed[(px, py)] = f"{name}.{face}"
    return claimed


def check_star() -> None:
    """The silhouette must be a four-point molette: the axle cell, four teeth on the orthogonals, and
    the four corners bitten out.

    At 5 x 5 this check had to hunt for teeth attached to the hub only at a corner, because there was
    a ring of cells that could be cut in more than one way and some of those ways left a pixel that
    reads as detached the moment the texture is filtered. At 3 x 3 there is one ring and one legal
    cut, so the assertion that earns its place is the exact one: this table and no other. The corner
    bite at [2][0] is also what keeps the rowel's underside out of the tang's top plane, so a filled
    corner is a z-fighting patch and not merely a squarer wheel - which is why the shape is asserted
    rather than some property of it."""
    assert len(STAR) == 3 and all(len(r) == 3 for r in STAR), "the star must be 3 x 3"
    assert sum(c == "X" for r in STAR for c in r) == 5, "5 opaque cells: one axle and four teeth"
    assert star_at(1, 1), "the axle cell must be solid"
    for j, i in ((0, 0), (0, 2), (2, 0), (2, 2)):
        assert not star_at(j, i), f"corner [{j}][{i}] must be bitten out"
    for j, i in ((0, 1), (1, 0), (1, 2), (2, 1)):
        assert star_at(j, i), f"tooth [{j}][{i}] must be solid"


def main() -> None:
    check_geometry()
    check_star()
    claimed = check_layout()
    img = Image.new("LA", (TEX_W, TEX_H), (0, 0))
    paint_band(img)
    paint_neck(img)
    paint_fork(img)
    paint_rowel(img)
    paint_tang(img)

    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque <= set(claimed), "painted pixels fall outside the UV rectangles"
    assert opaque == expected_opaque(), "the painted silhouette is not the silhouette STAR describes"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    cut = len(claimed) - len(opaque)
    print(f"wrote {OUT} ({len(opaque)} opaque px, {cut} cut by alpha, values {min(lums)}-{max(lums)})")


if __name__ == "__main__":
    main()
