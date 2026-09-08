# Plan: local-first — a library without an account, and pictures that are never recomputed

`docs/plans/website.md` built the site and `docs/plans/wardrobe-library.md` built the loop on it:
gallery, library, wardrobe, packs. Both assumed the loop begins at `/account/`. It should not. A
player who has just installed the mod and wants to look at pieces should be able to browse, keep
what they like, dress a figure, and download a pack of exactly that — **without an account** — and
sign in only at the moment they want something the browser cannot do for them: publish a pack, host
one, or have their shelf follow them to another machine.

Two things follow from that, and this plan is both:

1. **The shelf and the wardrobe work signed out**, in the browser, and are *adopted* into an account
   when one is made — nothing lost, nothing re-picked.
2. **Every stored picture is rendered once, ahead of the person who wants to see it, and kept.**
   Storage is cheaper than recomputing; a headless Chromium on a 1-core box in front of a visitor is
   the most expensive thing the site can do.

This does **not** change how the accounts that exist are proven. The four OAuth providers in
`auth.config.ts` stay. Identity is the one thing worth not running ourselves: no passwords, no
resets, no mail deliverability, no breach. "No account needed" is about *where a visitor's data
lives*; it is a different question from *how a user is recognised*, and the answer to the second one
is already right.

---

## What is already there

Half of section 1 exists, deliberately, and its comments already say so. This plan mostly finishes a
shape the code has committed to rather than introducing one.

| already true | where |
|---|---|
| The gallery keeps an anonymous selection in `localStorage` | `public/gallery.js:14`, "a library that forgets itself" |
| Signing in offers to *adopt* it, and only clears what the server took | `public/library.js:33` |
| The wardrobe keeps a working set in the browser | `public/wardrobe.js:22` |
| Composing and downloading a pack needs **no session at all** | `src/pages/api/compose.ts` — an IP bucket, nothing more |
| The editor is entirely local (IndexedDB), and always was | `src/pages/editor/index.astro` |
| The privacy and cookie pages already describe all of it | `/privacy/`, `/cookies/` |
| Piece thumbnails are rendered once, at approval | `api/admin/publications/[id].ts:20` |
| Set pictures are content-addressed and cached `immutable` for a year | `src/pages/wardrobe/[hash].png.ts` |

What is missing is that the **pages do not present it**: `/library/` signed out is a page of prose
about libraries, `/wardrobe/?view=mine` is a link to `/account/`, the local selection is a flat list
of bare ids that cannot round-trip into `library_pieces`, and set pictures are rendered *lazily, in
front of the visitor, one at a time*.

---

## The shape

**Local is a shelf, not a copy.** Everything the browser keeps is *references* — a pack id, a
`(pack, piece)` pair, a set of ids and materials. Exactly what the database rows hold. Nothing local
is bytes, with one exception that is already true and stays out of this plan: the editor's own packs
in IndexedDB.

**One source of truth at a time.** `gallery.js` already has the rule and it is the rule everywhere:
signed in, the server is the whole truth and `localStorage` is not read; signed out, the browser is
the whole truth. The only moment both are read is adoption, and adoption is one-way and ends by
clearing what was taken. Two shelves merging continuously is how this feature rots.

**The account line is a capability line, not a paywall.** An account buys exactly the things a
browser cannot do:

| signed out (local) | needs an account |
|---|---|
| browse the gallery and the wiki | publish a pack to the gallery |
| keep packs and pieces on a shelf | host a pack (quota, versions, review) |
| dress a figure, keep sets | a share link for a set, and its rendered picture |
| compose and download a pack | link a GitHub repo or a Drive file |
| the whole editor, packs on disk | the desktop plugin's device token |
| export the shelf as a file | the shelf on a second machine |

That line is honest and it is easy to say on the page: *a local set has no picture and no link
because nobody has published it.* Which brings section 5.

---

## 1. The local shelf

`localStorage`, one versioned object per concern, all under the `armorpieces.` prefix already in
use.

