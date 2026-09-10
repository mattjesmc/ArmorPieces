#!/usr/bin/env python3
"""Build `packs/legacy` - the restore pack - out of the move table the other packs already carry.

`docs/plans/additive-packs.md` step 3. The mod shrank from 91 pieces to 66 on 2026-09-07: 25 pieces
and 5 skins moved into the Wild Hunt, Coral, the Hive and Legends, and every id they had under
`armorpieces:` stopped resolving. `docs/plans/compatibility.md` made that survivable - nothing a save
names is destroyed any more - but a player on 0.4.0 still sees a plain helmet where their antlers
were. This pack is what puts them back.

**The trick is the namespace.** `packs/legacy` declares `armorpieces` - the mod's own - because a
datapack may define ids in any namespace, so the pack restores `armorpieces:tusks` under exactly the
id 0.3.0 wrote into the save. No Java change, no alias, no rename. It is also why this is the one
pack in the tree whose folder name and namespace differ, and why `check_authoring.py`,
`pack_manifest.py` and `mint_uids.py` were checked against it rather than assumed to cope.

**There is no move table file.** Every piece that moved declares its own history in `former_ids`
(compatibility plan section 2.1), so the 30 pack data files carrying a `former_ids` entry that starts
`armorpieces:` ARE the table, and this reads them. A pack that takes another piece tomorrow is
restored by re-running this, with nothing to keep in step by hand.

What is generated, and wiped on every run:

    data/armorpieces/armorpieces/armor_decoration/<name>.json   the pack's file, ids reversed
    data/armorpieces/armorpieces/armor_skin/<name>.json         the same for a skin
    assets/armorpieces/armorpieces/decoration/<name>.json       geometry, copied
    assets/armorpieces/textures/entity/decoration/<name>*.png   master, static layer, fitting masks
    assets/armorpieces/textures/entity/skin/<name>/*.png        a skin's master pair
    assets/armorpieces/lang/en_us.json                          only the restored lines

What is the pack's own, hand-written, and never touched here:

    data/armorpieces/armorpieces/loot_group/{beast,tidal,carapace}.json   verbatim from 0.3.0
    data/armorpieces/tags/armorpieces/armor_decoration/{beast,tidal,carapace}.json
    pack.mcmeta, LICENSE, armorpieces-credits.json

**Zero template recipes, deliberately.** Every template in this mod is the same ring of paper around
one centre item, so the centre IS the recipe. The Wild Hunt already ships `template_horns` with the
original centre and Legends the five skin templates; shipping them here too would put two shaped
recipes on one grid and make one result silently unobtainable. The pieces are reachable through the
three restored loot groups instead, which is checked below.

The art tracks the packs rather than 0.3.0's bytes: what a save needs back is the ID, and a piece
whose art the Wild Hunt has since redrawn should come back redrawn. That is what "generated so it
cannot go stale" buys.

Usage:
    python tools/build_legacy_pack.py            # write the pack
    python tools/build_legacy_pack.py --check    # change nothing; fail if the tree has drifted
"""

from __future__ import annotations

import argparse
import filecmp
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKS = ROOT / "packs"
LEGACY = PACKS / "legacy"
LOCK = ROOT / "uids.lock"
NAMESPACE = "armorpieces"

# The registries that can move, and the language prefix each one's description key uses.
KINDS = {"armor_decoration": "decoration", "armor_skin": "skin", "cloth": "cloth"}

