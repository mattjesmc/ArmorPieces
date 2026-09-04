# Brief: Gothic

From `docs/plans/armor-skins.md`:

> **gothic** — fluted German plate: vertical flutes on breast, pauldrons and cuisses, cusped edges.
> Hard light/dark striping — the most sculpted of the eight and the heaviest user of the ramp's ends.

Gothic harness is plate with the surface folded into ridges. It is the loudest skin in the set and
the one that most needs the ramp's whole range: a flute is a highlight column immediately beside a
shadow column, and if those two are three steps apart it disappears. Read [[plate]] first — this is
that skin with a different surface, and its proportions are the ones to keep. Read the lessons of
whatever ran before it.

## The flutes

One texel of highlight, one of shadow, repeating, with the pattern running vertically down a face:

    e5e5e5e5

That is deliberately extreme. It is the test of whether the deepened ramp really gives eight
distinguishable shades on iron and gold — if it does not, this skin will say so first. Two rules
keep it from turning into a barcode:

- flutes only on the big convex surfaces: the front and back of the chest, the front of the arm and
  leg, the top of the pauldron. Side faces stay plain (`6`), or the figure strobes;
- a flute stops where the plate stops. The last row before a hem is `2` across the full width, which
  cuts every flute off at once and reads as the plate's edge.

## Cusped edges

The one place gothic differs in silhouette rather than surface. Where a plate ends, the last painted
row alternates: paint, clear, paint, clear across the width, so the edge is toothed. Use it on the
bottom of the chest (row 8), the bottom of the fauld (row 11 of the waist) and the top of the boot
(row 6). Nowhere else — a toothed edge on everything is a saw, not a harness.

## Net by net

**helmet.** A sallet. Rows 0..5 of sides and back, plain `9` — the skull is smooth, and this is what
keeps the flutes from covering the whole body. `top` carries three flutes front to back (`e`/`5`)
down the middle. The front is solid rows 0..2 as a heavy brow at `c`, with a `2` line under it, and
open below except one texel at each edge. `bottom` empty. Nothing on `helmet_raised`.

**chest.** Rows 0..8. Flutes down the full front, radiating is not possible at this size so keep them
parallel, with the two centre columns at `f`/`4` so the keel is still the brightest thing. Neck open
in the middle four texels of row 0. Row 8 cusped. Back the same, one band darker. Sides plain `6`.

**arm.** Rows 0..6. The pauldron (rows 0..1) carries three flutes across its `top` and front; rows
2..6 are two lames, plain, separated by `3` lines. This keeps the shoulder loud and the elbow quiet.

**waist.** Rows 7..11. Belt at rows 7..8 (`5`, `b` highlight). A fauld of two lames, fluted, with the
bottom row cusped.

**leg.** Rows 0..8. Flutes down the front face only; the sides plain `6`. Rows 7..8 a poleyn: a
two-by-two block at `d` with `2` around it, unfluted, so the knee reads as a separate plate.

**boot.** The bottom six rows, a long pointed sabaton. Row 6 cusped as the top edge. Rows 7..11
fluted lengthways on the front, plain on the sides. `bottom` (sole) `2`.

## Done means

`armorpieces_save_skin` accepted without `force`; `python tools/check_skin.py gothic` clean; looked
at on iron, gold and netherite, from the front, the side and the three-quarter — a fluted surface is
exactly the thing that reads well head-on and turns to noise at an angle, so if it does, say so; the
lessons below written, including whether one-texel flutes survived the bake on iron.

## Lessons from the session that drew it

When this session opened Blockbench, nine skin tabs were already open with unsaved edits, gothic's
among them, and its "unsaved edits" counter disagreed with what `armorpieces_skin_sheet` actually
read back (blank). `armorpieces_open_skin` with `reload: true, discard: true` produced a genuinely
empty sheet (`0 texels, 0/8 shades`) and everything below is from that fresh draw. Worth stating
plainly for whoever reads this next: **a reused tab's edit count is not proof its canvas holds
anything — read the sheet back before trusting it.**

