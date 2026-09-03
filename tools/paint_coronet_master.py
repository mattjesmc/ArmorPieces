"""
Paint the grayscale master for the "coronet" part.

Like the garters painter one theme over - and like the brooch, sash, tassets, spurs, greaves,
brush_crest and vambraces painters before it - this does not merely claim that CUBES matches the
shipped geometry, it reads assets/armorpieces/armorpieces/decoration/coronet.json at run time and
asserts it: bone names, pivots and rotations, and every cube's size, uv AND pivot-relative origin.
The bones are asserted as well as the cubes because five of this part's six bones are *rotated*, and
a rotation is the one edit that moves every pixel of a face without changing a single number this
file would otherwise read. Output goes to tools/decoration_masters/coronet.png, which
sync_decoration_masters.py installs for the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

**This master is 100% opaque**, for the circlet's reason rather than the feathering's: a crown's
silhouette IS its boxes. There is no fringe to cut, and alpha carving would only expose the ring's
interior, because armorCutoutNoCull draws back faces too. It also could not do the one thing it
would be wanted for here. The obvious wish on a coronet is to taper the points, and on a box that is
not available: cutting the top corners off a 1-deep point removes its `east` and `west` columns at
those rows as well, so the tapered part keeps only two faces that are edge-on from the side and the
point simply vanishes when the camera moves. Every point here is a rectangle in elevation, and what
makes the five read as a crown rather than as a fence is that they *lean* - which is a bone, not a
texture.

--------------------------------------------------------------------------------------------------
The part, in numbers

`BROW` is `Attachment.of(HEAD, 0, -4, -4)`, one attachment and no mirror, so this part is authored
whole rather than as a half. Part-local (0, 0, 0) is head-local (0, -4, -4), the middle of the head
box's front face. Two frames are quoted throughout: *part-local* (what the geometry JSON holds) and
*head-local* (part-local + (0, -4, -4)), which is what `trace_geometry.py` prints. The head box is
head-local x +-4, y -8..0, z +-4; the helmet shell is 1.0 inflate everywhere - `createBaseArmorMesh`
takes its 0.1 off the legs, not the head - so head-local x +-5, y -9..1, z +-5, which in part-local
is x +-5, y -5..5, z -1..9. **The helmet's front wall is part-local z = -1 and its crown is
part-local y = -5**, and those two numbers decide most of what follows.

    cube        part-local                                   head-local
    band_front  x -6.00.. 6.00 y -2.00..-1.00 z -1.65..-0.65  x -6.00.. 6.00 y -6.00..-5.00 z -5.65..-4.65
    band_left   x  4.75.. 5.75 y -2.05..-1.05 z -1.25.. 1.75  x  4.75.. 5.75 y -6.05..-5.05 z -5.25..-2.25
    band_right  x -5.75..-4.75 y -2.05..-1.05 z -1.25.. 1.75  x -5.75..-4.75 y -6.05..-5.05 z -5.25..-2.25
    point_c     x -1.00.. 1.00 y -5.21..-1.14 z -2.18..-0.83  x -1.00.. 1.00 y -9.21..-5.14 z -6.18..-4.83
    point_ml    x  1.87.. 3.53 y -4.48..-1.26 z -1.91..-0.65  x  1.87.. 3.53 y -8.48..-5.26 z -5.91..-4.65
    point_mr    x -3.53..-1.87 y -4.48..-1.26 z -1.91..-0.65  x -3.53..-1.87 y -8.48..-5.26 z -5.91..-4.65
    point_ol    x  3.90.. 5.66 y -3.79..-1.48 z -1.85..-0.68  x  3.90.. 5.66 y -7.79..-5.48 z -5.85..-4.68
    point_or    x -5.66..-3.90 y -3.79..-1.48 z -1.85..-0.68  x -5.66..-3.90 y -7.79..-5.48 z -5.85..-4.68

The five point rows are hulls of *rotated* cubes and so are wider and taller than the cubes are:
every point is one unit of section, and the extra is the lean.

Eight cubes, six bones, five of them rotated. The band is three axis-aligned bars; each point is its
own bone with its own rotation, because **cubes cannot rotate - only bones can**. That is not a
detail here, it is the design: five parallel pickets standing off a brow read as a fence and five
splayed ones read as a crown, and the difference is one `rotation` field on five bones.

**Every dimension on this part is a whole unit.** 12 x 1 x 1, 1 x 1 x 3, 2 x 4 x 1, 1 x 3 x 1,
1 x 2 x 1 - only the origins are fractional. That is worth more than tidiness: `net()` rounds up, so
a cube with a fractional side gets a net wider than it uses and the game stretches the face across
it, while `cell()` below clamps a pixel's footprint to one whole unit. On an integer cube those two
agree exactly, and the burial mask therefore measures the same rectangle the game samples. The first
cut of this part had a 1.3-deep leaf and 2.05-tall outer points, and the disagreement painted a
visible sliver of every point's foot as INNER - which rendered as a hole punched in the band beside
each point, with every arithmetic check in this file passing. The heights are made whole by burying
the foot rather than by moving the tip: a point's cube runs from its rise above the pivot down to
0.80, 0.60 or 0.30 *below* it, into the band it stands on, which is also what stops the lean from
opening a wedge underneath.

**The band is one unit tall and one unit deep** and it lies on the helmet the way the garters lie on
the leggings: back face 0.35 *inside* the shell wall, front face 0.65 proud of it. That is the Court
section, and it is what separates this part from the shipped circlet, the other part on this socket:
the circlet's ring is 2 x 2 and carries one stone, this one is 1 x 1 and carries five points. Twelve
units wide is the circlet's own width, deliberately - `past helmet x +1.00` for both - so that
swapping one for the other reads as a change of idea rather than a change of size.

**The ring does not close at the back, and that is a measurement rather than a preference.** The
`horns` socket's two shipped parts, `horns` and `helm_wings`, share one boss: a 3 x 3 x 4 block at
head-local x 4..7, y -8..-5, z -2..2, mirrored. In part-local that is x 4..7, y -4..-1, z 2..6, and
the band's own height - part-local y -2.05..-1.05 - lies wholly inside that y span. There is no
height on this socket at which a brow ring can pass a horn boss: lift the band clear of the boss's
top and it sits at head-local y -8, on the crown of the skull rather than the brow; drop it clear of
the bottom and it sits at head-local y -4.9, across the eyes. So both flanks stop at part-local
z = +1.75, a quarter of a unit in front of the boss's front face, and the ring is a diadem open at
the back. The shipped circlet closes its ring and takes the interpenetration - `OVERLAP: band into
horns:horns's boss by 2.00 x 1.00 x 4.00` - which is defensible, because most of it is inside the
helmet; this part measures the same wall and stops at it, which is the garters' answer to the heel
wings restated one bone up.

**The points stand on whole texels of the band, and that is what the master's beading is made of.**
The band runs from x = -6 to x = +6, so its `north` face has twelve columns whose boundaries are the
integers. point_c is 2 wide at x -1..1 and stands on columns 5 and 6; the mid points on x 2..3 and
-3..-2, columns 8 and 3; the outer points on x 4..5 and -5..-4, columns 10 and 1. FEET below is that
set, computed from the geometry rather than typed, and PEARLS is its complement - the six columns of
band nobody's foot covers, which are painted as the raised beads a coronet carries between its
points. Reading the row left to right that gives pearl, point, pearl, point, pearl, LEAF, pearl,
point, pearl, point, pearl. A crown whose points landed on half-columns could not have that row at
all, and invented beading on a band one pixel tall is a dither.

The rise, the lean and the depth are graduated and none of the three is styling:

    point       rise above the band   lean (rotation z)   front face   part-local top
    point_c            3.20                  0 deg          -1.90          -5.21
    point_ml/mr        2.40                +-13 deg         -1.70          -4.48
    point_ol/or        1.70                +-24 deg         -1.70          -3.79

The rises put the crown's profile at -3.79 / -4.48 / -5.21 / -4.48 / -3.79, which is a curve rather
than a comb. The leans open outward as the rise falls, so the five read as one fan. The depths are
the garters' knot trick: the leaf's front face stands 0.20 proud of the four points and 0.25 proud
of the band, which is what stops three bright uprights side by side from reading as one bright blob.
All five points also carry `rotation` x = 5 degrees, a lean *forward* off the brow shared by every
one of them, so the fan tips away from the face together.

Only the leaf rises past the helmet: its top at part-local y -5.21 clears the helmet crown at y = -5
by 0.21, which `trace_geometry` prints as `past helmet y +0.21`. Nothing else on the part leaves the
helmet's envelope in y at all, which is why a coronet worn under a plumed helm does not fight it -
the two `crest` parts start at head-local z = -3.5 and -3.0 and this part's highest cube ends at
head-local z = -4.83, so they clear by 1.33 without either having to know about the other.

--------------------------------------------------------------------------------------------------
The second helmet shell, and why the numbers above are still the right ones

A helmet is the one armor piece whose mesh has two boxes on its bone. `ARMOR_SLOTS["helmet"]` keeps
children, so `createBaseArmorMesh` emits `head_helmet` at 1.0 inflate AND `hat_helmet` at 1.5, and
`trace_geometry.py` builds its ARMOR_LAYERS with `if not b["name"].startswith("hat_")` - so the
`past helmet` line it prints is measured against the 1.0 box and is half a unit generous about the
outer one. Against the 1.5 hat box, at part-local x +-5.5, y -5.5..5.5, z -1.5..9.5, this part's
margins are:

    band_front   0.15 proud in z      (front face -1.65 against a wall at -1.50)
    band_left/r  0.25 proud in x      (outer face 5.75 against a wall at 5.50)
    point_ml/r   0.20 proud in z, and point_c 0.40 unrotated, 0.68 at the lean
    point_c      0.29 BELOW the hat crown - the leaf clears the 1.0 box in y and not the 1.5 one

against the shipped circlet's 0.50 in z, 0.50 in x and 1.50 for its stone. So on that measurement
this part sits three times closer to the outer box than the other part on its socket does.

It is still the right geometry, because **the hat box draws nothing**. Counting opaque pixels in the
hat region - x 32..64, y 0..16 - of the nine armor sheets `vanilla_assets.py` extracts (chainmail,
copper, diamond, gold, iron, leather, leather_overlay, netherite, turtle_scute) gives zero on every
one of them: vanilla paints the head box and leaves the hat box blank. Armor draws through
`RenderType.armorCutoutNoCull`, whose shader discards a fully transparent fragment before the depth
write, so a blank hat box neither draws a surface for this part to sit against nor writes depth to
occlude it. The surface a player sees, and the only surface that hides anything, is the 1.0 box -
which is why the burial mask below is computed against that one and why `trace_geometry`'s choice to
drop the hat box is the correct one for what it reports.

What that leaves is a resource-pack risk rather than a shipped one: a pack that painted the hat
region would put an opaque wall 0.15 in front of this band. It would put one 0.50 in front of the
circlet's too, and inside the visor's brow plate entirely, so it is a property of the socket and not
of this part - and buying the margin here would cost the 0.35 / 0.65 section that is the whole point
of the shape. The measurement is recorded rather than designed around.

--------------------------------------------------------------------------------------------------
What it clears

    band       clears horns:horns's boss       by 0.25 in z   (the flanks stop at z 1.75, boss at 2)
    band       clears helm_wings:horns's boss  by 0.25 in z   (the same box)
    everything else on the head bone clears by more than half a unit

`trace_geometry` reports no OVERLAP and no COPLANAR line for this part, on any shell or against any
neighbour. That is not luck on the shell either: every plane the band owns was picked off the helmet
walls on purpose, which is why the numbers read -1.65 and 4.75 and 1.75 rather than -1.5 and 5.0
and 2.0.

--------------------------------------------------------------------------------------------------
Burial is computed, not eyeballed

The tassets note in PLAN.md is the method, and it needs one more step here than it did on the flat
parts: five of the eight cubes sit on rotated bones, so "is this face pixel inside that box" cannot
be an axis-aligned comparison. Each cube carries its own frame - an origin and an orthonormal basis
composed down the bone chain exactly as the renderer composes it - and a sample point is tested
against a cube by taking it *into that cube's frame* and comparing against the cube's own corners.
The helmet shell is the one box that is axis-aligned in the part's frame and is tested directly.

Of 154 face pixels, 24 are INNER, and **every one of them is the helmet's**: no cube of this part
hides a whole texel of another, which is the check that says nothing has been driven into anything.

    band_front.south   10 of 12   the band's back, sunk 0.35 into the helmet. Only the two end
                                  columns survive, and only because the band is 12 wide on a shell
                                  10 wide, so a whole texel at each end hangs past the corner
    band_left.east      2 of 3    the flank's inboard face, sunk 0.25 into the helmet wall
    band_right.west     2 of 3    the same face on the other flank
    point_c.south       4 of 8    the leaf's back; the top two rows survive because the leaf's 5
                                  degree forward lean carries them past the shell's front wall as
                                  they rise, the upper one by the 0.21 that stands over the crown
    point_ml.south      3 of 3    a mid point's back, wholly inside the helmet
    point_mr.south      3 of 3    likewise

Nothing else is buried, and in particular no point's foot is: a foot is 0.30 to 0.80 of a unit deep
inside a band 1.00 tall, so the texel it lands in is always part visible. Partly-covered pixels are
painted as visible, which is the safe direction - a visible pixel painted dark is a mistake you can
see, a buried pixel painted bright is not - and those six foot texels get SEAT rather than INNER
for exactly that reason.

The occluder list is the helmet and the part's own cubes, and nothing else. The horn parts are
*optional* - one socket holds one part, and a player may wear no horns at all - so a mask that let
the boss black out the flanks would be painted for one combination of parts rather than for this
part.

--------------------------------------------------------------------------------------------------
Faces and their directions

Blockbench's face names, which are the ones the flip gives: bb = (-geo_x, 24 - geo_y, geo_z), so
`west` is the geo +x face and `east` the geo -x face. This part is not a mirrored pair - `BROW` has
one attachment - so `east` and `west` are simply the two sides of one crown and are painted alike.
The light direction the circlet fixes with a small left/right lean is used here only inside the
leaf, for the circlet's own reason: two units is too few to bevel with alpha, so a facet has to be a
value.

The face rectangles come from paint_circlet_master.faces(): row one (v .. v+d) holds up then down,
each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west, south with widths
d, w, d, w - the two thin d-wide faces FIRST and THIRD. Orientation inside each rectangle is
PLAN.md's measured table:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x              max z (back)
    down            +y  (underside)      min x              max z (back)
    west            +x                   min z (front)      min y (top)
    east            -x                   max z (back)       min y (top)
    north           -z  (front)          min x              min y (top)
    south           +z  (back)           max x              min y (top)

--------------------------------------------------------------------------------------------------
The palette, and which faces are actually seen

The wing roots' warning applies and is worth restating because this is the first of three parts in
one theme: these constants do not transfer between parts by name, they mean "a face that is seen"
and "a face that is not". On a brow band the hero faces are `band_front.north` - twelve pixels in
one row, square on to a camera at eye level - and the five points' `north`. `band_front.up` matters
more than it looks: it is the one lit edge a ring of this section has, and on a head it is what a
camera above the player sees of the whole part.

Values run 34..255. Of the 154 painted pixels 130 survive the burial mask and 24 are INNER; 72 of
them sit below 127, which is the circlet's lesson - the material ramp interpolates dark -> mid over
0..127 and mid -> light over 128..255, so a master that never dips below the middle only ever uses
half of every material's ramp. A crown spends its light narrowly: nearly all of it is on the twelve
pixels of the band's top, the twelve of its front, and the eight of the leaf's face.

Two values were set by looking rather than by arithmetic, both of them the garters' mistake at the
other end of the part. `band_front.north`'s end columns, at the same value as the field, made the
band read as thirteen units wide rather than twelve, because a bar of one flat value has no ends;
dropped by a full bead's worth they read as two holes punched past the corner. They sit 16 under
their neighbours now, which is a falloff running out rather than a statement. And SEAT, the bottom
row of every point, began at the seam value the loops of the garters' bow use; at that value each
point read as standing in a slot cut through the band. It is 128 now - dark enough to seat the
point, light enough to still be band.

--------------------------------------------------------------------------------------------------
The fitting

One fitting, `armorpieces:gemstone`, over `point_c` and nothing else: the crown's principal stone is
the leaf at the front, and the band and the four flanking points keep whatever metal the smithing
table put there. That is the circlet's own relationship - band metal, stone gem - moved off the band
and onto the tallest thing on the part, which is the difference between a circlet with a boss and a
coronet with a jewel in its centre point.

It survives the size test, which is the thing to check before spending a fitting. 28 of the 154
pixels are the leaf and 24 of those are ones a camera can reach, against 106 seen pixels of metal:
so a filled coronet reads as a metal band under a coloured centre at every angle that shows the
front, and as a plain metal crown from behind - which is right, because there is no stone on the
back of a real one either. A mask over all five points would have been a fitting that turns
everything above the band one colour, which is a recolour and not a setting.

The mask is the sash's kind, the master restricted to the leaf's face rectangles, because the leaf's
shading IS the stone's shading: the facet break down its `north` face and the highlight on its `up`
face are the cut, whatever the stone is made of.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image

from fitting_mask import write_mask

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "coronet.json"
OUT = ROOT / "tools" / "decoration_masters" / "coronet.png"

TEX_W, TEX_H = 64, 32

# Pivot and rotation of every bone, mirroring coronet.json. "band" is the root and sits on the
# anchor itself; the five point bones are its children and every one of them is rotated, which is
# the only way a cube in this format can lean. All five share rotation x = 5 - the fan tips forward
# off the brow together - and differ in rotation z, which is the splay.
BONES = {
    "band":     ((0.0, 0.0, 0.0),      (0.0, 0.0, 0.0)),
    "point_c":  ((0.0, -2.0, -1.15),   (5.0, 0.0, 0.0)),
    "point_ml": ((2.5, -2.0, -1.15),   (5.0, 0.0, 13.0)),
    "point_mr": ((-2.5, -2.0, -1.15),  (5.0, 0.0, -13.0)),
    "point_ol": ((4.5, -2.0, -1.15),   (5.0, 0.0, 24.0)),
    "point_or": ((-4.5, -2.0, -1.15),  (5.0, 0.0, -24.0)),
}

# bone, size (w, h, d), uv (u, v) and pivot-relative origin, mirroring coronet.json in that file's
# own order.
#   band_front - the brow bar. 12 wide like the circlet's, 1 x 1 in section instead of 2 x 2; back
#                face 0.35 inside the helmet shell, front face 0.65 proud of it.
#   band_left  - the outboard flank: 0.25 in, 0.75 out. Three long, which stops it a quarter of a
#                unit in front of the horn socket's boss.
#   band_right - the same flank on the other side.
#   point_c    - the centre leaf, 2 wide and standing 0.20 proud of the other four. The one cube the
#                gemstone mask covers.
#   point_ml/r - the mid points, 1 x 1 in section, leaning 13 degrees out.
#   point_ol/r - the outer points, the shortest, leaning 24 degrees out.
# Every point's cube runs from its rise above the pivot down BELOW it - 0.80, 0.60 and 0.30 - so its
# foot is inside the band, its height is a whole number of units, and the lean cannot open a wedge.
CUBES = {
    "band_front": ("band",     (12, 1, 1), (0, 0),   (-6.0, -2.0, -1.65)),
    "band_left":  ("band",     (1, 1, 3),  (0, 2),   (4.75, -2.05, -1.25)),
    "band_right": ("band",     (1, 1, 3),  (8, 2),   (-5.75, -2.05, -1.25)),
    "point_c":    ("point_c",  (2, 4, 1),  (16, 2),  (-1.0, -3.2, -0.75)),
    "point_ml":   ("point_ml", (1, 3, 1),  (22, 2),  (-0.5, -2.4, -0.55)),
    "point_mr":   ("point_mr", (1, 3, 1),  (26, 2),  (-0.5, -2.4, -0.55)),
    "point_ol":   ("point_ol", (1, 2, 1),  (30, 2),  (-0.5, -1.7, -0.55)),
    "point_or":   ("point_or", (1, 2, 1),  (34, 2),  (-0.5, -1.7, -0.55)),
}

POINTS = tuple(name for name in CUBES if name.startswith("point_"))

# The helmet shell over this head, in part-local coordinates (head-local x +-5, y -9..1, z +-5
# shifted by the anchor at (0, -4, -4)). It is always worn when this part draws and it rides the
# same bone, so anything inside it is buried permanently.
SHELL = ((-5.0, -5.0, -1.0), (5.0, 5.0, 9.0))

ANCHOR = (0.0, -4.0, -4.0)  # part-local -> head-local

# The one number this part's shape is answerable to outside its own shell: the front face of the
# boss that `horns` and `helm_wings` share, at head-local z = -2 (a 3 x 3 x 4 block at head-local
# x 4..7, y -8..-5, z -2..2, mirrored). It is a recorded datum, not a dependency - nothing here
# reads their files - and check_mask() asserts the quarter unit the flanks stop short of it by. If
# either of those parts is reshaped, this line is where the new number gets written down.
HORN_BOSS_FRONT = -2.0

PUSH = 0.05      # how far off a face a sample sits before it is tested for containment
EPS = 1e-9

random.seed(41)  # deterministic output - regenerating must not churn the PNG

GEM = 252       # the leaf's face: the brightest thing on the part
TOP = 234       # a lit top edge - the band's own, and what a camera above the player sees
PEARL = 214     # a column of the band's front between two points: the bead a coronet carries there
POINT = 204     # a flanking point's outward face
FACE = 178      # the band's front where a point stands on it: the field the pearls read against
FLANK = 164     # the outboard profile of a flank, the read from the side
SEAT = 128      # the bottom row of a point, most of it sunk into the band it stands on
CAP = 118       # a cut end
SEAM = 70       # where one cube emerges from under another
CREVICE = 56    # a back face outside the shell but facing the helmet across nothing at all
INNER = 44      # buried - wholly inside the helmet shell
DOWN = 36       # a free underside

RIM = 18        # the lit chamfer along a free top edge
FALL = 26       # top-to-bottom falloff down a standing face
ZFALL = 18      # front-to-back falloff along a flank
XFALL = 16      # centre-to-end falloff along the brow bar
LIP = 16        # a free lower edge catching light off its own roll


def net(size):
    """A cube's box-UV net in whole pixels. Rounds UP - which on this part changes nothing, because
    every dimension is already whole. See the docstring on why that was made true."""
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


def rotate(vec, deg):
    """Apply one bone's rotation to a vector.

    Order matters and it is not the order the name suggests. ModelPart.rotate calls JOML's
    rotateZYX(z, y, x), which post-multiplies - the composed matrix is Rz * Ry * Rx, so the vector
    meets X first and Z last. On this part that is not academic: every point bone carries both an x
    and a z angle, and applying them in the written order instead moves each tip by a fraction of a
    unit, which is exactly the case trace_geometry's own note warns about."""
    rx, ry, rz = (math.radians(d) for d in deg)
    x, y, z = vec
    y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
    x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
    x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
    return (x, y, z)


