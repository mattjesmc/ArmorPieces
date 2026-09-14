# Brief: Ecranche

A piece of **Armor Pieces: Tournament** (`armorpieces_tourney`) — bright steel and heraldry - azure and gold, the joust and the lists, a lady's favour on the arm; the hardware answers the trim and the colours are its own.

From the `back` row of the Tournament table:

> `ecranche` - a small azure jousting shield with the lance notch cut from its top corner, slung on the back - fitting `inlay` - centre `blue_banner`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          ecranche
    anchor:        back
    namespace:     armorpieces_tourney
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\tourney\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\tourney\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Ecranche",
                           fittings: ["armorpieces:inlay"],
                           static: true,
                           recipe: { centre: "minecraft:blue_banner", craftable: true } }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Heraldic azure is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `tilt` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:blue_banner` is confirmed free against every
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

Nothing here is bare material: the **board** is static azure by default AND masked `inlay`, so a player re-dyes the field; the guige is static leather. Paint a gold bend on the board's `south` face on the static sheet if the tool lets you (`#e0b13a`).

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

The jouster's little shield carried on the back: an azure board on the upper back, its top-right corner missing where the lance notch (the bouche) is cut, so the top edge is one shorter cube on the left only, and a leather guige strap across the shoulders above it. Azure by default; a player re-dyes the field.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **board** — the main board:

        x -3.93 .. 3.93    y 13.57 .. 21.45    z 3.47 .. 4.07

- **upper** — the top of the board, left side only - the notch is the missing right side:

        x -3.93 .. -0.57    y 21.45 .. 23.03    z 3.47 .. 4.07

- **guige** — the leather guige strap across the shoulders:

        x -4.29 .. 4.33    y 23.03 .. 23.73    z 3.07 .. 3.57

**3 cubes in total is the budget**, and there is no 4th.

**Envelope budget.** Stay inside `x -4.4 .. 4.4, y 13.5 .. 23.8, z 3.0 .. 4.2`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the body bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -4.4 .. 4.4      y  0.2 .. 10.5      z  3.0 .. 4.2

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `banner` | x -3.50..3.50, y 8.50..21.50, z 1.75..6.25 | the mod's banner - a flat thing on the back at your width, hanging lower |
| `carapace` | x -4.75..4.75, y 15.60..24.60, z 3.10..5.25 | the Hive's back plate - your height band |
| `pouch_belt (belt)` | x -7.10..6.55, y 11.05..13.60, z -3.40..5.00 | worn WITH you; its back pouches reach z 5.00 and y 13.60, crossing your board's bottom in a hull test - an OVERLAP `-`, not a `!` |
| `lance_rest (collar)` | x 1.00..4.10, y 19.50..21.90, z -5.20..-3.00 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `sword_belt (belt)` | x -6.30..5.40, y 5.20..17.80, z -3.40..3.40 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

board and upper: base **130**, `south` **150** (the back face is the one you see). guige: base **90**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `board`, `upper`: base `#2244aa`, `up` `#3560c8` — heraldic azure - the field of the arms
- `guige`: base `#5a3d28`, `up` `#75523a` — oiled leather

**Mask `part_inlay`** — flat **140**, on `board`, `upper`. 140 is the value every mask in this project
uses.

## Done when

- [ ] The check is clean, or every `!` left standing is one this brief allows.
- [ ] Envelope inside the budget above, **reported in the check's frame**.
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

