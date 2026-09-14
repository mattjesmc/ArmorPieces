# Brief: Dolphin Flukes

A piece of **Armor Pieces: Coral** (`armorpieces_coral`) — turtle-scute armor with copper hardware, the reef worn ashore - coral, kelp and the creatures of the shallows, every one in its own colour.

From the `spurs` row of the Ocean table:

> `dolphin_flukes` - a dolphin's tail fluke trailing from each heel - fitting `guard` - centre `salmon`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          dolphin_flukes
    anchor:        spurs
    namespace:     armorpieces_coral
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\coral\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\coral\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Dolphin Flukes",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:salmon", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Dolphin grey-blue is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `ocean` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:salmon` is confirmed free against every
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

The **ring** carries no static. It is masked `guard`, it is the anklet, and it is the piece's whole material surface.

## The rig, in Blockbench coordinates

    left leg box            x -3.9 .. 0.1   y 0 .. 12       z -2 .. 2
    leggings shell (+0.4)   x -4.3 .. 0.5   y -0.4 .. 12.4  z -2.4 .. 2.4
    boots shell (+0.9)      x -4.8 .. 1.0   y -0.9 .. 12.9  z -2.9 .. 2.9
    the `spurs` anchor       (-1.9, 2, 2)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-1.9, 2, 2)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

A dolphin's tail worn at the heel: a copper anklet, a short thick tail stock going straight back from it, and the flat horizontal fluke spread sideways at the end - wider than the leg, thin as a blade. Grey-blue, the dolphin's own colour. It is horizontal, not a fin standing up.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **ring** — the copper anklet:

        x -4.12 .. 0.33    y 1.22 .. 2.38    z -3.10 .. 3.27

- **stock** — the tail stock, straight back from the heel:

        x -2.42 .. -1.37    y 1.53 .. 2.47    z 3.27 .. 5.07

- **fluke** — the flat fluke, spread sideways at the end of the stock:

        x -3.93 .. 0.13    y 1.72 .. 2.29    z 5.07 .. 6.73

**3 cubes in total is the budget**, and there is no 4th.

**Envelope budget.** Stay inside `x -4.2 .. 0.4, y 1.1 .. 2.6, z -3.2 .. 6.8`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.3 .. 2.3      y  9.4 .. 10.9      z  -3.2 .. 6.8

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `4.12`, so the pair spans **8.24**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `allay_wisps` | x -4.15..0.35, y 1.15..5.15, z -3.20..5.55 | a pack piece on this socket; its ring is the precedent for yours |
| `dragon_talons` | x -3.36..-0.49, y 0.77..2.60, z 3.00..4.66 | your height band exactly, and shorter than you |
| `swim_fins (greaves)` | x -7.14..-4.11, y 0.78..3.44, z -2.00..2.00 | your pack's own fins, worn WITH you, on the OUTBOARD side; your ring ends at x -4.12, inside its -4.11 by 0.01, and that is deliberate |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

stock and fluke: base **175**, `up` **205**, `down` **150**. ring: base **150**, `up` **185**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `stock`, `fluke`: base `#9db2c9`, `up` `#bfd0db` — dolphin grey-blue - the game's own dolphin, and `down` #8a9ab1, the darker underside

**Mask `part_guard`** — flat **140**, on `ring`. 140 is the value every mask in this project
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
