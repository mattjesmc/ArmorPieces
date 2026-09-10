# Brief: Crystal Pendant

A piece of **Armor Pieces: Dragonslayer** (`armorpieces_dragon`), the first pack of the line in
`docs/plans/pack-line.md` — netherite plate with amethyst light, every piece a part of her or of the
End around her. Read `docs/plans/briefs/LESSONS.md` first — it is the current technique. **Do not
skim other briefs for technique**; the numbers you need are below.

From the `collar` row of the Dragonslayer table:

> `crystal_pendant` — a caged end crystal at the throat — fitting `gemstone` — centre `end_crystal`.

This is the pack's one **gemstone** piece: the caged crystal takes the player's chosen gem, so the
same pendant is amethyst on one player and emerald on another. Everything else on the piece is iron
cage and cord, and must stay out of the gem's way.

## The part

    armorpieces_new
      name:         crystal_pendant
      anchor:       collar
      namespace:    armorpieces_dragon
      datapack:     C:\Users\Matthijs\ArmorPieces\packs\dragon\datapack
      resourcepack: C:\Users\Matthijs\ArmorPieces\packs\dragon\resourcepack

**Name the namespace and both pack folders explicitly** or the piece is written into the mod.

Then, before you paint:

    armorpieces_set_part
      name:     "Crystal Pendant"
      fittings: [ "armorpieces:gemstone" ]
      recipe:   { centre: "minecraft:end_crystal" }

That call creates `part_gemstone`, the mask sheet, and writes the template recipe.
`minecraft:end_crystal` is a flat item and is free across the mod and every pack. **No static layer,
no effects, no loot row.**

## The rig, in Blockbench coordinates

`collar` is **not** a mirrored socket. One attachment at the base of the throat, and you model the
whole thing.

    body box                x  -4.00 ..  4.00    y  12.00 .. 24.00    z  -2.00 ..  2.00
    chestplate shell (+1.0) x  -5.00 ..  5.00    y  11.00 .. 25.00    z  -3.00 ..  3.00
    leggings shell (+0.5)   x  -4.50 ..  4.50    y  11.50 .. 24.50    z  -2.50 ..  2.50
    the collar anchor       (0, 23, -2)

The body bone's pivot is at Blockbench `y = 24`, so the check's frame is `y_local = 24 - y_bb`.

Front is **negative z**. Your own shell is the **chestplate**, whose front wall is `z = -3`:
everything must sit in front of that (more negative) or it is buried. `z = -3.00` is the plane that
would be an outright `!`.

Do not land a face on `z = ±3`, `z = ±2.50`, `x = ±5`, `x = ±4.50`, `y = 25` or `y = 11`.

## Shape

A band across the throat, a short link, and a caged crystal hanging below it: two uprights and two
caps around a single gem cube. Seven cubes. **No rotations** — a pendant hangs straight, and the
cage is square because the crystal inside it is not.

- One bone `base` at the anchor (rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube).

- **`band`**, one cube in `base` — the collar the pendant hangs from:

        x  -3.25 ..  3.25     y  22.35 .. 23.15     z  -3.55 .. -3.05

- **`link`**, one cube in `base` — the short drop between band and cage:

        x  -0.35 ..  0.35     y  21.55 .. 22.35     z  -3.75 .. -3.45

- **`crystal`**, one cube in `base` — **the gem, and the whole of the `gemstone` mask**:

        x  -0.95 ..  0.95     y  19.35 .. 21.25     z  -3.95 .. -3.15

- **The cage**, four cubes in `base`, standing 0.1 proud of the crystal on every side so it reads as
  metal around glass:

        bar_l       x  -1.25 .. -0.95     y  19.05 .. 21.55     z  -4.05 .. -3.05
        bar_r       x   0.95 ..  1.25     y  19.05 .. 21.55     z  -4.05 .. -3.05
        cap_top     x  -1.25 ..  1.25     y  21.25 .. 21.55     z  -4.05 .. -3.05
        cap_bottom  x  -1.25 ..  1.25     y  19.05 .. 19.35     z  -4.05 .. -3.05

