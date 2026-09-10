# Brief: Illager Mask

A piece of **Armor Pieces: Hero of the Village** (`armorpieces_village`) — iron armor with emerald hardware, the
raid worn by the person who won it.

From the `brow` row of the Hero of the Village table:

> `illager_mask` - the long grey nose and heavy brow - fitting `inlay` - found in a chest

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          illager_mask
    anchor:        brow
    namespace:     armorpieces_village
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\village\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\village\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Illager Mask",
                           fittings: ["armorpieces:inlay"],
                           static: true }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Illager skin - cold grey, faintly blue is a colour that must not change with the armor.
**Effects: none. Loot: none — leave `loot` out of your call entirely.** This piece is found in a chest rather than crafted, but the pack's loot group does not exist yet and a session must not invent one — I add it afterwards in the repo half. **Do not add a recipe either.**

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

The **brow** ridge carries no static and no mask: it reads as the mask's own hard edge and it is what answers the trim.

## The rig, in Blockbench coordinates

    head box                x -4 .. 4     y 24 .. 32    z -4 .. 4
    helmet shell (+1)       x -5 .. 5     y 23 .. 33    z -5 .. 5
    the `brow` anchor       (0, 28, -4)

Front is **negative z**. This socket is not mirrored: build the whole piece once.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(0, 28, -4)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** `ominous_banner` found this out on 2026-09-10: a
`back` piece gets no `past helmet` line at all, because the helmet is not its shell. So the check
will **not** warn you about running into a shell that belongs to a different armor piece. Every
coordinate below already clears the ones that matter; do not move them toward another shell.

## Shape

A pillager's face worn as a mask: a heavy flat brow, a long straight nose, and a hood band holding it on. The nose is the joke and it should be unmistakably too long.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **face** — the flat faceplate over your own face:

        x -4.10 .. 4.10    y 25.15 .. 30.15    z -5.85 .. -5.15

- **brow** — the heavy ridge above the eyes, standing proud of the face:

        x -4.10 .. 4.10    y 29.35 .. 30.45    z -6.35 .. -5.85

- **nose** — the long illager nose:

        x -0.95 .. 0.95    y 26.15 .. 29.45    z -7.35 .. -5.85

- **hood** — the band running back round the head:

        x -4.55 .. 4.55    y 29.65 .. 30.85    z -5.55 .. 4.55

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -4.6 .. 4.6, y 25.1 .. 30.9, z -7.4 .. 4.6`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the head bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -4.6 .. 4.6      y  -6.9 .. -1.1      z  -7.4 .. 4.6

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `wither_mask` | x -4.10..4.10, y 25.10..31.30, z -6.45..-5.15 | the same height band; you sit 0.9 deeper at the nose |
| `frog_mask` | x -5.50..5.50, y 25.25..31.75, z -7.25..-5.25 | reaches z -7.25; your nose at -7.35 is 0.1 past it and that is fine |
| `browband` | x -6.48..5.50, y 26.60..30.10, z -5.45..5.45 | the precedent for a band running right round the head |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

face and nose: base **120**, nose `west`/`east` **100** so it reads as a ridge rather than a slab. brow: base **150**, `up` **185**, `down` **95**. hood: base **110**.

**Cut nothing.** This mask has no eye slot - the brow's shadow does that work. A face with no paint behind it renders as a hole, so every face above gets paint.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `face`, `nose`: base `#8b9497`, `up` `#a3acb0` — illager skin - cold grey, faintly blue

**Mask `part_inlay`** — flat **140**, on `hood`. 140 is the value every mask in this project
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
