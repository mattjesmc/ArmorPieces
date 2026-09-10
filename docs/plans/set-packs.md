# Set packs

> **Where this stands (2026-09-07).** The seam is **committed and pushed** in all three repositories
> (mod `4a98782`, editor `3a9277b`, site `97b47c6`). The **Animals pack is built and complete in the
> working copy and committed nowhere** — eight pieces, the Menagerie, both zips in `dist/`. It has
> **not** been seen in game, **not** released and **not** published; the user parked those on purpose.
>
> Before picking it up again, read "As built" below, then the Checks, Release and Publishing
> sections, which are still the plan.
>
> **The server question is settled, and not by us (2026-09-07).** mcp-toolkit 0.133.0 replaced the
> third-party Blockbench plugin with its own — a queue, a **session bound to a project**, and an
> edit to a piece another live session holds refused with `held_by` instead of landing in it. That
> is the active-tab hazard below, closed. **Pack 2 (Coral) is being built on it**, which is both the
> next theme and the live test.

Replaces the "mob parts" sketch in `docs/plans/0.4.0.md` §7. Same starting point — content that
ships **outside the mod**, as a pack, published on armorpieces.com — but organised as **one themed
set per pack** rather than as a bag of mob souvenirs.

The first is **Armor Pieces: Animals**, eight pieces and the outfit they complete. Coral follows,
then the five packs of `docs/plans/pack-line.md` — each its own pack, each built the same way.

---

## Why a set rather than a theme

"Mob parts" is unbounded: the Minecraft world is the scope, so no release is ever finished and no
two pieces have to agree about anything. A set is bounded and it compounds:

- **It has a shape.** Twelve sockets, one outfit, a material palette. A piece either belongs or it
  does not, which is a question a brief can answer.
- **It is finished when it is finished.** A pack ships, and the next theme is the next pack rather
  than a bigger version of this one.
- **It borrows.** A set fills twelve sockets but needs nowhere near twelve new pieces — the mod's
  six official sets are built entirely out of the 91. So eight new pieces plus four borrowed ones is
  a complete outfit, and every set after this one can borrow from these eight as well. That is the
  compounding: pack three is cheaper than pack one.

**One pack per set**, so a player installs the themes they want. `armorpieces-animals`,
`armorpieces-coral`, `armorpieces-dragon`, `armorpieces-nether` and the rest of the line — one
library entry, one install and one release cadence each. (A pack may later hold a *second* set
rather than becoming a second pack; see `pack-line.md`.)

---

## The seam: a pack that declares its own sets

**The finding that shaped this plan: a pack cannot declare a set today.** The mod's six live in
`StageCommand.java` as "an author's private furniture", are regex-parsed by
`.modpage/generators/armorpieces.py`'s `armorpieces.sets`, and reach the wardrobe as virtual rows
through `dist/site.json`. Nothing in a datapack, a resource pack or the library index can say "these
twelve pieces are an outfit". If set packs are the way content grows, that gap is the first thing to
close — otherwise every pack's whole point lives only in its description text.

It closes **without touching the mod**, using the precedent the credits file already set: a file at
the pack's root that the game ignores and the toolchain reads.

`armorpieces-sets.json`, beside `armorpieces-credits.json`:

```json
{
  "sets": [
    {
      "id": "menagerie",
      "title": "The Menagerie",
      "description": "Every creature in the world lent something to it.",
      "set": {
        "name": "The Menagerie",
        "slots": { "helmet": { "material": "leather" }, "...": {} },
        "pieces": {
          "horns": { "id": "armorpieces_animals:fox_ears", "material": "copper" },
          "crest": { "id": "armorpieces:comb", "material": "copper" }
        }
      }
    }
  ]
}
```

The inner `set` is **exactly the shape that already exists** — `docs/examples/set.json`, what
`bb_rig.py --wear` renders and what the site's `WardrobeSet` interface and `cleanSet()` validate,
down to the per-socket `{id, material, fittings}`. `SetPiece` even carries an optional `pack` field
already, described as "which pack it came from … so a set survives an id being reused". The seam was
anticipated; it was just never fed.

Three changes, none of them in Java:

1. **`tools/pack_manifest.py`** reads the file and emits a `sets` array, validating that every piece
   named is either in this pack or namespaced to another (a set may borrow, and borrowing across
   packs is the point).
2. **`build/make_library.mjs`** carries `sets` into each library entry, the way it already carries
   `pieces`.
3. **`ArmorPiecesSite/src/lib/wardrobe.ts`** — `officialSets()` reads the library index's entries
   as well as `generated('sets')`, giving each an id of `<pack id>-<set id>`
   (`armorpieces-animals-menagerie`) under the existing `OFFICIAL_PREFIX` scheme. Everything
   downstream — `/wardrobe/<id>`, `/wardrobe/<hash>.png`, the `/give` strings, the composed
   download — already works on any `WardrobeSet` and needs nothing.

A set naming a piece the viewer has not installed is not an error: the wardrobe already renders sets
that reference pieces from packs you have not saved, and the pack page is one click away.

**What the file is, said plainly (added 2026-09-07, `docs/plans/content-model.md` §5).** This is
*one way a pack submits outfits*, and nothing more. An outfit is its own thing - it has an author,
it names pieces from any number of packs, and it outlives the pack that shipped it. The wording
above, and the addressing scheme `<pack id>-<set id>` it proposed, read as though a pack OWNS the
sets it declares; the content-model plan replaces that with rows of their own, where a pack's
`armorpieces-sets.json` becomes provenance (`from_pack`) on an outfit that belongs to whoever
imported it. Nothing in the file format changes.

