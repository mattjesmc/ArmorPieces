"""Run the gate's tier 2: every scenario, against a dedicated server this starts and stops.

    python tools/gate/tier2.py                 # start a server, run everything, stop it again
    python tools/gate/tier2.py --attach        # use the game that is already running
    python tools/gate/tier2.py --only loot     # scenarios whose name contains this
    python tools/gate/tier2.py --list
    python tools/gate/tier2.py --json report.json

A server takes about a minute to come up and the whole suite a few seconds after that, so the cost
of the tier is the boot. `--attach` is for writing scenarios, where the game is already there; the
gate itself always starts its own, because the point of a gate is that it needs nothing to be true
of the machine beforehand.

**The stale-instance guard is not optional.** A second game cannot bind 25599 and the bridge answers
from the OLDER JVM without saying so, which means a green run for code that is not loaded. Every run
here reads `ping.build` and refuses an instance that does not carry this mod, or that the toolkit
itself calls stale.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

if __package__ in (None, ""):  # run as a file rather than as a module
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from gate import fixtures
    from gate.bridge import Bridge, BridgeError
    from gate.scenarios import SCENARIOS, Failed, Game
else:
    from . import fixtures
    from .bridge import Bridge, BridgeError
    from .scenarios import SCENARIOS, Failed, Game

ROOT = Path(__file__).resolve().parent.parent.parent
GRADLEW = str(ROOT / ("gradlew.bat" if sys.platform == "win32" else "gradlew"))


def start_server(log: Path) -> subprocess.Popen:
    """`gradlew runServer`, its output on disk rather than in this terminal."""
    log.parent.mkdir(parents=True, exist_ok=True)
    handle = log.open("w", encoding="utf-8", errors="replace")
    return subprocess.Popen(
        [GRADLEW, "runServer", "--console=plain"],
        cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT,
    )


def stop_server(server: subprocess.Popen, bridge: Bridge) -> None:
    """Shut a server down, and make sure it is really gone.

    `/stop` is the polite way and the only one that saves the world. Killing the process this
    started is NOT enough on its own: what was started is the Gradle wrapper, and the game is its
    grandchild - terminate the wrapper and the game carries on holding port 25599, where the next
    run finds it and mistakes it for its own.
    """
    polite = False
    try:
        # `/stop` only means anything to a game that got as far as having a server. One that refused
        # its datapacks is still a live JVM - the bridge holds it open - and waiting for it to end
        # on its own is waiting for nothing.
        polite = bool(bridge.call("ping").get("serverRunning"))
        if polite:
            bridge.command("stop")
    except (BridgeError, OSError):
        pass
    deadline = time.monotonic() + (180 if polite else 5)
    while time.monotonic() < deadline:
        if server.poll() is not None and not bridge.alive():
            return
        time.sleep(2)
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(server.pid)],
                       capture_output=True, check=False)
    else:
        server.kill()
    try:
        server.wait(timeout=60)
    except subprocess.TimeoutExpired:
        pass


def check_instance(bridge: Bridge) -> str:
    """Refuse a game that is not this mod, or that the toolkit says is running old code."""
    ping = bridge.call("ping")
    build = ping.get("build") or {}
    mods = {mod.get("id"): mod for mod in build.get("mods") or [] if isinstance(mod, dict)}
    if "armorpieces" not in mods:
        raise SystemExit(
            "the game on this bridge is not running Armor Pieces: "
            f"{sorted(mods) or 'no mod list at all'}. A second game cannot bind the port, so this "
            "is another instance answering - stop it before running the gate.")
    if build.get("stale"):
        raise SystemExit(
            "the attached game is running code older than the tree (ping.build says stale). "
            "Rebuild and restart it; a green run against a stale instance is worse than no run.")
    if not ping.get("serverRunning"):
        raise SystemExit("the bridge answered but no server is running behind it")
    return f"{mods['armorpieces'].get('version')} in {ping.get('env')}"


@dataclass
class BootCheck:
    """A claim that can only be tested by STARTING a game with a pack in it.

    A datapack registry is read once, when the world loads, so anything about how the mod treats a
    file it disapproves of - or a file that names content nobody installed - happens before there is
    a bridge to ask. These get a server of their own: install the pack, start, watch, judge, stop.
    """

    name: str
    what: str
    pack: str
    judge: Callable[[str, "Bridge | None"], tuple[str, str]]


#: What a server that has given up says on its way down. Watched for, because a game that refuses a
#: datapack does NOT necessarily exit: the toolkit's bridge holds the JVM open, so waiting for the
#: process to end waits for the whole timeout and reports the right answer seven minutes late.
GAVE_UP = ("Failed to load registries", "Failed to load datapacks", "Exception in server tick loop")


def boot_with(pack: str, boot_seconds: int, log: Path) -> tuple[str, "Bridge | None", subprocess.Popen]:
    """Start a server with one fixture pack installed and wait for it to settle either way."""
    fixtures.install(pack)
    server = start_server(log)
    bridge = Bridge()
    deadline = time.monotonic() + boot_seconds
    while time.monotonic() < deadline:
        try:
            if bridge.call("ping").get("serverRunning"):
                return read(log), bridge, server
        except (BridgeError, OSError):
            pass
        text = read(log)
        if server.poll() is not None or any(marker in text for marker in GAVE_UP):
            return text, None, server
        time.sleep(2)
    return read(log), None, server


def read(log: Path) -> str:
    return log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""


def refused_by_name(text: str, up: "Bridge | None") -> tuple[str, str]:
    """A part the load-time rules forbid: the pack has to be refused, and the refusal has to say why."""
    if "if_fitting" in text:
        return "pass", ""
    if up is None:
        return "FAIL", ("the server gave up on the pack without a message naming "
                        "armorpieces:if_fitting, so a pack author is told nothing they can act on")
    return "FAIL", ("a part gating a glider on a wearer condition was ACCEPTED: the world came up "
                    "with the pack loaded, and gliding is asked on the client, where the condition "
                    "cannot be evaluated at all")


def survives_a_missing_tag(text: str, up: "Bridge | None") -> tuple[str, str]:
    """A group naming a tag nobody installed: an empty set, never a world that will not open."""
    if up is None:
        return "FAIL", (
            "a loot group naming a tag no installed pack defines took the WHOLE WORLD down: the "
            "server refused to start. This is the case every pack in the line meets the day a "
            "player installs one pack and not another - LootGroup binds its `parts`, `skins`, "
            "`cloths` and `fittings` with RegistryCodecs.homogeneousList, which resolves a tag when "
            "the file is READ, while MemberSet (used by TemplateEntry for exactly this reason) "
            "keeps the tag and asks for it at the moment it is used.\n"
            + "\n".join(line for line in text.splitlines() if "Unbound tags" in line))
    listed = up.command("armorpieces loot groups").get("output") or []
    if any("gate:absent" in str(line) for line in listed):
        return "pass", ""
    return "FAIL", ("the world came up but the group naming an absent tag was dropped: "
                    + "; ".join(str(line) for line in listed))


BOOT_CHECKS = [
    BootCheck("refusals", "a part the load-time rules forbid is refused when the pack loads, by name",
              fixtures.REFUSAL, refused_by_name),
    BootCheck("missing-tag", "a group naming a tag nobody installed is an empty set, not a dead world",
              fixtures.MISSING_TAG, survives_a_missing_tag),
]


def run_boot_check(check: BootCheck, boot_seconds: int) -> tuple[str, str]:
    log = ROOT / "build" / "gate" / f"boot-{check.name}.log"
    text, up, server = boot_with(check.pack, boot_seconds, log)
    try:
        status, note = check.judge(text, up)
        if note:
            note = f"{note}\n  the server's own log is {log}"
        return status, note
    finally:
        stop_server(server, Bridge())
        fixtures.remove(check.pack)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--attach", action="store_true",
                        help="use a game that is already running instead of starting one")
    parser.add_argument("--only", action="append", default=[], metavar="NAME")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--json", metavar="PATH")
    parser.add_argument("--url", default="http://127.0.0.1:25599")
    parser.add_argument("--boot-seconds", type=int, default=420,
                        help="how long to wait for a server to answer (default 420)")
    parser.add_argument("--no-boot-checks", action="store_true",
                        help="skip the checks that need a server of their own (a boot each)")
    parser.add_argument("--keep", action="store_true",
                        help="leave the server running afterwards (implied by --attach)")
    args = parser.parse_args(argv)

    scenarios = [s for s in SCENARIOS
                 if not args.only or any(term in s.name for term in args.only)]
    if args.list:
        for scene in SCENARIOS:
            print(f"tier 2  {scene.name:<20} {scene.what}")
        for check in BOOT_CHECKS:
            print(f"tier 2  {check.name:<20} {check.what}   (a server of its own)")
        return 0
    if not scenarios:
        print("nothing matched")
        return 2

    bridge = Bridge(args.url)
    server: subprocess.Popen | None = None
    log = ROOT / "build" / "gate" / "server.log"
    started = time.monotonic()

    if not args.attach:
        if bridge.alive():
            raise SystemExit(
                f"something is already answering on {args.url}. A second server cannot bind that "
                "port and would be invisible behind the first; stop it, or pass --attach to use it.")
        print(f"starting a dedicated server; its log is {log}")
        # Before the boot, and it has to be: a part or a loot group is a registry entry, and a
        # datapack registry is read exactly once, when the world loads.
        fixtures.install(fixtures.GOOD)
        server = start_server(log)

    try:
        bridge.wait(args.boot_seconds if server else 30, server=True)
        print(f"attached to Armor Pieces {check_instance(bridge)} "
              f"after {time.monotonic() - started:.0f}s\n")

        game = Game(bridge)
        results = []
        for scene in scenarios:
            began = time.monotonic()
            status, note = "pass", ""
            try:
                scene.run(game)
            except Failed as failure:
                status, note = "FAIL", str(failure)
            except BridgeError as refused:
                status, note = "FAIL", f"the bridge refused a call: {refused}"
            except Exception as broke:  # a scenario's own bug is not the mod's fault, but it is a fail
                status, note = "FAIL", f"{type(broke).__name__}: {broke}"
            finally:
                game.restore()
            seconds = time.monotonic() - began
            results.append({"name": scene.name, "what": scene.what, "status": status,
                            "seconds": round(seconds, 1), "note": note})
            print(f"  {status:<5} {scene.name:<20} {seconds:5.1f}s")
            if note:
                for line in note.splitlines():
                    print(f"        {line}")

        # The boot checks come last and cost a server each; they are the claims that cannot be
        # asked of a running game, because they are about what happens while a world loads.
        if not args.attach and not args.no_boot_checks:
            stop_server(server, bridge)
            server = None
            for check in BOOT_CHECKS:
                if args.only and not any(term in check.name for term in args.only):
                    continue
                began = time.monotonic()
                status, note = run_boot_check(check, args.boot_seconds)
                results.append({"name": check.name, "status": status, "note": note,
                                "what": check.what, "seconds": round(time.monotonic() - began, 1)})
                print(f"  {status:<5} {check.name:<20} {time.monotonic() - began:5.1f}s")
                if note:
                    for line in note.splitlines():
                        print(f"        {line}")

        failed = [r for r in results if r["status"] == "FAIL"]
        print(f"\n{len(results) - len(failed)} passed, {len(failed)} failed, "
              f"in {time.monotonic() - started:.0f}s")
        if args.json:
            Path(args.json).write_text(json.dumps({"tier": 2, "scenarios": results}, indent=2),
                                       encoding="utf-8")
            print(f"report: {args.json}")
        return 1 if failed else 0
    finally:
        if server is not None and not args.keep:
            print("stopping the server")
            stop_server(server, bridge)
        if not args.attach:
            fixtures.remove(fixtures.GOOD)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
