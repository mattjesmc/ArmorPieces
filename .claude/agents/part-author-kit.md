---
name: part-author-kit
description: part-author, served through the mcp-toolkit loop kit instead of tools/mcp/server.mjs - the Blockbench tools come from mcptoolkit's `project` profile (.mcptoolkit/loop.json - the same keep-list, notes, instructions and check-on-every-reply), and only the nine armorpieces_* tools still come from the proxy. LOOP_KIT_DESIGN.md section 9 step 7, the kit's falsifier. Authors ONE part end to end; one fresh session per part, sequentially.
tools: Read, Grep, Glob, Bash, Edit, Write, mcp__blockbench__armorpieces_pieces, mcp__blockbench__armorpieces_open, mcp__blockbench__armorpieces_new, mcp__blockbench__armorpieces_check, mcp__blockbench__armorpieces_paint, mcp__blockbench__armorpieces_save, mcp__blockbench__armorpieces_part, mcp__blockbench__armorpieces_set_part, mcp__blockbench__armorpieces_close, mcp__mcptoolkit__get_project_info, mcp__mcptoolkit__list_outline, mcp__mcptoolkit__inspect, mcp__mcptoolkit__place_cube, mcp__mcptoolkit__modify_cube, mcp__mcptoolkit__add_group, mcp__mcptoolkit__element, mcp__mcptoolkit__list_textures, mcp__mcptoolkit__get_texture, mcp__mcptoolkit__texture, mcp__mcptoolkit__capture_screenshot, mcp__mcptoolkit__undo, mcp__mcptoolkit__get_undo_stack, mcp__mcptoolkit__risky_eval
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
the cubes' face rectangles, `armorpieces_check` lists them all, and `inspect` with `faces` prints
the CURRENT ones - which is how stray paint from a layout you have since changed is found. For
anything that is not a face, `texture op:rects` takes a list of rectangles in inclusive pixels, and
a rect with `c: null` clears. `get_texture` comes back too small to read a 64x32 sheet; use
`texture op:read`, trust the check, or open the saved PNG with Pillow. `capture_screenshot` takes
`fit` and a `views` list that composes several angles into one contact sheet; a material preview is
read-only.

What the check does not do: it never compares two parts of the same socket, since they are never
worn together. Where the nasal sits relative to the circlet is your choice, made from the numbers:
the reply to `armorpieces_open` and `armorpieces_new` lists the envelopes of every other part on
the bone, same-socket ones first, in both the game's frame (+Y down) and Blockbench's, so you do
not open other pieces or read their geometry files to find a hairline height.

## The check on every reply

After every editing call the reply ends with the piece's check (the same `tools/check_part.py`
report, appended by the toolkit's loop file). Lines marked `!` are problems that need a decision:
a face lying on the part's own armor shell (move it - it z-fights), a plane shared with another
part on the same bone, faces with no paint behind them (paint them, or cut them on purpose and
say so in your report), paint outside every face, colour on a greyscale sheet, static or mask
pixels outside the master's silhouette. `-` lines are notes. `armorpieces_check` prints the whole
report. `armorpieces_save` refuses while problems stand unless you pass `force` and say why each
one is acceptable. Pictures are re-sent on every later turn: take one only where it can still
change what you draw. Six is the budget for a part, and every reply that carries one prices it.

## Order of work

Everything you need is in this profile, the brief, and the bridge's replies. Do not read
`docs/authoring.md` unless a reply sends you there. **The one other file to read is
`docs/plans/briefs/LESSONS.md`** - the technique the earlier sessions worked out, distilled and
current. Do NOT skim other briefs for technique: 52 of the 77 were written against a bridge that
no longer exists and teach tools that are gone, and reading one was measured at 48% of everything
a session carries (`docs/measurements/CONCURRENCY_AB.md`, round 2). Open another brief only when
your own names a specific neighbouring piece and you need that piece's numbers.

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
6. `armorpieces_close`. **Leave the workspace as you found it** - a tab left open is the active
   tab for whoever claims this window next, and it is what makes `tools/mcp/check_kit.mjs` go
   red for reasons that have nothing to do with the change being tested.
7. Report: what you built, every `!` you accepted and why, and what the next part should know.
   If something you learned generalises beyond this piece, add it to
   `docs/plans/briefs/LESSONS.md` rather than only to your brief.

Do not run the game, do not commit, do not touch other parts' files, and do not use `risky_eval`
for anything an `armorpieces_*` tool does.
