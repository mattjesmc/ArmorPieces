# Plan: storage, retrieval and versions

> **Status (2026-09-08): BUILT AND DEPLOYED**, sections 1 to 3, as `a2f1988` in ArmorPiecesSite.
> 144 tests pass, 18 of them new (`test/capacity.test.mjs`, `test/takedown.test.mjs`,
> `test/formats.test.mjs`).
> Section 0 is a survey of what already existed, written first because the brief that opened this
> plan describes a back end that was replaced on 2026-09-07 and is live. Section 4 records two
> decisions the user made up front, and the one risk deliberately left open - still open.
>
> **What the building changed about the plan**, because a plan that is not corrected by contact
> with the code is a plan nobody read afterwards:
>
> - **"Published only" is two rules, not one.** Refusing to assemble anything unpublished for a
>   stranger would have emptied every UNLISTED pack (whose pieces were never offered for review -
>   the link is the secret) and every half-approved public one. So: a WITHDRAWN object is held back
>   from everyone but its owner, whatever the pack's visibility; and out of a PUBLIC pack an object
>   that was never published is held back too, which closes a hole the plan did not name - a public
>   pack may carry somebody else's unpublished piece, because `filePackPublication` files no review
>   for one that is not the publisher's.
> - **The cache was not the only place a withdrawn piece survives.** Composed packs are not in
>   `data/cache` at all: `/api/compose` writes a stored zip under `data/composed`, keyed by its own
>   bytes, with links meant to be permanent. `forgetComposedWith(id)` throws those away too.
> - **`forgetMerged()` was not enough either.** A version's manifest is PINNED at the cut, so the
>   catalogue the plugin reads went on advertising the withdrawn piece after the download had
>   stopped carrying it. `unpublishedOf()` filters the merged index.
> - **The name 'withdrawn' was taken.** `withdrawPack` already set queued rows to `'withdrawn'`
>   when an author made a pack private - not a decision, nobody looked. That is `'cancelled'` now,
>   so `reviewOf(hash)` can treat a withdrawal as the reverse of an approval and find it. And
>   "withdrawn" means the LAST decision, not any decision, or a restore would be a no-op.
> - **The byte quota had a hole of its own.** `copyPieces` with `as` - duplicate, the one verb that
>   makes new content - never checked the quota at all. It does now, in both bytes and files.
> - **There is only ONE format profile in the mod's whole history**, and it is not a placeholder:
>   resourcepack 88 / datapack 107 since 0.1.1, because gradle.properties reads them out of the
>   game's own version.json and Minecraft has not moved. (0.1.0 shipped no numbers.) So the profile
>   is named after the game - `mc26` - and not after a mod release, since calling it `0.3` would
>   have said something false about 0.1.1 to 0.2.0. The version selector renders nothing until
>   there is a second one.
> - **0.1.0 and 0.1.1 shipped no pack zips**, so the mirror is 0.1.2, 0.1.3 and 0.2.0, plus 0.3.0
>   from the editor bundle. The parity test diffs against all four.

The user's brief, 2026-09-08:

> Currently the back end of the website is a shim. It is static, requires maintaining github
> repo's and any content moderation was never tested or perhaps not even developed. [...] For the
> website to be a safe environment all downloads should come from our server. The content library
> should be hosted on our server, with back ups and smart storage and retrieval. [...] Inherent
> version support in the database. [...] Storage division. Users private content encrypted or
> not? [...] Storage space management.

## 0. What is already true, with the numbers

`docs/plans/content-model.md` built the object store and it is merged and deployed. On the box on
2026-09-08:

| | |
|---|---|
| objects (91 pieces, 14 skins, 2 cloth) | 107 |
| blobs | 572, **365 kB** total, **654 B** average |
| packs / publications / reports | 0 / 0 / 0 |
| static library index entries | **1** — the mod, its zips mirrored locally |
| database | 9.2 MB |

Point by point against the brief:

