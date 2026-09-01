"""
Paint the grayscale master for the "brooch" part.

Kept as a script rather than a checked-in binary so the shape stays editable and reviewable. The
CUBES table below is the same cube list as
assets/armorpieces/armorpieces/decoration/brooch.json - and unlike the earlier five painters this
one does not merely claim that, it reads the geometry at run time and asserts it (check_geometry).
A silent drift between the two is the one bug in this pipeline that neither the roundtrip check nor
the layout check can see, because both halves stay internally consistent while the texture slides
off the model. Output goes to tools/decoration_masters/brooch.png, which
sync_decoration_masters.py installs for the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

Like the circlet, the horns, the spaulders and the wing roots, this master is 100% opaque. A clasp
has no fringe, and parts draw with armorCutoutNoCull, so a hole punched anywhere would show the
inside of the clasp rather than the chestplate behind it. Every pixel here is value.

What this part is, and what that costs the painter:

  * `collar` is a SINGLE, non-mirrored attachment on the torso, so - as with `back` - the layer's
    scale(-1, 1, 1) never runs and no one-master-serves-both economy applies. Nor is there a pair to
    light, and unlike the other chest parts there is no figure centreline to hang the shape on: this
    is one clasp pinned over the wearer's left breast, geo x 0.5..3.5. What symmetry it has is its
    own. The three cubes are stacked concentrically about the part's own axis at x = 2 - band 3
    wide, head 2, strap 1, each centred half a unit inside the one above it - so every face is still
    painted symmetrically, only about x = 2 rather than x = 0, and `west` and `east` differ only in
    the order their depth columns run. The band's outboard end reaches x = 3.5, half a unit over the
    1.0-inflate sleeve's inboard wall at x = 3, and only among its buried rows: the proud unit at
    z -4..-3 stands in front of the sleeve's own front wall rather than inside it.

  * Its hero face is `north` (geo -z), the front. That is the opposite end of the model from the
    wing roots' `south`, so the palette constants are the same numbers wearing different names: read
    NORTH/FACE as "the face that is seen".

  * Almost nothing of this part is allowed to stick out. The clasp lives between the helmet's rest
    bottom plane (geo y = 1) and the chest, and every unit it stands proud of the chestplate costs
    head-pitch clearance, so the whole part is 1.75 units proud at its deepest. The detail a bigger
    part would model - the seat the clasp head sits down into, the keeper mouth the strap runs out
    of - is therefore PAINTED, the way the wing roots painted their collar band instead of modelling
    it. What that restraint buys is pitch. The band's top edge is at y = 4.5 and the corner the
    helmet reaches first is the head's top-front at (5, -4.75), which the chin swallows at 38.1
    degrees, against 38.8 for the band's own top-front corner at (4.5, -4). A part that survives
    that hard a look down pays for it in the read: the clasp sits low enough to be a breast
    fastening rather than a throat one.

  * It is small. Sixty-two texels of box UV, of which fewer than half are ever seen - the band's
    front face is three pixels, the head's is two, and of the strap's two only one clears the head.
    At three pixels across there is no room for both a bolt and the plainly darker surround a
    one-pixel bolt needs before it reads as a bolt rather than as noise, so the band carries none.
    What its three pixels say instead is end, score, end.

Burial, and why the buried rows are painted anyway. The chestplate's outer layer is 1.0 inflate, so
its front surface is geo z = -3 and the torso box begins at z = -2. The band spans z -4..-1, the
head -4.75..-2.75 and the strap -4.25..-2.25: every cube is authored deeper than it shows, and their
back faces land on three different planes, none of them the chestplate's own at z = -3 and none of
them the torso box's front at z = -2. Nothing on this part is coplanar with anything, and there is
slack left over if COLLAR moves in pass B. Those hidden rows are painted at INNER rather than left
black, exactly as the horns' and spaulders' were.

The strap is the only thing here that is not axis-aligned: it hangs from its own bone at -10 degrees
so its tip lifts away from the chest. Rotating about the pivot at (0, 5.5, -3.5) swings the BACK
bottom corner outward as much as it swings the front one inward, and that swing goes with distance
from the pivot - which is what fixes the strap at two units tall. At two tall the corner lands at
z = -2.573, four tenths of a unit inside the chestplate surface, while the tip's front face reaches
-4.542; at four tall the same corner would sit at -2.920, eight hundredths inside, one rounding
error from a hairline of decoration hanging in the air below the clasp. The rule is the spaulders'
rule read from the other end: on a rotated segment, compute the corner that moves away from the
body, not the one that moves into it.

The face rectangles come from paint_circlet_master.faces(), copied verbatim: row one (v .. v+d)
holds up then down, each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west,
south with widths d, w, d, w. Note the row-two order: the two thin d-wide faces come FIRST and THIRD.

Orientation inside each rectangle is the table PLAN.md records as measured, not recalled:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        inboard (min x)    back  (max z)
    down            +y  (underside)      inboard (min x)    back  (max z)
    west            +x                   front   (min z)    top   (min y)
    east            -x                   back    (max z)    top   (min y)
    north           -z  (front)          inboard (min x)    top   (min y)
    south           +z  (back)           outboard(max x)    top   (min y)

Note what that means for the depth rows of `up` and `down`: row 0 is the BACK of the box, so on the
band, which is 3 deep, the one row that shows is row 2, and on the head and the strap, which are 2
deep, it is row 1. Getting it the other way round would paint the buried grey onto the only lit edge
of the part.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "brooch.json"
OUT = ROOT / "tools" / "decoration_masters" / "brooch.png"

TEX_W, TEX_H = 64, 32

# size (w, h, d) and uv (u, v), mirroring brooch.json, in that file's own order.
#   plate  - the band over the breast, 1 unit proud of the chestplate surface and 2 buried;
#            geo x 0.5..3.5, y 4.5..5.5, z -4..-1.
#   boss   - the clasp head, sunk to its waist in the band's lower half and hanging half a unit
#            below it, 1.75 units proud of the chestplate and 0.75 proud of the band's own front
#            face; geo x 1..3, y 5..6, z -4.75..-2.75.
#   tongue - the strap end running out of the head's underside, on its own bone at -10 degrees so
#            its tip lifts away from the chest; geo x 1.5..2.5, y 5.25..7.25, z -4.25..-2.25 before
#            the rotation, which carries the tip's bottom-front corner to (7.093, -4.542).
CUBES = {
    "plate":  ((3, 1, 3), (4, 0)),
    "boss":   ((2, 1, 2), (24, 1)),
    "tongue": ((1, 2, 2), (38, 1)),
}

random.seed(53)  # deterministic output - regenerating must not churn the PNG

# Calibrated against the ramp, not guessed. the material ramp interpolates dark -> mid over
# master values 0..127 and mid -> light over 128..255, so a master confined to one half only ever
# uses half of a material's ramp. The visible pixels here run SLOT (22) to the boss's lit lip (250).
UP = 244        # a top face standing proud - the brightest plane on the part
FACE = 204      # `north`, the front: the hero surface of a chest part
FLANK = 152     # the proud depth column of a side face
DOWN = 40       # an underside
INNER = 74      # buried in the chestplate, in the torso, or in another cube of the part
SLOT = 22       # the keeper mouth the strap runs out of

RIM = 34        # the lit chamfer along the forward-most top edge, which only the head gets
SHADOW = 54     # a depth column lapping behind something - into the band, or into the shell
GROOVE = 90     # the seat the clasp head sits down into


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


def fill(img, rect, lum: int, jitter: int = 4) -> None:
    x0, y0, w, h = rect
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            put(img, x, y, lum + random.randint(-jitter, jitter))


def paint_plate(img) -> None:
    """The band. Three deep with only its front unit outside the chestplate surface, so on both side
    faces exactly one depth column shows and on `up` / `down` exactly one depth row does - and
    because those rows run back-to-front, it is the LAST row, not the first.

    Its `north` face is three pixels, and they are the part's whole spelling of a band: two lit ends
    with, between them, the seat the clasp head sits down into. That middle pixel is dark because
    something really is standing in front of it - the head covers it outright and laps half a unit
    over each end besides - so the score is measured rather than drawn."""
    size, uv = CUBES["plate"]
    w, h, d = size
    f = faces(size, uv)
    seat = 1                              # the column the clasp head stands on

    x0, y0, fw, fh = f["north"]           # 3 x 1, col 0 = min x, inboard
    for i in range(fw):
        put(img, x0 + i, y0, FACE - (GROOVE if i == seat else 0) + random.randint(-3, 3))

    x0, y0, fw, fh = f["up"]              # 3 wide x 3 deep, rows back to front; row 2 is the ledge
    for i in range(fw):
        put(img, x0 + i, y0 + 0, INNER + random.randint(-3, 3))
        put(img, x0 + i, y0 + 1, INNER + random.randint(-3, 3))
        put(img, x0 + i, y0 + 2, UP + random.randint(-3, 3))

    x0, y0, fw, fh = f["down"]            # same layout; the head hangs through the middle column
    for i in range(fw):
        put(img, x0 + i, y0 + 0, INNER + random.randint(-3, 3))
        put(img, x0 + i, y0 + 1, INNER + random.randint(-3, 3))
        put(img, x0 + i, y0 + 2, (INNER if i == seat else DOWN) + random.randint(-3, 3))

    # The band is one unit tall, so each flank is a single row of depth columns: one proud and two
    # buried. `west` runs front-to-back and `east` back-to-front, which is the only difference.
    for name, proud in (("west", 0), ("east", 2)):
        x0, y0, fw, fh = f[name]          # 3 wide (depth) x 1 tall
        for i in range(fw):
            put(img, x0 + i, y0, (FLANK if i == proud else INNER) + random.randint(-3, 3))

    fill(img, f["south"], INNER)          # inside the torso


def paint_boss(img) -> None:
    """The clasp head. 1.75 units proud of the chestplate - the deepest anything on this part goes -
    sunk to its waist in the band's lower half and hanging half a unit below it. Two pixels of front
    face and a two-pixel top ledge are the whole statement, which is why the head takes the chamfer
    that a wider part would spread along every top edge it had: it is the forward-most thing here,
    and if the band carried one too the step between them would flatten to nothing. Its own ledge is
    0.75 deep and half a unit lower than the band's, so it is painted below UP for both reasons."""
    size, uv = CUBES["boss"]
    w, h, d = size
    f = faces(size, uv)

    x0, y0, fw, fh = f["north"]           # 2 x 1: the lit lip, and the brightest value on the part
    for i in range(fw):
        put(img, x0 + i, y0, FACE + RIM + 12 + random.randint(-3, 3))

    x0, y0, fw, fh = f["up"]              # 2 wide x 2 deep; row 0 is inside the band
    for i in range(fw):
        put(img, x0 + i, y0 + 0, INNER + random.randint(-3, 3))
        put(img, x0 + i, y0 + 1, UP - 22 + random.randint(-3, 3))

    x0, y0, fw, fh = f["down"]            # hangs clear below the band, so both depth rows are free
    for i in range(fw):
        put(img, x0 + i, y0 + 0, DOWN + random.randint(-3, 3))
        put(img, x0 + i, y0 + 1, DOWN + 12 + random.randint(-3, 3))

    # The head is a unit narrower than the band and its side faces are inside it over the half unit
    # they share in y. The front depth column stands clear of the band's front face and carries the
    # same chamfer that face does; the back one is half buried in the band.
    for name, front in (("west", 0), ("east", 1)):
        x0, y0, fw, fh = f[name]          # 2 wide (depth) x 1 tall
        put(img, x0 + front, y0, FLANK + RIM + random.randint(-3, 3))
        put(img, x0 + (1 - front), y0, FLANK - SHADOW + random.randint(-3, 3))

    fill(img, f["south"], INNER)          # inside the chestplate shell


