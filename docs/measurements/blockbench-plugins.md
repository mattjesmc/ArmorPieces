# The two Blockbench plugins, measured

Every Armor Pieces part built by a headless session left a transcript. Those transcripts are the
only record of what each generation of tooling cost, and they live in `~/.claude/projects/`, which
is not ours and is not backed up — so `python tools/measure_sessions.py --archive` copies them into
`.mcptoolkit/runs/archive/<era>/` (69 transcripts, 47 MB, gitignored) and writes
`measurements.json` beside them. Re-run it after any batch; it is idempotent.

Four eras, detected from the tool names a session actually called rather than from its date —
except the C/D boundary, which is a date, because what changed there is who each session says it is:

| era | Blockbench served by | tool names |
|---|---|---|
| **A** one server | `tools/mcp/server.mjs` served Blockbench itself | `mcp__blockbench__*`, third-party plugin's 94 |
| **B** kit split | the toolkit's shim; Blockbench still the **third-party** plugin | `paint_with_brush`, `remove_element`, … |
| **C** own plugin | the toolkit's shim; Blockbench is **mcp-toolkit's own bridge** | `element`, `texture`, `inspect`, … (26) |
| **D** own id | the same 26 tools, but each session presents its **own** `mcptk-<ppid>` | same as C; the boundary is a date, not a name |
| **E** a window each | the same 26 tools, but each session works in its **own Blockbench window** | same as C/D; the boundary is a date, and `claimed_by` is the evidence |

## The comparison that matters

Like for like: pack pieces, same brief shape, same model (Sonnet 5), one session per piece.

| | min | turns | bridge calls | out | cache read | **$/piece** |
|---|---|---|---|---|---|---|
| **B** Animals, old plugin, alone (n=5) | 8.9 | 70 | 28 | 82k | 4.3M | **$5.14** |
| **C** Coral, new plugin, alone (n=2) | 5.2 | 60 | 31 | 95k | 3.4M | **$2.19** |
| **C** Coral, new plugin, **contended** (n=2) | 14.3 | 123 | 59 | 159k | 13.7M | **$5.15** |
| **D** Dragonslayer, own id, alone (n=2) | 7.4 | 71 | 37 | 114k | 4.5M | **$2.67** |
| **D** Dragonslayer, own id, **contended** (n=2) | 11.6 | 90 | 39 | 126k | 6.1M | **$3.01** |
| **E** Dragonslayer, a window each, sequential (n=2, *void*) | 7.0 | 56 | 38 | 29k | 2.9M | **$1.42** |
| **E** Dragonslayer, a window each, **concurrent** (n=2) | 5.6 | 30 | 24 | 26k | 1.4M | **$0.78** |

**Era E reverses the verdict below: two sessions started together produced two pieces in 7.0
minutes, against 14.8 sequential.** `risky_eval`, `held_by` and `armorpieces_open` are all 0 in both
concurrent runs, each session claimed a Blockbench window of its own within 26 seconds, and the
window a person had reserved was never touched. Two caveats travel with those rows and are argued in
`CONCURRENCY_AB.md`'s round 2: the E *sequential* arm is **void as a baseline** — a launcher quoting
defect gave both its children the prompt `"Build"`, so each spent about a quarter of its calls
choosing a piece before starting — and the **$/piece drop is confounded**, because round 2's briefs
pre-solve the rotation arithmetic that round 1's did not. The wall clock and the three zeros are what
era E establishes; the money is suggestive.

Everything below this line is the era-D reading, kept as written.

**Contention now costs 1.13x per piece instead of 2.4x — and is still not worth doing.** The
identity fix plus a binding fix (below) brought the *alone* row back to the C era's shape, and the
contended row is no longer a catastrophe. But the money is the wrong column: two sessions started
at the same second produced two pieces in **16.4 min**, against **14.8 min** for the same two built
one after the other. Concurrency bought negative wall clock, because it did not happen.

