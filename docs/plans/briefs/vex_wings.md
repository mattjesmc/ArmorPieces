# Brief: Vex Wings

A piece of **Armor Pieces: Hero of the Village** (`armorpieces_village`) — iron armor with emerald hardware, the
raid worn by the person who won it.

From the `pauldrons` row of the Hero of the Village table:

> `vex_wings` - two small grey wings at the shoulder blades - fitting `inlay` - found in a chest

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          vex_wings
    anchor:        pauldrons
    namespace:     armorpieces_village
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\village\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\village\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Vex Wings",
                           fittings: ["armorpieces:inlay"],
                           static: true }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Vex wing - cold near-white, almost translucent is a colour that must not change with the armor.
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

The **mount** carries no static and no mask. It is the clasp, it is metal, and it is this piece's whole material surface.

## The rig, in Blockbench coordinates

    left arm box            x -8 .. -4    y 12 .. 24    z -2 .. 2
    sleeve shell (+1)       x -9 .. -3    y 11 .. 25    z -3 .. 3
    the `pauldrons` anchor       (-6, 22, 0)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-6, 22, 0)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** `ominous_banner` found this out on 2026-09-10: a
`back` piece gets no `past helmet` line at all, because the helmet is not its shell. So the check
will **not** warn you about running into a shell that belongs to a different armor piece. Every
coordinate below already clears the ones that matter; do not move them toward another shell.

## Shape

A vex's wings, small and ragged, sitting high and just behind the shoulder. They are deliberately SMALL - a vex is a hand-sized thing, and wings that read as a cloak would be the wrong monster.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **mount** — the small clasp on the shoulder the wings grow from:

        x -7.35 .. -5.15    y 22.15 .. 23.85    z 0.55 .. 2.35

- **wing_up** — the upper wing, standing up and back:

        x -7.15 .. -5.35    y 23.85 .. 27.65    z 1.15 .. 2.05

- **wing_lo** — the lower wing, shorter and further out:

        x -8.15 .. -6.35    y 22.45 .. 25.35    z 1.35 .. 2.25

**3 cubes in total is the budget**, and there is no 4th.

**Envelope budget.** Stay inside `x -8.2 .. -5.1, y 22.1 .. 27.7, z 0.5 .. 2.4`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the arm bone's pivot at Blockbench `(-5, 22, 0)` - **not** the top of the arm box. For this socket:

    check_x = -5 - bb_x        check_y = 22 - bb_y        check_z = bb_z

and your budget in that frame is

    x  0.1 .. 3.2      y  -5.7 .. -0.1      z  0.5 .. 2.4

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `8.15`, so the pair spans **16.3**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the arms are already outboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `spiked_pauldrons` | x -9.85..-7.20, y 22.40..28.53, z -3.10..3.10 | your height twin; it sits further out, you sit further in |
| `epaulettes` | x -9.85..-7.20, y 22.00..25.95, z -2.60..2.60 | the modest end of this socket |
| `wither_heads` | x -9.45..-4.55, y 23.55..28.15, z -2.55..2.55 | a pack piece of the same scale - a good size check |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

wings: base **190** with a `[210, 150]` top-to-bottom gradient on `west` and `east` so they fade toward the trailing edge. mount: base **145**, `up` **180**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `wing_up`, `wing_lo`: base `#b9c2cc`, `up` `#d6dde4` — vex wing - cold near-white, almost translucent

**Mask `part_inlay`** — flat **140**, on `wing_up`, `wing_lo`. 140 is the value every mask in this project
uses.

## Done when

- [ ] The check is clean, or every `!` left standing is one this brief allows.
- [ ] Envelope inside the budget above, **reported in the check's frame**.
- [ ] Pair span reported.
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
