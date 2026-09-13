# Plan: the UX rounds

> **Status (2026-09-13, evening): Rounds 0, 1, 2 and 3 BUILT** on ArmorPiecesSite. Rounds 0-2
> were a stack of branches and pull requests (`ux-0` = `42f136b` + `bfa6c77` + `e352f0c`, PR #4;
> `ux-1` = `3602eb3`, PR #5; `ux-2` = `c84df78`, PR #6), all three MERGED to main the same evening
> (fa0b1d5 / 1e65cbc / cf1d023) and deployed by their push runs. Round 3 is `ux-3` off `main` =
> `ff3fe14` (PR #7), `npm test` 331/331, the walk 104/104 and 104/104 under WALK_WIDE_FONTS=1; it also needed one commit on
> ArmorPiecesBlockbench `main` (`2da8ef0`, the library index's `requires` and `archive` fields),
> because the site's CI builds the editor from that repo's main. Round 4 is as proposed. Written for the
> next session from the two-pass review in `docs/reviews/site-ux-2026-09-12.md` (32 broken flows,
> numbered there; this plan cites them as **R5**, **R13** and so on). The review was read against
> ArmorPiecesSite `3662d20`; every line number below is from that commit and MUST be re-verified at
> fix time, the site moves fast. Round 0's eight are struck through there; the rest stand. The
> published copy of the review is the artifact
> "Armorpieces.com UX Audit"; the screenshots and both walks' notes are in
> `docs/reviews/site-ux-2026-09-12/shots/`.

## 0. How to run this

The 32 broken items and the seventy-odd friction points share four root causes (section 1), so the
work is five rounds by cause, not thirty-two fixes by item. Each round is:

- **One session, one branch** in ArmorPiecesSite (`ux-0`, `ux-1`, …), merged as a PR when its gate
  is green. The security rounds ran this way and it held (`site-security-round-3.md`, round 4).
- **The gate is `npm test` plus the walk.** Round 0 turns the second walk into a test
  (section 3) so every later round is judged by the same eyes that found the problems. A round is
  not done while the walk test fails, whatever the unit tests say.
- **Re-verify before editing.** Open the cited file, confirm the line still says what the review
  says, then change it. If it moved, fix the review's copy of the line number in the same commit
  so the review stays a map.
- **Mod-side items go through the mod repo**, committed from the published clone
  (`Documents\GitHub\ArmorPieces`, never the working copy). They are marked **[mod]** below and
  belong in the 0.4.0 release, not in a site PR.
- **Scope discipline.** A round fixes its cause. A finding met on the way that belongs to a later
  round is written into that round's list here, not fixed in passing (the review already recorded
  how a release once swept in a concurrent feature: `release-excludes-unreleased-work.md`).
- **Copy as code.** Wherever a sentence promises a number or a state, derive it (the site already
  does this for the mod version, `mod.ts:123-135`). A typed number is a future finding.

Estimated effort, for pacing not for promising: Round 0 an afternoon, Round 1 two sessions,
Round 2 two sessions, Round 3 one session, Round 4 a plan first and then two or three sessions.

## 1. The four root causes

1. **The server knows, the page does not render it.** Verbs and states exist in the API and are
   proven by tests that drive the API and grep HTML for a name, and no page control was ever wired:
   outfit publish (R5), `withheld` (R3), the offer checkboxes (R4), `pendingOf` (R6 friction), the
   ingest report after linking, the reviewer's note on a pack rejection, the empty pack's own
   controls (R2). The tests could not see it because nothing clicks.
2. **One flag where a standing is needed.** Packs and sets carry a `visibility`; the review state
   lives in `publications`. So a rejection leaves the pack `public` (R18), a takedown of a pack or
   outfit is undone by Visibility › Public (R16), the zip route and the thumbnail renderer cannot
   tell a maintainer from a stranger (R13), and an outfit held on a withdrawn piece is told it is
   "waiting on review" (R11). Pieces already have a `withdrawn` standing that sticks (`publish.ts:82`);
   packs and outfits need the same.
3. **Copy that drifted from code.** The privacy and connectors pages (R24), the delete sentence and
   dialog (R22), the download page's promise about reserved pieces (R10), "come back to this page"
   (R21), "open the pack in the editor from its link" (R14), "N versions waiting" (R18), the wiki
   synced from `main` (R26), the hand-typed "Thirty".
4. **Configuration and layout slips.** The CSP token (R30), the sweep's column (R20), the setup
   redirect (R19), the regex `pattern` (R32), the `.gives` grid (R12), the dialog focus (R31), no
   error pages (R28), no road from the mod (R27).

## 2. The rounds

### Round 0: the one-liners

Goal: remove everything that is a single line, in one PR, each with a test, and build the walk test
that gates the rest. Nothing here needs a design decision.

| Item | Review | File (re-verify) | Change | Test |
|---|---|---|---|---|
| Wiki search | R30 | `server.mjs:34` | add `'wasm-unsafe-eval'` to the SITE `script-src` (the editor CSP at `:40` already has it) | walk: type "skin" on `/wiki/`, expect a result |
| Audit prune | R20 | `scripts/sweep.mjs:289,292` | `created_at` → `at` | a sweep test that inserts an old audit row and sees it go |
| GitHub App return | R19 | `api/github/setup.ts:18,27` | redirect to `/account/connectors/#github` and `/account/connectors/?github=cancelled`; Connectors reads the query and says "installed" / "cancelled" | `links.test.mjs`: assert the redirect target |
| Link page callback | R21 | `link/index.astro:17`, `account.js:47` | the signed-out notice's sign-in link carries `callbackUrl=/link/?code=…`; the sign-in buttons honour a `data-callback` | `accounts.test.mjs`: sign-in from `/link/?code=X` lands back on it |
| Code length hint | R21 | `link/index.astro` | say "eight characters, ABCD-EFGH" beside the field; validate on input, not only on submit | walk: bogus 6-char code shows a sentence |
| The five `pattern`s | R32 | `NewPackForm.astro:33`, `connectors/index.astro:72,88`, `gallery/build.astro:39`, the pack page | `[a-z0-9][a-z0-9\-]{1,39}` (hyphen escaped) | walk: zero "Pattern attribute value" console errors |
| Outfit page width | R12 | `global.css:273-274` | `.gives > * { min-width: 0 }` or `overflow-x: auto` on the grid child | walk: `scrollWidth == clientWidth` on `/wardrobe/armorpieces-knight_errant/` at 1280 and 400 |
| Banner fitting | R12 | `OutfitDetail.astro:95` | render an object fitting as its keys ("base, N patterns") | `wardrobe.test.mjs`: no `[object Object]` in the page |
| "someone" on composed | R10 | `api/compose.ts:70` | official pieces credited to the mod's name (`site.ts` has it) | `objects.test.mjs`: compose an official piece, read the credit |
| Missing spaces | walk | `Base.astro:60`, `OutfitDetail.astro:38`, `queue/index.astro:78-79` | "the Armor Pieces License", "cloth. One of", "terms (all ages" | walk: grep the three strings |
| Confirm-dialog focus | R31 | `ui.js:96-124` | initial focus on Cancel (the non-danger action); `finish()` restores focus to the opener | walk: open "Delete this pack?", read `document.activeElement`, press Escape, read it again |
| Second h1 | R29 | `content/wiki/authoring.md:7` **[mod: `docs/authoring.md`]** | drop the `# Authoring parts` line; "part" → "piece" in the intro | `site.test.mjs`: one `<h1>` per wiki page |
| "Thirty" | reader | `content/wiki/getting-started.md:19` | read the count from `content/mod/site.json` | `site.test.mjs`: the sentence equals the count |
| Contact block | R27 | `src/main/resources/fabric.mod.json` **[mod]** | `"contact": { "homepage": "https://armorpieces.com", "sources": …, "issues": … }`; `modpage.yml` `links.website` | modpage build; the README header names the site |

Done when: `npm test` green, the new walk test green, and R12, R19, R20, R21, R29, R30, R31, R32
are struck through in the review file with the commit hash.

**Built 2026-09-13 as `42f136b`.** Notes for the rounds after it: the walk runs in 55 s, 82 tests;
the pack page in the R32 row was a false trail - its console error was the New pack form's, carried
over by `UI.become` - and the fifth pattern was the pack page's *Add a piece* id (a `/` in the
class). Two more overflows at 400 px came out of the walk (a wiki table, inline code paths) and
went in the same commit. "Thirty" is a Sätteri plugin (`scripts/counts-plugin.mjs`), not remark:
Astro 7's processor has no remark hook without `@astrojs/markdown-remark`; rendered Markdown is
cached by digest in `node_modules/.astro/data-store.json`, so a plugin change needs that file
deleted. The [mod] items are in the mod's working copy, uncommitted, for the 0.4.0 commit: the
`contact` block, `links.website`, and the guide's intro; the README was rebuilt. The composed page
reads the credit from the recipe on disk, so a recipe written before this round still says
"by someone" until the sweep retires it.

**Built, second commit, `bfa6c77` (2026-09-13, the CI fix).** PR #4's run showed what `main`'s
own run at `3662d20` had already shown: `pieces.test.mjs` and `uploads.test.mjs` fail on a 429 on
the Linux runner, where a Pyodide edit is fast enough to empty the `edit` and `upload` buckets,
and pass here, where each edit is slow enough for them to refill. **The deploy is on push to
`main` and stops on a red build, so nothing after `337e38e` reached armorpieces.com.**
`RATE_LIMIT_SCALE` multiplies every bucket (`src/lib/limits.ts`); the two authoring suites set it
to 10, `site.test.mjs` (which asserts on a 429) does not, and no deployment sets it. The walk then
found three pages 27-36 px too wide at 400 under the runner's fonts (the view toggle, the pack
page's facts with a URL, the owner's pack form whose grid column took the select's longest option
as its minimum). `WALK_WIDE_FONTS=1` draws the walk in a wide monospace so a Windows machine can
find what Linux would; run it before pushing a round. A third commit, `e352f0c`: the workflow's
concurrency group was one `deploy` for every run, and GitHub keeps one PENDING run per group, so
pushing three stacked branches a minute apart cancelled two of the three runs; it is
`deploy-${{ github.ref }}` now - main still deploys one at a time.

