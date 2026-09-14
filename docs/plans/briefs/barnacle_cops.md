# Brief: Barnacle Cops

A piece of **Armor Pieces: Coral** (`armorpieces_coral`) — turtle-scute armor with copper hardware, the reef worn ashore - coral, kelp and the creatures of the shallows, every one in its own colour.

From the `knees` row of the Ocean table:

> `barnacle_cops` - copper knee cops crusted with barnacles - fitting `guard` - centre `prismarine_shard`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          barnacle_cops
    anchor:        knees
    namespace:     armorpieces_coral
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\coral\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\coral\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Barnacle Cops",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:prismarine_shard", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Barnacle shell is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `ocean` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:prismarine_shard` is confirmed free against every
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

The **cop** carries no static. It is masked `guard` and answers the trim until a player fills the fitting.

## The rig, in Blockbench coordinates

    left leg box            x -3.9 .. 0.1   y 0 .. 12       z -2 .. 2
    leggings shell (+0.4)   x -4.3 .. 0.5   y -0.4 .. 12.4  z -2.4 .. 2.4
    boots shell (+0.9)      x -4.8 .. 1.0   y -0.9 .. 12.9  z -2.9 .. 2.9
    the `knees` anchor       (-1.9, 6, -2)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-1.9, 6, -2)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

A plain copper knee cop that has been in the sea too long: three pale barnacles have grown on its front, each a small blunt cone with a dark opening. The cop is tidy hardware; the barnacles are what happened to it.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **cop** — the knee cop, over the front of the knee:

        x -3.57 .. -0.23    y 4.23 .. 7.26    z -3.77 .. -2.93

- **barnacle_a** — the upper-outer barnacle:

        x -3.07 .. -2.33    y 6.13 .. 6.87    z -4.27 .. -3.77

- **barnacle_b** — the middle-inner barnacle, the biggest:

        x -1.67 .. -0.93    y 5.33 .. 6.07    z -4.37 .. -3.77

- **barnacle_c** — the low barnacle:

        x -2.67 .. -1.93    y 4.57 .. 5.13    z -4.17 .. -3.77

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -3.7 .. -0.1, y 4.1 .. 7.4, z -4.5 .. -2.8`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -1.8 .. 1.8      y  4.6 .. 7.9      z  -4.5 .. -2.8

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `3.57`, so the pair spans **7.14**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `magma_cops` | x -3.55..-0.25, y 3.72..7.65, z -4.05..-2.58 | a pack knee cop at your width; your barnacles reach 0.3 further forward |
| `poleyns` | x -4.55..-1.55, y 4.90..8.30, z -4.65..-2.65 | the deepest knee piece; you stay inside it |
| `scale_shins (greaves)` | x -4.40..0.00, y -0.73..4.62, z -3.82..-0.41 | your pack's shin piece, worn WITH you, rising to y 4.62 - your cop starts at 4.23, so expect an OVERLAP note, a `-` and not a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

cop: base **145**, `up` **180**, `down` **100**. barnacles: base **200**, `north` **120** (the opening), `up` **225**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `barnacle_a`, `barnacle_b`, `barnacle_c`: base `#e6dfd0`, `up` `#f2ede2` — barnacle shell - chalky off-white, and `north` #8a8377, the dark opening at the tip

**Mask `part_guard`** — flat **140**, on `cop`. 140 is the value every mask in this project
uses.

## Done when

- [ ] The check is clean, or every `!` left standing is one this brief allows.
- [ ] Envelope inside the budget above, **reported in the check's frame**.
- [ ] Pair span reported.
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
