"""
Paint the grayscale master for the "feathering" part.

Kept as a script rather than a checked-in binary so the shape stays editable and reviewable: the CUBES
table below is the same cube list as
assets/armorpieces/armorpieces/decoration/feathering.json, and a change to one is meant to be a change
to the other. Output goes to tools/decoration_masters/feathering.png, which
sync_decoration_masters.py installs for the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette. Fully transparent pixels are
cut away by the armorCutoutNoCull render type, which is what turns a flat slab into a feather shape.

This is the second cut. The first shipped with two defects that PLAN.md deferred to pass A, and both
are fixed here; nothing about the plume's *proportions* is touched, because those were re-judged on a
body in Blockbench and `feather_column` below is byte-identical to the reviewed one.

**Fix 1 - the face rectangles.** The first cut walked the unwrap with `local = fx % (w + depth)` and
treated `local < w` as the thin edge face, which assumes row two is `[w][d][w][d]`. It is
`[d][w][d][w]`. Since the layout is periodic with period `w+d` that was a one-column shift, not a
scramble: the quill highlight landed on the first column of each big side face and the 1px edge faces
got the tail of the taper. Rectangles now come from `faces()`, which is the same helper every painter
since the circlet uses.

**Fix 2 - the direction inside a face**, which no painter before this one needed and none recorded.
The blade's big faces carry a gradient along the plume's length, so which texture column is the *brow*
end decides whether the crest peaks at the front or the back. Row two is a continuous band around the
box: left to right it runs geo -x, front, geo +x, back, and travelling right always travels the same
way around. So on the `east` rect (geo -x) the front is at the RIGHT edge, and on the `west` rect
(geo +x) the front is at the LEFT - the two big faces run in opposite texture directions. The first
cut ran both the same way, which is why its two sides disagreed about where the plume peaked by about
1.4 units of z. Checked against vanilla's own skin layout, which is the same unwrap: the head's
right-side face at (0,8) joins the face at (8,8) along the skin's shared column, so the front of the
head is at that rectangle's right edge.

Two consequences of `armorCutoutNoCull` that shape the code:

- The blade is one unit thick, so its two big faces are the *same* surface seen from either side. Any
  pixel cut on one and not the other is a hole you look through into the far face's interior. So the
  fringe mask and the jitter are computed ONCE per (column, row) and blitted to both faces, mirrored -
  never rolled twice.
- The top lid is only real geometry where the silhouette actually reaches the top of the box.
  Elsewhere it would be a 1px shelf floating above the carved outline, so it is carved too.

Value calibration, which is the other half of pass A's brief. the material ramp interpolates
dark -> mid over master values 0..127 and mid -> light over 128..255, so a master that never dips
below 127 only ever uses half of a material's ramp. The first cut's 300 opaque pixels ran 139..245
with not one under 127, which is why netherite read as mush. This one is built to span the range: the
barb troughs and the outer fringe sit well under 127 so a dark material has somewhere to be dark.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tools" / "decoration_masters" / "feathering.png"

TEX_W, TEX_H = 64, 32

# size (w, h, d) and uv (u, v), mirroring feathering.json.
CUBES = {
    "socket": ((2, 2, 6), (0, 0)),    # the mount that clamps the crest to the helmet
    "crest":  ((1, 8, 7), (0, 10)),   # the plume itself, one unit thick
    "tail":   ((1, 6, 7), (24, 10)),  # the trailing sweep, hung off the crest's back at 38 deg
}

# How far up from a blade's bottom edge its quill runs. Held at a constant height rather than at a
# fraction of the column, which is what the first cut did: a real shaft runs straight and it is the
# barbs around it that vary, so a quill that rises and falls with the outline reads as a painted
# stripe instead of as structure.
RACHIS_CREST = 1.6
RACHIS_TAIL = 1.6

SOCKET_UP = 242
SOCKET_DOWN = 34
BAND_HI = 206       # upper row of the socket's side faces
BAND_LO = 72        # lower row - the split is what stops a 2px band reading as a flat sticker
UNDER = 64          # the tail's underside, which light from above never reaches
RACHIS = 250        # the quill catches the light
BASE = 62           # the mass under the quill, in its own shadow
BARB_BASE = 76      # the barbs, from the quill outward
BARB_SPAN = 126
BARB_SWING = 34
FRONT_LEAN = 14     # the brow end catches light, the rear falls away
FRINGE_CUT = 0.28   # fraction of outline pixels cut away, eased from 0.45 in the re-proportioning

random.seed(7)  # deterministic output - regenerating must not churn the PNG


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


def fill(img, rect, lum: int, jitter: int = 6) -> None:
    x0, y0, w, h = rect
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            put(img, x, y, lum + random.randint(-jitter, jitter))


def feather_column(height: int, t: float) -> float:
    """
    Silhouette height of the plume at normalised position t along its length.

    A raised cosine, biased forward, so the crest rises quickly off the brow and tapers toward the
    back rather than sitting as a flat brick. Unchanged from the first cut - this curve is what was
    re-proportioned against a body in Blockbench, and re-cutting the master is not licence to
    re-judge it. It peaks at t = 0.397 and bottoms out at 0.35 of the height at either end; the dip
    at the crest's rear, before the tail rises again, is the deliberate double peak.
    """
    shaped = math.sin(math.pi * min(1.0, max(0.0, t)) ** 0.75)
    return height * (0.35 + 0.65 * shaped)


def crest_profile(s: float) -> float:
    """Silhouette height of the crest at s, measured from the brow end."""
    return feather_column(CUBES["crest"][0][1], s)


def tail_profile(s: float) -> float:
    """
    Silhouette height of the tail at s, measured from its root.

    The tail continues the taper rather than restarting it: it walks the back half of the same curve,
    tall where it leaves the crest and thinning to its tip. The root is the tail's -z end, since its
    cube runs z 0..7 out of a pivot sitting at the crest's rear.
    """
    return feather_column(CUBES["tail"][0][1], 0.5 * (1.0 - s))


def blade_cells(size, profile, rachis: float):
    """
    Paint one blade once, as a (column, row) -> (lum, alpha) table.

    Columns run front to back (s = 0 at the brow end), rows run top to bottom of the box. The table
    is built once and blitted to both big faces so the two sides of a one-unit blade agree pixel for
    pixel - see the module docstring on armorCutoutNoCull.
    """
    w, h, d = size
    cells: dict[tuple[int, int], tuple[int, int]] = {}
    for i in range(d):
        s = i / max(1, d - 1)
        column_h = profile(s)
        lean = FRONT_LEAN * (1.0 - 2.0 * s)
        for r in range(h):
            from_bottom = h - r
            if from_bottom > column_h:
                continue  # outside the silhouette - cut away
            if abs(from_bottom - rachis) <= 0.6:
                cells[(i, r)] = (RACHIS + random.randint(-4, 4), 255)
                continue
            if from_bottom < rachis:
                cells[(i, r)] = (BASE + int(lean) + random.randint(-6, 6), 255)
                continue
            # Above the quill: barbs sweeping up and back, fading toward the outer fringe.
            above = (from_bottom - rachis) / max(1.0, column_h - rachis)
            above = min(1.0, max(0.0, above))
            barb = math.sin(s * 26.0 + from_bottom * 0.9)
            lum = BARB_BASE + BARB_SPAN * (1.0 - above) + BARB_SWING * barb + lean
            alpha = 255
            if column_h - from_bottom < 1.0 and random.random() < FRINGE_CUT:
                alpha = 0  # fray the outline so it reads as feather rather than blade
            cells[(i, r)] = (int(lum) + random.randint(-7, 7), alpha)
    return cells


def paint_blade(img, name: str, profile, rachis: float, underside: bool) -> None:
    size, uv = CUBES[name]
    w, h, d = size
    f = faces(size, uv)
    cells = blade_cells(size, profile, rachis)

    # The two big faces are the same surface from either side, so they get the same table - mirrored,
    # because `east` (geo -x) carries the brow at its right edge and `west` (geo +x) at its left.
    ex, ey, _, _ = f["east"]
    wx, wy, _, _ = f["west"]
    for (i, r), (lum, alpha) in cells.items():
        put(img, ex + (d - 1 - i), ey + r, lum, alpha)
        put(img, wx + i, wy + r, lum, alpha)

    # The 1px edge faces: the leading edge catches light, the trailing one sits in shadow. Both take
    # their alpha from the end column beside them, so no cap juts past a frayed outline.
    for key, i, base in (("north", 0, 228), ("south", d - 1, 78)):
        x0, y0, _, _ = f[key]
        for r in range(h):
            cell = cells.get((i, r))
            if cell is None or cell[1] == 0:
                continue
            from_bottom = h - r
            fade = (from_bottom - 1) / max(1.0, h - 1)
            put(img, x0, y0 + r, int(base - 90 * fade) + random.randint(-5, 5))

    # The top lid, carved: it is only real surface where the silhouette reaches the top of the box.
    # In the cross unwrap the lid sits directly above the front face, so its bottom row is the brow.
    heights = [profile(i / max(1, d - 1)) for i in range(d)]
    crown = max(heights)
    ux, uy, _, _ = f["up"]
    for j in range(d):
        i = d - 1 - j  # row 0 of the lid is the back of the blade
        if heights[i] >= crown - 0.5:
            fill(img, (ux, uy + j, w, 1), 250, jitter=3)

    # The underside. Carving runs from the top down, so a blade's bottom edge is always solid and its
    # `down` face is real surface - but only the tail's is ever seen. The crest's sits at absolute
    # y = -2, exactly coplanar with the socket's `up` face, so it is left transparent: a cut-away
    # pixel writes no depth, which is the cheapest way to keep two coincident faces from z-fighting.
    if underside:
        fill(img, f["down"], UNDER, jitter=5)


def paint_socket(img) -> None:
    """The mount that clamps the crest to the helmet: banded metal, lit on top, dark at the base."""
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
                    lum += 34
                put(img, x0 + i, y0 + j, lum + random.randint(-4, 4))


def main() -> None:
    img = Image.new("LA", (TEX_W, TEX_H), (0, 0))
    paint_socket(img)
    paint_blade(img, "crest", crest_profile, RACHIS_CREST, underside=False)
    paint_blade(img, "tail", tail_profile, RACHIS_TAIL, underside=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
