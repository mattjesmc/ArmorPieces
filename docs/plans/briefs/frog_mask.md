# Brief: Frog Mask

The second piece of **Armor Pieces: Animals** (`docs/plans/set-packs.md`), after Fox Ears — read
that brief's Lessons section first if it is filled in; it is the first piece in the project that
leaned on the static layer, and whatever it learned applies here.

**Part.** `armorpieces_animals:frog_mask`, socket `brow` only. Display name "Frog Mask".
Fittings: `armorpieces:gemstone`, **one mask covering the two eyes only**. No effects, no loot rows.

Create it with `armorpieces_new`, naming the pack and namespace explicitly or it lands in the mod:

    name: frog_mask
    anchor: brow
    namespace: armorpieces_animals
    datapack: C:\Users\Matthijs\ArmorPieces\packs\animals\datapack
    resourcepack: C:\Users\Matthijs\ArmorPieces\packs\animals\resourcepack

**Shape.** `brow` is **not** mirrored: model both sides. A frog's face, worn as a mask across the
forehead — the game's frog is almost all head, so this is a wide, shallow, friendly shape, not a
snout:

- A face plate across the brow, roughly 10 wide × 4 high × 1 thick, sitting a texel proud of the
  helmet's front plane (the helmet reference is the head box inflated by 1, so its front face is at
  z −5; do not make any face coplanar with it).
- Two eye domes standing **above** the plate's top edge, one either side, about 3 × 3 × 3, their
  inner edges roughly 2 apart. They are the frog: high, round and wide-set. Give each its own bone
  so the pair can be nudged without redoing the plate.
- The mouth is paint, not geometry: a single dark line across the lower third of the plate, turning
  up a texel at each end.
- `brow` is the most crowded socket in the mod — fourteen pieces, including five helms that enclose
  the whole head. The `armorpieces_new` reply lists every one of their envelopes; stay inside the
  span the smaller brow pieces use (circlet, browband, nasal) rather than the great helms', and
  keep the eye domes below the crest parts' floor.

**Sheets.** Three of them, and the split matters:

- `frog_mask.png` — the **master**, greyscale, the form and the silhouette. Its value is a position
  on the *wearer's trim material ramp*, so anything left to it turns iron or gold with the armor.
- `frog_mask_static.png` — RGBA, **keeps its own colour**, shaded by the master's value beneath. The
  frog goes here: every face of the plate and the domes except the eyes themselves.
- `frog_mask_gemstone.png` — greyscale mask, **the eye faces only**. Shaded like the master, never
  flat: a flat mask flattens the form once the fitting is applied. Where the mask is opaque it wins
  over the static layer, so leave the eye pupils as `null` holes in the mask if you want them to
  survive the gem — an opaque mask pixel takes the gem's colour.

The frog's palette, from `python tools/mob_reference.py frog_cold` — **the cold frog, which is the
green one.** 26.2's *temperate* frog is orange and the *warm* one is grey, and a frog that is not
green does not read as a frog.

| hex | share | value | what it is |
|---|---|---|---|
| `#496b1e` | 23.2% | 88 | the deep green — the plate's shaded faces and its edges |
| `#568022` | 15.0% | 105 | the mid green — most of the plate |
| `#63902e` | 12.7% | 119 | the lit green — the tops of the domes |
| `#3a5a19` | 8.7% | 73 | the darkest green — under the jaw, the mouth line's shadow |
| `#bead6a` | 9.7% | 170 | pale gold — the throat, and a rim around each eye |
| `#b19e5f` | 7.1% | 156 | the same gold, shaded |
| `#2e1d10` | 9.2% | 33 | near-black — the mouth line and the pupils |

**Look at the frog once, first**: `tools/.mcassets/reference/entity/frog/frog_cold@8x.png`. The eyes
and the gold throat band are the two things that make it read; the head net is the top-left block.
Picture budget about six, and that look is the cheapest one you will take.

**What the Fox Ears session learned — read this, it will save you a third of the session.**

- **The static layer is created by `armorpieces_set_part {static: true}`.** In that reply,
  `static_created: true` is the line that matters; `sheets_created: []` just means no fitting masks
  were made yet. Set the part data (including the fitting) BEFORE painting: it is what creates the
  mask sheet too.
- **The master and the static layer take the SAME `faces` dict** — same keys, same order — greys in
  one, hex in the other. Write the two calls as a pair and change them as a pair; a face in one and
  not the other gives you a grey face on a coloured mask. The same goes for the gemstone mask over
  the faces it covers. `[top, bottom]` on a 2-row face gives exactly those two values with no blur.
- **The 3D view only ever shows the master**, so the piece renders grey the whole session and you
  cannot see the frog. Judge shape from the viewport, trust the palette for colour, and check the
  static sheet once at the end with a three-line Pillow read: equal opaque-pixel counts on master
  and static, and the colours all from the table above.
- **`python tools/check_part.py <name>` does not work for a piece in this pack** — it only looks in
  the mod's resources and answers "no shipped geometry". The bridge's own check, printed after every
  call, is the check for these pieces; `check_authoring.py` with the two pack folders is the other.
- **Groups cannot be renamed**: `add_group` with the name you want (parent by NAME, `part`), then
  `remove_element` the starter cube and then the starter group. And **a group's origin and rotation
  cannot be changed after it is created**, so compute the pivot and the angles before you make the
  bone — place cubes in the unrotated pose and rotate the bone about its base.