- **"Static, maintains github repos."** The static index has one entry left, the mod's own, and
  its zips are files we host. GitHub and Drive survive only as *import* sources
  (`link-github.ts`, `link-drive.ts`, `refresh.ts`) — a pack author may point at a repo, and we
  read it once. They are never in a download path.
- **"All downloads should come from our server."** They do, and have since the content model
  landed. `library/u/[pack]/[version].zip`, `composed/[hash].zip`,
  `gallery/pieces/[ns]/[name]/piece.zip`, `wardrobe/[id]/pieces.zip` and
  `wardrobe/pack/[hash].zip` all assemble from blobs on our disk. Nothing redirects offsite.
- **"Moderation never tested or perhaps not even developed."** Developed and unit-tested
  (`publish.ts`, `admin/queue/`, `publications`, `test/publish.test.mjs`, MAINTAINERS set on the
  box); never exercised by a real submission, because no third party has submitted one. Half
  right, and section 2 is where the half that is wrong lives.
- **"Backups."** `deploy/backup.sh` runs nightly from cron: `pg_dump -Fc` plus a tar of the data
  volume, fourteen days kept. It has never left the box — `BACKUP_RCLONE_REMOTE` is unset and
  rclone is not installed. See section 4.
- **"Version support."** Absent. `assemble.ts:modFormats()` reads *one* pair of numbers out of
  `content/mod/gradle.properties` and stamps every zip the site has ever built with them. Section
  1.

**So the shim is gone and the brief's premise is stale, except for versions and takedown.** The
value of writing that down is that nobody rebuilds the object store.

## 1. Format versions: transform at assembly, cache per target

**The seam already exists.** `AssembleSpec.formats` is an override that nothing sets
(`spec.formats || modFormats()`), and `assembledHash` already folds `formats` into the cache key.
The work is to give that override a name, a history and a transform.

### 1.1 A format profile

One record per mod release whose pack format differs from its predecessor's, in one file,
`src/lib/formats.ts`:

```ts
export interface Profile {
  id: string;            // '0.3', '0.4' — the profile's name, not the mod version
  modVersion: string;    // the release that introduced it, for the download's label
  resource: number;      // pack_format for assets/
  data: number;          // pack_format for data/
  from?: string;         // the profile this one succeeds
  up?: Transform;        // from `from` to this
  down?: Transform;      // this back to `from`; absent means the step is one-way
}
export type Transform = (files: File[], ctx: { object: ObjectRow }) => File[];
```

The list is append-only and hand-written: the mod knows only its *current* two numbers, so the
historical ones are recorded once, at the release that changes them. The newest profile's numbers
must equal `modFormats()`, and a test asserts it — that is what stops the list going stale.

### 1.2 The object never moves

An object is canonical at the format it was authored under. One new column,
`objects.format text not null default '<current profile>'`, set at ingest. No object is ever
rewritten, no second copy is stored, and a migration bug is not a data loss event.

### 1.3 Assembly walks the chain

`assemble(spec, target)` resolves the path from each object's `format` to `target` through
`from`/`up`/`down`, applies each step to the **file set in memory**, and writes the zip with the
target profile's two numbers. Transforms are pure `(files) => files`: they never read the
database and never touch a blob.

Where a step has no `down`, a downgrade to that target is refused with the reason, per object —
"`mine:crown` cannot be built for 0.3; it uses a socket 0.3 has no name for" — rather than
shipping a pack the game will half-read.

### 1.4 The cache does the storing

`assembledHash` gains the profile id. Every (spec, target) pair therefore has its own cached zip
under `data/cache/`, which is exactly "stored per version" — except that it is evictable, costs
nothing until somebody asks for that version, and is thrown away and rebuilt when a transform is
fixed. This is the whole reason to prefer it to migrate-on-write: **the recovery procedure for a
bad migration is `rm data/cache/*`.**

### 1.5 The parity test, which is the good part

We mirror the mod's own release zips. Assembling the mod's own objects at profile *P* must equal
the zip that release actually shipped, member for member. That turns "does the 0.3→0.4 transform
work" from a judgement into a diff against a real historical artifact, and it is the same shape as
the parity test the content model already holds against `pick_pieces` + `export_pack
--reproducible`.

