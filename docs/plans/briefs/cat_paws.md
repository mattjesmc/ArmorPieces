# Brief: Cat Paws

A piece of **Armor Pieces: Animals** (`armorpieces_animals`) — leather armor with copper hardware, and every piece reads as one NAMED animal drawn in that animal's own colours from the game.

From the `vambraces` row of the Animals table:

> `cat_paws` - a tabby's paws over the hands - fitting `guard` - centre `cod`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          cat_paws
    anchor:        vambraces
    namespace:     armorpieces_animals
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\animals\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\animals\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Cat Paws",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:cod", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Tabby brown is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `village` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:cod` is confirmed free against every
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

The **cuff** carries no static. It is masked `guard` and is the piece's whole material surface.

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

A tabby cat's paw worn over the fist: a rounded brown furred mitt at the bottom of the sleeve, a copper cuff holding it on, a cream pad underneath and two small cream claws at the front. Soft and blunt - it is a paw, not a gauntlet.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **cuff** — the copper cuff at the wrist:

        x -9.37 .. -2.63    y 14.47 .. 15.33    z -3.37 .. 3.37

- **mitt** — the furred paw over the hand:

        x -9.27 .. -2.73    y 11.53 .. 14.47    z -3.27 .. 3.27

- **pad** — the pad on the underside of the paw:

        x -6.87 .. -5.13    y 11.13 .. 11.53    z -1.87 .. -0.13

- **claw_a** — the outer claw, at the front-bottom edge:

        x -8.13 .. -7.47    y 11.13 .. 11.93    z -3.87 .. -3.27

- **claw_b** — the inner claw:

        x -4.53 .. -3.87    y 11.13 .. 11.93    z -3.87 .. -3.27

**5 cubes in total is the budget**, and there is no 6th.

**Envelope budget.** Stay inside `x -9.5 .. -2.5, y 11.0 .. 15.4, z -4.0 .. 3.5`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the arm bone's pivot at Blockbench `(-5, 22, 0)` - **not** the top of the arm box. For this socket:

    check_x = -5 - bb_x        check_y = 22 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.5 .. 4.5      y  6.6 .. 11.0      z  -4.0 .. 3.5

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `9.37`, so the pair spans **18.74**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the arms are already outboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `mittens` | x -8.50..-3.50, y 11.75..14.75, z -2.50..2.50 | the mod's own mitten - the shape yours is closest to; you sit outside the sleeve shell where it sits inside |
| `cuffs` | x -10.07..-1.93, y 12.60..16.97, z -4.07..4.07 | wider and deeper than you |
| `bee_wings (pauldrons)` | x -16.67..-8.90, y 22.03..24.71, z -1.50..3.12 | your own pack's wings, worn WITH you, far above you - never near |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

mitt: base **100**, `west` **115` (the outboard face), `down` **75**. pad and claws: base **190**, `down` **170**. cuff: base **150**, `up` **185**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `mitt`: base `#74563e`, `up` `#87654a` — tabby brown - the cat's own coat, and `down` #5e422d, the darker underside
- `pad`, `claw_a`, `claw_b`: base `#d1b7a1`, `up` `#e9d9c2` — tabby cream - the cat's own pale muzzle and chest

**Mask `part_guard`** — flat **140**, on `cuff`. 140 is the value every mask in this project
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
