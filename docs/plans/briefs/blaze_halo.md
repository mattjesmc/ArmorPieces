# Brief: Blaze Halo

A piece of **Armor Pieces: Nether** (`armorpieces_nether`) — netherite with gold hardware, the
dimension worn as a body. Other pieces of the pack exist on the forearms, temples, crown and hips;
none is on your bone and none concerns you.

From the `back` row of the Nether table:

> `blaze_halo` — a static ring of rods standing behind the shoulders — no fitting — centre
> `blaze_powder`.

**A real blaze's rods orbit it. The mod has no animation, so this ring is static** — that is
deliberate, it is honest, and it still reads. Do not try to suggest motion by tilting the ring.

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          blaze_halo
    anchor:        back
    namespace:     armorpieces_nether
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\nether\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\nether\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Blaze Halo",
                           recipe: { centre: "minecraft:blaze_powder", craftable: true } }

`minecraft:blaze_powder` is confirmed free. `minecraft:blaze_rod` is **taken** — it is the
`bellows_visor` centre — which is why this piece uses the powder.

**Fittings:** none. **Static layer:** none. **Effects:** none. **Loot:** none — recipe only.
So this piece has **one sheet**, the greyscale master. The reply will say `static_created: false`
and `sheets_created: []`; that is correct. The pack's colour comes from the armor and its trim, not
from this piece's own paint.

## The rig, in Blockbench coordinates

`back` is a **single, centred** socket on the upper back. It is **not** mirrored: you model the
whole ring, both halves of it, and nothing is reflected for you.

    body box                x −4 .. 4     y 12 .. 24    z −2 .. 2
    chestplate shell (+1.0) x −5 .. 5     y 11 .. 25    z −3 .. 3
    the back anchor         (0, 22, 2)

**Check the anchor before you build.** The reply to `armorpieces_new` prints it. It should read
`(0, 22, 2)` in Blockbench coordinates. **If it prints anything else, stop and tell me** — every
coordinate below is measured from that point.

Front is **negative z**, so the back of the body is `z = +2` and everything you build sits at
**positive z, behind the wearer**. The whole ring lives at `z 4.25 .. 4.75`, well clear of the
shell plane at `z = 3`, so nothing here z-fights.

## Shape

A ring of eight short rods standing on end behind the shoulders, evenly spaced around a circle, each
pointing **radially outward** from the ring's centre — a halo seen edge-on from the side and as a
full circle from behind.

- One bone `base` at the anchor (rename the starter `main`; never call a bone `root`; remove the
  starter cube).
- **Eight rods, each its own bone, all children of `base`.** Every rod is the same cube, `0.5` wide,
  `1.8` tall and `0.5` deep, built **upright and unrotated** first and then turned.

**The ring is centred at `(0, 20.0)` with a radius of `4.0`.** The eight rod centres are given
below — do not derive them, they are already worked out. `φ` is the angle round the ring from the
top, going toward `+x`:

| bone | φ | centre (x, y) | unrotated cube |
|---|---|---|---|
| `rod_00` | 0° | (0.00, 24.00) | x −0.25 .. 0.25, y 23.10 .. 24.90 |
| `rod_45` | 45° | (2.83, 22.83) | x 2.58 .. 3.08, y 21.93 .. 23.73 |
| `rod_90` | 90° | (4.00, 20.00) | x 3.75 .. 4.25, y 19.10 .. 20.90 |
| `rod_135` | 135° | (2.83, 17.17) | x 2.58 .. 3.08, y 16.27 .. 18.07 |
| `rod_180` | 180° | (0.00, 16.00) | x −0.25 .. 0.25, y 15.10 .. 16.90 |
| `rod_225` | 225° | (−2.83, 17.17) | x −3.08 .. −2.58, y 16.27 .. 18.07 |
| `rod_270` | 270° | (−4.00, 20.00) | x −4.25 .. −3.75, y 19.10 .. 20.90 |
| `rod_315` | 315° | (−2.83, 22.83) | x −3.08 .. −2.58, y 21.93 .. 23.73 |

**Every rod has the same z: `4.25 .. 4.75`.** The ring is flat.

- **Eight cubes is the budget.** No hub, no connecting band — the rods are the ring.

