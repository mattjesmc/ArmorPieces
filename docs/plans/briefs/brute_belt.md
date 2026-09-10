# Brief: Brute Belt

A piece of **Armor Pieces: Nether** (`armorpieces_nether`), the pack in `docs/plans/pack-line.md`
whose boss is the wither and whose body is the dimension. Read `docs/plans/briefs/LESSONS.md`
first — it is the current technique. **Do not skim other briefs for technique**; the numbers you
need are below.

From the `belt` row of the Nether table:

> `brute_belt` — the piglin brute's gold-studded belt — fitting `inlay` — centre `golden_axe`.

A piglin brute wears one thing worth taking, and this is it: a heavy strap with square gold studs
and a slab of a buckle. Netherite with gold hardware is the pack's look, and this is the piece that
says so most plainly.

## The part

    armorpieces_new
      name:         brute_belt
      anchor:       belt
      namespace:    armorpieces_nether
      datapack:     C:\Users\Matthijs\ArmorPieces\packs\nether\datapack
      resourcepack: C:\Users\Matthijs\ArmorPieces\packs\nether\resourcepack

Then, before you paint:

    armorpieces_set_part
      name:     "Brute Belt"
      fittings: [ "armorpieces:inlay" ]
      recipe:   { centre: "minecraft:golden_axe" }

That call creates `part_inlay`, the mask sheet, and writes the template recipe (a paper ring around
the centre item). `minecraft:golden_axe` is free: no other `template_*.json` in the mod or in any
pack uses it. **No static layer, no effects, no loot row.**

## The rig, in Blockbench coordinates

`belt` is **not** a mirrored socket: one attachment at the waist, and you model the whole ring.

    body box                x  -4.00 ..  4.00    y  12.00 .. 24.00    z  -2.00 ..  2.00
    chestplate shell (+1.0) x  -5.00 ..  5.00    y  11.00 .. 25.00    z  -3.00 ..  3.00
    leggings shell (+0.5)   x  -4.50 ..  4.50    y  11.50 .. 24.50    z  -2.50 ..  2.50
    the belt anchor         (0, 14, 0)

The body bone's pivot is at Blockbench `y = 24`, so the check's frame is `y_local = 24 - y_bb`.

**Your own shell is the leggings** (`belt` is a leggings socket), but the **chestplate** is the one
you have to clear: it is worn over the leggings and its walls are at `x = ±5`, `z = ±3`. A belt
inside those is a belt nobody sees. Every belt in the mod solves this the same way — `buckled_belt`
sits at `x ±5.50`, `girdle` at `±5.86` — and so do you.

Do not land a face on `x = ±5`, `x = ±4.5`, `z = ±3`, `z = ±2.5`, `y = 11`, `y = 11.5`, `y = 25`.

## Shape

A band around the waist, a buckle plate on the front of it, and a short tab hanging from the buckle.
**Three cubes, no rotations.** The studs are paint, not geometry — at 1/16 of a block a modelled
stud is a wasted cube and a lit pixel is a stud.

- One bone `base` at the anchor (rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube).

- **`band`**, one cube in `base` — the strap, enclosing the waist. Its inboard walls are inside the
  body and never seen, which is how every band in the mod is built:

        x  -5.35 ..  5.35     y  12.85 .. 15.15     z  -3.35 ..  3.35

- **`buckle`**, one cube in `base` — a slab across the front of the band (front is `-z`):

        x  -1.55 ..  1.55     y  12.65 .. 15.35     z  -3.88 .. -3.35

- **`tab`**, one cube in `base` — the strap end hanging below the buckle:

        x  -0.95 ..  0.95     y  11.35 .. 12.85     z  -3.78 .. -3.35

`tab` stops at `y = 11.35`, which is 0.15 clear of the leggings shell's floor at `11.50`. Do not
lengthen it: below that plane it is inside the boot's territory and the clearance line changes.

## Envelope budget, in both frames

    Blockbench      x  -5.45 ..  5.45     y  11.25 .. 15.45     z  -3.95 ..  3.45
    check's frame   x  -5.45 ..  5.45     y   8.55 .. 12.75     z  -3.95 ..  3.45

Same-socket pieces, for the heights and depths to place against (never worn together, so never
compared):

| piece | Blockbench |
|---|---|
| `buckled_belt` | x -5.50..5.50, y 12.50..15.50, z -4.50..3.50 |
| `girdle` | x -5.86..5.86, y 11.75..14.25, z -4.00..3.86 |
| `fauld` | x -5.35..5.35, y 9.40..13.50, z -4.02..4.02 |
| `chain_belt` | x -5.50..5.50, y 8.60..12.80, z -3.80..3.50 |

You are a hair tighter than `buckled_belt` in every axis, which is right: the brute's belt is a
strap, and `buckled_belt` is the mod's generic wide belt. Do not out-reach it.

## The sheets

**`part` (master), greyscale.** Worn leather, dark and matte, so the studs on it can be the bright
thing:

- `band` flat mid-dark on every face, one value, no gradient — leather that has been sat on.
- **The studs.** Every cube's face rectangles come back in the reply that placed it
  (`LESSONS.md` 10), and box UV means one unit is one pixel: the band's `north` face is about 11
  pixels wide and 2 tall. Paint **five single-pixel studs along the middle row of the `north` face**,
  spaced two pixels apart and centred on the face, and **three more on each of `east` and `west`**.
  Bright — near the top of the ramp. `armorpieces_paint` addresses whole faces, so the studs are the
  one place this piece needs `texture op:rects`; take the rectangles from the placement reply rather
  than guessing.
- `buckle` a step lighter than the band with its `up` edge brighter still, so it reads as metal
  standing off leather. Leave a dark one-pixel border around its `north` face: that shadow is what
  makes it a slab rather than a sticker.
