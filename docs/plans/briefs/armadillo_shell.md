# Brief: Armadillo Shell

The seventh piece of **Armor Pieces: Animals** (`docs/plans/set-packs.md`). A banded plate over each
knee — the piece in the pack whose whole read is one idea: **bands**.

**Part.** `armorpieces_animals:armadillo_shell`, socket `knees` only. Display name "Armadillo
Shell". Fittings: `armorpieces:guard`, **one mask covering the edging only** — the metal lip around
the outermost band. No effects, no loot rows.

    name: armadillo_shell
    anchor: knees
    namespace: armorpieces_animals
    datapack: C:\Users\Matthijs\ArmorPieces\packs\animals\datapack
    resourcepack: C:\Users\Matthijs\ArmorPieces\packs\animals\resourcepack

**Shape.** `knees` is a **mirrored** socket: model ONE knee and the pair is made for you. Remember
the rig's frame — the player's **left** limbs sit at negative x, left leg x −3.9..0.1 with its pivot
at (−1.9, 12, 0), and the leggings' leg shell is the leg box inflated by 0.4.

- **Three bands** curling over the front of the knee, each its own cube, the middle one widest:
  perhaps 4 × 2 × 1, 4.5 × 2 × 1, 4 × 2 × 1 stacked down the knee with each stepped 0.25 further out
  than its neighbour, so the profile is convex like the animal's. The step is what makes flat boxes
  read as a shell — the turtle and the frog both found the same thing.
- The bands should **curl round the outside** of the joint: give each its own bone and rotate them a
  few degrees of Y so their outer ends wrap the leg's side rather than stopping flat at its corner.
- An **edging** along the outer rim of the middle band, a quarter texel proud: the hardware, and the
  only thing on the master.
- Keep the whole thing under 2 units deep at the front. `poleyns`, `winged_cops`, `fanged_cop`,
  `garters`, `knee_studs` and `padding` are already on this socket and several are bulky; the
  `armorpieces_new` reply lists every envelope in both frames. This should read as the *smallest*
  of them.
- Nothing coplanar with the leggings shell.

**Sheets.** Three:

- `armadillo_shell.png` — master, greyscale, form and silhouette. The **edging** is the only
  hardware and stays here.
- `armadillo_shell_static.png` — RGBA, the shell's own colour.
- `armadillo_shell_guard.png` — greyscale mask, **the edging's faces only**.

The armadillo's palette, from `python tools/mob_reference.py armadillo`. It is a dusty pink-brown
animal, and only eight colours — the bands' seams are the darkest two:

| hex | share | value | what it is |
|---|---|---|---|
| `#824848` | 16.1% | 89 | the shell's body colour — most of each band |
| `#713e3e` | 11.3% | 77 | the shaded band, its lower edge |
| `#5c2d30` | 13.4% | 59 | the darkest — **the seams between bands** |
| `#965954` | 7.2% | 107 | a shade up, the band's middle |
| `#a06460` | 9.0% | 117 | the lit band |
| `#ad716d` | 12.5% | 130 | the pink-lit top of each band |
| `#b67b76` | 13.7% | 140 | the palest pink, the crown of the middle band |
| `#c68375` | 6.0% | 149 | one highlight row at most |

The seams are the piece. Three bands with `#5c2d30` between them reads as an armadillo; three bands
without reads as a stack of plates.

**Look at the armadillo once, first**: `tools/.mcassets/reference/entity/armadillo/armadillo@8x.png`.
Picture budget about six.

**The active-tab hazard — the one thing that has damaged a piece in this pack.**

- **After `armorpieces_new`, call `get_project_info` and confirm the name before your first edit.**
- Every mcptoolkit reply's check line begins `[armorpieces] <piece>` — read that name.
- If you land an edit in the wrong piece:
  `armorpieces_open <the damaged piece> {discard: true, reload: true}`. **Never `undo`** — it acts on
  whatever tab is active. `modify_cube` is safe where `undo` is not.
- **Close your tab at the end** with `armorpieces_close`.

**The short form of six sessions' lessons.**

- One `armorpieces_set_part` call creates the static layer *and* the mask sheet: pass the fitting and
  `static: true` together, before painting.
- Master, static and mask take the **same `faces` dict** — same keys, same order. An opaque mask
  pixel wins over the static layer; `pixels` with `value: null` punches a hole the fitting leaves.
