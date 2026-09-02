"""
Paint the grayscale master for the "chain_of_office" part.

The second of the three Court parts, and it reads the shipped geometry the way the coronet painter
beside it does: assets/armorpieces/armorpieces/decoration/chain_of_office.json is opened at run time
and asserted - bone names, pivots and rotations, and every cube's size, uv AND pivot-relative origin.
Four of this part's five bones are rotated, and a rotation is the one edit that moves every pixel of
a face without changing a number this file would otherwise read. Output goes to
tools/decoration_masters/chain_of_office.png, which sync_decoration_masters.py installs for the game
to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

**This master is 100% opaque.** A chain is a row of solid links and a badge is a plate; there is no
fretwork to punch, and a hole cut in a bar one unit thick would show the inside of the bar rather
than the chest behind it, because armorCutoutNoCull draws back faces too. What a chain wants from
its texture is not a silhouette but a *rhythm*, and that is what the alternation down every link
face below is: the links are drawn in value, one texel each, on bars that are geometrically smooth.

--------------------------------------------------------------------------------------------------
The part, in numbers

`COLLAR` is `Attachment.of(BODY, 0, 1, -2)`, one attachment and no mirror, so the part is authored
whole. Part-local (0, 0, 0) is body-local (0, 1, -2) - the base of the throat, on the front face of
the chest. Two frames are quoted: *part-local* (what the geometry JSON holds) and *body-local*
(part-local + (0, 1, -2)), which is what `trace_geometry.py` prints. The body bone's pivot is the
figure's own origin, so body-local IS entity space here, which matters for the one measurement this
part is answerable to off its own bone.

The body box is body-local x +-4, y 0..12, z +-2; the chestplate shell is 1.0 inflate and has one
box per bone, no second layer, so x +-5, y -1..13, z +-3 - in part-local, x +-5, y -2..12, z -1..5.
**The chestplate's front wall is part-local z = -1**, and so is the front wall of the two ARM
shells, which are entity x 3..9 and -9..-3, y -1..13, z +-3: the same plane. Anything of this part
standing in front of z = -1 stands in front of both.

    cube        part-local                                   body-local
    bail        x -0.50.. 0.50 y  1.60.. 3.60 z -1.80..-0.80  x -0.50.. 0.50 y  2.60.. 4.60 z -3.80..-2.80
    plate       x -2.00.. 2.00 y  3.20.. 6.20 z -1.90..-0.90  x -2.00.. 2.00 y  4.20.. 7.20 z -3.90..-2.90
    stone       x -1.00.. 1.00 y  3.70.. 5.70 z -2.60..-1.60  x -1.00.. 1.00 y  4.70.. 6.70 z -4.60..-3.60
    link_lo_l   x -0.31.. 1.88 y  0.27.. 2.29 z -1.65..-0.65  x -0.31.. 1.88 y  1.27.. 3.29 z -3.65..-2.65
    link_hi_l   x  1.07.. 4.22 y -0.44.. 1.25 z -1.60..-0.60  x  1.07.. 4.22 y  0.56.. 2.25 z -3.60..-2.60
    link_lo_r   x -1.88.. 0.31 y  0.27.. 2.29 z -1.70..-0.70  x -1.88.. 0.31 y  1.27.. 3.29 z -3.70..-2.70
    link_hi_r   x -4.22..-1.07 y -0.44.. 1.25 z -1.75..-0.75  x -4.22..-1.07 y  0.56.. 2.25 z -3.75..-2.75

The four link rows are hulls of *rotated* cubes and so are much wider than the cubes are: every link
bar is 1 x 1 in section and the rest is the angle.

Seven cubes, five bones, four of them rotated. **Every dimension is a whole unit** - 1 x 2 x 1,
4 x 3 x 1, 2 x 2 x 1, 2 x 1 x 1, 3 x 1 x 1 - and only the origins and pivots are fractional. That is
the coronet's lesson applied before the mistake rather than after it: `net()` rounds up and `cell()`
clamps to a whole unit, and those two agree exactly only on an integer cube, so a fractional side
would leave the burial mask measuring a different rectangle from the one the game samples.

**The chain lies on the chestplate the way the garters lie on the leggings**: 1 x 1 in section, back
face 0.35 inside the shell wall, front face 0.65 proud of it. That is the Court section and it is
the same one the coronet's brow band uses. Everything else on the part is measured off it: the bail
stands 0.15 prouder than the reference bar, the badge plate 0.25 prouder, and the stone 0.70 prouder
than the plate.

**The chain is a two-segment polyline per side, and the segments are the whole design.** A single
straight bar from the sternum to the shoulder is a strap; two bars at 38 and 14 degrees are a chain
hanging over a collarbone, because a chain's line is nearly flat where it lies on the shoulder and
steep where it falls to the badge. The knee between them is at part-local (1.58, 0.67), and the high
bar starts 0.40 *before* that point so the mitre on the outside of the bend is filled rather than
notched. The 0.20 of high bar that stands proud of the low one at the joint is a fifth of a texel:
it reads as one link lying over another, which is what it is.

**The four bars are stepped 0.05 apart in depth, and that step is load-bearing.** Two bars cross in
three places on this part: the two low bars at the sternum, where both pivot on part-local (0, 1.90)
and reach 0.31 past the centreline, and each low bar into its own high bar at the knee. Left flat
against right, or low flat against high, puts two faces in one plane with overlapping rectangles,
which is a z-fight down the front of the chain - the loudest defect this socket can produce, because
it is at chest height and dead centre. So the four run 0.60, 0.65, 0.70 and 0.75 proud of the shell -
link_hi_l, link_lo_l, link_lo_r, link_hi_r in that order - and at every crossing one bar passes in
front of the other. A twentieth of a unit is a twentieth of a texel and nobody reads it as a
thickness; what they read is a chain whose links overlap, which is what a chain is. It is the
garters' 0.05 offset between band and flank, used three times for the same reason.

The section this part is measured by is the middle of that spread: 0.65 proud, 0.35 in - the garters'
number and the coronet's. The step costs four one-pixel faces that would otherwise have been buried:
each low bar's outer cut end stands 0.05 proud of the high bar it runs into, and each low bar's inner
end stands 0.15 out of the bail. All four are painted as seams, which is what they look like.

**The badge hangs on a neck, and that is not decoration.** The first cut had a four-wide plate
directly under the chain's V, and it rendered as a T-shirt: a wide flat top edge with two straps
diverging above it is a garment, not a jewel. The bail is what fixes it - 1 wide, 2 tall, standing
0.15 proud of the chain so the chain's cut ends disappear behind it, leaving 0.91 of bare neck
between the lowest point of the chain (part-local y 2.29) and the top of the plate (3.20). A badge
narrower than the mouth of the V it hangs in reads as hanging; one wider than it reads as worn.

--------------------------------------------------------------------------------------------------
What it clears, and what it would be hidden by

`trace_geometry` reports no OVERLAP and no COPLANAR line on any shell or against any neighbour, and
one near miss:

    the part clears sash:belt's knot by 0.30 in y   (the plate ends at 6.20, the knot starts at 6.50)

The two measurements that matter more are on a bone this tool does not compare against, because they
are on the ARMS:

    mantle:pauldrons's ruff    entity x 4.75..10.75, y -3..1     this part reaches x 4.22:  0.53 clear
    spaulders:pauldrons's cap  entity x 5.75.. 9.75, y -1.5..-0.5             likewise:  1.53 clear

That is the note `DecorationAnchor` earns: `collar` sits on BODY and the `pauldrons` parts ride the
arms, so nothing in the mod measures them against each other. The shipped `gorget` reaches entity
x +-6.5 with its shoulder tabs, which is 1.75 inside the mantle's ruff and 0.75 inside the
spaulders' cap - so a gorget worn under either loses the ends of itself. This part stops at 4.22 on
purpose. What it does *not* try to do is go over the shoulder: above entity y = 1 the arm shell owns
everything outboard of x = 3, and an arm swinging forward sweeps its own shell to entity z -4.2 at
45 degrees, which is in front of this chain's -3.65. A chain that crossed the shoulder would be
sliced by the wearer's own arm twice a second. It ends at the collarbone's outer end instead, which
is where a chain of office passes out of sight anyway.

--------------------------------------------------------------------------------------------------
Burial is computed, not eyeballed

The coronet's method, unchanged: four of the seven cubes sit on rotated bones, so "is this face pixel
inside that box" cannot be an axis-aligned comparison. Each cube carries its own frame - an origin
and an orthonormal basis composed down the bone chain exactly as the renderer composes it - and a
sample point is tested against a cube by taking it into that cube's frame. The chestplate shell is
the one box that is axis-aligned in the part's frame and is tested directly.

Of 112 face pixels, 30 are INNER: 24 buried in the chestplate and 6 inside another cube of the part.

    plate.south      12 of 12   the badge's back, 0.10 inside the shell
    link_*.south      2 or 3    every bar's back, 0.25 to 0.40 inside the shell
    bail.south        2 of 2    likewise, 0.20 in
    stone.south       4 of 4    the gem's back, 0.30 inside the plate it is set into
    plate.north       2 of 12   the two texels the gem covers whole

Partly-covered pixels are painted as visible, which is the safe direction. Four of them are worth
naming because they look like omissions from that list and are not: the low bars' two cut ends each.
The inner pair, at the sternum, are covered by the bail from every angle a player has, but 0.15 of
their depth stands out of it; the outer pair are inside the high bar they run into but for the 0.05
step. Painting them as seams rather than as INNER is the safe direction, and at one pixel each it
costs nothing.

The occluder list is the chestplate and the part's own cubes. The `pauldrons` and `belt` parts are
optional, so nothing they would cover is masked here: a master is painted for the part, not for one
combination of parts.

--------------------------------------------------------------------------------------------------
Faces and their directions

Blockbench's face names, which are the ones the flip gives: bb = (-geo_x, 24 - geo_y, geo_z), so
`west` is the geo +x face and `east` the geo -x face. This part is not a mirrored pair - `COLLAR`
has one attachment - so the two halves are authored separately and `east` and `west` mean opposite
things on them. That is the trap on this part and it is why the link painters come in pairs: on the
left bars `north`'s column 0 is the end nearest the sternum, and on the right bars it is the end
nearest the shoulder, so the link rhythm has to be counted from the far end on one side to come out
symmetrical on the figure.

The face rectangles come from paint_circlet_master.faces(): row one (v .. v+d) holds up then down,
each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west, south with widths
d, w, d, w. Orientation inside each rectangle is PLAN.md's measured table:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x              max z (back)
    down            +y  (underside)      min x              max z (back)
    west            +x                   min z (front)      min y (top)
    east            -x                   max z (back)       min y (top)
    north           -z  (front)          min x              min y (top)
    south           +z  (back)           max x              min y (top)

--------------------------------------------------------------------------------------------------
The palette, and where the links come from

The wing roots' warning applies: these constants do not transfer between parts by name, they mean
"a face that is seen" and "a face that is not". The hero faces here are the ten pixels of the four
bars' `north` - the chain seen head on, which is the whole of this part from across a room - and the
four of `stone.north`.

**The links are painted, not modelled, and the alternation is the part's one texture idea.** Each
bar's front face is one row of 2 or 3 pixels, and they run LINK, LINK_LO, LINK, ... outward from the
sternum, continuing in phase across the mitre so that a side reads as five links rather than as a
two-piece bar. A 42-value swing is what makes that legible at one texel per link; the first cut used
18 and the chain read as a smooth cord. The `up` faces carry the same alternation half a step
brighter, because the top of a chain is the lit edge and the beads on it are what a camera above the
player sees. The `down` faces do not: an underside that alternates reads as a dotted line, and the
shadow under a chain is continuous.

Values run 35..255. Of the 112 painted pixels 82 survive the burial mask and 30 are INNER; 53 of
them sit below 127, which is the circlet's lesson - the material ramp interpolates dark -> mid over
0..127 and mid -> light over 128..255, so a master that never dips below the middle only ever uses
half of every material's ramp.

Two values were set by looking rather than by arithmetic. The plate's `north` frame began as one
flat value and the badge read as a blank tile; it is graded now, brightest along its top row where
the plate turns over, and the four pixels immediately around the stone are dropped to a seam so the
gem reads as set into the plate rather than stuck on it. And the bail was first painted at the
chain's own value, which made the neck disappear into the V above it; it is 20 brighter than the
links now, because a bail is the one piece of this part that is never in shadow.

--------------------------------------------------------------------------------------------------
The two fittings

Declared `["armorpieces:guard", "armorpieces:gemstone"]`, in that order, which is the order the
smithing table offers them: the chain is what the part *is*, and the stone is what a player adds
afterwards. They do not overlap, so the order does not change a pixel of the render - masks are laid
later over earlier - but it changes which one the table asks for first, and a chain of office with
an empty chain and a filled stone is nobody's first idea of the part.

    guard      the four bars, 48 of the 112 pixels
    gemstone   the stone, 16
    neither    the bail and the plate, 48

That split is the point of the part. The badge stays whatever metal the smithing table put there,
the chain takes a second metal, and the stone takes a gem - so one part is a gold chain on a gold
plate, or an iron chain on a gold plate with an emerald in it, and the three regions never collapse
into one colour the way a single mask over everything would. The masks are the sash's kind, the
master restricted to those cubes' face rectangles, because the shading is the same shading whatever
the material: a link is a link and a cut stone is a cut stone.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image

from fitting_mask import write_mask

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "chain_of_office.json"
OUT = ROOT / "tools" / "decoration_masters" / "chain_of_office.png"

TEX_W, TEX_H = 64, 32

# Pivot and rotation of every bone, mirroring chain_of_office.json. "collar" is the root and sits on
# the anchor itself; the four link bones are its children. The two low bars share one pivot at the
# sternum and reach past each other; the two high bars pivot on the knee of the polyline.
BONES = {
    "collar":    ((0.0, 0.0, 0.0),      (0.0, 0.0, 0.0)),
    "link_lo_l": ((0.0, 1.9, -1.15),    (0.0, 0.0, -38.0)),
    "link_hi_l": ((1.58, 0.67, -1.15),  (0.0, 0.0, -14.0)),
    "link_lo_r": ((0.0, 1.9, -1.15),    (0.0, 0.0, 38.0)),
    "link_hi_r": ((-1.58, 0.67, -1.15), (0.0, 0.0, 14.0)),
}

# bone, size (w, h, d), uv (u, v) and pivot-relative origin, mirroring chain_of_office.json in that
# file's own order.
#   bail  - the neck the badge hangs on, 0.15 proud of the chain so the chain's cut ends vanish
#           behind it. 0.91 of it shows between the chain's lowest point and the plate.
#   plate - the badge, 0.25 proud of the chain and 0.10 inside the chestplate shell.
#   stone - the gem, 0.70 proud of the plate and set 0.30 into it.
#   link_lo_* - the steep bar, 38 degrees, from the sternum out to the knee.
#   link_hi_* - the shallow bar, 14 degrees, from 0.40 behind the knee out to the collarbone's end.
# The right pair sits 0.05 further forward than the left, which is what makes the crossing at the
# sternum a lap instead of a z-fight.
CUBES = {
    "bail":      ("collar",    (1, 2, 1), (16, 0), (-0.5, 1.6, -1.8)),
    "plate":     ("collar",    (4, 3, 1), (0, 0),  (-2.0, 3.2, -1.9)),
    "stone":     ("collar",    (2, 2, 1), (10, 0), (-1.0, 3.7, -2.6)),
    "link_lo_l": ("link_lo_l", (2, 1, 1), (20, 0), (0.0, -0.5, -0.5)),
    "link_hi_l": ("link_hi_l", (3, 1, 1), (32, 0), (-0.4, -0.5, -0.45)),
    "link_lo_r": ("link_lo_r", (2, 1, 1), (26, 0), (-2.0, -0.5, -0.55)),
    "link_hi_r": ("link_hi_r", (3, 1, 1), (40, 0), (-2.6, -0.5, -0.6)),
}

LINKS = ("link_lo_l", "link_hi_l", "link_lo_r", "link_hi_r")

# The chestplate shell over this body, in part-local coordinates (body-local x +-5, y -1..13, z +-3
# shifted by the anchor at (0, 1, -2)). It is always worn when this part draws and it rides the same
# bone, so anything inside it is buried permanently. The two arm shells put their front wall in the
# same plane, z = -1, but they ride bones that swing and are not occluders a mask may rely on.
SHELL = ((-5.0, -2.0, -1.0), (5.0, 12.0, 5.0))

ANCHOR = (0.0, 1.0, -2.0)  # part-local -> body-local, which on this bone is entity space

# The two numbers this part's reach is answerable to, and neither is on its own bone: the inboard
# faces of the shipped `pauldrons` parts, in entity x. They are a recorded datum, not a dependency -
# nothing here reads their files - and check_neighbours() asserts the clearance. If either part is
# reshaped, this line is where the new number gets written down.
PAULDRON_INBOARD = {"mantle:ruff": 4.75, "spaulders:cap": 5.75}
# And the one on its own bone that trace_geometry does report.
SASH_KNOT_TOP = 6.5   # part-local y of sash:belt's knot cube

PUSH = 0.05      # how far off a face a sample sits before it is tested for containment
EPS = 1e-9

random.seed(53)  # deterministic output - regenerating must not churn the PNG

GEM = 250       # the stone's face: the brightest thing on the part
TOP = 234       # a lit top edge - the plate's, the bail's, a bar's
LINK = 210      # a link on a bar's front face
FRAME = 188     # the badge plate's face, around the stone
BAIL = 230      # the neck: brighter than the chain, because nothing shadows it
EDGE = 158      # the plate's or the stone's side faces
LINK_LO = 168   # the link between two lit ones - the alternation is the whole texture idea
CAP = 118       # a cut end of a bar
SEAM = 70       # where one cube emerges from under another, or a gem meets its setting
CREVICE = 56    # a back face outside the shell but facing the chest across nothing at all
INNER = 44      # buried - wholly inside the chestplate shell or inside another cube
DOWN = 36       # a free underside

RIM = 18        # the lit chamfer along a free top edge
FALL = 26       # top-to-bottom falloff down a standing face
XFALL = 14      # centre-to-end falloff along a bar
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
    Rz * Ry * Rx, so the vector meets X first and Z last. Every bone here turns about z alone, so the
    order happens not to matter on this part; it is written the general way because the coronet
    beside it does need it and the two files are meant to be read together."""
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


