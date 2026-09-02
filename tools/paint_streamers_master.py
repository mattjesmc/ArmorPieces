"""
Paint the grayscale master for the "streamers" part.

The third of the three Court parts, and it reads the shipped geometry the way the coronet and
chain_of_office painters beside it do: assets/armorpieces/armorpieces/decoration/streamers.json is
opened at run time and asserted - bone names, pivots and rotations, and every cube's size, uv AND
pivot-relative origin. Two of this part's three bones are rotated, and on this part the rotations are
the whole idea, so they are asserted alongside the origins. Output goes to
tools/decoration_masters/streamers.png, which sync_decoration_masters.py installs for the game to
colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

**This is the one master of the three that is not fully opaque**, and the eight transparent pixels
are all tip. A ribbon that ends in a square is a plank; a ribbon that ends in a point is a ribbon,
and on a strip two texels wide the only way to make a point is to cut one of the two away. So the
last row of each ribbon loses its outboard half on `north`, `south` and `down` and the matching row
of the side face it belonged to, which leaves a one-texel tip and a diagonal edge into it. The two
ribbons are cut on *opposite* sides, which is the cheapest way to say that they are two ribbons and
not one shape drawn twice.

That cut has a known cost and it is the feathering's: at the tip row the surviving half has no side
face of its own, because the face that would have covered it is the one that was carved. Looked at
exactly edge-on, the last texel of a ribbon is see-through. It is one texel at the far end of the
part and it buys a silhouette; the feathering spends the same coin on its fringe.

--------------------------------------------------------------------------------------------------
The part, in numbers

`SPURS` is `Attachment.of(LEFT_LEG, 0, 10, 2)` mirrored on the right, so part-local (0, 0, 0) is
leg-local (0, 10, 2) - the back face of the leg box, at the ankle. Two frames are quoted: *part-local*
(what the geometry JSON holds) and *leg-local* (part-local + (0, 10, 2)), which is what
`trace_geometry.py` prints. The leg box is leg-local x +-2, y 0..12, z +-2; the boots shell is 0.9
rather than 1.0, because `createBaseArmorMesh` re-adds both legs at `extend(-0.1)`, so leg-local
x +-2.9, y -0.9..12.9, z +-2.9 - in part-local, x +-2.9, y -10.9..2.9, z -4.9..0.9. **The boots
shell's back wall is part-local z = +0.9 and the sole is part-local y = +2.0**, and those two numbers
decide this part.

    cube          part-local                                   leg-local
    cuff_back     x -2.50.. 3.50 y -1.50..-0.50 z  0.55.. 1.55  x -2.50.. 3.50 y  8.50.. 9.50 z  2.55.. 3.55
    cuff_out      x  2.65.. 3.65 y -1.55..-0.55 z -1.15.. 0.85  x  2.65.. 3.65 y  8.45.. 9.45 z  0.85.. 2.85
    ribbon_long   x  1.13.. 3.59 y -1.44.. 1.67 z  0.97.. 5.98  x  1.13.. 3.59 y  8.56..11.67 z  2.97.. 7.98
    ribbon_short  x -1.43.. 0.94 y -1.28.. 1.72 z  0.82.. 3.72  x -1.43.. 0.94 y  8.72..11.72 z  2.82.. 5.72

The two ribbon rows are hulls of *rotated* cubes: each ribbon is a flat 2 x 1 strip and everything
else in those numbers is the hang.

Four cubes, three bones, two of them rotated, and **every dimension is a whole unit** - 6 x 1 x 1,
1 x 1 x 2, 2 x 5 x 1, 2 x 3 x 1 - so `net()` is exact and the burial mask measures the rectangle the
game samples. Only the origins and pivots are fractional.

**The cuff lies on the boot the way the garters lie on the leggings**: 1 x 1 in section, back face
0.65 proud of the shell wall and 0.35 of it inside. That is the Court section, the same one the
coronet's brow band and the chain's bars use. The one difference this socket forces is which way the
part faces: the anchor is on the BACK of the ankle, so the hero face of the band is `south` and its
`north` is the buried one - the reverse of the other two parts, and the reason the painters below are
not a copy of theirs.

**The cuff sits at leg-local y 8.5..9.5, above the anchor rather than on it.** That is where the
shipped parts on this socket sit too - `spurs` puts its heel band at leg-local y 7.5..9.5 and
`heel_wings` its clasp at 8.0..11.0 - and it is not fashion, it is the floor. The sole is at
leg-local y 12, and a ribbon hanging from the anchor itself would have two units to fall in before it
was underground. Hanging it from 9.5 buys 2.5, and the two ribbons spend that differently.

**The cuff is offset outboard, and the inboard end of it is deliberately inside the other boot.**
It runs x -2.50..3.50 on a shell that is x +-2.90: the outboard end hangs 0.60 past the shell's side
wall and is covered by the flank, and the inboard end sits 0.40 *inside* it. That is the shipped
`spurs` part's own choice - its heel band is leg-local x -0.15..3.85, further outboard still - and
the reason is the same. The leg bones sit at entity x +-1.9 and each boots shell is 5.8 wide, so the
two shells overlap between entity x -1.0 and +1.0: the inboard quarter of an ankle is inside the
*other* leg's boot at all times, and geometry put there is paid for and never seen. So the band's
weight is outboard, where a camera is, and it turns one corner - outboard only. There is no inboard
flank for the same reason: 0.75 proud on the inboard side would put it through the other boot.

The mirrored pair therefore overlaps itself, and that is the one thing on these three parts that is
allowed to. The band's inboard end sits at entity x -0.60 on the left leg and +0.60 on the right, so
the two copies of it cross by 1.20 - entirely inside two boots. The ribbons do not: the inboard-most
one reaches entity x +0.47, so the two legs' ribbons clear each other by 0.95 in open air, which is
the number that actually matters. check_neighbours() asserts both halves of that.

**The two ribbons differ in every number they have, which is the brief for this part.**

    ribbon         length   pitch (rotation x)   splay (rotation z)   reaches   stops above the sole
    ribbon_long      5          68 deg              -10 deg (out)     z 5.98          0.33
    ribbon_short     3          48 deg               +8 deg (in)      z 3.72          0.28

A symmetric pair reads as one shape drawn twice; two ribbons at different lengths and different
angles read as cloth. The long one streams almost flat and the short one hangs, so from the side they
cross rather than run parallel, and they splay in opposite directions so from behind they are two and
not one. Both stop about three tenths of a unit above the sole and neither goes through it; that
margin is what check_mask() asserts, in both directions, because a ribbon that cleared the floor by a
whole unit would not have used the socket and one that cleared it by nothing would be underground on
the first step.

**Both ribbons are threaded through the band rather than stuck to it**, which is worth a paragraph
because the first cut did the obvious thing and lost the band. The ribbons are 2 wide each and their
roots between them cover x -1.10..3.20 of a band that runs -2.50..3.50, so anything that put them in
front of it hid all of it a camera could see and the part read as two flaps with nothing holding
them. Each ribbon's root instead sits INSIDE the band. The topmost point of the long one is at
part-local y -1.44 and of the short one at -1.28, against a band that runs -1.50..-0.50; the
frontmost point of each is at z 0.97 and 0.82, against a band that runs 0.55..1.55. So both roots are
behind the band's outward face at z 1.55 and under its top edge, and the ribbons emerge from beneath
its lower edge. That is one number doing two jobs: it is why the band reads at all, and it is why a
ribbon never opens a gap where it is tied.

The root is 0.06 below the band's top edge on the long ribbon and 0.22 on the short, and those are
the margins the pitch buys: a ribbon 1 unit thick pitched 68 degrees puts 0.93 of that thickness into
the vertical, so the root patch of a flat strip is nearly as tall as the band it is threaded
through.

**The ribbons are flat plates 2 wide and 1 thick, and the width is in x on purpose.** The other
choice - width in z, the plate standing on edge - is what a hanging ribbon wants, and it is wrong
here: rotating a plate 68 degrees about x turns its z axis nearly vertical, so a 2-wide ribbon would
stand two units up the back of the calf at its root instead of lying along the strap. With the width
in x, which the x rotation leaves alone, the root stays a flat 2 x 1 patch and the strip trails.

--------------------------------------------------------------------------------------------------
What it clears, and the one thing it does not have to

`trace_geometry` reports no OVERLAP and no COPLANAR line for this part, on any shell or against any
neighbour, and no near miss under half a unit at all. Measured cube by cube against the six shipped
parts that can be worn beside it, the clearances are:

    garters:knees     0.65   greaves:greaves  1.60   tassets:tassets  1.75
    puttees:greaves   2.30   poleyns:knees    3.50   pelt:tassets     3.73

and every one of the six is nearest to `cuff_out`, the little flank - the ribbons themselves are
nowhere near anything, because everything else on this leg lives in front of it or above it.

**The reason this part can use the back-outer quadrant of the lower leg is that the thing which owns
it cannot be worn at the same time.** `heel_wings`' upper vane is a 1 x 4 x 6 plate on a bone rotated
(34, 14, 0) and it sweeps leg-local x 1.91..4.62, y 3.72..10.39, z 0.45..7.69 - which is exactly
where both of these ribbons are. The garters, one socket up, had to stop both of their flanks at
leg-local z +0.20 because of it. This part does not, because `heel_wings` is on `spurs` and so is
this: one socket holds one part, and `trace_geometry`'s neighbour pass excludes same-socket parts for
that reason. It is the one place in the mod where a part gets a whole quadrant to itself, and it is
why the ribbons can be 5 long instead of 2.

--------------------------------------------------------------------------------------------------
Burial is computed, not eyeballed

The coronet's method: two of the four cubes sit on rotated bones, so containment is tested by taking
a sample point into the other cube's own frame rather than by comparing axis-aligned boxes. The boots
shell is the one box that is axis-aligned in the part's frame and is tested directly.

Of 92 face pixels, 84 are painted and 8 are cut away at the tips. Only 7 of the 84 are INNER, and all
seven are the boot's:

    cuff_back.north   5 of 6   the band's leg-facing side, sunk 0.35 into the boot. The survivor is
                               the outboard column, the 0.60 that hangs past the shell's side wall
    cuff_out.east     2 of 2   the flank's inboard face, sunk 0.25 into the shell

Nothing on this part hides a whole texel of anything else on it: the ribbons stand 0.05 proud of the
band and their roots are a quarter of a texel into it, which is a lap and not a burial. A
cube-in-cube INNER appearing here would mean two cubes have been driven into each other.

Seven buried pixels out of eighty-four is the fewest of the three Court parts by a wide margin, and
it is the shape talking: a coronet and a chain lie against armour on every side, and this one hangs
off the back of it into open air.

--------------------------------------------------------------------------------------------------
Faces and their directions

Blockbench's face names, which are the ones the flip gives: bb = (-geo_x, 24 - geo_y, geo_z), so
`west` is the geo +x face - outboard on both legs after the layer's scale(-1, 1, 1) - and `east` is
the one facing the other ankle. One master serves both legs because of it, and the lit-outboard /
shadowed-inboard split survives the mirror; it has to be painted rather than left to the engine,
because vanilla's diffuse term shades +x and -x identically, as it does +z and -z.

**The hero face on this part is `south`, not `north`,** and that is the one thing a reader coming
from the coronet or the chain has to re-learn. The anchor is behind the ankle, so the band's outward
face is its +z one and its -z one is inside the boot. On the ribbons the same applies twice over: a
ribbon's two broad faces are `north` and `south`, and after a 68 or 48 degree pitch the `south` one
points up and back - at the sky and at anyone behind - while `north` points down and forward at the
ground. So `south` carries the light on every cube of this part.

The face rectangles come from paint_circlet_master.faces(): row one (v .. v+d) holds up then down,
each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west, south with widths
d, w, d, w. Orientation inside each rectangle is PLAN.md's measured table:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x              max z (back)
    down            +y  (underside)      min x              max z (back)
    west            +x  (outboard)       min z (front)      min y (top)
    east            -x  (inboard)        max z (back)       min y (top)
    north           -z  (front)          min x              min y (top)
    south           +z  (back)           max x              min y (top)

On a ribbon the cube's local +y runs down the strip, so `up` is the root end and `down` is the tip -
which is why the tip cut lands on `down` and on the last ROW of the two broad faces.

--------------------------------------------------------------------------------------------------
The palette

The wing roots' warning applies: these constants do not transfer between parts by name, they mean
"a face that is seen" and "a face that is not". Values run 37..244. Of the 84 painted pixels 77
survive the burial mask and 7 are INNER; 33 of them sit below 127, which is a smaller share than on
either of the other two Court parts and is again the shape: this one is nearly all outward-facing cloth, where the
coronet and the chain are half undersides, seams and buried backs.

Each ribbon falls 50 from root to tip on its lit face. That is the garters' hanging end at four
times the length and for the same reason: a ribbon that does not darken as it goes reads as a solid
rod, and the fall is the only cue at this scale that the far end is further away. The shaded face
falls too but from much lower, so the two never approach each other - a ribbon whose two sides met in
value would stop having a front.

The one value set by looking rather than by arithmetic is `cuff_back.south`'s outboard column. The
band is 6 wide and the ribbons cover its middle, so what a camera behind the player actually sees of
it is the two ends; at the field value the outboard end read as a separate stud floating past the
ribbons. It carries the falloff into it now instead.

--------------------------------------------------------------------------------------------------
The fitting

One fitting, `armorpieces:inlay`, a dye, over the two ribbons and nothing else. It is the garters'
argument on the garters' own socket-neighbour: a ribbon was never meant to be redstone, and on a part
this small a dye is most of its variety - one part becomes sixteen while the cuff keeps whatever
metal the smithing table put there, so a streamer is a coloured ribbon on a metal band rather than a
ribbon in a second metal.

It survives the size test. 60 of the 92 pixels are ribbon and 55 of those are seen, against 24 seen
pixels of band - so a dyed pair reads as colour from every angle that shows the part at all, with the
band as a metal line above it. The mask is the sash's kind, the master restricted to the two ribbons'
face rectangles, because the ribbon's shading IS the dye's shading; the eight cut pixels are
transparent in the master and so are transparent in the mask, which is what keeps a dyed tip pointed.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image

from fitting_mask import write_mask

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "streamers.json"
OUT = ROOT / "tools" / "decoration_masters" / "streamers.png"

TEX_W, TEX_H = 64, 32

# Pivot and rotation of every bone, mirroring streamers.json. "cuff" is the root and sits on the
# anchor itself; the two ribbon bones are its children and hang from the band's lower edge. Their
# rotations are the part: x is the pitch of the hang, z the splay, and no two numbers are shared.
BONES = {
    "cuff":         ((0.0, 0.0, 0.0),      (0.0, 0.0, 0.0)),
    "ribbon_long":  ((2.2, -0.8, 1.05),    (68.0, 0.0, -10.0)),
    "ribbon_short": ((-0.1, -0.8, 1.05),   (48.0, 0.0, 8.0)),
}

# bone, size (w, h, d), uv (u, v) and pivot-relative origin, mirroring streamers.json in that file's
# own order.
#   cuff_back - the band across the back of the ankle: 0.35 into the boot, 0.65 proud of it, and
#               offset outboard because the inboard quarter is inside the other leg's boot.
#   cuff_out  - the outboard flank, 0.25 in and 0.75 out, turning the one corner that is worth
#               turning. Two long, which stops it well clear of the greaves.
#   ribbon_*  - the two strips, 2 wide and 1 thick, rooted 0.25 into the band's lower edge and
#               0.05 proud of its back face.
CUBES = {
    "cuff_back":    ("cuff",         (6, 1, 1), (0, 0),   (-2.5, -1.5, 0.55)),
    "cuff_out":     ("cuff",         (1, 1, 2), (14, 0),  (2.65, -1.55, -1.15)),
    "ribbon_long":  ("ribbon_long",  (2, 5, 1), (20, 0),  (-1.0, 0.1, -0.45)),
    "ribbon_short": ("ribbon_short", (2, 3, 1), (26, 0),  (-1.0, 0.1, -0.45)),
}

RIBBONS = ("ribbon_long", "ribbon_short")

# The tip cut, as (cube, face, column, row) pixels made transparent. Each ribbon loses half of its
# last row so the strip ends in one texel instead of two, and the two ribbons are cut on opposite
# sides of themselves. `north`'s column 0 is min x and `south`'s is max x, so "the +x half" is a
# different index on each of them - which is the sort of thing that is invisible in a sheet and
# obvious on a leg, and is why this table is written out rather than computed from a side name.
#   ribbon_long  loses its OUTBOARD half: north col 1, south col 0, down col 1, west (the +x side)
#   ribbon_short loses its INBOARD half:  north col 0, south col 1, down col 0, east (the -x side)
CUT = frozenset(
    [("ribbon_long", "north", 1, 4), ("ribbon_long", "south", 0, 4),
     ("ribbon_long", "down", 1, 0), ("ribbon_long", "west", 0, 4),
     ("ribbon_short", "north", 0, 2), ("ribbon_short", "south", 1, 2),
     ("ribbon_short", "down", 0, 0), ("ribbon_short", "east", 0, 2)]
)

# The boots shell over this leg, in part-local coordinates (leg-local x +-2.9, y -0.9..12.9, z +-2.9
# shifted by the anchor at (0, 10, 2)). It is 0.9 and not 1.0 because createBaseArmorMesh re-adds
# both legs at extend(-0.1). It is always worn when this part draws and it rides the same bone, so
# anything inside it is buried permanently. The leggings shell is NOT in this list: it is optional,
# it is inside the boots shell everywhere this part goes, and it can hide nothing the boot does not.
SHELL = ((-2.9, -10.9, -4.9), (2.9, 2.9, 0.9))

ANCHOR = (0.0, 10.0, 2.0)  # part-local -> leg-local
SOLE = 2.0                 # part-local y of the bottom of the leg box: the floor a ribbon must clear
LEG_PIVOT_X = 1.9          # entity x of the left leg bone, for the self-clearance of the mirrored pair

# The shipped neighbours on this bone that CAN be worn beside this part, as part-local hulls read out
# of `trace_geometry.py`. A recorded datum, not a dependency - nothing here reads their files - and
# check_neighbours() asserts that every one of them is clear. `spurs` and `heel_wings` are absent on
# purpose: they are on this part's own socket and can never be worn with it, which is the whole
# reason the ribbons may use the back-outer quadrant of the leg at all.
NEIGHBOURS = {
    "garters:knees":   ((-3.15, -4.85, -5.05), (4.05, -1.80, -1.80)),
    "poleyns:knees":   ((-0.35, -6.30, -6.65), (2.65, -2.90, -4.65)),
    "greaves:greaves": ((-2.40, -2.80, -5.65), (2.60, 2.20, -2.75)),
    "puttees:greaves": ((-2.49, -2.45, -6.15), (3.15, 2.70, -3.45)),
    "tassets:tassets": ((-0.65, -10.25, -6.68), (2.70, -3.18, -2.90)),
    "pelt:tassets":    ((0.54, -10.30, -5.30), (3.00, -5.28, 0.98)),
}

PUSH = 0.05      # how far off a face a sample sits before it is tested for containment
EPS = 1e-9

random.seed(59)  # deterministic output - regenerating must not churn the PNG

TOP = 234       # the band's lit top edge, and what a camera above the player sees of the part
RIBBON = 212    # a ribbon's sunlit broad face, at the root
BAND = 190      # the band's outward face - `south` here, not `north`
EDGE = 172      # a ribbon's thin side, one texel wide
UNDER = 138     # a ribbon's shaded broad face, the one that points at the ground
CAP = 112       # a cut end of the band
SEAM = 70       # where the ribbons meet the band
CREVICE = 56    # a face standing outside the shell but turned towards the leg
INNER = 44      # buried - wholly inside the boots shell
DOWN = 36       # a free underside

RIM = 13        # the lit chamfer along a free top edge
FALL = 50       # root-to-tip falloff down a ribbon's lit face
XFALL = 20      # centre-to-end falloff along the band
LIP = 16        # a free lower edge catching light off its own roll


def net(size):
    """A cube's box-UV net in whole pixels. Rounds UP - which on this part changes nothing, because
    every dimension is already whole."""
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

    ModelPart.rotate calls JOML's rotateZYX(z, y, x), which post-multiplies - the composed matrix is
    Rz * Ry * Rx, so the vector meets X first and Z last. Both ribbons carry an x AND a z angle, so
    this is the case trace_geometry's own note warns about: applying them in the written order agrees
    whenever only one axis is non-zero and disagrees by a fraction of a unit exactly here."""
    rx, ry, rz = (math.radians(d) for d in deg)
    x, y, z = vec
    y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
    x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
    x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
    return (x, y, z)


