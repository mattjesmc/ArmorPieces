# Brief: Bellows Visor

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the twelfth
batch — six parts rather than the usual four, the mod's first family that is **flat rather than
cubic** (read `docs/plans/visor-styles.md`, then `barbute.md` for the plate and the cut, and
`sallet_slit.md` for the proud-cube overlap rule). This is the family's most literal part: a
bellows visor *is* ribs with air between them, which is a flat plate with slots and three proud
strips. From `docs/plans/visor-styles.md`:

> **Bellows Visor** - The fluted close-helm face: horizontal ribs stepping out, air between them.
> Opening: two slots between three proud ribs. Fitting: `inlay` (the flutes).

**Part.** `armorpieces:bellows_visor`, socket `brow` only, in the mod's own pack
(`src/main/resources`, namespace `armorpieces`), so the master lives in
`tools/decoration_masters/bellows_visor.png` and is installed on save. Display name "Bellows
Visor". Fittings: `armorpieces:inlay`, one mask, covering the three ribs — the plate stays the
armour's material and the flutes dye, which is how fluted armour was actually finished. No static
layer, no effects, no loot.

**The frame, which every visor in this family shares.** `brow` is not a mirrored socket: model the
whole thing on the head bone. The head box is x -4..4, y 24..32, z -4..4 (pivot 0, 24, 0); the
helmet shell is that box inflated a full unit, so its front plane is z -5; the anchor is at
Blockbench (0, 28, -4). **The face is empty.** Every part sharing this bone was measured: the
furthest forward any reaches is `brush_crest` at z -3.5, then `feathering` -3.0, `cheek_guards`
-2.4, `comb` -2.1, `horns` and `helm_wings` -2.0, `antlers` -1.7, `head_fins` -1.4 — so anything
in front of z -4 is free at any height and any width, and the clash lines should come back
silent. The other brow parts are never compared; the shipped `visor` is a competitor, not an
obstacle. What is left to dodge: the shell plane z -5, the head box's own planes (x ±4, y 24,
y 32 — stay below 32), and your own cubes.

**Shape.** Four bones. `mask` pivoted at the anchor (0, 28, -4) with a `plate`
**x -4..4, y 24..31, z -5.35..-5.10** — the family's full faceplate, eight wide, seven tall, a
quarter thick. Then `rib_1`, `rib_2`, `rib_3`, each a child bone with one full-width strip
**x -4..4, z -5.60..-5.30**, at **y 29..30**, **y 27..28** and **y 25..26**.

