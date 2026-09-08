# Brief: Dragon Scales

A piece of **Armor Pieces: Dragonslayer** (`armorpieces_dragon`), the first pack of the line in
`docs/plans/pack-line.md` — netherite plate with amethyst light, every piece a part of her body.
The pack folder already exists and is empty; you are one of its first four pieces. Skim
`docs/plans/briefs/coral_crown.md`'s **Lessons** section first: it is the most recent pack-external
piece and it says what held.

From the `greaves` row of the Dragonslayer table:

> `dragon_scales` — scaled plates up the shins — no fitting — centre `purpur_block`.

**Part.** `armorpieces_dragon:dragon_scales`, socket `greaves` only. Display name "Dragon Scales".
**No fittings, no static layer, no effects, no loot.** One sheet — the greyscale master. The pack's
black-and-purple look comes from the armor and its trim, not from this piece's own colour, which is
how the mod's own parts work.

`greaves` is the **shin** socket on the boots. It is not the hand — that is `vambraces` — and this
piece is never called a greave in its own name.

Create it with `armorpieces_new` and **name both pack folders and the namespace explicitly**, or it
will be written into the mod:

    name: dragon_scales
    anchor: greaves
    namespace: armorpieces_dragon
    datapack: C:\Users\Matthijs\ArmorPieces\packs\dragon\datapack
    resourcepack: C:\Users\Matthijs\ArmorPieces\packs\dragon\resourcepack

Then, before painting:

    armorpieces_set_part { name: "Dragon Scales",
                           recipe: { centre: "minecraft:purpur_block", craftable: true } }

The reply will say `static_created: false` and `sheets_created: []` — this piece has one sheet and
that is correct. Set the part data before you paint anyway: it is the step that writes the data
half, and doing it in the same order as every other piece keeps the report comparable.

## The rig, in Blockbench coordinates

`greaves` is a **mirrored** socket: model ONE side — the left leg, which is the **negative x** side
in Blockbench — and the game mirrors it.

    left leg box            x -3.9 .. 0.1    y 0 .. 12    z -2 .. 2
    leggings shell (+0.4)   x -4.3 .. 0.5    y -0.4 .. 12.4   z -2.4 .. 2.4
    boots shell (+0.9)      x -4.8 .. 1.0    y -0.9 .. 12.9   z -2.9 .. 2.9
    the greaves anchor      (-1.9, 4, -2)

Front is **negative z**. This is a boots socket, so the shell you must not touch is the **boots**
one: its front plane is `z = -2.9`, half a unit further out than the leggings shell. Sit a tenth off
it, never on it — a face in that plane z-fights.

## Shape

Not one plate. Overlapping scale, the way her hide is built: **four plates stacked up the front of
the shin**, each lapping the one below, each leaning a little further out at the top so the stack
follows the leg rather than lying flat on it.

- One bone `base` at the anchor (rename the starter `main`; never call a bone `root`).
- **Four plates**, each its own child bone off `base` so it can lean. In the unrotated pose each is
  a wide, thin cube on the front of the shin, `z -3.3..-3.0` — 0.3 thick, sitting 0.1 clear of the
  boots shell's `z = -2.9`:
  - plate 1, lowest and widest — `x -3.5..-0.3`, `y 0.8..2.0`;
  - plate 2 — `x -3.4..-0.4`, `y 1.8..3.0`;
  - plate 3 — `x -3.3..-0.5`, `y 2.8..3.9`;
  - plate 4, topmost and narrowest — `x -3.2..-0.6`, `y 3.7..4.4`.
  - Each laps the one below by 0.15–0.2 in y. That overlap is the whole point: a gap between two
    plates reads as a mistake, an overlap reads as scale.
- Lean each bone a little further about X than the one below — 3°, 6°, 9°, 12° is plenty — so the
  top edge of each plate lifts away from the shin. Rotate the **bones**, never the cubes, and
  compute where each lands before placing; the reply confirms it to a hundredth, so nothing needs
  nudging.
- A 0.2-unit ridge cube running up the centre of the stack is **not** wanted here: the read comes
  from the four lapped edges, and a spine would fight the talons at the heel.