### Round 1: show what the server already knows

Goal: every API verb has a page control, and every page control has a test that clicks it. No new
server behaviour except where a route needs one field it does not accept yet.

1. **Outfit publish (R5, R6, R11 in part).** On the outfit page and the wardrobe's Mine card:
   Publish, Unlisted, Private, Rename, Delete, wired to `POST /api/me/sets` with `id`, `visibility`
   and `publishAndGo`; the 422 `unresolved` list rendered as sentences ("Antennae is yours and not
   in the gallery: publish it with the outfit?" / "Comb is somebody else's: swap it out"); the
   reviewer's note from `publications` shown on the card after a rejection (`outfits.ts:79-82`
   clears the flag; read the note before clearing, or keep the row's id on the set). The outfit
   page passes its `id` into the draft (`OutfitDetail.astro:124` JSON gains `id`; `wardrobe.js:302`
   sends it), and `/wardrobe/new/?from=<id>` loads that set (`LibraryBody.astro:269`).
2. **`withheld` (R3).** Render `withheldOf` on the pack page beside the version links and in the
   Publish section ("3 of 12 pieces are not in the public zip until they are approved"); reword
   `LibraryPackDetail.astro:107`. Same list on the maintainer's group header (Round 2 reads it too).
3. **The offer checkboxes (R4).** Either `publish.js:164-168` sends `keep: [hashes]` and
   `filePackPublication` honours it, or the checkboxes go. Recommendation: send them, the server
   already computes per-piece rows.
4. **`pendingOf` (R6 friction).** `publish.ts:256-264` is computed for the GET; render it under
   the pack's Publish section ("waiting on: Great Helm, Comb").
5. **The empty pack (R2).** Move the picker, *Copy in*, Credits and the editor links out of
   `data-contents` (`LibraryPackDetail.astro:47,113-116`); ask licence and author on
   `NewPackForm.astro`; put an "Upload a pack (zip)" entry on Library › Packs and on New pack that
   opens the same import as the collection page (the route stays `collections/:id/import`; the
   page picks or makes the collection).
6. **The ingest report (account friction).** `link-github.ts:19` returns it; show "N pieces read,
   N dropped, because…" after linking and after refresh, and the dropped reasons after a collection
   import (`collection.js:65-72`).
7. **Rejections reach the author (R17 in part).** A pack-row rejection renders as "turned down –
   note" like a piece's (`LibraryPackDetail.astro:220-232`); `withdrawn` gets a sentence in both
   `says` maps (`LibraryPackDetail.astro:53-60`, `CollectionDetail.astro:38-45`); "N versions
   waiting" becomes "N items waiting" counting groups (`account/index.astro:30-36,91`).
8. **The picker's data (R7, R8, R9).** `/api/pieces` returns `packId` and a thumbnail for gallery
   rows (`api/pieces.ts:32-34,82`); the socket stores the real pack id and the hash; Random picks
   from the same rows so it carries hashes; "Save its pieces" sends the id. Pieces chosen from a
   collection or own pack are added to the page catalogue on pick (a fetch of the card), so a
   socket never reads "empty".
9. **Tests.** Each control above gets a Playwright test in `test/pages.test.mjs` (section 3) that
   clicks it and asserts the request and the rendered result. The existing API tests stay.

Done when: an outfit made in the walk reaches the Published tab through the page after a
maintainer approves it; R2, R3, R4, R5, R6, R7, R8, R9 struck through.

**Built 2026-09-13 as `0a9a480`** (`npm test` 310, the walk 100/100; the API half is
`test/ux-round-1.test.mjs`). What it found on the way:
- The round's one new route is `PATCH /api/me/sets { id, name?, visibility?, publishAndGo? }`:
  the verbs on a card carry an id and nothing else, and shipping every set's JSON on every card to
  feed POST was the wrong shape. The gate is one function (`publishGate`, `lib/outfits.ts`),
  thrown as `Unresolvable` and answered 422 by both verbs.
- The reviewer's note lives on the set (`sets.note`, migration `0015_outfit-note`), written by
  `resolvePendingFor` and cleared by the owner's next visibility decision. Round 2's `standing`
  should reuse the column rather than add a second note.
- R11's "pending forever" had a second cause the review did not name: the admin route ran
  `resolvePendingFor` only on an approval, so a rejection never reached the outfit. It runs on both
  now; the `withdrawn` half is still Round 2.
- The flip to public re-filed the version: `setVisibility` calls `filePackPublication`, and the
  publish route called both, so sending `keep` alone would have queued the unticked pieces a
  moment later. `setVisibility(…, file = false)` from the publish route.
- The signed-out wardrobe is cached a minute (`max-age=60`) and the walk's contexts are reused, so
  a test that publishes and then reads `/wardrobe/` signed out must ask past the cache.
- The client scripts are served from `dist/client`: an edit under `public/` shows only after
  `npm run build`, and a walk run against a stale build fails in ways that look like code.
- `jsonCall` in `account.js` always sends a body; a GET through it throws in Chromium. Use
  `UI.call` for reads.
- The picker's "Reload to see it in the table" after a pick is still there (Round 4, `UI.again`).

### Round 2: one standing per subject, and the maintainer's bytes

Goal: packs and outfits carry a standing the way pieces do, every surface reads it, the maintainer
sees what they are judging, and people are told.

1. **A `standing` on packs and sets.** `null | 'withdrawn'` (plus the note and the reviewer),
   written by `withdrawPackEntry` and `withdrawOutfit` (`takedown.ts:110-133`), cleared only by a
   maintainer's restore (`api/admin/takedown.ts:30` says restore "does not exist by design" for
   these; it exists now, as the reverse). `setVisibility` refuses `public` while withdrawn
   (`packs.ts:180`); `saveSet` refuses too. The owner sees "taken down: <note>" where the pill was.
   A rejection of the pack row also sets `visibility: 'private'` (`publish.ts:220-244`) so R18's
   "public but rejected" cannot exist. Outfits resolve on `withdrawn` as well as `rejected`
   (`outfits.ts:76-78`), and an own piece dressed without a hash is filed by id.
