"""
Paint the grayscale master for the "sash" part.

Kept as a script rather than a checked-in binary so the shape stays editable and reviewable. Like
paint_brooch_master.py - and unlike the five painters before it - this one does not merely claim
that CUBES matches the shipped geometry, it reads
assets/armorpieces/armorpieces/decoration/sash.json at run time and asserts it (check_geometry).
Output goes to tools/decoration_masters/sash.png, which sync_decoration_masters.py installs for
the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

Like every master since the circlet this one is 100% opaque. A leather belt has no fringe, and parts
draw with armorCutoutNoCull, so a hole punched in a 3-pixel band would show the inside of the band
rather than the leggings behind it. Every pixel here is value.

What this part is, and what that costs the painter:

  * `belt` is a SINGLE, non-mirrored attachment - Attachment.of(BODY, 0, 10, 0), geo (0, 10, 0) -
    so the layer's scale(-1, 1, 1) never runs and none of the one-master-serves-both economy the
    horns and spaulders got applies. The ring is symmetric about x = 0 and painted symmetrically;
    the knot and the tail are not, and they are the reason `west` and `east` here are genuinely
    different faces rather than the same face twice.

  * It has THREE hero faces, not one. `north` on the front bar and the buckle (seen head on),
    `south` on the back bar (seen in third person, which is where a player looks at their own
    character), and `west` on the knot and tail (the outboard flank of the hip). The wing roots'
    note that the palette constants are not transferable by name applies with a vengeance: read
    FACE as "a face that is seen" and INNER as "a face that is inside something".

  * Almost nothing on the waist is free space. The 1.0 arm sleeve occupies geo x 3..9 down to
    y = 13, which is every unit of room outboard of the torso at belt height, so the ring's two side
    bars are behind an arm whenever the arms hang. They are painted properly anyway - the arms swing
    through most of the walk cycle, and a band that is only right at rest is wrong for most of the
    time it is looked at.

Burial, and why the buried rows are painted anyway. The outermost shell over the torso at the waist
is the chestplate's 1.0 layer (geo x +/-5, z +/-3); the leggings' own layer is the INNER one at 0.5
(x +/-4.5, z +/-2.5), so designing against the 1.0 surface is the conservative choice and both cases
show. Every cube here is authored deeper than it shows: the front bar spans z -4..-2 with only its
front unit outside the shell, the back bar z 1..4 with only its back unit outside, the buckle
z -5..-2 with two of its three units inside the front bar. Those hidden rows are painted at INNER
rather than left black, exactly as the horns', spaulders' and brooch's were, so a pass-C nudge to
BELT reveals shading rather than a black stripe.

The two bars are not the same box, and the front one is the shallower at two deep. Depth behind the
waist is free - nothing is back there to land a face on - while in front every plane is spoken for,
and two is the depth that puts the bar's back face on z = -2, the naked body box's own front wall.
That is a plane already buried under both shells, which is the circlet's and the horns' burial trick
used on purpose rather than a face left fighting. It is also the cheaper cube to paint: a two-deep
bar spends one row of INNER and one of value on `up`, on `down` and on `east`, where the back bar
spends two and one.

A note on what this painter does NOT bury against. The bars end at geo x = +/-5.5, and the vambrace
cannon's inboard face lands on exactly that plane on the left, sharing 3.00 x 1.50 with the front
bar's `west` and 3.00 x 2.50 with the back bar's. Half a unit of each of those patches is outside the
arm sleeve, so the sleeve does not hide them. They are still painted as this part's own faces rather
than as INNER, for the reason no shell argument covers: a vambrace is a DECORATION, and its socket
may be empty. Burying a face against a part that might not be worn is the one burial that can leave a
black stripe on a finished set. (The front bar's `west` is INNER anyway - not because of the cannon,
but because this part's own knot swallows it whole.)

The face rectangles come from paint_circlet_master.faces(): row one (v .. v+d) holds up then down,
each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west, south with widths
d, w, d, w. Note the row-two order: the two thin d-wide faces come FIRST and THIRD.

The one line that is not copied verbatim is net(). This is the first part in the mod with a cube
that is not a whole number of units: the knot is 4.9 tall, a tenth lifted off the leggings shell's
bottom cap at y = 12.5 so its underside is not coplanar with it. A texture net is whole pixels, so
the net rounds UP - five rows for 4.9 units, of which the game maps the face across the first 4.9,
touching every one and dropping a tenth of the last. Rounding down would leave the bottom tenth of
the knot sampling a row nobody painted, which is the failure that is invisible in every check here
and obvious on a model.

Orientation inside each rectangle is the table PLAN.md records as measured, not recalled. It is
written here in terms of MIN X and MAX Z rather than "inboard" and "back", because this part has
cubes on both sides of x = 0 and the gloss inverts on the right-hand ones:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x              max z
    down            +y  (underside)      min x              max z
    west            +x                   min z              min y (top)
    east            -x                   max z              min y (top)
    north           -z  (front)          min x              min y (top)
    south           +z  (back)           max x              min y (top)

So on the back bar - whose only proud depth row is its BACK one - the lit row of `up` and `down` is
row 0, while on the front bar it is the last row (row 1 of two, not row 2 of three). Getting that
pair the same way round would paint the buried grey onto the one lit edge of one of them.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image

from fitting_mask import write_mask

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "sash.json"
OUT = ROOT / "tools" / "decoration_masters" / "sash.png"

TEX_W, TEX_H = 64, 32

# size (w, h, d) and uv (u, v), mirroring sash.json, in that file's own order (bone `belt`'s six
# cubes, then `tail`, then `tail_end`). Geo extents, for reading the paint code against:
#   front  - the band across the front of the waist, one unit proud of the 1.0 shell and one buried;
#            geo x -5.5..5.5, y 8..11, z -4..-2.
#   back   - the same band behind, a unit deeper because nothing crowds it there;
#            geo x -5.5..5.5, y 8..11, z  1..4.
#   side_l - the ring's left side, slimmer than the bars so no two of them share a plane;
#            geo x  4..6,   y 8.5..10.5, z -3.5..3.5.
#   side_r - the same on the right;                   geo x -6..-4,  y 8.5..10.5, z -3.5..3.5.
#   buckle - the plate at front centre, one unit proud of the band; geo x -2..2, y 7.5..10.5,
#            z -5..-2.
#   knot   - the gathered wrap at the LEFT hip that the tail runs out of; geo x 4.25..7.25,
#            y 7.5..12.4, z -4.5..-0.5. The 4.9 of height is the one fractional dimension on the
#            part: five units would put its underside on the leggings shell's bottom cap at 12.5.
#   tail_* - the hanging strap, on two bones at +5 and +12 degrees so it trails backwards; geo
#            x 5..7 then 5.75..6.75, reaching y 18.73. Both are outboard of x = 4.9, which is the
#            widest any leg layer ever reaches, and rotation about X preserves x - so no leg angle
#            can touch them. The upper segment's inboard face at x = 5 clears it by a tenth of a
#            unit, which is the tightest number on the part.
CUBES = {
    "front":      ((11, 3, 2), (1, 10)),
    "back":       ((11, 3, 3), (28, 9)),
    "side_l":     ((2, 2, 7), (0, 0)),
    "side_r":     ((2, 2, 7), (18, 0)),
    "buckle":     ((4, 3, 3), (10, 15)),
    "knot":       ((3, 4.9, 4), (36, 0)),
    "tail_upper": ((2, 5, 3), (50, 0)),
    "tail_end":   ((1, 4, 3), (1, 15)),
}

random.seed(29)  # deterministic output - regenerating must not churn the PNG

# Calibrated against the ramp, not guessed. the material ramp interpolates dark -> mid over
# master values 0..127 and mid -> light over 128..255, so a master confined to one half only ever
# uses half of a material's ramp. The visible pixels here run the buckle's aperture (24) to the lit
# top bar of its frame (250).
UP = 238        # a top face standing proud
FACE = 200      # a face that is seen: `north` at the front, `south` at the back, `west` at the hip
FLANK = 150     # a proud depth column of a side face
DOWN = 42       # an underside
INNER = 72      # buried in a shell, in the torso, or in another cube of the part
SLOT = 24       # the buckle's aperture and the mouth the tail runs out of

FALL = 28       # top-to-bottom falloff down a standing face
RIM = 34        # the lit chamfer along a top edge
HOLE = 95       # a punched belt hole - big, because one pixel is the whole hole
BINDING = 70    # the score where the knot's wrap is bound
FERRULE = 40    # the metal tag capping the strap end


def net(size):
    """A cube's box-UV net in whole pixels. Rounds UP; see the module docstring on the knot's 4.9."""
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


def put(img, x: int, y: int, lum: int, alpha: int = 255) -> None:
    if 0 <= x < TEX_W and 0 <= y < TEX_H:
        img.putpixel((x, y), (max(0, min(255, lum)), alpha))


def fill(img, rect, lum: int, jitter: int = 3) -> None:
    x0, y0, w, h = rect
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            put(img, x, y, lum + random.randint(-jitter, jitter))


def rows(img, rect, values, jitter: int = 3) -> None:
    """Paint a rectangle one value per ROW, top to bottom."""
    x0, y0, w, h = rect
    assert len(values) == h, f"{h} rows, {len(values)} values"
    for j, lum in enumerate(values):
        for i in range(w):
            put(img, x0 + i, y0 + j, lum + random.randint(-jitter, jitter))


def cols(img, rect, values, jitter: int = 3) -> None:
    """Paint a rectangle one value per COLUMN, left to right."""
    x0, y0, w, h = rect
    assert len(values) == w, f"{w} columns, {len(values)} values"
    for i, lum in enumerate(values):
        for j in range(h):
            put(img, x0 + i, y0 + j, lum + random.randint(-jitter, jitter))


def ramp(i: int, n: int) -> float:
    """Position along a face axis, 0.0 at column/row 0 and 1.0 at the far end."""
    return 0.0 if n <= 1 else i / (n - 1)


def paint_front(img) -> None:
    """The front bar. TWO deep, with its front unit outside the chestplate surface and its back one
    inside, so on `up` and `down` - whose depth rows run BACK to FRONT - the one row that shows is
    the last of two. Every buried run on this cube is a single row: one on `up`, one on `down`, one
    column on `east`.

    Its `north` face is eleven columns wide and two things sit on top of it: the buckle over
    columns 3-6 (geo x -2..2) and the knot, which swallows column 10 (geo x 4.5..5.5) whole. Those
    columns are painted as plain strap rather than as INNER, which costs nothing and keeps the read
    if BELT moves in pass C. The three columns at the far end (geo x -5.5..-2.5, the wearer's right,
    the side the free end of a real belt runs to) carry the punched holes, and they drop the top
    chamfer entirely: at one pixel a hole only reads if what surrounds it is plainly darker than the
    rest of the band, which is the lesson the brooch's rivet paid for."""
    size, uv = CUBES["front"]
    w, h, d = net(size)
    f = faces(size, uv)
    holes, under_buckle, under_knot = (0, 2), (3, 4, 5, 6), (10,)

    x0, y0, fw, fh = f["north"]          # 11 x 3, col 0 = min x, row 0 = top
    for j in range(fh):
        for i in range(fw):
            lum = FACE - round(FALL * ramp(j, fh))
            if i < 3:
                lum -= 16                # the punched run reads as a flatter, duller strap
                if i in holes and j == 1:
                    lum -= HOLE
            else:
                if j == 0:
                    lum += RIM           # the chamfer along the band's top edge
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["up"]             # 11 wide x 2 deep, row 1 is the proud one
    for i in range(fw):
        covered = i in under_buckle or i in under_knot
        put(img, x0 + i, y0 + 0, INNER + random.randint(-3, 3))
        put(img, x0 + i, y0 + 1, (INNER if covered else UP) + random.randint(-3, 3))

    x0, y0, fw, fh = f["down"]           # same layout; only the knot hangs past the band's underside
    for i in range(fw):
        put(img, x0 + i, y0 + 0, INNER + random.randint(-3, 3))
        put(img, x0 + i, y0 + 1,
            (INNER if i in under_knot else DOWN) + random.randint(-3, 3))

    fill(img, f["west"], INNER)          # the +x end is entirely inside the knot
    fill(img, f["south"], INNER)         # on the body box's front wall at z = -2, under both shells

    # `east` is the -x end cap, and it is NOT buried - nothing sits on the right hip. Its columns
    # run back to front, so of the two the proud one is the last.
    cols(img, f["east"], [INNER, FLANK])
    x0, y0, fw, fh = f["east"]
    put(img, x0 + 1, y0, FLANK + RIM + random.randint(-3, 3))


