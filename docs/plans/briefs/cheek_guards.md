# Brief: Cheek Guards

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the seventh
batch of four, a Knightly set (read aerials.md and ears.md first - the head frame, the brow
band's planes, the two workspace-killing traps). From the `horns` row of
`docs/plans/part-variety.md`:

> **Cheek Guards** - Hinged plates hanging beside the jaw off a temple rivet. Armour where
> everything else here is ornament. Theme: Knightly. Fitting: `guard`.

**Part.** `armorpieces:cheek_guards`, socket `horns` only, in the mod's own pack. Display name
"Cheek Guards". Fittings: `armorpieces:guard`, one mask, covering the rivet and the plate's
raised edge bar; the plate itself stays the material. No effects, no loot, no static layer.

**Shape.** `horns` is a mirrored socket on the head bone: model ONE side, the LEFT, at NEGATIVE
x. The head box is x -4..4, y 24..32, z -4..4 (pivot 0, 24, 0); the helmet shell is that box
inflated a full unit, x -5..5, y 23..33, z -5..5; the left temple anchor is at Blockbench
(-4, 29, 0). "Outboard" is more negative x. Read the envelopes in the `armorpieces_new` reply:
the brow parts share the bone and `circlet`'s band wraps the temples at y 27.75..30.75 out to
x ±6, `coronet` to 33.21 forward of z -2.25, `visor` forward of z -3.75 - a cheek plate on the
side of the helmet lives at x -5.1 or further out and dodges their planes by a twentieth. Build:
a `rivet` bone with a rivet cube 0.8 square straddling the shell's side plane, x -5.45..-4.65,
y 28.6..29.4, z -0.4..0.4; a `plate` bone pivoted at the rivet (-5.05, 29.0, 0) rotated about Z
so the plate flares OUT at the bottom by 6 degrees (for a cube BELOW its pivot on the negative-x
side a NEGATIVE Z rotation swings the free end toward -x - pendant and wing_cases measured it;
confirm on the first reply), carrying the cheek plate x -5.5..-5.1, y 24.4..28.7, z -2.4..1.6
(a tenth past the shell's x -5 and lapping the rivet by a tenth) and a raised edge bar along
the plate's bottom, x -5.7..-5.5, y 24.4..24.9, z -2.4..1.6. Nothing below y 24.2 (the
helmet's bottom is y 23; the plate stops at the jaw) and nothing inboard of x -4.65.

**Sheets.** Master: plate mid grey `[top, bottom]` lighter at the top with a darker column
along its rear edge (`pixels`), rivet bright with a brightest top texel, edge bar bright with a
dark underside. Guard mask: the rivet's and the bar's faces only, shaded like the master.

**Recipe.** Centre item `minecraft:chainmail_helmet` (a flat item, unused by any template),
paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
cheek_guards` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built 2026-09-03 in 18 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`armorpieces_part`, 1 `list_outline`, 2 `add_group`, 3 `place_cube`, 2 `remove_element`
(starter cube, then its `main` bone), 1 `armorpieces_check`, 1 `armorpieces_set_part`,
**2 `armorpieces_paint`** (one per sheet), 2 `set_camera_angle`, 1 `armorpieces_save`. No
`risky_eval`, no `modify_cube`, no nudging, nothing hand-edited; the save went through first
time **without `force`**, and `check_part`, `check_authoring` and `modpage build --offline`
were all clean on the first run.

**What I built, exactly the brief's numbers.** An unrotated `rivet` bone (pivot -5.05, 29, 0)
with `boss` x -5.45..-4.65, y 28.6..29.4, z +-0.4 - half in, half out of the helmet shell's
x -5 plane - and a `plate` bone on the same pivot rotated Z **-6**, carrying `cheek`
x -5.5..-5.1, y 24.4..28.7, z -2.4..1.6 and `edge_bar` x -5.7..-5.5, y 24.4..24.9, z -2.4..1.6.
**Sign confirmed by arithmetic before the first cube, then by the reply:** for a cube *below*
its pivot on the negative-x side, rotate-about-Z maps (dx, dy) to (dx cos - dy sin,
dx sin + dy cos), so with a NEGATIVE angle the negative dy term pushes x outboard - predicted
envelope min x -5.978 for the plate alone (reply `past helmet x+0.98`) and -6.177 with the bar
(`past helmet x+1.18`, check `x .. 6.18`). Rotated envelope Blockbench x -6.18..-4.65,
y 24.43..29.40, z -2.40..1.60; pair spans 12.35, well inside the shoulders' 18.

**`!` lines accepted: none** - the finished check reports zero problems. Three `-` notes stand,
and the two OVERLAP ones deserve a paragraph, because the check asks you to "check whether the
real cubes meet" and **here they do**. `circlet`'s geometry is a band whose *side rails* are
2 units wide (game x 4..6, i.e. Blockbench x -6..-4) running the whole length of the temple at
band height, so the rivet (x -5.45..-4.65, y 28.6..29.4, z +-0.4) sits **inside** the left rail,
and the plate's top unit (y 27.75..28.75, where the rotation has it at x -5.63..-5.13) does too.
I accepted both: nothing is coplanar (nearest planes are 0.25 apart in y and 0.35 in x, so no
z-fighting), circlet is 1 of the 12 parts on the head bone and the other 11 are clear, and a
brow band passing *over* a jaw hinge is how a real cheek plate is built - the hinge is under the
band by design. Avoiding it entirely was not open: the rivet has to straddle the helmet's x -5
side plane to look attached, and the circlet owns x -6..-4 at y 27.75..29.75 all the way round.
The third note (`plate clears coronet's band by 0.30 in y`) is a genuine miss, not a touch.

**Two paint calls, master 36 face writes (18 faces: `*.*` 140 then every face by name) + 5
pixels, guard mask 12 faces, and they covered everything** - 0 unpainted faces, no stray paint,
82 opaque master texels 70..255 and 24 mask texels 90..255, greyscale confirmed with Pillow.
Master: plate `west` (outboard) `[175, 120]`, `east` (inboard, mostly hidden but painted)
`[120, 85]`, `north` 150..105 / `south` 130..90 on the 1-wide edges, `up` 190, `down` 70;
bar bright all round (195..210) with `down` 90 for the dark underside; boss 200..230 with
`up` 255.

What the painter did and did not cover: **`[top, bottom]` pairs earned their keep only on the
cheek plate** - its `east`/`west` are 4x5 texels (a 4.3-tall cube rounds to 5 rows), while every
bar and boss face is 1 texel tall or 1x1, so those are flat values and the brief's "brightest
top texel" on the rivet is literally its `up` face. The rear-edge column had to be `pixels`, and
**working out which column is the rear needs the strip direction for a cube whose broad face is
a SIDE**: the box-UV strip runs east -> north -> west -> south around the vertical axis, so on
`west` texture-right runs toward **+z (rear)** - the rear column is the face's LAST x (x=8 here,
rows 4..8, 110 down to 88) - and on `east` it is reversed, the rear is the FIRST column. (The
aerials lesson gives the same rule for cubes whose long axis is x; this is the z-axis case.)
The guard mask is the boss's and the bar's 12 faces at the master's own values, so the fitting
takes the shading; the cheek plate is left unmasked and stays the trim material, as the brief
asked.

**For the next part.** `minecraft:chainmail_helmet` is now taken as a template centre, and it
needed **no cache round trip** - `python -m modpage build --offline` rendered all 86 recipes
without the "never cached" warning the last few sessions hit, so a vanilla *armour* item was
already in the icon cache; a second build reported `unchanged`. On `horns`, the **jaw** zone
(y 24..27.7 outboard of x -5) is completely empty - visor and nasal are far forward of z -3.75,
bone_mask is at z -6.10..-5.10, and everything else on the bone is above y 26 and inboard of
x 4.1 - so a part that hangs below the brow band is clear the moment it drops under y 27.75.
Above that line, up to y 30.75 and inboard of x 6, you are in circlet's rails and the only
question is whether you mind.
