# Brief: Rabbit Feet

The eighth and **last** piece of **Armor Pieces: Animals** (`docs/plans/set-packs.md`). A lucky
rabbit's foot hung behind each heel — the smallest piece in the pack, and the one that finishes the
set.

**Part.** `armorpieces_animals:rabbit_feet`, socket `spurs` only. Display name "Rabbit Feet".
Fittings: `armorpieces:gemstone`, **one mask covering the charm's cap only** — the little mount the
foot hangs from. No effects, no loot rows.

    name: rabbit_feet
    anchor: spurs
    namespace: armorpieces_animals
    datapack: C:\Users\Matthijs\ArmorPieces\packs\animals\datapack
    resourcepack: C:\Users\Matthijs\ArmorPieces\packs\animals\resourcepack

**Shape.** `spurs` is a **mirrored** socket on the boots: model ONE and the pair is made for you.
The rig's frame matters here — the **boots' shell is the leg box inflated by 0.9, so its front plane
is z −2.9, not −3**, and the left leg sits at negative x.

- A **cap** at the back of the heel where the charm is fixed: 2 × 1 × 1, sitting against the boot's
  back face. This is the hardware, the gemstone's face, and the only thing on the master.
- A **thong** of one or two 1 × 1 cubes hanging from it.
- The **foot** itself: two cubes, an upper about 1.5 × 3 × 1.5 and a lower about 1.5 × 1.5 × 2.5
  turned forward at the bottom so it reads as a foot rather than a stick — the little L is the whole
  idea. Rotate the bone, not the cube.
- Total drop: keep the bottom of the foot **above the boot's sole**. A charm that reaches the ground
  clips through the floor on every step.
- `spurs` already carries anklets, bells, heel_wings, rowel_spurs, spurs, streamers and talons —
  seven pieces on a small socket, so read the envelope table in the `armorpieces_new` reply
  carefully and sit **behind** the heel where `bells` and `anklets` are not.
- Nothing coplanar with the boot shell.

**Sheets.** Three:

- `rabbit_feet.png` — master, greyscale, form and silhouette. The **cap** is the only hardware.
- `rabbit_feet_static.png` — RGBA, the fur.
- `rabbit_feet_gemstone.png` — greyscale mask, **the cap's faces only**.

The brown rabbit's palette, from `python tools/mob_reference.py rabbit_brown` — note that vanilla has
no plain `rabbit.png`, seven colour variants and no default, and **brown is the one people picture**:

| hex | share | value | what it is |
|---|---|---|---|
| `#966945` | 26.6% | 114 | the fur's body colour |
| `#a0744d` | 24.4% | 125 | the lit fur |
| `#ab8361` | 18.5% | 139 | lighter still, the top of the foot |
| `#b49173` | 14.9% | 152 | the pale fur, the toes |
| `#bfa286` | 4.4% | 167 | the palest — one highlight |
| `#875c3b` | 2.1% | 101 | a shade down, the fur's shaded side |
| `#75492c` | 2.7% | 83 | darker, under the foot |
| `#553625` | 4.9% | 61 | the darkest — the thong, and the crease at the ankle |

**Look at the rabbit once, first**: `tools/.mcassets/reference/entity/rabbit/rabbit_brown@8x.png`.
Picture budget about six — but this is a small piece, so three or four should do.

**The active-tab hazard — the one thing that has damaged a piece in this pack.**

- **After `armorpieces_new`, call `get_project_info` and confirm the name before your first edit.**
- Every mcptoolkit reply's check line begins `[armorpieces] <piece>` — read that name.
- If you land an edit in the wrong piece:
  `armorpieces_open <the damaged piece> {discard: true, reload: true}`. **Never `undo`** — it acts on
  whatever tab is active. `modify_cube` is safe where `undo` is not.
- **Close your tab at the end** with `armorpieces_close`. You are the last session, so leave the
  editor as you found it.

**Two things the Armadillo Shell session found, and both bite hardest on a boots piece.**

