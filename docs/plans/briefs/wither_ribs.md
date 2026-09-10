# Brief: Wither Ribs

A piece of **Armor Pieces: Nether** (`armorpieces_nether`), the pack in `docs/plans/pack-line.md`
whose boss is the wither. Read `docs/plans/briefs/LESSONS.md` first — it is the current technique.
**Do not skim other briefs for technique**; every number you need is below.

From the `collar` row of the Nether table:

> `wither_ribs` — the ribcage worn high at the chest — no fitting — dropped by the wither.

The third of the wither's three drops, and the one that turns the other two into a skeleton: with
`wither_mask` on the helm and `wither_heads` on the shoulders, this is the body they belong to.
It goes on `collar`, **not** `crest`: a ribcage on a helmet top reads as nothing.

**This is the piece in the Nether pack that carries the rotation arithmetic.** Six ribs, each its
own bone, each rotated a little further than the one above it. `LESSONS.md` items 1, 3, 4 and 7a are
the whole job. Build it straight, let the check fire on the flat geometry, then aim it.

## The part

    armorpieces_new
      name:         wither_ribs
      anchor:       collar
      namespace:    armorpieces_nether
      datapack:     C:\Users\Matthijs\ArmorPieces\packs\nether\datapack
      resourcepack: C:\Users\Matthijs\ArmorPieces\packs\nether\resourcepack

Then, before you paint:

    armorpieces_set_part
      name: "Wither Ribs"
      loot: [ { table: "minecraft:entities/wither", weight: 1, chance: 1.0 } ]

**No fittings, no static layer, no effects, no recipe.** One sheet, the greyscale master.

## The rig, in Blockbench coordinates

`collar` is **not** a mirrored socket. One attachment, at the base of the throat, and **you model
both sides yourself** — the mirroring below is yours to write, not the game's.

    body box                x  -4.00 ..  4.00    y  12.00 .. 24.00    z  -2.00 ..  2.00
    chestplate shell (+1.0) x  -5.00 ..  5.00    y  11.00 .. 25.00    z  -3.00 ..  3.00
    leggings shell (+0.5)   x  -4.50 ..  4.50    y  11.50 .. 24.50    z  -2.50 ..  2.50
    the collar anchor       (0, 23, -2)

The body bone's pivot is at Blockbench `y = 24`, so the check's frame is `y_local = 24 - y_bb`.
Both frames are given for the budget; do not convert by hand.

Front is **negative z**. Your own shell is the **chestplate**, whose front wall is `z = -3`:
everything you build must sit **in front of** it (more negative than `-3`) or it is buried. Do not
land a face on `z = -3`, `z = -2.5`, `x = ±5`, `x = ±4.5`, `y = 25` or `y = 11`.

## Shape

A sternum bar at the throat with **three ribs on each side**, sweeping outward and down and getting
steeper as they descend. Seven cubes: one sternum, six ribs. **Do not add a fourth pair** — the
fourth would reach into the belt pieces' space, and the piece already reads as a ribcage at three.

- One bone `base` at the anchor (rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube).

- **`sternum`**, one cube in `base` — the bar the ribs hang off:

        x  -0.90 ..  0.90     y  17.80 .. 23.20     z  -3.95 .. -3.25

- **Six ribs.** Each is one cube in its own bone under `base`. Place every rib **unrotated first**,
  as written here, and set the rotations only once the flat geometry checks clean.

  The three on the **+x side** — bone `rib_r1`, `rib_r2`, `rib_r3`, each with its origin (pivot) on
  the sternum's `+x` face so the *far* end is what moves (`LESSONS.md` 7a):

  | bone | pivot | cube, unrotated | rotation |
  |---|---|---|---|
  | `rib_r1` | (0.90, 22.60, -3.60) | x 0.90..4.40, y 22.25..22.95, z -3.85..-3.30 | (0, 0, -22) |
  | `rib_r2` | (0.90, 20.90, -3.60) | x 0.90..4.30, y 20.55..21.25, z -3.85..-3.30 | (0, 0, -30) |
  | `rib_r3` | (0.90, 19.20, -3.60) | x 0.90..4.00, y 18.85..19.55, z -3.85..-3.30 | (0, 0, -38) |

  The three on the **-x side** — `rib_l1`, `rib_l2`, `rib_l3` — are the mirror image: pivot at
  `x = -0.90`, cube running to `-4.40` / `-4.30` / `-4.00`, and the rotation sign **flipped**:
  `(0, 0, 22)`, `(0, 0, 30)`, `(0, 0, 38)`.