**How the seam actually reaches the website, which is the part that bites.** The site does not have
its own copy of the toolchain: `src/lib/tools.ts` runs the mod's Python under Pyodide **over the
editor's bundle**, `public/editor/app/repo.tar.gz`, and that bundle is a snapshot of a *commit of
the clone*. So a change to `pack_manifest.py` in the working copy reaches armorpieces.com only along
this chain, in this order:

1. commit the tool change to the clone and push;
2. rebuild the bundle **from the clone** — `make_bundle.py --repo <clone> --out web`, then
   `make_plugin.mjs --repo <clone> --out web`, then `make_site.mjs`; the clone needs
   `tools/.mcassets` copied in, and `--repo` must be named or both default to the working copy;
3. `make_library.mjs`, which now reads every pack through that bundle's `pack_manifest.py`;
4. the site's sync and deploy.

Until step 2, every pack reads as having no sets and nothing says why. `build/test_pyodide.mjs`
compares CPython over the working copy against Pyodide over the bundle, so it fails on exactly this
gap until the bundle catches up — set `ARMORPIECES_CLONE` to a **Windows-style** path when comparing,
or the root-stripping never matches and every tool that prints a path fails on the path alone.

**Roughly a day across the two repositories, and every future pack inherits it.** It is also the
honest test of the platform's central claim: somebody else's content, describing its own outfit, in
the same wardrobe as ours.

### As built (2026-09-06, working copy only, not committed)

All three changes are in, and green. Four departures from the sketch above, each worth keeping:

- **`sets_of()` validates rather than trusts**, because the file is hand-written and the next thing
  to read it is a web page. Five refusals, each with a warning naming the file: an id that is not a
  slug, a duplicate id, a set with no `set`, a piece named without a namespace, and — the one that
  matters — a piece in the pack's *own* namespace that the pack does not contain, which is dropped
  rather than rendered as a hole nothing downstream could explain. A foreign id is passed through
  untouched and counted as `borrowed`.
- **The manifest reports `sockets` and `borrowed` per set**, so the gallery can say "twelve sockets,
  four borrowed" without re-reading the set body.
- **`PackSet.set` is typed `unknown` in `library.ts`**, not `WardrobeSet`: it is somebody else's
  JSON until `cleanSet` has been over it, and typing it properly would make `library.ts` depend on
  `wardrobe.ts`, which depends on `library.ts`.
- **`OfficialSet` grew `pack` and `packName`**, and the two pages stopped saying "the mod's own"
  about everything they did not find in the database. A pack's set is credited to its pack and links
  back to it; only a set with no `pack` claims to ship with the mod. `libraryIndex()` gained a
  `LIBRARY_INDEX` override, the way storage already has `DATA_DIR`, so the test could add an entry
  without editing the synced file every other test file reads at the same time.

Verified: `pack_manifest.py` on a fixture pack (all five refusals fire, the good set survives with
its borrowed piece); the same under **Pyodide** through `build/test_pyodide.mjs`, which is how a
server reads a pack, on a bundle rebuilt from the working copy (then reverted — the committed bundle
must stay a snapshot of a commit); the site's **44 tests green**, including a new one that a pack's
set is listed, credited to the pack, opens on its own page, links back and is no more a row than the
mod's six are. `astro check` was not run: `@astrojs/check` is not installed in this project and
offers to install itself, which is not this change's business.

---

## Pack 1: Armor Pieces: Animals

| | |
|---|---|
| source | `packs/animals/{datapack,resourcepack}` in this repository |
| namespace | `armorpieces_animals` |
| library id | `armorpieces-animals` |
| display name | Armor Pieces: Animals |
| version | 0.1.0 |
| requires | Armor Pieces 0.4.0 or later |
| licence | **CC BY 4.0** — open and free, credit kept |
| release | `mattjesmc/ArmorPieces`, tag `animals-0.1.0` |

**Two folders, not one**: it is how the game installs a pack (a world's `datapacks/` and the game's
`resourcepacks/` are different places), how the library entry publishes one (two zips), and what
`export_pack.py` zips. The Blockbench plugin takes the halves separately already.

`pack.mcmeta` carries `min_format` and `max_format`, never a bare `pack_format` — past resource 64 /
data 81 the game rejects it, falls back to a description-only metadata type and silently ignores the
contents. For 26.2 that is **resource 88, data 107**.

### Licence

**CC BY 4.0**, decided: open and free, credit kept. The mod's own pieces are `ARR` and stay that way;
this pack is the one that is meant to be copied, because a pack whose purpose is to show outsiders
how to make one has no business being closed.

Consequences, all of them wanted:

- `pack_manifest.py` already knows `CC-BY-4.0` and marks it **`compose: true`**, so the site's
  composer may copy these pieces into other people's packs — the first content on armorpieces.com
  for which that is true.
- `armorpieces-credits.json` carries `"license": "CC-BY-4.0"` at the pack level, so every piece
  inherits it and the gallery says so on each card.
- The `LICENSE` at each half's root is the CC BY 4.0 text, **not** the mod's — the two are
  different things and a pack zip is the easiest artifact in the project to re-host, so its terms
  have to travel inside it. The library entry says `"license": "CC BY 4.0"`.
- Attribution is "mattjes, armorpieces.com".

MIT was the other half of the instruction and is the wrong tool: it is a code licence, and
`pack_manifest.py`'s table does not carry it, so choosing it would mean editing the mod's tooling to
describe a pack. `CC0-1.0` is the same decision with the attribution line dropped, is already in the
table, and remains a one-word change if that is preferred later — though only before the pack is
published, since a licence cannot be narrowed after the fact.

### As built (2026-09-07, working copy only, not committed)

**All eight authored, the pack complete.** Nine sessions (Armadillo took three attempts — see the
launching note below), **$28.16**, about two hours of editor time. Every save was accepted
**without `force`**: eleven save calls across the batch, zero rejections.

