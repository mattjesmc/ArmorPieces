# Brief: Silverfish Greaves

A piece of **Armor Pieces: The Hive** (`armorpieces_hive`) — netherite and lime over lamellar - black insect chitin on dark metal hardware, with the lime of the membrane and the gold of honey as the only light in it.

From the `greaves` row of the Hive table:

> `silverfish_greaves` - overlapping grey segment plates up the shins - fitting `guard` - centre `stone_bricks`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          silverfish_greaves
    anchor:        greaves
    namespace:     armorpieces_hive
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\hive\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\hive\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Silverfish Greaves",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:stone_bricks", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Silverfish grey-green is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `hive` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:stone_bricks` is confirmed free against every
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

The **strap** carries no static. It is masked `guard` and is the piece's whole material surface.

## The rig, in Blockbench coordinates

    left leg box            x -3.9 .. 0.1   y 0 .. 12       z -2 .. 2
    leggings shell (+0.4)   x -4.3 .. 0.5   y -0.4 .. 12.4  z -2.4 .. 2.4
    boots shell (+0.9)      x -4.8 .. 1.0   y -0.9 .. 12.9  z -2.9 .. 2.9
    the `greaves` anchor       (-1.9, 4, -2)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-1.9, 4, -2)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

A silverfish's back worn up the shin: three overlapping grey-green plates, each a little wider than the one above so they step outward toward the ankle, a metal strap at the top, and two stiff bristles sticking forward from the lowest plate at the ankle. Grey, faintly green - the silverfish's own colour, not iron.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **strap** — the metal strap at the top, below the knee:

        x -5.27 .. 0.23    y 5.53 .. 6.13    z -3.57 .. -2.67

- **plate_up** — the top plate, the narrowest:

        x -4.93 .. 0.23    y 3.92 .. 5.53    z -3.47 .. -2.48

- **plate_mid** — the middle plate:

        x -5.03 .. 0.33    y 2.08 .. 3.77    z -3.57 .. -2.42

- **plate_lo** — the lowest and widest plate, at the ankle:

        x -5.08 .. 0.43    y 0.24 .. 1.94    z -3.68 .. -2.33

- **bristle_a** — the outer bristle, sticking forward from the ankle plate:

        x -3.13 .. -2.47    y 0.24 .. 0.74    z -4.63 .. -3.68

- **bristle_b** — the inner bristle:

        x -1.57 .. -0.87    y 0.24 .. 0.74    z -4.63 .. -3.68

**6 cubes in total is the budget**, and there is no 7th.

**Envelope budget.** Stay inside `x -5.4 .. 0.5, y 0.1 .. 6.2, z -4.7 .. -2.2`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box. For this socket:

    check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -2.4 .. 3.5      y  5.8 .. 11.9      z  -4.7 .. -2.2

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `5.27`, so the pair spans **10.54**. **The 18-unit ceiling is a `horns` rule and does not apply on this bone** — the legs sit inboard of the shoulders, and the mod's own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `soul_greaves` | x -4.06..-0.15, y 0.35..8.37, z -3.12..-2.62 | a pack shin piece; you are wider and shorter |
| `shin_spikes` | x -2.90..-0.90, y 0.90..3.75, z -5.51..-2.95 | the precedent for something sticking forward off the shin; your bristles stop at -4.63 |
| `knee_studs (knees)` | x -3.15..-0.65, y 3.90..6.10, z -3.50..-3.00 | worn WITH you and sharing your top plate's height band in a hull test - an OVERLAP `-`, not a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

plates: base **140**, `north` **160**, `down` **110**. bristles: base **50**. strap: base **130**, `up` **165**.

**Each plate's back face is inside the boot.** The plates run to z -2.33 / -2.42 / -2.48 and the boots shell's front wall is at z -2.9, so the back of every plate is buried and only the front and the sides show.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `plate_up`, `plate_mid`, `plate_lo`: base `#8e9485`, `up` `#8f9586` — silverfish grey-green - the silverfish's own back, and `down` #7a7e8b, its bluer shadow
- `bristle_a`, `bristle_b`: base `#262626`, `up` `#3a3a3a` — silverfish black - its bristles

**Mask `part_guard`** — flat **140**, on `strap`. 140 is the value every mask in this project
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
