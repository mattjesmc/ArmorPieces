# Brief: Dragon Horns (REWORK)

A **rework of a shipped part**. `armorpieces_dragon:dragon_horns` was built from a brief and the
pack's owner reviewed it today: *"not the dragon's horns - a good piece, but not here."* The model as
it stands is liked and has been backed up to be reused under another name elsewhere; in THIS slot
it is to be replaced by the Ender Dragon's own horns. The datapack half is right and must survive.

Open it with `armorpieces_open armorpieces_dragon:dragon_horns`. Do not create a new piece, do not
call `armorpieces_set_part`, do not touch any other tab.

## What is wrong with the shipped model

- Envelope bone-local `x 4.00..6.54 y -12.93..-4.20 z -1.00..2.42`, reach 8.42: a single tall horn
  rising 8 units from the temple. Handsome, and nothing like the dragon: the Ender Dragon has no
  tall horns - it has **two short, thick, swept-back scale-horns on top of its head**, boxy, black,
  angled back, the pair sitting either side of the crown behind the eyes.

## What must not change

- Id `armorpieces_dragon:dragon_horns`, name **"Dragon Horns"**, socket **`horns`** only.
- Fitting **`armorpieces:guard`** (masked), **static yes**. No effects, no recipe change, no loot.
- `horns` is MIRRORED: model **one side, the left, at negative x**; the game mirrors it.

## The rig, in Blockbench coordinates

    head box                x -4 .. 4       y 24 .. 32      z -4 .. 4
    helmet shell (+1)       x -5 .. 5       y 23 .. 33      z -5 .. 5
    the horns anchor        (-4, 29, 0)      - the side of the head, above the ear

Front is negative z. Stay off the helmet planes (`x -5`, `y 33`, `z +-5`) by 0.15 or more. The
check's frame on the head: `check = (-bb_x, 24 - bb_y, bb_z)`.

Worn together with `brow` and `crest` pieces on the same bone, and the check lists them: a `crest`
piece sits on top of the head from about `y 33` up at `|x| <= 2.5` (`spire`, `brush_crest`,
`coral_crown`, `witch_hat` at `|x| <= 6.45, y 32.15..39.95` is the wide one); a `brow` piece is on
the face (`z <= -5`), `laurel`/`circlet`/`browband` ring the head at `y 26.6..30.8`. So: outboard of
`|x| 5.2`, above `y 31`, behind `z -3`, and not above `y 35.5` inside `|x| 6.45` - that is the
lane the dragon's horn lives in without lapping anything. `helm_wings` (`x -6.40..-5.30,
y 31.14..38.37, z -0.74..6.58`) is the other horns-socket piece and is never worn with you.

## What it should be

**The Ender Dragon's scale-horn**: on the dragon it is a box 2 wide, 4 tall, 6 long, standing on
the top-back of the head, tilted back. On a player: a **thick, blunt horn in two links**, rising
from just above the temple and sweeping back at about 45 degrees, black hide with a grey-black
ridge, and a thin metal **ferrule** where it meets the helmet - the piece's material/`guard`
surface.

- **`ferrule`** - a ring cube at the horn's base: about `x -6.3..-5.2, y 30.6..32.0, z -1.2..1.2`.
- **`horn_a`** - the base link, a `1.6 x 1.6` section box `3.5` long, its bone pivoted at the
  ferrule (`(-5.75, 31.3, 0)`) and rotated about X so it leans BACK 40-45 degrees, and about Z a
  few degrees so it leans outboard.
- **`horn_b`** - a child link, `1.2 x 1.2` section, `2.5` long, another 20-25 degrees back.
- **Taper the axis you rotate about** (LESSONS #29): the links are rotated about X, so `horn_b`'s
  x extent must be strictly inside `horn_a`'s (1.2 inside 1.6 - do not centre them on different
  x) and the ferrule's x planes must not coincide with `horn_a`'s. No two same-facing faces on one
  plane.

**Budget.** Inside `x -8.2 .. -5.1, y 30.5 .. 36, z -1.5 .. 6` (Blockbench); check frame
`x 5.1 .. 8.2, y -12 .. -6.5, z -1.5 .. 6`. Reach about 6; pair span about 16 (inside the 18 the
horns socket holds to).

## Sheets

- **master**: the ferrule, lighter top row, darker bottom; horn cubes mid-grey under the static.
- **static**: hide black `#161218` with a `#302838` ridge along the top face of each link and a
  faint purple `#3a2050` on the underside. Nothing on the ferrule.
