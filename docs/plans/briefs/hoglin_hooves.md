# Brief: Hoglin Hooves

A piece of **Armor Pieces: Nether** (`armorpieces_nether`), the pack in `docs/plans/pack-line.md`
whose boss is the wither and whose body is the dimension. Read `docs/plans/briefs/LESSONS.md`
first — it is the current technique. **Do not skim other briefs for technique**; the numbers you
need are below.

From the `spurs` row of the Nether table:

> `hoglin_hooves` — cloven hooves at the heels — no fitting — a recipe.

The pack's third hoglin piece, after `hoglin_hair` on the crest. Worn together they are a hoglin's
head and feet on a person, which is the joke the pack is entitled to make once.

## The part

    armorpieces_new
      name:         hoglin_hooves
      anchor:       spurs
      namespace:    armorpieces_nether
      datapack:     C:\Users\Matthijs\ArmorPieces\packs\nether\datapack
      resourcepack: C:\Users\Matthijs\ArmorPieces\packs\nether\resourcepack

Then, before you paint:

    armorpieces_set_part
      name:   "Hoglin Hooves"
      recipe: { centre: "minecraft:crimson_fungus" }

`minecraft:crimson_fungus` is free across the mod and every pack. **No fittings, no static layer, no
effects, no loot row.** One sheet, the greyscale master.

## The rig, in Blockbench coordinates

`spurs` is a **mirrored** socket at the back of the ankles: model **one** side — the **negative x**
side, the left leg — and the game mirrors it.

    left leg box            x  -3.90 ..  0.10    y   0.00 .. 12.00    z  -2.00 ..  2.00
    leggings shell (+0.4)   x  -4.30 ..  0.50    y  -0.40 .. 12.40    z  -2.40 ..  2.40
    boots shell (+0.9)      x  -4.80 ..  1.00    y  -0.90 .. 12.90    z  -2.90 ..  2.90
    the spurs anchor        (-1.9, 2, 2)

The leg bone's pivot is at Blockbench **`y = 12` and `x = -1.9`** — the check answers
`y_local = 12 - y_bb`, `x_local = -x_bb - 1.9`. Both frames are given for the budget.

Front is **negative z**, so the anchor at `z = +2` is **behind** the ankle, which is where this piece
belongs. **Your own shell is the boots**: `x -4.80..1.00`, `z ±2.90`, floor at `y = -0.90`. A face
inside that box is inside the boot and nobody sees it, so the parts of this piece that are meant to
read — the outside of the ring, the hooves — must break out of it. That is exactly how `anklets`
(`x -5.40..1.40`, `z -3.52..3.80`) is built.

**The floor matters here and nowhere else in the pack.** `y = 0` is the sole of the foot. Nothing
goes below `y = 0.05`: a hoof through the floor is worse than a short hoof.

Do not land a face on `x = -4.80`, `x = 1.00`, `x = -4.30`, `x = 0.50`, `z = ±2.90`, `z = ±2.40`,
`y = -0.90`, `y = 0`.

## Shape

A fetlock ring around the ankle, and two cloven hooves hanging behind the heel with a gap between
them. **Three cubes, no rotations** — a hoof pointing straight down and back reads correctly, and
every angle worth having here costs more arithmetic than it returns.

- One bone `base` at the anchor (rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube).

- **`band`**, one cube in `base` — the fetlock ring. It encloses the ankle; its inboard walls are
  inside the leg and never seen, which is how every ring in the mod is built:

        x  -5.12 ..  1.32     y   2.45 ..  3.72     z  -3.18 ..  3.32

- **`hoof_out`**, one cube in `base` — the outer toe, hanging behind the heel:

        x  -3.62 .. -2.22     y   0.12 ..  2.45     z   2.62 ..  4.32

- **`hoof_in`**, one cube in `base` — the inner toe, the same size, with the cleft between them:

        x  -1.98 .. -0.58     y   0.12 ..  2.45     z   2.62 ..  4.32

The gap at `x -2.22 .. -1.98` is the cleft and it is what makes the pair read as cloven. Do not
close it, and do not widen it past a quarter unit either side.

## Envelope budget, in both frames

    Blockbench      x  -5.25 ..  1.45     y   0.05 ..  3.85     z  -3.30 ..  4.45
    check's frame   x  -3.35 ..  3.35     y   8.15 .. 11.95     z  -3.30 ..  4.45

Same-socket pieces, for the heights and depths to place against (never worn together, so never
compared):

| piece | Blockbench |
|---|---|
| `anklets` | x -5.40..1.40, y 0.95..2.20, z -3.52..3.80 |
| `talons` | x -3.40..-0.40, y 0.22..3.50, z 3.00..7.81 |
| `dragon_talons` | x -3.36..-0.49, y 0.77..2.60, z 3.00..4.66 |
| `rowel_spurs` | x -5.15..1.35, y 0.90..3.10, z 0.50..6.20 |
| `bells` | x -6.21..1.35, y 0.21..2.10, z -3.25..4.23 |

