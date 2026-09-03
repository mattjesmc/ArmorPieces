# Brief: Knee Studs

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, with the tooling
as the Antennae and Horsetail sessions had it. From the `knees` row of
`docs/plans/part-variety.md`:

> **Knee Studs** - Three rivets in a triangle, barely proud of the leg. The safest possible
> geometry. Theme: Knightly. Fitting: `guard`.

**Part.** `armorpieces:knee_studs`, socket `knees` only, in the mod's own pack. Display name
"Knee Studs". Fittings: `armorpieces:guard`, one mask, covering all three studs. No effects, no
loot, no static layer.

**Shape.** `knees` is a mirrored socket on the leg bone: model ONE leg, the left, and the game
mirrors it. In Blockbench the left leg box is x 0..4, y 0..12, z -2..2, and the knee anchor is
at y 6 on its front face (z -2). Two shells cover the leg: the leggings' half a unit out (front
at z -2.5) and the boots' a full unit out (front at z -3), so the studs must sit proud of z -3
or they are buried in the boots. This is the tightest socket in the mod: the tassets parts
above and the greaves parts below leave well under a unit of free height on the front of the
leg. Read the envelopes in the `armorpieces_new` reply (same socket first, then the tassets and
greaves parts that share the bone), then place three studs in a triangle - one up, two down, or
the reverse - each a 1x1 cube half a unit deep, faces at z -3 to -3.5, centred about x 2 and
spread no wider than x 0.75..3.25. Fit them in the free window if it holds a whole texel;
otherwise lap the tassets' lowest lame by a fraction the way Garters do, and say by how much.
Every stud is its own bone, no rotation needed. Plain planes shared with another part on the
bone are the one thing to avoid: offset by a quarter unit rather than sharing a face.

**Sheets.** Master: each stud a bright dome - lighter top face, mid sides, a dark bottom face,
one bright specular texel on the front face. Guard mask: all stud faces, flat grey.

**Recipe.** Centre item `minecraft:raw_iron` (a flat item, unused by any template - a copper
ingot in a paper ring is already the guard fitting's template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
knee_studs` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not
cover, and give the free y window you measured.

## Lessons from the session

**Built.** Three 1x1x0.5 studs, one bone each (`stud_top`, `stud_left`, `stud_right`, no
rotation), in a point-up triangle on the front of the left leg. Blockbench boxes: top
`(-2.4, 5.10, -3.5)..(-1.4, 6.10, -3.0)`, left `(-3.15, 3.90, ...)..(-2.15, 4.90, ...)`, right
`(-1.65, 3.90, ...)..(-0.65, 4.90, ...)`; all three z -3.5..-3.0, span x -3.15..-0.65 (2.5 wide,
centred on the leg), rows 0.2 apart. Data: `knees` only, fitting `armorpieces:guard`, no
effects/loot/static, recipe `minecraft:raw_iron` in a paper ring. Saved without `force`;
`check_part.py knee_studs` and `check_authoring.py` clean; page rebuilt (the first
`--offline` build warned that `minecraft:raw_iron` had no cached texture, so a plain
`python -m modpage build` was run once after it - now cached).

**The brief's leg numbers are in the wrong frame.** The brief says "the left leg box is
x 0..4 ... front at z -2.5 (leggings) / -3 (boots)". In this rig the left leg in Blockbench is
**x -3.9..0.1**, y 0..12, z -2..2; the shells are the same box inflated **0.4** (leggings) and
**0.9** (boots), so the boots' front plane is **z -2.9**, not -3.0. Modelling to the brief's
z -3.0 back face therefore leaves 0.1 of clearance rather than sitting on the shell - which is
what you want, but a part authored at z -2.9 would have z-fought. Convert the brief's x with
`bb_x = brief_x - 3.9`, so its "x 0.75..3.25" is `-3.15..-0.65`.

**Which frame the check prints.** For *other* parts the check prints both frames. For the *open*
piece the `envelope` / `at (...)` lines are **bone-local (+Y down, x mirrored)**, not Blockbench:
`bone_y = 12 - bb_y`, `bone_x = -bb_x - 1.9` on `left_leg`. Do not place cubes off those numbers.
`past boots z +0.60` etc. are measured against the inflated shell, so they are the honest gauge.

**The free window, measured.** Between the tallest greaves-socket part and the lowest
tassets-socket part on the front of the leg there is **0.38 units** of clear height: Blockbench
y **4.80** (top of `greaves:greaves`'s `greave`) to **5.18** (bottom of `tassets:tassets`'s
`lame3`). The cube-level `near:` lines confirm it to the hundredth (`stud_top clears greave by
0.30 in y`, `stud_left clears lame3 by 0.28 in y`). 0.38 does not hold one texel, let alone a
2.1-unit triangle, so the triangle was centred on the window's midpoint (y 4.99) and laps both
neighbours roughly equally: **0.92 into the tassets' lowest lame** (top stud, and only 0.55 of x
of it) and **0.90 into the greaves shells** (bottom studs). Garters and Poleyns lap by more
(Garters 1.0/1.67), so this is the socket's normal.

**`!` lines accepted: none.** The saved part reports 17 notes and zero problems. The nine
`OVERLAP` lines (into `scale_shins`'s `band`/`row1`, `puttees`'s `wrap1`, `greaves`'s `greave`,
`tassets`'s `lame3`) are `-` notes and unavoidable here: every greaves and tassets part on this
bone reaches z -3.65..-4.68, i.e. further out than studs that are meant to be "barely proud",
so a shin plate simply covers them. No shared plane was reported - z -3.0/-3.5 collides with no
neighbour's face plane, and 0.1 in front of the boots shell is enough to keep the check quiet.

**Paint: two calls, 18 faces each time, nothing left over.** One `armorpieces_paint` on `part`
and one on `part_guard`, both `{"*.*": 150, "*.up": 205, "*.east": 168, "*.west": 132,
"*.south": 105, "*.down": 78, "*.north": 235}` - wildcards cover all three studs at once, and
object key order is the paint order, so the base goes down first. Every face of a 1x1x0.5 cube
is exactly **one texel** (the 0.5-deep sides round up to 1x1), so the brief's "one bright
specular texel on the front face" *is* the whole north face: 235 on north, 205 up, 78 down,
168/132 on the sides for a little sideways form. The painter covered every face; it did not and
could not do any within-face gradient - `[top, bottom]` pairs are pointless on a 1-texel face.
The guard mask was shaded identically rather than the brief's "flat grey": every shipped mask
(`scale_shins_guard` mirrors `scale_shins` value for value) carries the same shading as the
master, and a flat mask would have flattened the domes whenever a guard is fitted.

**For the next part.** Read the leg/arm box out of the rig rather than out of the brief (one
read-only `risky_eval` over `Cube.all` gives `from`/`to`/`inflate` of the reference shells in
Blockbench coordinates in one shot, and there is no tool for it). On any leg socket assume the
front is full: only 0.38 units are actually free between greaves and tassets, so plan to lap and
say by how much rather than trying to fit. Sub-unit cubes still get 1x1 texel faces, so a small
part's whole look is the six greys you choose. `minecraft:raw_iron` is now taken as a template
centre item; `minecraft:copper_ingot` is the guard fitting's.
