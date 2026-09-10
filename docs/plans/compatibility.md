# Plan: identity and compatibility

> **Status (2026-09-08): BUILT in the mod, steps 1, 2, 6 and 7 - committed as `3fec698`.** Sections
> 1, 2 and 4 are in the game and were verified there (see [As built](#as-built)).
>
> **Step 3 (the restore pack) and step 4 (`check_additive.py`) were built later the same day** and
> live in `docs/plans/additive-packs.md`, whose "As built" section holds them: `packs/legacy`
> restores the 25 pieces and 5 skins under their `armorpieces:` ids, generated from the `former_ids`
> the packs carry, and `tools/check_additive.py` is the gate's tier-0 `additive` check. Working copy
> only, committed nowhere. Step 5 (the library's publication guard) is NOT built; it is in
> `ArmorPiecesSite`.
>
> `docs/plans/additive-packs.md` sketched the tolerant decode; this plan owns it, sizes it, and puts
> the identifier the user asked for around it.
>
> **Corrected 2026-09-10 — read [§5](#5-the-correction-2026-09-10--no-compatibility-pack-is-owed)
> before §3 or §4.** No pack has to be installed for a 0.2.0 or 0.3.0 save to cross to 0.4.0. Both
> documents were written while that was still true and neither was rewritten when sections 1 and 2
> made it false. `packs/legacy` is a convenience download, not an upgrade step, and the mod is
> heading for no shipped content at all.

The user's brief, 2026-09-08:

> We need to solve the version / pack change compatibility. Especially in the sense where packs are
> changed. And saves become incompatible. [...] One way to resolve this would give every piece a
> unique identifier from the start. Or to recognize them in another way. Game can decide to remove
> any piece which is not found from the armor. Or just not render it and warn the user untill the
> piece is overwritten. Perhaps the content library can play a role here. Every root piece / skin
> gets a unique identifier assigned automatically.

---

## 0. What actually happens today, measured

A JUnit probe under `fabric-loader-junit`, with `VanillaRegistries.createLookup()` plus a one-entry
`armorpieces:armor_decoration` registry — so the registry exists and only the *piece* is missing,
which is exactly the 0.3.0 → 0.4.0 situation:

| what was decoded | result |
|---|---|
| `ArmorDecorations.CODEC` with one good socket and one missing part | **error, but a usable partial**: the good socket survives, the missing one is dropped |
| `ItemStack.CODEC` on a diamond helmet carrying the same two sockets | **error, and `resultOrPartial()` is empty** |

```
PROBE map partial  = ArmorDecorations[entries={BROW=…visor…}]
PROBE stack success = false
PROBE stack partial =
PROBE stack error   = 'Failed to get element ResourceKey[armorpieces:armor_decoration /
                       armorpieces:tusks] missed input: {"crest":{…}}
                       missed input: {"armorpieces:decorations":{…}}'
```

**Read the second row again. The failure is not scoped to our component — it takes the whole
`ItemStack`.** `DataComponentPatch`'s codec is strict, so one unreadable component fails the
components map, which fails the stack. And every caller that loads a saved stack — a player's
inventory, a chest, an item frame, a villager's trade — turns a failed `ItemStack.CODEC` into a
logged line and *no item*.

So the honest statement of the bug is not "your crest disappears". It is:

> **A player who has worn a decorated helmet loses the helmet — enchantments, name and all — the
> first time the world is opened on a version that no longer defines that part.**

That is true of the pack split already staged in the working copy (25 pieces changed namespace), and
it is true of `armorpieces:horns`, whose data file and textures are deleted in the working tree right
now. It has quietly been true since 0.1.0; nothing has removed a part before.

**Reproducing it**: the probe is nine lines of setup and is worth keeping once section 1 exists —
see [Tests](#tests).

### One worry that is not real

The brief mentions datapacks reordering things. They cannot break a save: **every id this mod
persists is written as a string**, through `RegistryFileCodec`, and nothing anywhere stores a
numeric registry index. The network protocol does use per-session numeric ids, but they are
negotiated at join and never written down. Load order, file order and pack order are all irrelevant
to a saved item.

The three hazards that *are* real:

| | hazard | fix |
|---|---|---|
| **A** | an id that no longer resolves — moved, renamed, uninstalled, deleted | sections 1–3 |
| **B** | an id that resolves to something *else* — two packs, one name | the additive rule, `check_additive.py` |
| **C** | format drift — `pack_format`, and the mod's own field changes | `docs/plans/storage.md` §1; the mod's optional fields |

Hazard A is the one that eats items. This plan is mostly about A.

### Every component is exposed, not just parts

All five persistent components resolve registry holders by id, and every one of them fails the whole
stack the same way:

| component | what it holds | fails when |
|---|---|---|
| `armorpieces:decorations` | per socket: `Holder<TrimMaterial>`, `Holder<ArmorDecoration>`, `Map<Holder<Fitting>, FittingValue>` (dispatched) | any of the three goes missing — **including a datapack trim material that is not ours** |
| `armorpieces:decoration` | `Holder<ArmorDecoration>` on a part template | the part goes |
| `armorpieces:fitting` | `Holder<Fitting>` on a fitting template | the fitting goes |
| `armorpieces:skin` | `Holder<ArmorSkin>` | the skin goes |
| `armorpieces:cloth` | `Holder<Cloth>`, a dye, banner layers | the garment goes, or a datapack banner pattern goes |

A pack that ships a trim material and is later uninstalled therefore deletes armor that has nothing
of ours on it but a part in the material. The fix has to be uniform across the five, not a patch on
the decoration map.

---

## 1. Tolerant decode: nothing this mod stores may ever fail to read

**The rule.** No component of this mod may return a failed `DataResult` on load, for any input.
Whatever cannot be understood is kept as raw data, re-encoded verbatim, and resolved later if the
thing it names ever arrives.

**Why it comes first, and why it is retroactive.** Tolerance lives in the *reading* version, not the
writing one. A 0.3.0 save read by a 0.4.0 that decodes tolerantly is safe — the 0.3.0 client never
has to have known anything. This single change closes the split's break for every player, with no
pack installed and no action taken. Nothing else in this plan has that property.

### 1.1 The shape

One small shared type, because the same problem appears five times:

```java
/** A value of type T, or the raw data of one this installation cannot resolve. */
public record Tolerant<T>(Optional<T> value, Optional<Dynamic<?>> raw) {
    public static <T> Codec<Tolerant<T>> codec(Codec<T> inner);   // either(inner, PASSTHROUGH)
    public static <B extends RegistryFriendlyByteBuf, T> StreamCodec<B, Tolerant<T>> stream(…);
}
```

`Codec.either(inner, Codec.PASSTHROUGH)` is the whole mechanism: the right side always succeeds, so
the codec cannot fail; encoding puts a resolved value back exactly as it was and an unresolved one
back byte for byte.

For the socket map, keep the typed field and add a second, as `additive-packs.md` proposed:

```java
public record ArmorDecorations(
    Map<DecorationAnchor, DecorationEntry> entries,
    Map<String, Dynamic<?>> unresolved       // keyed by the RAW socket string
) { … }
```

**Keyed by the raw string, not by `DecorationAnchor`** — because the key half of the map can fail
too. `DecorationAnchor` is a closed enum; a socket a future version adds and a past version reads is
exactly the case a raw key preserves and an enum key throws away.

Keeping `entries` typed is what makes this cheap: rendering, effects, the tooltip, the smithing
recipes and `with`/`without` all keep the `Holder<ArmorDecoration>` they have and never see an
unresolved entry.

### 1.2 The rules around it

- **Nothing is ever deleted automatically.** The brief offers removal as an option; it should be
  refused. Removal is unrecoverable, it happens silently, and it happens precisely when the player
  is least able to notice — during a version change. Deliberate removal gets a command:
  `/armorpieces prune [dry-run]`, operator only, which lists what it would drop before it drops it.
  If a server owner wants it automatic, that is a server-config line they turn on themselves.
- **An unresolved entry renders nothing and does nothing.** No geometry, no texture, no effect, no
  attribute, no tooltip beyond the warning line.
- **It can always be overwritten.** `with(anchor, entry)` clears the raw entry for that socket, so a
  player who applies a new crest gets a clean item — the brief's "untill the piece is overwritten",
  and the escape hatch that means nobody is stuck.
- **It resolves the next time the item is read, once the pack is there.** Resolution is attempted on
  decode, so installing the Wild Hunt a month later brings the antlers back with no migration step.
  **"There" means loaded, and a datapack registry loads when the world does** — installing a pack
  into a running world and reloading leaves it invisible to this. See
  [§5.4](#54-proved-on-a-real-030-save-2026-09-10); it is what the advice strings now say.

### 1.3 Telling the player, without nagging

- **A tooltip block**, in the existing grey style, under the decorated block: a count line, and
  under it **the id of each thing that is missing, on the face of the tooltip and not behind F3+H**,
  named with its pack where the mod knows which pack that is. This is the answer to the brief's
  "warn the user", and it is the difference between a player thinking the mod is broken and a player
  knowing what to install — or writing the piece themselves. Superseded in detail by
  [§5.1](#51-what-the-tooltip-says); what was built on 2026-09-08 is the count line alone.
- **One log line per distinct missing id per session**, not per item and never per tick.
- **`/armorpieces missing`** lists every unresolved id this server has seen, with a count. An admin
  gets a shopping list.
- The raw entries must therefore **travel on the wire** — the tooltip is drawn client-side from the
  synced component — so the stream codec carries them as a tag rather than dropping them.

---

## 2. Re-binding: three ways, tried in order

When an id does not resolve, three things can rescue it. They are worth building in this order,
because each is strictly cheaper than the next.

| | mechanism | cost | works on a save written before it existed? |
|---|---|---|---|
| 1 | **`former_ids` on the part** | one optional field in a data file | **yes** |
| 2 | **`uid`** — a library-minted lineage id | a field in the data file *and* ~20 bytes per socket in every item | **no** |
| 3 | keep raw, warn | nothing | yes |

### 2.1 `former_ids`, and why it beats an alias table

`ArmorDecoration` (and `ArmorSkin`, `Cloth`, `Fitting`) gains one optional field:

```json
{ "asset_id": "armorpieces_hunt:tusks", "former_ids": ["armorpieces:tusks"], … }
```

The piece declares its own history. A second index beside the registry maps each former id to the
holder that claims it, consulted only when the primary lookup misses.

This is better than the standalone alias table `additive-packs.md` sketched for three reasons: it is
one field rather than a registry; the declaration travels with the piece through the library, so a
pack that is forked or re-published cannot lose its own history; and additivity is checkable —
`check_additive.py` already has to walk every pack's ids, and a former id is just another id that
must be claimed once.

**The split's thirty rows become thirty `former_ids` entries**, shipped by the packs that took the
pieces. A player on 0.4.0 with the Wild Hunt installed sees their antlers again, automatically.
A player with nothing installed is held safe by section 1 and can be made whole by the restore pack
(`additive-packs.md`, unchanged by this plan).

### 2.2 The uid — the brief's idea, sized honestly

**What it is.** A 128-bit random identifier minted once by the content library the first time a
piece is ingested, and carried by every later version of that piece. Written into the data file as
`"uid": "…"`, so it ships in the pack, reaches the registry, and can be stamped into the component
when a part is applied.

**It must not be the content hash.** The object store already gives every piece a stable unique
identifier — `sha256` of its file set — and it is the wrong one for this job. A content hash
identifies a *version*: fix one pixel and it changes. What a save needs is the identity of the
*thing*, which survives its art being redrawn. So the library needs a **lineage** column beside the
hash, and the uid is that column's value.

**What it buys**

- Renames and moves stop needing to be declared. An author who reorganises their pack breaks
  nothing, even if they forget the `former_ids` line.
- The site can tell a player that the helmet in their save is *that* gallery piece — provenance
  through the save, which the wardrobe and the library both want.
- Two packs shipping the same borrowed piece are recognisably the same piece, in the game as well as
  in the object store.

**What it does not buy, and this is the point to be clear about**

> **A uid cannot fix the 0.3.0 → 0.4.0 break.** Saves written by 0.3.0 contain no uids, because the
> field did not exist. Uids are insurance against *future* breaks; they do nothing about the one
> that is already staged.

That is why the order in this plan is tolerance, then `former_ids`, then uid, and not the reverse.
It is also why the uid is worth doing anyway: it is the mechanism that means this plan is written
once.

**Rules**

- **Optional, always.** A hand-written pack with no uid behaves exactly as today. Requiring one
  would break the mod's standing promise that a part is three JSON files and a PNG.
- **The id wins.** If the saved id resolves, use it and ignore the uid — a pack deliberately
  redefining an id (the restore pack does exactly this) must be allowed to. The uid is consulted
  only after the id misses. A resolved id whose uid disagrees is logged and otherwise ignored.
- **Stamped at apply time**, in `SmithingDecorationRecipe`, the skin and cloth recipes, and
  `set_decoration`'s loot function — wherever an entry is first constructed — and only when the part
  carries one.
- **Format**: `uid` is a string, opaque to the mod, so the library can change how it mints them
  without a Java change.

### 2.3 The resolution order, once all three exist

```
id resolves?            → use it                      (a pack may redefine an id on purpose)
former_ids index hit?   → use it, and log the rebind
uid index hit?          → use it, and log the rebind
otherwise               → keep raw, count it, warn once
```

---

## 3. What the library does, since it is the only thing that sees every version

The site holds every version of every pack, which means it can do two things the game cannot:
**assign identity** and **prevent the break in the first place**.

1. **Mint a uid at ingest.** One column, `objects.uid`, carried forward when a draft is derived from
   an existing object rather than re-minted — that derivation is what makes it a lineage rather than
   a second name for the hash.
2. **Seed the split.** The 25 moved pieces and 5 moved skins take the uid of their 0.3.0 objects, so
   the Wild Hunt's `pelt` and the mod's old `pelt` are one lineage in the library even though no save
   will ever say so.
3. **Guard publication.** A new version of a pack that drops or renames an id its previous version
   published is a save-breaking change, and the site knows it — it has both file lists. It should
   refuse quietly-breaking publishes: offer to write the `former_ids` line for a rename, and require
   an explicit acknowledgement for a genuine removal. **This is the highest-leverage item in the
   plan after section 1**, because it stops the class of problem instead of recovering from it.
4. **Ship the history.** `former_ids` and `uid` are fields in the data file, so they ride the object
   store and the assembled zips with no new machinery.
5. **Version-targeted artifacts** stay exactly as `docs/plans/storage.md` §1 designs them. Format
   profiles are about `pack_format` numbers; uids are about identity. The two do not interact, and
   neither should learn about the other.

---

## 4. The upgrade: accepting the break once, and never again

The user's framing, 2026-09-08: *"the problem will keep persisting every version unless we mitigate
it once accepting this break only once. Can work around it once but need it hooked into this new
system. 0.4.0 loads a 0.3.0 save, warns to use legacy pack first launch, -> port to new save
format."*

That is the right shape, with two corrections that make it cheaper to build and smaller to announce.

### 4.1 The port is a consequence of section 1, not an alternative to it

**You cannot port what you cannot read.** The failure measured in section 0 happens inside vanilla's
item-loading path, before any mod code sees the NBT. So a converter has nothing to convert.

Once the codec is tolerant, though, the port comes for free. `DataComponentPatch` re-encodes from the
**decoded value**, not from the bytes it read. So:

```
item read  →  id misses  →  former_ids / uid / the legacy pack re-binds it
           →  the in-memory value now holds the new id and the uid
           →  the next save writes it in the new form
```

No world sweep, no mod data version in level data, no conversion step that can half-finish. The
world upgrades itself as it is played, one item at a time, and an item that is never touched is
never at risk because the raw entry is still there.

### 4.2 Do not build a data fixer or a pre-decode mixin

The literal reading of "port to a new save format" is a pass that rewrites NBT before the codec runs.
It should be refused:

- it must reach every region file, every player file, every structure template and every shulker box
  inside a chest, keyed by a version **vanilla's `DataVersion` does not track**, so the bookkeeping is
  ours to invent and ours to get wrong;
- it rewrites bytes before anything has validated them, so a bug is written to disk;
- and it buys nothing the lazy path does not, because the lazy path's worst case is an item that has
  not been upgraded *yet* and is still perfectly safe.

The lazy path is strictly safer: a wrong re-bind is an in-memory value until the next save, and the
raw entry is preserved until something resolves it.

### 4.3 What the new form is

**Both the id and the uid, never the uid alone.**

```json
{"material": "minecraft:gold", "decoration": "armorpieces_hunt:tusks", "uid": "…", "fittings": {}}
```

The id keeps saved NBT readable, `/give` writable and a hand-authored pack possible; the uid is the
fallback that makes the *next* move a non-event. Storing the uid alone would turn every debugging
session into archaeology.

Most of a player's armor upgrades silently on first load, because the 66 pieces that stayed in the
mod resolve by id exactly as before and are simply stamped on the way through.

### 4.4 The first launch, and what it should say

A `SavedData` record — `armorpieces_state` — holds the mod version that last opened this world.
Absent means pre-0.4.0. That is also where the upgrade counters live, so the state is one object
rather than three mechanisms.

**The message is advisory, and that is the whole point.** With section 1 underneath there is no
deadline: nothing is destroyed by ignoring it, and installing the pack a month later still works. So
it says what happened and what to do, once, to operators:

> This world was last played on Armor Pieces 0.3.0. 25 pieces moved into content packs. Armor
> wearing them keeps them but will not show them until the pack is installed — the Legacy pack
> restores all 25. `/armorpieces missing` lists what this world is waiting for.

**Do not refuse to load the world.** A mod that will not open a world is a mod that gets a world
deleted.

### 4.5 What is actually being accepted

Not "saves break". With this design the cost of the split is a **rendering gap**: affected pieces are
invisible, and reversible at any time by installing a pack. That is the sentence for the changelog
and the store pages, and it is a very different announcement from the one the split implied.

### 4.6 Coverage, honestly

| where | upgraded? |
|---|---|
| worn and carried armor | **yes** — player data is written on logout regardless of what changed |
| a chest in a chunk that loads and is modified | yes, when the chunk is saved |
| a chest in a chunk that loads and is never dirtied | maybe not — an unmodified chunk need not be rewritten |
| a chunk never loaded again | no |

That is acceptable, because a non-upgraded item is not *unsafe* — it is merely not yet protected
against the next move, and its floor is 0.4.0's floor, which is "kept and warned". Offer
`/armorpieces upgrade` for a player who wants their base done: it dirties loaded chunks and **says
plainly that it cannot reach unloaded ones**. Do not offer a region-file sweep.

### 4.7 The mod's own uids, and the ledger

The library mints uids for library content. The mod's 66 pieces, 9 skins, 2 cloths and its fittings
ship in the jar and need theirs minted once by a tool and then **frozen forever** — a uid that
changes is worse than no uid at all, because a stale one in a save re-binds to the wrong piece.

So: `tools/mint_uids.py` writes a uid into any shipped data file lacking one, and a committed
`uids.lock` records every id-to-uid pair ever issued. A gate check asserts three things — every
shipped piece has a uid, no uid appears twice across the mod and its packs, and no uid in the lock
has changed. The lock is append-only; a removed piece keeps its line, because its uid may still be
sitting in somebody's save.

---

## 5. The correction, 2026-09-10 — no compatibility pack is owed

**What the documents implied, and should not have.** Read in order, this plan and
`additive-packs.md` say that a player crossing 0.3.0 → 0.4.0 needs `packs/legacy`. That was true on
2026-09-07, when the only answer to an id nothing defined was a pack that defined it again. It
stopped being true on 2026-09-08, the moment sections 1 and 2 were built and verified in the game,
and neither document was rewritten to say so. `additive-packs.md` still opens by calling the restore
pack "the answer"; this plan's own status block still lists it as step 3 of the crossing;
`main-pack-split.md` still says the absence of the pack is unsurvivable.

**What is actually true.** 0.4.0 opens a 0.2.0 or 0.3.0 save and, with nothing installed:

- **keeps the item** — that is section 1, and it is the whole of the safety;
- **rebinds every id an installed pack claims** through `former_ids`, and writes the new id and the
  uid back on the next save — that is section 2 and §4.1, with no upgrade code, no data fixer, no
  first-launch step and no world sweep;
- **keeps the rest verbatim** and says on the item what it is holding.

So the id system *is* the compatibility story. A pack is what makes a missing piece **visible**
again; it is not what makes the save **survivable**. Those two were being said as though they were
one thing, and saying them as one thing is what produced a compatibility pack the design does not
need.

The cost of a missing pack is a rendering gap — §4.5 already said so, and §4.5 is the sentence the
rest of the documentation should have been written from.

### 5.1 What the tooltip says

The user, 2026-09-10: *"The tooltip of the item can say: 'Missing pack x'. [...] And show the
missing piece id so used can just make their own packs."*

**What was built on 2026-09-08 is a count line** — `1 not installed` — with the ids hidden behind an
advanced tooltip. That is one keypress too many for the two things a player actually does next.

**The id goes on the face of the tooltip.** Two reasons, and the second is the mod's own promise:

1. The id is the only fact that says what to install. A count says something is wrong; an id says
   what.
2. A part is three JSON files and a PNG. A player who cannot get the pack — abandoned, private,
   never published — can **define the id themselves** and their armor comes back. The id is the
   entire input to that, and hiding it behind F3+H hides the escape hatch.

**The pack goes there too, where the mod can know it.** Shape:

```
Decorated
  Circlet
  2 not installed
    armorpieces:tusks — The Wild Hunt
    somepack:crown
```

Three cases, and only the first needs anything new:

| the missing id | shown as | why |
|---|---|---|
| one the mod's own history moved | `armorpieces:tusks — The Wild Hunt` | the moved index, below |
| any other id | `somepack:crown` | the namespace is already the best guess at the pack, and the mod has no business inventing a name for someone else's |
| more than four | the first four, then `+3 more` | uncapped under F3+H, which is what an advanced tooltip is for |

**The moved index, and why a table has to come back.** `former_ids` lives *inside* the pack that
took the piece. A pack that is not installed declares nothing, so with nothing installed
`armorpieces:tusks` is a string in the mod's own namespace and the namespace names nothing. Saying
*The Wild Hunt* therefore needs a table in the jar — the one `additive-packs.md` proposed and §2.1
of this plan removed.

It comes back, for a **strictly smaller job**: a label, never a rebind. Rules that keep it small:

- **Generated, never hand-written.** The same 30 `former_ids` rows `build_legacy_pack.py` reads are
  the source. `tools/build_moved_index.py` writes `assets/armorpieces/compat/moved.json`, mapping
  old id to current id; `--check` fails on drift, in the gate's tier 0, exactly as
  `build_legacy_pack.py --check` does.
- **No display name is in it.** A row is two ids and the name comes from a lang key on the current
  id's namespace — `pack.armorpieces_hunt` → *The Wild Hunt* — so it translates for free.
- **The namespaces it can name are in it**, though, as a second list read out of the mod's own
  `en_us.json`. Whether a lang key exists cannot be asked at runtime: `/armorpieces missing` runs on
  a **dedicated server**, whose `Language` holds vanilla's keys and none of the mod's, so a lookup
  there names nothing or prints a raw key at an operator. The list also covers the case that needs no
  row at all — `armorpieces_hunt:anything` under a pack that is simply not installed already names
  its own pack, and the list is how the mod knows that namespace is one it can name rather than a
  stranger's. **After §5.3 that is the common case and the rows are the rump**, which is the right
  way round.
- **Read from the classpath once, not through the resource manager.** It is not a game resource, it
  must not be overridable by a resource pack, and it is wanted on both sides.
- **It never resolves anything.** If the index and the registry disagree, the registry wins and the
  index is not consulted; it is only ever asked about an id that has already failed every step of
  §2.3. That is what makes a *generated* table safe here where a generated alias would not be: a
  stale row costs a wrong pack **name** on a tooltip, not a wrong **piece** in a save.

**As built, 2026-09-10.** `identity/Moved` (the reader), `tools/build_moved_index.py` and the gate's
tier-0 `moved` check, the eight `pack.<namespace>` lang lines, and the tooltip itself in
`ArmorDecorations.addToTooltip` — count, then up to four ids, then `+n more`, uncapped under F3+H.
`Tolerant.addToTooltip` gained the same treatment, so a missing **skin**, **cloth** or **template**
names its id instead of saying only *Not installed*; `Tolerant.rawId()` finds the id whether the
component is a bare holder or an object. `/armorpieces missing` names the pack beside each id, as a
translatable so the receiving client renders it. The two tests that pinned the old behaviour
(`ArmorDecorationsTest`, `TemplateItemsTest`) were rewritten to pin this one. 514 unit tests pass;
**not yet seen on a client.**

**Ten tests in `MovedIndexTest`, and four of them are about the table being SHIPPED** rather than
about what it says. That distinction is the one worth keeping: a jar the table fell out of degrades
to "show the id", which is correct in the game and invisible to every behavioural test, so the
packaging is asserted on its own — the resource is at the path `Moved` asks for, every moved id
lands in a namespace the table can name, every named namespace has a line in `en_us.json`, and
`Moved.parse` returns an empty table (never an exception) for a file that is absent, corrupt or the
wrong shape. Falsified by deleting the resource: four tests fail, the graceful-degradation ones
still pass.

### 5.2 Where `packs/legacy` goes

It stays — generated, gate-checked, and out of the crossing. What changes is only how it is
described and where it is offered:

- **It ships on the website's library and on the mod pages**, labelled for what it is: the 30 pieces
  and skins the 0.4.0 split moved, under their old ids, for a world saved before 0.4.0. A player
  looks for content where content is; nobody should meet it in a warning.
- **It is never bundled and never required**, and the first-launch advisory does not name it as a
  step. The advisory names ids and packs, and the player decides.
- **A player who installs it and the pack it came from gets both**, because §2.3 says a resolved id
  wins. Two definitions of one piece, one of them uncraftable — the known trade-off of a pack that
  redefines a namespace, and the reason the advisory points at the pack first.

### 5.3 The direction: the mod becomes the engine

The user, 2026-09-10: *"the best thing we can do is move the remaining items out of the mod, and
move everything into packs."*

That finishes what `main-pack-split.md` started — it moved 30 of 91 — and it lands on this plan in
three places.

1. **It makes a full legacy pack legitimate rather than partial.** `additive-packs.md` refused a
   0.3.0 snapshot because it would redefine the 66 pieces the mod still ships and freeze their art
   at 0.3.0 for exactly the players most likely to install it. Once the mod ships none, nothing else
   defines them: the snapshot is simply the archive of what 0.3.0 was, additive by construction.
   `packs/legacy` grows from 30 ids to 91 and the objection disappears with the content.
2. **It makes "which pack" the ordinary question rather than the migration question.** Today a
   missing pack is a version-crossing event. After this it is the normal condition of a save — every
   piece names a pack that may or may not be installed, forever. §5.1 is not a migration affordance;
   it is the permanent UI, and that is the argument for putting the id on the tooltip's face rather
   than behind a key.
3. **It forces the question `main-pack-split.md` left open** — *whether the mod should bundle its
   packs* — and the answer decides how much of this plan a player ever meets.

**Recommendation on the bundle, for the record and still Open.** The jar ships the content as a
**built-in pack, on by default and switchable off**, rather than as registry entries or as nothing
at all. `ResourceManagerHelper.registerBuiltinResourcePack` and its datapack counterpart are the
vanilla-blessed mechanism, and this shape satisfies both halves of the direction:

- everything is a pack, including the mod's own, so there is one content mechanism and no privileged
  tier;
- a fresh install still has content, which a mod that renders nothing on first run does not;
- the bundled pack carries the split's `former_ids`, so **every 0.3.0 save rebinds on a default
  install with nothing downloaded** — the crossing costs the player no action at all;
- and `parts.mod_parts` in `additive-packs.md`'s [switch](additive-packs.md#the-switch) becomes the
  ordinary act of turning a pack off, rather than a special case in Java.

The alternative — an empty jar and a separate core download — is the purer reading of "everything
into packs" and is worse for every player who is not reading the documentation.

**This needs its own plan before it is built.** It touches the loot groups, the three surviving
theme tags, the stage sets, the gate's content checks, the site's library entry for the mod, and
every tool that resolves a decoration path. `main-pack-split.md` gains the direction under
[Finishing the split](main-pack-split.md#finishing-the-split); nothing here waits on it.

### 5.4 Proved on a real 0.3.0 save, 2026-09-10

Not a synthesised item and not a hand-edited marker: **0.3.0 was checked out at its tag, built, run,
and used to write a save**, which was then opened by the working copy. Three boots through the
toolkit bridge. The helmet carried three sockets on purpose — `crest: armorpieces:dorsal_fin` (moved
to Coral), `brow: armorpieces:circlet` (stayed), `horns: armorpieces:tusks` (moved to the Wild Hunt)
— plus a chestplate wearing `armorpieces:varangian` (moved to Legends), and a custom name, because
the claim is about the ITEM and not about the socket.

**The save is genuinely 0.3.0-shaped.** Its player data holds the five ids and **no `uid` tag
anywhere** — 0.3.0 predates the field.

**Opened on 0.4.0 with nothing installed**, `data get entity @p Inventory` reads:

```
"armorpieces:decorations": {brow: {uid: "ap1sl5j4mr6qkmfbot3v6qa", material: "minecraft:gold",
                                   decoration: "armorpieces:circlet"},
                            horns: {material: "minecraft:iron", decoration: "armorpieces:tusks"},
                            crest: {material: "minecraft:copper", decoration: "armorpieces:dorsal_fin"}},
"minecraft:custom_name": '"Grandfather"'
```

The helmet is there, the name is there, the socket that resolves **has been stamped with its uid**,
and the two that cannot are byte-for-byte what 0.3.0 wrote. §4.1's lazy port, happening. The file
0.4.0 wrote back on logout carries the uid; 0.3.0's own file does not.

The tooltip, with nothing installed:

```
"Grandfather"                              Diamond Chestplate
Decorated                                  Not installed: armorpieces:varangian — Legends
 Circlet
  Hero of the Village, while fitted
 2 not installed
  armorpieces:dorsal_fin — Coral
  armorpieces:tusks — The Wild Hunt
```

Two packs named on one item, from the shipped index. `/armorpieces missing` lists all three with
their packs. **Then the three packs were installed into the world's `datapacks/`, the world reopened,
and every socket rebound** — `armorpieces_hunt:tusks`, `armorpieces_coral:dorsal_fin`,
`armorpieces_legends:varangian`, each with its uid, the helmet still named Grandfather, and
`/armorpieces missing` answering *Nothing is missing*. With the packs' language files pushed in, the
tooltip reads `Dorsal Fin / Circlet / Tusks` — identical to what 0.3.0 drew.

#### What the run broke

**1. `/reload` does not bring a pack's pieces back, and the mod said it did.** Copying the packs into
a running world's `datapacks/` and reloading is not enough, and neither is `/datapack enable` plus a
reload: the packs show as enabled, and **the pieces still do not resolve**. A datapack REGISTRY —
`armor_decoration`, `armor_skin`, `cloth`, like vanilla's own worldgen and trim registries — is read
by `RegistryDataLoader` when the world loads and is not touched by a resource reload. What *does*
reload is the reloadable half, which is how the failure announces itself: the count went from 3
missing ids to 13, the ten new ones being the packs' own ids, named by loot groups that had just
loaded against a registry that still had none of them.

> **None of that is new, and that is the actual finding.** This repository had already established
> it, in writing, at least four times: `docs/authoring.md`'s "it needs the world left and re-entered;
> `/reload` is not enough", `set-packs.md`'s "neither `/reload` nor `datapack enable` re-detects it",
> `testing.md`'s "a registry entry cannot be pushed into a running game", and `tools/gate/fixtures.py`,
> which **exists** because of it — the gate writes fixture packs into the world folder before the
> boot for precisely this reason. So the defect is not a gap in what the project knew. It is that the
> two strings the mod says **to a player** contradicted all of it, and nothing connected the two: the
> knowledge lived in author and test documentation, and the sentence that needed it was in a language
> file. Worth remembering when the next instruction is written.

`Compatibility` rebuilding `Rebind` on `END_DATA_PACK_RELOAD` is right and is not the problem — the
index it rebuilds is over a registry that has not changed.

So two strings were wrong, and are fixed: `armorpieces.compat.advice` and
`commands.armorpieces.missing.advice` now say **open the world again**, and say why. This is the one
place the mod gives a player an instruction, and it was an instruction that does not work.

> This also contradicts `additive-packs.md`'s as-built line that installing `packs/legacy` into a
> world and reloading brought the pieces back. That entry is corrected there rather than deleted;
> whatever was seen on 2026-09-08, a reload alone does not do it.

**2. The advisory can never say "was last played on 0.3.0" to a real 0.3.0 world.** `ArmorPiecesState`
did not exist in 0.3.0, so a genuine pre-0.4.0 world has no marker; `upgradedFrom` is empty and the
line is skipped. The three-line advisory seen on 2026-09-08 had its `state.dat` hand-edited, which is
exactly the thing that hid this. The player still gets the count and the advice, so nothing is
broken — but §4.4's "Absent means pre-0.4.0" is not what the code does with an absent marker, and
`ArmorPiecesState.upgradedFrom`'s own javadoc argues for the silence. **Left as it is, deliberately,
and flagged**: the fix is a second sentence for the absent case ("last played on a version before
0.4.0"), which is honest without guessing which one, and it is a behaviour decision rather than a
defect.

---

## Tests

Four, and the first is the probe from section 0 turned into an assertion:

- **A decorated helmet naming a part nothing defines decodes to a helmet.** `ItemStack.CODEC.parse`
  succeeds, the item is a diamond helmet, its custom name survives, and the socket count is what it
  should be. This is the regression test for the whole plan.
- **Round trip.** An unresolved entry re-encodes to bytes identical to what was read, for all five
  components.
- **Re-bind.** With `former_ids` present the entry resolves and no warning is raised; with only a
  `uid` match, likewise; with a resolvable id *and* a stale uid, the id wins.
- **The wire.** The stream codec carries an unresolved entry to a client, so the tooltip line shows.

- **The upgrade.** A 0.3.0-shaped entry decoded against a registry where the piece is reachable
  through `former_ids` re-encodes to the **new** id plus the uid — that is the whole port, asserted
  in one round trip.
- **The lock.** Every shipped piece has a uid, no uid is used twice, and no line in `uids.lock` has
  changed. A tool check rather than a JUnit one.

The first four need only `GameBootstrap` and a hand-built `HolderLookup.Provider`, as the probe did —
no game, so they belong in the gate's tier 1 rather than tier 2.

---

## Order

1. **Tolerant decode, all five components**, with the never-delete rule, the tooltip line and
   `/armorpieces missing`. **0.4.0 must not ship without it**, and shipping it late is worse than
   shipping it never: every world opened in between loses items permanently.
2. **`former_ids`** on the four registry types, and the split's thirty declarations in the packs that
   took the pieces.
3. **The restore pack** — `additive-packs.md`. Not part of the crossing at all: a download offered
   where content is offered ([§5.2](#52-where-packslegacy-goes)), never a step a player is told to
   take.
4. **`check_additive.py`**, extended to claim former ids as well as ids.
5. **The library's publication guard** (§3.3) — the cheapest thing that prevents rather than repairs.
6. **`uid`**: `mint_uids.py` and `uids.lock` for the mod's own content, the library column and
   minting, the data field, the component field, the resolution order.
7. **The upgrade** (§4): the `armorpieces_state` record, the first-launch message,
   `/armorpieces upgrade`. Small, and last, because 6 is what it stamps.
8. **The tooltip and the moved index** ([§5.1](#51-what-the-tooltip-says)): the ids on the face of
   the tooltip, `tools/build_moved_index.py` and its gate check, the pack-name lang keys. Added
   2026-09-10, and it belongs in 0.4.0 with the rest — a player meeting the crossing without it
   meets a number and no way to act on it.

Steps 1 and 2 are what 0.4.0 cannot ship without. 3 to 8 can follow it, in that order — though 6 and
7 shipping *in* 0.4.0 is what makes 0.4.0 the last version this problem happens in, so they are worth
holding the release for if they are close, and 8 is small enough that it should simply be in.

---

## Open

- **Should an unresolved entry block the smithing recipe's no-op guard?** Applying the same part
  twice is refused today by comparing entries. An unresolved socket compares equal to nothing, which
  is the behaviour we want, but the guard should be read once with this in mind.
- **How long should a raw entry be kept?** Forever is the recommendation. A server owner who
  disagrees has `/armorpieces prune`. The alternative — a "kept until" stamp — is a second clock to
  get wrong.
- **Does a uid belong on a *skin* and a *cloth* component too?** Yes by symmetry, and a skin is
  exactly as movable as a part; the cost is per item rather than per socket, so it is smaller.
- **Vanilla's own dynamic registries.** A datapack trim material or banner pattern that goes away
  breaks our components and we cannot fix that at the source. Tolerance covers it; nothing else can.
- **Whether `former_ids` should also be honoured by `/give` and loot tables** — that is, whether an
  old id is a permanent second name or only a rescue on load. Recommendation: rescue on load only,
  so a pack's ids stay unambiguous in every file an author writes.
- **Should `/armorpieces upgrade` exist at all in 0.4.0?** The lazy path covers worn armor, which is
  most of what anyone cares about. The command is for a player with a warehouse, and it can be added
  later without changing anything else.
- **Does a uid ever get re-minted?** No, and `uids.lock` is what enforces it. The one case worth
  thinking about is a piece deleted from the mod and later re-created under the same id by a
  different author — the lock keeps the old line, so the new piece must take a new uid and the old
  saves stay bound to nothing rather than to the wrong thing. That is the right answer and it is
  worth stating in the tool's own docs.

---

## As built

2026-09-08, in the mod's working copy. Java under `com.mattjesmc.armorpieces.identity`:
`Identified`, `Tolerant`, `Rebind`, `ArmorPiecesState`, `Compatibility`; plus
`command/CompatibilityCommand`, `tools/mint_uids.py`, `uids.lock`, and
`src/test/.../identity/IdentityCodecTest` (nine tests). The gate gained a `uids` check in tier 0.

**Five decisions taken while building, that the plan did not settle.**

1. **The uid is stamped in the SOCKET MAP only, never on a bare-holder component.** `ClothValue`'s
   serialised form is what `items/cloth_template.json` selects on (`{"cloth": "armorpieces:tabard"}`),
   so a field written beside the id would silently stop every cloth template rendering; the skin and
   the two template components are bare ids for the same kind of reason. Skins, cloths and templates
   are therefore carried by `former_ids` alone, and a test asserts a resolved skin still writes back
   as its bare id.
2. **The uid is not stored on `DecorationEntry` at all.** It is read off the part at encode time and
   discarded at decode time, so the record, the wire and every call site are unchanged, and *every
   save upgrades itself on the way out* with no upgrade code anywhere.
3. **`Tolerant<T>` wraps the four single-value components** (`decoration`, `fitting`, `skin`,
   `cloth`); the socket map has a hand-written codec instead, because only that one has to tolerate a
   failing map KEY as well as a failing value - `DecorationAnchor` is a closed enum, so a socket a
   later version adds has no name here, and `unresolved` is keyed by the raw string.
4. **Fittings are tolerated but never rebound.** A fitting's type is code, there are six, and none
   has moved, so the reverse index would be empty.
5. **The advisory is triggered by the first real miss, not by the version marker.** Decode is lazy:
   when a world opens, nothing has been read, so a first-launch message would be noise for a world
   with no decorated armor and premature for the chest that loads an hour later. The marker
   (`ArmorPiecesState`) only decides whether the message may add "this world was last played on X".

**Two traps worth keeping.**

- **`Codec` has a static field called `EMPTY`.** Inside `new Codec<>() {...}` it shadows the
  enclosing class's, so `ArmorDecorations.EMPTY` has to be written out in full or the code compiles
  against a `MapCodec<Unit>` with a baffling message.
- **A holder from `VanillaRegistries.createLookup()` decodes and then refuses to encode.** Its
  lookups' `HolderOwner` is not the one a `RegistryOps` built from the same provider carries, so
  `RegistryFileCodec.encode` fails `canSerializeIn`. The test builds all four registries by hand,
  trim materials included.

**Verified in game**, three `runServer` cycles on the dev world:

- an armor stand wearing a diamond helmet named "Grandfather", one socket naming
  `armorpieces:nonesuch` and one naming `armorpieces:visor`: **the helmet survives**, the good socket
  resolves and comes back stamped `uid: ap1bxgg7e6hkx4rxescerma`, the bad one is kept verbatim, the
  warning is logged once and `/armorpieces missing` names it;
- **through a real save, shutdown and restart** - identical on the way back in;
- and with a world datapack defining `test:rescued` with `former_ids: ["armorpieces:nonesuch"]`, the
  crest **comes back as `test:rescued` with its uid**, and `missing` reports nothing. That is the
  restore path, the rebind and the lazy port, end to end.

**What was measured and is now the mod's floor:** `ItemStack.MAP_CODEC` reads its components through
`Codec.optionalFieldOf("components", DataComponentPatch.EMPTY)` - **not** the lenient variant it uses
elsewhere - so a failing patch really does fail the whole stack. Section 0's claim is confirmed at the
bytecode, not just inferred from the error text.

**Seen on a client**, 2026-09-08, a flat creative world on the 26.2 dev client through the toolkit
bridge - the two things the server cycles could not reach:

- **The tooltip line.** A diamond helmet with `brow: armorpieces:circlet` and
  `horns: armorpieces:tusks` reads `Decorated / Circlet / Hero of the Village, while fitted /
  1 not installed`. The good socket keeps its name, its effect and its fitting line; the missing one
  costs one grey line and nothing else. With a second unresolvable socket the count says `2 not
  installed`, and under F3+H the ids are listed under it, one per line.
- **The operator advisory**, on the join that first reads such an item and again on the next join,
  all three lines: `This world was last played on Armor Pieces 0.2.0; it is now on 0.3.0.` (grey),
  `1 piece ids in this world are not installed. Armor wearing them keeps them but cannot show them.`
  (yellow), `Install the pack that provides them and they come back. /armorpieces missing lists what
  is waiting.` (grey). `/armorpieces missing` then lists each id with its read count.
- **And the restore path with the real pack**: `packs/legacy` copied into that world's `datapacks/`,
  the pieces come back under their `armorpieces:` ids with nothing else done, and the `not
  installed` line disappears.

**One wart seen there and not fixed:** `armorpieces.compat.missing` reads "1 piece ids", because the
string has no singular form.

**Still not verified:** `/armorpieces prune` and `/armorpieces upgrade`.
