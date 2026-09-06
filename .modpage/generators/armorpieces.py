"""
Armor Pieces' own generators: the mod's data, read where it lives.

Every number on a page and in the wiki used to be typed out, in several places, and every release
one of them drifted - "ninety-one parts" is in modpage.yml twice, in the wiki, in the library
index's description and in the CHANGELOG, and the socket list is prose in one place, a table in
another and a hardcoded array in the site's TypeScript. This module is where those facts come
from now: the enum, the datapack folders and the language file, which are the files the GAME
reads, so a page cannot say something the mod does not do.

These are the game hooks ModPageConstructor deliberately does not generalise. `mc.lang` and
`data.file` are its, because every mod has a language file and a data folder; "a socket is an
enum constant in DecorationAnchor.java" is ours, and belongs here.

Registered by ModPageConstructor at build time - it imports every .modpage/generators/*.py - so
`modpage generators` lists them and `{from: <name>}` in modpage.yml uses them.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from modpage.generators import Context, generator

# Where the mod keeps the things a page talks about. One place, so a folder that moves is one
# edit here rather than eight silent empties.
RESOURCES = "src/main/resources"
DATA = f"{RESOURCES}/data/armorpieces/armorpieces"
LANG = f"{RESOURCES}/assets/armorpieces/lang/en_us.json"
ANCHOR_SRC = "src/main/java/com/mattjesmc/armorpieces/decoration/DecorationAnchor.java"
EFFECTS_SRC = "src/main/java/com/mattjesmc/armorpieces/decoration/effect/DecorationEffects.java"

# The registries, and what a page calls each one. `lang` is the key prefix the game gives that
# registry's entries, which is how an id becomes a name.
KINDS = {
    "piece": {"dir": "armor_decoration", "lang": "decoration", "plural": "pieces"},
    "skin": {"dir": "armor_skin", "lang": "skin", "plural": "skins"},
    "cloth": {"dir": "cloth", "lang": "cloth", "plural": "cloths"},
}


# ---- reading the repository ---------------------------------------------------------------------

def _lang(ctx: Context) -> dict[str, str]:
    loaded = ctx.load_data(LANG)
    return {str(k): str(v) for k, v in loaded.items()} if isinstance(loaded, dict) else {}


def _entries(ctx: Context, kind: str) -> list[dict[str, Any]]:
    """Every JSON file in one registry folder, with its id and its display name."""
    spec = KINDS[kind]
    lines = _lang(ctx)
    out: list[dict[str, Any]] = []
    for path in sorted((ctx.root / DATA / spec["dir"]).glob("*.json")):
        try:
            body = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as error:
            ctx.warn(f"{path.name}: {error}")
            continue
        name = path.stem
        key = f"{spec['lang']}.armorpieces.{name}"
        description = body.get("description")
        if isinstance(description, dict) and isinstance(description.get("translate"), str):
            key = description["translate"]
        out.append({
            "id": f"armorpieces:{name}",
            "name": name,
            "kind": kind,
            "title": lines.get(key, name.replace("_", " ").title()),
            "key": key,
            "body": body,
        })
    if not out:
        ctx.warn(f"nothing under {DATA}/{spec['dir']}")
    return out


def _recipe_exists(ctx: Context, prefix: str, name: str) -> bool:
    return (ctx.root / RESOURCES / "data" / "armorpieces" / "recipe" / f"{prefix}{name}.json").is_file()


def _anchor_table(ctx: Context) -> list[dict[str, Any]]:
    """The socket table, parsed out of the enum.

    tools/bb_rig.py parses the same file with the same expression, and for the same reason: an
    offset tuned in the game must not need a second edit anywhere. This reads less of it - a page
    wants the name, the armor slot and whether the socket is a mirrored pair, not the offsets.
    """
    source = ctx.root / ANCHOR_SRC
    if not source.is_file():
        ctx.warn(f"no {ANCHOR_SRC}")
        return []
    text = source.read_text(encoding="utf-8")
    header = re.compile(r'^ {4}([A-Z][A-Z_]*)\("([a-z_]+)",\s*ArmorType\.([A-Z_]+),', re.MULTILINE)
    attach = re.compile(r'Attachment\.(of|mirrored)\(HumanoidPart\.([A-Z_]+),')
    lines = _lang(ctx)

    found = list(header.finditer(text))
    out: list[dict[str, Any]] = []
    for index, match in enumerate(found):
        end = found[index + 1].start() if index + 1 < len(found) else len(text)
        block = text[match.start():end]
        attachments = attach.findall(block)
        # The javadoc immediately above the constant is what the socket is FOR, in the words of
        # whoever wrote it. One sentence of it is what a table wants.
        #
        # It has to be the LAST block comment before the constant, with nothing but whitespace
        # between the two: the class's own javadoc is the last comment before the FIRST constant,
        # and a lazier match hands that to all twelve.
        before = text[:match.start()]
        doc = re.search(r"/\*\*((?:(?!\*/)[\s\S])*)\*/[ \t\r\n]*\Z", before)
        blurb = ""
        if doc:
            blurb = " ".join(line.strip(" *") for line in doc.group(1).splitlines()).strip()
            blurb = re.sub(r"\{@link [^}]*?([\w.#]+)\}", r"\1", blurb)
            blurb = re.sub(r"</?\w+>", "", blurb).split(". ")[0].strip(" .")
        name = match.group(2)
        out.append({
            "id": name,
            "name": name,
            "title": lines.get(f"anchor.armorpieces.{name}", name.replace("_", " ").title()),
            "slot": match.group(3).lower(),
            "bone": attachments[0][1].lower() if attachments else "",
            "pair": any(kind == "mirrored" for kind, _ in attachments),
            "description": blurb,
        })
    return out


# ---- the generators -----------------------------------------------------------------------------

@generator("armorpieces.sockets")
def sockets(ctx: Context) -> list[dict[str, Any]]:
    """The twelve sockets, from DecorationAnchor.java: name, armor slot, whether it is a pair."""
    table = _anchor_table(ctx)
    by_socket: dict[str, int] = {}
    for entry in _entries(ctx, "piece"):
        for anchor in entry["body"].get("anchors") or []:
            if isinstance(anchor, str):
                by_socket[anchor] = by_socket.get(anchor, 0) + 1
    for row in table:
        row["count"] = by_socket.get(row["id"], 0)
        # What a table's second column says when nothing else is given.
        row["value"] = f"{row['count']} pieces"
    return table


@generator("armorpieces.pieces")
def pieces(ctx: Context) -> list[dict[str, Any]]:
    """Every piece: its socket, its fittings, whether it is craftable and whether it is found."""
    out = []
    for entry in _entries(ctx, "piece"):
        body = entry.pop("body")
        anchors = [a for a in (body.get("anchors") or []) if isinstance(a, str)]
        out.append({
            **entry,
            "anchor": anchors[0] if anchors else "",
            "anchors": anchors,
            "fittings": [f for f in (body.get("fittings") or []) if isinstance(f, str)],
            "effects": len(body.get("effects") or []),
            "loot": bool(body.get("loot")),
            "craftable": _recipe_exists(ctx, "template_", entry["name"]),
            "description": ", ".join(anchors) or "",
        })
    return out


@generator("armorpieces.skins")
def skins(ctx: Context) -> list[dict[str, Any]]:
    """Every armor skin: what the plate itself is made of, rather than what is bolted to it."""
    out = []
    for entry in _entries(ctx, "skin"):
        body = entry.pop("body")
        out.append({**entry, "loot": bool(body.get("loot")),
                    "craftable": _recipe_exists(ctx, "skin_template_", entry["name"]),
                    "description": ""})
    return out


@generator("armorpieces.cloths")
def cloths(ctx: Context) -> list[dict[str, Any]]:
    """Every cloth: a garment worn over the chest, carrying a banner's design."""
    out = []
    for entry in _entries(ctx, "cloth"):
        body = entry.pop("body")
        out.append({**entry, "sheet": body.get("sheet", ""), "loot": bool(body.get("loot")),
                    "craftable": _recipe_exists(ctx, "cloth_template_", entry["name"]),
                    "description": f"drawn on the {body.get('sheet', 'shield')} net"})
    return out


