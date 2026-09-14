# Brief: Dragon Claws (REWORK)

A **rework of a shipped part**. `armorpieces_dragon:dragon_claws` was built from a qwen brief on
2026-09-09; the pack's owner reviewed it today: *"needs to look more claw-like - take inspiration
from the beast claws."* The datapack half is right and must survive; geometry and sheets are rebuilt.

Open it with `armorpieces_open armorpieces_dragon:dragon_claws`. Do not create a new piece, do not
call `armorpieces_set_part` (fitting, static, effect are all already right), do not touch any other tab.

**The example is `armorpieces_hunt:claws`** - the Wild Hunt's beast claws, a bridge rework that the
owner likes. Read its geometry file
(`packs/wildhunt/resourcepack/assets/armorpieces_hunt/armorpieces/decoration/claws.json`, bone-local
+Y down) and the Lessons at the end of `docs/plans/briefs/claws.md`. Do NOT open it in Blockbench -
a person is reviewing in the other window. Its shape, in Blockbench terms: a `bracer` bone (rotated
-90 about Y so its cubes read along the arm) carrying three talon chains `mid`, `out`, `in`, each
three tapering cubes (1.5 -> 1.0 -> 0.625 section) rotated about X by 85-100 rising to 65-100
cumulative, yaw only +-10, curling FORWARD past the fingertips.

## What is wrong with the shipped model

- Two bones, `claw_front` and `claw_back`, hanging off a bracer - two stubby wedges. It reads as a
  bracer with bumps, not as talons. Envelope `x -2.45..4.45 y 7.30..13.50 z -3.45..3.45`, reach 8.43.
- Nothing curls. A claw is a curve; every cube here is a slab.

## What must not change

- Id `armorpieces_dragon:dragon_claws`, name **"Dragon Claws"**, socket **`vambraces`** only.
- Fitting **`armorpieces:guard`** (masked) - the bracer band. **Static yes** - the talons are the
  dragon's own black. The **effect** (`if_wearer` empty main hand -> attack damage +1/+1.5/+2,
  id `armorpieces_dragon:dragon_claws_bite`) was added today and must survive: you never call
  `set_part`, so it will. No recipe change, no loot row.
- `vambraces` is MIRRORED: model the **left arm, negative x**.

## The rig, in Blockbench coordinates

    left arm box            x -8 .. -4      y 12 .. 24      z -2 .. 2
    sleeve shell (+1)       x -9 .. -3      y 11 .. 25      z -3 .. 3
    the vambraces anchor    (-6, 16, 0)

Front is negative z; outboard is negative x. Stay off the sleeve planes (`x -9, x -3, z +-3, y 11`)
by 0.15 or more - never ON them. The check's frame: `check_x = -5 - bb_x`, `check_y = 22 - bb_y`,
`check_z = bb_z`.

## What it should be

The Ender Dragon's claws on a knight's bracer: **three long black talons curling forward past the
fist**, longer and more curved than the beast's, with a purple sheen at the tips (the dragon's
membrane light). Plus a thin band at the wrist that is the piece's material and `guard` surface.

- **Bracer band** - one cube, the only material surface: about `x -9.2..-2.8, y 13.4..14.4,
  z -3.2..3.2` (0.2 off every sleeve plane).
- **Three talons**, each its own chain of three tapering cubes under bones `out`, `mid`, `in`
  (outboard, middle, inboard), rooted at the bottom-front edge of the sleeve (`y ~11.5`,
  `z ~ -2.5`), spaced across the fist (`x ~ -8.2, -6.0, -3.8`), curling forward and down past the
  fingertips: rotate the BONES about X, each link 30-40 degrees further than its parent, and give the
  outer two a yaw of +-10 so they splay. Section 1.5 -> 1.0 -> 0.6, links 3.0 / 2.5 / 2.0 long.
  Tips should reach about `z -8` and `y 8`.
