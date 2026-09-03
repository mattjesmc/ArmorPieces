# Brief: Lames

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the tenth
batch of four (read spiked_pauldrons.md, wing_cases.md and epaulettes.md first - the arm frame,
the head's sweep, the shoulder cap). From the `pauldrons` row of `docs/plans/part-variety.md`:

> **Lames** - Three overlapping curved plates stepping down the arm - the articulated answer to
> the spaulder's single shell. Theme: Knightly. Fitting: `guard`.

**Part.** `armorpieces:lames`, socket `pauldrons` only, in the mod's own pack. Display name
"Lames". Fittings: `armorpieces:guard`, one mask, covering the three lames; the shoulder cap
they hang from stays the material. No effects, no loot, no static layer.

**Shape.** `pauldrons` is a mirrored socket riding the arm: model ONE arm, the LEFT, at NEGATIVE
x. The arm box is x -8..-4, y 12..24, z -2..2 (pivot -5, 22, 0); the chestplate's arm shell is
that box inflated a full unit, x -9..-3, y 11..25, z -3..3, and the anchor is at Blockbench
(-6, 22, 0). Two hard limits: nothing inside the shell shows, and a turned head sweeps
everything above y 23 inboard of x -7.1. Read the envelopes in the `armorpieces_new` reply for
the other pauldrons parts (never compared) and the vambraces parts lower on the bone (claws top
out at y 18.2, buckler at 18.47) - keep the lowest lame above y 18.7. Build a `cap` bone at the
anchor with the shoulder cap x -9.7..-7.2, y 25.1..25.7, z -3.1..3.1 (a tenth above the shell's
top); then three lame bones down the outside of the arm, each pivoted at its plate's top
inboard edge and each rotated 4 degrees more than the last about Z so the stack flares out
(for a plate hanging BELOW its pivot on the negative-x side, a NEGATIVE Z rotation swings the
free end toward -x - cheek_guards and boot_cuffs measured it): `lame_1` pivot (-9.4, 25.2, 0)
rotation Z -4 with a plate x -9.9..-9.4, y 22.8..25.2, z -3.1..3.1 (its top a tenth inside the
cap); `lame_2` pivot (-9.65, 23.1, 0) rotation Z -8 with a plate x -10.15..-9.65, y 20.9..23.1,
z -2.9..2.9; `lame_3` pivot (-9.9, 21.2, 0) rotation Z -12 with a plate x -10.4..-9.9,
y 19.0..21.2, z -2.7..2.7 - each lame stepping a quarter unit further out and lapping the one
above by 0.3 in y, narrower in z as they go down. Each lame carries two rivet studs 0.4 square
standing 0.15 proud of its outer face near its top corners (a tenth into the plate). Compute
the rotated corners: nothing below y 18.7, nothing further out than x -11.0.

**Sheets.** Master: cap mid grey with a bright top; lames `[top, bottom]` lighter at the top
edge with a dark bottom row as the shadow of the lame above (`pixels`), each lame a step darker
than the one above; rivets bright. Guard mask: the three lames and their rivets at the master's
values, the cap left out.

**Recipe.** Centre item `minecraft:chainmail_chestplate` (a flat item, unused by any template),
paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py lames`
and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons paragraph below
filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

Built 2026-09-03 in 17 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`list_outline`, 4 `add_group`, 4 `place_cube`, 1 `remove_element`, 1 `armorpieces_check`,
1 `armorpieces_set_part`, 6 `armorpieces_paint`, 3 `set_camera_angle`, 1 `armorpieces_save`,
plus the two repo checks and the page build. No `risky_eval`, no `modify_cube`, no nudging, no
hand-edited file, and the save went through first time without `force`.

**What I built.** Exactly the brief's numbers, nothing moved. Four sibling bones under `part`
(NOT nested - the brief gives each lame an absolute pivot and an absolute rotation, so nesting
would have compounded -4/-8/-12 into -4/-12/-24). `cap` (pivot -6, 22, 0, unrotated) carries the
shoulder cap x -9.7..-7.2, y 25.1..25.7, z -3.1..3.1. `lame_1` (pivot -9.4, 25.2, 0, rot Z -4),
`lame_2` (pivot -9.65, 23.1, 0, rot Z -8) and `lame_3` (pivot -9.9, 21.2, 0, rot Z -12) each
carry a plate modelled upright in the unrotated pose (x -9.9..-9.4 / -10.15..-9.65 /
-10.4..-9.9, y 22.8..25.2 / 20.9..23.1 / 19.0..21.2, z ±3.1 / ±2.9 / ±2.7) and two 0.4-square
rivets standing 0.15 proud of the outer face and biting 0.1 into it (x -10.05..-9.8 /
-10.3..-10.05 / -10.55..-10.3, 0.3 below each plate's top, at z ±2.5 / ±2.3 / ±2.1 centres).

**The rotated corners, computed before placing and confirmed by the check.** With
`p' = pivot + (dx cos - dy sin, dx sin + dy cos)` the outermost / lowest corners land at
lame_1 x -10.066 y 22.841, lame_2 x -10.451 y 20.991, lame_3 x -10.847 y 19.152 (its plate
bottom edge y 19.048). The check's envelope came back bone-local x 2.20..5.85, y -3.70..2.95,
i.e. Blockbench x -10.85..-7.20, y 19.05..25.70, z ±3.10 - a hundredth off the hand arithmetic,
so nothing needed moving. Both hard limits held with margin: nothing below y 19.05 (limit 18.7,
buckler tops out at 18.47) and nothing further out than x -10.85 (limit -11.0). Nothing above
y 23 is inboard of x -9.4, well outboard of the head-sweep limit -7.1; the cap's inboard edge is
x -7.2. `all clear by more than half a unit` against all seven vambraces parts.

**The `!` I accepted: none.** The only `!` that ever appeared was the standing "faces have no
paint behind them", cleared by the first two paint calls. One `-` note remains: `pair spans 21.69
across the figure, over the 18 the shoulders span` - every pauldrons part outboard of x -9 gets
it, and wing_cases (22.04) exceeds it. The plates are outboard of the chestplate arm shell's
x -9 plane everywhere, and the cap floats 0.1 over its y 25 top, so no face lies on the shell and
no plane is shared. The 0.1 overlaps (lame_1's top a tenth inside the cap, each rivet a tenth
into its plate) produced no shared-plane line, as spiked_pauldrons found: a tenth is enough on a
static joint.

**Painting: six calls (two would have been enough for coverage; four were tone corrections).**
The first two - master then `part_guard` - covered all 60 faces on both sheets plus 25 pixels
each: zero unpainted, no stray paint, no colour on a greyscale sheet. Master: `*.*: 130` base,
`cap.*: [165,125]` with `cap.west: [180,140]` (west is the outboard face on this rig),
`cap.up: 205`, `cap.east: 95`, `cap.down: 60`; plates as three descending steps -
`[175,120]`/`[155,100]`/`[135,85]` with the outboard `west` a shade brighter and `up` faces
150/135/120; rivets 230/215/200 with their `west` faces 248/236/224. The guard mask repeats the
plate and rivet values verbatim and ends with `cap.*: null`, so the shoulder cap keeps the trim
material and the three lames take the fitting.

What the painter did NOT cover, and the lesson in it: **the seam row's value has to be judged in
the 3D view, not on the sheet.** Each plate's `west` face is only 3 texels tall over 2.4 units,
so one "row" of shadow is a third of the plate, and the preview's material ramp crushes low greys
- the row went in at 52, looked like a black void, barely changed at 88, and only read as an
articulation seam at 122/112/102 (the run x 39..47 y 9, x 54..61 y 10, x 6..13 y 16, which are
the bottom rows of each plate's north+west+south faces laid out contiguously). The `down` faces
had the same problem: 42-55 rendered as solid black bands under each plate (Minecraft shades a
down face at about half light on top of the ramp), and they were lifted to 118/106/95 before the
undersides read as metal. Budget two screenshot-and-correct rounds for any part whose undersides
face the camera.

**For the next part.**
- On a 2-3 texel face, a `[top, bottom]` gradient is nearly the whole shading budget; a
  single-texel accent row is a *third* of the face, so pick its value one or two steps below the
  face, not five. Cross-check on the model before saving.
- `remove_element main` took the starter bone and its cube together again (the outline showed
  `main` as the bone and `main_0` as the cube; one call, 10 cubes left).
- Sibling bones with absolute pivots are the right structure for a stepped stack: each plate's
  rotation is independent and the arithmetic stays one line per corner.
- `minecraft:chainmail_chestplate` was free as a template centre and already cached:
  `python -m modpage build --offline` ran clean, 97 recipes, no "no texture" warning.
