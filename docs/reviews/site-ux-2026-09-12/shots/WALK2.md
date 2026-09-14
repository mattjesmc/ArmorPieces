# Armor Pieces site: screenshot walk 2, 2026-09-12

The pages and interactions the first walk (`WALK.md`) never opened. Same build: ArmorPiecesSite at 3662d20, dist/ already built from that commit (tree clean, `dist/server/entry.mjs` present, no rebuild needed). Served by `node server.mjs` with `NODE_ENV=test TEST_LOGIN_SECRET=walk2 DATA_DIR=<scratchpad>/data-walk2 SHOTS=off PORT=4878 HOST=127.0.0.1 AUTH_SECRET=<40 chars> AUTH_TRUST_HOST=true`, after `node scripts/migrate.mjs` with the same environment on the fresh PGlite dir (the server does not migrate by itself). Walked in headless Chromium (playwright 1.63 from the site's node_modules) at 1280x800 (`walk2-desktop-*`) and 400x800 (`walk2-phone-*`), full-page unless the page exceeded 6000 px, in which case the viewport-height top was kept and it says so below. Three identities per width: signed out, "Author" (a plain user) and "Maintainer" (maintainer: true), made once each through `POST /api/test/login` and the cookies copied to the phone contexts, so both widths see the same library. The Author's "Saved" collection was seeded by `POST /api/me/library {kind:'piece', pieceId:'armorpieces:aerials'}` (the collection is made on demand, an account that never saved a piece has none). The bogus zip was a text file renamed `.zip`. `/api/test/objects` was read and not used: it ingests zips and runs the composers for the parity test, and the shipped catalogue (91 pieces, 14 skins, 2 cloths, three outfits) was already there without it.

Per page, `notes2.json` records url, status, final url, title, h1, console errors and warnings, failed requests (4xx/5xx and network failures), horizontal overflow (`scrollWidth > clientWidth`, with the numbers), controls without a text or aria label, the visible text, and an `extra` object with what each interaction found (dialog text and buttons, picker state, the compose response, redirect targets, tab order, and so on). 74 shots.

## Cross-page issues

1. **The wiki search is dead, on this build and on armorpieces.com.** Typing "skin" leaves "Searching for skin..." forever with no results (`walk2-desktop-wiki-search-skin.png`). Pagefind's WASM is refused by the CSP: "Compiling or instantiating WebAssembly module violates ... `script-src 'self'`" (five console errors per keystroke). The site CSP in `server.mjs` needs `'wasm-unsafe-eval'` in `script-src` (the editor's CSP already has it). `curl -I https://armorpieces.com/wiki/` returns the identical `Content-Security-Policy`, so the live wiki has no working search either. Real, and the first walk missed it because it never typed in the box.
2. **The outfit page scrolls horizontally at every width.** `/wardrobe/armorpieces-knight_errant/` has `scrollWidth` 3151 at both 1280 and 400 px. The `<pre>` under "Wearing it" has `overflow-x: auto`, but its `.gives` grid column is sized to the `<pre>`'s content (3131 px wide), so the column, not the pre, overflows; the desktop full-page capture is 3151 px wide with the page squeezed into its left 1280. The dressing room has the same fault once a piece is chosen: at 400 px `scrollWidth` 853 (`walk2-phone-wardrobe-new-chosen-*.png`); at 1280 the one short command fits. Real (`min-width: 0` on the grid item, or `overflow-x` on the `.gives` child).
3. **Every error page is bare text.** `/nonexistent-page/` answers "not found", `/gallery/packs/nope/` "No such pack", `/gallery/pieces/nope/nope/` "No such piece", `/wardrobe/nope/` "No such set", the signed-in `/library/packs/<zero uuid>/` "not found" - all 404, `text/plain`, no nav, no footer, no link anywhere (`walk2-*-error-*.png`, ten shots of a line of monospace text). `/admin/queue/` as a plain user is a bare 403 "Maintainers only". A mistyped or stale link (a deleted pack, an outfit made private) drops the visitor out of the site. Real.
4. **The confirm dialogs put the initial focus on the destructive button, and lose focus on Escape.** "Delete the account?" and "Delete this pack?" open with focus on *Delete it* (recorded in `extra.dialog.focused`), so Enter right after the click deletes. Escape closes both (good), but focus then lands on `<body>` rather than back on the button that opened it (`focusAfter` is the page's text from "Skip to content"). The gallery's Details sheet does this right: focus moves into the sheet and comes back to the *Details* link on Escape. Real, `public/ui.js` `dialog()`.
5. **The invalid `pattern` is in three forms, not one.** The first walk found it on New pack's slug. The same `[a-z0-9][a-z0-9-]{1,39}` is on the pack page (a console error on every `/library/packs/<id>/` load) and `[a-z0-9][a-z0-9-]{1,31}` on `/gallery/build/`'s pack name. Chromium skips the check in all three ("Invalid character class" under the `v` flag; write `[a-z0-9\-]` or put the hyphen first). Real.
6. **`banner: [object Object]` on the outfit page.** The Banner card under Knight Errant prints the fitting's value with `String()`; a banner fitting is `{base, patterns}` (`lib/wardrobe.ts:36`), and the card shows "banner: [object Object]" (`walk2-desktop-outfit-knight-errant.png`, the Banner card). Real, `OutfitDetail.astro` fittings line.
7. **The footer contact is a placeholder and has a missing space** - `contact@armorpieces.example` and "under theArmor Pieces License" on every page. The address is the default of `SITE_CONTACT_EMAIL` (`lib/site.ts:36`), so on this build it is an environment artefact; the live /about/ did not show it in a curl, so the VPS has the variable. The missing space is in the layout and real.
8. **Environment artefacts** carried over from walk 1: SHOTS=off means the High Court and Far Road renders answer 503 and their cards fall back to a piece thumbnail (two console errors on /wardrobe/ and /gallery/); every signed-out page with a Save button probes `/api/me/library` and logs a 401; no OAuth provider is configured. None of these are site faults.

## Screenshots

### walk2-desktop-wardrobe.png / walk2-phone-wardrobe.png (/wardrobe/, signed out)
As in walk 1. Every outfit link is `data-overlay` (title and *Look* both open the sheet). The Knight Errant link is `/wardrobe/armorpieces-knight_errant/`; the walk opened it as a page.

### walk2-desktop-outfit-knight-errant.png / walk2-phone-outfit-knight-errant.png (top crop, 7433 px)
"Knight Errant" with a "the mod's own" pill, "12 pieces, a skin, a cloth.One of the outfits that ship with the mod" (missing space after the full stop), the stage command in code, "12 from Armor Pieces", the outfit's description, then the render on the left with *Show the real figure* and a paragraph, and twelve 256 px piece cards two per row on the right, each "socket · material" and its fittings; then "Wearing it": four `/give` commands, each flagged in red "too long for a chat line; use a command block or the pack's function". **Every control on the page** (recorded in `extra.controls`): the nav, "← Wardrobe", *Show the real figure* (button), *Open it in the dressing room* (link), twelve piece links (overlay), *Open this in the dressing room* (link, again), footer links. **Nothing downloads**: no `download` attribute, no link to a zip, no Copy button on any command, and no report form (official outfits have none). The remedy for "too long" is the dressing room, two links away. Also: horizontal scroll at both widths (cross-page 2), `banner: [object Object]` (cross-page 6), the card grid makes the page 4.0k / 7.4k px, and on the phone the render fills the first screen. No console errors.

### walk2-{desktop,phone}-wardrobe-new-picker-{out,author}.png (/wardrobe/new/, crest "Choose…" clicked)
The picker is not a dialog: it is a grey panel in the document flow after the twelve socket rows and before "Wearing it in game" (`position: static`), so clicking *Choose…* on "crest" at the top scrolls the page 1100 px (2100 on the phone) down to it, because the panel's search box takes focus - which on a phone also raises the keyboard. Filters: a Source select ("The gallery"; signed in also "Saved (1)" and the Author's own pack), licence, search, "7 pieces"; seven cards (Antennae, Brush Crest, Comb, Dorsal Fin, Feathering, Horsetail, Spire), each a button with a thumbnail, name and "crest · Armor Pieces". Nothing says which socket is being dressed, and there is no Close. On the phone the cards are two per row. No console errors.