def paint_back(img) -> None:
    """The back bar. The front bar's opposite number in geometry and its OPPOSITE in texture layout:
    its proud unit is at z 3..4, the far end of its depth run rather than the near one, so on `up`
    and `down` the lit row is row 0 while the front bar's is its last, and on `west`/`east` the proud
    depth column swaps ends the same way. This is the one pair on the part where getting the row
    order the same way round on both would look right on one bar and inverted on the other, with
    nothing on either to say which.

    It is also a unit DEEPER than the front bar, three against two, and the asymmetry is earned
    rather than sloppy: forward of the waist the buckle wants a plane to stand proud of and the
    body box's own front wall at z = -2 is exactly where the front bar's back face wants to be,
    while behind it there is nothing in the way and a third unit of burial is free. So the two bars
    are the same band and not the same box, and none of the row indices below transfer to the front.

    In third person the back of a player is the face that is actually looked at, so this bar is not
    treated as a spare: a keeper loop at the centre, scored off on both sides, keeps a flat
    eleven-pixel slab from reading as a slab. The score has to go to -BINDING before it separates
    from the top chamfer every other column is getting - the brooch's finding, arriving again."""
    size, uv = CUBES["back"]
    w, h, d = net(size)
    f = faces(size, uv)
    keeper, score = (4, 5, 6), (3, 7)

    x0, y0, fw, fh = f["south"]          # 11 x 3, col 0 = MAX x, row 0 = top
    for j in range(fh):
        for i in range(fw):
            lum = FACE - round(FALL * ramp(j, fh))
            if j == 0:
                lum += RIM
            if i in keeper:
                lum += 18 if j else 6    # the loop stands a hair proud of the strap under it
            elif i in score:
                lum -= BINDING
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["up"]             # 11 wide x 3 deep, row 0 is the proud one here
    for i in range(fw):
        put(img, x0 + i, y0 + 0, UP + (10 if i in keeper else 0) + random.randint(-3, 3))
        put(img, x0 + i, y0 + 1, INNER + random.randint(-3, 3))
        put(img, x0 + i, y0 + 2, INNER + random.randint(-3, 3))

    x0, y0, fw, fh = f["down"]
    for i in range(fw):
        put(img, x0 + i, y0 + 0, DOWN + random.randint(-3, 3))
        put(img, x0 + i, y0 + 1, INNER + random.randint(-3, 3))
        put(img, x0 + i, y0 + 2, INNER + random.randint(-3, 3))

    cols(img, f["west"], [INNER, INNER, FLANK])   # +x end, columns run front to back
    cols(img, f["east"], [FLANK, INNER, INNER])   # -x end, columns run back to front
    for name, proud in (("west", 2), ("east", 0)):
        x0, y0, fw, fh = f[name]
        put(img, x0 + proud, y0, FLANK + RIM + random.randint(-3, 3))

    fill(img, f["north"], INNER)         # inside the torso


