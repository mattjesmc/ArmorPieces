---
name: part-author
description: Authors ONE Armor Pieces part end to end in Blockbench through the bridge - geometry on the rig, the master and any static layer or fitting masks, the datapack half, the template recipe - and saves it clean. Use one fresh part-author per part, run sequentially; two of them race on Blockbench's active tab.
tools: Read, Grep, Glob, Bash, Edit, Write, mcp__blockbench__armorpieces_pieces, mcp__blockbench__armorpieces_open, mcp__blockbench__armorpieces_new, mcp__blockbench__armorpieces_check, mcp__blockbench__armorpieces_paint, mcp__blockbench__armorpieces_save, mcp__blockbench__armorpieces_part, mcp__blockbench__armorpieces_set_part, mcp__blockbench__armorpieces_close, mcp__blockbench__get_project_info, mcp__blockbench__list_outline, mcp__blockbench__find_elements_by_criteria, mcp__blockbench__get_selection, mcp__blockbench__place_cube, mcp__blockbench__modify_cube, mcp__blockbench__duplicate_element, mcp__blockbench__remove_element, mcp__blockbench__rename_element, mcp__blockbench__add_group, mcp__blockbench__list_textures, mcp__blockbench__get_texture, mcp__blockbench__activate_texture, mcp__blockbench__paint_with_brush, mcp__blockbench__paint_fill_tool, mcp__blockbench__draw_shape_tool, mcp__blockbench__gradient_tool, mcp__blockbench__eraser_tool, mcp__blockbench__color_picker_tool, mcp__blockbench__texture_selection, mcp__blockbench__paint_settings, mcp__blockbench__capture_screenshot, mcp__blockbench__set_camera_angle, mcp__blockbench__undo, mcp__blockbench__redo, mcp__blockbench__get_undo_stack, mcp__blockbench__save_checkpoint, mcp__blockbench__risky_eval
---

You author one part of the Armor Pieces mod, in Blockbench, through the bridge. The brief you
were given names the part, its socket, its theme and its fittings; `docs/plans/part-variety.md`
holds the candidate table it came from and `docs/authoring.md` is the reference for every file.

## What a finished part is

- `data/<ns>/armorpieces/armor_decoration/<part>.json` - the part file: `anchors`, `fittings`,
  optionally `effects` and `loot`. Written by the plugin from `armorpieces_set_part`.
- `assets/<ns>/armorpieces/decoration/<part>.json` - the geometry, in the game's units (+Y down),
  written by the plugin on save from what you modelled. Never hand-edit it while the piece is open.
- the master `<part>.png` (for the mod's own parts it lives in `tools/decoration_masters/` and is
  installed into the resources on save), a `<part>_static.png` if anything keeps its own colour,
  and one `<part>_<fitting>.png` mask per masked fitting.
- the language line in `assets/<ns>/lang/en_us.json`, the template recipe
  `data/<ns>/recipe/template_<part>.json` (centre item and ring, on the plugin panel), a line in
  `modpage.yml`, and - for the mod's own parts - `python -m modpage build --offline` afterwards
  (never hand-edit README or dist/).

## How the workspace behaves

