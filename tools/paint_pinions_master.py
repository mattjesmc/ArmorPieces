"""
Paint the grayscale master and the static layer for the "pinions" part - a cut-down elytra, on the
back socket, and the first part in this mod that DOES something.

Kept as a script rather than a checked-in binary so the shape stays editable and reviewable: the
CUBES table below is the same cube list as
assets/armorpieces/armorpieces/decoration/pinions.json, and a change to one is meant to be a change
to the other. Output goes to tools/decoration_masters/pinions.png and pinions_static.png, which
sync_decoration_masters.py installs for the game to colour per trim material.

Master convention: luminance carries shading, alpha carries silhouette. The static layer's opaque
pixels keep their own colour, shaded by the master's value, instead of taking the material's.

**There is a static layer, and the reason is the recipe.** A pinion is an elytra that a smith cut
down and bolted to a bracket, so the membrane is not the smith's work and does not turn gold when
the bracket does. The frame - bracket, root rib, outboard spar, every edge - takes the trim
material; the membrane between them stays elytra. That is the same argument the horn made for
keratin, and it is what makes the part legible as "the flying one" in all sixteen materials rather
than only in the dark ones.

The alpha rake is the other half of the silhouette. A wing whose outline is a rectangle reads as a
paddle - the lesson the feathering learned the expensive way and the heel wings inherited - so the
inner-bottom corner of each vane is punched away and each tip is punched to a point at its outboard
bottom corner. On a plate one unit thick, punching through shows the far side's own face, which is
the same membrane, so the hole costs nothing; but the `down` and inboard edge faces run along the
cells the rake removes, and left painted they would hang in the air as a one-pixel outline of a wing
that is no longer there. They are masked by the same rule.

Geometry, checked against the body with tools/trace_geometry.py before it was painted:

  * The **bracket** spans body z 2..5, so it straddles the chestplate's back wall at z = 3 without
    putting a face on it, and its front face is buried on the body surface at z = 2 the way
    `wing_roots`' plate is. It stops at body y 7, a unit clear of the `sash`'s belt at y 8: those
    two sockets ride one bone, and the tool reports a plane shared between them as a defect.
  * The **vanes** hang from z = 5, a unit OUTBOARD of everything else the torso wears - the
    chestplate shell's back wall at 3 and the sash's rear bar at 4 both pass in front of them. That
    unit is what turns a hull overlap with the sash into 0.11 of clearance, and it is why the
    bracket is 3 deep rather than 2: it is a standoff, not a backplate.
  * **Reach is z = 6.01**, 3.01 past the chestplate. `wing_roots` on the same socket reaches 3.59
    past it, so this is the smaller projection of the two things that socket now carries.
  * The pair spans body x -7.38..7.38 and stops at body y 10.58, above the leg boxes at y 12. It
    sits behind the arms rather than through them at rest; a full backswing passes through it, which
    is true of every back part in the mod and of a vanilla cape.

The vanes are 1 unit thick, which makes their two broad faces the box's `north` and `south` - the
5-wide-by-6-tall rectangles. `bb = (-geo_x, 24 - geo_y, geo_z)`, so `south` is the geo +z face, the
one pointing away from the wearer's back and the only one a player normally sees, and `west` is the
geo +x face, which is the outboard edge on the left vane and the inboard edge on the right one.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "pinions.json"
MASTER_OUT = ROOT / "tools" / "decoration_masters" / "pinions.png"
STATIC_OUT = ROOT / "tools" / "decoration_masters" / "pinions_static.png"

TEX_W, TEX_H = 64, 32

# size (w, h, d) and uv (u, v), mirroring pinions.json - in its order, which is each vane followed
# by its own tip, because that is the bone chain.
CUBES = {
    "bracket": ((3, 6, 3), (0, 0)),    # the standoff, straddling the chestplate's back wall
    "vane_l":  ((5, 6, 1), (12, 0)),   # the shell, 18 deg outboard and 10 deg swept back
    "tip_l":   ((3, 4, 1), (24, 0)),   # the raked continuation, another 14 deg out
    "vane_r":  ((5, 6, 1), (32, 0)),
    "tip_r":   ((3, 4, 1), (44, 0)),
}

FACES = ("up", "down", "east", "north", "west", "south")

# Which geo-x end of a vane is its outboard edge. The left vane grows toward +x and the right one is
# its mirror, so every column rule below is written against the INNER end and one rule serves both.
OUTER_AT_MAX_X = {"vane_l": True, "tip_l": True, "vane_r": False, "tip_r": False}

random.seed(41)  # deterministic output - regenerating must not churn the PNG

# The elytra's own colour, kept out of the material ramp. A desaturated lilac-grey, which is what
# vanilla's elytra and a phantom membrane both read as next to any of the sixteen trim materials.
MEMBRANE = (136, 126, 150)

# Lit from above and behind, the same convention every part in this mod uses.
UP = 232        # a vane's root edge, and the bracket's top
DOWN = 44       # undersides
SOUTH = 190     # the outward broad face - the one a player sees
NORTH = 92      # the inward broad face, in the wearer's own shadow
OUTER = 212     # the outboard thin edge, lit along its whole span
INNER = 96      # the inboard thin edge, against the back

SPAR = 34       # the frame column down the outboard edge of a broad face
ROOT_RIB = 20   # the frame row across the top of a broad face, where it bolts to the bracket
VEIN = -34      # a membrane rib, every other row
SPAN_FADE = -36 # a vane darkening from its root to its trailing tip
RIVET = 26      # the bracket's mounting studs


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


def column(face: str, gx: int, w: int) -> int:
    """The u offset within a face for the geo-x column `gx`, where gx 0 is the geo -x end.

    `north` is viewed from -z with +x on the left, so its u runs with +x; `south`, `up` and `down`
    are all viewed with +x on the right, so theirs run against it. Getting this backwards is
    invisible on a symmetric face and off by the whole width on a raked one, which is exactly what
    every broad face here is."""
    return gx if face == "north" else w - 1 - gx


def put(img, x: int, y: int, lum: int, alpha: int = 255) -> None:
    if 0 <= x < TEX_W and 0 <= y < TEX_H:
        img.putpixel((x, y), (max(0, min(255, lum)), alpha))


def rake(name: str, gx: int) -> int:
    """Rows cut from the bottom of a broad face at geo-x column `gx`.

    Measured from the vane's INNER edge, so one rule mirrors. A vane loses its inner-bottom corner;
    a tip is cut to a point, keeping its full depth only at the outboard column. That is the
    difference between a wing and a plank, and it is spent entirely in alpha."""
    w = CUBES[name][0][0]
    inner = gx if OUTER_AT_MAX_X[name] else w - 1 - gx
    if name.startswith("tip"):
        return (2, 1, 0)[min(inner, 2)]
    return 1 if inner == 0 else 0


def solid(name: str, gx: int, row: int) -> bool:
    """Whether a broad-face cell survives the rake. Row 0 is the vane's root edge."""
    _, h, _ = CUBES[name][0]
    return row < h - rake(name, gx)


