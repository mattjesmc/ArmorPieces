"""
Paint the grayscale master for the "heel_wings" part - talaria, on the heel socket.

Kept as a script rather than a checked-in binary so the shape stays editable and reviewable: the
CUBES table below is the same cube list as
assets/armorpieces/armorpieces/decoration/heel_wings.json, and a change to one is meant to be a
change to the other. Output goes to tools/decoration_masters/heel_wings.png, which
sync_decoration_masters.py installs for the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

**No static layer, deliberately.** The horn got one because keratin is not metal. These are winged
boots in an armour set, and a metal vane is the reading that agrees with `wing_roots` on the back
being hardware rather than plumage - so the whole part takes the material, and a gold pair and a
netherite pair are different objects rather than the same feathers with different clasps.

The part is a clasp and two vanes, and the vanes are the flat swept blade that the `horns` rework
spent its whole budget avoiding. That is the point: the thing that reads as a wing is exactly the
thing a wing should be. Both hang off one clasp rather than chaining, because a fan of two feather
groups spreading 38 degrees apart is what separates a wing from a fin.

Geometry, checked against the body before it was written:

  * The **clasp** spans leg x 1..4 and z 0..4, so it straddles the boot shell's outer wall at x = 3
    and its back wall at z = 3 without putting a face on either. Coplanarity is a per-face check, and
    the obvious cube here - x 2..4, z 0..3 - would have had faces on both walls AND on the leg box's
    own surface at x = 2. Three planes, three chances to z-fight.
  * **Reach is z = 7.69**, 4.69 past the boot's back wall. The spurs' rowel already reaches 6.7 past
    it and that was flagged as the largest projection in the mod; staying under a number already
    considered generous is the whole argument.
  * The fan tops out at **leg y = 3.72**, mid-calf, which is where talaria sit, and the boot's sole
    at y = 13 is nowhere near the low vane.

  * Everything is behind the leg's own z = 0 plane, so nothing here can meet the `greaves` socket on
    the front of the same bone, and nothing reaches the front-outer thigh where the `tassets` hang.

The vanes are 1 unit thick, which makes their two broad faces the box's `east` and `west` - the
6-wide-by-4-tall rectangles, running z across and y down. Their thin edges are `north` (the leading
edge), `south` (the trailing edge) and the two 1-wide caps. `bb = (-geo_x, 24 - geo_y, geo_z)`, so
`west` is the geo +x face; the heel anchor mirrors, so geo +x is outward on both legs and the lit
face can be the outboard one on both.

**The trailing rake is punched in alpha, and the caps have to be punched with it.** A wing whose
silhouette is a rectangle reads as a paddle - the lesson the feathering learned the expensive way. So
RAKE removes the bottom-back corner of each vane. On a plate one unit thick, punching through shows
the far side's own face, which is the same feather painting, so the hole costs nothing; but the
`down` and `south` edge faces run along the rows the rake removes, and left painted they would hang
in the air as a one-pixel outline of a wing that is no longer there. They are masked by the same
rule that cuts the broad faces.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "heel_wings.json"
OUT = ROOT / "tools" / "decoration_masters" / "heel_wings.png"

TEX_W, TEX_H = 64, 32

# size (w, h, d) and uv (u, v), mirroring heel_wings.json.
CUBES = {
    "clasp":      ((3, 3, 4), (0, 0)),    # the mount, straddling the boot's outer and back walls
    "vane_upper": ((1, 4, 6), (14, 0)),   # the long vane, 34 deg up and 14 deg outboard
    "vane_lower": ((1, 3, 5), (28, 0)),   # the short one, 4 deg down and 7 deg out - a 38 deg fan
}

random.seed(23)  # deterministic output - regenerating must not churn the PNG

# Lit from above and outboard, the same convention every part in this mod uses.
UP = 236        # the vane's top edge, and the clasp's
DOWN = 44       # under the clasp; on a vane, the underside of the leading half
WEST = 224      # outward - the lit broad face
EAST = 108      # inboard, in the leg's shadow, but still seen past the calf from behind
NORTH = 196     # the leading edge, catching the light head-on
SOUTH = 96      # the trailing edge

QUILL = 40      # the shaft between two feathers, cut into the broad faces
LEADING = 22    # the front column of a vane - the wing bone, brighter than the vane behind it
SPAN_FADE = -30 # a vane darkening from its root to its trailing edge
RIVET = 24      # the clasp's mounting stud


def faces(size, uv):
    """Per-face pixel rectangles (x, y, w, h) for one box-UV cube. Row one (v .. v+d) holds up then
    down, each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west, south with
    widths d, w, d, w - the two thin d-wide faces FIRST and THIRD."""
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


def rake(col: int, depth: int) -> int:
    """How many rows are cut from the bottom of a vane at this column, front (0) to back.

    Nothing is cut over the leading half, then one row, then two: the wing keeps its full depth where
    it is attached and thins to a point behind, which is the shape of a feather group and the shape a
    rectangle is not. Expressed against the cube's depth so both vanes use one rule."""
    if col < depth // 2:
        return 0
    if col < depth - 1:
        return 1
    return 2


def solid(col: int, row: int, size) -> bool:
    """Whether a broad-face cell survives the rake. Row 0 is the vane's top edge."""
    _, h, d = size
    return row < h - rake(col, d)


def put(img, x: int, y: int, lum: int, alpha: int = 255) -> None:
    if 0 <= x < TEX_W and 0 <= y < TEX_H:
        img.putpixel((x, y), (max(0, min(255, lum)), alpha))


