# Brief: Talons

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, with the tooling
as the Antennae and Horsetail sessions had it. From the `spurs` row of
`docs/plans/part-variety.md`:

> **Talons** - A backward-pointing bird claw off the heel. Theme: Beast. Fittings: none.

The plan lists no fitting; this brief gives the metal heel cap that mounts the claw a `guard`
mask, the way the horsetail's tube stays metal while its hair takes the dye, so the part is not
the only one in the batch without a fitting. The claw itself stays plain horn.

**Part.** `armorpieces:talons`, socket `spurs` only, in the mod's own pack. Display name
"Talons". Fittings: `armorpieces:guard`, one mask, covering the heel cap only. No effects, no
loot, no static layer.

**Shape.** `spurs` is a mirrored socket on the leg bone: model ONE leg, the left, and the game
mirrors it. In this rig the left leg is on the NEGATIVE x side in Blockbench: the leg box is
x -3.9..0.1, y 0..12, z -2..2 (pivot x -1.9, y 12), and the heel anchor is at Blockbench
(-1.9, 2, 2), on the back face. The reference shells are that box inflated 0.4 (leggings) and
0.9 (boots), so the back of the ankle's boot is at z 2.9 and anything with z under 2.9 is
buried; sit faces a tenth off a shell plane, never on it. The knee_studs session measured all
of this with one read-only `risky_eval` over `Cube.all` (names `left_leg`, `left_leg_leggings`,
`left_leg_boots`) - the one use of eval that is worth it, since no tool reports the shells. Read
the envelopes of spurs, heel_wings and streamers in the `armorpieces_new` reply first. Build a
heel cap: one cube across the back of the ankle, x -3.4..-0.4, y 1..3.5, z 3..3.75, its own
bone. From the middle of the cap a single claw sweeps backward and curls down toward the
ground: a chain of three bones under the cap bone, each with one cube modelled straight back
along +Z from its pivot and each rotated a little further than the last about X so the tip
curls down (the same arithmetic as the horsetail's tail: pivot plus length times cos and sin
of the cumulative angle), 1.25 / 1.0 / 0.75 units square in section, 2.5 / 2 / 1.75 long, each
overlapping its parent's end by a quarter unit. Aim the tip to end about z 7 to 8 and just
above y 0 - it may hang to the ground but not below it, and it must not reach inside the other
leg's space (x stays within -3.9..0.1). The whole claw is horn, so nothing here should share a
plane with the spurs' yoke or the heel wings; the check never compares same-socket parts, so
read their envelopes and keep the claw a quarter unit off their faces where it can. Note the
check prints the OPEN piece's envelope bone-local (+Y down, x mirrored: bone_y = 12 - bb_y,
bone_x = -bb_x - 1.9 on left_leg); the `past boots` numbers are the honest gauge.

**Sheets.** Master: the cap mid-grey with a lighter top row as its rim; the claw dark at the root
running to a light tip, `[top, bottom]` per segment so each is lighter than the last, a single
bright texel at the very tip. Guard mask: the cap's faces only, flat grey.

