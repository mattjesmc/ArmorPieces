# The Blockbench bridge

An MCP server that stands between an agent and Blockbench. Blockbench already speaks MCP through the
[MCP Server plugin](https://github.com/jasonjgardner/blockbench-mcp-plugin), and the Armor Pieces
plugin already turns Blockbench into an editor for parts; what neither does is tell an agent, as it
works, what the plugin tells a human through the panel and what the repository's checks tell a
release. That plugin cannot be extended by another plugin, so this server sits one hop in front of
it and adds three things:

- **A profile.** The plugin registers ninety-odd tools; a part is cubes in bone groups on a rig,
  painted on three kinds of sheet, and armatures, meshes, PBR materials and animation have no
  part in it. `authoring` serves the twenty-nine that do. Names are unchanged, so a tool is still
  `mcp__blockbench__place_cube`, only its description now says what the workspace does with it.
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

Blockbench 5.1+ with the MCP Server plugin (port 3000, endpoint `/bb-mcp` - its defaults) and the
Armor Pieces plugin loaded. Node 18+ and the repository's Python. Then:

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
  "env": { "ARMORPIECES_BB_PROFILE": "authoring" }
}
```

Keeping the server name `blockbench` keeps every tool name a session has ever learned. Three
environment variables, all optional: `ARMORPIECES_BB_URL` (the plugin's endpoint),
`ARMORPIECES_BB_PROFILE` (`authoring` or `full`), `ARMORPIECES_PYTHON` (the interpreter for
`tools/`). Blockbench need not be running when the client starts: the tool list then comes from the
last live manifest, or from `blockbench-tools.json` beside the server, and the connection is made on
the first call.

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