`dragon_talons` is the Dragonslayer's heel piece and stops at `z = 4.66`; yours stops at `4.32`,
which is right — a hoof is blunt and a talon is not.

The pieces you are really measured against are the `greaves` and `knees` pieces on the same leg, and
every one of them is in front (`z ≤ -0.41`) or above (`y ≥ 3.75`). `shin_spikes` tops out at
`y = 3.75`, three hundredths above your band; that gap is deliberate, so do not raise the band.

## The sheet

One sheet, `hoglin_hooves.png`, the **master**: greyscale, its value a position on the trim ramp.

Hoof horn and a leather strap — two materials, told apart by value and by how flat they are:

- `band` mid-dark and flat, one value on every face, with the `up` face a step lighter. It is a
  strap and it should sit back.
- The **hooves** are the piece: a `[top, bottom]` gradient down the `north`, `east`, `west` and
  `south` faces from mid at the fetlock to **dark at the tread** — hoof horn is lighter where it
  grows and dark where it wears. The `down` faces (the tread itself) are the darkest values on the
  piece.
- Give each hoof one light pixel line where it meets the band, the way a hoof has a coronet band.
- The two hooves take the **same** values: they are one pair, not a left and a right.

Roughly `35 / 70 / 110 / 150 / 200` from tread to coronet. **One `armorpieces_paint` call for the
whole piece**: a `*` wildcard per cube for the base, then the `[top, bottom]` pairs and the `down`
overrides (`LESSONS.md` 11).

## How it is had

The recipe above, and nothing else. **No loot row and no tag** — the pack has no loot group and no
decoration tag yet, on purpose. `reach` passes on the recipe alone.

## Done means

- [ ] The check is clean, or every `!` still standing is one this brief allows.
- [ ] Envelope inside the budget, **reported in the check's frame**, and nothing below `y = 0.05`.
- [ ] The master painted on every face; nothing but greyscale on it.
- [ ] `armorpieces_save` accepted **without** `force`.
- [ ] `python tools/check_authoring.py packs/nether/datapack packs/nether/resourcepack` clean,
      including `reach hoglin_hooves.json: ok` and the recipe centre unique.
- [ ] The tab closed, and the Lessons section below filled in.

`python tools/check_part.py` does not work on an out-of-pack piece, and `python -m modpage build` is
not this pack's page.

**Allowed to force:** the band's inboard faces being buried or unpainted — that is what a ring
around an ankle is. **Nothing else.**

**Closing the tab is not optional and it is the last thing you do.** The window you are working in is
handed to the next piece's session, and a tab left open is the tab that session finds *active*. Call
`armorpieces_close` when you are done — and also when you are **not** done: if you abandon this piece
or stop to ask a question, close it first (`discard: true` if it should not be kept) and say in your
report what you left behind in the pack folders.

## Lessons from the session

Built exactly as specified: `base` bone at the spurs anchor, three unrotated cubes (`band`,
`hoof_out`, `hoof_in`) at the brief's coordinates, one master sheet. Painted in one
`armorpieces_paint` call — `band.*` at 100 with `band.up` lightened to 140, each hoof's four side
faces as a `[140, 35]` top-to-bottom gradient (fetlock to tread), `up` at 140, `down` (the tread)
at the darkest value 35, and a 16-texel `pixels` overlay at value 200 for the coronet line at the
top row of each hoof's four side faces — all in the same call as the whole-face map, per LESSONS
11a. The gradient worked as a plain `[top, bottom]` with no `pixels`-per-column workaround (unlike
LESSONS 19's warning): the hoof cubes' Y dimension (2.33) is the longest of the three, so box-UV's
face height axis lined up with the physical top-to-bottom I wanted, not the shortest axis.

No `!` accepted — the check came back "ok: nothing needs a decision" after paint, so the brief's
allowance (forcing the band's inboard faces) was never needed; the band's outward faces are all
visible and got painted normally, and its inboard walls landed inside the leg where box-UV simply
never generated a face rectangle for them to begin with (there's only one box, not two rings), so
there was nothing to force. The many `OVERLAP` lines against `greaves`/`knees`/`tassets` pieces on
the same bone are hull-test notes (LESSONS 8) and were left standing.

Confirmed the `FileNotFoundError: ... part.bbmodel` status-write race from LESSONS 14 fires after
`armorpieces_paint` too, not just after `armorpieces_check` — a no-op `element set {visibility}`
cleared it before paint, and it also showed up harmlessly after `armorpieces_save` itself (the
save had already completed and reported the recipe correctly; the stale status write is cosmetic
regardless of which call triggers it).

`python tools/check_authoring.py packs/nether/datapack packs/nether/resourcepack` reports
`hoglin_hooves.json` clean on every line (roundtrip, data, recipe, reach — all "ok"); the script's
overall exit code is 1 only because a pre-existing, unrelated piece in the same pack
(`wither_mask`) has no recipe/loot/tag yet. That is not this brief's problem to fix.
