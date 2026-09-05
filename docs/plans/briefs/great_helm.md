# Brief: Great Helm

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the twelfth
batch — six parts rather than the usual four, the mod's first family that is **flat rather than
cubic** (read `docs/plans/visor-styles.md`, then `barbute.md` for the plate and the cut,
`sallet_slit.md` for the proud-cube overlap rule, and `bellows_visor.md` for parallel strips).
This is the hardest one in the family: **two proud cubes that cross**, and the only asymmetric
paint job in the batch. From `docs/plans/visor-styles.md`:

> **Great Helm** - The crusader front: a reinforce cross riveted over a flat plate, breaths
> drilled on the sword side only. Opening: two sights over a field of drilled breaths.
> Fitting: `guard` (the cross).

**Part.** `armorpieces:great_helm`, socket `brow` only, in the mod's own pack
(`src/main/resources`, namespace `armorpieces`), so the master lives in
`tools/decoration_masters/great_helm.png` and is installed on save. Display name "Great Helm".
Fittings: `armorpieces:guard`, one mask, covering both arms of the cross — the plate stays the
helmet's material and the riveted reinforce takes a second metal, which is exactly what it was.
No static layer, no effects, no loot.

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

**Shape.** Three bones. `mask` pivoted at the anchor (0, 28, -4) with a `plate`
**x -4..4, y 24..31, z -5.35..-5.10** — the full faceplate. Then `cross_v`, a child bone with a
band **x -1..1, y 24..31, z -5.60..-5.25**, and `cross_h`, a child bone with a band
**x -4..4, y 27..29, z -5.55..-5.30**.

