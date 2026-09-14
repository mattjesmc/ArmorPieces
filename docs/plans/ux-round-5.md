# Plan: UX round 5 — the editor's own front

> **Status (2026-09-14): PROPOSED, nothing built.** Written the evening the five rounds of
> `docs/plans/ux-rounds.md` were merged and deployed (ArmorPiecesSite `5a6ed9f`), when the user
> opened the editor and found what the review had not looked at: the plugin's own front. Read
> against the mod working copy (`tools/blockbench_plugin/armorpieces.js`, 7579 lines),
> ArmorPiecesBlockbench `main` (`src/start.js`, 800 lines) and ArmorPiecesSite `main`
> (`LibraryBody.astro`, `editor/index.astro`, `public/pack.js`). Every line number is from those
> and is re-verified at fix time. The screenshots that ground section 1 are in the session's
> scratch (`r5/*.png`), not the repository.

The review of 2026-09-12 (`docs/reviews/site-ux-2026-09-12.md`) read the plugin's SOURCE for the
piece pipeline and the publish flows - that is where R1 (the dead sign-in URL) and the two
contradictory publish paths came from - and said in its "Not reviewed" paragraph that "the
Blockbench plugin's modelling and painting surface itself" was out of scope. What fell between the
two is the plugin's FRONT: the start page the web editor opens on, the Tools menu the desktop one
hides everything in, the four dialogs behind them, and the road between a pack here and a pack on
the site. Nobody walked it as a visitor. This round does, and the findings are section 1.

The round is the same shape as Round 4: design work, screens decided before a file is touched,
and three repositories in a fixed order. It is NOT a redesign of the modelling surface - the panel,
the sheets, the check - which is the bridge's and the gate's, and works.

## 0. How to run this

- **Three repositories, in order, as Round 4 item 2.4 did.** The plugin first
  (`tools/blockbench_plugin/armorpieces.js` in the MOD, edited in the working copy, committed
  through the clone - `armorpieces-two-repos.md`; the working copy's plugin may carry another
  session's hunks, so apply by script and diff the clone), then the editor bundle
  (ArmorPiecesBlockbench: `src/start.js`, and `web/armorpieces.js` rebuilt from the clone -
  `bundle-from-the-clone.md`; committed on `main` because the site's CI builds the editor from
  there), then the site (branch `ux-5`, one PR). A plugin change reaches the site only through the
  bundle, so the order is not a preference.
- **Two plugins, one file.** The desktop and the web run the SAME `armorpieces.js`; `isApp`
  branches the platform. `start.js` is site-only by design (its header: loading the plugin into
  somebody else's Blockbench "leaves their start screen exactly as it was"). So a verb that must
  exist on both fronts is written once in the plugin and DRAWN twice: as a card or button on the
  web start page, and as a start-screen section on the desktop (item 2.5).
- **The gates.** The mod's `tools/gate.py` tier 0 for the plugin (it loads the file); the editor
  repo's browser test (`bundle-from-the-clone.md`, it asserts `armorpieces_api`'s surface); the
  site's `npm test` detached plus the walk under `WALK_WIDE_FONTS=1`. Section 3 says what each
  gains. A change to the start page is looked at in Chromium against the built bundle
  (the recipe: Playwright from the site repo against `/editor/app/`, wait for
  `#ap_start .card`, screenshot; the session's `r5shots.mjs` did it), not imagined.
- **Traps carried forward.** The plugin has no `process` global and an eval-loaded copy hides
  that (`blockbench-source-extract.md`); a file-loaded plugin never reaches a second window
  (`blockbench-second-window-plugins.md`); Round 4's `plugin_r4.py` pattern (assert each
  replacement matches once) is how the plugin is edited safely; the site's `/editor/` page is
  prerendered and forwards `?pack=`, `?piece=`, `?view=` by script (`editor-frame.js`), so a new
  query key is added THERE too or it never reaches the frame.

## 1. What a visitor finds (verified 2026-09-14)

Walked signed out on the live `/editor/app/` at 1280 px, then read in source. **[live]** seen
on the page, **[src]** verified in source.

1. **There is no way to make a piece that a visitor can see.** [live] The start page's bar is
   *your pieces · N in the library · search · Upload to your library… · Use my game…*, and the
   only *New Armor Piece…* is `Tools › Armor Pieces › New Armor Piece…` (`armorpieces.js:7028`).
   [src] The site's Library › Pieces tab has filters and cards and no *New piece* - the Packs tab
   next to it has *New pack* (`LibraryBody.astro:174-176, 289-300`). The site's *Make a piece*
   page (Round 4 item 2.4) says "Make → Pack → Offer" above a frame whose first step is hidden in
   a menu. The desktop plugin adds nothing to Blockbench's start screen at all: the new user sees
   Blockbench's own formats (Bedrock Entity, Minecraft Skin…) and has to know the plugin is under
   Tools.
2. **A signed-out visitor's first piece lands in the pack that resets.** [live] *New Armor Piece*
   offers one *Where*: `In this browser: src/main/resources` - the example pack, which the page
   itself says "resets". [src] `newPieceTargets` (`:2559`) lists every `searchRoots()` folder and
   the example pack is one; `newPieceDialog` (`:2576-2580`) defaults the namespace to
   `armorpieces` because the pack is "in the repo". So the first thing a visitor makes is an
   `armorpieces:` piece in a folder the next bundle overwrites, and nothing says so until it is
   gone. There is no *+ New pack…* in that dialog; the pack has to be made first, elsewhere.
3. **The filters look like the tabs.** [live] `in this browser · any kind · any socket` are
   `<select class="tab">` (`start.js:445-461, 469-471`) - the same box, border and colour as the
   `your pieces` tab beside them and the `by socket` toggle after them; nothing says three of the
   five are menus. Blockbench's own `select` chrome is overridden by the page's `.tab` rule, so
   the native chevron is gone too.
4. **Packs have no front.** [live] Nothing on the start page lists packs. *Upload to your
   library…* in the bar opens the *Packs…* manager (`start.js:338-342`), which surprises: the
   button says upload, the dialog says every folder. [live] The manager itself
   (`PACKS_DIALOG_TEMPLATE`, `:2813-2853`) puts SEVEN buttons under each pack - *Work here ·
   Import zip… · From the library… · From your library… · Link a folder… · Export zip… · Upload to
   your library…* - and five *New pack from…* buttons under the list, so the two verbs a visitor
   wants (open one of my packs; make a new one) are the fourth and the eighth button, and "From
   your library…" under a pack means "install INTO this pack", not "open". Opening one of YOUR
   site packs is `New pack from your library…` → pick → and it arrives as `site-<id>` with no
   name on the card and no memory of where it came from (see 6).
5. **The library tab installs, it never opens.** [live] The library view's one card is the mod's
   own pack (0.3.0, "ships with the mod"); clicking it installs a copy into `/packs/<id>`. There is
   no *Open* for a pack you hold on the site, and the site's own packs (the ones under *your
   library*) are not on this tab - they are behind the manager (4).
