"""
Paint the grayscale master for the "mantle" part.

Like the brooch, sash, tassets, greaves and spaulders painters this does not merely claim that CUBES
matches the shipped geometry, it reads
assets/armorpieces/armorpieces/decoration/mantle.json at run time and asserts it (check_geometry).
Output goes to tools/decoration_masters/mantle.png and mantle_inlay.png, which
sync_decoration_masters.py installs for the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

This master is 100% opaque, and for once that is a decision rather than the default. Fur wants a
frayed edge, and the feathering established where a frayed edge may be cut: only on a cube ONE unit
thick, where the hole shows the far face, which is the same feather. Every cube here is two units or
more, so a hole cut anywhere in it would show the inside of a lock of fur - and parts draw with
armorCutoutNoCull, so it would show it lit. **The ragged hem therefore lives in the geometry, not in
the alpha**: four locks of four different lengths, on three bones at three different angles. That is
the same conclusion the feathering reached on its third cut, arrived at from the other end.

## What this part is

`mantle` is a thick fur ruff over both shoulders, on the `pauldrons` socket - the mod's second part
there, against the spaulders' hard shell. It exists to be the largest silhouette change in the mod:
the spaulders stands 0.50 units proud of the chestplate shoulder and spans 20.65 across the figure;
this stands 3.50 proud and spans 22.89.

`pauldrons` rides the ARM (Attachment.of(LEFT_ARM, 1, 0, 0) plus Attachment.mirrored on the right),
so the whole part swings with the limb and ONE master serves both shoulders through the layer's
scale(-1, 1, 1). That is also the hard constraint on the shape: nothing here may reach across to the
other shoulder or rest on the chest, because a collar, a yoke or a joining band tears apart on the
first stride. The two copies' inboard faces end up 9.5 units apart with the whole torso between
them, and every cube below is inside one arm's own frame and reads on its own.

## The cubes, in the part's frame and in the arm bone's

Part-local is the frame the geometry JSON is written in; bone-local is that plus the anchor's
(1, 0, 0), which is the frame trace_geometry prints. On the left arm, entity x = part x + 6 and
entity y = part y + 2. +Y is DOWN. Rotated cubes are given as their axis-aligned hull.

    cube       bone    size       part x          part y          part z          bone x
    ruff       ruff    6 x 4 x 7  -1.25 .. 4.75  -5.00 .. -1.00  -3.50 ..  3.50  -0.25 .. 5.75
    crown      ruff    3 x 3 x 3   1.50 .. 4.50  -6.50 .. -3.50  -0.50 ..  2.50   2.50 .. 5.50
    front_in   skirt   3 x 4 x 3  -0.34 .. 3.06  -2.74 ..  1.55  -3.25 .. -0.25   0.66 .. 4.06
    front_out  skirt   2 x 6 x 3   2.65 .. 5.26  -2.95 ..  3.22  -3.25 .. -0.25   3.65 .. 6.26
    mid        flank   4 x 3 x 2   0.34 .. 4.80  -2.34 ..  1.31  -0.75 ..  1.25   1.34 .. 5.80
    back       tail    3 x 5 x 2   1.18 .. 5.44  -2.87 ..  2.76   1.75 ..  3.75   2.18 .. 6.44

`ruff` is the mass over the shoulder and `crown` the lump raised on top of it, offset outboard and
back so the top edge breaks into steps rather than reading as one lid. The other four are the locks,
hung from three rotated bones: `skirt` at -6 degrees about Z, `flank` at -10, `tail` at -16. A
negative Z rotation carries a hanging cube's lower end toward +x, which is outboard on both
shoulders after the mirror - the same sign the spaulders' two lames use.

The angles are small on purpose. Fur hangs; it does not flare. The first cut of this part used
-8 / -13 / -24 on two-unit locks and read as three tusks, because a narrow lock that leaves the mass
at an angle reads as a horn however it is shaded. What makes the hem ragged is length and width:

    lock         hem at part y     outboard face at part x     depth
    front_in          1.55                  3.06              z -3.25 .. -0.25
    front_out         3.22                  5.26              z -3.25 .. -0.25
    mid               1.31                  4.80              z -0.75 ..  1.25
    back              2.76                  5.44              z  1.75 ..  3.75

Nearly two units of hem spread and two and a half of outboard spread, no two locks the same size,
and the ruff's own lower edge above them at -1.00 as a fifth step. front_in and front_out share the
`skirt` bone and sit side by side at the same depth, which is what puts a step in the hem where a
camera in front of the player can actually see it - the other two locks are behind that one and only
break the outline in three-quarter view.

## What clears what

The surfaces this part is measured against, in part-local coordinates:

    the arm's chestplate shell   x -3 .. 3    y -3 .. 11   z -3 .. 3
    the naked arm                x -2 .. 2    y -2 .. 10   z -2 .. 2
    the torso's chestplate shell x <= -1      y >= -3      z -3 .. 3
    the helmet shell             entity x -5 .. 5, so part x <= -1

Four numbers decide the whole part:

  * **y = -3 is the shoulder line** - the top of both chestplate shells. Everything above it is seen;
    everything below it, inside |x| < 3 and |z| < 3, is inside the sleeve and is painted INNER. The
    ruff's top is at -5.00 and the crown's at -6.50, so the part stands 2.00 and 3.50 proud.

  * **x = 3 is the sleeve's outboard wall.** The ruff reaches 4.75 and the locks 3.06 .. 5.44, so
    the hanging half of this part is outside the sleeve where it matters and buried where it is not:
    every lock spends its inboard end inside the chestplate, which is what makes a lock come out of
    the arm rather than off it. front_in is the extreme case and is deliberate - it reaches inboard
    to -0.34, almost the ruff's own -1.25, and nearly all of that is inside the sleeve. It is there
    for the FRONT view alone, where its face at z = -3.25 stands a quarter unit outside the shell's
    front wall and so is seen whole: without it the mass narrowed by half the moment it stopped
    being ruff and started being lock.

  * **x = -1 is the torso shell's wall**, and the ruff's inboard face stops at -1.25 - a quarter unit
    INSIDE it. That burial is deliberate: below the shoulder line it closes the seam between the
    ruff and the chest, and above it the same quarter unit hides under the helmet skirt (which
    reaches part x -1 too) rather than lying on it, which would z-fight. It does not reach the naked
    head, which stops at part x -2.

  * **z = +-3 are the shell's front and back walls**, and the ruff spans -3.50 .. 3.50, so it stands
    half a unit proud at both - the spaulders' cap makes exactly the same choice, and it is what
    stops a shoulder part reading as a decal on the sleeve.

Cross-socket, on the same arm bone, trace_geometry reports the vambraces and the mittens clear by
more than half a unit: the longest lock ends at bone y 3.22 and the bracer starts at 4.00. The three
sockets that could have fouled this one draw on the BODY bone, so no tool compares them and they
were measured by hand:

  * `collar`'s **gorget** puts a shoulder tab at entity x 4.5 .. 6.5, y -1.25 .. 1.75, and the ruff
    runs through it at entity x 4.75 .. 10.75, y -3.00 .. 1.00. All but a quarter unit of that tab is
    inside the arm's chestplate shell and invisible, and no face of either part lies in a plane of
    the other, so the interpenetration is occlusion and not a z-fight: the fur sits over the tab. The
    shipped spaulders already laps the same tab by 0.75 x 0.75 x 4.00.
  * `back`'s **pinions** reach entity x 6.4 on their vanes, but the vane's outboard edge is at
    z >= 4.86 there; the mantle's deepest face is z = 3.75, so they clear by 1.1. **wing_roots**
    reach entity x 4.53 but only over y 2.5 .. 9.5, and the mantle's inboard cube is the ruff, which
    ends at entity y 1.00. **banner** stays inside entity x +-3.5.

One thing this part does NOT clear, and cannot: a turned head. The helmet shell is entity y -9 .. 1,
which is the whole of the ruff's own y span, and at the 50 degrees vanilla lets the head lead the
body its back corner sweeps out to entity x 7.04 - a unit and a half inside the ruff. At rest the two
touch by the deliberate quarter unit and no more. This is the vanilla behaviour a yawed helmet
already has against the chestplate's own shoulders, and it is why the crown was moved outboard to
entity x 7.50 .. 10.50: the tall half of the part is now clear of the sweep even if the wide half
cannot be.

No two faces of this part share a plane, and the z table above is what that costs: ruff at -3.50 and
3.50, crown at -0.50 and 2.50, the two front locks at -3.25 and -0.25, mid at -0.75 and 1.25, back at
1.75 and 3.75. It is worth keeping, because two coplanar opaque faces of the SAME part z-fight
exactly as a part and a shell do, and neither one is hiding the other. The one pair of coincident
faces left is front_in's `west` against front_out's `east` at skirt-local x = 0, where the two locks
touch: that plane is enclosed by solid geometry on both sides over every row they share, so it is
never drawn against sky, and both are painted INNER.

## Why the master is shaped the way it is

Fur reads through silhouette and value. It does not read through detail: at three texels across a
lock there is no room for a hair, and anything regular enough to be a pattern reads as basketwork.
So this master has exactly three ideas in it and no fourth:

  1. **Strands.** Every standing face gets a per-COLUMN tone offset, +-44, laid down in runs of one
     to three columns and forced two thirds of an amplitude apart from the run before it, then
     BROKEN once down each column at a row of its own choosing. Runs rather than per-pixel noise,
     because noise at this scale averages back to a flat face at any distance a player actually sees
     a shoulder from, and a strand only exists because its neighbour is a different value. Broken
     rather than constant, because a column of one flat value reads as a stripe; a column that
     changes where its neighbour does not reads as a lock of hair ending. Both amplitudes were tuned
     against the render rather than chosen: at +-54 with a half-amplitude break, whole columns of a
     three-wide face went to 51 against a neighbour at 234 and read as a gap torn in the part.

  2. **Clumps.** The two faces seen from above - the ruff's `up` and the crown's `up`, 42 and 9
     texels, the largest unbroken areas on the part - take a field of soft blobs instead, seven and
     four of them, each a signed cone of radius 1.1 .. 2.0 texels. A top face has no hanging
     direction to organise it, so the strand rule would give it stripes; blobs give it lumps.

  3. **A broken hem.** The last row of every lock is lit by TIP on about half its columns, chosen
     per lock, and the un-lit ones are dropped instead. A highlight on every column of a bottom row
     is a hem; a highlight on half of them is fur. The ruff's own lower edge takes the same
     treatment on `north` and `south`, which is what keeps the one long straight edge on the part
     from reading as a cut. The row above a hem carries no highlight at all, so the lit texels have
     something to sit against.

Under all three is the ordinary standing-figure key the spaulders and the tassets use - lit from
above, from the front and from outboard - plus one shape-specific value: **SHELF**, the shadow the
ruff throws on the lock hanging out from under it. Row 0 of every lock is buried in the ruff and row
1 is the row the ruff's underside crosses. That was measured on each lock's outboard face rather
than assumed: the ruff's bottom at part y = -1 falls at dy 0.75 on front_in, 0.96 on front_out, 0.86
on mid and 0.95 on back, which is row 1 in all four cases. Without SHELF the locks and the ruff are
one continuous value and the mass reads as a single slab; with it the ruff sits ON the locks, which
is the whole reason the shape is built in pieces rather than as one tall box.

Value calibration, the same one every master here is held to: the material ramp interpolates
dark -> mid over master values 0 .. 127 and mid -> light over 128 .. 255, so a master confined to the
top half only ever uses half of a material's ramp. Here the crown's lit blobs and the hem's tips
saturate while the undersides, the inboard face and the shelf rows sit well under 127, so the
VISIBLE texels alone span the whole ramp - the line main() prints at the end is that range.

## The fitting

One fitting, `armorpieces:inlay`, and it covers the entire part. That is the sash's argument, and it
applies here more plainly than it does there: a leather belt was never meant to be redstone, and a
pelt was never meant to be diamond either. There is no hardware on this part to keep the trim
material - no buckle, no clasp, no strap - because every one of those would have been a detail at a
scale that cannot hold a detail, and because the brief for the shape was mass and outline. So the
mask is the master, and the choice a player gets is: leave the inlay empty and the fur takes the
trim material's own palette (a gold mantle is a tawny pelt, a diamond one a frost-white one), or dye
it and get the sixteen, which is the only way in the mod to get a plainly brown one. There is
deliberately no `_static.png`: a static layer would fix the fur's own colour, and the part would
then look identical in all sixteen materials - the one thing a decoration in this mod must not do.

## The unwrap

The face rectangles come from paint_circlet_master.faces(), copied verbatim: row one (v .. v+d) holds
up then down, each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west, south
with widths d, w, d, w. Note the row-two order: the two thin d-wide faces come FIRST and THIRD.

Orientation inside each rectangle is the table PLAN.md records as measured, not recalled:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x              max z
    down            +y  (underside)      min x              max z
    west            +x  (outboard)       min z  (front)     min y (top)
    east            -x  (inboard)        max z  (back)      min y (top)
    north           -z  (front)          min x  (inboard)   min y (top)
    south           +z  (back)           max x  (outboard)  min y (top)

Blockbench's `west` is the geo +x face - the one pointing away from the body for a left-side part -
and `east` is the one against the chest. That is what lets one master serve both shoulders: after the
layer's scale(-1, 1, 1) the geo +x face of the mirrored copy still points outboard, so
lit-outboard / shadowed-inboard survives the mirror and the pair reads as a pair.
"""

