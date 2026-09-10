"""The gate's own moving parts, checked without a game.

Tier 2 costs a server boot, so its plumbing is exactly the kind of code that rots between releases:
a fixture pack written to the wrong folder, a `pack.mcmeta` the game refuses, a scenario list that
silently lost half its entries in a rename. None of that needs Minecraft to catch, and all of it
would otherwise be caught by a run that takes four minutes and blames the mod.

    python tools/tests/test_gate.py
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gate import fixtures  # noqa: E402
from gate.bridge import Bridge  # noqa: E402
from gate.frames import ALLOWANCE, Goldens  # noqa: E402
from gate.scenarios import SCENARIOS, Failed, line_with  # noqa: E402
from gate.scenes3 import (  # noqa: E402
    PER_ANCHOR, SCENES, clothed, components, decorated, skinned)
from gate.tier2 import BOOT_CHECKS, refused_by_name, survives_a_missing_tag  # noqa: E402

ANCHORS = Path(__file__).resolve().parent.parent.parent / (
    "src/main/java/com/mattjesmc/armorpieces/decoration/DecorationAnchor.java")


class FixtureTest(unittest.TestCase):
    """A fixture pack has to be a datapack the game will actually read."""

    def setUp(self) -> None:
        self.run = Path(tempfile.mkdtemp())
        (self.run / "server.properties").write_text("level-name=gateworld\n", encoding="utf-8")

    def test_the_world_folder_comes_from_the_servers_own_settings(self) -> None:
        # A server's world is run/<level-name>, and guessing "world" is wrong the day someone
        # changes it - the fixtures would land in a folder no server reads, and every scenario
        # that needs one would fail saying the mod did not load it.
        self.assertEqual(self.run / "gateworld", fixtures.world(self.run))

    def test_a_pack_declares_the_format_three_ways(self) -> None:
        # This game version reads min_format/max_format and only falls back to pack_format with a
        # warning, so all three go in - and all three come from gradle.properties, not from here.
        fixtures.install(fixtures.GOOD, self.run)
        meta = json.loads((fixtures.world(self.run) / "datapacks" / fixtures.GOOD / "pack.mcmeta")
                          .read_text(encoding="utf-8"))["pack"]
        self.assertEqual(meta["pack_format"], fixtures.pack_format())
        self.assertEqual(meta["min_format"], fixtures.pack_format())
        self.assertEqual(meta["max_format"], fixtures.pack_format())

    def test_every_fixture_lands_where_a_datapack_is_read_from(self) -> None:
        for kind in (fixtures.GOOD, fixtures.REFUSAL, fixtures.MISSING_TAG):
            directory = fixtures.install(kind, self.run)
            for path in fixtures.files(kind):
                self.assertTrue((directory / path).is_file(), f"{kind}: {path} was not written")
                self.assertTrue(path.startswith(f"data/{fixtures.NAMESPACE}/"),
                                f"{kind}: {path} is outside the gate's own namespace")

    def test_a_fixture_is_taken_away_again(self) -> None:
        # A fixture left behind is content: the next person to open this world has a part in it
        # that exists nowhere in the repository.
        fixtures.install(fixtures.GOOD, self.run)
        self.assertEqual([fixtures.GOOD], fixtures.installed(self.run))
        fixtures.remove(fixtures.GOOD, self.run)
        self.assertEqual([], fixtures.installed(self.run))
        fixtures.remove(fixtures.GOOD, self.run)  # twice is not an error

    def test_the_refused_fixture_is_the_thing_the_rules_forbid(self) -> None:
        # If this file ever stops being illegal, the refusal check passes for the wrong reason.
        refused = list(fixtures.files(fixtures.REFUSAL).values())[0]
        self.assertEqual("armorpieces:if_wearer", refused["effects"][0]["type"])
        self.assertEqual("armorpieces:glide", refused["effects"][0]["then"]["type"])


class SuiteTest(unittest.TestCase):
    """The suite itself: named once, registered once, and not quietly empty."""

    def test_every_scenario_is_registered_under_its_own_name(self) -> None:
        names = [scene.name for scene in SCENARIOS] + [check.name for check in BOOT_CHECKS]
        self.assertEqual(len(names), len(set(names)), f"two checks share a name: {names}")
        self.assertGreaterEqual(len(SCENARIOS), 9, "scenarios went missing")

    def test_every_scenario_says_what_it_is_for(self) -> None:
        for scene in list(SCENARIOS) + list(BOOT_CHECKS):
            self.assertTrue(scene.what and len(scene.what) > 20,
                            f"{scene.name} has no description worth printing")


class ItemSyntaxTest(unittest.TestCase):
    """The /give form of a stack, which the game parses strictly and refuses whole.

    The bug this class exists for: item syntax has exactly ONE component list, so a chestplate that
    is both skinned and clothed cannot be written `chestplate[skin=..][cloth=..]`. It parses as
    nothing at all - and what it cost was a blessed golden of a skinned figure with no garment on it,
    which is a check that would have passed for ever while the feature was broken.
    """

    def test_two_components_land_in_one_bracket_list(self) -> None:
        both = clothed(skinned("minecraft:iron_chestplate", "armorpieces:plate"),
                       "armorpieces:tunic")
        self.assertEqual(1, both.count("["), both)
        self.assertEqual(1, both.count("]"), both)
        self.assertIn('armorpieces:skin="armorpieces:plate"', both)
        self.assertIn('cloth:"armorpieces:tunic"', both)

    def test_a_socket_carries_its_material_and_its_fittings(self) -> None:
        stack = decorated("minecraft:iron_chestplate", "collar", "armorpieces:bandolier",
                          fittings='"armorpieces:inlay":"red"')
        self.assertIn('collar:{material:"minecraft:gold"', stack)
        self.assertIn('fittings:{"armorpieces:inlay":"red"}', stack)

    def test_an_item_with_no_components_is_left_alone_until_one_is_added(self) -> None:
        self.assertEqual("minecraft:iron_boots[a=1]", components("minecraft:iron_boots", "a=1"))


class SceneTest(unittest.TestCase):
    """Tier 3's own suite, and the one thing it must not quietly stop covering."""

    def test_every_scene_is_registered_under_its_own_name_and_says_what_it_is_for(self) -> None:
        names = [scene.name for scene in SCENES]
        self.assertEqual(len(names), len(set(names)), f"two scenes share a name: {names}")
        for scene in SCENES:
            self.assertTrue(scene.what and len(scene.what) > 20,
                            f"{scene.name} has no description worth printing")

    def test_a_socket_the_mod_grew_is_photographed_too(self) -> None:
        # The coverage rule of the whole plan, made mechanical for the one tier where it can be:
        # every anchor the Java declares has a frame in the layer scene. A thirteenth socket fails
        # here rather than being silently unphotographed for a release.
        declared = set(re.findall(r'^\s+[A-Z_]+\("([a-z_]+)", ArmorType',
                                  ANCHORS.read_text(encoding="utf-8"), re.MULTILINE))
        self.assertTrue(declared, "no anchors were read out of DecorationAnchor.java")
        self.assertEqual(declared, set(PER_ANCHOR),
                         "the sockets the mod has and the sockets tier 3 photographs are not the "
                         "same set")


