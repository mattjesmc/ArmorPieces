# Brief: Dragon Horns

A piece of **Armor Pieces: Dragonslayer** (`armorpieces_dragon`), the first pack of the line in
`docs/plans/pack-line.md` — netherite plate with amethyst light, every piece a part of her body.
Four pieces of the pack already exist, all on the leg (`dragon_knuckles`, `wing_tatters`,
`dragon_scales`, `dragon_talons`); you are on the head. Read
`docs/plans/briefs/LESSONS.md` first: it is the technique the earlier sessions worked out,
distilled and current, and the rotation arithmetic in it is what costs a session a rebuild when
it is skipped.

From the `horns` row of the Dragonslayer table:

> `dragon_horns` — the two long back-swept head horns — no fitting.

**Part.** `armorpieces_dragon:dragon_horns`, socket `horns` only. Display name "Dragon Horns".
**No fittings, no static layer, no effects, no loot.** One sheet — the greyscale master. The pack's
black-and-purple look comes from the armor and its trim, not from this piece's own colour, which is
how the mod's own parts work.

Create it with `armorpieces_new` and **name both pack folders and the namespace explicitly**, or it
will be written into the mod:

    name: dragon_horns
    anchor: horns
    namespace: armorpieces_dragon
    datapack: C:\Users\Matthijs\ArmorPieces\packs\dragon\datapack
    resourcepack: C:\Users\Matthijs\ArmorPieces\packs\dragon\resourcepack

Then, before painting:

    armorpieces_set_part { name: "Dragon Horns",
                           recipe: { centre: "minecraft:ender_pearl", craftable: true } }

The reply will say `static_created: false` and `sheets_created: []` — this piece has one sheet and
that is correct. Set the part data before you paint anyway: it is the step that writes the data
half, and doing it in the same order as every other piece keeps the report comparable.

## The rig, in Blockbench coordinates

`horns` is a **mirrored** socket on the temples: model ONE side — the **negative x** side in
Blockbench — and the game mirrors it.

    head box                x -4 .. 4     y 24 .. 32     z -4 .. 4
    helmet shell (+1.0)     x -5 .. 5     y 23 .. 33     z -5 .. 5
    the horns anchor        (-4, 29, 0)

Front is **negative z**; the back of the skull is `z = +4`. The anchor sits exactly on the head
box's side face, so your first cube starts *inside* the helmet shell and comes out of it — which is
right, and is what the mod's own `horns` does (its check says `boss's x face at 4 lies on the body
surface` as an ordinary note). What is not right is a face sitting exactly on `x = -5`, `y = 33` or
`z = ±5`: a face in the shell's plane z-fights. Cross the shell, do not lie on it.

## Shape

Her head horns: **one long horn per temple, swept up and back** in three tapering segments, off a
small boss where it leaves the skull. Long and clean, not branched — `antlers` is the branched
piece and this is deliberately not that.

- One bone `base` at the anchor (rename the starter `main`; never call a bone `root`; remove the
  starter cube).
- **A boss**, one cube in `base`, where the horn leaves the temple: about `x -5.6 .. -4.0`,
  `y 28.2 .. 30.2`, `z -1.0 .. 1.0`. It starts inboard of the shell so no gap opens when the head
  turns.
- **Three segments**, each its own bone, each a child of the one before it, each shorter and
  thinner than the last — so the horn tapers and each joint can add a little more sweep:
  - `horn1` off the boss, the thickest, heading up and outboard;
  - `horn2` off `horn1`, thinner, turning back;
  - `horn3` off `horn2`, thinnest, ending in a point at the back.
  - Four cubes in total is the budget; five if the tip earns its own small cube.
- **Build it straight, then aim it.** Place each segment unrotated along one axis, look at it, and
  then set the bone's rotation with `element set {rotation}` — this plugin can re-aim a bone after
  the fact, which is why precomputing a chain of sines by hand is the wrong way to do it and was
  called "the backbone of the whole session" by the last piece that used it.
- **The two signs, worked out once.** Sweeping **back** is a rotation about **X**: a segment
  pointing up has `Δy` large and positive, and `Δz' = Δy·sinθ + Δz·cosθ`, so a **positive** θ about
  X swings the tip toward `+z`, which is backward. Sweeping **outboard** is a rotation about **Z**:
  `Δx' = Δx·cosθ − Δy·sinθ`, so a **positive** θ about Z swings an upward-pointing tip toward `−x`,
  which on this side is outboard. Both signs are positive; get one wrong and the horn goes into the
  wearer's face or into their ear.

