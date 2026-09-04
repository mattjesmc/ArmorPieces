# Brief: Lorica — the Roman legionary harness

*Lorica segmentata*: a cuirass built of wide iron hoops that wrap the body one above the other, a
stack of smaller lames over each shoulder, a `galea` helmet with a flared neck flange and cheek
plates, an apron of hanging leather strips at the belt, and hobnailed `caligae` on the feet.

**What has to tell it apart from the nine skins already drawn.** `lamellar` is also built of bands,
but its bands are *small laced plates* with the lacing showing between them; `gothic` and
`gothic_strict` run their lines *vertically*. Lorica is the only skin in the set made of **wide,
continuous horizontal hoops**, each one a bright lit edge over a body that falls away into the
shadow of the hoop below. Three values in a fixed vertical rhythm, repeated down the whole torso —
that rhythm is the skin. If a screenshot of your chest could be mistaken for `lamellar`, the bands
are too small; make them taller and the shadow line under each one harder.

## What is already done

Both sheets are seeded with **vanilla netherite's exact silhouette at a flat `8`**. Every texel
vanilla paints already carries paint: the crown, the cheek strips beside the face, the six-row
sleeve, the belt row, the sole. The vertical zoning is vanilla's own, so there is nothing to decide
about rows, hems or how far down a boot goes. Netherite is the seed because it is the only vanilla
set that wraps the cheeks and runs the sleeve to row 6 — which is exactly what a galea's cheek
plates and a shoulder stack of lames need.

## The rules, all of them enforced

1. **Every stamp shades and nothing else.** Paint aimed at a texel outside the silhouette is dropped
   before it lands, and the reply tells you how many. You cannot break the outline — and you cannot
   extend it either, so do not try. Do not use `.`; it does nothing here.
2. **Level `8` is reserved for "not yet drawn".** The check counts every texel still at `8` and the
   save is refused while any remain. Never use `8` as a value.
3. **Bands four to five levels apart.** Your ladder is `2` shadow, `6` mid-dark, `a` mid-light,
   `e` highlight, with `4` and `c` as half steps and `0`/`f` at the extremes. This is measured, not
   taste: a step of one or two levels can bake *identical* on some materials.
   `python tools/bake_skin.py --levels` prints why, and `--pair 6 a` checks any pair you fancy.
4. The usual: no paint over the face window (the silhouette already leaves it open), leave
   `helmet_raised` alone, reach at least 6 of the 8 ramp shades.

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

Two things the silhouette hands you for free, and you should use both:

- **`helmet.front` cols 3 and 4 at rows 3..4** are a separate island in the middle of the face
  window. On a galea there is no nasal bar, so let that island *recede* — it is the shadowed brow
  above the nose, not a highlight.
- **`helmet.back` row 6, cols 2..5** is a tab hanging below the rest of the helmet. That is the
  galea's neck flange. Make it the brightest thing on the back of the head.

## The armour, net by net

**chest — the hoops.** This is the whole skin; draw it first and set the scale by it.

Rows 3..11 are three hoops of three rows each, in the same three values every time:

    row 3   e e e e e e e e     hoop 1, lit top edge
    row 4   a a a a a a a a     hoop 1, body
    row 5   2 2 2 2 2 2 2 2     the shadow the next hoop casts on it
    rows 6,7,8    the same three
    rows 9,10,11  the same three

Rows 0..2 are above the hoops: the shoulder yoke and the collar. Row 0 and row 1 are only cols 0, 1,
6 and 7 (the shoulders either side of the neck) — `c`. Row 2 keeps its cols 0..2 and 5..7 — `6`, so
the collar reads as a shadowed step down into the first hoop.

`chest.back` is the same construction one band darker: `c` / `6` / `2` instead of `e` / `a` / `2`,
so the front reads as the lit side. `chest.left` and `chest.right` are 4 wide and rows 0..8 only:
run the same three-row rhythm across all four columns, at the back's values.

**arm — the shoulder stack.** A tighter rhythm than the chest, because these lames are smaller.
Two-row bands all the way down: rows 0..1 `e`/`a`, rows 2..3 `e`/`a`, rows 4..5 `e`/`a`, and
whatever survives on row 6 at `2` as the hem. `arm.top` flat `c` — the top of the shoulder catches
the light and it is seen from above constantly.

**helmet — the galea.** A smooth bowl, not a faceted one.

- `top`: `c` overall with the middle two columns at `e`, a soft fore-and-aft crown ridge.
- `front` rows 0..2: `6` at row 0, `a` at row 1, `e` across row 2 — a hard bright brow band, which
  is what makes a galea a galea at this size.
