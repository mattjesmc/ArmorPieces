"""
Paint the grayscale master for the "brush_crest" part.

Like the brooch, sash, tassets, spurs and greaves painters this does not merely claim that CUBES
matches the shipped geometry, it reads
assets/armorpieces/armorpieces/decoration/brush_crest.json at run time and asserts it - and it goes
one step further than those five, because half of this part's shading is decided by *where the cubes
are* rather than by how big they are: check_geometry() therefore also asserts the composed pivots,
the rotations and the pivot-relative origins in PLACEMENT below. Output goes to
tools/decoration_masters/brush_crest.png, which sync_decoration_masters.py installs for the game
to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

**This master is 100% opaque, and that is the design rather than a shortcut.** The feathering shares
this socket and carves its silhouette out of alpha, because a plume is a fringe and its blade is one
unit thick, so a hole punched through it shows the far side's own face and costs nothing. This part
is the opposite object on both counts. A legionary's crest is a *dense* brush - the fiction is that
there is no air in it - and its bristle mass is two units thick, so under armorCutoutNoCull a hole
cut in the top row would show the inside of the block rather than the sky. That is the circlet's
finding, and it applies here for the circlet's reason. Everything below is value.

--------------------------------------------------------------------------------------------------
What the part is, in numbers, and why they differ from the feathering's

Both parts hang off CREST, `Attachment.of(HEAD, 0, -8, 0)` - the top plane of the 8-tall head box -
so part-local y = 0 is the skull's crown, y = -1 is the 1.0-inflate helmet's own top, and negative y
is up. They are alternatives on one socket and are judged against each other, so every proportion
here was chosen against the feathering's traced numbers rather than against nothing:

                                  feathering        brush_crest
    top, above the head's crown       13.04                7.00
    top, above the helmet              12.04                6.00
    envelope depth (z)                12.52 (-3 .. 9.52)    9.32 (-4.66 .. 4.66)
    envelope width (x)                 2.00                3.00
    reach from the anchor             14.29                7.68
    height : depth                     1.04                0.75

So this one is a hair over half the feathering's height and its reach (0.537 of each, to three
places), one unit wider, and it is the only thing standing on the crown of the head that is longer
than it is tall. That ratio is the whole read: the feathering is a vertical spray with a rising tail,
this is a horizontal ridge. It tops out 0.64 above the horns' 6.36, which is the intended order - a
crest should just clear the horns beside it and be nowhere near the plume.

**The depth ceiling used here is the helmet's, not the head's, and that is a deliberate departure.**
PLAN.md's feathering finding is that overhanging the head's own 8-unit footprint is what made a
*tall* plate read as a banner, and the fix was to pull its depth to 7. A low ridge is not that
object: what would make this one read wrong is being short front-to-back, because a stubby brush is a
shaving brush. The ceiling that actually binds a part sitting on a helmet is the helmet's own 10-unit
footprint, and 9.32 is inside it by 0.34 at each end - so in profile the crest never breaks the
helmet's silhouette even though it does break the skull's. Reversible: dropping RAKE to 40 deg pulls
the tips back to +-4.53 and costs nothing else.

The four cubes, in geo units relative to the anchor:

  mount            x -1.5..1.5, y -3..0,      z -3.5..3.5
        The metal channel the brush is socketed into. It straddles the helmet wall exactly as the
        circlet's band does - 2 units of it stand above the helmet's top plane at y = -1 and 1 unit
        is buried inside the shell - which buys no coplanar face against the helmet anywhere and
        slack if CREST moves in pass A. Its down face lies on the head box's own crown at y = 0; that
        is the harmless case (it is under the opaque helmet shell) and trace_geometry prints it as a
        note, the same note the feathering's socket earns.

  brush            x -1..1,     y -7..-2,     z -3..3
        The bristle mass. Two units thick against the feathering blade's one, which is the single
        cheapest way to say "dense" - and it buries its bottom unit in the mount rather than sitting
        on it, so no face of this part touches a face of the mount. No two cubes here share a plane
        in ANY axis: x +-1.5 / +-1 / +-0.5, y {-3, 0} / {-7, -2}, z +-3.5 / +-3. That is the sash's
        rule, which needed stating because an X-rotated chain cannot separate its x planes for you.

  nose_front       x -0.5..0.5, y 0..4 local, z -2..0 local, pivot (0, -7, -3), rotation +34 deg
  nose_rear        mirrored in z about the part's own centre, rotation -34 deg
        The raked ends. Their pivot is the brush's top-front (and top-back) EDGE, and the cube hangs
        entirely on the far side of it, which is the one placement where the horns' burial trick is
        not needed: rotating about a pivot on the parent's top plane lifts anything on the near side
        of it *above* that plane, and a 1-unit burial in +z would have poked 0.56 out through the
        ridge. Instead the near end of the fold rotates INTO the mass - every point of the cube's
        near face maps to part-local z > -3 - so the joint is closed by the rotation itself. Verified
        by the sampler below rather than by assertion: the whole `down` face and the whole near end
        face come back 0% visible.

  The rake is 34 deg over 2 units of run, so each end drops 1.12 and reaches 1.66 further out. The
  top is dead flat over z -3..3, which is 6 of the ridge's 9.32 units - straight-topped, with clipped
  ends, which is what a crista is and what a plume is not.

The part is symmetric in z. That is a judgement call and it is reversible: a real crest often runs
slightly higher at the front, but a symmetric ridge reads identically from both profiles, is the
pose this socket is actually seen in, and it lets the fore-aft bristle comb below be symmetric about
the centreline instead of walking off one end.

--------------------------------------------------------------------------------------------------
How the shading is decided

The face rectangles come from paint_circlet_master.faces(), copied verbatim: row one (v .. v+d) holds
up then down, each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west, south
with widths d, w, d, w - the two thin d-wide faces FIRST and THIRD.

Orientation inside each rectangle is PLAN.md's measured table:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x              max z
    down            +y  (underside)      min x              max z
    west            +x                   min z  (front)     min y (top)
    east            -x                   max z  (back)      min y (top)
    north           -z  (front)          min x              min y (top)
    south           +z  (back)           max x              min y (top)

This part is the case that table exists for. CREST is a single, unmirrored attachment, so `west` and
`east` are the two big profile faces - one seen from the player's left, one from the right - and they
run in OPPOSITE fore-aft directions. Everything on them is a fore-aft pattern, so painting both with
the same loop would put the comb half a bundle out of step between the two sides, which is exactly
the failure the feathering's second cut was re-structured to avoid. Nothing here indexes a face by
column: every texel is resolved to a *fore-aft position on the part's own axis* first, and the value
is a function of that. The same call makes the comb line up around the corner onto `up`, which is the
horns' ring trick spent on stripes rather than grooves.

    axial(cube, z_local) = the cube's pivot z + its own local z

is used rather than the rotated part-local z, so that the comb keeps its pitch along the bristles as
they fold over the nose instead of bunching up by cos 34.

**The bundles are the form; a flat brush is a paddle.** bristle() puts a bundle wherever
floor(|axial|) is even, which is period 2 and symmetric about z = 0, giving five bundles and five
gullets over the ridge's ten units - and a bundle and a gullet get two *different* top-to-bottom
gradients (226 -> 78 and 150 -> 24) rather than one gradient plus an offset, so the gullet is darker
at every height and never clips at the root. On the `up` faces the same split runs 246 against 148,
which is the deepest contrast on the part: the top is the face that has to say "bristles" at a
glance, and the spurs' finding is that a form at this size is a value against its neighbour.

**Burial is measured, not eyeballed.** The tassets established the method and this part needs it
more than that one did, because a rotated nose folding through its own parent's face does not have a
row-by-row answer. visible_fraction() samples each texel on a 4x4 grid, pushes each sample 0.06 along
that face's outward normal, transforms it into part-local space and tests it against the 1.0-inflate
helmet shell (part-local x +-5, y -1..9, z +-5) and against every other cube of the part, rotations
included. The fraction that survives then picks the value: at or above 0.45 the face's own shading,
below 0.10 flat INNER, and in between a lerp toward INNER. Three of the masks that falls out of are
worth naming, because none of them is obvious from the cube list:

  * the mount's `up` face is 3 wide against the brush's 2, so its two outer columns come back ~50%
    visible along their whole length - half a unit of flange each side - while the middle column is
    buried except at its two ends. The rim reads, the middle does not, and neither was hand-masked.
  * the brush's `north` and `south` are each half-covered by a nose that is 1 wide on a 2-wide face,
    which is the greaves' "a 1-wide rib cannot be centred on an even host" arriving as an occluder
    instead of as a rib. They come back ~50% and are painted as the dimmed cut end of the mass.
  * on a nose's `west`/`east` the sampler returns 1.00 / 0.94 / 0.31 / 0.00 down the tip column and
    0.69 / 0.06 / 0.00 / 0.00 down the near one - two clean rows, one dimmed, the rest gone - and it
    puts them in whichever column each actually lands on, which is the reversed one on `east`.

The buried texels are painted at INNER rather than left dark for the reason every part since the
circlet has: CREST is a first-draft offset and pass A may move it, and a buried row that uncovers is
cheaper to have already painted than to notice in game.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "brush_crest.json"
OUT = ROOT / "tools" / "decoration_masters" / "brush_crest.png"

TEX_W, TEX_H = 64, 32

RAKE = 34.0  # degrees of fold at each end of the ridge; see the module docstring

# size (w, h, d) and uv (u, v), mirroring brush_crest.json in that file's own bone order.
CUBES = {
    "mount":      ((3, 3, 7), (0, 0)),
    "brush":      ((2, 5, 6), (20, 0)),
    "nose_front": ((1, 4, 2), (36, 0)),
    "nose_rear":  ((1, 4, 2), (42, 0)),
}

# Where each cube actually sits, which the shading needs and CUBES cannot say: `pivot` is the bone's
# origin COMPOSED down the chain into part-local space (the anchor's own frame, +Y down, y = 0 the
# skull's crown), `rot` its X rotation in degrees, `origin` the cube's pivot-relative corner. Every
# rotation on this part is about X, so composing a chain is one 2-D rotation in the y-z plane and the
# angles add - check_geometry asserts all three columns against the geometry file, and asserts that
# no bone carries a Y or Z rotation, since the rest of this module assumes it.
PLACEMENT = {
    "mount":      {"pivot": (0.0, 0.0, 0.0),   "rot": 0.0,    "origin": (-1.5, -3.0, -3.5)},
    "brush":      {"pivot": (0.0, -3.0, 0.0),  "rot": 0.0,    "origin": (-1.0, -4.0, -3.0)},
    "nose_front": {"pivot": (0.0, -7.0, -3.0), "rot": RAKE,   "origin": (-0.5, 0.0, -2.0)},
    "nose_rear":  {"pivot": (0.0, -7.0, 3.0),  "rot": -RAKE,  "origin": (-0.5, 0.0, 0.0)},
}

# The 1.0-inflate helmet shell in part-local coordinates. The head box is geo (-4, -8, -4) size 8 and
# CREST sits on its crown at (0, -8, 0), so head y maps to part-local y + 8: the shell's own top
# plane, geo y = -9, is part-local y = -1. The naked head box is strictly inside this and needs no
# separate entry - anything buried in the skull is buried in the helmet first.
HELMET = ((-5.0, -1.0, -5.0), (5.0, 9.0, 5.0))

random.seed(73)  # deterministic output - regenerating must not churn the PNG

# Calibrated against the ramp, not guessed. the material ramp interpolates dark -> mid over
# master values 0..127 and mid -> light over 128..255, so a master confined to one half only ever
# uses half of a material's ramp - the trap the circlet's first cut fell into and the feathering's
# shipped master was found to be sitting in. These run 24 at a gullet's root to 246 at a bundle's tip.
TIP = 246           # `up` on a bristle bundle - the top of the ridge, the part's brightest value
TIP_GULLET = 148    # `up` in the comb between two bundles
BUNDLE_HI = 226     # a flank at the ridge line ...
BUNDLE_LO = 78      # ... and at the root, where the mount's shadow is
GULLET_HI = 150     # the same two, one comb line over
GULLET_LO = 24
END_HI = 196        # the cut end of the bristle mass, top ...
END_LO = 52         # ... and bottom
FLANGE = 238        # the half unit of the mount's top face the brush does not cover
BAND_HI = 204       # the mount's chamfered upper row, geo y -3..-2
BAND_LO = 92        # its lower row, y -2..-1, the last unit above the helmet
PIN = 66            # a mounting pin, added to whichever row of the mount it lands on
INNER = 44          # buried - in the helmet, in the mount, or in the bristle mass

FULL, GONE = 0.45, 0.10  # the visibility fractions at which a texel is fully lit / fully buried

# Face frames in a cube's own bone-local space: the rectangle's (0, 0) corner, the step per texel
# column, the step per texel row, and the outward normal. This IS the measured orientation table
# above, written as arithmetic so that no loop in this file has to remember which way it runs.
FACE_FRAMES = {
    "up":    lambda w, h, d: ((0, 0, d), (1, 0, 0), (0, 0, -1), (0, -1, 0)),
    "down":  lambda w, h, d: ((0, h, d), (1, 0, 0), (0, 0, -1), (0, 1, 0)),
    "west":  lambda w, h, d: ((w, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0)),
    "east":  lambda w, h, d: ((0, 0, d), (0, 0, -1), (0, 1, 0), (-1, 0, 0)),
    "north": lambda w, h, d: ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, -1)),
    "south": lambda w, h, d: ((w, 0, d), (-1, 0, 0), (0, 1, 0), (0, 0, 1)),
}


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


# ---------------------------------------------------------------------------------------------
# Geometry: bone-local <-> part-local, and what is buried in what.

def to_part(cube: str, p) -> tuple:
    """A point in a cube's bone-local frame into part-local space. One X rotation about the pivot."""
    px, py, pz = PLACEMENT[cube]["pivot"]
    th = math.radians(PLACEMENT[cube]["rot"])
    x, y, z = p
    return (px + x,
            py + y * math.cos(th) - z * math.sin(th),
            pz + y * math.sin(th) + z * math.cos(th))


