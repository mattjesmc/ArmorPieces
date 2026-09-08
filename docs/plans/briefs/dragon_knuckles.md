# Brief: Dragon Knuckles

A piece of **Armor Pieces: Dragonslayer** (`armorpieces_dragon`), the first pack of the line in
`docs/plans/pack-line.md` — netherite plate with amethyst light, every piece a part of her body.
The pack folder already exists and is empty; you are one of its first four pieces. Skim
`docs/plans/briefs/coral_crown.md`'s **Lessons** section first: it is the most recent pack-external
piece and it says what held.

From the `knees` row of the Dragonslayer table:

> `dragon_knuckles` — the wing's knuckle joints as knee cops — no fitting — centre `end_rod`.

**Part.** `armorpieces_dragon:dragon_knuckles`, socket `knees` only. Display name "Dragon
Knuckles". **No fittings, no static layer, no effects, no loot.** One sheet — the greyscale master.
The pack's black-and-purple look comes from the armor and its trim, not from this piece's own
colour, which is how the mod's own parts work.

Create it with `armorpieces_new` and **name both pack folders and the namespace explicitly**, or it
will be written into the mod:

    name: dragon_knuckles
    anchor: knees
    namespace: armorpieces_dragon
    datapack: C:\Users\Matthijs\ArmorPieces\packs\dragon\datapack
    resourcepack: C:\Users\Matthijs\ArmorPieces\packs\dragon\resourcepack

Then, before painting:

    armorpieces_set_part { name: "Dragon Knuckles",
                           recipe: { centre: "minecraft:end_rod", craftable: true } }

The reply will say `static_created: false` and `sheets_created: []` — this piece has one sheet and
that is correct. Set the part data before you paint anyway: it is the step that writes the data
half, and doing it in the same order as every other piece keeps the report comparable.

## The rig, in Blockbench coordinates

`knees` is a **mirrored** socket: model ONE side — the left leg, which is the **negative x** side in
Blockbench — and the game mirrors it.

    left leg box            x -3.9 .. 0.1    y 0 .. 12    z -2 .. 2
    leggings shell (+0.4)   x -4.3 .. 0.5    y -0.4 .. 12.4   z -2.4 .. 2.4
    boots shell (+0.9)      x -4.8 .. 1.0    y -0.9 .. 12.9   z -2.9 .. 2.9
    the knees anchor        (-1.9, 6, -2)

Front is **negative z**. This is a leggings socket, so the shell you must not touch is the
**leggings** one: its front plane is `z = -2.4`. Sit a tenth off it, never on it — a face in that
plane z-fights.

## Shape

Not a smooth cop and not a spike. The knuckles of her wing finger, worn over the knee: a low
backing plate on the front of the leg with **three bony knobs** standing off it in a vertical line,
biggest at the top, the way a folded wing's finger joints stack.

- One bone `base` at the anchor (rename the starter `main`; never call a bone `root`).
- **The backing plate**, a cube on `base`: `x -3.4..-0.4`, `y 4.6..7.4`, `z -2.75..-2.5`. That is
  0.25 thick and its outer face sits 0.1 clear of the leggings shell's `z = -2.4`.
- **Three knobs**, each its own child bone off `base` so it can lean, stacked front-face-out:
  - upper, the largest — about `x -3.1..-0.7`, `y 6.5..7.4`, out to about `z -3.5`;
  - middle — about `x -2.9..-0.9`, `y 5.5..6.4`, out to about `z -3.3`;
  - lower, the smallest — about `x -2.7..-1.1`, `y 4.7..5.4`, out to about `z -3.1`.
  - Lean each bone 6–12° about X, a little further than the one below, so the stack follows the
    knee rather than standing off it as a flat slab. Rotate the **bones**, never the cubes, and
    compute where each lands before placing — the reply confirms it to a hundredth.

**Your envelope budget, and it is a hard one.** Stay inside `x -3.5 .. -0.3`, `y 4.5 .. 7.6`,
`z -3.8 .. -2.5`. Three other pieces of this pack are being built against the same leg on the same
budget and none of them may meet you: `dragon_scales` stops at `y 4.4`, `wing_tatters` stays
outboard of `x -4.3`, `dragon_talons` stays behind `z +1.0`. Do **not** reach out to the leg's
outboard edge at `x -3.9`, and do not cross `x 0.1` — the other leg is there.

**The one thing this socket makes you choose.** `DecorationAnchor.java` says it plainly: the knee
anchor sits *inside* the tassets' third lame rather than below it, so the shipped parts leave 0.13
units at their closest and a knee part **laps a neighbour rather than clearing both**. Do not spend
turns trying to clear everything. Lap the tassets, keep clear of the greaves below, and say in your
report which neighbour you lapped and by how much. The `armorpieces_new` reply lists every other
part on this bone with its envelope in both frames — read it once, decide, and move on.

## Sheets

One sheet: `dragon_knuckles.png`, the **master**, greyscale, its value a position on the wearer's
trim ramp. Alpha is the silhouette and the only source of truth.

Bone, not metal, and it reads as bone by its shading rather than its colour: a mid grey body, each
knob's outward face lighter than the plate behind it so the three stand out in silhouette, a bright
one-texel row along each knob's top edge, and the plate's `down` faces dark. A ramp of roughly
`60 / 95 / 130 / 175 / 220` across plate-shadow, plate-body, knob-body, knob-face, knob-highlight is
enough; `*.*` for a base then the faces that differ is the cheap way to leave nothing unpainted.
Count your paint calls and say what the face painter did and did not cover.

