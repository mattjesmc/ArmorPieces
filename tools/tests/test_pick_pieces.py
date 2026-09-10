"""
pack_manifest.py and pick_pieces.py, over the mod's own pack and a small pack made here.

    python -m unittest tools/tests/test_pick_pieces.py
    python tools/tests/test_pick_pieces.py
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import pack_manifest  # noqa: E402
import pick_pieces  # noqa: E402

ROOT = TOOLS.parent
MOD = ROOT / "src" / "main" / "resources"

PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d4944415478"
    "9c6360f8cfc00000030101009d4a5d3f0000000049454e44ae426082")


def write(path: Path, content) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(json.dumps(content, indent=1) if not isinstance(content, str) else content,
                        encoding="utf-8")


def make_pack(root: Path, namespace: str = "somebody", credits: dict | None = None) -> Path:
    """A pack with one piece (with a fitting of its own and a loot group), one skin, one cloth."""
    write(root / "pack.mcmeta", {"pack": {"description": "test", "pack_format": 107}})
    write(root / f"data/{namespace}/armorpieces/armor_decoration/great_helm.json",
          {"asset_id": f"{namespace}:great_helm", "description": {"translate": f"decoration.{namespace}.great_helm"},
           "anchors": ["crest"], "fittings": [f"{namespace}:plume"]})
    write(root / f"assets/{namespace}/armorpieces/decoration/great_helm.json",
          {"texture_width": 64, "texture_height": 32, "bones": []})
    write(root / f"assets/{namespace}/textures/entity/decoration/great_helm.png", PNG)
    write(root / f"assets/{namespace}/textures/entity/decoration/great_helm_plume.png", PNG)
    write(root / f"data/{namespace}/recipe/template_great_helm.json", {"type": "minecraft:crafting_shaped"})
    write(root / f"data/{namespace}/armorpieces/fitting/plume.json",
          {"type": "armorpieces:dye", "description": {"translate": f"fitting.{namespace}.plume"}})
    write(root / f"data/{namespace}/recipe/fitting_template_plume.json", {"type": "minecraft:crafting_shaped"})
    write(root / f"data/{namespace}/tags/armorpieces/armor_decoration/knightly.json",
          {"values": [f"{namespace}:great_helm", f"{namespace}:other"]})
    write(root / f"data/{namespace}/armorpieces/loot_group/knightly.json",
          {"chance": 0.1, "tables": ["minecraft:chests/simple_dungeon"], "parts": f"#{namespace}:knightly"})
    write(root / f"data/{namespace}/armorpieces/armor_skin/brigandine.json",
          {"asset_id": f"{namespace}:brigandine", "description": {"translate": f"skin.{namespace}.brigandine"}})
    write(root / f"assets/{namespace}/textures/entity/skin/brigandine/humanoid.png", PNG)
    write(root / f"assets/{namespace}/textures/entity/skin/brigandine/humanoid_leggings.png", PNG)
    write(root / f"data/{namespace}/armorpieces/cloth/surcoat.json",
          {"asset_id": f"{namespace}:surcoat", "sheet": "shield", "description": {"translate": f"cloth.{namespace}.surcoat"}})
    write(root / f"assets/{namespace}/textures/entity/cloth/surcoat/humanoid.png", PNG)
    write(root / f"assets/{namespace}/textures/entity/cloth/surcoat/humanoid_leggings.png", PNG)
    write(root / f"assets/{namespace}/lang/en_us.json", {
        f"decoration.{namespace}.great_helm": "Great Helm", f"skin.{namespace}.brigandine": "Brigandine",
        f"cloth.{namespace}.surcoat": "Surcoat", f"fitting.{namespace}.plume": "Plume",
        f"fitting.{namespace}.plume.ingredients": "any dye"})
    if credits is not None:
        write(root / pack_manifest.CREDITS_FILE, credits)
    return root


class ManifestTests(unittest.TestCase):
    def test_the_mods_own_pack(self):
        m = pack_manifest.manifest([MOD])
        # 66 since the split of 2026-09-07 moved 25 pieces and 5 skins into content packs; see
        # docs/plans/main-pack-split.md. The moved ones are checked through packs/legacy below.
        self.assertEqual(m["counts"]["pieces"], 66)
        self.assertGreaterEqual(m["counts"]["skins"], 9)
        self.assertEqual(m["counts"]["cloths"], 2)
        circlet = next(p for p in m["pieces"] if p["id"] == "armorpieces:circlet")
        self.assertEqual(circlet["label"], "Circlet")
        self.assertEqual(circlet["anchor"], "brow")
        self.assertEqual(circlet["fittings"], ["armorpieces:gemstone"])
        self.assertTrue(circlet["craftable"])
        self.assertTrue(circlet["loot"])
        self.assertEqual(circlet["license"], "ARR")  # no credits file: all rights reserved
        self.assertIn("assets/armorpieces/textures/entity/decoration/circlet_gemstone.png", circlet["files"])
        self.assertIn("data/armorpieces/recipe/template_circlet.json", circlet["files"])
        plate = next(s for s in m["skins"] if s["id"] == "armorpieces:plate")
        self.assertTrue(plate["loot"])
        self.assertIn("assets/armorpieces/textures/entity/skin/plate/humanoid_leggings.png", plate["files"])
        tunic = next(c for c in m["cloths"] if c["id"] == "armorpieces:tunic")
        self.assertEqual(tunic["sheet"], "shield")
        self.assertIn("assets/armorpieces/textures/item/cloth_template_tunic.png", tunic["files"])

    def test_the_restore_pack_whose_folder_is_not_its_namespace(self):
        """packs/legacy is the one pack whose folder name and namespace differ: it declares
        `armorpieces`, the mod's own, which is how it restores the ids 0.3.0 wrote into saves.
        Nothing here may derive a namespace from a folder name."""
        legacy = ROOT / "packs" / "legacy"
        m = pack_manifest.manifest([legacy / "datapack", legacy / "resourcepack"])
        self.assertEqual(m["counts"]["pieces"], 25)
        self.assertEqual(m["counts"]["skins"], 5)
        self.assertEqual(m["pack"]["namespaces"], ["armorpieces"])
        tusks = next(p for p in m["pieces"] if p["id"] == "armorpieces:tusks")
        self.assertEqual(tusks["label"], "Tusks")
        self.assertEqual(tusks["anchor"], "horns")
        self.assertTrue(tusks["loot"])
        # No template recipes at all: the packs that took the pieces already own their centres.
        self.assertFalse(any(e["craftable"] for e in m["pieces"] + m["skins"]))

    def test_credits_default_and_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            pack = make_pack(Path(tmp) / "a", credits={
                "pack": {"author": "somebody", "license": "CC-BY-4.0"},
                "pieces": {"somebody:surcoat": {"license": "ARR"},
                           "somebody:brigandine": {"author": "else", "license": "CC0-1.0", "source": "https://x"}}})
            m = pack_manifest.manifest([pack])
            by_id = {e["id"]: e for e in m["pieces"] + m["skins"] + m["cloths"]}
            self.assertEqual(by_id["somebody:great_helm"]["license"], "CC-BY-4.0")
            self.assertEqual(by_id["somebody:great_helm"]["author"], "somebody")
            self.assertEqual(by_id["somebody:surcoat"]["license"], "ARR")
            self.assertEqual(by_id["somebody:brigandine"]["author"], "else")
            self.assertEqual(by_id["somebody:brigandine"]["source"], "https://x")
            self.assertEqual(m["pack"]["license"], "CC-BY-4.0")
            self.assertEqual(by_id["somebody:great_helm"]["tags"],
                             ["data/somebody/tags/armorpieces/armor_decoration/knightly.json"])

    def test_two_halves(self):
        with tempfile.TemporaryDirectory() as tmp:
            whole = make_pack(Path(tmp) / "whole")
            data, assets = Path(tmp) / "data_half", Path(tmp) / "assets_half"
            shutil.copytree(whole / "data", data / "data")
            shutil.copytree(whole / "assets", assets / "assets")
            m = pack_manifest.manifest([data, assets])
            self.assertEqual(m["counts"], {"pieces": 1, "skins": 1, "cloths": 1, "sets": 0})
            self.assertEqual(m["pieces"][0]["label"], "Great Helm")

    def test_the_sets_a_pack_declares(self):
        """armorpieces-sets.json: what is kept, what is borrowed, and what is left out.

        The file is hand-written and the next thing to read it is a web page, so a set that is
        wrong is dropped with a warning rather than published as a broken row."""
        with tempfile.TemporaryDirectory() as tmp:
            pack = make_pack(Path(tmp) / "a")
            write(pack / pack_manifest.SETS_FILE, {"sets": [
                {"id": "knightly", "title": "The Knightly", "description": "one own, one borrowed",
                 "set": {"slots": {"helmet": {"material": "iron"}}, "pieces": {
                     "crest": {"id": "somebody:great_helm"},          # this pack's own: kept
                     "brow": {"id": "armorpieces:circlet"},           # another pack's: borrowed
                     "horns": {"id": "somebody:antlers"},             # own, but not here: dropped
                 }}},
                {"id": "Shouting", "set": {"pieces": {}}},            # not a slug: no set at all
                {"id": "knightly", "set": {"pieces": {}}},            # the id is taken: ignored
                {"id": "bodyless"},                                   # no `set`: ignored
            ]})
            m = pack_manifest.manifest([pack])
            self.assertEqual(m["counts"]["sets"], 1)
            declared = m["sets"][0]
            self.assertEqual(declared["title"], "The Knightly")
            self.assertEqual(declared["sockets"], 2)
            self.assertEqual(declared["borrowed"], 1)
            self.assertEqual(sorted(declared["set"]["pieces"]), ["brow", "crest"])
            # A set that says nothing about its name still has one, for the page that shows it.
            self.assertEqual(declared["set"]["name"], "The Knightly")


class PickTests(unittest.TestCase):
    def test_moves_a_piece_a_skin_and_a_cloth(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = make_pack(Path(tmp) / "a", credits={"pack": {"author": "somebody", "license": "CC-BY-4.0"}})
            dest = Path(tmp) / "mine"
            written = pick_pieces.pick([[a]], ["somebody:great_helm", "somebody:brigandine", "somebody:surcoat"], dest)
            self.assertEqual(set(written), {"somebody:great_helm", "somebody:brigandine", "somebody:surcoat"})
            for relative in [
                "pack.mcmeta", pack_manifest.CREDITS_FILE,
                "data/somebody/armorpieces/armor_decoration/great_helm.json",
                "assets/somebody/armorpieces/decoration/great_helm.json",
                "assets/somebody/textures/entity/decoration/great_helm.png",
                "assets/somebody/textures/entity/decoration/great_helm_plume.png",
                "data/somebody/recipe/template_great_helm.json",
                "data/somebody/armorpieces/fitting/plume.json",
                "data/somebody/recipe/fitting_template_plume.json",
                "data/somebody/tags/armorpieces/armor_decoration/knightly.json",
                "data/somebody/armorpieces/loot_group/knightly.json",
                "assets/somebody/textures/entity/skin/brigandine/humanoid.png",
                "assets/somebody/textures/entity/cloth/surcoat/humanoid_leggings.png",
                "assets/somebody/lang/en_us.json",
            ]:
                self.assertTrue((dest / relative).is_file(), relative)
            # The tag holds the picked member only; the other piece was not asked for.
            tag = json.loads((dest / "data/somebody/tags/armorpieces/armor_decoration/knightly.json").read_text())
            self.assertEqual(tag["values"], ["somebody:great_helm"])
            lang = json.loads((dest / "assets/somebody/lang/en_us.json").read_text(encoding="utf-8"))
            self.assertEqual(lang["decoration.somebody.great_helm"], "Great Helm")
            self.assertEqual(lang["fitting.somebody.plume"], "Plume")
            credits = json.loads((dest / pack_manifest.CREDITS_FILE).read_text(encoding="utf-8"))
            self.assertEqual(credits["pieces"]["somebody:great_helm"], {"author": "somebody", "license": "CC-BY-4.0"})
            self.assertTrue(credits["pack"]["composed"])
            # The result is a pack the manifest reads back with the licenses it came with.
            m = pack_manifest.manifest([dest])
            self.assertEqual(m["counts"], {"pieces": 1, "skins": 1, "cloths": 1, "sets": 0})
            self.assertEqual(m["pieces"][0]["license"], "CC-BY-4.0")
            mcmeta = json.loads((dest / "pack.mcmeta").read_text())
            self.assertIn("pack_format", mcmeta["pack"])

    def test_refuses_arr_unless_own(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = make_pack(Path(tmp) / "a")  # no credits: all rights reserved
            dest = Path(tmp) / "mine"
            with self.assertRaises(pick_pieces.PickError) as ctx:
                pick_pieces.pick([[a]], ["somebody:great_helm"], dest)
            self.assertIn("all rights reserved", str(ctx.exception))
            self.assertFalse(dest.exists(), "a refusal writes nothing")
            pick_pieces.pick([[a]], ["somebody:great_helm"], dest, own=True)
            self.assertTrue((dest / "data/somebody/armorpieces/armor_decoration/great_helm.json").is_file())

    def test_refuses_two_different_pieces_with_one_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            credits = {"pack": {"author": "somebody", "license": "CC0-1.0"}}
            a = make_pack(Path(tmp) / "a", credits=credits)
            b = make_pack(Path(tmp) / "b", credits=credits)
            # Same id, both composable, but b's helm is another model.
            write(b / "assets/somebody/armorpieces/decoration/great_helm.json",
                  {"texture_width": 64, "texture_height": 32, "bones": [{"name": "x"}]})
            with self.assertRaises(pick_pieces.PickError) as ctx:
                pick_pieces.pick([[a], [b]], ["somebody:great_helm"], Path(tmp) / "mine")
            self.assertIn("two different entries", str(ctx.exception))
            # Identical copies in two sources are one piece.
            write(b / "assets/somebody/armorpieces/decoration/great_helm.json",
                  json.loads((a / "assets/somebody/armorpieces/decoration/great_helm.json").read_text()))
            pick_pieces.pick([[a], [b]], ["somebody:great_helm"], Path(tmp) / "mine2")

    def test_refuses_a_collision_in_the_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            credits = {"pack": {"author": "somebody", "license": "CC0-1.0"}}
            a = make_pack(Path(tmp) / "a", credits=credits)
            dest = make_pack(Path(tmp) / "dest", credits=credits)
            write(dest / "assets/somebody/textures/entity/decoration/great_helm.png", PNG + b"\x00")
            with self.assertRaises(pick_pieces.PickError) as ctx:
                pick_pieces.pick([[a]], ["somebody:great_helm"], dest)
            self.assertIn("different content", str(ctx.exception))

    def test_unknown_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = make_pack(Path(tmp) / "a")
            with self.assertRaises(pick_pieces.PickError):
                pick_pieces.pick([[a]], ["somebody:nothing"], Path(tmp) / "mine", own=True)

    def test_duplicates_a_piece_under_another_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = make_pack(Path(tmp) / "a", credits={"pack": {"author": "somebody", "license": "CC-BY-4.0"}})
            written = pick_pieces.pick([[a]], ["somebody:great_helm"], a, as_id="mine:tall_helm")
            self.assertEqual(set(written), {"mine:tall_helm"})
            # Every file that carried the name is there under the new one, and the old is untouched.
            for relative in [
                "data/mine/armorpieces/armor_decoration/tall_helm.json",
                "data/mine/recipe/template_tall_helm.json",
                "assets/mine/armorpieces/decoration/tall_helm.json",
                "assets/mine/textures/entity/decoration/tall_helm.png",
                "assets/mine/textures/entity/decoration/tall_helm_plume.png",
                "data/somebody/armorpieces/armor_decoration/great_helm.json",
            ]:
                self.assertTrue((a / relative).is_file(), relative)
            body = json.loads((a / "data/mine/armorpieces/armor_decoration/tall_helm.json").read_text(encoding="utf-8"))
            self.assertEqual(body["asset_id"], "mine:tall_helm")
            self.assertEqual(body["description"]["translate"], "decoration.mine.tall_helm")
            # The fitting is the source pack's and keeps its own id.
            self.assertEqual(body["fittings"], ["somebody:plume"])
            lang = json.loads((a / "assets/mine/lang/en_us.json").read_text(encoding="utf-8"))
            self.assertEqual(lang["decoration.mine.tall_helm"], "Great Helm")
            # It belongs to the same loot group, beside the original.
            tag = json.loads((a / "data/somebody/tags/armorpieces/armor_decoration/knightly.json").read_text())
            self.assertIn("mine:tall_helm", tag["values"])
            self.assertIn("somebody:great_helm", tag["values"])
            credits = json.loads((a / pack_manifest.CREDITS_FILE).read_text(encoding="utf-8"))
            self.assertEqual(credits["pieces"]["mine:tall_helm"]["source"], "somebody:great_helm")
            # And the pack reads back with both.
            m = pack_manifest.manifest([a])
            self.assertEqual(m["counts"]["pieces"], 2)
            self.assertEqual({p["id"] for p in m["pieces"]}, {"somebody:great_helm", "mine:tall_helm"})

    def test_duplicates_a_skin_and_a_cloth(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = make_pack(Path(tmp) / "a", credits={"pack": {"author": "somebody", "license": "CC0-1.0"}})
            write(a / "assets/somebody/models/item/cloth_template_surcoat.json",
                  {"parent": "minecraft:item/generated", "textures": {"layer0": "somebody:item/cloth_template_surcoat"}})
            write(a / "assets/somebody/textures/item/cloth_template_surcoat.png", PNG)
            pick_pieces.pick([[a]], ["somebody:brigandine"], a, as_id="mine:scale")
            pick_pieces.pick([[a]], ["somebody:surcoat"], a, as_id="mine:tabard")
            self.assertTrue((a / "assets/mine/textures/entity/skin/scale/humanoid.png").is_file())
            self.assertTrue((a / "assets/mine/textures/entity/skin/scale/humanoid_leggings.png").is_file())
            self.assertTrue((a / "assets/mine/textures/item/cloth_template_tabard.png").is_file())
            model = json.loads((a / "assets/mine/models/item/cloth_template_tabard.json").read_text(encoding="utf-8"))
            self.assertEqual(model["textures"]["layer0"], "mine:item/cloth_template_tabard")
            body = json.loads((a / "data/mine/armorpieces/cloth/tabard.json").read_text(encoding="utf-8"))
            self.assertEqual(body["asset_id"], "mine:tabard")
            self.assertEqual(body["sheet"], "shield")
            m = pack_manifest.manifest([a])
            self.assertEqual(m["counts"], {"pieces": 1, "skins": 2, "cloths": 2, "sets": 0})

    def test_duplicating_refuses_a_taken_id_and_a_bad_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = make_pack(Path(tmp) / "a", credits={"pack": {"author": "somebody", "license": "CC0-1.0"}})
            for bad, why in [("nocolon", "namespaced"), ("mine:Tall", "lower-case"),
                             ("somebody:great_helm", "already has")]:
                with self.assertRaises(pick_pieces.PickError) as ctx:
                    pick_pieces.pick([[a]], ["somebody:great_helm"], a, as_id=bad)
                self.assertIn(why, str(ctx.exception))
            with self.assertRaises(pick_pieces.PickError) as ctx:
                pick_pieces.pick([[a]], ["somebody:great_helm", "somebody:surcoat"], a, as_id="mine:x")
            self.assertIn("exactly one id", str(ctx.exception))
            pick_pieces.pick([[a]], ["somebody:great_helm"], a, as_id="mine:tall_helm")
            with self.assertRaises(pick_pieces.PickError) as ctx:
                pick_pieces.pick([[a]], ["somebody:great_helm"], a, as_id="mine:tall_helm")
            self.assertIn("already holds", str(ctx.exception))

    def test_duplicating_still_refuses_all_rights_reserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = make_pack(Path(tmp) / "a")  # no credits: all rights reserved
            with self.assertRaises(pick_pieces.PickError) as ctx:
                pick_pieces.pick([[a]], ["somebody:great_helm"], Path(tmp) / "mine", as_id="mine:tall_helm")
            self.assertIn("all rights reserved", str(ctx.exception))

    def test_drops_an_entry_and_leaves_what_is_shared(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = make_pack(Path(tmp) / "a", credits={"pack": {"author": "somebody", "license": "CC0-1.0"}})
            dest = Path(tmp) / "mine"
            pick_pieces.pick([[a]], ["somebody:great_helm", "somebody:surcoat"], dest)
            removed = pick_pieces.drop(dest, ["somebody:great_helm"])
            self.assertIn("data/somebody/armorpieces/armor_decoration/great_helm.json", removed["somebody:great_helm"])
            for gone in [
                "data/somebody/armorpieces/armor_decoration/great_helm.json",
                "data/somebody/recipe/template_great_helm.json",
                "assets/somebody/armorpieces/decoration/great_helm.json",
                "assets/somebody/textures/entity/decoration/great_helm.png",
                "assets/somebody/textures/entity/decoration/great_helm_plume.png",
                # The tag held only it, so the file went with it.
                "data/somebody/tags/armorpieces/armor_decoration/knightly.json",
            ]:
                self.assertFalse((dest / gone).exists(), gone)
            # The cloth, the fitting and the loot group are still needed or still shared.
            for kept in [
                "data/somebody/armorpieces/cloth/surcoat.json",
                "data/somebody/armorpieces/fitting/plume.json",
                "data/somebody/armorpieces/loot_group/knightly.json",
            ]:
                self.assertTrue((dest / kept).is_file(), kept)
            lang = json.loads((dest / "assets/somebody/lang/en_us.json").read_text(encoding="utf-8"))
            self.assertNotIn("decoration.somebody.great_helm", lang)
            self.assertIn("cloth.somebody.surcoat", lang)
            credits = json.loads((dest / pack_manifest.CREDITS_FILE).read_text(encoding="utf-8"))
            self.assertNotIn("somebody:great_helm", credits["pieces"])
            m = pack_manifest.manifest([dest])
            self.assertEqual(m["counts"], {"pieces": 0, "skins": 0, "cloths": 1, "sets": 0})

    def test_a_move_is_a_pick_then_a_drop(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = make_pack(Path(tmp) / "a", credits={"pack": {"author": "somebody", "license": "CC0-1.0"}})
            b = Path(tmp) / "b"
            pick_pieces.pick([[a]], ["somebody:great_helm"], b)
            pick_pieces.drop(a, ["somebody:great_helm"])
            self.assertEqual(pack_manifest.manifest([a])["counts"]["pieces"], 0)
            self.assertEqual(pack_manifest.manifest([b])["counts"]["pieces"], 1)

    def test_dropping_an_id_the_pack_does_not_have(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = make_pack(Path(tmp) / "a", credits={"pack": {"author": "somebody", "license": "CC0-1.0"}})
            with self.assertRaises(pick_pieces.PickError):
                pick_pieces.drop(a, ["somebody:nothing"])

    def test_a_reindented_shared_file_is_not_a_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            credits = {"pack": {"author": "somebody", "license": "CC0-1.0"}}
            a = make_pack(Path(tmp) / "a", credits=credits)
            dest = Path(tmp) / "mine"
            pick_pieces.pick([[a]], ["somebody:great_helm"], dest)
            # A pack that has been through sanitize_pack.py comes back re-indented. The fitting
            # says exactly the same thing; copying beside it must not be refused over whitespace.
            fitting = dest / "data/somebody/armorpieces/fitting/plume.json"
            fitting.write_text(json.dumps(json.loads(fitting.read_text()), indent=4) + "\n", encoding="utf-8")
            pick_pieces.pick([[a]], ["somebody:great_helm"], dest, as_id="mine:tall_helm")
            self.assertEqual(pack_manifest.manifest([dest])["counts"]["pieces"], 2)
            # A fitting that genuinely differs is still a collision.
            fitting.write_text(json.dumps({"type": "armorpieces:trim"}, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(pick_pieces.PickError) as ctx:
                pick_pieces.pick([[a]], ["somebody:great_helm"], dest, as_id="mine:third_helm")
            self.assertIn("different content", str(ctx.exception))

    def test_the_mods_pieces_compose_with_own(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "mine"
            written = pick_pieces.pick([[MOD]], ["armorpieces:circlet", "armorpieces:plate", "armorpieces:tunic"],
                                       dest, own=True, name="test")
            self.assertEqual(len(written), 3)
            m = pack_manifest.manifest([dest])
            self.assertEqual(m["counts"], {"pieces": 1, "skins": 1, "cloths": 1, "sets": 0})
            # The circlet is found in the court group; the tag came along with just it in it.
            tags = list((dest / "data/armorpieces/tags/armorpieces/armor_decoration").glob("*.json"))
            self.assertTrue(tags)
            for tag in tags:
                self.assertEqual(json.loads(tag.read_text())["values"], ["armorpieces:circlet"])


if __name__ == "__main__":
    unittest.main()
