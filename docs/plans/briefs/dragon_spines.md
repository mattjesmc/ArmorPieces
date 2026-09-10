# Brief: Dragon Spines

A piece of **Armor Pieces: Dragonslayer** (`armorpieces_dragon`), the first pack of the line in
`docs/plans/pack-line.md` — netherite plate with amethyst light, every piece a part of her body.
Four pieces of the pack already exist, all on the leg (`dragon_knuckles`, `wing_tatters`,
`dragon_scales`, `dragon_talons`); you are on the shoulder. Read
`docs/plans/briefs/LESSONS.md` first: it is the technique the earlier sessions worked out,
distilled and current, and the rotation arithmetic in it is what costs a session a rebuild when
it is skipped.

From the `pauldrons` row of the Dragonslayer table:

> `dragon_spines` — the spine ridge, broken across both shoulders — no fitting.

**Part.** `armorpieces_dragon:dragon_spines`, socket `pauldrons` only. Display name "Dragon Spines".
**No fittings, no static layer, no effects, no loot.** One sheet — the greyscale master. The pack's
black-and-purple look comes from the armor and its trim, not from this piece's own colour, which is
how the mod's own parts work.

Create it with `armorpieces_new` and **name both pack folders and the namespace explicitly**, or it
will be written into the mod:

    name: dragon_spines
    anchor: pauldrons
    namespace: armorpieces_dragon
    datapack: C:\Users\Matthijs\ArmorPieces\packs\dragon\datapack
    resourcepack: C:\Users\Matthijs\ArmorPieces\packs\dragon\resourcepack

Then, before painting:

    armorpieces_set_part { name: "Dragon Spines",
                           recipe: { centre: "minecraft:amethyst_shard", craftable: true } }

The reply will say `static_created: false` and `sheets_created: []` — this piece has one sheet and
that is correct. Set the part data before you paint anyway: it is the step that writes the data
half, and doing it in the same order as every other piece keeps the report comparable.

## The rig, in Blockbench coordinates

`pauldrons` is a **mirrored** socket riding on the arm: model ONE side — the left arm, which is the
**negative x** side in Blockbench — and the game mirrors it.

    left arm box              x -8 .. -4    y 12 .. 24    z -2 .. 2
    chestplate arm shell      x -9 .. -3    y 11 .. 25    z -3 .. 3
    chestplate body shell     x -5 ..  5    y 11 .. 25    z -3 .. 3
    the pauldrons anchor      (-6, 22, 0)

Front is **negative z**. Two shells matter here and they overlap between `x = -5` and `x = -3`: the
arm's and the torso's. Sit outboard of the body shell (`x ≤ -5.4`) and above the arm shell's top
plane (`y ≥ 25`) rather than trying to thread between them, and never put a face exactly on
`x = -9`, `x = -5` or `y = 25` — a face in a shell's plane z-fights.

This socket rides the arm, so everything you build swings with it on every stride.

## Shape

Her back ridge, carried on the shoulder: **a low cap plate with four spines standing off it**,
marching outboard down the shoulder line and getting shorter as they go — the ridge is "broken
across both shoulders", so this is a *fragment* of a spine row, not a complete fan.

- One bone `base` at the anchor (rename the starter `main`; never call a bone `root`; remove the
  starter cube).
- **A cap**, one cube in `base`, lying along the top of the shoulder: `x -9.6 .. -5.5`,
  `y 24.2 .. 25.1`, `z -2.4 .. 2.4`. It is what the spines grow out of and what hides the seam
  where they meet the chestplate.
- **Four spine bones** as children of `base`, standing on the cap, marching outboard:
  - `spine1` — `x -6.6 .. -5.6`, to about `y 28.9` (inboard, the tallest);
  - `spine2` — `x -7.6 .. -6.7`, to about `y 28.2`;
  - `spine3` — `x -8.5 .. -7.7`, to about `y 27.3`;
  - `spine4` — `x -9.3 .. -8.6`, to about `y 26.4` (outboard, the shortest).
  - All four `z -1.5 .. 1.5` or narrower — thin in z, so they read as a ridge seen edge-on rather
    than as four blocks. One cube each; six cubes in total is the budget if one spine earns a
    second, smaller tip cube.
- **Lean them outboard**, a little more with each step out — roughly 6° on `spine1` rising to 16°
  on `spine4` — so the row fans away from the neck instead of standing as a picket fence.
