"""
Copy pieces, skins and cloths between packs, by id, credits and all.

The composer on the site, the cherry-picker in the editor and a command line are the same
tool: given source packs, a list of namespaced ids and a destination, it copies each entry's
file set as pack_manifest.py lists it - the geometry, the master and its layer sheets, the
data file, the template recipe, the language line, the loot-group tags it belongs to, and any
fitting a source pack defines that the piece declares - and writes the union of the sources'
credits into the destination.

Three refusals, all on purpose:

  - an entry whose license is `ARR` (all rights reserved) is not copied unless `--own` says the
    caller is the author and may do what they like with their own;
  - two sources offering different entries under one id is an error, not a coin toss;
  - an id the destination already holds with different content is not overwritten.

Usage:
    python tools/pick_pieces.py --from <pack> [--from <pack>...] --to <dest> [--own] [--name N] id...
    python tools/pick_pieces.py --from src/main/resources --to build/mine armorpieces:circlet --own
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

import pack_manifest
from pack_manifest import CREDITS_FILE, KINDS, LICENSES, find, read_json

ROOT = Path(__file__).resolve().parent.parent
GRADLE_PROPERTIES = ROOT / "gradle.properties"


class PickError(Exception):
    pass


def pack_formats() -> tuple[int, int]:
    """The two pack formats the game this mod is built for wants, from the one file that says."""
    text = GRADLE_PROPERTIES.read_text(encoding="utf-8") if GRADLE_PROPERTIES.is_file() else ""
    resource = re.search(r"^resourcepack_format\s*=\s*(\d+)", text, re.MULTILINE)
    data = re.search(r"^datapack_format\s*=\s*(\d+)", text, re.MULTILINE)
    return (int(resource.group(1)) if resource else 0, int(data.group(1)) if data else 0)


def locate(sources: list[list[Path]], piece_id: str) -> tuple[str, list[Path], dict]:
    """Which source holds the id and as what kind. Every source is asked, so that two sources
    holding different things under one id is seen rather than the first one winning."""
    hits: list[tuple[str, list[Path], dict]] = []
    for dirs in sources:
        for kind in KINDS:
            for entry in pack_manifest.entries(dirs, kind):
                if entry["id"] == piece_id:
                    hits.append((kind, dirs, entry))
    if not hits:
        raise PickError(f"{piece_id}: not in any source pack")
    if len(hits) > 1:
        first = hits[0]
        for other in hits[1:]:
            if other[0] != first[0] or not same_content(first[1], other[1], first[2]["files"]):
                raise PickError(f"{piece_id}: two different entries under one id, in "
                                f"{first[1][0]} and {other[1][0]}")
    return hits[0]


def same_content(a: list[Path], b: list[Path], files: list[str]) -> bool:
    for relative in files:
        left, right = find(a, relative), find(b, relative)
        if left is None or right is None or left.read_bytes() != right.read_bytes():
            return False
    return True


def copy_file(sources: list[Path], dest: Path, relative: str, piece_id: str) -> str:
    source = find(sources, relative)
    if source is None:
        raise PickError(f"{piece_id}: {relative} is listed but missing")
    target = dest / relative
    if target.exists() and target.read_bytes() != source.read_bytes():
        raise PickError(f"{piece_id}: {relative} already exists in {dest} with different content")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    return relative


def merge_json(target: Path, update: dict) -> None:
    current = read_json(target) if target.is_file() else {}
    if not isinstance(current, dict):
        current = {}
    current.update(update)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def add_tag_member(target: Path, piece_id: str) -> None:
    body = read_json(target) if target.is_file() else {"values": []}
    values = body.setdefault("values", [])
    ids = [v.get("id") if isinstance(v, dict) else v for v in values]
    if piece_id not in ids:
        values.append(piece_id)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")


def lang_lines(dirs: list[Path], namespace: str, keys: list[str]) -> dict:
    lang = pack_manifest.lang_of(dirs, namespace)
    return {k: lang[k] for k in keys if k in lang}


def fitting_files(dirs: list[Path], fitting_id: str) -> list[str]:
    """A fitting definition a source pack carries, with its template recipe and any tags it
    names. Only when the source defines it: a piece using the mod's own `armorpieces:gemstone`
    needs nothing copied, since the game has it."""
    namespace, name = pack_manifest.split_id(fitting_id)
    definition = f"data/{namespace}/armorpieces/fitting/{name}.json"
    if find(dirs, definition) is None:
        return []
    files = [definition]
    recipe = f"data/{namespace}/recipe/fitting_template_{name}.json"
    if find(dirs, recipe) is not None:
        files.append(recipe)
    try:
        materials = read_json(find(dirs, definition)).get("materials")
    except ValueError:
        materials = None
    if isinstance(materials, str) and materials.startswith("#"):
        tag_ns, tag_name = pack_manifest.split_id(materials[1:])
        tag = f"data/{tag_ns}/tags/trim_material/{tag_name}.json"
        if find(dirs, tag) is not None:
            files.append(tag)
    return files


def loot_groups_using(dirs: list[Path], tag_relative: str) -> list[str]:
    """Loot group definitions that name this tag, which the tag is nothing without."""
    parts = Path(tag_relative).parts  # data/<ns>/tags/armorpieces/armor_decoration/<tag>.json
    tag_id = f"#{parts[1]}:{Path(parts[-1]).stem}"
    out = []
    for d in dirs:
        data = d / "data"
        if not data.is_dir():
            continue
        for path in sorted(data.glob("*/armorpieces/loot_group/*.json")):
            try:
                if read_json(path).get("parts") == tag_id:
                    out.append(path.relative_to(d).as_posix())
            except ValueError:
                continue
    return out


def ensure_mcmeta(dest: Path, name: str, sources: list[list[Path]]) -> None:
    if (dest / "pack.mcmeta").is_file():
        return
    resource, data = pack_formats()
    formats = [f for f in (resource, data) if f]
    body = {"pack": {"description": f"{name}, composed from " +
                     ", ".join(sorted({d[0].name for d in sources})),
                     "pack_format": min(formats) if formats else 0}}
    if len(formats) == 2 and resource != data:
        # One folder is both halves; the game reads the range where it reads the number.
        body["pack"]["min_format"] = min(formats)
        body["pack"]["max_format"] = max(formats)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "pack.mcmeta").write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")


def pick(sources: list[list[Path]], ids: list[str], dest: Path, own: bool = False,
         name: str | None = None) -> dict:
    """Copy every id into dest. Returns what was written, per id. Nothing is written until every
    id has been checked, so a refusal leaves the destination as it was."""
    dest = Path(dest).resolve()
    name = name or dest.name
    plan = []
    for piece_id in ids:
        kind, dirs, entry = locate(sources, piece_id)
        if entry["license"] == "ARR" and not own:
            raise PickError(f"{piece_id}: all rights reserved by {entry['author'] or 'its author'}; "
                            f"not composed into another pack (pass --own if it is yours)")
        if entry["license"] not in LICENSES:
            raise PickError(f"{piece_id}: unknown license {entry['license']!r}")
        plan.append((kind, dirs, entry))

    # Check the destination before touching it: an id already there with other content stops
    # the whole run, since half a composed pack is worse than none.
    for kind, dirs, entry in plan:
        for relative in entry["files"]:
            source = find(dirs, relative)
            target = dest / relative
            if source is not None and target.exists() and target.read_bytes() != source.read_bytes():
                raise PickError(f"{entry['id']}: {relative} already exists in {dest} with different content")

    ensure_mcmeta(dest, name, sources)
    credits = read_json(dest / CREDITS_FILE) if (dest / CREDITS_FILE).is_file() else {}
    if not isinstance(credits, dict):
        credits = {}
    credits.setdefault("pack", {"name": name, "composed": True})
    credits.setdefault("pieces", {})
    written: dict[str, list[str]] = {}
    for kind, dirs, entry in plan:
        files = []
        for relative in entry["files"]:
            files.append(copy_file(dirs, dest, relative, entry["id"]))
        # The name, and the fittings' names if a source pack defines them.
        keys = [f"{KINDS[kind]['lang']}.{entry['namespace']}.{entry['name']}"]
        for fitting in entry.get("fittings", []):
            for relative in fitting_files(dirs, fitting):
                files.append(copy_file(dirs, dest, relative, entry["id"]))
            f_ns, f_name = pack_manifest.split_id(fitting)
            keys += [f"fitting.{f_ns}.{f_name}", f"fitting.{f_ns}.{f_name}.ingredients"]
        lines = lang_lines(dirs, entry["namespace"], keys)
        if lines:
            merge_json(dest / "assets" / entry["namespace"] / "lang" / "en_us.json", lines)
            files.append(f"assets/{entry['namespace']}/lang/en_us.json")
        # Loot: the tags the piece belongs to, with just this member, and the groups that read
        # them. Tags merge across packs, so this adds to a group the mod defines rather than
        # replacing it, and stands alone where the group comes along.
        for tag in entry.get("tags", []):
            add_tag_member(dest / tag, entry["id"])
            files.append(tag)
            for group in loot_groups_using(dirs, tag):
                if not (dest / group).exists():
                    files.append(copy_file(dirs, dest, group, entry["id"]))
        credit = {"author": entry["author"], "license": entry["license"]}
        if entry.get("source"):
            credit["source"] = entry["source"]
        credits["pieces"][entry["id"]] = credit
        written[entry["id"]] = sorted(set(files))
    (dest / CREDITS_FILE).write_text(json.dumps(credits, indent=2, ensure_ascii=False) + "\n",
                                     encoding="utf-8")
    return written


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="+", help="namespaced ids: pieces, skins or cloths")
    ap.add_argument("--from", dest="sources", action="append", required=True, metavar="PACK",
                    help="a source pack folder; repeat for more. A pack whose halves are two "
                         "folders is given as one --from with the folders joined by '+'")
    ap.add_argument("--to", dest="dest", required=True, type=Path, help="the destination pack folder")
    ap.add_argument("--own", action="store_true",
                    help="the pieces are yours: copy all-rights-reserved entries too")
    ap.add_argument("--name", help="the composed pack's name (default: the destination folder's)")
    args = ap.parse_args()

    sources: list[list[Path]] = []
    for spec in args.sources:
        dirs = [Path(p).resolve() for p in spec.split("+")]
        for d in dirs:
            if not d.is_dir():
                sys.exit(f"error: no pack folder at {d}")
        sources.append(dirs)
    try:
        written = pick(sources, args.ids, args.dest, own=args.own, name=args.name)
    except PickError as err:
        sys.exit(f"error: {err}")
    for piece_id, files in written.items():
        print(f"{piece_id}: {len(files)} files")
    print(f"-> {args.dest} ({CREDITS_FILE} written)")


if __name__ == "__main__":
    main()
