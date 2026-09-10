# Brief: Dragon Claws

A piece of **Armor Pieces: Dragonslayer** (`armorpieces_dragon`), the first pack of the line in
`docs/plans/pack-line.md` — netherite plate with amethyst light, every piece a part of her body.
Read `docs/plans/briefs/LESSONS.md` first — it is the current technique. **Do not skim other briefs
for technique**; the numbers you need are below.

From the `vambraces` row of the Dragonslayer table:

> `dragon_claws` — the wing claws laid along the forearms — fitting `guard` — found in the End.

**The name shadows the mod's own `claws`, on the same socket, and that is allowed** because the
qualifier is the subject: these are *her* claws, the three hooks at the bend of a dragon's wing,
strapped down along the arm. What is not allowed is building the mod's piece again. `claws`
(`x -9.50..-3.50`, `y 7.35..16.05`) hangs **past the hand** like a set of talons on the fingers.
Yours lie **flat along the forearm** and stop at the wrist.

## The part

    armorpieces_new
      name:         dragon_claws
      anchor:       vambraces
      namespace:    armorpieces_dragon
      datapack:     C:\Users\Matthijs\ArmorPieces\packs\dragon\datapack
      resourcepack: C:\Users\Matthijs\ArmorPieces\packs\dragon\resourcepack

**Name the namespace and both pack folders explicitly** or the piece is written into the mod.

Then, before you paint:

    armorpieces_set_part
      name:     "Dragon Claws"
      fittings: [ "armorpieces:guard" ]

That call creates `part_guard`, the mask sheet. **No static layer, no effects, no loot row, and NO
RECIPE** — see *How it is had*.

## The rig, in Blockbench coordinates

`vambraces` is a **mirrored** socket on the forearms: model **one** side — the **negative x** side —
and the game mirrors it.

    left arm box            x  -8.00 .. -4.00    y  12.00 .. 24.00    z  -2.00 ..  2.00
    sleeve shell (+1.0)     x  -9.00 .. -3.00    y  11.00 .. 25.00    z  -3.00 ..  3.00
    the vambraces anchor    (-6, 16, 0)

The arm bone's pivot is at Blockbench **`y = 22`, not the arm box's top at 24** — the check answers
`y_local = 22 - y_bb` on this bone, and converting with 24 makes a correct piece look two units out.
That mistake has already been made once on this socket; both frames are given below, so do not
convert by hand.

Front is **negative z**. On this side **`west` is the outboard face** and `north` is the front.

The anchor is inside the arm, so the strap below starts inside the sleeve and comes out through it.
That is correct. Do not land a face on `x = -9`, `x = -3`, `z = ±3`, `y = 25`, `y = 11`, or on the
arm box's own walls at `x = -8`, `x = -4`, `y = 24`, `y = 12`, `z = ±2`.

## Shape

A strap around the forearm with three claws lying along the outboard face beneath it, the outer two
splayed a little so they are not a comb. Four cubes, two of them in rotated bones.

**Build every bone unrotated first** (`LESSONS.md` 1); set the two rotations last.

- One bone `base` at the anchor (rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube).

- **`strap`**, one cube in `base`, unrotated — the band that holds the claws on, and **the whole of
  the `guard` mask**:

        x  -9.45 .. -2.55     y  17.25 .. 18.45     z  -3.45 ..  3.45

- **`claw_mid`**, one cube in `base`, unrotated — the middle claw, lying along the outboard face:

        x  -9.75 .. -9.05     y  12.25 .. 17.35     z  -0.65 ..  0.65

- **Two splayed claws**, one cube each in its own bone. The pivot is at the **top** of each claw,
  where it goes under the strap, so the free end is what swings (`LESSONS.md` 7a):

  | bone | pivot | cube, unrotated | rotation |
  |---|---|---|---|
  | `claw_front` | (-9.40, 17.35, -1.60) | x -9.75..-9.05, y 12.45..17.35, z -2.25..-0.95 | (10, 0, 0) |
  | `claw_back`  | (-9.40, 17.35,  1.60) | x -9.75..-9.05, y 12.75..17.35, z  0.95..2.25 | (-10, 0, 0) |

  **The signs are opposite on purpose.** On a rotation about X, a point below the pivot moves by
  `Δz' = Δy·sinθ`: `+10°` carries the front claw's tip forward (toward `-z`) and `−10°` carries the
  back claw's tip backward. Splayed claws read as a hand; parallel ones read as a rack.

**Where the tips land**, so you can confirm the rotations took:

    claw_front  tip (y 12.52, z -2.45)      claw_back  tip (y 12.52, z  2.45)

and the extreme **corners**, which are what the envelope is made of (`LESSONS.md` 3):

    claw_front  forward corner z = -3.09      claw_back  rear corner z = 3.09

Those corners clear the sleeve's walls at `z = ±3` by nine hundredths, which is deliberate: the
claws are meant to break the silhouette of the sleeve without lying in its planes.

## Envelope budget, in both frames

    Blockbench      x  -9.85 .. -2.45     y  12.20 .. 18.55     z  -3.55 ..  3.55
    check's frame   x  -2.55 ..  4.85     y   3.45 ..  9.80     z  -3.55 ..  3.55

`inspect bounds` measures a rotated cube by its **unrotated** box (`LESSONS.md` 5); the check's
envelope in the second frame is what confirms this piece.

**The pair-span rule does not apply on this socket.** The arms are already outboard of the
shoulders, so the check's pair comparison means nothing here. Report your envelope; do not try to
bring a span under 18.

Same-socket pieces, for the heights and depths to place against (never worn together, so never
compared):

