"""
Recolour a part's master through a trim material's palette, for previewing outside the game.

This is a PORT, and the Java is the original. `DecorationPalette` and `DecorationTextureManager`
are what the game actually runs; this file exists so Blockbench can show the same thing without a
running client. If the two ever disagree, the Java is right and this is the bug.

The port is kept deliberately literal for that reason - same three stops, same MID_STOP of 5/7, same
sRGB lerp, same "luminance is the master's red channel", same rule that alpha comes from the master
and a static pixel outside the silhouette is not drawn. See DecorationPalette's class javadoc for
why the ramp has three stops rather than vanilla's eight; that reasoning is not repeated here.

Fittings ride the same port. A masked fitting is one more greyscale sheet beside the master,
`<part>_<fitting>.png`, and while it is filled its opaque pixels take the mask's OWN value through
the fitting's colour: a second trim material's palette (`gemstone=emerald`), or a dye's colour
through the static ramp (`inlay=red`). Alpha is still the master's. The masks are laid over the
recoloured master in the order given, later over earlier, which is the order the part's `fittings`
list them - see DecorationTextureManager.applyMask. A fitting that draws its own geometry, like the
banner, has no mask and is not previewed here.

Palettes come from tools/.mcassets, so run tools/vanilla_assets.py first.

Usage:
    python tools/preview_material.py spaulders gold
    python tools/preview_material.py circlet gold --fitting gemstone=emerald
    python tools/preview_material.py sash iron --fitting inlay=red --fitting guard=gold
    python tools/preview_material.py spaulders --all --out-dir build/preview
    python tools/preview_material.py --ramp gold --static-colours '#ff0000,#00ff00'
    python tools/preview_material.py --fittings src/main/resources/data/armorpieces/armorpieces/armor_decoration/sash.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
MASTERS = ROOT / "tools" / "decoration_masters"
ASSETS = ROOT / "tools" / ".mcassets"
PALETTES = ASSETS / "palette"
RESOURCES = ROOT / "src" / "main" / "resources"

STATIC_SUFFIX = "_static"

# DecorationPalette.MID_STOP - where the ramp's middle stop sits between darkest and lightest.
MID_STOP = 5.0 / 7.0

# The materials a pack can ask for, which is every palette vanilla ships except the ordering key.
MATERIALS = [
    "amethyst", "copper", "diamond", "emerald", "gold", "iron", "lapis", "netherite", "quartz",
    "redstone", "resin",
    "copper_darker", "diamond_darker", "gold_darker", "iron_darker", "netherite_darker",
]

# DyeColor's texture diffuse colours, which is what DyeFitting.colour() hands the baker - the
# colour a dyed block's texture is tinted with, not the legibility-tuned text colour. Read out of
# the 26.2 jar with javap; they have not moved since 1.17, but check them if a dye ever looks off.
DYES = {
    "white": (0xF9, 0xFF, 0xFE),
    "orange": (0xF9, 0x80, 0x1D),
    "magenta": (0xC7, 0x4E, 0xBD),
    "light_blue": (0x3A, 0xB3, 0xDA),
    "yellow": (0xFE, 0xD8, 0x3D),
    "lime": (0x80, 0xC7, 0x1F),
    "pink": (0xF3, 0x8B, 0xAA),
    "gray": (0x47, 0x4F, 0x52),
    "light_gray": (0x9D, 0x9D, 0x97),
    "cyan": (0x16, 0x9C, 0x9C),
    "purple": (0x89, 0x32, 0xB8),
    "blue": (0x3C, 0x44, 0xAA),
    "brown": (0x83, 0x54, 0x32),
    "green": (0x5E, 0x7C, 0x16),
    "red": (0xB0, 0x2E, 0x26),
    "black": (0x1D, 0x1D, 0x21),
}

# The fitting types this mod ships that colour a mask, and the type that draws geometry instead.
# A type from another mod is listed by --fittings as unknown, with no options, which is the most
# this tool can say about a value whose shape it does not know.
MATERIAL_TYPE = "armorpieces:material"
DYE_TYPE = "armorpieces:dye"
BANNER_TYPE = "armorpieces:banner"


def _lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _ramp(dark, mid, light):
    """The three-stop ramp as a 256-entry table, mid stop at luminance 127."""
    table = []
    for v in range(256):
        if v <= 127:
            table.append(_lerp(dark, mid, v / 127.0))
        else:
            table.append(_lerp(mid, light, (v - 127) / 128.0))
    return table


def _stop_at(colours, position):
    """The colour at a fractional position along the palette, interpolating between its stops."""
    low = int(position)
    high = min(low + 1, len(colours) - 1)
    return _lerp(colours[low], colours[high], position - low)


def _pixels(image):
    """Row-major, so a palette laid out 8x1 and one laid out 4x2 read the same."""
    return list(image.convert("RGBA").getdata())


def palette_ramp(key_path: Path, palette_path: Path):
    """DecorationPalette.of - the material's ramp, ordered by the key's greys.

    Returns None when the pair does not describe at least two usable stops, which is the same
    signal the game uses to leave a part untinted rather than guess."""
    key = _pixels(Image.open(key_path))
    palette = _pixels(Image.open(palette_path))
    stops = min(len(key), len(palette))
    if stops < 2:
        return None

    pairs = sorted(((key[i][0], palette[i][:3]) for i in range(stops)), key=lambda p: p[0])
    greys = [p[0] for p in pairs]
    colours = [p[1] for p in pairs]
    if greys[0] == greys[-1]:
        return None

    return _ramp(colours[0], _stop_at(colours, (stops - 1) * MID_STOP), colours[-1])


def static_ramp(rgb):
    """DecorationPalette.ofStaticColour - dark is half the colour, light is halfway to white."""
    r, g, b = rgb
    return _ramp(
        (round(r * 0.5), round(g * 0.5), round(b * 0.5)),
        (r, g, b),
        (round(r + (255 - r) * 0.5), round(g + (255 - g) * 0.5), round(b + (255 - b) * 0.5)))


def material_ramp(material: str):
    """The ramp for a trim material by its palette suffix, or an exit if the palette is not here."""
    key_path = PALETTES / "trim_palette.png"
    palette_path = PALETTES / f"{material}.png"
    if not key_path.is_file() or not palette_path.is_file():
        sys.exit(f"error: no palette for {material!r} in {PALETTES}. "
                 f"Run: python tools/vanilla_assets.py")
    return palette_ramp(key_path, palette_path)


def parse_hex(colour: str):
    hex_colour = colour.strip().lstrip("#")
    if len(hex_colour) != 6:
        sys.exit(f"error: colour {colour!r} is not #rrggbb")
    return tuple(int(hex_colour[i:i + 2], 16) for i in (0, 2, 4))


def fitting_ramp(value: str):
    """The ramp a fitting value colours its mask through.

    `#rrggbb` and a dye name go through the static ramp, which is what DyeFitting asks for; anything
    else is a trim material's palette suffix, which is what MaterialFitting asks for. A material
    with no palette gives None, and the mask then shows at its own greys, as it does in the game."""
    value = value.strip().lower()
    if value.startswith("#"):
        return static_ramp(parse_hex(value))
    if value in DYES:
        return static_ramp(DYES[value])
    return material_ramp(value)


def recolour(master: Image.Image, statics: Image.Image | None, ramp) -> Image.Image:
    """DecorationTextureManager.recolour, pixel for pixel."""
    master = master.convert("RGBA")
    width, height = master.size
    source = master.load()
    static_pixels = statics.convert("RGBA").load() if statics is not None else None
    static_size = statics.size if statics is not None else (0, 0)

    out = Image.new("RGBA", (width, height))
    target = out.load()
    static_ramps: dict[tuple, list] = {}

    for y in range(height):
        for x in range(width):
            r, g, b, alpha = source[x, y]
            if alpha == 0:
                target[x, y] = (0, 0, 0, 0)
                continue
            luminance = r  # the master's red channel, exactly as the game reads it

            colour = None
            if static_pixels is not None and x < static_size[0] and y < static_size[1]:
                sr, sg, sb, sa = static_pixels[x, y]
                if sa != 0:
                    key = (sr, sg, sb)
                    colour = static_ramps.setdefault(key, static_ramp(key))[luminance]

            if colour is None:
                colour = ramp[luminance] if ramp is not None else (r, g, b)

            target[x, y] = (colour[0], colour[1], colour[2], alpha)
    return out


def apply_mask(out: Image.Image, master: Image.Image, mask: Image.Image, ramp) -> None:
    """DecorationTextureManager.applyMask, in place: the mask's own red channel is the shading, the
    master's alpha is still the silhouette, and a None ramp leaves the mask at its own greys."""
    master_pixels = master.convert("RGBA").load()
    mask_pixels = mask.convert("RGBA").load()
    target = out.load()
    width = min(out.width, mask.width)
    height = min(out.height, mask.height)
    for y in range(height):
        for x in range(width):
            mr, mg, mb, ma = mask_pixels[x, y]
            if ma == 0:
                continue
            alpha = master_pixels[x, y][3]
            if alpha == 0:
                continue
            colour = ramp[mr] if ramp is not None else (mr, mg, mb)
            target[x, y] = (colour[0], colour[1], colour[2], alpha)