def frame(bone):
    """A bone's (origin, basis) in part-local space, composed the way the renderer composes it."""
    pivot, rot = BONES[bone]
    basis = tuple(rotate(e, rot) for e in ((1, 0, 0), (0, 1, 0), (0, 0, 1)))
    return pivot, basis


def bounds(name):
    """A cube's (lo, hi) corners in its own bone's frame."""
    _, size, _, origin = CUBES[name]
    return tuple(origin), tuple(origin[a] + size[a] for a in range(3))


def to_part(name, v):
    org, basis = frame(CUBES[name][0])
    return tuple(org[a] + sum(basis[t][a] * v[t] for t in range(3)) for a in range(3))


def to_cube(name, p):
    """One part-local point, in a cube's own frame. The basis is orthonormal, so this is its
    transpose."""
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


def leg(name):
    """The same hull in the leg bone's frame, which is what trace_geometry prints."""
    lo, hi = hull(name)
    return (tuple(lo[a] + ANCHOR[a] for a in range(3)),
            tuple(hi[a] + ANCHOR[a] for a in range(3)))


def fspan(lo, hi, axis, i):
    return (min(lo[axis] + i, hi[axis]), min(lo[axis] + i + 1, hi[axis]))


def rspan(lo, hi, axis, i):
    return (max(hi[axis] - i - 1, lo[axis]), max(hi[axis] - i, lo[axis]))


