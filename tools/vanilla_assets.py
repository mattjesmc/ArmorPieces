"""
Extract the vanilla assets the Blockbench rigs need, out of a copy of the game.

The rigs show a real player wearing real armor, which means they need Mojang's own PNGs: the default
skin, the armor equipment layers, and the trim colour palettes. Those are not ours to redistribute -
the same reason `.modpage/`'s texture cache is gitignored - so nothing here is committed. The cache
is rebuilt on demand from a copy of the game that is already on the machine: the jar Loom fetched
for the build, the launcher's `.minecraft/versions/<v>/<v>.jar`, or any jar or resource pack the
user points this at. Whatever the source, it stays on this machine.

Without a game there is still an editor. The handful of NUMBERS the tools derive from the game's
textures - the sixteen trim ramps, the eight shades per armor material, the item and registry
lists - are baked into `tools/.webcache/` by `--bake` on a machine that has the jar, and every tool
that reads them falls back to that cache when the textures themselves are absent. That is what the
web build ships instead of the textures, and what a desktop clone without a jar runs on. The two
things that really are textures - the figure's skin and armor, and the banner pattern sprites -
have no substitute here: the rig wears the mod's own studio set instead, and the cloth preview asks
for the game.

The version comes from gradle.properties, not from an argument, because the rig has to agree with
the Minecraft the mod is compiled against. A Minecraft bump stays "that block and nothing else".

Usage:
    python tools/vanilla_assets.py               # extract everything the rigs need, from Loom's jar
    python tools/vanilla_assets.py --jar <file>  # ... from this jar, or this resource pack zip
    python tools/vanilla_assets.py --minecraft <dir>   # ... from a .minecraft folder's versions/
    python tools/vanilla_assets.py --from-dir <dir>    # ... from an unpacked resource pack folder
    python tools/vanilla_assets.py --list        # show what would be extracted, and where from
    python tools/vanilla_assets.py --bake        # write tools/.webcache from the extracted assets
    python tools/vanilla_assets.py --status      # what is here: game, cache, version, as JSON
    python tools/vanilla_assets.py --list-items  # print every vanilla item id with its name, as JSON
    python tools/vanilla_assets.py --list-ids    # attribute and mob effect ids, damage-type tags
    python tools/vanilla_assets.py --list-loot-tables  # every loot table id but the block drops
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
# The numbers derived from the game, kept where a clone without the game can read them.
WEBCACHE = ROOT / "tools" / ".webcache"
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


# The banner pattern sprites, which a cloth's design is composited out of. Both sheets, because a
# cloth chooses which one it samples the way `armorpieces:banner` does. Taken by DIRECTORY rather
# than by name: the pattern list is data, a pack may add to it, and a preview that hardcoded the
# vanilla twelve would go stale the first time one was added.
PATTERN_SHEETS = ["banner", "shield"]

# The language prefixes the tools translate through for the `minecraft` namespace: trim material
# names for the fitting options, dye names for the inlay options. Baked so the fallback can name
# things the way the game does without the whole language file coming along.
LANG_PREFIXES = ("trim_material.minecraft.", "color.minecraft.")

# What --bake writes, and what the fallbacks read. Each is one JSON file under tools/.webcache.
BAKED = ("items", "ids", "loot_tables", "lang", "registry", "material_ramps", "skin_ramps")


def minecraft_version(path: Path = GRADLE_PROPERTIES) -> str:
    """The version the mod is built against, read from the one place that declares it."""
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^minecraft_version=(.+)$", text, re.MULTILINE)
    if not match:
        sys.exit(f"error: no minecraft_version in {path}")
    return match.group(1).strip()


def find_jar(version: str) -> Path | None:
    """Locate a client jar for `version` in Loom's cache, or None when there is none.

    Both the plain and the deobfuscated jar carry the same `assets/` tree, so either will do and the
    first one that exists wins. Nothing here reads code out of the jar - only PNGs."""
    candidates = [
        LOOM / version / "minecraft-client.jar",
        LOOM / version / "minecraft-merged.jar",
        LOOM / "minecraftMaven" / "net" / "minecraft" / "minecraft-merged-deobf" / version
        / f"minecraft-merged-deobf-{version}.jar",
        LOOM / "minecraftMaven" / "net" / "minecraft" / "minecraft-clientonly-deobf" / version
        / f"minecraft-clientonly-deobf-{version}.jar",
        LOOM / version / "minecraft-client-only.jar",
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None


def launcher_jar(minecraft_dir: Path, version: str) -> Path | None:
    """The launcher's copy of the game: `versions/<v>/<v>.jar` for the mod's version, else the
    newest version folder that holds a jar. A modded profile's jar (fabric-loader-x-y) carries no
    assets, so only folders whose jar is named for the folder count."""
    versions = minecraft_dir / "versions"
    if not versions.is_dir():
        return None
    exact = versions / version / f"{version}.jar"
    if exact.is_file():
        return exact
    found = [p / f"{p.name}.jar" for p in versions.iterdir() if (p / f"{p.name}.jar").is_file()]
    if not found:
        return None
    return max(found, key=lambda p: p.stat().st_mtime)


class Source:
    """A copy of the game to read from: a jar, a resource pack zip, or an unpacked folder. The
    same `assets/minecraft/...` names either way, so the extraction does not care which."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self._zip = None
        if self.path.is_dir():
            self.kind = "folder"
            self._names = {p.relative_to(self.path).as_posix()
                           for p in self.path.rglob("*") if p.is_file()}
        elif self.path.is_file():
            self.kind = "jar" if self.path.suffix == ".jar" else "zip"
            self._zip = zipfile.ZipFile(self.path)
            self._names = set(self._zip.namelist())
        else:
            sys.exit(f"error: no game at {self.path}")

    @property
    def names(self) -> set[str]:
        return self._names

    def read(self, name: str) -> bytes:
        if self._zip is not None:
            return self._zip.read(name)
        return (self.path / name).read_bytes()

    def close(self) -> None:
        if self._zip is not None:
            self._zip.close()


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

    # The banner and shield pattern sprites are added by `extract`, which can see the jar's own
    # listing and so does not have to know their names. See PATTERN_SHEETS.

    # The language file, for the item list below. Not a texture, but the same rule applies: it is
    # Mojang's, and it is read from the jar rather than copied into the repo.
    out["assets/minecraft/lang/en_us.json"] = "lang/en_us.json"

    return out


