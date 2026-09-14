# Brief: Mantling

A piece of **Armor Pieces: Tournament** (`armorpieces_tourney`) — bright steel and heraldry - azure and gold, the joust and the lists, a lady's favour on the arm; the hardware answers the trim and the colours are its own.

From the `horns` row of the Tournament table:

> `mantling` - a cloth lambrequin at each temple flowing back and down behind the head - fitting `inlay` - centre `blue_dye`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          mantling
    anchor:        horns
    namespace:     armorpieces_tourney
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\tourney\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\tourney\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Mantling",
                           fittings: ["armorpieces:inlay"],
                           static: true,
                           recipe: { centre: "minecraft:blue_dye", craftable: true } }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Heraldic azure is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `tilt` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:blue_dye` is confirmed free against every
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

Nothing here is bare material: the cloth is static azure by default AND masked `inlay`, so a player re-dyes the whole mantling. Paint the `down` faces gold on the static sheet (`#e0b13a`) for the lining.

## The rig, in Blockbench coordinates

    head box                x -4 .. 4       y 24 .. 32      z -4 .. 4
    helmet shell (+1)       x -5 .. 5       y 23 .. 33      z -5 .. 5
    the `horns` anchor       (-4, 29, 0)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-4, 29, 0)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

The mantling of a heraldic helm: a piece of azure cloth fixed at each temple, swagging back over the side of the helmet, trailing down behind the head and ending in a hanging tip. Four cubes stepping back and down make the flow; no rotation. Azure outside, gold lining underneath.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **root** — the cloth fixed at the temple:

        x -5.68 .. -5.07    y 29.37 .. 31.83    z -0.63 .. 1.37

- **swag** — the swag flowing back over the side of the helm:

        x -5.77 .. -5.07    y 28.07 .. 30.57    z 1.37 .. 4.37

- **trail** — the trail hanging down behind the head:

        x -5.68 .. -5.13    y 26.69 .. 29.07    z 4.37 .. 6.57

- **tip** — the hanging tip:

        x -5.57 .. -5.23    y 25.55 .. 27.27    z 6.57 .. 7.77

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -5.9 .. -5.0, y 25.5 .. 31.9, z -0.7 .. 7.9`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the head bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  5.0 .. 5.9      y  -7.9 .. -1.5      z  -0.7 .. 7.9

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `5.77`, so the pair spans **11.54** — the check compares that against the **18** the shoulders span, and you are inside it. Report the span.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `helm_wings` | x -6.40..-5.30, y 31.14..38.37, z -0.74..6.58 | the mod's wings - on the same back half of the temple, going UP where you go back and down |
| `head_fins` | x -8.75..-4.66, y 26.31..31.87, z -1.40..7.71 | the Coral's fins - the precedent for trailing to z 7.7 behind the head on this socket |
| `browband (brow)` | x -6.48..5.50, y 26.60..30.10, z -5.45..5.45 | worn WITH you; its box crosses your root and swag in a hull test - an OVERLAP `-`, not a `!` |
| `lion_crest (crest)` | x -2.10..2.10, y 33.00..37.60, z -3.10..2.60 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `tilting_grille (brow)` | x -4.20..4.20, y 25.50..30.10, z -5.80..-5.00 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

all four cubes: base **120**, `west` **140** (the outboard face), `down` **170** (the lining is the light one).

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `root`, `swag`, `trail`, `tip`: base `#2244aa`, `up` `#3560c8` — heraldic azure - the field of the arms

**Mask `part_inlay`** — flat **140**, on `root`, `swag`, `trail`, `tip`. 140 is the value every mask in this project
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

