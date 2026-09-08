# Plan: the website

Section 5 of `0.4.0.md` sketched "the part website" and said it would get a plan of its own when
its turn came. This is that plan. It covers the whole site the user described on 2026-09-06:

- a main page, and a wiki;
- a public gallery of packs and pieces;
- a personal library per user, of pieces and packs, either hosted by the site or linked from
  GitHub, Google Drive or a local folder, with a license on every piece;
- both libraries reachable from the Blockbench editor, on the web and on the desktop, so a pack
  in an account can be selected and managed in the app;
- secure, with sign-in through third-party providers only;
- money only in ways the Minecraft Usage Guidelines allow, no advertising, and the mod's own
  downloads pointing at Modrinth and CurseForge;
- a cookie policy a visitor does not have to click through.

It is written the way the other plans are: what exists, what is missing, what changes, and how to
tell it is done. The decisions that are the user's to make are collected in one section and each
comes with a recommendation, so that the rest of the plan can assume them.

---

## Today

Everything below is real and tested; none of it is reachable from the internet.

- **The hosted editor.** `ArmorPiecesBlockbench` serves a pinned Blockbench 5.1.6 web build that
  loads the desktop plugin unchanged and runs the repository's Python under Pyodide. A start page
  of its own lists the pieces and skins of the mounted pack. Work persists in IndexedDB; on
  Chromium a pack can be linked to a real folder. Three test suites cover it.
- **Pack management** in the plugin is one implementation over six platform functions, and the
  list of *sources* (`packSources`) is the seam this plan hangs on: a source has `install(dest,
  done)` and `publish(dir, done)`, the manager renders whatever is registered, and a platform can
  contribute sources through `window.ArmorPiecesPlatform`.
- **The library** is a static index of author-hosted zips, one entry so far (the mod's own,
  mirrored because release assets have no CORS). The plugin reads it from a URL in a setting on
  both platforms. Submit is a prefilled GitHub issue; approve is a label and a workflow that
  validates each zip with `import_pack.py` and opens the PR.
- **The store pages.** `modpage.yml` renders the README and the Modrinth and CurseForge pages;
  the gallery pictures are shot in the game. `docs/authoring.md` is the only other prose.

Two facts about the current state decide the first two things this plan does:

1. **The repository is private, and Pages will not serve a private repository on the free plan.**
   The CI workflow builds and tests and then fails at deploy. Nothing here needs Pages, though:
   a site deployed from CI to a host of its own works from a private repository.
2. **`web/repo.tar.gz` contains the game's own textures.** The bundle carries
   `tools/.mcassets/` (the vanilla armor, leggings and banner sheets, extracted from the client
   jar) because the figure the editor shows wears real armor. The usage guidelines say "do not
   redistribute our games or any alterations of our games or game files", and a public URL
   serving that tarball would do exactly that. Being private has hidden it. Before any public
   deploy the vanilla textures have to leave the bundle; how is in section 2.

---

## What is missing

Reading the wish list against what exists:

| wanted | exists | missing |
| --- | --- | --- |
| main page | store pages from `modpage.yml` | a site to put a page on |
| wiki | `docs/authoring.md` | rendering, navigation, search, a way to edit |
| gallery of packs | the library index and its start-page tab | pictures, a page of its own |
| gallery of pieces | nothing: the index knows zips, not pieces | a per-piece manifest and a thumbnail per piece |
| personal library | IndexedDB in one browser | accounts, storage, versions, visibility |
| linked packs | Link a folder (Chromium) | GitHub and Drive as sources |
| license per piece | one license per pack, as a string in the entry | a place in the pack format for it, and tooling that carries it |
| editor ↔ account | the `packSources` seam | an `account` source, and a sign-in the desktop can do |
| compose a pack | `import_pack.py`, `export_pack.py` | a cherry-picker, and the licenses to say what may be picked |
| security | none needed for a static page | everything in section 5 |
| money | Modrinth and CurseForge listings | the site pointing at them; a sponsor link; nothing else |
| cookies | none set | a session cookie, and a page that says so |

---

## Decisions

Each is the user's. The recommendation is what the rest of this plan assumes.

1. **Name and domain.** The site is "Armor Pieces" at a domain without the word Minecraft in it.
   The guidelines allow "Minecraft" only as a secondary name and only where the domain is not
   used "principally to make money, including through affiliate services"; leaving it out
   removes the question. Every page carries the disclaimer the guidelines require, in the footer:
   *NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.*
