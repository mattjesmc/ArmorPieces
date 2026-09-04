"""
Colour a skin's greyscale master with an armor material's own palette.

The skin is drawn once, in grey. What makes a skinned iron helmet still read as IRON beside an
unskinned one is that the colours are not authored at all - they are taken out of the material's own
vanilla texture:

    every opaque texel of <material>.png and its leggings twin, sorted by luminance, cut into eight
    octiles, the median RGB of each kept, dark first.

Eight shades, derived rather than written down, which buys two things. No palette file exists to
fall out of date with a Minecraft bump, and a MODDED armor material is skinned for free, because the
only thing wanted from it is a texture it already ships.

The master's value is then a position on that ramp: the 256-entry lookup table below runs the eight
shades through a piecewise-linear interpolation, so a master that uses its whole range gets every
shade the material has and the steps between them. This is the same trade DecorationTextureManager
already makes for parts - one greyscale master, baked per material at load - and when the mod grows
an ArmorSkinTextureManager it should be this arithmetic, in Java, over these same eight numbers.

Both layers are sampled TOGETHER: one ramp per material, not one per sheet, or the leggings would
drift away from the body they are worn under.

Three materials do not fit the rule and want a decision rather than a bake:

  * chainmail's texels span 146..189, so its eight shades are nearly one shade and the mail weave -
    the only thing chainmail has - is lost. --report says so per material;
  * turtle_scute is a helmet and nothing else, so its ramp comes from one sheet and runs vivid;
  * leather is tinted by dye at render time over a second overlay layer, so what is baked here is
    the undyed shell.

Usage:
    python tools/bake_skin.py --report                    # every material's ramp, and its spread
    python tools/bake_skin.py --ramps                     # the 256-entry tables, as JSON
    python tools/bake_skin.py plate --out build/skins     # bake a skin for every material
    python tools/bake_skin.py plate --material iron --out <dir>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image

import skin_sheets
from skin_sheets import ASSETS, SHEETS, load_pair
from vanilla_assets import ARMOR_MATERIALS

# The materials a skin is baked for: every armor material, minus the leather overlay, which is not a
# material but a second layer of one.
MATERIALS = [m for m in ARMOR_MATERIALS if m != "leather_overlay"]

SHADES = 8

# The eight shades, measured, span almost nothing: iron's run 183..229 in luma, chainmail's 148..189.
# That is vanilla being vanilla - armor textures are flat, which is the very thing a skin is drawn to
# fix - but baked straight it would flatten a master that was drawn across its whole range right back
# down to iron's forty-six levels, and the feature would have been for nothing.
#
# So a ramp that comes out narrower than MIN_SPAN is DEEPENED: the lightest shade stays exactly where
# the material put it, and the darker ones are pushed down, in place, until the eight of them span
# that much. Each shade keeps its hue and its saturation, since it is scaled toward black rather than
# desaturated, so the material still reads as itself - the highlight is literally its own - and the
# master's form has somewhere to live. Netherite, the one vanilla set with real form in it, spans 78
# unaided; 100 is a little more than that and no material is left flat.
#
# --faithful bakes the medians as they come, which is the rule as first written down in
# docs/plans/armor-skins.md, for comparing the two.
MIN_SPAN = 100
FLOOR = 12

# Where each sheet's vanilla texture lives in the asset cache.
_FOLDER = {"humanoid": "armor", "humanoid_leggings": "armor_leggings"}


def luma(rgb) -> float:
    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]


def material_texels(material: str) -> list[tuple[int, int, int]]:
    """Every opaque texel of a material's armor pair. Both sheets, one bag."""
    out = []
    for sheet in SHEETS:
        path = ASSETS / _FOLDER[sheet] / f"{material}.png"
        if not path.is_file():
            continue
        with Image.open(path) as image:
            for r, g, b, a in image.convert("RGBA").getdata():
                if a:
                    out.append((r, g, b))
    if not out:
        raise SystemExit(f"no vanilla texture for {material!r} under {ASSETS} - "
                         f"run python tools/vanilla_assets.py")
    return out


