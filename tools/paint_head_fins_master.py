"""
Paint the grayscale master for the "head_fins" part, and the mask for its `inlay` fitting.

Like the pelt, puttees, greaves and tassets painters this does not merely claim that CUBES matches
the shipped geometry, it reads assets/armorpieces/armorpieces/decoration/head_fins.json at run time
and asserts it (check_geometry) - down to the origins, the pivots and the bone rotations, because on
this part the rotations ARE the fin and a master painted for an unswept fan would stay perfectly
self-consistent while describing a different object. Output goes to
tools/decoration_masters/head_fins.png and head_fins_inlay.png, which sync_decoration_masters.py
installs for the game to colour per trim material and per dye.

Master convention: luminance carries shading, alpha carries silhouette.

This master is 100% opaque. A webbed fin WANTS a punched membrane more than anything else in this
mod does, and it does not get one: parts draw with armorCutoutNoCull, so a hole cut between two rays
shows the lit INSIDE of the membrane's own far face, not the sky behind it. Every gap on this part
is geometry (the rays overhang the membrane's trailing edge, and that is a real edge) or value.

===========================================================================================
THE TIDAL IDIOM. This is the first part of the Tidal set, so this block sets the vocabulary the
Scale Skirt and the Scale Shins follow, and the three later Tidal parts should follow after them.
It is stated once, here, in full, and quoted rather than re-derived.

1. A SCALE ROW is never one cube per scale. At one texel to the unit there is no room for that, and
   a row of scale cubes would cost six faces each to draw four texels. A row is ONE cube and the
   scales are value across its face:

     * ALONG the row, a scale is TWO texels - a lit leading texel and a dimmer trailing one, which
       is the next scale lapping it. So the row reads hi, lo, hi, lo.
     * BETWEEN rows the pattern is offset by ONE texel, so the row under it reads lo, hi, lo, hi.
       The scale boundaries then stagger like brickwork and the face cannot read as a grid. This is
       the whole trick, and it is why the scale is two texels and not one: a one-texel scale with a
       one-texel stagger IS a checker, and a checker at this size is noise.
     * DOWN the rows, a falloff: a row's free lower edge is its brightest texel and its lapped upper
       edge its darkest, so the banding across a scale field is a shadow line under each lap rather
       than a ruled line.
     * Row exposures are deliberately UNEQUAL, which is the puttees' pitch finding arriving on
       scale: three rows at one pitch read as a barcode however they are shaded.

   SCALE_STEP below is that two-texel table, and `scale(col, row)` is the stagger. All three Tidal
   parts import nothing from each other - the table is copied - but the numbers are the same numbers.

2. WEBBING reads through value and relief, never through alpha. It is
     * a full step DARKER than the rays that carry it - the rays sit at the top of the part's range
       (RAY, CREST) and the membrane in its lower third (WEB_LO .. WEB_EDGE);
     * graded ALONG the span, darkest where it leaves the root and lightest at the free trailing
       edge, which is what a taut membrane does as it thins;
     * FLAT - the membrane carries a +-1 grain against the hardware's +-3, so it reads as one
       stretched surface where the rays read as worked material; and
     * physically recessed, 0.30 of a unit behind the rays on each side, because a value step alone
       does not survive a camera low enough to see the fin edge-on.

3. AN EDGE IS A LINE, NEVER A FACE. Every free edge here - a ray tip, the hem of a scale row, the
   outer lip of the gill plate - carries the part's brightest value in ONE texel, and the texel
   behind it drops to the part's mid. Cold light on something wet. Faces are lit by vanilla's
   diffuse term alone (up 1.0, down 0.5, +-z 0.8, +-x 0.6), which shades by normal and not by
   position, so a face that has to read as lit is GIVEN its value and never left to its normal.

4. THE FITTING TAKES THE FIELD; THE FRAME KEEPS THE SMITH'S METAL. A Tidal part is built as a stiff
   frame and a soft field. Here the frame is the three rays and the gill plate and the field is the
   membrane, so `armorpieces:inlay` - a dye - masks the `web` cube and nothing else. On the two
   scale parts the field is the scale rows and the frame is the binding, and `armorpieces:guard`
   takes the scales. Same sentence, three times.
===========================================================================================

What this part is, and what that costs the painter:

  * `horns` is a MIRRORED pair - Attachment.of(HEAD, 4, -5, 0) plus Attachment.mirrored at
    (-4, -5, 0) - so the layer's scale(-1, 1, 1) runs on the left-hand copy and ONE master serves
    both. `west` is geo +x, outboard on both temples; `east` is geo -x, inboard on both, and every
    `east` face of the gill plate is inside the helmet. The horns, the helm wings and the spaulders
    buy the same economy on the same terms.

  * THE HELMET IS A 1.5 SHELL ON THIS SOCKET, NOT A 1.0 ONE, and that is the one number a part
    author here can get wrong quietly. ARMOR_SLOTS["helmet"] keeps children, so createBaseArmorMesh
    emits `head` at g = 1.0 AND `hat` at g + HAT_EXTEND = 1.5 over it; the hat box is the larger of
    the two and is therefore the surface a player sees. trace_geometry excludes every hat_ box from
    its shell table, so its `past helmet` line on this socket is measured against the 1.0 shell and
    reads 0.5 generous. Every clearance quoted below is against the 1.5 hat shell instead, which in
    part-local terms is x = 1.5, y = -4.5, z = -5.5 at the front and +5.5 at the back. The shipped
    circlet makes the same choice from the brow: its band spans head-local z -6..-4 so that it
    stands 0.5 proud of the hat, not 0.5 inside it.

  * The geometry, in numbers. Part-local first (the frame the JSON is authored in, +Y DOWN), then
    head-local, which is part-local + (4, -5, 0) - the bone frame trace_geometry reports in. For
    reference in that frame the naked skull is x -4..4, y -8..0, z -4..4; the helmet's base shell is
    that box at 1.0 and its hat shell - the visible one - the same box at 1.5.

        cube        part-local x      part-local y      part-local z     head-local x
        root        1.05 ..  2.45    -1.90 ..  1.90    -1.40 ..  1.60    5.05 ..  6.45
        web         0.95 ..  3.63    -2.44 ..  2.50     0.40 ..  5.65    4.95 ..  7.63
        ray_upper   1.66 ..  4.75    -2.87 .. -1.28     0.17 ..  7.71    5.66 ..  8.75
        ray_mid     1.20 ..  3.90    -0.78 ..  0.42     0.37 ..  6.97    5.20 ..  7.90
        ray_lower   0.66 ..  3.13     1.56 ..  2.69     0.61 ..  6.31    4.66 ..  7.13

    Everything below `root` is a rotated hull, so those extents are the corners of tilted boxes and
    none of their faces is axis-aligned with anything. That is deliberate three times over, and it
    is the same argument the pelt makes on the hip: it stops a swept fin reading as a stack of
    bricks; it lets the rays sit a third of a unit off the membrane without any chance of two
    coplanar faces meeting; and the three rays' differing rotations mean no two of them are
    parallel, which is the cheapest thing that says "grown" rather than "forged".

  * The chain is root -> `sweep` -> ray. `sweep` is pivoted at part-local (1.65, 0.15, 0.30), inside
    the gill plate, and carries the WHOLE of the fin's attitude in one rotation, (6, 12, 16):
    6 degrees of lift, 12 of outboard yaw, and 16 of ROLL, which leans the fin's top edge outboard.
    The roll is what earns the part its front and back views. Without it the fin lies in the
    sagittal plane and a player looking at their own helmet sees two brackets edge-on; with it the
    pair opens into a V that reads from behind and from three-quarters, and the cost is 0.30 of
    lateral span. The three rays then carry only small rotations of their own - (3, 1.5, 0),
    (0, 1, 0), (-4, 2, 0) - off pivots 1.75 units apart in the sweep's y.

  * THE RAYS ARE THE SAME LENGTH IN NEITHER THE MODEL NOR THE NET: 7.5, 6.5 and 5.6, against a
    membrane 4.8 deep. So each ray overhangs the membrane's trailing edge - by 2.51, 1.55 and 0.65 -
    and the fin's back edge is a frayed diagonal rather than a cut. That is the whole silhouette,
    and it is why the membrane is a plain rectangle: the taper is spent on the rays, where three
    numbers buy it, instead of on a shape a cube cannot make. The first cut of this part had all
    three rays at one length and rendered as a webbed FORK.

  * WHAT CLEARS WHAT. The gill plate stands 0.95 proud of the hat shell and is buried 0.45 behind
    it, so its `east` face never draws and its outboard lip is a real edge. The fin's tip reaches
    head-local z 7.71, which is 2.21 clear of the hat shell's back wall at 5.5. Its highest point is
    head-local y -7.87 - 0.13 under the naked skull's crown and 1.63 under the helmet's - so the
    fin never breaks the helmet's own upper silhouette. It is a side fin and not a crest, by 1.63
    units, and that is deliberate: `crest` is a socket a player may already have filled.

  * THE ONE PART IT MEETS. Of the four parts that share the head bone, only the circlet reaches
    this: its `band` has a side rail at head-local x 4..6, y -6..-4, z -4..6, which runs the whole
    length of the temple at exactly the height the `horns` anchor sits at, so EVERY part on this
    socket meets it. An exact separating-axis test over the oriented boxes puts the deepest
    penetration at 0.95 (the gill plate into that rail, in x), with the membrane at 0.67 and
    `ray_mid` at 0.80; `ray_upper` clears it by 0.43 above and `ray_lower` by 0.56 below. The
    shipped horns and helm wings both drive their own boss 1.00 into the same rail, so this part is
    inside the precedent rather than setting a new one - and the plate's inboard face was moved from
    part-local 0.45 to 1.05 to make that true. Nothing else on the figure comes near: visor,
    feathering and brush_crest all return no intersecting pair at all.

  * WHAT IS ACTUALLY SEEN. The gill plate's `west` face - three columns of depth by four rows of
    height - is the part's readable mass and the one place a scale row fits, so it gets the field.
    Its `east` face is inside the helmet and its `south` face is behind the membrane's root; both
    are INNER. The membrane's `west` is the part's largest face at 25 texels and is crossed by all
    three rays, which is what its five rows are laid out around: rows 0, 2 and 4 lie under a ray and
    are painted as the shadow the ray throws, rows 1 and 3 are the two exposed bands of webbing.
    Its `east` is the same structure a step down - the fin's roll opens the inboard face to a camera
    below and behind the wearer, so it is painted rather than buried. A ray's `west` is a single row
    of six to eight texels: the ray IS a line, and it is drawn as one, climbing from RAY at the root
    to CREST at the tip. Each ray's `south` is one texel, its tip, and those three texels are the
    brightest thing on the part.

The face rectangles come from paint_circlet_master.faces(), over `net()`ed sizes the way the sash
and garters painters do it - four of this part's five cubes have a fractional dimension, and net()
rounds UP the way Blockbench does, so the 0.4-thick membrane gets one texel and the 7.5-long ray
gets eight. Row one (v .. v+d) holds up then down, each w wide, starting at u+d; row two
(v+d .. v+d+h) holds east, north, west, south with widths d, w, d, w - the two thin d-wide faces
FIRST and THIRD.

Orientation inside each rectangle is the table the greaves painter records as measured, not
recalled:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x              max z
    down            +y  (underside)      min x              max z
    west            +x  (outboard)       min z  (front)     min y (top)
    east            -x  (inboard)        max z  (back)      min y (top)
    north           -z  (front)          min x  (inboard)   min y (top)
    south           +z  (back)           max x  (outboard)  min y (top)

On every cube of this part `min z` is the root and `max z` the tip, so a `west` face reads root to
tip left to right and an `east` face reads tip to root. That reversal is why paint_ray() takes the
column index through `along()` rather than using it raw.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image

from fitting_mask import write_mask

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "head_fins.json"
OUT = ROOT / "tools" / "decoration_masters" / "head_fins.png"
INLAY = OUT.with_name("head_fins_inlay.png")

TEX_W, TEX_H = 64, 32

# size (w, h, d) and uv (u, v), mirroring head_fins.json in that file's own walk order: the root
# bone `fin` carries the gill plate, `sweep` carries the membrane, and `sweep`'s three children
# carry a ray each.
CUBES = {
    "root":      ((1.4, 3.8, 3), (12, 9)),
    "web":       ((0.4, 4.8, 4.8), (0, 9)),
    "ray_upper": ((1, 0.7, 7.5), (0, 0)),
    "ray_mid":   ((1, 0.7, 6.5), (18, 0)),
    "ray_lower": ((1, 0.7, 5.6), (34, 0)),
}

# origin, and the pivot + rotation of the bone the cube hangs from. On this part the rotations are
# the design, so they are asserted alongside the cube list rather than trusted.
PLACEMENT = {
    "root":      ((1.05, -1.9, -1.4), (0, 0, 0), (0, 0, 0)),
    "web":       ((-0.2, -2.4, 0.4), (1.65, 0.15, 0.3), (6, 12, 16)),
    "ray_upper": ((-0.5, -0.35, 0.25), (0, -1.95, 0), (3, 1.5, 0)),
    "ray_mid":   ((-0.5, -0.35, 0.25), (0, -0.2, 0), (0, 1, 0)),
    "ray_lower": ((-0.5, -0.35, 0.25), (0, 1.95, 0), (-4, 2, 0)),
}

# The fitting is a dye and it takes the membrane whole - every face of it, so no cube boundary can
# show a colour seam - while the rays and the gill plate keep the trim material. Idiom point 4.
FIELD = ("web",)

random.seed(211)  # deterministic output - regenerating must not churn the PNG

# Calibrated against the ramp, not guessed: the material ramp interpolates dark -> mid over master
# values 0..127 and mid -> light over 128..255, so a master confined to one half only ever uses half
# of a material's ramp. This part uses the whole of it, and it has to: the read is made of nothing
# but the distance between the rays and the membrane they carry.
CREST = 236     # a ray tip, and the outer lip of the gill plate - the brightest LINE on the part
RAY = 212       # a ray's outboard face
RAY_LO = 148    # a ray's inboard face, and its top ledge against the membrane
SCALE_HI = 198  # the lit leading texel of a scale
PLATE = 166     # a plate face carrying no scale field
WEB_EDGE = 168  # the membrane's free trailing edge, the one lit line the field is allowed
WEB = 132       # an exposed band of webbing at mid span
WEB_LO = 92     # webbing in the shadow of the ray that laps it
BACK = 82       # a face turned away from the light and not free
UNDER = 48      # a free underside
INNER = 28      # buried - inside the helmet, inside the gill plate, or behind the membrane

# The Tidal scale row - idiom point 1. Two texels to a scale, staggered one texel per row.
#
# The notch is deliberately SMALLER than the step between two scale rows (ROWS below steps 30, 24
# and 32; the notch is 24), and that ordering is the whole difference between a scale field and a
# checkerboard. The first cut of this part had the notch at 46 against a row step of 16 and the gill
# plate rendered as a chessboard: the eye read the alternation first and never found the rows. Rows
# first, scales second. The three steps are also unequal, which is idiom point 1's last clause -
# 30, 24, 32 rather than three of anything.
SCALE_STEP = (0, -24)   # the lit leading texel, then the lap of the scale in front of it
ROWS = (138, 168, 192, 224)  # the gill plate's four scale rows, top (most lapped) to free lower lip
FALL = 16               # per-row falloff down a standing face, away from the light
DEPTH = 22              # front-to-back falloff along a flank
GRAIN = 3               # the per-texel noise of hardware
SILK = 1                # the per-texel noise of membrane - idiom point 2, "flat"


def net(size):
    """A cube's box-UV net in whole pixels. Rounds up, the way Blockbench does - the membrane is
    0.4 thick on purpose and unwraps to one column."""
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


def rects(name):
    size, uv = CUBES[name]
    return faces(size, uv)


def scale(col: int, row: int) -> int:
    """The Tidal scale field, idiom point 1: a scale is two texels along the row, and consecutive
    rows are offset by one, so the boundaries stagger like brickwork instead of ruling a grid."""
    return SCALE_STEP[(col + row) % 2]


def put(img, x: int, y: int, lum: int, alpha: int = 255) -> None:
    if 0 <= x < TEX_W and 0 <= y < TEX_H:
        img.putpixel((x, y), (max(0, min(255, lum)), alpha))


def fill(img, rect, lum: int, jitter: int = GRAIN) -> None:
    x0, y0, w, h = rect
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            put(img, x, y, lum + random.randint(-jitter, jitter))


def ramp(i: int, n: int) -> float:
    """Position along a face axis, 0.0 at column/row 0 and 1.0 at the far end."""
    return 0.0 if n <= 1 else i / (n - 1)


def paint_root(img) -> None:
    """The gill plate: 1.4 x 3.8 x 3 at part-local x 1.05..2.45, unrotated on the root bone.

    It is the fin's mount and the part's readable mass. It stands 0.95 proud of the helmet's 1.5 hat
    shell and is buried 0.45 behind it, which is what puts its `east` face out of sight and makes
    its outboard lip a real edge rather than a seam.

    `west` is the one face on this part with room for a scale field - three columns of depth by four
    rows of height - and it gets one, because the plate is the operculum and because a Tidal set has
    to say scale somewhere on the helmet or the Skirt and the Shins are talking to themselves. The
    field is laid out per idiom point 1: two texels to a scale along the row, staggered a texel per
    row, with the bottom row lifted by HEM because it is the plate's free lower lip and the top row
    dropped because the helmet's own crown throws onto it."""
    f = rects("root")

    x0, y0, fw, fh = f["west"]           # 3 deep x 4 tall, col 0 = front, row 0 = top
    for j in range(fh):
        for i in range(fw):
            lum = ROWS[j] + scale(i, j) - round(DEPTH * ramp(i, fw))
            if i == fw - 1:
                lum -= 18                 # the membrane's root crosses the back column
            put(img, x0 + i, y0 + j, lum + random.randint(-GRAIN, GRAIN))

    x0, y0, fw, fh = f["north"]          # 2 x 4, col 0 = INBOARD, row 0 = top
    for j in range(fh):
        for i in range(fw):
            # col 0 spans part-local x 1.05..1.75 and straddles the hat shell at 1.50; col 1 is
            # 1.75..2.45 and stands clear of it, so only col 1 is ever lit.
            if i == 0:
                lum = INNER + 14
            else:
                lum = ROWS[j] - 34 + scale(i, j)
            put(img, x0 + i, y0 + j, lum + random.randint(-GRAIN, GRAIN))

    x0, y0, fw, fh = f["up"]             # 2 wide (x) x 3 deep, rows run BACK to front
    for j in range(fh):
        for i in range(fw):
            # An `up` face already renders at diffuse 1.0 against a flank's 0.6, so it is painted
            # DOWN the scale rather than up - idiom point 3, a lit face is given its value.
            lum = (PLATE - 44 if i else INNER + 10) + round(20 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + random.randint(-GRAIN, GRAIN))

    x0, y0, fw, fh = f["down"]           # 2 wide x 3 deep, rows BACK to front. Free underside.
    for j in range(fh):
        for i in range(fw):
            lum = (UNDER + 16 if i else INNER) + round(10 * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + random.randint(-GRAIN, GRAIN))

    x0, y0, fw, fh = f["south"]          # 2 x 4, col 0 = OUTBOARD; the membrane's root crosses it
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j, (BACK - 10 if i == 0 else INNER) + random.randint(-GRAIN, GRAIN))

    fill(img, f["east"], INNER)          # 0.45 inside the helmet's hat shell


