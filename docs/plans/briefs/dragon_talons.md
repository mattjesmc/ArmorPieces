# Brief: Dragon Talons

A piece of **Armor Pieces: Dragonslayer** (`armorpieces_dragon`), the first pack of the line in
`docs/plans/pack-line.md` — netherite plate with amethyst light, every piece a part of her body.
The pack folder already exists and is empty; you are one of its first four pieces. Skim
`docs/plans/briefs/coral_crown.md`'s **Lessons** section first: it is the most recent pack-external
piece and it says what held.

From the `spurs` row of the Dragonslayer table:

> `dragon_talons` — the hind claws at the heels — no fitting — centre `chorus_flower`.

**Part.** `armorpieces_dragon:dragon_talons`, socket `spurs` only. Display name "Dragon Talons".
**No fittings, no static layer, no effects, no loot.** One sheet — the greyscale master. The pack's
black-and-purple look comes from the armor and its trim, not from this piece's own colour, which is
how the mod's own parts work.

The name shadows the mod's own `talons`. That is allowed and deliberate — the qualifier is the
subject, exactly as `nautilus_gorget` sits beside `gorget`. Same socket as nothing you must clear:
same-socket parts are never worn together and the check ignores them.

Create it with `armorpieces_new` and **name both pack folders and the namespace explicitly**, or it
will be written into the mod:

    name: dragon_talons
    anchor: spurs
    namespace: armorpieces_dragon
    datapack: C:\Users\Matthijs\ArmorPieces\packs\dragon\datapack
    resourcepack: C:\Users\Matthijs\ArmorPieces\packs\dragon\resourcepack

Then, before painting:

    armorpieces_set_part { name: "Dragon Talons",
                           recipe: { centre: "minecraft:chorus_flower", craftable: true } }

The reply will say `static_created: false` and `sheets_created: []` — this piece has one sheet and
that is correct. Set the part data before you paint anyway: it is the step that writes the data
half, and doing it in the same order as every other piece keeps the report comparable.

## The rig, in Blockbench coordinates

`spurs` is a **mirrored** socket: model ONE side — the left leg, which is the **negative x** side in
Blockbench — and the game mirrors it.

    left leg box            x -3.9 .. 0.1    y 0 .. 12    z -2 .. 2
    leggings shell (+0.4)   x -4.3 .. 0.5    y -0.4 .. 12.4   z -2.4 .. 2.4
    boots shell (+0.9)      x -4.8 .. 1.0    y -0.9 .. 12.9   z -2.9 .. 2.9
    the spurs anchor        (-1.9, 2, 2)

Front is **negative z**; the spurs anchor is on the **back** of the ankle, at positive z. This is a
boots socket, so the shell you must not touch is the **boots** one: its rear plane is `z = 2.9`. Sit
a tenth off it, never on it — a face in that plane z-fights.

## Shape

Not a spur and not a rowel. Her hind foot's claws, worn at the heel: **three tapered talons** off a
short root, sweeping back and down, the middle one longest.

- One bone `base` at the anchor (rename the starter `main`; never call a bone `root`).
- **A short root block** on `base`: `x -3.2..-0.6`, `y 1.6..2.6`, `z 3.0..3.5`. That is 0.1 clear of
  the boots shell's `z = 2.9` and it is what makes the talons look mounted rather than glued on.
- **Three talons**, each its own child bone off the root so it can sweep, each built as two cubes in
  the unrotated pose — a `1 x 1` root segment and a `0.75 x 0.75` tip, overlapping by a quarter unit
  at the joint, so the claw tapers:
  - outer talon — around `x -3.1`, the shortest, sweeping about 25° down from horizontal;
  - middle talon — around `x -1.9`, the longest, about 35°;
  - inner talon — around `x -0.9`, middle length, about 30°.
  - Sweep them **back and down**: the tips land around `z 4.4..4.6`, `y 0.6..1.2`. Rotate the
    **bones**, never the cubes, model every segment upright in the unrotated pose, and compute where
    the chain lands (pivot plus length times cos and sin of the cumulative angle) before placing —
    the reply confirms it to a hundredth, so nothing needs nudging.
  - Fan them slightly in x as well, 5–8°, so the three do not read as one comb.

**Your envelope budget, and it is a hard one.** Stay inside `x -3.4 .. -0.4`, `y 0.5 .. 3.2`,
`z 1.0 .. 4.7`. Three other pieces of this pack are being built against the same leg on the same
budget and none of them may meet you: `dragon_scales` stays forward of `z -1.0` and stops at
`y 4.4`, `dragon_knuckles` starts at `y 4.5`, `wing_tatters` stops at `y 6.4`. **Nothing forward of
`z +1.0`** — that is the line that keeps the talons off the shin.

**What this socket makes you watch.** `spurs` rides the leg and sits at the ankle, so a talon that
sweeps too far down clips the ground plane on every step and one that sweeps too far back reads as a
tail. Keep the tips above `y 0.5`. The `armorpieces_new` reply lists every other part on this bone
with its envelope in both frames — read it once and say in your report what you cleared and by how
much.

## Sheets

