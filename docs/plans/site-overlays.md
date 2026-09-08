# Plan: the overlay pass — a detail is a layer, and still a page

`docs/plans/website.md` built the site, `wardrobe-library.md` built the loop on it and
`content-model.md` made a piece a thing rather than a row in a pack. Every one of them added a
**detail page**: `/gallery/pieces/<ns>/<name>/`, `/gallery/packs/<id>/`, `/wardrobe/<id>/`. They are
right as pages — an id is a URL, a URL is shareable, a crawler reads it — and wrong as the *only*
way to look at a piece.

Because looking at a piece is not going somewhere. It is glancing aside. Clicking a card in the
gallery today throws away the filters you set, the pack you were browsing and where you had
scrolled to, and offers one way back: a `← Gallery` link that returns you to the top of a page you
no longer recognise. And the gallery is not even the main place pieces are opened — your library
opens them, a pack's page opens them, an outfit opens them, and every one of those gets the same
one-way trip and the same wrong link back, because the link can only name one origin.

So: **a detail opens as a layer over where you were**, with a close button, and remains a whole
page for anyone who arrives at its URL. And while the library page is being touched, the two long
forms that have grown under its list of packs — *New pack*, *New collection* — move out to pages of
their own.

No framework. The CSP allows no inline script (`src/middleware.ts`), the site is nineteen
frameworkless modules on `data-` hooks over server-rendered HTML, and `public/ui.js` already exists
as the floor underneath them. This pass adds one module and three primitives to that floor.

---

## What is already there

| already true | where |
|---|---|
| One modal, with a backdrop, Escape, focus and a promise — replacing 22 native `prompt/alert/confirm` | `public/ui.js`, `.ap-dialog` in `src/styles/global.css` |
| `UI.call`, `UI.status`, `UI.working`, `UI.el`, `UI.cards`, `UI.jsonOf` | `public/ui.js` |
| The piece card is **one component** the gallery and the library both draw | `src/components/PieceCards.astro` |
| The verbs a card carries are **one module**, loaded by both | `public/verbs.js` |
| Every detail route already renders on request with its own cache header | `prerender = false` in the three routes |
| A view that lives in the URL, so a link to it is a link | `/gallery/?view=pieces&pack=…` |

What is missing is that a detail has no way to be anything but a navigation.

---

## The three decisions

### 1. Partial mode: `?partial=1`

Each detail route answers `?partial=1` with its body and nothing else — no `<html>`, no header, no
footer — under the same `cache-control` as the page it belongs to. The body moves into a component
that both modes render, so there is exactly one copy of the markup and no chance of the layer and
the page drifting apart.

`?partial=1` is a **distinct URL**, not a `Vary`-ing header on the same one. A distinct URL caches
without special-casing, can be fetched by hand while debugging, and cannot be served to a browser
that asked for the page.

### 2. The link is still a link

`public/overlay.js` intercepts a *plain left click* — no modifier, no middle button, same origin —
on `a[data-overlay]`, fetches the partial and shows it in a sheet. `history.pushState` puts the
real URL in the address bar, so the thing on screen is still the thing you can copy the link to,
and Back closes the layer.

Everything else falls through to the browser: no JavaScript, a middle click, a new tab, a crawler,
a fetch that fails. That is the whole progressive-enhancement claim, and it is why the links stay
ordinary `<a href>` elements rather than becoming buttons.

Opening a piece from inside a pack sheet **pushes onto a stack**, and the sheet grows a back arrow.
The stack is the history — one `pushState` per level — so the browser's Back walks it and closing
from three deep is `history.go(-3)`, which puts the address bar back where it started.

### 3. Modules mount per subtree

Every module binds with `document.querySelectorAll` at load, which is correct for a page and blind
to a subtree that arrives later. `ui.js` grows three primitives:

- **`UI.mounted(fn)`** — register a binder. It runs immediately for every live root (the document,
  plus any open sheet) and again for each subtree the overlay inserts.
- **`UI.mount(root)` / `UI.unmount(root)`** — what the overlay calls; nothing else should.
- **`UI.need(src)`** — inject a module the host page did not load, once, and resolve when it is
  ready. A pack sheet opened from the gallery needs `report.js`, which the gallery never loads.

Each partial declares what it needs in `data-needs`, so the sheet loads exactly the modules its
content binds and no more. This is the same rewrite `ui.js` performed once already, applied to the
five modules whose hooks can appear inside a detail.

