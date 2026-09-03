# Brief: Anklets

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the tenth
batch of four (read bells.md, rowel_spurs.md and talons.md first - same socket, the leg frame,
the swim_fins flank and the shin_spikes plate on the greaves socket). From the `spurs` row of
`docs/plans/part-variety.md`:

> **Anklets** - Beaded rings at the ankle. Theme: Court. Fitting: `gemstone`.

**Part.** `armorpieces:anklets`, socket `spurs` only, in the mod's own pack. Display name
"Anklets". Fittings: `armorpieces:gemstone`, one mask, covering the single stone at the back of
the upper ring; the rings and beads stay the material. No effects, no loot, no static layer.

**Shape.** `spurs` is a mirrored socket on the leg bone: model ONE leg, the LEFT, at NEGATIVE x.
The leg box is x -3.9..0.1, y 0..12, z -2..2 (pivot -1.9, 12, 0); the boots shell is that box
inflated 0.9, x -4.8..1.0, z ±2.9; the anchor is at Blockbench (-1.9, 2, 2). Read the envelopes
in the `armorpieces_new` reply: the other spurs parts are never compared; on the greaves socket
swim_fins owns the outer flank (x -7.14..-4.11, y 0.78..3.44, z -2..2) and shin_spikes' plate
the front at z -3.4..-2.95, y 0.9..3.5 - rings round the ankle lap both hulls (the socket's
norm) and must dodge their planes (x -4.11, z -3.4, z -2.95) by a twentieth. Build two rings,
`ring_low` at y 0.9..1.2 and `ring_high` at y 1.6..1.9, each four bars 0.3 square in section a
tenth off the shell (outer x -5.2..-4.9, inner x 1.1..1.4, front z -3.3..-3.0, back z 3.0..3.3,
each the full span so the corners double up - keep the two rings' outer planes identical, they
never touch each other in y). Six beads on the upper ring in one `beads` bone, each a 0.5 cube
straddling the bar (0.1 proud on both faces): at z -2.0, 0 and 2.0 on the outer bar, and at
x -3.5, -1.9 and -0.3 on the front bar, each bead a twentieth off the next plane the reply
lists. A `stone` bone with a 0.7 cube on the back bar at x -2.25..-1.55, y 1.5..2.2,
z 3.1..3.8 (a twentieth into the bar), the gemstone. Nothing below y 0.85, nothing above 2.25.

**Sheets.** Master: bars mid grey with a lighter top face; beads bright `[top, bottom]` with a
dark underside; stone brightest with a specular texel and a dark underside. Gemstone mask: the
stone's faces only.

