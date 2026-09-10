# Brief: Wing Cases

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, with the tooling
as the Antennae and Horsetail sessions had it. From the `pauldrons` row of
`docs/plans/part-variety.md`:

> **Wing Cases** - Hard elytra-style shells folded along the upper arm. Theme: Carapace.
> Fitting: `inlay`.

**Part.** `armorpieces:wing_cases`, socket `pauldrons` only, in the mod's own pack. Display name
"Wing Cases". Fittings: `armorpieces:inlay`, one mask, covering the whole shell - the dye is the
beetle's colour. No effects, no loot, no static layer.

**Shape.** `pauldrons` is a mirrored socket riding the arm: model ONE arm, the left, and the game
mirrors it. In this rig the left arm is on the NEGATIVE x side in Blockbench: the arm box is
x -8..-4, y 12..24, z -2..2, pivoting at the shoulder (-5, 22, 0), and the anchor is at
Blockbench (-6, 22, 0). The chestplate's arm shell (`left_arm_chestplate`) is that box inflated
a full unit, so x -9..-3, y 11..25, z -3..3, and anything inside it is buried; "outboard" is
more negative x. Sit faces a tenth off a shell plane, never on it. Read the envelopes of
spaulders, mantle and beast_head in the `armorpieces_new` reply before placing (the reply
prints the OPEN piece's own envelope bone-local, +Y down and x mirrored; the `past chestplate`
numbers are the honest gauge). A wing case is a hard shell lying along the OUTSIDE of the upper
arm, long and narrow like a folded elytron: build it as two overlapping plates, each its own
bone. The upper plate sits over the shoulder cap - outboard of x -9.1, from about y 19 up to
y 25.5, spanning most of the arm's depth (z about -2.75..2.75), a quarter to half a unit thick,
its top edge curving inward over the shoulder (a second, smaller cube on the same bone stepping
in over the top at y 25.1..25.85, x -9..-6, or the bone rotated a few degrees about Z so the
plate leans in at the top). The lower plate hangs from under the upper one, narrower in z, from
about y 14 up to y 19.5, its bone rotated 8 to 12 degrees about Z so it flares away from the arm
at the bottom, the way a wing case parts from the body. A one-texel ridge cube along the plate's
outer face, running the full height, gives the seam where the two cases would meet. Keep
everything outboard of the head's sweep: nothing above y 25.5 inboard of x -7.

**Sheets.** Master: the plates mid-dark `[top, bottom]` shaded lighter toward the shoulder, with
a bright single-texel row along the ridge as the gloss line and a darker row along each plate's
lower edge. Inlay mask: every plate and ridge face, the same gradient so the dye keeps the shading.

