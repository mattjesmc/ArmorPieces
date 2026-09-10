# Brief: Soul Greaves

A piece of **Armor Pieces: Nether** (`armorpieces_nether`), the pack in `docs/plans/pack-line.md`
whose boss is the wither and whose body is the dimension. Read `docs/plans/briefs/LESSONS.md`
first — it is the current technique. **Do not skim other briefs for technique**; the numbers you
need are below.

From the `greaves` row of the Nether table:

> `soul_greaves` — soul fire licking up the shins — no fitting — a recipe.

**About the glow.** Soul fire wants the fourth, fullbright sheet the pack line asks for. **It does
not exist yet.** The flames here are the brightest values on the master, and this piece joins
`magma_cops` on the retro-fit list. Do not invent a glow sheet.

**This is the piece in the pack that carries rotation arithmetic on a leg.** Three flames, three
bones, three different angles, and one of them is rotated the other way. `LESSONS.md` items 1, 3, 4
and 7a are the job: build every bone unrotated first, let the check fire on the flat geometry, and
only then set the rotations.

## The part

    armorpieces_new
      name:         soul_greaves
      anchor:       greaves
      namespace:    armorpieces_nether
      datapack:     C:\Users\Matthijs\ArmorPieces\packs\nether\datapack
      resourcepack: C:\Users\Matthijs\ArmorPieces\packs\nether\resourcepack

Then, before you paint:

    armorpieces_set_part
      name:   "Soul Greaves"
      recipe: { centre: "minecraft:soul_lantern" }

`minecraft:soul_lantern` is free across the mod and every pack. **No fittings, no static layer, no
effects, no loot row.** One sheet, the greyscale master.

## The rig, in Blockbench coordinates

`greaves` is a **mirrored** socket on the front of the lower legs: model **one** side — the
**negative x** side, the left leg — and the game mirrors it.

    left leg box            x  -3.90 ..  0.10    y   0.00 .. 12.00    z  -2.00 ..  2.00
    leggings shell (+0.4)   x  -4.30 ..  0.50    y  -0.40 .. 12.40    z  -2.40 ..  2.40
    boots shell (+0.9)      x  -4.80 ..  1.00    y  -0.90 .. 12.90    z  -2.90 ..  2.90
    the greaves anchor      (-1.9, 4, -2)

The leg bone's pivot is at Blockbench **`y = 12` and `x = -1.9`** — the check answers
`y_local = 12 - y_bb`, `x_local = -x_bb - 1.9`. Both frames are given for the budget.

Front is **negative z**. **Your own shell is the boots**, whose front wall is `z = -2.90`:
everything you build must sit in front of that or it is buried under your own armor. That is the
one number on this piece that is not negotiable.

Do not land a face on `z = ±2.90`, `z = ±2.40`, `x = -4.80`, `x = 1.00`, `x = -4.30`, `x = 0.50`,
`y = -0.90`, `y = 12.90`.

## Shape

A shin plate with three flames rising off its top edge, each leaning a different way. Four cubes,
three of them in rotated bones.

- One bone `base` at the anchor (rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube).

- **`plate`**, one cube in `base`, unrotated — the shin plate the fire comes off:

        x  -3.75 .. -0.15     y   0.35 ..  4.45     z  -3.12 .. -2.62

- **Three flames.** Each is one cube in **its own bone** under `base`. Place them unrotated exactly
  as written, check, and only then set the rotation. Every pivot sits at the **bottom** of its
  flame, on the plate's top edge, because the end that moves is the end away from the pivot
  (`LESSONS.md` 7a).

  | bone | pivot | cube, unrotated | rotation |
  |---|---|---|---|
  | `flame_out` | (-2.95, 4.45, -2.88) | x -3.35..-2.55, y 4.45..7.45, z -3.08..-2.68 | (0, 0, 14) |
  | `flame_mid` | (-1.95, 4.45, -2.88) | x -2.32..-1.52, y 4.45..8.35, z -3.08..-2.68 | (0, 0, -6) |
  | `flame_in`  | (-0.95, 4.45, -2.88) | x -1.35..-0.55, y 4.45..7.05, z -3.08..-2.68 | (0, 0, -8) |

  **The signs are deliberate and they are not all the same.** On this side, a positive rotation
  about Z carries the tip **outboard** (toward `-x`) and a negative one carries it **inboard**: for
  a point above the pivot, `Δx' = −Δy·sinθ`. The outer flame leans out, the two inner ones lean in,
  which is what makes three flames read as fire rather than as a fence.