For this to cover more than one step, the older release zips (0.1.0, 0.2.0) must be mirrored into
`content/mod/armorpieces/` beside 0.3.0. They are on GitHub releases; mirroring them is a `npm run
sync` change, and it is cheap — the whole mod is 365 kB of blobs.

### 1.6 What the visitor sees

A version selector on every download, defaulting to the newest profile. The desktop plugin already
derives the site origin from its `armorpieces_library` setting; if it sends its own version with
the request it gets the right zip without being asked, and if it does not, it gets the newest — so
nothing already installed breaks.

## 2. Takedown, and reports that go somewhere

Approval is currently **one-way and permanent**. That is the moderation hole, and it is three
separate defects:

1. **A report can only ever be open.** `/api/report` inserts a row; `admin/queue/index.astro`
   selects the open ones and shows them; *nothing in the codebase ever writes `reports.state`.*
   There is no dismiss and no uphold.
2. **Only a pack can be reported.** `reports.pack_id` is `not null` and references `packs`. A
   piece published on its own — which the content model made possible — and a public outfit, which
   is now first-class, cannot be reported at all.
3. **There is no reverse of approval.** No route sets `objects.published_at` back to null. Once a
   hash is public it is public.

### 2.1 The subject of a report

Migration: `reports.pack_id` becomes nullable, and the table gains `hash text` (an object) and
`set_id text` (an outfit), with a check that exactly one of the three is set, plus an index on
`(state, created_at desc)`. `/api/report` takes `{subject: 'pack'|'piece'|'outfit', id, reason}`.

### 2.2 A withdrawal is a decision row

Takedown is symmetric with approval and uses the machinery that is there: set
`objects.published_at = null` and write a `publications` row with state `'withdrawn'`. Then
`reviewOf(hash)` — which already means "reviewed once, ever" — returns the withdrawal, so
re-offering the same bytes inside another pack does not quietly re-queue them. A maintainer can
reverse a withdrawal; nobody else can.

The owner keeps their copy. Draft assembly already includes what a public download excludes
(`includeOfficial`, the same principle), so a withdrawal takes a piece out of circulation without
destroying the author's work.

### 2.3 The sweep, and the trap in it

A withdrawal is only real once every public surface stops carrying it:

- the gallery (`objects_published` index; a query change);
- the merged catalogue — call `forgetMerged()`, as the review route already does;
- **public pack versions that list the hash.** `assemble()` currently throws when an object is
  *missing*; here it exists and is merely not public, so public assembly needs a "published only"
  mode, and the pack page must name the withdrawn piece to its author the way a half-approved
  group already does;
- public outfits referencing it. `sets.pending_public` exists for the forward direction
  (publish-and-go) and is reused in reverse: an outfit whose piece is withdrawn goes back to
  pending rather than showing a hole;
- **the assembled-zip cache.** This is the trap. `data/cache/` is keyed by spec hash and will
  happily keep serving a zip containing the withdrawn piece for as long as the file sits there.
  *A takedown that does not evict the cache is not a takedown.* Withdrawal must delete every cache
  entry whose spec included the hash, which means the cache needs an index from hash to spec —
  a small table, `cache_entries(spec_hash, object_hash)`, written when a zip is cached.

Every withdrawal writes an `audit` row. That table exists and is already what `/api/me/export`
hands a user about themselves.

## 3. Capacity, honestly

### 3.1 The numbers

A piece is **3.4 kB** of blobs. The default quota is **200 MB**, which is about **58,000 pieces**
per account: not a limit, a rounding error. Meanwhile 572 blobs of 654 B occupy 3.2 MB of 4 kB
filesystem blocks — **small blobs cost roughly six times their size on disk**, and block waste, not
content, is what a hundred thousand blobs would actually consume.

Disk is 9.1 GB free, plus **6.1 GB of reclaimable Docker build cache**. Reserving ~3 GB for the OS,
images, database and fourteen days of on-box backups leaves ~12 GB for content. A realistic author
with fifty pieces and their thumbnails costs about 1 MB on disk, so the box supports **thousands of
real authors**. The quota is what stops one adversary; it is not what sizes the machine.