- **The starter cube carries `inflate: 0.25`. Zero it before you trust a single number.** Every
  clearance figure in the check is measured on the *inflated* box, so the armadillo's first
  arithmetic was 0.25 too generous in every axis and it collected three phantom COPLANAR lines. One
  `modify_cube {inflate: 0}` made the numbers match the arithmetic exactly. Nothing else in the
  reply hints at this — do it first.
- **Bone-local x on a leg is MIRRORED, not offset**: `bone_x = -(blockbench_x + 1.9)` for the left
  leg. Get the sign backwards and the "past boots" lines read as nonsense. And the shells differ
  more than you would guess: leggings = leg inflated **0.4** (x −4.3..0.5, z −2.4..2.4), **boots =
  leg inflated 0.9** (x −4.8..1.0, z −2.9..2.9). The boot box is a whole unit bigger than the body,
  and it is the one that governs this piece: a charm drawn to clear the leg is still swallowed by
  the boot.

**The short form of seven sessions' lessons.**

- One `armorpieces_set_part` call creates the static layer *and* the mask sheet: pass the fitting and
  `static: true` together, before painting.
- Master, static and mask take the **same `faces` dict** — same keys, same order. An opaque mask
  pixel wins over the static layer; `pixels` with `value: null` punches a hole the fitting leaves.
- **Do not shade a face taller than two rows with a `[top, bottom]` pair** — it interpolates, and the
  interpolated row belongs to no palette entry, which breaks the end-of-session count proof.
- **Sub-unit faces are one texel**, so a `[top, bottom]` pair and any per-row shading do nothing
  there — this piece is small enough that most of its faces are in that class. Flat fills plus
  explicit `pixels` is the way.
- **Resizing a cube after painting is safe** — the paint moves with it.
- **The 3D view only ever shows the master.** Prove the sheets with a Pillow read at the end: equal
  opaque counts on master and static, each master value's count matching its palette colour's count,
  zero static or mask pixels outside the master.
- The COPLANAR check flags the **plane**, not the overlap; a trim of 0.05 clears it and costs no UV
  texel. `-` notes are not `!` problems.
- Groups cannot be renamed; a group's origin and rotation cannot be changed after `add_group`.
- **Silhouette is what sells it.** For a piece this small the outline is nearly all of it.
- `python tools/check_part.py` does not see this pack.
- Recipe centres taken in this pack: `minecraft:sweet_berries`, `minecraft:lily_pad`,
  `minecraft:honeycomb`, `minecraft:turtle_helmet`, `minecraft:poppy`, `minecraft:lead`,
  `minecraft:wolf_armor`.

**Recipe.** Centre item `minecraft:rabbit_foot` (unused by any template in the mod or this pack),
paper ring, craftable. Result is the `spurs` template.

**Done means.** `armorpieces_save` accepted without `force`;
`python tools/check_authoring.py packs/animals/datapack packs/animals/resourcepack` clean — it will
then be reading all eight pieces of the finished pack; tab closed; the Lessons section below filled
in. No modpage build.

## Lessons from the session

<!-- filled in by the session: the bridge, the workarounds, paint calls, and - as the last piece -
     anything the NEXT set pack (Coral, Boss, Nether) should know before it starts. -->

Built 2026-09-07. 4 cubes in 2 bones, 100 opaque master texels on the starter 64x32 sheet, four
pictures spent (the rabbit, a back three-quarter, two profiles). No `!` stood at save; the save was
accepted without `force`.

**The shape, and the one place the brief could not be followed.** Cap 2x1x1 at Blockbench
`z 2.95..3.95, y 7.4..8.4`; a 1 x 1.5 x 0.8 thong; a 1.5 x 3.1 x 1.5 shank hanging vertically; a
1.5 x 3.05 x 1.5 pad in a bone pivoted at `(-1.9, 3.1, 3.7)` and rotated **-55 deg about X**. The
brief asked for the toe **turned forward**; forward is -Z and the boots shell fills `z < 2.9` for
the whole height of the leg, so a forward toe of any length is swallowed by the boot. The toe kicks
**backward and down** instead. It costs nothing: a spurs piece is read in profile, and an L that
projects away from the leg reads harder than one folded against it. Decide a dangling piece's
direction from the shell box, not from the brief's mental picture - the shell is full-height, so
"forward" and "inward" are often simply unavailable.

