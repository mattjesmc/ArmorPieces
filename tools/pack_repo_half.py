#!/usr/bin/env python3
"""The repo half of a batch-built pack: for every piece a session has SAVED into the pack, make sure
the lang line and the loot-tag entry are there, and say what is still missing. Idempotent; run
after each batch (RUNNING.md, "what is still owed when the last session exits").

    python tools/pack_repo_half.py samurai daimyo            # do it
    python tools/pack_repo_half.py samurai daimyo --check    # only report

The pack folder is under packs/, the tag is the pack's own loot tag (the one its loot group names).
Titles come from the piece's data file where the plugin wrote one, else from the id.
"""
import glob
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(p):
    return json.load(io.open(p, encoding="utf-8"))


def dump(p, d):
    io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")


def main(pack, tag, check):
    pdir = os.path.join(REPO, "packs", pack)
    nss = [d for d in os.listdir(os.path.join(pdir, "datapack", "data")) if d.startswith("armorpieces")]
    ns = nss[0]
    dec_dir = os.path.join(pdir, "datapack", "data", ns, "armorpieces", "armor_decoration")
    lang_p = os.path.join(pdir, "resourcepack", "assets", ns, "lang", "en_us.json")
    tag_p = os.path.join(pdir, "datapack", "data", ns, "tags", "armorpieces", "armor_decoration", tag + ".json")
    lang = load(lang_p) if os.path.exists(lang_p) else {}
    tagd = load(tag_p) if os.path.exists(tag_p) else {"values": []}
    pieces = sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(dec_dir, "*.json")))
    for piece in pieces:
        d = load(os.path.join(dec_dir, piece + ".json"))
        problems = []
        geo = os.path.join(pdir, "resourcepack", "assets", ns, "armorpieces", "decoration", piece + ".json")
        if not os.path.exists(geo):
            problems.append("no geometry")
        else:
            g = load(geo)
            n = sum(len(b.get("cubes", [])) for b in g.get("bones", [])) if isinstance(g, dict) else 0
            if n == 0:
                problems.append("geometry has no cubes")
        tex = glob.glob(os.path.join(pdir, "resourcepack", "assets", ns, "textures", "**", piece + ".png"), recursive=True)
        if not tex:
            problems.append("no master texture")
        if "fittings" not in d:
            problems.append("no fittings field")
        key = f"decoration.{ns}.{piece}"
        if key not in lang:
            problems.append("lang line missing" + ("" if check else " -> added"))
            if not check:
                lang[key] = piece.replace("_", " ").title()
        rid = f"{ns}:{piece}"
        if rid not in tagd["values"]:
            problems.append("tag entry missing" + ("" if check else " -> added"))
            if not check:
                tagd["values"].append(rid)
        if not os.path.exists(os.path.join(pdir, "datapack", "data", ns, "recipe", f"template_{piece}.json")):
            problems.append("no recipe")
        print(f"  {piece:<20} {'; '.join(problems) or 'ok'}")
    if not check:
        tagd["values"] = sorted(set(tagd["values"]))
        dump(tag_p, tagd)
        dump(lang_p, dict(sorted(lang.items())))
    print(f"{pack}: {len(pieces)} piece(s) on disk, tag {tag} holds {len(tagd['values'])}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args[0], args[1], "--check" in sys.argv)