def frame(bone):
    """A bone's (origin, basis) in part-local space, composed the way the renderer composes it.

    Every bone here is either the root or a direct child of it, and the root sits unrotated on the
    anchor, so a child's origin is simply its pivot and its basis its own rotation."""
    pivot, rot = BONES[bone]
    basis = tuple(rotate(e, rot) for e in ((1, 0, 0), (0, 1, 0), (0, 0, 1)))
    return pivot, basis


def bounds(name):
    """A cube's (lo, hi) corners in its own bone's frame."""
    _, size, _, origin = CUBES[name]
    return tuple(origin), tuple(origin[a] + size[a] for a in range(3))


def to_part(name, v):
    """One point of a cube's own frame, in part-local space."""
    org, basis = frame(CUBES[name][0])
    return tuple(org[a] + sum(basis[t][a] * v[t] for t in range(3)) for a in range(3))


def to_cube(name, p):
    """One part-local point, in a cube's own frame. The basis is orthonormal, so this is its
    transpose - which is what makes an oriented-box containment test as cheap as an axis-aligned
    one."""
    org, basis = frame(CUBES[name][0])
    d = [p[a] - org[a] for a in range(3)]
    return tuple(sum(basis[t][a] * d[a] for a in range(3)) for t in range(3))


def hull(name):
    """A cube's axis-aligned hull in part-local space - the box trace_geometry prints."""
    lo, hi = bounds(name)
    pts = [to_part(name, ((hi if i else lo)[0], (hi if j else lo)[1], (hi if k else lo)[2]))
           for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    return (tuple(min(p[a] for p in pts) for a in range(3)),
            tuple(max(p[a] for p in pts) for a in range(3)))


def head(name):
    """The same hull in the head bone's frame, which is what trace_geometry prints."""
    lo, hi = hull(name)
    return (tuple(lo[a] + ANCHOR[a] for a in range(3)),
            tuple(hi[a] + ANCHOR[a] for a in range(3)))


def fspan(lo, hi, axis, i):
    """Pixel i's footprint along one axis, counted from the minimum and clamped to the cube."""
    return (min(lo[axis] + i, hi[axis]), min(lo[axis] + i + 1, hi[axis]))


def rspan(lo, hi, axis, i):
    """The same footprint counted from the maximum, for the faces whose column 0 is the far end."""
    return (max(hi[axis] - i - 1, lo[axis]), max(hi[axis] - i, lo[axis]))


def cell(name, face, i, j):
    """The footprint of one face pixel in the cube's OWN frame, already pushed 0.05 off the face.

    The two in-plane axes span the pixel's whole square rather than just its centre, so a pixel only
    counts as buried when *all* of it is."""
    lo, hi = bounds(name)
    if face in ("up", "down"):                  # col 0 = min x, row 0 = max z
        x0, x1 = fspan(lo, hi, 0, i)
        z0, z1 = rspan(lo, hi, 2, j)
        y = lo[1] - PUSH if face == "up" else hi[1] + PUSH
        return ((x0, y, z0), (x1, y, z1))
    if face in ("east", "west"):                # row 0 = min y
        y0, y1 = fspan(lo, hi, 1, j)
        if face == "west":                      # geo +x, col 0 = min z
            z0, z1 = fspan(lo, hi, 2, i)
            x = hi[0] + PUSH
        else:                                   # geo -x, col 0 = max z
            z0, z1 = rspan(lo, hi, 2, i)
            x = lo[0] - PUSH
        return ((x, y0, z0), (x, y1, z1))
    y0, y1 = fspan(lo, hi, 1, j)                # north / south, row 0 = min y
    if face == "north":                         # geo -z, col 0 = min x
        x0, x1 = fspan(lo, hi, 0, i)
        z = lo[2] - PUSH
    else:                                       # geo +z, col 0 = max x
        x0, x1 = rspan(lo, hi, 0, i)
        z = hi[2] + PUSH
    return ((x0, y0, z), (x1, y1, z))


def cell_corners(name, face, i, j):
    """The corners of a face pixel's footprint, in part-local space."""
    lo, hi = cell(name, face, i, j)
    return [to_part(name, ((hi if a else lo)[0], (hi if b else lo)[1], (hi if c else lo)[2]))
            for a in (0, 1) for b in (0, 1) for c in (0, 1)]


def inside_shell(pts) -> bool:
    """True when every corner of a face pixel's footprint lies inside the helmet."""
    return all(all(SHELL[0][a] - EPS <= p[a] <= SHELL[1][a] + EPS for a in range(3)) for p in pts)


def inside_cube(other, pts) -> bool:
    """True when every corner lies inside another cube, tested in that cube's own frame."""
    lo, hi = bounds(other)
    for p in pts:
        q = to_cube(other, p)
        if not all(lo[a] - EPS <= q[a] <= hi[a] + EPS for a in range(3)):
            return False
    return True


def buried_by_shell(name, face, i, j) -> bool:
    return inside_shell(cell_corners(name, face, i, j))


def buried(name, face, i, j) -> bool:
    """True when the whole of this face pixel is inside the helmet or inside another cube."""
    pts = cell_corners(name, face, i, j)
    if inside_shell(pts):
        return True
    return any(inside_cube(other, pts) for other in CUBES if other != name)


def feet():
    """The columns of band_front's twelve that a point stands on, read out of the geometry.

    A point's foot is its unrotated cross-section at the band's own height, so its footprint on the
    bar is the cube's x span carried to part-local through the bone's pivot - and every one of the
    five lands on whole integers, which is the alignment the beading depends on."""
    lo, hi = bounds("band_front")
    out = set()
    for name in POINTS:
        plo, phi = bounds(name)
        px = BONES[CUBES[name][0]][0][0]
        for i in range(net(CUBES["band_front"][1])[0]):
            c0, c1 = fspan(lo, hi, 0, i)
            if px + plo[0] <= c0 + EPS and c1 <= px + phi[0] + EPS:
                out.add(i)
    return frozenset(out)


FEET = feet()
PEARLS = frozenset(range(net(CUBES["band_front"][1])[0])) - FEET


def put(img, x: int, y: int, lum: int, alpha: int = 255) -> None:
    if 0 <= x < TEX_W and 0 <= y < TEX_H:
        img.putpixel((x, y), (max(0, min(255, lum)), alpha))


def ramp(i: int, n: int) -> float:
    """Position along a face axis, 0.0 at column/row 0 and 1.0 at the far end."""
    return 0.0 if n <= 1 else i / (n - 1)


def arch(i: int, n: int) -> float:
    """Distance from the middle of a face axis, 0.0 at the centre and 1.0 at either end."""
    return 0.0 if n <= 1 else abs(i - (n - 1) / 2) / ((n - 1) / 2)


def paint_face(img, name, face, value) -> int:
    """Fill one face rectangle, INNER wherever the burial test says the pixel cannot be seen.

    Returns the number of pixels that survived as visible, which main() reports - a face whose count
    goes to zero after a geometry edit is the loudest warning this file can give without failing."""
    x0, y0, fw, fh = faces(CUBES[name][1], CUBES[name][2])[face]
    seen_here = 0
    for j in range(fh):
        for i in range(fw):
            if buried(name, face, i, j):
                lum = INNER
            else:
                lum = value(i, j, fw, fh)
                seen_here += 1
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))
    return seen_here