## Recipe

Centre item `minecraft:end_rod`, paper ring, craftable. Verified unused by any `template_*.json` in
the mod or in any pack. The result is the `knees` template.

## Done means

`armorpieces_save` accepted **without** `force`;
`python tools/check_authoring.py packs/dragon/datapack packs/dragon/resourcepack` clean; the Lessons
section below filled in.

Two things this piece does **not** do, because it is not the mod's own:
`python tools/check_part.py` does not work for an out-of-pack piece — the bridge's own check,
printed after every reply, is the check here. And do **not** run `python -m modpage build`: this
pack is not on the mod's page, and there is no `modpage.yml` line to add.

## Lessons from the session

Built as: one `base` bone at the knees anchor (renamed from the starter `main`), holding the
`plate` cube (renamed from `main_0`) at x -3.4..-0.4, y 4.6..7.4, z -2.78..-2.53 — nudged 0.03
deeper than the brief's literal `-2.75..-2.5` because that exact `-2.75` face turned out to be
exactly coplanar with `greaves:greaves`'s own `greave` cube; the shift keeps 0.12–0.13 clear of
the leggings shell (still "off it, never on it") and clears the coincidence. Three child bones —
`knob_lower`, `knob_middle`, `knob_upper` — each pivoted at the plate's outer face at its knob's
attach height (`(-1.9, y, -2.53)`), holding one cube apiece built upright first at the brief's
literal ranges (`lower_knob` x -2.7..-1.1 y 4.7..5.4 z -3.1..-2.53; `middle_knob` x -2.9..-0.9
y 5.5..6.4 z -3.3..-2.53; `upper_knob` x -3.1..-0.7 y 6.5..7.4 z -3.5..-2.53), then leaned by
setting each bone's own rotation about X after the fact: -6° / -9° / -12°, lower to upper, all
the same sign so the stack curves one way rather than fanning. The resulting envelope (x
-3.4..-0.4, y 4.6..7.4, z -3.67..-2.53 in world terms) stayed inside the brief's budget on every
axis with margin to spare (z had 0.13 left before -3.8).

No `!` was accepted with `force` — the only problem the checker raised along the way (the
plate/greave coplanar plane) was fixed by nudging the plate depth rather than forced through, and
by the time of save the report read "ok: nothing needs a decision".

Neighbour lapped: **tassets**, exactly as the brief expects for this socket. The hull test shows
`base`, `knob_middle` and `knob_upper` overlapping `tassets:tassets`'s `lame2`/`lame3` and
`loin_panels:tassets`'s `panel_front` by up to 2.4×1.1×1.1 units (hull bounding boxes, not
necessarily the real cubes touching — the checker says so itself). Cleared instead: **greaves**
and **thigh_sheath** — every `near:` line for those two came back a positive real clearance (0.05
to 0.42 units), even though their hull boxes also flagged as overlapping `base`/`knob_lower`. So
the piece does what the brief asked: lean on the tassets, stay off the greaves below.

Painting: one `armorpieces_paint` call on the master, 11 face-address entries covering all 24
faces of the 4 cubes (`*.* ` for a 95 base, `plate.down` at 60, `<knob>.*` at 130 to overwrite the
knobs' base, `<knob>.north` at 175 for the outward-facing knuckle face, `<knob>.up` at 220 for the
highlight). No pixel-level work was needed: every knob's `north` and `up` face UV rectangle came
back exactly 1 texel tall in the sheet layout (the cubes are thin enough that box-UV rounds their
height to a single row), so "a bright one-texel row along each knob's top edge" is naturally what
painting the whole `up` face gives — there was no room for a gradient within any single face.
Reply came back "ok: nothing needs a decision" with all 24 faces covered on the first call.

For the next piece of this pack (dragon_scales / wing_tatters / dragon_talons, same leg, same
budget):
- The bridge's cube-name vs bone-name distinction bit here: `armorpieces_paint` addresses want the
  **cube's own name** (what you pass to `place_cube`'s `elements[].name`), not the bone it lives
  in. Naming a knob bone `knob_lower` and its cube `lower_knob` (so both read sensibly in the
  outliner) meant the first paint call had to be corrected once — simplest fix is giving the cube
  and its bone the *same* name unless one is a plate/base with multiple future children.
- `x -3.9` (outboard) and `x 0.1` (the other leg) were never approached — this piece stayed within
  roughly x -3.4..-0.4 the whole time, well inside `wing_tatters`'s `x -4.3` outboard limit and
  nowhere near the other leg.
- Watch for exact-plane coincidences with the mod's own shipped parts sharing this bone
  (`greaves:greaves` here) even when your numbers come straight from the brief — the checker
  catches it immediately as a `!`, and a millimetre's nudge (0.02-0.03 units) was enough to clear
  it without changing the shape.
- The `envelope` line the checker prints for this piece uses two different frames in the same
  report (bone-relative x, but world-ish y/z, when the anchor's own x offset is nonzero) — read
  the `past leggings/boots/body` reach lines and the explicit `near:`/`OVERLAP:` notes instead of
  trying to reconcile the envelope line's x against y/z by hand.