| piece | socket | turns | min | cost |
|---|---|---|---|---|
| fox_ears | horns | 36 | 8.5 | $2.80 |
| frog_mask | brow | 30 | 7.3 | $2.14 |
| bee_wings | pauldrons | 48 | 8.9 | $3.24 |
| turtle_shell | back | 39 | 10.7 | $3.40 |
| flower_brooch | collar | 60 | 19.1 | $5.67 |
| donkey_tail | belt | 47 | 8.8 | $2.95 |
| armadillo_shell | knees | 68 | 14.2 | $5.53 |
| rabbit_feet | spurs | 37 | 8.2 | $2.43 |

The data half was written afterwards, by hand, because no session touched it: the tag
`armorpieces_animals:menagerie` over all eight, `loot_group/village.json` at 0.05 over the seven
village chests, and the single entity probe — a `loot` row on `rabbit_feet` for
`minecraft:entities/rabbit` at 0.05. Every piece now reads **"crafted + found"** in the manifest.

**The art holds, checked mechanically across all eight**: no static or mask pixel outside its
master's silhouette, no non-grey pixel on any master, and **every static colour in the pack comes
from that mob's own extracted palette** — nothing invented, which is what the reference tooling was
for. Two shapes of hardware both appear and both are right: a mask-only clasp or rim takes the
wearer's material when no fitting is set (bee, turtle, armadillo, donkey), while a face that is both
static and masked reads as itself bare and jewelled when a gem is set (frog's eyes, rabbit's cap).

`armorpieces-sets.json` carries **The Menagerie**: twelve sockets, eight this pack's and **four
borrowed** from the mod (`comb`, `mittens`, `pelt`, `puttees`), on leather with copper hardware. The
manifest reads it as `12 sockets, 4 borrowed`, and it survives the **two-zip merge** that
`make_library.mjs` performs — which is the path it will actually reach the website by.

Both halves export reproducibly: `armorpieces-animals-0.1.0-datapack.zip` (22 files, 8.4 kB) and
`-resourcepack.zip` (35 files, 21 kB), and re-import to the same eight pieces and one set.

**Not done yet: the in-game pass, the release and the publish.** Nothing has been committed, no
release exists, and no piece has been seen on a player in the game.

### The eight pieces

Eight animals, eight sockets, none of them shadowing one of the 91 — which rules out the generic
`ears`, `pelt`, `claws`, `tusks`, `carapace` and `feathering` that already shipped, so each piece has
to read as a **named animal** rather than as fur in general.

| piece | socket | animal | static colour (the animal) | fitting (the hardware) | recipe centre |
|---|---|---|---|---|---|
| `fox_ears` | horns | Fox | orange fur, cream inner ear, dark tips | none — a dyed fox is not a fox | `minecraft:sweet_berries` |
| `frog_mask` | brow | Frog (**cold**) | green hide, pale gold throat | gemstone, as the eyes | `minecraft:lily_pad` |
| `bee_wings` | pauldrons | Bee | yellow and black bands, pale wings | guard, the shoulder clasp | `minecraft:honeycomb` |
| `turtle_shell` | back | Turtle | olive scutes, green rim | guard, the rim and straps | `minecraft:turtle_helmet` |
| `flower_brooch` | collar | — (a poppy) | red petals, green stem | gemstone, as the pollen | `minecraft:poppy` |
| `donkey_tail` | belt | Donkey | grey-brown hair | guard, the ferrule | `minecraft:lead` |
| `armadillo_shell` | knees | Armadillo | banded brown-pink plates | guard, the edging | `minecraft:wolf_armor` |
| `rabbit_feet` | spurs | Rabbit (brown) | brown fur | gemstone, the charm's cap | `minecraft:rabbit_foot` |

Eight distinct sockets, so no two can ever be worn against each other, and the crowded `brow`
(fourteen shipped parts) takes only one.

**Each as a one-line model brief:**

- **Fox Ears** — two upright triangles rising off the helmet's crown, wide at the base, canted
  slightly out, dark at the tips, a notch of inner ear cut into the front face.
- **Frog Mask** — the frog's whole face as a plate over the brow: two domed eyes standing proud
  above the helmet line, a wide flat mouth line beneath, nostrils two texels apart. **The cold
  frog**, which is the green one — 26.2's *temperate* frog is orange and the *warm* one is grey,
  and a frog that is not green does not read as a frog. Worth knowing before it is drawn, and the
  kind of thing only reading the actual palette catches.
- **Bee Wings** — two pairs of short rounded wings at the shoulder blades, the rear pair half the
  length, held out and slightly back, veined by the dye fitting.
- **Turtle Shell** — a low domed shell across the back, six hexagonal scutes ridged at their seams,
  a scalloped rim standing off the chestplate.
- **Flower Brooch** — a five-petal bloom at the throat on a short stem collar, the gemstone set at
  its centre as the pollen.
- **Donkey Tail** — a plaited tail off the belt at the back, tufted at the end, hanging to the
  middle of the thigh and swinging clear of the leggings' shell.
- **Armadillo Shell** — banded plates over each knee, three bands, the middle one widest, curling
  round the outside of the joint the way the animal's do.
- **Rabbit Feet** — one charm behind each heel: a foot on a short thong, the gemstone as its cap.

