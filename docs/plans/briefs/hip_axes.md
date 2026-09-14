# Brief: Hip Axes

A piece of **Armor Pieces: Norse** (`armorpieces_norse`) — riveted iron, wolf-grey fur, painted lime wood and a little gold - the north as the sagas tell it, hair and beard included.

From the `tassets` row of the Norse table:

> `hip_axes` - a bearded axe hanging from a loop at each hip, haft down, blade back - fitting `guard` - centre `stone_axe`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          hip_axes
    anchor:        tassets
    namespace:     armorpieces_norse
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\norse\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\norse\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Hip Axes",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:stone_axe", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Lime wood is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `jarl` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:stone_axe` is confirmed free against every
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

The **head** and **beard** carry no static. They are masked `guard` and are the piece's material surface; the haft and loop are static.

## The rig, in Blockbench coordinates

    left leg box            x -3.9 .. 0.1   y 0 .. 12       z -2 .. 2
    leggings shell (+0.4)   x -4.3 .. 0.5   y -0.4 .. 12.4  z -2.4 .. 2.4
    boots shell (+0.9)      x -4.8 .. 1.0   y -0.9 .. 12.9  z -2.9 .. 2.9
    the `tassets` anchor       (-1.9, 10, 0)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-1.9, 10, 0)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

An axe at the hip: a leather loop at the top of the thigh, a wooden haft hanging straight down from it along the outside of the leg, and the iron head at the top of the haft with its blade pointing BACKWARDS and its beard hanging down below the blade. The head is up, the haft is down - it hangs the way an axe is carried.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **loop** — the leather loop at the top of the hip:

        x -5.01 .. -4.36    y 11.27 .. 12.03    z -0.53 .. 0.53

- **haft** — the wooden haft, hanging down the outside of the thigh:

        x -4.88 .. -4.36    y 4.84 .. 11.27    z -0.33 .. 0.33

- **head** — the iron axe head at the top of the haft, blade pointing back:

        x -5.18 .. -4.08    y 8.27 .. 10.43    z 0.33 .. 2.64

- **beard** — the beard of the axe, hanging below the blade:

        x -5.01 .. -4.08    y 6.83 .. 8.27    z 1.77 .. 2.64

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -5.3 .. -4.0, y 4.7 .. 12.1, z -0.6 .. 2.7`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  2.1 .. 3.4      y  -0.1 .. 7.3      z  -0.6 .. 2.7

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `5.18`, so the pair spans **10.36**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `wing_tatters` | x -4.70..-4.40, y 6.45..10.09, z -2.29..2.35 | the Dragonslayer's strips - a thin thing hanging on the outside of the thigh, like your haft |
| `thigh_sheath` | x -5.35..0.85, y 3.53..11.94, z -2.80..2.80 | the mod's thigh sheath - the precedent for a weapon carried on this socket |
| `garters (knees)` | x -5.95..1.25, y 3.80..6.85, z -3.05..0.20 | worn WITH you; your haft crosses its box between y 4.87 and 6.85 in a hull test - an OVERLAP `-`, not a `!` |
| `fur_cops (knees)` | x -3.90..0.10, y 4.30..8.40, z -4.20..-2.80 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `winingas (greaves)` | x -5.10..0.50, y 0.30..4.20, z -3.80..-2.20 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `snowshoes (spurs)` | x -5.20..1.30, y 0.00..1.40, z 2.90..8.00 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

haft: base **110**, `west` **125**. loop: base **90**. head and beard: base **140**, `west` **170**, `south` **185** (the blade's edge faces back).

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `haft`: base `#a37a48`, `up` `#bf9460` — lime wood - the shield board and the axe haft
- `loop`: base `#5a3d28`, `up` `#75523a` — oiled leather - the straps and the belt

**Mask `part_guard`** — flat **140**, on `head`, `beard`. 140 is the value every mask in this project
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

