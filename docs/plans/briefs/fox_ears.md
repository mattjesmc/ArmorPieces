# Brief: Fox Ears

The first piece of **Armor Pieces: Animals**, a pack that ships outside the mod
(`docs/plans/set-packs.md`). Everything about the bridge is as it was for the last eight parts;
what is new here is that the piece does **not** go in the mod, and that its colour does not come
from the wearer's armor.

**Part.** `armorpieces_animals:fox_ears`, socket `horns` only. Display name "Fox Ears".
**No fittings** — a dyed fox is not a fox. No effects, no loot rows.

Create it with `armorpieces_new` and **name both pack folders and the namespace explicitly**, or it
will be written into the mod:

    name: fox_ears
    anchor: horns
    namespace: armorpieces_animals
    datapack: C:\Users\Matthijs\ArmorPieces\packs\animals\datapack
    resourcepack: C:\Users\Matthijs\ArmorPieces\packs\animals\resourcepack

**Shape.** `horns` is a **mirrored** socket: model ONE ear and the pair is made for you. A fox's ear
is a tall triangle, wide at the base, standing up off the temple with a slight outward cant and a
very slight forward lean — not a horn, not a cone, and not curved. Suggested build, all in
Blockbench coordinates, adjust from what you see:

- A root bone at the temple, the ear's base sitting **half a texel inside the helmet shell** (the
  helmet reference is the head box inflated by 1), so no face is coplanar with the shell.
- Three stacked cubes, or two plus a tip, narrowing as they rise: about 4 wide × 1 thick at the
  base, 3 × 1 in the middle, 2 × 1 at the tip, over roughly 5–6 units of height. One texel thick
  throughout — a fox's ear is a flap, and thickness reads as a horn.
- The inner ear is a recess, not a separate cube: paint it. If you want it to read in silhouette,
  inset the middle cube's front face by a quarter texel rather than adding geometry.
- Rotate the **bone**, never the cubes: perhaps 8–12° of Z to cant the ear outward and 5° of X to
  lean it forward. Keep it under the helm_wings and aerials envelopes — the reply to
  `armorpieces_new` lists every other `horns` part's envelope in both frames, so place against
  those numbers rather than measuring anything yourself.

**Sheets, and this is the part that is different from every part you may have seen before.**

A piece has three layers and they do different jobs:

- `fox_ears.png` — the **master**, greyscale. Its value is a position on the *wearer's trim material
  ramp*, so anything drawn here turns iron, gold or netherite with the armor. Its alpha is the
  silhouette and it is the single source of truth: a static pixel where the master is transparent
  is not drawn.
- `fox_ears_static.png` — **RGBA, keeps its own colour**, shaded by the master's value underneath.

So: **draw the fox in the static layer.** The master carries the same shapes in greyscale at the
values listed below, so the shading agrees with the colour instead of fighting it. There is no
hardware on this piece, so nothing stays metal — the master exists here to give the static layer its
form and its silhouette.

The fox's own palette, read out of the game by `python tools/mob_reference.py fox`
(share = how much of the mob it covers, value = what to paint on the master beneath it):

| hex | share | value | what it is |
|---|---|---|---|
| `#cc6920` | 26.6% | 126 | the orange body — the ear's outer face |
| `#b05122` | 17.8% | 104 | the darker orange — shading, and the ear's edges |
| `#e27c21` | 16.7% | 144 | the lighter orange — the lit top of the ear |
| `#d5b69f` | 10.7% | 189 | the cream muzzle and chest — **the inner ear** |
| `#e7d9d3` | 3.0% | 221 | the palest cream, for one highlight row at most |
| `#06040e` | 4.0% | 6 | near-black — **the ear tips**, two or three rows |

**Look at the fox before you model anything**, once: `tools/.mcassets/reference/entity/fox/fox@8x.png`
(the real texture, eight times, nearest-neighbour). The ears are at the top-left of the head net,
and they show exactly how the game does a dark tip and a cream inner ear in three pixels. That look
is your cheapest picture of the session — take it first, and spend the rest of your picture budget
(about six) on the model.

Three colours do 61% of a fox. If the piece reads orange with a dark tip and a cream inner ear, it
is a fox; if it reads brown, it is a rabbit.