2. **A third repository, `ArmorPiecesSite`, private.** The site holds server code, a database
   schema and secrets, none of which belong beside a GPL Blockbench build. `ArmorPiecesBlockbench`
   keeps building the editor exactly as now, and the site consumes its `dist/site` as a build
   artifact mounted at `/editor/`. Same origin, so the editor shares the site's session cookie and
   no cross-origin token flow is needed in the browser. The static library moves into the site's
   database, seeded from the one entry that exists; `/library/index.json` keeps its shape, so the
   plugin's library source keeps working by changing one URL, which is what
   `armorpieces-pack-library` said moving it would cost.
3. **Stack.** One TypeScript application: Astro for the content pages (main page, wiki, gallery)
   with server endpoints for the API, Auth.js for sign-in, Postgres through Drizzle, and
   S3-compatible object storage for zips and thumbnails. The server runs the repository's Python
   the same way the browser does: under Pyodide, in node, which `build/test_pyodide.mjs` already
   demonstrates. That is what keeps "no second implementation" true on the server too: an
   uploaded zip is validated by `import_pack.py`, a composed pack is built by `pick_pieces.py`,
   and a thumbnail is a screenshot of the real editor taken by Playwright.
4. **Hosting.** A container on Fly.io in Amsterdam, with Fly Postgres and Cloudflare R2 (EU
   jurisdiction) for objects; Cloudflare in front for TLS and rate limiting. The alternative is a
   Hetzner box with Docker Compose, which costs the same and needs patching. Either keeps the
   data in the EU, which the privacy page then says. Vercel, Pages and Workers are out because
   the server needs Pyodide and headless Chromium.
5. **Sign-in providers.** GitHub, Google, Discord and Microsoft, through Auth.js, OAuth with PKCE,
   nothing else: no passwords, no magic links. A user is a row keyed by provider and subject id;
   the display name comes from the provider and can be changed; the email is kept only if the
   provider gives one and is used for nothing but account recovery and abuse contact.
6. **Where a piece's license lives.** A file the game ignores, at the pack root:
   `armorpieces-credits.json`, with a pack-level default and a per-piece override:

   ```json
   {
     "pack": { "author": "somebody", "license": "CC-BY-4.0", "homepage": "https://..." },
     "pieces": {
       "somebody:great_helm": { "license": "CC-BY-SA-4.0" },
       "somebody:tabard_lion": { "author": "someone else", "license": "CC0-1.0", "source": "https://..." }
     }
   }
   ```

   The keys are namespaced ids and cover pieces, skins and cloths alike. The license is one of a
   fixed list: `CC0-1.0`, `CC-BY-4.0`, `CC-BY-SA-4.0`, `CC-BY-NC-4.0`, `CC-BY-NC-SA-4.0`, and
   `ARR` (all rights reserved: listed, downloadable as the author's pack, never composed into
   another). The mod's own pieces are `ARR` under the Armor Pieces License, with the exception
   the site itself grants in point 8. Nothing in the data or resource folders changes, so no
   codec is touched and every existing pack stays valid; a pack without the file is `ARR` by its
   author, which is what copyright law says anyway.
7. **Composing is server-side.** A visitor's selection is built into a zip on the server and
   given a link, so it can be shared and cached, and so that a composed pack is always one the
   site has checked. The editor can do the same locally through the same tool, but that is a
   convenience, not the product.
8. **Composed packs and the mod's license.** The Armor Pieces License reserves redistribution.
   The site is the copyright holder distributing, so serving the mod's pieces, alone or composed,
   is fine. What a composed pack is *for* has to be said on the download: personal use and use
   on a server you run, no re-uploading, which is section 1 of the license. Third-party pieces
   go into a composed pack only where their license allows it; `ARR` pieces do not.
9. **Free at launch.** Section 6 says why. Every account gets the same quota. Nothing about an
   account changes anything in the game.

---

## 1. The site, and the editor on it

The first deliverable is the static part, live, and it resolves the Pages problem without making
anything public.

- `ArmorPiecesSite`: Astro, deployed from CI to the host on push to `main`. Pages: `/` (the main
  page), `/wiki/...`, `/gallery` (section 3), `/editor/` (the artifact from
  `ArmorPiecesBlockbench`), `/library/index.json` (served by the site from section 4 on, static
  until then), `/about`, `/privacy`, `/cookies`, `/terms`, `/contact`.
