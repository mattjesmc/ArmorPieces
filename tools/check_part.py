"""
Check one part the way every shipped part is checked before release, in one report.

Two checks exist already and this runs both: `trace_geometry.py` measures the geometry against the
vanilla body, its armor shells and every other part that can share its bone; the checks inside
`sync_decoration_masters.py` hold the sheets against the geometry - a face with no paint behind it,
paint no face samples, colour on a greyscale sheet, a static or mask pixel outside the silhouette.
Neither is new. What is new is that they run over a part wherever it is:

    python tools/check_part.py antlers                # a shipped part, by name
    python tools/check_part.py --all                  # every shipped part
    python tools/check_part.py --status               # the piece open in the Blockbench plugin
    python tools/check_part.py <geometry.json> --anchor horns --master m.png [--static s.png]
                               [--mask gemstone=g.png ...] [--name stem]
    ... --json                                        # the same, as data, with a compact text

The third form is the one the MCP bridge uses. The Blockbench plugin publishes the open piece
after every edit - its model compiled without textures, its sheets as PNGs, a meta.json written
last with a sequence number - into `<tmp>/armorpieces-bb/status/<project>/`, and `current.json`
beside those says which project is active. The bridge's proxy (tools/mcp) runs this over that
folder after every editing call an agent makes and appends the compact text to the reply, so a
face that landed on the helmet shell is reported by the call that put it there.

Reading the report. A **problem** is something that needs a decision before the part is saved:
a COPLANAR face on the part's own shell (move the face, or say why it cannot fight), a COPLANAR
plane shared with another part, a face with no paint behind it (paint it, or cut it on purpose),
paint outside every face, colour on the master or a mask, a static or mask pixel the master's
silhouette does not cover, or a sheet whose size disagrees with the geometry. A **note** is a
datum: a face buried under an outer layer, an OVERLAP that is only a hull test, a near miss, a
pair wider than the shoulders. The exit status is 1 when there are problems.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from PIL import Image

import bb_geo
import sync_decoration_masters as sync
import trace_geometry as trace
from bb_rig import GEO_DIR, ROOT, parse_anchors

MASTERS = ROOT / "tools" / "decoration_masters"
DEC_DIR = trace.DEC_DIR
AXES = trace.AXES


def status_root() -> Path:
    """Where the Blockbench plugin publishes open pieces. The plugin uses Node's os.tmpdir() and
    this uses Python's tempfile.gettempdir(); both read TEMP/TMP, so they agree."""
    return Path(tempfile.gettempdir()) / "armorpieces-bb" / "status"


def current_status_dir() -> Path | None:
    pointer = status_root() / "current.json"
    if not pointer.is_file():
        return None
    uuid = json.loads(pointer.read_text(encoding="utf-8")).get("uuid")
    if not uuid:
        return None
    folder = status_root() / uuid
    return folder if (folder / "meta.json").is_file() else None


# ---- the check ------------------------------------------------------------------------------