def body(name):
    """The same hull in the body bone's frame, which on this bone is entity space."""
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
    """The corners of a face pixel's footprint, in part-local space."""
    lo, hi = cell(name, face, i, j)
    return [to_part(name, ((hi if a else lo)[0], (hi if b else lo)[1], (hi if c else lo)[2]))
            for a in (0, 1) for b in (0, 1) for c in (0, 1)]


def inside_shell(pts) -> bool:
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
    """Fill one face rectangle, INNER wherever the burial test says the pixel cannot be seen."""
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
# the four bars - the chain itself
#
# `outward(i, fw, name)` turns a face column into a link index counted from the sternum, so the
# alternation runs the same way down both halves of the figure. On the left bars the cube runs from
# the sternum outward in +x, so column 0 is already the inner end; on the right bars it runs from the
# shoulder inward, so the count has to be reversed. Getting that wrong is invisible in the sheet and
# obvious on a player: one shoulder beaded, the other not.


def outward(i, fw, name):
    return (fw - 1 - i) if name.endswith("_r") else i


def link_north(name):
    """A bar's front face, one row of two or three pixels: the chain seen head on.

    LINK and LINK_LO alternate outward from the sternum, and the phase carries across the mitre
    because the low bar is two pixels long and the high one starts on an even index. A 42-value swing
    is what makes one texel read as one link; at 18 the chain read as a smooth cord."""
    def paint(i, j, fw, fh):
        k = outward(i, fw, name)
        base = LINK if k % 2 == 0 else LINK_LO
        return base - round(XFALL * ramp(k, 3))
    return paint


