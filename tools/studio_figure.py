"""
The studio figure: what the reference player wears when the game's textures are not here.

bb_rig.py shows a piece on a player wearing armor, and both of those are Mojang's PNGs when they
have been extracted from a jar on this machine. They are not ours to ship, so a clone without a
jar - and the web build, which is one - needs a figure of its own. This writes it:

    tools/studio/skin.png            a 64x64 player skin, drawn here: a plain mannequin
    tools/studio/skin_slim.png       the same on the 3-wide arms
    tools/studio/armor.png           the mod's own `plate` skin, baked in iron
    tools/studio/armor_leggings.png  its leggings sheet, likewise

The boxes are the same boxes - mc_humanoid transcribes them from the game and the rig builds the
same geometry either way - so fit and clipping are judged against the same shells. Only the pixels
differ, and the rig says so in its `armorpieces_figure` note.

The iron ramp comes from bake_skin.table, which reads the game's sheet when it is here and the
baked copy of that answer when it is not, so the output is the same on both kinds of machine.

    python tools/studio_figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

import bake_skin
import mc_humanoid
from sync_decoration_masters import face_rects

ROOT = Path(__file__).resolve().parent.parent
STUDIO = ROOT / "tools" / "studio"
PLATE = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "textures" / "entity" / "skin" / "plate"

# A mannequin: one warm grey for the whole body, lit from above - the top faces a step lighter,
# the undersides a step darker, the sides in between - and a face drawn on the head so the rig
# reads as facing somewhere. Nothing here is a person's skin, deliberately: it is a stand.
BASE = (176, 172, 164)
TOP = (204, 200, 192)
BOTTOM = (132, 129, 122)
SIDE = (160, 156, 149)
BACK = (152, 148, 141)
# The head is a little lighter than the body so it reads apart from the collar of a chestplate.
HEAD = (190, 186, 178)
HEAD_SIDE = (172, 168, 160)
EYE = (68, 70, 78)
EYE_LIGHT = (240, 240, 244)
SEAM = (140, 137, 130)

# Which face gets which shade, by the net's face names.
SHADES = {"up": TOP, "down": BOTTOM, "north": BASE, "south": BACK, "east": SIDE, "west": SIDE}
HEAD_SHADES = {"up": TOP, "down": BOTTOM, "north": HEAD, "south": HEAD_SIDE,
               "east": HEAD_SIDE, "west": HEAD_SIDE}


def paint_box(px, box: dict, shades: dict) -> None:
    size = tuple(int(v) for v in box["size"])
    for face, (x, y, w, h) in face_rects(size, box["tex"]).items():
        colour = shades[face]
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                px[xx, yy] = (*colour, 255)


def draw_face(px, box: dict) -> None:
    """Two eyes on the head's front face, at the rows and columns Steve's are, and a seam line
    across the brow so a browband has something to sit under."""
    x, y, w, h = face_rects((8, 8, 8), box["tex"])["north"]
    for ex in (1, 6):
        px[x + ex, y + 4] = (*EYE_LIGHT, 255)
    for ex in (2, 5):
        px[x + ex, y + 4] = (*EYE, 255)
    for xx in range(x, x + w):
        px[xx, y + 1] = (*SEAM, 255)


def skin(slim: bool) -> Image.Image:
    image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    px = image.load()
    # The base boxes only. The overlays (hat, jacket, sleeves, pants) stay transparent: a mannequin
    # wears nothing of its own, and a part on the `hat` shell should not compete with paint there.
    for box in mc_humanoid.player_boxes(slim):
        if box["inflate"]:
            continue
        if box["name"] == "head":
            paint_box(px, box, HEAD_SHADES)
            draw_face(px, box)
        else:
            paint_box(px, box, SHADES)
    # Seams at the waist and the shoulder, one texel, so the body's boxes read as boxes.
    for box in mc_humanoid.player_boxes(slim):
        if box["name"] in ("body",):
            x, y, w, h = face_rects(tuple(int(v) for v in box["size"]), box["tex"])["north"]
            for xx in range(x, x + w):
                px[xx, y + h - 1] = (*SEAM, 255)
    return image


def armor() -> dict[str, Image.Image]:
    lut = bake_skin.table("iron")
    out = {}
    for sheet in ("humanoid", "humanoid_leggings"):
        source = PLATE / f"{sheet}.png"
        if not source.is_file():
            sys.exit(f"error: the plate skin is missing at {source}")
        with Image.open(source) as image:
            out[sheet] = bake_skin.bake(image, lut)
    return out


def main() -> None:
    STUDIO.mkdir(parents=True, exist_ok=True)
    written = []
    for name, slim in (("skin.png", False), ("skin_slim.png", True)):
        path = STUDIO / name
        skin(slim).save(path)
        written.append(path)
    baked = armor()
    for sheet, name in (("humanoid", "armor.png"), ("humanoid_leggings", "armor_leggings.png")):
        path = STUDIO / name
        baked[sheet].save(path)
        written.append(path)
    for path in written:
        print(path.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
