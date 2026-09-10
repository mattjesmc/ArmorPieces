# Brief: Wither Mask

A piece of **Armor Pieces: Nether** (`armorpieces_nether`), the pack in `docs/plans/pack-line.md`
whose boss is the wither and whose body is the dimension. Five pieces exist (`blaze_bracers`,
`blaze_halo`, `ghast_tendrils`, `hoglin_hair`, `strider_hair`); you are the sixth, and the first of
the three the wither itself drops.

Read `docs/plans/briefs/LESSONS.md` first — it is the technique the earlier sessions worked out,
distilled and current. **Do not skim other briefs for technique**; most of them were written against
a bridge that no longer exists. Open another brief only for a neighbour's numbers, and the numbers
you need are already below.

From the `brow` row of the Nether table:

> `wither_mask` — the skull's face over your own — no fitting — dropped by the wither.

**`wither_mask` and `wither_heads` worn together are the wither's three heads, with yours in the
middle.** That is the pack's hero idea, and this is the middle head. Build it as a face, not as a
helmet: the player's own head is inside it.

## The part

    armorpieces_new
      name:         wither_mask
      anchor:       brow
      namespace:    armorpieces_nether
      datapack:     C:\Users\Matthijs\ArmorPieces\packs\nether\datapack
      resourcepack: C:\Users\Matthijs\ArmorPieces\packs\nether\resourcepack

**Name the namespace and both pack folders explicitly** or the piece is written into the mod.

Then, before you paint:

    armorpieces_set_part
      name: "Wither Mask"
      loot: [ { table: "minecraft:entities/wither", weight: 1, chance: 1.0 } ]

**No fittings, no static layer, no effects, and no recipe.** One sheet, the greyscale master. The
reply will say `static_created: false` and `sheets_created: []`; that is correct. Set the part data
anyway — it is the step that writes the data half and the language line.

## The rig, in Blockbench coordinates

`brow` is **not** a mirrored socket: one attachment, on the front of the head, and you model the
whole thing.

    head box                x  -4.00 ..  4.00    y  24.00 .. 32.00    z  -4.00 ..  4.00
    helmet shell (+1.0)     x  -5.00 ..  5.00    y  23.00 .. 33.00    z  -5.00 ..  5.00
    the brow anchor         (0, 28, -4)

The head bone's pivot is at Blockbench `y = 24`, so the check's own frame (bone-local, +Y down) is
`y_local = 24 - y_bb` on this bone. Both frames are given for every budget below; do not convert.

Front is **negative z**, so this piece builds *forward*, out through the helmet's front plane at
`z = -5`. Sitting partly inside the head is normal here and every shipped brow piece does it. What
you must not do is land a face exactly on `z = -5`, `x = ±5`, `y = 23` or `y = 33`.

**The freedom this socket has.** The check never compares two pieces of the same socket, because
they are never worn together — a face of yours sharing a plane with `bone_mask`, `visor` or any
other `brow` piece is not a problem and will not be flagged. The planes that matter are the shells
above and the pieces on the **other** sockets of the head, which ARE worn with you. The pack's own
are `hoglin_hair` (`crest`: `x -0.55..0.55`, `y 32.03..34.65`, `z -3.03..4.33`) and `strider_hair`
(`horns`, mirrored: `x -7.25..-4.16`, `y 25.32..31.66`, `z -1.60..1.60`). Both are above you or
behind your cheek line; `strider_hair` is the one to watch, because its `z` range meets yours if you
grow sideways past `x = ±4.2`.

## Shape

A wither skeleton's skull, flattened onto the face: **a broad faceplate, a heavy brow shelf over
two black sockets, a squared jaw pushed forward, and a narrow nose ridge between the eyes.** Four
cubes. **No rotations anywhere in this piece** — a skull's face is flat, and every angle you might
want is a paint value instead. If you find yourself computing a sine, re-read this line.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, `list_outline` gives the uuid
  (`LESSONS.md` 7b).

