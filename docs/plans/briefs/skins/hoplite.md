# Brief: Hoplite — the Greek bronze harness

A muscled bronze cuirass, hammered into the shape of the body it covers: pectorals, a hard arc under
them, the ridged blocks of the abdomen, and a flared rim at the hip. Over the shoulders a yoke; below
it a short skirt of leather **pteruges**. An Attic helmet with a raised brow and hinged cheek pieces,
and smooth one-piece greaves on the shins.

**What has to tell it apart from the nine skins already drawn.** Every other skin in the set is made
of *hardware* — plates, rivets, lacing, scales, flutes, a weave. This one has **no line work at
all**. It is the only skin whose subject is a curved surface and whose whole vocabulary is where the
light falls on it. `milanese` is the nearest relative and it is smooth *and blank*; this is smooth
and **anatomical**. If your chest could be described as "a pattern", it is wrong. It should be
describable only as "a body".

That makes this the hardest of the five and the one most worth spending your picture budget on.
Take the first screenshot after the chest, not at the end.

## What is already done

Both sheets are seeded with **vanilla netherite's exact silhouette at a flat `8`**. Every texel
vanilla paints already carries paint: the crown, the cheek strips beside the face, the six-row
sleeve, the belt row, the sole. The vertical zoning is vanilla's own, so there is nothing to decide
about rows, hems or how far down a boot goes. Netherite is the seed because it is the only vanilla
set that wraps the cheeks, and an Attic helmet's cheek pieces are the second thing this skin is
recognised by.

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

**The trap this skin walks straight into.** "Smooth" tempts you to shade in single steps — `a`, `b`,
`c`, `d` across a pectoral — and every one of those steps can bake to the same colour. A rounded
form at eight texels wide is **three values, not eight**: a lit face, a mid, and a turn into shadow,
four levels apart each time. `milanese` learned this and so did `plate`. Build every curve out of
`4` / `a` / `e` (or `2` / `6` / `a` where the form is in shadow) and nothing between.

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

**`helmet.front` cols 3 and 4 at rows 3..4** are an island in the middle of the face window. An
Attic helmet has *no* nasal, so that island is the shadowed underside of the brow: put `2` there and
leave it alone. Resisting the urge to make it bright is what separates this helmet from
`varangian`'s.

## The armour, net by net

**chest — the muscle cuirass.** Draw this first, screenshot it, and only then do anything else.

Here is the whole front face, written out. Rows 0..2 keep only the columns the silhouette gives them
(the shoulders either side of the neck); a space below means that texel is outside the outline.

    row 0   c c . . . . c c      the shoulders, lit
    row 1   a a . . . . a a      turning down into the chest
    row 2   6 a a . . a a 6      the collarbone shelf
    row 3   4 a e a a e a 4      pectorals: each one a highlight with a fall-off either side
    row 4   4 6 a c c a 6 4      the lower half of each pectoral, rounding under
    row 5   4 6 2 4 4 2 6 4      the hard arc under the pecs — the darkest line on the torso
    row 6   4 a e 6 6 e a 4      upper abdominals, with the centre line between them
    row 7   4 a e 6 6 e a 4      the same block repeated: an abdomen is a stack
    row 8   4 6 a 4 4 a 6 4      the lowest block, sinking toward the navel
    row 9   6 6 a a a a 6 6      the waist, flattening off
    row10   . c c c c c c .      the flared rim of the cuirass, catching light all the way round
    row11   . . 2 2 2 2 . .      and its shadowed underside

`chest.back` is the same body seen from behind: shoulder blades instead of pectorals. Use the same
construction with the two highlights moved *outward* one column (rows 3..4 at cols 1 and 6 instead
of 2 and 5), and run everything one band darker, so the front reads as the lit side. Give it the
same `c` rim at row 10 and `2` at row 11 — the rim goes all the way round.

`chest.left` and `chest.right` are 4 wide, rows 0..8: the flank. Three values only — `6 a a 6`
across, dropping to `4 6 6 4` from row 5 down. No anatomy on the sides; the ribs are not visible on
a cuirass.

**arm — the yoke and the shoulder pteruges.** Rows 0..3 are the bronze shoulder yoke: `c` at row 0,
`e` at row 1 (the top of the shoulder is the brightest thing on the figure), `a` at row 2, `6` at
row 3. Rows 4..6 are leather pteruges hanging from under it: alternate `a` and `4` by column
(`a4a4`), which reads as separate strips, and let row 6 keep whatever the silhouette gives it at
`2`. `arm.top` flat `e` — this is the surface the sun hits.

**helmet — the Attic.**

- `top`: `a` bowl with the middle two columns at `e`, a low fore-and-aft crown ridge.
- `front` row 0: `6` (the bowl curving away above the brow). Row 1: `a`. Row 2: `e` — the raised
  brow band, a hard bright line right across.
- `front` rows 3..4, cols 3 and 4: `2`, as above.
- `front` rows 3..7, outer columns: the hinged cheek pieces. `c` on the outer column and `6` on the
  inner one, so each cheek is a small plate standing away from the face.
