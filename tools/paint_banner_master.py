"""
Paint the grayscale master for the "banner" part.

Like the brooch, sash, tassets, spurs, greaves, brush_crest and vambraces painters this does not
merely claim that CUBES matches the shipped geometry, it reads
assets/armorpieces/armorpieces/decoration/banner.json at run time and asserts it - sizes, uv AND
pivot-relative origins, because on this part the positions are not decoration: every INNER pixel
below is decided by testing a face pixel against the other cubes and against the chestplate shell,
and the whole swallowtail is a table of cells that has to agree with the cube it is cut out of.
Output goes to tools/decoration_masters/banner.png, which sync_decoration_masters.py installs for
the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

**No static layer, deliberately.** This is the one part in the mod whose largest face is *meant* to
take the trim material over its whole area: a gold banner and a redstone banner are two heraldic
tinctures, and that expressiveness is the reason the part exists. Painting the field ivory or crimson
in a static layer would throw exactly that away.

--------------------------------------------------------------------------------------------------
The part, in numbers

`BACK` is `Attachment.of(BODY, 0, 2, 2)` and is not mirrored, so part-local (0, 0, 0) is body-local
(0, 2, 2) - the upper back, one unit inside the torso's own back wall. Two frames are quoted
throughout: *part-local* (what the geometry JSON holds) and *geo* (part-local + (0, 2, 2)), which is
what trace_geometry.py prints and what every number in PLAN.md is in. The torso box is geo
x -4..4, y 0..12, z -2..2; the chestplate's 1.0-inflate shell, the only one guaranteed present when
this part draws, is x -5..5, y -1..13, z -3..3; the leggings' 0.5 shell over the torso is
x -4.5..4.5, y -0.5..12.5, z -2.5..2.5.

    cube     part-local                                     geo
    cloth    x -3.50..3.50  y 1.50..13.50  z  3.25..4.25    x -3.50..3.50  y  3.50..15.50  z 5.25..6.25
    staff    x -0.50..0.50  y 2.00.. 9.00  z  2.50..3.50    x -0.50..0.50  y  4.00..11.00  z 4.50..5.50
    finial   x -1.50..1.50  y 0.50.. 2.50  z  3.00..4.00    x -1.50..1.50  y  2.50.. 4.50  z 5.00..6.00
    mount    x -2.00..2.00  y 0.75.. 3.75  z -0.25..2.75    x -2.00..2.00  y  2.75.. 5.75  z 1.75..4.75

Four cubes, one bone, no rotations - the third part in the mod with none, after the greaves and the
vambraces, and for their reason: a hanging banner is a flat plane and there was nothing to cant.

**The stack runs front to back and never repeats a plane.** mount (-0.25..2.75), staff (2.50..3.50),
finial (3.00..4.00), cloth (3.25..4.25): eight z planes, eight distinct values, each cube overlapping
the next by a quarter or a half so the part is one welded object rather than four plates in a row.
That ordering is the whole reading of the part - **the cloth is the outermost cube and the pole hangs
behind it**, which is how a banner is actually carried, and it is why the pole contributes nothing to
the hero face except the ridge it tents into it. check_planes() asserts the eight-distinct part,
because a flush face here is not tidiness, it is two coplanar quads under `armorCutoutNoCull`
fighting for one depth.

--------------------------------------------------------------------------------------------------
Why this is not a bedsheet, in numbers - and where that argument has been spent

PLAN.md's oldest finding is that the feathering read as a banner and **depth was the culprit, not
height**; the horns rework found the same thing again (7.8 units of depth against 4.5 of lateral
travel is a swept fin, not a horn). This part is the thing both of those were warned away from, so
the depth budget was set first and everything else was fitted inside it.

  * **The cloth's own plane is one unit thick and stands at z 5.25..6.25** - 2.25 to 3.25 past the
    chestplate surface at z = 3. The whole part reaches z = 6.25, which is **3.25 past the wall**:
    less than `wing_roots` on this same socket (3.59), less than the horns' 3.5-past-the-helmet
    precedent that PLAN.md treats as the ceiling, and less than half the spurs' 6.7, which that file
    already calls generous-bordering-on-too-much. **Nothing goes past the field.** The field *is* the
    far face of the part, and the pole, the spearhead and the bracket all live in the three and a
    half units of depth between it and the torso.
  * **Its silhouette is not a rectangle.** The swallowtail below takes 14 of the field's 84 cells out
    of alpha - one sixth of the plate - so the outline forks into two tails. That is the feathering's
    own lesson ("a part's silhouette lives in the master's alpha") applied to the shape that most
    needs it.
  * **The finial breaks the top of the outline** the way the wing roots' keel tab breaks the bottom
    of theirs: its point stands at geo y 2.50 against the field's hem at 3.50, and the bracket's top
    at 2.75 shows above the hem beside it. The staff does no work here - it is inside the field's
    outline on every axis - so the top of the part is the spearhead and the bracket and nothing else.

**It is not narrow, and the rest of this file is written around that.** The field is 7 wide and 12
tall against a torso 8 wide and 12 tall: it covers the back almost exactly. The "a banner that reads
as a bedsheet is one whose area competes with the back it hangs on" test is therefore **not** what
carries this shape - it fails that test outright. What carries it instead is the depth budget above,
the forked outline, and the fact that the field is a shaded surface rather than a flat one: the pole
tents it along the middle column and the two columns either side of that fall 48 values into shadow,
so even under one tincture the field reads as cloth over a stave rather than as a rectangle of paint.

**The arms are a clearance, not a proof, and the width is what spends it.** Every rotation on this
body - arm swing, leg swing, body pitch - is about X, and X is preserved, so a part that stays
inboard of the chestplate's 1.0-inflate arm sleeve, whose inboard wall is at geo x = 3, disposes of
the arms with an inequality and no swept envelope at all. The field is 7 wide, so its outer
half-texel - the band x 3.00..3.50 on each flank - is inside the sleeve's own x range, and the
question becomes an angle instead. The sleeve's back-bottom edge sits 11 under the shoulder pivot and
3 behind it, so on a backswing of t it reaches z = 3 cos(t) + 11 sin(t), which meets the field's
front face at z = 5.25 at **12.2 degrees**. That is a twelfth of a stride: the chestplate's own
sleeve passes through the outer half of the field's outermost column for most of a walk cycle. Half a
texel is a small thing to lose and it is lost identically on both flanks, so nothing reads asymmetric
- but it is the price of the seventh column, and it is worth knowing that a 5-wide field does not pay
it.

**The head costs nothing here, for the wing roots' reason plus one more.** Nothing on the part rises
above geo y = 2.50, a clear 1.50 under the 1.0-inflate helmet's rest bottom at y = 1, and head *yaw*
preserves y, so that holds at every turn with no further argument. Head *pitch* is the case the wing
roots had to concede - their bar's top-back corner (y 2.5, z 4) enters the helmet box at 19.8 degrees
of looking up. This part sits further back, and past the helmet's own back wall at z = 5 that stops
being a cost and becomes the defence: the finial's top-front corner (y 2.5, z 5) needs
z_local = 2.5 sin(t) + 5 cos(t) <= 5 before the helmet can contain it at all, which does not happen
until **53.1 degrees**; its top-back corner (y 2.5, z 6) until 62.3; the mount's top-back corner
(y 2.75, z 4.75) until 54.4; the field's top-front corner (y 3.5, z 5.25) until 71.3. The part is
swallowed by a raised chin roughly two and a half times later than the part already on this socket.

**Where it stops against the legs, which is the expensive clearance on this part.** The thighs pitch
about X from pivots at (+-1.9, 12, 0) and cover x -4.4..4.4, so - the sash's finding - there is no x
to escape to and a hanging tail is swept by a thigh sooner or later; the only question is how soon.
The field hangs to geo y = 15.50, which is 3.50 *below* the leg pivot, and the leggings' 0.5 shell
contains a point once its z in the thigh's own frame falls to 2.5:

    the tail tips       (y 15.50, z 5.25)   5.25 cos(t) - 3.50 sin(t) <= 2.5   at  32.9 degrees
    the fork's mouth    (y 13.50, z 5.25)   5.25 cos(t) - 1.50 sin(t) <= 2.5   at  46.7 degrees
    the hip line        (y 12.00, z 5.25)   5.25 cos(t)               <= 2.5   at  61.6 degrees

The vanilla leg term reaches 80 degrees at a sprint and runs 40 to 64 at an ordinary walk, so **the
tails are inside a thigh while walking** and the fork's mouth joins them at a brisk one. For scale,
PLAN.md accepts 47.5 degrees on the tassets' leading lame and records that the leggings' own torso
shell is inside the thigh at 0, so this is the same kind of concession that file already makes, taken
several rows further down. Each row of field costs about ten degrees of it, and the four rows below
the hip line cost exactly that: a field that stopped at geo y = 11.50 would not meet a thigh until
68.3.

**Neither the brooch nor the sash is touched, and that was designed rather than discovered.** The
sash's back bar reaches geo z 4.00 across x -6..7.25 and y 7.50..18.73 - exactly the corridor a
banner hangs down. The nearest thing this part puts in that corridor is the staff at geo z 4.50, half
a unit clear, and the field itself is 1.25 clear at z 5.25. `trace_geometry.py` reports zero COPLANAR
lines and "all clear by more than half a unit" against both bone-mates.

--------------------------------------------------------------------------------------------------
The swallowtail, and how an alpha cut works on a one-unit plate

CUT below is a set of (column, row) cells in each cube's own x-y grid, columns counted from min x and
rows from min y, and it is a **through-cut**: the cell is removed from the whole depth of the cube.
That is the only kind of cut a part drawn with `armorCutoutNoCull` can afford, and PLAN.md says why -
a hole shows the far face of the same box, so a cut only works where the two faces line up. Both cut
cubes are exactly one unit deep, so they do: you look through the notch and out the far side, not
into an interior.

The heel_wings' warning is the other half of it, and it is what makes the cut a table rather than a
loop over one face: **the edge faces run along the rows the cut removes**, and left painted they hang
in the air as a one-pixel outline of a shape that is no longer there. So a face pixel is transparent
whenever the cell of the cube's outer layer it belongs to is cut - `down` follows the bottom row,
`east` and `west` follow the first and last columns, `up` follows the top row, and `north`/`south`
follow the grid itself, in opposite directions. `expected_opaque()` builds the whole opaque set from
CUT and main() asserts the drawing against it, which is the spurs' discipline: the weaker "opaque is
a subset of the claimed rectangles" passes happily on a banner that has lost its tails.

    field rows (0 = top), * opaque, . cut          the tails are 1 x 2 x 1 solids, not slivers:
        0-7  * * * * * * *                         each keeps its own outer side face, its own
        8    * * * . * * *                         underside and both of its big faces, so what
        9    * * . . . * *                         survives is a real volume rather than a
       10    * . . . . . *                         one-pixel line of colour
       11    * . . . . . *

Fourteen of the field's eighty-four cells; a fork four rows deep on a field twelve rows tall. The V
opens one column per row from a single-cell apex until it is w - 2 wide, then runs straight for the
last two rows, which is the widest mouth a field can hold and still keep two tails. The apex has to
be one column, so on an odd field the fork is odd all the way down and the tails are what is left
over - the same elimination the rowel's 5 x 5 grid came out of, and a second reason the field wants an
odd width quite apart from the pole.

The finial is cut the same way and for the same reason - its top row keeps only its centre column, so
a 3 x 2 block becomes a spearhead - and the two cuts do different jobs: the tails stop the outline
being a rectangle at the bottom, the point stops it being one at the top.

--------------------------------------------------------------------------------------------------
Burial is computed, and it has to know about the holes

The vambraces' method - sample each face over its pixel footprint, push 0.05 along the normal, test
containment against the boxes that could hide it - decides every INNER pixel here, and on this
geometry it decides a great many of them, because the field stands in front of everything:

  * the **pole's whole back face** is inside the field, all seven rows of it. The pole is 0.75 proud
    of the field's inner surface and 0.25 sunk into it, so it is a stave leaning on cloth rather than
    a stripe drawn on it, and not one pixel of it reaches the hero face.
  * the **field's own inner face** loses its middle column over the six rows the pole fully spans,
    and the middle three cells of its top row to the spearhead standing behind them.
  * the **spearhead's back face** loses everything but the point, which is the one cell of it above
    the field's hem. It is the *back* of the finial that goes, not the front, and only because the
    cloth is the outermost cube: reverse the stack and the same test would take the other face, so
    which one it is has to be read off the z ordering rather than remembered.
  * the **bracket's front face** is inside the chestplate shell, and so is one of its three depth
    indices on the top, the underside and both flanks - part-local z -0.25..0.75, the unit that is
    through the wall and into the torso.

`covers()` tests containment *and* then asks whether every cell of the occluder that the sample's
footprint touches is opaque, because a box with an alpha cut in it is not an occluder over that cut.
That refinement is PLAN.md's, it came out of this part, and on the present geometry **it saves no
pixel**: the pole's foot stops at part-local y 9.00 and the fork's first cut row does not begin until
9.50, so nothing at all stands behind the notch to be wrongly buried. check_mask() asserts that half
unit rather than describing it, because the staff is one edit taller than being false again, and the
plain box test would then quietly bury rows of pole that are looked straight through.

**The one thing the mask does not find is the bracket's back face.** The field clears it by half a
unit - the bracket stops at part-local z 2.75 and the field's inner surface is at 3.25 - so those
twelve pixels are painted rather than INNER. They are not *seen* in any useful sense, because the
field covers them completely in x and in y from behind, but the mask is a containment test and not a
judgement, and a half-unit slot is a half-unit slot: they are edge-on visible in the gap from below
and from the flanks, so they take the gap's own dark value instead of the buried one.

Everything the mask does find is permanent in the one direction that matters. The chestplate shell
rides BODY exactly as this part does, so the mount's buried unit stays buried at every pose - the
tassets' warning about rows that uncover on a stride is about a part on a *different* bone from its
shell and does not apply here.

--------------------------------------------------------------------------------------------------
Faces, directions and the palette

Face rectangles come from paint_circlet_master.faces(), copied verbatim: row one (v .. v+d) holds up
then down, each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west, south with
widths d, w, d, w. Orientation inside each rectangle is PLAN.md's measured table:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x              max z (back)
    down            +y  (underside)      min x              max z (back)
    west            +x                   min z (front)      min y (top)
    east            -x                   max z (back)       min y (top)
    north           -z  (front)          min x              min y (top)
    south           +z  (back)           max x              min y (top)

The four nets tile the sheet left to right in the order the cubes are declared. The field's net is
16 x 13 - a one-deep 7 x 12 plate pays for its depth twice in u and once in v - so it takes u 0..16
and everything downstream of it starts where it ends: staff at 16, finial at 20, mount at 28, the
last of them finishing at u = 42 on a 64 x 32 sheet. check_layout() asserts that packing pixel by
pixel, in both directions: no rectangle off the sheet, no two rectangles on the same pixel.

`BACK` is a single, non-mirrored attachment, so - the wing roots' note - `west` is the +x face of the
one and only copy and there is no `scale(-1, 1, 1)` to make one master serve two sides. That costs
nothing here, because the part is symmetric about x = 0 and both flanks are painted the same. What it
does not excuse is the **mount**, which is three units deep: its `east` counts z back to front and
its `west` counts front to back, so the proud-end highlight is column 0 on one and column 2 on the
other. Running them the same way lights the bracket from the front on one flank and from the back on
the other, and it is the only place on this part where the direction table has teeth. The field, the
staff and the finial are all one unit deep, so their side rectangles are a single column and have no
direction to get wrong.

Which faces are seen, since the wing roots' warning is that these constants never transfer between
parts by name:

  * `south` is the hero and it is not close. The field's back face is the banner - 70 opaque cells and
    **not one of them buried**, because the field is the outermost cube on the part and nothing stands
    between it and the camera. Third person is the angle a player looks at their own character from,
    and this is what they look at. Of the master's 283 opaque pixels, 237 survive the burial mask and
    140 sit below 127.
  * `west`/`east` are one pixel of thickness each and twelve tall, and they are what stops a flat part
    reading as a decal in profile. They carry the tails' outline.
  * `up` is the top hem, seven cells, seen from above and from any camera higher than the shoulder.
  * `north` faces the wearer's back across a 2.25-unit gap to the chestplate surface. It is seen from
    below and from low angles and it is painted dark for it, and at 61 surviving cells it is where
    most of this master's sub-127 content comes from.
  * `down` is two tail tips, the pole's foot, the spearhead's underside and the bracket's ledge, seen
    only from below.

The circlet's lesson matters more here than on any other part, because the field is the largest
material-coloured area in the mod: the material ramp interpolates dark -> mid over 0..127 and
mid -> light over 128..255, so a master that never dips under the middle confines every tincture to
the light half of its ramp and makes gold and copper the same banner. The field itself is meant to
sit high - it is the tincture - so the dark half is bought elsewhere: the inner face, the gap the
bracket looks into, every underside, and the fold shadows either side of the pole's ridge, which are
the one place the hero face itself comes down to meet the middle.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "banner.json"
OUT = ROOT / "tools" / "decoration_masters" / "banner.png"

TEX_W, TEX_H = 64, 32

# size (w, h, d), uv (u, v) and pivot-relative origin, mirroring banner.json in that file's own
# order. The single bone sits at the anchor with no rotation, so origin IS the part-local corner.
#   cloth  - the heraldic field: one unit thick, 7 x 12, swallowtailed in alpha. The material's face,
#            and the outermost cube on the part - everything else hangs behind it.
#   staff  - the pole down the field's centre line, 0.75 proud of the field's inner surface and 0.25
#            sunk into it, socketed at the top into the mount. One unit wide so that it lands on the
#            field's middle column exactly.
#   finial - the spearhead crowning the staff, its top row cut to a point, and the only cube that
#            breaks the top of the part's outline.
#   mount  - the bracket at the shoulder blades, three deep: 1.25 buried through the chestplate wall
#            and into the torso, 1.75 proud, its back face half a unit short of the field.
CUBES = {
    "cloth":  ((7, 12, 1), (0, 0),  (-3.5, 1.5, 3.25)),
    "staff":  ((1, 7, 1),  (16, 0), (-0.5, 2.0, 2.5)),
    "finial": ((3, 2, 1),  (20, 0), (-1.5, 0.5, 3.0)),
    "mount":  ((4, 3, 3),  (28, 0), (-2.0, 0.75, -0.25)),
}

# Cells removed from a cube's x-y grid, columns from min x and rows from min y. A through-cut: the
# cell goes from the whole depth, which is the only cut that works under armorCutoutNoCull and is
# free here because both cut cubes are exactly one unit deep. See the module docstring.
CUT = {
    "cloth": {(3, 8),
              (2, 9), (3, 9), (4, 9),
              (1, 10), (2, 10), (3, 10), (4, 10), (5, 10),
              (1, 11), (2, 11), (3, 11), (4, 11), (5, 11)},
    "finial": {(0, 0), (2, 0)},
}

# The chestplate's 1.0-inflate shell in part-local coordinates (geo x -5..5, y -1..13, z -3..3 shifted
# by the anchor at (0, 2, 2)). It is the only shell guaranteed present when this part draws, it rides
# the same bone, and so anything inside it is buried permanently.
SHELL = ((-5.0, -3.0, -5.0), (5.0, 11.0, 1.0))

PUSH = 0.05      # how far off a face a sample sits before it is tested for containment
EPS = 1e-9

random.seed(41)  # deterministic output - regenerating must not churn the PNG

FIELD = 206     # the field's south face: the heraldic tincture, and the point of the whole part
RIDGE = 222     # the field's middle column, tented out by the pole standing behind it
GUTTER = 158    # the two columns flanking that ridge: the folds the tenting drags into shadow
HEM = 26        # added along a free edge of the field - the top, and every cut edge of the tail
SIDEHEM = 12    # added where the field's neighbour across a column is gone, cut away or off the edge
EDGE = 178      # west/east, one pixel of cloth thickness - the profile silhouette
UPFACE = 238    # a free top face
POLE = 246      # the staff's south face: hardware, brighter than any cloth on the part
PFLANK = 152    # the staff's flanks, standing in the gap behind the field
RING = -74      # a binding band on the staff, at one axial index on all four of its side faces
FINIAL = 252    # the spearhead's point
BACKF = 116     # north: the field's inner face, across the gap to the wearer's back
MOUNT = 142     # the bracket's seen flanks
RIVET = 74      # a bolt through the bracket: +74 against a dropped row, not +30 against the field
DOWNF = 74      # a free underside
INNER = 44      # buried - in the chestplate shell, or in another cube of this part

FALL = 34       # top-to-bottom falloff down the twelve rows of the hanging field
ZFALL = 24      # front-to-back falloff across the mount's three units of depth


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


FACE_ORDER = ("up", "down", "east", "north", "west", "south")


def bounds(name):
    """A cube's part-local (lo, hi) corners."""
    size, _, origin = CUBES[name]
    return tuple(origin), tuple(origin[a] + size[a] for a in range(3))


