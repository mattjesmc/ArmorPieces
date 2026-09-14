# Brief: Sea Pickle Belt

A piece of **Armor Pieces: Coral** (`armorpieces_coral`) — turtle-scute armor with copper hardware, the reef worn ashore - coral, kelp and the creatures of the shallows, every one in its own colour.

From the `belt` row of the Ocean table:

> `sea_pickle_belt` - sea pickles hanging round a kelp cord - fitting `inlay` - centre `sea_pickle`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          sea_pickle_belt
    anchor:        belt
    namespace:     armorpieces_coral
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\coral\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\coral\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Sea Pickle Belt",
                           fittings: ["armorpieces:inlay"],
                           static: true,
                           recipe: { centre: "minecraft:sea_pickle", craftable: true } }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Sea pickle olive is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `ocean` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:sea_pickle` is confirmed free against every
template centre in the project.

So this piece has **three sheets**: the greyscale master `part`, the colour layer `part_static`,
and the greyscale mask `part_inlay`.

## The three surfaces, and which cube gets which

A piece is drawn from three sheets and **they stack** — `recolour(master, static, palette)`, then
one `applyMask` per fitting:

    MATERIAL   `part`            greyscale master, recoloured through the TRIM material's ramp
    STATIC     `part_static`     real colour, painted OVER the recoloured master
    FITTING    `part_inlay`     greyscale mask over both, filled by the PLAYER

**Static hides material** — a static cube stops answering the trim forever. **An empty fitting costs
nothing** — its mask is not read until a player fills it, so a masked cube still answers the trim
until then, and a static layer *under* a mask is the default look with the fitting as an override.

The **cord** carries no static. It is masked `inlay` (it is cord - dyed matter), so it answers the trim until a player dyes it.

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

A cord round the waist with five sea pickles hanging from it - squat olive-green nubs, each with a pale glowing tip on its underside. They hang at uneven heights round the whole waist, front, sides and back, so the belt reads from every angle.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **cord** — the cord itself, right round the waist:

        x -5.33 .. 5.33    y 12.67 .. 13.53    z -3.33 .. 3.33

- **pickle_a** — front-left pickle:

        x -3.87 .. -2.93    y 11.73 .. 13.87    z -4.13 .. -3.33

- **pickle_b** — front-right pickle, hanging a little lower:

        x 1.53 .. 2.47    y 11.53 .. 13.87    z -4.13 .. -3.33

- **pickle_c** — left-side pickle:

        x -6.13 .. -5.33    y 11.63 .. 13.87    z -0.87 .. 0.07

- **pickle_d** — right-side pickle:

        x 5.33 .. 6.13    y 11.83 .. 13.87    z -1.47 .. -0.53

- **pickle_e** — the one at the back:

        x -0.93 .. 0.13    y 11.63 .. 13.87    z 3.33 .. 4.13

**6 cubes in total is the budget**, and there is no 7th.

**Envelope budget.** Stay inside `x -6.2 .. 6.2, y 11.4 .. 14.0, z -4.2 .. 4.2`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the body bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -6.2 .. 6.2      y  10.0 .. 12.6      z  -4.2 .. 4.2

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `cord` | x -5.60..5.60, y 8.83..13.30, z -4.55..3.60 | the mod's own cord belt - yours sits higher and hangs less |
| `girdle` | x -5.86..5.86, y 11.75..14.25, z -4.00..3.86 | your height band, almost exactly |
| `pouch_belt` | x -7.10..6.55, y 11.05..13.60, z -3.40..5.00 | the precedent for things hanging off the belt line |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

pickles: base **80**, `up` **95**, `down` **220** (the tip is the bright thing). cord: base **140**, `up` **170**.

**The cord is one cube right round the body.** Its inner volume is inside the chestplate and never seen; its six faces are the belt. That is how `girdle` and `buckled_belt` are built too.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `pickle_a`, `pickle_b`, `pickle_c`, `pickle_d`, `pickle_e`: base `#575c1d`, `up` `#6c722a` — sea pickle olive - the item's own green, and `down` #c5f4c2, the pale glowing tip

**Mask `part_inlay`** — flat **140**, on `cord`. 140 is the value every mask in this project
uses.

## Done when

- [ ] The check is clean, or every `!` left standing is one this brief allows.
- [ ] Envelope inside the budget above, **reported in the check's frame**.
- [ ] All three sheets painted — master, `part_static`, `part_inlay`. `list_textures` is the list;
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
