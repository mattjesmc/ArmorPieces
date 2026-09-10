# Brief: Dragon Wings

A piece of **Armor Pieces: Dragonslayer** (`armorpieces_dragon`), the first pack of the line in
`docs/plans/pack-line.md` — netherite plate with amethyst light, every piece a part of her body.
Nine pieces exist; you are the tenth. Read `docs/plans/briefs/LESSONS.md` first — it is the current
technique. **Do not skim other briefs for technique**; the numbers you need are below.

From the `back` row of the Dragonslayer table:

> `dragon_wings` — folded membrane wings — **the glide piece** — no fitting — found in the End.

**This is the first effect any pack has ever shipped.** The mod's own `pinions`, `claws`, `circlet`
and `cloak` carry effects; no pack does. `dragon_wings` carrying `armorpieces:glide` is the
deliberate first test of that seam, so the data half of this piece matters as much as the model.

## The part

    armorpieces_new
      name:         dragon_wings
      anchor:       back
      namespace:    armorpieces_dragon
      datapack:     C:\Users\Matthijs\ArmorPieces\packs\dragon\datapack
      resourcepack: C:\Users\Matthijs\ArmorPieces\packs\dragon\resourcepack

**Name the namespace and both pack folders explicitly** or the piece is written into the mod.

Then, before you paint:

    armorpieces_set_part
      name:    "Dragon Wings"
      effects: [ { type: "armorpieces:glide", sink: 0.02, wear_interval: 6 } ]

**No fittings, no static layer, no loot row, and NO RECIPE** — see *How it is had* below. One sheet,
the greyscale master.

**The effect numbers are not yours to tune.** The mod's `pinions` is `{"sink": 0.03,
"wear_interval": 4}`, deliberately a worse elytra. Hers are the reward for the hardest fight in the
game and are the better of the two, still worse than a real elytra: `sink 0.02`, `wear_interval 6`.
The wear is spent on the chestplate carrying them. If `armorpieces_set_part` refuses the effect
block, stop and report exactly what it said — that is the seam being tested and a workaround would
hide the answer.

## The rig, in Blockbench coordinates

`back` is **not** a mirrored socket. One attachment between the shoulder blades, and **you model
both wings yourself** — the mirroring below is yours to write, not the game's.

    body box                x  -4.00 ..  4.00    y  12.00 .. 24.00    z  -2.00 ..  2.00
    chestplate shell (+1.0) x  -5.00 ..  5.00    y  11.00 .. 25.00    z  -3.00 ..  3.00
    the back anchor         (0, 22, 2)

The body bone's pivot is at Blockbench `y = 24`, so the check's frame is `y_local = 24 - y_bb`.

Back is **positive z**. Your own shell is the **chestplate**, whose back wall is `z = +3`:
**everything must sit behind that** (greater than 3) or it is buried under the armor. `z = 3.00` is
the one plane on this piece that would be an outright `!`.

Do not land a face on `z = ±3`, `x = ±5`, `y = 25` or `y = 11`.

## Shape

Wings folded against the back: two spars per side meeting in a bend above the shoulder, a membrane
panel between them, and a mount block over the shoulder blades. Seven cubes, four of them in rotated
bones.

**Build every bone unrotated first** (`LESSONS.md` 1), let the check fire on the flat geometry, and
only then set the rotations. The two spars on a side are **siblings under `base`, not a chain** —
each carries its own absolute rotation, so nothing composes and the tip table below is exact.

- One bone `base` at the anchor (rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube).

- **`mount`**, one cube in `base`, unrotated — the block the wings grow out of:

        x  -2.45 ..  2.45     y  20.35 .. 23.65     z   3.05 ..  3.75

- **Four spars**, one cube each in its own bone under `base`:

  | bone | pivot | cube, unrotated | rotation |
  |---|---|---|---|
  | `spar1_l` | (-1.60, 21.40, 3.75) | x -1.95..-1.25, y 21.40..25.90, z 3.45..4.05 | (0, 0, 30) |
  | `spar2_l` | (-3.85, 25.30, 3.75) | x -4.18..-3.48, y 21.10..25.30, z 3.45..4.05 | (0, 0, -20) |
  | `spar1_r` | (1.60, 21.40, 3.75) | x 1.25..1.95, y 21.40..25.90, z 3.45..4.05 | (0, 0, -30) |
  | `spar2_r` | (3.85, 25.30, 3.75) | x 3.48..4.18, y 21.10..25.30, z 3.45..4.05 | (0, 0, 20) |

  **While the spars are still unrotated the envelope will read above the budget** — `spar1`'s
  unrotated cube tops out at `y = 25.90` against a budget ceiling of `25.80`. That is expected and it
  resolves the moment the rotations are set (the rotated top corner lands at `25.47`). Do not shorten
  the spars to make the flat geometry fit.

  `spar1` is the wing's upper arm, rising outward from the mount; `spar2` is the forearm, folded
  back down from the bend. **The two sides take opposite signs** — on a rotation about Z, a point
  above the pivot moves by `Δx' = −Δy·sinθ`, so `+30°` carries the left tip to `−x` and `−30°`
  carries the right tip to `+x`. Get one side right, then mirror both the cube and the sign.