The pair is not two halves of one experience. `dragon_scales` won the window and ran like a solo
piece (6.7 min, 64 turns, 0 `held_by`). `dragon_talons` was refused **10 times** with
`held_by: session mcptk-13676 is bound to "dragon_scales"`, retried `armorpieces_new` three times,
and first held its own piece at 10:46:09 — **3¼ minutes after `dragon_scales` had finished**. A
session has no binding until it has a piece, so `armorpieces_new` has nothing to name and resolves
against the active tab, which in one window belongs to whoever is working. `risky_eval` was **0**
in both runs and nothing was corrupted: the guards hold, the failure is safe but total. That is the
case for `BLOCKBENCH_ISOLATION_DESIGN.md` step 2, on wall clock rather than on damage.

**The binding fix that made the D rows legible.** A first batch measured $6.16 for a *solo* piece.
`evalIn`'s no-project retry creates the scratch with `project op:new`, which *binds the session to
what it makes*, and `dropScratch()` closed it only `if (s !== Project)` — so when the scratch was
the active project it was never closed and the session stayed **bound to the scratch**, resolving
every call there by binding (`armorpieces_scratch bound:true` 28 times in one transcript). And
`evalIn` gates its wrong-project arbiter on `if (bound)`, this server's own local, which
`bindActive()` left `null` — so the guard was off in exactly the state that trips it. Fixed
2026-09-08: `bindActive()` finds the piece among `ModelProject.all` by key and `op:select`s it,
`dropScratch()` closes through `project op:close` after the bind, and `armorpieces_new` registers a
pack root it was told to write into. Same piece, same brief, before and after:

| `dragon_knuckles` | min | turns | bridge | `risky_eval` | "no piece is open" |
|---|---|---|---|---|---|
| before | 14.5 | 188 | 90 | 23 | 30 |
| after | **5.6** | **65** | **31** | **0** | **0** |

*Identity:* every session presented its own `mcptk-<ppid>` and no reply carried the plugin's
shared-connections note. Contention is no longer an id collision; what remains is the shared window.

**The new plugin costs 57% less per piece and finishes 42% faster** — when the session has
Blockbench to itself. Contention erases the entire gain and then some.

### Why the contended runs cost what they did

Not the plugin's fault, and worth stating precisely because the number is so large. `.mcp.json`
derived `MCPTK_SESSION` from `CLAUDE_CODE_SESSION_ID`, and **a headless `claude -p` child inherits
its parent's copy of that variable**. So all four Coral children presented one session id, were one
session to the plugin, and shared **one binding**. The plugin then did exactly what it promises: it
sent every call that did not name a project to the bound project — which was another piece.

The tool mix shows the damage in one line:

| | `risky_eval` | `armorpieces_check` | `armorpieces_part` | `armorpieces_open` | `armorpieces_paint` |
|---|---|---|---|---|---|
| B alone | 0.0 | 1.4 | 0.4 | 0.8 | 3.4 |
| C alone | 0.0 | 2.5 | 0.5 | 0.0 | 3.5 |
| C contended | **11.5** | 6.5 | 4.5 | 4.5 | **0.0** |
| D alone (n=2) | **0.0** | 5.0 | 0.0 | **0.0** | 1.5 |
| D contended (n=2) | **0.0** | 3.0 | 0.5 | **0.0** | 3.0 |

A contended session re-opened its piece four times, checked six, and abandoned `armorpieces_paint`
entirely for hand-written `risky_eval` with a guard clause — which is a sensible thing for an agent
to do and an expensive one. **`risky_eval` is 0.0 in the clean runs of *both* eras**: the escape
hatch is only reached for when the tools stop being trustworthy, which makes it a good health
metric.

Two fixes went in (2026-09-07): `.mcp.json` now takes the id from `ARMORPIECES_SESSION`, which a
launcher sets per child and nothing inherits by accident; and `tools/mcp/server.mjs` names its
project on **every** eval and refuses a reply that came back about a different piece. The second is
the real fix — it holds even if two sessions do share an id.

