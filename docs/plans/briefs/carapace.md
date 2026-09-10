# Brief: Carapace

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the second
batch of four (skim the lessons in girdle.md for the body-bone neighbours and wing_cases.md for
the Carapace look). From the `back` row of `docs/plans/part-variety.md`:

> **Carapace** - A domed beetle back, segmented and glossy. Theme: Carapace. Fitting: `inlay`.

**Part.** `armorpieces:carapace`, socket `back` only, in the mod's own pack. Display name
"Carapace". Fittings: `armorpieces:inlay`, one mask, covering the whole shell - the dye is the
beetle's colour, matching Wing Cases and Aerials. No effects, no loot, no static layer.

**Shape.** `back` is not a mirrored socket: model the whole thing, centred on x = 0, on the body
bone. The torso box is x -4..4, y 12..24, z -2..2 (pivot 0, 24, 0); the chestplate shell is that
box inflated a full unit, x -5..5, y 11..25, z -3..3, and the anchor is at Blockbench (0, 22, 2)
on the back face. Anything with z under 3 is buried; sit faces a tenth off a shell plane, never
on it. Read the envelopes in the `armorpieces_new` reply: the belt parts share the bone (girdle
tops out at y 14.25 and reaches z 3.86; buckled_belt y 12.5..15.5, z to 3.5), so keep the
lowest segment above y 15.6 or say by how much it laps. The dome is a stack of four horizontal
segments (lames), each its own bone, each a wide flat cube spanning most of the back and
stepping OUT then back IN so the profile is a dome from the side and the top: top segment about
x -4.25..4.25, y 21.75..24.6, z 3.1..4.1; second x -4.75..4.75, y 19..21.95, z 3.1..5.0; third
x -4.75..4.75, y 16.5..19.2, z 3.1..4.8; bottom x -4.25..4.25, y 15.6..16.7, z 3.1..4.0 - each
overlapping the one above by a fifth of a unit. Nothing above y 25 and nothing wider than x ±5
(the arms swing past at x ±3..±5 below y 25 - the chestplate arm shells are x 3..9 and -9..-3,
so the dome must stay inside |x| 5 to not clip them). A one-texel seam ridge, 0.5 wide in x,
0.25 proud, running down the middle of the second and third segments, splits the shell into two
wing cases.

**Sheets.** Master: segments mid-dark `[top, bottom]` shaded lighter at the top of each so every
lame has its own highlight, a bright single-texel row along each segment's top edge as the gloss
(the `pixels` list, read off the sheet layout), the seam ridge brightest, the down faces dark.
Inlay mask: every face, the same gradient.

**Recipe.** Centre item `minecraft:cocoa_beans` (a flat item, unused by any template), paper
ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
carapace` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-03 in 21 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1 `list_outline`,
1 `armorpieces_part`, 4 `add_group`, 4 `place_cube`, 1 `modify_cube`, 2 `remove_element` (starter
cube, then its bone), 1 `armorpieces_check`, 1 `armorpieces_set_part`, **2 `armorpieces_paint`**,
1 `set_camera_angle`, 1 `armorpieces_save`. No `risky_eval`, nothing hand-edited, and the save went
through first time without `force`.

**What I built.** Four bones under `part`, one per lame, all unrotated - the dome is made by
stepping z, not by rotating anything, so no trigonometry was needed and the check matched the
placed numbers exactly. `lame_1` (pivot 0, 24, 3) carries `shell_1` x -4.25..4.25, y 21.75..24.6,
z 3.1..4.1; `lame_2` (pivot 0, 21.85, 3) `shell_2` x -4.75..4.75, y 19..21.95, z 3.1..5.0;
`lame_3` (pivot 0, 19.1, 3) `shell_3` x -4.75..4.75, y 16.5..19.2, z 3.1..4.8; `lame_4`
(pivot 0, 16.6, 3) `shell_4` x -4.25..4.25, y 15.6..16.7, z 3.1..**4.05**. The seam ridges are
cubes inside the second and third bones: `ridge_2` x -0.25..0.25, y 19.05..21.9, z 3.5..5.25 and
`ridge_3` x -0.25..0.25, y 16.55..19.15, z 3.5..5.05 - 0.5 wide, 0.25 proud, and deliberately
*inset* from their lame in y (0.05 top and bottom) and started at z 3.5 rather than the lame's
3.1, so no face of the ridge is coplanar with a face of its own shell. Envelope x ±4.75,
y 15.6..24.6 (Blockbench), z 3.1..5.25; reach 7.95, past the chestplate z+2.25 and x-0.25 - the
dome stays inside |x| 5 and so never touches the arm shells.

**The one number the brief got wrong by 0.05, and how the bridge caught it.** `shell_4` as briefed
(z 3.1..4.0) came back as a `!`: `COPLANAR: lame_4 and sash:belt's belt share the plane z = 4`.
The sash is a `belt`-socket part on the same bone, so a shared plane there is a real z-fight when
both are worn. One `modify_cube` to z 4.05 cleared it - the same "a tenth off a plane" rule the
brief gives for the armour shells applies to other parts' planes, and the check only names them
once you land exactly on one.