def geo_cell(name, face, i, j):
    """The (column, row) of the cube's own x-y grid that this face pixel belongs to.

    A through-cut removes a cell from every face that touches it, so this is the single mapping the
    whole alpha silhouette is built from: `up` follows the top row, `down` the bottom row, `east` the
    first column and `west` the last, and the two big faces are the grid itself read in opposite
    directions. Getting `south` the same way round as `north` would mirror the cut - invisible on a
    symmetric notch, which is exactly why it is written down rather than relied on."""
    w, h, _ = CUBES[name][0]
    if face == "up":
        return (i, 0)
    if face == "down":
        return (i, h - 1)
    if face == "east":
        return (0, j)
    if face == "west":
        return (w - 1, j)
    if face == "north":
        return (i, j)
    if face == "south":
        return (w - 1 - i, j)
    raise KeyError(face)


def solid(name, col, row) -> bool:
    """Is this cell of a cube's x-y grid there at all?"""
    return (col, row) not in CUT.get(name, ())


def face_opaque(name, face, i, j) -> bool:
    return solid(name, *geo_cell(name, face, i, j))


def cell(name, face, i, j):
    """The part-local footprint of one face pixel, already pushed 0.05 off the face.

    The two in-plane axes span the pixel's whole unit square rather than just its centre, so a pixel
    only counts as buried when *all* of it is. The normal axis is a single value, which is what makes
    the test "is this sample inside that box" rather than "do these boxes touch"."""
    lo, hi = bounds(name)
    if face == "up":                       # col 0 = min x, row 0 = max z, normal -y
        return ((lo[0] + i, lo[1] - PUSH, hi[2] - j - 1), (lo[0] + i + 1, lo[1] - PUSH, hi[2] - j))
    if face == "down":                     # col 0 = min x, row 0 = max z, normal +y
        return ((lo[0] + i, hi[1] + PUSH, hi[2] - j - 1), (lo[0] + i + 1, hi[1] + PUSH, hi[2] - j))
    if face == "east":                     # col 0 = max z, row 0 = min y, normal -x
        return ((lo[0] - PUSH, lo[1] + j, hi[2] - i - 1), (lo[0] - PUSH, lo[1] + j + 1, hi[2] - i))
    if face == "west":                     # col 0 = min z, row 0 = min y, normal +x
        return ((hi[0] + PUSH, lo[1] + j, lo[2] + i), (hi[0] + PUSH, lo[1] + j + 1, lo[2] + i + 1))
    if face == "north":                    # col 0 = min x, row 0 = min y, normal -z
        return ((lo[0] + i, lo[1] + j, lo[2] - PUSH), (lo[0] + i + 1, lo[1] + j + 1, lo[2] - PUSH))
    if face == "south":                    # col 0 = max x, row 0 = min y, normal +z
        return ((hi[0] - i - 1, lo[1] + j, hi[2] + PUSH), (hi[0] - i, lo[1] + j + 1, hi[2] + PUSH))
    raise KeyError(face)


