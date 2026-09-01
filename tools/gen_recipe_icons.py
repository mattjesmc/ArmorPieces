"""
Generate stand-in inventory icons for the vanilla items that have no flat texture.

modpage draws each recipe by looking up a 16x16 PNG per ingredient. Most vanilla items have one:
`textures/item/<id>.png`. A handful do not, because the game renders them from a 3D model instead -
shields and banners are the two this mod crafts with, and both came out of `modpage build` as the
missing-texture checkerboard on the CurseForge and Modrinth recipe images.

There is no "correct" file to point at: the sprite a player sees is a render, not an asset. So these
two are drawn here and wired up through modpage's `recipes.icons` override.

Authored as pixel art rather than drawn procedurally, for the same reason gen_template_icons.py is:
at this size every pixel is a decision.

The palettes are SAMPLED from the real 26.2 client assets rather than picked by eye, so the icons
sit correctly beside the genuine vanilla sprites they share a crafting grid with:

    shield   oak_planks.png + iron_ingot.png   - the shield's own recipe, and its actual materials
    banner   entity/banner/base.png + stick.png - the banner cloth sheet, and its pole

Only the darkest outline of each is derived rather than sampled: an item sprite needs a border
darker than anything in the material texture, which by definition is not in it.

Usage:
    python tools/gen_recipe_icons.py           # write the PNGs
    python tools/gen_recipe_icons.py --sheet   # also write a magnified contact sheet to inspect
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "assets" / "icons"

SHIELD_PALETTE = {
    ".": (0, 0, 0, 0),
    "o": (0x3A, 0x2C, 0x17, 0xFF),  # outline (derived: oak's darkest, darkened)
    "h": (0xC2, 0x9D, 0x62, 0xFF),  # oak, lit edge
    "f": (0xAF, 0x8F, 0x55, 0xFF),  # oak, face
    "s": (0x67, 0x50, 0x2C, 0xFF),  # oak, shaded edge
    "I": (0xD8, 0xD8, 0xD8, 0xFF),  # iron boss, lit
    "i": (0xA8, 0xA8, 0xA8, 0xFF),  # iron boss
}

# A front-facing shield: rounded top, tapering to a point, iron boss at the centre. The vanilla
# render is tilted, but a tilt reads as a smear at 16x16 and the silhouette is what identifies it.
SHIELD = [
    "................",
    "...oooooooooo...",
    "..ohhhhhhhhhho..",
    "..ohffffffffso..",
    "..ohffffffffso..",
    "..ohffiiiiffso..",
    "..ohffiIIiffso..",
    "..ohffiIIiffso..",
    "..ohffiiiiffso..",
    "..ohffffffffso..",
    "..ohffffffffso..",
    "...ohffffffso...",
    "....ohffffso....",
    ".....ohffso.....",
    "......oooo......",
    "................",
]

BANNER_PALETTE = {
    ".": (0, 0, 0, 0),
    "P": (0x89, 0x67, 0x27, 0xFF),  # crossbar, lit
    "p": (0x49, 0x36, 0x15, 0xFF),  # crossbar
    "C": (0xF3, 0xF3, 0xF3, 0xFF),  # cloth, lit edge
    "w": (0xE4, 0xE4, 0xE4, 0xFF),  # cloth
    "d": (0xC9, 0xC9, 0xC9, 0xFF),  # cloth, shaded edge (derived)
}

# White cloth hung from a wooden crossbar, which is the shape the banner item reads as. The bar
# overhangs the cloth on both sides - that overhang is most of what tells a banner from a painting.
BANNER = [
    "................",
    "................",
    "..PPPPPPPPPPPP..",
    "..pppppppppppp..",
    "...Cwwwwwwwwd...",
    "...Cwwwwwwwwd...",
    "...Cwwwwwwwwd...",
    "...Cwwwwwwwwd...",
    "...Cwwwwwwwwd...",
    "...Cwwwwwwwwd...",
    "...Cwwwwwwwwd...",
    "...Cwwwwwwwwd...",
    "...Cwwwwwwwwd...",
    "...Cwwwwwwwwd...",
    "...dddddddddd...",
    "................",
]

ICONS = {
    "shield": (SHIELD, SHIELD_PALETTE),
    "white_banner": (BANNER, BANNER_PALETTE),
}


def render(rows, palette):
    if len(rows) != 16 or any(len(row) != 16 for row in rows):
        raise SystemExit("error: every icon must be exactly 16x16")
    image = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, key in enumerate(row):
            if key not in palette:
                raise SystemExit(f"error: no palette entry for {key!r} at ({x}, {y})")
            image.putpixel((x, y), palette[key])
    return image


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    images = {}
    for name, (rows, palette) in ICONS.items():
        image = render(rows, palette)
        image.save(OUT / f"{name}.png")
        images[name] = image
        print(f"wrote {(OUT / f'{name}.png').relative_to(ROOT)}")

    if "--sheet" in argv:
        scale, pad = 16, 8
        width = len(images) * (16 * scale + pad) + pad
        sheet = Image.new("RGBA", (width, 16 * scale + 2 * pad), (0x20, 0x20, 0x20, 0xFF))
        for index, image in enumerate(images.values()):
            magnified = image.resize((16 * scale, 16 * scale), Image.NEAREST)
            sheet.paste(magnified, (pad + index * (16 * scale + pad), pad), magnified)
        sheet.save(ROOT / "tools" / "recipe_icons_preview.png")
        print(f"wrote tools/recipe_icons_preview.png")


if __name__ == "__main__":
    main(sys.argv[1:])
