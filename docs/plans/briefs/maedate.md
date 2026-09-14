# Brief: Maedate

A piece of **Armor Pieces: Samurai** (`armorpieces_samurai`) — black lacquer over iron, red odoshi lacing and gilt fittings - the armor of a daimyo, every piece a named part of a real suit.

From the `crest` row of the Samurai table:

> `maedate` - a gilt crescent standing up at the front of the crown - fitting `guard` - centre `sunflower`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          maedate
    anchor:        crest
    namespace:     armorpieces_samurai
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\samurai\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\samurai\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Maedate",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:sunflower", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Gilt is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `daimyo` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:sunflower` is confirmed free against every
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

The **mount** and **stem** carry no static and no mask; they are the piece's material surface, plain metal answering the trim. The **crescent** (bar and tips) is static gold by default AND masked `guard`, so a player can make it iron or copper instead.

## The rig, in Blockbench coordinates

    head box                x -4 .. 4       y 24 .. 32      z -4 .. 4
    helmet shell (+1)       x -5 .. 5       y 23 .. 33      z -5 .. 5
    the `crest` anchor       (0, 32, 0)

Front is **negative z**. This socket is not mirrored: build the whole piece once.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(0, 32, 0)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

The front crest of a kabuto: a small mount plate on the front of the crown, a short stem rising from it, and a wide gilt crescent standing up on the stem - a horizontal bar with two tips curving up at its ends. Flat, thin and tall; it is a blade of gold leaf, not a horn. It faces forward and is seen edge-on from the side.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **mount** — the mount plate on the front of the crown:

        x -1.03 .. 1.03    y 33.07 .. 33.63    z -3.97 .. -1.96

- **stem** — the stem rising from the mount:

        x -0.43 .. 0.43    y 33.63 .. 35.08    z -3.37 .. -2.57

- **bar** — the crescent's horizontal bar:

        x -3.52 .. 3.52    y 35.08 .. 35.90    z -3.27 .. -2.67

- **tip_l** — the left tip curving up:

        x -3.52 .. -2.67    y 35.90 .. 38.47    z -3.27 .. -2.67

- **tip_r** — the right tip:

        x 2.67 .. 3.52    y 35.90 .. 38.47    z -3.27 .. -2.67

**5 cubes in total is the budget**, and there is no 6th.

**Envelope budget.** Stay inside `x -3.6 .. 3.6, y 33.0 .. 38.6, z -4.1 .. -1.9`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the head bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -3.6 .. 3.6      y  -14.6 .. -9.0      z  -4.1 .. -1.9

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `brush_crest` | x -1.50..1.50, y 32.00..39.00, z -4.66..4.66 | the mod's crest on this socket, front-to-back where you are side-to-side |
| `dragon_crest` | x -0.55..0.55, y 31.88..35.60, z -3.40..3.62 | a pack crest at your stem's thinness |
| `coronet (brow)` | x -6.00..6.00, y 29.00..33.21, z -6.18..-2.25 | a brow piece that rises to y 33.21 at the front - your mount sits inside its box in a hull test, an OVERLAP `-`, never a `!` |
| `mempo (brow)` | x -4.00..4.00, y 22.50..28.00, z -6.50..-4.90 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `kuwagata (horns)` | x -5.70..-5.00, y 29.30..38.20, z -3.70..-1.80 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

crescent (bar, tips): base **170**, `north` **200** (the front face is the one that shines), `up` **215**. mount and stem: base **120**, `up` **150**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `bar`, `tip_l`, `tip_r`: base `#d4a83a`, `up` `#f1cc5a` — gilt - the maedate's gold leaf

**Mask `part_guard`** — flat **140**, on `bar`, `tip_l`, `tip_r`. 140 is the value every mask in this project
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

