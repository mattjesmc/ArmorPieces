# Brief: Corinthian Face

A piece of **Armor Pieces: Antiquity** (`armorpieces_antiquity`) — bronze and red leather - Greece and Rome, the hoplite and the legionary, every piece a thing with a Latin or Greek name.

From the `brow` row of the Antiquity table:

> `corinthian_face` - the Corinthian helmet's bronze face plate: two cheek pieces, a nasal and a brow bar - fitting `guard` - centre `copper_helmet`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          corinthian_face
    anchor:        brow
    namespace:     armorpieces_antiquity
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\antiquity\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\antiquity\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Corinthian Face",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:copper_helmet", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Bronze is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `legion` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:copper_helmet` is confirmed free against every
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

The **nasal** carries no static and no mask; it is the piece's material surface. The cheeks and brow bar are static bronze by default AND masked `guard`, so a player can make the face iron instead.

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

The face of a Corinthian helmet: two big bronze cheek pieces covering the lower face, a narrow nasal running down between the eyes, and a brow bar across the top - leaving the T-shaped opening of eyes and nose-slot. Bronze by default; the fitting can make it iron or gold.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **cheek_l** — the left cheek piece:

        x -4.13 .. -0.77    y 24.37 .. 27.42    z -5.63 .. -5.07

- **cheek_r** — the right cheek piece:

        x 0.77 .. 4.13    y 24.37 .. 27.42    z -5.63 .. -5.07

- **nasal** — the nasal, down between the eyes:

        x -0.47 .. 0.48    y 25.57 .. 29.63    z -5.83 .. -5.07

- **brow_bar** — the brow bar across the top:

        x -4.13 .. 4.13    y 29.63 .. 30.83    z -5.63 .. -5.07

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -4.2 .. 4.2, y 24.3 .. 30.9, z -5.9 .. -5.0`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the head bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -4.2 .. 4.2      y  -6.9 .. -0.3      z  -5.9 .. -5.0

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `nasal` | x -4.50..4.50, y 26.00..30.00, z -5.75..-4.50 | the mod's nasal helm - your brow bar and nasal, without the cheeks |
| `great_helm` | x -4.00..4.00, y 23.25..30.25, z -5.35..-4.50 | the mod's great helm face, which covers everything where you leave the T open |
| `wither_mask` | x -4.10..4.10, y 25.10..31.30, z -6.45..-5.15 | a pack faceplate at your width |
| `transverse_crest (crest)` | x -7.20..7.20, y 33.00..37.60, z -1.00..1.00 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `ammon_horns (horns)` | x -6.20..-5.00, y 26.50..31.50, z -1.50..3.10 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

cheeks and brow bar: base **150**, `north` **185**, `down` **110**. nasal: base **140**, `north` **175**.

**Cut nothing.** The eye holes and the nose slot are the gaps between the cubes; every face above gets paint.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `cheek_l`, `cheek_r`, `brow_bar`: base `#b8783a`, `up` `#d99a5a` — bronze - the polished bronze of a real greave, warm and orange

**Mask `part_guard`** — flat **140**, on `cheek_l`, `cheek_r`, `brow_bar`. 140 is the value every mask in this project
uses.

## Done when

- [ ] The check is clean, or every `!` left standing is one this brief allows.
- [ ] Envelope inside the budget above, **reported in the check's frame**.
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