**Reserve, for the next Animals release** — every one of these is a real idea that lost on socket
contention, not on merit: rabbit ears, panda ears, goat curl (all `horns`, contested by the fox);
villager nose, chicken beak with its wattle (both `brow`, contested by the frog — note vanilla has
**no duck** in 26.2, so the bill with a lobe becomes a chicken's); axolotl frills (`crest`); panda
paws (`vambraces`); sniffer fringe (`crest`); parrot perch (`pauldrons`).

### Looking like Minecraft: reference, and where colour lives

**The thing that makes a mob recognisable is its palette, not its shape.** At sixteen pixels nothing
is recognisable by silhouette; a fox is eleven colours of which three are 62% of it. Guessing those
three is the one part of authoring an animal piece that no amount of care in Blockbench recovers
from — so no piece here gets authored without the mob's own colours in front of the author.

`tools/mob_reference.py` (new, built 2026-09-06) reads the mob's texture out of the game and prints
every colour in it, ranked by coverage, with the greyscale **value** each one carries:

```
entity/fox/fox.png  48x32, 11 colours
  hex      share  value
  #cc6920   26.6    126     #b05122  17.8  104     #e27c21  16.7  144
  #d5b69f   10.7    189     #f9f4f4   6.0  245     #06040e   4.0    6
```

`--extract` also puts the texture under `tools/.mcassets/reference/`, with an `@8x` nearest-neighbour
copy beside it that is actually legible in a conversation, and `--bake` writes
`tools/.webcache/mob_palettes.json` so an author with no jar still has the numbers. It takes items
and blocks too (`poppy`, `honeycomb`), for the pieces not taken from an animal. Nothing is
redistributed: the palette is *numbers* derived from the game, which is exactly what `.webcache`
already keeps (the trim ramps, the armor shades), and the extracted PNGs land in `.mcassets`, which
is gitignored and stays on this machine.

**And this decides where the colour goes, which is a design constraint, not a brief detail.** A
piece is three layers: the `master` is greyscale and its value is a position on the **wearer's trim
material ramp**, so anything drawn there turns iron, gold or netherite with the armor. Only
`<part>_static` keeps its own colour — shaded by the master's value. So:

> A fox drawn on the master alone is a fox-shaped piece of iron.

Every animal colour in this pack belongs in the **static layer**, and the master carries the form
and shading underneath it (the palette's `value` column is what to paint there, so the shading
agrees with the colour instead of fighting it). Only genuine hardware — a clasp, a rim, a buckle —
stays on the master where it can follow the armor.

That makes this **the most static-heavy pack in the project**: 11 of the mod's 91 pieces have a
static layer, and seven of these eight need one. It also re-reads the fitting column above — a
fitting is no longer "what colour is this piece", it is the metal or the gem on the *hardware*: the
frog's eyes take the gemstone, the turtle's shell gets a metal rim, the rabbit's charms are capped,
the fox's ears carry no fitting at all, because a dyed fox is not a fox.

### The set: The Menagerie

Twelve sockets. Eight new, **four borrowed from the mod** — which is the whole argument for building
this way.

| socket | piece | from |
|---|---|---|
| crest | `armorpieces:comb` | the mod — a rooster's comb, and it was always an animal piece |
| brow | `armorpieces_animals:frog_mask` | new |
| horns | `armorpieces_animals:fox_ears` | new |
| pauldrons | `armorpieces_animals:bee_wings` | new |
| back | `armorpieces_animals:turtle_shell` | new |
| collar | `armorpieces_animals:flower_brooch` | new |
| vambraces | `armorpieces:mittens` | the mod — paws |
| belt | `armorpieces_animals:donkey_tail` | new |
| tassets | `armorpieces:pelt` | the mod |
| knees | `armorpieces_animals:armadillo_shell` | new |
| spurs | `armorpieces_animals:rabbit_feet` | new |
| greaves | `armorpieces:puttees` | the mod — rustic cloth wraps |

Built on **leather** armor with **copper** trim on the metal fittings and green-brown dyes on the
inlays: nothing about the Menagerie should read as a knight.

### How they are had

The rule: the difficult mobs drop theirs, everything else is crafted or found. **Every animal here is
easy**, so the pack is craft-first, with two secondary routes:

- **Eight recipes.** The template ring is `minecraft:paper` around one centre, and the centre *is*
  the recipe — two recipes sharing a centre is one silently unobtainable piece. All eight centres
  above are the animal's own product where one exists (`rabbit_foot`, `honeycomb`, `turtle_helmet`,
  `wolf_armor` — which vanilla makes from armadillo scutes) and were checked free against the mod's
  51 in use. The obvious picks are already taken: `goat_horn`, `turtle_scute`, `armadillo_scute`,
  `phantom_membrane`, `feather`, `leather`, `rabbit_hide`, `string`, `dandelion`, `pink_petals`.
- **A village group.** `loot_group/village.json` at `chance: 0.05` over the seven village chest
  tables, naming the pack's own tag `#armorpieces_animals:menagerie`. The tag lives in the pack's
  namespace, so nothing of ours is edited to create it.
- **One entity probe.** `rabbit_feet` carries an exact `loot` row on
  `minecraft:entities/rabbit` at `0.05` — thematically right (vanilla already drops a rabbit's foot
  rarely), and it is the one place this pack exercises the **entity-table route** at all. The Boss
  pack is where that route gets its real test; this proves it fires before we build a pack that
  depends on it.

**The overlap with `wayfarer` is expected behaviour and is worth watching.** The mod's own wayfarer
group already names five of those seven village tables at `0.08`. Where two groups name one table
the result must be **one pool, rolled once, at the higher chance** — so village chests get *more
varied*, not richer. That invariant is the foundation of the whole loot design and has never once
been observed across two separate packs. `/armorpieces loot explain
minecraft:chests/village/village_shepherd` should name both groups and a single 0.08.

---

## Pack 2: Armor Pieces: Coral

The second set pack, and the first built on the toolkit's **own** Blockbench plugin
(`mcptoolkit_bridge.js`, mcp-toolkit 0.133.0+). It exists for two reasons at once: it is the next
theme in the line, and it is the live test of that bridge — so the "As built" note below has to say
what the new plugin changed about authoring, not only what the pieces look like.

