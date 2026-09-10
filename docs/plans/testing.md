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
| the pool the mod adds to a loot table | 1 | one pool, rolled once, one entry per member at the best weight it was offered, and one `random_chance` at the highest chance any source asked for; the table's own pools untouched |
| the server's say over loot | 1 | the off switch, the multiplier and its clamp, and every field of a group override - `enabled`, `chance`, `weight`, `add`, `remove` - over a pack the suite writes |
| the pieces a foreign table uses (`armorpieces:template`, `armorpieces:set_decoration`) | 1 | both read out of a loot table file and written back unchanged, and `validate` names what could never come out of them: a tag nobody installed loads AND is reported |
| an effect gated on a fitting | 1 | `if_fitting` fires on the value in the socket and on nothing else: presence, one material, a tag of them, a dye colour, and a narrowing meeting the wrong SHAPE of value |
| what a worn part reaches | 1 | the walk from a living entity to the effects it wears: every armor slot head to toe and every socket on each piece, hands are not armor, a socket riding on the wrong piece is skipped, only the hook asked for is reached, the first refusal ends the question, and one context is built per socket |
| the numbers a part puts on its wearer | 1 | the modifier lands under an id scoped to its SOCKET, at the amount its material gets, transiently; a piece taken off takes it back; and a condition that stops holding while the piece stays on is taken back too - the removal is by what the effect COULD give |
| the two conditions as gates (`if_fitting`, `if_wearer`) | 1 | every hook forwarded while the gate holds and none while it does not - damage ALLOWED rather than refused, gliding REFUSED rather than granted - and a wearer condition with no server behind it holds nothing |
| the shape a part is drawn as | 1 | every shipped geometry parses into `DecorationGeometry` and bakes; and the bake's own rules - a bone is a place and a child rides on it, degrees become radians, a box is drawn at its true size and unwrapped on WHOLE texels, `inflate` grows the box and not the picture, a cube's `mirror` is its own, and `without` takes a bone and everything under it out |
| the loader that finds it | 1 | a file's own path is its id, the last pack to name one wins, a broken file costs that part and no other, and a fitting's variant is baked once and forgotten on reload |
| the colour a part is drawn in | 1 | every material's ramp, every static ramp, and every shipped part composited - master, static layer and filled masks - against what `tools/preview_material.py` produces, texel for texel; and the atlas read as a stack, so two material mods coexist |
| the garment a piece is wearing | 1 | the cut judged per FACE of the torso box rather than per texel; the design on the two panels and the base dye everywhere else; the mask's own value plus the armor's light through the same ramp a dyed inlay takes; the sprite's alpha read and its colour not; and a bake filed under a hash of the design |
| the skin bake | 1 | `SkinBakeTest`, already there; and the walk to it - which material an armor texture names, both its sheets measured together for the ramp and separately for the light, a material with nothing to measure, the size guard, a pack's own art beating the bake, and where a bake is filed |
| the wire | 1 | every shipped element, every filled socket, the five components and a whole `ItemStack` survive a `RegistryFriendlyByteBuf` round trip: the buffer drains, the payload keeps its size, the value comes back — and an uninstalled piece travels as raw NBT rather than taking its item down |
| the four smithing recipes' rules | 1 | every apply and clear recipe the mod ships, run over three real stacks: what crafts, every refusal (wrong socket, wrong slot, wrong metal, chainmail, a template with nothing on it), the routing an item decides, and the no-op guards |
| the four templates a player holds | 1 | one item per socket and no two alike; the name a template composes out of the part, fitting, skin or cloth it carries; the five lines each one promises, and the fitting template's narrowing when it names a fitting; and a template naming a part nobody has is still a template |
| the advanced table's slots | 1 | a display slot takes only armor that equips in it, and one of it; the two input slots take exactly what the smithing table's do, vanilla's own templates included; the preview slot is never drawn, filled or taken from; and a shift-click routes armor to its own slot, a template and a material to theirs, and anything else across the bag |
| what that table is working on | 1 | the selection follows the pieces in and out; a piece lists its own sockets and one row of its own, whose places are the trim, the skin and - only on armor a garment may go on - the cloth; every row and place has a button id of its own; and a row or place the piece can no longer support is dropped rather than left aiming at nothing |
| Remove | 1 | the five things it takes off, each from the place that names it; the last part off drops the component and leaves vanilla armor byte for byte; and every place the button lights on is a place Remove empties, the two swept together |
| Apply | 1 | the smithing table's own lookup over the table's three stacks - this mod's four recipes, a vanilla trim and a netherite upgrade - written back into the display slot and spending both inputs; the narrowing of a fitting to a picked socket or place, and the template's own choice beating it; and a result that could not go back in the slot it came from |
| the decorations tooltip | 1 | one heading, anchor order rather than map order, one line per effect, a fitting line only while it holds something, the missing-parts line last and its ids behind the advanced flag |
| the decorations map | 1 | a part written over a hole, `without` reporting nothing to remove, `pruned` dropping only the holes, and the saved form in anchor order |
| a world loads the mod's own pack | 2 | no `Failed to load`, no mod warning in `get_log` |
| loot groups | 2 | `/armorpieces loot list\|explain\|groups\|roll`, and `roll_loot` with a seed over the tables a group names — share and avg, not presence |
| `set_decoration` + `armorpieces:template` | 2 | a pushed foreign table hands out a part on the right socket template |
| a missing tag | 2 | the entry drops and the table still rolls — the 0.4.0 trap, as a test |
| the server config | 2 | written with every key; `enabled`, `chance`, `weight`, `add`, `remove`, the multiplier, and `/reload` picking up an edit in both directions |
| effects | 2 | equip through `/item replace`, then `/armorpieces effects` and `/attribute … get`: claws by material and by empty hand, head_fins in water, circlet on a set gem, heel_wings' jump number, cloak's per-material chance |
| the load-time refusals | 2 | a pushed part with a wearer condition over a glider, and over an attribute effect, each fails the pack with the message that names the test |
| stage command | 2 | `/armorpieces stage pieces\|random\|bases\|fittings\|skins\|table\|set\|clear` each answer |
| the four smithing recipes | 3 | the advanced table's SCREEN, driven by clicks: part, skin, cloth, fitting each produce the right output stack; `DisabledRecipe` produces nothing. The menu's own rules came down to tier 1 (2026-09-10); what is left here is the drawing, and the client branch a menu with no recipes takes |
| the decoration render layer | 3 | a golden frame per socket, on the studio floor, each also measured against the same figure without it |
| skins per material | 3 | eight materials of one skin, one frame each |
| cloth | 3 | tunic and tabard, chest and leggings, on a skinned pair and on plain iron |
| fitting colour | 3 | dye and banner fittings render their colour |
| the template items' icons | 3 | one frame of every template's model, in item frames (the creative tab cannot be opened from the bridge) |
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

> **All six landed (2026-09-07).** mcp-toolkit shipped them as the "consumer's gate", `RELEASE_1.md`
> section K, across 0.129.0-0.132.0, and this repository is now pinned to **0.134.0**
> (`build.gradle`). `create_world` with datapacks at creation and `get_tooltip` are registered in
> `McpToolkitClient` (`WorldCreation`, `TooltipTools`); the studio grew `{entity, equipment,
> freeze}`, which is asks 2 and 4; `ping` gained `build {started_at, mods_hash, mods}`, which is
> ask 6 and the answer to [[minecraft-bridge-port-collision]]; the manifest's `context` column is
> the documented server-only surface, ask 2's other half. Also new and useful here: `click {hover}`,
> which is the only way a tooltip is ever in frame.
>
> **Both tiers are built now** (2026-09-09 and 2026-09-10), and the asks below were re-read against
> what actually shipped before tier 3 was written. All six hold, with two corrections worth keeping:
> `studio {freeze}` is ask 4 in practice but is NOT used here (see "Tier 3, as built" - the partial
> tick keeps moving under it, so it does not pin a frame, and an armor stand needs no pinning), and
> the entity of ask 2 is `studio {entity, equipment}` rather than a tool of its own.

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