def link_up(name):
    """A bar's top, one row. The lit edge of the chain and what a camera above the player sees, so it
    is the brightest thing on the bars - and it carries the same alternation as the front, half a step
    up, because the beads on top of a chain are the ones daylight finds."""
    def paint(i, j, fw, fh):
        k = outward(i, fw, name)
        return TOP + RIM - (0 if k % 2 == 0 else 30)
    return paint


def link_down(i, j, fw, fh):
    """A bar's underside. Deliberately NOT alternating: a dotted line under a chain reads as damage,
    and the shadow a chain casts on a chest is continuous."""
    return DOWN + LIP


def link_cap_out(i, j, fw, fh):
    """The outboard cut end of a high bar, where the chain passes out of sight over the collarbone.
    A free face - nothing covers it - so it is an edge rather than a seam."""
    return CAP + 16


def link_cap_in(i, j, fw, fh):
    """The inboard cut end of a low bar, at the sternum. Covered by the bail from every angle a
    player has, but only 0.85 of its depth is inside it, so the footprint test cannot prove it and
    this paints it as the seam it looks like from behind the neck."""
    return SEAM


def link_south(i, j, fw, fh):
    """A bar's back, wholly inside the chestplate. Painted anyway, in case an anchor moves."""
    return CREVICE


# ------------------------------------------------------------------------------------------------
# bail - the neck the badge hangs on


