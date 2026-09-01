"""
Paint the grayscale master for the "gorget" part.

Like the brooch, sash, tassets, spurs, greaves, brush_crest, vambraces and banner painters this does
not merely claim that CUBES matches the shipped geometry, it reads
assets/armorpieces/armorpieces/decoration/gorget.json at run time and asserts it - sizes, uv AND
pivot-relative origins, because on this part the positions are not decoration: every INNER pixel
below is decided by testing a face pixel against the other four cubes and against the chestplate
shell, and this part is a collar lapped over a bib with a bar laid across it and a cap butted onto
each end, so a cube nudged a quarter of a unit would leave the whole burial mask silently wrong
while every other check in the pipeline kept passing. Output goes to
tools/decoration_masters/gorget.png, which sync_decoration_masters.py installs for the game to
colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

**This master is 100% opaque, and there is no static layer.** A gorget is a solid plate of steel: it
has no fringe to fray, and parts draw with `armorCutoutNoCull`, so a hole punched in a plate three
units deep shows the *inside* of the plate rather than the chest behind it - the circlet's case, not
the feathering's. The banner's swallowtail could afford its cut only because its field is exactly one
unit deep and the two big faces line up through the hole. Exactly one cube here is one unit deep -
the boss - and its front face is three pixels by one, which is not a place to put a hole. The shaped
outline this part wanted is therefore cut in *geometry* - four courses of 4, 13, 9 and 5 units of
width - and not in alpha. No static layer for the same reason the wing roots have none: this is
hardware.

--------------------------------------------------------------------------------------------------
The part, in numbers

`COLLAR` is `Attachment.of(BODY, 0, 1, -2)` and is not mirrored, so part-local (0, 0, 0) is
body-local (0, 1, -2) - the base of the throat, on the torso's own front face, one unit below the
neck. Two frames are quoted throughout: *part-local* (what the geometry JSON holds) and *geo*
(part-local + (0, 1, -2)), which is what trace_geometry.py prints and what every number in PLAN.md
is in. The torso box is geo x -4..4, y 0..12, z -2..2; the chestplate's 1.0-inflate shell, the only
one guaranteed present when this part draws, is x -5..5, y -1..13, z -3..3, and the same chestplate's
1.0-inflate arm sleeves are x +-(3..9), y -1..13, z -3..3.

    cube        part-local                                   geo
    bib         x -2.50..2.50  y  1.50..3.50  z -1.25..1.75   x -2.50..2.50  y  2.50..4.50  z -3.25..-0.25
    collar      x -4.50..4.50  y -0.25..1.75  z -1.50..1.50   x -4.50..4.50  y  0.75..2.75  z -3.50..-0.50
    boss        x -1.50..1.50  y  1.50..2.50  z -1.75..-0.75  x -1.50..1.50  y  2.50..3.50  z -3.75..-2.75
    shoulder_r  x -6.50..-4.50 y -2.25..0.75  z -1.25..2.75   x -6.50..-4.50 y -1.25..1.75  z -3.25..0.75
    shoulder_l  x  4.50..6.50  y -2.25..0.75  z -1.25..2.75   x  4.50..6.50  y -1.25..1.75  z -3.25..0.75

Five cubes, one bone, no rotations - the fourth part in the mod with none, after the greaves, the
vambraces and the banner, and for a reason none of those had: every burial mask below is a box
containment test, and a canted plate would make all of them approximations.

**The silhouette is a yoke, and the yoke is the whole argument against the brooch.** Read down the
front: 4 units of width from y -1.25 to 0.75, which is the two shoulder caps standing alone above the
shoulder line; 13 from 0.75 to 1.75, where the collar reaches x = +-4.50 and the caps carry on from
exactly there, so the three cubes read as one unbroken band the full width of the figure; 9 from 1.75
to 2.75 (the collar alone, with the bib's top quarter unit lapped away behind it); and 5 from 2.75
to 4.50 (the bib, with the boss laid across its upper half). That is 38.75 square units of frontal
silhouette against the brooch's 5.44 for band plus head plus tongue, and 13 units of width against
the brooch's 3 - a plate that armours an area, which is what a gorget is and what a clasp is not.

**Almost nothing is spent on projection, and what little there is, is spent low and central.** The
collar stands 0.50 units proud of the chestplate surface at z = -3, the bib 0.25, and the boss 0.75;
the caps stand 0.25 in front of the sleeve's own front wall and 0.25 above its top at y = -1. Nothing
on this part is more than three quarters of a unit off the armor it is bolted to. That is the
opposite of the spending pattern the brooch chose - a 2x1x2 head 1.75 proud, because a clasp is a
point and a point has to project to be seen - and it is deliberate: this part is seen because it is
wide.

--------------------------------------------------------------------------------------------------
The head pitch, which is the constraint this part was once rejected on, and is now rejected on again

PLAN.md records `gorget` being passed over for `brooch` because "both sit in crowded space near the
neck, and the lower-profile reading is the one that clips least", and the number behind that is the
helmet's: its bottom-front edge sweeps a radius of 5.099 about the head pivot at geo (0, 0, 0), and
its 1.0-inflate box is x -5..5, y -9..1, z -5..5. Every angle below is full box containment against
that box rotated about X, all six planes, over every corner of every cube - not the `y cos t +
z sin t > 1` bottom-plane inequality, which ignores the front wall the deep corners actually leave
through.

**Three of the five cubes are inside the resting helmet at 0 degrees, and that is the headline fact
about this shape.** The collar's top edge is geo y = 0.75, a quarter unit above the helmet's bottom
plane at y = 1, so a 9 x 0.25 x 3 slab of it shares the helmet's volume before the head moves at all;
each cap contributes a 0.5 x 2.25 x 4 sliver, the part of it inboard of x = +-5. Only the two cubes
that hang clear below the throat have an angle at all: the **bib at 23.45 deg**, on its top-front
corner (+-2.50, 2.50, -3.25), and the **boss at 20.87 deg**, on its own top-front corner
(+-1.50, 2.50, -3.75) - half a unit further forward and 2.58 deg dearer for it, which is 5.2 deg per
unit stood proud against PLAN's rule of thumb of about 4, and the rule of thumb is the optimistic
one this close in.

For scale, PLAN.md's own: the chestplate's top-front corner (y -1, z -3) is inside the helmet box at
**0 deg** too, so the company this part keeps at rest is the armor it is bolted to rather than
anything wrong in kind. But the comparison that decided the socket has now inverted. The brooch, at
the size it was cut down to, is 3 wide and 1 tall and sits over the breast at geo y 4.50..5.50: its
first corner into the helmet is the band's inboard-top-back at (0.50, 4.50, -1.00), at **64.94 deg**.
The old reading of this file - that the gorget survived to 22.10 against the brooch's 19.77 and was
therefore the better-behaved of the two - was true of a gorget whose top course started at geo
y = 2.50. This one starts 1.75 units higher, which puts it a quarter unit through the helmet's own
bottom plane, and that quarter unit is the whole of the margin.

--------------------------------------------------------------------------------------------------
The arms, and what the caps cost

The 1.0-inflate arm sleeve's inboard wall is geo x = 3, and the two caps live entirely outboard of
it, at |x| 4.50..6.50 - so unlike the banner (|x| <= 2.50, never touched) this part now has whole
cubes over the sleeve, and `trace_geometry.py` cannot see across bones. Checked by hand instead, by
sweeping each sleeve box about its arm pivot at geo (+-5, 2, 0):

  * **At rest 85.9% of each cap's volume is inside its sleeve.** The cap is 2 x 3 x 4 = 24 cubic
    units; the sleeve contains all but the 0.25 that stands above y = -1 and the 0.25 that stands in
    front of z = -3, which is 3.375 of it. The whole read of the cap at rest is a quarter-unit lip.
    Everything behind that lip uncovers on the first step the wearer takes, because the sleeve rides
    LEFT_ARM/RIGHT_ARM and this part rides BODY.
  * That is why the sleeve is deliberately **not** an occluder in the burial mask below. A pixel
    painted INNER because an arm was in front of it would be a black patch swinging in and out of
    view, which is the tassets' finding stated the other way round. So the caps are painted whole,
    45 visible pixels each, and 90 of this master's 157 visible pixels are cap.
  * The collar's own outboard-bottom-front corner (+-4.50, 2.75, -3.50) is the first thing on the
    part that a *swing* carries the sleeve into, at **20.96 deg**. The brooch's band, which reaches
    x = 3.50 on the wearer's left only, is reached at **14.45 deg** on its outboard-bottom-front
    corner (3.50, 5.50, -4.00) - the one corner of it the re-cut did not move, since the band lost
    its inboard half and its upper two units but kept its bottom and its front. So on the swing the
    collar is still the better-behaved of the two, and the thing doing the reaching is a six-unit
    opaque limb, which is *occlusion*: the sash's knot argument, "the swinging arm does pass through
    the knot, but that is occlusion by a large opaque box, not a thin decoration emerging from inside
    a limb".

**The spaulders are no longer clear, and this is the one clearance on the part that arithmetic
cannot argue away.** Their cap is geo x 5.75..9.75, y -1.50..-0.50, z -3.50..3.50, and it rides the
arm bone - but every rotation on this body is about X, which preserves x, so the 0.75 units of x this
part now shares with it are shared at *every* arm angle. At rest the two boxes interpenetrate over
0.75 x 0.75 x 4.00. `PAULDRONS` and `COLLAR` are different sockets on the same armor piece, so the
two can be worn together, and `trace_geometry.py` reports nothing because they ride different bones.
The old width of 9 was fixed by exactly this: 10 would have put the plate's side faces on the
chestplate shell's own wall at x = +-5, and 11 would have been inside the spaulder. The collar is
still 9. The caps are what reach past it.

**The two note lines the trace prints are the leggings' torso shell at x = +-4.5**, which the
collar's side faces and both caps' inboard faces land on exactly - three cubes, two planes. That
surface is 0.5 inside the chestplate's own at x = +-5 and this part only ever draws with a chestplate
on, so the shared plane is behind an opaque wall wherever the leggings shell actually is (z -2.5..2.5,
inside the chestplate's z -3..3). It is a `note:` and not a `COPLANAR:` for that reason, and there
are no COPLANAR lines.

--------------------------------------------------------------------------------------------------
The bone-mates

`brooch` shares this socket and can never be worn with it. The four that can are all clear, but the
order has changed and the margin has thinned:

  * **`wing_roots`** is now the near one, at **0.57**. Its rotated socket_l reaches forward to
    geo z = 0.32 and the bib's back face is at z = -0.25. Half a unit is the floor this pipeline
    holds parts to and this clears it by seven hundredths - close enough that any later session
    pushing the bib backwards is spending that gap, not finding one.
  * **`sash`** used to be the near one and is now the far one. Its highest points are the buckle and
    the knot at geo y = 7.50; this part's lowest point is the bib's underside at y = 4.50. Three
    whole units, because the whole part moved up the chest.
  * **`banner`** clears by 2.00 and **`pinions`** by 2.25, both in z, on the opposite side of the
    torso, and both of those gaps are measured off the bib's back face at z = -0.25 rather than off
    the caps, which reach further back to z = 0.75 but are a unit outboard of anything either of
    those two hangs.

--------------------------------------------------------------------------------------------------
Burial is computed, not eyeballed

The vambraces' method: sample each face over its whole pixel footprint, push 0.05 along the face
normal, and test containment against the boxes that could hide it - the chestplate shell and the
part's own other cubes. A pixel is painted INNER only when *all* of it is covered; partly-covered
pixels are painted as visible, which is the safe direction, since a visible pixel painted dark is a
mistake you can see and a buried pixel painted bright is not.

`covers()` is the banner's hole-aware version rather than the vambraces' plain box test, and it is
kept even though CUT is empty on this part: the two are identical while there are no holes, and the
one that survives a later session adding one is the one that asks. `expected_opaque()` is built the
same way, from the same table, so the day a cut is added the drawing is asserted against it.

Everything the mask finds is permanent. The chestplate's *torso* shell rides BODY exactly as this
part does, so unlike the tassets - which had to paint a row as flank because their shell rides a
different bone - there is no row here that uncovers on a stride. The arm sleeve is the shell that
does uncover, and it is excluded for that reason; see the section above, where excluding it is what
leaves 90 of 157 visible pixels on two cubes that a standing figure mostly hides.

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

`COLLAR` is a single, non-mirrored attachment, so - the wing roots' note - `west` is the +x face of
the one and only copy and there is no `scale(-1, 1, 1)` to make one master serve two sides. Symmetry
about x = 0 is therefore something this file has to paint, twice, and it has to paint it in two
different ways:

  * The bib, the collar and the boss are each centred on x = 0, so each is its own mirror. Their two
    flanks must read identically in 3D, which is *not* the same as painting the two rectangles
    identically, because `west` counts z front to back and `east` counts it back to front. One
    function per course, and `east` reads it reversed.
  * The two caps are a mirror *pair* of separate cubes with separate UV, and there every face has a
    partner: `up`, `down`, `north` and `south` swap the meaning of column 0 between inboard and
    outboard, so shoulder_r reads shoulder_l's function with the column index reversed; and the
    outboard flank is shoulder_l's `west` but shoulder_r's `east`, so those two are written once
    with column 0 at the front and one of them reads it reversed. The inboard pair is the other way
    round again.

Running any of those the same way round puts the front-edge highlight on the front of one shoulder
and the back of the other, and check_mask asserts every one of the pairings rather than trusting it.

Which faces are seen, since the wing roots' warning is that these constants never transfer between
parts by name:

  * `north` is the hero - the collar's 9x2 whole, the bib's 5x2 less the three the boss takes, the
    boss's own 3x1 and 2x3 on each cap - and the chest is a front-on object in a way a shoulder or a
    heel is not.
  * `up` is second, and it is 28 pixels: the collar's front strip the full 9 wide, the boss's 3, and
    both caps whole, 2x4 each, because the caps stand outboard of the torso shell and nothing on this
    part is above them. The bib's top is the exception that proves the mask works - it is *entirely*
    buried, under the collar for its front row and inside the shell for the other two, which is the
    same lapped joint the bib's front row reads as a shadow.
  * `west`/`east` are the profile, 44 pixels of it, and on this part the profile is two big outboard
    cap flanks - 4x3 apiece and fully lit - against five pixels of inboard cap flank each and ten of
    centred plate edge in total.
  * `down` is 33 pixels the same way up is: the collar's front strip, the bib's, the boss's, and both
    caps whole, seen from below and from any low camera.
  * `south` is seen only on the caps, 2x3 each. On the three centred cubes every back face is inside
    the chestplate shell and all 31 pixels of it are INNER - which is what "the projection is all
    spent forwards" means, and it is the one claim that covers a ninth of the master.

The circlet's lesson applies as it does everywhere: the material ramp interpolates dark -> mid
over master values 0..127 and mid -> light over 128..255, so a master that never dips below the
middle confines the whole part to the light half of every material's ramp. Values run 37..249 over
the whole master and 61..249 over the 157 pixels the burial mask leaves visible, 51 of which - just
under a third - sit below the ramp's midpoint. That dark content is real form rather than padding,
and most of it is new: the caps alone contribute 16 pixels of free underside and 12 of back face,
and a cap seen from behind or below that is not plainly darker than its own top would flatten the
one piece of this shape with real depth to it. The rest is the boss's cast shadow on the bib, the
lap row where the bib disappears behind the collar, and the three undersides. On netherite, the
material PLAN.md flags as the one that mushes, the visible pixels span 41..90 against the
spaulders' recut 31..58.
"""