from __future__ import annotations

import json
import math
import random
import zlib
from pathlib import Path

from PIL import Image

from fitting_mask import write_mask

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "mantle.json"
OUT = ROOT / "tools" / "decoration_masters" / "mantle.png"

TEX_W, TEX_H = 64, 32

# size (w, h, d) and uv (u, v), mirroring mantle.json in that file's own order: the ruff over the
# shoulder, the crown lump raised outboard and back on top of it, then the four locks - two side by
# side on `skirt`, one on `flank`, one on `tail`. Their placed extents are in the module docstring.
CUBES = {
    "ruff":      ((6, 4, 7), (0, 0)),
    "crown":     ((3, 3, 3), (26, 0)),
    "front_in":  ((3, 4, 3), (38, 0)),
    "front_out": ((2, 6, 3), (50, 0)),
    "mid":       ((4, 3, 2), (0, 11)),
    "back":      ((3, 5, 2), (12, 11)),
}

SEED = 0x4655522A  # deterministic output - regenerating must not churn the PNG

# The standing-figure key: lit from above, from the front, and from outboard.
CROWN = 240     # the crown's top - the highest surface on the part, and the one seen from anywhere
UP = 216        # the ruff's top
WEST = 180      # outboard, away from the body - the hero face
NORTH = 152     # the front
SOUTH = 118     # the back
EAST = 72       # inboard, in the slot between the ruff and the neck
DOWN = 44       # a free underside
INNER = 64      # buried - in the ruff, in the sleeve, or in the torso shell

