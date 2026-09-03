# Brief: Antennae

The third part authored through the bridge (`tools/mcp`), by one `part-author` session on Opus,
after the Nasal and the Spire. What changed since the Spire: `armorpieces_paint` paints whole
faces by name in one call, the reply to `armorpieces_open`/`_new` lists the envelopes of every
other part on the bone, and the recipe is checked against the other templates before it is
written. From the `crest` row of `docs/plans/part-variety.md`:

> **Antennae** - Two thin stalks rising and curling forward from the crown, bulbed at the tips.
> Theme: Carapace. Fitting: `gemstone` (the bulbs).

**Part.** `armorpieces:antennae`, socket `crest` only, in the mod's own pack. Display name
"Antennae". Fittings: `armorpieces:gemstone`, one mask, covering the two bulbs only. No effects,
no loot.

**Shape.** `crest` is not a mirrored socket, so model both stalks. Each stalk is its own bone
chain under `part`: a root bone on the crown a little off centre (x about ±1.5), a one-texel
stalk rising from it, tilted forward by rotating the bone (cubes do not rotate in this format;
a rotated bone group does), a second bone further up tilted further so the stalk curls forward,
and a bulb bone at the tip holding a 2x2x2 cube. Keep the whole thing lower than the feathering
and narrower than the head; the reply to `armorpieces_new` gives every crest part's envelope to
place against. Nothing on the shell's top plane: sit the roots half a texel inside the helmet,
the way the spire does.

**Sheets.** Master: dark stalks (chitin), lighter toward the tips, bulbs bright with a darker
underside. Gemstone mask: the bulbs' faces only. No static layer.

**Recipe.** Centre item `minecraft:lightning_rod` (unused by any template), paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py antennae`
and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons paragraph below
filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

Built in 22 bridge calls: 6 `add_group`, 6 `place_cube`, 2 `remove_element` (the starter cube
and then its bone), 2 `armorpieces_paint`, one `set_part`, one `save`, plus checks and two
screenshots. No `risky_eval`, no hand-edited file.

**What the bridge told me.** The envelope table in the `armorpieces_new` reply is enough to place
a crest part without opening another piece: it gave me the three crest parts in Blockbench units
(brush_crest tops out at 39.0, spire at 40.0, feathering at 44.18, all of them starting at
32.0-32.5 on the shell), so "lower than the feathering" and "the roots half a texel inside the
helmet" turned into concrete numbers before the first cube. The `other sockets on the bone` half
of the same table is what the clash lines measure - the brow parts (circlet, coronet, nasal,
visor) all sit below y 33.3, so a crest that only lives above the helmet crown never comes near
them, and the check confirmed "all clear by more than half a unit" from the start. `past helmet`
in the compact line is the useful running number while blocking out: it climbed 1.25 -> 3.24 ->
5.35 -> 6.73 as the chain grew.

**What I had to work around.**
- The starter piece is a bone `main` with one cube `main_0`, and it counts as 6 unpainted faces
  in every check until it is gone. `remove_element` takes the cube by name and then the group by
  name, two calls, both fine - only `rename_element` is broken on groups, so name bones right the
  first time (`stalk_right`, `curl_right`, `bulb_right` and their mirrors here).
- Bone chains: `add_group` needs the parent to exist, so roots first, then the middles, then the
  tips - three rounds, and the pairs inside a round go in one message. Child pivots and cubes are
  written in the *unrotated* model pose (absolute Blockbench coordinates); the rotations compose
  afterwards. Modelling both stalks straight up at x ±1.5 from y 32.5 to y 40.6 and then giving
  the bones -15 / -30 / -15 degrees of X (with ±6 of Z splay on the roots only) landed the tips at
  z -4.9 and y 39.7 - within a tenth of the hand calculation, so the arithmetic is worth doing
  before the call rather than nudging afterwards.
- The 3D view shows nothing at all while the master is transparent: the first screenshot was a bare
  helmet and looked like a modelling failure. Paint first, then look. The check does say
  `master: every pixel is transparent - nothing will draw`, as a `-` note, not a `!`.
- `python -m modpage build --offline` warned `no texture for minecraft:lightning_rod`; one plain
  `python -m modpage build` fetched it and the recipe icon draws the real rod. The README text was
  unchanged by that second run - only the icon PNG differed - so "unchanged" in the output is not a
  sign the fix failed.

**What the painter covered.** Two `armorpieces_paint` calls, one per sheet, and they covered
everything: 36 faces on the master (`*.*` base, then every face by name with `[top, bottom]` pairs
- dark chitin 55-128 on the lower stalks, 110-185 on the curls, 105-240 on the bulbs) and the 12
bulb faces on `part_gemstone`. Zero unpainted faces afterwards, no stray paint, no colour on a
greyscale sheet. What it did *not* do is anything smaller than a face: the four bright specular
texels on the bulbs went in as the `pixels` list of the same call, which is the right tool for a
highlight and much easier than working out inclusive rectangles for `draw_shape_tool`. Faces that
end up buried (the stalk roots inside the helmet, the joint overlaps) still need paint or they are
reported as holes, so paint them anyway - it costs one entry.

**For the next part.** Model a curled or jointed shape as one bone per segment with a small
overlap at each joint (0.2-0.4 units here); the check treats an own-cube overlap as a silent note,
not a problem, while a gap would have shown as daylight. `armorpieces_set_part` before painting is
the real ordering constraint - it is what creates `part_gemstone`. And check the template centre
item against `data/*/recipe/template_*.json` before choosing: `minecraft:lightning_rod` was free,
and `check_authoring.py` would have caught a collision only after the file was written.
