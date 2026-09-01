"""
Paint the grayscale master for the "visor" part.

Like paint_brooch_master.py, paint_sash_master.py and paint_spurs_master.py this does not merely
claim that CUBES matches the shipped geometry, it reads
assets/armorpieces/armorpieces/decoration/visor.json at run time and asserts it - origins, sizes,
UVs, the lip bone's pivot and its rotation (check_geometry). Output goes to
tools/decoration_masters/visor.png, which sync_decoration_masters.py installs for the game to
colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette. No static colour layer: a
visor is helmet hardware, so every pixel here takes the trim material, which is the opposite call
from the horns (keratin) and the same one heel_wings made.

WHAT THIS PART IS
-----------------
A knight's sight-slit visor on the `brow` anchor - head geo (0, -4, -4), the middle of the head's
front face. It shares the socket with `circlet` and had to read as a different object: the circlet is
a 2-tall band that wraps the head and carries a stone, so this one is the other thing a brow socket
can hold, a solid frontal plate with mass and a hole. Four cubes, two bones:

  * `plate` - 8 x 5 x 1 at head x -4..4, y -7..-2, z -7..-6. The faceplate, standing 2 units proud of
    the 1.0-inflate helmet's front wall at z = -5 with a unit of air behind it. The sight is punched
    through this cube in alpha, and the cube is ONE unit thick for that reason - see THE SIGHT below.
  * `bar` - 6 x 2 x 4 at head x -3..3, y -7.6..-5.6, z -7.75..-3.75. The brow reinforce, and the
    thing that stops the plate reading as a slab floating off the helmet: it is the only cube that
    reaches back through the helmet wall - 1.25 units behind it, ending 0.25 inside the head box -
    so the plate is visibly bolted on rather than hovering.
  * `keel` - 2 x 2 x 1 at head x -1..1, y -6..-4, z -7.5..-6.5. The nasal ridge, 0.5 proud of the
    plate and 0.4 buried up into the bar, ending exactly on the sight's top edge at y = -4.
  * `lip` - 5 x 4 x 1 on a child bone pivoted at head (0, -2, -6.5) - the plate's own bottom edge, at
    its mid-depth - rotated -20 degrees about X so it folds down and OUT. One of its four units is
    buried up inside the plate, the horns' trick for closing a rotated joint. It is a flap and not a
    wedge: one unit thick, and 5 wide against the plate's 8, so it hangs from the middle of the sill
    and leaves two columns of the plate's underside showing at each end.

The profile is the whole design: the brow juts (z -7.75), the sight recedes (z -7), the chin comes
back out furthest of anything here (the lip's leading corner at z -7.761, 0.011 past the bar). Head
on, none of that shows - vanilla's diffuse term shades by normal alone, so a face parallel to the
face behind it is lit identically, which is the greaves' finding. So the relief is modelled for the
profile and PAINTED for the front: the plate's `north` is banded field / gutter / keel / gutter /
field across, and shadow / field / sight / sill down. The keel is 2 wide on an 8-wide plate and
therefore covers columns 3 and 4 exactly - an even rib on an even host, which is the case the
greaves' "an odd rib wants an odd host" was the failure of.

THE SIGHT, AND WHAT IS BEHIND IT
--------------------------------
The slot is punched in alpha, the way `spurs` punches its rowel star, and the same warning applies
with more force: parts draw with armorCutoutNoCull, so a hole shows whatever is behind it including
the far side of the cube it was cut in. Three things make this hole legal, and a fourth measures the
only thing that stands in it.

  * **The plate is one unit thick.** The cut is taken on `north` and `south` at the same rows, so the
    two holes line up and there is no interior to look at - the heel_wings' argument. A 2-deep plate
    would have shown the slot's own tunnel walls lit as exterior faces.
  * **The cut does not reach the ends.** It spans head x -3..3 of the plate's -4..4, so `east` and
    `west` stay solid and there is a full texel of plate at each end of the slot. A full-width slot
    would have severed the plate into two floating slabs, since nothing in the silhouette would join
    the brow to the sill.
  * **What is behind it is air and then the helmet.** Directly behind the sight is the 1-unit gap
    between the plate's back face at z = -6 and the helmet shell's front wall at z = -5, and the
    only cube of this part anywhere near that sight line is the lip, whose top surface passes
    **0.118 below the slot's bottom edge** at the plate's back plane and falls away to 0.317 below it
    at z = -5.453, where the flap's own back edge ends the surface half a unit short of the wall. So
    the sight looks at helmet, in shadow, which is what a sight looks at.
  * **The one thing standing in the tunnel is the lip's own fold, by 0.025.** The flap's top front
    edge rises to head y -3.025 while it is still inside the plate's thickness, at z -6.393 - a
    fortieth of a unit above the slot's bottom edge at y = -3, which on a texture where one unit is
    one row is two and a half percent of the bottom row. Everything it shows there is painted INNER,
    so it reads as the dark bottom of the slot rather than as a thing standing in it.

Everything the sight opens onto is painted INNER, and that is a judgement rather than a measurement:
the dead pocket between the plate and the helmet is sealed in front by the plate, behind by the
helmet, above by the 4-deep bar and below by the lip as far back as z = -5.453, and the sight is the
one hole into it worth the name. The last half unit of the pocket floor is open, but it opens
downward onto the helmet's own front wall coming past the jaw, so what is under there is the same
shell that closes the back. A sliver of the pocket can be seen through the slot from above. INNER is
56, which is the value that sliver wants anyway.

CLEARANCES, ALL AGAINST THE HELMET IT IS BOLTED TO
--------------------------------------------------
  * Envelope head x -4..4, y -7.60..1.08, z -7.76..-3.75; reach 6.54 from the anchor. In x it is
    entirely inside the 1.0-inflate helmet's own outline (x +-5) with 1.0 of margin at each side, and
    it clears the crown by 1.4. The one thing that leaves the outline is the chin lip's lowest
    corner, at y 1.076 against the helmet's bottom plane at y = 1 - 0.08 below it, and 1.8 units in
    front of the shell at z -6.82, where there is no helmet left to overhang. A chin lip that stops
    above the jaw is a moustache, so the flap is allowed the eighth of a unit; everything else this
    part adds to the silhouette is depth, which is the feathering's footprint lesson applied to a
    faceplate: a visor wider than the helmet is not a visor.
  * Projection past the helmet wall: 2.76 at the lip's leading corner, 2.75 at the bar, 2.5 at the
    keel, 2.0 at the plate - against the circlet's stone at 2.0 and the horns' 3.5, which is the
    head's established ceiling.
  * `horns` and `helm_wings` put a boss at head x 4..7, y -8..-5, z -2..2. This part stops at x = 4
    and at z = -3.75, so it misses the boss on two axes at once and by construction: it never
    reaches the temples in x, and it never reaches the ears in z. The lip, the only cube that swings,
    is the narrowest of the four and stops at x +-2.5.
  * `feathering` and `brush_crest` mount at head y <= -8 over z -3..3 and -3.5..3.5. The topmost face
    here is the bar's at y = -7.6, and the backmost is the bar's at z = -3.75 - clear of the crest
    parts in y by 0.4 and in z by 0.25, so the two never meet even though a player wears both.
  * Head pitch. The lip's lowest corner sits at head (y 1.076, z -6.821), radius 6.906 about the head
    pivot, and crosses the chestplate's front plane at z = -3 at **55.3 degrees** of look-down. The
    head box's own bottom-front edge crosses it at 41.4 and the 1.0-inflate helmet's at 42.7. The
    part is therefore the last thing in that region to be swallowed rather than the first, which is
    the standard `wing_roots` and `brooch` set for anything living near the neck.
  * The collar parts, on the body bone rather than this one. The chin hangs past the jaw - y 1.076
    against the head box's own bottom at y = 0 - which puts it inside the band the `gorget` and the
    `brooch` occupy in y, and the two are worn with this one. They are missed in depth instead, which
    is the axis this whole part lives on: the lip's backmost face is at z -5.45 against the gorget's
    frontmost at -3.75 and the brooch's at -4.75, so 1.70 and 0.70 of air at rest, and the brooch is
    a further 3.4 below in y besides.

FACE LAYOUT
-----------
The rectangles come from paint_circlet_master.faces(), copied verbatim: row one (v .. v+d) holds up
then down, each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west, south with
widths d, w, d, w. Note the row-two order - the two thin d-wide faces come FIRST and THIRD.

Orientation inside each rectangle is the table PLAN.md records as measured, not recalled:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x              max z
    down            +y  (underside)      min x              max z
    west            +x  (outboard)       min z  (front)     min y (top)
    east            -x  (inboard)        max z  (back)      min y (top)
    north           -z  (front)          min x              min y (top)
    south           +z  (back)           max x              min y (top)

This painter does not hand-index against that table, though - it *uses* it. Every pixel of every
face is turned into a point in head space, and both the burial mask and the alpha cut are decided
from that point. Two things fall out that the earlier painters had to get right by hand: the sight
punches identically on `north` (which counts x up) and `south` (which counts x down) because it is
specified as a band of head x, not as a range of columns; and a face pixel is INNER exactly when its
own centre is inside something, which is how the plate's top row, the four middle columns of the
plate's underside that the chin lip hangs under, the bar's buried depth rows and the lip's whole `up`
face get their values without a per-face burial table.

The one thing that is NOT derived: this part is centred on the body midline and is not a mirrored
pair, so there is no outboard flank to light and no inboard one to shade. Any left-right lean would
read as an asymmetry rather than as a light direction, so every value here is a function of row, not
of column, apart from the keel's two gutters - which are symmetric.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "visor.json"
OUT = ROOT / "tools" / "decoration_masters" / "visor.png"

TEX_W, TEX_H = 64, 32

# DecorationAnchor.BROW - Attachment.of(HEAD, 0, -4, -4). Not parsed, but asserted against the trace:
# every head-space number in this file is anchor + the geometry's own local origin.
ANCHOR = (0.0, -4.0, -4.0)

# size (w, h, d) and uv (u, v), mirroring visor.json in that file's own order (the three cubes of the
# `visor` bone, then the `lip` child's). check_geometry() asserts this, and asserts the origins below.
CUBES = {
    "plate": ((8, 5, 1), (0, 0)),
    "bar":   ((6, 2, 4), (20, 0)),
    "keel":  ((2, 2, 1), (42, 0)),
    "lip":   ((5, 4, 1), (3, 9)),
}

# Each cube's origin in its own bone's local frame, again mirroring visor.json.
ORIGIN = {
    "plate": (-4.0, -3.0, -3.0),
    "bar":   (-3.0, -3.6, -3.75),
    "keel":  (-1.0, -2.0, -3.5),
    "lip":   (-2.5, -1.0, -0.25),
}

LIP_PIVOT = (0.0, 2.0, -2.5)   # local to the `visor` bone, i.e. head (0, -2, -6.5)
LIP_ROT_X = -20.0              # negative pitches the lip's free end DOWN and FORWARD, away from the face

# The sight, specified as a band of head space rather than as pixel indices, so that the cut lands on
# `north` and `south` identically without either one being hand-mirrored.
SIGHT_TOP, SIGHT_BOTTOM = -4.0, -3.0   # head y; the top edge is the BROW anchor's own plane
SIGHT_HALF_W = 3.0                     # head |x| < 3, one full texel of plate left at each end

# The 1.0-inflate helmet shell over the head bone, and the dead pocket between the plate and it.
# Burial in the shell is free and permanent here for the reason it is on the circlet and the horns:
# part and shell ride the same bone, so a buried face never uncovers.
HELMET = ((-5.0, -9.0, -5.0), (5.0, 1.0, 5.0))
POCKET = ((-4.0, -7.6, -6.0), (4.0, -2.0, -5.0))

random.seed(29)  # deterministic output - regenerating must not churn the PNG

# Calibrated against the ramp, not guessed. the material ramp interpolates dark -> mid over
# master values 0..127 and mid -> light over 128..255, so a master confined to one half only ever
# uses half of a material's ramp. The buried faces at INNER and the gutters under 127 are what keep
# this one honest on netherite.
FACE = 196      # `north` - on a faceplate this is the part, and everything else is edge
UP = 238        # a top face standing proud of the helmet
DOWN = 34       # an underside
FLANK = 146     # `east`/`west`, the edges seen in profile
INNER = 56      # buried: in the helmet shell, in another cube of the part, or in the dead pocket

BAR_GAIN = 22   # the bar is the proudest thing on the part and reads brightest
KEEL_GAIN = 36  # the nasal ridge, which has to beat the plate behind it at 2 pixels wide
LIP_GAIN = 26   # the lip's face tilts 20 degrees toward the sky, so it catches more than the plate
GUTTER = -76    # the shadow column each side of the keel - the greaves' five-band read
BROW_SHADE = -52  # the plate's row under the bar's overhang
SILL = -40      # the row under the sight, falling away toward the fold
POST = -18      # the sight's two end posts, dropped so the slot's ends read as ends
RIM = 26        # the lit chamfer along a free top edge
FALL = 18       # top-to-bottom falloff down a standing face


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


# --- geometry, in head space --------------------------------------------------------------------

def bounds(name):
    """A cube's (lo, hi) in its own bone's frame."""
    (w, h, d), _ = CUBES[name]
    o = ORIGIN[name]
    return o, (o[0] + w, o[1] + h, o[2] + d)


def to_head(name, p):
    """A point in a cube's own bone frame, in head space. Only the lip's bone is rotated."""
    if name != "lip":
        return (ANCHOR[0] + p[0], ANCHOR[1] + p[1], ANCHOR[2] + p[2])
    a = math.radians(LIP_ROT_X)
    c, s = math.cos(a), math.sin(a)
    y, z = p[1] * c - p[2] * s, p[1] * s + p[2] * c
    return (ANCHOR[0] + LIP_PIVOT[0] + p[0],
            ANCHOR[1] + LIP_PIVOT[1] + y,
            ANCHOR[2] + LIP_PIVOT[2] + z)


def to_local(name, p):
    """The inverse of to_head - a head-space point in a cube's own bone frame."""
    if name != "lip":
        return (p[0] - ANCHOR[0], p[1] - ANCHOR[1], p[2] - ANCHOR[2])
    a = math.radians(-LIP_ROT_X)
    c, s = math.cos(a), math.sin(a)
    dx = p[0] - ANCHOR[0] - LIP_PIVOT[0]
    dy = p[1] - ANCHOR[1] - LIP_PIVOT[1]
    dz = p[2] - ANCHOR[2] - LIP_PIVOT[2]
    return (dx, dy * c - dz * s, dy * s + dz * c)


