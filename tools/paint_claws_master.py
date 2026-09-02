"""
Paint the grayscale master for the "claws" part.

Like the mantle, the pelt, the antlers and the beast head - the Beast parts this one closes the set
with - this does not merely claim that CUBES is the shipped geometry, it reads
assets/armorpieces/armorpieces/decoration/claws.json at run time and asserts it: sizes, uvs AND
origins, because every clearance below is made out of the origins (check_geometry). Output goes to
tools/decoration_masters/claws.png plus claws_guard.png, which sync_decoration_masters.py installs
for the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

This master is 100% opaque. Parts draw with armorCutoutNoCull, so a hole cut in the flank of a blade
shows the LIT INSIDE of that blade's far face, not the arm behind it - which is why no Beast part in
this mod punches its silhouette into the alpha. The two fur locks at the back of the wrist end at
two different heights because they are two different cubes on two different bones, not because
anything was cut out of a rectangle.

## What this part is

`claws` is three blades projecting past the back of the hand on the `vambraces` socket - the mod's
third part there, against the Vambraces (a closed bracer, spanning 20.00) and the Mittens (a padded
glove, spanning 17.00). Both of those are things you put your arm INTO; this is a thing that comes OUT of the arm,
and that is the whole difference: it reaches 5.37 units past the front of the chestplate sleeve and
2.17 units below the fingertips, so it is the first part on this socket that changes the arm's
outline rather than its surface: it spans 22.96 across the figure where the vambraces spans 20.00.

`vambraces` rides the ARM - Attachment.of(LEFT_ARM, 1, 6, 0) plus Attachment.mirrored on the right -
so the part swings with the limb and ONE master serves both forearms through the layer's
scale(-1, 1, 1). `west` is geo +x, outboard on both arms; `east` is geo -x, toward the body on both.

## The cubes, in the part's frame, in the arm bone's, and in the entity's

Part-local is the frame the geometry JSON is written in; bone-local is that plus the anchor's
(1, 6, 0); entity is bone-local plus the left arm's pivot (5, 2, 0), so entity = part + (6, 8, 0).
+Y is DOWN. Rotated cubes are given as their axis-aligned hull.

    cube     bone     size       part x          part y          part z          entity z
    cuff     bracer   4 x 2 x 7  -0.50 .. 3.50  -2.20 .. -0.20  -3.60 ..  3.40  -3.60 ..  3.40
    knuckle  bracer   4 x 3 x 3  -0.40 .. 3.60  -0.30 ..  2.70  -3.90 .. -0.90  -3.90 .. -0.90
    blade_a  blade_a  1 x 2 x 4  -1.71 .. 0.76   0.79 ..  4.24  -7.79 .. -3.25  -7.79 .. -3.25
    blade_b  blade_b  1 x 2 x 5   0.94 .. 2.12   1.51 ..  6.17  -8.37 .. -3.17  -8.37 .. -3.17
    blade_c  blade_c  1 x 2 x 3   2.44 .. 4.45   0.94 ..  3.69  -6.96 .. -3.38  -6.96 .. -3.38
    lock_a   lock_a   2 x 4 x 2   1.43 .. 4.09  -1.17 ..  3.12   0.40 ..  2.40   0.40 ..  2.40
    lock_b   lock_b   2 x 5 x 2   1.89 .. 5.48  -1.41 ..  3.97   2.50 ..  4.50   2.50 ..  4.50

`cuff` and `knuckle` are the two cubes of the unrotated root bone and they are the BINDING: a band
round the forearm and a plate over the back of the hand. Everything else is on a bone of its own:

    bone     pivot (part frame)    rotation        what it is
    bracer   (0, 0, 0)             -               the band and the knuckle plate
    blade_a  (0.15, 1.7, -3.8)     ( 24,  20, 0)   the inboard blade, medium, swung inboard
    blade_b  (1.60, 2.3, -3.8)     ( 38,   2, 0)   the middle blade, the longest, swept furthest down
    blade_c  (3.00, 1.9, -3.8)     ( 16, -18, 0)   the outboard blade, the shortest, swung outboard
    lock_a   (2.50, -0.5, 1.4)     (  0,   0, -10) the short fur lock at the back of the band
    lock_b   (3.00, -0.6, 3.5)     (  0,   0, -20) the long one behind it

These are the only Y rotations in the Beast set, and they are here because nothing else splays a
fan. A blade points along -z, and a Z rotation does nothing to a vector already lying on the z axis;
X pitches it down, Y swings it sideways. So the three blades' 20 / 2 / -18 about Y are what open the
hand, and their 24 / 38 / 16 about X are what curl it. The two locks are the mantle's rule instead -
a negative Z rotation carries a HANGING cube's lower end toward +x, which is outboard on both arms
after the mirror - and they are -10 and -20 because the mantle's four locks are -6, -6, -10 and -16
and a lock that leaves the mass at the same angle as its neighbour is not a second lock.

WHERE THE POINTS LAND, which is this part's version of the pelt's hem line:

    blade      tip at entity z   tip at entity y   swing at entity x
    blade_a        -7.79             12.24          4.29 (inboard)
    blade_b        -8.37             14.17          6.94
    blade_c        -6.96             11.69         10.45 (outboard)

    lock       hem at entity y   outboard face at entity x
    lock_a          11.12               10.09
    lock_b          11.97               11.48

Three blades of three lengths at three pitches and three swings, and two locks whose hems are 0.85
apart and whose outboard faces are 1.39 apart. No two elements of this part are the same size, at
the same angle, or end in the same place - the rule the pelt states as a hem with no two equal steps
and the antlers as five tines at five heights.

## What clears what

The surfaces this part is measured against, in part-local coordinates:

    the arm's chestplate shell   x -3 .. 3    y -9 .. 5    z -3 .. 3
    the naked arm                x -2 .. 2    y -8 .. 4    z -2 .. 2
    the fingertips               y = 4        (the bottom of the arm box)

Four numbers decide the whole part:

  * **z = -3 is the sleeve's front wall.** The knuckle plate stands 0.90 past it and the band 0.60,
    which is what makes them read as hardware strapped ON the arm rather than as paint on it. The
    blades then leave from part z = -3.8, a tenth inside the plate's own front face, so they grow
    out of it instead of floating in front of it.

  * **x = 3 is the sleeve's outboard wall**, and the band reaches 3.50 and the plate 3.60. The
    inboard halves of both are inside the sleeve and are painted INNER; their `west` faces are the
    hero of the part, because a forearm is seen from the side more than from anywhere else.

  * **y = 4 is where the hand ends.** blade_b reaches part y 6.17, so the longest blade hangs 2.17
    units past the fingertips; blade_a reaches 4.24 and blade_c 3.69, which stops short of them.
    One blade past the hand, one level with it and one inside its reach is what makes the three read
    as a hand rather than as a fork.

  * **part y = -2.20 is the top of the band.** The pauldrons socket sits on the same arm bone and
    the tallest thing the mod puts there, this set's own beast head, reaches bone y 2.22, which is
    part y -3.78 here. The band therefore clears the beast head by 1.58 and the shipped mantle by
    2.58, which is what trace_geometry's "all clear by more than half a unit" is reporting.

No face of this part lies in a plane of any shell. Only the two cubes of the root bone could - the
other five are on rotated bones, and a rotated face can never be coplanar with an axis-aligned
shell - and their twelve faces are at part x -0.50 / 3.50 / -0.40 / 3.60, y -2.20 / -0.20 / -0.30 /
2.70 and z -3.60 / 3.40 / -3.90 / -0.90, none of which is a wall of anything. The band and the plate
overlap each other over part y -0.30 .. -0.20 rather than meeting, so there is no shared plane
inside the part either.

## Why the master is shaded the way it is

Half of this part is hide and half of it is claw, and they have to be told apart at four texels
across. Three ideas, and no fourth:

  1. **Clumps on the binding.** The band, the plate and the two locks take a per-COLUMN tone offset
     out of a hand-written table - CLUMP7 / CLUMP4 / CLUMP3 / CLUMP2 below, one per face width. They
     are written and not generated, and the point of them is the pelt's point: no two consecutive
     steps are equal and the sequence never repeats. The grain under them is +-10, three times the
     plate parts' +-3, which is what the whole Beast set uses to say "grown, not forged".

  2. **A keel on the blades.** A blade's `down` face is its cutting edge and runs to EDGE, the
     brightest value on the part; its two flanks fall away from the edge toward the back of the
     blade; its `up` face - the spine - is a step under the flanks. That gradient across three
     surfaces is the only thing that separates a blade from a stick at one texel of thickness, and
     it is deliberately NOT the clump treatment: the binding is lumpy and the claws are smooth, and
     a player has to be able to see which of the two the guard fitting is going to recolour.

  3. **Three different tips.** TIP_FACES names, per blade, which two of its four long faces catch
     the light at the point and which two are dropped, and no two blades get the same pair. Three
     points lit identically are three bright bars - the failure the last batch of parts kept
     finding - and three lit from three sides are three claws.

Under all three is the standing-figure key the spaulders, the mantle and the pelt share - lit from
above, from the front and from outboard - and one shape-specific value, SOCKET, on the row where a
lock leaves the band. That is the mantle's SHELF, and like the antlers it is used sparingly: only
the two locks get it, because only they hang out from under something.

Value calibration, the same one every master here is held to: the material ramp interpolates
dark -> mid over master values 0 .. 127 and mid -> light over 128 .. 255, so a master confined to
the top half only ever uses half of a material's ramp. Here the blades' edges saturate while the
locks' pile, the band's underside and the buried faces sit well under 127, so the visible texels
alone span the ramp - the line main() prints at the end is that range.

## The fitting

One fitting, `armorpieces:guard`, and it is exactly the three blades - every face of blade_a,
blade_b and blade_c and nothing else. That split is the point of the part: the binding keeps the
material the piece was smithed in and the claws take a second metal, so a player can wear leather-
coloured straps with netherite claws, or gold straps with iron ones. It is the mod's cleanest case
for `guard`, because a guard is meant to be the part of an object that does the work, and on this
part the blades are unambiguously that.

There is deliberately no `_static.png`. A static layer would fix the binding's colour and the part
would then look identical in all sixteen materials, which is the one thing a decoration in this mod
must not do - and it would also spend the trim material on the blades alone, which is the fitting's
job and not the master's.

## The unwrap

The face rectangles come from paint_circlet_master.faces(), copied verbatim: row one (v .. v+d)
holds up then down, each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west,
south with widths d, w, d, w. Note the row-two order: the two thin d-wide faces come FIRST and
THIRD. The seven cubes take two rows of the sheet, 0 .. 9 and 9 .. 15.

Orientation inside each rectangle is the table PLAN.md records as measured, not recalled:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x              max z
    down            +y  (underside)      min x              max z
    west            +x  (outboard)       min z  (front)     min y (top)
    east            -x  (inboard)        max z  (back)      min y (top)
    north           -z  (front)          min x  (inboard)   min y (top)
    south           +z  (back)           max x  (outboard)  min y (top)

The three blade cubes span z -L .. 0 and grow along -z, so on THEM `north` is the point and `south`
is the root inside the plate, and column 0 of `west` is the TIP while column 0 of `east` is the
root. That is the third inversion in this set - the antlers' tines grow along -y and the beast
head's ears with them - and it is the one thing about this net a reader has to hold on to.

Blockbench's `west` is the geo +x face - the one pointing away from the body for a left-side part -
and `east` is the one against it. That is what lets one master serve both forearms: after the
layer's scale(-1, 1, 1) the geo +x face of the mirrored copy still points outboard, so
lit-outboard / shadowed-inboard survives the mirror and the pair reads as a pair.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image

from fitting_mask import write_mask

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "claws.json"
OUT = ROOT / "tools" / "decoration_masters" / "claws.png"

TEX_W, TEX_H = 64, 32

# origin, size (w, h, d) and uv (u, v), mirroring claws.json in that file's own order, which is the
# order walk() visits: the root bone's band and plate, then the three blades, then the two locks.
# Origins are asserted as well as sizes because this part's whole argument - what stands proud of
# the sleeve, where the blades leave the plate, how far past the fingertips they reach - is made out
# of them.
CUBES = {
    "cuff":    ((-0.5, -2.2, -3.6), (4, 2, 7), (0, 0)),
    "knuckle": ((-0.4, -0.3, -3.9), (4, 3, 3), (22, 0)),
    "blade_a": ((-0.5, -1, -4), (1, 2, 4), (36, 0)),
    "blade_b": ((-0.5, -1, -5), (1, 2, 5), (46, 0)),
    "blade_c": ((-0.5, -1, -3), (1, 2, 3), (0, 9)),
    "lock_a":  ((-1, -0.5, -1), (2, 4, 2), (8, 9)),
    "lock_b":  ((-1, -0.5, -1), (2, 5, 2), (16, 9)),
}

BLADES = ("blade_a", "blade_b", "blade_c")
LOCKS = ("lock_a", "lock_b")

random.seed(0x434C4157)  # deterministic output - regenerating must not churn the PNG

# Calibrated against the ramp, not guessed, and pitched in the same register as pelt.py, mantle.py,
# antlers.py and beast_head.py so the five Beast parts sit together on one figure.
EDGE = 222      # a blade's cutting edge and its point - the brightest thing on the part
BLADE = 188     # a blade's outboard flank
SPINE = 150     # a blade's back - the one long face that is not lit
HIDE = 172      # the band's outboard face, the hero of the binding
STRAP = 152     # the plate's front, and any lit hide face turned forward
FUR = 166       # a lock's outboard face
NAPE = 118      # hide facing backward or inboard, in its own shadow
PILE = 88       # deep pile: fur disappearing under the band
SOCKET = 44     # how far the row where a lock leaves the band falls below that face
INNER = 62      # buried: in the sleeve, in the band, or in the plate
UNDER = 46      # a free underside

FALL = 22       # top-to-bottom falloff down a standing face
DEPTH = 26      # front-to-back falloff across a flank
LIFT = 16       # inboard-to-outboard brightening across a face's width
DROP = 26       # how far an unlit face falls at a blade's point

# Hand-written, not generated, and read along a face's columns. Changing one of these numbers moves
# a clump, which is a design edit and not a tuning knob. Same amplitudes as the pelt's.
CLUMP7 = (20, -30, 8, -18, 34, -12, 26)   # seven columns: the band's flanks, front to back
CLUMP4 = (-28, 18, 32, -14)               # four: the band's ends and the plate's front
CLUMP3 = (-22, 32, -8)                    # three: the plate's flanks
CLUMP2 = (18, -26)                        # two: a lock, and any two-wide face
HEM2 = (-30, 40)                          # per-column tip / trough on a FREE hem row, two wide
CLUMPS = {2: CLUMP2, 3: CLUMP3, 4: CLUMP4, 7: CLUMP7}

# Which two of a blade's four long faces catch the light at the point, and which two are dropped.
# Three blades, three different pairs; see idea 3 in the module docstring.
TIP_FACES = {
    "blade_a": ("west", "down"),
    "blade_b": ("down", "east"),
    "blade_c": ("west", "up"),
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
    """The per-texel noise of a hide. Three times the plates' +-3, which is the pelt's number and
    the reason a Beast part does not read as sheet metal at four texels across."""
    return random.randint(-10, 10)


def smooth() -> int:
    """The per-texel noise of a claw. A blade is the one thing on this part that is NOT grown out of
    hair, and painting it with the hide's grain is what made the first cut read as seven pieces of
    the same material."""
    return random.randint(-3, 3)


# ---- the binding ---------------------------------------------------------------------------------


def paint_cuff(img) -> None:
    """The band round the forearm: 4 x 2 x 7, standing 0.50 outboard of the sleeve, 0.60 past its
    front wall and 0.40 past its back.

    Its `west` is fourteen texels and nothing hides any of them but one corner of the long lock, so
    it takes CLUMP7 down its whole depth and carries the binding's reading. Its `east` is inside the
    sleeve except for its front column, which crosses the shell's front wall at z = -3; its `up` and
    `down` are inside the sleeve except for the front row, and `down` is under the plate and the two
    locks besides."""
    f = rects("cuff")

    x0, y0, fw, fh = f["west"]           # 7 deep x 2 tall, col 0 = front, row 0 = top
    for j in range(fh):
        for i in range(fw):
            buried = j == 1 and i == fw - 1        # the long lock's top-front corner
            lum = INNER if buried else \
                HIDE + CLUMP7[i] - round(DEPTH * 0.5 * ramp(i, fw)) - round(FALL * 0.5 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["north"]          # 4 wide x 2 tall, col 0 = inboard. 0.60 proud of the shell.
    for j in range(fh):
        for i in range(fw):
            lum = STRAP + CLUMP4[i] + round(LIFT * ramp(i, fw)) - round(FALL * 0.5 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["south"]          # 4 wide x 2 tall, col 0 = OUTBOARD; the locks hang on it
    for j in range(fh):
        for i in range(fw):
            lum = INNER if (j == 1 and i < 2) else \
                NAPE + CLUMP4[i] + round(LIFT * (1.0 - ramp(i, fw))) - round(FALL * 0.4 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["east"]           # 7 deep x 2 tall, col 0 = BACK; only the front column shows
    for j in range(fh):
        for i in range(fw):
            lum = (PILE + CLUMP7[i] // 2 - round(FALL * 0.4 * ramp(j, fh))) if i == fw - 1 else INNER
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["up"]             # 4 wide (x) x 7 deep, rows BACK to front; front row only
    for j in range(fh):
        for i in range(fw):
            lum = (NAPE + 18 + CLUMP4[i] // 2) if j == fh - 1 else INNER
            put(img, x0 + i, y0 + j, lum + grain())

    fill(img, f["down"], INNER)          # in the sleeve, under the plate, under both locks


def paint_knuckle(img) -> None:
    """The plate over the back of the hand: 4 x 3 x 3, standing 0.90 past the sleeve's front wall
    and 0.60 outboard of it, with the three blades leaving its front face.

    Its `north` is the plate's face and the only place on the part where a viewer can see all three
    blade roots at once, so its bottom row - the row they come through - is dropped to SOCKET
    everywhere except the one column no blade crosses. Its `up` is entirely inside the band above
    it, which is the joint that keeps the two pieces of binding reading as one strap."""
    f = rects("knuckle")

    x0, y0, fw, fh = f["west"]           # 3 deep x 3 tall, col 0 = front, row 0 = top. All seen.
    for j in range(fh):
        for i in range(fw):
            lum = HIDE - 10 + CLUMP3[i] - round(DEPTH * 0.4 * ramp(i, fw)) \
                - round(FALL * 0.4 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["north"]          # 4 wide x 3 tall, col 0 = inboard. The plate's face.
    for j in range(fh):
        for i in range(fw):
            lum = STRAP + CLUMP4[i] + round(LIFT * ramp(i, fw)) - round(FALL * 0.5 * ramp(j, fh))
            if j == fh - 1 and i != 2:
                lum = STRAP - SOCKET - 14 + CLUMP4[i] // 3   # the row the blades come through
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["east"]           # 3 deep x 3 tall, col 0 = BACK; only the front column shows
    for j in range(fh):
        for i in range(fw):
            lum = (PILE + 14 + CLUMP3[i] // 2 - round(FALL * 0.4 * ramp(j, fh))) \
                if i == fw - 1 else INNER
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["south"]          # 4 wide x 3 tall, col 0 = OUTBOARD; only that column shows
    for j in range(fh):
        for i in range(fw):
            lum = (NAPE - 10 + CLUMP4[i] // 2) if i == 0 else INNER
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["down"]           # 4 wide (x) x 3 deep, rows BACK to front. The plate's sole.
    for j in range(fh):
        for i in range(fw):
            free = i == fw - 1 or j == fh - 1
            lum = (UNDER + 16 + CLUMP4[i] // 3 + round(12 * ramp(j, fh))) if free else INNER
            put(img, x0 + i, y0 + j, lum + random.randint(-4, 4))

    fill(img, f["up"], INNER)            # wholly inside the band


# ---- the blades ----------------------------------------------------------------------------------


def paint_blade(img, name: str) -> None:
    """One claw. These cubes span z -L .. 0 and grow along -z, so `north` is the point, `south` is
    the root inside the plate, and column 0 of `west` is the TIP while column 0 of `east` is the
    root - `east` counts its columns back to front.

    The keel is the whole idea: `down` is the cutting edge and runs to EDGE, the two flanks fall
    away from it, and `up` - the blade's back - is a step under both. A claw at one texel of
    thickness has no room for a shape, so the shape has to be a gradient across the three surfaces
    that meet at the edge. TIP_FACES then says which two of the four catch the light at the point,
    and no two blades are given the same pair."""
    _, (w, h, d), _ = CUBES[name]
    f = rects(name)
    lit = TIP_FACES[name]

    x0, y0, fw, fh = f["west"]           # d cols of z (0 = TIP) x h rows. The hero flank.
    for j in range(fh):
        for i in range(fw):
            lum = BLADE - round(DEPTH * 0.5 * ramp(i, fw)) + (10 if j == fh - 1 else -10)
            if i == 0:
                lum += 18 if "west" in lit else -DROP
            put(img, x0 + i, y0 + j, lum + smooth())

    x0, y0, fw, fh = f["east"]           # d cols of z (0 = ROOT) x h rows. The inboard flank.
    for j in range(fh):
        for i in range(fw):
            lum = BLADE - 46 + round(DEPTH * 0.4 * ramp(i, fw)) + (8 if j == fh - 1 else -8)
            if i == fw - 1:
                lum += 18 if "east" in lit else -DROP
            put(img, x0 + i, y0 + j, lum + smooth())

    x0, y0, fw, fh = f["down"]           # w wide (x) x d deep, rows BACK to front. The cutting edge.
    for j in range(fh):
        for i in range(fw):
            lum = EDGE - round(20 * (1.0 - ramp(j, fh)))
            if j == fh - 1:
                lum += 8 if "down" in lit else -DROP
            put(img, x0 + i, y0 + j, lum + smooth())

    x0, y0, fw, fh = f["up"]             # w wide (x) x d deep, rows BACK to front. The blade's back.
    for j in range(fh):
        for i in range(fw):
            lum = SPINE - round(14 * (1.0 - ramp(j, fh)))
            if j == fh - 1:
                lum += 16 if "up" in lit else -DROP // 2
            put(img, x0 + i, y0 + j, lum + smooth())

    x0, y0, fw, fh = f["north"]          # w x h. The point itself - the smallest, brightest face.
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j, EDGE - 4 - round(16 * ramp(j, fh)) + smooth())

    fill(img, f["south"], INNER, 2)      # the root, inside the plate


# ---- the fur locks -------------------------------------------------------------------------------


def paint_lock(img, name: str) -> None:
    """One lock of fur at the back of the band. These hang: row 0 is the top, inside the band, row 1
    is the row the band's underside crosses and takes SOCKET, and the last row is a free hem and
    takes HEM2 - one column lifted, one dropped, so the hem is not a cut edge.

    That is the mantle's lock, at a third of the size, and it is here so that the one part of this
    set that is mostly hardware still has fur on it."""
    f = rects(name)
    _, (w, h, d), _ = CUBES[name]
    hem = h - 1

    def hang(base: int, i: int, j: int, clump) -> int:
        if j == 0:
            return INNER                                   # inside the band
        if j == 1:
            # The band's underside crosses this row. SOCKET as a DROP from the face rather than as
            # an absolute: a lock is four rows tall and two of them are already buried, so an
            # absolute 74 here left the whole lock reading as a dark stub against a lit band.
            return base - SOCKET + clump[i] // 3
        lum = base + clump[i] - round(FALL * 0.5 * ramp(j - 1, h - 1))
        if j == hem:
            lum += HEM2[i % 2]
        return lum

    x0, y0, fw, fh = f["west"]           # d cols of z (0 = front) x h rows. The hero face.
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j, hang(FUR, i, j, CLUMP2) + grain())

    x0, y0, fw, fh = f["south"]          # w cols of x (0 = OUTBOARD) x h rows
    for j in range(fh):
        for i in range(fw):
            lum = hang(NAPE + 12, i, j, CLUMP2)
            if j > 1:
                lum += round(LIFT * 0.5 * (1.0 - ramp(i, fw)))
            put(img, x0 + i, y0 + j, lum + grain())

    # `north` looks at the back of the band over its top row and its inboard column is in the
    # sleeve; only the outboard column below the top row is ever seen.
    x0, y0, fw, fh = f["north"]
    for j in range(fh):
        for i in range(fw):
            free = i == fw - 1 and j > 0
            lum = hang(PILE + 10, i, j, CLUMP2) if free else INNER
            put(img, x0 + i, y0 + j, lum + grain())

    # `east` is against the sleeve for its whole area on the short lock; on the long one the BACK
    # column stands 1.50 past the shell's back wall and is seen from behind the wearer.
    x0, y0, fw, fh = f["east"]
    for j in range(fh):
        for i in range(fw):
            free = name == "lock_b" and i == 0 and j > 0
            lum = hang(PILE, i, j, CLUMP2) if free else INNER
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["down"]           # w wide (x) x d deep. The hem's sole.
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j,
                UNDER + CLUMP2[i] // 3 + round(14 * ramp(j, fh)) + random.randint(-4, 4))

    fill(img, f["up"], INNER)            # under the band


# ---- checks -------------------------------------------------------------------------------------


def check_geometry() -> None:
    """CUBES must be the cube list of the shipped geometry, in order, down to the origins. Painting
    a texture for a shape the model no longer has is invisible to every other check in this
    pipeline: both halves stay internally consistent while the rectangles slide off the faces they
    were drawn for. The origins are asserted as well as the sizes because this part's argument -
    what stands proud of the sleeve, where the blades leave the plate, how far past the fingertips
    they reach - is made entirely out of them."""
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

    # Five cubes hang off rotated bones and the pivots are what put them where the prose says they
    # are - the fan of three blades, the two locks' hems. The three Y rotations in particular are
    # the only ones in the Beast set and the only thing that opens the hand; a bone silently
    # un-rotated would leave every number in the docstring false and nothing else here would notice.
    bones = {}

    def walk_bones(bone):
        bones[bone["name"]] = (tuple(bone.get("pivot", [0, 0, 0])),
                               tuple(bone.get("rotation", [0, 0, 0])))
        for child in bone.get("children", []):
            walk_bones(child)

    for bone in doc["bones"]:
        walk_bones(bone)
    assert bones == {
        "bracer": ((0, 0, 0), (0, 0, 0)),
        "blade_a": ((0.15, 1.7, -3.8), (24, 20, 0)),
        "blade_b": ((1.6, 2.3, -3.8), (38, 2, 0)),
        "blade_c": ((3, 1.9, -3.8), (16, -18, 0)),
        "lock_a": ((2.5, -0.5, 1.4), (0, 0, -10)),
        "lock_b": ((3, -0.6, 3.5), (0, 0, -20)),
    }, f"the bones have moved: {bones}"


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
    paint_cuff(img)
    paint_knuckle(img)
    for blade in BLADES:
        paint_blade(img, blade)
    for lock in LOCKS:
        paint_lock(img, lock)

    # This master is 100% opaque - the fan is opened in the geometry and the hems are hems - so the
    # painted set must be exactly the net: a texel short is a face the model shows and the texture
    # does not, and a texel over is paint the model never samples.
    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque == set(claimed), "painted pixels do not match the UV rectangles"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)})")

    # The guard takes the three blades and nothing else; the binding keeps the base material.
    blades = [r for name in BLADES for r in rects(name).values()]
    write_mask(img, blades, OUT.with_name("claws_guard.png"))


if __name__ == "__main__":
    main()
