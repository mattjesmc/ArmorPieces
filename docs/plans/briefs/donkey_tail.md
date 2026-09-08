# Brief: Donkey Tail

The sixth piece of **Armor Pieces: Animals** (`docs/plans/set-packs.md`). The first piece in this
pack to hang off the belt, which brings one trap no check will tell you about — read the Geometry
warning below before you place anything.

**Part.** `armorpieces_animals:donkey_tail`, socket `belt` only. Display name "Donkey Tail".
Fittings: `armorpieces:guard`, **one mask covering the ferrule only** — the metal band where the
tail is fixed to the belt. No effects, no loot rows.

    name: donkey_tail
    anchor: belt
    namespace: armorpieces_animals
    datapack: C:\Users\Matthijs\ArmorPieces\packs\animals\datapack
    resourcepack: C:\Users\Matthijs\ArmorPieces\packs\animals\resourcepack

**Shape.** `belt` is **not** mirrored: model the whole thing, at the **back**. A donkey's tail is a
thin, almost bare rope of a tail with a heavy tuft at the end — that silhouette is the whole piece,
and it is what tells it apart from `horsetail`, which is a plume on the crest:

- A **ferrule** at the belt line, centred at the back: a small band about 3 wide × 2 high × 2 deep
  clasping the top of the tail. This is the hardware, and the only thing on the master.
- The tail itself: three or four cubes in a bone chain, each about 1.5 × 3 × 1.5, hanging down and
  angling slightly back and then forward again so it reads as hanging under its own weight rather
  than as a stick. Rotate each bone a little more than the last (perhaps 5°, 10°, 8° of X), and
  remember cubes never rotate — bones do.
- A **tuft** at the end: two or three cubes 2.5–3 wide × 3 high × 2 deep, wider than the tail, with
  the bottom one narrowing again to a point. The tuft is half the length of the whole piece.
- Length: end it around the middle of the thigh. Past the knee it fights the `knees` parts and the
  walk cycle.

**The trap: the player's arm box.** The arms hang at **x ±4..±8, y 12..24, z −2..2**, and they are on
the *arm* bone — so `check_part` never mentions them and a hip hanger placed there simply vanishes
inside an arm. `pouch_belt` lost two cubes that way. Your tail is at the **back** (positive z, behind
the body), which is clear of the arms, so keep it there: do not let the ferrule or the tuft wander
out to x ±4 at z between −2 and 2. Also keep clear of the `back` parts hanging low — `bedroll` and
`quiver` both reach down behind, and `turtle_shell` is now on that socket; the `armorpieces_new`
reply lists every envelope, in both frames.

**Sheets.** Three:

- `donkey_tail.png` — master, greyscale, form and silhouette. The **ferrule** is the only hardware.
- `donkey_tail_static.png` — RGBA, the tail's hair.
- `donkey_tail_guard.png` — greyscale mask, **the ferrule's faces only**.

The donkey's palette, from `python tools/mob_reference.py donkey`. It is a grey-brown animal with a
near-black mane and tail, so the tail's own colours are the dark end of this list — use the mid
greys only where the light catches it:

| hex | share | value | what it is |
|---|---|---|---|
| `#161616` | 5.8% | 22 | the near-black of the tail and mane — most of the tuft |
| `#2a251d` | 3.0% | 38 | the brown-black — the tail's shaded side |
| `#52463a` | 6.1% | 72 | the dark grey-brown — the rope of the tail |
| `#5a4e43` | 9.5% | 80 | a shade up, for the lit side of the rope |
| `#655749` | 9.2% | 90 | the mid grey-brown |
| `#6f6053` | 11.7% | 99 | the coat colour, where the tail meets the belt |
| `#806e5e` | 14.2% | 114 | the lit coat, one or two rows at most |
| `#b2ab9f` | 4.9% | 172 | the pale muzzle grey — a single highlight on the tuft's top |

**Look at the donkey once, first**: `tools/.mcassets/reference/entity/horse/donkey@8x.png`. The tail
is the narrow strip on the right of the net, and the mane shows how the game does coarse hair in
three values. Picture budget about six.