**The two `-` notes I accepted.** `OVERLAP: lame_4 into sash:belt's belt by 8.50 x 0.40 x 0.90`
and `near: lame_4 clears sash:belt's belt by 0.10 in y`. The sash's hull is x -7.25..6.0,
y 5.27..16.5, z -5..4 - a diagonal band, so its AABB claims a slab of the lower back it does not
actually fill, and the intersection with the bottom lame is a 0.4-high, 0.9-deep sliver at
y 15.6..16.5. The brief's shape cannot avoid it: any bottom lame low enough to finish the dome
above the belts (girdle tops at 14.25, buckled_belt at 15.5) is inside the sash hull, and raising
it above y 16.5 would open a two-unit gap over the belt line. No plane is shared after the 4.05
move, so it stays a note.

**Painting: two calls, one per sheet, 36 faces each, and they covered everything.** Master:
`"*.*": 100` as the base, then all 36 faces by name - outward `south` faces `[190,122]`,
`[185,116]`, `[178,110]`, `[172,104]` top lame to bottom (each lame a step darker so the stack
reads as separate plates), `up` 172→160, `down` 58→50, end caps `[140,88]`→`[128,76]`, the buried
`north` faces flat 62, and the ridges brightest (`[250,198]` / `[244,192]` south, 238/232 up,
`[228,168]` sides) - plus 40 `pixels`: the top row of each `south` rectangle at 236/232/228/224
as the gloss, and one 255 texel at the top of each ridge. `south` is the outward (+z) face on the
back socket; the sheet layout block gives each rectangle as `x,y w x h`, so the gloss row for
`shell_1` is `south 23,1 9x3` → y 1, x 23..31. The inlay mask is the identical face map (the brief
asks for the same gradient, and the dye is the beetle's whole colour) - 404 opaque texels on both
sheets, so the mask silhouette is exactly the master's, greyscale, 50..255.

What the painter did **not** cover: anything that is not a whole face or a listed texel. The
per-lame gloss row had to be enumerated as 40 explicit pixels because a `[top, bottom]` gradient
ramps over the whole face and a gloss line wants a hard step; and the seam between the two wing
cases reads only because `ridge_2`/`ridge_3` are real geometry standing 0.25 proud - a painted
seam column would have been another hand-placed texel run and would vanish at three metres.

**For the next part.**
- A stack of flat lames needs no rotated bones at all: step `z` out and back in (4.1 → 5.0 → 4.8 →
  4.05 here) and the side profile is a dome, with every cube axis-aligned and every face rectangle
  a clean box-UV strip. Overlap in `y` by 0.2 and the joints never gap.
- Give an add-on cube (a ridge, a stud) a slightly smaller extent than the cube it sits on *and*
  start it inside that cube's volume, or you buy yourself coplanar faces within your own part.
- `minecraft:cocoa_beans` is a flat item and was free; `python -m modpage build --offline` warned
  it had never been cached, one plain `python -m modpage build` fetched the icon and reported the
  three pages `unchanged`, exactly as the wing_cases and girdle sessions found.
- Six cubes with two 9.5-wide lames fit a 64x32 sheet with most of it still empty (404 texels).
