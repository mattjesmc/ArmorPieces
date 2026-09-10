# Brief: Chain Belt

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the tenth
batch of four (read cord.md and pouch_belt.md first - same socket, the ring of plates, the arm
box the check cannot see, the tassel in the crotch gap). From the `belt` row of
`docs/plans/part-variety.md`:

> **Chain Belt** - A draped loop of chain slung across the hips. Theme: Court. Fitting: `guard`.

**Part.** `armorpieces:chain_belt`, socket `belt` only, in the mod's own pack. Display name
"Chain Belt". Fittings: `armorpieces:guard`, one mask, covering the whole chain and its drop -
it is all metal. No effects, no loot, no static layer.

**Shape.** `belt` is not a mirrored socket: model the whole thing on the body bone. The torso
box is x -4..4, y 12..24, z -2..2 (pivot 0, 24, 0); the leggings shell is that box inflated 0.5
and the chestplate's a full unit (x -5..5, y 11..25, z -3..3), so every chain face lies past
x ±5 or z ±3; the anchor is at Blockbench (0, 12, 0). The player's ARMS hang at x ±4..±8,
y 12..24, z -2..2 on their own bones and the check never mentions them, so anything at the
flank above y 12 inside that box is invisible - the drape goes on the FRONT. Read the envelopes
in the `armorpieces_new` reply (other belt parts never compared; back parts on the bone start
at y 14.5 and up, so a belt at y 12.4..12.8 is clear). Build: a `chain` bone with a ring of four
bars 0.4 square in section at y 12.4..12.8 a tenth off the shells (front z -3.5..-3.1, back
z 3.1..3.5, flanks x ±5.1..±5.5, each the full span so the corners double up) - the chain
itself, its links painted; then the drape, two bones `drape_l` / `drape_r` pivoted on the front
bar at the hips (x -4.6, y 12.4, z -3.3) and (x 4.6, y 12.4, z -3.3), each carrying a bar 0.35
square modelled straight DOWN from its pivot, 5.2 long, the bones rotated about Z so the two
bars meet low at the centre in a V - the left bar (negative x) needs a POSITIVE Z rotation of
about 62 degrees to swing its free end toward +x (pendant measured the sign: for a cube below
its pivot, positive Z swings the free end toward +x), the right bar the negative of that;
compute the ends so they meet at about (0, 10.0) and lap each other by a quarter unit; and a
`drop` bone at the V's point with a link 0.5 square and a hanging tag 0.9 wide, 1.1 tall, 0.35
thick under it, z -3.75..-3.4, from y 10.0 down to y 8.6. The tag hangs in the gap between the
thighs (x ±0.45), in front of the leggings, as cord's tassel does. Nothing below y 8.5, nothing
above 12.8.

**Sheets.** Master: bars mid grey with the links suggested by alternating light and dark texels
along every visible row (`pixels`), the drape bars the same, link and tag bright with a
brightest top face and one dark texel as the tag's setting. Guard mask: every face at the same
values, link pixels included.