def paint_side(img, name, outboard_face, out_col_up, out_col_cap) -> None:
    """One of the ring's two side bars, 2 x 2 x 7, spanning front bar to back bar.

    These are the part's least-seen cubes and the argument for painting them properly is worth
    stating: the 1.0 arm sleeve is geo x 3..9 down to y = 13, so at rest an arm covers everything
    from the torso wall outwards at belt height and both side bars are behind one. They are visible
    for most of a walk cycle, from directly above or below, and whenever the arms are raised.

    Only four of the seven depth columns of the outboard flank are free: the knot swallows the front
    three of the left bar. `up` and `down` have to be masked twice over, because two different things
    bury them and the two are counted from opposite ends of the same run.

    The bars take the ends. The back bar spans z 1..4 and covers rows 0 and 1; the front bar spans
    z -4..-2 and covers row 6; rows 2..5 are left. Rows 2 and 5 are each only half covered - the bars
    stop at z = 1 and z = -2, mid-row both times - and a half-covered row counts as free, because the
    half that shows is worth more than the half that does not.

    Then the knot takes three of those four back, on the LEFT bar alone. `up` and `down` number their
    depth rows from max z while the flanks number their columns from min z, so the flank's buried
    columns 0, 1, 2 arrive here as rows 6, 5, 4 - which is why free_rows is derived from
    buried_depth by reversal rather than written out twice and left to drift. What survives is two
    lit rows on the left bar and four on the right.

    Only the outboard of the two x columns is outside the shell - which side that is depends on the
    sign of x, hence out_col_up rather than a hardcoded 1."""
    size, uv = CUBES[name]
    w, h, d = net(size)
    f = faces(size, uv)
    buried_depth = (0, 1, 2) if name == "side_l" else ()   # the knot covers the left bar's front
    clear_depth = (2, 3, 4, 5)                             # rows of `up`/`down` outside both bars
    free_rows = [j for j in clear_depth if (d - 1 - j) not in buried_depth]

    x0, y0, fw, fh = f[outboard_face]    # 7 wide (depth) x 2 tall
    for j in range(fh):
        for i in range(fw):
            free = i not in buried_depth
            lum = (FLANK + (RIM if j == 0 else 0) - round(FALL * ramp(j, fh))) if free else INNER
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))
    fill(img, f["west" if outboard_face == "east" else "east"], INNER)   # the inboard flank

    for face, lit in (("up", UP), ("down", DOWN)):
        x0, y0, fw, fh = f[face]         # 2 wide (x) x 7 deep
        for j in range(fh):
            for i in range(fw):
                free = i == out_col_up and j in free_rows
                put(img, x0 + i, y0 + j, (lit if free else INNER) + random.randint(-3, 3))

    # The 0.5-unit step where the bar overhangs the front and back bars is all that shows of its
    # end caps. `north` numbers its columns from min x and `south` from max x, so the free column
    # is at opposite ends of the two.
    for face, free in (("north", out_col_cap["north"]), ("south", out_col_cap["south"])):
        x0, y0, fw, fh = f[face]         # 2 wide x 2 tall
        for j in range(fh):
            for i in range(fw):
                put(img, x0 + i, y0 + j,
                    ((FLANK - 10) if i == free else INNER) + random.randint(-3, 3))