def check(geo: dict, anchor: str, anchors: dict, stem: str, master: Image.Image | None,
          static: Image.Image | None, masks: dict[str, Image.Image], geo_error: str | None = None):
    """Everything known about one part, as data. `geo` may be None when it could not be exported;
    `geo_error` then says why, and the paint checks are skipped."""
    problems: list[str] = []
    notes: list[str] = []
    out = {"piece": stem, "anchor": anchor, "geometry": None, "paint": None}

    if geo_error:
        problems.append(f"geometry: {geo_error}")
    elif not sync.geometry_cubes(geo):
        # Bones without a cube yet: mid-build, and nothing to measure.
        problems.append("geometry: no cubes in any bone yet - nothing to measure")
    else:
        g = trace.analyse(geo, anchor, anchors, stem)
        out["geometry"] = g
        problems += [line.strip() for line in g["flagged"]]
        for line in g["clash"]:
            (problems if line.strip().startswith("COPLANAR") else notes).append(line.strip())
        notes += [line.strip() for line in g["buried"]]
        if g["pair_span"] and g["pair_span"]["over"]:
            notes.append(f"pair spans {g['pair_span']['span']:.2f} across the figure, over the 18 "
                         f"the shoulders span")

    if geo is not None and master is not None and sync.geometry_cubes(geo):
        paint = {"size": list(master.size), "empty_faces": [], "outside": 0,
                 "master": [], "static": [], "masks": {}}
        out["paint"] = paint
        want = (geo["texture_width"], geo["texture_height"])
        if want != master.size:
            problems.append(f"paint: the geometry is {want[0]}x{want[1]}, the master is "
                            f"{master.size[0]}x{master.size[1]}")
        else:
            empty, outside = sync.face_coverage(geo, master)
            paint["empty_faces"] = [f"{bone}[{i}].{face}" for _, bone, i, face in empty]
            paint["outside"] = outside
            total = 6 * len(sync.geometry_cubes(geo))
            if empty:
                names = paint["empty_faces"]
                shown = ", ".join(names[:6]) + (f" (+{len(names) - 6} more)" if len(names) > 6 else "")
                problems.append(f"paint: {len(empty)}/{total} faces have no paint behind them and "
                                f"render as holes unless cut on purpose: {shown}")
            if outside:
                problems.append(f"paint: {outside} opaque px outside every face - the master and "
                                f"the model disagree about the shape")
        for w in sync.master_warnings(master, stem):
            paint["master"].append(w)
            (notes if w.startswith("every pixel") else problems).append(f"master: {w}")
        if static is not None:
            paint["static"] = sync.static_warnings(static, master, "static")
            problems += [f"static: {w}" for w in paint["static"]]
        for name, mask in masks.items():
            paint["masks"][name] = sync.mask_warnings(mask, master, f"mask {name}")
            for w in paint["masks"][name]:
                (notes if "entirely transparent" in w else problems).append(w)

    # Where each cube's faces sit on the sheet, for whoever paints by coordinates: the box-UV net
    # the plugin laid out, face by face, as (x, y, w, h) in sheet pixels - and, when there is a
    # master of the right size, how many of each face's texels are painted. A face painted in
    # part is a technique (plumes, ribbons, spur tips), so it is a note here; what a painter
    # wants warned about is a face that WAS complete and is not since a resize, and the bridge
    # reports that from two consecutive reports.
    if geo is not None:
        layout = []
        partial = []
        sized = master is not None and (geo["texture_width"], geo["texture_height"]) == master.size
        px = master.convert("RGBA").load() if sized else None
        for bone, i, cube in sync.geometry_cubes(geo):
            rects = sync.face_rects(cube["size"], cube["uv"])
            item = {"cube": f"{bone}[{i}]", "size": cube["size"], "uv": cube["uv"],
                    "faces": {f: list(r) for f, r in rects.items()}}
            if px is not None:
                coverage = {}
                for f, (x, y, w, h) in rects.items():
                    seen = sum(1 for yy in range(y, y + h) for xx in range(x, x + w)
                               if 0 <= xx < master.size[0] and 0 <= yy < master.size[1] and px[xx, yy][3])
                    coverage[f] = [seen, w * h]
                    if 0 < seen < w * h:
                        partial.append(f"{item['cube']}.{f} {seen}/{w * h}")
                item["coverage"] = coverage
            layout.append(item)
        out["layout"] = layout
        if partial:
            notes.append(f"{len(partial)} face(s) painted in part: {', '.join(partial[:8])}"
                         + (f" (+{len(partial) - 8} more)" if len(partial) > 8 else ""))

    if anchor in anchors:
        out["references"] = references(stem, anchor, anchors)

    own = anchors[anchor]["armor_type"].lower() if anchor in anchors else None
    out.update({"own_shell": own, "problems": problems, "notes": notes, "ok": not problems})
    out["text"] = compact(out)
    out["full"] = full(out)
    return out


def to_blockbench(bone: str, lo, hi):
    """A bone-local box (+Y down, the game's units) as the Blockbench box the rig shows it at:
    the bone's pivot added, then bb_geo's flip - x mirrored, y = 24 - y. Lo and hi swap on the
    two flipped axes."""
    px, py, pz = trace.BODY[bone][0]
    xs = sorted((-(px + lo[0]), -(px + hi[0])))
    ys = sorted((24 - (py + lo[1]), 24 - (py + hi[1])))
    return [xs[0], ys[0], pz + lo[2]], [xs[1], ys[1], pz + hi[2]]


