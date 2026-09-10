# Brief: Boot Cuffs

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the eighth
batch of four (read thigh_sheath.md, padding.md and loin_panels.md first - the leg frame and
the planes the knees and tassets parts already use). From the `greaves` row of
`docs/plans/part-variety.md`:

> **Boot Cuffs** - A folded-over cuff at the top of the boot, flaring out. Theme: Wayfarer.
> Fitting: `inlay`.

**Part.** `armorpieces:boot_cuffs`, socket `greaves` only, in the mod's own pack. Display name
"Boot Cuffs". Fittings: `armorpieces:inlay`, one mask, covering the fold (the lining that shows
when a boot top is turned down); the cuff ring under it stays the material. No effects, no loot,
no static layer.

**Shape.** `greaves` is a mirrored socket on the leg bone: model ONE leg, the LEFT, at NEGATIVE
x. The leg box is x -3.9..0.1, y 0..12, z -2..2 (pivot -1.9, 12, 0); the boots shell is that box
inflated 0.9 (x -4.8..1.0, z ±2.9); the anchor is at Blockbench (-1.9, 4, -2). Read the
envelopes in the `armorpieces_new` reply: the knees parts on the front reach up to y 8.3
(poleyns) and use the planes z -2.65 / -2.95 / -3.0 / -3.45 / -3.5 / -3.62; the tassets parts
hang to y 5.18 (tassets), loin_panels' strips at z -3.15..-2.75 and 2.75..3.15 down to 5.4,
thigh_sheath's upper strap ring at y 7.8..8.3 (z ±2.5..±2.75); the spurs parts are at the
ankle. A cuff ring at y 8.5..9.7 clears the knees crowd above y 8.3 and dodges the loin panels'
planes if its faces sit at z ±3.05..±3.3 - it will still lap the tassets hulls (the socket's
norm; say by how much). Build a `cuff` bone with a ring of four plates a quarter thick and 1.2
tall at y 8.5..9.7 a tenth off the boots shell (outer x -5.15..-4.9, inner x 1.1..1.35, front
z -3.3..-3.05, back z 3.05..3.3, each the full span so corners double up) - the boot's top. Then
the fold: four bones `fold_out` / `fold_in` / `fold_front` / `fold_back`, each pivoted on the
cuff ring's top edge at the middle of its side and carrying a plate 0.3 thick and 1.1 tall
hanging DOWN from y 9.8 to y 8.7 (lapping the ring's top by a tenth, standing 0.1 proud of it),
the bone rotated 12 degrees about the axis along its plate so the fold's bottom edge flares
OUT from the leg (for a plate hanging below its pivot on the outer side, a positive Z rotation
swings the free end toward +x, i.e. INTO the leg - pendant and cheek_guards measured it - so
the outer fold wants NEGATIVE Z, the inner fold positive Z, the front fold positive X (below
the pivot, +X swings toward -Z) and the back fold negative X; confirm each on its reply).
Nothing above y 9.9, nothing below 8.4.

**Sheets.** Master: cuff ring mid grey `[top, bottom]`; fold plates a step lighter (the
lining) with a bright bottom row as the turned edge (`pixels`) and a darker top row where it
meets the ring. Inlay mask: the four fold plates at the same values, the ring left out.

**Recipe.** Centre item `minecraft:leather_boots` (a flat item, unused by any template), paper
ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
boot_cuffs` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

**Built 2026-09-03 in 20 bridge calls**: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`list_outline`, 2 `remove_element` (starter cube, then its bone), 5 `add_group`, 5 `place_cube`
(8 cubes), 4 `modify_cube`, 1 `armorpieces_check`, 1 `armorpieces_set_part`, **3
`armorpieces_paint`**, 3 `set_camera_angle`, 1 `armorpieces_save`. No `risky_eval`, nothing
hand-edited; the save went through first time without `force`.

**What I built.** Five bones under `part`: `cuff` at (-1.9, 9.7, 0) unrotated with the four ring
plates, and `fold_out` (-5.2, 9.7, 0) rot **[0,0,-12]**, `fold_in` (1.35, 9.7, 0) rot
**[0,0,+12]**, `fold_front` (-1.9, 9.7, -3.25) rot **[+12,0,0]**, `fold_back` (-1.9, 9.7, 3.3)
rot **[-12,0,0]**, each with one plate. Ring: `ring_out` (-5.2, 8.5, -3.25)..(-4.95, 9.7, 3.3),
`ring_in` x 1.1..1.35, `ring_front` z -3.25..-3.0, `ring_back` z 3.05..3.3, the last two spanning
x -5.2..1.35 so the corners double up. Folds: 0.3 thick, y 8.7..9.8, `fold_out_plate` x
-5.3..-5.0, `fold_in_plate` x 1.15..1.45, `fold_front_plate` z -3.35..-3.05, `fold_back_plate`
z 3.1..3.4, the side plates spanning z -3.25..3.3 and the front/back ones x -5.2..1.35. Envelope
Blockbench **x -5.51..1.66, y 8.50..9.82, z -3.56..3.61**; reach 8.58, past boots 0.71 in x and
z. Nothing above 9.9, nothing below 8.4, as briefed. Data: `greaves` only, fitting
`armorpieces:inlay`, no effects/loot/static, recipe `minecraft:leather_boots` in a paper ring.

**All four rotation signs confirmed on their own reply, from `past boots`.** The brief's hedge is
right and the reading is free: place one fold, read `past boots x/z`. `fold_out` at -12 about Z
took `past boots x` 0.40 -> **0.71** (the free end swung to -x, outboard); `fold_in` at +12 left
that number alone (its own flare is 0.656, under the outer's 0.71); `fold_front` at +12 about X
took `past boots z` 0.40 -> **0.66** (toward -Z, forward); `fold_back` at -12 took it to
**0.71**. So on this rig: below the pivot, **negative Z swings to -x, positive Z to +x, positive
X to -z, negative X to +z** - the same measurement thigh_sheath and loin_panels made for X, now
also for Z. Arithmetic that matched to a hundredth: for a plate hanging `h` below the pivot and
`d` proud of it, the free corner moves `h*sin|a| + d*cos a` sideways and rises
`d_top*sin|a|` above the pivot (top corner at y 9.82 for a plate whose top is 9.8).

**Two `!` COPLANAR problems, both fixed by moving faces; `!` lines accepted at save: none.**
The briefed ring drew `cuff and pelt:tassets's pelt share the plane z = -3.3` and `cuff and
thigh_sheath:tassets's hilt share the plane x = 3` (bone-local; Blockbench x -4.9). Both are
tassets parts that reach down into y 8.5..9.7. Fixes: the whole front of the ring moved 0.05
forward-in (z -3.25..-3.0 instead of -3.3..-3.05) and the outer plate 0.05 outboard
(x -5.2..-4.95 instead of -5.15..-4.9), which also cleared `pelt`'s and `scale_skirt`'s x -4.90.
The fold pivots then followed the ring. The rotated fold bones never raised a COPLANAR line at
all - **a rotated bone's faces are not axis-aligned, so they cannot share a plane**; only the
unrotated ring had to dodge.

**The laps, since the brief asked by how much.** 15 hull OVERLAP notes, every one into a
`tassets` part: `tassets`'s `lame2` (3.00 x 1.20 x 0.25 with the ring, 3.00 x 1.14 x 0.52 with
`fold_front`), `tasset` (3.00 x 0.45..0.57), `lame3` (0.11 in y); `loin_panels`' `panel_front`
and `panel_back` (3.00 x 1.14..1.20 x 0.25..0.52 each); `pelt` (2.00 x 1.15 x 0.25);
`thigh_sheath`'s `sheath` and `hilt` (only 0.02..0.05 in x - the cuff passes a twentieth inside
the knife). So the cuff laps the hanging tassets parts by about **1.2 in y and half a unit in
z** - unavoidable: anything that rings this leg at y 8.5..9.7 is inside whatever the tassets
socket hangs past the knee. Tightest clearances: 0.05 in z to `pelt`, 0.05 in x to
`thigh_sheath`'s hilt, 0.07 in y to `tassets`' `lame3`. The knees crowd is 0.20 clear
(`poleyns` in y) and the spurs crowd 0.22 (`heel_wings`).