def sample(name, face, i, j):
    """The head-space centre of one face pixel, and that face's outward normal in head space.

    The (column, row) -> (axis, direction) mapping is the measured table in the module docstring. The
    normal is carried along because the burial test pushes off the surface before asking what
    contains it - a face pixel sitting exactly on another cube's wall is not buried by it."""
    lo, hi = bounds(name)
    table = {
        "up":    ((lo[0] + i + 0.5, lo[1], hi[2] - j - 0.5), (0.0, -1.0, 0.0)),
        "down":  ((lo[0] + i + 0.5, hi[1], hi[2] - j - 0.5), (0.0, 1.0, 0.0)),
        "east":  ((lo[0], lo[1] + j + 0.5, hi[2] - i - 0.5), (-1.0, 0.0, 0.0)),
        "north": ((lo[0] + i + 0.5, lo[1] + j + 0.5, lo[2]), (0.0, 0.0, -1.0)),
        "west":  ((hi[0], lo[1] + j + 0.5, lo[2] + i + 0.5), (1.0, 0.0, 0.0)),
        "south": ((hi[0] - i - 0.5, lo[1] + j + 0.5, hi[2]), (0.0, 0.0, 1.0)),
    }
    p, n = table[face]
    origin = to_head(name, p)
    tip = to_head(name, (p[0] + n[0], p[1] + n[1], p[2] + n[2]))
    return origin, tuple(tip[a] - origin[a] for a in range(3))


