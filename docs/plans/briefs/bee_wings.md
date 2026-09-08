# Brief: Bee Wings

The third piece of **Armor Pieces: Animals** (`docs/plans/set-packs.md`), after Fox Ears and Frog
Mask. Read both of their Lessons sections first — everything they learned about the static layer
applies here, and this is the first piece in the pack with a metal fitting.

**Part.** `armorpieces_animals:bee_wings`, socket `pauldrons` only. Display name "Bee Wings".
Fittings: `armorpieces:guard`, **one mask covering the shoulder clasp only** — not the wings. No
effects, no loot rows.

    name: bee_wings
    anchor: pauldrons
    namespace: armorpieces_animals
    datapack: C:\Users\Matthijs\ArmorPieces\packs\animals\datapack
    resourcepack: C:\Users\Matthijs\ArmorPieces\packs\animals\resourcepack

**Shape.** `pauldrons` is a **mirrored** socket riding on the ARM bone, so model one shoulder and
the pair is made for you — and remember the pieces swing with the arm. A bee has two pairs of wings,
the rear pair markedly shorter:

- A clasp at the shoulder: a small plate, about 3 × 2 × 1, sitting against the arm's shell (the
  chestplate arm reference is the arm box inflated by 1). This is the only part that stays on the
  master, because it is the hardware the guard fitting colours.
- From it, two wings per shoulder, each its own bone off the clasp: the fore wing about 7 long × 3
  wide × 1 thick, the rear about 4 × 2 × 1, both held **out and slightly back** — perhaps 15–25° of
  Y so they trail, and a few degrees of Z so they lift. A bee's wing is a rounded blade, widest a
  third of the way out, so taper the last two cubes rather than ending square.
- Keep them clear of the `back` parts (cloak, quiver, banner) — the `armorpieces_new` reply lists
  every pauldrons envelope and the other sockets on the arm bone; the shipped `wing_cases` is the
  nearest neighbour in spirit, so read its numbers before choosing your span. Do not let a wing
  reach past the elbow.
- Nothing coplanar with the arm shell.

**Sheets.** Three:

- `bee_wings.png` — master, greyscale, the form and the silhouette. The **clasp** lives here alone
  and takes the wearer's material.
- `bee_wings_static.png` — RGBA, the bee: the wing membrane and, if you band the wing roots, the
  yellow-and-black.
- `bee_wings_guard.png` — greyscale mask, **the clasp's faces only**, shaded like the master.

The bee's palette, from `python tools/mob_reference.py bee`:

| hex | share | value | what it is |
|---|---|---|---|
| `#edc343` | 13.3% | 193 | the yellow band |
| `#fed668` | 9.8% | 213 | the lit yellow, one row at most |
| `#e4ae3b` | 5.6% | 177 | the shaded yellow |
| `#5f3225` | 15.0% | 92 | the brown fuzz — the wing roots |
| `#43241b` | 7.0% | 44 | the dark brown band |
| `#16100e` | 8.6% | 18 | near-black — the outline of a band, the wing's leading edge |
| `#f1f2e0` | 3.3% | 240 | **the wing membrane** — pale, almost white |
| `#302b37` | 4.2% | 46 | the grey-violet in the wing's shadow |

A bee's wings are nearly white with a dark edge; the yellow and black belong to the body, so use
them at the wing roots and on the clasp's surround only. Too much yellow and it reads as a wasp
costume rather than wings.

**Look at the bee once, first**: `tools/.mcassets/reference/entity/bee/bee@8x.png`. The wings are
the pale block at the top right of the net. Picture budget about six.

**What the two previous sessions learned — read before you start.**

- `armorpieces_set_part {static: true}` creates the static layer; `static_created: true` is the line
  that matters in the reply. Set the part data, **including the fitting**, before painting: that is
  what creates the mask sheet.
- The master, the static layer and the mask all take the **same `faces` dict** — same keys, same
  order. Write them as a set and change them as a set; a face in one and not the others gives you a
  grey face on a coloured wing. `[top, bottom]` on a 2-row face gives exactly those two values, no
  blur. An opaque mask pixel **wins over the static layer**, so a mask must cover only what the
  fitting should colour, and anything that must survive the fitting is a `null` hole in the mask.
