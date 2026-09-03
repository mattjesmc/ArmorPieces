# Brief: Spiked Pauldrons

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the seventh
batch of four, a Knightly set (read wing_cases.md and epaulettes.md first - the arm frame, the
head's sweep, the Z sign - and talons.md for chains). From the `pauldrons` row of
`docs/plans/part-variety.md`:

> **Spiked Pauldrons** - Heavy domes with three spikes each, brutal. Theme: Knightly. Fitting:
> `guard`.

**Part.** `armorpieces:spiked_pauldrons`, socket `pauldrons` only, in the mod's own pack.
Display name "Spiked Pauldrons". Fittings: `armorpieces:guard`, one mask, covering the three
spikes; the dome stays the material. No effects, no loot, no static layer.

**Shape.** `pauldrons` is a mirrored socket riding the arm: model ONE arm, the LEFT, at NEGATIVE
x. The arm box is x -8..-4, y 12..24, z -2..2 (pivot -5, 22, 0); the chestplate's arm shell is
that box inflated a full unit, x -9..-3, y 11..25, z -3..3, and the anchor is at Blockbench
(-6, 22, 0). Two hard limits: nothing inside the shell shows, and a turned head sweeps
everything above y 23 inboard of x -7.1. Read the envelopes in the `armorpieces_new` reply for
the other pauldrons parts (never compared) and the vambraces parts lower on the bone. Build a
`dome` bone at the anchor carrying the dome as two cubes: a cap over the shoulder x -9.7..-7.2,
y 25.1..26.4, z -3.1..3.1, and a skirt down the outside of the arm x -9.85..-9.2, y 22.4..25.2,
z -3.1..3.1 (its top a tenth inside the cap, no shared plane). Then three spikes, each its own
bone pivoted on the cap's top at (-8.45, 26.4, -1.9), (-8.45, 26.4, 0) and (-8.45, 26.4, 1.9),
each a chain of two cubes modelled straight UP from the pivot: a base 0.8 square by 1.5 tall
starting a tenth inside the cap (y 26.3), then a tip 0.45 square by 1.1 tall in a child bone
starting a quarter unit before the base's end. Every spike bone leans OUTBOARD 25 degrees about
Z (for an upright above its pivot on the negative-x side a POSITIVE Z rotation tips the top
toward -x - ears confirmed it), and the front and back spikes also fan 20 degrees about X
(the front one tipping toward -Z, the back one toward +Z; a positive X rotation tips an upright
toward +Z - horsetail). Compute the tips before placing: they should land around x -9.6,
y 28.6, z -2.8 / 0 / 2.8. Nothing above y 28.8.

**Sheets.** Master: dome mid `[top, bottom]` with a bright top face on the cap and a dark
underside, the skirt a step darker with a bright top row (`pixels`); spikes bright metal
lighter toward the tip, tip end faces brightest, dark undersides. Guard mask: the six spike
cubes' faces only, shaded like the master.

**Recipe.** Centre item `minecraft:iron_chestplate` (a flat item, unused by any template), paper
ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
spiked_pauldrons` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

Built 2026-09-03 in 24 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 7 `add_group`,
7 `place_cube`, 1 `remove_element`, 1 `list_outline`, 1 `armorpieces_check`, 1
`armorpieces_set_part`, 2 `armorpieces_paint`, 1 `set_camera_angle`, 1 `armorpieces_save`, plus
the two repo checks and the page build. No `risky_eval`, no `modify_cube`, no nudging, no
hand-edited file, and the save went through first time without `force`.

**What I built.** Exactly the brief's numbers, nothing moved. `dome` (pivot -6, 22, 0,
unrotated) carries `cap` x -9.7..-7.2, y 25.1..26.4, z -3.1..3.1 and `skirt` x -9.85..-9.2,
y 22.4..25.2, z -3.1..3.1. Three spike bones on the cap's top at (-8.45, 26.4, -1.9 / 0 / 1.9),
each with `*_base` 0.8 square from y 26.3 to 27.8 and a child bone `*_tip` (pivot at
(-8.45, 27.55, z0), rotation 0 - it is only a container, the segment is straight) carrying
`*_pt` 0.45 square from y 27.55 to 28.65. Rotations `spike_f [-20,0,25]`, `spike_m [0,0,25]`,
`spike_b [20,0,25]`. Final envelope Blockbench x -9.85..-7.20, y 22.40..28.53, z -3.10..3.10;
reach 7.65; past chestplate x+0.85 y+3.53 z+0.10. Nothing above y 28.53 (limit 28.8), nothing
above y 23 is inboard of x -7.2 (limit -7.1), and the whole part is outboard of the shell's
x -9 plane wherever it is below the shell's y 25 top.

**Rotation order, measured.** Blockbench composes a bone's Euler as **R = Rz . Rx** - the X
rotation is applied to the local vector first, then Z. With (0, L, 0) as the segment axis the
end lands at pivot + (-L sin z cos x, L cos z cos x, L sin x) for a +Z / +X pair. The check's
bone-local `spike_f_tip at (3.91, -5.38, -2.29)` matched that formula's (-8.907, 27.379, -2.293)
to a hundredth and ruled out the other order (which predicts z -2.256), so the placement was
confirmed before any cube went in. Tip axis ends: x -9.34, y 28.32, z -2.67 / 0 / +2.67 - a
little shy of the brief's "around -9.6 / 28.6 / 2.8", which are the corner extremes, not the
axis.

**The `!` I accepted: none.** The only `!` that ever appeared was the standing "faces have no
paint behind them", cleared by the two paint calls. The finished check has one `-` note, `pair
spans 19.70 across the figure, over the 18 the shoulders span` - every pauldrons part that sits
outboard of x -9 gets it, and 19.70 is exactly epaulettes' span (the skirt's x -9.85 sets it,
not the spikes, which lean back in to x -9.6). The five vambraces parts on the bone are `all
clear by more than half a unit`: this part lives entirely above y 22.4 and the highest vambraces
part (claws) tops out at y 18.2.

**Painting: two calls, one per sheet, and they covered everything** - 48 master faces + 9 pixels,
36 mask faces, zero unpainted, no stray paint, no colour on a greyscale sheet. Master: `*.*: 140`
as the base, then `cap.*: [165,125]` with `cap.up: 205`, `cap.west: [185,135]` (west is the
outboard face on this rig), `cap.east: 95` and `cap.down: 60`; `skirt.*: [125,90]` a step darker
with `skirt.west: [140,100]`, `skirt.up: 150`, `skirt.down: 55`; the spikes as two bright steps,
bases `[195,150]` (up 210, down 70) and tips `[240,200]` with `up: 255` as the brightest end
face. The mask repeats the six spike cubes' master values verbatim - a shaded mask, like every
other in the pack, because the mask is the spike's position on the guard material's ramp and a
flat one would flatten the lit tip.

What the painter did NOT cover: the skirt's bright top row. A `[top, bottom]` pair shades a whole
face, so the one-texel rim went in as the same call's `pixels` list - x 19..27 at y 7, 215, which
is the top row of the skirt's `north` (19,7 1x3), `west` (20,7 7x3) and `south` (27,7 1x3) faces
in one contiguous run because the plugin laid those three faces out side by side. Read that run
off the `sheet layout` block rather than assuming it; it only works when the faces happen to be
adjacent.

**For the next part.**
- `remove_element main` took the starter bone with it this time - `list_outline` showed no
  leftover `base` group and a second `remove_element` errored with "not found". Check the outline
  before deleting the bone rather than assuming two calls.
- A 0.8-unit cube unwraps to 1x2 texels and a 0.45-unit one to 1x1 sides with a 1x1 cap, so a
  spike's whole shading budget is the per-cube step plus its `up` face. Anything finer than
  "base grey, tip grey, white cap" is invisible; spend the detail on the dome instead.
- Cap and skirt were deliberately given a 0.1 vertical overlap (skirt top 25.2 inside the cap's
  25.1..26.4) and every spike base starts 0.1 inside the cap: no shared plane appeared anywhere,
  so a tenth is enough on a static joint (a quarter is for rotated ones).
- `minecraft:iron_chestplate` was free as a template centre and already cached: `python -m
  modpage build --offline` ran clean with no "no texture" warning, unlike the raw-ore centres the
  earlier sessions picked.
