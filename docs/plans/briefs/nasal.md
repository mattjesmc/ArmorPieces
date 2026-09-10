# Brief: Nasal

The first part authored through the bridge (`tools/mcp`), by one `part-author` session. From the
`brow` row of `docs/plans/part-variety.md`:

> **Nasal** - A T-bar down the bridge of the nose off a plain brow band. Cheap, iconic, very
> Norman. Theme: Knightly. Fitting: `guard`.

**Part.** `armorpieces:nasal`, socket `brow` only, in the mod's own pack (`src/main/resources`,
namespace `armorpieces`), so the master lives in `tools/decoration_masters/nasal.png` and is
installed on save. Display name "Nasal". Fittings: `armorpieces:guard`, one mask, covering the bar
(the band stays the helmet's material, the bar takes the guard's). No effects, no loot.

**Shape.** Two bones under `part`: a flat band across the brow, one texel thick, sitting on the
helmet's front face at the hairline height the circlet and coronet use (open them with
`armorpieces_open` and read the check's envelope for the height and depth they chose - the nasal
must not lie on the same plane as the circlet's band, which the check will say); and a bar hanging
from its centre down the bridge of the nose, one texel wide, stopping above the mouth. Nothing
behind the head: the band is a front plate, not a ring. Model the whole thing - `brow` is not a
mirrored socket.

**Sheets.** Master: light band, darker bar, a highlight texel along the top edge of the band. Guard
mask: the bar only. No static layer.

**Recipe.** Centre item `minecraft:iron_nugget`, paper ring (the panel's default).

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py nasal`
and `python tools/check_authoring.py` clean; a `modpage.yml` entry in the brow group; the
lessons paragraph below filled in.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-03 through the bridge. Band 9×2×1 at Blockbench x −4.5..4.5, y 28..30,
z −5.5..−4.5 (front face 0.5 past the helmet shell, back face buried in it); bar 1×2×1 at
x ±0.5, y 26..28, z −5.75..−4.75, a child bone of the band. Master 70..240 grey, guard mask the
bar's six faces. Saved without `force`; both checks clean; recipe iron nugget in paper.

**Reading the neighbours.** The check reports in the game's units: the `brow` anchor is at
(0, −4, −4) on the head, and Blockbench y = 24 − game y, z the same. So the circlet's band
(`[-6,-2,-2] 12×2×2` in its geometry) is Blockbench y 28..30 with its front at z −6 and its inner
face on the head; the coronet's is y 29..30 with its front at z −5.65. Both put their top edge at
y 30 — that is the hairline height. Reading the geometry JSON on disk is cheaper than opening the
piece, and gives the same numbers once the anchor offset is added.

**The check never compares two parts of the same socket.** "Shares head with" lists antlers,
brush_crest, feathering, head_fins, helm_wings and horns — never the circlet or coronet, because
two brow parts are never worn together. So the brief's "the check will say" if the nasal shares
the circlet's plane is wrong: it says nothing, and the distinct plane (z −5.5 here) is a choice
you make by hand.

**The starter piece opens with a problem.** `armorpieces_new`'s one cube has its back face on the
helmet shell (`COPLANAR ... z face at -5`). A front plate must have its back face *inside* the
shell (z > −5 in Blockbench) or clear of it; on the shell it z-fights. Removing the starter cube
and bone leaves an empty `part`, and the check then dies with `min() iterable argument is empty`
on every reply until the first cube is placed - harmless, just noise.

**The UV layout missed the second cube.** `place_cube` for the bar, in a different bone, gave it
uv 0,0 on top of the band's faces. The layout runs again on resize, so resizing the cube by half
a unit and back (two `modify_cube` calls) moved it to free space at 20,0. Always read the `sheet
layout` block of `armorpieces_check` before painting; the brief reply does not show it.

**Painting.** `draw_shape_tool` `rectangle` takes inclusive pixel coordinates, so a 9×2 face at
1,1 is start (1,1) end (9,2). One rectangle per face from the layout listing, all in one batch;
each reply's check counts the unpainted faces down. `get_texture` on a 64×32 sheet comes back too
small to read; inspect the saved PNG with PIL, or trust the check.

**`armorpieces_set_part` does not create the mask sheet** - only the panel's Fitting selector
does. The route that works without the panel: save, write
`tools/decoration_masters/<part>_<fitting>.png` yourself (64×32 RGBA, transparent = not the
fitting's, opaque grey = the fitting's shading, only inside faces the master paints), then
`armorpieces_open` with `reload: true` - the sheet appears as `part_<fitting>` and the next save
installs it. `list_textures` confirms it is there.

**`armorpieces_new` does not put the master in `tools/decoration_masters`.** It writes the blank
sheet under `src/main/resources/.../textures/entity/decoration/`, and the plugin only treats
`tools/decoration_masters/<part>.png` as the master if that file already exists (`masterFor` in
the plugin). So the first save wrote the resources copy and skipped the sync. Fix: copy the saved
PNG to `tools/decoration_masters/<part>.png`, reopen with `reload`, save again - that save runs
`sync_decoration_masters.py` ("installed 2 file(s)"). Do this before writing the mask, so both
sheets are found in the same place.

**No bridge tool sets the recipe.** The first save said `no recipe (no centre item)`. Copy a
sibling's `data/armorpieces/recipe/template_<part>.json`, change the centre item and the
`armorpieces:decoration` id, reopen; `armorpieces_part` then shows `recipe.focus` and the next
save rewrites the file itself.

**modpage.** `modpage.yml` has no per-socket part list - the recipes section is discovered from
`data/`, so there was nothing to add; the "twenty parts" prose in it is already stale and was
left alone. Build once *online* (`python -m modpage build`, no `--offline`) when the recipe uses
an item the cache has not seen: offline it warned `no texture for minecraft:iron_nugget` and
drew a checkerboard. The current tool writes `dist/curseforge.md` beside the older
`curseforge.html`, and the README diff is large because the pages had not been rebuilt with this
tool version before.

**Small things.** `set_camera_angle` returns a screenshot itself, so no `capture_screenshot`
after it; position [6, 30, −22] target [0, 27.5, 0] frames the face. Existing masters span about
27..255. `risky_eval` on `armorpieces_api` lists `pieces, open, openFor, close, create, packs,
anchors, publish, statusDir, currentPiece, displayName, state, data, fittings,
availableFittings, editPart, applyPartEdit, effectSchema, effectRow, effectFromRow,
isWorkspace, save, readRecipe, refresh` - nothing for masks or the recipe centre, which is why
the file routes above are the way.
