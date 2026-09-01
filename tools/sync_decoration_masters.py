"""
Install a decorative part's authored master into the mod's resources.

This script used to GENERATE sixteen recolours of every part, one per trim material, and the mod
shipped all 288 of them. It no longer does, because the game now colours a part at load time through
vanilla's own trim palettes - the same palettes, and the same remap, that vanilla has always used to
turn one greyscale trim pattern into every pattern-by-material sprite. See DecorationTextureManager.

So there is nothing left to generate. A part is two files at most, and this script's whole job is to
copy them from the authoring directory to the one the mod loads from, and to check on the way past
that they are shaped the way the loader expects:

    tools/decoration_masters/<part>.png         greyscale + alpha, the shape and its shading
    tools/decoration_masters/<part>_static.png  optional RGBA, the parts that are not metal

The master's value channel is what gets mapped onto a material's ramp, and its alpha is the
silhouette. The static layer's opaque pixels keep their own colour instead of taking the material's,
shaded by the master's value - so a horn stays keratin and a sash stays cloth while the hardware
still turns gold. The master stays the single source of truth for the silhouette: a static pixel
where the master is transparent is not drawn, and is reported here rather than silently ignored.

Usage:
    python tools/sync_decoration_masters.py feathering
    python tools/sync_decoration_masters.py            # every master in the masters dir
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
MASTERS = ROOT / "tools" / "decoration_masters"
OUT = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "textures" / "entity" / "decoration"

STATIC_SUFFIX = "_static"


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


def install(master_path: Path) -> None:
    name = master_path.stem
    master, warnings = check_master(master_path)

    static_path = MASTERS / f"{name}{STATIC_SUFFIX}.png"
    has_static = static_path.is_file()
    if has_static:
        warnings += check_static(static_path, master)

    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(master_path, OUT / master_path.name)
    if has_static:
        shutil.copy2(static_path, OUT / static_path.name)

    files = 2 if has_static else 1
    print(f"{name}: installed {files} file(s) to {OUT}")
    for warning in warnings:
        print(f"  warning: {warning}")


def main() -> None:
    if not MASTERS.is_dir():
        sys.exit(f"No masters directory at {MASTERS}")
    wanted = sys.argv[1:]
    masters = [m for m in sorted(MASTERS.glob("*.png")) if not m.stem.endswith(STATIC_SUFFIX)]
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