def bail_north(i, j, fw, fh):
    """The neck, 1 x 2, and the only part of this piece with nothing above or in front of it. 20
    brighter than the links, because a bail is never in shadow - the first cut painted it at the
    chain's own value and the neck disappeared into the V above it."""
    return BAIL - round(FALL * ramp(j, fh))


def bail_side(i, j, fw, fh):
    """The neck's two sides, one pixel wide each. They are what says the bail is a ring standing off
    the chest rather than a painted line."""
    return BAIL - 62 - round(FALL * ramp(j, fh))


def bail_up(i, j, fw, fh):
    """The top of the neck, one pixel, standing 0.15 proud of the chain that passes behind it."""
    return TOP + RIM


def bail_down(i, j, fw, fh):
    """The underside of the neck where it enters the plate: a seam, and all but 0.10 of it is inside
    the plate anyway."""
    return SEAM - 8


def bail_south(i, j, fw, fh):
    return CREVICE


# ------------------------------------------------------------------------------------------------
# plate - the badge, and stone - the gem set in it


def plate_north(i, j, fw, fh):
    """The badge's face, 4 x 3, with the gem covering the middle two pixels of the middle row.

    The frame is graded rather than flat: the top row is where the plate turns over into its own lit
    edge and is the brightest, and the four pixels immediately above and below the stone are
    dropped 44 so the gem reads as set into the plate rather than stuck on it. The first cut was one
    value over the whole face and the badge read as a blank tile; the second dropped those four to the
    seam value and they read as two holes punched through it, which is the garters' in_north mistake
    at a different scale."""
    touching = 1 <= i <= 2 and j in (0, 2)
    if touching:
        return FRAME - 44 - (0 if j == 0 else 14)
    return FRAME + RIM - round(30 * ramp(j, fh)) - round(10 * arch(i, fw))


