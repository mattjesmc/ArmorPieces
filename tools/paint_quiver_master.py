"""
Paint the grayscale master, the static leather layer and the guard mask for the "quiver" part.

Kept as a script rather than a checked-in binary so the shape stays editable and reviewable. Like
the buckled_belt and puttees painters this one does not merely claim that CUBES matches the shipped
geometry, it reads assets/armorpieces/armorpieces/decoration/quiver.json at run time and asserts it
(check_geometry) - the origins AND the two bone frames, because on this part the frames ARE the
design: a cube cannot rotate, so the whole diagonal lives in the `sling` bone's [6, 0, -36] and the
arrow bundle's extra -6 about z. A master painted for an untilted stack would stay perfectly
self-consistent while describing a different object. Output goes to
tools/decoration_masters/quiver.png, quiver_static.png and quiver_guard.png, which
sync_decoration_masters.py installs.

Master convention: luminance carries shading, alpha carries silhouette. This master is 100% opaque.
A quiver is a solid vessel, it has no fringe, and parts draw with armorCutoutNoCull, so a hole cut
in the leather would show the inside of the leather rather than the back plate behind it. The
mouth's opening, the buckle's slot and the groove between the two arrows are therefore VALUE, not
alpha.

WHAT THIS PART IS, AND WHY IT IS SHAPED LIKE THIS

`back` is the best-served socket in the mod - Banner, Pinions, Wing Roots - and all three of them
are FLAT THINGS ON THE SPINE: a hanging cloth, two vanes off a bracket, a plate with two sockets.
Each is symmetric about x = 0, each lies parallel to the back plate, and none of them is an object
you could pick up and put down. This one is. It is a vessel, it is asymmetric, it is diagonal, and
the two numbers that matter most are that it stands 0.22 off the chestplate where it is bolted on
and 3.56 off it at its deepest - it leans away from the back as it descends. None of the three
shipped parts does that, and it is the most reliable way to read as something slung ON a person
rather than built INTO them.

The diagonal is a bone, because cubes cannot rotate. `sling` carries [6, 0, -36]: -36 about z is the
slant across the back, and +6 about x is the lean. Composed the way ModelPart.rotate composes them -
Rz * Ry * Rx, so a vector meets X first - the sling's three axes come out in the body's frame as

    local +x  ->  ( 0.809, -0.588,  0.000)   across the tube, up and to the wearer's LEFT
    local +y  ->  ( 0.585,  0.805,  0.105)   down the tube, to the left hip and away from the back
    local +z  ->  (-0.061, -0.085,  0.995)   out of the back

so every unit travelled down the tube also travels 0.105 away from the body. Over the 12.19 units of
tube-axis this part spans that is 1.27 units of standoff bought for nothing, and it is what lets the
lower half of the quiver pass the belt line in DEPTH rather than in height. Rotating about z alone
would have left the whole thing parallel to the back plate and a fifth of a unit off it everywhere,
which is the Wing Roots' silhouette with a different outline.

THE CUBES, IN SLING-LOCAL UNITS AND IN THE BODY'S

`back` is a SINGLE, non-mirrored attachment - Attachment.of(BODY, 0, 2, 2) - so the layer's
scale(-1, 1, 1) never runs, one master serves one draw, and `west` and `east` are genuinely
different faces rather than the same face twice. That is what earns the asymmetry: the mouth is over
the wearer's RIGHT shoulder blade (body x negative) and the base swings out to the LEFT hip, the way
an archer wears one. The Sash's knot is the precedent for a Wayfarer part that picks a side.

Part-local (0, 0, 0) is body (0, 2, 2). +Y is DOWN. `sling` pivots at part (0.5, 4.55, 2.25), which
is body (0.5, 6.55, 4.25); `arrows` pivots at sling-local (0, -3.3, 1).

    cube      sling-local origin   size              body-frame hull
    tube      (-1.4, -2.9,  0   )  (2.8, 6.7, 2   )  x -2.45..3.85   y  3.22..10.43  z 3.95..6.64
    mouth     (-1.6, -3.7,  0.1 )  (3.2, 1  , 2.1 )  x -3.09..0.21   y  2.45.. 5.31  z 3.96..6.16
    base      (-1.2,  3.6,  0.2 )  (2.4, 1.4, 1.6 )  x  1.52..4.38   y  8.59..11.26  z 4.83..6.56
    band_hi   (-1.5, -2.7, -0.75)  (3  , 2  , 2.85)  x -2.42..1.35   y  3.32.. 6.93  z 3.22..6.27
    band_lo   (-1.5,  2.1,  0   )  (3  , 1  , 2.1 )  x  0.39..3.53   y  7.18.. 9.93  z 4.47..6.66
    fletch    (-1.1, -3.8, -0.6 )  (2.2, 3.8, 1.2 )  x -4.88..-0.64  y  0.22.. 4.60  z 3.90..5.51

Six cubes: a leather tube with a flared mouth and a tapered base, two steel bands round it, and the
ends of two arrows standing out of the mouth. Read down the diagonal that is
arrows / mouth / band_hi / bare leather / band_lo / base. The bare leather between the bands is 2.8
units long and there is another 0.7 below band_lo, which is 3.5 of the tube's 6.7 - and it is the
whole reason the bands sit where they do rather than at the thirds. A band at each third would have
left three equal panels and read as a barrel; a wide bracket at the top and one thin strap low down
reads as a thing that is held near its mouth and hangs from there, which is what it is.

WHAT CLEARS WHAT

Three surfaces are in play on `body`, and this part is authored against all three:

  * naked body box       x +/-4.0   z +/-2.0
  * leggings shell 0.5   x +/-4.5   z +/-2.5
  * chestplate shell 1.0 x +/-5.0   z +/-3.0   <- the piece this socket belongs to, always worn

Nothing here is buried. The lowest point of the whole part above the chestplate is band_hi's
mounting face at body z = 3.22 - a fifth of a unit of air, the same tenth-and-a-bit the buckled belt
spends clearing the leggings and the greaves spend clearing the boots. Landing it ON z = 3 would
have put a face of the decoration in the plane of a shell that is always worn with it, and the
decoration layer draws AFTER the armor layer, so at equal depth the later draw wins and the bracket
would flicker its own dark INNER texels onto the back plate.

band_hi is the mount and is the only cube that reaches the plate. It is 2.85 deep where every other
cube here is about two, because it has two jobs: it wraps the tube (sling-local z -0.75..2.1, over
the tube's 0..2) and it runs back to sling-local z = -0.75, which is the plate. Everything below it
hangs, which is why the part gets steadily further from the back as it descends and why the base
ends up 3.56 units off the chestplate. That is how a slung quiver actually sits and it is also what
buys the belt clearance below.

Sideways the part reaches body x -4.88 at the arrow tips and 4.38 at the base, so it stays inside
the chestplate's +/-5 with a tenth to spare at each end while overhanging the naked torso's +/-4 at
both. The arrows overhanging the shoulder is wanted - it is what puts the part in the silhouette
from the front, where a back decoration is otherwise invisible - and the right arm's own 1.0 shell,
which occupies world x -9..-3 at z -3..3, is cleared in depth: the arrows are at z 3.90 and up.

THE BELT LINE, MEASURED

The brief for this batch names it: `wing_roots` hangs to body y 9.5 over z 2..5, and both the
shipped Sash and the Buckled Belt pass through it. This part goes lower still - the base bottoms out
at body y 11.26 - so it shares the waist with both of them and the numbers have to be exact.

  * the Sash's back band is body x +/-5.5, y 8..11, z 1..4.
  * the Buckled Belt's back bar is body x +/-5.5, y 9..11, z 2.6..3.5.

trace_geometry reports one OVERLAP, `sling` into the Sash's band by 6.30 x 2.43 x 0.05, and says of
itself that it is a hull test. It is a hull artefact: the tube is a rotated cube, its axis-aligned
hull is much larger than the cube, and an exact separating-axis test over the two real boxes gives a
clear gap of 0.329 for the tube and 0.470 for band_lo. One line of arithmetic is why. The tube's
near face is the plane sling-local z = 0, whose body z is 4.25 + 0.1045 * ly; its lowest edge is the
one at local x = -1.4, whose body y is 7.373 + 0.8046 * ly. The tube therefore first touches y = 8
at ly = 0.779, and by then its near face has climbed to z = 4.331 - past the Sash's z = 4 back wall.
Where the tube IS shallower than z = 4 (ly < -2.392) its lowest point is body y 5.45, two and a half
units clear above the Sash. So the quiver passes the belt behind it, the way a quiver passes a belt,
and the six degrees of x rotation are what pay for that.

THE HEAD, WHICH IS THE OTHER LIMIT

The arrow tips stop at body y 0.22 and that is not a stylistic choice. The head is a separate bone
that yaws freely under the player's own aim while the body does not follow: its box is y -8..0, so
at 0.22 this part never touches the bare head at any yaw, which is the case that must hold because
the head is always there. A helmet's 1.0 shell is y -9..1, so the top 0.78 of the bundle is inside
the helmet's y band - but the helmet is z -3..3 and the bundle is z 3.90 and up, so at rest they
are 0.9 apart, and only a helmet turned near 45 degrees, whose corner swings back to z 7.07, can
reach it. The shipped Pinions' bracket tops out at body y 1.0 and accepts exactly that trade. The
cost here is real and is worth naming: it is why the tube is 6.7 long and hangs to the hip rather
than being centred on the shoulder blades, and why the arrows had to be given their own bone.

THE ARROWS

`arrows` is a child of `sling` with its own -6 about z, pivoted at the mouth. Six degrees is small
and that is the point: shafts on the SAME axis as the tube read as the tube continuing, and shafts
on a slightly different one read as loose objects standing in it. It also throws the bundle 0.4
further outboard at the tip, which is what puts the top of the part over the shoulder blade instead
of straight up the spine.

The bundle is one cube, 2.2 x 3.8 x 1.2, and its foot is its own bone's pivot at sling-local
ly = -3.3, which is 0.4 below the mouth's top rim and 0.6 above its bottom - standing inside the
flare, not balanced on it. TWO arrows, not three: 2.2 units nets to three texel columns and a rod
needs a lit column with a dark one beside it, so the only honest reading of three columns is
lit / groove / lit. Five columns would have bought a third arrow and there is nowhere to put them,
because the bundle has to stand inside a mouth that is 3.2 wide. The groove runs the whole length of
the bundle rather than stopping under the fletching, which was the first cut and read as a single
grey wedge with a notch in it: 74 against 226 down every row is what makes two rods.

THE THREE SHEETS, AND WHAT SHOWS WHICH MATERIAL

  * the MASTER shades everything. Its leather values are deliberately held in 61..204 rather than
    run out to 250: leather pixels are read through the LEATHER static ramp, whose mid stop is at
    master 127 and whose light stop is only halfway to white, so a face painted at 240 would read as
    tan canvas rather than as leather. That is the same window the buckled belt uses and it is the
    single most visible thing the two parts have in common. The steel of the two bands runs 29..241
    and the arrows 43..244, because both go through a trim material's own ramp and want the whole of
    it.
  * the STATIC layer is opaque LEATHER over every pixel of tube, mouth and base, and transparent
    everywhere else. #a06540 is vanilla's own undyed-leather-armour tint - the colour a player reads
    as leather without being told, and the colour the buckled belt uses.
  * the GUARD mask is band_hi and band_lo, six face rectangles each, copied out of the master by
    fitting_mask.write_mask - same shading, second material.

So with nothing in the fitting the part already shows two materials at once, leather against the
base trim, and three when the guard is filled. The arrows are the piece that stays on the BASE
material in every case, and that is deliberate: a quiver is a container and what it holds is the
point, so a gold quiver has gold arrow ends standing in it and an iron one iron. It is the same
bargain the buckled belt strikes - always leather, always some of the base material - taken round
the other way, because there the base material lives in the hardware and here it lives in the
contents.

FACE LAYOUT AND ORIENTATION

The face rectangles come from paint_circlet_master.faces(): row one (v .. v+d) holds up then down,
each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west, south with widths
d, w, d, w. The two thin d-wide faces come FIRST and THIRD. Sizes here are fractional, so the net
rounds UP the way Blockbench does - the tube's 6.7 of length nets to seven rows and the seventh is
sampled over only its first seven tenths.

Orientation inside each rectangle is the table the greaves and puttees painters record as measured,
not recalled:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x              max z
    down            +y  (underside)      min x              max z
    west            +x                   min z              min y
    east            -x                   max z              min y
    north           -z  (front)          min x              min y
    south           +z  (back)           max x              min y

Read that through the sling's basis above and the six faces of a cube on this part mean:

    south   the face pointing away from the wearer's back - the HERO, and the only face a camera
            behind a standing player meets square on
    north   the face turned back toward the plate, across between 0.95 and 3.5 units of air. NOT
            buried, so it is painted as a shadowed face rather than as INNER
    west    the flank on the upper side of the diagonal, toward the wearer's left and the light
    east    the flank on the lower side, turned away from it
    up      toward the mouth, i.e. up the tube
    down    toward the base

Vanilla gives +x and -x the same 0.6 diffuse term, exactly as it gives +z and -z the same 0.8, so
`west` and `east` would be lit identically if this file did not separate them - and the roundness of
the tube is nothing but that separation, 184 against 116.

Which faces of which cube are covered by another cube of this part is what the row values are built
on, and it is all in ly:

    the mouth covers the tube over ly -2.9..-2.7    (and the tube's `up` is wholly inside it)
    band_hi  covers the tube over ly -2.7..-0.7     (south rows 0 and 1 whole, row 2's first fifth)
    band_lo  covers the tube over ly  2.1.. 3.1     (south row 5 whole)
    the base sits inside the tube in x and z, so it covers the tube's `down` and nothing else
    the fletch sits inside the mouth in x and z, so it covers the mouth's `up` and nothing else
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
       / "decoration" / "quiver.json")
OUT = ROOT / "tools" / "decoration_masters" / "quiver.png"
OUT_STATIC = OUT.with_name("quiver_static.png")
OUT_GUARD = OUT.with_name("quiver_guard.png")

TEX_W, TEX_H = 64, 32

# origin, size (w, h, d) and uv (u, v), mirroring quiver.json in that file's own walk order - the
# root bone `rig` carries no cubes, so the order is `sling`'s five and then `arrows`' one. The
# origins are asserted with the sizes because every clearance in the docstring is a statement about
# them: -0.75 is band_hi's reach back to the plate, 2.5 is how far the base sinks into the tube, and
# a size table alone would let all of it drift while staying self-consistent.
CUBES = {
    "tube":    ((-1.4, -2.9, 0),      (2.8, 6.7, 2),    (0, 0)),
    "mouth":   ((-1.6, -3.7, 0.1),    (3.2, 1, 2.1),    (10, 0)),
    "base":    ((-1.2, 3.6, 0.2),     (2.4, 1.4, 1.6),  (10, 5)),
    "band_hi": ((-1.5, -2.7, -0.75),  (3, 2, 2.85),     (34, 0)),
    "band_lo": ((-1.5, 2.1, 0),       (3, 1, 2.1),      (46, 0)),
    "fletch":  ((-1.1, -3.8, -0.6),   (2.2, 3.8, 1.2),  (24, 0)),
}

# The bone each cube hangs from: (pivot, rotation). On this part the rotations are the design, so
# they are asserted rather than trusted - a lost tilt would turn a slung vessel back into a box
# bolted to the spine without moving one texel of this file.
FRAMES = {
    "tube":    ((0.5, 4.55, 2.25), (6, 0, -36)),
    "mouth":   ((0.5, 4.55, 2.25), (6, 0, -36)),
    "base":    ((0.5, 4.55, 2.25), (6, 0, -36)),
    "band_hi": ((0.5, 4.55, 2.25), (6, 0, -36)),
    "band_lo": ((0.5, 4.55, 2.25), (6, 0, -36)),
    "fletch":  ((0, -3.3, 1), (0, 0, -6)),
}

LEATHER_CUBES = ("tube", "mouth", "base")
GUARD_CUBES = ("band_hi", "band_lo")

random.seed(41)  # deterministic output - regenerating must not churn the PNG

# ---- leather ------------------------------------------------------------------------------------
# Read through LEATHER's static ramp, whose mid stop is master 127 and whose light stop is only
# halfway to white. These stay inside 66..200 on purpose; see the docstring.
L_TOP = 200      # the mouth's rim seen from above - the one leather surface the light hits square
L_LIT = 184      # the flank on the upper side of the diagonal
L_FACE = 158     # the hero face of the tube, centre column
L_DIM = 116      # the flank on the lower side
L_BACK = 82      # a leather face turned back toward the plate, across open air
L_UNDER = 90     # the base's underside
L_INNER = 66     # buried leather: inside the mouth, under a band, behind the base

# ---- steel --------------------------------------------------------------------------------------
# Read through a trim material's own ramp, so these run the full width of it.
M_LIT = 240      # the top bar of the buckle plate
M_FACE = 202     # a band in the light
M_DIM = 140      # a band turned away
M_APERTURE = 30  # the slot the sling strap threads through
M_INNER = 32     # the band's mounting face and the parts of it inside the tube

# ---- arrows -------------------------------------------------------------------------------------
A_NOCK = 228     # the fletched end of a shaft - mottled, and the brightest thing on the part
A_LIT = 226      # the outboard shaft
A_SHAFT = 204    # the inboard shaft
A_GROOVE = 74    # the gap BETWEEN the two shafts, at every row - the whole read is this step
A_SHADE = 96     # the bundle turned back toward the plate
A_INNER = 46     # inside the mouth

# Two shafts, not three: 2.2 units of bundle nets to three texel columns and a rod needs a lit
# column with a dark one beside it, so the honest reading of three columns is lit / groove / lit.
# Five columns would have bought a third arrow and there is nowhere to put them - the mouth is 3.2
# wide and the bundle has to stand inside it.
SHAFTS = (A_SHAFT, A_GROOVE, A_LIT)
GROOVE_COLUMN = 1  # the middle column, which is the gap and never a rod
FLETCHED_ROWS = 1  # of the four rows of the bundle, only the top one is feather

RIM = 16         # the chamfer along a top edge
FALL = 22        # the falloff down a standing face
GRAIN = 4        # leather grain jitter
JITTER = 3


def net(size):
    """A cube's box-UV net in whole pixels. Rounds UP the way Blockbench does - the tube's 6.7 of
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


