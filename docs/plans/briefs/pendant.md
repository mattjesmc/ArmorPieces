# Brief: Pendant

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the second
batch of four (skim the lessons in girdle.md for the body-bone frame and wing_cases.md for the
Z-rotation sign). From the `collar` row of `docs/plans/part-variety.md`:

> **Pendant** - A cord with a single hanging stone at the sternum. Theme: Court. Fitting:
> `gemstone`.

**Part.** `armorpieces:pendant`, socket `collar` only, in the mod's own pack. Display name
"Pendant". Fittings: `armorpieces:gemstone`, one mask, covering the stone only - the cord stays
the material's metal, a fine chain. No effects, no loot, no static layer.

**Shape.** `collar` is not a mirrored socket: model the whole thing, centred on x = 0, on the
body bone. The torso box is x -4..4, y 12..24, z -2..2 (pivot 0, 24, 0); the chestplate shell is
that box inflated a full unit, x -5..5, y 11..25, z -3..3, and the anchor is at Blockbench
(0, 23, -2) on the chest's front face. Anything with z above -3 is buried; the cord lies on the
chestplate at z -3.35..-3.1. Read the envelopes in the `armorpieces_new` reply; the other body-
bone sockets (belt, back) are far from the upper chest, so expect a clean bone. Build a V of
two cords, each its own bone: a cube 0.5 wide (x), 4.5 long (y), 0.25 deep (z), modelled
straight down from its pivot at the collarbone (pivots at about (-3.2, 24.3, -3.225) and
(3.2, 24.3, -3.225)), the bones rotated about Z so the two cords meet at the sternum - about
-35 degrees on the left cord (negative x side) and +35 on the right; check the first one's
envelope in the reply and flip the sign if it swung outward. Compute where the ends land
(pivot + L x (sin θ, -cos θ)) so they meet at about (0, 20.6). A `stone` bone at the meeting
point holds a bail cube 0.75x0.5x0.5 at y 20.5..21 and the stone 1x1.5x0.75 at x -0.5..0.5,
y 19..20.5, z -3.85..-3.1. Nothing above y 25 and nothing wider than x ±4.

**Sheets.** Master: cords mid-grey with a lighter top row (chain catching light); bail and
stone bright `[top, bottom]` with a dark underside and one brightest specular texel on the
stone's front face (the `pixels` list). Gemstone mask: the stone's faces only, not the bail.

**Recipe.** Centre item `minecraft:lapis_lazuli` (a flat item, unused by any template), paper
ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py pendant`
and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons paragraph below
filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

Built 2026-09-03 in 20 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`armorpieces_part`, 1 `list_outline`, 3 `add_group`, 3 `place_cube`, 2 `remove_element` (starter
cube, then its bone), 1 `armorpieces_set_part`, **2 `armorpieces_paint`**, 2 `armorpieces_check`,
2 `set_camera_angle`, 1 `armorpieces_save`. No `risky_eval`, no `modify_cube`, nothing nudged,
nothing hand-edited, and the save went through first time without `force`.

**What I built.** Three bones under `part`, four cubes. `cord_l` (pivot -3.2, 24.3, -3.225,
rotation 0,0,**+40**) and `cord_r` (pivot 3.2, 24.3, -3.225, rotation 0,0,**-40**) each carry one
cube modelled straight down from the pivot: 0.5 wide, y 19.8..24.3, z -3.35..-3.1. `stone` (pivot
0, 20.9, -3.3, unrotated) carries `bail` x -0.375..0.375, y 20.25..21.0, z -3.6..-3.1 and `gem`
x -0.5..0.5, y 19..20.5, z -3.85..-3.1. Envelope (Blockbench) x ±3.39, y 19.0..24.46,
z -3.85..-3.10; reach 4.44, `past chestplate z+0.85`.

**The sign is the opposite of the brief's guess, and the arithmetic says so before the bridge
does.** The brief suggested -35 on the left (negative-x) cord; that swings the free end *outward*.
Rotating about Z by θ sends a point at (0, -L) below the pivot to (L sin θ, -L cos θ), so the
left cord needs a POSITIVE θ to travel toward +x - the same rule wing_cases found from the other
side (negative Z moves the below-pivot end toward -x). I never had to flip anything: the check's
first envelope after placing `cord_l` read bone-local x 0.499..3.39 (Blockbench -3.39..-0.499),
matching the hand computation to a hundredth.

**Why 40 degrees and not 35.** 35 is what puts the cord *ends* at y 20.6, but it leaves the inner
bottom corners at x ∓0.41 - 0.035 short of a 0.75-wide bail, i.e. a visible hairline gap at the
one joint the eye goes to. 40 degrees drops the ends to y 20.69..20.96 and pushes the inner
corners to x ∓0.116, so each cord laps 0.26 onto the bail: the profile's quarter-unit joint
overlap, bought by three degrees. To keep the same quarter unit at the other joint I made the
bail 0.75 tall (y 20.25..21.0) instead of 0.5, so it overlaps the gem's y 20.5 top by 0.25 and
still covers the cord ends; the gem kept the briefed 1x1.5x0.75 at y 19..20.5 exactly.

**The `!` I accepted: none.** The only `!` this part ever raised was the standing unpainted-face
count, cleared by the two paint calls. The clash section stayed at `all clear by more than half a
unit` for every body-bone neighbour - the upper chest at z -3.85..-3.1 is empty except for the
other `collar` parts, which are never compared. Worth noting from the same-socket table for
whoever writes the next collar part: `chain_of_office` occupies Blockbench y 16.80..23.44 at
z -4.60..-2.60 and `bandolier` y 15.66..25.20 at z -3.65..-2.35, so a chest hanger has to live in
front of z -3 and the depth budget out to about -4.6 is already spoken for by two shipped parts.

**Painting: two calls, and they covered everything.** Master: `*.*: 120`, then all 24 faces by
name - cords `[165,115]` on the front (`north`) face, `[135,95]` on the narrow sides, 175 up, 70
down, 80 on the buried `south` face; `bail.*: 200` then its six faces (`[225,185]` front, 95
down); `gem.*: 210` then `[248,195]` front, `[225,170]` sides, 62 underside - plus 7 `pixels`.
The gemstone mask repeats the gem's six faces and its one specular texel and touches nothing else,
so the cord stays the trim material's metal. Saved sheets: master 60 opaque texels spanning
62..255, mask 10, both pure greyscale, nothing outside the silhouette.

**`north` is the front face on the body bone** (the sheet layout tells you which rectangle is
which by size, and on a 0.5x4.5x0.25 cord every long face unwraps to a 1x5 column). That is the
painter's limit here: a 1-texel-wide face means the chain's "lighter top row" is literally one
texel, so the sheen along the cord is the `[top, bottom]` ramp down the column plus one brighter
texel at the top of each of the three visible columns (205 front, 188 sides) placed by `pixels`.
Anything finer - links, a twist - is below the sheet's resolution at this thickness; the cord
reads as a chain because it is thin and turned, not because it is painted like one.

**For the next part.** `armorpieces_set_part` reported `sheets_created: [part_gemstone]` and wrote
the recipe on save (`minecraft:lapis_lazuli in minecraft:paper`); `minecraft:lapis_lazuli` was
already in `.modpage/cache`, so `python -m modpage build --offline` rendered the grid with no
warning and no plain rebuild was needed. Four cubes with sub-unit dimensions cost 60 texels of a
64x32 sheet - a pendant is the cheapest part in the pack. And the 3D view is still blank until the
master has paint: paint, then screenshot; a close camera at (-6, 24, -16) aimed at (0, 21, -3.5)
frames the sternum.