def plate_up(i, j, fw, fh):
    """The badge's top edge, 4 x 1 - the lit edge of the largest flat thing on the part, and what
    tells a camera above the player that the badge stands off the chest at all."""
    return TOP - round(16 * arch(i, fw))


def plate_down(i, j, fw, fh):
    """The badge's underside, 4 x 1: the shadow line that separates it from the chest below."""
    return DOWN + round(10 * (1.0 - arch(i, fw)))


def plate_side(i, j, fw, fh):
    """The badge's two sides, 1 x 3. One unit of depth seen edge-on, falling away downward."""
    return EDGE - round(FALL * ramp(j, fh))


def plate_south(i, j, fw, fh):
    return CREVICE


def stone_north(i, j, fw, fh):
    """The gem's face, 2 x 2, and the brightest thing on the part.

    Two units is too small for alpha to bevel - cutting a corner off a 2-wide face removes half the
    row - so the cut reads entirely in value, as the circlet's cabochon does: a fall from the top row
    to the bottom, with the left column a shade brighter than the right to fix a light direction on a
    stone too small to model one."""
    lean = 10 if i == 0 else -10
    return GEM + lean - round((FALL + 30) * ramp(j, fh))


def stone_up(i, j, fw, fh):
    """The gem's table, 2 x 1: the top facet, and the face that says it stands 0.70 off the plate."""
    return GEM - 10