# The lateral profile across the tube's three hero columns, from the upper edge of the diagonal to
# the lower. A MULTIPLIER rather than an offset, so a shadowed row keeps its shape instead of being
# flattened into INNER by a subtraction sized for the lit ones - a cylinder's shading is
# proportional. Column 0 is `south`'s max x, which the sling's basis puts on the upper side.
TUBE_PROFILE = (1.00, 0.93, 0.79)

# What each of the tube's six hero rows is worth, and why. Row j covers sling-local ly -2.9 + j
# .. -1.9 + j, and the two bands and the mouth cover the ly ranges listed in the docstring.
TUBE_ROWS = (
    0.44,   # 0  wholly covered - the mouth over its first fifth, band_hi over the other four
    0.42,   # 1  wholly under band_hi
    0.94,   # 2  the top of the bare panel - band_hi laps only its first fifth
    1.00,   # 3  the middle of the bare panel, the brightest leather on the part
    0.97,   # 4  bare panel, one step down the length of the vessel
    0.46,   # 5  wholly under band_lo
    0.88,   # 6  the last 0.7 of the tube, between band_lo and the base
)

# The stitched seam runs down the tube's lower edge - column 2 of the hero face - as an alternating
# value rather than a modelled step, because a step parallel to the face behind it is lit
# identically to it and buys nothing (the greaves painter records the same finding against a rib).
SEAM = 14