Namespace `armorpieces_coral`, licence CC BY 4.0, `packs/coral/{datapack,resourcepack}`, same as
Animals in every structural way.

### Four pieces, eight borrowed

Animals needed eight new pieces to fill twelve sockets. This one needs **four**, because the mod
already ships the tidal half of a diver: that is the compounding the plan claimed, stated as a
number. A future pack can borrow from these four as well.

| piece | socket | subject | static colour (the reef) | fitting (the hardware) | recipe centre |
|---|---|---|---|---|---|
| `coral_crown` | crest | a reef growing off the crown of the helm | horn, fire and tube coral | `guard` — the band it grows from | `minecraft:brain_coral_block` |
| `axolotl_frills` | horns | the three feathery gills, one temple, mirrored | lucy pink | none — a frill is not hardware | `minecraft:axolotl_bucket` |
| `kelp_mantle` | pauldrons | kelp fronds hanging over both shoulders | kelp greens | `guard` — the cord and toggle | `minecraft:kelp` |
| `nautilus_gorget` | collar | a nautilus shell spiral at the throat | shell cream and brown | `guard` — the clasp holding it | `minecraft:nautilus_shell` |

Two of the four carry hardware and two do not, which is the balance Animals arrived at: a fitting is
the *hardware* (a band, a cord, a clasp), never "what colour is this piece". Colour lives in the
static layer, because a master is greyscale and its value is a position on the **wearer's** trim
ramp — a coral drawn on the master alone is a coral-shaped piece of iron.

**Two names deliberately shadow a mod piece in their own socket**: `mantle` is already on
`pauldrons` and `gorget` is already on `collar`. That is not the mistake Animals avoided. Animals
could not use `ears` or `pelt` because those are *generic* — the pack's whole claim was that each
piece reads as a **named** animal. `kelp_mantle` and `nautilus_gorget` read as named things already;
the qualifier is the subject. In the socket picker they sit beside the plain ones as what they are,
the same garment made of something.

### The palettes, read out of the game

`python tools/mob_reference.py <name>` for each; every static pixel in this pack must come from one
of these tables, exactly as it did for Animals. The `value` column is what goes on the master
underneath, so the shading agrees with the colour instead of fighting it.

| subject | hex | share | value | what it is |
|---|---|---|---|---|
| horn coral | `#e4da4a` | 19% | 205 | the lit tip |
| | `#d5cb3e` | 21% | 190 | the pale yellow body |
| | `#d1b341` | 25% | 175 | the ochre body |
| | `#b68930` | 24% | 140 | the shaded underside |
| fire coral | `#e23f36` | 16% | 111 | the lit edge |
| | `#c62a37` | 22% | 90 | the red body |
| | `#a4222f` | 29% | 74 | the shaded body |
| | `#791a26` | 33% | 56 | the deep red root |
| tube coral | `#3f6ce5` | 18% | 108 | the lit blue |
| | `#405ce2` | 14% | 99 | the blue body |
| | `#314fdd` | 25% | 86 | the shaded blue |
| | `#1c3788` | 24% | 56 | the dark root |
| axolotl (lucy) | `#fbc1e3` | 30% | 214 | the pale pink body |
| | `#f3add6` | 12% | 199 | the next pink down |
| | `#e384bc` | 17% | 167 | the mid pink — the frills |
| | `#c8629e` | 19% | 135 | the deep pink — the frill roots |
| | `#b14283` | 7% | 107 | the darkest pink, edges only |
| kelp | `#59ab30` | 28% | 132 | the lit frond |
| | `#5c8332` | 28% | 110 | the green body |
| | `#5e7025` | 14% | 98 | the shaded body |
| | `#55671e` | 15% | 89 | the darker shade |
| | `#415011` | 14% | 68 | the deepest green, edges |
| nautilus shell | `#d4ccc3` | 15% | 205 | the pale rim |
| | `#baad96` | 18% | 174 | the cream body |
| | `#a6846a` | 24% | 139 | the tan body |
| | `#8a6a53` | 10% | 113 | the shaded whorl |
| | `#6d533f` | 17% | 88 | the deep brown groove |
| | `#ae4635` | 3% | 99 | the rust stripe, sparingly |

### The set: The Reef

Twelve sockets, **four this pack's and eight borrowed** from the mod, on `turtle_scute` with
`copper` hardware — verdigris and scute, which is what the sea does to metal.

| socket | piece | material |
|---|---|---|
| crest | `armorpieces_coral:coral_crown` | copper |
| brow | `armorpieces:spectacle_visor` | copper |
| horns | `armorpieces_coral:axolotl_frills` | turtle_scute |
| pauldrons | `armorpieces_coral:kelp_mantle` | copper |
| back | `armorpieces:carapace` | turtle_scute |
| collar | `armorpieces_coral:nautilus_gorget` | copper |
| vambraces | `armorpieces:wraps` | leather |
| belt | `armorpieces:cord` | leather |
| tassets | `armorpieces:scale_skirt` | turtle_scute |
| knees | `armorpieces:poleyns` | turtle_scute |
| spurs | `armorpieces:streamers` | copper |
| greaves | `armorpieces:swim_fins` | turtle_scute |

It goes in `packs/coral/datapack/armorpieces-sets.json` in the shape the seam already reads, and
`tools/pack_manifest.py` should report it as `12 sockets, 8 borrowed`.

### How they are had

Craftable, all four, on their own template recipes; plus one **loot group** over the ocean-ruin and
shipwreck tables, which is where a reef set should turn up. No entity rows: the drowned are farmable
and the chance belongs to the table.

### As built