- `back` rows 0..5: `a` bowl falling to `6`; row 6 (cols 2..5) at `c` as the neck guard, with row 5
  above it at `4`.
- `left`/`right` rows 0..4: `a` bowl, `6` at row 4; the single surviving column at rows 5..7 at `c`,
  agreeing with the cheek pieces on the front.

**waist — the bronze skirt.** Not pteruges: this skin's pteruges are on the shoulder, and repeating
them here would flatten the whole figure into stripes. Row 7 is the bottom edge of the cuirass, `c`.
Rows 8..10 are a smooth bronze fauld — `6 a a a a a a 6` on the front and sides, one band darker on
the back. Row 11 is the scalloped hem: `2`.

**leg — the greave.** A one-piece bronze shell moulded to the calf, and the same three-value rule as
the chest. `front` and `back`: `4 a e a` across the four columns — the ridge of the shin, lit.
`left` and `right`: `6 a a 4`. Rows 0..1 lift one band (`a e f a` on the front) for the knee cop,
which is the part of a greave that is actually shaped. Rows 6..8 disappear under the boot: spend
nothing there. `leg.top` flat `a`.

**boot — the sandal.** Rows 7..11: a `6` leather field with `2` down cols 1 and 2 as the strap
gaps, and `a` on the front at rows 7..8 as the lit instep. `boot.bottom` (the sole) flat `4`.

## What to do

One `armorpieces_skin_paint` call per sheet, a stamp per face; `fill` for a flat face, `rows` for
everything anatomical — `tile` has almost no use in this skin, which is the point of it. Compose the
arithmetic in your reply text *before* the call.

Look at it on iron, gold and netherite before saving — **gold is the one that matters here**, since
a bronze cuirass is what this skin is actually of. Judge the dark end on netherite and the mid-tones
on iron, never on the greyscale master. **Six pictures is the budget** and every one is re-sent on
every later turn, so take the first after the chest, where it can still change what you draw.

## Done means

`armorpieces_save_skin` accepted without `force`; `python tools/check_skin.py hoplite` clean;
`python tools/bake_skin.py hoplite --out build/skins`; and the anatomy still reading as a body on
all three materials. This is the skin most likely to flatten in the bake, so if the pectorals or the
abdominal blocks merge into a field on any material, say which, by how many luma, and what you did
about it.

## Lessons from the session

**The ladder held.** `2` shadow / `6` mid-dark / `a` mid-light / `e` highlight, four levels apart
each, was the spine of the whole skin and it is what makes the cuirass read as a body on iron and
netherite as well as it does on gold. Every row that used only that spine (row 3's `4 a e a a e a
4`, row 6/7's `4 a e 6 6 e a 4`, the greave's `4 a e a`, the boot's `6 2 2 6`) held its shape on all
three materials without a second look.

**Three values were enough for a curve at eight texels — but the half-steps (`4`, `c`) were not a
free fourth value.** The brief's own row 4 (`4 6 a c c a 6 4`, "the lower half of each pectoral,
rounding under") puts `a` next to `c`, and `a`-`c` is a 2-level gap: `--pair a c` measures it at 3
luma on iron and 4 on netherite — invisible, the worst pair in the whole ladder. On iron the row
still reads as a lit patch (the `6`→`a` step on either side is 24 luma and carries it) but the
extra "rounding under" bump that `c` was meant to add over `a` does not show; the row plateaus
instead of cresting twice. I left it as written since it's the brief's own construction and the
surrounding rows (3's sharp `a`/`e` peak, 5's `2` arc) still carry the pectoral's shape, but a
skin that used `a`/`c` for a step that has to be *seen* rather than merely felt would need `a`/`d`
or `a`/`e` instead. Net effect: no block merges into a flat field on any material, but row 4
specifically is a half-step weaker than the brief's prose implies — worth flagging rather than
quietly fixing, since it's exactly the trap the brief warned about, just at a smaller scale than a
whole-field collapse.

**Reading it in 3D vs. arithmetic.** Composing the whole sheet as arithmetic before any paint call
worked and cost two calls total, but I couldn't judge the a/c flatness from the numbers alone —
`bake_skin.py --pair` after the fact is what actually caught it, not the screenshot (iron looked
"a bit flat" but I couldn't say why without the pair check). Next skin: run `--pair` on every
adjacent-value transition the brief specifies *before* painting, not just `--levels` once at the
start — it's cheap (no picture budget) and would have caught this before the paint call instead of
after.

**helmet_raised had zero silhouette texels** (vanilla netherite paints no second shell), so
"leave it alone" cost nothing to honour — it never appeared in any unpainted-face warning because
it was never counted at all. Worth saying in the tool docs so the next skin doesn't go looking for
it in the check output.

**Six-picture budget was generous here.** Two views (front, three-quarter) plus three material
previews used five of six; the sixth was never needed because the arithmetic-first, screenshot-once
approach meant nothing had to be redrawn. The chest's construction was legible at 8 texels wide
without a close-up.