6. **The road back to the site is half built.** [src] `openDraft` (`:7383-7404`) imports a site
   pack's working copy into `packs/site-<id8>`, adds it to the user's list and scopes to it - and
   writes NO marker saying which pack it is the working copy of. `saveDraft` (`:7405`) exists and
   is called from ONE place: the site's pack page around the embedded frame (`public/pack.js:191`).
   From `/editor/?pack=<id>` - which is where *Edit in the editor* on the Library › Packs tab goes
   (`LibraryBody.astro:196`) and where *Full screen* goes - there is no *Save to the working copy*
   at all: the author edits, saves the piece locally, and has to know to open *Packs… › Upload to
   your library… › The working copy of X*. A piece checked out by hash is different and works
   (`checkinAfterSave`, `:2373`): the difference is invisible to the author.
7. **The upload answers with a URL in a toast.** [src] `publishToAccount` (`:1362-1368`) ends in
   `done('Uploaded: X. Cut a version on its page and offer it from there: https://…/#publish')`,
   shown by `Blockbench.showQuickMessage(report, 3000)` - three seconds of an address nobody can
   click. The upload dialog asks for a slug, a visibility and a version label in one form for
   three different targets, with the description "For a new pack" on two of them.
8. **The desktop's *Open Armor Piece…* is a `<select>` of every piece** (`pickPiece`, `:2170-2190`),
   66 entries in one native menu, no socket, no pack, no search; the web start page draws the
   same list as cards by socket. [src]
9. **The intro is two paragraphs and two notes before the first control** [live]: what Pyodide
   is, what the figure wears and why Mojang's textures are not served, then the sign-in note. The
   page's first verb is 430 px down at 1280 px.

