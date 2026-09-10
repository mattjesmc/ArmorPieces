# Brief: Frog-Mouth

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the twelfth
batch — six parts rather than the usual four, the mod's first family that is **flat rather than
cubic** (read `docs/plans/visor-styles.md`, then `barbute.md` for the plate and the cut and
`sallet_slit.md` for the proud-cube overlap rule). **Build it last.** It is the boldest silhouette
in the family — almost the whole face is blank — and it should be judged against the five that
came before it. From `docs/plans/visor-styles.md`:

> **Frog-Mouth** - The jousting helm: one slot right at the top and a huge blank face jutting
> below it, so it only sees when the head is bowed. Opening: one slot at the brow.
> Fitting: `guard` (the lip).

The *Stechhelm* is the most extreme face in armour: a single slot placed so high that the wearer
sees through it only while couched forward over the lance, and is blind the moment he sits up.
That is the idea to sell, and it is sold by how much steel sits under the slot, not by detail.

**Part.** `armorpieces:frog_mouth`, socket `brow` only, in the mod's own pack
(`src/main/resources`, namespace `armorpieces`), so the master lives in
`tools/decoration_masters/frog_mouth.png` and is installed on save. Display name "Frog-Mouth".
Fittings: `armorpieces:guard`, one mask, covering the lip only — the plate stays the helmet's
material and the reinforce over the sight takes a second metal. No static layer, no effects, no
loot.

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

**Shape.** Two bones. `mask` pivoted at the anchor (0, 28, -4) with a `plate`
**x -4..4, y 24..31, z -5.35..-5.10** — the full faceplate. Then `lip`, a child bone with a band
**x -4..4, y 27..29, z -5.60..-5.30**, full width, two tall, 0.30 thick, sitting proud across the
middle of the face.

