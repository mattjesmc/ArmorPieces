# Plan: the editor as a client of the content model

> **Status (2026-09-08): STEPS 1-7 BUILT, 8 DEFERRED**, committed in all three repos and pushed
> nowhere. The plugin half - checkout folders, the api calls, Save's automatic check-in with its
> checkbox and action, and the new-piece destination - is this commit. The site half is
> ArmorPiecesSite `11c4f34` on branch `editor-client`, which is branched off `lineage` because the
> check-in needs the uid that branch adds: `oneObjectPack()`, `holdsObject()`, the checkout,
> check-in and `pieces.json` routes, the pack page's Save button, and `test/checkout.test.mjs`
> (11 pass). The new tab is ArmorPiecesBlockbench `7e4a83a`. Step 8 is the release after, as the
> plan itself says. Nothing has been through the bundle chain yet, so nothing in the plugin or the
> tab has run in a browser: that is the next thing.
>
> Three things the build corrected, written into the sections they belong to: a check-in must ADD
> before it REMOVES or the pack's loot membership goes with the old hash; it must carry the
> lineage or every save mints a fresh uid; and a piece must be opened by FOLDER, not by id, or a
> checkout of an id a local pack also defines edits the pack's copy instead. This supersedes
> decision 9 of
> `docs/plans/content-model.md` — "A pack's contents are edited on the pack page, and the editor
> edits one piece at a time. The editor does not change for this." — which was true when the
> object store was being built and is not true now that it is deployed.

The user's brief, 2026-09-08:

> The blockbench editor that is running in our website requires some upgrades. The 'New tab'
> screen needs to be adapted to the new library style. Keep pieces/skins filters. Show only pieces
> owned by user. Filterable by collection, slot, etc just like the gallery or library pages,
> scoped to the users personal library. 'New piece' creates a new piece in a picked collection (or
> create new collection). And further what else we could do to integrate the blockbench plugin
> further with the new content model and storage.

And, on the first draft of this plan, which added routes around the existing seams instead of
asking whether they should exist:

> Why do we keep it separate. Why not just integrate blockbench further. Share sign in, personal
> content library. Upload routes etc. Your system ignores what was built and changed underneath
> the stale blockbench plugin. It needs to interact directly with the users database. Why keep
> separate duplicates.

That is the plan. What follows is the survey that justifies it, then the decisions, then the work.

## 0. What is already true

### The editor has no idea who you are

`ArmorPiecesBlockbench/src/start.js` is the page that replaces Blockbench's start screen on the
site. It has three tabs — *N parts*, *N armor skins*, *library* — and every one of them is drawn
from the **browser's virtual filesystem**: `readParts()` calls `armorpieces_api.pieces()`, which is
`allPieces()` in the plugin (`tools/blockbench_plugin/armorpieces.js:644`) walking the pack folders
under `/packs`. The "library" tab is the *public* catalogue of author-hosted zips. Nothing on the
page asks `/api/me`, and nothing on it can.

This is not a missing mechanism. The editor is served same-origin from `/editor/app/`, and the
plugin's `siteOptions()` already sets `credentials: 'include'` for the web build
(`armorpieces.js:1131`) and an `authorization: Bearer` header for the desktop. `siteJson('/api/me')`
works today. The start page simply never calls it.

### `/api/me/library.json` is a compatibility shim

`libraryIndexFor()` (`ArmorPiecesSite/src/lib/mylibrary.ts`) takes an account — objects, packs,
collections — and reshapes it into the **old** `LibraryEntry` catalogue: a list of downloadable
zips with an author, a description and a version, the same shape as the third-party pack
catalogue. It exists so the plugin's pre-content-model dialog (`libraryDialog`, `installEntry`)
can read the account without changing.

The reshaping loses things, and one loss is a live bug: `ownEntry()` returns `null` for a pack with
no cut version (`src/lib/packs.ts:242`), because a *catalogue* lists published things. So a pack you
made on the site and filled with pieces is **absent** from *Packs… › From your library…*, while
`/editor/?pack=<id>` opens it perfectly. It also cannot carry collections at all, because a
collection is not a downloadable zip and never will be.

### The site already does per-object checkout and per-object write

This is the part the first draft of this plan missed.

- `objects.files` (`src/db/schema.ts:354`) is a pack-relative file list where every entry names a
  blob sha. An object **is** a checkout-able file set — `pack_manifest.files_of()` plus
  `fitting_files()`, which is exactly what `pick_pieces.py` would copy.
- `writeOnePack(tools, dir, object, extra)` (`src/lib/packverbs.ts:249`) writes one object into a
  folder as a real, minimal pack: its files, its language lines, its credit, a `pack.mcmeta`.
  "Everything that makes a NEW object starts here."
