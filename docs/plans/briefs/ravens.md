# Brief: Ravens

A piece of **Armor Pieces: Norse** (`armorpieces_norse`) — riveted iron, wolf-grey fur, painted lime wood and a little gold - the north as the sagas tell it, hair and beard included.

From the `pauldrons` row of the Norse table:

> `ravens` - a raven perched on an iron shoulder plate - fitting `guard` - centre `ink_sac`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          ravens
    anchor:        pauldrons
    namespace:     armorpieces_norse
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\norse\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\norse\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Ravens",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:ink_sac", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Raven black is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `jarl` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:ink_sac` is confirmed free against every
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

The **perch** carries no static. It is masked `guard` and is the piece's whole material surface; the bird is static and never answers the trim.

## The rig, in Blockbench coordinates

    left arm box            x -8 .. -4      y 12 .. 24      z -2 .. 2
    sleeve shell (+1)       x -9 .. -3      y 11 .. 25      z -3 .. 3
    the `pauldrons` anchor       (-6, 22, 0)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-6, 22, 0)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

Thought and Memory: a black raven perched on each shoulder, on a small iron plate. A squat body, a head thrust forward with a dark beak, and a tail sticking out behind. It faces forward, the way the wearer does, and it is blockier than a real bird.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **perch** — the iron shoulder plate the bird stands on:

        x -9.03 .. -4.87    y 25.07 .. 25.63    z -2.31 .. 2.31

- **body** — the raven's body:

        x -8.83 .. -6.37    y 25.63 .. 27.43    z -1.83 .. 1.37

- **head** — the head, thrust forward:

        x -8.33 .. -6.85    y 27.43 .. 28.73    z -2.87 .. -1.33

- **beak** — the beak:

        x -7.93 .. -7.27    y 27.73 .. 28.33    z -3.93 .. -2.87

- **tail** — the tail, sticking out behind:

        x -8.11 .. -7.06    y 25.93 .. 26.63    z 1.37 .. 3.31

**5 cubes in total is the budget**, and there is no 6th.

**Envelope budget.** Stay inside `x -9.1 .. -4.8, y 25.0 .. 28.8, z -4.0 .. 3.4`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the arm bone's pivot at Blockbench `(-5, 22, 0)` - **not** the top of the arm box. For this socket:

    check_x = -5 - bb_x        check_y = 22 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -0.2 .. 4.1      y  -6.8 .. -3.0      z  -4.0 .. 3.4

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `9.03`, so the pair spans **18.06**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the arms are already outboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `wither_heads` | x -9.45..-4.55, y 23.55..28.15, z -2.55..2.55 | the Nether's shoulder skulls - a figure on the shoulder at exactly your height |
| `beast_head` | x -10.00..-5.90, y 23.80..29.97, z -4.78..2.90 | the Wild Hunt's, reaching further forward than your beak |
| `blaze_bracers (vambraces)` | x -9.45..-2.65, y 15.15..20.45, z -3.35..3.35 | the tallest vambrace, worn WITH you, stopping at y 20.45 - well below your perch |
| `oath_rings (vambraces)` | x -9.60..-2.40, y 11.60..16.80, z -3.60..3.60 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

body, head, tail: base **35**, `up` **60** (the sheen is on top), `down` **25**. beak: base **50**. perch: base **130**, `up` **165**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `body`, `head`, `tail`: base `#141416`, `up` `#2a2b33` — raven black - with a blue sheen in the light
- `beak`: base `#3a3a3a`, `up` `#4c4c4c` — beak grey

**Mask `part_guard`** — flat **140**, on `perch`. 140 is the value every mask in this project
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