# Everything below these is this tool's output and is rebuilt from scratch on every run. Anything
# else in the pack is hand-written and survives.
GENERATED = [
    "datapack/data/armorpieces/armorpieces/armor_decoration",
    "datapack/data/armorpieces/armorpieces/armor_skin",
    "datapack/data/armorpieces/armorpieces/cloth",
    "resourcepack/assets/armorpieces/armorpieces/decoration",
    "resourcepack/assets/armorpieces/textures/entity/decoration",
    "resourcepack/assets/armorpieces/textures/entity/skin",
    "resourcepack/assets/armorpieces/lang",
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def move_table() -> list[dict]:
    """Every piece, skin and cloth that left the mod, read off the `former_ids` the packs carry.

    One row per RESTORED id, so a piece claiming two former `armorpieces:` ids yields two - which
    is legal and would be a real restore of both.
    """
    rows: list[dict] = []
    for pack in sorted(p for p in PACKS.iterdir() if p.is_dir()):
        if pack == LEGACY:
            continue
        for kind in KINDS:
            for data in sorted(pack.glob(f"datapack/data/*/armorpieces/{kind}/*.json")):
                body = read_json(data)
                source_ns = data.parents[2].name
                for former in body.get("former_ids", []):
                    if not isinstance(former, str) or not former.startswith(f"{NAMESPACE}:"):
                        continue
                    rows.append({
                        "kind": kind,
                        "name": former.split(":", 1)[1],
                        "from": f"{source_ns}:{data.stem}",
                        "source_ns": source_ns,
                        "source_name": data.stem,
                        "pack": pack,
                        "body": body,
                    })
    rows.sort(key=lambda r: (r["kind"], r["name"]))
    return rows


def known_uid(kind: str, name: str) -> str | None:
    """The uid this restored id already carries, so a rebuild never mints a second one.

    The pack's own uid is NOT reused: the restored piece and the piece that took it over are two
    registry entries that can be installed at once, and `mint_uids.py --check` fails on a doubled
    uid for exactly that reason. `former_ids` is what ties them together, and the restored piece
    deliberately declares none - the pack that took the piece claims that history, and two claims on
    one former id is the collision the same check exists to catch.
    """
    existing = LEGACY / "datapack" / "data" / NAMESPACE / "armorpieces" / kind / f"{name}.json"
    if existing.is_file():
        uid = read_json(existing).get("uid")
        if isinstance(uid, str):
            return uid
    if LOCK.is_file():
        locked = read_json(LOCK).get(f"{kind}/{NAMESPACE}:{name}")
        if isinstance(locked, str):
            return locked
    return None


def restored_body(row: dict) -> dict:
    """The pack's data file with its ids turned back: `armorpieces:<name>`, the mod's language key,
    no `former_ids` (this file IS the former id), and the uid this restored piece already has."""
    kind, name = row["kind"], row["name"]
    out: dict = {"asset_id": f"{NAMESPACE}:{name}",
                 "description": {"translate": f"{KINDS[kind]}.{NAMESPACE}.{name}"}}
    for key, value in row["body"].items():
        if key in ("asset_id", "description", "former_ids", "uid"):
            continue
        out[key] = value
    uid = known_uid(kind, name)
    if uid is not None:
        out["uid"] = uid
    return out


def art_of(row: dict) -> list[tuple[Path, str]]:
    """(source file, path relative to the resource pack root) for everything the piece draws with."""
    ns, name = row["source_ns"], row["source_name"]
    assets = row["pack"] / "resourcepack" / "assets" / ns
    out: list[tuple[Path, str]] = []
    if row["kind"] == "armor_decoration":
        geometry = assets / "armorpieces" / "decoration" / f"{name}.json"
        out.append((geometry, f"assets/{NAMESPACE}/armorpieces/decoration/{row['name']}.json"))
        textures = assets / "textures" / "entity" / "decoration"
        for png in sorted(textures.glob(f"{name}.png")) + sorted(textures.glob(f"{name}_*.png")):
            suffix = png.stem[len(name):]  # "" for the master, "_static" / "_<fitting>" for a layer
            out.append((png, f"assets/{NAMESPACE}/textures/entity/decoration/{row['name']}{suffix}.png"))
    elif row["kind"] == "armor_skin":
        for sheet in ("humanoid", "humanoid_leggings"):
            png = assets / "textures" / "entity" / "skin" / name / f"{sheet}.png"
            out.append((png, f"assets/{NAMESPACE}/textures/entity/skin/{row['name']}/{sheet}.png"))
    elif row["kind"] == "cloth":
        for sheet in ("humanoid", "humanoid_leggings"):
            png = assets / "textures" / "entity" / "cloth" / name / f"{sheet}.png"
            out.append((png, f"assets/{NAMESPACE}/textures/entity/cloth/{row['name']}/{sheet}.png"))
    return out


def language(rows: list[dict]) -> dict[str, str]:
    """The restored names, under the mod's own keys, taken from each source pack's language file.

    Only these lines are shipped, and that is safe because the game MERGES language files across
    packs rather than letting one win: `ClientLanguage.loadFrom` asks the resource manager for the
    whole stack of `lang/en_us.json` under each namespace and puts every file's entries into one
    map, key by key. A partial `assets/armorpieces/lang/en_us.json` therefore adds 30 lines and
    wipes none of the mod's own. (Verified in 26.2's bytecode, 2026-09-08.)
    """
    out: dict[str, str] = {}
    for row in rows:
        prefix = KINDS[row["kind"]]
        source = (row["pack"] / "resourcepack" / "assets" / row["source_ns"] / "lang" / "en_us.json")
        names = read_json(source) if source.is_file() else {}
        key = f"{prefix}.{row['source_ns']}.{row['source_name']}"
        label = names.get(key)
        if label is None:
            print(f"warning: {row['from']}: no language line at {key} in {source}", file=sys.stderr)
            label = row["name"].replace("_", " ").title()
        out[f"{prefix}.{NAMESPACE}.{row['name']}"] = label
    return dict(sorted(out.items()))


def reachable(rows: list[dict], into: Path) -> list[str]:
    """Every restored piece is in one of the pack's own tags, so a loot group can find it.

    The pack ships no template recipes on purpose, so the tags are the only route a restored piece
    has to a survival world. A piece that moved into a pack tomorrow and is restored here without
    being added to a tag would ship unobtainable, and this is the check that says so - the same
    thing `check_authoring.py`'s reach pass would report, said at build time where the fix is.
    """
    tagged: set[str] = set()
    tags = into / "datapack" / "data" / NAMESPACE / "tags" / "armorpieces" / "armor_decoration"
    for tag in sorted(tags.glob("*.json")) if tags.is_dir() else []:
        tagged.update(v for v in read_json(tag).get("values", []) if isinstance(v, str))
    return [f"{NAMESPACE}:{row['name']} is in no tag of this pack - it would ship unobtainable"
            for row in rows
            if row["kind"] == "armor_decoration" and f"{NAMESPACE}:{row['name']}" not in tagged]


def build(rows: list[dict], into: Path) -> int:
    for relative in GENERATED:
        shutil.rmtree(into / relative, ignore_errors=True)

    written = 0
    for row in rows:
        target = (into / "datapack" / "data" / NAMESPACE / "armorpieces" / row["kind"]
                  / f"{row['name']}.json")
        write_json(target, restored_body(row))
        written += 1
        for source, relative in art_of(row):
            if not source.is_file():
                print(f"warning: {row['from']}: no {source.relative_to(ROOT).as_posix()}",
                      file=sys.stderr)
                continue
            destination = into / "resourcepack" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            written += 1

    write_json(into / "resourcepack" / "assets" / NAMESPACE / "lang" / "en_us.json", language(rows))
    return written + 1


def compare(built: Path, live: Path) -> list[str]:
    """Which generated files differ between a fresh build and the tree."""
    problems: list[str] = []
    for relative in GENERATED:
        left, right = built / relative, live / relative
        names = {p.relative_to(left).as_posix() for p in left.rglob("*") if p.is_file()} | \
                {p.relative_to(right).as_posix() for p in right.rglob("*") if p.is_file()} \
                if left.is_dir() or right.is_dir() else set()
        for name in sorted(names):
            a, b = left / name, right / name
            where = f"{relative}/{name}"
            if not b.is_file():
                problems.append(f"missing from the tree: {where}")
            elif not a.is_file():
                problems.append(f"in the tree but not generated: {where}")
            elif not filecmp.cmp(a, b, shallow=False):
                problems.append(f"differs from a fresh build: {where}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="change nothing; fail if the pack in the tree is not what this builds")
    args = parser.parse_args()

    rows = move_table()
    if not rows:
        sys.exit("error: no pack declares a former id in the armorpieces namespace - nothing to "
                 "restore, which is either a moved packs/ or a lost former_ids")

    if not (LEGACY / "datapack" / "pack.mcmeta").is_file():
        sys.exit(f"error: no pack at {LEGACY} - its pack.mcmeta, LICENSE, credits, loot groups and "
                 "tags are hand-written and this only fills in the content")

    problems = reachable(rows, LEGACY)

    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            fresh = Path(tmp) / "legacy"
            for relative in ("datapack/data/armorpieces/tags", "datapack/pack.mcmeta"):
                source = LEGACY / relative
                destination = fresh / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                if source.is_dir():
                    shutil.copytree(source, destination)
                else:
                    shutil.copy2(source, destination)
            build(rows, fresh)
            problems += compare(fresh, LEGACY)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        if problems:
            print(f"legacy pack: {len(problems)} problem(s) - run python tools/build_legacy_pack.py",
                  file=sys.stderr)
            return 1
        print(f"legacy pack: {len(rows)} restored ids, all tagged, all files as generated")
        return 0

    written = build(rows, LEGACY)
    for problem in problems:
        print(f"  {problem}", file=sys.stderr)
    pieces = sum(1 for r in rows if r["kind"] == "armor_decoration")
    skins = sum(1 for r in rows if r["kind"] == "armor_skin")
    print(f"legacy pack: {pieces} pieces, {skins} skins, {written} files written")
    missing = [r for r in rows if known_uid(r["kind"], r["name"]) is None]
    if missing:
        print(f"note: {len(missing)} restored id(s) have no uid yet - run python tools/mint_uids.py")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
