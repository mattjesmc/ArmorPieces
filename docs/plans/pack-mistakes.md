# Plan: a pack author's mistakes

What the mod does when a pack is wrong. Everything that can be worked around is worked around and
warned about; everything that cannot is skipped, by name, and the world still opens.

---

## Measured today, 2026-09-11

A synthetic pack holding one `armor_decoration` file, loaded through `RegistryDataLoader` - the same
call a dedicated server makes - with the mod's own data stacked under it. One file, one mistake:

| the mistake | today |
| --- | --- |
| truncated JSON (`{ "asset_id": "probe:thing",`) | **the world does not open** |
| no `description` | **the world does not open** |
| `"anchors": []` | **the world does not open** |
| `"anchors": "crest"` (a string, not a list) | **the world does not open** |
| `"anchors": ["nose"]` (a socket that does not exist) | **the world does not open** |
| `"fittings": ["probe:no_such_fitting"]` | **the world does not open** |
| `"effects": [{"type": "probe:no_such_effect"}]` | **the world does not open** |
| one bad file beside one good one | **the world does not open**, and the good part is lost too |
| `loot` naming a table nothing defines | loads, and says nothing at all |

`ReportedException: Registry Loading`, from `RegistryDataLoader.load`. Vanilla's own log is not bad -
it names the registry, the element and the pack the file came from - but the outcome is that a
misplaced comma in one of a pack's ten files costs the player every part of every pack they have
installed, and on a dedicated server it costs them the world.

Three things about that table decide the design.

**It is the whole registry, not the element.** `RegistryDataLoader` collects per-element failures into
one map and throws at the end of the load. One unreadable file therefore takes down
`armorpieces:armor_decoration` entirely - the mod's sixty-six parts included - and the server never
reaches the point where anything could be reported to anyone.

**The throw lands on a background thread.** The load runs on Minecraft's background executor, whose
uncaught handler answers a `ReportedException` with `System.exit(-1)`. Measured here as a Gradle test
worker dying with `java.io.EOFException` and no reportable failure at all: the JVM was gone before
JUnit could write its report. A dedicated server does the same thing - the process ends, and whether
the owner ever sees a reason depends on where their console output went.

**Two cases already degrade, and they are the precedent.** A loot group naming a tag nobody installed
is an empty group rather than a dead world (`AbsentTagGroupTest`, and the tier-2 `missing-tag` boot
check). A saved item naming a part nothing defines keeps the part as raw bytes rather than losing the
item (`Tolerant`, `docs/plans/compatibility.md` §0). The rule this plan generalises is already written
down there: *a mod that will not open a world is a mod that gets a world deleted.*

---

## The contract

Three buckets, and every mistake belongs to exactly one.

**Worked around.** The file is readable and one part of it is not. The element loads without that
part: an unknown socket is dropped from `anchors`, a fitting id nothing defines is dropped from
`fittings`, an effect that cannot be read is dropped from `effects`, a loot row that cannot be read is
dropped from `loot`, a missing `description` becomes the element's own id. One warning per mistake,
naming the file, the field and what was dropped.

**Skipped.** The file cannot be read at all - broken markup, no `asset_id`, a record-level rule
refused it. That one element is skipped and everything else in the pack loads. One warning naming the
element, the pack it came from and the reason, and the element's id stays absent - which the item
half already handles, because a piece whose part is not installed is kept and rebound the day it is
(`Tolerant`).

**Reported only.** The file is legal and cannot do what its author meant: a part with no socket left
to sit in, a `loot` row naming a table no pack defines, a recipe whose anchor the part does not
allow, two shaped recipes with the same grid, a part whose `asset_id` has no geometry in any resource
pack, an id a second pack has overridden. Nothing to work around and nothing to skip - so it is a
line in the report, which is the only place a mistake like this has ever been visible.

Nothing in any bucket refuses the world, and nothing is silent.

### Where the report goes

`PackProblems` collects, in the shape `Rebind` already uses for missing ids: one line per distinct
problem, never one per item or per frame, with a running count.

- **The log**, grouped, once at the end of the load: how many problems, by bucket, then the lines.
- **`/armorpieces packs`**, at gamemaster level, listing them with the pack and file that caused each.
- **Operators on join**, one line, only when the report is not empty and only to somebody who could
  act on it - exactly the rule `Compatibility.advise` already applies to missing ids.

A client keeps its own report, because half the mistakes are art and art is only ever wrong on the
client.

---

## The mistake matrix

`tier` is the gate tier that asserts the row - see `docs/plans/testing.md`. A **skipped** element is
the mixin's work, and a mixin is not applied in a plain test JVM: so tier 1 asserts the rule it
applies (`PackSkips`, `MissingFittings`) and tier 2 asserts that it is wired to the loader at all, on
a real server with a real broken pack.

