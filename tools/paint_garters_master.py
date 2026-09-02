"""
Paint the grayscale master for the "garters" part.

Like the poleyns painter one socket-mate over - and like the brooch, sash, tassets, spurs, greaves,
brush_crest and vambraces painters before it - this does not merely claim that CUBES matches the
shipped geometry, it reads assets/armorpieces/armorpieces/decoration/garters.json at run time and
asserts it: sizes, uv AND pivot-relative origins. The origins carry meaning here for the poleyns'
reason and for one of this part's own. First, every INNER pixel below is decided by testing a face
pixel against the other cubes and against the leggings shell, so a cube nudged a tenth of a unit
would leave the burial mask silently wrong. Second, this is a *flat* part on the tightest socket in
the mod, and its whole claim to be wearable rests on four clearances measured in quarters of a unit
against three shipped neighbours. Those four are asserted in check_neighbours() against the
neighbours' recorded hulls, because a quarter of a unit is exactly the size of edit nobody notices.
Output goes to tools/decoration_masters/garters.png, which sync_decoration_masters.py installs for
the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

**This master is 100% opaque**, for the poleyns' reason rather than the spurs': a ribbon has no
fretwork to punch, and a hole in a band one unit tall would not read as shaping, it would read as
the band being broken. Everything is value.

--------------------------------------------------------------------------------------------------
The part, in numbers

`KNEES` is `Attachment.of(LEFT_LEG, 0, 6, -2)` mirrored on the right, so part-local (0, 0, 0) is
leg-local (0, 6, -2) - the leg box's own front face, at the knee. Two frames are quoted throughout:
*part-local* (what the geometry JSON holds) and *leg-local* (part-local + (0, 6, -2)), which is what
`trace_geometry.py` prints. The leg box is leg-local x +-2, y 0..12, z +-2; the leggings shell - the
INNER armor layer, and on a leg that is 0.4 rather than 0.5, because `createBaseArmorMesh` re-adds
both legs at `extend(-0.1)` - is x +-2.4, y -0.4..12.4, z +-2.4. The boots shell is 0.9 for the same
reason, at x +-2.9.

    cube        part-local                                   leg-local
    band_front  x -2.20.. 2.80 y -0.50..0.50 z -1.05..-0.05  x -2.20.. 2.80 y 5.50..6.50 z -3.05..-2.05
    band_out    x  2.15.. 3.15 y -0.55..0.45 z -0.55.. 2.20  x  2.15.. 3.15 y 5.45..6.45 z -2.55.. 0.20
    band_in     x -3.15..-2.15 y -0.55..0.45 z -0.55.. 2.20  x -3.15..-2.15 y 5.45..6.45 z -2.55.. 0.20
    loop_f      x  2.85.. 3.85 y -0.85..0.95 z -0.75.. 0.25  x  2.85.. 3.85 y 5.15..6.95 z -2.75..-1.75
    knot        x  3.05.. 4.05 y -0.50..0.50 z  0.05.. 1.35  x  3.05.. 4.05 y 5.50..6.50 z -1.95..-0.65
    loop_b      x  2.85.. 3.85 y -0.85..0.95 z  1.15.. 2.15  x  2.85.. 3.85 y 5.15..6.95 z -0.85.. 0.15
    tail        x  2.95.. 3.95 y  0.40..2.20 z  0.35.. 1.25  x  2.95.. 3.95 y 6.40..8.20 z -1.65..-0.75

Seven cubes, one bone, no rotations - the fourth part in the mod with none, after the greaves, the
vambraces and the poleyns, and for a reason this part shares with none of them: a garter is a strap
pulled tight round a straight box, and a strap that is tight has nothing to cant. It also buys the
check the rotated parts cannot have, because `trace_geometry` only tests a cube for coplanarity with
a shell when the whole chain is axis-aligned. It reports none, on any of the three shells, and that
is not luck: every plane this part owns was picked off the shell planes on purpose, which is why the
numbers read -2.20 and 2.15 and -3.05 rather than -2.4 and 2.4 and -3.0.

The strap is one unit tall and one unit deep. Leg-local y 5.50..6.50 on a limb that runs 0..12 is
one texel of a twelve-texel leg, which is what a garter is; there was never a version of this part
that was two.

**Everything except the bow lies ON the armour rather than standing off it.** The front band's back
face is at leg-local z = -2.05, 0.35 *inside* the leggings shell's front wall at -2.40, and its
front face at -3.05 stands 0.65 proud of it. The two flanks do the same sideways: 0.25 of the cube
inside the shell's side wall at 2.40, 0.75 outside. That is the deliberate opposite of the poleyns'
choice one part over - the cop stands 0.40 *off* the leg and paints the crevice behind it - and it
is the right opposite, because a knee cop is bolted on and a garter is tied round. It costs this
part its back faces, which the burial mask takes; it buys a band with no shadow gap under it at any
camera angle and 0.65 of silhouette, which at sixteen texels to the block is 0.65 of a texel. A
ribbon should not have more.

**The bow is the one thing allowed to stand proud, and it stands proud OUTBOARD**, which on this
socket is the one free direction. Everything a knee can collide with lives in front of the leg or
below it: the tassets' lames come down the front, the greaves come up the front, the boots' spur
parts come off the back of the ankle. Nothing shipped reaches past leg-local x = 2.70 anywhere near
this height, so the bow runs from x 2.85 out to 4.05 - 1.65 proud of the shell, against the band's
0.65 - and still leaves the pair spanning 11.90 across the figure, against the 18 the shoulders
span.

The bow is three cubes and a hanging end, and it is shaped for one specific silhouette. Two loops
1.80 tall stand 0.35 above and 0.45 below the 1.00 strap they are tied to; between them is a 0.90
gap in z, filled only by a knot 1.00 tall and 0.20 more proud than either loop. That is the whole
trick: from outboard the part reads as two lobes and a waist, because the waist is a real notch
0.90 wide, cut 0.35 into the silhouette above the knot and 0.50 below the flank, rather than a
painted one. An earlier draft had loops 1.70 tall butted
against a one-unit buckle with 0.20 of overlap each side; it measured the same and rendered as a
lump, which is the difference between a bow and a latch and is why the numbers above are the ones
they are.

--------------------------------------------------------------------------------------------------
The four clearances, and the one collision that could not be avoided

Sampled against the neighbours' true rotated solids rather than the hulls `trace_geometry` prints:

    band_out  clears tassets:lame3         by 0.20 in x  (lame3 ends at x 1.95, the flank starts at 2.15)
    loop_b    clears heel_wings:vane_upper by 0.30 in z  (the vane's sweep starts at z 0.45)
    loop_f    clears greaves:greave        by 0.25 in x  (the greave plate ends at x 2.60)
    tail      clears greaves:greave        by 0.35 in x

Everything else on the part clears everything else it can be worn with by half a unit or more. Those
four are asserted in check_neighbours() against hulls recorded here from `trace_geometry`.

**The one collision is `band_front` into the tassets' third lame, and it is not avoidable.**
`DecorationAnchor.KNEES` warns that a knee part sits *inside* that lame rather than below it, and the
arithmetic bears it out with no room to argue. lame3 is a 2 x 3 x 2 plate carried on two -8 degree
bones, so it hangs diagonally across the front of the knee, and its rear face rides the leggings
shell's own front wall over the whole of this band's height: leg-local z = -2.52 at y 6.0 and -2.66
at y 6.5, against a shell wall at -2.40. The widest gap anywhere between the armour and the tasset at
knee height is 0.26, and a cube is one unit deep. Passing *in front* of lame3 instead needs leg-local
z <= -4.60, which is 2.6 units of standing proud on a part whose brief is flatness. The only other
free window is below lame3 and above the greave, and `trace_geometry` measures that at **0.38 in y**
(lame3's hull bottom 6.825, the greave plate's top 7.200) - which no one-unit cube fits either. So a
`knees` part that reads from the front chooses which neighbour to lap, exactly as the enum says, and
this one laps the same neighbour the poleyns lap.

What it does not do is lap it by the same amount. Sampling all seven cubes against the tassets' three
real solids: **6.3% of this part's volume is inside the shipped tassets**, all of it in `band_front`
(21.6% of that one cube), against the poleyns' 73% of the cop, 83% of the crown and 34% of the lame.
The difference is not subtlety, it is where the volume is: six sevenths of this part sits on the
flanks and outboard of the leg, where lame3 - only 2.00 wide, x -0.05..1.95 - never goes.

**The garter does not close at the back, and that is a measurement rather than a preference.** The
heel wings' upper vane is a 1 x 4 x 6 plate on a bone rotated (34, 14, 0) off the heel, and it sweeps
up and outboard through the whole back-outer quadrant of the knee. At this band's height it fills
everything outboard of about x 2.2 behind about z +1.1: a 5-wide back segment at leg-local z
2.05..3.05 sits 0.54 inside it, and the flanks themselves start biting at z +1.15. Both flanks
therefore stop at leg-local z = +0.20, two thirds of the way round a leg box that ends at +2.00, and
the bow's rearmost cube stops at +0.15. A closed ring is not available on this socket while the boots
can carry heel wings, and that is worth more to a later part than the ring would have been to this
one.

--------------------------------------------------------------------------------------------------
Three fractional dimensions

The flanks are 2.75 deep, the loops and the hanging end 1.8 tall, the knot 1.3 deep and the end 0.9.
It is the sash's knot problem and it gets the sash's answer: `net()` rounds UP, so those cubes get
nets a whole pixel wider than they use and the game maps each face across the fraction it has, and
`cell()` clamps a pixel's footprint to the cube's real extent so the burial test measures the solid
rather than the net. Without the clamp the last column of a 2.75-deep face would be tested a quarter
of a unit outside the cube, and both flanks would lose a pixel of INNER they should keep.

None of the four fractions is styling. 2.75 is where the flank has to stop to clear the heel wings'
vane by 0.25. 1.8 is the tallest a loop can be while clearing the greave plate's top by 0.25 with its
underside and the `pelt` candidate's lowest fall by 0.17 with its top. 1.3 is the shortest knot that
still laps 0.20 into each loop across a 0.90 gap. 0.9 lands the hanging end under the middle of the
knot, lapping the rear loop but sharing no plane with either.

--------------------------------------------------------------------------------------------------
Burial is computed, not eyeballed

The tassets note in PLAN.md is the method: sample each face at its pixel footprint, push 0.05 along
the face normal, and test containment against the boxes that could hide it. This painter does that
for every pixel of all forty-two faces, against the other six cubes and against the leggings shell,
and paints INNER wherever the *whole* pixel is covered. Partly-covered pixels are painted as visible,
which is the safe direction: a visible pixel painted dark is a mistake you can see, a buried pixel
painted bright is not.

Unlike the poleyns, **the shell finds plenty**, and that is the design working rather than failing.
Eight of the ninety pixels are INNER and all eight are the shell's:

    band_front.south   4 of 5   the strap's back, sunk 0.35 into the leggings; only the outboard
                                column survives, and only because the band is 5 wide on a shell
                                4.8 wide and hangs 0.40 past its side wall
    band_out.east      2 of 3   the flank's inboard face, likewise sunk 0.25 in
    band_in.west       2 of 3   the same face on the other flank

The bow contributes none: every cube of it lives outboard of x = 2.4 and the shell cannot reach it.
Neither does any cube of this part hide a whole texel of another - the ring laps its own corners by
0.05 and 0.65, the loops lap the flank and the knot laps the loops - so this master has no
cube-in-cube INNER at all, where the poleyns had three. check_mask() asserts exactly that: if a
cube-in-cube pixel ever appears, two cubes have been driven into each other.

The occluder list is short for the poleyns' reason, restated because it costs this part more: the
tassets, the greaves and the heel wings are all *optional* - one socket holds one part and a player
may wear none of them - so a mask that assumed the tassets would black out a fifth of `band_front`
for everyone wearing a garter on its own. A master is painted for the part, not for one combination
of parts.

--------------------------------------------------------------------------------------------------
Faces and their directions

Blockbench's face names, which are the ones the flip gives: bb = (-geo_x, 24 - geo_y, geo_z), so
`west` is the geo +x face - outboard on both legs after the layer's scale(-1, 1, 1) - and `east` is
the one facing the other knee. One master serves both legs because of it, and the lit-outboard /
shadowed-inboard split survives the mirror; it has to be painted rather than left to the engine,
because vanilla's diffuse term shades +x and -x identically, as it does +z and -z.

The face rectangles come from paint_circlet_master.faces(), copied verbatim over `net()`ed sizes:
row one (v .. v+d) holds up then down, each w wide, starting at u+d; row two (v+d .. v+d+h) holds
east, north, west, south with widths d, w, d, w. Orientation inside each rectangle is PLAN.md's
measured table:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x (inboard)    max z (back)
    down            +y  (underside)      min x (inboard)    max z (back)
    west            +x  (outboard)       min z (front)      min y (top)
    east            -x  (inboard)        max z (back)       min y (top)
    north           -z  (front)          min x (inboard)    min y (top)
    south           +z  (back)           max x (outboard)   min y (top)

A one-unit-tall band collapses most of this part's rectangles to a single row or column, the way the
poleyns' one-unit plate did: `band_front` is 5 x 1 on four faces and 1 x 1 on the other two, so there
is no falloff to run down anything and every gradient the strap has runs *across* - inboard to
outboard on the band, front to back on the flanks. The two places with a second axis to spend are the
loops and the hanging end, and both spend it downward.

--------------------------------------------------------------------------------------------------
The palette, and which faces are actually seen

The wing roots' warning applies: these constants do not transfer between parts by name, they mean "a
face that is seen" and "a face that is not". On a knee band the hero face is `band_front.north` - one
row of five pixels, square on to a camera at eye level, and the whole read of the part from the
front. The bow's three `west` faces are the read from the side, which is the angle one player looks
at another's legs from. `up` on the strap matters more than it looks: it is what a player sees of
their own knee looking down, and on a band this flat it is the only lit edge there is.

`band_out.west` is the one face this part spends and does not get back: the bow stands 0.70 proud of
it and covers all of its 2.75 but the rearmost 0.05, so it is painted as backing for the loops
rather than as a feature, with no highlight anywhere on it to fight them.

The knot is 250 and the loops are 212, and the faces of the loops that touch the knot are dropped to
86. That gap is the rowel's lesson - at one texel a detail is a value against its neighbour, and when
every neighbour is also bright none of them is a detail - and it is doing two jobs here: it makes the
knot read as a buckle rather than as more ribbon, and it is the only shading that says the two loops
are two. The hanging end starts at 152 and falls 40 down its two rows, because it hangs into the 0.25
seam over the greave where nothing lights it, and because a ribbon end that does not darken reads as
a second buckle.

Values run 39..254. Of the 90 painted pixels 82 survive the burial mask and 8 are INNER; 53 of them
sit below 127, which is the circlet's lesson - the material ramp interpolates dark -> mid over 0..127
and mid -> light over 128..255, so a master that never dips below the middle only ever uses half of
every material's ramp. The split landing past even is the shape talking: a strap has two lit aspects,
its top and its outward face, and four that are underside, seam or buried, and on a band one unit
tall the undersides are as many pixels as the tops. Nearly all of this part's light is spent on ten
pixels - the five of `band_front.north`, the five of its `up` - and on the eight of the bow's
outboard faces.

--------------------------------------------------------------------------------------------------
The fitting

One fitting, `armorpieces:inlay`, a dye, over everything except the knot. The sash's argument on a
part a fifth of its size: a ribbon was never meant to be redstone, and on a part this small a dye is
most of its variety - one part becomes sixteen while the knot keeps whatever metal the smithing table
put there, so a garter is a coloured strap with a metal buckle rather than a strap in a second metal.
The mask is the sash's kind, the master restricted to the ribbon's face rectangles, because the
ribbon's shading IS the dye's shading; nothing here wants a second cut.

It survives the size test, which is the thing to check before spending a fitting on a part this
small. 80 of the 90 pixels are ribbon and 10 are knot, and the ten are not scattered: they are one
cube, whose two `west` pixels are the brightest on the part and sit in the middle of a bow whose four
loop pixels the mask does cover. So a dyed garter reads as a coloured strap with a metal knot at
every angle that shows the bow at all, and as a coloured strap from every angle that does not. A mask
that had covered the knot too would have been a fitting that turns the whole part one colour, which
is a recolour and not an inlay.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image

from fitting_mask import write_mask

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "garters.json"
OUT = ROOT / "tools" / "decoration_masters" / "garters.png"

TEX_W, TEX_H = 64, 32

# size (w, h, d), uv (u, v) and pivot-relative origin, mirroring garters.json in that file's own
# order. The single bone sits at the anchor with no rotation, so origin IS the part-local corner.
#   band_front - the strap across the front of the knee. Back face 0.35 inside the leggings shell,
#                front face 0.65 proud of it; 5 wide on a shell 4.8 wide, so its ends clear the
#                corners the flanks turn.
#   band_out   - the outboard flank: 0.25 in, 0.75 out. Stops 2.75 back, which is where the heel
#                wings' upper vane starts sweeping through.
#   band_in    - the inboard flank, mirrored. Its outer face lands at world x -1.15 on the left leg
#                and +0.15 on the right, so the pair clears itself by 0.30 between the knees.
#   loop_f     - the bow's forward loop, 1.8 tall: 0.35 above and 0.45 below the strap.
#   knot       - the knot the strap is tied through, 0.20 more proud than either loop and the one
#                cube the inlay mask does not cover.
#   loop_b     - the bow's rear loop, leaving a 0.90 gap for the knot to sit in.
#   tail       - the free end hanging from under the knot, outboard of everything the greave has.
CUBES = {
    "band_front": ((5, 1, 1),      (0, 0),  (-2.20, -0.50, -1.05)),
    "band_out":   ((1, 1, 2.75),   (0, 3),  (2.15, -0.55, -0.55)),
    "band_in":    ((1, 1, 2.75),   (10, 3), (-3.15, -0.55, -0.55)),
    "loop_f":     ((1, 1.8, 1),    (14, 0), (2.85, -0.85, -0.75)),
    "knot":       ((1, 1, 1.3),    (24, 0), (3.05, -0.50, 0.05)),
    "loop_b":     ((1, 1.8, 1),    (19, 0), (2.85, -0.85, 1.15)),
    "tail":       ((1, 1.8, 0.9),  (20, 3), (2.95, 0.40, 0.35)),
}

# The cubes the inlay dye covers: the ribbon, which is everything but the knot.
RIBBON = tuple(name for name in CUBES if name != "knot")

# The leggings shell over this leg, in part-local coordinates (leg-local x +-2.4, y -0.4..12.4,
# z +-2.4 shifted by the anchor at (0, 6, -2)). It is the INNER armor layer, 0.5 everywhere but the
# legs and 0.4 on them because createBaseArmorMesh re-adds both legs at extend(-0.1). It is always
# worn when this part draws and it rides the same bone, so anything inside it is buried permanently.
# The boots shell is NOT in this list: it is optional, and its texture is transparent this far up the
# leg, so it neither occludes this part nor can fight it.
SHELL = ((-2.4, -6.4, -0.4), (2.4, 6.4, 4.4))

# The shipped neighbours this part can be worn beside, as leg-local hulls read out of
# `trace_geometry.py`. They are a recorded datum, not a dependency - nothing here reads their files -
# and check_neighbours() asserts the four clearances the part's wearability rests on. If a cube of
# this part is ever moved, the number that vanished is named here instead of being discovered in
# game; if one of those parts is reshaped, this file is the place the new numbers get written down.
NEIGHBOURS = {
    "tassets:lame3":         ((-0.05, 3.39, -4.68), (1.95, 6.83, -1.93)),
    "greaves:greave":        ((-2.40, 7.20, -2.75), (2.60, 12.20, -0.75)),
    "heel_wings:vane_upper": ((1.91, 3.72, 0.45), (4.62, 10.39, 7.69)),
}
ANCHOR = (0.0, 6.0, -2.0)  # part-local -> leg-local

PUSH = 0.05      # how far off a face a sample sits before it is tested for containment
EPS = 1e-9

random.seed(37)  # deterministic output - regenerating must not churn the PNG

KNOT = 250      # the knot's outboard plate: the brightest thing on the part by 38
TOP = 234       # a strap's top face - the lit edge, and what a player sees of their own knee
LOOP = 212      # a bow loop's outboard face
FACE = 190      # `north` on the front band: the strap across the knee, the read from ahead
FLANK = 166     # `west` on the outboard flank, all but 0.25 of it behind the bow
TAILF = 152     # the hanging end's outboard face
CAP = 118       # a cut end of the strap, half of it tucked behind the neighbouring cube
IN = 92         # `east`, geo -x: the inboard aspect, across 0.30 of air at the other knee's garter
SEAM = 70       # where one ribbon passes under another, or under the knot
CREVICE = 56    # a back face standing outside the shell but turned towards the leg
INNER = 44      # buried - wholly inside the leggings shell
DOWN = 36       # a free underside

RIM = 18        # the lit chamfer along a free top edge
FALL = 26       # top-to-bottom falloff down a standing face
ZFALL = 18      # front-to-back falloff along a flank
XGAIN = 24      # inboard-to-outboard brightening across a face's width
LAP = 40        # the shadow where one cube emerges from under another
LIP = 16        # a free lower edge catching light off its own roll


def net(size):
    """A cube's box-UV net in whole pixels. Rounds UP; see the docstring on the four fractions."""
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


