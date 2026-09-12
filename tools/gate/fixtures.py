"""The datapack a tier-2 run needs to be there BEFORE the world loads.

Most of what a scenario needs can be pushed into the running game: a loot table, a recipe, a tag are
all read on `/reload`. **A registry entry is not.** A part, a fitting, a skin, a cloth and a loot
group live in datapack REGISTRIES, and vanilla reads those exactly once, when the world loads - so a
part pushed into a running server is a file nobody will ever read, and a scenario that expects one
fails in a way that looks like the mod's fault.

So the fixtures live in a real datapack directory in the server's world folder, written before the
server is started and deleted after it stops. Two packs, because they want different things:

  `armorpieces_gate`          content a scenario asserts ON: a part with a measurable effect, and a
                              loot group naming a tag nothing defines - which is the 0.4.0 trap
                              (an eagerly bound tag takes its whole loot table down) as a fixture.
  `armorpieces_gate_refusal`  content the mod must REFUSE: a wearer condition over a glider.
  `armorpieces_gate_missing_tag`
                              a loot group naming a tag no installed pack defines - the cross-pack
                              case the whole pack line rests on.
  `armorpieces_gate_broken`   a pack an author got wrong five different ways at once, including one
                              file that is not JSON at all. Everything in it has to be warned about
                              and worked around or skipped, and the world has to open - see
                              docs/plans/pack-mistakes.md.

The last two are packs of their own and are booted on their own, because content that is refused
takes the pack it is in down with it: put beside the fixtures above, one bad file would make every
other scenario fail for a reason that has nothing to do with it.

Nothing here writes into `src/` or into `packs/`: a fixture is not content, and the day one of these
files ships is the day the gate tests itself instead of the mod.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

GOOD = "armorpieces_gate"
REFUSAL = "armorpieces_gate_refusal"
MISSING_TAG = "armorpieces_gate_missing_tag"
BROKEN = "armorpieces_gate_broken"

#: The namespace every fixture is in, so that a stray one is obvious in any listing.
NAMESPACE = "gate"

#: What the attribute fixture adds, in half-hearts of armor. Asserted exactly.
ARMOR_BONUS = 4.0


def world(run: Path | None = None) -> Path:
    """The dedicated server's world folder, read from its own settings rather than guessed."""
    run = run or ROOT / "run"
    name = "world"
    properties = run / "server.properties"
    if properties.is_file():
        for line in properties.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("level-name="):
                name = line.split("=", 1)[1].strip()
    return run / name


def pack_format() -> int:
    """The datapack format this mod builds against, out of gradle.properties - one source, not two."""
    for line in (ROOT / "gradle.properties").read_text(encoding="utf-8").splitlines():
        if line.startswith("datapack_format="):
            return int(line.split("=", 1)[1].strip())
    raise RuntimeError("gradle.properties has no datapack_format")


