# Brief: Rooster Comb

A piece of **Armor Pieces: Animals** (`armorpieces_animals`) — leather armor with copper hardware, and every piece reads as one NAMED animal drawn in that animal's own colours from the game.

From the `crest` row of the Animals table:

> `rooster_comb` - a rooster's red comb along the crown - fitting `guard` - centre `egg`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          rooster_comb
    anchor:        crest
    namespace:     armorpieces_animals
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\animals\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\animals\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Rooster Comb",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:egg", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Rooster red is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `village` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:egg` is confirmed free against every
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

The **mount** carries no static. It is masked `guard` and is the only thing here that answers the trim.

## The rig, in Blockbench coordinates

    head box                x -4 .. 4       y 24 .. 32      z -4 .. 4
    helmet shell (+1)       x -5 .. 5       y 23 .. 33      z -5 .. 5
    the `crest` anchor       (0, 32, 0)

Front is **negative z**. This socket is not mirrored: build the whole piece once.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(0, 32, 0)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

A rooster's comb: a thin red serrated ridge running front to back over the crown, three points standing up from it, the middle one tallest. It sits on a small copper mount. It is red flesh, not a helmet comb - the mod's own `comb` is the steel one and this must not be mistaken for it.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **mount** — the copper mount plate on the crown the comb rises from:

        x -1.08 .. 1.08    y 32.13 .. 32.83    z -3.87 .. 3.53

- **ridge** — the comb's base ridge, front to back:

        x -0.53 .. 0.53    y 32.83 .. 34.07    z -3.47 .. 3.13

- **point_fr** — the front point:

        x -0.43 .. 0.43    y 34.07 .. 35.33    z -3.07 .. -1.93

- **point_mid** — the middle point, the tallest:

        x -0.43 .. 0.43    y 34.07 .. 35.87    z -1.13 .. 0.27

- **point_bk** — the back point, the shortest:

        x -0.43 .. 0.43    y 34.07 .. 35.13    z 1.09 .. 2.27

**5 cubes in total is the budget**, and there is no 6th.

**Envelope budget.** Stay inside `x -1.2 .. 1.2, y 32.0 .. 36.0, z -4.0 .. 3.6`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the head bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -1.2 .. 1.2      y  -12.0 .. -8.0      z  -4.0 .. 3.6

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `comb` | x -0.75..0.75, y 32.50..34.60, z -2.10..5.60 | the mod's STEEL comb, the piece yours must not be mistaken for - yours is taller and red |
| `dragon_crest` | x -0.55..0.55, y 31.88..35.60, z -3.40..3.62 | a pack crest at your exact thinness and almost your height |
| `fox_ears (horns)` | x -6.11..-1.81, y 31.84..38.71, z -2.31..-0.50 | your own pack's ears, worn WITH you, starting at x -1.81 - your mount ends at -1.08, clear by 0.73 |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

ridge and points: base **120**, `up` **150**, `down` **90`, so the flat red shades itself. mount: base **150**, `up` **185**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `ridge`, `point_fr`, `point_mid`, `point_bk`: base `#ff0000`, `up` `#ff0000` — rooster red - the chicken's own comb colour, one flat red; the master does all the shading

**Mask `part_guard`** — flat **140**, on `mount`. 140 is the value every mask in this project
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