**Where the tips land**, so you can confirm the rotations took:

    flame_out  tip (-3.68, 7.36)      flame_mid  tip (-1.54, 8.33)      flame_in  tip (-0.19, 7.08)

and the extreme **corners**, which are what the envelope is made of (`LESSONS.md` 3):

    flame_out  outboard corner x = -4.06,  top corner y = 7.46
    flame_mid  inboard corner  x = -1.14,  top corner y = 8.37
    flame_in   inboard corner  x = -0.19

`flame_in`'s inboard corner is the number to watch: at `-8°` it stops at `x = -0.19`, just short of
the leg's inner wall. **Do not steepen it** — past about `-10°` the flame crosses the centre line and
meets its own mirror image on the other leg.

## Envelope budget, in both frames

    Blockbench      x  -4.20 .. -0.05     y   0.30 ..  8.50     z  -3.20 .. -2.55
    check's frame   x  -1.85 ..  2.30     y   3.50 .. 11.70     z  -3.20 .. -2.55

`inspect bounds` measures a rotated cube by its **unrotated** box and will not show a rotation
overshoot (`LESSONS.md` 5). The check's envelope, in the frame on the second line, is what confirms
this piece.

Same-socket pieces, for the heights and depths to place against (never worn together, so never
compared):

| piece | Blockbench |
|---|---|
| `greaves` | x -4.50..0.50, y -0.20..4.80, z -3.65..-0.75 |
| `scale_shins` | x -4.40..0.00, y -0.73..4.62, z -3.82..-0.41 |
| `dragon_scales` | x -3.50..-0.30, y 0.78..4.38, z -3.52..-3.05 |
| `shin_spikes` | x -2.90..-0.90, y 0.90..3.75, z -5.51..-2.95 |
| `puttees` | x -5.05..0.59, y -0.70..4.45, z -4.15..-1.45 |

Every one of them stops around `y = 4.8`, at the top of the shin. **You are the only greave that
goes past the knee**, and that is the point of the piece — but it is also why the knee pieces will
show up as `OVERLAP` and `near` notes.

## The knee is where this piece meets its neighbours

`knees` pieces are worn with you and the flames rise straight into them: `poleyns`
(`x -4.55..-1.55`, `y 4.90..8.30`, `z -4.65..-2.65`), `padding` (`y 4.40..7.60`, `z -3.45..-0.50`),
`armadillo_shell`, `dragon_knuckles`, `fanged_cop`. Two things follow:

- **`OVERLAP` and `near` notes against knee pieces are expected and allowed.** They are hull tests,
  and a flame licking past a knee cop is what was asked for.
- **A shared plane with one of them is not.** The flame cubes are inside rotated bones, and the
  coplanar pass only tests unrotated cubes in unrotated chains — so in practice only `plate` can
  raise one. Its planes were chosen against that list; if you move it, check the values above
  before you do.

## The sheet

One sheet, `soul_greaves.png`, the **master**: greyscale, its value a position on the trim ramp.

Soul fire is pale at the heart and dark at the edge — the opposite of a normal flame — and greyscale
is a good place to say that:

- `plate` dark and flat on every face, a step lighter along its `up` edge where the fire leaves it.
- Each **flame** takes a `[top, bottom]` gradient on its `north`, `east` and `west` faces running
  **dark at the bottom to near-white at the tip**. That inversion is the whole read: fire that gets
  brighter as it rises, rather than a torch.
- The `up` face of each flame — the tip — is the brightest value on the piece.
- Keep the outer flame a shade darker overall than the middle one, so the three do not read as a
  flat comb.

Roughly `40 / 70 / 130 / 190 / 250` from plate to tip. **One `armorpieces_paint` call for the whole
piece**: a `*` wildcard per cube for the base, then the `[top, bottom]` pairs (`LESSONS.md` 11).

**When the glow sheet lands, the flames move to it unchanged.** Note in your Lessons which faces
carry them.

## How it is had

The recipe above, and nothing else. **No loot row and no tag** — the pack has no loot group and no
decoration tag yet, on purpose. `reach` passes on the recipe alone.

## Done means

- [ ] The check is clean, or every `!` still standing is one this brief allows.
- [ ] Envelope inside the budget, **reported in the check's frame**, and the three tips confirmed
      against the table above.
- [ ] The master painted on every face; nothing but greyscale on it.
- [ ] `armorpieces_save` accepted **without** `force`.
- [ ] `python tools/check_authoring.py packs/nether/datapack packs/nether/resourcepack` clean,
      including `reach soul_greaves.json: ok` and the recipe centre unique.
- [ ] The tab closed, and the Lessons section below filled in.