- **`faceplate`**, one cube in `base` — the skull's front, standing off the helmet:

        x  -4.10 ..  4.10     y  25.60 .. 31.30     z  -5.85 .. -5.15

- **`browridge`**, one cube in `base` — the shelf that makes the sockets read as holes:

        x  -4.10 ..  4.10     y  29.90 .. 31.05     z  -6.45 .. -5.85

- **`jaw`**, one cube in `base` — narrower than the face, pushed forward under it:

        x  -2.70 ..  2.70     y  25.10 .. 26.75     z  -6.45 .. -5.85

- **`nose`**, one cube in `base` — the thin central ridge between the eye sockets:

        x  -0.75 ..  0.75     y  27.40 .. 29.90     z  -6.15 .. -5.85

Four cubes is the budget. A fifth only if you want a chin block under `jaw`, and only inside the
envelope below.

## Envelope budget, in both frames

    Blockbench      x  -4.30 ..  4.30     y  25.00 .. 31.40     z  -6.60 .. -5.05
    check's frame   x  -4.30 ..  4.30     y  -7.40 .. -1.00     z  -6.60 .. -5.05

The check prints the envelope **bone-local, +Y down, from the head's pivot at `y = 24`**. Compare
against the second line; converting the first by hand is where this goes wrong.

The `z ≤ -5.05` wall keeps every face off the helmet's front plane. The `z ≥ -6.60` wall is
deliberately short of `visor` (`z -7.76`) and `frog_mask` (`-7.25`): a wither skull is flat, not a
snout, and a mask that reaches as far forward as a muzzle stops reading as a skull.

Same-socket pieces, for the heights and depths to place against (never compared, so never a
problem):

| piece | Blockbench |
|---|---|
| `bone_mask` | x -4.10..4.10, y 26.50..31.25, z -6.10..-5.10 |
| `frog_mask` | x -5.50..5.50, y 25.25..31.75, z -7.25..-5.25 |
| `sallet_slit` | x -4.00..4.00, y 26.00..31.00, z -5.60..-5.10 |
| `great_helm` | x -4.00..4.00, y 23.25..30.25, z -5.35..-4.50 |

`bone_mask` is the closest relative in the mod and its numbers are why yours look as they do: it is
the same idea done as a skull *helmet*; yours is one face, deeper and heavier at the brow.

## The sheet

One sheet, `wither_mask.png`, the **master**: greyscale, its value a position on the wearer's trim
ramp. Alpha is the silhouette and the only source of truth.

A wither skull is charred bone — dark, and lit only on its edges. Work down from the brow:

- `browridge` is the brightest thing on the piece: its `up` face near-white, its `north` face a
  strong light, its `down` face (the underside that shades the sockets) the darkest value you use.
- The **eye sockets** are painted, not modelled: two black rectangles on the faceplate's `north`
  face under the brow, roughly two units wide and one and a half tall, their inner edges about a
  unit either side of the nose. Black here means near-zero, not transparent — the silhouette stays
  solid.
- `faceplate` mid-dark everywhere else, a touch lighter down the cheeks than at the temples.
- `jaw` slightly lighter than the faceplate so it comes forward, with a row of light teeth painted
  across the top of its `north` face where it meets the shadow.
- `nose` darkest at its sides, mid on its `north` face.

A ramp of about `20 / 60 / 95 / 140 / 195 / 235` across sockets, temples, faceplate, jaw, brow-lit
and teeth is enough. **One `armorpieces_paint` call for the whole piece** — a `*` wildcard per cube
for a base, then the faces that differ, then the two socket rectangles with `texture op:rects` if
the face painter cannot place them (`LESSONS.md` 11). Say in your report what the face painter
covered and what needed rectangles.

## How it is had

The wither drops it: the `loot` row above, `chance 1.0`, `weight 1`. **There is no recipe and no
tag.** The pack has no loot group and no decoration tag yet, on purpose — the pieces built so far
are recipe-only and a tag naming nothing would fail a check. Do not create one.

