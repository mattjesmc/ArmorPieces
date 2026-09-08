# Brief: Coral Crown

A piece of **Armor Pieces: Coral**, a pack that ships outside the mod (`docs/plans/set-packs.md`,
"Pack 2"). Read `docs/plans/briefs/axolotl_frills.md`'s **"What is new in the bridge"** section
first — it lists what the toolkit's own Blockbench plugin changed, and its Lessons section says what
actually held when the first piece of this pack was built.

**Part.** `armorpieces_coral:coral_crown`, socket `crest` only. Display name "Coral Crown".
**One fitting**, masked: `armorpieces:guard` — the band the coral grows from, and the only part of
this piece that follows the wearer's armor.

Create it with `armorpieces_new` and **name both pack folders and the namespace explicitly**, or it
will be written into the mod:

    name: coral_crown
    anchor: crest
    namespace: armorpieces_coral
    datapack: C:\Users\Matthijs\ArmorPieces\packs\coral\datapack
    resourcepack: C:\Users\Matthijs\ArmorPieces\packs\coral\resourcepack

Then, before painting anything — this call is what creates the two extra sheets:

    armorpieces_set_part { name: "Coral Crown", static: true,
                           fittings: ["armorpieces:guard"],
                           recipe: { centre: "minecraft:brain_coral_block", craftable: true } }

The reply must say `static_created: true` and `sheets_created: ["part_guard"]`. Fittings are plain
id strings — `["armorpieces:guard"]`, never objects; an object is accepted and then silently makes
no sheet.

## Shape

`crest` is **not** mirrored: it is the ridge along the top of the helm, and you model the whole
thing. This is the pack's showpiece, so it is allowed to be the busiest of the four.

A reef growing out of the crown of a helmet. Not a tiara, not antlers, not a mohawk — three or four
short coral *growths* of different species standing on a low band, at different heights and leaning
different ways, the way coral actually sits on rock.

- A low band bone across the crown, following the helmet shell about half a texel outside it, maybe
  1 tall and 1 thick, spanning the middle of the skull front to back. That band is the **guard**
  fitting: it is metal, it takes the armor's material, and it is what makes the piece look worn
  rather than glued on.
- Three growths on the band, each its own child bone so it can lean:
  - a **horn coral** stalk, front, tallest — a 1×1 column about 4 up with a 2-wide fork at the top;
  - a **fire coral** clump, middle — squat and wide, 2–3 across and 2 up, leaning back;
  - a **tube coral** pair, rear — two thin 1×1 tubes of different heights, close together.
- Nothing should exceed about 6 units above the shell: `spire`, `comb` and `brush_crest` are on this
  socket and the reply to `armorpieces_new` lists their envelopes in both frames. Stay under them.
- Rotate the **bones**, never the cubes, and lean each growth a different way — 10–20° is plenty.
  Coral that all leans the same way reads as a comb.

## Sheets

Three layers, all three used here:

- `coral_crown.png` — the **master**, greyscale, its value a position on the wearer's trim ramp.
  Alpha is the silhouette and the single source of truth.
- `coral_crown_static.png` — **RGBA, keeps its own colour**. Every coral face goes here.
- `coral_crown_guard.png` — the **mask**, greyscale. Wherever it is opaque the `guard` fitting's
  colour is used instead. Paint **only the band's faces** here, and leave the growths transparent —
  a mask over the coral would turn the reef into copper.

The three-layer rule that this pack is built on: colour lives in the static layer, the master carries
the same shapes in the greys below so shading and colour agree, and the mask is *hardware only*.

Palettes, from `python tools/mob_reference.py horn_coral fire_coral tube_coral`:

| coral | hex | value | what it is |
|---|---|---|---|
| horn | `#e4da4a` | 205 | the lit tip |
| horn | `#d5cb3e` | 190 | the pale yellow body |
| horn | `#d1b341` | 175 | the ochre body |
| horn | `#b68930` | 140 | the shaded underside |
| fire | `#e23f36` | 111 | the lit edge |
| fire | `#c62a37` | 90 | the red body |
| fire | `#a4222f` | 74 | the shaded body |
| fire | `#791a26` | 56 | the deep red root |
| tube | `#3f6ce5` | 108 | the lit blue |
| tube | `#405ce2` | 99 | the blue body |
| tube | `#314fdd` | 86 | the shaded blue |
| tube | `#1c3788` | 56 | the dark root |

Every static pixel must come from one of those twelve. Three species is what makes it a reef rather
than "a yellow thing"; keep each growth to its own four and do not blend between them.

