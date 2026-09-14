# Brief: Cingulum

A piece of **Armor Pieces: Antiquity** (`armorpieces_antiquity`) — bronze and red leather - Greece and Rome, the hoplite and the legionary, every piece a thing with a Latin or Greek name.

From the `belt` row of the Antiquity table:

> `cingulum` - a plated military belt with a bronze buckle and four studded straps hanging at the front - fitting `guard` - centre `copper_nugget`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          cingulum
    anchor:        belt
    namespace:     armorpieces_antiquity
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\antiquity\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\antiquity\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Cingulum",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:copper_nugget", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Red leather is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `legion` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:copper_nugget` is confirmed free against every
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

The **buckle** carries no static. It is masked `guard` and is the piece's whole material surface; the belt and straps are static leather (the belt's bronze plates are painted on its master as light squares, but the colour underneath is leather).

## The rig, in Blockbench coordinates

    body box                x -4 .. 4       y 12 .. 24      z -2 .. 2
    chestplate shell (+1)   x -5 .. 5       y 11 .. 25      z -3 .. 3
    leggings shell (+0.5)   x -4.5 .. 4.5   y 11.5 .. 24.5  z -2.5 .. 2.5
    the `belt` anchor       (0, 14, 0)

Front is **negative z**. This socket is not mirrored: build the whole piece once.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(0, 14, 0)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

The soldier's belt: a leather belt round the waist faced with bronze plates, a bronze buckle at the front, and hanging from it the apron - four narrow leather straps with bronze studs down their length and a weight at each end, swinging in front of the groin. The apron is what makes it a cingulum.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **belt** — the plated belt round the waist:

        x -5.33 .. 5.33    y 12.97 .. 14.23    z -3.33 .. 3.33

- **buckle** — the bronze buckle at the front:

        x -0.93 .. 0.93    y 13.07 .. 14.43    z -3.73 .. -3.33

- **strap_a** — the outer-left apron strap:

        x -2.93 .. -2.27    y 8.67 .. 12.97    z -3.83 .. -3.33

- **strap_b** — the inner-left strap, a little longer:

        x -1.31 .. -0.67    y 8.37 .. 12.97    z -3.83 .. -3.33

- **strap_c** — the inner-right strap:

        x 0.65 .. 1.35    y 8.37 .. 12.97    z -3.83 .. -3.33

- **strap_d** — the outer-right strap:

        x 2.27 .. 2.93    y 8.67 .. 12.97    z -3.83 .. -3.33

**6 cubes in total is the budget**, and there is no 7th.

**Envelope budget.** Stay inside `x -5.4 .. 5.4, y 8.3 .. 14.5, z -3.9 .. 3.4`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the body bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -5.4 .. 5.4      y  9.5 .. 15.7      z  -3.9 .. 3.4

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `fauld` | x -5.35..5.35, y 9.40..13.50, z -4.02..4.02 | the mod's fauld - the precedent for plates hanging below the belt line |
| `chain_belt` | x -5.50..5.50, y 8.60..12.80, z -3.80..3.50 | the court's chain belt, hanging to y 8.60 like your apron |
| `scutum (back)` | x -6.10..6.10, y 10.00..24.50, z 3.30..5.60 | your own pack's shield, built in this batch; its side panels start at z 3.37 and your belt ends at 3.33 - clear |
| `phalerae (collar)` | x -4.10..4.10, y 17.40..23.50, z -4.00..-3.00 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

belt: base **100**, `north` **120**, and alternate `pixels` of 100 / 200 along the `north` face if the tool lets you, for the bronze plates. straps: base **95**, `north` **115**, `down` **200** (the weight at the end). buckle: base **150**, `north` **190**.

**The belt is one cube right round the body.** Its inner volume is inside the chestplate; its six faces are the belt.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `belt`, `strap_a`, `strap_b`, `strap_c`, `strap_d`: base `#8e2a24`, `up` `#ad3a32` — red leather - the legion's own dyed leather, and `down` #6e1f1a, its shadow

**Mask `part_guard`** — flat **140**, on `buckle`. 140 is the value every mask in this project
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

