# Brief: Abdomen Plates

A piece of **Armor Pieces: The Hive** (`armorpieces_hive`) — netherite and lime over lamellar - black insect chitin on dark metal hardware, with the lime of the membrane and the gold of honey as the only light in it.

From the `tassets` row of the Hive table:

> `abdomen_plates` - banded black-and-lime segments over the hips - fitting `inlay` - centre `honey_bottle`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          abdomen_plates
    anchor:        tassets
    namespace:     armorpieces_hive
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\hive\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\hive\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Abdomen Plates",
                           fittings: ["armorpieces:inlay"],
                           static: true,
                           recipe: { centre: "minecraft:honey_bottle", craftable: true } }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Chitin black is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `hive` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:honey_bottle` is confirmed free against every
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

The **strap** carries no static and no mask; it is the piece's material surface. The **stripes** are static lime by default AND masked `inlay`, so a player can re-dye them; the segments are static and never answer the trim.

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

A bee's abdomen worn over each hip: a metal strap at the top, then black chitin segments stepping down with a lime stripe between each - the stripes a little wider than the segments so they stand proud as bands. Black, lime, black, lime, from the hip to mid-thigh.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **strap** — the metal strap over the top of the hip:

        x -4.47 .. 0.53    y 11.27 .. 12.07    z -2.97 .. 2.93

- **seg_a** — the first black segment:

        x -5.18 .. 0.43    y 9.53 .. 11.27    z -3.57 .. 3.53

- **stripe_a** — the first lime stripe, standing proud:

        x -5.37 .. 0.43    y 8.93 .. 9.53    z -3.73 .. 3.73

- **seg_b** — the second black segment, a little smaller:

        x -4.97 .. 0.33    y 7.33 .. 8.93    z -3.33 .. 3.37

- **stripe_b** — the second lime stripe:

        x -5.18 .. 0.33    y 6.73 .. 7.33    z -3.57 .. 3.53

**5 cubes in total is the budget**, and there is no 6th.

**Envelope budget.** Stay inside `x -5.5 .. 0.6, y 6.6 .. 12.2, z -3.8 .. 3.8`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.5 .. 3.6      y  -0.2 .. 5.4      z  -3.8 .. 3.8

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `5.37`, so the pair spans **10.74**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `pelt` | x -4.90..-2.44, y 7.28..12.30, z -3.30..2.98 | the Wild Hunt's pelt, the piece the Chitin set borrows here today - you replace it |
| `ravager_saddle` | x -5.15..-0.85, y 6.15..12.15, z -3.40..2.85 | a pack hip piece at your exact height band |
| `garters (knees)` | x -5.95..1.25, y 3.80..6.85, z -3.05..0.20 | worn WITH you, rising to y 6.85 - your lowest stripe starts at 6.73, so expect an OVERLAP note, a `-` and not a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

segments: base **55**, `west` **75**, `down` **40**. stripes: base **150**, `west` **170**. strap: base **130**, `up` **165**.

**Each segment encloses the thigh.** Its inner face at x 0.43 / 0.33 is inside the boots shell (which reaches x 1.0) and never seen.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `seg_a`, `seg_b`: base `#16100e`, `up` `#341911` — chitin black - the bee's own black
- `stripe_a`, `stripe_b`: base `#8fd13f`, `up` `#b6ef63` — membrane lime - the Hive's one colour

**Mask `part_inlay`** — flat **140**, on `stripe_a`, `stripe_b`. 140 is the value every mask in this project
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