def ramp_tables(material: str, static_colours) -> dict:
    """The lookup tables a live editor needs to composite a preview itself.

    The Blockbench plugin recolours on every brush movement, and a Python process per movement is
    too slow for that. But the maths must not move into JavaScript, or there would be two ports of
    DecorationPalette to keep in step. So the split is: this prints the finished 256-entry ramps,
    the material's own and one per static colour the layer currently uses, and the editor does
    nothing but index them by the master's red channel - the same table lookup the game does. A
    fitting is the same two tables again: a material fitting indexes a material's ramp, a dye
    fitting a static colour's, both by the mask's red channel."""
    statics = {}
    for colour in static_colours:
        rgb = parse_hex(colour)
        statics["#%02x%02x%02x" % rgb] = static_ramp(rgb)
    return {"material": material_ramp(material), "static": statics}


def preview(part: str, material: str, out_path: Path,
            master_override: Path | None = None,
            static_override: Path | None = None,
            fittings: list[tuple[str, str]] = (),
            mask_overrides: dict[str, Path] | None = None) -> Path:
    """Composite one material's look, with any filled fittings laid over it.

    The overrides exist so a live editor can preview UNSAVED paint: it dumps whatever is on screen
    to a scratch file and points this at that, instead of the alternative - flushing the editor's
    buffer to the real master first, which would make merely looking at a material a write to a
    tracked source file. `fittings` is (name, value) pairs in layer order; a fitting whose mask is
    not on disk changes nothing, exactly as in the game."""
    master_path = master_override or MASTERS / f"{part}.png"
    if not master_path.is_file():
        sys.exit(f"error: no master at {master_path}")
    ramp = material_ramp(material)

    statics_path = static_override or MASTERS / f"{part}{STATIC_SUFFIX}.png"
    statics = Image.open(statics_path) if statics_path.is_file() else None

    master = Image.open(master_path)
    image = recolour(master, statics, ramp)
    for name, value in fittings:
        mask_path = (mask_overrides or {}).get(name) or MASTERS / f"{part}_{name}.png"
        if not mask_path.is_file():
            print(f"note: no mask at {mask_path}, {name} changes nothing", file=sys.stderr)
            continue
        apply_mask(image, master, Image.open(mask_path), fitting_ramp(value))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path)
    return out_path


