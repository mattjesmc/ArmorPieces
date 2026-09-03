# Brief: Fanged Cop

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the ninth
batch of four (read winged_cops.md, padding.md and knee_studs.md first - the same socket, the
real 0.63 window against the greave cube, and every plane the front of the knee already uses).
From the `knees` row of `docs/plans/part-variety.md`:

> **Fanged Cop** - A small beast face over each knee, mouth open downward. Theme: Beast.
> Fitting: `gemstone` (the eyes).

**Part.** `armorpieces:fanged_cop`, socket `knees` only, in the mod's own pack. Display name
"Fanged Cop". Fittings: `armorpieces:gemstone`, one mask, covering the two eye stones. No
effects, no loot, no static layer.

**Shape.** `knees` is a mirrored socket on the leg bone: model ONE leg, the LEFT, at NEGATIVE x.
The leg box is x -3.9..0.1, y 0..12, z -2..2 (pivot -1.9, 12, 0); the boots shell is inflated
0.9 (front z -2.9); the anchor is at Blockbench (-1.9, 6, -2). The front of the knee is the most
crowded place in the mod; planes already in use there, in z: -2.65, -2.75, -2.95, -3.0, -3.12,
-3.15, -3.45, -3.5, -3.52, -3.62, -3.77, -3.87, -4.65; in x: -3.4, -0.4 (loin_panels), -3.45,
-0.45 (winged_cops, same socket so not compared), -3.65, -0.15 (padding); in y: 4.55 and 4.8
(greave), 5.18 (tassets lame). Read the envelopes in the `armorpieces_new` reply and dodge every
plane on another socket by a twentieth; laps with the tassets and greaves parts are the socket's
norm (say by how much). Build a `face` bone at the anchor with the face plate x -3.5..-0.3
(3.2 wide, centred on the leg), y 4.7..7.3, z -3.7..-3.2; a snout box across the plate's lower
half standing 0.25 proud, x -2.9..-0.9, y 4.7..5.9, z -3.95..-3.6 (a tenth into the plate); a
brow ridge along the plate's top edge x -3.5..-0.3, y 7.05..7.4, z -3.85..-3.6; two `eye_l` /
`eye_r` bones each with a stone 0.6 square standing a quarter proud of the plate above the snout,
x -2.95..-2.35 and -1.45..-0.85, y 6.15..6.75, z -3.95..-3.6; and two `fang_l` / `fang_r` bones
hanging from the snout's bottom edge, each a fang 0.4 square by 0.9 tall at x -2.6..-2.2 and
-1.6..-1.2, y 3.9..4.8 (its top a tenth inside the snout), z -3.9..-3.5, the bones rotated 6
degrees about Z so the fangs splay apart (for a cube below its pivot, positive Z swings the free
end toward +x - pendant measured it; the left fang wants negative). The fangs hang into the
greave plate's zone (top y 4.55): lap it, dodge its planes. Nothing below y 3.8.

**Sheets.** Master: plate mid `[top, bottom]` with a dark mouth shadow row along the snout's
underside (`pixels`), snout a step lighter with two nostril texels, brow ridge lighter, fangs
bright with a brightest tip row, eye stones bright with a dark underside. Gemstone mask: the
two stones' faces only.

