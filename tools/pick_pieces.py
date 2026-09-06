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

`--as` duplicates instead of copying: one id is written under another, with every file that
carries the name renamed and every reference inside them - the asset id, the language key, the
recipe's component, the item model's texture - rewritten to match. It is the one verb copying
alone cannot do, and the site's "duplicate a piece" is this.

`--drop` is the reverse: an entry taken out of a pack, with the files that are its alone, its
language line, its tag membership and its credit. Copy then drop is a *move*, and the same three
refusals guard the copy half, so a move that is not allowed leaves both packs as they were.

Usage:
    python tools/pick_pieces.py --from <pack> [--from <pack>...] --to <dest> [--own] [--name N] id...
    python tools/pick_pieces.py --from src/main/resources --to build/mine armorpieces:circlet --own
    python tools/pick_pieces.py --from build/mine --to build/mine --own --as mine:circlet_tall armorpieces:circlet
    python tools/pick_pieces.py --drop --to build/mine mine:circlet_tall
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


def agrees(source: Path, target: Path) -> bool:
    """Whether two files say the same thing. For JSON that means the same data, not the same
    bytes: a pack that has been through sanitize_pack.py is re-indented, and refusing to copy a
    fitting into a pack that already holds the identical fitting would be a refusal about
    whitespace. For anything else it is the bytes."""
    if source.suffix == ".json" and target.suffix == ".json":
        try:
            return read_json(source) == read_json(target)
        except ValueError:
            return False
    return source.read_bytes() == target.read_bytes()


def same_content(a: list[Path], b: list[Path], files: list[str]) -> bool:
    for relative in files:
        left, right = find(a, relative), find(b, relative)
        if left is None or right is None or not agrees(left, right):
            return False
    return True


# ---- duplicating under another id ---------------------------------------------------------------

def rename_map(dirs: list[Path], kind: str, namespace: str, name: str,
               new_namespace: str, new_name: str) -> dict[str, str]:
    """Where each of an entry's files lands when it is written under another id. Every path
    files_of() can produce is answered for; anything else is left where it is, which is what a
    fitting, a loot group and a shared tag want."""
    spec = KINDS[kind]
    out = {
        f"data/{namespace}/{spec['data']}/{name}.json":
            f"data/{new_namespace}/{spec['data']}/{new_name}.json",
        f"data/{namespace}/recipe/{spec['recipe']}{name}.json":
            f"data/{new_namespace}/recipe/{spec['recipe']}{new_name}.json",
    }
    if kind == "piece":
        out[f"assets/{namespace}/armorpieces/decoration/{name}.json"] = (
            f"assets/{new_namespace}/armorpieces/decoration/{new_name}.json")
        # The master sheet and every companion: <name>.png, and <name>_<layer>.png.
        folder = f"assets/{namespace}/textures/entity/decoration"
        for d in dirs:
            here = d / folder
            if not here.is_dir():
                continue
            for path in sorted(here.glob(f"{name}*.png")):
                if path.stem != name and not path.stem.startswith(f"{name}_"):
                    continue
                suffix = path.stem[len(name):]
                out[f"{folder}/{path.name}"] = (f"assets/{new_namespace}/textures/entity/"
                                                f"decoration/{new_name}{suffix}.png")
    else:
        where = "skin" if kind == "skin" else "cloth"
        for sheet in ("humanoid", "humanoid_leggings"):
            out[f"assets/{namespace}/textures/entity/{where}/{name}/{sheet}.png"] = (
                f"assets/{new_namespace}/textures/entity/{where}/{new_name}/{sheet}.png")
        out[f"assets/{namespace}/models/item/{spec['recipe']}{name}.json"] = (
            f"assets/{new_namespace}/models/item/{spec['recipe']}{new_name}.json")
        out[f"assets/{namespace}/textures/item/{spec['recipe']}{name}.png"] = (
            f"assets/{new_namespace}/textures/item/{spec['recipe']}{new_name}.png")
    return out


def reference_map(kind: str, namespace: str, name: str, new_namespace: str, new_name: str) -> dict[str, str]:
    """The strings inside an entry's JSON that name the entry itself: its asset id, its language
    key, and the model and texture its template item points at. Whole values only - a rename is
    a substitution over JSON strings, never over the bytes of a file."""
    spec = KINDS[kind]
    return {
        f"{namespace}:{name}": f"{new_namespace}:{new_name}",
        f"{spec['lang']}.{namespace}.{name}": f"{spec['lang']}.{new_namespace}.{new_name}",
        f"{namespace}:item/{spec['recipe']}{name}": f"{new_namespace}:item/{spec['recipe']}{new_name}",
        f"{namespace}:{spec['recipe']}{name}": f"{new_namespace}:{spec['recipe']}{new_name}",
    }