- `front` rows 3..4, cols 3 and 4: `4`. The shadow over the nose. Do not brighten it.
- `front` rows 3..7, the outer columns (0, 1, 6, 7 where they exist): the cheek plates. `a` on the
  outer column, `6` on the inner one, so each cheek reads as a plate turning away from you.
- `back` rows 0..5: bowl, `a` falling to `6` at row 5.
- `back` row 6 (cols 2..5): the neck flange, `e`, with row 5 above it at `2` so the flange stands
  clear of the skull.
- `left`/`right`: `a` bowl rows 0..3, `6` at row 4, and the single surviving column at rows 5..7 at
  `c` — that is the cheek plate seen edge-on and it should agree with the front.

**waist — the cingulum and its apron.** Row 7 is the belt: `e` on the front's four texels and on the
sides, `c` across the back. Rows 8..10 are the hanging strips: `a` `4` `a` `4` `a` `4` `a` `4`
straight across, so every strip is a lit face beside its own shadowed edge. Row 11 is the hem, `2`,
with no strips on it — a strip that runs off the bottom row reads as a smear.

**leg — the greave.** Rows 0..8, and remember rows 6..8 disappear under the boot, so spend nothing
there. A bronze greave is a single rounded shell with a ridge down the shin: front and back
`a e a 4` across the four columns; `left` and `right` `6 a a 4`. `leg.top` flat `6`.

**boot — the caligae.** Rows 7..11 (and the fragments at row 6). Open-work leather: an `a` field
with `2` running down cols 1 and 2 as the strap gaps, and row 11 at `6` as the sole edge.
`boot.bottom` is the hobnailed sole — this face is seen every time the player looks down and it is
the one joke in the skin: a `2` field with `c` at every other texel in both directions, a grid of
nail heads.

## What to do

One `armorpieces_skin_paint` call per sheet, a stamp per face; `fill` for a flat face, `tile` for
anything repeating (the hoops are `tile: ["e","a","2"]` on a face — three rows repeating down it),
`rows` for the hand-placed work. Compose the arithmetic in your reply text *before* the call: doing
it there is what turns three corrective calls into one correct one.

Look at it on iron, gold and netherite before saving — judge the dark end on netherite, the
mid-tones on iron, never on the greyscale master. **Six pictures is the budget** and every one is
re-sent on every later turn, so take them where they can still change what you draw.

## Done means

`armorpieces_save_skin` accepted without `force`; `python tools/check_skin.py lorica` clean;
`python tools/bake_skin.py lorica --out build/skins`; and the hoop rhythm still visible on all three
materials — a three-row band is the one thing a narrow ramp can flatten, so if the hoops merge on
any material, say which and by how much.

## Lessons from the session

The ladder as drawn: `2` shadow, `4` half-shadow, `6` mid-dark, `a` mid-light, `c` half-highlight,
`e` highlight — six of the eight stops, `0` and `f` never used (nothing on this skin needed the
absolute extremes, and the brief's own ladder didn't ask for them). Front chest hoops used
`e`/`a`/`2`, back and both chest sides one band darker at `c`/`6`/`2`. Arm used tight `e`/`a` two-row
bands with `2` hems. Waist strips used `a`/`4` alternation. Legs used a four-column ridge `a e a 4`
(front/back) and `6 a a 4` (sides). Boot open-work used `a` field with `2` strap-gap columns and `6`
sole edge; the sole itself is a `c`/`2` checkerboard.

Two calls did the whole skin (19 stamps on `humanoid`, 9 on `humanoid_leggings`) — the brief's
worked-out per-row arithmetic made this straightforward: every face was either a flat `fill`, a
short repeating row cycle, or an explicit row array with leading blank/space rows to skip past
whatever sat above the painted band. Padding a `rows` array with space-rows to reach a band that
starts mid-face (waist row 7, boot row 6) worked cleanly and kept every stamp anchored at the face's
own row 0, which is easier to get right by inspection than computing an `at` pixel offset by hand.

The hoop rhythm survived on all three checked materials. It's most legible on gold (strong
saturation keeps the three steps distinct), still readable on iron (the steps compress toward the
light end but the shadow line under each hoop stays visible), and on netherite the bands stay
distinct even though the whole chest sits at the dark end — no two adjacent hoops merged into one
band on any of the three. Nothing here read badly in 3D that didn't already look right in the
greyscale master; the seeded silhouette removed the usual failure mode (a shape that only exists
because of hand-picked hems) since every hem was already vanilla's.

One thing worth flagging for the next seeded-and-pinned skin: the check's "reach at least 6 of the
8 ramp shades" note is satisfied by using six *named* values without ever touching `0` or `f` — true
here only because the brief's ladder happened to list six stops. A skin whose brief gives a narrower
named ladder (say four stops) would need to deliberately reach for the extremes to clear that bar,
and nothing in the tool warns about it until the final check.
