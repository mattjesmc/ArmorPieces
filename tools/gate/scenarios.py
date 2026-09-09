"""Tier 2: what the mod does, asked of a running dedicated server.

Everything here was verified by hand once, by a person or an agent driving a game and reading chat -
three `runClient` cycles for the loot work alone - and none of it was ever asked again. A scenario is
that same conversation, written down: a few bridge calls and what their answers have to say.

The rules a scenario is written to, all of them scars:

  * **Say what is wrong, not that something is.** A failure here is read by someone who cannot see
    the game, so every check carries the line the game actually printed.
  * **Leave the world as it was found.** A scenario that pushes a datapack file clears it again in a
    `finally`, or the next one runs against its mess - and so does the next person to open this world.
  * **Ask for a share, not for presence.** "A template came out of this chest" passes with the loot
    system switched off, because one of ninety parts turns up eventually. The assertions here are
    over thousands of rolls with a fixed seed.
  * **A player is required.** Half the mod's commands refuse a console: they are about a wearer.
    The toolkit can spawn a real headless player, which is what {@code Game.player} is.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from . import fixtures
from .bridge import Bridge, BridgeError

ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG = ROOT / "run" / "config" / "armorpieces-server.json"

# The flat world the dev run makes has its surface here; a player has to be put on something.
SPAWN = {"x": 0, "y": 101, "z": 0}


class Failed(AssertionError):
    """A scenario's assertion did not hold. The message is what the game said."""


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise Failed(message)


def line_with(lines: list[str], needle: str) -> str:
    """The first line holding `needle`, or a failure naming everything that was there instead."""
    for line in lines:
        if needle.lower() in line.lower():
            return line
    raise Failed(f"nothing said {needle!r}; what was said was:\n    " + "\n    ".join(lines))


@dataclass
class Game:
    """One attached server, and the housekeeping every scenario would otherwise repeat."""

    bridge: Bridge
    player: str = ""
    pushed: list[str] = field(default_factory=list)

    # ---- talking to it ---------------------------------------------------------------------

    def out(self, command: str) -> list[str]:
        """A command's own output lines. A command the game refused to parse is a failure here."""
        result = self.bridge.command(command)
        lines = [str(line) for line in (result.get("output") or [])]
        if any("Unknown or incomplete command" in line for line in lines):
            raise Failed(f"the game does not know `{command}`: {lines}")
        return lines

    def as_player(self, command: str) -> list[str]:
        """The same, run as the headless player - for the commands that are about a wearer."""
        return self.out(f"execute as {self.needs_player()} run {command}")

    def needs_player(self) -> str:
        if not self.player:
            self.player = self.spawn_player()
        return self.player

    def wear(self, wearer: str, slot: str, item: str, anchor: str, part: str) -> None:
        """Put one decorated piece of armor on a wearer, in the item syntax a player would type."""
        self.out(f"item replace entity {wearer} armor.{slot} with {item}"
                 "[armorpieces:decorations={" + anchor + ':{material:"minecraft:gold",'
                 f'decoration:"{part}"}}}}]')

    def needs_fixtures(self) -> None:
        """Refuse to pass a scenario whose fixture pack was never installed - see fixtures.py."""
        if fixtures.GOOD not in fixtures.installed():
            raise Failed(
                f"the fixture pack {fixtures.GOOD} is not in the world, so this scenario would be "
                "asserting on content nobody loaded. A registry entry cannot be pushed into a "
                "running server; run tools/gate/tier2.py, which installs it before the boot.")

    def spawn_player(self) -> str:
        """A real headless player on the flat surface, in creative, with nothing hunting it."""
        self.bridge.command("difficulty peaceful")
        body = self.bridge.call("bot_body", action="spawn", type="player", pos=SPAWN)
        name = body.get("name") or "anon"
        self.bridge.command(f"gamemode creative {name}")
        return name

    # ---- the live datapack -----------------------------------------------------------------

    def push(self, path: str, content: dict | str, reload: bool = True) -> None:
        """A third-party pack file, with no file in this repository. Cleared by `restore`."""
        text = content if isinstance(content, str) else json.dumps(content, indent=2)
        self.bridge.push(path, text, reload=reload)
        self.pushed.append(path)

    def restore(self) -> None:
        """Take back everything this run pushed. Called in a finally, always."""
        while self.pushed:
            path = self.pushed.pop()
            try:
                self.bridge.clear(path, reload=not self.pushed)
            except BridgeError:
                pass

    # ---- reading the world -----------------------------------------------------------------

    def registry(self, registry: str, **args) -> list[str]:
        result = self.bridge.call("query_registry", registry=registry, limit=5000, **args)
        return result.get("ids") or result.get("entries") or result.get("values") or []

    def roll(self, table: str, count: int, seed: int) -> dict:
        return self.bridge.call("roll_loot", table=table, count=count, seed=seed)


