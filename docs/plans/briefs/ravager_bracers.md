# Brief: Ravager Bracers

A piece of **Armor Pieces: Hero of the Village** (`armorpieces_village`) — iron armor with emerald hardware, the
raid worn by the person who won it.

From the `vambraces` row of the Hero of the Village table:

> `ravager_bracers` - the ravager's hide banded over the forearms - fitting `guard` - found in a chest

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          ravager_bracers
    anchor:        vambraces
    namespace:     armorpieces_village
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\village\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\village\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Ravager Bracers",
                           fittings: ["armorpieces:guard"],
                           static: true }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Ravager hide - dull brown, no shine is a colour that must not change with the armor.
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

The two **bands** and the **studs** carry no static. They are masked `guard`, so they answer the trim while the fitting is empty and take the metal when it is filled.

## The rig, in Blockbench coordinates

    left arm box            x -8 .. -4    y 12 .. 24    z -2 .. 2
    sleeve shell (+1)       x -9 .. -3    y 11 .. 25    z -3 .. 3
    the `vambraces` anchor       (-6, 16, 0)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-6, 16, 0)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** `ominous_banner` found this out on 2026-09-10: a
`back` piece gets no `past helmet` line at all, because the helmet is not its shell. So the check
will **not** warn you about running into a shell that belongs to a different armor piece. Every
coordinate below already clears the ones that matter; do not move them toward another shell.

## Shape

Thick ravager hide wrapped round the forearm and pinned by two metal bands. It reads as scavenged, not tailored - the hide is the subject and the bands merely hold it on.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **hide** — the hide wrap round the forearm:

        x -9.15 .. -2.85    y 13.15 .. 17.85    z -3.15 .. 3.15

- **band_up** — the upper retaining band:

        x -9.35 .. -2.65    y 17.85 .. 18.95    z -3.35 .. 3.35

- **band_lo** — the lower retaining band:

        x -9.35 .. -2.65    y 12.15 .. 13.25    z -3.35 .. 3.35

- **studs** — a short row of studs on the outboard face:

        x -9.55 .. -9.15    y 14.15 .. 16.85    z -1.55 .. 1.55

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -9.6 .. -2.6, y 12.1 .. 19.0, z -3.4 .. 3.4`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the arm bone's pivot at Blockbench `(-5, 22, 0)` - **not** the top of the arm box. For this socket:

    check_x = -5 - bb_x        check_y = 22 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.4 .. 4.6      y  3.0 .. 9.9      z  -3.4 .. 3.4

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `9.55`, so the pair spans **19.1**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the arms are already outboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `blaze_bracers` | x -9.45..-2.65, y 15.15..20.45, z -3.35..3.35 | a pack piece on this socket at your exact width |
| `cuffs` | x -10.07..-1.93, y 12.60..16.97, z -4.07..4.07 | wider and deeper than you |
| `wraps` | x -9.56..-3.75, y 12.10..18.25, z -3.95..3.49 | your height twin |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

hide: base **115**, `west` **135** (the outboard face catches light), `down` **85**. bands and studs: base **160**, `up` **195**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `hide`: base `#6b5d4e`, `up` `#877866` — ravager hide - dull brown, no shine

**Mask `part_guard`** — flat **140**, on `band_up`, `band_lo`, `studs`. 140 is the value every mask in this project
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
