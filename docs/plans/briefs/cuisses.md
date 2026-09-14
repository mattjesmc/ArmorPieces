# Brief: Cuisses

A piece of **Armor Pieces: Tournament** (`armorpieces_tourney`) — bright steel and heraldry - azure and gold, the joust and the lists, a lady's favour on the arm; the hardware answers the trim and the colours are its own.

From the `tassets` row of the Tournament table:

> `cuisses` - a steel thigh plate with a raised rib and one articulated lame below it - fitting `guard` - centre `iron_leggings`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          cuisses
    anchor:        tassets
    namespace:     armorpieces_tourney
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\tourney\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\tourney\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Cuisses",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:iron_leggings", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Heraldic or is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `tilt` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:iron_leggings` is confirmed free against every
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

The **plate**, **rib** and **lame** carry no static. They are masked `guard` and are the piece's material surface; the stud is static gold.

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

Plate cuisses: a steel plate wrapping the front and outside of the thigh from the hip to above the knee, a raised rib running down its front, and one narrower lame hanging under its bottom edge. Smooth tournament steel that takes the trim, with a small gold stud at the top of the rib.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **plate** — the thigh plate, front and outside:

        x -4.78 .. 0.39    y 6.83 .. 11.73    z -3.38 .. 1.57

- **rib** — the raised rib down the front:

        x -3.38 .. -1.01    y 7.33 .. 11.23    z -3.80 .. -3.38

- **lame** — the lame under the bottom edge:

        x -4.73 .. 0.27    y 6.05 .. 6.83    z -3.38 .. 1.47

- **stud** — the gold stud at the top of the rib:

        x -2.58 .. -1.87    y 10.57 .. 11.13    z -3.98 .. -3.80

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -4.9 .. 0.5, y 6.0 .. 11.8, z -4.1 .. 1.7`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.4 .. 3.0      y  0.2 .. 6.0      z  -4.1 .. 1.7

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `4.78`, so the pair spans **9.56**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `tassets` | x -4.60..-1.25, y 5.18..12.25, z -4.68..-0.90 | the mod's own tassets - your height band, hanging where you wrap |
| `ravager_saddle` | x -5.15..-0.85, y 6.15..12.15, z -3.40..2.85 | a pack hip piece wrapping the thigh like you |
| `boot_cuffs (greaves)` | x -5.51..1.66, y 8.50..9.82, z -3.56..3.61 | worn WITH you; its cuff crosses your plate in a hull test - an OVERLAP `-`, not a `!` |
| `rondel_cops (knees)` | x -5.70..-0.20, y 3.30..6.00, z -3.80..-1.00 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `schynbalds (greaves)` | x -5.60..0.30, y 1.00..3.30, z -3.70..1.50 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `sabatons (spurs)` | x -5.20..0.30, y 0.00..1.70, z -7.10..3.90 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

plate: base **150**, `north` **175**, `west` **165**, `down` **110**. rib: base **165**, `north` **200**. lame: base **140**, `down` **100**. stud: base **180**.

**The plate's inner face at x 0.37 is inside the leggings shell** (which reaches x 0.5) and never seen.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `stud`: base `#e0b13a`, `up` `#f3cb5c` — heraldic or - the gold of the arms

**Mask `part_guard`** — flat **140**, on `plate`, `rib`, `lame`. 140 is the value every mask in this project
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