from __future__ import annotations

import itertools
import json
import math
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "gorget.json"
OUT = ROOT / "tools" / "decoration_masters" / "gorget.png"

TEX_W, TEX_H = 64, 32

# size (w, h, d), uv (u, v) and pivot-relative origin, mirroring gorget.json in that file's own
# order. The single bone sits at the anchor with no rotation, so origin IS the part-local corner.
#   bib        - the breast plate: the lowest and narrowest course, 0.25 proud of the chestplate
#                surface, its top quarter unit lapped under the collar and its underside the part's
#                lowest point.
#   collar     - the throat plate: the widest centred course, 0.50 proud, spilling 0.50 either side
#                of the torso box and handing off to the caps at exactly x = +-4.50.
#   boss       - the bar laid across the bib's upper half, 3 x 1 x 1 and 0.75 proud - the only cube
#                on the part one unit deep, and the only one whose front face is a single row.
#   shoulder_r - the right shoulder cap, outboard of the torso shell entirely.
#   shoulder_l - the left one. The pair is a mirror about x = 0 and every painter below says which
#                of its two columns is the inboard one.
CUBES = {
    "bib":        ((5, 2, 3), (0, 0),  (-2.5, 1.5, -1.25)),
    "collar":     ((9, 2, 3), (16, 0), (-4.5, -0.25, -1.5)),
    "boss":       ((3, 1, 1), (40, 0), (-1.5, 1.5, -1.75)),
    "shoulder_r": ((2, 3, 4), (48, 0), (-6.5, -2.25, -1.25)),
    "shoulder_l": ((2, 3, 4), (0, 7),  (4.5, -2.25, -1.25)),
}