**Recipe.** Centre item `minecraft:sweet_berries` (foxes love them; unused by any template in the
mod or this pack), paper ring, craftable. Result is the `horns` template.

**Done means.** `armorpieces_save` accepted without `force`;
`python tools/check_authoring.py packs/animals/datapack packs/animals/resourcepack` clean; the
lessons paragraph below filled in. Do **not** run the modpage build — this pack is not on the mod's
page. Do not touch any other tab: there is an unrelated `bedroll` open with unsaved edits, and it is
not yours.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built in 14 bridge calls, 4 of them paint, 3 pictures (the fox texture, then two renders). Clean
save without `force`; `check_authoring.py packs/animals/datapack packs/animals/resourcepack` passes.

**The pack folders worked exactly as the brief said.** `armorpieces_new` with `namespace`,
`datapack` and `resourcepack` wrote all six files under `packs/animals/` and nothing into the mod;
the reply lists the three paths it created, so one glance confirms you did not land in
`src/main/resources`. `tools/check_part.py fox_ears` from the repository root does **not** work for
an out-of-pack piece - it only looks in the mod's resources and says "no shipped geometry". The
bridge's own check (printed after every call) is the check for these pieces; run only
`check_authoring.py` with the two pack folders afterwards.

**Two layers, one call each, painted identically.** The master and the static layer take the *same*
`faces` dict - the same keys, the same order - with greys in one and hex in the other, and that is
the whole trick: 72 opaque pixels on each sheet, six values on the master exactly matching the six
colours on the static layer. Write the two calls as a pair and change them as a pair; if a face is
in one and not the other you get a grey face on a coloured ear. `[top, bottom]` pairs on a 2-row
face give exactly the two values (no blur), which is how the black tip stayed crisp. The static
layer needs `armorpieces_set_part {static: true}` first, and `sheets_created: []` in that reply is
normal for a part with no fittings - `static_created: true` is the line that matters.

**The 3D view only ever shows the master,** so the piece renders grey while you work and you cannot
see the fox. Judge shape from the viewport and trust the palette table for colour; the static sheet
is worth one Pillow read at the end (opaque-pixel count equal on both sheets, six colours each).

**Geometry.** The starter bone is called `main` with one cube; since groups cannot be renamed, add
the bone you want (`add_group` name `ear`, parent by NAME `part`) and `remove_element` the cube then
the group - the check clears the starter's COPLANAR line the moment the cube goes. The ear is a flap
one texel thick in **z**, standing in the XY plane, so its `north` face is the inner ear the camera
sees: 4x2, 3x2, 2x1.5 and a 1x1 point, x -5.8..-1.8 down to -4.3..-3.3, y 32.4..38.15, z -1.5..-0.5,
in a bone at (-2.8, 32.4, -1) rotated (-5, 0, 10). Sitting the base at y 32.4 buries it 0.6 inside
the helmet shell (top y 33) and puts the outer corner just past the side wall x -5, which is what
makes it read as growing out of the skull corner. The fourth 1x1 cube is what makes it a fox and not
a bear: a 4-3-2 taper still ends in a flat 2-wide top. Keep the stack outboard - centred on x -3.8
rather than -2.8 - and the crest parts' OVERLAP notes drop from 12 to 4; they are only notes (only
COPLANAR is a problem) but a spire through an ear is real.

**Colour.** Palette straight from the brief, no invention: `*.*` orange, `*.east/west` dark orange
(edges), `*.up` light orange, both `north` faces cream, `ear_tip.*` a `[black, colour]` pair, the
point all black. Two extras earn their keep: six `pixels` for a 1-texel orange rim down the sides of
the lower front face (so the cream reads as an inner ear inside a rim, not as a pale ear), and a
1-texel pale-cream streak up the middle of the recessed mid face. The recess itself is the mid
cube's front inset 0.25 with the tip at full thickness above it, so the inner ear is a pocket walled
on three sides - no extra geometry, and it shows in silhouette from three quarters.

**For the next Animals piece:** `minecraft:sweet_berries` is now taken as a recipe centre in this
pack. Nothing here needed `force`, and nothing needed `risky_eval` - the one thing no tool can do is
change a group's origin or rotation after `add_group`, so compute the pivot and the two angles
before you create the bone (place cubes in the unrotated pose and rotate the bone about the base).
