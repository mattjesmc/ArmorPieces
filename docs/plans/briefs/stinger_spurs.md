# Brief: Stinger Spurs

A piece of **Armor Pieces: The Hive** (`armorpieces_hive`) — netherite and lime over lamellar - black insect chitin on dark metal hardware, with the lime of the membrane and the gold of honey as the only light in it.

From the `spurs` row of the Hive table:

> `stinger_spurs` - a bee's stinger jutting back from each heel - fitting `guard` - centre `bee_nest`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          stinger_spurs
    anchor:        spurs
    namespace:     armorpieces_hive
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\hive\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\hive\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Stinger Spurs",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:bee_nest", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Bee yellow is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `hive` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:bee_nest` is confirmed free against every
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

A bee's tail end worn at the heel: a dark metal anklet, a striped yellow-and-black abdomen going straight back from it, and a thin black stinger jutting out of the end. It is a spur that stings. The stripe is a black band standing a hair proud of the yellow.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **ring** — the metal anklet:

        x -4.12 .. 0.37    y 1.13 .. 2.33    z -3.22 .. 3.37

- **abdomen** — the yellow abdomen, straight back from the heel:

        x -2.93 .. -0.87    y 1.33 .. 2.73    z 3.37 .. 5.27

- **stripe** — the black stripe round the abdomen, standing a hair proud:

        x -3.03 .. -0.77    y 1.22 .. 2.83    z 4.13 .. 4.73

- **stinger** — the stinger, a thin black rod out of the end:

        x -2.23 .. -1.57    y 1.72 .. 2.33    z 5.27 .. 6.87

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -4.2 .. 0.5, y 1.0 .. 2.9, z -3.3 .. 7.0`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.4 .. 2.3      y  9.1 .. 11.0      z  -3.3 .. 7.0

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `4.12`, so the pair spans **8.24**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `talons` | x -3.40..-0.40, y 0.22..3.50, z 3.00..7.81 | the Wild Hunt's talons, the piece the Chitin set borrows here today - you replace it, and reach less far back |
| `dragon_talons` | x -3.36..-0.49, y 0.77..2.60, z 3.00..4.66 | your height band exactly, shorter than you |
| `silverfish_greaves (greaves)` | x -5.27..0.43, y 0.24..6.13, z -4.63..-2.33 | your own pack's shins, worn WITH you, all in FRONT of the leg where you are all behind - never near |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

abdomen: base **190**, `up` **215**, `down` **160**. stripe and stinger: base **50**, `up` **70**. ring: base **130**, `up` **165**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `abdomen`: base `#edc343`, `up` `#fed668` — bee yellow - the bee's own stripe colour
- `stripe`, `stinger`: base `#16100e`, `up` `#341911` — bee black

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