def to_local(cube: str, q) -> tuple:
    """The inverse: part-local into a cube's own bone-local frame."""
    px, py, pz = PLACEMENT[cube]["pivot"]
    th = math.radians(-PLACEMENT[cube]["rot"])
    x, y, z = q[0] - px, q[1] - py, q[2] - pz
    return (x, y * math.cos(th) - z * math.sin(th), y * math.sin(th) + z * math.cos(th))


def in_box(lo, hi, p) -> bool:
    return all(lo[a] <= p[a] <= hi[a] for a in range(3))


def in_cube(cube: str, q) -> bool:
    """Is this part-local point inside that cube's solid?"""
    w, h, d = CUBES[cube][0]
    o = PLACEMENT[cube]["origin"]
    return in_box(o, (o[0] + w, o[1] + h, o[2] + d), to_local(cube, q))


def buried(cube: str, q) -> bool:
    """A part-local point is out of sight if it is inside the helmet shell or inside another cube of
    this part. Both matter here: the mount straddles the shell, and the two noses fold through the
    bristle mass they hang off."""
    if in_box(HELMET[0], HELMET[1], q):
        return True
    return any(in_cube(other, q) for other in CUBES if other != cube)


def visible_fraction(cube: str, face: str, i: int, j: int, n: int = 4) -> float:
    """How much of one texel a player can see, sampled on an n x n grid.

    Each sample is pushed 0.06 along the face's outward normal before it is tested, so that a face
    lying exactly on another solid's wall counts as outside it rather than inside - the same 0.05
    trick the tassets' mask used, one hundredth further out because two of this part's occluders are
    rotated and their walls are not axis-aligned.
    """
    corner, du, dv, nvec = FACE_FRAMES[face](*CUBES[cube][0])
    o = PLACEMENT[cube]["origin"]
    seen = 0
    for a in range(n):
        for b in range(n):
            fu, fv = (a + 0.5) / n, (b + 0.5) / n
            p = tuple(o[t] + corner[t] + du[t] * (i + fu) + dv[t] * (j + fv) + nvec[t] * 0.06
                      for t in range(3))
            if not buried(cube, to_part(cube, p)):
                seen += 1
    return seen / (n * n)