# The two caps, right first, as the mirror pairing every shoulder painter and every mirror assertion
# below is written against.
CAPS = ("shoulder_r", "shoulder_l")

# Cells removed from a cube's x-y grid, columns from min x and rows from min y. Empty: see the module
# docstring - a through-cut needs a cube one unit deep, and the only cube here that is one unit deep
# is three pixels wide. Kept as a table rather than deleted so that the hole-aware occlusion and
# expected_opaque() below are what a later session inherits, instead of a box test that would
# silently bury whatever it cut.
CUT: "dict[str, set[tuple[int, int]]]" = {}

# The chestplate's 1.0-inflate torso shell in part-local coordinates (geo x -5..5, y -1..13, z -3..3
# shifted by the anchor at (0, 1, -2)). It is the only shell guaranteed present when this part draws,
# it rides the same bone, and so anything inside it is buried permanently. The arm sleeves are
# deliberately absent: they ride LEFT_ARM/RIGHT_ARM and uncover on every stride, and on this shape
# that omission is worth 90 pixels.
SHELL = ((-5.0, -2.0, -1.0), (5.0, 12.0, 5.0))

PUSH = 0.05      # how far off a face a sample sits before it is tested for containment
EPS = 1e-9

random.seed(29)  # deterministic output - regenerating must not churn the PNG

