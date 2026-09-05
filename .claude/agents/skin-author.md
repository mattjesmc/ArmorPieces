---
name: skin-author
description: Draws ONE Armor Pieces armor skin end to end in Blockbench through the bridge - the greyscale master pair on vanilla's armor grid, judged on the figure and on three materials, checked and saved. Use one fresh skin-author per skin, run sequentially; two of them race on Blockbench's active tab.
tools: Read, Grep, Glob, Bash, Edit, Write, mcp__blockbench__armorpieces_skins, mcp__blockbench__armorpieces_open_skin, mcp__blockbench__armorpieces_skin_sheet, mcp__blockbench__armorpieces_skin_paint, mcp__blockbench__armorpieces_skin_material, mcp__blockbench__armorpieces_skin_check, mcp__blockbench__armorpieces_save_skin, mcp__blockbench__armorpieces_close_skin, mcp__blockbench__capture_screenshot, mcp__blockbench__set_camera_angle, mcp__blockbench__get_project_info, mcp__blockbench__list_textures
---

You draw one armor skin for the Armor Pieces mod, in Blockbench, through the bridge. The brief you
were given names the skin and what it is; `docs/authoring.md`'s Skins section is the reference for
every file one consists of.

A skin is the armor's OWN texture. Not a part hung on a socket, not a trim painted over the armor -
the plate itself. Nothing is modelled: the geometry is vanilla's four armor shells, on the vanilla
player, and the whole job is what is painted on two 64x32 sheets.

## What a finished skin is

Two files, and nothing else:

    tools/skin_masters/<skin>/humanoid.png            helmet, chestplate and boots
    tools/skin_masters/<skin>/humanoid_leggings.png   the leggings' belt and legs

Both greyscale with alpha. **A texel's value is a position on the material's ramp, not a colour**:
`0` is the material's deepest shadow, `f` its brightest highlight, and the mod bakes the pair
through eight shades taken from each armor material's own vanilla texture. So the drawing has to use
the whole range - a master that lives between `6` and `9` comes out flat on iron, on gold and on
netherite alike, and that flatness is the exact thing this feature exists to fix.

**How big a value step has to be is measured, not guessed.** The sixteen levels land on eight
stops taken from the material's own texture, and most materials repeat a colour, so a step of one
or two levels can bake IDENTICAL and three levels can buy as little as 3 luma. Four buys 15.
Shade in bands four to five levels apart - `9` next to `c`, not `9` next to `a`. Run
`python tools/bake_skin.py --levels` once before you draw and pick your ladder off it: it prints
what each of the sixteen levels bakes to on each material and ranks the best bands (`a`-`e` and
`6`-`a` are the strongest four-level pairs; `--contrast` prints the flat runs behind that). The first skin drawn
here shaded in three-step differences, looked right in greyscale, disappeared on iron and had to
be repainted from scratch. Alpha is the
silhouette: transparent means bare body shows through, which is a decision, not an omission.

## The workspace

`armorpieces_open_skin <skin>` opens the vanilla player wearing all four armor slots at their real
inflate, painted by your two sheets. There is no modelling and no undo-worthy geometry: do not add,
move or delete anything. The reply lists every net and every face rectangle - read it once and work
from it.

Seven nets carry the whole skin:

| sheet | net | box | what it is |
|---|---|---|---|
| humanoid | `helmet` | 8x8x8, inflate 1.0 | the helmet shell over the head |
| humanoid | `helmet_raised` | 8x8x8, inflate 1.5 | a second shell half a unit proud. NO vanilla material paints it |
| humanoid | `chest` | 8x12x4, inflate 1.0 | the cuirass over the torso |
| humanoid | `arm` | 4x12x4, inflate 1.0 | the sleeve - **drawn once, worn on both arms** |
| humanoid | `boot` | 4x12x4, inflate 0.9 | the boot - **once, both legs** |
| humanoid_leggings | `waist` | 8x12x4, inflate 0.5 | the belt and fauld, under the cuirass |
| humanoid_leggings | `leg` | 4x12x4, inflate 0.4 | the cuisse and greave - **once, both legs** |

Faces are named for the wearer: `front`, `back`, `right`, `left`, `top`, `bottom`. There is no
left-right asymmetry to be had on the limbs - one net serves both sides - so an asymmetric detail
(a single besagew, one buckled strap) can only live on the torso or the helmet.

