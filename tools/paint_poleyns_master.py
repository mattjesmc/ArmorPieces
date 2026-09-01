"""
Paint the grayscale master for the "poleyns" part.

Like the brooch, sash, tassets, spurs, greaves, brush_crest and vambraces painters this does not
merely claim that CUBES matches the shipped geometry, it reads
assets/armorpieces/armorpieces/decoration/poleyns.json at run time and asserts it - and like the
vambraces it asserts the cube ORIGINS as well as their sizes and uv, because on this part the
positions are not decoration: every INNER pixel below is decided by testing a face pixel against the
other cubes and against the leggings shell, so a cube that moved a quarter of a unit would leave the
whole burial mask silently wrong while every other check in the pipeline kept passing. Output goes
to tools/decoration_masters/poleyns.png, which sync_decoration_masters.py installs for the game to
colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

**This master is 100% opaque**, for the circlet's reason rather than the spurs'. The cop is a
one-unit plate and not a closed box, so the argument cannot be the one a deep part gets to use - that
a hole would show the inside of the box under `armorCutoutNoCull` - and the policy has to stand on
its own: a knee cop has no fringe to fray and no fretwork to punch, and the only thing behind the
plate is the leggings shell 0.40 away, so a hole here reads as a hole in the armour rather than as
shaping. Everything is value.

--------------------------------------------------------------------------------------------------
The part, in numbers

`KNEES` is `Attachment.of(LEFT_LEG, 0, 6, -2)` mirrored on the right, so part-local (0, 0, 0) is
leg-local (0, 6, -2) - the leg box's own front face, at the knee. Two frames are quoted throughout:
*part-local* (what the geometry JSON holds) and *leg-local* (part-local + (0, 6, -2)), which is what
`trace_geometry.py` prints. The leg box is leg-local x -2..2, y 0..12, z -2..2; the leggings shell -
the INNER layer at 0.5, not the outer 1.0 the chest parts are used to - is x +-2.5, y -0.5..12.5,
z +-2.5.

    cube     part-local                                    leg-local
    cop      x -0.35..2.65 y -2.30..0.70 z -1.90..-0.90    x -0.35..2.65 y 3.70..6.70 z -3.90..-2.90
    crown    x  0.15..2.15 y -1.80..0.20 z -2.65..-0.65    x  0.15..2.15 y 4.20..6.20 z -4.65..-2.65
    lame     x  0.25..2.25 y  0.10..1.10 z -2.35..-1.35    x  0.25..2.25 y 6.10..7.10 z -4.35..-3.35

Three cubes, one bone, no rotations - the third part in the mod with none, after the greaves and the
vambraces, and for their reason: a knee cop is a dome on a straight box and there was nothing to
cant. It also buys a check the rotated parts cannot have, because `trace_geometry` only tests a cube
for coplanarity with a shell when the whole chain is axis-aligned. It reports none here.

**The cop is a plate, and it stands clear of every shell.** Its back face is at leg-local z = -2.90,
0.40 in front of the leggings shell's front wall at -2.50, so *nothing of this part is buried in the
armour it hangs on*. That 0.40 is the number the whole master turns on: it is a real gap, a low or
side-on camera can see into it, and it is what makes `cop.south` and `crown.south` faces to be
painted rather than INNER fill. The boots shell is the near miss - it is the OUTER layer at 1.0, its
wall is at z = -3.00, and the plate's rearmost 0.10 lies inside it - but its texture up here is
transparent, so it neither occludes this part nor can fight it, and no face of this part lies on it
either way (walls z = -3.00, x = +-3.00; the nearest approach is that 0.10).

**The crown pierces the plate rather than sitting in it.** It is 2 deep against the plate's 1, so it
stands 0.75 proud in front and pokes 0.25 out the back into the gap. That is what leaves the boss
wholly visible: no one-unit texel of any of its faces is *entirely* inside a plate only one unit
thick and offset from it by a quarter, so the mask paints all twenty-four of the crown's pixels and
the shading has to say where the plate crosses them instead. The crossing is a step and is painted as
one - `SUNK` on the flanks and on the top.

**What the depth no longer does is clear the tassets.** The tassets' third lame dives to leg-local
z = -4.68 across y 3.39..6.82, which is exactly this part's band, and the plate's face is at -3.90 -
behind it. Sampled against the tassets' true rotated solids rather than the hulls `trace_geometry`
prints, 73% of the cop, 83% of the crown and 34% of the lame lie inside the tassets' lames; only the
crown's face, at -4.65, comes within 0.03 of the tassets' frontmost point. Both parts ride LEFT_LEG,
so the interpenetration is rigid - it cannot open on a stride, and it shares no plane with anything -
but a player wearing both sockets sees mostly tasset. That is a property of the two shipped parts and
not something a texture can paint around, which is exactly why the burial mask does not try.

**The greaves are cleared outright.** The lame's underside is at leg-local y = 7.10 against the
greave plate's top at 7.20 and its ribs at 7.45 - 0.10 and 0.35 of clearance in y - and in z the
lame's back at -3.35 stands 0.60 in front of the greave plate's front wall at -2.75 and 0.25 in front
of the ribs' at -3.10. Nothing outside the part sets the lame's depth any more: it stands 0.45 proud
of the plate's face and hangs 0.40 below its lower edge, and the greave is clear of it in both axes
at once.

--------------------------------------------------------------------------------------------------
Burial is computed, not eyeballed

The tassets note in PLAN.md is the method: sample each face at its pixel footprint, push 0.05 along
the face normal, and test containment against the boxes that could hide it. This painter does that
for every pixel of all eighteen faces, against the other two cubes and against the leggings shell,
and paints INNER wherever the *whole* pixel is covered. Partly-covered pixels are painted as visible,
which is the safe direction: a visible pixel painted dark is a mistake you can see, a buried pixel
painted bright is not.

**The shell finds nothing**, because the plate stands 0.40 in front of it, and `check_mask` asserts
that rather than leaving it as dead code - if the part is ever pushed back onto the leg the mask has
to start biting again and the assertion is what will say so. All three INNER pixels this master has
are cube-in-cube: the centre of the plate's face and the centre of its back, both taken by the boss
driven through them, and the inboard pixel of the lame's top, which is under the boss's lower edge.
Three out of sixty-four - a plate standing off a leg has very little of itself to hide.

The occluder list is deliberately short. The boots shell is excluded for the reason above. The
tassets and the greaves are excluded because they are *optional* - a socket holds one part and a
player may wear neither - and a mask that assumed them would black out almost the whole of this part
for anyone wearing a poleyn on its own. That exclusion costs more than it used to, now that the
tassets swallow three quarters of the cop, and it is still the right policy: a master is painted for
the part, not for one combination of parts. Everything the mask does find is permanent, because the
leggings shell rides LEFT_LEG exactly as this part does - so unlike the tassets, which had to paint
one row as flank because the torso shell rides a different bone, there is no row here that uncovers
on a stride.

--------------------------------------------------------------------------------------------------
Faces and their directions

Blockbench's face names, which are the ones the flip gives: bb = (-geo_x, 24 - geo_y, geo_z), so
`west` is the geo +x face - outboard on both legs after the layer's scale(-1, 1, 1) - and `east` is
the one facing the other knee. One master serves both legs because of it, and the lit-outboard /
shadowed-inboard split survives the mirror; it has to be painted rather than left to the engine,
because vanilla's diffuse term shades +x and -x identically, as it does +z and -z.

The face rectangles come from paint_circlet_master.faces(), copied verbatim: row one (v .. v+d) holds
up then down, each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west, south
with widths d, w, d, w. Orientation inside each rectangle is PLAN.md's measured table:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x (inboard)    max z (back)
    down            +y  (underside)      min x (inboard)    max z (back)
    west            +x  (outboard)       min z (front)      min y (top)
    east            -x  (inboard)        max z (back)       min y (top)
    north           -z  (front)          min x (inboard)    min y (top)
    south           +z  (back)           max x (outboard)   min y (top)

The plate being one unit deep collapses four of its six rectangles to a single row or column: its
top, underside and both flanks are 3 x 1 or 1 x 3, so the front-to-back falloff that used to run
across them has nowhere left to live and `ZFALL` is spent on the crown instead, the only cube here
with two units of depth.

--------------------------------------------------------------------------------------------------
The palette, and which faces are actually seen

The wing roots' warning applies: these constants do not transfer between parts by name, they mean "a
face that is seen" and "a face that is not". On a knee the hero face is `north` - the front of the
leg, square on to a camera at eye level - and `west` is the profile, which is the angle one player
looks at another's legs from. `up` matters more here than it did on the shin: it is what a player
sees of their own knee looking down, and it is the ledge the cuisse's lames cross. `east` looks
inboard across 0.95 units of air at the other leg's leggings shell, and 3.10 at the other knee's own
cop, so it is a face in shadow rather than a face that is hidden.

`south` is the face this shape creates. The plate's back and the boss's 0.25 stub both stand in the
0.40 crevice in front of the leggings, lit by nothing and seen only by a camera low enough or
side-on enough to look into the gap - so they are painted at `CREVICE`, above INNER and well below
anything on the front. Thirteen of the sixty-four pixels go on those two faces; that is what box UV
costs on a plate whose back is not buried.

Values run 38..243. Of the 64 painted pixels 61 survive the burial mask and 3 are INNER; 41 of them
sit below 127, which is the circlet's lesson - the material ramp interpolates dark -> mid over 0..127
and mid -> light over 128..255, so a master that never dips below the middle only ever uses half of
every material's ramp. This part leans dark, because a plate standing off a leg turns three of its
six aspects back towards the leg.

The dome is *painted*, not modelled, and that is the greaves' finding arriving one bone up: vanilla's
diffuse term shades by normal alone, so the crown standing 0.75 proud of the plate is lit exactly as
the plate is and is invisible head on except as what this file puts on it. The modelled cube buys the
profile and the three-quarter silhouette; the roundness is the 2x2 falloff on `crown.north` against a
ring 56 values below it. Contrast placed *outward* like that is the rowel's lesson - at this size a
detail is a value against its neighbour, and when every neighbour is also a detail none of them is
one.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "poleyns.json"
OUT = ROOT / "tools" / "decoration_masters" / "poleyns.png"

TEX_W, TEX_H = 64, 32

# size (w, h, d), uv (u, v) and pivot-relative origin, mirroring poleyns.json in that file's own
# order. The single bone sits at the anchor with no rotation, so origin IS the part-local corner.
#   cop   - the plate over the kneecap. 1 deep, and its back face at part-local z = -0.90 stands
#           0.40 in front of the leggings shell, so none of it is buried in the armour.
#   crown - the domed boss, 2 deep against the plate's 1: it stands 0.75 proud in front and pokes
#           0.25 out the back, piercing the plate rather than sitting in it.
#   lame  - the lower lame, 0.45 proud of the plate's face, hanging 0.40 below its lower edge and
#           clearing the greave plate by 0.10 in y and 0.60 in z.
CUBES = {
    "cop":   ((3, 3, 1), (2, 2),  (-0.35, -2.30, -1.90)),
    "crown": ((2, 2, 2), (12, 0), (0.15, -1.80, -2.65)),
    "lame":  ((2, 1, 1), (20, 0), (0.25, 0.10, -2.35)),
}

# The leggings shell over this leg, in part-local coordinates (leg-local x +-2.5, y -0.5..12.5,
# z +-2.5 shifted by the anchor at (0, 6, -2)). It is the INNER armor layer at 0.5 inflate, it is
# always worn when this part draws, and it rides the same bone - so anything inside it would be
# buried permanently. Nothing is: the whole part sits in front of z = -0.5, and check_mask asserts
# it, so the day the part is pushed back onto the leg this file will say so. The boots shell is NOT
# in this list; see the docstring.
SHELL = ((-2.5, -6.5, -0.5), (2.5, 6.5, 4.5))

PUSH = 0.05      # how far off a face a sample sits before it is tested for containment
EPS = 1e-9

random.seed(71)  # deterministic output - regenerating must not churn the PNG

UP = 242        # the plate's top: the face a player sees of their own knee, and the lit one
CROWN = 238     # the boss's own front - the brightest thing on the part
FLANK = 210     # `west`, geo +x: the profile
LAMEFACE = 198  # `north` on the lower lame, which stands 0.45 proud of the plate's face
FACE = 182      # `north` on the plate: the rim ringing the boss
GUTTER = 100    # the plate's face where the boss's shadow and the lame's top edge both cross it
IN = 84         # `east`, geo -x: the inboard flank, across 0.95 of air to the other leg's shell
SUNK = 64       # a texel three quarters of the way inside the plate: the shadow at the boss's root
CREVICE = 60    # a back face standing in the 0.40 gap in front of the leggings shell
INNER = 42      # buried - wholly inside another cube of the part, or inside the leggings shell
DOWN = 36       # a free underside

RIM = 20        # the lit chamfer along a free top edge
FALL = 24       # top-to-bottom falloff down a standing face
ZFALL = 26      # front-to-back falloff across the crown, the only cube still 2 deep
XGAIN = 22      # inboard-to-outboard brightening across a face's width
LAP = 46        # the shadow row where one cube emerges from under another
LIP = 20        # a free lower edge catching light off its own roll, on the lame's underside
RIVET = 56      # a rim rivet: against a dropped row, not against the field


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


def bounds(name):
    """A cube's part-local (lo, hi) corners."""
    size, _, origin = CUBES[name]
    return tuple(origin), tuple(origin[a] + size[a] for a in range(3))


