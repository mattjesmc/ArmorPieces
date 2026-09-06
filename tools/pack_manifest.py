"""
What is in a pack, as JSON: every piece, skin and cloth with its socket, fittings, license and
author, and the files each one is made of.

The gallery is built from this, the composer picks by it, and pick_pieces.py copies the file
sets it lists - so the one place that knows which files make up a piece is here. A pack is one
folder holding data/ and assets/, or two folders holding one half each; name them all.

The license comes from `armorpieces-credits.json` at a pack's root, a file the game ignores:

    {
      "pack": { "author": "somebody", "license": "CC-BY-4.0", "homepage": "https://..." },
      "pieces": {
        "somebody:great_helm": { "license": "CC-BY-SA-4.0" },
        "somebody:tabard_lion": { "author": "someone else", "license": "CC0-1.0", "source": "..." }
      }
    }

A per-piece entry overrides the pack's default; a pack without the file is all rights reserved
(`ARR`) by its author, which is what copyright law says anyway. The license is one of LICENSES.

Usage:
    python tools/pack_manifest.py <pack dir> [<pack dir> ...]        # JSON on stdout
    python tools/pack_manifest.py <pack dir> --brief                  # one line per entry
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CREDITS_FILE = "armorpieces-credits.json"

# The licenses a piece may carry. `compose` says whether the site may copy it into another pack.
LICENSES = {
    "CC0-1.0": {"name": "CC0 1.0", "compose": True},
    "CC-BY-4.0": {"name": "CC BY 4.0", "compose": True},
    "CC-BY-SA-4.0": {"name": "CC BY-SA 4.0", "compose": True},
    "CC-BY-NC-4.0": {"name": "CC BY-NC 4.0", "compose": True},
    "CC-BY-NC-SA-4.0": {"name": "CC BY-NC-SA 4.0", "compose": True},
    "ARR": {"name": "All rights reserved", "compose": False},
}
DEFAULT_LICENSE = "ARR"

# Where each kind of entry keeps its halves. `data` is the registry folder under data/<ns>/,
# `lang` the language key prefix, `recipe` the template recipe's file name prefix.
KINDS = {
    "piece": {"data": "armorpieces/armor_decoration", "lang": "decoration", "recipe": "template_",
              "tag": "armorpieces/armor_decoration"},
    "skin": {"data": "armorpieces/armor_skin", "lang": "skin", "recipe": "skin_template_", "tag": None},
    "cloth": {"data": "armorpieces/cloth", "lang": "cloth", "recipe": "cloth_template_", "tag": None},
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def find(dirs: list[Path], relative: str) -> Path | None:
    """The first pack folder that holds this relative path."""
    for d in dirs:
        candidate = d / relative
        if candidate.exists():
            return candidate
    return None


def credits_of(dirs: list[Path]) -> dict:
    """The credits file, from whichever half carries it; both halves' entries merged if both do."""
    out: dict = {"pack": {}, "pieces": {}}
    for d in dirs:
        path = d / CREDITS_FILE
        if not path.is_file():
            continue
        try:
            data = read_json(path)
        except ValueError as err:
            print(f"warning: {path} is not valid JSON ({err}); ignored", file=sys.stderr)
            continue
        if isinstance(data.get("pack"), dict):
            out["pack"] = {**out["pack"], **data["pack"]}
        if isinstance(data.get("pieces"), dict):
            for key, value in data["pieces"].items():
                if isinstance(value, dict):
                    out["pieces"][key] = {**out["pieces"].get(key, {}), **value}
    return out


def resolve_credit(credits: dict, piece_id: str) -> dict:
    """author, license, source for one id: the piece's own entry over the pack's default."""
    pack = credits.get("pack", {})
    own = credits.get("pieces", {}).get(piece_id, {})
    license_id = str(own.get("license") or pack.get("license") or DEFAULT_LICENSE)
    if license_id not in LICENSES:
        print(f"warning: {piece_id}: unknown license {license_id!r}, treated as {DEFAULT_LICENSE}",
              file=sys.stderr)
        license_id = DEFAULT_LICENSE
    out = {"license": license_id, "author": str(own.get("author") or pack.get("author") or "")}
    if own.get("source"):
        out["source"] = str(own["source"])
    return out


