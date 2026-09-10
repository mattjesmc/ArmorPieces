# The concurrency A/B: does a second session pay, now that it has its own name?

**Status: asked and answered twice.** Round 1 (2026-09-08 morning, below) said *step 2 is the fix*:
contention was no longer damaging but it was total, and two sessions took longer than one. Round 2
(**2026-09-08 evening**, at the end of this file) ran the same question on step 2 as built — a window
each, mcp-toolkit 0.140.0 — and **two sessions started together produced two pieces in 7.0 minutes
against 14.8 sequential.** Concurrency pays now. Read round 1 for the case that got step 2 built and
round 2 for what it bought; round 2's sequential arm is void for a launcher reason it explains.

---

**Round 1 status: run 2026-09-08, both arms complete. Answer: step 2 is the fix.** Contention no longer
corrupts anything — `risky_eval` is 0 in both concurrent runs and the guards hold — but the second
session is locked out of the shared window until the first finishes, so two sessions started
together took *longer* (16.4 min) than the same two pieces in sequence (14.8 min). See Results. A
first batch was voided by a binding defect on the single-session path, fixed in
`tools/mcp/server.mjs` and written up below. All four Dragonslayer pieces were built.

## The question

`blockbench-plugins.md` measured, on the same plugin and the same brief shape:

| | min | turns | bridge calls | out | cache read | **$/piece** |
|---|---|---|---|---|---|---|
| **C** new plugin, **alone** (n=2) | 5.2 | 60 | 31 | 95k | 3.4M | **$2.19** |
| **C** new plugin, **contended** (n=2) | 14.3 | 123 | 59 | 159k | 13.7M | **$5.15** |

Contention cost 2.4x the money and 2.8x the wall clock, and the cause was identity: every session
presented the same id, so the plugin saw one session, held one binding, and sent every call that
did not name a project to somebody else's piece.

That cause is gone. mcp-toolkit 0.136.0 / shim 0.66.0 derives the session id from the **parent
process** — the `claude.exe` a session's MCP servers are both children of — so two sessions cannot
collide by accident and one session's two servers cannot split by accident either. `.mcp.json` sets
no session id at all.

**What this A/B asks is not whether the fix works.** A probe answers that. It asks what concurrency
costs *once identity is correct*, because that number decides the next piece of engineering:

- If contended ≈ alone, **step 2 of `BLOCKBENCH_ISOLATION_DESIGN.md` (per-window ports and window
  claiming) is an optimisation** and can wait behind content work.
- If contended is still materially worse, **step 2 is the fix**, and this run's transcripts will say
  which of the remaining shared-window hazards did it — the design record's section 4 predicts them
  by name, and the tool mix below is how they show up.

Either answer is worth the spend. The one outcome that wastes the run is an inconclusive one, which
is what the preconditions and the pre-registered signals below exist to prevent.

## Preconditions, each one checkable before spending anything

1. **The extract is 0.136.0.** `run/mcptoolkit/mcp-server/.extracted-version` reads `0.136.0`, and
   `grep SESSION_ID run/mcptoolkit/mcp-server/upstream/blockbench.mjs` ends in `mcptk-${process.ppid}`.
   (Both true as of 2026-09-07 20:0x; a dev boot re-extracts from the jar, which now carries it.)
2. **Nothing sets an id.** `MCPTK_SESSION` appears in no `.mcp.json`, no user or machine environment
   variable, and no launcher. An explicit one still wins by design, which here would silently
   recreate the bug.
3. **Blockbench is plugin 0.2.0 or later**, one window, and `GET http://127.0.0.1:25801/hello`
   answers with `"plugin_version":"0.2.0"` and 26 tools. An older plugin never opens `/presence` and
   falls back to the timer, which changes what a binding's lifetime means mid-experiment.
4. **Each concurrent piece is its OWN `claude.exe`.** This is the precondition most likely to be got
   wrong, because it is invisible: two pieces authored by two *subagents inside one session* share a
   process, therefore share a parent, therefore share an id — the exact condition being measured
   against. Concurrency here means separate headless `claude -p` children, one per piece, as the
   earlier batch used.
