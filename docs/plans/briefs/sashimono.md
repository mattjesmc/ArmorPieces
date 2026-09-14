# Brief: Sashimono

A piece of **Armor Pieces: Samurai** (`armorpieces_samurai`) — black lacquer over iron, red odoshi lacing and gilt fittings - the armor of a daimyo, every piece a named part of a real suit.

From the `back` row of the Samurai table:

> `sashimono` - a banner on a pole standing up the back, above the head - fitting `banner` + `guard` - centre `red_banner`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          sashimono
    anchor:        back
    namespace:     armorpieces_samurai
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\samurai\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\samurai\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Sashimono",
                           fittings: ["armorpieces:banner", "armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:red_banner", craftable: true } }

**Fittings: two, and they are different kinds.**

- `armorpieces:banner` is **not a mask**. It is rendered by the game's own banner renderer onto the
  cubes in a bone that must be named exactly **`banner`**, off the `shield` sheet. **No
  `part_banner.png` is created and none should be** — if the reply lists one, stop and tell me.
- `armorpieces:guard` **is** a mask, and `part_guard` will be created for you to paint.
**Static layer: yes.** `static_created: true` is correct. Lacquer black is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `daimyo` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:red_banner` is confirmed free against every
template centre in the project.

So this piece has **three sheets**: the greyscale master `part`, the colour layer `part_static`,
and the greyscale mask `part_guard`. There is no fourth; the banner fitting paints nothing of its own.

## The three surfaces, and which cube gets which

A piece is drawn from three sheets and **they stack** — `recolour(master, static, palette)`, then
one `applyMask` per fitting:

    MATERIAL   `part`            greyscale master, recoloured through the TRIM material's ramp
    STATIC     `part_static`     real colour, painted OVER the recoloured master
    FITTING    `part_guard`     greyscale mask over both, filled by the PLAYER

**Static hides material** — a static cube stops answering the trim forever. **An empty fitting costs
nothing** — its mask is not read until a player fills it, so a masked cube still answers the trim
until then, and a static layer *under* a mask is the default look with the fitting as an override.

The **harness** and **crossbar** carry no static; they are masked `guard` and answer the trim until a player fills the fitting. The **pole** is static black lacquer. The **cloth** is neither: plain cloth on the master, and the banner a player fits paints it.

## The rig, in Blockbench coordinates

    body box                x -4 .. 4       y 12 .. 24      z -2 .. 2
    chestplate shell (+1)   x -5 .. 5       y 11 .. 25      z -3 .. 3
    leggings shell (+0.5)   x -4.5 .. 4.5   y 11.5 .. 24.5  z -2.5 .. 2.5
    the `back` anchor       (0, 22, 2)

Front is **negative z**. This socket is not mirrored: build the whole piece once.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(0, 22, 2)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

The samurai's back banner: a laced harness across the upper back, a black lacquered pole standing straight up from it to well above the head, a short iron crossbar at the top, and the banner cloth hanging from the crossbar. It stands higher than the Village's raid banner and the cloth hangs from the bar rather than flying from the pole.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `mount` at the anchor. Rename the starter bone `main` to **`mount`** (not `base` — this piece
  follows the mod's own banner convention); never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **harness** — the harness across the upper back, starting inside the chestplate and coming out through it:

        x -1.85 .. 1.87    y 19.57 .. 22.43    z 1.73 .. 5.43

- **pole** — the pole, standing straight up past the head:

        x -0.57 .. 0.53    y 20.11 .. 39.87    z 5.23 .. 6.13

- **crossbar** — the crossbar at the top, from which the cloth hangs:

        x -3.77 .. 3.77    y 38.83 .. 39.37    z 6.23 .. 7.43

- **cloth** — the banner cloth - in the bone named `banner`; 7 x 12 x 1, fixed:

        x -3.50 .. 3.50    y 26.83 .. 38.83    z 6.33 .. 7.33

**The cloth goes in a second bone named exactly `banner`, a child of `mount`.** The banner fitting
binds to a bone of that name and finds nothing if it is called anything else. **The cloth is 7 wide x 12
tall x 1 deep and those three numbers are not yours to change** — they are the mod's own banner cloth,
and the banner renderer maps the shield sheet onto exactly that shape. Every other cube goes in `mount`.

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -3.9 .. 3.9, y 19.5 .. 40.0, z 1.6 .. 7.5`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the body bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -3.9 .. 3.9      y  -16.0 .. 4.5      z  1.6 .. 7.5

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `ominous_banner` | x -3.50..3.50, y 19.55..38.35, z 1.75..7.35 | the Village's raid banner, the precedent for a pole above the head - you go 1.5 higher, and the rig took it without complaint |
| `banner` | x -3.50..3.50, y 8.50..21.50, z 1.75..6.25 | the mod's own banner, mounted LOW on the back; you are its opposite |
| `ruff (collar)` | x -5.88..5.88, y 25.10..26.55, z -5.88..5.88 | the only bone-mate that rises above the shoulders, and it stops at y 26.55 - below your cloth |
| `nodowa (collar)` | x -4.70..4.70, y 18.50..24.70, z -4.10..-3.10 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `daisho (belt)` | x -6.20..5.40, y 12.60..14.60, z -5.70..7.00 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

pole: base **50**, `up` **70**. harness: base **130**, `up` **170**, `down` **80**. crossbar: base **140**, `up` **175**. cloth: flat **160**, all faces.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `pole`: base `#1a1614`, `up` `#2e2724` — lacquer black - the suit's own black, with a warm brown in the light

**Mask `part_guard`** — flat **140**, on `crossbar`, `harness`. 140 is the value every mask in this project
uses. **Do not mask the cloth** — the banner fitting owns it — and paint the cloth flat **160** on
the master anyway: an unpainted face renders as a hole, and the renderer covers it once a banner is fitted.

## Done when

- [ ] The check is clean, or every `!` left standing is one this brief allows.
- [ ] Envelope inside the budget above, **reported in the check's frame**.
- [ ] All three sheets painted — master, `part_static`, `part_guard`. No `part_banner` sheet exists.
- [ ] The bone holding the cloth is named exactly `banner`. `list_textures` is the list;
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

