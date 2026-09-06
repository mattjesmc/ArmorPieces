# Plan: the content platform — gallery, library, wardrobe, packs

`docs/plans/website.md` got the site built: Astro + node behind `server.mjs` on the VPS, accounts,
hosted and linked packs, the gallery, the composer, the real editor at `/editor/`. That plan treated
the site as a *place the mod is described and its packs are downloaded*. This one turns it into what
it is actually for: **the content pipeline around the mod** — where pieces are found, kept, worn,
assembled into a pack of exactly what someone wants, and published back for the next person.

The end goal, in one loop:

> Browse everything published in the **gallery**. Keep what you like in **your library**. Dress a
> figure in the **wardrobe** and save the set. Build **your own pack** out of the pieces you
> actually want — yours, and other people's you are allowed to use. Publish it, and it is in the
> gallery for the next person. Install your library, or a chosen set of packs, into the game.

Everything below is in service of that loop. Five things are wanted, in the order they block each
other:

0. **The account page is one wall.** Everything a signed-in person can do is stacked on
   `/account/`: the display name, the pack table, the upload form, the GitHub App, the Drive grant,
   the devices, the export and the deletion. Eight `<h2>`s, one 273-line script, no division. It
   should be three pages — **profile**, **connectors**, **account** — and the pack half should not
   be on any of them.
1. **"Library" means the wrong thing.** Today `/library/` is the *curated public index* the editor
   installs from, and "your library" is a heading on the account page. It should be the other way
   round: the **gallery** is everything published, the **library** is your personal selection out of
   it. Nothing in the codebase has this shape yet, and everything in 2-4 hangs off it.
2. **A wardrobe.** There is no way to see a whole set before you own it, and no way to keep one.
   `wardrobe.png` on the home page is a screenshot of `/armorpieces stage random`; the word means
   nothing on the site yet. A visitor should dress a figure, look at it, save the set, and be handed
   the commands and the pack that make it real.
3. **A pack cannot be authored on the site.** `packs.ts` has no verb smaller than a version. Editing
   means leaving for `/editor/`, which owns the whole viewport and keeps its work in one browser's
   IndexedDB. Copying a piece into a pack of your own, duplicating one, moving one between packs,
   choosing what a pack contains — all things the site could do better than Blockbench and currently
   cannot do at all. This is the half of the loop that makes the rest worth having.
4. **The same facts are written down four times.** "Ninety-one pieces" is in `modpage.yml` twice, in
   `content/wiki/pieces.md`, in `library.json`'s description and in the `CHANGELOG`. The socket list
   is prose in `modpage.yml:48`, a table in `content/wiki/pieces.md:11-24`, and a hardcoded array in
   `ArmorPiecesSite/src/lib/library.ts:78-84`. Every release these drift, and every release
   something has to be trusted to find all of them.

---

## The shape

Five nouns. Getting these right is most of the work; the pages follow from them.

**Piece** — the unit of authorship: a piece, a skin or a cloth. It is *authored inside a pack* and
identified by its namespaced id, so a piece is always `(pack, version, id)`. It carries a license
and an author, and those travel with it everywhere.

**Pack** — the unit the *game* loads. The only thing installable. Two kinds in a library: **authored**
(yours — a draft, versions, publishable) and **saved** (someone else's published pack, kept on your
shelf as a reference to a version, not a copy).

**Library** — one per user: your personal selection. It holds saved packs, saved pieces and your
sets. A saved piece is a **bookmark**, not a copy: a row naming `(pack, piece)`. This matters twice
over —

- it costs nothing, so a library can hold a thousand pieces against a 200 MB quota that only your
  own authored packs draw on;
- **an all-rights-reserved piece can be bookmarked and worn but never copied.** Bookmarking is
  looking; copying is publishing. `pick_pieces.py` already refuses an ARR entry without `--own`, and
  routing the *copy* verb through it means the platform's licensing is enforced by the same code the
  command line uses, not by a second rule written in TypeScript.