### walk2-{desktop,phone}-wardrobe-new-chosen-{out,author}.png (Antennae picked)
The picker hides. The figure box changes: the note is hidden and the piece's thumbnail (a head close-up) appears in it, not a figure. The crest row reads "Antennae in iron" with *Clear*, and a second line "material [iron] gemstone [empty]" - the gemstone fitting select offers 28 options: empty, eleven trim materials and sixteen dyes, unexplained. "Wearing it in game" fills in: four commands, one carrying the antennae, each with a *Copy* button (the outfit page has none). Phone: the command line overflows (cross-page 2). Signed in, identical plus "Add its pieces to a collection…" / "Make a pack of this outfit…". The draft is kept in `localStorage` (`armorpieces.wardrobe`), so leaving the page does not lose it.

### walk2-{desktop,phone}-wardrobe-new-built-{out,author}.png (*Download the pack for this set* clicked)
The button does not download. It posts `/api/compose` (200, JSON) and then **navigates away** to `/composed/ac42ac…/` - the page titled "untitled-set" because no name was typed ("untitled-set, a composed pack"), where the actual download is a further click ("Download untitled-set.zip (4 KB)"). The page shows "A pack of 1 piece", licences ("All rights reserved · 1", "Antennae (piece) by someone"). Works, signed out and in, both widths, but the label says download and the click leaves the dressing room; the name should come from the outfit or the button should say "Build the pack…". The zip answers `application/zip` with `Content-Disposition: attachment`.