class GoldenTest(unittest.TestCase):
    """The picture comparison, which is the only thing in the gate that judges a render."""

    def setUp(self) -> None:
        self.out = Path(tempfile.mkdtemp())
        self.goldens = Goldens(self.out)
        # The store is the repository's; point it at a temporary one for the life of the test.
        self.store = Path(tempfile.mkdtemp())
        self.goldens.golden = lambda name: self.store / f"{name}.png"

    def frame(self, name: str, *, mark: int = 0) -> Path:
        image = Image.new("RGB", (32, 32), (255, 255, 255))
        if mark:
            image.paste(Image.new("RGB", (mark, 1), (10, 10, 10)), (0, 0))
        path = self.out / f"{name}.png"
        image.save(path)
        return path

    def test_a_frame_with_no_golden_is_new_rather_than_a_pass(self) -> None:
        result = self.goldens.compare("thing", self.frame("thing"))
        self.assertEqual("new", result.status)
        self.assertIn("never been looked at", result.note)

    def test_blessing_writes_the_golden_and_the_next_run_passes(self) -> None:
        self.goldens.bless = True
        self.assertEqual("blessed", self.goldens.compare("thing", self.frame("thing")).status)
        self.goldens.bless = False
        self.assertEqual("pass", self.goldens.compare("thing", self.frame("thing")).status)

    def test_a_piece_that_stopped_drawing_fails_and_draws_the_difference(self) -> None:
        self.goldens.bless = True
        self.goldens.compare("thing", self.frame("thing", mark=ALLOWANCE + 8))
        self.goldens.bless = False
        result = self.goldens.compare("thing", self.frame("thing"))
        self.assertEqual("FAIL", result.status)
        self.assertEqual(ALLOWANCE + 8, result.pixels)
        self.assertTrue((self.out / "thing.diff.png").is_file(),
                        "a failed frame has to leave a picture of what changed")

    def test_blessing_replaces_a_golden_that_has_changed(self) -> None:
        # The common case: a part was re-authored on purpose and the golden is now the old picture.
        self.goldens.bless = True
        self.goldens.compare("thing", self.frame("thing"))
        result = self.goldens.compare("thing", self.frame("thing", mark=ALLOWANCE + 8))
        self.assertEqual("blessed", result.status)
        self.goldens.bless = False
        self.assertEqual(
            "pass", self.goldens.compare("thing", self.frame("thing", mark=ALLOWANCE + 8)).status)

    def test_a_handful_of_pixels_is_not_a_failure(self) -> None:
        self.goldens.bless = True
        self.goldens.compare("thing", self.frame("thing", mark=ALLOWANCE))
        self.goldens.bless = False
        self.assertEqual("pass", self.goldens.compare("thing", self.frame("thing")).status)