def _lang_of(source: Source) -> dict:
    name = "assets/minecraft/lang/en_us.json"
    if name not in source.names:
        return {}
    return json.loads(source.read(name))


def list_items(source: Source) -> dict[str, str]:
    """Every vanilla item id with its English name, for an editor's autocomplete.

    Read from the language file rather than from a registry dump, because the jar has no registry
    dump and the language file names exactly the things a player can hold: `item.minecraft.<id>`
    for items, `block.minecraft.<id>` for blocks, most of which are items too. A few blocks are not
    (a piston head, a fire block) and a recipe naming one would fail to load - the editor treats the
    list as suggestions, not as proof."""
    lang = _lang_of(source)
    items: dict[str, str] = {}
    for prefix in ("item.minecraft.", "block.minecraft."):
        for key, name in lang.items():
            if key.startswith(prefix) and key.count(".") == 2:
                items.setdefault("minecraft:" + key[len(prefix):], name)
    return dict(sorted(items.items()))


def list_ids(source: Source) -> dict:
    """The ids an effect's fields can name, with their English names, for an editor's autocomplete:
    attributes and mob effects from the language file, the way list_items reads items, and the
    damage-type tags from the data the jar carries."""
    lang = _lang_of(source)
    tags = sorted(
        "#minecraft:" + name.rsplit("/", 1)[1][:-5]
        for name in source.names
        if name.startswith("data/minecraft/tags/damage_type/") and name.endswith(".json"))
    attributes, effects = {}, {}
    for key, name in lang.items():
        if key.startswith("attribute.name."):
            attributes["minecraft:" + key[len("attribute.name."):]] = name
        elif key.startswith("effect.minecraft.") and key.count(".") == 2:
            effects["minecraft:" + key[len("effect.minecraft."):]] = name
    return {
        "attribute": dict(sorted(attributes.items())),
        "mob_effect": dict(sorted(effects.items())),
        "damage_type_tags": tags,
    }


def list_loot_tables(source: Source) -> list[str]:
    """Every vanilla loot table id a part could name in its `loot` list, for an editor's
    autocomplete: read off the jar's `data/minecraft/loot_table/` tree. Block drops are left out -
    they are four fifths of the tree and a part in a dirt block's drops is nobody's intention - so
    the list is chests, entities, gameplay tables and the rest. The chest tables come first, since
    they are the ones a part is nearly always for."""
    prefix = "data/minecraft/loot_table/"
    ids = sorted(
        "minecraft:" + name[len(prefix):-5]
        for name in source.names
        if name.startswith(prefix) and name.endswith(".json")
        and not name.startswith(prefix + "blocks/"))
    chests = [i for i in ids if i.startswith("minecraft:chests/")]
    return chests + [i for i in ids if i not in chests]


