# Brief: Hoglin Hair

A piece of **Armor Pieces: Nether** (`armorpieces_nether`) — netherite with gold hardware, the
dimension worn as a body. One other piece of the pack exists, `blaze_bracers` on the forearms; it is
on a different bone and does not concern you.

From the `crest` row of the Nether table:

> `hoglin_hair` — the bristled tuft over the crown — no fitting — centre `porkchop`.

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          hoglin_hair
    anchor:        crest
    namespace:     armorpieces_nether
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\nether\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\nether\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Hoglin Hair",
                           static: true,
                           recipe: { centre: "minecraft:porkchop", craftable: true } }

`minecraft:porkchop` is confirmed free — no other template recipe uses it.

**Fittings:** none. **Effects:** none. **Loot:** none — recipe only.
**Static layer: yes.** A hoglin's bristles are their own brown and do not take the armor's trim
colour, so this piece has **two sheets**: the greyscale master `part`, and `part_static` which keeps
real colour. The reply to `set_part` will say `static_created: true` and `sheets_created: []` — no
fitting masks, which is correct.

## The rig, in Blockbench coordinates

`crest` is a **single, centred** socket on the top of the skull. It is **not** mirrored: you model
the whole piece, both sides of it, and nothing is reflected for you.

    head box                x −4 .. 4     y 24 .. 32     z −4 .. 4
    helmet shell (+1.0)     x −5 .. 5     y 23 .. 33     z −5 .. 5
    the crest anchor        (0, 32, 0)

**Check the anchor before you build.** The reply to `armorpieces_new` prints it. It should read
`(0, 32, 0)` in Blockbench coordinates. **If it prints anything else, stop and tell me** — every
coordinate below is measured from that point.

Front is **negative z**; the back of the skull is `z = +4`.

The anchor sits on the head box's top face, so your first cube starts inside the helmet shell and
comes out of it. That is right. A face lying exactly in the shell plane `y = 33` z-fights, so the
numbers below are off the round value on purpose.

## Shape

A stiff bristled ridge over the crown, running front to back — a hoglin's mane. **Low and wide, a
row of separate bristles, splaying outward from the centreline.** `spire` and `feathering` are the
tall pieces on this socket; this is deliberately not those, and it must stay short.

- One bone `base` at the anchor (rename the starter `main`; never call a bone `root`; remove the
  starter cube).
- **Five bristles, each its own bone, all children of `base`**, in a row along z, all the same
  height, each a thin upright cube. Build them all **straight up and unrotated first**, then aim
  them. Unrotated, each bristle is a cube:

        x −0.55 .. 0.55      y 32.15 .. 34.6

  placed at these z positions, front to back:

        bristle_f2   z −2.45 .. −1.45
        bristle_f1   z −1.15 .. −0.15
        bristle_m    z  0.15 ..  1.15
        bristle_b1   z  1.45 ..  2.45
        bristle_b2   z  2.75 ..  3.75

- **Five cubes is the budget**, one per bristle. A sixth only if you add a low base ridge under
  them, and only if it stays inside the envelope.

**Then aim it.** Each bone's pivot goes at its **bottom** edge (`y = 32.15`, at its own z centre),
because rotating moves everything except the pivot — the bristle must splay at the tip and stay put
at the root. Set a rotation **about X** on each, fanning front to back:

    bristle_f2  −14°      bristle_f1  −7°      bristle_m  0°      bristle_b1  +7°      bristle_b2  +14°

The middle bristle stands straight; the front pair leans forward, the back pair leans back. This is
a fan, not a curve, so the rotations are **not** compounded — every bristle is a child of `base`,
not of its neighbour.

**The signs, worked out once — and they are the OPPOSITE of a hanging piece.** These bristles point
**up**, so a tip sits at `Δy = +L` from its pivot. About X, `Δz' = Δy·sinθ + Δz·cosθ`, which for
`Δy = +L` gives `Δz' = +L·sinθ`. So a **positive** angle about X swings a tip toward `+z`, which is
**backward**, and a negative angle swings it **forward** toward the face. That is why the front
bristles above are negative and the back ones positive. Get this backwards and the mane leans the
wrong way, which looks like a mistake rather than a style.

**Budget for the corner, not the centreline.** A bristle's own half-depth, rotated by the same
angle, adds `halfdepth × sin θ` beyond where the centreline lands. `bristle_b2` at `+14°` is the one
that reaches furthest back — check its four corners against the `z` wall before you commit.

**Envelope budget.** Stay inside `x −2.6 .. 2.6`, `y 31.9 .. 35.5`, `z −3.2 .. 4.5`.

> **Corrected 2026-09-09, after the build.** The `z` wall read `−2.6 .. 2.6`, which this brief's own
> bristle lanes break before any rotation — `bristle_b2` sits at `z 2.75 .. 3.75` unrotated, and
> leaning it back takes its top corner to `4.33`. The lanes and the angles were right; the wall was
> arithmetic I never checked. `z −3.2 .. 4.5` is the real figure, and it is unremarkable for this
> socket: `comb` reaches `5.60`, `horsetail` `7.73`, `feathering` `8.21`.

**The same budget in the check's own frame**, so you never have to convert: the check prints the
envelope **bone-local, +Y down, from the BONE'S PIVOT**, and the head's pivot is at Blockbench
`y = 24`. This socket is **not** mirrored, so bone-local `x` and `z` are the same as Blockbench's.
In that frame your budget is

    x  −2.6 .. 2.6      y  −11.5 .. −7.9      z  −3.2 .. 4.5

Compare the check's envelope line against **those** numbers.

**No pair span.** This socket is a single centred piece, not a mirrored pair, so no pair-span line
applies to you. Report your envelope only.

**Neighbours you must clear**, measured, in Blockbench coordinates:

| piece | reaches | what it means for you |
|---|---|---|
| `comb` | x ±0.75, y 32.50 .. 34.60, z −2.10 .. 5.60 | the closest in height — your 34.6 top is deliberately level with it |
| `brush_crest` | x ±1.50, y 32.00 .. 39.00 | much taller; you are the low piece here on purpose |
| `antennae` | x ±3.24, y 32.32 .. 39.73 | the widest on this socket; your `x ≤ 2.6` stays inside it |
| `spire` | x ±2.50, y 32.50 .. 40.00 | tall and narrow; no conflict at your height |

These are the same socket and are **never worn together**, so the check never compares them — they
are heights and depths to place against, not walls.

## Paint

Master sheet `part`, greyscale — a value is a position on the trim material's ramp. One
`armorpieces_paint` call. Coarse bristle: give every bristle's four side faces a `[top, bottom]`
pair running from light at the tip to dark at the root, so the mane reads as separate hairs rather
than a block. The top faces are the lightest value on the piece.

Static sheet `part_static`, real colour, one call. A hoglin's brown on **every face of every
bristle** — around `#6B4A32` at the tip fading to `#3E2A1C` at the root, using `[top, bottom]` pairs
the same way. This is the layer that carries the piece's colour; the master only carries its
shading.

## Done when

- [ ] The check is clean, or every `!` still standing is one this brief allows.
- [ ] Envelope inside the budget, in the check's frame, and reported.
- [ ] All five bristles present, fanned front to back, middle one upright.
- [ ] Both sheets painted: master greyscale, static in colour, same faces.
- [ ] Saved, and the tab closed.

**Allowed to force:** nothing. If a `!` stands, stop and ask me.

## Lessons

<!-- Filled in after the session, from its report. -->
