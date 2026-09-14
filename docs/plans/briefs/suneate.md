# Brief: Suneate

A piece of **Armor Pieces: Samurai** (`armorpieces_samurai`) — black lacquer over iron, red odoshi lacing and gilt fittings - the armor of a daimyo, every piece a named part of a real suit.

From the `greaves` row of the Samurai table:

> `suneate` - three iron splints on an indigo cloth backing up each shin - fitting `guard` - centre `bamboo`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          suneate
    anchor:        greaves
    namespace:     armorpieces_samurai
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\samurai\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\samurai\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Suneate",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:bamboo", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Indigo cloth is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `daimyo` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:bamboo` is confirmed free against every
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

The three **splints** carry no static. They are masked `guard` and are the piece's whole material surface; the backing is static indigo.

## The rig, in Blockbench coordinates

    left leg box            x -3.9 .. 0.1   y 0 .. 12       z -2 .. 2
    leggings shell (+0.4)   x -4.3 .. 0.5   y -0.4 .. 12.4  z -2.4 .. 2.4
    boots shell (+0.9)      x -4.8 .. 1.0   y -0.9 .. 12.9  z -2.9 .. 2.9
    the `greaves` anchor       (-1.9, 4, -2)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-1.9, 4, -2)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

The shin guard: a panel of indigo cloth wrapped over the front of the shin, with three vertical iron splints standing proud on it, evenly spaced. The splints are the hardware; the cloth is what they are sewn to. It stops below the knee.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **backing** — the cloth panel over the shin:

        x -5.03 .. 0.23    y 0.47 .. 4.11    z -3.28 .. -2.42

- **splint_a** — the outer splint:

        x -4.38 .. -3.87    y 0.67 .. 3.92    z -3.68 .. -3.28

- **splint_b** — the middle splint:

        x -2.72 .. -2.13    y 0.67 .. 3.92    z -3.68 .. -3.28

- **splint_c** — the inner splint:

        x -0.97 .. -0.37    y 0.67 .. 3.92    z -3.68 .. -3.28

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -5.1 .. 0.3, y 0.4 .. 4.2, z -3.8 .. -2.3`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.2 .. 3.2      y  7.8 .. 11.6      z  -3.8 .. -2.3

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `5.03`, so the pair spans **10.06**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `golem_plates` | x -3.85..0.05, y 0.35..5.45, z -3.82..-2.85 | a pack shin slab at your width; you are shorter |
| `puttees` | x -5.05..0.59, y -0.70..4.45, z -4.15..-1.45 | the mod's own leg wraps - deeper and wider than you |
| `knee_studs (knees)` | x -3.15..-0.65, y 3.90..6.10, z -3.50..-3.00 | worn WITH you and reaching down to y 3.90 - your splints end at 3.93, so expect an OVERLAP note, a `-` and not a `!` |
| `kusazuri (tassets)` | x -5.40..0.60, y 6.70..12.20, z -3.90..3.80 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `haidate (knees)` | x -3.90..0.10, y 4.20..6.80, z -4.00..-2.80 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `waraji (spurs)` | x -5.20..1.40, y 0.30..2.80, z 0.50..4.40 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

backing: base **90**, `north` **105**, `down` **70**. splints: base **140**, `north` **175**, `up` **185**.

**The backing's back face is inside the boot.** It runs z -3.37 .. -2.43 and the boots shell's front wall is at z -2.9, so its back half is buried and only the front and the two sides show.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `backing`: base `#2b3a6b`, `up` `#3d4f8a` — indigo cloth - the sleeve and backing cloth of a real suit

**Mask `part_guard`** — flat **140**, on `splint_a`, `splint_b`, `splint_c`. 140 is the value every mask in this project
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