def _span(lo_v, hi_v, base, count):
    """The indices of a cube's unit cells along one axis that a [lo, hi] interval touches."""
    first = int(math.floor(lo_v - base + EPS))
    last = int(math.ceil(hi_v - base - EPS)) - 1
    if last < first:
        last = first
    return range(max(0, first), min(count - 1, last) + 1)


def covers(other, clo, chi) -> bool:
    """Does cube `other` hide this sample - box containment AND no hole over it?

    A box with a cut in it is not an occluder over that cut. No pixel on the present geometry is
    saved by the second half of that test, because the pole's foot stops half a unit above the fork
    and nothing else stands behind the notch - but the staff is one edit taller than needing it
    again, and check_mask() asserts the half unit that keeps it inert."""
    blo, bhi = bounds(other)
    if not all(blo[a] - EPS <= clo[a] and chi[a] <= bhi[a] + EPS for a in range(3)):
        return False
    w, h, _ = CUBES[other][0]
    for col in _span(clo[0], chi[0], blo[0], w):
        for row in _span(clo[1], chi[1], blo[1], h):
            if not solid(other, col, row):
                return False
    return True


def buried(name, face, i, j) -> bool:
    """True when the whole of this face pixel is inside the chestplate shell, or inside another cube
    of the part that is opaque over it."""
    clo, chi = cell(name, face, i, j)
    if all(SHELL[0][a] - EPS <= clo[a] and chi[a] <= SHELL[1][a] + EPS for a in range(3)):
        return True
    return any(covers(other, clo, chi) for other in CUBES if other != name)


