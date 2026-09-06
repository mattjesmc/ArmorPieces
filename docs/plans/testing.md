# Plan: the gate

One command that has to pass before a release, and that grows a check every time a feature lands.

---

## Today

Six things can be run against this repository, and nothing runs them together:

| what | covers | gates? |
| --- | --- | --- |
| `gradlew build` | compiles; `SkinBakeTest` (Java bake vs `bake_skin.py`, texel for texel), `SkinTemplateIconTest` | yes |
| `tools/check_authoring.py` | the plugin's round trip over every part, skin, cloth, recipe, loot group; grid collisions; reach | yes, exit 1 |
| `tools/check_skin.py --all` | every master pair: unpainted slots, off-net paint, ramp range, the steps vanilla overrules | yes, exit 2 |
| `tools/check_painters.py` | every `paint_*_master.py` still describes its geometry and reproduces its PNG; `trace_geometry` over all 91 | yes, exit 1 |
| `tools/tests/test_pick_pieces.py` | the pack picker's refusals | yes |
| `node --check tools/blockbench_plugin/armorpieces.js` | the plugin parses | yes |

Three facts about that table decide everything below.

**Nothing in the build runs `tools/`.** The painters rotted through the whole of 0.2.0 unnoticed, and
they are rotten again right now: `antlers`, `bandolier` and `helm_wings` are stale as of 2026-09-06,
the third of them new since the last recorded run. A check that exists and is not run is not a check.

**Everything else was verified by hand, in a game an agent drove.** Section 2 of 0.4.0 took three
`runClient` cycles, section 3 one, section 4 three — each one a person or an agent typing commands,
reading chat and looking at frames. That work found four traps that no static check could have
found: a codec that omits its own fields on encode, a `withAlternative` that always encodes with the
first alternative, a missing tag that takes a whole loot table down, and a sub-predicate key that
arrives full-id on the client and bare in the file. Every one of them is a *round trip* or a *load*,
which is to say: exactly the kind of thing a machine can assert, in a game a machine can drive.

**The release checklist is in one person's head**, plus a memory file. Version bump, `modpage`
rebuild, pack zips, tag, release body, the three-repo sync. None of it is checked.

---

## What the gate is

`python tools/gate.py` — runs every check that can fail, prints one line per check, and exits
nonzero if any failed. Tiers are named by **what they need**, because that is what decides whether a
check can run right now:

- **tier 0 — the tree.** Python and node only. Runs anywhere, in seconds to a couple of minutes.
- **tier 1 — the JVM.** Gradle, no game window. Compiles, unit tests, codec round trips.
- **tier 2 — the server.** A dedicated server with the mcp-toolkit bridge, no client. Loading,
  loot, effects, commands, config, datapack refusals. Minutes.
- **tier 3 — the client.** One client run with the bridge. Rendering, screens, tooltips. Slowest,
  and the only tier that needs a picture compared to a picture.