def inside(p, lo, hi, eps=1e-6):
    return all(lo[a] + eps < p[a] < hi[a] - eps for a in range(3))


def buried(name, face, i, j):
    """Is this face pixel's centre inside something that hides it?

    Three kinds of thing, and all three are permanent because every one of them rides the head bone
    with the part: the helmet shell, another cube of this part, and the dead pocket between the plate
    and the helmet wall. The point is pushed 0.02 along its own outward normal first, which is the
    method the tassets used - without it a face lying against another cube's wall reads as buried by
    the cube it is flush with rather than by the cube in front of it."""
    p, n = sample(name, face, i, j)
    q = tuple(p[a] + 0.02 * n[a] for a in range(3))
    if inside(q, *HELMET) or inside(q, *POCKET):
        return True
    for other in CUBES:
        if other == name:
            continue
        lo, hi = bounds(other)
        if inside(to_local(other, q), lo, hi):
            return True
    return False


def cut(name, face, i, j):
    """Is this face pixel part of the sight slot?

    Specified as a band of head space, so `north` (which counts x up) and `south` (which counts x
    down) cut the same six columns without either being written out. The plate's `east` and `west`
    are 1 x 5 and lie outside the band in x, so they are never touched, which is what keeps the two
    halves of the plate joined."""
    if name != "plate" or face not in ("north", "south"):
        return False
    p, _ = sample(name, face, i, j)
    return SIGHT_TOP < p[1] < SIGHT_BOTTOM and abs(p[0]) < SIGHT_HALF_W