- **Do not shade a face taller than two rows with a `[top, bottom]` pair** — it interpolates, and the
  interpolated row belongs to no palette entry, which breaks the end-of-session count proof. Flat
  fills plus explicit `pixels`.
- **Resizing a cube after painting is safe** — the paint moves with it, and the reply's sheet-layout
  block confirms the new rectangles.
- **The 3D view only ever shows the master.** Prove the sheets with a Pillow read at the end: equal
  opaque counts on master and static, each master value's count matching its palette colour's count,
  zero static or mask pixels outside the master.
- The COPLANAR check flags the **plane**, not the overlap; a trim of 0.05 clears it and costs no UV
  texel. `-` notes are not `!` problems.
- Groups cannot be renamed; a group's origin and rotation cannot be changed after `add_group`.
  Compute pivots and angles first, place cubes unrotated, rotate the bone. Never name a bone `root`.
- **Silhouette is what sells it.** Take one render and ask what the outline says before painting.
- `python tools/check_part.py` does not see this pack.
- Recipe centres taken in this pack: `minecraft:sweet_berries`, `minecraft:lily_pad`,
  `minecraft:honeycomb`, `minecraft:turtle_helmet`, `minecraft:poppy`, `minecraft:lead`.

**Recipe.** Centre item `minecraft:wolf_armor` (vanilla makes it from armadillo scutes, and it is
unused by any template in the mod or this pack — `minecraft:armadillo_scute` itself is already taken
by a mod piece), paper ring, craftable. Result is the `knees` template.

**Done means.** `armorpieces_save` accepted without `force`;
`python tools/check_authoring.py packs/animals/datapack packs/animals/resourcepack` clean; tab
closed; the Lessons section below filled in. No modpage build.

## Lessons from the session

Built as seven cubes in four bones: `main` (unrotated) holding three stacked band plates and the
edging, plus three sibling bones `wrap_top` / `wrap_mid` / `wrap_bot`, each rotated **Y +30 deg**,
holding one chamfer plate that carries the band round the leg's outer corner. Envelope (Blockbench)
x -5.43..0.65, y 4.0..8.0, z -4.00..-2.50; bone-local x -2.55..3.33, y 4.00..8.00, z -3.60..-2.15.
Saved clean without `force`, `check_authoring.py` clean on both pack folders. Five renders.

**The starter cube carries inflate 0.25 — zero it before you trust a single number.** The first
resize produced three COPLANAR lines against `thigh_sheath` at x = +-2.75 when the cube's own faces
were at +-2.5. The clearance line said `past leggings x+0.35 z+1.20` where the arithmetic said
+0.10 / +0.95: every figure was 0.25 too generous, in every axis, because the check measures the
*inflated* box. One `modify_cube {inflate: 0}` and the numbers matched the arithmetic exactly. This
is the first thing to do on a new piece; nothing else in the reply hints at it.

**Bone-local x on a leg is MIRRORED, not offset.** The envelope table converts as
`bone_x = -(blockbench_x + 1.9)` for the left leg, not `+1.9`. Getting the sign backwards makes the
"past boots" and "past body" lines read as nonsense — they are the only way to recover the shells'
real boxes, and from them: leggings = leg inflated **0.4** (x -4.3..0.5, z -2.4..2.4), boots = leg
inflated **0.9** (x -4.8..1.0, z -2.9..2.9). The boot box is the one that bites on `knees`: it is a
whole unit bigger than the body and 0.5 bigger than the leggings, so a knee piece drawn to clear the
*leggings* is still swallowed by a booted player.

**That was the silhouette failure, and it was worth the two renders it cost.** The first pass had
fronts at z -3.10 / -3.35 / -2.95 (0.55-0.95 past the leggings) and the render showed a thin dark
line with the bottom band gone entirely — buried in the boot. Pushing every front out by 0.35-0.45
(final: bot -3.40, top -3.45, mid -3.75, edging -4.00) put all three bands 0.5-1.1 clear of the
**boots** and the three-band read appeared at once. Rule for the next leg piece: **measure clearance
from the boots line, not the leggings line**, and aim for 0.5 minimum.

