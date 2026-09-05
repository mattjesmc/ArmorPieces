# Brief: Claws (REWORK)

This is a **rework of a shipped part**, not a new one. `armorpieces:claws` already exists — it was
authored by hand in batch 2 of the content line (2026-09-03), before the Blockbench bridge, and it
does not read. Everything about the datapack half is already right and must survive; the geometry
and both sheets are to be rebuilt.

Open it with `armorpieces_open armorpieces:claws`. Do **not** create a new piece.

## What is wrong with the shipped model

Judged in the viewport on the rig, front and three-quarter, at the size the game draws it:

- **The three blades read as flat paddles, not points.** Each is a single cube 1 wide × 2 tall,
  constant section from root to tip — `blade_a` 1×2×4, `blade_b` 1×2×5, `blade_c` 1×2×3. A claw is
  a cone; these are fins. Nothing tapers, so at four texels across they are slabs.
- **They fan sideways instead of forward.** The Y rotations are +20 / +2 / −18 about the vertical,
  which throws the outer two across the width of the hand. From the front the part reads as two
  dark wedges stuck out the side of the wrist, not as points in front of a fist.
- **They are painted too dark.** The outboard flanks run nearly black; through a trim ramp they
  come out as black wedges with no form in them, which is what makes them read as holes rather
  than as claws.
- **The two "fur locks" behind the wrist are boxes.** `lock_a` 2×4×2 and `lock_b` 2×5×2 hanging off
  the back of the band read as two rectangular flaps, not fur, and they are the mass that laps
  `wing_cases:pauldrons` in four places on the clash list. They are the ugliest thing in the
  silhouette and the least load-bearing.
- **The binding is a big grey box.** `cuff` is 4×2×7 — it runs the whole length of the forearm and
  contributes nothing but bulk, while the part's actual subject sits at the far end of it.

## What must not change

- Part id `armorpieces:claws`, display name **"Claws"**, socket **`vambraces`** only.
- Fitting: `armorpieces:guard`, one mask, and it covers **the claws themselves and nothing else** —
  the binding stays on the base trim ramp. That contrast is the point of the fitting here: the
  player can see which half of the part the guard material is going to take.
- **No recipe.** `claws` is loot-only (it is in
  `data/armorpieces/tags/armorpieces/armor_decoration/beast.json` and has no `template_claws.json`).
  Do not set a recipe, do not pick a centre item, do not touch the recipe panel.
- No effects, no loot field on the part file, no static layer. The part JSON as shipped is already
  correct; leave `armorpieces_set_part` alone unless a mask sheet needs recreating.
- Theme is **Beast** — grown, not forged. It is the set's hand piece, beside Antlers, Beast Head,
  Ears, Fang Necklace, Pelt, Shin Spikes and Spine Ridge.
- The language line and the mod page entry already exist; the page still needs a rebuild at the end
  because the texture changes.

## The frame

`vambraces` is a **mirrored** socket on the arm bone: model the **left** arm only, the game mirrors
it. In Blockbench the player's left limbs are on the **negative x** side.

    left arm box (naked)          x −8 .. −4    y 12 .. 24    z −2 .. 2
    chestplate sleeve (inflate 1) x −9 .. −3    y 11 .. 25    z −3 .. 3
    fingertips                    y = 12        (the bottom of the arm box)
    arm bone pivot                (−5, 22, 0);  the anchor is bone (1, 6, 0)

Frame conversion, so the check's bone-local numbers (+Y down, x mirrored) can be read back:
`bb_x = −bone_x − 5`, `bb_y = 22 − bone_y`, `bb_z = bone_z`.

The shipped part's envelope for reference: bone x −0.71..6.48, y 3.80..12.17, z −8.37..4.50 —
i.e. Blockbench x −11.48..−4.29, y 9.83..18.20, z −8.37..4.50. Reach 9.74; past the chestplate
x +2.48, y +1.17, z +5.37. That envelope is roughly the right budget; the shape inside it is not.

