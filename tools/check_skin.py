"""
Check an armor skin's master pair the way check_part.py checks a part.

A skin is two greyscale sheets on vanilla's grid (skin_sheets.py), coloured per material at load
time from a ramp derived from that material's own texture (bake_skin.py). Almost everything that can
go wrong with one is invisible while you are painting it and obvious in game:

  * paint outside every net rectangle - texels no face samples, so work that will never be seen;
  * colour on a sheet whose value is read as a position on a ramp, where a colour is not a colour
    but the wrong shade;
  * a slot with nothing painted at all, which renders as no armor rather than as plain armor;
  * a painted visor. The face opening is the shape the `brow` socket is designed to sit in, and
    seven parts are drawn expecting it. A skin never paints one - it is a part's job;
  * and the one that only shows up across eight materials at once: a master drawn inside a narrow
    band of greys. The bake spends eight shades on the range the master actually uses, so a master
    that lives between 40% and 60% grey throws six of them away and comes out flat on every
    material. Netherite's own sheet has exactly this problem, which is why the plan says to redraw
    it rather than reuse it;
  * and its twin, which is not about the range but about the STEPS in it: a texel is not read at
    the value it was drawn at. Vanilla's own texture for the material is added first, and between
    two texels side by side it can put five levels of its own - so shading drawn in small bands
    bakes level, or the wrong way round, and the greyscale says nothing about it. `against_light`
    counts the pairs it really happens to.

Lines marked `!` are problems that need a decision before the skin is saved; `-` lines are notes.

Usage:
    python tools/check_skin.py plate               # one skin under tools/skin_masters
    python tools/check_skin.py --all
    python tools/check_skin.py --status <dir>      # what the Blockbench plugin published
    python tools/check_skin.py plate --json --brief
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image

import bake_skin
import skin_sheets as sheets_mod
from skin_sheets import (ANATOMY, FACE_WINDOW, MASTERS, SHEETS, SHEET_H, SHEET_W,
                         level_of, owners, regions)

# How many of the eight ramp shades a master has to reach to be worth baking, and the least spread
# between its darkest and lightest texel. Both are floors, not targets: a good master uses the range.
MIN_OCTILES, MIN_SPREAD = 6, 110

# What share of the drawn steps vanilla's own lighting may overrule before it is a problem rather
# than a fact. Some is unavoidable and wanted - the light is mixed in on purpose - but a master
# whose shading loses more often than not is a master drawn in steps too small to survive its own
# armor, and the fix is bigger bands, not a different mix. See against_light.
MAX_LIGHT_LOSS = 0.35

# Every armor slot has to carry paint somewhere, or that piece of armor renders as nothing.
SLOTS = ("helmet", "chestplate", "leggings", "boots")

# Where a boot stops. Vanilla's boots paint the bottom six rows of the twelve-row leg net; above
# that the leggings are what shows, so a boot drawn higher hides them.
BOOT_TOP_ROW = 6

# The faces every vanilla armor set fills, measured off iron and netherite rather than assumed:
# the crown, the top of the sleeve, the top of the thigh, the sole. Bare, they are a hole you
# look through from above - unlike chest.top and waist.top, which vanilla leaves empty too.
ALWAYS_FILLED = ("helmet.top", "arm.top", "leg.top", "boot.bottom")

# Nets that share a bone and a box, the outer one more inflated than the inner: it renders in
# front of it texel for texel, so paint on the inner one underneath is never seen. The four
# slots overlap in space and vanilla resolves it by leaving rows empty; this says the same
# thing from what the skin actually paints.
SHELLS = (("boot", "leg"), ("chest", "waist"), ("helmet_raised", "helmet"))


def pinned_to(name: str) -> str | None:
    """The material a skin has pinned its silhouette to, or None.

    `tools/skin_masters/<skin>/silhouette` holds a material name, written by
    `skin_sheets.py --seed`. It is opt-in per skin because a skin is normally allowed to depart
    from vanilla's outline on purpose - a longer boot, a coat-length hem."""
    marker = MASTERS / name / "silhouette"
    if not marker.is_file():
        return None
    parts = marker.read_text("utf8").split()
    return parts[0] if parts else "iron"


