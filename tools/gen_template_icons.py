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

The SKIN templates are the exception, and they are not drawn at all: a skin template's icon IS the
skin - the front of its chestplate, lifted straight off the sheet that ships, levelled into the
card's own range and set in the recess. A skin is the armor's own surface, so a swatch of that
surface is not a symbol for the thing, it is the thing, and it cannot drift from what the player
will actually be wearing. It also means a skin added later gets its icon by existing.

Drawing them by hand was tried first and thrown out. Thirteen emblems in one palette at 10x10 come
out as thirteen grey lattices, and the ones whose identity is a CULTURE rather than a construction
cannot be drawn at that size at all - a spangenhelm needs more texels than the recess has. What a
skin does NOT need is the socket icons' other half: one skin template goes on any of the four
pieces, so there is no place to point at and no armor silhouette to point at it on.

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

import json
import sys
from pathlib import Path

from PIL import Image

import skin_sheets

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


# ---------------------------------------------------------------------------
# The skins: a swatch of the skin's own chestplate, not an emblem for it. See the module docstring.

SKIN_SHEETS = (ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "textures"
               / "entity" / "skin")
SKIN_MODELS = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "models" / "item"
SKIN_ITEM = (ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "items"
             / "skin_template.json")

# The band the card's own art occupies, from the armor's shadow to its lit edge. Every swatch is
# levelled into it: a master that lives in the middle of the ramp would otherwise come out as ten
# shades of one grey, and thirteen of those are one icon thirteen times.
SWATCH_LO, SWATCH_HI = 0x4A, 0xE8


def skins() -> list[str]:
    """Every skin with art in the resources. The icons follow what ships, not a list kept here."""
    if not SKIN_SHEETS.is_dir():
        return []
    return sorted(d.name for d in SKIN_SHEETS.iterdir() if (d / "humanoid.png").exists())


def swatch(skin: str) -> Image.Image:
    """The top ten rows of the chest's front face, greyscale, levelled to the card's range.

    The face is 8 wide and 12 tall and the recess is 10x10, so ten of the twelve rows are taken and
    NOTHING is resampled: a scaled sheet is a blurred sheet, and at sixteen pixels blur is the one
    thing a swatch cannot afford. The rows kept are the top ones - the collar, the shoulders and the
    breast, which is where a skin says most about itself; the hem is under a belt half the time.
    """
    x, y, width, _ = skin_sheets.rect_of("chest", "front")
    sheet = Image.open(SKIN_SHEETS / skin / "humanoid.png").convert("RGBA")
    face = sheet.crop((x, y, x + width, y + 10))
    px = face.load()
    values = [round(0.299 * r + 0.587 * g + 0.114 * b)
              for row in range(face.height) for col in range(face.width)
              for r, g, b, a in [px[col, row]] if a]
    low, span = (min(values), max(1, max(values) - min(values))) if values else (0, 1)
    out = Image.new("RGBA", face.size, (0, 0, 0, 0))
    dst = out.load()
    for row in range(face.height):
        for col in range(face.width):
            r, g, b, a = px[col, row]
            if not a:
                continue
            grey = round(0.299 * r + 0.587 * g + 0.114 * b)
            level = SWATCH_LO + round((grey - low) / span * (SWATCH_HI - SWATCH_LO))
            dst[col, row] = (level, level, level, 255)
    return out


def render_skin(skin: str) -> Image.Image:
    """The card with the skin's swatch in its recess, on the recess grey where the face is not."""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(CARD):
        for x, ch in enumerate(row):
            px[x, y] = PALETTE[ch]
    art = swatch(skin)
    src_px = art.load()
    ox, oy = 3 + (10 - art.width) // 2, 3 + (10 - art.height) // 2
    for y in range(art.height):
        for x in range(art.width):
            r, g, b, a = src_px[x, y]
            if a:
                px[ox + x, oy + y] = (r, g, b, 255)
    return img


def write_skin_models(names: list[str]) -> None:
    """One model per skin and the select that picks between them.

    One item carries every skin and chooses its look off the `armorpieces:skin` component, exactly
    as the fitting template chooses off `armorpieces:fitting`. Written here rather than by hand so
    that a new skin needs no JSON: draw it, sync it, run this. A pack's own skin cannot add a case -
    `minecraft:select` does not merge - so it falls back to the generic `skin_template` icon.
    """
    for skin in names:
        model = {"parent": "minecraft:item/generated",
                 "textures": {"layer0": f"armorpieces:item/skin_template_{skin}"}}
        (SKIN_MODELS / f"skin_template_{skin}.json").write_text(
            json.dumps(model, indent=2) + "\n", encoding="utf8")
    select = {"model": {
        "type": "minecraft:select",
        "property": "minecraft:component",
        "component": "armorpieces:skin",
        "cases": [{"when": f"armorpieces:{skin}",
                   "model": {"type": "minecraft:model",
                             "model": f"armorpieces:item/skin_template_{skin}"}}
                  for skin in names],
        "fallback": {"type": "minecraft:model", "model": "armorpieces:item/skin_template"},
    }}
    SKIN_ITEM.write_text(json.dumps(select, indent=2) + "\n", encoding="utf8")


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

    # The skins have no hint of their own: the advanced table has ONE skin place, and the generic
    # `skin_template` hint is what an empty one shows.
    skins_shipped = {skin: render_skin(skin) for skin in skins()}
    for skin, img in skins_shipped.items():
        img.save(OUT / f"skin_template_{skin}.png")
    write_skin_models(list(skins_shipped))
    print(f"wrote {len(skins_shipped)} skin icons to {OUT}, with their models and the select")

    if "--sheet" in sys.argv:
        scale, pad = 8, 2
        pitch = (16 + pad) * scale
        # The hints go on the row below, on the 139 grey of the slot floor they are drawn on, and
        # the skins on a third row under both.
        width = max(len(images), len(skins_shipped)) * pitch
        sheet = Image.new("RGBA", (width, 3 * pitch), (24, 24, 28, 255))
        sheet.paste((139, 139, 139, 255), (0, pitch, width, 2 * pitch))
        for i, anchor in enumerate(images):
            for row, img in enumerate((images[anchor], hint(anchor))):
                big = img.resize((16 * scale, 16 * scale), Image.NEAREST)
                sheet.paste(big, (i * pitch, row * pitch), big)
        for i, img in enumerate(skins_shipped.values()):
            big = img.resize((16 * scale, 16 * scale), Image.NEAREST)
            sheet.paste(big, (i * pitch, 2 * pitch), big)
        path = ROOT / "tools" / "template_icons_preview.png"
        sheet.save(path)
        print(f"sheet: {path}  ({', '.join(images)})")


if __name__ == "__main__":
    main()
