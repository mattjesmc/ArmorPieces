# Brief: Boar Crest

A piece of **Armor Pieces: Norse** (`armorpieces_norse`) — riveted iron, wolf-grey fur, painted lime wood and a little gold - the north as the sagas tell it, hair and beard included.

From the `crest` row of the Norse table:

> `boar_crest` - a gilt boar figure standing on the crown ridge - fitting `guard` - centre `cooked_porkchop`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          boar_crest
    anchor:        crest
    namespace:     armorpieces_norse
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\norse\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\norse\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Boar Crest",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:cooked_porkchop", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Gilt bronze is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `jarl` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:cooked_porkchop` is confirmed free against every
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

The **ridge** carries no static. It is masked `guard` and is the piece's whole material surface; the boar is static gilt and never answers the trim.

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

The boar-crested helm: an iron ridge running front to back over the crown, and a small gilt boar standing on it facing forward - a squat body, a lower head thrust forward, and a row of bristles standing up along its back. It is a figure, not a spike: blocky, stout, and unmistakably a pig.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **ridge** — the iron crest ridge over the crown:

        x -0.57 .. 0.57    y 33.07 .. 33.63    z -3.63 .. 3.63

- **body** — the boar's body, standing on the ridge:

        x -1.08 .. 1.08    y 33.63 .. 35.33    z -2.57 .. 1.63

- **head** — the head, thrust forward and a little lower:

        x -0.87 .. 0.87    y 33.87 .. 35.57    z -3.93 .. -2.57

- **bristles** — the bristles standing up along its back:

        x -0.33 .. 0.33    y 35.33 .. 36.13    z -2.37 .. 1.23

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -1.2 .. 1.2, y 33.0 .. 36.2, z -4.0 .. 3.7`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the head bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  -1.2 .. 1.2      y  -12.2 .. -9.0      z  -4.0 .. 3.7

Compare the check's envelope line against **those** numbers.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `comb` | x -0.75..0.75, y 32.50..34.60, z -2.10..5.60 | the mod's steel comb - a plain ridge where yours carries a figure |
| `hoglin_hair` | x -0.55..0.55, y 32.03..34.65, z -3.03..4.33 | a pack crest at your ridge's thinness |
| `coronet (brow)` | x -6.00..6.00, y 29.00..33.21, z -6.18..-2.25 | a brow piece whose box your ridge's front end crosses in a hull test - an OVERLAP `-`, never a `!` |
| `braided_beard (brow)` | x -3.40..3.40, y 18.80..26.50, z -5.70..-4.10 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `war_braids (horns)` | x -5.70..-4.90, y 20.00..30.50, z -4.00..-1.30 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

body and head: base **160**, `up` **195**, `north` **180**. bristles: base **120**. ridge: base **130**, `up` **165**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `body`, `head`: base `#c8962e`, `up` `#e0b04a` — gilt bronze - the boar's own gold
- `bristles`: base `#8a6a2a`, `up` `#a3823a` — darker bronze - the bristles

**Mask `part_guard`** — flat **140**, on `ridge`. 140 is the value every mask in this project
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

