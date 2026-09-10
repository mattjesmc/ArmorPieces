# Brief: Sallet Slit

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the twelfth
batch — six parts rather than the usual four, the mod's first family that is **flat rather than
cubic** (read `docs/plans/visor-styles.md`, then `barbute.md`'s lessons: same bone, same plate,
same cut-is-the-part discipline). This is the first visor in the family with a **second, proud
cube**, so it is where the two-depth rule gets tested. From `docs/plans/visor-styles.md`:

> **Sallet Slit** - The single narrow ocularium under a jutting brow, the plainest sight a helmet
> has. Opening: one slot, full width. Fitting: `guard` (the brow reinforce).

**Part.** `armorpieces:sallet_slit`, socket `brow` only, in the mod's own pack
(`src/main/resources`, namespace `armorpieces`), so the master lives in
`tools/decoration_masters/sallet_slit.png` and is installed on save. Display name "Sallet Slit".
Fittings: `armorpieces:guard`, one mask, covering the brow band only — the plate stays the
helmet's material and the reinforce takes a second metal. No static layer, no effects, no loot.

**The frame, which every visor in this family shares.** `brow` is not a mirrored socket: model the
whole thing on the head bone. The head box is x -4..4, y 24..32, z -4..4 (pivot 0, 24, 0); the
helmet shell is that box inflated a full unit, so its front plane is z -5; the anchor is at
Blockbench (0, 28, -4). **The face is empty.** Every part sharing this bone was measured: the
furthest forward any reaches is `brush_crest` at z -3.5, then `feathering` -3.0, `cheek_guards`
-2.4, `comb` -2.1, `horns` and `helm_wings` -2.0, `antlers` -1.7, `head_fins` -1.4 — so anything
in front of z -4 is free at any height and any width, and the clash lines should come back
silent. The other brow parts are never compared; the shipped `visor` is a competitor, not an
obstacle. What is left to dodge: the shell plane z -5, the head box's own planes (x ±4, y 24,
y 32 — stay below 32, where `comb`, `spire` and `dorsal_fin` put their bottom face), and your own
cubes.

**Shape.** Two bones. `mask` pivoted at the anchor (0, 28, -4) with a `plate`
**x -4..4, y 26..30, z -5.35..-5.10** — eight wide, four tall, a quarter thick. Then `brow`, a
child bone, with a band **x -4..4, y 29..31, z -5.60..-5.30** — full width, two tall, 0.30 thick,
proud of the plate and **overlapping its top row**.

This part covers the upper face only. A sallet's sight works because the brow juts over it and the
chin is somebody else's problem (the bevor's), so the plate stopping at y 26 is the design, not a
saving.

The overlap is the point and not sloppiness: the band's back face at z -5.30 sits 0.05 *inside*
the plate, and its y range laps the plate's top row, so **no two faces of this part are
coincident**. The checker does not flag self-coplanarity and the game z-fights it anyway —
`browband`'s session lost a cube to exactly this. The plate's own top face at y 30 ends up buried
inside the band, which is a `-` note and correct. The side faces at x ±4 are the usual note.
Nothing above y 31, nothing in front of z -5.60.

**Sheets.** The plate is 8x4 texels and the band 8x2. Rows counted from the top of the plate:
r1 = y 29..30 (behind the band), r2 = 28..29, r3 = 27..28, r4 = 26..27.

**The cut.** One slot, and only one: on the plate's north face leave r2 columns 2..7 unpainted.
That single row of absent texels, sitting directly under a brow that stands 0.25 proud of it, is
the entire part — the player's face shows through it 1.35 units behind. Cut the plate's two bottom
corner texels so the cheeks fall away, and the band's two end texels on its top row so the brow
curves with the skull. Unpainted is *absent*, not transparent.

Master: the plate a shadowed 130 falling to 105 at the bottom, because it lives under an
overhang and should look like it; the band bright, 230 along its top row dropping to 175 on its
lower row, so the step reads as a lip catching light rather than a stripe. A 90-value texel along
the top and bottom edge of the slot, which is what makes it a hole with a wall. Rim strips and
south faces take a flat 115 so no face is empty — a face with nothing behind it is a `!`, a partly
painted face is only a note — and at a quarter texel they take whatever texel they land in.

