"""
Paint the grayscale master for the "helm_wings" part.

This was authored as `horns` and is not one. Kept, renamed, rather than deleted: a four-cube chain
that leaves the temple sweeping 64 degrees back through a cross-section deeper front-to-back than it
is wide is a swept fin in the sagittal plane, and a swept fin flanking a skull is a wing. It is a
good wing. What it is not is a horn, which now exists separately as `horns` - square-sectioned,
tightly confined in depth, and curling inward rather than raking back. The two share a socket and are
alternatives to each other, which is the whole point of one part per anchor.

Being a metal wing, this part stays 100% material-painted and carries no `_static` companion. The
horn does, because keratin is not metal; see paint_horns_master.py.

Kept as a script rather than a checked-in binary so the shape stays editable and reviewable: the
CUBES table below is the same cube list as
assets/armorpieces/armorpieces/decoration/helm_wings.json, and a change to one is meant to be a
change to the other. Output goes to tools/decoration_masters/helm_wings.png, which
sync_decoration_masters.py installs for the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette.

Like the circlet and unlike the feathering, this master is 100% opaque. A vane has no fringe to carve
away, and parts draw with armorCutoutNoCull, so a hole punched anywhere would show the *inside* of
the part rather than the sky behind it. Every pixel here is value.

Two things this part has that the circlet did not, and both come from its geometry:

  * It is one horn drawn twice, the second with scale(-1, 1, 1). One face of every cube points away
    from the head and one points at it, and after the mirror that is still true - so the outward face
    can be the lit one and the inward face the shadowed one, and the pair reads as a pair. Which name
    is which was derived, not guessed: bb = (-geo_x, 24 - geo_y, geo_z), so Blockbench's `west`
    (-X in Blockbench) is the geo +x face, the one facing away from the head, and `east` is the one
    facing the skull.

  * It is a chain of four cubes end to end, which is four silhouette steps that want explaining. The
    growth rings below are cut on a single axial coordinate measured from the boss, not per cube, so
    a ring lands at the same height on every face of every segment and the four boxes read as one
    horn. The segments' tops sit at axial 3, 6, 9 and 12, so a period of 3 puts exactly one ring in
    each - deliberately mid-segment rather than at a joint, where the step already reads.

The face layout was measured, not recalled - see paint_circlet_master.faces(), from which this one is
copied verbatim: row one (v .. v+d) holds up then down, each w wide, starting at u+d; row two
(v+d .. v+d+h) holds east, north, west, south with widths d, w, d, w. Note the row-two order: the two
thin d-wide faces come FIRST and THIRD.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "helm_wings.json"
OUT = ROOT / "tools" / "decoration_masters" / "helm_wings.png"

TEX_W, TEX_H = 64, 32

# size (w, h, d), uv (u, v), and the axial height of the cube's `up` face, mirroring helm_wings.json.
# `h` runs along the horn's own axis, so a side face's rows ARE the axial direction: row 0 is the
# tip-ward end of that cube. axial_top is that row's position on the shared axis, measured up from
# the boss's underside at the temple. Each cube overhangs one unit into the one below it, which is
# what keeps the rotated joints closed, so the axial spans overlap by one.
CUBES = {
    "boss":  ((3, 3, 4), (0, 0), 3),     # the socket, straddling the helmet wall - 1 unit buried
    "horn1": ((1, 4, 3), (15, 0), 6),    # first segment, 13 deg outboard and 16 deg back
    "horn2": ((1, 4, 2), (25, 0), 9),    # second, cumulative 20 / 38
    "horn3": ((1, 4, 2), (32, 0), 12),   # the tip, cumulative 25 / 64
}

random.seed(41)  # deterministic output - regenerating must not churn the PNG

# Light from above and from outboard, which is where a horn on a standing figure is lit from: the
# outward face is the bright one, the two flanks fall off front to back, and the face against the
# skull sits in its shadow. These are base values, before the rings and the axial gradient.
UP = 248        # the tip-ward cap of a segment
DOWN = 30       # the base-ward cap; only the boss's is ever seen, from below
WEST = 226      # outward, away from the head - the lit face
NORTH = 172     # front
SOUTH = 138     # back
EAST = 74       # inward, against the skull
INNER = 90      # buried in another cube or in the helmet - painted anyway, in case an anchor moves

RING = -70      # a growth ring, cut into whatever face value it lands on
LIP = 24        # the row immediately tip-ward of a ring, catching the light off the groove's edge
TIP_GAIN = 26   # brightening from the boss to the point, spread over the full 12 units of axis
RIVET = 26      # the boss's mounting stud

# Calibrated against the ramp rather than guessed. the material ramp interpolates dark -> mid
# over master values 0..127 and mid -> light over 128..255, so a master confined to the top half only
# ever uses half of a material's ramp - the mistake the circlet's first cut made. Here EAST with a
# ring on it bottoms out near 0 and WEST near the tip saturates, so the span is the whole ramp.


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


def fill(img, rect, lum: int, jitter: int = 5) -> None:
    x0, y0, w, h = rect
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            put(img, x, y, lum + random.randint(-jitter, jitter))


def axial(top: int, row: int) -> float:
    """Where a side face's row sits on the horn's shared axis. Row 0 is the tip-ward end."""
    return top - row - 0.5


def ring_shift(a: float) -> int:
    """The ring cut at this axial position: the groove itself, or the lit row just above it."""
    if int(a) % 3 == 1:
        return RING
    if int(a) % 3 == 2:
        return LIP
    return 0


def paint_side(img, rect, base: int, top: int) -> None:
    """One of the four faces running along the horn's axis: rings across, gradient toward the tip."""
    x0, y0, w, h = rect
    for j in range(h):
        a = axial(top, j)
        lum = base + ring_shift(a) + round(TIP_GAIN * a / 12.0)
        for i in range(w):
            put(img, x0 + i, y0 + j, lum + random.randint(-4, 4))