def texel_local(cube: str, face: str, i: int, j: int) -> tuple:
    """The bone-local centre of one texel, so a caller can ask where it is rather than which way the
    loop runs."""
    corner, du, dv, _ = FACE_FRAMES[face](*CUBES[cube][0])
    o = PLACEMENT[cube]["origin"]
    return tuple(o[t] + corner[t] + du[t] * (i + 0.5) + dv[t] * (j + 0.5) for t in range(3))


def axial(cube: str, z_local: float) -> float:
    """The fore-aft position on the ridge's own axis: the bone's pivot z plus the cube's local z.

    Deliberately NOT the rotated part-local z. The comb is a count of bristle bundles, and bundles do
    not get narrower because the brush folds over at the ends - using the projected z would bunch the
    stripes by cos 34 exactly where the silhouette is thinnest.
    """
    return PLACEMENT[cube]["pivot"][2] + z_local


# ---------------------------------------------------------------------------------------------
# Shading.

def bristle(a: float) -> bool:
    """True on the crown of a bristle bundle, False in the gullet between two.

    Period 2 on the shared axis and keyed off abs(), so the pattern is symmetric about the part's own
    centreline: bundles at |axial| in [0,1), [2,3), [4,5), which is five bundles and five gullets
    across the ridge's ten units, the same on both profiles and the same fore and aft.
    """
    return math.floor(abs(a)) % 2 == 0


