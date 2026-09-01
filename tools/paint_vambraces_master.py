"""
Paint the grayscale master for the "vambraces" part.

Like the brooch, sash, tassets, spurs, greaves and brush_crest painters this does not merely claim
that CUBES matches the shipped geometry, it reads
assets/armorpieces/armorpieces/decoration/vambraces.json at run time and asserts it - and like
brush_crest it asserts the cube ORIGINS as well as their sizes and uv, because on this part the
positions are not decoration: every INNER pixel below is decided by testing a face pixel against the
other cubes and against the chestplate sleeve, so a cube that moved half a unit would leave the whole
burial mask silently wrong while every other check in the pipeline kept passing. Output goes to
tools/decoration_masters/vambraces.png, which sync_decoration_masters.py installs for the game to
colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

**This master is 100% opaque.** The feathering and the spurs carve their silhouettes out of alpha
because a plume is a fringe and a rowel is a wheel of air; this is the circlet's case instead. A
bracer is a solid wrap of plate, it has no fringe to fray, and parts draw with `armorCutoutNoCull`,
so a hole punched in the cannon would show the *inside* of the cannon rather than the arm behind it.
Everything here is value.

--------------------------------------------------------------------------------------------------
The part, in numbers

`VAMBRACES` is `Attachment.of(LEFT_ARM, 1, 6, 0)` mirrored on the right, so part-local (0, 0, 0) is
arm-local (1, 6, 0) - the arm box's own X centre, at forearm height. Two frames are quoted
throughout: *part-local* (what the geometry JSON holds) and *arm-local* (part-local + (1, 6, 0),
which is what `trace_geometry.py` prints). The arm box is arm-local x -1..3, y -2..10, z -2..2; the
chestplate's 1.0-inflate sleeve, which is the only shell over this bone and is always worn when this
part draws, is x -2..4, y -3..11, z -3..3.

    cube       part-local                                    arm-local
    cannon     x -0.50..3.50  y -2.0..3.0  z -3.50.. 3.50    x 0.50..4.50  y 4.0..9.0   z +-3.50
    rib_front  x  2.00..4.00  y -1.5..2.5  z -2.50..-1.50    x 3.00..5.00  y 4.5..8.5   z -2.50..-1.50
    rib_back   x  2.00..4.00  y -1.5..2.5  z  1.50.. 2.50    x 3.00..5.00  y 4.5..8.5   z  1.50.. 2.50
    rim        x -0.25..3.75  y  2.0..4.0  z -4.00.. 4.00    x 0.75..4.75  y 8.0..10.0  z +-4.00

Four cubes, one bone, no rotations - the second part in the mod with none, after the greaves, and
for the greaves' reason: a forearm is a straight box and there was nothing to cant.

**The sleeve is the thing this part has to beat, not the arm.** A vambraces decoration only ever
draws with a chestplate on, and the chestplate's arm sleeve is a 6x6 section running the whole length
of the limb. Anything inside x -3..3, z -3..3 part-local is swallowed by it and invisible, so the
minimum visible bracer is one that stands proud of a 6x6 tube. The cannon clears it by 0.5 outboard
and 0.5 front and back; the rim by 0.75 and 1.0; the ribs by 1.0 outboard and not at all front or
back - they sit well inside the sleeve's z, and everything they do to the outline they do in x.
Nothing here has margin to spare: the cannon's half unit is the whole reason its flank is a face a
player can see, and the ribs' own half unit on top of it is the whole reason they are in the
silhouette rather than only in the paint.

**One inequality disposes of the whole body.** Every cube here sits at arm-local x >= 0.5, which is
world x >= 5.5 on the left arm. The widest *shell* on the figure that does not ride the arm bone is
the chestplate's torso shell and the helmet, both at world x = 5.0 (the boots shell reaches 4.9, the
leggings 4.4). Every rotation on this body - arm swing, leg swing, body pitch - is about X, and X is
preserved, so the vambrace is clear of the torso, the head and both legs by at least half a unit at
*every* pose, with no swept envelope to compute. That is the wing roots' "clearances that need no
swing analysis at all" arriving as the whole design rather than as a footnote, and it is why this
part could be a wrap at all: the spaulders' first cut failed because it buried itself in a bone that
does not move with it, and nothing here is buried in anything but the sleeve, which rides this bone.

Shells are not the only things out there, and half a unit is not much room for the rest. The sash's
belt bands end at world x 5.5, the plane the cannon's inboard face stands on, and its side bar, knot
and tail all reach past it: the cannon runs 0.5 into the bar, 1.75 into the knot and 1.5 into the
tail, and the rim 0.25, 1.5 and 1.25. Those are decorations on the *body* bone, so they swing away
from this one and no arithmetic in this frame settles them - `trace_geometry.py` is bone-scoped and
does not see the pair at all. What matters to this file is that none of it changes what is buried:
the mask below tests against the sleeve and against this part's own cubes, both of which ride
LEFT_ARM, and a body-bone neighbour that is flush at rest is somewhere else entirely on a stride.

The price of the wrap is that it is open on the inboard side: the cannon covers arm-local x 0.5..4.5
of a sleeve spanning -2..4, so two and a half units of bare sleeve show inboard of it. That strip is
inside the torso at rest and behind the arm at every other pose, which is the same trade the
spaulders made when their cap stopped half a unit short of the chest wall.

**The rim ends at the wrist, not past it.** Its underside is at arm-local y = 10, the arm box's own
bottom cap, which leaves the sleeve's last unit (y 10..11) showing below the bracer as the hand. The
two coincident faces there are both inside the sleeve, so `trace_geometry` prints it as a note rather
than a COPLANAR and it cannot be seen fighting. The ribs' inboard faces sit on arm-local x = 3, the
arm box's own outboard wall, and print as the same kind of note for the same reason - that face is
1.5 units deep inside the cannon, never mind the sleeve.

**The only planes shared on this part are the twin ribs' own.** cannon x {-0.5, 3.5}, ribs x {2, 4},
rim x {-0.25, 3.75}; cannon y {-2, 3}, ribs y {-1.5, 2.5}, rim y {2, 4}; cannon z {+-3.5}, rib_front
z {-2.5, -1.5}, rib_back z {1.5, 2.5}, rim z {+-4}. Twenty-four faces on twenty distinct planes: the
four repeats are the two ribs agreeing on x and on y, which a mirrored pair cannot avoid and which
costs nothing, because they stand three units apart in z and so no two of those faces overlap by a
single unit of area. That is the sash's rule stated the way it actually reads - a shared plane is
only a fight where the faces meet - and it needs stating on a part like this because a rim and a cuff
that agree on a face look like the tidy option in the outliner.

--------------------------------------------------------------------------------------------------
Why the ribs are modelled cubes and not just paint

The greaves' finding is that a raised face parallel to the face behind it is invisible head on -
vanilla's diffuse term shades by normal alone, so a spine standing proud of a plate is lit exactly as
the plate is. It holds here too: from directly outboard the ribs and the cannon's flank are one
uniform slab, and the ribs exist in that view only as whatever this file paints. What the modelled
cubes buy is the front and three-quarter silhouette, where they break the cannon's outline by half a
unit, and the four flank faces of their own - and, because there are two of them, a channel between
them with a real depth in the silhouette rather than a painted one.

What they buy the *painter* is the thing the greaves could not have. "An odd rib wants an odd host":
the greaves' plate is four texels wide, so its one-wide spine straddled the boundary between columns
1 and 2 and both had to be painted as shadow. The cannon's outboard face is **seven** texels deep and
starts on a half unit, so the ribs land on columns 1 and 5 exactly, symmetric about column 3. The
five-band read the greaves had to fake is a seven-band read here by construction - land, rib, gutter,
crown, gutter, rib, land - with the crown the single centre column that an odd host leaves standing.

The rim is the counter-example, and it is worth having one. Its flank is eight texels deep and starts
at z = -4, an integer, so the ribs' half-unit feet straddle its columns 1/2 and 5/6 instead of
landing on them. There is no honest way to paint them there, so the rim is painted as one unbroken
roll and the ribs' last half unit reads on it by silhouette alone - which it can, because they stand
0.25 proud of the rim's own flank as well as 0.5 proud of the cannon's.

--------------------------------------------------------------------------------------------------
Burial is computed, not eyeballed

The tassets note in PLAN.md is the method: sample each face at its pixel footprint, push 0.05 along
the face normal, and test containment against the boxes that could hide it. This painter does that
for every pixel of all twenty-four faces, against the other three cubes and against the chestplate
sleeve, and paints INNER wherever the *whole* pixel is covered. Partly-covered pixels are painted as
visible, which is the safe direction: a visible pixel painted dark is a mistake you can see, a buried
pixel painted bright is not.

Two of the pixels that survive that way are worth naming, because both are half-covered rather than
free. The ribs are inset half a unit from the cannon's top edge, so the top row of columns 1 and 5 on
the cannon's flank is half rib and half chamfer and is painted as chamfer; and the ribs' undersides
overhang the rim by a quarter unit, so the one texel of each that survives is a quarter air and three
quarters rim and is painted as free plate. Both are the rule working, not exceptions to it.

Everything the mask finds is permanent. The sleeve rides LEFT_ARM exactly as this part does, so
unlike the tassets - which had to paint one row as flank because the torso shell rides a different
bone - there is no row here that uncovers on a stride.

--------------------------------------------------------------------------------------------------
Faces and their directions

Blockbench's face names, which are the ones the flip gives: bb = (-geo_x, 24 - geo_y, geo_z), so
`west` is the geo +x face - outboard on both arms after the layer's scale(-1, 1, 1) - and `east` is
the one against the body. One master serves both forearms because of it, and the lit-outboard /
shadowed-inboard split survives the mirror. The front/back split survives it too, untouched, since
the flip is in x alone.

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

`south` counting outboard-to-inboard while `north` counts inboard-to-outboard is what makes the two
gradients mirror images in the file; run them the same way and the bracer is lit from the left on one
face and from the right on the other. It is also why the twin ribs need four flank painters and not
two: rib_front's `north` and rib_back's `south` look out of the part, while rib_front's `south` and
rib_back's `north` look at each other across the channel.

--------------------------------------------------------------------------------------------------
The palette, and which faces are actually seen

The wing roots' warning applies: these constants do not transfer between parts by name, they mean
"a face that is seen" and "a face that is not". On a forearm three faces are seen and they are seen
about equally often - `west` in profile, which is how one player looks at another; `north` head on;
`south` in third person, which is how a player looks at their own character. So `south` is not the
5-pixel sliver it was on the shoulder and is not painted as one. `east` is never seen at all bar the
half-unit that clears the sleeve at the very front and back edges.

Values run 35..251. Of the 334 painted pixels 173 survive the burial mask, and 54 of those - just
under a third - sit below 127, with the buried 161 sitting at INNER below it as well. That is the
circlet's lesson: the material ramp interpolates dark -> mid over 0..127 and mid -> light over
128..255, so a master that never dips below the middle only ever uses half of every material's ramp.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "vambraces.json"
OUT = ROOT / "tools" / "decoration_masters" / "vambraces.png"

TEX_W, TEX_H = 64, 32

# size (w, h, d), uv (u, v) and pivot-relative origin, mirroring vambraces.json in that file's own
# order. The single bone sits at the anchor with no rotation, so origin IS the part-local corner.
#   cannon    - the tube of plate over the forearm, 0.5 proud of the sleeve outboard and 0.5 front
#               and back, open on the inboard side where nothing can see it.
#   rib_front - the forward of the two raised ribs down the outboard face, 0.5 proud of the cannon,
#               inset half a unit from its top edge and running down into the rim.
#   rib_back  - its twin across the channel, three units aft and identical in every other number.
#   rim       - the rolled rim at the wrist, 0.25 proud of the cannon outboard and 0.5 front and
#               back, with one of its two units buried up inside the cannon.
CUBES = {
    "cannon":    ((4, 5, 7), (0, 0),  (-0.5, -2.0, -3.5)),
    "rib_front": ((2, 4, 1), (22, 0), (2.0, -1.5, -2.5)),
    "rib_back":  ((2, 4, 1), (28, 0), (2.0, -1.5, 1.5)),
    "rim":       ((4, 2, 8), (34, 0), (-0.25, 2.0, -4.0)),
}

# The chestplate's 1.0-inflate arm sleeve in part-local coordinates (arm-local x -2..4, y -3..11,
# z -3..3 shifted by the anchor at (1, 6, 0)). It is the only shell over this bone, it is always worn
# when this part draws, and it rides the same bone - so anything inside it is buried permanently.
SLEEVE = ((-3.0, -9.0, -3.0), (3.0, 5.0, 3.0))

PUSH = 0.05      # how far off a face a sample sits before it is tested for containment
EPS = 1e-9

random.seed(67)  # deterministic output - regenerating must not churn the PNG

UP = 244        # a top edge that clears the sleeve
RIDGE = 236     # a rib's own outboard face - the brightest thing in the profile view
FLANK = 214     # `west`, geo +x: the hero face
FRONT = 188     # `north`, geo -z
BACK = 168      # `south`, geo +z - third person is a real angle, not a throwaway
STRAP = 138     # the band where the retaining strap crosses a side face
CHANNEL = 124   # a rib flank that faces into the channel instead of out of the part
GUTTER = 106    # the channel floor either side of a rib: the rib's shadow
IN = 76         # `east`, geo -x: the half unit of inboard face that clears the sleeve
INNER = 46      # buried - in the sleeve, in another cube of the part, or behind the rim
DOWN = 38       # a free underside

RIM = 20        # the lit chamfer along a free top edge
FALL = 22       # top-to-bottom falloff down a standing face
ZFALL = 26      # front-to-back falloff across a face's depth
XGAIN = 20      # inboard-to-outboard brightening across a face's width
LAP = 50        # the shadow row where the rim emerges from under the cannon
LIP = 22        # the free lower edge of the rim, catching light off its own roll
RIVET = 84      # a strap rivet: +84 against the dropped strap row, not +30 against the field

STRAP_ROW = 1     # the same y band (part-local y -1..0) on all four of the cannon's side faces
RIBS = (1, 5)     # the two columns of the cannon's flank the ribs stand on
GUTTERS = (2, 4)  # the columns of channel floor immediately inboard of each rib in z


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


def buried(name, face, i, j) -> bool:
    """True when the whole of this face pixel is inside the sleeve or inside another cube."""
    clo, chi = cell(name, face, i, j)
    boxes = [SLEEVE] + [bounds(other) for other in CUBES if other != name]
    for blo, bhi in boxes:
        if all(blo[a] - EPS <= clo[a] and chi[a] <= bhi[a] + EPS for a in range(3)):
            return True
    return False


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
# the cannon


def cannon_west(i, j, fw, fh):
    """Outboard, 7 deep x 5 tall. Column 0 is the front land, columns 1 and 5 carry the ribs, columns
    2 and 4 are the channel floor beside them, column 3 is the crown, row 4 is under the rim. This is
    the face the seven-band read lives on: land, rib, gutter, crown, gutter, rib, land.

    Columns 1 and 5 keep a painter at all because their top row survives: the ribs start half a unit
    below the cannon's top edge, so that row is half rib and half chamfer and the mask calls it
    visible. It is painted as the chamfer its neighbours are, which is what it looks like."""
    if i in GUTTERS:                                  # the channel floor, one column each side
        return GUTTER - (12 if j == STRAP_ROW else 0)
    lum = FLANK - round(ZFALL * abs(ramp(i, fw) - 0.5) * 2)   # brightest at the crown of the channel
    if j == 0:
        return lum + RIM                              # the chamfer where the cannon leaves the arm
    if j == STRAP_ROW:
        # The strap is riveted to the lands outside the ribs, because it cannot be riveted through
        # one - and columns 1 and 5 have no strap row at all, the ribs having taken it.
        return STRAP + (RIVET if i in (0, fw - 1) else 0)
    return lum - round(FALL * ramp(j - 1, fh - 1))


def cannon_north(i, j, fw, fh):
    """Front, 4 wide x 5 tall, column 0 inboard. Lit toward the outboard edge."""
    lum = FRONT + round(XGAIN * ramp(i, fw))
    if j == 0:
        return lum + RIM
    if j == STRAP_ROW:
        return STRAP + 8
    return lum - round(FALL * ramp(j - 1, fh - 1))


def cannon_south(i, j, fw, fh):
    """Back, 4 wide x 5 tall, column 0 OUTBOARD - the gradient runs the other way round the box."""
    lum = BACK + round(XGAIN * (1.0 - ramp(i, fw)))
    if j == 0:
        return lum + RIM
    if j == STRAP_ROW:
        return STRAP - 12
    return lum - round(FALL * ramp(j - 1, fh - 1))


def cannon_east(i, j, fw, fh):
    """Inboard. Only columns 0 and 6 - the half unit at the back and front edges that clears the
    sleeve - ever survive the burial test; everything between them is inside the sleeve. The strap
    row runs through it anyway: the band is one axial index shared by all four side faces, which is
    the horns' ring trick, and it is the only reason a band lines up around the corners of a box."""
    if j == STRAP_ROW:
        return STRAP - 30
    return IN + round(10 * ramp(i, fw)) - round(FALL * ramp(j, fh))