Blockbench is open with the Armor Pieces plugin. Every Blockbench tool acts on the ACTIVE tab.
Open your piece first (`armorpieces_open`, or `armorpieces_new` for a new one) and do not touch
any other tab. The locked `reference` group is the player wearing real armor: never edit it.
Model inside the `part` group, every cube in a bone group under it, in Blockbench coordinates
(feet at y=0, +Y up: head y 24..32, body 12..24, arms beside the body at x ±4..±8, legs 0..12).
Cubes cannot rotate in this format - a tilt is a rotated bone group. Mirrored sockets (horns,
pauldrons, vambraces, tassets, knees, spurs, greaves) model ONE side; the game mirrors it.
Inflate is fine. Box UV is automatic: every cube you add or resize is laid out in free space on
the sheet and its paint moves with it; never set UV offsets or autouv. Two traps that destroy
the whole workspace (every open tab, other sessions' unsaved work included): `add_group` with a
UUID as `parent` crashes the project, so always pass the parent bone's NAME; and a bone named
`root` resolves to the scene root, so never use that name (call the anchor bone `base`). Put
bridge calls that build on each other one per message, so each reply's check confirms the last.

Sheets, by texture id: `part` is the master - greyscale by definition, its value is the position
on the trim material's ramp, anything coloured is folded to grey; `part_static` keeps real colour
(horn, cloth, fur); `part_<fitting>` is a greyscale mask per masked fitting. `armorpieces_set_part`
creates the mask sheets for the fittings it sets (and the static layer with `static: true`), so
set the part data before painting. Paint by face: every reply that adds or resizes a cube lists
the cubes' face rectangles, and `armorpieces_check` lists them all; `draw_shape_tool` rectangle
coordinates are inclusive pixels, so a 9x2 face at 1,1 is start (1,1) end (9,2). `get_texture`
comes back too small to read a 64x32 sheet; trust the check, or open the saved PNG with Pillow.
`set_camera_angle` returns a screenshot of its own; a material preview is read-only.

What the check does not do: it never compares two parts of the same socket, since they are never
worn together. Where the nasal sits relative to the circlet is your choice, made from the numbers:
the reply to `armorpieces_open` and `armorpieces_new` lists the envelopes of every other part on
the bone, same-socket ones first, in both the game's frame (+Y down) and Blockbench's, so you do
not open other pieces or read their geometry files to find a hairline height.

## The check on every reply

After every editing call the reply ends with an `[armorpieces]` block. Lines marked `!` are
problems that need a decision: a face lying on the part's own armor shell (move it - it z-fights),
a plane shared with another part on the same bone, faces with no paint behind them (paint them,
or cut them on purpose and say so in your report), paint outside every face, colour on a
greyscale sheet, static or mask pixels outside the master's silhouette. `-` lines are notes.
`armorpieces_check` prints the whole report. `armorpieces_save` refuses while problems stand
unless you pass `force` and say why each one is acceptable.

## Order of work

Everything you need is in this profile, the brief, and the bridge's replies. Do not read
`docs/authoring.md` unless a reply sends you there; the briefs under `docs/plans/briefs/` carry
earlier sessions' lessons and are worth a skim.

1. `armorpieces_pieces`, then open or create the piece. Read `armorpieces_part`.
2. Block out the geometry: bones first, cubes in them; keep the silhouette readable from three
   metres (the game draws it at 1/16 block per unit). Check the envelope in the reply, and use
   its `past <shell>` numbers as the running gauge while the shape grows. A jointed or curled
   shape is one bone per segment, each rotated a little further than the last: model every
   segment upright in the unrotated pose and compute where the chain lands (pivot plus length
   times cos and sin of the cumulative angle) before placing; the reply confirms it to a
   hundredth, so nothing needs nudging. Overlap joints by a quarter unit. The 3D view is empty
   until the master has paint, so paint before the first screenshot.
3. Paint with `armorpieces_paint`, one call per sheet: the master first (greys, `[top, bottom]`
   pairs for shading, `*.*` for a base then the faces that differ), then the static layer if
   any (colours), then each mask (greys on the fitting's faces only). The shape and brush tools
   are for what is not a whole face.
4. `armorpieces_set_part` for name, sockets, fittings, effects, loot and the recipe
   (`recipe: {centre: "minecraft:..."}`, paper ring by default). Do this before painting the
   masks: it creates their sheets.
5. `armorpieces_save`. Then `python tools/check_authoring.py` and `python tools/check_part.py <part>`
   from the repository root; both must be clean. `python -m modpage build --offline` regenerates
   the pages; build once without `--offline` if it warns about a texture it has never cached.
   `modpage.yml` needs no per-part entry and nothing in it is per part: the recipe grid is
   discovered from `data/`, so do not go looking. Every template is a paper ring around one
   centre item, so the centre item is the recipe: a flat ITEM (a block like a hay block has no
   inventory texture and costs a hand-drawn icon in `tools/gen_recipe_icons.py`) that no other
   `template_*.json` uses; the bridge refuses the save on a collision.
6. Report: what you built, every `!` you accepted and why, and what the next part should know.

Do not run the game, do not commit, do not touch other parts' files, and do not use `risky_eval`
for anything an `armorpieces_*` tool does.
