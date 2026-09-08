// What an agent authoring a part sees of Blockbench, and what it is told.
//
// Blockbench's own bridge is `mcptoolkit_bridge.js` (mcp-toolkit 0.133.0+), which registers 26
// tools. A part is cubes in bone groups on a rig the Armor Pieces plugin builds, painted on three
// kinds of sheet, and animation, export and the app's menus have no part in it. The `authoring`
// profile is the slice that does, plus the piece-level tools the proxy adds. `full` is everything,
// for debugging the bridge itself. Set ARMORPIECES_BB_PROFILE to choose.
//
// `kit` is the third, and it is a SUBTRACTION. Since mcp-toolkit 0.122.0 the toolkit's own shim
// does everything this file describes - a project keep-list over Blockbench's manifest, notes
// appended to descriptions, an instructions paragraph, a checker run after every editing call and a
// save gate - from `.mcptoolkit/loop.json` (mcp-toolkit docs-release/LOOPS.md). Under `kit` this
// proxy therefore serves NO upstream tool and none of the skin tools: only the nine part tools that
// are genuinely ours, so the two servers do not both offer place_cube and the manifest is paid for
// once. That split is what `.claude/agents/part-author-kit.md` is written against.
//
// ONE SOURCE FOR THE SLICE (2026-09-07). The keep-list and the notes below are READ FROM
// `.mcptoolkit/loop.json` rather than written here twice. The kit is the production path, so its
// file is the one that is kept true; a second hand-kept copy here is how `authoring` came to be
// annotating `paint_with_brush` and `save_checkpoint` months after the plugin that had them was
// replaced. When the loop file cannot be read, `authoring` still serves a slice - it just serves it
// without the traps, and says so on stderr.

import { readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const LOOP_FILE = join(resolve(dirname(fileURLToPath(import.meta.url)), "..", ".."), ".mcptoolkit", "loop.json");

function loopProfile() {
  try {
    return JSON.parse(readFileSync(LOOP_FILE, "utf8")).profile ?? {};
  } catch (e) {
    process.stderr.write(`[armorpieces-bridge] no keep-list or notes: ${LOOP_FILE} (${e.message})
`);
    return {};
  }
}
const LOOP = loopProfile();

/**
 * Upstream tools that never edit the project, so no check runs after them.
 *
 * A FALLBACK ONLY: every entry in the plugin's manifest carries its own `mechanism`, and
 * server.mjs reads that first. This is what is left for a name a cached manifest does not carry.
 */
export const READ_ONLY = new Set([
  "get_project_info", "list_outline", "get_selection", "find_elements_by_criteria", "inspect",
  "list_textures", "get_texture", "get_undo_stack", "capture_screenshot", "set_camera_angle",
  "export_model",
]);

/**
 * The upstream tools a part author uses. Everything else is hidden under `authoring`.
 *
 * The kit's keep-list (`.mcptoolkit/loop.json`) plus the two a ONE-SERVER session needs that a kit
 * session does not: `project`, because without the shim there is no other way to see the binding or
 * close a stray tab, and `trigger_action` as the last escape hatch. If the loop file is unreadable
 * the slice falls back to the same names, hard-coded, so a session still starts.
 */
export const AUTHORING = [
  ...(LOOP.keep ?? [
    "get_project_info", "list_outline", "find_elements_by_criteria", "get_selection", "inspect",
    "place_cube", "modify_cube", "add_group", "element", "list_textures", "get_texture", "texture",
    "capture_screenshot", "set_camera_angle", "undo", "redo", "get_undo_stack", "risky_eval",
  ]),
  "project", "trigger_action",
];

/** The nine part tools. Under `kit` they are the whole of what this proxy adds: the skin loop has
 * its own eight (`armorpieces_skin*`), and serving both costs every part session the skin manifest
 * for nothing. */
export const PART_TOOLS = [
  "armorpieces_pieces", "armorpieces_open", "armorpieces_new", "armorpieces_check",
  "armorpieces_save", "armorpieces_part", "armorpieces_set_part", "armorpieces_paint",
  "armorpieces_close",
];

/** The eight skin tools, for the same reason in reverse. */
export const SKIN_TOOLS = [
  "armorpieces_skins", "armorpieces_open_skin", "armorpieces_skin_sheet", "armorpieces_skin_paint",
  "armorpieces_skin_material", "armorpieces_skin_check", "armorpieces_save_skin",
  "armorpieces_close_skin",
];

export const PROFILES = {
  authoring: new Set(AUTHORING),
  // Nothing from Blockbench: under `kit` those come from the toolkit shim's `project` profile.
  kit: new Set(),
  kit_skin: new Set(),
  full: null,
};

/** Which of this proxy's OWN tools each profile serves. `null` (or an absent entry) is all of them,
 * which is what `authoring` and `full` have always meant. */
export const OWN_PROFILES = {
  kit: new Set(PART_TOOLS),
  kit_skin: new Set(SKIN_TOOLS),
};

/** Sentences appended to upstream descriptions, so the model learns the workspace's rules where
 * it reads the tool, not in a document it may not have opened. The kit's notes verbatim
 * (`.mcptoolkit/loop.json`), plus the two names only `authoring` serves. */
export const NOTES = {
  ...(LOOP.notes ?? {}),
  project:
    " Not for an Armor Piece's own tab: armorpieces_open, armorpieces_save and armorpieces_close " +
    "own it, and they bind this session to the piece so another session's edit to it is refused. " +
    "`op:list` and `op:info` are the safe halves - they say who holds what.",
  trigger_action:
    " Not for the Armor Pieces menu: use armorpieces_open, armorpieces_save, armorpieces_new.",
};

/** Under `kit` the workspace's rules are served by the toolkit shim (`.mcptoolkit/loop.json`
 * `instructions`), which is the other half of the same session. Saying them twice is a per-turn
 * cost for nothing, so this says only what is left: which nine tools live here and what they are
 * for. */
export const KIT_INSTRUCTIONS = `The Armor Pieces piece tools, in front of the Blockbench plugin's own scripting surface. Blockbench
itself - modelling, painting, looking, history - comes from the mcptoolkit server in this same
session, and its instructions describe the workspace; these nine are what that server cannot do.

A PIECE is a part file plus a geometry plus its sheets, and only these tools move it: armorpieces_pieces
lists what exists, armorpieces_open / armorpieces_new open one and BIND this session to it - so
every Blockbench call after that goes to your piece by name, whatever tab a human clicks on, and
another live session's edit to it is refused (the reply also lists the envelopes of every other part
on the same bone, in both frames, so neighbour heights need no research), armorpieces_part / armorpieces_set_part are the datapack half (name, sockets, fittings,
effects, loot, the template recipe), armorpieces_paint paints whole faces by name on one sheet in one
call, armorpieces_check prints the piece's whole report, armorpieces_save writes it back into its
pack, and armorpieces_close closes the tab. Set the part data BEFORE painting masks: it is what
creates their sheets.

Sheets: \`part\` is the master (greyscale - the value is a position on the trim material's ramp),
\`part_static\` keeps real colour, \`part_<fitting>\` is one greyscale mask per masked fitting.
Every reply here ends with the piece's check, the same one the Blockbench tools carry; armorpieces_save
refuses while problems stand unless \`force\` says why each is acceptable.`;

/** The one thing every session should know before its first call. Served as the MCP server's
 * `instructions`, and repeated in tools/mcp/README.md. */
export const INSTRUCTIONS = `Blockbench, through the Armor Pieces bridge. Blockbench is running with the Armor Pieces plugin,
which opens a part as a tab on the vanilla player wearing real armor and saves it back into its
pack. Open the piece FIRST (armorpieces_open, or armorpieces_new for a new one): that binds this
session to it, and every call after it goes to that piece by name rather than to whichever tab
happens to be active. Blockbench still edits one project at a time - two sessions take turns, they
do not work in parallel - but a second session's edit to your piece is now refused with the name of
who holds it, rather than silently landing in it.

The workspace: the locked \`reference\` group is the player and armor - never edit it. Model inside
the \`part\` group only, every cube in a bone group (a group under part), in Blockbench coordinates
(feet at y=0, +Y up; a helmet part lives around y 24..32, the head bone's pivot). The game's
geometry (+Y down, x mirrored) is written by the plugin on save - never hand-edit the geometry JSON
of an open piece. Cubes cannot rotate; rotate the bone group. Mirrored sockets (horns, pauldrons,
vambraces, tassets, knees, spurs, greaves) model ONE side; the game mirrors it. Box UV is automatic:
the plugin lays out every added or resized cube on the sheet and moves its paint along, so do not
set UV offsets. Sheets: \`part\` is the master (greyscale = shading on the material ramp),
\`part_static\` keeps real colour, \`part_<fitting>\` is one greyscale mask per masked fitting.

The other thing this bridge opens is an ARMOR SKIN: the armor's own texture rather than a part hung
on it. That workspace is the same figure with the armor UNLOCKED and painted by one greyscale pair,
\`humanoid\` (helmet, chestplate, boots) and \`humanoid_leggings\` (belt, legs), both 64x32 on
vanilla's grid. Nothing is modelled - the geometry is vanilla's four shells - so the tools are
armorpieces_skins / _open_skin / _skin_sheet / _skin_paint / _skin_material / _skin_check /
_save_skin / _close_skin, and the sheets are read and written as rows of characters (\`.\`
transparent, \`0\`-\`9\` and \`a\`-\`f\` the sixteen greys). A texel's value is a position on the
material's ramp, so \`0\` is that material's deepest shadow and \`f\` its brightest highlight; a
master drawn inside a narrow band comes out flat on every material. A skin never paints a visor -
the face opening is what the brow parts are for.

After every editing call the reply ends with an [armorpieces] block: the same checks every shipped
part passes (tools/check_part.py), or tools/check_skin.py when a skin is open. A line marked "!" is a PROBLEM that needs a decision before
saving - a face lying on the part's own armor shell (move it: it will z-fight), a plane shared with
another part, a face with no paint behind it (paint it, or leave it cut on purpose and say so),
paint outside every face, colour on a greyscale sheet. "-" lines are notes (buried faces, hull
overlaps, near misses). armorpieces_check gives the whole report; armorpieces_save refuses while
problems stand unless force is passed. The datapack half (name, sockets, fittings, effects, loot)
is armorpieces_part / armorpieces_set_part; the template recipe is on the plugin panel.`;