**Your envelope budget, and one wall of it is a hard number.** Stay inside `x -8.9 .. -4.1`,
`y 28.4 .. 37.6`, `z -1.6 .. 7.4`. This is a mirrored socket, so **the pair spans `2 × |x|` across
the figure**, and the check compares that against the 18 the shoulders span: at `x = -8.9` the pair
spans 17.8 and stays inside it, as the mod's own `horns` does at 17.93. Going one unit further out
puts the pair over the shoulders, which the check reports and which looks wrong on a walking
figure. Say your span in your report.

**What this socket makes you watch.** `dragon_crest` is the sister piece of this pack on the same
bone and it is built against `x -1.6 .. 1.6` — your `x ≤ -4.1` wall is what keeps the two from ever
meeting, and it has 2.5 units of slack, so do not spend it. `dragon_mask` will take the brow, on
the front of the face at about `z ≤ -4.8`, which your `z ≥ -1.6` clears with room. The
`armorpieces_new` reply lists every other part on this bone with its envelope in both frames,
same-socket first — read it once and say in your report what you cleared and by how much.

## Sheets

One sheet: `dragon_horns.png`, the **master**, greyscale, its value a position on the wearer's trim
ramp. Alpha is the silhouette and the only source of truth.

Horn, and a long one, so the eye needs the taper told in value as well as in size: darkest at the
boss where it leaves the helmet, brightening along the length, brightest at the tip; the `down`
faces of every segment a step darker than its `up` face, so the sweep reads as round rather than
flat. A ramp of roughly `55 / 90 / 130 / 175 / 215` across boss-shadow, boss-body, mid-horn,
upper-horn and tip is enough; `*.*` for a base pair and then the faces that differ is the cheap way
to leave nothing unpainted. A single brighter row along the horn's leading (outboard) edge is worth
one extra call. Count your paint calls and say what the face painter did and did not cover.

## Recipe

Centre item `minecraft:ender_pearl`, paper ring, craftable. Verified unused by any
`template_*.json` in the mod or in any pack. The result is the `horns` template.


**Dropped after the run (2026-09-08).** The recipe existed only so that every session of the
concurrency A/B did identical work; `docs/plans/pack-line.md` gives this piece no centre, and a
measurement is not a reason to add a craftable to a pack. `template_dragon_horns.json` is deleted and
the piece is reached the way the plan says the pack is reached - the `end` loot group over
`minecraft:chests/end_city_treasure`, tag `#armorpieces_dragon:dragonslayer`, both added with it.
The session's work is untouched; only the recipe file is gone.

## Done means

`armorpieces_save` accepted **without** `force`;
`python tools/check_authoring.py packs/dragon/datapack packs/dragon/resourcepack` clean; the Lessons
section below filled in.

Two things this piece does **not** do, because it is not the mod's own:
`python tools/check_part.py` does not work for an out-of-pack piece — the bridge's own check,
printed after every reply, is the check here. And do **not** run `python -m modpage build`: this
pack is not on the mod's page, and there is no `modpage.yml` line to add.

## Lessons from the session

Built as: one `base` bone at the anchor (starter `main` renamed, starter cube removed) holding the
`boss` cube, then a three-bone chain `horn1` → `horn2` → `horn3` (each parented to the last,
pivoted at the previous segment's unrotated top), one cube per bone. Four cubes total, well under
the five-cube budget. Sizes tapered as the brief asked: `boss` `x -5.47..-4.00` `y 28.2..30.2`
`z -1..1`; `horn1_c` `x -5.25..-4.35` `y 30.2..32.9` `z -0.7..0.7`; `horn2_c` `x -5.1..-4.5`
`y 32.9..35.3` `z -0.5..0.5`; `horn3_c` `x -4.9..-4.5` `y 35.3..37.3` `z -0.35..0.35`.

**Built straight (all bones unrotated, stacked in +y) first, exactly as the brief says, and it
caught two coplanar faces before any rotation was involved:** the boss's outer face landed exactly
on `x -5.60`/`-5.55`, both of which happen to be where `browband`'s and `laurel`'s own cubes sit
(their bands and a knot cluster in that x range) — pulled the boss in to `x -5.47` to clear it, no
particular reasoning needed beyond "not a round number any sibling used". Separately, `horn1`'s
unrotated top landed exactly on `y 33.0`, the helmet shell's own top plane (the brief's own warning
about this — trimmed to `y 32.9`), and `horn3`'s outer face landed exactly on `x -5.0`, the helmet
shell's side plane (trimmed to `x -4.9`). All three were caught by the coplanar check immediately
after placing the unrotated cube, before rotation, which is the right order: fix flat-geometry
coincidences on the straight chain, then bend it, rather than debugging them through a rotation.