def seed_level(name: str) -> int | None:
    """The flat grey a pinned skin was seeded at, so what is still untouched can be counted."""
    marker = MASTERS / name / "silhouette"
    if not marker.is_file():
        return None
    parts = marker.read_text("utf8").split()
    if len(parts) < 2:
        return None
    try:
        return int(parts[1], 16)
    except ValueError:
        return None


def drawn_steps(images: dict[str, Image.Image]) -> dict[str, list[tuple[int, int, int, int, int]]]:
    """Every adjacent pair of painted texels the master puts a step between, per sheet.

    `(x, y, nx, ny, step)`, where `step` is the second texel's value minus the first's. Measured
    once and reused across the materials, because the drawing does not change per material and the
    lighting does."""
    out: dict[str, list[tuple[int, int, int, int, int]]] = {}
    for sheet, image in images.items():
        if image is None:
            continue
        px = image.convert("RGBA").load()
        width, height = image.size
        found = []
        for y in range(height):
            for x in range(width):
                r, g, b, a = px[x, y]
                if not a:
                    continue
                here = r if r == g == b else round(bake_skin.luma((r, g, b)))
                for nx, ny in ((x + 1, y), (x, y + 1)):
                    if nx >= width or ny >= height:
                        continue
                    r2, g2, b2, a2 = px[nx, ny]
                    if not a2:
                        continue
                    there = r2 if r2 == g2 == b2 else round(bake_skin.luma((r2, g2, b2)))
                    if there != here:
                        found.append((x, y, nx, ny, there - here))
        out[sheet] = found
    return out


def against_light(images: dict[str, Image.Image],
                  mix: float = bake_skin.LIGHT_MIX) -> tuple[str, int, int]:
    """How much of the drawing vanilla's own lighting overrules, on the material it hurts most.

    A texel's value is not what the ramp is read at. The material's own texture - the panel edges,
    the rim along the top of a plate, the shadow under an overhang - is measured as a signed offset
    and added to the value first (`bake_skin.lightmap`, `SkinBake.lightmap`), which is what keeps a
    skinned plate reading as metal rather than as a flat pattern. It also means a pair of texels the
    author drew a step apart can come out level, or the other way round, wherever vanilla puts more
    between them than the author did - and none of that is visible in the greyscale, which is the
    only thing being drawn.

    So this counts the pairs it really happens to rather than quoting the worst case, which is
    useless as advice: vanilla's textures have hard edges, so somewhere on every sheet the offset
    jumps its whole range and "a step of six levels or nothing" is the only safe rule. The share
    below is what the drawing in hand actually loses. Returns the worst material, that count, and
    how many steps the master drew at all."""
    steps = drawn_steps(images)
    worst = ("", 0, 0)
    worst_share = -1.0
    for material in bake_skin.MATERIALS:
        maps = bake_skin.lightmap(material, mix)
        spoiled = drawn = 0
        for sheet, pairs in steps.items():
            rows = maps.get(sheet)
            if rows is None:
                continue
            for x, y, nx, ny, step in pairs:
                drawn += 1
                after = step + (rows[ny][nx] - rows[y][x])
                # Level, or the wrong way round: either way the pair no longer says what it said.
                if after == 0 or (after > 0) != (step > 0):
                    spoiled += 1
        if not drawn:
            continue
        share = spoiled / drawn
        if share > worst_share:
            worst_share = share
            worst = (material, spoiled, drawn)
    return worst


def against_vanilla(images: dict[str, Image.Image], material: str) -> tuple[list[str], list[str]]:
    """Per face: texels painted where vanilla has none, and vanilla texels left bare."""
    extra, missing = [], []
    for sheet, folder in (("humanoid", "armor"), ("humanoid_leggings", "armor_leggings")):
        image = images.get(sheet)
        source = sheets_mod.ASSETS / folder / f"{material}.png"
        if image is None or not source.is_file():
            continue
        with Image.open(source) as opened:
            vanilla = opened.convert("RGBA").load()
        px = image.load()
        for region in regions(sheet).values():
            for face, (x, y, w, h) in region["faces"].items():
                over = under = 0
                for dy in range(h):
                    for dx in range(w):
                        mine, theirs = px[x + dx, y + dy][3], vanilla[x + dx, y + dy][3]
                        if mine and not theirs:
                            over += 1
                        elif theirs and not mine:
                            under += 1
                where = f"{region['region']}.{face}"
                if over:
                    extra.append(f"{where} {over}")
                if under:
                    missing.append(f"{where} {under}")
    return extra, missing


