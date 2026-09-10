# Brief: Cuffs

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the eighth
batch of four (read bangles.md and buckler.md first - same socket, the arm frame, rings of
plates, the pauldron parts that reach down the arm). From the `vambraces` row of
`docs/plans/part-variety.md`:

> **Cuffs** - Wide flared bracers, bell-mouthed at the elbow. Theme: Court. Fitting: `inlay`.

**Part.** `armorpieces:cuffs`, socket `vambraces` only, in the mod's own pack. Display name
"Cuffs". Fittings: `armorpieces:inlay`, one mask, covering the cuff's cloth; the trim band at
the bell's mouth stays the material. No effects, no loot, no static layer.

**Shape.** `vambraces` is a mirrored socket riding the arm: model ONE arm, the LEFT, at
NEGATIVE x. The arm box is x -8..-4, y 12..24, z -2..2 (pivot -5, 22, 0); the chestplate's arm
shell is that box inflated a full unit, x -9..-3, y 11..25, z -3..3, and the anchor is at
Blockbench (-6, 16, 0). "Outboard" is more negative x. Read the envelopes in the
`armorpieces_new` reply: the pauldrons parts share the bone and reach down to y 14.07
(wing_cases, at x -10.8..-9.2) - a bell that flares above y 14 laps their hulls, which the
shipped vambraces do too; dodge the listed planes by a twentieth. Build two rings of four plates
each, 0.35 thick. The lower ring, `cuff_low`, unrotated, hugs the shell a tenth off at
y 12.6..14.6 (outer x -9.45..-9.1, inner x -2.9..-2.55, front z -3.45..-3.1, back z 3.1..3.45,
each plate the full span so the corners double up). The upper ring is the bell: four separate
bones `bell_out` / `bell_in` / `bell_front` / `bell_back`, each pivoted on the lower ring's top
edge at the middle of its side (outer at (-9.275, 14.6, 0), inner at (-2.725, 14.6, 0), front at
(-6, 14.6, -3.275), back at (-6, 14.6, 3.275)) and carrying a plate the same thickness rising
2.4 to y 17.0 in the unrotated pose, each bone rotated 14 degrees about the axis that runs along
its plate so the top leans OUTWARD from the arm (outer plate: positive Z tips an upright's top
toward -x on this side, ears confirmed; inner plate: negative Z; front plate: negative X tips
the top toward -Z; back plate: positive X - confirm each on its reply). The bell plates' bottoms
lap the lower ring's top by a tenth (start at y 14.5). A trim band 0.2 proud along the top edge
of each bell plate, 0.4 tall, in the same bone, is the mouth's braid. Nothing above y 17.5, and
in the rotated pose nothing further out than x -10.1.

**Sheets.** Master: lower ring mid grey `[top, bottom]`; bell plates lighter toward the mouth
`[top, bottom]` with the outer plate brightest; trim bands bright with a dark underside. Inlay
mask: the eight cloth plates at the same values, the trim bands left out.

