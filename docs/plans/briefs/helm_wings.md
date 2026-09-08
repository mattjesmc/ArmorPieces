# Brief: Helm Wings (REWORK)

This is a **rework of a shipped part**, not a new one. `armorpieces:helm_wings` is one of the
original twenty, authored by hand long before the bridge. The datapack half is right and must
survive; the geometry and the master sheet are to be rebuilt.

Open it with `armorpieces_open armorpieces:helm_wings`. Do **not** create a new piece, and do not
delete the part JSON.

This is also the second measured run of the mcp-toolkit loop kit, now at toolkit 0.124.0 with the
five fixes the first run found. Nothing about the job changes.

## What is wrong with the shipped model

- **It is a second Horns.** Both parts on this socket have the same four bones in the same chain —
  `boss` → `horn1` → `horn2` → `horn3` — anchored at the same `(4, -5, 0)`, and both are a tapering
  cone curling off the temple. `horns` reaches `x 3.61..8.96, y -14.36..-5.00, z -2.00..2.00`;
  `helm_wings` reaches `x 4.00..7.98, y -12.43..-5.00, z -2.00..5.29`. The only real difference is
  that this one curls backward. A player choosing between the two sees one silhouette offered twice,
  and the socket has only two parts to offer.
- **The boss sits on the head.** The check reports `boss's x face at 4 lies on the body surface` and
  `boss's y face at -8 lies on the body surface` — two faces on a shell plane. They will z-fight.
- **It laps the laurel.** `OVERLAP: boss into laurel:brow's leaf_sl2 by 0.25 x 0.88 x 1.13`. `brow`
  and `horns` are different sockets, so the two are worn together; the reply to `armorpieces_open`
  lists laurel's envelope in both frames, so this is placeable from numbers.

## What must not change

- Part id `armorpieces:helm_wings`, display name **"Helm Wings"**, socket **`horns`** only.
- **No fittings**, and none are to be added. Neither part on this socket has one; the master alone
  carries the form on the trim ramp.
- **No recipe.** `helm_wings` is loot-only. Do not set one, do not pick a centre item, do not touch
  the recipe panel.
- **The loot field on the part file is exact and already correct** — `end_city_treasure` weight 2
  chance 0.1, `ancient_city` weight 1 chance 0.05. Leave `armorpieces_set_part` alone entirely:
  there is no mask sheet to create and nothing on the datapack half to change.
- `horns` is a MIRRORED socket. Model ONE side; the game mirrors it.
- Do not touch `tools/paint_helm_wings_master.py`. A bridge rework orphans a part's hand painter and
  removing it is the orchestrator's job, not yours.

## What it should be

The winged helm: a **wing**, flat and feathered, sweeping back and up off the side of the helmet.
Theme **Knightly** — forged, not grown, which is the other half of the contrast with `horns`.

- **A plane, not a cone.** Three or four tapering feather plates in a fan, each its own bone off a
  small mount, each rotated a little further back and up than the one below. Thin in x — a wing is
  seen edge-on from the front and broad from the side. Model every plate upright in the unrotated
  pose and compute where the chain lands (pivot plus length times cos and sin of the cumulative
  angle) before placing; the reply confirms it to a hundredth.
- **The gauge.** Stay inside about `x 7.0` — narrower than `horns`' 8.96, because the whole point is
  that this one is not a spread — and buy the silhouette in length instead: back to about `z 6` and
  up to about `y -14`. Keep the mount clear of the helmet shell planes rather than on them, and clear
  of `laurel:brow`'s leaves; the open reply gives you both.
- **The mount is small.** The shipped `boss` is the thing that lies on the head and laps the laurel.
  Whatever holds the plates on should be the least of the part, not a lump at the temple.

**Sheets.** Master only, greyscale, its value a position on the trim material's ramp: the plates
lighter towards their leading edge and their tips, a darker line where each overlaps the one below
so the fan reads as separate feathers at three metres, the mount darkest. No static layer, no masks.

**Budget.** Two or three `armorpieces_paint` calls and no more than six pictures. Take the first
picture where it can still change what you draw and none after the last edit; every reply that
carries one prices it for you.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py helm_wings`
and `python tools/check_authoring.py` clean from the repository root; the lessons section below
filled in. No `modpage.yml` entry, no recipe, no page rebuild.

## Lessons from the session

**What was built.** `base` (one small `mount` cube, x -6.40..-5.30, y 31.5..32.5, z 0.0..2.4 in
Blockbench) carries four sibling bones `plate_a..d`, rotated 22 / 34 / 46 / 60 degrees about X, each
holding a `quill_` root plate and a narrower `vane_` tip plate. Envelope bone-local
`x 5.30..6.40  y -14.37..-7.14  z -0.74..6.58`: 2.5 narrower than `horns`, 4.6 deeper, same height.
`all clear by more than half a unit` — no laurel lap, no shell-plane note, nothing forced.

**A positive X rotation on a bone leans an upward cube toward +Z (backward).** Worth one probe
before committing a chain: place the first bone, read `past helmet` in the reply, then place the
rest. Predicted `y 38.30 z 3.05` and the reply gave `y+5.37 z+1.58` off the 33/5 helmet planes —
the same numbers. The whole nine-cube fan was then placed blind from one Python table and needed no
nudging.

**A fan is set by the chord, not the angle.** The first attempt (22/42/62/82, chord 1.9 tapering to
1.1) rendered as four spread fingers: the transverse gap between neighbours is `L * dtheta`, which
at L=6 and 20 degrees is 2.09 units — wider than the plates. Halving the spread to 12-14 degrees and
widening the chord to 2.25/1.55 closed it into one feathered plane. Compute `L * dtheta` against the
chord before placing, and remember that stepping each pivot back in z adds its own gap on top.

**Box UV: u runs around the cube, so the west face's leftmost column is its -Z edge.** The strip
order the check prints (`east(d) north(w) west(d) south(w)`) is a walk around the box, so u
increases toward -z on the east face and toward +z on the west. That is what let the leading-edge
highlight and the dark trailing seam be placed per-column with `pixels` without a test render.
Rows run tip-to-root, so the `[top, bottom]` face pair and the per-pixel ramp agree.

**`eraser_tool` and `draw_shape_tool` did nothing to the sheet** (`set_opacity 0` over the whole
64x32, twice: the stray count did not move). Only `armorpieces_paint` writes. To clear paint outside
the faces, pass `pixels` with `value: null`; to find them, reconstruct the *old* face rectangles from
the earlier replies and subtract the current ones — the set difference is a superset of the strays
and nulling the extras is harmless. That fixed 54 old-master pixels and later 42 of my own.

**A rework leaves its own strays.** Every `remove_element`, `modify_cube` and re-place re-lays the
sheet, and paint from the previous layout survives wherever no new face landed on it. Expect one
null pass after the geometry settles, and keep every `sheet layout` block from the replies — they are
the only record of where the old rectangles were.

**Another session stole the active tab between two of my calls.** `armorpieces_open` returned
helm_wings, and the very next `armorpieces_check` reported `bedroll`. Every reply header names the
piece: read it each time, and re-open rather than trusting that the tab held.

**Left for the orchestrator:** `tools/paint_helm_wings_master.py` is now orphaned — its `CUBES`
table is the dead `boss/horn1/horn2/horn3` chain, and the `check_geometry()` guard it gained will
fail against the new nine-cube model. Untouched here, as the brief directed.
