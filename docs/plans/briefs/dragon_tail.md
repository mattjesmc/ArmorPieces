# Brief: Dragon Tail

A piece of **Armor Pieces: Dragonslayer** (`armorpieces_dragon`), the first pack of the line in
`docs/plans/pack-line.md` — netherite plate with amethyst light, every piece a part of her body.
Four pieces of the pack already exist, all on the leg (`dragon_knuckles`, `wing_tatters`,
`dragon_scales`, `dragon_talons`); you are on the waist. Read
`docs/plans/briefs/LESSONS.md` first: it is the technique the earlier sessions worked out,
distilled and current, and the rotation arithmetic in it is what costs a session a rebuild when
it is skipped.

From the `belt` row of the Dragonslayer table:

> `dragon_tail` — the tail base ringing the waist, hanging behind — no fitting.

**Part.** `armorpieces_dragon:dragon_tail`, socket `belt` only. Display name "Dragon Tail".
**No fittings, no static layer, no effects, no loot.** One sheet — the greyscale master. The pack's
black-and-purple look comes from the armor and its trim, not from this piece's own colour, which is
how the mod's own parts work.

Create it with `armorpieces_new` and **name both pack folders and the namespace explicitly**, or it
will be written into the mod:

    name: dragon_tail
    anchor: belt
    namespace: armorpieces_dragon
    datapack: C:\Users\Matthijs\ArmorPieces\packs\dragon\datapack
    resourcepack: C:\Users\Matthijs\ArmorPieces\packs\dragon\resourcepack

Then, before painting:

    armorpieces_set_part { name: "Dragon Tail",
                           recipe: { centre: "minecraft:popped_chorus_fruit", craftable: true } }

The reply will say `static_created: false` and `sheets_created: []` — this piece has one sheet and
that is correct. Set the part data before you paint anyway: it is the step that writes the data
half, and doing it in the same order as every other piece keeps the report comparable.

## The rig, in Blockbench coordinates

`belt` is **not** a mirrored socket: one attachment, at the waistline on the body, and you model
the whole ring.

    body box                  x -4   .. 4     y 12   .. 24     z -2   .. 2
    leggings shell (+0.5)     x -4.5 .. 4.5   y 11.5 .. 24.5   z -2.5 .. 2.5
    chestplate shell (+1.0)   x -5   .. 5     y 11   .. 25     z -3   .. 3
    the belt anchor           (0, 14, 0)

Front is **negative z**; behind the wearer is `+z`. The chestplate covers the whole torso down to
`y = 11`, so a belt is *always* outside a shell rather than between two — sit clear of `x = ±5` and
`z = ±3`, and never put a face exactly on either plane. `girdle` clears the chestplate by 0.86 in x
and 1.0 in z and the check reports that as an ordinary `past chestplate` line.

## Shape

The base of her tail, worn as a belt: **a ring around the waist that thickens at the back into a
short tail** of three tapering segments, hanging down and behind. The ring is the belt; the tail is
what makes it hers.

- One bone `base` at the anchor (rename the starter `main`; never call a bone `root`; remove the
  starter cube).
- **The ring**, four cubes in `base`, a band about 2 units tall at `y 12.9 .. 14.9`:
  - `front` — `x -4.4 .. 4.4`, `z -3.0 .. -2.4`;
  - `back` — `x -4.4 .. 4.4`, `z 2.4 .. 3.0`;
  - `flank_l` — `x -5.4 .. -4.4`, `z -2.6 .. 2.6`;
  - `flank_r` — `x 4.4 .. 5.4`, `z -2.6 .. 2.6`.
  - Four straight cubes, no mitred corners: `girdle` spends eight cubes on a mitred ring and this
    piece cannot afford that and a tail as well.
- **The tail**, three bones hanging off the back of the ring, each a child of the one before it,
  each shorter and thinner, curving down and back:
  - `tail1` from about `y 13.4` at `z 3.0`, the thickest;
  - `tail2` off `tail1`;
  - `tail3` off `tail2`, ending in a point.
  - Three cubes; seven or eight in total including the ring is the budget.
