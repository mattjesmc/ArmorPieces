# Brief: Dragon Wings (REWORK)

A **rework of a shipped part**, and the biggest piece in the mod. `armorpieces_dragon:dragon_wings`
was built from a qwen brief and it is a flat strip on the back (envelope bone-local `x -5.60..5.60
y -1.47..3.65 z 3.08..4.08`, reach 6.07 - eleven units across, one unit deep). The pack's owner:
*"should be grand 3D wings, the largest piece in the mod."* The datapack half is right and must
survive - it carries the pack's first effect - and geometry and sheets are rebuilt.

Open it with `armorpieces_open armorpieces_dragon:dragon_wings`. Do not create a new piece, do not
call `armorpieces_set_part`, do not touch any other tab.

## What must not change

- Id `armorpieces_dragon:dragon_wings`, name **"Dragon Wings"**, socket **`back`** only.
- **The effect stays**: `armorpieces:glide` with `sink 0.02`, `wear_interval 6`. You never call
  `set_part`, so it survives.
- Fitting **`armorpieces:inlay`** (masked - the membrane takes the player's dye), **static yes**.
  No recipe change, no loot row.
- `back` is NOT mirrored: **model both wings**, mirror-symmetric about x 0.

## The rig, in Blockbench coordinates

    body box                x -4 .. 4       y 12 .. 24      z -2 .. 2
    chestplate shell (+1)   x -5 .. 5       y 11 .. 25      z -3 .. 3
    head + helmet           x -5 .. 5       y 23 .. 33      z -5 .. 5     (a different slot: the check never mentions it)
    arms                    x +-4 .. +-8    y 12 .. 24      z -2 .. 2     (sleeve +1: to z 3, x to +-9)
    the back anchor         (0, 22, 2)

Front is negative z; **the wings go to +z and out to +-x**. Stay off the chestplate's back plane
`z 3` (and its `x +-5`, `y 25`) by 0.15 or more. **Anything above `y 23` must be at `z >= 5.25`**
to clear the helmet, and anything within `x +-9` at `y 12..24` must be at `z >= 3.2` to clear the
sleeves. The check measures the chestplate only; the helmet and sleeve lines are yours to hold.
The check's frame on the body: `check = (-bb_x, 24 - bb_y, bb_z)`.

## What it should be

**The Ender Dragon's wings, folded half-open on the back.** The dragon's wing is a thick black
bone from the shoulder, a second bone (the wing tip) hinged off it, and a purple-black membrane
stretched between - bone and membrane are the two materials. Grand means: **the wingtips reach
above the head and well outboard of the shoulders, and the wings have depth** - the bones are real
bars, the membrane is a series of plates that fan, not one flat card.

Per wing (`_l` at negative x, `_r` mirrored at positive x):

- **`wing_l`** - the root bone, pivot at the shoulder blade about `(-3.5, 21.5, 3.5)`; its cube is
  the upper arm bone, a bar about `1.2 x 1.2` in section and `12-14` long, rotated to sweep **up,
  back and out**: something like Z 35-45 degrees (out), X -20 (back) - compute the tip from the
  pivot, then confirm against the reply.
- **`wing_l_tip`** - a child bone at the end of the upper bone, the forearm/tip bar, `1.0 x 1.0`
  section, `12-16` long, folded back and down from the elbow (another 60-90 degrees about the same
  axis), ending in a small talon cube.
- **Membrane** - three or four thin plates (`0.3` thick) under the bones, each its own child bone,
  fanning from the elbow like a bat's fingers, the trailing edge scalloped by the plates ending at
  different lengths. The membrane is the `inlay` surface. Fan rule: plates rotated about one axis
  must **step along that axis** (LESSONS #29) - give each plate its own offset along the rotation
  axis (0.25 apart) so no two share a plane; the same for `_l` vs `_r`, which are mirrored and can
  never meet at x 0 - keep everything at `|x| >= 0.5`.
- A small **shoulder mount** per wing against the back, the only material surface: two cubes about
  `x +-(1.0..4.5), y 19.5..23, z 3.2..4.2`, holding the bones on.

Bone names matter: `wing_l`, `wing_l_tip`, `wing_r`, `wing_r_tip` exactly, membranes as their
children - a later animation pass will fold and flap these by rotating those four bones.

**Budget - be grand, inside this.** `x -24 .. 24, y 6 .. 38, z 3.2 .. 16` (Blockbench); check
frame `x -24 .. 24, y -14 .. 18, z 3.2 .. 16`. Reach can be 25+; there is no ceiling on a `back`
piece except that the shipped largest (`ominous_banner`, reach 17.09) is what you are meant to
beat. Pair span is whatever the tips make it. Same-socket neighbours (`cloak`, `pinions`,
`ominous_banner`, ...) are never compared; collar and belt pieces are worn with you and the check
lists them - everything of yours at `z >= 3.2` clears them.

**The sheet will not be 64x32.** Bars this long and plates this big need the plugin to grow the
canvas (it does, when it lays boxes out), likely to 128x64 or 128x128; that is fine and expected.
Keep the plate count to what the sheet can carry: 2 bones + 4 plates + 1 talon + 1 mount per wing
= 16 cubes total is the budget.

## Sheets

- **master**: the two mounts, lighter top rows, darker bottoms; every wing cube mid-grey under the
  static.
- **static**: bones black `#141018` with a lighter ridge `#302838` on their top faces, the talon
  lighter grey-black; the membrane the dragon's purple-black `#2a1a3a` with a `#5a2a8a` ->
  `#8a48c0` gradient toward the trailing edge and a bright `#c080ff` vein line along each plate's
  leading edge. Nothing on the mounts.
- **inlay mask**: the membrane plates only, shaded like their static (not flat), so a dye colours
  the membrane and the bones stay black.

Null strays on all three sheets first (`texture op:rects` with `c: null` over the whole sheet,
per sheet), then paint. Budget three paint calls per sheet and no more than eight pictures - a
piece this size needs a `fit` contact sheet (`south`, `east`, `top`) at `tile 600+` early, and
one three-quarter from behind at the end.

**Done means.** `armorpieces_save` without `force`; `python tools/check_part.py <geometry.json>
--name dragon_wings --master <pack png> --static <pack png> --mask inlay=<pack png>` clean;
`python tools/check_authoring.py packs/dragon/datapack packs/dragon/resourcepack` clean; Lessons
filled in; `armorpieces_close` last. Nothing copied into `tools/decoration_masters/`.

## Lessons from the session

Built 2026-09-14 on the kit bridge: 16 cubes, reach 28.30, envelope (check frame) `x -22.70..22.70
y -11.87..4.45 z 3.20..14.05`, sheet 64x64, saved without `force`, `check_part.py` by file and
`check_authoring.py` both clean, effect/fittings/uid untouched (no `set_part` call). ~50 calls,
three pictures.

**What it is.** Per wing: `wing_l` (pivot `(-4.75, 21.0, 3.9)`, rotation `X 25, Z 30`) holding a
1.2-section humerus 13.5 long from 0.3 below the pivot; `wing_l_tip` at the elbow (unrotated
`(-4.75, 33.95, 3.9)`, `Z 36`) holding a 1.0-section 12.25 bar; `wing_l_talon` at its end (`Z 45`,
a 0.8x0.7x1.55 hook); and four membrane plates `wing_l_web1..4` as children of the TIP bone, all
pivoted at the elbow and rotated `Z 18 / 48 / 80 / 125`, stepped 0.35 in z (3.5 / 3.85 / 4.2 / 4.55
to +0.3). Right wing is the mirror with every Z negated. Two mounts `x +-(1.05..4.45) y 19.55..22.95
z 3.2..4.15` in `base`. Elbow lands at `(-10.62, 31.17, 9.37)`, the tip bar ends near
`(-21.1, 35.3, 13.5)` - tips above the helmet, elbows at head height, wings swept ~30 degrees back
in plan.

**The helmet corner is the whole placement problem.** A `back` bone sweeping up-out from a pivot at
`x -3.5` (the brief's number) puts the humerus's inboard corners inside `x > -5.15` while already
above `y 23` - about 0.2 into the helmet box at the (x -5, y 23, z 4..5) corner, and the check is
silent about it (#21). Moving the pivot outboard to `x -4.75` and down to `y 21.0` makes every
corner cross `x = -5.15` at `y <= 22.9`. The four corners to test are the local `(+-0.6, s, +-0.6)`
offsets pushed through `Rz(Rx(v))`; the `+x,-z` corner is the one that bites (it stays inboard
longest and lowest in z).

**Rotation order is X first, then Z** (Blockbench composes `ZYX`): an up-pointing bar tilted `X 25`
then swung `Z 30` keeps its full 25-degree backward lean and swings out in the tilted plane. Direction
of a unit bar = `(-cosX sinZ, cosX cosZ, sinX)`; the reply's envelope matched this to 0.01. Positive X
tilts an upright bar BACK (+z) - the brief's `X -20` had the sign the other way; I took the sign the
envelope confirmed.

**Child-bone angles compose in the parent's tilted frame.** A plate rotated `delta` about Z inside the
tip bone sits at `phi = delta + 36` from the humerus axis, in the humerus's plane; its world direction
is `(0.866a - 0.453b, 0.5a + 0.785b, 0.423b)` with `a = -sin phi, b = cos phi` (for X 25 / Z 30). Local
`+x` of the rotated plate points toward SMALLER delta - toward the leading bar - so a chord placed on
the `+x` side of the pivot line (left wing) laps the previous plate and the fan closes from the root out.

**Fan geometry that reads as a membrane, not a hub.** Radial plates pivoted at one point stick their
root corners out past the leading bar if they start at the pivot. Start each plate a few units out
(s = 4 / 3.5 / 2.5 / 2) and put the WHOLE chord on the leading side (3.0 / 4.5 / 5.5 / 5.5; the last
plate gets 1.5 on the trailing side too, toward the humerus); the root corner then lands inside the
bar or under the previous plate. Test: root corner angle `atan2` vs the previous plate's radial, and
its `(t, c)` coordinates in the previous plate's frame must fall inside that plate's rectangle. The
fan closes to `r = chord / sin(step)` and is scalloped beyond - the ragged trailing edge is free.

**Unrotated plate cubes may cross x 0.** web3/web4's chords reach `x +0.75` in the straight pose on
the left wing; the rotated result is at `x <= -8` and that is all the check measures. No warning.

**Sheet grows on resize, and the layout moves.** Widening six plates re-laid them (64x32 -> 64x64);
a second full null sweep of all three sheets (now 64x64 - read `list_textures` for the size first) and
a full repaint was cheaper than subtracting. Two sweeps, two paints per sheet in total.

**Vein columns.** Box-UV `north` has its column 0 at the cube's `+x` edge (`to.x`), `south` column 0
at `-x` (`from.x`) - so the leading-edge vein is `north` column 0 / `south` last column on the left
wing and the reverse on the right. Verified in the saved PNG with Pillow.

**`armorpieces_save` narrated `dragon_mask`** (another tab had gone active in the window) and refused
on that piece's problems; nothing was written. `armorpieces_open` on my own piece, then `save` again,
went through.

Notes left standing (all `-`): OVERLAP/near hull tests against `ruff` and `scarf` (collar), at the
mounts and the humerus roots - the same lines the flat strip had.
