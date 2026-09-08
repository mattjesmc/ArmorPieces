# Brief: Turtle Shell

The fourth piece of **Armor Pieces: Animals** (`docs/plans/set-packs.md`), after Fox Ears, Frog Mask
and Bee Wings. Read their Lessons sections first — three sessions of accumulated bridge knowledge
sits there, and the summary below is only the short form.

**Part.** `armorpieces_animals:turtle_shell`, socket `back` only. Display name "Turtle Shell".
Fittings: `armorpieces:guard`, **one mask covering the rim and the straps only** — never the scutes.
No effects, no loot rows.

    name: turtle_shell
    anchor: back
    namespace: armorpieces_animals
    datapack: C:\Users\Matthijs\ArmorPieces\packs\animals\datapack
    resourcepack: C:\Users\Matthijs\ArmorPieces\packs\animals\resourcepack

**Shape.** `back` is **not** mirrored: model the whole thing. A turtle's carapace worn over the
shoulder blades — low, wide, domed, and unmistakably a shell rather than a plate:

- The dome is a stack of two or three slabs, each smaller and further out than the one below, so the
  profile steps up from the chestplate: perhaps 11 × 7 × 1 against the shell, then 9 × 5 × 1, then
  7 × 3 × 1. The step is what makes a box read as a dome from three metres — the Frog Mask session
  found the same thing with its eyes, and it costs six faces.
- A **rim** all round the bottom slab, standing a quarter texel proud of it: this is the hardware
  the guard fitting colours, and it is what stops the piece reading as a lump.
- Two short straps over the shoulders from the top slab, one either side, a texel wide. Also
  hardware, also on the master.
- The scutes are **paint, not geometry** — hexagonal panels drawn on the dome's up and back faces
  with darker seams between them. Do not model them.
- `back` already carries carapace, cloak, quiver, banner, bedroll, pinions, spine_ridge and
  wing_roots; the `armorpieces_new` reply lists every envelope. `carapace` is the nearest neighbour
  in spirit, so read its numbers and make sure this reads as a different thing: a turtle's shell is
  wider, lower and smoother than a chitin back. Keep clear of the pauldrons' arm boxes — Bee Wings
  is now on that bone.

**Sheets.** Three:

- `turtle_shell.png` — master, greyscale, form and silhouette. The **rim and the straps** live here
  alone and take the wearer's material.
- `turtle_shell_static.png` — RGBA, the shell itself: the scutes and their seams.
- `turtle_shell_guard.png` — greyscale mask, **the rim's and the straps' faces only**, shaded like
  the master.

The turtle's palette, from `python tools/mob_reference.py turtle`. Note the two families: the
**shell is olive-tan**, the **skin is green**, and mixing them up gives you a frog on someone's back.

| hex | share | value | what it is |
|---|---|---|---|
| `#948b63` | 19.9% | 137 | the shell's olive-tan — most of the dome |
| `#a89a73` | 12.9% | 154 | the lit tan — the top slab |
| `#828854` | 9.5% | 128 | the shaded olive — the seams between scutes |
| `#c2b780` | 8.3% | 180 | the pale tan — one highlight row on the crown |
| `#cad091` | 8.3% | 199 | the palest, for the rim's inner edge if you want it to catch light |
| `#3fa442` | 8.0% | 123 | the skin green — a band under the rim only |
| `#30723f` | 7.1% | 88 | the dark green — the shadow beneath the shell |
| `#256433` | 4.6% | 76 | darker still, the deepest seam |

**Look at the turtle once, first**: `tools/.mcassets/reference/entity/turtle/turtle@8x.png`. Its
texture is 128×64, twice the usual, and the carapace is the big tan block — look at how few colours
the seams take. Picture budget about six.

**Read this first: the active-tab hazard, which cost the last session real damage.**

`armorpieces_new` returns the new piece, and its check names the new piece, **while the editor's
active tab can still be the previous one**. The Bee Wings session's first two `add_group` calls
landed in `fox_ears`, two pieces back, and one of those strays reached disk and had to be repaired
by hand.

- **After `armorpieces_new`, call `get_project_info` and confirm the name before your first edit.**
  One cheap call. If it names the wrong piece, `armorpieces_open <your piece>` and check again.
- If you do land an edit in the wrong piece, the repair is
  `armorpieces_open <the damaged piece> {discard: true, reload: true}` — it rebuilds from disk and
  drops the stray. **Do not use `undo`**: undo acts on whatever tab is active and will take apart
  something you did not do.
- The check block appended to every mcptoolkit reply **names the piece it is describing**. Read that
  name, not just the numbers; it is the thing that catches this.
- **Close your tab at the end** (`armorpieces_close`), so the next session has no stale target.

**The short form of three sessions' lessons.**

- One `armorpieces_set_part` call creates the static layer *and* the mask sheet: pass the fitting and
  `static: true` together, before painting. `static_created: true` and `sheets_created: [...]` in the
  reply are the lines that matter.