5. **No session that predates the fix is still connected.** A running Claude session keeps the shim
   it started with and the environment it was launched with, so a session opened before `.mcp.json`
   lost `MCPTK_SESSION` still presents `armorpieces` for as long as it lives. Measured while writing
   this brief: `project op:list` showed a live session `armorpieces` with **2 connections** beside a
   fresh `mcptk-87744` with 1. Such a session can still take a binding mid-run. Close them, or check
   `project op:list` shows only `mcptk-` ids before starting.
6. **The identities are distinct, asserted before any modelling.** Each session's first bridge call
   is `project op:list`; its own id appears in the reply, and the human (or the launcher) confirms
   the two ids differ and that no reply carries the shared-connections note. Abort on a collision —
   a run that turns out to have been contended-by-id measures nothing new.

## The run

Four pieces, paired: **two authored alone, one after the other; two authored concurrently.** Same
model as the earlier batch (Sonnet 5), same `part-author-kit` agent, same brief shape, so the new
rows sit beside the old ones without an asterisk.

Choose the pieces from `docs/plans/briefs/` by three rules, and let this repository's own content
plan pick within them:

- **Unbuilt pieces the mod actually wants.** The point of spending model time is a piece at the end
  of it; a throwaway subject makes the money a pure experiment cost.
- **Matched difficulty across the pair boundary.** The solo pair and the concurrent pair should be
  of a kind — comparable element counts and comparable painting, no ornate piece opposite a plain
  one. The earlier batch's spread (3.7 min for `coral_crown` against 20.0 for `kelp_mantle`) is
  wide enough to swamp the effect being measured if the pairs are unbalanced.
- **One pack, or none.** Pieces from one theme share a palette and a reference, which is one fewer
  reason for two sessions to differ.

The concurrent pair starts together. Both sessions may keep their own tab in the one Blockbench
window, which is the arrangement step 2 would replace — measuring it is the point.

## What to record, and what would falsify what

Everything below already comes out of `python tools/measure_sessions.py --archive`, which files the
transcripts under `.mcptoolkit/runs/archive/D/` and writes `measurements.json`. Run it after the
batch; it is idempotent.

**The headline** is the same six columns as the table above, so the new rows drop straight into
`blockbench-plugins.md`: minutes, turns, bridge calls, output tokens, cache reads, dollars per piece.

**The identity column is the falsifier.** `measure_sessions.py` now reads session ids out of the
replies and flags `SHARED` when the plugin's shared-connections note appears. A D row marked
`SHARED` is not a D run — it is a C run with a newer date, and the batch is void.

**The tool mix is the diagnosis**, and the earlier batch pre-registers it. These were the contended
signatures, per piece:

| | `risky_eval` | `armorpieces_check` | `armorpieces_open` | `armorpieces_paint` |
|---|---|---|---|---|
| C alone | 0.0 | 2.5 | 0.0 | 3.5 |
| C contended | 11.5 | 6.5 | 4.5 | 0.0 |

`risky_eval` is the health metric: **0.0 in the clean runs of both earlier eras**, 11.5 when the
tools stopped being trustworthy. `armorpieces_open` counts how many times a session had to re-open
its own piece — the direct fingerprint of another session stealing the active tab. If the concurrent
pair comes back at or near the *alone* row on both, the shared window is not hurting and step 2 is
an optimisation. If `armorpieces_open` stays high while `risky_eval` returns to zero, the tab is
still being stolen but the guards are now catching it, which is a weaker case for step 2 than raw
cost would suggest and should be said out loud rather than averaged away.

**Two things the numbers will not show, so read for them in the transcripts.** The design record's
section 4 lists the state a tab does *not* own — the selected animation, keyframes, the timeline
playhead, paint selection, erase mode, alpha lock, mirror painting — none of which any counter here
covers. And a `held_by` refusal is a *success* of the fix, not a failure of the run: it is the guard
firing, which under a shared id it never could. Count them; do not treat them as errors.