| the mistake | bucket | after | tier |
| --- | --- | --- | --- |
| broken markup in a registry file | skipped | the element is skipped, named, with the pack it came from | 1 (rule), 2 (wired) |
| no `asset_id` | skipped | skipped: a part with nothing to draw is not a part | 1, 2 |
| a record-level rule refuses it (`if_wearer` over a glider, a fitting predicate taking both material and dye) | skipped | skipped, with the rule's own message | 2 |
| no `description` | worked around | the element's id is its name, and the report says so | 1 |
| `anchors` holds a socket that does not exist | worked around | that socket is dropped; the rest stand | 1 |
| `anchors` is not a list of strings | skipped | the field cannot be salvaged, so the element is | 1 |
| `anchors` ends up empty | reported | the part loads, no loot offers it, nothing can apply it, and the report says so | 1 (loads, and no table offers it), 2 (reported) |
| `fittings` names an id nothing defines | worked around | the id gets an inert stand-in, so the part loads and that one fitting can never be filled | 1 (rule), 2 (wired) |
| `effects` holds one that cannot be read | worked around | that effect is dropped; the part keeps the others | 1 |
| `loot` holds a row that cannot be read | worked around | that row is dropped | 1 |
| `loot` names a table no pack defines | reported | nothing to add it to, said once per table | 2 |
| a loot group names a tag nobody installed | worked around | already true: an empty group | 1, 2 |
| two packs define one registry id | reported | the topmost wins, which is how packs work; every pack in the stack is named | 2 |
| two packs claim one `former_ids` entry or one `uid` | reported | the first claim stands, both named | 2 |
| a recipe hands out a template for a part that is not installed, or for a socket the part does not fit | reported | it can never be applied, said at load | 2 |
| two shaped recipes share one grid | reported | only the first is reachable, both named | 2 |
| `asset_id` has no geometry in any resource pack | reported | nothing is drawn, swept once per world join | not covered yet - tier 3 |
| a texture or a mask sheet is missing | not covered | vanilla's missing texture, and the bake's own log line | - |
| a lang line is missing | reported | the key is drawn, which is vanilla's answer; `tools/check_lang.py <pack>` is the author's | 0 |
| a synced element a client cannot read | skipped | the client drops it and says so; the piece is `Tolerant` on the item | not covered yet - tier 3 |

---

## The mechanism

**`pack/PackProblems`** - the collector, the report and the log. Static, like `Rebind`, and for the
same reason: a codec cannot be handed a service. Cleared when the server stops and rebuilt by every
load, so `/reload` never shows yesterday's problems.

**`pack/PackFile`** - which file is being read right now, as a thread local. `PendingRegistration
.loadFromResource` is where an element's JSON is parsed and decoded, and it is handed the element key
and the `Resource` (which knows its pack) - so a mixin at its head can name the file for every warning
raised underneath it, however deep in a codec. Without this a salvaged field is a warning that says
"some part somewhere", which is not something an author can act on.

**`mixin/RegistryLoadTaskMixin`** - `registerElements(Stream<PendingRegistration<T>>)` is handed every
element, resolved or failed, as `Either<T, Exception>`, and files the failures into the map that
becomes the crash. The mixin filters that stream for the mod's five registry keys and no others: a
failed element of ours is logged, filed in the report and dropped, and one bad file costs one part.
Every other registry in the game, vanilla's and every other mod's, keeps vanilla's behaviour exactly.

The same class serves the network path (`NetworkRegistryLoadTask`), which is a second win: a client
that cannot read a synced element - a part naming an effect type from a mod it does not have - drops
that element instead of being disconnected, and the item half already knows what to do with a part
that is not installed.

**Salvaging codecs** - `pack/Lenient`, over the list fields of `ArmorDecoration`: a list whose element
fails is a list without that element, and the drop is reported with the file `PackFile` names.
Deliberately not over `asset_id`: a part with no asset is skipped, not salvaged.

**`pack/MissingFittings`** - the one mistake none of the above can answer, and the reason is worth
keeping. A cross-registry reference is NOT resolved when it is read: the loader hands out a
placeholder holder, because the fitting a part names may be in a file that has not been read yet. The
reference is checked at the end, when the fitting registry freezes, and an id nothing ever defined
fails that freeze - `Unbound values in registry armorpieces:fitting`. That failure cannot be taken out
of the error map the way an element's can: a registry that will not freeze is **dropped from the
load**, so rescuing the error would leave the game with no fitting registry at all, which is worse
than the crash.

So the reference is made to resolve instead. Every fitting id a part names is written down as it is
read, and at the head of the freeze each one nothing defined is registered as a stand-in: a real
`material` fitting whose material set is empty, so no item can ever fill it. The world opens, the part
keeps its other fittings, and the report names the id. Install the pack that defines it and no
stand-in is ever made. The alternative - dropping the reference - is not available by then: the part
is built and registered, holding that very holder, and twenty-four call sites iterate the field.

**`pack/PackAudit`** - everything in the "reported only" bucket, run once per load at
`SERVER_STARTING` and at the end of every `/reload`, against the registries, the recipe manager and
the loot table registry. This is the pass that can see what a single file's codec cannot: that two
packs wrote the same id, that a recipe can never match, that a table nobody defines was named.

**`command/PackCommand`** - `/armorpieces packs`, beside `/armorpieces missing`, which is the same
question asked of the other half of the identity system.

---

## What this does not do

**It does not validate art.** A part whose geometry is nonsense - a zero-size box, a cube outside the
model - is the resource pack's business, and `DecorationGeometryManager` already drops one bad
geometry rather than the reload. What this plan adds there is the report line, not a judgement.

**It does not replace `tools/`.** `check_authoring.py`, `check_additive.py` and `check_lang.py` see
things no runtime can - a recipe grid collision across packs that are not installed together, a
painter that no longer reproduces its sheet - and they take a pack directory, so a pack author can run
all three against their own work. The runtime report is for the pack that is *installed*, which is
the only place a third party's mistake can ever be seen.

**It does not stub another mod's registry.** A fitting naming a trim material id that does not exist
dangles in *vanilla's* registry, and registering a fake trim material to paper over a typo is not this
mod's business. That one is still fatal, with vanilla's own message.

**It does not make a broken pack work.** A skipped element is missing content, and the report says so
plainly. The promise is that the cost of a mistake is proportional to it.
