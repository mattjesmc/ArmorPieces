# Plan: identity and compatibility

> **Status (2026-09-08): BUILT in the mod, steps 1, 2, 6 and 7 - working copy only, committed
> nowhere.** Sections 1, 2 and 4 are in the game and were verified there (see
> [As built](#as-built)). Step 3 (the restore pack), step 4 (`check_additive.py`) and step 5 (the
> library's publication guard) are NOT built: the first two are content and tool work that belongs
> with the split, the third is in `ArmorPiecesSite`.
>
> `docs/plans/additive-packs.md` sketched the tolerant decode; this plan owns it, sizes it, and puts
> the identifier the user asked for around it.

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
- **It resolves the moment the pack arrives.** Resolution is attempted on decode, so installing the
  Wild Hunt a month later brings the antlers back with no migration step.

### 1.3 Telling the player, without nagging

- **One tooltip line**, in the existing grey style, under the decorated block: *"1 part not
  installed"*. Under an advanced tooltip (F3+H) it names the ids. This is the answer to the brief's
  "warn the user", and it is the difference between a player thinking the mod is broken and a player
  knowing which pack to install.
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
3. **The restore pack** — `additive-packs.md`, unchanged, now a convenience rather than a rescue.
4. **`check_additive.py`**, extended to claim former ids as well as ids.
5. **The library's publication guard** (§3.3) — the cheapest thing that prevents rather than repairs.
6. **`uid`**: `mint_uids.py` and `uids.lock` for the mod's own content, the library column and
   minting, the data field, the component field, the resolution order.
7. **The upgrade** (§4): the `armorpieces_state` record, the first-launch message,
   `/armorpieces upgrade`. Small, and last, because 6 is what it stamps.

Steps 1 and 2 are what 0.4.0 cannot ship without. 3 to 7 can follow it, in that order — though 6 and
7 shipping *in* 0.4.0 is what makes 0.4.0 the last version this problem happens in, so they are worth
holding the release for if they are close.

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

**Not verified:** the tooltip line (`item.armorpieces.missing_parts`) and the join advisory, both of
which need a client. `/armorpieces prune` and `/armorpieces upgrade` were not exercised in game.
