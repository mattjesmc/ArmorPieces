# Brief: Milanese

From `docs/plans/armor-skins.md`:

> **milanese** — smooth rounded Italian plate, polished, almost no line work, one big besagew. The
> opposite pole to gothic and the test of the ramp's smooth middle.

Milanese armour is one continuous polished curve. This skin is drawn by taking almost everything
away: no flutes, no rivets, no repeated pattern anywhere, and the form carried entirely by where the
light falls across a face. It is the hardest of the eight, because at sixteen texels "smooth" is one
step away from "blank". Read [[plate]] for the value scale and [[gothic]] for what this is answering.

## The surface

A face is a curve, and a curve at this size is three bands and a highlight:

    front of the chest, column by column:  6 9 c e e c 9 6

Not row by row — the chest is a cylinder standing up, so the shading runs ACROSS it and the rows
repeat. That is the single idea of this skin, and it is why it looks nothing like gothic even though
the same eight values are in play. Two rules:

- the highlight column is two texels wide and stays in the same place on every row of a face, so the
  curve is continuous down the whole plate;
- a horizontal line is only allowed where two plates actually meet. There are three of them on the
  whole skin: under the breastplate, under the pauldron, and at the top of the sabaton.

## The besagew

The one asymmetric detail in the set. A besagew is the disc that covers the armpit, and because the
limb nets are shared between left and right it cannot go on the arm — put it on the **chest front**,
top left as the wearer sees it: a three-by-three of `d` with a `2` ring around it and an `f` texel at
its top left, over rows 1..3, columns 0..2. Nothing mirrors it on the other side, and that asymmetry
is the whole point.

## Net by net

**helmet.** An armet: a smooth ovoid. Sides and back rows 0..6, shaded across rather than down —
`7 a c a 7` from the front edge to the back on each side. Cheeks at rows 6..7 on the two columns
nearest the front. Front solid rows 0..2 as a brow with a single `e` highlight row, open below except
one texel each edge. `top` a broad `d` field with `9` at the edges. `bottom` empty. Nothing on
`helmet_raised`.

**chest.** Rows 0..8, the curve above, plus the besagew. Neck open in the middle four texels of row
0. Row 8 is the one horizontal line: `3`, with `c` immediately above it. Back the same curve one band
darker, no besagew. Sides plain `7` with a lighter column at the front edge.

**arm.** Rows 0..6. A single large pauldron, rows 0..3, curved across (`6 a d a 6`), with `2` under
it at row 4; rows 5..6 a plain vambrace at `9`. Two pieces, not five — that is what makes it
Milanese rather than gothic.

**waist.** Rows 7..11. A plain belt at rows 7..8 (`5`, `a` highlight). A fauld of one deep lame, rows
9..11, curved across like the chest, its bottom row `4`.

**leg.** Rows 0..8. A cuisse curved across, `6 9 c 9`; rows 7..8 a poleyn as a smooth `c` dome with
`3` beneath it and no outline on the sides.

**boot.** The bottom six rows. Row 6 a `3` line, the top of the sabaton; rows 7..11 curved across,
with a `d` ridge down the centre of the foot. `bottom` (sole) `2`.

## Done means

`armorpieces_save_skin` accepted without `force`; `python tools/check_skin.py milanese` clean; looked
at on iron, gold and netherite, and next to gothic if it is drawn — the two must not be mistakable;
the lessons below written, including whether an across-the-face gradient survives at four texels
wide on the arms.

## Lessons from the session

Drawn 2026-09-04, the second skin through the bridge and the first drawn as its own session
(plate and gothic were drawn earlier). Matches the brief net by net; departures noted below.

### The value scale, as it ended up