def stone_side(i, j, fw, fh):
    """The gem's girdle, 1 x 2 on each side. 0.70 of real depth mapped over one pixel."""
    return EDGE - round(FALL * ramp(j, fh))


def stone_down(i, j, fw, fh):
    """The gem's underside, in the plate's own shadow."""
    return SEAM - 12


def stone_south(i, j, fw, fh):
    return INNER


PAINTERS = {
    ("bail", "north"): bail_north, ("bail", "east"): bail_side, ("bail", "west"): bail_side,
    ("bail", "up"): bail_up, ("bail", "down"): bail_down, ("bail", "south"): bail_south,

    ("plate", "north"): plate_north, ("plate", "up"): plate_up, ("plate", "down"): plate_down,
    ("plate", "east"): plate_side, ("plate", "west"): plate_side, ("plate", "south"): plate_south,

    ("stone", "north"): stone_north, ("stone", "up"): stone_up, ("stone", "down"): stone_down,
    ("stone", "east"): stone_side, ("stone", "west"): stone_side, ("stone", "south"): stone_south,
}
for _name in LINKS:
    _out = "west" if _name.endswith("_l") else "east"   # the end that points at the shoulder
    _in = "east" if _name.endswith("_l") else "west"
    PAINTERS.update({
        (_name, "north"): link_north(_name), (_name, "up"): link_up(_name),
        (_name, "down"): link_down, (_name, "south"): link_south,
        (_name, _out): link_cap_out if _name.startswith("link_hi") else link_cap_in,
        (_name, _in): link_cap_in,
    })


