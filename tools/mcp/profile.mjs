// What an agent authoring a part sees of Blockbench, and what it is told.
//
// The Blockbench MCP Server plugin registers ninety-odd tools: armatures, meshes, PBR materials,
// Hytale, animation. A part is cubes in bone groups on a rig the Armor Pieces plugin builds, painted
// on three kinds of sheet, and none of the rest applies to it. The `authoring` profile is the slice
// that does, plus the piece-level tools the proxy adds. `full` is everything, for debugging the
// bridge itself. Set ARMORPIECES_BB_PROFILE to choose.

/** Upstream tools that never edit the project, so no check runs after them. */
export const READ_ONLY = new Set([
  "get_project_info", "list_outline", "get_selection", "find_elements_by_criteria",
  "list_textures", "get_texture", "get_undo_stack", "capture_screenshot", "capture_app_screenshot",
  "set_camera_angle", "list_export_formats", "export_model", "list_materials", "get_material_info",
  "list_material_instances", "get_face_material_instances", "filter_by_material", "list_armatures",
  "get_armature", "list_armature_bones", "get_armature_bone", "get_vertex_weights",
  "color_picker_tool", "select_all_of_type", "select_mesh_elements", "select_armature_bones",
  "save_checkpoint", "paint_settings", "activate_texture", "texture_selection",
  "hytale_get_cube_properties", "hytale_get_cube_stretch", "hytale_get_format_info",
  "hytale_list_attachment_pieces", "hytale_list_attachments", "hytale_validate_model",
]);

/** The upstream tools a part author uses. Everything else is hidden under `authoring`. */
export const AUTHORING = [
  // orientation
  "get_project_info", "list_outline", "find_elements_by_criteria", "get_selection",
  // modelling: cubes in bone groups
  "place_cube", "modify_cube", "duplicate_element", "remove_element", "rename_element", "add_group",
  // painting: the master, the static layer, the fitting masks
  "list_textures", "get_texture", "activate_texture", "paint_with_brush", "paint_fill_tool",
  "draw_shape_tool", "gradient_tool", "eraser_tool", "color_picker_tool", "texture_selection",
  "paint_settings",
  // looking
  "capture_screenshot", "set_camera_angle",
  // history
  "undo", "redo", "get_undo_stack", "save_checkpoint",
  // escape hatches
  "trigger_action", "risky_eval",
];

export const PROFILES = {
  authoring: new Set(AUTHORING),
  full: null,
};

/** Sentences appended to upstream descriptions, so the model learns the workspace's rules where
 * it reads the tool, not in a document it may not have opened. */