- `reingestOne()` (`src/lib/packverbs.ts:271`) is checkout → mutate → re-ingest → new hash, and
  `editPiece` follows it with `removeItems(pack, [old])` / `addItems(pack, [{hash: new}])`. That is
  a commit with a hash swap, written and working.
- `ingest.ts`'s own header names its three callers: "an upload, a linked pack's refresh, **an
  editor save**."

So the loop the editor needs exists server-side and is driven from lambdas instead of from
Blockbench. What the editor speaks instead is whole-pack zips: `openDraft` pulls
`/api/me/packs/:id/draft`, `saveDraft` PUTs it back. Pushing megabytes to repaint one 64×32 sheet
throws away precisely the blob-level dedup the object store was built for.

### And `saveDraft` has no caller

`armorpieces_api.saveDraft` (`armorpieces.js:7016`) is called by nothing in any of the three repos.
The pack page even builds a bridge to the embedded editor (`public/pack.js:158`,
`window.ArmorPiecesEditor`) and then offers no Save. Round-tripping today means knowing to open
*Packs… › Upload to your library › The working copy of X*.

### What is genuinely not duplication

Blockbench edits in memory, and the mod's Python — `bb_rig.py`, `pack_manifest.py`, the check, the
save, `sanitize_pack.py` — reads and writes a **pack folder**. That is the toolchain principle from
the beginning: no part of it gets a second implementation, which is why the browser runs the real
Python under Pyodide against a real filesystem rather than reimplementing it in JavaScript.

So files must exist locally while you edit. But a working tree is not a library — git has both and
nobody calls the checkout a duplicate. **The duplicate is the pack library persisted in IndexedDB**:
a parallel, permanent, account-invisible collection of packs that drifts from your real content, and
that the new tab currently presents as the primary thing you own.

## Decisions

1. **The editor is a client of the content model.** It browses your objects, collections and packs,
   by hash, through the same queries the site's own pages run. It does not get a re-shaped copy of
   them. Supersedes content-model decision 9.
2. **The local filesystem is a working tree, not a library.** It stays — the Python needs a folder
   — and it keeps signed-out and offline use working, which the account page promises in prose. It
   stops being the axis the new tab is organised around. Existing local packs still open; they are
   listed as *in this browser*, one source among several, not as your content.
3. **The unit of exchange is one object, by hash.** Checkout writes a one-object pack into the
   working tree; check-in sends one back. A pack zip moves only when a whole pack is meant to move.
4. **`ingest` stays the trust boundary.** No client-computed hash is trusted, and none is even
   offered: an object's hash is over the bytes `sanitize_pack.py` produces, so a hash computed in
   the browser would not match one computed here. The editor sends bytes; the server sanitises,
   reads and hashes them, exactly as it does for an upload.
5. **Loot membership stays the pack's, not the object's.** `files_of` is what a piece *is*;
   `tag_memberships` is which loot groups a *pack* files it under (content-model decision 2). So the
   loot control on a checked-out piece edits the pack it came from, through `setTags`, and is
   disabled for a piece checked out of a collection — a collection has no loot. Say this in the
   panel, or the first save silently drops a loot group.
6. **Sign-in is the site's session, not a second identity.** Web: the same-origin cookie, already
   sent. Desktop: the device token, already minted. Nothing new.
7. **A new piece lands in a collection**, because import-into-a-collection is the only ingestion
   verb on the site (content-model decision 8) and `own: true` is what makes the objects yours
   (decision 10). A new piece in a *pack* is the same call plus one `addItems` on the pack.
8. **`/api/me/library.json` stops being what the editor reads.** It is kept while the desktop
   plugin's old *From your library…* dialog still exists, and dropped when that follows. It is not
   extended, and the version-less-pack bug in it is not worth fixing on the way out.
9. **Save checks in by itself, and you can turn it off and do it by hand.** Decided 2026-09-08,
   closing the question this plan was left open on. Three parts, all of them small:
   - **Automatic.** A Save of a checkout folder, signed in, checks in after it writes the working
     tree — debounced, never blocking the local write, and reported on the status line.
   - **A checkbox.** `new Setting(ID + '_checkin', { type: 'checkbox', … })` beside the other
     `edit`-category settings (`armorpieces.js:6524–`), default on. Off is what offline and
     throwaway work want, and it is the honest answer to the cost risk below.
   - **A button.** A second `Action` beside `ID + '_save'` — *Check In to My Library* — always
     enabled on a checkout whether or not the checkbox is on, so the manual path is not a setting
     you have to find. With the checkbox off it is the only path, and that is the point.

## 1. The seam: two routes

