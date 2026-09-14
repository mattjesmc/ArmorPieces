# Armor Pieces site: screenshot walk, 2026-09-12

Built from ArmorPiecesSite at 3662d20 (`npm run build`, dist rebuilt because it predated the last commit), served by `node server.mjs` against dist/ with the tests' environment (PGlite under data/test-uxshots, NODE_ENV=test, TEST_LOGIN_SECRET set, SHOTS=off), walked in headless Chromium (playwright 1.63) at 1280x800 (`desktop-*`) and 400x800 (`phone-*`), full-page. Raw per-page data (title, nav links, h1, console, failed requests, overflow check, unlabeled controls) is in `notes.json`.

Every page answered 200. The nav on every page reads: Armor Pieces (brand) · Wiki · Gallery · Wardrobe · Library · Editor · Account. No page scrolls horizontally at 400px (scrollWidth == clientWidth everywhere), and no button or link without a text label or aria-label was found on any page. The footer (disclaimer, contact, license, About/Terms/Privacy/Cookies/Contact/Source) is the same everywhere.

## Cross-page issues

1. **Environment artefacts, not site bugs, but they shape what the shots show.** With SHOTS=off the outfit renders for High Court and Far Road are never made, so `/wardrobe/<hash>.png?w=256` answers 503 and the card falls back to a piece thumbnail: a grey close-up of a chestplate. On the deployed site those renders are pre-made. Every signed-out page that has a Save button calls `/api/me/library` (and the piece pages `/api/me/packs`) and gets 401 - that is the shelf script probing for a session, harmless but it is a red line in the console on every gallery page.
2. **The editor's Blockbench build phones home** (web.blockbench.net/content/news.json, blckbn.ch/api/stats/plugins, blckbn.ch/api/event/new_installation) and is blocked by the CSP - three console errors on every editor load, plus "A bad HTTP response code (404) was received when fetching the script" and an uncaught `[pageerror] Object` from inside the frame.
3. **Real bug, new-pack form:** the slug input's `pattern="[a-z0-9][a-z0-9-]{1,39}"` is rejected by Chromium ("Invalid regular expression ... /v: Invalid character class" - a trailing `-` inside a class is not allowed under the `v` flag browsers now compile patterns with), so the browser silently skips the pattern check. The server still validates, but the inline hint is not enforced client-side.
4. **The editor frame is short.** On both pages that embed it (/editor/ signed out and in) the iframe is about 520px tall inside an 800px viewport; the Blockbench start page is cut off below the filter row, so the piece list itself is never visible without scrolling inside the frame. On the phone the frame's own menu bar overflows inside it ("Vi Blockbe... Download Ap" clipped) - not page overflow, but the editor is unusable at 400px and the page does not say so.
5. **Hero slider caption collides with its controls** on the front page: the caption ("Themed sets, every socket filled - ...") is drawn on the same line as the prev/next arrows and the dot indicators and is unreadable behind them, at both widths.
6. **Tall pages.** The pack detail page is 15,766px on desktop and 48,517px on the phone (105 cards, three or one per row); the pieces view is 13,105 / 55,765px; About is 8,883 / 16,985px because the full release notes are appended. No pagination, no "back to top".
7. **Copy density and jargon.** Almost every page opens with a paragraph of explanatory prose before any control, and the wording assumes the model: "socket", "fitting", "cloth", "skin", "composed", "a set names pieces rather than holding them", "one review per piece", "a version cut", `/api/me/library.json` shown on the library page, "pack.mcmeta beside data/". The signed-in library page explains the editor's menu path and an API route in its empty state.

## Screenshots

### desktop-home.png / phone-home.png (/)
Header nav, title "Armor Pieces" with tagline and "Minecraft 26.2 · Fabric · version 0.3.0", then a hero slider of four rendered figures, then sections Outfits (three cards), Packs (one official pack card + a "Yours could be here" card), What it does (pill links), Get it (Modrinth / CurseForge / GitHub buttons), footer. Problems: hero caption drawn over the slider arrows and dots; on the phone the hero crops to one and two half figures and the caption is cut; two of three outfit thumbnails are the grey chest fallback (see cross-page 1). Console: two 503s (outfit renders).