def paint_web(img) -> None:
    """The membrane: 0.4 x 4.8 x 4.8 on `sweep`, which carries the fin's whole attitude at
    (6, 12, 16) off a pivot inside the gill plate.

    It is the part's largest surface - 25 texels a side - and the whole of the fitting. Its five
    rows are laid out around the three rays that cross it: the rays sit on rows 0, 2 and 4 and stand
    0.30 proud, so those rows are painted as the shadow a ray throws (WEB_LO) and only rows 1 and 3
    are exposed webbing. Two bands, not five, and they are unequal by the rays' own divergence.

    Along the span the field lifts from the root to the trailing edge: a membrane thins as it goes
    out, and idiom point 2 asks for the free edge to be the light end. It carries SILK grain, +-1,
    against the rays' +-3 - at this size the only thing separating a stretched membrane from a
    hammered plate is whether neighbouring texels agree.

    `north` is the leading edge and is inside the gill plate, so it is INNER. `south` is the free
    trailing edge between the ray overhangs and is the one lit line the field is allowed."""
    f = rects("web")

    x0, y0, fw, fh = f["west"]           # 5 deep x 5 tall, col 0 = root, row 0 = top
    for j in range(fh):
        for i in range(fw):
            lapped = j % 2 == 0          # rows 0, 2, 4 lie under ray_upper, ray_mid, ray_lower
            base = WEB_LO if lapped else WEB
            lum = base + round(26 * ramp(i, fw))
            if i == fw - 1 and not lapped:
                lum = WEB_EDGE           # the band's own free corner at the trailing edge
            put(img, x0 + i, y0 + j, lum + random.randint(-SILK, SILK))

    x0, y0, fw, fh = f["east"]           # 5 deep x 5 tall, col 0 = TIP, row 0 = top
    for j in range(fh):
        for i in range(fw):
            lapped = j % 2 == 0
            base = (WEB_LO if lapped else WEB) - 26   # the inboard face, a step under the outboard
            lum = base + round(20 * (1 - ramp(i, fw)))
            put(img, x0 + i, y0 + j, lum + random.randint(-SILK, SILK))

    x0, y0, fw, fh = f["south"]          # 1 x 5, the free trailing edge. Row 0 = top.
    for j in range(fh):
        put(img, x0, y0 + j, WEB_EDGE - round(FALL * ramp(j, fh)) + random.randint(-SILK, SILK))

    x0, y0, fw, fh = f["up"]             # 1 wide (x) x 5 deep, rows TIP to root
    for j in range(fh):
        put(img, x0, y0 + j, WEB - 22 + round(18 * (1 - ramp(j, fh))) + random.randint(-SILK, SILK))

    x0, y0, fw, fh = f["down"]           # 1 wide x 5 deep, rows TIP to root. Free underside.
    for j in range(fh):
        put(img, x0, y0 + j, UNDER + round(14 * (1 - ramp(j, fh))) + random.randint(-SILK, SILK))

    fill(img, f["north"], INNER, SILK)   # the leading edge, inside the gill plate


