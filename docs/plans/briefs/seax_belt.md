# Brief: Seax Belt

A piece of **Armor Pieces: Norse** (`armorpieces_norse`) — riveted iron, wolf-grey fur, painted lime wood and a little gold - the north as the sagas tell it, hair and beard included.

From the `belt` row of the Norse table:

> `seax_belt` - a leather belt with a sheathed seax hung horizontally across the front - fitting `guard` - centre `stone_sword`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          seax_belt
    anchor:        belt
    namespace:     armorpieces_norse
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\norse\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\norse\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Seax Belt",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:stone_sword", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Oiled leather is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `jarl` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:stone_sword` is confirmed free against every
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

The **buckle** carries no static. It is masked `guard` and is the piece's whole material surface.

## The rig, in Blockbench coordinates

    body box                x -4 .. 4       y 12 .. 24      z -2 .. 2
    chestplate shell (+1)   x -5 .. 5       y 11 .. 25      z -3 .. 3
    leggings shell (+0.5)   x -4.5 .. 4.5   y 11.5 .. 24.5  z -2.5 .. 2.5
    the `belt` anchor       (0, 14, 0)

Front is **negative z**. This socket is not mirrored: build the whole piece once.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(0, 14, 0)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

A belt with a seax: a plain leather belt round the waist with an iron buckle at the front, and a sheathed seax hanging horizontally below it across the front of the body, hilt to the right, held by two short straps from the belt. The antler hilt is pale; the sheath is dark leather.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **belt** — the leather belt round the waist:

        x -5.33 .. 5.33    y 12.87 .. 14.13    z -3.33 .. 3.33

- **buckle** — the iron buckle at the front:

        x -0.87 .. 0.87    y 12.67 .. 14.33    z -3.73 .. -3.33

- **sheath** — the seax's sheath, horizontal across the front below the belt:

        x -4.55 .. 2.07    y 11.47 .. 12.43    z -4.03 .. -3.33

- **hilt** — the antler hilt, out of the right end of the sheath:

        x 2.07 .. 3.87    y 11.57 .. 12.33    z -3.88 .. -3.43

- **strap_a** — the left strap hanging the sheath from the belt:

        x -3.47 .. -2.83    y 12.43 .. 12.87    z -3.83 .. -3.33

- **strap_b** — the right strap:

        x 1.03 .. 1.67    y 12.43 .. 12.87    z -3.83 .. -3.33

**6 cubes in total is the budget**, and there is no 7th.

**Envelope budget.** Stay inside `x -5.4 .. 5.4, y 11.4 .. 14.4, z -4.1 .. 3.4`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the body bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -5.4 .. 5.4      y  9.6 .. 12.6      z  -4.1 .. 3.4

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `pillager_belt` | x -5.35..5.35, y 12.05..15.35, z -4.35..3.85 | a pack belt at your width with something hung on it |
| `buckled_belt` | x -5.50..5.50, y 12.50..15.50, z -4.50..3.50 | the mod's buckled belt - the precedent for the buckle standing proud |
| `round_shield (back)` | x -7.00..7.00, y 11.00..25.00, z 3.60..5.50 | your own pack's shield, built in this batch, starting at z 3.67 - your belt ends at 3.33, clear |
| `torc (collar)` | x -4.40..4.50, y 22.50..24.40, z -4.10..-3.00 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

belt and straps: base **90**, `up` **110**. sheath: base **60**, `north` **75**. hilt: base **200**. buckle: base **140**, `north` **175**.

**The belt is one cube right round the body.** Its inner volume is inside the chestplate; its six faces are the belt.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `belt`, `strap_a`, `strap_b`: base `#5a3d28`, `up` `#75523a` — oiled leather - the straps and the belt
- `sheath`: base `#3b2a1c`, `up` `#4f3a28` — dark leather - the sheath
- `hilt`: base `#e6dfcf`, `up` `#f2ede2` — bone - the antler hilt and the bead

**Mask `part_guard`** — flat **140**, on `buckle`. 140 is the value every mask in this project
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