### desktop-gallery.png / phone-gallery.png (/gallery/)
"Gallery" with intro, Featured outfits (three cards, same fallback thumbnails), a Packs 1 / Pieces 107 segmented toggle, one pack card (Browse its pieces / Details / Save), then a collapsed disclosure "The catalogue, for the editor and for pack authors" and a lot of empty space on desktop. Problems: the default view shows one card and a blank page; the toggle counts read as tabs but the badges are unexplained; "The catalogue..." is jargon for a visitor. Console: two 503s, 401 on /api/me/library.

### desktop-gallery-pieces-view.png / phone-gallery-pieces-view.png (+ -top.png crops) (/gallery/?view=pieces)
Same head, Pieces toggle active, a filter row (search, kind, socket, license, pack, author, "107 of 107") and a four-column grid of piece cards with a thumbnail, name, "piece · socket · fittings", "Armor Pieces · All rights reserved", Save / Wear it. On the phone the filter row wraps to three lines and the grid is one column, 55k px tall. The full-page shots were re-taken after scrolling so lazy images loaded; the two broken images are the High Court and Far Road outfit renders (503). Console: 503 x2, 401 x2.

### desktop-gallery-pack.png / phone-gallery-pack.png (+ -top.png crops) (/gallery/packs/armorpieces/)
Breadcrumb "← Gallery", "Armor Pieces official", description, a definition list (Author, Version, License, Homepage, Added, Tags), Download with two purple buttons "Datapack zip (0.1 MB)" / "Resource pack zip (0.2 MB)" and a license callout, "What is in it" with a "Browse its pieces in the gallery" button and a three-column grid of 105 piece cards (no Save/Wear on these). Problems: the grid is the whole pack with no filter and no paging; the install paragraph is dense (datapacks/ resourcepacks/ code spans, "Packs... → From the library..."). Document title is just "Armor Pieces" (no " · Armor Pieces" suffix like the other pages, and the same as the front page). No console errors.

### desktop-gallery-piece.png / phone-gallery-piece.png (/gallery/pieces/armorpieces/aerials/)
Breadcrumb "← Gallery · Armor Pieces", "Aerials", one-line description, a definition list (Kind, Socket, Fittings "armorpieces:inlay", Author, License with an "ARR" badge, Pack, Id in code, Obtained "found in the world"), buttons Save / Wear it / Build a pack from the selection, a license sentence, and a large render on the right (below on the phone), then "Something wrong with this piece? Report it by email." Problems: "Build a pack from the selection" with no selection anywhere in view; "Fittings armorpieces:inlay" is a raw id; the render is a close-up of the head with the piece hard to make out. Console: 401 x2 (library, packs).

### desktop-wardrobe.png / phone-wardrobe.png (/wardrobe/)
"Wardrobe" with a purple "Create new" button top right, a two-sentence intro, Published / Mine toggle, three outfit cards with "Look" buttons, and a note that outfits are kept in this browser without an account. Problems: same two fallback thumbnails; "Look" is a vague verb (Open? View?); the intro ("A set names pieces rather than holding them") is conceptual. Console: 503 x2.

### desktop-library-signed-out.png / phone-library-signed-out.png (/library/)
"Your library" with a five-line explanation of browser-local vs account library, Packs 0 / Pieces 0 toggle, a purple callout "Nothing kept in this browser yet...", a line about the wardrobe and the editor, a collapsed "This shelf as a file" disclosure, and buttons Browse the gallery / Sign in. Problems: empty state is all prose; the two buttons at the bottom are the only actions and sit below a disclosure. Console: 401 on /api/me/library.

### desktop-editor-signed-out.png / phone-editor-signed-out.png (/editor/)
A one-line strip ("Blockbench with the Armor Pieces plugin, running in this tab... Armor Pieces 0.3.0 at 0.3.0-32-ga681235. How to use it · Full screen") then the Blockbench iframe: menu bar, a "New Tab" tab, "Armor Pieces in Blockbench" start page with two callouts (the studio set and "Sign in to the site"), a "your pieces / 1 in the library" toggle, a search box, "Submit a pack..." / "Use my game...", filters "in this browser / any kind / any socket / by socket". The frame is cut off below the filter row (see cross-page 4). On the phone the frame's menu bar is clipped and the content is unusable. Console: three CSP-blocked calls to blockbench.net/blckbn.ch, a 404 script fetch, an uncaught error object, 401 on /api/me/pieces.json.

