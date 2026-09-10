# Brief: Ravager Horns

A piece of **Armor Pieces: Hero of the Village** (`armorpieces_village`) — iron armor with emerald hardware, the
raid worn by the person who won it.

From the `horns` row of the Hero of the Village table:

> `ravager_horns` - the two chipped, down-curved horns - fitting `guard` - found in a chest

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          ravager_horns
    anchor:        horns
    namespace:     armorpieces_village
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\village\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\village\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Ravager Horns",
                           fittings: ["armorpieces:guard"],
                           static: true }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Ravager horn - pale grey-brown, dead keratin is a colour that must not change with the armor.
**Effects: none. Loot: none — leave `loot` out of your call entirely.** This piece is found in a chest rather than crafted, but the pack's loot group does not exist yet and a session must not invent one — I add it afterwards in the repo half. **Do not add a recipe either.**

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

The **mount** carries no static. It is masked `guard`, so it answers the trim while the fitting is empty and takes the metal when a player fills it.

## The rig, in Blockbench coordinates

    head box                x -4 .. 4     y 24 .. 32    z -4 .. 4
    helmet shell (+1)       x -5 .. 5     y 23 .. 33    z -5 .. 5
    the `horns` anchor       (-4, 29, 0)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-4, 29, 0)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** `ominous_banner` found this out on 2026-09-10: a
`back` piece gets no `past helmet` line at all, because the helmet is not its shell. So the check
will **not** warn you about running into a shell that belongs to a different armor piece. Every
coordinate below already clears the ones that matter; do not move them toward another shell.

## Shape

A ravager's horns: thick at the temple, curving down and outward past the jaw, blunt and chipped rather than sharp. They are heavy, not elegant - the opposite of `dragon_horns`, which sweep up and back.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **mount** — the banded cap at the temple, where the horn is strapped on:

        x -4.85 .. -3.55    y 28.15 .. 30.15    z -1.15 .. 1.15

- **horn1** — the thick first segment, already stepping out and down:

        x -6.05 .. -4.65    y 27.05 .. 29.35    z -0.95 .. 0.95

- **horn2** — the middle segment:

        x -7.05 .. -5.85    y 25.35 .. 27.45    z -0.75 .. 0.75

- **horn3** — the blunt chipped tip:

        x -7.75 .. -6.85    y 23.95 .. 25.75    z -0.55 .. 0.55

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -7.8 .. -3.5, y 23.9 .. 30.2, z -1.2 .. 1.2`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the head bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  3.5 .. 7.8      y  -6.2 .. 0.1      z  -1.2 .. 1.2

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `7.75`, so the pair spans **15.5** — the check compares that against the **18** the shoulders span, and you are inside it. Report the span.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `tusks` | x -6.22..-4.35, y 25.40..29.03, z -3.18..0.50 | the closest thing to this piece; you reach 1.5 further out and 1.4 lower |
| `horns` | x -8.96..-3.61, y 29.00..38.36, z -2.00..2.00 | goes UP where you go down - no conflict, but it is the piece yours must not be mistaken for |
| `cheek_guards` | x -6.18..-4.65, y 24.43..29.40, z -2.40..1.60 | shares your height band exactly; never worn with you (same socket) |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

horns: base **135**, `up` **170**, `down` **95**, and the tip cube 10 lower all round so the horn darkens toward the end. mount: base **150**, `up` **185**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `horn1`, `horn2`, `horn3`: base `#6b6358`, `up` `#857c6e` — ravager horn - pale grey-brown, dead keratin

**Mask `part_guard`** — flat **140**, on `mount`. 140 is the value every mask in this project
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