One sheet: `dragon_talons.png`, the **master**, greyscale, its value a position on the wearer's trim
ramp. Alpha is the silhouette and the only source of truth.

Claw, not metal, and it reads as claw by its shading rather than its colour: each talon lightest at
the root and darkening toward the tip is wrong — do it the other way, a **dark root and a pale,
almost white tip**, which is what makes a claw read as a claw at three metres. The root block stays
mid grey so the talons stand out of it, and every `down` face is the darkest value on the sheet. A
ramp of roughly `55 / 90 / 130 / 180 / 240` across down-faces, root-block, talon-root, talon-body,
talon-tip is enough; `*.*` for a base then the faces that differ is the cheap way to leave nothing
unpainted. A tip segment under a unit thick unwraps to one texel, so the taper reads from the
silhouette and the value, not from detail inside the face. Count your paint calls and say what the
face painter did and did not cover.

## Recipe

Centre item `minecraft:chorus_flower`, paper ring, craftable. Verified unused by any
`template_*.json` in the mod or in any pack. The result is the `spurs` template.

## Done means

`armorpieces_save` accepted **without** `force`;
`python tools/check_authoring.py packs/dragon/datapack packs/dragon/resourcepack` clean; the Lessons
section below filled in.

Two things this piece does **not** do, because it is not the mod's own:
`python tools/check_part.py` does not work for an out-of-pack piece — the bridge's own check,
printed after every reply, is the check here. And do **not** run `python -m modpage build`: this
pack is not on the mod's page, and there is no `modpage.yml` line to add.

## Lessons from the session

Built as: `base` bone at the spurs anchor (renamed from the starter `main`), holding the `root`
cube (renamed from the starter cube), resized to exactly the brief's box (`x -3.2..-0.6, y
1.6..2.6, z 3.0..3.5`, inflate removed). Three child bones off `base` — `talon_outer`,
`talon_middle`, `talon_inner` — each pivoted on the root's back face (`z = 3.5`) at its own `x`/`y`,
each holding two cubes built **upright in the unrotated pose** (a 1×1 root segment from local `z
0..1` and a 0.75×0.75 tip overlapping it by a quarter unit from local `z 0.75..`), then the *bone*
rotated (never the cubes): outer `[25, -6, 0]`, middle `[35, 0, 0]`, inner `[30, 6, 0]` (x = pitch
down, y = yaw fan). `armorpieces_check`'s bone-local envelope (not `inspect bounds`, which openly
measures rotated cubes by their unrotated box and is useless here) is what actually confirms a
rotated placement — it applies the real rotation and reports the true AABB, so it is what to read
after every rotation, not the generic inspect tool.

**Hand math needed one correction the check caught.** My pre-placement arithmetic (pivot + reach ×
cos/sin of the pitch) gets the *centreline* tip right, but the piece's `z` envelope maximum comes
from a **cube corner**, not the centreline — the tip cube's own half-width, rotated by the same
pitch, adds `halfwidth × sin(pitch)` on top of the centreline reach. That pushed the first pass
0.06–0.08 past the brief's hard `z ≤ 4.7`. Fixed by trimming each tip segment's far edge (shortest
first: outer and inner lost more length than middle, since their yaw added a further small `z`
term) until the checked envelope read `z 3.00..4.66` — 0.04 clear of the limit. Lesson for the next
rotated-bone piece: budget for the corner, not the centreline, or leave more slack before the first
check.

Cleared, all in bone-local Blockbench coordinates (converted from the check's mirrored +Y-down
report): `x -3.36..-0.49` (budget `-3.4..-0.4`, 0.04–0.09 clear both sides), `y 0.77..2.60` (budget
`0.5..3.2`, comfortably inside, tips well above the `y 0.5` floor), `z 3.00..4.66` (budget
`1.0..4.7`, 0.04 clear at the tight end, nowhere near the `z +1.0` forward line). Against the same
socket's own six same-socket parts (never worn together, never compared) and the eleven other
`left_leg` sockets worn together, `armorpieces_check` reported "all clear by more than half a
unit" with no adjustment needed — the ankle-height, back-of-leg placement this brief specifies
doesn't reach into knee or greaves territory at all.

One paint call, one sheet (the master; no fittings, no static layer — `set_part` correctly reported
`sheets_created: []`). Painted `*.*` to 130 (talon-root default) as the base pass, then `*.down` to
55 (every down face, darkest, in one selector), then the `root` block's five side faces to 90, then
each tip's four non-cap faces (`up`/`north`/`east`/`west`) to 180 and its outward `south` cap
(local +z, the pointed end after the back-sweep) to 240. That's the brief's full five-value ramp in
one call covering all 42 faces with zero left unpainted — `armorpieces_check` read "ok: nothing
needs a decision" straight after.

For the next piece of this pack: creating a piece while another pack piece is concurrently open
under the same MCP session id can hang the bridge with `held_by: ... work in your own project` on
every `armorpieces_*` call, including `armorpieces_pieces` and `armorpieces_new` — this cleared on
its own within a few minutes without intervention (the other session finished and released its
binding), so if it happens, retry `armorpieces_new` rather than trying to force or steal the other
project's binding.