def paint_buckle(img) -> None:
    """The plate at front centre, one unit proud of the band and the only place on the front with
    room for a statement, so its 4 x 3 `north` face carries the whole idea: a lit frame, an open
    aperture, and one bright pin crossing it. At three by three there is no such thing as a subtle
    aperture - it goes to SLOT, 24, against a frame at 250, because a detail at this size is a value
    against its neighbour and the neighbour is the top-edge highlight everything else is getting.

    Four columns is exactly enough for frame, aperture, pin, frame and not one more, so the pin sits
    at column 2 and the aperture at column 1 - geo x -1..0, the same side as the punched holes on the
    band, so the strap's story runs one way rather than two."""
    size, uv = CUBES["buckle"]
    w, h, d = net(size)
    f = faces(size, uv)

    x0, y0, fw, fh = f["north"]          # 4 x 3, col 0 = min x, row 0 = top
    frame_top = [FACE + RIM + 16] * 4
    middle = [FACE - 20, SLOT, FACE + 38, FACE - 20]
    frame_bottom = [FACE - 20, FACE - 50, FACE - 50, FACE - 20]
    for j, row in enumerate((frame_top, middle, frame_bottom)):
        for i, lum in enumerate(row):
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    for face, lit in (("up", UP), ("down", DOWN)):
        x0, y0, fw, fh = f[face]         # 4 wide x 3 deep; only the front row clears the band,
                                         # which still spans z -4..-2 across the buckle's back two
        for i in range(fw):
            put(img, x0 + i, y0 + 0, INNER + random.randint(-3, 3))
            put(img, x0 + i, y0 + 1, INNER + random.randint(-3, 3))
            put(img, x0 + i, y0 + 2, lit + random.randint(-3, 3))

    # One unit proud of the band means exactly one free depth column on each flank, and `west`
    # counts from the front while `east` counts from the back.
    for name, proud in (("west", 0), ("east", 2)):
        x0, y0, fw, fh = f[name]         # 3 wide (depth) x 3 tall
        for j in range(fh):
            for i in range(fw):
                lum = (FLANK + (RIM if j == 0 else 0) - round(FALL * ramp(j, fh))) \
                    if i == proud else INNER
                put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    # The buckle's back face and the front bar's now land on the same plane, z = -2 - which is also
    # the naked body box's front wall. Three coplanar faces, and not one of them is a defect: the
    # nearest thing that can be seen there is the leggings shell at z = -2.5, a full half unit in
    # front, with the chestplate's at -3 in front of that.
    fill(img, f["south"], INNER)


