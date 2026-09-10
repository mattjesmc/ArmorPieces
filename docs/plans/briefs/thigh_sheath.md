# Brief: Thigh Sheath

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the fourth
batch of four, a Wayfarer set (skim the lessons in knee_studs.md and swim_fins.md for the leg
frame and the leg's crowded front, and bangles.md for rings made of plates). From the `tassets`
row of `docs/plans/part-variety.md`:

> **Thigh Sheath** - A strapped-down knife on the outside of each thigh. Theme: Wayfarer.
> Fitting: `guard`.

**Part.** `armorpieces:thigh_sheath`, socket `tassets` only, in the mod's own pack. Display name
"Thigh Sheath". Fittings: `armorpieces:guard`, one mask, covering the knife's metal - hilt
fittings, crossguard, pommel and the sheath's chape at the tip; the leather sheath and straps
stay the material. No effects, no loot, no static layer.

**Shape.** `tassets` is a mirrored socket on the leg bone: model ONE leg, the LEFT, which in
this rig is at NEGATIVE x. The leg box is x -3.9..0.1, y 0..12, z -2..2 (pivot -1.9, 12, 0); the
leggings shell is that box inflated 0.4 (outer side x -4.3, front z -2.4, back z 2.4) and the
boots shell 0.9 (only matters below the knee); the anchor is at Blockbench (-1.9, 10, 0), high
on the outer thigh. "Outboard" is more negative x. Read the envelopes in the `armorpieces_new`
reply: the front of the thigh is taken by the knees and greaves parts (poleyns to z -4.65,
garters, knee_studs), the back of the ankle by the spurs parts, but the OUTER FACE of the thigh
above y 4 is free - the shipped tassets, pelt and scale_skirt are same-socket and never
compared. One more box the check never mentions: the player's ARM hangs beside the hip at
x -8..-4, y 12..24, z -2..2 (pouch_belt's session lost two hangers inside it), so nothing of
this part may rise above y 11.9. Build on that outer face: a `sheath` bone (pivot -4.3, 9.3, 0)
with the sheath body x -5.0..-4.4, y 3.8..9.3, z -0.75..0.75 and a chape cube at its tip 0.15
proud all round (x -5.15..-4.4, y 3.6..4.3, z -0.9..0.9); the bone rotated about X by 8
degrees so the tip trails back a little (positive X tips the lower end toward -Z on this rig -
check the reply, and flip if the tip went forward); a `hilt` bone above it with the grip
x -4.9..-4.5, y 9.3..11.3, z -0.35..0.35, a crossguard x -5.0..-4.4, y 9.2..9.6, z -0.9..0.9,
and a pommel x -5.0..-4.4, y 11.3..11.9, z -0.45..0.45 - the hilt bone gets the same 8 degrees
so the knife is straight; and two `strap_upper` / `strap_lower` bones, each a ring of four
plates a quarter unit thick and half a unit tall hugging the leggings shell a tenth off
(x -4.65..-4.4 and 0.6..0.85, z -2.75..-2.5 and 2.5..2.75, each plate the full span so corners
overlap), at y 7.8..8.3 and y 4.8..5.3, the outer plate of each passing OVER the sheath (so
push those two outer plates to x -5.35..-5.1 and let them float, they read as straps holding
the knife). The inner plates sit inside the other leg's shell and are never seen - paint them
anyway. Nothing below y 3.6 and nothing above y 11.9.

**Sheets.** Master: sheath and straps mid grey `[top, bottom]` darker toward the tip with a
stitched edge (a darker texel column, `pixels`); the grip a step darker with two lighter wrap
bands; crossguard, pommel and chape bright metal with dark undersides. Guard mask: the
crossguard, pommel and chape faces only, shaded like the master.

**Recipe.** Centre item `minecraft:iron_sword` (a flat item, unused by any template), paper
ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
thigh_sheath` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-03 in 36 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`list_outline`, 2 `remove_element` (starter cube, then its bone), 4 `add_group`, 4 `place_cube`,
8 `modify_cube`, 3 `armorpieces_check`, 1 `armorpieces_set_part`, **6 `armorpieces_paint`**,
4 `set_camera_angle`, 1 `armorpieces_save`. No `risky_eval`, nothing hand-edited; the save went
through first time without `force`.

**What I built.** Four bones under `part`: `sheath` and `hilt`, both pivoted at (-4.3, 9.3, 0)
and both rotated **-8 about X**, and `strap_upper` / `strap_lower` at (-4.3, 8.05, 0) and
(-4.3, 5.05, 0), unrotated. Cubes exactly as briefed except the two changes below:
`sheath_body` -5.0..-4.4 x 3.8..9.3 x +-0.75, `chape` -5.15..-4.4 x 3.6..4.3 x +-0.9, `grip`
-4.9..-4.5 x 9.3..11.3 x +-0.35, `crossguard` -5.0..-4.4 x 9.2..9.6 x +-0.9, `pommel`
-5.0..-4.4 x 11.3..11.9 x +-0.45, and two four-plate rings. Final envelope bone-local
x -2.75..3.45, y 0.06..8.47, z -2.80..2.80 = Blockbench **x -5.35..0.85, y 3.53..11.94**; reach
7.24. The pommel's rotated top corner lands at y **11.94**, 0.06 under the arm box - the check
never mentions the arm (it reports `past leggings y -0.46` and nothing else), so do that
arithmetic yourself: `y_top = pivot_y + h*cos(a) + (z_max)*sin(|a|)`.

**Rotation sign, measured on the first bone.** The brief's hedge was right to be there:
in Blockbench a **positive** X rotation swings a point below the pivot toward **-Z (forward)**,
so a back-trailing tip needs **-8**, not +8. I placed the `sheath` bone alone first and read the
envelope before anything else existed: bone-local z **-0.74..1.68** (bottom of the sheath at
+Z), which is the tip trailing back. The check prints the same z in both frames (only x and y
are re-framed: `bb_x = -bone_x - 1.9`, `bb_y = 12 - bone_y`), so a one-bone envelope is the
cheapest way to settle a rotation sign.

**The two `!` COPLANAR lines, and how they went away.** As briefed, both strap rings sat at
z -2.75..-2.5 / 2.5..2.75. The **lower** ring (y 4.8..5.3) overlaps `garters` (y 3.80..6.85) and
`greaves` (top y 4.80) in the other two axes, and both of those have a face at exactly
**z = -2.75**, so the check raised two `!` COPLANAR problems. Fix: push the lower ring 0.05
further out - front `z -2.80..-2.55`, back `2.55..2.80`, outer/inner plates spanning +-2.80 -
which cleared both at once. The upper ring keeps the briefed +-2.75/+-2.5 (nothing else on the
bone reaches y 7.8..8.3 at that z), so the two rings differ by 0.05 in depth; invisible, and
better than moving a ring that the check is happy with. **`!` lines accepted at save: none** -
`check_part.py thigh_sheath` is `ok: nothing needs a decision` with 44 `-` notes.

Those 44 are worth naming, because the brief's "the outer face of the thigh above y 4 is free"
is true only of the *tassets* socket. 16 hull OVERLAPs, every one of them into `garters` (knees,
which flares to x -5.95) or into the spurs crowd (`heel_wings` z 0..7.69, `spurs`, `streamers`):
the strap rings must close around the leg, and anything that closes around this leg passes
through whatever the knees and spurs sockets hang there. Two shared-plane *notes* (`y = 7.2` with
`greaves`, `y = 4.2` with `poleyns`) are marked "inside the shell, so occluded" and are notes,
not problems. Tightest real gaps: 0.01 in z to `garters`, `greaves` and `scale_shins` - the
z +-2.8/+-2.75 plates live one hundredth off their front faces.

**One geometry change from the brief, made off a screenshot.** With every plate at "the full
span", the front and back plates ran x -5.35..0.85 to keep the corners lapping the pushed-out
outer plate - and from the front they read as two flanges jutting a unit into the air off the
leg, a luggage rack rather than a strap. I trimmed all four to the brief's nominal
**x -4.65..0.85**; the ring is now open by 0.45 at the two outboard corners, which is exactly
the "let them float" the brief allows, and from every angle the outer plate reads as the keeper
crossing the knife.

**The painting lesson: -x faces are shaded hardest, so pre-compensate the money face.** The
whole part is read from outboard, i.e. off its **west** faces, and west is the darkest side in
Blockbench's preview (and Minecraft multiplies east/west by 0.6). My first pass gave the sheath
body `west [200, 152]` and `north [178, 138]`, and the render showed the outboard face as a
near-black slot while the *narrower* north face read as the light one. I proved which face was
which by painting `north 255` / `west 20` for one screenshot (one paint call, worth it) and then
lifted every outward face: `sheath_body.west [222, 172]`, `chape/crossguard/pommel.west
248..252`, `grip.west [200, 132]`, strap outer plates `west 186`. Rule of thumb that matches
swim_fins' tilted-flank finding: **+30 to +40 on a west face over what you would give the same
surface facing north.**

**Paint: six calls, master 284 texels (58..252, all grey), guard mask 26 texels (58..252).**
Call 1 was the whole master - `"*.*": 138`, `"*.up": 185`, `"*.down": 72`, then all 13 cubes face
by face, plus 10 `pixels`; it took the unpainted count from 78 to 0 in one go. Call 2 fixed two
stray pixels (below). Call 3 lifted the sheath body. Call 4 was the west/north probe. Call 5 was
the west pre-compensation plus the re-laid stitch column and buckle texels. Call 6 was the guard
mask: `chape`, `crossguard` and `pommel` only, value for value with the master, so the fitting
does not flatten the knife.

What the painter did **not** cover: the brief's "two lighter wrap bands" on the grip is
impossible - the grip is 2 units tall, so its side faces are **2 texels**, and a `[top, bottom]`
pair is the only band there is (one light row over one dark). Same for every strap plate: 0.5
tall = one texel, so their whole read is the flat value plus the silhouette; the "stitched edge"
survives only on the sheath body's west face, which is 2 texels of z by 6 rows - one column of
it (x=4, rows 2..7, about 40 below the gradient) is the seam. The two `pixels` per outer strap
plate at value 120 are the buckle/keeper over the knife, and are the only sub-face detail on the
straps.

**Trap: `pixels` coordinates go stale the moment you resize a cube.** I took
`strap_lower[0].west` from a layout printed *before* the ring was pushed to +-2.80; after the
resize that face had moved from `13,7` to `13,13`, and the two buckle texels landed nowhere -
the check caught it immediately as `! 2 opaque px outside every face`. Clearing them with
`value: null` and repainting at the new address was one call. **Re-read the face rectangles from
the reply of the resize itself, never from an older reply.**

**For the next part.** `minecraft:iron_sword` is now taken as a template centre item; the first
`python -m modpage build --offline` warned it had never been cached, one plain
`python -m modpage build` fetched it and the repeat offline build reported all three pages
`unchanged`. Thirteen cubes - two of them 5.5-long plates - fit the default 64x32 with room to
spare (284 opaque texels); the plugin never grew the sheet. Four other tabs were open and
`armorpieces_new` made this one active without touching them. On any leg socket that has to
*encircle* the leg, expect a dozen hull OVERLAP notes and do not try to dodge them: the knees
and spurs sockets own the front and the back of this bone, and z = -2.75 in particular is a
plane both `garters` and `greaves` already use.
