# Brief: Daisho

A piece of **Armor Pieces: Samurai** (`armorpieces_samurai`) — black lacquer over iron, red odoshi lacing and gilt fittings - the armor of a daimyo, every piece a named part of a real suit.

From the `belt` row of the Samurai table:

> `daisho` - an obi round the waist with the two swords thrust through it at the left hip - fitting `inlay` - centre `golden_sword`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          daisho
    anchor:        belt
    namespace:     armorpieces_samurai
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\samurai\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\samurai\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Daisho",
                           fittings: ["armorpieces:inlay"],
                           static: true,
                           recipe: { centre: "minecraft:golden_sword", craftable: true } }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Undyed silk is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `daimyo` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:golden_sword` is confirmed free against every
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

The **hilts** carry no static and no mask; they are the piece's material surface (a wrapped hilt with metal fittings, answering the trim). The **obi** is static cream by default AND masked `inlay`, so a player dyes the sash; the scabbards are static black.

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

The pair of swords: a broad cream silk sash round the waist, and at the left hip two black lacquered scabbards thrust through it horizontally, pointing backwards - the long katana below, the shorter wakizashi above - with their wrapped hilts standing out forward of the hip. Seen from the front you see two hilts; from the side, two scabbards.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **obi** — the silk sash round the waist:

        x -5.33 .. 5.33    y 12.67 .. 14.33    z -3.33 .. 3.33

- **katana** — the long scabbard, along the left side pointing back:

        x -6.13 .. -5.33    y 13.23 .. 13.87    z -3.03 .. 6.87

- **wakizashi** — the short scabbard above it:

        x -6.03 .. -5.33    y 13.97 .. 14.47    z -2.03 .. 4.03

- **hilt_k** — the katana's wrapped hilt, forward of the hip:

        x -6.07 .. -5.39    y 13.17 .. 13.93    z -5.57 .. -3.03

- **hilt_w** — the wakizashi's hilt:

        x -5.97 .. -5.39    y 13.97 .. 14.53    z -3.83 .. -2.03

**5 cubes in total is the budget**, and there is no 6th.

**Envelope budget.** Stay inside `x -6.2 .. 5.4, y 12.6 .. 14.6, z -5.7 .. 7.0`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the body bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -5.4 .. 6.2      y  9.4 .. 11.4      z  -5.7 .. 7.0

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `dragon_tail` | x -5.40..5.40, y 10.45..14.90, z -2.95..6.21 | the precedent for something running off the BACK of the belt; your katana reaches 0.7 further |
| `sash` | x -7.25..6.00, y 5.27..16.50, z -5.00..4.00 | the mod's own sash - the precedent for reaching out to x -7 at the hip |
| `pinions (back)` | x -7.78..8.32, y 13.68..23.29, z 2.00..6.29 | worn WITH you; its box crosses your katana's tail in a hull test - an OVERLAP `-`, not a `!` |
| `sashimono (back)` | x -3.90..3.90, y 19.50..40.00, z 1.60..7.50 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `nodowa (collar)` | x -4.70..4.70, y 18.50..24.70, z -4.10..-3.10 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

obi: base **200**, `up` **225**, `down` **170**. scabbards: base **55**, `up` **75**, `west` **70**. hilts: base **120**, `north` **150**.

**The obi is one cube right round the body.** Its inner volume is inside the chestplate; its six faces are the sash, the way `girdle` is built.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `obi`: base `#e8dcc2`, `up` `#f4ecd8` — undyed silk - the obi's own cream
- `katana`, `wakizashi`: base `#1a1614`, `up` `#2e2724` — lacquer black - the suit's own black, with a warm brown in the light

**Mask `part_inlay`** — flat **140**, on `obi`. 140 is the value every mask in this project
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

