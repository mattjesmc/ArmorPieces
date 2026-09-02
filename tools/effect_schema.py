"""
What the built-in effect types take, read out of the Java that defines them.

The Blockbench plugin offers an effect as a row of fields, and the fields, their ranges, their
defaults and what they mean all live in one place already: the `MapCodec` of each record under
decoration/effect/builtin/, and the javadoc beside it. Copying that table into another language
would be a second source of truth that drifts the first time a default is tuned - the same reason
bb_rig.py parses the anchor enum rather than restating it - so this file parses the records
instead. It reads exactly the shapes those records use: `RecordCodecBuilder.mapCodec(i -> i.group(
<codec>.fieldOf("name").forGetter(...), <codec>.optionalFieldOf("name", <default>).forGetter(...)
).apply(...))`, and the `@param` lines of the class javadoc for the descriptions.

Each field is reduced to a kind an editor can build a control for:

    bool                 a checkbox
    int, number          a number, with `min` and `max` when the codec bounds them
    enum                 a select over `options`
    id                   a text field; `registry` says which ids it takes, for autocomplete
    tag                  a text field for `#namespace:name`; `registry` says which tags
    fitting_predicate    the `if` of if_fitting - the plugin builds its own control for this
    effect               a nested effect - the `then` of if_fitting
    unknown              a codec this parser does not recognise; the plugin shows it read-only

Usage:
    python tools/effect_schema.py            # the schema as JSON
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EFFECTS = ROOT / "src" / "main" / "java" / "com" / "mattjesmc" / "armorpieces" / "decoration" / "effect"
BUILTIN = EFFECTS / "builtin"
REGISTRY = EFFECTS / "DecorationEffects.java"

# Vanilla's AttributeModifier.Operation, as its codec spells it. A vanilla enum, so it is the one
# thing here that is restated rather than parsed.
OPERATIONS = ["add_value", "add_multiplied_base", "add_multiplied_total"]

# Named constants a default may be spelled as, and what they are in JSON.
CONSTANTS = {
    "AttributeModifier.Operation.ADD_VALUE": "add_value",
    "AttributeModifier.Operation.ADD_MULTIPLIED_BASE": "add_multiplied_base",
    "AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL": "add_multiplied_total",
    "DamageTypeTags.IS_PROJECTILE": "#minecraft:is_projectile",
}


def _registered() -> dict[str, str]:
    """Effect type id -> record class, from the register() calls in DecorationEffects."""
    text = REGISTRY.read_text(encoding="utf8")
    out = {}
    for path, cls in re.findall(r'register\("(\w+)",\s*(\w+)\.CODEC\)', text):
        out[f"armorpieces:{path}"] = cls
    return out


def _snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def _params(javadoc: str) -> dict[str, str]:
    """`@param field text`, continuation lines included, keyed by the JSON field name."""
    lines = [re.sub(r"^\s*\*\s?", "", line) for line in javadoc.splitlines()]
    out, current = {}, None
    for line in lines:
        m = re.match(r"@param\s+(\w+)\s*(.*)", line)
        if m:
            current = _snake(m.group(1))
            out[current] = m.group(2).strip()
        elif current and line.strip() and not line.startswith("@"):
            out[current] += " " + line.strip()
        else:
            current = None
    return {k: re.sub(r"\{@code ([^}]*)\}", r"\1", v) for k, v in out.items()}


def _summary(javadoc: str) -> str:
    """The first sentence of the class javadoc after the `{@code id} - ` it opens with."""
    text = " ".join(re.sub(r"^\s*\*\s?", "", line) for line in javadoc.splitlines())
    text = re.sub(r"\{@code [^}]*\}\s*-\s*", "", text, count=1).strip()
    text = re.sub(r"\{@(?:code|link) ([^}]*)\}", r"\1", text)
    return text.split(". ")[0].rstrip(".") + "."


def _literal(value: str):
    value = value.strip()
    if value in CONSTANTS:
        return CONSTANTS[value]
    if value in ("true", "false"):
        return value == "true"
    m = re.fullmatch(r"-?\d+(\.\d+)?[FfDd]?", value)
    if m:
        number = float(value.rstrip("FfDd"))
        return int(number) if number.is_integer() and "." not in value else number
    return None


def _kind(codec: str) -> dict:
    """A codec expression, reduced to a control."""
    codec = codec.strip()
    m = re.search(r"(?:intRange)\(\s*(-?\d+),\s*(-?\d+)\s*\)", codec)
    if m:
        return {"kind": "int", "min": int(m.group(1)), "max": int(m.group(2))}
    m = re.search(r"(?:floatRange|doubleRange)\(\s*(-?[\d.]+)[FfDd]?,\s*(-?[\d.]+)[FfDd]?\s*\)", codec)
    if m:
        return {"kind": "number", "min": float(m.group(1)), "max": float(m.group(2))}
    if "NON_NEGATIVE_INT" in codec:
        return {"kind": "int", "min": 0}
    if "POSITIVE_INT" in codec:
        return {"kind": "int", "min": 1}
    if codec.endswith("Codec.INT"):
        return {"kind": "int"}
    if codec.endswith(("Codec.FLOAT", "Codec.DOUBLE")):
        return {"kind": "number"}
    if codec.endswith("Codec.BOOL"):
        return {"kind": "bool"}
    if codec.endswith("Identifier.CODEC"):
        return {"kind": "id", "registry": None}
    m = re.search(r"BuiltInRegistries\.(\w+)\.holderByNameCodec\(\)", codec)
    if m:
        return {"kind": "id", "registry": m.group(1).lower()}
    m = re.search(r"TagKey\.codec\(Registries\.(\w+)\)", codec)
    if m:
        return {"kind": "tag", "registry": m.group(1).lower()}
    if "AttributeModifier.Operation.CODEC" in codec:
        return {"kind": "enum", "options": OPERATIONS}
    if "FittingPredicate.CODEC" in codec:
        return {"kind": "fitting_predicate"}
    if "DecorationEffect.CODEC" in codec:
        return {"kind": "effect"}
    return {"kind": "unknown", "codec": codec}


def _fields(source: str) -> list[dict]:
    """The group(...) entries of the record's CODEC, one field each, in codec order."""
    m = re.search(r"i\.group\((.*?)\)\s*\.apply\(", source, re.DOTALL)
    if not m:
        return []
    body = re.sub(r"\s+", " ", m.group(1))
    fields = []
    for chunk in body.split(".forGetter(")[:-1]:
        # Everything after the previous forGetter's closing paren and comma is the next codec.
        chunk = re.sub(r"^[^,]*\),\s*", "", chunk) if fields else chunk
        entry = re.fullmatch(
            r"\s*(?P<codec>.+?)\.(?P<opt>optionalFieldOf|fieldOf)\(\"(?P<name>\w+)\"(?:,\s*(?P<default>.+))?\)\s*",
            chunk)
        if not entry:
            continue
        field = {"name": entry.group("name"), "required": entry.group("opt") == "fieldOf"}
        field.update(_kind(entry.group("codec")))
        if entry.group("default") is not None:
            field["default"] = _literal(entry.group("default"))
        fields.append(field)
    return fields


def schema() -> dict:
    out = {}
    for type_id, cls in _registered().items():
        path = BUILTIN / f"{cls}.java"
        if not path.is_file():
            continue
        source = path.read_text(encoding="utf8")
        doc = re.search(r"/\*\*(.*?)\*/\s*public record", source, re.DOTALL)
        javadoc = doc.group(1) if doc else ""
        params = _params(javadoc)
        fields = _fields(source)
        for field in fields:
            field["description"] = params.get(field["name"], "")
        out[type_id] = {
            "class": cls,
            "label": type_id.split(":")[1].replace("_", " ").title(),
            "summary": _summary(javadoc) if javadoc else "",
            "fields": fields,
        }
    return out


def main() -> None:
    result = schema()
    if not result:
        sys.exit(f"error: parsed no effect types out of {REGISTRY}; the shape must have changed")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