The lip is what makes it a frog-mouth rather than a blank plate: the sight is at the very top, and
the steel below it steps *out* toward the viewer, so the face reads as jutting forward and upward
the way the real helm's does. It sits 0.05 inside the plate's front face and shares no plane with
it — self-coplanarity is not flagged by the checker and z-fights in the game anyway
(`browband`'s lesson). The plate's faces buried behind it are `-` notes and correct.

Expected notes: side faces on x = ±4, the plate's bottom face on y = 24, and overlap or near lines
against `ruff` on `collar` (Blockbench y 24.4..26.0, z -7.5..3.5, x ±5.5) — right for a faceplate,
but not as a shared plane.

**Sheets.** The plate is 8x7 texels and the lip 8x2. Plate rows from the top: r1 = y 30..31,
r2 = 29..30, r3 = 28..29, r4 = 27..28 (behind the lip), r5 = 26..27 (behind the lip), r6 = 25..26,
r7 = 24..25.

**The cut.** One slot and nothing else: on the plate's north face leave **r2 columns 2..7**
unpainted. It sits one row below the top edge, which is as high as a sight can go and still have
steel above it, and everything under it — five rows, forty texels — stays solid. Resist adding
breaths; the blankness is the part. Cut the plate's four corner texels only so the outline is a
helmet rather than a board.

Master: this part has almost no detail, so all of it is in the grade. Give the plate a long
`[top, bottom]` fall from 210 at r1 to 120 at r7 — a single sweep down the whole face, brightest
right at the sight — then the lip a step brighter than the plate behind it (215 north, 245 `up`,
120 `down`) so the step catches a hard line of light across the middle. A 90-value texel along the
top and bottom edge of the slot gives it a wall. Two rivet texels at 250 on the lip, near the
ends. Rim strips and south faces take a flat 125 — a face with nothing behind it is a `!`, a
partly painted face is only a note — and at a quarter texel the rim strips take whatever texel
they land in.

Guard mask: the lip's faces at the master's own values, rivets included.

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

**Also from the Great Helm session — part four, built clean.**

- **The hole is the skin, not the gap.** A single-texel breath reads as a drilled hole, and it is
  *not* the size that does it: at one texel it is the same as a noise pixel. What makes it a hole
  is the player's own skin showing through in warm brown, a hue no trim material produces, plus
  the 90-value jamb beside it giving it depth. Without the jamb, or over a background of the same
  hue, it would read as dirt. Every cut in this brief depends on that contrast, so keep the jamb.
- **The checker's silence about your own cubes is total** — not just coplanarity. Great Helm's
  horizontal band is buried inside its vertical at the crossing and not one line mentions the
  crossing, the overlap or the depths. Any depth stagger in this brief is unverifiable by tool.
- **Handedness, settled once**: the wearer's **right** (the sword side) is Blockbench **+x**, which
  is the **low sheet-x end** of a north face's strip. It was derived from the reference figure's
  `right_arm` cube at Blockbench x 4..8, without spending a screenshot on it.

**Also from the Savoyard session — part five, built clean, and the last one before this.**

- **Nothing in either checker verifies that a cut landed where you meant it.** A partly-painted
  face is only a note, so the report will look identical whether the slot is on the right row or
  one row off. Dump the saved master with Pillow and confirm the texels — north pattern, mirrored
  south pattern, cleared rim texels — before you call it done.
- **`armorpieces_paint` can do the whole sheet in one call**: it applies `faces` then `pixels`,
  and `pixels` accepts `null`, so the gradient, the grey detail *and the cuts* go in one call. The
  shape, brush and eraser tools were never needed on any part of this family.
- **A mouth needs more than two painted texels, or a row two texels tall.** Savoyard's grin put
  two 235 teeth in six columns and it reads as a broken dark bar rather than as teeth — the one
  weak thing in the family so far. This brief's opening is full-width, so give the row enough
  surviving material to read as an edge, and do not thin it further than specified.
- **A cut shows the skin's *eye* texel, not just cheek** — sclera plus a saturated iris, which is
  contrast rather than hue, and it is why an opening at eye height reads best of all. It also
  means an opening at eye height reads as *a face looking through*, not as an empty helmet. That
  is right for a visor and needs no backing plate; do not spend one.

**Recipe.** Centre item `minecraft:trident` (a flat item, unused by any template — the closest
thing the game has to a lance), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
frog_mouth` and `python tools/check_authoring.py` clean; the mod page rebuilt (if the centre has never been cached,
`--offline` warns and draws a checkerboard — one plain `python -m modpage build` fetches it,
then re-run offline); the lessons paragraph below filled in. Count your paint calls and say what
the painter did and did not cover. This session closes the family, so it owes a verdict as well as
a part: across the six, **did flat plates earn their place next to the cubic `visor`**, and is
there a seventh worth cutting (`visor-styles.md` lists the spectacle visor and the klappvisier as
the ones held back)? Judge from the straight-on shot (`set_camera_angle` position [0, 28, -24],
target [0, 28, 0]) and one three-quarter ([6, 30, -22], target [0, 27.5, 0]).

**Picture budget: two screenshots, and both after the last paint call.** An image is billed by
area and re-sent on every later turn, so looks taken while painting are paid for many times over;
the leanest sessions on record took every shot after the painting was done.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-05 in 18 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 2 `add_group`,
2 `place_cube`, 2 `remove_element` (`main_0` then `main`), 2 `armorpieces_set_part`, 1
`armorpieces_part`, **2 `armorpieces_paint`** (master, guard mask), 1 `armorpieces_check`, 2
`set_camera_angle`, 1 `armorpieces_save`, 1 `armorpieces_close`. No `risky_eval`, no `modify_cube`,
no `list_outline`, no shape/brush/eraser tool, nothing hand-edited, no nudging; the save went
through first time **without `force`**. Geometry is exactly the brief's: `mask` at (0, 28, -4) with
`plate` x -4..4, y 24..31, z -5.35..-5.10 (uv 12,0 8x7x0.25 — up 13,0 8x1, down 21,0 8x1, east
12,1 1x7, north 13,1 8x7, west 21,1 1x7, south 22,1 8x7) and child bone `lip` at (0, 28, -5.3)
with `band` x -4..4, y 27..29, z -5.60..-5.30 (uv 30,0 8x2x0.3 — up 31,0 8x1, down 39,0 8x1, east
30,1 1x2, north 31,1 8x2, west 39,1 1x2, south 40,1 8x2). Final check: six `-` notes (four `x face
at ±4`, `mask`'s `y face at 0`, and the partly-painted line `down 6/8, east 6/7, north 48/56, west
6/7, south 48/56`), `ok: nothing needs a decision`, `all clear by more than half a unit`.

**The brief's own row table is off by one, and it matters for exactly one thing.** With rows
r1 = y 30..31 … r7 = y 24..25, a band at **y 27..29 covers r3 and r4**, not "r4 and r5" as the
sheets paragraph says. Nothing in the painting changes — the plate's gradient is continuous and
both buried rows take it — but the consequence is the good one: the lip's **top edge is y 29, which
is exactly the slot row's bottom edge**, so the lip's `up` face is the sight's sill. That is
Bellows' rule arriving for free ("when a proud cube laps a cut row exactly, the proud cube's rim
faces are the opening's wall"), and it is why the wall texels below the slot were not needed.

**Three deviations, each one a correction the brief itself carries.**
1. **Only the two bottom corners are cut, not four.** The brief says "cut the plate's four corner
   texels" and then quotes Barbute's rule warning against it; the rule wins. The opening is r2
   columns 2..7, so r1 minus its two corners would be columns 2..7 sitting directly over six cut
   texels with nothing beside it — Barbute's severed brow exactly. Note the difference from
   Bellows, which *did* cut all four with the same 2..7 opening: there the opening was on r3/r5,
   not the row under the top edge. The rule is about **adjacency to the plate's own edge row**, not
   about the opening's column span: a full-width opening one row from an edge forbids that edge's
   corners; one row from the middle forbids nothing.
2. **The 90-value walls went sideways, not above and below.** The row under the slot (r3) is buried
   behind the lip and a wall there is invisible (Bellows); the row above it (r1) is the brow, and
   Barbute found bright-above separates a hole better than dark-above. So the four 90s are on the
   cut row's **surviving side texels** — r2 columns 1 and 8, north and south — and the opening's
   real jambs are the lip's `up` face (245) below and the plate's own top edge above. Four wall
   texels is the fewest of any part in the family and the hole still reads.
3. **`band.north` is [230, 200], not a flat 215.** Sallet's rule is that a proud band must sit
   *outside* the plate's value range, and this plate runs 210..120, so a flat 215 would have been
   inside it at the top. 230/200 keeps the top row above every plate texel while averaging the
   brief's number. `band.east`/`west` are 150 rather than the flat rim 125, and `up` 245 / `down`
   120 as briefed — the lit ledge and the overhang shadow are the whole of what the step reads as
   from three quarters, and Sallet's "do not flat-paint a proud cube's rim" was applied verbatim.
   The two 250 rivets went on the band's **lower** row (over 200) rather than the top (over 230),
   for the same separation reason.

**Two paint calls, and what the painter did and did not cover.** Master: 7 face entries (`*.*` 125,
`plate.north` [210, 120], `band.east`/`band.west` 150, `band.north` [230, 200], `band.up` 245,
`band.down` 120) resolving to 18 faces, plus 26 pixels — 4 jambs at 90, 2 rivets at 250, and 20
nulls (6 slot texels on north at x 14..19 y 2, 6 mirrored on south at x 23..28 y 2, 4 bottom
corners at 13/20,7 and 22/29,7, and 4 rim clears at `down` 21,0 and 28,0, `east` 12,7, `west`
21,7). Guard mask: 6 face entries and 2 pixels, the band's own master values with `down` lifted
120 → 130 per Bellows. Verified with Pillow on the **saved** files: master 174 opaque texels,
greyscale, range 90..250, nothing outside a face rectangle; mask 52 texels, range 125..250, a
strict subset of the master's band. What the painter did **not** do: no gradient on the plate's
south face or any rim (flat 125 — the inside of a visor is never lit), no wall texels on the rows
the lip buries, and no cut on the band at all, so its rims stay whole.

**The sight lands on the eyes, not the forehead — Sallet's prediction was one row out.** Sallet
reasoned that a slot at the very brow would show forehead; but r2 of a **y 24..31** plate is
y 29..30, and Great Helm already measured that row as the vanilla skin's brow/eye line. The
straight-on shot confirms it: two eye texels and warm skin through the slot. So the frog-mouth's
"blind unless bowed" is sold entirely by the **five blank rows and the proud lip below** the sight,
not by the sight missing the eyes — and that is better, because the part reads as a man looking out
of a wall of steel rather than as an empty box. A plate that genuinely wants to clear the eye row
has to stop at y 25..31 or higher, not just put its slot at the top.

**Both shots, and the verdict this session owes.** Straight on: a thin lit brow, a dark full-width
slot with the player's eyes in it, the bright lip stepping out across the middle, then five rows
falling 165 → 120 to a chin nipped at both corners. At three metres the shape that registers is the
**mass under the slot**, exactly as the brief hoped, and it is legible with no fitting applied.
Three quarters: the lip's 245 top face is a hard white line across the face and the 120 underside
turns it into an overhang — the same finding as Sallet and Bellows, now on the plainest part in the
family.
*Did flat plates earn their place next to the cubic `visor`?* **Yes, decisively, and this part is
the proof rather than the exception.** Six faces, each unmistakably a different helmet, from one
8×7 slab and at most three small cubes; ~15–18 bridge calls and **two paint calls** each, the
cheapest family the mod has built. They do not compete with `visor` because they answer a different
question: `visor` gives the helmet a *shape* in profile, these give it a *face* head-on, and the
cut — the player's own skin at a hue no trim material makes — is a thing geometry cannot do at all.
The family's one real limit is scale: Savoyard's two teeth and its 1×1 gemstone are the only weak
things across the six, and both are small detail. Frog-Mouth has the least detail of any of them
and is the most readable, which settles the design rule for anything that follows: **on a flat
plate, spend the budget on silhouette and value break, never on texel detail.**
*Is a seventh worth cutting?* **One, and then stop.** The **klappvisier** should stay dead —
`visor-styles.md` was right that it collapses onto Sallet Slit once flattened, and building Sallet
confirmed a single slot under a band is already that part. The **spectacle visor** is worth
building, but for a reason the plan did not have: a *brille* is a raised border with an eye-shaped
hole **through the raised part**, and all six of these cut the plate and never the band (Sallet and
Bellows only nipped their bands' corners). A cut proud cube — with its `up`/`down`/`east`/`west`
rim texels cleared around the opening, and the plate behind it left solid or cut through as a
second decision — is genuinely new, and it is the only new mechanism left in flat plates. After
that the socket has eight visors and thirteen brow parts, and a ninth flat plate would be
repetition. The better 0.3.x move in this space is not a part at all: it is a **north-facing
`banner` fitting**, which would let the finished `frog_mouth` carry real arms and turn the
tournament helm idea from "a part we cannot build" into a fitting on one we already have.

**modpage.** The usual three-step dance: `--offline` drew `minecraft:trident` as a checkerboard,
one plain `python -m modpage build` fetched it (the missing-texture list dropped from four items to
three), and the third build reported `unchanged` on all three outputs. `modpage.yml` needed
nothing. The remaining warnings — `minecraft:chain`, `armorpieces:cloth_template`,
`minecraft:white_carpet`, two `armorpieces:smithing_skin` and two `armorpieces:smithing_cloth`
recipes — are pre-existing and belong to a concurrent cloth feature, not to this part. `trident`
was cleared against all 87 `template_*`, four `fitting_template_*` and fourteen `skin_template_*`
grids with Great Helm's one-line `grep -rl` before `set_part`, so the recipe passed first time.
One small thing for the next author: `armorpieces_set_part` echoes the display name **normalised**
(it reported `Frog Mouth` for a name of `Frog-Mouth`) and `armorpieces_part` reports `recipe: null`
until the save — both are display quirks, not lost data; the saved `en_us.json` line is
`"Frog-Mouth"` and the recipe file has the trident. Do not re-issue `set_part` to "fix" either.