def bounds(name):
    """A cube's part-local (lo, hi) corners."""
    size, _, origin = CUBES[name]
    return tuple(origin), tuple(origin[a] + size[a] for a in range(3))


def leg(name):
    """The same corners in the leg bone's frame, which is what trace_geometry prints."""
    lo, hi = bounds(name)
    return (tuple(lo[a] + ANCHOR[a] for a in range(3)),
            tuple(hi[a] + ANCHOR[a] for a in range(3)))


def fspan(lo, hi, axis, i):
    """Pixel i's footprint along one axis, counted from the minimum and clamped to the cube.

    The net rounds up, so a 2.75-deep cube gets three columns of which the last covers only 0.75 of a
    unit. Clamping is what makes the burial test measure the solid rather than the net."""
    return (min(lo[axis] + i, hi[axis]), min(lo[axis] + i + 1, hi[axis]))


def rspan(lo, hi, axis, i):
    """The same footprint counted from the maximum, for the faces whose column 0 is the far end."""
    return (max(hi[axis] - i - 1, lo[axis]), max(hi[axis] - i, lo[axis]))


def cell(name, face, i, j):
    """The part-local footprint of one face pixel, already pushed 0.05 off the face.

    The two in-plane axes span the pixel's whole (clamped) square rather than just its centre, so a
    pixel only counts as buried when *all* of it is - see the docstring. The normal axis is a single
    value, which is what makes the test "is this sample inside that box" rather than "do these boxes
    touch"."""
    lo, hi = bounds(name)
    if face == "up":                       # col 0 = min x, row 0 = max z, normal -y
        x0, x1 = fspan(lo, hi, 0, i)
        z0, z1 = rspan(lo, hi, 2, j)
        return ((x0, lo[1] - PUSH, z0), (x1, lo[1] - PUSH, z1))
    if face == "down":                     # col 0 = min x, row 0 = max z, normal +y
        x0, x1 = fspan(lo, hi, 0, i)
        z0, z1 = rspan(lo, hi, 2, j)
        return ((x0, hi[1] + PUSH, z0), (x1, hi[1] + PUSH, z1))
    if face == "east":                     # col 0 = max z, row 0 = min y, normal -x
        z0, z1 = rspan(lo, hi, 2, i)
        y0, y1 = fspan(lo, hi, 1, j)
        return ((lo[0] - PUSH, y0, z0), (lo[0] - PUSH, y1, z1))
    if face == "west":                     # col 0 = min z, row 0 = min y, normal +x
        z0, z1 = fspan(lo, hi, 2, i)
        y0, y1 = fspan(lo, hi, 1, j)
        return ((hi[0] + PUSH, y0, z0), (hi[0] + PUSH, y1, z1))
    if face == "north":                    # col 0 = min x, row 0 = min y, normal -z
        x0, x1 = fspan(lo, hi, 0, i)
        y0, y1 = fspan(lo, hi, 1, j)
        return ((x0, y0, lo[2] - PUSH), (x1, y1, lo[2] - PUSH))
    if face == "south":                    # col 0 = max x, row 0 = min y, normal +z
        x0, x1 = rspan(lo, hi, 0, i)
        y0, y1 = fspan(lo, hi, 1, j)
        return ((x0, y0, hi[2] + PUSH), (x1, y1, hi[2] + PUSH))
    raise KeyError(face)


