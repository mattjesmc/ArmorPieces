# Brief: Honeycomb Gorget

A piece of **Armor Pieces: The Hive** (`armorpieces_hive`) — netherite and lime over lamellar - black insect chitin on dark metal hardware, with the lime of the membrane and the gold of honey as the only light in it.

From the `collar` row of the Hive table:

> `honeycomb_gorget` - a slab of honeycomb hung at the throat - fitting `guard` - centre `honeycomb_block`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          honeycomb_gorget
    anchor:        collar
    namespace:     armorpieces_hive
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\hive\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\hive\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Honeycomb Gorget",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:honeycomb_block", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Honeycomb gold is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `hive` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:honeycomb_block` is confirmed free against every
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

The **collar** carries no static. It is masked `guard` and is the piece's whole material surface.

## The rig, in Blockbench coordinates

    body box                x -4 .. 4       y 12 .. 24      z -2 .. 2
    chestplate shell (+1)   x -5 .. 5       y 11 .. 25      z -3 .. 3
    leggings shell (+0.5)   x -4.5 .. 4.5   y 11.5 .. 24.5  z -2.5 .. 2.5
    the `collar` anchor       (0, 23, -2)

Front is **negative z**. This socket is not mirrored: build the whole piece once.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(0, 23, -2)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

A gorget cut from honeycomb: a dark metal collar band at the throat, a slab of golden comb hanging from it over the upper chest, and two drips of honey running off its bottom edge. The comb is the subject; the collar band is the only hardware.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **collar** — the metal collar band at the throat:

        x -4.73 .. 4.73    y 23.12 .. 24.47    z -3.90 .. -3.16

- **comb** — the slab of honeycomb hanging from the collar:

        x -3.63 .. 3.63    y 18.93 .. 23.12    z -3.93 .. -3.16

- **drip_a** — a drip of honey off the left of the bottom edge:

        x -2.13 .. -1.27    y 17.93 .. 18.93    z -3.90 .. -3.23

- **drip_b** — a longer drip off the right:

        x 0.67 .. 1.53    y 17.53 .. 18.93    z -3.90 .. -3.23

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -4.8 .. 4.8, y 17.4 .. 24.6, z -4.0 .. -3.1`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the body bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -4.8 .. 4.8      y  -0.6 .. 6.6      z  -4.0 .. -3.1

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `wither_ribs` | x -4.28..4.28, y 17.02..23.20, z -3.95..-3.25 | a pack chest piece at your exact depth and almost your height |
| `nautilus_gorget` | x -3.00..3.00, y 16.85..25.05, z -4.45..-3.15 | Coral's gorget - the same idea, a different sea |
| `carapace (back)` | x -4.75..4.75, y 15.60..24.60, z 3.10..5.25 | your own pack's back piece, worn WITH you, all BEHIND the body where you are all in front |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

comb: base **150**, `north` **175**, `down` **120**. drips: base **200**, `north` **220**. collar: base **130**, `up` **165**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `comb`, `drip_a`, `drip_b`: base `#e88c08`, `up` `#faab1c` — honeycomb gold - the honeycomb block's own colour, and `down` #c86a08, the darker wax

**Mask `part_guard`** — flat **140**, on `collar`. 140 is the value every mask in this project
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
