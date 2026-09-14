# Brief: Cat Paws (REWORK)

This is a **rework of a shipped part**, not a new one. `armorpieces_animals:cat_paws` was built
from a brief on 2026-09-12 and the person who owns the pack looked at it today and said: *"terrible
- it should be cute, not lumpy and ugly."* The datapack half is right and must survive; the
geometry and the three sheets are to be rebuilt.

Open it with `armorpieces_open armorpieces_animals:cat_paws`. Do **not** create a new piece, do not
delete the part JSON, do not call `armorpieces_set_part` at all (the fitting, the static layer and
the recipe are already right, and the three sheets already exist), and do not touch any other tab.

## What is wrong with the shipped model

- **It is a box.** One 6.5 x 3 x 6.5 slab wrapped round the bottom of the sleeve, a second slab on
  top of it for the cuff, a paper-thin pad and two 0.66-unit claws. It reads as a bucket on the
  fist, not a paw - the "mitt" is *wider* than the sleeve it hangs from.
- **Nothing on it is paw-shaped.** No toes, no rounding, the pad is a 0.4-unit sliver that cannot
  be seen from any angle a player uses.
- **The claws are the wrong idea.** A cute cat paw is toe beans and fur, not claws.

## What must not change

- Part id `armorpieces_animals:cat_paws`, display name **"Cat Paws"**, socket **`vambraces`** only.
- Fitting **`armorpieces:guard`** (masked), **static layer yes**, recipe centre `minecraft:cod`,
  no effects, no loot row in the file. All of it is already in the part - leave it. Three sheets:
  master `part`, colour `part_static`, mask `part_guard`.
- `uid` stays. There is no `former_ids` and none is to be added.
- `vambraces` is a MIRRORED socket. Model ONE side - the **left arm, negative x** - and the game
  mirrors it.
- **No rotations.** Every bone stays at rotation 0. If you are computing a sine you have misread
  the brief. (A fan or a chain is where the check goes blind; this piece needs neither.)

## The rig, in Blockbench coordinates

    left arm box            x -8 .. -4      y 12 .. 24      z -2 .. 2
    sleeve shell (+1)       x -9 .. -3      y 11 .. 25      z -3 .. 3
    the vambraces anchor    (-6, 16, 0)

Front is **negative z**; outboard is **negative x**. The shell you must stay off is the
**chestplate's sleeve**: its planes are `x -9`, `x -3`, `z -3`, `z 3` and its **bottom `y 11`**.
Never put a face ON one of those planes. A cube may sit *below* `y 11` - that is the whole idea
here - and a cube may sit *inside* the sleeve (hidden), but a face in a shell plane z-fights.

The check prints YOUR envelope bone-local (+Y down, x mirrored): `check_x = -5 - bb_x`,
`check_y = 22 - bb_y`, `check_z = bb_z`. Other parts' envelopes come in both frames.

## What it should be

A **tabby cat's paw**: a compact, rounded mitt that hangs just below the sleeve like the cat's own
paw, three toe bumps along its front edge, pink toe beans underneath and on the toes, and a slim
copper cuff at the wrist holding it on. Soft and round. **Smaller than the sleeve, not bigger** -
the sleeve's own bottom face shows as a ring around the wrist, which is what makes the paw read as
a paw and not as a bucket.

Six cubes, all under one bone `base` (never `root`):

- **cuff** - the copper band at the wrist, the piece's only material surface and its `guard` mask:

        x -9.2 .. -2.8    y 13.6 .. 14.4    z -3.2 .. 3.2

  0.2 clear of every sleeve plane. Thin: it is a band, not a bracer.

- **paw** - the body of the mitt, hanging out of the sleeve bottom:

        x -8.5 .. -3.5    y 9.8 .. 11.4    z -2.5 .. 2.5

  Its top 0.4 sits *inside* the sleeve (hidden) so there is no gap at the join; its sides are 0.5
  in from the sleeve planes on every side, which is the ring of sleeve you want to see around it.

- **paw_under** - a slightly smaller slab beneath it, so the bottom reads rounded rather than cut:

        x -8.1 .. -3.9    y 9.4 .. 9.8    z -2.1 .. 2.1

- **toe_a / toe_b / toe_c** - three toe bumps along the front-bottom edge, protruding 0.6 forward
  of the paw's front face:

        toe_a   x -7.9 .. -7.1    y 9.6 .. 10.6    z -3.1 .. -2.5
        toe_b   x -6.4 .. -5.6    y 9.6 .. 10.6    z -3.1 .. -2.5
        toe_c   x -4.9 .. -4.1    y 9.6 .. 10.6    z -3.1 .. -2.5

  Their back faces at `z -2.5` sit against the paw's front face (hidden, not coplanar - they face
  each other). No two of the six cubes share a same-facing plane: check that the reply agrees.

**Envelope budget.** Stay inside `x -9.4 .. -2.6, y 9.2 .. 14.6, z -3.4 .. 3.4` (Blockbench), which
in the check's frame is `x -2.4 .. 4.4, y 7.4 .. 12.8, z -3.4 .. 3.4`. Reach from the anchor will be
about 7.3; the pair spans `2 * 9.2 = 18.4`, and the 18 ceiling is a `horns` rule that does not apply
on the arm (`cuffs` spans 20.14 here). Report it; do not shrink for it.

**Neighbours.** Everything else on `vambraces` is never worn with you and never compared. The
other socket on this bone is `pauldrons`, at the top of the arm (`y 20+`), nowhere near.