**Recipe.** Centre item `minecraft:golden_chestplate` (a flat item, unused by any template),
paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py cuffs`
and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons paragraph below
filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-03 in 22 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`list_outline`, 5 `add_group`, 5 `place_cube`, 2 `remove_element` (starter cube, then its bone),
1 `armorpieces_check`, 1 `armorpieces_set_part`, **2 `armorpieces_paint`**, 2 `set_camera_angle`,
1 `armorpieces_save`. No `risky_eval`, no `modify_cube`, nothing nudged, nothing hand-edited; the
save went through first time without `force` and the check ended `ok: nothing needs a decision`.

**What I built.** Five bones under `part`, 12 cubes. `cuff_low` (pivot -6, 14.6, 0, unrotated)
is the brief's lower ring, exactly its numbers: `low_out` x -9.45..-9.10, `low_in` x -2.90..-2.55
(both z +-3.45), `low_front` z -3.45..-3.10, `low_back` z 3.10..3.45 (both x -9.45..-2.55), all
y 12.6..14.6, so every plate runs the full span and the four corners double up by 0.35. The bell
is four bones, each pivoted on the lower ring's top edge at the middle of its side and each
carrying a plate y 14.5..17.0 (0.1 of lap onto the ring) plus a trim band: `bell_out` (-9.275,
14.6, 0) rotation **Z +14**, `bell_in` (-2.725, 14.6, 0) **Z -14**, `bell_front` (-6, 14.6,
-3.275) **X -14**, `bell_back` (-6, 14.6, 3.275) **X +14**. Every sign in the brief was right
first time and each reply confirmed it: `bell_out` took `past chestplate x` from +0.45 to +1.07
(outward), `bell_front` took `past chestplate z` to +1.07 (forward). Envelope, Blockbench frame:
x -10.07..-1.93, y 12.60..16.97, z +-4.07; reach 5.95.

**The one number I changed, and the arithmetic that forced it.** The brief asks for a trim band
"0.2 proud along the top edge" AND "in the rotated pose nothing further out than x -10.1"; those
two cannot both hold. The bell plate alone already reaches x -10.02 at its top-outboard corner
(local (-0.175, 2.4) through a 14 deg Z rotation), and at the band's height the plate's own face
is at -10.00, so **every 0.1 of proudness costs cos 14 = 0.097 in x**: a 0.2-proud band at the
mouth lands at -10.20, a tenth past the guard. I kept the guard and moved the band: **0.15 proud
(0.2 thick, 0.05 of it biting into the plate so no face is coplanar) and seated at y 16.2..16.6
instead of at the lip**, which puts the outermost texel at -10.07. It reads better than the
compromise sounds - the mouth now has a plain 0.4 lip above the braid, which is what a real
bell-mouthed cuff has. If a future brief wants the braid *at* the lip, either drop the tilt to
about 10 deg or let the guard go to -10.25 (the shipped `vambraces` is at -10.00, `buckler` at
-10.20).

**Every `!` I accepted: none.** The only `!` that ever stood was the 72-face unpainted count,
cleared by the two paint calls. Seven `-` notes survive, all predicted by the brief: five
`OVERLAP ... wing_cases:pauldrons's case_lower` (its lower plate comes down to y 14.07 at
x -11.02..-7.05, and a bell that flares above y 14 must lap it - the same lap the shipped
`vambraces` takes), one `near: cuff_low clears case_lower by 0.15 in x` (a clearance, not a
contact) and `pair spans 20.15 across the figure` (vambraces 20.00, buckler 20.40). No face on an
armor shell, no shared plane with any part: the 0.1 stand-off from x -9 / x -3 / z +-3 and the
0.05 insets on the bands did their job.

**Painting: two calls, one per sheet, and they covered everything.** Master: 181 face paints over
72 faces plus 6 texels; `part_inlay`: 73 face paints over the 48 cloth faces plus the same 6
texels. Zero unpainted, no stray paint, no colour on a greyscale sheet; Pillow on the saved PNGs
gives master 552 opaque texels 50..252, mask 432 texels 50..225, both grey. Structure of the
master call, general-to-specific: `"*.*": 105`, then each cube's `<cube>.*` base, then its one
outward face as a `[top, bottom]` pair (`west` outboard, `north` front, `south` back, `east` for
the buried inner plates), then per-cube `up`/`down` - never a global `*.up` after the per-cube
work, which would have flattened the bands. Lower ring 120 with west `[148, 112]`, bells 160-175
with `[225, 160]` on the outboard plate (brightest, as asked), bands 225-235 with a 58-60
underside, and the two inner cubes dropped to 78-110 because they sit inside the torso box and
are only ever seen when the wearer has no chestplate.

What the painter did **not** cover: **the bands are 0.4 units tall, so every band face is one
texel** - the bangles/buckler lesson again - and a `[top, bottom]` pair on them collapses to the
top value, so I wrote scalars and let the *silhouette* (0.15 proud, 0.4 tall) carry the braid.
The plates do have room: 2 units is 2 rows, 2.5 units is 3, and the ramp on the bell's outboard
face (225 down to 160 over three rows) is the only real shading on the part. `pixels` did the one
thing faces cannot - three 205 rivets along the bottom row of the bell's outboard face and three
165 ones on the ring's - and those six texels are also the only place the inlay mask differs in
texture from a flat wash. Nothing paints the *corners* where two rings' plates double up; they
read as a single grey, which is fine at 1/16 block per unit.

**For the next part.**
- Four bones rotated about two different axes cost nothing extra: model each plate upright in its
  own bone's unrotated frame with the pivot on the shared edge, and the tilt is one field. The
  reply's `past chestplate` line is the cheapest confirmation that a sign was right - it moves the
  moment the bone leans the way you meant.
- A tilted plate's top corner moves outward by (height x sin theta) and its own thickness by
  (t x cos theta). Budget the *guard* first and the decoration second; anything sitting proud at
  the top of a tilt spends the whole margin.
- `armorpieces_set_part` before painting still holds: it answered `sheets_created: [part_inlay]`
  and the mask call worked immediately after.
- `minecraft:golden_chestplate` is flat, unused by any other template and already cached:
  `python -m modpage build --offline` rendered 91 recipes with no warning at all.
- 12 cubes, the longest 6.9 units, fitted the default 64x32 with 552 texels used; the plugin never
  grew the sheet.
