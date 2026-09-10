# Brief: Dragon Mask

A piece of **Armor Pieces: Dragonslayer** (`armorpieces_dragon`), the first pack of the line in
`docs/plans/pack-line.md` — netherite plate with amethyst light, every piece a part of her body.
Eight pieces of the pack exist; you are the ninth, and the last one on the head. Read
`docs/plans/briefs/LESSONS.md` first: it is the technique the earlier sessions worked out, distilled
and current. Do not skim other briefs for technique — most of them were written against a bridge that
no longer exists.

From the `brow` row of the Dragonslayer table:

> `dragon_mask` — her eyes and snout, built into the visor — no fitting — found in the End.

**Part.** `armorpieces_dragon:dragon_mask`, socket `brow` only. Display name "Dragon Mask".
**No fittings, no static layer, no effects, no loot row, and NO RECIPE** — see *How it is had* below.
One sheet, the greyscale master. The pack's black-and-purple look comes from the armor and its trim,
not from this piece's own colour, which is how the mod's own parts work.

Create it with `armorpieces_new` and **name both pack folders and the namespace explicitly**, or it
will be written into the mod:

    name: dragon_mask
    anchor: brow
    namespace: armorpieces_dragon
    datapack: C:\Users\Matthijs\ArmorPieces\packs\dragon\datapack
    resourcepack: C:\Users\Matthijs\ArmorPieces\packs\dragon\resourcepack

Then, before painting:

    armorpieces_set_part { name: "Dragon Mask" }

**No `recipe` argument.** The reply will say `static_created: false` and `sheets_created: []` — this
piece has one sheet and that is correct. Set the part data before you paint anyway: it is the step
that writes the data half.

## The rig, in Blockbench coordinates

`brow` is **not** a mirrored socket: one attachment, on the front of the head, and you model the
whole thing.

    head box                x -4 .. 4     y 24 .. 32     z -4 .. 4
    helmet shell (+1.0)     x -5 .. 5     y 23 .. 33     z -5 .. 5
    the brow anchor         (0, 28, -4)

Front is **negative z**, so this piece builds *forward*, out through the shell's front plane at
`z = -5`. Sitting partly inside the head is normal here and every shipped brow piece does it — what
you must not do is put a face exactly on `z = -5`, `x = ±5`, `y = 23` or `y = 33`.

**One freedom this socket has that the others do not.** The check never compares two pieces of the
same socket, because they are never worn together — so a face of yours sharing a plane with
`nasal`, `visor`, `sallet_slit` or any other `brow` piece is not a coplanar problem and will not be
flagged. The planes you must actually avoid are the shells above, and the pieces on the **other**
sockets of this bone, which ARE worn with you: `dragon_crest` (`crest`, the pack's own, `x ±1.6`,
`y 32.0..36.4`, `z -3.6..3.8`) and `dragon_horns` (`horns`, the pack's own, `x -6.54..-4.00`
mirrored, `y 28.20..36.93`, `z -1.00..2.42`). Both are well behind and above you; you have room.

## Shape

Her face, worn as a visor: **a browplate across the eyes, two ridges over them, and a short snout
tapering forward** — an ender dragon's head read down to six cubes, not a helmet.

- One bone `base` at the anchor (rename the starter `main`; never call a bone `root`; remove the
  starter cube).
- **`plate`**, one cube in `base`, the browplate the rest is built on: `x -4.0 .. 4.0`,
  `y 27.2 .. 29.8`, `z -5.62 .. -5.18`. Thin in z, spanning the face.
- **Two eye ridges**, one cube each in `base`, sitting proud of the plate and angled inward so they
  read as a scowl: `ridge_l` `x -3.6 .. -1.1` and `ridge_r` `x 1.1 .. 3.6`, both
  `y 29.2 .. 30.1`, `z -5.95 .. -5.5`. Give each its own bone if you want to tilt it; a few degrees
  about Z, tips down toward the centreline, is the whole expression.
- **The snout**, two bones off `base`, chained, tapering forward and slightly down:
  - `snout1` — about `x -2.2 .. 2.2`, `y 26.4 .. 28.4`, reaching to about `z -6.9`;
  - `snout2` off `snout1` — narrower and shorter, ending blunt at about `z -7.7`, not a point: she
    has a squared muzzle.
- Six cubes is the budget; seven if the snout earns a third segment.

**Build it straight, then aim it** — place every bone unrotated first, fix whatever the coplanar
check flags on the flat geometry, and only then set the rotations with `element set {rotation}`.
`LESSONS.md` items 1–5 are the arithmetic; the one that bites here is item 3, because the snout is
long in **z** and a droop about X moves its far corners in **y** by `Δz·sinθ`, which is a big number
when `Δz` is 3.7.

