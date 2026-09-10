# Brief: Ominous Banner

A piece of **Armor Pieces: Hero of the Village** (`armorpieces_village`) — iron armor with emerald
hardware, the raid worn by the person who won it.

**This is the first piece of the pack.** Nothing else exists in it yet, so there are no pack
siblings to clear and no house style to match beyond this brief.

From the `back` row of the Hero of the Village table:

> `ominous_banner` — a pole rising behind the head, banner flying above it — fitting `banner` +
> `guard` — found in a chest, not crafted.

**It is deliberately built first, because it is the risky one.** Nothing in the mod's 66 pieces
stands this far above the head from the `body` bone: the tallest thing on `body` is the mod's own
`banner` at Blockbench `y = 21.50`, which is *below* the chin. This piece goes to `y = 38.35`.
Eleven other pieces in the pack are waiting on what you find out here, so **your report matters as
much as the piece**.

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          ominous_banner
    anchor:        back
    namespace:     armorpieces_village
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\village\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\village\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Ominous Banner",
                           fittings: ["armorpieces:banner", "armorpieces:guard"] }

**Fittings: two, and they are different kinds.**

- `armorpieces:banner` is **not a mask**. It is rendered by the game's own banner renderer onto the
  cubes in a bone that must be named exactly **`banner`**, off the `shield` sheet. **No
  `part_banner.png` is created and none should be** — if the reply lists one, stop and tell me.
- `armorpieces:guard` **is** a mask, and `part_guard` will be created for you to paint.

**Static layer: none.** `static_created: false` is correct, and it is a deliberate decision, not an
omission: the cloth's colour comes from the banner a player fits, and the pole and bracket are
hardware that should answer the trim. A static layer here would fight both.

**Effects: none. Loot: none — leave `loot` out of your call entirely.** This piece is found in a
chest rather than crafted, but the pack's loot group does not exist yet and a session must not
invent one. I add it afterwards in the repo half. **Do not add a recipe either.**

So this piece has **two sheets**: the greyscale master `part`, and the greyscale mask `part_guard`.

## The rig, in Blockbench coordinates

    body box                x −4 .. 4     y 12 .. 24    z −2 .. 2
    chestplate shell (+1)   x −5 .. 5     y 11 .. 25    z −3 .. 3
    head box                x −4 .. 4     y 24 .. 32    z −4 .. 4
    helmet shell (+1)       x −5 .. 5     y 23 .. 33    z −5 .. 5
    the `back` anchor       (0, 22, 2)

Front is **negative z**, so **+z is behind the wearer** and everything here lives back there.
`back` is **not** a mirrored socket: build the whole piece once.

**Check the anchor before you build.** The reply to `armorpieces_new` prints it and it should read
`(0, 22, 2)`. **If it prints anything else, stop and tell me** — every coordinate below is measured
from that point.

**The helmet shell is the wall this piece has to clear**, and it is the whole reason for the z
numbers below. The helmet shell reaches `z = 5`, and a pole that passes the head at `z < 5` would
run through the helmet. Everything that rises past `y = 23` is therefore at `z ≥ 5.25`.

## Shape

A raid captain's banner: a short bracket strapped across the upper back, a pole standing well above
the head, and the cloth flying from the top of it. It is deliberately **not** the mod's `banner`,
which is a mounted banner sitting low on the back — this one is carried high and is meant to be
seen across a village.

**This piece has no rotations at all.** Every bone stays at rotation `0`; a banner pole stands
straight. If you find yourself computing a sine, you have misread the brief.

- **Bone `mount`** at the anchor. Rename the starter bone `main` to **`mount`**, not `base` — this
  piece follows the mod's own banner convention. Remove the starter cube. Never name a bone `root`.

  - **the bracket**, one cube in `mount` — the strap across the upper back, starting inside the
    chestplate and coming out through it:

        x −1.85 .. 1.85     y 19.55 .. 22.45     z 1.75 .. 5.45

    It crosses the chestplate shell plane at `z = 3` rather than lying in it, which is correct and
    expected. Its top stays at `22.45`, **below the helmet shell's `y = 23`**, deliberately.

  - **the pole**, one cube in `mount`:

        x −0.55 .. 0.55     y 20.15 .. 38.35     z 5.25 .. 6.15

    It starts inside the bracket (they overlap from `z 5.25` to `5.45`, which is interpenetration,
    not a shared face — no z-fight) and runs up past the head at `z 5.25`, clearing the helmet
    shell's `z = 5` by **0.25**.