# --- values -------------------------------------------------------------------------------------

def ramp(i: int, n: int) -> float:
    """Position along a face axis, 0.0 at column/row 0 and 1.0 at the far end."""
    return 0.0 if n <= 1 else i / (n - 1)


def plate_value(face, i, j, w, h):
    """The faceplate. Its `north` is the part, and it is banded in both directions.

    Down the face: the top row lives under the bar's overhang and is dropped 52; the second is the
    lit brow; then the sight; then a sill dropped 40, which exists to be the dark half of the fold -
    the lip's own first exposed row comes back up 86 above it, and that step is the only thing that
    says the lower plate is angled, since a tilted face parallel-projected from the front is not.

    Across it: the keel covers columns 3 and 4 exactly, so those two are buried and columns 2 and 5
    are its gutters at -76. Columns 0 and 7 are the plate's shoulders, outboard of both the bar and
    the keel and the only part of the top rows that is seen at all.

    `down` is the sill's underside. The chin lip hangs from the middle of it and is 5 wide on this
    cube's 8, so buried() takes columns 2 through 5 and leaves two at each end - the only place on
    the part where the plate is seen from below."""
    if face == "north":
        gutter = GUTTER if i in (2, w - 3) else 0
        if j == 0:
            return FACE - 20 + gutter           # only columns 0 and 7 survive the bar; see buried()
        if j == 1:
            return FACE + BROW_SHADE + gutter
        if j == 2:
            return FACE + gutter
        if j == 3:
            return FACE + POST                  # the sight's end posts; the middle six are cut
        return FACE + SILL
    if face == "south":
        return INNER                            # into the pocket; buried() catches it anyway
    if face == "up":
        return UP
    if face == "down":
        return DOWN + 10
    # east / west: a 1 x 5 edge seen in profile, chamfered at the top and falling away.
    return FLANK + (RIM if j == 0 else -round(FALL * ramp(j, h)))


