# Brief: Varangian — the Norse harness

A tenth-century northern warrior: a **spangenhelm** — a conical helmet built from four panels held
by bright ribs, with a nasal bar down the front and a mail curtain hanging beside the face — a mail
**byrnie** over the body, a heavy fur collar at the neck, a broad belt, and **winingas**, the long
woollen strips wound spiralling up the leg.

**What has to tell it apart from the two mail skins already drawn.** `mail` is a harness of riveted
mail over a gambeson, and `chainmail` (not yet drawn) is vanilla's own weave. If this skin is only a
weave it is a duplicate and the session has failed. Four things carry it, and none of them is the
weave:

1. the **nasal bar** — one bright vertical bar in the middle of the face opening;
2. the **ribs** on the helmet, four bright verticals dividing four darker panels;
3. the **fur collar** — a broken, irregular light-and-dark band across the top of the chest, the
   only soft edge in the whole set;
4. the **winingas** — a diagonal barber-pole wrap down the leg, a direction nothing else uses.

Draw those four hard. The mail between them is a quiet field, not the subject.

## What is already done

Both sheets are seeded with **vanilla netherite's exact silhouette at a flat `8`**. Every texel
vanilla paints already carries paint: the crown, the cheek strips beside the face, the six-row
sleeve, the belt row, the sole. The vertical zoning is vanilla's own, so there is nothing to decide
about rows, hems or how far down a boot goes. Netherite is the seed because it is the only vanilla
set that wraps the cheeks — and those cheek strips are exactly where a spangenhelm's mail curtain
hangs.

## The rules, all of them enforced

1. **Every stamp shades and nothing else.** Paint aimed at a texel outside the silhouette is dropped
   before it lands, and the reply tells you how many. You cannot break the outline — and you cannot
   extend it either, so do not try. Do not use `.`; it does nothing here.
2. **Level `8` is reserved for "not yet drawn".** The check counts every texel still at `8` and the
   save is refused while any remain. Never use `8` as a value.
3. **Bands four to five levels apart.** Your ladder is `2` shadow, `6` mid-dark, `a` mid-light,
   `e` highlight, with `4` and `c` as half steps and `0`/`f` at the extremes. A step of one or two
   levels can bake *identical* on some materials. `python tools/bake_skin.py --levels` prints why,
   `--pair 6 a` checks any pair you fancy.
4. The usual: no paint over the face window (the silhouette already leaves it open), leave
   `helmet_raised` alone, reach at least 6 of the 8 ramp shades.

**One measured fact you will need.** A two-value weave in `2`/`6`/`a` reads *better* on chainmail
than on iron, because chainmail's ramp is dead only in the middle. A weave built out of `6` and `a`
alone will be mush on some materials — put `2` in it.

## The silhouette you are shading

`#` carries paint and must end up shaded; `.` is outside the outline and will be dropped. Rows are
numbered from the top of each face. This is the seed, so you do not need to read the sheets back.

    helmet  (humanoid)
            front     back      left      right     top
      row 0 ########  ########  ########  ########  ########
      row 1 ########  ########  ########  ########  ########
      row 2 ########  ########  ########  ########  ########
      row 3 #..##..#  ########  ########  ########  ########
      row 4 #..##..#  ########  ##..####  ####..##  ########
      row 5 #......#  ########  #.......  .......#  ########
      row 6 ##....##  ..####..  #.......  .......#  ########
      row 7 ##....##  ........  #.......  .......#  ########

    chest  (humanoid)                          arm  (humanoid)
            front     back      left  right            front  back  left  right  top
      row 0 ##....##  ########  ####  ####      row 0 ####  ####  ####  ####  ####
      row 1 ##....##  ########  ####  ####      row 1 ####  ####  ####  ####  ####
      row 2 ###..###  ########  ####  ####      row 2 ####  ####  ####  ####  ####
      row 3 ########  ########  ####  ####      row 3 ####  ####  ####  ####  ####
      row 4 ########  ########  ####  ####      row 4 ####  ####  ####  ####
      row 5 ########  ########  ####  ####      row 5 ####  ####  #..#  ####
      row 6 ########  ########  ####  ####      row 6 #.#.  .#..  ....  .##.
      row 7 ########  ########  ####  ####
      row 8 ########  ########  ####  ####      boot  (humanoid)
      row 9 ########  ########  ....  ....            front back  left  right bottom
      row10 .######.  .######.  ....  ....      row 0 ....  ....  ....  ....  ####
      row11 ..####..  ..####..  ....  ....      row 1 ....  ....  ....  ....  ####
                                                row 2 ....  ....  ....  ....  ####
    waist  (humanoid_leggings)                  row 3 ....  ....  ....  ....  ####
            front     back      left  right     row 6 ####  ....  #...  ...#
      row 7 ..####..  ########  ..##  ##..      row 7 ####  ####  ####  ####
      row 8 ########  ########  ####  ####      row 8 ####  ####  ####  ####
      row 9 ########  ########  ####  ####      row 9 ####  ####  ####  ####
      row10 ########  ########  ####  ####      row10 ####  ####  ####  ####
      row11 ########  ########  ####  ####      row11 ####  ####  ####  ####

    leg  (humanoid_leggings): front/back/left/right rows 0..8 full, top full.