**1. `axolotl_frills` (2026-09-07)** — the first part ever authored through the toolkit's own
Blockbench plugin. 15 bridge calls, saved **without `force` on the first attempt**,
`check_authoring.py` clean. Three gill stalks, each a root+tip cube pair, fanned 40° from one temple
bone. Verified mechanically afterwards: 100 opaque pixels on the master and 100 on the static layer,
**zero** static pixels outside the master's silhouette, **zero** non-grey pixels on the master, and
all five static colours straight from the lucy palette with the master values (107/135/167/199/214)
exactly matching them.

The session was asked to report on the six bridge claims and **marked three of them unverified
rather than confirming them**, which is the answer worth having:

| claim | verdict |
|---|---|
| the piece is bound to this session | **held** — every call went to `axolotl_frills`, `bedroll` never touched |
| a bone can be renamed and re-aimed after the fact | **held, and was the backbone of the session** |
| `capture_screenshot` `views` composes one contact sheet | **held** — two pictures instead of six |
| undo leaves no ghost cube | not exercised |
| `texture op:rects {c: null}` clears | not exercised |
| `inspect faces` prints current face rectangles | not called — the same numbers ride on every edit reply |

**All four built (2026-09-07), and the pack is complete.** `check_authoring.py` clean;
`pack_manifest.py` reads The Reef as **12 sockets, 8 borrowed**, no warnings; every piece is
"crafted + found" once `loot_group/ocean.json` puts the `reef` tag over the four ocean chest tables
the mod's own `tidal` group already uses.

| piece | socket | fitting | recipe centre | saved |
|---|---|---|---|---|
| `axolotl_frills` | horns | none | `minecraft:axolotl_bucket` | first try, no `force` |
| `coral_crown` | crest | `guard` | `minecraft:brain_coral_block` | first try, no `force` |
| `kelp_mantle` | pauldrons | `guard` | `minecraft:kelp` | first try, no `force` |
| `nautilus_gorget` | collar | `guard` | `minecraft:nautilus_shell` | first try, no `force` |

The art was verified mechanically on the two pieces that had a mask: `coral_crown`'s static (92) and
guard (30) partition its master (122) exactly, with **zero overlap** — the band is hardware, the
coral is colour, and neither strays outside the silhouette. Every static colour in the pack comes
from its subject's own extracted palette.

**What the batch cost, and what it proves** — the numbers, the archived transcripts and six asks for
mcp-toolkit are in `docs/measurements/blockbench-plugins.md`. The short version: **$2.19 a piece on
the new plugin against $5.14 on the old, and 5.2 minutes against 8.9** — when a session has
Blockbench to itself. The two pieces that ran concurrently cost $5.15 each and took 14.3 minutes,
because a wiring mistake gave every child session the same identity and therefore one shared project
binding; `risky_eval` went from 0.0 calls per piece to 11.5 as the sessions fell back to guarded
hand-written evals. Both bugs are fixed (`ARMORPIECES_SESSION`, and the proxy naming its project on
every call), but the lesson stands: **one authoring session at a time, unless each has its own
identity.**

**The one nuance it found, now in `.mcptoolkit/loop.json`'s `element` note:** moving a bone's
`origin` moves only its **pivot**, never the cubes inside it. Repositioning the whole cluster 2.5
units down meant editing four bone origins *and* six cubes' `from`/`to` by the same delta in one
pass. The "build it straight, look at it, then rotate the bone" workflow the new plugin makes
possible is real and replaces precomputing sines by hand — but it does not move geometry for you.

Also worth carrying: an OVERLAP note against a part in a **different socket on the same bone** is a
hull test against that part's whole bounding box, so a small accessory near `circlet`, `browband` or
`laurel` will always show some. Judge it by the numbers, not by the presence of the line; only
COPLANAR is a problem.

---

## What this proves

Four claims the mod makes about outside content, none tested by content that was actually outside:

1. **A foreign namespace is a first-class citizen** — `armorpieces_animals:fox_ears` renders, is
   worn, takes a fitting and shows a name, with no entry in any file of the mod's.
2. **A pack can join the loot system** by both routes, exact rows and a group, from a pack the mod
   has never heard of.
3. **Entity tables work** — believed, never done.
4. **Overlap behaves** — one pool at the higher chance, across a pack boundary.

And one the seam adds: **a pack can describe its own outfit**, and it appears in the same wardrobe
as the mod's six.

Anything the pack cannot do without a mod change is a **finding for this document, not a patch**.
The exercise is worthless if the first outside pack needs the mod edited for it.

One gap is already known: `check_authoring`'s grid check cannot see across packs, so nothing tells
an outside author which recipe centres the mod has used. The cheap fix is a `--against <pack>` flag;
whether to build it is a decision for after the pack ships.

---

## Authoring

**One part-author session per piece, sequential** — a fresh context per unit, and every Blockbench
editing tool reads the ambient active tab, so concurrent sessions race on it.

Once, before the first session:

- Create both `pack.mcmeta`, the two `LICENSE` copies, `armorpieces-credits.json` and
  `armorpieces-sets.json`, so the pack reads as a pack from the start.
- Add `packs\animals\datapack` and `packs\animals\resourcepack` to the plugin's own pack list
  (Packs… → add). It only finds `src/main/resources`, `run/resourcepacks` and
  `run/saves/*/datapacks` by itself, so without this the pieces cannot be reopened by name.

Per piece:

- A brief at `docs/plans/briefs/<piece>.md` in the established shape, carrying the accumulated
  gotchas: Blockbench frame numbers (left limbs at **negative** x; the boots' front plane is z −2.9;
  reference shells are the limb box inflated), a picture budget of about six, and the reminder that
  masks are shaded like the master, never flat.