def cell(name, face, i, j):
    """The part-local footprint of one face pixel, already pushed 0.05 off the face.

    The two in-plane axes span the pixel's whole unit square rather than just its centre, so a pixel
    only counts as buried when *all* of it is - see the docstring. The normal axis is a single value,
    which is what makes the test "is this sample inside that box" rather than "do these boxes touch".
    """
    lo, hi = bounds(name)
    if face == "up":                       # col 0 = min x, row 0 = max z, normal -y
        return ((lo[0] + i, lo[1] - PUSH, hi[2] - j - 1), (lo[0] + i + 1, lo[1] - PUSH, hi[2] - j))
    if face == "down":                     # col 0 = min x, row 0 = max z, normal +y
        return ((lo[0] + i, hi[1] + PUSH, hi[2] - j - 1), (lo[0] + i + 1, hi[1] + PUSH, hi[2] - j))
    if face == "east":                     # col 0 = max z, row 0 = min y, normal -x
        return ((lo[0] - PUSH, lo[1] + j, hi[2] - i - 1), (lo[0] - PUSH, lo[1] + j + 1, hi[2] - i))
    if face == "west":                     # col 0 = min z, row 0 = min y, normal +x
        return ((hi[0] + PUSH, lo[1] + j, lo[2] + i), (hi[0] + PUSH, lo[1] + j + 1, lo[2] + i + 1))
    if face == "north":                    # col 0 = min x, row 0 = min y, normal -z
        return ((lo[0] + i, lo[1] + j, lo[2] - PUSH), (lo[0] + i + 1, lo[1] + j + 1, lo[2] - PUSH))
    if face == "south":                    # col 0 = max x, row 0 = min y, normal +z
        return ((hi[0] - i - 1, lo[1] + j, hi[2] + PUSH), (hi[0] - i, lo[1] + j + 1, hi[2] + PUSH))
    raise KeyError(face)


