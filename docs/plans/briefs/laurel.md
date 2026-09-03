# Brief: Laurel

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the eighth
batch of four (read cheek_guards.md and aerials.md first - the head frame, circlet's rails at
x ±4..±6 / y 27.75..30.75, the workspace-killing traps - and girdle.md for a ring of plates).
From the `brow` row of `docs/plans/part-variety.md`:

> **Laurel** - A wreath of leaves across the brow, meeting at the back. Theme: Court. Fitting:
> `inlay`.

**Part.** `armorpieces:laurel`, socket `brow` only, in the mod's own pack. Display name
"Laurel". Fittings: `armorpieces:inlay`, one mask, covering the leaves only; the band they sit
on and the knot at the back stay the material. No effects, no loot, no static layer.

**Shape.** `brow` is not a mirrored socket: model the whole wreath on the head bone. The head box
is x -4..4, y 24..32, z -4..4 (pivot 0, 24, 0); the helmet shell is that box inflated a full
unit, x -5..5, y 23..33, z -5..5; the anchor is at Blockbench (0, 28, -4). Read the envelopes in
the `armorpieces_new` reply: the other brow parts are never compared, but the horns parts share
the bone - aerials' boss sits at x -5.5..-4.5, y 31..32.5, z ±0.75, cheek_guards' rivet at
y 28.6..29.4, ears from y 31.3, head_fins and helm_wings outboard of x 4.66 from y 26.3 up - so
a band at y 29.6..30.4 threads between the rivet and the boss; dodge every listed plane by a
twentieth. Build a `band` bone with a thin ring of four plates a quarter unit thick and 0.8
tall at y 29.6..30.4 closing round the helmet a tenth off its shell (front z -5.35..-5.1, back
z 5.1..5.35, flanks x ±5.1..±5.35, each the full span so the corners double up). Then the leaves:
eight `leaf_*` bones, each a leaf cube 1.0 long along the band, 0.55 tall, 0.25 proud of the band
(front leaves at z -5.6..-5.35, side leaves at x ±5.35..±5.6), placed two per front-half
quarter - at x ±1.2 and ±3.2 on the front plate, and at z -2.6 and -0.6 on each flank - each
bone pivoted at the leaf's inner-lower corner and rotated ±22 degrees about the axis normal to
the plate face (Z for front leaves, X for side leaves) so the leaves lean back toward the knot
like a real wreath, alternating one up one down along the band. A `knot` cube 0.9x0.9x0.4 on the
back plate at x -0.45..0.45, y 29.5..30.4, z 5.35..5.75 ties it. Nothing above y 31.0, nothing
outboard of x ±5.7 or z ±5.8.