- **The animal's own reference, in the brief**: the palette table from `mob_reference.py` as text
  (a dozen lines, always in context, no per-turn image cost) and the path to the `@8x` view under
  `tools/.mcassets/reference/`, to be looked at **once, first**, before any modelling. That look is
  the cheapest picture in the session — a fox at 8x is about 130 tokens, against ~324 for a
  viewport screenshot — and it is the one that decides whether the piece reads as the animal.
- **The layer rule, stated in every brief**: the animal's colours go in `<piece>_static` with the
  hex values from the table; the master carries the form in greyscale at the `value` the table
  gives for each colour; only hardware stays on the master to follow the armor.
- `armorpieces_new` with **`namespace: armorpieces_animals`** and both pack paths given explicitly —
  the default namespace inside this repository is `armorpieces`, which would put the piece in the
  mod.
- Part data before painting: it is what creates the mask sheets. Recipe through
  `armorpieces_set_part`'s `recipe: {centre, ring, craftable}`.

Budget: about $3–5 and 10–15 minutes a piece, so **roughly $30 and two hours** for the eight, plus
the seam work, the in-game pass and the release.

### The active-tab hazard, found on piece three

**`armorpieces_new` returns the new piece, and its check names the new piece, while the toolkit's
ambient `Project` can still be the previous tab.** The Bee Wings session's first two `add_group`
calls therefore landed in **fox_ears**, two pieces back. It noticed (the check block appended to
every mcptoolkit reply names the piece it is describing) and repaired with
`armorpieces_open <piece> {discard: true, reload: true}`, which rebuilds from disk and throws the
stray group away.

**And one of those strays reached disk anyway**, which is the part worth keeping. `fox_ears.json`
was rewritten at 21:32:56 UTC — mid-Bee-session — carrying an empty bone named `base` whose pivot is
the bee's shoulder clasp. The write cannot have come from the bee agent: `savePiece()` is the only
function in the plugin that writes a piece's geometry (`publishStatus` writes only into the status
directory), and the bee session's single `armorpieces_save` wrote `bee_wings`. So **a save issued
from outside that session — the panel's Save button, or another MCP client — landed on whatever tab
was active, and the active tab was somebody else's piece mid-accident.** Repaired by hand; the fox
is back to one bone and four cubes and its round trip passes.

Two rules follow, and both are now in every remaining brief:

- **Confirm the tab before the first edit.** After `armorpieces_new` or `armorpieces_open`, call
  `get_project_info` and check the name. It is one cheap call against silently modelling into
  another piece.
- **Close your tab when you are done.** A session that leaves its piece open leaves a target for the
  next session's accident, and for any stray Save.

The deeper fix — `armorpieces_new` not returning until the ambient `Project` really is the new piece,
and `armorpieces_save` refusing when the active tab is not the piece the caller named — belongs in
the bridge, not in a brief. It is a finding of this pack, filed here rather than patched mid-batch so
that all eight pieces run against identical tooling.

**Close the tab, and not only for tidiness.** The first three briefs did not say to, so `fox_ears`,
`frog_mask` and `bee_wings` sat open for the whole batch — which is exactly what the bee's stray
`add_group` found. The last three briefs say to close, and those three sessions did. An open tab is
a target.

### Launching a session so it survives

**Two attempts at Armadillo Shell were killed**, both about ninety seconds in and both immediately
after `armorpieces_new` — no API error, no stderr, no crash: the log simply stopped and the process
was stopped from outside the session. This workspace has seen background wrappers stopped before;
what is new is that the `claude` child died with the wrapper rather than surviving it.

- **Launch detached**: PowerShell `Start-Process ... -RedirectStandardOutput <log>` gives the session
  no parent to be killed with, and it then runs to completion. `claude.exe` is only a launcher shim,
  so **do not watch its PID** — it exits immediately while the real session continues. Watch the
  log's line count instead.
