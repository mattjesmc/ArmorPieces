"""
The two sheets an armor skin is painted on: which texels the game samples, and what to call them.

A skin is the armor's OWN texture - not a part hung on a socket and not a trim painted over it. It
is one greyscale master pair on vanilla's grid:

    humanoid.png            64x32   helmet, chestplate and boots
    humanoid_leggings.png   64x32   the leggings' belt and legs

and the colour comes later, from the material the piece is made of (see bake_skin.py). So the whole
authoring surface is seven box-UV nets, about fifteen hundred texels, and every one of them belongs
to a cube whose size and UV offset are already written down - in mc_humanoid, transcribed from
`HumanoidModel.createBaseArmorMesh`. This module reads them from there rather than repeating them,
for the same reason bb_rig parses DecorationAnchor.java: a second copy of a number is a number that
drifts.

The nets, per sheet, are:

    humanoid            helmet (8x8x8 @ 0,0)   helmet_raised (8x8x8 @ 32,0)
                        chest  (8x12x4 @ 16,16)  arm (4x12x4 @ 40,16)  boot (4x12x4 @ 0,16)
    humanoid_leggings   waist  (8x12x4 @ 16,16)  leg (4x12x4 @ 0,16)

Two of them are worn by both limbs: the game builds the left arm and the left leg as MIRRORED cubes
at the same UV offset as the right, so `arm`, `boot` and `leg` are each painted once and appear on
both sides. And `helmet_raised` is the `hat` shell the HEAD slot keeps through
`retainPartsAndChildren` - half a unit proud of the helmet, and painted by no vanilla material.

Faces are named for the wearer, not for the compass: the rig flips x, so a cube's `east` face is on
the wearer's RIGHT. Anywhere a person has to read a face name, they read `front`, `back`, `right`,
`left`, `top`, `bottom`.

ASCII is the authoring form. A 64x32 sheet is 32 lines of 64 characters - small enough to read in a
tool reply and to write in one - where `.` is transparent, `0`-`9` and `a`-`f` are the sixteen grey
levels (level i is the value 17i, so `f` is white), and a SPACE means "leave this texel alone", which
is what makes a stamp over one region possible without redrawing the sheet around it.

Usage:
    python tools/skin_sheets.py --regions              # the net legend
    python tools/skin_sheets.py --show <png>           # any 64x32 sheet as ASCII, with the legend
    python tools/skin_sheets.py --vanilla netherite    # the vanilla pair, to draw against
    python tools/skin_sheets.py --new <skin>           # a blank master pair under tools/skin_masters
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image

import mc_humanoid
from sync_decoration_masters import ROOT, face_rects

# The mod's own skins, one of which stands in for a vanilla outline when the game is not here.
SHIPPED_SKINS = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "textures" / "entity" / "skin"
STUDIO_OUTLINE = "plate"

MASTERS = ROOT / "tools" / "skin_masters"
ASSETS = ROOT / "tools" / ".mcassets"

SHEET_W, SHEET_H = 64, 32

# The two sheets, by the name the game's equipment renderer gives their folder.
SHEETS = ("humanoid", "humanoid_leggings")

# mc_humanoid's texture key for a slot -> our sheet name.
_SHEET_OF = {"armor": "humanoid", "armor_leggings": "humanoid_leggings"}

# What to call each armor cube. One name per NET: the mirrored left limbs share the right's.
_REGION_OF = {
    "head_helmet": "helmet",
    "hat_helmet": "helmet_raised",
    "body_chestplate": "chest",
    "right_arm_chestplate": "arm",
    "right_leg_boots": "boot",
    "body_leggings": "waist",
    "right_leg_leggings": "leg",
}

# Which of them are drawn on both sides of the body.
_BOTH_SIDES = {"arm", "boot", "leg"}

# A face by what the wearer would call it. The rig mirrors x, so east is the wearer's right.
ANATOMY = {"up": "top", "down": "bottom", "north": "front",
           "south": "back", "east": "right", "west": "left"}
FACES = ("top", "bottom", "front", "back", "right", "left")
_COMPASS = {v: k for k, v in ANATOMY.items()}

LEVELS = "0123456789abcdef"
CLEAR = "."
KEEP = " "

# The face opening. Netherite is the only vanilla set that wraps the cheeks, and it leaves the face
# itself transparent - which is the shape a `brow` part is designed to sit in front of. A skin that
# painted a visor would be arguing with seven parts, so this window has to stay open, and check_skin
# says so. Columns and rows are within `helmet.front`, whose own rectangle is 8x8.
FACE_WINDOW = (1, 3, 6, 5)  # x, y, w, h inside helmet.front


def regions(sheet: str | None = None) -> dict:
    """Every net, keyed by region name: its sheet, box size, UV offset, inflate and face rectangles.

    Built from mc_humanoid.armor_boxes so a change to the game's armor mesh arrives here on its own.
    Mirrored boxes are dropped: they carry the same UV offset as the box they mirror, so they are
    the same rectangles on the sheet and would only be listed twice."""
    out: dict[str, dict] = {}
    for slot, spec in mc_humanoid.ARMOR_SLOTS.items():
        where = _SHEET_OF[spec["texture"]]
        for box in mc_humanoid.armor_boxes(slot):
            if box["mirror"]:
                continue
            name = _REGION_OF[box["name"]]
            rects = face_rects(box["size"], box["tex"])
            out[name] = {
                "region": name,
                "sheet": where,
                "slot": slot,
                "cube": box["name"],
                "size": tuple(box["size"]),
                "uv": tuple(box["tex"]),
                "inflate": box["inflate"],
                "both_sides": name in _BOTH_SIDES,
                "faces": {ANATOMY[d]: rects[d] for d in rects},
            }
    if sheet is not None:
        return {k: v for k, v in out.items() if v["sheet"] == sheet}
    return out


def rect_of(region: str, face: str) -> tuple[int, int, int, int]:
    """One face rectangle, (x, y, w, h), by region and anatomical face name."""
    all_regions = regions()
    if region not in all_regions:
        raise KeyError(f"no region {region!r}; known: {', '.join(sorted(all_regions))}")
    if face in _COMPASS:
        return all_regions[region]["faces"][face]
    if face in ANATOMY:
        return all_regions[region]["faces"][ANATOMY[face]]
    raise KeyError(f"no face {face!r}; one of {', '.join(FACES)}")


def owners(sheet: str) -> dict[tuple[int, int], str]:
    """Which `region.face` each texel of a sheet belongs to. Texels in no net belong to nothing, and
    paint there is paint the game never samples."""
    out: dict[tuple[int, int], str] = {}
    for region in regions(sheet).values():
        for face, (x, y, w, h) in region["faces"].items():
            for dy in range(h):
                for dx in range(w):
                    out[(x + dx, y + dy)] = f"{region['region']}.{face}"
    return out


# ---- the ASCII form ----------------------------------------------------------------------------


def level_of(value: int) -> int:
    """A 0..255 grey as one of the sixteen levels."""
    return max(0, min(15, int(round(value / 17.0))))


def value_of(level: int) -> int:
    return max(0, min(255, level * 17))


def to_ascii(image: Image.Image) -> list[str]:
    """A sheet as rows of characters. A coloured pixel is shown by its luma, which is how the game
    would read it anyway, so a vanilla sheet can be printed as a drawing to work from."""
    rgba = image.convert("RGBA")
    w, h = rgba.size
    px = rgba.load()
    rows = []
    for y in range(h):
        row = []
        for x in range(w):
            r, g, b, a = px[x, y]
            if not a:
                row.append(CLEAR)
                continue
            value = r if r == g == b else round(0.299 * r + 0.587 * g + 0.114 * b)
            row.append(LEVELS[level_of(value)])
        rows.append("".join(row))
    return rows


def apply_ascii(image: Image.Image, rows: list[str], at: tuple[int, int] = (0, 0)) -> int:
    """Stamp rows onto a sheet at `at`, in place. Returns how many texels changed.

    `.` clears, a level character paints that grey opaque, a space leaves the texel alone. Anything
    off the sheet is an error rather than a silent crop: a stamp that lands half outside is a
    mistake about where a region is, and swallowing it would hide it."""
    px = image.load()
    w, h = image.size
    ox, oy = at
    changed = 0
    for dy, row in enumerate(rows):
        y = oy + dy
        for dx, char in enumerate(row):
            x = ox + dx
            if char == KEEP:
                continue
            if not (0 <= x < w and 0 <= y < h):
                raise ValueError(f"row {dy} column {dx} lands at {x},{y}, off a {w}x{h} sheet")
            if char == CLEAR:
                pixel = (0, 0, 0, 0)
            else:
                level = LEVELS.find(char)
                if level < 0:
                    raise ValueError(
                        f"unknown character {char!r} at row {dy} column {dx}: "
                        f"'.' clears, ' ' keeps, '0'-'9' and 'a'-'f' are the greys")
                value = value_of(level)
                pixel = (value, value, value, 255)
            if px[x, y] != pixel:
                px[x, y] = pixel
                changed += 1
    return changed


def blank() -> Image.Image:
    return Image.new("RGBA", (SHEET_W, SHEET_H), (0, 0, 0, 0))


def pair_paths(skin: str, root: Path | None = None) -> dict[str, Path]:
    """Where a skin's two masters live: tools/skin_masters/<skin>/<sheet>.png."""
    base = (root or MASTERS) / skin
    return {sheet: base / f"{sheet}.png" for sheet in SHEETS}


