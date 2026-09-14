# Brief: Heel Wings (REWORK)

This is a **rework of a shipped part**, not a new one. `armorpieces_court:heel_wings` is one of the
original pieces, hand-authored long before the bridge, and it now lives in the Court pack. The
datapack half is right and must survive; the geometry and the sheets are to be rebuilt.

Open it with `armorpieces_open armorpieces_court:heel_wings`. Do **not** create a new piece, do
not delete the part JSON, and do not touch any other tab.

**The example to follow is `armorpieces_knightly:helm_wings`** - the same idea already done right
on the head: a fan of thin feather plates off a small mount. Read its geometry file
(`packs/knightly/resourcepack/assets/armorpieces_knightly/armorpieces/decoration/helm_wings.json`,
bone-local +Y down) and the **Lessons** at the end of `docs/plans/briefs/helm_wings.md` before you
place anything. Do not open helm_wings in Blockbench: another person is working in the other window
and it is theirs.

## What is wrong with the shipped model

- **It is three slabs.** `clasp`, `vane_upper`, `vane_lower` - a lump at the heel and two flat
  boards behind it. Nothing reads as a wing.
- **It climbs the leg.** The envelope runs to bone-local `y 3.72`, which is Blockbench `y 8.28` -
  two thirds of the way up the shin. That is why the check lists forty-odd `OVERLAP` lines against
  tassets and knees pieces that are worn together with it. A heel wing lives at the **ankle**.
- **`clasp` sits in the boot.** `clasp and swim_fins:greaves's web2 share the plane z = 0 (inside
  the shell, so occluded)` - part of it is inside the boots shell and never seen.
- **No surface for the player.** Master only, no fitting. `helm_wings` now carries an `inlay`
  mask on its feathers; this piece should match it.

## What must not change

- Part id `armorpieces_court:heel_wings`, display name **"Heel Wings"**, socket **`spurs`** only.
- **The effect stays exactly as it is** - `armorpieces:heel_wings_jump`, jump strength
  `add_multiplied_base` 0.1 / 0.15 on netherite. It is one of the mod's worked examples.
- **The loot row stays exactly as it is** - `end_city_treasure` weight 2 chance 0.1.
- **No recipe.** Loot-only. Do not set one, do not pick a centre item.
- `former_ids` and `uid` stay as they are. `armorpieces_set_part` keeps every field you leave out,
  so the ONE call you make to it carries `fittings` and nothing else:

      armorpieces_set_part { fittings: ["armorpieces:inlay"] }

  Make that call BEFORE painting - it is what creates the `part_inlay` sheet. Check the reply:
  `sheets_created` must name the inlay sheet, and the effect and loot must still be in the part.
- `spurs` is a MIRRORED socket. Model ONE side - the **left leg, negative x** - and the game mirrors.
- Do not touch `tools/paint_heel_wings_master.py`. A bridge rework orphans a part's hand painter
  and removing it is the orchestrator's job, not yours.

## The rig, in Blockbench coordinates

    left leg box            x -3.9 .. 0.1    y 0 .. 12       z -2 .. 2
    leggings shell (+0.4)   x -4.3 .. 0.5    y -0.4 .. 12.4  z -2.4 .. 2.4
    boots shell (+0.9)      x -4.8 .. 1.0    y -0.9 .. 12.9  z -2.9 .. 2.9
    the spurs anchor        (-1.9, 2, 2)     - the centre of the heel

Front is **negative z**; the heel is at **+z**. Outboard (away from the other leg) is **negative
x**. This is a boots socket, so the shell you must stay off is the **boots** one: its back plane is
`z = 2.9` and its outboard plane is `x = -4.8`. Sit a tenth or more off both, never on them.

The check prints YOUR envelope bone-local (+Y down, x mirrored): `bone_x = -(bb_x + 1.9)`,
`bone_y = 12 - bb_y`, `bone_z = bb_z`. Other parts' envelopes come in both frames.

## What it should be

The winged sandal: a **small wing at the outer ankle, sweeping back and up off the heel**. Court
theme - gilt and feathered, a herald's ornament, the thing that makes the jump effect make sense.

