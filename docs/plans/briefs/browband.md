# Brief: Browband

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the ninth
batch of four (read laurel.md and cheek_guards.md first - same bone, the 1.6-unit corridor
between the cheek-guard rivet and the aerials boss, the horn bosses at the temples). From the
`brow` row of `docs/plans/part-variety.md`:

> **Browband** - A cloth wrap knotted at one temple with a short tail. The un-armoured brow.
> Theme: Wayfarer. Fitting: `inlay`.

**Part.** `armorpieces:browband`, socket `brow` only, in the mod's own pack. Display name
"Browband". Fittings: `armorpieces:inlay`, one mask, covering the whole band, knot and tail. No
effects, no loot, no static layer.

**Shape.** `brow` is not a mirrored socket: model the whole band on the head bone. The head box
is x -4..4, y 24..32, z -4..4 (pivot 0, 24, 0); the helmet shell is that box inflated a full
unit, x -5..5, y 23..33, z -5..5; the anchor is at Blockbench (0, 28, -4). Read the envelopes in
the `armorpieces_new` reply: the other brow parts are never compared; the horns parts share the
bone - cheek_guards' rivet at x -5.45..-4.65, y 28.6..29.4, z ±0.4 (and its mirror), the horn
bosses at x ±4.66..±5.6, y 29..31, aerials' boss from y 31 - so a band at y 28.9..30.1 laps
the rivet and the bosses (a wrap round the temples cannot avoid them; laurel accepted the same)
but must not share their planes: keep the flank plates at x ±5.15..±5.5, not ±5.45, and dodge
every listed plane by a twentieth. Build a `band` bone with a ring of four plates 0.35 thick and
1.2 tall at y 28.9..30.1 a tenth off the shell (front z -5.45..-5.1, back z 5.1..5.45, flanks
x ±5.15..±5.5, each the full span so the corners double up); a `knot` bone at the LEFT temple
(negative x) with a knot cube x -6.25..-5.5, y 28.95..30.05, z -0.9..0.1 (its inner face a
twentieth inside the flank plate's slab) and a small second lump 0.5 square on the knot's
front; and a `tail` bone pivoted at the knot's bottom (-5.9, 28.95, -0.4) carrying a tail
plate 0.6 wide (z), 0.3 thick (x), hanging from y 29.05 (lapping the knot by a tenth) to
y 26.6, the bone rotated about Z so the tail flares OUTBOARD at the bottom (for a cube below its
pivot on the negative-x side a NEGATIVE Z rotation swings the free end toward -x - cheek_guards
confirmed it) by 8 degrees, and 6 degrees about X so it trails back a little. The tail passes
outside cheek_guards' plate (x -5.5..-5.1) - keep its inner face at x -5.85 or further out.
Nothing below y 26.4, nothing above 30.1.

**Sheets.** Master: band mid grey with a fold line as a darker single row along the middle of
the front plate's outer face (`pixels`; the face is one row tall if the band is under 2 units,
so make the fold a darker texel every third column instead), knot a step lighter with a bright
top, tail `[top, bottom]` darker toward the tip with a bright bottom row as the fringe. Inlay
mask: every face at the same values.

