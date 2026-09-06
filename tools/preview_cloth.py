"""
The cloth bake, in Python, and a contact sheet of what it produces.

The reference implementation of `ClothTextureManager`, the way `bake_skin.py` is the reference for
`SkinBake`: same steps, same numbers, no game. It exists because the only thing worth judging about a
garment is how it LOOKS on a material, and a round trip through the client to find out that a fold is
too dark is a slow way to move a number by ten.

The five steps, per texel, and they are the ones the Java does:

  1. the base - the armor's own texture, upsampled nearest, so the plate is untouched where the mask
     is transparent;
  2. the cut - where the mask is transparent, stop; and on a face the armor USES, where the armor
     is transparent, stop as well.  A face the armor paints nothing on at all - the box's top, the
     box's underside - is the garment's to use, and is never trimmed;
  3. the colour - the banner's design where the texel is on one of the two torso panels, the base dye
     everywhere else the mask covers;
  4. the value - the mask's own, plus the armor's lighting at that texel, at LIGHT;
  5. the ramp - `DecorationPalette.ofStaticColour`, the same three-stop rule a dye fitting goes
     through.

Both sheets a garment reaches: the chestplate's torso and arms, and - stacked under it in the same
cell - the leggings' legs, which is where the hem is. They are two textures on two models and there
is nothing to be gained by pretending otherwise, but a hem is judged against the garment it hangs
off, so they belong in one picture.

Usage:
    python tools/preview_cloth.py                    # a sheet of the shipped cloths on four metals
    python tools/preview_cloth.py --light 0.45       # the same at a different armor-light mix
    python tools/preview_cloth.py --sheet humanoid   # one armor sheet rather than both
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

import skin_sheets

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "tools" / ".mcassets"
MASKS = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "textures" / "entity" / "cloth"

# Must match ClothTextureManager.
LIGHT = 0.30
WIDTH = 256
GRID = (64, 32)
FRONT = skin_sheets.rect_of("chest", "front")
BACK = skin_sheets.rect_of("chest", "back")
# Every face of the torso box, for the per-face clip - see ClothTextureManager.paintedFaces.
FACES = [skin_sheets.rect_of("chest", f)
         for f in ("front", "back", "left", "right", "top", "bottom")]
FLAG = (20, 40, 1)
PLATE = (12, 22, 1)
SPRITE_SHEET = 64.0

# Vanilla's own diffuse colours, which is what a banner pass is tinted with.
DYES = {
    "white": 0xF9FFFE, "orange": 0xF9801D, "magenta": 0xC74EBD, "light_blue": 0x3AB3DA,
    "yellow": 0xFED83D, "lime": 0x80C71F, "pink": 0xF38BAA, "gray": 0x474F52,
    "light_gray": 0x9D9D97, "cyan": 0x169C9C, "purple": 0x8932B8, "blue": 0x3C44AA,
    "brown": 0x835432, "green": 0x5E7C16, "red": 0xB02E26, "black": 0x1D1D21,
}


def luma(rgb) -> float:
    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]


def static_ramp(rgb: int) -> list[tuple[int, int, int]]:
    """`DecorationPalette.ofStaticColour`: three stops around one colour, as a 256-entry table."""
    r, g, b = rgb >> 16 & 0xFF, rgb >> 8 & 0xFF, rgb & 0xFF
    dark = (round(r * 0.5), round(g * 0.5), round(b * 0.5))
    mid = (r, g, b)
    light = (round(r + (255 - r) * 0.5), round(g + (255 - g) * 0.5), round(b + (255 - b) * 0.5))

    def lerp(a, c, t):
        return tuple(round(a[i] + (c[i] - a[i]) * t) for i in range(3))

    return [lerp(dark, mid, v / 127) if v <= 127 else lerp(mid, light, (v - 127) / 128)
            for v in range(256)]


def lightmap(image: Image.Image, mix: float = LIGHT) -> list[list[int]]:
    """`SkinBake.lightmap`: the deviation from the middle of the image's own range, normalised."""
    px = image.load()
    values = sorted(luma(px[x, y][:3])
                    for y in range(image.height) for x in range(image.width) if px[x, y][3])
    if not values:
        return [[0] * image.width for _ in range(image.height)]
    lo = values[int(0.05 * (len(values) - 1))]
    hi = values[int(0.95 * (len(values) - 1))]
    mid = (lo + hi) / 2
    spread = max(1.0, hi - lo)
    rows = []
    for y in range(image.height):
        row = []
        for x in range(image.width):
            r, g, b, a = px[x, y]
            offset = max(-0.5, min(0.5, (luma((r, g, b)) - mid) / spread))
            row.append(round(mix * 255 * offset) if a else 0)
        rows.append(row)
    return rows