def inside(box, clo, chi) -> bool:
    """True when the whole of a face pixel's footprint lies inside one box."""
    blo, bhi = box
    return all(blo[a] - EPS <= clo[a] and chi[a] <= bhi[a] + EPS for a in range(3))


def buried_by_shell(name, face, i, j) -> bool:
    """True when this face pixel is wholly inside the leggings shell. Nothing is, on this geometry;
    check_mask asserts it, so a part pushed back onto the leg cannot slip past unnoticed."""
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
# the cop - the plate itself


def cop_north(i, j, fw, fh):
    """The front of the knee, 3 wide x 3 tall, column 0 inboard and row 0 the top.

    The boss covers the middle of this 3 x 3 and only the centre pixel entirely, so what is left is a
    ring of eight pixels, each of them a rim of plate showing round the dome. Painting it as a ring
    rather than as a field is what the geometry forces: a 2-wide boss cannot be centred on a 3-wide
    host - the greaves' "an odd rib wants an odd host" met from the other side - so no column here is
    cleanly beside the dome and every one of them is partly under it.

    Row 0 is the chamfer where the plate leaves the thigh and carries a rivet at each end, dropped
    below the field first, because the brooch found that a one-pixel bolt only reads if what
    surrounds it is plainly darker. Row 2 is doubly shadowed: the dome throws down onto it, and the
    lame, standing 0.45 in front of the plate, crosses the lower 0.60 of it."""
    if j == 0:
        return (FACE - 52 + RIVET) if i in (0, fw - 1) else (FACE - 52 + RIM)
    if j == fh - 1:
        return GUTTER + round(10 * ramp(i, fw))
    return FACE - 20 + round(XGAIN * ramp(i, fw))


