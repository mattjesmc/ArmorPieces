"""
Check that everything with a name has one, in en_us.json.

A missing language line is the quietest defect this mod can ship. Nothing logs it, nothing refuses
to load, and the game draws the key itself - `item.armorpieces.brow_template` in a tooltip, in the
creative tab, in a command's reply - so it survives every other check here and is found by a player.
Four families are checked, and each is derived rather than listed, so a part added tomorrow is
covered without editing this file:

  literals   every `translatable("...")` in the Java. A key ending in `.` is a PREFIX the code
             completes at runtime (`"anchor.armorpieces." + name`), so it is satisfied by any key
             that starts with it; anything else must be there exactly. Keys in another namespace
             (vanilla's `block.minecraft.`, `color.minecraft.`) are vanilla's to supply.
  content    every part, skin, cloth and fitting in the datapack half: `decoration.`, `skin.`,
             `cloth.` and `fitting.` with the file's own id. This family grows with the content.
  anchors    every constant of DecorationAnchor, which is the one list that is not datapack-driven:
             the socket's own name and its `.applies_to` line.
  registry   every item and block the mod registers, under the key the game builds from its id -
             the per-socket templates come from the anchor enum, the rest are literals in
             registry/Mod*.java.

Unused keys are reported as notes, never as failures: a line can be there for a datapack that
nobody in this repository writes, which is the point of a datapack.

Usage:
    python tools/check_lang.py            # the mod's own resources
    python tools/check_lang.py <pack>     # any pack directory holding data/ and assets/
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JAVA = ROOT / "src" / "main" / "java" / "com" / "mattjesmc" / "armorpieces"
RESOURCES = ROOT / "src" / "main" / "resources"
NAMESPACE = "armorpieces"

TRANSLATABLE = re.compile(r'translatable(?:WithFallback)?\(\s*"([^"]+)"')
MOD_ID_PATH = re.compile(r'MOD_ID,\s*"([a-z0-9_/]+)"')
ANCHOR_CONSTANT = re.compile(r'^\s{4}([A-Z_]+)\("([a-z_]+)",', re.MULTILINE)


def lang_keys(pack: Path) -> dict[str, str]:
    path = pack / "assets" / NAMESPACE / "lang" / "en_us.json"
    if not path.exists():
        sys.exit(f"no language file at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def anchors() -> list[str]:
    """The socket names, out of the enum that defines them."""
    source = (JAVA / "decoration" / "DecorationAnchor.java").read_text(encoding="utf-8")
    return [serialized for _constant, serialized in ANCHOR_CONSTANT.findall(source)]


def ids(pack: Path, registry: str) -> list[str]:
    """The ids of one datapack registry, in file order."""
    folder = pack / "data" / NAMESPACE / "armorpieces" / registry
    return sorted(path.stem for path in folder.glob("*.json")) if folder.is_dir() else []


def registered(file: str) -> list[str]:
    """The literal ids a registry class registers, minus the ones built from the anchor enum."""
    source = (JAVA / "registry" / file).read_text(encoding="utf-8")
    return sorted(set(MOD_ID_PATH.findall(source)))


def wanted(pack: Path) -> list[tuple[str, str, bool]]:
    """Every key that has to be there: (key, why, is_prefix)."""
    out: list[tuple[str, str, bool]] = []

    for java in sorted(JAVA.rglob("*.java")):
        for key in TRANSLATABLE.findall(java.read_text(encoding="utf-8")):
            if f".{NAMESPACE}." not in key and not key.startswith(f"{NAMESPACE}."):
                continue  # vanilla's own key, vanilla's to supply
            out.append((key, f"translatable in {java.relative_to(JAVA)}", key.endswith(".")))

    for registry, prefix in (("armor_decoration", "decoration"),
                             ("armor_skin", "skin"),
                             ("cloth", "cloth"),
                             ("fitting", "fitting")):
        for name in ids(pack, registry):
            out.append((f"{prefix}.{NAMESPACE}.{name}", f"{registry}/{name}.json", False))

    for anchor in anchors():
        out.append((f"anchor.{NAMESPACE}.{anchor}", "DecorationAnchor", False))
        out.append((f"anchor.{NAMESPACE}.{anchor}.applies_to", "DecorationAnchor", False))
        out.append((f"item.{NAMESPACE}.{anchor}_template", "the socket's template item", False))

    for name in registered("ModItems.java"):
        out.append((f"item.{NAMESPACE}.{name}", "ModItems", False))
    for name in registered("ModBlocks.java"):
        out.append((f"block.{NAMESPACE}.{name}", "ModBlocks", False))

    return out


def main(argv: list[str]) -> int:
    pack = Path(argv[0]).resolve() if argv else RESOURCES
    have = lang_keys(pack)

    missing: list[tuple[str, str]] = []
    used: set[str] = set()
    seen: set[str] = set()

    for key, why, is_prefix in wanted(pack):
        if (key, is_prefix) in seen:
            continue
        seen.add((key, is_prefix))
        if is_prefix:
            hits = [k for k in have if k.startswith(key)]
            if hits:
                used.update(hits)
            else:
                missing.append((key + "*", why))
        elif key in have:
            used.add(key)
        else:
            missing.append((key, why))

    for key, why in missing:
        print(f"MISSING  {key}   ({why})")

    spare = sorted(set(have) - used)
    if spare:
        print(f"\n{len(spare)} key(s) nothing in this repository asks for, which is not a fault:")
        for key in spare[:12]:
            print(f"  - {key}")
        if len(spare) > 12:
            print(f"  ... and {len(spare) - 12} more")

    if missing:
        print(f"\n{len(missing)} missing language line(s) over {len(have)} key(s)")
        return 1

    print(f"\nevery name has a line: {len(seen)} required, {len(have)} in en_us.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