Seven cubes is the budget. If you want it simpler, the two caps are the pair to drop — never the
bars, which are what hold the gem visually.

## Envelope budget, in both frames

    Blockbench      x  -3.35 ..  3.35     y  18.95 .. 23.25     z  -4.15 .. -3.02
    check's frame   x  -3.35 ..  3.35     y   0.75 ..  5.05     z  -4.15 .. -3.02

Same-socket pieces, for the heights and depths to place against (never worn together, so never
compared):

| piece | Blockbench |
|---|---|
| `pendant` | x -3.39..3.39, y 19.00..24.46, z -3.85..-3.10 |
| `fang_necklace` | x -3.20..3.20, y 21.10..24.30, z -3.90..-3.05 |
| `nautilus_gorget` | x -3.00..3.00, y 16.85..25.05, z -4.45..-3.15 |
| `chain_of_office` | x -4.22..4.22, y 16.80..23.44, z -4.60..-2.60 |
| `flower_brooch` | x -4.74..0.74, y 17.02..23.33, z -5.04..-3.15 |

`pendant` is the mod's lapis drop on a cord and the closest relative; yours is the same silhouette
with a cage on it and hangs a little shorter and a little deeper. Do not out-hang it: below
`y = 19` a pendant starts colliding with what a `belt` piece does.

The pieces you are really measured against are the `back` and `belt` pieces on the same body bone,
and all of them are behind you or below `y = 16.5`. You have this space to yourself.

## The sheets

**`part` (master), greyscale.** Its value is a position on the trim ramp, and for the crystal it is
also what the gemstone material is modulated against — so **do not black the crystal out**. Paint
it a **mid to light value**, flat, on every face: a dark master under a gemstone mask makes the gem
read as a hole. (The mod has never had a piece that masks over a light master, and this is the
piece that settles what it looks like.)

- `crystal` flat mid-light on all six faces, the `north` face a step lighter than the sides.
- `bar_l`, `bar_r`, `cap_top`, `cap_bottom` — iron: mid-dark, with each bar's outer face a step
  lighter than its inner one. The cage must be plainly darker than the gem it holds.
- `band` mid-dark and flat, with a light `up` edge.
- `link` the darkest thing on the piece.

Roughly `55 / 85 / 120 / 175 / 205` from link to crystal.

**`part_gemstone` (mask), greyscale.** The `crystal` cube and **nothing else** — all six faces, one
flat mid value. Nothing on the cage, nothing on the band, nothing on the link. A mask pixel outside
the master's silhouette is a `!`, so paint the mask by face rather than by rectangle.

## How it is had

The recipe above. The pack's loot group also names the pack's tag, so **add this piece's id to the
tag file** once it is saved — the pack's craftable pieces are in it too, and being in both is how
the End's chests can also produce it:

    packs/dragon/datapack/data/armorpieces_dragon/tags/armorpieces/armor_decoration/dragonslayer.json

A plain `{"values": [...]}` list, already holding the pack's other pieces, sorted. Add
`"armorpieces_dragon:crystal_pendant"` in sorted position and write it back as
`JSON.stringify(value, null, 2) + "\n"`. The group itself (`armorpieces/loot_group/end.json`) needs
no change.

## Done means

- [ ] The check is clean, or every `!` still standing is one this brief allows.
- [ ] Envelope inside the budget, **reported in the check's frame**.
- [ ] Both sheets painted: master everywhere, `part_gemstone` on `crystal` only.
- [ ] The tag file updated.
- [ ] `armorpieces_save` accepted **without** `force`.
- [ ] `python tools/check_authoring.py packs/dragon/datapack packs/dragon/resourcepack` clean,
      including `reach crystal_pendant.json: ok (found)` and the recipe centre unique.