- Master, static and mask take the **same `faces` dict** — same keys, same order, greys in two of
  them and hex in the static. Write them as a set; a face in one and not the others gives a grey
  face on a coloured shell. `[top, bottom]` gives exactly those two values with no blur.
- An opaque mask pixel wins over the static layer; `pixels` with `value: null` punches a hole the
  fitting does not fill, and the static shows through it.
- **The 3D view only ever shows the master.** The piece renders grey all session; judge shape in the
  viewport, trust the palette for colour, and prove the sheets with a Pillow read at the end: equal
  opaque counts on master and static, each master value's count matching its palette colour's count,
  and zero static or mask pixels outside the master.
- The COPLANAR check flags the **plane**, not the overlap — moving a face outward clears it as well
  as moving it in. `-` notes are not `!` problems and do not need `force`.
- Groups cannot be renamed and a group's origin and rotation cannot be changed after `add_group`, so
  compute the pivot and the angles first and place cubes in the unrotated pose. Never name a bone
  `root`. `add_group` parents by NAME.
- `python tools/check_part.py` does not see this pack. The bridge's check plus
  `check_authoring.py` with the two pack folders is the whole verification.
- Recipe centres already taken in this pack: `minecraft:sweet_berries`, `minecraft:lily_pad`,
  `minecraft:honeycomb`.

**Recipe.** Centre item `minecraft:turtle_helmet` (unused by any template in the mod or this pack —
`minecraft:turtle_scute` is already taken by a mod piece), paper ring, craftable. Result is the
`back` template.

**Done means.** `armorpieces_save` accepted without `force`;
`python tools/check_authoring.py packs/animals/datapack packs/animals/resourcepack` clean; the
Lessons section below filled in. No modpage build. Do not touch any other tab.

## Lessons from the session

Built in 18 bridge calls, 3 of them paint (master, static, guard mask), 4 pictures (the turtle
texture once, then three renders: three-quarter high, straight from behind, and low from the left).
`armorpieces_save` accepted **without `force`** - the check ended on "ok: nothing needs a decision" -
and `check_authoring.py packs/animals/datapack packs/animals/resourcepack` is clean;
`minecraft:turtle_helmet` collides with nothing (it appears only in the mod's
`reforging_materials` tag, which is not a template centre).

**The active-tab hazard did not bite, because of the one cheap call.** `armorpieces_new` returned
`turtle_shell`, and `get_project_info` immediately after named `turtle_shell` too - the drift the
Bee Wings session hit did not happen this time (the previous active tab was `bee_wings`, saved and
quiet). Spend the call anyway: it costs nothing and it is the only thing between you and editing
somebody else's piece. Every mcptoolkit reply's check line started `[armorpieces] turtle_shell`,
which was checked on each of the first few edits. Nothing needed `undo` all session - when a cube
was wrong it was fixed with `modify_cube`, which is safe where `undo` is not.

**Geometry: 3 bones, 9 cubes.** `base` at (0, 19.75, 3.1) rotation 0 holds seven cubes; `strap_left`
at (-3.8, 22.4, 3.6) rotated (0, 0, 30) and `strap_right` at (3.8, 22.4, 3.6) rotated (0, 0, -30)
hold one cube each. The dome is the brief's three slabs, each 0.25 into the one below so no two of
my own cubes share a plane: shell_a x -5.45..5.45, y 16.25..23.25, z 3.10..4.10; shell_b x
-4.45..4.45, y 17.25..22.25, z 3.85..4.85; shell_c x -3.5..3.5, y 18.25..21.25, z 4.60..5.60. The
rim is four cubes 0.75 thick standing proud to z 4.35 (0.25 past shell_a): two side bars x
5.25..6.0 spanning y 16.25..23.25, and top/bottom bars y 23.0..23.75 and 15.75..16.5. The side bars
overlap the horizontal bars by 0.25 in y so that no two rim faces coincide - butting them exactly
would put two up-faces on the same plane, which the check does not flag (it only compares against
other parts and the shells) but which is still two faces in one place.

**Two starting numbers had to move, and both were told to me by the check, not by judgement.**
`x = ±5.5` is `scarf:collar`'s wrap plane - a full-width back piece hits it, so shell_a went to
±5.45 and the two COPLANAR problems vanished. `x = ±4.5` is the leggings surface, so shell_b went to
±4.45; that one was only a `-` note (shell_b lives at z 3.85..4.85, a unit and a half behind the
leggings) but it costs one `modify_cube` and 0.05 of nothing to make the report quiet. **Neither
change altered a single UV texel**: 10.9 and 8.9 still lay out as 11 and 9, so this trimming is
free even after the sheets are painted.

