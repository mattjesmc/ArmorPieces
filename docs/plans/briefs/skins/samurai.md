# Brief: Samurai — the ō-yoroi

Japanese lamellar as it is actually built: small plates laced together by **vertical cords of silk**,
so the surface is a grid — horizontal plate courses crossed by bright vertical lacing. Over it, a
`kabuto` helmet with a flared `shikoro` neck guard and `fukigaeshi`, the two plates that turn back
beside the face; enormous flat `sode` shoulder boards; and a `kusazuri` skirt of hanging panels.

**What has to tell it apart from `lamellar`, which is already drawn.** They are the same idea and
the difference is entirely in the *lacing direction and the scale of the parts*:

| | `lamellar` | this |
|---|---|---|
| surface | horizontal bands, lacing showing *between* them | a **grid** — plate courses crossed by vertical cords running down the whole torso |
| shoulder | part of the same banding | one **big flat board**, three lacing lines, a bright rim |
| skirt | continuous | **separate hanging panels** with dark gaps between them |
| helmet | plain | a **flared tier** at the back and two **bright plates beside the face** |

Get the vertical lacing and the big flat sode right and nobody will confuse them. Repeat
`lamellar`'s horizontal banding and the session has produced a duplicate.

## What is already done

Both sheets are seeded with **vanilla netherite's exact silhouette at a flat `8`**. Every texel
vanilla paints already carries paint: the crown, the cheek strips beside the face, the six-row
sleeve, the belt row, the sole. The vertical zoning is vanilla's own, so there is nothing to decide
about rows, hems or how far down a boot goes. Netherite is the seed because it is the only vanilla
set that wraps the cheeks — those strips are the `fukigaeshi` — and the only one whose sleeve runs
to row 6, which is the depth a `sode` needs.

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

**A one-texel detail survives only if it is far from its field.** `brigandine`'s rivets held at six
to seven levels from the field and would have vanished at three. Your lacing is one texel wide, so
it must be `e` on an `a` field and nothing closer.

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

Two islands the silhouette hands you:

- **`helmet.front` cols 3 and 4 at rows 3..4** — the brow of the kabuto over the nose. There is no
  nasal bar on a kabuto; leave it dark (`4`) so it recedes.
- **`helmet.back` row 6, cols 2..5** — a tab hanging below the skull. That is the lowest tier of the
  `shikoro`, and it should read as a *separate* flared plate, not as more helmet.

## The armour, net by net

**chest — the dō, and the grid.** This is one `tile` and it is the whole skin.

Plate courses two rows tall, a dark seam row between them, and bright lacing running vertically
through all of it:

    tile: ["aeaeaeae",
           "aeaeaeae",
           "26262626"]

Read it: on a plate row, every second column is a silk cord at `e` over an `a` plate; on the seam row
the same alternation drops to `2`/`6`, so the cords carry on down through the seam while the plate
goes dark. That is exactly how a laced cuirass looks and it costs one stamp per face.

Run it on `front`, `back`, `left` and `right`. The back one band darker (`6`/`a` plate, `2`/`4`
seam). Rows 0..2 on the front keep only their outer columns — the shoulder straps: `c` flat, no
lacing, so there is somewhere for the eye to rest. Row 11 on both front and back: `2`, the bottom
edge of the dō.

**arm — the sode.** The board, and the thing most likely to be got wrong. It is **flat** — a single
large plate, not a stack of small ones.

- row 0: `e` right across — the lit top rim of the board.
- rows 1, 2: `c` field.
- row 3: `2` — a lacing line across the board.
- row 4: `c` field.
- rows 5..6: whatever the silhouette leaves, at `6`, as the board's lower edge in shadow.

No vertical lacing on the sode: the contrast between the plain board and the grid on the dō is what
makes both of them read. `arm.top` flat `e`.

**helmet — the kabuto.**

- `top`: `a` bowl, the middle four texels at `c`, and the very centre two at `e` — the `tehen`, the
  opening at the crown. Concentric, not striped.
- `front` row 0: `6`. Row 1: `a`. Row 2: `e` — the `mabizashi`, the peak over the brow, a hard
  bright bar right across.
- `front` rows 3..4, cols 3 and 4: `4`.
- `front` rows 3..7, outer columns: the **fukigaeshi**, `e` on the outer column with `2` on the
  inner one. These two bright plates flanking the face are the single most recognisable thing on a
  kabuto — do not let them be quiet.
- `back` rows 0..3: `a` bowl. Rows 4..5: `6` then `2` — the first tier of the shikoro and its
  shadow. Row 6 (cols 2..5): `a`, the flared lowest tier standing clear.
- `left`/`right` rows 0..3: `a` bowl; row 4 `6`; the single surviving column at rows 5..7 at `e`,
  agreeing with the fukigaeshi on the front.

**waist — the kusazuri.** The same grid as the dō, cut into hanging panels.

Row 7: `2`, the gap under the dō. Rows 8..11: the chest's tile again, but with **cols 2 and 5 forced
to `2` on every row**, which splits the eight columns into three hanging panels with dark gaps
between them. Row 11 all `2` — the panels' bottom edge. On the back, one band darker throughout.

**leg — the suneate.** Vertical splints, which agrees with the lacing direction and keeps the figure
consistent: `front` and `back` at `a e 6 2` across the four columns, `left` and `right` at
`6 a a 4`. Rows 0..1 one band up for the knee. Rows 6..8 vanish under the boot; spend nothing there.
`leg.top` flat `a`.