- **Build it straight, then aim it.** Place each segment unrotated pointing back along `+z`, look
  at it, then set each bone's rotation with `element set {rotation}` so the tail droops. The droop
  is a rotation about **X**: a segment pointing back has `Δz` large and positive, and
  `Δy' = Δy·cosθ − Δz·sinθ`, so a **positive** θ about X sends the tip **down**. Roughly 15°, 20°
  and 25° down the chain reads as weight; check each tip against the `y ≥ 8.2` floor before you
  commit the angle rather than fixing an overage afterwards, because these segments are long in z
  and the droop moves them a long way in y.

**Your envelope budget.** Stay inside `x -5.6 .. 5.6`, `y 8.2 .. 15.2`, `z -3.2 .. 6.6`. Nothing
else in this pack is on this bone yet, so the budget is about the wearer, not about siblings: the
floor at `y = 8.2` is what keeps the tail off the knee, and `z ≤ 6.6` is what keeps it from
trailing further behind the figure than a cloak does.

**What this socket makes you watch, and it is the interesting part of this piece.** The `back`
socket rides the same bone and is worn at the same time — `cloak` (`z 2.90 .. 4.63`, down to
`y 9.63`), `banner`, `quiver`, `carapace`, `bedroll`, `pinions`. A tail hanging behind will
hull-overlap several of them, and the check will say so. Those lines are `-` notes, an advisory
hull test ("check whether the real cubes meet"), not `!` problems: `girdle` ships with three
OVERLAP notes against `cloak`'s banner for exactly this reason. **Decide them rather than
averaging them away** — say in your report which back pieces you overlap, by how much, and why
that is acceptable for a tail (or shorten it). The `armorpieces_new` reply lists every other part
on this bone with its envelope in both frames, same-socket first; read it once.

## Sheets

One sheet: `dragon_tail.png`, the **master**, greyscale, its value a position on the wearer's trim
ramp. Alpha is the silhouette and the only source of truth.

Scaled hide over a hard band: the ring flatter and mid-grey with a bright `up` edge and a dark
`down` edge so it reads as a belt, the tail graded darker toward the tip so it recedes, and each
tail segment's `down` face darkest of all. A ramp of roughly `55 / 85 / 120 / 165 / 210` across
under-shadow, tail-low, tail-high, ring-body and lit-edge is enough; `*.*` for a base pair and then
the faces that differ is the cheap way to leave nothing unpainted. The ring and the tail should not
read as one material — step them a few points apart. Count your paint calls and say what the face
painter did and did not cover.

## Recipe

Centre item `minecraft:popped_chorus_fruit`, paper ring, craftable. Verified unused by any
`template_*.json` in the mod or in any pack. The result is the `belt` template.


**Dropped after the run (2026-09-08).** The recipe existed only so that every session of the
concurrency A/B did identical work; `docs/plans/pack-line.md` gives this piece no centre, and a
measurement is not a reason to add a craftable to a pack. `template_dragon_tail.json` is deleted and
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

Built exactly as sketched: one `base` bone at the belt anchor (renamed from the starter `main`,
starter cube removed), four ring cubes in `base` — `front`, `back`, `flank_l`, `flank_r` — at the
brief's coordinates, then a three-bone chain `tail1` → `tail2` → `tail3`, each a child of the last,
one cube each, all built straight (unrotated, pointing along `+z`, in a line at `y=13.4`) before any
rotation was set, per the brief's method. Pivots: `tail1` at `(0, 13.4, 3.0)`, `tail2` at
`(0, 13.4, 4.5)`, `tail3` at `(0, 13.4, 5.85)` — each 0.25 back from the previous cube's rear face,
giving the quarter-unit overlap. Cube sizes tapered as asked: `tail1_cube` 2.6×1.8×2.0 (thickest),
`tail2_cube` 2.2×1.4×1.6, `tail3_cube` 1.4×1.0×1.4 (ending in a point). 7 cubes total (4 ring + 3
tail), one under the 8-cube budget.

