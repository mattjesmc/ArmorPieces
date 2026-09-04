# Brief: Gambeson

From `docs/plans/armor-skins.md`:

> **gambeson** — a quilted textile jack, no metal at all. Vertical quilted channels, soft edges, the
> least-armored pole, and the proof that the ramp is not only for steel.

A gambeson is stuffed linen stitched into vertical tubes. It is the softest thing in the set and the
one that must NOT look like plate: no hard edge highlights, no specular texels, and every value step
should sit inside a channel rather than along a seam. Follow [[plate]]'s value scale and read its
lessons and [[mail]]'s first.

## The quilting

Vertical channels two texels wide, seams one texel between them:

    99cc99cc  -> no. Seams first:
    5aa5aa5a

A channel is `a` in the middle, `8` at its shoulders, and the seam between two channels is `4`. The
whole surface is that, repeated, and the form comes from moving the whole band up or down:

- `top` faces one band lighter: channels `c`, seams `6`;
- the outer column of each side face two bands darker;
- the bottom hem of every garment is `2` — cloth ends in shadow, it does not catch a highlight;
- nothing above `d` anywhere on this skin. It is not shiny.

## Net by net

**helmet.** An arming cap: rows 0..5 of sides and back only — a gambeson does not armour the jaw,
and leaving rows 6..7 bare is the point, because it makes the padded silhouette read as smaller than
plate's. The front is solid rows 0..2, open below. `top` quilted at `c`/`6`. `bottom` empty. Nothing
on `helmet_raised`.

**chest.** Rows 0..9 — a jack hangs longer than a breastplate. Vertical channels the full width of
the front and back, running unbroken from row 1 to row 8. Row 0 leaves the middle four texels open
for the neck and is `6` either side (the collar roll). Row 9 is the hem, `2`. The sides are two
channels, dark.

**arm.** Rows 0..8, a full padded sleeve. Channels run vertically here too, so the arm and the body
read as the same garment. `top` full and light; row 8 hem `2`; `bottom` empty.

**waist.** Rows 7..11, the skirt of the jack: the same channels continuing, hem at row 11 in `2`. A
belt across rows 7..8 in flat `5` with a `9` highlight — one hard line, no more.

**leg.** Rows 0..8: padded hose, channels, hem `2`.

**boot.** The bottom four rows only — a soft shoe, not a sabaton, and the shorter boot is a
deliberate contrast with plate's. Rows 8..11 at `6` with a `9` line along the top of the toe.
`bottom` (sole) `3`. Leaving rows 6..7 bare shows the padded hose above the shoe, which is right.

## Done means

`armorpieces_save_skin` accepted without `force`; `python tools/check_skin.py gambeson` clean;
looked at on iron, gold and netherite, and on **leather**, which is the material this skin is really
for; the lessons below written, including whether a skin with no highlights above `d` still passes
the ramp check and still reads in 3D.

## Lessons from the session
Drawn 2026-09-04, the third skin through the bridge. **Three paint calls and six pictures**; nothing
was repainted at a new value scale, and the one correction pass was a shape note, not a contrast one.

### The value scale: five levels, and the brief's bands are still four levels wide

This brief writes the quilt as `a` channel / `8` shoulder / `4` seam and caps the skin at `d`.
Reconciled with plate's and mail's measured rule the same way mail did — the brief's "band" is one
four-level step — and it collapses to **five levels for the entire skin**:

    1        the sole, and nothing else. It exists to reach the ramp's dark end
    2 / 6    DARK quilt   seam / channel   side faces, the row above every hem, and flat `2` hems
    6 / a    MID quilt    seam / channel   every front and back: the field
    9 / d    LIT quilt    seam / channel   every `top` face, and nothing else
    5        the belt body, and the shoe: the two smooth (unquilted) things on the skin
    a        the shoe welt

Every adjacent pair here is off `bake_skin.py --levels`'s ranked list: `2`-`6` (18 luma worst),
`6`-`a` (24), `5`-`a` (30), `9`-`d` (23). The two 3-level steps that carry the form — mid channel
`a` to lit channel `d` (14 worst) and mid seam `6` to lit seam `9` (12 worst) — were checked
individually against the table before use rather than taken from the summary line, which would have
called them useless. That is the same trap mail flagged; **`--levels` now prints the table and the
ranked pairs, and it made this the cheapest analysis of the three sessions.** One Bash call replaced
mail's hand-written `python -c`.

