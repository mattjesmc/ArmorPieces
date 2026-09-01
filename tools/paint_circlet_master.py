"""
Paint the grayscale master for the "circlet" part.

Kept as a script rather than a checked-in binary so the shape stays editable and reviewable: the CUBES
table below is the same cube list as
assets/armorpieces/armorpieces/decoration/circlet.json, and a change to one is meant to be a change to
the other. Output goes to tools/decoration_masters/circlet.png, which sync_decoration_masters.py
installs for the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

Where this part differs from the feathering, deliberately: the circlet's silhouette IS its box - a
metal band has no fringe to cut away - so every painted pixel here is fully opaque and the whole
master is value. Alpha carving would only expose the band's interior, because armorCutoutNoCull draws
back faces too, so a hole punched in the top row would show the inside of the ring rather than the
helmet behind it.

The face layout below was measured, not recalled: a box (w, h, d) at uv (u, v) was placed in
Blockbench and its computed per-face UVs read back. Row one (v .. v+d) holds up then down, each w
wide, starting at u+d. Row two (v+d .. v+d+h) holds east, north, west, south with widths d, w, d, w.
Note the row-two order - the two thin d-wide faces come FIRST and THIRD, which is the detail worth
reading twice when a face lands one pixel off.
"""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tools" / "decoration_masters" / "circlet.png"

TEX_W, TEX_H = 64, 32

# size (w, h, d) and uv (u, v), mirroring circlet.json. The ring straddles the helmet wall: every
# piece is 2 deep with one unit outside the 1.0-inflate helmet surface and one unit buried in it.
CUBES = {
    "front":    ((12, 2, 2), (0, 0)),    # across the brow, 1 unit past each helmet corner
    "temple_l": ((2, 2, 10), (0, 6)),    # left side of the ring, front corner to back corner
    "temple_r": ((2, 2, 10), (26, 6)),   # right side
    "back":     ((8, 2, 2), (0, 20)),    # closes the ring behind the skull
    "stone":    ((2, 3, 3), (32, 0)),    # the raised centre boss, 1 unit above the band
}

random.seed(23)  # deterministic output - regenerating must not churn the PNG

# Light comes from above, as it does for an entity's ambient shading, so up faces are the brightest
# value in the master and down faces the darkest. The band's own two rows repeat that in miniature.
UP = 244
DOWN = 40
BAND_HI = 215       # upper row of a band face
BAND_LO = 78        # lower row - the split is what stops a 2px band reading as a flat sticker
STUD = 40           # the beading, every third column, added to whichever row it lands on
INNER = 90          # faces buried in the helmet - painted anyway, in case an anchor moves

# These numbers were calibrated against the ramp, not guessed. the material ramp interpolates
# dark -> mid over master values 0..127 and mid -> light over 128..255, so a master that never goes
# below ~127 only ever uses HALF of a material's ramp. The first cut of this one ran 168..238 and the
# gold render came out as one flat hue for exactly that reason; a shadow has to sit well under 127
# before it reads as a shadow.


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


def paint_band_face(img, rect) -> None:
    """One outward face of the ring: a bright upper row, a shaded lower row, beaded every third column.

    The beading is what stops a 2-pixel-tall band from reading as a flat sticker. It runs on a period
    of 3 from column 1, which on the 12-wide brow leaves an unbeaded column at each end and so lands
    symmetrically - and puts a bead at columns 4 and 7, immediately flanking the centre boss, so those
    two read as its setting. The 10- and 8-wide runs inherit the same pitch rather than fitting their
    own, because the pitch is what carries the eye around the corners of the ring.
    """
    x0, y0, w, h = rect
    for i in range(w):
        stud = i % 3 == 1
        for j in range(h):
            top = j < h / 2
            lum = BAND_HI if top else BAND_LO
            if stud:
                lum += STUD
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))


def paint_band(img, name: str, outward: tuple[str, ...]) -> None:
    size, uv = CUBES[name]
    f = faces(size, uv)
    fill(img, f["up"], UP)
    fill(img, f["down"], DOWN)
    for key in ("east", "north", "west", "south"):
        if key in outward:
            paint_band_face(img, f[key])
        else:
            fill(img, f[key], INNER, jitter=4)


def paint_stone(img) -> None:
    """The centre boss, as a cut cabochon: a hard highlight on the top row falling to shadow.

    Two units wide is too small for alpha to bevel - cutting a corner off a 2-wide face removes half
    the row - so the facet reads entirely in value, with the left column a shade brighter than the
    right to fix a light direction.

    **Three units deep, not two.** At two the stone's back face landed on head z = -5, which is the
    helmet shell's own front wall, and over the 2x1 patch where the stone rises above the band
    (y -7..-6) that wall is not covered by anything - so the two coplanar faces z-fought in the one
    place on the part a player looks at. The third unit buries the back face at z = -4 instead, the
    head box's front plane, which is inside the helmet and is the same burial the band already does.
    Found by tools/trace_geometry.py, which is the reason that tool exists.
    """
    size, uv = CUBES["stone"]
    f = faces(size, uv)
    fill(img, f["up"], 252, jitter=3)
    fill(img, f["down"], 30, jitter=3)
    fill(img, f["south"], INNER, jitter=4)  # buried in the helmet - see the depth note below

    # The bottom row runs near-black on every facet: that shadow line is the only thing separating the
    # boss from the band behind it, since both are the same trim material and get the same ramp.
    for key, base in (("north", (254, 176, 46)), ("east", (150, 104, 44)), ("west", (150, 104, 44))):
        x0, y0, w, h = f[key]
        for j in range(h):
            for i in range(w):
                lean = (10 if i == 0 else -10) if key == "north" else 0  # light from the upper left
                put(img, x0 + i, y0 + j, base[j] + lean + random.randint(-3, 3))


def main() -> None:
    img = Image.new("LA", (TEX_W, TEX_H), (0, 0))
    # `outward` names the faces a player can actually see; the rest sit inside the helmet shell.
    # The brow bar owns the ring's two front corners, so its end faces are outward; the temples' end
    # faces butt into it and the back bar's butt into the temples, so those stay inner.
    paint_band(img, "front", ("north", "east", "west"))
    paint_band(img, "temple_l", ("east", "west"))
    paint_band(img, "temple_r", ("east", "west"))
    paint_band(img, "back", ("south",))
    paint_stone(img)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