All five are built. The tiers are `python tools/gate.py --tier 0..3`, and the sections below are
what each one turned out to be.

## As built

Tier 0 and tier 1 run. `tools/gate.py` is the runner; `check_lang.py`, `check_effect_schema.py` and
`preview_material.py --reference --check` are new checks; tier 1 is `gradlew build`, and the JUnit
half grew from one test to six classes, and from six to **thirty-eight classes and 534 tests** as the
sections below were written.

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
`MemberSetTest` and `WearerPredicateTest`.

### The owed row, closed (2026-09-09)

Every shipped part, skin, cloth, fitting and loot group is now decoded and re-encoded, and so is
every one in `packs/`. The fixture is `src/test/.../data/ShippedData.java`, and it is a real
**datapack load**, not a hand-built registry: `RegistryDataLoader.load` - the call a dedicated server
makes - over `src/main/resources` and every `packs/*/datapack`, stacked on top of vanilla's own
built-in datapack (`ServerPacksSource.createVanillaPackSource()`). Five test classes ask questions of
it, and the suite went from 38 tests to 68:

| class | what it holds |
| --- | --- |
| `ShippedDataTest` | the files on disk and the registry are the same set; every element survives its own codec; a part's fittings are bound; every loot line and group is sane; no uid is used twice; no former id is also a live id |
| `PartAssetsTest` | every part's geometry parses AND BAKES through vanilla's `LayerDefinition`; its master sheet is there; a masked fitting has its mask; a replaced bone exists |
| `ShippedTagsTest` | every tag file this repository ships loads through `TagLoader`, has members, and names only ids that exist |
| `ShippedRecipesTest` | all 63 recipes decode through `Recipe.CODEC` and re-encode stably; all four smithing serializers are exercised by what ships; every template a recipe hands out names a piece that exists |
| `DecorationEffectsTest` | one sample per registered effect type (the registry is the checklist), `reaches` through a gate, and both `if_wearer` load-time refusals |

Four things had to be learned, and each is a trap for the next person:

- **Nothing may touch `ArmorPiecesRegistries` from a static initialiser.** JUnit loads a test class
  before any `@BeforeAll` runs, so a `static final Map` naming a registry key initialises that class
  before the game is bootstrapped, and the failure is a `NoClassDefFoundError` from a Fabric mixin.
  Both the fixture and the test use methods where a constant would read better.
- **Vanilla's trim materials must be loaded IN THE SAME PASS**, not handed in as a parent lookup. A
  tag resolved against a parent belongs to the loader's own wrapper for that lookup, so a fitting
  holding `#armorpieces:gemstones` decodes and then refuses to encode: "not valid in current registry
  set". Taking `Registries.TRIM_MATERIAL`'s entry out of `RegistryDataLoader.SYNCHRONIZED_REGISTRIES`
  and loading it with everything else is the fix; taking the whole list is not, because the rest of
  it is worldgen and `minecraft:overworld` will not parse without registries this pass has no reason
  to load.
- **Binding tags is two different calls, and which one is right depends on state.** An `Ingredient`
  names an item tag and binds it as it reads, so no recipe decodes until the tags are bound.
  `bindTags` refuses a frozen registry; `prepareTagReload` refuses an unfrozen one; and in a Fabric
  environment the built-in registries are still OPEN at the end of mod init, which is where a test
  JVM stops. An open registry also answers every tag with "Tags not bound" however the members were
  handed to it, so the order is: bind, then freeze.
- **A test JVM has to register the mod's own content**, not only its codecs: `GameBootstrap.content()`
  registers the components, block, items, recipe serializers, menu and loot pieces. Without it
  `data/minecraft/tags/block/mineable/axe.json` names a block that does not exist, and a tag with a
  missing member is not a smaller tag - the whole tag is dropped.

### Tier 2, as built (2026-09-09)

`python tools/gate/tier2.py` starts a dedicated server, asks it everything, and stops it again;
`tools/gate.py` runs it as the tier-2 check. Four files:

| file | what it is |
| --- | --- |
| `tools/gate/bridge.py` | the HTTP client for `127.0.0.1:25599`, plus the stale-instance guard |
| `tools/gate/scenarios.py` | the scenarios, and the `Game` helper every one of them shares |
| `tools/gate/fixtures.py` | the datapacks that have to be in the world BEFORE it loads |
| `tools/gate/tier2.py` | the runner: boot, attach, run, boot again for the load-time checks, stop |

Nine scenarios run against one server - `load`, `commands`, `stage`, `loot-groups`, `loot-rolls`,
`foreign-table`, `config`, `effects`, `identity` - and two more get a server each, because what they
are about happens while a world loads.

What the building taught, beyond the plan:

- **A registry entry cannot be pushed into a running game.** `push_data` + `/reload` is enough for a
  loot table, a recipe or a tag, and useless for a part, a fitting, a skin, a cloth or a loot group:
  those are datapack REGISTRIES, and vanilla reads a registry exactly once, when the world loads. So
  anything that needs new content of ours is a fixture pack written into the world folder before the
  boot (`fixtures.py`), and a scenario that would assert on one refuses to pass if it is missing.
- **A dedicated server can wear armor.** Half of `/armorpieces` refuses a console because it is about
  a wearer; `bot_body {action:"spawn", type:"player"}` puts a real headless player on the flat
  surface, and `item replace entity <player> armor.chest with <item>[armorpieces:decorations={...}]`
  dresses it. That is the whole of what the effects work was verified by hand, in one call.
- **An attribute is read a few ticks late.** Equipment lands immediately; the modifiers it carries
  are reconciled on the entity's next tick, so a read in the same breath measures what the wearer had
  before putting it on.
- **A game that refuses a datapack does not necessarily exit.** The toolkit's bridge holds the JVM
  open, so a boot check that waits for the process to end waits for its whole timeout and reports the
  right answer seven minutes late. The runner watches the log for "Failed to load registries" too.
- **Stopping a server means stopping the game, not the Gradle wrapper.** Terminating what was started
  leaves the game holding port 25599, where the next run finds it and mistakes it for its own.

**The gate's first tier-2 run found a defect, and it is the one this tier exists for.** A loot group
naming a tag no installed pack defines does not load as an empty set: it takes the WHOLE WORLD down,
with `Unbound tags in registry armorpieces:armor_decoration`. `LootGroup` binds its `parts`, `skins`,
`cloths` and `fittings` with `RegistryCodecs.homogeneousList`, which resolves a tag when the file is
read, while `MemberSet` - written for exactly this, and used by `TemplateEntry` - keeps the tag and
asks for it at the moment it is used. This is the cross-pack case the whole pack line rests on: a
player who installs one pack and not another. The `missing-tag` boot check is that finding, and it
fails until `LootGroup` uses `MemberSet`.

**Closed on 2026-09-10.** `LootGroup`'s four member fields are `MemberSet`s now, resolved where they
are used - `DecorationLootTables` passes the loot event's own registries, and `/armorpieces loot
groups` counts through `LootGroup.memberCount(registries)`, because how many members a group has is a
question only the installed packs can answer. Nothing about the FILES changed: both a tag and a list
of ids read and write exactly as before.

The finding also came down a tier while it was being fixed. `AbsentTagGroupTest` writes a pack into a
temporary directory - a loot group naming a tag nothing defines, and one naming `#armorpieces:knightly`
which the mod does - and loads it beside `src/main/resources` through `ShippedData.withPack`, the
same `RegistryDataLoader.load` a server runs. It is a true falsifier: put the eager binding back and
the test dies in the LOADER, before any assertion, exactly as the world did. A second boot-length
answer now costs a second, and the boot check stays as the proof that a real server agrees.