**Rotation:** all three tail bones rotate about X only, each set with `element set {rotation}`
directly (no manual per-cube repositioning) — `tail1 = 20°`, `tail2 = 25°`, `tail3 = 30°`, all
positive, all compounding down the chain (cumulative effective droop at the tip is close to 75°
since Blockbench's nested-group rotation is hierarchical and X rotations compose by simple angle
addition). This is a bit steeper than the brief's "roughly 15/20/25", chosen after hand-computing
the chain with the brief's own formula (`Δy' = Δy·cosθ − Δz·sinθ`, `Δz' = Δy·sinθ + Δz·cosθ`,
composed link by link using each joint's *cumulative* angle, not just its own) **before** setting
anything: at 15/20/25 the tip corner landed at `z ≈ 6.77`, over the `z ≤ 6.6` wall — a segment
pointing back is long in z, so a shallow droop barely compresses its reach, exactly the trap
`wing_tatters` hit on a different axis. Steepening to 20/25/30 pulled the worst corner back to
`z ≈ 6.21` (checked value, matched the hand math almost exactly: predicted 6.209) with a lot of
room left on the floor (`y ≥ 8.2`) since the drop was never the binding constraint here — z was.
Final envelope from the check: `x -5.40..5.40  y 9.10..13.55  z -2.95..6.21`, inside the brief's box
`x ±5.6, y 8.2..15.2, z ≤ 6.6` on every axis, with the z margin the tightest at 0.39. **Lesson for
the next chain-rotation piece:** work out which wall is actually binding (floor vs. reach) before
picking angles from a "roughly N°" suggestion — a segment "long in z" is bounded by z from droop
compression, not by y from the drop, and the two don't move together at the same rate.

**`!` problems accepted:** none at save time. The ring's `front`/`back` cubes as the brief specified
them (`z -3.0..-2.4` / `2.4..3.0`) put a face exactly on the chestplate shell's own `z = ±3` plane —
the check only surfaced this as a `-` note ("lies on the chestplate surface"), not a blocking `!`,
but on the `wing_tatters` precedent of not trusting a coplanar face to render cleanly, both were
pulled in by 0.05 (`front` to `-2.95`, `back` to `2.95`) before painting. This cost nothing else —
`tail1`'s overlap into the (now slightly shorter) `back` cube is still comfortably inside its
0.25-unit design overlap. The OVERLAP and `near` hull-test notes against `cloak:back`, `banner:back`
and `quiver:back` (all worn on the same bone at the same time as `belt`) were left standing as `-`
notes: a tail hanging behind the waist by design reaches into the same z-range as a cloak, a banner
mount and a quiver sling, and the check itself only asks for a decision on `!` lines. Shortening the
tail to clear all three would have gutted the segment lengths well below the brief's shape; the
piece reads as a tail, the overlaps are with objects a player would not literally clip through
(cloth banners, a sling), and `girdle` already shipped with the same kind of note against the same
neighbours for the same reason.

**Paint:** one `armorpieces_paint` call on `part` (the only sheet), 56 face-writes covering all 42
faces of the 7 cubes (`<cube>.*` wildcards for the base coat, then `<cube>.up`/`<cube>.down`
overrides, so several faces were written twice — later entries win, as documented). Ring cubes:
body 165, `up` 210, `down` 55 (bright top edge, dark underside, per the "ring-body"/"lit-edge"/
"under-shadow" bands). Tail, graded darker toward the tip so it recedes and reads as a different
material from the ring: `tail1_cube` body 120 (`tail-high`), `up` 140, `down` 55; `tail2_cube` body
100, `up` 115, `down` 45; `tail3_cube` body 85 (`tail-low`), `up` 95, `down` 35 — each segment's
`down` face darker than the last, satisfying "each tail segment's down face darkest of all" as a
progression rather than a single repeated value. No `texture op:rects` or pixel work was needed; the
face painter's wildcard-then-override pattern left nothing unpainted in the one call.

**For the next belt-socket piece of this pack:** the `belt` bone's neighbours worth checking against
are the other `belt`-socket pieces (`buckled_belt`, `chain_belt`, `cord`, `donkey_tail`, `fauld`,
`girdle`, `pouch_belt`, `sash` — never compared, but useful for placing relative height) and the
worn-together back-socket family (`bandolier`, `banner`, `bedroll`, `carapace`, `chain_of_office`,
`cloak`, `fang_necklace`, `flower_brooch`, `gorget`, `nautilus_gorget`, `pendant`, `pinions`,
`quiver`, `ruff`, `scarf`, `spine_ridge`, `turtle_shell`, `wing_roots`) — anything that hangs behind
the waist will hull-overlap several of these and that is expected, not a defect to chase away.
