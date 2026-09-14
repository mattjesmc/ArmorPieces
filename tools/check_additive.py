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

The other half of the rule is the FLOOR. Removing content is a setting, never a pack
(`parts.disabled` in the server config), and a pack that only adds still has to say which mod it
adds to: every pack half's pack.mcmeta carries `"armorpieces": {"requires": "<mod version>"}` - a
section the game ignores and the library, the editor and pack_manifest.py read to say which mod a
pack needs (`docs/plans/additive-packs.md`, "Versioned packs in the library"). Since 0.4.0 the floor
is 0.4.0 for everything this repository ships (backwards support stops below it), so a half that
says nothing, says something older, or disagrees with its other half is reported here.

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

# The lowest mod version any pack here may claim to run on. Not the current mod version: a pack
# that needs nothing newer than 0.4.0 should keep saying 0.4.0 when the mod is at 0.5.0.
FLOOR = "0.4.0"

# Scratch, never shipped, never checked for a floor.
UNSHIPPED = {"vlm-scratch"}


def version_key(version: str) -> tuple[int, ...] | None:
    parts = version.strip().split(".")
    if not parts or not all(part.isdigit() for part in parts):
        return None
    return tuple(int(part) for part in parts)


def floors() -> list[dict]:
    """Every pack half whose pack.mcmeta does not say, correctly, which mod it needs."""
    problems: list[dict] = []
    for name, roots in sources():
        if name == "the mod" or name in UNSHIPPED:
            continue
        said: dict[str, str] = {}
        for root in roots:
            mcmeta = root / "pack.mcmeta"
            half = root.relative_to(ROOT).as_posix()
            if not mcmeta.is_file():
                problems.append({"pack": name, "half": half, "problem": "no pack.mcmeta"})
                continue
            try:
                requires = json.loads(mcmeta.read_text(encoding="utf-8")).get("armorpieces", {}).get("requires")
            except (ValueError, AttributeError):
                problems.append({"pack": name, "half": half, "problem": "pack.mcmeta is not readable"})
                continue
            if not isinstance(requires, str) or version_key(requires) is None:
                problems.append({"pack": name, "half": half,
                                 "problem": 'pack.mcmeta has no "armorpieces": {"requires": "x.y.z"} section'})
                continue
            if version_key(requires) < version_key(FLOOR):
                problems.append({"pack": name, "half": half,
                                 "problem": f"requires {requires}, below the {FLOOR} floor"})
            said[half] = requires
        if len(set(said.values())) > 1:
            problems.append({"pack": name, "half": ", ".join(said),
                             "problem": "the two halves disagree: " + ", ".join(f"{h} says {v}" for h, v in said.items())})
    return problems


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
    unfloored = floors()
    if args.json:
        print(json.dumps({"collisions": collisions, "counts": counts, "floors": unfloored}, indent=2))
        return 1 if collisions or unfloored else 0

    for name, count in counts.items():
        print(f"{name}: {count} definitions")
    for hit in collisions:
        print(f"\nCOLLISION {hit['what']}\n"
              f"  {hit['first']}: {hit['first_file']}\n"
              f"  {hit['second']}: {hit['second_file']}", file=sys.stderr)
    for miss in unfloored:
        print(f"\nFLOOR {miss['pack']} ({miss['half']}): {miss['problem']}", file=sys.stderr)
    if collisions:
        print(f"\n{len(collisions)} collision(s): a pack may only define what nothing else defines",
              file=sys.stderr)
    if unfloored:
        print(f"\n{len(unfloored)} pack half/halves without a correct floor: every pack.mcmeta says "
              f'"armorpieces": {{"requires": "{FLOOR}"}} or later', file=sys.stderr)
    if collisions or unfloored:
        return 1
    print(f"\nadditive: {sum(counts.values())} definitions across {len(counts)} sources, none twice; "
          f"every pack declares the mod it needs ({FLOOR} or later)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