def _load(path: Path) -> Image.Image:
    with Image.open(path) as image:
        return image.convert("RGBA")


def sheet_facts(image: Image.Image, sheet: str) -> dict:
    """Everything the checks need from one sheet, in one pass over its texels."""
    px = image.load()
    w, h = image.size
    own = owners(sheet)
    facts = {
        "sheet": sheet, "size": (w, h),
        "opaque": 0, "coloured": 0, "stray": [], "values": [],
        "coverage": {}, "region_paint": {},
    }
    for region in regions(sheet).values():
        for face, (x, y, fw, fh) in region["faces"].items():
            got = 0
            for dy in range(fh):
                for dx in range(fw):
                    if 0 <= x + dx < w and 0 <= y + dy < h and px[x + dx, y + dy][3]:
                        got += 1
            facts["coverage"][f"{region['region']}.{face}"] = (got, fw * fh)
            facts["region_paint"][region["region"]] = facts["region_paint"].get(region["region"], 0) + got

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if not a:
                continue
            facts["opaque"] += 1
            if not (r == g == b):
                facts["coloured"] += 1
            facts["values"].append(r if r == g == b else round(0.299 * r + 0.587 * g + 0.114 * b))
            if (x, y) not in own:
                facts["stray"].append((x, y))
    return facts


def face_window_open(image: Image.Image) -> tuple[int, int]:
    """How much of the helmet's face opening is transparent, out of how much there is."""
    fx, fy, fw, fh = sheets_mod.rect_of("helmet", "front")
    wx, wy, ww, wh = FACE_WINDOW
    px = image.load()
    open_count = 0
    for dy in range(wh):
        for dx in range(ww):
            x, y = fx + wx + dx, fy + wy + dy
            if not px[x, y][3]:
                open_count += 1
    return open_count, ww * wh