What works and stays: the card list by socket with thumbnails for the account's pieces; the
checkout-by-hash round trip (open a library piece → edit → save → checked in); *Use my game…*;
the device-flow sign-in on the desktop; the pack sources as a list (`registerPackSource`) that
this round adds to rather than replaces; the `Packs…` manager's forget/delete distinction.

## 2. The items

### 2.1 Make a piece, from every front

**Screen (web start page, signed out and in):**

```
Armor Pieces in Blockbench                      [ + New piece ]  [ Use my game… ]
one sentence · Pick a piece to open it on the figure; make a new one; a pack is what you ship.

[ Pieces ] [ Packs ] [ Library ]     ( search…                          )
Where ▾  Kind ▾  Socket ▾  Pack ▾                                [x] by socket
```

- `+ New piece` is the page's one primary button, in the header, on every view. It calls
  `BarItems.armorpieces_new.click()` - the plugin's own dialog (2.2 fixes it), so desktop and web
  ask the same questions.
- The empty states get it too: "Nothing in your library yet. *Make a piece*, or save one from
  the gallery."
- **Site, Library › Pieces tab:** a `New piece` button beside the filters (`LibraryBody.astro:
  289`), `href="/editor/?new=piece"`; on the Packs tab each own pack's card gains `New piece in
  it` → `/editor/?pack=<id>&new=piece`. `editor-frame.js` forwards `new`; `start.js`'s `wanted()`
  reads it and, after `openDraft` when a pack was named, clicks the action. The *Make a piece*
  page's "Make" line links the button rather than describing a menu.
- **Desktop:** item 2.5.

Files: `start.js` (bar, empty states, `wanted`), `LibraryBody.astro`, `editor-frame.js`,
`editor/index.astro`. Test: the editor repo's browser test clicks the button and asserts the
dialog `#armorpieces_new` is shown; the walk asserts the Pieces tab has a control whose href
contains `new=piece`.

### 2.2 The New Armor Piece dialog knows where a piece can live

```
New Armor Piece
Name        [ gorget            ]
Where       [ ▾ + New pack in this browser…        ]   ← default when no pack of yours exists
            |   Pack: Reef (your library)           |
            |   Collection: Helmets (your library)  |
            |   In this browser: my_pack            |
            |   (the example pack is not offered)   |
Anchor      [ ▾ crest (head)                        ]
Namespace   [ my_pack ]   from the pack; editable
```

