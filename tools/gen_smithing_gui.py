"""Draws the advanced smithing table's background sheet.

The panel is vanilla's own container art rather than anything new: the 198/255/85 bevel a chest
screen wears, and the 55/139/255 wells its slots sit in. Both are two rules and a handful of
chamfer pixels, so the sheet is generated rather than painted - the layout constants here are the
ones AdvancedSmithingMenu and AdvancedSmithingScreen read, and moving a slot means moving a number
in both places and running this again.

    python tools/gen_smithing_gui.py
"""

from __future__ import annotations

import os

from PIL import Image

SHEET = 256

# The vanilla container palette, in the order a bevel uses them.
CLEAR = (0, 0, 0, 0)
OUTLINE = (0, 0, 0, 255)
HIGHLIGHT = (255, 255, 255, 255)
FACE = (198, 198, 198, 255)
SHADOW = (85, 85, 85, 255)
WELL = (139, 139, 139, 255)
WELL_SHADOW = (55, 55, 55, 255)

# ---- layout, mirroring the two Java classes -------------------------------------------------
WIDTH = 242
HEIGHT = 220

DISPLAY_X = 8
DISPLAY_Y = 20
# Two more than a slot is tall: the rows sit in bands with a pixel of air above and below, which is
# what lets a picked row's ground show around the slots on it rather than only behind them.
ROW_HEIGHT = 20
DISPLAY_SLOTS = 4

INVENTORY_X = 8
INVENTORY_Y = 138

# The right-hand column, top to bottom: the stand, the two crafting slots under it, and - drawn as
# widgets, not here - the Apply and Remove buttons under those.
STAND_X = 173
STAND_Y = 16
STAND_W = 62
STAND_H = 131

TEMPLATE_X = 187
MATERIAL_X = 205
INPUT_Y = 151


def panel(px, w: int, h: int) -> None:
    """The raised plate: black outline, two-pixel highlight top-left, two-pixel shadow bottom-right."""
    for y in range(h):
        for x in range(w):
            px[x, y] = FACE

    for x in range(2, w - 3):
        px[x, 0] = OUTLINE
    for x in range(3, w - 2):
        px[x, h - 1] = OUTLINE
    for y in range(3, h - 3):
        px[0, y] = OUTLINE
        px[w - 1, y] = OUTLINE
    px[1, 1] = px[w - 3, 1] = OUTLINE
    px[0, 2] = px[w - 2, 2] = OUTLINE
    px[1, h - 3] = px[2, h - 2] = OUTLINE
    px[w - 2, h - 2] = OUTLINE

    for x in range(2, w - 3):
        px[x, 1] = HIGHLIGHT
    for x in range(1, w - 3):
        px[x, 2] = HIGHLIGHT
    for y in range(2, h - 3):
        px[1, y] = px[2, y] = HIGHLIGHT
    px[3, 3] = HIGHLIGHT

    for y in range(3, h - 2):
        px[w - 3, y] = px[w - 2, y] = SHADOW
    for x in range(3, w - 1):
        px[x, h - 3] = SHADOW
    for x in range(3, w - 2):
        px[x, h - 2] = SHADOW
    px[w - 4, h - 4] = SHADOW

    # The chamfered corners: the plate's outline stops short of them, so it reads as rounded.
    for x, y in ((0, 0), (1, 0), (w - 3, 0), (w - 2, 0), (w - 1, 0),
                 (0, 1), (w - 2, 1), (w - 1, 1),
                 (w - 1, 2),
                 (0, h - 3),
                 (0, h - 2), (1, h - 2), (w - 1, h - 2),
                 (0, h - 1), (1, h - 1), (2, h - 1), (w - 2, h - 1), (w - 1, h - 1)):
        px[x, y] = CLEAR


def well(px, x: int, y: int, w: int, h: int) -> None:
    """A sunken area holding (x, y, w, h): dark on its top and left, white on its bottom and right."""
    for iy in range(y, y + h):
        for ix in range(x, x + w):
            px[ix, iy] = WELL
    for ix in range(x - 1, x + w):
        px[ix, y - 1] = WELL_SHADOW
    for iy in range(y - 1, y + h):
        px[x - 1, iy] = WELL_SHADOW
    for ix in range(x, x + w + 1):
        px[ix, y + h] = HIGHLIGHT
    for iy in range(y, y + h + 1):
        px[x + w, iy] = HIGHLIGHT
    px[x + w, y - 1] = WELL
    px[x - 1, y + h] = WELL


def main() -> None:
    image = Image.new("RGBA", (SHEET, SHEET), CLEAR)
    px = image.load()
    panel(px, WIDTH, HEIGHT)

    # The player's inventory and hotbar.
    for row in range(3):
        for col in range(9):
            well(px, INVENTORY_X + col * 18, INVENTORY_Y + row * 18, 16, 16)
    for col in range(9):
        well(px, INVENTORY_X + col * 18, INVENTORY_Y + 58, 16, 16)
    # The stand down the right edge, and the smithing table's own two slots below it.
    well(px, STAND_X, STAND_Y, STAND_W, STAND_H)
    well(px, TEMPLATE_X, INPUT_Y, 16, 16)
    well(px, MATERIAL_X, INPUT_Y, 16, 16)

    # Two things are NOT here, because both move with the piece being worked on and are drawn at
    # runtime over this face - see AdvancedSmithingScreen#extractBox and #extractDisplaySlots: the
    # row box with the neck that joins it to that piece, and the four armor slots themselves, since
    # the picked one steps out of the column and a well left behind would be a hole where it was.

    out = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "src", "main", "resources", "assets", "armorpieces",
        "textures", "gui", "container", "advanced_smithing.png",
    )
    image.save(out)
    print(f"{out}  {WIDTH}x{HEIGHT}")


if __name__ == "__main__":
    main()