def paint_knot(img) -> None:
    """The gathered wrap at the left hip. Four deep, a shade under five tall, and the only cube on
    the part that hangs below the band, which is what makes the tail read as running out of something
    rather than being glued on. The height is 4.9 rather than 5 so its underside misses the leggings
    shell's bottom cap at y = 12.5; the net is still the five rows net() rounds it up to, and every
    row below is a net row, not a geometry unit.

    A single binding at row 2 is painted at the same row index on `north`, `west`, `east` and `south`,
    so it lines up around all four corners - the horns' ring trick spent on a lashing rather than a
    groove. One is deliberate: the first cut lashed rows 1 and 3, and on a five-row face that
    alternates dark and light all the way down and reads as a stack of coins rather than a wrap. The
    bottom row is the mouth the tail emerges from and goes to SLOT, the same reading the brooch's
    keeper got.

    `east` faces back into the body: the chestplate shell is geo x = 5 and this face is at 4.25, so
    its two rearmost depth columns - the two inside the shell's own z -3..3 - are painted INNER."""
    size, uv = CUBES["knot"]
    w, h, d = net(size)
    f = faces(size, uv)
    bindings = (2,)

    x0, y0, fw, fh = f["north"]          # 3 x 5, col 0 = min x, row 0 = top
    for j in range(fh):
        for i in range(fw):
            if j == fh - 1:
                lum = SLOT + (24 if i in (0, fw - 1) else 0)
            else:
                lum = FACE - round(FALL * ramp(j, fh)) + (RIM if j == 0 else 0)
                if j in bindings:
                    lum -= BINDING
                if i == 1:
                    lum += 10            # the middle column rounds the wrap
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    # Nothing sits on top of or under the knot, so both horizontal faces are fully exposed. Both
    # brighten towards the front (row 3), which is the end that stands out of the shell - the top
    # by falling away from UP towards the back, the underside by lifting off DOWN towards the front,
    # because an underside that walked 60 down from DOWN would clamp at black and lose the jitter.
    for face, base, swing in (("up", UP, -60), ("down", DOWN, 26)):
        x0, y0, fw, fh = f[face]         # 3 wide (x) x 4 deep, rows run back to front
        for j in range(fh):
            for i in range(fw):
                t = ramp(j, fh) if swing > 0 else (1.0 - ramp(j, fh))
                lum = base + round(swing * t) + (0 if i else -18)
                put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["west"]           # +x, the outboard flank: 4 wide (depth) x 5 tall
    for j in range(fh):
        for i in range(fw):
            lum = FACE - 30 - round(FALL * ramp(j, fh)) + (RIM if j == 0 else 0) \
                - round(30 * ramp(i, fw))          # columns run front to back, into shadow
            if j in bindings:
                lum -= BINDING
            if j == fh - 1:
                lum = DOWN + 24
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["east"]           # -x, inboard: columns run BACK to front, 0 and 1 buried
    for j in range(fh):
        for i in range(fw):
            if i < 2:
                lum = INNER
            else:
                lum = FLANK - 30 - round(FALL * ramp(j, fh))
                if j in bindings:
                    lum -= BINDING
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["south"]          # the back of the knot: inside the arm sleeve at rest
    for j in range(fh):
        for i in range(fw):
            lum = DOWN + 30 - (BINDING // 2 if j in bindings else 0)
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))