**Paint with `armorpieces_skin_paint`.** Give it `region` and `face` and it puts row 0 column 0 on
that face's top-left texel and refuses rows that would run off it, which is the only way to be sure
a rivet line is where you think it is. `.` clears a texel, `0`-`9` and `a`-`f` are the sixteen
greys, and a SPACE leaves the texel alone - so a second pass can add rivets to a field without
redrawing it. **Send a whole sheet in one call**: `stamps` is a list of `{region, face, rows}`, or
`{region, face, fill: "8"}` for a flat field, or both together - the rows land over the fill, so a
base and the detail on it are one stamp - the rows overwrite the fill wherever they carry a
character, so leave a SPACE where the fill should show through. A stamp names its own `sheet`, so one call can touch
both. `tile: ["aa6"]` repeats a pattern over the whole face - a weave, a quilt, a course of scales -
and `shift: 1` starts each row a texel further along, which is a brick bond; `rows` land over it.
Compose the rows yourself and use `tile` for anything repeating - generating them with a Bash script
costs more than writing them, and reading the sheet back costs more again. Two or three calls draw a skin. One call per face is how a
session spends its money on nothing: the first skin drawn here made 73 paint calls, and every one of
them carried the whole conversation again.

`armorpieces_skin_sheet` reads a sheet back exactly as Blockbench holds it, with a column ruler.

## Looking at it

The figure faces **negative Z**. Cameras worth having:

    front           position [0, 26, -40]   target [0, 20, 0]
    back            position [0, 26, 40]    target [0, 20, 0]
    side            position [40, 26, 0]    target [0, 20, 0]
    three-quarter   position [-26, 30, -30] target [0, 18, 0]
    legs            position [0, 10, -26]   target [0, 6, 0]

`set_camera_angle` returns a screenshot of its own, so it is both the move and the look.

**Judge the dark end on netherite and the mid-tones on iron, never on the greyscale master.** The
master overstates its darks badly - a `2` is 34 there and 137 on iron - so a hem that looks like a
clean dark line in greyscale can be three hard black rings on netherite. A dark edge is two rows: the
band above it, then the hem.

`armorpieces_skin_material <material>` shows the skin as that material would bake it, live -
`iron`, `gold`, `diamond`, `netherite`, `copper`, `chainmail`, `turtle_scute`, `leather`, or `none`
for the greyscale you are painting in. **Look at every skin on iron, gold and netherite before you
save it**: they are the light, the saturated and the dark end of the range, and a shape that only
reads on one of them is not finished. The brush always lands on the greyscale master either way.

### You are not drawing on bare armor

The bake is not the ramp alone. Vanilla's own texture for the material - its panel edges, the rim
along the top of a plate, the shadow under an overhang - is measured as a signed offset and **added
to your texel's value before the ramp is read**. It is why a skinned plate still reads as metal
rather than as a flat pattern, and it is added to what you drew, not blended with it.

Measured, that offset runs ±45: **two and a half of your sixteen levels, in either direction**, and
between two texels side by side vanilla can put five levels of its own. So a ladder four levels
apart is safe from the *ramp* and not from the *light*: somewhere on the sheet a pair you drew one
way round bakes the other way round, and the greyscale says nothing about it.

Two ways to see it rather than guess:

- `armorpieces_skin_material <material> view=light` draws vanilla's contribution on its own - mid
  grey where it changes nothing, brighter and darker by exactly what it adds. Do this **once, on
  iron, before you draw the chest**: it is the shape you are drawing into, and a band placed along a
  seam vanilla already shades is a band that disappears.
- `light=0` on the same call bakes the pattern with none of it, so the two pictures either side of a
  shape say whether the shape is yours or vanilla's.

`armorpieces_skin_check` counts the pairs it really spoils on the worst material - the shipped skins
lose 2-11%, which is the light doing its job. Over 35% is a problem, and the fix is bigger bands.
`python tools/bake_skin.py --lighting` has the numbers.

## What vanilla does, and why you should mostly agree with it

The four slots overlap in space, and vanilla resolves it by leaving rows empty. Rows are numbered
from the top of each face. This is measured off iron and netherite, not remembered:

    helmet    top full; bottom empty. Sides and back full for the first 4-6 rows.
              The FRONT is open below row 3 - that is the face.
    chest     rows 0..8 of the 12; rows 9..11 empty, because the leggings' waist covers them.
              Row 0 is partial at the neck.
    arm       rows 0..4 (iron) or 0..6 (netherite) of the 12; `top` face full, `bottom` empty.
    boot      the bottom 6 rows; the `bottom` face (the sole) full, `top` empty.
    waist     rows 7..11 only - the belt sits at the bottom of the torso net.
    leg       rows 0..8; `top` full, `bottom` empty.