2. **The maintainer's bytes (R13, R14).** `hostedZip` takes `asker: { id, maintainer }` and hands a
   maintainer the whole version (`packs.ts:343-352`; the route `[version].zip.ts:28` passes the
   actor); `renderThumbnailsFor` also runs at filing time into a `pending/` folder the queue reads
   (`thumbnails.ts:25-38`); a per-object download for loose submissions
   (`piece.zip.ts:33-35` allows a maintainer). Drop the "open in the editor" sentence
   (`queue/index.astro:78`) or link `/editor/?piece=<hash>` if the editor can open by hash.
3. **The group header shows what is judged.** Pack author and homepage, the already-published
   objects, `withheld`, `lineage` / `formerIds` per piece ("forked from X by Y"), the reporter of a
   report, and a *Reject all* beside *Approve all* (`publications/[id].ts`, `queue.js`).
4. **Takedown from the piece page (R15).** For a maintainer, a *Take it down* / *Put it back*
   button on the piece, pack and outfit pages posting the hash or id itself; the hash box on the
   queue goes. Report subjects become links (`queue/index.astro:141`).
5. **Telling people (R17).** No e-mail. An `events` view over `publications`, `audit` and
   `reports` per user: "Great Helm was turned down: <note>", "Your pack Coral was taken down:
   <note>", "Your report on X was upheld / dismissed". Rendered on `/account/` above the fold with
   a count, and a maintainer's nav item "Queue (3)" (`Base.astro`, reading the queued count).
   `account/index.astro:59` "No badge" goes.
