# Brief: Totem Pendant

A piece of **Armor Pieces: Hero of the Village** (`armorpieces_village`) — iron armor with emerald hardware, the
raid worn by the person who won it.

From the `collar` row of the Hero of the Village table:

> `totem_pendant` - the totem's face hung at the throat - fitting `gemstone` - centre `totem_of_undying`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          totem_pendant
    anchor:        collar
    namespace:     armorpieces_village
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\village\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\village\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Totem Pendant",
                           fittings: ["armorpieces:gemstone"],
                           static: true,
                           recipe: { centre: "minecraft:totem_of_undying", craftable: true } }

**Fittings:** one, **`armorpieces:gemstone`**, masked. The reply will say a `part_gemstone` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Totem green - the carved wood and its jade inlay is a colour that must not change with the armor.
**Effects: none. Loot: none — leave `loot` out of your call entirely.** The recipe above is the only way this piece is had; `minecraft:totem_of_undying` is confirmed free against every template centre in the project.

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

The **cord** and the **link** carry no static and no mask - the cord is the piece's material surface and it should read as the same metal as the armor.

## The rig, in Blockbench coordinates

    body box                x -4 .. 4     y 12 .. 24    z -2 .. 2
    chestplate shell (+1)   x -5 .. 5     y 11 .. 25    z -3 .. 3
    the `collar` anchor       (0, 23, -2)

Front is **negative z**. This socket is not mirrored: build the whole piece once.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(0, 23, -2)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** `ominous_banner` found this out on 2026-09-10: a
`back` piece gets no `past helmet` line at all, because the helmet is not its shell. So the check
will **not** warn you about running into a shell that belongs to a different armor piece. Every
coordinate below already clears the ones that matter; do not move them toward another shell.

## Shape

A totem of undying worn on a cord: the little carved face and its stubby arms, hanging at the throat. It must NOT grant the hero-of-the-village effect - the mod's `circlet` already does that and duplicating it would make that piece pointless. This is an ornament.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **cord** — the bar of the cord across the collarbone:

        x -3.45 .. 3.45    y 22.85 .. 23.65    z -3.65 .. -3.05

- **link** — the short drop from the cord to the totem:

        x -0.45 .. 0.45    y 21.55 .. 22.95    z -3.75 .. -3.25

- **face** — the totem's carved face:

        x -1.55 .. 1.55    y 19.25 .. 21.75    z -4.15 .. -3.15

- **arms** — the totem's stubby outstretched arms:

        x -2.35 .. 2.35    y 20.15 .. 21.05    z -4.05 .. -3.35

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -3.5 .. 3.5, y 19.2 .. 23.7, z -4.2 .. -3.0`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the body bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -3.5 .. 3.5      y  0.3 .. 4.8      z  -4.2 .. -3.0

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `pendant` | x -3.39..3.39, y 19.00..24.46, z -3.85..-3.10 | the piece yours is closest to; you hang 0.3 deeper |
| `crystal_pendant` | x -3.25..3.25, y 19.05..23.15, z -4.05..-3.05 | a pack pendant at your exact depth |
| `nautilus_gorget` | x -3.00..3.00, y 16.85..25.05, z -4.45..-3.15 | the deepest and tallest on this socket |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

face and arms: base **140**, `up` **175**, `down` **95**. cord and link: base **160**, `up` **195** - a thin bright line at the collarbone.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `face`, `arms`: base `#8fbf4a`, `up` `#c6d96b` — totem green - the carved wood and its jade inlay

**Mask `part_gemstone`** — flat **140**, on `face`. 140 is the value every mask in this project
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
