# Brief: Torc

A piece of **Armor Pieces: Norse** (`armorpieces_norse`) — riveted iron, wolf-grey fur, painted lime wood and a little gold - the north as the sagas tell it, hair and beard included.

From the `collar` row of the Norse table:

> `torc` - a twisted neck ring lying on the upper chest, open at the front between two knobs - fitting `guard` - centre `raw_gold`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          torc
    anchor:        collar
    namespace:     armorpieces_norse
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\norse\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\norse\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Torc",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:raw_gold", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Torc gold is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `jarl` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:raw_gold` is confirmed free against every
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

The two **arms** carry no static; they are masked `guard` and answer the trim until a player fills the fitting. The **knobs** are static gold by default AND masked `guard`.

## The rig, in Blockbench coordinates

    body box                x -4 .. 4       y 12 .. 24      z -2 .. 2
    chestplate shell (+1)   x -5 .. 5       y 11 .. 25      z -3 .. 3
    leggings shell (+0.5)   x -4.5 .. 4.5   y 11.5 .. 24.5  z -2.5 .. 2.5
    the `collar` anchor       (0, 23, -2)

Front is **negative z**. This socket is not mirrored: build the whole piece once.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(0, 23, -2)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

A torc: a thick twisted ring lying on the upper chest at the base of the neck, open at the front where its two ends finish in round knobs a little apart. Two arms, two knobs; it sits flat against the chest and reads as one heavy ring of gold.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **arm_l** — the left arm of the ring, across the upper chest:

        x -4.33 .. -1.07    y 22.93 .. 23.97    z -3.70 .. -3.16

- **arm_r** — the right arm:

        x 1.07 .. 4.37    y 22.93 .. 23.97    z -3.70 .. -3.16

- **knob_l** — the left terminal knob:

        x -1.37 .. -0.23    y 22.63 .. 24.27    z -3.97 .. -3.05

- **knob_r** — the right knob:

        x 0.23 .. 1.37    y 22.63 .. 24.27    z -3.97 .. -3.05

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -4.4 .. 4.5, y 22.5 .. 24.4, z -4.1 .. -3.0`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the body bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -4.5 .. 4.4      y  -0.4 .. 1.5      z  -4.1 .. -3.0

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `fang_necklace` | x -3.20..3.20, y 21.10..24.30, z -3.90..-3.05 | the Wild Hunt's necklace - your height band exactly |
| `pendant` | x -3.39..3.39, y 19.00..24.46, z -3.85..-3.10 | the mod's pendant, hanging lower than you |
| `gorget` | x -6.50..6.50, y 19.50..25.25, z -3.75..0.75 | wider than you and wrapping the shoulders; you stay on the chest |
| `round_shield (back)` | x -7.00..7.00, y 11.00..25.00, z 3.60..5.50 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `seax_belt (belt)` | x -5.40..5.40, y 11.40..14.40, z -4.10..3.40 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

arms: base **150**, `north` **185**, and alternate `pixels` of 150 / 190 along the length if the tool lets you, so the ring reads as twisted. knobs: base **170**, `north` **210**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `knob_l`, `knob_r`: base `#d9a441`, `up` `#f0c460` — torc gold - the terminals' own gold

**Mask `part_guard`** — flat **140**, on `arm_l`, `arm_r`, `knob_l`, `knob_r`. 140 is the value every mask in this project
uses.

## Done when

- [ ] The check is clean, or every `!` left standing is one this brief allows.
- [ ] Envelope inside the budget above, **reported in the check's frame**.
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