def flank(a: float, t: float) -> int:
    """A side face of the bristle mass at fore-aft position `a`, `t` down from the ridge to the root.

    Bundle and gullet get two separate gradients rather than one gradient and an offset: subtracting
    a constant from a value that is already 78 at the root either clips or stops reading, and the
    root is where the comb has to survive if the brush is to look dense at its base as well as its
    top.
    """
    hi, lo = (BUNDLE_HI, BUNDLE_LO) if bristle(a) else (GULLET_HI, GULLET_LO)
    return round(hi + (lo - hi) * t)


def dim(lum: int, frac: float) -> int:
    """Fold a texel's measured visibility into its value: fully lit, flat INNER, or a lerp between."""
    if frac >= FULL:
        return lum
    if frac < GONE:
        return INNER
    return round(INNER + (lum - INNER) * frac / FULL)


def shade(img, cube: str, face: str, value) -> None:
    """Walk one face's rectangle, handing `value` the texel's own fore-aft axis position and its
    height down the brush, then dim the result by how much of that texel is actually visible."""
    x0, y0, fw, fh = faces(*CUBES[cube])[face]
    _, h, _ = CUBES[cube][0]
    for j in range(fh):
        for i in range(fw):
            xl, yl, zl = texel_local(cube, face, i, j)
            lum = value(axial(cube, zl), yl, xl, i, j)
            put(img, x0 + i, y0 + j,
                dim(lum, visible_fraction(cube, face, i, j)) + random.randint(-3, 3))


