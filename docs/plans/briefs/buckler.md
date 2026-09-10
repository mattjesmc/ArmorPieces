# Brief: Buckler

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the seventh
batch of four, a Knightly set (read bangles.md first - same socket, the arm frame - and
bedroll.md for the two-cubes-at-45-degrees round profile). From the `vambraces` row of
`docs/plans/part-variety.md`:

> **Buckler** - A small round shield strapped over the forearm - the one part outside `back`
> that could carry a real banner design. Theme: Knightly. Fittings: `banner`, `guard`.

The `banner` fitting maps a shield pattern onto a bone named `banner` with a fixed front face
and is out of scope for this session: give the buckler `guard` only.

**Part.** `armorpieces:buckler`, socket `vambraces` only, in the mod's own pack. Display name
"Buckler". Fittings: `armorpieces:guard`, one mask, covering the central boss; the disc and
straps stay the material. No effects, no loot, no static layer.

**Shape.** `vambraces` is a mirrored socket riding the arm: model ONE arm, the LEFT, at
NEGATIVE x. The arm box is x -8..-4, y 12..24, z -2..2 (pivot -5, 22, 0); the chestplate's arm
shell is that box inflated a full unit, x -9..-3, y 11..25, z -3..3, and the anchor is at
Blockbench (-6, 16, 0). "Outboard" is more negative x. Read the envelopes in the
`armorpieces_new` reply: the pauldrons parts share the bone and `wing_cases`' lower plate
reaches down to y 14.07 at x -10.8..-9.2, `spaulders` to -10.33 - an outer-forearm disc cannot
avoid lapping their hulls (the shipped vambraces reach x -10 too), so lap them and dodge their
planes by a twentieth. Build a `disc` bone pivoted at the disc's centre (-9.35, 15.5, 0)
carrying a plate x -9.6..-9.1 (a tenth off the shell's x -9), y 12.75..18.25 (5.5 tall),
z -2.75..2.75 (5.5 wide); a child bone `disc_turned` at the same pivot rotated 45 degrees about
X holding a plate of the same thickness but 4.4 square (y 13.3..17.7, z -2.2..2.2 before
rotation - its corners then reach 3.11 from the centre, inside the flat plate's 2.75 half-size
plus a corner, so the two make an octagon and no end faces are coplanar); a `boss` cube 1.5
square, 0.6 proud, x -10.2..-9.6, y 14.75..16.25, z -0.75..0.75 (a tenth into the plate, no
shared plane); and two strap plates in a `straps` bone hugging the arm shell's front and back
a tenth off, x -9.1..-3.1, y 15.25..15.75, z -3.35..-3.1 and 3.1..3.35 (their outboard ends a
tenth inside the disc). Nothing above y 18.5, nothing below 12.5.

**Sheets.** Master: disc mid-light `[top, bottom]` with the flat plate a touch lighter than
the turned one so the octagon reads as facets, a bright rim row around the flat plate's outer
face (`pixels`, its top and bottom rows), boss brightest with a dark underside and a specular
texel, straps mid grey. Guard mask: the boss's faces only, shaded like the master.

**Recipe.** Centre item `minecraft:iron_trapdoor` (a flat item, unused by any template), paper
ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
buckler` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.
Built 2026-09-03 in 16 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`list_outline`, 4 `add_group`, 4 `place_cube`, 2 `remove_element` (starter cube, then its bone),
1 `armorpieces_check`, 1 `armorpieces_set_part`, **2 `armorpieces_paint`**, 2 `set_camera_angle`,
1 `armorpieces_save`. No `risky_eval`, no `modify_cube`, nothing nudged, nothing hand-edited; the
save went through first time without `force` and the check ended `ok: nothing needs a decision`.

**What I built.** Four bones under `part`: `disc` (pivot -9.35, 15.5, 0) with `plate`
x -9.6..-9.1, y 12.75..18.25, z **-2.70..2.70**; its child `disc_turned` (same pivot, rotation 45
about X) with `plate_turned` x **-9.55..-9.15**, y **13.4..17.6**, z **+-2.1**; `boss` (pivot
-9.85, 15.5, 0) with `boss_stud` x -10.2..**-9.5**, y 14.75..16.25, z +-0.75; `straps` (pivot -6,
15.5, 0) with `strap_front` and `strap_back`, both x **-9.2**..-3.1, y 15.25..15.75, z
-3.35..-3.1 and 3.1..3.35. Envelope x -10.20..-3.10, y 12.53..18.47, z +-3.35; reach 5.55 from
the anchor; past the chestplate x+1.20, y-1.53, z+0.35.

**Four numbers in the brief had to move, all of them to dodge a coplanar face** - and none of
them by more than a twentieth, so the shape is the brief's:
- The flat plate's z **2.75 -> 2.70**. `wing_cases`' `case_lower` is z +-2.75 exactly and its
  hull overlaps the disc, so the brief's 5.5-wide plate would have shared two planes with it.
- The turned plate 4.4 square **-> 4.2** (half-side 2.1). At 4.4 the corners reach 2.2*sqrt2 =
  3.111, which breaks the brief's own "nothing above y 18.5, nothing below 12.5" (18.61 / 12.39)
  and would have pushed z to 3.111, past the chestplate's z 3 by 0.11. At 4.2 the corners reach
  2.970: still 0.22 proud of the flat plate's edges (an octagon), inside y 12.53..18.47, and the
  check's `past chestplate z` came out **-0.03** - i.e. it just barely does not break the arm
  shell, which is what the brief wanted.
- The turned plate's thickness x -9.55..-9.15 rather than the flat plate's -9.6..-9.1: two cubes
  of the *same* thickness on the same axis share both x planes over the whole octagon overlap
  (the bedroll lesson). 0.05 recessed on each side is invisible and coplanar-free.
- The boss's inboard face x -9.6 **-> -9.5** and the straps' outboard end x -9.1 **-> -9.2**: the
  brief's numbers put them exactly on the disc plate's own faces. "A tenth into the plate" and "a
  tenth inside the disc" have to be read as *crossing* the face, not meeting it.

**Every `!` I accepted: none.** The only `!` that ever stood was the 30-face unpainted count,
cleared by the two paint calls. Five `-` notes survive and are all the same fact the brief
predicted: the disc, the turned plate and the boss overlap `wing_cases:pauldrons`' `case_lower`
hull (by 0.42, 0.37 and 0.70 in x), because an outer-forearm disc at x -9.6 cannot avoid a
pauldron that comes down to y 14.07 at x -11.02..-7.05. The planes are all dodged - `near:
disc_turned clears case_lower by 0.05 in x` is the tightest, and it is a clearance, not a
contact - so nothing z-fights; the two shapes simply interpenetrate as a shield strapped under a
pauldron would. The other notes are `disc_turned clears mantle's skirt by 0.31 in y` and `pair
spans 20.40 across the figure` (the shipped `vambraces` spans 20.0; a disc on each forearm cannot
do better).

**Painting: two calls, one per sheet, and they covered everything** - 30 master faces (86 face
paints, since the object walks general-to-specific) plus 13 texels, and 6 faces plus 1 texel on
`part_guard`; zero unpainted, no stray paint, no colour on a greyscale sheet. Pillow on the saved
sheets: master 242 opaque texels spanning 54..255, mask 16 texels 54..255, both grey. The master
call is `"*.*": 110`, then each cube's `<cube>.*` base and its faces: flat plate 150 with `west`
(the outboard disc face) `[195, 120]`, `up` 200, `down` 60, `north`/`south` `[175, 110]`, `east`
72 (buried against the arm shell); turned plate one step darker throughout (132 base, west
`[168, 104]`, up 182) so the octagon reads as two facets rather than one smooth disc; boss 210
with west `[248, 190]`, up 235 and `down` 54. `pixels` did the two things a `[top, bottom]` pair
cannot: the bright rim rows across the top and bottom of the flat plate's 6x6 west face (228 at
y 6, 208 at y 11 - the lower one dimmer so the rim itself shades) and the specular at 41,2.

What the painter did **not** cover: the straps. At 0.5 units tall **every strap face is one texel
tall** (the bangles lesson again), so a ramp on them is a single flat row - they are 120 with a
155 top row and 56 underside and that is all the modelling they can carry. The boss is 1.5 units,
so its west face is 2x2: "a specular texel" is a quarter of the face, and the dark underside is a
1x2 strip. And nothing paints the *rim* of the octagon as a ring - the flat plate's rim rows sit
on its west face only, so the bright edge reads from straight outboard and vanishes at a glancing
angle. Sub-unit detail stays a modelling decision in this format.

**For the next part.**
- Two cubes at 45 degrees is still the cheap round profile, but on a *disc* (unlike the bedroll's
  roll) the turned cube's corners grow the envelope on **both** free axes at once, so size it
  from the half-diagonal against whichever limit is tighter. Half-side 2.1 inside a 2.75 flat
  half-size is the sweet spot: 0.22 of corner proud, 0.03 of chestplate clearance left.
- `wing_cases` is the pauldron that reaches into vambraces territory (y 14.07 down to x -11.02,
  z +-2.75). Anything on the outer forearm above y 14 laps it; keep off its z +-2.75 and x -11.02
  planes and the check will only ever say OVERLAP, which is a note.
- `minecraft:iron_trapdoor` is free and flat: `--offline` warned it had never been cached, one
  plain `python -m modpage build` fetched it, and the next offline build was silent, all three
  pages `unchanged`.
- The 3D view stays blank until the master has paint; one shot from outboard-front (-34, 17, 16)
  and one straight outboard (-40, 15.5, 3) were enough to confirm the octagon silhouette and that
  the boss reads as a bump, not a hole.
