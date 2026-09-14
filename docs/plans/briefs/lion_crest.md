# Brief: Lion Crest

A piece of **Armor Pieces: Tournament** (`armorpieces_tourney`) — bright steel and heraldry - azure and gold, the joust and the lists, a lady's favour on the arm; the hardware answers the trim and the colours are its own.

From the `crest` row of the Tournament table:

> `lion_crest` - a gold lion standing on a twisted azure-and-gold wreath on the crown - fitting `inlay` - centre `yellow_dye`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          lion_crest
    anchor:        crest
    namespace:     armorpieces_tourney
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\tourney\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\tourney\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Lion Crest",
                           fittings: ["armorpieces:inlay"],
                           static: true,
                           recipe: { centre: "minecraft:yellow_dye", craftable: true } }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Heraldic azure is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `tilt` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:yellow_dye` is confirmed free against every
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

Nothing here is bare material: the **torse** is static azure by default AND masked `inlay`, so a player re-dyes the wreath, and the lion is static gold. That is allowed because the fitting is there to change.

## The rig, in Blockbench coordinates

    head box                x -4 .. 4       y 24 .. 32      z -4 .. 4
    helmet shell (+1)       x -5 .. 5       y 23 .. 33      z -5 .. 5
    the `crest` anchor       (0, 32, 0)

Front is **negative z**. This socket is not mirrored: build the whole piece once.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(0, 32, 0)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

A heraldic crest: a twisted wreath (the torse) lying on the crown, and on it a golden lion standing up on its hind legs facing forward - a body, a head thrust forward, a forepaw raised in front, and a tail curling up behind. Blocky and gold; the wreath is azure and a player can re-dye it.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **torse** — the twisted wreath on the crown:

        x -2.03 .. 2.03    y 33.07 .. 33.83    z -2.03 .. 2.03

- **body** — the lion's body, standing on the wreath:

        x -0.93 .. 0.93    y 33.83 .. 36.03    z -1.63 .. 1.75

- **head** — the head, thrust forward:

        x -0.83 .. 0.83    y 36.03 .. 37.53    z -2.37 .. -0.81

- **paw** — the raised forepaw in front:

        x -0.63 .. 0.63    y 35.33 .. 36.43    z -2.97 .. -1.63

- **tail** — the tail curling up behind:

        x -0.33 .. 0.33    y 34.62 .. 37.03    z 1.75 .. 2.47

**5 cubes in total is the budget**, and there is no 6th.

**Envelope budget.** Stay inside `x -2.1 .. 2.1, y 33.0 .. 37.6, z -3.1 .. 2.6`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the head bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.1 .. 2.1      y  -13.6 .. -9.0      z  -3.1 .. 2.6

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `spire` | x -2.50..2.50, y 32.50..40.00, z -2.50..2.50 | the mod's spire - a crest at your wreath's width, going higher |
| `boar_crest` | x -1.20..1.20, y 33.00..36.20, z -4.00..3.70 | the Norse boar, built in this batch - a figure on the crown like yours, never worn with you |
| `coronet (brow)` | x -6.00..6.00, y 29.00..33.21, z -6.18..-2.25 | a brow piece rising to y 33.21 at the front; your wreath's front edge crosses its box in a hull test - an OVERLAP `-`, never a `!` |
| `tilting_grille (brow)` | x -4.20..4.20, y 25.50..30.10, z -5.80..-5.00 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `mantling (horns)` | x -5.90..-5.00, y 25.50..31.90, z -0.70..7.90 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

torse: base **130**, `up` **160**, and alternate `pixels` of 130 / 200 round its sides if the tool lets you, for the twist. lion (body, head, paw, tail): base **170**, `up` **205**, `north` **190**, `down` **135**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `torse`: base `#2244aa`, `up` `#3560c8` — heraldic azure - the field of the arms
- `body`, `head`, `paw`, `tail`: base `#e0b13a`, `up` `#f3cb5c` — heraldic or - the gold of the arms

**Mask `part_inlay`** — flat **140**, on `torse`. 140 is the value every mask in this project
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