def paint_segment(img, name: str, inner_east: bool = False) -> None:
    size, uv, top = CUBES[name]
    f = faces(size, uv)
    fill(img, f["up"], UP - TIP_GAIN + round(TIP_GAIN * top / 12.0))
    fill(img, f["down"], DOWN if name == "boss" else INNER, jitter=4)
    paint_side(img, f["east"], INNER if inner_east else EAST, top)
    paint_side(img, f["north"], NORTH, top)
    paint_side(img, f["west"], WEST, top)
    paint_side(img, f["south"], SOUTH, top)


def check_geometry() -> None:
    """CUBES must be the cube list of the shipped geometry, in order.

    Painting a texture for a shape the model no longer has is invisible to every other check here:
    both halves stay internally consistent while the rectangles slide off the faces they were drawn
    for. That is exactly how this file's horn1 and horn2 came to be painted a unit wider than the
    model's, leaving a strip of every face unpainted on a chain that had since been slimmed."""
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
    want = [(size, uv) for size, uv, _ in CUBES.values()]
    assert found == want, f"CUBES disagrees with {GEO.name}: {found} vs {want}"


def check_layout() -> dict:
    """Every face rectangle must sit inside the texture and no two may overlap - a silent overlap
    would paint one cube's shading onto another's face and only show up on a model in game."""
    claimed = {}
    for name, (size, uv, _) in CUBES.items():
        for face, (x, y, w, h) in faces(size, uv).items():
            assert 0 <= x and x + w <= TEX_W, f"{name}.{face} runs off the texture in u"
            assert 0 <= y and y + h <= TEX_H, f"{name}.{face} runs off the texture in v"
            for py in range(y, y + h):
                for px in range(x, x + w):
                    prev = claimed.get((px, py))
                    assert prev is None, f"{name}.{face} overlaps {prev} at {(px, py)}"
                    claimed[(px, py)] = f"{name}.{face}"
    return claimed


def paint_boss_rivet(img) -> None:
    """A stud on the boss's outward face, so the socket reads as hardware bolted through the helmet
    rather than as the horn simply growing thicker. One stud, centred: the face is 4 wide by 3 tall,
    and two would leave no unmarked pixel between them. It lands on the boss's ring row on purpose -
    the groove is the darkest pixels on the whole cube, so seating the brightest ones inside it is
    what makes a 2x1 detail read at all at this scale."""
    size, uv, _ = CUBES["boss"]
    x0, y0, _, _ = faces(size, uv)["west"]
    for i in (1, 2):
        put(img, x0 + i, y0 + 1, WEST + RIVET + random.randint(-3, 3))


def main() -> None:
    check_geometry()
    claimed = check_layout()
    img = Image.new("LA", (TEX_W, TEX_H), (0, 0))
    # The boss's inward face is inside the head box, a unit behind the helmet wall; the three horn
    # segments' inward faces clear the helmet and are seen head-on from the front.
    paint_segment(img, "boss", inner_east=True)
    paint_boss_rivet(img)
    paint_segment(img, "horn1")
    paint_segment(img, "horn2")
    paint_segment(img, "horn3")

    # This master is 100% opaque, so the painted set must be exactly the net: a pixel short is a
    # face the model shows and the texture does not.
    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque == set(claimed), "painted pixels do not match the UV rectangles"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)})")


if __name__ == "__main__":
    main()
