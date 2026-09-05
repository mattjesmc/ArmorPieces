"""
Convert vanilla's own chainmail texture into the `chainmail` skin master pair.

Every other skin in `tools/skin_masters` was drawn. This one is not: `docs/plans/armor-skins.md`
asks for "vanilla's own chainmail, converted rather than drawn - its sheet reduced to the sixteen
greys and used as a master", because the weave was that one armor's only trick and the point of the
skin is to take it off chainmail and put it on every other material. So the silhouette, the mesh and
the shading here are all Mojang's; what this script does is requantise them.

    tools/.mcassets/armor/chainmail.png           ->  tools/skin_masters/chainmail/humanoid.png
    tools/.mcassets/armor_leggings/chainmail.png  ->  tools/skin_masters/chainmail/humanoid_leggings.png

Three things have to happen on the way, and only three:

**1. Grey.** Vanilla's chainmail is very slightly tinted - (164, 165, 164), (148, 145, 148) - and a
master's texel is a position on a ramp, not a colour, so every texel becomes its own luminance.

**2. The range.** Chainmail's 526 texels live between luma 146 and 189: four tones inside 43 levels,
which is why the material looks flat and why `bake_skin.py --report` calls its ramp dead. Bake that
straight through and the weave stays as invisible on gold as it is on chainmail. So the sheet is
stretched: vanilla's darkest texel becomes level 1 and its brightest level f, linearly.

That stretch alone gives four levels and reaches four of the eight ramp shades, which
`check_skin.py` rejects - correctly, because four values is a flat master. The four are not the
whole picture though. Vanilla shades each net TOP-BRIGHT TO BOTTOM-DARK - the crown of the helmet at
189, its brow rim at 180, its sides at 164, its bottom two rows at 148 - and had to quantise that
gradient into three or four steps because chainmail's palette has four colours in it. Sixteen greys
do not have that problem. So the conversion restores the gradient at full resolution: per face, the
per-row mean of vanilla's own texels is smoothed with a [1, 2, 1] kernel and becomes the row's base
value, and each texel keeps its own deviation from its raw row mean on top of that. Nothing is
invented - the shape of the gradient, its direction and its endpoints are all read out of the
texture - it is simply expressed in the levels vanilla did not have.

**3. The sole.** `boot.bottom` is bare on vanilla chainmail, the one face where its silhouette has a
hole in it: iron and netherite both fill it and `check_skin.ALWAYS_FILLED` treats a bare one as a
problem, because you see through the foot from below. It is filled flat, at the value the boot's own
hem carries, and it is the only texel in either sheet that vanilla did not put there.

What is deliberately NOT done: the sleeve is not lengthened, the coif does not wrap the cheeks, the
skirt stays three rows. That is chainmail's outline and keeping it is what stops this skin from
converging with the hand-drawn `mail`, which is the fuller harness - a coif, a longer haubergeon,
a gambeson under it. The two are meant to sit side by side.

Usage:
    python tools/convert_chainmail_skin.py            # write the pair and print the check
    python tools/convert_chainmail_skin.py --ascii    # print the pair as well
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

import check_skin
import skin_sheets
from skin_sheets import ASSETS, MASTERS, SHEETS, SHEET_H, SHEET_W, level_of, regions

# The material being converted, and where its two sheets live under tools/.mcassets.
SOURCE = "chainmail"
FOLDERS = {"humanoid": "armor", "humanoid_leggings": "armor_leggings"}

# What vanilla's own range is stretched onto: levels 2..e, the same range brigandine and scale were
# drawn in. Neither end is the ramp's own extreme, and that is deliberate twice over. `e` and `f`
# bake within two luma of each other on iron and on chainmail, so a crown at `f` costs the whole top
# of the ramp and buys nothing; and mail hanging in shadow is dark, not absent. It also keeps the
# stretch honest: chainmail's brightest texel is its crown, and mapping it to `f` made a white cap
# eight levels above the field, where every drawn skin puts its top faces one to two bands above it.
LO, HI = 34, 238

# How much of a texel's departure from its row's mean survives the stretch. At 1.0 the stretch is
# uniform and vanilla's alternating 164/180 rim texels - 16 luma apart, invisible in game - come out
# five levels apart and the rim turns into a dotted line. Two thirds keeps the glint and does not
# let a single-texel wobble outshout the gradient it sits on.
DEVIATION_GAIN = 0.66

# The face vanilla leaves as a hole, and the row whose value fills it.
SOLE = ("boot", "bottom")


def luma(rgb) -> float:
    r, g, b = rgb[:3]
    return 0.299 * r + 0.587 * g + 0.114 * b


def source_pair() -> dict[str, Image.Image]:
    return {sheet: Image.open(ASSETS / folder / f"{SOURCE}.png").convert("RGBA")
            for sheet, folder in FOLDERS.items()}


def smooth(profile: list[float | None]) -> list[float | None]:
    """A [1, 2, 1] pass over a face's per-row means, skipping the rows with no paint on them.

    The rows that carry nothing are the ones above a hanging net's top or below a hem: they are not
    dark, they are absent, so they must not be allowed to drag the rows beside them down."""
    out: list[float | None] = []
    for i, value in enumerate(profile):
        if value is None:
            out.append(None)
            continue
        before = next((profile[j] for j in range(i - 1, -1, -1) if profile[j] is not None), value)
        after = next((profile[j] for j in range(i + 1, len(profile)) if profile[j] is not None), value)
        out.append((before + 2 * value + after) / 4.0)
    return out


def convert(images: dict[str, Image.Image]) -> tuple[dict[str, Image.Image], dict]:
    """Vanilla's pair as a master pair, plus the numbers the conversion was made on."""
    # One stretch for both sheets, from the whole material's range: the leggings are worn under the
    # body and would drift away from it if each sheet were scaled to its own extremes.
    all_values = [luma(images[sheet].load()[x, y])
                  for sheet in SHEETS
                  for y in range(SHEET_H) for x in range(SHEET_W)
                  if images[sheet].load()[x, y][3]]
    lo, hi = min(all_values), max(all_values)
    scale = (HI - LO) / (hi - lo)

    def stretch(value: float) -> float:
        return LO + (value - lo) * scale

    out = {sheet: Image.new("RGBA", (SHEET_W, SHEET_H), (0, 0, 0, 0)) for sheet in SHEETS}
    for sheet in SHEETS:
        src, dst = images[sheet].load(), out[sheet].load()
        for region in regions(sheet).values():
            for face, (x, y, w, h) in region["faces"].items():
                rows = []
                for dy in range(h):
                    seen = [luma(src[x + dx, y + dy]) for dx in range(w) if src[x + dx, y + dy][3]]
                    rows.append(sum(seen) / len(seen) if seen else None)
                base = smooth(rows)
                for dy in range(h):
                    if rows[dy] is None:
                        continue
                    for dx in range(w):
                        if not src[x + dx, y + dy][3]:
                            continue
                        deviation = (luma(src[x + dx, y + dy]) - rows[dy]) * DEVIATION_GAIN
                        value = round(stretch(base[dy] + deviation))
                        value = skin_sheets.value_of(level_of(value))
                        dst[x + dx, y + dy] = (value, value, value, 255)

    sole = fill_sole(out["humanoid"], images["humanoid"])
    return out, {"vanilla range": f"{lo:.0f}..{hi:.0f}", "sole": sole}