UPFACE = 242    # a free top ledge: the collar's step, the boss's crown, the caps' tops
BOSSF = 248     # the boss's own front face - the brightest thing on the part
FRONT = 200     # `north`, geo -z: the hero face's field
FLANK = 168     # `west`/`east`: the profile
BIBF = 156      # the bib's front, which sits 0.25 BEHIND the collar's and is lit for it
BACKF = 148     # `south` on the two caps - the only back faces this part ever shows
GUTTER = 112    # the boss's cast shadow on the bib's lower row
DOWNF = 72      # a free underside
INNER = 40      # buried - in the chestplate shell, or under another cube of this part

CHAMFER = 26    # the lit top row of a course's front face, where it leaves the course above
FALL = 20       # top-to-bottom falloff down a standing face
ZFALL = 24      # front-to-back falloff across a face's depth
XFALL = 16      # centre-to-edge falloff across a plate's width
LAP = 62        # the shadow row where a course disappears behind the course in front of it
LIP = 22        # the free lower edge of the breast plate, catching light off its own turned edge
ENDDROP = 44    # the collar's two end blocks, dropped so that a one-pixel bolt can read
RIVET = 80      # the bolt itself: +80 against the dropped block, not +30 against the field
SCORE = 74      # the scored line inboard of each end block
CAPDROP = 12    # the caps' outboard half, dropped so the pair reads as turning away from the chest


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

    A through-cut removes a cell from every face that touches it, so this is the single mapping an
    alpha silhouette would be built from: `up` follows the top row, `down` the bottom row, `east` the
    first column and `west` the last, and the two big faces are the grid itself read in opposite
    directions."""
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


def inside(box, clo, chi) -> bool:
    """Is the whole of this sample inside that (lo, hi) box?"""
    return all(box[0][a] - EPS <= clo[a] and chi[a] <= box[1][a] + EPS for a in range(3))


def covers(other, clo, chi) -> bool:
    """Does cube `other` hide this sample - box containment AND no hole over it?

    The banner's test rather than the vambraces' plain one: a box with a cut in it is not an occluder
    over that cut. CUT is empty here, so the second half is a no-op today and a guard rail tomorrow.
    """
    blo, bhi = bounds(other)
    if not inside((blo, bhi), clo, chi):
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
    if inside(SHELL, clo, chi):
        return True
    return any(covers(other, clo, chi) for other in CUBES if other != name)


def put(img, x: int, y: int, lum: int, alpha: int = 255) -> None:
    if 0 <= x < TEX_W and 0 <= y < TEX_H:
        img.putpixel((x, y), (max(0, min(255, lum)), alpha))


def ramp(i: int, n: int) -> float:
    """Position along a face axis, 0.0 at column/row 0 and 1.0 at the far end."""
    return 0.0 if n <= 1 else i / (n - 1)


def hump(i: int, n: int) -> float:
    """1.0 at the middle of an axis, 0.0 at both ends - a plate's crown across its width."""
    return 1.0 - abs(ramp(i, n) - 0.5) * 2


def flip(value):
    """The same painter read with its columns reversed.

    Three different mirrorings on this part come out as this one operation: a centred cube's `east`
    against its own `west`, a cap's `up`/`down`/`north`/`south` against its partner's, and the
    outboard and inboard flanks of the pair. In every case the two rectangles hold the same surface
    counted the opposite way round, and running them the same way is the one direction error this
    shape can make."""
    def mirrored(i, j, fw, fh):
        return value(fw - 1 - i, j, fw, fh)
    return mirrored


def paint_face(img, name, face, value) -> int:
    """Fill one face rectangle: nothing where a cut removed the cell, INNER where the burial test
    says the pixel cannot be seen, the painter's value otherwise.

    Returns the number of pixels that survived as visible, which main() reports - a face whose count
    goes to zero after a geometry edit is the loudest warning this file can give without failing."""
    x0, y0, fw, fh = faces(CUBES[name][0], CUBES[name][1])[face]
    seen_here = 0
    for j in range(fh):
        for i in range(fw):
            if not face_opaque(name, face, i, j):
                continue
            if buried(name, face, i, j):
                lum = INNER
            else:
                lum = value(i, j, fw, fh)
                seen_here += 1
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))
    return seen_here


