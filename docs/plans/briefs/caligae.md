# Brief: Caligae

A piece of **Armor Pieces: Antiquity** (`armorpieces_antiquity`) — bronze and red leather - Greece and Rome, the hoplite and the legionary, every piece a thing with a Latin or Greek name.

From the `spurs` row of the Antiquity table:

> `caligae` - a leather heel cup with two straps round the ankle and a lace up the outside - fitting `inlay` - centre `leather_boots`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          caligae
    anchor:        spurs
    namespace:     armorpieces_antiquity
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\antiquity\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\antiquity\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Caligae",
                           fittings: ["armorpieces:inlay"],
                           static: true,
                           recipe: { centre: "minecraft:leather_boots", craftable: true } }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Dark leather is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `legion` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:leather_boots` is confirmed free against every
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

The two **straps** carry no static. They are masked `inlay` (leather - dyed matter) and are the piece's material surface until a player dyes them; the rest is static leather.

## The rig, in Blockbench coordinates

    left leg box            x -3.9 .. 0.1   y 0 .. 12       z -2 .. 2
    leggings shell (+0.4)   x -4.3 .. 0.5   y -0.4 .. 12.4  z -2.4 .. 2.4
    boots shell (+0.9)      x -4.8 .. 1.0   y -0.9 .. 12.9  z -2.9 .. 2.9
    the `spurs` anchor       (-1.9, 2, 2)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-1.9, 2, 2)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

The soldier's sandals, seen at the heel: a leather cup round the back of the heel, two narrow straps going round the back of the ankle one above the other, a lace running up the outside of the ankle over them, and a knot at the back where the top strap ties. All leather.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **heel** — the leather cup round the back of the heel:

        x -5.12 .. 1.23    y 0.37 .. 1.72    z 2.95 .. 3.49

- **strap_a** — the lower ankle strap, round the back:

        x -5.13 .. 1.33    y 1.79 .. 2.33    z 0.37 .. 3.39

- **strap_b** — the upper strap:

        x -5.13 .. 1.33    y 2.87 .. 3.42    z 0.37 .. 3.39

- **lace** — the lace up the outside of the ankle:

        x -5.41 .. -5.13    y 0.37 .. 3.62    z 1.17 .. 1.83

- **knot** — the knot at the back:

        x -2.42 .. -1.37    y 3.42 .. 4.05    z 3.39 .. 3.97

**5 cubes in total is the budget**, and there is no 6th.

**Envelope budget.** Stay inside `x -5.5 .. 1.4, y 0.3 .. 4.1, z 0.3 .. 4.1`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -3.3 .. 3.6      y  7.9 .. 11.7      z  0.3 .. 4.1

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `5.41`, so the pair spans **10.82**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `anklets` | x -5.40..1.40, y 0.95..2.20, z -3.52..3.80 | the mod's anklet - a strap round the ankle at your height |
| `waraji` | x -5.20..1.40, y 0.30..2.80, z 0.50..4.40 | the Samurai's sandal, built in this batch - the same idea in straw, never worn with you |
| `ocreae (greaves)` | x -5.10..0.50, y 0.30..4.20, z -4.00..-2.30 | your own pack's greaves, built in this batch, all in FRONT of the leg where you are all behind and beside |
| `pteruges (tassets)` | x -5.10..0.60, y 6.20..12.20, z -3.50..3.00 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `gorgon_cops (knees)` | x -3.60..-0.20, y 4.30..7.30, z -4.20..-2.80 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

heel, lace and knot: base **70**, `south` **85**. straps: base **130**, `south` **155**, `up` **145**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `heel`, `lace`, `knot`: base `#4a2f1e`, `up` `#5f3f2a` — dark leather - the straps

**Mask `part_inlay`** — flat **140**, on `strap_a`, `strap_b`. 140 is the value every mask in this project
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

