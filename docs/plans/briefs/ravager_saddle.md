# Brief: Ravager Saddle

A piece of **Armor Pieces: Hero of the Village** (`armorpieces_village`) — iron armor with emerald hardware, the
raid worn by the person who won it.

From the `tassets` row of the Hero of the Village table:

> `ravager_saddle` - the leather saddle skirt over the hips - fitting `inlay` - found in a chest

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          ravager_saddle
    anchor:        tassets
    namespace:     armorpieces_village
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\village\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\village\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Ravager Saddle",
                           fittings: ["armorpieces:inlay"],
                           static: true }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Saddle leather - mid brown, a warmer leather than the belt's is a colour that must not change with the armor.
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

The **strap** carries no static and no mask. It is the piece's material surface.

## The rig, in Blockbench coordinates

    left leg box            x -4 .. 0     y 0 .. 12     z -2 .. 2
    leggings shell (+1)     x -5 .. 1     y -1 .. 13    z -3 .. 3
    the `tassets` anchor       (-1.9, 10, 0)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-1.9, 10, 0)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** `ominous_banner` found this out on 2026-09-10: a
`back` piece gets no `past helmet` line at all, because the helmet is not its shell. So the check
will **not** warn you about running into a shell that belongs to a different armor piece. Every
coordinate below already clears the ones that matter; do not move them toward another shell.

## Shape

The ravager's saddle, cut down and worn as a hip skirt: a strap over the hip, a broad leather panel, and a cut fringe along the bottom. Heavy leather, not cloth.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **strap** — the strap over the top of the hip:

        x -4.95 .. -0.85    y 11.15 .. 12.15    z -3.15 .. 2.85

- **panel** — the broad saddle panel:

        x -5.15 .. -0.95    y 7.35 .. 11.35    z -3.45 .. 2.65

- **fringe** — the cut fringe along the bottom edge:

        x -5.05 .. -1.05    y 6.15 .. 7.55    z -3.25 .. 2.45

**3 cubes in total is the budget**, and there is no 4th.

**Envelope budget.** Stay inside `x -5.2 .. -0.8, y 6.1 .. 12.2, z -3.5 .. 2.9`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -1.1 .. 3.3      y  -0.2 .. 5.9      z  -3.5 .. 2.9

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `5.15`, so the pair spans **10.3**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `pelt` | x -4.90..-2.44, y 7.28..12.30, z -3.30..2.98 | the closest match in shape and depth |
| `scale_skirt` | x -4.90..-1.00, y 7.10..12.50, z -3.00..1.00 | your width twin |
| `thigh_sheath` | x -5.35..0.85, y 3.53..11.94, z -2.80..2.80 | the longest on this socket |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

panel: base **120** with a `[135, 95]` gradient down `west` so the skirt darkens toward the hem. fringe: base **95**. strap: base **150**, `up` **185**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `panel`, `fringe`: base `#6b4a2e`, `up` `#8a6440` — saddle leather - mid brown, a warmer leather than the belt's

**Mask `part_inlay`** — flat **140**, on `panel`, `fringe`. 140 is the value every mask in this project
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
