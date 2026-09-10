# Brief: Barbute

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the twelfth
batch — six parts rather than the usual four, and the mod's first family that is **flat rather
than cubic**: a faceplate a quarter of a unit thick whose whole character is what has been *cut*
out of it (read `docs/plans/visor-styles.md` first, then `bone_mask.md` for the brow socket and
`nasal.md` for the front-plate trap). **Build this one first.** It is one cube and one cut, the
family's proof, and the other five are specified against it. From `docs/plans/visor-styles.md`:

> **Barbute** - The Italian one: a smooth plate with a T cut through it, no hinge, no relief.
> Opening: a T - an eye band with a slot running down to the mouth. Fitting: `inlay` (border
> round the opening).

**Part.** `armorpieces:barbute`, socket `brow` only, in the mod's own pack (`src/main/resources`,
namespace `armorpieces`), so the master lives in `tools/decoration_masters/barbute.png` and is
installed on save. Display name "Barbute". Fittings: `armorpieces:inlay`, one mask, covering the
border of texels around the opening. **No static layer** — every part in this family stays on the
master so the plate takes the armour's own material. No effects, no loot.

**The frame, which every visor in this family shares.** `brow` is not a mirrored socket: model the
whole thing on the head bone. The head box is x -4..4, y 24..32, z -4..4 (pivot 0, 24, 0); the
helmet shell is that box inflated a full unit, so its front plane is z -5; the anchor is at
Blockbench (0, 28, -4). **The face is empty.** Every part sharing this bone was measured: the
furthest forward any reaches is `brush_crest` at z -3.5, then `feathering` -3.0, `cheek_guards`
-2.4, `comb` -2.1, `horns` and `helm_wings` -2.0, `antlers` -1.7, `head_fins` -1.4 — so anything
in front of z -4 is free at any height and any width, and the clash lines should come back
silent. The other brow parts are never compared: two brow parts are never worn together, so the
shipped `visor` (four cubes, reaching z -7.75) is a **competitor, not an obstacle** — this family
must not repeat its snout. What is left to dodge: the shell plane z -5, the head box's own planes
(x ±4, y 24, y 32 — stay below 32, where `comb`, `spire` and `dorsal_fin` put their bottom face),
and your own cubes.

**Shape.** One bone `mask` pivoted at the anchor (0, 28, -4), one cube `plate`:
**x -4..4, y 24..31, z -5.35..-5.10** — eight wide, seven tall, a quarter thick, a tenth off the
shell, covering the face from the hairline to the jaw. That is the whole model. Integer bounds are
not decoration: box UV lays a cube out at one texel per unit, so this face is exactly 8x7 texels
with its boundaries on the head's own texel grid, and a slot cut on the second row sits exactly
over the skin's eyes.

Two `-` notes are expected and correct: the side faces lie on the head box's x = ±4 plane and the
bottom face on its y = 24 plane — the same notes `bone_mask`'s cheek ridges accepted. Neither can
z-fight, because the plate hangs 1.35 units in front of the head's own front face where those
planes have no geometry. `ruff`, on `collar`, is the one part in the mod that reaches into this
volume (Blockbench y 24.4..26.0, z -7.5..3.5, x ±5.5), so expect overlap or near lines against
the plate's lower rows: a faceplate in front of a ruff is right, a *shared plane* with it is not.

**Sheets.** Rows below are counted from the top of the plate: r1 = y 30..31, r2 = 29..30,
r3 = 28..29, r4 = 27..28, r5 = 26..27, r6 = 25..26, r7 = 24..25. Columns 1..8 across.

**The cut is the part.** On the north face leave unpainted: r2 columns 2..7 — the eye band — and
columns 4..5 of r3, r4 and r5, the slot running down to the mouth. That is the T. An unpainted
texel is *absent*, not transparent, so the player's own face shows through the opening 1.35 units
behind it, which is exactly what a sight is. Also cut the four corner texels so the plate is a
helmet front and not a rectangle.