STRAND = 44     # peak of the per-column strand tone on a standing face
CLUMP = 46      # peak of the blob field on a top face
SHELF = 44      # the shadow the ruff throws on the row where a lock leaves it
TIP = 34        # the light a strand's last row takes, on about half its columns
FALL = 10       # top-to-bottom falloff down a standing face
DEPTH = 24      # front-to-back falloff across a flank
GAIN = 18       # inboard-to-outboard brightening across a face's width


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


def put(img, x: int, y: int, lum: int, alpha: int = 255) -> None:
    if 0 <= x < TEX_W and 0 <= y < TEX_H:
        img.putpixel((x, y), (max(0, min(255, lum)), alpha))


def ramp(i: int, n: int) -> float:
    """Position along a face axis, 0.0 at column/row 0 and 1.0 at the far end."""
    return 0.0 if n <= 1 else i / (n - 1)


def rng_for(key: str) -> random.Random:
    """A generator keyed by name rather than by call order.

    The other painters here draw from one seeded stream, which is fine for them and means that
    re-ordering their paint calls re-rolls the whole sheet. This part is six cubes of noise and was
    tuned face by face, so every face gets its own stream: adding a highlight to the crown must not
    move a single texel of the locks. crc32 rather than hash(), because hash() of a str is salted
    per process and would make the output different on every run."""
    return random.Random(SEED ^ zlib.crc32(key.encode("utf-8")))