def check_geometry() -> None:
    """BONES and CUBES must be the shipped geometry: bone names, pivots and rotations, and every
    cube's size, uv and pivot-relative origin, in file order.

    Painting a texture for a shape the model no longer has is invisible to every other check in this
    pipeline - `bb_geo roundtrip` checks the model against itself and check_layout() checks the
    master against itself, and both keep passing while the rectangles slide off the faces they were
    drawn for."""
    doc = json.loads(GEO.read_text(encoding="utf-8"))
    assert (doc["texture_width"], doc["texture_height"]) == (TEX_W, TEX_H), \
        f"{GEO.name} is {doc['texture_width']}x{doc['texture_height']}, this master is {TEX_W}x{TEX_H}"
    assert len(doc["bones"]) == 1, f"{GEO.name} has {len(doc['bones'])} root bones; this master assumes 1"
    root = doc["bones"][0]
    assert root["name"] == "collar", f"{GEO.name}'s root bone is {root['name']!r}, not 'collar'"

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
    for name in LINKS:
        assert any(abs(r) > EPS for r in BONES[CUBES[name][0]][1]), \
            f"{name}'s bone is no longer rotated - the chain has gone straight"


def check_planes() -> None:
    """No axis-aligned face of this part may lie in a chestplate wall, and no two of them may lie in
    one plane with overlapping rectangles.

    Every link bone turns about z alone, so a bar keeps its two z faces square to the world and loses
    its other four - which is exactly the pair that could fight, since the left and right halves cross
    at the sternum with their fronts and backs parallel. The 0.05 that separates them is what this
    check is here to defend."""
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
                f"{owners} put a face in the chestplate wall {'xyz'[t]} = {v:g}"
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
    return {(i, j) for j in range(fh) for i in range(fw) if not buried(name, face, i, j)}


