# Brief: Tusks

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the ninth
batch of four (read cheek_guards.md, ears.md and aerials.md first - the head frame, the empty
jaw zone below y 27.7, rotation signs on the negative-x side - and talons.md for a curling
chain). From the `horns` row of `docs/plans/part-variety.md`:

> **Tusks** - Short thick tusks curving up from the jawline. Theme: Beast. Fittings: none.

The plan lists no fitting; this brief puts the ivory on a static layer so the tusks stay bone
white whatever the material, and gives the metal ferrule at the root a `guard` mask, the way
the talons' heel cap works.

**Part.** `armorpieces:tusks`, socket `horns` only, in the mod's own pack. Display name "Tusks".
Fittings: `armorpieces:guard`, one mask, covering the ferrule only. Static layer (`static:
true`) for the three tusk segments. No effects, no loot.

**Shape.** `horns` is a mirrored socket on the head bone: model ONE side, the LEFT, at NEGATIVE
x. The head box is x -4..4, y 24..32, z -4..4 (pivot 0, 24, 0); the helmet shell is that box
inflated a full unit, x -5..5, y 23..33, z -5..5; the left temple anchor is at Blockbench
(-4, 29, 0). "Outboard" is more negative x. Read the envelopes in the `armorpieces_new` reply:
the jaw zone (y 24..27.7 outboard of x -5) is empty of every other socket; above y 27.75 the
brow bands (circlet to x ±6, laurel and browband at the same temples) and the coronet
(y 29..33.21 forward of z -2.25, to x ±6) are what a tusk curving up and forward meets - keep
the tip inboard of x -6.1 and below y 29.5, or say what it laps. Build: a `ferrule` bone with a
ferrule cube 1.5 square, 0.6 tall, straddling the shell's side plane at x -5.6..-4.6 (half
buried), y 25.4..26.0, z -1.0..0.5 - the metal socket the tusk grows from; under it a chain of
three bones, each with one cube modelled straight UP from its pivot, 1.2 / 1.0 / 0.8 square in
section and 1.8 / 1.6 / 1.4 long, each starting a quarter unit before its parent's end, the
whole chain leaning OUTBOARD by a constant 12 degrees about Z (positive Z tips an upright's top
toward -x on this side - ears) and curling FORWARD by cumulative -20 / -45 / -70 degrees about X
(a negative X rotation tips an upright toward -Z - horsetail's rule reversed). Blockbench
composes a bone's Euler as Rz then Rx on the local vector (spiked_pauldrons measured it), so
compute the tip before placing; it should land near x -6.0, y 28.8, z -3.4. Nothing below
y 25.2.

**Sheets.** Master: ferrule bright metal with a dark underside and a brighter top row; the
segments mid grey `[top, bottom]` lighter toward the tip (the master still supplies the
silhouette under the static). Static layer: the three segments only, ivory `[#efe6d2, #d9cdb0]`
with a `#c4b795` root row on the first segment and a brighter `#f7f1e3` tip face. Guard mask:
the ferrule's faces only, shaded like the master.

**Recipe.** Centre item `minecraft:porkchop` (a flat item, unused by any template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py tusks`
and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons paragraph below
filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-03 in 27 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`armorpieces_part`, 1 `list_outline`, 5 `add_group`, 5 `place_cube`, 4 `remove_element`,
2 `armorpieces_check`, 1 `armorpieces_set_part`, **3 `armorpieces_paint`** (one per sheet),
2 `set_camera_angle`, 1 `armorpieces_save`. No `risky_eval`, no `modify_cube`, nothing
hand-edited; the save went through first time **without `force`**, and `check_part tusks`,
`check_authoring` and the page build were clean on the first run.

**What I built.** An unrotated `ferrule` bone (pivot -5.1, 25.7, -0.25) with `ferrule_ring`
x -5.85..-4.35, y 25.4..26.0, z -1.0..0.5, and **three sibling bones under it** - `tusk1`
(pivot -5.1, 25.75, -0.25, rotation X -20 Z 12, cube 1.2 square x 1.8 long), `tusk2`
(-5.4223, 27.1747, -0.7685, X -45 Z 12, 1.0 x 1.6), `tusk3` (-5.6208, 28.1084, -1.7231,
X -70 Z 12, 0.8 x 1.4), each modelled straight up from its own pivot and starting a quarter
unit before its parent's end. Final envelope Blockbench x -6.22..-4.35, y 25.40..29.03,
z -3.18..0.50; tip axis (-5.72, 28.58, -3.04); pair spans 12.44, well inside the shoulders'
18. Nothing below y 25.40 and the top is 0.47 under the brief's y 29.5 ceiling.

**The one number in the brief I changed: the ferrule's width.** The brief calls it "1.5 square,
0.6 tall" but then gives x -5.6..-4.6, which is 1.0 wide - and the root segment is **1.2** wide,
so that ferrule would have had the tusk bursting 0.1 through each side. I resolved the brief
against itself in favour of the stated size: x **-5.85..-4.35**, same centre, genuinely 1.5 x 0.6
x 1.5, wrapping the root with 0.15 to spare, still straddling the helmet shell's x -5 plane
(0.85 proud, 0.65 buried). The buried east face is painted anyway, as antennae warned.

**The Euler order the brief states is the reverse of what Blockbench does, and the check settles
it in one call.** The brief says "Blockbench composes a bone's Euler as Rz then Rx on the local
vector"; the actual matrix is **Rz . Rx**, i.e. the X curl acts on the local vector *first* and
the Z lean then tips the whole rotated segment. The two are not the same once both angles are
non-zero, and the difference is measurable: predicting with Rx.Rz gave envelope x -6.385,
y 28.981, z -3.204, while the check printed x -6.27, y 29.03, z -3.155 - exactly the Rz.Rx
prediction, to the hundredth. **Rule: for a bone with rotation [ax, 0, az], world direction of a
local +Y segment of length L is L * ( -cos(ax) sin(az), cos(ax) cos(az), sin(ax) ).** (Check it
with a chain of two - one segment cannot distinguish the orders when the pivots are on the axis.)

**A chain that leans *and* curls has to be siblings, not nested.** Rotations about different axes
do not add, so a child bone cannot be given the local increment (-25 X) and still land on the
cumulative -45: `Rx(-20)Rz(12) . Rx(-25)` is not `Rx(-45)Rz(12)`, and the correcting local
rotation `Rz(-12)Rx(-25)Rz(12)` is not expressible as one Z-then-X Euler. So all three segments
hang **flat under `ferrule`**, each carrying its own absolute pair (Z 12 constant, X -20/-45/-70
cumulative), with each pivot placed at the *world* point where the previous segment ends. This
is the difference from talons and aerials, whose chains were pure single-axis and could nest.
It cost one rebuild: `tusk3`'s pivot, computed under the wrong order, sat **0.107** off the
axis of `tusk2` (a visible kink at the joint), so the cube and the bone were removed and re-added
at (-5.6208, 28.1084, -1.7231) - `remove_element` on a cube then on its group works fine, and
`add_group` by parent NAME never misbehaved.

**`!` lines accepted: none** - the finished check reports zero problems. Eleven `-` notes stand
and five are OVERLAPs, all with the two brow bands: `tusk2`/`tusk3` into `circlet`'s band (up to
1.14 x 0.73 x 1.84), `tusk1`/`tusk2` into `browband`'s tail, `tusk3` into `browband`'s band. **The
real cubes do meet, and it is unavoidable on this socket.** A tusk rooted at the jaw (y 25.4) and
long enough to read has to climb through y 27.75..29.0 at the temple, and `circlet` (x -6..6,
y 27.75..30.75) and `browband` (x -6.48..5.5, y 26.6..30.1) own that whole shell of the head
ring; the only escapes were to stop the tusk at 1.5 units long or to lean it past 30 degrees,
both of which throw away the brief's shape. Nothing is **coplanar** (the check names no shared
plane - once a bone is rotated 12/20 degrees none of its face planes is axis-aligned, so nothing
can z-fight), and a brow band crossing *over* a jaw fixture is how it would be worn, exactly the
argument cheek_guards recorded for its rivet. The last note - `tusk3 clears coronet's band by
0.02 in y` - is a genuine miss, not a touch: the top corner is 28.98 against coronet's 29.00.

**Three paint calls, and they covered everything** (0 unpainted faces, no stray paint, no colour
on a greyscale sheet; Pillow confirms master 60 opaque texels 100..255 all grey, guard mask 16
texels 105..255 all grey, static 44 texels inside the master's silhouette). Master (24 faces,
66 writes, 2 pixels): `*.*` 150, ferrule 200 with `up` 235 / `down` 105 / `east` 170 (buried
side) / `west` 210, then a per-segment step 150 -> 178 -> 208 with `[top, bottom]` pairs and the
tip's `up` at 238. Static (24 faces + 8 pixels): the three segments only, `[#efe6d2, #d9cdb0]`
warming per segment, `#c4b795` on the root's `down`, `#f7f1e3` on the tip's `up`. Guard mask (12
faces + 2 pixels): the ferrule's six faces at the master's own values, so the fitting takes the
shading rather than a flat fill; the ivory segments carry no mask and no material.

What the painter did **not** cover: **the "root row" of the brief is not a face, so it had to be
`pixels`.** `tusk_root`'s four side faces are 2x2 texels laid at 20,2 / 22,2 / 24,2 / 26,2, so
their bottom row is the single scanline **y = 3, x 20..27** - eight texels, painted `#c4b795`
after the `[top, bottom]` pairs (later entries win). The same trick is the only way to get any
band that runs *around* a cube: face addresses cannot reach a row. And `[top, bottom]` pairs
earn their keep here on every segment (all the side faces are 2 rows tall) but are dead on the
up/down caps, which are 2x2 or 1x1 - the tip's "brighter face" is literally its 1x1 `up` texel.

**For the next part.** `minecraft:porkchop` is taken as a template centre; `--offline` warned it
had never been cached, one plain `python -m modpage build` fetched it and reported `unchanged`,
and the next offline build was clean - the same three-build dance the last five sessions found,
94 recipes now. On `horns`, the jaw zone below y 27.7 really is empty (cheek_guards was right)
but it is only **2.5 units tall**: anything that wants length has to climb into the brow ring and
accept the overlap notes, so budget the argument rather than the geometry. And when a bone needs
two angles, predict with **Rz . Rx** and place the chain flat.