def inside(box, clo, chi) -> bool:
    """True when the whole of a face pixel's footprint lies inside one box."""
    blo, bhi = box
    return all(blo[a] - EPS <= clo[a] and chi[a] <= bhi[a] + EPS for a in range(3))


def buried_by_shell(name, face, i, j) -> bool:
    """True when this face pixel is wholly inside the leggings shell. Eight are; the design put them
    there and check_mask() names which."""
    return inside(SHELL, *cell(name, face, i, j))


def buried(name, face, i, j) -> bool:
    """True when the whole of this face pixel is inside the leggings shell or inside another cube."""
    clo, chi = cell(name, face, i, j)
    boxes = [SHELL] + [bounds(other) for other in CUBES if other != name]
    return any(inside(box, clo, chi) for box in boxes)


def put(img, x: int, y: int, lum: int, alpha: int = 255) -> None:
    if 0 <= x < TEX_W and 0 <= y < TEX_H:
        img.putpixel((x, y), (max(0, min(255, lum)), alpha))


def ramp(i: int, n: int) -> float:
    """Position along a face axis, 0.0 at column/row 0 and 1.0 at the far end."""
    return 0.0 if n <= 1 else i / (n - 1)


def paint_face(img, name, face, value) -> int:
    """Fill one face rectangle, INNER wherever the burial test says the pixel cannot be seen.

    Returns the number of pixels that survived as visible, which main() reports - a face whose count
    goes to zero after a geometry edit is the loudest warning this file can give without failing."""
    x0, y0, fw, fh = faces(CUBES[name][0], CUBES[name][1])[face]
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
# band_front - the strap across the knee