def paint_ray(img, key: str, root_value: int, tip_value: int, ledge: int) -> None:
    """One ray: 1 x 0.7 x L on its own bone, L being 7.5, 6.5 or 5.6.

    A ray is a LINE and it is drawn as one. Its `west` face is a single row of six to eight texels
    and it climbs the whole way from `root_value` at the gill plate to `tip_value`, so the fin reads
    brightest where it is loose. Its `south` face is one texel - the tip.

    The three rays are given three DIFFERENT tip values as well as three different roots, and that
    is not decoration: with one tip value between them the part rendered as three bright bars over a
    dark field, which is the failure this whole idiom is arranged against. The topmost ray is the
    fin's leading edge and takes CREST; the two it shelters come down 26 and 44 from it.

    The `up` ledge is where the ray meets the membrane it stands on. It is an `up` face, so vanilla
    already renders it at diffuse 1.0 against the flank's 0.6; it is therefore painted DOWN the
    scale, at `ledge`, and the topmost ray gets the higher of the two values because its ledge is
    the fin's leading edge in open air while the other two look up at the membrane above them."""
    f = rects(key)

    x0, y0, fw, fh = f["west"]           # D deep x 1 tall, col 0 = root, col fw-1 = tip
    for i in range(fw):
        lum = root_value + round((tip_value - root_value) * ramp(i, fw))
        put(img, x0 + i, y0, lum + random.randint(-GRAIN, GRAIN))

    x0, y0, fw, fh = f["east"]           # D deep x 1 tall, col 0 = TIP, col fw-1 = root
    for i in range(fw):
        lum = RAY_LO + round(34 * (1 - ramp(i, fw)))
        put(img, x0 + i, y0, lum + random.randint(-GRAIN, GRAIN))

    x0, y0, fw, fh = f["up"]             # 1 wide (x) x D deep, rows TIP to root
    for j in range(fh):
        put(img, x0, y0 + j, ledge + round(24 * (1 - ramp(j, fh))) + random.randint(-GRAIN, GRAIN))

    x0, y0, fw, fh = f["down"]           # 1 wide x D deep, rows TIP to root
    for j in range(fh):
        put(img, x0, y0 + j, UNDER + round(20 * (1 - ramp(j, fh))) + random.randint(-GRAIN, GRAIN))

    fill(img, f["south"], tip_value + 12)  # the tip: one texel, a shade over the face behind it
    fill(img, f["north"], INNER)         # the butt, inside the gill plate


