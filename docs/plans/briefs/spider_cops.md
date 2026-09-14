# Brief: Spider Cops

A piece of **Armor Pieces: The Hive** (`armorpieces_hive`) — netherite and lime over lamellar - black insect chitin on dark metal hardware, with the lime of the membrane and the gold of honey as the only light in it.

From the `knees` row of the Hive table:

> `spider_cops` - knee cops with spider legs jutting from the sides - fitting `gemstone` - centre `fermented_spider_eye`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          spider_cops
    anchor:        knees
    namespace:     armorpieces_hive
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\hive\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\hive\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Spider Cops",
                           fittings: ["armorpieces:gemstone"],
                           static: true,
                           recipe: { centre: "minecraft:fermented_spider_eye", craftable: true } }

**Fittings:** one, **`armorpieces:gemstone`**, masked. The reply will say a `part_gemstone` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Spider black-brown is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `hive` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:fermented_spider_eye` is confirmed free against every
template centre in the project.

So this piece has **three sheets**: the greyscale master `part`, the colour layer `part_static`,
and the greyscale mask `part_gemstone`.

## The three surfaces, and which cube gets which

A piece is drawn from three sheets and **they stack** — `recolour(master, static, palette)`, then
one `applyMask` per fitting:

    MATERIAL   `part`            greyscale master, recoloured through the TRIM material's ramp
    STATIC     `part_static`     real colour, painted OVER the recoloured master
    FITTING    `part_gemstone`  greyscale mask over both, filled by the PLAYER

**Static hides material** — a static cube stops answering the trim forever. **An empty fitting costs
nothing** — its mask is not read until a player fills it, so a masked cube still answers the trim
until then, and a static layer *under* a mask is the default look with the fitting as an override.

The **cop** carries no static and no mask; it is the piece's material surface. The **eye** is static red by default AND masked `gemstone`, so a player can set a stone there instead.

## The rig, in Blockbench coordinates

    left leg box            x -3.9 .. 0.1   y 0 .. 12       z -2 .. 2
    leggings shell (+0.4)   x -4.3 .. 0.5   y -0.4 .. 12.4  z -2.4 .. 2.4
    boots shell (+0.9)      x -4.8 .. 1.0   y -0.9 .. 12.9  z -2.9 .. 2.9
    the `knees` anchor       (-1.9, 6, -2)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-1.9, 6, -2)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

A dark metal knee cop with two black spider legs jutting straight out sideways from its outboard edge, one above the other, and a single red eye set in its front. The legs are thin and stiff and stick out further than anything else on the leg.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **cop** — the knee cop over the front of the knee:

        x -3.53 .. -0.27    y 4.13 .. 7.23    z -3.73 .. -2.93

- **leg_up** — the upper spider leg, jutting out sideways:

        x -5.63 .. -3.53    y 6.33 .. 6.93    z -3.54 .. -2.98

- **leg_lo** — the lower leg, a little shorter:

        x -5.27 .. -3.53    y 4.86 .. 5.42    z -3.54 .. -2.98

- **eye** — the red eye set in the front of the cop:

        x -2.33 .. -1.47    y 5.33 .. 6.13    z -4.13 .. -3.73

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -5.7 .. -0.2, y 4.0 .. 7.3, z -4.2 .. -2.8`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -1.7 .. 3.8      y  4.7 .. 8.0      z  -4.2 .. -2.8

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `5.63`, so the pair spans **11.26**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `winged_cops` | x -5.99..-0.45, y 4.50..7.60, z -3.87..-1.53 | the precedent for reaching out sideways from the knee; your legs stop at -5.63, inside it |
| `magma_cops` | x -3.55..-0.25, y 3.72..7.65, z -4.05..-2.58 | a pack knee cop at your width |
| `ghast_tendrils (tassets)` | x -5.46..-3.45, y 4.82..9.72, z -2.30..2.35 | worn WITH you, on the outboard side down to y 4.82 - your legs are in FRONT of it (z < -2.98) but their x range overlaps, so expect an OVERLAP note, a `-` and not a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

cop: base **135**, `up` **165**, `down` **95**. legs: base **55**, `up` **75**. eye: base **45**, `north` **80**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `leg_up`, `leg_lo`: base `#3d342d`, `up` `#4f453c` — spider black-brown - the spider's own body colour
- `eye`: base `#3c0202`, `up` `#7a1a1a` — spider-eye red

**Mask `part_gemstone`** — flat **140**, on `eye`. 140 is the value every mask in this project
uses.

## Done when

- [ ] The check is clean, or every `!` left standing is one this brief allows.
- [ ] Envelope inside the budget above, **reported in the check's frame**.
- [ ] Pair span reported.
- [ ] All three sheets painted — master, `part_static`, `part_gemstone`. `list_textures` is the list;
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
