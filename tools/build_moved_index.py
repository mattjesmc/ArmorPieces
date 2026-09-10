#!/usr/bin/env python3
"""Build the moved index - the table that lets a tooltip name a pack that is not installed.

`docs/plans/compatibility.md` section 5.1. A save names a piece by id. When that id no longer
resolves the mod keeps the socket, says so on the item, and prints the id - and the one thing it
cannot say by itself is WHICH PACK to go and get, because `former_ids` lives inside the pack that
took the piece and a pack that is not installed declares nothing. With nothing installed
`armorpieces:tusks` is a string in the mod's own namespace and the namespace names nobody.

So the mod ships a table. This writes it.

    assets/armorpieces/compat/moved.json

    {"packs": ["<namespace>", ...],                       every pack the mod ships a NAME for
     "moved": {"<former id>": "<current id>", ...}}       every id that has moved

**It is a label, never a rebind.** Nothing resolves through this file: the registry wins, `former_ids`
and `uid` do the rebinding (compatibility plan section 2.3), and this is consulted only about an id
that has already failed every one of those. A stale row costs a wrong pack NAME in a tooltip, which
is why it is safe to ship a generated table and not safe to ship a generated alias.

**No display names in it.** A row is two ids; the pack's name comes from a lang key on the current
id's namespace - `pack.armorpieces_hunt` -> "The Wild Hunt" - so it translates for free and this
tool never has to know what a pack is called. What the file DOES carry is the list of namespaces
that key exists for, because the mod has no other way to ask: `/armorpieces missing` runs on a
dedicated server, whose `Language` holds vanilla's keys and none of ours, so a lang lookup there
would either name nothing or print a raw key at an operator. The list is read out of the mod's own
`en_us.json`, and `--check` fails if a namespace the index points at is not in it.

**The `packs` list is also what lets an id that never moved name its pack.** `armorpieces_hunt:x`
under a pack that is simply not installed has no row here and needs none - its own namespace is the
answer, and the list is how the mod knows the namespace is one it can name rather than a stranger's.

**The source is the same one `build_legacy_pack.py` reads** - every `former_ids` entry declared by
the mod or by any pack in this repository. There is no hand-written move table and there should
never be one. `packs/legacy` is skipped: it is generated from these same declarations, and its files
carry no `former_ids` by design (the file IS the former id).

Usage:
    python tools/build_moved_index.py            # write the index
    python tools/build_moved_index.py --check    # change nothing; fail if the tree has drifted
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKS = ROOT / "packs"
MOD = ROOT / "src" / "main" / "resources"
INDEX = MOD / "assets" / "armorpieces" / "compat" / "moved.json"
LANG = MOD / "assets" / "armorpieces" / "lang" / "en_us.json"

# Generated, and experiments. `legacy` is built from the very declarations read here.
SKIP_PACKS = {"legacy", "vlm-scratch"}

# The registries whose entries can move. A fitting's type is code and has never moved, so it is not
# rebound and not indexed - see the compatibility plan's fourth as-built decision.
KINDS = ("armor_decoration", "armor_skin", "cloth")


def sources() -> list[tuple[str, Path]]:
    """Every tree that may declare a `former_ids`: the mod, then each pack."""
    found = [("mod", MOD)]
    for pack in sorted(PACKS.iterdir()):
        if pack.is_dir() and pack.name not in SKIP_PACKS:
            found.append((pack.name, pack / "datapack"))
    return [(name, path) for name, path in found if path.is_dir()]


def collect() -> tuple[dict[str, str], list[str]]:
    """The index, and any problem that makes it untrustworthy rather than merely incomplete."""
    moved: dict[str, str] = {}
    claimed_by: dict[str, str] = {}
    problems: list[str] = []
    for source, root in sources():
        for kind in KINDS:
            for file in sorted(root.glob(f"data/*/armorpieces/{kind}/*.json")):
                try:
                    data = json.loads(file.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    problems.append(f"{file.relative_to(ROOT)}: {exc}")
                    continue
                current = data.get("asset_id")
                if not current:
                    continue
                for former in data.get("former_ids") or []:
                    if former in claimed_by and moved[former] != current:
                        # Two pieces claiming one history: the rebind is already ambiguous and
                        # mint_uids.py --check reports it. Do not guess which pack to name.
                        problems.append(
                            f"{former} is claimed by both {moved[former]} ({claimed_by[former]}) "
                            f"and {current} ({source})")
                        continue
                    moved[former] = current
                    claimed_by[former] = source
    return dict(sorted(moved.items())), problems


def named_packs() -> tuple[list[str], list[str]]:
    """Every namespace the mod's own language file has a `pack.<ns>` line for."""
    try:
        lang = json.loads(LANG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], [f"could not read {LANG.relative_to(ROOT)}: {exc}"]
    return sorted(key[len("pack."):] for key in lang if key.startswith("pack.")), []


def unnamed(moved: dict[str, str], packs: list[str]) -> list[str]:
    """Namespaces the index points at that nothing can name - silent in game, so fail here."""
    known = set(packs)
    return [f"{ns} is the target of a moved id but has no lang key pack.{ns} - "
            f"a tooltip would name no pack at all"
            for ns in sorted({current.split(":", 1)[0] for current in moved.values()})
            if ns not in known]


def render(moved: dict[str, str], packs: list[str]) -> str:
    return json.dumps({"packs": packs, "moved": moved}, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="change nothing; fail if the index is not what a fresh build produces")
    args = parser.parse_args()

    moved, problems = collect()
    packs, lang_problems = named_packs()
    problems += lang_problems + unnamed(moved, packs)
    if problems:
        for problem in problems:
            print(f"moved index: {problem}", file=sys.stderr)
        return 1

    fresh = render(moved, packs)
    if args.check:
        current = INDEX.read_text(encoding="utf-8") if INDEX.is_file() else ""
        if current != fresh:
            print(f"moved index: {INDEX.relative_to(ROOT)} is not what a fresh build produces - "
                  f"run python tools/build_moved_index.py", file=sys.stderr)
            return 1
        print(f"moved index: {len(moved)} moved ids, {len(packs)} named packs, as generated")
        return 0

    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(fresh, encoding="utf-8")
    print(f"moved index: {len(moved)} moved ids, {len(packs)} named packs, written to "
          f"{INDEX.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