**Recipe.** Centre item `minecraft:quartz` (a flat item, unused by any template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
anklets` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

Built 2026-09-04 in 23 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`list_outline`, 4 `add_group`, 3 `place_cube`, **6 `modify_cube`**, 2 `remove_element` (starter
cube, then its bone), 1 `armorpieces_check`, 1 `armorpieces_part`, 1 `armorpieces_set_part`,
**2 `armorpieces_paint`**, 2 `set_camera_angle`, 1 `armorpieces_save`. No `risky_eval`, no
`undo`; the save went through without `force`.

**What I built.** Four bones, all at the anchor (-1.9, 2, 2), none rotated. `ring_low` and
`ring_high` are each four bars: side bars `low_out`/`high_out` x -5.20..-4.90 and
`low_in`/`high_in` x 1.10..1.40, z -3.25..3.25, y 0.98..1.22 / 1.65..1.89; front and back bars
x -5.15..1.35, z -3.30..-3.00 and 3.00..3.30, y 0.95..1.25 / 1.62..1.92. `beads` holds six
cubes at y 1.56..2.06 - three on the outer bar (x -5.40..-4.95) at z -2, 0, +2, three on the
front bar (z -3.52..-3.02) at x -3.5, -1.9, -0.3. `stone` holds `gem`, 0.7 cube at
x -2.25..-1.55, y 1.5..2.2, z 3.1..3.8, its front face 0.2 inside the back bar. Envelope
x -5.40..1.40, y 0.95..2.20, z -3.52..3.80; past boots x+0.60 z+0.90.

**The corners: which bar is "full span" is a choice, and only one of the two can be.** The brief
asked for four bars "each the full span so the corners double up", which as written gives eight
coincident faces per ring. Applying rowel_spurs' rule, the front/back bars are the full ones in
x (their ends die inside the side bars' 0.3 thickness at -5.15 / 1.35) and the side bars are the
full ones in z but stop at ±3.25, inside the front/back bars; the side bars are also 0.03 inset
in y at top and bottom. Result: no two cubes of the part share a plane, every joint is a real
interpenetration, and all offsets are under a twentieth of a texel. Both rings keep identical
x and z planes as briefed - they never meet in y, so their coplanar-but-disjoint outer faces are
harmless.

**A 0.5 bead cannot straddle the boot's side bar symmetrically - the shell plane is where it
lands.** Beads centred on the outer bar at x -5.30..-4.80 put their inner face exactly on the
boots shell at bb x -4.80 (bone x 2.9), and the check said so at once:
`! COPLANAR: beads's x face at 2.9 lies on the boots shell`. The corridor is unforgiving: the
shell is 0.10 inside the bar's inner face, so any bead wide enough to be proud on both sides
must either sit on the shell or reach through it. I made them 0.45 wide, x -5.40..-4.95, so they
bulge 0.20 outward and their inner face is buried 0.05 *inside* the bar - a bead on the outside
of a band, which is what a bead is. The same reasoning drives the front beads: shin_spikes' plate
occupies z -3.40..-2.95 and the shell is at -2.90, so a bead there is z -3.52..-3.02, proud 0.22
forward with its back face buried in the bar. **Rule for the spurs socket: at the ankle, plan
ornaments to be proud outward only and buried inward; the twentieth-of-a-unit corridor between
the shell and the neighbours has no room for a symmetric straddle.**

**"clears ... by 0.00" is worth fixing even though it is only a note.** With the beads at
y 1.52..2.02 the check said `near: beads clears scale_shins:greaves's row1 by 0.00 in y` - the
bead bottoms and that scale row's tops were the same plane, back to back, over a real x/z
overlap. The check does not mark that `!` (it is not a *shared* plane in its sense), but it is a
z-fight all the same, so all six beads moved to y 1.56..2.06: 0.04 clear of scale_shins' row1
below and 0.05 clear of puttees' wrap1 above. Six `modify_cube` calls, one per cube - there is no
batched resize.

**`!` lines accepted: none.** The finished check reads `ok: nothing needs a decision`. 75 `-`
notes stand, all against the greaves parts, and all of them are what bells predicted: a ring
round the ankle laps `swim_fins`' rays and webs on the outer flank, `puttees`' wraps and tie,
`scale_shins`' rows, `greaves`' greave and `shin_spikes`' plate, because between y 0.9 and 2.1
the ankle is where every greaves part already is. The four `share the plane` notes
(z ±0.25, ±1.75 against swim_fins, x 1.85 against greaves, y 10.75 / 10.35 against greaves and
puttees) are each tagged by the check itself as "inside the shell, so occluded". Nothing of mine
lies on the boots shell or on a neighbour's exposed plane.

**Paint: two calls, 90 master faces + 6 mask faces, nothing unpainted.** Master (1 call):
`"*.*": 130` then a per-cube block for all fifteen cubes - bars 118..136 with lit `up` faces
170..190 and dark `down` 76..86, the outward long face of each bar ~20 brighter than the inward
one, upper ring ~8 brighter than the lower; beads 198..204 with `up` 240 and `down` 68; the gem
226 with `south` (its exposed back face) 246, `up` 255 and `down` 58. Gemstone mask (1 call): the
gem's six faces at the master's own values, so a fitted stone keeps the shading rather than going
flat - the rings and beads stay trim material as briefed.

What the painter did **not** cover: **every ornament face here is one texel, and half the bar
faces are single-row strips**, so `[top, bottom]` pairs were useless throughout and were not used
once. A bead is 0.5 units - all six of its faces are 1x1 - so the brief's "bright `[top, bottom]`
with a dark underside" collapses to two scalars, and the gem's "specular texel" is simply its
`up` face painted 255. The bars' `east`/`west` (7x1) and `north`/`south` (7x1) faces are one row
too; only the side bars' `up`/`down` are 1x7, and a gradient down a strip whose vertical is the
leg's z axis says nothing, so those stayed flat. All the modelling of light here is *between*
faces, not within them.

**Recipe.** `minecraft:quartz` in a paper ring: a flat item, unused by any other `template_*`
(one grep over `data/armorpieces/recipe/template_*.json` before setting it). `python -m modpage
build --offline` warned `no texture for minecraft:quartz`; one plain `python -m modpage build`
cached it and the next offline build is clean - the talons/flint, bells/bell pattern again.

**For the next part.** Three sessions have now recorded the same ankle geography, so take it as
settled: **behind z 3 is empty, the ring at y 1..2.2 laps everything, and the outer flank from
x -4.11 is swim_fins'.** The new number is the boots shell's *side* plane, bb x -4.80 (bone x
2.9) - the one plane on the leg that gives a real `!`, and the reason anything sitting on the
boot's side must be either 0.1 proud of it or frankly inside it. Twenty other tabs were open and
`armorpieces_new` made this one active without touching them.
