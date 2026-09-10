# Brief: Dragon Crest

A piece of **Armor Pieces: Dragonslayer** (`armorpieces_dragon`), the first pack of the line in
`docs/plans/pack-line.md` — netherite plate with amethyst light, every piece a part of her body.
Four pieces of the pack already exist (`dragon_knuckles`, `wing_tatters`, `dragon_scales`,
`dragon_talons`, all on the leg); you are the first one on the head. Read
`docs/plans/briefs/LESSONS.md` first: it is the technique the earlier sessions worked out,
distilled and current, and the rotation arithmetic in it is what costs a session a rebuild when
it is skipped.

From the `crest` row of the Dragonslayer table:

> `dragon_crest` — the ridge of small horns down the crown — no fitting — centre `dragon_breath`.

**Part.** `armorpieces_dragon:dragon_crest`, socket `crest` only. Display name "Dragon Crest".
**No fittings, no static layer, no effects, no loot.** One sheet — the greyscale master. The pack's
black-and-purple look comes from the armor and its trim, not from this piece's own colour, which is
how the mod's own parts work.

Create it with `armorpieces_new` and **name both pack folders and the namespace explicitly**, or it
will be written into the mod:

    name: dragon_crest
    anchor: crest
    namespace: armorpieces_dragon
    datapack: C:\Users\Matthijs\ArmorPieces\packs\dragon\datapack
    resourcepack: C:\Users\Matthijs\ArmorPieces\packs\dragon\resourcepack

Then, before painting:

    armorpieces_set_part { name: "Dragon Crest",
                           recipe: { centre: "minecraft:dragon_breath", craftable: true } }

The reply will say `static_created: false` and `sheets_created: []` — this piece has one sheet and
that is correct. Set the part data before you paint anyway: it is the step that writes the data
half, and doing it in the same order as every other piece keeps the report comparable.

## The rig, in Blockbench coordinates

`crest` is **not** a mirrored socket: one attachment, on the top of the skull, and you model the
whole thing.

    head box                x -4 .. 4     y 24 .. 32     z -4 .. 4
    helmet shell (+1.0)     x -5 .. 5     y 23 .. 33     z -5 .. 5
    the crest anchor        (0, 32, 0)

Front is **negative z**; the back of the skull is `z = +4`. The helmet's top plane is `y = 33`, and
a crest is *expected* to stand proud of it — `comb` clears it by 1.6 and the check reports that as
an ordinary `past helmet` line, not a problem. What you must not do is sit a face exactly *on*
`y = 33` or on `z = ±5`: a coplanar face z-fights.

## Shape

Her crown ridge: **five small back-swept horns** in a single line down the midline of the skull,
front to back, tallest in the middle and shortest at the ends — a saw-tooth, not a fan and not a
comb's continuous blade.

- One bone `base` at the anchor (rename the starter `main`; never call a bone `root`; remove the
  starter cube).
