# Brief: Ammon Horns

A piece of **Armor Pieces: Antiquity** (`armorpieces_antiquity`) — bronze and red leather - Greece and Rome, the hoplite and the legionary, every piece a thing with a Latin or Greek name.

From the `horns` row of the Antiquity table:

> `ammon_horns` - a ram's horn curling round each temple in a C, opening forward - fitting `guard` - centre `cooked_mutton`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          ammon_horns
    anchor:        horns
    namespace:     armorpieces_antiquity
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\antiquity\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\antiquity\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Ammon Horns",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:cooked_mutton", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Horn is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `legion` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:cooked_mutton` is confirmed free against every
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

The **base** carries no static. It is masked `guard` and is the piece's whole material surface; the horn is static.

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

The horns of Ammon that Alexander wore on his coins: a ram's horn on each temple, curling in a C - from the temple up and back, down the back of the ear, forward along the jaw, and the tip curling up at the front. Four straight cubes make the curl; no rotation. Ridged horn, cream, with a small bronze base plate where it meets the helmet.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **base** — the bronze base plate on the temple:

        x -5.47 .. -5.07    y 28.47 .. 30.81    z -1.03 .. 1.33

- **seg_a** — the top of the curl, going back from the temple:

        x -6.07 .. -5.13    y 30.03 .. 31.37    z -0.53 .. 2.67

- **seg_b** — the back of the curl, coming down behind the ear:

        x -6.13 .. -5.07    y 27.37 .. 30.03    z 1.77 .. 2.97

- **seg_c** — the bottom of the curl, coming forward along the jaw:

        x -6.07 .. -5.13    y 26.57 .. 27.37    z -0.83 .. 2.67

- **tip** — the tip, curling up at the front:

        x -5.97 .. -5.23    y 27.37 .. 28.73    z -1.42 .. -0.53

**5 cubes in total is the budget**, and there is no 6th.

**Envelope budget.** Stay inside `x -6.2 .. -5.0, y 26.5 .. 31.5, z -1.5 .. 3.1`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the head bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  5.0 .. 6.2      y  -7.5 .. -2.5      z  -1.5 .. 3.1

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `6.13`, so the pair spans **12.26** — the check compares that against the **18** the shoulders span, and you are inside it. Report the span.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `horns` | x -8.96..-3.61, y 29.00..38.36, z -2.00..2.00 | the Wild Hunt's horns - straight and tall where yours curl tight to the head |
| `dragon_horns` | x -6.54..-4.00, y 28.20..36.93, z -1.00..2.42 | a pack horn at your depth, going up where you go round |
| `transverse_crest (crest)` | x -7.20..7.20, y 33.00..37.60, z -1.00..1.00 | your own pack's crest, built in this batch, starting at y 33.07 - your curl tops out at 31.37, clear |
| `corinthian_face (brow)` | x -4.20..4.20, y 24.30..30.90, z -5.90..-5.00 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

horn (segments and tip): base **175**, `west` **195**, `down` **140**. base: base **140**, `west` **175**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `seg_a`, `seg_b`, `seg_c`, `tip`: base `#cfc2a0`, `up` `#e3d8bb` — horn - a ram's horn, ridged cream

**Mask `part_guard`** — flat **140**, on `base`. 140 is the value every mask in this project
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

