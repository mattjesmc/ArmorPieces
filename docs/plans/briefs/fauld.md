# Brief: Fauld

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the eleventh
batch (read girdle.md, cord.md and pouch_belt.md first - the waist frame, the ring of plates,
and the player's arm box the check cannot see). From the `belt` row of
`docs/plans/part-variety.md`:

> **Fauld** - A short skirt of hanging panels, front and back, below the plate. Theme: Knightly.
> Fittings: `banner`, `guard`.

**The banner is deliberately left off.** The shared `armorpieces:banner` fitting is fixed at
`front: "south"`, i.e. the design reads correctly from BEHIND, which suits a cape or a back
banner. A fauld's interesting panel is the front one, and a south-fronted pattern there would
be drawn back to front. Giving the fauld a correct front-reading banner would need a second
fitting definition, which is a data change beyond this content batch. So: `guard` only, and say
in your lessons that a front-reading banner fitting is the thing that would complete this part.

**Part.** `armorpieces:fauld`, socket `belt` only, in the mod's own pack. Display name "Fauld".
Fittings: `armorpieces:guard`, one mask, covering the panels' rivets and their bottom rims; the
panel plates stay the material. No effects, no loot, no static layer.

**Shape.** `belt` is not a mirrored socket: model the whole thing on the body bone. The torso
box is x -4..4, y 12..24, z -2..2 (pivot 0, 24, 0); the leggings shell is that box inflated 0.5
and the chestplate's a full unit (x -5..5, y 11..25, z -3..3), so every face lies past x ±5 or
z ±3; the anchor is at Blockbench (0, 12, 0). The player's ARMS hang at x ±4..±8, y 12..24,
z -2..2 on their own bones and the check never mentions them, so the flanks are invisible above
y 12 - put the panels on the FRONT and BACK only, as the plan says, and leave the hips bare.
Read the envelopes in the `armorpieces_new` reply: other belt parts are never compared; on the
back the carapace's lowest lame is y 15.6..16.7 at z 3.1..4.05, sash reaches y 16.5 at z 1..4,
spine_ridge's lowest plate y 15.77..16.83 - a waist band at y 12.5..13.5 clears them all;
dodge every listed plane by a twentieth. Build a `belt_band` bone with a ring of four plates a
quarter thick and one unit tall at y 12.5..13.5 a tenth off the shells (front z -3.45..-3.2,
back z 3.2..3.45, flanks x ±5.1..±5.35, each the full span so the corners double up, with the
front and back plates inset a twentieth in x and y so no two plates of your own share a plane -
rowel_spurs' and bells' rule). Then six panels, each its own bone hanging from the band: three
across the front at x -4.4..-1.6, -1.4..1.4 and 1.6..4.4, and three across the back at the same
x, each panel a plate 0.3 thick, hanging from y 12.6 (a tenth inside the band) down to y 9.4,
the front panels at z -3.5..-3.2 and the back ones at z 3.2..3.5, each bone rotated 5 degrees
about X so the hem swings away from the body (positive X swings a below-pivot end toward -z;
so the front panels want +5 and the back ones -5 - confirm on the first reply). A rivet 0.4
square standing 0.15 proud near the top of each panel, and a rim bar 0.2 proud and 0.4 tall
along each panel's bottom edge. Nothing below y 9.2.

**Sheets.** Master: band mid grey with a lighter top face; panels `[top, bottom]` lighter at the
top with a darker bottom row as each panel's shadow on the next (`pixels`); rivets and rims
bright. Guard mask: the six rivets and six rim bars only, shaded like the master.

**Recipe.** Centre item `minecraft:chainmail_leggings` (a flat item, unused by any template),
paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py fauld`
and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons paragraph below
filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-04 in 28 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`list_outline`, 2 `remove_element` (starter cube, then its bone), 7 `add_group`, 7 `place_cube`,
1 `armorpieces_set_part`, **2 `armorpieces_paint`**, 3 `armorpieces_check`, 2 `set_camera_angle`,
1 `armorpieces_save`. No `modify_cube`, no `risky_eval`, nothing hand-edited; the save went
through first time without `force` and `check_part.py fauld` / `check_authoring.py` were clean on
the first run afterwards.

**What I built.** Seven bones, 22 cubes - the most cubes any `belt` part has. `belt_band`
(pivot 0, 13, 0): four 0.25-thick plates at Blockbench y 12.5..13.5, `band_front`
x -5.3..5.3 z -3.45..-3.2 and `band_back` the mirror at z 3.2..3.45 (both inset 0.05 in x and y),
`band_right` x 5.1..5.35 and `band_left` x -5.35..-5.1, both running z -3.4..3.4 so the corners
double up. Six panel bones, all pivoted on the band line at y 12.6 - `panel_fl/fc/fr` at
(-3, 12.6, -3.4), (0, ...), (3, ...) rotated **+5** about X, `panel_bl/bc/br` at z +3.4 rotated
**-5** - each holding three cubes: a plate 2.8 x 3.2 x 0.3 (x -4.4..-1.6 / -1.4..1.4 / 1.6..4.4,
y 9.4..12.6, z -3.55..-3.25 front, 3.25..3.55 back), a 0.4 `rivet` standing 0.15 proud near the
top, and a 2.7-wide `rim` bar 0.2 proud along the hem. Envelope x +-5.35, Blockbench y 9.40..13.50
(bone-local 10.50..14.60), z -4.02..4.02; reach 7.44.

**The rotation sign the brief asked me to confirm: for a bone whose cubes hang BELOW its pivot,
+X swings the free end toward -z.** So the front panels take +5 and the back ones -5, exactly as
briefed, and the check confirmed it on the very first panel: `past leggings z+1.52` = z -4.02,
against the 4.023 I had computed from pivot + 3.2 sin 5 deg. Nothing needed nudging afterwards.
The floor was the same arithmetic: the lowest corner is the plate's *inner*-bottom one
(dz = +0.15, which the rotation pushes down), y = 12.6 - (3.2 cos 5 + 0.15 sin 5) = 9.399 - two
thousandths above the brief's 9.2 limit with room to spare.

**Nothing shares a plane, because every joint laps INTO the thing it hangs from.** The band's
front/back plates are inset 0.05 in x and y from the flanks and the flanks are pulled to z +-3.4
so the front plate's z = -3.45 outer face has no partner; each panel's inner face sits at
z -/+3.25, i.e. 0.05 *inside* the band plate's own 0.25 slab, and its top at y 12.6 is 0.05 inside
the band's 12.55; the rivets and rims bury 0.05..0.07 into the plate rather than sitting flush on
it, and I gave them different back-face depths (rivet -3.50, rim -3.48) so the two never share a
plane either. Result: not one coplanar or shell-surface note in the entire run. Copy this - it is
free at design time and expensive afterwards.

**The `!`s I accepted: none.** The only `!` that ever stood was the running unpainted-face count
(132/132), cleared by the first master call. I did accept **twelve `-` notes**, and eleven of them
are the same fact: `OVERLAP: panel_b{l,c,r} / belt_band into cloak:back's banner` (2.80 x 2.98 x
0.49 for the plates, 0.40 x 0.42 x 0.23 for the rivets, 2.70 x 0.26 x 0.30 for the rims, 0.11 and
0.06 for the band). `cloak:back` is a sheet hanging over the whole back at z 2.90..~3.74 from
Blockbench y 24.85 down to 9.63, so **any** back-hanging `belt` part intersects it unless it is
pushed past z 3.8 - 0.8 clear of the chestplate shell, which would make the fauld stand off the
body like a shelf. These are hull-test notes, not shared planes, so nothing z-fights: worn
together the cloak simply drapes over the back panels, which is what a cloak does. The twelfth is
`belt_band clears quiver:back's sling by 0.50 in z`, a gap. The save needed no `force`.

