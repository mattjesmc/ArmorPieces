# Brief: Plate

The first armor skin, and the reference the other seven are judged against. From
`docs/plans/armor-skins.md`:

> **plate** — the reference. A cheek-wrapping bascinet with the face open, a one-piece breastplate
> with a raised centre ridge, layered pauldrons, sabatons — netherite's silhouette redrawn
> deliberately across the whole range rather than netherite's sheet reused.

This is a fifteenth-century harness: hard, smooth, jointed, and read at sixteen texels. Everything
about it is **big value steps**, not gradients. Three or four bands per face is a shape; twelve rows
of a smooth fade is mud.

## The value scale

Set it here, because every later skin follows it:

    0-2   the deepest recess: the gap between two lames, under a lip, the sole of a boot
    4-6   a side plane turned away from the light, the shadowed half of a curved surface
    8-a   the mid field, most of what a plate is
    c-e   a lit top surface, the crest of a ridge, the edge highlight along a lame
    f     a specular texel. A handful on the whole skin, on the shoulder and the brow, or none

Light is from above: a face's `top` is one band lighter than its `front`, and its `right`/`left` are
one band darker. Keep that consistent and the figure reads as one object.

## Net by net

**helmet.** A bascinet. Rows 0..5 of the sides and back are the skull, mid field with a lighter row
at the crown. Below that the sides keep going: rows 6..7 stay painted for the two columns nearest
the front, and those are the cheeks — that wrap is the one thing netherite gets right that iron does
not. The front is solid across rows 0..2 (the brow), and open from row 3 down except a one-texel
column at each edge, which is the inside of the cheek. `top` is fully painted with a raised comb: two
texels down the middle at `d`-`e`, the rest `9`-`a`. `bottom` stays empty. Do not touch
`helmet_raised`.

**chest.** Rows 0..8; leave 9..11 for the waist. The front is a one-piece breastplate with a keel: a
two-texel centre column at `c`, falling to `9` either side, and `6` in the outer columns where the
curve turns away. Row 0 leaves the middle four texels open — that is the neck. Row 8 is the lower
lip of the breastplate: a dark `4` line across, with a `b` highlight row just above it. The back is
the same construction, one band darker overall. Sides are `6`-`7` with a lighter column at the front
edge. `top` is the shoulder line: `c`, with `9` where it meets the neck.

**arm.** One net, both arms. Rows 0..6, drawn as three lames: rows 0..1 the pauldron, `c` with an
`e` top edge; row 2 a `3` gap; rows 3..4 the second lame, `a`; row 5 a `3` gap; row 6 the last lame,
`8`. `top` full at `d` — that is what is seen from above and it does more work than any other face
here. `bottom` empty.

**waist.** Rows 7..11 only. A belt across rows 7..8 (`5` with a `b` highlight row), then a fauld of
two hanging lames: rows 9..10 at `9` with a `3` line under each. The bottom row is the fauld's edge,
`6`.

**leg.** Rows 0..8. A cuisse: mid field `9`, a `c` highlight column down the front centre, `5` at
the sides. Rows 7..8 are the poleyn, a knee disc — a two-by-two block at `c` with `3` around it, so
it reads as a separate plate rather than a stain.

**boot.** The bottom six rows. A sabaton: rows 6..8 the ankle at `8`, rows 9..11 the foot at `a`
with a `d` line along the top of the toe. `bottom` (the sole) fully painted at `2`. `top` empty.

## Done means

`armorpieces_save_skin` accepted without `force`; `python tools/check_skin.py plate` clean; the skin
looked at on iron, gold and netherite with a screenshot of each; the lessons below written.

## Lessons from the session

Drawn 2026-09-04, the first skin through the bridge. What was drawn matches the brief net by net
except where noted below.

### The value scale, as it ended up

The brief's five bands are right, but the **step size between two adjacent fields is what matters,
not the band they sit in**. The first pass used three-step differences (`6` field / `9` mid / `c`
crest) and it looked correct in greyscale and *vanished on iron*. `bake_skin.py --report` says why:

    iron    818181 909090 999999 bababa bababa cbcbcb cbcbcb e5e5e5