# ---------------------------------------------------------------------------------------------
# The four cubes.

def height(cube: str, y_local: float) -> float:
    """0.0 at the ridge line, 1.0 at the bottom of the bristle mass. Shared by the brush and the two
    noses so the flank gradient is continuous around the fold: the brush's five rows are y -7..-2 and
    a nose's four are its own 0..4 hanging off the ridge, and both index from the same top, so a
    texel at a given height gets the same value whichever cube it belongs to."""
    top = -7.0 if cube == "brush" else 0.0
    return min(1.0, max(0.0, (y_local - top) / 5.0))


def paint_brush(img) -> None:
    """The bristle mass: 2 x 5 x 6, geo x -1..1, y -7..-2, z -3..3, its bottom unit inside the mount.

    `west` and `east` are the hero faces - a longitudinal crest is an object seen in profile, and
    these are the only two large faces this part has. They are 6 wide by 5 tall each and they run in
    opposite fore-aft directions, which is the whole reason nothing here indexes by column.

    `up` is the ridge, and it is where the comb has to be unmistakable: 246 against 148, against the
    flanks' 226/150 at the same fore-aft position. `down` is flat on the mount's inside and comes back
    0% visible everywhere. `north` and `south` are the cut ends of the mass, half-covered by a nose
    that is one unit wide on a two-unit face, so they land in the dimmed tier by measurement.
    """
    shade(img, "brush", "up",
          lambda a, yl, xl, i, j: TIP if bristle(a) else TIP_GULLET)
    shade(img, "brush", "down",
          lambda a, yl, xl, i, j: INNER)
    for side in ("west", "east"):
        shade(img, "brush", side,
              lambda a, yl, xl, i, j: flank(a, height("brush", yl)))
    for cap in ("north", "south"):
        shade(img, "brush", cap,
              lambda a, yl, xl, i, j: round(END_HI + (END_LO - END_HI) * height("brush", yl)))


