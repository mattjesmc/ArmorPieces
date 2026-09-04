# Brief: Scale

From `docs/plans/armor-skins.md`:

> **scale** — staggered overlapping scales from the collar to the skirt, one scale about two texels.

Scale armour is a roof: small plates hung in overlapping rows so each one sheds onto the one below.
It is the most regular of the eight, and its whole quality is that the rows STAGGER — line the scales
up in columns and it turns into a grid, which is brigandine. Read [[plate]] for the value scale and
[[mail]] for how a repeating field is kept from becoming noise.

## The scale

Two texels wide, two rows tall, offset by one every second row:

    cc99cc99
    3333333
    99cc99cc
    33333333

Read that as: a scale's top row is its lit face, the row under it is the shadow it casts on the
scale below, and the next band of scales starts one texel over. In practice each band is
`c`/`9` alternating along the row with a `3` row beneath — the alternation is what makes individual
scales visible, and the offset is what makes them overlap.

Three rules:

- the scales always run the same way, downward, on every face of every net. A scale field that
  changes direction between the chest and the leg reads as two different armours;
- the topmost band of a net is `e` rather than `c`, so the shoulder line and the top of each limb
  catch the light;
- the last row of a net is `2` flat: scales end on a hem.

## Net by net

**helmet.** Scales over rows 0..6 of the sides and back — a scaled coif. The front is solid scales
rows 0..2 and open below, one texel each edge. `top` scales at `e`/`b`. `bottom` empty. Nothing on
`helmet_raised`.

**chest.** Rows 0..9. Scales the full front, back and sides, running down, unbroken. Neck open in the
middle four texels of row 0. Row 9 hem `2`. Because the pattern is uniform, the form has to come from
the sides being two bands darker than the front — do that by dropping the whole scale band, not by
shading inside a scale.

**arm.** Rows 0..7. Scales. `top` at `e`/`b`. Row 7 hem `2`. `bottom` empty.

**waist.** Rows 7..11: the scale skirt continuing, hem `2` at row 11. A belt across rows 7..8 at flat
`5` — one plain band in the middle of the field, which is what stops the torso and the skirt reading
as one wall of scales.

**leg.** Rows 0..8. Scales, hem `2` at row 8.

**boot.** The bottom six rows: scales over rows 6..9, then a plain `6` foot at rows 10..11 with a `9`
toe line — a scaled shoe is not a thing, and the plain foot is what makes the scaled shin obvious.
`bottom` (sole) `2`.

## Done means

`armorpieces_save_skin` accepted without `force`; `python tools/check_skin.py scale` clean; looked at
on iron, gold and netherite, from the front and the three-quarter — a staggered field is the pattern
most likely to alias into stripes at an angle; the lessons below written, including whether two-texel
scales are too small at four texels of arm width and what you did about it.

## Drawn 2026-09-04 — second attempt, saved clean

`check_skin.py scale` is clean (`ok`, no `!`), 7/8 ramp shades reached, values 34..238. Two paint
calls total: one `stamps` call for `humanoid` (helmet, chest, arm, boot — 19 stamps), one for
`humanoid_leggings` (leg, waist — 9 stamps). Confirmed by material preview on iron, gold and
netherite plus one greyscale three-quarter shot.

### The formula that made this mechanical

Every scaled row reduces to one rule set, applied per net independently (each net restarts its own
row-0):

- `band = row // 2`, `local = row % 2`.
- `local == 1` → shadow row, flat `3`, UNLESS it is the net's declared hem row (see below), then `2`.
- `local == 0` → scale row. `band == 0` on a net whose top is meant to catch light → tile `eebb`
  (2-wide repeat). Otherwise tile `cc99` if `band` is even, `99cc` if odd.
- The hem row is whatever row the brief names, in place of whatever the formula would have put
  there — it can land on a natural shadow-row position (chest, arm: even total row count, hem
  replaces the last shadow) or a natural scale-row position (leg, boot's transition: odd total, hem
  replaces what would have been a lit scale). Both are correct; just overwrite that row wholesale.

Chest's sides "two bands darker than the front" is simply: don't apply the `band==0` special case
there. Start the sides straight into the `cc99`/`99cc` cycle from row 0. `e`/`c` and `b`/`9` are each
exactly two ramp levels apart, so this reads as a clean shift, not a re-shade.

