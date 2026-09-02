"""
Install a decorative part's authored master into the mod's resources.

This script used to GENERATE sixteen recolours of every part, one per trim material, and the mod
shipped all 288 of them. It no longer does, because the game now colours a part at load time through
vanilla's own trim palettes - the same palettes, and the same remap, that vanilla has always used to
turn one greyscale trim pattern into every pattern-by-material sprite. See DecorationTextureManager.

So there is nothing left to generate. A part is two files at most, and this script's whole job is to
copy them from the authoring directory to the one the mod loads from, and to check on the way past
that they are shaped the way the loader expects:

    tools/decoration_masters/<part>.png            greyscale + alpha, the shape and its shading
    tools/decoration_masters/<part>_static.png     optional RGBA, the parts that are not metal
    tools/decoration_masters/<part>_<fitting>.png  optional greyscale + alpha, one per fitting the
                                                   part declares: the region a second material takes

It also checks the master against the part's geometry, which is the one defect no painter could
catch on its own before every paint_<part>_master.py grew a check_geometry(): a master painted for a
cube list the model no longer has stays perfectly self-consistent while its rectangles slide off the
faces they were drawn for. Four parts had drifted that way. The two symptoms are a face of the model
with no opaque pixel behind it - which renders as a hole straight through the part - and a painted
pixel outside every face rectangle, which is paint the model never samples.

The master's value channel is what gets mapped onto a material's ramp, and its alpha is the
silhouette. The static layer's opaque pixels keep their own colour instead of taking the material's,
shaded by the master's value - so a horn stays keratin and a sash stays cloth while the hardware
still turns gold. A fitting mask is greyscale like the master and, while the fitting is filled, its
opaque pixels take the mask's own value through the fitting's colour. The master stays the single
source of truth for the silhouette: a static or mask pixel where the master is transparent is not
drawn, and is reported here rather than silently ignored.

A companion file is recognised by its name: anything `<part>_<x>.png` where `<part>.png` exists
beside it. So a part called `helm_wings` is a master, and `helm_wings_static` is its layer.

Usage:
    python tools/sync_decoration_masters.py feathering
    python tools/sync_decoration_masters.py            # every master in the masters dir
"""

from __future__ import annotations

import json
import math
import shutil
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
MASTERS = ROOT / "tools" / "decoration_masters"
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration"
OUT = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "textures" / "entity" / "decoration"

STATIC_SUFFIX = "_static"
FACES = ("up", "down", "east", "north", "west", "south")


def check_master(path: Path) -> tuple[Image.Image, list[str]]:
    """Open a master and report anything the loader would read differently than intended."""
    image = Image.open(path)
    warnings: list[str] = []

    rgba = image.convert("RGBA")
    if not any(p[3] for p in rgba.getdata()):
        warnings.append("every pixel is transparent - nothing will draw")

    # The loader reads a master pixel's RED channel as its luminance, so a master painted in colour
    # would be mapped through the material ramp by its red alone. That is almost never what someone
    # meant: colour belongs in the static layer, which is what keeps it.
    coloured = sum(1 for r, g, b, a in rgba.getdata() if a and not (r == g == b))
    if coloured:
        warnings.append(
            f"{coloured} opaque pixel(s) are not grey - the loader reads only the red channel as "
            f"shading, so put colour in {path.stem}{STATIC_SUFFIX}.png instead"
        )
    return image, warnings


def net(size):
    """A cube's box-UV net in whole pixels. Rounds up, the way Blockbench does - the sash's knot is
    4.9 units tall on purpose and unwraps to 5 rows."""
    return tuple(int(math.ceil(v - 1e-9)) for v in size)


def face_rects(size, uv):
    """Per-face pixel rectangles (x, y, w, h) for one box-UV cube. Row one (v .. v+d) holds up then
    down, each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west, south with
    widths d, w, d, w - the two thin d-wide faces FIRST and THIRD."""
    w, h, d = net(size)
    u, v = uv
    return {
        "up":    (u + d, v, w, d),
        "down":  (u + d + w, v, w, d),
        "east":  (u, v + d, d, h),
        "north": (u + d, v + d, w, h),
        "west":  (u + d + w, v + d, d, h),
        "south": (u + d + w + d, v + d, w, h),
    }


