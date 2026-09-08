"""The check over whatever piece is ACTIVE in Blockbench, for `.mcptoolkit/loop.json`.

The mcp-toolkit loop file (LOOP_KIT_DESIGN.md section 5.2) runs a command after every editing
call and appends its last stdout line, which must be JSON `{text, problems, notes, full}`. Our
checkers already print exactly that with `--json --brief`, but they take a piece DIRECTORY, and
which directory is the active piece's is something only the Armor Pieces plugin knows: it writes
`<tmp>/armorpieces-bb/status/current.json` naming the active project's uuid, and under that uuid a
`meta.json` whose `kind` says whether this is a part or a skin. tools/mcp/server.mjs did this
lookup inline; this is the same lookup as a one-file command, so the loop file can name it.

Usage:  python tools/check_active.py --json --brief [--no-layout] [--previous FILE]

With nothing open it falls back to `MCPTK_UNIT`, the brief's file stem, which mcp-toolkit's
tools/loop/run-unit.ps1 exports from 0.124.0 on: an authoring session closes its tab as its last
act, so the runner's after-the-fact check has no active piece to address and has to name the unit
instead.

Two lines of the report are a DIFF against the last check, not a property of the piece, and they
are the reason this script keeps state:

  - THE SHEET LAYOUT of the cubes whose net moved or appeared since the last check, one line per
    cube with each face's rectangle. A reply that added or resized a cube then says where to paint,
    which is the whole of "put in the reply the numbers the agent would otherwise spend turns
    researching" (LOOP_KIT_DESIGN.md section 2). Without it every cube costs an extra
    armorpieces_check. `--no-layout` suppresses the block for a caller that prints the whole
    report anyway.
  - THE GREW DIFF: a face that was fully painted and is no longer, because a resize grew it and
    paint only moves. The per-face coverage test cannot see this on its own - the face is painted,
    just not to its new edge - so it is a diff or it is nothing (section 3).

Both were `layoutLines()` in tools/mcp/server.mjs, which held the previous report in memory.

THE HISTORY IS THE PIECE'S, NOT THE CALLER'S, and that is the whole reason this script owns it
rather than taking the loop's `--previous`. Two servers edit one piece in a kit session: Blockbench
through the mcp-toolkit shim (which runs this from `.mcptoolkit/loop.json`) and the nine
armorpieces_* tools through tools/mcp/server.mjs. Give each its own previous report and a cube
painted through the proxy and then GROWN through the shim compares against a state where it was
never painted - the regrow goes unreported, which is exactly the finding the diff exists to make.
So the last report is written beside the piece's own status directory and every caller reads the
same one. `--previous` is still accepted, because the loop passes it for a stateful check, and
ignored.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATUS = Path(tempfile.gettempdir()) / "armorpieces-bb" / "status"


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def fail(text: str) -> int:
    # Not a report: the loop treats a non-JSON last line as "could not run" and says so LOUDLY on
    # the reply, which is the right reading of "no piece is open".
    print(text)
    return 2


def net_key(item: dict) -> str:
    return "%s|%s" % (",".join(map(str, item.get("uv") or [])), "x".join(map(str, item.get("size") or [])))


def layout_lines(report: dict, previous: dict | None) -> list[str]:
    """The proxy's layoutLines(), against the previous report instead of module state."""
    layout = report.get("layout") or []
    if not layout:
        return []
    was_net = {i["cube"]: net_key(i) for i in (previous or {}).get("layout") or []}
    was_full = {
        "%s.%s" % (i["cube"], face): got == area
        for i in (previous or {}).get("layout") or []
        for face, (got, area) in (i.get("coverage") or {}).items()
    }
    changed = [i for i in layout if was_net.get(i["cube"]) != net_key(i)]
    grew = [
        "%s.%s %d/%d" % (i["cube"], face, got, area)
        for i in layout
        for face, (got, area) in (i.get("coverage") or {}).items()
        if was_full.get("%s.%s" % (i["cube"], face)) and got < area
    ]
    lines: list[str] = []
    if changed:
        which = "every cube" if len(changed) == len(layout) else "the cubes that moved"
        lines.append("  sheet layout (face x,y w x h): " + which)
        for i in changed:
            faces = "  ".join(
                "%s %d,%d %dx%d" % (f, r[0], r[1], r[2], r[3]) for f, r in (i.get("faces") or {}).items()
            )
            lines.append("    %s uv %s %s: %s" % (
                i["cube"], ",".join(map(str, i.get("uv") or [])), "x".join(map(str, i.get("size") or [])), faces,
            ))
    if grew:
        lines.append("  ! repaint: faces that were complete and grew: " + ", ".join(grew))
    return lines