def rewrite(value, subs: dict[str, str]):
    """A JSON tree with every string that is exactly one of the old names replaced."""
    if isinstance(value, str):
        return subs.get(value, value)
    if isinstance(value, list):
        return [rewrite(v, subs) for v in value]
    if isinstance(value, dict):
        return {rewrite(k, subs): rewrite(v, subs) for k, v in value.items()}
    return value


def copy_renamed(sources: list[Path], dest: Path, relative: str, target_relative: str,
                 subs: dict[str, str], piece_id: str) -> str:
    """One file, under its new name, with its JSON rewritten. A texture is copied as it is."""
    source = find(sources, relative)
    if source is None:
        raise PickError(f"{piece_id}: {relative} is listed but missing")
    target = dest / target_relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if relative.endswith(".json"):
        try:
            body = read_json(source)
        except ValueError as err:
            raise PickError(f"{piece_id}: {relative} is not valid JSON ({err})")
        text = json.dumps(rewrite(body, subs), indent=2, ensure_ascii=False) + "\n"
        if target.exists() and target.read_text(encoding="utf-8") != text:
            raise PickError(f"{piece_id}: {target_relative} already exists in {dest} with different content")
        target.write_text(text, encoding="utf-8")
    else:
        if same_file(source, target):
            return target_relative
        if target.exists() and not agrees(source, target):
            raise PickError(f"{piece_id}: {target_relative} already exists in {dest} with different content")
        shutil.copyfile(source, target)
    return target_relative


def same_file(a: Path, b: Path) -> bool:
    """Whether two paths are the one file. Duplicating inside a pack has the source pack as the
    destination, so most of what is asked for is already exactly where it should be."""
    try:
        return a.resolve() == b.resolve()
    except OSError:
        return False


