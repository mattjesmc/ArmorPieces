"""
Recolour a part's master through a trim material's palette, for previewing outside the game.

This is a PORT, and the Java is the original. `DecorationPalette` and `DecorationTextureManager`
are what the game actually runs; this file exists so Blockbench can show the same thing without a
running client. If the two ever disagree, the Java is right and this is the bug.

The port is kept deliberately literal for that reason - same three stops, same MID_STOP of 5/7, same
sRGB lerp, same "luminance is the master's red channel", same rule that alpha comes from the master
and a static pixel outside the silhouette is not drawn. See DecorationPalette's class javadoc for
why the ramp has three stops rather than vanilla's eight; that reasoning is not repeated here.

Palettes come from tools/.mcassets, so run tools/vanilla_assets.py first.

Usage:
    python tools/preview_material.py spaulders gold
    python tools/preview_material.py spaulders --all --out-dir build/preview
    python tools/preview_material.py --ramp gold --static-colours '#ff0000,#00ff00'
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
MASTERS = ROOT / "tools" / "decoration_masters"
PALETTES = ROOT / "tools" / ".mcassets" / "palette"

STATIC_SUFFIX = "_static"

# DecorationPalette.MID_STOP - where the ramp's middle stop sits between darkest and lightest.
MID_STOP = 5.0 / 7.0

# The materials a pack can ask for, which is every palette vanilla ships except the ordering key.
MATERIALS = [
    "amethyst", "copper", "diamond", "emerald", "gold", "iron", "lapis", "netherite", "quartz",
    "redstone", "resin",
    "copper_darker", "diamond_darker", "gold_darker", "iron_darker", "netherite_darker",
]


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


def ramp_tables(material: str, static_colours) -> dict:
    """The lookup tables a live editor needs to composite a preview itself.

    The Blockbench plugin recolours on every brush movement, and a Python process per movement is
    too slow for that. But the maths must not move into JavaScript, or there would be two ports of
    DecorationPalette to keep in step. So the split is: this prints the finished 256-entry ramps,
    the material's own and one per static colour the layer currently uses, and the editor does
    nothing but index them by the master's red channel - the same table lookup the game does."""
    key_path = PALETTES / "trim_palette.png"
    palette_path = PALETTES / f"{material}.png"
    if not key_path.is_file() or not palette_path.is_file():
        sys.exit(f"error: no palette for {material!r} in {PALETTES}. "
                 f"Run: python tools/vanilla_assets.py")
    material_ramp = palette_ramp(key_path, palette_path)
    statics = {}
    for colour in static_colours:
        hex_colour = colour.strip().lstrip("#")
        if len(hex_colour) != 6:
            sys.exit(f"error: static colour {colour!r} is not #rrggbb")
        rgb = tuple(int(hex_colour[i:i + 2], 16) for i in (0, 2, 4))
        statics["#" + hex_colour.lower()] = static_ramp(rgb)
    return {"material": material_ramp, "static": statics}


def preview(part: str, material: str, out_path: Path,
            master_override: Path | None = None,
            static_override: Path | None = None) -> Path:
    """Composite one material's look.

    The two overrides exist so a live editor can preview UNSAVED paint: it dumps whatever is on
    screen to a scratch file and points this at that, instead of the alternative - flushing the
    editor's buffer to the real master first, which would make merely looking at a material a write
    to a tracked source file."""
    master_path = master_override or MASTERS / f"{part}.png"
    if not master_path.is_file():
        sys.exit(f"error: no master at {master_path}")
    key_path = PALETTES / "trim_palette.png"
    palette_path = PALETTES / f"{material}.png"
    if not key_path.is_file() or not palette_path.is_file():
        sys.exit(f"error: no palette for {material!r} in {PALETTES}. "
                 f"Run: python tools/vanilla_assets.py")

    statics_path = static_override or MASTERS / f"{part}{STATIC_SUFFIX}.png"
    statics = Image.open(statics_path) if statics_path.is_file() else None

    image = recolour(Image.open(master_path), statics, palette_ramp(key_path, palette_path))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path)
    return out_path


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

    if not args.part:
        ap.error("name a part, or pass --ramp")
    if not args.all and not args.material:
        ap.error("name a material, or pass --all")

    materials = MATERIALS if args.all else [args.material]
    for material in materials:
        out = preview(args.part, material, args.out_dir / f"{args.part}_{material}.png",
                      args.master, args.static)
        print(f"{args.part} x {material} -> {out}")


if __name__ == "__main__":
    main()