def paint_tube(img) -> None:
    """The body of the quiver: 2.8 x 6.7 x 2, leather, on the sling bone.

    `south` is the hero and the only face here a camera behind a standing player meets square on.
    Three columns and seven rows, of which rows 2, 3, 4 and 6 are the
    only bare leather on the whole part. Everything above it is under band_hi and the mouth and
    everything below it under band_lo, so those rows are painted as the shadow they are: dark
    enough that if the anchor is ever nudged what appears is leather in shade rather than a black
    stripe, and no brighter, because there is nothing to be gained from paint nobody can see.

    `west` is the flank on the upper side of the diagonal and `east` the flank on the lower, which
    is a fact about the sling's basis rather than about the cube: local +x comes out at
    (0.809, -0.588, 0), so it points up and to the wearer's left. Vanilla gives +x and -x the same
    0.6 diffuse term, so the two flanks would be lit identically if this file did not separate them,
    and the whole roundness of the tube is that separation - 184 against 116.

    Each flank is two texels deep: column 0 is min z, the side nearer the back plate, and column 1
    the side away from it. Both are free - nothing on this part or on the body is beside the tube -
    so both are painted, with the near column dropped because it looks into the gap between the
    quiver and the plate.

    `north` looks back at the plate across between 0.85 and 1.6 units of air. It is NOT buried and
    is painted as a shadowed face rather than as INNER: at a low three-quarter angle from behind and
    below, with the wearer's arms raised, it is visible.

    `up` is wholly inside the mouth. `down` is covered by the base but for a rim - the base is 2.4
    by 1.6 inside the tube's 2.8 by 2 - so it gets the rim and nothing else."""
    f = face_rects("tube")

    x0, y0, fw, fh = f["south"]          # 3 wide x 6 tall, col 0 = upper edge, row 0 = the mouth end
    for j in range(fh):
        for i in range(fw):
            lum = max(L_INNER, round(L_FACE * TUBE_ROWS[j] * TUBE_PROFILE[i]))
            if i == fw - 1 and j % 2 == 0:
                lum -= SEAM             # the stitched seam down the lower edge
            put(img, x0 + i, y0 + j, max(L_INNER - 4, lum) + random.randint(-GRAIN, GRAIN))

    for name, base in (("west", L_LIT), ("east", L_DIM)):
        x0, y0, fw, fh = f[name]         # 2 deep x 6 tall, row 0 = the mouth end
        for j in range(fh):
            for i in range(fw):
                near = (i == 0) if name == "west" else (i == fw - 1)
                lum = base - round(FALL * ramp(j, fh)) - (26 if near else 0)
                if j == 0:
                    lum += RIM
                put(img, x0 + i, y0 + j, lum + random.randint(-GRAIN, GRAIN))

    x0, y0, fw, fh = f["north"]          # 3 wide x 6 tall, looking back at the plate
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j,
                L_BACK - round(10 * ramp(j, fh)) + random.randint(-GRAIN, GRAIN))

    fill(img, f["up"], L_INNER)          # inside the mouth

    x0, y0, fw, fh = f["down"]           # 3 wide x 2 deep; the base covers all but a rim
    for j in range(fh):
        for i in range(fw):
            edge = i in (0, fw - 1) or j == 0
            put(img, x0 + i, y0 + j, (L_UNDER - 12 if edge else L_INNER)
                + random.randint(-JITTER, JITTER))


