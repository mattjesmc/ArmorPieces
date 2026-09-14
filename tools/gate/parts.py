"""
Every shipped part passes the authoring check, or a person has said why it need not.

`tools/check_part.py` is the check the Blockbench plugin runs after every edit and `armorpieces_save`
refuses on: a COPLANAR face on the shell, a face with no paint behind it, paint outside every face, a
static or mask pixel the master does not cover. Until 2026-09-13 nothing ran it at release - the
gate's `painters` check traces every geometry, and `trace_geometry.py` is a REPORT that exits 0
whatever it finds - so the gate was green over five shipped parts the plugin would have refused to
save. A force reason lives only in the session that gave it; nothing on disk carried the decision.

`tools/gate/accepted_parts.json` carries it now, with the goldens' discipline: a problem listed there
is matched on the check's exact wording, and

  * a problem on a shipped part that is NOT listed fails the run - somebody has to look;
  * a listed problem that no longer occurs fails the run too - the art moved under the waiver, and a
    repaint that fixed one hole and opened another should not pass on the old approval.

    python tools/gate/parts.py            # every shipped part, one line each
    python tools/gate/parts.py antlers    # some of them, by name
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent
sys.path.insert(0, str(TOOLS))

import check_part  # noqa: E402
import decoration_paths  # noqa: E402

ACCEPTED = HERE / "accepted_parts.json"


def accepted() -> dict[str, dict]:
    table = json.loads(ACCEPTED.read_text(encoding="utf-8"))
    table.pop("_", None)  # the file's own note to a reader
    return table


def main(names: list[str]) -> int:
    waivers = accepted()
    failures: list[str] = []
    checked = 0
    for geometry in decoration_paths.all_geometry():
        part = geometry.stem
        if names and part not in names:
            continue
        checked += 1
        report = check_part.from_shipped(part, None)
        found = list(report["problems"])
        waived = list(waivers.get(part, {}).get("problems", []))

        unexpected = [p for p in found if p not in waived]
        stale = [p for p in waived if p not in found]
        if not found and not stale:
            print(f"ok     {part}")
            continue
        if not unexpected and not stale:
            print(f"waived {part}: {len(found)} accepted problem(s) - {waivers[part].get('why', '')}")
            continue
        print(f"FAIL   {part}")
        for p in unexpected:
            print(f"  ! {p}")
            failures.append(f"{part}: {p}")
        for p in stale:
            print(f"  ? no longer occurs, retire it from accepted_parts.json: {p}")
            failures.append(f"{part}: stale waiver: {p}")

    for part in waivers:
        if not names and part not in {g.stem for g in decoration_paths.all_geometry()}:
            print(f"FAIL   {part}: waived in accepted_parts.json and no longer ships")
            failures.append(f"{part}: waived and not shipped")

    print(f"\n{checked} part(s) checked, {len(failures)} problem(s) nobody has accepted")
    if failures:
        print("Fix the part, or look at it on the figure and add the check's exact wording to "
              f"{ACCEPTED.relative_to(TOOLS.parent)} with the date.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