def staff_column() -> int:
    """The field column the pole stands behind, derived rather than written down.

    "An odd rib wants an odd host": a 1-wide pole on a 7-wide field lands on one column exactly, and
    the read - field, field, gutter, ridge, gutter, field, field - comes free. On an even field it
    would straddle two, and every centre-line value below would be a lie about where the pole is."""
    clo, _ = bounds("cloth")
    slo, shi = bounds("staff")
    cols = list(_span(slo[0], shi[0], clo[0], CUBES["cloth"][0][0]))
    assert len(cols) == 1, f"the pole straddles field columns {cols}"
    return cols[0]


def pole_rows() -> set:
    """The field rows the pole stands behind at all, which is where the ridge and its two gutters get
    painted. The pole is 7 tall on a field of 12, so the bottom third of the field hangs free and is
    shaded flat across its whole width - and two rows under the pole's foot the fork opens."""
    lo_y = bounds("cloth")[0][1]
    s_lo, s_hi = bounds("staff")[0][1], bounds("staff")[1][1]
    h = CUBES["cloth"][0][1]
    return {k for k in range(h) if lo_y + k < s_hi - EPS and lo_y + k + 1 > s_lo + EPS}


STAFF_COL = staff_column()
POLE_ROWS = pole_rows()


def put(img, x: int, y: int, lum: int, alpha: int = 255) -> None:
    if 0 <= x < TEX_W and 0 <= y < TEX_H:
        img.putpixel((x, y), (max(0, min(255, lum)), alpha))