@dataclass
class Scenario:
    name: str
    what: str
    run: Callable[[Game], None]


SCENARIOS: list[Scenario] = []


def scenario(name: str, what: str):
    def register(function: Callable[[Game], None]) -> Callable[[Game], None]:
        SCENARIOS.append(Scenario(name, what, function))
        return function

    return register


# ---------------------------------------------------------------------------------------------
# The world loads what this repository ships
# ---------------------------------------------------------------------------------------------


@scenario("load", "the mod's own datapack loaded, with every registry filled and no errors logged")
def load(game: Game) -> None:
    counts = {
        "armorpieces:armor_decoration": 60,
        "armorpieces:fitting": 4,
        "armorpieces:armor_skin": 9,
        "armorpieces:cloth": 2,
    }
    for registry, least in counts.items():
        ids = game.registry(registry)
        expect(len(ids) >= least,
               f"{registry} holds {len(ids)} entries; the mod ships at least {least}. "
               f"A registry this empty means the datapack did not load.")

    groups = game.out("armorpieces loot groups")
    for group in ("armorpieces:court", "armorpieces:knightly", "armorpieces:wayfarer"):
        line_with(groups, group)  # the three this mod ships; a run also has the gate's own

    # And nothing complained on the way in. `warn` and worse, ours only.
    noise = [line.get("message", "") for line in game.bridge.log(level="warn", limit=200)
             if "armorpieces" in json.dumps(line).lower()]
    expect(not noise, "the server logged this while loading the mod:\n    " + "\n    ".join(noise))


@scenario("commands", "every node of /armorpieces answers, and the ones about a wearer take one")
def commands(game: Game) -> None:
    listed = game.out("help armorpieces")
    for node in ("stage", "loot", "effects", "table", "missing", "prune", "upgrade"):
        line_with(listed, node)

    # The console can answer these.
    expect(game.out("armorpieces missing"), "missing said nothing at all")
    expect(game.out("armorpieces upgrade"), "upgrade said nothing at all")
    expect(game.out("armorpieces loot list"), "loot list said nothing at all")

    # And these are about a wearer, so they refuse a console and answer a player.
    console = game.bridge.command("armorpieces effects").get("output") or []
    expect(any("player is required" in line for line in console),
           f"effects should refuse a console rather than answer it: {console}")
    expect(game.as_player("armorpieces effects"), "effects said nothing to a player")


@scenario("stage", "the staging command builds its cross product and takes it away again")
def stage(game: Game) -> None:
    # The preview a part is judged in, and the one command of this mod a person uses every session.
    # Held to the world rather than to its own arithmetic: `clear` counts the entities it actually
    # finds carrying the stage tag, so staging N and then clearing at least N is the pair that says
    # the stands were really there. (The toolkit's entity survey does not see an armor stand, so
    # this is the count to use.)
    game.needs_player()  # staging is a player's command: it builds in front of whoever ran it
    game.as_player("armorpieces stage clear")  # start from an empty floor, whatever was left before
    try:
        for what in ("pieces", "skins", "random"):
            staged = game.as_player(f"armorpieces stage {what}")
            expect(staged, f"stage {what} said nothing at all")
            placed = number(staged[0], f"stage {what}")
            expect(placed > 0, f"stage {what} staged nothing: {staged[0]}")

            cleared = game.as_player("armorpieces stage clear")
            removed = number(cleared[0], "stage clear")
            expect(removed >= placed,
                   f"stage {what} said it staged {placed} and clear found {removed} in the world")

        # `bases` and `fittings` are the two whose whole cross product is past the four-thousand
        # limit, so the bare form is a REFUSAL - and the refusal is the interesting behaviour: it
        # says how many it would have been and what to do about it, rather than filling the world.
        for wide in ("bases", "fittings"):
            refused = game.as_player(f"armorpieces stage {wide}")
            expect("past the limit" in refused[0],
                   f"stage {wide} used to refuse its whole cross product; it now says: {refused[0]}")
            expect("argument" in refused[0],
                   f"the refusal has to say how to narrow it: {refused[0]}")

        # Narrowed, they stage - which is also the only place the two ARGUMENT forms are exercised.
        for narrow in ("bases minecraft:iron_chestplate", "fittings armorpieces:bandolier",
                       "skins armorpieces:brigandine"):
            staged = game.as_player(f"armorpieces stage {narrow}")
            expect(number(staged[0], f"stage {narrow}") > 0,
                   f"stage {narrow} staged nothing: {staged[0]}")
            game.as_player("armorpieces stage clear")
    finally:
        game.as_player("armorpieces stage clear")


