# Brief: Pouch Belt

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the fourth
batch of four, a Wayfarer set (skim the lessons in girdle.md - the waist frame, the plate ring,
why 45-degree corners fail over a box - and carapace.md for the belt-line neighbours). From
the `belt` row of `docs/plans/part-variety.md`:

> **Pouch Belt** - Two or three pouches and a coil of rope at the hips. Theme: Wayfarer.
> Fitting: `inlay`.

**Part.** `armorpieces:pouch_belt`, socket `belt` only, in the mod's own pack. Display name
"Pouch Belt". Fittings: `armorpieces:inlay`, one mask, covering the strap and the pouches (the
leather takes the dye); the rope coil and the pouch buckles stay the material. No effects, no
loot, no static layer.

**Shape.** `belt` is not a mirrored socket: model the whole thing, centred on x = 0, on the body
bone. The torso box is x -4..4, y 12..24, z -2..2 (pivot 0, 24, 0); the leggings shell is that
box inflated 0.5 and the chestplate's a full unit (x -5..5, y 11..25, z -3..3), so every strap
face must lie past x ±5 or z ±3; the anchor is at Blockbench (0, 12, 0). Read the envelopes in
the `armorpieces_new` reply: the other belt parts are never compared but give the gauge
(buckled_belt's strap sits at x ±5.5, z -4.5..3.5, y 12.5..15.5; girdle at y 11.75..14.25), and
the back and collar parts that share the bone are what the clash lines measure (carapace's
lowest lame is y 15.6..16.7 at z 3.1..4.05, wing_roots starts at y 14.5). Build: a `strap` bone
with four plates a quarter unit thick and one unit tall at y 12.6..13.6, exactly the girdle's
cardinal layout (front z -3.35..-3.1, back z 3.1..3.35, flanks x ±5.1..±5.35, each running the
full width so the corners double up by a quarter unit) - no corner tabs, a plain strap shows
its corners. Three hangers, each its own bone, each hanging from the strap and standing proud of
it: `pouch_left`, a box x -6.6..-5.4, y 11.0..13.4, z -1.6..0.6 with a flap cube 0.25 proud on
its outer face across the top third (x -6.85..-6.6, y 12.5..13.6, z -1.7..0.7) and a 0.5 buckle
stud on the flap; `pouch_back`, a smaller box on the right rear at x 2.4..4.6, y 11.2..13.4,
z 3.4..4.5 with its own flap; and `coil`, a rope coil on the right hip - a 1.6x1.6x0.9 block at
x 5.4..6.3, y 11.6..13.2, z -0.9..0.7 with a 0.5-square knot cube on its face - which reads as
rope by paint (a bright-dark-bright banding in `pixels`). Nothing above y 13.7 (the strap's
top) and nothing below y 11.0.

**Sheets.** Master: strap mid grey `[top, bottom]` with a lighter top row; pouches a step
darker with a lighter flap and a bright buckle stud; coil banded light/dark across its width
with the knot brightest. Inlay mask: the strap's and pouches' faces (flaps included), null on
the studs and the coil, the same gradients.

**Recipe.** Centre item `minecraft:map` (the empty map, a flat item, unused by any template),
paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
pouch_belt` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-03 in 26 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`armorpieces_part`, 1 `list_outline`, 2 `remove_element` (starter cube, then its bone), 4
`add_group`, 4 `place_cube`, 7 `modify_cube`, 1 `find_elements_by_criteria`,
1 `armorpieces_set_part`, **4 `armorpieces_paint`**, 2 `armorpieces_check`, 4 `set_camera_angle`,
1 `armorpieces_save`. No `risky_eval`, nothing hand-edited, the save went through first time
without `force`, and both checks were clean on the first run afterwards.

**What I built.** Four bones, twelve cubes, no rotations anywhere. `strap`: the briefed cardinal
ring exactly - `plate_front` x -5.35..5.35 z -3.35..-3.1, `plate_back` the mirror at z 3.1..3.35,
`plate_right` x 5.1..5.35 and `plate_left` x -5.35..-5.1 both running z -3.35..3.35, all
y 12.6..13.6, corners doubling up by the quarter unit. `pouch_left`: `bag_l` 1.3 x 2.3 x 2.2,
`flap_l` 0.35 thick standing proud on the outer face, `stud_l` 0.5 square on the flap.
`pouch_back`: the same three cubes at x 2.4..4.6, z 3.3..4.75. `coil`: `rope` 1.0 x 2.4 x 1.6
with a 0.5 `knot` on its outer face. Envelope x -6.55..7.10, y 11.05..13.6 (Blockbench),
z -3.40..5.00; reach 7.93.

**The one thing the check cannot see, and the reason for the two deviations I made: the arms.**
The reference player's arms are cubes x ±4..±8, y 12..24, z -2..2, and they are on the *arm*
bones, so `armorpieces_check` never mentions them - it only compares parts that share the body
bone. Both of the brief's hip hangers were specified at z -1.6..0.6 and z -0.9..0.7, i.e. dead
centre of the arm's z span and outboard of x 4, so the first screenshot showed them completely
swallowed: nothing but a dark 0.9-unit stub below y 12 where they hang out under the arm. A thin
strap can live inside the arms (girdle's flanks at x ±5.5 do, and so does buckled_belt) because
it also crosses the front and back where it is visible; a hanger that exists *only* at the flank
is simply invisible when worn. So I slid `pouch_left` and `coil` forward onto the front hip
corners, keeping every dimension the brief gave and every other coordinate: `bag_l` z -3.3..-1.1,
`flap_l` z -3.4..-1.0, `stud_l` z -2.45..-1.95, `rope` z -3.3..-1.7, `knot` z -2.75..-2.25. Their
front faces now land *inside* the front plate's own slab (-3.35..-3.1), so they still hang off
the strap with no gap and no shared plane, and 1.3 units of each stands clear in front of the
arm. The finished part reads from the front as a pouch on one hip and a rope coil on the other,
with the third pouch on the right rear where the arm never was a problem. **Take the arm box into
your own arithmetic on any `belt`, `tassets` or `pauldrons` part: `|x| > 4` and `-2 < z < 2` and
`y > 12` is inside the player's arm, and no line of the check will tell you.**

The second deviation: the brief's coil was 1.6 tall, which is **two** texels on a 64x32 sheet, and
a bright-dark-bright banding needs three. Sheet resolution is exactly one texel per unit, so any
paint idea has to be checked against the face rectangle first - the check prints it (`east 0,10
2x3`). I grew the coil to 2.4 tall (y 11.05..13.45, inside the brief's "nothing above 13.7,
nothing below 11.0") to buy the third row, which also made it match the pouches in bulk. Same
trap in the other direction: the strap plates are 1 unit tall, so their outward faces are a
*single* texel row and the brief's "mid grey `[top, bottom]` with a lighter top row" is not
expressible - a `[top, bottom]` pair on a 1-row face is just the top value. The strap's lit edge
is its `up` face at 200 instead.

**The `!`s I accepted: none.** The save needed no `force`. The only `!` that ever stood was the
running "N faces have no paint behind them", cleared by the paint calls. Three `-` notes about
planes I removed instead of accepting, all before painting and all one `modify_cube` each:
`pouch_left's y face at 13 lies on the chestplate surface` (bag bottom on the shell's y = 11
plane -> 11.1) and `coil's y face at 12 lies on the body surface` (twice, the knot's bottom on the
torso's y = 12 plane -> 12.05). The six notes that remain are all gaps between `pouch_back` and
parts on other sockets that ride the same bone and so never move relative to it: `clears
quiver:back's sling by 0.02 in y` (and 0.17), `clears pinions:back's tip_r by 0.17 / 0.32 / 0.47
in y`, `clears banner:back's banner by 0.25 in z`. 0.02 is a hair, but it is a hair of *air* - no
plane is shared, so there is nothing to z-fight - and the check names only the distance, not the
face, so nudging blind was as likely to land on zero as to help.

**Painting: four calls, and what they covered.** Two on the master and two on the mask, because I
repainted the pouches and coil after the first screenshot: at `[126, 74]` the leather bottoms came
out nearly black on the preview ramp, which is steep below ~120, so the second pass lifted the
bags to `[140, 96]` with the lit outer face `[172, 116]` and the flaps to `[180, 124]` / `[200,
138]`. Worth knowing before your first call: **on the preview material grey 150 reads as a light
band and grey 75 reads as black**, so keep a leather-and-cloth part in 96..210 and save the values
under 70 for buried faces. The first master call was `"*.*": 110` then all 72 faces by name; the
second re-stated the 8 pouch/coil cubes. Both master calls carried the same 18 `pixels` - the rope
banding, three rows per visible face (east 212/124/198, north 198/116/184, south 172/100/160,
west dark) - because a `*.*`-style base repaints the face underneath and wipes any pixels laid
before it: **always re-send your `pixels` in the same call as the base that covers them.** The
inlay mask is the master's values on the strap, bags and flaps only; the studs and the whole coil
were simply left out of the `faces` map, which is cheaper than `null` and leaves them clear.
Pillow confirms master 320 opaque texels spanning 46..252, mask 280 spanning 52..210, zero colour
on either and zero mask texels outside the master's silhouette. What the painter did **not**
cover: the strap has no painted buckle, no stitch line and no seam where the four plates double up
at the corners - all of that would be hand-placed texels on 1-row faces, invisible at three
metres; and the pouch flaps read as flaps only because they are real 0.25-proud geometry.

**For the next part.**
- Twelve cubes with nothing wider than 10.7 fit a 64x32 sheet with half of it empty (320 texels).
- `armorpieces_set_part` wrote the data, the mask sheet and the recipe in one go, and the save
  installed both PNGs; `minecraft:map` is a flat item, `--offline` warned it was uncached, one
  plain `python -m modpage build` fetched the icon and reported all three pages `unchanged`, the
  same sequence girdle, carapace and wing_cases hit.
- A hanger that overlaps the plate it hangs from by 0.05..0.1 (inner face *inside* the plate's
  slab, never on one of its planes) is better than the brief's flush 0.05 standoff: no hairline
  gap, no coplanar `!`. I moved all three hangers' inner faces in by 0.1 for this.
- `find_elements_by_criteria` on the `reference` groups returns names only, no coordinates, so
  there is no way to read the arm box out of the bridge - use the vanilla numbers above.