def extract(source: Source, listing_only: bool = False) -> tuple[int, list[str]]:
    """Copy every wanted entry out of the source. Returns (count, missing entries).

    Missing entries are reported rather than fatal: the armor material list is deliberately generous
    (not every material has a leggings layer in every version), and a rig is still useful without
    one of sixteen palettes. A resource pack that carries only some of it fills in what it has."""
    entries = wanted()
    written, missing = 0, []

    names = source.names
    # The trim-material registry entries and any tags over them, so a tool here can say which
    # materials exist and what a tag means. Enumerated from the jar rather than listed here,
    # because the set is Mojang's to grow. (The client-only jar carries no data/ at all, so the
    # candidates below prefer a jar that does.)
    for name in names:
        if name.endswith(".json") and (name.startswith("data/minecraft/trim_material/")
                                       or name.startswith("data/minecraft/tags/trim_material/")
                                       or name.startswith("data/minecraft/tags/damage_type/")):
            entries[name] = name
    # The banner and shield pattern sprites, enumerated the same way and for the same reason:
    # the pattern list is Mojang's to grow, and a pack may add to it.
    for sheet in PATTERN_SHEETS:
        prefix = f"assets/minecraft/textures/entity/{sheet}/"
        for name in names:
            if name.startswith(prefix) and name.endswith(".png"):
                entries[name] = f"{sheet}/{name[len(prefix):]}"
    for entry, relative in sorted(entries.items()):
        if entry not in names:
            missing.append(entry)
            continue
        if listing_only:
            written += 1
            continue
        target = CACHE / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read(entry))
        written += 1

    return written, missing


# ---- the cache of numbers ----------------------------------------------------------------------

def cached(name: str):
    """One baked answer, or None when it has not been baked."""
    path = WEBCACHE / f"{name}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _registry_from_assets() -> dict | None:
    """The vanilla trim materials and the tags over them, read from the extracted data folder."""
    data = CACHE / "data" / "minecraft"
    if not data.is_dir():
        return None
    materials = sorted("minecraft:" + p.stem for p in (data / "trim_material").glob("*.json"))
    tags: dict[str, dict[str, list]] = {}
    for registry in ("trim_material", "damage_type"):
        folder = data / "tags" / registry
        if not folder.is_dir():
            continue
        tags[registry] = {}
        for path in sorted(folder.glob("*.json")):
            values = json.loads(path.read_text(encoding="utf-8")).get("values", [])
            tags[registry]["minecraft:" + path.stem] = [
                v.get("id") if isinstance(v, dict) else v for v in values]
    return {"trim_material": materials, "tags": tags}


def registry() -> dict:
    """The vanilla registry answers the tools ask: from the extracted data when it is here, else
    from the cache, else empty."""
    return _registry_from_assets() or cached("registry") or {"trim_material": [], "tags": {}}


def vanilla_lang() -> dict:
    """The `minecraft` namespace's English strings: the whole file when the game is here, else the
    baked subset the tools translate through."""
    full = CACHE / "lang" / "en_us.json"
    if full.is_file():
        return json.loads(full.read_text(encoding="utf-8"))
    return cached("lang") or {}


def game_present() -> bool:
    """Whether the extracted textures are here - the figure's, at least, which is what a rig is."""
    return (CACHE / "skin" / "wide_steve.png").is_file() and (CACHE / "armor" / "iron.png").is_file()


def bake(source: Source | None) -> list[Path]:
    """Write every derived answer into tools/.webcache, from the source for the lists and from the
    extracted textures for the ramps. Returns the files written. A source that cannot answer one
    (a resource pack with no language file) leaves that file as it was."""
    WEBCACHE.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    def put(name: str, value) -> None:
        path = WEBCACHE / f"{name}.json"
        path.write_text(json.dumps(value, indent=1) + "\n", encoding="utf-8", newline="\n")
        written.append(path)

    if source is not None:
        lang = _lang_of(source)
        if lang:
            put("items", list_items(source))
            put("ids", list_ids(source))
            put("lang", {k: v for k, v in lang.items() if k.startswith(LANG_PREFIXES)})
        if any(n.startswith("data/minecraft/loot_table/") for n in source.names):
            put("loot_tables", list_loot_tables(source))
    reg = _registry_from_assets()
    if reg is not None:
        put("registry", reg)

    # The ramps are computed by the tools that own the arithmetic, so the cache is by construction
    # what they would have said. Imported here rather than at the top: both of them import this
    # module for the material lists.
    if (CACHE / "palette" / "trim_palette.png").is_file():
        import preview_material
        ramps = {}
        for material in preview_material.MATERIALS:
            if (CACHE / "palette" / f"{material}.png").is_file():
                ramps[material] = preview_material.palette_ramp(
                    CACHE / "palette" / "trim_palette.png", CACHE / "palette" / f"{material}.png")
        put("material_ramps", ramps)
    if (CACHE / "armor" / "iron.png").is_file():
        import bake_skin
        tables = {}
        for material in bake_skin.MATERIALS:
            try:
                tables[material] = bake_skin.table(material)
            except SystemExit:
                continue
        put("skin_ramps", tables)
    return written


