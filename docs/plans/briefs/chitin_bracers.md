# Brief: Chitin Bracers

A piece of **Armor Pieces: The Hive** (`armorpieces_hive`) — netherite and lime over lamellar - black insect chitin on dark metal hardware, with the lime of the membrane and the gold of honey as the only light in it.

From the `vambraces` row of the Hive table:

> `chitin_bracers` - segmented black chitin down the forearms - fitting `inlay` - centre `beehive`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          chitin_bracers
    anchor:        vambraces
    namespace:     armorpieces_hive
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\hive\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\hive\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Chitin Bracers",
                           fittings: ["armorpieces:inlay"],
                           static: true,
                           recipe: { centre: "minecraft:beehive", craftable: true } }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Chitin black is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `hive` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:beehive` is confirmed free against every
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

The **cuff** carries no static and no mask; it is the piece's material surface. The **joint** is static lime by default AND masked `inlay`, so a player can re-dye the membrane; the plates are static and never answer the trim.

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

An insect's leg worn as a bracer: a dark metal cuff below the elbow, then two plates of black chitin down the forearm with a band of lime membrane showing between them at the joint. The plates are glossy black; the membrane is the only colour.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **cuff** — the metal cuff below the elbow:

        x -9.23 .. -2.77    y 17.53 .. 18.67    z -3.23 .. 3.23

- **plate_up** — the upper chitin plate:

        x -9.47 .. -2.57    y 15.33 .. 17.53    z -3.43 .. 3.43

- **joint** — the membrane at the joint, inset between the plates:

        x -9.13 .. -2.87    y 14.73 .. 15.33    z -3.13 .. 3.13

- **plate_lo** — the lower chitin plate, to the wrist:

        x -9.31 .. -2.67    y 12.43 .. 14.73    z -3.33 .. 3.33

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -9.6 .. -2.5, y 12.3 .. 18.8, z -3.5 .. 3.5`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the arm bone's pivot at Blockbench `(-5, 22, 0)` - **not** the top of the arm box. For this socket:

    check_x = -5 - bb_x        check_y = 22 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.5 .. 4.6      y  3.2 .. 9.7      z  -3.5 .. 3.5

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `9.47`, so the pair spans **18.94**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the arms are already outboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `ravager_bracers` | x -9.55..-2.65, y 12.15..18.95, z -3.35..3.35 | a pack bracer at your width and height - the closest match |
| `blaze_bracers` | x -9.45..-2.65, y 15.15..20.45, z -3.35..3.35 | sits higher than you |
| `wing_cases (pauldrons)` | x -11.02..-7.05, y 14.07..25.85, z -2.75..2.75 | your own pack's wing cases, worn WITH you, reaching DOWN to y 14.07 on the outboard side and overlapping your plates in a hull test - that is an OVERLAP `-`, not a `!`; it is how the Chitin set already wears them |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

plates: base **60**, `west` **80** (the outboard face has the gloss), `down` **40**. joint: base **150**. cuff: base **130**, `up` **165**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `plate_up`, `plate_lo`: base `#16100e`, `up` `#341911` — chitin black - the bee's own black, with the faintest brown in it
- `joint`: base `#8fd13f`, `up` `#b6ef63` — membrane lime - the Hive's one colour

**Mask `part_inlay`** — flat **140**, on `joint`. 140 is the value every mask in this project
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
