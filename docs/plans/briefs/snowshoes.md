# Brief: Snowshoes

A piece of **Armor Pieces: Norse** (`armorpieces_norse`) — riveted iron, wolf-grey fur, painted lime wood and a little gold - the north as the sagas tell it, hair and beard included.

From the `spurs` row of the Norse table:

> `snowshoes` - a wooden snowshoe frame with rawhide webbing lying flat behind each heel - fitting `inlay` - centre `stick`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          snowshoes
    anchor:        spurs
    namespace:     armorpieces_norse
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\norse\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\norse\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Snowshoes",
                           fittings: ["armorpieces:inlay"],
                           static: true,
                           recipe: { centre: "minecraft:stick", craftable: true } }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Lime wood is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `jarl` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:stick` is confirmed free against every
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

The two **cross-cords** carry no static. They are masked `inlay` (rawhide - dyed matter) and are the piece's material surface until a player dyes them; the frame is static wood.

## The rig, in Blockbench coordinates

    left leg box            x -3.9 .. 0.1   y 0 .. 12       z -2 .. 2
    leggings shell (+0.4)   x -4.3 .. 0.5   y -0.4 .. 12.4  z -2.4 .. 2.4
    boots shell (+0.9)      x -4.8 .. 1.0   y -0.9 .. 12.9  z -2.9 .. 2.9
    the `spurs` anchor       (-1.9, 2, 2)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-1.9, 2, 2)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

A snowshoe, seen as its tail: a leather binding round the back of the heel, and from it two long wooden rails lying flat on the ground straight back from the heel, joined by two rawhide cross-cords and closed by a rounded tail piece at the end. It lies FLAT - everything is a hair above the ground.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **binding** — the leather binding round the back of the heel:

        x -5.12 .. 1.23    y 0.69 .. 1.33    z 2.95 .. 3.43

- **rail_l** — the outer wooden rail, flat on the ground going back:

        x -3.28 .. -2.61    y 0.07 .. 0.53    z 3.43 .. 7.03

- **rail_r** — the inner rail:

        x -1.13 .. -0.48    y 0.07 .. 0.53    z 3.43 .. 7.03

- **cross_a** — the front rawhide cross-cord:

        x -2.61 .. -1.13    y 0.12 .. 0.49    z 3.67 .. 4.13

- **cross_b** — the rear cross-cord:

        x -2.61 .. -1.13    y 0.12 .. 0.49    z 5.47 .. 5.93

- **tail** — the rounded tail piece closing the frame:

        x -2.77 .. -1.07    y 0.07 .. 0.53    z 7.03 .. 7.93

**6 cubes in total is the budget**, and there is no 7th.

**Envelope budget.** Stay inside `x -5.2 .. 1.3, y 0.0 .. 1.4, z 2.9 .. 8.0`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -3.2 .. 3.3      y  10.6 .. 12.0      z  2.9 .. 8.0

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `5.12`, so the pair spans **10.24**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `spurs` | x -5.75..-1.50, y 2.24..7.83, z 1.50..9.76 | the mod's spur reaches further back than your tail; you lie on the ground where it stands up |
| `streamers` | x -5.55..0.60, y 0.28..3.55, z 0.85..7.98 | the precedent for something trailing to z 8 behind the heel |
| `winingas (greaves)` | x -5.10..0.50, y 0.30..4.20, z -3.80..-2.20 | your own pack's leg wraps, built in this batch, all in FRONT of the leg where you are all behind - never near |
| `hip_axes (tassets)` | x -5.30..-4.00, y 4.70..12.10, z -0.60..2.70 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `fur_cops (knees)` | x -3.90..0.10, y 4.30..8.40, z -4.20..-2.80 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

rails and tail: base **120**, `up` **145**. binding: base **90**. cross-cords: base **190**, `up` **210**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `rail_l`, `rail_r`, `tail`: base `#a37a48`, `up` `#bf9460` — lime wood - the shield board and the axe haft
- `binding`: base `#5a3d28`, `up` `#75523a` — oiled leather - the straps and the belt

**Mask `part_inlay`** — flat **140**, on `cross_a`, `cross_b`. 140 is the value every mask in this project
uses.

## Done when

- [ ] The check is clean, or every `!` left standing is one this brief allows.
- [ ] Envelope inside the budget above, **reported in the check's frame**.
- [ ] Pair span reported.
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

