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
  grids      no two shaped recipes in the pack share a crafting grid: every template is the same
             ring of paper, so two parts given one centre item is one unobtainable part, silently
  skins      every data/<ns>/armorpieces/armor_skin/<skin>.json re-serialises to its own bytes,
             its loot rows are in the part's own three-key shape, and both of its master sheets are
             actually in the resource pack - a skin with no art draws as plain armor and says nothing
  cloths     every data/<ns>/armorpieces/cloth/<cloth>.json re-serialises to its own bytes, names
             a sheet that exists, ships at least one cut mask, and has a template recipe of the
             usual shape - a cloth with no art at all is a garment that draws nothing
  skin art   the select in assets/<ns>/items/skin_template.json and the skin_template_<skin>.png
             beside it name each other: a case with no texture draws the chequer, a texture with no
             case is art nothing can show, and a pack's own skin correctly has neither
  recipes    every data/<ns>/recipe/template_<part>.json in the plugin's shape - the ring pattern,
             switched on or off with `armorpieces:disabled` - re-serialises to its own bytes from
             the two items and the switch the panel reads out of it, so a save reproduces the file
             and a disabled recipe keeps what it was

Usage:
    python tools/check_authoring.py                       # the mod's own resources
    python tools/check_authoring.py <pack>                # any pack directory holding data/ and assets/
    python tools/check_authoring.py <datapack> <respack>  # a piece split over two folders
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


def check_fitting_recipes(pack: Path) -> list[str]:
    """Every fitting's template recipe, `recipe/fitting_template_<fitting>.json`, in the shape the
    New Fitting dialog writes: the ring, the bare fitting template as the result, and the fitting
    as its `armorpieces:fitting` component. Hand-made ones are left alone like a part's."""
    failures: list[str] = []
    for recipe_file in sorted(pack.glob("data/*/recipe/fitting_template_*.json")):
        namespace = recipe_file.parents[1].name
        fitting = recipe_file.stem[len("fitting_template_"):]
        text = recipe_file.read_text(encoding="utf8")
        try:
            recipe = json.loads(text)
        except ValueError:
            failures.append(f"recipe {recipe_file.name}: not valid JSON")
            continue
        if recipe.get("type") != "minecraft:crafting_shaped" or recipe.get("pattern") != RING_PATTERN:
            print(f"recipe {recipe_file.name}: hand-made, left alone")
            continue
        key = recipe.get("key") or {}
        focus, ring = _ingredient_id(key.get("F")), _ingredient_id(key.get("#"))
        if not focus or not ring:
            print(f"recipe {recipe_file.name}: hand-made, left alone")
            continue
        rewrite = dict(recipe)
        rewrite.update({
            "type": "minecraft:crafting_shaped",
            "category": "equipment",
            "pattern": RING_PATTERN,
            "key": {"#": ring, "F": focus},
            "result": {
                "id": "armorpieces:fitting_template",
                "components": {"armorpieces:fitting": f"{namespace}:{fitting}"},
            },
        })
        if json.dumps(rewrite, indent=2) + "\n" != text:
            failures.append(f"recipe {recipe_file.name}: would be rewritten by a save")
            continue
        if not (pack / "data" / namespace / "armorpieces" / "fitting" / f"{fitting}.json").exists():
            failures.append(f"recipe {recipe_file.name}: no fitting {namespace}:{fitting} in this pack")
            continue
        print(f"recipe {recipe_file.name}: ok")
    return failures


