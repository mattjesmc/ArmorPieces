# Brief: Allay Wisps

A piece of **Armor Pieces: Hero of the Village** (`armorpieces_village`) — iron armor with emerald hardware, the
raid worn by the person who won it.

From the `spurs` row of the Hero of the Village table:

> `allay_wisps` - two small blue wisps trailing at the ankles - fitting `gemstone` - centre `amethyst_shard`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          allay_wisps
    anchor:        spurs
    namespace:     armorpieces_village
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\village\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\village\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Allay Wisps",
                           fittings: ["armorpieces:gemstone"],
                           static: true,
                           recipe: { centre: "minecraft:amethyst_shard", craftable: true } }

**Fittings:** one, **`armorpieces:gemstone`**, masked. The reply will say a `part_gemstone` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Allay blue - pale and cold, lit from inside is a colour that must not change with the armor.
**Effects: none. Loot: none — leave `loot` out of your call entirely.** The recipe above is the only way this piece is had; `minecraft:amethyst_shard` is confirmed free against every template centre in the project.

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

The **ring** carries no static and no mask. It is the anklet, it is metal, and it is this piece's material surface.

## The rig, in Blockbench coordinates

    left leg box            x -4 .. 0     y 0 .. 12     z -2 .. 2
    leggings shell (+1)     x -5 .. 1     y -1 .. 13    z -3 .. 3
    the `spurs` anchor       (-1.9, 2, 2)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-1.9, 2, 2)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** `ominous_banner` found this out on 2026-09-10: a
`back` piece gets no `past helmet` line at all, because the helmet is not its shell. So the check
will **not** warn you about running into a shell that belongs to a different armor piece. Every
coordinate below already clears the ones that matter; do not move them toward another shell.

## Shape

Two small allay-blue motes trailing behind the ankle on an anklet, as if something is following you. They are the piece that makes the pack's name true - you freed the allay - and they are the pack's one glowing thing, so they must read as light rather than as beads.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **ring** — the anklet the wisps trail from:

        x -4.15 .. 0.35    y 1.15 .. 2.45    z -3.15 .. 3.35

- **wisp_near** — the nearer, lower mote:

        x -2.85 .. -1.55    y 2.65 .. 4.15    z 3.55 .. 4.85

- **wisp_far** — the further, higher mote:

        x -1.45 .. -0.35    y 3.85 .. 5.15    z 4.35 .. 5.55

**3 cubes in total is the budget**, and there is no 4th.

**Envelope budget.** Stay inside `x -4.2 .. 0.4, y 1.1 .. 5.6, z -3.2 .. 5.6`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.3 .. 2.3      y  6.4 .. 10.9      z  -3.2 .. 5.6

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `4.15`, so the pair spans **8.3**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `rabbit_feet` | x -2.90..-0.90, y 0.76..8.40, z 2.95..6.59 | the closest match - something small trailing behind the heel |
| `anklets` | x -5.40..1.40, y 0.95..2.20, z -3.52..3.80 | the precedent for your ring, at your exact height |
| `talons` | x -3.40..-0.40, y 0.22..3.50, z 3.00..7.81 | reaches further back than you do |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

wisps: base **215**, `up` **245** - as near white as the ramp goes, because they are light. ring: base **150**, `up` **185**.

**They cannot actually glow.** The mod has no glow sheet, so a bright value on the master is the whole trick. Do not try anything else.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `wisp_near`, `wisp_far`: base `#5fa8e0`, `up` `#a8d8f5` — allay blue - pale and cold, lit from inside

**Mask `part_gemstone`** — flat **140**, on `wisp_near`, `wisp_far`. 140 is the value every mask in this project
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
