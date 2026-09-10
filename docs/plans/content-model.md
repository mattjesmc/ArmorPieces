# Plan: the content model — objects, packs, collections, outfits

> **Status (2026-09-07): BUILT, sections 0 to 6.** Step 0 is `6e780ae` in the mod clone with the
> bundle rebuilt from it (`ArmorPiecesBlockbench 19b52bc`); sections 1 to 6 are six commits in
> ArmorPiecesSite - `911c5c3` the object store, `9ec29e1` packs as lists and per-piece review,
> `7a5df10` collections, `ee0d786` the picker and the outfit's verbs, `ff4b7ac` outfits
> first-class, `046f5c1` the gallery over objects. 101 tests pass. **Nothing is pushed**: a push
> to the site is a deploy. Section 7 was to be the cleanup a release later; it was built on
> 2026-09-10 instead, guarded rather than deferred (see the block under section 7), and the
> migration is `/api/admin/objects` rather than a script (see below).
>
> What was decided while building, that this plan did not settle:
>
> - **The object hash** is `sha256(canonicalJson({kind, id, files: [(path, digest)] sorted, lang}))`,
>   where a `.json`/`.mcmeta` file's digest is over its canonical JSON and every other file's is
>   its bytes. The BLOBS keep the file as `sanitize_pack.py` wrote it, so assembled packs stay
>   readable. Written down in `objects.ts`; it cannot change later.
> - **The language lines no object claims are carried** (`Ingested.lang`, `AssembleSpec.lang`).
>   Without them the mod's own pack loses three hundred tooltips and the parity test fails - the
>   "regenerated set" as written here would have thrown them away.
> - **`AssembleSpec.credits`** carries the pack's own credits block, or null: a pack that had no
>   credits file does not grow one.
> - **Pack formats come from `content/mod/gradle.properties`**, already synced, rather than from a
>   new `formats` element in the mod's `site` generator.
> - **The DRAFT assembles WITH the mod's own objects**; the download without. Decision 5 is about
>   what a pack SHIPS, and a working copy is not a distribution.
> - **A piece's credit is a column on the object**, not part of its hash, and only its owner may
>   write it. A name or recipe change makes a NEW object; tags are pack rows and change nothing.
> - **Seeding is not on the request path.** Pyodide is synchronous on the node thread, so seeding
>   the mod's objects is ~13 s in which the server answers nothing; `ensureOfficial()` is awaited
>   by whoever needs the rows. The outfits that ship seed separately and cheaply
>   (`ensureOfficialSets()`), because pages read those on every render.
> - **The migration is a maintainer-only route**, `/api/admin/objects` with `seed`, `migrate` and
>   `check`, not `scripts/migrate-objects.mjs`: the migration IS `ingest()`, which is this build's
>   TypeScript, and a plain-node script cannot reach it.
> - **`LIMITS.save`** (20/min, burst 10) for the draft PUT: the editor's autosave was sharing the
>   upload bucket and ran out mid-session.

`docs/plans/wardrobe-library.md` built the loop (gallery → library → wardrobe → your pack → gallery)
and `docs/plans/local-first.md` let it run without an account. Both were built fast, and the thing
underneath them is a **zip**: a pack is a zip in `data/objects/`, a draft is a zip, a version is a
zip, a "saved piece" is a row naming a pack id and a piece id, and the composer copies files out of
zips into a new zip. That was the quickest way to a working site and it is now the thing in the way.

The user's brief, 2026-09-07:

> The Library page is a user's personal library: packs and pieces, plus **collections** and
> **outfits**. Create, modify, and export to a pack for the latest mod version. No more "new pack"
> form with a zip upload, but third-party packs can be uploaded *into a collection*. A pack
> submitted to the gallery reuses pieces already in the gallery by **linking**; the pack is
> **constructed dynamically on download**. The wardrobe saves an outfit to the library, adds pieces
> to a collection, and chooses pieces from a collection, the gallery or a pack through one filtered
> list. All of it needs **deduplication**.
>
> "The content sharing platform is off to a good start but the core content mechanics are really
> sloppy."

And, on review: **individual pieces are publishable, and a pack is a published collection of
them**; the mod's own piece ids are not reserved — a player may replace one; and the wardrobe's
sets must stop being a pack's property.

What is sloppy, precisely, so that the fix is aimed:

| today | why it is wrong |
|---|---|
| The unit of storage is the pack zip (`data/objects/<sha256>.zip`, `packs.ts:32-55`) | The same piece in ten packs is ten copies. Nothing can say two packs share a piece. |
| A saved piece is `(gallery entry id, piece id)` (`library_pieces`, `schema.ts:207`) | It names *where a piece was seen*, not *which piece*. A re-versioned pack silently changes what the bookmark means; a deleted pack breaks it. |
| A piece id is unique "by convention only, official wins" (`packOfPiece`, `mylibrary.ts:132`) | Two packs shipping `armorpieces:circlet` with different bytes are indistinguishable everywhere except the composer's refusal. |
| `pieces` table is written and never read (`packs.ts:170`; the gallery reads `pack_versions.manifest`) | Two sources of truth, one of them dead. |
| Composing is `pick_pieces.py` under Pyodide, one queue, `MAX_QUEUE = 12` (`tools.ts:91`) | Every download that is not a stored zip boots Python on a one-core box. |
| The static entry (`content/mod/library.json`) and the database are merged at read time (`mergedIndex`, `packs.ts:344`) | Official content is not rows, so it cannot be linked, counted, or referenced the way uploaded content is. |
| A set can only be declared inside a pack, is addressed `<pack>-<set>`, and only *static* entries' sets reach the wardrobe (`officialSets`, `wardrobe.ts:301`; `entryOf` drops `sets`) | "A pack's pieces are meant to be worn together" was an authoring choice for Animals and Coral, written into five places as a rule. The Reef is eight mod pieces and four of Coral's; an uploaded pack's set never reaches the wardrobe at all. |
| The live figure calls `wear()` with no pack list; `bb_rig.py --wear` searches only the mod's resources | Any set that leaves the mod raises "no geometry". Only the thumbnail strip covers published packs. |

---

## The shape

Five nouns, one of them new to the code and one promoted. Everything else is a view.

