# Brief: Magma Cops

A piece of **Armor Pieces: Nether** (`armorpieces_nether`), the pack in `docs/plans/pack-line.md`
whose boss is the wither and whose body is the dimension. Read `docs/plans/briefs/LESSONS.md`
first — it is the current technique. **Do not skim other briefs for technique**; the numbers you
need are below.

From the `knees` row of the Nether table:

> `magma_cops` — cracked magma cops, glowing in the seams — no fitting — a recipe.

**About the glow.** The plan wants this piece's seams to be a fourth, fullbright sheet
(`<part>_glow.png`). **That sheet does not exist yet** — it is the one mod change the pack line asks
for and it has not been built. So the seams here are the **brightest values on the master**, and
this piece is on the retro-fit list for the day glow lands. Do not invent a glow sheet; the kit
enumerates sheets by name and would reject it.

## The part

    armorpieces_new
      name:         magma_cops
      anchor:       knees
      namespace:    armorpieces_nether
      datapack:     C:\Users\Matthijs\ArmorPieces\packs\nether\datapack
      resourcepack: C:\Users\Matthijs\ArmorPieces\packs\nether\resourcepack

Then, before you paint:

    armorpieces_set_part
      name:   "Magma Cops"
      recipe: { centre: "minecraft:fire_charge" }

**The centre is `fire_charge`, not `magma_block`.** The plan named `magma_block`, and a magma block
has no flat inventory sprite — the game renders it from a 3D model, so every page that draws the
recipe would draw a checkerboard. `fire_charge` is a flat item, is free across the mod and every
pack, and is if anything a better reading of a knee that is cracked open and burning. The plan file
has been corrected to match.

**No fittings, no static layer, no effects, no loot row.** One sheet, the greyscale master.

## The rig, in Blockbench coordinates

`knees` is a **mirrored** socket on the front of the legs: model **one** side — the **negative x**
side, the left leg — and the game mirrors it.

    left leg box            x  -3.90 ..  0.10    y   0.00 .. 12.00    z  -2.00 ..  2.00
    leggings shell (+0.4)   x  -4.30 ..  0.50    y  -0.40 .. 12.40    z  -2.40 ..  2.40
    boots shell (+0.9)      x  -4.80 ..  1.00    y  -0.90 .. 12.90    z  -2.90 ..  2.90
    the knees anchor        (-1.9, 6, -2)

The leg bone's pivot is at Blockbench **`y = 12` and `x = -1.9`**, not at a box corner — the check
answers `y_local = 12 - y_bb` and `x_local = -x_bb - 1.9` on this bone. Both frames are given for
the budget below; do not convert by hand.

Front is **negative z**. Your own shell is the **leggings**, whose front wall is `z = -2.40`:
everything must sit in front of that. The **boots** shell reaches to `z = -2.90`, and the check
counts a face behind that as buried under the boot — `dragon_knuckles` and every other knee piece
live with the same note, and so will you.

Do not land a face on `x = -4.30`, `x = 0.50`, `x = -4.80`, `x = 1.00`, `z = ±2.40`, `z = ±2.90`,
`y = -0.40`, `y = 12.40`.

## Shape

A rounded cop over the kneecap, cracked open, with a proud boss at its centre and a skirt below it.
**Three cubes, no rotations.** A kneecap is a dome; the crack is paint.

- One bone `base` at the anchor (rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube).

- **`cop`**, one cube in `base` — the plate over the knee:

        x  -3.55 .. -0.25     y   4.35 ..  7.65     z  -3.55 .. -2.55

- **`boss`**, one cube in `base` — the raised centre, standing proud of the cop (front is `-z`):

        x  -2.95 .. -0.85     y   5.05 ..  6.95     z  -4.05 .. -3.55

- **`lip`**, one cube in `base` — the skirt under the cop, thinner and shorter:

        x  -3.35 .. -0.45     y   3.72 ..  4.35     z  -3.35 .. -2.55

`lip` bottoms out at `y = 3.72` and not at `3.75`, which is `shin_spikes`' top plane — a `greaves`
piece, worn with you, and a shared plane there is a real `!` rather than a note. Keep the 0.03.