def deepen(shades: list[tuple[int, int, int]], span: int = MIN_SPAN) -> list[tuple[int, int, int]]:
    """Push the darker shades down until the eight of them span `span` luma. See MIN_SPAN."""
    lumas = [luma(s) for s in shades]
    hi, lo = lumas[-1], lumas[0]
    if hi - lo >= span or hi <= lo:
        return shades
    scale = min(span / (hi - lo), (hi - FLOOR) / (hi - lo))
    out = []
    for shade, value in zip(shades, lumas):
        if value <= 0:
            out.append(shade)
            continue
        target = hi - (hi - value) * scale
        factor = max(0.0, target) / value
        out.append(tuple(max(0, min(255, int(round(c * factor)))) for c in shade))
    return out


def ramp(material: str, faithful: bool = False) -> list[tuple[int, int, int]]:
    """The material's eight shades, dark first, and every one of them a colour it really uses.

    Not the median of each octile, which is what this was first written as: an armor texture spends
    most of its texels on one or two values, so four of the eight octiles came back the same colour
    and half the ramp was flat. The stops are spaced along the material's own luminance RANGE
    instead - the 5th to the 95th percentile, to keep one stray highlight from stretching it - and
    each stop takes the median colour of the texels nearest that luma, so the shade is one the
    material has and the eight of them are eight different things.

    Deepened to MIN_SPAN afterwards unless `faithful`."""
    texels = material_texels(material)
    values = sorted(luma(t) for t in texels)
    lo = values[int(0.05 * (len(values) - 1))]
    hi = values[int(0.95 * (len(values) - 1))]
    if hi <= lo:
        lo, hi = values[0], values[-1]

    by_value: dict[int, list[tuple[int, int, int]]] = {}
    for texel in texels:
        by_value.setdefault(round(luma(texel)), []).append(texel)

    shades = []
    for i in range(SHADES):
        target = lo + (hi - lo) * i / (SHADES - 1)
        nearest = min(by_value, key=lambda v: (abs(v - target), v))
        bucket = sorted(by_value[nearest])
        shades.append(bucket[len(bucket) // 2])
    return shades if faithful else deepen(shades)


def table(material: str, faithful: bool = False) -> list[tuple[int, int, int]]:
    """A 256-entry lookup from a master's value to the material's colour.

    The eight shades are placed at the centres of their eight bands and interpolated between, so
    the ends of the master's range reach the material's own darkest and lightest texel rather than
    stopping an eighth short of them."""
    shades = ramp(material, faithful)
    stops = [((i + 0.5) * 256.0 / SHADES, shades[i]) for i in range(SHADES)]
    out = []
    for value in range(256):
        if value <= stops[0][0]:
            out.append(stops[0][1])
            continue
        if value >= stops[-1][0]:
            out.append(stops[-1][1])
            continue
        for i in range(SHADES - 1):
            lo, hi = stops[i], stops[i + 1]
            if lo[0] <= value <= hi[0]:
                t = (value - lo[0]) / (hi[0] - lo[0])
                out.append(tuple(int(round(lo[1][c] + (hi[1][c] - lo[1][c]) * t)) for c in range(3)))
                break
    return out


# How much of vanilla's own lighting to mix back over a master. Vanilla's armor textures carry
# the panel edges, the rim highlight along the top of a plate and the shadow under an overhang -
# the things that make a flat pattern read as metal - and a master that replaces every value with
# its own pattern throws all of it away. The mix adds vanilla's deviation from its own median
# back on top: the skin keeps its design and inherits the light. 0 is the pattern alone.
LIGHT_MIX = 0.35


def lightmap(material: str, mix: float = LIGHT_MIX) -> dict[str, list[list[int]]]:
    """Vanilla's lighting for one material: a signed amount to add to each master texel.

    Normalised by the material's own 5th-to-95th percentile spread, so netherite's dark sheet and
    gold's bright one contribute the same amount of SHAPE rather than their own contrast."""
    out: dict[str, list[list[int]]] = {}
    for sheet, folder in (("humanoid", "armor"), ("humanoid_leggings", "armor_leggings")):
        path = ASSETS / folder / f"{material}.png"
        if not path.is_file():
            continue
        with Image.open(path) as opened:
            image = opened.convert("RGBA")
        px = image.load()
        values = sorted(luma(px[x, y][:3])
                        for y in range(image.height) for x in range(image.width) if px[x, y][3])
        if not values:
            continue
        lo = values[int(0.05 * (len(values) - 1))]
        hi = values[int(0.95 * (len(values) - 1))]
        # The MIDDLE of the material's own range, not its median: an armor texture spends most of
        # its texels on one or two values, so the median sits at one end and a median-centred map
        # would only ever brighten. Clamped so one stray highlight cannot blow a texel out.
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
        out[sheet] = rows
    return out


def bake(image: Image.Image, lut: list[tuple[int, int, int]],
         light: list[list[int]] | None = None) -> Image.Image:
    """One sheet through one table. Alpha is the master's; the value chooses the colour."""
    rgba = image.convert("RGBA")
    out = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
    src, dst = rgba.load(), out.load()
    for y in range(rgba.size[1]):
        for x in range(rgba.size[0]):
            r, g, b, a = src[x, y]
            if not a:
                continue
            value = r if r == g == b else round(luma((r, g, b)))
            if light is not None:
                value += light[y][x]
            dst[x, y] = (*lut[max(0, min(255, value))], a)
    return out


def bake_skin(skin: str, material: str, out_dir: Path, faithful: bool = False,
              mix: float = LIGHT_MIX) -> list[Path]:
    lut = table(material, faithful)
    light = lightmap(material, mix) if mix else {}
    written = []
    target = out_dir / skin / material
    target.mkdir(parents=True, exist_ok=True)
    for sheet, image in load_pair(skin).items():
        path = target / f"{sheet}.png"
        bake(image, lut, light.get(sheet)).save(path)
        written.append(path)
    return written


def report(faithful: bool = False) -> str:
    """Every material's ramp: what its texture spans, what the eight shades span before and after
    deepening, and the shades themselves."""
    lines = ["material       texels  vanilla    ramp span   eight shades (hex, dark first)"]
    for material in MATERIALS:
        texels = material_texels(material)
        values = sorted(round(luma(t)) for t in texels)
        plain = ramp(material, faithful=True)
        shades = ramp(material, faithful=faithful)
        was = round(luma(plain[-1]) - luma(plain[0]))
        now = round(luma(shades[-1]) - luma(shades[0]))
        hexes = " ".join("%02x%02x%02x" % s for s in shades)
        lines.append(f"{material:<14} {len(texels):>6}  {values[0]:>3}..{values[-1]:<3}  "
                     f"{was:>3} -> {now:<3}   {hexes}")
    return "\n".join(lines)


def _levels(faithful: bool = False) -> dict[str, list[int]]:
    """The luma each of the sixteen master levels bakes to, per material."""
    out = {}
    for material in MATERIALS:
        lut = table(material, faithful)
        out[material] = [round(luma(lut[17 * i])) for i in range(16)]
    return out


def contrast_rule(faithful: bool = False) -> str:
    """One measured sentence: how big a step between two levels has to be to survive the bake.

    The sixteen levels a master is drawn in land on eight stops, and a material whose texture
    repeats a colour repeats a stop - so levels two apart can bake identical. This is the number
    a drawing has to obey, and it is not guessable from the greyscale."""
    lums = _levels(faithful)
    worst = [min(min(v[i + k] - v[i] for i in range(16 - k)) for v in lums.values())
             for k in range(1, 6)]
    safe = next((k for k in range(1, 6) if worst[k - 1] >= 10), 5)
    vanish = max((k for k in range(1, 6) if worst[k - 1] == 0), default=0)
    return ("contrast: a level is a position on an eight-stop ramp and most materials repeat "
            f"stops, so a step of {vanish} level(s) or less can bake IDENTICAL; "
            + ", ".join(f"{k}->{worst[k - 1]} luma" for k in range(1, 6))
            + f". Shade in bands {safe}-{safe + 1} levels apart - smaller steps read in "
            "greyscale and vanish on iron. That is the worst case over every material and every "
            "pair; particular pairs are much better, and --levels prints them.")


def pair(lo: str, hi: str, faithful: bool = False) -> str:
    """What one pair of levels buys on each material, weakest first.

    The ranked list in --levels answers "what is the best pair"; every real decision while
    drawing is "is the pair I want good enough", which is this."""
    lums = _levels(faithful)
    a, b = int(lo, 16), int(hi, 16)
    rows = sorted((lums[m][b] - lums[m][a], m) for m in lums)
    out = [f"{lo}-{hi}: what the step buys, weakest material first"]
    for gain, m in rows:
        out.append(f"  {m:<14}{gain:>4} luma   ({lums[m][a]} -> {lums[m][b]})")
    worst = rows[0][0]
    verdict = ("invisible on " + rows[0][1] if worst < 4 else
               "weak on " + rows[0][1] if worst < 10 else "reads on every material")
    return "\n".join(out + ["", f"worst case {worst} luma - {verdict}"])


def levels(faithful: bool = False) -> str:
    """What every one of the sixteen levels bakes to on every material, and the best pairs.

    The worst case alone is misleading: the flat spots are level-specific and the table
    interpolates between the eight stops, so `7`-`a` buys 29 luma on chainmail where `b`-`e`
    buys 4. A drawing picks its bands off this table."""
    lums = _levels(faithful)
    names = list(lums)
    head = "level  " + "".join(f"{m[:9]:>10}" for m in names)
    lines = [head]
    for i in range(16):
        lines.append(f"  {i:x}    " + "".join(f"{lums[m][i]:>10}" for m in names))
    lines += ["", "best bands to shade in (the pair's smallest gain over all eight materials)"]
    for k in (2, 3, 4, 5):
        ranked = sorted(((min(lums[m][i + k] - lums[m][i] for m in names), i)
                         for i in range(16 - k)), reverse=True)[:3]
        pairs = ", ".join(f"{i:x}-{i + k:x} ({gain} luma)" for gain, i in ranked)
        lines.append(f"{k} levels apart: {pairs}")
    return "\n".join(lines)


def contrast(faithful: bool = False) -> str:
    """The whole budget: which levels each material flattens, and what each step size buys."""
    lums = _levels(faithful)
    lines = ["material       flat runs of levels (these bake to the same colour)"]
    for material, values in lums.items():
        runs, start = [], 0
        for i in range(1, len(values) + 1):
            if i == len(values) or values[i] != values[start]:
                if i - start > 1:
                    runs.append("%x-%x" % (start, i - 1))
                start = i
        lines.append(f"{material:<14} {', '.join(runs) or 'none'}")
    lines += ["", "step        worst case over all eight materials"]
    for k in range(1, 6):
        pair = min((min(v[i + k] - v[i] for i in range(16 - k)), m) for m, v in lums.items())
        lines.append(f"{k} level(s)   {pair[0]:>3} luma  ({pair[1]})")
    return "\n".join(lines + ["", contrast_rule(faithful), "",
                              "--levels prints what each level bakes to on each material, and the "
                              "best pairs: the worst case above is a floor, not the whole story."])


def reference(mix: float = LIGHT_MIX) -> dict:
    """Every number the bake depends on, as data, so another implementation can be held to it.

    The mod bakes a skin in Java and this bakes it in Python; the two must agree texel for texel
    or a skin looks one way in Blockbench and another in game. Rather than describe the algorithm
    and hope, this writes out what it produces: the eight shades, samples down the 256-entry
    table, and a digest of each material's whole lightmap. A Java test that reads this file and
    disagrees has found a real difference."""
    import hashlib

    out = {
        "note": "generated by python tools/bake_skin.py --reference; the Java bake must match",
        "shades": SHADES, "min_span": MIN_SPAN, "light_mix": mix,
        "materials": {},
    }
    for material in MATERIALS:
        lut = table(material)
        maps = lightmap(material, mix)
        digests = {}
        for sheet, rows in sorted(maps.items()):
            flat = [value for row in rows for value in row]
            digests[sheet] = {
                "sha1": hashlib.sha1(",".join(map(str, flat)).encode()).hexdigest(),
                "nonzero": sum(1 for v in flat if v),
                "min": min(flat), "max": max(flat),
                "samples": [[x, y, rows[y][x]] for x, y in ((20, 20), (24, 24), (44, 22), (8, 8))],
            }
        out["materials"][material] = {
            "ramp": ["%02x%02x%02x" % shade for shade in ramp(material)],
            "table": {str(v): "%02x%02x%02x" % lut[v] for v in range(0, 256, 17)},
            "lightmap": digests,
        }
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("skin", nargs="?", help="a skin under tools/skin_masters")
    parser.add_argument("--material", help="one material (default: all of them)")
    parser.add_argument("--out", default="build/skins", help="where the baked sheets go")
    parser.add_argument("--report", action="store_true", help="every material's ramp and its spread")
    parser.add_argument("--contrast", action="store_true",
                        help="what a step between two master levels buys, per material")
    parser.add_argument("--rule", action="store_true", help="with --contrast: the one line only")
    parser.add_argument("--levels", action="store_true",
                        help="what each of the sixteen levels bakes to, per material")
    parser.add_argument("--pair", nargs=2, metavar=("LO", "HI"),
                        help="what one pair of levels buys on each material, e.g. --pair 6 a")
    parser.add_argument("--ramps", action="store_true", help="the 256-entry tables, as JSON")
    parser.add_argument("--reference", action="store_true",
                        help="write docs/plans/skin-bake-reference.json for the Java half")
    parser.add_argument("--light", type=float, default=LIGHT_MIX,
                        help="how much of vanilla's own lighting to mix back in (0 for none)")
    parser.add_argument("--faithful", action="store_true",
                        help="the octile medians as they come, without deepening them to MIN_SPAN")
    args = parser.parse_args()

    if args.reference:
        path = skin_sheets.ROOT / "docs" / "plans" / "skin-bake-reference.json"
        path.write_text(json.dumps(reference(args.light), indent=2) + "\n", encoding="utf8")
        print(path)
        return
    if args.pair:
        print(pair(args.pair[0], args.pair[1], args.faithful))
        return
    if args.levels:
        print(levels(args.faithful))
        return
    if args.contrast:
        print(contrast_rule(args.faithful) if args.rule else contrast(args.faithful))
        return
    if args.report:
        print(report(args.faithful))
        return
    if args.ramps:
        materials = [args.material] if args.material else MATERIALS
        out = {m: table(m, args.faithful) for m in materials}
        # The lighting rides along with the ramps: the plugin composites its preview the same
        # way this bakes a file, so a skin looks in Blockbench exactly like it will in game.
        out["lightmaps"] = {m: lightmap(m, args.light) for m in materials} if args.light else {}
        print(json.dumps(out))
        return
    if not args.skin:
        parser.print_help()
        sys.exit(2)

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = skin_sheets.ROOT / out_dir
    for material in ([args.material] if args.material else MATERIALS):
        written = bake_skin(args.skin, material, out_dir, args.faithful, args.light)
        print(f"{args.skin} on {material}: " + ", ".join(str(p) for p in written))


if __name__ == "__main__":
    main()