## Sheets

- **master `part`** (greyscale, the trim ramp): the **cuff only** - a band, lighter along its top
  edge, a darker seam line at its bottom. Every paw cube gets master paint too (mid-grey, so a
  hole in the static would still draw), but its look comes from the static.
- **`part_static`** (real colour) - this is the piece:
  - **tabby fur** on paw, paw_under and the three toes: an orange-ginger tabby from the game's own
    cat - base around `#d08a3c`, darker stripes `#9c5a22` as two or three bands running across the
    top (up) face and down the outboard (west) face, cream `#f1d9a6` on the front toes' tops. Shade
    the underside darker than the top.
  - **toe beans, pink** `#e8879c` with a darker rim `#c2607a`: one bean on the DOWN face of each toe,
    and on the paw_under's down face one big bean in the middle with three small ones toward the
    front (that face is 4.2 x 4.2 units, about 4 x 4 texels - a 2x2 big bean and three 1-texel
    small ones is right). The beans are the cute; do not skip them.
  - **nothing on the cuff** - it must keep answering the trim.
- **`part_guard`** (greyscale mask): the **cuff only**, shaded like the cuff's master (lighter top
  edge, darker bottom), so the player's metal fills the band. Nothing on any paw cube.

Only `armorpieces_paint` writes these sheets. Address faces as `<cube>.<face>`; `[top, bottom]`
pairs shade per row; a `pixels` list is applied AFTER the faces map, so a stray-clearing
`value: null` sweep must be its OWN call before the face paint (LESSONS #28).

**A rework leaves strays.** The old sheets were painted for five cubes of a different size; after the
geometry settles, null every texel outside the current face rectangles on ALL THREE sheets (the old
static and the old mask have strays too), then paint. Keep every `sheet layout` block the replies give
you - they are the record of where the old rectangles were. `inspect op:faces` gives the current ones.

**Budget.** One null sweep per sheet, then one or two `armorpieces_paint` calls per sheet; no more
than six pictures. Take the first picture where it can still change what you draw and none after the
last edit.

**Done means.** `armorpieces_save` accepted without `force`; from the repository root
`python tools/check_part.py <geometry.json> --name cat_paws --master <pack png> --static <pack png>
--mask guard=<pack png>` clean (the by-name form reads a stale copy elsewhere - use the pack's files), `python tools/check_authoring.py packs/animals/datapack packs/animals/resourcepack`
clean, `python tools/check_surfaces.py` with no `cat_paws` line; the lessons section below filled
in; `armorpieces_close` as your last call. No `modpage.yml` entry, no recipe change, no page
rebuild. Do not copy anything into `tools/decoration_masters/` - the pack's texture folder is the
only source for a pack piece.

## Lessons from the session

Built 2026-09-14, saved without `force`, every check clean.

- **The brief's six cubes went in exactly as written, in one `place_cube` call, and the reply
  already said everything the check would**: reach 7.36, `past chestplate x+0.20 y+1.60 z+0.20`,
  pair span 18.40, no coplanar line, every toe "touching" the paw and nothing else. Envelope
  `x -2.20..4.20 y 7.60..12.60 z -3.20..3.20` (check frame) - inside the budget by 0.2 on every
  axis. Three `-` notes accepted: the `wing_cases:pauldrons` hull OVERLAP/near (its case hangs to
  y 14.07 and the cuff's x -9.2 sits 0.02 inside its x envelope, a hull test only; no cube meets)
  and the 18.40 pair span the brief says to report and not shrink for.
- **A rework's null sweep is one `texture op:rects` per sheet over the whole 64x32 with `c: null`**
  - three calls, 2048 texels each - not a 400-entry `pixels` list. Nothing of the old layout
  survives, so there is nothing to subtract afterwards; the three `armorpieces_paint` calls then
  paint every current face. (The sweep hit LESSONS #14's `part.bbmodel` FileNotFoundError on the
  next four replies; one `element set {visibility:true}` on a cube brought the check back.)
- **Box UV orientation on the DOWN face: row 0 (top row on the sheet) is the SOUTH (+z) edge,
  the last row is north/front.** The first pass put the three small beans on row 0 and the
  screenshot from below showed them at the BACK of the paw, behind the big bean. Moved to the
  last row (y = face_y + 4) they sit just behind the toes. Anything front/back-asymmetric on a
  `down` face needs this; left/right-symmetric stripes on `up`/`west` never did.
- **The paw's `up` face (y 11.4) is inside the sleeve shell in game**, so the tabby stripes the
  brief puts "across the top face" are never seen; the ones that carry are the two dark columns
  on the outboard `west` face (5x2 - columns 1 and 3, both rows). If a future paw wants visible
  top stripes, run them down the `north` face instead.
- **1-texel-tall band faces cannot be graded.** The cuff's side faces are 7x1, so "lighter along
  its top edge, darker seam at its bottom" became `cuff.up 195 / cuff.* 150 / cuff.down 85` on
  both the master and the guard mask - the up and down faces are the only rows the band has.
- Pictures: four of six. The 3-view `fit` contact sheet was too small to read a paw-sized piece
  (LESSONS #15's warning holds at this scale); a `position`/`target` perspective aimed at the
  hand from below (`[-10,3,-10]` -> `[-6,10.5,0]`) is the one that showed the beans and caught
  the row-0 mistake. Take that kind first on a small piece.

