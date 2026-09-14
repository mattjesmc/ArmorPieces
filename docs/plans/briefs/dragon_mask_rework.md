# Brief: Dragon Mask (REWORK)

A **rework of a shipped part**. `armorpieces_dragon:dragon_mask` was built from a brief; the pack's
owner reviewed it today: *"doesn't look like the Minecraft dragon enough."* The datapack half is
right and must survive; geometry and sheets are rebuilt.

Open it with `armorpieces_open armorpieces_dragon:dragon_mask`. Do not create a new piece, do not
call `armorpieces_set_part`, do not touch any other tab.

## What is wrong with the shipped model

- Envelope bone-local `x -4.00..4.00 y -6.10..-2.26 z -7.81..-5.18`, reach 4.68: a face plate with
  two ridges. 2.6 units deep. The Ender Dragon's head is **all snout** - a long box muzzle with a
  separate lower jaw, two nostril bumps on top of the muzzle, a row of teeth, and the eyes set back
  on the head behind the muzzle. A plate cannot read as that.

## What must not change

- Id `armorpieces_dragon:dragon_mask`, name **"Dragon Mask"**, socket **`brow`** only.
- Fitting **`armorpieces:gemstone`** (masked) - **the eyes**. **Static yes**. No effects, no recipe
  change, no loot.
- `brow` is NOT mirrored: model the whole face, symmetric about x 0.

## The rig, in Blockbench coordinates

    head box                x -4 .. 4       y 24 .. 32      z -4 .. 4
    helmet shell (+1)       x -5 .. 5       y 23 .. 33      z -5 .. 5
    chestplate shell        x -5 .. 5       y 11 .. 25      z -3 .. 3     (a different slot; the check never mentions it)
    the brow anchor         (0, 28, -4)      - the middle of the face

Front is negative z: **the muzzle goes to -z**. Stay off the helmet's front plane `z -5` (and
`x +-5`, `y 23`) by 0.15 or more. The check's frame on the head: `check = (-bb_x, 24 - bb_y, bb_z)`.

Worn together with `horns` and `crest` pieces: `horns` pieces are outboard of `|x| 4.3` and mostly
above `y 28`; `crest` pieces are on top from `y 32` up; `dragon_horns` (being rebuilt alongside
you) will sit at `|x| 5.1..8.2, y 30.5..36, z -1.5..6`. Everything of yours inside `|x| 4.5`, below
`y 32.5` and in front of `z -4.9` clears all of it. The chestplate's top is `y 25` at `z >= -3`: a
jaw hanging below `y 25` must be in front of `z -3.2`.

## What it should be

