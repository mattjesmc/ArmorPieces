# Brief: Tilting Grille

A piece of **Armor Pieces: Tournament** (`armorpieces_tourney`) — bright steel and heraldry - azure and gold, the joust and the lists, a lady's favour on the arm; the hardware answers the trim and the colours are its own.

From the `brow` row of the Tournament table:

> `tilting_grille` - a barred visor of four horizontal steel bars between two posts - fitting `guard` - centre `iron_trapdoor`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          tilting_grille
    anchor:        brow
    namespace:     armorpieces_tourney
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\tourney\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\tourney\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Tilting Grille",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:iron_trapdoor", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Heraldic or is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `tilt` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:iron_trapdoor` is confirmed free against every
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

Everything here is masked `guard` and answers the trim until a player fills the fitting; the **top bar** alone is static gold by default under its mask, the gilt brow-band of a tournament helm.

## The rig, in Blockbench coordinates

    head box                x -4 .. 4       y 24 .. 32      z -4 .. 4
    helmet shell (+1)       x -5 .. 5       y 23 .. 33      z -5 .. 5
    the `brow` anchor       (0, 28, -4)

Front is **negative z**. This socket is not mirrored: build the whole piece once.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(0, 28, -4)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

A tournament grille: two vertical steel posts at the sides of the face and four horizontal bars running between them, evenly spaced from the brow to the chin. You look out between the bars. It is a cage for the face, all steel, and it takes the trim.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **post_l** — the left post:

        x -4.13 .. -3.50    y 25.57 .. 30.01    z -5.63 .. -5.13

- **post_r** — the right post:

        x 3.50 .. 4.13    y 25.57 .. 30.01    z -5.63 .. -5.13

- **bar_a** — the top bar, at the brow:

        x -3.50 .. 3.50    y 29.43 .. 30.01    z -5.73 .. -5.13

- **bar_b** — the second bar, at the eyes:

        x -3.50 .. 3.50    y 28.13 .. 28.71    z -5.73 .. -5.13

- **bar_c** — the third bar:

        x -3.50 .. 3.50    y 26.83 .. 27.42    z -5.73 .. -5.13

- **bar_d** — the bottom bar, at the chin:

        x -3.50 .. 3.50    y 25.57 .. 26.13    z -5.73 .. -5.13

**6 cubes in total is the budget**, and there is no 7th.

**Envelope budget.** Stay inside `x -4.2 .. 4.2, y 25.5 .. 30.1, z -5.8 .. -5.0`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the head bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -4.2 .. 4.2      y  -6.1 .. -1.5      z  -5.8 .. -5.0

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `coral_visor` | x -4.13..4.13, y 25.93..30.07, z -5.83..-5.07 | the Coral's barred visor - the same grille idea in coral; yours is all steel |
| `frog_mouth` | x -4.00..4.00, y 24.00..31.00, z -5.60..-5.10 | the mod's own jousting helm face - the piece yours sits beside in the picker |
| `sallet_slit` | x -4.00..4.00, y 26.00..31.00, z -5.60..-5.10 | a mod visor at your depth |
| `lion_crest (crest)` | x -2.10..2.10, y 33.00..37.60, z -3.10..2.60 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `mantling (horns)` | x -5.90..-5.00, y 25.50..31.90, z -0.70..7.90 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

posts and bars: base **150**, `north` **185**, `up` **195**, `down` **110**. top bar: base **175**, `north` **210**.

**Cut nothing.** The gaps between the bars are the eye slots; every face above gets paint.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `bar_a`: base `#e0b13a`, `up` `#f3cb5c` — heraldic or - the gold of the arms

**Mask `part_guard`** — flat **140**, on `post_l`, `post_r`, `bar_a`, `bar_b`, `bar_c`, `bar_d`. 140 is the value every mask in this project
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