def paint_mouth(img) -> None:
    """The flared rim the arrows stand in: 3.2 x 1 x 2.1, leather, 0.2 proud of the tube in x and z.

    Its `up` face is the one place on this part where a hole is drawn, and it is drawn in value
    because a hole cut in alpha would show the inside of the leather rather than anything behind it.
    Four columns by three rows over 3.2 by 2.1 units: the arrow bundle stands inside 2.2 by 1.4 of
    that, which lands on the middle two columns and the lower two rows, so the rim survives as an
    L of bright leather with a 2 x 2 dark opening inside it. Row 0 is max z, the far lip, and it is
    whole - the bundle only reaches into its first fifth - which is why the opening reads as a mouth
    tipped toward the viewer rather than as a square hole.

    `south` is one texel row of rim seen from behind and `west`/`east` are the rim in profile. All
    three are the brightest leather on the part after `up`, because a rim is the edge that catches
    everything. `north` faces the plate. `down` sits on the tube: the mouth is 0.2 wider in x on
    each side and 0.1 deeper at the far side, so it overhangs by exactly that and the overhang is
    the one lit texel of it."""
    f = face_rects("mouth")

    x0, y0, fw, fh = f["up"]             # 4 wide x 3 deep, col 0 = min x, row 0 = max z
    for j in range(fh):
        for i in range(fw):
            rim = j == 0 or i in (0, fw - 1)
            lum = (L_TOP - round(18 * ramp(j, fh))) if rim else L_INNER - 4
            put(img, x0 + i, y0 + j, lum + random.randint(-GRAIN, GRAIN))

    x0, y0, fw, fh = f["south"]          # 4 wide x 1 tall
    for i in range(fw):
        put(img, x0 + i, y0, L_FACE + 22 - round(14 * ramp(i, fw))
            + random.randint(-GRAIN, GRAIN))

    for name, base in (("west", L_LIT + 8), ("east", L_DIM + 10)):
        x0, y0, fw, fh = f[name]         # 3 deep x 1 tall
        for i in range(fw):
            put(img, x0 + i, y0, base - round(12 * ramp(i, fw))
                + random.randint(-GRAIN, GRAIN))

    fill(img, f["north"], L_BACK + 6)    # toward the plate

    x0, y0, fw, fh = f["down"]           # 4 wide x 3 deep; only the overhang is not on the tube
    for j in range(fh):
        for i in range(fw):
            edge = i in (0, fw - 1) or j == 0
            put(img, x0 + i, y0 + j, (L_UNDER if edge else L_INNER)
                + random.randint(-JITTER, JITTER))