- **The sign, worked out once so you do not have to guess.** These lean about **Z**. A Z rotation
  sends a point `(Δx, Δy)` from the pivot to `(Δx·cosθ − Δy·sinθ, Δx·sinθ + Δy·cosθ)`, and a spine
  standing on its pivot has `Δy` large and positive — so a **positive** θ swings the tip toward
  `−x`, which on this (left, negative-x) arm is **outboard**, away from the head. Negative θ leans
  them into the wearer's ear. At 16° a 2.2-tall spine's tip moves 0.6 units in x: size the angle
  against your nearest wall before you place, rather than fixing an overage afterwards.

**Your envelope budget.** Stay inside `x -10.6 .. -5.4`, `y 24.0 .. 29.6`, `z -2.6 .. 2.6`. The
three sister pieces of this pack that share this bone are `dragon_claws` (vambraces, at the
forearm, `y ≤ 18`) and nothing else yet; the wall that matters is `x ≥ -10.6`, because this is a
mirrored socket and the pair's span is `2 × |x|`. At `x = -10.6` the pair spans 21.2 against the
18 the shoulders span, which the check reports as a note — `spaulders` (20.65), `lames` (21.7) and
`mantle` (22.9) all carry it. Say in your report what your span came out as and that you meant it.

**What this socket makes you watch.** `y ≥ 24.0` keeps the whole piece above the arm box's top
plane, so nothing of it is buried in the sleeve; `x ≤ -5.4` keeps it off the torso. Both walls are
tight and both are load-bearing. The `armorpieces_new` reply lists every other part on this bone
with its envelope in both frames, same-socket first — read it once and say in your report what you
cleared and by how much.

## Sheets

One sheet: `dragon_spines.png`, the **master**, greyscale, its value a position on the wearer's
trim ramp. Alpha is the silhouette and the only source of truth.

Bone spines standing on a plate, and the two should not read as one material: the cap flatter and
mid-grey with a bright `up` face and a dark `down`, each spine graded from a dark base to a bright
tip so the four read as horn. A ramp of roughly `55 / 90 / 130 / 175 / 215` across cap-shadow,
cap-body, spine-low, spine-high and tip is enough; `*.*` for a base pair and then the faces that
differ is the cheap way to leave nothing unpainted. Step the four spines a shade apart so the row
has depth. Count your paint calls and say what the face painter did and did not cover.

## Recipe

Centre item `minecraft:amethyst_shard`, paper ring, craftable. Verified unused by any
`template_*.json` in the mod or in any pack. The result is the `pauldrons` template.


**Dropped after the run (2026-09-08).** The recipe existed only so that every session of the
concurrency A/B did identical work; `docs/plans/pack-line.md` gives this piece no centre, and a
measurement is not a reason to add a craftable to a pack. `template_dragon_spines.json` is deleted and
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

Built exactly to the brief's shape: one `base` bone at the anchor (renamed from the starter `main`,
starter cube removed), one `cap` cube (`x -9.6..-5.5`, `y 24.2..25.1`, `z -2.4..2.4`) and four child
bones `spine1..spine4`, each pivoted at the cap's top plane (`y 25.1`) at the x-center of its own
spine, `z 0`. Each holds one cube built *unrotated* from `y 24.9` (0.2 into the cap, for overlap) up
to the brief's target tip height, `z -1.5..1.5` on all four, then the bone rotated about Z by
6°/9°/13°/16° (spine1..spine4) exactly as suggested. Five cubes total (no second tip cubes needed —
the brief's six-cube ceiling wasn't used).