**Recipe.** Centre item `minecraft:ender_eye` (a flat item, unused by any template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
fanged_cop` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not
cover, and how much the part laps each neighbour.

## Lessons from the session

**Built.** Five bones, seven cubes. `face` at the anchor `(-1.9, 6, -2)`, no rotation, carrying
`plate (-3.50, 4.65, -3.70)..(-0.30, 7.25, -3.20)`, `snout (-2.85, 4.70, -3.95)..(-0.95, 5.90,
-3.55)` and `brow (-3.45, 7.05, -3.85)..(-0.35, 7.40, -3.55)`; `eye_l` at `(-2.65, 6.45, -3.75)`
and `eye_r` at `(-1.15, 6.45, -3.75)` with `stone_l (-2.95, 6.15, -3.95)..(-2.35, 6.75, -3.55)`
and `stone_r (-1.45, ...)..(-0.85, ...)`; `fang_l` pivoted `(-2.4, 4.85, -3.7)` rotated
`[0, 0, -6]` with `fang_left (-2.60, 3.95, -3.90)..(-2.20, 4.85, -3.50)`, and `fang_r` pivoted
`(-1.4, 4.85, -3.7)` rotated `[0, 0, +6]` with `fang_right (-1.60, ...)..(-1.20, ...)`.
Blockbench envelope x -3.50..-0.30, y 3.93..7.40, z -3.95..-3.20; reach 2.89, pair span 7.00.
Data: `knees` only, fitting `armorpieces:gemstone`, no effects, no loot, no static layer, recipe
`minecraft:ender_eye` in a paper ring. Saved without `force`; `check_part.py fanged_cop` and
`check_authoring.py` clean; page rebuilt.

**The brief's planes were nearly all fine - the ones that were not are internal.** Only two of
the brief's numbers collided with another socket, and neither is in the brief's own list: the
"back face at z -3.60" that the snout, brow and eyes were to share is **exactly**
`loin_panels:tassets`'s `panel_front` front plane (Blockbench z -3.60, and it overlaps this part
in all three axes), so all three back faces moved to **-3.55**; and the snout's `x -2.9..-0.9`
is **exactly** `shin_spikes:greaves`'s envelope in x, so the snout was narrowed to
**-2.85..-0.95** (still centred on the leg at -1.9). Both would have been `!` COPLANAR lines.
The check's own envelope table is the authority, not the plane list a brief inherits - read the
*other socket* rows and compare all six bounds, not just z.

**Four sibling z-fights the checker will never mention.** It only tests a part against other
parts, so every butt-joint inside `fanged_cop` had to be reasoned out by hand (the winged_cops
lesson, applied four more times): the snout/brow/eye back faces sink **0.15 inside** the plate
front (-3.55 vs -3.70) rather than butting it; the plate bottom dropped to **4.65** so the
snout's down face at 4.70 is buried inside it instead of coplanar in the 0.10 z-sliver where
they overlap; the brow was inset to **x -3.45..-0.35** so its east/west quads are not coplanar
with the plate's identical -3.50/-0.30; and the fang back face went to **-3.50**, 0.05 behind
the snout's -3.55, so the 0.15 band where fang and snout overlap in y is buried rather than
two opposed quads on one plane. Rule of thumb: two cubes of one part that overlap in any axis
must not agree on a coordinate in any other.

**A Z-rotated bone frees its x and y planes, not its z.** winged_cops learned that a Y rotation
leaves only the y planes testable; the mirror holds here - the fangs rotate about Z, so their
x and y bounds land on irrational numbers and only z -3.90/-3.50 can ever trip the coplanar
test. That is why the fangs could be dropped to y 3.95 straight through the greave zone without
worrying about y 4.55/4.80, and why their z had to be picked with care. `[0, 0, -6]` on the
outer bone and `[0, 0, +6]` on the inner did splay them apart, as the brief predicted from
pendant: for a cube hanging below its pivot, positive Z swings the free end toward +x.

**Laps and clearances, from the saved check.** All fifteen OVERLAP lines are `-` notes. The
`face` bone laps `tassets:tassets`'s `lame3` by up to **2.07 in y** (1.65 x, 0.50 z) and `lame2`
by 0.30, and passes through `loin_panels`'s `panel_front` by **1.81 in y** (3.00 x, 0.40 z) -
the same order as padding (2.42) and winged_cops (2.42), so the mouth sits under the lowest
lame the way the socket always does. Downward the fangs lap `scale_shins`'s `band` by 0.69 in y
and `puttees`'s `wrap1` by 0.51, each 0.49 wide. Everything else is clearance: the plate clears
the real `greave` cube by **0.10 in y** (its bottom 4.65 against the greave top 4.55 - the 0.63
window winged_cops measured, used from the top) and by 0.20-0.45 in z; the fangs clear the
greave by 0.15 in z and `scale_shins`'s `row1` by **0.02 in y**, the tightest number in the
part and deliberately a clearance rather than a shared plane.

**`!` lines accepted: none.** The saved part reports 37 notes and zero problems; the two
cross-socket collisions above were designed out before the first cube was placed.

**Paint: two calls.** One `armorpieces_paint` on `part` - 50 face keys, which the painter
expanded to 126 face writes because later keys repaint earlier ones, plus 4 pixels - and one on
`part_gemstone` (14 keys, 24 writes). Master: plate `[152,118]` with north `[174,132]`, up 192,
down 78; snout a step lighter `[172,140]` / north `[190,158]`, up 204, down 66; brow lighter
still (186-216); stones 206 with north 228 and a dark 72 underside; fangs 232 with north 240
and the **down** face 252 as the bright tip. The 4 pixels are the two nostrils on the snout's
2x1 up face at (23,0) (24,0) = 150, and the mouth shadow as the bottom row of the snout's 2x2
north face at (23,2) (24,2) = 58. What the painter did **not** cover: nothing was left
unpainted (42/42 faces), but the beast's expression is nearly all in six greys per cube - the
snout's north face is only 2x2 texels, so "nostrils *and* a mouth line" does not fit on it and
the nostrils had to go on the muzzle's top face; and the fangs and eyes are 1x1 per face, where
`[top, bottom]` pairs are meaningless. The gemstone mask repeats the master's stone values
face for face (12 faces) so a fitted gem keeps the domed shading; no `null` pixels were needed
here because the whole stone is meant to take the gem colour.

**For the next part.** The `knees` front now has a fifth occupant; if you are working from the
brief's plane list, add **z -3.60 (loin_panels)** and **x -2.90/-0.90 (shin_spikes)** to it, and
note that `pelt:tassets` starts at Blockbench y **7.28**, which is why this plate stops at 7.25.
The free-height story is unchanged: 0.63 against the real greave cube, and every knee part laps
the tassets by roughly two units. Template centres taken so far on this socket:
`minecraft:ender_eye` (this part), `minecraft:iron_leggings`, `minecraft:raw_iron`,
`minecraft:wheat` - `ender_eye` had no cached recipe texture, so one online
`python -m modpage build` was run after the `--offline` one; it is cached now.
