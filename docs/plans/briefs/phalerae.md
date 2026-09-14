# Brief: Phalerae

A piece of **Armor Pieces: Antiquity** (`armorpieces_antiquity`) — bronze and red leather - Greece and Rome, the hoplite and the legionary, every piece a thing with a Latin or Greek name.

From the `collar` row of the Antiquity table:

> `phalerae` - a leather harness on the chest hung with three bronze discs - fitting `guard` - centre `golden_apple`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          phalerae
    anchor:        collar
    namespace:     armorpieces_antiquity
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\antiquity\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\antiquity\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Phalerae",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:golden_apple", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Dark leather is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `legion` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:golden_apple` is confirmed free against every
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

The three **discs** carry no static. They are masked `guard` and are the piece's whole material surface; the straps are static leather.

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

A decorated soldier's phalerae: a leather harness of one horizontal and two vertical straps on the upper chest, and three bronze discs on it - a big one at the centre, a smaller one at each side lower down. The discs stand proud of the straps. Medals, worn as armor.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **strap_h** — the horizontal strap across the chest:

        x -4.03 .. 4.03    y 20.97 .. 21.63    z -3.62 .. -3.07

- **strap_l** — the left vertical strap:

        x -3.37 .. -2.63    y 17.47 .. 23.45    z -3.57 .. -3.16

- **strap_r** — the right vertical strap:

        x 2.63 .. 3.37    y 17.47 .. 23.45    z -3.57 .. -3.16

- **disc_c** — the big central disc:

        x -1.37 .. 1.37    y 20.07 .. 22.53    z -3.93 .. -3.57

- **disc_l** — the left disc, lower:

        x -3.89 .. -2.13    y 18.37 .. 19.83    z -3.90 .. -3.57

- **disc_r** — the right disc:

        x 2.13 .. 3.89    y 18.37 .. 19.83    z -3.90 .. -3.57

**6 cubes in total is the budget**, and there is no 7th.

**Envelope budget.** Stay inside `x -4.1 .. 4.1, y 17.4 .. 23.5, z -4.0 .. -3.0`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the body bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -4.1 .. 4.1      y  0.5 .. 6.6      z  -4.0 .. -3.0

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `chain_of_office` | x -4.22..4.22, y 16.80..23.44, z -4.60..-2.60 | the mod's chain of office - the same idea, a harness with things hung on it |
| `bandolier` | x -5.47..5.47, y 15.66..25.20, z -3.65..-2.35 | the wayfarer's bandolier - straps on the chest at your depth |
| `scutum (back)` | x -6.10..6.10, y 10.00..24.50, z 3.30..5.60 | your own pack's shield, built in this batch, all BEHIND the body where you are all in front |
| `cingulum (belt)` | x -5.40..5.40, y 8.30..14.50, z -3.90..3.40 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

straps: base **70**, `north` **85**. discs: base **150**, `north` **195** (the face of a medal), `up` **175**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `strap_h`, `strap_l`, `strap_r`: base `#4a2f1e`, `up` `#5f3f2a` — dark leather - the straps

**Mask `part_guard`** — flat **140**, on `disc_c`, `disc_l`, `disc_r`. 140 is the value every mask in this project
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