def is_frame(name: str, gx: int, row: int) -> bool:
    """Frame or membrane. The root row and the outboard column are the smith's metal; the rest of a
    broad face is the elytra he cut up, and takes the static colour instead of the material's."""
    w = CUBES[name][0][0]
    outer_gx = w - 1 if OUTER_AT_MAX_X[name] else 0
    return row == 0 or gx == outer_gx


def paint_vane(img, statics, name: str) -> None:
    size, uv = CUBES[name]
    w, h, _ = size
    f = faces(size, uv)
    outer_face = "west" if OUTER_AT_MAX_X[name] else "east"
    inner_face = "east" if OUTER_AT_MAX_X[name] else "west"

    # The two broad faces carry the membrane; the rake cuts them and everything that borders them.
    for face, base in (("north", NORTH), ("south", SOUTH)):
        x0, y0, _, _ = f[face]
        for row in range(h):
            for gx in range(w):
                if not solid(name, gx, row):
                    continue
                lum = base + round(SPAN_FADE * row / max(1, h - 1)) + random.randint(-4, 4)
                x, y = x0 + column(face, gx, w), y0 + row
                if is_frame(name, gx, row):
                    put(img, x, y, lum + (ROOT_RIB if row == 0 else SPAR))
                else:
                    put(img, x, y, lum + (VEIN if row % 2 == 0 else 0))
                    statics.putpixel((x, y), (*MEMBRANE, 255))

    # The root edge survives everywhere - the rake only ever cuts upward from the bottom. This face
    # is w wide by d = 1 tall.
    x0, y0, _, _ = f["up"]
    for gx in range(w):
        put(img, x0 + column("up", gx, w), y0, UP + random.randint(-4, 4))

    # The trailing edge exists only where the vane still reaches its bottom row.
    x0, y0, _, _ = f["down"]
    for gx in range(w):
        if rake(name, gx) == 0:
            put(img, x0 + column("down", gx, w), y0, DOWN + random.randint(-4, 4))

    # Outboard edge: full height, and the brightest line on the part - it is the spar the whole
    # shell hangs off. Inboard edge: only the rows the rake left at the inner column.
    x0, y0, _, _ = f[outer_face]
    for row in range(h):
        put(img, x0, y0 + row, OUTER + round(SPAN_FADE * row / max(1, h - 1)) + random.randint(-4, 4))
    inner_gx = 0 if OUTER_AT_MAX_X[name] else w - 1
    x0, y0, _, _ = f[inner_face]
    for row in range(h):
        if solid(name, inner_gx, row):
            put(img, x0, y0 + row, INNER + random.randint(-4, 4))


