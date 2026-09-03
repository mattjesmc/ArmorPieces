"""
Paint the grayscale master for the "wraps" part, and the mask for its `inlay` fitting.

Like the puttees, greaves, quiver and bandolier painters this does not merely claim that CUBES
matches the shipped geometry, it reads assets/armorpieces/armorpieces/decoration/wraps.json at run
time and asserts it (check_geometry) - the origins, the pivots AND the five bone rotations, because
on this part the rotations are the design twice over: four of them are the helix and the fifth is
the tucked end crossing it. A master painted for an untilted stack would stay perfectly
self-consistent while describing a different object. Output goes to
tools/decoration_masters/wraps.png and wraps_inlay.png, which sync_decoration_masters.py installs
for the game to colour per trim material and per dye.

Master convention: luminance carries shading, alpha carries silhouette. This master is 100% opaque,
for the puttees' reason: cloth wound round an arm has no fringe to fray, and because parts draw with
armorCutoutNoCull a hole cut in a winding would show the inside of that winding rather than the
sleeve behind it. Everything here is value.

WHAT THIS PART IS, AND HOW IT DIFFERS FROM THE PUTTEES

This is the arm's answer to the shipped Puttees and it shares their logic on purpose: turns of cloth
on tilted bones, an uneven pitch, and an overlap read carried by VALUE rather than by relief. What
it does not share is its geometry, because a forearm is not a shin.

  * the LEGS are 3.8 apart at the midline and the shipped Puttees' two copies meet there, which is
    why that part is a 5 x 2 x 2 band on the front of the leg and why its painter spends a whole
    paragraph on the seam. The ARMS are ten apart. There is no midline here, so a turn can be a
    CLOSED RING - a box that encircles the sleeve on all four sides - and this part is four of them.
    A ring has an outboard face, a back face and two annular caps that the Puttees simply do not
    have, and half this file is about what is worth painting on them.
  * FOUR turns, not three. The Puttees have five units of shin between the poleyns and the boot; the
    forearm gives 6.2 between the mantle's reach and the wrist, and four turns at a tightening pitch
    read as a wrap where three at this length would read as three bracelets.
  * the TUCK. The Puttees finish with a knot - unrotated, 2 x 2 x 1, standing 0.40 proud on the
    outboard shin, the brightest ledge in that file. This one finishes with a FLAP: a 1.6 x 4.4 x 0.5
    strip on its own bone at +26 about z, crossing the four turns at 31 degrees to them, whose upper
    end runs UNDER the top turn and whose lower end stands 0.26 proud of the bottom one with a
    metal pin through it. A knot is a lump you add; a tuck is an end you hide, and the difference is
    the whole reason this part is not the Puttees at another scale.

THE CUBES, IN PART-LOCAL UNITS AND IN THE ARM BONE'S

`vambraces` is a MIRRORED pair - Attachment.of(LEFT_ARM, 1, 6, 0) plus Attachment.mirrored on the
right - so the layer's scale(-1, 1, 1) runs on the right-hand copy and ONE master serves both. The
attachment's x = 1 is the arm box's own X centre (the box spans arm-local -1..3), so part-local
x = 0 is the middle of the arm and `west` (+x) is OUTBOARD on both arms, `east` (-x) inboard on
both. The outboard-lit / inboard-buried split therefore survives the flip, and it has to be painted
rather than left to the engine: vanilla's diffuse term gives +x and -x the same 0.6, exactly as it
gives +z and -z the same 0.8.

Part-local (0, 0, 0) is arm-local (1, 6, 0). +Y is DOWN. Each turn hangs from its own bone pivoted
on the arm's axis at (0, cy, 0); the tuck and its pin share a fifth bone at (1.2, 0.9, 0).

    cube    bone pivot / rot   local origin           size                arm-frame hull
    turn1   (0,-1.00) -5 deg   (-2.15, -0.95 , -3.49) (5.64, 1.9 , 6.98)  x -1.22..4.56 y 3.75..6.13
    turn2   (0, 0.55) -7 deg   (-2.15, -0.925, -3.29) (5.44, 1.85, 6.58)  x -1.25..4.38 y 5.23..7.73
    turn3   (0, 1.85) -6 deg   (-2.15, -0.825, -3.21) (5.36, 1.65, 6.42)  x -1.22..4.28 y 6.69..8.90
    turn4   (0, 3.00) -4 deg   (-2.15, -0.75 , -3.13) (5.28, 1.5 , 6.26)  x -1.20..4.17 y 8.03..9.90
    tuck    (1.2,0.9) +26 deg  (-0.8 , -2.2  , -3.39) (1.6 , 4.4 , 0.5 )  x  0.52..3.88 y 4.57..9.23
    pin     (same bone)        (-0.7 ,  1.5  , -3.95) (1.4 , 1.2 , 0.62)  x  0.39..2.17 y 7.94..9.63

WHAT CLEARS WHAT

Two surfaces cover the arm, and both are quoted here in the ARM BONE's frame rather than part-local,
because that is the frame trace_geometry reports in:

  * naked arm box        x -1..3   y -2..10  z -2..2
  * chestplate shell 1.0 x -2..4   y -3..11  z -3..3   <- the piece this socket belongs to

The arm shell is the OUTER deformation at the full 1.0 and nothing trims it. That is worth saying
plainly, because the LEG shells are not: `createBaseArmorMesh` re-adds both legs at `extend(-0.1)`,
so a legging's leg is 0.4 and a boot's is 0.9, and two shipped painters still carry 0.5 and 1.0 from
before that was found. None of it applies here. This part is authored against x -2..4, y -3..11,
z -3..3 and nothing else.

Each turn is a ring round that sleeve. Its OUTBOARD wall stands 0.56, 0.38, 0.28 and 0.17 proud of
it going down the arm and its front and back walls stand the same, because a ring's radius is one
number. Its INBOARD wall is the exception and is the one asymmetry in the box: it stops at arm-local
x = -1.20 to -1.25, which covers the naked arm's own -1 by a quarter of a unit but stops three
quarters of a unit SHORT of the sleeve's -2.

That is the part's one real compromise and it was made at the renderer. A ring closed all the way
round the sleeve reaches arm-local -2, which is world x 3 - and the torso's chestplate shell runs to
world x 5, so two whole units of banded cloth would sit inside the torso's x range on each arm. That
would be invisible if the ring were shallow, the way the shipped Mittens' inboard 0.5 is invisible
inside the same shell; but a ring standing at z +/-3.49 is OUTSIDE the torso shell's +/-3, so those
two units are drawn in FRONT of the belly instead of inside it. Rendered, that is four units of red
band crossing the front of the chest on a ten-unit torso, and it read as bracelets floating over the
stomach rather than as anything worn on an arm.

Stopping at -1.15 leaves 0.85 of sleeve uncovered on the inboard side. At rest that strip is world
x 3..3.85 at z +/-3, which is inside the torso's own shell and never seen; mid-stride, with the arm
swung forward, it can be glimpsed from a low angle on the inboard side. That is the cost, it is
paid once per swing at one angle, and it is much smaller than the cost of the alternative. `east` is
INNER on every turn for the same reason and is the only face of this part drawn purely so that no
hole appears.

Above, the new `mantle` on `pauldrons` rides this same arm bone and hangs to part y -2.78. turn1's
highest corner stops at -2.25, so the fur clears the cloth by 0.53. The shipped Spaulders stop at
-4.37 and are no constraint at all. Below, the naked arm box ends at arm-local y 10 and turn4's
lowest corner is 9.90 - the last turn is AT the wrist and nothing hangs over the hand.

The pair spans 19.12 units across the figure against the shoulders' 18, which trace_geometry flags
and which is right for this part: it is 0.56 of cloth outboard of a sleeve that is itself 1.0 proud
of the arm, and every shipped part on this bone - Spaulders at 20.65, Mantle at 22.89 - is wider.

THE PITCH, WHICH IS THE PART

The four bones pivot at part y -1.00, 0.55, 1.85 and 3.00, so the spacing tightens down the arm:
1.55, 1.30, 1.15. Read on the FRONT face at the arm's centre line, where a player meets it, the four
turns are exposed over

    turn1  1.91     nothing laps it
    turn2  1.53     turn1 laps 0.34 of it
    turn3  1.20     turn2 laps 0.46
    turn4  1.07     turn3 laps 0.43

and that sequence - not the individual numbers - is the whole point. Four equal exposures read as a
barcode however they are shaded; four unequal ones read as cloth wound by hand and pulled tighter as
it comes down to the wrist, which is how a wrap is actually wound. The Puttees found the same thing
on the shin at 2.00 / 1.44 / 1.32 and record what the first, evener cut looked like.

The lap is real and not just painted: each turn's radius is smaller than the one above it - 3.49,
3.29, 3.21, 3.13 - so where two turns share a y the upper one is outside and hides the lower. That
buys the correct OCCLUSION. It buys no shading at all, because the two faces are parallel and
vanilla shades by normal alone, which is why row 0 of every turn's front face is painted at LAP and
row 1 at EDGE: 74 against 224, four times down the arm at four different spacings.

THE TUCK, AND WHY IT IS A FLAP RATHER THAN A KNOT

`tuck` is a fifth bone at +26 about z - the opposite sign to all four turns, which lean -4 to -7 -
so the strip crosses them at 31 degrees. That crossing is what says "loose end" rather than "fifth
turn", and it is the only thing on this part that is not parallel to everything else.

Its depth is the argument. The strip runs from part z -3.39 to -2.89, one constant plane, while the
turns' front walls step out from -3.13 at the wrist to -3.49 at the elbow. So the same strip is

    0.10 UNDER turn1  - hidden, which is the tuck
    0.10 proud of turn2
    0.18 proud of turn3
    0.26 proud of turn4  - the loose tip

without a single rotation about x or y. The upper end disappears under the top turn exactly the way
the end of a bandage does, the lower end lifts off the cloth, and the transition is free. A knot
would have needed a cube proud on three sides and would have read as the Puttees' tie moved to
another limb.

The `pin` is 1.4 x 1.2 x 0.62 of metal through the loose tip, sunk 0.06 into the flap, and it is the
ONE thing on this part that stays on the base trim material. That is the Puttees' bargain exactly -
dyed cloth over hardware that still turns gold - and it is what stops a dyed pair from hiding the
material the piece was smithed in. It is small on purpose: the Puttees' knot is 2 x 2 x 1 and this
is smaller, because here the cloth has a tuck to look at and does not need a second focus.

THE FITTING

`armorpieces:inlay` is a dye and it takes the four turns and the tuck whole - every face of them, so
no cube boundary can show a colour seam - and leaves the pin on the trim material. Sixteen colours
of arm wrap over one bright fixing. No static layer ships: nothing on a cloth wrap has a colour it
must keep against the player's choice, and the shipped Puttees make the same call.

FACE LAYOUT AND ORIENTATION

The face rectangles come from paint_circlet_master.faces(): row one (v .. v+d) holds up then down,
each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west, south with widths
d, w, d, w. Sizes here are fractional, so the net rounds UP the way Blockbench does - every turn is
5.28 to 5.64 wide, which nets to six texels, and 6.26 to 6.98 deep, which nets to seven - so all
four turns share one 26 x 9 footprint and tile two to a row.

Orientation inside each rectangle is the table the greaves and puttees painters record as measured:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x              max z
    down            +y  (underside)      min x              max z
    west            +x  (outboard)       min z  (front)     min y (top)
    east            -x  (inboard)        max z  (back)      min y (top)
    north           -z  (front)          min x  (inboard)   min y (top)
    south           +z  (back)           max x  (outboard)  min y (top)

Which face of a ring is worth what:

    north   the front of the forearm, six columns by two rows. The HERO, and where the whole
            lap-and-pitch read lives.
    west    the outboard face, seven columns (front to back) by two rows. The face a third-person
            camera sees most of the time, and the one the tuck's tip leans over.
    south   the back of the forearm. Painted properly and dropped under the front, because an arm at
            rest shows it to anyone standing behind and it is the same cloth.
    east    inboard, inside the shell, against the torso. INNER on every turn.
    up      the top annulus, six by seven. Only turn1's is ever seen - the other three are inside the ring above,
            which is both higher and wider - and even turn1's shows only where it clears the shell,
            which is the outermost half-texel of the outer three edges.
    down    the underside annulus. On turns 1 to 3 it is the 0.20, 0.08 and 0.08 of overhang over
            the turn below, which is the one real shadow line the lap has; on turn4 it is the hem of
            the whole part at the wrist.
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
       / "decoration" / "wraps.json")
OUT = ROOT / "tools" / "decoration_masters" / "wraps.png"
INLAY = OUT.with_name("wraps_inlay.png")

TEX_W, TEX_H = 64, 32

# origin, size (w, h, d) and uv (u, v), mirroring wraps.json in that file's own walk order - the
# root bone `wrap` carries no cubes, so the order is its five children, and the tuck bone carries
# two. The origins are asserted with the sizes because every clearance in the docstring is a
# statement about them: -2.15 is the inboard wall stopping short of the sleeve, and the four z values
# are the radii the tuck's constant plane is measured against.
CUBES = {
    "turn1": ((-2.15, -0.95, -3.49),  (5.64, 1.9, 6.98),  (0, 0)),
    "turn2": ((-2.15, -0.925, -3.29), (5.44, 1.85, 6.58), (26, 0)),
    "turn3": ((-2.15, -0.825, -3.21), (5.36, 1.65, 6.42), (0, 9)),
    "turn4": ((-2.15, -0.75, -3.13),  (5.28, 1.5, 6.26),  (26, 9)),
    "tuck":  ((-0.8, -2.2, -3.39),    (1.6, 4.4, 0.5),    (52, 0)),
    "pin":   ((-0.7, 1.5, -3.95),     (1.4, 1.2, 0.62),   (52, 6)),
}

# The bone each cube hangs from: (pivot, z rotation). On this part the rotations ARE the design -
# four of them are the helix and the fifth is the tuck crossing it - so they are asserted rather
# than trusted. A lost tilt would turn a wound arm back into a stack of bracelets without moving one
# texel of this file, and a tuck that lost its +26 would become a fifth turn.
TUCK_FRAME = ((1.2, 0.9, 0), 26)
FRAMES = {
    "turn1": ((0, -1.0, 0), -5),
    "turn2": ((0, 0.55, 0), -7),
    "turn3": ((0, 1.85, 0), -6),
    "turn4": ((0, 3.0, 0), -4),
    "tuck": TUCK_FRAME,
    "pin": TUCK_FRAME,
}

TURNS = ("turn1", "turn2", "turn3", "turn4")
CLOTH_CUBES = TURNS + ("tuck",)

random.seed(67)  # deterministic output - regenerating must not churn the PNG

# Calibrated against the ramp, not guessed. The material ramp interpolates dark -> mid over master
# values 0..127 and mid -> light over 128..255, so a master confined to one half only ever uses half
# of a material's - or a dye's - range. This one runs the width of it, because the overlap read is
# made of nothing but the distance between LAP and EDGE.
LEDGE = 232      # turn1's top ring where it clears the shell - the brightest thing here
EDGE = 224       # a turn's free lower row on the front, at the peak of the lateral profile
FLANK = 190      # the outboard face at its front edge
BACK = 130       # the back of the forearm
CLOTH = 104      # turn1's upper row, where the wrap runs out under the sleeve
LAP = 74         # a turn's upper row, in the shadow of the turn that laps it
UNDER = 52       # an underside, and the overhang lip over the turn below
INNER = 34       # buried: inboard, inside the ring above, behind the tuck

T_TIP = 216      # the tuck's loose lower end
T_FACE = 176     # the tuck where it lies against the cloth
T_HIDDEN = 60    # the tuck's upper end, under turn1

P_LIT = 238      # the pin, on the base trim material
P_FACE = 196
P_DIM = 118
P_INNER = 36

FALL = 20        # per-turn falloff going down the arm, away from the light
JITTER = 3
WEAVE = 5        # the extra jitter a turn's front row gets - cloth, not sheet metal

# The lateral profile across a turn's six front columns, inboard to outboard. A MULTIPLIER rather
# than an offset, so the dark rows keep their shape instead of being flattened into INNER by a
# subtraction sized for the light ones - the shading of a cylinder is proportional. Column 0 is the
# inboard edge, which is against the torso and is floored near INNER; the peak sits one column in
# from the outboard edge so the cloth is seen to turn round the arm rather than end flat.
PROFILE = (0.40, 0.74, 0.92, 1.00, 0.98, 0.84)

# The same idea across the outboard face, whose seven columns run FRONT to BACK.
FLANK_PROFILE = (1.00, 0.97, 0.90, 0.82, 0.73, 0.64, 0.55)


def net(size):
    """A cube's box-UV net in whole pixels. Rounds UP the way Blockbench does - a turn is 5.28 to
    5.64 wide and nets to six texels, and 6.26 to 6.98 deep and nets to seven."""
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


def paint_turn(img, name: str, top: int, bottom: int, flank: int, lit_cap: bool) -> None:
    """One closed ring of cloth round the sleeve, on a bone tilted a few degrees about z.

    `top` is the value of the front face's row 0 - the upper half of the turn, which the turn above
    laps - and `bottom` that of row 1, its free lower edge. Those two numbers are the part.
    Everything a player reads as "wound cloth" rather than "four bracelets on an arm" is the
    distance between them repeated at four different spacings, because the geometry cannot help: the
    four front faces are parallel to each other and to the sleeve behind them, and vanilla lights
    parallel faces identically however far apart they are.

    Six columns, inboard to outboard. Column 0 is the one against the torso and is floored near
    INNER; the profile peaks at column 3 so the cloth is seen to turn round the arm rather than end
    flat.

    `west` is the outboard face and is the one this part can afford to spend on: it is seven texels
    of depth by two of height, it is never occluded by anything on the figure, and in third person it
    is what a player looks at. Its columns run FRONT to BACK and are painted as the same cylinder
    seen the other way round.

    `south` is the back of the forearm, painted at BACK rather than INNER: an arm at rest shows it to
    anyone standing behind, and it is the same cloth as the front.

    `east` is INNER on every turn - it is inside the sleeve's own wall and pressed against the
    torso, and it is the only face here drawn purely so no hole appears.

    `up` is worth painting only on turn1 (`lit_cap`); on the other three it is inside the ring above,
    which is both higher and wider, and hidden for good. Even on turn1 only the outermost texel of
    the front, back and outboard edges clears the shell, so that is all that is lit.

    `down` is painted on all four but means different things: on turns 1 to 3 it is the 0.20, 0.08
    and 0.08 of overhang over the turn below, the one real shadow line the lap has; on turn4 it is
    the hem of the whole part at the wrist."""
    f = face_rects(name)

    x0, y0, fw, fh = f["north"]          # 6 wide x 2 tall, col 0 = inboard, row 0 = top
    for j in range(fh):
        base = top if j == 0 else bottom
        for i in range(fw):
            lum = round(base * PROFILE[i])
            put(img, x0 + i, y0 + j, max(INNER, lum) + random.randint(-WEAVE, WEAVE))

    x0, y0, fw, fh = f["west"]           # 7 deep x 2 tall, col 0 = front
    for j in range(fh):
        for i in range(fw):
            lum = round(flank * FLANK_PROFILE[i]) - round(FALL * ramp(j, fh))
            put(img, x0 + i, y0 + j, max(INNER, lum) + random.randint(-JITTER, JITTER))

    x0, y0, fw, fh = f["south"]          # 6 wide x 2 tall, col 0 = OUTBOARD
    for j in range(fh):
        base = BACK if j else BACK - 34
        for i in range(fw):
            lum = round(base * PROFILE[fw - 1 - i])
            put(img, x0 + i, y0 + j, max(INNER, lum) + random.randint(-JITTER, JITTER))

    fill(img, f["east"], INNER)          # inside the sleeve's own wall, against the torso

    x0, y0, fw, fh = f["up"]             # 6 wide x 7 deep - an annulus, almost all of it in the arm
    for j in range(fh):
        for i in range(fw):
            rim = lit_cap and (i == fw - 1 or j in (0, fh - 1)) and i != 0
            lum = round(LEDGE * (0.75 + 0.25 * ramp(i, fw))) if rim else INNER
            put(img, x0 + i, y0 + j, lum + random.randint(-JITTER, JITTER))

    x0, y0, fw, fh = f["down"]           # same annulus underneath: the overhang, or the hem
    for j in range(fh):
        for i in range(fw):
            rim = (i == fw - 1 or j in (0, fh - 1)) and i != 0
            put(img, x0 + i, y0 + j, (UNDER if rim else INNER) + random.randint(-JITTER, JITTER))


def paint_tuck(img) -> None:
    """The free end of the wrap: 1.6 x 4.4 x 0.5 on a bone at +26 about z, crossing the four turns.

    Five rows down the strip and two columns across it. Row 0 is under turn1 and is painted at
    T_HIDDEN - it is not INNER, because the turn above it is only 0.10 proud and a low angle from
    below reaches the sliver of it that clears; rows 1 to 3 are the strip lying over turns 2 and 3,
    and row 4 is the loose tip standing 0.26 clear of turn4 and carrying the pin.

    The strip brightens downward, which is the opposite of every other face in this file and is the
    point: on the turns the light comes from above and each one is darker than the one over it,
    while on the tuck the END is what the eye should find, so it is the brightest cloth on the part
    after turn1's top ring. A tucked end that faded into the wrap would be a stripe.

    `south` faces the turns it lies on and is INNER. `up` is the cut end under turn1 and is INNER
    with it. `down` is the tip's underside, `west` and `east` its two edges - one texel each, and
    the only place on this part where a cloth edge is seen end on."""
    f = face_rects("tuck")

    x0, y0, fw, fh = f["north"]          # 2 wide x 5 tall, row 0 = the tucked upper end
    for j in range(fh):
        base = T_HIDDEN if j == 0 else round(T_FACE + (T_TIP - T_FACE) * ramp(j - 1, fh - 1))
        for i in range(fw):
            put(img, x0 + i, y0 + j, round(base * (1.0 if i else 0.88))
                + random.randint(-WEAVE, WEAVE))

    for face, mult in (("west", 1.0), ("east", 0.7)):
        x0, y0, fw, fh = f[face]         # 1 deep x 5 tall - the strip's two edges
        for j in range(fh):
            base = T_HIDDEN if j == 0 else round(T_FACE + (T_TIP - T_FACE) * ramp(j - 1, fh - 1))
            put(img, x0, y0 + j, round(base * mult) - 18 + random.randint(-JITTER, JITTER))

    fill(img, f["up"], INNER)            # the cut end, under turn1
    fill(img, f["down"], UNDER + 8)      # the tip's underside
    fill(img, f["south"], INNER)         # lying on the turns


def paint_pin(img) -> None:
    """The metal fixing through the loose tip: 1.4 x 1.2 x 0.62, sunk 0.06 into the flap.

    Two texels by two, which is the whole budget, and the whole budget goes on one thing: a lit top
    row over a dark lower one, so at any distance it is a bright dot on dyed cloth. There is no
    frame and no aperture; the Buckled Belt's buckle needed three columns for those and this has
    two, and the brooch's rivet is the standing proof that a detail this size is a value against its
    neighbour rather than a shape.

    It is the ONE thing on this part left on the base trim material, so on a red-dyed pair worn on
    gold armour this is the gold. `south` is inside the flap and is INNER."""
    f = face_rects("pin")

    x0, y0, fw, fh = f["north"]          # 2 wide x 2 tall
    rows = ((P_LIT, P_FACE), (P_FACE - 30, P_DIM))
    for j, row in enumerate(rows):
        for i, lum in enumerate(row):
            put(img, x0 + i, y0 + j, lum + random.randint(-JITTER, JITTER))

    fill(img, f["up"], P_LIT - 10)
    fill(img, f["down"], P_DIM - 50)
    for face, base in (("west", P_FACE + 16), ("east", P_DIM + 10)):
        x0, y0, fw, fh = f[face]         # 1 deep x 2 tall
        for j in range(fh):
            put(img, x0, y0 + j, base - round(28 * ramp(j, fh)) + random.randint(-JITTER, JITTER))
    fill(img, f["south"], P_INNER)       # sunk into the flap


def check_geometry() -> None:
    """CUBES and FRAMES must be the cube list, the origins, the uv, the pivots and the rotations of
    the shipped geometry, in order.

    Painting a texture for a shape the model no longer has is invisible to every other check in this
    pipeline: both halves stay internally consistent while the rectangles slide off the faces they
    were drawn for. The frames are asserted with the rest because on this part they are the design,
    and because the tuck's depth argument is a statement about four numbers in three different
    cubes."""
    doc = json.loads(GEO.read_text(encoding="utf-8"))
    found = []

    def walk(bone):
        pivot = tuple(bone.get("pivot", [0, 0, 0]))
        rot = bone.get("rotation", [0, 0, 0])
        for c in bone.get("cubes", []):
            found.append(((tuple(c["origin"]), tuple(c["size"]), tuple(c["uv"])), (pivot, rot[2])))
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

    # The three statements the docstring is made of, read back off the table rather than trusted.
    radii = [-CUBES[t][0][2] for t in TURNS]
    assert radii == sorted(radii, reverse=True), \
        "the turns must get NARROWER down the arm, so an upper turn laps the one below it"
    pitches = [FRAMES[b][0][1] - FRAMES[a][0][1] for a, b in zip(TURNS, TURNS[1:])]
    assert pitches == sorted(pitches, reverse=True) and len(set(pitches)) == len(pitches), \
        "the pitch must tighten toward the wrist and no two gaps may be equal - four even " \
        "exposures read as a barcode however they are shaded"
    assert all(FRAMES[t][1] < 0 for t in TURNS) and FRAMES["tuck"][1] > 0, \
        "the four turns lean one way (a helix) and the tuck crosses them the other; that crossing " \
        "is what says loose end rather than fifth turn"
    tuck_front = CUBES["tuck"][0][2]
    assert -radii[0] < tuck_front < -radii[1], \
        "the tuck's constant plane must run UNDER the top turn and PROUD of the second - that is " \
        "the whole tuck, and it costs no rotation about x or y"


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


def main() -> None:
    check_geometry()
    claimed = check_layout()
    img = Image.new("LA", (TEX_W, TEX_H), (0, 0))
    # Top turn first, then down the arm: each one a little darker than the one above it, because the
    # light is above and the wrist sits in the arm's own shadow.
    paint_turn(img, "turn1", CLOTH, EDGE, FLANK, lit_cap=True)
    paint_turn(img, "turn2", LAP, EDGE - FALL, FLANK - 16, lit_cap=False)
    paint_turn(img, "turn3", LAP - 8, EDGE - 2 * FALL, FLANK - 30, lit_cap=False)
    paint_turn(img, "turn4", LAP - 14, EDGE - 3 * FALL, FLANK - 42, lit_cap=False)
    paint_tuck(img)
    paint_pin(img)

    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque == set(claimed), "the opaque set is not exactly the UV rectangles"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)})")

    # The dye takes the four turns and the tuck whole - every face, so no cube boundary can show a
    # colour seam - and leaves the pin on the trim material.
    cloth = [r for name in CLOTH_CUBES for r in face_rects(name).values()]
    write_mask(img, cloth, INLAY)


if __name__ == "__main__":
    main()