def cop_west(i, j, fw, fh):
    """The outboard flank, one column deep and 3 tall - the plate's whole profile, and the reason the
    part reads from the side at all. There is no depth left to fall off across, so the only gradient
    is down: a lit chamfer on the top row and `FALL` under it. The column shows in full because the
    plate hangs 0.15 past the leggings shell's outer wall at x = 2.5 - the same trick, and nearly the
    same small number, that keeps the greaves' flank alive at 0.35."""
    if j == 0:
        return FLANK + RIM
    return FLANK - round(FALL * ramp(j, fh))


def cop_east(i, j, fw, fh):
    """The inboard flank, one column and 3 tall, looking across 0.95 of air at the other leg's
    leggings shell. Nothing covers it - the plate stands in front of its own shell - so it is painted
    as the dimmest standing face on the part rather than as filler, falling off downward the way the
    outboard flank does but from `IN` instead of from `FLANK`."""
    return IN - round(FALL * ramp(j, fh))


def cop_up(i, j, fw, fh):
    """The top of the plate, 3 wide and one row deep: a narrow ledge, wholly free of the shell, and
    the one the cuisse's lames cross on their way down the thigh. It is the brightest thing on the
    part after the boss, brightening outboard the way every top face here does."""
    return UP - round(18 * (1.0 - ramp(i, fw)))


