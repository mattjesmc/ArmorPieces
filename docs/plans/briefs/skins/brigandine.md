# Brief: Brigandine

From `docs/plans/armor-skins.md`:

> **brigandine** — small plates riveted inside a cloth cover: a grid of rivet heads, leather straps,
> a fabric field that is flatter than the hardware on it.

A brigandine hides its armour: what you see is a cloth coat, and what tells you it is armour is the
grid of rivet heads holding the plates behind it. So this skin has two materials in one greyscale
sheet — a flat, quiet field and a hard, bright hardware — and the whole trick is keeping them far
enough apart in value. Read [[plate]] for the scale and the lessons of whatever ran before this.

## Field and rivets

The cloth is flat: `7`, with `5` in the outer columns of a side face and `9` on a `top` face. No
gradient inside it, because cloth over plates is stiff and does not curve.

The rivets are a grid: one texel at `d`, every second column and every second row, with a `3` texel
immediately below each one as its shadow. That is a three-value hardware over a one-value field,
which is what will read at distance.

    7d7d7d7d
    73737373
    7d7d7d7d

Where the rivet shadow would fall on the last row of a plate, drop it — a shadow hanging off an edge
looks like a hole.

## Straps

Leather straps are the other hardware: two-texel columns at `5` with a `2` line down each side, and a
`b` buckle texel where a strap crosses a hem. Put them where a brigandine really has them — two
vertical straps down the front of the chest and one across the waist — and nowhere else.

## Net by net

**helmet.** A kettle hat over a padded cap: rows 0..5 of the sides and back in field `7` with the
rivet grid, and a brim — row 5 painted at `b` all the way round as a single bright band, which is
the hat's edge seen from above. Front solid rows 0..2, open below, one texel each edge. `top` field
`9` with rivets at `e`. `bottom` empty. Nothing on `helmet_raised`.

**chest.** Rows 0..9 — a brigandine is a coat and hangs a row lower than a breastplate. Field with
the full rivet grid front and back. Two strap columns down the front at columns 1..2 and 5..6. Neck
open in the middle four texels of row 0, with a `4` collar line either side. Row 9 the hem: `2`, no
rivets on it.

**arm.** Rows 0..5 only — a brigandine's shoulder is short, and the bare rows below it are what
distinguishes it from plate at a glance. Field, rivet grid, `top` at `9`, row 5 hem `2`.

**waist.** Rows 7..11. A strap across rows 7..8 at `5` with a `b` buckle at the centre. Rows 9..11
field and rivets, hem `2`.

**leg.** Rows 0..8. Field and rivets — but drop the rivets on the last two rows and run a plain `9`
there, so the knee reads as a separate padded piece rather than more of the same.

**boot.** The bottom five rows: a riveted shoe. Rows 7..8 field with one rivet row; rows 9..11 plain
`6` leather with a `9` toe line. `bottom` (sole) `2`.

## Done means

`armorpieces_save_skin` accepted without `force`; `python tools/check_skin.py brigandine` clean;
looked at on iron, gold and netherite — a one-texel rivet is exactly what a narrow ramp destroys, so
if the grid vanishes on any of them, say which and by how much; the lessons below written.

## Lessons from the session

Drawn 2026-09-04, the second skin through the bridge and the first drawn in a single paint call (28
stamps, one `armorpieces_skin_paint` call for both sheets). Saved clean on the first attempt, no
`force` needed. `python tools/check_skin.py brigandine` clean; baked pairs left in `build/skins`.

### The value scale, as it ended up

The brief's values (`7` field, `d`/`3` rivet+shadow, `5`/`2` strap+border, `b` buckle/brim, `9` top,
`6`/`9` boot leather, `2` hem, `4` collar) were used exactly as written — no repainting was needed,
unlike `plate`. Checked against `bake_skin.py --levels`: `7`→`d` is 6 levels apart (strong on every
material), `7`→`2`/`3` is 4-5 apart (strong), but **`7`→`5` (field to strap fill) is only 2 levels
apart**, which the level table flags as a weak pair on some materials (chainmail gains 5 luma,
turtle_scute 9). It didn't matter here because the strap's own `2` borders (5 apart from `5`, 3 from
`7`) carry the shape — the strap reads by its edges, not by its fill contrasting the field. Where a
brief gives you a value that's numerically close to its neighbour, check whether an edge line is
doing the actual work before assuming it needs repainting.