**The two warnings in the brief both paid.** `modify_cube {inflate: 0}` in the same call that shaped
the cap, and from then on every clearance line matched the arithmetic to 0.01: a cap ending at
`z 3.95` reported `past boots z+1.05`, and the rotated pad's predicted tip `z 6.59` reported
`z+3.69`. That first cube is worth using as a **probe**: place one face a known distance past the
shell and read the `past <shell>` line before modelling anything, and the whole coordinate mapping
(the leg's x mirror, the +Y flip) is proved in one reply.

**Rotation arithmetic, for the next jointed piece.** About X by theta, offsets from the pivot map
`y' = dy*cos - dz*sin`, `z' = dy*sin + dz*cos`. A **negative** theta swings a cube hanging below the
pivot **backward (+Z)**. Check all four corners of the (dy, dz) rectangle, not just the axis: the
half-thickness contributes `0.75*sin` to the lowest corner, which was the difference between a toe
at `y 1.05` and one poking through the floor.

**Resizing after painting is safe, until a face crosses a texel boundary.** Lengthening the pad from
2.55 to 3.05 grew its four side faces from 3 rows to 4, and the check answered with
`! repaint: faces that were complete and grew: toe[0].east 6/8 ...` - one flat repaint of those four
faces on master and static cleared it. The paint that existed did move with the cube.

**`pixels` land where the sheet layout says, not where you assume.** A 167 highlight aimed at the top
of the foot went onto the sole: `pad.north` is at `20,2` and `pad.south` at `24,2`. Every paint
reply echoes each face's rectangle - read that echo, and place pixels in a call after the face fills,
where the numbers are in front of you.

**A layer split that keeps the fitting meaningful.** Master over **every** face (fur painted at the
palette's luminances, the cap in hardware greys 120-200), `part_static` over the **fur cubes only**,
`part_gemstone` over the **cap only**. So `static + mask = master` exactly - 90 + 10 = 100, overlap 0,
nothing outside the silhouette - which is a stronger proof than "equal opaque counts on master and
static", and it leaves the trim material showing on the cap for a player who fits no gemstone. All
eight palette entries were used and each master value's count equalled its colour's count exactly
(61/18, 83/12, 101/16, 114/24, 125/8, 139/6, 152/4, 167/2).

**Four `-` OVERLAP notes were accepted.** `main` meets `loin_panels:tassets`'s `panel_back` (up to
2.00 x 1.00 x 0.65) and grazes `pelt:tassets`'s `trail` by 0.03. A charm hanging behind the boot
cannot avoid a tasset panel that hangs down the back of the leg to Blockbench `y 5.44, z 3.60`;
clearing it would mean floating the cap 0.7 off the boot, which looks worse than the intersection.
They are notes, not `!`. Any future back-of-boot piece will collect the same lines.

**For the next set pack (Coral, Boss, Nether).**

- One `armorpieces_set_part` with `fittings` + `static: true` creates both sheets; do it before any
  paint call, as every brief says.
- `python tools/check_authoring.py <datapack> <resourcepack>` takes the pack's two folders;
  `tools/check_part.py` still does not see packs.
- The active-tab hazard never fired: `get_project_info` right after `armorpieces_new`, and the
  `[armorpieces] <piece>` prefix on every check line, are enough. Nine other tabs were open, two with
  unsaved edits, and none were touched.
- Animals is now complete at 8/8: armadillo_shell, bee_wings, donkey_tail, flower_brooch, fox_ears,
  frog_mask, turtle_shell, rabbit_feet. Recipe centres spent in this pack: `sweet_berries`,
  `lily_pad`, `honeycomb`, `turtle_helmet`, `poppy`, `lead`, `wolf_armor`, `rabbit_foot`.
