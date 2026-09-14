# Brief: Llama Wraps

A piece of **Armor Pieces: Animals** (`armorpieces_animals`) — leather armor with copper hardware, and every piece reads as one NAMED animal drawn in that animal's own colours from the game.

From the `greaves` row of the Animals table:

> `llama_wraps` - creamy llama-wool wraps up the shins - fitting `inlay` - centre `white_carpet`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          llama_wraps
    anchor:        greaves
    namespace:     armorpieces_animals
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\animals\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\animals\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Llama Wraps",
                           fittings: ["armorpieces:inlay"],
                           static: true,
                           recipe: { centre: "minecraft:white_carpet", craftable: true } }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Creamy llama wool is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `village` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:white_carpet` is confirmed free against every
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

The **knot** carries no static. It is masked `inlay` (it is cord) and is this piece's material surface until a player dyes it.

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

Three bands of creamy llama wool wound round the shin, each a little narrower than the one below, with a cord knot on the outboard side of the top band. Soft, thick, the colour of the creamy llama. The bands are separated by a hair's gap so they read as wraps and not one tube.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **wrap_lo** — the lowest and widest band, at the ankle:

        x -5.07 .. 0.53    y 0.14 .. 1.94    z -3.47 .. -2.27

- **wrap_mid** — the middle band:

        x -4.97 .. 0.43    y 2.08 .. 3.87    z -3.33 .. -2.37

- **wrap_up** — the top band, below the knee:

        x -4.92 .. 0.33    y 4.02 .. 5.67    z -3.27 .. -2.47

- **knot** — the cord knot on the outboard side of the top band:

        x -5.37 .. -4.92    y 4.33 .. 5.13    z -3.07 .. -2.48

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -5.5 .. 0.6, y 0.0 .. 5.8, z -3.6 .. -2.2`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.5 .. 3.6      y  6.2 .. 12.0      z  -3.6 .. -2.2

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `5.37`, so the pair spans **10.74**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `golem_plates` | x -3.85..0.05, y 0.35..5.45, z -3.82..-2.85 | a pack shin piece at your height band; you wrap the sides where it is a front slab |
| `puttees` | x -5.05..0.59, y -0.70..4.45, z -4.15..-1.45 | the mod's own leg wraps - your closest relative; you are shallower and go higher |
| `rabbit_feet (spurs)` | x -2.90..-0.90, y 0.76..8.40, z 2.95..6.59 | your own pack's feet, worn WITH you, all BEHIND the leg (z > 2.95) where you are all in front - never near |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

wraps: base **215**, `north` **230** (the front is the face you see), `down` **185**. knot: base **130**, `west` **160**.

**Each wrap's back face is inside the boot.** The bands run z -3.47 .. -2.27 and the boots shell's front wall is at z -2.9, so the back half of every band is buried and only the front and the two sides show. The inner side face at x 0.53 / 0.43 / 0.33 is inside the shell too (it reaches x 1.0).

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `wrap_lo`, `wrap_mid`, `wrap_up`: base `#f5e2b8`, `up` `#fcebc6` — creamy llama wool - the creamy llama's own coat, and `down` #e3ca95, its shadow

**Mask `part_inlay`** — flat **140**, on `knot`. 140 is the value every mask in this project
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
