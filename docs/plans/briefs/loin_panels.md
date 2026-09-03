# Brief: Loin Panels

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the sixth
batch of four (read thigh_sheath.md and padding.md first - the leg frame, the knees crowd's
planes, and that the check prints the OPEN piece bone-local). From the `tassets` row of
`docs/plans/part-variety.md`:

> **Loin Panels** - Two long cloth strips falling to the knee. Theme: Court. Fittings: `banner`,
> `inlay`.

The `banner` fitting maps a shield pattern onto a bone named `banner` and is out of scope for
this session: give the panels `inlay` only.

**Part.** `armorpieces:loin_panels`, socket `tassets` only, in the mod's own pack. Display name
"Loin Panels". Fittings: `armorpieces:inlay`, one mask, covering the cloth but not the hem row
and not the top band. No effects, no loot, no static layer.

**Shape.** `tassets` is a mirrored socket on the leg bone: model ONE leg, the LEFT, at NEGATIVE
x. The leg box is x -3.9..0.1, y 0..12, z -2..2 (pivot -1.9, 12, 0); the leggings shell is that
box inflated 0.4 (front z -2.4, back z 2.4); the anchor is at Blockbench (-1.9, 10, 0). The
player's ARM box (x -8..-4, y 12..24) is above this part; keep everything under y 11.9. Two
strips per leg, one on the FRONT of the thigh and one on the BACK, each its own bone pivoted on
the shell at (-1.9, 11.9, -2.4) and (-1.9, 11.9, 2.4): each strip 3 wide (x -3.4..-0.4), 0.4
thick and falling from y 11.9 to y 5.4, the front strip at z -3.15..-2.75 and the back at
z 2.75..3.15 in the unrotated pose, the bones rotated about X by +4 (front) and -4 (back) so
the hems swing away from the leg (a point below its pivot swings toward -Z under a positive X
rotation on this rig - thigh_sheath measured it; confirm on the first reply). A top band on
each strip, 0.15 proud and 0.7 tall at y 11.2..11.9, the same width, is the belt loop the
panel hangs from. Read the envelopes in the `armorpieces_new` reply before choosing the exact
z: the knees parts on the same bone use the planes z -2.65 (poleyns), -2.95 and -3.45
(padding), -3.0 and -3.5 (knee_studs), and the back is shared with the spurs parts (heel_wings
to y 8.28); hull overlaps with all of those are the socket's norm (tassets itself falls to
y 5.18), but no face of yours may lie on one of their planes, so shift by a twentieth where
the reply names a shared plane. Nothing below y 5.3.

**Sheets.** Master: strips mid grey `[top, bottom]` a little darker toward the hem, with a
brighter bottom row as the hem's braid and a darker second row as its shadow (`pixels`); bands a
step lighter. Inlay mask: every strip face at the same values but with the hem's two rows
`null`, and the bands left out, so the dye leaves a metal braid and loop.