**The active-tab hazard — the one thing that has damaged a piece in this pack.**

- **After `armorpieces_new`, call `get_project_info` and confirm the name before your first edit.**
- Every mcptoolkit reply's check line begins `[armorpieces] <piece>` — read that name.
- If you land an edit in the wrong piece:
  `armorpieces_open <the damaged piece> {discard: true, reload: true}`. **Never `undo`** — it acts on
  whatever tab is active. `modify_cube` is safe where `undo` is not.
- **Close your tab at the end** with `armorpieces_close`.

**The short form of five sessions' lessons.**

- One `armorpieces_set_part` call creates the static layer *and* the mask sheet: pass the fitting and
  `static: true` together, before painting.
- Master, static and mask take the **same `faces` dict** — same keys, same order. An opaque mask
  pixel wins over the static layer; `pixels` with `value: null` punches a hole the fitting leaves.
- **Do not shade a face taller than two rows with a `[top, bottom]` pair** — it interpolates, and the
  interpolated row belongs to no palette entry, which breaks the end-of-session count proof. Flat
  fills plus explicit `pixels`.
- **Resizing a cube after painting is safe** — the paint moves with it, and the reply's sheet-layout
  block confirms the new rectangles.
- **The 3D view only ever shows the master.** Prove the sheets with a Pillow read at the end: equal
  opaque counts on master and static, each master value's count matching its palette colour's count,
  zero static or mask pixels outside the master.
- The COPLANAR check flags the **plane**, not the overlap; a trim of 0.05 clears it and costs no UV
  texel. `-` notes are not `!` problems.
- Groups cannot be renamed; a group's origin and rotation cannot be changed after `add_group`.
  Compute pivots and angles first, place cubes unrotated, rotate the bone. Never name a bone `root`.
- **Silhouette is what sells it** — the turtle read as a briefcase until its corners were chamfered.
  Take one render and ask what the outline says before painting. For this piece the outline is
  everything: thin rope, heavy tuft.
- `python tools/check_part.py` does not see this pack.
- Recipe centres taken in this pack: `minecraft:sweet_berries`, `minecraft:lily_pad`,
  `minecraft:honeycomb`, `minecraft:turtle_helmet`, `minecraft:poppy`.

**Recipe.** Centre item `minecraft:lead` (unused by any template in the mod or this pack), paper
ring, craftable. Result is the `belt` template.

**Done means.** `armorpieces_save` accepted without `force`;
`python tools/check_authoring.py packs/animals/datapack packs/animals/resourcepack` clean; tab
closed; the Lessons section below filled in. No modpage build.

## Lessons from the session

Built as seven cubes in seven bones: `main` (the ferrule, unrotated) and a six-link chain
`tail1 > tail2 > tail3 > tuft1 > tuft2 > tuft3`, one bone per segment. Envelope
x -1.75..1.75, y 5.0..14.6 (Blockbench), z 2.4..5.7; tip just above the knee. Saved clean
without `force`, `check_authoring.py` clean on both pack folders.

**A bone chain that has to hang: author it straight, let the bones bend it.** Blockbench stores a
child group's origin in the same (unrotated) space as its parent, so the whole chain can be laid
out as a straight vertical column — each bone's origin at the top of its own segment, each cube
placed 0.25 below the previous segment's bottom for the joint overlap — and then each bone given
its own small X rotation. No cube coordinate needs pre-rotating. Only the *result* needs
predicting, and that is one line of trigonometry per link: from the pivot, the segment's end is
`(-L·cos a, -L·sin a)` in (y, z) with `a` the **cumulative** angle. My prediction for the tip was
y 5.29 / z 4.56 and the check reported the envelope to within 0.03 of it, so nothing had to be
nudged afterwards.

Sign convention, which is easy to get backwards on a back-hanging piece: a **negative** X rotation
swings a downward segment **backwards** (+z, away from the body); positive brings it forward. The
hang here is cumulative -5°, -14°, -9°, -6°, -4°, -2° — leaning out, then easing back towards
vertical, which is what reads as weight rather than as a stick. Relative rotations per bone are
therefore -5, -9, +5, +3, +2, +2.

