# The Blockbench bridge

An MCP server that stands between an agent and Blockbench. Blockbench speaks HTTP through
mcp-toolkit's own bridge plugin (`mcptoolkit_bridge.js`, 127.0.0.1:25801), and the Armor Pieces
plugin already turns Blockbench into an editor for parts; what neither does is tell an agent, as it
works, what the plugin tells a human through the panel and what the repository's checks tell a
release. Neither can be extended by another plugin, so this server sits one hop in front and adds
three things:

> **The upstream changed on 2026-09-07.** It was jasonjgardner's "Blockbench MCP" 1.6.1, MCP over
> HTTP on `/bb-mcp` with 94 tools, until mcp-toolkit 0.133.0 replaced it with the toolkit's own
> plugin: plain HTTP (`GET /hello`, `GET /tools`, `POST /cmd`), 26 argument-checked tools, a queue,
> and a **session bound to a project** so an edit to a piece another session holds is refused with
> `held_by` rather than landing in it. This server speaks that transport, and both it and the
> mcp-toolkit shim present the same `MCPTK_SESSION`, so the two are one session holding one piece.

- **A profile.** A part is cubes in bone groups on a rig, painted on three kinds of sheet; export,
  animation and the app's menus have no part in it. `authoring` serves twenty of the plugin's
  twenty-six, read from `.mcptoolkit/loop.json` so the kit and the pre-kit profile cannot drift.
  Names are unchanged, so a tool is still `mcp__blockbench__place_cube`, only its description now
  says what the workspace does with it.
- **A check after every edit.** The Armor Pieces plugin publishes the open piece after each edit
  (its model, its sheets, a `meta.json` with a sequence number, under the temp dir); after any
  editing call the bridge runs `tools/check_part.py` over that and appends the compact report to
  the reply. It is the same check every shipped part passes - `trace_geometry` for clearance and
  shared planes, the sheet checks from `sync_decoration_masters` for unpainted faces and stray or
  coloured paint - so a face that lands on the helmet shell is reported by the call that put it
  there, and "3/36 faces unpainted" is a line the model reads before it thinks it is done.
- **Piece-level tools.** `armorpieces_pieces`, `_open`, `_new`, `_check`, `_paint`, `_save`,
  `_part`, `_set_part`, `_close`. Each is the plugin's scripting surface called through
  `risky_eval`, with the bridge's traps handled here: an eval that changes nothing leaves no undo
  entry, a project is never closed inside an eval, a tab with unsaved edits is not reopened
  silently, and Save refuses while problems stand unless `force` is passed. `armorpieces_paint`
  paints whole faces by name on one sheet in one undo step - a grey, a colour, or a `[top,
  bottom]` pair shaded row by row - which is how both authoring sessions painted anyway, one
  shape-tool rectangle at a time. `armorpieces_set_part` creates the mask sheets its fittings
  need and takes the recipe, whose centre item is checked against every other template in the
  pack before Save writes it. The reply to `_open` and `_new` lists the envelopes of every other
  part on the bone, same-socket parts first, in the game's frame and Blockbench's.

Nothing else changes hands. Blockbench remains the editor; the checks remain the repository's
Python; the bridge is wiring, and `check_part.py --status` prints the same report by hand.

## Setup

Blockbench 5.1+ with two plugins loaded from file: mcp-toolkit's `blockbench/mcptoolkit_bridge.js`
(then Tools > MCP Toolkit Bridge > Start, and allow `process` once - it binds 127.0.0.1:25801) and
the Armor Pieces plugin. Node 18+ and the repository's Python. Then:

```
cd tools/mcp && npm install
```

and point the client at the server. For Claude Code, in `.mcp.json` (kept out of git - it holds
absolute paths):

```json
"blockbench": {
  "type": "stdio",
  "command": "node",
  "args": ["<repo>/tools/mcp/server.mjs"],
  "env": {
    "ARMORPIECES_BB_PROFILE": "${ARMORPIECES_BB_PROFILE:-kit}",
    "MCPTK_SESSION": "${CLAUDE_CODE_SESSION_ID:-armorpieces}"
  }
}
```

