"""Check that every part's painter still agrees with the part.

This exists because the painters rotted in silence. Each `paint_<part>_master.py` grew a
`check_geometry()` after four masters drifted off the cube lists they were painted for - a master
painted for a shape the model no longer has stays perfectly self-consistent while its rectangles
slide off the faces, which renders as a hole straight through the part - but an assertion nobody
executes is not a guard. Nothing in the Gradle build runs `tools/`, so by the 0.2.0 release three
tools were broken and no one knew:

    trace_geometry.py           dead on import - the mc_humanoid refactor moved BODY/ARMOR_LAYERS
                                out of bb_rig and trace was never updated
    paint_greaves_master.py     CUBES said the rim was 5x1x2 at uv (26,0); the shipped geometry
                                said 4x1x2 at (27,0), so it failed its own check_geometry()
    paint_poleyns_master.py     SHELL carried the leggings at 0.5 inflate when the legs are 0.4

Two things are checked here, and they are different failures:

  * **stale** - the painter raises. Its CUBES, its SHELL or its face maths no longer describe the
    shipped geometry. Someone changed the model (usually in Blockbench, which writes the geometry and
    the PNG but never the painter) and the painter did not follow.
  * **churn** - the painter runs but writes a different PNG than the one in the tree. The painters
    are deterministic on purpose (`random.seed(...)  # regenerating must not churn the PNG`), so a
    difference means the installed art and the script that claims to produce it have parted company:
    someone painted over the master by hand, or the painter was edited without reinstalling.

The check is non-destructive. Every master is hashed first, the painters run, the hashes are
compared, and anything that changed is put back - so running this never silently rewrites art.

`trace_geometry.py` is exercised too, over every part, because that is the tool the whole authoring
process leans on and it is the one that died most quietly.

**Every part means the packs' too.** The split of 2026-09-07 moved 25 parts out of the mod, and both
halves of this check went blind to them at once: seven painters raised on a geometry file that was
no longer where they looked, and the trace pass simply stopped visiting a quarter of the parts
without saying so. `decoration_paths` is where "which file is this part's" lives now; the masters
did not move, because `tools/decoration_masters/` is one authoring directory and which pack a part
ships in is decided after it is drawn.

Usage:
    python tools/check_painters.py                 # every painter, then trace over every part
    python tools/check_painters.py greaves sash    # just these
    python tools/check_painters.py --no-trace      # skip the trace pass
"""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decoration_paths  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
MASTERS = TOOLS / "decoration_masters"

PAINTER = re.compile(r"^paint_(?P<part>.+)_master\.py$")


def painters(only: list[str]) -> list[tuple[str, Path]]:
    found = []
    for path in sorted(TOOLS.glob("paint_*_master.py")):
        match = PAINTER.match(path.name)
        if match and (not only or match["part"] in only):
            found.append((match["part"], path))
    return found


def digests() -> dict[Path, str]:
    return {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(MASTERS.glob("*.png"))}


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    do_trace = "--no-trace" not in sys.argv[1:]

    found = painters(args)
    if args and len(found) != len(args):
        missing = set(args) - {part for part, _ in found}
        print(f"no painter for: {', '.join(sorted(missing))}")
        return 2

    stale: list[tuple[str, str]] = []
    churned: list[str] = []

    with tempfile.TemporaryDirectory() as tmp:
        keep = Path(tmp)
        before = digests()
        for path, digest in before.items():
            shutil.copy2(path, keep / path.name)

        for part, path in found:
            done = subprocess.run([sys.executable, str(path)], capture_output=True, text=True, cwd=ROOT)
            if done.returncode != 0:
                tail = (done.stderr or done.stdout).strip().splitlines()
                stale.append((part, tail[-1] if tail else f"exit {done.returncode}"))

        after = digests()
        for path, digest in after.items():
            was = before.get(path)
            if was is None:
                continue  # a sheet this run created; nothing to compare it against
            if was != digest:
                churned.append(path.name)
                shutil.copy2(keep / path.name, path)  # non-destructive: put the tree back

    for part, why in stale:
        print(f"STALE  {part}: {why}")
    for name in churned:
        print(f"CHURN  {name}: the painter writes different pixels than the installed sheet")

    traced = 0
    if do_trace:
        for geometry in decoration_paths.all_geometry():
            if args and geometry.stem not in args:
                continue
            done = subprocess.run([sys.executable, str(TOOLS / "trace_geometry.py"), str(geometry)],
                                  capture_output=True, text=True, cwd=ROOT)
            traced += 1
            if done.returncode != 0:
                tail = (done.stderr or done.stdout).strip().splitlines()
                stale.append((geometry.stem, f"trace_geometry: {tail[-1] if tail else done.returncode}"))
                print(f"STALE  {geometry.stem}: trace_geometry failed")

    if stale or churned:
        print(f"\n{len(stale)} stale, {len(churned)} churned over {len(found)} painter(s)"
              f"{f' and {traced} trace(s)' if do_trace else ''}")
        return 1

    print(f"{len(found)} painter(s) agree with their geometry and reproduce their sheets"
          f"{f'; {traced} part(s) trace clean' if do_trace else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