- **Two membranes**, one cube each in `base`, **unrotated** — the skin stretched between the spars:

        membrane_l    x  -5.15 .. -1.45     y  21.60 .. 24.60     z   3.58 ..  3.90
        membrane_r    x   1.45 ..  5.15     y  21.60 .. 24.60     z   3.58 ..  3.90

  They sit inside the spars' `z` range, so the spars stand a little proud on both faces, which is
  what makes a membrane read as stretched between bones rather than painted on a slab.

**Where the bends and tips land**, so you can confirm the rotations took:

    spar1_l  bend (-3.85, 25.30)      spar2_l  tip (-5.29, 21.35)
    spar1_r  bend ( 3.85, 25.30)      spar2_r  tip ( 5.29, 21.35)

and the extreme **corners**, which are what the envelope is made of (`LESSONS.md` 3):

    spar2  outboard corner  x = ±5.62        spar1  top corner  y = 25.47

`spar1`'s top corner is above the chestplate's shoulder line at `y = 25`, on purpose: the bend of a
folded wing stands over the shoulder, which is how a folded wing is read at a glance.

## Envelope budget, in both frames

    Blockbench      x  -5.80 ..  5.80     y  20.20 .. 25.80     z   3.02 ..  4.10
    check's frame   x  -5.80 ..  5.80     y  -1.80 ..  3.80     z   3.02 ..  4.10

`inspect bounds` measures a rotated cube by its **unrotated** box and will not show a rotation
overshoot (`LESSONS.md` 5). The check's envelope, in the frame on the second line, is what confirms
this piece.

Same-socket pieces, for the heights and depths to place against (never worn together, so never
compared):

| piece | Blockbench |
|---|---|
| `pinions` | x -7.78..8.32, y 13.68..23.29, z 2.00..6.29 |
| `cloak` | x -5.45..5.45, y 9.63..24.85, z 2.90..4.63 |
| `wing_roots` | x -4.53..4.53, y 14.50..21.50, z 0.32..6.59 |
| `carapace` | x -4.75..4.75, y 15.60..24.60, z 3.10..5.25 |
| `blaze_halo` | x -4.90..4.90, y 15.10..24.90, z 4.25..4.75 |

**`pinions` is the piece you must not repeat.** It is the mod's spread pair of feathered wings,
16 units across and hanging to `y = 13.68`. Yours are **folded**: half the span, entirely above the
waist, and made of two straight spars and a flat membrane rather than a fan. If yours starts looking
like `pinions`, shorten the membranes rather than the spars.

The pieces you are really measured against are the `collar` and `belt` pieces on the same body bone.
The one that comes close is `scarf` (`collar`, `z -3.85..3.55`, `y 18.53..24.30`) — the membranes'
front face at `z = 3.58` clears its back face at `3.55` by three hundredths. **Do not move the
membranes forward.**

## The sheet

One sheet, `dragon_wings.png`, the **master**: greyscale, its value a position on the wearer's trim
ramp. Alpha is the silhouette and the only source of truth.

Two materials again, and the contrast between them is the piece:

- **Spars** are bone: the lightest large surfaces, a flat mid-light with their `up` faces brighter
  and their `down` faces dark, so the folded arm reads as a solid thing in front of the membrane.
- **Membranes** are skin stretched thin: much darker than the spars, and **shaded across the span** —
  a `[top, bottom]` pair on the big `north`/`south` faces running from mid at the top edge, where the
  spar holds it up, to dark at the bottom where it sags. Paint three or four one-pixel light lines
  running down each membrane, spaced evenly: those are the finger bones under the skin and they are
  what stop a flat rectangle from looking like a flag.
- **`mount`** darkest of all: it is the root and it should disappear into the armor.

Roughly `40 / 70 / 110 / 165 / 215` from mount to spar highlight. **One `armorpieces_paint` call for
the whole piece** — a `*` wildcard per cube, then the `[top, bottom]` pairs on the membranes, then
the finger lines with `texture op:rects` if the face painter cannot place them (`LESSONS.md` 11).

## How it is had

`pack-line.md` gives this piece **no recipe centre**: the Dragonslayer pack is found in the End, and
only the pack's six pieces with a centre are also craftable. So `reach` will fail until the piece is
in the pack's loot group tag. **Add its id to that file yourself** once the piece is saved:

    packs/dragon/datapack/data/armorpieces_dragon/tags/armorpieces/armor_decoration/dragonslayer.json

It is a plain `{"values": [...]}` list, already holding the pack's other nine, sorted. Add
`"armorpieces_dragon:dragon_wings"` in sorted position, and write the file back as
`JSON.stringify(value, null, 2) + "\n"` so it does not churn. The group itself
(`armorpieces/loot_group/end.json`, 0.15 over `minecraft:chests/end_city_treasure`) already exists
and needs no change.

## Done means

- [ ] The check is clean, or every `!` still standing is one this brief allows.
- [ ] Envelope inside the budget, **reported in the check's frame**, and the bends and tips
      confirmed against the table above.
