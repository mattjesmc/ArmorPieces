# Brief: Favour

A piece of **Armor Pieces: Tournament** (`armorpieces_tourney`) — bright steel and heraldry - azure and gold, the joust and the lists, a lady's favour on the arm; the hardware answers the trim and the colours are its own.

From the `vambraces` row of the Tournament table:

> `favour` - a rose scarf knotted round the forearm with two ends trailing down the outside - fitting `inlay` - centre `rose_bush`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          favour
    anchor:        vambraces
    namespace:     armorpieces_tourney
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\tourney\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\tourney\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Favour",
                           fittings: ["armorpieces:inlay"],
                           static: true,
                           recipe: { centre: "minecraft:rose_bush", craftable: true } }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. The favour's rose is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `tilt` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:rose_bush` is confirmed free against every
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

Nothing here is bare material: the whole favour is static rose by default AND masked `inlay`, so a player re-dyes it. That is allowed because the fitting is there to change.

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

A lady's favour worn into the lists: a band of rose-coloured silk tied round the forearm below the elbow, a knot standing off its outboard side, and two loose ends trailing down the outside of the arm from the knot, one longer than the other. All silk; a player re-dyes it to their own lady's colours.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **band** — the silk band round the forearm:

        x -9.31 .. -2.67    y 15.37 .. 16.83    z -3.33 .. 3.33

- **knot** — the knot on the outboard side:

        x -9.93 .. -9.31    y 15.57 .. 16.63    z -1.03 .. 0.36

- **tail_a** — the long trailing end:

        x -9.77 .. -9.31    y 11.57 .. 15.57    z -1.53 .. -0.45

- **tail_b** — the short trailing end:

        x -9.67 .. -9.31    y 12.37 .. 15.57    z 0.36 .. 1.39

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -10.0 .. -2.6, y 11.5 .. 16.9, z -3.4 .. 3.4`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the arm bone's pivot at Blockbench `(-5, 22, 0)` - **not** the top of the arm box. For this socket:

    check_x = -5 - bb_x        check_y = 22 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.4 .. 5.0      y  5.1 .. 10.5      z  -3.4 .. 3.4

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `9.93`, so the pair spans **19.86**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the arms are already outboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `wraps` | x -9.56..-3.75, y 12.10..18.25, z -3.95..3.49 | the wayfarer's cloth wraps - the closest thing to you on this socket |
| `blaze_bracers` | x -9.45..-2.65, y 15.15..20.45, z -3.35..3.35 | a pack bracer at your band's height |
| `wing_cases (pauldrons)` | x -11.02..-7.05, y 14.07..25.85, z -2.75..2.75 | worn WITH you, reaching down to y 14.07 on the outboard side - an OVERLAP `-`, not a `!` |
| `grandguard (pauldrons)` | x -10.30..-4.40, y 20.50..28.40, z -3.60..3.00 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

band: base **160**, `up` **185**, `down` **130**. knot: base **170**, `west` **195**. tails: base **155**, `west` **175**, `down` **125**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `band`, `knot`, `tail_a`, `tail_b`: base `#c8395e`, `up` `#e0577a` — the favour's rose - a lady's colours

**Mask `part_inlay`** — flat **140**, on `band`, `knot`, `tail_a`, `tail_b`. 140 is the value every mask in this project
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

