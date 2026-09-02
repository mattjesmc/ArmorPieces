"""
Extract the vanilla assets the Blockbench rigs need, out of the jar Loom already downloaded.

The rigs show a real player wearing real armor, which means they need Mojang's own PNGs: the default
skin, the armor equipment layers, and the trim colour palettes. Those are not ours to redistribute -
the same reason `.modpage/`'s texture cache is gitignored - so nothing here is committed. The cache
is rebuilt on demand from the copy of the game Loom has already fetched for the build.

The version comes from gradle.properties, not from an argument, because the rig has to agree with
the Minecraft the mod is compiled against. A Minecraft bump stays "that block and nothing else".

Usage:
    python tools/vanilla_assets.py               # extract everything the rigs need
    python tools/vanilla_assets.py --list        # show what would be extracted, and where from
    python tools/vanilla_assets.py --list-items  # print every vanilla item id with its name, as JSON
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "tools" / ".mcassets"
GRADLE_PROPERTIES = ROOT / "gradle.properties"

# Where Loom parks the jars it downloads. The deobfuscated jar is preferred only because it is the
# one guaranteed to exist after a build; both carry an identical `assets/` tree.
LOOM = Path.home() / ".gradle" / "caches" / "fabric-loom"

# The default skin, both arm widths. PlayerModel.createMesh(scale, slim) is one branch per width, so
# a rig that offers the slim body needs the slim skin to go with it.
SKINS = ["wide/steve", "slim/steve"]

# Armor materials that have BOTH an equipment layer and, where relevant, a leggings layer. Leather
# additionally ships an `_overlay` that is tinted by dye at runtime; it is extracted so a leather
# preview can show the undyed shell rather than nothing.
ARMOR_MATERIALS = [
    "leather", "leather_overlay", "chainmail", "iron", "gold", "diamond", "netherite",
    "turtle_scute", "copper",
]

# Trim materials, for the per-material texture preview. `trim_palette` is the KEY that orders every
# other palette - DecorationPalette.of() takes both - so it is not optional.
TRIM_PALETTES = [
    "trim_palette",
    "amethyst", "copper", "diamond", "emerald", "gold", "iron", "lapis", "netherite", "quartz",
    "redstone", "resin",
    "copper_darker", "diamond_darker", "gold_darker", "iron_darker", "netherite_darker",
]


def minecraft_version(path: Path = GRADLE_PROPERTIES) -> str:
    """The version the mod is built against, read from the one place that declares it."""
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^minecraft_version=(.+)$", text, re.MULTILINE)
    if not match:
        sys.exit(f"error: no minecraft_version in {path}")
    return match.group(1).strip()


def find_jar(version: str) -> Path:
    """Locate a client jar for `version` in Loom's cache.

    Both the plain and the deobfuscated jar carry the same `assets/` tree, so either will do and the
    first one that exists wins. Nothing here reads code out of the jar - only PNGs."""
    candidates = [
        LOOM / "minecraftMaven" / "net" / "minecraft" / "minecraft-clientonly-deobf" / version
        / f"minecraft-clientonly-deobf-{version}.jar",
        LOOM / version / "minecraft-client.jar",
        LOOM / version / "minecraft-client-only.jar",
        LOOM / version / "minecraft-merged.jar",
    ]
    for path in candidates:
        if path.is_file():
            return path
    sys.exit(
        f"error: no Minecraft {version} client jar in {LOOM}.\n"
        f"       Run a gradle build first - Loom downloads it as part of one.")


def wanted() -> dict[str, str]:
    """Map of jar entry -> path under the cache, for everything the rigs need."""
    out: dict[str, str] = {}
    base = "assets/minecraft/textures"

    for skin in SKINS:
        out[f"{base}/entity/player/{skin}.png"] = f"skin/{skin.replace('/', '_')}.png"

    for material in ARMOR_MATERIALS:
        out[f"{base}/entity/equipment/humanoid/{material}.png"] = f"armor/{material}.png"
        out[f"{base}/entity/equipment/humanoid_leggings/{material}.png"] = \
            f"armor_leggings/{material}.png"

    for palette in TRIM_PALETTES:
        out[f"{base}/trims/color_palettes/{palette}.png"] = f"palette/{palette}.png"

    # The language file, for the item list below. Not a texture, but the same rule applies: it is
    # Mojang's, and it is read from the jar rather than copied into the repo.
    out["assets/minecraft/lang/en_us.json"] = "lang/en_us.json"

    return out


def list_items(jar_path: Path) -> dict[str, str]:
    """Every vanilla item id with its English name, for an editor's autocomplete.

    Read from the language file rather than from a registry dump, because the jar has no registry
    dump and the language file names exactly the things a player can hold: `item.minecraft.<id>`
    for items, `block.minecraft.<id>` for blocks, most of which are items too. A few blocks are not
    (a piston head, a fire block) and a recipe naming one would fail to load - the editor treats the
    list as suggestions, not as proof."""
    with zipfile.ZipFile(jar_path) as jar:
        lang = json.loads(jar.read("assets/minecraft/lang/en_us.json"))
    items: dict[str, str] = {}
    for prefix in ("item.minecraft.", "block.minecraft."):
        for key, name in lang.items():
            if key.startswith(prefix) and key.count(".") == 2:
                items.setdefault("minecraft:" + key[len(prefix):], name)
    return dict(sorted(items.items()))


def extract(jar_path: Path, listing_only: bool = False) -> tuple[int, list[str]]:
    """Copy every wanted entry out of the jar. Returns (count, missing entries).

    Missing entries are reported rather than fatal: the armor material list is deliberately generous
    (not every material has a leggings layer in every version), and a rig is still useful without
    one of sixteen palettes. A missing SKIN is fatal, because that is the whole point of the rig."""
    entries = wanted()
    written, missing = 0, []

    with zipfile.ZipFile(jar_path) as jar:
        names = set(jar.namelist())
        for entry, relative in sorted(entries.items()):
            if entry not in names:
                missing.append(entry)
                continue
            if listing_only:
                written += 1
                continue
            target = CACHE / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with jar.open(entry) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            written += 1

    fatal = [m for m in missing if "/player/" in m]
    if fatal:
        sys.exit(f"error: the default skin is not in {jar_path.name}: {', '.join(fatal)}")

    return written, missing


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true",
                    help="report what would be extracted without writing anything")
    ap.add_argument("--list-items", action="store_true",
                    help="print every vanilla item id with its display name as JSON and exit")
    args = ap.parse_args()

    version = minecraft_version()
    jar_path = find_jar(version)
    if args.list_items:
        print(json.dumps(list_items(jar_path), indent=1))
        return
    print(f"minecraft {version} <- {jar_path}")

    written, missing = extract(jar_path, listing_only=args.list)
    verb = "would extract" if args.list else "extracted"
    print(f"{verb} {written} files -> {CACHE.relative_to(ROOT)}")
    for entry in missing:
        print(f"  missing (skipped): {entry}")


if __name__ == "__main__":
    main()