def paint_base(img) -> None:
    """The tapered foot: 2.4 x 1.4 x 1.6, leather, sunk 0.2 into the tube and inside it in x and z.

    It is the lowest thing on the part - body y 10.36 - and the only one a player sees from below,
    so `down` is painted as a real cap rather than as INNER, dark because it faces away from the
    light and with a lighter border where the two side seams of a stitched leather bottom would run.

    `south`, `west` and `east` are the taper. All three are dropped under the tube's own values:
    the foot of a hanging vessel is in its own shadow, and the step in value is what says the base
    is a separate, narrower piece rather than the tube continuing - because it is narrower by only
    0.4 on the side and 0.2 in depth, which at this scale no silhouette would show.

    `up` is inside the tube."""
    f = face_rects("base")

    x0, y0, fw, fh = f["south"]          # 3 wide x 2 tall
    for j in range(fh):
        for i in range(fw):
            lum = round((L_FACE - 26 - round(FALL * ramp(j, fh))) * TUBE_PROFILE[i])
            put(img, x0 + i, y0 + j, lum + random.randint(-GRAIN, GRAIN))

    for name, base in (("west", L_LIT - 28), ("east", L_DIM - 16)):
        x0, y0, fw, fh = f[name]         # 2 deep x 2 tall
        for j in range(fh):
            for i in range(fw):
                put(img, x0 + i, y0 + j, base - round(FALL * ramp(j, fh))
                    + random.randint(-GRAIN, GRAIN))

    fill(img, f["north"], L_BACK - 8)    # toward the plate

    x0, y0, fw, fh = f["down"]           # 3 wide x 2 deep - the cap, seen from below
    for j in range(fh):
        for i in range(fw):
            seam = i in (0, fw - 1)
            put(img, x0 + i, y0 + j, (L_UNDER if seam else L_UNDER - 20)
                + random.randint(-JITTER, JITTER))

    fill(img, f["up"], L_INNER)          # inside the tube


