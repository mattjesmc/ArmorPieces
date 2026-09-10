# Brief: Dorsal Fin

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the second
batch of four (skim the lessons in spire.md, antennae.md and horsetail.md - the three crest
parts done through the bridge - and knee_studs.md for the rig frame). From the `crest` row of
`docs/plans/part-variety.md`:

> **Dorsal Fin** - A scalloped fin along the midline of the skull, webbing between the rays.
> Theme: Tidal. Fitting: `inlay`.

**Part.** `armorpieces:dorsal_fin`, socket `crest` only, in the mod's own pack. Display name
"Dorsal Fin". Fittings: `armorpieces:inlay`, one mask, covering the webbing only - the rays stay
the material, the web takes the dye. No effects, no loot, no static layer.

**Shape.** `crest` is not a mirrored socket: model the whole thing, centred on x = 0, on the
head bone. The head box is x -4..4, y 24..32, z -4..4 (pivot 0, 24, 0); the helmet shell is that
box inflated a full unit, so its top plane is y 33, and the anchor is at Blockbench (0, 32, 0).
Read the envelopes in the `armorpieces_new` reply: the other crest parts are not compared (never
worn together) but give the height gauge - brush_crest tops out at 39, spire at 40, feathering
at 44 - and the brow parts on the same bone all sit below y 33.3, so a fin that lives above the
crown is clear of them. Build five rays, each its own bone, thin upright cubes 0.5 wide (x) and
0.5 deep (z), spaced along the midline from z -3 to z +3 (about z -3, -1.5, 0, 1.5, 3), their
bases half a texel inside the shell at y 32.5, heights 2 / 3.25 / 4 / 3.25 / 2.25 so the peak
is over the crown and the fin trails lower toward the back, each bone tipped back a little
further than the last about X (positive X tips an upright toward +Z, the back: about 5, 10, 15,
20, 25 degrees) so the rays fan. Between each pair of rays one web plate, its own bone, 0.25
wide in x, sitting between the two rays' bases and rising to about two thirds of the shorter
ray so the top edge scallops between the rays; tilt each web to match the mean of its two rays.
Keep everything inside x ±0.5 and below y 37.

**Sheets.** Master: rays light `[top, bottom]` brighter at the tip with a dark base row; webs a
step darker than the rays, `[top, bottom]` dark at the base to lighter at the scalloped edge.
Inlay mask: the four webs' faces only, the same gradient.

**Recipe.** Centre item `minecraft:prismarine_crystals` (a flat item, unused by any template),
paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
dorsal_fin` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-03 in 23 bridge calls: 1 `armorpieces_new`, 9 `add_group`, 9 `place_cube`,
2 `remove_element` (starter cube, then its bone), 1 `armorpieces_set_part`, 4 `armorpieces_paint`,
1 `armorpieces_check`, 3 `set_camera_angle`, 1 `armorpieces_save`. No `risky_eval`, no
`modify_cube`, no hand-edited file, and the save went through first time without `force`.

**What I built.** Nine bones under `part`, all pivoted at Blockbench (0, 32.5, z) - half a texel
inside the helmet shell, the crest trick from `spire` - and each rotated about X only. Five rays
(`ray1`..`ray5`) at z -3 / -1.5 / 0 / 1.5 / 3, cubes 0.5 x h x 0.5 modelled straight up from the
pivot with h = 2 / 3.25 / 4 / 3.25 / 2.25, bones at +5 / +10 / +15 / +20 / +25 degrees. Four webs
(`web1`..`web4`) at the midpoints z -2.25 / -0.75 / 0.75 / 2.25, cubes 0.25 wide in x spanning the
full 1.5 between the two ray *pivots* (so each end laps 0.25 into a ray's box, the profile's
quarter-unit joint), heights 1.33 / 2.17 / 2.17 / 1.5 - two thirds of the shorter neighbour - and
bones at the mean angle, +7.5 / +12.5 / +17.5 / +22.5. Envelope came out x -0.25..0.25,
Blockbench y 32.21..36.43, z -3.25..4.18: inside the brief's x +-0.5 and y 37 ceiling, and well
under brush_crest's 39 / spire's 40 / feathering's 44. Data: `crest` only, fitting
`armorpieces:inlay`, no effects, loot or static layer; recipe `minecraft:prismarine_crystals` in
a paper ring.

**`!` lines accepted: none.** The finished check is `ok: nothing needs a decision` with zero
notes - `all clear by more than half a unit` from every brow and horns part on the head bone,
because nothing on this part goes below y 32.21 and the tallest brow part (coronet) stops at
33.21 but sits at z -6.18..-2.25, forward of the fin's front ray. The only `!` that ever appeared
was the standard 54/54 unpainted faces while the sheet was blank.

**Arithmetic, confirmed to the hundredth again.** Tip of a ray = pivot + h x (cos a, sin a):
ray3 (h 4, 15 degrees) was predicted at Blockbench y 36.36, z 1.04, and the check's envelope
maxima (36.43 in
y with the half-width corner, 4.18 in z off ray5) matched. Worth knowing for a *plate* rather
than a chain: a web bone rotated about a pivot at its own mid-z lifts one bottom corner and drops
the other by (half its length) x sin a. At the steepest web (22.5 degrees, 1.5 long) that is
+-0.29, so the raised corner sits at y 32.79 - still under the shell's top plane at y 33, so the
whole bottom edge stays buried and no seam shows. Sink a tilted plate to 32.5, not 32.9.

**Painting: four calls, and the second pair was a value fix, not a coverage fix.** Call 1 covered
all 54 master faces (`*.*` base 130, then each ray `[230..235, 142..148]` with `up` 245-252 and
`down` 70, each web `[178..182, 88..90]`), plus 23 `pixels` - a dark base row across all four side
faces of every ray and three specular texels on the ray tips. Call 2 was the 32 inlay faces.
Zero unpainted faces after call 1, so the *check* was happy - but the screenshot was not: the
brief's "webs a step darker than the rays" at 178/88 against rays at 232/145 read as a shadow
trench from three metres, and the fin looked like a comb of five spikes with nothing between
them. Calls 3 and 4 re-lit the webs to `[200..204, 128..130]` / up 222-226 / down 90 and lifted
the ray base row from 85 to 110. **A step darker on a 1-2 texel wide face is about 30 values, not
60**: the check can only tell you a face is empty, never that it is too dark to see, so take the
screenshot before you believe the sheet is done. What the painter did not cover, and did not need
to: nothing here is smaller than a face except the base row and the tip specks, and the `pixels`
list handled both - `draw_shape_tool` was never needed.

**For the next part.**
- The inlay mask is a straight copy of the master's web entries, so when the master's values
  changed the mask had to be repainted too (call 4). Settle the master's greys on a screenshot
  *first*, then paint the mask once.
- A 0.25-wide plate and a 0.5-wide post both unwrap to 1 texel in x, so the web's flat sides are
  its `east`/`west` faces (2 texels of z by h) and the *only* place a gradient shows. On a ray,
  every side face is 1 texel wide; the whole ray is four 1-texel columns.
- `minecraft:prismarine_crystals` is now taken as a template centre item (`prismarine_shard` was
  already `head_fins`). It is a flat item, so no icon work - but `python -m modpage build
  --offline` warned it had never been cached; one plain `python -m modpage build` fetched it and
  a repeat offline build is silent. README text was unchanged by the online run, only the icon.
- `armorpieces:aerials` was the open tab when the session started and stayed untouched;
  `armorpieces_new` made dorsal_fin active.
