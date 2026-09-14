# Brief: Compound Eyes

A piece of **Armor Pieces: The Hive** (`armorpieces_hive`) — netherite and lime over lamellar - black insect chitin on dark metal hardware, with the lime of the membrane and the gold of honey as the only light in it.

From the `brow` row of the Hive table:

> `compound_eyes` - two bulging faceted insect eyes over your own - fitting `gemstone` - centre `spider_eye`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          compound_eyes
    anchor:        brow
    namespace:     armorpieces_hive
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\hive\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\hive\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Compound Eyes",
                           fittings: ["armorpieces:gemstone"],
                           static: true,
                           recipe: { centre: "minecraft:spider_eye", craftable: true } }

**Fittings:** one, **`armorpieces:gemstone`**, masked. The reply will say a `part_gemstone` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Spider-eye red is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `hive` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:spider_eye` is confirmed free against every
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

The **band** carries no static and no mask. It is the piece's material surface and it should read as the same dark metal as the armor.

## The rig, in Blockbench coordinates

    head box                x -4 .. 4       y 24 .. 32      z -4 .. 4
    helmet shell (+1)       x -5 .. 5       y 23 .. 33      z -5 .. 5
    the `brow` anchor       (0, 28, -4)

Front is **negative z**. This socket is not mirrored: build the whole piece once.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(0, 28, -4)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

Two big dark-red insect eyes bulging out over the wearer's eyes, held by a narrow band of dark metal across the face. The eyes are the piece: rounded, glossy, too large, and dead-looking. Nothing else is on the face.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **band** — the narrow metal band across the eyes that holds them:

        x -4.19 .. 4.19    y 27.13 .. 29.43    z -5.57 .. -5.13

- **eye_l** — the left eye, bulging forward off the band:

        x -3.87 .. -1.13    y 26.83 .. 29.71    z -6.23 .. -5.57

- **eye_r** — the right eye:

        x 1.13 .. 3.87    y 26.83 .. 29.71    z -6.23 .. -5.57

**3 cubes in total is the budget**, and there is no 4th.

**Envelope budget.** Stay inside `x -4.3 .. 4.3, y 26.7 .. 29.8, z -6.3 .. -5.0`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the head bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -4.3 .. 4.3      y  -5.8 .. -2.7      z  -6.3 .. -5.0

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `bone_mask` | x -4.10..4.10, y 26.50..31.25, z -6.10..-5.10 | the Wild Hunt's mask on this socket, the one the Chitin set borrows today - you replace it |
| `frog_mask` | x -5.50..5.50, y 25.25..31.75, z -7.25..-5.25 | wider and deeper than you |
| `antennae (crest)` | x -3.24..3.24, y 32.32..39.73, z -4.91..0.48 | your own pack's crest, worn WITH you, above the helmet - never near you |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

eyes: base **45**, `north` **70**, `up` **90** (a single gloss highlight on top). band: base **135**, `up` **165**.

**Cut nothing.** The eyes have no pupil and no slot; every face gets paint.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `eye_l`, `eye_r`: base `#3c0202`, `up` `#7a1a1a` — spider-eye red - the spider's own eye colour, near black

**Mask `part_gemstone`** — flat **140**, on `eye_l`, `eye_r`. 140 is the value every mask in this project
uses.

## Done when

- [ ] The check is clean, or every `!` left standing is one this brief allows.
- [ ] Envelope inside the budget above, **reported in the check's frame**.
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