def bar_value(face, i, j, w, h):
    """The brow reinforce. Four deep, of which 2.75 stands in front of the helmet and the last unit
    is inside the head box, so its `up` and flank rows walk out of the shell as they come forward -
    which buried() decides row by row rather than this function guessing.

    `up` brightens toward the leading edge because that edge is the part's horizon from any angle
    above the eyeline, and it is the only place on the visor where a top face is more than one pixel
    deep."""
    if face == "north":
        return FACE + BAR_GAIN + (RIM if j == 0 else -FALL)
    if face == "up":
        return UP - 16 + round(16 * ramp(j, h))   # row 0 is the BACK; the front row is the brightest
    if face == "down":
        return DOWN + 10
    if face == "south":
        return INNER
    # east / west: 4 deep x 2 tall, the flank of the overhang.
    return FLANK + 14 + (RIM if j == 0 else -FALL) - round(10 * ramp(i, w))


def keel_value(face, i, j, w, h):
    """The nasal ridge: two pixels wide, so it is a value against its neighbour and nothing else.

    It runs 232 against gutters at 120 on the plate behind it - the brooch's rule at the size the
    brooch found it. Its own top row is shaded because 0.4 of that row is up inside the bar."""
    if face == "north":
        return FACE + KEEL_GAIN - (30 if j == 0 else 0)
    if face == "down":
        return DOWN + 6                         # the dark line directly above the sight
    if face in ("up", "south"):
        return INNER
    return FLANK + 20 - (24 if j == 0 else 0)