def cop_down(i, j, fw, fh):
    """The underside, 3 wide and one row deep. What shows of it is the sliver in the seam above the
    greave, so it is graded outboard rather than left flat."""
    return DOWN + round(10 * ramp(i, fw))


def cop_south(i, j, fw, fh):
    """The plate's back, 3 x 3, column 0 outboard and row 0 the top - a face that only needs painting
    because the plate stands 0.40 clear of the leggings. It is seen through that gap, by a camera low
    or side-on enough to look into it, so it is `CREVICE` rather than INNER: dark enough to read as
    the shadowed side of a plate, light enough not to look like a hole. The outboard column carries
    the most of what light gets in there, because it is the one hanging 0.15 past the shell's wall
    where the gap is open rather than roofed. The centre pixel is the boss coming through, and the
    mask takes it."""
    lum = CREVICE - round(6 * ramp(j, fh))
    return lum + 14 if i == 0 else lum - round(10 * ramp(i, fw))


# ------------------------------------------------------------------------------------------------
# the crown - the dome


def crown_north(i, j, fw, fh):
    """The dome, 2 x 2, and the whole reason this part reads as a cop rather than as a plate. Vanilla
    lights it exactly as it lights the ring behind it, so the roundness is entirely here: a
    top-outboard highlight falling away to the bottom-inboard corner, over a ring 56 values darker."""
    return CROWN - round(16 * (1.0 - ramp(i, fw))) - round(26 * ramp(j, fh))


def crown_west(i, j, fw, fh):
    """The dome's outboard flank, column 0 the front. The boss is 2 deep against a 1-deep plate, so
    neither column is *wholly* inside the plate and both are painted - but column 0 is only a quarter
    covered and column 1 is three quarters, so the plate's edge crosses this face as a step and is
    painted as one. Painted against crown_east so the boss has a direction: vanilla shades +x and -x
    identically, so a boss that is not painted round is a step of the wrong kind."""
    if i == fw - 1:
        return SUNK + 6 - round(6 * ramp(j, fh))
    return CROWN - 22 - round(ZFALL * ramp(i, fw)) - round(FALL * ramp(j, fh))