def references(stem: str, anchor: str, anchors: dict) -> dict:
    """The other parts a new one is placed against, as envelopes in the bone's frame and in
    Blockbench's: the parts of the SAME socket, which the clash pass never compares because they
    are never worn together but which are exactly what "the hairline height the circlet uses"
    means; and the bone-mates the clash pass does compare. Saves opening any of them."""
    bone = anchors[anchor]["attachments"][0]["part"]
    same, mates = [], []
    for dec in sorted(DEC_DIR.glob("*.json")):
        if dec.stem == stem:
            continue
        geo_path = GEO_DIR / f"{dec.stem}.json"
        if not geo_path.is_file():
            continue
        entry = json.loads(dec.read_text(encoding="utf-8"))
        geo = json.loads(geo_path.read_text(encoding="utf-8"))
        for name in entry.get("anchors", []):
            if name not in anchors:
                continue
            att = next((a for a in anchors[name]["attachments"] if a["part"] == bone), None)
            if att is None:
                continue
            boxes = trace.placed_cubes(geo, att)
            lo = [min(b[1][a] for b in boxes) for a in range(3)]
            hi = [max(b[2][a] for b in boxes) for a in range(3)]
            blo, bhi = to_blockbench(bone, lo, hi)
            rec = {"part": dec.stem, "socket": name, "cubes": len(boxes),
                   "lo": lo, "hi": hi, "bb_lo": blo, "bb_hi": bhi}
            (same if name == anchor else mates).append(rec)
    return {"bone": bone, "same_socket": same, "mates": mates}


def reference_lines(r: dict) -> list[str]:
    refs = r.get("references")
    if not refs:
        return []

    def row(rec):
        g = "  ".join(f"{AXES[a]} {rec['lo'][a]:6.2f}..{rec['hi'][a]:6.2f}" for a in range(3))
        b = "  ".join(f"{AXES[a]} {rec['bb_lo'][a]:6.2f}..{rec['bb_hi'][a]:6.2f}" for a in range(3))
        return f"    {rec['part']:14s} {g}   |  {b}"

    lines = [f"  envelopes of the other parts on {refs['bone']}, bone-local (+Y down)  |  Blockbench"]
    if refs["same_socket"]:
        lines.append(f"   same socket ({r['anchor']}), never worn together, so never compared - "
                     f"the heights and depths to place against:")
        lines += [row(rec) for rec in refs["same_socket"]]
    if refs["mates"]:
        lines.append("   other sockets on the bone, worn together - what the clash lines above measure:")
        lines += [row(rec) + f"  ({rec['socket']})" for rec in refs["mates"]]
    return lines


def compact(r: dict) -> str:
    """The few lines the bridge appends to every editing reply."""
    g = r["geometry"]
    head = f"[armorpieces] {r['piece']} on {r['anchor']}"
    if g:
        bits = [f"{g['cubes']} cubes", f"reach {g['reach']:.1f}"]
        own = next((out for label, out in g["past"] if label == r["own_shell"]), None)
        if own:
            bits.append(f"past {r['own_shell']} " + " ".join(f"{AXES[a]}{own[a]:+.2f}" for a in range(3)))
        if g["mates"]:
            bits.append("shares " + g["bone"] + " with " + ", ".join(g["mates"]))
        head += " (" + g["bone"] + "): " + "; ".join(bits)
    lines = [head]
    lines += [f"  ! {p}" for p in r["problems"]]
    if r["notes"]:
        lines.append(f"  - {len(r['notes'])} note(s); armorpieces_check lists them")
    n = len(r["problems"])
    lines.append("  ok: nothing needs a decision" if not n
                 else f"  {n} problem(s) need a decision before Save (armorpieces_save refuses "
                      f"without force)")
    return "\n".join(lines)


