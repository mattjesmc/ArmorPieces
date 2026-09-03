# Brief: Padding

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the fourth
batch of four, a Wayfarer set (read the lessons in knee_studs.md first - the same socket, the
measured 0.38 window, the frame - and garters' numbers in the envelope reply). From the `knees`
row of `docs/plans/part-variety.md`:

> **Padding** - Quilted pads, stitched in a diamond grid. Theme: Wayfarer. Fitting: `inlay`.

**Part.** `armorpieces:padding`, socket `knees` only, in the mod's own pack. Display name
"Padding". Fittings: `armorpieces:inlay`, one mask, covering the pad's cloth; the stitching
stays the material so a dyed pad keeps its grid. No effects, no loot, no static layer.

**Shape.** `knees` is a mirrored socket on the leg bone: model ONE leg, the LEFT, which in this
rig is at NEGATIVE x. The leg box is x -3.9..0.1, y 0..12, z -2..2 (pivot -1.9, 12, 0); the
leggings shell is inflated 0.4 (front z -2.4) and the boots shell 0.9 (front z -2.9), and the
anchor is at Blockbench (-1.9, 6, -2). The front of the knee is the tightest place in the mod:
the tassets' lowest lame ends at y 5.18 and the greave plate starts at y 4.8, both deeper than
z -3.6, so any pad taller than 0.38 laps one or both - knee_studs lapped 0.9 each way and
garters 1.0/1.67. Plan to lap and say by how much; the one thing to avoid is a shared plane,
so keep every face a tenth off the neighbours' planes the envelope reply lists (poleyns' back
face is z -2.65, greaves' and tassets' faces are further out). Build a `pad` bone at the
anchor with one pad cube x -3.65..-0.15 (3.5 wide, centred on the leg), y 4.4..7.6 (3.2 tall,
centred on the window's midpoint at y 4.99 is not possible without dropping below the greave's
top, so centre it on the knee itself at y 6 and accept the lap), z -3.45..-2.95 - the 0.05
past the boots shell keeps it off z -2.9; and two `tie_l` / `tie_r` bones with a small tie
plate each wrapping the leg's sides a tenth off the leggings shell at y 5.75..6.25: outer
x -4.55..-4.3, z -2.5..-0.5, and inner x 0.5..0.75, z -2.5..-0.5 (the inner one is inside the
other leg's shell and never seen; paint it anyway). Nothing else - the quilting is paint. The
pad's front face is 4x4 texels: the diamond grid is the stitching drawn as `pixels`, the
darker texels at (0,0) (1,1) (2,2) (3,3) and (3,0) (2,1) (1,2) (0,3) of the face rectangle,
which reads as one diamond with a cross through it - the most a 4x4 face can say.

**Sheets.** Master: pad mid-light `[top, bottom]` with the stitch diagonals about 40 values
darker in `pixels`, the ties darker plain; sides of the pad a step darker, top face lightest.
Inlay mask: the pad's faces at the same values but WITHOUT the stitch pixels (paint the mask
face flat-shaded, then null nothing - the stitches simply are not repeated), so the dye leaves
the grid in the material's colour; ties included in the mask.