`--tier 0..3` runs up to a tier and stops; the default is everything that can run on this machine
(the bridge's `ping` says whether a game is attached, so the default degrades rather than fails).
`--json` writes a report; failures carry the command that reproduces them alone.

### What each tier asserts

Coverage is tracked against the mod's own surface, not against files. The list is what exists today;
a feature that lands without a row here is not finished.

| the mod does | tier | the assertion |
| --- | --- | --- |
| the four registries load (`armor_decoration`, `armor_skin`, `cloth`, `loot_group`) | 1 | every shipped element decodes, and re-encodes to its own bytes |
| effect types (`attribute`, `mob_effect`, `blink`, `glide`, `if_fitting`, `if_wearer`) | 1 | each codec round-trips; `MaterialValue` encodes bare when no case is set; `reaches(hook)` per wrapper |
| fitting types (`material`, `dye`, `banner`) | 1 | round trip, and the mask a masked fitting names exists |
| both configs | 1 | the write codec emits **every** field — the trap that wrote `{}` twice |
| `LootGroup` table entries | 1 | a bare id and an id-with-chance both survive encode; the `withAlternative` trap |
| the geometry loader | 1 | every shipped geometry parses into `DecorationGeometry` |
| the skin bake | 1 | `SkinBakeTest`, already there |
| a world loads the mod's own pack | 2 | no `Failed to load`, no mod warning in `get_log` |
| loot groups | 2 | `/armorpieces loot list\|explain\|groups\|roll`, and `roll_loot` with a seed over the tables a group names — share and avg, not presence |
| `set_decoration` + `armorpieces:template` | 2 | a pushed foreign table hands out a part on the right socket template |
| a missing tag | 2 | the entry drops and the table still rolls — the 0.4.0 trap, as a test |
| the server config | 2 | written with every key; `enabled`, `chance`, `weight`, `add`, `remove`, the multiplier, and `/reload` picking up an edit in both directions |
| effects | 2 | equip through `/item replace`, then `/armorpieces effects` and `/attribute … get`: claws by material and by empty hand, head_fins in water, circlet on a set gem, heel_wings' jump number, cloak's per-material chance |
| the load-time refusals | 2 | a pushed part with a wearer condition over a glider, and over an attribute effect, each fails the pack with the message that names the test |
| stage command | 2 | `/armorpieces stage pieces\|random\|bases\|fittings\|skins\|table\|set\|clear` each answer |
| the four smithing recipes | 3 | the advanced table's menu, driven by slots: part, skin, cloth, fitting each produce the right output stack; `DisabledRecipe` produces nothing |
| the decoration render layer | 3 | a golden frame per socket, on the studio floor |
| skins per material | 3 | eight materials of one skin, one frame each |
| cloth | 3 | tunic and tabard, chest and leggings, on a skinned pair and on plain iron |
| fitting colour | 3 | dye and banner fittings render their colour |
| the template items' icons | 3 | a frame of the creative tab |
| the tooltip | 3 | `get_tooltip` against `description()` — the one 0.4.0 claim never seen with eyes |

---

## The in-game half: the bridge is the API

The mcp-toolkit bridge (`127.0.0.1:25599`, `POST /cmd`) is already a dev-runtime dependency of this
build for both the client and the server run, and it already carries most of what a scenario needs:
`run_command` at full permission, `roll_loot` with a seed and aggregate share/avg, `push_data` /
`push_asset` / `reload_data` (a third-party pack without a file in this repository), `get_log` and
`get_events`, `get_screen` reporting a container's slots and `click` routing real events into them,
`render` and `studio` (no HUD, no sky, flat full-bright — the F1 problem does not exist out of
band), and `review_post` for the judgements that genuinely need a person.

A **scenario** is a file under `tools/gate/scenarios/`: a name, the tier it needs, a `setup` list of
bridge calls, and a list of assertions over their replies. The runner speaks HTTP to the bridge
directly — the MCP shim is for a session, not for a suite — and every scenario is written so it can
be run alone by name.

Two rules the scenarios inherit from what has already gone wrong:

- **Prove the build before believing a reply.** A second client cannot bind 25599 and answers from
  the older JVM, silently. The runner asks `ping` first and refuses to run against an instance it
  did not start (see the toolkit ask below — today this is a version string the mod prints).
- **Build the world; never reuse one.** A datapack folder created after a world loaded is invisible
  to `/reload` and to `datapack enable` both.

### What the toolkit must add first

Six asks, in the order they unblock work. Everything else — image diffing, goldens, the scenario
format — is ours.

1. **`create_world`**: name, seed, flat preset, gamerules, cheats, and **datapacks enabled at
   creation**. `open_world` only opens what exists; driving the creation screens by widget label
   would break on any vanilla UI change. Tier 2 and 3 both stand on this.
2. **An entity in the studio.** `stage_entity` wears an authored geometry file and `studio` stands
   blocks; nothing puts a living entity wearing **real item stacks in full item syntax, components
   included**, on the white floor at a fixed yaw. Everything this mod draws is an entity render
   layer, so this is the tool tier 3 is made of.
3. **`get_tooltip`**: the lines the game would render for a stack, as text. The toolkit cannot hover
   a slot, which is why the 0.4.0 tooltip was shipped unseen.
4. **A pinned render tick.** `studio` kills sky and light drift; animation phase (walk, idle, hurt),
   item-model animation and anything on wall-clock millis are what make a golden diff flaky.
   `render {tick: N}`.
5. **`ping` names the build**: loaded mod versions plus a hash or mtime of the jar and classes, not
   only `instanceId`. This is the cheap detector for the stale-instance trap.
6. **A documented server-only manifest**: which tools answer with no client attached, so tier 2 is
   written against a guarantee.

Nice to have, not blocking: item syntax with components in `bot_give` / `bot_equip`, and a `slot`
addressing mode for `click` to pair with the slots `get_screen` already reports.

---

## Build order

1. **`tools/gate.py` with tier 0**, wrapping the six things that already exist, plus the checks that
   are cheap and missing: every lang key a command or item names exists in `en_us.json`; the effect
   schema the plugin reads still matches the Java; `modpage build --offline` leaves `README.md` and
   `dist/` unchanged; `CHANGELOG.md` has a section for `mod_version` unless it is `Unreleased`.
2. **Fix the three stale painters.** They are a defect the gate found on its first run, and they are
   0.2.x/0.3.x debt, not 0.4.0 work.
3. **Tier 1.** Gradle `test` grows the codec round trips over the mod's own shipped data. The four
   0.4.0 traps become four named tests, so the class of bug that cost three game cycles costs a
   second.
4. **Tier 2.** The bridge client, the scenario format, and the scenarios in the table above, run
   against a dedicated server. This is the tier that pays for itself: it is most of what the last
   three sections were verified by, and it needs only ask 1 and 6.
5. **Tier 3.** Goldens, once asks 2 and 4 land. Until then the frames go to `review_post` and a
   person answers, which is the honest version of the same check.

## As built

Tier 0 and tier 1 run. `tools/gate.py` is the runner; `check_lang.py` and `check_effect_schema.py`
are new checks; tier 1 is `gradlew build`, and the JUnit half grew from one test to six classes.

The one thing that changed shape in the building: **tier 1 needed Fabric after all.** A codec that
names a registry cannot be BUILT in a bare JVM - `ArmorPiecesRegistries` registers its dynamic
registries in its static initialiser, which goes through a Fabric mixin into `BuiltInRegistries`, so
the class fails to initialise and every test touching it fails with `NoClassDefFoundError` rather
than anything about registries. `fabric-loader-junit` (a test dependency, matching `loader_version`)
runs the tests under Knot with mixins applied, and `GameBootstrap.once()` then calls
`Bootstrap.bootStrap()` for the built-in registries themselves - vanilla refuses to register into
them before that, with "Not bootstrapped". Two layers, two different failures, and neither is a
game: no world, no server, no client. That is the line between tier 1 and tier 2.

The four traps of 0.4.0 are `ConfigCodecTest` (both write codecs, asserted against the record's own
component count so the test does not need editing when a field is added), `TableEntryCodecTest`,
`MemberSetTest` and `WearerPredicateTest`. What is still owed here is the row above them: every
shipped part, skin, cloth and loot group decoded and re-encoded to its own bytes, which needs a
`RegistryOps` over a registry access rather than plain `JsonOps`.

## What the gate is not

It is not CI. It needs a game, and the toolchain needs Mojang's textures on the machine; the web
editor's suites are what run in CI, and they cover the tools, not the mod.

It is not a replacement for looking at the game. Tier 3 asserts that a frame has not *changed*,
never that it is good; the first frame is always judged by a person. `review_post` is that seam and
the gate uses it rather than pretending.

It does not test other people's packs. Every check here runs over the mod's own content and over
packs the suite writes itself with `push_data`.