**Recipe.** Centre item `minecraft:golden_leggings` (a flat item, unused by any template),
paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
chain_belt` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-04 in 19 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`armorpieces_part`, 1 `list_outline`, 2 `remove_element` (starter cube, then its bone), 4
`add_group`, 4 `place_cube`, 1 `armorpieces_set_part`, **2 `armorpieces_paint`**, 2
`armorpieces_check`, 3 `set_camera_angle`, 1 `armorpieces_save`. No `risky_eval`, no
`modify_cube`, nothing hand-edited, no repaint pass, and the save went through first time
without `force`. `check_part.py chain_belt` and `check_authoring.py` were clean on the first
run, and `python -m modpage build --offline` needed no non-offline follow-up: **`minecraft:golden_leggings`
was already in modpage's icon cache**, the first belt centre item in a while that did not cost a
second build.

**What I built.** Four bones, eight cubes, two rotations. `chain` (pivot 0, 12.6, 0): four bars
0.4 square in section at Blockbench y 12.4..12.8 - `bar_front` x -5.5..5.5 z -3.5..-3.1,
`bar_back` the mirror at z 3.1..3.5, `bar_left` x -5.5..-5.1 and `bar_right` x 5.1..5.5 both
running the full z -3.5..3.5 so the corners double up. `drape_l` (pivot -4.6, 12.4, -3.295,
rotated **+62 deg about Z**) and `drape_r` (pivot 4.6, 12.4, -3.29, **-62 deg**), each with one
bar 0.35 wide and **5.26** long modelled straight down from the pivot. `drop` (pivot 0, 10.05,
-3.55, no rotation): `link` 0.5 cubed at y 9.55..10.05, z -3.8..-3.3, and `tag` 0.9 x 1.1 x 0.35
at y 8.6..9.7, z -3.75..-3.4. Envelope x +-5.50, Blockbench y 8.60..12.80, z -3.80..3.50; reach
6.71; `all clear by more than half a unit` from every other part on the body bone - not one clash
or near-miss note in the whole run.

**The bar length is not a free number: it is solved from the lap, and 5.2 is 0.1 short.** The
brief asks for a 5.2-long bar *and* a quarter-unit lap at the centre, and those two cannot both
hold. For a bar of half-width w = 0.175 pivoted at x = -4.6 and rotated by t about Z, the far
end's greatest x is `-4.6 + w*cos t + L*sin t`; setting that to +0.125 (so the two bars overlap
x -0.125..0.125) gives L = 5.2578, i.e. **5.26**, not 5.2. At the brief's literal 5.2 the lap is
only 0.147. The finished tips span x -0.038..0.126 (left bar) and the mirror, y 9.776..10.085,
so they meet at about (0, 9.93) - the brief's "(0, 10.0)" to within a tenth - and the check
confirmed the envelope to the hundredth with no nudging. The rotation sign the brief inherited
from pendant is right: **below the pivot, +Z swings the free end toward +x**, so the LEFT
(negative-x) bar takes +62.

**Two cubes of the same part in the same z slab will z-fight, and no check line says so.** The
two drape bars overlap at the tips, and if both are modelled at z -3.475..-3.125 their z faces
are *identical planes* over that overlap - a rotation about Z leaves z alone. The check reports
coplanarity against the shells and against other parts, never within the part, so this would
have shipped as flicker. Fix: nest the slabs instead of matching them - left bar z -3.47..-3.12
(0.35 thick), right bar z -3.44..-3.14 (0.30 thick), fully inside the left's range where they
cross. At one texel per unit both still read as the same 0.35 bar. Same rule kept every other
plane distinct: the chain's front slab is -3.5..-3.1, the drape bars are strictly inside it, the
link is -3.8..-3.3 and the tag -3.75..-3.4, so nothing anywhere in the part shares a plane with
anything else, and the `!` list never had a coplanar line on it.

**Two paint calls, and why it was not four.** Call 1 was the whole master: `"*.*": 150`, then a
`chain[i].*` base of 145 per bar, then all 48 faces by name, plus **133 `pixels`**. Call 2 was
the guard mask - the master's map copied **verbatim**, all the same faces and all 133 pixels,
because the brief wants the whole part to take the material. No touch-up pass was needed: every
value was chosen in 105..240 up front, the band pouch_belt and cord found safe on the preview
ramp, and the first screenshot was already right. The 133 pixels are the links: alternating
205/120 along **every** long outward row - both 11-texel rows of the front bar and of the back
bar, both 7-texel rows of each flank, and the 6-texel north face of each drape bar - plus
170/215 alternating **one texel out of phase** along all four `up` rows so the highlight walks
around the ring, plus 235/175 down the two drape bars' lit sides, plus one dark 110 texel as the
tag's setting. Pillow confirms both sheets 220 opaque texels spanning 105..240, zero coloured
pixels on either, zero mask texels outside the master's silhouette. What the painter did **not**
cover: there is no seam where the four bars double up at the corners, no painted ring-and-pin on
the link (it is a 1x1 face - there is nowhere to put one), no device or engraving on the tag
(its front is a single 1x2 column: one texel of setting, one texel of tag), and the `down` faces
of the whole ring are a flat 105 with no link rhythm, since nothing looks up at a belt.

**A trap in addressing faces: `chain[0]`..`chain[3]` are ambiguous, cube names are not.** Four
cubes in one bone come back as `chain[0..3]` in the check's sheet layout, and the pixel
coordinates are only given under those labels - but which index is `bar_front` is a guess until
the paint reply echoes the names back. I removed the guess by painting the two 11-long bars
identically and the two 7-long flanks identically, so the mapping could not matter; the reply
then confirmed placement order does hold (chain[0] = bar_front, [1] = back, [2] = left,
[3] = right). Cheaper than a probe call, and the symmetric treatment is what a chain wants
anyway - it has links all the way round.

**The `!`s I accepted: none.** The only `!` that ever stood was the running unpainted-face count,
cleared by the first master call, and the single `-` note ("master: every pixel is transparent")
went with it.

**For the next part.**
- Eight cubes on a 64x32 sheet used rows 0..6 only (220 texels): a `belt` ring of 0.4-square bars
  is almost free, since every long face is a one-texel strip.
- The envelope table's minimum for `quiver:back` is Blockbench y 12.74 and for `banner:back`
  y 8.50 - both *bounding boxes* that overlap a belt at y 12.4..12.8 on paper. I nearly moved the
  ring down 0.2 over that and did not need to: the check compares real cubes, said `all clear by
  more than half a unit`, and cord (back plate at y 12.5..13.0, z 3.1..3.6) had already got away
  with the same numbers. **Place from the brief, then read the clash lines; do not pre-dodge a
  bounding box.**
- The arm box (`|x| > 4`, `-2 < z < 2`, `y > 12`, invisible, never mentioned by the check) cost
  nothing again: the ring crosses front and back, and both drape pivots are at z -3.3, forward of
  it, so the whole V hangs where it can be seen.
- The drop occupies the crotch gap at x -0.45..0.45, z -3.4..-3.8, Blockbench y 8.6..10.05 -
  dead centre, where cord put its tassel to the left (x -1.45..-0.55). Those two are the only
  belt parts down there and they are never worn together, but a future belt hanger has now got
  both the centre line and the left hip taken as precedent; take the right hip.
- `minecraft:golden_leggings` is now used by `template_chain_belt`. It is a flat item and its
  icon was already cached, so `--offline` was enough.
