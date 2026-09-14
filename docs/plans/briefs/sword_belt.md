# Brief: Sword Belt

A piece of **Armor Pieces: Tournament** (`armorpieces_tourney`) — bright steel and heraldry - azure and gold, the joust and the lists, a lady's favour on the arm; the hardware answers the trim and the colours are its own.

From the `belt` row of the Tournament table:

> `sword_belt` - a leather belt with a sheathed longsword hanging straight down at the left hip - fitting `guard` - centre `wooden_sword`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          sword_belt
    anchor:        belt
    namespace:     armorpieces_tourney
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\tourney\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\tourney\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Sword Belt",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:wooden_sword", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Oiled leather is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `tilt` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:wooden_sword` is confirmed free against every
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

The **cross** and **pommel** carry no static. They are masked `guard` and are the piece's material surface; the belt, scabbard and grip are static.

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

A knight's sword belt: a leather belt round the waist and, at the LEFT hip, a longsword in its azure scabbard hanging straight down beside the thigh, with the cross-guard lying on the belt line, the wrapped grip standing up above it and a round pommel on top. This socket is not mirrored, so the sword is on one side only.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **belt** — the leather belt round the waist:

        x -5.33 .. 5.33    y 12.77 .. 14.33    z -3.33 .. 3.33

- **scabbard** — the scabbard hanging down beside the left thigh:

        x -6.23 .. -5.33    y 5.27 .. 12.77    z -0.83 .. 0.37

- **cross** — the cross-guard, lying across the belt line:

        x -6.03 .. -5.52    y 14.33 .. 14.87    z -2.03 .. 1.57

- **grip** — the wrapped grip above the cross:

        x -6.13 .. -5.41    y 14.87 .. 16.87    z -0.73 .. 0.27

- **pommel** — the round pommel on top:

        x -6.23 .. -5.33    y 16.87 .. 17.67    z -0.83 .. 0.37

**5 cubes in total is the budget**, and there is no 6th.

**Envelope budget.** Stay inside `x -6.3 .. 5.4, y 5.2 .. 17.8, z -3.4 .. 3.4`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the body bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -5.4 .. 6.3      y  6.2 .. 18.8      z  -3.4 .. 3.4

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `thigh_sheath (tassets)` | x -5.35..0.85, y 3.53..11.94, z -2.80..2.80 | the mod's dagger at the thigh - on the LEG bone, so the check never compares you; the precedent for a weapon at the hip |
| `sash` | x -7.25..6.00, y 5.27..16.50, z -5.00..4.00 | the mod's sash - the precedent for a belt piece reaching x -7 and y 5 |
| `gorget (collar)` | x -6.50..6.50, y 19.50..25.25, z -3.75..0.75 | worn WITH you, its bottom at y 19.50 - your pommel ends at 17.67, clear |
| `ecranche (back)` | x -4.40..4.40, y 13.50..23.80, z 3.00..4.20 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `lance_rest (collar)` | x 1.00..4.10, y 19.50..21.90, z -5.20..-3.00 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

belt: base **90**, `up` **110**. scabbard: base **120**, `west` **140**. grip: base **60**. cross and pommel: base **150**, `up` **190**.

**The belt is one cube right round the body.** Its inner volume is inside the chestplate; its six faces are the belt.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `belt`: base `#5a3d28`, `up` `#75523a` — oiled leather
- `scabbard`: base `#2244aa`, `up` `#3560c8` — heraldic azure - the field of the arms
- `grip`: base `#3b2a1c`, `up` `#4f3a28` — dark leather - the wrapped grip

**Mask `part_guard`** — flat **140**, on `cross`, `pommel`. 140 is the value every mask in this project
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