**Chamfering the rim is what stops a back piece reading as a briefcase.** The first render showed a
perfect 12 x 8 rectangle with a lip - a suitcase, not a shell. Shortening only the top and bottom
rim bars from x ±6.0 to ±5.3 (the side bars still reach ±6.0 over the middle 7 units) cuts the four
corners and the outline becomes an octagon; from three metres that is the difference between a
plate and a carapace. Two `modify_cube` calls, and **the paint moved with the resize with no
unpainted faces** even though those faces went from 12 texels to 11 - resizing after painting is
safe here, and the reply's sheet-layout block confirms the new rectangles.

**Painting a panelled surface without modelling it.** The thing to understand first is that a
stepped dome hides most of its own paint: shell_a's 11x7 south face is visible only as a 1-texel
ring (shell_b covers the rest), shell_b's 9x5 the same, and only shell_c's 7x3 is fully in view. So
the scutes are one central hexagon on shell_c plus seam ticks on the two rings, and the ticks have
to line up across the steps or the eye reads noise. The columns map by world x: shell_a texel k
spans -5.45+0.99k, shell_b texel j spans -4.45+0.99j, shell_c texel c spans -3.5+c, which puts the
same world seam at shell_a x+3 = shell_b x+2 = shell_c - i.e. the seams at world x = -2.5 and +1.5
are sheet columns 40/44 on shell_a, 37/41 on shell_b, 58/62 on shell_c, and the same two seams
continue onto the three `up` faces at 28/32, 27/31 and 50/54. The centre hexagon is 3 texels wide on
the outer rows and 5 on the middle row (154 / `#a89a73` on a 137 / `#948b63` field, seams 128 /
`#828854`, and 76 / `#256433` at the two points where three scutes meet). That is 21 texels of
hexagon and 24 of seam tick, and it reads. **Do not shade a face taller than two rows with a
`[top, bottom]` pair** - it interpolates, and an interpolated middle row is in no palette entry and
breaks the end-of-session count proof. Everything here is flat face fills plus 59 explicit pixels.

**The palette's two families, used as the brief split them.** Tan for the shell (137 field, 154 lit
scute and up faces, 180 as the single crown row on shell_c's `up`, 199 as a lit inner-edge row just
under the top rim, 128 seams, 76 deep seams); green only twice - `#3fa442` as the 11-texel band
along the bottom row of shell_a's south face, which is the strip of skin the rim frames, and
`#30723f` on the three `down` faces as the shadow under each step. Nothing was invented.

**The rim and the straps are hardware and exist on two sheets only.** They are painted on the master
(215 up / 200 south / 175 sides / 160 north / 140 down for the rim; 165 / 150 / 135 / 130 / 120 for
the straps) and on `part_guard` with the *same* values, and are **absent from `part_static`**, which
is what makes them take the wearer's material. Pick hardware greys that are not palette values
(none of 76/88/123/128/137/154/180/199) or the arithmetic proof below stops working.

**The Pillow proof came out exact and is worth copying.** master 638 opaque = static 370 + guard
268, a perfect partition (no face on both); every static colour's count equals its master value's
count, one for one - `#256433`/76: 2, `#30723f`/88: 27, `#3fa442`/123: 11, `#828854`/128: 201,
`#948b63`/137: 90, `#a89a73`/154: 27, `#c2b780`/180: 5, `#cad091`/199: 7; the ten remaining master
values are the guard's ten values with identical counts; 0 non-grey pixels on the two greyscale
sheets and 0 static or mask pixels outside the master.

**Notes accepted, not fixed** (all `-`, the save was clean): six OVERLAP hull notes into
`scarf:collar`'s wrap and one into `sash:belt`'s belt - the scarf reaches z 3.55 and any back piece
sitting the regulation 0.1 off the chestplate shell (z 3.1, as `carapace` and `cloak` also do) shares
that half-unit of depth with it, and moving out to z 3.6 would leave the shell floating; and nine
`near:` lines, the tightest being the straps clearing the scarf by 0.05 in z and the ruff by 0.25 in
y, which is the price of straps that actually go over the shoulder.

**Straps on `back` must stay behind z = 3.** The arm shells are x ±3..±9, y 11..25, z -3..3, so a
strap that keeps z ≥ 3.1 can cross the shoulder line at x ±5 without touching them; leaning it
*forward* over the shoulder (z < 3) is what would collide. Rotating a 1-wide bar 30° about Z from a
pivot on the shell (the tip lands at x -3.8 - 2.6·sin30 = -5.1, y 22.4 + 2.6·cos30 = 24.65) puts the
end exactly on the top of the shoulder, and that reads as a strap from every angle tried.

**For the next Animals piece:** `minecraft:sweet_berries` (Fox Ears), `minecraft:lily_pad` (Frog
Mask), `minecraft:honeycomb` (Bee Wings) and now `minecraft:turtle_helmet` (Turtle Shell) are taken
as recipe centres in this pack. Nothing needed `risky_eval` or `force`. `tools/check_part.py` still
does not see this pack; the bridge's own check, `check_authoring.py` with the two pack folders, and
the Pillow read are the whole verification. Close your tab at the end - this session's did, so the
next one starts with no stale target.
