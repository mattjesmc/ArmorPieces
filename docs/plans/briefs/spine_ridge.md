# Brief: Spine Ridge

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the fifth
batch of four, a Beast set (skim carapace.md and bedroll.md for the back frame and the
belt-line neighbours, dorsal_fin.md for a fan of plates). From the `back` row of
`docs/plans/part-variety.md`:

> **Spine Ridge** - A row of dorsal plates stepping down the spine, tallest at the shoulders.
> Theme: Tidal / Beast. Fitting: `guard`.

**Part.** `armorpieces:spine_ridge`, socket `back` only, in the mod's own pack. Display name
"Spine Ridge". Fittings: `armorpieces:guard`, one mask, covering every plate. No effects, no
loot, no static layer.

**Shape.** `back` is not a mirrored socket: model the whole thing on the midline x = 0, on the
body bone. The torso box is x -4..4, y 12..24, z -2..2 (pivot 0, 24, 0); the chestplate shell is
that box inflated a full unit, x -5..5, y 11..25, z -3..3, and the anchor is at Blockbench
(0, 22, 2). Anything with z under 3 is buried. Read the envelopes in the `armorpieces_new`
reply: the same-socket parts are never compared; the belt parts share the bone and top out at
y 15.5 (buckled_belt, z to 3.5) and 14.25 (girdle), so the lowest plate stays above y 15.7.
Build five plates down the spine, each its own bone pivoted on the shell's back plane at
(0, y_k, 3) and rotated about X so the plates sweep UP and back (a plate modelled along +Z
from its pivot tips DOWN under a positive X rotation - talons - so use NEGATIVE X, about -25
degrees on the top plate easing to -10 on the bottom one). Each plate is two cubes in its bone,
modelled along +Z in the unrotated pose: a base 0.7 wide (x), h tall, d long, then a tip half
the width and half the height stacked on the base's far end; from the shoulders down:
y_k = 23.6 / 21.6 / 19.6 / 17.7 / 16.1, base sizes (h x d) 1.6x2.4 / 1.5x2.2 / 1.3x1.9 /
1.1x1.5 / 0.9x1.1, every cube starting at z 3.1 in its own bone. Nothing above y 25 after
rotation (check the top plate's tip: pivot y plus d times sin 25 plus h - if it crosses 25,
shorten it), nothing below y 15.7, nothing wider than x ±0.35 on bases and ±0.2 on tips.

**Sheets.** Master: plates mid-light `[top, bottom]` lighter toward the tip, the bases a step
darker than the tips, each plate's leading (up) face brightest, the down faces dark. Guard
mask: every plate face, the same shading.