def check_geometry() -> None:
    """CUBES and PLACEMENT must be the cube list, the origins and the bone frames of the shipped
    geometry, in order. Painting a texture for a shape the model no longer has is invisible to every
    other check in this pipeline: both halves stay internally consistent while the rectangles slide
    off the faces they were drawn for. The rotations are asserted with the rest because on this part
    a lost sweep would turn a swept fin back into a webbed fork without moving one texel."""
    doc = json.loads(GEO.read_text(encoding="utf-8"))
    found = []

    def walk(bone):
        pivot = tuple(bone.get("pivot", [0, 0, 0]))
        rot = tuple(bone.get("rotation", [0, 0, 0]))
        for c in bone.get("cubes", []):
            found.append(((tuple(c["size"]), tuple(c["uv"])), (tuple(c["origin"]), pivot, rot)))
        for child in bone.get("children", []):
            walk(child)

    for bone in doc["bones"]:
        walk(bone)

    assert (doc["texture_width"], doc["texture_height"]) == (TEX_W, TEX_H), \
        f"{GEO.name} is {doc['texture_width']}x{doc['texture_height']}, this master is {TEX_W}x{TEX_H}"
    assert [c for c, _ in found] == list(CUBES.values()), \
        f"CUBES disagrees with {GEO.name}: {[c for c, _ in found]} vs {list(CUBES.values())}"
    assert [p for _, p in found] == list(PLACEMENT.values()), \
        f"PLACEMENT disagrees with {GEO.name}: {[p for _, p in found]} vs {list(PLACEMENT.values())}"


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
    paint_root(img)
    paint_web(img)
    # The upper ray is the fin's leading edge in open air and starts brighter and ends on a higher
    # ledge than the two it shelters.
    paint_ray(img, "ray_upper", RAY - 34, CREST, RAY_LO)
    paint_ray(img, "ray_mid", RAY - 58, CREST - 34, RAY_LO - 30)
    paint_ray(img, "ray_lower", RAY - 76, CREST - 58, RAY_LO - 44)

    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque == set(claimed), "painted pixels do not match the UV rectangles"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)})")

    write_mask(img, [r for name in FIELD for r in rects(name).values()], INLAY)


if __name__ == "__main__":
    main()
