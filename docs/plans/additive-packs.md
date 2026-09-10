# Additive packs

> **Status (2026-09-08): steps 1 to 4 are BUILT** — working copy only, committed nowhere. Step 1
> (the move table) and step 2 (tolerant decode) are `docs/plans/compatibility.md`'s, committed as
> `3fec698`; step 3 (`packs/legacy`) and step 4 (`tools/check_additive.py`, in the gate's tier 0) are
> this session's. See [As built](#as-built). Steps 5 (versioned artifacts) and 6 (the config switch)
> are not.
>
> **Corrected 2026-09-10.** The restore pack is **not** the compatibility answer and this document
> should never have said it was — `docs/plans/compatibility.md` §1 and §2, built and verified the
> day after this was written, carry the crossing on their own with no pack installed. `packs/legacy`
> is a convenience download. See that plan's
> [§5](compatibility.md#5-the-correction-2026-09-10--no-compatibility-pack-is-owed), which owns the
> correction; the rest of this document — the additive rule, the checker, versioned artifacts, the
> switch — is unaffected and still stands.

2026-09-08. Follows `docs/plans/main-pack-split.md`, which moved 25 pieces and 5 skins out of the
mod and left one thing unresolved: armor saved on 0.3.0 loses a piece the mod no longer defines.

The answer this document reached was a **restore pack** rather than an alias table in Java, and
around it a rule the whole library follows.

**The restore pack half of that was wrong, and the rule was right.** A day later the break was
measured properly — a missing id costs the whole `ItemStack`, not the socket — and the fix went into
the mod instead: a decode that cannot fail, plus `former_ids` declared by the pack that took the
piece. Both are built and were verified in the game. So a 0.3.0 save crosses to 0.4.0 with **nothing
installed**, and `packs/legacy` went from the rescue to a download for a player who wants the old
pieces back under their old ids. `docs/plans/compatibility.md` owns all of that; what remains this
document's, and is untouched by the correction, is **the additive rule** below.

---

## The principle

**Every pack is additive. A pack may only define ids that nothing else defines.**

This is the user's rule and it decides several questions at once:

- The restore pack ships only the 30 things that **left** the mod, not a snapshot of all 91. A
  snapshot would redefine the 66 pieces the mod still ships and silently freeze their data and art
  at 0.3.0, for exactly the players most likely to install it. (**This objection expires** the day
  the mod ships no content of its own — nothing else would define those 66, so the snapshot becomes
  additive by construction and the pack grows to 91. See
  [compatibility.md §5.3](compatibility.md#53-the-direction-the-mod-becomes-the-engine).)
- The library's current `armorpieces` entry (`content/mod/library.json` in `ArmorPiecesSite`, v0.3.0,
  107 items) **breaks the rule today**. It is the whole mod as a standalone pack, so installing it
  over 0.4.0 overrides everything. It becomes an archive download or it goes.
- Anything that wants to *remove* content is a **setting**, never a pack. See
  [The switch](#the-switch).

A pack that only adds cannot break another pack, which is what makes a library of them safe to
browse and mix.

---

## The one table

Thirty rows, `armorpieces:<name>` to `<pack ns>:<name>`, for the 25 pieces and 5 skins. It is the
only new data any of this needs, and it drives three separate things:

| consumer | what it does with it |
|---|---|
| the restore pack | generates the pack's contents, ids reversed |
| the version port | rewrites a pack's cross-pack references for a target mod version |
| the additive checker | knows which collisions are the split's and which are real |

It belongs in the mod repository as data, not in a tool, because the mod may want to read it too
(see the note under [Tolerant decode](#tolerant-decode)). Generate it from
`docs/plans/main-pack-split.md`'s tables once and check it against the packs.

---

## Tolerant decode

> **Superseded by `docs/plans/compatibility.md` (2026-09-08), which owns this section.** The blast
> radius was measured there and is worse than described below: a failed component fails the whole
> `ItemStack`, so the armor piece itself is lost, not just the socket. That plan also generalises the
> fix to all five of the mod's components and replaces the alias table with `former_ids` on the part.

**This comes first, and without it the restore pack is a race rather than a safety net.**

`ArmorDecorations` (`decoration/ArmorDecorations.java:37`) decodes its socket map with a strict
`Codec.unboundedMap(DecorationAnchor.CODEC, DecorationEntry.CODEC)`, and `DecorationEntry` resolves
the piece through `ArmorDecoration.CODEC`, a `RegistryFileCodec`. An id the registry does not hold
fails that entry. At best the socket is lost; depending on how the partial result is handled the
whole component goes. Either way **it happens during component decode, before any mod code runs, and
nothing can recover it afterwards.**

So as things stand the restore pack helps only if it is installed *before* the save is first opened
on 0.4.0. A website cannot guarantee that.

**The shape of the fix.** `ArmorDecorations` is a 125-line record with one field. Give it a second:
the entries it could not resolve, held as raw data, keyed by socket. They render nothing, they are
re-encoded verbatim on save, and the moment the pack that defines them is installed they resolve
again. Install the restore pack a month later and the armor comes back.

Doing it in the socket map rather than in `DecorationEntry` is what keeps it cheap: the
`Holder<ArmorDecoration>` type is unchanged, so rendering, effects, tooltips and the smithing
recipes are untouched. The stream codec is same-version on both ends and can carry the raw entries
or drop them, whichever is simpler.

**A tolerant decode makes the alias table optional rather than owed**, which is the second reason to
do it first. With raw entries preserved, a rename is survivable without the mod knowing the move
table at all.

---

## The restore pack

> **Read this section as a description of a download, not of an upgrade step.** Everything below is
> accurate about what `packs/legacy` *is*; the framing around it — that a player crossing to 0.4.0
> needs it — was corrected on 2026-09-10. It is offered in the website's library and on the mod
> pages, never bundled, and never named in the first-launch advisory as something to do.

`packs/legacy`, namespace **`armorpieces`** — the mod's own, which is the trick that makes it work.
A datapack may define ids in any namespace, so the pack restores `armorpieces:tusks` exactly as
0.3.0 wrote it. No Java change, no alias, no rename.

| contents | count |
|---|---|
| piece data files, ids and lang keys reversed | 25 |
| geometry files | 25 |
| piece textures | ~57 |
| skin data files, and master sheets | 5, and 10 |
| retired tags: beast, tidal, carapace | 3 |
| retired loot groups, verbatim | 3 |
| template recipes | **0** |

**Zero template recipes, deliberately.** Every template in this mod is the same ring of paper around
one centre item, so a recipe is identified by its centre. The Wild Hunt already ships
`template_horns` with the original centre and Legends ships the five skin templates. Shipping them
here too would put two shaped recipes on one grid and silently make one result unobtainable —
the collision `check_authoring`'s grid check exists to catch, which it cannot see across packs.

The three restored loot groups are why the pack is not inert: they keep the pieces obtainable, so
the reach check passes, and a legacy player still finds beast trophies in bastions. Their `skins`
lists resolve, because `varangian` comes back with the pack and `scale` and `lamellar` never left.

**Two mechanisms to confirm before building it:**

1. **Language files must merge across packs** rather than one winning, or a partial
   `assets/armorpieces/lang/en_us.json` would wipe the mod's other lines. Expected to be true;
   verify rather than assume.
2. **`check_authoring.py` and `pack_manifest.py` must not assume a pack's namespace matches its
   folder.** Both derive the namespace from the path, so `packs/legacy/datapack/data/armorpieces/`
   should work, but this is the first pack where the two differ.

---

## Versioned packs in the library

**The driver is not pack formats. It is cross-pack references.** Animals' Menagerie borrows
`armorpieces:pelt`, which on 0.4.0 is `armorpieces_hunt:pelt`. A pack's *outfits* are therefore
version-dependent even when its pieces are not, and the same pack built for 0.3.0 and for 0.4.0
differs in more than a number in `pack.mcmeta`.

So a pack has one **source** in `packs/<name>/` and one **artifact per target version**, built by
running its ids through the move table in the right direction and stamping the format.
`tools/export_pack.py` already exists and is where that belongs.

The library entry grows an artifact list keyed by the version it is for, instead of one pair of
zips:

```json
"packs": [
  {"kind": "datapack", "for": "0.4", "url": "…", "origin": "…", "size": 0},
  {"kind": "datapack", "for": "0.3", "url": "…", "origin": "…", "size": 0}
]
```

The site picks by the mod version the visitor says they run; the editor and the plugin already know
theirs. The restore pack is then simply another product of the same build, offered for 0.4 and
later and never for 0.3, where its ids would collide with the mod's own.

**This is what makes the restore pack permanent rather than a one-off.** It is generated, so it
cannot go stale, and it is offered for every version where it is additive.

---

## The additive checker

`tools/check_additive.py`, or a pass inside `check_authoring.py`. It fails when any pack defines a
registry path that the mod or another pack already defines, with the move table as the list of
collisions that are expected and allowed.

It is cheap, and it would have caught the full-snapshot hazard on its own. Run it in
`tools/gate.py` alongside the rest.

---

## The switch

Removing content is a setting. The server config already has the right shape:
`ArmorPiecesServerConfig` (`config/ArmorPiecesServerConfig.java:84`) holds `enabled`,
`chance_multiplier` and a per-group `groups.<id>.enabled`, and it is re-read at the **start of every
datapack reload**, so `/reload` picks up an edit with no second command.

Add one field:

| key | effect |
|---|---|
| `parts.mod_parts` | `false` turns off everything in the `armorpieces` namespace in one line |
| `parts.disabled` | a list of ids **and tags**, so the mod's three themes are free granularity |

**The rule that keeps it safe:** disabled means not offered, not craftable, not dropped, not in the
creative tab — but **still decoded and still rendered if already worn**. The moment disabling stops
a worn piece drawing, the split's break has been rebuilt as a setting.

Every place that enumerates parts already goes through `listElements()` on a registry lookup, so one
predicate covers it:

- `registry/ModCreativeTabs.java:41` — the tab's `displayItems`
- `loot/DecorationLootTables.java:150` — the loot pass
- `recipe/SmithingDecorationRecipe.java` — the ingredient check
- template recipe availability, which needs a runtime filter; the existing
  `armorpieces:disabled` recipe type is a datapack author's tool, not a config one

It is a server setting and the client needs it for the picker, so it syncs as the rest does. Note
that `WRITE_CODEC` mirrors `CODEC` field for field and `ConfigCodecTest` enforces it — a field added
to one has to be added to the other.

---

## Order

Each step unlocks the next.

1. **The move table**, as data in the mod repository.
2. **Tolerant decode.** First of the code, because it removes the restore pack's timing constraint
   and makes the alias optional.
3. **The restore pack**, generated from the table.
4. **The additive checker**, and relabelling the library's `armorpieces` entry as an archive.
5. **Versioned artifacts** in the library, and `export_pack.py` targeting a version.
6. **The config switch.**

**Corrected 2026-09-10.** Step 2 is the only one 0.4.0 cannot ship without, and it is built. Step 1
was deleted by `compatibility.md` §2.1 in favour of `former_ids` and comes back in §5.1 as a
*generated* index used only to name a pack in a tooltip. Step 3 is a download, on nobody's critical
path. Steps 4 to 6 can follow whenever.

---

## As built

2026-09-08, steps 3 and 4. Everything below is in the working copy and committed nowhere.

**`tools/build_legacy_pack.py` generates `packs/legacy`.** There is no move-table file: the 30 pack
data files carrying a `former_ids` entry that starts `armorpieces:` ARE the table, and the generator
reads them. It rewrites each piece's `asset_id` and language key back to the mod's namespace, drops
`former_ids` (this file *is* the former id, and two claims on one former id is what
`mint_uids.py --check` reports), copies the geometry and sheets, and writes the 30 language lines.
The three loot groups, their three tags and the pack's paperwork are hand-written and never touched
by a rebuild; `--check` fails if the tree is not what a fresh build produces. 133 files, 25 pieces,
5 skins, 0 template recipes.

**The art tracks the packs, not 0.3.0's bytes.** What a save needs back is the *id*; a piece the Wild
Hunt has since redrawn should come back redrawn. (The generated data is in fact identical to 0.3.0's
for every row but two — `claws` and `head_fins` gained a wearer-gated effect after the split, which
the restored copies now carry as well.)

**The two mechanisms the plan said to confirm before trusting it, confirmed:**

1. **Language files merge across packs**, key by key. `ClientLanguage.loadFrom` asks the resource
   manager for the whole *stack* of `lang/en_us.json` under each namespace and puts every file's
   entries into one map (verified in 26.2's bytecode). A partial `assets/armorpieces/lang/en_us.json`
   therefore adds 30 lines and wipes none of the mod's own.
2. **Nothing derives a namespace from a folder name.** `pack_manifest.py` and `check_authoring.py`
   both glob `data/*/…` and take the namespace from the path, so `packs/legacy/` holding
   `data/armorpieces/` reads correctly — 25 pieces, 5 skins, labels resolved, reach found.
   `check_authoring.py` had a *different* assumption that this pack was the first to break: that a
   `#tag` a loot group names is inside the pack. The three restored groups name
   `#armorpieces:common`, the mod's fitting tag, which never left; the check now looks in the pack
   and then in the mod's own resources.

**`tools/check_additive.py`** walks the mod and every pack and fails when two of them define one
registry id, recipe id or asset path. Tags and language files are exempt by design, because the game
merges those rather than letting one win. 787 definitions across 8 sources, none twice. It is
`gate.py`'s tier-0 `additive` check. It does not repeat `mint_uids.py --check`'s former-id pass.

**Seen in the game**, 26.2 dev client, a flat creative world:

- the tooltip on a diamond helmet whose `horns` socket names `armorpieces:tusks` reads
  `Decorated / Circlet / … / 1 not installed`, with the good socket intact; under F3+H it names the
  ids.
- the operator advisory arrives on the join that first reads such an item, and again on the next
  join, with `This world was last played on Armor Pieces 0.2.0; it is now on 0.3.0.` in front of it
  when the world's `armorpieces_state` says so.
- installing `packs/legacy` into that world and reloading brings the pieces back under their old
  ids, with nothing else done.
  > **Corrected 2026-09-10 by a measurement that contradicts it.** A reload alone does **not** do it,
  > and neither does `/datapack enable` plus a reload — a datapack REGISTRY is read when the world
  > loads, not on a resource reload, so the pack shows as enabled and its pieces still do not
  > resolve. The world has to be opened again. Whatever was seen on 2026-09-08, this is what three
  > boots of a real 0.3.0 save show; see
  > [compatibility.md §5.4](compatibility.md#54-proved-on-a-real-030-save-2026-09-10). The two
  > strings that told a player to `/reload` are fixed.

---

## Open

- **Does the restore pack carry the three retired outfits?** It would duplicate the ones the Wild
  Hunt, Coral and the Hive now declare. Leaving them out is the recommendation, and is what was
  built.
- **Licence.** ARR like the mod, since the art is the mod's, rather than CC BY like Animals and
  Coral. Same open question as the three packs the split created. Built as ARR, copied from the
  Wild Hunt's credits file.
- **What "for": "0.4"` matches.** A mod version, a range, or a pack-format number. A range is
  probably right and is the more annoying one to get wrong.
- **Whether `parts.disabled` should also take skins, cloths and fittings.** The same predicate would
  serve all four registries, and "full customizability" reads like it should.
- ~~**Whether the raw unresolved entries should be visible**~~ — **answered, and then answered
  again.** Built 2026-09-08 as a count line with the ids behind F3+H; corrected 2026-09-10 to put
  the ids and the pack name on the face of the tooltip, because "naming nothing else" leaves a
  player who cannot get the pack with nothing to act on. See
  [compatibility.md §5.1](compatibility.md#51-what-the-tooltip-says).

## What this is not

- Not a change to what any pack contains. The split is done and this builds around it.
- Not the pack line. `docs/plans/pack-line.md` still holds five unbuilt place-based packs.
- Not a migration in the vanilla sense. There is no data fixer here; the pieces come back because a
  pack defines them again, which is a thing a player installs rather than a thing the mod does.