**Recipe.** Centre item `minecraft:pufferfish` (a flat item, unused by any template), paper
ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
spine_ridge` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

Built 2026-09-03 in 24 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 5 `add_group`,
5 `place_cube`, 1 `list_outline`, 2 `remove_element` (starter cube, then its bone), 1
`armorpieces_part`, 1 `armorpieces_set_part`, **2 `armorpieces_paint`**, 2 `armorpieces_check`,
2 `set_camera_angle`, 1 `armorpieces_save`. No `risky_eval`, no `modify_cube`, nothing nudged,
nothing hand-edited, and the save went through first time without `force`.

**What I built.** Five bones under `part`, `plate_1`..`plate_5`, pivots on the chestplate's back
plane at Blockbench (0, 23.6/21.6/19.6/17.7/16.1, 3), rotated **-25 / -21 / -17 / -13.5 / -10**
about X so each blade sweeps up and back. Two cubes per bone, modelled along +Z in the unrotated
pose, all starting at z 3.1: a base 0.7 wide (x -0.35..0.35) and a tip 0.35 wide
(x -0.175..0.175) starting 0.25 before the base's far end, half the base's height, centred on the
base's mid-height. Bases (bb y, z): 22.20..23.80 / 3.1..5.4; 20.50..22.00 / 3.1..5.3;
18.60..19.90 / 3.1..5.0; 17.00..18.10 / 3.1..4.6; 15.75..16.65 / 3.1..4.2. Tips: 22.60..23.40 /
5.15..6.05; 20.875..21.625 / 5.05..5.85; 18.93..19.58 / 4.75..5.45; 17.28..17.83 / 4.35..4.95;
15.98..16.43 / 3.95..4.40. Envelope x ±0.35, bb y 15.77..24.80, z 2.95..6.19, reach 6.45, past
the chestplate z +3.19 and **y -0.20** - i.e. 0.2 *under* the shell's y 25 ceiling. Data: `back`
only, fitting `armorpieces:guard`, no effects, loot or static layer; recipe `minecraft:pufferfish`
in a paper ring.

**The brief's height formula is off by the plate's own placement, and it decides the whole part.**
"pivot y plus d times sin 25 plus h" reads as *cube from the pivot upward* (local y 0..h). That
placement cannot be built: at y_k 23.6 the headroom to 25 is 1.4, the 2.4-long plate spends
2.5·sin25 = 1.06 of it on lift alone, and the remaining 0.34 caps the plate at h ≤ 0.38 - a
razor blade, not a dorsal plate. Centring the cube on the pivot (local y ±h/2) still lands at
25.38. The fix that keeps every briefed h and d is to **hang each plate below its pivot line with
a small top offset u**: base local y = (u-h)..u, and then

    top    = y_k + u·cosφ + (0.1+d)·sinφ
    bottom = y_k + (u-h)·cosφ + 0.1·sinφ

with u = **0.2 / 0.4 / 0.3 / 0.4 / 0.55** from the shoulders down (and d1 trimmed 2.4 -> 2.3).
That gives tops 24.80 / 22.80 / 20.44 / 18.44 / 16.83 and bottoms 22.37 / 20.61 / 18.67 / 17.04 /
15.77: under the 25 ceiling, over the 15.7 floor, and every plate clears the one above it by
0.19..0.71 measured *along the plate above's bottom face at the lower plate's top corner z* (the
raw y ranges overlap - two plates at different z can share a y band without touching, so compare
in the plane, not in the envelope). u also sets how the root meets the back: at u 0.2 the near
face is a tilted edge from (y 22.37, z 3.68) to (y 23.82, z 3.01), so the blade grows out of the
armour instead of floating on it. Every predicted number came back from the check to the
hundredth on the first placement.

**`!` lines accepted: none.** The finished check is `ok: nothing needs a decision`. Two notes
stand, both deliberate:
- `OVERLAP: plate_5 into sash:belt's belt by 0.70 x 0.23 x 1.00` (with `near: clears ... by 0.15
  in y`). The brief derived the 15.7 floor from `buckled_belt` (top 15.5) and `girdle` (14.25),
  but **`sash` is the belt part that actually reaches up the back**: its second cube is a band
  x -5.5..5.5, bb y 13.5..16.5, z 1..4, so anything on the midline below y 16.5 and inside z 4
  laps it. Nothing can be done about it inside the brief's y_k 16.1 - lifting plate_5 clear of
  16.5 pushes its top through plate_4's root - and the lap is harmless: the plates are rotated,
  so no face of mine is axis-aligned in y or z and no plane can be shared, and the shipped
  `carapace` puts its lowest lame (bb y 15.60..16.70, z 3.10..4.05) in exactly the same volume.
  Read as "the bottom plate emerges from under the sash".
- plate_2's near-top corner sits at z 2.95, 0.05 *inside* the chestplate shell. Also deliberate:
  the root is hidden rather than hovering, and again there is no coplanarity to fight over.

**Paint: two calls, 60 master faces and 60 guard-mask faces, nothing left over.** Call 1 (master):
`"*.*" 170`, then `"*.up" 228 / "*.down" 95 / "*.north" 120 / "*.south" 160` for the whole part,
then a `[top, bottom]` pair per base side face (195/150 at the shoulders easing to 186/142 at the
tail) and a full six-face override per tip (sides 226/182 down to 218/174, up 246, down 115,
north 175, south 210). Call 2 repeated exactly those values on `part_guard` - a mask is the
part's position on the guard material's ramp, so a flat mask would flatten the lit top edges, as
knee_studs and talons recorded. **What the painter covered and did not.** The blade's readable
faces are `east`/`west` (base 1: 3x2 texels; plate 5: 2x1), and on them a `[top, bottom]` pair is
a *vertical* gradient in y - exactly the lit-top/dark-bottom story wanted. The brief's other axis,
"lighter toward the tip", is a gradient **along z on the same faces**, which `armorpieces_paint`
cannot express; it is carried instead by the base->tip cube step (~30 values), which is
unambiguous and reads at three metres. No `pixels` and no shape tool were needed: at 0.7 x 0.35
units nothing on this part is smaller than one face, and the "bright specular tip" is simply the
tip's 1x1 `south` end cap at 210.

**For the next part.**
- On the `body` bone, `sash` is the one belt part that occupies the back above y 15.5 (to 16.5,
  z 1..4) and `pouch_belt` reaches z 5.0 but stops at y 13.6. If a `back` part must come down to
  the belt line, plan to lap the sash or stay above y 16.6.
- A rotated bone is the cheapest clash insurance there is: with every cube tilted 10-25 degrees,
  the check never had a single COPLANAR line to report, on a bone shared with ten other parts.
- `minecraft:pufferfish` is now taken as a template centre item. Flat item, no icon work, but
  `python -m modpage build --offline` warned it had never been cached; one plain
  `python -m modpage build` fetched it and the repeat offline build is silent (README text
  unchanged by the online run, only the icon).
- Five other tabs were open (aerials, dorsal_fin, swim_fins, epaulettes, thigh_sheath,
  shin_spikes); `armorpieces_new` made spine_ridge active and none of them was touched.
