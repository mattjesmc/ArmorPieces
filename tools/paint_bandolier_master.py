"""
Paint the grayscale master, the static leather layer and the guard mask for the "bandolier" part.

Kept as a script rather than a checked-in binary so the shape stays editable and reviewable. Like
the buckled_belt, quiver and puttees painters this one does not merely claim that CUBES matches the
shipped geometry, it reads assets/armorpieces/armorpieces/decoration/bandolier.json at run time and
asserts it (check_geometry) - the origins AND the three bone frames, because the crossing IS the two
rotations: a master painted for a pair of vertical bands would stay perfectly self-consistent while
describing a different object, and one painted for the wrong SIGN would light the X from below.
Output goes to tools/decoration_masters/bandolier.png, bandolier_static.png and bandolier_guard.png,
which sync_decoration_masters.py installs.

Master convention: luminance carries shading, alpha carries silhouette. This master is 100% opaque.
A strap has no fringe and parts draw with armorCutoutNoCull, so a hole cut through a 0.9-thick band
would show the inside of the band rather than the chest behind it. The buckles' slots, the seam
between the two pouches and the gap between the two vials are therefore VALUE, not alpha.

WHAT THIS PART IS

`collar` had two parts on it and they are the same idea at two sizes: the Gorget is a symmetric
plate collar 0.75 proud of the chestplate, the Brooch a single clasp 1.75 proud of it, and both sit
tight under the throat and stop by body y 4.5. This one covers the whole chest, crosses itself,
carries three bags and stands 3.15 proud at the pouches. It is the first part on this socket that is
WORN rather than fastened, and the first a player reads as luggage.

Its Wayfarer relatives are the shipped Sash and Buckled Belt, and it takes the split the Belt
established: the leather keeps its own colour through a static layer, the buckles take a second trim
material through `armorpieces:guard`, and exactly one thing is left on the base trim material so a
gold bandolier is visibly gold. On the Belt that thing is the buckle; here it is the pair of
stoppered vials, which is the bargain the Quiver strikes with its arrows - the CONTENTS carry the
material, and the harness that holds them stays leather in every one.

THE CUBES, IN BONE-LOCAL UNITS AND IN THE BODY'S

`collar` is a SINGLE, non-mirrored attachment - Attachment.of(BODY, 0, 1, -2) - so the layer's
scale(-1, 1, 1) never runs, one master serves one draw, and `west` and `east` are genuinely
different faces rather than the same face twice. Part-local (0, 0, 0) is body (0, 1, -2). +Y is DOWN.

Three bones. `harness` is the root, unrotated, and carries the pouches alone. `over_left` sits at
part (0.7, 2.57, -1.55) rotated +45 about z and runs over the wearer's LEFT shoulder down to the
right; `over_right` at part (-0.7, 2.57, -2.55) rotated -45 is its opposite and is a whole unit
further from the chest, so it lies OVER the other everywhere they meet.

    cube      bone-local origin      size              body-frame hull
    pouch     (-1.6 ,  3.6 , -4.15)  (3.2, 2.4, 1.25)  x -1.60..1.60  y 4.60..7.00  z -6.15..-4.90
    strap_l   (-1.05, -3.7 , -0.45)  (2.1, 7.4, 0.9 )  x -2.66..4.06  y 0.21..6.93  z -4.00..-3.10
    buckle_l  (-1.05, -3.7 , -0.8 )  (2.1, 1.6, 0.4 )  x  1.44..4.06  y 0.21..2.83  z -4.35..-3.95
    strap_r   (-1.05, -3.7 , -0.45)  (2.1, 7.4, 0.9 )  x -4.06..2.66  y 0.21..6.93  z -5.00..-4.10
    buckle_r  (-1.05, -3.7 , -0.8 )  (2.1, 1.6, 0.4 )  x -4.06..-1.44 y 0.21..2.83  z -5.35..-4.95
    vials     (-1.1 , -2   , -1.35)  (2.2, 2.5, 1.1 )  x -2.89..0.43  y 1.38..4.70  z -5.90..-4.80

The straps are 2.1 wide and 0.9 THICK, and the 0.9 is the Buckled Belt's strap exactly. The Belt is
0.9 rather than 1.0 because a tenth of a unit of air was cheaper than a z-fight against the leggings
shell; the same 0.9 is here for the same reason against the chestplate. That thickness is the most
concrete thing the three Wayfarer parts of this batch have in common, and the reason to keep it even
where nothing forces it is that a player who owns the Belt and the Bandolier should see one leather.

THE COMPOSITION, WHICH TOOK THREE RENDERS

The first cut was two straps at 34 degrees with their pivots 1.2 apart, and everything - a buckle, a
bag and the vials - hung down the outer one. Rendered, it read as a V of hardware with a grey slab
in it. Two things were wrong and both were geometric rather than painterly:

  * at 34 degrees a 6.7-long strap sweeps only +/-1.9 in x, so the two straps crossed in the middle
    of their run and their tails, which are what say "X", were a unit long and sat behind the bag.
    Opening the angle to 45 and the length to 7.4 sweeps +/-2.6 instead, which moves the crossing up
    to body (0, 4.27) and leaves 2.7 units of tail below it, reaching out to body x +/-2.66 - past
    the pouches at +/-1.6, so the four ends are all visible.
  * the bags moved off the straps and onto the ROOT bone, unrotated, centred on x = 0 at the
    crossing. That is what a bandolier's main pouch does in life, it hangs where the straps meet and
    is held by both; and it makes the busiest object on the part sit where the eye already goes. It
    is also the only unrotated cube here, so the only one whose edges are vertical, which reads as a
    made thing among four leaning bands.

A second bag was tried on the INNER strap, to balance the vials, and thrown away. It cannot be done:
above the crossing the inner strap is on the wearer's left and the outer strap on their right, but
the outer strap is a unit further forward, and any bag on the inner strap thick enough to be seen
reaches into the outer one's depth range and then has to dodge it in x. Every placement that cleared
it was within a tenth of a unit of not clearing it. The honest answer is the one real bandoliers
give: the load rides on ONE strap and the other only holds it up. A fourth Wayfarer part on a
crossing harness should assume the same.

WHAT CLEARS WHAT

  * naked body box       x +/-4.0   z +/-2.0
  * leggings shell 0.5   x +/-4.5   z +/-2.5
  * chestplate shell 1.0 x +/-5.0   z +/-3.0   <- the piece this socket belongs to, always worn

strap_l's back face is body z = -3.10, a tenth of a unit clear of the chestplate's front wall.
Landing it ON -3 would have put a decoration face in the plane of a shell that is always worn with
it, and the decoration layer draws AFTER the armor layer, so at equal depth the later draw wins and
the strap would flicker its own dark INNER texels onto the breastplate. The same tenth clears the
chestplate's ARM shell, which is world x 3..9 at z -3..3 and which the top of each strap passes at
body x 4.06.

strap_r's back face is body z = -4.10, a tenth clear of strap_l's front face at -4.00. That tenth is
the whole of the layering: two crossing straps at one depth share both their z planes and z-fight
over the rhombus where they meet, and no plate that fits on a chest this size covers that rhombus. A
tenth of air is cheaper, and it also makes the crossing legible, because one strap plainly passing
over the other is what a crossing IS.

Above, both straps stop at body y 0.21. That is the head, and the limit is exact rather than
stylistic: the head bone yaws freely under the player's own aim while the body does not follow, and
its box is y -8..0, so anything above 0 is inside a cube that moves independently of this one. A
fifth of a unit is all the margin there is and all that is needed.

Below, the shipped Sash's gathered knot is body x -2..2, y 7.5..10.5, z -5..-2, and its front band
is y 8..11, z -4..-2. The lowest thing here is the pouch at body y 7.00, which clears the knot by
0.50 and the band by 1.00. That is what caps the strap length at 7.4: the X is exactly as long as
the gap between the head and the Sash, and every unit of it is spent.

Sideways nothing reaches past body x 4.06, six hundredths outside the naked torso and a whole unit
inside the chestplate. That matters because of the new `mantle` on `pauldrons`: the mantle rides the
ARM bone, and traced onto the body its ruff spans world x 4.75 and outward - it covers the shoulder
caps and the outer deltoid and does not reach the chest at all. Nothing on this part is hidden by
it. The shipped Gorget, whose shoulder pads reach x 6.5, is the collar part that does go under fur.

Two deliberate interpenetrations are worth naming, because a reader running a separating-axis test
will find them and wonder. The vials sink 0.2 into the strap they hang on and the pouches 0.1 into
theirs, which is what threading a bag onto a strap looks like and is what stops their back faces
from being coplanar with the strap's front face. The vials' inboard foot also runs 0.10 behind the
pouches, which is the same idea: a vial standing behind a bag rather than balanced beside it.

THE THINGS ON THE STRAPS

  * buckle_l and buckle_r sit at the top of each strap over the collarbones, 0.35 proud of the
    leather and sunk 0.05 into it so no two faces are coincident. `north` is 3 texels by 2, which is
    the budget the Buckled Belt's buckle had and it is spent the same way: a lit bar with a dark
    slot cut in it over a duller plate, 240 against 30. There is no tongue, because four columns is
    the minimum for frame-slot-tongue-frame and there are three. The Quiver's band plate is the same
    three-by-two figure, so all three parts of this batch say "buckle" with one shape.
  * the pouches are one cube, 3.2 x 2.4 x 1.25, four texel columns wide. Four columns is TWO bags,
    lit / shaded / lit / shaded; three could only ever have been one, which is why the cube grew
    from the 2.6 it started at. Three rows: flap, body, and a hem sampled over two fifths of a
    texel.
  * the vials hang on the outer strap, 2.2 x 2.5 x 1.1, netting to three rows - cork, glass, glass -
    and three columns, of which the MIDDLE one is the gap between two vials. Two vials, not three,
    for the Quiver's reason: a rod needs a lit column with a dark one beside it, so three columns
    can only read as lit / gap / lit.

THE THREE SHEETS

  * the MASTER shades everything. Leather is held inside 61..201 rather than run out to 250: it is
    read through the LEATHER static ramp, whose mid stop is at master 127 and whose light stop is
    only halfway to white, so a face painted at 240 would read as tan canvas rather than as leather.
    That is the window the Buckled Belt uses and the Quiver uses. The buckles run 27..240 and the
    vials 39..240, because those go through a trim material's own ramp and want all of it.
  * the STATIC layer is opaque LEATHER over both straps and the pouches, transparent over the
    buckles and the vials. #a06540 is vanilla's own undyed-leather-armour tint.
  * the GUARD mask is the two buckles, six face rectangles each, copied out of the master by
    fitting_mask.write_mask - same shading, second material.

FACE LAYOUT AND ORIENTATION

The face rectangles come from paint_circlet_master.faces(): row one (v .. v+d) holds up then down,
each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west, south with widths
d, w, d, w. The two thin d-wide faces come FIRST and THIRD.

Orientation inside each rectangle is the table the greaves and puttees painters record as measured:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x              max z
    down            +y  (underside)      min x              max z
    west            +x                   min z              min y
    east            -x                   max z              min y
    north           -z  (front)          min x              min y
    south           +z  (back)           max x              min y

`north` is the hero on every cube, because a chest decoration is met head on. What the two rotations
do to the rest of the table is the thing this painter has to get right, and it is NOT the same for
the two straps:

    over_left  (+45): local +x -> body ( 0.707,  0.707, 0)  so `west` is the strap's LOWER edge
    over_right (-45): local +x -> body ( 0.707, -0.707, 0)  so `west` is the strap's UPPER edge

Vanilla gives +x and -x the same 0.6 diffuse term, exactly as it gives +z and -z the same 0.8, so
the lit and the shaded edge of a strap are lit identically by the engine and the whole difference
has to be painted. LIT_EDGE is therefore passed in per bone rather than assumed, and `north`'s three
columns are read in opposite directions on the two straps for the same reason: on over_left column 0
is the upper edge, on over_right it is the lower one. Getting that backwards is invisible to every
arithmetic check in this pipeline and lights the X from underneath.

`up` on both straps is the cut end at the shoulder and is free on both - it is also the one face of
a strap that faces the light squarely, which is why it carries the brightest leather after the
pouches' lids. `down` is the cut end at the lower ribs and is behind the pouches on both, so both
are INNER.
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
       / "decoration" / "bandolier.json")
OUT = ROOT / "tools" / "decoration_masters" / "bandolier.png"
OUT_STATIC = OUT.with_name("bandolier_static.png")
OUT_GUARD = OUT.with_name("bandolier_guard.png")

TEX_W, TEX_H = 64, 32

# origin, size (w, h, d) and uv (u, v), mirroring bandolier.json in that file's own walk order: the
# root bone's pouch first, then over_left's three and over_right's three. The origins are asserted
# with the sizes because every clearance in the docstring is a statement about them - -0.45 with 0.9
# is the tenth off the chestplate, -1.55 against -2.55 is the tenth between the straps, and 6.7 is
# the length the Sash's knot leaves.
CUBES = {
    "pouch":    ((-1.6, 3.6, -4.15),   (3.2, 2.4, 1.25),  (32, 0)),
    "strap_l":  ((-1.05, -3.7, -0.45), (2.1, 7.4, 0.9),   (0, 0)),
    "buckle_l": ((-1.05, -3.7, -0.8),  (2.1, 1.6, 0.4),   (16, 0)),
    "strap_r":  ((-1.05, -3.7, -0.45), (2.1, 7.4, 0.9),   (8, 0)),
    "buckle_r": ((-1.05, -3.7, -0.8),  (2.1, 1.6, 0.4),   (24, 0)),
    "vials":    ((-1.1, -2, -1.35),    (2.2, 2.5, 1.1),   (44, 0)),
}

# The bone each cube hangs from: (pivot, rotation). The two rotations ARE the crossing, so they are
# asserted rather than trusted, and so is the root's lack of one - the pouch being unrotated is the
# reason it reads as a made thing among four leaning bands.
ROOT_FRAME = ((0, 0, 0), (0, 0, 0))
LEFT_FRAME = ((0.7, 2.57, -1.55), (0, 0, 45))
RIGHT_FRAME = ((-0.7, 2.57, -2.55), (0, 0, -45))
FRAMES = {
    "pouch": ROOT_FRAME,
    "strap_l": LEFT_FRAME, "buckle_l": LEFT_FRAME,
    "strap_r": RIGHT_FRAME, "buckle_r": RIGHT_FRAME, "vials": RIGHT_FRAME,
}

LEATHER_CUBES = ("pouch", "strap_l", "strap_r")
GUARD_CUBES = ("buckle_l", "buckle_r")

random.seed(29)  # deterministic output - regenerating must not churn the PNG

# ---- leather ------------------------------------------------------------------------------------
# Read through LEATHER's static ramp, whose mid stop is master 127 and whose light stop is only
# halfway to white. These stay inside 62..204 on purpose; see the docstring.
L_TOP = 198      # a ledge facing straight up - the pouch's lid, a strap's cut end at the shoulder
L_LIT = 184      # the upper long edge of a strap
L_FACE = 160     # the front of a strap, centre column
L_DIM = 116      # the lower long edge
L_BACK = 80      # a leather face turned back at the chestplate, a tenth of a unit away
L_UNDER = 92     # an underside
L_INNER = 64     # buried: inside a strap, behind the pouch

# ---- steel --------------------------------------------------------------------------------------
M_LIT = 240      # the top bar of a buckle
M_FACE = 200     # the plate under it
M_DIM = 138      # the buckle turned away
M_APERTURE = 30  # the slot the strap threads through
M_INNER = 32     # the buckle's back face, sunk into the leather

# ---- glass --------------------------------------------------------------------------------------
# On the base trim material, like the Quiver's arrows: the contents are what the material shows.
G_CORK = 126     # the stopper - deliberately UNDER the glass it plugs
G_LIT = 238      # the lit side of a vial
G_BODY = 196     # the rest of it
G_GAP = 58       # the gap between the two vials, which is the whole read
G_INNER = 42     # inside the strap

FALL = 26        # the falloff down a standing face
GRAIN = 4        # leather grain jitter
JITTER = 3


def net(size):
    """A cube's box-UV net in whole pixels. Rounds UP the way Blockbench does - a strap's 6.7 of
    length nets to seven rows and the seventh is sampled over only its first seven tenths."""
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


def fill(img, rect, lum: int, jitter: int = JITTER) -> None:
    x0, y0, w, h = rect
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            put(img, x, y, lum + random.randint(-jitter, jitter))


def ramp(i: int, n: int) -> float:
    """Position along a face axis, 0.0 at column/row 0 and 1.0 at the far end."""
    return 0.0 if n <= 1 else i / (n - 1)


# The lateral profile across a strap's three front columns, from its lit edge to its shaded one. A
# MULTIPLIER rather than an offset, so a row in shadow keeps its shape instead of being flattened
# into INNER by a subtraction sized for a lit one - leather over a chest is a curved surface and its
# shading is proportional.
STRAP_PROFILE = (1.00, 0.92, 0.76)

# What each of a strap's seven rows is worth. Row j spans bone-local ly -3.35 + j .. -2.35 + j, and
# the covering cubes are: the buckle over ly -3.35..-1.75, the satchel or the vials over -1.6..0.4
# or -1.6..0.9, and the pouch - which is on the root bone and crosses both straps - over roughly
# ly 1.9..3.35 on each. Row 4 is the one stretch of strap that nothing laps, on either side, and it
# is the brightest leather on the part.
LEFT_ROWS = (0.50, 0.62, 1.00, 1.00, 1.00, 0.92, 0.70, 0.58)
RIGHT_ROWS = (0.50, 0.54, 0.52, 0.86, 1.00, 0.92, 0.70, 0.58)


def paint_strap(img, name: str, lit_edge: str, rows) -> None:
    """One strap of the X: 2.1 x 7.4 x 0.9, leather, on a bone tilted 45 degrees about z.

    `north` is the hero - three columns by eight rows, of which the eighth is sampled over only its
    first two fifths. Which of the three columns is the lit one is NOT a property of the cube:
    `north`'s column 0 is min local x, and the two bones send local +x to opposite sides of the
    horizon, so on over_left column 0 is the strap's upper edge and on over_right it is the lower.
    The caller says which, and `lit_edge` says the same thing for the two one-texel flanks.

    `rows` is what the buckle, the bag and the pouch cover. A row under one of them is painted as
    leather in shade rather than as INNER: it costs nothing, and if the anchor is ever nudged what
    appears is a strap in shadow rather than a black stripe.

    `up` is the cut end at the shoulder, the one face of a strap that faces the light squarely, and
    it is free on both. `down` is the cut end at the lower ribs and is behind the pouch on both.
    `south` faces the chestplate a tenth of a unit away on strap_l and the back of strap_l on
    strap_r; neither is buried outright - a low angle from the side reaches both - so both get
    L_BACK rather than INNER."""
    f = face_rects(name)
    reversed_columns = lit_edge == "west"

    x0, y0, fw, fh = f["north"]          # 3 wide x 8 tall
    for j in range(fh):
        for i in range(fw):
            profile = STRAP_PROFILE[fw - 1 - i] if reversed_columns else STRAP_PROFILE[i]
            lum = max(L_INNER, round(L_FACE * rows[j] * profile))
            put(img, x0 + i, y0 + j, lum + random.randint(-GRAIN, GRAIN))

    for face in ("west", "east"):        # 1 deep x 8 tall - the strap's two long edges
        base = L_LIT if face == lit_edge else L_DIM
        x0, y0, fw, fh = f[face]
        for j in range(fh):
            lum = round((base - round(18 * ramp(j, fh))) * (rows[j] * 0.4 + 0.6))
            put(img, x0, y0 + j, max(L_INNER, lum) + random.randint(-GRAIN, GRAIN))

    x0, y0, fw, fh = f["up"]             # 3 wide x 1 deep - the cut end at the shoulder
    for i in range(fw):
        put(img, x0 + i, y0, L_TOP - round(20 * ramp(i, fw)) + random.randint(-GRAIN, GRAIN))

    fill(img, f["down"], L_INNER)        # the cut end at the ribs, behind the pouch
    fill(img, f["south"], L_BACK)        # the chestplate, or the strap behind


def paint_buckle(img, name: str) -> None:
    """One buckle at the top of a strap, over a collarbone: 2.1 x 1.6 x 0.4, 0.35 proud of the
    leather and sunk 0.05 into it so no two faces are coincident.

    `north` is 3 by 2 and that is the whole budget. Three columns is one short of
    frame-slot-tongue-frame, so what there is is a lit bar with a dark slot cut in it over a duller
    plate: 240 against 30, and at this size that contrast IS the buckle. The Buckled Belt paid for
    that lesson at three by three and the Quiver's band plate repeats it at three by two; all three
    parts of this batch say "buckle" with one figure, which is most of what makes them a set.

    `up`, `down` and the two flanks are the plate's rim, a single texel each way and all of it
    proud of the strap. `south` is sunk in the leather and is INNER."""
    f = face_rects(name)

    x0, y0, fw, fh = f["north"]          # 3 wide x 2 tall
    rows = ((M_LIT, M_APERTURE, M_LIT),          # the slot the strap threads
            (M_FACE, M_DIM, M_FACE))             # the plate under it
    for j, row in enumerate(rows):
        for i, lum in enumerate(row):
            put(img, x0 + i, y0 + j, lum + random.randint(-JITTER, JITTER))

    x0, y0, fw, fh = f["up"]
    for i in range(fw):
        put(img, x0 + i, y0, M_LIT - 8 - round(20 * ramp(i, fw)) + random.randint(-JITTER, JITTER))
    x0, y0, fw, fh = f["down"]
    for i in range(fw):
        put(img, x0 + i, y0, M_DIM - 40 + random.randint(-JITTER, JITTER))

    for face, base in (("west", M_FACE + 20), ("east", M_DIM)):
        x0, y0, fw, fh = f[face]         # 1 deep x 2 tall
        for j in range(fh):
            put(img, x0, y0 + j, base - round(22 * ramp(j, fh)) + random.randint(-JITTER, JITTER))

    fill(img, f["south"], M_INNER)       # sunk into the strap


def paint_pouch(img) -> None:
    """The pair of pouches at the sternum: one cube, 3.2 x 2.4 x 1.25, unrotated on the root bone.

    Four texel columns is what 3.2 units buys and it is the reason the cube is 3.2 rather than the
    2.6 it started at: four columns is TWO bags - lit, shaded, lit, shaded - where three columns
    could only ever have been one. The seam between them is the value STEP from column 1 to column
    2, not a modelled gap: a gap cut in alpha would show the inside of the leather, and a modelled
    one would cost two more cubes and 0.2 of chest that the Sash's knot does not leave.

    Three rows: the flap, the body, and a hem sampled over only two fifths of a texel. `up` is a
    real ledge two texels deep - the pouch stands a whole unit proud of the outer strap and 1.15 in
    front of the inner one - so it takes the brightest leather in the file.

    `south` sinks 0.1 into the outer strap, which is what threading a bag onto a strap looks like
    and what stops the two faces from being coincident. It never reaches the inner strap at all: it
    is 0.9 in front of it, and that is right, because the inner strap passes BEHIND the pouch, which
    is what a crossing means."""
    f = face_rects("pouch")
    rows, profile = POUCH_ROWS, POUCH_PROFILE

    x0, y0, fw, fh = f["north"]
    for j in range(fh):
        for i in range(fw):
            lum = round(L_FACE * rows[j] * profile[i])
            if j == 0:
                lum += 20                # the flap catches the light
            put(img, x0 + i, y0 + j, max(L_INNER, lum) + random.randint(-GRAIN, GRAIN))

    x0, y0, fw, fh = f["up"]             # 4 wide x 2 deep - the tops of the two flaps
    for j in range(fh):
        for i in range(fw):
            lum = round((L_TOP - round(16 * ramp(j, fh))) * profile[i])
            put(img, x0 + i, y0 + j, lum + random.randint(-GRAIN, GRAIN))

    x0, y0, fw, fh = f["down"]           # the underside, where a bag is at its darkest
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j, L_UNDER - 18 - round(8 * ramp(j, fh))
                + random.randint(-JITTER, JITTER))

    for face, base in (("west", L_LIT - 8), ("east", L_DIM + 14)):
        x0, y0, fw, fh = f[face]         # d deep x h tall
        for j in range(fh):
            for i in range(fw):
                lum = base - round(20 * ramp(j, fh)) - round(24 * ramp(i, fw))
                put(img, x0 + i, y0 + j, max(L_INNER, lum) + random.randint(-GRAIN, GRAIN))

    fill(img, f["south"], L_INNER)       # sunk into the strap


# A bag is a soft thing, so its lateral profile is rounder than a strap's and peaks off centre.
# Four columns are two bags: each is lit on its own left and falls away to its right, and the step
# from column 1 to column 2 is the seam between them.
POUCH_PROFILE = (1.00, 0.64, 0.98, 0.62)
POUCH_ROWS = (1.00, 0.90, 0.64)          # flap, body, and a 0.4-texel hem at the bottom


def paint_vials(img) -> None:
    """Two stoppered vials hanging on the right strap: 2.2 x 2.5 x 1.1, on the base trim material.

    Three columns and three rows. The middle column is not a vial, it is the GAP between two, and
    74 against 238 down all three rows is the entire read - the Quiver's arrows are made the same
    way and for the same reason: at one texel per object, relief buys nothing, because vanilla
    shades by normal alone and two parallel faces are lit identically however far apart they are.

    Row 0 is the corks and it is painted DARK against the glass under it. That is the opposite of
    what a highlight would do and it is right: a stopper is wood in a bright bottle, and the only
    way three texels can say "stoppered" is for the top row to be plainly duller than the two below.
    Row 2 is sampled over half a texel - the foot of the glass - and is dropped further, which also
    hides the 0.33 by which the inboard vial runs behind the pouch.

    These are the one thing on this part left on the base trim material, so on a gold bandolier they
    are the gold. `south` is inside the strap and is INNER."""
    f = face_rects("vials")

    x0, y0, fw, fh = f["north"]          # 3 wide x 3 tall: cork, glass, glass
    rows = ((G_CORK, G_GAP - 8, G_CORK - 14),
            (G_LIT, G_GAP, G_BODY),
            (G_BODY - 26, G_GAP - 16, G_BODY - 42))
    for j, row in enumerate(rows):
        for i, lum in enumerate(row):
            put(img, x0 + i, y0 + j, lum + random.randint(-JITTER, JITTER))

    x0, y0, fw, fh = f["up"]             # 3 wide x 2 deep - the tops of the two corks
    for j in range(fh):
        for i in range(fw):
            lum = (G_GAP if i == 1 else G_CORK + 42) - round(20 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + random.randint(-JITTER, JITTER))

    fill(img, f["down"], G_INNER + 18)   # the feet, behind the pouch

    for face, base in (("west", G_LIT - 14), ("east", G_BODY - 62)):
        x0, y0, fw, fh = f[face]         # 2 deep x 3 tall
        for j in range(fh):
            for i in range(fw):
                lum = base - round(34 * ramp(j, fh)) - round(26 * ramp(i, fw))
                put(img, x0 + i, y0 + j, lum + random.randint(-JITTER, JITTER))

    fill(img, f["south"], G_INNER)       # sunk into the strap


# The colour master value 127 maps to, through DecorationPalette.ofStaticColour: dark is half of it,
# light is halfway from it to white. Vanilla's own undyed-leather-armour tint, and the colour the
# Buckled Belt and the Quiver use.
LEATHER = (0xA0, 0x65, 0x40)


def check_geometry() -> None:
    """CUBES and FRAMES must be the cube list, the origins, the uv and the bone frames of the
    shipped geometry, in order.

    Painting a texture for a shape the model no longer has is invisible to every other check in this
    pipeline: both halves stay internally consistent while the rectangles slide off the faces they
    were drawn for. The rotations are asserted with the rest because on this part they are the
    design, and because their SIGN decides which column of `north` is the lit one - a swap there is
    silent everywhere else and lights the X from underneath."""
    doc = json.loads(GEO.read_text(encoding="utf-8"))
    found = []

    def walk(bone):
        frame = (tuple(bone.get("pivot", [0, 0, 0])), tuple(bone.get("rotation", [0, 0, 0])))
        for c in bone.get("cubes", []):
            found.append(((tuple(c["origin"]), tuple(c["size"]), tuple(c["uv"])), frame))
        for child in bone.get("children", []):
            walk(child)

    for bone in doc["bones"]:
        walk(bone)

    assert (doc["texture_width"], doc["texture_height"]) == (TEX_W, TEX_H), \
        f"{GEO.name} is {doc['texture_width']}x{doc['texture_height']}, this master is {TEX_W}x{TEX_H}"
    assert [c for c, _ in found] == list(CUBES.values()), \
        f"CUBES disagrees with {GEO.name}: {[c for c, _ in found]} vs {list(CUBES.values())}"
    assert [fr for _, fr in found] == list(FRAMES.values()), \
        f"FRAMES disagrees with {GEO.name}: {[fr for _, fr in found]} vs {list(FRAMES.values())}"

    # The four clearances the docstring is made of, read back off the tables rather than trusted.
    back = LEFT_FRAME[0][2] + CUBES["strap_l"][0][2] + CUBES["strap_l"][1][2]
    assert abs(back + 1.1) < 1e-9, \
        "strap_l's back face must be part z -1.1, a tenth of a unit off the chestplate's -1"
    left_front = LEFT_FRAME[0][2] + CUBES["strap_l"][0][2]
    right_front = RIGHT_FRAME[0][2] + CUBES["strap_r"][0][2] + CUBES["strap_r"][1][2]
    assert abs((left_front - right_front) - 0.1) < 1e-9, \
        "strap_r must lie a tenth of a unit in front of strap_l - two crossing straps at one depth" \
        " share both z planes and z-fight over the rhombus where they meet"
    assert LEFT_FRAME[1][2] == -RIGHT_FRAME[1][2] != 0 and LEFT_FRAME[0][0] == -RIGHT_FRAME[0][0], \
        "the two straps must be equal and opposite in both rotation and pivot, which is what an X is"
    assert FRAMES["pouch"][1] == (0, 0, 0), \
        "the pouch is the one unrotated cube here; that is why it reads as a made thing"
    assert math.ceil(CUBES["pouch"][1][0]) == 4, \
        "the pouch must net to four texel columns - four columns is two bags, three is one"


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
    """The static layer: opaque LEATHER over both straps, the satchel and the pouch, transparent over
    the buckles and the vials.

    A transparent static pixel takes the trim material's ramp; an opaque one takes its own colour
    through the static ramp with the master's value as the shading. So this one file is the whole of
    the leather / steel / glass split, and it is derived from the master's own alpha rather than
    painted, which is what makes it impossible for the two to disagree about the silhouette."""
    static = Image.new("RGBA", (TEX_W, TEX_H), (0, 0, 0, 0))
    source = master.convert("LA")
    count = 0
    for name in LEATHER_CUBES:
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
    # `lit_edge` is the flank on the upper side of each strap, and it is opposite for the two bones -
    # see the orientation table in the docstring.
    paint_strap(img, "strap_l", "east", LEFT_ROWS)
    paint_strap(img, "strap_r", "west", RIGHT_ROWS)
    paint_buckle(img, "buckle_l")
    paint_buckle(img, "buckle_r")
    paint_pouch(img)
    paint_vials(img)

    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque == set(claimed), "painted pixels do not match the UV rectangles"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)})")

    leather = {p for name in LEATHER_CUBES for x0, y0, w, h in face_rects(name).values()
               for p in ((x, y) for y in range(y0, y0 + h) for x in range(x0, x0 + w))}
    leather_lums = [img.getpixel(p)[0] for p in sorted(leather)]
    assert max(leather_lums) <= 210, \
        f"a leather value of {max(leather_lums)} runs the leather ramp towards white; keep it under 210"
    assert min(leather_lums) >= 55, \
        f"a leather value of {min(leather_lums)} sinks under the leather ramp's dark stop"

    write_static(img)

    # One fitting. The two buckles alone are the guard and take a metal; the leather is in neither
    # the mask nor the base ramp, and the vials are on the base ramp in every case.
    write_mask(img, [r for name in GUARD_CUBES for r in face_rects(name).values()], OUT_GUARD)


if __name__ == "__main__":
    main()