# ------------------------------------------------------------------------------------------------
# band_front - the brow bar


def front_north(i, j, fw, fh):
    """The brow, twelve pixels in one row, and the whole of this part seen head on.

    There is no second axis to shade across - the band is one unit tall - so everything this face has
    to say is said sideways, and what it says is where the points are NOT. The six PEARL columns are
    the ones no point stands on, computed from the geometry; the other six are the field a foot sits
    against and are mostly covered by it anyway. Over the top runs a falloff from the middle to the
    ends, which is what keeps a twelve-pixel bar from reading as a decal and, at the two end columns,
    is the only thing separating the unit of band that hangs past the helmet's corner from the corner
    itself."""
    return (PEARL if i in PEARLS else FACE) - round(XFALL * arch(i, fw))


def front_up(i, j, fw, fh):
    """The top of the band, 12 x 1: a one-unit ledge, wholly clear of the helmet, and the only lit
    edge a ring of this section gets. The five points stand on it, so what is painted here is the
    band between them and the quarter unit of it that shows behind each foot."""
    return TOP + RIM - round(30 * arch(i, fw))


def front_down(i, j, fw, fh):
    """The underside, 12 x 1. This is the shadow line that separates the band from the brow below it,
    and it is why a one-texel ring reads at all from below eye level."""
    return DOWN + round(14 * (1.0 - arch(i, fw)))


