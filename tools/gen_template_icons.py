"""
Generate the item icon for each socket's smithing template.

One icon per DecorationAnchor plus one for the fitting template, and they have to be told apart at
16x16 in a full hotbar. The scheme
that does that: every icon is the same template card, and inside it sits the ARMOR PIECE the socket
belongs to (helmet / chestplate / leggings / boots) with the socket itself picked out in amber. So
the icon answers both questions a player has - what does this go on, and where - without reading the
tooltip, and the four silhouettes group the twelve templates into four families at a glance.

Authored as pixel art rather than drawn procedurally: at this size every pixel is a decision, and a
generator that "draws a helmet" would only be a worse way of writing the same ten strings.

Usage:
    python tools/gen_template_icons.py           # write the PNGs
    python tools/gen_template_icons.py --sheet   # also write a magnified contact sheet to inspect
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "textures" / "item"

PALETTE = {
    ".": (0, 0, 0, 0),
    "o": (0x2B, 0x25, 0x1C, 0xFF),  # card outline
    "f": (0x9A, 0x8F, 0x7A, 0xFF),  # card face
    "h": (0xC6, 0xBB, 0xA4, 0xFF),  # card face, lit edge
    "r": (0x36, 0x31, 0x28, 0xFF),  # recessed inlay
    "a": (0x76, 0x82, 0x8D, 0xFF),  # armor
    "A": (0x9E, 0xAB, 0xB6, 0xFF),  # armor, lit
    "+": (0xB8, 0x83, 0x14, 0xFF),  # socket accent, shadow
    "*": (0xFF, 0xCE, 0x4B, 0xFF),  # socket accent
    "g": (0x1E, 0x8A, 0x4C, 0xFF),  # gem, shadow
    "G": (0x5C, 0xE0, 0x8C, 0xFF),  # gem, lit
}

# The card. Its 10x10 recess (rows 3-12, cols 3-12) is where the armor art goes.
CARD = [
    "................",
    ".oooooooooooooo.",
    ".ohhhhhhhhhhhho.",  # lit top edge
    ".ohrrrrrrrrrrfo.",
    ".ohrrrrrrrrrrfo.",
    ".ohrrrrrrrrrrfo.",
    ".ohrrrrrrrrrrfo.",
    ".ohrrrrrrrrrrfo.",
    ".ohrrrrrrrrrrfo.",
    ".ohrrrrrrrrrrfo.",
    ".ohrrrrrrrrrrfo.",
    ".ohrrrrrrrrrrfo.",
    ".ohrrrrrrrrrrfo.",
    ".offffffffffffo.",
    ".oooooooooooooo.",
    "................",
]

# 10x10 inlays. Same armor silhouette across each family; only the amber changes.
INLAY = {
    "crest": [
        "....**....",
        "...*++*...",
        "...aaaa...",
        "..aaaaaa..",
        ".aaaaaaaa.",
        ".aa.aa.aa.",
        ".aaaaaaaa.",
        ".aa....aa.",
        ".aa....aa.",
        "..........",
    ],
    "brow": [
        "..........",
        "..........",
        "...aaaa...",
        "..aaaaaa..",
        ".a******a.",
        ".aa.aa.aa.",
        ".aaaaaaaa.",
        ".aa....aa.",
        ".aa....aa.",
        "..........",
    ],
    "horns": [
        "..........",
        "*........*",
        "*..aaaa..*",
        "+.aaaaaa.+",
        ".aaaaaaaa.",
        ".aa.aa.aa.",
        ".aaaaaaaa.",
        ".aa....aa.",
        ".aa....aa.",
        "..........",
    ],
    "pauldrons": [
        "..........",
        ".**....**.",
        "**aa..aa**",
        "*+aaaaaa+*",
        ".aaaaaaaa.",
        "..aaaaaa..",
        "..aaaaaa..",
        "..aaaaaa..",
        "..aa..aa..",
        "..........",
    ],
    "back": [
        "..........",
        "..........",
        ".aaa..aaa.",
        "*aaaaaaaa*",
        "*aaaaaaaa*",
        "+.aaaaaa.+",
        "..aaaaaa..",
        "..aaaaaa..",
        "..aa..aa..",
        "..........",
    ],
    "collar": [
        "..........",
        "..........",
        ".aaa**aaa.",
        ".aa*++*aa.",
        ".aaaaaaaa.",
        "..aaaaaa..",
        "..aaaaaa..",
        "..aaaaaa..",
        "..aa..aa..",
        "..........",
    ],
    "vambraces": [
        "..........",
        "..........",
        ".aaa..aaa.",
        ".aaaaaaaa.",
        "aaaaaaaaaa",
        "a.aaaaaa.a",
        "a.aaaaaa.a",
        "+.aaaaaa.+",
        "*.aa..aa.*",
        "..........",
    ],
    "belt": [
        "..........",
        "..........",
        ".********.",
        ".+aaaaaa+.",
        ".aaaaaaaa.",
        ".aaa..aaa.",
        ".aa....aa.",
        ".aa....aa.",
        ".aa....aa.",
        "..........",
    ],
    "tassets": [
        "..........",
        "..........",
        ".aaaaaaaa.",
        ".aaaaaaaa.",
        "*aaa..aaa*",
        "*aa....aa*",
        "+aa....aa+",
        ".aa....aa.",
        ".aa....aa.",
        "..........",
    ],
    "knees": [
        "..........",
        "..........",
        ".aaaaaaaa.",
        ".aaaaaaaa.",
        ".aaa..aaa.",
        ".aa....aa.",
        ".aa....aa.",
        ".++....++.",
        ".**....**.",
        "..........",
    ],
    "spurs": [
        "..........",
        "..........",
        "..........",
        ".aa....aa.",
        ".aa....aa.",
        ".aa....aa.",
        "+aa....aa+",
        "*aaa..aaa*",
        "*aaa..aaa*",
        "..........",
    ],
    "greaves": [
        "..........",
        "..........",
        "..........",
        ".a*a..a*a.",
        ".a*a..a*a.",
        ".a*a..a*a.",
        ".a+a..a+a.",
        ".aaa..aaa.",
        ".aaa..aaa.",
        "..........",
    ],
    # Not a socket: the fitting template, which sets a second material into a part already worn.
    # No armor silhouette, because it goes on any of them - a cut gem in an amber setting instead,
    # the one fitting every player will meet first.
    "fitting": [
        "..........",
        "....**....",
        "...*GG*...",
        "..*GGGG*..",
        ".*GGGgGG*.",
        ".*GGgggG*.",
        "..*gggg*..",
        "...*gg*...",
        "....**....",
        "..........",
    ],
}


def render(anchor: str) -> Image.Image:
    """The card with one inlay composited into its recess."""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(CARD):
        for x, ch in enumerate(row):
            px[x, y] = PALETTE[ch]
    for y, row in enumerate(INLAY[anchor]):
        for x, ch in enumerate(row):
            if ch != ".":
                px[x + 3, y + 3] = PALETTE[ch]
    return img


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    images = {}
    for anchor in INLAY:
        img = render(anchor)
        img.save(OUT / f"{anchor}_template.png")
        images[anchor] = img
    print(f"wrote {len(images)} icons to {OUT}")

    if "--sheet" in sys.argv:
        scale, pad = 8, 2
        sheet = Image.new("RGBA", (len(images) * (16 + pad) * scale, 16 * scale), (24, 24, 28, 255))
        for i, img in enumerate(images.values()):
            sheet.paste(img.resize((16 * scale, 16 * scale), Image.NEAREST),
                        (i * (16 + pad) * scale, 0), img.resize((16 * scale, 16 * scale), Image.NEAREST))
        path = ROOT / "tools" / "template_icons_preview.png"
        sheet.save(path)
        print(f"sheet: {path}  ({', '.join(images)})")


if __name__ == "__main__":
    main()
