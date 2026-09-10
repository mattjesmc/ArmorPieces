"""
bb_rig.py --wear: the wardrobe rig, over the mod's own pieces.

    python -m unittest tools/tests/test_wear.py
    python tools/tests/test_wear.py

What is checked is the arithmetic that has no other witness: that every socket in a set lands at
its anchor, that a mirrored pair is a real mirror rather than the same half twice, and that every
face in the project names a texture that exists. What it looks like is a job for eyes, and the
plan's acceptance check says so.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import bb_rig  # noqa: E402
import mc_humanoid  # noqa: E402

ROOT = TOOLS.parent
EXAMPLE = ROOT / "docs" / "examples" / "set.json"


def cubes_under(model: dict, wanted: str) -> list[dict]:
    """Every cube anywhere below the group of this name - a piece's cubes sit in its own bone
    groups inside the socket group, however deep those go."""
    groups = {g["uuid"]: g for g in model["groups"]}
    elements = {e["uuid"]: e for e in model["elements"]}
    out: list[dict] = []

    def collect(node):
        if isinstance(node, str):
            if node in elements:
                out.append(elements[node])
            return
        for child in node["children"]:
            collect(child)

    def find(node):
        if isinstance(node, str):
            return
        if groups.get(node["uuid"], {}).get("name") == wanted:
            collect(node)
            return
        for child in node["children"]:
            find(child)

    for top in model["outliner"]:
        find(top)
    return out


class WearTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def build(self, spec):
        return bb_rig.build_worn_rig(spec, out_dir=self.out, animate=False)

    def test_one_piece_lands_on_its_anchor(self):
        model, worn = self.build({"name": "one", "pieces": {"brow": {"id": "armorpieces:circlet"}}})
        self.assertEqual([w["socket"] for w in worn], ["brow"])
        anchors = bb_rig.parse_anchors()
        attachment = anchors["brow"]["attachments"][0]
        pivot = mc_humanoid.BONES[attachment["part"]]
        anchor_geo = [pivot[i] + attachment["offset"][i] for i in range(3)]
        group = next(g for g in model["groups"] if g["name"] == "brow")
        self.assertEqual(group["origin"], [bb_rig.num(v) for v in bb_rig.flip_point(anchor_geo)])
        # The viewer is for looking at: nothing in it can be dragged.
        self.assertTrue(group["locked"])
        # And it hangs off the bone it is attached to, so it swings with the walk cycle.
        bone = next(g for g in model["groups"] if g["name"] == attachment["part"])
        def holds(node, uuid):
            if isinstance(node, str):
                return node == uuid
            return node["uuid"] == uuid or any(holds(c, uuid) for c in node["children"])
        def find(node, uuid):
            if isinstance(node, str):
                return None
            if node["uuid"] == uuid:
                return node
            for c in node["children"]:
                got = find(c, uuid)
                if got:
                    return got
            return None
        tree = next(t for top in model["outliner"] for t in [find(top, bone["uuid"])] if t)
        self.assertTrue(holds(tree, group["uuid"]), "the piece hangs off its bone")

    def test_a_mirrored_pair_is_a_real_mirror(self):
        model, _ = self.build({"name": "pair", "pieces": {"greaves": {"id": "armorpieces:greaves"}}})
        left = next(g for g in model["groups"] if g["name"] == "greaves")
        right = next(g for g in model["groups"] if g["name"] == "greaves_1")
        # The two anchors are mirror images of each other in X.
        self.assertAlmostEqual(left["origin"][0], -right["origin"][0])
        self.assertEqual(left["origin"][1:], right["origin"][1:])
        a, b = cubes_under(model, "greaves"), cubes_under(model, "greaves_1")
        self.assertEqual(len(a), len(b))
        self.assertTrue(a, "the piece has cubes")
        for one, other in zip(a, b):
            # Each cube spans the mirrored range about its own anchor, and its UV mirrors with it.
            self.assertAlmostEqual(one["from"][0] - left["origin"][0],
                                   -(other["to"][0] - right["origin"][0]), places=5)
            self.assertAlmostEqual(one["to"][0] - left["origin"][0],
                                   -(other["from"][0] - right["origin"][0]), places=5)
            self.assertEqual(one["from"][1:], other["from"][1:])
            self.assertEqual(one["to"][1:], other["to"][1:])
            self.assertNotEqual(bool(one["mirror_uv"]), bool(other["mirror_uv"]))

    def test_the_whole_example_set(self):
        spec = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        model, worn = self.build(spec)
        self.assertEqual(len(worn), len(spec["pieces"]))
        # Every socket in the set has a group, and a texture of its own.
        names = {g["name"] for g in model["groups"]}
        for socket in spec["pieces"]:
            self.assertIn(socket, names, socket)
        textures = {t["name"] for t in model["textures"]}
        self.assertIn("skin", textures)
        for slot in bb_rig.SET_SLOTS:
            self.assertIn(f"armor_{slot}", textures, slot)
        # Nothing points at a texture that is not there.
        count = len(model["textures"])
        for element in model["elements"]:
            for face in (element.get("faces") or {}).values():
                self.assertLess(face["texture"], count, element["name"])
        # The set travels with the project, so the site can read back what a rig is showing.
        self.assertEqual(model["armorpieces_set"], spec)

    def test_an_unknown_socket_is_skipped_rather_than_fatal(self):
        model, worn = self.build({"name": "odd", "pieces": {
            "brow": {"id": "armorpieces:circlet"},
            "elbows": {"id": "armorpieces:circlet"},
        }})
        self.assertEqual([w["socket"] for w in worn], ["brow"])

    def test_an_unknown_piece_is_an_error(self):
        with self.assertRaises(SystemExit):
            self.build({"name": "no", "pieces": {"brow": {"id": "armorpieces:not_a_piece"}}})

    def test_a_piece_borrowed_from_a_pack(self):
        """An outfit may name a piece from any pack, and since the 2026-09-07 split most of them
        must: the mantle this set used to wear as `armorpieces:mantle` is `armorpieces_hunt:mantle`
        now. The rig finds it because the pack's folders are named alongside the mod's."""
        hunt = ROOT / "packs" / "wildhunt"
        spec = {"name": "borrowed", "pieces": {"pauldrons": {"id": "armorpieces_hunt:mantle"}}}
        model, worn = bb_rig.build_worn_rig(
            spec, out_dir=self.out, animate=False,
            packs=[hunt / "datapack", hunt / "resourcepack"])
        self.assertEqual([w["socket"] for w in worn], ["pauldrons"])
        self.assertTrue(cubes_under(model, "pauldrons"), "the borrowed piece has cubes")
        # And without the pack it is simply not there, which is the split's break in miniature.
        with self.assertRaises(SystemExit):
            self.build(spec)


if __name__ == "__main__":
    unittest.main()