## What the new plugin changed, by the numbers

| | B (old) | C (new) | |
|---|---|---|---|
| `add_group` | 5.3 | 3.2 | bones are placed once instead of rebuilt to rename them |
| `element` | — | 6.5 | replaces `remove_element` + `rename_element` + `duplicate_element`, and adds `set` |
| `remove_element` | 1.5 | — | folded into `element` |
| `set_camera_angle` | 2.7 | ~0 | `capture_screenshot {views}` composes one contact sheet |
| `place_cube` | 4.3 | 4.0 | unchanged in count, but now batched per call |

The three traps that died with the old plugin (verified live, then confirmed by the sessions):
renaming a **bone** works, undo leaves no ghost cube, and `texture op:rects {c: null}` clears.
The first was load-bearing — the axolotl session called it "the backbone of the whole session",
because "build it straight, look at it, then rotate the bone" replaces precomputing sines by hand.

Manifest cost of the split, from `node tools/mcp/check_kit.mjs`: **28 tools, ~6.4k tokens per
turn** (9 from the proxy, 19 from the shim), against 39 and ~8.6k on the old plugin and 46 and
~10.4k before the split.

---

# Suggestions for mcp-toolkit

> **Answered, same day.** mcp-toolkit **0.135.0 / shim 0.65.0 / plugin 0.2.0** ships asks 1-4 and 6;
> ask 5 is written up in the toolkit's `TODO.md` 1.7 with the arithmetic. This repository is on it:
> the pin is 0.135.0, `run/mcptoolkit/mcp-server` is re-extracted (an old shim never opens
> `/presence`, and the plugin then falls back to the timer), the running Blockbench was reloaded
> from 0.1.1, and `tools/mcp/server.mjs` now asserts `PROJECT` inside every eval. `check_kit.mjs` is
> green against all three.
>
> Two notes from that upgrade. The refusal message changed - it ends in `connected` instead of
> `seen Ns ago` - and our arbiter survived only because it matches `/held/i` over error+hint rather
> than the timestamp wording; anything matching the old phrasing goes red on load. And the arbiter's
> own last assertion was environment-dependent (it assumed no other piece tab was open) and is now
> written against the invariant it meant.

Ordered by what the evidence supports, not by how easy they are.

### 1. `risky_eval` should hand the resolved project to the code it runs  *(shipped in 0.135.0)*

This is the one that cost real money. A plugin-hosted API reached *through* `risky_eval` —
`window.armorpieces_api`, and the toolkit's own `mcptoolkitPush` / `mcptoolkitEntity` — reads
Blockbench's **global** `Project`. The eval's `project` argument selects the tab before the code
runs, which is correct, but the code has no way to *assert* what it got, so a resolution that lands
on the wrong tab is silent and writes.

Ask: bind the resolved project into the eval's scope (a `PROJECT` local, or `this.project`), so a
plugin API can be written as `api.save(PROJECT)` instead of reading the global. Cheap, and it makes
every third-party plugin reachable through the bridge safe by construction rather than by the
caller remembering to pass `project`.

### 2. A binding should die with its connection, not only on a timer  *(shipped in 0.135.0)*

The binding on `coral_crown` outlived the session that made it: later children reusing the same id
kept it "seen 15s ago" indefinitely, and it then **refused a cleanup call from the human's own
session**. Expiring on last-seen is right for a crashed client; it is wrong for one that closed.
Ask: release a binding when the connection that holds it goes away, and let `project op:list` show
`held_by.stale: true` rather than a fresh timestamp for an id nothing is actually using.

### 3. Warn when one session id arrives from two processes  *(shipped in 0.135.0)*

