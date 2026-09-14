# Brief: Schynbalds

A piece of **Armor Pieces: Tournament** (`armorpieces_tourney`) — bright steel and heraldry - azure and gold, the joust and the lists, a lady's favour on the arm; the hardware answers the trim and the colours are its own.

From the `greaves` row of the Tournament table:

> `schynbalds` - a steel shin plate over the front of the shin with an outer wing and a rimmed top - fitting `guard` - centre `chainmail_leggings`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          schynbalds
    anchor:        greaves
    namespace:     armorpieces_tourney
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\tourney\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\tourney\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Schynbalds",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:chainmail_leggings", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Heraldic or is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `tilt` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:chainmail_leggings` is confirmed free against every
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

The **plate** and **wing** carry no static. They are masked `guard` and are the piece's material surface; the rim is static gold.

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

The early plate greave: a steel plate over the front of the shin from the ankle to below the knee, a narrower wing plate down the outside of the shin, and a rolled rim across the top edge of both. Steel that takes the trim; the rim is gilt.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **plate** — the front shin plate:

        x -4.93 .. 0.17    y 1.07 .. 2.93    z -3.48 .. -2.83

- **wing** — the wing plate down the outside of the shin:

        x -5.51 .. -4.92    y 1.07 .. 2.93    z -2.83 .. 1.37

- **rim** — the rolled rim across the top:

        x -5.03 .. 0.23    y 2.93 .. 3.23    z -3.64 .. 1.45

**3 cubes in total is the budget**, and there is no 4th.

**Envelope budget.** Stay inside `x -5.6 .. 0.3, y 1.0 .. 3.3, z -3.7 .. 1.5`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.2 .. 3.7      y  8.7 .. 11.0      z  -3.7 .. 1.5

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `5.51`, so the pair spans **11.02**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `greaves` | x -4.50..0.50, y -0.20..4.80, z -3.65..-0.75 | the mod's own greaves - taller than you, wrapping the same way |
| `dragon_scales` | x -3.50..-0.30, y 0.78..4.38, z -3.52..-3.05 | a pack shin plate at your depth |
| `knee_studs (knees)` | x -3.15..-0.65, y 3.90..6.10, z -3.50..-3.00 | worn WITH you, starting at y 3.90 - your rim ends at 3.23, clear |
| `cuisses (tassets)` | x -4.90..0.50, y 6.00..11.80, z -4.10..1.70 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `rondel_cops (knees)` | x -5.70..-0.20, y 3.30..6.00, z -3.80..-1.00 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `sabatons (spurs)` | x -5.20..0.30, y 0.00..1.70, z -7.10..3.90 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

plate: base **150**, `north` **180**, `down` **110**. wing: base **145**, `west` **175**. rim: base **180**, `up` **215**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `rim`: base `#e0b13a`, `up` `#f3cb5c` — heraldic or - the gold of the arms

**Mask `part_guard`** — flat **140**, on `plate`, `wing`. 140 is the value every mask in this project
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