def crown_east(i, j, fw, fh):
    """The dome's inboard flank; column 0 is the BACK here, so it is column 0 that the plate takes
    three quarters of and column 1 that stands out in front of it."""
    if i == 0:
        return SUNK - 8 - round(6 * ramp(j, fh))
    return IN + 22 - round(FALL * ramp(j, fh))


def crown_up(i, j, fw, fh):
    """The boss's shoulder, 2 wide x 2 deep, rows running BACK to front. Row 0 is the three quarters
    of it that lies inside the plate; row 1 is the 0.75 standing out in front - the biggest step on
    the master, and the one that tells a camera looking down that the boss is a boss."""
    if j == 0:
        return SUNK + 12 + round(10 * ramp(i, fw))
    return UP - 8 - round(20 * (1.0 - ramp(i, fw)))


def crown_down(i, j, fw, fh):
    """The boss's underside, rows back to front. Neither row is free of the plate the way the front
    row of the top is, so the two sit only a few values apart - an underside is dark before anything
    else is done to it."""
    return DOWN + (10 if j == 0 else 22)


def crown_south(i, j, fw, fh):
    """The 0.25 stub the boss pokes out of the back of the plate, standing 0.15 from the leggings
    shell - the deepest-set face on the part, and the only one with armour that close behind it."""
    return CREVICE + (8 if i == 0 else 0) - round(8 * ramp(j, fh))


# ------------------------------------------------------------------------------------------------
# the lower lame


def lame_north(i, j, fw, fh):
    """The lame's face, 2 x 1. It stands 0.45 proud of the plate and hangs 0.40 below it, crossing
    the plate's bottom row - so from the front it is the band that separates the cop from the shin,
    and it is the one thing on this part that says poleyn rather than knee disc."""
    return LAMEFACE + round(XGAIN * ramp(i, fw))


def lame_west(i, j, fw, fh):
    return FLANK - 14


def lame_east(i, j, fw, fh):
    return IN + 10


def lame_up(i, j, fw, fh):
    """The lap: where the lame emerges from under the boss, whose lower edge overhangs its top by
    0.10. Dropped below the flank the way the vambraces' rim is under its cannon, because that shadow
    line is what makes two plates read as two. The inboard pixel is wholly under the boss and the
    mask takes it; this paints the outboard one, which the boss misses by 0.10 in x."""
    return FLANK - LAP


def lame_down(i, j, fw, fh):
    """The lowest face of the whole part, and the only free underside it has - what a camera below
    the knee sees, and what closes the 0.10 seam over the greave plate."""
    return DOWN + LIP - 10


def lame_south(i, j, fw, fh):
    """The lame's back. Its upper 0.60 is inside the plate and its lower 0.40 hangs below it, facing
    the leg across the same crevice the plate's own back stands in - so it is painted at `CREVICE`, a
    little above the plate because it is the nearer of the two to a camera looking UP at the knee."""
    return CREVICE + 6


PAINTERS = {
    ("cop", "north"): cop_north, ("cop", "west"): cop_west, ("cop", "east"): cop_east,
    ("cop", "up"): cop_up, ("cop", "down"): cop_down, ("cop", "south"): cop_south,
    ("crown", "north"): crown_north, ("crown", "west"): crown_west, ("crown", "east"): crown_east,
    ("crown", "up"): crown_up, ("crown", "down"): crown_down, ("crown", "south"): crown_south,
    ("lame", "north"): lame_north, ("lame", "west"): lame_west, ("lame", "east"): lame_east,
    ("lame", "up"): lame_up, ("lame", "down"): lame_down, ("lame", "south"): lame_south,
}