**Your envelope budget.** Stay inside `x -4.6 .. 4.6`, `y 25.6 .. 30.4`, `z -7.9 .. -5.05`. The
`z ≤ -5.05` wall is what keeps a face off the helmet's front plane; the `z ≥ -7.9` wall is what
keeps the snout from out-reaching `visor`'s lip (`z -7.76`), the longest thing any brow piece does.

## Sheets

One sheet: `dragon_mask.png`, the **master**, greyscale, its value a position on the wearer's trim
ramp. Alpha is the silhouette and the only source of truth.

Plate, not horn: the browplate flat and mid-grey with a bright `up` edge where the light catches it
and a dark `down`; the two eye ridges brighter than the plate so they read as raised, with their
`down` faces darkest of all — that shadow under the ridge is the whole of the scowl. The snout steps
a little darker as it comes forward so it recedes rather than looming. A ramp of roughly
`55 / 90 / 130 / 175 / 215` across ridge-shadow, snout, plate-body, plate-lit and ridge-top is
enough; a `*` wildcard per cube for a base then per-face overrides is the cheap way to leave nothing
unpainted (`LESSONS.md` item 11). Count your paint calls and say what the face painter did and did
not cover.

## How it is had — read this, it is not a recipe

`pack-line.md` gives this piece **no recipe centre**: the Dragonslayer pack is found in the End, and
only the six pieces with a centre are also craftable. So `reach` will fail until the piece is in the
pack's loot group tag. **Add its id to that file yourself** once the piece is saved:

    packs/dragon/datapack/data/armorpieces_dragon/tags/armorpieces/armor_decoration/dragonslayer.json

It is a plain `{"values": [...]}` list, already holding the pack's other eight, sorted. Add
`"armorpieces_dragon:dragon_mask"` in sorted position. The group itself
(`armorpieces/loot_group/end.json`, 0.15 over `minecraft:chests/end_city_treasure`) already exists
and needs no change.

## Done means

`armorpieces_save` accepted **without** `force`; the tag file updated;
`python tools/check_authoring.py packs/dragon/datapack packs/dragon/resourcepack` clean — including
`reach dragon_mask.json: ok (found)`; the Lessons section below filled in.

Two things this piece does **not** do, because it is not the mod's own:
`python tools/check_part.py` does not work for an out-of-pack piece — the bridge's own check,
printed after every reply, is the check here. And do **not** run `python -m modpage build`: this
pack is not on the mod's page, and there is no `modpage.yml` line to add.

## Lessons from the session

Built as briefed: `base` holding `plate`, then `ridge_l`/`ridge_r` as their own bones and a
two-segment `snout1`→`snout2` chain, five cubes total (no third snout segment needed — two reads
fine at this scale). One paint call covered all 30 faces; no `texture op:rects` needed.

**The pivot placement mattered more than the angle.** The brief says the ridges' pivot can go
either way ("give each its own bone if you want to tilt it"), but "tips down toward the
centreline" only comes out right with the pivot at the **outer** edge, not the inner one I tried
first mentally: with the pivot at the inner edge (near the nose), rotating about Z moves the
*outer* tip, not the inner one — the opposite of a scowl. Pivot at the outer edge (`ridge_l`
origin `(-3.6, 29.65, -5.725)`, rotation `(0,0,-6)`; `ridge_r` mirrored, `(0,0,6)`) put the inner
tips down by about 0.3, which reads as an angry brow. Worth a line in `LESSONS.md`: when a brief
says "tip X moves", check which end sits away from the pivot before picking which edge to pivot
on, not just the rotation's sign.

The snout got a droop the same way: `snout1` at `(0, 27.4, -5.5)` (the plate's front, unrotated)
rotated `(-6,0,0)` about X, `snout2` at `(0, 27.3, -6.9)` (in the parent's *unrotated* local frame,
per the chain-building technique) rotated another `(-6,0,0)` on top, for a cumulative ~12° droop
at the tip. Final envelope (Blockbench frame, converted from the check's game-frame numbers via
`y_bb = 24 − y_game`): `x -4.00..4.00`, `y 26.26..30.10`, `z -7.81..-5.18` — comfortably inside the
brief's budget box (`x -4.6..4.6`, `y 25.6..30.4`, `z -7.9..-5.05`) with no corner-overshoot
surprises, because the rotations were small (6° each) and the cubes short.

The two `!` notes the brief expected (`base's x face at ±4 lies on the body surface`) showed up
exactly as flagged and needed no decision — they're notes, not problems, and `armorpieces_save`
went through without `force`.

Only real friction: `element set` on `ridge_l`/`ridge_r`/`snout1`/`snout2` refused by name
("names 2 elements") because each bone and its one cube share a name, exactly as the brief's
`base`/`main_0` pattern also would have if I hadn't renamed the cube. Fetched `list_outline` once
to get the group uuids and used those instead. Worth adding to `LESSONS.md`: a bone and its cube
sharing a name is common in this workflow (the brief and the plugin both encourage it) and
`element set`/`rename` need a uuid the moment that happens — `list_outline` prints them.