def full(r: dict) -> str:
    """The whole report: the trace as trace_geometry prints it, then the sheets, then the verdict."""
    lines = []
    if r["geometry"]:
        lines += trace.format_report(r["geometry"])
    lines += reference_lines(r)
    if r.get("layout"):
        lines.append("  sheet layout, per cube: uv offset, size w x h x d, then each face's x,y w x h")
        for item in r["layout"]:
            faces = "  ".join(f"{f} {x},{y} {w}x{h}" for f, (x, y, w, h) in item["faces"].items())
            lines.append(f"    {item['cube']:14s} uv {item['uv'][0]},{item['uv'][1]}  "
                         f"{'x'.join(str(v) for v in item['size'])}:  {faces}")
    paint = r["paint"]
    if paint:
        lines.append(f"  sheet {paint['size'][0]}x{paint['size'][1]}")
        if paint["empty_faces"]:
            lines.append(f"  unpainted faces: {', '.join(paint['empty_faces'])}")
        if paint["outside"]:
            lines.append(f"  paint outside every face: {paint['outside']} px")
        for w in paint["master"]:
            lines.append(f"  master: {w}")
        for w in paint["static"]:
            lines.append(f"  static: {w}")
        for name, ws in paint["masks"].items():
            for w in ws:
                lines.append(f"  {w}")
    lines.append("")
    lines += [f"  ! {p}" for p in r["problems"]]
    lines += [f"  - {n}" for n in r["notes"]]
    lines.append("  ok: nothing needs a decision" if not r["problems"]
                 else f"  {len(r['problems'])} problem(s) need a decision")
    return "\n".join(lines)


# ---- the three ways in ----------------------------------------------------------------------

def open_image(path: Path | None) -> Image.Image | None:
    return Image.open(path) if path and Path(path).is_file() else None


def export_geometry(bb_path: Path, out_path: Path):
    """bb_geo's export, with its sys.exit turned into a message: an agent mid-edit has cubes in
    the wrong place often enough that 'no bones in part' is a finding, not a crash."""
    try:
        return bb_geo.export(bb_path, out_path, quiet=True), None
    except SystemExit as e:
        return None, str(e.code).replace("error: ", "")


def strays(bb_path: Path) -> list[str]:
    """Cubes of a rig project that are neither locked reference nor inside the `part` group: they
    are on screen, they look like part of the part, and bb_geo will never export them."""
    data, cubes, groups = bb_geo.read_bbmodel(bb_path)
    inside: set[str] = set()

    def collect(node):
        for child in node.get("children", []):
            if isinstance(child, str):
                inside.add(child)
            else:
                collect(child)

    part = bb_geo.find_group(data.get("outliner", []), bb_geo.PART_GROUP, groups)
    if part is not None:
        collect(part)
    return [cube.get("name", uid) for uid, cube in cubes.items()
            if uid not in inside and not cube.get("locked")]


def recipe_collision(meta: dict) -> str | None:
    """The template recipe the plugin will write on save, against every shaped recipe already in
    the datapack: every template is the same ring of paper, so the centre item IS the recipe, and
    two parts given the same one is the mistake check_authoring.py catches after the fact. Here
    it is caught before the save writes it."""
    recipe = meta.get("recipe") or {}
    centre = (recipe.get("centre") or "").strip()
    if not centre:
        return None
    import check_authoring
    ring = (recipe.get("ring") or "").strip() or "minecraft:paper"
    mine = check_authoring._shaped_signature({
        "type": "minecraft:crafting_shaped",
        "pattern": [" # ", "#F#", " # "],
        "key": {"#": ring, "F": centre},
    })
    own_file = f"template_{meta.get('piece', {}).get('name')}.json"
    pack = Path(meta.get("piece", {}).get("dataPack") or "")
    for recipe_file in sorted(pack.glob("data/*/recipe/*.json")):
        if recipe_file.name == own_file:
            continue
        try:
            other = check_authoring._shaped_signature(json.loads(recipe_file.read_text(encoding="utf8")))
        except (ValueError, OSError):
            continue
        if other is not None and other == mine:
            return (f"recipe: {centre} in a {ring} ring is already {recipe_file.name}'s grid - "
                    f"one of the two could never be crafted; pick another centre item")
    return None


def from_status(folder: Path):
    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    anchors = parse_anchors()
    anchor = meta.get("anchor")
    stem = meta.get("piece", {}).get("name") or "piece"
    model = folder / meta["files"]["model"]
    geo, err = export_geometry(model, folder / "geometry.json")
    outside = strays(model)
    sheets = meta.get("sheets", {})
    master = open_image(folder / sheets["master"]) if sheets.get("master") else None
    static = open_image(folder / sheets["static"]) if sheets.get("static") else None
    masks = {name: open_image(folder / file)
             for name, file in (sheets.get("masks") or {}).items() if file}
    masks = {k: v for k, v in masks.items() if v is not None}
    if anchor not in anchors:
        err = err or f"unknown anchor {anchor!r}"
    r = check(geo, anchor, anchors, stem, master, static, masks, err)
    if outside:
        r["problems"].append(f"{len(outside)} cube(s) outside the part group, so never exported: "
                             + ", ".join(outside[:6]) + (" ..." if len(outside) > 6 else "")
                             + " - move them into a bone group under part")
    clash = recipe_collision(meta)
    if clash:
        r["problems"].append(clash)
    if outside or clash:
        r["ok"] = False
        r["text"] = compact(r)
        r["full"] = full(r)
    r["status"] = {k: meta.get(k) for k in ("seq", "reason", "time", "unsaved_edits", "part_dirty",
                                            "editing", "fitting", "anchors")}
    r["status"]["key"] = meta.get("piece", {}).get("key")
    r["status"]["dir"] = str(folder)
    return r