**A COPLANAR line names the plane, so dodge it by 0.05-0.12 rather than redesigning.** Three
separate hits, all from `thigh_sheath` (tassets, worn together): x = -2.5, z = -2.5, z = -2.55.
Moving the bands' back faces to z = -2.62 cleared all of them and cost nothing, since those faces
are inside the leg and never drawn. Note the test needs the faces to *overlap in the other two
axes*: `band_bot` sat on z = -2.5 unflagged for the whole session because its y range misses the
strap's. Do not read "not flagged" as "not on the plane".

**Rotated wrap plates: the pivot is fixed forever, so pick it last and place the cube around it.**
A group's origin cannot be changed after `add_group`, so the three wrap bones were pinned at their
band's outer-front corner while the bands were still at their first-pass depth. When the bands moved
forward 0.35-0.45 the cubes moved with them but the pivots did not, which is harmless — the plate
simply swings about a point 0.4 behind its own front face — but every clearance had to be recomputed
by hand: for a plate at cumulative Y angle `a`, a corner at bone-local `(dx, dz)` lands at
`(dx*cos a + dz*sin a, -dx*sin a + dz*cos a)`. The rule that made the wraps safe:
**a rotated plate is clear of a shell if every one of its four xz corners is outside the shell box
AND each of its two long edges crosses the shell's x plane at a z still outside it** — checking
corners alone passes plates whose middle cuts the shell corner. At +30 deg with a 0.9 reach the top
and mid wraps clear everything; the bottom wrap's back-outer corner sits inside the *boot* box by
about 0.2, which is hidden geometry and produced only `-` notes.

**Sheets, and the count proof.** 42 faces, three calls, no shape tools. Master carries all 42;
`part_static` carries the six shell cubes' 36; `part_guard` carries the edging's 6 with the same
greys the master has there. Choosing the edging's greys (150/165/175/185/200/235) disjoint from the
palette's values (59/77/89/107/117/130/140/149) made the proof exact in one pass:

    master 150 = static 124 + guard 26, overlap 0, uncovered 0, outside 0
    every palette value's count == its hex's count (25/43/22/4/10/2/8/10)
    the 26 master pixels whose value is NOT in the palette are exactly the 26 mask pixels
    master and guard: 0 non-grey pixels

Only two faces are two rows tall (`band_mid.north`, `wrap_mid_p.north`), so those take a
`[top, bottom]` pair and land on exactly two palette values; everything else is a flat fill plus six
explicit tick `pixels`. **The seams are three flat `down`/`up` faces filled 59** — `band_mid.down`,
`band_top.down` and `band_bot.up` — which is why the bands read as bands rather than as a stack: the
ledge the z-step creates is a real face, and painting it the darkest palette entry costs nothing.

**Resizing after painting moved the paint every time and only warned once.** Deepening `band_mid`
from 0.73 to 1.13 grew four faces (`up`, `down`, `east`, `west`) and the reply named exactly those
four; one repeat of those four keys fixed it. The later depth changes (0.75 -> 0.9, 0.35 -> 0.4) grew
nothing because the face rectangles still rounded to the same pixel count. **The tick `pixels` moved
with their face** — `band_mid.north` migrated from uv 1,1 to 20,4 and the ticks went with it — so do
NOT re-send the original `pixels` list after a resize, or they land on the old coordinates as stray
paint. Re-send only the grown faces.

**For the last Animals piece (`rabbit_feet`, spurs).** Recipe centres now taken in this pack:
`minecraft:sweet_berries`, `minecraft:lily_pad`, `minecraft:honeycomb`, `minecraft:turtle_helmet`,
`minecraft:poppy`, `minecraft:lead`, `minecraft:wolf_armor`. `spurs` is on `left_leg` too, so the
boots-inflate-0.9 number and the mirrored bone-local x apply unchanged — and `spurs` sits at the
ankle where the boot box is at its most opaque, so budget the same 0.5 clearance from -2.9 / -4.8.
`armorpieces_set_part` with `fittings` + `static: true` in one call created both sheets before any
paint. The active-tab hazard never fired: `get_project_info` once after `armorpieces_new` and then
the `[armorpieces] armadillo_shell` prefix on every reply; nine other tabs were open, two with
unsaved edits, none touched, tab closed at the end. `python tools/check_part.py` still does not see
this pack; `check_authoring.py` on the two pack folders and the bridge's own check are the gate.
The pack still has **no `armorpieces-sets.json`** — the Menagerie file the plan calls for has not
been written yet, and eight pieces will be finished without it.
