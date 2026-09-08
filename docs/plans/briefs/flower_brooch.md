# Brief: Flower Brooch

The fifth piece of **Armor Pieces: Animals** (`docs/plans/set-packs.md`), after Fox Ears, Frog Mask,
Bee Wings and Turtle Shell. The only piece in the pack taken from a plant rather than an animal —
it is the flower the bees live on, and it is what makes the set a menagerie rather than a zoo.

**Part.** `armorpieces_animals:flower_brooch`, socket `collar` only. Display name "Flower Brooch".
Fittings: `armorpieces:gemstone`, **one mask covering the flower's centre only** — the pollen. No
effects, no loot rows.

    name: flower_brooch
    anchor: collar
    namespace: armorpieces_animals
    datapack: C:\Users\Matthijs\ArmorPieces\packs\animals\datapack
    resourcepack: C:\Users\Matthijs\ArmorPieces\packs\animals\resourcepack

**Shape.** `collar` is **not** mirrored: model the whole thing. A poppy pinned at the throat:

- A bloom of **four or five petals** around a centre, facing forward and slightly up, as if pinned
  to the collarbone on the wearer's right of centre — not dead centre, which reads as a medal.
  Each petal is its own cube, 2–3 wide × 2 high × 1 thick, on its own bone rotated out from the
  centre so the bloom is a shallow cup rather than a flat disc. Rotate the bones, not the cubes.
- A **centre boss**, 2 × 2 × 1, standing a quarter texel proud of the petals. This is the gemstone's
  face and the only thing the mask covers.
- A short **stem and one leaf** falling from the bloom along the collarbone, a texel wide — this
  plus the petals is what makes it a flower rather than a rosette.
- `collar` already carries `brooch`, and this must not read as a second one: `brooch` is metal
  hardware, this is a bloom. Read its envelope in the `armorpieces_new` reply and sit clear of it.
  `scarf`'s wrap plane is at **x ±5.5** and the leggings surface at **x ±4.5** — the Turtle Shell
  session hit both; a small collar piece should never come near either, but the check will say so.
- Nothing coplanar with the chestplate shell.

**Sheets.** Three:

- `flower_brooch.png` — master, greyscale, form and silhouette. The **pin and the boss's rim** are
  the only hardware; keep them here so they follow the armor.
- `flower_brooch_static.png` — RGBA, the flower: petals, stem, leaf.
- `flower_brooch_gemstone.png` — greyscale mask, **the boss's outward faces only**.

The poppy's palette, from `python tools/mob_reference.py poppy` — it is a 16×16 block texture and
only eight colours, which is why a poppy reads at any distance:

| hex | share | value | what it is |
|---|---|---|---|
| `#ed302c` | 25.7% | 104 | the petal red — most of the bloom |
| `#bf2529` | 14.3% | 84 | the shaded red — petal edges and the cup's inside |
| `#9b221a` | 11.4% | 69 | the deepest red — where petals meet the centre |
| `#742303` | 2.9% | 56 | the brown-red, one or two texels at the very centre's rim |
| `#204626` | 20.0% | 55 | the dark green — the stem's shaded side |
| `#265a25` | 14.3% | 68 | the mid green — the stem and the leaf |
| `#4a8f28` | 8.6% | 111 | the lit green — the leaf's top edge |
| `#2b702a` | 2.9% | 83 | between the two greens, for one seam |

**Look at the poppy once, first**: `tools/.mcassets/reference/block/poppy@8x.png`. Note how the game
gets a flower from four red texels and a dark centre. Picture budget about six.

**The active-tab hazard — the one thing that has damaged a piece in this pack.**

`armorpieces_new` returns the new piece, and its check names it, **while the editor's active tab can
still be the previous one**. The Bee Wings session's first two `add_group` calls landed in
`fox_ears`, two pieces back, and a stray reached disk.

- **After `armorpieces_new`, call `get_project_info` and confirm the name before your first edit.**
- Every mcptoolkit reply's check line begins `[armorpieces] <piece>` — read that name, not just the
  numbers.