def front_north(i, j, fw, fh):
    """The front of the knee: five pixels, one row, and the whole of this part seen head on.

    There is no second axis to shade across - the band is one unit tall - so everything this face has
    to say is said sideways. It brightens outboard, and the two end columns are dropped well below
    the field because they are the 0.40 of strap hanging past the leggings shell's side walls, where
    the band turns the corner onto the flanks and starts facing away from a camera in front of it.
    Dropping them is also what stops a five-pixel bar reading as a five-pixel bar: at this size an
    unbroken row of one value is a decal, and a row with darker ends is a strap with thickness."""
    if i in (0, fw - 1):
        return FACE - 38 + round(XGAIN * ramp(i, fw))
    return FACE - 12 + round(XGAIN * ramp(i, fw))


def front_up(i, j, fw, fh):
    """The top of the strap, 5 x 1: a one-unit ledge, wholly clear of the shell, and the only lit
    edge a band this flat gets. It is what a player sees of their own knee looking down, and it is
    where a tasset's lames cross on their way down the thigh."""
    return TOP + RIM - round(28 * (1.0 - ramp(i, fw)))


def front_down(i, j, fw, fh):
    """The underside, 5 x 1. On the poleyns this was a sliver in a seam; here it is the shadow line
    that separates the strap from the leg below it, and it is why a one-texel band reads at all from
    below eye level. Graded outboard like everything else on the part."""
    return DOWN + round(12 * ramp(i, fw))


