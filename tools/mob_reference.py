"""
What a mob is actually coloured, for an author drawing a piece taken from one.

A piece from the Animals pack has to READ as its animal at a glance, and the thing that makes a
Minecraft mob recognisable is not its shape - at sixteen pixels nothing is - but its palette. A fox
is eleven colours, three of which are 62% of it. Getting those three right is most of the job, and
guessing them is the one part of authoring an animal piece that no amount of care in Blockbench can
recover from.

So this reads the mob's own texture out of the game and says what is in it: every distinct colour,
ranked by how much of the mob it covers, with the greyscale VALUE each one carries. That last column
is the useful one here, because of how a piece is drawn:

    master        greyscale; its value is a position on the wearer's trim material ramp, so
                  everything drawn here turns iron, gold, netherite... with the armor it sits on
    <part>_static RGBA; these pixels KEEP THEIR OWN COLOUR, shaded by the master's value
    <part>_<fit>  greyscale; the fitting's colour, wherever the fitting is filled

An animal's colours therefore belong in the STATIC layer - a fox that is drawn on the master alone
is a fox-shaped piece of iron. Draw the animal in the static layer with the colours below, and put
only the hardware that should follow the armor (a strap's buckle, a rim, a chain) on the master.
The value column tells you what to paint the master underneath each static colour, so the shading
agrees with the colour instead of fighting it.

Nothing here is redistributed. The palette is NUMBERS derived from the game's own files, which is
exactly what tools/.webcache already keeps (the trim ramps, the armor shades); `--extract` puts a
copy of the texture under tools/.mcassets, which is gitignored, stays on this machine and is the
same arrangement vanilla_assets.py already uses for the rigs' armor.

Usage:
    python tools/mob_reference.py fox                  # the palette, as a table
    python tools/mob_reference.py fox --json           # ... as JSON
    python tools/mob_reference.py fox --extract        # ... and put the PNG where it can be looked at
    python tools/mob_reference.py --list               # every mob texture the game has
    python tools/mob_reference.py --bake fox frog bee  # write tools/.webcache/mob_palettes.json
    python tools/mob_reference.py entity/fox/fox.png   # any texture, by its path in the jar
    python tools/mob_reference.py poppy                # a block or an item, for a piece taken from one

A name that is not an exact texture is matched against the folder names, so `fox` finds
`entity/fox/fox.png` and `donkey` finds `entity/horse/donkey.png`. Where a mob has variants the
plain one wins and the rest are listed, because a piece should look like the mob people picture.
"""

from __future__ import annotations

import argparse
import collections
import io
import json
import sys
from pathlib import Path

from PIL import Image

from vanilla_assets import CACHE, WEBCACHE, Source, find_jar, launcher_jar, minecraft_version

TEXTURES = "assets/minecraft/textures/"
ENTITY = "entity/"

# A baby, a sleeping fox, an angry bee: the same animal in the same colours, and never the picture
# somebody has in mind when they say "fox". Skipped when a plain texture exists beside them.
VARIANT_MARKS = ("_baby", "_sleep", "_angry", "_aggressive", "_worried", "_lazy", "_weak",
                 "_shooting", "_stunned", "_hurt", "_eyes", "_shed")


def sources() -> Source:
    version = minecraft_version()
    jar = find_jar(version)
    if jar is None:
        jar = launcher_jar(Path.home() / "AppData" / "Roaming" / ".minecraft", version)
    if jar is None:
        sys.exit("error: no copy of the game found. Run `gradlew build` once so Loom fetches the "
                 "jar, or pass a jar to vanilla_assets.py's --jar and read its notes.")
    return Source(jar)


def textures(source: Source) -> list[str]:
    """Every texture, as paths relative to the textures folder. Mobs live under entity/, but a
    piece is as often taken from a flower or an item as from an animal, so the search is the whole
    tree with entity/ preferred."""
    return sorted(n[len(TEXTURES):] for n in source.names
                  if n.startswith(TEXTURES) and n.endswith(".png"))


def resolve(source: Source, name: str) -> tuple[str, list[str]]:
    """One texture for `name`, and the other candidates that lost. Accepts an exact path, a mob
    folder, or a bare name."""
    every = textures(source)
    name = name.replace("\\", "/").removeprefix(TEXTURES)
    if name.endswith(".png") and name in every:
        return name, []
    stem = name.removesuffix(".png")
    hits = [t for t in every
            if t.endswith(f"/{stem}/{stem}.png") or f"/{stem}/" in f"/{t}"
            or Path(t).stem == stem or Path(t).stem.startswith(f"{stem}_")]
    if not hits:
        sys.exit(f"error: no entity texture matches {name!r}. `--list` prints them all.")
    plain = [t for t in hits if not any(m in Path(t).stem for m in VARIANT_MARKS)]
    ranked = sorted(plain or hits,
                    key=lambda t: (not t.startswith(ENTITY), Path(t).stem != stem, len(t)))
    return ranked[0], [t for t in hits if t != ranked[0]]


