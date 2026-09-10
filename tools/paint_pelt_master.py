"""
Paint the grayscale master for the "pelt" part.

Like the brooch, sash, tassets and greaves painters this does not merely claim that CUBES matches
the shipped geometry, it reads assets/armorpieces/armorpieces/decoration/pelt.json at run time and
asserts it - sizes, uvs AND origins, because on this part the origins are the whole argument
(check_geometry). Output goes to tools/decoration_masters/pelt.png plus pelt_inlay.png, which
sync_decoration_masters.py installs for the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

This master is 100% opaque, and the temptation to do otherwise was real: a fur hem WANTS a fringe
punched into it. It does not get one. Parts draw with armorCutoutNoCull, so a hole in the outboard
face of a strand shows the INSIDE of that strand's inboard face, not the leg behind it - a lit notch
where a gap was wanted. Raggedness on this part is carried by the geometry's own hem line and by
value, which is the tassets' rule applied to something soft.

What this part is, and what that costs the painter:

  * `pelt` is a MIRRORED pair - Attachment.of(LEFT_LEG, 0, 2, 0) plus Attachment.mirrored on the
    right - so the layer's scale(-1, 1, 1) runs on the right-hand copy and ONE master serves both.
    `west` is geo +x, outboard on both legs; `east` is geo -x, inboard on both, and every `east`
    face here is inside the wearer's own thigh. The tassets, the horns and the spaulders buy the
    same economy on the same terms.

  * The hero face is `west`, and that is the one thing this part does NOT share with the tassets on
    the socket beside it. The tassets is a plate on the FRONT-outer quadrant of the thigh and paints
    `north` as its hero; a hide draped over the hip is a flank object, so the outboard face carries
    it and `north` is painted a step under `west` on every cube. That is not only composition: the
    vanilla diffuse term shades by normal alone (up 1.0, down 0.5, +-z 0.8, +-x 0.6), so a +-x face
    renders a quarter darker than a +-z one at the same value. Painting the flank highest is what
    buys the flank back.

  * It rides the LEG bone, so it swings with the thigh and can never reach across to the other hip -
    the pauldron note in docs/plans/part-variety.md, one socket down. The one surface here that is
    buried at rest and NOT buried in motion is the thong's `up` face: the leggings TORSO shell
    reaches leg-local y = 0.4 and covers x <= 2.5, and it rides BODY, so it walks out from over this
    part twice a cycle. It is painted as a dimmed top edge, not as filler - the tassets' finding,
    arriving on a cord instead of a lame.

  * FUR IS NOT DETAIL AT THIS SIZE. The whole outboard surface of one hide is 32 texels. A hatched
    pile, a stitched edge or any repeating mark would turn to noise the moment the material ramp
    compressed it. So the part reads as fur through three things only: a hem that steps, which is
    geometry; clumped VALUE with no period, which is the CLUMP/HEM tables below; and a per-texel
    grain three times the plates', because at this size the difference between fur and sheet metal
    is whether neighbouring texels agree. Those tables are hand-written, and the point of them is
    that no two consecutive steps are equal and the sequence never repeats. Compare the tassets,
    whose whole point is that its three lames DO step by the same amount.

The geometry, in numbers. Part-local first (the frame the JSON is authored in, +Y DOWN), then
leg-local, which is part-local + (0, 2, 0) - the bone frame trace_geometry reports in. For reference
in that frame: the naked thigh is x -2..2, y 0..12, z -2..2; the leggings LEG shell is x -2.4..2.4,
y -0.4..12.4, z -2.4..2.4; the boots shell is the same box at 0.9; and the leggings TORSO shell,
which rides a different bone, covers x -6.3..2.5, y -12.4..0.4, z -2.4..2.4.

    cube     part-local x       part-local y       part-local z      leg-local y (top .. hem)
    cape     0.55 .. 2.55      -1.40 ..  0.60     -2.95 ..  2.05      0.60 ..  2.60
    thong    1.00 .. 3.00      -2.30 .. -1.30     -2.60 ..  0.40     -0.30 ..  0.70
    bunch    0.98 .. 2.98      -0.55 ..  1.45     -3.30 .. -0.30      1.45 ..  3.45
    strand   0.66 .. 2.83      -0.51 ..  2.72     -2.43 .. -0.23      1.49 ..  4.72
    swag     0.59 .. 2.69      -1.02 ..  1.15     -0.19 ..  1.88      0.98 ..  3.15
    tuft     0.54 .. 2.84      -1.03 ..  2.18      1.93 ..  2.98      0.97 ..  4.18

`strand`, `swag` and `tuft` are the three rotated cubes - bones `fall` (0, 0.3, -1.22) rotated
(-4, 0, -3), `sway` (0, -0.25, 0.83) rotated (2, 0, -3) and `trail` (0, -0.2, 2.44) rotated
(1, 0, -6) - so their extents above are rotated hulls and their faces are axis-aligned with nothing.
That is deliberate three times over. It stops a hanging clump reading as a box; it lets each strand
be placed a tenth of a unit off its neighbours without z-fighting, because a rotated face can never
be coplanar with an axis-aligned one; and the differing X rotations mean no two strands hang
parallel, which is the single cheapest way to say "this is not articulated plate".

    surface        part-local x      proud of the leggings thigh at 2.40
    leggings thigh      2.40         -
    cape                2.55         0.15   the hide pulled tight to the leg under the cord
    swag           2.58 .. 2.69      0.18 .. 0.29
    tuft           2.53 .. 2.84      0.13 .. 0.44
    strand         2.66 .. 2.83      0.26 .. 0.43   swelling as it falls clear of the fold
    bunch               2.98         0.58   the fold bunched over the hip crest
    thong               3.00         0.60   the cord, over everything it crosses

Nothing on this part is inside the leggings shell it hangs on: every cube clears x = 2.40, the
`bunch` clears the shell's front wall at z = -2.40 by another 0.90, and the `tuft` clears its back
wall by 0.58. No face lies in a shell plane - the fractional origins above exist for that reason
and for no other, so 2.55 must not be tidied to 2.5 and 0.98 must not be tidied to 1.0.

The three strands are laid end to end down the depth of the hide with 0.04, 0.05 gaps between them
(strand ends at z -0.23 and swag begins at -0.19; swag ends at 1.88 and tuft begins at 1.93). Those
gaps are the point: contiguous strands read as one ragged mass where spaced ones read as separate
boxes, and a gap that narrow is a crack rather than a hole - what shows through it is the `cape`
0.15 further in, never the leg. It also means no two strands' `west` faces ever share a z range, so
the fact that two of them carry the same -3 roll never matters.

WHERE THE HEM LANDS, which is the constraint this part was designed around. The `knees` socket sits
at leg-local y = 6 and DecorationAnchor.KNEES records what the shipped parts do to it: the tassets'
third lame reaches leg-local y = 6.82, so a knee part sits INSIDE it rather than below it, and the
tassets and the greaves leave 0.13 units between them. This part refuses that. Read front to back,
its hem is

    3.45  the bunch, at the front of the hip
    4.72  the strand, the longest
    3.15  the swag, the short middle one
    4.18  the tuft, at the back

so the LOWEST point of the pelt stops 2.10 above the tassets' third lame and 1.28 above the knee
anchor itself. The steps between those four hem lines are +1.27, -1.57 and +1.03: no two alike,
which is the hem doing the work the texture cannot. Measured against the shipped knee part rather
than against the socket, an exact separating-axis test over the two parts' oriented boxes puts the
closest approach at 0.215 (the strand to the poleyn, in z) - the poleyn is a front-of-leg object at
z -4.65..-2.65 and this is a flank object whose only cube reaching that far forward, the `bunch`,
stops 2.55 units short of the poleyn's top. A knee part authored after this one has the whole of
leg-local y 4.72..12 and the whole of the leg's front free of it.

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

WHAT IS ACTUALLY SEEN, since half of this master is not. `bunch` is the only cube with two fully
exposed faces - nothing stands outboard of it but the cord, a unit above and never crossing it, and
nothing is in front of it at all - so its six `west` and four `north` texels are the part's readable
mass and get the most careful values. `swag` and `tuft` have fully exposed `west` faces for the same
reason, the strands being laid end to end. `strand`'s top two rows are behind the `bunch`, so its
value climbs DOWN the face - deep pile where it disappears under the fold, base pelt in the middle,
the free bottom row carried to TIP. A strand that is brightest where it is attached reads as a
plate; brightest where it is loose reads as hair. `cape` is the connective mass and is mostly
buried: of its ten `west` texels the top row is the band of hide between the cord and the strands
(its two back columns only 38% of the way, where the swag's top edge crosses them) and the bottom
row is behind three strands at once. Every face of `strand` and `swag` that looks along the depth of
the hide - the `south` and `north` faces that sit either side of a 0.04 crack - is painted INNER, so
that whatever those two nearly-parallel faces do to each other at that distance, they do it in the
dark.

THE FITTING. The part declares `armorpieces:inlay`, a dye, and the mask is the five FUR cubes -
cape, bunch, strand, swag, tuft - with the `thong` left out of it. That is the whole reason the cord
is a cube of its own rather than a painted band: a band would have had to be dyed with the hide it
was drawn on. With the fitting empty the pelt is one trim material throughout; with a dye in it the
hide takes the dye and the cord keeps the metal that was smithed into it, which is the one
combination a fur part actually wants. That is also why CORD sits above every fur value on the
part: after the mask is applied the cord's twelve texels are the only pixels still speaking for
the material, and they have to separate from a dye of any brightness. No static layer: a fixed-colour
hide would spend the trim material on the cord alone, and a part that barely answers its own
material is a worse part than a metallic pelt.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image

import decoration_paths
from fitting_mask import write_mask

ROOT = Path(__file__).resolve().parent.parent
GEO = decoration_paths.geometry("pelt")
OUT = ROOT / "tools" / "decoration_masters" / "pelt.png"

TEX_W, TEX_H = 64, 32

# origin, size (w, h, d) and uv (u, v), mirroring pelt.json in that file's own order - the three
# cubes of the root `pelt` bone, then `fall`'s, `sway`'s and `trail`'s. Origins are asserted as well
# as sizes because the docstring's whole clearance argument is made out of them.
CUBES = {
    "cape":   ((0.55, -1.4, -2.95), (2, 2, 5), (0, 0)),
    "thong":  ((1, -2.3, -2.6), (2, 1, 3), (14, 0)),
    "bunch":  ((0.98, -0.55, -3.3), (2, 2, 3), (24, 0)),
    "strand": ((0.7, -0.6, -1.05), (2, 3, 2), (34, 0)),
    "swag":   ((0.62, -0.6, -1), (2, 2, 2), (42, 0)),
    "tuft":   ((0.6, -0.55, -0.5), (2, 3, 1), (50, 0)),
}

# The fitting takes the hide and leaves the cord. See the docstring's last paragraph.
FUR = ("cape", "bunch", "strand", "swag", "tuft")

random.seed(73)  # deterministic output - regenerating must not churn the PNG

# Calibrated against the ramp, not guessed: the material ramp interpolates dark -> mid over master
# values 0..127 and mid -> light over 128..255, so a master confined to one half only ever uses half
# of a material's ramp. The visible values here run the deep pile under the fold to the lit tips of
# the longest strand, with the cord above all of them.
CORD = 222      # the thong's outboard face - smooth, and the one face that must not read as fur
CORD_LO = 170   # the cord turned away from the light
TIP = 212       # a free hem edge, where the hair ends and catches
PELT = 168      # the base value of an outboard fur face
PELT_LO = 116   # a trough between two clumps
BACK = 104      # fur facing backward or inboard, in its own shadow
PILE = 84       # deep pile - fur disappearing under the cord or under another clump
INNER = 62      # buried: inside the thigh, inside the cape, or under the fold
UNDER = 40      # a free underside

FALL = 22       # top-to-bottom falloff down a standing face
DEPTH = 26      # front-to-back falloff across a flank
LASH = 18       # the shadow the cord throws onto the hide directly under it

# Hand-written, not generated, and read along a face's columns. Changing one of these numbers moves
# a clump, which is a design edit and not a tuning knob.
CLUMP5 = (24, -34, 10, -20, 38)   # five depth columns: the cape's flank
CLUMP3 = (-22, 32, -8)            # three: the bunch's flank
CLUMP2 = (18, -26)                # two: a strand's flank, and any two-wide face
HEM3 = (44, -34, 18)              # per-column tip / trough on a FREE hem row, three wide
HEM2 = (-30, 40)                  # the same, two wide


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
    """The per-texel noise of a fur face. Three times the plates' +-3: on a hide the grain IS the
    material, because at this size the only thing separating fur from sheet metal is whether
    neighbouring texels agree."""
    return random.randint(-10, 10)


def paint_cape(img) -> None:
    """The body of the hide: 2 x 2 x 5, lying against the outboard thigh at x = 2.55 and running its
    whole depth, z -2.95..2.05.

    It is the connective mass and it is mostly buried, which is the honest description rather than a
    complaint. `west` row 0 is the band of hide between the cord above and the strands below, and it
    is the only part of this cube a camera reaches in quantity - its two back columns only for the
    top 38%, where the swag's own top edge crosses them, which is why they are dropped toward the
    pile rather than lit like the front three. Row 1 lies behind the bunch, the strand, the swag and
    the tuft, all four of which stand further out; it is painted as deep pile rather than as INNER
    because the crossings of three rotated clumps leave slivers of it showing, and filler would read
    as a hole there.

    Its `down` face is dark everywhere. The strands are laid end to end with 0.04 gaps, so nothing
    of it is ever seen except through those cracks, and a crack that shows a lit underside stops
    being a crack."""
    f = rects("cape")

    x0, y0, fw, fh = f["west"]           # 5 deep x 2 tall, col 0 = front, row 0 = top
    for j in range(fh):
        for i in range(fw):
            if j == 0:
                # Well under the base pelt value: this band sits in the cord's own shadow, and if it
                # is lit like a free face the cord above it and this below read as two straps rather
                # than as a cord tied over a hide.
                lum = PELT - LASH - 22 + CLUMP5[i] - round(DEPTH * ramp(i, fw))
                if i >= 3:
                    lum -= 24            # the swag crosses these two columns from 38% down
            else:
                lum = PILE + CLUMP5[i] // 4
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["north"]          # 2 x 2, col 0 = inboard, row 0 = top
    for j in range(fh):
        for i in range(fw):
            lum = (PELT - 30 + CLUMP2[i]) if j == 0 else INNER   # row 1 is behind the bunch
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["south"]          # 2 x 2, col 0 = OUTBOARD; in the thigh and behind the tuft
    for j in range(fh):
        for i in range(fw):
            free = i == 0 and j == 0     # only the outboard-top sliver clears the thigh at x = 2.4
            put(img, x0 + i, y0 + j, (BACK - 22 if free else INNER) + random.randint(-3, 3))

    x0, y0, fw, fh = f["up"]             # 2 wide (x) x 5 deep, rows run BACK to front
    for j in range(fh):
        for i in range(fw):
            # The cord covers z -2.60..0.40; rows 0, 1 and 4 reach past its ends, and only the
            # outboard column of them is also clear of the thigh.
            free = i == 1 and j in (0, 1, fh - 1)
            put(img, x0 + i, y0 + j, (BACK - 30 if free else INNER) + random.randint(-3, 3))

    fill(img, f["down"], INNER)          # seen only through 0.04-wide cracks; kept dark on purpose
    fill(img, f["east"], INNER)          # the whole face is inside the thigh


def paint_thong(img) -> None:
    """The cord the hide is lashed on with: 2 x 1 x 4 at x = 3.00, the proudest surface on the part
    and the only one that is not fur.

    It exists for the fitting. A dye inlay covering the whole pelt would leave the trim material
    nothing to be, and a binding painted as a band on the cape's own face would have been dyed along
    with it; a cube of its own is the only version of this that survives the mask. So its three
    `west` texels are painted smooth - jitter +-2 against the fur's +-10 - and pitched above every
    fur value on the part.

    It is also three units deep against the cape's five, set back 0.35 at the front and 1.65 at the
    back, so the hide runs past both ends of it. A cord as long as the thing it ties is a hem, not a
    cord - and at a unit tall and 0.6 proud it is already the largest single surface here, which is
    why it was shortened rather than made brighter to read."""
    f = rects("thong")

    x0, y0, fw, fh = f["west"]           # 4 deep x 1 tall, col 0 = front. The cord itself.
    for i in range(fw):
        put(img, x0 + i, y0, CORD - round(DEPTH * ramp(i, fw)) + random.randint(-2, 2))

    x0, y0, fw, fh = f["north"]          # 2 x 1, col 0 = inboard; 0.2 clear of the thigh's front
    for i in range(fw):
        put(img, x0 + i, y0, CORD - 40 + 14 * i + random.randint(-2, 2))

    x0, y0, fw, fh = f["up"]             # 2 wide (x) x 4 deep, rows BACK to front
    for j in range(fh):
        for i in range(fw):
            # col 1 is x 2.00..3.00, half of it outboard of the torso shell's wall at 2.5; col 0 is
            # under that shell at rest and out from under it on every stride, so it is dimmed flank
            # and not filler.
            lum = CORD_LO - round(20 * ramp(j, fh)) if i == 1 else INNER + 20
            put(img, x0 + i, y0 + j, lum + random.randint(-2, 2))

    x0, y0, fw, fh = f["south"]          # 2 x 1, col 0 = OUTBOARD; only its outer 0.6 clears the leg
    for i in range(fw):
        put(img, x0 + i, y0, (CORD - 96 if i == 0 else INNER) + random.randint(-2, 2))

    fill(img, f["down"], INNER)          # sits on the cape for its whole length
    fill(img, f["east"], INNER)          # inside the thigh


def paint_bunch(img) -> None:
    """The fold bunched over the hip crest: 2 x 2 x 3 at x = 2.98, reaching z = -3.30, which is 0.90
    clear of the leggings thigh's front wall.

    It is the only cube on the part with two fully exposed faces. Nothing stands outboard of it
    except the cord, which is a unit above and never crosses it, so all six `west` texels are seen;
    and nothing is in front of it at all, so all four `north` texels are seen. That makes it the
    part's readable mass and the reason a pelt is not simply a flap: from directly in front of the
    wearer - the view a player has of their own legs - the tassets on this socket shows a plate
    edge-on and this shows a lobe of hide standing off the hip.

    Its bottom row is a FREE HEM at leg-local 3.45, so it carries HEM3: one column lifted past the
    tip value, one dropped under the pile, one between. That is the whole trick for fur at this
    scale - a hem uniform in value reads as a cut edge whatever the geometry does."""
    f = rects("bunch")

    x0, y0, fw, fh = f["west"]           # 3 deep x 2 tall, col 0 = front, row 0 = the crest
    for j in range(fh):
        for i in range(fw):
            lum = PELT + CLUMP3[i] - round(DEPTH * ramp(i, fw))
            lum += HEM3[i] - FALL if j == fh - 1 else 10
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["north"]          # 2 x 2, col 0 = inboard, row 0 = top. Fully exposed.
    for j in range(fh):
        for i in range(fw):
            lum = PELT - 26 + CLUMP2[i] + (HEM2[i] - FALL if j == fh - 1 else 0)
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["down"]           # 2 wide (x) x 3 deep, rows BACK to front
    for j in range(fh):
        for i in range(fw):
            # Rows 0-1 are over the strand; row 2 is z -2.30..-3.30, hanging free in front of it.
            free = j == fh - 1
            put(img, x0 + i, y0 + j,
                ((UNDER + 26 + 10 * i) if free else INNER) + random.randint(-3, 3))

    x0, y0, fw, fh = f["up"]             # 2 wide x 3 deep; under the cape except outboard and front
    for j in range(fh):
        for i in range(fw):
            free = i == 1 or j == fh - 1
            put(img, x0 + i, y0 + j,
                ((BACK - 14 - round(16 * ramp(j, fh))) if free else INNER) + random.randint(-3, 3))

    x0, y0, fw, fh = f["south"]          # 2 x 2, col 0 = OUTBOARD; inside the cape but for a sliver
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j,
                ((PILE - 16) if i == 0 else INNER) + random.randint(-3, 3))

    fill(img, f["east"], INNER)          # inside the thigh


def paint_strand(img) -> None:
    """The long strand, on `fall`: pivoted at (0, 0.3, -1.22) and rotated (-4, 0, -3), so it swings
    forward and outward as it descends and its outboard face swells from 2.66 at the top to 2.83 at
    the hem.

    It is the lowest thing on the part, and where it stops is the part's whole restraint: leg-local
    4.72, which is 2.10 above the tassets' third lame and 1.28 above the knee anchor.

    Its top two rows are behind the bunch, which stands 0.15 further out over exactly that band, so
    the value climbs down the face rather than up it. Both of its depth-facing sides are painted
    INNER: `north` looks into the back of the bunch, and `south` looks across a 0.04 crack at the
    swag's own `north`, two nearly-parallel faces a twenty-fifth of a unit apart. Whatever they do
    to each other at that distance they do in the dark."""
    f = rects("strand")

    x0, y0, fw, fh = f["west"]           # 2 deep x 3 tall, col 0 = front, row 0 = under the fold
    for j in range(fh):
        for i in range(fw):
            if j == 0:
                lum = PILE + CLUMP2[i] // 2
            elif j == fh - 1:
                lum = TIP + CLUMP2[i] // 2 + HEM2[i]
            else:
                lum = PELT_LO + CLUMP2[i]
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["down"]           # 2 wide (x) x 2 deep, rows BACK to front. The hem tip.
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j,
                UNDER + round(34 * ramp(j, fh)) + (12 if i else -10) + random.randint(-4, 4))

    fill(img, f["north"], INNER)         # into the back of the bunch
    fill(img, f["south"], INNER)         # across the crack at the swag
    fill(img, f["up"], INNER)            # under the cape and under the fold
    fill(img, f["east"], INNER)          # inside the thigh


def paint_swag(img) -> None:
    """The short middle strand, on `sway`: pivoted at (0, -0.25, 0.83) and rotated (2, 0, -3), a
    POSITIVE X where the strand in front of it has a negative one, so the two hang apart rather than
    parallel.

    It is the shortest thing that hangs, leg-local 3.15, and it is between the two longest - the
    -1.57 step in the hem line, and the reason that line does not simply taper. Its `west` face is
    fully exposed for the same reason the strands are laid end to end: nothing outboard of it shares
    its z. Both depth-facing sides look across a crack and are painted INNER."""
    f = rects("swag")

    x0, y0, fw, fh = f["west"]           # 2 deep x 2 tall, col 0 = front, row 0 = top
    for j in range(fh):
        for i in range(fw):
            lum = PELT - 10 + CLUMP2[i] - round(DEPTH * ramp(i, fw))
            lum += HEM2[i] + 14 if j == fh - 1 else 0
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["down"]           # 2 wide (x) x 2 deep, rows BACK to front
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j,
                UNDER + round(24 * ramp(j, fh)) + (10 if i else -8) + random.randint(-4, 4))

    fill(img, f["north"], INNER)         # across the crack at the strand
    fill(img, f["south"], INNER)         # across the crack at the tuft
    fill(img, f["up"], INNER)            # under the cape
    fill(img, f["east"], INNER)          # inside the thigh


def paint_tuft(img) -> None:
    """The strand at the back, on `trail`: pivoted at (0, -0.2, 2.44) and rotated (1, 0, -6), and
    the only cube on the part that is one unit deep rather than two or three. It is the tail of the
    hide, and a tail that is as thick as the body of it is not a tail.

    Its `south` face stands 0.58 outboard of the leggings thigh's back wall, which makes this the
    only part of the pelt visible from directly behind the wearer, and it is painted as a dim rear
    clump rather than as a buried one for that reason. Its `west` face is a single column three
    texels tall, and it is the one place on the part where the fur gradient runs purely vertically:
    pile at the top where the cape swallows it, base pelt, tip."""
    f = rects("tuft")

    x0, y0, fw, fh = f["west"]           # 1 deep x 3 tall, row 0 = top
    for j in range(fh):
        lum = (PILE + 12, PELT - 18, TIP - 18)[j]
        put(img, x0, y0 + j, lum + grain())

    x0, y0, fw, fh = f["south"]          # 2 x 3, col 0 = OUTBOARD, row 0 = top. Seen from behind.
    for j in range(fh):
        for i in range(fw):
            lum = BACK + 22 - 26 * i - round(FALL * ramp(j, fh))
            if j == fh - 1:
                lum += HEM2[i] + 24
            put(img, x0 + i, y0 + j, lum + grain())

    x0, y0, fw, fh = f["down"]           # 2 wide (x) x 1 deep. The hem.
    for i in range(fw):
        put(img, x0 + i, y0, UNDER + 18 + (12 if i else -10) + random.randint(-4, 4))

    fill(img, f["north"], INNER)         # across the crack at the swag
    fill(img, f["up"], INNER)            # under the cape
    fill(img, f["east"], INNER)          # inside the thigh


def check_geometry() -> None:
    """CUBES must be the cube list of the shipped geometry, in order, down to the origins. Painting
    a texture for a shape the model no longer has is invisible to every other check in this
    pipeline: both halves stay internally consistent while the rectangles slide off the faces they
    were drawn for. The origins are asserted as well as the sizes because this part's argument -
    what clears the leggings shell, what clears the knee, which cube stands in front of which - is
    made entirely out of them, and a nudged origin would leave that prose quietly false."""
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
    paint_cape(img)
    paint_thong(img)
    paint_bunch(img)
    paint_strand(img)
    paint_swag(img)
    paint_tuft(img)

    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque == set(claimed), "painted pixels do not match the UV rectangles"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)})")

    fur = [r for name in FUR for r in rects(name).values()]
    write_mask(img, fur, OUT.with_name("pelt_inlay.png"))


if __name__ == "__main__":
    main()
