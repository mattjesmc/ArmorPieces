"""
Check that the authoring round trip is clean for every shipped part.

The Blockbench plugin writes three kinds of file back on Save, and each is checked here against
the claim that opening a part and saving it unchanged changes nothing:

  geometry   bb_geo's round trip - geo -> bbmodel -> geo loses nothing and the writer is stable -
             over every assets/<ns>/armorpieces/decoration/<part>.json
  data       every data/<ns>/armorpieces/armor_decoration/<part>.json re-serialises to its own
             bytes with the plugin's formatting (two-space JSON, trailing newline), so the Part
             dialog's write-back reproduces the file rather than reformatting it
  fittings   every fitting a part lists resolves to a definition the plugin can offer, with a type
             it knows how to show

Usage:
    python tools/check_authoring.py            # the mod's own resources
    python tools/check_authoring.py <pack>     # any pack directory holding data/ and assets/
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bb_geo  # noqa: E402
import effect_schema  # noqa: E402
import preview_material  # noqa: E402

GATE = "armorpieces:if_fitting"


def _effect_editable(effect, schema) -> bool:
    """Whether the plugin's Part dialog can show this effect as a row rather than read-only."""
    if not isinstance(effect, dict):
        return False
    if effect.get("type") == GATE:
        condition = effect.get("if", {})
        if set(condition) - {"fitting", "material", "dye"} or not isinstance(condition.get("fitting"), str):
            return False
        if not isinstance(condition.get("material", ""), str) or not isinstance(condition.get("dye", ""), str):
            return False
        effect = effect.get("then", {})
        if not isinstance(effect, dict) or effect.get("type") == GATE:
            return False
    definition = schema.get(effect.get("type"))
    return bool(definition) and set(effect) - {"type"} <= {f["name"] for f in definition["fields"]}

ROOT = Path(__file__).resolve().parent.parent
RESOURCES = ROOT / "src" / "main" / "resources"


def check_pack(pack: Path) -> list[str]:
    failures: list[str] = []
    data_files = sorted(pack.glob("data/*/armorpieces/armor_decoration/*.json"))
    geometry_files = sorted(pack.glob("assets/*/armorpieces/decoration/*.json"))
    if not data_files and not geometry_files:
        return [f"{pack}: no parts found"]

    for geometry in geometry_files:
        if not bb_geo.roundtrip(geometry):
            failures.append(f"geometry {geometry.name}: round trip is not clean")

    schema = effect_schema.schema()
    for data in data_files:
        text = data.read_text(encoding="utf8")
        parsed = json.loads(text)
        if json.dumps(parsed, indent=2) + "\n" != text:
            failures.append(f"data {data.name}: would be reformatted by a save")
        for fitting in preview_material.list_fittings(data, pack):
            if fitting["type"] is None:
                failures.append(f"data {data.name}: fitting {fitting['id']} has no definition")
        for effect in parsed.get("effects", []):
            if not _effect_editable(effect, schema):
                failures.append(f"data {data.name}: effect {effect.get('type') if isinstance(effect, dict) else effect}"
                                " would show read-only in the editor")
        print(f"data {data.name}: ok")
    return failures


def main() -> None:
    pack = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else RESOURCES
    failures = check_pack(pack)
    print()
    if failures:
        print("\n".join(failures))
        sys.exit(1)
    print("authoring round trip clean")


if __name__ == "__main__":
    main()