Both are thin, and both reuse what section 0 found.

**`GET /api/me/objects/:hash/checkout`** → a zip of the one-object pack.

`writeOnePack` is pure composition over `filesOf(object)`, `object.lang` and the credit — the only
thing tying it to Pyodide is that it writes through `Tools`. Refactor the composition out as
`oneObjectPack(object): { path, bytes }[]` in `src/lib/objects.ts`, have `writeOnePack` call it, and
zip it with `fflate` the way `assemble.ts` already does. **No Python on this path**, so a checkout
is file copying and stays off the slow path.

Permission: an object the asker *holds* — in a pack of theirs or a collection of theirs, which is
one query over `packItems`/`collectionItems`, the same join `heldPieces` does — or one that is
published or official. Not any hash on the site, or this is a bulk downloader for private work.

**`POST /api/me/objects/checkin`** → the piece back, as the same one-object pack.

Body: the zip. Headers or query naming where it came from: `from` (the hash being replaced, or
absent for something new), and one of `collection=<id>` / `pack=<id>`. Then:

```
ingest(zip, { ownerId: who.user.id, own: true })
  → the single object it read (refuse a zip that yields none, or more than one)
  → if `from` and it is unchanged: answer { changed: false }, touch nothing
  → else swap: removeItems(target, [from]) + addItems(target, [{ hash, id }])
```

`LIMITS.save` (20/min, burst 10) — it is the same verb the draft PUT was sized for, and now it is
one piece instead of a pack. Quota is checked as everywhere else: a new object charges its new
blobs to the owner, and `checkQuota` refuses with a sentence.

Answers `{ hash, id, fresh, changed, replaced }`, so the editor can say "saved to *Saved*, and it is
a new piece" or "nothing changed" without a second call.

## 2. The plugin: checkouts

A new concept beside packs, and deliberately not a pack source — a pack source installs a whole
pack, which is the thing being moved away from.

- **Where.** `/checkouts/<8 of the hash>-<name>/`, one object each, in the same virtual filesystem.
- **What marks it.** `.armorpieces-checkout.json` in the folder: `{ site, hash, id, origin: { kind:
  'collection'|'pack', id, name } }`. `sanitize_pack.py` drops files that are not pack files, so it
  cannot reach an ingest even by accident; `export_pack.py` is told to leave it out anyway.