**Set** (the wardrobe's unit) — a named outfit: per socket a piece with its material and its
fittings' values; per armor slot a base material, a vanilla trim and a skin; a cloth on the
chestplate. A set *references* pieces, so a set costs nothing either, and can name pieces from packs
you have not saved. It is the lightest shareable thing the site has and probably the best one.

**Gallery** — the public view over everything published: packs, pieces, and sets. Not a separate
store of anything; a query.

### The verbs, and where each lands

| From | On a piece | On a pack |
|---|---|---|
| Gallery | Save to library · Add to a pack… · Wear it | Save to library · Install · Download |
| Library | Add to a pack… · Wear it · Remove | Open in editor · Edit contents · New version · Publish · Export · Remove |
| Wardrobe | (search gallery + library) Save the set · Save its pieces to my library · Build a pack of this set · Copy /give · Share |

**Save** writes a reference. **Add to a pack…** is the only verb that copies bytes, and it is
`pick_pieces.py` with the destination being one of your authored packs' drafts — which is exactly
where the ARR refusal, the two-sources-one-id refusal, the no-silent-overwrite refusal and the
credits union already live.

### What this reuses

The gallery already does most of the browsing: `/gallery/index.astro` renders every pack and every
piece from `mergedIndex()`, with filters by kind, socket, license, pack and author, a name search,
and a **selection kept in `localStorage`** (`public/gallery.js`, key `armorpieces.selection`) that
"Build a pack" posts to `/api/compose`. That anonymous selection is a library that forgets itself.
Signing in should adopt it — "keep this selection" — rather than replace it, and the same
`Add to selection` button becomes `Save to library` with a session.

---

## Decisions

1. **`/gallery/` is everything published; `/library/` is yours.** The current `/library/` page — what
   the index is, how the editor reads it, how to offer a pack — is prose about the catalogue and
   moves to `/gallery/` and `/wiki/packs`. The route `/library/` becomes the signed-in library.
2. **The catalogue's machine URL cannot move.** The desktop plugin derives `siteOrigin()` from the
   `armorpieces_library` setting (`armorpieces.js:1100-1102`), so `/library/index.json` is what every
   existing install talks to and how it finds `/api/me/*`. It keeps answering, forever, with a
   comment saying why. `/gallery/index.json` becomes its canonical name and what new builds ship as
   the default.
3. **One index shape, two URLs.** `/gallery/index.json` is the public catalogue (no auth, CORS `*`);
   `/api/me/library.json` is your library in the *same* `LibraryIndex` shape. The plugin's two pack
   sources — `library` (`armorpieces.js:1080`) and `account` (`:1348`) — become "The gallery" and
   "Your library" over one code path. "Choose a set of packs to use" is then just: your library's
   shelf is the install manifest.
4. **The account splits into three pages.** Tabs **Profile · Connectors · Account**; routes
   `/account/`, `/account/connectors/`, `/account/settings/`, because `/account/account/` is silly
   and the tab label, not the path, is what a reader sees.
5. **A pack being edited has one autosaved draft, and deliberate versions.** The draft is a zip
   object on the server that the editor and the site's own forms both write back to;
   `pack_versions` stays the deliberate, sequential, publishable thing. IndexedDB becomes a cache,
   not the master.
6. **The wardrobe renders in the real editor, not in a compositor.** A layered paper-doll of tinted
   greyscale renders would be fast and would be correct at one fixed camera, but it cannot rotate,
   cannot order two pieces on one bone by depth, and would be a second renderer to keep true.
   Instead the plugin gains a viewer mode: one rig wearing a whole set, everything locked, no editor
   chrome, free orbit. The site iframes `/editor/` and drives it. Boot cost is real (Blockbench,
   then Pyodide) and is covered by painting the existing per-piece thumbnails immediately and
   swapping the live figure in when it is ready.
7. **A set is handed over as vanilla `/give`, and as the pack that makes it work.** A short code is
   not possible without either a length limit or the mod phoning home, and the mod never contacts
   the site — that is a stated invariant of `website.md` §5 and one of its acceptance checks. So:
   four `/give` strings with a copy button, plus the composed pack of exactly the pieces used, built
   by the composer that already exists — and that pack carries an mcfunction that gives the whole
   set, so the download the player needs anyway is also the one-line way in. No mod change is
   required.
8. **Wiki pages become documents made of sections**, some prose, some generated, constructed by
   ModPageConstructor the way the home page already is. Prose stays hand-written; every fact that
   changes with a release comes from the mod's own data files.
9. **Generation runs in the mod repository, not on the site.** The data lives there, the site does
   not have it, and `scripts/sync.mjs` is already the seam. `modpage build -t site` writes JSON into
   the mod repo; sync copies it; the site reads JSON instead of parsing YAML.

---

## 0. The account, in three

Repo: `ArmorPiecesSite`. Nothing here is new behaviour — the same forms and the same `/api/me/*`
routes, divided. `public/account.js` binds everything by `document.querySelector`, so a form that
moves page keeps working as long as its `data-` attribute travels with it and the script stays
loaded.

**`/account/` — Profile.** Signed out this is the sign-in page exactly as today. Signed in it is who
you are on the site: the display name (`form[data-profile]`), what that name is attached to (packs
published under it, anything in the review queue), and a note that there is no avatar and no bio
because the site stores neither.

**`/account/connectors/` — Connectors.** Everything that is another thing reaching this account,
each with what it can see and how to cut it:

- **Sign-in** — the identities on the account (`schema.identities`), read-only, so a person can see
  they are the Google one and not the GitHub one. New: today the page never shows this.
- **GitHub** — the App installations (`myInstallations`), the install link, the link-a-repository
  form. Grant text as written: a grant for that repository, not the account.
- **Google Drive** — the `drive.file` grant, the picker, the link form, Revoke.
- **Devices** — the desktop editor's tokens, last use, Revoke, and a link to `/link/`.

**`/account/settings/` — Account.** The account as an object: storage used of quota as a bar and
what counts (your authored packs' versions only — saved packs and bookmarked pieces are references
and cost nothing); sign out; export everything; delete account with the `keepPublished` checkbox;
and the Review queue link for a maintainer.

**Shared shell.** `src/components/AccountTabs.astro` — the three links with `aria-current` — used by
all three. Signed-out `/account/connectors/` and `/account/settings/` redirect to `/account/`, as
`/account/packs/[id]` already does.

**Tests that move with it:** `test/accounts.test.mjs:177,182` read the device list off `/account/`;
`test/links.test.mjs:204` reads GitHub state off `/account/`. Both follow their forms to
`/account/connectors/`.

## 1. The library becomes yours

Repo: `ArmorPiecesSite`. This is the keystone; 2 and 3 are unbuildable without it.

**Schema.** Two tables and a third for sets:

- `library_packs` — `(userId, packId, kind: 'authored' | 'saved', versionId | null, addedAt)`.
  `versionId` null means *track the current published version*; set means *pinned*.
- `library_pieces` — `(userId, packId, pieceId, addedAt)`. A bookmark. No bytes, no quota.
- `sets` — `(id, userId, name, visibility, data jsonb, createdAt, updatedAt)`, `data` being the set
  as §2 defines it. Content-addressed share hash alongside, as composed packs already are
  (`src/lib/store.ts:38-55`).

A user's authored packs already exist as `packs.ownerId`; the `library_packs` row for them is
derived, not duplicated — `myLibrary()` unions the two.

**`/library/`** — your library, four sections: **Your packs** (authored: name, visibility, versions,
size, updated, and *New pack*), **Saved packs** (someone else's, with what version you track),
**Saved pieces** (the cards the gallery renders, with *Add to a pack…* and *Wear it*), **Your sets**.
Signed out: what a library is, plus your anonymous gallery selection with "sign in to keep this".

**`/library/packs/[id]/`** — `src/pages/account/packs/[id].astro` moved verbatim, `/account/packs/…`
kept as a 301 for a release because the upload and link flows redirect there. Grows teeth in §3.

**The Save verb.** `/api/me/library` — POST a `{kind: 'pack'|'piece', packId, pieceId?}` to save,
DELETE to remove, GET to list. On the gallery, `public/gallery.js`'s selection buttons become *Save
to library* when there is a session and keep their `localStorage` behaviour when there is not; a
sign-in offers to adopt what is in `localStorage`.

**`/api/me/library.json`** — your library as a `LibraryIndex`, the shape the plugin already reads,
so `siteJson('/api/me/packs')` in the `account` source (`armorpieces.js:1241`) becomes
`siteJson('/api/me/library.json')` and installs saved packs as well as your own.

**`/gallery/index.json`** — the canonical catalogue URL, `mergedIndex()` as today.
`/library/index.json` stays as a permanent alias (decision 2).

**The old `/library/` prose** — what the index is, how the editor reads it, how to offer a pack —
moves onto `/gallery/` and `/wiki/packs`. `NAV` gains **Library** beside **Gallery**; the Library
entry links to `/account/` when signed out.

## 2. The wardrobe, and sets

Repos: `ArmorPieces` (tool + plugin), `ArmorPiecesBlockbench` (build), `ArmorPiecesSite` (page).

- **`tools/bb_rig.py --wear <set.json>`.** The existing rig builder makes a project holding the
  vanilla body, the four armor layers and one part group for a single anchor (`build_rig`, line
  393). `--wear` makes one project holding the figure and every piece in the set, each at its
  anchor, each textured through `build_textures` with its own trim material — the function that
  already does the greyscale → material ramp. Base armor material, skin and cloth come through the
  same path (`build_skin_rig`, line 301). Everything locked. One tool, three callers: the plugin,
  the site's Playwright renderer, and a test.
- **Plugin: a viewer mode.** `window[ID + '_api']` (`armorpieces.js:6738`) gains `wear(set)` — build
  the rig, open it, no editing surface — and `viewMode(on)`, which hides the panels, toolbars and
  outliner and leaves an orbiting canvas. The existing `figure()` and `paintFaces` neighbours show
  the shape to follow. This is the whole plugin change.
- **`/wardrobe/`.** Sockets down the side, grouped by armor slot, each opening a picker over **your
  library first, then the whole gallery** — same filters, same cards, from `mergedIndex()` and
  `myLibrary()`, which already carry anchor, fittings, name and a thumbnail per piece. Per piece a
  trim material; per fitting its own value (a second material, a dye, a banner); per armor slot a
  base material, a vanilla trim and a skin; the chestplate a cloth. Thumbnails paint instantly; the
  iframe swaps in when `armorpieces_api` answers. A *Random* button and the six `GallerySets` as
  starting points (`StageCommand.java:850-948` is the reference for what a good set looks like —
  read it, do not import it).
- **Sets are saved, listed and shared.** *Save the set* writes a `sets` row; `/wardrobe/[id]/` opens
  one; *Save its pieces to my library* is a bulk POST to `/api/me/library`; *Add these to a pack…*
  goes straight to §3's copy verb. A public set appears at `/gallery/sets/[id]/`.
- **Handing it over.** Four `/give` strings built from the components as `ModDataComponents.java`
  defines them — `armorpieces:decorations` as a map keyed by anchor with
  `{material, decoration, fittings}`, `armorpieces:skin` as a bare id, `armorpieces:cloth` as
  `{cloth, base, patterns}`, vanilla `minecraft:trim` beside them. Beneath it, the packs the set
  needs and *Download the pack for this set*, posting the selection to the existing `/api/compose`
  (`src/lib/tools.ts`, `pick_pieces.py` + `export_pack.py`), with an mcfunction added to the
  composed pack that gives the whole set. Say plainly that the `/give` strings need the pieces
  installed and that a chat line caps at 256 characters.
- **A share card.** `scripts/thumbnails.mjs` already drives the editor headlessly; a sibling that
  calls `wear()` and photographs it gives `/wardrobe/<hash>.png` and a permalink, content-addressed
  exactly as composed packs are.

## 3. Authoring a pack on the site

Repos: `ArmorPieces` (tools), `ArmorPiecesSite`. The half that closes the loop.

- **Drafts.** `packs` gains `draftObjectKey`; `/api/me/packs/:id/draft` GETs and PUTs the working zip
  through the same quarantine every upload goes through (`checkUpload`, `src/lib/packs.ts:62-86`).
  *Save a version* is unchanged and still writes `pack_versions`.
- **The copy verb.** `pick_pieces.py` already copies a piece's whole file set between packs — the
  geometry, the master and its layer sheets, the data file, the template recipe, the language line,
  the loot-group tags, any fitting the source defines — refusing an ARR entry without `--own`,
  refusing two sources offering one id, refusing to overwrite. That is *move* (with a delete) and
  *copy* already. Add `--as <newid>` for *duplicate*, the one thing it cannot do today.
  `POST /api/me/packs/:id/pieces` takes `{from: [{packId, versionId, pieceId}], as?}`, runs the tool
  against the draft under Pyodide, re-manifests, and returns what it refused and why — in the tool's
  own words, so the site never invents a licensing rule.
- **The rest of the piece verbs.** Under `/api/me/packs/:id/pieces/*`: list (from the manifest),
  duplicate, move to another pack, delete, edit metadata.
- **Pack contents, outside Blockbench.** A form on `/library/packs/[id]`: pack name, description,
  license and credits (`armorpieces-credits.json`), which pieces are in, loot-group tag membership,
  recipe on/off, and the lang name of each piece. All small JSON edits in the pack folder that are
  miserable in Blockbench and obvious in a form.
- **The editor, embedded and full.** `/editor/` in a same-origin iframe on the pack page, driven
  through `contentWindow.armorpieces_api` (no `postMessage` needed while same-origin; leave a thin
  bridge object so it can become one later). `?embed=1` hides the start panel and site chrome — the
  same switch decision 6's viewer mode adds. A fullscreen button navigates to
  `/editor/?pack=<id>&piece=<id>`, so deep links need those two query parameters in
  `armorpieces-start.js`. Signed in, the editor's `account` source opens from and autosaves to the
  draft, so the browser stops being the master copy.
- **Publish** is what already exists: visibility public → `publications` → the review queue → the
  gallery, with thumbnails rendered on approval.

## A. ModPageConstructor: element types, a site target, and lang

Generic work, none of it about this mod, and independent of 0-3. Repo:
`C:\Users\Matthijs\ModPageConstructor` (heavy WIP — uncommitted `generators.py`,
`builtin_generators.py`, `gitinfo.py`, `action.yml`, `.github/`, `scaffold/workflow.yml`; these land
on top of it, not instead of it).

**What it has.** A generator registry with a repo-local plugin seam (`.modpage/generators/*.py`,
loaded by `generators.py:load_project_generators`); a `Context` that can glob, read text, and parse
JSON/YAML out of the mod repo; a shaping pipeline (`where`/`sort`/`limit`/`map`/`group_by`/…) usable
both at the declaration and at every reference site; `{from: name}` references expanded anywhere in
the config (`config.py:538-545`); nine built-ins including `data.file`. A genuine Minecraft data
layer in `recipes.py` / `textures.py`: recipe JSON across six loader layouts, ingredient shapes
across versions, recursive item-tag resolution with a vanilla fallback from misode/mcmeta, item
textures resolved through model JSON, and `custom_types:` for a mod's own recipe serializers —
which `modpage.yml:214-226` already uses for all four smithing types.

**What it lacks.** No lang reading (display names are guessed by prettifying an id). No registry
enumeration (items are found only where a recipe mentions them, so the 61 pieces with no recipe are
invisible). No element types (`partials/{md,plain,html}.j2` dispatch on `section.layout` — seven
fixed layouts, no `type:` dispatch, no raw-HTML element; a repo can only override the whole template
directory). No output but the three marketplaces (`render.py:34-45` `TARGETS` is a Python dict; a
downstream repo can add a generator without forking, but not a target). No versioned config.

So the generator half is ready and the emit half is not. Four additions, all generic and additive:

- **`type:` on an element, and a per-type template.** `partials/*.j2`'s `elements()` gains one
  branch: an element carrying `type: <name>` renders through `elements/<name>.<target>.j2`, looked
  up on the existing `ChoiceLoader` (`render.py:76-79`) so `.modpage/elements/` in a mod repo wins
  over the packaged set — the same shape the generator seam already has.
- **A `site` target.** One more `Target` in `render.py:34-45`, template `site.json.j2`, writing the
  fully resolved config plus every declared generator's elements (`gen`, already in the template
  context at `render.py:195`) as JSON. It is "the config, after generators, as data".
- **`mc.lang`, a built-in generator.** Reads `assets/<ns>/lang/<code>.json`, emits one element per
  key with `key`, `value` and the id parsed out of the key. Add a `lang:` option to `data.file` too,
  so a generator reading decoration JSON can resolve `description.translate` to a real name — the
  rule `pack_manifest.py:231-236` already uses.
- **Document targets.** Decision 8 needs more than one page per build: a `documents:` block naming
  extra configs, each rendered to its own output under the `site` target. Keep it small — a list of
  `{id, config, out}`.

**Note for whoever does it:** the layout/element dispatch exists three times over (`md.j2`,
`plain.j2`, `html.j2`) with no test holding them symmetric. Anything added here must be added in all
of them, and CI's only signal is that `examples/example-mod` still renders byte-identically. Also
`ACTION_REPO = "USER/ModPageConstructor"` (`cli.py:18`, and four places in `README.md`) is still a
placeholder.

## B. The generated content

Repos: `ArmorPieces` (mod), then `ArmorPiecesSite`. Needs A.

- **`.modpage/generators/armorpieces.py`** — the mod's own generators, in the mod repo where the
  data is. Each reads `src/main/resources/data/armorpieces/armorpieces/*` and the lang file:
  `sockets` (from `DecorationAnchor.java`, parsed the way `tools/bb_rig.py:70` already parses it,
  joined to `anchor.armorpieces.*` lang keys), `pieces`, `skins`, `cloths`, `fittings`,
  `loot_groups`, `effect_types`, and `counts` (the derived numbers: 91, 14, 2, 4, 6, 30 craftable,
  "at least six per socket"). These are the game hooks section A does not generalise, and they
  belong here rather than in the tool.
- **`modpage.yml` stops stating numbers.** `sections.about`, `features` and the whats-new custom
  section reference `{from: counts}` and `{from: sockets}` instead of spelling them out. The prose
  around them stays.
- **`docs/wiki/*.yml`** — each wiki page as a document: an ordered list of sections, each either
  prose or `{from: <generator>}`. `pieces.yml`'s socket table, `loot.yml`'s group list, `skins.yml`'s
  fourteen and `fittings.yml`'s four become generated; the prose moves across verbatim from
  `content/wiki/*.md`. `authoring.md` keeps coming from `docs/authoring.md` as it does today.
- **Site.** `scripts/sync.mjs` gains `dist/site.json` and `dist/wiki/*.json` to its `WANTED` list.
  `src/lib/mod.ts` reads the JSON instead of `js-yaml` over `modpage.yml`. `src/content.config.ts`
  and `src/pages/wiki/[...slug].astro` render a document's sections; `src/components/Wiki.astro`
  keeps its shell, sidebar, TOC and Pagefind. Delete `SOCKETS`/`SOCKET_SLOT` from
  `src/lib/library.ts:78-84` and read them from the generated data — that is the third copy of the
  socket list.

---

## Order

Two tracks. The platform track is a chain; the content track is independent and can be picked up
whenever the other is blocked.

**Platform:** 0 → 1 → 3 → 2.

1. **0** — the account in three. Cheap, local, and it clears `/account/` so §1 can take the packs.
2. **1** — the library becomes yours: the tables, `/library/`, the Save verb, `/api/me/library.json`,
   `/gallery/index.json`, the prose moved. Everything else needs this.
3. **3** — authoring: drafts, `--as`, the copy verb, the piece endpoints, the pack form, the embedded
   editor. This closes the loop — gallery → library → your pack → gallery — and is pure site and
   tool work.
4. **2** — the wardrobe and sets: `bb_rig.py --wear`, the plugin's viewer mode, `/wardrobe/`, the
   give strings, the composed pack with its function, the share card. Last because it is the
   heaviest (a rig tool, a plugin mode, a headless renderer) and because saving a set into a library
   and adding its pieces to a pack both want §1 and §3 finished.

**Content:** A → B, any time.

§2 and §3 both want the editor's `?embed=1` switch; whichever lands first builds it.

## Verification

- `/account/`, `/account/connectors/` and `/account/settings/` each render signed in and signed out;
  every form that moved still saves; `test/accounts.test.mjs` and `test/links.test.mjs` follow their
  forms rather than being deleted. `/account/packs/<id>/` still resolves.
- **The catalogue URL never breaks:** `/library/index.json` answers with the same bytes as
  `/gallery/index.json`, with CORS, for a request carrying no session — the desktop plugin's
  `siteOrigin()` depends on it. `test/site.test.mjs:92` covers the old URL; add the new one beside it.
- A library round-trip over HTTP in `test/accounts.test.mjs`'s style: save a piece, save a pack,
  `/api/me/library.json` lists both in `LibraryIndex` shape, remove them, quota is unchanged
  throughout (a bookmark costs nothing).
- **Licensing holds:** bookmarking an ARR piece succeeds; `POST /api/me/packs/:id/pieces` copying
  that piece into a pack that is not its author's is refused, in `pick_pieces.py`'s own words;
  copying your own ARR piece succeeds; a name collision is refused; the destination's
  `armorpieces-credits.json` carries the union.
- `npm test` stays green; extend it (or a sibling `pieces.test.mjs` — every suite there drives the
  built server over HTTP) with: draft round-trip, duplicate a piece, move a piece to another pack,
  refuse a colliding move, and a version cut from a draft.
- `test/editor-account.test.mjs` grows a case for the embedded iframe reaching `armorpieces_api` and
  for `?pack=&piece=` opening the right piece.
- `python tools/bb_rig.py --wear <a set with a piece in every socket, a skin and a cloth>` opens in
  desktop Blockbench and shows the set with nothing clipping; `tools/tests` gets a case. The same
  call under Pyodide (`build/test_pyodide.mjs` in `ArmorPiecesBlockbench` compares tool output
  byte-for-byte against CPython) must agree.
- `/wardrobe/`: pick a piece in all twelve sockets, a skin, a cloth, a trim and every fitting; the
  figure shows it; the four `/give` strings paste into a 26.2 client and produce exactly that armor;
  *Download the pack* gives a pack whose function does the same on a server without the mod's own
  datapack. Save it, reopen it from `/library/`, and get the same figure. Check a phone width and
  check that the thumbnails paint before the iframe boots.
- `modpage build -c examples/example-mod/modpage.yml -t all --check --offline` still passes, and a
  new example element type and `-t site` are covered the same way (add the new output to the
  committed example).
- In `ArmorPieces`: `modpage generators` lists the eight new generators and previews each;
  `modpage build -t site` writes `dist/site.json` and `dist/wiki/*.json`; its counts match
  `ls data/armorpieces/armorpieces/armor_decoration | wc -l` and friends. Grep the repo and the site
  for `91`, `ninety-one`, `fourteen` and the socket names: the only hits should be generated output.
- The mod still opens no connection to the site: grep, and the existing check in `website.md`.

## Risks

- **The word "library" is changing meaning under running software.** Decision 2 keeps the machine URL
  and moves only the human one, but the plugin's UI strings, the wiki, the desktop setting's
  description and `library/entries/*.json` in `ArmorPiecesBlockbench` all say "library" meaning the
  catalogue. Rename the prose in one pass, deliberately, and leave the JSON alone.
- **A bookmark is not a copy, and people will expect it to be.** A saved piece whose pack is
  unpublished, deleted or re-versioned goes stale. The library must show that state ("this pack is
  gone", "version 3 no longer has this piece") rather than 404 in a wardrobe.
- **Editor boot on a dress-up page.** Blockbench plus Pyodide is seconds. The thumbnails-first paint
  covers it; if it still reads badly, the fallback is decision 6's paper-doll for the idle view with
  the live figure behind a "look closer" button. Decide after measuring, not before.
- **Quota, once packs can be authored on the site.** A draft plus fifty versions per pack, times
  however many packs, against 200 MB. Drafts are content-addressed like everything else, so a save
  that changes nothing costs nothing; but `MAX_VERSIONS` and the quota want revisiting before §3
  ships, not after.
- **ModPageConstructor is mid-change.** Everything in A lands on an uncommitted working tree. Do not
  start A while that tree is being edited elsewhere.
- **Four repos, three of them WIP-heavy.** `ArmorPieces` is mid-0.4.0 with sections 2-4 built and
  uncommitted. Nothing here should be swept into someone else's commit; and commits go to
  `Documents\GitHub\ArmorPieces`, not the working copy.
- **The wiki rewrite is a content migration.** Moving ten hand-written pages into documents is where
  prose gets silently lost. Move it verbatim, one page per commit, and diff the rendered output.