def cell(name, face, i, j):
    """The footprint of one face pixel in the cube's OWN frame, already pushed 0.05 off the face."""
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
    lo, hi = cell(name, face, i, j)
    return [to_part(name, ((hi if a else lo)[0], (hi if b else lo)[1], (hi if c else lo)[2]))
            for a in (0, 1) for b in (0, 1) for c in (0, 1)]


def inside_shell(pts) -> bool:
    return all(all(SHELL[0][a] - EPS <= p[a] <= SHELL[1][a] + EPS for a in range(3)) for p in pts)


def inside_cube(other, pts) -> bool:
    lo, hi = bounds(other)
    for p in pts:
        q = to_cube(other, p)
        if not all(lo[a] - EPS <= q[a] <= hi[a] + EPS for a in range(3)):
            return False
    return True


def buried_by_shell(name, face, i, j) -> bool:
    return inside_shell(cell_corners(name, face, i, j))


def buried(name, face, i, j) -> bool:
    pts = cell_corners(name, face, i, j)
    if inside_shell(pts):
        return True
    return any(inside_cube(other, pts) for other in CUBES if other != name)


def put(img, x: int, y: int, lum: int, alpha: int = 255) -> None:
    if 0 <= x < TEX_W and 0 <= y < TEX_H:
        img.putpixel((x, y), (max(0, min(255, lum)), alpha))