# ---- what a part's fittings are, for a live editor ------------------------------------------

def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf8"))


def _split_id(value: str, default_namespace: str = "minecraft") -> tuple[str, str]:
    namespace, _, name = value.rpartition(":")
    return (namespace or default_namespace), name


def _lang(pack_dirs: list[Path], namespace: str) -> dict:
    """The English strings for a namespace: the pack's own, else the mod's, else vanilla's."""
    for pack in pack_dirs:
        lang = pack / "assets" / namespace / "lang" / "en_us.json"
        if lang.is_file():
            return _read_json(lang)
    vanilla = ASSETS / "lang" / "en_us.json"
    return _read_json(vanilla) if namespace == "minecraft" and vanilla.is_file() else {}


def _translate(pack_dirs: list[Path], namespace: str, key: str, fallback: str) -> str:
    return _lang(pack_dirs, namespace).get(key) or fallback.replace("_", " ").title()


def _find(pack_dirs: list[Path], *relative: str) -> Path | None:
    for pack in pack_dirs:
        candidate = pack.joinpath(*relative)
        if candidate.is_file():
            return candidate
    return None


def _tag_members(pack_dirs: list[Path], registry: str, tag: str, seen: set | None = None) -> list[str]:
    """The ids a tag lists, nested tags flattened, in file order."""
    seen = seen if seen is not None else set()
    if tag in seen:
        return []
    seen.add(tag)
    namespace, name = _split_id(tag)
    # Vanilla's own tags come last, from the copy vanilla_assets.py takes out of the jar.
    path = _find(pack_dirs + [ASSETS], "data", namespace, "tags", registry, f"{name}.json")
    if path is None:
        return []
    members: list[str] = []
    for entry in _read_json(path).get("values", []):
        value = entry.get("id") if isinstance(entry, dict) else entry
        if not isinstance(value, str):
            continue
        if value.startswith("#"):
            members.extend(_tag_members(pack_dirs, registry, value[1:], seen))
        elif value not in members:
            members.append(value)
    return members


