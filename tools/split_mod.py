#!/usr/bin/env python3
"""Finish the split: move the mod's own content into three packs and leave the mod as the engine.

    docs/plans/main-pack-split.md, "Finishing the split" (the user, 2026-09-10: "move the remaining
    items out of the mod, and move everything into packs"); docs/plans/compatibility.md section 5.3.

    python tools/split_mod.py --dry-run     # say what would move, touch nothing
    python tools/split_mod.py               # do it

The three surviving themes are the three packs, cut along the mod's own theme tags:

    armorpieces_knightly   packs/knightly   #armorpieces:knightly  + plate, gothic, milanese, mail, chainmail
    armorpieces_court      packs/court      #armorpieces:court     + lamellar, scale
    armorpieces_wayfarer   packs/wayfarer   #armorpieces:wayfarer  + gambeson, brigandine

A piece is its data file (asset_id and translate key rewritten, `armorpieces:<id>` added to
former_ids, the uid DROPPED so `mint_uids.py` issues a fresh one - the project's convention for a
move, because `packs/legacy` restores the old id with the old uid and two files may not share
one), its geometry, its sheets, its template recipe and its lang line. A skin is the same minus geometry. The theme's loot group goes with it, over the
pack's own tag. The four fittings and the two cloths STAY: a fitting's type is code and every pack
names it, and the cloth template item's icons select on `armorpieces:tabard` / `armorpieces:tunic`
in the mod's own item model.

Run `python tools/mint_uids.py` afterwards; `StageCommand.java`'s three mod sets get their
namespaces; `tools/sync_decoration_masters.py` / `sync_skin_masters.py` are told where the art
installs. Idempotent enough to re-run after a `git checkout` of the mod half.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "src/main/resources/data/armorpieces"
ASSETS = REPO / "src/main/resources/assets/armorpieces"
LANG = ASSETS / "lang/en_us.json"
LOCK = REPO / "uids.lock"
STAGE = REPO / "src/main/java/com/mattjesmc/armorpieces/command/StageCommand.java"
TEX_DIR = ASSETS / "textures/entity/decoration"
SKIN_TEX = ASSETS / "textures/entity/skin"
DRY = "--dry-run" in sys.argv

PACKS = {
    "armorpieces_knightly": dict(dir=REPO / "packs/knightly", title="Armor Pieces: Knightly", name="Knightly", theme="knightly"),
    "armorpieces_court": dict(dir=REPO / "packs/court", title="Armor Pieces: Court", name="Court", theme="court"),
    "armorpieces_wayfarer": dict(dir=REPO / "packs/wayfarer", title="Armor Pieces: Wayfarer", name="Wayfarer", theme="wayfarer"),
}


def jload(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def jdump(p: Path, obj) -> None:
    if DRY:
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def move(src: Path, dst: Path) -> None:
    if DRY:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))


def unlink(p: Path) -> None:
    if not DRY:
        p.unlink()


def say(msg: str) -> None:
    print(("would " if DRY else "") + msg)


# ------------------------------------------------------------------ what goes where
owner: dict[str, str] = {}      # piece -> namespace
skin_owner: dict[str, str] = {}
groups: dict[str, dict] = {}
for ns, spec in PACKS.items():
    tag = jload(DATA / "tags/armorpieces/armor_decoration" / f"{spec['theme']}.json")
    for value in tag["values"]:
        owner[value.split(":", 1)[1]] = ns
    group = jload(DATA / "armorpieces/loot_group" / f"{spec['theme']}.json")
    groups[ns] = group
    for skin in group.get("skins", []):
        skin_owner[skin.split(":", 1)[1]] = ns

on_disk = sorted(p.stem for p in (DATA / "armorpieces/armor_decoration").glob("*.json"))
unowned = [p for p in on_disk if p not in owner]
if unowned:
    sys.exit(f"pieces in no theme tag, and so with nowhere to go: {unowned}")
skins_on_disk = sorted(p.stem for p in (DATA / "armorpieces/armor_skin").glob("*.json"))
unowned = [s for s in skins_on_disk if s not in skin_owner]
if unowned:
    sys.exit(f"skins in no loot group, and so with nowhere to go: {unowned}")

# ------------------------------------------------------------------ skeletons
for ns, spec in PACKS.items():
    d = spec["dir"]
    for half, fmt in (("datapack", 107), ("resourcepack", 88)):
        root = d / half
        if not (root / "pack.mcmeta").exists():
            jdump(root / "pack.mcmeta", {
                "pack": {"description": f"{spec['title']} 0.1.0 - the "
                                        f"{'datapack' if half == 'datapack' else 'resource pack'} half. "
                                        f"Requires the Armor Pieces mod, 0.4.0 or later.",
                         "min_format": fmt, "max_format": fmt},
                "armorpieces": {"requires": "0.4.0"}})
        if not (root / "LICENSE").exists() and not DRY:
            root.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / "LICENSE", root / "LICENSE")
        if not (root / "armorpieces-credits.json").exists():
            jdump(root / "armorpieces-credits.json",
                  {"pack": {"author": "mattjes", "license": "ARR", "homepage": "https://armorpieces.com"}})
    say(f"skeleton {d.relative_to(REPO)} ({ns})")

lang = jload(LANG)
pack_lang: dict[str, dict] = {ns: {} for ns in PACKS}


# ------------------------------------------------------------------ pieces
def move_piece(part: str, ns: str) -> None:
    d = PACKS[ns]["dir"]
    dp = d / "datapack/data" / ns
    rp = d / "resourcepack/assets" / ns
    src = DATA / "armorpieces/armor_decoration" / f"{part}.json"
    obj = jload(src)
    obj["asset_id"] = f"{ns}:{part}"
    obj["description"] = {"translate": f"decoration.{ns}.{part}"}
    formers = obj.setdefault("former_ids", [])
    if f"armorpieces:{part}" not in formers:
        formers.append(f"armorpieces:{part}")
    obj.pop("uid", None)  # a move mints anew; the legacy pack keeps the old uid under the old id
    jdump(dp / "armorpieces/armor_decoration" / f"{part}.json", obj)
    unlink(src)
    geo = ASSETS / "armorpieces/decoration" / f"{part}.json"
    if geo.exists():
        move(geo, rp / "armorpieces/decoration" / f"{part}.json")
    pat = re.compile(rf"^{re.escape(part)}(_[a-z0-9_]+)?\.png$")
    n = 0
    for png in sorted(TEX_DIR.glob(f"{part}*.png")):
        if pat.match(png.name):
            move(png, rp / "textures/entity/decoration" / png.name)
            n += 1
    rec = DATA / "recipe" / f"template_{part}.json"
    has_recipe = rec.exists()
    if has_recipe:
        r = jload(rec)
        r["result"]["components"]["armorpieces:decoration"] = f"{ns}:{part}"
        jdump(dp / "recipe" / f"template_{part}.json", r)
        unlink(rec)
    key = f"decoration.armorpieces.{part}"
    pack_lang[ns][f"decoration.{ns}.{part}"] = lang.pop(key, part.replace("_", " ").title())
    say(f"  piece {part:18} -> {ns}  ({n} sheet(s){', recipe' if has_recipe else ''})")


def move_skin(skin: str, ns: str) -> None:
    d = PACKS[ns]["dir"]
    dp = d / "datapack/data" / ns
    rp = d / "resourcepack/assets" / ns
    src = DATA / "armorpieces/armor_skin" / f"{skin}.json"
    obj = jload(src)
    obj["asset_id"] = f"{ns}:{skin}"
    obj["description"] = {"translate": f"skin.{ns}.{skin}"}
    formers = obj.setdefault("former_ids", [])
    if f"armorpieces:{skin}" not in formers:
        formers.append(f"armorpieces:{skin}")
    obj.pop("uid", None)  # a move mints anew; the legacy pack keeps the old uid under the old id
    jdump(dp / "armorpieces/armor_skin" / f"{skin}.json", obj)
    unlink(src)
    if (SKIN_TEX / skin).exists():
        move(SKIN_TEX / skin, rp / "textures/entity/skin" / skin)
    rec = DATA / "recipe" / f"skin_template_{skin}.json"
    if rec.exists():
        r = jload(rec)
        r["result"]["components"]["armorpieces:skin"] = f"{ns}:{skin}"
        jdump(dp / "recipe" / f"skin_template_{skin}.json", r)
        unlink(rec)
    pack_lang[ns][f"skin.{ns}.{skin}"] = lang.pop(f"skin.armorpieces.{skin}", skin.title())
    say(f"  skin  {skin:18} -> {ns}")


for part in on_disk:
    move_piece(part, owner[part])
for skin in skins_on_disk:
    move_skin(skin, skin_owner[skin])

# ------------------------------------------------------------------ tags, loot groups, lang
for ns, spec in PACKS.items():
    d = spec["dir"] / "datapack/data" / ns
    parts = sorted(p for p, o in owner.items() if o == ns)
    jdump(d / "tags/armorpieces/armor_decoration" / f"{spec['theme']}.json",
          {"values": [f"{ns}:{p}" for p in parts]})
    g = dict(groups[ns])
    g["parts"] = f"#{ns}:{spec['theme']}"
    g["skins"] = [f"{ns}:{s.split(':', 1)[1]}" for s in g.get("skins", [])]
    jdump(d / "armorpieces/loot_group" / f"{spec['theme']}.json", g)
    unlink(DATA / "tags/armorpieces/armor_decoration" / f"{spec['theme']}.json")
    unlink(DATA / "armorpieces/loot_group" / f"{spec['theme']}.json")
    f = spec["dir"] / "resourcepack/assets" / ns / "lang/en_us.json"
    existing = jload(f) if f.exists() else {}
    existing.update(pack_lang[ns])
    jdump(f, dict(sorted(existing.items())))
    lang[f"pack.{ns}"] = spec["name"]
    say(f"pack {ns}: tag {spec['theme']} ({len(parts)}), loot group, {len(pack_lang[ns])} lang line(s)")
jdump(LANG, lang)

# ------------------------------------------------------------------ StageCommand: the mod's sets
text = STAGE.read_text(encoding="utf-8")


def namespaced(m: re.Match) -> str:
    name = m.group(2)
    if ":" in name:
        return m.group(0)
    if m.group(1) == "on":
        ns = owner.get(name)
    else:
        ns = skin_owner.get(name)
    return m.group(0) if ns is None else f'{m.group(1)}{m.group(3)}"{ns}:{name}"'


new = re.sub(r'(on|skin)(\(DecorationAnchor\.\w+, |\()"([\w:]+)"',
             lambda m: (m.group(0) if ":" in m.group(3) else
                        (f'{m.group(1)}{m.group(2)}"{(owner if m.group(1) == "on" else skin_owner).get(m.group(3), "armorpieces")}:{m.group(3)}"'
                         if (owner if m.group(1) == "on" else skin_owner).get(m.group(3)) else m.group(0))),
             text)
changed = sum(1 for a, b in zip(text.splitlines(), new.splitlines()) if a != b)
if not DRY:
    STAGE.write_text(new, encoding="utf-8")
say(f"StageCommand.java: {changed} line(s) namespaced")

# ------------------------------------------------------------------ the sync tools
SYNC = REPO / "tools/sync_skin_masters.py"
s = SYNC.read_text(encoding="utf-8")
if 'KNIGHTLY = ' not in s:
    s = s.replace('MOD = _skins_under(ROOT / "src" / "main" / "resources" / "assets", "armorpieces")',
                  'MOD = _skins_under(ROOT / "src" / "main" / "resources" / "assets", "armorpieces")\n'
                  'KNIGHTLY = _skins_under(ROOT / "packs" / "knightly" / "resourcepack" / "assets", "armorpieces_knightly")\n'
                  'COURT = _skins_under(ROOT / "packs" / "court" / "resourcepack" / "assets", "armorpieces_court")\n'
                  'WAYFARER = _skins_under(ROOT / "packs" / "wayfarer" / "resourcepack" / "assets", "armorpieces_wayfarer")')
    for skin, ns in skin_owner.items():
        s = s.replace(f'"{skin}": ("{skin}", MOD)', f'"{skin}": ("{skin}", {PACKS[ns]["theme"].upper()})')
    if not DRY:
        SYNC.write_text(s, encoding="utf-8")
    say("sync_skin_masters.py: the nine skins install into their packs")

print(f"\n{len(on_disk)} piece(s), {len(skins_on_disk)} skin(s) -> three packs" + (" (dry run, nothing touched)" if DRY else ""))