def copy_file(sources: list[Path], dest: Path, relative: str, piece_id: str) -> str:
    source = find(sources, relative)
    if source is None:
        raise PickError(f"{piece_id}: {relative} is listed but missing")
    target = dest / relative
    if same_file(source, target):
        return relative
    if target.exists() and not agrees(source, target):
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
         name: str | None = None, as_id: str | None = None) -> dict:
    """Copy every id into dest. Returns what was written, per id. Nothing is written until every
    id has been checked, so a refusal leaves the destination as it was.

    With `as_id`, exactly one id is copied and it lands under that name instead of its own:
    every file that carries the name is renamed and every reference inside them is rewritten."""
    dest = Path(dest).resolve()
    name = name or dest.name
    if as_id is not None:
        if len(ids) != 1:
            raise PickError("--as renames one entry; give exactly one id")
        if ":" not in as_id:
            raise PickError(f"--as {as_id}: a namespaced id, like mine:{as_id}")
        new_ns, new_name = pack_manifest.split_id(as_id)
        if not re.fullmatch(r"[a-z0-9_.-]+", new_ns) or not re.fullmatch(r"[a-z0-9_/.-]+", new_name):
            raise PickError(f"--as {as_id}: a resource id is lower-case letters, digits, "
                            f"underscores, dots and hyphens")
        if as_id == ids[0]:
            raise PickError(f"--as {as_id}: that is the id it already has")
    plan = []
    for piece_id in ids:
        kind, dirs, entry = locate(sources, piece_id)
        if entry["license"] == "ARR" and not own:
            raise PickError(f"{piece_id}: all rights reserved by {entry['author'] or 'its author'}; "
                            f"not composed into another pack (pass --own if it is yours)")
        if entry["license"] not in LICENSES:
            raise PickError(f"{piece_id}: unknown license {entry['license']!r}")
        plan.append((kind, dirs, entry))

    if as_id is not None:
        kind, dirs, entry = plan[0]
        # The new id must be free: a duplicate that lands on something is a rename gone wrong.
        for other in pack_manifest.entries([dest], kind) if dest.is_dir() else []:
            if other["id"] == as_id:
                raise PickError(f"--as {as_id}: {dest} already holds a {kind} with that id")
        paths = rename_map(dirs, kind, entry["namespace"], entry["name"], new_ns, new_name)
        subs = reference_map(kind, entry["namespace"], entry["name"], new_ns, new_name)

    # Check the destination before touching it: an id already there with other content stops
    # the whole run, since half a composed pack is worse than none. Under --as the check is
    # against where each file will land, not where it came from.
    for kind, dirs, entry in plan:
        for relative in entry["files"]:
            source = find(dirs, relative)
            if source is None:
                continue
            if as_id is not None:
                # copy_renamed rewrites JSON, so byte equality means nothing for those; it does
                # its own check as it writes, and a texture is compared here as usual.
                target = dest / paths.get(relative, relative)
                if relative.endswith(".json"):
                    continue
            else:
                target = dest / relative
            if target.exists() and not agrees(source, target):
                raise PickError(f"{entry['id']}: {relative} already exists in {dest} with different content")

    ensure_mcmeta(dest, name, sources)
    credits = read_json(dest / CREDITS_FILE) if (dest / CREDITS_FILE).is_file() else {}
    if not isinstance(credits, dict):
        credits = {}
    credits.setdefault("pack", {"name": name, "composed": True})
    credits.setdefault("pieces", {})
    written: dict[str, list[str]] = {}
    for kind, dirs, entry in plan:
        renaming = as_id is not None
        written_id = as_id if renaming else entry["id"]
        out_ns = new_ns if renaming else entry["namespace"]
        files = []
        for relative in entry["files"]:
            if renaming:
                files.append(copy_renamed(dirs, dest, relative, paths.get(relative, relative),
                                          subs, written_id))
            else:
                files.append(copy_file(dirs, dest, relative, entry["id"]))
        # The name, and the fittings' names if a source pack defines them. A fitting keeps its
        # own id: it is a thing of the source pack's, not part of what is being renamed.
        own_key = f"{KINDS[kind]['lang']}.{entry['namespace']}.{entry['name']}"
        keys = [own_key]
        for fitting in entry.get("fittings", []):
            for relative in fitting_files(dirs, fitting):
                files.append(copy_file(dirs, dest, relative, written_id))
            f_ns, f_name = pack_manifest.split_id(fitting)
            keys += [f"fitting.{f_ns}.{f_name}", f"fitting.{f_ns}.{f_name}.ingredients"]
        lines = lang_lines(dirs, entry["namespace"], keys)
        if renaming and own_key in lines:
            lines = {(subs.get(k, k)): v for k, v in lines.items()}
        if lines:
            merge_json(dest / "assets" / out_ns / "lang" / "en_us.json", lines)
            files.append(f"assets/{out_ns}/lang/en_us.json")
        # Loot: the tags the piece belongs to, with just this member, and the groups that read
        # them. Tags merge across packs, so this adds to a group the mod defines rather than
        # replacing it, and stands alone where the group comes along.
        for tag in entry.get("tags", []):
            add_tag_member(dest / tag, written_id)
            files.append(tag)
            for group in loot_groups_using(dirs, tag):
                if not (dest / group).exists():
                    files.append(copy_file(dirs, dest, group, written_id))
        credit = {"author": entry["author"], "license": entry["license"]}
        if entry.get("source"):
            credit["source"] = entry["source"]
        if renaming:
            # A duplicate is derived from the original, and says so.
            credit["source"] = credit.get("source") or entry["id"]
        credits["pieces"][written_id] = credit
        written[written_id] = sorted(set(files))
    (dest / CREDITS_FILE).write_text(json.dumps(credits, indent=2, ensure_ascii=False) + "\n",
                                     encoding="utf-8")
    return written


# ---- taking an entry out again ------------------------------------------------------------------

def remove_tag_member(target: Path, piece_id: str) -> bool:
    """Take an id out of a tag file. The file goes when it holds nothing."""
    if not target.is_file():
        return False
    try:
        body = read_json(target)
    except ValueError:
        return False
    values = body.get("values", [])
    kept = [v for v in values if (v.get("id") if isinstance(v, dict) else v) != piece_id]
    if len(kept) == len(values):
        return False
    if kept:
        body["values"] = kept
        target.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    else:
        target.unlink()
    return True


def prune_empty(root: Path, path: Path) -> None:
    """Walk up from a deleted file, removing the folders it emptied, never past the pack root."""
    root = root.resolve()
    folder = path.parent.resolve()
    while folder != root and root in folder.parents:
        try:
            next(folder.iterdir())
            return
        except StopIteration:
            folder.rmdir()
        except OSError:
            return
        folder = folder.parent