def ramp(i: int, n: int) -> float:
    return 0.0 if n <= 1 else i / (n - 1)


def arch(i: int, n: int) -> float:
    return 0.0 if n <= 1 else abs(i - (n - 1) / 2) / ((n - 1) / 2)


def paint_face(img, name, face, value) -> int:
    """Fill one face rectangle: transparent where the tip is cut, INNER where the burial test says
    the pixel cannot be seen, and the painter's own value everywhere else."""
    x0, y0, fw, fh = faces(CUBES[name][1], CUBES[name][2])[face]
    seen_here = 0
    for j in range(fh):
        for i in range(fw):
            if (name, face, i, j) in CUT:
                continue                                  # left transparent: the tip
            if buried(name, face, i, j):
                lum = INNER
            else:
                lum = value(i, j, fw, fh)
                seen_here += 1
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))
    return seen_here


# ------------------------------------------------------------------------------------------------
# cuff_back - the band across the back of the ankle


def band_south(i, j, fw, fh):
    """The band seen from behind, six pixels in one row, and the whole of the metal on this part.

    `south` and not `north`, because the anchor is behind the ankle: this is the face that points
    away from the leg. Column 0 is the OUTBOARD end. The falloff runs into both ends, and the
    outboard one needs it: the ribbons cover the middle of the band, so the two ends are what a
    camera behind the player actually sees, and at the field value the outboard end read as a stud
    floating past the ribbons rather than as the band continuing under them."""
    return BAND - round(XFALL * arch(i, fw))


