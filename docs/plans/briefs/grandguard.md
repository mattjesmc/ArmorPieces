# Brief: Grandguard

A piece of **Armor Pieces: Tournament** (`armorpieces_tourney`) — bright steel and heraldry - azure and gold, the joust and the lists, a lady's favour on the arm; the hardware answers the trim and the colours are its own.

From the `pauldrons` row of the Tournament table:

> `grandguard` - a big domed shoulder plate with an upstanding neck guard and one lower lame - fitting `guard` - centre `copper_chestplate`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          grandguard
    anchor:        pauldrons
    namespace:     armorpieces_tourney
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\tourney\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\tourney\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Grandguard",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:copper_chestplate", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Heraldic azure is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `tilt` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:copper_chestplate` is confirmed free against every
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

The **plate**, **haute-piece** and **lame** carry no static. They are masked `guard` and are the piece's material surface; the lozenge is static azure.

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

The tilt reinforce: a big domed steel plate over the whole shoulder, an upstanding haute-piece rising from its inner edge beside the neck to catch a lance, one lower lame under the plate's outer edge, and a small azure lozenge painted on the outboard face. Heavy, smooth steel; it takes the trim.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **plate** — the domed plate over the shoulder:

        x -10.04 .. -4.47    y 22.37 .. 25.83    z -3.53 .. 2.87

- **haute** — the haute-piece standing up beside the neck:

        x -6.53 .. -4.47    y 25.83 .. 28.33    z -2.43 .. 1.47

- **lame** — the lower lame under the plate's outer edge:

        x -9.83 .. -6.07    y 20.57 .. 22.37    z -3.03 .. 2.57

- **lozenge** — the azure lozenge painted on the outboard face:

        x -10.23 .. -10.04    y 23.07 .. 24.87    z -1.33 .. 0.87

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -10.3 .. -4.4, y 20.5 .. 28.4, z -3.6 .. 3.0`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the arm bone's pivot at Blockbench `(-5, 22, 0)` - **not** the top of the arm box. For this socket:

    check_x = -5 - bb_x        check_y = 22 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -0.6 .. 5.3      y  -6.4 .. 1.5      z  -3.6 .. 3.0

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `10.23`, so the pair spans **20.46**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the arms are already outboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `spiked_pauldrons` | x -9.85..-7.20, y 22.40..28.53, z -3.10..3.10 | the mod's spiked pauldron - your height band, rising as high as your haute-piece |
| `spaulders` | x -10.33..-5.75, y 20.37..25.50, z -3.50..3.50 | the mod's spaulders - the plain plate you are the tournament version of |
| `blaze_bracers (vambraces)` | x -9.45..-2.65, y 15.15..20.45, z -3.35..3.35 | the tallest vambrace, worn WITH you, ending at y 20.45 - your lame starts at 20.57, clear |
| `favour (vambraces)` | x -10.00..-2.60, y 11.50..16.90, z -3.40..3.40 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

plate: base **150**, `up` **195**, `west` **170**, `down` **105**. haute-piece: base **150**, `up` **190**. lame: base **140**, `down` **100**. lozenge: base **130**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `lozenge`: base `#2244aa`, `up` `#3560c8` — heraldic azure - the field of the arms

**Mask `part_guard`** — flat **140**, on `plate`, `haute`, `lame`. 140 is the value every mask in this project
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