Guard mask: the band's faces at the master's own values, so the reinforce takes a second metal
with its shading intact. Preview it filled and empty and say whether a two-unit band is enough to
read as a separate piece, because `great_helm` and `frog_mouth` are both counting on it.

**Corrections from the Barbute session — the first part of this family, built clean. Read these
before painting; two of them would otherwise ship a visor with no holes in it.**

1. **Cut the south face too, in the same pattern.** `armorCutoutNoCull` draws back faces, so an
   opening cut only in the north face is filled by the *inside* of the painted south face and
   stops being a hole. Every cut described above has to be made twice — once in the north
   rectangle, once in the south — and where the silhouette is nipped, clear the matching
   rim texels as well. Barbute shipped this way and its T reads as a hole at three metres, with
   the player's own skin showing through at a hue no trim material has.
2. **Never cut a corner texel directly above or below the end column of a full-width opening.**
   Barbute cut only its two *bottom* corners: cutting the top pair as well would have left the
   brow row hanging over the eye band with nothing orthogonal holding it.
3. **Check the recipe centre against the fitting templates as well as the part templates.**
   `copper_ingot` was free of all 84 `template_*.json` but is `fitting_template_guard.json`'s
   centre, so Barbute shipped `minecraft:raw_copper` instead. `armorpieces_set_part` accepts a
   colliding centre silently — the `!` only appears on the next check. This part's centre has
   been re-checked against both sets and is free.
4. **`ruff` will never appear in your check.** It sits on the `collar` bone and no tool compares
   across bones, so the warning above about it is yours to apply by eye, or to ignore.