def drop(dest: Path, ids: list[str]) -> dict:
    """Remove entries from a pack: the files that are theirs alone, their language lines, their
    tag membership and their credit. What is shared - a fitting, a loot group, another entry's
    sheet - stays, because something else in the pack still needs it.

    This is the other half of *move*: pick into the destination, then drop from the source."""
    dest = Path(dest).resolve()
    plan = []
    for piece_id in ids:
        kind, dirs, entry = locate([[dest]], piece_id)
        plan.append((kind, entry))
    # What everything else in the pack is made of; nothing in there is deleted.
    dropping = {entry["id"] for _, entry in plan}
    shared: set[str] = set()
    for kind in KINDS:
        for entry in pack_manifest.entries([dest], kind):
            if entry["id"] not in dropping:
                shared.update(entry["files"])

    removed: dict[str, list[str]] = {}
    for kind, entry in plan:
        gone = []
        for relative in entry["files"]:
            if relative in shared:
                continue
            path = dest / relative
            if path.is_file():
                path.unlink()
                prune_empty(dest, path)
                gone.append(relative)
        # The language line, and the file itself once it holds nothing.
        lang_path = dest / "assets" / entry["namespace"] / "lang" / "en_us.json"
        key = f"{KINDS[kind]['lang']}.{entry['namespace']}.{entry['name']}"
        if lang_path.is_file():
            try:
                lang = read_json(lang_path)
            except ValueError:
                lang = None
            if isinstance(lang, dict) and key in lang:
                del lang[key]
                if lang:
                    lang_path.write_text(json.dumps(lang, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                else:
                    lang_path.unlink()
                    prune_empty(dest, lang_path)
                gone.append(lang_path.relative_to(dest).as_posix())
        for tag in entry.get("tags", []):
            if remove_tag_member(dest / tag, entry["id"]):
                gone.append(tag)
        removed[entry["id"]] = sorted(set(gone))

    credits_path = dest / CREDITS_FILE
    if credits_path.is_file():
        try:
            credits = read_json(credits_path)
        except ValueError:
            credits = None
        if isinstance(credits, dict) and isinstance(credits.get("pieces"), dict):
            for piece_id in dropping:
                credits["pieces"].pop(piece_id, None)
            credits_path.write_text(json.dumps(credits, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return removed


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="+", help="namespaced ids: pieces, skins or cloths")
    ap.add_argument("--from", dest="sources", action="append", metavar="PACK",
                    help="a source pack folder; repeat for more. A pack whose halves are two "
                         "folders is given as one --from with the folders joined by '+'. "
                         "Not used with --drop")
    ap.add_argument("--to", dest="dest", required=True, type=Path,
                    help="the destination pack folder, or with --drop the pack to remove from")
    ap.add_argument("--drop", action="store_true",
                    help="remove the ids from --to instead of copying into it: the files that are "
                         "theirs alone, their language lines, their tags and their credit. The "
                         "other half of a move")
    ap.add_argument("--own", action="store_true",
                    help="the pieces are yours: copy all-rights-reserved entries too")
    ap.add_argument("--name", help="the composed pack's name (default: the destination folder's)")
    ap.add_argument("--as", dest="as_id", metavar="NEWID",
                    help="write the one id given under this namespaced id instead: a duplicate, "
                         "with its files renamed and its own references rewritten")
    args = ap.parse_args()

    if args.drop:
        if args.sources:
            ap.error("--drop removes from --to; it has no source")
        if not args.dest.is_dir():
            sys.exit(f"error: no pack folder at {args.dest}")
        try:
            removed = drop(args.dest, args.ids)
        except PickError as err:
            sys.exit(f"error: {err}")
        for piece_id, files in removed.items():
            print(f"{piece_id}: {len(files)} files removed")
        print(f"-> {args.dest}")
        return

    if not args.sources:
        ap.error("--from is required (or --drop to remove from --to)")
    sources: list[list[Path]] = []
    for spec in args.sources:
        dirs = [Path(p).resolve() for p in spec.split("+")]
        for d in dirs:
            if not d.is_dir():
                sys.exit(f"error: no pack folder at {d}")
        sources.append(dirs)
    try:
        written = pick(sources, args.ids, args.dest, own=args.own, name=args.name, as_id=args.as_id)
    except PickError as err:
        sys.exit(f"error: {err}")
    for piece_id, files in written.items():
        print(f"{piece_id}: {len(files)} files")
    print(f"-> {args.dest} ({CREDITS_FILE} written)")


if __name__ == "__main__":
    main()