@generator("armorpieces.fittings")
def fittings(ctx: Context) -> list[dict[str, Any]]:
    """Every fitting: a piece's second colour, set separately at the smithing table."""
    lines = _lang(ctx)
    out = []
    for path in sorted((ctx.root / DATA / "fitting").glob("*.json")):
        try:
            body = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as error:
            ctx.warn(f"{path.name}: {error}")
            continue
        name = path.stem
        key = f"fitting.armorpieces.{name}"
        description = body.get("description")
        if isinstance(description, dict) and isinstance(description.get("translate"), str):
            key = description["translate"]
        # Which pieces declare it - a fitting nothing uses is a fitting that does nothing.
        used = [e["id"] for e in _entries(ctx, "piece")
                if f"armorpieces:{name}" in (e["body"].get("fittings") or [])]
        out.append({
            "id": f"armorpieces:{name}", "name": name,
            "title": lines.get(key, name.replace("_", " ").title()),
            "type": None,  # not a typed ELEMENT; the fitting's own kind is `kind` below
            "kind": str(body.get("type", "")).replace("armorpieces:", ""),
            "ingredients": lines.get(f"{key}.ingredients", ""),
            "pieces": used, "count": len(used),
            "description": lines.get(f"{key}.ingredients", ""),
        })
    if not out:
        ctx.warn(f"nothing under {DATA}/fitting")
    return out


