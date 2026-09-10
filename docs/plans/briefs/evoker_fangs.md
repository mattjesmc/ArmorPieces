# Brief: Evoker Fangs

A piece of **Armor Pieces: Hero of the Village** (`armorpieces_village`) — iron armor with emerald hardware, the
raid worn by the person who won it.

From the `knees` row of the Hero of the Village table:

> `evoker_fangs` - fangs erupting from under each kneecap - fitting `guard` - centre `ominous_bottle`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          evoker_fangs
    anchor:        knees
    namespace:     armorpieces_village
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\village\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\village\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Evoker Fangs",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:ominous_bottle", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Fang bone - pale, almost white is a colour that must not change with the armor.
**Effects: none. Loot: none — leave `loot` out of your call entirely.** The recipe above is the only way this piece is had; `minecraft:ominous_bottle` is confirmed free against every template centre in the project.

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

The **cop** carries no static. It is masked `guard` and answers the trim until a player fills the fitting.

## The rig, in Blockbench coordinates

    left leg box            x -4 .. 0     y 0 .. 12     z -2 .. 2
    leggings shell (+1)     x -5 .. 1     y -1 .. 13    z -3 .. 3
    the `knees` anchor       (-1.9, 6, -2)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-1.9, 6, -2)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** `ominous_banner` found this out on 2026-09-10: a
`back` piece gets no `past helmet` line at all, because the helmet is not its shell. So the check
will **not** warn you about running into a shell that belongs to a different armor piece. Every
coordinate below already clears the ones that matter; do not move them toward another shell.

## Shape

An evoker's fang attack caught mid-summon: a plain knee cop with three bone fangs bursting upward out of its top edge. The fangs must clearly come OUT of the cop, not sit on it.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **cop** — the knee cop the fangs erupt from:

        x -3.65 .. -0.15    y 4.15 .. 7.45    z -3.95 .. -2.95

- **fang_a** — the outer fang, shortest:

        x -3.15 .. -2.35    y 7.35 .. 9.05    z -3.75 .. -3.05

- **fang_b** — the middle fang, tallest:

        x -2.15 .. -1.45    y 7.35 .. 9.25    z -3.75 .. -3.05

- **fang_c** — the inner fang:

        x -1.25 .. -0.55    y 7.35 .. 8.75    z -3.75 .. -3.05

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -3.7 .. -0.1, y 4.1 .. 9.3, z -4.0 .. -2.9`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -1.8 .. 1.8      y  2.7 .. 7.9      z  -4.0 .. -2.9

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `3.65`, so the pair spans **7.3**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `magma_cops` | x -3.55..-0.25, y 3.72..7.65, z -4.05..-2.58 | a pack knee at your exact width and depth |
| `fanged_cop` | x -3.50..-0.30, y 3.93..7.40, z -3.95..-3.20 | the piece yours must not be mistaken for - its fangs point DOWN |
| `poleyns` | x -4.55..-1.55, y 4.90..8.30, z -4.65..-2.65 | the deepest knee piece |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

fangs: base **200**, `up` **230** at the points, `down` **150**. cop: base **140**, `up` **175**, `down` **95**.

**Expect an OVERLAP note against the tassets pieces.** Your fangs rise to `y 9.25`, which is inside the range every tassets piece occupies (`y 5.2 .. 12.5`). That is a hull test on a crowded bone, it is a `-` and not a `!`, and you should leave it standing and say so in your report.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `fang_a`, `fang_b`, `fang_c`: base `#e0d9c4`, `up` `#f2ecdc` — fang bone - pale, almost white

**Mask `part_guard`** — flat **140**, on `cop`. 140 is the value every mask in this project
uses.

## Done when

- [ ] The check is clean, or every `!` left standing is one this brief allows.
- [ ] Envelope inside the budget above, **reported in the check's frame**.
- [ ] Pair span reported.
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
