# Brief: Epomides

A piece of **Armor Pieces: Antiquity** (`armorpieces_antiquity`) — bronze and red leather - Greece and Rome, the hoplite and the legionary, every piece a thing with a Latin or Greek name.

From the `pauldrons` row of the Antiquity table:

> `epomides` - a bronze yoke plate on the shoulder with three red leather strips hanging down the outer arm - fitting `guard` - centre `leather_helmet`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          epomides
    anchor:        pauldrons
    namespace:     armorpieces_antiquity
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\antiquity\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\antiquity\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Epomides",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:leather_helmet", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Red leather is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `legion` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:leather_helmet` is confirmed free against every
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

The **yoke** carries no static. It is masked `guard` and is the piece's whole material surface; the strips are static leather.

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

The shoulder flaps of a hoplite's cuirass: a bronze yoke plate lying over the top of the shoulder, and three strips of stiff red leather hanging straight down from its outer edge over the upper arm, a gap between each. Bronze on top, leather down the side.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **yoke** — the bronze yoke plate over the shoulder:

        x -9.33 .. -4.67    y 25.07 .. 25.83    z -2.83 .. 2.83

- **strip_a** — the front strip hanging down the outer arm:

        x -9.73 .. -9.33    y 20.67 .. 25.07    z -2.73 .. -1.37

- **strip_b** — the middle strip, a little longer:

        x -9.73 .. -9.33    y 20.57 .. 25.07    z -0.63 .. 0.63

- **strip_c** — the back strip:

        x -9.73 .. -9.33    y 20.67 .. 25.07    z 1.37 .. 2.73

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -9.8 .. -4.6, y 20.5 .. 25.9, z -2.9 .. 2.9`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the arm bone's pivot at Blockbench `(-5, 22, 0)` - **not** the top of the arm box. For this socket:

    check_x = -5 - bb_x        check_y = 22 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -0.4 .. 4.8      y  -3.9 .. 1.5      z  -2.9 .. 2.9

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `9.73`, so the pair spans **19.46**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the arms are already outboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `epaulettes` | x -9.85..-7.20, y 22.00..25.95, z -2.60..2.60 | the mod's epaulettes - a shoulder plate at your depth |
| `lames` | x -10.85..-7.20, y 19.05..25.70, z -3.10..3.10 | the mod's lames reach lower and further out than your strips |
| `blaze_bracers (vambraces)` | x -9.45..-2.65, y 15.15..20.45, z -3.35..3.35 | the tallest vambrace, worn WITH you, ending at y 20.45 - your strips end at 20.57, clear |
| `manica (vambraces)` | x -9.60..-2.50, y 12.00..18.30, z -3.50..3.50 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

strips: base **100**, `west` **120**, `down` **70**, and a `pixels` row of 200 near the bottom of each `west` face if the tool lets you, for the bronze stud. yoke: base **145**, `up` **185**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `strip_a`, `strip_b`, `strip_c`: base `#8e2a24`, `up` `#ad3a32` — red leather - the legion's own dyed leather, and `down` #6e1f1a, its shadow

**Mask `part_guard`** — flat **140**, on `yoke`. 140 is the value every mask in this project
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