## The spend

Four pieces at the earlier batch's rates is roughly $10-20 and something like an hour of wall clock,
most of it concurrent. That is the whole cost of knowing whether to build step 2, which is a
plugin-and-shim change to port discovery on both sides.

## Results

**Run 2026-09-08. Both arms completed on the fixed bridge, and the answer is: step 2 is the fix,
not an optimisation.** Contention no longer corrupts anything — the guards hold and `risky_eval`
stays at 0 — but the second session is *locked out of the window entirely* until the first is
finished, so concurrency delivers no wall clock at all. Getting there took two attempts: the first
batch was contaminated by a binding defect on the single-session path, diagnosed and fixed below.

All four pieces were built and are on disk; `check_authoring.py` is clean across the pack.

### The four pieces

The first four of **Armor Pieces: Dragonslayer** (`armorpieces_dragon`), from
`docs/plans/pack-line.md`. All 69 briefs under `docs/plans/briefs/` were already built, so the
pieces come from the pack line and the briefs are new; `packs/dragon/` was scaffolded empty
beforehand so every session did identical work.

| | piece | socket | centre | kind |
|---|---|---|---|---|
| solo | `dragon_knuckles` | knees | `end_rod` | small hard part |
| solo | `wing_tatters` | tassets | `chorus_fruit` | medium multi-element |
| concurrent | `dragon_scales` | greaves | `purpur_block` | medium multi-element |
| concurrent | `dragon_talons` | spurs | `chorus_flower` | small hard part |

Each pair is one small piece and one medium one, so the pair boundary is matched; all four are
mirrored lower-leg sockets, no fitting, no static layer, no effect, one greyscale master and one
recipe each, with **mutually disjoint envelope budgets** so the concurrent pair carried no
clearance work the solo pair did not.

### The headline

| | min | turns | bridge calls | out | cache read | **$/piece** |
|---|---|---|---|---|---|---|
| **C** new plugin, alone (n=2) | 5.2 | 60 | 31 | 95k | 3.4M | **$2.19** |
| **C** new plugin, **contended** (n=2) | 14.3 | 123 | 59 | 159k | 13.7M | **$5.15** |
| **D** own id, alone (n=2) | 7.4 | 71 | 37 | 114k | 4.5M | **$2.67** |
| **D** own id, **contended** (n=2) | 11.6 | 90 | 39 | 126k | 6.1M | **$3.01** |

Per piece: contention used to cost **2.4x** the money; it now costs **1.13x**. That is the identity
fix and the binding fix showing up, and on money alone it would say "optimisation, defer it".

**The money is the wrong column.** The point of running two sessions is wall clock, and there was
none:

| | wall clock for two pieces |
|---|---|
| the solo pair, one after the other | 5.7 + 9.1 = **14.8 min** |
| the concurrent pair, started together | **16.4 min** |

Two sessions started at the same second took *longer* to produce two pieces than the same two
pieces built in sequence. Concurrency bought nothing, because it did not happen.

### What the pair actually did

The two runs are not two halves of one experience. One won the window and one did not:

| | min | turns | bridge | `risky_eval` | `held_by` | `armorpieces_new` |
|---|---|---|---|---|---|---|
| `dragon_scales` — won | 6.7 | 64 | 33 | **0** | 0 | 1 |
| `dragon_talons` — lost | 16.4 | 116 | 44 | **0** | **10** | **3** |

`dragon_scales` is indistinguishable from a solo run. `dragon_talons` spent the whole of the other
session's life being refused:

```
10:37:11  scales   armorpieces_pieces        (first bridge call — wins the race)
10:37:16  scales   armorpieces_new           dragon_scales created, bound
10:38:25  talons   held_by: session mcptk-13676 is bound to "dragon_scales", connected
10:38:30  talons   held_by …                 armorpieces_new refused
10:38:33  talons   ← reply describing dragon_scales, 23 cubes (the OTHER session's piece)
10:38:39  talons   held_by …                 armorpieces_new refused (2nd)
10:39:22  talons   held_by …
10:40:14  talons   held_by …
10:40:55  talons   held_by …
10:42:13  talons   held_by …                 (7th refusal)
10:42:52  scales   last bridge call — finishes and releases
10:46:09  talons   first reply bound to dragon_talons — its own piece, at last
```

