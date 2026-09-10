# How a batch of briefs is run

**This file is for whoever launches the sessions, not for the sessions themselves.** A part session
reads its own brief and `LESSONS.md`, and nothing here. What is written down here is the workflow
around them: how a batch is started, what it needs to be true beforehand, where everything it
produces is kept, and what is still owed once the last session exits.

The workflow itself is `tools/run_briefs.ps1`. It exists because the batch had been re-remembered
every time, and each time it cost something: a batch launched with the prompt `"Build"`, a session
whose two halves bound to different Blockbench windows, transcripts that were only found because
nobody had cleared `~/.claude/projects` yet.

    .\tools\run_briefs.ps1 wither_mask wither_heads wither_ribs
    .\tools\run_briefs.ps1 -MaxConcurrent 3 -Model sonnet brute_belt magma_cops soul_greaves
    .\tools\run_briefs.ps1 -DryRun -AllowBusyWindow dragon_wings      # plan only, launch nothing

## What has to be true before you start

- **One Blockbench window per concurrent session**, each running the mcptoolkit bridge plugin, each
  with **nothing open in it**. The plugin takes the first free port at or above 25801, so the port
  names the window; `run_briefs.ps1` prints the whole table before it launches anything. A window
  that still holds another piece's tab is refused unless you pass `-AllowBusyWindow`, because a
  leftover tab is the active tab for whoever claims that window next.
- **No stale claim.** A window stays claimed by a session that has already exited, and an *idle
  interactive* session — a `qwen -Brief` left open in a terminal, say — keeps its claim fresh
  forever. The runner treats a claim seen in the last 120 seconds as live and will not take that
  window. Close those sessions before a batch; they are usually the reason there are no free windows.
- **The right repository.** The agent profile and `.mcp.json` are found from the working directory,
  so the batch runs from the repo root. The runner refuses to start anywhere else.
- **A listener on 25599 is the Minecraft dev client**, not Blockbench. Do not let a preflight mistake
  it for one: an open port proves nothing about who is behind it, which is why the runner asks
  `/hello` who it is talking to instead of testing whether a socket opens.

## The four traps, and why the script looks the way it does

1. **The prompt goes on stdin.** `Start-Process -ArgumentList @(...)` joins the array with spaces and
   quotes nothing, so a multi-word prompt reaches `claude -p` as many argv entries and only the first
   word survives. On 2026-09-08 both children of an A/B arm were launched with the prompt `"Build"`;
   neither crashed, both went looking through the briefs for something to do, one built a different
   piece than it was sent for, and the arm was void as a measurement. The prompt is written to a file
   and passed with `-RedirectStandardInput`.

2. **Do not watch the PID.** `claude.exe` is a launcher shim and exits immediately while the real
   session runs on. A run is **finished** when its stream-json log carries a `"type":"result"` line,
   and **stalled** when nothing has been written to that log for `-StallMinutes`. Watching the
   process would call every run finished about a second after it started.

3. **Pin both halves to one window, and share the identity — and pin the right variable.** A session
   has two servers: the armorpieces proxy (`tools/mcp/server.mjs`, the nine piece tools) and the
   toolkit's shim (Blockbench itself). The proxy takes `ARMORPIECES_BB_URL`; **the shim's Blockbench
   adapter takes `MCPTK_BLOCKBENCH`** — `MCPTK_URL` is its *Minecraft* upstream and defaults to
   25599, so setting that pins nothing. Unpinned, the adapter range-scans 25801-25816 and **claims a
   window of its own**, so the piece sits in the proxy's window while every `mcp__mcptoolkit__*` call
   answers `no project is open ... (open: (none open))`. Both must also share `MCPTK_SESSION`, or the
   proxy falls back to `mcptk-<parent pid>` while the shim lets the bridge assign it one.

   All three (`MCPTK_BLOCKBENCH`, `ARMORPIECES_BB_URL`, `MCPTK_SESSION`) are set per session before
   each launch **and named in `.mcp.json`'s `env` blocks** as `${VAR:-}` — a variable the config does
   not interpolate never reaches the server, whatever the launcher exported. Both servers already
   treat an empty value as unset, so an interactive session is unaffected.

   This cost the `wither_mask` run of 2026-09-09 its entire turn budget: the session created the
   piece, could not place a single cube, and honestly reported the piece unbuildable rather than
   saving the starter cube. `LESSONS.md` 17-18a is the session-side diagnosis and the
   `POST /cmd` fallback a later session used to build a whole piece through the raw bridge.

