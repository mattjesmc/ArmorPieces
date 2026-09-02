"""
Write a fitting's mask from a painted master.

A fitting is a region of a part that takes a second material - the stone in the circlet, the cloth
of the sash - and the game finds that region in a mask beside the master:

    tools/decoration_masters/<part>_<fitting>.png

The mask is a greyscale sheet exactly like the master: opaque where the fitting is, value carrying
the shading. While the fitting is empty the game ignores it; while it is filled, every opaque mask
pixel takes the mask's OWN value through the fitting's colour - a second material's palette, or a
dye - in place of the master's. Alpha is still the master's, so a mask pixel outside the silhouette
never draws (and sync_decoration_masters.py reports one).

The simplest mask, and the one every painter here uses, is the master restricted to the faces of
the cubes the fitting covers: same shading, second colour. A painter that wants a gem cut
differently from the metal it sits in paints the mask by hand instead; the format is the same.

Usage, from a painter, after the master is painted:

    from fitting_mask import write_mask
    write_mask(img, faces(*CUBES["stone"]).values(), OUT.with_name("circlet_gemstone.png"))
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image


def write_mask(master: Image.Image, rects: Iterable[tuple[int, int, int, int]], out: Path) -> int:
    """Copy the master's pixels inside `rects` (x, y, w, h) into a new sheet and save it.

    Returns the number of opaque pixels written. Transparent master pixels stay transparent in the
    mask, so a silhouette cut into the master is cut into the mask too."""
    mask = Image.new("LA", master.size, (0, 0))
    source = master.convert("LA")
    count = 0
    for x0, y0, w, h in rects:
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                if 0 <= x < master.width and 0 <= y < master.height:
                    lum, alpha = source.getpixel((x, y))
                    if alpha:
                        mask.putpixel((x, y), (lum, alpha))
                        count += 1
    out.parent.mkdir(parents=True, exist_ok=True)
    mask.save(out)
    print(f"wrote {out} ({count} opaque px)")
    return count
