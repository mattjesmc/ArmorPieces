# Brief: War Braids

A piece of **Armor Pieces: Norse** (`armorpieces_norse`) — riveted iron, wolf-grey fur, painted lime wood and a little gold - the north as the sagas tell it, hair and beard included.

From the `horns` row of the Norse table:

> `war_braids` - a blonde braid from each temple hanging in front of the shoulder, with a metal ring - fitting `guard` - centre `bone`

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          war_braids
    anchor:        horns
    namespace:     armorpieces_norse
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\norse\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\norse\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "War Braids",
                           fittings: ["armorpieces:guard"],
                           static: true,
                           recipe: { centre: "minecraft:bone", craftable: true } }

**Fittings:** one, **`armorpieces:guard`**, masked. The reply will say a `part_guard` sheet was created; that is what you paint the mask onto later, and it is why this call comes before painting.
**Static layer: yes.** `static_created: true` is correct. Flaxen hair is a colour that must not change with the armor.
**Effects: none. Loot: none in YOUR call — leave `loot` out entirely.** The piece joins the pack's `jarl` loot group
afterwards, in the repo half, by one line in a tag file; a session must not invent a loot row.
The recipe above is the other way it is had; `minecraft:bone` is confirmed free against every
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

The **ring** carries no static. It is masked `guard` and is the piece's whole material surface.

## The rig, in Blockbench coordinates

    head box                x -4 .. 4       y 24 .. 32      z -4 .. 4
    helmet shell (+1)       x -5 .. 5       y 23 .. 33      z -5 .. 5
    the `horns` anchor       (-4, 29, 0)

Front is **negative z**. **This is a mirrored socket: model the negative-x side ONLY** and the game mirrors it to the other side. On this side, `west` is the outboard face and `north` is the front.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(-4, 29, 0)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The check only measures your own armor shell.** A `back` piece gets no `past helmet` line at all,
because the helmet is not its shell. So the check will **not** warn you about running into a shell
that belongs to a different armor piece. Every coordinate below already clears the ones that
matter; do not move them toward another shell.

## Shape

A warrior's braids: a root of hair at the front of each temple, a thick plait hanging straight down beside the face and past the chin, a metal ring binding it below the jaw, and a loose tail hanging from the ring in front of the shoulder. The plait runs down the FRONT-side of the head so it clears the shoulder below.

**This piece has no rotations.** Every bone stays at rotation `0`. If you find yourself computing a
sine, you have misread the brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If a bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.

- **root** — the hair at the front of the temple:

        x -5.57 .. -5.07    y 28.36 .. 30.43    z -2.63 .. -1.42

- **braid** — the plait hanging beside the face and past the chin:

        x -5.53 .. -5.07    y 23.07 .. 28.36    z -3.83 .. -3.17

- **ring** — the metal ring binding the plait below the jaw:

        x -5.63 .. -4.97    y 22.27 .. 23.07    z -3.91 .. -3.05

- **tail** — the loose tail below the ring, in front of the shoulder:

        x -5.47 .. -5.13    y 20.07 .. 22.27    z -3.77 .. -3.23

**4 cubes in total is the budget**, and there is no 5th.

**Envelope budget.** Stay inside `x -5.7 .. -4.9, y 20.0 .. 30.5, z -4.0 .. -1.3`.

**The same budget in the check's own frame**, so you never have to convert. The check reports
**bone-local, +Y down, from the BONE'S PIVOT** — the head bone's pivot at Blockbench `(0, 24, 0)`. For this socket:

    check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z

and your budget in that frame is

    x  4.9 .. 5.7      y  -6.5 .. 4.0      z  -4.0 .. -1.3

Compare the check's envelope line against **those** numbers.

**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` is `5.63`, so the pair spans **11.26** — the check compares that against the **18** the shoulders span, and you are inside it. Report the span.

**Neighbours.** In Blockbench coordinates:

| piece | reaches | what it tells you |
|---|---|---|
| `strider_hair` | x -7.25..-4.16, y 25.32..31.66, z -1.60..1.60 | the Nether's temple tufts - the precedent for hair on this socket |
| `axolotl_frills` | x -9.35..-3.91, y 23.69..29.05, z -0.24..3.38 | a pack piece that reaches below the helmet's y 23.69 here; you go lower, in front |
| `mempo (brow)` | x -4.00..4.00, y 22.50..28.00, z -6.50..-4.90 | built in this batch on the face; your braid at z -3.83..-3.17 sits BEHIND its plane, and the two never meet |
| `boar_crest (crest)` | x -1.20..1.20, y 33.00..36.20, z -4.00..3.70 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |
| `braided_beard (brow)` | x -3.40..3.40, y 18.80..26.50, z -5.70..-4.10 | your own pack's piece on this bone, worn WITH you and built in the same batch - the coordinates above already stay off its faces; an OVERLAP note against it is a `-`, never a `!` |

## Paint

One call per sheet: master first, then static, then the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not colour:

root, braid and tail: base **150**, `west` **170** (the outboard face), `north` **165**. ring: base **140**, `west` **175**.

**Static** — real colour, `#rrggbb`, and it stays that colour:

- `root`, `braid`, `tail`: base `#c9a24a`, `up` `#e0bd63` — flaxen hair - the beard and braids' own blonde

**Mask `part_guard`** — flat **140**, on `ring`. 140 is the value every mask in this project
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