**Sheets.** Master: band mid grey with a lighter top row (`pixels`); leaves a step lighter with
a darker centre vein texel row (`pixels`, along each leaf's length); knot bright. Inlay mask: the
eight leaves' faces at the same values, vein included, the band and knot left out.

**Recipe.** Centre item `minecraft:dandelion` (a flat item, unused by any template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py laurel`
and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons paragraph below
filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

Built 2026-09-03 in 31 bridge calls: 1 `armorpieces_pieces`, 1 `armorpieces_new`, 1
`list_outline`, 9 `add_group`, 9 `place_cube`, 2 `remove_element` (starter cube, then its
`main` bone), 1 `armorpieces_check`, 1 `armorpieces_part`, 1 `armorpieces_set_part`,
**2 `armorpieces_paint`** (one per sheet), 2 `set_camera_angle`, 1 `armorpieces_save`. No
`risky_eval`, no `modify_cube`, no nudging, nothing hand-edited; the save went through first
time **without `force`**, and `check_part`, `check_authoring` and `modpage build` were clean.

**What I built, the brief's numbers unchanged.** A `band` bone (pivot 0, 30, 0, unrotated)
holding four ring plates 0.25 thick at y 29.6..30.4 - `band_front` z -5.35..-5.10,
`band_back` z 5.10..5.35, both x +-5.35; `band_right` x 5.10..5.35 and `band_left`
x -5.35..-5.10, both z +-5.35, so the corners double up - plus `knot` x +-0.45, y 29.5..30.4,
z 5.35..5.75. Eight `leaf_*` bones parented to `band`, each with one 1.0 x 0.55 x 0.25 cube
modelled upright from its pivot at the leaf's inner-lower corner (y 29.9..30.45), alternating
up-tilt / down-tilt away from the front centre: `leaf_fr1` pivot (1.2, 29.9, -5.475) rot Z
**+22**, `leaf_fr2` (3.2) Z **-22**, `leaf_fl1` (-1.2) Z **-22**, `leaf_fl2` (-3.2) Z **+22**,
all at z -5.6..-5.35; `leaf_sr1` pivot (5.475, 29.9, -2.6) rot X **-22** and `leaf_sr2`
(z -0.6) rot X **+22** at x 5.35..5.6, `leaf_sl1` / `leaf_sl2` the same rotations at
x -5.6..-5.35. Envelope Blockbench x +-5.60, y 29.50..30.78, z -5.60..5.75; reach 11.04.

**Rotation signs, worked out on paper and confirmed to a hundredth by the first reply.**
About Z, (dx, dy) -> (dx cos - dy sin, dx sin + dy cos): a leaf extending **+x** tips its free
end UP on a **positive** Z angle, a leaf extending **-x** on a **negative** one - so the
left/right pairs are sign-mirrored and the wreath stays symmetric. About X, (dy, dz) ->
(dy cos - dz sin, dy sin + dz cos): a leaf extending **+z** tips UP on a **negative** X angle,
and because the mirror plane is x = 0 the two flanks take the *same* X sign. Predicted top
corner of an up-tilted leaf = pivot_y + 1.0 sin22 + 0.55 cos22 = 30.785; the reply printed
`past helmet y-2.22` (= 30.78) on the very first leaf, so nothing was ever moved after placing.
Down-tilted leaves bottom out at 29.9 - 1.0 sin22 = 29.525, which is why the pivot sits at
y 29.9 rather than on the band's own 29.6 floor: at 29.7 the down leaves would have dipped into
`cheek_guards`' rivet (top y 29.4). As placed the band clears the rivet by 0.20 and the leaves
by 0.13, and the tallest leaf clears `aerials`' seg1 by 0.10 - the brow band really does thread
between them, but the corridor is only about 1.6 units tall.

**`!` lines accepted: none** - the finished check reports `ok: nothing needs a decision`. It
does print **30 OVERLAP notes, one shared-plane note and 16 near notes**, all `-`, and they are
the price of the shape: a wreath that *closes round the helmet* occupies the temples at
x +-5.1..5.6, and `horns`, `helm_wings`, `head_fins` and `antlers` all put their socket boss on
that exact patch (x 4.66..5.6, y 29..31). There is no height that avoids them - above y 31 is
aerials' boss and the ears, below y 29.4 is the cheek-guard rivet - so a closed ring on `brow`
either laps the horn bosses or is not a ring. Every listed overlap is a horn root passing
*through* the wreath, which is what a wreath worn over horns would do. The one shared plane
(`band and antlers:horns's burr share the plane y = -6.4`, i.e. the band's top at Blockbench
30.4) the checker itself marks *inside the shell, so occluded*; I left the brief's 0.8-tall band
rather than shaving it to 0.75 for a plane nothing can see. The tightest near miss, 0.03 in y
against `helm_wings`' horn1, is a gap, not a touch.

**Two paint calls, and the interesting half is what the painter could not do.** Master: 78
faces (`*.*` 140, then all 78 by name) plus 44 `pixels`; inlay mask: the 48 leaf faces at the
master's own values. Zero unpainted faces, no stray paint, greyscale confirmed with Pillow -
master 238 opaque texels spanning 85..245, mask 48 spanning 95..185, none outside the
silhouette. **The brief's two `pixels` jobs were both impossible as written, because this part
has almost no multi-texel faces.** A leaf is 1.0 x 0.55 x 0.25, so *every one of its six faces
is 1x1* - there is no room for a "darker centre vein texel row", and no room for `[top, bottom]`
either. I spent the vein on the leaf's `up` face instead (118 against a 185/168 blade): on a
22-degree leaf that single texel reads as a dark midrib line down its length and, as a bonus,
separates neighbouring leaves. Likewise the band is 0.8 tall, so its outer face is **one row**
(11x1) and the brief's "lighter top row" cannot be a row of pixels inside it - the band's `up`
face *is* the highlight (200 against 150). What I did spend the 44 pixels on is the one thing
`faces` genuinely cannot do here: a **horizontal** grade along each of the four band plates'
outer rows, since `[top, bottom]` shades rows and these faces are a single row - front bright at
the centre (170) falling to 132 at the ends, back plate a flat-lit 112..135, and each flank
ramped 118 (rear) to 158 (front). Getting the direction right needs the box-UV strip rule the
cheek_guards session wrote down: on `east` texture-x increases toward -z (front), on `west`
toward +z (rear), and on `north` toward -x. The mask is the leaves only - band and knot stay the
trim material, as asked.

**For the next part.** `minecraft:dandelion` is now taken as a template centre; it had never
been cached, so `--offline` drew it as missing-texture, one plain `python -m modpage build`
fetched it and a re-run came back `unchanged` (89 recipes). `brow` is a *non-mirrored* socket:
eight leaves means eight bones and eight cubes, nothing is free, and the left/right sign flip
is yours to get right. And if you are planning texture detail, size the cube first: anything
under 2 units on an axis rounds to one texel there, so **a 1-unit ornament is six flat texels**
- design the shading as per-face values and keep `pixels` for the long thin pieces, which on
this part were the only faces wider than one texel.