def panel(sheet: str, base: str, layers: list[tuple[str, str]]) -> Image.Image:
    """The banner's design, composited into the rectangle its sprites are painted for."""
    box = FLAG if sheet == "banner" else PLATE
    out = Image.new("RGBA", (box[0], box[1]), (0, 0, 0, 0))
    passes = [(f"{sheet}_base", base)] + [(name, colour) for name, colour in layers]
    for name, colour in passes:
        path = ASSETS / sheet / f"{name}.png"
        if not path.is_file():
            print(f"  (no sprite {path.name}, skipped)")
            continue
        with Image.open(path) as opened:
            sprite = opened.convert("RGBA")
        unit = sprite.width / SPRITE_SHEET
        x0 = y0 = round(box[2] * unit)
        face = (round(box[0] * unit), round(box[1] * unit))
        tint = DYES[colour]
        src, dst = sprite.load(), out.load()
        for y in range(box[1]):
            for x in range(box[0]):
                sx, sy = x0 + x * face[0] // box[0], y0 + y * face[1] // box[1]
                a = src[sx, sy][3]
                if not a:
                    continue
                # Alpha only: the sprite's own colour is vanilla's flag shading, and this garment
                # already has the mask's folds and the armor's light. See ClothTextureManager.pass.
                over = (tint >> 16 & 0xFF, tint >> 8 & 0xFF, tint & 0xFF)
                if a == 255:
                    dst[x, y] = (*over, 255)
                else:
                    under = dst[x, y]
                    dst[x, y] = (*[(over[i] * a + under[i] * (255 - a)) // 255 for i in range(3)], 255)
    return out


def within(rect, gx: float, gy: float) -> bool:
    return rect[0] <= gx < rect[0] + rect[2] and rect[1] <= gy < rect[1] + rect[3]


def painted_faces(armor: Image.Image) -> list[bool]:
    """Which faces of the torso box the armor paints anything at all on."""
    px = armor.load()
    out = []
    for x, y, w, h in FACES:
        out.append(any(px[x * armor.width // GRID[0] + c, y * armor.height // GRID[1] + r][3]
                       for r in range(h) for c in range(w)))
    return out


def clipped(painted: list[bool], gx: float, gy: float) -> bool:
    """Whether the cloth here is trimmed to the armor: yes on a face it uses, no on an empty one."""
    for i, rect in enumerate(FACES):
        if within(rect, gx, gy):
            return painted[i]
    return True


def bake(cloth: str, material: str, base: str, layers: list[tuple[str, str]],
         sheet: str = "shield", mix: float = LIGHT, armor_sheet: str = "humanoid",
         armor_override: Image.Image | None = None) -> Image.Image | None:
    """One garment in one design on one material, as a 256x128 armor sheet.

    `armor_sheet` picks which half: `humanoid` is the chestplate's, `humanoid_leggings` the hem. The
    net rectangles are the same on both - vanilla lays the leggings' waist box out exactly where the
    chestplate's torso box is, which is what makes a tunic's two halves line up - so the panels and
    the per-face clip need no second table here any more than they do in the Java.

    `armor_override` is the sheet to lay the garment over when it is not the material's own - a
    SKIN's bake, which is what the game hands this pass on skinned-and-clothed armor. The order is
    the game's: the skin decides what the plate is, the cloth is laid over it.
    """
    mask_path = MASKS / cloth / f"{armor_sheet}.png"
    armor_path = ASSETS / ("armor" if armor_sheet == "humanoid" else "armor_leggings") / f"{material}.png"
    if not mask_path.is_file() or (armor_override is None and not armor_path.is_file()):
        return None
    with Image.open(mask_path) as opened:
        mask = opened.convert("RGBA")
    if armor_override is not None:
        armor = armor_override.convert("RGBA")
    else:
        with Image.open(armor_path) as opened:
            armor = opened.convert("RGBA")

    scale = max(1, round(WIDTH / armor.width))
    width, height = armor.width * scale, armor.height * scale
    light = lightmap(armor, mix)
    design = panel(sheet, base, layers)
    fallback = DYES[base]
    ramps: dict[int, list] = {}

    painted = painted_faces(armor)
    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    src, msk, dsn, dst = armor.load(), mask.load(), design.load(), out.load()
    for y in range(height):
        for x in range(width):
            bx, by = x // scale, y // scale
            under = src[bx, by]
            mx, my = x * mask.width // width, y * mask.height // height
            m = msk[mx, my]
            if not m[3]:
                dst[x, y] = under
                continue
            gx, gy = x * GRID[0] / width, y * GRID[1] / height
            rect = FRONT if within(FRONT, gx, gy) else BACK if within(BACK, gx, gy) else None
            colour = fallback
            if rect is not None:
                px = min(design.width - 1, int((gx - rect[0]) / rect[2] * design.width))
                py = min(design.height - 1, int((gy - rect[1]) / rect[3] * design.height))
                pixel = dsn[px, py]
                if pixel[3]:
                    colour = pixel[0] << 16 | pixel[1] << 8 | pixel[2]
            # Clipped to the armor's silhouette, but only on a face the armor uses at all.
            if clipped(painted, gx, gy) and not src[bx, by][3]:
                dst[x, y] = under
                continue
            shade = max(0, min(255, m[0] + light[by][bx]))
            table = ramps.setdefault(colour, static_ramp(colour))
            dst[x, y] = (*table[shade], 255)
    return out


# The designs the sheet is judged on: one plain, one two-layer, one busy. Between them they show a
# flat field, a hard edge and a charge, which are the three things a panel can be asked to carry.
DESIGNS = [
    ("plain", "white", []),
    ("cross", "white", [("cross", "red"), ("border", "red")]),
    ("charge", "yellow", [("half_horizontal", "black"), ("creeper", "green")]),
]
MATERIALS = ["iron", "gold", "diamond", "netherite", "leather"]


def require_game() -> None:
    """The cloth preview composites the game's own banner pattern sprites over the game's own
    armor sheets. Both are game art with no derived stand-in, so without them there is nothing
    honest to draw - say so, rather than a sheet of blank plates."""
    missing = [s for s in ("banner", "shield") if not (ASSETS / s).is_dir()]
    if not (ASSETS / "armor").is_dir():
        missing.append("armor")
    if missing:
        raise SystemExit(
            "The cloth preview needs the game's banner pattern sprites and armor sheets, which are "
            f"not extracted here ({', '.join(missing)} missing under {ASSETS}). They are game art "
            "and nothing stands in for them: run python tools/vanilla_assets.py, or point it at "
            "your game with --jar or --minecraft (Use my game... in the editor).")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--light", type=float, default=LIGHT, help="armor-light mix (0 = none)")
    parser.add_argument("--cloth", default=None, help="one cloth rather than every shipped one")
    parser.add_argument("--sheet", default=None, choices=skin_sheets.SHEETS,
                        help="one armor sheet rather than both")
    args = parser.parse_args()
    require_game()

    cloths = [args.cloth] if args.cloth else sorted(
        d.name for d in MASKS.iterdir() if (d / "humanoid.png").exists())
    armor_sheets = [args.sheet] if args.sheet else list(skin_sheets.SHEETS)

    scale = 3
    cell = (64 * 4 * scale, 32 * 4 * scale * len(armor_sheets))
    columns = len(MATERIALS)
    lines = len(cloths) * len(DESIGNS)
    sheet = Image.new("RGBA", (cell[0] * columns, cell[1] * lines), (24, 24, 28, 255))

    line = 0
    for cloth in cloths:
        for name, base, layers in DESIGNS:
            for column, material in enumerate(MATERIALS):
                for half, armor_sheet in enumerate(armor_sheets):
                    img = bake(cloth, material, base, layers, mix=args.light, armor_sheet=armor_sheet)
                    if img is None:
                        # A garment that does not reach this sheet ships no mask for it, and the
                        # cell stays empty rather than repeating the half above.
                        continue
                    big = img.resize((cell[0], cell[1] // len(armor_sheets)), Image.NEAREST)
                    sheet.paste(big, (column * cell[0],
                                      line * cell[1] + half * cell[1] // len(armor_sheets)), big)
            line += 1
            print(f"{cloth:8} {name:8} {' '.join(MATERIALS)}")

    path = ROOT / "tools" / "cloth_preview.png"
    sheet.save(path)
    print(f"sheet: {path}  (light {args.light})")


if __name__ == "__main__":
    main()
