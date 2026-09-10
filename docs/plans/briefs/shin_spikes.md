# Brief: Shin Spikes

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the fifth
batch of four, a Beast set (read knee_studs.md, padding.md and swim_fins.md for the leg frame
and the crowded shin, and talons.md for a chain pointing along Z). From the `greaves` row of
`docs/plans/part-variety.md`:

> **Shin Spikes** - Two forward spikes off a narrow plate. Theme: Beast. Fitting: `guard`.

**Part.** `armorpieces:shin_spikes`, socket `greaves` only, in the mod's own pack. Display name
"Shin Spikes". Fittings: `armorpieces:guard`, one mask, covering the two spikes; the plate
stays the material. No effects, no loot, no static layer.

**Shape.** `greaves` is a mirrored socket on the leg bone: model ONE leg, the LEFT, which in
this rig is at NEGATIVE x. The leg box is x -3.9..0.1, y 0..12, z -2..2 (pivot -1.9, 12, 0); the
boots shell is that box inflated 0.9, front plane z -2.9; the anchor is at Blockbench
(-1.9, 4, -2). Read the envelopes in the `armorpieces_new` reply: the knees parts own the front
of the leg from y 3.7 up (poleyns 3.7..7.1 at z -4.65..-2.65, garters from 3.8, knee_studs
3.9..6.1 at z -3.5..-3.0, padding 4.4..7.6 at z -3.45..-2.95), so this part lives BELOW y 3.6
on the front of the shin, where only the same-socket greaves parts are (never compared). Build
a `plate` bone at (-1.9, 2.2, -2.9) with a narrow plate x -2.9..-0.9, y 0.9..3.5, z -3.4..-2.95
(a tenth off the boot's front plane, its top a fifth under the knees crowd), and two spike
bones `spike_upper` / `spike_lower` pivoted on the plate's front face at (-1.9, 2.9, -3.4) and
(-1.9, 1.6, -3.4), each carrying a chain of two cubes modelled straight FORWARD along -Z from
the pivot: a base 0.7 square by 1.5 long, then a tip 0.4 square by 1.0 long starting a quarter
unit before the base's end (its own child bone, unrotated), the whole spike bone rotated about
X so it points forward and a little up - about 20 degrees (for a segment modelled along -Z a
POSITIVE X rotation tips its far end UP on this rig; talons found +X curls a +Z segment down,
which is the same rule - confirm on the first reply). Tips land near z -5.9, y 3.7 and 2.4;
nothing reaches above y 3.8 and nothing goes wider than x -2.3..-1.5 on the spikes.

**Sheets.** Master: plate mid grey `[top, bottom]` with a lighter top row; spikes bright metal
lighter toward the tip, the tip's end face brightest, dark undersides. Guard mask: the four
spike cubes' faces only, shaded like the master.

**Recipe.** Centre item `minecraft:pointed_dripstone` (a flat item icon, unused by any
template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
shin_spikes` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-03 in 19 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`list_outline`, 5 `add_group`, 5 `place_cube`, 2 `remove_element` (starter cube, then its bone),
2 `armorpieces_check`, 1 `armorpieces_set_part`, **4 `armorpieces_paint`**, 3 `set_camera_angle`,
1 `armorpieces_save`. No `risky_eval`, no `modify_cube`, no nudging; the save went through first
time without `force`.

**What I built.** The brief's construction, with two deliberate deviations (below). A `plate`
bone at Blockbench (-1.9, 2.2, -2.9) carrying one cube `plate` (-2.9, 0.9, -3.4)..(-0.9, 3.5,
-2.95); two spike bones on the plate's front face, `spike_upper` at (-1.9, 2.9, -3.4) and
`spike_lower` at (-1.9, 1.6, -3.4), both rotated **+18 about X**, each with a base cube 0.7
square running (-2.25, y-0.35, -4.8)..(-1.55, y+0.35, -3.3) and an unrotated child bone
`spike_*_tip` at z -4.55 with a 0.4-square cube z -5.55..-4.55. Final envelope in Blockbench
**x -2.90..-0.90, y 0.90..3.75, z -5.51..-2.95**; tip axes land at y 3.60 / 2.26, z -5.44.
Data: `greaves` only, fitting `armorpieces:guard`, no effects, loot or static layer; recipe
`minecraft:pointed_dripstone` in a paper ring.

**Rotation sign confirmed, and the arithmetic landed to the hundredth.** For a segment modelled
along **-Z**, a positive X rotation tips its far end **UP**: a local point (0, 0, -L) maps to
(0, +L sin th, -L cos th). Same rule talons recorded for +Z (there it curls down). The check
confirmed it on the first cube: predicted top corner y 3.666, reported envelope top 3.67.

**18 degrees, not 20, and the base bites 0.1 into the plate.** At 20 degrees the base's far top
corner reaches y 3.742 at z -4.69 - 0.04 in front of `poleyns`'s front plane z -4.65 and above
its bottom y 3.70 (bone-local); the tip's top corner reaches 3.857, over the brief's own y 3.8
ceiling. 18 degrees puts the base corner at 3.666 and the tip corner at 3.755, both under
`garters`'s 3.80, the lowest knees-socket part *in Blockbench*. Second deviation: the base cubes
start at z **-3.3**, a tenth behind the pivot, instead of at the pivot z -3.4. Rotating a cube
whose rear face sits exactly on the pivot plane swings that face 0.1-0.2 out of the plate and
opens a wedge at the joint; starting 0.1 back buries it (rear face after rotation spans
z -3.20..-3.41, i.e. at or behind the plate's front face). Length stays the brief's 1.5.

**The brief's knees-crowd heights are BONE-LOCAL, not Blockbench.** It says "poleyns 3.7..7.1",
"garters from 3.8", "knee_studs 3.9..6.1", "padding 4.4..7.6" - those are the check's *left column*
(+Y down). In Blockbench the same parts are poleyns 4.90..8.30, garters 3.80..6.85, knee_studs
3.90..6.10, padding 4.40..7.60. Only `padding` happens to read the same in both. The brief's
conclusion ("stay below y 3.6") is still right and even conservative in Blockbench, but do not
reuse those numbers as clearances - `bone_y = 12 - bb_y` on the leg, as knee_studs recorded.

**`!` lines accepted: none.** The saved check reports zero problems and only four `-` `near`
notes, all against `knee_studs:knees` (`spike_upper` clears its studs by 0.23 in y, `plate` by
0.40). No OVERLAP at all - the first greaves part in this batch that laps nothing, because the
shin front below y 3.75 really is empty once you stay under garters. No shared plane either:
the plate's back face z -2.95 does *not* collide with `padding`'s -2.95 (their y ranges are
disjoint, 0.9..3.5 against 4.4..7.6, and the check stayed quiet), and z -3.4 misses knee_studs'
-3.5/-3.0.

**Paint: four calls - two per sheet, 98 master faces and 56 mask faces, every face covered by the
first call on each sheet.** Call 1 on `part`: `"*.*": 150`, then the plate (`[170,132]` body,
north `[182,140]`, up 205, east/west `[160,124]`/`[150,116]`, south 112, down 96) and per-cube
bases for the spikes, 195 on the base segments and 228 on the tips, with `[top,bottom]` pairs on
the 2-texel flanks, up 228/246, north (the forward end cap) 215/**255** and down 108/128 for the
dark undersides. Call 3 on `part`, calls 2 and 4 the same values on `part_guard` (shaded exactly
like the master, per knee_studs/talons - a flat mask flattens the spikes). Call 3 was a value fix
found in a profile screenshot, not coverage: the spikes' east/west flanks are the only faces you
see from outboard and at 190/168 they read as dark as the boot, so they went up ~25 (base east
`[222,200]`, west `[216,194]`, tips 248/242).

What the painter did not cover: nothing is smaller than a face here, so `draw_shape_tool` was
never needed, and there is nothing to gradient - a 0.7-square segment's end caps and a 0.4 tip's
whole six faces are 1 texel each, so the whole tip's look is six numbers. The only within-face
gradients that show are the 2x1 flanks of the base segments and the plate's 3-row north/east/west.
Note the preview compresses high values through the trim ramp: 216 and 242 on the flanks looked
almost identical to 190/168 in the screenshot, so judge the *ordering* (tip lighter than base,
down darkest) rather than expecting the render to track the numbers.

**For the next part.** `minecraft:pointed_dripstone` is now taken as a template centre item; the
first `python -m modpage build --offline` warned it had no cached texture, one plain
`python -m modpage build` cached it and the icon now draws the real dripstone. Four other tabs
were open (`thigh_sheath` active) and `armorpieces_new` made shin_spikes active without touching
them. On `greaves`, the band of the shin front between y 0.9 and 3.75 at z -3.4 or further forward
is genuinely free of every other socket - the one part of the leg where you can build forward
without lapping anything - but it is 0.05 from being on the boots shell at z -2.9, so compute the
back face rather than copying "a tenth off the shell".
