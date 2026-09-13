# Plan: UX round 4 — the design work

> **Status (2026-09-14): BUILT**, on ArmorPiecesSite branch `ux-4` off `main` (PR #7 merged first as
> `ff39f01`, decision 1), ten commits `2f3775b`..`30cbb93`, one per item; the plugin half is Armor
> Pieces `f177858` and ArmorPiecesBlockbench `6e69fc8`, both on `main` and pushed. `npm test`
> 346/346 (three older suites updated to the new markup), the walk 111/111 at 1280 and 400 and
> 111/111 under `WALK_WIDE_FONTS=1`. R1, R27 and R28 struck through in the review; only R26 stands,
> by decision 4. The "As built" section at the end records what differs from the plan. Written
> 2026-09-13 as: planned, nothing built. Round 4 of `docs/plans/ux-rounds.md`, the one
> that round said to plan before building "because these change what a page is, not what a line
> says". Read against ArmorPiecesSite `ux-3` = `ff3fe14` (PR #7, not yet merged), the mod working
> copy, and ArmorPiecesBlockbench `2da8ef0`. Every line number below is from those and is
> re-verified at fix time. The review it answers is `docs/reviews/site-ux-2026-09-12.md`; its
> numbers are cited as **R1**, **R28**. Those two are the last broken items this round can close
> (R26 stays open by decision 4 of the rounds plan - ship 0.4.0 - and R27 was built in Round 0 in
> the mod, `fabric.mod.json:9` and `modpage.yml:12`, and only wants striking through).

Rounds 0-3 fixed lines: a copy that lied, a control that was missing, a flag where a standing was
needed. What is left is the seventy-odd friction points that are not wrong sentences but wrong
shapes - a picker that is a grey box in the document flow, an outfit page that shows twelve
commands and no way to download the thing they need, an editor page that is a frame and one
caption, an error that is two words of `text/plain`. Each of these needs a screen decided before a
file is touched, which is what this document is for.

## 0. How to run this