def load_pair(skin: str, root: Path | None = None) -> dict[str, Image.Image]:
    out = {}
    for sheet, path in pair_paths(skin, root).items():
        if not path.is_file():
            raise SystemExit(f"no {sheet} sheet for skin {skin!r} at {path}")
        with Image.open(path) as image:
            out[sheet] = image.convert("RGBA")
    return out


# ---- printing ----------------------------------------------------------------------------------


def legend(sheet: str) -> list[str]:
    """The nets of one sheet as lines, each face with its rectangle."""
    lines = []
    for region in regions(sheet).values():
        size = "x".join(str(int(v)) for v in region["size"])
        both = ", both sides" if region["both_sides"] else ""
        lines.append(f"  {region['region']:<14} {region['slot']:<10} {size} at "
                     f"{region['uv'][0]},{region['uv'][1]}  inflate {region['inflate']}{both}")
        cells = [f"{face} {r[0]},{r[1]} {r[2]}x{r[3]}"
                 for face, r in region["faces"].items() if r[2] and r[3]]
        lines.append("      " + "   ".join(cells))
    return lines


def show(image: Image.Image, sheet: str, title: str = "") -> str:
    """One sheet as a drawing: a column ruler, the rows numbered, then the legend."""
    rows = to_ascii(image)
    tens = "    " + "".join(str((x // 10) % 10) if x % 10 == 0 else " " for x in range(image.size[0]))
    ones = "    " + "".join(str(x % 10) for x in range(image.size[0]))
    out = [f"{title or sheet} ({image.size[0]}x{image.size[1]})", tens, ones]
    for y, row in enumerate(rows):
        out.append(f"{y:>3} {row}")
    out.append(f"nets on {sheet}:")
    out += legend(sheet)
    return "\n".join(out)


def outline_source(material: str, sheet: str) -> Path | None:
    """Where an outline's sheet is: a vanilla material's extracted sheet, or one of the mod's own
    skins by name - `plate` is the studio figure's, and is always here."""
    folder = {"humanoid": "armor", "humanoid_leggings": "armor_leggings"}[sheet]
    vanilla = ASSETS / folder / f"{material}.png"
    if vanilla.is_file():
        return vanilla
    shipped = SHIPPED_SKINS / material / f"{sheet}.png"
    if shipped.is_file():
        return shipped
    authored = MASTERS / material / f"{sheet}.png"
    return authored if authored.is_file() else None


def outlines() -> list[dict]:
    """What a new skin can start from, for a dialog: the mod's plate outline first, since it is
    always here, then every vanilla material whose sheets have been extracted."""
    out = [{"value": STUDIO_OUTLINE, "label": "The mod's plate outline", "source": "armorpieces"}]
    from vanilla_assets import ARMOR_MATERIALS
    for material in ARMOR_MATERIALS:
        if material == "leather_overlay":
            continue
        if (ASSETS / "armor" / f"{material}.png").is_file():
            out.append({"value": material, "label": f"Vanilla's {material} outline", "source": "vanilla"})
    return out


def seed(name: str, material: str = "iron", level: int = 8) -> list[Path]:
    """Start a skin as an existing silhouette at one flat grey: vanilla's own for a material whose
    sheets are extracted, or the mod's `plate` where they are not.

    A skin seeded this way can only get its silhouette wrong by erasing, which the check sees -
    so the drawing is purely shading, which is the part worth a session's attention. It also
    writes the `silhouette` marker beside the sheets, which is what turns the check strict."""
    value = max(0, min(15, level)) * 17
    target = MASTERS / name
    target.mkdir(parents=True, exist_ok=True)
    written = []
    for sheet in SHEETS:
        source = outline_source(material, sheet)
        if source is None:
            raise SystemExit(f"no outline named {material!r}: no vanilla sheet for it under "
                             f"{ASSETS} and no skin of that name. Run python tools/vanilla_assets.py "
                             f"(or Use my game... in the editor), or start from {STUDIO_OUTLINE!r}.")
        with Image.open(source) as image:
            vanilla = image.convert("RGBA")
        out = Image.new("RGBA", vanilla.size, (0, 0, 0, 0))
        src, dst = vanilla.load(), out.load()
        for y in range(vanilla.size[1]):
            for x in range(vanilla.size[0]):
                if src[x, y][3]:
                    dst[x, y] = (value, value, value, 255)
        path = target / f"{sheet}.png"
        out.save(path)
        written.append(path)
    (target / "silhouette").write_text(f"{material} {max(0, min(15, level)):x}\n", encoding="utf8")
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--regions", action="store_true", help="print the net legend for both sheets")
    parser.add_argument("--json", action="store_true", help="with --regions: the table as JSON")
    parser.add_argument("--show", metavar="PNG", help="print a 64x32 sheet as ASCII")
    parser.add_argument("--sheet", default=None, help="which sheet --show is (default: from the file name)")
    parser.add_argument("--vanilla", metavar="MATERIAL", help="print vanilla's own pair for a material")
    parser.add_argument("--seed", metavar="SKIN",
                        help="start a skin as a vanilla silhouette at one flat grey")
    parser.add_argument("--from", dest="material", default="iron",
                        help="with --seed: the material whose silhouette to take (default iron), "
                             "or the mod's own 'plate' when the game is not here")
    parser.add_argument("--outlines", action="store_true",
                        help="print what --seed can start from here, as JSON")
    parser.add_argument("--level", type=int, default=8, help="with --seed: the flat grey, 0-15")
    parser.add_argument("--skin", metavar="NAME", help="print an authored skin's pair")
    parser.add_argument("--new", metavar="NAME", help="create a blank master pair for a new skin")
    args = parser.parse_args()

    if args.regions:
        if args.json:
            print(json.dumps(regions()))
            return
        for sheet in SHEETS:
            print(f"nets on {sheet}:")
            print("\n".join(legend(sheet)))
        return

    if args.show:
        path = Path(args.show)
        sheet = args.sheet or ("humanoid_leggings" if "leggings" in path.stem else "humanoid")
        with Image.open(path) as image:
            print(show(image.convert("RGBA"), sheet, str(path)))
        return

    if args.outlines:
        print(json.dumps(outlines()))
        return
    if args.seed:
        for path in seed(args.seed, args.material, args.level):
            print(path)
        print(f"silhouette pinned to {args.material}: check_skin refuses a texel out of place")
        return
    if args.vanilla:
        for sheet, folder in (("humanoid", "armor"), ("humanoid_leggings", "armor_leggings")):
            path = ASSETS / folder / f"{args.vanilla}.png"
            if not path.is_file():
                print(f"{sheet}: no vanilla {args.vanilla} sheet at {path} "
                      f"(run python tools/vanilla_assets.py)")
                continue
            with Image.open(path) as image:
                print(show(image.convert("RGBA"), sheet, f"vanilla {args.vanilla} {sheet}"))
                print()
        return

    if args.skin:
        for sheet, image in load_pair(args.skin).items():
            print(show(image, sheet, f"{args.skin} {sheet}"))
            print()
        return

    if args.new:
        paths = pair_paths(args.new)
        for sheet, path in paths.items():
            if path.is_file():
                print(f"{sheet}: already at {path}")
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            blank().save(path)
            print(f"{sheet}: blank sheet at {path}")
        return

    parser.print_help()
    sys.exit(2)


if __name__ == "__main__":
    main()