Overlap of the two bridge windows: **4.5 minutes**, every one of them spent refused. `dragon_talons`
first held its own piece at 10:46:09, **3¼ minutes after `dragon_scales` had already finished**.

**Why.** A session has no binding until it has a piece, and `armorpieces_new` has nothing to name
yet — so its eval resolves against the active tab. In one window the active tab is whatever the
other session is working on, and the plugin correctly refuses an edit to a project another live
session holds. The refusal is right; the architecture is what makes it inevitable. This is the
creation path specifically, and it is precisely the gap per-window ports and window claiming close.

### Which of the two answers: step 2 is the fix

The brief pre-registered how to read this, including this exact case: *"If `armorpieces_open` stays
high while `risky_eval` returns to zero, the tab is still being stolen but the guards are now
catching it, which is a weaker case for step 2 than raw cost would suggest and should be said out
loud rather than averaged away."*

Said out loud: **`risky_eval` is 0 in both concurrent runs, `armorpieces_open` is 0, and nothing was
corrupted or written to the wrong piece.** The guards work. Judged on damage, step 2 would be an
optimisation.

But the failure is no longer *damaging* — it is *total*. The second session cannot begin. Averaging
the pair hides this behind a 1.13x cost ratio; the pair is really one ordinary run and one run that
sat in a retry loop for four and a half minutes, read the bridge's own source trying to understand
why, and started work only after the other had gone. **Concurrency currently has negative value:**
it is slower than sequential and costs more. That is worth the plugin-and-shim change to port
discovery on both sides.

Two smaller notes for whoever builds step 2. A `held_by` refusal is the guard succeeding and should
stay — the goal is for the second session never to *need* it, not to weaken it. And the refused
session was handed a full description of the other session's piece (23 cubes, its bones) at
10:38:33; a session should not be able to read another's work by asking for its own.

### Getting here: the binding defect, and the first batch

The first batch (three `dragon_knuckles` attempts, 2026-09-08 early hours) is void, and its D rows
in `blockbench-plugins.md` were flagged as a bug measurement until these replaced them. What it hit
was not concurrency at all:

`armorpieces_new` opens a piece out of a scratch project. When the Armor Pieces api needed a tab and
there was none, `evalIn`'s catch created that scratch with **`project op:new`** — which *binds the
session to what it makes* — and `dropScratch()` then declined to close it, because it closed the
scratch only `if (s !== Project)` and there the scratch *was* the active project. So the session was
never unbound; it was **bound to the scratch**, and calls resolved there by binding rather than by
any active-tab fallback, which is why the piece tab becoming active never fixed it. The bridge's own
project stamp reads `armorpieces_scratch bound:true` 33 / 4 / 28 times across those three runs,
against `dragon_knuckles bound:false` 25 / 1 / 23.

Worse, `evalIn` applies its PROJECT arbiter — the guard added in 0.135.0 to refuse an eval that
resolved to the wrong piece — only `if (bound)`, this server's own local, which `bindActive()` had
left `null` while the plugin considered the session bound. **The guard was switched off in exactly
the state that trips it.**

The first of those runs also finished with a full "the piece is complete and saved … files on disk
confirmed correct by direct read" report and left **nothing on disk** — a false success, which is a
worse failure mode than a crash because it is invisible. The second was killed by the OS for memory
with zero cubes placed. The third built a piece, expensively.

Fixed 2026-09-08 in `tools/mcp/server.mjs`:

- **`bindActive()` locates the piece by key.** The plugin keeps a project's piece on the project
  object (`Project['armorpieces_piece']`), so every open tab's key is readable without selecting it.
  It scans `ModelProject.all` for the key it was asked for and `op:select`s that uuid instead of
  reading the global `Project` — which also sets the local `bound`, re-arming the arbiter.