**Where the tips land**, so you can confirm the rotations took (rotation about Z:
`Δx' = Δx·cosθ − Δy·sinθ`, `Δy' = Δx·sinθ + Δy·cosθ`):

    rib_r1  tip (4.15, 21.29)      rib_r2  tip (3.84, 19.20)      rib_r3  tip (3.34, 17.29)

and each tip's lowest corner is about 0.3 below the figure quoted, because the rib is 0.7 tall and
the corner rotates too (`LESSONS.md` 3). The lowest point on the piece is `rib_?3`'s outer bottom
corner at about `y = 16.97`.

## Envelope budget, in both frames

    Blockbench      x  -4.60 ..  4.60     y  16.80 .. 23.40     z  -4.05 .. -3.15
    check's frame   x  -4.60 ..  4.60     y   0.60 ..  7.20     z  -4.05 .. -3.15

The floor at `y ≥ 16.80` is not decoration: `sash` (a `belt` piece, worn with you) reaches up to
`y = 16.50`, and a rib that hangs past it is a real overlap rather than a note. That is why the
third rib is the shortest and steepest rather than the longest.

Same-socket pieces, for the depths to place against (never worn together, so never compared):

| piece | Blockbench |
|---|---|
| `gorget` | x -6.50..6.50, y 19.50..25.25, z -3.75..0.75 |
| `nautilus_gorget` | x -3.00..3.00, y 16.85..25.05, z -4.45..-3.15 |
| `bandolier` | x -5.47..5.47, y 15.66..25.20, z -3.65..-2.35 |
| `pendant` | x -3.39..3.39, y 19.00..24.46, z -3.85..-3.10 |

`nautilus_gorget` is the deepest thing on this socket at `z -4.45`; you stop at `-4.05`, which is
proud enough to read and shallow enough not to look like a breastplate.

## The sheet

One sheet, `wither_ribs.png`, the **master**: greyscale, its value a position on the trim ramp.

Charred bone, matched to `wither_mask` and `wither_heads` — the three are one skeleton and must
share a palette:

- The **sternum** is the lightest large surface: its `north` (front) face mid-light with a bright
  edge down the centre, its side faces dark.
- Each **rib** takes a `[top, bottom]` gradient down its `north` face, light where it leaves the
  sternum and darker at the tip — bone catching light near the body and falling into shadow at the
  edge. The `up` face of each rib is lighter than its `down` face; the `down` faces are the darkest
  values on the piece and are what make the ribs look separated.
- The lower ribs a shade darker overall than the upper ones, so the cage recedes.

Roughly `45 / 80 / 120 / 165 / 210` from rib-underside to sternum-highlight. **One
`armorpieces_paint` call for the whole piece**: a `*` wildcard per cube for the base, then the
`north` faces with `[top, bottom]` pairs, then the `up`/`down` overrides (`LESSONS.md` 11).

## How it is had

The wither drops it: the `loot` row above. **No recipe, no tag** — the pack has neither a loot group
nor a decoration tag yet, deliberately. Do not create one. All three wither pieces offer that one
table at chance 1.0 and weight 1; the mod resolves a table to one pool rolled once, so a wither
drops exactly one of the three.

## Done means

- [ ] The check is clean, or every `!` still standing is one this brief allows.
- [ ] Envelope inside the budget, **reported in the check's frame**, and the three tip positions
      confirmed against the numbers above.
- [ ] The master painted on every face; nothing but greyscale on it.
- [ ] `armorpieces_save` accepted **without** `force`.
- [ ] `python tools/check_authoring.py packs/nether/datapack packs/nether/resourcepack` clean,
      including `reach wither_ribs.json: ok`.
- [ ] The tab closed, and the Lessons section below filled in.

`python tools/check_part.py` does not work on an out-of-pack piece, and `python -m modpage build` is
not this pack's page.

**Allowed to force:** an `OVERLAP` or `near` note against a `back` piece (`cloak`, `quiver`,
`pinions`) — those are hull tests on the far side of the body and cannot actually meet your ribs.
Nothing else. A shared **plane** with any `back` or `belt` piece is a real problem: move the face
0.05–0.15 and it goes away (`LESSONS.md` 6).

**Closing the tab is not optional and it is the last thing you do.** The window you are working in is
handed to the next piece's session, and a tab left open is the tab that session finds *active*. Call
`armorpieces_close` when you are done — and also when you are **not** done: if you abandon this piece
or stop to ask a question, close it first (`discard: true` if it should not be kept) and say in your
report what you left behind in the pack folders.

## Lessons from the session