The failure was invisible: three processes, one id, no error anywhere. The plugin sees the PIDs'
sockets even if the id is identical. Ask: when `/cmd` receives the same `session.id` from
concurrent connections, put one `note` on the reply — `"session id shared by 2 connections; a
binding cannot distinguish them"`. One sentence would have saved this batch about $6 and an hour.
Related and cheaper: say in `LOOPS.md` that `MCPTK_SESSION` must not be derived from a variable a
child process inherits.

### 4. `inspect` earns no manifest space yet  *(shipped in 0.135.0)*

Not one session in either era called `inspect`, including the two that needed exactly what it
offers (stray paint after a re-lay). The information it returns already rides on the reply to
`place_cube` / `modify_cube`, so agents read it there. Either drop it from the `art` keep-list, or
give its description the one sentence that says when it beats the edit reply — *"after a rework,
for the faces you did not just touch"*. It is ~1 entry of prefix on every turn of every session.

### 5. Consider mid-session `tool_surface` narrowing as a documented pattern  *(accepted; toolkit TODO.md 1.7)*

Cache reads are 3.4M per piece — about a third of the run's cost — and they are dominated by the
per-turn prefix. A part session has two clean phases: modelling, then painting. Nothing in the
painting half calls `place_cube`, `add_group` or `element`. `tool_surface` already exists; what is
missing is a worked example of a loop file declaring **phases** so the shim can drop half the
manifest at a phase boundary. This is the biggest remaining lever on cost that is not the model.

### 6. Small things the transcripts show  *(shipped in 0.135.0)*

- `capture_screenshot {views}` is a clear win (2.7 `set_camera_angle` calls per piece → ~0). Worth
  promoting in the tool description from an option to the recommended path.
- `armorpieces_check` rose from 1.4 to 2.5 calls per piece between eras even in the clean runs.
  Worth checking whether the check block appended to edit replies got less informative under the
  new mechanism stamp, since an explicit re-check is a wasted turn.
- ArgCheck refusing an undeclared argument **by name** (`undeclared argument(s) cubes; declared:
  project, elements, …`) was correct and immediately actionable in the one case it fired here.
  Keep it.

---

# Orientation, re-measured on the new bridge (2026-09-08)

Every mechanism this repository built to keep a session from researching its way to the start line is
still in place and still current — envelopes riding on `armorpieces_open`/`_new`, face rectangles on
the call that moved them, the check on every reply, the priced keep-list, the rig frame inline in the
agent profile, the brief carrying the numbers. They work: **a cleanly-prompted session now spends 3
calls, about 10% of its run, before it has its piece** — read its brief, read one other brief,
`armorpieces_pieces`.

So the calls were not the problem. Ranking context by what it actually costs — bytes multiplied by
the turns still to come, which is what the cache-read column is — found the problem somewhere else:

| source | calls/run | tok each | **tok/turn carried** |
|---|---|---|---|
| `Read` (two briefs) | 2.0 | 2,714 | **5,084** |
| `list_outline` | 1.0 | 1,305 | 1,051 |
| `place_cube` | 4.5 | 379 | 977 |
| `armorpieces_new` | 1.0 | 1,000 | 860 |
| `armorpieces_check` | 1.5 | 1,845 | 828 |
| `armorpieces_pieces` | 1.0 | 847 | 749 |
| **all tool results** | 29 | 555 | **10,620** |
| *manifest floor on top* | | | *7,358* |

**Reading briefs was 48% of everything a session carried**, and half of that was the line in every
brief telling it to skim a sibling's Lessons section for technique. That line had rotted: **52 of the
77 briefs teach the third-party plugin's tools** — `remove_element`, `rename_element`,
`draw_shape_tool`, `paint_with_brush`, `activate_texture` — which two bridge changes have since
removed, and at least one makes a claim that is now false. The most expensive thing a session read
was also the least accurate.