def band_up(i, j, fw, fh):
    """The top of the band, 6 x 1: a one-unit ledge in open air, and the only lit edge a strap of this
    section has. On a leg it is what a camera above the player sees of the whole part."""
    return TOP + RIM - round(26 * arch(i, fw))


def band_down(i, j, fw, fh):
    """The underside, 6 x 1 - and on this part it is not a shadow line but the ceiling the two
    ribbons hang out of, so it carries a little more light at the middle where they are."""
    return DOWN + round(18 * (1.0 - arch(i, fw)))


def band_north(i, j, fw, fh):
    """The band's leg-facing side. Five of six are inside the boot and the mask takes them; the
    survivor is the outboard column, the 0.60 that hangs past the shell's side wall and looks into
    the slot between the band and the flank."""
    return SEAM


def band_cap_out(i, j, fw, fh):
    """The band's outboard cut end, one pixel, tucked inside the flank for all but its rear 0.70."""
    return CAP + 12


def band_cap_in(i, j, fw, fh):
    """The band's inboard cut end, one pixel. It is 0.40 inside this leg's own boot and inside the
    other leg's as well, so it is never seen from any angle the game offers - but the footprint test
    cannot prove the second of those, because the other boot is not on this bone. Painted as the
    seam it would be if it ever showed."""
    return SEAM - 10