def paint_bracket(img) -> None:
    """The standoff the vanes bolt to. All metal, and the one place a rivet reads at this size: the
    same argument the heel wings' clasp makes, that a wing here is hardware rather than something
    the wearer grew."""
    size, uv = CUBES["bracket"]
    f = faces(size, uv)
    for face, base in (("up", UP), ("down", DOWN), ("east", INNER),
                       ("north", NORTH), ("west", INNER), ("south", SOUTH)):
        x0, y0, fw, fh = f[face]
        for y in range(y0, y0 + fh):
            for x in range(x0, x0 + fw):
                put(img, x, y, base + random.randint(-5, 5))
    # Two studs down the centre of the 3-wide-by-6-tall outward face, one per vane root.
    x0, y0, _, _ = f["south"]
    for row in (1, 3):
        put(img, x0 + 1, y0 + row, SOUTH + RIVET + random.randint(-3, 3))


def check_geometry() -> None:
    """CUBES must be the cube list of the shipped geometry, in order.

    Painting a texture for a shape the model no longer has is invisible to every other check here:
    both halves stay internally consistent while the rectangles slide off the faces they were drawn
    for. That is exactly how this file came to paint 4x6 vanes and 3x3 tips for a model carrying 5x6
    and 3x4 ones, at UVs that had moved to make room - which left three of tip_r's faces with no
    texture at all and put sixteen painted pixels where the model has no face."""
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
    """This master carves alpha, so it may not be checked against the net pixel for pixel the way an
    all-opaque one is - but the two failures either side of the rake still can be.

    A pixel painted outside the net is paint the model never samples. A face left with no opaque
    pixel at all is worse: the rake is meant to cut a corner off a wing, and a face it empties is a
    face that renders as a hole straight through the part."""
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
    statics = Image.new("RGBA", (TEX_W, TEX_H), (0, 0, 0, 0))
    paint_bracket(img)
    for name in ("vane_l", "vane_r", "tip_l", "tip_r"):
        paint_vane(img, statics, name)
    check_paint(img, claimed)
    MASTER_OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(MASTER_OUT)
    statics.save(STATIC_OUT)
    print(f"wrote {MASTER_OUT}")
    print(f"wrote {STATIC_OUT}")


if __name__ == "__main__":
    main()
