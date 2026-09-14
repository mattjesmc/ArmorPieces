# Brief: Scutum

A piece of **Armor Pieces: Antiquity** (`armorpieces_antiquity`) — bronze and red leather - Greece and Rome, the hoplite and the legionary, every piece a thing with a Latin or Greek name.

From the `back` row of the Antiquity table:

> `scutum` - a tall red rectangular shield on the back with a bronze spine and boss - fitting `guard` - centre `painting`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          scutum
    anchor:        back
    namespace:     armorpieces_antiquity
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\antiquity\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\antiquity\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Scutum",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:painting", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Red leather is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `legion` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:painting` is confirmed free against every
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

The **spine** and **boss** carry no static. They are masked `guard` and are the piece's material surface; the board is static red.

## The rig, in Blockbench coordinates

    body box                x -4 .. 4       y 12 .. 24      z -2 .. 2
    chestplate shell (+1)   x -5 .. 5       y 11 .. 25      z -3 .. 3
    leggings shell (+0.5)   x -4.5 .. 4.5   y 11.5 .. 24.5  z -2.5 .. 2.5
    the `back` anchor       (0, 22, 2)

Front is **negative z**. This socket is not mirrored: build the whole piece once.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(0, 22, 2)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

A legionary's scutum carried on the back: a tall red board covering the back from the waist to the shoulders, two side panels set a little closer to the body so the shield reads as curved, a bronze spine running down the middle and a bronze boss at its centre. Red, with the wings of the legion painted in gold on the board.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **board** — the main board:

        x -4.43 .. 4.43    y 10.07 .. 24.43    z 3.89 .. 4.47

- **wing_l** — the left side panel, set closer to the body:

        x -6.05 .. -4.43    y 10.57 .. 23.93    z 3.38 .. 3.97

- **wing_r** — the right side panel:

        x 4.43 .. 6.03    y 10.57 .. 23.93    z 3.38 .. 3.97

- **spine** — the bronze spine down the middle:

        x -0.57 .. 0.53    y 10.07 .. 24.43    z 4.47 .. 4.77

- **boss** — the bronze boss at the centre:

        x -1.33 .. 1.33    y 15.87 .. 18.65    z 4.42 .. 5.47

**5 cubes in total is the budget**, and there is no 6th.

**Envelope budget.** Stay inside `x -6.1 .. 6.1, y 10.0 .. 24.5, z 3.3 .. 5.6`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the body bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -6.1 .. 6.1      y  -0.5 .. 14.0      z  3.3 .. 5.6

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `turtle_shell` | x -6.00..6.00, y 15.75..24.90, z 3.10..5.60 | the Animals' shell - a broad thing on the back at your width |
| `cloak` | x -5.45..5.45, y 9.63..24.85, z 2.90..4.63 | the mod's cloak - your height band exactly |
| `pouch_belt (belt)` | x -7.10..6.55, y 11.05..13.60, z -3.40..5.00 | worn WITH you; its back pouches reach z 5.00 and cross your board in a hull test - an OVERLAP `-`, not a `!` |
| `phalerae (collar)` | x -4.10..4.10, y 17.40..23.50, z -4.00..-3.00 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `cingulum (belt)` | x -5.40..5.40, y 8.30..14.50, z -3.90..3.40 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

board and wings: base **110**, `south` **130** (the back face is the one you see), and if the tool lets you a `pixels` block of 200 on the board's `south` face either side of the spine, for the gold wings. spine and boss: base **145**, `south` **185**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `board`, `wing_l`, `wing_r`: base `#8e2a24`, `up` `#ad3a32` — red leather - the legion's own dyed leather, and `down` #6e1f1a, its shadow

**Mask `part_guard`** — flat **140**, on `spine`, `boss`. 140 is the value every mask in this project
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