**What changed.** `docs/plans/briefs/LESSONS.md` is new: the technique the current-bridge sessions
worked out, distilled to sixteen numbered items — build straight then aim, budget for the corner not
the centreline, a rotated bone moves its base too, `inspect bounds` measures a rotated cube by its
unrotated box, `!` needs a decision and `-` does not, one paint call, and the `FileNotFoundError`
workaround. `part-author.md` and `part-author-kit.md` now send sessions there and tell them **not** to
skim other briefs for technique; a brief is opened only for a named neighbour's numbers. The 52 stale
Lessons sections keep their content — they are the record of what each piece cost — under a banner
saying which bridge they were written on.

**And the keep-list was re-cut on the same evidence.** Eleven of the nineteen served tools were never
called in any of the four runs (~2,488 tok/turn, 49% of the shim's manifest). Four came out —
`set_camera_angle` (superseded by `capture_screenshot {views}`, measured 2.7 calls per piece → 0),
`find_elements_by_criteria`, `get_selection`, `redo` — for 534 tok/turn. The other seven stayed on
purpose, and the reason is written into `.mcptoolkit/loop.json` so nobody finishes the job later:
`texture`, `get_texture` and `inspect` are the rework tools and none of these four pieces reworked;
`undo` and `get_undo_stack` are the same insurance; and **`risky_eval` is the health metric** — 0.0 in
every clean run of every era, 11.5 in the contended C-era ones — so removing it would hide the signal
that says the tools have stopped being trustworthy.

Honest sizes, so the next reader spends effort in the right place: the manifest cut is worth about a
third of a cent a piece. The reading change is worth roughly ten times that, and it also stops
sessions being taught tools that do not exist. The next real lever is neither — it is mid-session
phase narrowing (mcp-toolkit `TODO.md` 1.7): nothing in the painting half of a session calls
`place_cube`, `add_group` or `element`.

## Validated, on one piece (`dragon_mask`, 2026-09-08 22:27)

The change was aimed at one number, so that number is what was checked. Same agent, same model, same
launcher, brief written to the new convention:

| the session's second read | tok | carried |
|---|---|---|
| `wing_tatters.md` — `dragon_spines`, before | 3,391 | 3,108 tok/turn |
| `wing_tatters.md` — `dragon_tail`, before | 3,391 | 3,144 tok/turn |
| **`LESSONS.md` — `dragon_mask`, after** | **1,748** | **1,674 tok/turn** |

**A 48% cut on the thing that was changed**, and what it now reads is current instead of teaching six
tools that no longer exist. With the keep-list re-cut on top, a session carries about **1,980 tok/turn
less** than it did that afternoon. Orientation is 3 calls and 8% of the run; the own-brief read is
unchanged at ~2,000 tok, which is right — that one is the piece's own numbers.

**What did NOT get cheaper, said plainly.** The run was longer than either concurrent run (71 turns
against 48 and 55) and carried *more* in total (12,338 tok/turn of results against 10,620). Three
reasons, and none of them is the intervention: this brief asked for work the others did not (edit the
pack's loot tag, and contribute back to `LESSONS.md` — 3 `Edit` calls and a fourth read), the session
hit a real snag and wrote it up (item 7b: a bone and a cube sharing a name make `element set` refuse
by name), and `armorpieces_check` ran 3 times against 1–2. Run-level cost lands in the same band as
the correctly-prompted runs either way — **$0.87 against $0.58 and $0.99** — with `risky_eval`,
`held_by` and `armorpieces_open` all still 0.

So: the lever moved as designed and the piece is correct (5 bones, 5 cubes, saved without `force`,
`check_authoring` clean, and the session added itself to the loot tag). A single run cannot say what
the change is worth end to end, and this one is not a like-for-like; what it establishes is that the
substitution works and costs nothing.

**And the channel works in both directions**, which was the other half of the point: the session
appended two items to `LESSONS.md` rather than burying them in its own brief where the next session
would not look. That is the file accumulating instead of 78 briefs accumulating separately.
