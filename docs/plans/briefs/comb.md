# Brief: Comb

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the seventh
batch of four, a Knightly set (skim spire.md, dorsal_fin.md and aerials.md for the crest and
head frame). From the `crest` row of `docs/plans/part-variety.md`:

> **Comb** - A low fluted ridge running front to back, hugging the skull - the burgonet answer
> to the brush's height. Theme: Knightly. Fitting: `guard`.

**Part.** `armorpieces:comb`, socket `crest` only, in the mod's own pack. Display name "Comb".
Fittings: `armorpieces:guard`, one mask, covering the whole comb. No effects, no loot, no static
layer.

**Shape.** `crest` is not a mirrored socket: model the whole thing on the midline x = 0, on the
head bone. The head box is x -4..4, y 24..32, z -4..4 (pivot 0, 24, 0); the helmet shell is
that box inflated a full unit, so its top plane is y 33 and its front z -5; the anchor is at
Blockbench (0, 32, 0). Read the envelopes in the `armorpieces_new` reply: the other crest parts
are never compared, but the brow parts share the bone and `coronet` reaches y 33.21 forward of
z -2.25 (x ±6), so a ridge that runs to the front of the skull at y 32.5..34 would share its
volume and possibly its planes - either start the ridge at z -2.1 (a comb from the crown back)
or keep its base above y 33.3 in front of z -2.25; say which. Build a `comb` bone at the anchor
with three cubes: the ridge x -0.75..0.75, y 32.5..34.0, z -2.1..4.4 (base half a unit inside
the shell, like the spire's plate); a crown strip on top of it x -0.4..0.4, y 34.0..34.6,
z -1.9..4.2 (a tenth in from the ridge's ends, no shared end planes); and a tail block where
the comb meets the back of the skull, x -0.6..0.6, y 32.5..33.6, z 4.4..5.6 (a tenth past the
shell's back plane z 5 is buried; that is fine). The fluting is paint: alternating light and
dark texel columns along the ridge's two long side faces. Nothing above y 34.6 and nothing
wider than x ±0.75.

**Sheets.** Master: ridge mid-light `[top, bottom]` lighter at the top, with the flutes as
alternating columns (`pixels`) every other texel along both side faces about 35 values apart;
crown strip bright with a brightest top face; tail block a step darker. Guard mask: every face,
shaded like the master, flutes included.

**Recipe.** Centre item `minecraft:iron_helmet` (a flat item, unused by any template), paper
ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py comb`
and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons paragraph below
filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-03 in 17 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1 `add_group`,
3 `place_cube`, 1 `list_outline`, 2 `remove_element`, 1 `armorpieces_check`, 1
`armorpieces_set_part`, **2 `armorpieces_paint`**, 2 `set_camera_angle`, 1 `armorpieces_save`.
No `risky_eval`, no `modify_cube`, no nudging, nothing hand-edited; the save went through first
time without `force`.

**What I built.** One bone, `comb`, pivot Blockbench (0, 32.5, 0), unrotated, with the brief's
three cubes exactly as specified: `ridge` x -0.75..0.75, y 32.5..34.0, z -2.1..4.4; `crown`
x -0.4..0.4, y 34.0..34.6, z -1.9..4.2; `tail` x -0.6..0.6, y 32.5..33.6, z 4.4..5.6. Envelope
x -0.75..0.75, Blockbench y 32.50..34.60, z -2.10..5.60, reach 5.85. Data: `crest` only, fitting
`armorpieces:guard`, no effects, loot or static layer; recipe `minecraft:iron_helmet` in a paper
ring (no collision - the bridge and `check_authoring.py` both accepted it, and `modpage build
--offline` had the item texture cached already, so no plain build was needed).

**Which of the brief's two options I took: the comb starts at the crown, z -2.1.** That is 0.15
behind `coronet`'s back plane (z -2.25), so nothing of this part is ever in the brow parts'
volume and the base can stay low at y 32.5, half a unit inside the helmet shell (the `spire`
trick - the bottom face is buried, so no COPLANAR and no seam). The check confirms **"all clear
by more than half a unit"** from all eleven parts on the head bone.

**`!` lines accepted: none.** The finished check is `ok: nothing needs a decision` with zero
notes. The only `!` that ever appeared was the standard "N/N faces have no paint behind them"
while the sheet was blank, and the `-` note "master: every pixel is transparent" that goes with
it. The tail's back tenth (z 5.0..5.6) sticks out past the helmet shell's z 5 by design and the
part of it inside is simply buried - the check says nothing about it either way, and its faces
are painted anyway.

**Two `armorpieces_paint` calls, and they covered everything.** One per sheet, identical maps:
`*.*` 120 as a base, then `ridge` sides `[165,120]`, ends `[150,110]`, up 190, down 70; `crown`
205 flat with sides `[220,190]`, up 240, down 120; `tail` `[130,95]` with up 150, down 60, south
105 - then the fluting as a 12-entry `pixels` list. 43 faces + 12 pixels each time, 0 unpainted
faces after the first call, 118 opaque texels on each sheet, all greyscale, 60..240 (Pillow).
What the painter did **not** cover: the flutes. `armorpieces_paint` has no column pattern, so
alternating texel columns are hand-listed pixels - the ridge's long side faces are `east` 12,7
7x2 and `west` 21,7 7x2, and darkening columns 13/15/17 and 22/24/26 by 35 (165->130 top,
120->85 bottom) is the whole fluting effect, twelve pixels. It reads clearly from three metres
in the screenshot. Note that a 1.5-tall cube gives side faces only **two** texel rows, so a
`[top, bottom]` pair on the ridge is literally one light row over one dark row; on `crown`
(0.6 tall) the side faces are a single row and the pair collapses to its top value.

**What the next part should know.**
- The guard mask is the master repeated verbatim (the brief asked for the whole comb to take the
  fitting), so the same `faces`+`pixels` payload went to `part_guard` unchanged - one edit of the
  values means editing both calls. Set the part data *before* painting: `armorpieces_set_part`
  reported `sheets_created: ["part_guard"]` on the spot.
- `remove_element` cannot find the starter cube by the check's label `main[0]`; `list_outline`
  shows its real name is **`main_0`**, and that works. The group `main` then removes by name.
- `minecraft:iron_helmet` is now taken as a template centre item.
- A crest that hugs the skull (top y 34.6) is the shortest thing on the socket by a wide margin
  - spire 40, feathering 44.18, brush_crest 39, dorsal_fin 36.43 - which is the point of a comb,
  but it also means the silhouette rests entirely on the crown strip's brightness and the flutes.
  Do not shade a low part flat.
