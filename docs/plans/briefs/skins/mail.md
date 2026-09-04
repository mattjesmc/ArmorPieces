# Brief: Mail

From `docs/plans/armor-skins.md`:

> **mail** — riveted mail over a padded gambeson: a two-texel weave, a coif, a mail skirt. It is
> also the answer to chainmail's dead ramp — the material with no colour range gets the skin whose
> whole content is texture.

Mail is the opposite problem to plate. It has no flat surfaces and no edges: it is one material,
everywhere, and what makes it read is a repeating weave plus the fact that it HANGS. Follow
[[plate]]'s value scale — that brief sets it — and read its lessons before starting.

## The weave

A riveted ring is smaller than a texel, so the weave is a lie that reads at distance: a two-texel
checker, one step apart, offset by one every row.

    a7a7a7a7
    7a7a7a7a

Two values one step apart, no more, or it turns to noise. The weave is the FIELD; the range comes
from what is done to it, not from within it:

- a face's `top` runs the weave two bands lighter (`c`/`9`) — mail catches the light on the
  shoulders and nowhere else;
- the outer columns of every side face drop two bands (`5`/`3`) as the body curves away;
- the last row above a hem is `2` flat, so the mail reads as ending rather than fading;
- three or four `e` texels on the shoulder tops, and nothing else that bright.

The check will still want the range: make sure the deepest recess really is `0`-`2` somewhere, at
the hems and under the coif.

## Net by net

**helmet.** A coif, not a helmet: the weave over rows 0..7 of both sides and the back, all the way
down — mail does not stop at the ear. The front is solid weave across rows 0..2 and open below it,
with a two-texel column of weave at each edge framing the face. `top` is the weave at `c`/`9`.
`bottom` empty. Nothing on `helmet_raised`.

**chest.** A haubergeon, so it runs a row lower than plate does: rows 0..9. The weave everywhere,
with the shoulder tops light and the sides dark. Row 0 leaves the middle four texels open for the
neck. Row 9 is the hem: `2`. Underneath the weave, at the very edges of the front, one column of
`8` flat — the gambeson showing past the mail.

**arm.** Rows 0..7, a full mail sleeve to the elbow. Weave; `top` at `c`/`9`; row 7 the hem at `2`.
`bottom` empty.

**waist.** Rows 7..11: the mail skirt continuing down, weave, with the last row `2`. A belt across
rows 7..8 at flat `5` with a `b` buckle-line highlight, so there is one man-made straight line in a
skin that otherwise has none.

**leg.** Rows 0..8, mail chausses: weave, `top` light, the outer columns dark, row 8 hem `2`.

**boot.** The bottom six rows. Rows 6..8 mail over the ankle; rows 9..11 a leather shoe, flat `6`
with a `9` line along the top of the toe — the contrast between woven and smooth is what makes both
of them legible. `bottom` (sole) `2`.

## Done means

`armorpieces_save_skin` accepted without `force`; `python tools/check_skin.py mail` clean; looked at
on iron, gold and netherite, and on **chainmail** as well — this is the skin that has to rescue that
material; the lessons below written, including whether the weave survived the chainmail ramp.

## Lessons from the session

Drawn 2026-09-04, the second skin through the bridge and the first drawn *from* plate's lessons
rather than discovering them. It cost **three paint calls and six pictures**, and nothing had to be
repainted at a new value scale. The reason is entirely section one below.

### The brief's "bands" are two levels; the real band is four. They reconcile exactly.

This brief is written in bands of about two levels (`a`/`7` weave, "two bands lighter" = `c`/`9`,
"drop two bands" = `5`/`3`). Plate's lesson says two-level steps bake identical. Both are right,
because **the brief's "two bands" is one four-level step**. Everything here was drawn on a ladder of
three weave bands, each four levels wide internally and four levels apart in the mean:

    dark weave    2 / 6      mean 4     side back-columns, the drape under the coif, the arm cuff
    mid weave     6 / a      mean 8     the field: every front, back and side
    lit weave     a / e      mean 12    every `top` face, and one row at the crown/shoulder line