Each rib is 0.30 thick and sits 0.05 *inside* the plate's front face, so no two faces of this part
are coincident (self-coplanarity is not flagged by the checker and z-fights in the game anyway —
`browband`'s lesson). The three ribs share a front plane with each other, which is fine and
unavoidable: they are disjoint in y, so no two faces ever occupy the same place. Say in the
lessons whether the checker treated the three as a shared plane or ignored them, because the rest
of the mod has never stacked parallel strips like this.

The usual `-` notes are expected: side faces on x = ±4, the plate's bottom face on y = 24. And
`ruff`, on `collar`, reaches into this volume (Blockbench y 24.4..26.0, z -7.5..3.5, x ±5.5), so
expect overlap or near lines against the bottom rib: a visor in front of a ruff is right, a shared
plane with it is not.

**Sheets.** The plate is 8x7 texels, each rib 8x1. Plate rows from the top: r1 = y 30..31,
r2 = 29..30 (behind rib_1), r3 = 28..29, r4 = 27..28 (behind rib_2), r5 = 26..27, r6 = 25..26
(behind rib_3), r7 = 24..25.

**The cut.** Two slots, on the plate's north face: **r3 columns 2..7** and **r5 columns 2..7** —
the breathing gaps between the ribs. Leave them unpainted; an unpainted texel is *absent*, not
transparent, so each gap is a real opening with the player's face 1.35 units behind it, and the
ribs above and below stand proud of nothing. Cut the plate's four corner texels so the visor is a
face and not a rectangle.

Master: the plate dark, 120 at the top falling to 95 at the jaw — it is the shadow the ribs throw,
and it should never compete with them. Each rib bright and graded across its single row is
impossible (**one unit on an axis is one texel there**, the rule `laurel` wrote down), so the
vertical story is per-face: give every rib `up` 235, north 200, `down` 110, so the light reads as
coming from above and each rib turns the light three ways. Vary the three by 10 values, brightest
at the brow. A 90-value texel along the top and bottom edge of each slot gives the openings their
wall. Rim strips and south faces take a flat 105 so nothing is empty — a face with nothing behind
it is a `!`, a partly painted face is only a note.

Inlay mask: the three ribs' faces at the master's own values, all six faces of each, so the dyed
flute keeps its top-lit shading. Preview it filled and say whether three dyed strips over a dark
plate reads as fluting or as a bar code.

**Corrections from the Barbute session — the first part of this family, built clean. Read these
before painting; two of them would otherwise ship a visor with no holes in it.**

1. **Cut the south face too, in the same pattern.** `armorCutoutNoCull` draws back faces, so an
   opening cut only in the north face is filled by the *inside* of the painted south face and
   stops being a hole. Every cut described above has to be made twice — once in the north
   rectangle, once in the south — and where the silhouette is nipped, clear the matching
   rim texels as well. Barbute shipped this way and its T reads as a hole at three metres, with
   the player's own skin showing through at a hue no trim material has.
2. **Never cut a corner texel directly above or below the end column of a full-width opening.**
   Barbute cut only its two *bottom* corners: cutting the top pair as well would have left the
   brow row hanging over the eye band with nothing orthogonal holding it.
3. **Check the recipe centre against the fitting templates as well as the part templates.**
   `copper_ingot` was free of all 84 `template_*.json` but is `fitting_template_guard.json`'s
   centre, so Barbute shipped `minecraft:raw_copper` instead. `armorpieces_set_part` accepts a
   colliding centre silently — the `!` only appears on the next check. This part's centre has
   been re-checked against both sets and is free.
4. **`ruff` will never appear in your check.** It sits on the `collar` bone and no tool compares
   across bones, so the warning above about it is yours to apply by eye, or to ignore.
5. **A flat-90 inlay dyes almost black.** Barbute's border mask used 90 over a small region and
   came out very dark; this part's flute region is far larger, so shade the mask 130–150.

**Also from the Sallet Slit session — part two, built clean.**

- **There is a THIRD set of recipe centres.** Not just the 86 `template_*.json` and the four
  `fitting_template_*.json` but fourteen `skin_template_*.json`: `iron_door` was free of the first
  two and turned out to be `skin_template_gothic.json`'s centre, so Sallet Slit ships
  `minecraft:shears`. Dump all three sets at once if you ever need a new centre. This part's centre
  has been checked against all three and is free.
- **A two-unit proud band does read as a separate piece** — at three metres, straight on, with no
  fitting applied. But two units is the *minimum* that works, and it works because the band's
  values sit clearly **outside** the plate's range rather than merely above it (band 230/175 over
  a plate of 130/105). Keep that separation in your own values.
- **Do not flat-paint a proud cube's rim.** Sallet Slit deviated from its brief's flat rims on
  purpose and was right to: `up` 200 and `down` 90 on the band, because the lit top strip is the
  only thing the depth reads as from an angle, and the dark underside is what turns a step into an
  overhang instead of a gap. Do the same on every proud cube here.
- **The back-face cut rule covers proud cubes too**, and their `up`/`down`/`east`/`west` rim
  texels wherever the silhouette is nipped — not only the plate's.

