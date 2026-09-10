# Brief: Rowel Spurs

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the sixth
batch of four (read talons.md first - same socket, the leg frame, the boots' back plane at
z 2.9 - and bedroll.md for the two-cubes-at-45-degrees round profile). From the `spurs` row of
`docs/plans/part-variety.md`:

> **Rowel Spurs** - A spiked star wheel on a yoke - the cavalry spur to the shipped prick spur.
> Theme: Knightly. Fitting: `guard`.

**Part.** `armorpieces:rowel_spurs`, socket `spurs` only, in the mod's own pack. Display name
"Rowel Spurs". Fittings: `armorpieces:guard`, one mask, covering the rowel and its hub; the yoke
and neck stay the material. No effects, no loot, no static layer.

**Shape.** `spurs` is a mirrored socket on the leg bone: model ONE leg, the LEFT, at NEGATIVE x.
The leg box is x -3.9..0.1, y 0..12, z -2..2 (pivot -1.9, 12, 0); the boots shell is that box
inflated 0.9, so its back plane is z 2.9 and its sides are x -4.8 and 1.0; the anchor is at
Blockbench (-1.9, 2, 2). Read the envelopes in the `armorpieces_new` reply: the other spurs
parts (spurs, heel_wings, streamers, talons) are never compared, and the back of the ankle above
z 3 is free of every other socket (talons found it so). Build: a `yoke` bone at the anchor
carrying two side arms a quarter thick and half a unit tall running along the boot's sides a
tenth off the shell (x -5.15..-4.9 and 1.1..1.35, y 1.75..2.25, z 0.5..3.25) and a back bar
joining them behind the heel (x -5.15..1.35, y 1.75..2.25, z 3.0..3.25 - a tenth off the shell's
z 2.9); a `neck` cube from the bar's middle straight back, x -2.15..-1.65, y 1.75..2.25,
z 3.25..4.6, in the same bone; and the rowel, a `rowel` bone pivoted at the wheel's axle
(-1.9, 2.0, 5.1): a hub cube 0.6 square (x -2.2..-1.6, y 1.7..2.3, z 4.8..5.4) and two crossed
plates a quarter thick in x, one upright (x -2.02..-1.78, y 0.9..3.1, z 4.95..5.25) and one
flat (x -2.02..-1.78, y 1.85..2.15, z 4.0..6.2), then a child bone `rowel_turned` at the same
pivot rotated 45 degrees about X holding the same two plates a hair shorter (2.1 and 2.1 long,
so their ends are not coplanar with the first pair's) - eight points. The lowest point sits at
y 0.9, above the ground; the neck's end at z 4.6 laps the hub by 0.2. Nothing wider than
x -5.15..1.35 and nothing further back than z 6.3.

**Sheets.** Master: yoke and neck mid grey `[top, bottom]` with a lighter top face; hub bright;
rowel plates bright metal lighter toward each point, their end faces brightest (each is one
texel). Guard mask: the hub and the four rowel plates only, shaded like the master.

**Recipe.** Centre item `minecraft:diamond_horse_armor` (a flat item, unused by any template),
paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
rowel_spurs` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-03 in 19 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`list_outline`, 3 `add_group`, 3 `place_cube`, 2 `remove_element` (starter cube, then its bone),
1 `armorpieces_check`, 1 `armorpieces_part`, 1 `armorpieces_set_part`, **2 `armorpieces_paint`**,
2 `set_camera_angle`, 1 `armorpieces_save`. No `risky_eval`, no `modify_cube`, no `undo`: the
brief's rig numbers were enough, the first check after the last cube already read
`ok: nothing needs a decision` on geometry, and the save went through without `force`.

**What I built.** Three bones: `yoke` at the anchor (-1.9, 2, 2) with `arm_out`
x -5.1..-4.9, `arm_in` x 1.1..1.3 (both y 1.8..2.2, z 0.5..3.2), `bar` x -5.15..1.35,
y 1.75..2.25, z 3.0..3.25 and `neck` x -2.15..-1.65, y 1.8..2.2, z 3.05..4.6; `rowel` at the
axle (-1.9, 2, 5.1) with `hub` 0.6 square, `spoke_v` (y 0.9..3.1) and `spoke_h` (z 4.0..6.2);
and `rowel_turned`, its child at the same pivot rotated 45 about X, with `spoke_v2` (2.1 tall)
and `spoke_h2` (2.1 long). Envelope x -5.15..1.35, y 0.9..3.1, z 0.5..6.2; reach 4.21, past
boots z+3.30; the bar sits 0.1 off the shell's z 2.9 and both arms 0.1 off its sides.

**Four plates on one axle share their x planes - stagger them, don't just shorten them.**
The bedroll's "give the turned cube a slightly shorter length" is *not* enough here, because a
rotation about X leaves a cube's x extent untouched: all four plates keep their real world x
planes whatever the bone does. Four plates all "a quarter thick in x" at x -2.02..-1.78 would
have been three pairs of coincident, overlapping faces buried in the hub. I gave each plate its
own thickness slot, 0.24 wide and 0.03 apart: spoke_v -2.06..-1.82, spoke_h -2.00..-1.76,
spoke_v2 -2.03..-1.79, spoke_h2 -1.97..-1.73. All four still sit inside the hub's x -2.2..-1.6,
the offsets are far under one texel, and the check found nothing. Two more of the same trap
were designed out before placing: the neck as briefed started exactly on the bar's back plane
(z 3.25) and was flush with the bar in y, so it moved to z 3.05..4.6 (starting *inside* the bar)
and y 1.8..2.2 (inside the bar's 1.75..2.25); and the arms, briefed flush with the bar in both
y and at x -5.15, were inset to y 1.8..2.2 and x -5.1 / 1.3 so the bar overhangs them by 0.05
on every shared plane. Rule: where two cubes of one part meet, make one strictly inside the
other on both axes it does not travel along.

**`!` lines accepted: none.** The finished check reports zero problems. Three `-` notes stand,
all against `swim_fins:greaves`: `OVERLAP yoke into ray3 by 0.20 x 0.40 x 0.50`, `OVERLAP yoke
into web2 by 0.20 x 0.40 x 1.25`, and `near: clears ray2 by 0.25 in z`. These are real, not hull
artefacts - `arm_out` is 0.2 x 0.4 in section and the overlap boxes are its full section, so the
outboard arm passes through the fin's rays where they cross z 0.5..2.0. Accepted deliberately:
swim_fins occupies the *whole* outboard flank (x -7.14..-4.11, y 0.78..3.44, z -2..2), so any
spur yoke arm lying on the boot's side at ankle height meets it; clearing it would mean starting
the arms at z 2.1, a 1.1-unit stub instead of a yoke. Notes, not problems, and the shipped
`spurs` part (x -5.75..-1.50 from z 1.50) lives in the same volume.

**Paint: two calls, and they covered every face.** Master (1 call): `"*.*": 140`, then per-cube
`[top, bottom]` pairs on the yoke (arms/bar/neck 160->118 with `up` 195..205 and `down` 88..95),
the hub at 210 with a 240 top, and the four plates at 198..205 with each end-cap face 245..252 -
plus 48 explicit texels. 54 faces, nothing left unpainted. Guard mask (1 call): the hub and the
four plates only, the same values and the same 48 texels, so the fitted metal keeps the wheel's
shading; the yoke, bar and neck stay trim material as briefed.

What the painter did **not** cover, and the workaround: a `[top, bottom]` pair is a linear ramp,
so it cannot make a plate that is **bright at both ends and dark in the middle** - which is what
"lighter toward each point" means on a spoke that runs through the hub. Each plate's four long
faces are 3 texels, so I enumerated them: 235 / 175 / 235 down every strip, ~10 darker per face
going round the plate. **The pattern being symmetric is the point**: talons had to give up on
within-segment gradients because nothing the bridge prints says which end of an `up`/`down` strip
is which, but a bright-dark-bright triple reads identically either way, so the ambiguity never
arises. The eight points themselves are literally eight 1x1 faces (`spoke_*.up/down` on the
uprights, `.north/.south` on the flats) - one texel each, painted brightest.

**Recipe.** `minecraft:diamond_horse_armor` in a paper ring: `iron_`, `golden_` and `leather_
horse_armor` are all taken by other templates, the diamond one was free (one grep over
`data/armorpieces/recipe/template_*.json` before setting it). `python -m modpage build --offline`
warned `no texture for minecraft:diamond_horse_armor`; one plain `python -m modpage build` cached
it and both later builds are warning-free - the talons/flint pattern exactly, not the bedroll's
"no such file exists" case.

**For the next part.** The `spurs` socket's outboard flank below y 3.5 is not free space, whatever
the "back of the ankle above z 3 is empty" lesson suggests: that is true only *behind* z ~2.9.
`swim_fins` owns x -7.14..-4.11 out to z 2.0, so a part that hugs the boot's side rather than its
back will collect overlap notes; plan the sideways bits to start at z 2.1 if you want them clean.
Nine other tabs were open (aerials, dorsal_fin, swim_fins, epaulettes, thigh_sheath, shin_spikes,
spine_ridge, cord, loin_panels) and `armorpieces_new` made this one active without disturbing them.