def files(kind: str) -> dict[str, dict]:
    """The fixture files of one pack, by pack-relative path."""
    if kind == GOOD:
        return {
            # A part whose whole reason to exist is that its effect can be MEASURED: four points of
            # armor, added, so the wearer's attribute says a number a test can subtract.
            f"data/{NAMESPACE}/armorpieces/armor_decoration/measured.json": {
                "asset_id": "armorpieces:pinions",
                "description": {"translate": "decoration.armorpieces.pinions"},
                "anchors": ["back"],
                "effects": [{
                    "type": "armorpieces:attribute",
                    "id": f"{NAMESPACE}:measured",
                    "attribute": "minecraft:armor",
                    "amount": ARMOR_BONUS,
                    "operation": "add_value",
                }],
            },
        }
    if kind == MISSING_TAG:
        return {
            # A group that names a tag no pack defines - which is what every pack in the line does
            # the day a player installs one of them and not the others. The claim under test is the
            # one MemberSet was written for: an unresolved tag is an empty set, not a broken world.
            f"data/{NAMESPACE}/armorpieces/loot_group/absent.json": {
                "chance": 0.5,
                "tables": ["minecraft:chests/simple_dungeon"],
                "parts": f"#{NAMESPACE}:nothing_defines_this",
            },
        }
    if kind == REFUSAL:
        return {
            # Refused when the pack loads: gliding is asked on the client too, where an entity
            # predicate cannot be evaluated, so a wearer condition may not gate a glider.
            f"data/{NAMESPACE}/armorpieces/armor_decoration/refused.json": {
                "asset_id": "armorpieces:pinions",
                "description": {"translate": "decoration.armorpieces.pinions"},
                "anchors": ["back"],
                "effects": [{
                    "type": "armorpieces:if_wearer",
                    "if": {"equipment": {"mainhand": {}}},
                    "then": {"type": "armorpieces:glide"},
                }],
            },
        }
    if kind == BROKEN:
        parts = f"data/{NAMESPACE}/armorpieces/armor_decoration"
        return {
            # Not JSON at all. Vanilla files this as an element that failed to parse, and a failed
            # element takes the whole registry - and so the world - down with it. It has to cost
            # itself and nothing else.
            f"{parts}/markup.json": '{ "asset_id": "armorpieces:pinions", ',
            # A socket that does not exist beside one that does: the real one has to survive.
            f"{parts}/socket.json": {
                "asset_id": "armorpieces:brooch",
                "description": {"translate": "decoration.armorpieces.brooch"},
                "anchors": ["collar", "nose"],
            },
            # No name at all. The part is named by its own id and still works.
            f"{parts}/nameless.json": {
                "asset_id": "armorpieces:brooch",
                "anchors": ["collar"],
            },
            # A fitting nothing defines. Resolved at the END of the load, when the fitting registry
            # freezes, which is why it needs a stand-in rather than a dropped field.
            f"{parts}/dangling.json": {
                "asset_id": "armorpieces:brooch",
                "description": {"translate": "decoration.armorpieces.brooch"},
                "anchors": ["collar"],
                "fittings": [f"{NAMESPACE}:no_such_fitting"],
            },
            # A loot table no pack defines: legal, loaded, and the part will never be found.
            f"{parts}/nowhere.json": {
                "asset_id": "armorpieces:brooch",
                "description": {"translate": "decoration.armorpieces.brooch"},
                "anchors": ["collar"],
                "loot": [{"table": "minecraft:chests/no_such_table", "chance": 0.5}],
            },
            # And one file with nothing wrong with it, in the same pack as all of that. If this one
            # is missing afterwards, a mistake cost its neighbours, which is the whole failure.
            f"{parts}/fine.json": {
                "asset_id": "armorpieces:brooch",
                "description": {"translate": "decoration.armorpieces.brooch"},
                "anchors": ["collar"],
            },
        }
    raise ValueError(kind)


def install(kind: str, run: Path | None = None) -> Path:
    """Write one fixture pack into the world. Returns the pack directory."""
    directory = world(run) / "datapacks" / kind
    remove(kind, run)
    directory.mkdir(parents=True, exist_ok=True)
    # All three of pack_format, min_format and max_format: this game version reads the range and
    # falls back with a warning on a pack that declares only the old field.
    version = pack_format()
    (directory / "pack.mcmeta").write_text(json.dumps({
        "pack": {
            "description": f"Armor Pieces gate fixtures ({kind})",
            "pack_format": version,
            "min_format": version,
            "max_format": version,
        }
    }, indent=2), encoding="utf-8")
    for path, content in files(kind).items():
        target = directory / path
        target.parent.mkdir(parents=True, exist_ok=True)
        # A str is written verbatim: a fixture whose whole point is that it is not valid JSON
        # cannot be expressed as a dict and dumped.
        target.write_text(content if isinstance(content, str) else json.dumps(content, indent=2),
                          encoding="utf-8")
    return directory


def remove(kind: str, run: Path | None = None) -> None:
    """Take a fixture pack away again. Safe to call when it was never installed."""
    shutil.rmtree(world(run) / "datapacks" / kind, ignore_errors=True)


def installed(run: Path | None = None) -> list[str]:
    """Which fixture packs are in the world right now - the check a run makes before it trusts one."""
    return [kind for kind in (GOOD, REFUSAL, MISSING_TAG, BROKEN)
            if (world(run) / "datapacks" / kind).is_dir()]