- **`dropScratch()` closes through `project op:close`**, which nulls every session bound to that
  uuid; a raw `s.close(true)` eval does not, and leaves a session bound to a dead uuid. The
  `s !== Project` condition is gone.
- **Bind before drop** at all three call sites.
- **`armorpieces_new` registers an unregistered pack root** it was told to write into. A pack folder
  on disk is invisible to the plugin until it is in `armorpieces_packs`, which cost the first
  session of this pack entirely. hive, legends and wildhunt were also missing and were registered.

  **Superseded 2026-09-10 for packs inside the repository.** Registering was only half a fix:
  `armorpieces_packs` is one setting saved whole by whichever Blockbench window saves last, so the
  registrations went away again, and by 2026-09-10 the setting held only `legacy` and `vlm-scratch`
  — every piece in dragon, nether, animals, coral, hive and wildhunt was unreachable, which is
  exactly the failure this row describes, returning. The plugin now finds `packs/<name>/*` in the
  repository itself (`packsInRepo`, ahead of `run/`), so a folder that is here on disk needs no
  remembering. `armorpieces_new` still registers, for packs kept outside the clone.

The fix is worth its own row, because it is most of the "era D" gain:

| `dragon_knuckles`, same brief, same model | min | turns | bridge | `risky_eval` | "no piece is open" |
|---|---|---|---|---|---|
| before the binding fix | 14.5 | 188 | 90 | 23 | 30 |
| after | **5.6** | **65** | **31** | **0** | **0** |

### Identity: the fix holds

Every session in both batches presented its own `mcptk-<ppid>`, and no reply in any transcript
carried the plugin's shared-connections note. Contention is no longer an id collision — what remains
is the shared window, which is what step 2 addresses.

One caveat for the tooling: `measure_sessions.py` reports `dragon_talons`' id as `mcptk-13676`,
which is the *other* session's — it reads ids out of reply text, and a `held_by` refusal names the
holder rather than the caller. Talons was `mcptk-99264` (asserted live during the run). The identity
column is the A/B's falsifier, so it should prefer a session's own stamp over a name quoted in a
refusal.

### What it cost

The seven Sonnet authoring runs cost **$23.47** — $12.11 for the three voided first-batch attempts,
$11.36 for the four that count ($1.79 + $3.55 + $2.17 + $3.85). Opus driver sessions cost several
times that: the first evening alone added $48.75. Budget a batch like this at **$60–100 all in**,
not the brief's "$10–20" — that figure counted only the authoring arm, and it is the smaller half.

---

# Round 2, on a window each: step 2 works

**Run 2026-09-08 evening, mcp-toolkit 0.140.0 / shim 0.68.0 / Blockbench plugin 0.6.0. Two sessions
started at the same second produced two pieces in 7.0 minutes, against 13.9 for two built one after
the other the same evening and the 14.8 round 1 measured.** Each session took a window of its own
within 26 seconds and held its own piece within 41; `held_by` refusals, `risky_eval` calls and
re-opens were all **zero**, in both arms. The reserved window was never touched. Round 1's verdict —
*"concurrency currently has negative value"* — is reversed by the change it asked for.

## What was different

`BLOCKBENCH_ISOLATION_DESIGN.md` section 6.3, built as toolkit 0.139.0 and published to mavenLocal
as 0.140.0: each Blockbench window's plugin takes the first free port at or above 25801, so the port
names the window, and a shim rejoins its own window, claims a free one, or asks an existing window
for another. This repository's half is `tools/mcp/server.mjs` discovering over the same range instead
of pinning the base port — **and that half is load-bearing**: a proxy pinned to 25801 while the shim
scanned would have sent this session's piece work into the window another session had taken, which is
the failure being measured. `build.gradle` names 0.140.0 and `run/mcptoolkit/mcp-server` is
re-extracted from it (`.extracted-version` says which).

## Two things a live second window settled that no harness could

