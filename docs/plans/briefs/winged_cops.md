# Brief: Winged Cops

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the sixth
batch of four (read knee_studs.md and padding.md first - the same socket, the 0.38 window, the
frame, the neighbours' planes). From the `knees` row of `docs/plans/part-variety.md`:

> **Winged Cops** - A poleyn with a fin flaring off the outer side - lapping the tassets
> deliberately. Theme: Knightly. Fitting: `guard`.

**Part.** `armorpieces:winged_cops`, socket `knees` only, in the mod's own pack. Display name
"Winged Cops". Fittings: `armorpieces:guard`, one mask, covering the fin and the cop's rim; the
cop's dome stays the material. No effects, no loot, no static layer.

**Shape.** `knees` is a mirrored socket on the leg bone: model ONE leg, the LEFT, at NEGATIVE x.
The leg box is x -3.9..0.1, y 0..12, z -2..2 (pivot -1.9, 12, 0); the leggings shell is
inflated 0.4 (front z -2.4, outer side x -4.3), the boots shell 0.9 (front z -2.9); the anchor
is at Blockbench (-1.9, 6, -2). This socket's front is full - the tassets' lowest lame ends at
y 5.18 and the greave plate starts at y 4.8 - and the shipped parts here use the planes
z -2.65 / -4.65 (poleyns), -2.95 / -3.45 (padding), -3.0 / -3.5 (knee_studs); read the
envelopes in the `armorpieces_new` reply and keep every face a twentieth off all of them.
Build a `cop` bone at the anchor with the knee dome as two cubes: a plate x -3.4..-0.4,
y 4.55..7.45, z -3.62..-3.12 and a smaller boss on it x -2.65..-1.15, y 5.3..6.7,
z -3.87..-3.62 (a tenth inside the plate's front so no plane is shared); a rim: two thin
bars along the plate's top and bottom edges 0.15 proud (x -3.4..-0.4, y 7.2..7.45 and
4.55..4.8, z -3.77..-3.62). Then the wing: a `fin` bone pivoted at the cop's outer edge
(-3.4, 6.0, -3.37), rotated about Y by +35 degrees so the fin sweeps out and BACK along the
outside of the knee (for a plate modelled along -X from its pivot, a positive Y rotation swings
its far end toward +Z - confirm on the first reply and flip if it swung forward), carrying a fin
plate modelled along -X: x -5.6..-3.4, y 4.9..7.6, z -3.52..-3.22, and a fin tip half as tall
stacked beyond it x -6.4..-5.6, y 5.6..6.9, same z. The fin laps the tassets' lames on
purpose - say by how much. Nothing below y 4.5 and nothing above y 7.7.

**Sheets.** Master: dome plate mid-light `[top, bottom]` with the boss a step lighter and a
bright specular texel, rim bars bright, the fin `[top, bottom]` lighter toward its tip with a
bright leading (up) face and a dark down face. Guard mask: the fin, fin tip and rim bars only,
shaded like the master.

**Recipe.** Centre item `minecraft:iron_leggings` (a flat item, unused by any template), paper
ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
winged_cops` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not
cover, and how much the fin laps the tassets.

## Lessons from the session

**Built.** Two bones. `cop` at the anchor `(-1.9, 6, -2)`, no rotation, four cubes:
`plate (-3.45, 4.60, -3.62)..(-0.45, 7.45, -3.12)`, `boss (-2.65, 5.30, -3.87)..(-1.15, 6.70,
-3.52)`, `rim_top (-3.45, 7.20, -3.77)..(-0.45, 7.55, -3.52)`, `rim_bottom (-3.45, 4.50,
-3.77)..(-0.45, 4.75, -3.52)`. `fin` pivoted at `(-3.45, 6, -3.37)` and rotated `[0, 35, 0]`,
carrying `vane (-5.65, 4.90, -3.52)..(-3.45, 7.60, -3.22)` and `vane_tip (-6.45, 5.60,
...)..(-5.65, 6.90, ...)`. Blockbench envelope x -5.99..-0.45, y 4.50..7.60, z -3.87..-1.53;
reach 4.20, pair span 11.99. Data: `knees` only, fitting `armorpieces:guard`, no effects, no
loot, no static layer, recipe `minecraft:iron_leggings` in a paper ring (it was already cached,
so one `--offline` build rendered it). Saved without `force`; `check_part.py winged_cops` and
`check_authoring.py` clean; page rebuilt.

**The brief's x sits exactly on loin_panels.** `plate`/`rim` at x -3.4..-0.4 is bone-local
x -1.5..1.5, which is *exactly* `loin_panels:tassets`'s `panel_front` - and that part overlaps
the cop in all three axes, so the brief's numbers would have been two COPLANAR problems. The
whole cop was shifted a twentieth outward to x **-3.45..-0.45**; the fin pivot moved with it to
-3.45 so the wing still springs from the plate's outer edge. Check a knee part's x against the
tassets parts' bone-local ±1.5 before placing, not after.

**+35 about Y did swing the tip back**, as the brief guessed: for cubes modelled along -X from
the pivot the far end goes to +Z, and the first reply confirmed it (envelope z reaching -1.53
from a pivot at -3.37). No flip needed. A rotated bone is also cheap insurance: the fin's hull
bounds land on irrational numbers in x and z, so only its two y planes (4.90, 7.60) can ever
trip the shared-plane test - and neither did.

**The greave's real top is y 4.55, not 4.80.** knee_studs and padding both recorded the free
window as 4.80..5.18 = 0.38; 4.80 is the greaves **envelope** top (some other cube of that
part), and the `greave` cube that actually sits on the front of the knee tops out at Blockbench
y **4.55**. The first placement put the plate's bottom there and drew
`note: cop and greaves:greaves's greave share the plane y = 7.45 (inside the shell, so
occluded)` - a `-` note, but a real pair of coplanar opposed quads, and entity rendering does
not cull backfaces. Moved to y 4.60, which the saved check reports as `cop clears greave by
0.05 in y`. Against the real cube the front-of-knee window is 4.55..5.18 = 0.63, not 0.38.

**Sink sibling faces, do not butt them.** The brief's boss and rim bars had their back faces at
z -3.62, the plate's own front plane. The checker never looks at a part's own internal planes,
so it would have stayed silent while the boss's south quad z-fought the plate's north quad in
game. Both were sunk a tenth into the plate (back face z -3.52), and for the same reason the
rim bars were made 0.1 proud of the plate in y (7.20..7.55 and 4.50..4.75) instead of flush at
7.45/4.55 - which also keeps rim_bottom's up face off y 4.80. The lip reads as a rolled rim.

**Laps, measured from the saved check.** All `-` OVERLAP notes. The fin laps `tassets:tassets`'s
lowest lame `lame3` by **2.42 in y** (0.49 x, 1.51 z) and `lame2` by 0.50 in y (0.89 x, 1.51 z);
the cop body laps `lame3` by 2.27 in y (1.60 x, 0.50 z) and `lame2` by 0.35. The fin also passes
through `loin_panels`'s `panel_front` (2.16 y x 0.74 z), `thigh_sheath`'s `strap_lower`
(0.40 y x 0.81 z), `pelt`'s `fall` (0.32 y) and `scale_skirt`'s `row3` (0.50 y). That is the
point of the part - the wing laps the tassets deliberately, by about two and a half units of
height where the lowest lame hangs - and it is in the same range as padding (2.42) and garters.

**`!` lines accepted: none.** The saved part reports 34 notes and zero problems; the two
placements above were fixed by moving faces rather than accepting anything.

**Paint: two calls.** One `armorpieces_paint` on `part` (37 face entries, which the painter
expanded to 102 face writes because later keys repaint earlier ones, plus 1 pixel) and one on
`part_guard` (22 entries, 42 writes). The master: plate `[158,120]` with north `[178,138]`, up
196, down 84; boss a step lighter `[186,150]` / north `[202,164]` with the single specular texel
at (21,1) = 236; both rim bars bright (194-228); vane `[166,128]` and vane_tip `[192,156]` with
up 226/232 and down 70/76. The mask repeats the master's values on `vane`, `vane_tip`,
`rim_top`, `rim_bottom` only - 24 faces - so a fitted guard dyes the wing and the rim while the
dome and boss stay on the trim material, as the brief asked. What the painter did **not** cover:
any gradient *along* the fin, because `[top, bottom]` shades vertically only - the taper toward
the tip is a step between the two cubes' value pairs, not a ramp; and nothing was left unpainted
(36/36 faces on the master, including the vane's east face buried in the plate).

**For the next part.** The `knees` window is 0.63 against the greave cube, 0.38 against the
greaves hull - use the cube-level `near:` lines, not the envelope table, once something is
placed. Same-socket parts are never compared, so the only planes worth pre-computing are the
tassets and greaves parts' - and bone-local ±1.5 (Blockbench -3.40/-0.40) is a busy pair of
planes on this leg. Template centres now taken: `minecraft:iron_leggings` (this part),
`minecraft:raw_iron`, `minecraft:wheat`.
