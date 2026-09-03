# Brief: Epaulettes

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the third
batch of four (skim the lessons in wing_cases.md for the arm frame and the pauldron
constraints). From the `pauldrons` row of `docs/plans/part-variety.md`:

> **Epaulettes** - Flat boards with a fringe of cords hanging off the outer edge. Theme: Court.
> Fitting: `inlay`.

**Part.** `armorpieces:epaulettes`, socket `pauldrons` only, in the mod's own pack. Display name
"Epaulettes". Fittings: `armorpieces:inlay`, one mask, covering the board's cloth top and the
cords - the dye is the regiment's colour; the board's metal edge and the cord tips stay the
material. No effects, no loot, no static layer.

**Shape.** `pauldrons` is a mirrored socket riding the arm: model ONE arm, the LEFT, which in
this rig is at NEGATIVE x. The arm box is x -8..-4, y 12..24, z -2..2 (pivot -5, 22, 0); the
chestplate's arm shell is that box inflated a full unit, x -9..-3, y 11..25, z -3..3, and the
anchor is at Blockbench (-6, 22, 0). "Outboard" is more negative x. Two hard limits: nothing
inside the shell shows, and a turned head sweeps everything above y 23 inboard of x -7.1, so
the board sits on TOP of the shoulder shell (y 25) and stops at x -7.2 inboard. Read the
envelopes in the `armorpieces_new` reply for the other pauldrons parts (spaulders, mantle,
beast_head, wing_cases) as the gauge, though they are never compared, and note the vambraces
parts lower on the same bone. Build: a `board` bone carrying the board, x -9.6..-7.2,
y 25.1..25.6, z -2.6..2.6, half a unit thick, lying flat on the shoulder a tenth above the
shell; a raised rim along its outer edge, x -9.85..-9.35, y 25.1..25.85, z -2.6..2.6 (the metal
crescent); a small button cube 0.75 square on top near the inboard end at x -8.1..-7.35,
y 25.6..25.95, z -0.375..0.375; and a `fringe` bone under the rim carrying five cords hanging
straight down off the outer edge outside the arm shell: each 0.5 wide in z and 0.35 thick in x
at x -9.7..-9.35, from y 25.1 down to y 22.0, spaced at z -2.25 / -1.1 / 0 / 1.1 / 2.25, each
its own cube, their tips capped by painting. Nothing goes below y 21.5 (wing_cases' lower plate
starts at 19.5 but is a different part on the same socket, never compared).

**Sheets.** Master: board top and cords mid grey `[top, bottom]`, the rim and button bright
metal, cord tips a brighter bottom row (`pixels`), the board's underside dark. Inlay mask: the
board's top face, its front and back edges, and every cord face except the bottom texel row of
each cord - build the mask from the same face list, then null the rim and button.