def fill(img, rect, lum: int, jitter: int = 3) -> None:
    x0, y0, w, h = rect
    rng = rng_for(f"fill:{rect}")
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            put(img, x, y, lum + rng.randint(-jitter, jitter))


def strands(key: str, n: int, amp: int = STRAND) -> list[int]:
    """Per-column tone offsets, in runs of one to three columns.

    A run is a lock of hair, so consecutive runs are forced two thirds of an amplitude apart: a
    strand exists only because its neighbour is a different value, and a random walk that happens to
    pick two similar values in a row leaves a flat patch exactly where the eye is looking."""
    rng = rng_for("strand:" + key)
    out: list[int] = []
    previous = 0
    while len(out) < n:
        tone = rng.randint(-amp, amp)
        for _ in range(8):
            if abs(tone - previous) >= (amp * 2) // 3:
                break
            tone = rng.randint(-amp, amp)
        previous = tone
        out.extend([tone] * rng.choice((1, 1, 2, 2, 3)))
    return out[:n]


def strand_field(key: str, w: int, h: int, amp: int = STRAND) -> dict[tuple[int, int], int]:
    """`strands` across the columns, then broken once down each column at a row of its own.

    The break is what stops the face reading as a bar code. Each column picks its own cut row and
    its own signed step, so where one strand ends its neighbour carries on - which is the whole
    difference between a pelt and a stack of planks at four texels tall."""
    base = strands(key, w, amp)
    rng = rng_for("break:" + key)
    field = {}
    for i in range(w):
        cut = rng.randrange(1, h) if h > 1 else h
        step = rng.choice((-1, 1)) * rng.randint(amp // 4, amp // 2)
        for j in range(h):
            field[(i, j)] = base[i] + (0 if j < cut else step)
    return field


def tipped(key: str, n: int, fraction: float = 0.55) -> list[bool]:
    """Which columns of a hem carry a lit tip. Never all of them - see the module docstring."""
    rng = rng_for("tip:" + key)
    picks = [rng.random() < fraction for _ in range(n)]
    if n > 1 and all(picks):
        picks[rng.randrange(n)] = False
    if not any(picks):
        picks[rng.randrange(n)] = True
    return picks


def blobs(key: str, w: int, h: int, count: int, amp: int = CLUMP) -> dict[tuple[int, int], int]:
    """A field of signed cones over a top face - fur seen from above is lumps, not a gradient."""
    rng = rng_for("blob:" + key)
    centres = [(rng.uniform(-0.5, w - 0.5), rng.uniform(-0.5, h - 0.5),
                rng.choice((-1.0, 1.0)) * rng.uniform(0.6, 1.0), rng.uniform(1.1, 2.0))
               for _ in range(count)]
    field = {}
    for j in range(h):
        for i in range(w):
            value = 0.0
            for cx, cy, sign, radius in centres:
                distance = math.hypot(i - cx, j - cy)
                if distance < radius:
                    value += sign * (1.0 - distance / radius) ** 2
            field[(i, j)] = round(amp * max(-1.0, min(1.0, value)))
    return field


# ---- the ruff ------------------------------------------------------------------------------------

# The crown's footprint on the ruff's `up` face, worked out from the two cubes rather than eyeballed.
# `up` runs 6 columns of x (column i spans part x -1.25+i .. -0.25+i) and 7 rows of z back to front
# (row j spans z 2.5-j .. 3.5-j). The crown covers x 1.50 .. 4.50 and z -0.50 .. 2.50, so columns
# 3 and 4 and rows 1, 2, 3 are wholly under it, and columns 2 and 5 are the two it half covers -
# which is why the contact shadow below runs 2 .. 5 and not 3 .. 4.
CROWN_COLS = (3, 4)
CROWN_ROWS = (1, 2, 3)


def under_crown(i: int, j: int) -> bool:
    return i in CROWN_COLS and j in CROWN_ROWS


def crown_shadow(i: int, j: int) -> bool:
    """The ring of texels the crown's own contact shadow falls on, one out from its footprint."""
    return 2 <= i <= 5 and 0 <= j <= 4 and not under_crown(i, j)


def paint_ruff(img) -> None:
    """The mass over the shoulder: 6 x 4 x 7, standing 2.00 units proud of the shoulder line and
    half a unit proud of the shell at the front and the back.

    Its `up` is the largest face on the part and the one a player sees from any camera angle at all,
    so it takes the blob field. Its `west`, `north` and `south` are all outside their shells and are
    painted as real faces down to the last row; `east` and `down` are the two that are mostly
    buried, and are the only two with INNER in them."""
    size, uv = CUBES["ruff"]
    w, h, d = size
    f = faces(size, uv)

    x0, y0, fw, fh = f["up"]              # 6 wide (x) x 7 deep, row 0 = back
    field = blobs("ruff.up", fw, fh, 7)
    rng = rng_for("ruff.up")
    for j in range(fh):
        for i in range(fw):
            if under_crown(i, j):
                lum = INNER
            else:
                lum = UP + field[(i, j)] \
                    - round(DEPTH * 0.4 * (1.0 - ramp(j, fh))) \
                    - round(GAIN * (1.0 - ramp(i, fw)))
                if crown_shadow(i, j):
                    lum -= 30            # the crown's contact shadow - it is what raises the crown
            put(img, x0 + i, y0 + j, lum + rng.randint(-3, 3))

    x0, y0, fw, fh = f["west"]           # 7 deep x 4 tall, col 0 = front, row 0 = top. All seen.
    field = strand_field("ruff.west", fw, fh)
    rng = rng_for("ruff.west")
    for j in range(fh):
        for i in range(fw):
            lum = WEST + field[(i, j)] - round(DEPTH * ramp(i, fw)) - round(FALL * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + rng.randint(-4, 4))

    x0, y0, fw, fh = f["north"]          # 6 wide x 4 tall, col 0 = inboard. Half a unit proud.
    field = strand_field("ruff.north", fw, fh)
    tips = tipped("ruff.north", fw)
    rng = rng_for("ruff.north")
    for j in range(fh):
        for i in range(fw):
            lum = NORTH + field[(i, j)] + round(GAIN * ramp(i, fw)) - round(FALL * ramp(j, fh))
            if j == fh - 1:
                lum += 18 if tips[i] else -16   # the pelt's cut lower edge, broken like a hem
            put(img, x0 + i, y0 + j, lum + rng.randint(-4, 4))

    x0, y0, fw, fh = f["south"]          # 6 wide x 4 tall, col 0 = OUTBOARD
    field = strand_field("ruff.south", fw, fh)
    tips = tipped("ruff.south", fw)
    rng = rng_for("ruff.south")
    for j in range(fh):
        for i in range(fw):
            lum = SOUTH + field[(i, j)] + round(GAIN * (1.0 - ramp(i, fw))) \
                - round(FALL * ramp(j, fh))
            if j == fh - 1:
                lum += 18 if tips[i] else -16
            put(img, x0 + i, y0 + j, lum + rng.randint(-4, 4))

    # `east` is 7 deep x 4 tall, col 0 = BACK. Rows 0 and 1 are the two above the shoulder line and
    # are seen beside the neck; rows 2 and 3 are inside the torso shell except at the two end
    # columns, which straddle its z walls at +-3 and keep half a texel in the open.
    x0, y0, fw, fh = f["east"]
    field = strand_field("ruff.east", fw, fh, STRAND // 2)
    rng = rng_for("ruff.east")
    for j in range(fh):
        for i in range(fw):
            free = j < 2 or i in (0, fw - 1)
            lum = (EAST + field[(i, j)] + round(14 * ramp(i, fw)) - round(FALL * ramp(j, fh))
                   - (0 if j < 2 else 16)) if free else INNER
            put(img, x0 + i, y0 + j, lum + rng.randint(-3, 3))

    # `down` is 6 wide (x) x 7 deep, rows back to front. Column 5 is the one outside the sleeve's
    # x = 3 wall, and rows 0 and 6 straddle its z walls; everything else is inside the sleeve, and
    # most of what is not is behind a lock anyway.
    x0, y0, fw, fh = f["down"]
    rng = rng_for("ruff.down")
    for j in range(fh):
        for i in range(fw):
            free = i == fw - 1 or j in (0, fh - 1)
            lum = (DOWN + round(14 * ramp(i, fw))) if free else INNER
            put(img, x0 + i, y0 + j, lum + rng.randint(-3, 3))


def paint_crown(img) -> None:
    """The lump raised on the ruff, offset back and outboard of it: 3 x 3 x 3 at part x 1.50 .. 4.50,
    buried 1.50 units into the ruff so the joint is closed, standing 3.50 units proud of the
    shoulder line.

    It exists for the outline. A single slab over the shoulder is a slab from every angle; a second
    mass offset out of line with the first breaks the top edge into three steps - 2.75 units of ruff
    inboard of it, the crown, then a quarter unit of ruff outboard - which is what separates a fur
    ruff from a pauldron at a hundred blocks. Being outboard also puts it at entity x 7.50 .. 10.50,
    clear of the arc a turned helmet sweeps, which the ruff underneath it cannot be."""
    size, uv = CUBES["crown"]
    w, h, d = size
    f = faces(size, uv)

    x0, y0, fw, fh = f["up"]             # 3 wide x 3 deep, row 0 = back. The brightest face here.
    field = blobs("crown.up", fw, fh, 4)
    rng = rng_for("crown.up")
    for j in range(fh):
        for i in range(fw):
            lum = CROWN + field[(i, j)] - round(GAIN * 0.6 * (1.0 - ramp(i, fw)))
            put(img, x0 + i, y0 + j, lum + rng.randint(-3, 3))

    for name, base in (("west", WEST + 16), ("north", NORTH + 12),
                       ("south", SOUTH + 12), ("east", EAST + 12)):
        x0, y0, fw, fh = f[name]
        tone = strands("crown." + name, fw)
        rng = rng_for("crown." + name)
        for j in range(fh):
            for i in range(fw):
                # Row 0 stands clear above the ruff; row 1 is the one the ruff's top at y = -5
                # cuts through, so half of it is seen and it is dropped rather than buried; row 2
                # is inside the ruff.
                if j == 0:
                    lum = base + tone[i]
                elif j == 1:
                    lum = base + tone[i] // 2 - 26
                else:
                    lum = INNER
                put(img, x0 + i, y0 + j, lum + rng.randint(-3, 3))

    fill(img, f["down"], INNER)          # inside the ruff


# ---- the four locks -----------------------------------------------------------------------------

# Per lock: the base value its `north` and `south` take, and which part of its `east` face clears
# something. `east` faces the sleeve from a quarter to two units inside it, so almost none of it is
# ever seen; the exceptions are named here as (which columns, from which row):
#   front_in   its front depth column crosses the shell wall at z = -3
#   front_out  its whole face below row 4, which is where front_in beside it has ended
#   mid        nothing - it lies wholly between z = -3 and z = +3 and inboard of x = 3
#   back       its back depth column crosses the shell wall at z = +3
# `north` and `south` are dropped on the faces a neighbouring lock stands in front of: mid overlaps
# the front pair over z -0.75 .. -0.25 and is inside it there, and back's `north` looks across a
# half-unit slot at mid's back. The three a camera reaches squarely are the front pair's `north`
# (at z = -3.25, a quarter unit outside the shell's front wall) and back's `south` (at z = 3.75, a
# quarter unit outside the ruff's own back face).
LOCKS = {
    "front_in":  {"north": NORTH + 8, "south": SOUTH - 24, "east": ("front", 2)},
    "front_out": {"north": NORTH + 8, "south": SOUTH - 24, "east": ("all", 4)},
    "mid":       {"north": NORTH - 26, "south": SOUTH - 16, "east": (None, 0)},
    "back":      {"north": NORTH - 16, "south": SOUTH + 6, "east": ("back", 2)},
}


def paint_lock(img, name: str) -> None:
    """One hanging lock. Row 0 is inside the ruff, row 1 is the row the ruff's underside crosses and
    takes SHELF, and the rows below it are the fur that is actually seen. The last row is the hem and
    is lit on about half its columns.

    A lock is two to four units wide and spends its inboard end inside the chestplate: the sleeve's
    outboard wall is at part x = 3 and these hang from x -0.34 .. 5.44. That buried end is not waste
    - it is what makes the lock come out of the arm rather than off it."""
    size, uv = CUBES[name]
    w, h, d = size
    f = faces(size, uv)
    spec = LOCKS[name]
    hem = h - 1

    def hang(base: int, field, i: int, j: int, tips: list[bool]) -> int:
        """One texel of a standing face on a lock, given its row's place in the hang."""
        if j == 0:
            return INNER                                   # inside the ruff
        if j == 1:
            return base + field[(i, j)] // 2 - SHELF       # the ruff's underside crosses this row
        lum = base + field[(i, j)] - round(FALL * 0.5 * ramp(j - 1, h - 1))
        if j == hem:
            lum += TIP if tips[i] else -18
        return lum

    x0, y0, fw, fh = f["west"]           # d cols of z (0 = front) x h rows. The hero face.
    field = strand_field(name + ".west", fw, fh)
    tips = tipped(name + ".west", fw)
    rng = rng_for(name + ".west")
    for j in range(fh):
        for i in range(fw):
            lum = hang(WEST, field, i, j, tips)
            if j > 1:
                lum -= round(DEPTH * 0.5 * ramp(i, fw))
            put(img, x0 + i, y0 + j, lum + rng.randint(-4, 4))

    for face, base, outward in (("north", spec["north"], True), ("south", spec["south"], False)):
        x0, y0, fw, fh = f[face]         # w cols of x x h rows; north counts inboard -> outboard
        field = strand_field(f"{name}.{face}", fw, fh)
        tips = tipped(f"{name}.{face}", fw)
        rng = rng_for(f"{name}.{face}")
        for j in range(fh):
            for i in range(fw):
                lum = hang(base, field, i, j, tips)
                if j > 1:
                    lum += round(GAIN * 0.5 * (ramp(i, fw) if outward else 1.0 - ramp(i, fw)))
                put(img, x0 + i, y0 + j, lum + rng.randint(-4, 4))

    # `east` is against the sleeve; LOCKS says which of it, if any, clears something. `east` counts
    # its columns BACK to front, so the front depth column is the LAST and the back one the FIRST.
    x0, y0, fw, fh = f["east"]
    where, from_row = spec["east"]
    tone = strands(name + ".east", fw, STRAND // 2)
    rng = rng_for(name + ".east")
    for j in range(fh):
        for i in range(fw):
            free = j >= from_row and (where == "all"
                                      or (where == "front" and i == fw - 1)
                                      or (where == "back" and i == 0))
            lum = (EAST + tone[i] - round(FALL * ramp(j, fh))) if free else INNER
            put(img, x0 + i, y0 + j, lum + rng.randint(-3, 3))

    fill(img, f["up"], INNER)            # inside the ruff

    x0, y0, fw, fh = f["down"]           # w wide (x) x d deep, rows back to front. The hem's sole.
    tone = strands(name + ".down", fw, STRAND // 2)
    rng = rng_for(name + ".down")
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j,
                DOWN + tone[i] // 2 + round(16 * ramp(j, fh)) + rng.randint(-3, 3))


# ---- checks -------------------------------------------------------------------------------------


def check_geometry() -> None:
    """CUBES must be the cube list of the shipped geometry, in order. Painting a texture for a shape
    the model no longer has is invisible to every other check in this pipeline: both halves stay
    internally consistent while the rectangles slide off the faces they were drawn for."""
    doc = json.loads(GEO.read_text(encoding="utf-8"))
    found = []
    origins = []

    def walk(bone):
        for c in bone.get("cubes", []):
            found.append((tuple(c["size"]), tuple(c["uv"])))
            origins.append(tuple(c["origin"]))
        for child in bone.get("children", []):
            walk(child)

    for bone in doc["bones"]:
        walk(bone)

    assert (doc["texture_width"], doc["texture_height"]) == (TEX_W, TEX_H), \
        f"{GEO.name} is {doc['texture_width']}x{doc['texture_height']}, this master is {TEX_W}x{TEX_H}"
    assert found == list(CUBES.values()), \
        f"CUBES disagrees with {GEO.name}: {found} vs {list(CUBES.values())}"

    # Two origins carry meaning the paint code reads off directly and would not notice losing.
    # The ruff's y decides where the shoulder line falls inside its faces, and the crown's x and z
    # decide which texels of the ruff's `up` face are under it (CROWN_COLS / CROWN_ROWS).
    assert origins[0] == (-1.25, -5, -3.5), \
        f"the ruff has moved to {origins[0]} - the shoulder line is no longer 2.00 below its top"
    assert origins[1] == (1.5, -6.5, -0.5), \
        f"the crown has moved to {origins[1]} - CROWN_COLS / CROWN_ROWS no longer name its footprint"


def check_layout() -> dict:
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
    paint_ruff(img)
    paint_crown(img)
    for lock in LOCKS:
        paint_lock(img, lock)

    # This master is 100% opaque - the hem is ragged in the geometry, not in the alpha - so the
    # painted set must be exactly the net: a texel short is a face the model shows and the texture
    # does not, and a texel over is paint the model never samples.
    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque == set(claimed), "painted pixels do not match the UV rectangles"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)})")

    # One fitting, and it is the whole part: there is no hardware on a pelt. See the module
    # docstring for why this part ships no static layer either.
    every = [rect for size, uv in CUBES.values() for rect in faces(size, uv).values()]
    write_mask(img, every, OUT.with_name("mantle_inlay.png"))


if __name__ == "__main__":
    main()