| piece | Blockbench |
|---|---|
| `claws` | x -9.50..-3.50, y 7.35..16.05, z -3.00..3.00 |
| `vambraces` | x -10.00..-5.50, y 12.00..18.00, z -4.00..4.00 |
| `buckler` | x -10.20..-3.10, y 12.53..18.47, z -3.35..3.35 |
| `blaze_bracers` | x -9.45..-2.65, y 15.15..20.45, z -3.35..3.35 |
| `cuffs` | x -10.07..-1.93, y 12.60..16.97, z -4.07..4.07 |

The piece you are really measured against is whatever sits on `pauldrons` above you, and the lowest
of those is `wing_cases` at `y = 14.07` — it will show as an `OVERLAP` hull note against your
claws. `dragon_spines`, the pack's own pauldrons piece, stops at `y = 24.20` and is nowhere near.

## The sheets

**`part` (master), greyscale.** Her claws are horn over the same black plate as the rest of the
pack, and the strap is hardware:

- Each **claw** takes a `[top, bottom]` gradient down its `west` (outboard), `north` and `south`
  faces, from mid-dark where it goes under the strap to **near-white at the tip**. A claw is lightest
  where it is thinnest, and that gradient is the whole read at 1/16 of a block.
- The claws' `down` faces — the tips — take the brightest value on the piece.
- The middle claw one step darker overall than the two splayed ones, so the three separate.
- **`strap`** flat mid-dark on every face, no gradient. It is hardware; it must sit back and let the
  claws read.

Roughly `50 / 85 / 130 / 190 / 240` from strap to claw tip. **One `armorpieces_paint` call for the
whole piece**: a `*` wildcard per cube for the base, then the `[top, bottom]` pairs
(`LESSONS.md` 11).

**`part_guard` (mask), greyscale.** The `strap` cube and **nothing else** — all six faces, one flat
mid value. The strap takes the player's chosen guard material; the claws never do.

## How it is had

`pack-line.md` gives this piece **no recipe centre**: the Dragonslayer pack is found in the End, and
only the pack's pieces with a centre are also craftable. So `reach` will fail until the piece is in
the pack's loot group tag. **Add its id to that file yourself** once the piece is saved:

    packs/dragon/datapack/data/armorpieces_dragon/tags/armorpieces/armor_decoration/dragonslayer.json

A plain `{"values": [...]}` list, already holding the pack's other pieces, sorted. Add
`"armorpieces_dragon:dragon_claws"` in sorted position and write it back as
`JSON.stringify(value, null, 2) + "\n"`. The group itself (`armorpieces/loot_group/end.json`,
0.15 over `minecraft:chests/end_city_treasure`) needs no change.

## Done means

- [ ] The check is clean, or every `!` still standing is one this brief allows.
- [ ] Envelope inside the budget, **reported in the check's frame**, and the two tips confirmed
      against the table above.
- [ ] Both sheets painted: master everywhere, `part_guard` on `strap` only.
- [ ] The tag file updated.
- [ ] `armorpieces_save` accepted **without** `force`.
- [ ] `python tools/check_authoring.py packs/dragon/datapack packs/dragon/resourcepack` clean,
      including `reach dragon_claws.json: ok (found)`.
- [ ] The tab closed, and the Lessons section below filled in.

`python tools/check_part.py` does not work on an out-of-pack piece, and `python -m modpage build` is
not this pack's page.

**Allowed to force:** the strap's inboard faces being buried or unpainted — that is what a band
around an arm is — and an `OVERLAP` or `near` note against a `pauldrons` piece such as
`wing_cases`. **Nothing else.**

**Closing the tab is not optional and it is the last thing you do.** The window you are working in is
handed to the next piece's session, and a tab left open is the tab that session finds *active*. Call
`armorpieces_close` when you are done — and also when you are **not** done: if you abandon this piece
or stop to ask a question, close it first (`discard: true` if it should not be kept) and say in your
report what you left behind in the pack folders.

## Lessons from the session

Built exactly as specified: `base` bone at the anchor holding `strap` and `claw_mid` unrotated,
plus `claw_front` and `claw_back` in their own bones at the given pivots, placed unrotated first
and then rotated `(10,0,0)` / `(-10,0,0)` last. All four cubes' coordinates were taken verbatim
from the brief's tables — no nudging needed, and the check's envelope came back
`x -2.45..4.75 y 3.55..9.75 z -3.45..3.45` in its own frame, inside the brief's budget
(`-2.55..4.85 / 3.45..9.80 / -3.55..3.55`) on every axis. Did not independently re-derive the tip
and corner positions by hand (`LESSONS.md` 5 says `inspect bounds` wouldn't show them anyway); the
envelope match is the confirmation the brief points to.

Hit `7b` immediately: `claw_front` and `claw_back` name both a bone and its cube, so
`element {op:"set", id:"claw_front", ...}` for the rotation was refused ("names 2 elements") until
I addressed the bone by its uuid from the `add_group` reply. Same trick would be needed for any
future addressing of these bones by name.

Painting followed the brief's five-value ramp (50 strap / 85 & 190 for the middle claw's
under-strap-to-tip gradient / 130 & 240 for the two splayed claws), with the down faces on every
claw flat at 240 (read as "the brightest value on the piece", applied to all three tips equally,
distinct from the "one step darker overall" instruction which I took to mean the side-face
gradient only). One `armorpieces_paint` call per sheet, as `LESSONS.md` 11 recommends; no pixel
work needed.

The only check lines left standing are the ones the brief names as acceptable: five `OVERLAP` and
four `near` notes against `wing_cases:pauldrons`, and the `pair spans 19.50` note (the brief says
not to chase this on the vambraces socket). `armorpieces_save` needed no `force` — none of these
are `!` lines, only `-` advisory ones (`LESSONS.md` 8).

Nothing here generalises beyond what `LESSONS.md` already says; no addition made.