def vane_value(base: int, col: int, row: int, depth: int) -> int:
    """One cell of a vane: its face's base value, the quill grooves between feather rows, the bright
    leading column, and a fade from root to trailing edge."""
    lum = base + round(SPAN_FADE * col / max(1, depth - 1))
    if col == 0:
        lum += LEADING
    if row % 2 == 1:
        lum -= QUILL
    return lum


def paint_vane(img, name: str) -> None:
    size, uv = CUBES[name]
    _, h, d = size
    f = faces(size, uv)

    # The two broad faces carry the feathering; the rake cuts them and everything that borders them.
    for face, base in (("east", EAST), ("west", WEST)):
        x0, y0, _, _ = f[face]
        for row in range(h):
            for col in range(d):
                if not solid(col, row, size):
                    continue
                # `west` is the geo +x face and its columns run back-to-front against `east`'s, so a
                # feather painted at one column lands on the same place on the vane from both sides.
                u = col if face == "east" else d - 1 - col
                put(img, x0 + u, y0 + row, vane_value(base, col, row, d) + random.randint(-4, 4))

    # The top edge survives everywhere - the rake only ever cuts upward from the bottom. This face is
    # w = 1 wide by d tall, so its rows are the span, not its columns.
    x0, y0, _, _ = f["up"]
    for col in range(d):
        put(img, x0, y0 + col, UP + round(SPAN_FADE * col / max(1, d - 1)) + random.randint(-4, 4))

    # The underside exists only where the vane still reaches the bottom row.
    x0, y0, _, _ = f["down"]
    for col in range(d):
        if rake(col, d) == 0:
            put(img, x0, y0 + col, DOWN + random.randint(-4, 4))

    # Leading edge: full height. Trailing edge: only the rows the rake left at the back column.
    x0, y0, _, _ = f["north"]
    for row in range(h):
        put(img, x0, y0 + row, NORTH - (QUILL if row % 2 == 1 else 0) + random.randint(-4, 4))
    x0, y0, _, _ = f["south"]
    for row in range(h):
        if solid(d - 1, row, size):
            put(img, x0, y0 + row, SOUTH + random.randint(-4, 4))


def paint_clasp(img) -> None:
    """The mount. Flat metal with a stud on its outboard face - the same argument the horn's boss
    makes: hardware bolted to the boot, rather than the wing growing out of it."""
    size, uv = CUBES["clasp"]
    f = faces(size, uv)
    for face, base in (("up", UP), ("down", DOWN), ("east", EAST),
                       ("north", NORTH), ("west", WEST), ("south", SOUTH)):
        x0, y0, fw, fh = f[face]
        for y in range(y0, y0 + fh):
            for x in range(x0, x0 + fw):
                put(img, x, y, base + random.randint(-5, 5))
    # One stud, centred on the 4-wide-by-3-tall outboard face; two would leave no gap between them.
    x0, y0, _, _ = f["west"]
    for i in (1, 2):
        put(img, x0 + i, y0 + 1, WEST + RIVET + random.randint(-3, 3))


FACES = ("up", "down", "east", "north", "west", "south")


def check_geometry() -> None:
    """CUBES must be the cube list of the shipped geometry, in order.

    Painting a texture for a shape the model no longer has is invisible to every other check in this
    pipeline: `bb_geo roundtrip` checks the model against itself and check_layout() checks the master
    against itself, and both keep passing while the rectangles slide off the faces they were drawn
    for. Four parts had drifted that way before this check existed on any of them."""
    doc = json.loads(GEO.read_text(encoding="utf-8"))
    found = []

    def walk(bone):
        for c in bone.get("cubes", []):
            found.append((tuple(c["size"]), tuple(c["uv"])))
        for child in bone.get("children", []):
            walk(child)

    for bone in doc["bones"]:
        walk(bone)

    assert (doc["texture_width"], doc["texture_height"]) == (TEX_W, TEX_H),         f"{GEO.name} is {doc['texture_width']}x{doc['texture_height']}, this master is {TEX_W}x{TEX_H}"
    assert found == list(CUBES.values()),         f"CUBES disagrees with {GEO.name}: {found} vs {list(CUBES.values())}"


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


def check_paint(img, claimed: dict) -> None:
    """This master rakes alpha, so it may not be checked against the net pixel for pixel the way an
    all-opaque one is - but the two failures either side of the rake still can be.

    A pixel painted outside the net is paint the model never samples. A face left with no opaque
    pixel is worse: the rake is meant to cut a corner off a vane, and a face it empties renders as a
    hole straight through the part."""
    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    stray = opaque - set(claimed)
    assert not stray, f"{len(stray)} painted pixel(s) lie outside every face rectangle: {sorted(stray)[:8]}"
    painted = {claimed[p] for p in opaque}
    for name in CUBES:
        for face in FACES:
            assert f"{name}.{face}" in painted, f"{name}.{face} has no opaque pixel - it will render as a hole"


def main() -> None:
    check_geometry()
    claimed = check_layout()
    img = Image.new("LA", (TEX_W, TEX_H), (0, 0))
    paint_clasp(img)
    paint_vane(img, "vane_upper")
    paint_vane(img, "vane_lower")
    check_paint(img, claimed)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    print(f"wrote {OUT} ({len(opaque)} opaque px of {len(claimed)} net, "
          f"values {min(lums)}-{max(lums)})")


if __name__ == "__main__":
    main()