iron's eight shades contain two duplicated pairs, so a third of the ramp is flat. `9` bakes to
~`bd` and `c` bakes to `cb` — fourteen levels apart, invisible at 16 texels. Everything was
repainted with **four-to-five-step jumps** and it read on all three materials at once:

    1      the sole only - it exists to anchor the ramp's dark end so the check reaches 8/8
    2      a real recess: the lame gaps, the articulation line at the knee, the lip under the
           breastplate, the fauld gap. On iron these are the only lines that stay dark
    4-5    a plane turned away: the outer columns of the breastplate, the chest sides, the
           cheek bottoms, the belt under the cuirass
    7-9    the mid field, most of the armor
    c-d    lit: the keel, the shoulder line, every `top` face, the toe of the sabaton
    e      an edge that catches light along one row: the pauldron's top lame, the brow
    f      four texels on the whole skin - two on the pauldron top, two on the brow

**The next skin should pick its values from that list and not from between them.** `6` next to `9`
is not a value step on iron; `4` next to `9` is. Gold and netherite forgive three-step work, iron
does not, and iron is the one everybody wears.

Light from above held throughout: `top` faces are `c`-`d`, fronts `8`-`9`, sides `4`-`5`, and the
back plate one band under the front. The front-edge column trick (one column of a `right`/`left`
face lifted a band, on the column that borders the front face in the net band) is cheap and makes
the torso and the greaves look round rather than boxy. In the net's column order the band runs
right → front → left → back, so the front edge is the **last** column of `right` and the **first**
column of `left`.

### What read badly in 3D, and the fix

* **A 2x2 patch of `f` is a white sticker,** not a specular. On the pauldron top it read as a hole
  in the armor on iron. Reduced to one `f` inside a `d`/`e` dome and it became a highlight.
* **The back plate at `3` went black.** "One band darker overall" applied to values already near
  the bottom pushes the outer columns off the ramp. Darken the *mid*, keep the outer columns at
  `4`, and give the back its own lit centre.
* **Solid black gap lines everywhere read as stripes on a sleeve.** They became lames once each
  lame got a lit top row falling to a darker body (`e`→`a`, gap, `d`→`9`, gap, `c`), i.e. the gap
  is only half the trick; the overlap edge below it is the other half.
* Three or four bands per face is right. Every face on this skin is 2-4 values and nothing is a
  gradient.

### Occlusion, measured on the rig - this is the most useful thing here

The four shells overlap and the bigger inflate always wins. Things that were painted and then
turned out to be invisible with the full set on:

* **The boot (inflate 0.9) completely hides leg rows 6..11 (inflate 0.4).** The brief's poleyn at
  leg rows 7..8 exists only for a leggings-without-boots player. It was drawn anyway, as briefed,
  but a knee that is meant to be seen in a full harness has to live at **leg row 5 or above**, or
  the boot has to be shortened to rows 8..11. Whoever writes `gothic` and `milanese` should decide
  this before drawing.
* **The cuirass (inflate 1.0) hides waist rows 7..8 (inflate 0.5).** The belt is under the
  breastplate by construction, exactly as vanilla does it. Only waist rows **9..11** are ever seen
  with a chestplate on, so the fauld has three rows to work in and no more: one lame, one gap, one
  edge.
* `chest.top` is painted here and is a departure - vanilla leaves it empty. It is almost entirely
  swallowed by the helmet; it costs nothing and shows a sliver at the neck. Not worth repeating
  unless the design wants a gorget.
* The arm net is 4 wide and both arms use it, so from a side camera the near arm hides the whole
  chest side face. Detail spent on `chest.right`/`chest.left` is only seen in motion.

### Departures from vanilla's row table

* Helmet sides carry rows 6..7 on the two front columns (the cheek wrap) and a dark rim at row 5,
  where iron stops at row 4. That is netherite's silhouette, deliberately.
* Helmet back stops at row 5 with no neck lame, so the cheeks read as separate plates.
* Everything else sits on vanilla's lines: chest 0..8, arm 0..6, waist 7..11, leg 0..8, boot 6..11.

### What the next skin should know about the tools

* `region` + `face` painting is the right interface; an empty string `""` in `rows` skips a whole
  row, and a SPACE skips one texel, so `["", "", "", "", "", "", "", "4444dd44", ...]` is how you
  reach waist row 7 without counting sheet coordinates, and a second pass can drop rivets onto a
  finished field. Both were used constantly.
* Rewriting a face is one call. Rewriting the whole skin at a new value scale was ~25 calls and
  about ten minutes; do not be precious about the first pass.
* `armorpieces_skin_material` + `capture_screenshot` is the only honest test. Judge on **iron
  first**, not last - greyscale flatters everything.
* `bake_skin.py --report` should be read before drawing, not after. It is the actual specification
  of how much contrast a value difference buys.