def paint_band(img, name: str, plate: bool) -> None:
    """One steel band round the tube. band_hi is also the mount and is 2.85 deep for it; band_lo is
    2.1 and only wraps.

    `south` is the band's outer face and on band_hi it carries the BUCKLE, which is paint and not a
    cube. Three columns by two rows is exactly the budget the buckled belt's frame needed and it is
    spent the same way: a bright bar with a dark slot cut in it over a duller plate, 240 against 30,
    and at this size that contrast IS the buckle. There is no tongue, because four columns is the
    minimum for frame-slot-tongue-frame and there are three. A seventh cube for a buckle was tried
    and thrown away: at 2.2 units it swallowed most of the band it was meant to sit on, and the
    brooch's rivet already paid for the lesson that a detail this size is a value against its
    neighbour rather than a box.

    band_lo gets a plain lit bar instead. Two identical buckles would say the sling is fastened
    twice, which is not what a second band on a quiver is for.

    `north` is band_hi's mounting face, a fifth of a unit off the chestplate and looking straight at
    it, and band_lo's back face looking into open air. Both are INNER: the first because nothing can
    get between it and the plate, the second because it is behind the tube from every angle that
    could reach it.

    `west` and `east` are the band in profile - on band_hi they are the bracket's cheeks and are
    three texels deep, which is the only place on this part where the mount is legible as a
    structure. `up` and `down` are the band's edges: the tube passes through the middle of both, so
    only the 0.1 of proud rim and, on band_hi, the run of bracket behind the tube, are ever seen."""
    f = face_rects(name)

    x0, y0, fw, fh = f["south"]          # 3 wide x 2 (band_hi) or 1 (band_lo) tall
    if plate:
        rows = ((M_LIT, M_APERTURE, M_LIT),          # the slot the strap threads
                (M_FACE, M_DIM, M_FACE))             # the plate under it
        for j, row in enumerate(rows):
            for i, lum in enumerate(row):
                put(img, x0 + i, y0 + j, lum + random.randint(-JITTER, JITTER))
    else:
        for i, lum in enumerate((M_FACE, M_LIT - 14, M_DIM)):
            put(img, x0 + i, y0, lum + random.randint(-JITTER, JITTER))

    for face, base in (("west", M_FACE + 22), ("east", M_DIM - 6)):
        x0, y0, fw, fh = f[face]         # d deep x h tall
        for j in range(fh):
            for i in range(fw):
                lum = base - round(20 * ramp(i, fw)) - round(14 * ramp(j, fh))
                put(img, x0 + i, y0 + j, lum + random.randint(-JITTER, JITTER))

    for face, base in (("up", M_FACE + 30), ("down", M_DIM - 30)):
        x0, y0, fw, fh = f[face]         # 3 wide x d deep, rows run back to front
        for j in range(fh):
            for i in range(fw):
                rim = i in (0, fw - 1) or j == 0
                put(img, x0 + i, y0 + j, (base if rim else M_INNER)
                    + random.randint(-JITTER, JITTER))

    fill(img, f["north"], M_INNER)       # the mounting face, or the air behind the lower band