def fill_sole(master: Image.Image, vanilla: Image.Image) -> int:
    """Fill the one face vanilla leaves as a hole, at the value the boot's own hem carries."""
    region = regions("humanoid")[SOLE[0]]
    hx, hy, hw, hh = region["faces"]["front"]
    px, src = master.load(), vanilla.load()
    hem = [px[hx + dx, hy + hh - 1][0] for dx in range(hw) if src[hx + dx, hy + hh - 1][3]]
    value = round(sum(hem) / len(hem)) if hem else LO
    value = skin_sheets.value_of(level_of(value))

    x, y, w, h = region["faces"][SOLE[1]]
    for dy in range(h):
        for dx in range(w):
            px[x + dx, y + dy] = (value, value, value, 255)
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--ascii", action="store_true", help="print the converted pair")
    parser.add_argument("--out", type=Path, default=MASTERS / SOURCE,
                        help="where the pair goes (default: tools/skin_masters/chainmail)")
    args = parser.parse_args()

    images, facts = convert(source_pair())
    args.out.mkdir(parents=True, exist_ok=True)
    for sheet in SHEETS:
        images[sheet].save(args.out / f"{sheet}.png")
    print(f"chainmail: converted vanilla {facts['vanilla range']} -> {LO}..{HI}, "
          f"sole filled at {facts['sole']}, written to {args.out}")

    if args.ascii:
        for sheet in SHEETS:
            print(f"\n{sheet}")
            for line in skin_sheets.to_ascii(images[sheet]):
                print("  " + line)

    report = check_skin.analyse(images, SOURCE)
    print()
    for line in report.get("problems", []):
        print(f"  ! {line}")
    for line in report.get("notes", []):
        print(f"  - {line}")
    if report.get("problems"):
        sys.exit(1)


if __name__ == "__main__":
    main()