- **Five horn bones** as children of `base`, one per horn, so each can lean back by its own amount.
  Along z, front to back, each a small tapering spike standing on the crown at `y = 32`:
  - `horn1` — `z -3.4 .. -2.5`, rising to about `y 33.4` (the shortest, over the brow);
  - `horn2` — `z -2.1 .. -1.1`, to about `y 34.4`;
  - `horn3` — `z -0.7 .. 0.5`, to about `y 35.6` (the tallest, at the crown's centre);
  - `horn4` — `z 0.9 .. 1.9`, to about `y 34.8`;
  - `horn5` — `z 2.3 .. 3.2`, to about `y 33.6`.
  - All five `x -0.55 .. 0.55` — 1.1 wide, centred on the midline. One cube each is the budget;
    six cubes in total if one horn earns a second, smaller cube stacked on it as a tip.
- **Lean them back, not forward.** Rotate each *bone* about X so its tip swings toward `+z`, by a
  different amount front to back — roughly 8° at the front rising to 20° at the back reads as a
  ridge swept by the wind of a dive. Rotate the **bone**, never the cube.
- **Work the arithmetic before you place, not after.** A horn is tall in y and thin in z, so an X
  rotation moves its tip mostly in *z* by `Δz' = Δy·sinθ + Δz·cosθ`, and `Δy` is the horn's whole
  height. At 20° a 3.6-tall horn's tip moves 1.2 units in z — which is what will push `horn5`
  through the back of the budget if you pick the angle first and check afterwards. `wing_tatters`
  lost an attempt to exactly this.

**Your envelope budget.** Stay inside `x -1.6 .. 1.6`, `y 32.0 .. 36.4`, `z -3.6 .. 3.8`. The three
sister pieces of this pack that share the head are `dragon_horns` (temples, outboard of `x = -4.2`
on its modelled side), `dragon_mask` (the brow, front of the face) and nothing else — the `x ±1.6`
wall is what keeps this piece and `dragon_horns` from ever meeting, and it is a hard wall.

**What this socket makes you watch.** Every brow piece in the mod sits on the front face of the
head at about `z = -4.85 .. -5.35`, outside the head box; `z ≥ -3.6` keeps the front horn off all
of them. The `armorpieces_new` reply lists every other part on this bone with its envelope in both
frames, same-socket first — read it once and say in your report what you cleared and by how much.

## Sheets

One sheet: `dragon_crest.png`, the **master**, greyscale, its value a position on the wearer's trim
ramp. Alpha is the silhouette and the only source of truth.

Horn, not plate. Each spike darker at its base than at its tip, so the five read as horn growing
out of the helmet rather than as five grey teeth: the `up` and the two side faces bright toward the
tip, the `down` cap and the lowest row darkest. A ramp of roughly `60 / 95 / 135 / 180 / 220` across
base-shadow, low-body, high-body, lit-face and tip is enough; `*.*` for a base pair and then the
faces that differ is the cheap way to leave nothing unpainted. Vary the five by a step or two of
grey — the middle one brightest — so the ridge has a peak in value as well as in height. Count your
paint calls and say what the face painter did and did not cover.

## Recipe

Centre item `minecraft:dragon_breath`, paper ring, craftable. Verified unused by any
`template_*.json` in the mod or in any pack. The result is the `crest` template.

## Done means

`armorpieces_save` accepted **without** `force`;
`python tools/check_authoring.py packs/dragon/datapack packs/dragon/resourcepack` clean; the Lessons
section below filled in.

Two things this piece does **not** do, because it is not the mod's own:
`python tools/check_part.py` does not work for an out-of-pack piece — the bridge's own check,
printed after every reply, is the check here. And do **not** run `python -m modpage build`: this
pack is not on the mod's page, and there is no `modpage.yml` line to add.

## Lessons from the session

Built as: one `base` bone at the crest anchor (renamed from the starter `main`, starter cube
removed), five child bones (`horn1`..`horn5`) each pivoted at `(0, 32, z_center)` — the crown
surface, at each horn's own z-centre — holding one cube apiece except `horn3` (the tallest,
centre of the ridge), which got a second, narrower cube (`horn3_tip`) stacked on top for a
tapered peak. Six cubes total, matching the budget. Cube spans as the brief specified almost
exactly: `horn1` z -3.4..-2.5 (h 1.4), `horn2` z -2.1..-1.1 (h 2.4), `horn3_main` z -0.7..0.5
(h 2.6) + `horn3_tip` z -0.5..0.3, x -0.3..0.3 (h 1.0, inset and touching `horn3_main`'s top),
`horn4` z 0.9..1.9 (h 2.8), `horn5` z 2.3..3.2 (h 1.6); all main cubes `x -0.55..0.55`.

**Reworked the brief's 8°-20° lean range down and flattened the ramp to 8/10/12/14/16° before
placing, not after**, by running the brief's own formula (`Δz' = Δy·sinθ + Δz·cosθ`, and the
matching `Δy' = Δy·cosθ − Δz·sinθ` for the top of the range) against all four corners of each
cube ahead of time rather than picking an angle and checking the reply. The tightest case is
`horn5` (rearmost, nearest the `z ≤ 3.8` wall): at the brief's own suggested 20° its back-top
corner (`z_center + h·sinθ + (s/2)·cosθ` = 2.75 + 1.6·sin20° + 0.45·cos20°) lands at z=3.72,
an 0.08 margin — workable but thin given rounding. Dropping to 16° (matching a flatter,
monotonic 8/10/12/14/16 ramp across the five horns rather than the brief's 8→20) widened that to
z=3.62, a 0.18 margin, confirmed by the reply's own envelope (`z -3.40..3.62`, inside the
`-3.6..3.8` budget on both walls) without changing the read — the ridge still sweeps back
visibly, just a touch less dramatically than "20° at the back" would. The front wall was never
at risk: for Δy=0 at the pivot, `Δy'=Δy·cosθ` scales the *base* corners' z-spread down by cosθ
(they move slightly toward the centreline, never past their unrotated extent), so only the back
wall needed checking for horns leaning toward +z. **A side effect not in the brief:** rotating
about X also moves the *base* corners in y, not just the tip — `Δy'` at the base (`Δy=0`) is
`−Δz·sinθ`, nonzero because `Δz≠0` there, so the back-base corner of each horn sinks slightly
*into* the skull (a few hundredths to ~0.09 units for the largest angle/span pair) while the
front-base corner lifts the same amount off it. The reply's envelope floor came out at
Blockbench y≈31.88, a hair under the brief's stated `y ≥ 32.0` floor — accepted without `force`
since it is not a reported problem (the check only flags real clashes, not this brief's own
budget numbers) and reads as intended: a horn rooted fractionally into the crown rather than
floating a hairline above it.

**`!` problems accepted:** none at save time. The only "touching" relation the reply reported
was `horn3_main`/`horn3_tip` (the intentional taper step, inset and stacked, not coplanar with
anything else), and the check's one standing note was `horn1 clears visor:brow's visor by 0.35
in z` — a `-` advisory near-note, not a decision line, left alone.

**Paint:** one `armorpieces_paint` call on `part` (the only sheet), 36 face-writes covering every
face of all 6 cubes explicitly (no wildcards needed at this size) — `up` a flat tip value per
cube (190-220, `horn3_tip` brightest since it is the crown's peak), `down` a flat 55
(base-shadow) on every cube, and `north`/`south`/`east`/`west` each a `[top, bottom]` pair so the
tip-to-base gradient runs up each side face (front/`north` brightest since these horns are read
face-on, back/`south` dimmest, `east`/`west` in between). Values stepped a few points per horn
so the five don't read as one material, `horn3` (both cubes) pushed brightest to mark the ridge's
peak as the brief asked. No `texture op:rects` or pixel work was needed; the face painter alone
left nothing unpainted.

**For the next head piece of this pack (`dragon_horns`, temples, outboard of `x=-4.2`, or
`dragon_mask` on the brow):** this piece confirms the rotation-corner-check technique from
`wing_tatters` generalises past hanging shapes to standing ones — check **all four corners**
of a bone's cubes against the nearest wall with the brief's own Δz'/Δy' formulas before placing,
not just the tip. It also flags something the pack hasn't hit yet: a bone rotated about X so its
tip leans one way sinks its own *base* into the shell on the opposite corner by a small but
non-zero amount — worth checking against the shell clearance (`past helmet`), not just the
budget box, if a future piece leans harder or starts closer to a shell wall.