@generator("armorpieces.loot_groups")
def loot_groups(ctx: Context) -> list[dict[str, Any]]:
    """Every loot group: a theme, the chests it turns up in, and what belongs to it."""
    lines = _lang(ctx)
    out = []
    for path in sorted((ctx.root / DATA / "loot_group").glob("*.json")):
        try:
            body = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as error:
            ctx.warn(f"{path.name}: {error}")
            continue
        name = path.stem
        # `parts:` names a tag; its members are the group's pieces.
        members: list[str] = []
        tag = body.get("parts")
        if isinstance(tag, str) and tag.startswith("#"):
            namespace, _, tag_name = tag[1:].partition(":")
            tag_path = (ctx.root / RESOURCES / "data" / namespace / "tags"
                        / "armorpieces" / "armor_decoration" / f"{tag_name}.json")
            if tag_path.is_file():
                try:
                    values = json.loads(tag_path.read_text(encoding="utf-8")).get("values") or []
                    members = [v.get("id") if isinstance(v, dict) else str(v) for v in values]
                except ValueError:
                    pass
        tables = [str(t) for t in (body.get("tables") or [])]
        out.append({
            "id": f"armorpieces:{name}", "name": name,
            "title": lines.get(f"loot_group.armorpieces.{name}", name.replace("_", " ").title()),
            "chance": body.get("chance"),
            "tables": tables,
            "skins": [str(s) for s in (body.get("skins") or [])],
            "pieces": members,
            "count": len(members),
            "description": ", ".join(t.replace("minecraft:chests/", "") for t in tables),
        })
    if not out:
        ctx.warn(f"nothing under {DATA}/loot_group")
    return out


@generator("armorpieces.effect_types")
def effect_types(ctx: Context) -> list[dict[str, Any]]:
    """The effect types a piece may carry, from the registry that declares them."""
    source = ctx.root / EFFECTS_SRC
    if not source.is_file():
        ctx.warn(f"no {EFFECTS_SRC}")
        return []
    text = source.read_text(encoding="utf-8")
    out = []
    for match in re.finditer(r'register\(\s*"([a-z_]+)"', text):
        name = match.group(1)
        out.append({"id": f"armorpieces:{name}", "name": name,
                    "title": name.replace("_", " ").title(), "description": ""})
    if not out:
        ctx.warn(f"no effect types found in {EFFECTS_SRC}")
    return out


@generator("armorpieces.counts")
def counts(ctx: Context) -> list[dict[str, Any]]:
    """The derived numbers a page states, counted rather than remembered.

    One element per fact, each with `id`, `value` (the number) and `text` (the number as a page
    would write it), so a sentence can reference exactly one of them.
    """
    piece_list = pieces(ctx)
    socket_list = sockets(ctx)
    per_socket = [row["count"] for row in socket_list if row["count"]]
    facts = [
        ("pieces", len(piece_list), "the pieces, over every socket"),
        ("skins", len(skins(ctx)), "the armor skins"),
        ("cloths", len(cloths(ctx)), "the cloths"),
        ("fittings", len(fittings(ctx)), "the fittings"),
        ("sockets", len(socket_list), "the sockets a piece can hang on"),
        ("loot_groups", len(loot_groups(ctx)), "the loot groups"),
        ("effect_types", len(effect_types(ctx)), "the effect types a piece may carry"),
        ("craftable", sum(1 for p in piece_list if p["craftable"]),
         "the pieces with a template recipe; the rest are found"),
        ("least_per_socket", min(per_socket) if per_socket else 0,
         "the fewest pieces any socket has to choose from"),
    ]
    return [{"id": key, "name": key, "title": WORDS.get(value, str(value)), "value": value,
             "text": str(value), "word": WORDS.get(value, str(value)), "description": blurb}
            for key, value, blurb in facts]


# Small numbers read as words in prose and as digits in a table; a page picks with `.word` or
# `.value`. Only as far as a count here plausibly goes.
WORDS = {
    0: "none", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
    8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen",
    15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen", 20: "twenty",
}