**The sign check paid off, and the numbers land almost exactly on the brief's "about" targets.**
Working the rotation formula from the brief (`Δx' = Δx·cosθ − Δy·sinθ`, `Δy' = Δx·sinθ + Δy·cosθ`,
pivot at each spine's own base) before placing, using the *inboard* top corner (`Δx = +width/2`) for
the highest point and the *outboard* top corner (`Δx = −width/2`) for the leftmost point:
spine1 (h 3.8, w 1.0, θ6°) tops out at bb `y≈28.93` against the brief's "about 28.9"; spine2
(h 3.1, w 0.9, θ9°) at `y≈28.23` against "28.2"; spine3 (h 2.2, w 0.8, θ13°) at `y≈27.33` against
"27.3"; spine4 (h 1.3, w 0.7, θ16°) at `y≈26.45` against "26.4" and its outboard tip swings to
`x≈-9.645`. All four landed within 0.05 of the brief's suggested heights on the first placement —
unlike `wing_tatters`, this brief's own worked example was correct and safe to place from directly
rather than needing a redo. `inspect bounds` on `part` confirms the *unrotated* box
(`x -9.6..-5.5`, `y 24.2..28.9`, `z -2.4..2.4`, matching the hand cubes exactly); the small rotation
overshoot on x and y (to ≈-9.645 and ≈28.93-28.23-27.33-26.45) is not reported by that tool since it
measures rotated cubes by their unrotated box — the check's own pair-span note is what confirms it
in the game frame instead (below).

**Envelope.** The check's own pair-span note: `pair spans 19.29 across the figure (over the 18 the
shoulders span)` — `19.29 / 2 = 9.645`, exactly the hand-computed spine4 outboard tip, confirming the
rotation math. This sits well inside the brief's ceiling of 21.2 at the `x -10.6` wall (margin
`0.955`), and above the 18-unit shoulder span as the brief said it would, alongside `spaulders`
(20.65), `lames` (21.7) and `mantle` (22.9) — I meant this span. `y` topped out at ≈28.93
(spine1), inside the `24.0..29.6` budget with 0.67 of headroom; `y ≥ 24.0` was never at risk since
every cube starts at `24.2` or `24.9`. `z` stayed at the brief's own `-2.4..2.4` (unrotated only —
Z-axis rotation doesn't move z at all, so no per-spine z check was needed here, unlike
`wing_tatters`'s X-axis strips). No face sits on `x=-9`, `x=-5` or `y=25`: the cap's own faces are at
`x=-9.6/-5.5` and `y=24.2/25.1`, a tenth-plus clear of the shells named in the brief, and the check
raised zero `!` lines or COPLANAR notes against `beast_head`, `spaulders`, `mantle` or the other
same-socket/vambraces neighbours listed in the `armorpieces_new` reply.

**Paint:** one `armorpieces_paint` call on `part` (the only sheet), 31 face-address entries covering
all 30 faces of the 5 cubes in one call (`cap.*` then `cap.up`/`cap.down` overrides; per-spine
`spineN_tip.*` base fill then `north`/`south`/`east`/`west` as a `[high, low]` pair — since each
spine cube's side faces span its full height with the top row at the tip, the pair shading *is* the
"graded from a dark base to a bright tip" the brief asked for with no pixel work — then `up`/`down`
overrides for the tip cap and hidden base). Values: cap 55/90/175 (down/sides/up) as specified;
spines stepped a shade apart per the brief, `low/high/tip` = 125/170/210 (spine1) rising to
140/185/225 (spine4), five points apart per step so the four read distinctly without leaving the
ramp's rough 55–215 range. The face painter covered every face; no `texture op:rects` or pixel
addressing was needed anywhere on this piece.

**`!` problems:** none, at any point — the piece saved clean without `force` on the first attempt.

**`check_authoring.py packs/dragon/datapack packs/dragon/resourcepack` is NOT clean as a whole**,
but the one failure (`reach dragon_tail.json: no recipe, no loot row and in no group's tag`) belongs
to `dragon_tail` (`belt` socket), a piece with a data file present in the same pack folder but not
listed by `armorpieces_pieces` at the start of this session and not touched by it — evidently another
concurrent session's in-progress work on the same pack (its file's mtime lands in the same minute as
this session's save). Every check line naming `dragon_spines` specifically passed (`roundtrip`,
`data`, `recipe template_dragon_spines.json: ok (on)`, `reach dragon_spines.json: ok (crafted)`); I
left `dragon_tail` untouched per the standing instruction not to touch other parts' files. The next
session touching this pack should expect `dragon_tail` to be mid-build and re-run the authoring check
once it's finished rather than reading this collision as a regression in `dragon_spines`.

**For the next piece of this pack:** the rotation formula from this brief and `wing_tatters`' is
worth carrying forward as a standing method — compute the pivot-relative corner deltas for the
tightest-wall corner *before* placing, not after — but on a Z-only lean (rather than X or Y) it is
noticeably simpler, since z stays exactly fixed and only x/y move; if a future shoulder piece leans
about X or Y as well, check that axis's swing separately, the way `wing_tatters` had to for X.