`MCPTK_SESSION` must be **the same string the mcptoolkit server gets**. That is what makes the two
processes one session to the plugin: the piece this server opens is bound, and the shim's
`place_cube` goes to it by name rather than to whichever tab is active. Two different ids would make
them refuse each other.

Keeping the server name `blockbench` keeps every tool name a session has ever learned. Three
environment variables, all optional: `ARMORPIECES_BB_URL` (the plugin's endpoint),
`ARMORPIECES_BB_PROFILE` (below), `ARMORPIECES_PYTHON` (the interpreter for `tools/`). Blockbench
need not be running when the client starts: the tool list then comes from the last live manifest, or
from `blockbench-tools.json` beside the server, and the connection is made on the first call.

## The kit split

Since mcp-toolkit 0.123.0 the toolkit's own shim does everything the first two bullets above
describe - a project keep-list over Blockbench's manifest, notes appended to descriptions, an
instructions paragraph, a checker run after every editing call - out of `.mcptoolkit/loop.json`
(the toolkit's `docs-release/LOOPS.md`). This repository takes it, so the default profile is now
`kit`: this server serves ONLY its nine piece tools, and `mcp__blockbench__place_cube` comes from
`mcp__mcptoolkit__place_cube` instead. That loop file is also where the keep-list and the
description notes are WRITTEN - `profile.mjs` reads them, rather than keeping a second copy that
went on annotating `paint_with_brush` for weeks after the plugin that had it was replaced.

| Profile | Blockbench | This server's own | For |
|---|---|---|---|
| `kit` (default) | none - the shim serves them | the nine part tools | part authoring, with `.mcptoolkit/loop.json` |
| `kit_skin` | none | the eight skin tools | skin authoring, same split |
| `authoring` | 29 | all 17 | the pre-kit loop, one server; still works |
| `full` | 94 | all 17 | debugging the bridge itself |

What it is worth, as `node tools/mcp/check_kit.mjs` prints it at the top of a run: `kit` plus the
shim's project profile is **28 tools and ~6.4k tokens** of manifest on **every turn** of a 40-turn
session (9 tools ~1.7k here, 19 ~4.7k there). It was 39 tools and ~8.6k against the old plugin, and
46 and ~10.4k under `authoring` before the split - the drop is the plugin's own doing, since its 26
tools replace the 94 by folding families behind an `op`.

One thing the split has to get right, and it is why `runCheck` here shells out to
`tools/check_active.py` rather than to `check_part.py`: the sheet-layout block and the `! repaint:
faces that were complete and grew` line are DIFFS against the last check, and in a kit session two
servers edit one piece. Two histories means a face painted through this server and grown through
the shim compares against a state where it was never painted, and the regrow - the whole reason
the diff exists - goes unsaid. `check_active.py` owns one history file beside the piece's status
directory; both servers read it. `node tools/mcp/check_kit.mjs` is the live arbiter for all of
this: it opens a shipped piece, edits it through both servers, asserts the check, the layout block,
the regrow line and the picture budget, and closes without saving.

## What the model is told

The server's `instructions` (in `profile.mjs`) are the one paragraph every session should read
before its first call, and `.claude/agents/part-author.md` is the profile for a session that
authors one part: the same tools, the brief, and what a finished part consists of.

> Blockbench is running with the Armor Pieces plugin, which opens a part as a tab on the vanilla
> player wearing real armor and saves it back into its pack. All Blockbench tools act on the ACTIVE
> tab, so open the piece first, and do not run two agents against one Blockbench. Model inside the
> `part` group only, every cube in a bone group, in Blockbench coordinates; the game's geometry is
> written by the plugin on save. Cubes cannot rotate; rotate the bone group. Mirrored sockets model
> one side. Box UV is automatic. Sheets: `part` (master, greyscale), `part_static` (colour),
> `part_<fitting>` (masks). After every editing call the reply ends with an `[armorpieces]` block:
> `!` lines need a decision before saving, `-` lines are notes.

## Running a part session

One fresh session per part, sequentially - every Blockbench tool acts on the active tab. Write a
brief under `docs/plans/briefs/<part>.md` (the existing ones are the pattern: part, socket,
shape, sheets, a flat item as recipe centre that no template uses, and an empty "Lessons"
section), then from the repository root:

```
claude -p --agent part-author --model <model> --dangerously-skip-permissions \
  "Build the Armor Pieces part described in docs/plans/briefs/<part>.md. Read the brief, then
   author the part through the Blockbench bridge tools. Blockbench is running with the plugins
   loaded. When it is saved clean and the checks pass, fill in the brief's Lessons section and
   give a short final report."
```

The four runs of 2026-09-03 (nasal, spire, antennae, horsetail) went from 76 turns and hand
workarounds to about 20 bridge calls and two paint calls per part; the briefs' Lessons sections
record what each one found.

## Running a skin session

An **armor skin** is the other thing this bridge opens: the armor's own texture rather than a part
hung on it - one greyscale pair, `humanoid` and `humanoid_leggings`, 64x32 on vanilla's grid, under
`tools/skin_masters/<name>/`. Nothing is modelled, so the tools are different ones:
`armorpieces_skins`, `_open_skin`, `_skin_sheet`, `_skin_paint`, `_skin_material`, `_skin_check`,
`_save_skin`, `_close_skin`, and the check after every edit is `tools/check_skin.py`.

The sheets are read and written as ASCII - `.` transparent, `0`-`9` and `a`-`f` the sixteen greys, a
space for "leave this texel alone" - and a paint call is addressed by net and face
(`region: "chest", face: "front"`), so a stamp that would run off the face is refused instead of
landing somewhere wrong. `armorpieces_skin_material iron` shows the bake in the viewport, live.

Same shape as a part session: one fresh session per skin, sequentially, a brief under
`docs/plans/briefs/skins/<skin>.md`, and

```
claude -p --agent skin-author --model <model> --dangerously-skip-permissions \
  "Draw the Armor Pieces armor skin described in docs/plans/briefs/skins/<skin>.md. Read the brief,
   then draw it through the Blockbench bridge tools. Blockbench is running with the plugins loaded.
   When it is saved clean and the checks pass, fill in the brief's Lessons section and give a short
   final report."
```

`python tools/skin_sheets.py --regions` prints the seven nets and every face rectangle;
`--vanilla netherite` prints a vanilla pair as a drawing to work from; `python tools/bake_skin.py
--report` prints what each armor material's ramp comes out as.

## Reading the check

```
[armorpieces] antlers on horns (head): 9 cubes; reach 17.3; past helmet x+5.96 y+11.49 z+2.76; shares head with circlet:brow, ...
  ! COPLANAR: burr and circlet:brow's band share the plane x = 6
  ! paint: 6/54 faces have no paint behind them and render as holes unless cut on purpose: burr[1].north, ...
  - 8 note(s); armorpieces_check lists them
  2 problem(s) need a decision before Save (armorpieces_save refuses without force)
```

A **problem** is something the part cannot ship with unless someone decides otherwise: a face on
the part's own armor shell (it z-fights; move it), a plane shared with another part that can be worn
at the same time, a face with no paint behind it (a hole, unless cut on purpose - the feathering
cuts three), paint no face samples, colour on a greyscale sheet, a static or mask pixel outside the
master's silhouette. A **note** is a datum: a face buried under an outer layer, a hull overlap, a
near miss, a pair wider than the shoulders. `armorpieces_check` prints all of it in the form
`trace_geometry.py` always has; the compact block is what rides on every reply.

## The in-game passes

The bridge stops at Blockbench. The four in-game passes a part is judged by after the arithmetic -
worn on each armor material, in each pose, with each fitting filled - run through the MCP Toolkit
bridge into the game (`mcptoolkit` in `.mcp.json`, profile `standard`), with `/armorpieces stage`
putting the part on the player. That is the orchestrator's step, after a part is saved, not the
part author's.