- **New API.** `checkout(hash, origin, done, fail)` — `origin` is the bag the card came from,
  which the zip does not carry and the site is not asked twice for — `checkin(dir, done, fail)`,
  `checkouts()`, and `checkoutOf(dir)` so the panel can say what a folder is. These sit beside
  `openDraft`/`saveDraft`, which stay for the whole-pack case (the pack page's embedded editor).
- **And `openCheckout(dir)`, which the first draft of this section did not see it needed.**
  `open(key)` resolves an id across every pack here and the first found wins, so checking out your
  own `armorpieces:circlet` while a pack in this browser also defines one would open the pack's
  copy, edit that, and save it where the library never hears of it. A checkout is addressed by its
  FOLDER.
- **Loot, in the end, needs nothing here** (decision 5 anticipated a control that does not
  exist). The plugin's loot rows are `data.loot` in the piece's own data file — part of the
  OBJECT, and they travel with it. What belongs to the pack is `tag_memberships`, which this
  editor has never edited and still does not. The care it needs is server-side, in the order the
  check-in writes its rows.
- **Save.** `savePiece` writes the working tree as it does now — local, fast, always. When the
  folder is a checkout, the editor is signed in and the check-in setting is on, it then checks in,
  debounced, and the status line says so. The check-in never gates or delays the local write: a
  failed or refused check-in leaves a saved working tree and a message, not lost work. The
  *Check In to My Library* action does the same thing on demand, setting or no setting, and is how
  you resolve a `changed elsewhere` refusal after looking at it. Decision 9.
- **The desktop gets this too.** The account source is already platform-neutral: `siteJson` works
  there on a device token. Nothing in this section is web-only.

And the caller that is simply missing: a **Save to the working copy** button on the pack page's
embedded editor (`LibraryPackDetail.astro` + `public/pack.js`), calling the `saveDraft` that has sat
uncalled since it was written. One button, one line of glue.

## 3. The new tab

One card grid in the library's style, over `GET /api/me/pieces.json` — `heldPieces(userId)` shaped
the way `LibraryBody.astro` shapes it for the Pieces tab, plus the collection and pack rosters the
filter selects need. Same query, same cards, same words as `/library/?view=pieces`.

- **Filters, named after the `data-` attribute they match**, as `gallery.js` does it: search,
  `kind` (piece / skin / cloth — this is where "keep pieces/skins" lands, as a filter rather than
  two tabs), `socket`, `collection` (multi), `pack`, `license`, `author`, and `where`.
- **`where` is the source axis**: *in my library* (default, signed in) / *in this browser*. A card
  carries chips saying which packs and collections hold it, exactly as the library page's do.
- **Thumbnails**, from the same `/library/…` pictures the site renders. Local-only pieces have none
  until something renders them; the empty state the gallery uses is fine.
- **Clicking a card checks it out and opens it.** A piece already in a checkout folder opens from
  there without a fetch.
- **Signed out** it is the same grid over the browser's packs alone, with one line offering sign-in.
  Nothing about it is broken by having no account.

The anchor-grouped list the page has today is a *view*, not a filter, and it is good — keep it as an
option once a socket is not selected. The pack-scope select goes: it is the working tree's idea of
scope, and the `where`/`pack` filters replace it.

## 4. New piece → a collection

The dialog gains a destination and loses two folder pickers:

- **Name**, **namespace**, **anchor** as today.
- **Where**: one of your collections, one of your packs, *+ New collection…* (`POST
  /api/me/collections`, which exists), or *this browser only*.

The piece is created in the working tree — a checkout folder with no hash yet — so Blockbench and
the Python have their folder. The first Save checks it in with no `from`, which creates the object
as **yours** (`own: true`) and adds it to the chosen bag. Every later Save swaps the hash.

Signed out, or with *this browser only*, it lands in a local pack exactly as it does today.

## 5. Retiring the shim

Once section 3 is in, the editor's *Packs… › From your library…* is the only reader of
`/api/me/library.json` left, and it is the old dialog over the old shape. Replace it with the same
piece list the new tab uses plus the pack list from `/api/me/packs`, and the route is dead. Drop it
in the release after, with the section 7 cleanup that `content-model.md` already has pending.

## Order

1. `oneObjectPack()` + the checkout route + tests. Nothing else can be tried without it.
2. The check-in route, the hash swap, the quota and rate limits, tests.
3. The plugin: checkout folders, the three API calls, Save's check-in, the loot rule of decision 5.
4. `GET /api/me/pieces.json`.
5. The new tab screen.
6. New piece with a destination.
7. The Save button on the pack page's embedded editor.
8. Retire the shim.

Steps 1–2 and 4 are ArmorPiecesSite; step 3 and 6 are the **mod repo's** plugin; step 5 is
ArmorPiecesBlockbench. The deploy chain is unchanged and still three repos in order: mod →
`npm run plugin` and `npm run bundle` **from the published clone** → commit `web/*` →
site `npm run sync` → deploy. See `armorpieces-blockbench-web` for why the bundle comes from the
clone and not the working copy.

## Verification

- Node tests for both routes: a checkout round-trips to the same hash through `ingest` (the parity
  the object store already asserts elsewhere); a check-in with no change answers `changed: false`
  and writes nothing; a check-in of somebody else's hash is refused; a checkout of a hash the asker
  does not hold is 404, not 403 with a hint.
- `test:browser` in ArmorPiecesBlockbench, against a signed-in fixture: the new tab lists the
  library, a filter narrows it, a card checks out and opens, Save checks in and the hash moves.
- The existing browser test asserts `91 parts` and 15 skins from the bundled example pack. The main
  pack split has moved those numbers; whatever the bundle says at build time is what the test should
  say, and it should not be the *library* count once the tab is a query.

## Risks

- **A checkout is a copy, and copies go stale.** Two tabs, or a tab and the site's own pack page,
  can edit the same object; the second check-in silently wins because the hash it replaces is no
  longer the one in the bag. The cheap answer is to send `from` and refuse the swap when the bag no
  longer holds it, with "this piece changed elsewhere" — which is the same shape as the artifact
  conflict rule and is worth having from the start rather than added after somebody loses an
  afternoon.
- **Ingest is not free.** Sanitise plus manifest under Pyodide, per save, on a one-core box. It is
  one piece rather than a pack, which is the improvement, but `LIMITS.save` is what stands between
  an autosave loop and the site answering nothing. Debounce on the editor side too.
- **The working tree will accumulate.** Checkouts are cheap and nothing prunes them. A checkout
  whose object is no longer held anywhere is garbage; sweep it on the start page's refresh.
- **Signed-out use must not regress.** Everything in sections 3, 4 and 2 has a signed-out branch,
  and the browser tests should run both.

## Open

Nothing. The one question this plan carried — whether Save checks in by itself — was answered on
2026-09-08 and is now decision 9: it does, with a checkbox to turn it off and a *Check In to My
Library* action beside Save for doing it by hand. The plan is ready to build, starting at step 1
of the order above.
