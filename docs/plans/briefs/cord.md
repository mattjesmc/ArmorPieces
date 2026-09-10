# Brief: Cord

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the sixth
batch of four (read pouch_belt.md's lessons first - same socket, the strap ring, and the arm box
the check cannot see - then girdle.md). From the `belt` row of `docs/plans/part-variety.md`:

> **Cord** - A rope belt with a knot and a tassel falling at one hip. Theme: Court. Fitting:
> `inlay`.

**Part.** `armorpieces:cord`, socket `belt` only, in the mod's own pack. Display name "Cord".
Fittings: `armorpieces:inlay`, one mask, covering the whole rope, knot and tassel - a silk cord
takes the dye entire. No effects, no loot, no static layer.

**Shape.** `belt` is not a mirrored socket: model the whole thing on the body bone. The torso
box is x -4..4, y 12..24, z -2..2 (pivot 0, 24, 0); the leggings shell is that box inflated 0.5
and the chestplate's a full unit (x -5..5, y 11..25, z -3..3), so every rope face lies past
x ±5 or z ±3; the anchor is at Blockbench (0, 12, 0). The player's ARMS hang at x ±4..±8,
y 12..24, z -2..2 on their own bones and the check never mentions them: anything at the flank
inside that box is invisible, so the knot and tassel go on the FRONT. Read the envelopes in the
`armorpieces_new` reply (the other belt parts are never compared; carapace's lowest lame at
y 15.6 and wing_roots at 14.5 on the back are what the clash lines measure). Build: a `rope`
bone with four plates closing a square ring exactly as pouch_belt's strap, but half a unit
square in section (front z -3.6..-3.1, back z 3.1..3.6, flanks x ±5.1..±5.6, each the full
span so the corners double up), at y 12.5..13.0; a `knot` bone at the front, left of centre,
with a knot cube x -1.7..-0.3, y 12.2..13.3, z -4.1..-3.2 (its inner face 0.1 inside the front
rope's slab, no shared plane) and a small loop cube 0.5 square standing on the knot's face; a
`tassel` bone under the knot, pivoted at (-1.0, 12.2, -3.65), with a hanging cord 0.4 square
from y 12.3 down to y 10.0 (lapping the knot by a tenth) and a tuft 0.9 wide (x), 1.3 tall,
0.8 deep at y 8.8..10.1 under it, the bone rotated 4 degrees about X so the tassel swings a
little forward at the tip (for a part BELOW its pivot a positive X rotation swings it toward
-Z - thigh_sheath measured it; confirm on the reply). The tassel hangs in the gap between the
thighs (x -1.4..-0.6 is between the legs' inner faces at x ±0.1 plus the shells), in front of
the leggings, so it clips nothing when the legs swing. Nothing above y 13.3, nothing below 8.8.

**Sheets.** Master: rope mid grey with a twist suggested by alternating single texels along
the top row of the front and flank plates (`pixels`, light-dark-light), knot a step lighter with
a bright loop, tassel cord mid, tuft `[top, bottom]` darker toward the bottom with a bright
top row as the binding. Inlay mask: every face, the same values, including the twist pixels.

**Recipe.** Centre item `minecraft:bamboo` (a flat item, unused by any template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py cord`
and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons paragraph below
filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-03 in 23 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`armorpieces_part`, 1 `list_outline`, 2 `remove_element` (starter cube, then its bone), 3
`add_group`, 3 `place_cube`, 1 `armorpieces_set_part`, **4 `armorpieces_paint`**, 2
`armorpieces_check`, 3 `set_camera_angle`, 1 `armorpieces_save`. No `risky_eval`, no
`modify_cube` at all, nothing hand-edited, and the save went through first time without `force`.
`check_part.py cord` and `check_authoring.py` were clean on the first run afterwards.

**What I built.** Three bones, eight cubes, one rotation. `rope` (pivot 0, 12.75, 0): four
0.5-square plates at Blockbench y 12.5..13.0 closing the ring exactly as briefed - `rope_front`
x -5.6..5.6 z -3.6..-3.1, `rope_back` the mirror at z 3.1..3.6, `rope_right` x 5.1..5.6 and
`rope_left` x -5.6..-5.1 both running the full z -3.6..3.6 so the corners double up. `knot`
(pivot -1, 12.75, -3.65): `knot_body` 1.4 x 1.1 x 0.9 at x -1.7..-0.3, y 12.2..13.3,
z -4.1..-3.2, and `knot_loop` 0.5 cubed at z -4.55..-4.05 - lapped 0.05 *into* the knot's front
face rather than flush on it, so no two cubes of the part share a plane either. `tassel` (pivot
-1, 12.2, -3.65, rotated +4 deg about X): `tassel_cord` 0.4 square from y 10.05 to 12.3 and
`tassel_tuft` 0.9 x 1.3 x 0.8 at y 8.85..10.15. Envelope x +-5.60, Blockbench y 8.83..13.30,
z -4.55..3.60; reach 6.83; `all clear by more than half a unit` from every other part on the
body bone - not one clash or near-miss note in the whole run.

**The rotated bone landed where the arithmetic said, to the hundredth, and the arithmetic is
what set the tassel's floor.** The brief's "nothing below 8.8" is a constraint on the *rotated*
envelope, not on `from`. For a +4 deg X rotation the plugin uses y' = y cos t - z sin t,
z' = y sin t + z cos t on the offset from the pivot, so the tuft's deepest corner is its
*back*-bottom one (z offset +0.4, which the rotation pushes further down): at the brief's
y 8.8 that corner lands at 8.78, two hundredths under the floor. Raising the whole tassel by
0.05 (cord 10.05..12.3, tuft 8.85..10.15, same 0.1 laps at both joints) put it at 8.83. Confirm
the sign the same way the brief says: below the pivot, +X swings toward -Z, and the check's
envelope came back z -4.55..3.60 with the tuft front at -4.29, exactly as computed.

**One texel per unit is the real constraint on a rope, and it bites twice.** A 0.5-unit section
is a **one-texel** face, so every "top row" the brief asks for is the *whole* face: the front
plate's outward face is 12x1 and the flanks' are 8x1. That is fine for the twist - twelve
alternating texels along a single row is precisely a laid cord, and it is the one thing on this
part that reads at three metres - but it means `[top, bottom]` is meaningless anywhere on the
rope, so the ring's lighting is done entirely with per-face flats (outward 158/160, `up`
185..190, `down` 95..100, buried inward faces 70). The second bite is the tuft: it is 1.3 tall,
i.e. **two** rows, and the brief wants both a `[top, bottom]` ramp and a bright binding row -
the binding pixel eats the top row, so the "ramp" is only ever binding-plus-one-value. I ended
up steering that one value by eye (see below) instead of pretending to a gradient.

**Three master calls, and why it was not one.** Call 1 was the whole part: a `*.*` base of 150,
then all 48 faces by name, plus 60 `pixels` - the twist, alternating 195/120 along the front
plate's north row and both flanks' outward rows, and 150/210 phase-shifted by one along the four
`up` rows so the highlight walks diagonally around the ring - and the tuft's four binding texels.
Calls 2 and 3 were the tassel only, after screenshots: at the brief's literal reading the tuft's
lower row at 110 rendered nearly black against the belt (the preview ramp is steep below ~130,
as pouch_belt found), so it went 110 -> 138 -> 152, and the cord went one step up as well
(north 155 -> 175). **Both repaints re-sent the four binding pixels**, because a face repaint
covers the texels laid under it - the same trap pouch_belt names, and it applies to a two-call
touch-up just as much as to a `*.*` base. Call 4 was the inlay mask: a silk cord takes the dye
entire, so it is the master's map copied verbatim, all 48 faces and all 60 pixels, one call.
Pillow confirms both sheets 214 opaque texels spanning 70..240, zero coloured pixels on either,
zero mask texels outside the master's silhouette. What the painter did **not** cover: there is
no painted knot-over-knot weave (the knot is one box and reads as a box), no seam where the four
plates double up at the corners, no fray at the tuft's tip, and the back half of the ring has no
twist at all - it is a flat 150 with a lit top, because nothing behind the wearer is worth 24
more texels of pixel list.

**The `!`s I accepted: none.** The only `!` that ever stood was the running unpainted-face count,
cleared by the first master call, and the save needed no `force`. Nor did I have a single
coplanar or clash note to weigh: putting the rope at y 12.5..13.0 keeps it off the body's y = 12
plane, every face is past x +-5 or z +-3 as the brief laid out, and the knot's inner face at
z -3.2 sits 0.1 *inside* the front plate's slab rather than on its z = -3.1 surface. Cheap and
worth copying: pick the numbers so the check has nothing to say.

**For the next part.**
- Eight cubes, the widest 11.2 units, fit a 64x32 sheet using rows 0..8 only - a `belt` ring
  costs almost nothing in sheet space because 0.5-thick plates are one-texel strips.
- `minecraft:bamboo` is a flat item and was free: `armorpieces_set_part` wrote the data, the
  `part_inlay` sheet and the recipe together, the save installed both PNGs, `--offline` warned
  once that bamboo was uncached, and one plain `python -m modpage build` fetched the icon and
  reported all three pages `unchanged`. Same sequence as girdle, pouch_belt and carapace.
- The arm box (`|x| > 4`, `-2 < z < 2`, `y > 12`, invisible, and the check never mentions it)
  cost nothing here: the ring crosses front and back so its flanks may hide inside the arms, and
  the knot and tassel are at z < -3.2, well clear. Any `belt` part with a *hanger* still has to
  keep it forward of z = -2 or it disappears.
- The tassel occupies the gap in front of the crotch, x -1.45..-0.55, z -3.25..-4.29, from
  Blockbench y 13.3 down to 8.83 - the lowest anything on this socket has gone. A future belt
  part with a second hanger should take the other hip, not the centre line.