- **The 3D view only ever shows the master**, so the piece renders grey all session. Judge shape in
  the viewport, trust the palette for colour, and read the static sheet once at the end with Pillow:
  equal opaque-pixel counts, colours all from the table.
- `python tools/check_part.py <name>` does **not** work for a piece in this pack — it only looks in
  the mod's resources. The bridge's check after every call, plus `check_authoring.py` with the two
  pack folders, is what there is.
- Groups cannot be renamed, and **a group's origin and rotation cannot be changed after it is
  created** — compute the pivot and the angles first, place cubes in the unrotated pose, rotate the
  bone about its base. `add_group` parents by NAME (`part`); a bone called `root` resolves to the
  scene root, so never use that name.
- **One `armorpieces_set_part` call makes everything**: the Frog Mask session got
  `sheets_created: ["part_gemstone"]` and `static_created: true` from a single call, so there is no
  reason to set the part data twice.
- **`pixels` with `value: null` on a mask punches a hole the fitting does not fill**, and the static
  layer shows through it. That is how the frog kept dark pupils inside a jewelled eye.
- **An open question you may be able to settle**: nobody yet knows whether a mask pixel *replaces*
  the master's value or is *modulated* by it. Until it is confirmed in game, do what the frog did —
  leave the master under a mask at a sensible mid value rather than blacking it out, so the fitting
  is not dimmed either way, and the piece still reads when no fitting is applied.
- **The COPLANAR check flags the PLANE, not the overlap**: a face can be flagged for lying on the
  helmet's side plane while sitting entirely in front of the helmet. Moving *outward* clears it just
  as well as moving in. A `-` note is not a `!` problem and does not need `force`.
- **Prove the sheets with Pillow before you finish**: equal opaque-pixel counts on master and static,
  each master value's pixel count matching its palette colour's count one for one, and zero static
  or mask pixels outside the master's silhouette.
- Taken as recipe centres in this pack already: `minecraft:sweet_berries`, `minecraft:lily_pad`.

**Recipe.** Centre item `minecraft:honeycomb` (unused by any template in the mod or this pack),
paper ring, craftable. Result is the `pauldrons` template.

**Done means.** `armorpieces_save` accepted without `force`;
`python tools/check_authoring.py packs/animals/datapack packs/animals/resourcepack` clean; the
Lessons section below filled in. No modpage build. Do not touch any other tab.

## Lessons from the session

Built in about 28 bridge calls, 3 of them paint (master, static, guard mask), 4 pictures (the bee
texture once, then three renders: three-quarter front, top-down, and from behind). `armorpieces_save`
accepted without `force`; `check_authoring.py packs/animals/datapack packs/animals/resourcepack` is
clean and `minecraft:honeycomb` collides with nothing.

**The one real trap: the active tab lags behind `armorpieces_new`.** The `armorpieces_new` reply
said `bee_wings` and its check was `bee_wings`, but the next two `add_group` calls landed in
**fox_ears** - the tab that had been active before. The check line appended to every mcptoolkit
reply is what tells you (it names the piece), and `get_project_info` confirms it. The repair is
`armorpieces_open <the piece you damaged> {discard: true, reload: true}`, which rebuilds it from
disk and throws the stray group away; nothing reaches disk without a save, so an accident here is
recoverable as long as you notice. Do **not** reach for `undo` to fix it: `undo` acts on whatever
project is active at that moment, and one blind undo here landed on frog_mask's paint (a `redo`
put it back). After the drift settled, `add_group` and everything else stayed on `bee_wings` for
the rest of the session. **Read the piece name in the check line of every reply's first line, and
before the first edit after `armorpieces_new`, spend one `get_project_info`.**