**Rotation, once the chain was straight:** set `element set {rotation}` on each bone independently,
innermost-first only by convenience (order doesn't matter — each bone stores its own local
rotation and Blockbench composes the chain regardless of write order). Used the brief's two signs
directly: X positive sweeps a segment's tip toward `+z` (back), Z positive sweeps it toward `-x`
(outboard, on this negative-x side). Angles increased down the chain as the brief suggested —
`horn1 (8°, 0, 6°)`, `horn2 (10°, 0, 8°)`, `horn3 (12°, 0, 10°)` — and both signs came out right on
the first try (no rebuild): the resulting envelope converts to Blockbench-frame `x -6.54..-4.00`
`y 28.20..36.93` `z -1.00..2.42`, comfortably inside the budget's z and well inside its x outboard
wall (`-8.9`), and the horn visibly sweeps up, back and outboard away from the head in the
screenshot. Two small, expected departures from the budget box, both accepted rather than fixed:
the boss's inner face sits at `x -4.00`, 0.1 past the budget's `-4.1` inboard wall, because it
touches the head surface exactly as the brief's own boss placement (`x -5.6..-4.0`) requires — the
check reports this as a `-` note ("lies on the body surface"), not a problem, and matches how the
mod's own `horns` does it. The y floor came out at `28.20`, 0.2 below the budget's stated `28.4` —
also directly from the brief's own boss coordinates (`y 28.2..30.2`); the two numbers in the brief
disagree with each other by that 0.2 and the boss placement was followed literally since it's the
more specific instruction.

**`!` problems accepted:** none at save time. All three coplanar flags were design fixes (see
above), not accepted problems — every one was resolved by nudging the offending cube 0.05-0.13
units before rotating, not by forcing the save. The OVERLAP and `near` hull-test notes against
`circlet`, `laurel` and `browband` (all real mod `brow`-socket pieces worn at the same time as
`horns`) were left standing as `-` notes: advisory hull tests only, and a horn rising from the
temple is always going to graze the brow's ornaments in a hull test given how little clearance the
head has — the check itself never asks for a decision on them.

**Paint:** one `armorpieces_paint` call on `part` (the only sheet), 15 face-writes covering all 24
faces of the 4 cubes via each cube's `*` wildcard plus `up`/`down` overrides: boss at 90 (base) /
55 (down, shadow) / 100 (up), then the three horn segments stepping up the ramp roughly as the
brief suggested — `horn1_c` 130/100/145, `horn2_c` 175/150/190, `horn3_c` 215/190/225 — each also
getting a `west` override a few points brighter than its base (155/200/235) for the brief's
"brighter row along the leading edge": on this negative-x side, `west` is the face whose normal
points further toward `-x`, i.e. outboard, which is the horn's leading edge as it sweeps away from
the head. No `texture op:rects` or pixel-level work was needed; the face painter covered every face
in the one call.

**A tooling note for the next session, not a piece note:** `armorpieces_check` returned a
`FileNotFoundError` on `part.bbmodel` for one call right after the paint call (three retries, same
error); a trivial no-op edit (`element set {visibility: true}` on an already-visible cube) produced
a fresh status write and the very next check succeeded normally with the full clean report. If a
check ever comes back with that error, don't treat it as a real problem — make any small edit and
check again.

**What the next piece of this pack should know.** `dragon_crest` (the other `crest`-socket sibling
of this bone, budget `x -1.6..1.6`) never came close to this piece's `x -4.1..-8.9` wall — the 2.5
units of slack the brief mentioned was never spent. `dragon_mask` (brow, front of face) will clear
this piece's `z ≥ -1.6` with room since this horn never goes below `z -1.00`. Two more sockets on
this bone remain unbuilt with briefs already written and ready: `dragon_spines` (pauldrons) and
`dragon_tail` (belt) — both chained/rotated builds of the same kind as this one, one session each.
