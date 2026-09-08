# Brief: Wing Tatters

A piece of **Armor Pieces: Dragonslayer** (`armorpieces_dragon`), the first pack of the line in
`docs/plans/pack-line.md` — netherite plate with amethyst light, every piece a part of her body.
The pack folder already exists and is empty; you are one of its first four pieces. Skim
`docs/plans/briefs/coral_crown.md`'s **Lessons** section first: it is the most recent pack-external
piece and it says what held.

From the `tassets` row of the Dragonslayer table:

> `wing_tatters` — torn membrane strips hanging from the hips — no fitting — centre `chorus_fruit`.

**Part.** `armorpieces_dragon:wing_tatters`, socket `tassets` only. Display name "Wing Tatters".
**No fittings, no static layer, no effects, no loot.** One sheet — the greyscale master. The pack's
black-and-purple look comes from the armor and its trim, not from this piece's own colour, which is
how the mod's own parts work.

Create it with `armorpieces_new` and **name both pack folders and the namespace explicitly**, or it
will be written into the mod:

    name: wing_tatters
    anchor: tassets
    namespace: armorpieces_dragon
    datapack: C:\Users\Matthijs\ArmorPieces\packs\dragon\datapack
    resourcepack: C:\Users\Matthijs\ArmorPieces\packs\dragon\resourcepack

Then, before painting:

    armorpieces_set_part { name: "Wing Tatters",
                           recipe: { centre: "minecraft:chorus_fruit", craftable: true } }

The reply will say `static_created: false` and `sheets_created: []` — this piece has one sheet and
that is correct. Set the part data before you paint anyway: it is the step that writes the data
half, and doing it in the same order as every other piece keeps the report comparable.

## The rig, in Blockbench coordinates

`tassets` is a **mirrored** socket: model ONE side — the left leg, which is the **negative x** side
in Blockbench — and the game mirrors it.

    left leg box            x -3.9 .. 0.1    y 0 .. 12    z -2 .. 2
    leggings shell (+0.4)   x -4.3 .. 0.5    y -0.4 .. 12.4   z -2.4 .. 2.4
    boots shell (+0.9)      x -4.8 .. 1.0    y -0.9 .. 12.9   z -2.9 .. 2.9
    the tassets anchor      (-1.9, 10, 0)

Front is **negative z**. This is a leggings socket, so the shell you must not touch is the
**leggings** one: its outboard plane is `x = -4.3`. Sit a tenth off it, never on it — a face in that
plane z-fights.

## Shape

Not a plate and not a skirt. What is left of her wing after the fight: four **torn membrane strips**
hanging on the outside of the hip, each a different length, ending ragged rather than square.

- One bone `base` at the anchor (rename the starter `main`; never call a bone `root`).
- **Four strips**, each its own child bone off `base` so it can splay. A strip is a thin plate whose
  broad face points outboard, so it is thin in **x** and spans y and z:
  - front strip — `z -2.3..-1.2`, hanging to about `y 7.6`;
  - second — `z -1.0..0.2`, the longest, hanging to about `y 6.5`;
  - third — `z 0.4..1.5`, hanging to about `y 7.0`;
  - rear strip — `z 1.7..2.4`, the shortest, hanging to about `y 8.2`.
  - All four `x -4.75..-4.45` in the unrotated pose: 0.3 thick, sitting 0.15 clear of the leggings
    shell's `x = -4.3`. All four start at the anchor's height, `y 10`.
- **The tear is geometry, not paint.** Alpha is the silhouette, so a ragged hem means the cubes end
  ragged: give two of the four strips a short second cube beside the first, one texel wide and
  ending half a unit higher, so the hem breaks. Six cubes in total is the budget.
- Splay each bone 5–12° about Z or X, a different amount and not all the same way, so the strips
  hang apart rather than as one slab. Rotate the **bones**, never the cubes, and compute where each
  lands before placing — the reply confirms it to a hundredth.

