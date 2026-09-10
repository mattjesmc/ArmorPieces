# Brief: Horsetail

The fourth part authored through the bridge (`tools/mcp`), by one `part-author` session on
Fable, with the tooling exactly as the Antennae session had it - the control for that run. From
the `crest` row of `docs/plans/part-variety.md`:

> **Horsetail** - A socket tube at the crown with a long tail falling backward down the neck.
> Reads as motion where the brush reads as bulk. Theme: Beast. Fitting: `inlay` (the hair).

**Part.** `armorpieces:horsetail`, socket `crest` only, in the mod's own pack. Display name
"Horsetail". Fittings: `armorpieces:inlay`, one mask, covering the hair only - the tube stays the
helmet's metal, the tail takes the dye. No effects, no loot.

**Shape.** `crest` is not a mirrored socket, so model the whole thing, centred on x = 0. A short
tube bone on the crown (a 2x2 cube, a little taller than wide, its base half a texel inside the
helmet the way the spire's plate is), and behind it a chain of tail bones falling backward and
down: three or four segments, each its own bone rotated a little further than the last so the
tail arcs over the back of the head, each cube one or two texels wide and thinner than the one
before, the last reaching the nape but not below the shoulders. Keep the whole thing inside the
brush crest's width and lower than the feathering; the reply to `armorpieces_new` gives every
crest part's envelope to place against.

**Sheets.** Master: the tube mid-grey with a lighter rim, the hair darker with lighter streaks
toward the tip. Inlay mask: the tail's faces only. No static layer.

**Recipe.** Centre item `minecraft:hay_block` (unused by any template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py horsetail`
and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons paragraph below
filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-03 in 20 bridge calls: 1 `armorpieces_new`, 5 `add_group`, 5 `place_cube`,
2 `remove_element` (starter cube, then its bone), 1 `armorpieces_set_part`, 2 `armorpieces_paint`,
1 `armorpieces_check`, 2 `set_camera_angle`, 1 `armorpieces_save`. No `risky_eval`, no
`modify_cube`, no hand-edited part file, and the save went through first time without `force`.

**What I built.** A `tube` bone at the crown, cube 2x3x2 at Blockbench y 32.5..35.5 (base half a
texel inside the shell, like the spire's plate), and under it a chain of four bones -
`tail_root` (+50 X), `tail_mid` (+60), `tail_lower` (+45), `tail_tip` (+30), cumulative
50/110/155/185 degrees - each with one cube modelled straight up from its pivot, 1.5 / 1.25 /
1.0 / 0.8 wide, 3 / 3.5 / 4 / 6 long, each overlapping its parent's end by 0.3-0.5. The tip hangs
at Blockbench y 26.1, z 6.8 - the nape, two units above the shoulders - and the whole thing stays
in x +-1, inside brush_crest's +-1.5, topping out at y 37.6, well under the feathering's 44.
Master 55..230: tube `[200,130]` with a 215 top; hair `[95,60]` -> `[200,125]` segment by segment,
lighter toward the tip, plus 16 single-texel streaks. Inlay mask: the 24 hair faces, 90..255, the
same gradient. Recipe hay block in paper.

**What the bridge told me.** The `armorpieces_new` reply had everything a crest part needs, and
the three problems the earlier sessions hit are gone: `armorpieces_set_part` created `part_inlay`
on the spot (`sheets_created: [part_inlay]`) and the recipe was written on save; the master went
straight to `tools/decoration_masters/` and the first save ran the sync ("installed 2 file(s)");
and `place_cube` gave every cube its own free UV rectangle (uv 0,0 / 8,0 / 12,0 / 20,0 / 28,0),
no resize dance. Rotation sign: positive X on a bone tips an upright segment toward +Z, the back
of the head. The arithmetic (pivot + length x (cos, sin) of the cumulative angle) matched the
check's bone positions to a hundredth - `tail_tip at (0, -8.11, 7.28)` is game space for my
predicted Blockbench (y 32.11, z 7.28). Do the sums before placing; nothing needed nudging.

**Painting.** Two `armorpieces_paint` calls, one per sheet, covered all 30 master faces and all 24
mask faces - zero unpainted afterwards, and the mask stayed inside the master's silhouette because
it addresses the same cubes. The `[top, bottom]` pair runs from the face's UV top, which for a
segment modelled upright is the far end of the segment, so `[light, dark]` is "lighter toward the
tip" without any thought about the rotation. The `pixels` list is the right tool for hair
streaks: a 1-2 texel wide face has no room for a shape, and a streak is two texels in one column.
What the painter cannot do is anything defined relative to a neighbouring face - the tube's rim
is a whole lighter top face plus a bright top row, not a painted ring.

**Things worth knowing.**
- The check's `past helmet z` is the running number for a tail: -3.75 (starter) -> +0.80 (mid)
  -> +2.73 (lower); the tip added nothing in z because it curls back in at 185 degrees.
- The one note is `tail_tip clears circlet:brow's band by 0.36 in z`: the circlet's band reaches
  z 6 at the back of the head, the tip hangs at z 6.36..7.16. It is a gap, and the circlet rides
  the same head bone, so nothing ever moves relative to it - accepted, no force needed. A tip at
  180 instead of 185 would clear by 0.9 but hang straight instead of tucking in.
- The 60-degree joint shows a visible kink at the top of the arc in the screenshot; five
  segments of 35-40 degrees would arc more smoothly for one more bone and a sheet row. Fine at
  three metres.
- A 0.8-wide cube unwraps to 1 texel; 1.25 and 1.5 both unwrap to 2, so the mid and root
  segments differ only in the model, not on the sheet. Widths worth stepping on the sheet are
  2 -> 1 -> under 1; anything between paints alike.
- **A block as the centre item has no flat icon.** `hay_block` is rendered from a model in game,
  so `python -m modpage build` warned `no texture for minecraft:hay_block` online as well as
  offline (the mirror has `hay_block_side`/`_top`, never `hay_block.png`). The repo's route for
  that is `tools/gen_recipe_icons.py`: a 16x16 pixel-art stand-in, palette sampled from the real
  block textures, written to `docs/assets/icons/` and wired through `recipes.icons` in
  `modpage.yml`. Check the centre item is a flat item (or budget an icon) when picking it - the
  brief said hay block, so the icon was the cost. `gen_recipe_icons.py` was already modified in
  the working copy by another session; the hay block entry is purely additive.
- Other tabs were open in Blockbench (nasal with unsaved edits, spire) and stayed untouched;
  `armorpieces_new` made the new piece the active tab.