4. **The transcripts are not ours.** They live in `~/.claude/projects/<slug>/<session id>.jsonl`,
   which nothing backs up. Every finished run is copied into `.mcptoolkit/runs/archive/E/` the moment
   it ends, and the batch manifest records the session id and where the copy went. If a run's session
   id cannot be read out of its log, the runner says so **in red**: that is a transcript about to be
   lost, and it is worth going and finding by hand
   (`ls -t ~/.claude/projects/C--Users-Matthijs-ArmorPieces | head`).

One more, found while writing the runner and worth knowing in any PowerShell here:
**variable names are case-insensitive**, so `$runs = @()` silently overwrote the `$RUNS` directory
constant and `$live` overwrote a `$LIVE` timeout — the first produced "cannot bind Path because it is
an empty array" three functions away, the second made every window's claim look stale. Directory
constants in this script carry a `_DIR` suffix for that reason.

## Cleaning up after a session

A session's last tool call is `armorpieces_close`, and the prompt the runner pipes in says so three
ways: close when finished, close with `discard: true` when abandoning the piece, and close before
stopping to ask a question. The reason is not tidiness — **the window is handed to the next piece**,
and a tab left open is the tab that session finds active.

The runner checks rather than trusts. When a run ends it asks that window's `/hello` again and
compares the project count with what the window held at launch:

- **clean** — the count did not grow and the active tab is not this piece: printed as a grey note;
- **not clean** — printed in yellow, recorded in the manifest as `clean_exit: false` and
  `left_open: <n>`, and **that window is dropped from the pool for the rest of the batch**, so no
  later piece is handed somebody else's tab.

Windows only ever leak forward, so a batch that ends with a yellow line has left tabs for you to
close by hand. `left_open` in the manifest is the count.

## What a batch leaves behind

Everything lands under `.mcptoolkit/runs/`:

| file | what it is |
|---|---|
| `<agent>-<piece>-<stamp>.jsonl` | the run's own stream-json output — the live progress signal |
| `<agent>-<piece>-<stamp>.stderr.log` | anything the child wrote to stderr |
| `<agent>-<piece>-<stamp>.prompt.txt` | the exact prompt that was piped in, verbatim |
| `batch-<stamp>.json` | the manifest: piece, brief, window, port, session id, minutes, turns, cost, and the path of the archived transcript |
| `archive/E/<piece>--<session id>.jsonl` | **the transcript**, copied out of `~/.claude` |

**Where the corpus is.** Everything archived up to 2026-09-10 — 176 files, 71 MB, eras A-E plus
`E-qwen` — was moved to `anon@192.168.0.105:~/texture-vlm/newresults/` and deleted here (verified
byte-identical by md5 first; `.mcptoolkit/runs/MOVED.md` is the pointer). New batches still write
here. A transcript carries its own screenshots as base64, so it travels alone.

`python tools/measure_sessions.py` reads that archive and prints the eras side by side;
`--archive` sweeps in anything the runner missed. **Era E** is "a window each" — mcp-toolkit 0.140.0
onwards, from 2026-09-08 evening, which is what these batches run on.

**A qwen batch's transcripts are somewhere else.** `qwen -Brief` sets
`CLAUDE_CONFIG_DIR=~\.claude-qwen`, so those sessions write to `~/.claude-qwen/projects/<slug>/` and
`measure_sessions.py` does not look there. Copy them by hand into the archive if a qwen run is worth
keeping.

## What is still owed when the last session exits

A clean check is **not** evidence that the right piece was built — the check knows the rig and the
neighbours, and knows nothing about the brief. So, per piece:

1. **Read the geometry against the brief.** `packs/<pack>/resourcepack/assets/<ns>/armorpieces/
   decoration/<piece>.json` holds the cubes in the anchor's own frame; the brief's numbers are in
   Blockbench world. Confirm the spans, the cube count, and — where the brief gave a tip table — that
   the rotations landed where it said.
2. **Check the data half.** Fittings, effects, loot rows and the recipe centre, and the language line
   in the pack's `lang/en_us.json`.
3. **Run the pack's own checks**: `python tools/check_authoring.py packs/<pack>/datapack
   packs/<pack>/resourcepack`, and `python tools/check_pack_line.py` once for the whole line.
4. **Read the brief's Lessons section**, which the session fills in, and promote anything that
   generalises into `LESSONS.md` — that file is the channel; 78 separate briefs are not.
5. Only then commit. `packs/` pieces are not on the mod's page: do **not** run `python -m modpage
   build` for them.