# ------------------------------------------------------------------------------------------------
# cuff_out - the outboard flank, the one corner the band turns


def flank_west(i, j, fw, fh):
    """The flank's outboard profile, two columns front to back: the read from the side, and the only
    piece of band that is not behind a ribbon. Falls off forward, away from the ribbons."""
    return BAND - 16 - round(24 * (1.0 - ramp(i, fw)))


def flank_east(i, j, fw, fh):
    """The flank's inboard face, wholly inside the boot."""
    return INNER


def flank_up(i, j, fw, fh):
    """The top of the flank, one column and two rows running BACK to front."""
    return TOP - 22 - round(20 * (1.0 - ramp(j, fh)))


def flank_down(i, j, fw, fh):
    """The flank's underside, rows back to front. Free of everything - the greaves' plate is 1.60
    away in z - so it is graded rather than flat."""
    return DOWN + LIP - round(8 * (1.0 - ramp(j, fh)))


def flank_north(i, j, fw, fh):
    """The flank's forward cut end, one pixel, where the band stops rather than closing round the
    front of the ankle. Nothing shipped is within 1.60 of it; it stops there because a band that ran
    on would be a boot cuff and this part is a tie."""
    return CAP


def flank_south(i, j, fw, fh):
    """The flank's rear cut end, one pixel, inside the band's own outboard end."""
    return SEAM + 8


# ------------------------------------------------------------------------------------------------
# the two ribbons
#
# On a ribbon the cube's local +y runs down the strip, so on `north` and `south` row 0 is the root
# and the last row is the tip; on `east` and `west` the same; and `up` is the root end while `down`
# is the tip.


def ribbon_lit(i, j, fw, fh):
    """A ribbon's sunlit broad face - `south`, which after the pitch points up and back at anyone
    behind the player. It falls 60 from root to tip, which is the garters' hanging end at four times
    the length and for its reason: a strip that does not darken as it goes reads as a rod, and the
    fall is the only cue at this scale that the far end is further away."""
    return RIBBON - round(FALL * ramp(j, fh))


def ribbon_shade(i, j, fw, fh):
    """A ribbon's shaded broad face - `north`, pointing down and forward at the ground. It falls too,
    but from much lower, so the two faces never approach each other in value: a ribbon whose sides
    met would stop having a front."""
    return UNDER - round(26 * ramp(j, fh))


def ribbon_edge(i, j, fw, fh):
    """A ribbon's thin side, one texel wide down its whole length. This is the whole of a ribbon seen
    edge-on and it is what makes the strip read as cloth rather than as a plank: it sits between the
    two broad faces in value, so a ribbon rolling past the camera never jumps."""
    return EDGE - round(30 * ramp(j, fh))


def ribbon_root(i, j, fw, fh):
    """A ribbon's root end, 2 x 1, a quarter of a unit inside the band it hangs from."""
    return SEAM


def ribbon_tip(i, j, fw, fh):
    """A ribbon's tip end, 2 x 1 - one pixel of which is cut away, so this paints the half that is
    left. The darkest thing on the ribbon, because it is the end of the fall and because a tip that
    is not dark is a tip that reads as broken off."""
    return SEAM + 48


PAINTERS = {
    ("cuff_back", "south"): band_south, ("cuff_back", "up"): band_up,
    ("cuff_back", "down"): band_down, ("cuff_back", "north"): band_north,
    ("cuff_back", "west"): band_cap_out, ("cuff_back", "east"): band_cap_in,

    ("cuff_out", "west"): flank_west, ("cuff_out", "east"): flank_east,
    ("cuff_out", "up"): flank_up, ("cuff_out", "down"): flank_down,
    ("cuff_out", "north"): flank_north, ("cuff_out", "south"): flank_south,
}
for _name in RIBBONS:
    PAINTERS.update({
        (_name, "south"): ribbon_lit, (_name, "north"): ribbon_shade,
        (_name, "west"): ribbon_edge, (_name, "east"): ribbon_edge,
        (_name, "up"): ribbon_root, (_name, "down"): ribbon_tip,
    })


def check_geometry() -> None:
    """BONES and CUBES must be the shipped geometry: bone names, pivots and rotations, and every
    cube's size, uv and pivot-relative origin, in file order.

    Painting a texture for a shape the model no longer has is invisible to every other check in this
    pipeline. The rotations matter more here than on either of the other two Court parts, because on
    this one they are the design: the two ribbons differ by nothing except their length and their two
    angles, and a copied rotation would turn the pair symmetric without moving a cube."""
    doc = json.loads(GEO.read_text(encoding="utf-8"))
    assert (doc["texture_width"], doc["texture_height"]) == (TEX_W, TEX_H), \
        f"{GEO.name} is {doc['texture_width']}x{doc['texture_height']}, this master is {TEX_W}x{TEX_H}"
    assert len(doc["bones"]) == 1, f"{GEO.name} has {len(doc['bones'])} root bones; this master assumes 1"
    root = doc["bones"][0]
    assert root["name"] == "cuff", f"{GEO.name}'s root bone is {root['name']!r}, not 'cuff'"

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
    assert found_cubes == want_cubes, f"CUBES disagrees with {GEO.name}: {found_cubes} vs {want_cubes}"
    for name, (_, size, _, _) in CUBES.items():
        assert all(abs(v - round(v)) < EPS for v in size), \
            f"{name} has a fractional side; the net would no longer be the face"
    # The pair is a pair only in name: no two of length, pitch and splay may match.
    a, b = (BONES[n][1] for n in RIBBONS)
    la, lb = (CUBES[n][1][1] for n in RIBBONS)
    assert la != lb and abs(a[0] - b[0]) > 5 and a[2] * b[2] < 0, \
        "the two ribbons have become a symmetric pair - same length, same pitch, or splaying the " \
        "same way"


