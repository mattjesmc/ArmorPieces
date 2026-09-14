# Brief: Haidate

A piece of **Armor Pieces: Samurai** (`armorpieces_samurai`) — black lacquer over iron, red odoshi lacing and gilt fittings - the armor of a daimyo, every piece a named part of a real suit.

From the `knees` row of the Samurai table:

> `haidate` - an indigo cloth panel over each knee set with lacquered plates in a brick pattern - fitting `inlay` - centre `leather_leggings`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          haidate
    anchor:        knees
    namespace:     armorpieces_samurai
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\samurai\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\samurai\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Haidate",
                           fittings: ["armorpieces:inlay"],
                           static: true,
                           recipe: { centre: "minecraft:leather_leggings", craftable: true } }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Indigo cloth is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `daimyo` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:leather_leggings` is confirmed free against every
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

Nothing here is bare material: the **backing** is static indigo by default AND masked `inlay`, so a player re-dyes the cloth, and the plates are static black. That is allowed because the fitting is there to change.

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

The thigh apron's lower panel: a rectangle of indigo cloth hanging over the front of the knee, with three small black lacquered plates sewn onto it in a brick pattern - two above, one below and between them. Soft cloth with hard plates; the plates stand a little proud of the cloth.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **backing** — the indigo cloth panel over the knee:

        x -3.77 .. -0.03    y 4.27 .. 6.75    z -3.54 .. -2.93

- **plate_a** — the upper-outer plate:

        x -3.47 .. -2.08    y 5.47 .. 6.37    z -3.87 .. -3.54

- **plate_b** — the upper-inner plate:

        x -1.68 .. -0.33    y 5.47 .. 6.37    z -3.87 .. -3.54

- **plate_c** — the lower plate, between the two above:

        x -2.63 .. -1.19    y 4.43 .. 5.33    z -3.87 .. -3.54

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -3.9 .. 0.1, y 4.2 .. 6.8, z -4.0 .. -2.8`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.0 .. 2.0      y  5.2 .. 7.8      z  -4.0 .. -2.8

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `3.77`, so the pair spans **7.54**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `magma_cops` | x -3.55..-0.25, y 3.72..7.65, z -4.05..-2.58 | a pack knee cop at your width |
| `knee_studs` | x -3.15..-0.65, y 3.90..6.10, z -3.50..-3.00 | the mod's studded knee - the same idea in steel |
| `silverfish_greaves (greaves)` | x -5.27..0.43, y 0.24..6.13, z -4.63..-2.33 | worn WITH you and rising to y 6.13 - your panel starts at 4.27, so expect an OVERLAP note, a `-` and not a `!` |
| `kusazuri (tassets)` | x -5.40..0.60, y 6.70..12.20, z -3.90..3.80 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `suneate (greaves)` | x -5.10..0.30, y 0.40..4.20, z -3.80..-2.30 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `waraji (spurs)` | x -5.20..1.40, y 0.30..2.80, z 0.50..4.40 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

backing: base **90**, `north` **105**. plates: base **60**, `north` **80**, `down` **40**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `backing`: base `#2b3a6b`, `up` `#3d4f8a` — indigo cloth - the sleeve and backing cloth of a real suit
- `plate_a`, `plate_b`, `plate_c`: base `#1a1614`, `up` `#2e2724` — lacquer black - the suit's own black, with a warm brown in the light

**Mask `part_inlay`** — flat **140**, on `backing`. 140 is the value every mask in this project
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