def ramp(i: int, n: int) -> float:
    """Position along a face axis, 0.0 at column/row 0 and 1.0 at the far end."""
    return 0.0 if n <= 1 else i / (n - 1)


def paint_face(img, name, face, value) -> int:
    """Fill one face rectangle: nothing where the cut removed the cell, INNER where the burial test
    says the pixel cannot be seen, the painter's value otherwise.

    Returns the number of pixels that survived as visible, which main() reports - a face whose count
    goes to zero after a geometry edit is the loudest warning this file can give without failing."""
    x0, y0, fw, fh = faces(CUBES[name][0], CUBES[name][1])[face]
    seen = 0
    for j in range(fh):
        for i in range(fw):
            if not face_opaque(name, face, i, j):
                continue
            if buried(name, face, i, j):
                lum = INNER
            else:
                lum = value(i, j, fw, fh)
                seen += 1
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))
    return seen


# ------------------------------------------------------------------------------------------------
# the cloth - the field, and everything the swallowtail does to its edges


def _field_edges(col, row):
    """(free lower edge, free side edge) for one cell of the field's grid.

    A swallowtail is only a silhouette until its cut edges are lit; a hem along every free lower edge
    is what turns four removed rows into a shaped hem, and it costs nothing, because those are the
    pixels that were going to be the outline anyway."""
    w, h, _ = CUBES["cloth"][0]
    below = row + 1 >= h or not solid("cloth", col, row + 1)
    beside = ((col - 1 < 0 or not solid("cloth", col - 1, row))
              or (col + 1 >= w or not solid("cloth", col + 1, row)))
    return below, beside


def cloth_south(i, j, fw, fh):
    """The field, and the largest material-coloured surface in the mod. Column 0 is max x, so the grid
    column is 6 - i; the pole stands *behind* column 3 and tents the cloth out along it, so that column
    is a ridge and not a cast shadow - which is the one thing about this face that has to be read off
    the z ordering rather than assumed. Columns 2 and 4 are the folds the tenting drags down either
    side, and 0, 1, 5 and 6 are field. That is the greaves' five-band read - field, gutter, spine,
    gutter, field - arriving by construction on an odd host, with a spare column of plain field on
    each flank because the field is 7 wide and the rib is 1.

    The banding stops where the pole does. Below its foot the cloth hangs free and is shaded flat
    across its whole width, and two rows after that the fork opens."""
    col = fw - 1 - i
    if j in POLE_ROWS and col == STAFF_COL:
        lum = RIDGE
    elif j in POLE_ROWS and abs(col - STAFF_COL) == 1:
        lum = GUTTER
    else:
        lum = FIELD
    lum -= round(FALL * ramp(j, fh))
    below, beside = _field_edges(col, j)
    if j == 0:
        lum += HEM
    if below:
        lum += HEM
    if beside:
        lum += SIDEHEM
    return lum