- **Put the prompt on STDIN, never in `-ArgumentList`** (2026-09-07, Coral's first launch).
  PowerShell joins an `-ArgumentList` array with spaces and adds **no quoting**, so a multi-word
  prompt arrives as many arguments and `claude -p` takes only the first word. The session that day
  was given `"Build"` — and a session with no task does the most dangerous thing available: it looks
  at the Blockbench tab that is already open and starts working on that. It read another piece's
  sheets for two minutes before it was stopped. (It only read; the binding does not help here,
  because an unbound session is exactly what acts on the active tab.) Write the prompt to a file and
  pass `-RedirectStandardInput <file>`, then confirm the child's first user message is the whole
  prompt before walking away.
- **`-p` buffers, so the redirected log is useless as a progress signal** — it stays at 0 bytes until
  the session ends. The child's own transcript
  (`~/.claude/projects/<slug>/<uuid>.jsonl`, newest) updates live: watch its mtime and treat "no
  write for five minutes" as finished-or-stalled. `--output-format stream-json` into a `.jsonl` is
  the other way, and is what the 2026-09-06 runs used.
- **Recovering an interrupted session** is three steps, and the piece must be cleaned up before a
  relaunch or `armorpieces_new` refuses ("already in that pack"): `armorpieces_close {discard: true}`
  on the abandoned tab, delete the three starter files
  (`data/.../armor_decoration/<piece>.json`, `assets/.../decoration/<piece>.json`,
  `textures/entity/decoration/<piece>.png`), and remove the piece's line from the pack's `en_us.json`
  — rewriting it as `JSON.stringify(value, null, 2) + "\n"`, which is what the plugin's `writeJson`
  produces, so the file does not churn. There is no `tools/decoration_masters` entry to delete: that
  path is for the mod's own namespace only.

---

## Checks

Per piece: `check_part.py` clean and saved without `force`; then
`python tools/check_authoring.py packs/animals/datapack packs/animals/resourcepack` clean — the
round trips, the grid check, the group's tag existing, and `reach` (every piece obtainable).

Once, in game: copy the two halves into `run/saves/<world>/datapacks/` and `run/resourcepacks/`, then
**restart the client** — a datapack folder created after the world loaded is invisible, and neither
`/reload` nor `datapack enable` re-detects it.

- All eight worn, front and back, on leather and on iron; every fitting applied and removed.
- **Settle the open question the Frog Mask session raised**: does an opaque fitting-mask pixel
  *replace* the master's value, or is it *modulated* by it? Nothing in the mod has needed to know,
  because no mod piece paints a mask over a static layer. The frog was drawn to be safe either way
  (the master under the eyes left at a mid green rather than blacked out); look at a gemmed eye
  against a dark master and write the answer into `docs/authoring.md`.
- The Menagerie dressed whole, via `/armorpieces stage` or the wardrobe's `/give` strings, to see
  the borrowed four sit with the new eight.
- All eight crafted; `/armorpieces loot explain` on `village_shepherd` naming **both groups and one
  0.08**, and on `minecraft:entities/rabbit` naming the exact row.
- `/armorpieces loot roll` on a village table and on the rabbit, enough times to see the written odds.
- The datapack half removed: the mod still loads and village chests go back to wayfarer alone.

The loot commands are 0.4.0 work and exist only in the dev build. The **pack needs nothing newer than
0.3.0**, which is what the library entry claims — so load it against the released 0.3.0 jar too.

Add the pack's `check_authoring` invocation to `tools/gate.py` tier 1, so a later mod change that
breaks outside packs is caught by the gate rather than by a player.

---

## Release and publishing

```
python tools/export_pack.py packs/animals/datapack     dist/armorpieces-animals-0.1.0-datapack.zip     --reproducible
python tools/export_pack.py packs/animals/resourcepack dist/armorpieces-animals-0.1.0-resourcepack.zip --reproducible
```

Committed on the clone, then a GitHub release on `mattjesmc/ArmorPieces` tagged **`animals-0.1.0`**
with both zips attached — its own tag, not the next mod release, because the pack's cadence is its
own. The assets must be fetchable without a token: `build/library.mjs`'s `download()` sends no
credentials (confirmed — the repository is public and the 0.3.0 assets answer 200 unauthenticated).

Then **one file** in the editor repository, `library/entries/armorpieces-animals.json`, in the shape
`armorpieces.json` already uses: the two release URLs, `mirror: true` (a browser cannot fetch a
GitHub release asset — no CORS), `official: true`, `tags: ["official", "animals"]`.

That one file then does all of this by itself: `make_library.mjs` downloads both zips, unpacks them
with this repository's own `import_pack.py` under Pyodide and reads them with `pack_manifest.py`;
`thumbnails.mjs` opens each piece in the real editor in Chromium and photographs it; and the site's
`mergedIndex()` serves the entry at `/gallery/index.json` and `/library/index.json` — which puts the
eight pieces in **the gallery**, in **the plugin's library** on both platforms as a one-click
install, and (with the seam) the Menagerie in **the wardrobe** beside the mod's six.

Order: `npm run library && npm run thumbnails` locally first and look at the pictures; push the
editor repo; push or re-run the site workflow, which checks out both repositories, rebuilds the
editor, renders the thumbnails itself and deploys. Then verify live — the pack at `/library/`, its
page at `/library/packs/armorpieces-animals`, eight pieces with pictures in `/gallery/`, the
Menagerie at `/wardrobe/armorpieces-animals-menagerie` — and finally install it **through the
website** from the plugin on a profile that has never seen this repository, which is the loop the
pack exists to prove.

---

## The line after

**Read `docs/plans/main-pack-split.md` first (2026-09-07).** The mod's themed pieces were moved out
into packs, which created two packs this list does not name — **The Wild Hunt** (15 pieces) and
**The Hive** (4) — grew Coral from 4 pieces to 10, and made **Legends** the first pack to ship armor
skins. Every "borrowed" number below was counted before that and is now too high.

Each is its own pack, built the same way, and each borrows more than the last.

- ~~**Coral**~~ — designed and being built; see **Pack 2** above. Four new pieces, eight borrowed,
  which is the first hard number the "it compounds" claim has.
- ~~**Boss**~~ — **dissolved (2026-09-07).** Five bosses cannot fill twelve sockets without becoming
  five sets wearing one name, and each of them already belongs to a place with more in it. It is now
  five packs organised by place — Dragonslayer, Nether, Deep Dark, Hero of the Village and Ocean
  (which is this pack, grown) — in **`docs/plans/pack-line.md`**, which also carries the verified
  finding that the Ender Dragon's loot table is never rolled.
- ~~**Nether**~~ — absorbed into the Boss dissolve above: the wither is its boss and the dimension is
  its body, so it is one pack rather than two. See `pack-line.md`. The floating blaze rod still waits
  on the roadmap's animation section and must not hold the pack.

---

## What this is not

- **No mod change**, in the pack or in the seam.
- **No animation**; nothing in the eight moves.
- **No trades.** A villager trade is not a loot table and is out of reach of every mechanism the mod
  has. The pack's description should say so rather than implying a wandering trader might carry one.
- **No skins, no cloths, no fittings** — pieces only. A pack proving one seam at a time is easier to
  read when it fails.
- **No new sockets, anchors or template items.** The twelve that exist.

---

## Open, for review

- **The eight**, and the four borrowed pieces that complete the Menagerie.
- **The name.** `armorpieces_animals:` is permanent once a piece is in somebody's chest.
- **Build order.** The seam first (so the set is visible the day the pack ships) or the eight pieces
  first (so there is something to look at sooner). Recommended: seam first, because it is the part
  that might turn up a surprise, and eight pieces with nowhere to be worn together is a worse
  half-finished state than a wardrobe row with nothing in it yet.
