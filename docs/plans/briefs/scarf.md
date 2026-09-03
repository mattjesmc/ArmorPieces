# Brief: Scarf

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the eighth
batch of four (read pendant.md and fang_necklace.md first - same socket, the Z-rotation sign,
the depth budget on the chest). From the `collar` row of `docs/plans/part-variety.md`:

> **Scarf** - A wrapped neck cloth with two tails down the chest. Theme: Wayfarer. Fitting:
> `inlay`.

**Part.** `armorpieces:scarf`, socket `collar` only, in the mod's own pack. Display name "Scarf".
Fittings: `armorpieces:inlay`, one mask, covering the whole scarf. No effects, no loot, no
static layer.

**Shape.** `collar` is not a mirrored socket: model the whole thing on the body bone. The torso
box is x -4..4, y 12..24, z -2..2 (pivot 0, 24, 0); the chestplate shell is that box inflated a
full unit, x -5..5, y 11..25, z -3..3, and the anchor is at Blockbench (0, 23, -2). Read the
envelopes in the `armorpieces_new` reply: the same-socket parts are never compared (gorget
reaches y 25.25, so a wrap at the collar line is the socket's norm); the back and belt parts
share the bone but are far from the upper chest. Build: a `wrap` bone with a ring of four
plates half a unit thick and 1.4 tall at y 23.9..25.3, hugging the chestplate's top edge a
tenth off the shell (front z -3.6..-3.1, back z 3.1..3.6, flanks x ±5.1..±5.6, each the full
span so the corners double up) - the wrapped cloth round the neck; a second, smaller front plate
on top of the first, x -3..3, y 24.6..25.6, z -3.85..-3.6, the fold where the scarf crosses;
and two `tail_l` / `tail_r` bones hanging from the wrap's front, each a plate 2.0 wide (x),
0.4 thick, pivoted at the wrap's bottom edge (x -1.7, y 23.9, z -3.35) and (x 1.5, y 23.9,
z -3.35), the left tail falling to y 18.6 and the right to y 20.2 (unequal, as a tied scarf
hangs), both at z -3.5..-3.1 in the unrotated pose (a tenth inside the wrap's slab at the top so
no plane is shared), the bones rotated about Z by -5 (left) and +5 (right) so the tails splay a
little (for a cube BELOW its pivot a positive Z rotation swings the free end toward +x - pendant
measured it; confirm on the first reply). Nothing above y 25.6 and nothing below y 18.5.

**Sheets.** Master: wrap mid `[top, bottom]` with a lighter top face and a darker single row
along its bottom edge (`pixels`) as the fold shadow; the fold plate a step lighter; tails
`[top, bottom]` darker toward the hem with a bright bottom row as the fringe (`pixels`). Inlay
mask: every face at the same values, fringe row included.

