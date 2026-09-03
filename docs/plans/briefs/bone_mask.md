# Brief: Bone Mask

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the third
batch of four (skim the lessons in nasal.md for the brow socket and aerials.md for the head
frame and the two workspace-killing traps). From the `brow` row of
`docs/plans/part-variety.md`:

> **Bone Mask** - A jawless skull-front covering the upper face, eye sockets dark. Theme: Beast.
> Fitting: `gemstone` (the eyes).

**Part.** `armorpieces:bone_mask`, socket `brow` only, in the mod's own pack. Display name
"Bone Mask". Fittings: `armorpieces:gemstone`, one mask, covering the two eye stones only. The
bone itself keeps real colour through a static layer (`static: true`): an off-white bone that
does not take the trim material, with the metal fittings around the eyes on the master. No
effects, no loot.

**Shape.** `brow` is not a mirrored socket: model the whole thing, centred on x = 0, on the head
bone. The head box is x -4..4, y 24..32, z -4..4 (pivot 0, 24, 0); the helmet shell is that box
inflated a full unit, so its front plane is z -5, and the anchor is at Blockbench (0, 28, -4) on
the face. Anything with z above -5 is buried; sit faces a tenth off a shell plane. Read the
envelopes in the `armorpieces_new` reply: the crest and horns parts on the same bone all live
above y 31 or outboard of x 5 (aerials' boss at x -5.5..-4.5, y 31..32.5), so a mask on the
face is clear of them; the other brow parts (circlet, coronet, nasal, visor) are never compared
but give the depth gauge (visor reaches z -7.76, nasal -5.75). Build: a `mask` bone with the
face plate x -4.1..4.1, y 26.5..31.25, z -5.6..-5.1, half a unit thick, spanning the upper face
from the cheekbones to the brow; two `eye_l` / `eye_r` bones each with a 1.5x1.5 socket recess
cube standing 0.15 proud of the plate (x -2.9..-1.4 and 1.4..2.9, y 28..29.5, z -5.75..-5.5) that
will be painted near-black on the static layer to read as hollow, and inside each a 0.75x0.75
stone standing a further quarter proud (z -6.0..-5.75) - the gemstone; a `nose` bone with a
0.75-wide bridge 0.5 proud running from between the eyes down to the plate's bottom edge
(x -0.4..0.4, y 26.5..28.25, z -6.1..-5.6); and two `cheek_l` / `cheek_r` bones with a small
zygomatic ridge each, 1.75 long along x under the eye, 0.5 tall, 0.25 proud (y 27..27.5,
z -5.85..-5.6, x -4.0..-2.25 and 2.25..4.0). Nothing wider than x ±4.25 and nothing above
y 31.5. Whether the plate's top corners should be cut back to a brow curve is your call - two
more thin cubes, or leave it square.

**Sheets.** Master: everything a mid grey except the eye stones (bright `[top, bottom]`, dark
underside) and the rim of each eye socket, a single lighter texel ring (`pixels`), which is the
metal setting. Static layer (`part_static`, real colour): the plate, nose and cheeks bone white
`[#e9e2cf, #cfc4a8]` top to bottom with a darker tone under the cheek ridges, the eye recess
faces near-black `#1a1612`, one crack of two or three darker texels down from one eye. Static
pixels override the master where they exist, so leave the stones off the static layer.
Gemstone mask: the two stones' faces only.

**Recipe.** Centre item `minecraft:bone_meal` (a flat item, unused by any template - `bone` is
taken), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py
bone_mask` and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons
paragraph below filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

Built 2026-09-03 in 25 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`armorpieces_part`, 1 `list_outline`, 5 `add_group`, 6 `place_cube`, 2 `remove_element` (starter
cube, then its `main` bone), 1 `armorpieces_check`, 1 `armorpieces_set_part`, **3
`armorpieces_paint`** (one per sheet), 2 `set_camera_angle`, 1 `armorpieces_save`. No
`risky_eval`, no `modify_cube`, no nudging, nothing hand-edited, and the save went through first
time **without `force`**.

**What I built.** Nine cubes in six bones, all unrotated (a skull front needs no chain): `mask`
(pivot at the anchor 0, 28, -4) with `plate` x -4.1..4.1, y 26.5..**30.25**, z -5.6..-5.1 and
`brow` x -3.3..3.3, y 30.25..31.25, z **-5.75**..-5.1; `eye_l`/`eye_r` each with a `socket_*`
bezel x ±1.4..±2.9, y 28..29.5, z -5.75..-5.5 and a `stone_*` x 0.75 square at z -6.0..-5.75;
`nose` with `bridge` x -0.4..0.4, y 26.5..28.25, z -6.1..-5.5; `cheek_l`/`cheek_r` with
`zygo_*` x ±2.25..±4.0, y 27..27.5, z -5.85..-5.5. Envelope x ±4.10, y 26.50..31.25 (bone-local
-7.25..-2.50), z -6.10..-5.10 - a full unit shallower than `visor` and 0.35 deeper than `nasal`,
so it reads as its own depth band on the socket.

**I took the brow-curve option, with one cube instead of two.** The brief left the top corners
to me: shortening the plate to y 30.25 and stacking a narrower `brow` (6.6 wide instead of 8.2,
and 0.15 proud) cuts both top corners in one cube and gives the skull a browridge that catches
the light - two thin corner cubes would have added four more faces for the same silhouette. The
step is legible at three metres in the screenshot; the plate's own top row still shows either
side of it.

**One deviation from the brief's numbers, on purpose.** The nose and cheeks are given back faces
at z -5.5 rather than the brief's -5.6, i.e. 0.1 **inside** the plate instead of exactly on its
front plane. The check does not flag coplanar faces between two cubes of the same part, but a
back face sitting exactly on the plate's front face is the classic z-fight; the eye bezels
already sat at -5.5 in the brief, so this only makes the other proud cubes consistent with them.
Nothing about the front silhouette changes.

**`!` lines accepted: none.** The finished check reports zero problems. Two `-` notes stand and
are correct as built: *`cheek_l`'s x face at 4* and *`cheek_r`'s x face at -4 lie on the body
surface* - the head box is x ±4, so the cheek ridges' outer faces share that plane. They cannot
z-fight, because the whole ridge lives at z -5.85..-5.5, a full 1.5 units in front of the head
box (whose front is z -4) and 0.5 in front of the helmet shell at z -5: the head's side face
does not exist at that depth. Keeping the brief's 1.75-unit ridge was worth the note; trimming
to x ±3.95 would have bought silence and nothing else. The clash lines are silent -
*"all clear by more than half a unit"* from all eleven other-socket parts on the head, because
everything on `crest` is above y 32 or inboard behind z -1, and everything on `horns` is
outboard of x 4.66 (`head_fins`) / 4.50 (`aerials`) while the mask stops at 4.10.

**Three paint calls, and they covered everything.** Master (54 faces + 12 pixels): `*.*` 140,
then per-face pairs on the bone shapes (plate north [190,120], up 200, down 80; brow north
[215,165], up 228, down 100 as the shadow it throws over the eyes; bridge, zygo the same idea),
the bezels dark (95 on their north face) with **bright sides** - up 205, east/west 185 - and the
stones 210..255 with a 120 underside. The static layer (34 faces + 3 pixels) puts the bone white
[#e9e2cf, #cfc4a8] on plate/brow/nose/cheeks, #9d9279 under the cheek ridges, #1a1612 on the two
bezels' north faces, and a three-texel crack (20,3) (20,4) (19,4) below the left eye. The
gemstone mask is the twelve stone faces only, shaded to the master's values (a flat mask would
kill the lit top texel when a gemstone is fitted, as knee_studs and talons found).

What the painter did **not** cover: the brief's "single lighter texel ring" around each eye is
not paintable as a ring. A 1.5-unit face is **2x2 texels**, so its perimeter is the whole face,
and the static's near-black recess would have eaten it anyway. The metal setting instead lives on
the bezel cube's four side faces (1 texel wide each), which the static deliberately leaves
unpainted so the master - and therefore the trim material - shows there; the `pixels` list then
brightens the top edge (235) and tapers the two side edges (215 -> 195), which is what actually
reads as a ring in the render. Same lesson as before about `[top, bottom]`: on the 1-texel-tall
brow, zygo and stone faces a pair collapses to its top value, so the vertical story is carried by
the per-cube step, and only the 4-row plate and the 2-row bridge take a real gradient.

**Bridge behaviour that has changed since nasal.** `armorpieces_set_part` now does everything
nasal had to do by hand: `fittings: ["armorpieces:gemstone"]` created `part_gemstone`,
`static: true` created `part_static`, and `recipe: {centre: "minecraft:bone_meal"}` wrote
`template_bone_mask.json` - the reply lists `sheets_created` and `static_created`, no file
copying, no reopen with `reload`, and the save reported *"installed 3 file(s)"* into the
resources with the masters already in `tools/decoration_masters/`. Do the `set_part` **before**
painting so both extra sheets exist for the paint calls.

**For the next part.** `minecraft:bone_meal` is now taken as a template centre (`bone` was
already `antlers`'s); one `python -m modpage build --offline` warned it had never been cached,
one plain `python -m modpage build` fetched it, and the third build was clean and `unchanged` -
the same three-step dance as the last six sessions. The Blockbench 3D view draws the **master
only**, so a static-coloured part looks grey in every screenshot: judge the silhouette and the
shading from it, and verify the colours with Pillow on the saved `_static.png` (this one: 174
opaque texels, 27 colours; master 202 texels, 75..255, greyscale confirmed). On `brow`, the face
between the helmet shell (z -5) and `visor`'s -7.76 is empty in every direction: a mask can be
0.6 to 1.1 units thick there without touching anything, and the only real constraint is x ±4.5,
where `head_fins` and `aerials` start.