**A new window served nothing, and the reason was not in any of the code.** `POST /window` opened a
real window every time — and none of them answered `/hello`. Blockbench's stored `installed_plugins`
did not contain `mcptoolkit_bridge`: it had been loaded from file without being installed, so it
lived in the window that loaded it and in no other. A new window boots from the persisted list, got
the ArmorPieces plugin and the two older toolkit plugins, and got no bridge. Worse, the shim's
`askForWindow` has no memory of having asked, so every call that found no window asked for another:
one `check_kit.mjs` run left **five** blank windows behind, twelve seconds apart. Installing the
plugin properly fixes it; the shim asking once per call is worth a cap or a "did the window I asked
for ever appear" check on the toolkit side.

**`TODO.md` 3.4 step 6, answered: the two older plugins ARE there.** In a real second window
`typeof mcptoolkitPush` and `typeof mcptoolkitEntity` are both `function`, alongside
`armorpieces_api` and the bridge — because all four are in `installed_plugins` and a new window loads
that list. So 1.9's port gap in a second window was never a loud `ReferenceError`. It was a working
push aimed at whichever game answered 25599, which is exactly the silent-and-wrong case 0.140.0's
`GAME` injection closes.

## The four pieces

The next four unbuilt pieces of **Armor Pieces: Dragonslayer**, briefs written for this run, all with
mutually disjoint envelope budgets so no session carried clearance work another did not:

| | piece | socket | bone | centre | kind |
|---|---|---|---|---|---|
| sequential | `dragon_crest` | crest | head | `dragon_breath` | small hard part |
| sequential | `dragon_horns` | horns | head | `ender_pearl` | medium hard part |
| concurrent | `dragon_spines` | pauldrons | left_arm | `amethyst_shard` | medium multi-element |
| concurrent | `dragon_tail` | belt | body | `popped_chorus_fruit` | medium multi-element |

`pack-line.md` gives a recipe centre only to `dragon_crest`; the other three were given one so that
every session did identical work. **They were dropped after the run** — a measurement is not a reason
to add craftables to a pack — and the three are reached the way the plan says the pack is reached:
the `end` loot group over `minecraft:chests/end_city_treasure` at 0.15, tag
`#armorpieces_dragon:dragonslayer`, both written when the recipes came out. Worth knowing before that
group is played: `pack-line.md` records that this table is already claimed by the mod's `court` and
`carapace` groups at the same 0.15, so three groups must resolve to one pool rolled once.

## The headline

| | min | turns | bridge | out | cache read | **$/piece** |
|---|---|---|---|---|---|---|
| **C** new plugin, alone (n=2) | 5.2 | 60 | 31 | 95k | 3.4M | **$2.19** |
| **C** new plugin, contended (n=2) | 14.3 | 123 | 59 | 159k | 13.7M | **$5.15** |
| **D** own id, alone (n=2) | 7.4 | 71 | 37 | 114k | 4.5M | **$2.67** |
| **D** own id, contended (n=2) | 11.6 | 90 | 39 | 126k | 6.1M | **$3.01** |
| **E** a window each, sequential (n=2, *void — see below*) | 7.0 | 56 | 38 | 29k | 2.9M | **$1.42** |
| **E** a window each, **concurrent** (n=2) | 5.6 | 30 | 24 | 26k | 1.4M | **$0.78** |

And the column the whole thing is for:

| | wall clock for two pieces |
|---|---|
| round 1, the solo pair in sequence | 14.8 min |
| this evening, two in sequence (void) | 13.9 min |
| this evening, **two started together** | **7.0 min** |

**Two sessions now produce two pieces in half the time one session takes to produce two.** Round 1's
concurrent pair took *longer* than sequential; this one is 2.0x faster than the sequential run beside
it and 2.1x faster than round 1's.

## What the pair actually did — which is the point