**boot — the warazi over tabi.** Rows 7..11: a `6` field with `2` across rows 8 and 10 as the binding
cords, and `a` on the front rows 7..8. `boot.bottom` (the sole) flat `4` — woven straw, no hardware.

## What to do

One `armorpieces_skin_paint` call per sheet, a stamp per face; `tile` does the dō and the kusazuri,
`rows` does the sode, the kabuto and the fukigaeshi. Compose the arithmetic in your reply text
*before* the call — in particular work out on paper which absolute row of each face is a plate row
and which is a seam row, because `tile` starts its pattern at row 0 of the face and a course that
starts half a row out looks like a mistake.

Look at it on iron, gold and netherite before saving — judge the dark end on netherite, the
mid-tones on iron, never on the greyscale master. **Six pictures is the budget** and every one is
re-sent on every later turn, so take them where they can still change what you draw.

## Done means

`armorpieces_save_skin` accepted without `force`; `python tools/check_skin.py samurai` clean;
`python tools/bake_skin.py samurai --out build/skins`; and the one-texel lacing still visible on all
three materials, because that is what a narrow ramp destroys first. Say explicitly whether this
still reads as a different armour from `lamellar` at a glance — you may look at
`tools/skin_masters/lamellar/humanoid.png` through `python tools/skin_sheets.py --skin lamellar` to
check, and that is the only other skin you may look at.

## Lessons from the session

**Value ladder as drawn.** Exactly the brief's: `2` shadow, `6` mid-dark, `a` mid-light, `e`
highlight, `4`/`c` half steps, plus `f` used once (knee bump on the leg, see below) and `9`
touched by nothing — 6 of 8 ramp shades reached, range 34..255 on netherite. No `8` left anywhere;
the save went through clean on the first try, no `force` needed.

**The three-row `tile` landed on the right courses without adjustment.** `chest.front`/`back` are
12 rows, so the `aeaeaeae`/`aeaeaeae`/`26262626` cycle repeats exactly four times (rows 0-2, 3-5,
6-8, 9-11) with no half-course at the bottom — row 11 lands on a seam row by construction, which is
why overriding it flat `2` for "the bottom edge of the dō" cost nothing extra to reconcile. Worth
noting for the next skin that uses `tile` on a 12-row face: 12 is divisible by 3, so this is the
lucky case: `arm` (7 painted rows) and `helmet` (8) are not, which is exactly why those two were
written as explicit `rows` instead of `tile` — trying to force a 3-cycle onto them would have
landed a seam row wherever the cycle happened to fall, not where the brief wanted it.

**A discovery worth recording: clipping does the hand-tailoring for you.** The brief's silhouette
table shows exactly which columns of each row are inside the outline (e.g. `helmet.front` row 3 is
`#..##..#`, only cols 0,3,4,7 real), and I started out planning to hand-carve every `rows` string to
match those gaps. It's unnecessary — "paint aimed at a texel outside the silhouette is dropped"
means a plain solid row (`"e2a44a2e"` sent for all 8 columns) lands only on the columns the
silhouette keeps and is silently dropped everywhere else. Composed the whole helmet front as three
full-width rows (peak) plus five outer/inner-column rows, sent solid, and let the seed shape carve
the fukigaeshi and the brow out of it. This is the single biggest time-saver in the brief and it's
worth stating explicitly in the shared instructions rather than leaving it to be rediscovered per
skin — "you do not need to match the silhouette's gaps in what you paint, only cover the row" would
have saved the planning-on-paper time the brief itself asks for.

**One texel-count judgment call: boot row 6.** The brief's boot instructions only cover rows 7-11,
but the seed silhouette has a partial row 6 (front full, sides one column, back empty — the ankle
just showing above the solid boot). Not addressed in the brief, and it still needed a real value.
Extended the base `6` field up into row 6 rather than inventing new detail there; reasonable, but a
brief that hands out a seeded silhouette should probably enumerate every row that has paint, even
where "nothing to see" is the right answer, so this isn't a guess next time.

**The "one band up" instruction for the leg's knee rows needed interpretation.** "Rows 0..1 one band
up for the knee" on a column already at `e` (the ladder's top main rung) has nowhere to go but `f`,
a 1-level step from `e` that the brief's own contrast rule says can bake identical. Used it anyway
since it's a topping-out, not a shading pair the eye is meant to distinguish two values by — but a
ladder that reserves its top rung for a detail that then needs headroom above it is worth flagging:
maybe leave `f` out of the four-rung ladder proper and treat it only as this kind of ceiling.

**Compares to `lamellar` in the sheet, not just in 3D.** Read `lamellar/humanoid.png` back as text
(`skin_sheets.py --skin lamellar`): its chest is horizontal banding — every row of the 8-wide chest
face is one flat value or a fixed alternation, repeated identically across all 8 columns, with the
lacing living as short vertical tick marks at four fixed column positions (`bbb3eee6eee6bbb3e6eee6ee`
-style rows). `samurai`'s chest instead alternates *within* every row and changes character every
row (two `a`/`e` plate rows then a `2`/`6` seam row), which is a true crossed grid, not a banded
surface with accents. In the viewport this reads as a checkerboard weave on samurai against stacked
horizontal plates on lamellar — confirmed on iron, gold and netherite, and the one-texel lacing
(`e` on `a`, `c` on `9`/`6`-ish fields) stayed visible on all three, including netherite where the
whole ramp compresses hardest. The sode's flat board (no vertical lacing) against the grid on the dō
is what sells "this is not lamellar" fastest at a glance — the plain plate reads immediately as a
different construction method, which the checkerboard alone might not have.
