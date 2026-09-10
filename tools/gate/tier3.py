"""Run the gate's tier 3: every scene, against a client this starts and stops.

    python tools/gate/tier3.py                  # start a client, run everything, stop it again
    python tools/gate/tier3.py --attach         # use the game that is already running
    python tools/gate/tier3.py --only layer     # scenes whose name contains this
    python tools/gate/tier3.py --bless          # keep this run's frames as the goldens
    python tools/gate/tier3.py --list
    python tools/gate/tier3.py --json report.json

The tier costs a client boot - a minute or so - plus a world, and then a couple of seconds a scene.

**What --bless means, and it is the whole difference between this tier and the others.** A golden is
a frame a PERSON has looked at and said is right. `--bless` writes one, and the runner will not
write one on its own for any reason: a scene with no golden reports `new` and fails the run, with
the path of the frame to open. Blessing a frame nobody looked at turns the tier into a machine that
asserts the mod still draws whatever it drew the day it broke.

**The world is built, never reused.** A datapack registry is read once when a world loads, the
studio moves the client, and the last run's frozen tick is the last run's problem: every run creates
its own flat world with `create_world {replace: true}`. `--attach` is for writing scenes, where the
world is already open.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

if __package__ in (None, ""):  # run as a file rather than as a module
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from gate.bridge import Bridge, BridgeError
    from gate.frames import Goldens
    from gate.scenes3 import SCENES, Client, Failed
else:
    from .bridge import Bridge, BridgeError
    from .frames import Goldens
    from .scenes3 import SCENES, Client, Failed

ROOT = Path(__file__).resolve().parent.parent.parent
GRADLEW = str(ROOT / ("gradlew.bat" if sys.platform == "win32" else "gradlew"))
OUT = ROOT / "build" / "gate" / "tier3"

#: The world every run builds for itself. Flat, empty, lit, and nothing alive in it but the subject.
WORLD = {
    "name": "gate_tier3",
    "generator": "flat",
    # A floor rather than the void: the client's own player has to stand somewhere
    # while the studio does its work in another dimension, and a player falling
    # through nothing takes the loaded chunks with it - which is where the item-frame
    # wall the icons scene photographs would have to be.
    "flat": "minecraft:classic_flat",
    "gamemode": "creative",
    # NOT peaceful: the studio's subject is a zombie, and a peaceful world removes one the moment it
    # is spawned - which the toolkit refuses rather than photographing an empty floor.
    "difficulty": "easy",
    "cheats": True,
    "structures": False,
    "seed": "armorpieces gate",
    "replace": True,
}

#: What the world is told once it is up. `doMobSpawning` off is not tidiness: a hostile wandering
#: into a frame is a golden that fails for a reason that is nothing to do with this mod.
GAMERULES = ("doMobSpawning false", "doDaylightCycle false", "doWeatherCycle false",
             "doFireTick false", "mobGriefing false", "sendCommandFeedback true")


def start_client(log: Path) -> subprocess.Popen:
    """`gradlew runClient`, its output on disk rather than in this terminal."""
    log.parent.mkdir(parents=True, exist_ok=True)
    handle = log.open("w", encoding="utf-8", errors="replace")
    return subprocess.Popen(
        [GRADLEW, "runClient", "--console=plain"],
        cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT,
    )


def stop_client(client: subprocess.Popen | None, bridge: Bridge) -> None:
    """Close the game, and make sure it is really gone.

    `quit_game` is the polite way and the one that releases the jar lock. Killing what was started
    is not enough on its own: that is the Gradle wrapper, and the game is its grandchild - terminate
    the wrapper and the game carries on holding port 25599, where the next run finds it and mistakes
    it for its own.
    """
    if client is None:
        return
    try:
        bridge.call("quit_game")
    except (BridgeError, OSError):
        pass
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        if client.poll() is not None and not bridge.alive():
            return
        time.sleep(2)
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(client.pid)],
                       capture_output=True, check=False)
    else:
        client.kill()
    try:
        client.wait(timeout=60)
    except subprocess.TimeoutExpired:
        pass


def check_instance(bridge: Bridge) -> str:
    """Refuse a game that is not this mod, that is stale, or that has no client behind it."""
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
    return f"{mods['armorpieces'].get('version')} in {ping.get('env')}"


def open_world(bridge: Bridge, seconds: int) -> None:
    """Build the world this run photographs in, and wait until the client is standing in it."""
    # The client registers its own tools after the bridge starts answering; `create_world` is one
    # of them and is the first thing this suite needs.
    bridge.wait_for_tool("create_world", seconds)
    bridge.call("create_world", **WORLD)
    # `serverRunning` is not "the client is in the world": the integrated server comes up first, and
    # a `studio` or a `get_tooltip` in that window is refused with "no level loaded". What answers
    # only once the client is really standing in a level is get_world_info's world_uuid, and what
    # answers once the player exists is get_entities.
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if in_a_world(bridge):
            for rule in GAMERULES:
                bridge.command(f"gamerule {rule}")
            # A fixed standing place, so the chunks a scene builds in are the loaded ones and a
            # frame is never refused for a camera in a chunk this client was not sent.
            bridge.command("spawnpoint @a 0 5 0")
            bridge.command("tp @a 0 5 0 135 0")
            return
        time.sleep(2)
    raise SystemExit(f"the client did not finish loading {WORLD['name']} within {seconds}s")


def in_a_world(bridge: Bridge) -> bool:
    """Whether the client is standing in a loaded level with its player in it."""
    try:
        if not bridge.call("ping").get("serverRunning"):
            return False
        if not bridge.call("get_world_info").get("world_uuid"):
            return False
        return "player" in (bridge.call("get_entities", radius=1).get("source") or "")
    except (BridgeError, OSError):
        return False


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--attach", action="store_true",
                        help="use a game that is already running, and its world")
    parser.add_argument("--only", action="append", default=[], metavar="NAME")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--bless", action="store_true",
                        help="write this run's frames as the goldens - only after LOOKING at them")
    parser.add_argument("--json", metavar="PATH")
    parser.add_argument("--url", default="http://127.0.0.1:25599")
    parser.add_argument("--boot-seconds", type=int, default=420,
                        help="how long to wait for a client to answer (default 420)")
    parser.add_argument("--keep", action="store_true",
                        help="leave the game running afterwards (implied by --attach)")
    args = parser.parse_args(argv)

    scenes = [s for s in SCENES if not args.only or any(term in s.name for term in args.only)]
    if args.list:
        for scene in SCENES:
            print(f"tier 3  {scene.name:<12} {scene.what}")
        return 0
    if not scenes:
        print("nothing matched")
        return 2

    bridge = Bridge(args.url)
    client: subprocess.Popen | None = None
    log = ROOT / "build" / "gate" / "client.log"
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()

    if not args.attach:
        if bridge.alive():
            raise SystemExit(
                f"something is already answering on {args.url}. A second game cannot bind that "
                "port and would be invisible behind the first; stop it, or pass --attach to use it.")
        print(f"starting a client; its log is {log}")
        client = start_client(log)

    try:
        try:
            bridge.wait(args.boot_seconds if client else 30)
        except BridgeError as silence:
            # --attach with nothing to attach to is the ordinary mistake here, and a stack trace is
            # a poor way to say "start a client first".
            raise SystemExit(f"{silence}\n  --attach needs a game already running: "
                             "`gradlew runClient`, or drop --attach and let this start one.")
        print(f"attached to Armor Pieces {check_instance(bridge)} "
              f"after {time.monotonic() - started:.0f}s")
        if not args.attach:
            open_world(bridge, args.boot_seconds)
            print(f"the world is up after {time.monotonic() - started:.0f}s\n")

        goldens = Goldens(OUT, bless=args.bless)
        game = Client(bridge, goldens, OUT)
        results = []
        for scene in scenes:
            began = time.monotonic()
            status, note = "pass", ""
            try:
                scene.run(game)
                if game.problems:
                    # Every frame this scene could not pass, not only the first: a run that stopped
                    # at frame one of twelve would have to be repeated eleven times.
                    status, note = "FAIL", "\n".join(game.problems)
            except Failed as failure:
                status, note = "FAIL", str(failure)
            except BridgeError as refused:
                status, note = "FAIL", f"the bridge refused a call: {refused}"
            except Exception as broke:  # a scene's own bug is not the mod's fault, but it is a fail
                status, note = "FAIL", f"{type(broke).__name__}: {broke}"
            finally:
                game.restore()
            seconds = time.monotonic() - began
            results.append({"name": scene.name, "what": scene.what, "status": status,
                            "seconds": round(seconds, 1), "note": note})
            print(f"  {status:<5} {scene.name:<12} {seconds:5.1f}s")
            if note:
                for line in note.splitlines():
                    print(f"        {line}")

        frames = goldens.results
        blessed = [f for f in frames if f.status == "blessed"]
        if blessed:
            print(f"\n{len(blessed)} golden(s) written: " + ", ".join(f.name for f in blessed))
        failed = [r for r in results if r["status"] == "FAIL"]
        print(f"\n{len(results) - len(failed)} passed, {len(failed)} failed, "
              f"{len(frames)} frame(s), in {time.monotonic() - started:.0f}s")
        if args.json:
            Path(args.json).parent.mkdir(parents=True, exist_ok=True)
            Path(args.json).write_text(json.dumps({
                "tier": 3, "scenes": results,
                "frames": [{"name": f.name, "status": f.status, "pixels": f.pixels}
                           for f in frames],
            }, indent=2), encoding="utf-8")
            print(f"report: {args.json}")
        return 1 if failed else 0
    finally:
        if client is not None and not args.keep:
            stop_client(client, bridge)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
