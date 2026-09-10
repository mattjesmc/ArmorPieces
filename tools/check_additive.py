#!/usr/bin/env python3
"""Every pack is additive: a pack may only define ids that nothing else defines.

`docs/plans/additive-packs.md`, "The principle". It is the rule that makes a library of packs safe
to browse and mix - a pack that only ADDS cannot break another pack, so nothing a player installs
can silently change what they already have. Two things break it, and they look identical on disk:

  * a pack that ships a SNAPSHOT of the mod rather than the part that left it. The library's 0.3.0
    `armorpieces` entry is exactly this, and installing it over 0.4.0 would freeze all 107 ids at
    0.3.0's data and art for precisely the players most likely to install it.
  * two packs that happen to choose one name. The second one loaded wins, quietly, and a save that
    says `somebody:great_helm` now means a different helmet than it did.

What is checked is the PRIMARY id - the path a file defines. A former id claimed twice is the same
collision seen from the other side, and `tools/mint_uids.py --check` already reports it; this does
not repeat that.

The restore pack is not an exception and does not need to be. `packs/legacy` defines
`armorpieces:tusks` under the mod's own namespace, which is legal because the mod stopped defining
it in 0.4.0 - the pack is additive against the version it is built for. That is also the shape of
the guard: if a future mod version brought a piece back, this would fail, which is precisely when
somebody needs to be told.

What is deliberately NOT a collision:

    tags       the game MERGES tag files across packs rather than letting one win, so two packs
               adding to `#armorpieces:knightly` is the intended way to join a loot group.
    lang       merged the same way, key by key (ClientLanguage.loadFrom).
    pack.mcmeta, LICENSE, armorpieces-credits.json, armorpieces-sets.json
               a pack's own paperwork, one copy per pack half, never loaded as content.

Usage:
    python tools/check_additive.py            # the mod and every pack under packs/
    python tools/check_additive.py --json     # the same, as JSON
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOD = ROOT / "src" / "main" / "resources"
PACKS = ROOT / "packs"

# Paperwork, not content: it lives at a pack's root and the game never loads it.
PAPERWORK = {"pack.mcmeta", "armorpieces-credits.json", "armorpieces-sets.json", "LICENSE"}


def sources() -> list[tuple[str, list[Path]]]:
    """(name, roots) for the mod and every pack, each pack's halves listed together."""
    out: list[tuple[str, list[Path]]] = [("the mod", [MOD])]
    if PACKS.is_dir():
        for pack in sorted(p for p in PACKS.iterdir() if p.is_dir()):
            halves = [pack / half for half in ("datapack", "resourcepack") if (pack / half).is_dir()]
            out.append((pack.name, halves or [pack]))
    return out


def defined(roots: list[Path]) -> dict[str, str]:
    """What one source defines: {what it is: the file that says so}.

    A key is the thing the game would end up with - a registry id, a recipe id, an asset path - so
    that two sources producing the same key really are two answers to one question.
    """
    out: dict[str, str] = {}
    for root in roots:
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(root)
            parts = relative.parts
            if relative.name in PAPERWORK or parts[0] not in ("data", "assets"):
                continue
            if len(parts) < 3:
                continue
            namespace = parts[1]
            rest = parts[2:]
            if rest[0] == "tags" or (rest[0] == "lang"):
                continue  # merged by the game, not overridden
            if parts[0] == "data" and rest[0] == "armorpieces" and len(rest) == 3:
                key = f"{rest[1]} {namespace}:{rest[2].removesuffix('.json')}"
            elif parts[0] == "data" and rest[0] == "recipe":
                key = f"recipe {namespace}:{'/'.join(rest[1:]).removesuffix('.json')}"
            elif parts[0] == "data":
                key = f"data {namespace}:{'/'.join(rest)}"
            else:
                key = f"asset {namespace}:{'/'.join(rest)}"
            out[key] = (root / relative).relative_to(ROOT).as_posix()
    return out


def run() -> tuple[list[dict], dict]:
    owners: dict[str, tuple[str, str]] = {}
    collisions: list[dict] = []
    counts: dict[str, int] = {}
    for name, roots in sources():
        mine = defined(roots)
        counts[name] = len(mine)
        for key, file in sorted(mine.items()):
            if key in owners:
                first_name, first_file = owners[key]
                collisions.append({"what": key, "first": first_name, "first_file": first_file,
                                   "second": name, "second_file": file})
            else:
                owners[key] = (name, file)
    return collisions, counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="the result as JSON on stdout")
    args = parser.parse_args()

    collisions, counts = run()
    if args.json:
        print(json.dumps({"collisions": collisions, "counts": counts}, indent=2))
        return 1 if collisions else 0

    for name, count in counts.items():
        print(f"{name}: {count} definitions")
    for hit in collisions:
        print(f"\nCOLLISION {hit['what']}\n"
              f"  {hit['first']}: {hit['first_file']}\n"
              f"  {hit['second']}: {hit['second_file']}", file=sys.stderr)
    if collisions:
        print(f"\n{len(collisions)} collision(s): a pack may only define what nothing else defines",
              file=sys.stderr)
        return 1
    print(f"\nadditive: {sum(counts.values())} definitions across {len(counts)} sources, none twice")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
