# Brief: Kuwagata

A piece of **Armor Pieces: Samurai** (`armorpieces_samurai`) — black lacquer over iron, red odoshi lacing and gilt fittings - the armor of a daimyo, every piece a named part of a real suit.

From the `horns` row of the Samurai table:

> `kuwagata` - a flat gilt blade at each temple, sweeping up and forward - fitting `guard` - centre `golden_hoe`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          kuwagata
    anchor:        horns
    namespace:     armorpieces_samurai
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\samurai\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\samurai\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Kuwagata",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:golden_hoe", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Gilt is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `daimyo` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:golden_hoe` is confirmed free against every
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

The **foot** carries no static and no mask; it is the piece's material surface. The **blade** and **tip** are static gold by default AND masked `guard`.

## The rig, in Blockbench coordinates

    head box                x -4 .. 4       y 24 .. 32      z -4 .. 4
    helmet shell (+1)       x -5 .. 5       y 23 .. 33      z -5 .. 5
    the `horns` anchor       (-4, 29, 0)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-4, 29, 0)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

The kabuto's antler-blades: a thin flat gilt blade standing up from the front of each temple, leaning forward as it rises, with a small iron foot where it meets the helmet. Thin in x, tall in y, so from the front it reads as two gold lines framing the maedate.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **foot** — the iron foot on the temple, where the blade is fixed:

        x -5.57 .. -5.07    y 29.37 .. 30.43    z -3.45 .. -1.88

- **blade** — the blade rising from the foot:

        x -5.47 .. -5.07    y 30.43 .. 36.25    z -3.13 .. -2.27

- **tip** — the tip, leaning forward at the top:

        x -5.43 .. -5.12    y 36.25 .. 38.13    z -3.57 .. -2.63

**3 cubes in total is the budget**, and there is no 4th.

**Envelope budget.** Stay inside `x -5.7 .. -5.0, y 29.3 .. 38.2, z -3.7 .. -1.8`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the head bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  5.0 .. 5.7      y  -14.2 .. -5.3      z  -3.7 .. -1.8

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `5.57`, so the pair spans **11.14** — the check compares that against the **18** the shoulders span, and you are inside it. Report the span.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `helm_wings` | x -6.40..-5.30, y 31.14..38.37, z -0.74..6.58 | the mod's wings on this socket - the same height as you, but on the BACK half of the temple where you are on the front |
| `dragon_horns` | x -6.54..-4.00, y 28.20..36.93, z -1.00..2.42 | a pack horn at your height |
| `coronet (brow)` | x -6.00..6.00, y 29.00..33.21, z -6.18..-2.25 | a brow piece whose box your foot and blade cross in a hull test - an OVERLAP `-`, never a `!` |
| `maedate (crest)` | x -3.60..3.60, y 33.00..38.60, z -4.10..-1.90 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `mempo (brow)` | x -4.00..4.00, y 22.50..28.00, z -6.50..-4.90 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

blade and tip: base **170**, `west` **200** (the outboard face), `north` **190**. foot: base **115**, `up` **145**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `blade`, `tip`: base `#d4a83a`, `up` `#f1cc5a` — gilt - the maedate's gold leaf

**Mask `part_guard`** — flat **140**, on `blade`, `tip`. 140 is the value every mask in this project
uses.

## Done when

- [ ] The check is clean, or every `!` left standing is one this brief allows.
- [ ] Envelope inside the budget above, **reported in the check's frame**.
- [ ] Pair span reported.
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

