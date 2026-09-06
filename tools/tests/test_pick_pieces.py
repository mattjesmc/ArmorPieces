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
        self.assertEqual(m["counts"]["pieces"], 91)
        self.assertGreaterEqual(m["counts"]["skins"], 14)
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
            self.assertEqual(m["counts"], {"pieces": 1, "skins": 1, "cloths": 1})
            self.assertEqual(m["pieces"][0]["label"], "Great Helm")


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
            self.assertEqual(m["counts"], {"pieces": 1, "skins": 1, "cloths": 1})
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

    def test_the_mods_pieces_compose_with_own(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "mine"
            written = pick_pieces.pick([[MOD]], ["armorpieces:circlet", "armorpieces:plate", "armorpieces:tunic"],
                                       dest, own=True, name="test")
            self.assertEqual(len(written), 3)
            m = pack_manifest.manifest([dest])
            self.assertEqual(m["counts"], {"pieces": 1, "skins": 1, "cloths": 1})
            # The circlet is found in the court group; the tag came along with just it in it.
            tags = list((dest / "data/armorpieces/tags/armorpieces/armor_decoration").glob("*.json"))
            self.assertTrue(tags)
            for tag in tags:
                self.assertEqual(json.loads(tag.read_text())["values"], ["armorpieces:circlet"])


if __name__ == "__main__":
    unittest.main()