def front_west(i, j, fw, fh):
    """The strap's outboard cut end, one pixel, tucked inside the outboard flank for all but its
    front 0.50. Painted at CAP rather than as a lit face: it is a seam, not an edge."""
    return CAP


def front_east(i, j, fw, fh):
    """The inboard cut end, one pixel, the same seam on the side nobody looks at."""
    return CAP - 30


def front_south(i, j, fw, fh):
    """The strap's back, 5 x 1, column 0 outboard. Four of the five pixels are inside the leggings
    shell and the mask takes them; this paints the outboard one, which survives only because the band
    is 5 wide on a 4.8-wide shell and hangs 0.40 past its wall. It faces the armour across nothing at
    all, so it is CREVICE."""
    return CREVICE


# ------------------------------------------------------------------------------------------------
# band_out - the outboard flank


def out_west(i, j, fw, fh):
    """The outboard profile, three columns front to back - the face this part spends and does not get
    back. The bow stands 0.70 proud of it and covers all of it but the rearmost 0.05, so it is painted
    as backing for the loops rather than as a feature: FLANK falling away to the rear, and no
    highlight anywhere on it to fight the knot."""
    return FLANK - round(ZFALL * ramp(i, fw))


def out_east(i, j, fw, fh):
    """The flank's inboard face, column 0 the back. Two of three columns are inside the leggings shell
    and the mask takes them; the survivor is the front one, which reaches 0.15 past the shell's front
    wall and looks into the 0.05 slot between this flank and the front band."""
    return SEAM


def out_up(i, j, fw, fh):
    """The top of the flank, one column and three rows running BACK to front. Row 2 is the front,
    under the leading edge of the bow's forward loop; rows 0 and 1 are open sky. Falls off backward
    because the leg turns away there and because the flank stops before the knee's rear quarter."""
    return TOP - 16 - round(22 * (1.0 - ramp(j, fh)))