export const NOTES = {
  place_cube:
    " In an Armor Piece: put the cube in a bone group under `part` (`group`), in Blockbench space " +
    "(feet at y=0, +Y up; the head is y 24..32). Leave `faces` and `texture` alone - the plugin " +
    "gives every part cube box UV in free space on the sheet and grows the sheet when full. Cubes " +
    "do not rotate in this format; rotate the bone group instead.",
  modify_cube:
    " In an Armor Piece leave `uv_offset`, `autouv` and `rotation` alone: box UV is laid out by " +
    "the plugin on every resize (paint moves with the faces), and a rotated cube is a rotated bone " +
    "group. `inflate` is fine.",
  add_group:
    " In an Armor Piece a group under `part` is a bone: its `origin` is the pivot the game rotates " +
    "about and `rotation` is the only rotation this format has. `parent` names the bone above it, " +
    "or `part`. Name it right the first time: rename_element cannot rename a group.",
  rename_element:
    " Cubes only: on a group it fails inside Blockbench's undo snapshot (`getUndoCopy is not a " +
    "function`). To rename a bone, add a new group with the name, move or re-place its cubes, and " +
    "remove_element the old one.",
  paint_with_brush:
    " Sheets of an Armor Piece: `part` (the master; greyscale, its value is the position on the " +
    "material's ramp, anything coloured is folded to grey), `part_static` (real colour that stays " +
    "as painted) and `part_<fitting>` (a greyscale mask per masked fitting). Name one as " +
    "`texture_id`. Coordinates are sheet pixels; the reply's check names any face still unpainted. " +
    "For whole faces use armorpieces_paint instead.",
  paint_fill_tool:
    " On an Armor Piece sheet keep `fill_mode` at `color_connected` and start inside the face " +
    "rectangle you mean (armorpieces_check lists every cube's face rectangles): `element` and " +
    "`selection` follow the editor's selection and can flood the whole sheet, which the check then " +
    "reports as paint outside every face. `part` is the master sheet, see paint_with_brush.",
  draw_shape_tool:
    " For an Armor Piece prefer armorpieces_paint: it paints whole faces by name, shaded, in one " +
    "call. This tool is for a shape that is not a face; coordinates are inclusive sheet pixels. " +
    "Sheets are `part`, `part_static`, `part_<fitting>` - see paint_with_brush.",
  gradient_tool: " Sheets of an Armor Piece are `part`, `part_static`, `part_<fitting>` - see paint_with_brush.",
  eraser_tool: " Sheets of an Armor Piece are `part`, `part_static`, `part_<fitting>` - see paint_with_brush.",
  get_texture: " An Armor Piece's sheets are `part`, `part_static` and `part_<fitting>`; `preview` is the material preview, read-only.",
  undo:
    " In an Armor Piece one undo step is one edit including the UV layout and paint moves it " +
    "caused. Undoing a place_cube can leave the cube behind as a ghost outside every group; the " +
    "check reports it, remove_element by name clears it.",
  risky_eval:
    " Every eval is one undo entry unless it changed nothing. `armorpieces_api` is the Armor Pieces " +
    "plugin's scripting surface, but prefer the armorpieces_* tools: they know the traps. Never " +
    "close or switch projects inside an eval (use armorpieces_open / armorpieces_close); the code " +
    "may not contain `//`, block comments or the word console.",
  trigger_action:
    " Not for the Armor Pieces menu: use armorpieces_open, armorpieces_save, armorpieces_new.",
};

/** The one thing every session should know before its first call. Served as the MCP server's
 * `instructions`, and repeated in tools/mcp/README.md. */
export const INSTRUCTIONS = `Blockbench, through the Armor Pieces bridge. Blockbench is running with the Armor Pieces plugin,
which opens a part as a tab on the vanilla player wearing real armor and saves it back into its
pack. All Blockbench tools act on the ACTIVE tab, so open the piece first (armorpieces_open, or
armorpieces_new for a new one), and do not run two agents against one Blockbench.

The workspace: the locked \`reference\` group is the player and armor - never edit it. Model inside
the \`part\` group only, every cube in a bone group (a group under part), in Blockbench coordinates
(feet at y=0, +Y up; a helmet part lives around y 24..32, the head bone's pivot). The game's
geometry (+Y down, x mirrored) is written by the plugin on save - never hand-edit the geometry JSON
of an open piece. Cubes cannot rotate; rotate the bone group. Mirrored sockets (horns, pauldrons,
vambraces, tassets, knees, spurs, greaves) model ONE side; the game mirrors it. Box UV is automatic:
the plugin lays out every added or resized cube on the sheet and moves its paint along, so do not
set UV offsets. Sheets: \`part\` is the master (greyscale = shading on the material ramp),
\`part_static\` keeps real colour, \`part_<fitting>\` is one greyscale mask per masked fitting.

After every editing call the reply ends with an [armorpieces] block: the same checks every shipped
part passes (tools/check_part.py). A line marked "!" is a PROBLEM that needs a decision before
saving - a face lying on the part's own armor shell (move it: it will z-fight), a plane shared with
another part, a face with no paint behind it (paint it, or leave it cut on purpose and say so),
paint outside every face, colour on a greyscale sheet. "-" lines are notes (buried faces, hull
overlaps, near misses). armorpieces_check gives the whole report; armorpieces_save refuses while
problems stand unless force is passed. The datapack half (name, sockets, fittings, effects, loot)
is armorpieces_part / armorpieces_set_part; the template recipe is on the plugin panel.`;
