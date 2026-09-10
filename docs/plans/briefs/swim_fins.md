# Brief: Swim Fins

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the third
batch of four (skim the lessons in knee_studs.md and talons.md for the leg frame, and
dorsal_fin.md for rays-and-web construction and the greys that read). From the `greaves` row of
`docs/plans/part-variety.md`:

> **Swim Fins** - Broad fins flaring off the outer shin, webbed. Theme: Tidal. Fitting: `inlay`.

The plan floats a small effect for this part; this brief gives it none - keep it an ornament.

**Part.** `armorpieces:swim_fins`, socket `greaves` only, in the mod's own pack. Display name
"Swim Fins". Fittings: `armorpieces:inlay`, one mask, covering the webbing only - the rays stay
the material, the web takes the dye, exactly as the Dorsal Fin does. No effects, no loot, no
static layer.

**Shape.** `greaves` is a mirrored socket on the leg bone: model ONE leg, the LEFT, which in this
rig is at NEGATIVE x. The leg box is x -3.9..0.1, y 0..12, z -2..2 (pivot -1.9, 12, 0); the
boots shell is that box inflated 0.9, so its outer side plane is x -4.8 and its front is
z -2.9; the anchor is at Blockbench (-1.9, 4, -2) on the front of the shin. "Outboard" is more
negative x, and anything with x above -4.8 is inside the boot. Read the envelopes in the
`armorpieces_new` reply: tassets parts on the same bone come down to y 5.18 at the front and
reach x -4.9 on the outside (pelt to x -4.9, scale_skirt to -4.9 at y 7.1 and up), and the
knees parts sit on the front at y 3.9..8.3, so this fin lives on the OUTER side of the lower
shin, below y 5 and behind z -2.9 - the one face of the lower leg nothing else uses. Build it
like the dorsal fin turned on its side: a `base` bone at (-4.8, 1, 0) and three ray bones
pivoted on the outer shin at Blockbench x -4.3 (half a unit inside the shell), y 1.0, at
z -1.75 / 0 / 1.75, each ray a 0.5x0.5 post modelled straight up from its pivot with heights
2.5 / 3.5 / 3.0, each bone rotated about Z so the rays lean OUTBOARD (for an upright on the
negative-x side, a POSITIVE Z rotation tips the top toward -x; check the first reply and flip
if it leaned into the leg) by 40 / 50 / 60 degrees, so the fin flares out and slightly back
like a flipper. Two web plates between the rays, each its own bone: a plate 0.25 thick in x,
1.75 long in z so it spans between two ray pivots and laps a quarter unit into each ray's box,
and two thirds of the shorter neighbour tall, pivoted at the midpoint z on the same x -4.3 /
y 1.0 line as the rays and rotated about Z by the mean of its two rays' angles, so it leans
with them and lies in the fin's plane. The rays' outboard tips should land no further
than x -7.5 (the check's `past boots x` is the gauge) and nothing goes below y 0.

**Sheets.** Master: rays light `[top, bottom]` brighter at the tips with a darker base row;
webs about thirty values darker than the rays, not sixty - the dorsal fin session found a
bigger step reads as a trench. Inlay mask: the webs' faces only, the same gradient. Screenshot
after the master call and adjust before painting the mask.

**Recipe.** Centre item `minecraft:kelp` (a flat item, unused by any template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
swim_fins` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-03 in 27 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`list_outline`, 6 `add_group`, 5 `place_cube`, 2 `remove_element` (starter cube, then its bone),
1 `armorpieces_check`, 1 `armorpieces_set_part`, **4 `armorpieces_paint`**, 4 `set_camera_angle`,
1 `armorpieces_save`. No `risky_eval`, no `modify_cube`, no nudging, no hand-edited file; the save
went through first time without `force`.

**What I built.** Exactly the brief's construction, and every number it gave landed. A `base` bone
at Blockbench (-4.8, 1, 0) carrying five children: `ray1`/`ray2`/`ray3` pivoted at (-4.3, 1,
-1.75 / 0 / +1.75), rotated about Z by +40 / +50 / +60, each a 0.5 x h x 0.5 post modelled
straight up from its pivot with h = 2.5 / 3.5 / 3.0 (cubes `ray_front`, `ray_mid`, `ray_rear`);
`web1`/`web2` pivoted at the midpoints (-4.3, 1, -0.875 / +0.875), rotated by the mean angles +45
/ +55, each a 0.25-thick plate spanning the full 1.75 between the two ray *pivots* (so 0.25 laps
into each ray's box) and two thirds of the shorter neighbour tall, h = 1.67 / 2.0 (cubes
`web_front`, `web_rear`). Data: `greaves` only, fitting `armorpieces:inlay`, no effects, loot or
static layer; recipe `minecraft:kelp` in a paper ring.

**Rotation sign, confirmed on the first cube.** The brief's guess was right: on the negative-x
(left) leg a **positive Z rotation leans an upright post outboard**, toward -x. A point (0, h)
above the pivot goes to (-h sin a, h cos a), and the far top corner of a 0.5-wide post to
(-0.25 cos a - h sin a, +0.25 sin a + h cos a). The check confirmed it as soon as `ray_front`
existed: predicted x -6.10, reported `past boots x +1.30` against the shell plane at x -4.8.
Final envelope (bone-local x 2.21..5.24, y 8.56..11.22 = Blockbench **x -4.11..-7.14, y 0.78..3.44,
z -2.00..2.00**) matched the arithmetic to the hundredth, so nothing needed moving: tips inside the
brief's -7.5 ceiling, nothing below y 0 (lowest corner 0.78, a base corner that dips by 0.25 sin a),
and the top corner at 3.44 stays **0.36 clear of `garters`'s 3.80**, the lowest knees-socket part.

**`!` lines accepted: none.** The saved check is `ok: nothing needs a decision` with 18 `-` notes.
Worth recording what those notes are, because the brief's "the one face of the lower leg nothing
else uses" is true only of the *front*-and-*knees*-and-*tassets* crowd: the outer shin below y 3.5
is shared with the **spurs** socket, whose parts wrap round from behind. Seven hull OVERLAPs
(`ray3`/`web2`/`ray2` into `heel_wings`'s clasp, vane_upper and vane_lower, into `spurs`'s heel,
into `streamers`'s cuff) and three shared-plane notes at z = 0 and z = 1.5 - all of them `-`,
all of them either inside the boots shell (the check says so itself) or between a 0.5-wide ray and
a heel wing that sweeps backwards, and the tightest real gap is 0.13 (`web2` to `heel_wings`'s
vane_lower in z). Rear ray and rear web are the parts that touch; moving the fin forward in z would
have cured it but would have walked into the knees/greaves front instead, so the notes stand.

**Paint: four calls, three of them the master, all 30 faces covered from the first one.** Call 1
laid `"*.*": 150` then every face of all five cubes (rays `[240ish, 155ish]` on the flanks, up
250-254, down 80; webs ~30 lower) plus 12 `pixels` for a dark base row across the ray flanks -
zero unpainted faces immediately. Calls 2 and 3 were value fixes found in screenshots, not
coverage: the flank *bottoms* at 140-155 plus Blockbench's own directional shading made a dark
trench where the webs meet the rays, so call 2 lifted every bottom (rays now `[242,178]`, webs
`[212,150]`, base row 134) and call 3 lifted only the **west** faces (rays `[230,174]`, webs
`[202,148]`). That last one is the lesson: on a blade tilted 40-60 degrees about Z, the west face
is no longer a side face - its normal has swung to point mostly *down*, so the preview (and the
game's face lighting) shades it like a `down` face. **Pre-compensate a steeply tilted face by
about +20 rather than shading it as a flank.** The dorsal fin's "30 values, not 60" for the
web-to-ray step held: 30 reads as webbing, and it was right the first time here.
Call 4 was the 12 inlay-mask faces, a straight copy of the master's final web values - painted
after the master's greys were settled on a screenshot, which is what the dorsal fin session asked
for and it saved a repaint.

What the painter did not cover: the west-face lift in call 3 overwrote three of the 12 base-row
pixels (the west columns at 14,3 / 18,4 / 22,3), so the darker root row now survives on the east,
north and south flanks only - deliberate, since those west bottoms are the values that were too
dark. Nothing else here is smaller than a face; `draw_shape_tool` was never needed.

**Geometry-to-sheet, for a plate on its side.** A 0.5 post unwraps to four 1-texel columns (h+1
tall at h = 2.5, so a `[top, bottom]` pair has 3-4 rows to work with); the 0.25 x h x 1.75 web
unwraps with its **east/west** faces 2 texels of z by 2 rows - the only place a gradient shows on
the web - and its `up` face is a 1x2 strip that is the plate's outer *edge*, which is what you see
when the fin is viewed from outboard-and-above. Give that up face the brightest web value; it does
a lot of the reading.

**For the next part.** `minecraft:kelp` is now taken as a template centre item. As with
`raw_iron`/`flint`, `python -m modpage build --offline` warned `no texture for minecraft:kelp`;
one plain `python -m modpage build` cached it and the repeat offline build reports every page
`unchanged`. Two other tabs were open (`aerials`, `dorsal_fin` active) and `armorpieces_new` made
swim_fins active without touching them. On any **greaves** part built on the outer shin below
y 3.5, plan against the *spurs* socket, not the knees/tassets one: `heel_wings` alone spans
Blockbench x -6.52..-2.90, y 0.72..8.28, z 0.00..7.69 and will produce hull overlaps for anything
that flares outboard behind z 0.