- [ ] The tab closed, and the Lessons section below filled in.

`python tools/check_part.py` does not work on an out-of-pack piece, and `python -m modpage build` is
not this pack's page.

**Allowed to force:** nothing. If an `!` stands that this brief did not predict, stop and say so
rather than forcing it.

**Closing the tab is not optional and it is the last thing you do.** The window you are working in is
handed to the next piece's session, and a tab left open is the tab that session finds *active*. Call
`armorpieces_close` when you are done — and also when you are **not** done: if you abandon this piece
or stop to ask a question, close it first (`discard: true` if it should not be kept) and say in your
report what you left behind in the pack folders.

## Lessons from the session

Built exactly as specified: `base` bone at the collar anchor, seven cubes (`band`, `link`, `crystal`,
`bar_l`, `bar_r`, `cap_top`, `cap_bottom`), no rotations. The brief's coordinates dropped straight in
with no fixups — every cube's envelope came back `touching` or `clear` against its neighbours on the
first `place_cube` call, and the whole-piece check was `ok: nothing needs a decision` before any paint
existed for the unpainted-face warning to even need clearing later.

Master values used: link 55 (flat, darkest) · cage 85 base with the bars' outboard face (`bar_l.west`,
`bar_r.east`, per LESSONS #12) lifted to 105 · band 120 base with a 150 `up` edge · crystal 175 base
with `north` lifted to 205. The brief's "roughly 55/85/120/175/205" turned out to be five anchor
points across seven tonal slots (link; cage inner/outer; band base/edge; crystal base/north), not one
value per cube — I read it as anchors and interpolated the two "a step lighter" steps (105, 150)
between them, which kept everything monotonic link < cage < band < crystal as the brief asked.

**What a gemstone mask over a light master looks like:** painted `part_gemstone` as a single flat 140
on all six `crystal` faces, nothing on the cage/band/link (mask sheets default to unpainted =
transparent = fitting has no effect there). The master under it is 175/205 — mid-light, per the
brief's instruction not to black the crystal out. This is the first piece to pair a masked fitting
with a light master rather than a dark one; whether it reads right in-game (the gemstone material
modulating a light base rather than a dark one) still wants a screenshot or an in-game look, which
this session didn't spend — the check has no way to judge material rendering, only silhouette and
paint coverage.

Envelope landed at x -3.25..3.25, y 0.85..4.95, z -4.05..-3.05 in the check's frame — inside the
brief's budget box on every axis, and shorter/shallower than `pendant`'s as the brief predicted.

No `!` stood at any point; nothing was forced. `armorpieces_save` accepted without `force`.
`check_authoring.py` on the pack exits 1, but only for `dragon_claws.json` — a different piece another
concurrent session was mid-building in the same window (no recipe/loot/tag yet, "the part cannot be
had in survival"). Not this piece's file, not touched.

**Shared-window confirmation of LESSONS #20:** the first `armorpieces_open`/`armorpieces_check` pair
on this piece answered with `dragon_claws`' report (a concurrent session's piece, same Blockbench
window) even though the reply's own JSON said `"piece":"armorpieces_dragon:crystal_pendant"`. Calling
`armorpieces_open` on my own piece name again immediately before the next call snapped it back, and
it held correctly for the rest of the session — but `mcp__mcptoolkit__get_project_info` showed my
session was bound to the right project (`bound:true`) the whole time, meaning the mismatch was in
`armorpieces_check`'s status-file publish (whichever tab last became active in the real UI), not in
the mcptoolkit binding. Worth adding to LESSONS explicitly: **the mcptoolkit tools (`place_cube`,
`list_outline`, `element`, …) stayed correctly bound to my session throughout, even while
`armorpieces_check`'s narration was showing a sibling session's piece** — so an edit landing on the
wrong piece and a check *reporting* the wrong piece are different failure modes, and `get_project_info`
is the cheap way to tell which one you're looking at before you distrust a whole edit.