def out_down(i, j, fw, fh):
    """The flank's underside, rows back to front. Free of everything - the greave plate's top is 0.75
    below it - so it is graded rather than flat, brightest at the front where a camera below the knee
    can see up into it."""
    return DOWN + LIP - round(10 * (1.0 - ramp(j, fh)))


def out_north(i, j, fw, fh):
    """The flank's front cut end, one pixel. Its inboard 0.65 is behind the front band and its
    outboard 0.35 is not, so it is half a seam and half an edge: CAP with a rim."""
    return CAP + RIM


def out_south(i, j, fw, fh):
    """The flank's rear cut end - where the garter stops rather than closing, because the heel wings'
    vane owns everything behind it. It faces backward into that space, lit by nothing."""
    return CREVICE + 6


# ------------------------------------------------------------------------------------------------
# band_in - the inboard flank


def in_east(i, j, fw, fh):
    """The inboard flank's outer face, column 0 the back: the one face of this part that looks across
    the gap between the legs, at the other knee's own garter 0.30 away. Nothing covers it, so it is
    painted as the dimmest lit face rather than as filler, falling off backward the way its outboard
    twin does but from IN instead of from FLANK."""
    return IN - round(ZFALL * ramp(i, fw))


def in_west(i, j, fw, fh):
    """The inboard flank's leg-facing side. Two of three columns are inside the leggings shell and the
    mask takes them; the survivor is the front one, looking into the slot behind the band."""
    return SEAM - 12


def in_up(i, j, fw, fh):
    """The top of the inboard flank, rows back to front - lit, but from the shaded side of the leg."""
    return TOP - 52 - round(16 * (1.0 - ramp(j, fh)))


def in_down(i, j, fw, fh):
    return DOWN + round(8 * ramp(j, fh))


def in_north(i, j, fw, fh):
    """The inboard flank's front cut end, one pixel - and the one value on this master that was set
    by looking rather than by arithmetic. At CAP - 26 it read, head on, as a hole punched beside the
    strap rather than as the strap turning the corner: on a band five pixels wide, one pixel 90 below
    its neighbour is not shading, it is a gap. It sits just under CAP now, still 14 below its outboard
    twin because this is the shaded side of the leg."""
    return CAP + 4


def in_south(i, j, fw, fh):
    return CREVICE


# ------------------------------------------------------------------------------------------------
# the bow - two loops, the knot in the gap between them, and the hanging end


def loop_west(i, j, fw, fh):
    """A loop's outboard face, one column and two rows: the bow's wing, and the second brightest thing
    on the part. Row 1 is only 0.80 of a unit of real face - the loops are 1.8 tall - so the falloff
    down it covers more ground than the row count suggests. It sits 38 below the knot deliberately:
    three bright cubes side by side would be one bright blob."""
    return LOOP - round(FALL * ramp(j, fh))


def loop_east(i, j, fw, fh):
    """A loop's inboard face. Most of it is inside the flank it is tied round - not by a whole texel,
    so the mask leaves it alone - and none of it is ever seen."""
    return SEAM


def loop_out(i, j, fw, fh):
    """The face of a loop that points away from the knot: forward on loop_f, backward on loop_b. These
    two are the bow's silhouette from straight ahead and straight behind, which on a part only 5 wide
    is the only way the bow announces itself to a camera that cannot see the outboard side."""
    return LOOP - 34 - round(FALL * ramp(j, fh))


def loop_knot(i, j, fw, fh):
    """The face of a loop that the knot sits in front of, across the 0.90 gap. Dropped to 86, which is
    126 below the loop's own outboard face, because that shadow is doing two jobs: it is what makes
    the knot read as hardware rather than as more ribbon, and it is the only thing on the master that
    says the two loops are two. The vambraces' rim under its cannon, at a fifth the size."""
    return SEAM + 16 - round(8 * ramp(j, fh))


def loop_up(i, j, fw, fh):
    """A loop's top, one pixel. It stands 0.35 above the strap it is tied to, so it is the highest lit
    face on the part and is painted as one."""
    return TOP + 6


def loop_down(i, j, fw, fh):
    """A loop's underside, one pixel, hanging 0.45 below the strap and 0.25 above the greave plate."""
    return DOWN + LIP


def knot_west(i, j, fw, fh):
    """The knot's outboard plate, two pixels front to back: 250, the brightest on the master, and the
    only pixels of this part that are not ribbon. It stands 0.20 proud of the loops on either side of
    it, which is what makes the value legible as a step rather than as noise - and it is the one cube
    the inlay mask leaves alone, so a dyed garter keeps a metal knot here."""
    return KNOT - round(10 * ramp(i, fw))


def knot_up(i, j, fw, fh):
    """The knot's top, one column and two rows running back to front. It sits level with the strap's
    own top, so this is the only place on the part where two lit tops meet, and the row nearest the
    camera is the brighter of the two."""
    return KNOT - 22 - round(12 * (1.0 - ramp(j, fh)))


def knot_down(i, j, fw, fh):
    """The knot's underside - and the roof of the seam the hanging end comes out of."""
    return DOWN + 24


def knot_edge(i, j, fw, fh):
    """The knot's fore and aft edges, one pixel each, each sunk 0.20 between the loops. Metal, so well
    above the ribbon's seam value, but far enough under the plate to read as its sides."""
    return KNOT - 96


def knot_east(i, j, fw, fh):
    """The knot's leg-facing side, inside the flank. Never seen; kept off INNER only because the
    footprint test cannot prove it."""
    return SEAM + 8


def tail_west(i, j, fw, fh):
    """The hanging end's outboard face, one column and two rows. It falls away downward harder than
    anything else on the part, because it hangs into the 0.25 seam over the greave where nothing
    lights it - and because a ribbon end that does not darken reads as a second buckle."""
    return TAILF - round(40 * ramp(j, fh))