## Envelope budget, in both frames

    Blockbench      x  -3.65 .. -0.15     y   3.65 ..  7.75     z  -4.15 .. -2.55
    check's frame   x  -1.75 ..  1.75     y   4.25 ..  8.35     z  -4.15 .. -2.55

Same-socket pieces, for the heights and depths to place against (never worn together, so never
compared):

| piece | Blockbench |
|---|---|
| `dragon_knuckles` | x -3.40..-0.40, y 4.60..7.40, z -3.67..-2.53 |
| `poleyns` | x -4.55..-1.55, y 4.90..8.30, z -4.65..-2.65 |
| `fanged_cop` | x -3.50..-0.30, y 3.93..7.40, z -3.95..-3.20 |
| `knee_studs` | x -3.15..-0.65, y 3.90..6.10, z -3.50..-3.00 |
| `padding` | x -4.70..0.85, y 4.40..7.60, z -3.45..-0.50 |

You are a shade wider and a shade deeper than `dragon_knuckles`, which is the Dragonslayer's cop and
the closest thing in shape. `poleyns` is the mod's armoured cop and reaches `z -4.65`; you stop at
`-4.15`, because a magma cop is a crust rather than a plate.

The pieces you are really measured against are the `greaves` and `tassets` pieces on the same leg.
The tightest is `ghast_tendrils` — the pack's own tassets piece — at `x -5.46..-3.45`,
`y 4.82..9.72`, `z -2.30..2.35`: it is behind you in z and outboard in x, and it does not reach you.

## The sheet

One sheet, `magma_cops.png`, the **master**: greyscale, its value a position on the trim ramp.

Magma is a dark crust with light in the cracks, and at this size that is a **high-contrast** piece:
almost everything very dark, and a few pixels near the top of the ramp.

- `cop` and `lip` very dark on every face — near the bottom of the ramp, one flat value, with the
  `up` faces a step lighter so the shape reads.
- `boss` mid-dark, so the centre of the knee is slightly lighter than its rim.
- **The seams.** On the `north` (front) faces of `cop` and `boss`, paint a **branching crack** in the
  brightest value on the piece: one line down the middle of the boss, splitting into two on the cop
  above and below it, one pixel wide. Put a mid value on the pixels immediately either side of each
  crack — heat bleeding into the crust — and leave everything else dark. `armorpieces_paint` paints
  whole faces, so the cracks are the one place this piece needs `texture op:rects`; the face
  rectangles come back in the reply that placed the cubes (`LESSONS.md` 10).
- Nothing on the `east` (inboard) faces needs care beyond a flat dark: it faces the other knee.

Roughly `30 / 50 / 90 / 160 / 245` from crust to crack.

**When the glow sheet lands, this piece is the first retro-fit**: the crack pixels move to
`magma_cops_glow.png` unchanged. Say so in your Lessons so the retro-fit can find them.

## How it is had

The recipe above, and nothing else. **No loot row and no tag** — the pack has no loot group and no
decoration tag yet, on purpose. `reach` passes on the recipe alone.

## Done means

- [ ] The check is clean, or every `!` still standing is one this brief allows.
- [ ] Envelope inside the budget, **reported in the check's frame**.
- [ ] The master painted on every face, cracks included; nothing but greyscale on it.
- [ ] `armorpieces_save` accepted **without** `force`.
- [ ] `python tools/check_authoring.py packs/nether/datapack packs/nether/resourcepack` clean,
      including `reach magma_cops.json: ok` and the recipe centre unique.
- [ ] The tab closed, and the Lessons section below filled in.

`python tools/check_part.py` does not work on an out-of-pack piece, and `python -m modpage build` is
not this pack's page.

**Allowed to force:** faces reported as buried under the **boots** shell — every knee piece in the
mod has them and the boot is not always worn. **Nothing else.**

**Closing the tab is not optional and it is the last thing you do.** The window you are working in is
handed to the next piece's session, and a tab left open is the tab that session finds *active*. Call
`armorpieces_close` when you are done — and also when you are **not** done: if you abandon this piece
or stop to ask a question, close it first (`discard: true` if it should not be kept) and say in your
report what you left behind in the pack folders.

