# Brief: Sode

A piece of **Armor Pieces: Samurai** (`armorpieces_samurai`) — black lacquer over iron, red odoshi lacing and gilt fittings - the armor of a daimyo, every piece a named part of a real suit.

From the `pauldrons` row of the Samurai table:

> `sode` - a big flat lacquered plate hanging outboard of each shoulder, laced in red - fitting `inlay` - centre `black_dye`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          sode
    anchor:        pauldrons
    namespace:     armorpieces_samurai
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\samurai\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\samurai\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Sode",
                           fittings: ["armorpieces:inlay"],
                           static: true,
                           recipe: { centre: "minecraft:black_dye", craftable: true } }

**Fittings:** one, **`armorpieces:inlay`**, masked. The reply will say a `part_inlay` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Lacquer black is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `daimyo` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:black_dye` is confirmed free against every
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

The **cap** carries no static and no mask; it is the piece's material surface, iron answering the trim. The **lacing** is static red by default AND masked `inlay`, so a player can re-dye it; the plate is static and never answers the trim.

## The rig, in Blockbench coordinates

    left arm box            x -8 .. -4      y 12 .. 24      z -2 .. 2
    sleeve shell (+1)       x -9 .. -3      y 11 .. 25      z -3 .. 3
    the `pauldrons` anchor       (-6, 22, 0)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-6, 22, 0)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

The samurai's shoulder guard: an iron cap plate lying on top of the shoulder, and a large flat rectangular plate of black lacquered lamellae hanging straight down from it on the outside of the arm, with two rows of red lacing standing proud on its outer face. It is a flat hanging slab, not a curved pauldron.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **cap** — the iron cap plate on top of the shoulder:

        x -9.63 .. -4.37    y 25.07 .. 25.83    z -3.31 .. 3.31

- **plate** — the lamellar plate hanging outboard of the arm:

        x -10.37 .. -9.63    y 18.37 .. 25.07    z -3.31 .. 3.31

- **lace_up** — the upper row of lacing on the plate's outer face:

        x -10.57 .. -10.37    y 22.43 .. 23.07    z -3.03 .. 3.02

- **lace_lo** — the lower row:

        x -10.57 .. -10.37    y 20.03 .. 20.67    z -3.03 .. 3.02

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -10.7 .. -4.3, y 18.3 .. 25.9, z -3.4 .. 3.4`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the arm bone's pivot at Blockbench `(-5, 22, 0)` - **not** the top of the arm box. For this socket:

    check_x = -5 - bb_x        check_y = 22 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -0.7 .. 5.7      y  -3.9 .. 3.7      z  -3.4 .. 3.4

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `10.57`, so the pair spans **21.14**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the arms are already outboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `lames` | x -10.85..-7.20, y 19.05..25.70, z -3.10..3.10 | the mod's own shoulder lames - the shape you are closest to, and reaching further out |
| `spaulders` | x -10.33..-5.75, y 20.37..25.50, z -3.50..3.50 | a plainer mod pauldron at your depth |
| `blaze_bracers (vambraces)` | x -9.45..-2.65, y 15.15..20.45, z -3.35..3.35 | the tallest vambrace, worn WITH you: it ends at x -9.45 and your plate starts at -9.63, so the two never meet |
| `kote (vambraces)` | x -9.80..-2.60, y 12.30..18.40, z -3.40..3.40 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

plate: base **60**, `west` **80** (the outboard face has the gloss), `down` **40**. lacing: base **150**, `west` **170**. cap: base **130**, `up` **165**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `plate`: base `#1a1614`, `up` `#2e2724` — lacquer black - the suit's own black, with a warm brown in the light
- `lace_up`, `lace_lo`: base `#b3202a`, `up` `#d8323a` — odoshi red - the lacing cord's own red

**Mask `part_inlay`** — flat **140**, on `lace_up`, `lace_lo`. 140 is the value every mask in this project
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