6. **Featuring.** *Feature it* on the queue's group header and on pack pages for maintainers;
   `featured.ts:11-12` gains packs.

Done when: the walk's maintainer downloads a version with the new pieces in it; a rejected pack is
private; a taken-down outfit cannot be re-published by its owner; R11, R13, R14, R15, R16, R17, R18
struck through.

**Built 2026-09-13 as `c84df78`** (site branch `ux-2` off `ux-1`, PR #6; `npm test` 323, the walk
104/104 and 104/104 under `WALK_WIDE_FONTS=1`; the API half is `test/ux-round-2.test.mjs`).
Decisions taken with the user first: in-site events, not e-mail; featuring packs in this round.
What it found on the way:
- **The standing** is `packs.standing` + `standing_note` and `sets.standing` (migration 0016);
  the outfit's note reuses `sets.note`. A restore hands back the RIGHT to publish, not the
  publication: the pack's head row stays `withdrawn`, the owner re-offers, a new `pack` row is
  filed and the maintainer approves it again, while the pieces - reviewed once, ever - are skipped
  as "already in the gallery". A test that expects the pack back in the gallery after a restore
  must approve that second head.
- **The thumbnail renderer is a stranger to the zip route** (a child process with no credentials,
  by design), and a stranger is handed a queued version minus exactly the pieces under review. A
  render grant (`lib/grants.ts`: one random token, one version, ten minutes, in-process) rides on
  the zip URLs the renderer is given; `[version].zip.ts` reads it as "a maintainer is asking". The
  pending pictures land in `data/thumbs/pending/<hash>.png`, are served by `/api/admin/thumbs/`
  to maintainers alone, and the approval copies them into the per-pack folder instead of
  rendering twice. `renderingOff()` (SHOTS=off) is honoured now; it was not, and every test
  filing a pack would have spawned Chromium.