**Recipe.** Centre item `minecraft:blue_wool` (a block with a flat texture, unused by any
template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
loin_panels` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

**Built 2026-09-03 in 20 bridge calls**: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`list_outline`, 2 `remove_element` (starter cube, then its bone), 2 `add_group`, 3 `place_cube`
(4 cubes), 3 `armorpieces_check`, 1 `armorpieces_set_part`, **2 `armorpieces_paint`**, 3
`set_camera_angle`, 1 `armorpieces_save`. No `modify_cube`, no `risky_eval`, nothing hand-edited:
the briefed numbers went in unchanged and the save went through first time without `force`.

**What I built.** Two bones under `part`, exactly as briefed: `panel_front` at
(-1.9, 11.9, -2.4) rotated **+4 about X** and `panel_back` at (-1.9, 11.9, 2.4) rotated **-4**.
Four cubes: `front_strip` (-3.4, 5.4, -3.15)..(-0.4, 11.9, -2.75), `front_band`
(-3.4, 11.2, -3.3)..(-0.4, 11.9, -2.6), and their mirror images in z on the back
(`back_strip` z 2.75..3.15, `back_band` z 2.6..3.3). The bands are the brief's "0.15 proud"
read as proud on **both** faces (0.7 x 0.7 in section, a square belt loop), which keeps their
z planes 0.05 off poleyns' z -2.65 and well clear of the leggings shell at z -2.4. Data:
`tassets` only, fitting `armorpieces:inlay`, no effects/loot/static, recipe
`minecraft:blue_wool` in a paper ring.

**Envelope, and the arm.** Bone-local x -1.50..1.50, y 0.04..6.56, z -3.60..3.60 = Blockbench
**x -3.4..-0.4, y 5.44..11.96, z -3.60..3.60**; reach 5.98. Two arithmetic notes for the next
tassets part: a strip whose top edge sits ON the pivot height still rises **above** it once the
bone is rotated - the band's top far corner lands at y 11.96, 0.06 over the 11.9 the brief asked
for (`y_top = pivot_y + |dz_max| * sin|a|`). That is still under the arm box's y 12, and this
part is at x -3.4..-0.4, entirely inboard of the arm's x -8..-4, so the arm was never in play;
but if you hang a panel on the OUTER thigh, budget that sine term. And the hem: 6.5 units of
drop at 4 degrees loses 0.07 of height and gains 1.20 of z, so the bottom sits at y 5.47 (brief:
nothing below 5.3) and the hem stands 1.2 off the leggings shell - the swing is all depth.

**Rotation sign confirmed, one bone at a time.** thigh_sheath's measurement holds: a **positive**
X rotation swings a point below the pivot toward **-Z**. I placed `panel_front` alone and read
`z -3.60..-2.75` before building anything else; the hem had swung forward, so +4 front / -4 back
is right for "away from the leg" on both sides.

**`!` lines accepted: none.** The saved check is `ok: nothing needs a decision`, with 7 `-`
notes: six hull OVERLAPs, all on the FRONT panel and all into the knees crowd - `poleyns`
(three, up to 1.85 x 2.86 x 0.85), `padding` (3.00 x 2.16 x 0.50), `knee_studs` and `garters` -
plus one near note, `panel_back` clearing `heel_wings`'s `vane_upper` by 0.41 in x. No COPLANAR
line was ever raised: the front planes z -3.15 / -2.75 / -3.30 / -2.60 dodge the knees planes
the brief listed (-2.65, -2.95, -3.45, -3.0, -3.5) by at least 0.05, and x -3.4 / -0.4 match
nobody's x face. The back panel meets nothing at all: the spurs parts all live below y 8.3 and
behind z 0..7.7 but the ones that reach up (heel_wings, spurs) sit outboard of x -2.9, and the
back strip stops at x -3.4 by 0.41. **The back of the thigh above y 5.4 is the emptiest place on
this bone** - the front is the one that has to lap.

**Paint: two calls - the master's 24 faces, then the mask's 12.** Call 1, master: `"*.*": 150` then every face of the four
cubes (strips `[168,128]` with the outward face `[180,140]`, the leg-side face `[128,94]`,
edges `[150,114]`/`[156,118]`, up 202, down 188; bands a step lighter at 196/204/168, up 218,
down 162) plus **32 `pixels`** - the hem braid at 212 and its shadow at 92, painted as two full
sheet rows across each strip's whole 8-texel-wide face block (`x 0..7` and `x 16..23` at
`y 6` and `y 7`), which is one row for all four side faces at once. Nothing was left unpainted
and no second pass was needed. Call 2, `part_inlay`: the same face values on the two strips'
12 faces only - the bands are simply absent from the mask, so the belt loops stay on the material ramp -
with the same 32 hem/shadow texels and both `.down` faces passed as `value: null`.

What the painter did **not** cover: the strip is 3 x 6.5 x 0.4, so its side edges are **one
texel wide** - no lengthwise seam or fold is possible there, and the only vertical structure the
panel has is the `[top, bottom]` gradient plus the two hem rows. There is no per-panel motif;
the brief did not ask for one and a 3x7 face has no room for a device beside the hem.

**The mask-null idiom, second confirmation.** padding's finding is general: `applyMask` replaces
the baked pixel wherever the mask is opaque, so anything meant to survive a dye has to be a hole.
Nulling the two hem rows and the hem's underside on `part_inlay` is what makes the brief's
"metal braid on a dyed panel" true; leaving out the band cubes entirely does the same for the
loops. Neither shows up in the check either way - it is a decision the tooling will not make.

**For the next part.** `minecraft:blue_wool` is now taken as a template centre item; the first
`python -m modpage build --offline` warned it had never been cached, one plain
`python -m modpage build` fetched it (a block, but one with a flat inventory texture, so no
hand-drawn icon was needed) and the repeat offline build reported all three pages `unchanged`.
Four cubes fit the default 64x32 with the whole sheet below y=8 and x<32 - a `banner` fitting
added later (out of scope here) would have room for its own bone. The `tassets` socket's own
crowd is still never compared: pelt, scale_skirt, tassets and thigh_sheath are listed in the
envelope reply for reference only, and thigh_sheath's x -5.35..0.85 does NOT constrain you.
