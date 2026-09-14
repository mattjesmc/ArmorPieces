#!/usr/bin/env python3
"""Write the stage sets that dress a PACK's pieces into that pack's `armorpieces-sets.json`.

`StageCommand.java` is the one place a set is typed in; the modpage generator reads the mod's own
sets out of it for the site and SKIPS a set that wears another namespace's pieces, because that set
belongs to the pack and the pack's own file is what the site and the wardrobe read. After the split
of 2026-09-14 the sets of packs under packs/ are such sets (the jar's own three excepted, which
stay the mod's), so this writes them: one file per pack, the set keyed by the namespace most of its
pieces come from (a borrowed socket stays in, with its own pack named, the way the Reef's did).

    python tools/stage_sets_to_packs.py            # write
    python tools/stage_sets_to_packs.py --check    # print what would be written

The values a fitting stores are worked out the way the game does it, from the fitting's kind and
its materials tag - the same walk the modpage generator makes.
"""
import collections
import io
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGE = os.path.join(REPO, "src/main/java/com/mattjesmc/armorpieces/command/StageCommand.java")
LANG = os.path.join(REPO, "src/main/resources/assets/armorpieces/lang/en_us.json")
FITTINGS = os.path.join(REPO, "src/main/resources/data/armorpieces/armorpieces/fitting")
TRIM_TAGS = os.path.join(REPO, "src/main/resources/data/minecraft/tags/trim_material")
ARMOR_ITEM = {"gold": "golden"}
CHECK = "--check" in sys.argv

_SET = re.compile(r'new GallerySet\("(?P<name>\w+)", EquipmentAssets\.(?P<base>\w+), '
                  r'(?:skin\("(?P<skin>[\w:]+)"\)|null),'
                  r'\s*(?:cloth\("(?P<cloth>\w+)", DyeColor\.(?P<colour>\w+)\)|null), List\.of\(')
_SOCKET = re.compile(r'on\(DecorationAnchor\.(?P<anchor>\w+), "(?P<part>[\w:]+)", TrimMaterials\.(?P<material>\w+)'
                     r'(?P<items>(?:,\s*(?:metal|dyed|flag)\((?:TrimMaterials|DyeColor)\.\w+\))*)\)')
_ITEM = re.compile(r'(metal|dyed|flag)\((?:TrimMaterials|DyeColor)\.(\w+)\)')


def load(p):
    return json.load(io.open(p, encoding="utf-8"))


def trim_tag(tag):
    name = tag.lstrip("#").split(":", 1)[1]
    p = os.path.join(TRIM_TAGS, name + ".json")
    if not os.path.exists(p):
        return []
    return [v["id"] if isinstance(v, dict) else v for v in load(p).get("values", [])]


fittings = {}
for f in os.listdir(FITTINGS):
    body = load(os.path.join(FITTINGS, f))
    mats = body.get("materials")
    fittings["armorpieces:" + f[:-5]] = {"kind": str(body.get("type", "")).replace("armorpieces:", ""),
                                          "materials": trim_tag(mats) if isinstance(mats, str) and mats.startswith("#") else []}


def accepts(fit, kind, value):
    if kind == "metal" and fit["kind"] == "material":
        m = f"minecraft:{value.lower()}"
        return m if m in fit["materials"] else None
    if kind == "dyed" and fit["kind"] == "dye":
        return value.lower()
    if kind == "flag" and fit["kind"] == "banner":
        return {"base": value.lower(), "patterns": []}
    return None


# every pack piece by id, and which folder its namespace lives in
pieces, folder_of = {}, {}
for pack in os.listdir(os.path.join(REPO, "packs")):
    dd = os.path.join(REPO, "packs", pack, "datapack", "data")
    if not os.path.isdir(dd):
        continue
    for ns in os.listdir(dd):
        folder_of[ns] = pack
        dec = os.path.join(dd, ns, "armorpieces", "armor_decoration")
        if os.path.isdir(dec):
            for f in os.listdir(dec):
                pieces[f"{ns}:{f[:-5]}"] = load(os.path.join(dec, f))

text = io.open(STAGE, encoding="utf-8").read()
lang = load(LANG)
found = list(_SET.finditer(text))
per_pack = collections.defaultdict(list)
for i, m in enumerate(found):
    end = found[i + 1].start() if i + 1 < len(found) else len(text)
    block = text[m.end():end]
    before = text[:m.start()].rstrip()
    notes = []
    for line in reversed(before.splitlines()):
        s = line.strip()
        if s.startswith("//"):
            notes.insert(0, s[2:].strip())
        else:
            break
    name = m.group("name")
    armor = m.group("base").lower()
    out = {}
    for sock in _SOCKET.finditer(block):
        part = sock.group("part")
        pid = part if ":" in part else "armorpieces:" + part
        if pid not in pieces:
            print(f"  set {name}: no piece {pid}", file=sys.stderr)
            continue
        ns = pid.split(":")[0]
        piece = {"id": pid, "pack": ns.replace("_", "-"), "material": sock.group("material").lower()}
        vals = {}
        declared = [f for f in pieces[pid].get("fittings", []) if isinstance(f, str)]
        for kind, value in _ITEM.findall(sock.group("items")):
            for fid in declared:
                stored = accepts(fittings[fid], kind, value) if fid in fittings else None
                if stored is not None:
                    vals[fid] = stored
                    break
        if vals:
            piece["fittings"] = vals
        out[sock.group("anchor").lower()] = piece
    namespaces = collections.Counter(p["id"].split(":")[0] for p in out.values())
    if not namespaces:
        continue
    ns = namespaces.most_common(1)[0][0]
    # The jar's own three (knightly, court, wayfarer) are the mod's sets still: the modpage
    # generator lists them from the Java for the mod's page and the site, so a pack file for them
    # would list each twice.
    if ns in ("armorpieces", "armorpieces_knightly", "armorpieces_court", "armorpieces_wayfarer") or ns not in folder_of:
        continue
    title = lang.get(f"commands.armorpieces.stage.set.{name}", name.replace("_", " ").title())
    entry = {"id": name, "title": title, "description": " ".join(notes),
             "set": {"name": title,
                     "slots": {s: {"material": ARMOR_ITEM.get(armor, armor)} for s in ("helmet", "chestplate", "leggings", "boots")},
                     "pieces": out}}
    if m.group("skin"):
        entry["set"]["skin"] = m.group("skin") if ":" in m.group("skin") else "armorpieces:" + m.group("skin")
    if m.group("cloth"):
        entry["set"]["cloth"] = {"cloth": "armorpieces:" + m.group("cloth"), "base": m.group("colour").lower(), "patterns": []}
    per_pack[folder_of[ns]].append(entry)

for pack, entries in per_pack.items():
    path = os.path.join(REPO, "packs", pack, "datapack", "armorpieces-sets.json")
    doc = load(path) if os.path.exists(path) else {"sets": []}
    have = {s["id"].replace("-", "_"): i for i, s in enumerate(doc["sets"])}
    # A set the pack already declares is the pack's, with its own curated description: kept as is.
    # Only a set the file lacks is added, from the Java.
    entries = [e for e in entries if e["id"] not in have]
    doc["sets"].extend(entries)
    print(f"{pack}: {[e['id'] for e in entries]} -> {os.path.relpath(path, REPO)}")
    if not CHECK:
        io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