def cloth_north(i, j, fw, fh):
    """The field's inner face, 2.25 units off the chestplate surface and the darkest large area on the
    part. Seen from below and from any low camera - the gap it faces into is where the pole and the
    bracket live. Lightens downward, because past the torso's own bottom the gap stops being a gap and
    opens on daylight. The middle column and the top row's middle cells never reach this painter: the
    pole and the spearhead stand behind them and the mask paints them INNER."""
    lum = BACKF - 8 + round(16 * ramp(j, fh))
    below, _ = _field_edges(i, j)
    return lum + (14 if below else 0)


def cloth_up(i, j, fw, fh):
    """The top hem, 7 x 1. The brightest run on the part after the finial, and the only face that says
    the field has a thickness when the camera is above the shoulder. Nothing buries it: the spearhead
    behind it is a quarter of a unit short of the hem's own depth."""
    return UPFACE - round(12 * abs(ramp(i, fw) - 0.5) * 2)


def cloth_down(i, j, fw, fh):
    """Two tail tips, and nothing else - the middle five columns went with the notch."""
    return DOWNF + 12


def cloth_west(i, j, fw, fh):
    """One pixel of thickness down the +x edge, 12 tall. This face and its `east` twin carry the whole
    silhouette in profile, which is the angle at which a flat part is most at risk of vanishing. One
    column deep, so there is no front-to-back direction here to get backwards - the mount is the only
    cube on this part where that matters."""
    lum = EDGE - round(FALL * ramp(j, fh))
    return lum + (HEM if j in (0, fh - 1) else 0)


def cloth_east(i, j, fw, fh):
    """The -x edge. Painted identically to `west`: the part is symmetric about x = 0 and `BACK` never
    mirrors, so the two flanks are one flank seen from opposite sides."""
    return cloth_west(i, j, fw, fh)


# ------------------------------------------------------------------------------------------------
# the staff


def staff_south(i, j, fw, fh):
    """The pole's back face, and every pixel of it is INNER: it is inside the field over its whole
    length, which is the point of hanging the pole behind the cloth. The values are kept anyway,
    because the mask decides what is drawn and this file does not get to assume the mask agrees with
    it - and because a pole ever lengthened past the fork will want them. At this width a binding band
    is a single pixel, and it is placed at the same axial row on all four side faces so that it closes
    round the pole's corners - the horns' ring trick, spent on a lashing."""
    if j in (1, 5):
        return POLE + RING
    return POLE - round(18 * ramp(j, fh))


def staff_west(i, j, fw, fh):
    """A flank, standing in the gap between the field and the wearer's back. Three quarters of this one
    pixel is in open air and a quarter is sunk into the cloth, so it is the only sign from the side
    that the banner is carried on something. A third under the pole's own back face, because the gap
    it stands in is shadow."""
    if j in (1, 5):
        return PFLANK + RING // 2
    return PFLANK - round(14 * ramp(j, fh))


def staff_east(i, j, fw, fh):
    return staff_west(i, j, fw, fh)


def staff_north(i, j, fw, fh):
    """The pole's front face, looking back at the wearer. Row 0 is inside the bracket and painted INNER
    by the mask - that socket is what makes this a mounted pole rather than a floating one - and rows
    1 to 6 look down the gap and are painted for it."""
    return BACKF - 6 + round(12 * ramp(j, fh))


def staff_up(i, j, fw, fh):
    """One pixel, half of it under the spearhead and the rest under the field's top rows. A sliver in
    permanent shade, which is why it does not get a top face's value."""
    return UPFACE - 96


def staff_down(i, j, fw, fh):
    """The pole's foot, hanging in the gap two rows above the fork and lit from below."""
    return DOWNF + 20


# ------------------------------------------------------------------------------------------------
# the finial


def finial_south(i, j, fw, fh):
    """The spearhead's back face. Row 1 is inside the field and INNER; row 0 is a single cell - the
    point, standing one unit above the field's hem - and it is the brightest pixel on the part,
    because a finial is polished metal against cloth and because at one pixel a form is nothing but a
    value against its neighbours."""
    if j == 0:
        return FINIAL
    return FINIAL - 26


def finial_north(i, j, fw, fh):
    """The spearhead's front face, and the larger half of it: four cells against the back face's one,
    because the field buries the back and nothing buries this. Row 0 clears the field's hem and
    catches light over the shoulder; row 1 is down in the gap with the pole and takes the gap's
    value."""
    if j == 0:
        return FINIAL - 56
    return BACKF + 26


def finial_up(i, j, fw, fh):
    return UPFACE + 12


def finial_down(i, j, fw, fh):
    """The spearhead's underside, proud of the staff on all three columns and lit as the boundary
    between hardware and cloth."""
    return DOWNF + 30 - (10 if i in (0, fw - 1) else 0)


def finial_west(i, j, fw, fh):
    """One pixel of the spearhead's flank - row 0 went with the point. It sits well inside the field's
    outline in x, so it is hardware seen edge-on against cloth rather than against the sky."""
    return MOUNT + 30


def finial_east(i, j, fw, fh):
    return finial_west(i, j, fw, fh)


# ------------------------------------------------------------------------------------------------
# the mount - the only cube on this part deep enough for its two flanks to disagree


def mount_east(i, j, fw, fh):
    """The -x flank, three deep. Column 0 is max z, the proud end that stands out behind the
    chestplate; column 2 is buried through the wall. A rivet sits in the proud column."""
    lum = MOUNT - round(ZFALL * ramp(i, fw)) - round(12 * ramp(j, fh))
    if i == 0 and j == 1:
        lum += RIVET
    return lum


def mount_west(i, j, fw, fh):
    """The +x flank. Column 0 is min z here - the *front*, the buried end - so the gradient and the
    rivet both run the other way round the box. Running this the same way as `east` lights the
    bracket from opposite ends on its two sides, and it is the one direction error this part can
    make."""
    lum = MOUNT - round(ZFALL * (1.0 - ramp(i, fw))) - round(12 * ramp(j, fh))
    if i == fw - 1 and j == 1:
        lum += RIVET
    return lum


