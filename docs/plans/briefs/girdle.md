# Brief: Girdle

The fifth part authored through the bridge (`tools/mcp`), by one `part-author` session on Opus,
with the tooling as the Antennae and Horsetail sessions had it. From the `belt` row of
`docs/plans/part-variety.md`:

> **Girdle** - Overlapping metal plates ringing the waist. Theme: Knightly. Fittings: `guard`,
> `gemstone`.

**Part.** `armorpieces:girdle`, socket `belt` only, in the mod's own pack. Display name "Girdle".
Fittings, in this order: `armorpieces:guard` (one mask, every plate) and `armorpieces:gemstone`
(one mask, a single stone set in the front plate only). No effects, no loot, no static layer.

**Shape.** `belt` is not a mirrored socket and sits on the body bone at the waist: Blockbench
y 12 is the bottom of the torso, the torso box is x -4..4, z -2..2. Two armour shells cover it,
the leggings' at half a unit out and the chestplate's at a full unit, so every plate must lie
past x ±5 and z ±3 or it is buried; the reply to `armorpieces_new` gives the envelopes of the
shipped belt parts (sash, buckled_belt) as the gauge for where a waist part actually sits. Ring
the waist with a course of thin plates, each its own bone so it can tilt: a plate on the front,
one on the back, one on each flank, and four corner plates each rotated 45 degrees about Y to
close the ring - eight plates, every plate a quarter-unit thick, about two to two and a half
units tall, overlapping its neighbours by a quarter unit so no daylight shows at the corners.
Stagger them so the ring reads as overlapping lames, not a smooth band: alternate plates a
quarter unit further out, or a quarter unit lower. The front plate carries a small stone, a
1x1 cube half a texel proud of the plate, centred. Keep the whole thing between Blockbench
y 11 and 14.5 so it does not climb the chestplate or drop onto the tassets' line.

**Sheets.** Master: plates mid-grey `[top, bottom]` shaded lighter at the top edge, a bright
single-texel row along each plate's top as the rolled rim, corner plates a step darker than the
faces they sit between; the stone bright with a dark underside. Guard mask: every plate face,
flat grey. Gemstone mask: the stone's faces only.

**Recipe.** Centre item `minecraft:iron_horse_armor` (a flat item, unused by any template),
paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py girdle`
and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons paragraph below
filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-03 in 33 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 2
`remove_element` (starter cube, then its bone), 8 `add_group`, 8 `place_cube`, 4 `modify_cube`,
1 `armorpieces_set_part`, **3 `armorpieces_paint`**, 1 `armorpieces_check`, 3 `set_camera_angle`,
1 `armorpieces_save`. No `risky_eval`, nothing hand-edited, and the save went through first time
without `force`.

**What I built.** Eight plates, one bone each, all 0.25 thick. Four cardinals at Blockbench
y 11.9..14.25: `plate_front` x -5.25..5.25 z -3.5..-3.25, `plate_back` the mirror at z 3.25..3.5,
`plate_right` x 5.25..5.5 and `plate_left` x -5.5..-5.25, both z -3.25..3.25. Four corner tabs
1.5 long, y 11.75..14.0 (a quarter unit lower - the stagger), each modelled as a plate lying
along X centred on the corner point (+-5.24, +-3.24) and turned by its bone: `corner_fr` -45,
`corner_fl` +45, `corner_br` +45, `corner_bl` -45 degrees of Y. `stone`, 1x1x0.7 at
z -4.0..-3.3, sits in the `front` bone, half a unit proud of the front plate. Envelope
x +-5.86, y 11.75..14.25, z -4.0..3.86; reach 6.87, just past buckled_belt's 6.60.

**The geometry lesson: a 45-degree chamfer over a box body is a small tab, not a long facet.**
The body is a box and both armour shells are boxes, so a plate is only outside the chestplate
if `|x| > 5` OR `|z| > 3` - a diagonal segment cutting the corner sinks straight into the shell
in the middle of its run. The arithmetic that decides it, for the front-right corner: write the
tab's mid-plane as `x - z = D` (so `D = x_c - z_c` for the tab's centre); its inner face is at
`D - 0.177`, and the shell corner (5, -3) is at `x - z = 8`. So `D >= 8.177` or the tab is
buried. My `D = 8.48` clears the shell corner by 0.21. That also fixes the tab's length: at that
distance the chord between the two cardinal plates' surfaces is only ~0.7 units, so 1.5 (0.25 of
overlap onto each neighbour, wedge-shaped in plan) is as long as a 45-degree corner plate can be
before it stands off the ring like a fin. The brief's "eight plates, corners at 45 degrees" is
therefore four long cardinals and four small corner caps, not a regular octagon: an octagon with
equal sides would need the front plate 7 wide and the flanks 3, and its diagonals would be buried
by more than a unit.

**Other numbers the bridge handed me.** The `armorpieces_new` reply's envelope table gave the
waist gauge without opening anything: buckled_belt is x +-5.50 z -4.50..3.50 at Blockbench
y 12.5..15.5, i.e. the shipped belt sits 0.5 past the chestplate shell with its inner face buried,
so 3.25/5.25 inner and 3.5/5.5 outer is the right radius pair. `past leggings x+1.36` in the
compact line confirmed the corner tabs landed at x 5.86 exactly as computed - bone rotations are
worth doing on paper first, the check matches to a hundredth. The back-parts table is what keeps
the top edge honest: `wing_roots` starts at Blockbench y 14.5, so a plate topping out at 14.5
would share its plane; 14.25 leaves the note `back clears wing_roots:back's plate by 0.25 in y`.