**Recipe.** Centre item `minecraft:wheat` (a flat item, unused by any template - straw
stuffing), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
padding` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not
cover, and how much the pad laps each neighbour.

## Lessons from the session

**Built.** One `pad` bone at the anchor `(-1.9, 6, -2)` with a single cube
`(-3.65, 4.40, -3.45)..(-0.15, 7.60, -2.95)` (3.5 x 3.2 x 0.5, centred on the leg, 0.05 in front
of the boots shell), plus `tie_l` / `tie_r` bones carrying a 0.25 x 0.5 x 2 tie plate each,
`(-4.70, 5.75, -2.5)..(-4.45, 6.25, -0.5)` outside and `(0.60, ...)..(0.85, ...)` inside. No
rotation anywhere - the quilting is paint. Data: `knees` only, fitting `armorpieces:inlay`, no
effects/loot/static, recipe `minecraft:wheat` in a paper ring (unused by any other template; it
rendered with a real texture on the second, online `modpage build`, so it is now cached).
Saved without `force`; `check_part.py padding` and `check_authoring.py` clean; page rebuilt.

**The brief's tie x values sit exactly on a shell.** `outer x -4.55..-4.30` and
`inner x 0.5..0.75` both start ON the leggings shell (the leg box x -3.9..0.1 inflated 0.4 is
x -4.30..0.50), so the first placement drew `! COPLANAR: tie_l's x face at 2.4 lies on the
leggings shell`. Moving out to -4.65 then hit a second one: `tie_l and thigh_sheath:tassets's
sheath share the plane x = 2.5` (Blockbench x -4.40). The pair that is clear of both is
**-4.70..-4.45** outside and **0.60..0.85** inside - a tenth clear of the shell and a quarter
clear of the sheath. Read a "a tenth off the shell" instruction as an instruction to compute,
not to copy.

**Laps, measured from the saved check.** Every lap is a `-` OVERLAP note, none a problem:
into `tassets:tassets`'s `lame3` by **2.42 in y** (1.80 x, 0.50 z) and `lame2` by 0.50 in y -
the pad's top at y 7.6 is 2.42 above the tassets' lowest lame bottom at y 5.18; into
`greaves:greaves`'s `greave` by **0.15 in y** (twice, 0.90 and 1.00 wide), into
`scale_shins`'s `band` by 0.22 in y, into `puttees`'s `wrap1` by 0.05 in y - the pad's bottom
at y 4.4 is 0.40 under the greaves envelope's top at 4.80, but the real greave cubes only meet
it by 0.15. `tie_l` laps `thigh_sheath`'s `sheath` by 0.25 x 0.50 x 0.24. So the pad laps the
tassets by ~2.4 and the greaves by ~0.2-0.4 - more upward than knee_studs (0.9/0.9) because a
3.2-tall pad centred on the knee at y 6 cannot do otherwise in a 0.38 window, and the tassets'
lames are cloth-adjacent lamellae that a quilted pad reads as sitting under.

**`!` lines accepted: none.** The two COPLANAR problems above were fixed by moving faces, not
accepted; the saved part reports 13 notes and zero problems. The pad's z -3.45/-2.95 collides
with no neighbour's face plane (poleyns' back face is z -2.65, greaves' and tassets' faces are
at -3.65 and further).

**Paint: two calls, 46 faces + 8 pixels each.** One `armorpieces_paint` on `part` and one on
`part_inlay`, both with the same face map -
`{"*.*":150, "pad.*":[170,140], "pad.east/west":[152,126], "pad.south":118,
"pad.north":[178,152], "pad.up":205, "pad.down":104, "tie_out.*":96, "tie_in.*":96,
"tie_out/in.up":118, ".down":72}` - so the mask carries the master's shading rather than a flat
grey. The painter covered every face; the only thing it could not do by face is the quilting,
which is the 8 `pixels`: on the master the two diagonals of the 4x4 north face at (13,1) (14,2)
(15,3) (16,4) and (16,1) (15,2) (14,3) (13,4), each about 40 values under the gradient row it
sits in (136/128/119/111), which reads as one diamond with a cross through it.

**The mask must be NULL where the stitching is, not flat.** The brief says "paint the mask face
flat-shaded, then null nothing", but `DecorationTextureManager.applyMask` *replaces* the baked
pixel wherever the mask's alpha is non-zero (the master only supplies the silhouette's alpha).
A flat mask over the whole north face would therefore erase the grid the moment an inlay is
fitted - the opposite of the brief's own intent ("the stitching stays the material so a dyed
pad keeps its grid"). So the second paint call passes the same 8 pixels with `value: null`,
leaving the stitch texels transparent on `part_inlay`: the dye fills the cloth, the diagonals
stay on the trim material's ramp. The check is happy either way, so this is a decision the
tooling will not make for you.

**For the next part.** A masked fitting is opaque-wins: anything you want to survive the dye has
to be a hole in the mask, and `armorpieces_paint` takes `null` per pixel for exactly that. The
`knees` window is still 0.38 units (greaves top y 4.80, tassets lame3 bottom y 5.18) - the
third part in a row to lap it. `minecraft:wheat` and `minecraft:raw_iron` are now taken as
template centre items.