def mount_up(i, j, fw, fh):
    """The bracket's top, 4 wide by 3 deep, and the one face of it that clears the field's hem and is
    seen from above. Row 0 is max z, the proud end; row 2 is inside the shell and painted INNER by the
    mask."""
    return UPFACE - 34 - round(20 * ramp(j, fh)) - round(10 * abs(ramp(i, fw) - 0.5) * 2)


def mount_down(i, j, fw, fh):
    """The bracket's underside - the ledge the pole is socketed into, seen from below."""
    return DOWNF + 16 - round(14 * ramp(j, fh))


def mount_north(i, j, fw, fh):
    """Entirely inside the chestplate shell; kept honest by check_mask rather than by prose."""
    return INNER


def mount_south(i, j, fw, fh):
    """The bracket's back face, which the field clears by half a unit rather than swallowing - the one
    face on this part that the mask calls exposed and the eye almost never finds, because the field
    hides it completely from behind. It exists edge-on in the gap and nowhere else, so it is painted
    below the inner face's own value, darkening downward as the bracket's ledge closes the gap under
    it."""
    return BACKF - 18 - round(10 * ramp(j, fh))


PAINTERS = {
    ("cloth", "up"): cloth_up, ("cloth", "down"): cloth_down,
    ("cloth", "east"): cloth_east, ("cloth", "north"): cloth_north,
    ("cloth", "west"): cloth_west, ("cloth", "south"): cloth_south,
    ("staff", "up"): staff_up, ("staff", "down"): staff_down,
    ("staff", "east"): staff_east, ("staff", "north"): staff_north,
    ("staff", "west"): staff_west, ("staff", "south"): staff_south,
    ("finial", "up"): finial_up, ("finial", "down"): finial_down,
    ("finial", "east"): finial_east, ("finial", "north"): finial_north,
    ("finial", "west"): finial_west, ("finial", "south"): finial_south,
    ("mount", "up"): mount_up, ("mount", "down"): mount_down,
    ("mount", "east"): mount_east, ("mount", "north"): mount_north,
    ("mount", "west"): mount_west, ("mount", "south"): mount_south,
}


def check_geometry() -> None:
    """CUBES must be the shipped geometry, in order: sizes, uv AND pivot-relative origins.

    Painting a texture for a shape the model no longer has is invisible to every other check in this
    pipeline - `bb_geo roundtrip` checks the model against itself and check_layout() checks the
    master against itself, and both keep passing while the rectangles slide off the faces they were
    drawn for. The origins are asserted as well as the sizes because this painter's burial mask and
    its whole alpha silhouette are computed from them: a cube nudged a quarter of a unit would leave
    every INNER pixel wrong and the swallowtail cut into the wrong rows, with nothing else in the mod
    noticing."""
    doc = json.loads(GEO.read_text(encoding="utf-8"))
    assert (doc["texture_width"], doc["texture_height"]) == (TEX_W, TEX_H), \
        f"{GEO.name} is {doc['texture_width']}x{doc['texture_height']}, this master is {TEX_W}x{TEX_H}"
    # The cloth lives on its own bone, `banner`, under the mount: that is the bone the banner
    # fitting takes over when a banner is applied, and the game draws the pattern layers on it in
    # place of the master. Every bone still sits at the anchor unrotated, because every burial mask
    # and the swallowtail below assume axis-aligned cubes in the one frame.
    found = []

    def walk(bone):
        assert tuple(bone.get("pivot", [0, 0, 0])) == (0, 0, 0), \
            f"{GEO.name}'s bone {bone['name']} pivot is {bone.get('pivot')}, not the anchor itself"
        assert all(r == 0 for r in bone.get("rotation", [0, 0, 0])), \
            f"{GEO.name}'s bone {bone['name']} is rotated; every burial mask here assumes axis-aligned cubes"
        found.extend((tuple(c["size"]), tuple(c["uv"]), tuple(float(v) for v in c["origin"]))
                     for c in bone.get("cubes", []))
        for child in bone.get("children", []):
            walk(child)

    for bone in doc["bones"]:
        walk(bone)
    assert any(b["name"] == "banner" for b in doc["bones"][0].get("children", [])), \
        f"{GEO.name} has no `banner` child bone for the banner fitting to draw on"
    want = [(size, uv, tuple(float(v) for v in origin)) for size, uv, origin in CUBES.values()]
    found.sort(key=lambda t: t[1])
    want.sort(key=lambda t: t[1])
    assert found == want, f"CUBES disagrees with {GEO.name}: {found} vs {want}"
    for name, cells in CUT.items():
        w, h, _ = CUBES[name][0]
        for col, row in cells:
            assert 0 <= col < w and 0 <= row < h, f"{name}'s cut cell {(col, row)} is off the cube"


def check_planes() -> None:
    """No two cubes of this part may share a plane, whichever way the two faces point.

    PLAN.md's rule, stated as an assertion because on a part built out of one flat plate and three
    things bolted to it, flush is exactly what looks tidy in the outliner - and two coplanar quads
    under `armorCutoutNoCull` are two quads fighting for one depth over whatever area they share.
    Twenty-four planes, no repeats; the eight z values of the front-to-back stack are the ones that
    go wrong first, because that is the axis every cube here is stacked along."""
    for axis, label in enumerate("xyz"):
        seen = {}
        for name in CUBES:
            lo, hi = bounds(name)
            for v in (lo[axis], hi[axis]):
                assert v not in seen, f"{name} and {seen[v]} share the plane {label} = {v:g}"
                seen[v] = name


def check_layout() -> dict:
    """Every face rectangle must sit inside the texture and no two may overlap - a silent overlap
    would paint one cube's shading onto another's face and only show up on a model in game, and a
    rectangle that runs off the sheet samples whatever the atlas has packed next door."""
    claimed = {}
    for name, (size, uv, _) in CUBES.items():
        for face, (x, y, w, h) in faces(size, uv).items():
            assert 0 <= x and x + w <= TEX_W, f"{name}.{face} runs off the texture in u"
            assert 0 <= y and y + h <= TEX_H, f"{name}.{face} runs off the texture in v"
            for py in range(y, y + h):
                for px in range(x, x + w):
                    prev = claimed.get((px, py))
                    assert prev is None, f"{name}.{face} overlaps {prev} at {(px, py)}"
                    claimed[(px, py)] = f"{name}.{face}"
    return claimed


