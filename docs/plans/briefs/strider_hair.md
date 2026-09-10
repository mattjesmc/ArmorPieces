# Brief: Strider Hair

A piece of **Armor Pieces: Nether** (`armorpieces_nether`) — netherite with gold hardware, the
dimension worn as a body. One other piece of the pack exists, `blaze_bracers` on the forearms; it is
on a different bone and does not concern you.

From the `horns` row of the Nether table:

> `strider_hair` — the long red side-tufts at the temples — no fitting — centre `warped_fungus`.

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          strider_hair
    anchor:        horns
    namespace:     armorpieces_nether
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\nether\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\nether\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Strider Hair",
                           static: true,
                           recipe: { centre: "minecraft:warped_fungus", craftable: true } }

`minecraft:warped_fungus` is confirmed free — no other template recipe uses it.

**Fittings:** none. **Effects:** none. **Loot:** none — recipe only.
**Static layer: yes.** A strider's hair is its own dull red and does not take the armor's trim
colour, so this piece has **two sheets**: the greyscale master `part`, and `part_static` which keeps
real colour. The reply to `set_part` will say `static_created: true` and `sheets_created: []` — no
fitting masks, which is correct.

## The rig, in Blockbench coordinates

`horns` is a **mirrored** socket on the temples: model **one** side — the **negative x** side — and
the game mirrors it to the other temple.

    head box                x −4 .. 4     y 24 .. 32     z −4 .. 4
    helmet shell (+1.0)     x −5 .. 5     y 23 .. 33     z −5 .. 5
    the horns anchor        (−4, 29, 0)

**Check the anchor before you build.** The reply to `armorpieces_new` prints it. It should read
`(−4, 29, 0)` in Blockbench coordinates. **If it prints anything else, stop and tell me** — every
coordinate below is measured from that point.

Front is **negative z**; the back of the skull is `z = +4`. On this side **`west` is the outboard
face** and `north` is the front.

The anchor sits on the head box's side face, so your first cube starts inside the helmet shell and
comes out of it. That is right. What is wrong is a face lying exactly in a shell plane — `x = −5`,
`y = 33`, `z = ±5` — which z-fights. Every number below is off the round value on purpose.

## Shape

Two long tufts of coarse hair hanging down the sides of the head, one per temple, the way a
strider's mane hangs. **They hang and taper — they do not branch and do not curl up.** `ears` and
`helm_wings` are the pieces that stand up off this socket; this is deliberately not those.

- One bone `base` at the anchor (rename the starter `main`; never call a bone `root`; remove the
  starter cube).
- **Three segments, each its own bone, each a child of the one before it**, hanging downward and
  tapering. Build every one of them **straight down and unrotated first**, then aim them:
  - `tuft1` off `base`, the thickest, from the temple: cube about
    `x −6.3 .. −4.15`, `y 26.4 .. 29.3`, `z −1.6 .. 1.6`
  - `tuft2` off `tuft1`, thinner: cube about
    `x −6.1 .. −4.35`, `y 24.2 .. 26.6`, `z −1.35 .. 1.35`
  - `tuft3` off `tuft2`, thinnest, ending in a point: cube about
    `x −5.9 .. −4.55`, `y 23.15 .. 24.4`, `z −1.05 .. 1.05`
  - Overlap each joint by about a quarter unit, which the ranges above already do.
- **Four cubes is the budget** — the three segments plus, optionally, one small cube where the tuft
  leaves the temple. Five only if that root cube earns it.

**Then aim it.** Each bone's pivot goes at its **top** edge (the near end), because rotating moves
everything except the pivot — a pivot at the bottom would swing the root instead of the tip. Set:

    tuft1  rotation about Z:  −6°       tuft2  about Z: −9°       tuft3  about Z: −12°

Each is a **local** rotation, so the chain compounds and the tuft curves outward as it falls. Add
about `−5°` about **X** on `tuft2` and `tuft3` if you want it drifting back; it is optional.

**The signs, worked out once — and they are NEGATIVE here.** These segments point **down**, so the
tip sits at `Δy = −L` from its pivot. About Z, `Δx' = Δx·cosθ − Δy·sinθ`, which for `Δx = 0` and
`Δy = −L` gives `Δx' = +L·sinθ`. Outboard on this side is **−x**, so you need `Δx'` negative, so you
need **sinθ negative — a negative angle.** A positive angle here swings the tuft *into the wearer's
head*. The same reasoning about X gives `Δz' = Δy·sinθ = −L·sinθ`, so a **negative** angle sweeps
the tip **backward** (+z). Both signs are negative. This is the opposite of a piece that points up,
and it is the single thing most likely to go wrong in this brief.

**Budget for the corner, not the centreline.** A segment's own half-width, rotated by the same
angle, adds `halfwidth × sin θ` beyond where the centreline lands. Check all four corners of the
lowest segment against the walls below before you commit.

**Envelope budget.** Stay inside `x −8.5 .. −4.05`, `y 23.0 .. 30.0`, `z −2.5 .. 2.5`.

**The same budget in the check's own frame**, so you never have to convert: the check prints the
envelope **bone-local, +Y down, from the BONE'S PIVOT**, and the head's pivot is at Blockbench
`y = 24`. On this mirrored socket bone-local `x` is the **negation** of Blockbench `x`. In that
frame your budget is

    x  4.05 .. 8.5      y  −6.0 .. 1.0      z  −2.5 .. 2.5

Compare the check's envelope line against **those** numbers.

**The pair span DOES apply on this socket.** It is a mirrored pair on the head, so the pair spans
`2 × |x|` across the figure and the check compares it against the 18 the shoulders span. At
`x = −8.5` the pair spans 17.0 and stays inside it. Report your span.

**Neighbours you must clear**, measured, in Blockbench coordinates on this side:

| piece | reaches | what it means for you |
|---|---|---|
| `cheek_guards` | x −6.18 .. −4.65, y 24.43 .. 29.40 | the closest thing to your tuft; you overlap its band in y, so stay outboard of `x = −4.65` where you can |
| `ears` | x −6.38 .. −3.99, y 31.31 .. 36.21 | above you; no conflict |
| `head_fins` | x −8.75 .. −4.66, y 26.31 .. 31.87 | the widest piece here; your `x ≥ −8.5` keeps you inside it |
| `aerials` | x −9.25 .. −4.50, y 28.08 .. 32.50 | above and outboard; no conflict |

These are the same socket and are **never worn together**, so the check never compares them — they
are heights and depths to place against, not walls.

## Paint

Master sheet `part`, greyscale — a value is a position on the trim material's ramp. One
`armorpieces_paint` call. Coarse hair, so give each segment's four side faces a `[top, bottom]` pair
running from mid at the top to dark at the bottom, and let each lower segment be a little darker
than the one above. The bottom face of `tuft3` is the darkest value on the piece.

Static sheet `part_static`, real colour, one call. A strider's dull red on **every face of every
segment** — around `#8B3A3A` at the top fading to `#5C2626` at the bottom, using `[top, bottom]`
pairs the same way. This is the layer that carries the piece's colour; the master only carries its
shading.

## Done when

- [ ] The check is clean, or every `!` still standing is one this brief allows.
- [ ] Envelope inside the budget, in the check's frame, and reported.
- [ ] Pair span reported, and under 18.
- [ ] Both sheets painted: master greyscale, static in colour, same faces.
- [ ] Saved, and the tab closed.

**Allowed to force:** nothing. If a `!` stands, stop and ask me.

## Lessons

<!-- Filled in after the session, from its report. -->