def _material_options(pack_dirs: list[Path], materials) -> list[dict]:
    """One option per trim material the fitting accepts, named as the game names it. Only materials
    with a palette here are offered: the game would show the others at the mask's own greys, which
    is not a preview anyone asks for."""
    if isinstance(materials, str):
        ids = _tag_members(pack_dirs, "trim_material", materials[1:]) if materials.startswith("#") else [materials]
    else:
        ids = [m for m in materials if isinstance(m, str)]
    options = []
    for material in ids:
        namespace, name = _split_id(material)
        if not (PALETTES / f"{name}.png").is_file():
            continue
        label = _translate(pack_dirs, namespace, f"trim_material.{namespace}.{name}", name)
        options.append({"value": name, "id": material, "label": label.removesuffix(" Material"),
                        "colour": f"palette:{name}"})
    return options


def _dye_options(pack_dirs: list[Path]) -> list[dict]:
    return [{
        "value": name,
        "label": _translate(pack_dirs, "minecraft", f"color.minecraft.{name}", name),
        "colour": "solid:#%02x%02x%02x" % rgb,
    } for name, rgb in DYES.items()]


def _pack_dirs(pack: Path) -> list[Path]:
    """Where a pack's references resolve: the pack itself first, then the mod's own resources."""
    pack = pack.resolve()
    return [pack] + ([RESOURCES] if RESOURCES.resolve() != pack else [])