### desktop-about.png / phone-about.png (/about/)
"About this site", Who runs it, What it is not (the Mojang disclaimer), Where the money is, What the site is made of, Legal, then "Releases" with the whole 0.3.0 changelog inline (thousands of words, code spans, sub-headings) followed by short 0.2.0 / 0.1.3 entries. Problem: the page is 8.9k / 17k px because release notes are appended in full; on the phone it is a wall of text.

### desktop-wiki.png / phone-wiki.png (/wiki/)
Two-column: a search box and a 13-entry page list on the left, "Armor Pieces wiki" article on the right (four-layer explanation, Where to start, A note on words, Edit this page). On the phone the sidebar stacks above the article, so the reader scrolls past the search box and 13 links to reach the content. Clean, no console errors.

### desktop-account-signed-out.png / phone-account-signed-out.png (/account/)
"Sign in" with an explanation, a purple callout "No sign-in provider is configured on this deployment yet. The operator sets the providers' client ids in the environment." (local env only), the agree-to-terms line, and "What an account is for". Note the callout speaks to the operator, not the visitor. No console errors.

### desktop-library.png / phone-library.png (/library/, signed in as "Reviewer")
"Your library", "0 packs of your own, 0 linked, 0 pieces. Storage 0.0 of 52.4 MB and 0 of 20000 files...", a four-way toggle Packs / Pieces / Collections / Outfits (all 0), a purple "New pack" button with an inline sentence of alternatives, "No packs yet.", and a paragraph that quotes the editor's menu path and `/api/me/library.json`. Problems: storage quota shown to a new user before they have anything; the empty state explains an API. On the phone the toggle's counts wrap under the labels.

### desktop-library-packs-new.png / phone-library-packs-new.png (/library/packs/new/)
"← Your library", "New pack", an intro paragraph, fields Slug (hint "letters, digits, hyphens; in the URL"), Name, Description, a purple "Make the pack" button, and a note about linked packs. Problems: the slug field comes before the name and is required, with no auto-fill from the name; "galleryor" is missing a space in the intro ("fill it from the galleryor from your own work"); the pattern is invalid in Chromium (cross-page 3).

### desktop-library-packs-new-filled.png
The same form with slug "review-pack", name "Review Pack" and a description typed in, just before submit.

### desktop-create-pack-result.png (after submitting)
Submit landed on /library/packs/<uuid>/ - the URL uses a UUID, not the slug the user was made to type. Content is the pack page below.

