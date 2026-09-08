# Additive packs

**Status: design only, nothing built.** 2026-09-08. Follows `docs/plans/main-pack-split.md`, which
moved 25 pieces and 5 skins out of the mod and left one thing unresolved: armor saved on 0.3.0
loses a piece the mod no longer defines.

The answer is a **restore pack** rather than an alias table in Java, and around it a rule the whole
library follows.

---

## The principle

**Every pack is additive. A pack may only define ids that nothing else defines.**

This is the user's rule and it decides several questions at once:

- The restore pack ships only the 30 things that **left** the mod, not a snapshot of all 91. A
  snapshot would redefine the 66 pieces the mod still ships and silently freeze their data and art
  at 0.3.0, for exactly the players most likely to install it.
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

Steps 1 to 3 are what 0.4.0 cannot ship without. Steps 4 to 6 can follow it.

---

## Open

- **Does the restore pack carry the three retired outfits?** It would duplicate the ones the Wild
  Hunt, Coral and the Hive now declare. Leaving them out is the recommendation.
- **Licence.** ARR like the mod, since the art is the mod's, rather than CC BY like Animals and
  Coral. Same open question as the three packs the split created.
- **What "for": "0.4"` matches.** A mod version, a range, or a pack-format number. A range is
  probably right and is the more annoying one to get wrong.
- **Whether `parts.disabled` should also take skins, cloths and fittings.** The same predicate would
  serve all four registries, and "full customizability" reads like it should.
- **Whether the raw unresolved entries should be visible** — a tooltip line saying a socket holds
  something this install cannot draw, and naming nothing else, would tell a player why their helmet
  looks plain instead of leaving them to guess.

## What this is not

- Not a change to what any pack contains. The split is done and this builds around it.
- Not the pack line. `docs/plans/pack-line.md` still holds five unbuilt place-based packs.
- Not a migration in the vanilla sense. There is no data fixer here; the pieces come back because a
  pack defines them again, which is a thing a player installs rather than a thing the mod does.