def _fitting_entry(pack_dirs: list[Path], fitting_id: str) -> dict:
    """One fitting, resolved far enough for an editor to offer it: its mask name (the id's path),
    its type, whether it is a mask over the texture, a display name, the file it was read from,
    and - for the two masked types this mod ships - the values it can take, each with the colour
    it asks the baker for: `palette:<suffix>` or `solid:#rrggbb`. A fitting with no file is listed
    with a null type, which is what an editor should show as missing."""
    namespace, name = _split_id(fitting_id, "armorpieces")
    entry = {"id": f"{namespace}:{name}", "name": name, "type": None, "masked": False,
             "label": name.replace("_", " ").title(), "options": [], "path": None}
    path = _find(pack_dirs, "data", namespace, "armorpieces", "fitting", f"{name}.json")
    if path is not None:
        fitting = _read_json(path)
        entry["path"] = str(path)
        entry["type"] = fitting.get("type")
        description = fitting.get("description")
        if isinstance(description, dict) and isinstance(description.get("translate"), str):
            entry["label"] = _translate(pack_dirs, namespace, description["translate"], name)
        elif isinstance(description, str):
            entry["label"] = description
        if entry["type"] == MATERIAL_TYPE:
            entry["masked"] = True
            entry["options"] = _material_options(pack_dirs, fitting.get("materials", []))
        elif entry["type"] == DYE_TYPE:
            entry["masked"] = True
            entry["options"] = _dye_options(pack_dirs)
        elif entry["type"] == BANNER_TYPE:
            # Not a mask: the game draws the banner's layers over the named bone instead of its
            # texture. An editor can stand in for that with the base colour, so the options are
            # the sixteen banner bases, and the bone is named for it to find.
            entry["bone"] = fitting.get("bone", "banner")
            entry["options"] = _dye_options(pack_dirs)
    return entry


def list_fittings(data_path: Path, pack: Path | None = None) -> list[dict]:
    """The fittings a part declares, resolved far enough for an editor to offer them.

    `data_path` is the part's datapack half, `<pack>/data/<ns>/armorpieces/armor_decoration/<part>.json`.
    Fittings, tags and language files are looked up in that pack first and the mod's own resources
    second, which is how the game would resolve them with both loaded. `pack` names the pack when
    the file is not inside one - a live editor's scratch copy of unsaved data, say."""
    data_path = data_path.resolve()
    if pack is None:
        pack = data_path.parents[4] if len(data_path.parents) > 4 else data_path.parent
    pack_dirs = _pack_dirs(pack)
    return [_fitting_entry(pack_dirs, fitting_id)
            for fitting_id in _read_json(data_path).get("fittings", [])
            if isinstance(fitting_id, str)]


def available_fittings(pack: Path) -> list[dict]:
    """Every fitting a part in `pack` could declare: the pack's own definitions and the mod's,
    resolved the same way as list_fittings, the pack's winning where both define one id."""
    pack_dirs = _pack_dirs(pack)
    seen: dict[str, dict] = {}
    for directory in pack_dirs:
        data = directory / "data"
        if not data.is_dir():
            continue
        for path in sorted(data.glob("*/armorpieces/fitting/*.json")):
            fitting_id = f"{path.parents[2].name}:{path.stem}"
            if fitting_id not in seen:
                seen[fitting_id] = _fitting_entry(pack_dirs, fitting_id)
    return list(seen.values())


def fitting_choices(pack: Path) -> dict:
    """What a new fitting definition can be made of: the trim materials with a palette here, named
    as the game names them, and every trim-material tag in the pack, the mod and vanilla with the
    materials it resolves to. The Blockbench plugin's New Fitting dialog is built from this."""
    pack_dirs = _pack_dirs(pack)
    materials, seen = [], set()
    # Every trim material registered: vanilla's from the jar copy, then any a pack defines. Only
    # ones with a palette here are offered, for the same reason _material_options skips them.
    for directory in [ASSETS] + pack_dirs:
        data = directory / "data"
        if not data.is_dir():
            continue
        for path in sorted(data.glob("*/trim_material/*.json")):
            material = f"{path.parents[1].name}:{path.stem}"
            if material in seen or not (PALETTES / f"{path.stem}.png").is_file():
                continue
            seen.add(material)
            namespace, name = _split_id(material)
            label = _translate(pack_dirs, namespace, f"trim_material.{namespace}.{name}", name)
            materials.append({"value": material, "label": label.removesuffix(" Material")})
    tags, seen = [], set()
    for directory in pack_dirs + [ASSETS]:
        data = directory / "data"
        if not data.is_dir():
            continue
        for path in sorted(data.glob("*/tags/trim_material/*.json")):
            tag = f"{path.parents[2].name}:{path.stem}"
            if tag in seen:
                continue
            seen.add(tag)
            tags.append({"id": f"#{tag}", "members": _tag_members(pack_dirs, "trim_material", tag)})
    return {"materials": materials, "tags": tags}