The three wither pieces all offer `minecraft:entities/wither` at chance 1.0 and weight 1. The mod
resolves one table to **one pool, rolled once**, so a wither drops exactly one of the three and the
weights decide which. That is intended: three kills, on average, for the set.

## Done means

- [ ] The check is clean, or every `!` still standing is one this brief allows.
- [ ] Envelope inside the budget above, and **reported in the check's frame**.
- [ ] The master painted on every face; nothing but greyscale on it.
- [ ] `armorpieces_save` accepted **without** `force`.
- [ ] `python tools/check_authoring.py packs/nether/datapack packs/nether/resourcepack` clean,
      including `reach wither_mask.json: ok`.
- [ ] The tab closed, and the Lessons section below filled in.

Two things this piece does **not** do, because it is not the mod's own: `python tools/check_part.py`
does not work for an out-of-pack piece — the bridge's own check, printed after every reply, is the
check here; and do **not** run `python -m modpage build`, because this pack is not on the mod's page.

**Allowed to force:** nothing. If an `!` stands that this brief did not predict, stop and say so
rather than forcing it.

**Closing the tab is not optional and it is the last thing you do.** The window you are working in is
handed to the next piece's session, and a tab left open is the tab that session finds *active*. Call
`armorpieces_close` when you are done — and also when you are **not** done: if you abandon this piece
or stop to ask a question, close it first (`discard: true` if it should not be kept) and say in your
report what you left behind in the pack folders.

## Lessons from the session

**Built clean on the second attempt.** The bridge fault the first session hit (`LESSONS.md`
§17–18) was already fixed in the launcher by the time this session ran — `get_project_info` right
after `armorpieces_new` answered normally, and the whole piece went in without any raw-bridge
fallback. `armorpieces_pieces` confirmed the previous session's discard had left nothing behind:
no `wither_mask` files existed anywhere under `packs/nether`, so this session created it fresh
rather than overwriting stale starter content.

The brief's four cubes, coordinates and envelope were exact — no adjustment needed. One
`place_cube` call built `faceplate`, `browridge`, `jaw` and `nose` together (all reported
`touching`, none `overlap`), and one `armorpieces_paint` call did the whole sheet: `*` wildcards
per cube for the ramp bases (faceplate 95, browridge 195, jaw 140, nose 95), face overrides for
the temples (`faceplate.east`/`west` and `nose.east`/`west` at 60), a `[90, 110]` gradient on
`faceplate.north` for the cheeks reading lighter toward the jaw, `browridge.up`/`down` at 235/20
for the lit brow and its dark underside, and `pixels` in that same call for the two eye sockets
(3×2 texels each, value 12, read off `faceplate.north`'s own face rectangle `1,1 9x6` by hand —
inner edge ~1 unit from the nose, ~2 units wide, landed at abs texels x2–4 and x7–9, y2–3) and the
teeth row (`jaw.north`'s top row, x47–52 y1, value 235). That is `LESSONS.md` 11a exactly: one
`armorpieces_paint` call, faces plus pixels together, no `texture op:rects` needed at all —
contrary to the brief's fallback suggestion, the face painter's own `pixels` list placed the
sockets fine once the face rectangle gave the addressing.

`armorpieces_check` came back `ok: nothing needs a decision` on the first try after painting (one
`FileNotFoundError` from a stale status file between the paint call and the first check, fixed per
`LESSONS.md` 14 with a no-op `element set {visibility: true}`). Envelope: `x -4.10..4.10
y -7.30..-1.10 z -6.45..-5.15` (check's frame), inside the brief's budget on every axis. Saved
without `force`. `tools/check_authoring.py packs/nether/datapack packs/nether/resourcepack` is
clean, `reach wither_mask.json: ok (found)` among it.

**For the wither pieces after this one:** the bridge is healthy again as of 2026-09-09; do not
assume §17–18's fault still stands, just confirm with one `get_project_info` and move on if it
answers.