- **The main page** says what the mod is, shows the gallery shots, and its download buttons go to
  Modrinth and CurseForge and nowhere else. The mod's zips stay downloadable from GitHub releases
  and are mirrored for the library as now; the *mod* is never served by the site. Whether the
  page is generated from `modpage.yml` as a fourth target is a `ModPageConstructor` question; the
  text should come from there either way, so the store pages and the site do not drift.
- **The wiki** is Markdown under `content/wiki/` in the site repository, rendered by Astro with a
  sidebar, a client-side search index (Pagefind) and an "edit this page" link to GitHub.
  `docs/authoring.md` is pulled from the mod repository at build time, at the tag the editor's
  bundle names, rather than copied, so there is one authoring guide. The vocabulary rule holds:
  pages say *piece*, never *part*.
- **Legal pages.** `/about` names who runs the site and how to reach them by email (the
  guidelines require a responsible party and a contact method, and say chat and forum links are
  not acceptable). `/terms` covers accounts, uploads, licenses, takedowns and the all-ages rule.
  `/privacy` and `/cookies` are section 7.
- **The footer** on every page: the disclaimer from decision 1, the license, the contact.

**The editor at `/editor/`** is the existing build with two changes, both in
`ArmorPiecesBlockbench`:

- **The vanilla textures leave the bundle, and the editor stops needing them by default.**
  What `tools/.mcassets/` is for in the editor, consumer by consumer:

  | consumer | takes from the game | is it a texture? |
  | --- | --- | --- |
  | `bb_rig.py`, the reference figure | Steve's skin, the armor and leggings sheet of one material | yes |
  | `preview_material.py`, the material preview | the sixteen trim colour palettes | eight colours each |
  | `bake_skin.py`, a skin's colours | eight shades per material, the octile medians of its sheet | eight colours each |
  | `skin_sheets.py --seed`, a new skin | the alpha of one material's sheet, as the outline to draw on | a mask |
  | `preview_cloth.py`, cloth patterns | the banner and shield pattern sprites | yes |
  | the item list, ids, loot tables | the jar's registries and lang | no, and already baked |

  None of this was ever about compensating for weak textures: the ramps are how the game itself
  colours a greyscale master at runtime, in `DecorationTextureManager` and
  `ArmorSkinTextureManager`, out of the game's own resources. The editor needs the same answers
  to show a piece the way the game will. Two of the five are textures; the other three are
  numbers derived from textures, which is the standing the baked item list already has. So:

  1. **Bake the numbers.** `make_bundle.py` runs `preview_material.py --ramp` for every palette
     and `bake_skin.py --ramps` and writes both to `tools/.webcache/` beside the three answers
     already there. Today the web shim answers `vanilla_assets.py --list-*` out of that cache;
     the ramps go the same way, or better, the two tools grow the fallback themselves, which
     also serves a desktop clone that has no jar. `make_bundle.py` stops packing `.mcassets`.
  2. **The figure wears our own.** A studio player skin drawn by us, and the mod's own `plate`
     skin baked in iron through that ramp, as the default reference armor. The shells are the
     same geometry, transcribed in `mc_humanoid.py`, so fit and clipping are judged against the
     same boxes; only the pixels are ours. The figure says which set it is wearing.
  3. **Seed from the mod's outline.** *Start from* offers the mod's `plate` silhouette; the
     vanilla outlines appear only when the game's sheets are present.
  4. **The cloth pattern preview asks for the game**, and says so, since the pattern sprites are
     nothing but game art.
  5. **Use my game** is the option, not the requirement. A visitor can point the editor at their
     client jar (`versions/<v>/<v>.jar` in `.minecraft`), their `.minecraft` folder where the
     File System Access API exists, or any resource pack folder. `vanilla_assets.py` extracts the
     same set it does on the desktop, into IndexedDB beside the packs, and from then on the figure
     wears real armor, the seed offers vanilla outlines, patterns preview, and a modded material's
     sheet gives a modded ramp, which `bake_skin.py` already promises. Nothing leaves the browser.

  This is the item that makes the tarball publishable, and CI checks it by listing the tarball
  and failing on `.mcassets`. What it does *not* change: the resource pack keeps shipping
  greyscale masters and the game keeps deriving the colours, because baking per material into
  the pack would multiply every skin by every material and lose modded materials. One known
  vanilla-derived file does ship in the mod today, the chainmail skin converted from the
  vanilla sheet; a single converted texture is not "a substantial part" of the game's content
  under the mods rule, but it is worth knowing it exists.