- **One branch, `ux-4`**, in ArmorPiecesSite, one PR. It is bigger than Round 3 by files but not
  by risk: seven of the eight items are additive (a new page, a new route, a new attribute), and
  the one that changes behaviour - the picker - keeps every `data-` hook the walk test already
  drives. If it grows past a day, split at the line between items 1-3 (the visitor's screens) and
  4-8 (the author's and the reader's), in that order; the walk is the gate for both halves.
- **Where to branch from.** PR #7 (`ux-3`) is not merged. Either merge #7 first and branch off
  `main` (cleanest; its push run deploys Round 3), or branch `ux-4` off `ux-3` now and stack the
  PR the way Rounds 0-2 were stacked (CI runs one concurrency group per ref since `e352f0c`, so
  stacked PRs do not cancel each other). This plan assumes off `ux-3`, rebased onto `main` once #7
  lands; the choice is the user's, section 4.
- **Three repositories, in order.** Item 4 touches the desktop plugin (`tools/blockbench_plugin/
  armorpieces.js` in the MOD, committed through the clone - `armorpieces-two-repos.md`), then the
  editor bundle (ArmorPiecesBlockbench `src/start.js`, bundled from the clone -
  `bundle-from-the-clone.md`, committed on that repo's `main` because the site's CI builds the
  editor from there), and only then the site. Item 8's `authoring.md` half is the mod's too. Every
  other item is the site alone.
- **The gate** is `npm test` (run detached, it outruns the tool's cap - Round 3's note) plus the
  walk under `WALK_WIDE_FONTS=1`. Section 3 says what the walk gains. `npm run build` before the
  walk: the client scripts are served from `dist/client` (Round 1's trap), and a prerendered
  `404.astro` exists only after a build.
- **Traps carried forward:** `content/mod/library.json` is gitignored and loses its thumbnails if
  rebuilt (Round 3); don't `npm run sync` from the working copy (`storage-plan-built.md`);
  `npx tsc --noEmit` has five pre-existing errors; a Drizzle migration that adds a column is
  additive and needs no guard, but run it against the test database first anyway
  (`content-model-build.md`: the guard tripped for real once).

## 1. What is already there

The round is cheaper than it reads because most of the machinery exists and only the screens
are missing.

| already true | where |
|---|---|
| The node adapter reads a prerendered `404.html` / `500.html` off disk when an on-demand route answers `new Response(null, {status})` with an EMPTY body | `@astrojs/node/dist/serve-app.js` `readErrorPageFromDisk`; `astro/dist/core/routing/handler.js:126` reroutes only when `response.body === null` |
| One modal with a backdrop, Escape, focus restore and a promise, that takes any node as its body, at `z-index: 50` - ABOVE the overlay sheet at 40, "because a chooser raised from inside a sheet belongs on top of it" | `public/ui.js` `dialog()`, `.ap-dialog` in `global.css:317-323` |
| The picker is one component over one API, already with thumbnails (R7, Round 1) and a socket filter; it is only its PLACEMENT that is wrong | `PiecePicker.astro`, `public/picker.js`, `/api/pieces` |
| `POST /api/compose {name, set}` builds the whole outfit as one zip with the give-function, answers `{download, page, leftOut}`, works signed out, and its page has `Content-Disposition` | `api/compose.ts:1-14`, `/composed/<hash>/` |
| The outfit page is partial-capable and carries the owner's, the maintainer's and the reporter's verbs (Rounds 1-3) | `OutfitDetail.astro` |
| The editor page is already a flex-filled frame (`min-height: 30rem`) with a caption bar, deep links forwarded by script, and a full-screen link | `editor/index.astro`, `editor-frame.js`, `global.css:303-314` |
| *Upload to your library…* exists in the plugin as a verb of its own; `LIBRARY_SITE`'s only remaining job is to be the default of the `armorpieces_library` setting that `siteOrigin()` derives everything from | `armorpieces.js:58-60, 884, 1193-1199, 1358-1430` |
| `/library/index.json` is a permanent URL by contract, precisely so that this default can point at it | `src/lib/catalogue.ts:4-8` |
| Per-object publish exists as an API and the piece's standing (`new / queued / rejected / published / withdrawn / official`) is one `says` map on two pages | `api/me/objects/[hash]/publish.ts`, `LibraryPackDetail.astro:58-70`, `CollectionDetail.astro` |
| Editing a piece is three different things and `editPiece` already knows which: name / recipe / former ids make a NEW object, credit is an owner-only column, tags are the pack's | `packverbs.ts:198-215` |
| The version-cut guard, with sentences and a real "Drop it anyway" | `guard.ts`, `BreakingVersion` |
| The overlay sheet is `role=dialog aria-modal`, takes focus, returns it, honours reduced motion; the confirm dialogs open on Cancel (Round 0) | `overlay.js`, `ui.js` |
| Playwright is a dependency and already renders every thumbnail and outfit shot in Chromium | `scripts/thumbnails.mjs`, `wardrobe-shot.mjs` |
| The site's `SITE_URL` is set on the deploy (`deploy/docker-compose.yml:22`, the Dockerfile build arg from `vars.SITE_URL`); `Astro.site` is real in production | `astro.config.mjs:16` |
| The walk test lists the five error URLs "so that Round 4's error pages have a place to be asserted" | `test/pages.test.mjs:115-132` |

What is missing, item by item, is a screen.

## 2. The eight items

### 2.1 Error pages (R28)

**The screen.** One page, three sentences, the nav. It says what was asked for, does not say
"error", and offers the four places a visitor was probably going.

```
┌─────────────────────────────────────────────────────────────────┐
│ ⛨ Armor Pieces     Wiki  Gallery  Wardrobe  Library  Editor  Account │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Nothing here                                                   │
│                                                                 │
│  There is no page at /gallery/pieces/coral/reef_crown/. If a    │
│  link brought you, the piece may have been taken down or its    │
│  pack unpublished; if you typed it, check the spelling.         │
│                                                                 │
│  [Gallery]  [Wardrobe]  [Your library]  [Search the wiki]       │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  footer                                                         │
└─────────────────────────────────────────────────────────────────┘
```

The 500 is the same page with "Something went wrong on our side. It is logged; try again in a
minute, and if it keeps happening, tell us on the contact page." The 403 on the queue is the same
shape, rendered by the queue route itself: "Maintainers only. You are signed in as *name*; the
queue is for the people who review packs."

**Decisions.**

- `404.astro` and `500.astro` are **prerendered** (the site's default), in `Base`. The adapter
  reads them off disk; nothing fetches the site from inside the container (which the resolver trap
  in `armorpieces-vps.md` says would be a bad idea). The cost is that a maintainer's nav on the
  error page has no "Queue (N)" - the count comes from the middleware on on-demand pages only.
  Acceptable: it is an error page.
- The seven PAGE routes answer `new Response(null, { status: 404 })` - the body must be null or
  Astro keeps the plain text: `composed/[hash]/index.astro:15`, `gallery/packs/[id].astro:16`,
  `gallery/pieces/[ns]/[name].astro:26`, `library/collections/[id].astro:24`,
  `library/packs/[id].astro:22`, `wardrobe/[id].astro:37, 46`. The FILE routes (`.zip`, `.png`,
  `.json`) keep their sentences: they are fetched by scripts, and an HTML page in a zip's place
  is the wrong answer there.
- The path that was asked for is not available to a prerendered page, so the sentence reads it
  from `location.pathname` with two lines in a tiny `public/error.js` - and reads as "There is no
  page here." without script. No path is echoed server-side, so nothing is reflected.
- `server.mjs:126-129`, the `next` callback for a path no route matches: stream
  `dist/client/404.html` with status 404 and `text/html`, `HEAD` included; `not found` stays as
  the fallback if the file is missing (a `--offline` build, a test without a build).
- `admin/queue/index.astro:44`: instead of `new Response('Maintainers only', {status: 403})`, set
  `Astro.response.status = 403` and render the sentence above in `Base`. (403 is not one of
  Astro's reroutable statuses, so the page does it itself.)
- `overlay.js:134-137`: a partial that fails no longer navigates. The sheet keeps its title and
  shows one paragraph - "Nothing at this address any more (404). It may have been taken down." -
  with the existing *Open as a page* arrow still pointing at the URL, so the visitor can still
  go and see the branded page, and *Close* returns them to the gallery they were in, which is the
  whole point of the layer. A 5xx says "The site could not answer (503). Try again in a moment."
  The `html[url]` cache is not written for a failure, so a retry is a real fetch.

**Files.** `src/pages/404.astro`, `src/pages/500.astro`, `public/error.js`, the seven routes,
`server.mjs`, `admin/queue/index.astro`, `public/overlay.js`.

**Test.** The walk's five error URLs assert `content-type: text/html`, the nav present, a link to
`/gallery/`, no "No such" text. `site.test.mjs`: `dist/client/404.html` and `500.html` exist after
the build and contain no path. A unit test on `overlay.js` is not possible without a browser; the
walk opens a card whose partial 404s (the `?partial=1` of a withdrawn piece - the walk already has
a maintainer take one down) and asserts the sheet is still open with the notice and that the
gallery underneath is unchanged.

### 2.2 The picker as a sheet

**The screen.** Today `Choose…` on "crest" scrolls the page 1100 px to a grey panel below the
twelve socket rows, with no title and no Close (the review's "Dressing"). It becomes the modal
the site already has, over the page, titled by what it is for.

```
   ┌──────────────────────────────────────────────────────────────┐
   │  Choose for crest                                         ✕  │
   │                                                              │
   │  [The gallery ▾]  [Any licence ▾]  [Search names and ids… ]  │
   │  41 pieces                                                   │
   │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐      │
   │  │  img   │ │  img   │ │  img   │ │  img   │ │  img   │      │
   │  │ Plume  │ │ Crest  │ │ Halo   │ │ Spike  │ │ Comb   │      │
   │  │ crest  │ │ crest  │ │ crest  │ │ crest  │ │ crest  │      │
   │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘      │
   │  …                                       [More]              │
   │                                                              │
   │                                                    [Close]   │
   └──────────────────────────────────────────────────────────────┘
```

Titles: the wardrobe says **Choose for *socket*** (verb "Wear"); a pack says **Add pieces to
*pack name***; a collection says **Add pieces to *collection name***. Picking for a socket
closes the sheet (one socket, one piece); picking for a pack or a bag keeps it open and counts in
the status line ("3 added"), and *Close* is when the table underneath redraws (item 2.5's
`UI.again`).

**Decisions.**

- **Use `UI.dialog`, not the overlay layer.** The overlay is a URL - pushState, a partial, Back
  closes it - and a picker is not a place, it is a question. The dialog is already a `role=dialog`
  with a backdrop, Escape, a promise and focus restore to the opener (which is the *Choose…*
  button, exactly right), and it sits at `z-index: 50` over a pack's sheet at 40, which is the
  case that matters: a pack opened as a layer from the library, *Add pieces…* pressed inside it.
- `ArmorPiecesPicker.open(id, {socket, title, onPick})` MOVES the mounted `[data-picker]` panel
  into the dialog's body (leaving a comment node where it was) and moves it back when the dialog
  resolves; the panel keeps its `data-` hooks and its mounted state, so nothing re-mounts and the
  walk's selectors (`test/pages.test.mjs:351`) keep working. `close(id)` calls `UI.close()`. The
  document-level Escape listener in `picker.js:126-129` goes: the dialog owns Escape now.
- `dialog()` gains one option, `wide: true`, that adds `.ap-dialog-wide` (`max-width: 62rem`, the
  sheet's width). The list's `max-height: 26rem` becomes `min(26rem, 55vh)` so the dialog's own
  `max-height: 85vh` keeps the filter bar and the Close button on screen on a phone.
- The search box takes focus on open, as now - inside a fixed dialog the keyboard raising no
  longer scrolls the page away (the review's phone complaint), and typing is what the visitor
  came to do.
- The dialog's resolve value is the number of picks made; the caller (`pack.js:96-109`,
  `collection.js:86-87`) does `if (n) UI.again()` and the "Reload to see it in the table" line
  goes, which is item 2.5's last bullet done here.

**Files.** `public/picker.js`, `public/ui.js` (`wide`), `src/styles/global.css`, `public/pack.js`,
`public/collection.js`, `public/wardrobe.js` (passes the socket's name as the title).

**Test.** The walk: press *Choose…* on crest at 400 px; assert `document.activeElement` is inside
`.ap-dialog`, the dialog's `aria-label` contains "crest", `window.scrollY` did not change, Escape
returns focus to the *Choose…* button. The existing picker test (pictures, gallery id) stays.
`pages.test.mjs:367` (an empty pack filled from its own page) asserts the table has the row
WITHOUT a reload.

### 2.3 The outfit page

**The screen.** The two things a visitor wants from an outfit - the pack that makes it work and
the command to wear it - move up beside the figure; the report form learns about official outfits.

```
  ← Wardrobe · your sets
  Knight Errant  [public] [featured]
  12 pieces, a skin. By mattjes, saved 2026-09-06. 9 from Armor Pieces, 3 from Coral.

  ┌──────────────────┐  ┌──────────────────────────────────────────────────┐
  │                  │  │ Get it                                           │
  │    the figure    │  │ [Download the pack]  one zip, both halves, with  │
  │                  │  │ a function that gives the whole set.             │
  │                  │  │ Needs Armor Pieces 0.4.0 or later on 26.2.       │
  │ [Show the real   │  │ Left out: reef_crown (all rights reserved, in    │
  │  figure]         │  │ its own pack).                                   │
  └──────────────────┘  ├──────────────────────────────────────────────────┤
                        │ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐     │
                        │ │piece │ │piece │ │piece │ │piece │ │piece │ …   │
                        │ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘     │
                        ├──────────────────────────────────────────────────┤
                        │ Wearing it                                       │
                        │ head · diamond_helmet                    [Copy]  │
                        │ ┌──────────────────────────────────────────────┐ │
                        │ │ /give @s minecraft:diamond_helmet[…]         │ │
                        │ └──────────────────────────────────────────────┘ │
                        │ chest · …  too long for a chat line     [Copy]  │
                        │ …                                                │
                        └──────────────────────────────────────────────────┘
  Something wrong with this outfit?  [report form]   — or, official:
  "This outfit ships with the mod; tell us by email if something is wrong with it."
```

**Decisions.**

- **Download = the composed pack.** `POST /api/compose {name, set}` is the one route that builds
  an outfit as an installable pack with its give-function, omits reserved pieces and lists them
  (Round 3), works signed out and is rate-limited. `/wardrobe/<id>/pieces.zip` is NOT it: that is
  the figure's zip of borrowed pieces only, 204 when nothing is borrowed. So the button is a verb
  in `wardrobe-set.js` (`data-outfit-download`): compose, then `location.href = data.download`
  (the zip has `Content-Disposition`), and the status line says "Built - also at *its own page*"
  with `data.page` as a link, plus the `leftOut` names. The route does not compose at render time:
  the outfit page is public-cached and a zip is not something to build for a crawler.
- The name handed to compose is the outfit's name slugged the way `wardrobe.js:363-365` already
  does; move that slugging into `ui.js` as `UI.slug` so there is one.
- **Copy per command.** The dressing room has a per-command *Copy* (`wardrobe.js:229-236`); the
  same button on the outfit page, with the clipboard write moved into `ui.js` as `UI.copy(text,
  statusEl)` so both pages use one and the status ("Copied.") is one sentence.
- **Layout.** The `.wardrobe` grid stays two columns; the right column becomes three stacked
  panels - Get it, the cards, Wearing it - so the commands sit beside the figure instead of under
  the whole thing. At 900 px and under the grid is already one column. `.gives > * { min-width: 0 }`
  (Round 0) still applies inside the panel; the walk's `scrollWidth == clientWidth` proves it.
- **Report on official outfits.** The piece page already does this for official pieces (an
  email sentence instead of the form, `PieceDetail.astro:91-93`); the outfit page gets the same
  sentence pointing at `/contact/`.
- The "Open this in the dressing room to build the pack" sentence under the commands is
  shortened to "Open this in the dressing room to change it" - the pack is one click away now.

**Files.** `OutfitDetail.astro`, `public/wardrobe-set.js`, `public/wardrobe.js`, `public/ui.js`,
`global.css`.

**Test.** The walk's outfit page: a control whose href or resulting navigation ends in `.zip`
(the rounds plan already reserved this assertion); after clicking Download the response is
`application/zip`; a *Copy* per `<pre>`. `outfits.test.mjs`: the official outfit's page contains
`/contact/` and no `<form data-report`.

### 2.4 One "Make a piece" page for `/editor/`

**The screen.** The editor page stops being a frame with a caption and becomes the one entry the
review said did not exist: what you are about to use, where your work goes, and the three steps
after it.

```
  Make a piece                                             [How to use it] [Full screen ↗]
  ┌─────────────────────────┬─────────────────────────┬──────────────────────────────────┐
  │ 1  Make                 │ 2  Pack                 │ 3  Offer                         │
  │ Model and paint it here.│ Save it into a pack in  │ Cut a version, then offer the    │
  │ Nothing leaves this tab │ your library, or keep   │ pack to the gallery from its     │
  │ until you say so.       │ it in this browser.     │ page. A maintainer reviews it.   │
  └─────────────────────────┴─────────────────────────┴──────────────────────────────────┘
  ⚠ You are not signed in: what you make is kept in THIS BROWSER only, and clearing site data
    deletes it. [Sign in] to keep it in your library.            ← swapped by /api/whoami
  Prefer the desktop app? Blockbench with the plugin runs the same Python on your machine and
  saves straight into your game: [the plugin] · [how it signs in to this site].
  ┌────────────────────────────────────────────────────────────────────────────────────────┐
  │                                                                                        │
  │                              the editor (fills the viewport)                           │
  │                                                                                        │
  └────────────────────────────────────────────────────────────────────────────────────────┘
```

At phone width (under 700 px) the frame is replaced by a notice: "The editor needs a screen at
least 700 px wide - Blockbench's own panels do not fit below that. Open it on a larger screen, or
[open it anyway]." The `?pack=` / `?piece=` deep links still forward.

**Decisions.**

- The page stays prerendered; the sign-in sentence is swapped by `editor-frame.js` after one
  `GET /api/whoami` (the same call the gallery's maintainer verbs make, Round 2). Without script
  the signed-out sentence stands, which is the safe one.
- The three steps are static prose with links: 2 → `/library/`, 3 → the wiki's packs page. They
  are the site's answer to "two contradictory publish paths"; the wiki pages `packs.md` and
  `editor.md` and `gallery/index.astro:147` are checked for any remaining mention of the issue
  path (Round 3 may have caught them).
- The frame's height is already the viewport minus chrome; the walk asserts it (`boundingBox().height
  >= 0.6 * viewport`) at 1280 so the review's "520 px in 800" cannot return.
- **The plugin (mod repo, `armorpieces.js`)** - R1: `LIBRARY_SITE = 'https://armorpieces.com/'`
  and `LIBRARY_INDEX = LIBRARY_SITE + 'library/index.json'` (the permanent URL). `LIBRARY_HOME`
  stays the repository, it is only ever shown. The `armorpieces_library` setting's description
  (`:6980`) names the site. *Sign in to the site…* when `siteOrigin()` is empty says "The *Armor
  Pieces library* setting does not name a site (armorpieces_library)." instead of "Could not start
  the sign-in".
- **Retire *Submit…*.** The library pack source's `publishLabel` becomes *Upload to your
  library…* and its `publish` is the existing upload (`:1358-1430`); `submitDialog` and
  `SUBMIT_TO` go; `armorpieces_api.submit` stays as an alias of the upload for one release so an
  older start page does not break, and `submissionUrl` is removed from the API surface. The
  reply after an upload gains the link: "In your library. Cut a version on its page and offer it
  from there: *site*/library/packs/*id*/#publish".
- **The start page (ArmorPiecesBlockbench `src/start.js`)**: the *Submit a pack…* tab (`:338`)
  and its listener (`:381-383`) become *Upload to your library…* calling the plugin's upload; the
  sentence at `:597` ("Your own pack goes in through its Submit…") follows.
- **"In this browser only", persistently.** A failed auto check-in is a three-second toast
  (`armorpieces.js` around `:2390`). The plugin records `notCheckedIn: true` on the piece's entry
  in the browser pack, and the start page's chips (`start.js:560`) draw "in this browser -
  not in your library yet" for it, until a check-in succeeds. Signed out, *New Armor Piece…*'s
  browser default (`:2620-2626`) gets one sentence in the dialog: "kept by this browser only".
- Order: plugin first (commit in the clone), then the bundle and `start.js` on ArmorPiecesBlockbench
  `main`, then the site page - the site's CI builds the editor from that main.

**Files.** Mod: `tools/blockbench_plugin/armorpieces.js`. Blockbench: `src/start.js`, the bundle.
Site: `src/pages/editor/index.astro`, `public/editor-frame.js`, `global.css`,
`content/wiki/editor.md` (the desktop sentence names the default).

**Test.** The walk: `/editor/` at 1280 has the three steps and a frame ≥ 60 % of the viewport; at
400 the frame is hidden and the notice shown; signed out the page says "this browser only", the
plain user's says their library. Blockbench's own tests (`ArmorPiecesBlockbench/test`) for the
start page's tab label. The plugin's default URL is asserted by grep in `tools/gate.py`'s tier 0
if there is a natural row; otherwise by the bundle's smoke test.

### 2.5 One place to manage a piece

**The screen.** A piece of your own has no page: its name is edited in one pack's table, its
publish button is on a collection's table, and a piece held only in a bag can be edited nowhere.
It gets a sheet, opened from *Edit* on every card the Pieces tab draws.

```
   ┌──────────────────────────────────────────────────────────────┐
   │  ← Reef crown                                          ↗  ✕  │
   │  ┌────────┐  coral:reef_crown · piece · crest                 │
   │  │  img   │  In: Coral (working list), Saved. Was: coral:crown│
   │  └────────┘  Published: waiting on review since 2026-09-12   │
   │                                                              │
   │  Name      [Reef crown            ]   ← makes a new object;  │
   │  Licence   [CC BY 4.0 ▾]                every pack and bag of │
   │  Author    [mattjes               ]     yours that held the  │
   │  Recipe    [x] template                 old one follows       │
   │  Former ids [coral:crown          ]                          │
   │                                          [Save]              │
   │                                                              │
   │  Publish                                                     │
   │  Waiting on review as a piece of its own. [Withdraw the offer]│
   │  – or – Not in the gallery. [Offer this piece to the gallery] │
   │  – or – In the gallery since …, in 3 packs. Taking it out of  │
   │  the gallery is a maintainer's verb: report it, or ask by     │
   │  email. [Turned down: <note>] [Offer it again]                │
   │                                                              │
   │  Download  [piece.zip]   Wear it   Add to a pack…            │
   └──────────────────────────────────────────────────────────────┘
```

**Decisions.**

- **Route `/library/pieces/<hash>/`**, owner only (a maintainer sees the same page read-only
  through the queue's link later; not this round), partial-capable, one component
  `OwnPieceDetail.astro`. The hash is the identity because an unpublished piece has no gallery
  page and an id is not unique across packs; the gallery page stays where it is for published
  ones and links here for the owner ("Yours: manage it").
- **Edits go through one new verb**, `PATCH /api/me/objects/:hash` with the `PieceEdit` shape,
  implemented by lifting `editPiece` out of its pack (`packverbs.ts:198`) into `objects.ts` as
  `editObject(owner, hash, edit)`: the credit part writes the column; the name / recipe /
  former-ids part makes the new object AND repoints every working list and every collection item
  of the owner's that held the old hash (a new `retarget(ownerId, oldHash, newHash)` in
  `collections.ts` + `packlists.ts`). A held-only-in-a-bag piece is editable at last, and the
  pack table's per-row edit calls the same function through its existing route so the two cannot
  disagree. Tags stay on the pack page - they are the pack's.
- **Publish / withdraw.** *Offer this piece* is `POST /api/me/objects/:hash/publish` (exists).
  *Withdraw the offer* is new and small: `DELETE /api/me/objects/:hash/publish` cancels a QUEUED
  object publication of the owner's (`publications` row → `cancelled`, the same word
  `cancelPackQueue` uses). An APPROVED piece is not withdrawn by its author here - it may be in
  other people's packs and outfits by hash, and the storage plan's takedown is the verb that hides
  it in the four places; the sheet says so and points at the report form. This is decision 2 of
  section 4.
- **"Reload to see it"** (`pack.js:109`, `collection.js:87`) becomes `UI.again()` on the picker's
  close - done in 2.2. *Copy in* and *Remove* already use it.
- The pack table keeps its inline fields (they are fast for a whole pack) and gains a *Manage…*
  link per row to the sheet; `PieceCards.astro:52`'s *Edit* points at the sheet instead of
  `/library/packs/<id>/#contents`.

**Files.** `src/pages/library/pieces/[hash].astro`, `src/components/OwnPieceDetail.astro`,
`src/pages/api/me/objects/[hash]/index.ts` (PATCH), `.../publish.ts` (DELETE), `src/lib/objects.ts`,
`src/lib/collections.ts`, `src/lib/packlists.ts`, `public/piece.js` (the sheet's verbs),
`PieceCards.astro`, `LibraryPackDetail.astro`.

**Test.** `objects.test.mjs`: PATCH the name of a piece held in two packs and a bag → one new
hash, all three point at it, the old object still exists (immutable, content-addressed);
credit-only PATCH → same hash; a stranger's PATCH → 404. `publish.test.mjs`: DELETE on a queued
object → cancelled and gone from the queue; DELETE on an approved one → 409 with the sentence.
The walk: the Pieces tab's *Edit* opens a sheet titled by the piece, Save works, Escape returns
focus to the card.

### 2.6 Versions

**The screen.** One idea of "new version" instead of two, and a Delete that asks.

```
  Cut a version
  From  (•) the working list - 14 pieces, changed since 1.0
        ( ) a zip  [Datapack ▾ file] [Resource pack ▾ file]  one zip with both halves in either box
  Label      [1.1        ]
  What changed
  [Three coral pieces, the reef crown recoloured.                                  ]
  [Save this as a version]     Same as the current version - cutting it makes a copy.
```

Versions table: a *What changed* column; *Delete* on an approved version of a public pack opens
the same dialog as the cut guard - "Version 2 is the one the gallery serves and 3 people have
downloaded it. Deleting it makes 1 current, which does not publish coral:reef_crown. Drop it
anyway?" - with the `breaks` list from `guard.ts` computed for (the version after deletion, the
deleted one).

**Decisions.**

- **`pack_versions.changelog text not null default ''`**: one additive migration. The label
  stays (it is the number people say); the changelog is what the public pack page shows under
  each version in the `versions[]` list Round 3 built, and what the queue's group shows the
  maintainer ("what the author says changed").
- The two forms (`LibraryPackDetail.astro:235-241` and `:322-329`) become one with a *From*
  radio; the zip half keeps the multipart route, the list half keeps the JSON one - the page picks
  the route by the radio, the server does not change shape.
- Cutting an unchanged list is allowed (a re-cut with a changelog is a legitimate thing) but the
  status line says it is a copy.
- `deleteVersion` (`packs.ts:222-232`) gains the guard: if the version was ever approved
  (`publications` has a row for it) it throws `BreakingVersion` unless `?force=1`, the same
  contract the cut uses, so `pack.js` reuses the cut's dialog code path. "Never the last" stays.

**Files.** `drizzle/` (migration), `schema.ts`, `LibraryPackDetail.astro`, `PackDetail.astro`
(shows the changelog), `admin/queue/index.astro`, `public/pack.js`, `packs.ts`, `versions.ts`,
`guard.ts` (a `breaksBetween(newer, older)` that the cut and the delete both call).

**Test.** `packs.test.mjs`: a cut with a changelog → the public page and `versions[]` carry it;
delete an approved current version → 409 with `breaks`, `?force=1` → gone and the previous is
current. The walk: the versions table shows the changelog text.

### 2.7 Previews, keyboard, weight

Small, independent, and every one of them is the kind a later round would keep postponing.

**Previews.**

- `Base.astro` gains `image?: string` and emits `og:title`, `og:description`, `og:image` (absolute,
  from `Astro.site`), `og:type`, `twitter:card = summary_large_image`, and `<link rel=canonical>`.
  A piece page passes its thumbnail, an outfit its render (`/wardrobe/<hash>.png`), a pack its
  first thumbnail, everything else `public/assets/card.png` - a 1200×630 card made once from a
  gallery shot by the same script as the heroes below.
- `public/robots.txt`: allow all; disallow `/api/`, `/account/`, `/library/`, `/admin/`, `/link/`,
  `/composed/`; `Sitemap: <site>/sitemap.xml`.
- `/sitemap.xml` is an ON-DEMAND route (no integration, no new dependency, the site's habit):
  the static page list (NAV, the legal pages, every wiki page from both content folders) plus
  every published piece, pack and public outfit from the catalogue and the sets table, cached
  five minutes like the catalogue.
- `/about/releases.atom`: an Atom feed from the changelog reader that already refuses Unreleased
  (`changelog.ts`), one entry per release with the GitHub link. Linked from `/about/#releases`
  and as `<link rel=alternate>` on that page.

**Keyboard.**

- **`inert`** instead of a focus trap: when the sheet or the dialog opens, every other child of
  `<body>` gets `inert` (the dialog over the sheet inerts the sheet's backdrop too), and it is
  removed on close. Supported by every browser the CSP already assumes; one attribute, no key
  handler, and the screen reader's virtual cursor is kept out as well, which a trap never did.
- **`aria-live="polite"`** on the status lines: `UI.mounted` sets it on every `[data-status]`,
  and `UI.status()` sets it before its first write on anything else it is handed (the second
  message is then announced; the first is the price of not sweeping thirty templates).
- The ten `role="tab"` anchors (`gallery/index.astro:78-80`, `LibraryBody.astro:132, 166`, the
  wardrobe's, the account's) lose `role`, `role="tablist"` and `aria-selected` and keep
  `aria-current`: they are links that reload a view, and the role promised arrow keys they do not
  have. The `.view-toggle` look is CSS, untouched.
- The slider (`slider.js`) gets a visible **pause** button after the dots (`aria-pressed`),
  which also stops the auto-advance for good in that page view; the caption drawn over the
  arrows (the review's first line) moves under the picture.

**Weight.**

- `scripts/images.mjs`: Playwright's Chromium as the encoder, since it is already here and nothing
  else is - opens each source PNG in a page, draws it on a canvas, `toBlob('image/webp', 0.82)`
  (and JPEG for the heroes), writes beside the source. Run for `public/assets/gallery/*.png` (the
  five heroes, 1.75 MB → about 400 KB) and for the thumbnail folders at build.
- `/gallery/thumbs/[file].ts` answers `.webp` beside `.png`; `PieceCards.astro` and
  `PieceDetail.astro` draw `<picture>` with a WebP source and the PNG fallback. The renderer
  (`thumbnails.mjs`) writes both from now on, with the same canvas trick in the page it already
  drives.
- Pagefind on focus: `Wiki.astro:65-66` renders a plain `<input type=search>` and loads
  `pagefind-ui.js` + its CSS on the first focus or click, then mounts `PagefindUI` and hands it
  the typed text. 134 KB less on every wiki page, and the walk's "typing skin yields a result"
  still holds because Playwright's `fill` focuses first.

**Files.** `Base.astro`, the three detail routes, `public/robots.txt`, `src/pages/sitemap.xml.ts`,
`src/pages/about/releases.atom.ts` (`about.astro` moves to `about/index.astro`), `overlay.js`,
`ui.js`, five templates for `role=tab`, `slider.js`, `index.astro`, `scripts/images.mjs`,
`scripts/thumbnails.mjs`, `thumbs/[file].ts`, `PieceCards.astro`, `PieceDetail.astro`,
`Wiki.astro`, `wiki-search.js`, `package.json` (`images` script, in `build`).

**Test.** `site.test.mjs`: a piece page's HTML has `og:image` with an absolute URL and a canonical;
`/robots.txt` 200; `/sitemap.xml` is XML that names the piece and the outfit the suite created;
`/about/releases.atom` parses and has 0.3.0. The walk: with the sheet open, `main` has `inert`;
after close it does not; Tab from the sheet's Close button lands inside the sheet; the slider has
a button named Pause; no `role="tab"` anywhere; the gallery's first `<img>` has a `<picture>`
parent with a `image/webp` source; the wiki page loads no `pagefind-ui.js` before focus and does
after.

### 2.8 Wiki content

The reader's chapter listed five questions the FAQ does not answer and one section the getting
started page lacks. All of it is Markdown in the site repo except `authoring.md`, which is the
mod's (`docs/authoring.md`, synced).

- `content/wiki/getting-started.md`: a section **Installing a pack** between Installing and
  Applying a piece - the zip from the gallery is both halves in one file; where it goes
  (`datapacks/` of the world AND `resourcepacks/`, or the one zip in both); **reopen the world**,
  not `/reload`, because the pieces are read at world load (`save-compatibility.md`; the game's
  own message at `en_us.json:214` says so and no wiki page did).
- `content/wiki/faq.md`, five entries: *Which version of the mod does a pack need?* (the pack's
  page and its `pack.mcmeta` say; today every pack needs 0.4.0); *Why is a piece missing from the
  public zip?* (it is reserved, or under review; the pack's page lists what it left out); *Where
  did my upload go?* (your library, Packs; the pack page has Cut a version and Publish); *Do I
  need an account to download?* (no; an account is for keeping and publishing); *I installed a
  pack and nothing shows* (reopen the world).
- `content/wiki/changelog.md` stops being a 435-line copy of the release notes: the sync's second
  `CHANGELOG.md` line (`scripts/sync.mjs:50`) goes, the page becomes six lines that point at
  `/about/#releases` and the feed, and the wiki search stops indexing every release twice. The
  first sync line (`content/mod/CHANGELOG.md`, what `/about/` renders) stays.
- A community link: `SITE_COMMUNITY_URL` in `site.ts`, rendered in the footer and in the FAQ's
  last entry when set, and nowhere when not - the Discord server does not exist yet
  (`discord-repo.md`), and a link to nothing is worse than none.
- Mod: `docs/authoring.md` is fine (one h1 since Round 0). Nothing to do there unless the
  installing section wants a sentence from it.

**Files.** Three Markdown pages, `scripts/sync.mjs`, `src/lib/site.ts`, `Base.astro`, `faq.md`.

**Test.** `site.test.mjs`: getting-started has an "Installing a pack" heading containing "reopen";
faq has the five headings; changelog page under 30 lines; the footer has no community link
without the env and has one with it.

## 3. The walk as a test, this round

`test/pages.test.mjs` gains, in the fixed-list pass: the five error URLs assert HTML + nav + a
link (the comment at `:115` says this is where); `/editor/` at both widths; `/sitemap.xml`,
`/robots.txt` and the feed as three more rows with their content types. The scenario tests gain
the eight named above, one per item. Every one is a few assertions over a page the walk already
visits, so the budget - under a minute in the suite - holds; the picker and the sheet-inert tests
are the only ones that open a dialog and they reuse the existing helpers.

## 4. Decisions for the user, with a recommendation each

1. **Branch off `ux-3` now, or merge #7 first?** Recommend merging #7 now and branching off
   `main`: Round 3 is green, its push run deploys it, and the stack stays one deep. If the user
   prefers to see Round 4 before anything more deploys, stack.
2. **May an author withdraw an APPROVED piece?** Recommend no, this round: it can be in other
   people's packs and outfits by hash; the sheet says so and offers the report route; a maintainer's
   takedown is the verb that hides it in the four places (`storage-plan-built.md`). Cancelling a
   QUEUED offer is built. Alternative: an owner takedown reusing the maintainer's standing with the
   actor recorded - a second session's work once the other seven items are in.
3. **WebP thumbnails through Chromium, or leave PNG?** Recommend build it: it is one script over a
   dependency the site already pays for, and the gallery's 2.7 MB of lazy PNGs is the review's only
   weight finding that is not the editor. Alternative: skip 2.7's weight bullets and ship the rest.
4. **Retire *Submit…* outright, or keep the issue path as a second door?** Recommend outright (as
   the rounds plan proposed): two doors with different rules is the review's chapter, and the
   library index's `submit` field then means nothing. The mod's own `SUBMIT_TO = 'mod'` case ("take
   this pack into Armor Pieces itself") had no real flow behind it either.
5. **Should the Pieces-tab *Edit* open the sheet, or keep going to the pack page?** Recommend the
   sheet; the pack page keeps its inline table for bulk work and gains *Manage…* per row.

## 5. Order

2.1 error pages first: smallest, and the walk's error rows turn green. Then 2.2 the picker and
2.3 the outfit page - the two visitor-facing screens, each half a day. 2.4 next because it spans
three repositories and the site half waits on the bundle. 2.5 and 2.6 are the author's day. 2.7
and 2.8 last, each bullet independent, so a half-finished 2.7 still merges. Strike R1 and R28 (and
R27, already built) through in the review with the commit hash; re-read the friction sections
against each item's "kept" list and note in the review what is kept on purpose (the slugs, the
UUID pack URLs, "shelf", the 28 gemstone options - each a sentence, not a fix).

Done when: `npm test` green, the walk green at both widths and under `WALK_WIDE_FONTS=1`, R1 and
R28 struck through, PR opened, and the plugin's new default committed in the clone so the next
desktop install signs in against a site that exists.

## 6. As built (2026-09-14)

Every item landed as planned; the differences are the ones a build finds.

- **2.1** `notFound()` in `lib/error.ts` is the one place the empty 404 is made, with the reason
  written on it; the file routes keep their sentences. `500.astro` is prerendered like the 404
  and read off disk by the adapter. The sheet's notice carries `data-sheet-gone="<status>"` for
  the walk.
- **2.2** An `async` `onPick` returns a Promise, and `keep !== false` read that as "close" - the
  close fired `UI.again`, which reloaded the page before the POST landed. The pick now awaits
  what `onPick` resolves to. `UI.dialog` gained `wide`; the picker's own Escape listener went.
- **2.3** `UI.copy` and `UI.slug` are the one copy of what the dressing room did on its own;
  `[data-copy]` buttons are bound by `ui.js` itself, so any page or layer can draw one.
- **2.4** The plugin lives in the MOD repository, and the working copy's `armorpieces.js` also
  carried the other session's uncommitted additive-packs hunks - so the Round 4 edits were
  applied to the CLONE's copy by script (`plugin_r4.py`, twelve replacements and one removal,
  each asserted to match once) and committed alone; the bundle was rebuilt from the clone.
  `make_plugin.mjs`'s `base` default was the Pages URL too, and now names `/editor/app/` on the
  site. `armorpieces_api.submit` is the upload under its old name; `submissionUrl` is gone and
  the browser test asserts the new surface. The "in this browser only" sentence is conditioned
  on `isApp`. The plugin's `pending` mark is read by the start page onto the LIBRARY's card,
  since a checkout is one card, the library's.
- **2.5** `editPiece` is split into `editObject` (credit column; new object) and the new
  `editHeldObject`, which repoints every own pack list and bag; the pack table's row calls the
  same function as before through its own route. The old object stays the owner's (objects are
  immutable and never deleted): its sheet says "In none of your packs or collections". Withdraw
  cancels only a row filed with no `groupId`; one filed with a pack says so.
- **2.6** Migration `0017_changelog.sql`, additive. `breaksBetween(newer, older)` in `guard.ts`
  reuses `breakingChanges` over two cut versions; the delete guard fires only for the CURRENT
  version of a pack that is not private. The public pack page shows the current version's
  changelog above the "Earlier versions" table, which only appears with two approved versions.
- **2.7** `inert` is not a trap: Tab past the sheet's last control goes to the browser's chrome
  (the body, as the document sees it), never to the page - the walk asserts that, not "stays
  inside". A `<picture>` whose WebP 404s shows nothing, so `lib/images.ts` answers a WebP only
  where the file exists (data dir for rendered thumbs, `dist/client` then `public` for the
  bundle's), and `scripts/images.mjs` runs first in `npm run build` (idempotent by mtime; 110
  files in 41 s cold, nothing warm). The heroes and the card are gitignored with their sources.
  The Atom feed's dates come from `content/mod/release-dates.json`, which `sync.mjs` writes
  when it has a token; without one the build's date stands in. `about.astro` moved to
  `about/index.astro` to host the feed beside it.
- **2.8** The changelog wiki page is generated by `sync.mjs` and gitignored; `changelogPage`
  now writes the pointer page, and the local copy was regenerated by calling that function
  alone rather than running the sync from the working copy.

**Traps for the next round:** a Python `io.open(..., 'w')` without `newline=''` writes CRLF
into the LF site (`git checkout -- .` after committing restores git's line endings); long bash
heredocs die and short ones mangle backslash escapes - write scripts with the Write tool and run
them by path; a Playwright script started on a fixed port can hit a lingering server (4399
answered a bare 500 that was not the site's); `RATE_LIMIT_SCALE=10` is needed by any suite
that makes more than a handful of packs, `publish.test.mjs` now sets it; the API calls a
pack's current version `current`, not `currentVersionId`.