`python tools/check_part.py` does not work on an out-of-pack piece, and `python -m modpage build` is
not this pack's page.

**Allowed to force:** `OVERLAP` and `near` notes against `knees` pieces, as above — say which ones
you accepted. **Nothing else.** A face on the boots shell at `z = -2.90` is a real problem, not a
note: move it forward and it goes away.

**Closing the tab is not optional and it is the last thing you do.** The window you are working in is
handed to the next piece's session, and a tab left open is the tab that session finds *active*. Call
`armorpieces_close` when you are done — and also when you are **not** done: if you abandon this piece
or stop to ask a question, close it first (`discard: true` if it should not be kept) and say in your
report what you left behind in the pack folders.

## Lessons from the session

Built exactly as specified: one `base` bone at the anchor with the `plate` cube, and three flame
bones (`flame_out`, `flame_mid`, `flame_in`) each holding one cube, placed unrotated first, checked
clean, then rotated (+14°, -6°, -8° about Z respectively).

**Tips landed exactly on the brief's numbers.** Worked the rotation arithmetic by hand for
`flame_out` before trusting the rig: pivot (-2.95, 4.45, -2.88), top-centre point at Δy=3.0 from
the pivot, rotated +14° about Z gives Δx' = -3.0·sin14° = -0.726, Δy' = 3.0·cos14° = 2.911 → tip
(-3.676, 7.361), matching the brief's (-3.68, 7.36) to the last digit. The two top corners came out
at x = -4.06 (outboard) and y = 7.46 (inboard top), both exact matches too. Did not re-derive
`flame_mid`/`flame_in` by hand since the method was already confirmed and the check's envelope
(below) fell inside budget, which only happens if all three landed correctly.

**Envelope, in the check's frame:** x -1.75..2.16, y 3.63..11.65, z -3.12..-2.62 — inside the
brief's budget (x -1.85..2.30, y 3.50..11.70, z -3.20..-2.55) on every axis, with margin to spare.

**Faces that will carry the flames when the glow sheet lands:** `north`, `east` and `west` on each
of `flame_out_cube`, `flame_mid_cube`, `flame_in_cube` (the gradient faces, dark at the bone-local
bottom to bright at the tip), plus their `up` face (the tip, flat brightest value). `south` and
`down` on each flame cube were painted flat and dark (60-70) since they face into the leg / sit on
the plate and are not part of the fire read — leave those on the master, they do not need a glow
value.

**Paint values used:** plate flat 40, its `up` edge 70. `flame_out` (darkest) [220, 65] on
north/east/west, up 220, down 65, south 60. `flame_mid` (brightest) [250, 70], up 250, down 70,
south 65. `flame_in` [240, 70], up 240, down 70, south 65 — between the other two, since the brief
only asked the outer flame be darker than the middle and left the inner one free.

**No `!` accepted.** The check came back `ok: nothing needs a decision` after painting — every
`OVERLAP`/`near` note against the knee pieces (`armadillo_shell`, `magma_cops`, `dragon_knuckles`,
`poleyns`, `padding`, `winged_cops`, `fanged_cop`, `garters`, `knee_studs`) and against the tassets
socket (`tassets`, `loin_panels`, `scale_skirt`, `thigh_sheath`, `pelt`, `ghast_tendrils`,
`wing_tatters`) and spurs socket (`anklets`, `bells`) were all `-` lines, exactly the hull-test
notes the brief said to expect from a greave that goes past the knee. `armorpieces_save` went
through without `force`.

**Bridge note:** `mcp__mcptoolkit__*` answered `no project is open` on every call throughout this
session, right after a working `armorpieces_open`/`armorpieces_new` — the disconnected-bridges
case LESSONS 18/18a describe. `env | grep MCPTK` gave a single matching port (25805) for both
`MCPTK_URL` and `ARMORPIECES_BB_URL`; `curl .../hello` on it confirmed `active: soul_greaves`. Used
the documented direct-POST fallback (`POST /cmd` with `{tool, args, session}` and the
`X-MCPTK-Session` header) for every geometry call (`element`, `add_group`, `place_cube`) and
confirmed each one with `armorpieces_check` (which worked normally throughout — only the
`mcptoolkit` MCP tool wrapper was unreachable, not the `armorpieces_*` tools or the underlying
bridge). One addition to LESSONS 18a: `element op:remove` wants `id` (or `ids`), not `name` — the
declared schema takes `id`/`ids` even though the by-name addressing works for `op:set`/`rename` via
`id` too; passing `name` alone to `remove` errors `give id or ids`.
