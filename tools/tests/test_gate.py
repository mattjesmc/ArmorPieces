"""The gate's own moving parts, checked without a game.

Tier 2 costs a server boot, so its plumbing is exactly the kind of code that rots between releases:
a fixture pack written to the wrong folder, a `pack.mcmeta` the game refuses, a scenario list that
silently lost half its entries in a rename. None of that needs Minecraft to catch, and all of it
would otherwise be caught by a run that takes four minutes and blames the mod.

    python tools/tests/test_gate.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gate import fixtures  # noqa: E402
from gate.bridge import Bridge  # noqa: E402
from gate.scenarios import SCENARIOS, Failed, line_with  # noqa: E402
from gate.tier2 import BOOT_CHECKS, refused_by_name, survives_a_missing_tag  # noqa: E402


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
