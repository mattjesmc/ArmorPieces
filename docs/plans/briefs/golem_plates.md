# Brief: Golem Plates

A piece of **Armor Pieces: Hero of the Village** (`armorpieces_village`) — iron armor with emerald hardware, the
raid worn by the person who won it.

From the `greaves` row of the Hero of the Village table:

> `golem_plates` - the iron golem's slab legs, cut down - fitting `inlay` - centre `iron_helmet`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          golem_plates
    anchor:        greaves
    namespace:     armorpieces_village
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\village\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\village\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Golem Plates",
                           fittings: ["armorpieces:inlay"],
                           static: true,
                           recipe: { centre: "minecraft:iron_helmet", craftable: true } }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Vine green - the one living thing on an iron leg is a colour that must not change with the armor.
**Effects: none. Loot: none — leave `loot` out of your call entirely.** The recipe above is the only way this piece is had; `minecraft:iron_helmet` is confirmed free against every template centre in the project.

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

**Both slabs carry no static and no mask.** They are iron and they must answer the trim - this piece has the largest material surface in the pack, and that is the point of it.

## The rig, in Blockbench coordinates

    left leg box            x -4 .. 0     y 0 .. 12     z -2 .. 2
    leggings shell (+1)     x -5 .. 1     y -1 .. 13    z -3 .. 3
    the `greaves` anchor       (-1.9, 4, -2)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-1.9, 4, -2)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** `ominous_banner` found this out on 2026-09-10: a
`back` piece gets no `past helmet` line at all, because the helmet is not its shell. So the check
will **not** warn you about running into a shell that belongs to a different armor piece. Every
coordinate below already clears the ones that matter; do not move them toward another shell.

## Shape

Two heavy iron slabs strapped up the shin, with a single vine growing across them - the vine is what says iron GOLEM rather than iron plate. Blunt and heavy; nothing here tapers.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **slab_lo** — the lower slab, the heavier of the two:

        x -3.85 .. 0.05    y 0.35 .. 2.85    z -3.75 .. -2.85

- **slab_up** — the upper slab:

        x -3.65 .. -0.15    y 2.85 .. 5.15    z -3.65 .. -2.95

- **vine** — the vine running up across both slabs:

        x -3.25 .. -2.55    y 0.65 .. 5.45    z -3.82 .. -3.28

**3 cubes in total is the budget**, and there is no 4th.

**Envelope budget.** Stay inside `x -3.9 .. 0.1, y 0.3 .. 5.5, z -3.9 .. -2.8`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.0 .. 2.0      y  6.5 .. 11.7      z  -3.9 .. -2.8

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `3.85`, so the pair spans **7.7**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `soul_greaves` | x -4.06..-0.15, y 0.35..8.37, z -3.12..-2.62 | a pack greave starting at your exact height |
| `scale_shins` | x -4.40..0.00, y -0.73..4.62, z -3.82..-0.41 | your width twin |
| `shin_spikes` | x -2.90..-0.90, y 0.90..3.75, z -5.51..-2.95 | the deepest on this socket |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

slabs: base **155**, `up` **190**, `down` **110**, `west` **170** - plain bright iron. vine: base **120** with a `[140, 100]` gradient down its `west` face.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `vine`: base `#4a7a35`, `up` `#66a049` — vine green - the one living thing on an iron leg

**Mask `part_inlay`** — flat **140**, on `vine`. 140 is the value every mask in this project
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