def paint_tail_upper(img) -> None:
    """The strap's upper segment, on a bone at +5 degrees. Its top two rows and its whole `up` face
    are inside the knot, so of a 2 x 5 x 3 box what is ever seen is a 2 x 3 patch of front, a 2 x 3
    patch of back, three rows of each flank and one of the underside's two columns. Row 0 of the
    standing faces (geo y 10.75..11.75) is wholly inside the knot
    and row 1 (11.75..12.75) is inside it as far as the knot's underside at 12.4, two thirds of the
    way down, and both are treated as buried: the sliver that would show sits against the knot's own
    SLOT mouth, and the mouth is meant to read as one thing rather than as a strap peeking out from
    under a wrap.

    The strap trails BACKWARDS - the tail hangs off the hip at geo x 5..7, outboard of every leg
    layer, and tilting it back rather than forward keeps it inside the figure's own footprint
    instead of pushing the tip three units clear of the chest. So the front face is the lit one all
    the way down and the flanks fall away towards the back."""
    size, uv = CUBES["tail_upper"]
    w, h, d = net(size)
    f = faces(size, uv)
    buried = (0, 1)                      # rows inside the knot

    x0, y0, fw, fh = f["north"]          # 2 x 5, col 0 = min x, row 0 = top
    for j in range(fh):
        for i in range(fw):
            lum = INNER if j in buried else FACE - 12 * (j - 2) - (18 if i == 0 else 0)
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    fill(img, f["up"], INNER)            # inside the knot

    # `down` is not one flat INNER, because the segment below does not cover it. tail_end is ONE unit
    # wide against this segment's two, centred, so it takes only the middle of the underside - a
    # quarter of the inboard column and three quarters of the outboard one. Columns run min x to
    # max x and min x is inboard here, so the column that is mostly open is column 0, and it gets a
    # real underside. Column 1 stays INNER, which is also the brighter of the two and reads as light
    # bouncing off the segment butted against it.
    x0, y0, fw, fh = f["down"]           # 2 wide (x) x 3 deep
    for j in range(fh):
        put(img, x0 + 0, y0 + j, DOWN + 6 * j + random.randint(-3, 3))
        put(img, x0 + 1, y0 + j, INNER + random.randint(-3, 3))

    for name, order in (("west", (0, 1, 2)), ("east", (2, 1, 0))):
        x0, y0, fw, fh = f[name]         # 3 wide (depth) x 5 tall
        front, mid, back = order
        shade = 0 if name == "west" else 30          # the inboard flank faces the leg
        for j in range(fh):
            free = j not in buried
            base = FLANK + 10 - shade - round(FALL * ramp(j, fh))
            put(img, x0 + front, y0 + j, (base if free else INNER) + random.randint(-3, 3))
            put(img, x0 + mid, y0 + j, (base - 20 if free else INNER) + random.randint(-3, 3))
            put(img, x0 + back, y0 + j, (base - 45 if free else INNER) + random.randint(-3, 3))

    x0, y0, fw, fh = f["south"]          # the back of the strap
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j,
                (INNER if j in buried else DOWN + 30) + random.randint(-3, 3))