- [ ] The `armorpieces:glide` effect on the part file, with exactly `sink 0.02`,
      `wear_interval 6` — and **the part file re-read after saving to confirm it survived the round
      trip**. This is the first effect a pack has shipped; say in your report what the file holds.
- [ ] The tag file updated.
- [ ] `armorpieces_save` accepted **without** `force`.
- [ ] `python tools/check_authoring.py packs/dragon/datapack packs/dragon/resourcepack` clean,
      including `reach dragon_wings.json: ok (found)`.
- [ ] The tab closed, and the Lessons section below filled in.

`python tools/check_part.py` does not work on an out-of-pack piece, and `python -m modpage build` is
not this pack's page.

**Allowed to force:** an `OVERLAP` or `near` note against a `collar` piece — those are hull tests
across the body and cannot meet a wing behind it. **Nothing else.** A face on the chestplate's back
wall at `z = 3.00` is a real problem: move it back and it goes away.

**Closing the tab is not optional and it is the last thing you do.** The window you are working in is
handed to the next piece's session, and a tab left open is the tab that session finds *active*. Call
`armorpieces_close` when you are done — and also when you are **not** done: if you abandon this piece
or stop to ask a question, close it first (`discard: true` if it should not be kept) and say in your
report what you left behind in the pack folders.

## Lessons from the session

Built as specced: `base` bone at the anchor holding `mount` (unrotated), two `membrane_l/r` cubes
(unrotated), and four spar bones (`spar1_l`, `spar2_l`, `spar1_r`, `spar2_r`), each with one cube,
built flat first and then rotated by (0,0,±30) and (0,0,±20) per the table. One `armorpieces_paint`
call did the whole master: mount at 40, spars at 165/215(up)/130(down), membranes at a [110,70]
north/south gradient with 90 on the thin end faces, plus 36 `pixels` entries for three finger lines
per membrane face (north and south), each line shaded 140/110/85 top-to-bottom to match the base
gradient's trend.

Two coplanar `!`s came up that the brief didn't call out, both against `scarf:collar`'s `wrap` cube,
not the chestplate shell the brief warned about:

- The `mount` cube's front face, exactly at the brief's `z 3.05`, sat on the same plane as
  `scarf`'s wrap. Nudged the whole cube 0.03 forward (`z 3.08..3.78`) and it cleared. This is a
  LESSONS #6 case (nudge off a coincidental plane) even though `3.05` isn't a round number — it
  just happened to match another piece's cube exactly.
- Setting the spar rotations triggered a second, related coplanar: `spar2_l`/`spar2_r`'s front face
  at `z 3.45` (unaffected by a Z-axis rotation, since Z-rotation doesn't move a point's z-coordinate)
  also sat on `scarf`'s wrap plane. This one only appeared *after* rotating, not on the flat
  geometry — worth noting since LESSONS #1 says build flat and let the check fire there; here the
  coplanar check on this particular plane wasn't triggered until the rotation was set, so building
  flat first didn't catch it. Fixed the same way: nudged all four spar cubes' z-range by +0.03
  (`3.48..4.08` instead of `3.45..4.05`). Since rotation is about Z only, this shift doesn't touch
  x/y and so doesn't move the bend/tip positions at all.

After both nudges, `armorpieces_check` came back completely clean (`ok: nothing needs a decision`) —
every remaining line is a `-` note: five OVERLAP and two `near` lines, all against `scarf:collar` or
`ruff:collar`'s sub-cubes, which the brief pre-authorized. No `!` was force-accepted; the save went
through without `force`.

Envelope, check's own frame (+Y down): `x -5.60..5.60  y -1.47..3.65  z 3.08..4.08`. Converting the y
to Blockbench (`y_bb = 24 - y_local`) gives `y 20.35..25.47` — the max matches the brief's stated
`spar1 top corner y = 25.47` exactly. The x max came out `5.60` against the brief's stated corner
`±5.62`; the 0.02 difference is presumably from the brief's own rounding versus this exact rotation
math, not a placement error — everything else lines up so closely that it isn't worth chasing.
Everything sits inside the stated budget box in both frames.

The `armorpieces:glide` effect was accepted by `armorpieces_set_part` with no error — the seam this
brief exists to test is fine. Re-read after save, straight off disk
(`dragon_wings.json`): `"effects": [{"type": "armorpieces:glide", "sink": 0.02, "wear_interval": 6}]`,
byte-identical to what was set, survived the round trip.

Added `armorpieces_dragon:dragon_wings` to `dragonslayer.json` in sorted order (between
`dragon_talons` and `wing_tatters`). `check_authoring.py` on the pack came back fully clean,
including `reach dragon_wings.json: ok (found)`.

Nothing here needs to go into `LESSONS.md` beyond what's already there — the coplanar-after-rotation
behaviour is a specific instance of #1/#5 (a rotation about one axis doesn't move that axis's own
coordinate, so a plane check on that axis can pass flat and fail once other cubes' rotations are
irrelevant to it — not a new principle, just a reminder that "build flat, let the check fire" catches
everything the axis you're about to rotate touches, not planes on the axis you're rotating *about*).
