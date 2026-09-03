# Brief: Bangles

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the third
batch of four (skim the lessons in wing_cases.md for the arm frame and girdle.md for building a
ring out of plates). From the `vambraces` row of `docs/plans/part-variety.md`:

> **Bangles** - A stack of loose rings at each wrist. Theme: Court. Fitting: `gemstone`.

**Part.** `armorpieces:bangles`, socket `vambraces` only, in the mod's own pack. Display name
"Bangles". Fittings: `armorpieces:gemstone`, one mask, covering a single stone set in the
middle ring on the outside of the wrist. No effects, no loot, no static layer.

**Shape.** `vambraces` is a mirrored socket riding the arm: model ONE arm, the LEFT, which in
this rig is at NEGATIVE x. The arm box is x -8..-4, y 12..24, z -2..2 (pivot -5, 22, 0); the
chestplate's arm shell is that box inflated a full unit, x -9..-3, y 11..25, z -3..3, and the
anchor is at Blockbench (-6, 16, 0), the middle of the forearm. Anything inside the shell is
buried; sit faces a tenth off a shell plane, never on it. Read the envelopes in the
`armorpieces_new` reply: the pauldrons parts share the bone and come down to about y 14
(wing_cases' lower plate to y 14.07 at x -10.8..-9.2), so keep the rings below y 14 or say by
how much they lap; the wrist end of the arm is y 12, the shell's bottom is y 11. Build three
rings, each its own bone, each ring four plates a quarter unit thick closing a square around
the shell: outer plate at x -9.35..-9.1, inner at x -2.9..-2.65, front at z -3.35..-3.1, back at
z 3.1..3.35, each plate running the full width of the ring so the corners overlap by a quarter
unit (the girdle session's lesson: corner plates at 45 degrees do not work over a box, plain
overlapping plates do). Ring heights 0.5 each at y 11.4..11.9, 12.2..12.7, 13.0..13.5 - loose,
so they do not touch, and the middle one pushed a tenth further out on every side so the stack
is not a smooth column. The stone: a 0.75x0.75x0.5 cube on the middle ring's OUTER plate
(x -9.85..-9.35), centred at z 0, its own `stone` bone. Twelve plates and a stone: place them
one call per message and let each reply's check confirm the last.

**Sheets.** Master: rings bright metal `[top, bottom]` with a brighter top face and a dark
underside, the middle ring a step lighter than the outer two; the stone brightest with a dark
underside and one specular texel (`pixels`). Gemstone mask: the stone's faces only.

**Recipe.** Centre item `minecraft:golden_horse_armor` (a flat item, unused by any template),
paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py bangles`
and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons paragraph below
filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

Built 2026-09-03 in 20 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`list_outline`, 2 `remove_element` (starter cube, then its bone), 4 `add_group`, 4 `place_cube`,
1 `armorpieces_check`, 1 `armorpieces_set_part`, **2 `armorpieces_paint`**, 2 `set_camera_angle`,
1 `armorpieces_save`. No `risky_eval`, no `modify_cube`, no nudging, nothing hand-edited, and the
save went through first time without `force`.

**What I built.** Exactly the brief's numbers, unchanged - which is the headline: every plate
landed where the arithmetic said, so there was nothing to move. Four bones under `part`, none
rotated: `ring_low` (pivot -6, 11.65, 0), `ring_mid` (-6, 12.45, 0), `ring_top` (-6, 13.25, 0),
`stone` (-9.45, 12.45, 0). Each ring is four 0.25-thick plates closing a square around the
chestplate's arm shell (x -9..-3, z -3..3), every face sitting 0.1 off a shell plane: outer
x -9.35..-9.1, inner x -2.9..-2.65, front z -3.35..-3.1, back z 3.1..3.35, the outer/inner pair
running the full z span and the front/back pair the full x span so all four corners double up by
a quarter unit. `ring_mid` is the same square pushed 0.1 further out on all four sides
(-9.45..-9.2 / -2.8..-2.55 / z +-3.2..3.45), which is what stops the stack reading as a smooth
column. Ring heights y 11.4..11.9, 12.2..12.7, 13.0..13.5 - 0.3 of air between rings. `gem`,
0.5x0.75x0.75 at x -9.85..-9.35, y 12.075..12.825, z +-0.375, overlaps the middle ring's outer
plate by 0.1 and stands 0.4 proud of it. Envelope x -2.45..4.85 (bone-local), y 8.50..10.60,
z +-3.45; reach 6.60, the same reach the girdle got round the waist.

**The `!` I accepted: none.** The only `!` that ever stood was the standing unpainted-face count,
cleared by the two paint calls. What remained afterwards was one `-` note: *pair spans 19.70
across the figure, over the 18 the shoulders span* - unavoidable and shared with the shipped
`vambraces` (20.0), since the rings must clear the arm shell's x -9 plane on both arms. The check
reported no shell-plane contact, no shared plane, and `all clear by more than half a unit`
against the four pauldrons parts on the same bone: the rings top out at y 13.5 and the lowest
pauldron geometry (`wing_cases`) starts at y 14.07, so the brief's "keep the rings below y 14"
left 0.57 of daylight with no lapping to explain.

**The buried inner plate is deliberate and the check will not tell you.** The arm shell's inner
plane is x -3, but the *torso* box is x -4..4, so a ring plate at x -2.9..-2.65 is inside the
body/chestplate and its outer face is never seen from any angle. That is the price of a closed
ring over a boxy arm; the check counted its six faces as needing paint and said nothing about
them being invisible, so paint them dark (I used 70-138) rather than leaving them, or they render
as holes when the wearer has no chestplate on.

**Painting: two calls, one per sheet, and they covered everything** - 78 master faces and 6 on
`part_gemstone`, zero unpainted, no stray paint, no colour on a greyscale sheet. Pillow on the
saved sheets: master 366 opaque texels spanning 48..255, mask 6 texels 120..255, all grey. The
master call was one `*.*: 110` base, then each of the 13 cubes as `<cube>.*` plus its one
outward face as a `[top, bottom]` pair - `west` for the outer plates, `north` for the front
plate, `south` for the back plate, `east` for the buried inner plate - then a global `*.up: 205`
/ `*.down: 58` for the bright top and dark underside, then the middle ring's up/down bumped to
228/66 and every inner plate's darkened, then the gem last so the global wildcards could not
overwrite it. **Order is the whole technique: general first, specific after, and anything you
want to survive goes at the end of the object.**

What the painter did NOT cover, and could not: **a 0.5-unit-tall plate is exactly one texel
tall**, so a `[top, bottom]` pair on a ring's outward face collapses to a single row at the
`top` value - the ramp does nothing. All the visible modelling of these rings is silhouette and
the flat grey step between ring_mid (215) and the outer two (190); there is no room for a rim
row, a bevel, or anything the girdle session did with `pixels`. The same trap ate the specular:
the gem is 0.75 units, so **all six of its faces are 1x1 texels** and the brief's "one specular
texel" is simply the whole `west` face. I painted it as a `pixels` entry at 34,13 anyway (255)
so the intent is legible in the call, but `"gem.west": 255` would have been identical. Sub-unit
detail is a modelling decision in this format, never a painting one.

**For the next part.**
- `armorpieces_set_part` before painting still holds: it answered `sheets_created:
  [part_gemstone]` and the mask call worked immediately after.
- Thirteen cubes, twelve of them long thin plates, packed into the default 64x32 with room left
  (366 opaque texels); the plugin never had to grow the sheet. A plate 6.7 long and 0.25 thick
  unwraps to a 14x8 island - it is the LONG axis that costs sheet, not the count of cubes.
- `place_cube` takes an `elements` array, so a four-plate ring is one call and one undo step, and
  the reply prints all four cubes' face rectangles at once. One call per bone is the natural
  granularity for a repetitive part.
- `minecraft:golden_horse_armor` is a flat item and was free; `python -m modpage build --offline`
  warned it had never been cached, one plain `python -m modpage build` fetched it and reported
  all three pages `unchanged`.
- The 3D view is blank until the master has paint. Two `set_camera_angle` shots from outboard
  (-30, 22, 24) and (-34, 14, -14) were enough to confirm the three rings read as separate loose
  bands and the stone as a bump on the middle one.