`armorpieces_open`'s reply lists the envelopes of every other part on this bone. The six other
`vambraces` parts are never worn with this one and are never compared — they are only there to tell
you what heights this socket has already used. The seven `pauldrons` parts **are** worn with it, and
`wing_cases` is the one the current part collides with: it reaches down to Blockbench y 14.07 on the
outboard side (bone y −3.85..7.93, x 2.05..6.02 → bb x −11.02..−7.05). Keep clear of it this time.

## What to build

Three **tapering, curling talons** off the back of the hand, on a binding that gets out of their way.

**The talons.** Each one is a chain of bones — the idiom the `talons` (spurs) and `horsetail`
sessions proved, and it is the whole reason this rework is worth doing: model every segment straight
along its local axis in the unrotated pose, put each child's pivot at the parent's pivot plus the
parent's length minus a quarter unit of overlap, and rotate each bone a little further than the last
about X so the chain curls. Compute where the chain lands before placing anything
(pivot + L × (0, −sin θ, cos θ) for a segment modelled along +Z with cumulative angle θ, sign
flipped for one modelled along −Z); the check confirms every bone-local position to a hundredth, so
nothing should need nudging afterwards.

- **Three segments each**, square in section and shrinking: about 1.5 → 1.0 → 0.625 across, lengths
  falling too. That is the taper the current part has none of, and it is what separates a claw from
  a stick at this scale.
- They leave from the **front edge of the knuckle plate** and curl **forward and down**, past the
  fingertips. Aim the longest tip to hang roughly 2 units below y 12 and about 5 past the sleeve's
  front wall at z −3 — near where the shipped `blade_b` ends, so the part keeps its presence.
- **Keep the sideways splay small.** ±10° about Y at the outer two and nothing at the middle is
  plenty to make them three points instead of one wedge; the shipped ±20 is what threw them across
  the hand. The differences that should be large are **length, curl and drop**: three tips at three
  heights, three depths and three curls, no two alike — the Beast set's standing rule (the pelt's
  hem with no two equal steps, the antlers' five tines at five heights).
- Sibling segments must cross a neighbour's face by about a tenth, never lie on it, and no face may
  land on a shell plane (x −9 / −3, y 11 / 25, z −3 / 3).

**The binding.** Cut it down. A short band around the wrist end of the forearm plus a knuckle plate
over the back of the hand is all that is needed — the plate is the thing the talons grow out of, and
the band exists to say the plate is strapped on. Do not run a 7-long box up the whole forearm, and
do not put mass outboard where `wing_cases` hangs. Standing a face 0.5–0.9 past the sleeve wall is
what makes hardware read as strapped on rather than painted on; keep that, and keep the inboard
halves inside the sleeve where they cost nothing.

**The locks.** Delete `lock_a` and `lock_b`. If the part wants a hide note at the wrist, it must be
something that reads as fur at four texels — two or three short, thin, tapering tufts lying close
along the band, on their own bones, hems at different heights — and it must stay clear of
`wing_cases`. If it cannot be made to read, leave it out: three good talons with nothing behind them
beat three talons plus two boxes. This is your call; say which way you went and why.

## Sheets

Both are repainted from scratch, and there are only two: the master `part` and the guard mask
`part_guard`. No static layer.

- **Master.** Binding: mid-grey hide/hardware, a lighter top row where the light falls, the Beast
  set's coarser grain (the plate parts use ±3 per texel, the Beast parts ±10) so it reads as grown
  rather than milled. Talons: **dark at the root running light to the tip**, one clear step per
  segment, with a `[top, bottom]` pair inside each segment for the gradient and a bright texel at
  the very point. Do **not** repeat the shipped part's near-black flanks — keep the range on any one
  surface tight and let the per-segment step carry the story. A blade's cutting edge being the
  brightest value on the part is the one idea from the old master worth keeping.
- **Guard mask.** The talons' faces only, nothing on the binding. **Shaded, not flat** — mirror the
  master's values on those faces, because the mask is the talon's position on the guard material's
  ramp and a flat mask flattens the form the moment a guard is fitted. Every shipped mask does this.
