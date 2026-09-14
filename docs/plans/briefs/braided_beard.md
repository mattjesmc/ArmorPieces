# Brief: Braided Beard

A piece of **Armor Pieces: Norse** (`armorpieces_norse`) — riveted iron, wolf-grey fur, painted lime wood and a little gold - the north as the sagas tell it, hair and beard included.

From the `brow` row of the Norse table:

> `braided_beard` - a great blonde beard on the face, two braids hanging below the chin with metal beads - fitting `guard` - centre `shears`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          braided_beard
    anchor:        brow
    namespace:     armorpieces_norse
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\norse\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\norse\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Braided Beard",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:shears", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Flaxen hair is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `jarl` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:shears` is confirmed free against every
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

The two **beads** carry no static. They are masked `guard` and are the piece's whole material surface; the hair is static and never answers the trim.

## The rig, in Blockbench coordinates

    head box                x -4 .. 4       y 24 .. 32      z -4 .. 4
    helmet shell (+1)       x -5 .. 5       y 23 .. 33      z -5 .. 5
    the `brow` anchor       (0, 28, -4)

Front is **negative z**. This socket is not mirrored: build the whole piece once.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(0, 28, -4)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

A jarl's beard: a thick block of blonde hair over the lower face from under the nose to below the chin, and two plaited braids hanging down from it in front of the chest, each ending in a metal bead. It is worn on the helmet's face, so it turns with the head. The eyes are open above it.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **beard** — the beard over the lower face:

        x -3.27 .. 3.27    y 23.37 .. 26.37    z -5.63 .. -5.13

- **braid_l** — the left braid hanging below the chin:

        x -2.37 .. -1.23    y 19.57 .. 23.37    z -4.93 .. -4.23

- **braid_r** — the right braid:

        x 1.23 .. 2.37    y 19.57 .. 23.37    z -4.93 .. -4.23

- **bead_l** — the bead at the end of the left braid:

        x -2.27 .. -1.33    y 18.87 .. 19.57    z -4.83 .. -4.33

- **bead_r** — the right bead:

        x 1.33 .. 2.27    y 18.87 .. 19.57    z -4.83 .. -4.33

**5 cubes in total is the budget**, and there is no 6th.

**Envelope budget.** Stay inside `x -3.4 .. 3.4, y 18.8 .. 26.5, z -5.7 .. -4.1`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the head bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -3.4 .. 3.4      y  -2.5 .. 5.2      z  -5.7 .. -4.1

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `barbute` | x -4.00..4.00, y 22.50..29.50, z -5.10..-4.85 | the precedent for a brow piece reaching below the helmet's y 23; yours goes to 18.87 |
| `mempo` | x -4.00..4.00, y 22.50..28.00, z -6.50..-4.90 | the Samurai's face mask, built in this batch - the same band of the face, never worn with you |
| `ruff (collar)` | x -5.88..5.88, y 25.10..26.55, z -5.88..5.88 | on the BODY bone, so the check never compares you with it, but the braids would hang through it - a player's problem, not yours |
| `boar_crest (crest)` | x -1.20..1.20, y 33.00..36.20, z -4.00..3.70 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `war_braids (horns)` | x -5.70..-4.90, y 20.00..30.50, z -4.00..-1.30 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

beard and braids: base **150**, `north` **170**, `down` **115**. beads: base **140**, `north` **175**.

**Cut nothing.** The eyes are the open space ABOVE the beard.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `beard`, `braid_l`, `braid_r`: base `#c9a24a`, `up` `#e0bd63` — flaxen hair - the beard and braids' own blonde

**Mask `part_guard`** — flat **140**, on `bead_l`, `bead_r`. 140 is the value every mask in this project
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