**Recipe.** Centre item `minecraft:blaze_rod` (a flat item, unused by any template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
bellows_visor` and `python tools/check_authoring.py` clean; the mod page rebuilt (if the centre has never been
cached, `--offline` warns and draws a checkerboard — one plain `python -m modpage build` fetches
it, then re-run offline); the lessons paragraph below filled in. Count your paint calls and say
what the painter did and did not cover. Judge from the straight-on shot (`set_camera_angle`
position [0, 28, -24], target [0, 28, 0]) and one three-quarter ([6, 30, -22], target
[0, 27.5, 0]) — this is the part whose whole effect is the depth step, so the three-quarter matters
more here than anywhere else in the family.

**Picture budget: two screenshots, and both after the last paint call.** An image is billed by
area and re-sent on every later turn, so looks taken while painting are paid for many times over;
the leanest sessions on record took every shot after the painting was done.

## Lessons from the session

Built 2026-09-05 in 15 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 4 `add_group`
(`mask`, `rib_1`, `rib_2`, `rib_3`), 4 `place_cube`, 2 `remove_element` (starter cube `main_0`,
then bone `main`), 1 `armorpieces_check`, 1 `armorpieces_set_part`, **2 `armorpieces_paint`**
(master, inlay mask), 2 `set_camera_angle`, 1 `armorpieces_save`. No `risky_eval`, no
`modify_cube`, no `list_outline`, no nudging, nothing hand-edited; the save went through first
time **without `force`**, and one `set_part` sufficed because the centre had already been cleared
against all three template sets. Geometry is exactly the brief's: `mask` at (0, 28, -4) with
`plate` x -4..4, y 24..31, z -5.35..-5.10 (uv 12,0 8x7x0.25), and child bones `rib_1` (0, 30,
-5.3), `rib_2` (0, 28, -5.3), `rib_3` (0, 26, -5.3) holding `rib_top` y 29..30, `rib_mid`
y 27..28, `rib_low` y 25..26, all x -4..4, z -5.60..-5.30 (uv 30,0 / 30,2 / 30,4, 8x1x0.3).

**THE QUESTION THE BRIEF ASKED: three parallel proud strips sharing a front plane are not
mentioned by the checker at all.** No `COPLANAR`, no `shared plane`, not even a `-` note. Ten
notes came back and nine of them are the foreseen `x face at ±4 lies on the body surface` — one
per cube per side — plus `mask's y face at 0`. So the coplanarity test is strictly **cross-part**:
it compares this part's planes against the body, the armour shells and the envelopes of parts on
the same bone, and never one of the part's own cubes against another. That is consistent with what
`browband` learned the hard way (self-coplanarity is invisible to the checker *and* z-fights in
the game), and it means the family's "no two cubes of one part share a plane" rule is entirely on
the author. Here it was never at risk: the three ribs are coplanar in z but **disjoint in y**, so
no two faces ever occupy the same square of space and there is nothing to fight. Great Helm's two
*crossing* proud cubes are the case where the checker's silence is dangerous, and its 0.05 step
must be applied by hand.

**The ribs make their own slot walls, so the brief's 90-value wall texels had to move.** The brief
asked for a 90 texel along the top and bottom edge of each slot. Those edges are plate rows r2 and
r4 (and r4/r6 for the lower slot) — the rows sitting **directly behind the ribs**, exactly covered
in y and 0.25 buried in z, so a wall painted there is invisible. What actually bounds each opening
is `rib_n.down` above it and `rib_(n+1).up` below it: the rib's own 0.30 of thickness *is* the
wall, already painted 110 dark above and 225 bright below. So the 90 went instead on the plate's
**side jambs** — columns 1 and 8 of rows r3 and r5, the only plate texels of those rows that
survive the cut, on north and south both. Eight texels, and they read as the dark cheek either
side of each breath. General note for the family: when a proud cube laps a cut row exactly, the
proud cube's rim faces are the opening's wall and the plate row behind it is decoration.

**Two paint calls; 41 face entries and 48 pixels on the master, 33 face entries on the mask.**
Master: `*.*` 105 as the floor, then `plate.up` 125, `plate.north` [120, 95], and per rib
`north`/`up`/`down`/`east+west` — 200/235/110/150 at the brow, 190/225/100/150, 180/215/90/150
at the jaw, the brief's 10-value ladder. Then 8 pixels at 90 (the jambs) and 40 nulls: 24 for the
two slots on north (x 14..19, y 3 and y 5) and south (x 23..28, same rows), 8 for the four corner
texels on both faces, 8 for the matching rim texels (`up` 13,0 and 20,0; `down` 21,0 and 28,0;
`east` 12,1 and 12,7; `west` 21,1 and 21,7). Finished master: **204 opaque texels, greyscale,
range 90..235**; mask 102 texels, range 105..235, verified with Pillow to be a strict subset of
the master. What the painter did **not** cover: no gradient on any rib (one unit on an axis is one
texel — `laurel`'s rule — so the ribs' vertical story is entirely per-face), no variation in the
90 jambs, and no separate treatment of the plate rows behind the ribs, which simply take the
plate's own gradient because they are only ever glimpsed from steeply below.

**The corner rule survived a full-width opening on two rows.** Both slots run columns 2..7, so
their end columns are 2 and 7 and the corners at columns 1 and 8 are *not* directly above or below
them — Barbute's rule permits all four corners here, and cutting all four is what turns the
rectangle into a face. The plate that remains is r1 (c2..7), r2 full, r3 (c1, c8), r4 full,
r5 (c1, c8), r6 full, r7 (c2..7): every row is held by the two full-height jamb columns, and the
three ribs bridge the whole width in front of them. Nothing floats.

**Fluting, not a bar code — and the three-quarter shot is where it is won.** Straight on, the
three bright bands (180..235) over a plate of 120..95 read as steel ribs with the player's own skin
plainly visible in both gaps, at a hue no trim material has; the value separation Sallet Slit
insisted on (band clearly *outside* the plate's range, not merely above it) is what keeps it from
being three painted stripes. But the depth only becomes undeniable at three quarters, where each
rib's `up` face is a one-texel white line and its `down` face a dark one: three lit edges stacked
down the face is exactly what fluted armour looks like, and it is impossible to read as printing.
A one-unit rib works where Sallet Slit needed two, because a rib does not have to read as a
*separate plate* — three of them in a row read as a *surface treatment*, and the repetition does
the work the extra unit did there. Great Helm can therefore trust one-unit relief for anything
repeated, and should keep two units for its single reinforce cross.

**The inlay mask is the master's own shading with the undersides lifted.** All six faces of each
rib, at 235/200/150/105 (up/north/east+west/south) as the master, but `down` at 130/125/120
instead of 110/100/90 — Barbute's warning that a flat 90 dyes almost black applies hardest to the
one face of the flute that is already in shadow, and the region here is the part's whole subject.
The bright faces needed no lifting at all: the correction's 130-150 floor is about a region's
*dominant* value, and this one is dominated by 180..235. Three dyed flutes over an undyed steel
plate is the right division — the plate keeps the armour's material, which is what makes the part
look forged rather than stuck on.

**Notes accepted, and the one warning no tool gives.** Ten `-` notes stand, all foreseen: nine
`x face at ±4` (the plate and all three ribs, both sides) and the plate's bottom face on y 24. None
can z-fight — every one of them lives 1.35 units or more in front of the head's front face, where
those planes carry no geometry. The clash lines against the fifteen head-bone parts came back
`all clear by more than half a unit`. `ruff` never appeared, exactly as Barbute predicted: it is on
`collar`, a different bone, so the overlap between its Blockbench y 24.4..26.0 and `rib_low` at
y 25..26 is mine to judge by eye. It is fine and it is correct — a visor's bottom rib in front of a
collar ruff is how the two were worn, they meet at z -5.3 versus the ruff's -7.5..3.5 with the rib
in front, and no plane is shared.

**modpage.** The same three-step dance as the two before: `--offline` warned `minecraft:blaze_rod`
had never been cached and drew a checkerboard, a plain `python -m modpage build` fetched it, and
the third build reported `unchanged` on all three outputs. `modpage.yml` needed nothing.
`blaze_rod` was confirmed free against all 86 `template_*`, four `fitting_template_*` and fourteen
`skin_template_*` grids before `set_part`, so the recipe check passed on the first save — the
first part of this family for which it did. The remaining warnings (`minecraft:chain`, two
`armorpieces:smithing_skin` recipes) are pre-existing.