**Recipe.** Centre item `minecraft:flint` (a flat item, unused by any template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py talons`
and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons paragraph below
filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-03 in 21 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`list_outline`, 4 `add_group`, 4 `place_cube`, 2 `remove_element` (starter cube, then its bone),
1 `armorpieces_check`, 1 `armorpieces_part`, 1 `armorpieces_set_part`, 2 `armorpieces_paint`,
2 `set_camera_angle`, 1 `armorpieces_save`. **No `risky_eval`** - the brief's rig numbers
(leg box x -3.9..0.1, y 0..12, z -2..2, shells inflated 0.4 and 0.9, boots' back plane z 2.9)
were enough, so the knee_studs eval never had to be repeated. No `modify_cube`, no nudging, and
the save went through first time without `force`.

**What I built.** A `cap` bone at the heel anchor (Blockbench -1.9, 2, 2) carrying one cube
`heel_cap` x -3.4..-0.4, y 1..3.5, z 3..3.75 - its north face a tenth clear of the boots shell
at z 2.9 - and under it a three-bone chain, each bone's cube modelled straight back along +Z
from its own pivot: `claw_root` (+8 X) cube 1.25 square x 2.25 long from z 3.5, `claw_mid`
(+22, cumulative 30) 1.0 square x 1.75 from z 5.5, `claw_tip` (+32, cumulative 62) 0.75 square
x 1.5 from z 7.0, each starting 0.25 before its parent's end. The tip's axis lands at Blockbench
y 0.40, z 7.48, its lowest corner at y 0.22 - hanging to the ground, not through it - and the
whole part spans x -3.4..-0.4, inside the leg's -3.9..0.1.

**The brief's segment lengths do not fit and the arithmetic says so before you place anything.**
2.5 / 2 / 1.75 with quarter-unit overlaps is a 5.75-unit path. From a root at y 2.5-2.75 the
drop budget to "just above y 0" is about 2.2, and z 3.5 -> 7.5 is 4.0 of horizontal: a chord of
sqrt(4.0^2 + 2.2^2) = 4.6. A monotone curl cannot waste 1.15 units of length without either
lifting the first segment above horizontal (an S, not a sweep) or dropping through the floor -
every angle triple I tried put the tip either below y 0 or past z 8.3. Trimming to
**2.25 / 1.75 / 1.5** (path 5.0) makes 8/30/62 degrees land exactly on target. Rule of thumb for
anything hanging off the ankle: the usable drop is ~2.5 units, so the chain's total length must
stay under about 1.15x the straight line from root to tip.

**Rotation sign and the chain formula.** For a segment modelled along **+Z**, a positive X
rotation curls it **down**: end = pivot + L x (0, -sin θ, cos θ) with θ the cumulative angle
(the horsetail's upright segments used +cos/+sin because their local axis was +Y). Child bone
origins are placed in the *unrotated* pose, parent's pivot + (0, 0, L - 0.25); the check's
bone-local positions confirmed all three to a hundredth (`claw_mid at (0, 9.53, 5.48)` =
Blockbench y 2.47, z 5.48 against a predicted 2.4717 / 5.4805). `bone_y = 12 - bb_y` on the leg,
as knee_studs recorded.

**`!` lines accepted: none.** The finished check reports zero problems and zero notes; the nine
other-socket parts on `left_leg` are "all clear by more than half a unit", because the back of
the ankle above z 3 is empty - every greaves/knees/tassets part lives at z -4.7..+1.0 (only
`pelt` reaches z 2.98, and it is 7 units higher). Same-socket parts are never compared and never
worn together, but for the record the claw's bounding box does lap `spurs` (x -5.75..-1.50,
z 1.50..9.76) and `streamers` (y 0.28..3.55, z 0.85..7.98) as volumes; no face plane of mine
(x -3.4/-0.4, y 1/3.5, z 3/3.75 and the rotated claw) coincides with any of their envelope
planes, and the claw keeps 0.375 clear of `heel_wings`'s inboard face at x -2.90.

**Paint: two calls, 24 master faces + 1 pixel and 12 mask faces, nothing left over.** Master:
`*.*` 150 as the cap's mid-grey, then per-face pairs on the cap (up 210 as the rim, south
[195,135], sides [180,125]/[170,118], north 118, down 92) and a per-cube base for each claw
segment (95 -> 140 -> 200) with `[top, bottom]` pairs inside each, plus a 255 texel on
`claw_tip_seg.south` - the 1x1 end cap *is* the "single bright texel at the tip". What the
painter did not cover: the direction of a `[top, bottom]` pair on the **up/down** faces of a
segment modelled along Z is not stated anywhere the bridge prints (for those faces the UV
vertical is Z, and box UV flips the down face), so the within-segment gradients were kept to
~30 values and the real dark-root-to-light-tip story is carried by the per-segment step, which
is unambiguous. It also cannot paint anything defined against a neighbouring face - the cap's
"rim" is simply its whole 3x1 up face.

**The guard mask is shaded, not flat.** The brief asked for flat grey on the cap; the mask
instead mirrors the master's six cap values, for the reason knee_studs gave - the mask is the
cap's position on the guard material's ramp, so a flat mask flattens the cap's lit top edge
whenever a guard is fitted. Every shipped mask in the pack does the same.

**Recipe.** `minecraft:flint` in a paper ring: a flat item, unused by any other `template_*`
(checked with one grep before setting it), so no hand-drawn icon was needed. As with
`raw_iron`, `python -m modpage build --offline` warned `no texture for minecraft:flint`; one
plain `python -m modpage build` cached it and the second offline build is clean. Taken centre
items now include `flint`.

**For the next part.** Seven other tabs were open (nasal with unsaved edits among them) and
`armorpieces_new` made talons active without touching them. On `spurs` the space behind the
ankle from z 3 outward is completely free of the other sockets - it is the one leg socket where
you can build without lapping anything - but it is shared with three long same-socket parts, so
plan against their envelopes rather than against the clash lines, which will stay silent.