def palette(png: bytes, most: int = 24) -> list[dict]:
    """Every opaque colour in a texture, commonest first, with its share and its greyscale value.

    The value is the same one the mod's own loader reads - the red channel of a grey pixel - so it
    is what to paint on the master under a static pixel of this colour. Rec. 601 luma, because that
    is what reads as "the same brightness" to an eye, and the master's job is the form."""
    image = Image.open(io.BytesIO(png)).convert("RGBA")
    pixels = [p for p in image.getdata() if p[3] > 0]
    if not pixels:
        return []
    counted = collections.Counter(pixels)
    out = []
    for (r, g, b, _a), n in counted.most_common(most):
        out.append({
            "hex": f"#{r:02x}{g:02x}{b:02x}",
            "rgb": [r, g, b],
            "share": round(100 * n / len(pixels), 1),
            "value": round(0.299 * r + 0.587 * g + 0.114 * b),
        })
    return out


def read(source: Source, texture: str) -> bytes:
    return source.read(TEXTURES + texture)


def table(texture: str, colours: list[dict], size: tuple[int, int], others: list[str]) -> str:
    lines = [f"{texture}  {size[0]}x{size[1]}, {len(colours)} colours",
             "  hex      share  value  bar"]
    for c in colours:
        bar = "#" * max(1, round(c["share"] / 2))
        lines.append(f"  {c['hex']}  {c['share']:5.1f}  {c['value']:5d}  {bar}")
    if others:
        lines.append(f"  other textures of this mob: {', '.join(others)}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*", help="a mob, an item, a block, or a texture path")
    ap.add_argument("--list", action="store_true", help="every texture the game has")
    ap.add_argument("--json", action="store_true", help="the palette as JSON")
    ap.add_argument("--extract", action="store_true",
                    help="also copy the texture into tools/.mcassets/reference, to be looked at")
    ap.add_argument("--bake", action="store_true",
                    help="write the named mobs' palettes into tools/.webcache/mob_palettes.json")
    ap.add_argument("--scale", type=int, default=8,
                    help="how much to enlarge the extracted view, nearest-neighbour (default 8)")
    ap.add_argument("--most", type=int, default=24, help="how many colours to print (default 24)")
    args = ap.parse_args()

    source = sources()
    if args.list:
        print("\n".join(textures(source)))
        return
    if not args.names:
        sys.exit("error: name a mob, or pass --list")

    baked: dict = {}
    for name in args.names:
        texture, others = resolve(source, name)
        # A mob with variants has no plain texture to fall back on, and which variant is "the"
        # one is a judgement (a brown rabbit, a temperate frog) that this cannot make. Say so
        # rather than let a palette be taken for the mob's when it is one costume of seven.
        if Path(texture).stem != name.removesuffix(".png").rsplit("/", 1)[-1] and others:
            print(f"note: {name} has no plain texture; showing {texture}. Name one of the "
                  f"{len(others)} others if that is not the one you mean.", file=sys.stderr)
        png = read(source, texture)
        colours = palette(png, args.most)
        size = Image.open(io.BytesIO(png)).size
        if args.extract:
            out = CACHE / "reference" / texture
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(png)
            # And a legible copy. A mob texture is 48x32 or so, which displays at a size nobody
            # can read a pixel off; nearest-neighbour keeps every pixel exactly what it was, and
            # eight times is still a small picture to carry in a conversation.
            view = out.with_name(f"{out.stem}@{args.scale}x.png")
            image = Image.open(io.BytesIO(png))
            image.resize((image.width * args.scale, image.height * args.scale),
                         Image.NEAREST).save(view)
            print(out, file=sys.stderr)
            print(view, file=sys.stderr)
        if args.bake:
            baked[name] = {"texture": texture, "size": list(size), "colours": colours}
        elif args.json:
            print(json.dumps({"texture": texture, "size": list(size), "colours": colours,
                              "others": others}, indent=1))
        else:
            print(table(texture, colours, size, others))
            print()

    if args.bake:
        WEBCACHE.mkdir(parents=True, exist_ok=True)
        path = WEBCACHE / "mob_palettes.json"
        existing = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        existing.update(baked)
        path.write_text(json.dumps(existing, indent=1) + "\n", encoding="utf-8")
        print(f"{path}: {len(existing)} mobs")


if __name__ == "__main__":
    main()
