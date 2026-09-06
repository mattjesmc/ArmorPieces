"""
Check that the effect schema the Blockbench plugin reads still describes the Java it is parsed from.

`effect_schema.py` builds the Part dialog's effect controls by PARSING the built-in effect records -
their `MapCodec` and their javadoc - rather than restating them, which is what keeps the editor from
becoming a second source of truth. The cost of that choice is that the parser is coupled to the
shape of the Java: rename a codec helper, wrap a field, add a type, and the parser does not crash -
it silently produces a schema with a type missing or a field it cannot classify, and the dialog
quietly stops offering it. The plugin's own reply looks exactly the same either way.

So three things are asserted here, and they are the three ways that goes wrong:

  types      every type `DecorationEffects.register` puts in the registry has an entry, and no
             entry describes a type that is not registered
  fields     no field came out `unknown`, which is the parser saying it did not recognise a codec
  shape      the schema is JSON, every entry has a label and a summary, and every field has a name
             and a kind

An empty field description is a note, not a fault: a field whose meaning is in its name has nothing
to say, and the javadoc `@param` line is optional by design.

Usage:
    python tools/check_effect_schema.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
EFFECTS = ROOT / "src" / "main" / "java" / "com" / "mattjesmc" / "armorpieces" / "decoration" / "effect"

REGISTER = re.compile(r'^\s*register\("([a-z_]+)",', re.MULTILINE)


def registered() -> list[str]:
    """The effect type ids, out of the class that registers them."""
    source = (EFFECTS / "DecorationEffects.java").read_text(encoding="utf-8")
    return [f"armorpieces:{path}" for path in REGISTER.findall(source)]


def schema() -> dict:
    done = subprocess.run([sys.executable, str(TOOLS / "effect_schema.py")],
                          capture_output=True, text=True, cwd=ROOT)
    if done.returncode != 0:
        sys.exit(f"effect_schema.py failed:\n{done.stderr.strip() or done.stdout.strip()}")
    try:
        return json.loads(done.stdout)
    except json.JSONDecodeError as exc:
        sys.exit(f"effect_schema.py did not print JSON: {exc}")


def main() -> int:
    have = schema()
    want = registered()
    problems: list[str] = []
    notes: list[str] = []

    for type_id in want:
        if type_id not in have:
            problems.append(f"{type_id} is registered in DecorationEffects and not in the schema - "
                            f"the parser did not recognise its record")
    for type_id in have:
        if type_id not in want:
            problems.append(f"{type_id} is in the schema and not registered - a type was removed "
                            f"from DecorationEffects and its record left behind")

    for type_id, entry in sorted(have.items()):
        if not entry.get("label"):
            problems.append(f"{type_id}: no label")
        if not entry.get("summary"):
            problems.append(f"{type_id}: no summary - the class javadoc's first sentence is missing")
        for field in entry.get("fields", []):
            name = field.get("name")
            kind = field.get("kind")
            if not name or not kind:
                problems.append(f"{type_id}: a field with no {'name' if not name else 'kind'}")
                continue
            if kind == "unknown":
                problems.append(f"{type_id}.{name}: kind 'unknown' - the parser met a codec it does "
                                f"not know, and the dialog shows the field read-only")
            if not field.get("description"):
                notes.append(f"{type_id}.{name}: no @param line")

    for problem in problems:
        print(f"!  {problem}")
    for note in notes:
        print(f"-  {note}")

    if problems:
        print(f"\n{len(problems)} problem(s) over {len(have)} effect type(s)")
        return 1

    fields = sum(len(entry.get("fields", [])) for entry in have.values())
    print(f"\nschema describes every registered effect: {len(have)} type(s), {fields} field(s), "
          f"none unknown")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