def paint_fletch(img) -> None:
    """The ends of three arrows standing in the mouth: 2.2 x 2.7 x 1.4, on the `arrows` bone.

    One cube, three arrows, one texel column each. That is the whole budget and it decides the
    method: the arrows are read from the value STEP between neighbouring columns and from nothing
    else. Relief would not help even if there were room for it - the three would be coplanar and
    vanilla shades by normal alone - and alpha would not help either, because a gap cut between two
    shafts would show the inside of the bundle. So `south` runs 214 / 150 / 236 across and `up` runs
    the same way, and the middle shaft is the dark one so the outer two read as round.

    Row 0 of `south` is the fletching and rows 1 and 2 are shaft. The fletching gets a much wider
    jitter than anything else in this file - feathers are the one thing on this part that is not a
    smooth surface - and it is the brightest row, because it is the end of the part and it is what a
    player is meant to notice from thirty blocks away.

    `down` is inside the quiver and so is the bottom fifth of both flanks; the whole of `down` is
    INNER. `north` looks back over the shoulder blade at the plate."""
    f = face_rects("fletch")

    x0, y0, fw, fh = f["south"]          # 3 wide x 4 tall: two rows of fletching, two of shaft
    for j in range(fh):
        for i in range(fw):
            if i == GROOVE_COLUMN:       # the dark gap runs the whole length of the bundle
                put(img, x0 + i, y0 + j, A_GROOVE - 6 * j + random.randint(-JITTER, JITTER))
            elif j < FLETCHED_ROWS:      # each shaft is capped with its own mottled fletching
                put(img, x0 + i, y0 + j, A_NOCK - 4 * i + random.randint(-16, 16))
            else:
                lum = SHAFTS[i] - round(18 * ramp(j - FLETCHED_ROWS, fh - FLETCHED_ROWS))
                put(img, x0 + i, y0 + j, lum + random.randint(-JITTER, JITTER))

    x0, y0, fw, fh = f["up"]             # 3 wide x 2 deep - the nock ends, seen from above
    for j in range(fh):
        for i in range(fw):
            lum = SHAFTS[i] + (0 if i == GROOVE_COLUMN else 12) - round(26 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + random.randint(-6, 6))


    for face, base in (("west", A_LIT + 6), ("east", A_SHAFT - 22)):
        x0, y0, fw, fh = f[face]         # 2 deep x 4 tall - the outer shaft seen edge on
        for j in range(fh):
            for i in range(fw):
                if j < FLETCHED_ROWS:
                    put(img, x0 + i, y0 + j,
                        base - 4 - round(14 * ramp(i, fw)) + random.randint(-18, 18))
                    continue
                lum = base - round(22 * ramp(j, fh)) - round(20 * ramp(i, fw))
                put(img, x0 + i, y0 + j, lum + random.randint(-JITTER, JITTER))

    x0, y0, fw, fh = f["north"]          # 3 wide x 3 tall, back toward the plate
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j, A_SHADE - round(20 * ramp(j, fh))
                + random.randint(-JITTER, JITTER))

    fill(img, f["down"], A_INNER)        # inside the quiver