Module-level *state* stays module-level — `gallery.js`'s `savedPieces` and `savedPacks` are the
answer to one question asked once per page load, and a second sheet must not ask it again. Only the
*binding* moves into the callback.

---

## What is built

### The layer

| file | what |
|---|---|
| `public/ui.js` | `mounted`, `mount`, `unmount`, `need`, and the list of live roots |
| `public/overlay.js` | new: the interception, the sheet, the stack, `popstate`, focus, the partial cache, the fallback |
| `src/styles/global.css` | `.ap-sheet` beside `.ap-dialog`: same backdrop idiom, wider, a header row with the title, a back arrow and a close button |
| `public/gallery.js`, `verbs.js`, `report.js`, `shots.js`, `wardrobe-set.js` | rewritten onto `UI.mounted` |

### The three details

Each route becomes a component plus a two-branch route file.

| route | component | `data-needs` |
|---|---|---|
| `gallery/pieces/[ns]/[name].astro` | `components/PieceDetail.astro` | `/local.js /gallery.js /verbs.js` |
| `gallery/packs/[id].astro` | `components/PackDetail.astro` | `/report.js` |
| `wardrobe/[id].astro` | `components/OutfitDetail.astro` | `/shots.js /local.js /wardrobe-set.js` |

```astro
{partial ? <PieceDetail … /> : (
  <Base title={piece.name} description={…}>
    <PieceDetail … />
    <script is:inline src="/ui.js"></script>…
  </Base>
)}
```

The component always renders `<div class="detail" data-detail data-needs=… data-title=…>`, which
is what the sheet reads for its header. The breadcrumb (`← Gallery`) belongs to the page and is
hidden inside a sheet, which has its own chrome and its own honest way back.

**The piece sheet carries the card's verbs** — Save, Add to selection, Wear it, Add to a pack… — so
a layer is never a dead end. This also fixes something that was quietly broken: the piece page's
`data-select` had no `data-pack` on its host element, so *Save* on a piece's own page wrote a row
with a null pack.

### The links that become layers

`data-overlay` goes on: the card link in `PieceCards.astro`; *Details* on the gallery's pack cards
and on the library's linked-pack cards; the piece cards on a pack's page; the outfit cards and
*Look* in the wardrobe; the featured-outfit strip on the gallery and the main page; the outfit
cards under `/library/?view=outfits`; the *Pack* link inside a piece detail.

*Browse its pieces* stays a navigation. It changes what the gallery is showing, which is not a
detail — and the distinction is the whole rule: **a layer is a thing you look aside at, a
navigation is a change of what you are looking at.**

### The library's two forms

- `src/pages/library/packs/new.astro` — the *New pack* form, the `fromCollection` select and the
  prose about what a pack is. A static segment beats a dynamic one in Astro, so `/library/packs/new/`
  resolves here and not to `[id].astro`. Signed out it redirects to `/account/`, as its sibling does.
- `src/pages/library/collections/new.astro` — the same for *New collection*.
- `src/pages/library/index.astro` — the two `<details>` blocks come out; the Packs and Collections
  views get a button in a `.title-row`, and the empty states point at the new pages.

These are **pages, not layers**, deliberately. Making a pack is somewhere you go: it wants a URL,
it is linked from the editor and from a collection's *Make a pack of it*, and it ends by taking you
somewhere else. A layer is for looking.

---

## Check

- `npm run build && npm test` in `ArmorPiecesSite`.
- New `test/overlays.test.mjs`: for a piece, a pack and a shipped outfit — the partial answers 200,
  carries `data-detail`, and carries neither `<html` nor the footer's disclaimer; the whole page
  still answers 200 with the disclaimer; the partial's `cache-control` matches the page's; every
  path named in a `data-needs` exists under `public/`.
- `test/site.test.mjs`: `/library/packs/new/` and `/library/collections/new/` redirect to `/account/`
  signed out.
- By hand (`npm run start`, after a build — the server must be restarted for a new one): gallery →
  a card (sheet, URL changed, Escape closes, filters and scroll intact) → *Details* on a pack → a
  piece inside it (back arrow, then Back) → the same card from `/library/` → the wardrobe's cards →
  a piece URL pasted into a fresh tab, which is the whole page.
- With JavaScript off, every one of those links still navigates.

## Not in this pass

The library's own pack page, a collection and the review queue stay pages. They are forms, tables
and an embedded Blockbench rather than read-only details, and an editor inside a sheet is a
separate design problem.