**Your envelope budget, and it is a hard one.** Stay inside `x -4.9 .. -4.3`, `y 6.4 .. 10.1`,
`z -2.4 .. 2.4`. Three other pieces of this pack are being built against the same leg on the same
budget and none of them may meet you: `dragon_knuckles` stays inboard of `x -3.5`, `dragon_scales`
stops at `y 4.4`, `dragon_talons` stops at `y 3.2`. **Nothing may hang below `y 6.4`** — that is the
line that keeps the tatters off the knee.

**What this socket makes you watch.** `tassets` rides the leg, so the strips swing with it, and a
strip that reaches inboard fouls the other leg on every stride. Keep every cube outboard of
`x -4.3` in the *rotated* pose, not just the unrotated one: a bone leaned about Z swings its bottom
inboard or outboard depending on sign, and on this (left, negative-x) leg a **positive** Z rotation
swings the bottom toward `+x`, i.e. into the leg. The `armorpieces_new` reply lists every other part
on this bone with its envelope in both frames — read it once and say in your report what you cleared
and by how much.

## Sheets

One sheet: `wing_tatters.png`, the **master**, greyscale, its value a position on the wearer's trim
ramp. Alpha is the silhouette and the only source of truth.

Membrane, not plate, and it reads as membrane by its shading rather than its colour: each strip
darker at the hem than at the hip, so the four read as hanging cloth and not as four grey rectangles;
a brighter one-texel row down the leading (front) edge of each strip where the light catches it; the
`down` faces at the hem darkest of all. A ramp of roughly `55 / 85 / 120 / 165 / 215` across
hem-shadow, strip-body-low, strip-body-high, lit-face, edge-highlight is enough; `*.*` for a base
then the faces that differ is the cheap way to leave nothing unpainted. Vary the four strips by a
step or two of grey so they do not read as one sheet of material. Count your paint calls and say
what the face painter did and did not cover.

## Recipe

Centre item `minecraft:chorus_fruit`, paper ring, craftable. Verified unused by any
`template_*.json` in the mod or in any pack. The result is the `tassets` template.

## Done means

`armorpieces_save` accepted **without** `force`;
`python tools/check_authoring.py packs/dragon/datapack packs/dragon/resourcepack` clean; the Lessons
section below filled in.

Two things this piece does **not** do, because it is not the mod's own:
`python tools/check_part.py` does not work for an out-of-pack piece — the bridge's own check,
printed after every reply, is the check here. And do **not** run `python -m modpage build`: this
pack is not on the mod's page, and there is no `modpage.yml` line to add.

## Lessons from the session

Built as: one `base` bone at the tassets anchor (renamed from the starter `main`, starter cube
removed), four child bones (`front_strip`, `second_strip`, `third_strip`, `rear_strip`), each
pivoted at `(-4.6, 10, z_center)` — the top of its strip — holding one or two cubes. Six cubes
total, all `x -4.75..-4.45` or `-4.7..-4.4` (0.3 thick), 0.15/0.1 clear of the leggings shell's
`x -4.3` and 0.15/0.2 clear of the budget's `x -4.9`: `front_main`/`front_ragged` (z -2.3..-1.7 /
-1.7..-1.2, hem y 7.6 / 8.1), `second_main` (z -1.0..0.2, hem y 6.5, the longest, no ragged
partner), `third_main`/`third_ragged` (z 0.4..1.0 / 1.0..1.5, hem y 7.0 / 7.5), `rear_main`
(z 1.7..2.35, hem y 8.2, shortest). The two ragged pairs are adjacent, touching cubes built to the
brief's total z-span for that strip but split so the outer half ends half a unit higher — the hem
reads as torn without any paint trick.