# The colour master value 127 maps to, through DecorationPalette.ofStaticColour: dark is half of it,
# light is halfway from it to white. This is vanilla's own undyed-leather-armour tint - the colour a
# player already reads as "leather" without being told, and the one the buckled belt uses.
LEATHER = (0xA0, 0x65, 0x40)


def check_geometry() -> None:
    """CUBES and FRAMES must be the cube list, the origins, the uv and the bone frames of the
    shipped geometry, in order.

    Painting a texture for a shape the model no longer has is invisible to every other check in this
    pipeline: both halves stay internally consistent while the rectangles slide off the faces they
    were drawn for. The origins are asserted because the docstring's clearances are statements about
    them, and the rotations because on this part they are the design - a quiver that has lost its
    -36 is a box on a spine."""
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

    # The four numbers the docstring is made of, read back off the table rather than trusted.
    assert CUBES["band_hi"][0][2] == -0.75, \
        "band_hi is the mount: it must reach sling-local z -0.75, which is body z 3.20 at its top"
    assert CUBES["tube"][0][2] == 0 and CUBES["tube"][1][2] == 2, \
        "the tube's near face must be the sling's own z = 0 plane - every belt clearance is measured"\
        " off it"
    assert CUBES["base"][0][1] < CUBES["tube"][0][1] + CUBES["tube"][1][1], \
        "the base must sink into the tube rather than butt onto it - two coincident opposed faces"
    mouth_top = CUBES["mouth"][0][1]
    assert mouth_top < FRAMES["fletch"][0][1] < mouth_top + CUBES["mouth"][1][1], \
        "the arrow bundle's foot - its own bone's pivot - must stand inside the mouth's flare"


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
    """The static layer: opaque LEATHER over the tube, the mouth and the base, transparent elsewhere.

    A transparent static pixel takes the trim material's ramp; an opaque one takes its own colour
    through the static ramp with the master's value as the shading. So this one file is the whole of
    the leather / steel / contents split, and it is derived from the master's own alpha rather than
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
    paint_tube(img)
    paint_mouth(img)
    paint_base(img)
    paint_band(img, "band_hi", plate=True)
    paint_band(img, "band_lo", plate=False)
    paint_fletch(img)

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

    # One fitting. The two bands alone are the guard and take a metal; the leather is in neither the
    # mask nor the base ramp, and the arrows are on the base ramp in every case.
    write_mask(img, [r for name in GUARD_CUBES for r in face_rects(name).values()], OUT_GUARD)


if __name__ == "__main__":
    main()