def check_skins(pack: Path, assets: Path) -> list[str]:
    """Every skin: its data file, its two sheets, and its template recipe.

    A skin is the third template family and it round-trips like the other two - the data file
    re-serialises to its own bytes, its loot rows are in the same three-key shape a part's are, and
    `recipe/skin_template_<skin>.json` is the same ring of paper with the skin on the result's
    `armorpieces:skin` component. What is checked here and nowhere else is that the ART EXISTS: a
    skin whose master pair is missing is a skin the game silently draws as plain armor, because the
    bake has nothing to colour and vanilla's own texture stands.
    """
    failures: list[str] = []
    for data in sorted(pack.glob("data/*/armorpieces/armor_skin/*.json")):
        namespace, skin = data.parents[2].name, data.stem
        text = data.read_text(encoding="utf8")
        parsed = json.loads(text)
        if json.dumps(parsed, indent=2) + "\n" != text:
            failures.append(f"skin {data.name}: would be reformatted by a save")
        for index, row in enumerate(parsed.get("loot", [])):
            if not _loot_row_ok(row):
                failures.append(f"skin {data.name}: loot row {index} would be rewritten by a save")
        asset = parsed.get("asset_id") or ""
        if ":" not in asset:
            failures.append(f"skin {data.name}: asset_id {asset!r} is not a namespaced id")
            continue
        asset_ns, asset_path = asset.split(":", 1)
        for sheet in ("humanoid", "humanoid_leggings"):
            png = assets / "assets" / asset_ns / "textures" / "entity" / "skin" / asset_path / f"{sheet}.png"
            if not png.exists():
                failures.append(f"skin {data.name}: no {sheet}.png at {png} - it would draw as plain armor")
        print(f"skin {data.name}: ok")

        recipe_file = pack / "data" / namespace / "recipe" / f"skin_template_{skin}.json"
        if not recipe_file.exists():
            continue
        recipe_text = recipe_file.read_text(encoding="utf8")
        try:
            recipe = json.loads(recipe_text)
        except ValueError:
            failures.append(f"recipe {recipe_file.name}: not valid JSON")
            continue
        craftable = recipe.get("type") != DISABLED_TYPE
        key = recipe.get("key") or {}
        focus, ring = _ingredient_id(key.get("F")), _ingredient_id(key.get("#"))
        if (craftable and recipe.get("type") != "minecraft:crafting_shaped")                 or recipe.get("pattern") != RING_PATTERN or not focus or not ring:
            print(f"recipe {recipe_file.name}: hand-made, left alone")
            continue
        rewrite = dict(recipe)
        rewrite.update({
            "type": "minecraft:crafting_shaped" if craftable else DISABLED_TYPE,
            "pattern": RING_PATTERN,
            "key": {"#": ring, "F": focus},
            "result": {
                "id": "armorpieces:skin_template",
                "components": {"armorpieces:skin": f"{namespace}:{skin}"},
            },
        })
        rewrite.setdefault("category", "equipment")
        if json.dumps(rewrite, indent=2) + "\n" != recipe_text:
            failures.append(f"recipe {recipe_file.name}: would be rewritten by a save")
            continue
        print(f"recipe {recipe_file.name}: ok ({'off' if not craftable else 'on'})")
    return failures


def _shaped_signature(recipe: dict):
    """What the crafting grid sees of a shaped recipe: the pattern and the ingredient under each
    key. Two recipes with the same signature are one recipe to the game - it hands out whichever
    it finds first and the other is silently unobtainable."""
    if recipe.get("type") != "minecraft:crafting_shaped":
        return None
    pattern = recipe.get("pattern")
    key = recipe.get("key")
    if not isinstance(pattern, list) or not isinstance(key, dict):
        return None
    return (tuple(pattern), tuple(sorted((k, json.dumps(v, sort_keys=True)) for k, v in key.items())))


def check_recipe_collisions(pack: Path) -> list[str]:
    """Every shaped recipe in the pack has a grid no other shaped recipe in the pack has. Every
    template recipe here is the same ring of paper, so the centre item is the whole recipe, and two
    parts given the same centre is exactly the mistake nothing else reports."""
    seen: dict = {}
    failures: list[str] = []
    for recipe_file in sorted(pack.glob("data/*/recipe/*.json")):
        try:
            signature = _shaped_signature(json.loads(recipe_file.read_text(encoding="utf8")))
        except ValueError:
            continue
        if signature is None:
            continue
        if signature in seen:
            failures.append(f"recipe {recipe_file.name}: same crafting grid as {seen[signature]} - "
                            "one of the two can never be crafted")
        else:
            seen[signature] = recipe_file.name
    return failures