### desktop-library-pack.png / phone-library-pack.png (/library/packs/<id>/)
"← Your library", "Review Pack" with a "private" badge, description, two small grey buttons "Its pieces" / "Export...", then sections Details (Name, Description, Homepage, Visibility select, Save), Contents ("Nothing in it yet..."), Publish (paragraph + "Offer this pack to the gallery..."), Versions (an empty table with headers # Label Holds Contents Cut, then a two-file upload form: Datapack zip, Resource pack zip, Label, "Upload version"), Delete ("Delete this pack", red). Problems: an empty pack shows the full publishing and versioning machinery; the empty Versions table draws its header row over nothing; "Holds", "Cut", "Its pieces" are terse; "Its pieces" is placed as a button beside Export but reads like a heading.

### desktop-library-pack-export.png / phone-library-pack-export.png (Export... clicked)
A centered modal "Nothing to export yet - This pack holds nothing and has no version cut. Add a piece to it first." with a Close button, page dimmed behind. Note the dim only covers the top ~800px in the full-page capture (the overlay is viewport-fixed; not a real issue). The button is enabled on an empty pack and answers with a dead end instead of being disabled or pointing at Add pieces.

### desktop-library-collections-new.png / phone-library-collections-new.png (/library/collections/new/)
"← Your collections", "New collection", a three-line definition ("A collection is a working bag: references, private, never published as such..."), Name, Description, "Make it", and a note about the auto-made "Saved" collection. Problem: the button label "Make it" versus "Make the pack" elsewhere; the concept paragraph is the only explanation of what a collection is.

### desktop-account.png / phone-account.png (/account/, signed in)
"Reviewer" with tabs Profile / Connectors / Account, "Who you are on the site...", Display name input + Save, "Shown as the author of your packs...", "What the name is attached to: Nothing published under it yet...", and a note that there is no avatar or bio. Clean. Nothing here links to sign out (that is presumably under the Account tab, not visited).

### desktop-account-connectors.png / phone-account-connectors.png (/account/connectors/)
Same tabs, Connectors active. Sign-in table (Provider "test", Kind "oauth", What it granted "sign-in only"), Linked packs with GitHub ("The GitHub App is not configured on this deployment.") and Google Drive ("Drive linking is not configured..."), Devices ("No devices." with "Link a device · how to sign the plugin in"). Fine; the two "not configured" lines are local-env only. Raw provider ids ("test", "oauth") are shown as-is.

### desktop-wardrobe-new.png / phone-wardrobe-new.png (/wardrobe/new/)
"← Wardrobe", "Dress a figure", intro ("...underneath.91 pieces" - missing space after the full stop), a large empty grey box "Pick something, and it appears here." with "Show the real figure" / Random / Clear beneath and an explanation of the editor-backed figure; on the right "Armor" with four material selects (helmet/chestplate/leggings/boots = iron) and skin / cloth / cloth colour selects, then per-slot socket rows (helmet: crest, brow, horns; chestplate: pauldrons, back, collar, vambraces; leggings: belt, tassets, knees; boots: spurs, greaves), each "empty" with a "Choose..." button at the far right; then "Wearing it in game" (commands, "Nothing chosen yet."), "The pack for this set" (a purple download button for an empty set), "Keeping it" (Name this outfit, Save the outfit, Save its pieces to my library, Copy a link to it, Add its pieces to a collection..., Make a pack of this outfit...). Problems: on desktop the Choose... buttons are 600px from their labels; the figure box is empty and the two most prominent buttons ("Show the real figure", "Download the pack for this set") act on nothing; six action buttons under Keeping it for an empty set; on the phone the whole thing is a 3.4k px column with the figure box eating the first screen.

### desktop-editor-15s.png / desktop-editor-60s.png / phone-editor-15s.png / phone-editor-60s.png (/editor/, signed in)
Byte-identical at 15s and 60s: the Blockbench start page was fully loaded before 15s (Pyodide is not booted until a piece is opened). Same as signed-out except the second callout now says "Signed in. These are the pieces in your library on the site - 0 of them, across 1 packs and 0 collections..." and the filter toggle reads "in my library / by socket". Same frame-height and phone clipping problems, same console errors (minus the 401).

## Console errors / failed requests per page (deduplicated)

| page | console | failed requests |
|---|---|---|
| / | 2 x "Failed to load resource: 503" | 503 GET /wardrobe/bc27bb...png?w=256, 503 GET /wardrobe/ee7fa3...png?w=256 |
| /gallery/ | same + 401 | the two 503s, 401 GET /api/me/library |
| /gallery/?view=pieces | same + 401 x2 | the two 503s, 401 /api/me/library, 401 /api/me/packs |
| /gallery/packs/armorpieces/ | none | none |
| /gallery/pieces/armorpieces/aerials/ | 401 x2 | 401 /api/me/library, 401 /api/me/packs |
| /wardrobe/ | 503 x2 | the two 503s |
| /library/ (signed out) | 401 | 401 /api/me/library |
| /editor/ (signed out) | 3 CSP violations (web.blockbench.net news.json, blckbn.ch stats, blckbn.ch new_installation), "bad HTTP response code (404) fetching the script", pageerror Object, 401 | CSP-blocked x3, 401 /api/me/pieces.json |
| /about/, /wiki/, /account/ (out) | none | none |
| /library/, /library/packs/new/, /library/collections/new/, /account/, /account/connectors/, /wardrobe/new/ (signed in) | none | none |
| /library/packs/new/ on submit | "Pattern attribute value [a-z0-9][a-z0-9-]{1,39} is not a valid regular expression ... /v: Invalid character class" | none |
| /library/packs/<id>/ (+ export) | none | none |
| /editor/ (signed in) | 3 CSP violations, 404 script, pageerror Object | CSP-blocked x3 |

## What did not work / caveats

- Nothing failed to boot. dist/ was rebuilt first (the last commit touched src/ after the previous build).
- The outfit renders (High Court, Far Road) are missing because SHOTS=off; their cards show a fallback thumbnail, so judge outfit cards by Knight Errant only.
- The gallery-pack and gallery-pieces-view full-page shots were retaken after scrolling; the first pass had grey placeholders below the fold because lazy images never loaded in a static full-page capture. The `-top.png` crops of those two pages are the readable versions.
- The export "dialog" on a freshly made pack is a "Nothing to export yet" notice; the real export options need a pack with a piece or a cut version, which the walk did not create.
- The account's third tab ("Account") and the wardrobe's "Choose..." picker overlays were not opened.