Top faces (helmet, arm, leg — the ones the check flags as "bare from above") got a plain 2-row
checker, `tile: ["eebb", "bbee"]`, no shadow row: they're flat-on surfaces, not a hanging edge, so
the lit/shadow logic doesn't apply, just the two brightest values alternating.

### `at` beats padding for a net that starts mid-face

The waist (rows 7..11 of 12) and boot (rows 6..11 of 12) both start well below row 0. `region`+`face`
always places row 0 at the face's top-left texel, and passing `at` alongside `region`/`face` in the
same stamp is **ignored** — `at` only works if you drop `region`/`face` and address the sheet
directly. Since the net legend gives every face's top-left sheet coordinate, this is one line of
arithmetic (`face_y + row_offset`) and it skips writing out `"........"` for six rows per face. Used
it for all 8 waist/boot side faces; saved ~50 characters of dead dots per face.

### Hidden coverage is real, not hypothetical — and the belt paid for it

The check's closing notes:

    leg: 48 painted texel(s) hidden by boot (inflate 0.9 over 0.4) - rows 6..8
    waist: 72 painted texel(s) hidden by chest (inflate 1.0 over 0.5) - rows 7..9 of back,front,left,right; rows 10..11 still show

That second one means: **the flat-`5` belt (waist rows 7..8) is completely covered by the chest net**
whenever both pieces are worn together, because chest paints through row 9 and chest/waist share the
same box position, just different inflate. The belt is not a rendering bug and the check correctly
calls it a note, not a problem — a fauld/belt on the leggings net is only ever visible below wherever
the chestplate net actually stops, which is exactly what the general tool docs already say
("a fauld is only ever the rows below the cuirass"). But it means this brief's own stated reason for
the belt ("stops the torso and skirt reading as one wall of scales") does not actually happen when
the full matching set is worn — only when the chestplate slot is empty or holds a different, shorter
piece. What DOES read as a break on the full set is the chest's own hem row (flat `2` at row 9)
immediately followed by one more scale row and the waist's own hem (row 11) — two flat rows close
together, which still breaks the field, just not via the belt colour. Left it as the brief specifies
(the belt is real, useful, and correctly painted; a future brief that wants the break to be visible on
the assembled set should have chest stop several rows earlier, e.g. row 6, so waist rows 7+ clear it).

### Read on iron / gold / netherite

- **iron**: the strongest read. `c`/`9` bake far enough apart (203/191, a small but real gap) that
  the checker alternation is obvious at a glance, staggering included.
- **netherite**: darkest but still legible — the 4-level top-band jump (`e`→`c`) is what keeps the
  shoulder/limb-top line visible here; without it the whole net would sit in one narrow dark band.
- **gold**: reads as bands more than individual scales at a distance (gold saturates `c` and `9`
  closer together than iron does), but the offset checker is still visible on closer inspection and
  does not alias into diagonal stripes at the three-quarter angle. No changes made for gold
  specifically — the brief's four-level steps carry it well enough.

Two-texel scales at four-texel arm width: two full scales across the sleeve, same conclusion as the
superseded attempt — this is the minimum for the alternation to read as scales rather than noise, and
it holds up in-game at all three materials tested.

### What was awkward in the tools

1. **`at` and `region`/`face` don't compose** — passing both in one stamp silently drops `at`
   (confirmed by re-reading the tool description, not by trial and error, but worth stating
   explicitly since the schema lists both as sibling fields on the same stamp object without saying
   one wins). A `start_row` sibling to `region`/`face` would let a stamp both validate against the
   face's real width (which raw `at` does not) and skip leading blank rows, getting the safety of
   the named form with the brevity of the raw one.
2. **No arithmetic in `tile`.** `tile: ["eebb", "bbee"]` for a checker was clean, but every graded
   scale row (the `cc99`/`99cc`/hem substitution) still had to be hand-expanded per face because the
   hem override, the top-band override and the per-net row count are three independent exceptions
   layered on one repeating rule — `tile` alone can't express "repeat this, except the last row."
   Writing them out was mechanical but long; a `tile` + `hem_row` pair of parameters (paint the tile,
   then flood-fill one named row with a value) would have cut the row-by-row transcription to
   essentially zero for every net here except the two masked ones (helmet front, chest front).
3. Otherwise the two-call, `stamps`-array shape worked exactly as documented: one call per sheet,
   19 and 9 stamps respectively, no back-and-forth needed before `check_skin` came back clean.
