# Brief: Ruff

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the tenth
batch of four (read scarf.md first - same socket, and its finding that anything inside x ±4,
z > -4 above y 24 is inside the player's head and never seen - then girdle.md for a ring of
plates). From the `collar` row of `docs/plans/part-variety.md`:

> **Ruff** - A pleated cloth collar standing around the neck. Theme: Court. Fitting: `inlay`.

**Part.** `armorpieces:ruff`, socket `collar` only, in the mod's own pack. Display name "Ruff".
Fittings: `armorpieces:inlay`, one mask, covering the whole ruff. No effects, no loot, no
static layer.

**Shape.** `collar` is not a mirrored socket: model the whole thing on the body bone. The torso
box is x -4..4, y 12..24, z -2..2 (pivot 0, 24, 0); the chestplate shell is that box inflated a
full unit, x -5..5, y 11..25, z -3..3, and the anchor is at Blockbench (0, 23, -2). Above the
chestplate sits the HEAD: its box is x -4..4, y 24..32, z -4..4 and its helmet shell x -5..5,
y 23..33, z -5..5, on another bone, so the check never mentions it - anything inside that shell
is invisible when a helmet is worn, and the head turns, so its corners sweep a circle of radius
7.07 about the neck. A standing ruff therefore lives OUTSIDE the helmet shell and just outside
the sweep where it can: a square ring of four plates 0.4 thick at x ±5.1..±5.5 and z ±5.1..±5.5
(its inner corners at radius 7.2 clear the sweep, and a plate's flat middle at 5.1 is grazed by
the helmet's own face at 5.0 by 0.1 - a tenth off a plane), standing from y 25.1 (a tenth above
the chestplate's top) to y 26.5. Build a `ring` bone at (0, 25.1, 0) with those four plates
(each the full span so the corners double up); then the pleats: eight `pleat_*` bones, each a
pleat block 0.7 wide along the plate, 1.4 tall (y 25.1..26.5), 0.3 proud of the ring's OUTER
face (a twentieth into the plate), two per side at the quarter points (x ±2.75 on the front and
back plates, z ±2.75 on the flanks), every pleat bone rotated 15 degrees about the vertical
axis (Y) so the blocks sit askew like folded lace. Read the envelopes in the `armorpieces_new`
reply: the back parts share the bone and carapace's top lame reaches y 24.6, bedroll's roll to
24.85 and its knots to 24.95, spine_ridge's top plate to 24.8, pinions' bracket, so the ring's
back plate at y 25.1 clears them by 0.15 or more; dodge every listed plane by a twentieth. The
gorget (same socket, never compared) shows the socket already reaches y 25.25. Nothing above
y 26.6.

**Sheets.** Master: ring light `[top, bottom]` brighter at the top edge with a darker bottom
row (`pixels`); pleats brighter still on their outward faces with dark side faces so each fold
reads; top faces brightest. Inlay mask: every face at the same values.

**Recipe.** Centre item `minecraft:light_gray_wool` (a block with a flat texture, unused by any
template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py ruff`
and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons paragraph below
filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-03 in 36 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`armorpieces_part`, 1 `list_outline`, 9 `add_group`, 9 `place_cube`, 2 `remove_element` (the
starter cube, then its `main` bone), 3 `armorpieces_check`, 1 `armorpieces_set_part`, **4
`armorpieces_paint`**, 3 `set_camera_angle`, 1 `armorpieces_save`. No `risky_eval`, no
`modify_cube` (every box landed right first time), nothing hand-edited, and the save went
through **without `force`**.

**What I built.** Twelve cubes in nine bones. `ring` (pivot 0, 25.1, 0) carries four plates
0.4 thick standing y 25.1..26.5: `ring_front` x -5.35..5.35 z -5.5..-5.1, `ring_back` the same
box at z 5.1..5.5, `ring_left` x -5.5..-5.1 and `ring_right` x 5.1..5.5, both z -5.45..5.45 and
y 25.15..26.45. Eight `pleat_*` bones, each pivoted on the plate's outer face at the quarter
points (x ±2.75 front and back, z ±2.75 on the flanks, y 25.15) and rotated **+15° about Y**,
each holding one `fold_*` block 0.7 along the plate, 0.35 thick (0.05 into the plate, 0.3
proud), y 25.15..26.55. Envelope (Blockbench) x ±5.88, y 25.10..26.55, z ±5.88; reach 9.88,
`past chestplate x+0.88 y+1.55 z+2.88` - the widest and the highest `collar` part so far, and
the socket's first that closes a full square ring above the shoulders.

**The brief's numbers held; the two I changed were both the scarf session's shared-plane trap.**
A ring whose four plates all span the full width and all share y 25.1..26.5 gives coincident
*exterior* faces at every corner (the front plate's end face at x = -5.5 lying exactly on the
flank's outer face at x = -5.5, same direction, same depth). Fix, as scarf found: let the flanks
own the outer x planes (±5.5) and stop the front/back plates 0.15 short at x ±5.35 so their end
faces die inside the flank slab; then take 0.05 off the flanks' top and bottom (25.15..26.45) and
stop them at z ±5.45 inside the front/back slabs. Every overlapping corner face is then strictly
buried and the check came back with zero `!` from the geometry. Same reasoning put the pleats at
y 25.15..26.55 rather than the briefed 25.1..26.5: sharing the ring's top and bottom planes would
have been eight more coincident pairs, and 0.05 of overhang at each end also makes the folds read
as standing proud of the band. Top is 26.55, inside the brief's 26.6 ceiling.

**`!` lines accepted: none.** The only `!` the session ever showed was the standing "faces have
no paint behind them" count, cleared by the first two paint calls. The final check is `ok:
nothing needs a decision` with 12 `-` notes, every one of them a *clearance*, not an overlap:
`ring`/`pleat_b*`/`pleat_l2`/`pleat_r2` clear `bedroll:back`'s roll and straps by 0.30..0.45 and
`spine_ridge:back`'s plate_1 by 0.30/0.39. The brief's y 25.1 floor is exactly what buys those:
the back parts top out at Blockbench 24.6 (carapace), 24.8 (spine_ridge) and 24.85 (bedroll), so
a ring starting a tenth above the chestplate shell clears the tallest of them by 0.25.

**The head, again.** No `!` will ever tell you about it - the check only measures the body bone -
but the geometry the brief handed me is right: at x/z ±5.1 the ring stands a tenth outside the
helmet shell (±5), so nothing is swallowed, and the inner corners at radius 7.21 clear the
helmet corner's sweep (7.07). What that sweep does *not* clear is the flat middle of each plate
at 5.1: turn the head 45° and a helmet's corner passes outside it. That is unavoidable for any
square standing collar and is the same compromise `gorget` already ships with, so I left it.

**Four paint calls, two per sheet, and they covered every face.** Call 1 (master) and call 2
(`part_inlay`) each painted 152 face entries - `*.*` 118 as the base, `*.up` 212, `*.down` 78,
then ring outward faces `[190, 150]`, inner 92, end caps `[162, 122]`; pleat outward `[232, 182]`,
pleat side faces 126 (dark, so each fold reads as a separate tab), pleat inner 100, pleat tops 245
- plus 44 `pixels` for the shadow row along the bottom of the four outward faces. Calls 3 and 4
were only those 44 pixels again, one sheet each: at 72 the row read as a near-black stripe on a
face that is only two texels tall, which at 1/16 block turns the whole ruff into a dark band with
a bright lip. 108 keeps it a light starched collar with a shadow under the rim. **On a 1.4-unit
face you have two rows and no more: a `[top, bottom]` pair plus a `pixels` row is not a gradient
plus an accent, it is simply "top value, pixel value", so pick the pair as if the bottom half did
not exist.** The mask repeats the master exactly, so the whole ruff takes the dye. Saved sheets:
360 opaque texels each, 12 distinct greys, span 78..245, pure greyscale, a 64x32 sheet about a
fifth full. What the painter still did not do: nothing here needed it - no seam between plates,
no per-texel lace, and a rotated cube's faces paint by name exactly like an axis-aligned one.

**For the next part.** `minecraft:light_gray_wool` is now taken as a template centre, and the
three-step dance is still the rule for a never-cached item: `--offline` warned *"no texture for
1 item(s) ... drawn as missing-texture"*, one plain `python -m modpage build` fetched it, the
third build reported `unchanged`. Eight `add_group` calls and eight `place_cube` calls can be
issued in a single message each when they do not depend on each other - the bridge answered all
sixteen without complaint and the compact check line after the last one already read
`past chestplate x+0.88`, matching the pen-and-paper rotation to the hundredth (a 0.7x0.35 block
turned 15° about a pivot on its inner face reaches 0.35·sin15 + 0.30·cos15 = 0.38 outward). And
name the cubes differently from their bones (`fold_f1` in `pleat_f1`): `armorpieces_paint`
addresses cubes by name, and a name shared with a group is asking for the wrong element.