def check_mask() -> None:
    """The burial and clearance facts the shape was designed around, asserted rather than described.
    """
    # Every back face on the part is inside something: the chestplate for the chain, the bail and the
    # plate; the plate itself for the stone.
    for name in ("bail", "plate") + LINKS:
        assert not seen(name, "south"), f"{name}'s back has come out of the chestplate"
    assert not seen("stone", "south"), "the stone is no longer set into the plate"
    # The gem covers exactly the middle two texels of the plate's middle row - and nothing else of
    # the plate, which is what leaves it a frame rather than a fringe.
    assert seen("plate", "north") == {(i, j) for j in range(3) for i in range(4)} - {(1, 1), (2, 1)}, \
        "the stone no longer covers exactly the middle two texels of the plate's face"
    # Not one cut end of a bar is wholly buried, and that is the step talking rather than a gap: at
    # the knee the low bar lies 0.05 proud of the high one it runs into, and at the sternum the bail
    # covers all but 0.15 of the low bars' inner ends. Four one-pixel faces, painted as seams.
    for name, face in (("link_lo_l", "west"), ("link_lo_r", "east"),
                       ("link_lo_l", "east"), ("link_lo_r", "west")):
        assert seen(name, face) == {(0, 0)}, \
            f"{name}.{face} is no longer the one-pixel seam the 0.05 step leaves"
    # Every INNER pixel accounted for: 24 the shell's and 6 cube-in-cube, all six named above.
    grid = [(n, f, i, j)
            for n in CUBES
            for f, (_, _, fw, fh) in faces(CUBES[n][1], CUBES[n][2]).items()
            for j in range(fh) for i in range(fw)]
    shell_inner = {c for c in grid if buried_by_shell(*c)}
    all_inner = {c for c in grid if buried(*c)}
    assert len(shell_inner) == 24 and len(all_inner) == 30, \
        f"expected 24 shell + 6 cube-in-cube INNER pixels; got {len(shell_inner)} and " \
        f"{len(all_inner) - len(shell_inner)}"
    # The Court section, and the four steps of proudness built on it.
    assert abs(hull("link_lo_l")[1][2] - SHELL[0][2] - 0.35) < EPS, \
        "the chain's back no longer sits 0.35 inside the chestplate shell"
    assert abs(SHELL[0][2] - hull("link_lo_l")[0][2] - 0.65) < EPS, \
        "the chain no longer stands 0.65 proud of the chestplate shell"
    # The four bars are stepped 0.05 apart, so no two of them share a plane where they cross.
    steps = sorted(round(SHELL[0][2] - hull(n)[0][2], 6) for n in LINKS)
    assert steps == [0.60, 0.65, 0.70, 0.75], f"the chain is no longer stepped: {steps}"
    assert abs(hull("link_lo_l")[0][2] - bounds("bail")[0][2] - 0.15) < EPS, \
        "the bail no longer stands 0.15 proud of the chain"
    assert abs(bounds("bail")[0][2] - bounds("plate")[0][2] - 0.10) < EPS, \
        "the plate no longer stands 0.10 proud of the bail"
    assert abs(bounds("plate")[0][2] - bounds("stone")[0][2] - 0.70) < EPS, \
        "the stone no longer stands 0.70 proud of the plate"
    # The right half passes 0.05 in front of the left, which is what makes the crossing a lap.
    assert abs(hull("link_lo_l")[0][2] - hull("link_lo_r")[0][2] - 0.05) < EPS, \
        "the two halves of the chain no longer cross - they are coplanar and will fight"
    assert abs(hull("link_hi_l")[0][2] - hull("link_lo_l")[0][2] - 0.05) < EPS, \
        "the mitre at the knee is coplanar and will fight"
    # The neck: 0.91 of bare bail between the chain's lowest point and the top of the plate. Lose it
    # and the badge stops hanging and starts being worn.
    assert abs(bounds("plate")[0][1] - hull("link_lo_l")[1][1] - 0.91) < 0.005, \
        "the badge no longer hangs on a neck; it is back against the chain"


def check_neighbours() -> None:
    """The clearances this part's reach rests on: one on its own bone, two on the arms.

    `trace_geometry` compares a part only against others on the same bone, so the two `pauldrons`
    parts - which ride the arms and are the reason the shipped gorget loses its shoulder tabs - are
    invisible to it. They are recorded in PAULDRON_INBOARD as entity x and asserted here."""
    reach = max(body(name)[1][0] for name in CUBES)
    for label, wall in PAULDRON_INBOARD.items():
        got = wall - reach
        assert got > 0.5, f"the chain now reaches entity x {reach:.2f}, only {got:.2f} clear of {label}"
    assert abs(PAULDRON_INBOARD["mantle:ruff"] - reach - 0.53) < 0.005, \
        f"the chain reaches entity x {reach:.2f}; the mantle clearance is no longer 0.53"
    gap = SASH_KNOT_TOP - max(hull(name)[1][1] for name in CUBES)
    assert abs(gap - 0.30) < 0.005, f"the badge now clears the sash's knot by {gap:.2f}, not 0.30"


def main() -> None:
    check_geometry()
    check_planes()
    claimed = check_layout()
    check_mask()
    check_neighbours()

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
    for key in sorted(counts):
        print(f"    {key:20s} {counts[key]:3d} seen")

    # Two fittings, in the order the part declares them. The four bars are the chain and take a
    # second metal; the stone takes a gem; the bail and the plate keep whatever metal the smithing
    # table put there, which is what stops a filled part from collapsing into one colour.
    chain = [rect for name in LINKS for rect in faces(*CUBES[name][1:3]).values()]
    write_mask(img, chain, OUT.with_name("chain_of_office_guard.png"))
    write_mask(img, faces(*CUBES["stone"][1:3]).values(),
               OUT.with_name("chain_of_office_gemstone.png"))


if __name__ == "__main__":
    main()