- **The gallery pages are public-cached (`max-age=60`) and session-blind**, so the maintainer's
  verbs are drawn on the client (`public/moderate.js`) into `data-moderate` slots after one
  `/api/whoami` - a route that always answers 200, because `/api/me`'s 401 for a visitor is a
  console error on every piece page and the walk counts those. The routes check again; a slot is
  a place, not a permission. The pack page's slot names the pack's uuid parsed off its own zip
  URL: the public catalogue does not carry `packId` on purpose.
- **A loose published object has no gallery page** until a pack lists it: `variantsOf` is over
  the merged index. The walk's takedown test had to publish the walk pack first.
- **`UI.working` puts the button's label back when the job ends**, so a verb that changes its
  own label sets it after `await UI.working(...)`, not inside.
- **"Queue (N)" is the middleware's** (`context.locals.queued` for a page request carrying a
  session cookie, `App.Locals` in `src/env.d.ts`); a prerendered page (the wiki) never sees it.
- The other session's five uncommitted "requires" files were kept out of the commit by saving
  `git diff` to a patch before editing, `git apply -R -C1` before the commit, `git apply -C1`
  after; a rebase of a checked-out branch needs `git stash` around it.
- The bash tool eats one backslash per heredoc level again: a Python edit whose replacement
  text carries `\s` or `\(` must be a file run with `python file.py`, or the regex lands wrong.

### Round 3: make the copy true

Goal: every sentence about storage, deletion, linking and downloads matches the code, and the
three account seams are closed. Needs the decisions in section 4.

1. **Delete (R22).** `settings/index.astro:50` and `account.js:100` say exactly what goes: with
   "keep" ticked, identities, sessions, tokens, private and unlisted packs and unapproved public
   packs go and the name stays on the published ones; unticked, everything and the account row.
   `accounts.test.mjs:339-355` asserts the row, not a 401.
2. **Storage truth (R24, R25).** Privacy, Connectors and Profile list tokens (kept for GitHub
   organisation checks and Drive refresh), the avatar URL, the device-code IP, `gh_state`, the
   Picker; or the Microsoft `profile` override drops the photo and tokens are dropped after
   sign-in where nothing reads them. Microsoft: verified e-mail only, `allowDangerousEmailAccountLinking`
   like the others (`auth.config.ts:65`). Show the stored e-mail on Profile. Add "sign out
   everywhere".
3. **Linked packs (R23).** A "my own work" tick on both Connectors forms, default off, passed to
   `ingestIntoPack` (`packs.ts:161`); the comment matches the code. A `linked` pill on own-pack
   cards; a `source` state on the pack page (ok / unreachable / grant gone / App uninstalled),
   computed on view from the last refresh's outcome; an *Unlink* verb that deletes the pack's
   source fields and, when no other pack uses it, the installation row.