| | min | turns | bridge | `risky_eval` | `held_by` | `armorpieces_open` | window |
|---|---|---|---|---|---|---|---|
| `dragon_spines` | 4.2 | 29 | 22 | **0** | **0** | **0** | 25802 `win-nqwo9t54` |
| `dragon_tail` | 7.0 | 31 | 26 | **0** | **0** | **0** | 25803 `win-juedetll` |

The two runs are indistinguishable from solo runs, which is what round 1 could not say about either
of its concurrent pair. Read off the plugin's own claim records, every two seconds, from outside both
sessions:

```
20:02:07  both children launched
20:02:33  25801 reserved      25802 mcptk-77440           25803 mcptk-67600
20:02:48  25801 reserved      25802 …/dragon_spines       25803 …/dragon_tail
20:06:35  25801 reserved      25802 released              25803 …/dragon_tail
20:09:22  25801 reserved      25802 released              25803 released
```

Both sessions had a window in 26 seconds and their own piece in 41. Round 1's second session was
refused ten times, retried `armorpieces_new` three times, and first held a piece of its own at
10:46:09 — **9 minutes after launch and 3¼ minutes after the other session had already finished.**
`dragon_spines` finishing at 20:06 released 25802 while `dragon_tail` worked on undisturbed in 25803,
which is the claim-dies-with-the-connection half of 0.135.0 doing its job in a second window.

## Identity: evidence at last, and how

Round 1's identity column was decoration. `measure_sessions.py` read session ids out of reply text,
and the only id that appears there is the one a `held_by` refusal names — which is by definition
somebody else's, so every id it had ever collected was the *holder's* (mcp-toolkit CHANGELOG
0.140.0). Two fixes make the column evidence here:

- **`tools/mcp/server.mjs` says its own id once, on stderr, at startup** — `mcptk-<ppid>`, computed
  by the process that uses it. Nothing but that process writes that line.
- **The windows were watched from outside**, every two seconds, recording `claimed_by.session` per
  port. That sees BOTH sessions at once, which no single transcript can.

`mcptk-77440` and `mcptk-67600` are exactly the two pids the launcher printed. Two ids, two windows,
no shared-connections note anywhere. And a warning for the next reader of these numbers: a
`held_by`-shaped string in a transcript is usually a session's own project info naming **itself** as
the holder. Counting those as refusals shows 1 per sequential run here; there were none.

## Why the sequential arm is void, and what it costs the conclusion

**Both children of the sequential arm were launched with the prompt `"Build"`.** PowerShell's
`Start-Process -ArgumentList @(...)` joins an array with spaces and quotes nothing, so a multi-word
prompt arrives as many argv entries and `claude -p` takes only the first word — the same trap
`docs/plans/set-packs.md:662` recorded. Each session then went looking through `docs/plans/briefs/`
for something to do: one found `dragon_crest.md` and built it, the other read three briefs and built
`dragon_horns` instead of the `dragon_spines` it was sent for. Both pieces are correct and clean —
they were built to their briefs, and both briefs' Lessons sections are filled in — but as a
*controlled baseline* the arm is void: **25% of each run's tool calls went on orientation before
`armorpieces_new`**, which inflates every column, wall clock included.

That matters in one direction only, and it is the safe one: a padded sequential arm **flatters**
concurrency. So the honest reading is:

- The **13.9 min** sequential figure is an upper bound; a cleanly-prompted pair would land nearer 11.
- Round 1's **14.8 min** is the un-padded baseline the criterion was written against, on an older
  build.
- **7.0 min beats both by about 2x**, which is wide enough that the contamination cannot explain it.

**Do not read the $/piece column as a 3.4x cost win over era D.** These briefs pre-solve the rotation
signs and give exact coordinates — more prescriptive than round 1's — so part of the drop from 71
turns to 30 is the brief, not the bridge. The wall clock and the three zeros (`risky_eval`,
`held_by`, `armorpieces_open`) are what this run establishes; the money is suggestive and confounded.

## Still owed

A cleanly-prompted sequential pair, if anyone wants the $/piece row to mean something. It is two more
pieces and about $3, and the launcher bug that made it necessary is fixed. Nothing about the verdict
on step 2 turns on it.
