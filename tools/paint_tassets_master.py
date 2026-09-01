"""
Paint the grayscale master for the "tassets" part.

Kept as a script rather than a checked-in binary so the shape stays editable and reviewable. Like
paint_brooch_master.py and paint_sash_master.py it does not merely claim that CUBES matches the
shipped geometry, it reads assets/armorpieces/armorpieces/decoration/tassets.json at run time and
asserts it (check_geometry). Output goes to tools/decoration_masters/tassets.png, which
sync_decoration_masters.py installs for the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

Like every master since the circlet this one is 100% opaque. A plate of thigh armour has no fringe,
and parts draw with armorCutoutNoCull, so a hole punched in a three-pixel lame would show the inside
of the lame rather than the leg behind it. Every pixel here is value.

What this part is, and what that costs the painter:

  * `tassets` is a MIRRORED pair - Attachment.of(LEFT_LEG, 0, 2, 0) plus Attachment.mirrored on the
    right - so the layer's scale(-1, 1, 1) runs on the right-hand copy and ONE master serves both.
    That works only because the face-name mapping survives the flip: `west` is geo +x, which is
    outboard on both legs, and `north` column 0 is the material point at min x, which is inboard on
    both. The horns and the spaulders bought the same economy; the wing roots, on a single BODY
    attachment, could not.

  * The hero face is `north`. This is a plate hung on the FRONT-outer quadrant of the thigh (the
    outer flank belongs to the sash - see below), so the front is the only large face any camera
    ever sees. `west` is second: on the right hip, where no sash competes for the space, it is the
    part's whole profile. `east` faces the other leg across a 2.5-unit gap and is painted as a face
    in shadow, not as a face that is hidden.

  * It rides the LEG bone, so burial in the thigh is free and permanent - unlike the sash, which
    rides BODY and had to keep clear of a limb that moves under it. Every INNER pixel below is one
    of exactly three things: inside the wearer's own thigh, inside the lame above it, or (on
    lame1's `west` top row alone) inside the torso shell at rest, which uncovers on every stride
    and is therefore painted as flank rather than as filler.

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

Two consequences the code leans on. On `west` the depth columns run front to back, so the proud
leading edge is column 0 and the shadow deepens to the right; on `east` they run back to front, so
the same physical edge is the LAST column. And every `up` / `down` row runs back to front, which is
why lame1's one uncovered depth row - the unit of it that stands proud of the chestplate shell - is
row 2 and not row 0.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "tassets.json"
OUT = ROOT / "tools" / "decoration_masters" / "tassets.png"

TEX_W, TEX_H = 64, 32

# size (w, h, d) and uv (u, v), mirroring tassets.json in that file's own order - the three lames of
# one hanging plate, each on its own bone so the stack breaks forward as it descends. Geo extents at
# rest, for reading the paint code against (left-hand copy; the right one is the mirror image):
#   lame1 - the hip plate, hung from the belt line; geo x 1.60..4.60, y 11.75..14.75, z -3.90..-0.90.
#           Bone rotation 0. Its outboard face at x = 4.60 is the only part of the whole tasset that
#           stands outside the leggings thigh (x = 4.40), and it stops 0.15 short of the sash's
#           innermost face at x = 4.75.
#   lame2 - the middle lame, bone at -8 degrees; geo x 1.25..4.25, y 13.52..16.90, z -4.41..-1.02.
#   lame3 - the tapered tip, a further -8; geo x 1.85..3.85, y 15.39..18.82, z -4.68..-1.93.
# Each lame buries one unit up into the one above, so the wedge a rotated joint opens is inside
# solid geometry - the horns' rule, and the reason every lame's `up` face is INNER.
CUBES = {
    "lame1": ((3, 3, 3), (0, 0)),
    "lame2": ((3, 3, 3), (16, 0)),
    "lame3": ((2, 3, 2), (32, 0)),
}

random.seed(41)  # deterministic output - regenerating must not churn the PNG

# Calibrated against the ramp, not guessed. the material ramp interpolates dark -> mid over
# master values 0..127 and mid -> light over 128..255, so a master confined to one half only ever
# uses half of a material's ramp. The visible pixels here run the lap shadow under a lame to the lit
# hem of the bottom one.
UP = 236        # a top face standing proud - only lame1's leading depth row qualifies
FACE = 196      # `north`, the hero face
FLANK = 148     # `west`, the outboard flank
IN = 104        # `east`, the inboard flank: it faces the other leg and lives in its shadow
INNER = 72      # buried - in the thigh, in the lame above, or in the torso shell
DOWN = 46       # an underside

RIM = 32        # the lit chamfer along a free top edge
RIB = 22        # the raised centre column down the front of a lame
HEM = 46        # the lit lower edge of the bottom lame
FALL = 22       # top-to-bottom falloff down a standing face
DEPTH = 46      # front-to-back falloff across a flank
SEAM = 34       # the shadow row where a lame laps under the one above

# The three columns of a 3-wide `north` face: inboard (toward the other leg), the raised centre rib,
# outboard. The rib is what stops a 3 x 3 plate reading as a flat chip; at this size a form is a
# value against its neighbour, which is the brooch's finding arriving on a leg.
NORTH_COLS_3 = (FACE - 24, FACE + RIB, FACE + 4)
NORTH_COLS_2 = (FACE - 16, FACE + 8)


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


def fill(img, rect, lum: int, jitter: int = 3) -> None:
    x0, y0, w, h = rect
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            put(img, x, y, lum + random.randint(-jitter, jitter))


def ramp(i: int, n: int) -> float:
    """Position along a face axis, 0.0 at column/row 0 and 1.0 at the far end."""
    return 0.0 if n <= 1 else i / (n - 1)


def paint_lame1(img) -> None:
    """The hip plate. Three by three by three, hung so its top edge sits 0.75 under the sash's belt
    band and its bottom row is swallowed by lame2.

    Only one of its six faces is a top face and only one depth row of that: the plate is 3 deep and
    the 1.0 chestplate shell reaches geo z = -3, so of the three depth units exactly the leading one
    stands outside it. `up` rows run back to front, so that row is row 2.

    Its `west` face is the whole of the part's profile on the right hip. The top row's two rear
    depth columns are inside the torso shells at rest - but the shells ride BODY and this plate
    rides LEFT_LEG, so they uncover on every stride. They are painted as flank, dimmed, rather than
    as INNER filler: a row that is visible for most of a walk cycle is not a buried row."""
    size, uv = CUBES["lame1"]
    w, h, d = size
    f = faces(size, uv)

    x0, y0, fw, fh = f["north"]          # 3 x 3, col 0 = inboard, row 0 = top
    for j in range(fh):
        for i in range(fw):
            if j == fh - 1:
                lum = INNER              # under lame2
            else:
                lum = NORTH_COLS_3[i] + (RIM if j == 0 else 0) - round(FALL * ramp(j, fh - 1))
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["west"]           # 3 deep x 3 tall, col 0 = front (the proud leading edge)
    for j in range(fh):
        for i in range(fw):
            lum = FLANK + (RIM if j == 0 else 0) \
                - round(FALL * ramp(j, fh)) - round(DEPTH * ramp(i, fw))
            if j == 0 and i > 0:
                lum -= 20                # inside the torso shell at rest; still painted as flank
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["east"]           # 3 deep x 3 tall, col 0 = BACK, so the free one is col 2
    for j in range(fh):
        for i in range(fw):
            free = i == fw - 1 and j < fh - 1
            lum = (IN - round(FALL * ramp(j, fh)) + (RIM // 2 if j == 0 else 0)) if free else INNER
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["up"]             # 3 wide (x) x 3 deep, rows run BACK to front
    for j in range(fh):
        for i in range(fw):
            if j < fh - 1:
                lum = INNER              # inside the thigh
            else:
                lum = UP + (14 if i == 1 else -10)   # the rib crests the leading edge
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    fill(img, f["down"], INNER)          # entirely inside lame2
    fill(img, f["south"], INNER)         # entirely inside the thigh


def paint_lame2(img) -> None:
    """The middle lame, on a bone at -8 degrees. It is the only cube on the part whose `north` face
    is exposed all the way down, and the row that makes the stack read is its FIRST one: it laps
    under lame1 and goes to SEAM against a plate at FACE. Two 8-degree breaks do not read as three
    lames on their own - the spaulders' finding, and the reason each break here gets a hard shadow
    row rather than an angle and a hope.

    Its outboard flank keeps the front two depth columns and loses the third: the lame is inset to
    geo x = 4.25 where the leggings thigh surface is 4.40, so everything behind the thigh's own
    front plane at z = -2.5 is inside the leg. That inset is deliberate and it is part of the
    resolution of the sash collision - see PLAN.md - so it is worth not "tidying" back out."""
    size, uv = CUBES["lame2"]
    w, h, d = size
    f = faces(size, uv)

    x0, y0, fw, fh = f["north"]          # 3 x 3, all of it exposed
    for j in range(fh):
        for i in range(fw):
            if j == 0:
                lum = SEAM - 20 + 10 * i          # the lap shadow, itself lit toward outboard
            else:
                lum = NORTH_COLS_3[i] - round(FALL * ramp(j - 1, fh - 1))
                if j == fh - 1:
                    lum += 10                     # the free lower edge catches a little light
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["west"]           # 3 deep x 3 tall; row 0 under lame1, col 2 inside the thigh
    for j in range(fh):
        for i in range(fw):
            free = j > 0 and i < fw - 1
            lum = (FLANK - 8 - round(FALL * ramp(j, fh)) - round(DEPTH * ramp(i, fw))) if free else INNER
            if free and j == 1:
                lum -= 18                # the shadow the plate above throws down this flank
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["east"]           # 3 deep x 3 tall, col 0 = BACK and inside the thigh
    for j in range(fh):
        for i in range(fw):
            lum = INNER if i == 0 else (IN - 8 - round(FALL * ramp(j, fh)) + round(20 * ramp(i, fw)))
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["down"]           # 3 wide x 3 deep; only the inboard column clears lame3
    for j in range(fh):
        for i in range(fw):
            free = j > 0 and i == 0
            put(img, x0 + i, y0 + j,
                ((DOWN + round(16 * ramp(j, fh))) if free else INNER) + random.randint(-3, 3))

    fill(img, f["up"], INNER)            # inside lame1
    fill(img, f["south"], INNER)         # inside lame1, then inside the thigh


def paint_lame3(img) -> None:
    """The tip, a further -8 degrees and two units narrower. Its top row is buried a unit up into
    lame2, so of a 2 x 3 front face what is ever seen is two rows: the lap shadow and the hem.

    The hem is the brightest thing on the part and it is carried at the same row index on `north`,
    `west`, `east` and `south`, so it closes around all four corners - the horns' ring trick spent
    on an edge rather than a groove. It only reads because the row above it is dropped well below
    the plate: a bright hem against a bright plate is not a hem.

    Its underside is the one fully exposed `down` face on the part, and it is the face a player in
    first person actually looks at, so it gets a real front-to-back lift rather than a flat DOWN."""
    size, uv = CUBES["lame3"]
    w, h, d = size
    f = faces(size, uv)
    hem = h - 1

    x0, y0, fw, fh = f["north"]          # 2 x 3, col 0 = inboard, row 0 inside lame2
    for j in range(fh):
        for i in range(fw):
            if j == 0:
                lum = INNER
            elif j == hem:
                lum = NORTH_COLS_2[i] + HEM
            else:
                lum = SEAM - 12 + 12 * i
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    for name, front in (("west", 0), ("east", 1)):
        base = FLANK - 16 if name == "west" else IN - 16
        x0, y0, fw, fh = f[name]         # 2 deep x 3 tall; west counts front->back, east back->front
        for j in range(fh):
            for i in range(fw):
                if j == 0:
                    lum = INNER
                else:
                    lum = base - round(DEPTH * ramp(abs(i - front), fw))
                    lum += HEM - 8 if j == hem else -round(FALL * ramp(j, fh))
                put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["down"]           # 2 wide (x) x 2 deep, rows run back to FRONT, fully exposed
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j,
                DOWN + round(26 * ramp(j, fh)) + (8 if i else -6) + random.randint(-3, 3))

    x0, y0, fw, fh = f["south"]          # 2 x 3, col 0 = OUTBOARD; only the hem row clears the thigh
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j,
                ((DOWN + 34 - 10 * i) if j == hem else INNER) + random.randint(-3, 3))

    fill(img, f["up"], INNER)            # inside lame2


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
    paint_lame1(img)
    paint_lame2(img)
    paint_lame3(img)

    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque == set(claimed), "painted pixels do not match the UV rectangles"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)})")


if __name__ == "__main__":
    main()
