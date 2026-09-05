# Brief: Savoyard

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the twelfth
batch — six parts rather than the usual four, the mod's first family that is **flat rather than
cubic** (read `docs/plans/visor-styles.md`, then `barbute.md` for the plate and the cut,
`sallet_slit.md` for the proud-cube overlap rule, and `bone_mask.md` for shading a gemstone).
This is the family's one gemstone part, and the only one whose openings are meant to read as a
*face*. From `docs/plans/visor-styles.md`:

> **Savoyard** - The death's-head visor: round eyes and a grinning row of teeth, a stone set in
> the brow. Opening: two eyes, a nose, a toothed grin. Fitting: `gemstone` (the brow stone).

The Savoyard is a real seventeenth-century harquebusier's helmet whose visor was pierced as a
skull — this is the historical part, not the fantasy one, and it should look grim rather than
comic.

**Part.** `armorpieces:savoyard`, socket `brow` only, in the mod's own pack
(`src/main/resources`, namespace `armorpieces`), so the master lives in
`tools/decoration_masters/savoyard.png` and is installed on save. Display name "Savoyard".
Fittings: `armorpieces:gemstone`, one mask, covering the brow stone only. No static layer — the
whole family stays on the master, so an iron suit gives a grey death's head and a gold one a
gilded skull. No effects, no loot.

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
**x -4..4, y 24..30, z -5.35..-5.10** — eight wide, six tall, a quarter thick. A `brow` bone with
a band **x -3..3, y 29..31, z -5.60..-5.30**, proud and lapping the plate's top row. A `stone`
bone with a cube **x -0.5..0.5, y 29..30, z -5.85..-5.55**, centred on the band and standing a
further quarter proud, overlapping the band's front by 0.05.