No `f` anywhere: `e` and `f` bake within 2 luma of each other on iron *and* chainmail, so a spark
above the lit weave's own `e` costs a texel and buys nothing. The brief's "three or four `e` texels
on the shoulder tops" is satisfied by the lit weave itself, which only ever appears on top faces.

Do not take the step sizes from `bake_skin.py --contrast`'s summary line. It reports the *worst*
3-level step (3 luma) and the *worst* 4-level step (15 luma), but which levels are flat is
material-specific and the LUT interpolates, so particular pairs are far better than the worst case.
Compute the actual per-level luma table before choosing — `bake_skin.table(material)` is a 256-entry
LUT and level `i` sits at index `i*17`:

    python -c "import sys;sys.path.insert(0,'tools');import bake_skin as b;
    t=b.table('chainmail');print([round(b.luma(t[i*17])) for i in range(16)])"

Ranked over all eight materials, the best pairs four levels apart or closer are `a`/`e` (worst 27
luma), `1`/`5` (24), `6`/`a` (24), `9`/`d` (23). The three used here are from that list. `3`/`5`,
which the brief asks for as the dark side columns, buys **1 luma on gold** and was replaced by
`2`/`6` (worst 18).

### The weave

"A two-texel checker ... offset by one every row" was drawn as a **brick**, not a diagonal: cells
two texels wide, the phase shifted by one on odd rows only.

    aa66aa66
    a66aa66a
    aa66aa66

Shifting by one on *every* row gives a 45 degree twill that reads as diagonal stripes on a 4-wide
limb. The brick reads as staggered rings, and at 16 texels the two values resolve into little
plus-shaped links — it genuinely looks like mail from a normal camera distance. Generating this from
a two-line Python function and pasting the JSON into `stamps` is the whole technique: 29 faces,
three calls.

**It rescues chainmail.** That was the brief's actual test and the answer is yes, emphatically:
chainmail's dead ramp is dead in the *middle* (`6`-`8` are one colour), but `2`-to-`6` is 41 luma on
chainmail and `6`-to-`a` is 31 — the largest of any material for those pairs. The skin whose content
is a two-value weave in exactly those bands comes out with *more* texture on chainmail than on iron,
where the same pairs buy 39 and 24. Chainmail is the best-looking material for this skin.

### What read badly in 3D, and the fix

* **The first pass lit rows 0..1 of every net plus every `top` face.** From a three-quarter camera
  the arm became a solid white box — plate's "white sticker" again, arrived at from a different
  direction. On a small net, `top` plus two lit rows is most of what is visible. Fixed by cutting
  the lit rows back to row 0 only on chest and helmet, and to *nothing* on the arm: the arm is mid
  weave from row 0, lit on `top` alone. That one call is the entire difference between "hooded
  figure" and "man in a marshmallow".
* Nothing else needed changing. Big value steps chosen up front meant no repaint.
* Gold is the weak material here, not iron: gold's `2`, `4` and `5` sit within 12 luma, so the
  hems and the leather shoe soften. They still read, because a *solid* row against a *woven* field
  reads by texture even when the values converge. That is worth remembering — smooth-versus-woven
  is a second channel that survives a flat ramp, and this skin leans on it at the shoe and the belt.

### Departures, and why

* **Dark side columns `2`/`6`, not `5`/`3`** — `3`/`5` is 1 luma on gold. Same intent, real contrast.
* **The leather shoe is flat `4` with a `c` welt line, not flat `6` with a `9` line.** `6` is the
  weave's own dark texel, so a flat `6` shoe reads as an unlit patch of mail rather than a different
  material. `4`/`c` makes the shoe dark and smooth under a bright straight welt, which is the
  "woven versus smooth" contrast the brief wanted. The sole is `0`, not `2`, to anchor the ramp's
  dark end (plate did the same).