def paint_tongue(img) -> None:
    """The strap end. Its top row is up inside the head and its back depth column runs into the
    chestplate, so of a 1 x 2 x 2 box the pixels that carry it are one of front face, two of
    underside and one column of each flank.

    The tilt is a rotation about X, which leaves the +-x normals exactly where they were: the
    strap's flanks are lit no differently from the band's, and the one face the tilt actually turns
    into the light is its front. That is where the +24 goes, and the only place it goes. Above that
    is the keeper mouth - a row nine tenths inside the head, whose visible tenth is precisely the gap
    the strap comes out of, and therefore the darkest value on the part."""
    size, uv = CUBES["tongue"]
    w, h, d = size
    f = faces(size, uv)

    x0, y0, fw, fh = f["north"]           # 1 x 2: row 0 in the mouth, row 1 clear of the head
    for i in range(fw):
        put(img, x0 + i, y0 + 0, SLOT + random.randint(-3, 3))
        put(img, x0 + i, y0 + 1, FACE + 24 + random.randint(-3, 3))

    fill(img, f["up"], INNER)             # the whole top is inside the head

    x0, y0, fw, fh = f["down"]            # 1 wide x 2 deep; the tip's underside, front row lit
    for i in range(fw):
        put(img, x0 + i, y0 + 0, DOWN + random.randint(-3, 3))
        put(img, x0 + i, y0 + 1, DOWN + 12 + random.randint(-3, 3))

    for name, front in (("west", 0), ("east", 1)):
        x0, y0, fw, fh = f[name]          # 2 wide (depth) x 2 tall; row 0 is up inside the head
        back = 1 - front
        put(img, x0 + front, y0 + 0, INNER + random.randint(-3, 3))
        put(img, x0 + back, y0 + 0, INNER + random.randint(-3, 3))
        put(img, x0 + front, y0 + 1, FLANK + random.randint(-3, 3))
        put(img, x0 + back, y0 + 1, FLANK - SHADOW + random.randint(-3, 3))

    fill(img, f["south"], INNER)          # inside the chestplate shell


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
    paint_plate(img)
    paint_boss(img)
    paint_tongue(img)

    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque == set(claimed), "painted pixels do not match the UV rectangles"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)})")


if __name__ == "__main__":
    main()