def cannon_up(i, j, fw, fh):
    """The top of the wrap. Survives only on the outboard column and the front and back edge rows,
    which together are the rim of plate that stands out of the sleeve's own 6x6 section."""
    return UP - round(18 * (1.0 - ramp(i, fw))) - (0 if 0 < j < fh - 1 else 14)


def cannon_down(i, j, fw, fh):
    return DOWN + 8


# ------------------------------------------------------------------------------------------------
# the ribs - one pair of cubes, identical but for their z, so most of their faces share a painter


def rib_west(i, j, fw, fh):
    """A rib's own outboard face, one column wide and the brightest thing on the part. It is lit
    identically to the flank behind it by the engine, so the separation has to be painted: 236
    against a crown of 214 and a gutter of 106."""
    return RIDGE + (12 if j == 0 else -round(14 * ramp(j, fh)))


def rib_front_north(i, j, fw, fh):
    """rib_front's outward flank, the one that faces the front of the part. Only column 1, the
    outboard half that stands clear of the cannon, survives. Painted against the channel walls to
    give the pair a direction - vanilla shades -z and +z identically, so ribs that are not painted
    round are two stripes."""
    return FRONT + 18 - round(FALL * ramp(j, fh))


def rib_back_south(i, j, fw, fh):
    """rib_back's outward flank; column 0 is the outboard half here, not column 1."""
    return BACK - 18 - round(FALL * ramp(j, fh))