- `tab` the darkest thing on the piece, with a light bottom edge.

Roughly `45 / 75 / 110 / 170 / 225` from tab-shadow to stud.

**`part_inlay` (mask), greyscale.** The gold is the **studs, the buckle and the tab's tip** — not
the strap. Concretely: every face of `buckle`, plus **the same stud rectangles** you painted on the
master, at the same coordinates on this sheet. One flat mid value; a mask is greyscale and its job
is to say *where*, not how bright. Nothing on the band outside the studs, and nothing on `tab`
except its bottom two pixel rows.

A mask pixel outside the master's silhouette is a `!`; both sheets are laid out identically, so
copying the rectangles across is safe.

## How it is had

The recipe above, and nothing else. **No loot row and no tag** — the pack has no loot group and no
decoration tag yet, on purpose (a tag naming nothing fails a check), and the pack-line plan puts
this piece in the craftable half. `reach` passes on the recipe alone.

## Done means

- [ ] The check is clean, or every `!` still standing is one this brief allows.
- [ ] Envelope inside the budget, **reported in the check's frame**.
- [ ] Both sheets painted: master everywhere, `part_inlay` on the studs, the buckle and the tab tip.
- [ ] `armorpieces_save` accepted **without** `force`.
- [ ] `python tools/check_authoring.py packs/nether/datapack packs/nether/resourcepack` clean,
      including `reach brute_belt.json: ok` and the recipe centre unique.
- [ ] The tab closed, and the Lessons section below filled in.

`python tools/check_part.py` does not work on an out-of-pack piece, and `python -m modpage build` is
not this pack's page.

**Allowed to force:** the band's inboard faces being buried or unpainted, if the check calls them
out — that is what a band around a waist is; and an `OVERLAP` note against a `back` piece
(`cloak`, `quiver`, `pinions`), which is a hull test around the far side of the body. **Nothing
else.**

**Closing the tab is not optional and it is the last thing you do.** The window you are working in is
handed to the next piece's session, and a tab left open is the tab that session finds *active*. Call
`armorpieces_close` when you are done — and also when you are **not** done: if you abandon this piece
or stop to ask a question, close it first (`discard: true` if it should not be kept) and say in your
report what you left behind in the pack folders.

## Lessons from the session

Built exactly as specified: `base` bone at the anchor holding three cubes (`band`, `buckle`, `tab`),
no rotations. Renamed the starter bone `main` → `base` and removed its starter cube before placing
the three geometry cubes in one `place_cube` call, which is how their face rectangles were known for
painting (band's `north` face came back `11x3`, not `11x2` as the brief estimated — box UV rounds a
2.3-unit height up to 3 texels, so the "middle row" of the 3-row face, not the 2-row one, is what
the studs sit on).

The stud rectangles were **not** something `armorpieces_paint`'s `faces` map could place — that
tool only does whole faces or `[top, bottom]` gradients, never individual texels within a face — but
its own `pixels` parameter (a list of `{x, y, value}`) did the job directly, in the same call as the
whole-face base colours, no `texture op:rects` needed. One `armorpieces_paint` call painted the
master's whole-face bases *and* the buckle's one-pixel dark border *and* all eleven stud pixels
together; a second call did the `part_inlay` mask (buckle's six faces, plus the same eleven stud
pixel addresses, plus tab's four side faces + `down`, since `tab`'s side faces were only 2 texels
tall — "the bottom two pixel rows" of a 2-row face is the whole face, so masking `tab.north/south/
east/west/down` and leaving `tab.up` bare (it's inside the buckle's overlap, unseen) satisfied the
brief without further pixel work).

Both `mcptoolkit` MCP tools (`list_outline`, `get_project_info`, `risky_eval`) answered
`no project is open` right after a working `armorpieces_open` — LESSONS.md #18's disconnected-bridge
case, confirmed with the two-call check it recommends. The 18a fallback worked exactly as described:
`env | grep MCPTK` gave the port and session id, `curl .../hello` confirmed the piece was active
there, and `curl -X POST .../cmd` with `{tool, args, session:{id, client, profile}}` ran
`list_outline`, two `element` calls (rename, remove) and `place_cube` with the same argument shapes
the wrapped tools document. Only the geometry setup needed this path — painting, part data and save
all went through the normal `armorpieces_*` tools once the bones and cubes existed.

Confirmed LESSONS.md #17 firsthand: two `armorpieces_check` calls in a row, with no other tool
between them, each answered for a different sibling piece being built concurrently on the same
window (`magma_cops`, then `soul_greaves`) rather than `brute_belt`. Re-issuing `armorpieces_open`
on my own piece name immediately before `armorpieces_check` snapped the active tab back both times
and the very next check was correct — this needs doing before *every* read, not just once at the
start of a session, exactly as the lesson says.

Check came back clean on the first paint pass: no `!` lines at all, `ok: nothing needs a decision`.
The two `OVERLAP` notes (against `wing_roots:back`'s plate and `cloak:back`'s banner) are advisory
`-` lines, not problems — they're exactly the back-piece hull grazing the brief pre-authorised, and
`armorpieces_save` did not need `force` since no `!` stood at all. Envelope
(x -5.35..5.35, y 8.65..12.65, z -3.88..3.35) landed inside the brief's budget on every axis.
`check_authoring.py` on the pack showed `data brute_belt.json: ok`, `recipe template_brute_belt.json:
ok (on)`, `reach brute_belt.json: ok (crafted)` — the script's overall exit code was 1, but only
because two *other*, concurrently-mid-build pieces in the same pack (`magma_cops`, `soul_greaves`)
had no recipe/loot/tag yet; nothing in that output named `brute_belt`.