def front_cap(i, j, fw, fh):
    """Either cut end of the bar, one pixel, a whole unit past the helmet's corner and covered by
    nothing. A free edge rather than a seam, so it sits above CAP - but well under the face it abuts,
    because at this size a pixel level with its neighbour is a pixel that has vanished."""
    return CAP + 14


def front_south(i, j, fw, fh):
    """The band's back, 12 x 1, column 0 outboard. Ten of the twelve are inside the helmet and the
    mask takes them; this paints the two end columns, which survive because the band is 12 wide on a
    shell 10 wide. They face the helmet's corner across nothing at all, so they are CREVICE."""
    return CREVICE


# ------------------------------------------------------------------------------------------------
# band_left / band_right - the two flanks
#
# The part is not a mirrored pair, so the two flanks are the two sides of one crown and are painted
# alike: whichever of `east` and `west` points away from the head gets the outboard treatment.


def flank_out(i, j, fw, fh):
    """A flank's outboard profile, three columns front to back - the read from the side, and the only
    part of this crown a camera level with the ear sees at all. Falls off backward, because the ring
    stops there rather than closing and the last thing it should do is end on a highlight."""
    return FLANK - round(ZFALL * ramp(i, fw))


def flank_out_rev(i, j, fw, fh):
    """The same face on the other flank, whose column 0 is the BACK rather than the front."""
    return FLANK - round(ZFALL * (1.0 - ramp(i, fw)))