def rib_channel(i, j, fw, fh):
    """The two flanks that face each other across the channel - rib_front's `south` and rib_back's
    `north`. The engine lights the two identically and so does this: what tells them apart is not
    their own value but the gutter, crown and gutter running between them."""
    return CHANNEL - round(FALL * ramp(j, fh))


def rib_east(i, j, fw, fh):
    """A rib's inboard cap, 1.5 of its 2 units deep inside the cannon. Never seen; kept honest by
    check_mask rather than by assertion in prose."""
    return INNER


def rib_up(i, j, fw, fh):
    return UP - 10


def rib_down(i, j, fw, fh):
    """A rib's underside. Only its outboard texel survives, and only because the rib overhangs the
    rim by a quarter unit - three quarters of that pixel is sitting on the rim's top face."""
    return DOWN + 14


# ------------------------------------------------------------------------------------------------
# the rim


def rim_west(i, j, fw, fh):
    """The rolled rim, outboard, 8 deep x 2 tall and entirely clear of the cannon and of the ribs.
    Two rows and both of them work: row 0 is the shadow where the rim emerges from under the cannon,
    row 1 is the free lower edge catching the light off its own roll. That is the spaulders' lame
    idiom spent on a single course instead of a stack. The ribs' feet cross this face on half-unit
    boundaries, so nothing here is painted for them - see the docstring."""
    lum = FLANK - round(ZFALL * abs(ramp(i, fw) - 0.5) * 2)
    return lum - LAP if j == 0 else lum + LIP