- One `armorpieces_paint` call per sheet. The shape and brush tools are for what is not a whole face.
- The old geometry's cubes are gone, so every face is new: expect the check to walk you through the
  unpainted ones. Nothing on this part is cut on purpose — there should be no holes.

## Working notes

- **Removing the old shape.** `remove_element` the five obsolete bones and their cubes by name
  (`blade_a`, `blade_b`, `blade_c`, `lock_a`, `lock_b`, and the two `bracer` cubes if you resize
  rather than reuse them). Watch for ghost cubes left at outliner root — the check reports "cubes
  outside the part group"; remove them by name if it does.
- Never pass a UUID as `add_group`'s `parent` (it crashes the whole Blockbench project, every open
  tab with it) — pass the parent bone's **name**. Never name a bone `root`.
- **Picture budget: about eight screenshots**, and spend them where they decide something. The part
  has no visible surface until the master has paint, so paint before the first look. At minimum,
  look at it head-on and from a three-quarter front once the talons are shaped and again once both
  sheets are painted — this rework exists because the arithmetic on the shipped part was clean and
  the part still read badly.
- `tools/paint_claws_master.py` is the old hand painter and will be **deleted by the orchestrator**
  after this session; do not edit it, do not run it, and do not let it decide anything.

## Done means

`armorpieces_save` accepted **without** `force`; `python tools/check_part.py claws` and
`python tools/check_authoring.py` clean from the repository root; `python -m modpage build --offline`
run; and the Lessons section below filled in. In the final report: what the talons' segment lengths
and cumulative angles came out as, what you did about the locks, how many paint calls, any `!` you
accepted and why, and whether it reads.

## Lessons from the session