### Does a skin with nothing above `d` still pass the ramp check, and still read?

**Yes to the check, and yes in 3D — this was the brief's actual question.** The check reports
`values 17..221, 7 of 8 ramp shades` and marks it a `-` note, not a `!`. Reaching 8/8 needs a texel
at `e` or `f`; the eighth shade is the *only* thing a no-highlight skin gives up, and the check does
not treat that as a problem. The `!` is for a narrow *band*, and 1..d is not narrow.

It reads because the range is spent downward instead of upward: the sole at `1` and the hems at `2`
anchor the dark end, so the skin still spans 17..221 in master values. **Ceiling `d` costs almost
nothing anyway** — `d` to `e` is 13 luma on iron and 14 on netherite, and `e` to `f` is 2 on every
material. The visible difference between this skin and plate is not the missing `e`, it is that
nothing here is a *hard line*: no one-texel bright edges, no specular dots. That is what makes it
look like cloth, and a future skin that wants "matte" should copy the ceiling AND the absence of
one-texel highlight rows, not just the ceiling.

### The quilting: make the loop divisible by three, then make the face symmetric

A channel is 2 texels, a seam is 1, so the pattern has period 3, and the torso loop is
right(4) + front(8) + left(4) + back(8) = **24 columns, which is divisible by 3**. That is a gift and
it should be used: pick

    8-wide face   c c s c c s c c     "aa6aa6aa"
    4-wide face   s c c s             "6aa6"

and every corner of the torso comes out with 2-wide channels and 1-wide seams all the way round, no
doubled seam anywhere, and both the 8-wide and the 4-wide face is symmetric under reflection. Check
it: right ends `6`, front starts `a`; front ends `a`, left starts `6`. Perfect wrap.

The limbs are 4+4+4+4 = 16, **not** divisible by 3, so the same two patterns give a 2-texel seam at
each of the four corners. That was accepted rather than fixed: on a soft garment a doubled dark
texel at a vertical corner reads as a crease, which is what a padded sleeve does. Do not try to
force period 3 round a 16-column loop; the discontinuity has to go somewhere and a corner is the
best place for it.

Symmetry matters more than phase continuity on the 8-wide front. A period-3 pattern that wraps the
24-column loop cannot also be mirror-symmetric across the chest; `aa6aa6aa` happens to be both, which
is why it was chosen over the brief's `5aa5aa5a`.

### What read badly in 3D, and the fix

* **A flat `2` hem under an `a` field is black tape, not a shadow.** In greyscale and on iron it was
  fine; on netherite (`2` bakes to 19) the chest hem, the arm cuff and the cap brim were three hard
  black rings and the softest skin in the set had the hardest lines on it. Fixed with one call:
  the row *above* every hem became the dark quilt band (`2`/`6`), so a hem now steps
  `a` -> `6` -> `2` over three rows and reads as a rolled, shadowed edge. **A hem is two rows, not
  one.** Plate learned the same thing about lame gaps ("the gap is only half the trick"); this is
  that lesson at the bottom of a garment. The chest already had it because the brief asked for a
  dark row 8; the arm, the helmet and the leg did not, and needed it.
* **Nothing else needed changing.** No white-sticker problem this time, despite every `top` face
  being the lit band: `d` is not `f`, and a lit band whose own seams are `9` has internal texture,
  so a fully-lit 8x8 helmet top still reads as a quilted cap rather than a lamp.
* Gold is again the weak material (its `2`-`4`-`5`-`6` sit inside 18 luma) so the shoe barely
  separates from the hose. It survives on texture, exactly as mail predicted: smooth-versus-quilted
  is a second channel that outlives a flat ramp. Leaning on that is now a reliable technique, not a
  lucky escape.
* Leather is the right material for this skin and it is undyed grey by default, which is a slightly
  disappointing preview — the shape reads beautifully but the *point* of a gambeson on leather is a
  dyed one, and there is no way to preview a dye through the bridge.

### Departures from the brief, and why