- `minecraft:sweet_berries` is now taken as a recipe centre in this pack.

**Recipe.** Centre item `minecraft:lily_pad` (unused by any template in the mod or this pack), paper
ring, craftable. Result is the `brow` template.

**Done means.** `armorpieces_save` accepted without `force`;
`python tools/check_authoring.py packs/animals/datapack packs/animals/resourcepack` clean (it now
has Fox Ears in it too, so a recipe-grid clash would show here); the Lessons section below filled
in. Do **not** run the modpage build — this pack is not on the mod's page. Do not touch any other
tab.

## Lessons from the session

> **Written on an older bridge.** The tool names below (`remove_element`, `paint_with_brush`, …)
> were the third-party Blockbench plugin's and no longer exist; the toolkit's own bridge replaced
> them with 26 tools behind `op` families (`element`, `texture`, `inspect`). The numbers about
> THIS piece are still true — the technique is not. `docs/plans/briefs/LESSONS.md` is current.

Built in 19 bridge calls, 3 of them paint (master, static, gemstone mask), 3 pictures (the frog
texture once, then a three-quarter and a front render). `armorpieces_save` accepted without
`force`; `check_authoring.py packs/animals/datapack packs/animals/resourcepack` is clean and
`minecraft:lily_pad` collides with nothing.

**A masked fitting over a static layer works, and the recipe is one dict painted three times.**
The master, the static layer and the mask all take the *same* face addresses, so write the master
call, copy it to the static call swapping grey for hex, and then give the mask only the subset of
faces the fitting covers. The end-of-session Pillow read is the proof and it is worth the three
lines: 246 opaque pixels on master and static, seven master values whose counts match the seven
palette colours one for one (33/15, 73/23, 88/118, 105/30, 119/23, 156/16, 170/21), and 0 static
or mask pixels outside the master. The mask sheet is created by `armorpieces_set_part` in the same
call as `static: true` - one call gave `sheets_created: ["part_gemstone"]` and
`static_created: true` together, so there is no reason to set the part data twice.

**Null pupils in the mask.** `pixels` with `value: null` on the mask sheet punches holes the gem
does not fill, and the static layer shows through them - a 1-texel-wide, 2-texel-tall dark bar
down the centre of each 3x2 eye face, painted `#2e1d10` on the static and 33 on the master. The
same trick in reverse gives the highlight: a single 240 texel at the top corner of each eye on the
mask, one column out from the pupil. Both eyes take the highlight at the SAME column index of
their north face, which is the same world side for both cubes, so the light stays consistent.
The one thing this session could not settle is whether the master's value modulates a mask pixel
or is simply replaced by it; the safe assumption is "replaced", but the eye faces were left at the
deep green 88 / `#496b1e` rather than blacked out, so that if the master does modulate, the gem is
not dimmed - and un-gemmed the eyes still read as dark green frog eyes. Confirm it in-game before
another piece paints a mask over a *dark* master.

**Geometry.** `brow` is crowded but the numbers make it easy: the small brow pieces (circlet,
browband, nasal, laurel, bone_mask) live between y 26 and 31.25 in Blockbench, and every crest
part's floor is y 32.0 or higher, so a brow piece that stays under 32 never meets one. Three bones:
`base` at (0, 29.25, -5.75) holding the plate, and `eye_left` / `eye_right` at (-+2.5, 28.75,
-6.25) holding one eye each, all rotation 0. Plate x -5.5..5.5, y 25.25..29.25, z -6.25..-5.25 -
one texel proud of the helmet front at z -5 with its back a quarter clear of it. Each eye is two
cubes: a ball 3 x 2 x 2 at y 28.75..30.75, z -7.25..-5.25, and a cap inset a quarter on every side
at y 30.5..31.75. The step from ball to cap is what makes a box read as a dome from three metres,
and it costs six faces.

**A 10-wide plate at x -+5 is COPLANAR with the helmet's side walls** even though the plate is
entirely in front of the helmet - the check flags the plane, not the overlap. Going *out* to
-+5.5 clears it as well as coming in would, and 11 wide suits a frog better; browband already
reaches x 6.48, so this is not unusually wide for the socket.

**Two notes were accepted, not fixed:** "eye_left's x face at 4 lies on the body surface" and its
mirror. The eye balls' outer faces sit on the plane x = -+4, which is the head box's side, but the
balls span z -7.25..-5.25 and the head box ends at z -4, so the two never overlap and nothing can
z-fight. They are `-` notes, not `!` problems, and the save was clean without `force`.

**The paint reads front-on** and that is the only view that matters for a brow piece: a wide green
plate, a gold throat band along the bottom row, a near-black mouth across the row above it that
steps up one texel onto the dark edge column at each end, and two bulging eyes with a gold rim
(the cap's north/east/west faces, 170 and 156) over a jewelled iris. The mouth is nine texels of
33 plus two turn-ups - eleven `pixels` entries, no geometry.

**For the next Animals piece:** `minecraft:sweet_berries` (Fox Ears) and `minecraft:lily_pad`
(Frog Mask) are taken as recipe centres in this pack. Nothing needed `risky_eval` or `force`.
`tools/check_part.py` still does not see this pack - the bridge's own check and
`check_authoring.py` with the two pack folders are the whole verification, plus the Pillow read.