**The two proud cubes cross, and the depths are staggered on purpose.** The vertical stands
furthest out (-5.60) and reaches deepest into the plate (-5.25); the horizontal sits between them
(-5.55..-5.30). Neither shares a plane with the other or with the plate, so nothing z-fights where
they meet — self-coplanarity is not flagged by the checker and z-fights in the game anyway
(`browband`'s lesson), and this is the first part in the mod where two proud cubes overlap at all.
The horizontal's faces end up buried inside the vertical at the crossing, which is a `-` note and
correct. A vertical riveted over a horizontal is also the right way round historically.

Expected `-` notes: side faces on x = ±4, the plate's bottom face on y = 24. `ruff`, on `collar`,
reaches into this volume (Blockbench y 24.4..26.0, z -7.5..3.5, x ±5.5) — a faceplate in front of
a ruff is right, a shared plane with it is not.

**Sheets.** The plate is 8x7 texels, `cross_v` 2x7, `cross_h` 8x2. Plate rows from the top:
r1 = y 30..31, r2 = 29..30, r3 = 28..29, r4 = 27..28, r5 = 26..27, r6 = 25..26, r7 = 24..25.
Columns 1..8 across.

**The cut, in two parts.** The **sights**: on the plate's north face leave r2 columns 2..3 and
columns 6..7 unpainted — two slots either side of the vertical band, which is what a great helm
actually gives you. The **breaths**: single unpainted texels on **one side only**, the sword side,
in r5 and r6 — three or four of them in a loose diagonal, never touching, each a separate drilled
hole. Also cut the plate's four corner texels.

**The asymmetry is the trap.** The breaths must land on the same side every time, and the box-UV
`north` strip runs texture-x toward **-x** (the `laurel` and `cheek_guards` sessions both wrote
this down), so the sheet's left is not the viewer's left. Paint the breaths, take the straight-on
screenshot, and *check* before painting anything else — everything else on this part is symmetric
and cannot tell you if you got it backwards. Say in the lessons which way it went.

Master: the plate 185 at the brow falling to 145 at the jaw; both cross bands a step brighter
(215 north, 240 `up`, 125 `down`) so the reinforce reads as riveted on top; four rivet texels at
250 along the vertical band, one every other row; a 90-value texel bordering every sight and every
breath, which is what makes a hole look like a hole rather than a printed dot. Rim strips and
south faces take a flat 130 — a face with nothing behind it is a `!`, a partly painted face is
only a note — and at a quarter texel the rim strips take whatever texel they land in.

Guard mask: both cross cubes' faces at the master's own values, rivets included.

**Corrections from the Barbute session — the first part of this family, built clean. Read these
before painting; two of them would otherwise ship a visor with no holes in it.**

1. **Cut the south face too, in the same pattern.** `armorCutoutNoCull` draws back faces, so an
   opening cut only in the north face is filled by the *inside* of the painted south face and
   stops being a hole. Every cut described above has to be made twice — once in the north
   rectangle, once in the south, and this part's asymmetric breaths must be *mirrored* into the south
   columns rather than copied to the same offsets — and where the silhouette is nipped, clear the matching
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

**Also from the Bellows Visor session — part three, built clean.**

- **The checker is completely silent about a part's own cubes.** Three ribs sharing both a front
  plane and a back plane produced no `COPLANAR`, no shared-plane line, not even a `-` note: the
  coplanarity test is strictly cross-part. So the family's "no two cubes of one part share a
  plane" rule is **yours to enforce by hand** — you will get no warning, only z-fighting in the
  game. Where this brief staggers two proud cubes by 0.05, that stagger is load-bearing.
- **A wall texel painted on a row a proud cube covers is invisible.** It is buried 0.25 deep in z.
  What actually walls an opening is the proud cube's `down` face above it and `up` face below —
  which the rim rule already paints. Spend the dark jamb texels on the **side** columns of the cut
  row instead (the ones that survive the cut), which read as the dark cheek beside the opening.
- **Lift a mask's `down` faces above the master's.** Bellows shaded its inlay to the master's own
  values except the shadow faces, raised to 120–130, because a dye applied over a 90 comes out
  near-black. Shade masks, never flat — but do not let them go darker than about 120.

**Recipe.** Centre item `minecraft:netherite_ingot` (a flat item, unused by any template), paper
ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
great_helm` and `python tools/check_authoring.py` clean; the mod page rebuilt (if the centre has never been cached,
`--offline` warns and draws a checkerboard — one plain `python -m modpage build` fetches it,
then re-run offline); the lessons paragraph below filled in. Count your paint calls and say what
the painter did and did not cover. Two answers the family wants from this session: whether
**crossing proud cubes** cost anything the checker noticed, and whether **a single-texel breath**
reads as a drilled hole or as dirt. Judge from the straight-on shot (`set_camera_angle` position
[0, 28, -24], target [0, 28, 0]) and one three-quarter ([6, 30, -22], target [0, 27.5, 0]).

**Picture budget: two screenshots, and both after the last paint call.** An image is billed by
area and re-sent on every later turn, so looks taken while painting are paid for many times over;
the leanest sessions on record took every shot after the painting was done.

## Lessons from the session

Built clean on the first pass — geometry exactly as briefed, `armorpieces_save` accepted without
`force`, `check_part`/`check_authoring` clean, page rebuilt offline (its only warning is the
pre-existing `minecraft:chain` one; `netherite_ingot` was already cached). **Two paint calls, and
that was the whole part**: one on the master (18 faces + 44 pixels — every face, the four rivets,
the ten 90-value jamb texels, and all 24 cut texels, north and south and rim, in one undo step)
and one on `part_guard` (12 faces + 4 pixels). The painter covered everything; nothing needed
`draw_shape_tool`, `paint_fill_tool` or the brush.

**Crossing proud cubes cost nothing the checker noticed — and that is worse than it sounds.**
Bellows found the coplanarity test is cross-part only; this part shows the silence is even wider.
The brief predicted the horizontal's buried faces at the crossing would come back as a `-` note.
They did not. The final report is seven lines: the six body-surface notes for x ±4 and y 24, and
the partly-painted-face line. **Not one word about the crossing** — no buried face, no overlap, no
depth. The 0.05 stagger (`cross_v` −5.60..−5.25 over `cross_h` −5.55..−5.30) is invisible to every
tool in the repo, so the next author who crosses two cubes gets no confirmation that they did it
and no complaint if they did not. Write the numbers down before placing, as here.

**A single-texel breath reads as a drilled hole, decisively — but not because of its size.** At
one texel it is exactly as big as a noise pixel; what makes it a hole is *what is behind it*. The
player's skin shows through at a warm brown no trim material can produce, so three isolated texels
on a grey cheek read instantly as three drilled holes rather than three dirty pixels. The 90-value
border is the second half of it: it gives each hole a jamb, so the eye reads depth rather than a
printed dot. Cut a single texel without the border, or over a background the same hue as the plate,
and it would be dirt. Barbute's rule stands and generalises: **the hole is the skin, not the gap.**

**Which way the asymmetry went, and how to settle it without spending a picture.** Breaths on the
wearer's **right** — the sword side — which is **Blockbench +x**, which is the box-UV `north`
strip's **low sheet-x end** (columns 13–15 of a 13..20 rect), because north texture-x runs toward
−x. The brief said to paint them and check with a screenshot; there is a cheaper and exact answer:
the reference figure's own `right_arm` cube sits at Blockbench **x 4..8**. That single fact settles
handedness for every future part, mirrored socket or not, and it cost one read. The straight-on
shot then confirmed the breaths on the viewer's left (camera at −z, so screen-right is −x) with
skin showing through, and the three-quarter from +x put them on the near cheek. Both shots were
taken after the last paint call, as budgeted.

**The south mirror, as arithmetic.** For a plate whose north rect is x 13..20 and south rect
x 22..29, the mirrored column is `x_south = 42 − x_north` — in general `north_start + south_end −
x`. Symmetric cuts (corners, the two sights) land on the same offsets and need no thought; only
the breaths actually move. Deriving the constant once and listing all 24 nulls in one `pixels`
array is much safer than mirroring by eye.

**Do not clear a rim texel for a hole that does not nip the silhouette.** The corner cuts do nip
it, so `up` 13/20, `down` 21/28, `east` 12 rows 1 and 7 and `west` 21 rows 1 and 7 were cleared.
The breath at column 13 is in the plate's *outermost* column (world x 3..4) and is right against
the east rim — and the east rim texel must **stay painted**. Clearing it would open the hole
through to the edge and turn a drilled breath into a notch in the outline. From straight on the
0.25 sliver has no projected area, so the hole still reads as a hole. The rule is: cut the rim only
where the outline itself loses a corner.

**Two deviations, both forced by the grid, both minor.** (1) The breaths are a *triangle* —
(13,5), (15,5), (14,6) — not the "loose diagonal" the brief asked for: `cross_v` buries the middle
two columns, so the sword side has three usable columns and the brief allows two rows, and a
three-hole diagonal needs three rows. The triangle reads as a drilled cluster, which is what a
breath field is. (2) The four rivets are staggered 31/32 down rows 1, 3, 5, 7 rather than run in
one column: the band is two texels wide, so a single-column rivet line sits half a texel off centre
and reads as a seam. Row 3 puts a rivet exactly on the crossing, which is where a real reinforce is
riveted.

**Free gift from the family's grid.** With the plate at y 24..31 the sights on r2 (y 29..30) land
precisely over the vanilla skin's brow/eye row, so the player's own eyes look out of them. That is
the "visor texel grid falls on the head's own" claim in `visor-styles.md` paying off literally —
worth aiming for deliberately in Savoyard's eyes.

**Recipe centres, in one command.** All three sets at once:
`grep -rl netherite_ingot --include="template_*.json" --include="fitting_template_*.json" --include="skin_template_*.json" src/main/resources/data/`
— one line, no exit-code ambiguity, and it is the whole of corrections 3 and the Sallet note.
`netherite_ingot` was free.
