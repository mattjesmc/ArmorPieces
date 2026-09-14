# Brief: Coral Visor

A piece of **Armor Pieces: Coral** (`armorpieces_coral`) — turtle-scute armor with copper hardware, the reef worn ashore - coral, kelp and the creatures of the shallows, every one in its own colour.

From the `brow` row of the Ocean table:

> `coral_visor` - a lattice of tube coral across the eyes - fitting `guard` - centre `tube_coral_block`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          coral_visor
    anchor:        brow
    namespace:     armorpieces_coral
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\coral\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\coral\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Coral Visor",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:tube_coral_block", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Tube coral blue is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `ocean` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:tube_coral_block` is confirmed free against every
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

The two **frame** bars carry no static. They are masked `guard`, so they answer the trim while the fitting is empty and take the metal when a player fills it.

## The rig, in Blockbench coordinates

    head box                x -4 .. 4       y 24 .. 32      z -4 .. 4
    helmet shell (+1)       x -5 .. 5       y 23 .. 33      z -5 .. 5
    the `brow` anchor       (0, 28, -4)

Front is **negative z**. This socket is not mirrored: build the whole piece once.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(0, 28, -4)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

A visor made of tube coral: two copper bars above and below the eyes, and three blue coral tubes standing between them like the bars of a grille. You look out between the tubes. It is a reef thing, not a knight's visor - the bars are the only metal in it.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **frame_top** — the upper copper bar, across the brow:

        x -4.13 .. 4.13    y 29.33 .. 30.07    z -5.63 .. -5.13

- **frame_low** — the lower copper bar, across the cheekbones:

        x -4.13 .. 4.13    y 25.93 .. 26.67    z -5.63 .. -5.13

- **tube_a** — the left coral tube, standing between the bars:

        x -3.27 .. -2.33    y 26.67 .. 29.33    z -5.83 .. -5.07

- **tube_b** — the middle tube, over the nose:

        x -0.47 .. 0.47    y 26.67 .. 29.33    z -5.83 .. -5.07

- **tube_c** — the right tube:

        x 2.33 .. 3.27    y 26.67 .. 29.33    z -5.83 .. -5.07

**5 cubes in total is the budget**, and there is no 6th.

**Envelope budget.** Stay inside `x -4.2 .. 4.2, y 25.8 .. 30.2, z -5.9 .. -5.0`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the head bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -4.2 .. 4.2      y  -6.2 .. -1.8      z  -5.9 .. -5.0

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `wither_mask` | x -4.10..4.10, y 25.10..31.30, z -6.45..-5.15 | a pack faceplate at your width; you are shallower |
| `spectacle_visor` | x -4.00..4.00, y 24.00..31.00, z -5.60..-5.10 | the mod's own visor on this socket - the depth you match |
| `coral_crown (crest)` | x -1.25..2.03, y 33.50..39.01, z -3.50..3.50 | your pack's crown, worn with you; it is above the helmet and never near you |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

tubes: base **90**, `north` **110** (the front catches light), `up` **120**. frame bars: base **160**, `up` **195`, `down` **115**.

**Cut nothing.** The gaps between the tubes are the eye slots; every face above gets paint.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `tube_a`, `tube_b`, `tube_c`: base `#314fdd`, `up` `#3f6ce5` — tube coral blue - the game's own block colour, deep and saturated

**Mask `part_guard`** — flat **140**, on `frame_top`, `frame_low`. 140 is the value every mask in this project
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