- **Mount.** One small cube behind the heel, at the outer-back corner of the boot - about
  `x -5.1..-3.9, y 1.0..2.6, z 3.2..4.0`. Clear of both shell planes (`x -4.8`, `z 2.9`) by 0.3.
  Bone `base` at the anchor; never name a bone `root`.
- **Four feather plates**, each its own child bone off `base`, like `helm_wings`' `plate_a..d`.
  Each plate is two cubes - a broader `quill` root and a narrower `vane` tip - **0.4 thick in x**,
  sitting just outboard of the boot at about `x -5.35..-4.95` (0.15 clear of `x -4.8`). Model each
  plate upright (+Y) in the unrotated pose, then rotate the BONE about X so it leans back toward +z.
  A heel wing lies flatter than a helm wing: something like **35 / 50 / 65 / 80 degrees** back
  from vertical, the lowest plate the flattest, each pivot stepped a little further back in z
  (0.3-0.5) so the roots fan.
- **Lengths.** Roughly 4.5 / 4.2 / 3.9 / 3.5 units root to tip. Compute where each tip lands before
  placing - `dy = L cos(theta)`, `dz = L sin(theta)` from the pivot - and confirm against the
  reply. The whole fan should end up inside about `y 0.5..6.0` and `z 3.0..7.5`.
- **The fan must close into one plane.** The gap between neighbouring plates is `L * dtheta`
  (radians); with 15-degree steps at L 4 that is ~1.05 units, so the quills need a chord (their z
  depth in the unrotated pose) of at least 1.6-2.0 tapering to ~1.2 at the vane, or it renders as
  four spread fingers. This is helm_wings' hardest lesson; read it.

**Budget - and these are the lines that matter.**

- Stay inside **`x -5.4 .. -3.9`, `y 0.5 .. 6.0`, `z 3.0 .. 7.5`** (Blockbench).
- **`y <= 6.0`** keeps you under every tassets piece (the lowest, `thigh_sheath`, stops at `z 2.8`
  anyway; the ones that reach `z 3.7` start at `y 6.1`). **`z >= 3.0`** keeps you behind every
  greaves and knees piece (`schynbalds` reaches `z 1.45`, `swim_fins` spans `x -7.1..-4.1` but only
  `z -2..2`). Meeting those two lines is what turns forty overlap notes into none.
- Same-socket neighbours are never worn with you and never compared; `rabbit_feet` and
  `dolphin_flukes` reach `z 6.6-6.7`, so `z 7.5` is generous, not a target.
- Reach from the anchor should come out around 7; the shipped part is 8.18. Pair span will be
  about 10.8 - well inside 18.

**Sheets.** Two: the greyscale **master** and the **`inlay` mask**. No static layer - do not create
one (an empty static sheet is a check finding). Master: plates lighter toward the leading edge and
the tips, a darker line where each overlaps the one below so the fan reads as separate feathers at
three metres, the mount darkest. Inlay: cover the feather plates (quill and vane) shaded like the
master - NOT flat - and leave the mount out of it, exactly as helm_wings does; the dye then colours
the feathers and the mount keeps the trim metal.

**A rework leaves strays.** The old master's paint survives wherever no new face lands. After the
geometry settles, null every texel outside the current face rectangles (`armorpieces_paint` with
`pixels` and `value: null`); keep every `sheet layout` block the replies give you, they are the
record of where the old rectangles were. Only `armorpieces_paint` writes these sheets.

**Budget.** Two or three `armorpieces_paint` calls per sheet at most, and no more than six pictures.
Take the first picture where it can still change what you draw and none after the last edit.

**Done means.** `armorpieces_save` accepted without `force`; from the repository root
`python tools/check_part.py heel_wings`, `python tools/check_authoring.py packs/court/datapack
packs/court/resourcepack` and `python tools/check_surfaces.py` clean for this piece; the lessons
section below filled in; `armorpieces_close` as your last call. No `modpage.yml` entry, no recipe,
no page rebuild.

