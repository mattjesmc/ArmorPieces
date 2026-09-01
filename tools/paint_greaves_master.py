"""
Paint the grayscale master for the "greaves" part.

Like the brooch, sash, tassets and spurs painters this does not merely claim that CUBES matches the
shipped geometry, it reads assets/armorpieces/armorpieces/decoration/greaves.json at run time and
asserts it (check_geometry). Output goes to tools/decoration_masters/greaves.png, which
sync_decoration_masters.py installs for the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

This master is 100% opaque, for the circlet's reason rather than the spurs'. A greave is a solid
plate; it has no fringe to fray and no gullet to punch, and because parts draw with
armorCutoutNoCull a hole cut in it would show the inside of the plate rather than the boot behind
it. Everything here is value.

What this part is, and what that costs the painter:

  * `greaves` is a MIRRORED pair - Attachment.of(LEFT_LEG, 0, 8, -2) plus Attachment.mirrored on the
    right - so the layer's scale(-1, 1, 1) runs on the right-hand copy and ONE master serves both.
    `west` is geo +x, outboard on both legs; `east` is geo -x, inboard on both. The outboard-lit /
    inboard-shadowed split therefore survives the flip - and it has to be painted rather than left to
    the engine, because vanilla's diffuse term gives +x and -x faces the same shade, as it does +z
    and -z. The pair MEETS at the midline: the ankle band reaches geo x = -0.25, so the two bands
    overlap over x -0.25..0.25 and their `north` faces are one plane, z = -3.4, with that whole half
    unit of it outside every shell. No master can separate two coincident faces, so the band's
    inboard column is painted as the seam it has become - dropped to SEAM, far under the rest of the
    band - and the composition is arranged so the eye reads the ribs either side of it rather than
    the join itself.

  * The hero face is `north`, the front of the shin, and this part now has exactly three of them
    worth the name: the two ridges' and the band's. The consequence the geometry cannot escape is
    that RELIEF BUYS NOTHING HEAD ON - a raised face parallel to the face behind it is lit
    identically to it, because vanilla's diffuse term shades by normal alone (up 1.0, down 0.5, +-z
    0.8, +-x 0.6). PLAN.md records it against a rib and the plate behind it; on this part it bites
    harder still, because every face the camera can see is parallel to the BOOT SURFACE behind it,
    0.1 out on the ribs and 0.4 on the band. The rendered proof is in PLAN.md. The design conclusion is that the front is made entirely
    of the values in this file - rib, bare boot, rib, band - and that the modelled relief exists for
    the three-quarter view and for the profile, not for the render a player sees first.

  * It rides the LEG bone, and so do the boots shell and the leggings shell over the leg. Burial down
    here is permanent: part and shell share the bone, so no INNER pixel ever uncovers - unlike the
    tassets, which had to paint one row as flank because the torso shell rides a different bone. The
    1.0 boots shell is geo x -1.1..4.9, y 11..25, z -3..3, and the plate is inside all six of those
    walls, its front face stopping 0.25 short of the shell's own. So 90 of this master's 180 opaque
    texels are on a cube no camera can reach, and what carries the part is 11 texels of `north` - the
    ridges' six free rows and the band's five columns - plus the slivers of flank, top and underside
    that clear the shell's front wall by a tenth of a unit and by four tenths.

  * There are no studs on this part. A bolt only reads against a plainly darker neighbour on both
    sides (the brooch's lesson, learned at three by three), and the widest face left in the light
    here is the band's five texels on a single row: a dropped bed under a stud would eat the band it
    was meant to sit on. The value that would have gone into rivets goes into the ridge-to-band
    junction instead, which is the one place this part has a shadow line to spend it on.

The face rectangles come from paint_circlet_master.faces(), copied verbatim: row one (v .. v+d)
holds up then down, each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west,
south with widths d, w, d, w.

Orientation inside each rectangle is the table PLAN.md records as measured, not recalled:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x              max z
    down            +y  (underside)      min x              max z
    west            +x  (outboard)       min z  (front)     min y (top)
    east            -x  (inboard)        max z  (back)      min y (top)
    north           -z  (front)          min x  (inboard)   min y (top)
    south           +z  (back)           max x  (outboard)  min y (top)

The two `up`/`down` rows on every cube run BACK to front, which on this part is what decides burial:
the boots shell's front wall is geo z = -3, and on all four cubes it falls inside row 1. Row 0 is
always inside the boot; row 1 is the row the wall crosses - 0.4 of it proud on the band, 0.1 on the
ridges, and none of it at all on the plate.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "greaves.json"
OUT = ROOT / "tools" / "decoration_masters" / "greaves.png"

TEX_W, TEX_H = 64, 32

# size (w, h, d) and uv (u, v), mirroring greaves.json in that file's own order. Geo extents at rest
# (left-hand copy; the right one is the mirror image in the body midline x = 0):
#   plate     - the shin plate; geo x -0.5..4.5, y 19.2..24.2, z -2.75..-0.75. Inside the 1.0 boots
#               shell on all six walls, front face 0.25 behind the shell's. It is the backing the
#               ridges and the band are bolted through, and it is never itself seen.
#   ridge_out - the outboard rib, 0.35 proud of the plate and 0.1 proud of the boot; geo x 2.75..3.75,
#               y 19.45..23.45, z -3.1..-1.1. Inset a quarter unit from the plate's top edge.
#   ridge_in  - the inboard rib, the same box at geo x 0.5..1.5. Its inboard 0.6 overhangs the RIGHT
#               boot's shell wall at x = 1.1 rather than being buried in it, which is only legal
#               because it clears that shell in z as well - it stands in front of the far boot, not
#               inside it, and the same 0.1 that clears the near shell clears the far one.
#   rim       - the ankle band, 0.65 proud of the plate and 0.4 proud of the boot; geo x -0.25..4.75,
#               y 22.75..23.75, z -3.4..-1.4. It crosses in front of both ridges and swallows the
#               last 0.7 of each.
# Shared planes with area in common, from an exhaustive pairwise face scan over the part, the
# mirrored twin, the naked body and all four armor shells: the two plates share four (they overlap a
# unit across the midline), the plate and the twin's inboard ridge share x = -0.5, and the two bands
# share four. Every one of those is inside a boots shell and therefore occluded except three of the
# band's - y 22.75, y 23.75 and z = -3.4 - which are the midline seam the docstring answers above.
CUBES = {
    "plate":     ((5, 5, 2), (0, 0)),
    "ridge_out": ((1, 4, 2), (14, 0)),
    "ridge_in":  ((1, 4, 2), (20, 0)),
    "rim":       ((5, 1, 2), (26, 0)),
}

random.seed(61)  # deterministic output - regenerating must not churn the PNG

# Calibrated against the ramp, not guessed. the material ramp interpolates dark -> mid over
# master values 0..127 and mid -> light over 128..255, so a master confined to one half only ever
# uses half of a material's ramp. The eleven texels that carry this part run a ridge root at 88 to a
# chamfered ridge crest at 254, which is most of the ramp on its own - it has to be, because with the
# plate gone into the boot there is no wide field left to spread the range over.
UP = 240        # a top face where it clears the boot's front wall
RIDGE = 236     # `north` on the outboard rib - the brightest face the front view has
RIDGE_IN = 208  # `north` on the inboard rib: the same face, painted as the shaded side
BAND = 214      # `north` on the ankle band, the one face of this part that is 0.4 clear
FLANK = 200     # the front sliver of an outboard face - all this part has of a profile
SEAM = 150      # the band's inboard column, where the pair's two bands lie in one plane
IN = 92         # an inboard face, looking across at the other boot
ROOT = 88       # a rib's last row, seven tenths of it behind the band
INNER = 38      # buried - in a shell, in the plate, behind the band, or in the mirrored twin
DOWN = 34       # an underside

RIM = 18        # the lit chamfer along a free top edge
FALL = 20       # top-to-bottom falloff down a standing face


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


def paint_plate(img) -> None:
    """The shin plate. Five wide, five tall, two deep, and entirely inside the boots shell.

    Every wall of the 1.0 boots shell is outside it - x -1.1..4.9 against the plate's -0.5..4.5,
    y 11..25 against 19.2..24.2, z -3..3 against -2.75..-0.75 - so not one of its ninety texels is
    reachable by a camera, at any leg angle, because part and shell ride the same bone and the shell
    is worn by definition whenever a boots decoration draws at all. That makes this cube the backing
    the ridges and the band are bolted through rather than a face of the part, and the honest paint
    for a permanently buried face is INNER: value spent here is value the eleven lit texels do not
    get, and a bright buried face only comes back as mipmap bleed into its neighbours in the atlas.

    Two consequences worth recording rather than rediscovering. The plate is the only cube of the
    part with no free edge anywhere, so it is also the only one with no chamfer, no falloff and no
    lateral split - there is nothing for those to describe. And the pair's two plates interpenetrate
    a full unit across the midline, x -0.5..0.5, sharing four planes: that is a z-fight in the
    geometry and it costs nothing at all, because both of them are inside both boots shells."""
    size, uv = CUBES["plate"]
    f = faces(size, uv)

    for face in ("north", "west", "east", "up", "down", "south"):
        fill(img, f[face], INNER)


def paint_ridge(img, key: str, north: int, flank: int) -> None:
    """One of the two ribs, 0.35 proud of the plate and 0.1 proud of the boot, inset a quarter unit
    from the plate's top edge and run down into the band at the bottom.

    Of the two depth units only the leading 0.1 clears the boots shell's front wall, so on every face
    here the column or row nearest the front is a tenth of a texel of light and everything behind it
    is INNER - and `south`, and the whole of `down` where the band closes over it, are INNER
    throughout. What that leaves is `north`, which is worth the entire cube: four texels tall, of
    which the top three stand free and the fourth is seven tenths swallowed by the band.

    That fourth row is the part's only shadow line and it is painted as one, at ROOT - far below both
    the rib above it and the band below it. It is what stops a rib and a band of similar value from
    fusing into an L, and it is the same trick the tassets' lap seam plays, spent here on the only
    junction this part has.

    `west` and `east` are the pair that would have done the rounding, and they no longer can: at 0.1
    of exposure they are a hairline. The outboard-lit / inboard-shadowed reading therefore moves up a
    level, from the two flanks of one rib to the two RIBS - the outboard one at RIDGE against the
    inboard one at RIDGE_IN, twenty-eight apart. Vanilla lights the two identically (its diffuse term
    shades +x and -x the same, and both ribs' `north` faces share a normal besides), so the entire
    difference between them is this file, and it is what keeps the front from reading as two
    identical bars stuck on a boot."""
    size, uv = CUBES[key]
    f = faces(size, uv)

    x0, y0, fw, fh = f["north"]          # 1 wide x 4 tall - the rib's own face, row 0 = top
    for j in range(fh):
        lum = ROOT if j == fh - 1 else north + (RIM if j == 0 else -round(FALL * ramp(j, fh)))
        put(img, x0, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["west"]           # 2 deep x 4 tall, col 0 = front (the tenth that clears)
    for j in range(fh):
        for i in range(fw):
            lit = i == 0 and j < fh - 1
            lum = (flank - round(FALL * ramp(j, fh))) if lit else INNER
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["east"]           # 2 deep x 4 tall, col 0 = BACK (buried), col 1 = front
    for j in range(fh):
        for i in range(fw):
            lit = i == fw - 1 and j < fh - 1
            lum = (IN + 4 - round(FALL * ramp(j, fh))) if lit else INNER
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["up"]             # 1 wide x 2 deep, rows run BACK to front
    for j in range(fh):
        put(img, x0, y0 + j, (INNER if j == 0 else UP - 12) + random.randint(-3, 3))

    fill(img, f["down"], INNER)          # closed over by the band
    fill(img, f["south"], INNER)         # the back cap, inside the plate


def paint_rim(img) -> None:
    """The ankle band, 0.4 proud of the boot and the frontmost thing on the part - it crosses in
    front of both ribs and swallows the last 0.7 of each. Five wide, one tall, two deep.

    Its `north` is the only face of this part that stands clear along its whole length, so it carries
    the lateral reading on its own: a ramp from the midline outboard, over five texels, which is the
    outboard-lit / inboard-shadowed split spread flat rather than folded round a rib. Column 0 is not
    on that ramp. It is the seam - the half unit where this band and the mirrored twin's occupy the
    same plane at z = -3.4 - and it is dropped to SEAM so that the pair reads as two bands meeting at
    the ankle rather than as one apron with a flaw down the middle. Nothing else can be done about
    two coincident faces from a texture, and a dark column at the join is what a join looks like.

    The band is the same width as the plate rather than inset inside it, offset a quarter unit
    outboard so that no side face of the two lands on one plane. The standing argument against a band as
    wide as its plate - that the pair renders as a capital I - does not arise here, because the plate
    is inside the boot and contributes no silhouette for a band to be measured against.

    Everything of this cube behind geo z = -3 is inside the boot. That leaves 0.4 of proud lip, which
    is row 1 of `up` and of `down` (rows run back to front) and column 0 of `west`. `east` gets none
    of it: at x = -0.25 that face is inside the twin's own band, which is the one place on this part
    where the occluder is the other copy of itself rather than a shell."""
    size, uv = CUBES["rim"]
    f = faces(size, uv)

    x0, y0, fw, fh = f["north"]          # 5 wide x 1 tall, col 0 = the midline seam, col 4 = outboard
    for i in range(fw):
        lum = SEAM if i == 0 else BAND - round(16 * (1 - ramp(i, fw)))
        put(img, x0 + i, y0, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["west"]           # 2 deep x 1 tall, col 0 = front (the proud lip)
    for i in range(fw):
        put(img, x0 + i, y0, (FLANK - 6 if i == 0 else INNER) + random.randint(-3, 3))

    fill(img, f["east"], INNER)          # inside the twin's band across the midline

    x0, y0, fw, fh = f["up"]             # 5 wide x 2 deep, rows run BACK to front
    for j in range(fh):
        for i in range(fw):
            lum = INNER if j == 0 else (UP - 14 - round(16 * (1 - ramp(i, fw))))
            put(img, x0 + i, y0 + j, lum + random.randint(-3, 3))

    x0, y0, fw, fh = f["down"]           # 5 wide x 2 deep, rows run back to front; the part's floor
    for j in range(fh):
        for i in range(fw):
            put(img, x0 + i, y0 + j, (INNER if j == 0 else DOWN) + random.randint(-3, 3))

    fill(img, f["south"], INNER)         # the back cap, entirely inside the plate


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
    paint_plate(img)
    paint_ridge(img, "ridge_out", RIDGE, FLANK)
    paint_ridge(img, "ridge_in", RIDGE_IN, FLANK - 24)
    paint_rim(img)

    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque == set(claimed), "the opaque set is not exactly the UV rectangles"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)})")


if __name__ == "__main__":
    main()