def from_shipped(name: str, anchor: str | None):
    anchors = parse_anchors()
    geo_path = GEO_DIR / f"{name}.json"
    if not geo_path.is_file():
        sys.exit(f"no shipped geometry for {name!r} at {geo_path}")
    anchor = anchor or trace.anchor_of(name)
    if anchor is None:
        sys.exit(f"{name}: no armor_decoration entry, so pass --anchor")
    geo = json.loads(geo_path.read_text(encoding="utf-8"))
    master = open_image(MASTERS / f"{name}.png")
    static = open_image(MASTERS / f"{name}{sync.STATIC_SUFFIX}.png")
    masks = {}
    for extra in sync.companions(name):
        if extra.stem != f"{name}{sync.STATIC_SUFFIX}":
            masks[extra.stem[len(name) + 1:]] = Image.open(extra)
    return check(geo, anchor, anchors, name, master, static, masks)


def from_files(geo_path: Path, anchor: str | None, name: str | None, master, static, mask_args):
    anchors = parse_anchors()
    stem = name or geo_path.stem
    anchor = anchor or trace.anchor_of(stem)
    if anchor is None:
        sys.exit("pass --anchor: this geometry has no shipped armor_decoration entry to read it from")
    geo = json.loads(geo_path.read_text(encoding="utf-8"))
    masks = {}
    for arg in mask_args or []:
        if "=" not in arg:
            sys.exit(f"--mask wants name=file, got {arg!r}")
        k, v = arg.split("=", 1)
        masks[k] = Image.open(v)
    return check(geo, anchor, anchors, stem, open_image(master), open_image(static), masks)


def emit(r: dict, as_json: bool, brief: bool) -> None:
    if as_json:
        print(json.dumps(r, indent=None if brief else 2))
    else:
        print(r["text"] if brief else r["full"])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", nargs="?", help="a shipped part name, or a geometry JSON")
    ap.add_argument("--all", action="store_true", help="every shipped part")
    ap.add_argument("--status", nargs="?", const="", metavar="DIR",
                    help="a folder the Blockbench plugin published, or the active piece's when bare")
    ap.add_argument("--anchor", help="the socket to measure against (default: the part's first)")
    ap.add_argument("--name", help="the part's name, for the cross-part pass and the report")
    ap.add_argument("--master", type=Path)
    ap.add_argument("--static", type=Path)
    ap.add_argument("--mask", action="append", metavar="NAME=FILE")
    ap.add_argument("--json", action="store_true", help="the report as data")
    ap.add_argument("--brief", action="store_true", help="the compact text (or one-line JSON)")
    args = ap.parse_args()

    if args.all:
        clean = True
        for geo_path in sorted(GEO_DIR.glob("*.json")):
            r = from_shipped(geo_path.stem, None)
            print(r["text"] if not args.json else json.dumps(r))
            clean &= r["ok"]
        sys.exit(0 if clean else 1)

    if args.status is not None:
        folder = Path(args.status) if args.status else current_status_dir()
        if folder is None or not (folder / "meta.json").is_file():
            sys.exit("no piece is open in the Blockbench plugin (nothing published under "
                     f"{status_root()})")
        r = from_status(folder)
    elif args.target and args.target.endswith(".json"):
        r = from_files(Path(args.target), args.anchor, args.name, args.master, args.static, args.mask)
    elif args.target:
        r = from_shipped(args.target, args.anchor)
    else:
        ap.error("give a part name, a geometry JSON, --status or --all")

    emit(r, args.json, args.brief)
    sys.exit(0 if r["ok"] else 1)


if __name__ == "__main__":
    main()
