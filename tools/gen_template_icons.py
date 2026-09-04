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

Each icon also gets a hint of itself, written as a GUI sprite under `container/slot/`: what the
advanced smithing table draws in a socket or fitting slot that is still empty, the way the vanilla
smithing table shows a faint template in its own empty template slot. It is the icon with its card
taken off and its subject knocked out - see `hint` - and it is derived from the icon rather than
authored beside it, so the two can never drift apart.

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
# The hint form of the same icon, for the slot it belongs in while that slot is empty - vanilla's
# own `container/slot/smithing_template_armor_trim`, one file per template instead of one for all.
GHOST_OUT = (ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "textures"
             / "gui" / "sprites" / "container" / "slot")
# Vanilla draws every empty-slot hint in this one flat grey, on the 139 grey a slot's floor is.
GHOST = (0x55, 0x55, 0x55, 0xFF)

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
    "d": (0x8E, 0x1E, 0x3A, 0xFF),  # dye drop, shadow
    "D": (0xE0, 0x3C, 0x66, 0xFF),  # dye drop, lit
    "b": (0x3A, 0x5B, 0xA8, 0xFF),  # banner field, pattern
    "B": (0xE8, 0xE4, 0xD8, 0xFF),  # banner cloth
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
    # Not a socket: the fitting templates, which set a second material into a part already worn.
    # No armor silhouette, because they go on any of them. The bare one, which fits anything, is a
    # cut gem in an amber setting; the four named ones each show the thing that fills them - the
    # gem alone, a metal ring, a dye drop, a banner on its pole - inside the same card.
    # The skin is not a socket: what it changes is the armor's own surface, every texel of it. So
    # the amber that names a place on the other icons runs right around the piece here - the whole
    # outside is what a skin is - and the armor shows through the middle unchanged, because a skin
    # moves nothing.
    "skin": [
        "..........",
        "..........",
        "...****...",
        "..**aa**..",
        ".**aaaa**.",
        ".**.aa.**.",
        ".**aaaa**.",
        ".**....**.",
        ".*+....+*.",
        "..........",
    ],
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
    "fitting_gemstone": [
        "..........",
        "..........",
        "....GG....",
        "...GGGG...",
        "..GGGgGG..",
        "..GGgggG..",
        "...gggg...",
        "....gg....",
        "..........",
        "..........",
    ],
    "fitting_guard": [
        "..........",
        "...AAAA...",
        "..AA..AA..",
        ".AA....AA.",
        ".A......A.",
        ".a......a.",
        ".aa....aa.",
        "..aa..aa..",
        "...aaaa...",
        "..........",
    ],
    "fitting_inlay": [
        "..........",
        "....D.....",
        "....DD....",
        "...DDDD...",
        "...DDDD...",
        "..DDDDDD..",
        "..DDdddD..",
        "..DddddD..",
        "...dddd...",
        "..........",
    ],
    "fitting_banner": [
        "..........",
        ".*BBBBBB..",
        ".*BBBBBB..",
        ".*BbbbbB..",
        ".*BbbbbB..",
        ".*BBBBBB..",
        ".*BB..BB..",
        ".*........",
        ".*........",
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


def hint(anchor: str) -> Image.Image:
    """
    The icon as the empty slot wears it: the same art with its card taken off and its subject
    knocked out of it.

    Both of the card's borders go - the dark outline and the lit bevel inside it - which leaves the
    10x10 recess alone. That recess becomes the darker grey vanilla paints an empty-slot hint in,
    the armor piece is cut clean out of it so the slot's own floor shows through the hole, and the
    amber that names the socket stays exactly as it is. So the hint is the icon inverted, which is
    why it is still read as that icon: the shape is the same shape, and the one spot of colour is
    the one thing that told the twelve of them apart.
    """
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(INLAY[anchor]):
        for x, ch in enumerate(row):
            if ch in "+*":
                px[x + 3, y + 3] = PALETTE[ch]
            elif ch == ".":
                px[x + 3, y + 3] = GHOST
    return img


def icon_name(anchor: str) -> str:
    """crest -> crest_template; fitting_gemstone -> fitting_template_gemstone."""
    if anchor.startswith("fitting_"):
        return f"fitting_template_{anchor[len('fitting_'):]}"
    return f"{anchor}_template"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    GHOST_OUT.mkdir(parents=True, exist_ok=True)
    images = {}
    for anchor in INLAY:
        img = render(anchor)
        # The name the item model's select case points at, and the sprite the screen asks for by
        # the same name - see AdvancedSmithingScreen.
        name = icon_name(anchor)
        img.save(OUT / f"{name}.png")
        hint(anchor).save(GHOST_OUT / f"{name}.png")
        images[anchor] = img
    print(f"wrote {len(images)} icons to {OUT}")
    print(f"wrote {len(images)} hints to {GHOST_OUT}")

    if "--sheet" in sys.argv:
        scale, pad = 8, 2
        pitch = (16 + pad) * scale
        # The hints go on the row below, on the 139 grey of the slot floor they are drawn on.
        sheet = Image.new("RGBA", (len(images) * pitch, 2 * pitch), (24, 24, 28, 255))
        sheet.paste((139, 139, 139, 255), (0, pitch, sheet.width, sheet.height))
        for i, anchor in enumerate(images):
            for row, img in enumerate((images[anchor], hint(anchor))):
                big = img.resize((16 * scale, 16 * scale), Image.NEAREST)
                sheet.paste(big, (i * pitch, row * pitch), big)
        path = ROOT / "tools" / "template_icons_preview.png"
        sheet.save(path)
        print(f"sheet: {path}  ({', '.join(images)})")


if __name__ == "__main__":
    main()
