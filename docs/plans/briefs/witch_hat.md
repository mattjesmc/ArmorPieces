# Brief: Witch Hat

A piece of **Armor Pieces: Hero of the Village** (`armorpieces_village`) — iron armor with emerald hardware, the
raid worn by the person who won it.

From the `crest` row of the Hero of the Village table:

> `witch_hat` - the pointed brim - fitting `inlay` - centre `glass_bottle`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          witch_hat
    anchor:        crest
    namespace:     armorpieces_village
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\village\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\village\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Witch Hat",
                           fittings: ["armorpieces:inlay"],
                           static: true,
                           recipe: { centre: "minecraft:glass_bottle", craftable: true } }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. The felt, witch-purple and almost black is a colour that must not change with the armor.
**Effects: none. Loot: none — leave `loot` out of your call entirely.** The recipe above is the only way this piece is had; `minecraft:glass_bottle` is confirmed free against every template centre in the project.

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

The **band** carries no static and no mask, so it always answers the trim material. That is the whole of this piece's material surface and it must stay bare.

## The rig, in Blockbench coordinates

    head box                x -4 .. 4     y 24 .. 32    z -4 .. 4
    helmet shell (+1)       x -5 .. 5     y 23 .. 33    z -5 .. 5
    the `crest` anchor       (0, 32, 0)

Front is **negative z**. This socket is not mirrored: build the whole piece once.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(0, 32, 0)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** `ominous_banner` found this out on 2026-09-10: a
`back` piece gets no `past helmet` line at all, because the helmet is not its shell. So the check
will **not** warn you about running into a shell that belongs to a different armor piece. Every
coordinate below already clears the ones that matter; do not move them toward another shell.

## Shape

A witch's pointed hat: a wide flat brim and a tall cone leaning off the crown. It is the tallest thing in the pack after the banner and it is meant to read in silhouette at thirty metres. It is deliberately NOT a wizard's hat with stars, and NOT a helmet.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **brim** — the flat wide brim, sitting straight on the crown:

        x -6.45 .. 6.45    y 32.15 .. 32.85    z -6.15 .. 6.15

- **band** — the hat band round the base of the cone - the one metal thing here:

        x -2.75 .. 2.75    y 32.85 .. 33.75    z -2.75 .. 2.75

- **cone1** — the cone's lowest and widest segment:

        x -2.55 .. 2.55    y 33.75 .. 35.35    z -2.55 .. 2.55

- **cone2** — the middle segment:

        x -1.75 .. 1.75    y 35.35 .. 37.65    z -1.75 .. 1.75

- **cone3** — the tip:

        x -0.85 .. 0.85    y 37.65 .. 39.95    z -0.85 .. 0.85

**5 cubes in total is the budget**, and there is no 6th.

**Envelope budget.** Stay inside `x -6.5 .. 6.5, y 32.1 .. 40.0, z -6.2 .. 6.2`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the head bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -6.5 .. 6.5      y  -16.0 .. -8.1      z  -6.2 .. 6.2

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `feathering` | x -1.50..1.50, y 32.00..44.18, z -3.00..8.21 | the tallest crest there is; you are shorter |
| `spire` | x -2.50..2.50, y 32.50..40.00, z -2.50..2.50 | almost exactly your height |
| `circlet (brow)` | x -6.00..6.00, y 27.75..30.75, z -7.00..6.00 | the widest brow piece - your brim is no wider |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

brim and cone: base **70** (the felt is dark), `up` **110** on the brim so the top face catches light, `down` **45` under it. The band: base **165**, `up` **200** - it is the bright metal ring against dark felt, and that contrast is the piece.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `brim`, `cone1`, `cone2`, `cone3`: base `#2a2036`, `up` `#3d3049` — the felt, witch-purple and almost black

**Mask `part_inlay`** — flat **140**, on `cone1`, `cone2`, `cone3`, `brim`. 140 is the value every mask in this project
uses.

## Done when

- [ ] The check is clean, or every `!` left standing is one this brief allows.
- [ ] Envelope inside the budget above, **reported in the check's frame**.
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