### What the brief's exact column math produces, and why it's fine

"Two-texel columns at `5` with a `2` line down each side" at chest columns 1..2 and 5..6, on an
8-wide face, consumes **every column** (0=border, 1-2=strap, 3=border, 4=border, 5-6=strap,
7=border) — there is no plain-field column left on the chest front at all between rows 1 and 9. That
reads as intended once baked: on netherite the whole front is a dark coat-front with two straps and
a shadowed centre seam, and the field only shows at the very top (row 0, around the neck) and on the
sides/back. It looks wrong in the greyscale master (a slab of near-black) and completely fine on all
three materials — this is `plate`'s "judge the dark end on netherite, never on the master" lesson
again, but for a mid-value collision rather than a genuine near-black.

### The rivet grid, read at distance

One texel per 2x2 cell (`d` rivet over `3` shadow, on a `7` field) stayed legible on iron, gold and
netherite alike — it did not vanish on any material, which the brief specifically asked to check
for. Gold shows it crispest (the two hardware values land far apart on gold's ramp); iron and
netherite both keep it as a clear checker pattern at 4 and 8 texels wide. A single-texel rivet
surviving depends entirely on `d` and `3` being 6-7 levels from the `7` field and from each other —
if a future skin wants a subtler hardware texture, don't shrink that gap, shrink the grid's density
instead (every third row/column, not every second).

### Occlusion, measured on the rig

* **The chest (inflate 1.0) hides waist rows 7..9, not just 7..8** — one row more than `plate`'s
  cuirass, because this chest runs to row 9 (a brigandine hangs a row lower, as briefed). Only waist
  rows **10..11** show with a chestplate on, which means the belt-and-buckle at rows 7..8 is
  invisible in full harness; it only shows on leggings worn alone. Worth knowing before spending
  detail on a waist strap in any coat-length chest design: check how far the chest's hem row reaches
  before deciding how many waist rows are worth decorating.
* **The boot (inflate 0.9) hides leg rows 7..8**, exactly the two rows the brief put the plain-`9`
  knee pad on. Same shape as `plate`'s lesson but smaller: because this skin's boot only starts at
  row 7 (not row 6 as vanilla/`plate` does), leg rows 0..6 — the whole rivet grid — stay visible with
  boots on, and only the knee pad itself is boots-only decoration. A shorter boot buys a lot of
  visible leg for one row of net height.
* `chest.top`, `waist.top`, `waist.bottom`, `chest.bottom` were left unpainted, matching vanilla's
  own convention (the check's bare-face note only flags `helmet.top`, `arm.top`, `leg.top` and
  `boot.bottom` as ones every vanilla set fills) — worth trusting that note rather than painting
  every face on principle.

### What the next skin should know about the tools

* **A field/hardware skin (two materials in one sheet) is still one paint call.** 28 stamps across
  two sheets, one call, one undo step — the `stamps` array's per-stamp `sheet` field is what makes
  this possible; there was no need to split humanoid and humanoid_leggings into separate calls.
* **`rows` entries of `""` to skip to a starting row work well for a net that's only painted in its
  bottom rows** (`boot` here starts at row 7 of 12) — cheaper than computing a sheet-relative `at`
  offset, and the tool's own row-overrun refusal double-checks the count.
* Planning the rivet grid's row parity (which absolute row is a "rivet row" vs a "shadow row") by
  hand, face by face, was the actual bottleneck of this session, not the API calls — a `tile` stamp
  with `shift` might do the 2x2 checker in one line per face instead of writing out every row
  explicitly, worth trying next time a skin wants a repeating grid rather than hand-placed
  ornament.
* The brief's literal column arithmetic for the straps (which columns get fill vs border) was
  unambiguous once worked out on paper, but doing that arithmetic in the reply text first, before
  the paint call, is what made it a single correct call instead of several corrective ones.