def octiles(values: list[int]) -> tuple[int, int, int]:
    """How many of the eight ramp shades this master reaches, and the range it spans."""
    if not values:
        return 0, 0, 0
    lo, hi = min(values), max(values)
    used = {min(7, v * 8 // 256) for v in values}
    return len(used), lo, hi


def occluded(images: dict[str, Image.Image]) -> list[str]:
    """Paint on an inner shell that an outer one covers texel for texel - work that renders
    nowhere. A boot at vanilla's height hides the bottom six rows of the leg net behind it, and
    the cuirass hides the top of the waist net, so a fauld is only ever the rows below it."""
    table = regions()
    lines = []
    for outer, inner in SHELLS:
        outside, inside = table.get(outer), table.get(inner)
        if not outside or not inside:
            continue
        image_o, image_i = images.get(outside["sheet"]), images.get(inside["sheet"])
        if image_o is None or image_i is None:
            continue
        px_o, px_i = image_o.load(), image_i.load()
        hidden, rows, faces = 0, set(), []
        shown: set[int] = set()   # rows of the inner net that still show something
        for face, (ix, iy, iw, ih) in sorted(inside["faces"].items()):
            rect = outside["faces"].get(face)
            if not rect or tuple(rect[2:]) != (iw, ih):
                continue
            count = 0
            for dy in range(ih):
                for dx in range(iw):
                    if not px_i[ix + dx, iy + dy][3]:
                        continue
                    if px_o[rect[0] + dx, rect[1] + dy][3]:
                        count += 1
                        rows.add(dy)
                    else:
                        shown.add(dy)
            if count:
                hidden += count
                faces.append(face)
        if hidden:
            span = f"row {min(rows)}" if len(rows) == 1 else f"rows {min(rows)}..{max(rows)}"
            # What is left is the number the drawing is actually designed against, so it is
            # worth as much as what is lost.
            left = sorted(shown)
            shows = (f"rows {left[0]}..{left[-1]} still show" if len(left) > 1
                     else f"row {left[0]} still shows" if left else "nothing of it shows")
            lines.append(f"{inner}: {hidden} painted texel(s) hidden by {outer} (inflate "
                         f"{outside['inflate']} over {inside['inflate']}) - {span} of "
                         f"{', '.join(faces)}; {shows}")
    return lines


def analyse(images: dict[str, Image.Image], name: str) -> dict:
    """The whole report for one skin as data: problems, notes, and the numbers behind them."""
    problems: list[str] = []
    notes: list[str] = []
    facts = {}

    for sheet in SHEETS:
        image = images.get(sheet)
        if image is None:
            problems.append(f"{sheet}: no sheet - a skin is a pair, and the game loads both")
            continue
        if image.size != (SHEET_W, SHEET_H):
            problems.append(f"{sheet}: {image.size[0]}x{image.size[1]}, not {SHEET_W}x{SHEET_H} - "
                            f"a skin sits on vanilla's grid or it sits nowhere")
            continue
        facts[sheet] = sheet_facts(image, sheet)

    values: list[int] = []
    for sheet, f in facts.items():
        values += f["values"]
        if f["coloured"]:
            problems.append(f"{sheet}: {f['coloured']} opaque texel(s) are not grey - the bake reads "
                            f"a texel's value as a position on the material's ramp, so colour here "
                            f"is a wrong shade, not a colour")
        if f["stray"]:
            spots = ", ".join(f"{x},{y}" for x, y in f["stray"][:6])
            more = f" (+{len(f['stray']) - 6} more)" if len(f["stray"]) > 6 else ""
            problems.append(f"{sheet}: {len(f['stray'])} texel(s) outside every net - no face samples "
                            f"them: {spots}{more}")

    # Every slot has to be somewhere, or that piece renders as nothing at all.
    painted_regions = {r: n for f in facts.values() for r, n in f["region_paint"].items() if n}
    by_slot: dict[str, int] = {}
    for region in regions().values():
        by_slot[region["slot"]] = by_slot.get(region["slot"], 0) + painted_regions.get(region["region"], 0)
    for slot in SLOTS:
        if not by_slot.get(slot):
            problems.append(f"{slot}: nothing painted - that piece of armor would render as nothing. "
                            f"Its nets are " +
                            ", ".join(r["region"] for r in regions().values() if r["slot"] == slot))

    # The face opening.
    if "humanoid" in facts:
        open_count, window = face_window_open(images["humanoid"])
        if open_count == 0:
            problems.append("helmet.front: the face opening is painted shut - a skin never paints a "
                            "visor, that is what the seven brow parts are for. Clear the window at "
                            f"{FACE_WINDOW[0]},{FACE_WINDOW[1]} {FACE_WINDOW[2]}x{FACE_WINDOW[3]} "
                            "inside helmet.front (sheet 9,11 6x5)")
        elif open_count < window // 2:
            notes.append(f"helmet.front: {open_count} of {window} texels of the face window are open - "
                         "netherite leaves the whole of it open and wraps the cheeks instead")

    # The ramp. While a slot is still blank the skin is half drawn and its range is going to move,
    # so this is only a problem once there is a whole skin to judge - otherwise it would nag through
    # every call of a session that is doing nothing wrong.
    reached, lo, hi = octiles(values)
    half_drawn = any(not by_slot.get(slot) for slot in SLOTS)
    if values:
        if reached < MIN_OCTILES or (hi - lo) < MIN_SPREAD:
            line = (f"value range {lo}..{hi} reaches {reached} of the 8 ramp shades - a master "
                    f"drawn in a narrow band comes out flat on every material. Draw the "
                    f"deepest shadow near 0 and the brightest highlight near 255")
            (notes if half_drawn else problems).append(line)
        else:
            notes.append(f"value range {lo}..{hi}, {reached} of 8 ramp shades reached")

    # The other half of the contrast budget, and the half the range above says nothing about: what
    # vanilla's own lighting does to the drawing once it is added to the value. Skipped while the
    # skin is half drawn, for the reason the ramp check is: the numbers are still moving.
    light_material, spoiled, drawn_pairs = ("", 0, 0)
    if facts and not half_drawn:
        light_material, spoiled, drawn_pairs = against_light(images)
    if drawn_pairs:
        share = spoiled / drawn_pairs
        line = (f"vanilla's light overrules {spoiled} of {drawn_pairs} drawn steps "
                f"({share * 100:.0f}%) on {light_material}: neighbours that bake level or the wrong "
                f"way round, the material's own texture being added to the value before the ramp "
                f"is read")
        if share > MAX_LIGHT_LOSS:
            problems.append(line + f". Over {MAX_LIGHT_LOSS * 100:.0f}% is shading too small to "
                                   f"survive its own armor - draw the bands further apart "
                                   f"(bake_skin.py --lighting)")
        else:
            notes.append(line + " - the light doing its job; judge it on a material, not in grey")

    # Cut faces, and the raised helmet shell.
    for sheet, f in facts.items():
        # A net with nothing on it at all is one line, not six: `helmet_raised` is unpainted on
        # every vanilla material, and listing its faces would bury the face that was forgotten.
        blank_regions = {r for r in regions(sheet) if not f["region_paint"].get(r)}
        cut = [k for k, (got, area) in sorted(f["coverage"].items())
               if got == 0 and k.split(".")[0] not in blank_regions]
        # `helmet_raised` is blank on every vanilla material and on nearly every skin, so it is
        # the expected state rather than news - it has its own note below when it IS painted.
        unexpected = sorted(blank_regions - {"helmet_raised"})
        if unexpected:
            notes.append(f"{sheet}: nets with nothing on them: {', '.join(unexpected)}")
        if cut:
            notes.append(f"{sheet}: unpainted faces (cut on purpose, or forgotten): {', '.join(cut)}")

    bare = [key for key in ALWAYS_FILLED
            for f in facts.values()
            if f["coverage"].get(key) and f["coverage"][key][0] == 0]
    if bare:
        line = (f"{', '.join(bare)}: bare, and every vanilla set fills them - the crown, the top of"
                f" the sleeve and of the thigh, the sole. You see through the armor from above")
        (notes if half_drawn else problems).append(line)

    # A skin pinned to a silhouette is drawn on vanilla's own outline and may not leave it: this
    # is what makes a session's shape correct by construction rather than by judgement.
    material = pinned_to(name)
    if material:
        level = seed_level(name)
        if level is not None:
            untouched = sum(1 for v in values if v == level * 17)
            if untouched:
                share = untouched * 100 // max(1, len(values))
                (notes if half_drawn else problems).append(
                    f"{untouched} texel(s) ({share}%) are still the flat grey this skin was seeded "
                    f"at - level {level:x} is reserved for 'not yet drawn' on a seeded skin, so do "
                    f"not use it as a value; the skin is finished when none are left")
        extra, missing = against_vanilla(images, material)
        if missing:
            (notes if half_drawn else problems).append(
                f"bare where vanilla {material} paints: {', '.join(missing)} - this skin is pinned "
                f"to that silhouette, so every texel of it carries paint (counts are texels)")
        if extra:
            (notes if half_drawn else problems).append(
                f"painted where vanilla {material} is clear: {', '.join(extra)} - outside the "
                f"silhouette this skin is pinned to; the armor grows where vanilla ends")
        if not extra and not missing:
            notes.append(f"silhouette matches vanilla {material} exactly")

    raised = painted_regions.get("helmet_raised", 0)
    if raised:
        notes.append(f"helmet_raised: {raised} texel(s). That shell is half a unit proud of the helmet "
                     f"and no vanilla material paints it, so it is a real second layer - and it is "
                     f"where crest and brow parts sit. Check it against them in game before shipping")

    # A boot drawn above vanilla's boot line hides the leggings under it.
    if "humanoid" in facts:
        px = images["humanoid"].load()
        high = 0
        for face in ("front", "back", "right", "left"):
            x, y, w, h = sheets_mod.rect_of("boot", face)
            for dy in range(h - BOOT_TOP_ROW):
                for dx in range(w):
                    if px[x + dx, y + dy][3]:
                        high += 1
        if high:
            notes.append(f"boot: {high} texel(s) above vanilla's boot line (the bottom {BOOT_TOP_ROW} "
                         f"rows of the leg net) - a tall boot covers the leggings behind it")

    notes += occluded(images)

    coverage = {}
    for sheet, f in facts.items():
        coverage[sheet] = f["coverage"]

    return {
        "skin": name,
        "ok": not problems,
        "problems": problems,
        "notes": notes,
        "values": {"low": lo, "high": hi, "shades": reached, "opaque": len(values)},
        "light": {"material": light_material, "spoiled": spoiled, "steps": drawn_pairs},
        "regions": painted_regions,
        "coverage": coverage,
    }


def brief(report: dict) -> str:
    lines = [f"[armorpieces] skin {report['skin']}: "
             f"{report['values']['opaque']} texels, {report['values']['shades']}/8 shades"]
    for problem in report["problems"]:
        lines.append(f"  ! {problem}")
    for note in report["notes"]:
        lines.append(f"  - {note}")
    lines.append("  ok" if not report["problems"] else f"  {len(report['problems'])} problem(s)")
    return "\n".join(lines)


def full(report: dict) -> str:
    lines = [f"skin {report['skin']}", ""]
    for sheet, coverage in report["coverage"].items():
        lines.append(f"{sheet}:")
        for face, (got, area) in sorted(coverage.items()):
            bar = "full" if got == area else ("cut " if got == 0 else f"{got * 100 // area:>3}%")
            lines.append(f"    {face:<22} {bar}  {got}/{area}")
        lines.append("")
    lines.append(f"values {report['values']['low']}..{report['values']['high']}, "
                 f"{report['values']['shades']} of 8 ramp shades, "
                 f"{report['values']['opaque']} opaque texels")
    lines.append("")
    lines.append(brief(report))
    return "\n".join(lines)


def from_status(directory: Path) -> tuple[dict, str]:
    """The pair the Blockbench plugin published for the open skin, unsaved edits included."""
    meta = json.loads((directory / "meta.json").read_text("utf8"))
    if meta.get("kind") != "skin":
        raise SystemExit(f"{directory} is not a skin's status folder (kind={meta.get('kind')!r})")
    images = {}
    for sheet, file in (meta.get("sheets") or {}).items():
        path = directory / file
        if path.is_file():
            images[sheet] = _load(path)
    return images, meta.get("skin", "?")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("skin", nargs="?", help="a skin under tools/skin_masters")
    parser.add_argument("--all", action="store_true", help="every skin under tools/skin_masters")
    parser.add_argument("--status", metavar="DIR", help="a status folder written by the plugin")
    parser.add_argument("--json", action="store_true", help="the report as JSON")
    parser.add_argument("--brief", action="store_true", help="only the compact block")
    args = parser.parse_args()

    reports = []
    if args.status:
        images, name = from_status(Path(args.status))
        reports.append(analyse(images, name))
    else:
        names = []
        if args.all:
            names = sorted(d.name for d in MASTERS.glob("*") if d.is_dir())
        elif args.skin:
            names = [args.skin]
        else:
            parser.print_help()
            sys.exit(2)
        for name in names:
            paths = sheets_mod.pair_paths(name)
            images = {sheet: _load(path) for sheet, path in paths.items() if path.is_file()}
            if not images:
                sys.exit(f"no sheets for skin {name!r} under {MASTERS / name}")
            reports.append(analyse(images, name))

    if args.json:
        for report in reports:
            print(json.dumps({**report, "text": brief(report), "full": full(report)}))
    else:
        for report in reports:
            print(brief(report) if args.brief else full(report))

    sys.exit(1 if any(r["problems"] for r in reports) else 0)


if __name__ == "__main__":
    main()