- **Bone `banner`**, a child of `mount`. **The name must be exactly `banner`** — the banner fitting
  binds to a bone of that name and finds nothing if it is called anything else.

  - **the cloth**, one cube in `banner`:

        x −3.5 .. 3.5     y 25.85 .. 37.85     z 6.35 .. 7.35

    **7 wide × 12 tall × 1 deep, and those three numbers are not yours to change.** They are exactly
    the mod's own banner cloth, and the banner renderer maps the shield sheet onto that shape. A
    different size would map the pattern wrongly.

**Three cubes in total is the budget**, and there is no fourth.

**Envelope budget.** Stay inside `x −3.6 .. 3.6`, `y 19.5 .. 38.4`, `z 1.7 .. 7.4`.

**The same budget in the check's own frame** — always compare like with like. The check reports
**bone-local, +Y down, from the BONE'S PIVOT**, and the `body` pivot is at Blockbench `(0, 24, 0)`.
So for this socket the conversion is

    check_x = −bb_x        check_y = 24 − bb_y        check_z = bb_z

and your budget in that frame is

    x  −3.6 .. 3.6      y  −14.4 .. 4.5      z  1.7 .. 7.4

**A negative check `y` means "above the body bone's pivot", which means above the shoulders.** No
other piece on this bone has one. That is expected here and is not a fault.

**Neighbours you must clear.** These are the other `back` pieces, in Blockbench coordinates. You are
worn *instead of* them, so the check never compares you with them — they are here so you know what
the socket normally does, and how far outside it you are:

| piece | reaches (Blockbench) |
|---|---|
| `banner` (the mod's) | x −3.50..3.50, y 8.50..21.50, z 1.75..6.25 |
| `cloak` | x −5.45..5.45, y 9.63..24.85, z 2.90..4.63 |
| `quiver` | x −4.38..4.88, y 12.74..23.78, z 3.22..6.66 |
| `bedroll` | x −6.00..6.00, y 20.60..24.85, z 2.70..7.35 |
| `pinions` | x −7.78..8.32, y 13.68..23.29, z 2.00..6.29 |

Your `z 7.35` matches `bedroll`'s exactly, so depth is precedented even though height is not.

**The pieces you WILL be compared against** are the other sockets on `body`, worn at the same time.
The belt pieces sit at `y 8.6 .. 16.5` and cannot reach you. The one to watch is the `collar` group,
which reaches up to `y 26.55` (`ruff`) at `z −5.88 .. 5.88` — your bracket at `y 19.55..22.45`,
`z 1.75..5.45` may graze it. **An OVERLAP or `near` note against `ruff` or `scarf` is a `-`, not a
`!`, and you should leave it standing and say so.**

## Paint

One call on the master, one on the mask.

**Master** — values are positions on the trim ramp, so read them as light and dark, not as colours:

- the pole: mid-dark, base **95**, with `up` at **150** so the top catches light. It is a shaft.
- the bracket: mid, base **130**, `up` **170**, `down` **80` — it reads as a strap end.
- the cloth: flat **160**, all faces. It is plain cloth when no banner is fitted, and the banner
  renderer covers it when one is. **Paint it anyway** — an unpainted face renders as a hole.

**Mask `part_guard`** — flat **140**, on the **pole only**:

    armorpieces_paint { sheet: "part_guard", faces: { "<the pole cube>.*": 140 } }

140 is the value every mask in this project uses. **The bracket is deliberately left unmasked**, so
that some of this piece always answers the trim material even when a player has filled the guard.
Do not mask the cloth — the banner fitting owns it.

## Done when

- [ ] The check is clean, or every `!` left standing is one this brief allows.
- [ ] Envelope inside the budget above, **reported in the check's frame**.
- [ ] Both sheets painted — master and `part_guard`. No `part_banner` sheet exists.
- [ ] The bone holding the cloth is named exactly `banner`.
- [ ] Saved, and the tab closed.

**Allowed to force:** nothing. If a `!` stands, stop and ask me.

## What I need in your report, beyond the usual

This piece exists to answer a question, so please say plainly:

1. **Did the rig take it?** Does a piece on `body` standing to `y = 38.35` render, and does the
   figure still look right — or does the banner read as floating, detached from the wearer?
2. **What did the check say about the height?** Any note you have not seen on a normal piece.
3. **Did the pole clear the helmet?** The `past helmet` / `past chestplate` clearance lines.
4. **Would you build another piece this tall?** Eleven more pieces are waiting on that answer.

## Lessons

<!-- Filled in after the session, from its report. -->
