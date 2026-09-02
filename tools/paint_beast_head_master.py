"""
Paint the grayscale master for the "beast_head" part.

Like the mantle, the pelt and the antlers - the Beast parts this one is written to sit beside - this
does not merely claim that CUBES is the shipped geometry, it reads
assets/armorpieces/armorpieces/decoration/beast_head.json at run time and asserts it: sizes, uvs AND
origins, because every clearance below is made out of the origins (check_geometry). Output goes to
tools/decoration_masters/beast_head.png plus beast_head_gemstone.png, which
sync_decoration_masters.py installs for the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

This master is 100% opaque. Parts draw with armorCutoutNoCull, so a hole cut in a face shows the LIT
INSIDE of the face behind it, which is why no Beast part in this mod punches its silhouette into the
alpha - the mantle's fur, the pelt's hem and the antlers' rack all carry their raggedness in
geometry, and so does this. The open mouth here is a real gap between two cubes, not a hole in a
texture, and the scruff's hem is a real hem.

## What this part is

`beast_head` is a snarling animal head over each shoulder on the `pauldrons` socket - the mod's
third part there, against the Spaulders (a hard plate cap, 0.50 proud, spanning 20.65) and the
Mantle (a fur ruff, 3.50 proud, spanning 22.89). This one stands 6.06 units proud of the chestplate
shoulder and spans 23.60, which makes it the tallest thing the mod puts on a shoulder; it is meant
to be read as a trophy the wearer is carrying, not as armour they are wearing.

`pauldrons` rides the ARM - Attachment.of(LEFT_ARM, 1, 0, 0) plus Attachment.mirrored on the right -
so the whole part swings with the limb and ONE master serves both shoulders through the layer's
scale(-1, 1, 1). That is also the hard constraint on the shape, and the reason the plan forbids a
yoke or a chain here: nothing may reach across to the other shoulder, because anything joining the
two tears apart on the first stride. Every cube below is inside one arm's own frame; the two copies
are 15.6 units apart at their closest with the whole torso between them.

## The cubes, in the part's frame, in the arm bone's, and in the entity's

Part-local is the frame the geometry JSON is written in; bone-local is that plus the anchor's
(1, 0, 0); entity is bone-local plus the left arm's pivot (5, 2, 0). +Y is DOWN. Rotated cubes are
given as their axis-aligned hull.

    cube     bone     size       part x         part y          part z          entity x
    skull    head     4 x 5 x 5  1.80 .. 5.80  -6.20 .. -1.20  -1.90 ..  3.10   7.80 .. 11.80
    muzzle   head     2 x 2 x 4  2.80 .. 4.80  -4.60 .. -2.60  -5.20 .. -1.20   8.80 .. 10.80
    jaw      jaw      2 x 1 x 4  2.68 .. 4.83  -2.98 .. -0.11  -5.04 .. -1.04   8.68 .. 10.83
    ear_in   ear_in   1 x 3 x 2  1.86 .. 3.63  -9.06 .. -5.61  -0.38 ..  2.11   7.86 ..  9.63
    ear_out  ear_out  1 x 2 x 2  4.08 .. 5.73  -8.13 .. -5.44   0.54 ..  3.06  10.08 .. 11.73
    scruff   scruff   3 x 3 x 2  1.80 .. 5.44  -3.41 ..  0.22   2.00 ..  4.00   7.80 .. 11.44

`skull` and `muzzle` are the two cubes of the unrotated root bone: the cranium, and a snout half its
width jutting 3.30 units past the front of the shoulder shell. The other four each have a bone of
their own, and every one of those rotations is doing a job:

    bone     pivot (part frame)   rotation      what it is
    head     (0, 0, 0)            -             cranium and snout
    jaw      (3.80, -2.4, -1.0)   ( 28, 0,  3)  the lower jaw, dropped open along its length
    ear_in   (3.10, -5.9,  0.6)   (-10, 0, -14) the inboard ear, tall, canted back and inward
    ear_out  (4.65, -5.9,  1.4)   (-18, 0,  16) the outboard ear, SHORT, canted back and outward
    scruff   (3.55, -2.3,  2.7)   (  0, 0, -14) the ruff of hide at the nape, hanging outboard

The jaw's +28 about X drops its forward end and only its forward end, which is what opens a mouth
without modelling a hinge: the hinge end stays 0.67 units INSIDE the snout, the two surfaces part
company 2.16 units along the jaw, and by the front the gape is 1.55 units - a fifth of the head's
whole height. The snout still leads the chin by 0.16, so the upper jaw overhangs the lower, which is
what a snarl looks like and what an even bite does not. The two ears are three units and two units long and lean 30 degrees apart - the Beast rule
that no two of a part's repeated elements may be the same, which the pelt states as a hem with no
two equal steps and the antlers as five tines at five heights. One good ear and one short one is
what a head that has been fought over looks like.

## What clears what

The surfaces this part is measured against, in part-local coordinates:

    the arm's chestplate shell    x -3 .. 3    y -3 .. 11   z -3 .. 3
    the naked arm                 x -2 .. 2    y -2 .. 10   z -2 .. 2
    the torso's chestplate shell  x <= -1      y >= -3      z -3 .. 3
    the helmet at rest            x <= -1      y -11 .. -1

Four numbers decide the whole part:

  * **y = -3 is the shoulder line** - the top of both chestplate shells. The skull's top is at -6.20
    and the taller ear reaches -9.06, so the part stands 3.20 and 6.06 proud. Below that line and
    inside |x| < 3 it is inside the sleeve and is painted INNER: that is the bottom two rows of the
    skull's `east` face, the inboard column of its `down`, the back half of the jaw's `east`, and
    the inboard column of the scruff's `north`. The three rows above those on the skull's `east`
    are NOT filler - they look across the 2.80-unit gap between this part and the wearer's own neck
    and are seen from the front, which is the one thing this part does not share with the mantle,
    whose whole inboard face is buried in the chest.

  * **x = 3 is the sleeve's outboard wall**, and this part starts at 1.80 - so 1.20 units of the
    skull's width is inside the shoulder and 2.80 hangs outboard of it. That is a smaller bite than
    the mantle takes and it is bought deliberately; see the next number.

  * **x = 1.75 is where a turned head stops.** Vanilla lets the head lead the body by 50 degrees,
    and at that yaw the helmet's outermost corner sweeps to entity x = 5 * (cos 50 + sin 50) = 7.04
    for the 1.0 shell and 5.5 * (cos 50 + sin 50) = 7.75 for the `hat` layer over it, which is
    part x 1.04 and 1.75. The Mantle's report records the first of those and admits its ruff cannot
    clear it. This part clears BOTH: its inboard face is at part x 1.80, entity 7.80, and the
    lowest inboard point of any cube - the scruff's, at 1.80 - is the same. A helmeted player can
    look as far over their shoulder as vanilla allows and the beast head does not move through
    their own helmet. It is the only part on this socket that can say that, and the 0.05 is the
    whole margin, so 1.80 must not be tidied to 1.75 or to 1.5.

  * **z = -3 is the shell's front wall**, and the snout reaches -5.20 and the open jaw -5.04. The
    head therefore leads the shoulder by more than three units, which is what stops it reading as a
    lump on the arm: from directly in front of the wearer - and from the wearer's own camera, which
    looks down at their shoulders - the snout is the silhouette and the shoulder behind it is not.
    At the back the scruff reaches z = 4.00, a full unit past the shell's back wall, so the part
    breaks the outline in both directions.

Cross-socket, on the same arm bone, trace_geometry reports the vambraces and the mittens clear by
more than half a unit: the lowest thing here is the scruff's hem at bone y 0.22 and the bracer
starts at bone y 4.00. The three sockets that could have fouled this one draw on the BODY bone, so
no tool compares them and they were measured by hand against the same numbers the mantle used:

  * `collar`'s **gorget** puts a shoulder tab at entity x 4.5 .. 6.5. Nothing here is inboard of
    7.80, so it clears by 1.30 - where the mantle's ruff runs straight through that tab.
  * `back`'s **pinions** reach entity x 6.4, **wing_roots** 4.53 and **banner** 3.5. All three are
    inboard of 7.80 and none of them is touched.

No face of this part lies in a plane of any shell. Only the two cubes of the root bone could - the
other four are on rotated bones, and a rotated face can never be coplanar with an axis-aligned
shell - and their twelve faces are at part x 1.80 / 5.80 / 2.80 / 4.80, y -6.20 / -1.20 / -4.60 /
-2.60 and z -1.90 / 3.10 / -5.20 / -1.20, none of which is a wall of anything. The skull's back
face at z = 3.10 is a tenth past the shell's z = 3 rather than on it, which is the same tenth the
pelt buys its fractional origins for.

Inside the part, the one pair of faces that could have been coplanar is the snout's back against
the cranium's front: the muzzle is written to run back to z = -1.20, seven tenths INSIDE the skull's
front face at -1.90, so the two overlap rather than meet.

## Why the master is shaded the way it is

A head is the one Beast shape with a face on it, and a face at this size is three marks: eyes, nose,
teeth. Everything else on the part is the same fur the mantle and the pelt are made of, and it is
painted with the same three ideas and no fourth:

  1. **Clumps.** Every fur face takes a per-COLUMN tone offset out of a hand-written table -
     CLUMP5 / CLUMP4 / CLUMP3 / CLUMP2 below, one per face width. They are written and not
     generated, and the point of them is the pelt's point: no two consecutive steps are equal and
     the sequence never repeats, so nothing here can strike the eye as a pattern. The tables are
     the pelt's own amplitudes, because these two parts are hide on the same body.

  2. **A broken hem.** The scruff's bottom row is the only free hem on the part, and it takes HEM3 -
     one column lifted past the tip value, one dropped under the pile, one between. A hem uniform in
     value reads as a cut edge whatever the geometry does. The ears' tips take the same treatment
     from the other end: they are DARKER than their roots, which is the wolf's own marking and the
     opposite of the antlers' climb, and it is what stops two ears of different lengths reading as
     two bright bars.

  3. **The maw.** This is the idea the other Beast parts do not have. The inside of the mouth is
     MAW, the darkest value on the part, and the four fangs are FANG, the brightest; they sit
     directly against each other on the jaw's `up` face and the muzzle's `down` face, which are the
     two surfaces the open jaw exposes. That contrast is doing the whole snarl - without it a head
     with its mouth open is a head with a crack in it. The fangs are broken across their columns
     rather than laid in a row for the same reason the hem is: four even teeth are a comb.

Under all three is the standing-figure key the spaulders, the mantle and the pelt share - lit from
above, from the front and from outboard - plus the per-texel grain of +-10 that every Beast part
carries, three times the plate parts' +-3, because at four texels across a cheek the only thing
separating fur from sheet metal is whether neighbouring texels agree.

Value calibration, the same one every master here is held to: the material ramp interpolates
dark -> mid over master values 0 .. 127 and mid -> light over 128 .. 255, so a master confined to
the top half only ever uses half of a material's ramp. Here the fangs and the skull's crown
saturate while the maw, the nose and the buried faces sit well under 127, so the visible texels
alone span the ramp - the line main() prints at the end is that range.

## The fitting

One fitting, `armorpieces:gemstone`, and it is four texels: the two eyes on the skull's `north` face
and the two brow texels directly above them on the front edge of its `up` face. That is the
smallest fitting in the mod and the size is the argument. An eye at this scale IS one texel; two
texels of eye plus the brow they fold over is the largest a pair of eyes can be before it stops
being eyes and becomes a mask over the whole face. Taking the brow as well as the eye is what makes
it visible from the direction a player actually looks at their own shoulder from, which is above.

The mask carries the master's own values, so the eyes are painted bright and the face around them
dropped to frame them: with the fitting empty they read as a pale stare in the trim material, and
with a gem in they light in the gem's own colour. There is deliberately no `_static.png` - a static
layer would fix the hide's colour and the part would look identical in all sixteen materials, which
is the one thing a decoration in this mod must not do.

## The unwrap

The face rectangles come from paint_circlet_master.faces(), copied verbatim: row one (v .. v+d)
holds up then down, each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west,
south with widths d, w, d, w. Note the row-two order: the two thin d-wide faces come FIRST and
THIRD. The six cubes fill exactly one 64-wide row, 0 .. 64, ten rows deep.

Orientation inside each rectangle is the table PLAN.md records as measured, not recalled:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x              max z
    down            +y  (underside)      min x              max z
    west            +x  (outboard)       min z  (front)     min y (top)
    east            -x  (inboard)        max z  (back)      min y (top)
    north           -z  (front)          min x  (inboard)   min y (top)
    south           +z  (back)           max x  (outboard)  min y (top)

The two ear cubes span y -h .. 0 and grow along -y, so on THEM row 0 is the tip and the last row is
the root inside the skull - the antlers' inversion, on the one part here that shares it. Every other
cube spans downward in the ordinary way.

Blockbench's `west` is the geo +x face - the one pointing away from the body for a left-side part -
and `east` is the one against the chest. That is what lets one master serve both shoulders: after
the layer's scale(-1, 1, 1) the geo +x face of the mirrored copy still points outboard, so
lit-outboard / shadowed-inboard survives the mirror and the pair reads as a pair.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image

from fitting_mask import write_mask

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "beast_head.json"
OUT = ROOT / "tools" / "decoration_masters" / "beast_head.png"

TEX_W, TEX_H = 64, 32

# origin, size (w, h, d) and uv (u, v), mirroring beast_head.json in that file's own order, which is
# the order walk() visits: the root bone's two cubes, then the jaw, the two ears and the scruff.
# Origins are asserted as well as sizes because this part's whole argument - the 1.80 that clears a
# turned helmet's hat corner, the snout leading the shell by 2.20, the scruff's unit past the back
# wall - is made out of them.
CUBES = {
    "skull":   ((1.8, -6.2, -1.9), (4, 5, 5), (0, 0)),
    "muzzle":  ((2.8, -4.6, -5.2), (2, 2, 4), (18, 0)),
    "jaw":     ((-1, -0.7, -4.2), (2, 1, 4), (30, 0)),
    "ear_in":  ((-0.5, -3, -1), (1, 3, 2), (42, 0)),
    "ear_out": ((-0.5, -2, -0.9), (1, 2, 2), (48, 0)),
    "scruff":  ((-1.6, -0.8, -0.7), (3, 3, 2), (54, 0)),
}

random.seed(0x42484541)  # deterministic output - regenerating must not churn the PNG

# Calibrated against the ramp, not guessed, and pitched in the same register as pelt.py, mantle.py
# and antlers.py so the four Beast parts sit together on one figure.
FANG = 224      # a tooth, and the pale hairs along the bridge of the snout
CROWN = 176     # the top of the skull - the surface seen from the wearer's own camera
FLANK = 176     # the outboard cheek, the hero face
HIDE = 158      # fur turned any other way and still in the light
FACE = 146      # the front of the skull, around the eyes
NAPE = 118      # fur facing backward, in its own shadow
MUZZLE = 122    # the bridge of the snout - short hair over bone, darker than the cheek
PILE = 86       # deep pile: fur disappearing under the scruff or into the ear
NOSE = 70       # the nose pad and the gum line
INNER = 64      # buried: in the sleeve, in the skull, or under the scruff
MAW = 46        # inside the open mouth - the darkest value on the part
UNDER = 52      # a free underside

EYE = 190       # the eye texel, and the two brow texels it folds over
SOCKET = 44     # how far the face around an eye is dropped to frame it
FALL = 22       # top-to-bottom falloff down a standing face
DEPTH = 26      # front-to-back falloff across a flank
LIFT = 16       # outboard brightening across a face's width

# Hand-written, not generated, and read along a face's columns. Changing one of these numbers moves
# a clump, which is a design edit and not a tuning knob. Same amplitudes as the pelt's, because the
# two parts are hide on the same body.
CLUMP5 = (24, -34, 10, -20, 38)   # five columns: the skull's flank
CLUMP4 = (-28, 18, 32, -14)       # four: the skull's front, back, top and underside
CLUMP3 = (-22, 32, -8)            # three: the scruff
CLUMP2 = (18, -26)                # two: the snout, the jaw, an ear
HEM3 = (44, -34, 18)              # per-column tip / trough on a FREE hem row, three wide
FANGS4 = (0, 1, 0, 1)             # which columns of a four-wide bite carry a tooth
CLUMPS = {2: CLUMP2, 3: CLUMP3, 4: CLUMP4, 5: CLUMP5}

# The ears' feet on the skull's `up` face, measured rather than assumed: `up` is 4 columns of x
# (column i spans part x 1.8+i .. 2.8+i) by 5 rows of z back to front (row j spans 3.1-j .. 2.1-j),
# and the two ear cubes stand on (col, row) pairs.
EAR_FEET = {(2, 0), (1, 1), (2, 1), (1, 2)}


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


# ---- the cranium ---------------------------------------------------------------------------------


def paint_skull(img) -> None:
    """The cranium: 4 x 5 x 5, the mass of the part, 1.20 of its width inside the sleeve and 2.80
    outboard of it.

    Its `west` is the hero face - twenty-five texels, the largest unbroken area in the mod's Beast
    set, and nothing stands outboard of it at all - so it takes CLUMP5 across its depth and the
    fullest falloff. Its `north` carries the face: the eyes at row 1 over the snout, with the texels
    around them dropped by SOCKET so that two lit texels read as eyes rather than as two lit texels.
    Its `east` is against the sleeve below its top row and is INNER there; its `down` hangs over the
    outside of the shoulder from column 1 out, which is why only its inboard column is filler."""
    f = rects("skull")

    x0, y0, fw, fh = f["west"]           # 5 deep x 5 tall, col 0 = front, row 0 = top. All seen.
    for j in range(fh):
        for i in range(fw):
            lum = FLANK + CLUMP5[i] - round(DEPTH * 0.6 * ramp(i, fw)) - round(FALL * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["up"]             # 4 wide (x) x 5 deep, row 0 = BACK. The wearer's own view.
    for j in range(fh):
        for i in range(fw):
            if (i, j) in EAR_FEET:
                lum = INNER
            elif j == fh - 1 and i in (1, 2):
                lum = EYE - 20           # the brow, which the gemstone mask folds over
            else:
                lum = CROWN + CLUMP4[i] - round(DEPTH * 0.3 * (1.0 - ramp(j, fh))) \
                    - round(LIFT * (1.0 - ramp(i, fw)))
            put(img, x0 + i, y0 + j, lum + grain())

    # `north` is 4 wide x 5 tall, col 0 = INBOARD. Column 0 below the top row is inside the sleeve;
    # columns 1 and 2 over rows 2 and 3 are behind the snout. What is left is the face.
    x0, y0, fw, fh = f["north"]
    for j in range(fh):
        for i in range(fw):
            if (i == 0 and j >= 3) or (i in (1, 2) and j in (2, 3)):
                lum = INNER
            elif j == 0 and i in (0, fw - 1):
                lum = EYE
            else:
                lum = FACE + CLUMP4[i] // 2 + round(LIFT * ramp(i, fw))                     - round(FALL * 0.6 * ramp(j, fh))
                if (j == 0 and i in (1, 2)) or (j == 1 and i == fw - 1):
                    lum -= SOCKET        # the ring that makes two lit texels read as eyes
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["south"]          # 4 wide x 5 tall, col 0 = OUTBOARD; the scruff hangs on it
    for j in range(fh):
        for i in range(fw):
            lum = INNER if (i > 0 and j >= 3) else \
                NAPE + CLUMP4[i] + round(LIFT * (1.0 - ramp(i, fw))) - round(FALL * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + grain())

    # `east` is 5 deep x 5 tall, col 0 = BACK. Its top three rows are above the shoulder line at
    # part y = -3 and look across the 2.80-unit gap between this part and the wearer's own neck, so
    # they are painted rather than filled; the two below are inside the sleeve.
    x0, y0, fw, fh = f["east"]
    for j in range(fh):
        for i in range(fw):
            lum = INNER if j >= 3 else                 PILE + 22 + CLUMP5[i] // 2 - round(DEPTH * 0.3 * ramp(i, fw))                 - round(FALL * 0.5 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + grain())

    # `down` is 4 wide (x) x 5 deep, rows BACK to front. Column 0 is inside the sleeve and the back
    # row is under the scruff; the rest hangs over the outside of the shoulder and is seen from
    # below, which is the one angle a fur part is usually spared.
    x0, y0, fw, fh = f["down"]
    for j in range(fh):
        for i in range(fw):
            buried = i == 0 or (j == 0 and i < 3)
            lum = INNER if buried else UNDER + CLUMP4[i] // 3 + round(14 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + random.randint(-4, 4))


# ---- the snout and the jaw -----------------------------------------------------------------------


def paint_muzzle(img) -> None:
    """The snout: 2 x 2 x 4, half the cranium's width and jutting 3.30 units past the shoulder
    shell's front wall.

    Its `north` is the nose pad and is the darkest lit face on the part after the maw; its `up` is
    the bridge, short hair over bone and a step under the cheek, with the front row darker still
    where the pad wraps over. Its `down` is the roof of the mouth and is MAW with two fangs in it -
    those two texels and the jaw's four are the whole snarl."""
    f = rects("muzzle")

    x0, y0, fw, fh = f["up"]             # 2 wide (x) x 4 deep, row 0 = BACK, inside the skull
    for j in range(fh):
        for i in range(fw):
            if j == 0:
                lum = INNER
            elif j == fh - 1:
                lum = NOSE + 14 + CLUMP2[i] // 3
            else:
                lum = MUZZLE + CLUMP2[i] - round(10 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["north"]          # 2 x 2, col 0 = inboard. The nose pad, seen from anywhere.
    for j in range(fh):
        for i in range(fw):
            lum = (NOSE + 26 + CLUMP2[i] // 2) if j == 0 else (NOSE + CLUMP2[i] // 3)
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["west"]           # 4 deep x 2 tall, col 0 = front; col 3 is inside the skull
    for j in range(fh):
        for i in range(fw):
            lum = INNER if i == fw - 1 else \
                HIDE + CLUMP2[i % 2] - round(DEPTH * 0.5 * (1.0 - ramp(i, fw))) \
                - round(FALL * 0.4 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["east"]           # 4 deep x 2 tall, col 0 = BACK and inside the cranium.
    for j in range(fh):                  # The snout stands clear of the sleeve, so the rest is seen.
        for i in range(fw):
            lum = INNER if i == 0 else PILE + 18 + CLUMP2[i % 2] // 2 - round(FALL * 0.4 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + grain())

    # `down` is the roof of the mouth: 2 wide (x) x 4 deep, rows BACK to front. Rows 0 and 1 are
    # inside the skull and behind the jaw; rows 2 and 3 are the gape, and row 3 carries the two
    # upper fangs - on alternating columns, so the bite is not a comb.
    x0, y0, fw, fh = f["down"]
    for j in range(fh):
        for i in range(fw):
            if j < 2:
                lum = INNER
            elif j == fh - 1 and FANGS4[i % 4]:
                lum = FANG
            else:
                lum = MAW + round(12 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + random.randint(-4, 4))

    fill(img, f["south"], INNER)          # wholly inside the cranium


def paint_jaw(img) -> None:
    """The lower jaw: 2 x 1 x 4 on a bone rotated 18 degrees about X, so its forward end drops and
    its hinge does not. The gape it opens runs 0.34 at the back of the mouth to 1.63 at the front.

    Its `up` face is the tongue side and takes the maw and the two lower fangs; its `down` is the
    underside of the chin, which is what a viewer standing in front of the wearer actually sees of
    it, so that face is fur and not filler."""
    f = rects("jaw")

    x0, y0, fw, fh = f["up"]             # 2 wide (x) x 4 deep, row 0 = BACK
    for j in range(fh):
        for i in range(fw):
            if j == 0:
                lum = INNER              # the hinge, inside the snout
            elif j == fh - 1 and not FANGS4[i % 4]:
                lum = FANG - 12          # the lower bite, offset from the upper one
            else:
                lum = MAW + 10 + round(10 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + random.randint(-4, 4))

    x0, y0, fw, fh = f["north"]          # 2 x 1, col 0 = inboard. The chin.
    for i in range(fw):
        put(img, x0 + i, y0, NOSE + 34 + CLUMP2[i] // 2 + grain())

    x0, y0, fw, fh = f["west"]           # 4 deep x 1 tall, col 0 = front; col 3 is inside the skull
    for i in range(fw):
        lum = INNER if i == fw - 1 else HIDE - 12 + CLUMP2[i % 2] - round(DEPTH * 0.4 * ramp(i, fw))
        put(img, x0 + i, y0, lum + grain())

    x0, y0, fw, fh = f["east"]           # 4 deep x 1 tall, col 0 = BACK; cols 0-1 buried
    for i in range(fw):
        lum = INNER if i < 2 else PILE + 12 + CLUMP2[i % 2] // 2
        put(img, x0 + i, y0, lum + grain())

    x0, y0, fw, fh = f["down"]           # 2 wide (x) x 4 deep, rows BACK to front. The chin's sole.
    for j in range(fh):
        for i in range(fw):
            lum = INNER if j == 0 else UNDER + 12 + CLUMP2[i] // 3 + round(16 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + random.randint(-4, 4))

    fill(img, f["south"], INNER)          # wholly inside the cranium


# ---- the ears and the scruff ---------------------------------------------------------------------


def paint_ear(img, name: str) -> None:
    """One ear. These two cubes span y -h .. 0 and grow along -y, so row 0 is the TIP and the last
    row is the root inside the cranium - the antlers' inversion, on the one part here that shares it.

    The value FALLS toward the tip, which is the opposite of an antler and the same as a wolf: a
    dark-tipped ear is the marking the animal actually has, and it is what keeps a three-unit ear
    and a two-unit ear from reading as two matched prongs.

    The last row is the socket row and takes the cranium's contact shadow rather than INNER. That
    was measured, not assumed: only 0.6 of each ear's bottom row is actually inside the skull -
    a two-row ear buried to the waist is a one-texel ear, and it read as a dark notch beside a lit
    one. SOCKET here is the same shadow the antlers put where a tine leaves its beam."""
    f = rects(name)
    _, (w, h, d), _ = CUBES[name]

    for face, base, cols in (("west", HIDE + 10, d), ("east", PILE + 16, d),
                             ("north", FACE - 18, w), ("south", NAPE - 6, w)):
        x0, y0, fw, fh = f[face]
        clump = CLUMPS.get(fw, (0,) * fw)
        for j in range(fh):
            for i in range(fw):
                if j == fh - 1:
                    lum = base - SOCKET + clump[i] // 3
                else:
                    lum = base + clump[i] - round(28 * (1.0 - ramp(j, fh)))
                put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["up"]             # the tip cap: w wide (x) x d deep, row 0 = back
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j, PILE + 26 - round(14 * ramp(j, fh)) + grain())

    fill(img, f["down"], INNER)          # the root, inside the cranium


def paint_scruff(img) -> None:
    """The ruff of hide at the nape: 3 x 3 x 2 on a bone rotated -14 degrees about Z, so it hangs
    outboard the way the mantle's four locks do - the same sign, and for the same reason, since a
    negative Z rotation carries a hanging cube's lower end toward +x, which is outboard on both
    shoulders after the mirror.

    It exists for three things. It closes the seam where the head meets the shoulder; it puts a unit
    of the part behind the shell's back wall at z = 4.00, so the silhouette is broken from behind as
    well as from the front; and it gives this part the one FREE HEM it has, which is where HEM3
    goes. Its `south` is the only face of the part a camera behind the wearer reaches, so that face
    is painted as a real flank and not as backing."""
    f = rects("scruff")

    x0, y0, fw, fh = f["south"]          # 3 wide x 3 tall, col 0 = OUTBOARD, row 0 = top. All seen.
    for j in range(fh):
        for i in range(fw):
            lum = NAPE + 14 + CLUMP3[i] + round(LIFT * (1.0 - ramp(i, fw))) \
                - round(FALL * 0.5 * ramp(j, fh))
            if j == fh - 1:
                lum += HEM3[i] - FALL    # the free hem, broken column by column
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["west"]           # 2 deep x 3 tall, col 0 = FRONT; the front column is in
    for j in range(fh):                  # the skull for its top two rows
        for i in range(fw):
            buried = i == 0 and j < 2
            lum = INNER if buried else HIDE + CLUMP2[i] - round(FALL * 0.5 * ramp(j, fh))
            if j == fh - 1 and not buried:
                lum += HEM3[i] // 2
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["east"]           # 2 deep x 3 tall, col 0 = BACK; col 1 is skull and sleeve
    for j in range(fh):
        for i in range(fw):
            lum = INNER if i == 1 else PILE + CLUMP2[i] // 2 - round(FALL * 0.4 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + grain())

    # `north` looks into the back of the cranium over its top two rows and its inboard column is in
    # the sleeve; only the bottom row of its two outboard columns is ever seen, hanging free below
    # the skull's own underside.
    x0, y0, fw, fh = f["north"]
    for j in range(fh):
        for i in range(fw):
            free = j == fh - 1 and i > 0
            lum = (PILE - 8 + CLUMP3[i] // 2) if free else INNER
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["up"]             # 3 wide (x) x 2 deep, row 0 = BACK; row 1 is in the skull
    for j in range(fh):
        for i in range(fw):
            lum = INNER if j == 1 else NAPE - 16 + CLUMP3[i] // 2
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["down"]           # 3 wide (x) x 2 deep. The hem's sole, free everywhere.
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j,
                UNDER + CLUMP3[i] // 3 + round(14 * ramp(j, fh)) + random.randint(-4, 4))


# ---- checks -------------------------------------------------------------------------------------


def eye_rects() -> list[tuple[int, int, int, int]]:
    """The four texels the gemstone fitting covers, derived from the skull's own net rather than
    written down: the two eyes at the outer columns of `north` row 0, and the two brow texels
    directly above them on the front row of `up`. Deriving them means a change to the skull's uv
    cannot leave the mask pointing at the cheek.

    The outer columns and the TOP row, not the middle pair a unit lower, and both of those were
    tried first. Two adjacent lit texels are one lit bar, not two eyes; and column 0 below the top
    row is inside the sleeve, so the only place a symmetric pair fits with face between them is the
    row above the snout's own top."""
    nx, ny, _, _ = rects("skull")["north"]
    ux, uy, _, ud = rects("skull")["up"]
    return [(nx, ny, 1, 1), (nx + 3, ny, 1, 1),
            (ux, uy + ud - 1, 1, 1), (ux + 3, uy + ud - 1, 1, 1)]


def check_geometry() -> None:
    """CUBES must be the cube list of the shipped geometry, in order, down to the origins. Painting
    a texture for a shape the model no longer has is invisible to every other check in this
    pipeline: both halves stay internally consistent while the rectangles slide off the faces they
    were drawn for. The origins are asserted as well as the sizes because this part's argument -
    the 1.80 that clears a turned helmet's hat corner, the snout leading the shell, which columns of
    the skull are inside the sleeve - is made entirely out of them."""
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

    # Four cubes hang off rotated bones and the pivots are what put them where the prose says they
    # are - the gape, the ears' 30 degrees of splay, the scruff's outboard hang. A bone silently
    # moved would leave every number in the docstring false and nothing else here would notice.
    bones = {}

    def walk_bones(bone):
        bones[bone["name"]] = (tuple(bone.get("pivot", [0, 0, 0])),
                               tuple(bone.get("rotation", [0, 0, 0])))
        for child in bone.get("children", []):
            walk_bones(child)

    for bone in doc["bones"]:
        walk_bones(bone)
    assert bones == {
        "head": ((0, 0, 0), (0, 0, 0)),
        "jaw": ((3.8, -2.4, -1), (28, 0, 3)),
        "ear_in": ((3.1, -5.9, 0.6), (-10, 0, -14)),
        "ear_out": ((4.65, -5.9, 1.4), (-18, 0, 16)),
        "scruff": ((3.55, -2.3, 2.7), (0, 0, -14)),
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
    paint_skull(img)
    paint_muzzle(img)
    paint_jaw(img)
    paint_ear(img, "ear_in")
    paint_ear(img, "ear_out")
    paint_scruff(img)

    # This master is 100% opaque - the mouth is a gap between cubes and the hem is a hem - so the
    # painted set must be exactly the net: a texel short is a face the model shows and the texture
    # does not, and a texel over is paint the model never samples.
    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque == set(claimed), "painted pixels do not match the UV rectangles"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)})")

    # The eyes, and the brow they fold over. Four texels; see the module docstring for the size.
    write_mask(img, eye_rects(), OUT.with_name("beast_head_gemstone.png"))


if __name__ == "__main__":
    main()
