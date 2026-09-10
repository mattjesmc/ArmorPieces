"""
Paint the grayscale master for the "scale_shins" part, and the mask for its `guard` fitting.

Like the pelt, puttees, greaves and tassets painters this does not merely claim that CUBES matches
the shipped geometry, it reads assets/armorpieces/armorpieces/decoration/scale_shins.json at run
time and asserts it (check_geometry) - down to the origins, the pivots and the four bone rotations,
because on this part the origins are the lap and the rotations are what lifts each row's lower edge
off the shin. Output goes to tools/decoration_masters/scale_shins.png and scale_shins_guard.png,
which sync_decoration_masters.py installs for the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

This master is 100% opaque, for the greaves' and the pelt's reason. A scalloped scale edge is
exactly what this part wants and it does not get one: parts draw with armorCutoutNoCull, so a notch
cut in the front face of a row shows the lit INSIDE of that row's back face, not the boot behind it.
The scalloping here is the geometry's own overhang and the value under it.

===========================================================================================
THE TIDAL IDIOM, as head_fins sets it and scale_skirt carries it onto scale. Quoted, not
re-derived - see paint_head_fins_master.py for the full statement. The three clauses this part is
built out of, and THE NUMBERS ARE THE SKIRT'S NUMBERS: SCALE_STEP, LAP and FREE below are the same
three values paint_scale_skirt_master.py uses, deliberately, because the two parts have to read as
one set worn together on adjacent sockets.

1. A SCALE ROW is one cube, and the scales are value across its face. Along the row a scale is TWO
   texels, a lit leading one and the dimmer one the next scale laps; between rows the pattern is
   offset by ONE texel so the boundaries stagger like brickwork; and the notch (34) is smaller than
   the step between a lapped row and a free one (66), so the eye reads rows first and scales second.

   THE SAME LOGIC AT A DIFFERENT SCALE, which is the whole reason this part and the skirt exist as a
   pair. A texel on the skirt covers 0.875 x 0.99 model units; a texel here covers 0.84 x 0.80. The
   scales on the shin are a fifth shorter than the scales on the hip, and nothing else about them
   changes - same two-texel scale, same one-texel stagger, same notch, same LAP and FREE. Scale is
   bought with the CUBE's size against its net, never with the shading.

2. AN EDGE IS A LINE, NEVER A FACE. The skirt's lit line is the vertical corner where the thigh
   turns from front to flank. This part has no such corner to spend - see below, the boot buries
   both flanks - so its line is horizontal instead: the free lower texel row of the bottom scale
   row, at the ankle, painted at EDGE and nothing else on the part allowed near it.

3. THE FITTING TAKES THE FIELD; THE FRAME KEEPS THE SMITH'S METAL. The field is the three scale
   rows and the frame is the `band` at the knee that they hang from, so `armorpieces:guard` - a
   second trim material - masks row1, row2 and row3 and leaves the band alone. Exactly the skirt's
   split, on exactly the same fitting, which is what lets a player set the two to the same metal and
   have them agree.
===========================================================================================

What this part is, and what that costs the painter:

  * `greaves` is a MIRRORED pair - Attachment.of(LEFT_LEG, 0, 8, -2) plus Attachment.mirrored on the
    right - so the layer's scale(-1, 1, 1) runs on the right-hand copy and ONE master serves both.
    `west` is geo +x, outboard on both legs; `east` is geo -x, inboard on both.

  * THE LEG SHELLS ARE 0.4 AND 0.9, NOT 0.5 AND 1.0. createBaseArmorMesh re-adds both legs at
    g.extend(-0.1F), so the BOOTS shell - the outer one down here, and the one that matters - is
    leg-local x -2.9..2.9, y -0.9..12.9, z -2.9..2.9, and the leggings' is the same box at 0.4. Two
    shipped painters still carry the old +-2.5 and are wrong; every number below is against 2.9.

  * THIS PART IS FRONT-ONLY, AND THAT IS THE BOOT'S DOING. The skirt one socket up wraps the thigh's
    front-outer corner and spends eight columns of scale on it. Here the boot is inflated 0.9 rather
    than the leggings' 0.4, so its outboard wall stands at leg-local x 2.9 - half a unit further out
    than the thigh's - and anything reaching past it runs into the shipped garters, which hang at
    x 2.85..4.05 down to leg-local y 8.20. So there is no flank to have: the widest cube here is the
    band at x 2.50, which is 0.40 INSIDE the boot. `west` and `east` are painted as the buried faces
    they are, the shipped greaves makes the same choice at x 2.60, and the whole read is `north`,
    five columns across the shin, plus the shadow under each row.

  * The geometry, in numbers. Part-local first (the frame the JSON is authored in, +Y DOWN), then
    leg-local, which is part-local + (0, 8, -2) - the bone frame trace_geometry reports in.

        cube    part-local x      part-local y      part-local z    leg-local y      leg-local z
        band   -1.90 .. 2.50    -0.62 ..  0.63    -1.82 .. 1.25    7.38 ..  8.63   -3.82 .. -0.75
        row1   -1.90 .. 2.30     0.08 ..  1.98    -1.76 .. 1.29    8.08 ..  9.98   -3.76 .. -0.71
        row2   -1.90 .. 2.30     1.35 ..  3.34    -1.66 .. 1.44    9.35 .. 11.34   -3.66 .. -0.56
        row3   -1.90 .. 2.30     2.79 ..  4.73    -1.49 .. 1.59   10.79 .. 12.73   -3.49 .. -0.41

    All four are rotated hulls. Each cube hangs from its own bone, pivoted ON THE LEG'S AXIS at
    (0, y, 0), and pitched about X by -4, -6, -8 and -7 degrees.

    THE PITCH IS NOT DECORATION. Four plates stacked down a shin, all axis-aligned, would put eight
    faces in two planes and every one of them a candidate for z-fighting with its neighbour; the
    mod's cubes cannot rotate, so a plate that is not parallel to the plate above it has to hang
    from a bone that is not parallel either, and -4, -6, -8, -7 are four different angles for that
    reason first. What the sign buys on top of it is the scale: a NEGATIVE pitch about x swings each
    row's lower edge FORWARD, off the leg, so every row lifts away from the shin at its hem the way
    a scale does and lies flat against it at its head. That is the skirt's roll rotated ninety
    degrees - the hip wants its rows to lift outboard, the shin wants them to lift forward - and it
    is the one place the two parts deliberately differ.

  * THE LAP IS THE ORIGINS. All three scale rows are the SAME CUBE - 4.2 x 1.6 x 2.9 - and differ
    only in where they are put. Each sits 0.15 further back than the row above it, so measured at
    the front the four surfaces step:

        surface   front z (leg-local)   proud of the boot's front wall at -2.90
        band            -3.82                        0.92
        row1            -3.76                        0.86
        row2            -3.66                        0.76
        row3            -3.49                        0.59

    Everything here stands clear of the boot in z, nothing is coplanar with it - trace_geometry
    reports no COPLANAR and no OVERLAP on this part at all - and the fractional origins exist for
    that reason and no other, so -1.76 must not be tidied to -1.75.

  * WHERE THE ROWS LAND. Above: the shipped poleyns hang to leg-local y 7.10 and the shipped garters
    to 8.20 at x 2.85..4.05, and an exact separating-axis test over the oriented boxes puts this
    part's closest approach at 0.278 to the poleyns (the band, in y) and 0.450 to the garters (the
    band again, in x - which is what the band's 2.50 is for). Below: the boots shell's sole is at
    leg-local 12.90 and the bottom row's lowest corner stops at 12.73. Behind: the shipped heel
    wings' clasp clears by 0.412 and the spurs by 1.912; the shipped tassets' third lame clears by
    0.621 and the pelt by 2.881. The tightest thing on this leg is the poleyn's 0.278, where the
    shipped greaves leaves 0.10 and the puttees 0.45.

  * THE PAIR MEETS AT THE MIDLINE AND DOES NOT OVERLAP THERE. Every row reaches geo x -1.90, and the
    left leg's bone pivot is world x 1.9, so the inboard edge of this part is world x 0.00 exactly -
    and the mirrored copy's is too. The two `north` faces are in one plane and share an EDGE rather
    than an area, so there is nothing for the depth buffer to fight over. That is the puttees'
    problem solved by arithmetic instead of by shading: its windings reach geo -2.49 and overlap
    their twin over 1.18 units of world x, and its master has to paint that seam. Column 0 here is
    still painted low - it is the crease between the two shins and it should read as one - but it is
    a choice rather than a repair.

  * WHAT IS ACTUALLY SEEN. Three kinds of face draw. `north` is the shin, five columns by two rows
    on each of four cubes, and it is the whole part. `down` is the overhang under each row - the
    only place the lap is geometry rather than value - of which only the front strip clears the row
    beneath. The band's `up` is the ledge at the knee, free because the poleyn stops 0.28 above it.
    Everything else is buried: `west` and `east` inside the boot, `south` inside the leg, and every
    row's `up` under the row above.

  * EXPOSURE. Each row cube is 1.6 tall and unwraps to TWO texel rows of 0.80 each. Measured hem to
    hem the exposures are 0.72, 0.81 and 1.39 leg-local units - three different numbers, per idiom
    point 1's last clause, opening towards the ankle - so on the upper two rows the free texel row
    is almost exactly what shows and the lapped one is genuinely lapped. The bottom row shows both,
    which is why it is the one that carries the hem line.

The face rectangles come from paint_circlet_master.faces(), over `net()`ed sizes the way the sash
and garters painters do it - every cube here has a fractional dimension. Row one (v .. v+d) holds up
then down, each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west, south with
widths d, w, d, w - the two thin d-wide faces FIRST and THIRD.

Orientation inside each rectangle is the table the greaves painter records as measured, not
recalled:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x              max z
    down            +y  (underside)      min x              max z
    west            +x  (outboard)       min z  (front)     min y (top)
    east            -x  (inboard)        max z  (back)      min y (top)
    north           -z  (front)          min x  (inboard)   min y (top)
    south           +z  (back)           max x  (outboard)  min y (top)

So `north` reads MIDLINE to outboard, left to right, on both legs.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image

import decoration_paths
from fitting_mask import write_mask

ROOT = Path(__file__).resolve().parent.parent
GEO = decoration_paths.geometry("scale_shins")
OUT = ROOT / "tools" / "decoration_masters" / "scale_shins.png"
GUARD = OUT.with_name("scale_shins_guard.png")

TEX_W, TEX_H = 64, 32

# size (w, h, d) and uv (u, v), mirroring scale_shins.json in that file's own walk order - the root
# bone `shin` carries no cubes, so the order is its four children: the knee binding, then the three
# scale rows down the shin.
CUBES = {
    "band": ((4.4, 1.05, 3), (48, 0)),
    "row1": ((4.2, 1.6, 2.9), (0, 0)),
    "row2": ((4.2, 1.6, 2.9), (16, 0)),
    "row3": ((4.2, 1.6, 2.9), (32, 0)),
}

# origin, and the pivot + rotation of the bone the cube hangs from. Every pivot is on the leg's own
# axis at x = 0 and z = 0, which is what turns the pitch into a hem that lifts off the shin.
PLACEMENT = {
    "band": ((-1.9, 0, -1.75), (0, -0.5, 0), (-4, 0, 0)),
    "row1": ((-1.9, 0, -1.6), (0, 0.25, 0), (-6, 0, 0)),
    "row2": ((-1.9, 0, -1.45), (0, 1.55, 0), (-8, 0, 0)),
    "row3": ((-1.9, 0, -1.3), (0, 2.95, 0), (-7, 0, 0)),
}

# The fitting takes the field: the three scale rows whole, every face of them, so no cube boundary
# can show a colour seam. The band keeps the trim material. Idiom point 3, and the same three cubes
# the skirt hands to the same fitting.
FIELD = ("row1", "row2", "row3")

random.seed(163)  # deterministic output - regenerating must not churn the PNG

# Calibrated against the ramp, not guessed: the material ramp interpolates dark -> mid over master
# values 0..127 and mid -> light over 128..255, so a master confined to one half only ever uses half
# of a material's ramp. FREE, LAP and SCALE_STEP are the SKIRT'S values, unchanged, because the two
# parts are worn together and a scale that is a different grey on the shin than on the hip is a
# different animal.
EDGE = 232      # the free lower texel row of the bottom scale row: the ankle line, idiom point 2
RIM = 204       # the band's own face - the frame, and the only thing here that is not scale
FREE = 204      # the free lower half of a scale row, at the peak of the lateral profile
LAP = 138       # the lapped upper half of a scale row, in the shadow of the row above it
LEDGE = 168     # the band's `up` face at the knee, free because the poleyn stops 0.28 above it
HEM = 78        # the underside of a row where it overhangs the row beneath
INNER = 26      # buried - inside the boot, inside the leg, or under the row above

# The Tidal scale row - idiom point 1. Two texels to a scale, staggered one texel per row, and the
# notch smaller than the 66 between LAP and FREE so that rows read before scales.
SCALE_STEP = (0, -34)

# The lateral profile across a row's five `north` columns, midline to outboard. It is a MULTIPLIER
# rather than an offset, so that the dark rows keep their own shape instead of being flattened into
# INNER by a subtraction sized for the light ones - the shading of a shin is proportional, not
# additive. The peak sits at column 3 rather than column 4, which is the puttees' finding on this
# same socket: a highlight one column in from the edge says the plate turns round the leg, where a
# highlight at the edge says it stops flat. Column 0 is the midline crease between the two shins.
PROFILE = (0.60, 0.83, 0.95, 1.00, 0.88)

GRAIN = 3


def net(size):
    """A cube's box-UV net in whole pixels. Rounds up, the way Blockbench does - a row is 1.6 tall
    on purpose and unwraps to two rows of 0.80 model units, which is where this part's scale comes
    from."""
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


def paint_row(img, key: str, phase: int, free: int, lap: int, hem: int, hemline: bool = False) -> None:
    """One scale row: 4.2 x 1.6 x 2.9 on its own bone, pitched a few degrees about x.

    `north` is the whole read - five columns of the scale field, two texel rows, row 0 the half the
    row above laps and row 1 the free half. `phase` is the cube's index down the shin and shifts the
    stagger by one texel per row of geometry, which is what carries the brickwork over a cube
    boundary and not merely within one; with the upper rows' free texel being almost exactly what
    shows, the phase is the ONLY thing carrying it here.

    `hemline` is the bottom row, whose free texel row is the part's one lit edge - the ankle - and
    is painted at EDGE per idiom point 2.

    `down` is the overhang, five by three texels of the shadow the row throws on the row beneath. It
    is the only place on this part where the lap is geometry rather than value, so it is painted as
    a real shadow that lightens towards the front, where the 0.15 step actually opens; at the back
    the two rows are inside the boot together and there is nothing to shadow."""
    f = rects(key)

    x0, y0, fw, fh = f["north"]          # 5 x 2, col 0 = the midline crease, row 0 = lapped
    for j in range(fh):
        for i in range(fw):
            base = lap if j == 0 else (EDGE if hemline else free)
            put(img, x0 + i, y0 + j,
                round((base + scale(i, j + phase)) * PROFILE[i]) + random.randint(-GRAIN, GRAIN))

    x0, y0, fw, fh = f["down"]           # 5 wide (x) x 3 deep, col 0 = midline, row 0 = BACK
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j,
                hem + round(34 * ramp(j, fh)) + random.randint(-GRAIN, GRAIN))

    fill(img, f["up"], INNER)            # under the row above, or under the band
    fill(img, f["east"], INNER)          # 0.60 inside the boot, and against the mirrored twin
    fill(img, f["west"], INNER)          # 0.60 inside the boot
    fill(img, f["south"], INNER)         # inside the leg


def paint_band(img) -> None:
    """The binding at the knee that the shin hangs from: 4.4 x 1.05 x 3, the proudest thing on the
    part at leg-local z -3.82 and the only cube the `guard` fitting does not take.

    It exists for the fitting, exactly as the skirt's band and the pelt's thong do. A second
    material covering the whole greave would leave the smithed one nothing to be, and a binding
    painted as a band on row1's own face would have been recoloured along with the scales it was
    drawn over; a cube of its own is the only version of this that survives the mask. So it is
    smooth - no scale field, and jitter and all - and pitched near the top of the range, because
    after the mask is applied its texels are the only ones still speaking for the material the part
    was smithed in.

    It is also the widest cube here, at x 2.50 against the rows' 2.30, and that half unit is not
    style: the shipped garters hang at x 2.85..4.05 down to leg-local y 8.20, which is inside this
    band's own y range, and 2.50 is what leaves 0.45 between them.

    Its `up` face is the ledge at the top of the whole part. The shipped poleyns stop 0.28 above it
    and nothing else is up there, so it is a free `up` face - already rendered at vanilla's diffuse
    1.0 against `north`'s 0.8 - and it is therefore painted DOWN the scale rather than up."""
    f = rects("band")

    x0, y0, fw, fh = f["north"]          # 5 x 2, col 0 = the midline crease, row 0 = top
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j,
                round((RIM - (30 if j == 0 else 0)) * PROFILE[i]) + random.randint(-GRAIN, GRAIN))

    x0, y0, fw, fh = f["up"]             # 5 wide (x) x 3 deep, col 0 = midline, row 0 = BACK
    for j in range(fh):
        for i in range(fw):
            # The back rows are inside the boot's front wall at leg-local z -2.90; only the front
            # row of the three clears it.
            free = j == fh - 1
            put(img, x0 + i, y0 + j,
                round((LEDGE if free else INNER + 16) * PROFILE[i]) + random.randint(-GRAIN, GRAIN))

    x0, y0, fw, fh = f["down"]           # 5 wide x 3 deep; sits on row1 but for the front step
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j,
                HEM + round(26 * ramp(j, fh)) + random.randint(-GRAIN, GRAIN))

    fill(img, f["east"], INNER)          # 0.40 inside the boot, and against the mirrored twin
    fill(img, f["west"], INNER)          # 0.40 inside the boot
    fill(img, f["south"], INNER)         # inside the leg


def check_geometry() -> None:
    """CUBES and PLACEMENT must be the cube list, the origins and the bone frames of the shipped
    geometry, in order. Painting a texture for a shape the model no longer has is invisible to every
    other check in this pipeline: both halves stay internally consistent while the rectangles slide
    off the faces they were drawn for. The origins are asserted because on this part they ARE the
    lap - three identical cubes differing only in where they sit - and the rotations because a lost
    pitch would lay four plates flat on the shin without moving one texel."""
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
    paint_band(img)
    # The three rows step down the shin, each a shade under the one above it because each is a shade
    # less proud, and each carrying the next phase of the stagger. The bottom row takes the hem line.
    paint_row(img, "row1", 0, FREE, LAP, HEM + 10)
    paint_row(img, "row2", 1, FREE - 16, LAP - 8, HEM + 4)
    paint_row(img, "row3", 2, FREE - 30, LAP - 14, HEM, hemline=True)

    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque == set(claimed), "painted pixels do not match the UV rectangles"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)})")

    write_mask(img, [r for name in FIELD for r in rects(name).values()], GUARD)


if __name__ == "__main__":
    main()
