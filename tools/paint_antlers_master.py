"""
Paint the grayscale master for the "antlers" part.

Like the mantle and the pelt - the two Beast parts this one is written to match - this does not
merely claim that CUBES is the shipped geometry, it reads
assets/<ns>/armorpieces/decoration/antlers.json at run time and asserts it: sizes, uvs AND origins,
because every clearance below is made out of the origins (check_geometry). The part left the mod in
0.4.0 and ships in the Wild Hunt now, so decoration_paths says where that file is. Output is a
single sheet, tools/decoration_masters/antlers.png, which sync_decoration_masters.py installs for
the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

This master is 100% opaque, and that is the Beast rule rather than laziness. Parts draw with
armorCutoutNoCull, so a hole punched in the outboard face of a tine shows the LIT INSIDE of that
tine's inboard face, not the sky behind it. The mantle reached that conclusion for fur and the pelt
for a hide; an antler is the same solid. **The raggedness lives in the geometry**: eight cubes on
eight bones - a burr, a three-segment beam and four tines, each tine on a bone of its own - ending
in five points that stop at five different heights.

## What this part is

`antlers` is the branching stag rack on the `horns` socket - the mod's third part there, against
Horns (curled, close to the skull, topping out at entity y -14.36) and Helm Wings (a swept plate
pair, y -13.60). Both of those hug the head. This one does not: it stands 12.49 units proud of the
head box and 24.80 wide across the pair, which makes it the largest silhouette the helmet can wear
and the reason the socket needed a third answer at all.

`horns` is a MIRRORED pair - Attachment.of(HEAD, 4, -5, 0) plus Attachment.mirrored at (-4, -5, 0) -
so the layer's scale(-1, 1, 1) runs on the right-hand copy and ONE master serves both temples.
`west` is geo +x, outboard on both sides; `east` is geo -x, toward the skull on both. The horns, the
spaulders and the pelt buy the same economy on the same terms.

Because the whole part rides the HEAD bone it turns with the head and can never foul the body - the
constraint that shapes a pauldrons part does not exist here. What does exist is the brow band: the
circlet's temple bar runs entity x 4..6, y -6..-4, z -4..6, straight through where a horn boss wants
to grip. Both shipped parts on this socket drive a boss straight through it - an exact
separating-axis test over the two oriented boxes puts horns' boss 1.000 inside the rail and helm
wings' the same 1.000, and both also share the plane x = 4 with it. This part is the first here that
does not: the burr is two units tall instead of three and stops at entity y -6.40, clearing the rail
by 0.400 on the same test. That 0.400 is the only reason the burr is 2 and not 3, and it must not be
tidied away.

Every other pair was measured the same way rather than read off trace_geometry's hull test, which
over-reports rotated cubes badly: against the circlet, the visor, the brush crest and the feathering,
no cube of this part comes within 0.5 of anything, and the burr's 0.400 to the temple rail is the
tightest approach on the whole socket.

## The cubes, in the part's frame and in the head bone's

Part-local is the frame the geometry JSON is written in. The head bone's pivot is the origin, so
bone-local IS entity space here, and it is part-local plus the anchor's (4, -5, 0). +Y is DOWN.
Rotated cubes are given as their axis-aligned hull.

    cube    bone    size       part x          part y           part z          entity x
    burr    burr    4 x 2 x 3  -1.10 .. 2.90   -3.40 .. -1.40   -1.70 ..  1.30   2.90 ..  6.90
    brow    brow    1 x 4 x 2   1.07 .. 3.09   -8.34 .. -3.91   -3.73 ..  0.43   5.07 ..  7.09
    beam1   beam1   2 x 5 x 2   0.41 .. 4.39   -8.27 .. -2.61   -0.83 ..  2.17   4.41 ..  8.39
    bez     bez     1 x 4 x 1   2.50 .. 4.49  -11.10 .. -6.95   -1.72 ..  0.97   6.50 ..  8.49
    beam2   beam2   2 x 4 x 2   2.28 .. 5.18  -11.80 .. -7.01    0.39 ..  4.01   6.28 ..  9.18
    trez    trez    1 x 4 x 1   4.75 .. 8.40  -13.99 .. -10.34    1.79 ..  3.43   8.75 .. 12.40
    beam3   beam3   1 x 3 x 2   3.35 .. 4.72  -13.44 .. -9.77    1.87 ..  5.43   7.35 ..  8.72
    crown   crown   1 x 5 x 1   1.68 .. 4.50  -15.49 .. -11.35   3.39 ..  7.76   5.68 ..  8.50

`burr` is the pedicle knot at the temple and the only unrotated cube on the part. Everything else
hangs off a chain of rotated bones, and every tine has a bone of its own:

    bone    parent   pivot (parent frame)   rotation      what it is
    burr    -        (0, 0, 0)              -             the knot on the skull
    brow    burr     (1.2, -2.6, -1.2)      ( 42, 0,  14) the brow tine, forward over the temple
    beam1   burr     (1.4, -3.2,  0.2)      (-12, 0,  24) the beam leaving the skull up and outboard
    bez     beam1    (0, -3.6, 0)           ( 38, 0, -10) the bez tine, forward off the first node
    beam2   beam1    (0, -4.8, 0)           (-14, 0, -12) the beam turning back and upright
    trez    beam2    (0, -2.2, 0)           ( 16, 0,  36) the trez tine, the widest reach on the part
    beam3   beam2    (0, -3.8, 0)           (-16, 0,  -6) the terminal beam, sweeping back
    crown   beam3    (0, -1.4,  0.2)        ( -8, 0, -22) the crown point, the tallest thing here

A positive Z rotation carries an UPWARD cube toward +x, which is outboard on both temples after the
mirror; a negative X rotation carries it toward +z, which is backward. So the beam chain's
(-12, +24) then (-14, -12) then (-16, -6) is "out and up, then back and upright, then back again",
and the tines' positive X rotations are the ones that come forward off it.

WHERE THE TIPS LAND, which is this part's version of the pelt's hem line. Read up the rack:

    tine / prong   tip at entity y   reach at entity x   deepest z
    brow               -13.34              7.09            -3.73  (forward, past the temple)
    bez                -16.10              8.49            -1.72
    beam3              -18.44              8.72             5.43
    trez               -18.99             12.40             3.43
    crown              -20.49              8.50             7.76

The steps between those five are +2.76, +2.34, +0.55 and +1.50: no two alike, which is the same
refusal the pelt's four-lock hem makes and the mantle's four locks after it. The outboard reaches
step 7.09, 8.49, 8.72, 12.40, 8.50 - the widest point is NOT the highest, which is what stops the
rack reading as a fan. Three of the five tips also differ in depth by more than two units, so from
any camera angle at all the five are five and not a comb.

## What clears what

The surfaces this part is measured against, in ENTITY coordinates, because the head bone's pivot is
the origin:

    the naked head box            x -4.0 .. 4.0   y -8.0 .. 0.0   z -4.0 .. 4.0
    the helmet shell (1.0)        x -5.0 .. 5.0   y -9.0 .. 1.0   z -5.0 .. 5.0
    the helmet's hat layer (1.5)  x -5.5 .. 5.5   y -9.5 .. 1.5   z -5.5 .. 5.5
    the circlet's temple bar      x  4.0 .. 6.0   y -6.0 .. -4.0  z -4.0 .. 6.0

The hat layer is the outermost surface a helmeted head actually draws, and it is the one this
painter treats as the burial line - trace_geometry stops at the 1.0 shell because HumanoidModel
keeps `hat` as a child rather than a slot part, so the extra half unit has to be carried by hand.
Four numbers decide the part:

  * **x = 5.5 is the burial wall.** The burr spans 2.90 .. 6.90, so its inboard half is inside the
    helmet and its outboard half is not: of its four x columns, 0 and 1 are buried, 2 straddles the
    wall by six tenths, and 3 is free. That is the whole reason the burr is four units wide - a burr
    that started outside the helmet would be a lump stuck ON the helmet rather than growing out of
    it, and the two shipped parts here both make the same choice with their bosses.

  * **y = -6.40, the burr's underside**, is 0.40 above the circlet's temple bar. See above.

  * **y = -9.5 is the top of the helmet.** Everything above it is against the sky. The beam leaves
    the burial wall almost at once (beam1 spans 4.41 .. 8.39 and only its bottom-inboard corner is
    inside the hat), so all five tines and all three beam segments are read against sky, not
    against armour. That is why this master has no INNER filler outside the burr and the joints.

  * **z = -5.5 is the front of the helmet**, and the brow tine stops at -3.73. It is well short
    on purpose: a brow tine that reached in front of the face would read as a beak from every
    camera the player has of themselves, and it is already the part's forward silhouette at entity
    x 5.07 .. 7.09, which is beside the helmet rather than in front of it.

Cross-part, on the same head bone, trace_geometry compares this against the two brow parts and the
two crest parts. The crest pair live inside |x| <= 1.50 and this part's inboard face is at x 2.90,
so they clear by 1.40 without either having to know about the other. The visor stays inside
x +-4.00 and z <= -3.75, and the nearest thing to it here is the brow tine, whose whole span is
outboard of x 5.07. The circlet is the 0.40 above.

No two faces of this part lie in a plane of any shell, and only the burr could - it is the only
unrotated cube here, and its six faces are at x -1.10 / 2.90, y -3.40 / -1.40 and z -1.70 / 1.30 in
part-local, none of which is a wall of anything. The other seven cubes sit on rotated bones and a
rotated face can never be coplanar with an axis-aligned shell at all, which is the cheapest form
that guarantee takes.

## Why the master is shaded the way it is

An antler is not fur, but it is the same problem: a shape with no room for detail that has to read
as something grown rather than forged. The mantle's answer was strands, clumps and a broken hem;
the pelt's was a clump table with no period and a grain three times the plates'. This part keeps
the grain and the tables and swaps what they describe. Three ideas, and no fourth:

  1. **Ridging.** Every standing face takes a per-COLUMN tone offset out of a hand-written table -
     RIDGE4 / RIDGE3 / RIDGE2 below. A column of a tine's face runs the length of the tine, so a
     column IS a longitudinal ridge, which is exactly what the outside of an antler has. The tables
     are written and not generated, and the point of them is the pelt's point: no two consecutive
     steps are equal and the sequence never repeats, so nothing on the part can strike the eye as a
     pattern. A one-column face gets no ridge at all - there is nothing for a ridge to be different
     from - and carries its whole reading in the climb below.

  2. **The climb.** Value rises from the root of a tine to its tip. That is the opposite of the
     mantle's locks, which fall away from the ruff, and it is deliberate: an antler is dark and
     pearled where it leaves the skull and rubbed pale where it has been thrashed against trees, so
     a tine brightest at the base reads as a bone spike and one brightest at the tip reads as an
     antler. Row 0 of every tine cube is its TIP - the cubes are written spanning y -L .. 0 so they
     grow along -y - which is the one thing about this net a reader has to hold on to, because it
     is upside down from every hanging part in the mod.

  3. **Pearling, and a broken tip.** The burr is knobbly: it takes PEARL4 / PEARL3, a second
     hand-written table with a bigger amplitude than the ridges, because at the burr the surface is
     lumps rather than lines. And no tine is lit on the same pair of faces as any other. TIP_FACES
     names the two faces of each tine that catch the light at the tip and the two that are dropped;
     five tines, five different pairs. A rack whose tips are all lit the same way reads as five
     bright bars - the failure the last batch of parts kept finding - and one where the light picks
     a different side of each tine reads as five tines.

Under all three is the standing-figure key the spaulders, the mantle and the pelt share - lit from
above, from the front and from outboard - plus one shape-specific value: **SOCKET**, the ring of
shadow on the row where a tine leaves the cube it grows out of. Every tine and beam here has its
last row buried in its parent (or in the helmet), and the row above that is the row the parent's
surface crosses. Without SOCKET a tine and its beam are one continuous value and the rack reads as
one folded ribbon; with it each branch sits ON the one before, which is the whole reason this is
eight cubes and not one.

Value calibration, the same one every master here is held to: the material ramp interpolates
dark -> mid over master values 0 .. 127 and mid -> light over 128 .. 255, so a master confined to
the top half only ever uses half of a material's ramp. Here the polished tips saturate while the
inboard faces, the sockets and the burr's underside sit well under 127, so the visible texels alone
span the ramp - the line main() prints at the end is that range.

## No fitting, and no static layer

The plan lists this part with no fitting and it keeps none. Every candidate was hardware that does
not belong on a rack: a gem at a tine tip is a wand, a metal guard on a beam is a splint, a dye
inlay over the whole thing is the mantle's answer and would leave the trim material nothing to be.
An antler is one substance from the burr to the crown point, and the honest thing for a part made
of one substance is to spend the whole of it on the material the player smithed it in.

No `_static.png` either, for the mantle's reason: a static layer would fix the antler's own ivory
and the part would then look identical in all sixteen materials, which is the one thing a
decoration in this mod must not do. A gold rack is a gilded trophy and a diamond one is frost.

## The unwrap

The face rectangles come from paint_circlet_master.faces(), copied verbatim: row one (v .. v+d)
holds up then down, each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west,
south with widths d, w, d, w. Note the row-two order: the two thin d-wide faces come FIRST and
THIRD.

Orientation inside each rectangle is the table PLAN.md records as measured, not recalled:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x              max z
    down            +y  (underside)      min x              max z
    west            +x  (outboard)       min z  (front)     min y (top)
    east            -x  (inboard)        max z  (back)      min y (top)
    north           -z  (front)          min x  (inboard)   min y (top)
    south           +z  (back)           max x  (outboard)  min y (top)

For a cube that grows upward - every one here but the burr - "min y" is the FAR end, so row 0 of a
tine's standing face is its tip and the last row is its root. `up` is the tip cap and `down` is the
root cap. That inversion is what the climb in idea 2 is written against.

Blockbench's `west` is the geo +x face - the one pointing away from the skull for a left-side part -
and `east` is the one against it. That is what lets one master serve both temples: after the layer's
scale(-1, 1, 1) the geo +x face of the mirrored copy still points outboard, so lit-outboard /
shadowed-inboard survives the mirror and the pair reads as a pair.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image

import decoration_paths

ROOT = Path(__file__).resolve().parent.parent
GEO = decoration_paths.geometry("antlers")
OUT = ROOT / "tools" / "decoration_masters" / "antlers.png"

TEX_W, TEX_H = 64, 32

# origin, size (w, h, d) and uv (u, v), mirroring antlers.json in that file's own order, which is
# the order walk() visits: the burr, then the brow tine, then the beam chain with each node's tine
# ahead of the beam segment that follows it. Origins are asserted as well as sizes because the
# docstring's whole clearance argument - the 0.40 over the circlet, the 5.5 burial wall, the -3.73
# the brow tine stops at - is made out of them.
#
# Four of these origins - burr's x, and the y of brow, bez and trez - were corrected on 2026-09-08
# to what the shipped geometry has always said. The part had been nudged in Blockbench after the
# master was painted and this table never followed, so `check_geometry` had been failing since
# 0.3.0. THE SHEET IS UNAFFECTED: sizes and uvs did not move, so every face rectangle is where it
# was, and the burr's four x columns still fall on the same side of the burial wall. What did move
# is the measured record above, which is re-derived rather than adjusted - the tip ladder now puts
# trez above beam3 instead of below it.
CUBES = {
    "burr":  ((-1.1, -3.4, -1.7), (4, 2, 3), (0, 0)),
    "brow":  ((-0.5, -5, 1.1), (1, 4, 2), (14, 0)),
    "beam1": ((-1, -5, -1.05), (2, 5, 2), (20, 0)),
    "bez":   ((-0.55, -5, -0.5), (1, 4, 1), (28, 0)),
    "beam2": ((-0.95, -4.2, -0.95), (2, 4, 2), (32, 0)),
    "trez":  ((-0.5, -6, -0.5), (1, 4, 1), (40, 0)),
    "beam3": ((-0.45, -2.6, -0.9), (1, 3, 2), (44, 0)),
    "crown": ((-0.5, -5, -0.55), (1, 5, 1), (50, 0)),
}

random.seed(0x414E544C)  # deterministic output - regenerating must not churn the PNG

# Calibrated against the ramp, not guessed, and pitched in the same register as pelt.py and
# mantle.py so the three Beast parts sit together on one figure.
POLISH = 208    # a tip cap - antler rubbed pale, and the one face lit at diffuse 1.0
TINE = 186      # the outboard face of a free tine
BEAM = 166      # the outboard face of a beam segment, a step under the tines it carries
FRONT = 152     # a -z face
BACK = 132      # a +z face
INBOARD = 118   # a -x face, turned back toward the skull - low, but NOT buried: unlike every
                # other Beast part the inboard side of this one is read against sky, so it cannot
                # take the pelt's inboard value and survive vanilla's 0.6 diffuse on a +-x normal
INNER = 62      # buried: in the helmet, in the burr, or in the beam below
UNDER = 58      # a free underside

CLIMB = 16      # root-to-tip brightening down a standing face's rows
DEPTH = 22      # front-to-back falloff across a flank
DROP = 12       # how far an unlit tip column falls below its face
SOCKET = 44     # how far the row where a BRANCH leaves its parent falls below that face

# Hand-written, not generated, and read along a face's columns. Changing one of these numbers moves
# a ridge, which is a design edit and not a tuning knob. Read them as the pelt's CLUMP tables: no
# two consecutive steps equal, and no sequence that repeats.
RIDGE4 = (18, -22, 8, -12)      # four columns: the burr's north / south / up / down
RIDGE3 = (-16, 20, -8)          # three: the burr's west, and any three-deep face
RIDGE2 = (14, -18)              # two: a beam's flank, and every two-wide face on the part
PEARL4 = (-14, 26, -10, 18)     # the burr's knobs, bigger than a ridge because a burr is lumps
PEARL3 = (22, -16, 9)
TIP3 = (26, -18, 10)            # per-column lift on a lit tip row, three wide
TIP2 = (-16, 24)                # the same, two wide

RIDGES = {1: (0,), 2: RIDGE2, 3: RIDGE3, 4: RIDGE4}
TIPS = {1: (20,), 2: TIP2, 3: TIP3}

# Which two of a tine's four standing faces catch the light at the tip, and which two are dropped.
# Five tines, five different pairs, so no two tips in the rack flare the same way. `beam3` is here
# because its own top is the front prong of the terminal fork and reads as a tine.
TIP_FACES = {
    "brow":  ("west", "north"),
    "bez":   ("west", "south"),
    "beam3": ("north", "south"),
    "trez":  ("west", "east"),
    "crown": ("east", "north"),
}

# How many rows at the ROOT end of each standing face are inside something - the parent cube, the
# helmet, or both. Measured face by face against the hat layer and against every other cube of the
# part, not assumed from the bone chain: a rotated tine leaves its parent through whichever wall it
# reaches first, and it is a different wall on each of the five. The row directly above the buried
# ones is the socket row and takes SOCKET.
BURIED_ROWS = {
    "brow":  {"west": 1, "east": 2, "north": 2, "south": 1},
    "beam1": {"west": 1, "east": 1, "north": 1, "south": 1},
    "bez":   {"west": 2, "east": 2, "north": 1, "south": 1},
    "beam2": {"west": 0, "east": 0, "north": 0, "south": 0},
    "trez":  {"west": 1, "east": 2, "north": 2, "south": 2},
    "beam3": {"west": 1, "east": 1, "north": 1, "south": 0},
    "crown": {"west": 1, "east": 0, "north": 1, "south": 1},
}

# The two beam segments are plugged at the top by the segment above them, so their tip cap is
# buried; the five tines end in the open and their tip cap is the brightest texel on the part.
CAPPED = ("beam1", "beam2")

# Which cubes get a socket row. A BRANCH leaves a cube that is not itself - the four tines leave a
# beam, and beam1 leaves the burr - and where it does the parent's surface throws a ring of shadow.
# beam2 and beam3 are not branches, they are the SAME beam carrying on, and giving their root rows a
# shadow too was the first cut of this master: eight dark rings up one antler, evenly spaced, and
# the rack read as a barber pole rather than as a shaft with tines on it. A socket is the mantle's
# SHELF and it has to be as rare here as SHELF is there.
BRANCHES = ("brow", "beam1", "bez", "trez", "crown")

# The burr is the one cube whose burial runs along COLUMNS instead of rows, because it is the one
# cube that lies half inside the helmet. Its four x columns span entity x 2.90-3.90, 3.90-4.90,
# 4.90-5.90 and 5.90-6.90 against a burial wall at 5.5, and columns 0 and 1 are wholly behind it.
# `up` loses column 2 as well, to the beam and the brow tine standing on it; `south` counts its
# columns the other way, so its buried pair is 2 and 3.
BURR_FREE = {
    "up":    (3,),
    "down":  (2, 3),
    "north": (2, 3),
    "south": (0, 1),
    "west":  (0, 1, 2),
    "east":  (),
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


def rects(name):
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


def grain() -> int:
    """The per-texel noise of a grown surface. Three times the plates' +-3, which is the pelt's
    number and the reason a Beast part does not read as sheet metal at four texels across."""
    return random.randint(-10, 10)


# ---- the burr ------------------------------------------------------------------------------------


def paint_burr(img) -> None:
    """The pedicle knot at the temple: 4 x 2 x 3, the only unrotated cube on the part, half inside
    the helmet and half outside it.

    Everything here is decided by the burial wall at entity x = 5.5. Its four x columns straddle it
    two and two, so half of every face that runs along x is filler and half is the readable knot -
    and its `west` face, the outboard end cap, is the one face of this cube nothing hides. That is
    the face the pearling is written for: three depth columns of PEARL3 over two rows, six texels,
    and they are the only place on the part where the surface is lumps rather than lines.

    Its `east` is against the skull and is INNER throughout; its `down` is the underside that clears
    the circlet's temple bar by 0.40, which is close enough that it is painted as a shadow rather
    than as a lit face."""
    f = rects("burr")

    x0, y0, fw, fh = f["west"]           # 3 deep x 2 tall, col 0 = front, row 0 = top. Fully seen.
    for j in range(fh):
        for i in range(fw):
            lum = TINE - 14 + PEARL3[i] - round(DEPTH * 0.5 * ramp(i, fw)) - (0 if j == 0 else 18)
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["up"]             # 4 wide (x) x 3 deep, rows BACK to front
    for j in range(fh):
        for i in range(fw):
            lum = (BEAM + PEARL4[i] - round(12 * ramp(j, fh))) if i in BURR_FREE["up"] else INNER
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["north"]          # 4 wide x 2 tall, col 0 = INBOARD
    for j in range(fh):
        for i in range(fw):
            lum = (FRONT + PEARL4[i] - (0 if j == 0 else 16)) if i in BURR_FREE["north"] else INNER
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["south"]          # 4 wide x 2 tall, col 0 = OUTBOARD
    for j in range(fh):
        for i in range(fw):
            lum = (BACK + PEARL4[i] - (0 if j == 0 else 14)) if i in BURR_FREE["south"] else INNER
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["down"]           # 4 wide (x) x 3 deep - the underside over the brow band
    for j in range(fh):
        for i in range(fw):
            lum = (UNDER + 14 + RIDGE4[i] // 3) if i in BURR_FREE["down"] else INNER
            put(img, x0 + i, y0 + j, lum + random.randint(-4, 4))

    fill(img, f["east"], INNER)          # against the skull for its whole area


# ---- the beams and the tines ---------------------------------------------------------------------


def paint_branch(img, name: str) -> None:
    """One rotated cube of the rack: a beam segment or a tine.

    Rows run TIP (row 0) to ROOT (the last row) because these cubes span y -L .. 0 and grow along
    -y, so the value CLIMBS down the face's rows in the reading order and the brightest row is the
    first one. BURIED_ROWS says how many rows at the root end are inside the parent or the helmet on
    each face; the row above those is the socket row and takes the parent's contact shadow. What is
    left is the fur of this part: RIDGES across the columns, a climb up the rows, and a tip row
    lifted on the two faces TIP_FACES gives this tine and dropped on the other two."""
    _, (w, h, d), _ = CUBES[name]
    f = rects(name)
    buried = BURIED_ROWS[name]
    lit = TIP_FACES.get(name, ())
    base_out = BEAM if name.startswith("beam") else TINE

    for face, base in (("west", base_out), ("east", INBOARD),
                       ("north", FRONT), ("south", BACK)):
        x0, y0, fw, fh = f[face]
        last_free = fh - 1 - buried[face]
        socket_row = last_free if name in BRANCHES else None
        span = socket_row if socket_row is not None else last_free + 1
        ridge = RIDGES[fw]
        tips = TIPS[fw]
        for j in range(fh):
            for i in range(fw):
                if j > last_free:
                    lum = INNER
                elif j == socket_row:
                    lum = base - SOCKET + ridge[i] // 3
                else:
                    lum = base + ridge[i] + round(CLIMB * (1.0 - ramp(j, max(span, 1))))
                    if face in ("west", "east"):
                        lum -= round(DEPTH * 0.4 * ramp(i, fw))
                    if j == 0:
                        lum += tips[i] if face in lit else -DROP
                put(img, x0 + i, y0 + j, lum + grain())

    # The tip cap. On the two beam segments it is plugged by the segment above and is filler; on the
    # five tines it is the end of the antler and the brightest texel the part has.
    if name in CAPPED:
        fill(img, f["up"], INNER)
    else:
        x0, y0, fw, fh = f["up"]
        for j in range(fh):
            for i in range(fw):
                put(img, x0 + i, y0 + j,
                    POLISH - round(10 * ramp(j, fh)) - round(8 * ramp(i, fw)) + grain())

    fill(img, f["down"], INNER)          # the root cap, inside whatever this grew out of


# ---- checks -------------------------------------------------------------------------------------


def check_geometry() -> None:
    """CUBES must be the cube list of the shipped geometry, in order, down to the origins. Painting
    a texture for a shape the model no longer has is invisible to every other check in this
    pipeline: both halves stay internally consistent while the rectangles slide off the faces they
    were drawn for. The origins are asserted as well as the sizes because this part's argument -
    the 0.40 over the circlet's temple bar, which columns of the burr are behind the helmet, where
    the brow tine stops in front of the face - is made entirely out of them."""
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

    # The rotations are the part, not decoration: every tine is a bone of its own and the five tips
    # land where they do because of these eight numbers. A bone silently un-rotated would leave the
    # tip table in the docstring false and nothing else in the pipeline would notice.
    rotations = {}

    def walk_bones(bone):
        rotations[bone["name"]] = tuple(bone.get("rotation", [0, 0, 0]))
        for child in bone.get("children", []):
            walk_bones(child)

    for bone in doc["bones"]:
        walk_bones(bone)
    assert rotations == {
        "burr": (0, 0, 0), "brow": (42, 0, 14), "beam1": (-12, 0, 24), "bez": (38, 0, -10),
        "beam2": (-14, 0, -12), "trez": (16, 0, 36), "beam3": (-16, 0, -6), "crown": (-8, 0, -22),
    }, f"the bone rotations have moved: {rotations}"


def check_layout() -> dict:
    """Every face rectangle must sit inside the texture and no two may overlap - a silent overlap
    would paint one cube's shading onto another's face and only show up on a model in game."""
    claimed = {}
    for name in CUBES:
        for face, (x, y, w, h) in rects(name).items():
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
    paint_burr(img)
    for name in CUBES:
        if name != "burr":
            paint_branch(img, name)

    # This master is 100% opaque - the rack is ragged in the geometry, not in the alpha - so the
    # painted set must be exactly the net: a texel short is a face the model shows and the texture
    # does not, and a texel over is paint the model never samples.
    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque == set(claimed), "painted pixels do not match the UV rectangles"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)})")


if __name__ == "__main__":
    main()
