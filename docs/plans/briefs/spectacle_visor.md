# Brief: Spectacle Visor

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus. The seventh and
last of the flat visor family — read `docs/plans/visor-styles.md` first; the six before it
(`barbute`, `sallet_slit`, `bellows_visor`, `great_helm`, `savoyard`, `frog_mouth`) are all built
and clean, and their briefs' Lessons sections are the accumulated record. From the closing verdict
of `visor-styles.md`, written by the Frog-Mouth session:

> The **spectacle visor** is worth building, for a reason this plan did not have: a *brille* is a
> hole cut through the **raised** part, and all six of these cut the plate and never the band. A
> cut proud cube is the last genuinely new mechanism flat plates have.

**That is the whole point of this part.** Everything else here is deliberately plain, so that what
the session learns is about the mechanism and nothing else.

**Part.** `armorpieces:spectacle_visor`, socket `brow` only, in the mod's own pack
(`src/main/resources`, namespace `armorpieces`), so the master lives in
`tools/decoration_masters/spectacle_visor.png` and is installed on save. Display name "Spectacle
Visor". Fittings: `armorpieces:guard`, one mask, covering the brille bar only — the plate stays the
helmet's material and the reinforce takes a second metal, which is what a brille is. No static
layer, no effects, no loot.

**The frame, which every visor in this family shares.** `brow` is not a mirrored socket: model the
whole thing on the head bone. The head box is x -4..4, y 24..32, z -4..4 (pivot 0, 24, 0); the
helmet shell is that box inflated a full unit, so its front plane is z -5; the anchor is at
Blockbench (0, 28, -4). **The face is empty.** Every part sharing this bone was measured: the
furthest forward any reaches is `brush_crest` at z -3.5, then `feathering` -3.0, `cheek_guards`
-2.4, `comb` -2.1, `horns` and `helm_wings` -2.0, `antlers` -1.7, `head_fins` -1.4 — so anything in
front of z -4 is free at any height and any width, and the clash lines should come back silent. The
other brow parts are never compared: two brow parts are never worn together. What is left to dodge:
the shell plane z -5, the head box's own planes (x ±4, y 24, y 32 — stay below 32, where `comb`,
`spire` and `dorsal_fin` put their bottom face), and your own cubes.

**Shape.** Two bones. `mask` pivoted at the anchor (0, 28, -4) with a `plate`
**x -4..4, y 24..31, z -5.35..-5.10** — the family's full faceplate, eight wide, seven tall, a
quarter thick. Then `brille`, a child bone, with a bar **x -4..4, y 28..30, z -5.60..-5.30** — full
width, two tall, 0.30 thick, proud of the plate and covering its rows r2 and r3.

The bar sits 0.05 *inside* the plate's front face and shares no plane with it. The checker will say
nothing about this — see the corrections below — so the stagger is yours to hold.

Plate rows from the top: r1 = y 30..31, **r2 = 29..30 (behind the bar)**, **r3 = 28..29 (behind the
bar)**, r4 = 27..28, r5 = 26..27, r6 = 25..26, r7 = 24..25. Columns 1..8 across. The bar's own north
face is 8x2: its upper row is plate r2, its lower row is plate r3.

**The cut, and the reason this part exists.** Two spectacle eyes, **columns 2..3 and columns 6..7**,
on the **bar's lower row** (y 28..29). Every other part in this family cut a plate; this one cuts
through a raised cube, and that means **four rectangles, not two**: `bar.north`, `bar.south`,
`plate.north` and `plate.south`, all at the same columns and the same row. Cut the bar alone and
you will see the *plate* through the holes, 0.25 behind — a recessed grey panel where a sight
should be. Cut the plate alone and the bar plugs them. This is the north/south rule from Barbute
applied twice over, and it is the thing to report on.