- **guard mask**: the ferrule only.

Null strays on all three sheets first (`texture op:rects` with `c: null` over the whole sheet,
per sheet), then paint - one paint call per sheet. No more than five pictures.

**Done means.** `armorpieces_save` without `force`; `python tools/check_part.py <geometry.json>
--name dragon_horns --master <pack png> --static <pack png> --mask guard=<pack png>` clean;
`python tools/check_authoring.py packs/dragon/datapack packs/dragon/resourcepack` clean; Lessons
filled in; `armorpieces_close` last. Nothing copied into `tools/decoration_masters/`.

## Lessons from the session

Built 2026-09-14 on the kit bridge. Three cubes, three bones, one `armorpieces_paint` call per
sheet, one contact sheet, saved without `force`; `check_part.py` by file and `check_authoring.py`
clean, nothing in `tools/decoration_masters/`.

- **Shape as built.** `base` (anchor, `(-4,29,0)`) holds the `ferrule` cube `x -6.95..-5.2,
  y 30.55..32.05, z -1.2..1.2`; `horn_a` (pivot `(-5.75,31.3,0)`, rotation `[42,0,4]`) holds a
  `1.6x3.5x1.6` link `x -6.85..-5.25, y 31.3..34.8`; `horn_b` (child of horn_a, pivot
  `(-6.05,34.8,0)`, rotation `[22,0,0]`) holds a `1.2x2.5x1.2` link `x -6.65..-5.45,
  y 34.55..37.05` (0.25 lap). Envelope in the check frame `x 5.20..7.07 y -11.44..-6.55
  z -1.20..4.63`, reach 8.11, pair span 14.13 - inside the budget on every axis.
- **The ferrule was widened past the brief's `x -6.3..-5.2` to `-6.95..-5.2`.** A 1.1-wide ring
  cannot wrap a 1.6-wide horn; the brief's own "1.6 section" is the more specific number (LESSONS
  #7), so the ring grew to 1.75 and took the horn inside it. The ferrule's top went to 32.05 and
  its bottom to 30.55 to stay off `y 32.00` (`brush_crest`/`feathering` bottoms) and `30.75`
  (`circlet` top) - round numbers, LESSONS #6.
- **The lean-back chain landed to the hundredth from the LESSONS #3 formulas** (y max 35.44
  predicted 35.43, z max 4.63 predicted 4.63) - no nudging. The 4-degree outboard lean about Z was
  chosen so the outer base corner (Δx -1.1 from the pivot) drops only `1.1*sin4 = 0.08` and stays
  inside the ferrule box.
- **The horn's "top" ridge is the `north` face.** A link built vertical and then leaned back 42-64
  degrees presents its unrotated front (`north`, -z) as its upper surface and its `south` as the
  underside; the `up` face is the tip. Paint the ridge on `north` and the underside colour on
  `south`, not on `up`/`down`.
- **The `-` lines left standing:** hull OVERLAPs into `witch_hat`'s brim envelope and
  `transverse_crest`'s bar, and `near` lines against `laurel`/`browband`/`witch_hat`. The brief's lane
  ("not above 35.5 inside |x| 6.45") allows lapping the witch hat's printed envelope below its brim,
  which is what these are; the horn's peak is 35.44.
- **The first `add_group` reply narrated `dragon_wings`** while `"bound":true` said the edit landed on
  `dragon_horns` (LESSONS #20a). One re-`armorpieces_open` of my own piece fixed the narration
  for the rest of the session.
- The starter-cube/bone name clash of LESSONS #7b never came up: the cubes were named `ferrule`,
  `horn_a_cube`, `horn_b_cube` from the start.