Each proud cube laps the one under it by a whole texel row (or 0.05 in z for the stone), so **no
two faces of this part are coincident** — self-coplanarity is not flagged by the checker and
z-fights in the game anyway (`browband`'s lesson). Buried faces underneath are `-` notes and
correct. Expected too: side faces on x = ±4 and the plate's bottom face on y = 24, and overlap or
near lines against `ruff` (Blockbench y 24.4..26.0, z -7.5..3.5, x ±5.5), which is right for a
faceplate but must not become a shared plane. Nothing above y 31, nothing in front of z -5.85 — a
quarter shallower than `bone_mask` at -6.10, so the family keeps its own depth band.

**Sheets.** The plate is 8x6 texels, the band 6x2, the stone 1x1 on every face — so the plate
takes `pixels` and the stone is per-face values (**anything under two units on an axis is one
texel there**, the rule `laurel` wrote down). Plate rows from the top: r1 = y 29..30 (behind the
band except at columns 1 and 8), r2 = 28..29, r3 = 27..28, r4 = 26..27, r5 = 25..26, r6 = 24..25.

**The cut, and it is the face.** On the plate's north face leave unpainted: **the eyes**, r2
columns 2..3 and columns 6..7, two square sockets; **the nose**, one texel at r3 on a centre
column, or a two-texel inverted V if one reads as a smudge; **the grin**, r5 columns 2..7 with
alternate texels *left painted* — the painted ones are the teeth and the cut ones are the gaps,
which is how the real visor was pierced and is the only place in this mod where the paint and the
hole trade places. Cut the plate's four corner texels so the skull tapers to a jaw.

An unpainted texel is *absent*, not transparent, so the player's own face sits 1.35 units behind
every one of these, and the eyes in particular will show skin. **The Great Helm session has
half-answered this**: skin through a cut is what makes a hole read as a hole at all, so the
expectation now is that the eyes work and are the best thing on the part. What is still open is
whether it survives at *eye* scale — a 2x2 socket showing a whole eye is a different proposition
from a one-texel breath showing a cheek. Say which in the lessons. If it does fail, the fix is a
second plate 0.3 behind the eyes rather than filling the cut, and that is a decision for the
family, not just this part.

Master: the plate 175 at the brow falling to 140 at the jaw, with a 200 highlight along each
cheekbone (r3, the outer columns) and 110 under the eye sockets so the skull has hollows; the band
brighter, 225 on its top row and 185 below; a 90-value texel bordering every cut, which gives each
opening a wall; the teeth themselves at 235, brighter than anything but the stone, because that
row is the part people will remember. The stone: 235 north, 250 `up`, 130 underneath. Rim strips
and south faces take a flat 125 — a face with nothing behind it is a `!`, a partly painted face is
only a note.

**Gemstone mask**: the stone's six faces at those same values, not a flat fill — a flat mask kills
the lit top texel when a gem is fitted, which `knee_studs` and `talons` found the hard way and
`bone_mask` fixed by shading its stones.

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

**Recipe.** Centre item `minecraft:skull_banner_pattern` (a flat item, unused by any template —
`bone` and `bone_meal` are both taken, and `skeleton_skull` was rejected because a head has no flat
item sprite for the recipe icon). Paper ring. If the pattern item turns out to have no flat sprite
either, fall back to `minecraft:ghast_tear` and say so.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py savoyard`
and `python tools/check_authoring.py` clean; the mod page rebuilt (if the centre has never been cached,
`--offline` warns and draws a checkerboard — one plain `python -m modpage build` fetches it, then
re-run offline); the lessons paragraph below filled in. Count your paint calls and say what the painter
did and did not cover. Judge from the straight-on shot (`set_camera_angle` position [0, 28, -24],
target [0, 28, 0]) and one three-quarter ([6, 30, -22], target [0, 27.5, 0]) — and say whether a
skull made only of holes reads at three metres, because that is the one thing eight texels may not
be enough for.

**Picture budget: two screenshots, and both after the last paint call.** An image is billed by
area and re-sent on every later turn, so looks taken while painting are paid for many times over;
the leanest sessions on record took every shot after the painting was done.

## Lessons from the session

Built clean, saved without `force`, both checkers and the page rebuild clean. Three bones
(`mask` → `brow` → `stone`, chained), three cubes, every number in the brief used unchanged.
**Two paint calls in total**: one master (18 faces + 64 pixels) and one `part_gemstone` (6 faces).
No shape tool, no brush, no eraser.

- **`armorpieces_paint` applies `faces` first and `pixels` second, and `pixels` accepts `null`.**
  That is the whole part in one call: `plate.north: [175, 140]` lays the brow-to-jaw gradient, the
  flat 125 goes on the south and the four rims, and then 64 texels overwrite the greys that differ
  and *clear* the ones that are cut. Painting and cutting are the same call. Everything after this
  brief should assume one call per sheet is genuinely enough, even for a 48-texel face.
- **The answer on the eyes: they read, they are the best thing on the part, and they are not
  pink.** Skin through a cut at eye scale holds — but for a reason a one-texel breath never had,
  and it is worth being precise about it. Great Helm's breath showed *cheek*: an undifferentiated
  warm brown. An eye socket shows the skin's **eye texel**, which on the default skin is white
  sclera plus a saturated blue-violet iris. Straight on that reads as a dark hollow with a glint;
  from three-quarters the blue is plainly visible. So the hue that sells the hole is not skin-brown
  at this scale, it is *contrast* — and pink was never the risk, because the eye region of a
  humanoid skin is the least pink part of the face. The 90-value jamb on columns 1 and 8 still does
  the work of walling it; the fix (a second plate 0.3 behind) was not needed and should stay
  unspent.
  The caveat for the family: because you see a real eye, this reads as *a face looking through a
  death's-head*, not as an empty skull. For the Savoyard that is correct and historical. A part
  that wants a genuinely empty socket needs the backing plate, and now there is a reason to build
  one.
- **The eyes are 2 wide × 1 tall, not 2×2.** The brief calls them "two square sockets" but names
  only r2, and r3 is spent on the 110 hollows and the 200 cheekbones — so they cannot be square
  without eating the only sculptural row on the face. One row is enough; do not read "square"
  as a size.
- **A symmetric cut pattern makes the back-face rule free.** Barbute's rule is to cut the same
  pattern in the south face, and the south face's columns run the other way. Every opening here is
  mirror-symmetric about the centre, so the south pixel list is the north list at a different x
  offset with no reversal — no handedness bookkeeping at all. Worth designing for.
- **Strict alternation cannot be symmetric over an even run.** Six mouth columns (2..7) alternating
  gives col 2 painted and col 7 cut. Symmetry won: holes at 2, 4, 5, 7 and teeth at 3 and 6 —
  hole, tooth, hole-hole, tooth, hole. That is also what the real Savoyard is, a broad mouth
  crossed by two bars, so the deviation from "alternate texels" is a correction rather than a
  compromise.
- **Does a skull made only of holes read at three metres? Yes, but the eyes and nose carry it and
  the grin does not.** The two eye holes plus the one centred two-texel nose are unmistakably a
  face; the 235 teeth are only two texels and at that distance the mouth row reads as a broken
  dark bar rather than as teeth. Ten cut texels was the right number — eight would not have been.
  If Frog-Mouth wants a mouth to read on its own, it needs more than two painted texels in the
  row, or a row two texels tall.
- **The check cannot verify a cut.** A partly painted face is only a note, so nothing in
  `armorpieces_check` or `check_part.py` confirms that the eyes landed on r2 rather than r1. Dump
  the saved master with Pillow instead — `tools/decoration_masters/<part>.png`, print each face
  rectangle as a grid of values with `.` for alpha 0. It took one command and confirmed all 64
  texels; it should be the standard last step for anything in this family.
- **`minecraft:skull_banner_pattern` was not in the page cache and does have a flat sprite.** One
  plain `python -m modpage build` fetched it and the missing-texture warning dropped from two
  items to one (`minecraft:chain`, pre-existing and not this part's). No fallback to `ghast_tear`
  needed.
- **The gem is 1×1 and will not read on the master alone** — 235 north over a band whose lower row
  is 185 is a stud, not a jewel. That is correct: the `gemstone` fitting is what makes it a stone,
  and the mask is shaded (250 up / 235 north / 205 east / 180 west / 130 down) so a fitted gem
  keeps its lit top instead of going flat, per `bone_mask`. Every mask value is at or above 130,
  so nothing crushes to near-black under a dye.
- Accepted `-` notes, all three predicted by the brief: the plate's x faces on ±4 and its bottom
  face on y 24 lie on the head box's own planes, where there is no geometry 1.35 units forward.
  `ruff` never appeared, as correction 4 said it would not; the plate is in front of it, not
  sharing a plane with it. Depth stagger (plate −5.35 / band −5.60 / stone −5.85, each lapping by
  0.05) is unverifiable by tool and was placed by hand.