class JudgementTest(unittest.TestCase):
    """The boot checks read a log rather than a reply, so their reading is worth a test of its own."""

    def test_a_refusal_naming_the_other_gate_passes(self) -> None:
        log = ("...IllegalStateException: armorpieces:if_wearer cannot gate a gliding effect: "
               "Use armorpieces:if_fitting, which asks about the part rather than the world.")
        self.assertEqual("pass", refused_by_name(log, None)[0])

    def test_a_silent_refusal_fails_and_says_why(self) -> None:
        status, note = refused_by_name("Failed to load registries due to errors", None)
        self.assertEqual("FAIL", status)
        self.assertIn("if_fitting", note)

    def test_a_world_that_never_opened_is_the_missing_tag_failure(self) -> None:
        status, note = survives_a_missing_tag(
            "Unbound tags in registry armorpieces:armor_decoration: [gate:nothing_defines_this]",
            None)
        self.assertEqual("FAIL", status)
        self.assertIn("MemberSet", note)
        self.assertIn("Unbound tags", note)


class HelperTest(unittest.TestCase):
    def test_a_missing_line_names_everything_that_was_there(self) -> None:
        # The rule the whole scenario file is written to: a failure has to carry what the game said,
        # because whoever reads it cannot see the game.
        with self.assertRaises(Failed) as raised:
            line_with(["3 loot group(s) loaded", "  armorpieces:court: 10.0%"], "wayfarer")
        self.assertIn("armorpieces:court", str(raised.exception))

    def test_the_bridge_is_pointed_at_the_toolkit_port(self) -> None:
        self.assertEqual("http://127.0.0.1:25599", Bridge().url)


if __name__ == "__main__":
    unittest.main()
