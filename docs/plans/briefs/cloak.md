# Brief: Cloak

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the eleventh
batch (read bedroll.md, carapace.md and spine_ridge.md first - the back frame, the belt-line
neighbours, and that `sash` reaches up the back to y 16.5). From the `back` row of
`docs/plans/part-variety.md`:

> **Cloak** - A cape falling from the shoulders to mid-thigh. The obvious hole. Wider and longer
> than the banner's hanging cloth, and it should take a banner's design the same way. Theme:
> Court. Fittings: `banner`, `guard` (the clasp).

**Part.** `armorpieces:cloak`, socket `back` only, in the mod's own pack. Display name "Cloak".
Fittings, in this order: `armorpieces:banner` and `armorpieces:guard`. No effects, no loot, no
static layer.

**The banner fitting is geometry, not a mask.** `armorpieces:banner` is the shared fitting the
shipped Banner part uses: it takes `bone: "banner"`, `sheet: "shield"`, `front: "south"`, finds
the bone named exactly **`banner`** in your geometry, and stretches the chosen shield pattern
over every face of its cubes (each face edge to edge, whatever the cube's size), with the
`south` face carrying the design the right way round. So: put the cape's cloth cubes in a bone
named `banner`, keep that bone's cubes plain boxes with their broad faces facing ±z, and give
the part no `part_banner` mask sheet - `armorpieces_set_part` creates mask sheets only for
masked fittings, and this one is not masked. The `guard` fitting IS masked and needs its
`part_guard` sheet for the clasp. Paint the master under the cloth anyway: the part's own pass
draws first and the banner draws over it.

**Shape.** `back` is not a mirrored socket: model the whole thing on the body bone. The torso
box is x -4..4, y 12..24, z -2..2 (pivot 0, 24, 0); the chestplate shell is that box inflated a
full unit, x -5..5, y 11..25, z -3..3, and the anchor is at Blockbench (0, 22, 2). Anything with
z under 3 is buried. Read the envelopes in the `armorpieces_new` reply: same-socket parts are
never compared; the belt parts share the bone (sash to y 16.5 at z 1..4, buckled_belt to 15.5,
girdle to 14.25) and the collar parts are in front, so a cape hanging past y 16.5 laps the sash
- accept it and say by how much, but dodge every listed plane by a twentieth. Build: a `yoke`
bone at the anchor with a shoulder bar x -5.5..5.5, y 23.6..24.6, z 3.1..3.7 (the cape's
collar, a tenth off the shell), and a clasp plate on its front centre x -1.2..1.2,
y 23.5..24.7, z 2.9..3.15 - the clasp sits over the shoulders where a cape is pinned, its back
face buried inside the shell; then the `banner` bone, a child of `yoke` pivoted at (0, 23.6,
3.4) and rotated 4 degrees about X so the cloth hangs a little away from the back at the hem
(for a plate hanging BELOW its pivot, a negative X rotation swings the free end toward +z, away
from the body - browband measured it), carrying ONE cloth cube x -5.5..5.5, y 9.6..23.7,
z 3.35..3.65 (14.1 tall, 11 wide, a third of a unit thick - the cape). One cube keeps the
banner's UV stretch clean: the pattern is remapped face by face, so a cape made of several
cubes would repeat the design on each. Nothing below y 9.5, nothing wider than x ±5.6.

**Sheets.** Master: cloth mid grey `[top, bottom]` a little darker toward the hem, with a
darker single row at the very bottom as the hem's shadow and a lighter row at the top where it
gathers under the yoke (`pixels`); yoke bar a step lighter with a bright top face; clasp
brightest with a dark underside. Guard mask: the clasp's faces only, shaded like the master.

**Recipe.** Centre item `minecraft:purple_wool` (a block with a flat texture, unused by any
template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py cloak`
and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons paragraph below
filled in. Count your paint calls, say what the painter did and did not cover, and say what the
`banner` bone needed that a masked fitting would not.

## Lessons from the session

Built 2026-09-04 in 20 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`armorpieces_part`, 1 `list_outline`, 2 `add_group`, 2 `place_cube` (bar+clasp together, then the
cloth), 2 `remove_element` (starter cube, then its bone), 1 `armorpieces_check`, 1
`armorpieces_set_part`, **2 `armorpieces_paint`**, 1 `modify_cube`, 4 `set_camera_angle`, 1
`armorpieces_save`. No `risky_eval`, nothing hand-edited, and the save went through first time
without `force` - the check read `ok: nothing needs a decision` before it.

**What I built.** Two bones. `yoke` at the anchor (0, 22, 2), unrotated, with `bar`
x -5.3..5.3, y 23.6..24.6, z 3.1..3.7 (the cape's collar, a tenth off the chestplate's back
plane) and `clasp` x -1.2..1.2, y **23.35..24.85**, z 2.9..**3.9**. Its child `banner`, pivot
(0, 23.6, 3.4), rotation **-4** about X, carries the one cube `cloth` x -5.45..5.45,
y 9.6..23.7, z 3.35..3.65. Envelope (Blockbench) x ±5.45, y 9.63..24.85, z 2.90..4.63; reach
13.75, past the chestplate x+0.45 y+1.37 z+1.63. Data: `back` only, fittings
`armorpieces:banner` then `armorpieces:guard`, no effects, no loot, no static layer; recipe
`minecraft:purple_wool` in a paper ring.

**Two places I changed the brief's numbers, both for a reason the numbers themselves give.**
1. *The clasp as briefed is invisible.* z 2.9..3.15 puts the whole plate **behind** the yoke
   bar's front face (the bar runs z 3.1..3.7), so the only thing that would ever show is the
   0.1 of clasp standing above and below a 1.0-tall bar. I kept the buried back face at z 2.9
   (inside the shell, as intended) and pushed the front to 3.9 - 0.2 proud of the bar - and
   after a screenshot also grew it in y to 23.35..24.85, 0.25 proud top and bottom. It now reads
   as a 2.4 x 1.5 plate pinned on the shoulder bar at three metres, which matters because the
   clasp is the entire `guard` fitting: everything else on this part is cloth.
2. *Bar and cloth cannot share a width.* The brief gives both x ±5.5. Rotation about X leaves
   the x extent alone, so the tilted cloth still has hard planes at x = ±5.5 - and it overlaps
   the bar at the shoulder, which would have been a self-COPLANAR pair inside my own part;
   ±5.5 is also `buckled_belt`'s and `chain_belt`'s own x plane. Split them: bar ±5.3, cloth
   ±5.45. Neither value appears in any other `body` part's envelope (the near misses are
   bandolier 5.47, buckled_belt/chain_belt 5.5, cord/scarf 5.6, girdle 5.86). The finished check
   has not one COPLANAR line.

**`!` lines accepted: none.** 22 `-` notes stand, and they are all one fact: a cape long enough
to reach mid-thigh lies over every belt. The cloth's front face crosses z 4 at about y 14.3, so
it is inside `sash`'s band (x ±5.5, y 13.5..16.5, z 1..4) only between y 14.3 and 16.5 - the
check calls that lap **0.66 deep** (10.90 x 3.00 x 0.66 against the sash hull) - and below y 14.3
the 4-degree tilt has carried it clear. The rest: `pouch_belt`'s pouch_back 1.16 deep (that pouch
reaches z 5.0, so the cape passes *through* it - no cape that hangs flat can dodge a backpack),
`girdle` 0.52 at its rear corners and 0.16 on its back plate, `buckled_belt` / `chain_belt` /
`cord` 0.16..0.26, and at the top `scarf`'s wrap 0.21..0.50 against the yoke and the cloth's
gather. None of them is a shared plane: the cloth lives in a rotated bone and therefore has **no
axis-aligned y or z plane at all**, which is the same clash insurance spine_ridge recorded. Two
`near` lines (banner clears pouch_back by 0.02 in z, girdle's flanks by 0.09) are the same story
measured from outside.

**What the `banner` bone needed that a masked fitting would not.** Three things, none of which
the check can tell you: (a) the bone must be named exactly `banner` - the fitting definition
(`src/main/resources/data/armorpieces/armorpieces/fitting/banner.json`) hardcodes
`bone: "banner"`, `sheet: "shield"`, `front: "south"`, so the name is the whole binding and
`rename_element` cannot rename a group - get it right in `add_group` or rebuild the bone.
(b) **One cube.** The pattern is remapped edge to edge on *every face of every cube* in that
bone, so a second cloth cube would print a second copy of the design; the cape is a single
10.9 x 14.1 x 0.3 slab, and its broad faces face ±z with `south` outward so the charge is the
right way round. (c) `armorpieces_set_part` created **only** `part_guard` - `armorpieces:banner`
is `masked: false`, so there is no `part_banner` sheet to paint and none is wanted. The master
still has to carry the cloth: the part's own pass draws first and the shield pattern draws over
it, so the unpainted-face check counts those faces exactly as if there were no fitting.

**Paint: two calls, and the second one is six faces.** Call 1 (master): `"*.*": 120` then all 18
faces by name - cloth `south` [152, 96] and `east`/`west` [142, 90] (the `[top, bottom]` pair is
a vertical ramp, which is exactly the "darker toward the hem" the brief wanted), `north` flat 88
(against the body, never seen), `up` 168, `down` 58; bar a step lighter (`south` [204, 154],
`up` 228, `down` 72, sides [190, 148], `north` 96); clasp brightest (`south` [246, 202], `up`
252, sides [232, 188], `down` 58, `north` 90) - plus **26 `pixels`**: the top row of the cloth's
`south` rectangle (33..43 at y 3) at 190 as the gather under the yoke, its bottom row (y 17) at
60 as the hem shadow, and the matching single texels on the two 1x15 edge strips. Call 2
(`part_guard`) repeats the clasp's six values and nothing else, so the clasp takes the metal and
the cloth stays trim material. What the painter did **not** cover: the two hard rows. A
`[top, bottom]` pair ramps smoothly over a whole face and can never make a one-texel step, so
gather and hem had to be enumerated - 11 texels each, read straight off the sheet-layout block
(`cloth.south 33,3 11x15`). Nothing else on this part is smaller than a face.

**For the next part.**
- `minecraft:purple_wool` is now taken. Flat block texture, no icon work; `--offline` warned it
  had never been cached, one plain `python -m modpage build` fetched it, the repeat offline build
  is silent and the three pages came back `unchanged` (only the icon changed).
- A cape is the widest thing on the `back` bone that hangs: expect a wall of OVERLAP notes from
  every `belt` part and from `scarf`, and expect them to be harmless *because the cloth is
  tilted*. If you ever build a hanging plate on an unrotated bone down there, you will collect
  real COPLANAR lines against sash z=4, girdle z=3.86, cord z=3.6 and the belts' z=3.5 instead.
- The 4-degree tilt costs the hem 0.98 in z (bottom at z 4.33..4.63 from a pivot at 3.4) and
  0.03 in y. Anything else on `back` that wants the volume behind the knees-to-belt strip should
  read those two numbers before assuming a cape stays flat against the shell.
- Screenshot from +z: the player faces -z, so a `back` part is invisible from the default camera.