- If you do land an edit in the wrong piece:
  `armorpieces_open <the damaged piece> {discard: true, reload: true}`. **Never `undo`** — it acts on
  whatever tab is active. `modify_cube` is safe where `undo` is not.
- **Close your tab at the end** with `armorpieces_close`, as the Turtle Shell session did.

**The short form of four sessions' lessons.**

- One `armorpieces_set_part` call creates the static layer *and* the mask sheet: pass the fitting and
  `static: true` together, before painting.
- Master, static and mask take the **same `faces` dict** — same keys, same order. Write them as a
  set. An opaque mask pixel wins over the static layer; `pixels` with `value: null` punches a hole
  the fitting does not fill.
- **Do not shade a face taller than two rows with a `[top, bottom]` pair** — it interpolates, and the
  interpolated middle row belongs to no palette entry, which breaks the end-of-session count proof.
  Flat face fills plus explicit `pixels` is how the last three pieces were painted.
- **Resizing a cube after painting is safe**: the paint moves with it and the reply's sheet-layout
  block confirms the new rectangles. So shape first, paint, and trim afterwards without fear.
- **The 3D view only ever shows the master** — the piece renders grey all session. Prove the sheets
  with a Pillow read at the end: equal opaque counts on master and static, each master value's count
  matching its palette colour's count, zero static or mask pixels outside the master.
- The COPLANAR check flags the **plane**, not the overlap; moving outward clears it as well as
  moving in, and a trim of 0.05 costs no UV texel. `-` notes are not `!` problems.
- Groups cannot be renamed and a group's origin and rotation cannot be changed after `add_group` —
  compute the pivot and angles first, place cubes unrotated, rotate the bone. Never name a bone
  `root`. `add_group` parents by NAME.
- **Silhouette is what sells it.** The turtle read as a briefcase until its corners were chamfered.
  Take one render and ask what the outline says before you paint anything.
- `python tools/check_part.py` does not see this pack.
- Recipe centres already taken in this pack: `minecraft:sweet_berries`, `minecraft:lily_pad`,
  `minecraft:honeycomb`, `minecraft:turtle_helmet`.

**Recipe.** Centre item `minecraft:poppy` (unused by any template in the mod or this pack —
`minecraft:dandelion` and `minecraft:pink_petals` are already taken by mod pieces), paper ring,
craftable. Result is the `collar` template.

**Done means.** `armorpieces_save` accepted without `force`;
`python tools/check_authoring.py packs/animals/datapack packs/animals/resourcepack` clean; tab
closed; the Lessons section below filled in. No modpage build.

## Lessons from the session

Built in 34 edits, six bridge pictures budgeted and four spent. Saved without `force`; the check
ended with no `!` and no `-` notes at all.

**The active-tab hazard did not bite.** `armorpieces_new` was followed immediately by
`get_project_info` (name `flower_brooch`) before the first `add_group`, and every reply's check
line was read for the piece name, not just the numbers. Cost: one call. Keep doing it.