def flank_in(i, j, fw, fh):
    """A flank's helmet-facing side. Two of three columns are inside the shell and the mask takes
    them; the survivor is the one that reaches 0.25 past the shell's front wall and looks into the
    0.40 slot between the flank and the brow bar."""
    return SEAM


def flank_up(i, j, fw, fh):
    """The top of a flank, one column and three rows running BACK to front. Row 2 is the front, level
    with the brow bar's own top; rows 0 and 1 are open sky over the temple. Falls off backward,
    because the skull turns away there and because the ring stops before the ear."""
    return TOP - 20 - round(24 * (1.0 - ramp(j, fh)))


def flank_down(i, j, fw, fh):
    """A flank's underside, rows back to front. Free of everything, so it is graded rather than flat,
    brightest at the front where a camera below the brow can see up into it."""
    return DOWN + LIP - round(10 * (1.0 - ramp(j, fh)))


def flank_north(i, j, fw, fh):
    """A flank's front cut end, one pixel, sitting 0.40 behind the brow bar's own front face and
    inside it for the height they share. Half a seam and half an edge: CAP with a rim."""
    return CAP + RIM


def flank_south(i, j, fw, fh):
    """A flank's rear cut end - where the ring stops rather than closing, a quarter of a unit in
    front of the horn socket's boss. It faces backward into that space, lit by nothing."""
    return CREVICE + 6