* **Lit band is `9`/`d`, not the brief's `6`/`c`.** Same intent (one band lighter), measured step.
* **Dark band is `2`/`6`, not `4`/`8`.** `4`-`8` is a fine pair but `2`-`6` puts the hem and the
  dark band on the same two levels, so the whole skin is five values instead of seven.
* **The sole is `1`, not `3`.** Anchors the ramp's dark end, as plate and mail both did.
* **The shoe is flat `5` with an `a` welt, not `6` with a `9` line.** `6` is the quilt's own seam
  value, so a `6` shoe reads as an unlit patch of quilting — mail hit this exactly and the fix is the
  same one. `5`/`a` is 30 luma worst-case and the shoe now reads as a different material.
* **The chest side faces are one channel, not two.** A 4-wide face fits one 2-wide channel between
  two seams; two channels would need five columns. Drawn as `2662` (dark band) so the torso rounds
  away at both corners.
* **The belt is `9` over `5`, two flat rows,** the lit edge on top. No buckle: the brief said one
  hard line and this skin cannot afford two. It is invisible under the chestplate anyway (below).
* **The leg gets a dark band at row 7 and its `2` hem at row 8 is under the boot.** So the visible
  hose ends in the dark band where it enters the shoe, which is better than the hem it was meant to
  end with.
* Rows follow the brief throughout: helmet sides/back 0..5 and front 0..2, chest 0..9, arm 0..8,
  waist 7..11, leg 0..8, boot 8..11. Arm 0..8 and boot 8..11 are both departures from vanilla, both
  asked for, and the short boot is the best decision in the brief — see below.

### Occlusion: the short boot is the fix plate and mail both wanted

Plate and mail each reported that the boot (inflate 0.9) swallows leg rows 6..11 and that a knee has
nowhere to live. **This brief's four-row boot solves it.** The check says: `leg: 16 texels hidden by
boot - row 8; rows 0..7 still show`. Sixteen texels lost instead of a hundred and ninety-two. Any
skin that wants detail on the shin or the knee should shorten its boot to rows 8..11; it costs one
row of leg and buys eight. `gothic` and `milanese` should read this before drawing.

The chest still eats the belt: `waist rows 7..9 hidden, 10..11 visible`. Chest 0..9 leaves the skirt
two rows, and the right move was to make row 10 the *mid* quilt (not a dark transition) so the one
visible skirt row is a bright continuation of the jack, with the `2` hem under it. A dark row 10
would have made the entire visible skirt a shadow.

### Tools

1. **`--levels` printing the 16x8 luma table and the ranked pairs is the single best change to this
   toolchain.** It is exactly what mail asked for, it arrived, and it turned the contrast decision
   from ten minutes of `python -c` into reading four lines. Keep it. The one thing still missing:
   the ranked list stops at 5 levels apart and only shows the top three per step size — a `--pair
   6 a` mode that prints one pair across all eight materials would close the loop, since every
   real decision here was "is *this* pair good enough", not "what is the best pair".
2. **The occlusion notes now say what remains visible** (`rows 0..7 still show`) — mail asked for
   that too, and it is the number the author actually uses. It decided the leg hem question in one
   read.
3. `helmet_raised` no longer clutters the notes when untouched. Also fixed since mail.
4. **`stamps` with leading `""` rows is still the whole interface.** The entire skin is three calls:
   20 stamps for `humanoid`, 9 for `humanoid_leggings`, 12 for the hem correction. Worth noting that
   a stamp can carry its own `sheet`, so the third call edited *both* sheets in one undo step, which
   is what made the hem fix a single turn.
5. Still no procedural stamp. For quilting it did not matter — a 3-texel period is short enough to
   type — but `mail`'s brick and this skin's channels are both `f(x)` fields and a `pattern` stamp
   (two levels, a period, a phase) would have written both from one line. Third session asking.
6. The greyscale master view **overstates the dark end badly**: `2` is 34 in the master and 137 on
   iron. Every dark decision looked wrong in greyscale and right on iron, and the hem problem was
   invisible in greyscale *and* on iron and only appeared on netherite. **Judge dark ends on
   netherite, mid-tones on iron, and never on the master.** That is the counterpart to plate's
   "judge on iron first".
