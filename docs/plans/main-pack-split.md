# The main pack split

**Status: done, in the working copy, committed nowhere.** 2026-09-07. Twenty-five pieces and five
armor skins left the mod for content packs. Everything below is the state of the repository now,
not a proposal.

This is the plan `docs/plans/pack-line.md` deferred under "Relocating mod pieces, which is a 1.0
breaking change and needs its own plan". That section said it could not be done; it can, and the
cost is named in [The break](#the-break) rather than avoided.

---

## Why

The mod shipped 91 pieces under six theme tags, and the tags were not six themes. They were **two
complete sets, one nearly complete, and three fragments**. The mod's own showcase sets measured it
without anyone reading the measurement: a set that has to borrow is a theme that cannot dress a
figure.

| set | theme | own pieces used | borrowed |
|---|---|---|---|
| knight_errant | knightly | 11 | 1 |
| high_court | court | 10 | 2 |
| wild_hunt | beast | 10 | 2 |
| far_road | wayfarer | 8 | 4 |
| deep_tide | tidal | 5 | 7 |
| chitin | carapace | 4 | 8 |

Socket coverage said the same. Knightly filled 11 of 12 sockets, court 10, beast 10, wayfarer 8,
tidal 5, carapace 4. The bottom two could never dress anyone, and they were exactly the themes the
pack line already wanted to own.

The decision, in the user's words: **the base mod shrinks. Not everyone wants so many. Choose and
pick what they like from the content website.** A player installs the looks they want instead of
ninety-one pieces to wear twelve, and the mod stops growing sideways.

---

## What moved

| destination | namespace | folder | from the mod |
|---|---|---|---|
| Armor Pieces: Coral | `armorpieces_coral` | `packs/coral` | the 6 **tidal** pieces |
| Armor Pieces: The Wild Hunt | `armorpieces_hunt` | `packs/wildhunt` | the 15 **beast** pieces |
| Armor Pieces: The Hive | `armorpieces_hive` | `packs/hive` | the 4 **carapace** pieces |
| Armor Pieces: Legends | `armorpieces_legends` | `packs/legends` | 5 cultural **skins** |

A piece is four to six files and they all moved together: the data file (with `asset_id` and the
`translate` key rewritten), the geometry, its master and fitting-mask textures, its template recipe
where it had one, and its language line. A skin is its data file, both master sheets, its template
recipe and its line.

### The three new packs

- **The Wild Hunt** — `antlers`, `ears`, `horns`, `tusks`, `horsetail`, `bone_mask`, `savoyard`,
  `beast_head`, `mantle`, `fang_necklace`, `claws`, `pelt`, `fanged_cop`, `talons`, `shin_spikes`.
  The hunter and the trophy: bone, antler, fur, claw. **Not** the Animals pack, which draws a named
  animal; this one draws what is left of one.
- **The Hive** — `aerials`, `antennae`, `wing_cases`, `carapace`. Insects and arthropods, and the
  smallest pack in the project by a long way.
- **Legends** — `lorica`, `hoplite`, `samurai`, `varangian`, `runic`. Five skins, no pieces. **The
  first pack in the project to ship a skin**, which works with no mod change at all: a skin's
  `asset_id` is namespaced, so its sheets are found under the pack's own assets, and
  `SkinTemplateIconSource` stitches an icon for "every skin with a body sheet in the resources"
  without being told a pack exists.

---

## The mod after

**66 pieces, 9 skins, 2 cloths, 4 fittings, 3 loot groups, 29 template recipes, 12 of 12 sockets.**

| theme | pieces | what it is |
|---|---|---|
| knightly | 30 | European plate, and the `banner` moved in from court to fill its one empty socket |
| court | 23 | jewellery, heraldry, the wings, and every one of the mod's four effects |
| wayfarer | 13 | the traveller's kit |

The nine kept skins say how armor is **made** — `plate`, `gothic`, `milanese`, `brigandine`, `mail`,
`chainmail`, `gambeson`, `scale`, `lamellar`. The five that left said who **wore** it. They
redistribute over the three surviving loot groups: knightly takes the plate-and-mail five, court
takes `lamellar` and `scale`, wayfarer keeps `gambeson` and `brigandine`.

**The socket the split hurt is `horns`,** down to two pieces (`cheek_guards`, `helm_wings`) from
eight. `least_per_socket` is 2. Four sockets sit at four or fewer. Filling `horns` is the first
content work the mod itself needs.

---

## Where every pack stands

Against the pack line's **rule 1** — a pack's showcase outfit uses only that pack's pieces, so a
pack needs 12 sockets of its own before it ships one.

| pack | pieces | skins | sockets | still needed | outfit | borrowed |
|---|---|---|---|---|---|---|
| Coral | 10 | 0 | 7/12 | brow, vambraces, belt, knees, spurs | The Reef; Deep Tide | 5; 7 |
| The Wild Hunt | 15 | 0 | 10/12 | back, belt | The Wild Hunt | 2 |
| Animals | 8 | 0 | 8/12 | crest, vambraces, tassets, greaves | The Menagerie | 4 |
| The Hive | 4 | 0 | 4/12 | eight sockets | Chitin | 8 |
| Legends | 0 | 5 | — | pieces, if it wants an outfit | none | — |

**The Wild Hunt is two pieces from being the first pack to satisfy rule 1** — a back and a belt.
That is the cheapest useful content work in the whole line, ahead of Coral's eight, which the
pack-line plan currently recommends second.

**Coral got much cheaper.** It was 4 pieces borrowing 8; it is 10 pieces borrowing 5, with a second
outfit it did not have. The pack-line plan's "Ocean: 8 new pieces" is now 5.

**The Hive is the one pack this split created that cannot stand up.** Four pieces on four sockets.
It exists because folding it elsewhere was worse: its names are generic, so Animals would have had
to break its own rule that every piece reads as a named animal. It needs eight pieces or a merger.

---

## The sets

`/armorpieces stage set` still dresses all eight. What changed is who **owns** them.

| set | owner | dressed from |
|---|---|---|
| knight_errant, high_court, far_road | the mod | the mod alone, 12/12 |
| wild_hunt | The Wild Hunt | hunt 10, mod 2 |
| deep_tide | Coral | mod 7, coral 5 |
| chitin | The Hive | hunt 5, hive 4, mod 3 |
| menagerie | Animals | animals 8, mod 3, hunt 1 |
| reef | Coral | coral 7, mod 5 |

The five pack sets are declared in their packs' own `armorpieces-sets.json`, which is the file the
site and the wardrobe read; `StageCommand.java` keeps a transcription so they can be staged in game.
**The mod now publishes only the three sets it owns outright**, because publishing a pack's set from
the mod as well would list one outfit twice.

Three sets needed a substitution when their piece or skin left:

- `far_road` wears `epaulettes` on the shoulders; the `mantle` went to the Wild Hunt, and wayfarer
  has no pauldron of its own.
- `high_court` wears the `lamellar` skin; `runic` went to Legends.
- `wild_hunt` wears `brigandine`; `varangian` went to Legends, and a pack set must not depend on
  another pack.

The Reef stopped borrowing the mod's `carapace` for its back and wears its own `spine_ridge`, which
took it from eight borrowed sockets to five.

---

## The break

> **Resolved 2026-09-08, and the resolution is better than what this section expected.** The break
> was measured (it costs the whole `ItemStack`, not the socket) and then closed in the mod:
> `docs/plans/compatibility.md` §1 and §2, built and verified in the game. A 0.3.0 save crosses to
> 0.4.0 **with nothing installed** — the item survives, and any id an installed pack claims through
> `former_ids` rebinds itself and writes back in the new form. What is left of the break is a
> *rendering gap*, reversible at any time by installing the pack. Read the rest of this section as
> the state of the question on 2026-09-07; its conclusion — that the answer is a restore pack — was
> superseded, see [compatibility.md
> §5](compatibility.md#5-the-correction-2026-09-10--no-compatibility-pack-is-owed).

**This is a breaking change and nothing in the repository softens it yet.** A decoration is stored
on the stack as a `Holder<ArmorDecoration>` (`DecorationEntry.java:46`). Remove `armorpieces:tusks`
from the registry and every helmet wearing it fails to decode that component and silently loses the
piece.

**The rename is survivable; the absence of the pack is not.** `ArmorDecoration.CODEC` is
`RegistryFileCodec.create(...)`, which decodes an id, so a legacy alias table mapping
`armorpieces:tusks` to `armorpieces_hunt:tusks` before the lookup would carry old armor across for
any player who installs the pack. It does **not** help a player who does not, and that player is the
whole point of the split. So the alias is worth building and it is not a rescue.

**The answer is a restore pack, not the alias — see `docs/plans/additive-packs.md` (2026-09-08).**
A datapack may define ids in any namespace, so a pack shipping
`data/armorpieces/armorpieces/armor_decoration/tusks.json` restores the original id exactly, with no
Java change at all. That plan carries the design; three things from it matter here:

1. **An unresolvable id is dropped during component decode, before any mod code runs**, so the
   restore pack only helps if it is installed before the save is opened on 0.4.0. Making
   `ArmorDecorations` keep an entry it cannot resolve as raw data removes that constraint and is
   what should ship first.
2. **The alias table becomes optional** once decode is tolerant, rather than owed.
3. **The version this lands under** is still open. 0.4.0 is in progress and already carries three
   unrelated sections; a break this size arguably wants its own number.

---

## Finishing the split

**2026-09-10, the user:** *"the best thing we can do is move the remaining items out of the mod, and
move everything into packs."*

This split moved 30 of 91. The direction is to move the other 61 — the whole of
[The mod after](#the-mod-after) — and leave the mod as the engine: registries, codecs, rendering,
effects, loot machinery, the identity system, and no content.

**Why it is much cheaper than it was on 2026-09-07.** Every reason this document gave for the split
being expensive has since been paid for, by work done for the first 30:

| what made it expensive | what pays for it now |
|---|---|
| a moved id destroys the item | tolerant decode — `compatibility.md` §1, built and seen in game |
| a moved id needs a Java alias table | `former_ids` on the piece — §2.1, built |
| two packs could claim one id | `tools/check_additive.py`, gate tier 0 |
| "where does this part live?" was "the mod" | `tools/decoration_paths.py` already searches mod-then-packs |
| the old ids would be unreachable | `tools/build_legacy_pack.py`, which generates from `former_ids` |

So the machinery is built and has been exercised on a quarter of the content. What is left is moving
files and deciding boundaries.

**What it changes that the first 30 did not.**

- **The legacy pack becomes the whole of 0.3.0**, and legitimately so — the objection to a full
  snapshot was that it would redefine pieces the mod still ships, and the mod would ship none. 30
  ids become 91, from the same generator.
- **Every save names a pack, always.** "Which pack?" stops being a version-crossing question and
  becomes the permanent condition — which is what
  [compatibility.md §5.1](compatibility.md#51-what-the-tooltip-says)'s tooltip is for.
- **The bundle question below has to be answered**, because after this it decides whether a fresh
  install has any content at all. The recommendation is on the record in
  [compatibility.md §5.3](compatibility.md#53-the-direction-the-mod-becomes-the-engine): a built-in
  pack, on by default, switchable off.

**What has to be decided, and is not decided here.**

- **The boundaries.** The three surviving themes — knightly (30), court (23), wayfarer (13) — are
  the obvious cut, but rule 1 says a pack needs 12 sockets of its own before it ships an outfit, and
  nobody has measured the three separately. Wayfarer at 13 pieces is the one to check first.
- **Who owns the four fittings, the two cloths and the nine skins.** A fitting's type is code and it
  is named by pieces in every pack, so `armorpieces:gemstone` moving would break every pack that
  names it. The likely answer is that fittings stay in the mod as engine and only pieces, skins and
  cloths move — but that is an answer, not an assumption.
- **The three loot groups and their tags**, which currently reach every mod piece.
- **The stage sets**, `/armorpieces stage set`, which would dress from packs that may be absent.
- **The gate's content tiers**, which count the mod's pieces (`test_pick_pieces` already expects a
  number this split invalidated).
- **The site's `armorpieces` library entry**, which `additive-packs.md` already says must become an
  archive rather than a pack.

**This wants its own plan.** It is a bigger move than this one was, with the difference that nothing
about it is risky any more — the risk was the break, and the break is closed.

---

## What this session changed, beyond moving files

Three defects surfaced. All three are fixed; all three are the kind that would otherwise be
rediscovered.

- **A stage set dressed without a skin was never parsed, and the set before it ran to the end of the
  file.** The site's `armorpieces.sets` generator matched only `new GallerySet(..., skin("x"), ...)`,
  so `menagerie` and `reef` ended no block and `chitin` — the last set with a skin — swallowed their
  sockets. **`chitin` had been publishing The Reef's pieces.** The generator now matches a skinless
  set, reads a piece that names another namespace, and skips a set the mod does not own.
- **Two numbers on the store page had already gone stale.** The `how-many-sets` table was recomputed
  from the data. The formula — 199 trims, times skins plus bare, times each socket's states, times
  the cloths on the chestplate — reproduces the published **helmet, leggings and boots** figures
  exactly from the pre-split inventory. It does not reproduce the **chestplate** or the
  **shape alone** figures, and the published chestplate is not even divisible by the page's own
  `199 × (skins+1) × (cloths+1)` prefix. Both were wrong before this release. A diamond set now
  reaches **5.3 × 10⁴⁵**, or **1.3 × 10⁶³** counting banners properly.
- **`tools/sync_skin_masters.py` installed every skin into the mod.** `SHIPPED` now carries a
  destination per skin, and the five Legends skins install into the pack. The masters do not move:
  `tools/skin_masters/` stays the one authoring directory, because that is where a skin is drawn.

Also changed: `modpage.yml`'s hand-written prose (the loot paragraph named beast and tidal; the
gallery caption said six themed sets; the skin count said fourteen), and a `CHANGELOG.md` entry
under Unreleased.

**Checks run, all green:** `check_authoring.py` on the mod and on all five packs, `pack_manifest.py`
on all five, `check_lang.py`, `check_pack_line.py`, `./gradlew build` and the test suite,
`modpage build --offline -t all`.

---

## Still owed

- **`docs/assets/gallery/sets.png` shows the old six themed sets** and cannot be regenerated from
  here. It needs a re-shoot; see [[gallery-shots]] for the studio.
- **The three new packs are licensed ARR**, copied from the mod, while Animals and Coral are
  CC BY 4.0. The art is the mod's own, so ARR is the conservative carry-over rather than a decision.
  Packs meant to be copied should probably be CC BY like their neighbours.
- **The Hive's eight pieces, the Wild Hunt's two, Coral's five, Animals' four.** Nineteen pieces
  makes every pack in the project satisfy rule 1.
- **`tools/paint_*_master.py` for the moved pieces still writes into the mod's resources.** Nothing
  runs them and two were already stale; they are historical authoring scripts, not a pipeline.
- **The three new packs are not in the Blockbench plugin's own pack list** (the `armorpieces_packs`
  setting, which lives in Blockbench and not in this repository). Without them a piece in one of
  those packs cannot be reopened by name, and nothing fails loudly. Add `packs/wildhunt`,
  `packs/hive` and `packs/legends` there before the first authoring session on any of them.
- **Nothing here has been seen in game.** No pack in the project has been, which is the same debt
  Animals and Coral already carry.
- **Whether Coral should be renamed Ocean**, which the pack line already assumes. The namespace is
  `armorpieces_coral` and the pack is unpublished, so it is free to rename now and costs an alias
  later.

## Open

- **Is `armorpieces_hive` a pack or a merger?** Four pieces is not a pack. The alternative is to give
  `carapace` to the Wild Hunt, which fills its back gap, and let the other three go somewhere.
- **Does Legends want pieces?** A galea crest, a hoplite plume, sode pauldrons, a spangenhelm nasal.
  It would make the only skins-led pack an ordinary one, which may be a loss rather than a gain.
- **`horns` has two pieces.** The mod's own thinnest socket, and the split caused it.
- **Whether the mod should bundle its packs.** No longer the question that decides how bad the break
  is — `compatibility.md` §1 decided that, and the break is a rendering gap. It is now the question
  that decides whether a fresh install has content at all, once
  [Finishing the split](#finishing-the-split) empties the mod. Recommendation on the record:
  a built-in pack, on by default, switchable off
  ([compatibility.md §5.3](compatibility.md#53-the-direction-the-mod-becomes-the-engine)).

## What this is not

- It is not a change to how anything works. No Java changed except `StageCommand.java`'s set list,
  and no registry, codec, effect or loot mechanism moved.
- It is not the pack line. `docs/plans/pack-line.md` still holds the five place-based packs, and
  none of them is built. This split is what those packs are built *on top of*.