def status() -> dict:
    """What this clone has to work with, for a tool or an editor to show."""
    version = minecraft_version() if GRADLE_PROPERTIES.is_file() else ""
    loom = find_jar(version) if version else None
    return {
        "version": version,
        "game": game_present(),
        "patterns": (CACHE / "shield").is_dir() and (CACHE / "banner").is_dir(),
        "palettes": sorted(p.stem for p in (CACHE / "palette").glob("*.png")
                           if p.stem != "trim_palette") if (CACHE / "palette").is_dir() else [],
        "armor": sorted(p.stem for p in (CACHE / "armor").glob("*.png"))
        if (CACHE / "armor").is_dir() else [],
        "cache": sorted(name for name in BAKED if (WEBCACHE / f"{name}.json").is_file()),
        "loom_jar": str(loom) if loom else "",
        "assets": str(CACHE),
    }


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jar", type=Path, metavar="FILE",
                    help="extract from this client jar or resource pack zip instead of Loom's jar")
    ap.add_argument("--minecraft", type=Path, metavar="DIR",
                    help="extract from the launcher's copy of the game under this .minecraft folder")
    ap.add_argument("--from-dir", type=Path, metavar="DIR",
                    help="extract from an unpacked resource pack or asset folder")
    ap.add_argument("--list", action="store_true",
                    help="report what would be extracted without writing anything")
    ap.add_argument("--bake", action="store_true",
                    help="write the derived numbers to tools/.webcache and exit")
    ap.add_argument("--status", action="store_true",
                    help="print what is here - game, palettes, cache - as JSON and exit")
    ap.add_argument("--list-items", action="store_true",
                    help="print every vanilla item id with its display name as JSON and exit")
    ap.add_argument("--list-ids", action="store_true",
                    help="print the attribute and mob effect ids with their names, and the "
                         "damage-type tags, as JSON and exit")
    ap.add_argument("--list-loot-tables", action="store_true",
                    help="print every vanilla loot table id but the block drops, chests first, "
                         "as JSON and exit")
    args = ap.parse_args()

    if args.status:
        print(json.dumps(status(), indent=1))
        return

    version = minecraft_version()
    source: Source | None = None
    if args.jar:
        source = Source(args.jar)
    elif args.minecraft:
        jar = launcher_jar(args.minecraft, version)
        if jar is None:
            sys.exit(f"error: no versions/<v>/<v>.jar under {args.minecraft}. Run the game once "
                     f"from the launcher so it downloads {version}, then try again.")
        source = Source(jar)
    elif args.from_dir:
        source = Source(args.from_dir)
    else:
        jar = find_jar(version)
        if jar is not None:
            source = Source(jar)

    lists = {"items": args.list_items, "ids": args.list_ids, "loot_tables": args.list_loot_tables}
    asked = [name for name, flag in lists.items() if flag]
    if asked:
        name = asked[0]
        able = source is not None and (
            any(n.startswith("data/minecraft/loot_table/") for n in source.names)
            if name == "loot_tables" else bool(_lang_of(source)))
        if able:
            answer = {"items": list_items, "ids": list_ids, "loot_tables": list_loot_tables}[name](source)
        else:
            answer = cached(name)
            if answer is None:
                sys.exit(f"error: no Minecraft {version} client jar in {LOOM} and no baked "
                         f"tools/.webcache/{name}.json. Run a gradle build first, or point this "
                         f"at your game with --jar or --minecraft.")
        print(json.dumps(answer, indent=1))
        return

    if args.bake:
        for path in bake(source):
            print(f"baked {path.relative_to(ROOT).as_posix()}")
        if source is not None:
            source.close()
        return

    if source is None:
        sys.exit(
            f"error: no Minecraft {version} client jar in {LOOM}.\n"
            f"       Run a gradle build first - Loom downloads it as part of one - or point this at\n"
            f"       your own copy: --jar <client.jar>, --minecraft <.minecraft folder>, or\n"
            f"       --from-dir <resource pack folder>.")

    print(f"minecraft {version} <- {source.path}")
    written, missing = extract(source, listing_only=args.list)
    verb = "would extract" if args.list else "extracted"
    print(f"{verb} {written} files -> {CACHE.relative_to(ROOT)}")
    for entry in missing:
        print(f"  missing (skipped): {entry}")
    if not args.list:
        # The numbers follow the textures: a game that has just arrived, or a modded resource pack
        # with its own materials, changes what the tools would say, and the cache says it too.
        for path in bake(source):
            print(f"baked {path.relative_to(ROOT).as_posix()}")
    source.close()


if __name__ == "__main__":
    main()