**Your envelope budget, and it is a hard one.** Stay inside `x -3.6 .. -0.2`, `y 0.7 .. 4.4`,
`z -3.9 .. -2.95`. Three other pieces of this pack are being built against the same leg on the same
budget and none of them may meet you: `dragon_knuckles` starts at `y 4.5`, `wing_tatters` stops at
`y 6.4` and stays outboard of `x -4.3`, `dragon_talons` stays behind `z +1.0`. **Nothing above
`y 4.4`** — that is the line that keeps the scales off the knee.

**What this socket makes you watch.** `greaves` and `knees` sit on the same bone two units apart in
the same plane, so the shipped knee parts are the neighbours to read, not the shipped greaves —
same-socket parts are never worn together and the check ignores them. The `armorpieces_new` reply
lists every other part on this bone with its envelope in both frames; read it once and say in your
report what you cleared and by how much.

## Sheets

One sheet: `dragon_scales.png`, the **master**, greyscale, its value a position on the wearer's trim
ramp. Alpha is the silhouette and the only source of truth.

Hide, not plate, and it reads as hide by the lapping: each plate lighter along its **top** edge where
it catches the light and darkest along its bottom edge where the plate above throws a shadow onto it,
so the four read as overlapping scale and not as a ladder of grey rectangles. The whole stack should
also grade slightly darker toward the ankle. A ramp of roughly `55 / 90 / 130 / 175 / 225` across
lap-shadow, plate-body-low, plate-body-high, lit-face, top-edge-highlight is enough; `*.*` for a base
then the faces that differ is the cheap way to leave nothing unpainted. Read the row coordinates for
the one-texel top edges straight off the check's `sheet layout` block — `west 19,6 6x7` means x
19..24, y 6..12, and the last row is the bottom of the cube in the model. Count your paint calls and
say what the face painter did and did not cover.

## Recipe

Centre item `minecraft:purpur_block`, paper ring, craftable. Verified unused by any
`template_*.json` in the mod or in any pack. The result is the `greaves` template. A block centre is
fine here — the recipe-icon cost in `tools/gen_recipe_icons.py` is a mod-page concern and this pack
is not on the mod's page.

## Done means

`armorpieces_save` accepted **without** `force`;
`python tools/check_authoring.py packs/dragon/datapack packs/dragon/resourcepack` clean; the Lessons
section below filled in.

Two things this piece does **not** do, because it is not the mod's own:
`python tools/check_part.py` does not work for an out-of-pack piece — the bridge's own check,
printed after every reply, is the check here. And do **not** run `python -m modpage build`: this
pack is not on the mod's page, and there is no `modpage.yml` line to add.

## Lessons from the session

