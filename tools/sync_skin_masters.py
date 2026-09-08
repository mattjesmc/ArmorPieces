"""
Install an authored skin's master pair into the mod's resources.

A skin is two greyscale sheets and nothing else - `humanoid` and `humanoid_leggings`, 64x32 each, on
the vanilla armor grid - and the mod colours them per material at load time, through a ramp taken
from that material's own vanilla texture. So there is nothing to generate here, exactly as there is
nothing to generate for a part any more: the whole job is to copy the pair from the authoring
directory to the one the mod loads from, and to run the same check the authoring bridge runs before
it lets a skin be saved.

    tools/skin_masters/<skin>/humanoid.png           the body sheet
    tools/skin_masters/<skin>/humanoid_leggings.png  the leggings sheet
        ->  assets/<namespace>/textures/entity/skin/<name>/{humanoid,humanoid_leggings}.png

The namespace is the mod's for a skin the mod ships and the pack's for one a pack ships - five of
the fourteen went to Armor Pieces: Legends in the split. The masters do not move with them: this is
where a skin is DRAWN, and `tools/skin_masters/` stays the one authoring directory.

The installed NAME may differ from the authoring directory's, which is what `--as` is for: a skin
drawn twice under two working names ships under one.

Usage:
    python tools/sync_skin_masters.py plate
    python tools/sync_skin_masters.py gothic_strict --as gothic
    python tools/sync_skin_masters.py                    # every skin the mod ships
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from pathlib import Path

import check_skin
import skin_sheets
from skin_sheets import MASTERS, SHEETS, load_pair

ROOT = skin_sheets.ROOT
def _skins_under(assets: Path, namespace: str) -> Path:
    return assets / namespace / "textures" / "entity" / "skin"


MOD = _skins_under(ROOT / "src" / "main" / "resources" / "assets", "armorpieces")
LEGENDS = _skins_under(ROOT / "packs" / "legends" / "resourcepack" / "assets", "armorpieces_legends")

# What ships, under what name, and into whose resources: the authoring directory on the left, the
# skin's id and the assets root it installs into on the right. `gothic` is drawn twice - once
# freehand and once pinned to vanilla's own silhouette - and only the later one ships.
#
# The mod keeps the nine that say how armor is MADE. The five that say who WORE it went to
# Armor Pieces: Legends, and install into that pack instead.
SHIPPED = {
    "plate": ("plate", MOD),
    "chainmail": ("chainmail", MOD),
    "mail": ("mail", MOD),
    "gambeson": ("gambeson", MOD),
    "gothic": ("gothic", MOD),
    "milanese": ("milanese", MOD),
    "brigandine": ("brigandine", MOD),
    "scale": ("scale", MOD),
    "lamellar": ("lamellar", MOD),
    "lorica": ("lorica", LEGENDS),
    "varangian": ("varangian", LEGENDS),
    "hoplite": ("hoplite", LEGENDS),
    "samurai": ("samurai", LEGENDS),
    "runic": ("runic", LEGENDS),
}


def install(skin: str, name: str, out: Path) -> list[str]:
    """Copy one skin's pair into the resources, and return whatever the check has to say about it."""
    paths = skin_sheets.pair_paths(skin)
    missing = [sheet for sheet in SHEETS if not paths[sheet].is_file()]
    if missing:
        sys.exit(f"{skin}: no {', '.join(missing)} under {MASTERS / skin}")

    report = check_skin.analyse(load_pair(skin), skin)
    target = out / name
    target.mkdir(parents=True, exist_ok=True)
    for sheet in SHEETS:
        shutil.copy2(paths[sheet], target / f"{sheet}.png")
    print(f"{skin} -> {name}: installed {len(SHEETS)} sheet(s) to {target.relative_to(ROOT)}")
    return report.get("problems", []) + report.get("notes", [])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("skin", nargs="?", help="a skin under tools/skin_masters")
    parser.add_argument("--as", dest="name", help="the id to install it under (default: its own)")
    args = parser.parse_args()

    if args.skin:
        name, out = SHIPPED.get(args.skin, (args.skin, MOD))
        wanted = {args.skin: (args.name or name, out)}
    elif args.name:
        sys.exit("--as needs a skin to rename")
    else:
        wanted = SHIPPED

    for skin, (name, out) in wanted.items():
        for line in install(skin, name, out):
            print(f"  {line}")


if __name__ == "__main__":
    main()
