# Brief: Bedroll

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the fourth
batch of four, a Wayfarer set (skim the lessons in carapace.md for the back frame and the
belt-line neighbours). From the `back` row of `docs/plans/part-variety.md`:

> **Bedroll** - A rolled blanket and straps across the shoulders. Theme: Wayfarer. Fitting:
> `inlay`.

**Part.** `armorpieces:bedroll`, socket `back` only, in the mod's own pack. Display name
"Bedroll". Fittings: `armorpieces:inlay`, one mask, covering the blanket roll; the two straps
and their knots stay the material. No effects, no loot, no static layer.

**Shape.** `back` is not a mirrored socket: model the whole thing, centred on x = 0, on the body
bone. The torso box is x -4..4, y 12..24, z -2..2 (pivot 0, 24, 0); the chestplate shell is that
box inflated a full unit, x -5..5, y 11..25, z -3..3, and the anchor is at Blockbench (0, 22, 2)
on the back face. Anything with z under 3 is buried. Read the envelopes in the `armorpieces_new`
reply: the same-socket parts (banner, pinions, quiver, wing_roots, carapace) are never compared;
the belt parts are far below, the collar parts in front, so expect a clean bone. The roll lies
ACROSS the upper back, horizontal along x, and it is round: make it from two cubes in one `roll`
bone - the first x -6..6, y 21.4..24.2, z 3.1..5.9 (2.8 square in section, centred on y 22.8,
z 4.5), and a second identical cube in a child bone `roll_turned` pivoted at the roll's axis
(0, 22.8, 4.5) and rotated 45 degrees about X, so the two squares make an octagon and the roll
reads as a cylinder from every side. The turned cube's corners reach 0.58 further than the
flat one's faces: check that its lowest corner stays above the belt line (it will, at y 20.8)
and its inboard corner stays outside the shell (axis z 4.5 minus 1.98 is 2.52, INSIDE the
shell's z 3 - so either move the axis out to z 5.0 or shrink the turned cube to 2.4 square;
pick one and say which). Nothing wider than x ±6.1 - the roll overhangs the torso by a unit
each side, over the shoulder shells (x 3..9 at y 11..25, whose back plane is z 3, so a roll at
z above 3.1 clears them). Two `strap_l` / `strap_r` bones at x -3.5..-3 and 3..3.5, each a
single band cube 0.5 wide that wraps the roll: y 21.25..24.35, z 2.95..6.05 (a tenth larger than
the roll's flat cube on every side; its back face at z 2.95 is inside the shell and never seen),
with a 0.6-square knot cube on the band's top face at y 24.35..24.95. That is six cubes.

**Sheets.** Master: the roll's flat cube `[top, bottom]` from light on top to dark underneath,
the turned cube the same values so the octagon shades continuously, and two darker texel
columns near each end as the rolled edge showing (`pixels`); straps mid grey with a lighter
top row; knots bright. Inlay mask: the two roll cubes' faces only, the same gradient.

**Recipe.** Centre item `minecraft:red_bed` (a flat item, unused by any template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py bedroll`
and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons paragraph below
filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

Built 2026-09-03 in 17 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1 `list_outline`,
1 `armorpieces_part`, 4 `add_group`, 4 `place_cube`, 2 `remove_element` (starter cube, then its
bone), 1 `armorpieces_check`, 2 `armorpieces_set_part`, **2 `armorpieces_paint`**, 2
`set_camera_angle`, 2 `armorpieces_save`. No `risky_eval`, nothing hand-edited, and the first save
went through without `force` - the check reported `ok: nothing needs a decision`, with no `!` and
no `-` note at all, so nothing was accepted against the check.

**What I built.** Four bones under `part`: `roll` (pivot 0, 22.8, 5.1) with `roll_core`
x -6..6, y 21.4..24.2, z 3.7..6.5; its child `roll_turned` (same pivot, rotation 45 about X) with
`roll_edge` x **-5.9..5.9**, same y/z; `strap_l` (pivot -3.25, 22.8, 5.1) with `band_l`
x -3.5..-3, y 21.3..24.3, z 2.95..6.6 and `knot_l` x -3.55..-2.95, y 24.1..24.85, z 5.95..6.55;
`strap_r` mirrored by hand (`back` is not a mirrored socket). Envelope x ±6, y 20.82..24.85,
z 2.95..7.08; reach 7.83, past the chestplate z+4.08; all nine other `body` parts clear by more
than half a unit.

**The z-axis decision the brief asked for, and why its second option does not work.** With a 2.8
square section the turned cube's half-diagonal is 1.4·√2 = 1.98, so its inboard corner sits 1.98
in front of the axis. The brief offered "move the axis out to z 5.0 or shrink the turned cube to
2.4 square". *Shrinking does not clear the shell*: 1.2·√2 = 1.697, and 4.5 − 1.697 = 2.80, still
inside the chestplate's z 3 (and a 2.4 cube inside a 2.8 one stops making an octagon anyway).
Moving the axis to 5.0 clears by 0.02, which is inside the tenth-of-a-unit margin every other
brief uses. So I **moved the axis out to z 5.1** and kept the full 2.8 section: inboard corner
3.12, 0.12 past the shell; outboard corner 7.08. The straps and knots moved with it (band z
2.95..6.6, still with the back face buried inside the shell as the brief intended).

**Two self-coplanar traps I designed out before placing anything** (the carapace lesson, applied):
rotation about X does not change a cube's x extent, so a full-width turned cube would have shared
the planes x = ±6 with the flat one over the whole octagon overlap - `roll_edge` is 11.8 wide, not
12. And the knot starts *inside* the band (y 24.1 against the band's top face at 24.3, 0.05 proud
in x on both sides, z 5.95..6.55 inside the band's 2.95..6.6), so it shares no plane with the cube
it sits on. Its z was pushed to the front-top corner deliberately: on the octagon's diamond
section |Δy| + |Δz| ≤ 1.98, and a knot centred on the axis (Δz ≈ 0) would have been buried in the
roll's top corner; at Δz ≈ 0.85..1.45 it sits clear.

**Painting: two calls, one per sheet, and they covered everything.** Master: `"*.*": 100` then all
36 faces by name - the roll shaded as a continuous octagon by walking the ring of normals
(flat `up` [230,210] → turned `up` [212,196] → flat `south` [190,130] → turned `south` [124,92] →
flat `down` [62,54] → turned `down` [70,60] → buried `north` 78/132), end caps [196,116] and
[186,108], bands [168,108] on their broad east/west flanks with `up` 198, knots 226 with `up` 246 -
plus 40 `pixels`: two 3-texel dark columns near each end of both roll cubes' `up` and `south`
rectangles (the rolled blanket edge) and a hard 4-texel lit top row on each band flank. The inlay
mask is the roll's 12 faces and its 24 edge texels only, identical values, so the dye shades with
the same octagon ramp; the bands and knots stay trim material, as briefed. `south` is the outward
(+z) face on `back`; a positive X rotation sends `up` to up-and-outward and `south` to
down-and-outward, which is what makes the eight-face ramp monotonic.

What the painter did **not** cover: nothing that is a whole face was a problem, but the rolled-edge
columns and the band's gloss row had to be enumerated as explicit texels - a `[top, bottom]` pair
ramps across a face and cannot make a hard line or a vertical stripe. There is no spiral on the end
caps beyond one gradient; at 12 units wide the roll reads as a cylinder from the octagon alone.

**The recipe: `minecraft:red_bed` is NOT a flat item.** The brief called for it and the bridge
accepted it, but `modpage build` warned `no texture for 1 item(s), drawn as missing-texture
(minecraft:red_bed)` - and a plain (non-`--offline`) build warned identically, because a bed has
neither `item/red_bed.png` nor `block/red_bed.png`; its only texture is `entity/bed/red.png`. Blocks
in general are fine (`hay_block`, `white_wool`, `iron_bars`, `torch` are all in use and resolve from
`block/<id>.png`); the bed, the shield and the banners are the special cases that need hand-drawn
icons in `tools/gen_recipe_icons.py`. Rather than add a hand-drawn bed to a shared tool I changed
the centre to **`minecraft:red_wool`** - flat (block texture), unused by any other template, and a
red blanket is what the bed was standing for. One `armorpieces_set_part` + `armorpieces_save`, and
the build is warning-free.

**For the next part.**
- Two identical cubes, one in a child bone rotated 45 about X, is a cheap round profile - but size
  it from the half-diagonal (side·0.707), never from the half-side, and give the turned cube a
  slightly shorter length so its end caps are not coplanar with the flat cube's.
- The `back` socket's belt-line neighbours all top out at y 16.5 (sash) or lower, so anything
  living above y 20 on the upper back has the bone to itself; the collar parts are all at z ≤ 0.75.
- Before committing to a brief's centre item, remember the three vanilla families with no flat
  sprite at all: beds, banners and shields. `python -m modpage build` (online) warning about a
  texture it "has never cached" is different from this - here even the online build warned, which
  is the tell that no such file exists.
