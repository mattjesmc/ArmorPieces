# Brief: Mempo

A piece of **Armor Pieces: Samurai** (`armorpieces_samurai`) — black lacquer over iron, red odoshi lacing and gilt fittings - the armor of a daimyo, every piece a named part of a real suit.

From the `brow` row of the Samurai table:

> `mempo` - a red lacquered half-mask below the eyes, moustache and throat plate - fitting `inlay` - centre `red_dye`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          mempo
    anchor:        brow
    namespace:     armorpieces_samurai
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\samurai\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\samurai\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Mempo",
                           fittings: ["armorpieces:inlay"],
                           static: true,
                           recipe: { centre: "minecraft:red_dye", craftable: true } }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Mask red is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `daimyo` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:red_dye` is confirmed free against every
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

The **yodare** (throat plate) carries no static. It is masked `inlay` - it is laced cord over iron - so it answers the trim until a player dyes it.

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

A samurai's face mask: a red lacquered plate covering the face from just under the eyes to the chin, a nose standing out of it, a bristling grey moustache across the lip, and a laced throat plate (the yodare-kake) hanging below the chin. The eyes are open above it. It is meant to look fierce.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **face** — the lacquered plate over the lower face:

        x -3.93 .. 3.93    y 24.37 .. 27.63    z -5.67 .. -5.07

- **nose** — the nose standing out of the plate:

        x -0.77 .. 0.77    y 26.53 .. 27.87    z -6.43 .. -5.67

- **moustache** — the bristling moustache across the lip:

        x -2.83 .. 2.83    y 25.93 .. 26.53    z -6.23 .. -5.67

- **yodare** — the laced throat plate hanging below the chin:

        x -3.37 .. 3.37    y 22.63 .. 24.37    z -5.53 .. -5.03

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -4.0 .. 4.0, y 22.5 .. 28.0, z -6.5 .. -4.9`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the head bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -4.0 .. 4.0      y  -4.0 .. 1.5      z  -6.5 .. -4.9

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `wither_mask` | x -4.10..4.10, y 25.10..31.30, z -6.45..-5.15 | a pack faceplate at your width; you sit lower and leave the eyes open |
| `bone_mask` | x -4.10..4.10, y 26.50..31.25, z -6.10..-5.10 | the Wild Hunt's mask - the same depth band |
| `barbute` | x -4.00..4.00, y 22.50..29.50, z -5.10..-4.85 | the precedent for reaching below the helmet's y 23 on this socket - your throat plate does the same |
| `maedate (crest)` | x -3.60..3.60, y 33.00..38.60, z -4.10..-1.90 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `kuwagata (horns)` | x -5.70..-5.00, y 29.30..38.20, z -3.70..-1.80 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

face and nose: base **110**, `north` **135**, `down` **80**. moustache: base **70**. yodare: base **140**, `north` **165**, `down` **110**.

**Cut nothing.** The eyes are the open space ABOVE the face plate; every face above gets paint.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `face`, `nose`: base `#8c1d1d`, `up` `#b02a2a` — mask red - the red lacquer of a real mempo
- `moustache`: base `#3a3431`, `up` `#55504c` — horsehair grey - the moustache

**Mask `part_inlay`** — flat **140**, on `yodare`. 140 is the value every mask in this project
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