## Lessons from the session

**What was built.** `base` (one `mount` cube, Blockbench x -5.10..-4.05, y 1.0..2.6, z 3.2..4.3)
carries four child bones `plate_a..d` at pivots (-5.15, 1.8, z 3.6 / 3.8 / 4.0 / 4.2), rotated
**36 / 49 / 62 / 75** degrees about X, each holding a `quill_` (0.4 x 2.0 chord) and a `vane_`
(0.4 x 1.4 chord), lengths root-to-tip 4.5 / 4.2 / 3.7 / 3.3. Envelope bone-local
`x 2.00..3.45  y 6.27..11.24  z 3.08..7.41` (Blockbench `x -5.35..-3.9  y 0.76..5.73  z 3.08..7.41`),
reach 6.72, pair span 10.70. `all clear by more than half a unit`: the forty overlap notes are gone,
nothing forced, no `!` at any point. Master + `inlay` mask on the eight plate cubes, mount left out.
No recipe, effect and loot untouched (verified in the saved data file).

**Flatter plates need their chord in FRONT of the pivot, steeper ones behind it.** With every plate
carrying the same 2.0 chord centred on its pivot, the 75-degree plate's trailing root corner lands
at `y = py - 0.2*cos + 1.0*sin(75)` = about `y 0.2`, under the floor, and the 36-degree plate's
leading root corner lands in front of the boots plane. Shifting the chord per plate (front/back
offsets 0.5/1.5, 0.8/1.2, 1.1/0.9, 1.4/0.6 from a to d) keeps every corner inside `y 0.76..5.73`
and `z >= 3.08` without touching the angles. The closure test is `b_i + f_(i+1) >= L*dtheta +
pivot_step*cos(theta_i)`; it came out 1.70 covered against 0.96-1.18 needed, so the fan closed on
the first placement and no picture changed anything.

**Angles: 13-degree steps, not 15.** The brief's 35/50/65/80 puts the last tip at z 7.9 with the
pivots stepped 0.3; 36/49/62/75 with 0.2 steps and plate_d at L 3.3 lands the fan at z 7.41.

**The rework's strays were nulled in one call.** The old sheet was x 0..39, y 0..9; a 400-entry
`pixels: null` list on the master before the face paint (the paint call applies pixels AFTER faces,
so nulling must be its own call) left zero stray pixels. New faces occupy x 0..55, y 0..4.

**`check_part.py <name>` reads `tools/decoration_masters/<name>.png`, and the plugin's save writes
only the pack's texture folder.** The by-name check therefore reported the OLD master (44 unpainted
faces, 123 strays) right after a clean save. `check_part.py <geometry.json> --name heel_wings
--master <pack png> --mask inlay=<pack png>` was clean; the saved sheets were then copied into
`tools/decoration_masters/` (heel_wings.png, heel_wings_inlay.png - the same bytes the plugin wrote)
and the by-name check went clean too. Nothing in the masters dir was hand-painted.

**A concurrent session in the same window steals the status publish.** `pinions` was being painted
in another tab throughout; `armorpieces_check` and the loop's per-reply check answered with
`pinions` or `FileNotFoundError ... part.bbmodel` on most calls. `armorpieces_open` on my own piece
carried the correct compact check every time, `get_project_info` confirmed `bound:true`, and every
edit landed. The full report came from `tools/check_part.py` on the saved files instead.

**`tools/paint_heel_wings_master.py` is now orphaned** (its cubes are the dead
`clasp/vane_upper/vane_lower`). Untouched, as the brief directed.

**Addendum (orchestrator, after review).** The fan as built z-fought on every plate: all four
pivots at one x and every plate cube `x -0.2..0.2`, so the eight x faces shared two planes and the
closed fan lapped everywhere. The brief caused it (one x for all plates, no step) and the check is
blind to it (LESSONS #29). Fixed by hand in Blockbench: quills and vanes staggered in x per plate,
plate_d reduced to one cube; the 22 strays that left behind were nulled on both sheets by script.
`check_part` clean afterwards, 8 cubes, reach 6.99.
