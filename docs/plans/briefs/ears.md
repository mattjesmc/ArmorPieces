# Brief: Ears

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the fifth
batch of four, a Beast set (skim the lessons in aerials.md - the head frame, the brow band's
top at y 30.75, the two workspace-killing traps - and bone_mask.md). From the `horns` row of
`docs/plans/part-variety.md`:

> **Ears** - Upright animal ears, tufted inside. Theme: Beast. Fitting: `inlay` (the inner ear).

**Part.** `armorpieces:ears`, socket `horns` only, in the mod's own pack. Display name "Ears".
Fittings: `armorpieces:inlay`, one mask, covering the inner-ear plate only; the ear itself stays
the material. No effects, no loot, no static layer.

**Shape.** `horns` is a mirrored socket on the head bone: model ONE side, the LEFT, which in this
rig is at NEGATIVE x. The head box is x -4..4, y 24..32, z -4..4 (pivot 0, 24, 0); the helmet
shell is that box inflated a full unit, x -5..5, y 23..33, z -5..5; the left temple anchor is at
Blockbench (-4, 29, 0). "Outboard" is more negative x. Read the envelopes in the
`armorpieces_new` reply: the brow parts' bands top out at y 30.75 (circlet) and the crest parts
all live inboard of x ±2.5, so an ear standing on the helmet's top corner is clear of both.
Build an `ear` bone pivoted at (-4.8, 32, 0) and rotated about Z so the ear leans OUTBOARD by
about 15 degrees (for an upright above its pivot on the negative-x side a POSITIVE Z rotation
tips the top toward -x - confirm on the first reply). The ear is two stacked cubes in that
bone, modelled upright in the unrotated pose: `ear_lower` x -5.6..-4.1, y 31.5..34.5,
z -1.25..1.25 (its lower half straddles the helmet's top corner - the inside is buried, paint it
anyway) and `ear_tip` x -5.3..-4.4, y 34.5..36.25, z -0.75..0.75. On the ear's FRONT face
(north, -z) an `inner` cube standing 0.2 proud: x -5.25..-4.45, y 32.4..34.3, z -1.45..-1.25 -
the tufted inner ear that takes the dye. Nothing above y 36.5 in the rotated pose, nothing
inboard of x -4.1.

**Sheets.** Master: ear mid grey `[top, bottom]` darker toward the tip on the back (south) face
and lighter on the front, tip a step lighter; inner plate lighter still with a darker centre
column of two texels (`pixels`) as the tuft's shadow. Inlay mask: the inner plate's faces only,
the same shading.