def paint_nose(img, cube: str) -> None:
    """One raked end: 1 x 4 x 2 folded 34 deg about the body's top edge, its far end 1.66 further out
    and 1.12 lower than the ridge.

    Its far end face - `north` on the front nose, `south` on the rear - is the brush's cut tip and is
    the only face on this part a camera directly in front of the player sees square on. Its near end
    face and its whole underside are inside the bristle mass; so are the lower rows of both flanks.
    None of that is hand-masked: visible_fraction measures it, and the numbers it returns are the
    ones quoted in the module docstring.
    """
    far = "north" if cube == "nose_front" else "south"
    near = "south" if cube == "nose_front" else "north"
    shade(img, cube, "up",
          lambda a, yl, xl, i, j: TIP if bristle(a) else TIP_GULLET)
    shade(img, cube, "down",
          lambda a, yl, xl, i, j: INNER)
    for side in ("west", "east"):
        shade(img, cube, side,
              lambda a, yl, xl, i, j: flank(a, height(cube, yl)))
    shade(img, cube, far,
          lambda a, yl, xl, i, j: round(END_HI + (END_LO - END_HI) * height(cube, yl)))
    shade(img, cube, near,
          lambda a, yl, xl, i, j: INNER)


def paint_mount(img) -> None:
    """The mount: 3 x 3 x 7, geo x -1.5..1.5, y -3..0, z -3.5..3.5, straddling the helmet's crown.

    Two of its three rows stand above the shell's top plane at y = -1 and the third is inside it, so
    its flanks are a two-row band: a chamfered 204 over a 92, which is the circlet's bright-top /
    dark-bottom split and is there for the same reason - it makes a 2-unit band read as thinner than
    2 units, and a mount that reads heavy would swallow the brush it is supposed to hold.

    The pins are the brooch's lesson applied at the only scale available: a stud has to be plainly
    brighter than what surrounds it, so they sit on the DARK row at 92 + 66 = 158 rather than on the
    204 chamfer where they would have had 50 points of headroom and read as noise. Two per flank at
    axial z = +-2, one in the centre of each end cap - and they are placed by axial position, not by
    column index, so they land in the same two places on `west` and on `east` even though those two
    faces count in opposite directions.

    The mount is 7 deep against the brush's 6, so half a unit of it shows fore and aft as well as each
    side: the `up` face's outer columns come back about half visible along their whole length and are
    painted as a bright flange. Its `down` face is inside the helmet in its entirety.
    """
    def band(a, yl, xl, i, j):
        # yl runs -3 (top) .. 0 (bottom of the buried unit); rows are 1 unit each.
        lum = BAND_HI if j == 0 else BAND_LO
        if j == 1 and abs(abs(a) - 2.0) < 0.51:
            lum += PIN
        return lum

    def cap(a, yl, xl, i, j):
        lum = BAND_HI if j == 0 else BAND_LO
        if j == 1 and abs(xl) < 0.51:      # one keeper pin, centred on the 3-wide end
            lum += PIN
        return lum

    shade(img, "mount", "up",
          lambda a, yl, xl, i, j: FLANGE - (0 if abs(xl) > 0.6 else 28))
    shade(img, "mount", "down", lambda a, yl, xl, i, j: INNER)
    for side in ("west", "east"):
        shade(img, "mount", side, band)
    for end in ("north", "south"):
        shade(img, "mount", end, cap)