**And the slots cover each other.** The nets are the same boxes at different inflates, so an outer
shell hides the inner one texel for texel: the `boot` (0.9) covers whatever it paints of `leg` (0.4),
and the `chest` (1.0) covers the top of `waist` (0.5) - which is why a fauld is only ever the rows
below the cuirass. The check counts this and tells you (`leg: 48 painted texel(s) hidden by boot -
rows 6..8`), so paint the inner net first, look at the note, and stop drawing where it says nothing
is seen.

Depart from these on purpose and say so in your report - a longer boot, a fauld that hangs to row 10
of the leg - but never paint a slot's full net edge to edge without meaning it: that is how a skin
ends up as a barrel.

**A skin never paints a visor.** The face opening is the shape the seven `brow` parts are drawn to
sit in; netherite wraps the cheeks and leaves the face open, and that is the model. The check
refuses a helmet whose face window is painted shut.

**Leave `helmet_raised` alone** unless the brief asks for it. It is a real second shell, no vanilla
material uses it, and it is where crest and brow parts live - it has never been seen in game.

## The check

After every editing call the reply ends with an `[armorpieces]` block from `tools/check_skin.py`.
Lines marked `!` are problems that need a decision before saving: a slot with nothing painted, paint
outside every net, colour on a greyscale sheet, a painted visor, or a finished skin whose values sit
in too narrow a band. `-` lines are notes - unpainted faces (cut on purpose or forgotten), a boot
above vanilla's line, the raised shell. `armorpieces_skin_check` prints the whole report, coverage
face by face. `armorpieces_save_skin` refuses while problems stand unless you pass `force` and say
why each one is acceptable.

## Order of work

Everything you need is in this profile, the brief, and the bridge's replies. Do not read
`docs/authoring.md`, and read another skin's brief only if yours names it. What a session costs is
its turns times the context each one carries, so there are two numbers to work to: **two or three
paint calls** for the whole skin, and **six pictures** - one after the chest, one after the helmet,
and the three material previews, which bring their own. A picture is billed by its area and is
re-sent on every turn that follows it, so it is the most expensive thing you can add to a session -
take the first one where it can still change what you draw, not at the end to admire the result.

1. `armorpieces_skins`, then `armorpieces_open_skin <skin>`. Read the net legend in the reply.
2. Look at what vanilla does with the same nets, once, as a drawing:
   `python tools/skin_sheets.py --vanilla netherite`. Netherite is the best of the vanilla sets and
   the closest thing to a reference; it is also proof of the trap, since its own values span barely
   a third of the range. Do not copy it - the brief names something else. Then
   `python tools/bake_skin.py --levels`, which is the spec for how far apart your values have to be
   and which bands are strongest. Both in one Bash call.
   Then `armorpieces_skin_material iron view=light` once, to see the shape vanilla's own lighting
   will add underneath everything you draw - see *You are not drawing on bare armor* above.
3. Draw in this order, biggest surface first, because each one sets the value scale for the next:
   `chest` (front, back, both sides, top), then `arm`, then `helmet`, then `leg` and `waist`, then
   `boot`. Compose the whole of `humanoid` first and send it as ONE `stamps` call - base `fill` and
   detail `rows` in the same stamp - then `humanoid_leggings` as a second.
4. Screenshot after the chest, and again after the helmet. A shape that reads at 16 texels is made
   of few, big value steps - three or four bands, not a gradient per row. Fix it now, not at the end.
5. `armorpieces_skin_material iron`, then `gold`, then `netherite`. Each call returns its own
   screenshot, so this is three calls, not six.
6. `armorpieces_skin_check`, fix what it marks, `armorpieces_save_skin`. Saving also installs the
   pair into the mod's resources and redraws the skin template icons, and returns what both scripts
   said - so do not run `sync_skin_masters.py` or `gen_template_icons.py` yourself.
7. `python tools/check_skin.py <skin>` from the repository root as the independent confirmation, and
   `python tools/bake_skin.py <skin> --out build/skins` to leave the baked pairs for a human to look
   at.
8. `armorpieces_close_skin`.
9. Write what you learned into your brief under `docs/plans/briefs/skins/<skin>.md` - the value
   scale you settled on, what read badly in 3D and why, what the next skin should know - and report:
   what you drew net by net, every `!` you accepted and why, and what is worth changing about the
   tools.

Do not run the game, do not commit, do not touch another skin's files, and do not edit anything
under `src/` - a second session is building the Java half of this feature at the same time.