def paint_tail_end(img) -> None:
    """The strap's lower segment, a further +7 degrees, ending at geo y 18.73 - knee height, and the
    lowest anything on this part reaches. Its top row is buried a unit up into the segment above it,
    which is the horns' rule: a rotated joint closes by burying, not by butting.

    It is ONE unit wide against the upper segment's two, so the strap tapers as it falls, which is
    what a leather end does. What the taper costs is cross-shading: `north` and `south` are one pixel
    across, and one pixel has no inboard column to shade against an outboard one. The -18 the upper
    segment spends darkening its inboard edge would here be a flat -18 on the whole face, a dimmer
    strap dressed up as a rounded one. So the round is carried by the silhouette instead and these
    two faces are painted flat across, with all of their relief in the rows. The flanks lose nothing
    - they are still three deep, and depth is where this strap's shading lives.

    The tip is a metal ferrule and it is painted, not modelled - there is no third unit of
    projection to spend on a modelled cap, the same trade the wing roots' collar band and the
    brooch's keeper slot made. It only reads because the row above it is dropped 50 below the strap:
    a bright hem against a bright strap is not a hem."""
    size, uv = CUBES["tail_end"]
    w, h, d = net(size)
    f = faces(size, uv)
    tip = h - 1

    x0, y0, fw, fh = f["north"]          # 1 x 4, row 0 = top; one column wide, so no cross-shading
    for j in range(fh):
        for i in range(fw):
            if j == 0:
                lum = INNER              # up inside tail_upper
            elif j == tip:
                lum = FACE + FERRULE
            elif j == tip - 1:
                lum = FACE - 50          # the shadow that makes the ferrule a ferrule
            else:
                lum = FACE - 24
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    fill(img, f["up"], INNER)            # inside tail_upper

    x0, y0, fw, fh = f["down"]           # 1 wide x 3 deep, the tip's underside, fully exposed
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j, DOWN + 8 * j + random.randint(-3, 3))

    for name, order in (("west", (0, 1, 2)), ("east", (2, 1, 0))):
        x0, y0, fw, fh = f[name]         # 3 wide (depth) x 4 tall
        front, mid, back = order
        shade = 0 if name == "west" else 30
        for j in range(fh):
            if j == 0:
                for i in range(fw):
                    put(img, x0 + i, y0 + j, INNER + random.randint(-3, 3))
                continue
            base = FLANK - shade - round(FALL * ramp(j, fh))
            if j == tip:
                base = FLANK + FERRULE - shade
            elif j == tip - 1:
                base -= 40
            put(img, x0 + front, y0 + j, base + random.randint(-3, 3))
            put(img, x0 + mid, y0 + j, base - 20 + random.randint(-3, 3))
            put(img, x0 + back, y0 + j, base - 45 + random.randint(-3, 3))

    x0, y0, fw, fh = f["south"]          # the back of the strap
    for j in range(fh):
        for i in range(fw):
            if j == 0:
                lum = INNER
            elif j == tip:
                lum = DOWN + 60
            else:
                lum = DOWN + 30
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))