**Recipe.** Centre item `minecraft:carrot` (a flat item, unused by any template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py ears`
and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons paragraph below
filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-03 in 17 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`armorpieces_part`, 1 `list_outline`, **1 `add_group`**, 3 `place_cube`, 2 `remove_element`
(starter cube, then its `main` bone), 1 `armorpieces_check`, 1 `armorpieces_set_part`, **2
`armorpieces_paint`** (one per sheet), 2 `set_camera_angle`, 1 `armorpieces_save`. No
`risky_eval`, no `modify_cube`, no nudging, nothing hand-edited, and the save went through first
time **without `force`**. The three checks after it (`check_part ears`, `check_authoring`,
`modpage build`) were clean on the first run.

**What I built, exactly as the brief specified.** One bone `ear` at pivot (-4.8, 32, 0) rotated
Z **+15**, holding `ear_lower` (x -5.6..-4.1, y 31.5..34.5, z ±1.25), `ear_tip` (x -5.3..-4.4,
y 34.5..36.25, z ±0.75) and the proud `inner` plate (x -5.25..-4.45, y 32.4..34.3, z -1.45..-1.25).
**The sign was worth predicting rather than testing:** for a cube *above* its pivot on the
negative-x side, rotate-about-Z maps local (0,h) to (-h sinθ, h cosθ), so a POSITIVE θ tips the
top toward -x, i.e. outboard - the reply confirmed it on the very first cube (`past helmet
y+1.60` = the rotated top at 34.596 against a predicted 34.596, and after `ear_tip`
`past helmet x+1.38` = min x -6.38 against a predicted -6.383). Rotated envelope: Blockbench
x -6.38..-3.99, y 31.31..36.21, z -1.45..1.25; pair spans 12.77, well inside the shoulders.

**`!` lines accepted: none.** The finished check reports zero problems and no `-` notes at all -
the only ones that ever appeared were the starter cube's unpainted faces and "every pixel is
transparent". Clash: *"all clear by more than half a unit"* from all eleven other-socket parts,
because the ear's lowest rotated corner is y **31.31**, 0.56 above `circlet`'s 30.75 top plane,
and its z band (-1.45..1.25) misses `coronet` (-6.18..-2.25) and `visor` (-7.76..-3.75) entirely.

**One number of the brief's own is unreachable, and it is harmless.** "Nothing inboard of x -4.1"
does not survive the 15-degree tip: the bottom-inboard corner of `ear_lower` (local dx +0.7,
dy -0.5) swings to x **-3.99**, 0.11 inboard of the stated bound and 0.006 past the head box's
x -4 plane. I kept the brief's cube instead of trimming, because that corner sits at y 31.7,
which is *inside* the helmet shell (x -5..5, y 23..33) - it is buried, it cannot z-fight (nothing
is coplanar once the bone is rotated), and the crest parts it was meant to avoid stop at x ±3.24
(`antennae`), still a quarter unit inboard. Rule for a rotated upright: the envelope's inboard
edge is the *bottom* corner swinging in, not the top, and it moves by (half-width)(1-cosθ) +
(drop below pivot)(sinθ) - so a bone pivoted at the cube's own bottom would have cost nothing.

**Two paint calls: master 36 faces + 3 pixels, inlay mask 6 faces + 3 pixels, and they covered
everything** (18/18 faces painted, 68 opaque texels on the master 70..225, 10 on the mask
120..225, both greyscale confirmed with Pillow). Master: `*.*` 120, then the back `south` faces
darkening upward (`[100,145]` lower, `[125,150]` tip), the fronts light (`[170,130]`,
`[200,180]`), the outboard `west` a step brighter than the inboard `east` (155/110 vs 95; 185/150
vs 110), `up` 180/215 and `down` 70/85, with the whole `ear_tip` a step lighter than `ear_lower`
so the tip reads at three metres. The inlay mask is the six `inner` faces at the master's own
values, so the dye takes the plate's shading rather than a flat fill.

What the painter did **not** cover: **the brief's "darker centre column of two texels" on the
inner plate does not exist as a column.** The plate is 0.8 x 1.9 x 0.2, which box-UVs to a
`north` face of exactly **1x2 texels** - its centre column *is* the whole face, so darkening it
would darken the plate. The tuft shadow went in instead as a shadow *band across the plate's
base*: `pixels` on the lower texel of the front (29,2 = 160) and of both side faces (28,2 and
30,2 = 130), on the master and again on the mask. Same trap as bone_mask and antennae from the
other end: under about 2 units a face has no interior, so detail has to be a step between faces,
not a pattern inside one. `[top, bottom]` pairs did work here - `ear_lower`'s faces are 3 texels
tall and the tip's 2 - which is the first part in this batch where the gradient earned its keep.

**For the next part.** `minecraft:carrot` is now taken as a template centre. The build dance has
shortened: `python -m modpage build --offline` warned once that carrot had never been cached, one
plain `python -m modpage build` fetched it and reported **`unchanged`** immediately (no third
build needed - the markdown does not change when only a recipe icon is filled in). On `horns`,
the helmet's **top** corner (x -5, y 33) is as empty as its side: everything on `crest` is
inboard of x 3.24 and everything on `brow` is below y 33.21 or behind z -2.25, so an upright
standing at x -4.8 above y 31.3 clears the whole bone before it is drawn - and, unlike a temple
part, it needs no boss to look attached, because the helmet corner meets it halfway.