# ---------------------------------------------------------------------------------------------

def check_geometry() -> None:
    """CUBES and PLACEMENT must be the shipped geometry, in order. Painting a texture for a shape the
    model no longer has is invisible to every other check in this pipeline: both halves stay
    internally consistent while the rectangles slide off the faces they were drawn for. PLACEMENT is
    checked as well as CUBES because on this part the composed pivots and the two rake angles decide
    the shading, not just the UV layout - a nose moved half a unit would leave every burial mask
    below silently wrong."""
    doc = json.loads(GEO.read_text(encoding="utf-8"))
    found = []

    def walk(bone, pivot, rot):
        px, py, pz = bone.get("pivot", [0, 0, 0])
        th = math.radians(rot)
        here = (pivot[0] + px,
                pivot[1] + py * math.cos(th) - pz * math.sin(th),
                pivot[2] + py * math.sin(th) + pz * math.cos(th))
        rx, ry, rz = bone.get("rotation", [0, 0, 0])
        assert ry == 0 and rz == 0, \
            f"{bone.get('name')} rotates about Y or Z; this master assumes X only"
        for c in bone.get("cubes", []):
            found.append((bone["name"], (tuple(c["size"]), tuple(c["uv"])),
                          {"pivot": here, "rot": rot + rx, "origin": tuple(c["origin"])}))
        for child in bone.get("children", []):
            walk(child, here, rot + rx)

    for bone in doc["bones"]:
        walk(bone, (0.0, 0.0, 0.0), 0.0)

    assert (doc["texture_width"], doc["texture_height"]) == (TEX_W, TEX_H), \
        f"{GEO.name} is {doc['texture_width']}x{doc['texture_height']}, this master is {TEX_W}x{TEX_H}"
    assert [n for n, _, _ in found] == list(CUBES), \
        f"CUBES names disagree with {GEO.name}: {[n for n, _, _ in found]} vs {list(CUBES)}"
    assert [c for _, c, _ in found] == list(CUBES.values()), \
        f"CUBES disagrees with {GEO.name}: {[c for _, c, _ in found]} vs {list(CUBES.values())}"
    for name, _, place in found:
        want = PLACEMENT[name]
        for key in ("pivot", "rot", "origin"):
            a, b = place[key], want[key]
            near = abs(a - b) < 1e-6 if key == "rot" else \
                all(abs(a[t] - b[t]) < 1e-6 for t in range(3))
            assert near, f"PLACEMENT[{name!r}][{key!r}] is {b}, {GEO.name} says {a}"


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


def main() -> None:
    check_geometry()
    claimed = check_layout()
    img = Image.new("LA", (TEX_W, TEX_H), (0, 0))
    paint_mount(img)
    paint_brush(img)
    paint_nose(img, "nose_front")
    paint_nose(img, "nose_rear")

    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque == set(claimed), "the opaque set is not exactly the UV rectangles"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    # The ramp-usage figure PLAN.md's circlet finding is about is a statement over the pixels a
    # player can SEE. Two fifths of this master is buried at a flat INNER, so quoting the whole
    # texture would report a spread that no material ever renders; both are printed, seen first.
    seen = []
    for cube, (size, uv) in CUBES.items():
        for face, (x, y, fw, fh) in faces(size, uv).items():
            for j in range(fh):
                for i in range(fw):
                    if visible_fraction(cube, face, i, j) >= GONE:
                        seen.append(img.getpixel((x + i, y + j))[0])
    print(f"wrote {OUT} ({len(opaque)} opaque px, {len(seen)} of them visible)")
    for label, vals in (("seen", seen), ("all ", lums)):
        low = sum(1 for v in vals if v < 128) / len(vals)
        print(f"  {label}: values {min(vals)}-{max(vals)}, {low:.0%} under 127")


if __name__ == "__main__":
    main()