* **The belt highlight is `d`, not `b`.** `b` and `c` are one colour on iron *and* chainmail; `d`
  against the `5` belt is 56 luma on iron. It is a 4-texel buckle plate on `waist.front` row 8 —
  the one asymmetric, man-made thing on the skin.
* **The lit weave is `a`/`e`, not `c`/`9`,** for `top` faces, so top faces sit a full band above the
  field rather than three levels.
* `chest.top` is painted (vanilla leaves it empty): a coif drapes over the shoulders, so the lit
  weave there is the point rather than a freebie. Still mostly swallowed by the helmet.
* Leg rows 0..1 are dark weave — the shadow the mail skirt casts on the thigh. Cheap, and it makes
  the chausses read as hanging under something.

### Occlusion, confirmed and extended

Plate measured this; mail hits it harder because the haubergeon is a row longer.

* **chest rows 0..9 (the haubergeon) hide waist rows 7..9.** The check says so exactly. That leaves
  the mail skirt **two rows**: waist row 10 (weave) and row 11 (hem `2`). The belt and its buckle at
  rows 7..8 are only ever seen by a player wearing leggings without a chestplate. Drawn anyway, as
  briefed — but a skin that wants a *visible* belt has to put the chest at rows 0..8, or put the
  belt at waist rows 9..10 and accept no skirt.
* Boot rows 6..11 hide leg rows 6..8, so the leg's hem row 8 is decorative. Same as plate. For mail
  it matters less: the boot's own rows 6..8 are the same weave, so the chausse and the boot read as
  one continuous mail leg ending in a shoe, which is what was wanted.

### What the next skin should know

* **Generate the sheet with a script and send it as `stamps` JSON.** A repeating field (weave,
  scales, lamellae, quilting) is a function of `(x, y, band)`; writing 29 faces by hand is where the
  turns go. Three calls, and the second and third were corrections, not construction.
* An empty string in `rows` skips a row; it is how you reach `boot` row 6 or `waist` row 7 without
  touching sheet coordinates. Used on every hanging net.
* Judge on **chainmail** as well as iron for anything textural. It is not simply "the flat one" —
  its ramp is flat in the middle and steep at both ends, so it punishes mid-tone gradients and
  rewards two-value fields. The opposite of iron, which is flat at `7`-`8` and `b`-`c` but broad
  elsewhere.
* Ask for the per-level luma table before drawing, not the `--contrast` summary.

### Tools: what was awkward

1. **`bake_skin.py --contrast` under-sells itself.** It prints one worst-case number per step size,
   which says "3 levels is useless" when in fact `7`-to-`a` is 29 luma on chainmail and 14 on iron.
   The genuinely useful artefact is the 16x8 luma table, and it had to be computed by hand with a
   `python -c` against `bake_skin.table()`. **`--levels` should print that table**, and ideally a
   ranked list of the best pairs at each step size. That one command would have replaced the only
   piece of real analysis in this session.
2. `armorpieces_skin_paint` has no way to say "this face, this band, procedurally". Not a real
   complaint — generating rows externally works — but a `pattern` stamp (checker/brick with two
   levels and a phase) would compress the common case enormously.
3. The occlusion notes are excellent and were trusted without re-deriving them. They should say
   which rows *remain visible*, not only which are hidden: "waist rows 7..9 hidden, 10..11 visible"
   is the number the author actually needs.
4. `armorpieces_skin_material` returning its own screenshot is exactly right and made the four
   material checks four turns instead of eight.
5. Minor: the check lists `helmet_raised` as "nets with nothing on them" on every single call. It is
   correct-by-default for almost every skin; it could be silent unless the brief touched it.
6. Bash heredocs die in this environment on any apostrophe-heavy text, so this file was written with
   the Write tool and concatenated. Worth knowing before drafting lessons.