**`helmet.front` cols 3 and 4 at rows 3..4 are a separate island in the middle of the face window.**
That is your nasal bar, handed to you by the silhouette. It is four texels and it is the single most
recognisable thing in this skin — make it the brightest value on the sheet.

## The armour, net by net

**helmet — the spangenhelm.** Four panels, four ribs, a nasal, a mail curtain.

- `front` rows 0..2: ribs at cols 0 and 7 at `e`, panel `6` across cols 1..6, and cols 3 and 4 at
  `a` so the eye is led down into the nasal.
- `front` rows 3..4, cols 3 and 4: **the nasal**, `e` — flat, bright, no shading inside it.
- `front` rows 3..7, the outer columns: the mail curtain beside the face. `6` and `2` alternating
  down each column, a hanging weave rather than a plate.
- `back` rows 0..5: the same panels and ribs, one band darker — ribs `a`, panel `4`.
- `back` row 6 (cols 2..5): the curtain at the nape, `2` with `6` interleaved.
- `left`/`right` rows 0..4: panel `6` with a rib `a` on the column nearest the front, so the four
  ribs meet correctly at the crown.
- `left`/`right` rows 5..7 (one column each): the curtain, `6`/`2` alternating.
- `top`: a cone seen from above — outer ring `6`, next ring in `a`, the middle four texels `e`, and
  the four ribs read out to the corners at `c`.

**chest — the byrnie and the fur.**

- Rows 0..2 are the **fur collar**. Not a band: a *broken* one. Give it `e`, `a`, `4` and `c` in an
  irregular order across the row, changing between the rows, so the edge reads as shaggy. This is
  the only place in the mod's whole skin set where a value is allowed to be noisy — everywhere else,
  noise is a mistake.
- Rows 3..9: the mail. `tile: ["6a6a6a6a", "a26a26a2"]` or your own two-line weave — it must carry a
  `2` somewhere or it dies on the flatter materials. The weave runs identically on front, back and
  both sides; the byrnie is not lit differently by side.
- Row 9 across, and rows 10..11 on the narrowing tail: the byrnie's skirt. Same weave one band
  darker, with row 11 at `2`.
- `chest.back` the same, with the collar rows a band darker.

**arm — the mail sleeve.** The same weave, rows 0..6, with rows 0..1 lifted one band (`a`/`e`
instead of `6`/`a`) so the shoulder catches light and the sleeve is not a flat tube. `arm.top` at
`a`, weave included.

**waist — the belt.** Row 7 is a broad leather belt: `e` on the front's four texels and the sides,
`c` across the back, with a `2` line at row 8 underneath it so the belt stands off the byrnie.
Rows 9..11: the weave again, ending at `2`.

**leg — the winingas.** This is the second signature and it is one stamp.

A spiral wrap is a diagonal, and the tool draws diagonals for you: `tile: ["a662"]` with
`shift: 1` on each of `front`, `back`, `left` and `right` gives a barber-pole running the same way
round the whole leg. Rows 0..8; rows 6..8 vanish under the boot so do not fuss them.
`leg.top` at `6`.