def tail_east(i, j, fw, fh):
    return IN - 26 - round(20 * ramp(j, fh))


def tail_north(i, j, fw, fh):
    """The end's forward face - the one a camera in front of the knee catches past the leg's edge, and
    with `loop_f.north` the only part of the bow that shows from dead ahead."""
    return TAILF - 26 - round(24 * ramp(j, fh))


def tail_south(i, j, fw, fh):
    return TAILF - 48 - round(20 * ramp(j, fh))


def tail_up(i, j, fw, fh):
    """The end's top, one pixel, wholly under the knot it hangs from: the seam where the strap passes
    through and turns down."""
    return SEAM - 10


def tail_down(i, j, fw, fh):
    """The lowest face of the whole part and its only free underside - what a camera below the knee
    sees, and what closes the 0.25 gap over the greave plate."""
    return DOWN + LIP - 6


PAINTERS = {
    ("band_front", "north"): front_north, ("band_front", "up"): front_up,
    ("band_front", "down"): front_down, ("band_front", "west"): front_west,
    ("band_front", "east"): front_east, ("band_front", "south"): front_south,

    ("band_out", "west"): out_west, ("band_out", "east"): out_east, ("band_out", "up"): out_up,
    ("band_out", "down"): out_down, ("band_out", "north"): out_north,
    ("band_out", "south"): out_south,

    ("band_in", "east"): in_east, ("band_in", "west"): in_west, ("band_in", "up"): in_up,
    ("band_in", "down"): in_down, ("band_in", "north"): in_north, ("band_in", "south"): in_south,

    ("loop_f", "west"): loop_west, ("loop_f", "east"): loop_east, ("loop_f", "north"): loop_out,
    ("loop_f", "south"): loop_knot, ("loop_f", "up"): loop_up, ("loop_f", "down"): loop_down,

    ("loop_b", "west"): loop_west, ("loop_b", "east"): loop_east, ("loop_b", "south"): loop_out,
    ("loop_b", "north"): loop_knot, ("loop_b", "up"): loop_up, ("loop_b", "down"): loop_down,

    ("knot", "west"): knot_west, ("knot", "east"): knot_east, ("knot", "up"): knot_up,
    ("knot", "down"): knot_down, ("knot", "north"): knot_edge, ("knot", "south"): knot_edge,

    ("tail", "west"): tail_west, ("tail", "east"): tail_east, ("tail", "north"): tail_north,
    ("tail", "south"): tail_south, ("tail", "up"): tail_up, ("tail", "down"): tail_down,
}


def check_geometry() -> None:
    """CUBES must be the shipped geometry, in order: sizes, uv AND pivot-relative origins.

    Painting a texture for a shape the model no longer has is invisible to every other check in this
    pipeline - `bb_geo roundtrip` checks the model against itself and check_layout() checks the master
    against itself, and both keep passing while the rectangles slide off the faces they were drawn
    for. The origins are asserted as well as the sizes because this painter's burial mask AND its four
    neighbour clearances are computed from them: a cube nudged a fifth of a unit would leave every
    INNER pixel below wrong and the part inside a greave, with nothing else in the mod noticing."""
    doc = json.loads(GEO.read_text(encoding="utf-8"))
    assert (doc["texture_width"], doc["texture_height"]) == (TEX_W, TEX_H), \
        f"{GEO.name} is {doc['texture_width']}x{doc['texture_height']}, this master is {TEX_W}x{TEX_H}"
    assert len(doc["bones"]) == 1, f"{GEO.name} has {len(doc['bones'])} bones; this master assumes 1"
    bone = doc["bones"][0]
    assert not bone.get("children"), f"{GEO.name}'s bone has children; this master assumes it does not"
    assert tuple(bone.get("pivot", [0, 0, 0])) == (0, 0, 0), \
        f"{GEO.name}'s bone pivot is {bone.get('pivot')}, not the anchor itself"
    assert all(r == 0 for r in bone.get("rotation", [0, 0, 0])), \
        f"{GEO.name}'s bone is rotated; every burial mask here assumes axis-aligned cubes"
    found = [(tuple(float(v) for v in c["size"]), tuple(c["uv"]),
              tuple(float(v) for v in c["origin"])) for c in bone["cubes"]]
    want = [(tuple(float(v) for v in size), uv, tuple(float(v) for v in origin))
            for size, uv, origin in CUBES.values()]
    assert found == want, f"CUBES disagrees with {GEO.name}: {found} vs {want}"


def check_planes() -> None:
    """No two cubes of this part may put OVERLAPPING faces in one plane, whichever way they point.

    The sash's rule, sharpened - and it had to be, because this part is a ring with a mirrored pair of
    flanks. Six pairs of faces here share a plane value while lying nowhere near each other: the two
    flanks are the same shape at opposite x, the two loops the same shape at opposite z, and the knot
    sits at the strap's own height. The poleyns' flat "no two cubes may share a plane" would have
    failed on all six. What actually z-fights is two coplanar faces whose rectangles overlap, and that
    is what this tests. It finds none: every plane that could have collided was placed 0.05 or more off
    its neighbour on purpose."""
    for a, name_a in enumerate(CUBES):
        for name_b in list(CUBES)[a + 1:]:
            lo_a, hi_a = bounds(name_a)
            lo_b, hi_b = bounds(name_b)
            for axis, label in enumerate("xyz"):
                other = [t for t in range(3) if t != axis]
                if not all(min(hi_a[t], hi_b[t]) - max(lo_a[t], lo_b[t]) > EPS for t in other):
                    continue
                for va in (lo_a[axis], hi_a[axis]):
                    for vb in (lo_b[axis], hi_b[axis]):
                        assert abs(va - vb) > EPS, \
                            f"{name_a} and {name_b} put overlapping faces in the plane {label} = {va:g}"


def check_layout() -> dict:
    """Every face rectangle must sit inside the texture and no two may overlap - a silent overlap
    would paint one cube's shading onto another's face and only show up on a model in game."""
    claimed = {}
    for name, (size, uv, _) in CUBES.items():
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
    """The face pixels the burial test leaves visible."""
    fw, fh = faces(CUBES[name][0], CUBES[name][1])[face][2:]
    return {(i, j) for j in range(fh) for i in range(fw) if not buried(name, face, i, j)}