**Object** — *the unit of deduplication, and the unit of publication.* An immutable,
content-addressed piece, skin, or cloth: the files that are its own (the ones
`pack_manifest.files_of` lists, plus the fitting definitions it declares and the source pack
provides, plus its language line), its manifest facts (kind, id, label, socket, fittings, license,
author), and a `hash` that is a function of exactly those bytes. Two uploads of the same piece are
one object. An edit is a new object. The same object in a hundred packs is stored once. An object
is published once, ever, and is in the gallery from then on.

**Pack** — *the unit the game installs: a published, versioned list.* A row of metadata plus an
ordered list of object references, plus the pack's own furniture (loot groups, `LICENSE`, anything a
zip carried that no object claims). A **version** pins that list. Publishing a pack publishes the
objects in it that are not published yet, in one review. A download **assembles** a zip from the
objects; nothing stores the zip.

**Collection** — *a user's working bag.* A named, unordered list of object references, private,
never publishable as such. Pieces get in from the gallery, from a pack, from the wardrobe, or from a
zip someone uploads. Pieces get out into a pack, onto a figure, into the gallery one at a time, or
as an export. "Saved pieces" today is a collection with no name.

**Outfit** — *a first-class, shareable thing:* a named dressing of the figure that may name pieces
from any published pack, the mod's, or your own. The `sets` table as it is, promoted: an outfit has
an owner (or is the mod's), can be public on its own, and *may* have come from a pack's
`armorpieces-sets.json` — that is provenance, not ownership. A set piece pins an object `hash`
beside its `id`.

**Library** — the person's view over all four: **Packs · Pieces · Collections · Outfits**. Pieces is
the flat union of every object the person holds anywhere (their packs, their collections), one card
each, with chips saying where it is. Nothing is stored under "Pieces"; it is a query.

The **gallery** stays a query too: published objects, published pack versions, public outfits. A
piece card in the gallery says "in 3 packs", because now it can.

### What a reference is

Every reference in the system is an **object hash**, with provenance beside it:

```
{ hash: "sha256…", id: "armorpieces_animals:fox_ears", from: { pack, version } }
```

The `id` is for display and for the game; the `hash` is the identity; `from` is where it was picked
up, so the library can say "a newer fox_ears is in Animals 0.2.0 — update?". A reference pins
content. It never goes stale by accident, only by choice; updating is a verb.

### Linking is not a feature, it falls out

"A pack submitted to the gallery can reuse pieces already in the gallery through linking" needs no
mechanism once packs are lists of hashes: a pack item whose object is already published *is* a
link. The review queue shows it as one ("12 pieces: 8 already in the gallery from Animals, 4 new,
to be reviewed with this pack") and the assembled download carries the bytes either way. What
publishing has to check is **licence**, and that check exists — `pick_pieces.py`'s ARR refusal —
it moves from copy-time to publish-time and cut-time.

### Deduplication, concretely

Two levels, both content-addressed, both on disk under `DATA_DIR`:

```
data/blobs/<aa>/<sha256>          one file's bytes; a texture unchanged across ten edits is one blob
objects.hash                      sha256 over the canonical listing [(path, blob sha256)…] + lang lines
```

A piece's master PNG that survives a JSON tweak is stored once; the two objects share the blob. The
object hash is over the *listing*, so it is cheap to compute and independent of zip packaging,
timestamps, JSON whitespace (JSON is canonicalised before hashing; `pick_pieces.agrees` already
compares JSON semantically for the same reason).

**Quota** becomes: the distinct blobs of the objects you *created* plus your packs' furniture,
counted once. Holding, wearing and bookmarking cost nothing, as before; now *including someone's
CC-BY piece in your pack* costs nothing either, because it is a link.

**Garbage** is an object no pack item, version, collection item or outfit names, that is not
published, older than seven days; a blob no object or furniture names. `npm run gc` walks them; a
cron runs it at night. Nothing is deleted on the request path.

---

## Decisions

1. **The object is the unit. Packs, collections and outfits are lists of object hashes.** Zips are
   never stored as the truth again; they are ingested on the way in and assembled on the way out.
2. **An object's file set is exactly what `pick_pieces.py` would copy for it, minus loot tags and
   loot groups.** The geometry, the master and its layer sheets, the data file, the template recipe,
   the item model and icon for a skin or cloth, the fitting definitions the piece declares and the
   source pack defines (with their recipes and material tags), and the language line. Loot-group
   membership is *pack furniture* — "loot is a pack implementation": the same piece is the same
   piece whether or not some pack puts it in a village chest.
3. **Ingest stays Python; assembly becomes TypeScript.** Ingest is rare (an upload, a linked-pack
   refresh, an editor save) and already runs `import_pack`, `sanitize_pack`, `pack_manifest` under
   Pyodide — keep it, the refusals are the tool's own. Assembly is frequent (every download) and is
   file copying plus four small JSON merges; doing it in Node with `fflate` takes milliseconds and
   no Python. The two are held together by a **parity test**: ingest a release zip, assemble it,
   compare (see Verification). This is the one place a rule is written twice, and the test is what
   makes that acceptable.
4. **Assembled zips are a cache, not storage.** `data/cache/<assembled hash>-<half>.zip`, evictable,
   never counted, rebuilt on a miss. This is what "constructed dynamically on download" means in
   practice: a download is a lookup or a millisecond build, never a copy kept per pack.
5. **The mod's own objects — by hash — are never assembled into another pack.** They are ingested
   (so the gallery, collections and outfits can reference them, and so a pack may list them as
   borrowed) but a pack that references one gets a "requires Armor Pieces ≥ x" line instead of the
   files. The game has them already, and they are ARR. `pick_pieces` refuses them today; this is
   the same rule with a better message.
6. **The `armorpieces` namespace is not reserved.** A player's edited `armorpieces:circlet` is an
   object under the mod's id with its own hash — a *variant*. It ships, and in any game that
   installs it, it replaces the mod's circlet. The card and the pack page say so ("replaces the
   mod's circlet"), and the gallery's piece page lists variants side by side. Decision 5 asks about
   the hash, not the namespace, so a variant is never confused with the original.
7. **Pieces are publishable, and reviewed one at a time. A pack is a published, versioned,
   installable list of published pieces.** The object carries `published_at`; the gallery's pieces
   are the published objects. A piece can be published on its own from the Pieces tab or a
   collection (it is downloadable as a one-piece pack). A pack's publication files **one queue item
   per unpublished own object**, plus one for the pack itself: the piece items are the content
   review (all ages, no logos or brands, nothing copied), the pack item is the metadata review
   (name, description, credits, licence). The items are grouped by the pack publication, so the
   reviewer meets them together and can decide the lot in one action — but every decision is its
   own. A pack can be half-approved: the version goes public when its pack item and every one of
   its piece items are approved, and until then the author is told exactly which pieces to drop or
   fix. A piece is reviewed once, ever — approval *and* rejection stick to the hash, so an object
   re-offered inside another pack arrives with its earlier decision attached and is not reviewed
   twice. A pack of already-published pieces is the metadata review alone. A collection is not
   publishable — making a pack from it is.
8. **Uploading a zip puts its pieces in a collection and its declared outfits in Outfits. It makes
   no pack.** The only ingestion verb on the site is *Import a zip into <collection>*. To publish
   something built in desktop Blockbench: import it into a collection, *Make a pack* from the
   collection, publish. Two steps where there was one form; the second step is where the licence
   check and the review live, and it is the same step everyone else takes.
9. **A pack's contents are edited on the pack page, and the editor edits one piece at a time.** The
   embedded editor keeps its zip in / zip out contract: *open* assembles the pack's working list,
   *save* ingests the result and diffs it against the list. The editor does not change for this.
10. **Ownership is who created the object on this site; authorship is what the credits say.** An
    upload with "this is my own work" ticked creates objects owned by the uploader; unticked,
    objects with no owner. Publishing anything requires every non-official object to be either
    compose-licensed (`LICENSES[*].compose`) or owned by the publisher. Private holding of anything
    is fine — a collection is a shelf, and shelving is looking. Nothing stronger is possible
    without the mod phoning home, which `website.md` §5 forbids; the review queue is where a false
    tick is caught, as today.
11. **An outfit is its own thing, not a pack's.** It has an owner, it can be public by itself, and a
    pack's `armorpieces-sets.json` is one *way to submit* outfits — provenance recorded as
    `from_pack`, nothing more. The mod's six are seeded rows, not virtual ones. An outfit may name
    pieces from any number of packs; the page says where each came from. A public outfit must
    resolve every piece it names to a published object or a mod object, so a visitor never sees a
    hole — and the refusal is not a dead end: it offers to publish the unresolved own pieces (one
    queue item each, decision 7) and holds the outfit `pending_public` until they clear.
12. **The live figure is handed the packs an outfit borrows from.** The site assembles the outfit's
    foreign objects into one wardrobe pack, the editor installs it, then wears the set. `bb_rig.py
    --wear` learns `--pack <dir>`; the plugin's `wear()` learns a pack list. The headless renderer
    does the same. This is the second mod-repo change and the one plugin change.
13. **Assembled downloads come as two halves, canonical, plus one combined zip for convenience.**
    The halves are what the game's two folders, the release, the plugin's install and `PackZip.kind`
    all speak; they carry honest `pack.mcmeta` formats. The combined zip is the composer's current
    output and what a player who wants one file drops in both places; its mcmeta carries the range
    the way `ensure_mcmeta` writes it today. Same assembler, three URLs.
14. **The `sets` table keeps its name; players read "Outfit".** Same rule as decoration/piece
    (`armorpieces-vocabulary`): rename the prose, not the data.
15. **`/library/index.json` and `/gallery/index.json` keep their shape.** `LibraryEntry.packs[].url`
    now points at assembled zips for account packs and at the mirrored release zips for the official
    entry, as today. The plugin needs no change to install from either. `Piece` gains `hash`.
16. **The interactive parts become shared client modules, not more per-page script.** Per-piece
    review means a publish screen that runs once per piece, in four places (the Pieces tab, a
    collection, the pack page, an outfit's publish-and-go); the picker is one component with three
    callers. Server-rendered pages plus a numbered `prompt()` cannot carry that. The site already
    has the pattern — seventeen vanilla modules in `public/`, mounted from `data-` hooks, fed by a
    `<script type="application/json">` block (`jsonScript`) — it just has no shared layer under
    them: six private copies of `call()`, twenty-two native `prompt`/`alert`/`confirm`. So: keep
    Astro and keep the modules frameworkless (the CSP allows no inline script, and a framework
    would add a build step, hydration and a second idiom for the same job), and **add `public/ui.js`
    beneath them** — one `call()`, one dialog, one status line, one card list — then write
    `publish.js` and `picker.js` against it. §4.

---

## 1. The object store

Repo: `ArmorPiecesSite`, one mod-repo change.

**Schema** (drizzle `0006_objects.sql`):

```
blobs            (sha256 PK, size, created_at)
objects          (hash PK, kind, id, namespace, name, label, anchor, fittings jsonb, meta jsonb,
                  files jsonb [{path, blob, size}], lang jsonb, license, author, source,
                  owner_id → users (nullable), official boolean, published_at (nullable), created_at)
                  index (id), index (owner_id), index (published_at)
```

`meta` is the manifest entry minus what has a column (`effects`, `craftable`, `loot`, `sheet`,
`anchors`, `description`). `files[].path` is the pack-relative path as `pack_manifest` lists it.
`official` is set only by the seeding step, never by an upload — a variant of a mod piece is an
ordinary object under the mod's id.

**Ingest** — `src/lib/ingest.ts`, `ingest(zip, {ownerId, own})` →
`{objects: Ref[], furniture: File[], outfits: WardrobeSet[], dropped: {id, reason}[]}`:

1. `checkUpload` as it is (`packs.ts:68`): size, magic, `import_pack`, `sanitize_pack`, `pack.mcmeta`,
   `pack_manifest`.
2. For every manifest entry: its `files`, its `fitting_files`, its lang line → read bytes out of the
   Pyodide FS, blob each, canonicalise JSON, compute the hash, `INSERT … ON CONFLICT DO NOTHING`
   on both tables. Existing hash → the existing row, owner unchanged.
3. Furniture = every file in the zip no object claimed, minus the regenerated set
   (`pack.mcmeta`, `assets/*/lang/*.json`, `armorpieces-credits.json`, `armorpieces-sets.json`)
   and minus tag files (regenerated from membership, §2). Blobbed the same way.
4. `outfits` = the zip's `armorpieces-sets.json` read by the site itself, each set through
   `cleanSet` (which is already the site's validation of that shape); pieces given hashes where the
   id resolves inside this zip, kept by id where it does not — a set may name what the pack does
   not carry, that is borrowing. `pack_manifest.py`'s own-namespace drop rule stops applying to
   the site; it stays in the tool for the CLI and the plugin, reworded as a warning (mod repo).

**Mod repo, first change:** `pack_manifest.py` entries gain `fitting_files` (the function is
`pick_pieces.fitting_files` today; move it and call it). Without it the site would re-derive the
three-path rule in TypeScript, which is the kind of duplication this plan is against. Reaches the
site along the bundle chain (`set-packs.md`, "how the seam actually reaches the website"): commit on
the clone, rebuild the bundle from the clone, sync.

**Official content is ingested at start.** `scripts/sync.mjs` already fetches the mirrored release
zips; a `seedOfficial()` on server start ingests them idempotently (hashes → no-ops on a warm
database), owner null, `official: true`, `published_at` = the release date. `mergedIndex()`'s
static half becomes rows like every other pack; the `library.json` entry keeps its release-asset
URLs.

**Assemble** — `src/lib/assemble.ts`, `assemble(spec) → {datapack, resourcepack, both}` where

```
spec = { name, description, license, author, homepage, formats: {resource, data},
         items: Ref[], furniture: File[], tags: {tagPath: id[]}, outfits: WardrobeSet[] }
```

- refuses two items with one `id` and different hashes (pick_pieces' second refusal);
- skips official objects, adds a `requires` line to the description and the credits; a variant
  under a mod id is written, and the description notes what it replaces;
- writes each object's files; two objects writing one path must agree byte-for-byte (fitting
  definitions shared by two pieces), else refuse (pick_pieces' third refusal);
- `assets/<ns>/lang/en_us.json` = merge of the items' lang lines per namespace;
- `armorpieces-credits.json` = the pack's own block plus one entry per item from the object's
  license/author/source (the union pick_pieces writes);
- `armorpieces-sets.json` from `outfits`;
- tag files from `tags`, members pruned to ids present;
- `pack.mcmeta` with `min_format`/`max_format` from `formats` — **the current mod's numbers**, read
  from `content/mod/site.json` (the mod's `gradle.properties` already states them; the `site`
  generator gains a `formats` element). This is what "export for the latest mod version" is: a
  stamp, not a migration. A piece format that changes between mod versions is not this plan's job
  and the page says which mod version the export targets;
- furniture files verbatim;
- the datapack half is everything under `data/` plus the root files; the resource half everything
  under `assets/` plus the root files; `both` is the union with the range mcmeta. Members sorted,
  timestamps fixed to ZIP's epoch, `0o644` — `export_pack.py --reproducible`'s convention, so the
  same spec is the same bytes.

`assembledHash(spec)` = sha256 of the canonical spec; the cache key.

**Verification for this section** is the parity test below; nothing user-visible changes.

## 2. Packs become lists

**Schema:**

```
pack_items      (pack_id, hash → objects, sort, added_at)            the working list (was: the draft)
pack_furniture  (pack_id, path, blob, size)                          the working furniture
pack_tags       (pack_id, tag_path, id)                              loot-group membership
pack_versions   + items jsonb, furniture jsonb, tags jsonb, outfits jsonb, assembled_hash
                − object_key (kept nullable through the migration release, then dropped)
packs           + license, author (the credits' pack block; `orphaned_credit` folds into author)
                − draft_object_key, draft_size, draft_updated_at
publications    + kind 'object' | 'pack', hash (nullable → objects, set on an object item),
                  group_id (nullable → publications, the pack item a piece item was filed under),
                  decided_at; pack_id / version_id become nullable.  One row per DECISION: a pack's
                  publication is one 'pack' row plus one 'object' row per unpublished own object,
                  all sharing group_id.  Index (hash, decided_at desc) — that index is what
                  "reviewed once, ever" means in practice
pieces          dropped (write-only today)
```

**Migration** (`scripts/migrate-objects.mjs`, run once, re-runnable): every `pack_versions.object_key`
zip and every draft → `ingest` (owner = the pack's owner, `own: true` for hosted packs, `false` for
linked ones) → `items`/`furniture`/`tags`/`outfits` on the version, and the newest draft-or-current
onto `pack_items`. Objects reachable from an approved public version get `published_at` = the
approval date. The old zips stay on disk until the parity check passes for every version
(assemble(version) ≡ stored zip, semantically); the column goes a release later.

**Routes** keep their paths and change their bodies:

| route | before | after |
|---|---|---|
| `GET /library/u/<pack>/<version>.zip` | `readObject` | `assemble` the version, cache; `…/<version>-datapack.zip`, `-resourcepack.zip` beside it |
| `GET /api/me/packs/:id/draft` | the draft zip | `assemble` the working list |
| `PUT /api/me/packs/:id/draft` | `writeDraft` | `ingest` (owner = you, own = true), then set `pack_items` to the result; answer with what was dropped |
| `POST /api/me/packs/:id/pieces` | `pick_pieces` into the draft | append refs (from a collection, the gallery, or another pack); `as` → a new object made by `pick_pieces --as` over the one source object, then appended |
| `PATCH …/pieces` | `editPiece` rewrites JSON in the draft | lang name → a new object (it is part of the object); recipe on/off → a new object; tags → `pack_tags` (no new object) |
| `DELETE …/pieces` | `--drop` | remove the ref |
| `POST …/versions {fromDraft}` | zip the draft | pin `pack_items` + furniture + tags + outfits; compute `assembled_hash`; **the licence check** (decision 10) |
| `POST /api/me/packs` (zip) | `createPack` | **removed** (decision 8); the JSON form `{name, slug, description, fromCollection?, fromOutfit?}` stays |
| `POST /api/me/packs/link-*` + `refresh` | zip → version | zip → `ingest` → version; unchanged from outside |
| `/api/compose` | `pick_pieces` + `export_pack` | `assemble` over resolved refs; `/composed/<hash>.zip` becomes a cache entry |
| `POST /api/me/objects/:hash/publish` | — | new: queue one own object (decision 7) |

**The pack page** (`/library/packs/[id]/`) gains: *Add pieces…* (the picker, §4), *Outfits* (the
outfits this pack declares, each a row of the owner's linked back with `from_pack`), and loses the
draft/upload language. The contents table shows each item's licence, whether it is published
already ("also in Animals"), and whether it replaces a mod piece.

**Publish** is the existing `publications` flow with `kind`, split per piece (decision 7).
`POST …/versions/:id/publish` resolves the version's own objects, drops the ones a previous
decision already covers, and files one `object` row per survivor under one `pack` row's `group_id`;
the answer names what it filed and what it skipped ("four pieces to review, two already published,
one rejected in March — replace it or drop it"). `POST /api/me/objects/:hash/publish` files a
single `object` row with no group. Approving an `object` row sets `published_at` on that object,
renders its thumbnail, and re-checks two things: whether its group's pack item and siblings are now
all approved (→ the version goes public), and whether any `pending_public` outfit naming it now
resolves whole (§5). Rejecting one leaves the rest of the group untouched and the version pending,
and the pack page lists the piece with the reviewer's note. `reviewOf(hash)` — the last decision on
that hash — is what makes a re-offer cheap and what the queue shows beside an object it has seen
before.

**The queue page** groups by `group_id`: the pack's card as the header (its metadata, the download,
the link counts) and its piece items beneath, each with the object's thumbnail, licence, "replaces
the mod's circlet" flag and prior decision, each with its own Approve/Reject — plus *Approve all N*
across the group, which is one request, not N. Ungrouped object items sit in their own list.
Thumbnails are rendered per *object* (`data/thumbs/<hash>.png`, so a piece in ten packs is
photographed once — today it is per pack, `packs.ts:57`). The page is the first caller of
`public/ui.js` and `public/publish.js` (§4): the reviewer's side and the author's side draw the same
per-piece row.

## 3. Collections

**Schema:**

```
collections        (id, user_id, name, description, created_at, updated_at)   index (user_id)
collection_items   (collection_id, hash → objects, id, from_pack, from_version, added_at)  PK (collection_id, hash)
library_pieces     migrated into the collection "Saved", then dropped
library_packs      unchanged (the Packs tab's "saved packs")
```

**Migration:** each user's `library_pieces` rows → one collection "Saved" → each `(pack_id, piece_id)`
resolved through that gallery entry's current version items to a hash; unresolvable rows are logged
and dropped (they were already broken bookmarks).

**API** — `/api/me/collections` (GET list, POST create), `/api/me/collections/:id` (GET, PATCH name
and description, DELETE), `/api/me/collections/:id/items` (POST `{add: Ref[]}` in bulk, DELETE),
`/api/me/collections/:id/import` (multipart zip + `own` boolean → `ingest`, items appended, declared
outfits saved to `sets` with the same idempotency `/api/me/sets` has), `/api/me/collections/:id/export`
(→ an assembled zip through the cache; refuses a same-id conflict and names the two packs). Caps:
`MAX_COLLECTIONS = 50`, `MAX_COLLECTION_ITEMS = 5000` (the old pieces cap).

`POST /api/me/library {kind:'piece'}` keeps working and lands in "Saved" — the plugin and the
adoption path call it. It gains an optional `collectionId`.

**`/library/`** — four tabs, `?view=packs|pieces|collections|outfits`, the packs-or-pieces toggle
generalised. Pieces = union query; each card's chips are the collections and packs holding it, and
an own unpublished object carries *Publish*. Collections = cards with a count and a stacked
thumbnail; `/library/collections/[id]/` = the cards with verbs *Remove · Add to pack… · Wear it ·
Make a pack · Export as pack · Import a zip*. Outfits = the list `/wardrobe/?view=mine` shows, here
as well. **The New pack form goes**; *New pack* is a name-and-slug dialog with "start from
collection ▾".

**Signed out** — `public/local.js` v2:

```
armorpieces.library = { v: 2, packs: [...],
                        collections: [{ id, name, items: [{ hash, id, from, at }] }] }
```

Migration v1→v2 moves `pieces` into a "Saved" collection, resolving hashes from
`/gallery/index.json` (whose pieces now carry `hash`; an id the catalogue no longer lists is kept
with `hash: null` and shown as unresolved). Adoption carries collections whole. `exportShelf` and
`/api/me/export` keep the same shape as each other.

## 4. The client layer: `ui.js`, the publish panel, the picker

Decision 16. Three modules under `public/`, each mounted the way the seventeen already there are —
a `data-` hook on the page, a `<script type="application/json">` block through `jsonScript`, no
inline script (the CSP forbids it), no framework, no build step.

**`public/ui.js`** — what the modules keep re-inventing, written once and taken away from the
others: `call(url, method, body)` (six private copies today: `account`, `gallery`, `library`,
`pack`, `verbs`, `wardrobe`), `dialog({title, body, actions})` and `choose(list)` replacing the
twenty-two native `prompt`/`alert`/`confirm` — `verbs.js` picks a destination pack with a numbered
`prompt()` today — `status(el)` for the "Saving… / Saved / the server answered 413" line every form
writes by hand, and `cards(list, render)` for the piece grid `account`, `build`, `shelf`,
`wardrobe-list` and `wardrobe` each draw their own way. It exposes `window.ArmorPiecesUI`, the
shape `local.js` already uses for `window.ArmorPiecesLocal`. Nothing new is designed here: every
primitive is lifted from the module that has the best version of it, and the others are rewritten
onto it in the same commit, so the count of `call()` copies goes to one and stays there.

**`public/publish.js`** — the publish panel, and the reason the layer exists. It takes a list of
pieces and draws **one row per piece**: thumbnail, id and name, licence, owner, "replaces the mod's
circlet", the earlier decision if the hash has one, and per row the thing that has to be confirmed —
that it is yours or compose-licensed, and that it meets the terms. Rows can be dropped from the
submission without leaving the panel. It posts to the routes in §2 and then *stays*, showing each
piece's queue state, so the author watches a half-approved pack from the same panel that filed it.
Four callers: the Pieces tab (`/library/?view=pieces`, one own unpublished object), a collection,
the pack page's *Publish*, and the outfit's publish-and-go (§5). A fifth, `/admin/queue/`, draws the
same row from the reviewer's side with Approve/Reject on it (§2) — one definition of "a piece under
review", drawn once.

**`public/picker.js`** — one component, three callers, with `src/components/PiecePicker.astro` for
the markup it mounts on: a filter bar on top — **Source** (Collection ▾ · Gallery · Pack ▾), socket (fixed when a wardrobe socket is
being dressed, free elsewhere), kind, licence, search — over one list of the piece cards
`PieceCards.astro` already draws. Fed by `GET /api/pieces?source=collection:<id>|gallery|pack:<id>&socket=&kind=&license=&q=&cursor=`,
one shape for all sources, session-aware (a collection source signed out reads the local shelf
client-side, the way the shelf page does). Callers: the wardrobe socket picker, the pack page's *Add
pieces…*, a collection's *Add pieces…*. `public/wardrobe.js`'s current per-socket picker becomes
this.

**Wardrobe verbs**, on the dressing page and on an outfit's page:

- *Save outfit* — exists (`/api/me/sets`); the set now carries each piece's `hash`.
- *Add its pieces to a collection…* — bulk POST to `/api/me/collections/:id/items`.
- *Make a pack of this outfit* — `POST /api/me/packs {fromOutfit}`: a pack whose items are the
  outfit's objects and whose `outfits` is this one; the mcfunction that gives the whole set comes
  along as furniture, as `/api/compose {set}` writes it today.
- *Download the pack for this outfit* — `/api/compose` over the outfit, unchanged in name.

`SetPiece` gains `hash?: string`; `cleanSet` accepts it; `setHash` covers it (an outfit dressed in
two different objects under one id is two outfits, and should be). The wardrobe writes the hash
whenever the picker supplied one; `/give` strings need only the id and are unchanged.

## 5. Outfits, first-class

Repos: `ArmorPiecesSite`; `ArmorPieces` (`bb_rig.py`, the plugin); `ArmorPiecesBlockbench` (bundle).

**Schema:**

```
sets   + official boolean, from_pack_id (nullable → packs), from_set_id (the slug inside the pack's
         armorpieces-sets.json, nullable), pending_public boolean (publish-and-go: the owner has
         asked for public and the pieces are in review); user_id becomes nullable (the mod's six,
         and a static entry's)
```

**Seeding and provenance.** `seedOfficial()` (§1) also inserts the mod's six from `generated('sets')`
with ids `armorpieces-<name>` — the ids they have today, so `/wardrobe/armorpieces-knight-errant/`
keeps working — and a static entry's declared sets under `<entry>-<set>`, all `official`, no owner.
An upload's or a draft's `armorpieces-sets.json` becomes rows owned by the uploader with
`from_pack`, through the same idempotent save `/api/me/sets` does (same owner + same hash →
update). `officialSets()`, `officialSet()`, `officialSetByHash()` and `OFFICIAL_PREFIX` go; the
three pages that consult them before the table read the table. `entryOf()` no longer has to carry
`sets` — the outfits are rows and the pack page lists the ones that point at it.

**Publishing an outfit.** Visibility widening on save stays as it is. Going `public` additionally
requires every piece to resolve: by `hash` to a published object, or by `id` to a mod object or a
published object. Otherwise the save is refused and answers with the pieces that do not — and then
offers the way through, rather than leaving the owner at a wall.

*Publish-and-go.* The refusal opens the publish panel (§4) on exactly the unresolved pieces, one row
each. The owner's own pieces can go from there: *Publish these N pieces and make this outfit public*
files one queue item per piece (decision 7) and sets `pending_public` on the outfit, which stays
private meanwhile and says so on its page ("public once four pieces clear review — two approved").
Approving an object re-checks every `pending_public` outfit naming it; the last one flips the outfit
to `public` and queues its picture. A rejection clears `pending_public`, leaves the outfit private
and names the piece with the reviewer's note. Pieces that are *not* the owner's cannot be published
by them at all — those rows say who owns the piece and offer only *ask them* or *swap it out*, so
publish-and-go never becomes a way to push a stranger's work through review. An outfit that goes
public by the normal route never touches `pending_public`, and the rendered picture is queued on
save as today.

**The page.** Credited to its owner, or "ships with the mod", or "declared by <pack>" when
`from_pack` is set — never "is where its pieces come from". The piece list is grouped by where each
came from: "eight from Armor Pieces, four from Coral", each linking to its pack.

**The five places that say a pack's pieces are meant to be worn together** — the commit message of
mod `4a98782` stays as history; the docstring of `tools/pack_manifest.py` (lines 22–33), the comments
at `src/lib/library.ts:52` and `src/lib/wardrobe.ts:274`, and `docs/plans/set-packs.md`'s "seam"
section get a paragraph saying what the file is: *one way a pack submits outfits.*

**The live figure.** Today `wear(set)` is called with nothing but the set; `bb_rig.py --wear`
searches the mod's own resources; a foreign piece raises "no geometry". Three changes:

- `bb_rig.py --wear <set.json> --pack <dir>…` searches the given pack folders before the mod's.
- The plugin's `wear(set, {packs: [url]})` installs each zip through the `library` source's path
  (`fetchBytes` → `import_pack.py --force`) into a wardrobe pack folder before building the rig, and
  `viewMode` is unchanged. Same code on the desktop.
- The site's `/wardrobe/<id>/pieces.zip` (an outfit's) and `/wardrobe/new/pieces.zip?set=…` (an
  unsaved one, POST, the compose bucket) assemble the outfit's non-official objects — published
  ones for anyone, plus the asker's own — into one wardrobe pack through the cache, and the
  dressing page hands that URL to the iframe. Assembly is milliseconds and cached by hash; it is
  not the render-on-request cost `local-first.md` forbids, and it is rate-limited the way
  `/api/compose` already is.
- `scripts/wardrobe-shot.mjs` does the same for the stored pictures, so an outfit borrowing from
  Coral renders on save.

`thumbnails.mjs` already opens uploaded packs in the headless editor; its install path is the one to
reuse. These two mod-repo pieces (`bb_rig.py`, the plugin) ride the bundle chain with §1's
`pack_manifest.py` change, so they land in the clone together.

## 6. The gallery over objects

`mergedIndex()` becomes a query over published objects and approved versions, plus the official
rows; `entryOf` builds a `LibraryEntry` from a version's items with `packs[].url` at the assembled
routes. The pieces view lists published objects, one card each, "in N packs" and "replaces the
mod's <name>" where it does; `/gallery/pieces/<ns>/<name>/` lists every published object under that
id with its packs — the mod's and any variants. A single published object's page offers its
one-piece pack. `packOfPiece` stays for the id-only callers, now answering the newest published
object under that id, official first.

`/gallery/index.json`: `Piece.hash` added; entry `packs[]` URLs assembled; otherwise the same. The
30-second cache stays.

## 7. Cleanup, a release later

Drop `pack_versions.object_key` and the `data/objects/` zips, `library_pieces`, the `pieces` table,
the draft columns, `officialSets` and its prefix. `npm run gc` runs nightly from then on.

> **BUILT 2026-09-10, and not a release later after all.** "A release later" was written to protect
> other people's data: keep both shapes until a release has run on production, because if assembly
> had drifted the stored zips would be the only way back. The site has no users yet and one
> published entry - the mod's own, re-derivable from the mirrored release zips in a command - so
> the wait was protecting nothing, and holding two shapes meant every path had a dead branch
> nothing exercised. The safety net that mattered is the parity test, and it is untouched: it
> diffs assembly against the zips four real releases shipped, with or without these columns.
>
> What guards the drop instead is `drizzle/0014_section-seven.sql`, which refuses to run while
> anything still needs the old shape - a version holding a zip and no item list, a pack holding a
> draft and no working list, a bookmark whose owner has no collection items. Each is a row the
> migrate action would have converted, so the guard fires exactly when `/api/admin/objects
> {action:'migrate'}` has not been run on that database. `test/section7.test.mjs` is the four
> cases against the real SQL. **So the deploy order is still migrate first**: run migrate on the
> box, then deploy this; the migration will stop the boot rather than let the drop lose a pack.
>
> `migrate` and `check` retired with the columns they read (`src/pages/api/admin/objects.ts`
> keeps `seed` and `lineage`); `readObject` and `data/objects/` went with them, and the nightly
> sweep deletes that directory the first time it runs. `officialSets` was already gone - section 5
> replaced it with rows. There is no `npm run gc`: `npm run sweep` is that script.

---

## Order

0. **Mod repo, on the clone:** `pack_manifest.py` `fitting_files` + the sets warning; `bb_rig.py
   --pack`; the plugin's `wear(set, {packs})`. One commit, then the bundle rebuilt from the clone.
1. **§1** — objects, ingest, assemble, official seeding, the parity tests. No page changes. Lands
   alone: it is the commit the rest stands on.
2. **§2** — packs as lists: migration script, assembled downloads, the draft round trip, the version
   cut with its licence check, per-piece publication and the grouped queue, the New pack zip route
   removed. Old zips retained. This commit carries the first half of §4 — `public/ui.js` and
   `public/publish.js` — because the author's publish screen and the reviewer's queue are both in
   it and both draw the same per-piece row; the six copies of `call()` collapse to one here, and
   the modules that had them are rewritten in the same commit.
3. **§3** — collections: schema, API, the four tabs, import-a-zip, local shelf v2, adoption.
4. **§4** — the rest of the client layer: the picker (with `wardrobe.js`'s own per-socket picker
   retired onto it) and the wardrobe's verbs.
5. **§5** — outfits: seeded rows, provenance, the public rule, the wardrobe pack and the live figure.
6. **§6** — the gallery over objects; link counts in the queue; per-object thumbnails.
7. **§7** — after a release has run on it.

Each of 1–6 is one commit in `ArmorPiecesSite`; a push is a deploy (`armorpieces-vps`), so pushing
waits for the user. Commits to the mod go to the clone, never the working copy.

## Verification

- **Parity, the test that carries the plan.** For the official release zips and the Animals pack
  (`packs/animals/{datapack,resourcepack}`): `ingest` then `assemble(both)` reproduces the input's
  file set exactly, PNGs byte-for-byte, JSON semantically; and for a chosen subset of ids,
  `assemble` agrees with `pick_pieces.py --from … --to … ; export_pack.py --reproducible` over the
  same subset, on the same terms. `test/objects.test.mjs`. Run it under the same Pyodide bundle
  the server uses.
- **Dedup is real.** Upload the same zip twice: the second answers with the same hashes, `blobs` and
  `objects` row counts are unchanged, quota is unchanged. Upload a zip with one texture changed:
  exactly one new blob and one new object.
- **Hash is stable.** Re-indent every JSON in a pack, re-zip with today's timestamps: the same
  object hashes.
- **Licensing holds, where it moved to.** Add a stranger's ARR object to your collection: allowed.
  Add it to your pack: allowed (it is a shelf until it is cut). Cut a version: refused, naming the
  object and its author. Tick "my own work" on an upload, cut: allowed. A CC-BY object from
  another user's public pack: cut allowed, credits carry the author. Publish one own object from a
  collection: queued, approved, in the gallery, downloadable as a one-piece pack.
- **Review is per piece.** Publish a five-piece pack of which two are already published: three
  `object` rows and one `pack` row, sharing a `group_id`; the answer names the two it skipped.
  Approve two of the three: the version is still pending and the pack page names the third.
  Approve it: the version goes public in the same request. Reject it instead: the other two stay
  approved (`published_at` set, in the gallery on their own), the version stays pending, the author
  sees the note. Offer the rejected object again inside a different pack: it is not queued a second
  time — the queue shows the earlier decision, and `reviewOf(hash)` is what it read. *Approve all*
  over a group of four is one request and four decisions.
- **The publish panel is one thing.** The row the author sees on `/library/?view=pieces`, on a
  collection, on the pack page and in the outfit's publish-and-go is drawn by the same code as the
  row the reviewer decides on in `/admin/queue/`; `public/ui.js` holds the only `call()` and the
  only dialog, and `grep -c "prompt(\|alert(\|confirm(" public/*.js` is zero outside `ui.js`.
- **A variant is a variant.** Upload a zip carrying an edited `armorpieces:circlet`: accepted as a
  new object under the mod's id; the card says it replaces the mod's; the official `circlet` (the
  release's hash) in the same zip is a link and is skipped at assembly.
- **The mod's own objects are never shipped.** A pack listing `armorpieces:comb` assembles without
  `comb`'s files and with the `requires` line; the outfit's `/give` still names it.
- **Outfits leave the pack.** Import Coral into a collection: The Reef appears under Outfits,
  owned by the importer, "declared by Coral", eight pieces credited to the mod and four to Coral.
  Make it public before Coral's four are published: refused, naming the four, and the panel offers
  publish-and-go over the ones the asker owns — the outfit goes `pending_public`, its page says
  "public once four pieces clear review", and approving the last one flips it and queues the
  picture. Reject one instead: private again, named, `pending_public` cleared. An outfit naming a
  stranger's unpublished piece offers no publish button for it, only *ask them* or *swap it out*.
  After: public, and
  `/wardrobe/<id>/` shows the live figure wearing all twelve — the first foreign piece the live
  figure has ever shown. The stored picture renders on save. The mod's six still open at their old
  URLs and are rows now.
- **Migration round trip.** On a copy of production data: every existing version assembles to what
  its stored zip holds; every `library_pieces` row lands in "Saved" or is named in the log; every
  set still opens and renders the same picture (same `setHash` — hashes on pieces are only added
  by the wardrobe from now on, never by migration).
- **Every existing suite stays green** (71 today) with the routes they drive keeping their paths.
  `test/pieces.test.mjs` moves from draft zips to items; `test/adopt.test.mjs` carries a v2 shelf;
  `test/wardrobe.test.mjs`'s "the mod's own six sets" reads rows.
- **The plugin installs from both indexes** on the desktop: the official entry from the mirrored
  zips, an account pack from an assembled URL, through `Settings > Armor Pieces library`.
- **The catalogue URL never breaks:** `/library/index.json` ≡ `/gallery/index.json`, CORS, no
  session, as `test/site.test.mjs:92` already checks.
- Cost: an assembled download of a 30-piece pack from a cold cache under 50 ms on the VPS; no
  Pyodide call on any GET.

## Risks

- **The parity test is the whole safety net.** If assembly drifts from `pick_pieces`, packs stop
  agreeing with what the editor and the command line make. Keep the test running the Python side
  under the bundle, and treat a red parity test as a stop.
- **Hashing JSON canonically is a decision that cannot change later** without re-hashing every
  object. Fix it in §1 — sorted keys, no whitespace, UTF-8 — and write it down in `ingest.ts`.
- **Ownership is self-declared at upload.** A user can tick "my own work" on anything. The review
  queue is where that is caught, as it is today. With variants allowed, the queue also has to see
  "this replaces a mod piece" and judge whether that is a remix or a re-upload.
- **Migration touches every row that matters.** Run it on a copy of the production database first;
  keep the zips until parity is green on production; the `object_key` column goes a release later.
- **The word "library" moved once already** (`wardrobe-library.md`, Risks). "Collection" and
  "Outfit" are new words on the same pages; rename the prose in one pass, and leave `sets` and
  the JSON keys alone.
- **Four repos again.** Step 0 lands in the mod clone and must ride the bundle chain before the site
  can read `fitting_files` or hand the figure a pack; until then ingest refuses, loudly, so the gap
  is seen rather than papered over in TypeScript.
- **A per-piece queue is a noisier queue.** Four pieces where there was one pack. Grouping by
  `group_id`, *Approve all N*, and never re-queueing a hash that has a decision are what keep it
  reviewable; if the queue still reads as noise after §2, the fix is collapsing an approved group
  to one line, not going back to one item per pack. And half-approval is a real state now: a pack
  can sit pending on one piece, so the pack page has to say which one, or the author is left
  guessing.
- **`ui.js` is a refactor riding a feature commit.** Rewriting six modules onto a shared `call()`
  and dialog in the same commit as the publish flow is how the copies actually go away, but it also
  means §2 touches pages that have nothing to do with objects. Keep it to lifting the existing
  behaviour — no redesign of a dialog while moving it — so a regression there is visible as a
  regression and not as a new look.
- **The wardrobe pack is a new thing the editor installs on every outfit page.** Its size is the
  outfit's foreign pieces, tens of kilobytes; boot cost is the same Blockbench-plus-Pyodide it is
  today. Keep the thumbnails-first paint.

---

## Answers (2026-09-07)

The first draft asked seven questions; the user answered:

1. Pieces reach the gallery through packs — *and* "we might change it to individual pieces are
   publishable and packs are published collections of them." **Taken up as decision 7**, because
   it makes the unit of publication the unit of deduplication and lets a piece be reviewed once.
2. Reserve the `armorpieces` namespace? **No — players may replace a mod piece.** Decision 6 rewritten:
   variants.
3. References pin content; updating is a verb. **Yes.**
4. Loot is a pack implementation. **Yes.** Decision 2.
5. Self-declared ownership, checked at cut and by the reviewer. **Yes.** Decision 10.
6. Halves or one zip? Asked back; **recommended and taken: halves canonical, one combined zip
   beside them.** Decision 13.
7. The plan lives here. **Yes.**

Plus the wardrobe-set finding (an investigation the same day, nothing changed then): a set is not a
pack's property. **Section 5 and decisions 11–12.**

**Confirmed the same day, with two changes:**

8. Decision 7 — approved, but **review is per piece**: a pack's publication files one queue item per
   unpublished own piece, not one bundled item. Decision 7 and §2 rewritten; a pack can be
   half-approved.
9. Section 5 — approved as a hard gate, **plus publish-and-go**, and with it: "we need to run the
   publish screen for every piece. Perhaps we should start using more reusable js applications
   instead of static pages to render in-page." **Decision 16 and §4**: no framework — the site is
   already seventeen frameworkless modules under `public/` and the CSP allows no inline script —
   but a shared layer beneath them (`ui.js`), and the publish screen written once as `publish.js`
   for its five callers. `ui.js` and `publish.js` ride §2; the picker stays in §4.

Nothing else is open. Section 1 (the object store, alone) is next, after step 0 in the mod clone.