def rim_north(i, j, fw, fh):
    lum = FRONT + round(XGAIN * ramp(i, fw))
    return lum - LAP if j == 0 else lum + LIP


def rim_south(i, j, fw, fh):
    lum = BACK + round(XGAIN * (1.0 - ramp(i, fw)))
    return lum - LAP if j == 0 else lum + LIP


def rim_east(i, j, fw, fh):
    return IN - 6 + (0 if j == 0 else 10)


def rim_up(i, j, fw, fh):
    """The rim's shoulder: the ledge of it that is not under the cannon. Rows run back to front."""
    return UP - 22 - round(16 * (1.0 - ramp(i, fw)))


def rim_down(i, j, fw, fh):
    """The underside of the whole part - the only downward face on it that is not inside one of its
    own cubes. The sleeve still takes most of it: only the outboard column and the front and back
    edge rows fall outside the 6x6 section."""
    return DOWN + round(10 * ramp(i, fw))


PAINTERS = {
    ("cannon", "west"): cannon_west, ("cannon", "north"): cannon_north,
    ("cannon", "south"): cannon_south, ("cannon", "east"): cannon_east,
    ("cannon", "up"): cannon_up, ("cannon", "down"): cannon_down,
    ("rib_front", "west"): rib_west, ("rib_front", "north"): rib_front_north,
    ("rib_front", "south"): rib_channel, ("rib_front", "east"): rib_east,
    ("rib_front", "up"): rib_up, ("rib_front", "down"): rib_down,
    ("rib_back", "west"): rib_west, ("rib_back", "north"): rib_channel,
    ("rib_back", "south"): rib_back_south, ("rib_back", "east"): rib_east,
    ("rib_back", "up"): rib_up, ("rib_back", "down"): rib_down,
    ("rim", "west"): rim_west, ("rim", "north"): rim_north,
    ("rim", "south"): rim_south, ("rim", "east"): rim_east,
    ("rim", "up"): rim_up, ("rim", "down"): rim_down,
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


def seen(name, face) -> set:
    """The pixels of one face that the burial mask leaves visible."""
    fw, fh = faces(CUBES[name][0], CUBES[name][1])[face][2:]
    return {(i, j) for j in range(fh) for i in range(fw) if not buried(name, face, i, j)}


def check_mask() -> None:
    """The burial facts the shape was designed around, asserted rather than described.

    Each one is a geometric claim made in the docstring above, and each would break silently if a
    cube moved: the mask would still be *a* mask and the render would still be *a* render."""
    # Each rib stands on the cannon's outboard face, so it hides its own column of it - and only the
    # three rows it fully covers, because its ends are inset half a unit from the cannon's own.
    # Row 4 is absent for a different reason - the rim laps over it - which the next assert owns, so
    # the only row of each rib column left standing is the top one.
    for i in RIBS:
        assert seen("cannon", "west") & {(i, j) for j in range(5)} == {(i, 0)}, \
            f"a rib no longer covers exactly rows 1..3 of column {i} of the cannon's flank"
    # The channel between them is gutter, crown and gutter all the way down to the rim: three whole
    # columns, which is what makes the seven-band read a read rather than two stripes touching.
    assert all((i, j) in seen("cannon", "west") for i in GUTTERS + (3,) for j in range(4)), \
        "the channel between the ribs is no longer open down the cannon's flank"
    # The rim laps a whole unit up inside the cannon, so the cannon's bottom row of flank is gone.
    assert not any((i, 4) in seen("cannon", "west") for i in range(7)), \
        "the cannon's bottom flank row is no longer buried under the rim"
    # The cannon's underside is entirely inside the rim or inside the sleeve, bar the two corners
    # where the quarter-unit inboard step of the rim coincides with the sleeve's own z walls.
    assert seen("cannon", "down") == {(0, 0), (0, 6)}, \
        "the cannon's underside is no longer buried"
    # The rim is 0.25 proud of the cannon outboard and of the ribs too, so its whole flank shows -
    # that quarter unit is the sash's trick and it is the only thing separating those x planes.
    assert len(seen("rim", "west")) == 16, "the rim's flank is no longer entirely exposed"
    # Both ribs are buried inboard: 1.5 of their 2 units are inside the cannon.
    for rib in ("rib_front", "rib_back"):
        assert seen(rib, "east") == set(), f"{rib}'s inboard cap is no longer buried"
    # And nothing on the part is buried outright. A cube that draws no pixel at all is a cube that
    # should not be modelled, and it is the one failure this file would otherwise report as a clean
    # run with a face count of zero.
    for name in CUBES:
        assert any(seen(name, f) for f in ("up", "down", "east", "north", "west", "south")), \
            f"{name} is entirely buried and never drawn"


def main() -> None:
    check_geometry()
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
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)}, "
          f"{low} under 127)")
    print(f"  {visible} px survive the burial mask, {len(opaque) - visible} are INNER")
    for key in sorted(counts):
        print(f"    {key:14s} {counts[key]:3d} seen")


if __name__ == "__main__":
    main()