**Paint: three calls, two sheets.** Call 1 was the whole master - 48 faces in one map (`"*.*":
128`, then each cube's faces: ring `[152,116]` with the outward face lifted to `[190,150]` west
/ `[168,130]` north, up 170, down 92; folds `[140,190]` with the outward face `[148,206]`, the
boot-side face `[126,168]`, `down` 232 as the turned edge) plus 16 `pixels`, two crease columns
on each fold's outward face - and took the unpainted count from 48 to 0. Call 2 was the
outboard pre-compensation after a screenshot: `fold_out_plate.west [174,228]` and `down` 240,
and the two crease columns re-lit to 138/188, plus every fold `up` face from 120 to 150 so the
cuff's top edge is not a black outline. Call 3 was `part_inlay`: the four fold plates' 40 faces
and all 16 crease texels at the master's values, the ring cubes simply absent, so a dyed lining
keeps its creases while the cuff ring under it stays on the trim material's ramp.

What the painter did **not** cover: every fold and ring face is **2 texels tall** (1.1 and 1.2
units), so a `[top, bottom]` pair *is* the whole vertical story - the brief's "a bright bottom
row as the turned edge and a darker top row where it meets the ring" is exactly the pair,
and the only sub-face structure possible is *along* the plate, which is what the crease columns
are. The `up`/`down` faces are 1 texel wide, so the turned edge itself is a flat value (232/240)
and cannot be highlighted. There is no stitching, buckle or motif; a 7x2 face has no room.

**For the next part.** `minecraft:leather_boots` is now taken as a template centre item; it was
already cached, so one `python -m modpage build --offline` rebuilt all three pages with no
warning. Eight cubes fit the default 64x32 with everything below y=12; the plugin never grew the
sheet. **thigh_sheath's west-face lesson holds on this socket too**: the outer plate is the money
face and needed +26 over the front plate's values to read as the same material. And the greaves
socket's y 8.5..9.7 band is now occupied by this ring on all four sides - a future greaves part
that wants the boot top must either sit under y 8.4 or accept sharing the band (same socket, so
never compared, but the planes z -3.25 / -3.0 / 3.05 / 3.3 and x -5.2 / -4.95 / 1.1 / 1.35 are
the ones this part uses).
