# Brief: Nodowa

A piece of **Armor Pieces: Samurai** (`armorpieces_samurai`) — black lacquer over iron, red odoshi lacing and gilt fittings - the armor of a daimyo, every piece a named part of a real suit.

From the `collar` row of the Samurai table:

> `nodowa` - a collar band with a two-tier lamellar bib hanging over the upper chest - fitting `inlay` - centre `iron_chestplate`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          nodowa
    anchor:        collar
    namespace:     armorpieces_samurai
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\samurai\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\samurai\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Nodowa",
                           fittings: ["armorpieces:inlay"],
                           static: true,
                           recipe: { centre: "minecraft:iron_chestplate", craftable: true } }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Lacquer black is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `daimyo` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:iron_chestplate` is confirmed free against every
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

The **collar** carries no static and no mask; it is the piece's material surface. The **lace** is static red by default AND masked `inlay`; the bib tiers are static and never answer the trim.

## The rig, in Blockbench coordinates

    body box                x -4 .. 4       y 12 .. 24      z -2 .. 2
    chestplate shell (+1)   x -5 .. 5       y 11 .. 25      z -3 .. 3
    leggings shell (+0.5)   x -4.5 .. 4.5   y 11.5 .. 24.5  z -2.5 .. 2.5
    the `collar` anchor       (0, 23, -2)

Front is **negative z**. This socket is not mirrored: build the whole piece once.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(0, 23, -2)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

The throat guard: an iron collar band round the base of the neck, and a bib of black lacquered lamellae in two tiers hanging from it over the upper chest, the tiers separated by a row of red lacing that stands a hair proud. Flat against the chest.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **collar** — the iron collar band at the throat:

        x -4.64 .. 4.64    y 23.12 .. 24.57    z -3.90 .. -3.16

- **bib_up** — the upper tier of the bib:

        x -3.73 .. 3.73    y 21.03 .. 23.12    z -3.93 .. -3.17

- **lace** — the row of lacing between the tiers:

        x -3.57 .. 3.57    y 20.46 .. 21.03    z -3.98 .. -3.17

- **bib_lo** — the lower tier, a little narrower:

        x -3.23 .. 3.23    y 18.63 .. 20.46    z -3.90 .. -3.17

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -4.7 .. 4.7, y 18.5 .. 24.7, z -4.1 .. -3.1`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the body bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -4.7 .. 4.7      y  -0.7 .. 5.5      z  -4.1 .. -3.1

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `honeycomb_gorget` | x -4.73..4.73, y 17.53..24.47, z -3.93..-3.16 | the Hive's gorget - almost your envelope exactly |
| `wither_ribs` | x -4.28..4.28, y 17.02..23.20, z -3.95..-3.25 | the Nether's chest piece at your depth |
| `gorget` | x -6.50..6.50, y 19.50..25.25, z -3.75..0.75 | the mod's own gorget, which wraps the shoulders where you stay flat on the chest |
| `sashimono (back)` | x -3.90..3.90, y 19.50..40.00, z 1.60..7.50 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `daisho (belt)` | x -6.20..5.40, y 12.60..14.60, z -5.70..7.00 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

bib tiers: base **60**, `north` **80**, `down` **40**. lace: base **150**, `north` **170**. collar: base **130**, `up` **165**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `bib_up`, `bib_lo`: base `#1a1614`, `up` `#2e2724` — lacquer black - the suit's own black, with a warm brown in the light
- `lace`: base `#b3202a`, `up` `#d8323a` — odoshi red - the lacing cord's own red

**Mask `part_inlay`** — flat **140**, on `lace`. 140 is the value every mask in this project
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