Followed the brief's literal ladders rather than re-deriving them from `--levels`, since the brief
already names exact values (`6 9 c e`, `7 a c`, `4 7 a c`, `6 a d`). Checked afterwards against the
per-material table: `6→9→c→e` (3,3,2-level steps) is uneven — the `9→c` step is only 12 luma on
iron, the weakest link in the whole skin, and `c→e` is only 5 luma on copper (not checked per the
brief's own done-means, which only asks for iron/gold/netherite). Everything else in the ladder set
(`7→a→c`, `4→7→a→c`, belt `5`/`a`, hem `3`/`4`) cleared 12+ luma on all three required materials.
**On iron and netherite it reads fine** — the weak step is real but small enough that adjoining bands
still separate at 16 texels, because the shapes are broad (a whole face-width column, not a
one-texel flute) and get help from ambient occlusion at the seams. Next time I'd still start from
`--levels` and slide `9→c` to `9→d` (20 luma) or `a→d` (14, and reuses `a` from the arm/helmet
ladder) rather than trust a brief's example numbers unchecked — a brief is english, not a bake
report.

### Does an across-the-face gradient survive at four texels wide? (the brief's question)

Yes, but it reads as **bands, not a gradient** — which turns out to be correct for this style, not a
failure of it. The arm (4 columns: `a d d a`) and leg (4 columns: `6 9 c 9`) came out as three or
four flat vertical stripes rather than a smooth roll, because there is no room to interpolate between
samples at that width. On first look this worried me — it resembles gothic's fluting at a glance,
especially on gold where the steps are most visible. Looked at longer: the two are not confusable.
Gothic alternates high/low every single texel (`e5e5e5e5`, 9-level jumps, one column of highlight
immediately beside one of shadow) and repeats on every row down the whole face. Milanese's bands are
half as many, each 1-2 texels wide, monotonic (rise then fall, not alternating), spaced 3 steps apart
not 9, and — this is the part that actually reads as "curved" rather than "striped" — **the same
values repeat down every row of the face**, so the eye reads a single continuous cross-section rather
than a repeating unit. A gradient does not survive four texels; a stepped curve does, and at this
size a stepped curve is the only kind of curve there is. Side by side on iron the two skins are not
mistakable (see `build/skins/{milanese,gothic}/iron/humanoid.png`) — milanese is a handful of broad
soft bands, gothic is a fine barcode.

### The besagew

Reads clearly on all three materials as a dark L-shaped ring wrapping the lit shoulder edge — the
single asymmetric detail is legible even at this scale and the `f` corner texel does not read as a
sticker (unlike the plate lesson's warning about 2×2 white patches; a single `f` texel inside a `2`
ring stays a highlight, not a hole). The brief's exact footprint (3×3 `d`, rows 1..3 cols 0..2) sits
right at the sheet's own top-left corner and the neck opening's left edge, so the ring is naturally
clipped on two of its four sides by geometry that was already there rather than by a decision I made
— convenient, but worth naming as luck: a besagew placed mid-face would need the ring drawn in full.

### What read badly in 3D, and the fix

* **An unpainted-but-visible face bakes as a flat saturated color, not "bare body".** `arm.top` was
  left unpainted (not mentioned in the brief) on the assumption it would show skin-tone through
  transparency like the profile describes. Instead, at inflate 1.0 over the shoulder, fully
  transparent alpha rendered as a solid cyan/teal patch — clearly some fallback rather than the arm
  underneath (the arm mesh is not directly below the shoulder cube; there is nothing to show through).
  It reads as a rendering error, not a design choice, from every camera angle that sees the shoulder
  from above. **Caught by looking from three-quarter, not front** — the front camera never reveals
  `arm.top` at all. Fixed by painting it flat `d`, matching the pauldron peak. **Lesson for the next
  skin: any face not explicitly addressed by the brief still needs a look from an angle that can see
  it before calling the skin done — "not mentioned" is not the same as "hidden".**
* Nothing else needed correction after that. The hem lines (chest row 8, waist row 11, boot row 6)
  read as clean single dark rings on netherite, not the "three hard black rings" the profile warns
  about — because each is one row of `3`/`4` with a lit row directly above it, not a bare dark line
  on its own.

### Occlusion, measured on the rig

Matches the plate/gothic notes exactly: `leg` rows 6..8 (the poleyn) are fully hidden by `boot`
(inflate 0.9 over 0.4) with a full harness on, and `waist` rows 7..8 (the belt) are fully hidden by
`chest`. Both were drawn anyway, per the brief, as the leggings-only fallback; the check names the
hidden count so this was confirmed rather than assumed.

### What the next skin should know about the tools

* The whole skin was 2 `armorpieces_skin_paint` calls (one per sheet) plus one follow-up 1-stamp fix
  for `arm.top` — the stamps-list-in-one-call interface works exactly as advertised for a skin this
  size (7 nets, ~1000 texels).
* `region`+`face` addressing made the "curve across, not down" construction trivial: every row of a
  face got the *same* short string, so a whole net's worth of rows was just that string repeated N
  times in the array, no coordinate arithmetic at all.
* The one gap: **nothing in the toolchain flags a visible-but-unpainted face before you go looking
  for it with a camera.** `armorpieces_skin_check` lists unpainted faces as a `-` note ("cut on
  purpose, or forgotten") but doesn't distinguish "genuinely never seen" (`arm.bottom`,
  `helmet.bottom`) from "seen from some angles" (`arm.top`) — that distinction currently lives only
  in a human's memory of the rig, or in trial screenshots from non-default angles. A note that named
  which unpainted faces are visible from *some* camera (even a rough one, "seen from above/three-
  quarter") would have caught the teal patch without needing the three-quarter shot at all.
* `bake_skin.py --levels` is worth running even when a brief already hands you numbers — it would
  have flagged the `9→c` step as the weakest link in this skin's ladder before painting rather than
  after.