Reworked 2026-09-05 in 35 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_open`,
1 `list_outline`, 1 `armorpieces_part`, 2 `armorpieces_check`, 7 `remove_element`,
4 `eraser_tool` (useless, see below), 9 `add_group`, 10 `place_cube`, 2 `armorpieces_paint`,
4 `set_camera_angle`, 1 `armorpieces_save`. No `risky_eval`, no `modify_cube`, no
`armorpieces_set_part` (the datapack half was never touched: the part file after the save is
byte-for-byte the anchors + fittings `armorpieces_part` printed, and only the geometry, the two
sheets and their `tools/decoration_masters` copies carry the save's timestamp; this checkout has
the whole part untracked, so git cannot tell you that - the timestamps can), and the save went
through first time without `force`. A stale `docs/assets/recipes/armorpieces__template_claws.png`
from 2026-09-03 sits in the tree unreferenced - the recipe cull's leftover, not this session's.

**What I built.** The old `bracer` bone (pivot at the anchor, Blockbench (-6, 16, 0)) was kept
and its seven children removed by name; nothing ghosted. In it: `band` 7x1.5x7 at
x -9.5..-2.5, y 12.3..13.8, z +-3.5 (0.5 proud of the sleeve on every side, 0.27 under
`wing_cases`), and `plate` 5x2.5x1.05 at x -8.5..-3.5, y 13.55..16.05, z -3.95..-2.9
(0.25 into the band's top, 0.15 clear of `wing_cases`' z -2.75 hull, 0.1 into the sleeve).
Three talon chains hang off the plate, pivots buried 0.45 inside its front face at z -3.5,
each segment modelled straight along **-Z** from its own pivot, square in section
1.5 / 1.0 / 0.625, child pivots at parent pivot + (L - 0.25) along -Z:

- `mid_a/b/c` (x -6.0, pivot y 14.8): lengths 3.25 / 2.25 / 1.75, X rotations -20 / -30 / -35
  (cumulative 20 / 50 / 85), no yaw. Tip axis lands at Blockbench (-6.0, 10.5, -7.75).
- `out_a/b/c` (x -7.65, pivot y 15.1): 2.5 / 2.0 / 1.5, -30 / -35 / -35 (30 / 65 / 100),
  yaw +10 on the root only. Tip (-8.07, 10.91, -5.89) - it hooks back in at 100 degrees.
- `in_a/b/c` (x -4.35, pivot y 14.5): 2.25 / 1.75 / 1.25, -15 / -25 / -25 (15 / 40 / 65),
  yaw -10. Tip (-3.72, 11.89, -7.06).

Three heights (10.5 / 10.9 / 11.9), three depths (-7.75 / -5.9 / -7.1), three curls
(85 / 100 / 65). Envelope bone x -2.50..4.50, y 5.95..11.53, z -8.15..3.50; reach 9.76,
past chestplate x +0.50 y +0.53 z +5.15 - the old part's presence (9.74) at a third of its width.

**Sign and order of a -Z chain, confirmed to a hundredth.** A segment modelled along -Z curls
**down** with a **negative** X rotation: end = pivot + L x (0, -sin|θ|, -cos|θ|). Yaw on the
root bone is applied after its pitch, about the vertical - i.e. Blockbench pitches first, then
swings the tilted talon - so the children keep curling in the yawed vertical plane and the tip
drifts sideways by (horizontal run) x sin(yaw): positive Y yaw sends a -Z segment toward -x
(outboard on the left arm). All nine bone positions matched the sums exactly (`out_b` at
bone (2.99, 8.03, -5.42) against a predicted bb (-7.99, 13.975, -5.42)).

**The locks are gone and nothing replaced them.** From the outboard side view the silhouette is
a strap, a bump, and a hook; at the game's scale a hide tuft would have been a 1-texel stick
in exactly the corner `wing_cases` hangs over. Three talons with nothing behind them, as the
brief allowed.

**Reworking a shipped part leaves the old paint on the sheets, and the eraser cannot clear it.**
After the removes the check reported 201 opaque px outside every face; `eraser_tool` with a
100-wide or 16-wide square brush "erased N points" but the count never moved (it seems to touch
a texel or two, not a brush's worth). What worked: read the on-disk master and mask with Pillow,
subtract the new face rectangles from the check's layout, and pass the leftovers as
`{x, y, value: null}` `pixels` in the same `armorpieces_paint` call that paints the faces - 163
nulls on the master, 44 on the mask, and the count matched the check's exactly, so the on-disk
PNG *is* the live sheet until the first save. Do this before the first look, not after: the
mask's strays only become a `!` ("outside the master's silhouette") once the master is painted.

**Paint: two calls, 66 master faces + 28 grain texels, 54 mask faces.** Master: `*.*` 150,
band up 185 / sides `[165,135]` / down 100, plate up 200 / north `[178,142]` / sides
`[168,140]`; talons 95 -> 140 -> 195 per segment with `[+10, -10]` flank pairs and `up`/`down`
+-15, the 1x1 `north` end cap of each `_c` segment at 255 as the bright point. Beast grain is
just `pixels` at +-10..28 on the binding's faces. The guard mask is the talon faces at the same
values, nothing on the binding. Zero unpainted faces after the two calls.

**`!` lines accepted: none.** Two `-` notes: `bracer clears wing_cases' case_lower by 0.27 in y`
(the band top at 13.8 under its 14.07) and the pair spanning 19.00 across the figure (the
band's 0.5 stand-off each side). The old part's four OVERLAP lines are gone.

**Reads?** Yes, in the four screenshots: head-on the three points sit at three heights and
fan slightly, the dark roots step to light tips; from outboard it is a strap, a plate and a
hooked claw. The band shows as a strap from the side but is nearly invisible head-on, which is
fine - the plate and talons are the subject. The one thing a next pass might do is a 1-texel
step between the `_a` and `_b` flank values that is larger than 35 - at 1.5 -> 1.0 the section
change is only visible from the front.

**For the next rework.** Keep the old anchor bone and remove its children by name; the pivot
is already right and nothing ghosts. Count on ~35 calls, not 20: the seven removes and the
stray-paint clearance are the rework tax. The screenshots are 288x384 and the part is ~100 px
of that - aim the camera at the part's own centre from 10-15 units away, not at the figure.
