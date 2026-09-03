# Brief: Bells

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the ninth
batch of four (read rowel_spurs.md and talons.md first - same socket, the leg frame, the
swim_fins flank, and staggering coplanar plates). From the `spurs` row of
`docs/plans/part-variety.md`:

> **Bells** - Small bells on ankle straps. Theme: Court. Fitting: `guard`.

**Part.** `armorpieces:bells`, socket `spurs` only, in the mod's own pack. Display name "Bells".
Fittings: `armorpieces:guard`, one mask, covering the three bells; the strap stays the
material. No effects, no loot, no static layer.

**Shape.** `spurs` is a mirrored socket on the leg bone: model ONE leg, the LEFT, at NEGATIVE x.
The leg box is x -3.9..0.1, y 0..12, z -2..2 (pivot -1.9, 12, 0); the boots shell is that box
inflated 0.9, x -4.8..1.0, z ±2.9; the anchor is at Blockbench (-1.9, 2, 2). Read the envelopes
in the `armorpieces_new` reply: the other spurs parts are never compared; the greaves parts
share the bone - swim_fins owns the outer flank (x -7.14..-4.11, y 0.78..3.44, z -2..2) and
shin_spikes' plate the front at z -3.4..-2.95, y 0.9..3.5 - so a strap round the ankle laps
swim_fins' hull (rowel_spurs' arm does the same) and must dodge the planes z -3.4 / -2.95,
x -4.11 / -7.14 by a twentieth. Build a `strap` bone at the anchor with a ring of four plates a
quarter thick and half a unit tall at y 1.6..2.1 a tenth off the shell (outer x -5.15..-4.9,
inner x 1.1..1.35, front z -3.25..-3.0, back z 3.0..3.25, each the full span so corners double
up). Three bells, each its own bone hanging from the strap, one at the back centre (pivot
(-1.9, 1.6, 3.125)), one at the back-outer corner (pivot (-5.0, 1.6, 3.125)) and one on the
outer side toward the front (pivot (-5.025, 1.6, -1.2)); each bell is three cubes: a loop
0.3 square from y 1.7 (a tenth inside the strap) down to y 1.3, a body 0.8 square from y 1.3
down to y 0.5, and a clapper 0.3 square from y 0.5 down to y 0.25, all standing a twentieth
proud of the strap face they hang beside; each bell bone rotated 8 to 12 degrees about the axis
along its strap plate so the three dangle at slightly different angles (any sign - they are
ornaments), and the lowest corner must stay above y 0.1. Stagger the three bodies' thicknesses
by a few hundredths if any two share a plane (rowel_spurs' lesson).

**Sheets.** Master: strap mid grey `[top, bottom]`; loops mid; bell bodies bright `[top,
bottom]` with a dark bottom face and one darkest texel as the slit (`pixels`) on each body's
outward face; clappers dark. Guard mask: the nine bell cubes' faces (loops, bodies, clappers) at
the master's values.

**Recipe.** Centre item `minecraft:bell` (a flat item icon, unused by any template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py bells`
and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons paragraph below
filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

Built 2026-09-03 in 15 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`list_outline`, 4 `add_group`, 4 `place_cube`, 2 `remove_element` (starter cube, then its bone),
1 `modify_cube`, 1 `armorpieces_check`, 1 `armorpieces_part`, 1 `armorpieces_set_part`,
**2 `armorpieces_paint`**, 1 `set_camera_angle`, 1 `armorpieces_save`. No `risky_eval`, no
`undo`: the brief's rig numbers were enough and the save went through without `force`.

**What I built.** A `strap` bone at the anchor (-1.9, 2, 2) with four plates - `strap_out`
x -5.15..-4.90 and `strap_in` x 1.10..1.35 (both y 1.60..2.10, z -3.25..3.25, the full span),
`strap_front` z -3.22..-3.00 and `strap_back` z 3.00..3.22 (both x -5.10..1.30, y 1.65..2.05) -
and three bell bones under it: `bell_back` at (-1.9, 1.6, 3.27) rotated -9 about X,
`bell_corner` at (-4.99, 1.6, 3.29) rotated +11 about X, `bell_side` at (-5.2, 1.6, -1.2)
rotated -12 about Z. Each bell is loop (0.3 sq, y 1.30..1.70) / body (0.8 sq, y 0.50..1.35) /
clapper (0.26 sq, y 0.25..0.55). Envelope x -6.28..1.35, y 0.21..2.10, z -3.25..4.23; past
boots x+1.41 z+1.33; lowest corner y 0.21 (`bell_corner`'s clapper), well above the 0.1 floor.

**The ring's corners must not be four plates meeting flush.** The brief's "each the full span so
corners double up" would give eight coincident face planes at the corners and four shared y
planes. Following rowel_spurs' rule ("where two cubes of one part meet, make one strictly inside
the other on both axes it does not travel along") the two side plates keep the full span and full
height, and the front/back plates are inset on *both* other axes: x -5.10..1.30 so their ends die
inside the side plates' thickness, y 1.65..2.05 so the side plates overhang them by 0.05, and
z -3.22 / 3.22 so they do not reach the side plates' end planes at ±3.25. Zero coplanar faces on
the ring, and the visible offsets are a twentieth of a texel.

**"A twentieth proud" reads as a horizontal offset, not a joint.** A bell body 0.8 deep centred
on the strap's back face would reach z 2.82, *inside* the boots shell at 2.9 - so the bells cannot
straddle the strap, they hang against its outer face: body near face 0.05 proud (z 3.27 / 3.29,
x -5.20 -> outward), loop and clapper 0.05 further in again so their footprints are strictly
inside the body's and no near face is shared. The loop's top at y 1.70 still overlaps the strap's
y 1.60..2.10 as briefed, so the bell reads as hung from the strap with a 0.10 gap that is a tenth
of a texel on screen. The one nudge of the session was `modify_cube body_back` raising its top
from 1.30 to 1.35: as first placed the loop's down face and the body's up face were exactly
coplanar at y 1.3 - back-to-back, z-fighting - and the corner and side bells were built with the
0.05 overlap from the start.

**Chain arithmetic before placing, again.** Each bell's lowest corner after rotation is
`pivot_y - r*cos(θ - φ)` with r the corner's radius from the pivot and φ its angle off vertical;
worst case here is r = 1.395 at φ = 14.5 degrees, so even a 12-degree tilt lands at y 0.21. The
check confirmed all three bones to a hundredth without a single nudge. Staggering the bodies'
thicknesses (0.80 / 0.75 / 0.80 and different depths) was cheap insurance, but the three bells
sit in different bones with different rotations, so their world planes never coincided anyway.

**`!` lines accepted: none.** The finished check reports zero problems. 31 `-` notes stand, all
against greaves parts on the same bone, and all of them are the price of a ring round the ankle:
`strap` laps `swim_fins`' rays and webs on the outer flank (rowel_spurs recorded the same - that
flank is occupied from x -4.11 outward for z -2..2), and the front plate necessarily laps
`puttees`' wraps, `scale_shins`' rows, `greaves`' greave and `shin_spikes`' plate, because the
front of the ankle between z -3.22 and -3.00 is where every greaves part already is. The one
plane note - `strap and puttees:greaves's tie share the plane y = 10.35` (my y 1.65) - is marked
by the check itself as "inside the shell, so occluded". A strap that avoided all of this would not
be a strap; the brief asked for the ring and named these lappings in advance.

**Paint: two calls, 78 master faces + 66 mask faces, nothing unpainted.** Master (1 call):
`"*.*": 140`, then `[top, bottom]` pairs on the four strap plates (162->118 outer, 156->112
inner, 160->116 front/back) with lit `up` faces 188..196 and dark `down` 88..92; loops flat
148..152; the three bodies bright with a different value per side (198..234) so the cube reads
round; clappers 82..86. Guard mask (1 call): the nine bell cubes at the master's own values, so a
fitted guard keeps the bells' shading - the strap stays trim material as briefed.

What the painter did **not** cover: **a 0.8-unit cube is one texel per face, so there is no such
thing as a detail texel on it.** The brief's "one darkest texel as the slit on each body's outward
face" and the whole-face value are literally the same pixel; painting it dark would have turned
the outward side of every bell black. Instead each body's `down` face - also one texel - carries
the darkest value (60..64) as the bell's mouth, which is where the slit shadow belongs and doubles
as the briefed dark bottom face; the sides keep the bright metal. Sub-texel detail on ornaments
under about 1.5 units is simply not available, and `pixels` buys nothing there.

**Recipe.** `minecraft:bell` in a paper ring: free, and it is a block that nonetheless has a flat
inventory item texture, so no hand-drawn icon was needed. `python -m modpage build --offline`
warned `no texture for minecraft:bell`; one plain `python -m modpage build` cached it and the
next offline build is clean - the talons/flint pattern exactly.

**For the next part.** The `spurs` socket has two different neighbourhoods and they behave
oppositely: behind the ankle from z 3 outward is empty (talons' lesson, still true - every bell
hanging there is note-free), while the ring around the ankle at y 1.5..2.5 crosses *every*
greaves part there is. If a brief asks for a band, budget for a page of OVERLAP notes and check
only that no face plane coincides; if it asks for something that must stay clean, keep it behind
z 3. Sixteen other tabs were open and `armorpieces_new` made this one active without touching
them.