def expected_opaque() -> set:
    """The opaque set the CUT table implies, built independently of the drawing.

    The all-opaque masters can assert `opaque == every claimed rectangle`; a punched one cannot, and
    the weaker "opaque is a subset of the rectangles" passes happily on a banner that has lost both
    of its tails. So the silhouette is derived from CUT here and the drawing is asserted against it -
    the spurs' discipline, and the only check that can see the six faces of a cut cube disagree with
    each other about where the notch is."""
    want = set()
    for name, (size, uv, _) in CUBES.items():
        for face, (x, y, fw, fh) in faces(size, uv).items():
            for j in range(fh):
                for i in range(fw):
                    if face_opaque(name, face, i, j):
                        want.add((x + i, y + j))
    return want


def check_mask() -> None:
    """The burial facts the shape was designed around, asserted rather than described.

    Each one is a geometric claim made in the docstring above, and each would break silently if a
    cube moved: the mask would still be *a* mask and the render would still be *a* render."""
    def seen(name, face):
        fw, fh = faces(CUBES[name][0], CUBES[name][1])[face][2:]
        return {(i, j) for j in range(fh) for i in range(fw)
                if face_opaque(name, face, i, j) and not buried(name, face, i, j)}

    w, h, _ = CUBES["cloth"][0]
    # The hero face. The field is the outermost cube on the part, so every one of its opaque cells is
    # seen; the day one of them is not, something has been built in front of the banner.
    assert len(seen("cloth", "south")) == w * h - len(CUT["cloth"]), \
        "the field's back face is no longer entirely exposed"
    # The pole hangs behind the cloth over its whole length, which is what a carried banner looks like
    # and what leaves the hero face clean. Its front face keeps only the row inside the bracket.
    assert seen("staff", "south") == set(), "the pole's back face is no longer inside the field"
    assert seen("staff", "north") == {(0, j) for j in range(1, 7)}, \
        "the pole's top row is no longer socketed into the bracket"
    # The pole lands on the field's middle column exactly and the spearhead stands behind the top
    # row's middle three cells - between them that is every INNER pixel of the field's inner face.
    assert STAFF_COL == w // 2, "the pole no longer lands on the field's middle column"
    inner_north = {(i, j) for j in range(h) for i in range(w)
                   if face_opaque("cloth", "north", i, j) and buried("cloth", "north", i, j)}
    assert inner_north == {(2, 0), (3, 0), (4, 0)} | {(STAFF_COL, j) for j in range(1, 7)}, \
        f"the field's inner face is buried in the wrong cells: {sorted(inner_north)}"
    # The ridge and its two gutters are painted exactly where the pole is behind the cloth; below its
    # foot the field hangs free, and two rows after that the fork opens.
    assert POLE_ROWS == set(range(8)), f"the pole no longer backs field rows 0-7: {sorted(POLE_ROWS)}"
    # Nothing stands behind the notch: the pole's foot stops half a unit above the fork's first cut
    # row. That half unit is what makes covers()' hole test inert here - lose it and the plain box
    # test starts burying rows of pole that are looked straight through.
    fork_top = bounds("cloth")[0][1] + min(row for _, row in CUT["cloth"])
    assert bounds("staff")[1][1] <= fork_top + EPS, \
        f"the pole's foot at {bounds('staff')[1][1]:g} reaches the fork at {fork_top:g}"
    # The bracket's front face is inside the chestplate shell, and its third depth index - part-local
    # z -0.25..0.75 - is the unit through the wall, on the top, the underside and both flanks.
    assert seen("mount", "north") == set(), "the mount's front face is no longer inside the shell"
    assert not any((i, 2) in seen("mount", "up") for i in range(4)), \
        "the mount's buried depth row is no longer inside the shell on `up`"
    assert not any((2, j) in seen("mount", "east") for j in range(3)), \
        "the mount's buried depth column is no longer inside the shell on `east`"
    assert not any((0, j) in seen("mount", "west") for j in range(3)), \
        "the mount's buried depth column is no longer inside the shell on `west`"
    # Its back face, by contrast, is *not* buried: the field stands half a unit behind it rather
    # than over it. Painted, not INNER - and if that ever changes, mount_south stops being drawn.
    assert len(seen("mount", "south")) == 12, \
        "the mount's back face is buried again - the field has moved back onto it"
    # Both of the field's one-pixel edges survive whole - they are the profile silhouette - and so
    # does the top hem, because the spearhead behind it is a quarter unit short of its depth.
    assert len(seen("cloth", "west")) == h and len(seen("cloth", "east")) == h, \
        "the field's side edges are no longer entirely exposed"
    assert len(seen("cloth", "up")) == w, "the field's top hem is no longer entirely exposed"


def main() -> None:
    check_geometry()
    check_planes()
    claimed = check_layout()
    check_mask()

    img = Image.new("LA", (TEX_W, TEX_H), (0, 0))
    counts = {}
    for name in CUBES:
        for face in FACE_ORDER:
            counts[f"{name}.{face}"] = paint_face(img, name, face, PAINTERS[(name, face)])

    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    want = expected_opaque()
    assert opaque == want, (f"the drawn silhouette is not the one CUT describes: "
                            f"{sorted(opaque - want)[:6]} extra, {sorted(want - opaque)[:6]} missing")
    assert opaque <= set(claimed), "a pixel was drawn outside every claimed face rectangle"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)

    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    visible = sum(counts.values())
    low = sum(1 for v in lums if v < 128)
    print(f"wrote {OUT} ({len(opaque)} opaque px of {len(claimed)} claimed, "
          f"values {min(lums)}-{max(lums)}, {low} under 127)")
    print(f"  {visible} px survive the burial mask, {len(opaque) - visible} are INNER")
    for key in sorted(counts):
        print(f"    {key:14s} {counts[key]:3d} seen")


if __name__ == "__main__":
    main()