**Geometry.** Three bones, eight cubes. `pauldrons` rides the left arm: the bone pivot is
Blockbench (-5, 22, 0), so bone-local x = -5 - BB x and local y = 22 - BB y, and the arm shell
(the arm box inflated by 1) is x -9..-3, y 11..25, z -3..3. `base` at (-9.5, 23.15, 0) rotation 0
holds the clasp, a 1.2 x 2 x 3 plate at x -10.1..-8.9, y 22.15..24.15, z -1.5..1.5 - it sinks 0.1
into the shell so that **no face lies on x = -9**, which is the whole of "nothing coplanar with the
arm shell" (the clasp came through with no COPLANAR line at all). Two wing bones hang off it:
`wing_fore` at (-9.8, 23.4, -0.4) rotated (0, 18, -8) and `wing_rear` at (-9.8, 22.5, 0.9) rotated
(0, 27, -3). Both wings are modelled flat in the XZ plane in the unrotated pose, extending in -x
from the pivot; +18 and +27 of Y sweep them back (for a limb pointing at -x, a POSITIVE ry trails
it toward +z), and a negative rz lifts the tip. The fore wing is four cubes, 7 long: 1.6 x 0.9 x 2,
2 x 0.9 x 3 (widest, a third of the way out), 1.75 x 0.8 x 2.3, 1.65 x 0.7 x 1.2 - the leading edge
curves as well as the trailing one, and thinning 0.9 -> 0.7 over the span is what stops it reading
as a plank. The rear wing is three cubes, 4 long, half a unit lower and swept nine degrees further,
so the two never share a plane. Both roots overlap the clasp by 0.3.

**The one note accepted, not fixed:** "pair spans 33.34 across the figure, over the 18 the shoulders
span". A 7-long fore wing on a mirrored socket is a two-block span - that is what the brief asked
for and what makes it read as a bee from three metres; the check is only observing that the pair is
wider than the shoulders, as any wing must be. Everything else was clear: no COPLANAR line, and all
seven vambraces parts "clear by more than half a unit" because the wings live at y 22..24.7, well
above the elbow.

**Master + static + mask on one piece.** One `armorpieces_set_part` call did everything -
`sheets_created: ["part_guard"]`, `static_created: true`, the name, the anchor and the recipe - and
the three paints are ONE face dict written three times with different values: the master gets every
face (48), the static gets the same keys minus the clasp (the clasp is the hardware and must take
the wearer's material), and the guard mask gets the clasp's six faces alone. Keep the grey and the
hex in step, value for colour, and the Pillow read at the end is arithmetic instead of judgement:
master 150 opaque, static 118, guard 32, and 150 - 32 = 118 exactly; every static colour's count
equals its master value's count (#f1f2e0/240: 45, #302b37/46: 35, #5f3225/92: 20, #16100e/18: 10,
#edc343/193: 4, #43241b/44: 4); the nine remaining master values are the clasp's 32 pixels; 0 static
or mask pixels outside the master and 0 non-grey pixels on the two greyscale sheets. Like the frog,
the master under the mask was left at sensible metal greys (105-195) rather than blacked out, since
nobody has confirmed whether a mask value replaces the master's or is modulated by it.

**`[top, bottom]` interpolates on a face taller than two rows.** The pair is exact on a 2-row face
and only there; a 3-row face (fore_b's and fore_c's `up`, 2x3) would have produced a middle row that
is in neither palette entry and would have broken the count-for-count proof. So the wing membrane is
flat `#f1f2e0` on the big up faces, `#302b37` underneath, and the dark leading edge lives on the
`north` faces, which are 1-row strips and are the true leading edge in 3D - no orientation guessing.
That matters because **which texture row of an `up` face is the north edge is not something the check
tells you**; put directional detail on the side faces and the question never comes up. The only
2-row pairs used are the yellow-to-brown band on the two wing roots' `up` faces and the lit/shaded
rows of the clasp's `north` and `south`.

**Colour discipline.** Every colour is from the `tools/mob_reference.py bee` table, nothing invented:
membrane `#f1f2e0`, its shadow `#302b37`, the leading edge `#16100e`, the fuzz `#5f3225`, the band
`#43241b`, one row of `#edc343` at each wing root. That single yellow row is the whole of the
yellow-and-black - four pixels - and it is enough; more would have made it a wasp costume.

**For the next Animals piece:** `minecraft:sweet_berries` (Fox Ears), `minecraft:lily_pad` (Frog
Mask) and `minecraft:honeycomb` (Bee Wings) are taken as recipe centres in this pack. Nothing needed
`risky_eval` or `force`. `tools/check_part.py` still does not see this pack; the bridge's own check,
`check_authoring.py` with the two pack folders, and the Pillow read are the whole verification. And
if you are the fourth piece here: check which tab you are actually in before your first edit.
