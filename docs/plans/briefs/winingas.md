# Brief: Winingas

A piece of **Armor Pieces: Norse** (`armorpieces_norse`) — riveted iron, wolf-grey fur, painted lime wood and a little gold - the north as the sagas tell it, hair and beard included.

From the `greaves` row of the Norse table:

> `winingas` - three bands of wool wound up each shin, held by two vertical leather straps - fitting `inlay` - centre `brown_wool`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          winingas
    anchor:        greaves
    namespace:     armorpieces_norse
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\norse\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\norse\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Winingas",
                           fittings: ["armorpieces:inlay"],
                           static: true,
                           recipe: { centre: "minecraft:brown_wool", craftable: true } }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Oiled leather is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `jarl` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:brown_wool` is confirmed free against every
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

The three **wraps** carry no static. They are masked `inlay` (wool - dyed matter) and answer the trim until a player dyes them; the straps are static leather.

## The rig, in Blockbench coordinates

    left leg box            x -3.9 .. 0.1   y 0 .. 12       z -2 .. 2
    leggings shell (+0.4)   x -4.3 .. 0.5   y -0.4 .. 12.4  z -2.4 .. 2.4
    boots shell (+0.9)      x -4.8 .. 1.0   y -0.9 .. 12.9  z -2.9 .. 2.9
    the `greaves` anchor       (-1.9, 4, -2)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-1.9, 4, -2)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

The leg wraps of the north: three bands of undyed wool wound round the shin from the ankle to below the knee, each a hair narrower than the one below, and two leather straps running straight down over them at the front to hold them. The wool takes the trim until a player dyes it; the straps stay leather.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **wrap_lo** — the lowest band, at the ankle:

        x -5.03 .. 0.41    y 0.39 .. 1.46    z -3.47 .. -2.33

- **wrap_mid** — the middle band:

        x -5.03 .. 0.23    y 1.83 .. 2.97    z -3.28 .. -2.42

- **wrap_up** — the top band, below the knee:

        x -4.93 .. 0.17    y 3.17 .. 4.11    z -3.27 .. -2.48

- **strap_a** — the outer strap, straight down over the bands:

        x -4.17 .. -3.43    y 0.47 .. 4.03    z -3.68 .. -3.47

- **strap_b** — the inner strap:

        x -1.03 .. -0.37    y 0.47 .. 4.03    z -3.68 .. -3.47

**5 cubes in total is the budget**, and there is no 6th.

**Envelope budget.** Stay inside `x -5.1 .. 0.5, y 0.3 .. 4.2, z -3.8 .. -2.2`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.4 .. 3.2      y  7.8 .. 11.7      z  -3.8 .. -2.2

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `5.03`, so the pair spans **10.06**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `puttees` | x -5.05..0.59, y -0.70..4.45, z -4.15..-1.45 | the mod's own puttees - your closest relative; you are shallower and carry straps |
| `llama_wraps` | x -5.37..0.53, y 0.14..5.67, z -3.47..-2.27 | the Animals' wraps - the same three-band idea in wool |
| `fur_cops (knees)` | x -3.90..0.10, y 4.30..8.40, z -4.20..-2.80 | your own pack's knee, built in this batch, starting at y 4.37 - your top band ends at 4.13, clear |
| `hip_axes (tassets)` | x -5.30..-4.00, y 4.70..12.10, z -0.60..2.70 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `snowshoes (spurs)` | x -5.20..1.30, y 0.00..1.40, z 2.90..8.00 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

wraps: base **190**, `north` **205**, `down` **160**. straps: base **90**.

**Each wrap's back face is inside the boot.** The bands run to z -2.33 / -2.43 / -2.53 and the boots shell's front wall is at z -2.9, so the back of every band is buried and only the front and the two sides show.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `strap_a`, `strap_b`: base `#5a3d28`, `up` `#75523a` — oiled leather - the straps and the belt

**Mask `part_inlay`** — flat **140**, on `wrap_lo`, `wrap_mid`, `wrap_up`. 140 is the value every mask in this project
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