**Two paint calls, one per sheet, and what they covered.** Call 1, the master: `"*.*": 120` then
all 132 faces by name (22 cubes x 6 - there is no way to address a subset of cubes, `*` is all of
them, so a 22-cube part is a 132-entry `faces` map) plus 18 `pixels`. Band outer faces 168 front /
152 back with `up` 205/196 and buried inner faces 64; panel plates `[195, 128]` front and
`[180, 118]` back on the outward face, `[150, 98]` edges, 62 on the buried inner face; rivets 228
outward / 238 up; rim bars 212 outward / 232 up. The `pixels` are the brief's shadow row: the
bottom texel row of each plate's outward face (`north 57,1 3x4` -> y 4, x 57..59, and so on) at
96/90, which reads as the dark line just above the bright hem. Call 2 was the guard mask: the six
rivets and six rim bars only, at the master's own values, everything else simply left out of the
map (cheaper than `null`). Pillow on the saved sheets: master 500 opaque texels spanning 62..238,
guard 120 spanning 88..238, zero coloured texels on either, no mask texel outside the master's
silhouette. **No repaint was needed** - the values from cord's and pouch_belt's lessons (keep
metal in 96..238, save <70 for buried faces) landed right the first time, which is why this part
took two paint calls instead of the usual four.

What the painter did **not** cover: there is no painted seam or bevel between neighbouring panels
(the 0.2-unit gap between plates does that geometrically), no scallop or cusp at the hem, no
articulation line where a panel meets the band, and the flanks (x 4.4..5.35) are bare band with no
panel at all - the plan's own decision, since the player's arms hide them. The `[top, bottom]`
gradient on a 4-row face is the only modelling of the plates' curvature; a real fauld's lames
would want a lighter vertical highlight down each panel's centre column, which is 6 x 4 hand
pixels nobody will see at three metres.

**For the next part.**
- 22 cubes, the widest 10.6, fit a 64x32 sheet using rows 0..14 only (500 opaque texels). Cube
  count, not cube size, is what makes a `faces` map long.
- `cloak:back` is the back-socket part that overlaps everything at the waist: z 2.90..3.74,
  Blockbench y down to 9.63, x +-5.45. Any `belt`, `back` or `tassets` part with a back panel will
  collect the same OVERLAP notes. They are notes; decide once and say so.
- `minecraft:chainmail_leggings` was free: `armorpieces_set_part` wrote data, the `part_guard`
  sheet and the recipe together, the save installed both PNGs, and `python -m modpage build
  --offline` rebuilt all three pages with no uncached-texture warning at all (the first offline
  build already had the icon), so no plain `build` was needed - the first part in a while that
  skipped that step.
- **The banner fitting is the missing half of this part.** `armorpieces:banner` is defined with
  `front: "south"`, so its design reads correctly from behind; on a fauld the interesting panel is
  the front one and a south-fronted pattern there is drawn back to front. A `front: "north"`
  fitting (call it `blazon`) would let the three front panels carry a heraldic charge and would
  finish the Fauld, and would equally serve tassets, loin_panels and any other forward-facing
  masked part. That is a data change, deliberately out of this content batch's scope.