### walk2-{desktop,phone}-account-settings.png (/account/settings/, Author)
"Author", tabs Profile / Connectors / **Account**, "The account itself: what it stores, and how to leave." Storage: "0.0 of 52.4 MB, across 0 versions of 0 packs", a meter (role=img, labelled), "0 of 20,000 files. A file costs a disk block whatever its size…", the note that library references cost nothing. Session: *Sign out* (the only sign-out on the site is here, three clicks from anywhere). Your data: *Export everything* (`/api/me/export`, `download`; answers 200 `application/json`, `attachment; filename="armorpieces-account.json"`, 500 bytes for a fresh account, 2.4 KB after the walk's pack and collection) and the explanation; a checkbox "Leave my published packs in the gallery under my name" and a red *Delete account* with "Removes the user, identities, sessions, device tokens and private packs at once. Not undone." Four controls in all. Clean, no console errors.

### walk2-{desktop,phone}-account-settings-delete-dialog.png
A centred dialog (role=dialog, aria-modal): "Delete the account? / Every private pack goes with it, and this is not undone. / Delete it · Cancel". Focus starts on *Delete it* (cross-page 4). The copy contradicts the checkbox above it: with the box unticked, public packs go too (the review's "Deleting" note), and the dialog says only "private". Escape closes it; not confirmed.

### walk2-{desktop,phone}-connectors-link-a-device.png (/account/connectors/ → "Link a device")
"Link a device" under Devices is a plain link to `/link/`, so what opens is the signed-in link page: "Link the desktop editor", the lead, an empty Code field (placeholder ABCD-EFGH), *Approve this device*, the phishing note. Nothing on it says what to do if you have no code, and it is reached from a page that just said "No devices".

### walk2-{desktop,phone}-link-no-code-{out,author}.png, walk2-{desktop,phone}-link-bogus-code-{out,author}.png (/link/ and /link/?code=ABCDEF)
Signed out, both: a single purple notice, "Sign in first, then come back to this page: Sign in. The code in the editor stays good for fifteen minutes." The *Sign in* link is `/account/` with no return URL, and `?code=ABCDEF` is not carried, so after signing in the person has to find `/link/` again and retype the code. Signed in, no code: the empty required field; submit shows only the browser's "Please fill out this field." bubble (not painted in headless shots). Signed in, `?code=ABCDEF`: the field is pre-filled "ABCDEF", `checkValidity()` false ("Please match the requested format."), the device notice stays hidden (the script only asks the server for eight characters), and submit does nothing visible - nothing on the page says a code is eight characters. Typed as ABCD-EFGH (`walk2-*-link-bogus-8-author.png`): "No such code, or it has expired. Ask the editor for a new one." appears at once as a warning notice and again as the submit status (two 404s in the console, `/api/device/info` and `/api/device/approve`). That path is good.

### walk2-{desktop,phone}-library-collections.png (/library/?view=collections, Author)
"Your library", "0 packs of your own, 0 linked, 1 piece. Storage 0.0 of 52.4 MB…", the four-way toggle with **Collections 1** active, a definition paragraph, *New collection* with "a piece you save from the gallery lands in one called Saved", a search box, and one card: "Saved / Pieces kept from the gallery. / 1 piece · updated 2026-09-12 / Open · Details · Export…". Below, the sentence quoting the editor's menu path and `/api/me/library.json`. The toggle is a link (`?view=collections`), fine. Phone: the toggle wraps its counts.

### walk2-{desktop,phone}-collection-saved.png (/library/collections/<id>/)
"← Your collections", "Saved", "Pieces kept from the gallery.", "1 piece · a collection costs nothing…", five buttons in a row (*Its pieces*, *Rename…*, *Export as a pack…*, *Make a pack of it…*, *Delete the collection*), then **Import a zip** - a paragraph, two file inputs (Datapack zip / Resource pack zip, `accept=.zip`, neither required), a five-line paragraph on halves, the "my own work" checkbox, *Import it* - then "What is in it" with *Add pieces…* and a table (Piece `armorpieces:aerials`, Kind "piece · horns", Name, Licence, From "armorpieces", In the gallery "ships with the mod", *Add to a pack…* / *Remove*). The import form sits between the verbs and the contents of a collection called "Saved", on the one page a person reaches by saving a gallery piece; the site's only upload is here. The delete button has no dialog check in this walk (not clicked).

### walk2-{desktop,phone}-collection-import-empty.png (Import it, no files)
Inline status beside the button: "Choose the datapack zip and the resource pack zip — a pack is both halves." Good sentence, no request sent.

### walk2-{desktop,phone}-collection-import-bogus.png (bogus.zip in Datapack, own ticked)
`POST …/import` answers 400 `{"error":"That is not a zip file."}` and the status line says the same. Good. The file stays chosen ("bogus.zip") so a retry is one click.

### walk2-{desktop,phone}-pack-delete-dialog.png (/library/packs/<id>/ after New pack)
The pack was made from `/library/packs/new/` (slug `walk2-desktop`, name "Walk2 desktop pack"); the form navigated to `/library/packs/<uuid>/` with the same content as walk 1's pack page (and its console error, cross-page 5). *Delete this pack* opens "Delete this pack? / Every version of it goes. The pieces themselves stay where they are published. / Delete it · Cancel", focus on *Delete it*; Escape closes it (not confirmed). The Visibility select's options, recorded (`walk2-*-pack-visibility-select.png` shows it focused; a native select's popup is not painted in headless Chromium): "Private (only you)", "Unlisted (anyone with the link)", "Public (after review, in the gallery)". Clear labels; note "Public" here files a publication with no licence tick or per-piece view (the review's two-doors point).

### walk2-{desktop,phone}-account-packs-redirect.png (/account/packs/<id>/)
A 301 to `/library/packs/<id>/` (raw request: status 301, `location` the library URL); the browser lands on the pack page. The old address still works; fine.

### walk2-{desktop,phone}-admin-queue-maintainer.png (/admin/queue/, Maintainer)
"Review queue", "0 waiting. Open the pack in the editor from its link, check it against the terms(all ages; …)" (missing space before the bracket), "Nothing waiting."; **Open reports** with a four-line explanation of Dismiss / Uphold and "None."; **Take a piece down, or put it back** with "Object hash (64 hex characters)" and "Why" inputs, *Take it down* / *Put it back*. The takedown form is live on an empty queue and asks for a raw hash; no link back to the account. As Author: 403 bare text "Maintainers only" (`walk2-*-admin-queue-author.png`). Signed out: 302 to `/account/`.

### walk2-{desktop,phone}-build-empty.png (/gallery/build/, signed out, nothing kept)
"Build a pack", the lead, and a notice "Nothing is selected. Pick some pieces in the gallery first." with the link; the table and form are hidden, so there is nothing to submit - the empty state is handled. Two 401s (`/api/me/library`, the shelf probe, twice). The page cannot pick pieces itself.

### walk2-{desktop,phone}-build-two-submitted.png (two Saves on /gallery/?view=pieces, then Build)
Saving Aerials and Anklets from the pieces view (buttons turn to "Kept"; the browser shelf `armorpieces.library` gains a local "Saved" collection) fills the table: Piece / Kind / Pack / License "All rights reserved" / Remove. A licence column reading "All rights reserved" on pieces that are about to be composed is a contradiction only the terms explain. Pack name "walk2-set" (the invalid pattern, cross-page 5), *Build the pack* → `/api/compose` 200 `{hash, download, page, size: 6064}` → "Your pack is ready / Download the zip · The download page". The build page stays; the result appears under the form.

### walk2-{desktop,phone}-composed.png (/composed/<hash>/)
"← Gallery", "walk2-set", "A pack of 2 pieces, built 2026-09-12 from the gallery. One zip, both halves: put it under a world's datapacks/ and under resourcepacks/, or bring it into the editor with Import zip…", *Download walk2-set.zip (6 KB)* (200, `application/zip`, `attachment; filename="walk2-set.zip"`), "What you may do with it", "Licenses in this pack: All rights reserved ARR · 2: Aerials (piece) by someone, from Armor Pieces". **"by someone"** for the mod's own pieces: the author field is empty and the fallback word is wrong for official content. "Content hash 923e40a58e092fb8…". Nothing says which mod version the zip needs (the review's point 4).

### walk2-desktop-{contact,privacy,terms,cookies}-top.png (viewport crops, desktop only)
Contact (800 px, fits): the address (placeholder here) and what to write about. Privacy 2142 px, Terms 2076 px, Cookies 1178 px: plain prose pages with headings, no table of contents; readable, no console errors. Not read for content.

### walk2-{desktop,phone}-error-*.png (five each)
Bare `text/plain` 404s (cross-page 3): "not found", "No such pack", "No such piece", "No such set", "not found".

### Keyboard (/gallery/, no shot for the tab order; walk2-{desktop,phone}-gallery-details-sheet.png)
Tab from the top: 1 "Skip to content" (#main), 2 "Armor Pieces" (/), 3 Wiki, 4 Gallery, 5 Wardrobe, 6 Library, 7 Editor, 8 Account - the skip link exists and every stop has the default focus ring (`outline: auto 1px`). Clicking the pack card's *Details* opens the sheet (title "Armor Pieces", `role=dialog`, focus on the sheet itself, URL becomes `/gallery/packs/armorpieces/`, `html.ap-sheet-open`); Escape closes it, focus returns to the *Details* link, the URL returns to `/gallery/`. Correct on both widths. The `unlabeled` list on this page is a false positive: seven links with text inside the closed "The catalogue…" disclosure, which have no `innerText` while hidden.

### walk2-{desktop,phone}-wiki-search-skin.png (/wiki/, "skin" typed)
The search box with "skin" and a *Clear* button, "Searching for skin..." under it, and nothing else, forever (cross-page 1). The sidebar and article are unchanged.

## Console errors / failed requests per page (deduplicated, both widths)

| page | console | failed requests |
|---|---|---|
| /wardrobe/ | 503 x2 | the two outfit renders (SHOTS=off) |
| /wardrobe/armorpieces-knight_errant/ | none | none |
| /wardrobe/new/ (picker, pick, build; out and in) | none | none |
| /composed/<hash>/ | none | none |
| /account/settings/ (+ dialog) | none | none |
| /account/connectors/, /link/ (all variants) | none | none |
| /link/ with ABCD-EFGH typed | 404 x2 | /api/device/info?code=ABCDEFGH, /api/device/approve (expected: bogus code) |
| /library/?view=collections, /library/collections/<id>/ | none | none |
| collection import, bogus zip | 400 | POST …/import (expected) |
| /library/packs/<id>/ (new pack, dialog) | "Pattern attribute value [a-z0-9][a-z0-9-]{1,39} is not a valid regular expression" | none |
| /account/packs/<id>/ | none (301 followed) | none |
| /admin/queue/ maintainer | none | none |
| /admin/queue/ author | 403 | /admin/queue/ (bare "Maintainers only") |
| /gallery/build/ (empty) | 401 x2 | /api/me/library x2 |
| /gallery/build/ (two pieces, built) | 401 x2 + "Pattern attribute value [a-z0-9][a-z0-9-]{1,31} is not a valid regular expression" | /api/me/library x2 |
| /contact/, /privacy/, /terms/, /cookies/ | none | none |
| the five error URLs | one 404 each | the page itself |
| /gallery/ (tab order, sheet) | 401, 503 x2 | /api/me/library, the two renders |
| /wiki/ (search) | "Failed to load the Pagefind WASM: … violates … script-src 'self'" x5 (1 console error + 4 pageerrors per query) | none (the fetch succeeds; instantiation is refused) |

## What did not work / caveats

- Everything ran; no step errored. The server needed `AUTH_SECRET` and `AUTH_TRUST_HOST` as the tests set them (taken from `test/accounts.test.mjs`), and `scripts/migrate.mjs` first.
- A native `<select>`'s open popup is not painted in headless Chromium, so `walk2-*-pack-visibility-select.png` shows the select focused and the option texts are in `notes2.json` and above.
- Browser validation bubbles ("Please fill out this field.", "Please match the requested format.") are likewise not painted; their `validationMessage` is recorded instead.
- The Knight Errant page at 400 px is 7433 px tall and was cropped to the viewport (the desktop capture is full and 3151 px wide because of the overflow).
- Neither delete was confirmed; both dialogs were closed with Escape. The collection's *Delete the collection* and the account's *Sign out* were not clicked.
- The dressing room's *Show the real figure* (boots Blockbench + Pyodide in an iframe) was not clicked; the figure box in the shots is the thumbnail stand-in the page describes.
- The wardrobe's build made a composed pack named "untitled-set" because no name was typed; that is what a visitor who clicks the button first gets too.
- `contact@armorpieces.example` in every footer is this environment's default for `SITE_CONTACT_EMAIL`; the live site does not show it. The missing space in "under theArmor Pieces License" is in the layout regardless.
- The server was stopped and `data-walk2` deleted afterwards; the pack, collection and composed zips made by the walk lived only there.