- **`fetchBytes` learns credentials.** The sixth platform function takes an options object
  (headers, `credentials`). On the web that is `credentials: 'include'` against the same origin;
  on the desktop it is a bearer token from section 4. One seam, as before.

## 2. Pieces as the unit: manifest, thumbnails, credits, picker

Everything the gallery and the composer need, and none of it needs an account.

- **`tools/pick_pieces.py`** in the mod repository, beside `import_pack.py`. Given source packs, a
  list of namespaced ids and a destination, it copies each piece's file set: the geometry json,
  the master and layer PNGs, the decoration entry, the template recipe, the lang line, and its
  membership in loot-group tags; skins and cloths likewise. It reads `armorpieces-credits.json`
  from each source and writes the union into the destination, refuses an `ARR` piece unless
  `--own`, and refuses two different pieces with one id. It runs on the desktop, in the browser
  and on the server, because it is one file.
- **`tools/pack_manifest.py`**: what is in a pack, as JSON. Pieces with anchor, fittings, kind,
  license and author; skins; cloths; the pack's own metadata. The plugin's piece list already
  computes most of this; the tool is the version a server can call.
- **Credits in the plugin.** The Part dialog and the skin workspace get a license field and an
  author field, written to `armorpieces-credits.json` on Save. The pack manager shows the pack's
  license. Import keeps the file; export includes it.
- **Thumbnails.** One PNG per piece, rendered by Playwright against `/editor/`: open the piece on
  the figure, one camera per socket, one screenshot. The site does this when a pack is approved
  (section 4) and at build time for the mod's own entry. `build/test_browser.mjs` already drives
  the page this way; the renderer is that harness with a camera table. The renderer's figure wears
  real armor: the server fetches the client jar from Mojang's own download and extracts it for
  its own use, which is playing the game rather than redistributing it, and a screenshot of our
  creation is something the guidelines allow. A user-supplied picture is never used as a
  thumbnail, because a picture is what the gallery says a piece looks like.
- **The library index grows `pieces`** per entry, from the manifest, with the thumbnail URL.
  The plugin ignores the field; the gallery is built from it.

## 3. The public gallery and the composer

- `/gallery` lists packs and pieces. Pieces filter by socket, fitting, kind, license, pack and
  author; search across names and descriptions. A piece page shows the thumbnail, the license,
  the author, the pack it belongs to, and *Add to selection*. A pack page shows its pieces and a
  download of the author's zips.
- **The selection** is a list of piece ids kept in the visitor's browser (no account needed).
  *Build a pack* posts it; the server runs `pick_pieces.py` over the installed copies of the
  packs involved, `export_pack.py` on the result, stores the zip under a content hash and returns
  its URL. The download page repeats every license included and the terms from decision 8. Two
  identical selections are one file.
- **Official first.** At launch the gallery holds the mod's 91 pieces, 15 skins and 2 cloths from
  the existing entry, which is enough to make the composer worth using before anyone else has
  published anything.

## 4. Accounts, personal libraries, and the editor's account source

- **Data.** `users`, `identities` (provider, subject), `sessions`, `packs` (owner, name,
  namespace, visibility: private, unlisted, public; source: hosted, github, drive), `pack_versions`
  (object key, hash, size, manifest), `pieces` (per version, from the manifest), `publications`
  (a version offered to the gallery, its review state), `compositions`, `device_tokens`,
  `reports`, `audit`.
- **A hosted pack** is uploaded as the zip `export_pack.py` writes, or saved straight from the
  editor. Every upload is quarantined until `import_pack.py` under Pyodide has unpacked it into
  a scratch directory and `pack_manifest.py` has read it back; then it is a version. Private is
  the default. Unlisted has a link. Public goes to a review queue; approving it makes it a
  gallery entry and renders its thumbnails. That is the existing approve workflow with a form on
  the site instead of an issue.
- **A GitHub-linked pack** is a repository the user installs a GitHub App on, so the site holds
  a per-repository grant rather than a token over the whole account. A version is a tag or a
  commit; publishing is a release. The site fetches through the App and stores nothing but the
  manifest and the thumbnails.
