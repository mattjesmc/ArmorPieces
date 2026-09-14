# Brief: Manica

A piece of **Armor Pieces: Antiquity** (`armorpieces_antiquity`) — bronze and red leather - Greece and Rome, the hoplite and the legionary, every piece a thing with a Latin or Greek name.

From the `vambraces` row of the Antiquity table:

> `manica` - four overlapping bronze lames down each forearm on a leather strap - fitting `guard` - centre `chainmail_chestplate`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          manica
    anchor:        vambraces
    namespace:     armorpieces_antiquity
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\antiquity\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\antiquity\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Manica",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:chainmail_chestplate", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Dark leather is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `legion` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:chainmail_chestplate` is confirmed free against every
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

The four **lames** carry no static. They are masked `guard` and are the piece's whole material surface; the strap is static leather.

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

The gladiator's arm guard: four bronze lames round the forearm, each a hair wider than the one above so they step outward toward the wrist, and a leather strap at the wrist below them. Metal that answers the trim; the strap is the only leather.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **lame_a** — the top lame, the narrowest:

        x -9.13 .. -2.87    y 17.07 .. 18.23    z -3.13 .. 3.13

- **lame_b** — the second lame:

        x -9.23 .. -2.77    y 15.67 .. 17.07    z -3.23 .. 3.23

- **lame_c** — the third lame:

        x -9.31 .. -2.67    y 14.27 .. 15.67    z -3.33 .. 3.33

- **lame_d** — the lowest and widest lame:

        x -9.47 .. -2.57    y 12.87 .. 14.27    z -3.43 .. 3.43

- **strap** — the leather strap at the wrist:

        x -9.05 .. -2.97    y 12.07 .. 12.87    z -3.05 .. 3.04

**5 cubes in total is the budget**, and there is no 6th.

**Envelope budget.** Stay inside `x -9.6 .. -2.5, y 12.0 .. 18.3, z -3.5 .. 3.5`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the arm bone's pivot at Blockbench `(-5, 22, 0)` - **not** the top of the arm box. For this socket:

    check_x = -5 - bb_x        check_y = 22 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.5 .. 4.6      y  3.7 .. 10.0      z  -3.5 .. 3.5

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `9.47`, so the pair spans **18.94**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the arms are already outboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `chitin_bracers` | x -9.47..-2.57, y 12.43..18.67, z -3.43..3.43 | the Hive's bracer - the same stepped plates, in chitin |
| `vambraces` | x -10.00..-5.50, y 12.00..18.00, z -4.00..4.00 | the mod's own vambrace - a plate on the outside where you go all round |
| `epomides (pauldrons)` | x -9.80..-4.60, y 20.50..25.90, z -2.90..2.90 | your own pack's shoulder flaps, built in this batch, ending at y 20.57 - your top lame ends at 18.23, clear |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

lames: base **150**, `up` **190** (each lame's top edge catches light), `down` **110**. strap: base **70**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `strap`: base `#4a2f1e`, `up` `#5f3f2a` — dark leather - the straps

**Mask `part_guard`** — flat **140**, on `lame_a`, `lame_b`, `lame_c`, `lame_d`. 140 is the value every mask in this project
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