### The wire, closed (2026-09-09)

`ShippedWireTest`, eleven tests, half a second — the other half of `ShippedDataTest`. Everything
before it asked about the SAVED form; nothing had ever run a `STREAM_CODEC`, though a sync bug is
the one this repository has actually paid for: the 0.4.0 sub-predicate that a file wrote bare and
the client decoded full-id cost three `runClient` cycles and was found by a client disconnecting.

What it asserts, over every part, skin, cloth and fitting the mod and the packs ship, every socket
filled with a value its fitting type could really hold, the five components through the codec they
were REGISTERED with (`DataComponentType.streamCodec()`, so a component wired to the wrong codec
cannot pass), and a decorated helmet, a clothed chestplate and two templates as whole `ItemStack`s:

- the reader consumed exactly what the writer wrote — the misalignment that disconnects a client;
- the payload that came back writes the same NUMBER of bytes — the field a codec reads and does not
  write;
- the value equals what went in, and a holder sent by id comes back as its own registry entry.

Both halves of tolerance travel: a component holding a piece nothing defines is sent as raw NBT and
comes back as the same raw NBT, which is what keeps a creative client from handing the server a hole
where the player's part was. `lineageStaysOnTheServer` pins the opposite decision — `former_ids` and
`uid` are deliberately NOT synced, because rebinding happens where saves are read.

Two things had to be learned:

