# Brief: Kusazuri

A piece of **Armor Pieces: Samurai** (`armorpieces_samurai`) — black lacquer over iron, red odoshi lacing and gilt fittings - the armor of a daimyo, every piece a named part of a real suit.

From the `tassets` row of the Samurai table:

> `kusazuri` - two tiers of lacquered lamellae hanging over each hip, laced in red - fitting `inlay` - centre `red_wool`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          kusazuri
    anchor:        tassets
    namespace:     armorpieces_samurai
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\samurai\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\samurai\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Kusazuri",
                           fittings: ["armorpieces:inlay"],
                           static: true,
                           recipe: { centre: "minecraft:red_wool", craftable: true } }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Lacquer black is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `daimyo` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:red_wool` is confirmed free against every
template centre in the project.

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

The **strap** carries no static and no mask; it is the piece's material surface. The **lacing** is static red by default AND masked `inlay`; the tiers are static and never answer the trim.

## The rig, in Blockbench coordinates

    left leg box            x -3.9 .. 0.1   y 0 .. 12       z -2 .. 2
    leggings shell (+0.4)   x -4.3 .. 0.5   y -0.4 .. 12.4  z -2.4 .. 2.4
    boots shell (+0.9)      x -4.8 .. 1.0   y -0.9 .. 12.9  z -2.9 .. 2.9
    the `tassets` anchor       (-1.9, 10, 0)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-1.9, 10, 0)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

The skirt of the cuirass: an iron strap over the top of the hip and, hanging from it, two tiers of black lacquered lamellae stepping outward as they go down, with a row of red lacing standing proud between the tiers and another below the lowest one. Black, red, black, red.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **strap** — the iron strap over the top of the hip:

        x -4.47 .. 0.47    y 11.47 .. 12.13    z -2.88 .. 2.93

- **tier_a** — the upper tier of lamellae:

        x -5.01 .. 0.39    y 9.67 .. 11.47    z -3.38 .. 3.47

- **lace_a** — the lacing between the tiers, standing proud:

        x -5.18 .. 0.39    y 9.17 .. 9.67    z -3.79 .. 3.63

- **tier_b** — the lower tier, a little wider:

        x -5.18 .. 0.27    y 7.33 .. 9.17    z -3.38 .. 3.57

- **lace_b** — the lowest lacing:

        x -5.32 .. 0.27    y 6.83 .. 7.33    z -3.79 .. 3.73

**5 cubes in total is the budget**, and there is no 6th.

**Envelope budget.** Stay inside `x -5.4 .. 0.6, y 6.7 .. 12.2, z -3.9 .. 3.8`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.5 .. 3.5      y  -0.2 .. 5.3      z  -3.9 .. 3.8

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `5.32`, so the pair spans **10.64**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `abdomen_plates` | x -5.37..0.53, y 6.73..12.07, z -3.73..3.73 | the Hive's hip piece - the same stacked-tier idea, in the same band |
| `ravager_saddle` | x -5.15..-0.85, y 6.15..12.15, z -3.40..2.85 | a pack hip piece at your height band |
| `garters (knees)` | x -5.95..1.25, y 3.80..6.85, z -3.05..0.20 | worn WITH you, rising to y 6.85 - your lowest lacing starts at 6.87, clear by a hair |
| `haidate (knees)` | x -3.90..0.10, y 4.20..6.80, z -4.00..-2.80 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `suneate (greaves)` | x -5.10..0.30, y 0.40..4.20, z -3.80..-2.30 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `waraji (spurs)` | x -5.20..1.40, y 0.30..2.80, z 0.50..4.40 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

tiers: base **60**, `west` **80**, `down` **40**. lacing: base **150**, `west` **170**. strap: base **130**, `up` **165**.

**Each tier encloses the thigh.** Its inner face at x 0.37 / 0.27 is inside the boots shell (which reaches x 1.0) and never seen.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `tier_a`, `tier_b`: base `#1a1614`, `up` `#2e2724` — lacquer black - the suit's own black, with a warm brown in the light
- `lace_a`, `lace_b`: base `#b3202a`, `up` `#d8323a` — odoshi red - the lacing cord's own red

**Mask `part_inlay`** — flat **140**, on `lace_a`, `lace_b`. 140 is the value every mask in this project
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

