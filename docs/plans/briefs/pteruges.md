# Brief: Pteruges

A piece of **Armor Pieces: Antiquity** (`armorpieces_antiquity`) — bronze and red leather - Greece and Rome, the hoplite and the legionary, every piece a thing with a Latin or Greek name.

From the `tassets` row of the Antiquity table:

> `pteruges` - a waistband with four strips of red leather hanging over each thigh - fitting `inlay` - centre `brown_dye`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          pteruges
    anchor:        tassets
    namespace:     armorpieces_antiquity
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\antiquity\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\antiquity\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Pteruges",
                           fittings: ["armorpieces:inlay"],
                           static: true,
                           recipe: { centre: "minecraft:brown_dye", craftable: true } }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Red leather is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `legion` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:brown_dye` is confirmed free against every
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

The **band** carries no static. It is masked `inlay` (cloth - dyed matter) and is the piece's whole material surface until a player dyes it; the strips are static leather.

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

The skirt of a cuirass: a cloth waistband over the top of each hip, and hanging from it four strips of stiff red leather - three down the outside of the thigh, one down the front - with a gap between each so they swing. The strips are the piece; the band is what holds them.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **band** — the waistband over the top of the hip:

        x -4.43 .. 0.47    y 11.37 .. 12.07    z -2.88 .. 2.93

- **strip_a** — the front-outer strip, down the outside of the thigh:

        x -5.01 .. -4.36    y 6.57 .. 11.37    z -2.70 .. -1.47

- **strip_b** — the middle strip, a little longer:

        x -5.01 .. -4.36    y 6.27 .. 11.37    z -0.53 .. 0.53

- **strip_c** — the back strip:

        x -5.01 .. -4.36    y 6.57 .. 11.37    z 1.47 .. 2.64

- **strip_f** — the strip down the front of the thigh:

        x -3.73 .. -2.45    y 7.33 .. 11.37    z -3.38 .. -2.88

**5 cubes in total is the budget**, and there is no 6th.

**Envelope budget.** Stay inside `x -5.1 .. 0.6, y 6.2 .. 12.2, z -3.5 .. 3.0`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.5 .. 3.2      y  -0.2 .. 5.8      z  -3.5 .. 3.0

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `5.01`, so the pair spans **10.02**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `wing_tatters` | x -4.70..-4.40, y 6.45..10.09, z -2.29..2.35 | the Dragonslayer's strips - the same thing in membrane |
| `loin_panels` | x -3.40..-0.40, y 5.44..11.96, z -3.60..3.60 | the court's loin panels - the precedent for a panel hanging down the front |
| `poleyns (knees)` | x -4.55..-1.55, y 4.90..8.30, z -4.65..-2.65 | worn WITH you, rising to y 8.30 - your front strip ends at 7.37 and crosses its box in a hull test, an OVERLAP `-`, not a `!` |
| `gorgon_cops (knees)` | x -3.60..-0.20, y 4.30..7.30, z -4.20..-2.80 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `ocreae (greaves)` | x -5.10..0.50, y 0.30..4.20, z -4.00..-2.30 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `caligae (spurs)` | x -5.50..1.40, y 0.30..4.10, z 0.30..4.10 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

strips: base **100**, `west` **120** (the outboard face), `north` **115** on the front strip, `down` **200** (a bronze tip). band: base **140**, `up` **165**.

**The band encloses the thigh.** Its inner face at x 0.47 is inside the boots shell (which reaches x 1.0) and never seen.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `strip_a`, `strip_b`, `strip_c`, `strip_f`: base `#8e2a24`, `up` `#ad3a32` — red leather - the legion's own dyed leather, and `down` #6e1f1a, its shadow

**Mask `part_inlay`** — flat **140**, on `band`. 140 is the value every mask in this project
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