def check_skin_icons(assets: Path) -> list[str]:
    """The skin templates' item art: a select case, its model and its texture have to agree.

    One item carries every skin, so `items/skin_template.json` picks its look off the
    `armorpieces:skin` component - and a skin shipped by a pack has no case of its own and falls
    back to the generic icon, which is correct and is the whole point of the fallback. What is not
    correct is half of a pair: a case whose model or texture is missing draws the missing-texture
    chequer in a hotbar, and a texture no case points at is art nothing can ever show. Both are
    silent in game, which is why they are checked here.
    """
    failures: list[str] = []
    for select in sorted(assets.glob("assets/*/items/skin_template.json")):
        namespace = select.parents[1].name
        model = json.loads(select.read_text(encoding="utf8")).get("model") or {}
        cased = {case.get("when") for case in model.get("cases", [])}
        drawn = {f"{namespace}:{png.stem[len('skin_template_'):]}"
                 for png in (assets / "assets" / namespace / "textures" / "item").glob("skin_template_*.png")}
        for skin in sorted(cased - drawn):
            failures.append(f"skin icon {skin}: a select case with no texture - it would draw as "
                            "the missing-texture chequer")
        for skin in sorted(drawn - cased):
            failures.append(f"skin icon {skin}: a texture no select case names - nothing can show it")
        for case in model.get("cases", []):
            named = ((case.get("model") or {}).get("model") or "").split(":")[-1]
            if named and not (assets / "assets" / namespace / "models" / f"{named}.json").exists():
                failures.append(f"skin icon {case.get('when')}: no model at {named}.json")
        fallback = ((model.get("fallback") or {}).get("model") or "").split(":")[-1]
        if fallback and not (assets / "assets" / namespace / "models" / f"{fallback}.json").exists():
            failures.append(f"skin icon fallback: no model at {fallback}.json - a pack's own skin "
                            "would draw as the missing-texture chequer")
        print(f"skin icons {namespace}: ok ({len(cased)} cases)")
    return failures


def check_cloths(pack: Path, assets: Path) -> list[str]:
    """Every cloth: its data file, its cut masks, and its template recipe.

    A cloth is the fourth template family and round-trips like the other three. What differs from a
    skin, and is the whole reason this is not the same function, is that its two masks are OPTIONAL
    ONE AT A TIME: a tabard that stops at the waist ships no leggings mask, and that absence is how
    it stops. What cannot be absent is BOTH - a cloth with no art at all is a garment the game puts
    on a piece of armor and then draws nothing for, which is silent in game and so is caught here.
    """
    failures: list[str] = []
    for data in sorted(pack.glob("data/*/armorpieces/cloth/*.json")):
        namespace, cloth = data.parents[2].name, data.stem
        text = data.read_text(encoding="utf8")
        parsed = json.loads(text)
        if json.dumps(parsed, indent=2) + "\n" != text:
            failures.append(f"cloth {data.name}: would be reformatted by a save")
        for index, row in enumerate(parsed.get("loot", [])):
            if not _loot_row_ok(row):
                failures.append(f"cloth {data.name}: loot row {index} would be rewritten by a save")
        sheet = parsed.get("sheet", "shield")
        if sheet not in ("banner", "shield"):
            failures.append(f"cloth {data.name}: sheet {sheet!r} is neither banner nor shield")
        asset = parsed.get("asset_id") or ""
        if ":" not in asset:
            failures.append(f"cloth {data.name}: asset_id {asset!r} is not a namespaced id")
            continue
        asset_ns, asset_path = asset.split(":", 1)
        masks = [name for name in ("humanoid", "humanoid_leggings")
                 if (assets / "assets" / asset_ns / "textures" / "entity" / "cloth" / asset_path
                     / f"{name}.png").exists()]
        if not masks:
            failures.append(f"cloth {data.name}: no cut mask at all under textures/entity/cloth/"
                            f"{asset_path}/ - it would draw nothing")
            continue
        print(f"cloth {data.name}: ok ({', '.join(masks)})")

        recipe_file = pack / "data" / namespace / "recipe" / f"cloth_template_{cloth}.json"
        if not recipe_file.exists():
            continue
        recipe_text = recipe_file.read_text(encoding="utf8")
        try:
            recipe = json.loads(recipe_text)
        except ValueError:
            failures.append(f"recipe {recipe_file.name}: not valid JSON")
            continue
        craftable = recipe.get("type") != DISABLED_TYPE
        key = recipe.get("key") or {}
        focus, ring = _ingredient_id(key.get("F")), _ingredient_id(key.get("#"))
        if (craftable and recipe.get("type") != "minecraft:crafting_shaped") \
                or recipe.get("pattern") != RING_PATTERN or not focus or not ring:
            print(f"recipe {recipe_file.name}: hand-made, left alone")
            continue
        rewrite = dict(recipe)
        rewrite.update({
            "type": "minecraft:crafting_shaped" if craftable else DISABLED_TYPE,
            "pattern": RING_PATTERN,
            "key": {"#": ring, "F": focus},
            "result": {
                "id": "armorpieces:cloth_template",
                # The garment and nothing else: the colour and the layers arrive off the banner at
                # the smithing table, and a template that named them would be a template for one
                # design rather than for a garment.
                "components": {"armorpieces:cloth": {"cloth": f"{namespace}:{cloth}"}},
            },
        })
        rewrite.setdefault("category", "equipment")
        if json.dumps(rewrite, indent=2) + "\n" != recipe_text:
            failures.append(f"recipe {recipe_file.name}: would be rewritten by a save")
            continue
        print(f"recipe {recipe_file.name}: ok ({'off' if not craftable else 'on'})")
    return failures