def number(line: str, what: str) -> int:
    """The first number a command printed - what it says it did, in its own words."""
    found = re.search(r"(\d+)", line)
    expect(found is not None, f"{what} printed no number to check: {line!r}")
    return int(found.group(1))


# ---------------------------------------------------------------------------------------------
# Loot
# ---------------------------------------------------------------------------------------------


@scenario("loot-groups", "a group's tables and members are the ones its file names")
def loot_groups(game: Game) -> None:
    groups = game.out("armorpieces loot groups")
    for name in ("armorpieces:court", "armorpieces:knightly", "armorpieces:wayfarer"):
        line = line_with(groups, name)
        members = re.search(r"(\d+) member", line)
        tables = re.search(r"(\d+) table", line)
        expect(members is not None and int(members.group(1)) > 0,
               f"{name} has no members, so it fills no chest: {line}")
        expect(tables is not None and int(tables.group(1)) > 0,
               f"{name} names no table, so it is never rolled: {line}")

    explained = game.out("armorpieces loot explain minecraft:chests/simple_dungeon")
    line_with(explained, "armorpieces:knightly")
    touched = game.out("armorpieces loot list")[0]
    count = re.search(r"(\d+) of them touched", touched)
    expect(count is not None and int(count.group(1)) > 0,
           f"no loot table is touched by the mod at all: {touched}")


@scenario("loot-rolls", "a group's chance is what a chest actually pays out, over ten thousand rolls")
def loot_rolls(game: Game) -> None:
    # The share the group declares, read from the game rather than from the file: the config's
    # multiplier is allowed to move it, and what is being checked is what a PLAYER would see.
    explained = game.out("armorpieces loot explain minecraft:chests/simple_dungeon")
    declared = re.search(r"(\d+(?:\.\d+)?)% of the time", explained[0])
    expect(declared is not None, f"the game did not say how often it offers: {explained}")
    chance = float(declared.group(1)) / 100.0

    rolled = game.roll("minecraft:chests/simple_dungeon", count=4000, seed=20260909)
    text = json.dumps(rolled)
    ours = re.findall(r"armorpieces:[a-z_]+", text)
    expect(ours, "four thousand rolls of a table three groups name produced nothing of ours")

    # The reply aggregates; what is wanted is the share of ROLLS that carried something of ours.
    items = rolled.get("items") or rolled.get("aggregate") or {}
    total = 0.0
    if isinstance(items, dict):
        for item, stats in items.items():
            if "armorpieces" in str(item):
                total += float(stats.get("avg") or stats.get("count") or 0) \
                    if isinstance(stats, dict) else float(stats)
    elif isinstance(items, list):
        for entry in items:
            if "armorpieces" in json.dumps(entry):
                total += float(entry.get("avg") or entry.get("count") or 0)
    if total > 1.0:  # a count rather than an average
        total /= 4000.0
    expect(0.3 * chance <= total <= 3.0 * chance,
           f"the table is meant to offer something of ours {chance:.1%} of the time and paid out "
           f"{total:.1%} over four thousand rolls - the group's share is not what it says")


@scenario("foreign-table", "another pack's table can hand out one of our templates, and does")
def foreign_table(game: Game) -> None:
    # `armorpieces:template` is the entry a third-party table names to offer a template of ours,
    # and the point of it is that the pack needs no knowledge of which parts exist.
    table = "data/gate/loot_table/gate_chest.json"
    try:
        game.push(table, {
            "type": "minecraft:chest",
            "pools": [{
                "rolls": 1,
                "entries": [{
                    "type": "armorpieces:template",
                    "parts": "#armorpieces:knightly",
                }],
            }],
        })
        rolled = game.roll("gate:gate_chest", count=20, seed=99)
        text = json.dumps(rolled)
        expect("armorpieces" in text,
               f"a table naming armorpieces:template handed out nothing of ours: {text[:400]}")
        expect("template" in text.lower(),
               f"what it handed out was not a template: {text[:400]}")
    finally:
        game.restore()


# ---------------------------------------------------------------------------------------------
# The settings a server owner has
# ---------------------------------------------------------------------------------------------