def check_planes() -> None:
    """No axis-aligned face of this part may lie in a boots-shell wall, and no two of them may lie in
    one plane with overlapping rectangles.

    Both ribbon bones carry an x rotation, so a ribbon keeps only its two x faces square to the world
    and loses the other four; the two cuff cubes keep all six. Those are the faces that could z-fight
    with the boot, and none of them does: the band's planes sit at -2.50 / 2.65 / 3.50 / 3.65 in x,
    -1.55 / -1.50 / -0.55 / -0.50 in y and -1.15 / 0.55 / 0.85 / 1.55 in z, against boot walls at
    +-2.90 in x, -10.90 and 2.90 in y and -4.90 and 0.90 in z."""
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
                f"{owners} put a face in the boots-shell wall {'xyz'[t]} = {v:g}"
        others = [k for k in range(3) if k != t]
        for a in range(len(owners)):
            for b in range(a + 1, len(owners)):
                la, ha = hull(owners[a])
                lb, hb = hull(owners[b])
                assert not all(min(ha[k], hb[k]) - max(la[k], lb[k]) > EPS for k in others), \
                    f"{owners[a]} and {owners[b]} put overlapping faces in {'xyz'[t]} = {v:g}"


def check_layout() -> dict:
    """Every face rectangle must sit inside the texture and no two may overlap."""
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
    fw, fh = faces(CUBES[name][1], CUBES[name][2])[face][2:]
    return {(i, j) for j in range(fh) for i in range(fw)
            if (name, face, i, j) not in CUT and not buried(name, face, i, j)}


def check_cut() -> None:
    """The tip cut must take exactly half of each ribbon's last row, on four faces, and no more.

    A cut in the wrong row would carve a hole in the middle of a ribbon; a cut on the wrong face
    would leave the tip square from one side and pointed from the other. Both are invisible in the
    sheet, so both are asserted from the geometry rather than trusted from the table."""
    assert len(CUT) == 8, f"the tip cut is {len(CUT)} pixels, not 8"
    for name in RIBBONS:
        rows = net(CUBES[name][1])[1]
        mine = {c for c in CUT if c[0] == name}
        assert len(mine) == 4, f"{name}'s tip is cut on {len(mine)} faces, not 4"
        assert {c[1] for c in mine} == {"north", "south", "down", "west" if name == "ribbon_long"
                                       else "east"}, f"{name}'s tip is cut on the wrong faces"
        for cube, face, i, j in mine:
            if face == "down":
                assert j == 0, f"{name}'s tip end is cut on the wrong row"
            else:
                assert j == rows - 1, f"{name} is cut at row {j}, not its last ({rows - 1})"
        # north's column 0 is min x and south's is max x, so the same physical half is a different
        # index on each: the two must NOT be equal, or the cut has taken opposite halves and the tip
        # is a diagonal slot rather than a point.
        north = next(c[2] for c in mine if c[1] == "north")
        south = next(c[2] for c in mine if c[1] == "south")
        down = next(c[2] for c in mine if c[1] == "down")
        assert north != south and down == north, \
            f"{name}'s tip cut takes different halves on its two broad faces"
    # And the two ribbons are cut on opposite sides of themselves.
    assert next(c[2] for c in CUT if c[0] == "ribbon_long" and c[1] == "north") != \
        next(c[2] for c in CUT if c[0] == "ribbon_short" and c[1] == "north"), \
        "both ribbons are now cut on the same side; they are a symmetric pair again"


