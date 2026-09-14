"""The four culture packs' outfits: armorpieces-sets.json per pack (what the site and the wardrobe
read) and the StageCommand.java transcription (so /armorpieces stage set can dress them), both
from the same piece table the briefs came from."""
import io, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_cultures as g

# pack -> (set id, title, armor item material, skin id, trim material, guard metal, gemstone, inlay dye, banner base, description)
SETS = {
 "samurai": ("daimyo", "The Daimyo", "iron", "armorpieces_samurai:samurai", "redstone", "gold", "redstone", "red", "red",
             "Iron under black lacquer, laced in red, gilt where it counts - a maedate and kuwagata on the kabuto, "
             "a mempo over the face, sode at the shoulders, the sashimono flying above the head, a nodowa at the "
             "throat, kote on the arms, the daisho at the obi, kusazuri over the hips, haidate at the knees, "
             "suneate on the shins and waraji at the heels. All twelve sockets are this pack's own."),
 "norse": ("jarl", "The Jarl", "iron", "armorpieces_norse:varangian", "iron", "gold", "amethyst", "white", "white",
           "Riveted iron and the sagas' own trimmings - a boar on the crest, a braided beard and war braids, "
           "Huginn and Muninn on the shoulders, a painted round shield on the back, a gold torc, oath rings, "
           "a seax at the belt, an axe at each hip, fur-trimmed knees, winingas up the shins and snowshoes "
           "trailing from the heels. All twelve sockets are this pack's own."),
 "antiquity": ("triumph", "The Triumph", "gold", "armorpieces_antiquity:lorica", "copper", "copper", "emerald", "red", "red",
               "Bronze and red leather, Greece and Rome together - a transverse crest, the Corinthian face, the "
               "horns of Ammon, epomides at the shoulders, a scutum on the back, phalerae on the chest, a manica "
               "on each arm, the cingulum with its apron, pteruges over the thighs, gorgon cops, muscled ocreae "
               "and caligae at the heels. All twelve sockets are this pack's own."),
 "tourney": ("tilt", "The Tilt", "iron", "armorpieces_knightly:milanese", "iron", "gold", "diamond", "blue", "blue",
             "Bright steel and heraldry for the lists - a lion crest on its torse, a tilting grille, azure "
             "mantling, the grandguard, an ecranche on the back, a lance rest at the breast, a lady's favour on "
             "the arm, a sword belt, plate cuisses, rondel cops, schynbalds and pointed sabatons. All twelve "
             "sockets are this pack's own."),
}
JAVA_ARMOR = {"iron": "IRON", "gold": "GOLD", "leather": "LEATHER", "netherite": "NETHERITE", "diamond": "DIAMOND", "copper": "COPPER"}
ORDER = ["crest", "brow", "horns", "pauldrons", "back", "collar", "vambraces", "belt", "tassets", "knees", "spurs", "greaves"]

java_blocks = []
for pack, (sid, title, armor, skin, trim, guard, gem, dye, flag, desc) in SETS.items():
    ns = g.PACKS[pack]["ns"]
    pieces = {p["socket"]: p for p in g.P if p["pack"] == pack}
    out_pieces = {}
    java_lines = []
    for sock in ORDER:
        p = pieces[sock]
        fits = {}
        items = []
        kinds = (["banner"] if p.get("banner") else []) + p["fittings"]
        for f in kinds:
            if f == "guard":
                fits["armorpieces:guard"] = f"minecraft:{guard}"; items.append(f"metal(TrimMaterials.{guard.upper()})")
            elif f == "gemstone":
                fits["armorpieces:gemstone"] = f"minecraft:{gem}"; items.append(f"metal(TrimMaterials.{gem.upper()})")
            elif f == "inlay":
                fits["armorpieces:inlay"] = dye; items.append(f"dyed(DyeColor.{dye.upper()})")
            elif f == "banner":
                fits["armorpieces:banner"] = {"base": flag, "patterns": []}; items.append(f"flag(DyeColor.{flag.upper()})")
        out_pieces[sock] = {"id": f"{ns}:{p['id']}", "pack": ns.replace("_", "-"), "material": trim, "fittings": fits}
        java_lines.append(f'            on(DecorationAnchor.{sock.upper()}, "{ns}:{p["id"]}", TrimMaterials.{trim.upper()}'
                          + "".join(", " + i for i in items) + ")")
    doc = {"sets": [{"id": sid, "title": title, "description": desc,
                     "set": {"name": title,
                             "slots": {s: {"material": armor} for s in ("helmet", "chestplate", "leggings", "boots")},
                             "pieces": out_pieces, "skin": skin}}]}
    path = os.path.join(g.PACKS[pack]["dir"], "datapack", "armorpieces-sets.json")
    io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print("wrote", path)
    java_blocks.append(
        f"        // {title}, from {g.PACKS[pack]['title']} - all twelve of the pack's pieces (2026-09-13).\n"
        f"        // Transcribed from the pack's own `armorpieces-sets.json`, which is the file the site and the\n"
        f"        // wardrobe read; this copy exists so the set can be staged in game.\n"
        f'        new GallerySet("{sid}", EquipmentAssets.{JAVA_ARMOR[armor]}, skin("{skin}"), null, List.of(\n'
        + ",\n".join(java_lines) + "))")
io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sets_java.txt"), "w", encoding="utf-8", newline="\n").write(",\n\n".join(java_blocks) + "\n")
print("java transcription in sets_java.txt")