def check_geometry(name: str, master: Image.Image) -> list[str]:
    """Report a master that no longer covers the faces of the geometry it is painted for.

    An empty face is not always a defect - the feathering cuts three of its own on purpose, each the
    buried half of a coincident pair, because a transparent pixel writes no depth and that is the
    cheapest way to keep two coplanar faces from z-fighting. So this names what it finds and leaves
    the judgement to the painter, which knows which of its faces are cut and asserts it."""
    path = GEO / f"{name}.json"
    if not path.is_file():
        return [f"no geometry at {path.relative_to(ROOT)} - nothing to check the net against"]

    doc = json.loads(path.read_text(encoding="utf-8"))
    warnings: list[str] = []
    if (doc["texture_width"], doc["texture_height"]) != master.size:
        warnings.append(f"{path.name} is {doc['texture_width']}x{doc['texture_height']}, "
                        f"the master is {master.size[0]}x{master.size[1]}")
        return warnings

    cubes = []

    def walk(bone):
        cubes.extend(bone.get("cubes", []))
        for child in bone.get("children", []):
            walk(child)

    for bone in doc["bones"]:
        walk(bone)

    px = master.convert("RGBA").load()
    width, height = master.size
    covered = set()
    empty = []
    for index, cube in enumerate(cubes):
        for face, (x, y, w, h) in face_rects(cube["size"], cube["uv"]).items():
            seen = 0
            for py in range(y, y + h):
                for pxl in range(x, x + w):
                    if 0 <= pxl < width and 0 <= py < height:
                        covered.add((pxl, py))
                        seen += px[pxl, py][3] > 0
            if not seen:
                empty.append(f"cube {index}.{face}")

    outside = sum(1 for y in range(height) for x in range(width)
                  if px[x, y][3] and (x, y) not in covered)
    if empty:
        warnings.append(f"{len(empty)} face(s) of {path.name} have no opaque pixel and will render "
                        f"as holes unless they are cut on purpose: {', '.join(empty)}")
    if outside:
        warnings.append(f"{outside} opaque pixel(s) lie outside every face rectangle of "
                        f"{path.name} - the master and the model disagree about the shape")
    return warnings


def check_static(path: Path, master: Image.Image) -> list[str]:
    """Report a static layer that does not line up with the master it belongs to."""
    warnings: list[str] = []
    layer = Image.open(path)
    if layer.size != master.size:
        sys.exit(f"{path.name}: static layer is {layer.size}, master is {master.size} - they must match")

    static_px = layer.convert("RGBA").load()
    master_px = master.convert("RGBA").load()
    width, height = master.size
    orphans = sum(
        1
        for y in range(height)
        for x in range(width)
        if static_px[x, y][3] and not master_px[x, y][3]
    )
    if orphans:
        warnings.append(f"{orphans} static pixel(s) lie outside the master's silhouette and will not draw")
    return warnings


def check_mask(path: Path, master: Image.Image) -> list[str]:
    """Report a fitting mask that the loader would read differently than intended."""
    warnings: list[str] = []
    mask = Image.open(path)
    if mask.size != master.size:
        sys.exit(f"{path.name}: mask is {mask.size}, master is {master.size} - they must match")

    mask_px = mask.convert("RGBA").load()
    master_px = master.convert("RGBA").load()
    width, height = master.size
    orphans = coloured = opaque = 0
    for y in range(height):
        for x in range(width):
            r, g, b, a = mask_px[x, y]
            if not a:
                continue
            opaque += 1
            if not master_px[x, y][3]:
                orphans += 1
            if not (r == g == b):
                coloured += 1
    if not opaque:
        warnings.append(f"{path.name} is entirely transparent - the fitting will change nothing")
    if orphans:
        warnings.append(f"{orphans} pixel(s) of {path.name} lie outside the master's silhouette and will not draw")
    if coloured:
        warnings.append(f"{coloured} pixel(s) of {path.name} are not grey - a mask is shading, and the "
                        f"loader reads only its red channel")
    return warnings


def companions(name: str) -> list[Path]:
    """Every `<name>_<x>.png` beside the master: the static layer and the fitting masks."""
    return sorted(p for p in MASTERS.glob(f"{name}_*.png") if p.stem != name)


def install(master_path: Path) -> None:
    name = master_path.stem
    master, warnings = check_master(master_path)

    warnings += check_geometry(name, master)

    extras = companions(name)
    for extra in extras:
        if extra.stem == f"{name}{STATIC_SUFFIX}":
            warnings += check_static(extra, master)
        else:
            warnings += check_mask(extra, master)

    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(master_path, OUT / master_path.name)
    for extra in extras:
        shutil.copy2(extra, OUT / extra.name)

    print(f"{name}: installed {1 + len(extras)} file(s) to {OUT}")
    for warning in warnings:
        print(f"  warning: {warning}")


def main() -> None:
    if not MASTERS.is_dir():
        sys.exit(f"No masters directory at {MASTERS}")
    wanted = sys.argv[1:]
    stems = {m.stem for m in MASTERS.glob("*.png")}
    masters = [m for m in sorted(MASTERS.glob("*.png"))
               if not ("_" in m.stem and m.stem.rsplit("_", 1)[0] in stems)]
    if wanted:
        masters = [m for m in masters if m.stem in wanted]
        missing = set(wanted) - {m.stem for m in masters}
        if missing:
            sys.exit(f"No master texture for: {', '.join(sorted(missing))}")
    if not masters:
        sys.exit("Nothing to install.")
    for master in masters:
        install(master)


if __name__ == "__main__":
    main()
