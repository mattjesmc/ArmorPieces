# Brief: Mail Fringe

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the eleventh
batch - the last part of `docs/plans/part-variety.md`'s candidate list (read loin_panels.md,
thigh_sheath.md and boot_cuffs.md first - the leg frame, the tassets socket's planes, and that
the check prints the OPEN piece bone-local). From the `tassets` row:

> **Mail Fringe** - A short curtain of chain hanging off the belt line. Theme: Knightly.
> Fittings: none.

The plan lists no fitting; this brief gives the whole curtain a `guard` mask, since it is all
metal and every other part on the socket takes something.

**Part.** `armorpieces:mail_fringe`, socket `tassets` only, in the mod's own pack. Display name
"Mail Fringe". Fittings: `armorpieces:guard`, one mask, covering every face. No effects, no
loot, no static layer.

**Shape.** `tassets` is a mirrored socket on the leg bone: model ONE leg, the LEFT, at NEGATIVE
x. The leg box is x -3.9..0.1, y 0..12, z -2..2 (pivot -1.9, 12, 0); the leggings shell is that
box inflated 0.4 (front z -2.4, back z 2.4, outer x -4.3); the anchor is at Blockbench
(-1.9, 10, 0). The player's ARM hangs at x -8..-4, y 12..24, so nothing may rise above y 11.9.
Read the envelopes in the `armorpieces_new` reply: same-socket parts are never compared, but
the knees crowd owns the front from y 3.7 up and uses the planes z -2.65 / -2.75 / -2.95 /
-3.0 / -3.15 / -3.20 / -3.45 / -3.5 / -3.62 / -3.70, and boot_cuffs rings the leg at
y 8.5..9.7 with faces at z ±3.05..±3.3 and x -5.2 / -4.95 / 1.1 / 1.35 - a curtain that stops
above y 10 clears the boot cuff and most of the knees crowd; dodge every plane the reply lists
by a twentieth. Build a `hanger` bone at (-1.9, 11.9, 0) with a top bar 0.3 thick and half a
unit tall ringing the thigh a tenth off the shell at y 11.4..11.9 (outer x -4.7..-4.4, inner
x 0.6..0.9, front z -2.8..-2.5, back z 2.5..2.8, each the full span so the corners double up,
the front and back plates inset a twentieth in x and y so no two of your own plates share a
plane). Then the curtain: sixteen `link_*` cubes in ONE `curtain` bone, each 0.5 wide, 0.35
thick and of a slightly different length, hanging from y 11.5 (a tenth inside the bar) down to
between y 10.4 and y 9.6 - four along the front bar at x -4.15, -2.95, -1.75, -0.55, four
along the back at the same x, and four down each flank at z -1.8, -0.6, 0.6, 1.8 - so the
curtain rings the thigh with a ragged hem. Give the sixteen lengths a repeating 3-step pattern
(long, short, medium) rather than making them all equal: that ragged hem is the whole read at
three metres. Every link's outer face sits a twentieth proud of its bar. Nothing below y 9.5.

**Sheets.** Master: bar mid grey with a lighter top face; links a step lighter with a
`[top, bottom]` pair darkening toward the hem and a bright bottom texel each, and alternate
links half a step darker so the curtain reads as woven rather than as a comb. Guard mask: every
face at the master's values.