**One judgment call, and it wants a sentence in the lessons.** A continuous crossbar leaves only
columns 1 and 8 holding r2 together, which is what a real barbute looks like and may still look
absurd at eight texels. If it does, leave columns 4..5 of r2 painted: the T becomes a Y, the
bridge of the nose survives, and that is equally historical. Decide it from the render, not from
the sheet.

Master: steel, 195 at the brow grading to 150 at the jaw (`[top, bottom]` on the north face), a
225 highlight row along r1 where the light catches the skull, and — the detail that sells the
thickness — a **90-value texel bordering every cut edge**, so each opening reads as a hole with a
wall rather than a printed black shape. Rim strips and the south face take a flat 120: a face with
nothing behind it is a `!`, a partly painted face is only a note, and at a quarter texel the rim
strips take whatever texel they land in.

Inlay mask: the border texels around the opening only, at the master's own values. The plate stays
the armour's material and the border dyes — sixteen barbutes off one part.

**Recipe.** Centre item `minecraft:copper_ingot` (a flat item, unused by any template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py barbute`
and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons paragraph below
filled in. Count your paint calls and say what the painter did and did not cover. The family is
resting on two answers from this session: **does a cut opening read as a hole at three metres**,
and **is one cube enough**? Judge from the straight-on shot (`set_camera_angle` position
[0, 28, -24], target [0, 28, 0]) — the three-quarter ([6, 30, -22], target [0, 27.5, 0]) only
shows how thin it is. If either answer is no, say so plainly and stop: the other five briefs get
re-cut before anyone builds them.

**Picture budget: two screenshots, and both after the last paint call.** An image is billed by
area and re-sent on every later turn, so looks taken while painting are paid for many times over;
the leanest sessions on record took every shot after the painting was done.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-05 in 13 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1 `add_group`,
1 `place_cube`, 1 `list_outline`, 2 `remove_element` (starter cube, then its `main` bone), 1
`armorpieces_check`, 2 `armorpieces_set_part`, **2 `armorpieces_paint`** (master, inlay mask), 2
`set_camera_angle`, 1 `armorpieces_save`. No `risky_eval`, no `modify_cube`, nothing hand-edited,
no nudging; the save went through first time **without `force`**. Geometry is exactly the brief's:
one bone `mask` at (0, 28, -4), one cube `plate` x -4..4, y 24..31, z -5.35..-5.10, UV 12,0
8x7x0.25 (north 13,1 8x7; south 22,1 8x7; up 13,0 8x1; down 21,0 8x1; east 12,1 1x7; west 21,1
1x7).

**Both of the family's questions are YES.** A cut opening reads as a hole at three metres - the
player's own skin is plainly visible through the T, a different hue from any trim material, and
the 90-value wall texels make it read as thickness rather than as printed black. And one cube is
enough: the plate, its four rim strips and two cut faces carry the whole part. The other five
briefs can be built as written, with the four corrections below.

**THE correction, and every remaining brief needs it: cut the BACK FACE TOO.** `visor-styles.md`
says "cut inside the front face, and paint the four rim strips and the back". That is wrong and
would have shipped six visors with no holes in them. `armorCutoutNoCull` draws back faces, so a
hole cut only in the north face is filled, from the player's viewpoint, by the *inside* of the
fully painted south face - a recessed grey panel, not an opening. Cut the identical pattern in the
south rectangle (here x 22..29 against the north's 13..20, same rows) and the hole is real. Two
notes for the ones that follow: box UV mirrors the south face left-right, so a **symmetric**
opening needs the same column offsets and nothing more (the T, the Sallet slit, the Bellows slots,
the Savoyard face all qualify), but the **Great Helm's asymmetric breaths must be mirrored** into
the south columns by hand. And where the silhouette itself is nipped - my two bottom corners - also
clear the matching texel on the rim faces (down 21,0 and 28,0; east 12,7; west 21,7), or the corner
is absent from the front and back and still edged in steel from the side. A partly painted face is
only a `-` note, so all of this is free: the finished check reports `down 6/8, east 6/7, north
42/56, west 6/7, south 42/56` and `ok: nothing needs a decision`.

**The recipe centre collided, and the collision the plan did not check for is the FITTING
templates.** `minecraft:copper_ingot` in a paper ring is already `fitting_template_guard.json`'s
grid; the check refused it (`one of the two could never be crafted`). Note *when* it surfaced:
`armorpieces_set_part` accepted the centre silently and the `!` only appeared on the next reply's
check, so read the check after setting a recipe. Barbute ships **`minecraft:raw_copper`** instead -
flat item, unused, keeps the copper flavour. The four fitting templates take `loom` (banner),
`amethyst_block` (gemstone), `copper_ingot` (guard) and `#minecraft:dyes` (inlay); I checked the
family's other five centres against both sets and **`iron_door`, `blaze_rod`, `netherite_ingot`,
`skull_banner_pattern` and `trident` are all still free**.

**One deviation from the brief's cut list: the top two corners stay painted.** Cutting all four
corners *and* running the eye band the full width of columns 2..7 severs the brow: r1's remaining
strip (columns 2..7) would sit directly above six cut texels, with columns 1 and 8 of r2 - its only
supports - cut away above it at r1. The result is a bar floating over the face, touching the plate
only at two diagonals. Cutting just the bottom two corners keeps the T's crossbar held at both ends
(which is what actually holds a real barbute's brow together), and the plate still reads as a jaw
taper rather than a rectangle. General rule for the family: **never cut a corner texel directly
above or below the end column of a full-width opening.** Frog-Mouth, whose slot sits at the very
brow, should read that twice.

**The T stands; no Y was needed.** With the crossbar supported at both ends the six-texel band is
legible as a sight, not as absurd, and the bridge of the nose is not missed - the vertical slot
below it does that job. Judged from the straight-on shot, as instructed. The three-quarter shot
confirms only what the brief predicted: it is very thin, and the lit rim strip on the leading edge
is the whole of what the depth reads as from an angle.

**Two paint calls, and what they did not cover.** Master: 7 face fills (`plate.*` 120, then
`plate.north` [195, 150]) plus 56 pixels - 8 for the 225 brow highlight on r1, 16 for the 90-value
walls, 32 nulls for the cuts on both faces and the rims. Inlay: 16 pixels, the same 16 wall texels
at the master's own 90. Finished sheet: 110 opaque texels, greyscale, range 90..225. What the
painter did **not** do is give the eye band a dark border along its *top* edge: r1 keeps the 225
highlight, because the skin showing through the opening is mid-toned and a bright row above it
separates the hole better than a dark one would - the 90 walls run down the sides and under every
cut instead. The other thing to weigh next time: an inlay mask at a flat 90 is a **dark** dyed
border, and most dyes read poorly that low on the ramp; matching the master keeps the shape honest
when the fitting is absent, but Bellows Visor (whose inlay is the flutes, a much larger region)
should consider 130-150.

**Notes accepted, and one warning that never fired.** Three `-` notes stand, all foreseen: the
plate's x faces on the head box's +/-4 planes and its bottom face on y 24. None can z-fight - the
plate is 1.35 units in front of the head's own front face, where those planes carry no geometry.
`ruff` never appeared anywhere in the report: it is on `collar`, i.e. the **body** bone, and the
check only compares parts sharing a bone, so the brief's "expect overlap or near lines against the
plate's lower rows" is something no tool will tell you. The clash lines against the fifteen
head-bone parts came back `all clear by more than half a unit`, exactly as predicted.

**modpage.** The usual three-step dance: `--offline` warned raw_copper had never been cached and
drew a checkerboard, a plain `python -m modpage build` fetched it, and the third build reported
`unchanged`. `modpage.yml` needed nothing. The remaining warnings (`minecraft:chain`, two
`armorpieces:smithing_skin` recipes) are pre-existing and not this part's.