Built as: one `base` bone at the greaves anchor (renamed from the starter `main`, starter cube
removed), holding four child bones `plate1`..`plate4`, each with its own cube and its own pivot at
the plate's bottom-back-centre edge (`x` = the plate's own centre, `y` = the plate's bottom, `z =
-3.05`, i.e. 0.15 clear of the boots shell's `z = -2.9`, not the brief's literal `-3.0` — see the
coplanar note below). Each cube built at the brief's exact unrotated box (`z -3.35..-3.05`, 0.3
thick, x/y per plate) then the bone rotated in place about X: `-3°, -6°, -9°, -12°` for
plate1..plate4. Sign convention was not obvious from the brief, so it was checked empirically:
rotating `plate1`'s bone from `0°` to `-3°` moved `past boots z` from `+0.45` to `+0.51` (the plate
reaching further outward, past the boot shell, as intended), confirming negative-about-X tips the
top of a bone sitting in front of its pivot (front is `-z`) further outward — the sign the brief's
"leans further out at the top" calls for on this rig.

**One `!` was hit and designed around, not accepted:** placing the plates at the brief's literal
`z -3.3..-3.0` put their back face exactly on `z = -3`, which is also a face plane of shipped
`anklets:spurs` and `bells:spurs` cubes on this same bone — a `COPLANAR` problem. Nudged the whole
z-range by `-0.05` (`z -3.35..-3.05` instead of `-3.30..-3.00`) before placing any cube; this keeps
the 0.3 thickness and the "0.1 clear of the boots shell" intent (now 0.15 clear) and the coplanar
warning never came back. Worth flagging for the pack's other three greaves-adjacent pieces if they
ever copy this z-range verbatim from this brief rather than from this file.

No other `!` was raised at any point — `armorpieces_save` accepted the piece clean, without
`force`, on the first attempt.

**What was cleared, and by how much (Blockbench frame, this piece's own envelope
`x -1.60..1.60 y 7.62..11.22 z -3.52..-3.05` relative to `base`, i.e. bone-local `x
-3.6..-0.2 y 0.7..4.4 z -3.9..-2.95` in absolute leg space — inside every number the brief's budget
gave):**
- Same-socket `greaves`/`boot_cuffs`/`puttees` — never compared, per the check's own rule.
- The three not-yet-built dragon siblings' reserved bands (`dragon_knuckles` `y ≥ 4.5`,
  `wing_tatters` `y ≥ 6.4` and outboard of `x -4.3`, `dragon_talons` behind `z +1.0`) were never
  approached: this piece tops out at `y 4.4` (plate4's unrotated top; the actual rotated apex is
  `y ≈ 4.39`, per the check, so it never reaches `4.4`) and never goes past `x -3.5` or `z -3.52`.
- The shipped `knees`-socket parts the brief named as the ones to read (`garters`, `knee_studs`,
  `padding`, `poleyns`, `winged_cops`) are genuinely close at the top: the check reports
  `plate4` overlapping `knee_studs`'s two studs by a hull test (`1.00 x 0.48 x 0.44`) and clearing
  `padding`'s pad and `winged_cops`'s cop by only `0.02`–`0.22` in y. This is inherent to the
  brief's own numbers (plate4 top `y 4.4`, `knee_studs` starts `y 3.90` in Blockbench frame) and
  not something this piece can fix without shrinking below the brief's stated box — accepted as a
  note (the check itself only flags it `-`, not `!`) and worth the next `dragon_knuckles` author
  knowing the top of this piece is genuinely snug under the knee.
- Less expected: the check also flagged hull-test `OVERLAP`s between `plate1`/`plate2` (the two
  lowest scales, `y 0.8..3.0`) and shipped `spurs`-socket parts' ankle hardware — `anklets`'s
  `beads`/`ring_high`/`ring_low` and `bells`'s `strap` — because those sit at Blockbench
  `y 0.95..2.20`, squarely inside this piece's lower two plates. The brief only named `knees` as
  the socket to watch; `spurs` turned out to matter too, at the ankle end, for any greaves piece
  whose lowest plate reaches this low. Also a note, not a problem, and also not fixable without
  leaving the brief's given plate-1 box.

**Paint: four calls, one per plate, each `"plateN_scale.*": <mid>` for a base then overrides on
`north` (the outward-facing, visible face — a `[top, bottom]` pair), `up`, `down` and `south` (the
inner face against the boot).** East/west (the thin side slivers) were left on the base value.
Values used the brief's five-step ramp (`55/90/130/175/225`) twice over: once as a per-plate
top/bottom gradient (top brighter, bottom darker, per the brief's literal wording) and again as an
ankle-to-knee grade across the whole stack (plate1's gradient `130→55`, plate2 `175→90`, plate3
`225→130`, plate4 flat `225` — its north face is only 1 texel tall so no gradient fits). All 24
faces across the four cubes ended up painted; the check's unpainted-face count went 24→18→12→6→0
across the four calls, one plate's 6 faces closing per call.

**For the next piece of this pack:** the `armorpieces_new`/`armorpieces_open` reply's envelope
table gives both frames but the "past boots/leggings/body" summary line only tracks this piece's
own reach, not a same-bone neighbour's — read the full per-part table (as above) to find a real
clash, and expect it to flag `spurs`-socket ankle hardware as well as `knees`-socket parts if your
plates reach as low as `y ≈ 1`. Also: do not reuse this brief's literal `z -3.0` boundary verbatim
if you're on the same bone — nudge by a few hundredths first and check for `COPLANAR` before
committing to cube placement, since shipped ankle/spur parts sit exactly on `z = -3`.