# ------------------------------------------------------------------------------------------------
# the centred flanks - one function per course, read forwards by `west` and backwards by `east`
#
# The three centred courses each step forward as they descend - collar 0.50 proud, bib 0.25, boss
# 0.75 - so the profile is a shallow stagger, and the only thing that says so is a front-to-back
# falloff running the same way round the body on both sides.


def flank(base):
    def west(i, j, fw, fh):
        return base - round(ZFALL * ramp(i, fw)) - round(FALL * ramp(j, fh))

    return west, flip(west)


bib_west, bib_east = flank(FLANK - 20)          # the shallowest course, so the dimmest edge
collar_west, collar_east = flank(FLANK + 14)    # the widest step, and the one profile sees first
boss_west, boss_east = flank(FLANK + 30)        # a bar standing off a plate catches the most


# ------------------------------------------------------------------------------------------------
# the collar - the throat plate, and the hero face of the part


def collar_north(i, j, fw, fh):
    """9 x 2, column 0 at min x, and the whole rectangle is seen: nothing on this part stands in
    front of the collar, and nothing above it reaches down over it.

    The two end columns are where the shoulder caps butt on - the cap's inboard wall is x = +-4.50,
    which is exactly this face's outer edge - so they carry the part's only bolts. The brooch's
    lesson is the whole of that treatment: a one-pixel bolt only reads if what surrounds it is
    plainly darker, so the end block is dropped 44 below the field AND loses its chamfer, and the
    bolt goes in at +80 rather than at +30 against a field it would otherwise nearly match. Inboard
    of it a scored line at -74 separates the end block from the plate - at -50 it merged with the
    chamfer on the row above, which is the same failure the brooch's groove had at -70."""
    if i in (0, fw - 1):
        return FRONT - ENDDROP + (RIVET if j == 1 else 0)
    if i in (1, fw - 2):
        return FRONT - SCORE
    lum = FRONT - round(XFALL * (1.0 - hump(i, fw)))
    return lum + CHAMFER if j == 0 else lum - FALL


def collar_up(i, j, fw, fh):
    """The throat ledge, 9 wide x 3 deep, rows back to front. Only row 2 - the half unit that clears
    the chestplate surface at z = -3, plus the pixel's own rounding - survives the mask, and it is
    the highest lit run on the centre of the part. Rows 0 and 1 are inside the shell."""
    return UPFACE - round(12 * (1.0 - hump(i, fw)))


def collar_down(i, j, fw, fh):
    """The collar's front underside, 9 wide, the strip that overhangs the bib by a quarter unit.
    It is the lit edge of the lap the bib's own top row reads as a shadow, so it is painted brighter
    than a free underside would be: the two faces are one joint seen from two sides."""
    return DOWNF + 24 - round(12 * (1.0 - hump(i, fw)))


def collar_south(i, j, fw, fh):
    return INNER


# ------------------------------------------------------------------------------------------------
# the bib - the breast plate