**Recipe.** Centre item `minecraft:netherite_scrap` (a flat item, unused by any template),
paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
mail_fringe` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

**Built 2026-09-04 in 19 bridge calls**: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`list_outline`, 2 `remove_element` (starter cube, then its bone), 2 `add_group`, 2 `place_cube`
(4 bar cubes, then all 16 links in one call), 1 `armorpieces_check`, 1 `armorpieces_set_part`,
**4 `armorpieces_paint`** (3 master, 1 mask), 3 `set_camera_angle`, 1 `armorpieces_save`. No
`modify_cube`, no `risky_eval`, nothing hand-edited: every briefed number went in unchanged
except the link thickness (below), the geometry never raised a single `!`, and the save went
through first time without `force`.

**What I built.** Two bones under `part`, both unrotated: `hanger` at (-1.9, 11.9, 0) with the
four bar plates, and `curtain` at (-1.9, 11.5, 0) with the sixteen links. Bar: `bar_out`
(-4.7, 11.4, -2.75)..(-4.4, 11.9, 2.75), `bar_in` x 0.6..0.9 the same, `bar_front`
(-4.65, 11.45, -2.8)..(0.85, 11.85, -2.5), `bar_back` z 2.5..2.8. Links 0.5 wide, **0.33** thick,
top y 11.5, hems on a repeating 9.6 / 10.4 / 10.0 pattern walked around the ring
(f1 9.6, f2 10.4, f3 10.0, f4 9.6, b1 10.4, b2 10.0, b3 9.6, b4 10.4, o1 10.0, o2 9.6, o3 10.4,
o4 10.0, i1 9.6, i2 10.4, i3 10.0, i4 9.6): front z -2.85..-2.52 and back z 2.52..2.85 at
x -4.15/-2.95/-1.75/-0.55, outer x -4.75..-4.42 and inner x 0.62..0.95 at z centres
-1.8/-0.6/0.6/1.8. Envelope bone-local x -2.85..2.85, y 0.10..2.40, z -2.85..2.85 = Blockbench
**x -4.75..0.95, y 9.60..11.90, z -2.85..2.85**; reach 4.36, past leggings 0.45 in x and z.
Nothing above 11.9, nothing below 9.6. Data: `tassets` only, fitting `armorpieces:guard`, no
effects/loot/static, recipe `minecraft:netherite_scrap` in a paper ring.

**Two arithmetic changes to the brief, both to keep my own plates off each other's planes.**
The brief's "each the full span so the corners double up" plus "the front and back plates inset a
twentieth in x and y" leaves the side plates' end caps at z = ±2.8 **on the same plane** as the
front/back plates' proud faces, which z-fight at the four corners where the plates lap. Fix: the
side plates stop at z ±2.75, a twentieth inside the front/back plates, so the corners still
double up in volume but share no plane. Same problem one level down: a link 0.35 thick whose
outer face is a twentieth proud of a 0.3-thick bar has its inner face exactly on the bar's inner
face, so I made every link **0.33 thick** - outer face 0.05 proud, inner face 0.02 *inside* the
bar's volume (buried where they lap, exposed below it). Net planes used: x -4.75/-4.7/-4.65/-4.42
/-4.4/0.6/0.62/0.85/0.9/0.95, y 9.6/10.0/10.4/11.4/11.45/11.5/11.85/11.9, z ±2.85/±2.8/±2.75
/±2.52/±2.5 - no two of mine coincide, and none of them is a plane the knees, greaves or spurs
crowd uses. **The check never tests a part against its own cubes**, so this is arithmetic you have
to do yourself; it will not be reported.

**`!` lines accepted: none.** `check_part.py mail_fringe` is `ok: nothing needs a decision` with
9 `-` notes, and every one of them is the same neighbour: `boot_cuffs` (greaves), the only other
part on this bone that reaches into y 8.5..9.82. They are all *near* notes, not overlaps - the
curtain clears its `cuff` ring by 0.15..0.30 and its four rotated fold plates by 0.18..0.23. No
COPLANAR line was ever raised, at any stage: the briefed 9.6/10.0/10.4 hems dodge boot_cuffs'
y 8.5/9.7/8.7/9.8, and stopping the hem at 9.6 keeps the whole part above the knees crowd
(poleyns tops out at y 8.30) and the spurs crowd (heel_wings 8.28). **A tassets part that stays
in y 9.5..11.9 meets nothing but boot_cuffs**, which is why this was the cleanest leg part yet.

**Paint: four calls, 280 + 64 + 48 master faces and 120 mask faces.** Call 1 was the whole master
in one map: `"*.*": 150`, `"*.up": 176`, `"*.down": 200` as a floor, then all 24 bar faces
explicitly (outer plate's `west` [206,182] per thigh_sheath's money-face rule, leg-side faces
110..120, tops 194..202) and all 96 link faces, each link's outward face a `[top, bottom]` pair
darkening toward the hem, its leg-side face dark, its `down` face bright, and **alternate links a
step darker all the way round the ring** so the curtain reads woven rather than as a comb. That
took the unpainted count from 120 to 0 in one go. Calls 2 and 3 were both reactions to
screenshots: the links read *darker* than the bar and than the iron leggings behind them, so call
2 lifted every outward and edge face (front/back to [206,178]/[186,158], the outer flank's west
faces to [232,202]/[212,184]) and call 3 raised only the **bottom** ends of those pairs by ~18
after the first lift left the hems fading into the leg - the ragged hem is the whole read, and a
hem painted dark disappears at three metres even though the geometry is right. Call 4 was
`part_guard`, all 120 faces value for value with the finished master, so the guard fitting
recolours the fringe without flattening it.

What the painter did **not** cover: every link face is **1 texel wide by 2 tall** (0.5 x 1.9
units), so a `[top, bottom]` pair *is* the entire vertical story of a link and there is no room
for a ring pattern, a rivet or a seam on one. The brief's "a bright bottom texel each" therefore
went on the `down` face (236 light / 218 dark, one texel), not on the outward face: a bright
bottom row there would have **replaced** the gradient's lower half and destroyed the darkening the
same sentence asks for. The bar's side plates are 6x1 texel faces, so they too are flat values
plus the up/down highlight - no lengthwise seam, no buckle, no per-link chain detail anywhere on
this part. All 20 cubes fit the default 64x32 with everything at y<8; the plugin never grew the
sheet, and no `pixels` were used at all.

**For the next part.** `minecraft:netherite_scrap` is now taken as a template centre item; the
first `python -m modpage build --offline` warned it had never been cached, one plain
`python -m modpage build` fetched it (a flat item, no hand-drawn icon needed) and the repeat
offline build reported all three pages `unchanged`. Sixteen small cubes in one bone are cheap:
one `place_cube` call placed them all and the reply printed all sixteen UV blocks, so the whole
paint map could be written from that single reply. And the y 9.5..11.9 band of the leg bone -
the top of the thigh, under the arm - is still nearly empty apart from this fringe and
boot_cuffs' ring just below it.