### Value scale and contrast
`e5e5e5e5` (a 9-level jump) is exactly as extreme as advertised and it works — the flutes are the
loudest thing on the figure on all three materials, and `bake_skin.py --levels` confirms the pair
sits on the strongest 5-level band (`5`↔`e`, 34 luma, the best pair on the whole table). The keel
used `f`/`4` (11 levels) for the brightest possible ridge; the back used the same row shapes shifted
down one hex digit uniformly (`e→a`, `5→1`, `f→b`, `4→0`) rather than re-deriving a second ladder by
eye — pick one row of characters, subtract a constant from every one, and "one band darker" becomes
arithmetic instead of a second judgement call. 8 of 8 ramp shades got used across the whole skin
(helmet brow at `c`, hems at `2`, belt at `5`/`b`, poleyn at `d`/`2`, plain fields at `6`/`9`/`3`,
flutes at `e`/`5`/`f`/`4`) — the full range, not just the flute extremes.

### Flutes read head-on, stay legible at three-quarter
Checked on iron, gold and netherite from the front, then netherite again from three-quarter
(`[-26,30,-30]`). The flutes do not turn to noise off-axis: the plain `6` side faces (chest, waist,
boot, and the arm/leg sides, which never carry a flute at all) sit right next to the fluted front,
and that plain-vs-loud contrast is what keeps the silhouette readable at an angle — the eye reads
"fluted front plate, quiet side plate" rather than a field of stripes. The helmet's solid `9` skull
and `c` brow do the same job for the head. This matches the brief's own warning almost exactly: a
fluted surface covering every face would have strobed; restricting it to front/back/top saved it.

### Cusped edges
The toothed row (alternating a painted texel and a clear one) reads as a scalloped hem on all three
materials without looking accidental, at chest row 8, waist row 11 and boot row 6. One thing worth
keeping: the tooth's own value kept varying with the flute pattern already running through it
(`e.5.e.5.` on the chest, not a flat `9.9.9.9.`), so the cusp reads as the flutes cut short rather
than a separate decoration bolted onto the hem.

### The two shell-overlap notes are correct, not bugs
`check_skin.py` reported the poleyn (leg rows 7-8) and the belt (waist rows 7-8) hidden by the boot
and the chest respectively — exactly the geometry the tool's own docstring warns about. I painted
them anyway, at the rows the brief names, rather than moving them to whatever rows happen to be clear
of the outer shell. Reasoning: leg/boot and waist/chest are different armor pieces (leggings vs.
boots, leggings vs. chestplate) — a player who removes the boots or the chestplate while keeping the
other piece will see the poleyn or the belt exactly where they were painted. Hiding them behind a
*usually*-worn companion piece is the same trade vanilla already makes with its own fauld. Worth
restating for the next skin: read the note, then ask whether the two nets are the *same* equipment
slot (relocate the paint) or *different* slots usually worn together (the paint is correct and the
note is just information).

### What to watch for
- A stamp's `rows` must match its face's height exactly — chest/waist front and back are 12 rows even
  though only 9 are painted; the trailing rows have to be explicit `"........"` (or whatever width)
  rather than omitted, or the call is refused for running short. Counting rows against each face's
  declared height before sending the call, worked out in the reply text first, avoided any rejected
  stamp this run.
- Every stamp passed `shade_only: false` explicitly rather than trusting the documented default (on,
  for a vanilla-pinned silhouette) not to drop paint aimed at a transparent texel — this skin starts
  from a wholly blank sheet, so nothing was worth risking on that default. Whether the default
  actually applies to skin nets at all (the wording reads as if it targets part sockets) went
  untested, deliberately: the cost of being wrong was silently losing most of the paint.
- Plain `6`/`9` fields on every side/back face the brief doesn't ask to flute are doing real work,
  not just filling space — they're what keeps the fluted faces reading as a form rather than a
  repeating pattern.

### Did the toolchain work?
Yes. Two `stamps` calls — one per sheet, matching the profile's advice to split at the sheet boundary
rather than combine — painted the whole skin in one undo step each, 20 stamps then 9. The check came
back clean (`ok`, 8/8 shades) on the first attempt, no corrective paint call needed.
`bake_skin.py --levels` run before drawing was the single most useful input: the brief's own
`e5e5e5e5` and `f`/`4` choices are visibly the two strongest bands on that table. The one real
friction was upstream of any one tool call: the Blockbench session had eight or nine other skins'
tabs open with unsaved, apparently-phantom edits, and gothic's own tab looked complete until read
back literally. `reload: true, discard: true` fixed it in one call, but the bridge could save the
next session the diagnosis by surfacing the sheet's real texel count next to the "unsaved edits"
count whenever a tab is reused, rather than only on request.