4. **The dressing room's download (R10).** Either the composer skips reserved pieces and the page
   lists them ("left out: Antennae, all rights reserved"), which is what `new/index.astro:142`
   promises, or the sentence says it refuses. Recommendation: skip and list. The button becomes
   *Build the pack…* and opens the composed page in place, named after the outfit.
5. **Downloads say what they need (R9 in the review's fix list).** "Requires Armor Pieces X on
   Minecraft 26.2" on the pack page, the composed page, the outfit page and `/gallery/index.json`,
   sourced from where `assemble.ts:199,280` stamps it. A both-halves zip for the official pack with
   `Content-Disposition`. The public pack page lists versions with per-version downloads.
6. **Small truths.** "Link a device" says what to do without a code; the five "account page"
   mentions point at Connectors; "linked" on the library page becomes "saved"; `cookies.astro`
   lists `gh_state` and the Picker; "announced on the account page for thirty days" gets the
   events list from Round 2 or goes.

Done when: a reader can compare each policy page against `schema.ts` and find nothing missing;
R10, R19 (the Connectors half), R22, R23, R24, R25 struck through.

**Built 2026-09-13 as `ff3fe14`** (site branch `ux-3` off `main`, PR #7; `npm test` 331/331, the
walk 104/104 and 104/104 under WALK_WIDE_FONTS=1; the API half is `test/ux-round-3.test.mjs`, the linked-pack half is three tests
added to `test/links.test.mjs`, which owns the GitHub and Drive mocks). Item by item:

1. `deleteAccount` is the sentence now: always the sign-ins, sessions, device tokens, App
   installations, saved packs, collections, unpublished packs, non-public outfits and the e-mail;
   ticked, the approved packs and public outfits stay under the name on a husk row (decision 2 -
   the outfit pages and the catalogue read `users.display_name`, so the row IS the name);
   unticked, the row and everything by cascade. Settings and the dialog say exactly that, and the
   dialog's sentence follows the tick.
2. `auth.config.ts` stores what is read and nothing else: `image: null` on every provider
   (Microsoft's default fetched the photo as base64), the adapter's `linkAccount` wrapped by
   `keptIdentity` (GitHub keeps its access token for the organisation check, Google its refresh
   token for Drive; id token, session state, expiry and token type are dropped), and an
   `events.signIn` that writes the fresh token back - which is also what makes *Allow Drive* work
   for a Google-first account, since Auth.js never updates an existing account row. Microsoft
   hands over no e-mail at all (Entra's claim is unverified, the nOAuth class) and no `User.Read`
   scope. The privacy table is rewritten row by row against `schema.ts` (tokens, no avatar, the
   device code's address, reports, the picker as the one third-party script), the cookie page
   lists `gh_state` and the picker, Profile shows the stored e-mail or says there is none,
   Connectors says per identity what is kept, and *Sign out everywhere* is `DELETE
   /api/me/sessions`. The export names each identity's scope and WHICH token it holds, never the
   token, plus installations and reports.
3. "My own work" ticks on both Connectors forms, default off, `own` through the link routes to
   `createLinkedPack` and into `sourceMeta.own` for every later refresh (decision 3; the comment
   that said the opposite of the code is gone). `refreshLinked` writes `sourceMeta.lastRead`
   either way, and `sourceState()` computes ok / unread / unreachable-since / grant gone /
   installation gone on view; the pack page shows it with a way out. `POST
   /api/me/packs/:id/unlink` makes the pack hosted and forgets the installation row when no other
   pack of the account reads through it. Own-pack cards carry a "linked to GitHub/Drive" pill,
   and a saved pack is "saved", not "linked" (`data-held="saved"`, both filters, the piece cards).
   Found on the way: the publish route's `ownPack` guard refused every linked pack ("edited where
   it lives"), so *Offer this pack* was dead on them; it asks `minePack` now.
4. `/api/compose` leaves a reserved piece OUT and lists it (`meta.leftOut`, with the gallery entry
   id of the author's own pack - the namespace alone linked to a page that did not exist, for
   composed credits too); the zip's `wear.mcfunction` dresses only what the zip carries, since a
   /give naming a missing part fails the whole stack. Only an outfit with nothing composable is
   refused. The button is *Build the pack…*, the composed page is a `[data-detail]` component
   (`ComposedDetail.astro`) that answers `?partial=1`, and the dressing room opens it as a sheet.
5. The five "requires" files adopted as they were (PackDetail's *Needs* row and archive branch,
   the gallery cards, `entryOf`'s `requires`, the assembler's `armorpieces.requires` stamp,
   `LibraryEntry.archive/requires`). On top: the composed meta carries `requires` and the page
   says "Needs the Armor Pieces mod, X or later, on Minecraft Y"; the outfit page says the same
   before its commands and links the dressing room with `?from=`, which now also opens somebody
   else's public outfit; `approved()` groups per pack (a pack approved twice was two entries under
   one id) and the entry lists `versions[]` with datapack / resource pack / both-in-one per
   approved version, which the public pack page draws under *Earlier versions*. The "both-halves
   zip for the official pack" half of this item is superseded by the archive decision: the mod's
   own entry has no download at all.
6. The link page says what to do without a code (the menu path, the wiki anchor); "account page"
   mentions point at Connectors or Settings (link page, terms, the site's own `content/wiki/editor.md`);
   the privacy page's "announced on the account page for thirty days" is gone (nothing announced
   anything) in favour of the dated line and the release notes.

Traps: the site's `content/mod/library.json` is gitignored and synced from the editor build, so
`archive: true` reached it only after `node build/make_library.mjs --out dist/site/library` in
ArmorPiecesBlockbench and a copy of the one file - not `npm run sync`, which from the working copy
breaks two suites (`storage-plan-built.md`); CI does it right because it builds the editor from
that repo's main, which is why `2da8ef0` had to land there. A linked pack's page draws no
contents table, so ownership is observed through the offer (`filed` against `skipped` "somebody
else's piece"). `npm test` outruns the tool's ten-minute cap and was run detached
(`Start-Process cmd /c npm test > log`). `astro check` is not installed here; `npx tsc --noEmit`
has five pre-existing errors and no new ones.

### Round 4: the design work (plan first)

Goal: the layouts that need designing rather than fixing. Write `docs/plans/ux-round-4.md` in the
site's plan voice before building, with the screens as ASCII or shots, because these change what a
page is, not what a line says.

1. **Error pages (R28).** `404.astro` and `500.astro` in `Base` with the nav, a sentence and a link
   back; the detail routes render them instead of `new Response('No such …')`; `server.mjs:124-127`
   serves the built 404; the queue's 403 is branded; `overlay.js:134-137` shows a notice in the
   sheet instead of navigating.
2. **The picker as a sheet.** `picker.js` becomes an overlay-layer sheet (the site has one,
   `site-overlays.md`) that names its socket, has Close, returns focus, and shows thumbnails.
3. **The outfit page.** A Download (both halves, from `/wardrobe/<id>/pieces.zip` or the composed
   pack), a Copy per `/give`, a report form on official outfits pointing at contact, and the
   command block inside the card grid rather than below it.
4. **One "Make a piece" page for `/editor/`.** Browser versus desktop, where work is kept, sign-in
   state, the three steps make → pack → offer, a taller frame, a phone-width notice, and a
   persistent "in this browser only" state on start-page cards. The plugin's *Submit…* and the
   start page's *Submit a pack…* are retired for *Upload to your library…* plus a link to the pack's
   Publish section (R1 lives here too: `LIBRARY_SITE` defaults to armorpieces.com and *Sign in to
   the site…* fails with the setting named).
5. **One place to manage a piece.** A piece sheet reachable from every Pieces-tab card: name,
   licence, author, former ids, publish / withdraw, review state with the note. "Reload to see it"
   becomes `UI.again`.
6. **Versions.** Delete guarded like the cut; *Upload version* folded into the cut flow; a
   changelog field.
7. **Previews, keyboard, weight.** Open Graph and Twitter meta in `Base.astro` with a per-page
   image; canonical; `robots.txt`; a sitemap; a releases feed. A focus trap or `inert` for the
   sheet; `aria-live` on `ui.js:285-289` status lines; plain links instead of `role="tab"`; a pause
   button on the slider. WebP thumbnails with `srcset` from `thumbs/[file].ts`; compressed heroes;
   Pagefind loaded on focus.
8. **Wiki content [mod for `authoring.md`].** An "Installing a pack" section with "reopen the
   world"; FAQ entries for: which mod version a pack needs, why a piece is missing from the public
   zip, where an upload went, whether downloading needs an account, why a new pack shows nothing
   until the world is reopened; the changelog page points at `/about/#releases`; a community link
   once the Discord server exists (`discord-repo.md`).

Done when: R1, R28 struck through and the friction sections of the review re-read with each line
either fixed or explicitly kept.

## 3. The walk as a test

Round 0 builds `test/pages.test.mjs`: Playwright 1.63 (already a dependency) against the test
server the other suites use, with the recipe from `WALK2.md` (`NODE_ENV=test`, `TEST_LOGIN_SECRET`,
`AUTH_SECRET`, `AUTH_TRUST_HOST`, `SHOTS=off`, `scripts/migrate.mjs` first). Three identities
(signed out, a plain user, a maintainer) at 1280 and 400 px. For every page in a fixed list it
asserts:

- status 200 (or the documented redirect), `scrollWidth == clientWidth`, no console `error`
  except the allowed set (the shelf's 401 probe, the 503 renders under `SHOTS=off`, the editor's
  blocked telemetry), no "Pattern attribute value" message, every button and link labelled;
- on `/wiki/`, typing "skin" yields at least one result;
- on each of the five error URLs, the response is HTML with the nav and a link (after Round 4);
- on "Delete this pack?", `activeElement` is Cancel on open and the opener after Escape;
- the outfit page has a control whose href ends in `.zip` (after Round 4);
- the strings "theArmor", "cloth.One", "terms(all" do not occur.

It runs in `npm test`. It is slower than the unit suites; keep the page list fixed and the
assertions cheap so it stays under a minute. The screenshot pass (`scripts/shots.mjs` style,
writing to `docs/reviews/...` in the mod repo) stays a manual tool for reviews, not a test.

## 4. Decisions for the user, with a recommendation each

All five were taken on 2026-09-13: 1 in-site events (built in Round 2); 2 keep the husk row; 3 unowned
unless ticked; 4 leave the wiki alone and ship 0.4.0 instead - no stamp, no pin; 5 publishable (built in
Round 2). Round 3 item 4 (the dressing room and a reserved piece): build the zip and list what was
left out, with a link to each reserved piece's own pack.

1. **Notifications: in-site list or e-mail?** Recommend the in-site events list (Round 2). No
   mail provider, no bounce handling, no new privacy sentence. E-mail can follow if authors ask.
2. **The deleted user's husk row under "keep my published packs".** Recommend keeping it, since
   the packs need an author name and `orphanedCredit` already carries it; the fix is the sentence,
   not the row. Alternative: delete the row and rely on `orphanedCredit`, which loses the
   maintainer's audit trail to that user.
3. **Linked packs: owned or not?** Recommend unowned by default with a tick, matching the
   collection import. A tick that defaults on is the current bug with a checkbox.
4. **The wiki until 0.4.0 ships: pin the sync to `0.3.0` or stamp the pages?** Recommend a stamp
   ("This page describes Armor Pieces 0.4.0, unreleased; the gallery's pack is 0.3.0") in
   `Wiki.astro` when `content/mod/gradle.properties` and the synced tag disagree. Pinning to 0.3.0
   would also roll back `authoring.md` and the tool list that the plugin work depends on. The real
   fix is shipping 0.4.0 (`main-pack-split.md`: "finish it and ship no content at all"), which also
   closes "requires 0.4.0" on every download surface.
5. **Should outfits be publishable at all, or only featured by a maintainer?** Recommend
   publishable: the gate, the review flip and the tests exist; only the page is missing.

## 5. Order and the first session

Round 0 first, in one session, ending with the walk test green and the review file's numbers
struck through (done). Then Round 1 (done, `ux-1`) and Round 2 (done, `ux-2`) in either order
(Round 1 is the visible win, Round 2 is the structural one; Round 2 touches `publications` and
`takedown.ts`, which Round 1's outfit-publish also reads, so if both run in parallel sessions,
Round 2 owns those files). Round 3 after both: it needs decisions 2, 3 and 4 of section 4, and
the other session's five "requires" files (`assemble.ts`, `packs.ts`, `library.ts`,
`PackDetail.astro`, `gallery/index.astro`, uncommitted in the site checkout since 2026-09-13
02:46) are its item 5 half-done - Round 3 adopts them rather than working around them. Merge
#4, #5 and #6 first, in that order, and branch `ux-3` off `main`. Round 4 begins with its plan.

The first session's brief, in one line: *check out ArmorPiecesSite, branch `ux-0`, build
`test/pages.test.mjs` from `WALK2.md`, watch it fail on the search, the overflow, the patterns and
the dialog focus, then fix the Round 0 table until it passes, and strike the numbers through in
`docs/reviews/site-ux-2026-09-12.md`.*