def _parse_pairs(values, what: str) -> list[tuple[str, str]]:
    pairs = []
    for item in values or []:
        name, sep, value = item.partition("=")
        if not sep or not name.strip() or not value.strip():
            sys.exit(f"error: {what} {item!r} is not NAME=VALUE")
        pairs.append((name.strip(), value.strip()))
    return pairs


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("part", nargs="?", help="part name, e.g. spaulders")
    ap.add_argument("material", nargs="?", help="trim material, e.g. gold")
    ap.add_argument("--ramp", metavar="MATERIAL",
                    help="print the material's ramp (and any --static-colours ramps) as JSON "
                         "and exit, for a live editor to composite with")
    ap.add_argument("--static-colours", default="",
                    help="comma-separated #rrggbb colours to include ramps for with --ramp")
    ap.add_argument("--fittings", metavar="DATA_JSON", type=Path,
                    help="print the fittings the part at this datapack file declares, with the "
                         "values each can take, as JSON and exit")
    ap.add_argument("--pack", metavar="DIR", type=Path,
                    help="with --fittings: the pack the file belongs to, when it is not inside one")
    ap.add_argument("--list-fittings", metavar="PACK_DIR", type=Path,
                    help="print every fitting a part in this pack could declare - the pack's own "
                         "and the mod's - as JSON and exit")
    ap.add_argument("--fitting-choices", metavar="PACK_DIR", type=Path,
                    help="print the trim materials and trim-material tags a new fitting in this "
                         "pack could take, as JSON and exit")
    ap.add_argument("--fitting", action="append", metavar="NAME=VALUE",
                    help="fill a fitting for the preview, e.g. gemstone=emerald, inlay=red, "
                         "guard=#c0c0c0; repeatable, laid over in the order given")
    ap.add_argument("--mask", action="append", metavar="NAME=PATH",
                    help="use this file as the fitting's mask instead of the authored one")
    ap.add_argument("--all", action="store_true", help="every material")
    ap.add_argument("--out-dir", type=Path, default=ROOT / "build" / "preview")
    ap.add_argument("--master", type=Path,
                    help="use this file as the master instead of the authored one")
    ap.add_argument("--static", type=Path,
                    help="use this file as the static layer instead of the authored one")
    args = ap.parse_args()

    if args.ramp:
        colours = [c for c in args.static_colours.split(",") if c.strip()]
        print(json.dumps(ramp_tables(args.ramp, colours)))
        return

    if args.fittings:
        if not args.fittings.is_file():
            sys.exit(f"error: no part data at {args.fittings}")
        print(json.dumps(list_fittings(args.fittings, args.pack)))
        return

    if args.list_fittings:
        if not args.list_fittings.is_dir():
            sys.exit(f"error: no pack at {args.list_fittings}")
        print(json.dumps(available_fittings(args.list_fittings)))
        return

    if args.fitting_choices:
        if not args.fitting_choices.is_dir():
            sys.exit(f"error: no pack at {args.fitting_choices}")
        print(json.dumps(fitting_choices(args.fitting_choices)))
        return

    if not args.part:
        ap.error("name a part, or pass --ramp, --fittings, --list-fittings or --fitting-choices")
    if not args.all and not args.material:
        ap.error("name a material, or pass --all")

    fittings = _parse_pairs(args.fitting, "--fitting")
    masks = {name: Path(value) for name, value in _parse_pairs(args.mask, "--mask")}
    suffix = "".join(f"_{name}-{value.lstrip('#')}" for name, value in fittings)
    materials = MATERIALS if args.all else [args.material]
    for material in materials:
        out = preview(args.part, material, args.out_dir / f"{args.part}_{material}{suffix}.png",
                      args.master, args.static, fittings, masks)
        print(f"{args.part} x {material}"
              + "".join(f" + {name}={value}" for name, value in fittings) + f" -> {out}")


if __name__ == "__main__":
    main()