def bib_north(i, j, fw, fh):
    """5 x 2, column 0 at min x. The boss covers the middle three columns of row 0 exactly - it is
    3 wide on a 5-wide host, and 5 and 3 are both odd, which is the greaves' "an odd rib wants an odd
    host" holding one course lower than it used to.

    What is left is four corners and a shadow band, and each of the three is a different fact:

      * Row 0's two surviving columns are under the collar's overhang, which stands a quarter unit
        proud of this face - so they take the lap shadow, and that shadow is the only thing that
        makes the bib read as a course *behind* the collar rather than flush with it. Vanilla shades
        the two faces identically, so the step exists only here.
      * Row 1's middle three columns are directly under the boss, whose underside is at geo y = 3.50
        and whose front face is three quarters of a unit further out - the darkest run on the hero
        face, and the centre column darkest of all.
      * Row 1's two end columns are the part's free lower edge, so they get a turned-edge highlight
        instead of the falloff a free lower row would otherwise take."""
    lum = BIBF - round(XFALL * (1.0 - hump(i, fw)))
    if j == 0:
        return lum - LAP
    if i in (0, fw - 1):
        return lum + LIP
    return GUTTER - (8 if i == fw // 2 else 0)


def bib_up(i, j, fw, fh):
    """Entirely buried, and the mask is what says so rather than this comment: the front row is under
    the collar and the other two are inside the shell. Asserted in check_mask()."""
    return INNER


def bib_down(i, j, fw, fh):
    """The part's own underside and its lowest geometry, three units above the sash. Rows count back
    to front, so rows 0 and 1 are inside the shell and only row 2 hangs free."""
    return DOWNF + round(18 * ramp(j, fh)) - (8 if i in (0, fw - 1) else 0)


def bib_south(i, j, fw, fh):
    return INNER


# ------------------------------------------------------------------------------------------------
# the boss - the bar across the breast plate


def boss_north(i, j, fw, fh):
    """Three pixels by one, and the brightest run on the part. It is lit identically to the plate
    behind it by the engine - vanilla's diffuse term shades by normal alone - so the whole separation
    is this value against the shadow band at 112 directly below it, which is the greaves' finding
    stated from the other end: model the relief for the profile, paint it for the front.

    The two end pixels drop 14 so that three pixels read as a bar with ends rather than as a bright
    slot."""
    return BOSSF - (14 if i in (0, fw - 1) else 0)


def boss_up(i, j, fw, fh):
    """The bar's crown, 3 x 1. One unit deep, so there is exactly one depth row and it is free: the
    boss stands three quarters of a unit in front of the chestplate surface and a quarter in front of
    the collar's, with nothing above it."""
    return UPFACE - round(10 * (1.0 - hump(i, fw)))


def boss_down(i, j, fw, fh):
    """The bar's underside, half a unit proud of the bib. It is the lit half of the same joint the
    bib's shadow band is the dark half of."""
    return DOWNF + 26 - (6 if i in (0, fw - 1) else 0)


def boss_south(i, j, fw, fh):
    return INNER


# ------------------------------------------------------------------------------------------------
# the shoulder caps - one set of functions, and shoulder_r reads every one of them reversed
#
# Written for shoulder_l throughout, whose min x is the inboard side. On shoulder_r min x is the
# outboard side, so every one of these is wrapped in flip() below; see the module docstring for why
# that is four separate pairings and not one.


def cap_up(i, j, fw, fh):
    """The cap's top, 2 wide x 4 deep, column 0 inboard, rows back to front. All eight pixels are
    free: the caps are outboard of the torso shell in x and there is nothing of this part above them.

    The front rows are the quarter unit that clears the sleeve at rest, so they are the brightest,
    and the outboard column drops so the pair reads as turning down over the shoulder."""
    return (UPFACE - 10
            - round(ZFALL * (1.0 - ramp(j, fh)))
            - round(CAPDROP * ramp(i, fw)))


def cap_down(i, j, fw, fh):
    """The cap's underside, 2 x 4, seen from any low camera and never from a standing one. Same axes
    as cap_up, and the same front lift, because it is the same leading edge from below."""
    return (DOWNF + round(20 * ramp(j, fh)) - round(8 * ramp(i, fw)))


def cap_north(i, j, fw, fh):
    """The cap's front, 2 wide x 3 tall, column 0 inboard, row 0 at the top. This is the face that
    continues the collar's own front across the shoulder line, so it is painted from the same field
    value, dropped 12 for standing a quarter unit further back, and it takes the collar's chamfer on
    its top row and the same falloff below it."""
    lum = FRONT - 12 - round(10 * ramp(i, fw))
    return lum + CHAMFER - round((CHAMFER + FALL) * ramp(j, fh))


def cap_south(i, j, fw, fh):
    """The cap's back, 2 x 3, column 0 OUTBOARD - `south` counts x the other way - and row 0 at the
    top. The only back faces on the part that are ever seen, and they are seen from directly behind,
    where the banner and the wing roots are the neighbours. Painted a full 40 below the front field,
    since vanilla shades +z and -z identically and nothing but this value says which way the cap
    faces."""
    return BACKF - round(FALL * ramp(j, fh)) - round(12 * ramp(i, fw))


def cap_out(i, j, fw, fh):
    """The outboard flank, 4 deep x 3 tall, column 0 at the front, row 0 at the top - shoulder_l's
    `west` and shoulder_r's `east`. Twelve pixels apiece and every one of them free: this is the
    largest unbroken lit face on the master and the one a side-on camera reads the part by."""
    return FLANK + 18 - round(ZFALL * ramp(i, fw)) - round(FALL * ramp(j, fh))


def cap_in(i, j, fw, fh):
    """The inboard flank, same axes - shoulder_l's `east` and shoulder_r's `west`. Only the top row
    and the front pixel of the row below it survive: everything else is inside the collar or inside
    the torso shell. Painted 30 below the outboard flank because what is left of it faces the neck
    and is lit by nothing."""
    return FLANK - 30 - round(ZFALL * ramp(i, fw)) - round(FALL * ramp(j, fh))


PAINTERS = {
    ("bib", "up"): bib_up, ("bib", "down"): bib_down, ("bib", "north"): bib_north,
    ("bib", "south"): bib_south, ("bib", "west"): bib_west, ("bib", "east"): bib_east,
    ("collar", "up"): collar_up, ("collar", "down"): collar_down,
    ("collar", "north"): collar_north, ("collar", "south"): collar_south,
    ("collar", "west"): collar_west, ("collar", "east"): collar_east,
    ("boss", "up"): boss_up, ("boss", "down"): boss_down, ("boss", "north"): boss_north,
    ("boss", "south"): boss_south, ("boss", "west"): boss_west, ("boss", "east"): boss_east,
    # shoulder_l is the one the cap painters are written for; shoulder_r reads each of them with its
    # columns reversed, which is what makes the pair a mirror in 3D rather than in the atlas.
    ("shoulder_l", "up"): cap_up, ("shoulder_l", "down"): cap_down,
    ("shoulder_l", "north"): cap_north, ("shoulder_l", "south"): cap_south,
    ("shoulder_l", "west"): cap_out, ("shoulder_l", "east"): flip(cap_in),
    ("shoulder_r", "up"): flip(cap_up), ("shoulder_r", "down"): flip(cap_down),
    ("shoulder_r", "north"): flip(cap_north), ("shoulder_r", "south"): flip(cap_south),
    ("shoulder_r", "east"): flip(cap_out), ("shoulder_r", "west"): cap_in,
}

# The face of shoulder_l that each face of shoulder_r mirrors. `up`, `down`, `north` and `south` pair
# with themselves because both cubes count the same axis; the flanks cross over, because the +x face
# of the left cap and the -x face of the right cap are the same outboard surface.
CAP_MIRROR = {"up": "up", "down": "down", "north": "north", "south": "south",
              "east": "west", "west": "east"}


def check_geometry() -> None:
    """CUBES must be the shipped geometry, in order: sizes, uv AND pivot-relative origins.

    Painting a texture for a shape the model no longer has is invisible to every other check in this
    pipeline - `bb_geo roundtrip` checks the model against itself and check_layout() checks the
    master against itself, and both keep passing while the rectangles slide off the faces they were
    drawn for. The origins are asserted as well as the sizes because this painter's burial mask is
    computed from them, and on a collar lapped a quarter unit over a bib a cube nudged an eighth of a
    unit would leave every INNER pixel wrong with nothing else noticing."""
    doc = json.loads(GEO.read_text(encoding="utf-8"))
    assert (doc["texture_width"], doc["texture_height"]) == (TEX_W, TEX_H), \
        f"{GEO.name} is {doc['texture_width']}x{doc['texture_height']}, this master is {TEX_W}x{TEX_H}"
    assert len(doc["bones"]) == 1, f"{GEO.name} has {len(doc['bones'])} bones; this master assumes 1"
    bone = doc["bones"][0]
    assert not bone.get("children"), f"{GEO.name}'s bone has children; this master assumes it does not"
    assert tuple(bone.get("pivot", [0, 0, 0])) == (0, 0, 0), \
        f"{GEO.name}'s bone pivot is {bone.get('pivot')}, not the anchor itself"
    assert all(r == 0 for r in bone.get("rotation", [0, 0, 0])), \
        f"{GEO.name}'s bone is rotated; every burial mask here assumes axis-aligned cubes"
    found = [(tuple(c["size"]), tuple(c["uv"]), tuple(float(v) for v in c["origin"]))
             for c in bone["cubes"]]
    want = [(size, uv, tuple(float(v) for v in origin)) for size, uv, origin in CUBES.values()]
    assert found == want, f"CUBES disagrees with {GEO.name}: {found} vs {want}"
    for name, cells in CUT.items():
        w, h, _ = CUBES[name][0]
        for col, row in cells:
            assert 0 <= col < w and 0 <= row < h, f"{name}'s cut cell {(col, row)} is off the cube"


def check_symmetry() -> None:
    """The part is symmetric about x = 0, and the two caps are each other's reflection.

    Stated as arithmetic because every mirrored painter below depends on it: if shoulder_r stopped
    being shoulder_l reflected, flip() would still run and would still produce a plausible-looking
    master with the two shoulders lit from opposite ends."""
    for name in ("bib", "collar", "boss"):
        lo, hi = bounds(name)
        assert abs(lo[0] + hi[0]) < EPS, f"{name} is not centred on x = 0"
    (rlo, rhi), (llo, lhi) = bounds(CAPS[0]), bounds(CAPS[1])
    assert abs(rlo[0] + lhi[0]) < EPS and abs(rhi[0] + llo[0]) < EPS, \
        "the two shoulder caps are not reflections of each other in x"
    assert rlo[1:] == llo[1:] and rhi[1:] == lhi[1:], \
        "the two shoulder caps do not share their y and z extents"


def check_planes() -> None:
    """No face of the part may lie on the chestplate shell it draws against, and no two cubes of the
    part may put *visible* coincident faces in one plane.

    PLAN.md's rule, stated as an assertion rather than as a hope. The second half of it is what
    trace_geometry.py reports as COPLANAR, which this part has none of. The first half needs the
    finer form, because this shape is deliberately butt-jointed in three places and a flat "no two
    cubes share a plane" would reject all three:

      * two cubes on OPPOSITE sides of a shared plane are a butt joint - the collar's ends against
        the caps' inboard walls at x = +-4.50 - and their coincident faces are interior to the union
        of the two solids, so nothing can ever see them fight;
      * two cubes on the SAME side, which here is the bib and the boss sharing their tops at
        y = 1.50, put two like-facing quads in one plane, and that only survives if something else
        buries the patch. It does: the collar covers the whole 3 x 0.5 overlap;
      * and cubes whose planes coincide but whose faces do not overlap at all - the bib and both caps
        sharing z = -1.25, the two caps sharing each other's y and z planes - never meet.

    So the assertion is per-pair and per-plane, and what it rejects is the one case that would
    actually z-fight in front of a player."""
    for name in CUBES:
        lo, hi = bounds(name)
        for axis, label in enumerate("xyz"):
            for v in (lo[axis], hi[axis]):
                for wall in (SHELL[0][axis], SHELL[1][axis]):
                    assert abs(v - wall) > EPS, \
                        f"{name}'s {label} face at {v:g} lies on the chestplate shell"

    for a, b in itertools.combinations(CUBES, 2):
        alo, ahi = bounds(a)
        blo, bhi = bounds(b)
        for axis, label in enumerate("xyz"):
            others = [k for k in range(3) if k != axis]
            patch = [(max(alo[k], blo[k]), min(ahi[k], bhi[k])) for k in others]
            if any(hi - lo <= EPS for lo, hi in patch):
                continue                                  # the planes may meet; the faces do not
            for av, bv in itertools.product((alo[axis], ahi[axis]), (blo[axis], bhi[axis])):
                if abs(av - bv) > EPS:
                    continue
                if (av == ahi[axis]) != (bv == bhi[axis]):
                    continue                              # butt joint: interior to the union
                lo = [0.0, 0.0, 0.0]
                hi = [0.0, 0.0, 0.0]
                lo[axis] = hi[axis] = av
                for k, (plo, phi) in zip(others, patch):
                    lo[k], hi[k] = plo, phi
                hidden = inside(SHELL, lo, hi) or any(
                    inside(bounds(c), lo, hi) for c in CUBES if c not in (a, b))
                assert hidden, (f"{a} and {b} put like-facing quads in the plane {label} = {av:g} "
                                f"over {patch}, and nothing buries them")


def check_layout() -> dict:
    """Every face rectangle must sit inside the texture and no two may overlap - a silent overlap
    would paint one cube's shading onto another's face and only show up on a model in game."""
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

    With CUT empty this is every claimed rectangle, which is the circlet's invariant; it is written
    the banner's way so that the day a cut is added the drawing is asserted against the table rather
    than against itself."""
    want = set()
    for name, (size, uv, _) in CUBES.items():
        for face, (x, y, fw, fh) in faces(size, uv).items():
            for j in range(fh):
                for i in range(fw):
                    if face_opaque(name, face, i, j):
                        want.add((x + i, y + j))
    return want


def seen(name, face) -> set:
    """The pixels of one face that the burial mask leaves visible."""
    fw, fh = faces(CUBES[name][0], CUBES[name][1])[face][2:]
    return {(i, j) for j in range(fh) for i in range(fw)
            if face_opaque(name, face, i, j) and not buried(name, face, i, j)}


def whole(name, face) -> set:
    """Every pixel of a face - what `seen` returns when the mask buries none of it."""
    fw, fh = faces(CUBES[name][0], CUBES[name][1])[face][2:]
    return {(i, j) for j in range(fh) for i in range(fw)}


def check_mask() -> None:
    """The burial facts the shape was designed around, asserted rather than described.

    Each one is a geometric claim made in the docstring above, and each would break silently if a
    cube moved: the mask would still be *a* mask and the render would still be *a* render."""
    # Every back face on the three centred cubes is inside the chestplate shell - "the projection is
    # all spent forwards" - and the caps' back faces are the exception, because they are the only
    # geometry on the part outboard of the shell at x = +-5.
    for name in ("bib", "collar", "boss"):
        assert seen(name, "south") == set(), f"{name}'s back face is no longer inside the shell"
    for cap in CAPS:
        assert seen(cap, "south") == whole(cap, "south"), \
            f"{cap}'s back face is no longer wholly outside the chestplate shell"
    # The collar is the hero and nothing on the part stands in front of it or reaches down over it.
    assert seen("collar", "north") == whole("collar", "north"), \
        "the collar's front face is no longer seen whole"
    # The boss is 3 wide on a 5-wide host and covers the middle three columns of the bib's upper row
    # exactly, which is what leaves two lit corners above and a shadow band below. The two-sided form
    # is the point: it fails if the boss grows down onto row 1 as well as if it shrinks off row 0.
    assert seen("bib", "north") == {(0, 0), (4, 0)} | {(i, 1) for i in range(5)}, \
        "the boss no longer covers exactly the middle three columns of the bib's upper row"
    # The bib's whole top is buried - under the collar for its front depth row, inside the shell for
    # the other two. It is the only face on the part the mask erases entirely.
    assert seen("bib", "up") == set(), "the bib's top is no longer wholly under the collar"
    # Each centred course stands only a fraction of its three units of depth proud of the chestplate
    # surface, so on the top and the underside only the front depth row survives.
    assert seen("collar", "up") == {(i, 2) for i in range(9)}, \
        "the throat ledge is no longer exactly the collar's front depth row"
    assert seen("collar", "down") == {(i, 2) for i in range(9)}, \
        "the collar's overhang is no longer exactly its front depth row"
    assert seen("bib", "down") == {(i, 2) for i in range(5)}, \
        "the breast plate's underside is no longer exactly its front depth row"
    # The boss is one unit deep and three quarters of a unit proud, so every face of it but the back
    # is free.
    for face in ("up", "down", "north", "west", "east"):
        assert seen("boss", face) == whole("boss", face), f"the boss's {face} is no longer free"
    # Each centred course shows its front depth column on both flanks and no more; the back ones are
    # in the shell.
    for name in ("bib", "collar"):
        assert seen(name, "west") == {(0, 0), (0, 1)}, \
            f"{name}'s flank is no longer just its front depth column"
    # A centred cube is its own mirror, and for box UV that means the SAME set read backwards,
    # because `west` counts z front to back and `east` back to front. Asserting plain equality would
    # pass on a part lit from the front on one flank and from the back on the other.
    for name in ("bib", "collar", "boss"):
        d = CUBES[name][0][2]
        assert seen(name, "east") == {(d - 1 - i, j) for i, j in seen(name, "west")}, \
            f"{name}'s two flanks are no longer mirror images about x = 0"
    # The caps mirror each OTHER, face for face, with the two flanks crossing over - and that is the
    # pairing every flip() in PAINTERS is built on.
    for face, partner in CAP_MIRROR.items():
        w = CUBES[CAPS[1]][0][0] if face in ("up", "down", "north", "south") else CUBES[CAPS[1]][0][2]
        assert seen(CAPS[0], face) == {(w - 1 - i, j) for i, j in seen(CAPS[1], partner)}, \
            f"{CAPS[0]}.{face} is no longer the mirror of {CAPS[1]}.{partner}"
    # Nothing of this part is above, below, in front of or outboard of a cap, so four of its six
    # faces are seen whole - which is why 90 of the 157 visible pixels are cap.
    for cap in CAPS:
        for face in ("up", "down", "north"):
            assert seen(cap, face) == whole(cap, face), f"{cap}'s {face} is no longer seen whole"
    assert seen(CAPS[1], "west") == whole(CAPS[1], "west"), \
        "the left cap's outboard flank is no longer seen whole"
    # The inboard flank is the one face of a cap that the collar and the shell do bury: its top row
    # clears the collar's own top at geo y = 0.75, and below that only the front pixel stands in
    # front of the shell at z = -3.
    assert seen(CAPS[1], "east") == {(i, 0) for i in range(4)} | {(3, 1)}, \
        "the left cap's inboard flank is no longer its top row plus its front-second pixel"


def main() -> None:
    check_geometry()
    check_symmetry()
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
    assert opaque == set(claimed), "the opaque set is not exactly the UV rectangles"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)

    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    visible = sum(counts.values())
    low = sum(1 for v in lums if v < 128)
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)}, "
          f"{low} under 127)")
    print(f"  {visible} px survive the burial mask, {len(opaque) - visible} are INNER")
    for key in sorted(counts):
        print(f"    {key:18s} {counts[key]:3d} seen")


if __name__ == "__main__":
    main()
