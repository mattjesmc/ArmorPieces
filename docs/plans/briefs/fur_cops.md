# Brief: Fur Cops

A piece of **Armor Pieces: Norse** (`armorpieces_norse`) — riveted iron, wolf-grey fur, painted lime wood and a little gold - the north as the sagas tell it, hair and beard included.

From the `knees` row of the Norse table:

> `fur_cops` - an iron knee cop with a roll of grey fur over its top and a tuft above - fitting `guard` - centre `mutton`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          fur_cops
    anchor:        knees
    namespace:     armorpieces_norse
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\norse\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\norse\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Fur Cops",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:mutton", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Wolf-grey fur is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `jarl` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:mutton` is confirmed free against every
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

The **cop** carries no static. It is masked `guard` and is the piece's whole material surface; the fur is static.

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

A knee cop for the cold: a plain iron cop over the front of the knee, a thick roll of wolf-grey fur lying over its top edge and standing proud of it, and a ragged tuft of fur sticking up above the roll. Iron below, fur above.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **cop** — the iron cop over the front of the knee:

        x -3.53 .. -0.27    y 4.37 .. 6.53    z -3.71 .. -2.93

- **fur** — the roll of fur over the top of the cop:

        x -3.82 .. 0.03    y 6.53 .. 7.73    z -4.07 .. -2.93

- **tuft** — the tuft standing up above the roll:

        x -3.33 .. -0.46    y 7.73 .. 8.35    z -3.84 .. -2.93

**3 cubes in total is the budget**, and there is no 4th.

**Envelope budget.** Stay inside `x -3.9 .. 0.1, y 4.3 .. 8.4, z -4.2 .. -2.8`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.0 .. 2.0      y  3.6 .. 7.7      z  -4.2 .. -2.8

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `3.82`, so the pair spans **7.64**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `poleyns` | x -4.55..-1.55, y 4.90..8.30, z -4.65..-2.65 | the mod's poleyn - your height band, and deeper |
| `padding` | x -4.70..0.85, y 4.40..7.60, z -3.45..-0.50 | the wayfarer's padded knee - soft where you are half fur |
| `hip_axes (tassets)` | x -5.30..-4.00, y 4.70..12.10, z -0.60..2.70 | your own pack's axe, built in this batch, hanging BEHIND your plane (z > -0.53) - the two never meet |
| `winingas (greaves)` | x -5.10..0.50, y 0.30..4.20, z -3.80..-2.20 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `snowshoes (spurs)` | x -5.20..1.30, y 0.00..1.40, z 2.90..8.00 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

cop: base **140**, `up` **175**, `down` **100**. fur and tuft: base **130**, `north` **150**, `down` **95**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `fur`, `tuft`: base `#7d7873`, `up` `#9a938c` — wolf-grey fur - the pelt's own grey, and `down` #5c5751, its shadow

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