One judgment call that no earlier session has faced: the bar's **`down` face** is a full-width strip
at y = 28, and the eye openings sit directly on top of it. It is a floor, not an obstruction — you
look through the holes along -z, not downward — so the expectation is that it stays painted and
costs nothing. Check it in the render. If it does read as a sill blocking the openings, clear the
two pairs of texels above the cut columns and say so, because that is a rule the family does not yet
have.

Silhouette: cut the plate's **two bottom corner texels** only. Do not cut the top pair — r1 is a
one-row brow strip above the bar and the corner rule below applies to it.

**Sheets.** Master: the plate 175 at r1 falling to 130 at r7 (`[top, bottom]` on the north face);
the bar clearly **outside** that range, north `[235, 205]`, `up` 250, `down` 120 — the lit top strip
is the only thing the depth reads as from an angle, and the dark underside is what makes it an
overhang rather than a gap. A 90-value jamb texel on the bar's lower row at columns 1, 4, 5 and 8 —
the material that survives between and beside the two eyes — which is what gives each opening a
wall. Rim strips and the surviving south texels take a flat 125 so no face is empty.

Guard mask: the bar's faces at the master's own values, with `down` kept at or above 120 so the
second metal does not dye near-black, and repeating every one of the bar's cuts.

**What the six sessions before you established. All of it is load-bearing; none of it is optional.**

1. **Cut the south face too, in the same pattern.** `armorCutoutNoCull` draws back faces, so an
   opening cut only in the north face is filled by the *inside* of the painted south face and stops
   being a hole. Here it applies to the bar *and* the plate — four rectangles. Where the silhouette
   is nipped, clear the matching rim texels as well.
2. **The hole is the skin, not the gap.** What makes a cut read as a hole is not its size but the
   player's own skin behind it, in a warm hue no trim material produces, plus a dark jamb beside it
   for depth. At eye height the cut shows the skin's own eye texel — sclera and iris — which is why
   an opening at this height reads best of all. Keep the jamb.
3. **The checker is completely silent about a part's own cubes.** Not just coplanarity: Great Helm's
   two crossing bands drew no line at all. Your 0.05 stagger is unverifiable by tool.
4. **Nothing verifies that a cut landed where you meant it.** A partly-painted face is only a note,
   so the report reads identically whether the eyes are on the right row or one row off. Dump the
   saved master with Pillow and confirm the texels — north, south, and both cubes — before you call
   it done. On this part that check matters more than on any other, because a misaligned pair of
   cuts between bar and plate is exactly the failure mode.
5. **Never cut a corner texel directly above or below the end column of a full-width opening** —
   the ban is about adjacency to the plate's own *edge row*, not the opening's column span.
6. **`armorpieces_paint` can do the whole sheet in one call**: it applies `faces` then `pixels`, and
   `pixels` accepts `null`, so the gradient, the grey detail *and the cuts* go in one call. No part
   in this family needed the shape, brush or eraser tools. Two paint calls total is the target.
7. **A wall texel painted on a row a proud cube covers is invisible** — it is buried 0.25 deep.
8. **`ruff` will never appear in your check.** It is on the `collar` bone and no tool compares across
   bones. It reaches Blockbench y 24.4..26.0, z -7.5..3.5: your plate is in front of it, sharing no
   plane, which is fine.
9. **The starter cube is `main_0`, not `main[0]`** — the check's `bone[i]` label is a paint address,
   not an element id.
10. **Recipe centres live in three sets**: 87 `template_*.json`, four `fitting_template_*.json` and
    fourteen `skin_template_*.json`. `minecraft:spyglass` has been checked against all three and is
    free.