def check_geometry() -> None:
    """CUBES must be the shipped geometry, in order: sizes, uv AND pivot-relative origins.

    Painting a texture for a shape the model no longer has is invisible to every other check in this
    pipeline - `bb_geo roundtrip` checks the model against itself and check_layout() checks the
    master against itself, and both keep passing while the rectangles slide off the faces they were
    drawn for. The origins are asserted as well as the sizes because this painter's burial mask is
    computed from them: a cube nudged a quarter of a unit would leave every INNER pixel below wrong
    with nothing else in the mod noticing."""
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
    found = [(tuple(c["size"]), tuple(c["uv"]), tuple(float(v) for v in c["origin"]))
             for c in bone["cubes"]]
    want = [(size, uv, tuple(float(v) for v in origin)) for size, uv, origin in CUBES.values()]
    assert found == want, f"CUBES disagrees with {GEO.name}: {found} vs {want}"


def check_planes() -> None:
    """No two cubes of this part may share a plane, whichever way the two faces point.

    The sash's rule, and it needs stating on a part built as three lapped plates: a crown driven
    through a plate and a lame hung under it are exactly the shape where "flush" looks like the tidy
    option in the outliner. Coincident faces z-fight when they face the same way too, and there is no
    bone rotation here that could separate them afterwards."""
    for axis, label in enumerate("xyz"):
        planes = {}
        for name in CUBES:
            lo, hi = bounds(name)
            for v in (lo[axis], hi[axis]):
                assert v not in planes, f"{name} and {planes[v]} share the plane {label} = {v:g}"
                planes[v] = name


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

    Each one is a geometric claim made in the docstring above, and each would break silently if a
    cube moved: the mask would still be *a* mask and the render would still be *a* render."""
    # The part stands entirely in front of the leggings shell, so the shell buries nothing at all and
    # every INNER pixel here is cube-in-cube. This is the load-bearing one: it is what makes
    # cop_south and crown_south faces to be painted rather than INNER fill, and if the part is ever
    # pushed back onto the leg those two routines would be painting a wall.
    for name in CUBES:
        for face, (_, _, fw, fh) in faces(CUBES[name][0], CUBES[name][1]).items():
            for j in range(fh):
                for i in range(fw):
                    assert not buried_by_shell(name, face, i, j), \
                        f"{name}.{face} at {(i, j)} is inside the leggings shell; the part has moved back"
    # The crown covers the middle of the plate's front and covers exactly one pixel of it entirely: a
    # 2-wide boss on a 3-wide host cannot do better, which is why cop_north paints a ring.
    assert seen("cop", "north") == {(i, j) for j in range(3) for i in range(3)} - {(1, 1)}, \
        "the boss no longer covers exactly the centre pixel of the plate's face"
    # And the boss comes out the back, so the plate's back cap is the same ring seen from behind -
    # which is why cop_south is a painted face and not a flat INNER fill.
    assert seen("cop", "south") == {(i, j) for j in range(3) for i in range(3)} - {(1, 1)}, \
        "the plate's back is no longer a ring round the boss's stub"
    # One unit of depth: the plate's top, underside and both flanks are single rows or columns, and
    # nothing covers any of them. A face that lost pixels here would mean the plate had been buried.
    for face in ("up", "down", "east", "west"):
        assert len(seen("cop", face)) == 3, f"the plate's {face} is no longer a free 3-pixel strip"
    # The boss is 2 deep against a 1-deep plate offset a quarter of a unit from it, so no texel of
    # any of its faces is wholly inside the plate and all twenty-four are painted. crown_west,
    # crown_east and crown_up carry the step where the plate's edge crosses them instead.
    for face in ("up", "down", "east", "north", "west", "south"):
        assert len(seen("crown", face)) == 4, \
            f"the crown's {face} is no longer wholly exposed; the plate must have thickened"
    # The boss's lower edge overhangs the lame's top by 0.10, and its x covers all but the outboard
    # 0.10 of it - so exactly the inboard pixel of the lame's top is buried.
    assert seen("lame", "up") == {(1, 0)}, "the lame no longer laps up under the boss"


def main() -> None:
    check_geometry()
    check_planes()
    claimed = check_layout()
    check_mask()

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
        print(f"    {key:12s} {counts[key]:3d} seen")


if __name__ == "__main__":
    main()
