# Brief: Pillager Belt

A piece of **Armor Pieces: Hero of the Village** (`armorpieces_village`) — iron armor with emerald hardware, the
raid worn by the person who won it.

From the `belt` row of the Hero of the Village table:

> `pillager_belt` - the crossbow belt with its quarrel loops - fitting `guard` - centre `crossbow`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          pillager_belt
    anchor:        belt
    namespace:     armorpieces_village
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\village\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\village\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Pillager Belt",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:crossbow", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Belt leather - dark, worn is a colour that must not change with the armor.
**Effects: none. Loot: none — leave `loot` out of your call entirely.** The recipe above is the only way this piece is had; `minecraft:crossbow` is confirmed free against every template centre in the project.

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

The **buckle** and both **loops** carry no static. They are masked `guard` and are the piece's material surface until a player fills the fitting.

## The rig, in Blockbench coordinates

    body box                x -4 .. 4     y 12 .. 24    z -2 .. 2
    chestplate shell (+1)   x -5 .. 5     y 11 .. 25    z -3 .. 3
    the `belt` anchor       (0, 14, 0)

Front is **negative z**. This socket is not mirrored: build the whole piece once.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(0, 14, 0)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** `ominous_banner` found this out on 2026-09-10: a
`back` piece gets no `past helmet` line at all, because the helmet is not its shell. So the check
will **not** warn you about running into a shell that belongs to a different armor piece. Every
coordinate below already clears the ones that matter; do not move them toward another shell.

## Shape

A pillager's working belt: a plain leather band, a square buckle, and two loops at the hip holding crossbow bolts. The loops are what makes it a pillager's rather than anyone's belt, so they must be visible from the front.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **band** — the leather belt itself, right round the waist:

        x -5.35 .. 5.35    y 13.15 .. 15.05    z -3.85 .. 3.85

- **buckle** — the square buckle at the front:

        x -1.45 .. 1.45    y 12.85 .. 15.35    z -4.35 .. -3.55

- **loop_a** — the inner quarrel loop:

        x 2.15 .. 3.05    y 12.05 .. 13.35    z -4.15 .. -3.45

- **loop_b** — the outer quarrel loop:

        x 3.55 .. 4.45    y 12.05 .. 13.35    z -4.15 .. -3.45

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -5.4 .. 5.4, y 12.0 .. 15.4, z -4.4 .. 3.9`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the body bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -5.4 .. 5.4      y  8.6 .. 12.0      z  -4.4 .. 3.9

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `buckled_belt` | x -5.50..5.50, y 12.50..15.50, z -4.50..3.50 | the piece yours is closest to - stay inside its width |
| `girdle` | x -5.86..5.86, y 11.75..14.25, z -4.00..3.86 | the widest belt |
| `pouch_belt` | x -7.10..6.55, y 11.05..13.60, z -3.40..5.00 | the precedent for something hanging off the belt line |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

band: base **105**, `up` **130**, `down` **80**. buckle and loops: base **165**, `up` **200**, so the hardware reads bright against dark leather.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `band`: base `#5a4130`, `up` `#75563f` — belt leather - dark, worn

**Mask `part_guard`** — flat **140**, on `buckle`, `loop_a`, `loop_b`. 140 is the value every mask in this project
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