**Recipe.** Centre item `minecraft:spyglass` (a flat item, free of all three template sets, and the
only optical instrument in the game), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
spectacle_visor` clean; the mod page rebuilt. Note that `check_authoring.py` currently reports one
**pre-existing** collision — `template_puttees.json` against the untracked `cloth_template_tunic.json`,
from a different line of work — which is **not yours to fix**: confirm it is the only line it
reports and leave it alone.

Fill in the Lessons section below and give a short final report. The family wants one answer from
you: **does cutting through a raised cube work, and what did it cost?** How many rectangles, whether
the bar's `down` face had to be cleared, and whether a hole through a proud cube reads better or
worse than the same hole through a flat plate. If it does not work, say so plainly — the family is
complete at six and this part can be dropped without loss.

**Picture budget: two screenshots, and both after the last paint call.** An image is billed by area
and re-sent on every later turn. Straight on (`set_camera_angle` position [0, 28, -24], target
[0, 28, 0]) and one three-quarter ([6, 30, -22], target [0, 27.5, 0]) for the bar's step.

## Lessons from the session

**Cutting through a raised cube works, and it costs exactly four rectangles and nothing else.**
The brief's prediction was right to the texel: `bar.north`, `bar.south`, `plate.north`,
`plate.south`, all at columns 2..3 and 6..7, the bar's cuts on its lower row and the plate's on r3.
All four go in the same `pixels` list of the same `armorpieces_paint` call as the shading, so a cut
proud cube is not a second paint call and not a second mechanism — it is the Barbute north/south
rule written twice. Two paint calls total, as for the six before. The one new discipline is
*bookkeeping*: two cubes means two UV islands and four rectangles whose columns must agree, and the
only reason the columns agreed here is that the pattern is symmetric about the centre line, so the
north/south mirror of box UV could be ignored. **An asymmetric cut through a proud cube would need
the mirror worked out on four faces, not two** — that is the real cost, and it is the thing to
budget for if anyone repeats this.

**A hole through a proud cube reads *better* than the same hole through a flat plate**, and for a
reason the flat six could not get at: the bar's lit `up` face (250) sits one texel above the
openings and its dark `down` face (120) one texel below, so each eye has a bright brow over it and a
shadow under it before any jamb is painted. On a flat plate the only depth cue is the 90-value jamb
beside the opening; here there are three cues around every eye, and at three metres the pair reads
as *set into* something rather than punched out of a sheet. The step is what makes it a brille.

**The bar's `down` face did not have to be cleared.** It is a floor, not a sill: you look through
the openings along -z and the strip is edge-on to that line of sight. In the three-quarter render it
appears as exactly what it should be, a dark line of shadow under the eyes; straight on it is
invisible. Left painted at 120. The family does not need a new rule — **a full-width strip directly
beneath an opening is free as long as it is a `down` face**, because a `down` face is never in the
line of sight of a -z cut.

**The 0.05 stagger is still unverifiable and still correct to hold.** Bar front -5.60, plate front
-5.35, bar back -5.30, plate back -5.10: the bar's south face is 0.05 in front of the plate's north
face and no plane is shared. The checker said nothing about either cube, exactly as lessons 3 and 7
predicted, and the two buried plate rows (r2, r3) came back only as `50/56` partly-painted notes.

**Verifying with Pillow is worth more here than anywhere in the family.** Dumping the saved master
as four aligned rows — bar north/south, plate north/south — makes a one-row misalignment between
bar and plate obvious in a way no check output can, and it is a five-second read. That dump is the
artefact this part should be remembered by; the check block was `ok: nothing needs a decision` from
the first paint call onward and would have said the same with the eyes a row too high.

**Housekeeping.** `minecraft:spyglass` was free of all three template sets, as the brief said, but
it had **never been cached by `modpage`**: `--offline` drew it as missing-texture, and one build
*without* `--offline` fixed it permanently. Any part whose centre item is new to the mod needs that
online build. And `check_authoring.py` came back **completely clean** — the `template_puttees` /
`cloth_template_tunic` collision the brief warned about no longer reports at all, so there was
nothing to leave alone.

**The family is complete at seven.** The mechanism worked, so the closing verdict of
`visor-styles.md` holds unchanged: what remains for this socket is fittings (a north-facing
`banner`), not parts.