def lang_of(dirs: list[Path], namespace: str) -> dict:
    out: dict = {}
    for d in dirs:
        path = d / "assets" / namespace / "lang" / "en_us.json"
        if path.is_file():
            try:
                out = {**read_json(path), **out}
            except ValueError:
                pass
    return out


def split_id(value: str) -> tuple[str, str]:
    namespace, _, name = value.rpartition(":")
    return (namespace or "minecraft"), name


def title(name: str) -> str:
    return name.replace("_", " ").title()


# ---- the file set of one entry -----------------------------------------------------------------

def files_of(dirs: list[Path], kind: str, namespace: str, name: str) -> list[str]:
    """Every file that is this entry's, as paths relative to a pack root, in the order they are
    found. Existence is checked against the given folders; a file that no folder holds is left
    out, so a piece with no recipe lists none."""
    spec = KINDS[kind]
    candidates = [
        f"data/{namespace}/{spec['data']}/{name}.json",
        f"data/{namespace}/recipe/{spec['recipe']}{name}.json",
    ]
    if kind == "piece":
        candidates.append(f"assets/{namespace}/armorpieces/decoration/{name}.json")
        candidates.append(f"assets/{namespace}/textures/entity/decoration/{name}.png")
        # The companion sheets: the static layer and one mask per fitting.
        for d in dirs:
            folder = d / "assets" / namespace / "textures" / "entity" / "decoration"
            if folder.is_dir():
                for path in sorted(folder.glob(f"{name}_*.png")):
                    candidates.append(f"assets/{namespace}/textures/entity/decoration/{path.name}")
    elif kind == "skin":
        for sheet in ("humanoid", "humanoid_leggings"):
            candidates.append(f"assets/{namespace}/textures/entity/skin/{name}/{sheet}.png")
        candidates.append(f"assets/{namespace}/models/item/skin_template_{name}.json")
        candidates.append(f"assets/{namespace}/textures/item/skin_template_{name}.png")
    elif kind == "cloth":
        for sheet in ("humanoid", "humanoid_leggings"):
            candidates.append(f"assets/{namespace}/textures/entity/cloth/{name}/{sheet}.png")
        candidates.append(f"assets/{namespace}/models/item/cloth_template_{name}.json")
        candidates.append(f"assets/{namespace}/textures/item/cloth_template_{name}.png")
    out, seen = [], set()
    for relative in candidates:
        if relative in seen:
            continue
        seen.add(relative)
        if find(dirs, relative) is not None:
            out.append(relative)
    return out


def tag_memberships(dirs: list[Path], kind: str, piece_id: str) -> list[str]:
    """The armor_decoration tag files (relative paths) that list this id, which is how a piece
    belongs to a loot group."""
    tag_dir = KINDS[kind]["tag"]
    if not tag_dir:
        return []
    out = []
    for d in dirs:
        data = d / "data"
        if not data.is_dir():
            continue
        for path in sorted(data.glob(f"*/tags/{tag_dir}/*.json")):
            try:
                values = read_json(path).get("values", [])
            except ValueError:
                continue
            ids = [v.get("id") if isinstance(v, dict) else v for v in values]
            if piece_id in ids:
                out.append(path.relative_to(d).as_posix())
    return sorted(set(out))


def loot_group_skins(dirs: list[Path]) -> set[str]:
    """Skins named directly by a loot group, which is how a skin is found in the world."""
    out: set[str] = set()
    for d in dirs:
        data = d / "data"
        if not data.is_dir():
            continue
        for path in data.glob("*/armorpieces/loot_group/*.json"):
            try:
                for skin in read_json(path).get("skins", []) or []:
                    if isinstance(skin, str):
                        out.add(skin)
            except ValueError:
                continue
    return out


