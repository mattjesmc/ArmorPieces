# Brief: Round Shield

A piece of **Armor Pieces: Norse** (`armorpieces_norse`) — riveted iron, wolf-grey fur, painted lime wood and a little gold - the north as the sagas tell it, hair and beard included.

From the `back` row of the Norse table:

> `round_shield` - a painted round shield slung flat on the back, iron boss at its centre - fitting `guard` - centre `oak_boat`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          round_shield
    anchor:        back
    namespace:     armorpieces_norse
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\norse\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\norse\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Round Shield",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:oak_boat", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Shield red is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `jarl` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:oak_boat` is confirmed free against every
template centre in the project.

So this piece has **three sheets**: the greyscale master `part`, the colour layer `part_static`,
and the greyscale mask `part_guard`.

## The three surfaces, and which cube gets which

A piece is drawn from three sheets and **they stack** — `recolour(master, static, palette)`, then
one `applyMask` per fitting:

    MATERIAL   `part`            greyscale master, recoloured through the TRIM material's ramp
    STATIC     `part_static`     real colour, painted OVER the recoloured master
    FITTING    `part_guard`     greyscale mask over both, filled by the PLAYER

**Static hides material** — a static cube stops answering the trim forever. **An empty fitting costs
nothing** — its mask is not read until a player fills it, so a masked cube still answers the trim
until then, and a static layer *under* a mask is the default look with the fitting as an override.

The **boss** carries no static. It is masked `guard` and is the piece's whole material surface; the painted board is static and never answers the trim.

## The rig, in Blockbench coordinates

    body box                x -4 .. 4       y 12 .. 24      z -2 .. 2
    chestplate shell (+1)   x -5 .. 5       y 11 .. 25      z -3 .. 3
    leggings shell (+0.5)   x -4.5 .. 4.5   y 11.5 .. 24.5  z -2.5 .. 2.5
    the `back` anchor       (0, 22, 2)

Front is **negative z**. This socket is not mirrored: build the whole piece once.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(0, 22, 2)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

A lime-wood round shield carried on the back: a big board painted in quarters - red left and right, cream top and bottom - built from a square with two side wings and a top and bottom tab so it reads as round, and a domed iron boss at the centre. It covers the whole back from the waist to the shoulders.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **board** — the main board:

        x -5.43 .. 5.43    y 12.57 .. 23.43    z 3.67 .. 4.29

- **wing_l** — the left side of the round:

        x -6.93 .. -5.43    y 15.07 .. 20.93    z 3.69 .. 4.23

- **wing_r** — the right side:

        x 5.43 .. 6.93    y 15.07 .. 20.93    z 3.69 .. 4.23

- **top** — the top of the round:

        x -3.43 .. 3.43    y 23.43 .. 24.93    z 3.69 .. 4.23

- **bottom** — the bottom of the round:

        x -3.43 .. 3.43    y 11.07 .. 12.57    z 3.69 .. 4.23

- **boss** — the domed iron boss at the centre:

        x -1.53 .. 1.62    y 16.47 .. 19.53    z 4.29 .. 5.38

**6 cubes in total is the budget**, and there is no 7th.

**Envelope budget.** Stay inside `x -7.0 .. 7.0, y 11.0 .. 25.0, z 3.6 .. 5.5`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the body bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -7.0 .. 7.0      y  -1.0 .. 13.0      z  3.6 .. 5.5

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `turtle_shell` | x -6.00..6.00, y 15.75..24.90, z 3.10..5.60 | the Animals' shell - a big flat thing on the back at your width |
| `cloak` | x -5.45..5.45, y 9.63..24.85, z 2.90..4.63 | the mod's cloak - your height band, and closer to the body than you |
| `girdle (belt)` | x -5.86..5.86, y 11.75..14.25, z -4.00..3.86 | worn WITH you, its back face at z 3.86 crosses your board's z 3.67 in a hull test - an OVERLAP `-`, not a `!` |
| `torc (collar)` | x -4.40..4.50, y 22.50..24.40, z -4.10..-3.00 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `seax_belt (belt)` | x -5.40..5.40, y 11.40..14.40, z -4.10..3.40 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

board and wings: base **120**, `south` **140** (the back face is the one you see). top and bottom: base **200**, `south` **220**. boss: base **140**, `south` **180**, `up` **170**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `board`, `wing_l`, `wing_r`: base `#9b2226`, `up` `#b8353a` — shield red - the painted board's own red
- `top`, `bottom`: base `#e6dccb`, `up` `#f3ece0` — shield cream - the unpainted quarters, whitewashed lime

**Mask `part_guard`** — flat **140**, on `boss`. 140 is the value every mask in this project
uses.

## Done when

- [ ] The check is clean, or every `!` left standing is one this brief allows.
- [ ] Envelope inside the budget above, **reported in the check's frame**.
- [ ] All three sheets painted — master, `part_static`, `part_guard`. `list_textures` is the list;
      an empty sheet is a defect, not a subtlety.
- [ ] Saved, and the tab closed.

**If a `!` COPLANAR appears against a piece on a DIFFERENT socket** — one you are worn *with*,
not one you replace — you do not have to stop. **Nudge your own face by 0.1 away from the shared
plane, repaint that face, and carry on**, staying inside the budget above. Say in your report which
face you moved and why. A shared plane z-fights in game, so moving is always right; it is only the
size of the move that needed permission, and this paragraph is that permission.

**Allowed to force:** nothing else. If any other `!` stands, stop and ask me.

## Lessons

<!-- Filled in after the session, from its report. -->