# ------------------------------------------------------------------------------------------------
# point_c - the centre leaf, and the gemstone


def leaf_north(i, j, fw, fh):
    """The stone's face: two columns, four rows, and the brightest thing on the coronet.

    Two units is too small for alpha to bevel - cutting a corner off a 2-wide face removes half the
    row - so the cut reads entirely in value, exactly as the circlet's cabochon does. The facet runs
    down from GEM at the crown, the left column a shade brighter than the right, which is the
    circlet's own way of fixing a light direction on a stone too small to model one. The bottom row
    is SEAT: four fifths of it is inside the band."""
    if j == fh - 1:
        return SEAT
    lean = 10 if i == 0 else -10
    return GEM + lean - round((FALL + 20) * ramp(j, fh - 1))


def leaf_up(i, j, fw, fh):
    """The stone's table, 2 x 1 - the top of the tallest thing on the part and the only face of it
    that stands clear of the helmet crown, by the 0.21 trace_geometry prints."""
    return GEM - 8


def leaf_side(i, j, fw, fh):
    """The stone's two flanks, 1 x 4. Painted the same on both sides - the crown is centred and is
    not a mirrored pair - and 40 under the face, which is what makes the leaf read as having a front
    rather than as a slab."""
    if j == fh - 1:
        return SEAT - 10
    return GEM - 40 - round(FALL * ramp(j, fh - 1))


def leaf_down(i, j, fw, fh):
    """The stone's underside where it meets the band. It is not buried - the leaf stands 0.25 proud
    of the bar, so a quarter of a unit of it hangs in front - but nothing lights it, so it is the
    seam the stone is set into."""
    return SEAM - 8


def leaf_south(i, j, fw, fh):
    """The stone's back, 2 x 4: four pixels are inside the helmet and the mask takes them. The two
    rows that survive do so because the leaf's 5 degree forward lean carries them past the shell's
    front wall as they rise - the upper one clears the helmet's crown outright and is the only part
    of this coronet visible from directly behind the player."""
    return CREVICE + 8


# ------------------------------------------------------------------------------------------------
# the four flanking points


def point_north(i, j, fw, fh):
    """A point's front face, one column. This and the leaf are the crown seen from ahead, and the
    four points are deliberately 48 under the leaf: five bright uprights side by side would be one
    bright blob and the centre would stop being the centre. The bottom row is the foot."""
    if j == fh - 1:
        return SEAT
    return POINT - round(FALL * ramp(j, fh - 1))


def point_side(i, j, fw, fh):
    """A point's two flanks. These are what a three-quarter camera sees of the fan, and they carry
    the same falloff as the front so a leaning point does not brighten as it tips."""
    if j == fh - 1:
        return SEAT - 10
    return POINT - 26 - round(FALL * ramp(j, fh - 1))


def point_up(i, j, fw, fh):
    """A point's tip, one pixel. It is the highest lit face on its own side of the crown and is
    painted as one - the five tips together are the profile."""
    return TOP + 6


def point_down(i, j, fw, fh):
    """A point's foot, one pixel, inside the band but for the fifth of it that hangs in front."""
    return SEAM - 6


def point_south(i, j, fw, fh):
    """A point's back. On the mid points every pixel is inside the helmet and the mask takes all
    three; on the outer points the lean carries the cube past the shell's side wall, so both rows
    face the temple across open air."""
    return CREVICE