**Give every bone in the chain a distinct set of world planes anyway.** Because rotated cubes have
no axis-aligned faces, the COPLANAR test cannot fire between two rotated links, but the ferrule is
unrotated and shares the frame with the body shells, so its z was set to 2.6..4.6 (front face 0.35
clear of the leggings shell) rather than the tempting 2.5.

**The arm box was never a risk here and the numbers say why.** The tail is at z 2.4..5.7, x ±1.75;
the arms are x ±4..±8 at z −2..2. Anything on the belt that stays *behind* z 2.4 and inside x ±2
cannot meet an arm. The thing that does bite on `belt` is the **back** socket: the check produced
ten OVERLAP notes against `cloak`'s banner, `quiver`'s sling and `banner`'s mount, because those
three hang down the same corridor. They are all `-` notes (hull test), and a tail under a cloak is
what a tail under a cloak looks like, so they were accepted, not designed around. There is no way
to hang anything at the small of the back that does not enter the cloak's hull.

**Length is the hard constraint, not the cube sizes.** The brief's "three or four cubes about
1.5x3x1.5 plus two or three 3-high tuft cubes" is 15 units of tail and mid-thigh is 7-8 units from
the belt. The dimensions had to give: rope links are 1.9, 2.05 and 1.35 tall and taper 1.1 -> 0.9
wide, the tuft is 1.85 + 1.75 + 1.15. Keep the *ratio* (tuft is 44% of the length here) and drop
the absolute sizes.

**Silhouette.** The first render showed a thin dark line and no tassel; the fix was in the two
things a side view sees — the rope was slimmed 1.4 -> 1.1 -> 0.9 wide and the tuft fattened in
**depth** (1.6 -> 2.0, 1.9 -> 2.4), because from the side a tail's width is its depth. Resizing
after painting cost nothing: only `tuft_b` grew past its old rectangle, the reply flagged exactly
which faces were now incomplete, and one repeat of the same master `faces` dict fixed it. Moving
the ferrule up 0.4 to expose more rope produced no repaint warning at all, because the box size
did not change.

**Sheets, and the count proof.** 42 faces, three calls, no shape tools at all. The master carries
every face; `part_static` carries the six hair cubes; `part_guard` carries the ferrule's six faces
with **the same greys as the master** in that region (this is what the mod's own `*_guard.png`
files do — the mask is shaded, not a flat 255 stencil). That partition makes the end-of-session
proof exact rather than approximate:

    master 188 = static 156 + guard 32, overlap 0, uncovered 0, outside 0
    every palette value's count == its hex's count on the static layer (68/39/17/11/12/4/4/1)
    the 32 master pixels whose value is NOT in the palette are exactly the 32 mask pixels

Choosing the ferrule's greys (150/160/175/185/200/215/235) disjoint from the palette's values
(22/38/72/80/90/99/114/172) is what makes that last line checkable in one pass. Worth copying.

No face is taller than three rows, so every fill is flat and every detail — two rivets, one pale
highlight, two hair streaks — is an explicit `pixels` entry; nothing interpolated, which is why
each count above lands on a palette entry.

**For the next Animals piece.** Recipe centres now taken in this pack: `minecraft:sweet_berries`,
`minecraft:lily_pad`, `minecraft:honeycomb`, `minecraft:turtle_helmet`, `minecraft:poppy`,
`minecraft:lead`. `armorpieces_set_part` with `fittings` + `static: true` in one call created both
new sheets, and it must come before the mask paint. The active-tab hazard never fired: the guard is
`get_project_info` once after `armorpieces_new` and then reading the `[armorpieces] donkey_tail`
prefix on every reply — twelve other tabs were open, two with unsaved edits, and none was touched.
`python tools/check_part.py` still does not see this pack;
`python tools/check_authoring.py packs/animals/datapack packs/animals/resourcepack` does, and the
bridge's own check is the real gate. Four renders were spent, two of them on the silhouette fix.