def check_mask() -> None:
    """The burial facts the shape was designed around, asserted rather than described.

    Each one is a geometric claim made in the docstring above, and each would break silently if a cube
    moved: the mask would still be *a* mask and the render would still be *a* render."""
    # The strap is sunk into the leggings shell all the way round - that is the whole difference
    # between this part and the poleyns, and it is what the mask is for. The front band's back keeps
    # only its outboard pixel, the 0.40 that hangs past the shell's side wall.
    assert seen("band_front", "south") == {(0, 0)}, \
        "the front band's back is no longer buried in the leggings but for its outboard end"
    # And the two flanks keep only their front column, the 0.15 that reaches past the shell's front
    # wall. Column 0 of `east` is the BACK and column 0 of `west` is the front, which is why the two
    # survivors are not the same index.
    assert seen("band_out", "east") == {(2, 0)}, "the outboard flank is no longer sunk into the shell"
    assert seen("band_in", "west") == {(0, 0)}, "the inboard flank is no longer sunk into the shell"
    # Nothing else on the part is buried at all. The bow lives outboard of the shell's x = 2.4 wall
    # and no cube of this part hides a whole texel of another, so all eight INNER pixels are the
    # shell's - if a cube-in-cube one ever appears, two cubes have been driven into each other.
    grid = [(n, f, i, j)
            for n in CUBES
            for f, (_, _, fw, fh) in faces(CUBES[n][0], CUBES[n][1]).items()
            for j in range(fh) for i in range(fw)]
    shell_inner = {c for c in grid if buried_by_shell(*c)}
    all_inner = {c for c in grid if buried(*c)}
    assert all_inner == shell_inner and len(all_inner) == 8, \
        f"expected 8 INNER pixels, all of them the shell's; got {len(all_inner)} of which " \
        f"{len(all_inner - shell_inner)} are cube-in-cube"
    for name in ("loop_f", "knot", "loop_b", "tail"):
        assert bounds(name)[0][0] > SHELL[1][0], \
            f"{name} has moved inboard of the leggings shell's wall"
    # The strap's 0.35 in / 0.65 out and 0.25 in / 0.75 out, stated as arithmetic so an edit that
    # flattens the band or lifts it off the armour cannot pass quietly.
    assert abs(bounds("band_front")[1][2] - SHELL[0][2] - 0.35) < EPS, \
        "the front band's back no longer sits 0.35 inside the leggings shell"
    assert abs(SHELL[0][2] - bounds("band_front")[0][2] - 0.65) < EPS, \
        "the front band no longer stands 0.65 proud of the leggings shell"
    assert abs(SHELL[1][0] - bounds("band_out")[0][0] - 0.25) < EPS \
        and abs(bounds("band_out")[1][0] - SHELL[1][0] - 0.75) < EPS, \
        "the outboard flank no longer sits 0.25 in and 0.75 out of the leggings shell"
    # The bow's waist: a 0.90 gap between the loops, a knot 1.30 deep lapping 0.20 into each of them,
    # and the knot 0.20 more proud than either. Lose any of the three and the bow reads as a lump.
    assert abs(bounds("loop_b")[0][2] - bounds("loop_f")[1][2] - 0.90) < EPS, \
        "the bow's loops no longer leave a 0.90 gap for the knot"
    assert abs(bounds("loop_f")[1][2] - bounds("knot")[0][2] - 0.20) < EPS \
        and abs(bounds("knot")[1][2] - bounds("loop_b")[0][2] - 0.20) < EPS, \
        "the knot no longer laps 0.20 into each loop"
    assert abs(bounds("knot")[1][0] - bounds("loop_f")[1][0] - 0.20) < EPS, \
        "the knot no longer stands 0.20 proud of the loops"


def check_neighbours() -> None:
    """The four clearances this part's wearability rests on, against the shipped neighbours' hulls.

    A `knees` part is judged by what it does NOT touch, and on this socket the margins are quarters of
    a unit. NEIGHBOURS is a recorded datum - the hulls `trace_geometry.py` prints for the shipped
    tassets, greaves and heel wings - so this is not a dependency on their files, it is a tripwire.
    The one intersection the part has, band_front into lame3, is asserted AS an intersection, because
    it is a choice the enum's own javadoc forces and a later edit that silently "fixed" it would have
    moved the strap off the knee."""
    def gap(name, hull):
        lo, hi = leg(name)
        return max(max(hull[0][a] - hi[a], lo[a] - hull[1][a]) for a in range(3))

    for name, other, want in (("band_out", "tassets:lame3", 0.20),
                              ("loop_b", "heel_wings:vane_upper", 0.30),
                              ("loop_f", "greaves:greave", 0.25),
                              ("tail", "greaves:greave", 0.35)):
        got = gap(name, NEIGHBOURS[other])
        assert abs(got - want) < 0.005, f"{name} now clears {other} by {got:+.3f}, not {want:+.2f}"
    assert gap("band_front", NEIGHBOURS["tassets:lame3"]) < 0, \
        "band_front no longer laps the tassets' third lame - has the strap left the knee?"
    for name in CUBES:
        if name != "band_front":
            assert gap(name, NEIGHBOURS["tassets:lame3"]) > 0, f"{name} has moved into the tassets"


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
        print(f"    {key:18s} {counts[key]:3d} seen")

    # One fitting. Everything that is ribbon - the strap round the knee, both loops, the hanging end -
    # is the inlay and takes a dye; the knot alone keeps whatever metal the smithing table put there.
    # See the docstring on why the knot is left out: a mask over the whole part would be a recolour,
    # not an inlay.
    ribbon = [rect for name in RIBBON for rect in faces(*CUBES[name][:2]).values()]
    write_mask(img, ribbon, OUT.with_name("garters_inlay.png"))


if __name__ == "__main__":
    main()
