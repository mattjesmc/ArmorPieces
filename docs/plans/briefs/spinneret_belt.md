# Brief: Spinneret Belt

A piece of **Armor Pieces: The Hive** (`armorpieces_hive`) — netherite and lime over lamellar - black insect chitin on dark metal hardware, with the lime of the membrane and the gold of honey as the only light in it.

From the `belt` row of the Hive table:

> `spinneret_belt` - a chitin belt with a spider's spinnerets at the back - fitting `guard` - centre `cobweb`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          spinneret_belt
    anchor:        belt
    namespace:     armorpieces_hive
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\hive\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\hive\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Spinneret Belt",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:cobweb", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Chitin black is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `hive` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:cobweb` is confirmed free against every
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

The **clasp** carries no static. It is masked `guard` and is the piece's whole material surface.

## The rig, in Blockbench coordinates

    body box                x -4 .. 4       y 12 .. 24      z -2 .. 2
    chestplate shell (+1)   x -5 .. 5       y 11 .. 25      z -3 .. 3
    leggings shell (+0.5)   x -4.5 .. 4.5   y 11.5 .. 24.5  z -2.5 .. 2.5
    the `belt` anchor       (0, 14, 0)

Front is **negative z**. This socket is not mirrored: build the whole piece once.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(0, 14, 0)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

A belt of black chitin round the waist with a dark metal clasp at the front, and at the back a spider's spinneret - a blunt nub - with a single strand of pale silk hanging from it to the hip. Seen from the front it is a plain black belt; the joke is behind you.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **band** — the chitin band round the waist:

        x -5.27 .. 5.27    y 12.72 .. 14.27    z -3.27 .. 3.27

- **clasp** — the metal clasp at the front:

        x -1.13 .. 1.13    y 12.53 .. 14.47    z -3.73 .. -3.27

- **spinneret** — the spinneret nub at the back:

        x -1.47 .. 1.47    y 12.33 .. 13.66    z 3.27 .. 4.70

- **silk** — the strand of silk hanging from it:

        x -0.33 .. 0.33    y 8.13 .. 12.33    z 3.73 .. 4.27

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -5.4 .. 5.4, y 8.0 .. 14.6, z -3.8 .. 4.8`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the body bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -5.4 .. 5.4      y  9.4 .. 16.0      z  -3.8 .. 4.8

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `brute_belt` | x -5.35..5.35, y 11.35..15.35, z -3.88..3.35 | a pack belt at your width; the precedent for a clasp standing proud at the front |
| `dragon_tail` | x -5.40..5.40, y 10.45..14.90, z -2.95..6.21 | the precedent for something hanging off the BACK of the belt; yours is shorter |
| `carapace (back)` | x -4.75..4.75, y 15.60..24.60, z 3.10..5.25 | your own pack's carapace, worn WITH you, ending at y 15.60 - your spinneret's top is 13.66, clear by 1.9 |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

band and spinneret: base **55**, `up` **75**, `down` **40**. silk: base **220**. clasp: base **140**, `north` **175**.

**The band is one cube right round the body.** Its inner volume is inside the chestplate; its six faces are the belt, the way `girdle` is built.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `band`, `spinneret`: base `#16100e`, `up` `#341911` — chitin black - the bee's own black
- `silk`: base `#e6e6e6`, `up` `#f8f8f8` — silk - near white, the string item's own colour

**Mask `part_guard`** — flat **140**, on `clasp`. 140 is the value every mask in this project
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