**Two-deep bones are how you get a compound rotation you can predict.** The bloom is a cup: five
petals each rotated round Z to its place on the clock *and* tipped forward out of the disc. One
bone with `rotation: [-12, 0, 72]` would have left the Euler order to guess. Instead: `bloom`
(the whole flower's 8 degree up-tilt) -> `pa..pe` (Z only, 0/72/144/216/288) -> `pa_t..pe_t`
(X only, -12). Nesting composes unambiguously as `Rx(8) . Rz(theta) . Rx(-12)`, so the landing
point is arithmetic. Predicted the first petal's envelope to `z -4.373`; the check said
`past chestplate z +1.37`. Every later cube landed on the predicted hundredth too. 15 bones for
9 cubes is not extravagant - it is what buys the shape without a single nudge.

**Do the occlusion arithmetic, not just the envelope arithmetic.** The check tells you where a
cube *is*; it never tells you that another of your own cubes is standing in front of it. Both
draft placements of the stem and leaf were geometrically perfect and completely invisible:

- Five petals 2 wide at radius 0.5..2.53 leave gaps only at theta = 36/108/180/252/324, each
  about +/-9 degrees wide at the tips. The stem was hung at 10 degrees off vertical *toward the
  sternum*, which is theta 190 - the exact edge of the down-right petal's 189.5..242.5 cover, so
  half the stem was behind a petal.
- The leaf's centre sat at radius 2.1 with the bloom's radius 2.72, so the whole blade was inside
  the flower.

The fix is one number: compute each appendage's polar angle and radius from the bloom centre, and
put it in a gap and outside the petal tips' radius. The leaf now runs from radius 2.79 to 3.24 at
about 7 o'clock - every texel of it clear of the bloom - and the stem's lower 1.3 units hang below
the petals. **A render of a grey piece cannot tell you this**: at one value per face, a hidden
leaf and a visible one look identical. Polar coordinates on paper were faster than pictures.

**Origins and rotations are frozen, cube coordinates are not.** Both rescues above were pure
`modify_cube` - the leaf was re-aimed by sliding the cube along its own bone's local axes
(local +x pointed world (0.5, -0.866) after the -60 chain, so shifting the cube in local x swung
the blade several degrees). No group was deleted, nothing was re-parented, no `undo` was needed.
When a bone's pivot is wrong, ask first whether a cube offset inside it gets you the same picture.

**Paint the master, the static layer and the mask from one dict.** The master call and the static
call were the same 45-key `faces` object; the master folded each poppy hex to its luminance and
those luminances came out as exactly the eight values in the brief's table (`#ed302c` -> 104,
`#204626` -> 55, and so on), so the end-of-session proof is a one-to-one count match:

    master opaque 156 = 114 flower + 42 hardware
    static opaque 114, mask opaque 4, 0 static or mask pixels outside the master
    #9b221a 30 = value 69 x 30, #204626 21 = 55 x 21, #ed302c 20 = 104 x 20,
    #bf2529 20 = 84 x 20, #742303 10 = 56 x 10, #265a25 8 = 68 x 8,
    #4a8f28 4 = 111 x 4, #2b702a 1 = 83 x 1

All eight poppy colours used, none invented. Faces two rows tall took `[top, bottom]` pairs; the
stem's 1x4 face was filled flat, per the no-interpolation rule.

**Sizing note the sheet enforces:** a cube's UV box is the *ceiling* of its size, so a 1x3.55x1
stem and a 1x4x1 stem share a rectangle - the last 0.05 trim (to clear the sash's belt envelope by
0.52 instead of 0.47, which turned a `-` note into silence) cost nothing and needed no repaint.
Shrinking a cube after painting moved the paint correctly and left no stray; growing one is what
the reply flags as `repaint`.

**Fitting.** The mask is the boss's north face alone, 4 texels. The brief's "outward faces" and
"the boss's rim ... hardware" only agree that way: the pollen disc is the gemstone, the four side
faces of the boss are the rim and stay on the master so they follow the trim material. The boss
stands 0.26 proud of the petals' inner faces, which is what makes those 4 texels read as a bead
rather than a sticker.

**Numbers the next collar piece can reuse.** Chestplate shell: front `z -3.0`, sides `x +/-5.0`,
top `y 25.0` (Blockbench). Leggings front `z -2.5`, sides `x +/-4.5`. This piece occupies
`x -4.74..0.74, y 17.02..23.33, z -5.04..-3.15` - it protrudes 2.05 in front of the shell, which
is in line with `brooch` (1.75) and `chain_of_office` (1.6), and is the price of any cupped bloom:
a 2.5-long petal tipped 20 degrees sweeps 1.3 forward on its own. The only neighbour that
constrains a collar piece downward is `sash:belt`, whose envelope tops out at `y 16.50`, so keep
everything at `y >= 17.0`.

**For the next Animals piece, on silhouette.** A small piece is read entirely by its outline, and
the outline is the *union of what is not hidden*. Budget one appendage that leaves the main mass
entirely - here the leaf, sticking a full unit past the petal tips - rather than three that all
graze it. And the sixth piece should be something that is not a disc: the pack now has ears, a
mask, wings, a shell and a bloom, all of which are round-ish; a long or jointed silhouette would
carry further.