def check_geometry() -> None:
    """CUBES must be the cube list of the shipped geometry, in order. Painting a texture for a shape
    the model no longer has is invisible to every other check in this pipeline: both halves stay
    internally consistent while the rectangles slide off the faces they were drawn for."""
    doc = json.loads(GEO.read_text(encoding="utf-8"))
    found = []

    def walk(bone):
        for c in bone.get("cubes", []):
            found.append((tuple(c["size"]), tuple(c["uv"])))
        for child in bone.get("children", []):
            walk(child)

    for bone in doc["bones"]:
        walk(bone)

    assert (doc["texture_width"], doc["texture_height"]) == (TEX_W, TEX_H), \
        f"{GEO.name} is {doc['texture_width']}x{doc['texture_height']}, this master is {TEX_W}x{TEX_H}"
    assert found == list(CUBES.values()), \
        f"CUBES disagrees with {GEO.name}: {found} vs {list(CUBES.values())}"


def check_layout() -> None:
    """Every face rectangle must sit inside the texture and no two may overlap - a silent overlap
    would paint one cube's shading onto another's face and only show up on a model in game."""
    claimed = {}
    for name, (size, uv) in CUBES.items():
        for face, (x, y, w, h) in faces(size, uv).items():
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
    paint_front(img)
    paint_back(img)
    # The two side bars differ only in which sign of x is outboard, and that decides three things:
    # which flank face is the free one, which x column of `up`/`down` clears the shell, and which
    # end of the `north` / `south` caps overhangs the bars. `north` numbers columns from min x and
    # `south` from max x, which is why the two entries are not the same number.
    paint_side(img, "side_l", "west", 1, {"north": 1, "south": 0})
    paint_side(img, "side_r", "east", 0, {"north": 0, "south": 1})
    paint_buckle(img)
    paint_knot(img)
    paint_tail_upper(img)
    paint_tail_end(img)

    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque == set(claimed), "painted pixels do not match the UV rectangles"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)})")

    # Two fittings. Everything that is strap - the ring, the knot, the hanging tail - is the inlay
    # and takes a dye; the buckle alone is the guard and takes a metal. Between them they cover the
    # whole part, so a sash dyed and buckled shows none of its first material at all, which is the
    # point: a leather belt was never meant to be redstone.
    cloth = [rect for name, (size, uv) in CUBES.items() if name != "buckle"
             for rect in faces(size, uv).values()]
    write_mask(img, cloth, OUT.with_name("sash_inlay.png"))
    write_mask(img, faces(*CUBES["buckle"]).values(), OUT.with_name("sash_guard.png"))


if __name__ == "__main__":
    main()