**The Ender Dragon's face worn as a mask**, in the game's own proportions: a **long boxy muzzle**
jutting forward from the brow, a **lower jaw** beneath it slightly open, two **nostril bumps** on
top near the tip, a row of small **teeth** along the muzzle's lower edge, and the **eyes** - the
`gemstone` surface - as two slanted slits on the mask plate either side of the muzzle's root.
Black hide, purple eyes (the fitting's default look), grey-white teeth.

Cubes, all under `base` (never `root`), no rotations needed (the jaw may take a single 10-degree X
rotation to hang open - if you do, its x extent must be strictly inside the muzzle's, LESSONS #29):

- **`plate`** - the mask over the face, the part the eyes sit on: `x -4.4..4.4, y 26.4..31.6,
  z -5.9..-5.15`.
- **`muzzle`** - the upper snout, from the plate forward: `x -2.6..2.6, y 26.9..29.4, z -11.0..-5.9`.
- **`nostril_l` / `nostril_r`** - two bumps on the muzzle's top near the tip: `x +-(0.9..2.1),
  y 29.4..30.0, z -10.6..-9.4`.
- **`jaw`** - the lower jaw under the muzzle, a little shorter and thinner: `x -2.3..2.3,
  y 25.3..26.5, z -10.2..-5.9` (0.4 gap under the muzzle so it reads open; its top face at 26.5 and
  the muzzle's bottom at 26.9 are not one plane).
- **`teeth`** - a thin row along the muzzle's lower front edge: `x -2.2..2.2, y 26.5..26.9,
  z -10.9..-10.3` - one cube, painted as alternating white/black texels so it reads as teeth. No
  face of it may share a plane with the muzzle: it sits 0.1 in from the muzzle's tip and its top
  meets the muzzle's underside (facing faces, hidden).

**Budget.** Inside `x -4.6 .. 4.6, y 25.0 .. 32.0, z -11.3 .. -5.1` (Blockbench); check frame
`x -4.6 .. 4.6, y -8 .. -1, z -11.3 .. -5.1`. Reach about 7.5. Eight cubes.

## Sheets

- **master**: mid-grey everywhere under the static - this piece has no bare material surface;
  its player surface is the gemstone eyes.
- **static**: hide black `#161218`, a `#2a2230` lighter top on the muzzle and plate, a faint
  purple `#3a2050` under the jaw; nostrils darker `#0c0a10`; teeth `#e8e4d8` texels alternating
  with hide black along the row. **Leave the eye slits UNPAINTED in the static** - two slanted
  2x1-texel slits on the plate's north face either side of the muzzle root - so the master shows
  through there.
- **gemstone mask**: **those eye slits only**, flat 140 - the fitting fills them with the player's
  gem, and until then the master shows.

Null strays on all three sheets first (`texture op:rects` with `c: null` over the whole sheet,
per sheet), then paint. One or two paint calls per sheet; no more than six pictures - a front
(`north`) and a three-quarter are the two that matter.

**Done means.** `armorpieces_save` without `force`; `python tools/check_part.py <geometry.json>
--name dragon_mask --master <pack png> --static <pack png> --mask gemstone=<pack png>` clean;
`python tools/check_authoring.py packs/dragon/datapack packs/dragon/resourcepack` clean; Lessons
filled in; `armorpieces_close` last. Nothing copied into `tools/decoration_masters/`.

## Lessons from the session

Built 2026-09-14 in 20 bridge calls, two pictures, no forced save, no nudges.

- **The brief's cube list is six, its budget line says eight.** I took the named list (LESSONS #7):
  plate, muzzle, nostril_l, nostril_r, jaw, teeth. Nothing in the description needed a seventh.
- **Every coordinate landed as written, check clean on the first placement.** Envelope
  `x -4.40..4.40 y -7.60..-1.30 z -11.00..-5.15`, reach 7.60 (brief said ~7.5), past helmet
  z +6.00. The three touching pairs (muzzle/plate at z -5.9, nostrils/muzzle at y 29.4,
  teeth/muzzle at y 26.9) are facing faces and the coplanar pass says nothing about them; the
  jaw's top at 26.5 and the teeth's bottom at 26.5 do not overlap in z (jaw ends at -10.2, teeth
  start at -10.3) so that plane is silent too. Jaw left unrotated: the 0.4 gap reads as open already.
- **A "slanted 2x1 slit" on a 9x6 face is two texels on a diagonal.** Plate north face is
  `25,1 9x6`; muzzle root covers columns 2..6 and rows 3..5, so the eyes went at (col 0,row 1)+
  (col 1,row 2) and mirrored (col 8,row 1)+(col 7,row 2) - sheet (25,2),(26,3),(33,2),(32,3) -
  outer texel high, inner low. Column 1 row 2 loses a 0.16x0.4 sliver behind the muzzle corner;
  invisible at game scale.
- **One static call did the whole colour job**: a faces map with `*.*` hide, `plate.north` as a
  `["#2a2230", "#161218"]` pair, nostril/teeth overrides, then `pixels` with the four eye slits as
  `null` (static shows the master through them) and nine `#e8e4d8` teeth texels at columns 0/2/4
  of the teeth's north (41,8), down (46,7) and south (47,8) rows. The gemstone call is `pixels`
  only, no `faces` - accepted fine.
- **`fit: true` on the contact sheet frames the whole player**, useless for a head-sized piece;
  a single perspective shot `position [-14,26,-22] target [0,28,-8]` read the muzzle, nostril,
  jaw gap and teeth strip in one picture. Take that one and skip the fit sheet.
- The viewport renders the master preview (grey), not the static colours - do not expect to
  judge black hide vs white teeth from a screenshot; read the saved PNGs with Pillow instead.