**Recipe.** Centre item `minecraft:shulker_shell` (a flat item, unused by any template), paper
ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
wing_cases` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-03 in 15 bridge calls: 1 `armorpieces_new`, 2 `add_group`, 2 `place_cube`,
2 `remove_element` (starter cube, then its bone), 1 `armorpieces_set_part`, 1 `armorpieces_check`,
2 `armorpieces_paint`, 1 `set_camera_angle`, 1 `armorpieces_save`, plus the two repo checks and
the page build. No `risky_eval`, no `modify_cube`, no nudging, no hand-edited file, and the save
went through first time without `force`.

**What I built.** Two bones under `part`. `case_upper` (pivot -9.45, 22, 0, unrotated) carries
`plate_upper` x -9.7..-9.2, y 19..25.5, z -2.75..2.75 - the shoulder shell, 0.5 thick, sitting
0.2 outboard of the chestplate arm shell's x -9 plane; `cap`, x -9.7..-7.05, y 25.1..25.85,
z -2.5..2.5, the step inward over the shoulder (the brief's alternative to leaning the bone, and
the easier one to keep legal: it stops at x -7.05, honouring "nothing above y 25.5 inboard of
x -7", and its underside floats 0.1 over the shell's y 25 top); and `ridge_upper`, x -9.95..-9.6,
y 19.2..25.4, z -0.5..0.5, the one-texel seam. `case_lower` (pivot -9.45, 19.4, 0, rotation
0,0,-12) carries `plate_lower` x -9.7..-9.2, y 14..19.5, z -2..2 and `ridge_lower` x -9.95..-9.6,
y 14.2..19.4, z -0.5..0.5, both modelled upright in the unrotated pose. **Sign:** a NEGATIVE Z
rotation swings the part below the pivot toward -x, i.e. outboard on this (left, negative-x) arm;
+Z would have folded it into the ribs. The hand arithmetic (pivot + (dx cos - dy sin, dx sin +
dy cos)) put the flared bottom at x -10.82..-10.33, y 14.07..14.17 and the top inner corner at
x -9.185 - still 0.185 clear of the shell - and the check's envelope (Blockbench x -10.83..-9.18,
after subtracting the anchor) matched to a hundredth, so nothing needed moving. Joint overlap:
the lower plate's top (y ~19.5 after rotation) runs 0.5 into the upper plate's bottom (y 19).

**The `!` I accepted: none.** The save was clean. What the check did report, all as `-` notes, is
nine `OVERLAP` lines and ten `near:` lines between `case_lower` and the vambraces-socket parts
(claws, vambraces, wraps). They are hull tests on the bone's AABB, and a rotated bone's AABB is
much bigger than its plates: the real interpenetration is the plate's inner edge sinking 0.3-0.5
units into the vambrace shell in a narrow band around y 16..18, and nothing at all below y 15
(the flare carries the plate out to x -10.4 while the vambraces stop at -10.0). Different sockets
nesting a third of a unit is invisible at three metres, and no plane is shared - every face of
`case_lower` is rotated 12 degrees, so it cannot be coplanar with an axis-aligned bracer, which is
what would have been a `!`. If a future pauldron part wants to be clean here, the honest fix is to
keep the lower plate above y 18 or push it 0.3 further outboard; the shape the brief asked for
cannot avoid the notes.

**Painting: two calls, one per sheet, and they covered everything** - 30 master faces and the same
30 on `part_inlay`, zero unpainted, no stray paint, no colour on a greyscale sheet. The master went
in as `*.*: 110`, then every face by name: plates `[175,120]` / `[150,95]` on the outboard `west`
face (upper lighter than lower, "lighter toward the shoulder"), `[90,60]` and `[80,55]` on the
buried inboard `east` faces, the ridges `[250,195]` and `[235,180]` as the gloss line, dark
`down` faces at 58-70. `cap.*: 190` before the specific cap faces is the cheap way to cover a
cube's leftovers. **`west` is the outboard face on this rig** (`east` = +x = into the arm) - the
sheet layout line tells you which is which by size before you paint.

What the painter did NOT cover: the "single-texel row" work. A face gradient runs top-to-bottom
over the whole face, so the bright ridge row and the dark row along each plate's lower edge went
in as the `pixels` list of the same call (22 texels: the top and bottom rows of both `west`
rectangles, plus one 255 texel at the tip of each ridge). Read the row coordinates straight off
the check's `sheet layout` block - `west 19,6 6x7` means x 19..24, y 6..12, and the last row is
the bottom of the cube in the model.

**For the next part.**
- `armorpieces_set_part` before painting is still the ordering constraint: it reported
  `sheets_created: [part_inlay]` and the mask call worked immediately after.
- A 0.35-unit-thick ridge and a 0.5-unit plate both unwrap to 1 texel, so the ridge reads only
  because it stands 0.25 proud of the plate and carries a brighter grey - thickness under a unit
  is a silhouette decision, not a sheet one.
- `minecraft:shulker_shell` is a flat item and was free; `python -m modpage build --offline`
  warned it had never been cached, one plain `python -m modpage build` fetched it and the README
  came back `unchanged` (only the icon PNG differed), exactly as the antennae session found.
- The 3D view is still blank until the master has paint, so paint, then screenshot: one
  `set_camera_angle` from behind-left at (-34, 30, 26) showed the whole thing.