**Then aim it.** Each bone's **pivot goes at its rod's centre** `(x, y, 4.5)` — the values in the
table — not at an end. A rod must turn on the spot so it stays on the circle; a pivot at an end
would swing it off. Set a rotation **about Z** of exactly **`−φ`**:

    rod_00    0°      rod_45   −45°     rod_90   −90°     rod_135  −135°
    rod_180 −180°     rod_225 −225°     rod_270 −270°     rod_315  −315°

If Blockbench will not take an angle past ±180, use the equivalent inside the range: `−225° = +135°`,
`−270° = +90°`, `−315° = +45°`. Say in your report which form you used.

**The sign, worked out once.** A rotation of `θ` about Z sends the rod's own `+Y` axis to
`(−sin θ, cos θ)`. You want the rod at angle `φ` to point along `(sin φ, cos φ)`, outward from the
centre. Setting `−sin θ = sin φ` gives **`θ = −φ`**. Get the sign backwards and every rod points
*inward*, which reads as a broken cog rather than a halo — and because the ring is symmetric it will
still look plausible in a single screenshot, so check a rod's outer end against the ring centre
rather than trusting the picture.

**Budget for the corner, not the centreline.** A rod's furthest point from the ring centre is its
outer **corner**, at `√(0.9² + 0.25²) = 0.93` from its own centre, so the ring's true outer *radius*
is `4.0 + 0.93 = 4.93`.

The envelope is not that number, and the difference is worth understanding rather than chasing: the
check reports an **axis-aligned box**, and no rod's corner happens to sit on the x or y axis, so the
box comes to **`x −4.90 .. 4.90`, `y 15.10 .. 24.90`**. Those are the numbers to expect. Seeing 4.90
where you predicted 4.93 is correct and is not something to fix.

**Envelope budget.** Stay inside `x −5.0 .. 5.0`, `y 15.0 .. 25.0`, `z 4.0 .. 5.0`.

**The same budget in the check's own frame**, so you never have to convert: the check prints the
envelope **bone-local, +Y down, from the BONE'S PIVOT**, and the body's pivot is at Blockbench
`y = 24`. This socket is **not** mirrored, so bone-local `x` and `z` are the same as Blockbench's.
In that frame your budget is

    x  −5.0 .. 5.0      y  −1.0 .. 9.0      z  4.0 .. 5.0

Compare the check's envelope line against **those** numbers.

**No pair span.** This socket is a single centred piece, not a mirrored pair.

**Neighbours you must clear**, measured, in Blockbench coordinates:

| piece | reaches | what it means for you |
|---|---|---|
| `carapace` | x ±4.75, y 15.60 .. 24.60, z 3.10 .. 5.25 | almost exactly your box; you sit in the same shell of space, which is normal for this socket |
| `turtle_shell` | x ±6.00, y 15.75 .. 24.90, z 3.10 .. 5.60 | wider and deeper than you |
| `pinions` | x −7.78 .. 8.32, y 13.68 .. 23.29, z 2.00 .. 6.29 | the widest piece here |
| `quiver` | x −4.38 .. 4.88, y 12.74 .. 23.78, z 3.22 .. 6.66 | comparable depth |

These are the same socket and are **never worn together**, so the check never compares them — they
are heights and depths to place against, not walls. Expect `-` OVERLAP and `near` lines against
pieces on the **collar** and **belt** sockets, which *are* worn with you; those are hull tests, and
on a ring this size they are unavoidable. Leave them standing and say so.

## Paint

Master sheet `part`, greyscale, one `armorpieces_paint` call. A blaze rod is banded light and dark
down its length. Give every rod's four side faces the same `[top, bottom]` pair — light at the outer
end, mid at the inner end — so all eight read identically however the ring is turned. The **outer**
end face of each rod is the lightest value on the piece; the inner end faces are the darkest.

Because the ring is symmetric, painting all eight rods the same way is correct and is the point: any
rod that differs will read as a mistake.

## Done when

- [ ] The check is clean, or every `!` still standing is one this brief allows.
- [ ] Envelope inside the budget, in the check's frame, and reported.
- [ ] Eight rods, all on the circle, all pointing outward — verified by a rod's outer end being
      further from `(0, 20.0)` than its inner end, not by a screenshot.
- [ ] Master painted; no static sheet and no masks.
- [ ] Saved, and the tab closed.

**Allowed to force:** the `-` OVERLAP and `near` lines against collar and belt pieces, which a ring
of this size cannot avoid. **Nothing else.** If any other `!` stands, stop and ask me.

## Lessons

<!-- Filled in after the session, from its report. -->
