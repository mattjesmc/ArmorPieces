# Brief: Starfish Bracers

A piece of **Armor Pieces: Coral** (`armorpieces_coral`) — turtle-scute armor with copper hardware, the reef worn ashore - coral, kelp and the creatures of the shallows, every one in its own colour.

From the `vambraces` row of the Ocean table:

> `starfish_bracers` - a sea star clamped on the outside of each forearm - fitting `guard` - centre `bubble_coral_block`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          starfish_bracers
    anchor:        vambraces
    namespace:     armorpieces_coral
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\coral\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\coral\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Starfish Bracers",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:bubble_coral_block", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Fire coral red is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `ocean` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:bubble_coral_block` is confirmed free against every
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

The **cuff** carries no static. It is masked `guard` and is the piece's whole material surface; the star never answers the trim.

## The rig, in Blockbench coordinates

    left arm box            x -8 .. -4      y 12 .. 24      z -2 .. 2
    sleeve shell (+1)       x -9 .. -3      y 11 .. 25      z -3 .. 3
    the `vambraces` anchor       (-6, 16, 0)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-6, 16, 0)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

A copper cuff round the forearm with a red sea star clamped flat on its outboard face: a central disc and five short arms - one up, one forward, one back, two down at a spread. The star is the subject; the cuff only holds it on.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **cuff** — the copper cuff round the forearm:

        x -9.27 .. -2.73    y 13.33 .. 16.87    z -3.27 .. 3.27

- **disc** — the star's central disc, on the outboard face of the cuff:

        x -9.87 .. -9.27    y 14.27 .. 15.93    z -0.83 .. 0.83

- **arm_up** — the arm pointing up the forearm:

        x -9.77 .. -9.27    y 15.93 .. 17.53    z -0.45 .. 0.43

- **arm_fr** — the arm pointing forward:

        x -9.77 .. -9.27    y 14.67 .. 15.53    z -2.63 .. -0.83

- **arm_bk** — the arm pointing back:

        x -9.77 .. -9.27    y 14.67 .. 15.53    z 0.83 .. 2.63

- **arm_dfr** — the lower-front arm, down and a little forward:

        x -9.77 .. -9.27    y 12.67 .. 14.27    z -1.73 .. -0.93

- **arm_dbk** — the lower-back arm, down and a little back:

        x -9.77 .. -9.27    y 12.67 .. 14.27    z 0.93 .. 1.73

**7 cubes in total is the budget**, and there is no 8th.

**Envelope budget.** Stay inside `x -10.0 .. -2.6, y 12.6 .. 17.6, z -3.4 .. 3.4`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the arm bone's pivot at Blockbench `(-5, 22, 0)` - **not** the top of the arm box. For this socket:

    check_x = -5 - bb_x        check_y = 22 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.4 .. 5.0      y  4.4 .. 9.4      z  -3.4 .. 3.4

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `9.87`, so the pair spans **19.74**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the arms are already outboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `ravager_bracers` | x -9.55..-2.65, y 12.15..18.95, z -3.35..3.35 | a pack cuff at almost your width; the precedent for the cuff |
| `buckler` | x -10.20..-3.10, y 12.53..18.47, z -3.35..3.35 | reaches further out than your star does |
| `wing_cases (pauldrons)` | x -11.02..-7.05, y 14.07..25.85, z -2.75..2.75 | worn WITH you and reaching down to y 14.07 on the outboard side - your star's arm_up ends at 17.53 and sits inside its x range; that is a hull graze, a `-`, not a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

star (disc and five arms): base **80**, `west` **100** (the outboard face is the one you see), the disc's `west` **115** so the centre reads raised. cuff: base **150**, `up` **185**, `down` **110**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `disc`, `arm_up`, `arm_fr`, `arm_bk`, `arm_dfr`, `arm_dbk`: base `#c62a37`, `up` `#e23f36` — fire coral red - the sea star's own colour, the game's fire coral block

**Mask `part_guard`** — flat **140**, on `cuff`. 140 is the value every mask in this project
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