**Recipe.** Centre item `minecraft:green_wool` (a block with a flat texture, unused by any
template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
browband` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-03 in 19 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`list_outline`, 3 `add_group`, 3 `place_cube`, 2 `remove_element` (starter cube, then its
`main` bone), 1 `armorpieces_check`, 1 `armorpieces_part`, 1 `armorpieces_set_part`,
**2 `armorpieces_paint`** (one per sheet), 2 `set_camera_angle`, 1 `armorpieces_save`. No
`risky_eval`, no `modify_cube`, no nudging, nothing hand-edited; the save went through first
time **without `force`**, and `check_part`, `check_authoring` and `modpage build` were clean.

**What I built.** A `band` bone (pivot 0, 29.5, 0, unrotated) with the brief's ring of four
0.35-thick plates at y 28.9..30.1: `band_front` z -5.45..-5.10 and `band_back` z 5.10..5.45,
both x ±5.5; `band_left` x -5.5..-5.15 and `band_right` x 5.15..5.5, both z ±5.45, so the
corners double up. A `knot` bone (child of `band`, pivot -5.8, 29.5, -0.4) with `knot_core`
and `knot_lump` x -6.05..-5.55, y 29.25..29.75, z -1.35..-0.85 (lapping the core's front by
0.05). A `tail` bone (child of `knot`, pivot -5.9, 28.95, -0.4) rotated **Z -8, X -6** carrying
`tail_plate` x -6.15..-5.85, y 26.6..29.05, z -0.7..-0.1. Envelope Blockbench x -6.48..5.50,
y 26.60..30.10, z -5.45..5.45; reach 11.13; nothing below 26.58 or above 30.10, as asked.

**Two numbers the brief left me to derive, both confirmed to a hundredth by the first reply.**
(a) The **X sign for "trails back"**: about X, (dy, dz) -> (dy cos - dz sin, dy sin + dz cos),
and the tail hangs *below* its pivot (dy negative), so a positive angle would swing the free end
toward **-z, i.e. forward, into the face**. Trailing back (+z) needs **X -6**, not +6. The Z sign
is cheek_guards' rule unchanged (negative Z, free end toward -x): predicted bottom outer corner
x = -5.9 + (-0.25 cos8 - 2.35 sin8) = -6.475, and the reply printed `past helmet x+1.48`.
(b) The **knot's inner face**. The brief's -5.5 is exactly `band_left`'s own outer plane - two
coincident faces of the same part, i.e. guaranteed z-fighting - and the obvious fix, a twentieth
inside at -5.45, lands exactly on `cheek_guards`' rivet plane x -5.45, which *is* a shared plane
with another part on the bone. I pushed it three times as far instead: `knot_core`
x -6.25..**-5.35**, 0.15 into the flank slab, 0.10 clear of the rivet plane and 0.20 clear of the
flank's inner face. Nothing on this part shares a plane with anything, and the check's
plane section is silent.

**`!` lines accepted: none** - the final check is `ok: nothing needs a decision`. It prints **19
OVERLAP notes and 21 near notes**, all `-`, and they are the same price laurel paid: a closed
ring at temple height on `brow` cannot miss the horn sockets' roots. `horns` and `helm_wings`
put a boss at x 4.66..5.6 / y 29..31, `head_fins` runs a whole sweep along the temple, and
`cheek_guards` rivets its hinge at exactly the band's height - so `band`, `knot` and `tail` all
pass through them. Every one is a horn root or a hinge passing *through a cloth wrap*, which is
what a wrap worn under horns does. The tightest near, `band clears horns' horn1 by 0.08 in y`,
is a gap. The one deliberate collision, `tail into cheek_guards' plate by 0.15`, is only the
hull test: the real cheek plate is tilted -6 degrees and at the tail's heights its outer face is
x -5.71..-5.75, while the tail's inner face runs -5.85 down to -6.18, so the two cubes never
actually meet - the brief's "inner face at x -5.85 or further out" is exactly right, and the
rotation only widens the gap.

**Two paint calls - master and `part_inlay` - 42 faces each (94 face writes: `*.*` 140, then a
`knot_core.*` / `knot_lump.*` base, then every face by name) plus 20 `pixels`, and they covered
everything**: 0 unpainted faces, no stray paint, 310 opaque texels 76..225 on each sheet,
greyscale confirmed with Pillow. **The 1.2-unit band rounds to TWO texel rows, not one**, so the
brief's fallback ("one row, so use a texel every third column") was half needed: the band's outer
faces are 11x2, which took a `[170, 130]` `[top, bottom]` grade, and I spent the pixels on the
fold - a value-98 texel every third column along the **lower** row of all four plates' outer
faces (front 1,15 / back 37,15 / flanks at y 12), which reads as a stitched crease all the way
round rather than only across the front. The tail is 0.3 x 2.45 x 0.6, so its side faces are
1x3: `[165, 105]` outboard, `[125, 85]` inboard, and the "bright bottom row as the fringe" is
four `pixels` on the last row (215 / 200 / 198 / 150) plus a 225 `down` face. Everything on the
knot is 1x1 or 1x2, so it is flat per-face values (core 178 with `up` 215, lump 195 with `up`
220) - the laurel rule again: **under 2 units on an axis is one texel there**. The inlay mask is
the master's own values on all 42 faces, whole band included, as the brief asked, so the dye
takes the shading and the fold line dyes with it.

**For the next part.** `minecraft:green_wool` is now taken as a template centre. It had never
been cached: `--offline` warned `no texture for 1 item(s) ... green_wool` and drew the
missing-texture square, one plain `python -m modpage build` fetched it, and a third run
(offline) was clean and `unchanged` at 93 recipes - so plan for that round trip whenever the
centre is a block rather than an item. On `brow`, the corridor is now crowded: `laurel` owns
y 29.50..30.78 and this band owns y 28.90..30.10, so a third brow ring has to go either under
the cheek rivet (below y 28.6) or accept sitting inside one of them. And when a brief gives a
cube face that lands on one of your *own* cubes' planes, move it - the checker will not flag
self-coplanarity, but the game will z-fight it.