def lip_value(face, i, j, w, h):
    """The chin lip, on the only rotated bone in the part.

    Its `north` normal tilts 20 degrees skyward, so it takes more light than the vertical plate and
    is painted 26 above it, with the fold row rimmed a further 26. That first exposed row lands at
    242 against the plate's sill at 156 directly above it - an 86-point step, and the whole reason
    the sill is dark: at this size an angle is a pair of values, not a shape. Three more rows fall
    away below it to 204 at the free bottom edge.

    Row 0 of every standing face here is buried up inside the plate - one of the lip's four units
    is, which is the horns' rule that a rotated joint is closed by burial rather than by butting.
    `up` is buried along its whole length: it is the floor of the dead pocket, and the only thing on
    the part that the sight could ever look at. The flap is one unit deep, so `down` and the two flanks are a
    single pixel across; there is no depth left to gradient and they carry the row falloff alone."""
    if face == "north":
        return FACE + LIP_GAIN + (RIM if j == 1 else 0) - round(FALL * ramp(j, h))
    if face == "down":
        return DOWN + 4
    if face in ("up", "south"):
        return INNER
    return FLANK + 8 - round(FALL * ramp(j, h))


VALUES = {"plate": plate_value, "bar": bar_value, "keel": keel_value, "lip": lip_value}


def put(img, x: int, y: int, lum: int) -> None:
    if 0 <= x < TEX_W and 0 <= y < TEX_H:
        img.putpixel((x, y), (max(0, min(255, lum)), 255))


def paint(img) -> set:
    """Every face of every cube, one pixel at a time. Returns the set of pixels the sight cut."""
    removed = set()
    for name, (size, uv) in CUBES.items():
        value = VALUES[name]
        for face, (x0, y0, fw, fh) in faces(size, uv).items():
            for j in range(fh):
                for i in range(fw):
                    if cut(name, face, i, j):
                        removed.add((x0 + i, y0 + j))
                        continue
                    lum = INNER if buried(name, face, i, j) else value(face, i, j, fw, fh)
                    put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))
    return removed


# --- checks ---------------------------------------------------------------------------------------

def check_geometry() -> None:
    """CUBES, ORIGIN, the lip's pivot and its rotation must be the shipped geometry's own.

    Painting a texture for a shape the model no longer has is invisible to every other check in this
    pipeline: bb_geo roundtrip checks the model against itself and check_layout checks the master
    against itself, and both keep passing while the rectangles slide off the faces they were drawn
    for. This part needs the stronger version of the assertion than the earlier painters' (size, uv)
    one, because its burial mask and its alpha cut are both computed from the ORIGINS - a cube that
    moved half a unit would silently re-decide which pixels are buried and where the sight lands."""
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
    mine = [(ORIGIN[n], CUBES[n][0], CUBES[n][1]) for n in CUBES]
    assert found == mine, f"this painter disagrees with {GEO.name}: {found} vs {mine}"

    lip = doc["bones"][0]["children"][0]
    assert tuple(lip["pivot"]) == LIP_PIVOT, f"lip pivot moved: {lip['pivot']} vs {LIP_PIVOT}"
    assert tuple(lip["rotation"]) == (LIP_ROT_X, 0, 0), \
        f"lip rotation moved: {lip['rotation']} vs {(LIP_ROT_X, 0, 0)}"


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