@scenario("config", "the server settings file shows every knob, and turning one is obeyed")
def config(game: Game) -> None:
    expect(CONFIG.is_file(), f"{CONFIG} was never written; a server owner has nothing to edit")
    original = CONFIG.read_text(encoding="utf-8")
    written = json.loads(original)
    for key in ("enabled", "chance_multiplier", "groups"):
        expect(key in written, f"the settings file has no {key!r}: {sorted(written)}")

    before = game.out("armorpieces loot list")[0]
    try:
        written["enabled"] = False
        CONFIG.write_text(json.dumps(written, indent=2), encoding="utf-8")
        game.out("reload")
        after = game.out("armorpieces loot list")[0]
        touched = re.search(r"(\d+) of them touched", after)
        expect(touched is not None and int(touched.group(1)) == 0,
               f"the mod was switched off in the settings and the tables still carry it: {after}")
    finally:
        CONFIG.write_text(original, encoding="utf-8")
        game.out("reload")
    restored = game.out("armorpieces loot list")[0]
    expect(restored == before,
           f"switching the mod back on did not restore what it touches:\n    was: {before}\n    "
           f"now: {restored}")


# ---------------------------------------------------------------------------------------------
# What a worn piece does
# ---------------------------------------------------------------------------------------------


@scenario("effects", "a worn part's effect is reported, and an attribute one is actually granted")
def effects(game: Game) -> None:
    player = game.needs_player()
    game.needs_fixtures()
    try:
        # A glider on the back: the one effect this mod itself ships.
        game.wear(player, "chest", "minecraft:diamond_chestplate", "back", "armorpieces:pinions")
        worn = game.out(f"armorpieces effects {player}")
        line_with(worn, "pinions")
        expect("contributing" in worn[0], f"a worn glider should be contributing: {worn[0]}")

        # The same base item with no part on it is what the measurement is against, so that what is
        # measured is the PART and not the chestplate.
        game.out(f"item replace entity {player} armor.chest with minecraft:diamond_chestplate")
        base = attribute(game, player, "minecraft:armor")

        game.wear(player, "chest", "minecraft:diamond_chestplate", "back", "gate:measured")
        granted = attribute(game, player, "minecraft:armor")
        expect(abs(granted - base - fixtures.ARMOR_BONUS) < 0.001,
               f"a part granting +{fixtures.ARMOR_BONUS} armor moved the wearer from {base} to "
               f"{granted}")

        # And taking it off takes the modifier with it - the reconcile the wearer-condition rule
        # exists to protect.
        game.out(f"item replace entity {player} armor.chest with minecraft:air")
        bare = attribute(game, player, "minecraft:armor")
        expect(bare < granted,
               f"the modifier stayed on after the piece came off: {bare} with nothing worn, "
               f"{granted} while wearing it")
    finally:
        game.out(f"item replace entity {player} armor.chest with minecraft:air")


def attribute(game: Game, player: str, attribute_id: str) -> float:
    """An attribute as the server has it, read a few ticks after whatever changed it.

    Equipment lands on the entity immediately; the modifiers it carries are reconciled on the
    entity's next tick, so a read in the same breath as the `item replace` measures the armor the
    wearer had BEFORE putting anything on.
    """
    time.sleep(0.3)
    line = game.out(f"attribute {player} {attribute_id} get")[0]
    found = re.search(r"is ([0-9.]+)", line)
    expect(found is not None, f"could not read an attribute out of: {line}")
    return float(found.group(1))


@scenario("identity", "a piece nothing defines is kept and reported, not thrown away")
def identity(game: Game) -> None:
    # The measurement this whole mechanism came from: before it, a helmet whose crest named a part
    # the installed packs no longer defined lost the HELMET, not the crest.
    player = game.needs_player()
    try:
        game.out(f"item replace entity {player} armor.head with minecraft:diamond_helmet"
                 '[armorpieces:decorations={brow:{material:"minecraft:gold",'
                 'decoration:"gate:a_pack_that_is_not_installed"}}]')
        held = game.out(f"data get entity {player} equipment.head")  # may be empty on a fake player
        missing = game.out("armorpieces missing")
        expect(any("gate:a_pack_that_is_not_installed" in line for line in missing),
               "a piece nothing defines was not reported by `armorpieces missing`; it said:\n    "
               + "\n    ".join(missing) + ("\n  the stack read as: " + "; ".join(held) if held else ""))
    finally:
        game.out(f"item replace entity {player} armor.head with minecraft:air")