### 3.2 What to change

- **Quota: 200 MB → 50 MB**, still ~15,000 pieces, and add a **blob-count cap** (20,000 per
  account) beside the byte cap, because block waste is per file and the byte cap cannot see it.
  `usedBytes()` already counts distinct blobs of objects you created plus your packs' furniture;
  a `usedBlobs()` beside it is the same query with `count(*)`.
- **Evict the assembly cache.** `data/cache/` is written and never swept. A nightly sweep: drop
  entries not touched in fourteen days, then oldest-first until the directory is under 1 GB.
  Rebuilding is milliseconds, so eviction is free; add `cache_entries` cleanup (2.3) to the same
  sweep.
- **Evict renders.** `data/sets/` grows one PNG per distinct outfit hash and nothing removes them.
  `LIMITS.shots` (3/min) and `MAX_QUEUED` (8) cap the *rate*; the sweep caps the *total*.
- **Prune the builder.** `docker builder prune -f --filter until=168h` in the nightly cron beside
  `backup.sh`, and once by hand now, for 6.1 GB back today.
- **A capacity line in `/healthz`** — free disk, blob count, cache size — so the box says when it
  is filling rather than being asked.

## 4. Two decisions, and one open risk

**Private content is not encrypted, and there is no account key.** Content-addressed storage and
per-user encryption are mutually exclusive: an encrypted blob is different ciphertext for every
owner, so deduplication ends, and the server can no longer assemble a zip, render a thumbnail, or
apply a section 1 transform, because it cannot read the bytes. "Private" means what it means now —
authorization on the read path (`visibility === 'private'`, already enforced in `hostedZip`) and
server-chosen sha256 keys that a visitor cannot guess or construct. Backups get the encryption
instead, before they leave the box.

**Publishing moves nothing.** A blob is shared between accounts, so a public "division" would break
deduplication and every collection referencing the moved bytes. Publication is a decision row about
a hash, which is what buys "reviewed once, ever"; section 2 gives it a reverse. Ownership is
already a column (`objects.owner_id`), not a location.

**Open risk, deliberately not scheduled: backups never leave the box.** Nightly dumps exist and are
fourteen days deep, but they are on the same disk as the thing they protect. Closing it is
`rclone` plus a remote (B2 or S3) plus `age`-encrypting the tarballs plus one rehearsed restore —
small work, blocked on a storage account that is the user's to create. Until then the honest
statement is that the site survives a bad deploy and does not survive a lost VPS.

## Order

Built in this order, on 2026-09-08:

1. Section 3's sweeps and the builder prune — the headroom the rest runs in.
2. Section 2, takedown — the live gap, and the one a first real submission would expose.
3. Section 1, versions — not urgent until a second incompatible format exists, and written now
   because the mirroring of the old release zips (1.5) should happen while those releases are
   still the recent past.

## Where it landed

| | |
|---|---|
| `src/lib/capacity.ts` | free disk, blobs, cache, renders — the numbers `/healthz` carries |
| `scripts/sweep.mjs`, `deploy/sweep.sh` | the nightly sweep, in the container and around it; `--dry-run` says what it would take |
| `src/lib/formats.ts` | the profile list, the chain, the refusal |
| `src/lib/takedown.ts` | withdraw and restore a piece, a pack or an outfit; act on a report |
| `src/pages/api/admin/takedown.ts`, `api/admin/reports/[id].ts` | the two routes the queue page drives |
| `drizzle/0010`–`0012` | `cache_entries`; the quota cut and the file cap; reports' subject; `objects.format` |
| `test/capacity.test.mjs`, `takedown.test.mjs`, `formats.test.mjs` | 18 tests, and 144 pass |

Two things on the box are still the operator's, and neither is code: `docker builder prune` once by
hand for the 6.1 GB back today (the cron takes it from tomorrow, once `server-setup.sh` has been
re-run to install it), and the open risk below.