def check_sight() -> None:
    """The slot must be a slot: one row tall, six columns wide, cut on exactly two faces, and cut on
    both of them at the same six columns of the plate.

    That last clause is the one worth asserting rather than reading. `north` counts x upward and
    `south` counts it downward, so the two rectangles are mirror images; a cut written as column
    indices agrees with itself only by luck, and the failure - a slot whose two halves are offset -
    is invisible in the master and only appears as a shard of daylight on a model. Here the cut is
    specified in head space and this asserts the consequence."""
    (w, h, d), uv = CUBES["plate"]
    cols = {}
    for face in ("up", "down", "east", "north", "west", "south"):
        fw, fh = faces((w, h, d), uv)[face][2:]
        hits = [(i, j) for j in range(fh) for i in range(fw) if cut("plate", face, i, j)]
        if face in ("north", "south"):
            assert len({j for _, j in hits}) == 1, f"the sight is not one row on {face}"
            cols[face] = sorted(i for i, _ in hits)
        else:
            assert not hits, f"the sight must not reach {face} - it would sever the plate"
    assert cols["north"] == cols["south"] == [1, 2, 3, 4, 5, 6], \
        f"the two halves of the slot disagree: {cols}"
    for name in CUBES:
        if name == "plate":
            continue
        for face, (_, _, fw, fh) in faces(*CUBES[name]).items():
            assert not any(cut(name, face, i, j) for j in range(fh) for i in range(fw)), \
                f"{name} must not be cut - only the plate carries the sight"


def lip_top(depth):
    """The head y of the lip's top surface at a head depth, or None where the lip is not there.

    The surface is the lip's local y = lo[1] plane, tilted -20 degrees, so a head depth picks out one
    local z on it; a depth the flap does not span has no answer rather than a wrong one."""
    lo, hi = bounds("lip")
    a = math.radians(LIP_ROT_X)
    c, s = math.cos(a), math.sin(a)
    z_local = (depth - ANCHOR[2] - LIP_PIVOT[2] - lo[1] * s) / c
    if not lo[2] <= z_local <= hi[2]:
        return None
    return ANCHOR[1] + LIP_PIVOT[1] + lo[1] * c - z_local * s


def check_sight_line() -> None:
    """Nothing of this part may cross the open sight line, and the lip is the only candidate.

    The line is horizontal, at the slot's own height, from the plate's back face at head z = -6 to
    the helmet wall at z = -5. The lip's top surface passes under it wherever it exists: 0.118 below
    the slot's bottom edge where the surface starts, falling to 0.317 by z = -5.453, where the flap's
    own back edge ends it half a unit short of the wall. Swept rather than sampled at the two ends,
    because the flap covers only the front half of that line, and an end-point test on a surface
    that stops partway is a test that can pass by not being taken.

    The second assertion is the tunnel's, and it is the fold's own doing. The fold rises to head
    y -3.025 while still inside the plate's own thickness, which is 0.025 above the slot's bottom
    edge - a fortieth of a row. That is a sliver, painted INNER like everything else the slot opens
    onto; a tenth of a row would be a shape standing in the sight. Both numbers are
    asserted rather than stated because the lip's -20 degrees is the number most likely to be tuned
    in pass A, and the first thing a steeper fold would do is lift the flap into the sight."""
    assert lip_top(-6.0) is not None, "the lip's top surface must start at the plate's back plane"
    for step in range(21):
        depth = -6.0 + 0.05 * step
        head_y = lip_top(depth)
        if head_y is None:
            continue
        assert head_y > SIGHT_BOTTOM + 0.1, \
            f"the lip's top surface reaches head y {head_y:.3f} at z {depth:.2f}, into the sight"

    fold = to_head("lip", (0.0, bounds("lip")[0][1], bounds("lip")[0][2]))
    intrusion = SIGHT_BOTTOM - fold[1]
    assert intrusion < 0.1, \
        f"the lip's top front edge stands {intrusion:.3f} into the slot's bottom row"
    if intrusion > 0:
        plo, phi = bounds("plate")
        assert plo[2] < to_local("plate", fold)[2] < phi[2], \
            "the lip's top front edge enters the sight outside the plate's own thickness"


def main() -> None:
    check_geometry()
    check_sight()
    check_sight_line()
    claimed = check_layout()

    img = Image.new("LA", (TEX_W, TEX_H), (0, 0))
    removed = paint(img)

    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque == set(claimed) - removed, \
        "the painted silhouette is not the rectangles minus the sight"
    assert len(removed) == 12, f"the sight should be 2 faces x 6 pixels, cut {len(removed)}"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    dark = sum(1 for v in lums if v < 127)
    print(f"wrote {OUT} ({len(opaque)} opaque px, {len(removed)} cut by alpha, "
          f"values {min(lums)}-{max(lums)}, {100 * dark // len(lums)}% under 127)")


if __name__ == "__main__":
    main()
