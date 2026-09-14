# Brief: Kote

A piece of **Armor Pieces: Samurai** (`armorpieces_samurai`) — black lacquer over iron, red odoshi lacing and gilt fittings - the armor of a daimyo, every piece a named part of a real suit.

From the `vambraces` row of the Samurai table:

> `kote` - an indigo cloth sleeve with a lacquered plate on the back of the forearm - fitting `guard` - centre `cyan_dye`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          kote
    anchor:        vambraces
    namespace:     armorpieces_samurai
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\samurai\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\samurai\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Kote",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:cyan_dye", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Indigo cloth is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `daimyo` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:cyan_dye` is confirmed free against every
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

The **cuff** carries no static. It is masked `guard` and is the piece's whole material surface; the sleeve, plate and lace never answer the trim.

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

The armoured sleeve: a tube of indigo cloth round the forearm, an iron cuff at its top just below the elbow, a black lacquered plate lying on the outside of the forearm, and a single strip of red lacing across that plate. Cloth first, metal second.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **sleeve** — the indigo cloth sleeve round the forearm:

        x -9.23 .. -2.77    y 12.37 .. 17.73    z -3.23 .. 3.23

- **cuff** — the iron cuff at the top of the sleeve:

        x -9.31 .. -2.67    y 17.73 .. 18.27    z -3.33 .. 3.33

- **plate** — the lacquered plate on the outside of the forearm:

        x -9.53 .. -9.23    y 13.07 .. 16.63    z -2.33 .. 2.33

- **lace** — the strip of lacing across the plate:

        x -9.67 .. -9.53    y 14.57 .. 15.13    z -2.03 .. 2.03

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -9.8 .. -2.6, y 12.3 .. 18.4, z -3.4 .. 3.4`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the arm bone's pivot at Blockbench `(-5, 22, 0)` - **not** the top of the arm box. For this socket:

    check_x = -5 - bb_x        check_y = 22 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.4 .. 4.8      y  3.6 .. 9.7      z  -3.4 .. 3.4

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `9.67`, so the pair spans **19.34**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the arms are already outboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `chitin_bracers` | x -9.47..-2.57, y 12.43..18.67, z -3.43..3.43 | the Hive's bracer at your width and almost your height |
| `ravager_bracers` | x -9.55..-2.65, y 12.15..18.95, z -3.35..3.35 | a pack cuff at your width |
| `wing_cases (pauldrons)` | x -11.02..-7.05, y 14.07..25.85, z -2.75..2.75 | worn WITH you and reaching down to y 14.07 on the outboard side - an OVERLAP `-`, not a `!` |
| `sode (pauldrons)` | x -10.70..-4.30, y 18.30..25.90, z -3.40..3.40 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

sleeve: base **90**, `west` **105**, `down` **70**. plate: base **60**, `west` **80**. lace: base **150**. cuff: base **130**, `up` **165**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `sleeve`: base `#2b3a6b`, `up` `#3d4f8a` — indigo cloth - the sleeve and backing cloth of a real suit
- `plate`: base `#1a1614`, `up` `#2e2724` — lacquer black - the suit's own black, with a warm brown in the light
- `lace`: base `#b3202a`, `up` `#d8323a` — odoshi red - the lacing cord's own red

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

