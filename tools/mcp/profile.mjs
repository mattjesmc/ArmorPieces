// What an agent authoring a part or a skin sees of this proxy, and what it is told.
//
// Blockbench's own bridge is `mcptoolkit_bridge.js` (mcp-toolkit 0.133.0+), which registers 26
// tools, and the toolkit's shim serves them. This proxy therefore serves NO upstream tool: only the
// pieces of the workflow that are genuinely ours - the nine PART tools under `kit`, the eight SKIN
// tools under `kit_skin` - so the two servers never both offer place_cube and the manifest is paid
// for once. That split is what `.claude/agents/part-author-kit.md` and `skin-author.md` are written
// against. `full` serves everything and is for a SCRIPT driving the bridge (`shoot_skins.mjs`), not
// for a session. Set ARMORPIECES_BB_PROFILE to choose; the default is `kit`.
//
// ONE SOURCE FOR THE SLICE (2026-09-07). The notes below are READ FROM `.mcptoolkit/loop.json`
// rather than written here twice: that file is the shim's keep-list and the one that is kept true.
// A second hand-kept copy here is how the old `authoring` profile came to be annotating
// `paint_with_brush` and `save_checkpoint` months after the plugin that had them was replaced -
// which is also why `authoring` itself is gone (2026-09-08; see PROFILES below). When the loop file
// cannot be read this proxy still starts and says so on stderr; it just serves its own tools
// without the traps appended.

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

/**
 * TWO PROFILES AND AN ESCAPE HATCH (2026-09-08). `authoring` - the pre-kit slice, one server
 * carrying twenty of Blockbench's tools as well as its own - is gone. It had no caller left: both
 * agents run under `kit`/`kit_skin`, where Blockbench comes from the toolkit shim, and the only
 * thing still asking for it was `shoot_skins.mjs`, which asked through an environment variable
 * nothing reads (`MCP_PROFILE`) and got it from the DEFAULT instead. Keeping a second, hand-kept
 * slice of the plugin's surface is exactly how this file came to be annotating `paint_with_brush`
 * months after the plugin that had it was replaced.
 *
 * `full` stays, and is now the honest name for what that was: serve everything, for a SCRIPT
 * driving the bridge rather than a session reasoning about it. `shoot_skins.mjs` names it.
 */
export const PROFILES = {
  // Nothing from Blockbench: under `kit` those come from the toolkit shim's `project` profile.
  kit: new Set(),
  kit_skin: new Set(),
  full: null,
};

/** Which of this proxy's OWN tools each profile serves. `null` (or an absent entry) is all of them,
 * which is what `full` means. */
export const OWN_PROFILES = {
  kit: new Set(PART_TOOLS),
  kit_skin: new Set(SKIN_TOOLS),
};

/** Sentences appended to upstream descriptions, so the model learns the workspace's rules where
 * it reads the tool, not in a document it may not have opened. The kit's notes verbatim
 * (`.mcptoolkit/loop.json`), plus the two that only `full` serves. */
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

/** The skin loop's half, and the same argument as KIT_INSTRUCTIONS: under `kit_skin` the workspace
 * - the figure, the armor shells, what the check means - is described by the toolkit shim's own
 * instructions, so this says only what these eight tools are for and the one thing about a skin
 * that a part session never has to know, which is what a texel's VALUE means.
 *
 * The long pre-kit paragraph that used to live here (both workspaces at once, for the one-server
 * `authoring` profile) went with that profile on 2026-09-08. `full` gets KIT_INSTRUCTIONS: it is a
 * script profile, and a script does not read them. */
export const KIT_SKIN_INSTRUCTIONS = `The Armor Pieces SKIN tools, in front of the Blockbench plugin's own surface. Blockbench itself -
looking, textures, history - comes from the mcptoolkit server in this same session; these eight are
what that server cannot do.

A SKIN is the armor's OWN texture, not a part hung on a socket and not a trim painted over it: the
plate itself. Nothing is modelled - the geometry is vanilla's four armor shells on the vanilla
player - so the whole job is what is painted on ONE GREYSCALE PAIR, \`humanoid\` (helmet,
chestplate, boots) and \`humanoid_leggings\` (belt, legs), both 64x32 on vanilla's grid.

armorpieces_skins lists what exists; armorpieces_open_skin opens one and BINDS this session to it,
so every call after that goes to your skin whatever tab a human clicks on; armorpieces_skin_sheet
reads a sheet back; armorpieces_skin_paint writes one, addressed by net and face
(\`region: "chest", face: "front"\`) so a stamp that would run off the face is refused rather than
landing somewhere wrong; armorpieces_skin_material bakes the figure to a material in the viewport,
live; armorpieces_skin_check prints the whole report; armorpieces_save_skin writes the pair back
under tools/skin_masters/<name>/; armorpieces_close_skin closes the tab.

Sheets are read and written as ROWS OF CHARACTERS - \`.\` transparent, \`0\`-\`9\` and \`a\`-\`f\`
the sixteen greys, a space for "leave this texel alone". A texel's value is a position on the
MATERIAL'S RAMP, so \`0\` is that material's deepest shadow and \`f\` its brightest highlight, and a
master drawn inside a narrow band comes out flat on every material - judge it on three materials,
not one. A skin never paints a visor: the face opening is what the brow parts are for.

Every reply here ends with the skin's check (tools/check_skin.py); armorpieces_save_skin refuses
while problems stand unless \`force\` says why each is acceptable.`;