- **An item's default components are baked, not fixed at registration.** `Item.Properties` files an
  initializer, and `DataComponentInitializers.build(provider)` runs them against a registry provider
  at the end of a datapack load — because a default may point into loaded data (an emerald's
  `provides_trim_material`, `fireResistant`'s `#minecraft:is_fire`). Until that has run, every item
  holder answers `Components not bound yet` and `new ItemStack(Items.DIAMOND_HELMET)` throws. The
  fixture gained `ShippedData.bakeItemComponents`, and it bakes against
  `VanillaRegistries.createLookup()` rather than this repository's load: the bake reaches registries
  no file of ours points at (damage types, the animal variants), and none of those holders can ever
  reach the wire, since only the component PATCH travels and a default is not in it.
- **The wire may reshuffle what the save may not.** A part's `anchors` and a piece's sockets are
  `Set.copyOf` / `Map.copyOf`, whose iteration order is not part of the value, so encoding the same
  decorations twice can put the sockets in a different order. That is why the assertion is the
  payload's SIZE and not its bytes. `ArmorDecorations.CODEC` writes anchor order on purpose, and
  that is the half where it matters.

### The crafting rules and the tooltip, closed (2026-09-10)

Everything before this asked what the mod's data IS. Nothing had ever run the code a player actually
reaches: the four smithing recipes decide what may be crafted in `matches` and what comes out in
`assemble`, over three `ItemStack`s and nothing else, and 970 lines of that had no test at all — tier
3 photographs four happy rows through the advanced table's menu, and every refusal was unasserted.
Six classes, 54 tests, about four seconds:

| class | what it holds |
| --- | --- |
| `recipe/Bench.java` | the fixture: the shipped recipe files by name, the parts found by SHAPE rather than by id, and the stacks a player would lay in the three slots |
| `SmithingDecorationRecipeTest` | a part reaches its socket; a part is refused in a socket it does not declare, on a slot it does not belong to, with nothing to colour it and with no part on the template; re-applying keeps what is set in the fittings and is otherwise a no-op |
| `SmithingFittingRecipeTest` | the routing: an ingot to the guard and a dye to the inlay from the same slot, one gem to every part that takes one, a named template to its own fitting alone, the advanced table's narrowing to one socket, and the two clearing shapes |
| `SmithingSkinRecipeTest` | re-skinning is re-forging and the piece is asked; chainmail refuses by tag; a saddle is not armor; a skinned piece may always be unskinned |
| `SmithingClothRecipeTest` | the template brings the garment and the banner brings the colour and the layers; only the chest is clothable; stripping |
| `DisabledRecipeTest` | it matches nothing, has no display, is its own type, and swallows the body of the recipe it replaced — the contract the Blockbench plugin's disable/enable swap rests on |
| `decoration/ArmorDecorationsTest` | the tooltip and the map under it (the table above says what) |

Four things had to be learned, and each is a trap for the next test in this repository:

- **A `matches` that needs no level should be handed none.** Vanilla's `SmithingRecipe.matches` tests
  the three ingredients and reads the level for nothing, and no override here reads it either, so
  `Bench.NO_LEVEL` is `null` on purpose: the day one of them does need a level, that is a
  `NullPointerException` in a test rather than a surprise on a server.
- **An argument is evaluated before the call it is passed to**, so a fixture method cannot bootstrap
  the game on its way past: `Bench.stack(Items.IRON_HELMET)` initialises `Items` FIRST. In a JVM that
  has not been bootstrapped that fails `BuiltInRegistries`' class initialiser, and every later test in
  that JVM then fails with a `NoClassDefFoundError` naming a class that is not the problem — 44 of 44,
  from one line. Every class here has a `@BeforeAll` whose only job is to be that first line.
- **A trim material has to come out of the load.** An item's default components are baked against
  vanilla's own lookup (`ShippedData.bakeItemComponents`, and for its own good reasons), so the holder
  an iron ingot carries is a different object than the one a fitting's `materials` set was resolved
  against, and `HolderSet.contains` is identity. A game has one registry set and this fixture has two,
  so `Bench.providing` sets the component explicitly. Nothing about the mod is wrong here; a test that
  did not know it would report a routing bug that does not exist.
- **The decoration recipe's no-op refusal is in `assemble`, not in `matches`** — unlike the other
  three, which fold theirs in as `!assemble(input).isEmpty()`. Re-applying the identical part in the
  identical material MATCHES and then produces nothing, exactly as vanilla's own trim recipe does, and
  it is invisible to a player because both tables show an empty result slot (`AdvancedSmithingMenu
  .findResult` filters an empty result out, and vanilla's has nothing to put in the slot). It is
  visible to a caller that asks `matches` and then trusts it. Left as it is, and pinned by a test that
  says so, rather than quietly "fixed" into a fourth shape.

The tooltip is the other half, and it is the mod's only sentence to a player. Tier 3 reads a real
stack's tooltip out of a client and compares it with `description()`, which answers "is the line
there"; the decisions are the shape — one heading, the enum's order and not the map's, a line for what
a part DOES, no line for a fitting holding nothing, and the ids only under an advanced tooltip. Those
are asserted by TRANSLATION KEY rather than by text: no language is loaded in a test JVM, so
`getString()` flattens every line to its own key and drops the arguments that say which fitting holds
which material.

### The loot pool and the foreign table, closed (2026-09-10)

Loot was the largest thing in the mod with no tier-1 test at all. `DecorationLootTables` is 393
lines that run as every loot table in the game loads, and the only thing that had ever asked it a
question was tier 2, by rolling chests on a running server and measuring the share a group's members
got. That is the right question about ODDS and the wrong one about SHAPE: by the time a chest has
been opened ten thousand times, "one pool, rolled once, with one `random_chance` on it" has been
assumed rather than checked, and a second pool or a condition per entry would have read as slightly
different luck. The shape is the design — it is what keeps the odds a property of the TABLE, so a
ninety-first part changes which part is found and never how often. Two classes, 27 tests, about six
seconds:

| class | what it holds |
| --- | --- |
| `loot/LootTablesTest` | the mod run over a loot table exactly as a loading server runs it — the Fabric `MODIFY` event, the table's own builder — and the built table read back as JSON. The shape swept over every table anything this repository ships names; the overlap rules on a pack the test writes; and every field of the server owner's config |
| `loot/ForeignTableTest` | the two pieces the mod puts in SOMEBODY ELSE's table: `armorpieces:template` and `armorpieces:set_decoration`, parsed out of a loot table file and then `validate`d, which is the call that says at load what an entry could never hand out |

Three worlds, because each answers what only it can. **Everything this repository ships**, swept:
one pool, rolled once, one entry per member, at most one `random_chance`, and a `LootReport` that
agrees with the pool that was actually built — over every table any group or any `loot` row names,
which is the set no single file knows. **A pack the test writes**, where the numbers are the test's
own: two groups overlapping on one table are the only way to ask what an overlap decides, and the
generous group is deliberately the one the loader reads FIRST, because with it last "the highest
chance wins" and "the last chance read wins" build the same table and every assertion holds for
both. **That same pack under a server owner's config**: the off switch, the multiplier and its clamp,
and every field of a group override — `enabled`, `chance`, `weight`, `add`, `remove` — none of which
had been covered anywhere, and all of which reach a chest through this one class.

The suite is a real falsifier, and it was held to that: with `Offers.offer` changed to keep the last
chance rather than the highest and to overwrite rather than keep the best weight, five tests fail
naming the rule. The first shape of the fixture caught only three, which is how the ordering above
was found.

**It found one defect, and it is small and real.** A `LootReport` was dropped at the START of a
datapack reload and nowhere else — but a reload is not the only way one JVM sees two sets of packs.
A single-player client opens a world, quits to the menu and opens another, and the loot tables are
built afresh for the second world while the first world's explanations are still in the map, so
`/armorpieces loot explain` answers about a table this world never touched, naming a group it may
not even have. `register()` clears on `SERVER_STOPPED` too now, and the clearing is a named method
(`forget`) rather than a lambda, because the test JVM has no boundary of its own and has to stand at
one by hand.

Two things had to be built to ask any of this, and both are the kind of seam worth keeping:

- **`ServerConfigFixture`**, in the test tree but in the config package, hands `ArmorPiecesServerConfig`
  a file. The settings in force are a static that only `load()` writes, so nothing that reads them
  could be asked a question about a configured server; the fixture takes the config as the JSON a
  server owner would type and puts it through the same `CODEC` their file goes through, so a test
  that asks about an override also proves the override can be written down.
- **The event, not the method.** The tests fire `LootTableEvents.MODIFY.invoker()` rather than calling
  the mod's own function, because that the mod hangs on MODIFY is half of what makes its loot happen
  at all, and `register()` is the only place that says so. Once per JVM: a second listener builds
  every pool twice.

What is NOT here, and why: the ROLL. `TemplateEntry.expand` and `SetDecorationFunction.run` both go
through `context.getLevel()`, and a `LootParams` cannot be built without a `ServerLevel` — so what
comes out of the pool is tier 2's `foreign-table` and `loot-rolls`, and what the pool IS is here.
The pair the foreign-table tests do assert is the bargain the whole pack line rests on: a tag nobody
installed LOADS, and is SAID OUT LOUD as a problem. Either half alone is the wrong design.

**The gate a part is written around, closed the same day.** `decoration/fitting/FittingPredicateTest`,
seven tests: `armorpieces:if_fitting` is how a part says "only while there is an emerald in it", and
its codec and its `reaches` were covered while the thing a player actually feels - whether the gate
says yes to the gem that is in the socket - was verified only by equipping armor in a running game.
`FittingPredicate.test` is a pure function of two values, so it is a millisecond here: presence, one
material, a tag of them, a dye colour, and the case that matters most, a narrowing that meets the
wrong SHAPE of value. A fitting value is opaque by design, so a material test on a dyed inlay is not
an error - it is simply false, and a predicate that answered yes there would fire the effect on
every colour. The load-time refusal (material and dye at once, which can never be true) is pinned
beside it.

### Tier 3, as built (2026-09-10)

`python tools/gate/tier3.py` starts a client, builds a world, runs seven scenes and stops the game:
**114 seconds cold, and the frames come back bit-identical across two separate clients and two
separate worlds**, which is the fact the whole tier stands on. `tools/gate.py` runs it as the
tier-3 check. Three files beside the two tier 2 already had:

| file | what it is |
| --- | --- |
| `tools/gate/frames.py` | the golden store: compare, bless, and the three-panel diff a failure leaves |
| `tools/gate/scenes3.py` | the scenes, the item syntax they are written in, and the `Client` they share |
| `tools/gate/tier3.py` | the runner: boot, create the world, run, stop |

Seven scenes, forty goldens (564K in `tools/gate/goldens/`): `layer` photographs all twelve sockets
on one figure in iron plus the undecorated control, `skins` puts one skin on all eight armor
materials, `cloth` covers tunic and tabard over plain iron and over a skinned suit and a patterned
one, `fittings` covers a dye fitting's colour and a banner fitting's, `icons` photographs every
template item's model at once, and `tooltip` and `smithing` assert in WORDS rather than pixels.

**A golden is only ever written by `--bless`, and blessing is a person looking.** A frame with no
golden is reported `new` and fails the run with the path to open; a frame that changed fails with a
three-panel picture - golden, this run, the mask between them - and `--bless` then replaces it,
naming every golden it wrote. Nothing writes one on its own for any reason.

**Every frame is judged twice, and the second judgement is the one that finds a broken mod.** Beside
its golden, each decorated frame is measured against the SAME figure without the piece: a socket
that stopped drawing is "the same picture as the undecorated figure", by name, where a golden diff
would only have said that something moved. It is also what keeps a frame honest when the piece is
too small to see at 320 pixels.

What the building taught, and every one of these cost real time:

- **The camera and the subject face the same way, so the default frame is of the figure's BACK.**
  `studio` stands its subject facing the corner it puts the client in - which is -x -z - so a
  `render` at yaw 135 stands on the opposite side. Four sockets then measured as *zero pixels of
  difference*, and the natural reading of that is that the mod had stopped drawing them. It had not:
  a collar, a knee cop and a greave are on the FRONT of a body. The frame is yaw -45, and `back` and
  `spurs` are the two sockets shot from behind, because one camera cannot have both sides.
- **The subject must not breathe.** Vanilla's idle arm bob is driven by `ageInTicks`, and the PARTIAL
  tick keeps advancing under `/tick freeze`, so a player or a zombie drifts by around a thousand
  pixels between two frames - more than a whole small piece is worth. An armor stand has no bob and
  is stable to the pixel, which is why the figure in every frame is one.
- **The studio is a real place in a real world.** A wall the icons scene built and did not take away
  stood beside the figure in every frame afterwards; forty goldens were blessed with a grey block in
  the corner, and the next clean run failed all forty by exactly 1124 pixels. A run now sweeps the
  air around the studio floor once, and the icons scene takes its wall down in a `finally`.
- **Item syntax has exactly ONE component list.** `chestplate[skin=..][cloth=..]` is not a stack with
  two components, it is a parse error - and what it produced was a blessed golden of a skinned figure
  with no garment on it, a check that would have passed for ever while the feature was broken. Every
  stack goes through `components()` now, and `test_gate.py` pins it.
- **"The bridge answered" is three different moments.** The bridge answers while the game is still
  starting; the client's own tools (`create_world` among them) are registered later; and the client
  is only IN a world later still - `serverRunning` is true before that, and a `studio` in that window
  is refused with "no level loaded". The runner waits for the tool by name, then for
  `get_world_info`'s `world_uuid` and a player.
- **A screen answers in words, so it should be asked in words.** The advanced table's result is a
  real slot (`AdvancedSmithingMenu.PREVIEW_SLOT`, index 6), so what a recipe produced is read with
  `get_tooltip {slot: 6}` rather than photographed: the four smithing rows assert "Decorated / Lames",
  "Skin / Plate", "Cloth / Tunic" and "Inlay: Red", and the `DisabledRecipe` row pushes
  `{"type": "armorpieces:disabled"}` over `apply_skin.json` and asserts the table then makes nothing.
- **Coverage is mechanical for this tier.** `test_gate.py` reads the anchors out of
  `DecorationAnchor.java` and fails if the set of sockets the mod has is not the set tier 3
  photographs. A thirteenth socket cannot ship unphotographed.

What is NOT in it, and why: the plan asked for a frame of the creative tab, and there is no way to
open the creative inventory from the bridge - `send_keys` needs a screen already open and nothing
opens that one. The icons scene answers the same question better anyway: fifteen invisible item
frames in a grid on the studio's own wall is every template's model in one picture, with no window
size or scroll position in it.

### The colour a part is drawn in, closed (2026-09-10)

Tier 3 photographs twelve sockets in iron and one skin across eight materials, and those pictures are
the only thing that had ever looked at the client's own recolour. But the recolour is not art, it is
**arithmetic**, and it is what every part in every material with every combination of fittings is made
of: a part ships one greyscale master, `DecorationPalette` turns a trim material's eight-stop palette
into a 256-entry ramp, `DecorationTextureManager.recolour` indexes it by the master's red channel, and
`applyMask` lays a filled fitting's mask over the result. Sixteen materials times ninety-one parts
times every fitting combination is a number no golden store will ever hold; the arithmetic under them
is one class and it now has 192 tests, in about a second.

**And the same arithmetic is ported to Python**, because Blockbench and the site preview a part with
no client running (`tools/preview_material.py`, whose own first line says it is a port and the Java is
the original). That is exactly the bargain `SkinBakeTest` was written for, one feature earlier, so it
is the shape used again: `python tools/preview_material.py --reference` writes
`docs/plans/decoration-bake-reference.json` - every material's ramp, the static ramp of every dye and
of every colour the shipped static layers use, and a digest of the finished picture for 132 cases -
and `DecorationBakeTest` reads it back. The cases are three sweeps, and each answers something the
others cannot: every part in iron with nothing set, every part that has a mask in gold with all of
them filled, and `bandolier` - the one part that is a master, a static layer and two masks at once -
through every material there is.

| class | what it holds |
| --- | --- |
| `client/texture/DecorationBakeTest` | the ramps and the composited parts against the port; the ramp's three stops, its ordering and its refusals; the two rules the bake never breaks; where a bake is filed; and the atlas the palettes are found through |

The vanilla palettes come off the test classpath, out of the game jar the build already depends on,
so this needs no asset cache and nothing extracted - the same trick `SkinBakeTest` uses. Everything
the shipped art cannot express is asserted over images the test paints itself: a palette with one
stop and a key with no order (both "not a palette", which leaves a part untinted rather than dropping
it), a material with no palette at all, a mask over a transparent master, a mask with no ramp, and two
masks overlapping.

**It found a defect, and it is the exact class of thing a port has.** Python's `round()` rounds a half
to the nearest EVEN number; Java's `Math.round` is `floor(x + 0.5)`. So `round(14.5)` is 14 where the
game says 15, and every channel that lands exactly on a half - which is constant here, since halving
an odd channel and interpolating at t = 1/2 both do - came out one unit off. Nothing anybody would see
in a picture, and fatal to the only mechanism that could ever have checked: a digest that can never
match is a check that can never run. `_half_up` is the fix, in the port, because the port is the copy.

Three things the building settled, beyond the plan:

- **The arithmetic is package-private now, and that is the whole of the change to the mod.**
  `recolour`, `applyMask`, `bakedId`, `palette` and `loadPaletteMapping` were private, and every one of
  them is a pure function of images and a map read out of an atlas - no `Minecraft`, no GL, no world.
  Widened by exactly one step, with the reason written where they are declared. `NativeImage` itself
  works in a test JVM: it allocates off-heap through LWJGL and needs no context, which is what makes
  any of this possible.
- **The master's own digest travels with each case.** A repainted master changes the answer with
  nothing being wrong, and the test says so in those words - `bandolier.png has been repainted since
  the reference was written` - rather than accusing the arithmetic. It is also the coverage rule:
  `theReferenceCoversEveryPartTheModShips` reads the mod's own `armor_decoration` files and fails if
  one of them has no case, so a ninety-second part cannot ship uncoloured.
- **A reference is only half a check unless the gate watches it too.** The Java is held to the file,
  and nothing held the FILE to the port: a change in `preview_material.py` that was never regenerated
  would leave the game agreeing with a description of the port as it used to be. `python
  tools/preview_material.py --reference --check` regenerates it in memory and fails if it differs, and
  the gate runs it as the tier-0 `bake-reference` check. (`skin-bake-reference.json` has the same gap
  and no such check yet.)

Falsified rather than assumed, three ways: `MID_STOP` moved from 5/7 to 4/7 fails 149 tests; taking the
top `armor_trims.json` instead of the resource stack fails `everyPacksMaterialsSurviveTheAtlas` alone -
after the fixture was hardened, because the first shape of it put each pack's palette at the
conventional path, where the convention fallback answered for it and the mutation passed; and dropping
`applyMask`'s master-alpha guard fails `theMasterIsTheSilhouette` by name plus every case with a mask.

### The effects half, closed (2026-09-10)

Effects are the gameplay of this mod - the one thing a part does that is not paint - and everything
about them was checked in a running game or not at all. Tier 1 had the codecs (`DecorationEffectsTest`,
`MaterialValueCodecTest`, `WearerPredicateTest`, `FittingPredicateTest`), which say a part LOADS; tier
2 equips a piece on a dedicated server and reads `/attribute`, which says the whole chain works once.
Between them sat `DecorationEffectDispatcher` - the single walk from an entity to the effects it is
wearing, the only subscriber this mod has to the game's events, and the place every rule about
*which* effect runs lives - with no test of its own. Three test classes on two fixtures, 36
tests, under two seconds:

| class | what it holds |
| --- | --- |
| `decoration/effect/Wearer.java` | the fixture: somebody wearing decorated armor, with no world for them to stand in, plus the parts and pieces to dress them in |
| `decoration/effect/Spy.java` | effects with no behaviour, one hook each, that record being asked - including a gated attribute effect whose PRESENCE can be flipped between two reconciles |
| `EffectDispatchTest` | the traversal and the context: who is visited, in what order, and what they are told |
| `WornAttributesTest` | the modifiers a piece puts on its wearer, the socket scoping, the material's number, and every way one comes back off |
| `EffectGateTest` | the ten forwarding methods each gate is made of, in both directions |

**An entity can be had without a game, and that is the reusable fact.** `new Zombie(type, level)` is
unreachable in a test JVM - vanilla's `Entity` constructor asks the level for an entity id on its
first line - and a `Level` needs a server or a client. But the dispatcher reads exactly two things off
a wearer, `getItemBySlot` (a straight field read on `LivingEntity.equipment`) and `getAttribute` (the
attribute map, which is a pure data structure and takes transient modifiers happily). So the fixture
allocates a zombie without running a constructor, the way a save file does, and fills in the three
fields the walk touches - `equipment`, `attributes`, `random`. Anything a future change reads that is
not one of those three is a `NullPointerException` in a test rather than a silent pass. The wearer's
`level()` is null on purpose: that is the honest reading of "no server", and it is what
`WearerPredicate.test` already answers false to.

**The whole of the change to the mod is one extracted method.** `onEquipmentChange` began with
`if (!(entity.level() instanceof ServerLevel)) return;` and then did the work; the work is now
`equipmentChanged`, package-private, and the guard stays at the event where it belongs. Everything
below that line is a pure function of an attribute map and two item stacks - no level read, no event
fired, nothing sent - which is precisely why it can be asked here and why it is where the rules are.

Three things the building settled:

- **The removal is the rule, and it has two halves.** The dispatcher takes modifiers off by
  `collectPossibleAttributes` - what an effect COULD grant - rather than by what it is granting, in
  two separate passes: over the piece coming OFF, and over the piece still on when anything reconciles
  it. A test in which the gate held on the old item and not the new one catches neither, because the
  old item's gate offers the modifier either way. What catches them is an effect whose condition
  changes with the item standing still - the wearer picked up a sword, and the claws stopped biting -
  which is what `Spy.Gated` is. Each pass is now falsified by exactly one named test.
- **`if_wearer` holds nothing in a test JVM, and that is behaviour rather than a limit.** Vanilla's
  entity predicate needs a `ServerLevel`, so off a server the condition is false and what it gates
  does nothing - the same reason it may not gate a glider, which the client asks too. Asserted as what
  it is: nothing forwarded, gliding refused, and the modifier still offered to the removal.
- **A holder set only reads a bare id when the ops can reach the registry.** `{"items": "minecraft:air"}`
  is what the shipped claws write, and through plain `JsonOps` the same line is refused as "not a json
  array". Parse a predicate through the load's own ops. (And inside an effect, `Attributes` is the
  HOOK, not vanilla's list of them - a name clash that reads as a missing constant.)

Falsified five ways, each by exactly the test that names the rule: dropping the wrong-piece guard
fails `aSocketRidingOnTheWrongPieceIsSkipped`; returning the base id from `scopedId` fails four tests
about socket scoping; swapping either removal pass to `collectAttributes` fails one reconcile test
each; and dropping `holds` from `allowsGliding`, or folding `allowDamage`'s veto the wrong way round,
fails the two tests written for exactly those inversions.

What stays in tier 2, and why: everything an effect does to the WORLD. A mob effect applied to its
wearer, a blink's teleport, a glider's durability, the tick loop's own bookkeeping of who is wearing
what, and the `ServerLevel` guard itself all need a world to happen in. This tier answers which effect
runs and with what; that one answers what the world then looks like.

### The templates a player holds, closed (2026-09-10)

The item in the first slot is where every player meets this mod, and all four templates are the same
trick - one item with the content carried as a component, so a datapack adds a variant with no item
registration and no model. That trick puts two player-facing strings on each of them, both BUILT
rather than looked up: a name composed out of the content's own description, and a five-line tooltip
in vanilla's smithing-template shape. Neither had ever been asserted - tier 3 photographs the models,
tier 2 never opens an inventory - so "the crest template says a crest goes on a helmet" was a thing
only a person looking at a screen had ever confirmed. One class, 10 tests:

| class | what it holds |
| --- | --- |
| `item/TemplateItemsTest` | a template per socket and no two alike; the composed name of all four kinds; the lines each promises, including the fitting template's bare-versus-named narrowing; and a template for a part nobody has |

`everySocketHasATemplateOfItsOwn` is the coverage rule of the item half, the counterpart of tier 3's
"a new socket cannot ship unphotographed": a socket added to `DecorationAnchor` with no item is a part
that can be loaded, drawn and worn, and never obtained.

The last test is the one that looks least like a test and matters most. A template naming a part this
installation cannot resolve keeps the item's own name, still draws its tooltip, and says in one grey
line that a pack is missing - which is `Tolerant`'s rule seen from the item a player is holding
rather than from a codec. Falsified by deleting that line, and by fixing the socket template's
`applies_to` key to one socket: one named test each.

### The table a player crafts at, closed (2026-09-10)

`AdvancedSmithingMenu` is 843 lines, it is the mod's own crafting station, and nothing had ever
driven it but a person clicking. The four recipes had tests - over three `ItemStack`s, which is where
a recipe decides everything - but the MENU is where this mod says the things a smithing table cannot
say: which of four pieces is being worked on, which row of it, which place of that row, what Remove
empties, where a fitting lands, and that the result goes back into the slot it came from instead of
into a result slot. All of that is decided over the stacks in the table's own slots. None of it is a
game. Four classes, 56 tests, about a second:

| class | what it holds |
| --- | --- |
| `menu/Table.java` | the fixture: a table standing in a level that answers exactly one question |
| `TableSlotsTest` | what each slot takes, where a shift-click sends it, and that closing keeps nothing |
| `TableSelectionTest` | the piece, the row and the place being worked on, and what a change to the table does to them |
| `TableRemoveTest` | the five things Remove takes off - and the button that lights it, swept against it |
| `TableApplyTest` | the craft: this mod's recipes, vanilla's, the narrowing, and the result that has nowhere to go |

**The whole of the change to the mod is nothing.** The last two sections each widened something -
one extracted method, five methods made package-private - and this one needed no change at all,
because every rule here is already public: the screen reads all of it to draw. A menu whose state a
screen can read is a menu a test can read.

**A player and a level, allocated rather than constructed.** The trick is
`decoration/effect/Wearer`'s, one layer up: a menu is built out of an `Inventory`, which belongs to a
`Player`, who stands in a `Level`, and the constructor reads that level for the two ingredient tests
its input slots use. So the fixture allocates a `ServerLevel` subclass and a `Player` subclass
straight from the class, with no constructor run, and fills in the three fields the menu touches -
the level's recipe manager, the player's level, the player's inventory. Anything a future change
reads that is not one of those three is a `NullPointerException` in a test rather than a silent pass.

**The recipes are real, and there are more of them than this mod ships.** `Table.recipes()` reads
EVERY recipe out of the same stacked datapack the registries came from - vanilla's built-in pack and
this repository's - into a real `RecipeManager`, `apply` then `finalizeRecipeLoading`, the pair a
server runs in the order it runs them. That is what makes Apply worth asking about: the menu's claim
is that it runs whatever the recipe manager matched, "this mod's socket and fitting recipes, but also
a vanilla trim or a netherite upgrade", and a fixture holding only our sixty-three could not tell the
difference. It is also what the two input-slot tests stand on, since a `RecipePropertySet` is built
out of the loaded recipes and nothing else.

Three things had to be learned:

- **A vanilla FILE can name a registry this load had no reason to hold.** Every
  `minecraft:*_armor_trim_smithing_template_smithing_trim` recipe names a trim PATTERN, and
  `ShippedData` loaded trim materials and not patterns - so the first run of the fixture died on
  vanilla's own pack with "Registry does not exist". `Registries.TRIM_PATTERN` joins
  `TRIM_MATERIAL` and `DAMAGE_TYPE` in `NEEDED`, with the reason written where they are listed. The
  rule generalises: the set of vanilla registries a test load needs is decided by what it READS, and
  reading recipes reads more than reading our own five directories did.
- **`clearContainer` hands things back only to a `ServerPlayer`.** So where a stack GOES when the
  table closes is not askable here - vanilla's own code drops it on the floor of a fixture whose
  player is not one - and the test asserts the half the menu decides: that the display slots, the two
  inputs and the preview are all empty afterwards. A menu that forgot to empty the preview keeps it,
  since no container clear reaches that slot, so the claim still has a falsifier.
- **A sweep must not read its own bound from the thing it is mutating.** The first
  `everyPlaceRemoveEmptiesIsOneItSaidItWould` looked right and was half a check: its inner loop asked
  `placesAt(row)` after each Remove, and taking a part out of a socket leaves that row with no places
  at all, so the loop walked straight past the fitting places it exists to visit. It PASSED under a
  mutation that lit Remove on an empty fitting. Found by mutating the mod, not by reading the test -
  which is the argument for doing that to every rule a suite claims.

Falsified seven ways, each by the tests that name the rule: dropping the `fitsSlot` filter fails
`aResultThatIsNotArmorHasNowhereToGo` alone; taking the selected socket out of `assemble` fails the
two narrowing tests; swapping the skin and cloth places fails the two tests named after them; swapping
the division and the remainder in the fitting button id fails eleven; dropping `clampSelection` fails
the two tests about a selection that can no longer stand; commenting out the preview's own emptying
fails the closing test; and stopping the selection from following the pieces fails thirty-eight.

What stays in tier 3, and why: the SCREEN. The client has no recipes, so the menu asks
`level instanceof ServerLevel` in three places and takes the other branch there - Apply reports what
the server last published in the hidden slot rather than looking anything up - and there is no honest
way to stand a client level in a test JVM. That branch, and every pixel of the screen the slot
positions are shared with, is what a client run is for.

### The garment a piece is wearing, closed (2026-09-10)

`DecorationBakeTest` closed the arithmetic for a part one section earlier; this is its counterpart for
the third texture manager, and the last of the three bakes with nothing under tier 3. Cloth is the
only one that does not start from a greyscale master of its own: a garment ships a CUT MASK - alpha
says where the cloth is, red says how it folds - the colour comes off a banner the player made at a
loom, and what the armor underneath supplies is neither the silhouette nor the colour but the LIGHT.
Four tier-3 frames photographed all of that at once, tunic and tabard over plain iron and over a skin,
and a frame can only ever report that something moved. One class, 27 tests, about ten seconds:

| class | what it holds |
| --- | --- |
| `client/texture/ClothBakeTest` | the cut, the value, the colour, the design and the cache key - one rule per test, over images the test paints itself, plus every garment the mod ships composited onto a plate |

The rules pinned are the ones that break invisibly, and each is a decision rather than a consequence:

- **The clip is judged per FACE, not per texel.** A garment is worn ON the armor, so where the armor
  paints nothing there is nothing to hang it on - except on a face the armor uses nowhere at all,
  which is the top of the chest box on every vanilla material, and which is exactly where a tunic's
  shoulders and a tabard's straps live. An empty face is not a hole to respect, it is room to use.
  Made per-texel instead, the straps simply are not there, and a golden diff calls that "something
  moved".
- **Only the sprite's ALPHA is read.** Vanilla multiplies a banner sprite by its dye, which is right
  for a flag; here the shading is already the mask's and the armor's, and the two base sprites do not
  even agree what white is - a banner's is 224 grey and a shield's 145 - so sampling the colour would
  make every garment a shade of slate.
- **The value is the mask's own plus the armor's light**, through `DecorationPalette.ofStaticColour`:
  the same three-stop ramp a dyed inlay and a horn's ivory go through, which is what makes a dyed
  cloth and a dyed fitting beside it shade identically. Clamped at both ends rather than wrapped.
- **A bake is filed under a hash of the design**, because a banner is a colour and up to six patterns
  and that is not a path. Every part of the key is now falsified separately: drop the patterns, the
  dye, a layer's colour or the armor texture and one player's heraldry lands on another's back.

**The whole of the change to the mod is one extracted method and one split.** `bake` read the
resources, did the arithmetic and registered the texture in one body; the arithmetic is `composite`
now, package-private, taking the pictures it needs, and `pass` - which read a sprite and then painted
it - keeps the reading and hands the painting to `paint`. Everything below those two lines is a pure
function of images, a dye and a mask, which is precisely why it can be asked here. `paintedFaces`,
`clipped`, `panel` and `bakedId` are widened by the same one step, with the reason written on the
class, exactly as `DecorationTextureManager` was.

Three things the building settled:

- **There is no port to hold this to, and that is the honest position.** Skins have `bake_skin.py`
  and parts have `preview_material.py`, because Blockbench and the site preview both without a client;
  nothing previews a garment, so there is nothing to drift against. The reference is the rules, one
  per test, and the sweep at the end is what keeps them honest about real art: every garment the mod
  ships is composited onto a plate, and has to cover something and to cover NOTHING its own mask did
  not ask for. A mask saved at the wrong size or with its alpha flattened fails one or the other, and
  a third garment cannot ship having been baked by nobody.
- **Vanilla's `base` banner pattern draws with the base sprite.** The first shape of the
  base-pass-then-layers test took the first pattern in the registry, which is `minecraft:base`, and
  wrote its sprite to the same file the base pass reads - so one sprite was being asked two questions
  and the test failed for a reason that had nothing to do with the mod. The layer is picked by
  comparing sprite paths now, with the trap written beside it.
- **`Registries.BANNER_PATTERN` joins the three vanilla registries the fixture loads.** A design is
  banner layers and a layer holds a pattern by reference; a direct holder has no registered name, so
  a cache key built from one cannot be asked whether two designs collide. The rule from the last
  section generalises again: the set of vanilla registries a test load needs is decided by what it
  READS.

Falsified sixteen ways, each by the tests that name the rule: making the clip per-texel everywhere
fails the two tests about the shoulders; reading the sprite's colour fails `onlyTheSpritesAlphaIsRead`
and the blend test; starting the pass at the corner of the sheet instead of one depth in fails
`theNorthFaceIsTheOneTaken` and the resolution test; unclamping the shade, dropping the fallback for a
hole in the design, baking at the armor's own width, dropping the clip, dropping the armor's light,
sampling every garment off the shield's plate, dropping the base pass, dropping the layers, and
returning a panel for a design nothing could be read for each fail exactly the test written for them;
and four separate mutations of the cache key - the patterns, the dye, a layer's colour, the armor
texture - each fail `everyBakeIsFiledSomewhereLegalAndSomewhereOfItsOwn` alone.

What stays in tier 3, and why: whether the garment is in the right PLACE on the body. This tier knows
where the torso box is on the net and nothing about where the net is on a model, so a mask cut for the
wrong box would pass every test here and be obvious in one frame.

### The walk to a skin's colour, closed (2026-09-10)

The third texture manager, and the one whose promise is the largest: **nothing anywhere names a
material.** A skin ships two greyscale PNGs and no per-material art at all, and an armor material
another mod adds is skinned the moment it is installed, because the only thing wanted from that mod is
the equipment texture it must already ship to be visible on a body. `SkinBakeTest` holds the
arithmetic to `tools/bake_skin.py` texel for texel, and tier 3 photographs one skin on all eight
vanilla materials - but everything BETWEEN an armor texture and the ramp those two assume it already
has lives in `ArmorSkinTextureManager`, and none of it had ever been asked a question. One class, 13
tests:

| class | what it holds |
| --- | --- |
| `client/texture/ArmorSkinTextureTest` | which material a texture belongs to, where its colour comes from, what happens when there is nothing to measure, the size guard, the resolution order, and where a bake is filed |

The four rules, each of which is the whole of some promise this mod makes:

- **The material is the equipment texture's own FILE NAME**, under vanilla's equipment directory and
  nowhere else. That single line is the compatibility story; a decoration's sheet or a block texture
  names no material and is not baked for.
- **Both of a material's sheets are measured together for the ramp and separately for the light.**
  One ramp per material or the leggings drift away from the body they are worn under; one lightmap
  per sheet because the light on a leg is not the light on a chest. Held to `SkinBake`'s own
  functions, and with the falsifier stated in the test: the leggings genuinely move the table, so
  measuring the body alone fails rather than passing by coincidence.
- **A material with nothing to measure cannot be skinned** - an entirely transparent equipment
  texture leaves vanilla's own drawn - and a material with only one sheet (the turtle scute is a
  helmet and nothing else) is measured from that one.
- **A pack's own art for one material beats the bake**, which is the only reason an override exists;
  a skin with no sheet for a layer leaves that layer alone; and a sheet that is not the humanoid grid
  is refused before anything is read.

**The change to the mod is one extracted method and four widenings**, the same shape as the cloth
section: `colour` is the bake's arithmetic - `SkinBake.bake` plus the size guard, which is the one
decision in this class that is not `SkinBake`'s - and `material`, `materialName` and `bakedId` are
package-private with the reason on the class.

Two things the building settled:

- **`Minecraft.getInstance()` is safe in a test JVM as long as nothing is dereferenced.** It returns
  null rather than throwing, so `onResourceManagerReload` - which releases baked textures before
  re-indexing - runs fine while nothing has been baked, and the resolution order can be asked with a
  real resource manager and no client. That is what makes the three `resolve` tests possible without
  extracting anything.
- **A test whose fixture is transparent where it matters proves nothing.** The first size-guard test
  used a 32x16 master over an armor sheet whose top rows are empty, so every lightmap entry it
  indexed was zero: dropping the guard changed the picture not at all and the mutation passed. The
  master is 64x16 now and the test asserts up front that the texels it covers are lit. Found by
  mutating the mod, which is the second time in this repository that a green suite has been shown to
  be half a check that way.

Falsified eight ways: making any file name a material fails the not-an-equipment-layer test; leaving
the material's namespace or the sheet out of the cache key fails the collision sweep; measuring the
body sheet alone fails the ramp test; keying the measurement by texture instead of by material fails
three; applying the light whatever size the sheet is fails the size-guard test; offering the master as
its own override fails the override test; and dropping the humanoid-grid guard fails the test named
after it.

### The shape a part is drawn as, closed (2026-09-10)

The last of the three texture managers closed the walk to a part's COLOUR. This is the other half of
what a player sees, and it had never been asked anything: the geometry was loaded, baked and drawn,
and the only assertion anywhere was `PartAssetsTest`'s sweep, which bakes all 66 shipped shapes and
then throws the result away. What a part is SHAPED like was therefore held by a person looking at a
frame - tier 3, minutes, and a golden that can only say "different".

Two classes, 25 tests:

| class | what it holds |
| --- | --- |
| `client/geometry/DecorationGeometryTest` | the format and the bake: the bone tree, pivots and degrees, the sub-texel unwrap, `inflate`, `mirror`, `without`, the defaults, the refusals, the round trip |
| `client/geometry/DecorationGeometryManagerTest` | the loader: where it looks, which pack wins, what one broken file costs, and the variant cache |

The rules, each of which is a promise the format makes to somebody who will never read the Java:

- **A bone is a place and a child rides on its parent**, which is what lets a plume's tip be authored
  against its base and what will carry animation when it comes.
- **Rotations are degrees in the file and radians in the model.** Every modelling tool writes degrees;
  a part whose conversion went missing stands at 90 *radians*, which is a plausible-looking angle.
- **A box is drawn at its true size AND unwrapped on whole texels.** The one piece of arithmetic here
  that is not vanilla's: a 2.1-wide face would otherwise sample 2.1 texels and share its edge column
  with the face beside it, so the unwrap is rounded up and the box shrunk back through the cube
  deformation. Both halves are asserted separately, because either alone passes half the tests -
  `no-unwrap` fails only the texel test and `no-shrink` only the size test.
- **`inflate` grows the box and leaves the UV alone.** It is a fitting allowance, not a bigger box to
  paint.
- **A cube's `mirror` is its own.** `CubeListBuilder.mirror()` is sticky and no `addBox` overload
  clears it, so what keeps a flag from running down the rest of the bone is that every cube states
  the one it wants on the way in.
- **`without` takes a bone AND everything under it out of the bake** - a half-drawn banner is worse
  than none - and it is a bake rather than a `visible` flag because deferred rendering reads that
  flag back long after it was reset.
- **The loader's four**: the file's own path is the id, namespace and all; the last pack to name an id
  wins; one broken file costs that part and no other; and a variant is baked once, reused for an
  equal request, and forgotten on the next reload.

Three things the building settled:

- **A baked model is read back through `ModelPart.visit`, and only the VERTICES are the truth.** A
  `ModelPart.Cube`'s `minX..maxZ` are the box vanilla was handed before the deformation is applied,
  so the fractional unwrap reads there as 3 wide where the drawn box is 2.1 - a test that measured
  those fields would have blessed exactly the bug the unwrap exists to prevent. `visit` also hands
  out the accumulated transform and the bone path, which is what makes the hierarchy assertable
  without any rendering.
- **The loader is driven through vanilla's own `reload`**, not through a call to `apply`:
  `PreparableReloadListener.reload` is public and takes two executors, so `Runnable::run` twice and a
  barrier that completes immediately runs the real scan, the real codec and the real bake over real
  `PathPackResources` in a temp directory. That is what makes "the file's own path is the id" an
  assertion about the mod rather than about a constant copied into the test - moving the directory one
  level fails five tests.
- **The bake's own guard is nearly unreachable from a pack, and that is worth writing down.** `apply`
  catches a `RuntimeException` per part so one bad shape cannot abort a reload, but a geometry that
  DECODES has a name, three floats per coordinate and a positive sheet, and vanilla bakes nonsense
  numbers without complaint - a zero-sized box, a NaN, a box off the sheet. The only way to hand the
  loader something that throws is to build the record in Java, which is what that one test does.

Two findings, neither shipped:

- **A bone's own `mirror` does nothing.** `Bone.addTo` opens the builder with it and `Cube.addTo` then
  states the cube's own flag - false unless that box asked - before the first box is added, so the
  bone's is overwritten every time. No geometry in this repository or in any pack beside it writes
  `mirror` at all, on a bone or on a cube, and the authoring tools emit neither, so nothing shipped
  depends on either answer. Pinned as it is, with the test named after it and the fix written down in
  it: a cube with no flag of its own would have to inherit the bone's.
- **`builder.mirror(false)` after each cube is dead code** - every cube sets the flag on the way in,
  so removing the clear alone changes no bake. It is the set, not the clear, that is load-bearing.

Falsified twelve ways, each by the test that names the rule: `no-unwrap`, `no-shrink`, `no-radians`,
`no-inflate`, `fixed-sheet`, `leaky-mirror` (the natural implementation: turn the flag on for the box
that asked and leave it), `no-cube-mirror`, `shallow-without`, `no-variant-cache`,
`variants-survive-reload`, `no-empty-shortcut`, `wrong-directory` and `no-bake-guard`. The one
mutation that was NOT caught is the one above: dropping the redundant clear.

What stays in tier 3, and why: whether the shape is in the right PLACE on a body. This tier knows
where a box is relative to its bone and nothing about where the bone is relative to a shoulder, so a
part cut for the wrong anchor passes every test here and is obvious in one frame.

## What the gate is not

It is not CI. It needs a game, and the toolchain needs Mojang's textures on the machine; the web
editor's suites are what run in CI, and they cover the tools, not the mod.

It is not a replacement for looking at the game. Tier 3 asserts that a frame has not *changed*,
never that it is good; the first frame is always judged by a person. `--bless` is that seam - the
one moment a person looks and says yes - and the gate refuses to write a golden without it rather
than pretending.

It does not test other people's packs. Every check here runs over the mod's own content and over
packs the suite writes itself with `push_data`.