def check_cloth_icons(assets: Path) -> list[str]:
    """The cloth templates' item art, on the same terms as the skins'.

    The one difference is the shape of a case: a cloth template's component is an object rather than
    a bare id, because the value carries a colour and pattern layers as well as the garment, so the
    `when` is `{"cloth": "<ns>:<name>"}` and the garment has to be read out of it.
    """
    failures: list[str] = []
    for select in sorted(assets.glob("assets/*/items/cloth_template.json")):
        namespace = select.parents[1].name
        model = json.loads(select.read_text(encoding="utf8")).get("model") or {}
        cased = {(case.get("when") or {}).get("cloth") for case in model.get("cases", [])}
        drawn = {f"{namespace}:{png.stem[len('cloth_template_'):]}"
                 for png in (assets / "assets" / namespace / "textures" / "item").glob("cloth_template_*.png")}
        for cloth in sorted(c for c in cased - drawn if c):
            failures.append(f"cloth icon {cloth}: a select case with no texture - it would draw as "
                            "the missing-texture chequer")
        for cloth in sorted(drawn - cased):
            failures.append(f"cloth icon {cloth}: a texture no select case names - nothing can show it")
        for case in model.get("cases", []):
            named = ((case.get("model") or {}).get("model") or "").split(":")[-1]
            if named and not (assets / "assets" / namespace / "models" / f"{named}.json").exists():
                failures.append(f"cloth icon {case.get('when')}: no model at {named}.json")
        # The fallback is the model a PACK's own cloth lands on - the one case the mod's own content
        # never exercises, and so the one that goes missing without anyone noticing.
        fallback = ((model.get("fallback") or {}).get("model") or "").split(":")[-1]
        if fallback and not (assets / "assets" / namespace / "models" / f"{fallback}.json").exists():
            failures.append(f"cloth icon fallback: no model at {fallback}.json - a pack's own cloth "
                            "would draw as the missing-texture chequer")
        print(f"cloth icons {namespace}: ok ({len(cased)} cases)")
    return failures


def check_pack(pack: Path, assets: Path | None = None) -> list[str]:
    """`pack` holds the datapack half; `assets`, when given, the resource pack half - the two
    folders a player's own content sits in. One folder for both is the usual case here."""
    assets = assets or pack
    failures: list[str] = []
    data_files = sorted(pack.glob("data/*/armorpieces/armor_decoration/*.json"))
    geometry_files = sorted(assets.glob("assets/*/armorpieces/decoration/*.json"))
    skin_files = sorted(pack.glob("data/*/armorpieces/armor_skin/*.json"))
    cloth_files = sorted(pack.glob("data/*/armorpieces/cloth/*.json"))
    if not data_files and not geometry_files and not skin_files and not cloth_files:
        return [f"{pack}: no parts, skins or cloths found"]

    for geometry in geometry_files:
        if not bb_geo.roundtrip(geometry):
            failures.append(f"geometry {geometry.name}: round trip is not clean")

    schema = effect_schema.schema()
    for data in data_files:
        text = data.read_text(encoding="utf8")
        parsed = json.loads(text)
        if json.dumps(parsed, indent=2) + "\n" != text:
            failures.append(f"data {data.name}: would be reformatted by a save")
        for fitting in preview_material.list_fittings(data, [pack, assets]):
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
    failures.extend(check_skins(pack, assets))
    failures.extend(check_skin_icons(assets))
    failures.extend(check_cloths(pack, assets))
    failures.extend(check_cloth_icons(assets))
    failures.extend(check_recipes(pack, data_files))
    failures.extend(check_fitting_recipes(pack))
    failures.extend(check_recipe_collisions(pack))
    return failures


def main() -> None:
    pack = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else RESOURCES
    assets = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None
    failures = check_pack(pack, assets)
    print()
    if failures:
        print("\n".join(failures))
        sys.exit(1)
    print("authoring round trip clean")


if __name__ == "__main__":
    main()