Built exactly as specified: `base` bone at the collar anchor holding a `sternum` cube plus six
rib bones (`rib_r1..3`, `rib_l1..3`), each one cube placed unrotated first per the brief's table,
then rotated by `element set {rotation}` in one pass. The check never showed a `!` at any point —
the flat-geometry pass produced only two `-` notes (`rib_l3`'s and `rib_r3`'s far face sitting on
the body surface at x=±4, from the unrotated cube reaching exactly to the body box edge), and
those notes were gone the moment the rotations landed, exactly as LESSONS.md 1 predicts. Checked
the tip table by hand (rotation formula about Z) for `rib_r1`: pivot (0.90, 22.60), far edge
Δx=3.50 at θ=-22° gives world (4.145, 21.289) against the brief's quoted (4.15, 21.29) — matches
to the hundredth. The final envelope (`x -4.28..4.28 y 0.80..6.98 z -3.95..-3.25` in the check's
frame) landed inside the budget on every axis with room to spare, and the lowest point (rib_?3's
outer bottom corner, computed the same way) came out at Blockbench y≈17.02 — just above the
sash floor at 16.50, matching the brief's "about 16.97" within rounding. No `!` was ever accepted;
nothing needed forcing. `armorpieces_save` accepted without `force`, and
`check_authoring.py packs/nether/datapack packs/nether/resourcepack` reports
`reach wither_ribs.json: ok (found)`. Two unrelated failures in that same run
(`wither_heads.json`, `wither_mask.json` — no recipe/loot/tag yet) belong to the other two wither
pieces, not this one; left untouched per the brief and the "don't touch other parts' files" rule.

Painting: the brief's `[top, bottom]` framing for the rib gradient doesn't actually work as
written — a rib's `north` face is only 1 texel TALL (0.7 units, box-UV height = the cube's Y
size), so there is no "row" to shade top vs bottom; the length the brief wants graded (near
sternum to tip) runs along the face's WIDTH (4 texels, the cube's X size), which `[top,bottom]`
cannot reach at all. Used `pixels` instead — four explicit texels per rib's `north` face, values
following the brief's 45/80/120/165/210 scale, lighter near the sternum and darker at the tip
(and lighter for the upper ribs than the lower ones). One thing to get right: box-UV lays out
columns by the cube's `from`→`to` order on that axis regardless of world sign, so the `+x` ribs
(`from` = near sternum, `to` = tip) and the `-x` ribs (`from` = tip since it's the more negative
value, `to` = near sternum) need the gradient written in OPPOSITE column order — got this from
first principles, not a screenshot; a picture afterward (one of two spent) confirmed it read
correctly, sternum brightest, ribs dimming outward and downward, `down` faces darkest. New
LESSONS.md item written below about the general shape of the trap (a face can be 1 texel in the
gradient axis you expect and full-width in the one you don't) since a thin, elongated cube is not
unique to this piece.

**Bridge-wiring note (not part-specific, but cost real time this session):** the
`mcp__mcptoolkit__*` tools (the shim) reported "no project is open" for this whole session even
after `armorpieces_open` bound the piece and `armorpieces_pieces` showed it active — `get_project_info`
and `list_outline` both failed with a generic "no project" error regardless of the `project`
argument tried. Diagnosis: eight `mcptoolkit_bridge` HTTP servers were listening on
`127.0.0.1:25801-25808` (one per open Blockbench window — other concurrent sessions' work), and
this session's own `MCPTK_URL` env var correctly named `:25805` (the window with `wither_ribs`
open, confirmed by `curl .../hello` showing `"active":"wither_ribs"`), and a direct
`curl -X POST http://127.0.0.1:25805/cmd` with the session's own `MCPTK_SESSION` id worked
perfectly for every tool (`list_outline`, `place_cube`, `add_group`, `element`,
`capture_screenshot`, all confirmed). So the HTTP bridge itself was fine; only the
`mcp__mcptoolkit__*` MCP tool wrapper in this particular session never reached it. Worked around
it for the whole geometry build by calling the bridge's `/cmd` endpoint directly with `Bash`+`curl`,
using the exact tool names/args the wrapper would have used (this is not `risky_eval` — it is the
same declared tools over their own native transport, used because the MCP wrapper was unreachable).
One consequence to know for the next session that hits this: a bone and its cube sharing a name
(the `base`/starter-cube pattern, and here also `rib_r1` bone + `rib_r1` cube by design) makes
`element {op:"set", id:"rib_r1"}` fail with "names 2 elements" over the plain HTTP path exactly as
it would through the MCP tool (LESSONS.md 7b) — use the uuid the `add_group`/`place_cube` reply
already gave you, not the name.