**Rotation axis matters far more than the brief's warning about Z on this leg suggests.** The
brief only worked out the Z-axis trap (positive Z swings the bottom toward +x, into the leg); it
does not mention that X-axis rotation swings the bottom in *z*, and by a much bigger number, since
these strips are long in y (up to 3.5 units) — `length * sin(angle)` moved the tips 0.3-0.7 units
sideways at the 6-12° the brief suggests, which blew straight through the z budget (`front_strip`
at +8° pushed the envelope to z=-2.63, `rear_strip` at -10° pushed it to z=+2.66, both past the
±2.4 wall) on the first attempt. The fix was to work out *per-strip* which rotation direction was
safe (using `Δz' = Δy·sinθ + Δz·cosθ`: for a bone hanging down, `Δy` is large and negative, so the
sign of `sinθ` alone decides whether the hem swings toward the tight boundary or away from it) and
to size the angle to the strip's own margin, not the brief's flat 5-12°: `front_strip -8°`,
`second_strip -9°`, `third_strip +9°`, `rear_strip +7°`, all about X, all confirmed swinging the
tip *away* from the nearest wall. `second_strip`'s rotation also nudged the envelope's top corner
(the part of the top face farthest from the pivot in z) *up* past y=10 — first attempt at -13°
put the ceiling at bb y≈10.14, over the 10.1 budget; dropping to -9° brought it to 10.09. Final
envelope, converted to Blockbench frame from the check's game-frame numbers: `x -4.70..-4.40`
`y 6.45..10.09` `z -2.29..2.35` — inside the brief's box on every axis, margins as small as 0.05
z-inches on two axes. Next time budget the rotation angle from the strip's own length and nearest
wall *before* picking a number, rather than starting from the suggested range and fixing overages
after.

**`!` problems accepted:** none at save time — both COPLANAR flags from the unrotated layout
(`rear_strip`'s z=2.4 face sitting on the leggings shell's own z=2.4 plane, and `second_strip`
sharing the plane `x=2.85`/bb `-4.75` with `garters:knees`'s `garter` cube) were design fixes, not
accepted problems: rear's outer z was pulled in to 2.35, and every cube's x was pulled in by 0.05
(to `-4.7/-4.4` for `second_strip`, though the others only needed it for the earlier COPLANAR and
could have stayed at `-4.75/-4.45`) so no face sits exactly on another shell's or part's plane.
The OVERLAP and `near` hull-test notes against `garters`, `heel_wings`, `boot_cuffs`, `poleyns` and
`winged_cops` (all real mod pieces on the `knees`/`spurs` sockets that a player could wear at the
same time as `tassets`) were left standing as `-` notes: the check itself only requires a decision
on `!` lines, these are advisory ("hull test - check whether the real cubes meet"), and the leg has
so little free volume around the hip that some hull overlap with knee/spur gear was unavoidable at
this shape without shrinking the strips well below the brief's lengths. The three sister pieces
named in the budget (`dragon_knuckles`, `dragon_scales`, `dragon_talons`) — `dragon_knuckles` had
already been built by another session by the time this one saved, and its check never flagged this
piece, so the two pieces of the pack clear each other.

**Paint:** one `armorpieces_paint` call on `part` (the only sheet — no fittings, no static layer),
60 face-writes covering all 36 faces of the 6 cubes: a `*.*` `[top, bottom]` grey pair per strip
(varied a few points per strip — 118/83, 122/87, 115/80, 125/90 — so the four don't read as one
material), then per-cube overrides for `down` (55, the hem-shadow, on every cube's bottom cap, so
even the ragged sub-cubes' higher hems read as torn edges too), `north` (215, the edge-highlight —
this face is exactly one texel wide by construction since the cubes are 0.3 thick in x, so painting
it whole *is* the brief's "one-texel row down the leading edge", no pixel-level work needed) and
`south` (100, a dimmer trailing edge). `up` was repainted to the strip's high value since the
`*.*` pair's top row already put it there but explicit is cheap. The face painter's wildcard/pair
system covered every face in this one call; no `texture op:rects` or pixel work was needed anywhere
on this piece.

**For the next piece of this pack (`dragon_scales` or `dragon_talons`, same `left_leg` bone):**
read the actual rotation-axis math above before picking a splay angle — work out which of X/Z stays
fixed for the axis you're not rotating, then check `length * sin(angent)` against the tightest wall
your strip/plate sits nearest to, in the *direction your chosen sign swings it*, before placing.
Both remaining budgets (`y ≤ 4.4` for scales, `y ≤ 3.2` for talons) sit well below this piece's
floor (`y ≥ 6.45`), so there was no need to check against `wing_tatters` specifically, but the same
hull-test neighbours (`garters`, `heel_wings`, `boot_cuffs`, `poleyns`, `winged_cops`, `padding`)
will show up again lower on the leg.