Take one look at the reference before modelling —
`python tools/mob_reference.py horn_coral fire_coral tube_coral --extract` puts the three under
`tools/.mcassets/reference/block/`. They are 16×16 and they show how the game builds a branch out of
two values and an edge.

## Recipe

Centre item `minecraft:brain_coral_block` — unused by any template in the mod or in either pack.
Paper ring, craftable. The result is the `crest` template. (Brain coral is not one of the three
species drawn; it is the item that most reads as "coral" in a recipe book, which is the job the
centre does.)

## Done means

`armorpieces_save` accepted **without** `force`;
`python tools/check_authoring.py packs/coral/datapack packs/coral/resourcepack` clean; the Lessons
section below filled in. Do **not** run the modpage build — this pack is not on the mod's page.
`tools/check_part.py` does not work for an out-of-pack piece; the bridge's own check, printed after
every call, is the check for these.

One extra check this piece owes, because it is the pack's first masked fitting: the mask must be
opaque **only** over the band's faces. `armorpieces_check` reports paint outside every face, but it
cannot know that a mask pixel over a coral face is wrong — read the guard sheet back with
`texture op:read` before saving and confirm the coral is transparent there.

## Lessons from the session

Built as: one `base` bone at the crest anchor (renamed from the starter `main`), holding the
`band` cube (the `guard` fitting) 1×1×7, x -0.5..0.5, y 33.5..34.5, z -3.5..3.5, sitting a half
unit above the flat top of the inflate-1 helmet shell (y=33) so it never shares a plane with it.
Three child bones off `base` — `horn_coral` (front, z=-2.5), `fire_coral` (middle, z=0),
`tube_coral` (rear, z=2.5) — each built straight/upright first (root+mid+two fork tips for horn
coral, two stacked cubes for fire coral, two adjacent columns of different height for tube
coral), then leaned by setting the bone's own rotation after the fact: horn coral -14° about Z,
fire coral -18° about X (leans it toward +Z, i.e. backward, matching the brief), tube coral +10°
about Z — three different axes/directions so the reef doesn't read as a single comb. Apex came
out at +6.01 units past the helmet shell, 0.01 over the brief's "about 6" — accepted as
negligible and clearly a soft guideline, not re-measured further. `armorpieces_set_part` before
any painting created `part_static` and `part_guard` as promised (`static_created: true`,
`sheets_created: ["part_guard"]`). Painted the master in the exact twelve greys from the brief's
table (one four-value ramp per species, tip/lit face brightest, down/root darkest), the static
layer in the matching twelve hexes on the identical face selectors, and the guard mask only on
the six `band.*` faces (200 body / 220 up / 170 down) — confirmed by `texture op:read
part_guard.png`, which showed opaque pixels only in the band's own UV rectangle (rows 0-7,
columns 7..22) and nothing at all under any coral cube's UV region. Saved clean without `force`
on the first attempt; `check_authoring.py` on both pack folders passed (roundtrip, data, recipe,
reach) for both pieces in the pack.

Notes for the next piece of this pack:
- **The texture id in `texture op:read`/`get_texture` is not the sheet id from
  `armorpieces_paint`.** `armorpieces_paint {sheet: "part_guard"}` is correct and is what the
  bridge documents throughout — but the underlying mcptoolkit `texture` tool only knows the file
  names Blockbench actually loaded, which for this piece were `part`, `coral_crown_static.png`
  and `coral_crown_guard.png` (`get_project_info`/error message names them; `part_guard` itself
  came back "no texture"). When the brief's own "read the mask back" check is needed, ask for the
  piece-named file, not the `part_<fitting>` alias.
- No pixel-level fringe or brush work was needed here (unlike axolotl_frills' filament dots) —
  the coral's species read comes entirely from the four-value ramp per growth plus the geometry
  (fork, squat clump, paired tubes), which was enough without extra highlight pixels. Painting the
  mask was three whole-face `armorpieces_paint` calls on the band alone, one per shading value.
- The three same-socket `crest` parts already on this bone (`spire`, `comb`, `brush_crest`) never
  factor into the check (never worn together), so the only real constraint besides the "~6 units"
  guidance was the `other sockets on the bone, worn together` list (`horns`/`brow` parts) — this
  piece's envelope (x -2.03..1.25, y -15.01..-9.50, z -3.50..3.50 bone-local) came back "all clear
  by more than half a unit" against every one of them without any adjustment needed, so a crest
  piece kept tight to the top of the skull (z within the head box, not swept far forward or back)
  is unlikely to clash with anything on `brow` or `horns`.