```
armorpieces.library  = { v: 1, packs: [{ pack, version, at }], pieces: [{ pack, piece, at }] }
armorpieces.sets     = { v: 1, sets: [{ id, name, data, hash, at }] }
armorpieces.wardrobe = the dressing room's working draft   (unchanged, one set)
armorpieces.selection = the old flat list                  (migrated on read, then removed)
```

**The key has to be fixed first.** `armorpieces.selection` holds bare piece ids; `library_pieces` is
keyed `(userId, packId, pieceId)`. The gallery's cards already carry the pack — `data-pack` on every
`[data-piece]` — so recording it costs nothing from here on. Migration for what is already in
people's browsers is free too: `/api/me/library` POST already resolves a missing `packId` through
`packOfPiece`, so an old flat id adopts correctly without a lookup on the client.

Extract the read/write/migrate into **`public/local.js`** exposing `window.ArmorPiecesLocal`, and
have `gallery.js`, `library.js`, `wardrobe.js` and `verbs.js` use it. It is the only new file with
logic worth testing, and it can be tested (see *Tests*).

`/library/` signed out stops being a page about libraries and becomes **the shelf**, laid out the way
the signed-in one is — the same `PieceCards`, the same PACKS/PIECES toggle. It cannot be rendered on
the server, because the server does not know what is in the browser, so signed out the page ships the
same markup for everyone and fills the cards client-side from `/gallery/index.json` (already the
canonical catalogue, already cacheable) against the local shelf. Signed-out the page therefore stays
fully cacheable, which the signed-in one never was.

The prose that is there now is not wasted — it moves above the shelf as a short line with the one
honest sentence about what an account adds, and the rest goes to `/wiki/`.

## 2. The local wardrobe

The dressing room already works signed out; only *keeping* does not. `armorpieces.sets` is a list of
saved outfits with the same `data` shape a `sets` row holds, and `setHash` is a pure function of the
set, so the local card and the server row agree about identity from the start.

`/wardrobe/?view=mine` gets a signed-out branch that renders from the local list instead of the
query. Its cards have no rendered figure — see section 5 — and show the stacked per-piece thumbnails
`public/wardrobe.js` already paints, which is instant and costs the server nothing.

`MAX_SETS` is 200 on the server; the local list gets the same cap, so a shelf that adopts cannot be
refused for being too long.

## 3. Adoption

`public/library.js` already does this for pieces, correctly, including the part that matters: only
what the server actually took is cleared from the browser, and a refusal stays visible. Three
changes:

- carry **packs and sets** as well as pieces. `/api/me/library` POST already takes
  `{save:[{kind:'pack'|'piece', ...}]}` in bulk and answers per entry; sets go to `/api/me/sets`,
  one POST each, which is fine at ≤200.
- fire on **first sign-in**, not only on a button on `/library/`. The account page is where a new
  user lands; the offer belongs there too, and it should be an offer — "keep the 34 pieces and 3
  sets from this browser?" — never automatic. Someone signing in on a friend's machine must not
  silently hoover up the friend's shelf.
- respect the caps already enforced (`MAX_SAVED_PIECES` 5000, `MAX_SAVED_PACKS` 500, `MAX_SETS` 200)
  and show what was refused. The API already answers with `refused`; the page has to render it.

Adoption is **additive and idempotent**: saving something already on the shelf is not an error, so
adopting twice is harmless, and a half-finished adoption resumes.

## 4. Losing it

Clearing site data throws a local shelf away silently, and that is the one real cost of this plan.
Two mitigations, both small:

- **Export/import a shelf as a JSON file** from `/library/`. `/api/me/export` already exists for the
  account side and the file should be the same shape, so an export from either can be imported into
  either.
- Say it plainly on the page, once, near the shelf — not a banner, a line. `/cookies/` already says
  it in the right place.

---

## 5. Pictures: render ahead, keep forever

Nothing that gets stored is browser-generated today, and that is right: both renderers are headless
Chromium driving the site's own `/editor/app/` (`scripts/thumbnails.mjs`, `scripts/wardrobe-shot.mjs`).
The browser makes only the *live, interactive* figure, which is not stored and should not be.

