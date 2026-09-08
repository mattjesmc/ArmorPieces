"""
The gate: everything that can fail, run in one command, before a release.

`docs/plans/testing.md` is the design. The short version: nothing in the build runs `tools/`, so the
authoring tools rot in silence - three painters are stale as this is written - and everything the
game does was verified by a person driving a client, once, and never again. This runner is the part
that costs nothing to keep: one command, one line per check, nonzero if any of them failed.

Checks are grouped by WHAT THEY NEED, because that is what decides whether one can run at all:

    tier 0   the tree      python and node. Runs anywhere, in a couple of minutes.
    tier 1   the JVM       gradle. Compiles the mod and runs the JUnit tests.
    tier 2   the server    a dedicated server with the mcp-toolkit bridge (not built yet)
    tier 3   the client    a client with the bridge, for rendering and screens (not built yet)

Sequential on purpose. `check_painters.py` re-runs every painter and puts the masters back, so a
check reading those PNGs at the same moment would read a file mid-rewrite.

Usage:
    python tools/gate.py                    # every tier this machine can run
    python tools/gate.py --tier 0           # the tree only
    python tools/gate.py --only painters    # one check, by name
    python tools/gate.py --list             # what would run
    python tools/gate.py --json report.json # the same result as a file
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
GRADLEW = str(ROOT / ("gradlew.bat" if sys.platform == "win32" else "gradlew"))


@dataclass
class Check:
    name: str
    tier: int
    what: str
    command: list[str]
    needs: str = "python"
    timeout: int = 1800


@dataclass
class Result:
    check: Check
    status: str  # pass | fail | skip | pending
    seconds: float = 0.0
    output: str = ""
    note: str = ""


def tier0() -> list[Check]:
    return [
        Check("authoring", 0,
              "the plugin's round trip over every part, skin, cloth, recipe and loot group",
              [PY, "tools/check_authoring.py"]),
        Check("skins", 0,
              "every master pair: unpainted slots, off-net paint, ramp range, overruled steps",
              [PY, "tools/check_skin.py", "--all"]),
        Check("uids", 0,
              "every shipped piece has a lineage uid, none doubled, none ever changed",
              [PY, "tools/mint_uids.py", "--check"]),
        Check("lang", 0,
              "every name the mod shows has a line in en_us.json",
              [PY, "tools/check_lang.py"]),
        Check("effect-schema", 0,
              "the schema the Blockbench dialog reads still describes the Java it is parsed from",
              [PY, "tools/check_effect_schema.py"]),
        Check("painters", 0,
              "every painter still describes its geometry and reproduces its sheet; every part traces",
              [PY, "tools/check_painters.py"], timeout=3600),
        Check("plugin-parses", 0,
              "the Blockbench plugin is syntactically valid JavaScript",
              ["node", "--check", "tools/blockbench_plugin/armorpieces.js"], needs="node"),
        *[Check(f"tests/{path.stem.removeprefix('test_')}", 0,
                f"the unit tests in {path.name}",
                [PY, str(path.relative_to(ROOT))])
          for path in sorted((ROOT / "tools" / "tests").glob("test_*.py"))],
    ]


def tier1() -> list[Check]:
    return [
        Check("build", 1,
              "the mod compiles, and the JUnit tests pass (the skin bake against its reference)",
              [GRADLEW, "build", "--console=plain"], needs="gradle", timeout=3600),
    ]


def pending() -> list[Check]:
    """Tiers designed and not built. Named here so the gate reports its own coverage honestly."""
    return [
        Check("server-scenarios", 2,
              "loading, loot, effects, config and the load-time refusals, on a dedicated server",
              []),
        Check("client-frames", 3,
              "the render layer, skins, cloth, fittings, the smithing screen and the tooltip",
              []),
    ]


def available(needs: str) -> bool:
    if needs == "python":
        return True
    if needs == "node":
        return shutil.which("node") is not None
    if needs == "gradle":
        return Path(GRADLEW).exists()
    return False


def run(check: Check) -> Result:
    if not check.command:
        return Result(check, "pending", note="not built yet - see docs/plans/testing.md")
    if not available(check.needs):
        return Result(check, "skip", note=f"{check.needs} is not on this machine")

    started = time.monotonic()
    try:
        done = subprocess.run(check.command, cwd=ROOT, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=check.timeout)
    except subprocess.TimeoutExpired:
        return Result(check, "fail", time.monotonic() - started,
                      note=f"timed out after {check.timeout}s")
    except FileNotFoundError:
        return Result(check, "skip", time.monotonic() - started,
                      note=f"{check.command[0]} not found")

    output = (done.stdout or "") + (done.stderr or "")
    status = "pass" if done.returncode == 0 else "fail"
    return Result(check, status, time.monotonic() - started, output,
                  note="" if status == "pass" else f"exit {done.returncode}")


def shell(command: list[str]) -> str:
    return " ".join(part if " " not in part else f'"{part}"' for part in command)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tier", type=int, default=None,
                        help="run tiers up to this one (default: every tier that is built)")
    parser.add_argument("--only", action="append", default=[], metavar="NAME",
                        help="run only checks whose name contains this; repeatable")
    parser.add_argument("--list", action="store_true", help="print what would run and stop")
    parser.add_argument("--json", metavar="PATH", help="write the result as JSON")
    parser.add_argument("--tail", type=int, default=25, metavar="N",
                        help="lines of a failure's output to print (default 25)")
    args = parser.parse_args(argv)

    checks = tier0() + tier1() + pending()
    if args.tier is not None:
        checks = [c for c in checks if c.tier <= args.tier]
    if args.only:
        checks = [c for c in checks if any(term in c.name for term in args.only)]
    if not checks:
        print("nothing matched")
        return 2

    if args.list:
        for check in checks:
            state = "" if check.command else "   (not built yet)"
            print(f"tier {check.tier}  {check.name:<22} {check.what}{state}")
        return 0

    print(f"the gate: {len(checks)} check(s)\n")
    results: list[Result] = []
    started = time.monotonic()
    live = sys.stdout.isatty()  # a piped run keeps the overwritten line, so only draw it on a tty
    for check in checks:
        if live:
            print(f"  ...   {check.name}", end="", flush=True)
        result = run(check)
        results.append(result)
        mark = {"pass": "ok", "fail": "FAIL", "skip": "skip", "pending": "todo"}[result.status]
        detail = f" - {result.note}" if result.note else ""
        print(f"{chr(13) if live else ''}  {mark:<5} {check.name:<22} "
              f"{result.seconds:5.1f}s{detail}")

    failed = [r for r in results if r.status == "fail"]
    for result in failed:
        print(f"\n--- {result.check.name}: {result.check.what}")
        lines = result.output.strip().splitlines()
        for line in lines[-args.tail:]:
            print(f"    {line}")
        print(f"    reproduce: {shell(result.check.command)}")

    counts = {state: sum(1 for r in results if r.status == state)
              for state in ("pass", "fail", "skip", "pending")}
    print(f"\n{counts['pass']} passed, {counts['fail']} failed, {counts['skip']} skipped, "
          f"{counts['pending']} not built yet, in {time.monotonic() - started:.0f}s")

    if args.json:
        Path(args.json).write_text(json.dumps({
            "root": str(ROOT),
            "seconds": round(time.monotonic() - started, 1),
            "checks": [{
                "name": r.check.name,
                "tier": r.check.tier,
                "what": r.check.what,
                "status": r.status,
                "seconds": round(r.seconds, 1),
                "note": r.note,
                "command": shell(r.check.command),
                "output": r.output if r.status == "fail" else "",
            } for r in results],
        }, indent=2), encoding="utf-8")
        print(f"report: {args.json}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