- The example pack (`repoRoot()`'s `src/main/resources`, and any pack the bundle unpacked) is
  not a destination: `newPieceTargets` skips roots that are not `userPacks()` on the web. On the
  desktop the repository's own pack stays offered - that is how the mod's pieces are authored -
  but is labelled *the mod's own pack* and is not the default when a user pack exists.
- `+ New pack in this browser…` as a target, the way `+ New collection…` already is: `newPack`
  runs first, then `makeNewPiece` into it. Default target: a pack of yours on the site if signed
  in; else the scoped local pack; else *+ New pack…*.
- Namespace defaults from the chosen pack (its `pack.mcmeta` description or folder name,
  slugged), `armorpieces` only for the mod's own pack, and follows the *Where* select until
  edited.
- Name first, Where second, Anchor third: the two things a visitor knows, then the one they
  learn.

Files: `armorpieces.js` `newPiece`, `newPieceTargets`, `newPieceDialog` (`:2533-2640`),
`newPack` (`:3007`, gains a callback with the folder - it has one already: `done(dir)`). Test:
tier 0's plugin load; a browser test that opens the dialog signed out and asserts the example
pack is absent from the options and the first option is *+ New pack*.

### 2.3 Filters that look like filters, tabs that look like tabs

- The three views are a segmented control (`role=tablist`, `aria-selected`), the filters are
  `<select>`s with a label prefix and a chevron - `Where: in this browser ▾` - drawn with one
  `.filter` class: Blockbench's `--color-back` field, `--color-border`, a 10 px SVG chevron as
  `background-image`, `padding-right` for it; `by socket` becomes a checkbox-styled toggle
  (`aria-pressed`) at the row's end. No `.tab` on a `select` anywhere.
- The site's own `.filters select` (`global.css`) is the reference look, translated to
  Blockbench's variables, so the two lists read as one product.
- The intro shrinks to one sentence and the two notes become one line each with a *more*
  disclosure (`<details>`): what the figure wears is an aside, not a preface (finding 9).

Files: `start.js` CSS block and `drawFilters`. Test: the browser test asserts every
`#ap_start select` has class `filter` and none has `tab`; a screenshot for the eye.

### 2.4 Packs on the front, and the road to the site

**Screen (the Packs view):**

```
[ Pieces ] [ Packs ] [ Library ]                                   [ + New pack ]

YOUR LIBRARY (on the site)                          signed in as mattjes · Sign out
┌ Reef ───────────────────── public · 4 pieces ┐  ┌ Chitin ────────── private · 12 pieces ┐
│ working copy is here (2 edits not saved up)  │  │ not opened here                        │
│ [ Open ] [ New piece in it ] [ Save to site ]│  │ [ Open ]                              │
│ Its page on the site ↗  (cut a version there)│  │ Its page on the site ↗                 │
└──────────────────────────────────────────────┘  └────────────────────────────────────────┘

IN THIS BROWSER
┌ my_pack ─────── datapack + resource pack · 3 pieces ┐  ┌ Armor Pieces (example) ── resets ┐
│ [ Open ] [ New piece in it ] [ Upload to your library… ] [ Export zip ] [ ⋯ ]            │
└─────────────────────────────────────────────────────┘  └───────────────────────────────────┘

[ + New pack ]  [ Import a zip… ]  [ From the library… ]                 signed out: Sign in ↗
```

- **One card per pack, two sections.** *Your library* is `GET /api/me/packs` (id, name,
  visibility, counts - `LibraryBody` already reads them); *In this browser* is `searchRoots()`
  through `packInfo`. A site pack whose working copy is open here is ONE card (by the marker
  below), with the state on it.
- **The marker.** `openDraft` writes `.armorpieces-draft.json` `{packId, name, openedAt}` into
  the folder, the way a checkout writes `.armorpieces-checkout.json`; `packInfo` reads it and
  the card says *working copy of Reef*. That is what makes *Save to site* possible from
  `/editor/?pack=`, not only from the embedded page.
- **Save to site** is `saveDraft` with the marked id - the plugin gains `draftOf(dir)` and a
  `Save Working Copy to Site` action (`condition: draftOf(scope)`), which the site's
  `pack.js` button can call too instead of carrying its own. Saving a PIECE in a marked pack
  offers the same automatic push `checkinAfterSave` gives a checkout, under the same setting
  (`armorpieces_checkin`), debounced the same way; a failure marks the folder pending and the
  card says *2 edits not saved up* (finding 6).
- **Open** on a site pack is `openDraft` (idempotent, `:7387`); on a local pack it is `workIn`.
  **New piece in it** is 2.1's action with the pack preselected. **Export zip** is the zip
  source's publish. **Upload to your library…** is 2.6's dialog with the pack given. The
  overflow `⋯` holds *Link a folder…* (desktop), *Import a zip into it*, *Forget* / *Delete*.
- **The bar's *Upload to your library…* goes**; the Packs view is where uploading lives. The
  `Packs…` dialog stays as the desktop's manager and as the web's, redrawn as the same cards
  (2.6): one template, mounted in a dialog on the desktop and inline on the start page.
- **Library view:** each entry keeps *Install*; an entry of YOURS (own, from `myLibraryIndex`
  when signed in) says *yours - open it under Packs* instead of installing a second copy.

Files: `armorpieces.js` (`openDraft`, `packInfo`, new `draftOf`, `saveDraftNow`, the action;
`publishToAccount` for the given-pack call), `start.js` (the view, `readPacks`), site `pack.js`
(call the plugin's action). Test: browser test - open a draft by id against the test server,
assert the marker and the card's *working copy of*; save a piece, assert `PUT …/draft` was
called once (the mock records it).

### 2.5 The desktop's start screen

```
┌─ 🛡 Armor Pieces ─────────────────────────────────────────────────────────────┐
│ Pieces for the Armor Pieces mod: open one on the player rig, or make one.     │
│ [ New piece… ] [ Open piece… ] [ Packs… ] [ Open skin… ]      Signed in as … │
└───────────────────────────────────────────────────────────────────────────────┘
```

- `addStartScreenSection(ID, {graphic: {type: 'icon', icon: 'shield'}, text: [{type:'h2'},
  {type:'p'}, four `{type:'button', click}`], closable: false})` on load, removed on unload
  (`section.delete()`), `isApp` only - the web has its own page. Verified in Blockbench 5.1's
  `js/interface/start_screen.js:41` (`window.addStartScreenSection`).
- *Open piece…* becomes a `Dialog` with the SAME card list the web draws - search, socket
  groups, pack chips - rendered from the plugin (`pickPiece` gains a component; the `<select>`
  stays as the fallback when the list is under eight). This is the one place `start.js`'s card
  code moves INTO the plugin, so the desktop is not a second, worse list (finding 8).

Files: `armorpieces.js` (`onload`/`onunload`, `pickPiece`). Test: tier 0 load; a `risky_eval`
in the running Blockbench that the section exists and its buttons are the four actions.

### 2.6 One pack manager, and an upload that ends somewhere

- The `Packs…` dialog draws 2.4's cards (one template constant, `PACK_CARDS_TEMPLATE`, used by
  the dialog's Vue component and by `start.js` through `armorpieces_api.packCards()` - or the
  start page mounts the same Vue component; decide at build, section 4).
- **Upload to your library…** becomes three buttons on the card, not one form with a select:
  *Save to site* (the working copy - only on a marked pack), *Upload as a new pack…* (name,
  slug, visibility), *Upload as a new version…* (label, changelog - Round 4 item 2.6's field,
  `x-pack-changelog`). Each ends in a `Dialog` with the result and **a button that opens the
  pack's page** (`Blockbench.openLink(origin + '/library/packs/<id>/#publish')`), not a
  three-second toast with an address in it (finding 7).
- The "what next" sentence is the site's: *Cut a version on its page and offer it to the gallery
  from there.* The editor never publishes; the plan keeps that (Round 4, decision: one road).

Files: `armorpieces.js` (`PACKS_DIALOG_TEMPLATE`, `publishToAccount`, `packsDialog`). Test:
browser test - upload a new pack against the test server, assert the result dialog names the
pack and its link.

### 2.7 The wiki says it

- `wiki/editor.md`: the start page's three views, *New piece* on both fronts, what "working copy
  of" means and that *Save to site* is the way back; the desktop section names the start-screen
  section instead of the Tools menu. `authoring.md` (mod) where it says `Tools > Armor Pieces >
  New Armor Piece...`: "or the *New piece* button on the start screen".

## 3. The tests, this round

- **Editor repo browser test** (`bundle-from-the-clone.md`) gains: the start page has one
  `[data-new-piece]` and it opens `#armorpieces_new`; every `#ap_start select` is `.filter`;
  the Packs view lists the example pack as *resets* and a user pack with *Open*; `?new=piece`
  opens the dialog; `?pack=<id>` leaves a `.armorpieces-draft.json` in the folder and a card
  saying *working copy of*.
- **Mod tier 0** loads the plugin as before; a `risky_eval` check of the start-screen section is
  manual (the gate has no Blockbench).
- **Site walk**: `/library/?view=pieces` has `a[href*="new=piece"]`; a pack card has `New piece
  in it`; `/editor/?new=piece` forwards the key (assert the frame's `src`).

## 4. Decisions for the user, with a recommendation each

1. **Move the card list into the plugin (2.5), or keep the desktop on dialogs?** Recommend
   move: one list, two hosts; `start.js` shrinks to the page around it. Cost: a day; the web
   page's card code becomes plugin code, which every desktop user then also gets.
2. **Should the example pack be a destination at all on the web?** Recommend no (2.2): it
   resets. On the desktop it is the mod's own pack and stays.
3. **Auto-push a marked working copy on piece save (2.4), under the existing `armorpieces_checkin`
   setting?** Recommend yes - it is what the checkout already does, and the card shows what did
   not go up. Alternative: manual *Save to site* only, and the card counts unsaved edits.
4. **Three upload buttons (2.6) or the one form?** Recommend three: the form's "for a new pack"
   descriptions on fields that apply to one target of three is the tell.
5. **Order and split.** Recommend one branch per repository, plugin first, and the site PR last;
   2.1-2.4 and 2.6 are one session on the plugin + bundle, 2.5 a second, 2.7 and the site's
   buttons ride with the site PR. Or, smaller: 2.1 + 2.2 + 2.3 alone first (a visitor can make a
   piece and read the page), 2.4-2.6 after.

## 5. Order

2.2 (the dialog) → 2.1 (its buttons, web + site) → 2.3 (the page's look) → 2.4 (packs + marker +
save to site) → 2.6 (manager + upload) → 2.5 (desktop) → 2.7 (wiki). Each step leaves the bundle
buildable and the browser test green; the site PR opens after 2.4 lands in the bundle, because
`New piece in it` needs `?new=` in the frame.
