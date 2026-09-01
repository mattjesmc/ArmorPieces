"""
Paint the grayscale master for the "feathering" part.

Kept as a script rather than a checked-in binary so the shape stays editable and reviewable: the CUBES
table below is the same cube list as
assets/armorpieces/armorpieces/decoration/feathering.json, and a change to one is meant to be a change
to the other. Output goes to tools/decoration_masters/feathering.png, which
sync_decoration_masters.py installs for the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

This is the third cut, and it exists because the second one was painting a shape the model no longer
had. The plume used to be three cubes - a socket and two one-unit blades whose feather outline was
cut into alpha by a cosine profile. It is now seven, and the outline lives in the geometry:

    socket   3 x 2 x 6   height  0.00 ..  2.00   z -3.00 .. 3.00   the clamp on the helmet
    blade    2 x 7 x 6   height  2.00 ..  9.00   z -1.75 .. 4.25   the plume itself, two thick
    spine    1 x 7 x 1   height  1.75 ..  8.75   z -2.75 ..-1.75   the leading quill, on the brow
    ridge    1 x 1 x 5   height  9.00 .. 10.00   z -1.50 .. 3.50   the crown, capping the blade
    boss     2 x 5 x 3   height  2.75 ..  7.75   z  4.00 .. 7.00   the knuckle the tail hinges on
    tail_up  1 x 3 x 5   height  6.74 .. 12.18   z  1.60 .. 7.39   the upper sweep, 38 deg back
    tail_lo  1 x 5 x 3   height  1.64 ..  7.42   z  2.77 .. 8.21   the lower lobe

Heights are measured up from the socket's underside and were read off tools/trace_geometry.py rather
than recalled. +Y in the geometry is DOWN, which is why the table above negates it.

**Where the alpha went.** The old master cut a fringe into every blade, on the argument that a blade
one unit thick has only one surface, so a hole punched through it shows the far face - which is the
same feather - and costs nothing. That argument is still exactly right, and it is still used, but it
now applies to two cubes rather than to all of them: only `tail_up` and `tail_lo` are one unit thick.
The blade is two, so a hole in it would show its own hollow interior the way the circlet's would, and
the ridge is bolted along its top, which a carved top row would leave floating. So the crest is
painted solid and the tail is frayed, and the part reads as a plume with a hard crest and a soft tail
rather than as one texture applied twice.

**The three faces that are cut on purpose**, each the enclosed half of a coincident pair:
`blade.down` on the socket's lid, `spine.south` on the blade's brow face and `ridge.down` on the
blade's top. Two coplanar opaque faces z-fight; a fully transparent pixel writes no depth, so cutting
the buried one is the cheapest fix there is. check_paint() asserts both halves of that - those three
faces carry no paint, and every other face carries some.

**Direction inside a face**, which the second cut established and which still holds. Row two of the
unwrap is a continuous band around the box: left to right it runs geo -x, front, geo +x, back, and
travelling right always travels the same way around. So on the `east` rect (geo -x) the front of the
part is at the RIGHT edge and on the `west` rect (geo +x) it is at the LEFT - the two big faces run
in opposite texture directions. Checked against vanilla's own skin layout, which is the same unwrap:
the head's right-side face at (0,8) joins the face at (8,8) along the skin's shared column, so the
front of the head is at that rectangle's right edge.

The blade is two units thick, so its `east` and `west` faces are two genuinely different surfaces -
the plume's left flank and its right flank - rather than one surface seen twice. They still take the
same table, mirrored, but now for the plainer reason that a plume standing on the centreline is
symmetric and a player sees both flanks in the same turn.

Value calibration. The material ramp interpolates dark -> mid over master values 0..127 and
mid -> light over 128..255, so a master that never dips below 127 only ever uses half of a material's
ramp - the first cut's 300 pixels ran 139..245 with not one under 127, which is why netherite read as
mush. Here the quill saturates and the mass under it, the undersides and every buried face sit well
below 127, so the visible pixels alone span the whole ramp.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "feathering.json"
OUT = ROOT / "tools" / "decoration_masters" / "feathering.png"

TEX_W, TEX_H = 64, 32

# size (w, h, d) and uv (u, v), mirroring feathering.json in its order - the socket, then the four
# cubes of the crest bone, then the two of the tail bone.
CUBES = {
    "socket":  ((3, 2, 6), (0, 0)),
    "blade":   ((2, 7, 6), (18, 0)),
    "spine":   ((1, 7, 1), (34, 0)),
    "ridge":   ((1, 1, 5), (38, 0)),
    "boss":    ((2, 5, 3), (50, 0)),
    "tail_up": ((1, 3, 5), (0, 13)),
    "tail_lo": ((1, 5, 3), (12, 13)),
}

FACES = ("up", "down", "east", "north", "west", "south")

# The enclosed half of each coincident pair of faces. See the module docstring: these are cut rather
# than painted, and check_paint() holds them to it in both directions.
CUT = {("blade", "down"), ("spine", "south"), ("ridge", "down")}

# Which edge of a tail cube hangs free, and how many rows the taper takes off it at the trailing end.
# `tail_up` sweeps up and back off the boss and frays along its top; `tail_lo` hangs down and back
# and frays along its bottom. The quill runs at RACHIS_TAIL from the OTHER edge - the attached one -
# because that is the end the lobe is carrying its own weight from.
TAIL = {
    "tail_up": ("top", 2),
    "tail_lo": ("bottom", 3),
}

# How far from a blade's attached edge its quill runs. Held at a constant height rather than at a
# fraction of the column: a real shaft runs straight and it is the barbs around it that vary, so a
# quill that rises and falls with the outline reads as a painted stripe instead of as structure.
RACHIS_CREST = 1.6
RACHIS_TAIL = 1.6

SOCKET_UP = 242
SOCKET_DOWN = 34
BAND_HI = 206       # upper row of the socket's side faces
BAND_LO = 72        # lower row - the split is what stops a 2px band reading as a flat sticker
CROWN = 250         # the ridge along the top of the blade, the highest metal on the part
UP_FACE = 232       # any other top face
UNDER = 64          # an underside, which light from above never reaches
RACHIS = 250        # the quill catches the light
BASE = 62           # the mass under the quill, in its own shadow
BARB_BASE = 76      # the barbs, from the quill outward
BARB_SPAN = 126
BARB_SWING = 34
FRONT_LEAN = 14     # the brow end catches light, the rear falls away
LEAD = 236          # the spine's own front face - the first thing on the part the light reaches
INNER = 88          # buried in another cube of the part or in the helmet - painted anyway
RIVET = 30          # a mounting stud on the socket or on the tail's knuckle
FRINGE_CUT = 0.28   # fraction of outline pixels frayed away along a tail's free edge

random.seed(7)  # deterministic output - regenerating must not churn the PNG


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


def put(img, x: int, y: int, lum: int, alpha: int = 255) -> None:
    if 0 <= x < TEX_W and 0 <= y < TEX_H:
        img.putpixel((x, y), (max(0, min(255, lum)), alpha))


def fill(img, rect, lum: int, jitter: int = 6) -> None:
    x0, y0, w, h = rect
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            put(img, x, y, lum + random.randint(-jitter, jitter))


def feather_cell(from_attached: float, h: int, rachis: float, s: float) -> int:
    """One cell of a feathered face: the quill, the mass under it, or a barb above it.

    `from_attached` is the distance in units from the edge the plume grows out of, so one rule serves
    a crest growing upward and a tail lobe hanging down. `s` runs 0 at the front of the part to 1 at
    the back, and is used only for the lean and to walk the barb wave along the length."""
    lean = FRONT_LEAN * (1.0 - 2.0 * s)
    if abs(from_attached - rachis) <= 0.6:
        return RACHIS + random.randint(-4, 4)
    if from_attached < rachis:
        return BASE + int(lean) + random.randint(-6, 6)
    above = min(1.0, max(0.0, (from_attached - rachis) / max(1.0, h - rachis)))
    swing = math.sin(s * 26.0 + from_attached * 0.9)
    return int(BARB_BASE + BARB_SPAN * (1.0 - above) + BARB_SWING * swing + lean) + random.randint(-7, 7)


def paint_socket(img) -> None:
    """The mount that clamps the crest to the helmet: banded metal, lit on top, dark at the base.
    Its underside lies on the helmet surface, which is the burial trick rather than a defect, so it
    is painted dark rather than cut - nothing is coplanar with it that could z-fight."""
    f = faces(*CUBES["socket"])
    fill(img, f["up"], SOCKET_UP, jitter=4)
    fill(img, f["down"], SOCKET_DOWN, jitter=4)
    for key in ("east", "north", "west", "south"):
        x0, y0, w, h = f[key]
        for i in range(w):
            rivet = i % 3 == 1
            for j in range(h):
                lum = BAND_HI if j < h / 2 else BAND_LO
                if rivet:
                    lum += RIVET
                put(img, x0 + i, y0 + j, lum + random.randint(-4, 4))


def paint_blade(img) -> None:
    """The plume itself. Two units thick and capped by the ridge, so nothing here is carved: the
    quill runs along its length near the socket and the barbs sweep up off it toward the crown."""
    size, uv = CUBES["blade"]
    w, h, d = size
    f = faces(size, uv)

    # The two flanks, from one table so the plume is symmetric about the centreline. `east` carries
    # the brow at its right edge and `west` at its left - see the module docstring.
    cells = {}
    for i in range(d):
        s = i / max(1, d - 1)
        for r in range(h):
            cells[(i, r)] = feather_cell(h - r, h, RACHIS_CREST, s)
    ex, ey, _, _ = f["east"]
    wx, wy, _, _ = f["west"]
    for (i, r), lum in cells.items():
        put(img, ex + (d - 1 - i), ey + r, lum)
        put(img, wx + i, wy + r, lum)

    # The brow face. The spine stands on its middle unit, but the spine is 1 wide against this face's
    # 2, so neither of its columns is fully covered and both are painted as seen.
    x0, y0, fw, fh = f["north"]
    for r in range(fh):
        lum = feather_cell(h - r, h, RACHIS_CREST, 0.0)
        for i in range(fw):
            put(img, x0 + i, y0 + r, lum + random.randint(-4, 4))

    # The back face is inside the boss over all but a quarter unit of its width.
    fill(img, f["south"], INNER, jitter=4)

    # The top, under the ridge for its middle unit and open to the sky either side of it. Row 0 of
    # the lid is the back of the blade, the way the cross unwrap folds it.
    x0, y0, fw, fh = f["up"]
    for j in range(fh):
        s = (fh - 1 - j) / max(1, fh - 1)
        fill(img, (x0, y0 + j, fw, 1), UP_FACE - round(28 * s), jitter=4)

    # `down` is coplanar with the socket's lid and is cut. See CUT.


def paint_spine(img) -> None:
    """The leading quill, standing a unit proud of the blade's brow face. It is the first metal the
    light reaches on a standing figure, so its front face is the brightest thing on the part after
    the crown, and its flanks fall away from it."""
    size, uv = CUBES["spine"]
    w, h, d = size
    f = faces(size, uv)

    x0, y0, fw, fh = f["north"]
    for r in range(fh):
        fade = r / max(1, fh - 1)
        fill(img, (x0, y0 + r, fw, 1), LEAD - round(70 * fade), jitter=4)

    for key in ("east", "west"):
        x0, y0, fw, fh = f[key]
        for r in range(fh):
            fade = r / max(1, fh - 1)
            fill(img, (x0, y0 + r, fw, 1), BAND_HI - round(96 * fade), jitter=4)

    fill(img, f["up"], UP_FACE, jitter=4)
    fill(img, f["down"], INNER, jitter=3)   # a quarter unit inside the socket

    # `south` is coplanar with the blade's brow face and is cut. See CUT.


def paint_ridge(img) -> None:
    """The crown capping the blade: one unit square in section and five long, and the only thing on
    the part a player looking down at it sees. The brightest values on the master."""
    size, uv = CUBES["ridge"]
    w, h, d = size
    f = faces(size, uv)

    x0, y0, fw, fh = f["up"]
    for j in range(fh):
        s = (fh - 1 - j) / max(1, fh - 1)
        fill(img, (x0, y0 + j, fw, 1), CROWN - round(34 * s), jitter=3)

    # The two flanks are a single row each, running front to back in opposite texture directions.
    for key, forward in (("east", False), ("west", True)):
        x0, y0, fw, fh = f[key]
        for i in range(fw):
            s = (i if forward else fw - 1 - i) / max(1, fw - 1)
            fill(img, (x0 + i, y0, 1, fh), BAND_HI - round(60 * s), jitter=4)

    fill(img, f["north"], CROWN - 20, jitter=3)
    fill(img, f["south"], BAND_LO, jitter=3)

    # `down` is coplanar with the blade's top and is cut. See CUT.


def paint_boss(img) -> None:
    """The knuckle at the back of the crest that the tail bone hinges on. Hardware, not feather: it
    takes a rivet on each flank the way the socket's band does, which is what keeps a five-unit block
    from reading as a continuation of the plume."""
    size, uv = CUBES["boss"]
    w, h, d = size
    f = faces(size, uv)

    fill(img, f["north"], INNER, jitter=4)   # a quarter unit inside the blade, and dark behind it
    fill(img, f["up"], UP_FACE - 18, jitter=4)
    fill(img, f["down"], UNDER, jitter=4)

    for key in ("east", "west"):
        x0, y0, fw, fh = f[key]
        for r in range(fh):
            fade = r / max(1, fh - 1)
            fill(img, (x0, y0 + r, fw, 1), BAND_HI - 24 - round(80 * fade), jitter=4)
        put(img, x0 + fw // 2, y0 + fh // 2, BAND_HI - 64 + RIVET)

    x0, y0, fw, fh = f["south"]
    for r in range(fh):
        fade = r / max(1, fh - 1)
        fill(img, (x0, y0 + r, fw, 1), BAND_LO + 46 - round(40 * fade), jitter=4)


def tail_cut(name: str, i: int) -> int:
    """Rows taken off a tail cube's free edge at depth column `i`, 0 at the attached end.

    Eased rather than linear so the taper starts slowly and runs out to a point, which is the
    difference between a feather and a wedge. It never reaches the full height, so the trailing cap
    keeps a row and the taper alone can never empty a face."""
    _, _, d = CUBES[name][0]
    span = TAIL[name][1]
    return round(span * (i / max(1, d - 1)) ** 1.3)


def tail_cells(name: str) -> dict:
    """Paint one tail lobe once, as a (column, row) -> (lum, alpha) table.

    Built once and blitted to both big faces so the two sides of a one-unit lobe agree pixel for
    pixel: any pixel cut on one and not the other is a hole you look through into the far face's
    interior. The fray is part of that table for the same reason."""
    size, _ = CUBES[name]
    w, h, d = size
    free, _ = TAIL[name]
    cells: dict[tuple[int, int], tuple[int, int]] = {}
    for i in range(d):
        s = i / max(1, d - 1)
        cut = tail_cut(name, i)
        # The fray is a trailing-edge effect: a feather frays where it hangs free, not where it is
        # bound into the knuckle, so column 0 is never frayed. Nor is a column the taper has already
        # worn down to a single texel - that texel is the tip, and taking it would put a hole through
        # whichever cap borders the column rather than a notch in the outline.
        frayable = i > 0 and h - cut > 1
        for r in range(h):
            # Rows come off whichever edge hangs free, and `from_attached` is measured from the other
            # one - the end the lobe grows out of.
            if free == "top":
                if r < cut:
                    continue
                from_attached = h - r
                outermost = r == cut
            else:
                if r >= h - cut:
                    continue
                from_attached = r + 1
                outermost = r == h - cut - 1
            lum = feather_cell(from_attached, h, RACHIS_TAIL, s)
            alpha = 0 if (outermost and frayable and random.random() < FRINGE_CUT) else 255
            cells[(i, r)] = (lum, alpha)
    return cells


def paint_tail(img, name: str) -> None:
    size, uv = CUBES[name]
    w, h, d = size
    f = faces(size, uv)
    cells = tail_cells(name)

    ex, ey, _, _ = f["east"]
    wx, wy, _, _ = f["west"]
    for (i, r), (lum, alpha) in cells.items():
        put(img, ex + (d - 1 - i), ey + r, lum, alpha)
        put(img, wx + i, wy + r, lum, alpha)

    # The two end caps are a single column each, and both take their alpha from the column of cells
    # beside them so no cap juts past a frayed outline.
    for key, i, base in (("north", 0, 228), ("south", d - 1, 78)):
        x0, y0, fw, fh = f[key]
        for r in range(fh):
            cell = cells.get((i, r))
            if cell is None or cell[1] == 0:
                continue
            fade = r / max(1, fh - 1)
            fill(img, (x0, y0 + r, fw, 1), int(base - 90 * fade), jitter=5)

    # The lid and the underside run along the lobe, one texel per depth column, and each exists only
    # where the row it caps survived the taper.
    for key, r, base in (("up", 0, UP_FACE), ("down", h - 1, UNDER)):
        x0, y0, fw, fh = f[key]
        for j in range(fh):
            i = fh - 1 - j            # row 0 of the lid is the trailing end of the lobe
            cell = cells.get((i, r))
            if cell is None or cell[1] == 0:
                continue
            fill(img, (x0, y0 + j, fw, 1), base - round(30 * (i / max(1, fh - 1))), jitter=4)


def check_geometry() -> None:
    """CUBES must be the cube list of the shipped geometry, in order.

    Painting a texture for a shape the model no longer has is invisible to every other check here:
    both halves stay internally consistent while the rectangles slide off the faces they were drawn
    for. That is exactly what happened to the second cut of this part - the plume was rebuilt from
    three cubes into seven and this file went on painting the three, which left thirty-one faces of
    the shipped model with no texture at all and a hundred and twenty-five painted pixels sitting
    where the model has no face."""
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


def check_paint(img, claimed: dict) -> None:
    """This master carves alpha, so it cannot be checked against the net pixel for pixel the way an
    all-opaque one is - but the two failures either side of the fray still can be.

    A pixel painted outside the net is paint the model never samples. A face left with no opaque
    pixel is worse: it renders as a hole straight through the part, and it is what a stale CUBES
    table produces. The three faces in CUT are the deliberate case and are asserted from the other
    direction - they must be *entirely* transparent, because a single stray pixel on one of them is
    a z-fight with the face it lies on."""
    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    stray = opaque - set(claimed)
    assert not stray, f"{len(stray)} painted pixel(s) lie outside every face rectangle: {sorted(stray)[:8]}"
    painted = {claimed[p] for p in opaque}
    for name in CUBES:
        for face in FACES:
            key = f"{name}.{face}"
            if (name, face) in CUT:
                assert key not in painted, f"{key} is meant to be cut - it is coplanar with the face it lies on"
            else:
                assert key in painted, f"{key} has no opaque pixel - it will render as a hole"


def main() -> None:
    check_geometry()
    claimed = check_layout()
    img = Image.new("LA", (TEX_W, TEX_H), (0, 0))
    paint_socket(img)
    paint_blade(img)
    paint_spine(img)
    paint_ridge(img)
    paint_boss(img)
    paint_tail(img, "tail_up")
    paint_tail(img, "tail_lo")
    check_paint(img, claimed)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    low = sum(1 for v in lums if v < 128)
    print(f"wrote {OUT} ({len(opaque)} opaque px of {len(claimed)} net, "
          f"values {min(lums)}-{max(lums)}, {low} under 127)")


if __name__ == "__main__":
    main()
