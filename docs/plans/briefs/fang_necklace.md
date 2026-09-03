# Brief: Fang Necklace

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the fifth
batch of four, a Beast set (read pendant.md's lessons first - same socket, the cord sign, the
depth budget - and bone_mask.md for the static layer). From the `collar` row of
`docs/plans/part-variety.md`:

> **Fang Necklace** - A string of teeth and beads. Theme: Beast. Fittings: none.

The plan lists no fitting; this brief gives the centre amulet a `gemstone` mask so the necklace
is not the only Beast part with nothing to fit, and puts the teeth on a static layer so they
stay ivory whatever the trim material.

**Part.** `armorpieces:fang_necklace`, socket `collar` only, in the mod's own pack. Display name
"Fang Necklace". Fittings: `armorpieces:gemstone`, one mask, covering the centre amulet only.
Static layer (`static: true`) for the teeth. No effects, no loot.

**Shape.** `collar` is not a mirrored socket: model the whole thing, centred on x = 0, on the
body bone. The torso box is x -4..4, y 12..24, z -2..2 (pivot 0, 24, 0); the chestplate shell is
that box inflated a full unit, x -5..5, y 11..25, z -3..3, and the anchor is at Blockbench
(0, 23, -2). The strand lies on the chestplate at z -3.35..-3.1. Read the envelopes in the
`armorpieces_new` reply; the same-socket parts are never compared, but for the record
chain_of_office occupies z -4.6..-2.6 and pendant z -3.85..-3.1, so keep this necklace inside
z -4.0. Build: a `strand` bone with a straight cord cube x -3.2..3.2, y 22.6..22.9,
z -3.35..-3.1 across the upper chest, and two short riser cords from its ends up to the
collarbones (x -3.2..-2.9 and 2.9..3.2, y 22.6..24.3) so the string reads as hung from the
neck; five `tooth_*` bones hanging from the strand at x -2.4, -1.2, 0, 1.2, 2.4, each a tooth
cube 0.5 wide, 1.25 tall (the centre one 1.6), 0.5 deep at z -3.6..-3.1, top at y 22.7 so it
laps the strand by a tenth, each bone rotated about Z so the outer teeth splay - about +12 and
+6 degrees on the negative-x side, -6 and -12 on the positive side, the centre straight (for
a cube hanging BELOW its pivot, positive Z swings the free end toward +x; pendant confirmed
this); four `bead_*` cubes 0.45 square sitting on the strand between the teeth at x ±0.6 and
±1.8, y 22.5..22.95, z -3.5..-3.05, in one `beads` bone; and an `amulet` bone with a
0.9x0.9x0.6 stone hanging under the centre tooth's root, x -0.45..0.45, y 21.6..22.5,
z -3.9..-3.3, standing proud of the tooth. Nothing above y 24.3 and nothing wider than x ±3.3.

**Sheets.** Master: strand and beads mid grey (the beads a step lighter with a bright top
face), teeth mid grey `[top, bottom]` lighter toward the tip (the master still needs paint
under the static layer, it supplies the silhouette), amulet bright with a dark underside and
one specular texel. Static layer: the five teeth only, ivory `[#efe6d2, #d9cdb0]` top to bottom
with a `#b9ab8c` bottom texel on each; leave the strand, beads and amulet off the static so they
keep the trim material. Gemstone mask: the amulet's faces only.

