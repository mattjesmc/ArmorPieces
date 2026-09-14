# Brief: Oath Rings

A piece of **Armor Pieces: Norse** (`armorpieces_norse`) — riveted iron, wolf-grey fur, painted lime wood and a little gold - the north as the sagas tell it, hair and beard included.

From the `vambraces` row of the Norse table:

> `oath_rings` - three heavy arm rings up each forearm, the middle one a double spiral - fitting `guard` - centre `raw_copper`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          oath_rings
    anchor:        vambraces
    namespace:     armorpieces_norse
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\norse\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\norse\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Oath Rings",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:raw_copper", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Oiled leather is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `jarl` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:raw_copper` is confirmed free against every
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

The three **rings** carry no static. They are masked `guard` and are the piece's whole material surface; the wrap is static leather.

## The rig, in Blockbench coordinates

    left arm box            x -8 .. -4      y 12 .. 24      z -2 .. 2
    sleeve shell (+1)       x -9 .. -3      y 11 .. 25      z -3 .. 3
    the `vambraces` anchor       (-6, 16, 0)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-6, 16, 0)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

A warrior's arm rings: a leather wrap at the wrist, and three thick metal rings round the forearm above it with gaps between them - the middle one thicker, a spiral of two turns. The rings are the piece; the mod's `bangles` are thin and many, these are heavy and few.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **wrap** — the leather wrap at the wrist:

        x -9.13 .. -2.87    y 11.67 .. 12.53    z -3.13 .. 3.13

- **ring_lo** — the lowest ring:

        x -9.37 .. -2.63    y 12.57 .. 13.37    z -3.37 .. 3.37

- **ring_mid** — the middle ring, a double spiral, thicker:

        x -9.47 .. -2.53    y 14.17 .. 15.13    z -3.47 .. 3.47

- **ring_up** — the top ring:

        x -9.37 .. -2.63    y 15.97 .. 16.73    z -3.37 .. 3.37

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -9.6 .. -2.4, y 11.6 .. 16.8, z -3.6 .. 3.6`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the arm bone's pivot at Blockbench `(-5, 22, 0)` - **not** the top of the arm box. For this socket:

    check_x = -5 - bb_x        check_y = 22 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.6 .. 4.6      y  5.2 .. 10.4      z  -3.6 .. 3.6

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `9.47`, so the pair spans **18.94**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the arms are already outboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `bangles` | x -9.85..-2.55, y 11.40..13.50, z -3.45..3.45 | the mod's bangles - thin rings low on the wrist; yours are heavy and climb the forearm |
| `cuffs` | x -10.07..-1.93, y 12.60..16.97, z -4.07..4.07 | wider and deeper than you |
| `wing_cases (pauldrons)` | x -11.02..-7.05, y 14.07..25.85, z -2.75..2.75 | worn WITH you, reaching down to y 14.07 on the outboard side - an OVERLAP `-`, not a `!` |
| `ravens (pauldrons)` | x -9.10..-4.80, y 25.00..28.80, z -4.00..3.40 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

rings: base **150**, `up` **190**, `down` **110**; the middle ring `west` **175** with two `pixels` rows of 150 / 185 if the tool lets you, so it reads as two turns. wrap: base **90**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `wrap`: base `#5a3d28`, `up` `#75523a` — oiled leather - the straps and the belt

**Mask `part_guard`** — flat **140**, on `ring_lo`, `ring_mid`, `ring_up`. 140 is the value every mask in this project
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