**The four `!`-free notes I accepted.** All four are `-` notes and none needed `force`:
`back clears wing_roots:back's plate by 0.25 in y`, `corner_bl clears pinions:back's tip_l by
0.35 in z`, `back clears quiver:back's sling by 0.45 in z`, `corner_br clears pinions:back's
tip_r by 0.49 in z`. Every one is a gap, not an overlap, between parts that both ride the body
bone and so never move relative to each other. The only `!` I ever had was the standing
"unpainted faces" count, cleared by painting.

**One thing I moved rather than accepted.** With the cardinals at y 12.0 the check printed four
notes of the form `front's y face at 12 lies on the body surface` - the torso's bottom plane.
They are notes, not problems, and the plates are outside the torso box in x/z so nothing would
actually z-fight, but four `modify_cube` calls dropping the bottoms to y 11.9 removed all four
and cost nothing (paint had not been laid yet - after painting, a resize moves paint without
growing it, as the spire session found).

**Painting: three calls, one per sheet, and they covered everything.** The master call carried a
`*.*` base of 120, then all 54 faces by name - cardinals `[175, 105]` on the outer face, 200 up,
68 down, `[148, 92]` end caps, 58 on the buried inner face; corner tabs one step darker
(`[148, 86]`, 172 up); stone `[245, 200]` with a 66 underside - plus 44 `pixels` for the rolled
rim, a single bright row (232 on cardinals, 198 on tabs) along the top row of each outer face's
rectangle. The rim is the one thing `faces` alone cannot do: `[top, bottom]` ramps smoothly over
the three rows, and a rim wants a step, so read the outer face's `x,y w x h` out of the sheet
layout and list its top row as pixels. The guard mask was the whole part in one line -
`{"*.*": 150, "stone.*": null}` - `null` clears, so "everything except the stone" is two entries;
the gemstone mask was the stone's six faces. Zero unpainted faces after, no stray paint, no
colour on a greyscale sheet, and Pillow confirms master 406 texels spanning 50..245, guard 400
flat at 150, gemstone 6, none outside the master's silhouette. What the painter still does not do
is anything defined relative to a neighbour: the plates read as one smooth band from the front
because a painted seam between lames would have to be a column of texels placed by hand.

**For the next part.** `armorpieces_set_part` now creates the mask sheets *and* writes the recipe
on save (`sheets_created: [part_guard, part_gemstone]`, `recipe: minecraft:iron_horse_armor in
minecraft:paper`), and the first save installed all three sheets from `tools/decoration_masters/`
- the three separate workarounds the nasal session needed are all gone. `minecraft:iron_horse_armor`
is a flat item; `python -m modpage build --offline` warned it had never cached it, one plain
`python -m modpage build` fixed the icon and left the pages otherwise unchanged. Nine cubes,
including two 10.5x2.35 plates, fit a 64x32 sheet with room to spare (406 opaque texels). And
when a socket is not mirrored, remember you are modelling both sides: eight bones, eight cubes,
no mirroring for free.