The problem is **when**. Piece thumbnails already render once at approval. Set pictures render
**lazily, on the first GET of `/wardrobe/<hash>.png`, serialised one Chromium at a time**
(`setshot.ts:19`). `src/pages/wardrobe/index.astro:85` renders up to 120 public sets plus the
official ones as `<img src="/wardrobe/<hash>.png">`, so the first visitor to a cold wardrobe queues
that many renders, each booting Chromium, Blockbench *and* Pyodide — the script allows itself 240
seconds — each holding an inbound request open, and each making further inbound requests to the same
server, because it loads the editor from this site. `loading="lazy"` softens it to what is scrolled
into view; it does not fix it. This is how a wardrobe with any traffic falls over.

**Decision: storage is cheaper than recomputing.** Every picture is rendered ahead of the person who
wants it and kept indefinitely. The site never renders in front of a visitor.

1. **Render on save.** `/api/me/sets` POST computes `setHash` already; queue the render there,
   fire-and-forget, exactly as `renderThumbnailsFor` is queued from the approve route. Not on publish
   — on *save* — because the picture is what makes the wardrobe's own "Mine" view worth looking at,
   and because the cost then lands on the person who made the outfit.
2. **Bake the official sets into the image.** `officialSets()` is deterministic from the mod's data,
   so the six (plus any pack's own) render in CI: boot the built server, run `wardrobe-shot.mjs`
   against `127.0.0.1`, copy `data/sets/` into the image. The box never renders them at all.
3. **Two sizes.** Cards ask for 256 and the file is 640 today; that is most of the wardrobe index's
   bytes. Render both, `256` for cards and `640` for the set page and the OG card.
4. **`/wardrobe/<hash>.png` never blocks.** Present → serve it. Absent → queue and answer 503 with
   `retry-after` (the route already has this branch for a machine with no Playwright) so the card
   falls back to the stacked thumbnails. A missing picture is a page that still works.
5. **Dedupe in flight.** `renderShot` checks `existsSync` *before* queueing but the job never
   re-checks, so two simultaneous asks for the same missing hash render it twice. A
   `Map<key, Promise>` of in-flight renders, and an `existsSync` at the top of the job.
6. **A backfill script.** `npm run shots` — walk the sets that have no picture and render them,
   slowly, one at a time. It is how the first deploy after this lands, how a renderer change is
   caught up, and what a cron can run at night.

**Caching is already as good as it gets and stays that way.** The URL is the sha256 of the set with
the name removed (`wardrobe.ts:253`), so the same outfit is the same file for everyone, an edited
outfit is a *different URL*, and `public, max-age=31536000, immutable` can never be stale. There is
one exception worth naming: the picture also depends on the **renderer** — a new editor build draws
the same set differently. So the URL takes the editor stamp `lib/mod.ts:117` already exposes:

```
/wardrobe/<hash>.png?w=256&v=<short commit>
```

One route, one file per (hash, size, stamp), honest `immutable` on all of them, and an editor bump
simply produces new URLs while the old files stay on disk until someone sweeps them. Pages emit the
current stamp; a request with no `v` serves the newest generation on disk.

**Anonymous sets are not rendered.** A local set has no row, no owner and no share link, and
rendering an arbitrary posted set would be a free headless-Chromium-per-request for anyone who asks —
the single most expensive DoS the site could offer. The dressing room's live figure and the stacked
per-piece thumbnails are what a local set gets, and a rendered picture is one of the things saving
buys. This is the clearest possible statement of the account line, and it is on the page for free.

**Budget.** ~60 KB at 640 and ~15 KB at 256, so ~75 KB a set-generation. 200 sets per user, 20 GB of
disk on the box: ten thousand sets is under a gigabyte. Storage is not the constraint; the single
core is, which is the whole argument. Add `data/` to whatever the deploy notes already watch.

---

## Decisions

1. **OAuth stays.** Four providers, no passwords, no magic links. Out of scope for this plan except
   to say so.
2. **Local holds references only.** No bytes in `localStorage`. The editor's IndexedDB packs are the
   pre-existing exception and are untouched.
3. **One source of truth at a time.** Signed in, `localStorage` is read only during adoption.
4. **Adoption is offered, never automatic**, and is additive and idempotent.
5. **Local caps match server caps**, so nothing on a local shelf can fail to adopt for being too many.
6. **Signed-out `/library/` is client-rendered over `/gallery/index.json`**, which keeps it cacheable.
7. **Every stored picture is rendered ahead of the visitor and kept forever.** No eviction, no
   render-on-view.
8. **A picture's URL carries the set hash, the size and the editor stamp**, so `immutable` stays true
   across renderer changes.
9. **Anonymous sets get no rendered picture**, both because they have no owner and because rendering
   on demand for unauthenticated input is unbounded cost.

## What stays account-only

Publishing to the gallery; hosting a pack (quota, versions, review); a set's share link, its
`/wardrobe/<id>/` page and its rendered picture; featuring; GitHub and Drive links; device tokens for
the desktop plugin; the shelf on a second machine.

## Build order

1. `public/local.js` — the versioned local store, the migration off `armorpieces.selection`, the
   caps. Rewire `gallery.js`, `library.js`, `wardrobe.js`, `verbs.js` onto it. *No visible change yet;
   this is the one commit that can break everything, so it lands alone.*
2. Section 5, points 4, 5 and 1 — stop the wardrobe blocking, dedupe, render on save. **Ship this
   before the wardrobe has traffic; it does not depend on anything else in this plan.**
3. Section 5, points 2, 3 and 6 — two sizes, the stamped URL, the official sets baked in CI,
   `npm run shots`.
4. Signed-out `/library/`: the shelf, client-rendered.
5. Signed-out `/wardrobe/?view=mine`: local sets, stacked thumbnails, the line about pictures.
6. Adoption: packs and sets, the offer on `/account/`, refusals rendered.
7. Export/import a shelf.

## Tests

`npm test` is `node --test` over `test/*.test.mjs` against mocks; these fit that.

- **`test/local.test.mjs`** — evaluate `public/local.js` in a `vm` with a stub `localStorage` and
  assert: a v0 flat selection migrates to v1 with the pack resolved-or-null; caps refuse the 5001st
  piece; a corrupt value yields an empty shelf rather than throwing; a private-window
  `localStorage` that throws on write is survived (the existing files all guard this — keep it).
- **`test/adopt.test.mjs`** — a local shelf of packs, pieces and sets against the real
  `/api/me/library` and `/api/me/sets` on PGlite: everything lands, a second run changes nothing,
  and a refusal is reported per entry rather than failing the batch.
- **`test/wardrobe.test.mjs`** (extend) — `setHash` is stable across key order and ignores the name
  (already relied on, worth pinning); a set saved through `/api/me/sets` queues exactly one render;
  two concurrent asks for one missing hash queue one job; `/wardrobe/<hash>.png` for an unrendered
  hash answers 503 promptly rather than blocking.
- **`test/site.test.mjs`** (extend) — signed out, `/library/` and `/wardrobe/?view=mine` render 200
  with no session and no database read for the shelf.

## Traps

- **The selection key.** Anything that ships before the migration writes ids that cannot name a pack.
  Section 1 is first for this reason.
- **`/library/index.json` must never move.** Every desktop plugin derives `siteOrigin()` from it
  (`docs/plans/wardrobe-library.md` §1); the signed-out shelf is a *page* change, not a route change.
- **CSP allows no inline script**, which is why every one of these is a file under `public/`.
- **The renderer loads the site itself.** Anything that renders during a request is a request that
  makes requests; keep every render on the fire-and-forget side of an HTTP response.
- **`officialSets()` is synchronous and cached** and reads the static index only. Baking its pictures
  in CI is fine; do not reach for approved uploads there.
- **Private sets** are `private, max-age=60` and must stay off any shared cache when the stamped URL
  lands.