PAINTERS = {
    ("band_front", "north"): front_north, ("band_front", "up"): front_up,
    ("band_front", "down"): front_down, ("band_front", "west"): front_cap,
    ("band_front", "east"): front_cap, ("band_front", "south"): front_south,

    ("band_left", "west"): flank_out, ("band_left", "east"): flank_in,
    ("band_left", "up"): flank_up, ("band_left", "down"): flank_down,
    ("band_left", "north"): flank_north, ("band_left", "south"): flank_south,

    ("band_right", "east"): flank_out_rev, ("band_right", "west"): flank_in,
    ("band_right", "up"): flank_up, ("band_right", "down"): flank_down,
    ("band_right", "north"): flank_north, ("band_right", "south"): flank_south,

    ("point_c", "north"): leaf_north, ("point_c", "up"): leaf_up,
    ("point_c", "west"): leaf_side, ("point_c", "east"): leaf_side,
    ("point_c", "down"): leaf_down, ("point_c", "south"): leaf_south,
}
for _name in ("point_ml", "point_mr", "point_ol", "point_or"):
    PAINTERS.update({
        (_name, "north"): point_north, (_name, "west"): point_side,
        (_name, "east"): point_side, (_name, "up"): point_up,
        (_name, "down"): point_down, (_name, "south"): point_south,
    })


def check_geometry() -> None:
    """BONES and CUBES must be the shipped geometry: bone names, pivots and rotations, and every
    cube's size, uv and pivot-relative origin, in file order.

    Painting a texture for a shape the model no longer has is invisible to every other check in this
    pipeline - `bb_geo roundtrip` checks the model against itself and check_layout() checks the
    master against itself, and both keep passing while the rectangles slide off the faces they were
    drawn for. The rotations are asserted alongside the origins because this painter's whole burial
    mask is computed through them: a point bone turned five degrees further would leave every INNER
    pixel here wrong, with nothing else in the mod noticing."""
    doc = json.loads(GEO.read_text(encoding="utf-8"))
    assert (doc["texture_width"], doc["texture_height"]) == (TEX_W, TEX_H), \
        f"{GEO.name} is {doc['texture_width']}x{doc['texture_height']}, this master is {TEX_W}x{TEX_H}"
    assert len(doc["bones"]) == 1, f"{GEO.name} has {len(doc['bones'])} root bones; this master assumes 1"
    root = doc["bones"][0]
    assert root["name"] == "band", f"{GEO.name}'s root bone is {root['name']!r}, not 'band'"

    found_bones, found_cubes = {}, []

    def walk(b):
        found_bones[b["name"]] = (tuple(float(v) for v in b.get("pivot", [0, 0, 0])),
                                  tuple(float(v) for v in b.get("rotation", [0, 0, 0])))
        for c in b.get("cubes", []):
            found_cubes.append((b["name"], tuple(float(v) for v in c["size"]), tuple(c["uv"]),
                                tuple(float(v) for v in c["origin"])))
        for child in b.get("children", []):
            walk(child)

    walk(root)
    want_bones = {n: (tuple(float(v) for v in p), tuple(float(v) for v in r))
                  for n, (p, r) in BONES.items()}
    assert found_bones == want_bones, f"BONES disagrees with {GEO.name}: {found_bones} vs {want_bones}"
    want_cubes = [(bone, tuple(float(v) for v in size), tuple(uv), tuple(float(v) for v in origin))
                  for bone, size, uv, origin in CUBES.values()]
    assert found_cubes == want_cubes, \
        f"CUBES disagrees with {GEO.name}: {found_cubes} vs {want_cubes}"
    # Every dimension whole, so net() is exact and the burial mask measures what the game samples.
    for name, (_, size, _, _) in CUBES.items():
        assert all(abs(v - round(v)) < EPS for v in size), \
            f"{name} has a fractional side; the net would no longer be the face"
    # Every point leans. A point bone whose rotation went to zero would put its faces back in planes
    # parallel to the helmet's own, and would also have stopped being a point.
    for name in POINTS:
        assert any(abs(r) > EPS for r in BONES[CUBES[name][0]][1]), \
            f"{name}'s bone is no longer rotated"


def check_planes() -> None:
    """No axis-aligned face of this part may lie in a helmet wall, and no two of them may lie in one
    plane with overlapping rectangles.

    Four of the eight cubes are on bones with a z rotation and have no axis-aligned faces at all, so
    this covers the three band bars plus the two x-normal faces of point_c, whose bone turns about x
    only and therefore keeps its x faces square. Those are exactly the faces that could z-fight with
    the helmet, and none of them does: the band's planes sit at -6.00 / -5.75 / -4.75 / 4.75 / 5.75 /
    6.00 in x, -2.05 / -2.00 / -1.05 / -1.00 in y and -1.65 / -1.25 / -0.65 / 1.75 in z, against
    helmet walls at +-5 in x, -5 and 5 in y and -1 and 9 in z."""
    planes = {}
    for name in CUBES:
        _, basis = frame(CUBES[name][0])
        lo, hi = bounds(name)
        for a in range(3):
            axis = [t for t in range(3) if abs(basis[a][t]) > 1e-6]
            if len(axis) != 1:
                continue                       # this face is not square to any wall
            t = axis[0]
            for corner in (lo, hi):
                v = to_part(name, tuple(corner[k] if k == a else (lo[k] + hi[k]) / 2
                                        for k in range(3)))[t]
                planes.setdefault((t, round(v, 6)), []).append(name)
    for (t, v), owners in sorted(planes.items()):
        for wall in (SHELL[0][t], SHELL[1][t]):
            assert abs(v - wall) > 1e-6, \
                f"{owners} put a face in the helmet wall {'xyz'[t]} = {v:g}"
        others = [k for k in range(3) if k != t]
        for a in range(len(owners)):
            for b in range(a + 1, len(owners)):
                la, ha = hull(owners[a])
                lb, hb = hull(owners[b])
                assert not all(min(ha[k], hb[k]) - max(la[k], lb[k]) > EPS for k in others), \
                    f"{owners[a]} and {owners[b]} put overlapping faces in {'xyz'[t]} = {v:g}"


def check_layout() -> dict:
    """Every face rectangle must sit inside the texture and no two may overlap - a silent overlap
    would paint one cube's shading onto another's face and only show up on a model in game."""
    claimed = {}
    for name, (_, size, uv, _) in CUBES.items():
        for face, (x, y, w, h) in faces(size, uv).items():
            assert 0 <= x and x + w <= TEX_W, f"{name}.{face} runs off the texture in u"
            assert 0 <= y and y + h <= TEX_H, f"{name}.{face} runs off the texture in v"
            for py in range(y, y + h):
                for px in range(x, x + w):
                    prev = claimed.get((px, py))
                    assert prev is None, f"{name}.{face} overlaps {prev} at {(px, py)}"
                    claimed[(px, py)] = f"{name}.{face}"
    return claimed


