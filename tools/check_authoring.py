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
  loot       every row of a part's `loot` list is in the shape the Part dialog writes - table,
             weight, chance, in that order and of those types - so a save reproduces it
  recipes    every data/<ns>/recipe/template_<part>.json in the plugin's shape - the ring pattern,
             switched on or off with `armorpieces:disabled` - re-serialises to its own bytes from
             the two items and the switch the panel reads out of it, so a save reproduces the file
             and a disabled recipe keeps what it was

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


def _loot_row_ok(row) -> bool:
    """Whether the Part dialog's Loot group would write this row back as it is: the three keys in
    the plugin's order, a namespaced table id, a positive integer weight and a chance in 0..1."""
    if not isinstance(row, dict) or list(row) != ["table", "weight", "chance"]:
        return False
    table, weight, chance = row["table"], row["weight"], row["chance"]
    return (isinstance(table, str) and ":" in table
            and isinstance(weight, int) and not isinstance(weight, bool) and weight > 0
            and isinstance(chance, (int, float)) and not isinstance(chance, bool) and 0 <= chance <= 1)


ROOT = Path(__file__).resolve().parent.parent
RESOURCES = ROOT / "src" / "main" / "resources"

# The plugin's recipe shape: one centre item in a ring of four, and the type it writes when the
# Craftable switch is off. Mirrors RING_PATTERN and DISABLED_TYPE in the plugin.
RING_PATTERN = [" # ", "#F#", " # "]
DISABLED_TYPE = "armorpieces:disabled"


def _ingredient_id(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("item"), str):
        return value["item"]
    return ""


def _recipe_rewrite(recipe: dict, namespace: str, part: str, anchor: str) -> dict | None:
    """What the plugin's Save would write for this recipe file, or None if it would leave it alone.

    Mirrors readRecipe + writeRecipe: a file not in the ring shape is somebody's hand-made recipe
    and is never touched; a ring-shaped one - switched on or off - is rewritten from its two items
    and the switch, over whatever else the file holds.
    """
    craftable = recipe.get("type") != DISABLED_TYPE
    if craftable and recipe.get("type") != "minecraft:crafting_shaped":
        return None
    if recipe.get("pattern") != RING_PATTERN:
        return None
    key = recipe.get("key") or {}
    focus, ring = _ingredient_id(key.get("F")), _ingredient_id(key.get("#"))
    if not focus or not ring:
        return None
    out = dict(recipe)
    out.update({
        "type": "minecraft:crafting_shaped" if craftable else DISABLED_TYPE,
        "pattern": RING_PATTERN,
        "key": {"#": ring, "F": focus},
        "result": {
            "id": f"armorpieces:{anchor}_template",
            "components": {"armorpieces:decoration": f"{namespace}:{part}"},
        },
    })
    out.setdefault("category", "equipment")
    return out


def check_recipes(pack: Path, data_files: list[Path]) -> list[str]:
    failures: list[str] = []
    for data in data_files:
        namespace, part = data.parents[2].name, data.stem
        recipe_file = pack / "data" / namespace / "recipe" / f"template_{part}.json"
        if not recipe_file.exists():
            continue
        text = recipe_file.read_text(encoding="utf8")
        try:
            recipe = json.loads(text)
        except ValueError:
            failures.append(f"recipe {recipe_file.name}: not valid JSON")
            continue
        anchors = json.loads(data.read_text(encoding="utf8")).get("anchors") or [""]
        rewrite = _recipe_rewrite(recipe, namespace, part, anchors[0])
        if rewrite is None:
            print(f"recipe {recipe_file.name}: hand-made, left alone")
            continue
        if json.dumps(rewrite, indent=2) + "\n" != text:
            failures.append(f"recipe {recipe_file.name}: would be rewritten by a save")
        state = "off" if recipe.get("type") == DISABLED_TYPE else "on"
        print(f"recipe {recipe_file.name}: ok ({state})")
    return failures


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
        for index, row in enumerate(parsed.get("loot", [])):
            if not _loot_row_ok(row):
                failures.append(f"data {data.name}: loot row {index} would be rewritten by a save")
        print(f"data {data.name}: ok")
    failures.extend(check_recipes(pack, data_files))
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