## Lessons from the session

Built as specified: bone `base` at the anchor, three cubes `cop`, `boss`, `lip`, no rotations.

**Two coincidences the brief's coordinates didn't anticipate**, both against a piece on the same
leg (worn together, so both were real `!`s, not hull-test notes): `lip`'s front face at the brief's
literal `z = -3.35` sat exactly on `greaves:greaves`'s `greave` cube, and `cop`+`lip`'s literal
back face at `z = -2.55` sat exactly on `thigh_sheath:tassets`'s `strap_lower`. Nudged by ~0.05:
`lip` became `z -3.30 .. -2.58` and `cop` became `z -3.55 .. -2.60` (the brief's own envelope
budget's z-max of `-2.55` is itself the boundary that produced the second coincidence, so nudging
`lip`'s back toward `-2.58`, i.e. slightly deeper/more-negative rather than shallower, was what
kept it inside the stated budget *and* off the plane — nudging the other direction would have
overshot the budget by 0.05). `boss` needed no change. Final envelope
`x -1.65..1.65  y 4.35..8.28  z -4.05..-2.58`, inside the brief's budget on every axis. Check came
back clean after the nudge — no `!` lines at all, only advisory OVERLAP/near hull-test notes
against other knee/greaves/tassets pieces on the same leg, all left standing per lesson 8. No
`force` was needed or used.

**Where the crack sits on the master (for the glow retro-fit):** `boss`'s `north` face is UV
`11,1 3x2` — the crack column is `x=12` (both rows, value 245), flanked by `x=11` and `x=13`
(value 160) — the whole face, no base 90 survives on it. `cop`'s `north` face is UV `1,1 4x4`; only
the top row (`y=1`, above where `boss` occludes it) and bottom row (`y=4`, below) carry crack:
`x=1` and `x=3` at 245, `x=2` and `x=4` at 160, on both rows. Rows `y=2..3` of `cop.north` are
plain 30 (occluded by `boss` from the front, so it doesn't matter that they're not part of the
branch). When the glow sheet lands, these are the exact texel addresses to copy into
`magma_cops_glow.png` unchanged, then likely blank on the master's crack pixels (or dim them) so
the glow layer carries the brightness instead.

**Base greys used:** `cop`/`lip` at 30 flat, `up` faces at 50 (lesson-style "up faces a step
lighter"); `boss` at 90 flat (all six faces, though `north` is fully overwritten by the crack
rects). Matches the brief's suggested `30/50/90/160/245` ramp exactly.

**Bridge was disconnected for `mcptoolkit` MCP tools this session** (lesson 18/18a): every
`list_outline`/`place_cube`/`element`/`texture` call through the `mcp__mcptoolkit__*` tools
answered `no project is open` right after a working `armorpieces_open`. `MCPTK_URL` and
`ARMORPIECES_BB_URL` were both `http://127.0.0.1:25804` and `/hello` confirmed `active` was my
piece, so I built the whole geometry and the crack pixels over the raw bridge with
`curl -X POST http://127.0.0.1:25804/cmd -d '{"tool":..., "args":..., "session":"'"$MCPTK_SESSION"'"}'`
(env var `MCPTK_SESSION`, not a hardcoded session id — matches lesson 18a exactly, adding the
detail that `MCPTK_SESSION` was already set in the environment and didn't need deriving from
`/hello`'s `claimed_by`). `element {op: remove, id: ...}` wants `id`, not `name`, when addressing
by the element's own name string (the tool's `name` field is for renaming, not addressing) —
`{"name": "main_0"}` failed with `"give id or ids"`.

**Concurrency**: this session shared the window with at least `soul_greaves` and `brute_belt`
(both mid-build). Two `armorpieces_check` calls came back answering for the wrong piece
(`brute_belt`, then `soul_greaves`) right after a normal `armorpieces_open` on my own piece — a
second `armorpieces_open` on my own piece name immediately before the next state-reading call
snapped it back every time, exactly as lesson 17 says. Confirm the piece name in every reply's
first line, not just once.