def entries(dirs: list[Path], kind: str) -> list[dict]:
    spec = KINDS[kind]
    credits = credits_of(dirs)
    found_skins = loot_group_skins(dirs) if kind == "skin" else set()
    out, seen = [], set()
    for d in dirs:
        data = d / "data"
        if not data.is_dir():
            continue
        for path in sorted(data.glob(f"*/{spec['data']}/*.json")):
            namespace = path.relative_to(data).parts[0]
            name = path.stem
            piece_id = f"{namespace}:{name}"
            if piece_id in seen:
                continue
            seen.add(piece_id)
            try:
                body = read_json(path)
            except ValueError as err:
                print(f"warning: {path}: {err}; skipped", file=sys.stderr)
                continue
            if not isinstance(body, dict):
                continue
            lang = lang_of(dirs, namespace)
            key = f"{spec['lang']}.{namespace}.{name}"
            desc = body.get("description")
            if isinstance(desc, dict) and isinstance(desc.get("translate"), str):
                key = desc["translate"]
            label = lang.get(key) if isinstance(desc, dict) else (desc if isinstance(desc, str) else None)
            files = files_of(dirs, kind, namespace, name)
            tags = tag_memberships(dirs, kind, piece_id)
            entry = {
                "id": piece_id,
                "kind": kind,
                "namespace": namespace,
                "name": name,
                "label": label or title(name),
                "files": files,
                "craftable": any(f"/recipe/{spec['recipe']}{name}.json" in f for f in files),
                "loot": bool(body.get("loot")) or bool(tags) or piece_id in found_skins,
                "tags": tags,
                **resolve_credit(credits, piece_id),
            }
            if kind == "piece":
                anchors = body.get("anchors") or []
                entry["anchors"] = [a for a in anchors if isinstance(a, str)]
                entry["anchor"] = entry["anchors"][0] if entry["anchors"] else None
                entry["fittings"] = [f for f in (body.get("fittings") or []) if isinstance(f, str)]
                entry["effects"] = len(body.get("effects") or [])
            if kind == "cloth":
                entry["sheet"] = body.get("sheet")
            out.append(entry)
    return out


def pack_meta(dirs: list[Path]) -> dict:
    credits = credits_of(dirs)
    meta = {"name": dirs[0].name, "description": "", "author": credits["pack"].get("author", ""),
            "license": credits["pack"].get("license", DEFAULT_LICENSE),
            "homepage": credits["pack"].get("homepage", ""), "dirs": [str(d) for d in dirs],
            "namespaces": [], "format": {}}
    if meta["license"] not in LICENSES:
        meta["license"] = DEFAULT_LICENSE
    for d in dirs:
        mcmeta = d / "pack.mcmeta"
        if mcmeta.is_file():
            try:
                pack = read_json(mcmeta).get("pack", {})
                desc = pack.get("description", "")
                if isinstance(desc, dict):
                    desc = desc.get("text", "") or desc.get("translate", "")
                meta["description"] = meta["description"] or str(desc)
                for key in ("pack_format", "min_format", "max_format"):
                    if key in pack:
                        meta["format"][key] = pack[key]
            except ValueError:
                pass
        for half in ("data", "assets"):
            folder = d / half
            if folder.is_dir():
                for ns in sorted(p.name for p in folder.iterdir() if p.is_dir()):
                    if ns not in meta["namespaces"] and ns != "minecraft":
                        meta["namespaces"].append(ns)
    return meta


def manifest(dirs: list[Path]) -> dict:
    dirs = [Path(d).resolve() for d in dirs]
    pieces = entries(dirs, "piece")
    skins = entries(dirs, "skin")
    cloths = entries(dirs, "cloth")
    return {
        "pack": pack_meta(dirs),
        "pieces": pieces,
        "skins": skins,
        "cloths": cloths,
        "counts": {"pieces": len(pieces), "skins": len(skins), "cloths": len(cloths)},
    }


def brief(m: dict) -> str:
    lines = [f"{m['pack']['name']}: {m['counts']['pieces']} pieces, {m['counts']['skins']} skins, "
             f"{m['counts']['cloths']} cloths; pack license {m['pack']['license']}"]
    for entry in m["pieces"] + m["skins"] + m["cloths"]:
        where = f" on {entry['anchor']}" if entry.get("anchor") else ""
        how = ", ".join(w for w, on in (("crafted", entry["craftable"]), ("found", entry["loot"])) if on) or "pack's own"
        lines.append(f"  {entry['kind']:5s} {entry['id']:32s} {entry['label']:24s}{where:12s} "
                     f"{entry['license']:14s} {how}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dirs", nargs="+", type=Path, help="the pack folder(s): one, or its two halves")
    ap.add_argument("--brief", action="store_true", help="one line per entry instead of JSON")
    args = ap.parse_args()
    for d in args.dirs:
        if not d.is_dir():
            sys.exit(f"error: no pack folder at {d}")
    m = manifest(args.dirs)
    print(brief(m) if args.brief else json.dumps(m, indent=1))


if __name__ == "__main__":
    main()
