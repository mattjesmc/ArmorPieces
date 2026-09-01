"""
Paint the grayscale master for the "wing_roots" part.

Kept as a script rather than a checked-in binary so the shape stays editable and reviewable: the
CUBES table below is the same cube list as
assets/armorpieces/armorpieces/decoration/wing_roots.json, and a change to one is meant to be a
change to the other. Output goes to tools/decoration_masters/wing_roots.png, which
sync_decoration_masters.py installs for the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

Like the circlet, the horns and the spaulders, this master is 100% opaque. Mounting hardware has no
fringe to carve away, and parts draw with armorCutoutNoCull, so a hole punched anywhere would show
the inside of the bracket rather than the chestplate behind it. Every pixel here is value.

What this part needs that the earlier four did not:

  * `back` is a SINGLE, non-mirrored attachment, so the layer draws one piece of geometry and the
    pair of sockets is modelled twice rather than mirrored once. The whole lit-outboard /
    shadowed-inboard idiom the horns and spaulders got for free from `scale(-1, 1, 1)` therefore has
    to be built by hand: socket_l and socket_r have separate UV rectangles, and every face and every
    gradient in paint_tube() is chosen through `side`, which is +1 for the +x socket and -1 for the
    -x one. Getting that backwards would light both sockets from the same side of the body and the
    pair would stop reading as a pair.

  * Its hero face points BACKWARD. Every previous part's brightest large face was `up` or the
    outboard `west`; here the only face a player ever really looks at is the bar's `south` (geo +z),
    because that is the surface pointing away from the spine. So SOUTH is the light end of the ramp
    on this part where it was the dark end on the spaulders. This is not a change of light
    direction - vanilla's own diffuse term shades +z and -z identically - it is the master carrying
    form for the face that is actually seen.

  * The two sockets are 3x3 tubes seen almost end-on. Their whole read is the mouth: a 3x3 `south`
    rectangle painted as a bright upper lip, a two-pixel bore at MOUTH, and a dimmer lower lip, with
    a collar band repeated at the same axial index on all four of the tube's side faces. The axial
    index is shared across up/down/east/west exactly the way the horns' rings are, which is the only
    reason the collar lines up around the tube's corners.

Burial, and why the buried rows are painted anyway. The bar is 2 deep with one unit outside the
1.0-inflate chestplate surface (geo z = 3) and one unit inside it, so every side face of the bar is
half buried; each tube runs from geo z 0.3 (inside the torso) out to 6.6, so roughly three of its
five axial units never show. Those rows are painted at INNER rather than left black, the way the
horns' and spaulders' buried rows were, in case BACK moves in pass B.

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

For this part "min x / max x" is literal model x, not a side-relative outboard: the geometry is
symmetric about x = 0 and is never mirrored by the layer, so `west` is the +x face of BOTH sockets
and only `side` tells you whether that is the outboard one.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "wing_roots.json"
OUT = ROOT / "tools" / "decoration_masters" / "wing_roots.png"

TEX_W, TEX_H = 64, 32

# size (w, h, d) and uv (u, v), mirroring wing_roots.json. `bar` is the harness plate across the
# shoulder blades; `strap` is the keel tab below it, standing one unit prouder than the bar; the two
# tubes are the sockets, splayed 20 degrees outboard and pitched 14 degrees up, each buried through
# the bar and into the torso so the joint cannot open a gap.
CUBES = {
    "bar":    ((7, 5, 2), (0, 0)),
    "strap":  ((3, 3, 3), (18, 0)),
    "tube_l": ((3, 3, 5), (32, 0)),
    "tube_r": ((3, 3, 5), (48, 0)),
}

random.seed(41)  # deterministic output - regenerating must not churn the PNG

# Calibrated against the ramp, not guessed. the material ramp interpolates dark -> mid over
# master values 0..127 and mid -> light over 128..255, so a master confined to one half only ever
# uses half of a material's ramp. The visible pixels here run MOUTH (22) to RIM (250).
UP = 242        # the bar's top edge - the one horizontal plane, so the brightest value here
FACE = 196      # the bar's south face - the hero surface of a back part
FLANK = 158     # a tube's outboard flank
IN = 84         # a tube's inboard flank, in the slot between the two sockets
DOWN = 38       # undersides
INNER = 72      # buried in the chestplate, in the torso, or in another cube of the part
MOUTH = 22      # the socket bore
RIM = 250       # the lit upper lip of the bore
TUBE_UP = 210   # a tube's top: tilted 14 degrees off horizontal, so it sits below the bar's own top
TUBE_DOWN = 58  # a tube's underside - lifted off DOWN so the collar's shadow row cannot clamp to 0

Y_FALL = 26     # top-to-bottom falloff down a standing face
COLLAR = 26     # the band at the mouth end of a tube, on all four of its side faces
SHADE = 40      # the axial unit sitting in the bar's own shadow
STUD = 42       # a bolt head
GROOVE = 46     # the centre channel down the bar, echoing the strap below it


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


def ramp(i: int, n: int) -> float:
    """Position along a face axis, 0.0 at column/row 0 and 1.0 at the far end."""
    return 0.0 if n <= 1 else i / (n - 1)


def paint_bar(img) -> None:
    """The harness plate. Two units deep with one unit outside the chestplate surface and one unit
    inside it, so the far column or row of every side face is buried; `south` is the whole part's
    hero face and carries the studs and the centre channel. The strap stands in front of the bar's
    lower middle, so those pixels are painted as the shadow it casts rather than as plate."""
    size, uv = CUBES["bar"]
    w, h, d = size
    f = faces(size, uv)
    strap_cols = (2, 3, 4)                    # the columns geo x -1.5..1.5 covered by the strap

    x0, y0, fw, fh = f["south"]               # 7 x 5, col 0 = max x, row 0 = top
    for j in range(fh):
        for i in range(fw):
            lum = FACE - round(Y_FALL * ramp(j, fh))
            if i == fw // 2:
                lum -= GROOVE                 # the centre channel the strap continues below
            elif abs(i - fw // 2) == 1:
                lum += 14                     # its two lit lips
            if j == fh - 1 and i in strap_cols:
                lum = INNER + 10              # in the strap's shadow
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))
    for i in (0, fw - 1):                     # four corner bolts, on the plate's own corners
        for j in (0, fh - 1):
            put(img, x0 + i, y0 + j,
                FACE - round(Y_FALL * ramp(j, fh)) + STUD + random.randint(-3, 3))

    x0, y0, fw, fh = f["up"]                  # 7 x 2, row 0 = the proud unit, row 1 = buried
    for i in range(fw):
        put(img, x0 + i, y0, UP + random.randint(-3, 3))
        put(img, x0 + i, y0 + 1, INNER + random.randint(-3, 3))

    x0, y0, fw, fh = f["down"]                # 7 x 2, same layout; the strap hides the middle
    for i in range(fw):
        put(img, x0 + i, y0, (INNER if i in strap_cols else DOWN) + random.randint(-3, 3))
        put(img, x0 + i, y0 + 1, INNER + random.randint(-3, 3))

    # The two side edges are the same face of a symmetric part, so they get the same treatment; only
    # the column order differs, because `west` runs front-to-back and `east` back-to-front.
    for name, proud in (("west", 1), ("east", 0)):
        x0, y0, fw, fh = f[name]              # 2 x 5, columns are depth, rows are height
        for j in range(fh):
            for i in range(fw):
                lum = (FLANK - round(Y_FALL * ramp(j, fh))) if i == proud else INNER
                put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    fill(img, f["north"], INNER)              # inside the torso


def paint_strap(img) -> None:
    """The keel tab. Three deep: one unit inside the chestplate, one inside the bar, and one proud
    of the bar - which is what keeps its `south` face off the bar's own plane. Two cubes flush at
    the same z would have put a 3x1 patch of coincident faces right in the middle of the part."""
    size, uv = CUBES["strap"]
    w, h, d = size
    f = faces(size, uv)

    x0, y0, fw, fh = f["south"]               # 3 x 3, col 0 = max x, row 0 = top
    for j in range(fh):
        for i in range(fw):
            lum = FACE + 12 - round(Y_FALL * ramp(j, fh))
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))
    put(img, x0 + fw // 2, y0 + fh // 2, FACE + STUD)   # the single bolt through the keel

    x0, y0, fw, fh = f["up"]                  # 3 wide x 3 deep; only row 0 clears the bar
    for i in range(fw):
        put(img, x0 + i, y0, UP - 12 + random.randint(-3, 3))
        put(img, x0 + i, y0 + 1, INNER + random.randint(-3, 3))
        put(img, x0 + i, y0 + 2, INNER + random.randint(-3, 3))

    x0, y0, fw, fh = f["down"]                # hangs below the bar, so rows 0 and 1 are both seen
    for i in range(fw):
        put(img, x0 + i, y0, DOWN + 12 + random.randint(-3, 3))
        put(img, x0 + i, y0 + 1, DOWN + random.randint(-3, 3))
        put(img, x0 + i, y0 + 2, INNER + random.randint(-3, 3))

    # Depth order along the columns: `west` runs front-to-back, `east` back-to-front. Column "front"
    # is inside the chestplate; the middle column is inside the bar for the top row only.
    for name, order in (("west", (0, 1, 2)), ("east", (2, 1, 0))):
        x0, y0, fw, fh = f[name]              # 3 x 3
        front, mid, back = order
        for j in range(fh):
            put(img, x0 + front, y0 + j, INNER + random.randint(-3, 3))
            put(img, x0 + mid, y0 + j,
                (INNER if j == 0 else FLANK - 20 - round(Y_FALL * ramp(j, fh))) + random.randint(-3, 3))
            put(img, x0 + back, y0 + j,
                FLANK - round(Y_FALL * ramp(j, fh)) + random.randint(-3, 3))

    fill(img, f["north"], INNER)              # inside the torso


def paint_tube(img, name: str, side: int) -> None:
    """One socket. `side` is +1 for the +x socket and -1 for the -x one, and it is the only thing
    that decides which of `west` / `east` is the lit outboard flank and which way the inboard-to-
    outboard gradient across `up` and `down` runs. The five axial units run from the mouth (index 0)
    to the end buried inside the torso (index 4); roughly the first two clear the bar."""
    size, uv = CUBES[name]
    w, h, d = size
    f = faces(size, uv)
    outboard, inboard = ("west", "east") if side > 0 else ("east", "west")

    def axial(a: int) -> int:
        """Value offset for axial unit `a`: a collar at the mouth, the bar's shadow behind it, and
        INNER once the unit is inside the bar. Shared by all four side faces so the bands line up
        around the tube's corners the way the horns' rings do."""
        return (COLLAR, 0, -SHADE)[a] if a < 3 else None

    x0, y0, fw, fh = f["south"]               # 3 x 3, THE MOUTH. col 0 = max x, row 0 = top
    for j in range(fh):
        for i in range(fw):
            if j == 0:
                lum = RIM                     # the lit upper lip of the socket
            elif j == 1:
                lum = MOUTH if i == 1 else RIM - 36
            else:
                lum = MOUTH + 12 if i == 1 else 74   # the lower lip, inside the bore's own shadow
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    for face, base in (("up", TUBE_UP), ("down", TUBE_DOWN)):
        x0, y0, fw, fh = f[face]              # 3 wide (x) x 5 tall (axial), row 0 = the mouth end
        for a in range(fh):
            off = axial(a)
            for i in range(fw):
                if off is None:
                    lum = INNER
                else:
                    # col 0 is min x on both faces, so which column is outboard follows `side`.
                    out = ramp(i, fw) if side > 0 else 1.0 - ramp(i, fw)
                    lum = base + off + round(8 * out)
                put(img, x0 + i, y0 + a, lum + random.randint(-3, 3))

    for face, base in ((outboard, FLANK), (inboard, IN)):
        x0, y0, fw, fh = f[face]              # 5 wide (axial) x 3 tall (y), row 0 = top
        # `west` columns run front-to-back, so the mouth is the last column; `east` is the reverse.
        for a in range(fw):
            col = (fw - 1 - a) if face == "west" else a
            off = axial(a)
            for j in range(fh):
                lum = INNER if off is None else base + off - round(Y_FALL * ramp(j, fh))
                put(img, x0 + col, y0 + j, lum + random.randint(-3, 3))

    fill(img, f["north"], INNER)              # the far end, inside the torso


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
    want = list(CUBES.values())
    assert found == want, f"CUBES disagrees with {GEO.name}: {found} vs {want}"


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
    paint_bar(img)
    paint_strap(img)
    paint_tube(img, "tube_l", +1)
    paint_tube(img, "tube_r", -1)

    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque == set(claimed), "painted pixels do not match the UV rectangles"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)})")


if __name__ == "__main__":
    main()