Use the same `shift` on all four faces or the wrap will change direction at the corners and read as
noise.

**boot — the turnshoe.** A soft leather shoe, no plate at all: `6` field on rows 7..11, `2` at row
11 as the welt, and `a` on the front's rows 7..8 as the lit instep. `boot.bottom` (the sole) at `4`,
plain — a leather sole has no nails.

## What to do

One `armorpieces_skin_paint` call per sheet, a stamp per face; `fill` for a flat face, `tile` (with
`shift` for the winingas) for anything repeating, `rows` for the hand-placed work — the fur collar,
the nasal and the ribs. Compose the arithmetic in your reply text *before* the call.

Look at it on iron, gold and netherite before saving — judge the dark end on netherite, the
mid-tones on iron, never on the greyscale master. **Six pictures is the budget** and every one is
re-sent on every later turn, so take them where they can still change what you draw.

## Done means

`armorpieces_save_skin` accepted without `force`; `python tools/check_skin.py varangian` clean;
`python tools/bake_skin.py varangian --out build/skins`; and all four signatures — nasal, ribs, fur,
winingas — still legible on iron, gold and netherite. The winingas is the one at risk: a diagonal
made of a two-level step will turn into a flat field on some materials, so check it and say so.

## Lessons from the session

**Value ladder used:** `2` shadow, `4`/`6` mid, `a` mid-light, `c` half-step, `e`/`f` highlight —
the nasal was pushed to `f` (not the `e` the brief suggested) so it stayed uniquely the brightest
texel on the whole sheet, distinct from the helmet-top apex and the rib highlights which stayed at
`e`. Reached 6/8 ramp shades (0-stop and 8-stop unused by design — 8 is reserved, and nothing
needed true black). Mail weave was `6a6a6a6a`/`a26a26a2` throughout, lifted to `aeaeaeae`/`e2ae2ae2`
for the shoulder (arm rows 0-1 and arm.top), and darkened to a plain `2`/`6` alternation for the
byrnie's skirt (chest rows 9-10) with row 11 flat `2`.

**`tile` + `shift` on the winingas worked cleanly.** One `{tile: ["a662"], shift: 1}` stamp per leg
face (front/back/left/right, same tile and same shift on all four) gave a continuous diagonal that
does not break direction at the corners — exactly as the brief predicted. On netherite the `a`/`6`/`2`
spread (79/48/19 baked) reads clearly as a barber pole even at the small size the boots reach; this
was the one signature I checked closest with a dedicated legs-camera shot, and it held up. Nothing
about it needs revisiting for the next diagonal-pattern skin.

**Reading the seed sheet directly (`armorpieces_skin_sheet`) beat parsing the brief's ASCII table.**
The brief's cramped two-column layout (chest table next to arm table, same lines) made one row -
arm's row 5 - look like it had a 5th "top" token when it didn't; the sheet dump resolved it in one
free text call with zero ambiguity. For any skin with an asymmetric or oddly-cut net (the arm's
top face ending at row 3 while front/back/left/right run to row 11), read the sheet before trusting
the brief's row table to the character - it costs nothing and the table format doesn't always survive
being column-packed.

**One thing the tools didn't tell me:** the paint reply reports texels dropped for landing off the
silhouette, but not *which* rows - on a net with a partial per-row cutout (chest.front's tapering
tail, the waist's row-7 belt cutout) I had to work out from the sheet dump which columns survived
in each row rather than being told. A per-face "n dropped in rows X..Y" breakdown would have saved
the manual column-slicing.

**What read fine without a fight:** the fur collar's forced irregularity (`e`/`a`/`4`/`c` on front,
one step darker `a`/`6`/`2`/`c` on back) was legible as a broken band on all three materials without
needing a repaint - the brief's warning that noise is normally a mistake elsewhere in the skin set
made it easy to keep this the *only* noisy region and not let it creep into the mail. The nasal's
four-texel island needed no special handling beyond writing `f` into the two center columns of rows
3-4; the silhouette did the framing for free.