**Recipe.** Centre item `minecraft:iron_door` (a flat item sprite, unused by any template), paper
ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
sallet_slit` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover,
and say whether the 0.30 proud band **earns its place** or whether the family should stay strictly
one-cube. Judge from the straight-on shot (`set_camera_angle` position [0, 28, -24], target
[0, 28, 0]) plus one three-quarter ([6, 30, -22], target [0, 27.5, 0]) to check the brow's step.

**Picture budget: two screenshots, and both after the last paint call.** An image is billed by
area and re-sent on every later turn, so looks taken while painting are paid for many times over;
the leanest sessions on record took every shot after the painting was done.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-05 in 18 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 2 `add_group`,
2 `place_cube`, 1 `list_outline`, 3 `remove_element` (one failed - the starter cube is `main_0`,
not `main[0]`; the check's `bone[i]` label is a paint address, not an element id), 1
`armorpieces_check`, 2 `armorpieces_set_part`, **2 `armorpieces_paint`** (master, guard mask), 2
`set_camera_angle`, 1 `armorpieces_save`. No `risky_eval`, no `modify_cube`, no nudging, nothing
hand-edited; the save went through **without `force`** and the final check is `ok: nothing needs a
decision` with four `-` notes, all four the foreseen x = +/-4 ones (both cubes, both sides).
Geometry is exactly the brief's: `mask` at (0, 28, -4) with `plate` x -4..4, y 26..30, z
-5.35..-5.10 (uv 12,0 8x4x0.25: up 13,0 8x1, down 21,0 8x1, east 12,1 1x4, north 13,1 8x4, west
21,1 1x4, south 22,1 8x4) and child bone `brow` at (0, 30, -5.3) with `band` x -4..4, y 29..31, z
-5.60..-5.30 (uv 30,0 8x2x0.3: up 31,0 8x1, down 39,0 8x1, east 30,1 1x2, north 31,1 8x2, west
39,1 1x2, south 40,1 8x2).

**The 0.30 proud band EARNS ITS PLACE - `great_helm` and `frog_mouth` can both be built as
written.** Three things carry it, and only the first is the geometry. (a) The step is legible from
three quarters: the band's own top face is a lit strip a texel wide at 200 while the plate below it
is 130 falling to 105, and that strip is what says "two plates riveted together" rather than
"a stripe painted on one". (b) Straight on, the value break alone does most of the work - a 230/175
band over a 130/105 plate reads as a separate piece at three metres *even with no fitting applied*,
which matters because a part must look right when its fitting is absent. (c) It gives the slot an
overhang: the 90-value underside of the band sits directly over the opening and the sight reads as
recessed rather than as a gap in a flat sheet. So the family should **not** stay strictly one-cube.
The caveat for Great Helm: two units is the minimum that reads: one row would be indistinguishable
from a painted line, and the band only survives at two because its top row is *unshaded by the
plate's gradient*, i.e. it needs a value clearly outside the plate's range, not merely above it.

**A THIRD template set exists and neither the plan nor Barbute knew about it: `skin_template_*`.**
`minecraft:iron_door` is free of all 85 `template_*.json` and all four `fitting_template_*.json` -
and it is `skin_template_gothic.json`'s centre. That is 18 more grids (14 armor skins plus the
four fittings) that the visor-styles table never checked. Same trap as Barbute's: `set_part`
accepted it silently and the `!` only appeared on the next check. This part ships
**`minecraft:shears`** - flat item, free of all three sets, and thematically the cut itself. I then
dumped every centre in `data/**/{template,fitting_template,skin_template}_*.json` at once, so this
is settled for the rest of the family: **`blaze_rod`, `netherite_ingot`, `skull_banner_pattern` and
`trident` are all still free against all three sets.** The skin centres to avoid, for the record:
leather_chestplate, chain, yellow_wool, iron_door, golden_helmet, copper_grate, iron_boots,
chainmail_boots, bucket, iron_block, echo_shard, pink_petals, tropical_fish, iron_axe.

**Two paint calls, and what the painter did and did not cover.** Master: 5 face entries (`*.*` 115,
`plate.north` [130, 105], `band.north` [230, 175], `band.up` 200, `band.down` 90) plus 60 pixels -
32 at 90 for the slot walls on both faces, 28 nulls for every cut. Guard mask: 4 face entries
(`band.*` 115, `band.north` [230, 175], `band.up` 200, `band.down` 90) and 8 nulls repeating the
band's cuts, so no mask texel falls outside the master's silhouette. Finished master: 112 opaque
texels, greyscale, range 90..230; mask 44 texels, verified with Pillow to be a strict subset.
**Two deliberate deviations from the brief**, both in service of its own sentence about the step
reading as a lip: `band.up` is 200 and `band.down` 90 rather than the flat 115 the brief gave every
rim. The up-face is the only thing the depth reads as from an angle (Barbute said the same) and the
down-face is the overhang shadow over the sight - painting them 115 would have thrown away the
part's one idea. The plate's rims, the plate's south face and the band's south/east/west stay at
the brief's flat 115. What the painter did **not** do: give the band's south face its own gradient
(it is inside the helmet and never lit), or vary the 90 walls - and note that painting the slot's
end columns *and* the row under it at 90 makes the plate's whole third row 90, which is not a bug:
it reads as one continuous shadow under the sight, with the cheek taper falling out of it.

**Cut discipline, confirmed.** Barbute's back-face rule is right and was applied: the slot is cut
in north (x 14..19, y 2) *and* south (x 23..28, y 2), symmetric so the same offsets serve both; the
plate's bottom corners are cut on north, south, the `down` rim (21,0 and 28,0) and the `east`/`west`
rim bottoms (12,4 and 21,4); the band's top-row ends are cut on north, south, the `up` rim (31,0 and
38,0) and the `east`/`west` rim tops (30,1 and 39,1). **A cut on a proud cube needs its rim texels
cleared exactly like a cut on the plate** - the band is only 0.30 thick and a nipped corner still
edged in steel from above is the same defect. The corner rule held: the slot's supports are columns
1 and 8 of r2 and neither the texel above nor below them was cut. The plate's `up` face is buried
inside the band, a `-` note the check did not even raise; nothing is coplanar with anything, as the
0.05 z lap and the one-row y lap were designed to ensure.

**One thing worth knowing for the rest of the family: the slot lands on the skin's eyes.** With the
plate at y 26..30 the slot's row is y 28..29, and the straight-on shot shows the player's eye
texels through it - the pupils, at a hue no trim material has. That is the payoff of keeping x and y
on integers, and it means Frog-Mouth's slot at the very brow (y 30..31) will show forehead, not
eyes, which is exactly what a frog-mouth helm is for and should be sold as such.

**modpage.** The same three-step dance as Barbute: `--offline` drew `minecraft:shears` as a
checkerboard, a plain `python -m modpage build` fetched it, and the third build reported
`unchanged` on all three outputs. `modpage.yml` needed nothing. The remaining warnings
(`minecraft:chain`, two `armorpieces:smithing_skin` recipes) are pre-existing.