- **A Drive-linked pack** is a zip the user chooses through the Google Picker with the
  `drive.file` scope, which grants exactly that file. Drive cannot be fetched by a browser, so
  the server fetches it; each version is a re-read.
- **A local pack** is the editor's linked folder and the site cannot see it. *Upload a version*
  in the editor is how it becomes hosted.
- **The `account` source in the plugin**: a third `registerPackSource`, `Your library`, with
  `install` (pick one of your packs and versions; fetch; `import_pack.py --force`) and `publish`
  (export; upload as a new version; choose visibility). On the web the session cookie does the
  authenticating. On the desktop, *Sign in* shows an eight-character code and opens
  `/link` in the browser; the user approves the device there, the plugin polls, and stores a
  scoped token in its settings. Tokens are listed and revocable at `/account/devices`. The
  library source is unchanged and now reads the site's index, so *From the library* is the
  public gallery and *Your library* is the private one, on both platforms.
- **Offering a pack to the mod** stays a pull request by hand; the site adds a button that opens
  the issue with the pack's link, as the plugin does today.
- **Moderation.** A report button on every public pack and piece; a maintainer queue; the
  all-ages rule and the "no logos, no brands" rule from the guidelines in `/terms`; takedown by
  email.

## 5. Security

Sign-in is the largest new surface, uploads the second. In order:

- **Identity** through the providers' OAuth only, via Auth.js with PKCE, `state` and `nonce`
  checked, callback URLs pinned. No credentials are stored. Provider scopes are minimal: the
  GitHub App is installed per repository; Google is `openid email profile`, plus `drive.file`
  only when a Drive link is made, and revocable separately.
- **Sessions** are database rows referenced by an `httpOnly`, `Secure`, `SameSite=Lax` cookie,
  rotated on sign-in, expiring, revocable from the account page. Desktop tokens are bearer tokens
  bound to one device row, scoped to the library API, never cookies.
- **Mutations** require the session plus an `Origin` check; the desktop API path takes the
  bearer token and no cookie, so a cookie can never authorise a cross-site request.
- **Uploads**: a size cap, a member-count cap, an allow-list of file types (`json`, `png`,
  `mcmeta`, the credits file), zip-slip refused by `import_pack.py` as it is now, every PNG
  decoded and re-encoded by Pillow, every JSON parsed and re-serialised, and nothing served
  until it has passed. Object keys are hashes the server chooses. Buckets are private; the site
  serves published objects through its own paths.
- **Rendering**: user text is plain text; descriptions allow a small Markdown subset, sanitised
  server-side, no raw HTML, no embeds. The thumbnail renderer runs in its own container with no
  credentials and no route to the database.
- **Headers**: a strict CSP for the site; `/editor/` gets its own, looser one, because Pyodide
  needs `wasm-unsafe-eval` and the plugin evaluates itself. HSTS, `frame-ancestors 'none'`,
  `Referrer-Policy: same-origin`.
- **Limits**: per-user quotas on storage and versions, rate limits on sign-in, upload, build and
  report, an audit log of publish, approve and delete.
- **Operations**: secrets in the host's secret store, dependency audit in CI, nightly database
  backups to the object store, a restore rehearsed once, account export and deletion working
  before launch.

## 6. Money, within the guidelines

Read against the text of the Minecraft Usage Guidelines as fetched on 2026-09-06.

- **Sharing counts as commercial use.** "When you decide to share your content with the
  community (whether you plan to make money off it or not), you are doing what we consider to be
  a commercial thing." Hence the disclaimer, the named responsible party and the email contact
  on every page, paid or not.
- **The mod may never check the account.** "The mod cannot be used to directly or indirectly
  verify whether a player owns or has access to out-of-game content, products, or services that
  affect in-game features and functions." The mod does not talk to the site, ever. An account,
  a paid anything, a badge: none of it can change what happens in the game. A composed pack is a
  file the player installs, which is why the composer is fine.
- **What is safe:**
  1. Downloads pointing at Modrinth and CurseForge, whose creator programmes pay per download
     under their own terms. This is the one revenue the site is built around, and it costs it
     nothing.
  2. A sponsor link (GitHub Sponsors, Ko-fi) that buys nothing. The guidelines allow donations
     "so long as you don't offer the donor something that only they can use"; the site applies
     the same rule to itself. A public thank-you list is the most it offers.
