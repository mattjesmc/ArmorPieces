"""
Generate stand-in inventory icons for the vanilla items that have no flat texture.

modpage draws each recipe by looking up a 16x16 PNG per ingredient. Most vanilla items have one:
`textures/item/<id>.png`. A handful do not, because the game renders them from a 3D model instead -
shields and banners, and the smithing table and loom, are what this mod crafts with, and each came
out of `modpage build` as the missing-texture checkerboard on the CurseForge and Modrinth recipe
images. The mod's own advanced smithing table is a block with the same problem.

There is no "correct" file to point at: the sprite a player sees is a render, not an asset. So these
are drawn here and wired up through modpage's `recipes.icons` override.

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

SMITHING_PALETTE = {
    ".": (0, 0, 0, 0),
    "o": (0x12, 0x13, 0x16, 0xFF),  # outline (derived: the top's darkest, darkened)
    "T": (0x49, 0x4B, 0x5F, 0xFF),  # top slab, lit
    "t": (0x36, 0x37, 0x3F, 0xFF),  # top slab
    "d": (0x2F, 0x30, 0x37, 0xFF),  # top slab, shaded
    "W": (0x4A, 0x1F, 0x1A, 0xFF),  # body, lit
    "w": (0x42, 0x1C, 0x17, 0xFF),  # body
    "s": (0x2F, 0x14, 0x11, 0xFF),  # body, shaded
    "i": (0x26, 0x27, 0x2D, 0xFF),  # tools on the front
    # Only the mod's table: the amber rim its top and front carry.
    "G": (0xE8, 0xC3, 0x3A, 0xFF),
    "g": (0xCF, 0xA5, 0x28, 0xFF),
}

# A smithing table seen from the front and slightly above: the dark slab on top, the dark-red
# body, the tools hung on the front. The mod's table is the same block with an amber rim.
SMITHING_TABLE = [
    "................",
    "..oooooooooooo..",
    ".oTTTTTTTTTTTTo.",
    ".oTttttttttttdo.",
    ".oTttttttttttdo.",
    ".odddddddddddoo.",
    ".oWWWWWWWWWWWso.",
    ".oWwiiwwwwiiwso.",
    ".oWwiiwwwwiiwso.",
    ".oWwwwwwwwwwwso.",
    ".oWwiiwwwwiiwso.",
    ".oWwiiwwwwiiwso.",
    ".oWwwwwwwwwwwso.",
    ".osssssssssssso.",
    "..oooooooooooo..",
    "................",
]

ADVANCED_SMITHING_TABLE = [
    "................",
    "..oooooooooooo..",
    ".oGGGGGGGGGGGGo.",
    ".oGttttttttttgo.",
    ".oGttttttttttgo.",
    ".oggggggggggggo.",
    ".oWWWWWWWWWWWso.",
    ".oWwiiwwwwiiwso.",
    ".oWwiiwGGwiiwso.",
    ".oWwwwwGGwwwwso.",
    ".oWwiiwwwwiiwso.",
    ".oWwiiwwwwiiwso.",
    ".oWwwwwwwwwwwso.",
    ".osssssssssssso.",
    "..oooooooooooo..",
    "................",
]

LOOM_PALETTE = {
    ".": (0, 0, 0, 0),
    "o": (0x1E, 0x16, 0x0B, 0xFF),  # outline (derived: the top's darkest, darkened)
    "F": (0xCA, 0xA6, 0x71, 0xFF),  # frame, lit
    "f": (0xB3, 0x8C, 0x51, 0xFF),  # frame
    "e": (0x80, 0x63, 0x37, 0xFF),  # frame, shaded
    "k": (0x52, 0x41, 0x27, 0xFF),  # the dark of the top
    "C": (0xB5, 0xA4, 0x9D, 0xFF),  # thread, lit
    "c": (0xA8, 0x95, 0x8C, 0xFF),  # thread
    "r": (0x84, 0x4F, 0x42, 0xFF),  # the red-brown of the sides
}

# A loom from the front: the pale wooden frame, the woven threads across its middle, the
# red-brown cloth beam at the sides - which is what tells it from a crafting table at a glance.
LOOM = [
    "................",
    "..oooooooooooo..",
    ".oFFFFFFFFFFFFo.",
    ".oFkkkkkkkkkkeo.",
    ".oFkCcCcCcCckeo.",
    ".oFkcCcCcCcCkeo.",
    ".oFkCcCcCcCckeo.",
    ".oFkcCcCcCcCkeo.",
    ".oFkkkkkkkkkkeo.",
    ".orffffffffffro.",
    ".orffffffffffro.",
    ".oFfffffffffeeo.",
    ".oFfo......ofeo.",
    ".oFfo......ofeo.",
    "..oo........oo..",
    "................",
]

HAY_PALETTE = {
    ".": (0, 0, 0, 0),
    "o": (0x4C, 0x36, 0x10, 0xFF),  # outline (derived: the side's darkest straw, darkened)
    "T": (0xCD, 0xB2, 0x08, 0xFF),  # top, lit
    "t": (0xAC, 0x8D, 0x08, 0xFF),  # top
    "k": (0x94, 0x7D, 0x10, 0xFF),  # top, the straw ends
    "e": (0x8B, 0x71, 0x10, 0xFF),  # top, shaded edge
    "H": (0xCB, 0xB6, 0x30, 0xFF),  # side straw, lit
    "h": (0xAB, 0x92, 0x25, 0xFF),  # side straw
    "s": (0x94, 0x80, 0x1E, 0xFF),  # side straw, shaded strand
    "d": (0x8A, 0x73, 0x20, 0xFF),  # side straw, dark
    "R": (0xA4, 0x51, 0x2B, 0xFF),  # binding tie
    "r": (0x92, 0x41, 0x23, 0xFF),  # binding tie, shaded
}

# A hay bale seen from the front and slightly above, the way the smithing table is drawn: the
# top's cut straw ends as a checker, the side's long strands, and the two red-brown ties that
# make it a bale rather than a yellow block. Palette sampled from hay_block_side.png and
# hay_block_top.png; only the outline is derived.
HAY_BLOCK = [
    "................",
    "..oooooooooooo..",
    ".oTTTTTTTTTTTTo.",
    ".oTtktktktktkeo.",
    ".oTktktktktkteo.",
    ".oeeeeeeeeeeeeo.",
    ".oHhhshhhshhhdo.",
    ".oHhshhhshhhsdo.",
    ".oRRRRRRRRRRRro.",
    ".oHhhshhhshhhdo.",
    ".oHshhhshhhshdo.",
    ".oHhhshhhshhhdo.",
    ".oRRRRRRRRRRRro.",
    ".odsddsddsddddo.",
    "..oooooooooooo..",
    "................",
]

ICONS = {
    "shield": (SHIELD, SHIELD_PALETTE),
    "white_banner": (BANNER, BANNER_PALETTE),
    "smithing_table": (SMITHING_TABLE, SMITHING_PALETTE),
    "advanced_smithing_table": (ADVANCED_SMITHING_TABLE, SMITHING_PALETTE),
    "loom": (LOOM, LOOM_PALETTE),
    "hay_block": (HAY_BLOCK, HAY_PALETTE),
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