- **Taper the axis you rotate about** (LESSONS #29). Each link is rotated about X, so each link's
  x extent must be strictly inside its parent's: 1.5 -> 1.0 -> 0.6 already does this. Never let two
  links share an x plane. No two same-facing faces on one plane anywhere in the piece.

**Budget.** Inside `x -9.4 .. -2.6, y 7.5 .. 14.6, z -8.5 .. 3.4` (Blockbench); in the check's frame
`x -2.4 .. 4.4, y 7.4 .. 14.5, z -8.5 .. 3.4`. Reach about 10; pair span about 18.8 - the 18 ceiling is
a `horns` rule and does not apply on the arm (`cuffs` spans 20.14). Report it, do not shrink for it.
Same-socket neighbours are never compared; `pauldrons` pieces are at the top of the arm.

## Sheets

- **master** (greyscale): the band, lighter along its top row, darker at the bottom; every talon cube
  mid-grey underneath the static.
- **static** (colour): the talons black-obsidian `#1a1420` with a lighter edge `#3a2e48` along each
  link's top face and a purple tip `#b04ee0` -> `#e0a0ff` on the last link's front/down faces.
  Nothing on the band.
- **guard mask**: the band only, shaded like its master.

Only `armorpieces_paint` writes these sheets. Null every texel outside the current faces on ALL
THREE sheets first (one `texture op:rects` with `c: null` over the whole sheet per sheet is the
cheapest, cat_paws did it), then paint - one or two paint calls per sheet. No more than six
pictures; a perspective aimed at the fist from the front-below shows the curl best.

**Done means.** `armorpieces_save` without `force`; `python tools/check_part.py <geometry.json>
--name dragon_claws --master <pack png> --static <pack png> --mask guard=<pack png>` clean;
`python tools/check_authoring.py packs/dragon/datapack packs/dragon/resourcepack` clean; the
Lessons below filled in; `armorpieces_close` last. Nothing copied into `tools/decoration_masters/`.

## Lessons from the session

Reworked 2026-09-14 in 37 bridge calls on the kit split: 1 `armorpieces_pieces`, 1 `_open`,
1 `list_outline`, 1 `element remove` (all four old children in one call), 9 `add_group`,
10 `place_cube`, 15 `element set` (6 of them refused, see below), 3 `texture op:rects`,
3 `armorpieces_paint`, 2 `capture_screenshot`, 2 `_check`, 1 `_save`, 1 `_close`. No `set_part`,
no `modify_cube`, no `risky_eval`; the save went through first time without `force`. The data
file kept its 12:27 timestamp - the effect and the fitting survived untouched.

**What I built.** The old `base` bone (origin bb (-6, 12.25, 0)) kept, `base_0`, `base_1`,
`claw_front`, `claw_back` removed by name. In `base`: `band` x -9.2..-2.8, y 13.4..14.4,
z -3.2..3.2 exactly as the brief. Three chains `out`/`out_b`/`out_c`, `mid`/..., `in`/...,
roots at (-8.0 / -6.0 / -4.0, 11.6, -2.5) - x pulled 0.2 inboard from the brief's -8.2/-3.8
so the yawed tips stay inside x -9.4 / -2.6 - each modelled straight along -Z, child pivots at
parent + 2.75 and + 2.25 (L - 0.25 overlap), cubes 1.5 / 1.0 / 0.6 square, 3.0 / 2.5 / 2.0 long.
Rotations, Blockbench, negative X curls down:

- `out`  [-8, +10, 0] / [-32] / [-35]  -> cumulative 8 / 40 / 75, tip bb (-8.9, 7.8, -7.4)
- `mid`  [-5, 0, 0]   / [-30] / [-35]  -> 5 / 35 / 70, tip (-6.0, 8.0, -7.9)
- `in`   [-4, -10, 0] / [-30] / [-30]  -> 4 / 34 / 64, tip (-3.0, 8.3, -7.9)

Envelope (check frame) x -2.38..4.35, y 7.60..14.24, z -8.22..3.20; reach 11.56; pair span
18.71. Every bone landed where the sums said (mid_b predicted bb (-6, 11.36, -5.24), reported
(1.00, 10.64, -5.24)).

**The brief's numbers do not all fit together, and the tip target is the one that decides the
curl.** Links 3.0/2.5/2.0 give a 7.0 chain; a tip at (y 8, z -8) from a root at (11.6, -2.5) is
a 6.5 chord, so the chain can only bend a little (cumulative 64-75 at the tip, increments of
30-35) - "more curved than the beast's" (85-100) and "tips at z -8" cannot both be had at these
lengths, and the y floor of 7.5 forbids fixing it by curling harder. I took the tip target and
the budget; the reach came out 11.6, not the brief's "about 10" (a tip at z -8, y 8 is 11.3 from
the anchor at (-6,16,0) whatever the shape, so "about 10" was never reachable with that tip).
If the owner wants a deeper hook, lengthen the `_b`/`_c` links rather than steepening: every
0.5 of extra length buys ~15 degrees of curl at the same tip.

**Bone and cube share a name from the moment `place_cube` lands** (LESSONS 7b): `out_b` the
bone and `out_b` the cube. `element set {id: "out_b"}` refuses with "names 2 elements". The
uuid is in the `add_group` reply you already have - no `list_outline` needed. Six refused
calls, one turn. Next time name the cubes `out_b_cube` or the bones `out_2`.

**The pack's sheets are under `textures/entity/decoration/`, not
`textures/armorpieces/decoration/`** - the brief's `<pack png>` hint sent the first
`check_part.py` run to a folder that does not exist. `find packs/<pack> -name "<part>*"` first.

**The viewport shows the master, not the static**, so the talons look mid-grey in every
screenshot; the purple tips are only verifiable on the sheet (`texture op:read` on
`part_static`) or in game. Two pictures were enough: one perspective from front-below-outboard
(the curl is visible but the angle is confusing), one orthographic from outboard at the fist
(reads at once: strap, straight link, hook).

**`!` lines accepted: none.** Three `-` notes: the band's hull overlaps `wing_cases`'
`case_lower` by 0.33 in y (the brief's own band coordinates, 14.4 top against its 14.07 bottom;
the beast's band sat 0.27 under it at 13.8 - lower the band to 12.9..13.9 if the owner minds),
`near` 0.40 in x to the same, and the pair span 18.71 (the brief says report, not shrink).

**Every reply carried** `session id held by 2 connections ... Name project on every call`;
passing `project: "dragon_claws"` on every mcptoolkit call cost nothing and nothing misfired.