**Recipe.** Centre item `minecraft:beef` (raw beef, a flat item, unused by any template), paper
ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
fang_necklace` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

Built 2026-09-03 in 30 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`armorpieces_part`, 1 `list_outline`, 8 `add_group`, 8 `place_cube`, 2 `remove_element` (starter
cube, then its `main` bone), 1 `armorpieces_check`, 1 `armorpieces_set_part`, **3
`armorpieces_paint`** (one per sheet), 2 `set_camera_angle`, 1 `armorpieces_save`. No
`risky_eval`, no `modify_cube`, nothing nudged, nothing hand-edited, and the save went through
first time **without `force`**.

**What I built.** Thirteen cubes in eight bones, exactly the brief's numbers except for five
rotation signs (below). `strand` (pivot 0, 23.4, -3.225) carries `cord` x -3.2..3.2,
y 22.6..22.9, z -3.35..-3.1 and the two risers `riser_l` x -3.2..-2.9 / `riser_r` x 2.9..3.2,
y 22.6..24.3, same depth. Five tooth bones pivot on the cord at y 22.7, z -3.35, at
x -2.4/-1.2/0/1.2/2.4, each holding one 0.5-wide fang modelled straight down from the pivot
(`fang_l2`, `fang_l1`, `fang_r1`, `fang_r2` 1.25 tall, `fang_c` 1.6, all z -3.6..-3.1). `beads`
holds four 0.45 cubes at x +/-0.6 and +/-1.8, y 22.5..22.95, z -3.5..-3.05; `amulet` holds
`stone` x -0.45..0.45, y 21.6..22.5, z -3.9..-3.3. Envelope (Blockbench) x +/-3.20,
y 21.10..24.30, z -3.90..-3.05; reach 3.71, `past chestplate z+0.90` - inside the brief's
z -4.0 budget and 0.05 shallower than `pendant`.

**The five tooth rotations are the brief's magnitudes with the signs flipped, on purpose.** The
brief asks for "the outer teeth splay" and then gives +12/+6 on the negative-x side while quoting
pendant's rule ("positive Z swings the free end toward +x"). Those two halves contradict each
other: with a positive angle the negative-x teeth swing their TIPS toward the centre, i.e. the
row converges into a V instead of fanning. I kept the word and dropped the numbers' signs:
`tooth_l2` -12, `tooth_l1` -6, `tooth_c` 0, `tooth_r1` +6, `tooth_r2` +12, which is what a cord
hung over the collarbones does to the teeth threaded on it. The arithmetic before placing said
the outermost fang's far bottom corner lands at x 2.905 (pivot 2.4 + 0.25 cos12 + 1.25 sin12) and
y 21.53, and the check's envelope came back x +/-3.20 - the risers, not the teeth, set the width,
so the fan is comfortably inside the briefed x +/-3.3. **Whenever a brief gives both a word and a
sign, do the trigonometry and trust the word:** the sign is the part that gets copied wrong.

**`!` lines accepted: none.** The only problem the check ever raised was the standing
unpainted-face count (78/78), cleared by the first paint call; clashes read *"all clear by more
than half a unit"* against all ten other-socket body parts, because everything on `back` is at
z > 0.3 and everything on `belt` is below y 16.5. Two numbers that could have raised a note and
did not: the beads' back faces at z -3.05 sit 0.05 in front of the chestplate shell's z -3 plane
(a near miss, not a coplanar face - the check stayed silent, so a 0.05 standoff is enough when
the face is small), and the `amulet` swallows the middle of `fang_c` (y 21.6..22.5 of a
21.1..22.7 tooth) without a buried-face note, since neither cube's face is fully inside the
other.

**Three paint calls, one per sheet, and they covered every face.** Master (232 face writes +
6 pixels in one call): `*.*` 120, then cord 150 north / 190 up / 75 down, risers `[175,140]`
north with a 200 top, beads a step lighter (165 base, 215 up, 185 north), teeth `[130,205]` down
the north and `[110,180]` on the sides with a 225 tip and a 100 root, stone 238 north / 246 up /
68 down; the pixels are the two riser crowns (210), three sparkles along the cord's top row
(205) and the amulet's specular texel (255). Static (30 faces): the five teeth only - ivory
`[#efe6d2, #d9cdb0]` on the north, a half-step darker on the sides, `#c9bd9f` on the root and
`#b9ab8c` on the tip texel - so cord, beads and amulet keep the trim material. Gemstone mask
(6 faces + 1 pixel): the stone's six faces at the master's own values, per bone_mask's rule that
a flat mask kills the lit top texel.

What the painter did **not** cover: at this scale there is nothing left to paint. Every fang face
is 1x2 texels and every bead and amulet face is **1x1**, so a `[top, bottom]` pair collapses to
its top value on eleven of the thirteen cubes and the whole vertical story is carried by the
per-face step, not by a gradient - the amulet's "dark underside" is literally one texel (68) and
its specular highlight is the single texel of the up face (255), which is why the `pixels` list
duplicates the face value there rather than adding detail inside it. Whole sheet: master 130
opaque texels in 22 greys, static 50 texels in 8 colours, mask 6 - a 64x32 sheet is barely a
third full.

**For the next part.** `minecraft:beef` is now taken as a template centre. It had never been
cached: `python -m modpage build --offline` warned *"no texture for 1 item(s), drawn as
missing-texture (minecraft:beef)"*, a plain `python -m modpage build` fetched it silently, and a
third offline build reported `unchanged` - the same three-step dance as the last seven sessions,
and the warning is the only signal you get, since the markdown does not change when only a
recipe icon is re-rendered. `armorpieces_set_part` created `part_gemstone` and `part_static` in
one call and wrote `template_fang_necklace.json` on save (*"installed 3 file(s)"*); do it before
painting. The 3D view draws the **master only**, so the ivory teeth render grey in every
screenshot - judge silhouette there and check the colours with Pillow on the saved `_static.png`.
For the next `collar` part, the shipped depth band is now crowded: `chain_of_office` -4.60..-2.60,
`bandolier` -3.65..-2.35, `pendant` -3.85..-3.10, this necklace -3.90..-3.05, `brooch` out to
-4.75 and `gorget` back to +0.75; the room left on the upper chest is either deeper than -4.75 or
below y 19, where only `pendant`'s stone reaches.