- **What is out:** selling the mod, a pack or a piece; a tier that unlocks anything in the game;
  advertising (excluded by the user, and the domain clause forbids running the site
  "principally to make money, including through affiliate services"); affiliate links; the
  Minecraft name in the domain or the site's own branding; anything not listed, because "if
  something isn't covered by these guidelines and we haven't otherwise said it's okay, that
  probably means we don't want you to do it."
- **Left open, with a condition:** a paid storage tier for hosted packs is a service of the
  site, not of the game, and is not covered either way. If it is ever wanted, keep the domain
  free of the Minecraft name, keep the tier about storage and nothing in-game, and get a
  lawyer's reading first. Paying pack authors through the site needs a payment provider and tax
  handling and is a separate plan.

## 7. Privacy and cookies

- **Cookies the site sets:** a session cookie, only once signed in, and a short-lived state
  cookie during sign-in. Nothing else: no analytics cookies, no third-party cookies, no ad
  cookies, no embedded players (external media is a link). Under the Dutch Telecommunicatiewet
  and the GDPR, strictly necessary cookies need no consent, so there is **no banner**. `/cookies`
  lists the two cookies by name, purpose and lifetime, and the editor's use of IndexedDB and
  localStorage for the visitor's own work.
- **Counts without cookies.** Download and view counts are server-side totals with no per-visitor
  record. If page analytics are ever wanted, a cookie-less, fingerprint-free service (Cloudflare
  Web Analytics) is the only kind that keeps the banner away, and it goes on `/privacy` too.
- **`/privacy`** says, plainly: what is stored (provider, subject id, display name, email if
  given, packs and their versions, device tokens, audit entries), where (EU), for how long
  (until deleted; audit entries one year), who receives anything (the host, the object store,
  and the sign-in provider chosen), and how to export or delete the account, which is a button.
  Minimum age follows the providers' terms and is stated.

---

## Build order

Each step is live and useful on its own.

1. **Decisions 1 to 5.** Register the domain; create `ArmorPiecesSite`; set up the host.
2. **Publishable editor.** Vanilla textures out of the bundle, the first-run jar step, the CI
   check. The `fetchBytes` options. `npm test` green.
3. **The static site live.** Main page, wiki, legal pages, footer, the editor at `/editor/`, the
   library index served from the site, the plugin's default library URL pointed at it.
4. **Pieces as the unit.** `pick_pieces.py`, `pack_manifest.py`, credits in the plugin, the
   thumbnail renderer, the per-piece index. Tests in the mod repository for the two tools.
5. **The gallery and the composer**, over the official entry.
6. **Accounts and hosted libraries.** Sign-in, uploads with validation, visibility, the review
   queue, the `account` source on the web.
7. **Desktop sign-in, GitHub and Drive links.**
8. **The sponsor link, and nothing else.**

## Check

- `tar tzf web/repo.tar.gz | grep .mcassets` prints nothing, in CI and locally. With no game
  given, the editor shows a piece on the studio figure in the mod's plate skin, the material
  preview of `spaulders gold` matches the desktop's pixel for pixel, and a new skin seeds from
  the plate outline. After the visitor points it at their jar the figure wears vanilla iron and
  `Start from` lists the vanilla outlines.
- The published `/editor/` opens a piece, paints it, saves it, in Chrome and Firefox and on a
  phone width; the desktop plugin with the library URL set to the site installs the official
  entry as it does from the dev server today.
- `pick_pieces.py` moves a piece, a skin and a cloth between two packs and the game loads the
  result; it refuses an `ARR` piece and an id collision; the credits file follows the pieces.
- A composed pack of pieces from two packs downloads, installs, and every included license is on
  the download page.
- A new user signs in with each of the four providers, uploads a pack, sees it private, makes it
  public, sees it in the queue, sees it approved with thumbnails, and installs it from the editor
  on the web and on the desktop through a device token that shows up under `/account/devices`
  and stops working when revoked.
- A zip with a path outside the pack, a non-PNG named `.png`, and a 200 MB file are all refused
  before anything is stored.
- The mod's client never opens a connection to the site: confirmed by reading the code, and
  nothing in the mod knows the site's address.
- Every page has the disclaimer, the contact and the license in its footer; no page sets a cookie
  before sign-in; the privacy page matches the schema.
- Account deletion removes the user, identities, sessions, tokens and private packs, and leaves
  public packs only if the user chose to keep them published under their credit.