def main(argv: list[str]) -> int:
    args: list[str] = []
    want_layout = True
    skip = False
    for a in argv:
        if skip:
            skip = False
            continue
        if a == "--previous":  # the loop's stateful hand-back; the history here is the piece's
            skip = True
            continue
        if a == "--no-layout":
            want_layout = False
            continue
        args.append(a)
    unit = (os.environ.get("MCPTK_UNIT") or "").strip()
    if unit and not re.fullmatch(r"[a-z0-9_]+", unit):
        return fail("MCPTK_UNIT %r is not a piece id (lowercase, digits, underscores)" % unit)

    current = read_json(STATUS / "current.json")
    meta = None
    piece_dir = None
    if current and current.get("uuid"):
        piece_dir = STATUS / current["uuid"]
        meta = read_json(piece_dir / "meta.json")
        if not meta:
            return fail("no meta.json for the active piece under " + str(piece_dir))

    # THE UNIT WINS OVER THE TAB. The active piece is whatever Blockbench happens to hold, and it is
    # only this session's piece while this session is the only one driving the editor. It is not,
    # twice over: run-unit.ps1 runs the loop's checks again AFTER the session, by which time the tab
    # is closed or someone else's; and a second session can take the tab mid-run (2026-09-06, the
    # helm_wings rework - `armorpieces_open` returned helm_wings and the next reply reported
    # `bedroll`, and the runner then attributed bedroll's stray mask pixels to that session). So when
    # MCPTK_UNIT names a unit and the tab does not hold it, check the unit and SAY the tab was
    # someone else's - never silently report a piece the caller did not ask about.
    open_name = ((meta or {}).get("piece") or {}).get("name")
    stolen = bool(unit and meta and open_name != unit)
    if meta and not stolen:
        script = "check_skin.py" if meta.get("kind") == "skin" else "check_part.py"
        cmd = [sys.executable, str(ROOT / "tools" / script), "--status", str(piece_dir), *args]
    else:
        if not unit:
            return fail("no active piece and no MCPTK_UNIT: nothing published under " + str(STATUS))
        piece_dir = None  # the unit's files on disk, not a live tab: no history, no layout diff
        skin = (ROOT / "tools" / "skin_masters" / (unit + ".png")).exists()
        script = "check_skin.py" if skin else "check_part.py"
        # No layout block on this path: the diff is against the last check of a piece being edited,
        # and there is no session left to act on it.
        want_layout = False
        cmd = [sys.executable, str(ROOT / "tools" / script), unit, *args]
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")
    lines = (r.stdout or "").strip().splitlines()
    if not lines:
        print((r.stderr.strip().splitlines() or ["checker exited %d" % r.returncode])[-1])
        return r.returncode or 1

    # The last line is the report; everything before it is the checker's own chatter and is passed
    # through untouched, because the loop reads only the last line.
    report = None
    try:
        report = json.loads(lines[-1])
    except ValueError:
        pass
    if not isinstance(report, dict):
        sys.stdout.write(r.stdout)
        return 0 if r.stdout.strip() else r.returncode or 1

    # No history on the by-unit path: there is no piece directory, and nothing to diff against.
    history = (piece_dir / "loop-previous.json") if piece_dir else None
    previous = read_json(history) if history else None
    # Written before the block is composed, so a caller that suppresses the block still advances the
    # history: the diff is against the last CHECK, whoever asked for it.
    if history:
        try:
            history.write_text(json.dumps(report), encoding="utf-8")
        except OSError:
            pass
    extra = layout_lines(report, previous if isinstance(previous, dict) else None) if want_layout else []
    if extra and isinstance(report.get("text"), str):
        report["text"] = report["text"].rstrip("\n") + "\n" + "\n".join(extra)
    if stolen and isinstance(report.get("text"), str):
        report["text"] = (
            "  ! the Blockbench tab holds %s, not %s - another session has the editor. This is %s "
            "as it stands ON DISK, which is not what is in front of anyone right now."
            % (open_name or "another piece", unit, unit)
        ) + "\n" + report["text"]
    for line in lines[:-1]:
        print(line)
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