**Recipe.** Centre item `minecraft:orange_wool` (a block with a flat texture, unused by any
template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py scarf`
and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons paragraph below
filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session


Built 2026-09-03 in 23 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`armorpieces_part`, 1 `list_outline`, 3 `add_group`, 3 `place_cube`, 8 `modify_cube`, 2
`remove_element` (starter cube, then its `main` bone), 2 `armorpieces_check`, 1
`armorpieces_set_part`, **4 `armorpieces_paint`** (master and inlay mask, painted twice - see
below), 4 `set_camera_angle`, 1 `armorpieces_save`. No `risky_eval`, nothing hand-edited, and the
save went through first time **without `force`**.

**What I built.** Seven cubes in three bones. `wrap` (pivot 0, 23.9, -3.35) carries the ring -
`wrap_front` x -5.5..5.5, y 22.9..24.3, z -3.6..-3.1; `wrap_back` same box at z 3.05..3.55;
`wrap_left` x -5.6..-5.1 and `wrap_right` x 5.1..5.6, both y 22.95..24.25, z -3.45..3.45 - plus
the knot `fold` x -3..3, y 22.4..23.4, z -3.85..-3.45. `tail_l` (pivot -1.7, 23.9, -3.35,
rotation 0,0,**-5**) holds `tail_left` x -2.7..-0.7, y 18.6..23.15, z -3.5..-3.1; `tail_r`
(pivot 1.5, 23.9, -3.35, **+5**) holds `tail_right` x 0.5..2.5, y 20.2..23.15, same depth.
Envelope (Blockbench) x ±5.60, y 18.53..24.30, z -3.85..3.55; reach 7.92, `past chestplate
x+0.60 y-0.70 z+0.85`. The brief's Z signs were right for once and the arithmetic agreed before
the bridge did: with pivot above the cube, θ=-5 sends the left tail's free end to x -3.07 (outward)
and θ=+5 the right one's to x +2.73, low corners at y 18.53 and 20.12.

**The one real deviation: the collar line is inside the player's head, so the ring came down a
unit.** The brief's y 23.9..25.3 wrap and its y 24.6..25.6 fold sit in the vanilla head cube
(x ±4, y 24..32, z ±4) and behind its front face at z = -4; a screenshot at the throat showed
exactly that - the fold invisible, the wrap's front only readable outboard of x ±4, where it
peeked past the head. Depth cannot rescue it (you would have to pass z -5 to clear a helmet's hat
layer, which is why `chain_of_office` and `brooch` only go to -4.6/-4.75 *below* y 23.5), so I
moved the whole ring down 1.0 to y 22.9..24.3 - the top 0.3 tucks under the chin, which is what a
scarf does - and put the knot below the band instead of above it (y 22.4..23.4, overlapping the
band's lower half by 0.5 and hanging 0.5 proud), so the tails emerge from under it. Tail tops
moved with it, to y 23.15, and their bottoms kept the briefed y 18.6 / 20.2. Everything else is
the brief's numbers. **The check will never tell you this**: it measures the body bone's own
shells and the other body-bone parts, not the head, so a `collar` part is on its own above y 24.
Rule of thumb for the socket: nothing between x ±4 and z > -4 above y 24 will ever be seen.

**Two other numbers I changed, both to stop z-fighting.** The brief's back plate at z 3.1 drew
the only `!` of the session - *"COPLANAR: wrap and carapace:back's lame_1 share the plane
z = 3.1"* - so it went to z 3.05..3.55, 0.05 clear of the chestplate shell at z 3 and 0.05 in
front of the carapace's face; the `!` disappeared on the next reply. And the "corners double up"
ring cannot be built from four boxes of the same y-span and the same outer planes: any two boxes
that overlap in a corner while sharing two axes' face planes give coincident *exterior* faces
(same direction, same depth). I kept the doubling but broke every shared plane - the flanks are
0.05 shorter in y (22.95..24.25) and stop at z ±3.45 inside the front/back slabs, and the
front/back plates stop at x ±5.5 inside the flanks - so each corner's overlapping faces are
strictly buried. The cost is a 0.1 x 0.15 notch at the four outer corners, a tenth of a texel,
invisible. Same trick on the fold (back plane z -3.45, inside both the wrap and tail slabs) and
the tails (tops 0.25 up inside the wrap, not the briefed tenth: a 2-wide plate rotated 5° lifts
its inner top corner by 0.087, so a tenth leaves a 0.012 bite of overlap - do the corner
trigonometry, not the edge).

**`!` lines accepted: none.** The final check is `ok: nothing needs a decision` with 15 notes,
all of them the wrap passing through `back`-socket parts at the shoulders: hull OVERLAPs into
`carapace`'s top lame (8.5 x 1.4 x 0.45), `bedroll`'s roll and straps, `spine_ridge`'s plate_1
and `pinions`' bracket, plus two "share the plane y = -0.3, inside the shell, so occluded" notes
against the bedroll straps. They are unavoidable and accepted by design: a ring round the neck has
to close behind it, and everything on `back` starts at z ≥ 2.95, i.e. right where the back plate
must be. The notes are hull tests inside the chestplate shell's shadow, not visible surfaces.

**Four paint calls, two per sheet, and they covered every face.** The first pair (master, then
`part_inlay`) painted 42 faces + 48 pixels each; then the geometry moved and the tails lost a
texel row of height (5.55 → 4.55 and 3.95 → 2.95 units), so the fringe `pixels` had to be
re-placed on the new bottom rows and the abandoned row nulled - hence the second pair. **Resizing
a cube after painting keeps the face paint but leaves any `pixels` you placed by sheet coordinate
in the wrong place; repaint the whole sheet rather than patching.** Values: `*.*` 130, wrap
`[150,110]` on the outward face, 185 up, 80 down, `[140,100]` on the ends, 85 on the buried face;
`fold` a step lighter (`[190,145]` north, 205 up, 95 down); tails `[150,95]` north, `[132,85]`
sides, 190 on the hem face. The `pixels` are the 36-texel fold shadow along the wrap's bottom row
on all four plates (78) and the 12-texel fringe on the tails' bottom rows (195-210). The inlay
mask repeats the master exactly - every face, fringe included, as briefed - so the whole scarf
takes the dye. Saved sheets: 314 opaque texels each, 26 greys, span 78..210, pure greyscale, a
64x32 sheet about half full.

**For the next part.** `minecraft:orange_wool` is now taken as a template centre; it had never
been cached, so the three-step dance again - `--offline` warned *"no texture for 1 item(s)"*, a
plain `python -m modpage build` fetched it, the third build reported `unchanged`. Group origins
cannot be edited by any bridge tool (`add_group` only creates, `rename_element` refuses groups),
so when you move a bone's cubes after the fact the pivot stays where it was: mine sit 0.75 above
the cloth, harmless because nothing animates, but place the bone right the first time if you care
about the geometry file reading cleanly. For the next `collar` part the depth band is now
`chain_of_office` -4.60..-2.60, `bandolier` -3.65..-2.35, `pendant` -3.85..-3.10, `fang_necklace`
-3.90..-3.05, `brooch` to -4.75, `gorget` +0.75, and this scarf -3.85..3.55 - the first collar
part that wraps all the way round, and the width record on the socket after gorget (x ±5.6).