def seen(name, face):
    """The face pixels the burial test leaves visible."""
    fw, fh = faces(CUBES[name][1], CUBES[name][2])[face][2:]
    return {(i, j) for j in range(fh) for i in range(fw) if not buried(name, face, i, j)}


def check_mask() -> None:
    """The burial and clearance facts the shape was designed around, asserted rather than described.

    Each one is a geometric claim made in the docstring above, and each would break silently if a
    cube or a bone moved: the mask would still be *a* mask and the render would still be *a* render.
    """
    # The band is sunk into the helmet all the way round, and the only pixels of its back that
    # survive are the whole texel at each end that hangs past the shell's corner.
    assert seen("band_front", "south") == {(0, 0), (11, 0)}, \
        "the brow bar's back is no longer buried in the helmet but for its two end columns"
    assert seen("band_left", "east") == {(2, 0)} and seen("band_right", "west") == {(0, 0)}, \
        "a flank is no longer sunk 0.25 into the helmet wall"
    # The beading is an alignment, not a decoration: every point stands on whole columns of the bar,
    # and the six columns left over alternate with the five points across the whole row.
    assert FEET == frozenset({1, 3, 5, 6, 8, 10}), \
        f"the points no longer stand on whole texels of the brow bar: {sorted(FEET)}"
    assert PEARLS == frozenset({0, 2, 4, 7, 9, 11}), f"the beads have moved: {sorted(PEARLS)}"
    # The leaf's back keeps the two rows its forward lean carries past the helmet's front wall, the
    # upper one over the crown itself - the 0.21 trace_geometry prints as `past helmet y +0.21`.
    assert seen("point_c", "south") == {(0, 0), (1, 0), (0, 1), (1, 1)}, \
        "the centre leaf no longer leans out past the helmet's front wall as it rises"
    assert abs(SHELL[0][1] - hull("point_c")[0][1] - 0.21) < 0.005, \
        "the centre leaf no longer clears the helmet crown by 0.21"
    # Every mid point is wholly inside the helmet behind; every outer point leans out past the side
    # wall and is not.
    for name in ("point_ml", "point_mr"):
        assert not seen(name, "south"), f"{name} has come out of the helmet behind"
    for name in ("point_ol", "point_or"):
        assert len(seen(name, "south")) == 2, \
            f"{name} no longer leans out past the helmet's side wall as it rises"
    # No foot is wholly buried, which is what SEAT is for, and nothing on the part hides a whole
    # texel of anything else: every INNER pixel is the helmet's. A cube-in-cube INNER appearing here
    # means two cubes have been driven into each other.
    grid = [(n, f, i, j)
            for n in CUBES
            for f, (_, _, fw, fh) in faces(CUBES[n][1], CUBES[n][2]).items()
            for j in range(fh) for i in range(fw)]
    shell_inner = {c for c in grid if buried_by_shell(*c)}
    all_inner = {c for c in grid if buried(*c)}
    assert all_inner == shell_inner and len(all_inner) == 24, \
        f"expected 24 INNER pixels, all of them the helmet's; got {len(all_inner)} of which " \
        f"{len(all_inner - shell_inner)} are cube-in-cube"
    # The section: 0.35 in, 0.65 out for the bar, 0.25 in and 0.75 out for a flank, and the leaf
    # 0.20 proud of the four points. Lose any of the three and this stops being the Court section.
    assert abs(bounds("band_front")[1][2] - SHELL[0][2] - 0.35) < EPS, \
        "the brow bar's back no longer sits 0.35 inside the helmet shell"
    assert abs(SHELL[0][2] - bounds("band_front")[0][2] - 0.65) < EPS, \
        "the brow bar no longer stands 0.65 proud of the helmet shell"
    assert abs(SHELL[1][0] - bounds("band_left")[0][0] - 0.25) < EPS \
        and abs(bounds("band_left")[1][0] - SHELL[1][0] - 0.75) < EPS, \
        "the outboard flank no longer sits 0.25 in and 0.75 out of the helmet shell"
    leaf_front = BONES["point_c"][0][2] + bounds("point_c")[0][2]
    point_front = BONES["point_ml"][0][2] + bounds("point_ml")[0][2]
    assert abs(point_front - leaf_front - 0.20) < EPS, \
        "the centre leaf no longer stands 0.20 proud of the flanking points"
    assert abs(bounds("band_front")[0][2] - leaf_front - 0.25) < EPS, \
        "the centre leaf no longer stands 0.25 proud of the brow bar"
    # Every point's foot is inside the band, and no deeper than the band is tall.
    for name in POINTS:
        foot = BONES[CUBES[name][0]][0][1] + bounds(name)[1][1]
        assert bounds("band_front")[0][1] < foot <= bounds("band_front")[1][1], \
            f"{name}'s foot is no longer seated inside the brow bar"
    # The ring stops a quarter of a unit in front of the horn socket's boss, which is the whole
    # reason it does not close. trace_geometry prints it as "band clears horns:horns's boss by 0.25".
    assert abs(HORN_BOSS_FRONT - head("band_left")[1][2] - 0.25) < 0.005, \
        "the flanks no longer clear the horn boss's front face by 0.25 in z"


def main() -> None:
    check_geometry()
    check_planes()
    claimed = check_layout()
    check_mask()

    img = Image.new("LA", (TEX_W, TEX_H), (0, 0))
    counts = {}
    for name in CUBES:
        for face in ("up", "down", "east", "north", "west", "south"):
            counts[f"{name}.{face}"] = paint_face(img, name, face, PAINTERS[(name, face)])

    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque == set(claimed), "the opaque set is not exactly the UV rectangles"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)

    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    visible = sum(counts.values())
    low = sum(1 for v in lums if v < 128)
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)}, {low} under 127)")
    print(f"  {visible} px survive the burial mask, {len(opaque) - visible} are INNER")
    print(f"  points stand on band_front columns {sorted(FEET)}, beads on {sorted(PEARLS)}")
    for key in sorted(counts):
        print(f"    {key:20s} {counts[key]:3d} seen")

    # One fitting. The centre leaf is the coronet's stone and takes the gem; the band and the four
    # flanking points keep whatever metal the smithing table put there. See the docstring on why the
    # other four points are left out: a mask over all five would turn everything above the band one
    # colour, which is a recolour and not a setting.
    write_mask(img, faces(*CUBES["point_c"][1:3]).values(), OUT.with_name("coronet_gemstone.png"))


if __name__ == "__main__":
    main()