def check_mask() -> None:
    """The burial and clearance facts the shape was designed around, asserted rather than described.
    """
    # The band is sunk into the boot, and the only pixel of its leg-facing side that survives is the
    # outboard column - the 0.60 that hangs past the shell's side wall.
    assert seen("cuff_back", "north") == {(5, 0)}, \
        "the band's leg-facing side is no longer buried in the boot but for its outboard column"
    assert not seen("cuff_out", "east"), "the flank is no longer sunk 0.25 into the boot"
    # Every INNER pixel is the boot's; nothing on this part hides a whole texel of anything else.
    grid = [(n, f, i, j)
            for n in CUBES
            for f, (_, _, fw, fh) in faces(CUBES[n][1], CUBES[n][2]).items()
            for j in range(fh) for i in range(fw) if (n, f, i, j) not in CUT]
    shell_inner = {c for c in grid if buried_by_shell(*c)}
    all_inner = {c for c in grid if buried(*c)}
    assert all_inner == shell_inner and len(all_inner) == 7, \
        f"expected 7 INNER pixels, all of them the boot's; got {len(all_inner)} of which " \
        f"{len(all_inner - shell_inner)} are cube-in-cube"
    # The Court section: 0.35 in, 0.65 out, and the flank 0.25 in and 0.75 out.
    assert abs(SHELL[1][2] - bounds("cuff_back")[0][2] - 0.35) < EPS, \
        "the band's leg-facing side no longer sits 0.35 inside the boots shell"
    assert abs(bounds("cuff_back")[1][2] - SHELL[1][2] - 0.65) < EPS, \
        "the band no longer stands 0.65 proud of the boots shell"
    assert abs(SHELL[1][0] - bounds("cuff_out")[0][0] - 0.25) < EPS \
        and abs(bounds("cuff_out")[1][0] - SHELL[1][0] - 0.75) < EPS, \
        "the outboard flank no longer sits 0.25 in and 0.75 out of the boots shell"
    # Both ribbons are threaded THROUGH the band: the topmost and the frontmost point of each is
    # inside it, so the band's outward face is in front of both roots and the band reads. Lose
    # either and the part becomes two flaps with nothing holding them.
    band_lo, band_hi = bounds("cuff_back")
    for name in RIBBONS:
        lo, hi = hull(name)
        assert band_lo[1] < lo[1] < band_hi[1], \
            f"{name}'s root has come out of the top or the bottom of the band"
        assert band_lo[2] < lo[2] < band_hi[2], \
            f"{name}'s root is no longer behind the band's outward face"
        assert band_hi[1] - lo[1] > 0.7, \
            f"{name} is no longer threaded through the whole depth of the band"
    # Neither ribbon goes through the floor, and both get close enough to it to have used the socket.
    for name in RIBBONS:
        drop = SOLE - hull(name)[1][1]
        assert 0.15 < drop < 0.60, f"{name} ends {drop:.2f} above the sole, which is wrong either way"


def check_neighbours() -> None:
    """Every shipped part that can be worn beside this one clears it, and the mirrored pair clears
    itself.

    NEIGHBOURS is a recorded datum - the hulls `trace_geometry.py` prints - so this is a tripwire and
    not a dependency. `spurs` and `heel_wings` are not in it because they cannot be worn with this
    part; see the docstring on why that is the reason the ribbons exist at all."""
    def gap_to(box):
        """The part's clearance from one hull: per cube, the widest axis separation - which is what
        separates two boxes - and then the narrowest of those over the part."""
        olo, ohi = box
        worst = 9.0
        for name in CUBES:
            lo, hi = hull(name)
            worst = min(worst, max(max(olo[a] - hi[a], lo[a] - ohi[a]) for a in range(3)))
        return worst

    for label, box in NEIGHBOURS.items():
        gap = gap_to(box)
        assert gap > 0.5, f"this part now clears {label} by only {gap:+.2f}"
    # The mirrored pair. Left leg x is entity 1.9 + leg x, and the right leg's mirror puts its own
    # copy at entity -1.9 - leg x, so the two copies of a cube meet when its inboard face passes
    # entity x = 0. The BAND's does, by 0.60, and that is the deliberate part: its inboard end is
    # 0.40 inside this boot and inside the other one too, so the two copies overlap only where both
    # are already buried in armour. What must not happen is a RIBBON doing it, because a ribbon
    # hangs in open air and two of them crossing between the ankles would be visible from every
    # angle at once.
    assert min(hull(n)[0][0] for n in CUBES) >= SHELL[0][0] - EPS, \
        "some of this part now hangs out of the boot on the inboard side, where the other leg is"
    gap = 2 * (LEG_PIVOT_X + min(hull(n)[0][0] for n in RIBBONS))
    assert gap > 0.5, f"the two legs' ribbons clear each other by only {gap:+.2f}"


def main() -> None:
    check_geometry()
    check_planes()
    claimed = check_layout()
    check_cut()
    check_mask()
    check_neighbours()

    img = Image.new("LA", (TEX_W, TEX_H), (0, 0))
    counts = {}
    for name in CUBES:
        for face in ("up", "down", "east", "north", "west", "south"):
            counts[f"{name}.{face}"] = paint_face(img, name, face, PAINTERS[(name, face)])

    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    cut = set()
    for name, face, i, j in CUT:
        x, y, _, _ = faces(CUBES[name][1], CUBES[name][2])[face]
        cut.add((x + i, y + j))
    assert opaque == set(claimed) - cut, "the opaque set is not the UV rectangles less the tip cut"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)

    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    visible = sum(counts.values())
    low = sum(1 for v in lums if v < 128)
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)}, {low} under 127)")
    print(f"  {visible} px survive the burial mask, {len(opaque) - visible} are INNER, "
          f"{len(cut)} are cut away at the tips")
    for key in sorted(counts):
        print(f"    {key:22s} {counts[key]:3d} seen")

    # One fitting. The two ribbons are the inlay and take a dye; the cuff alone keeps whatever metal
    # the smithing table put there. The eight cut pixels are transparent in the master, so write_mask
    # leaves them transparent here too and a dyed tip stays pointed.
    ribbon = [rect for name in RIBBONS for rect in faces(*CUBES[name][1:3]).values()]
    write_mask(img, ribbon, OUT.with_name("streamers_inlay.png"))


if __name__ == "__main__":
    main()
