# Brief: Lance Rest

A piece of **Armor Pieces: Tournament** (`armorpieces_tourney`) — bright steel and heraldry - azure and gold, the joust and the lists, a lady's favour on the arm; the hardware answers the trim and the colours are its own.

From the `collar` row of the Tournament table:

> `lance_rest` - a steel bracket on the right breast with a hook and lip projecting forward - fitting `guard` - centre `tripwire_hook`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          lance_rest
    anchor:        collar
    namespace:     armorpieces_tourney
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\tourney\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\tourney\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Lance Rest",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:tripwire_hook", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Heraldic or is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `tilt` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:tripwire_hook` is confirmed free against every
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

The **plate**, **hook** and **lip** carry no static. They are masked `guard` and are the piece's material surface; the bolt is static gold.

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

The arret: a small steel plate bolted to the RIGHT side of the upper chest, a hook projecting straight forward from it and an upturned lip at the hook's end, with a gilt bolt head on the plate. It is on one side only - the right, the lance side - and this socket is not mirrored, so build it there.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **plate** — the mount plate on the right breast:

        x 1.07 .. 4.03    y 19.59 .. 21.83    z -3.57 .. -3.07

- **hook** — the hook projecting forward:

        x 2.37 .. 3.95    y 19.87 .. 20.63    z -5.13 .. -3.57

- **lip** — the upturned lip at the end of the hook:

        x 2.37 .. 3.95    y 20.63 .. 21.53    z -5.13 .. -4.53

- **bolt** — the gilt bolt head on the plate:

        x 1.37 .. 1.97    y 20.27 .. 20.87    z -3.70 .. -3.57

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x 1.0 .. 4.1, y 19.5 .. 21.9, z -5.2 .. -3.0`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the body bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -4.1 .. -1.0      y  2.1 .. 4.5      z  -5.2 .. -3.0

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `brooch` | x -3.50..-0.50, y 16.56..19.50, z -4.75..-1.00 | the mod's brooch - a thing on ONE side of the chest, the left; you are its opposite |
| `flower_brooch` | x -4.74..0.74, y 17.02..23.33, z -5.04..-3.15 | the Animals' brooch, also on the left, reaching as far forward as your lip |
| `bandolier` | x -5.47..5.47, y 15.66..25.20, z -3.65..-2.35 | the wayfarer's strap at your depth |
| `ecranche (back)` | x -4.40..4.40, y 13.50..23.80, z 3.00..4.20 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `sword_belt (belt)` | x -6.30..5.40, y 5.20..17.80, z -3.40..3.40 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

plate: base **150**, `north` **180**. hook and lip: base **145**, `up` **185**, `north` **175**. bolt: base **180**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `bolt`: base `#e0b13a`, `up` `#f3cb5c` — heraldic or - the gold of the arms

**Mask `part_guard`** — flat **140**, on `plate`, `hook`, `lip`. 140 is the value every mask in this project
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