**Recipe.** Centre item `minecraft:raw_gold` (a flat item, unused by any template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
epaulettes` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

Built 2026-09-03 in 16 bridge calls: 1 `armorpieces_new`, 2 `add_group`, 2 `place_cube`,
2 `remove_element` (starter cube, then its bone), 2 `modify_cube`, 1 `armorpieces_set_part`,
3 `armorpieces_check`, 2 `armorpieces_paint`, 1 `set_camera_angle`, 1 `armorpieces_save`, plus
the two repo checks and the page build. No `risky_eval`, no hand-edited file, and the save went
through first time without `force`.

**What I built.** Two unrotated bones under `part`. `board` (pivot -7.2, 25.1, 0) carries the
three cubes exactly as briefed: `board` x -9.6..-7.2, y 25.1..25.6, z -2.6..2.6 (the flat cloth
board, 0.1 above the shoulder shell's y 25 top, stopping at x -7.2 so the turned head clears it),
`rim` x -9.85..-9.35, y 25.1..25.85, z -2.6..2.6 (the metal crescent standing 0.25 proud of the
board's top) and `button` x -8.1..-7.35, y 25.6..25.95, z -0.375..0.375. `fringe` (pivot
-9.5, 25.1, 0) carries five cords, x -9.7..-9.35, y **22.0..25.35**, 0.5 wide in z. Two
deviations from the letter of the brief, both to keep the check silent:
- the cords' tops go to y 25.35 rather than 25.1, so each cord's `up` face is buried a quarter
  unit inside the rim (y 25.1..25.85 at the same x and z) instead of being coplanar with the
  board's underside - the profile's "overlap joints by a quarter unit", applied vertically.
- the outer cords sit at z -2.55..-2.05 and 2.05..2.55 instead of ±2.25±0.25. At exactly ±2.0
  the check said `fringe's z face at -2 lies on the body surface` (twice) - the arm box's own
  z planes. A 0.05 shift outboard moved both faces off that plane and the notes vanished; the
  cord spacing is visually unchanged (centres -2.30 / -1.10 / 0 / 1.10 / 2.30).

Final envelope, Blockbench x -9.85..-7.2, y 22.0..25.95, z -2.6..2.6; reach 6.03; the only
remaining line is the note `pair spans 19.70 across the figure, over the 18 the shoulders span`,
which every part that sits outboard of x -9 gets and which spaulders (-10.33) and wing_cases
(-11.02) exceed by more.

**The `!` I accepted: none.** The only `!` that ever appeared was the standing "faces have no
paint behind them", which the two paint calls cleared. Nothing shares a plane with the vambraces
parts on the same bone - the check reports `all clear by more than half a unit`, because the
whole part lives above y 22 and the highest vambraces part (claws) tops out at y 18.2.

**Painting: two calls, one per sheet, and between them they covered all 48 faces** - zero
unpainted, no stray paint, no colour on a greyscale sheet. Master: `*.*: 120` as the base, then
`board.up [170,145]` and the z edges `[150,118]` for the cloth, `board.down: 55` for the dark
underside, `rim.*: 215` with the outboard `rim.west [250,200]` and `rim.up: 235` as the metal
crescent, `button.up: 250`. Cords went in as `cord_x.*: [150,95]`, mid grey darkening downward.
Mask `part_inlay`: `board.up: 210`, its `north`/`south` edges 190, `cord_x.*: 195`, then
`rim.*: null` and `button.*: null` - nulling a face that was never painted on that sheet is
harmless and reads as the intent.

What the painter did NOT cover: the single-texel tip row. A `[top, bottom]` gradient shades the
whole face, so the bright cord tips are the `pixels` list of the master call (20 texels, 220 -
the bottom row of each cord's four side faces) and their negatives are the `pixels` list of the
mask call (the same 20 texels, `value: null`, so the tip texel and the `down` cap stay material
while the rest of the cord takes the dye). Read the rows off the check's `sheet layout`:
`east 48,1 1x4` means the column x=48, rows y 1..4, so the tip row is y=4 - and note the fifth
cord landed in a different sheet row (`44,3 1x4`, tip row y=6), so do not assume the cords are
laid out in a straight line.

**For the next part.**
- `modify_cube` re-lays a resized cube's UV, but here both resized cords kept their old slot -
  still, re-read the layout from a full `armorpieces_check` after any resize before writing a
  `pixels` list. `armorpieces_check brief: true` does NOT print the sheet layout; the full one
  does.
- A face lying on a plane of the *reference body* (z ±2 on the arm, and presumably x ±4 / y 12
  and 24 on the torso) is reported as a note even when the cube is two units outboard and
  physically nowhere near it. It is only a note, but 0.05 of clearance buys silence.
- `minecraft:raw_gold` was free as a template centre. `python -m modpage build --offline` warned
  it had never been cached; one plain `python -m modpage build` fetched it and the three pages
  came back `unchanged`, exactly as the antennae and wing_cases sessions found.
- `set_part` reported `sheets_created: [part_inlay]` and the mask was paintable in the next call,
  so the "part data before masks" ordering still holds.
