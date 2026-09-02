# Changelog

## 0.2.0

**Fittings.** A part can take a second material. A fitting names a region of the part - a mask
beside the master, or a bone of the geometry - and the kind of item that fills it, and the smithing
table offers an item to every part on the piece, filling the first fitting on each that accepts it: a
gem to the `gemstone`, an ingot to the `guard`, a dye to the `inlay`, a banner made at a loom to the
`banner`. One fitting template covers all of them, and the template with nothing in the third slot
takes every fitting out again. The circlet takes a gem in its stone, the sash takes a dye on its
strap and a metal on its buckle, and the back banner wears a real banner's design, drawn in pattern
layers the way a shield wears one. Re-applying a part keeps what is set in it, so a circlet can be
changed from iron to gold without losing its emerald.

Fittings are data (`data/<ns>/armorpieces/fitting/`) over three code types - `material`, `dye`,
`banner` - and a mod can add a type the way it adds an effect type, registering the codec and, if it
draws, a renderer; whatever item fills it also goes in `#armorpieces:fitting_additions`, the tag the
one fitting recipe accepts. An effect can be gated on a fitting with `armorpieces:if_fitting`, so an
emerald in the circlet can mean something.

Nothing changes for a part without fittings, on disk or on screen: the field is optional, so armor
decorated before this version reads back exactly as it was written. On the wire the entry does grow,
by an empty map per part - the stream codec has no optional fields - which costs a byte between a
client and server of the same version and nothing else.

**Tools.** Painters emit fitting masks (`tools/fitting_mask.py`); `sync_decoration_masters.py`
installs and checks them; the banner's cloth moved to its own `banner` bone in the shipped geometry.
`preview_material.py` bakes masks the way the game does (`--fitting gemstone=emerald`,
`--fitting inlay=red`) and lists a part's fittings with the values each takes. The Blockbench
plugin paints masks as a third edit mode, greyscale like the master and created on first use, and
its material preview fills each fitting from a dropdown. The rigs load the masks beside the master.
`/armorpieces stage fittings [<part>]` stages every fitting filled with everything the item registry
puts in it, one block per fitting, the part's materials down the rows.

**Docs.** The mod page gains the fitting sections, the `smithing_fitting` recipe type and the
`armorpieces:if_fitting` effect row, and `fitting_template` is named as the thirteenth template item
beside the twelve socket ones.

## 0.1.3

**Docs.** Every claim on the mod page was checked against the code, and four were wrong. Twelve
sockets do not hold one part each: they hold one part *at a time*, and the twenty parts are spread
unevenly over them, three on `back` alone. The built-in effects reach four of the five hooks, not
all of them - nothing built in touches `Lifecycle`. A part is two files and a PNG, plus a line in a
language file, not three files and a PNG. Four stale source comments were corrected to match the
code they describe, including one in `DecorationEffect` that claimed effects are stripped from the
network codec when `ArmorDecoration` in fact sends them, and one in `ModItems` that still counted
ten sockets rather than twelve.

No behaviour changes: comments, `modpage.yml` and the pages generated from it.

## 0.1.2

**Blockbench plugin.** `tools/blockbench_plugin/armorpieces.js` turns Blockbench into an editor for
parts. A piece opens on the vanilla player wearing real armor, in its own trimmed-down workspace:
one panel holds the piece and anchor selectors, master or static editing, a live material preview,
the walk and sprint poses with a phase slider, and the reference toggles. Painting is kept legal by
construction - colour on the master folds to grey under the brush, the static layer is created on
first use, and strokes over a material preview land on the layer being edited. Cubes are box UV by
construction too: a new or resized cube is laid out in free space on the sheet, its paint moves with
its faces, and the sheet grows when it is full, all inside the same undo step as the edit. The
template recipe is two fields on the same panel, a centre item and a ring item with the game's item
list as autocomplete, written on Save.

**Mittens.** A twentieth part, on the vambraces socket, and the first made entirely in the plugin.

**Animated rigs.** The reference rigs now carry the vanilla walk and sprint cycles, baked from the
game's own limb arithmetic, and hang the part under the bone it is attached to so it swings with the
limb and the armor over it. The body, the armor and the cycle are transcribed once, in
`tools/mc_humanoid.py`; the rig's skin, armor and palette textures come from the game jar via
`tools/vanilla_assets.py` and are never committed.

**Material preview outside the game.** `tools/preview_material.py` is a literal port of the mod's
palette mapping, so a part can be seen in any trim material without a running client. It also
prints the ramps a live editor needs, which is what the plugin composites with.

## 0.1.1

Fix five parts whose masters were painted for geometry the model no longer had: feathering,
pinions, spaulders and helm_wings had drifted after their rigs were re-exported, leaving 38 faces
with no opaque pixel behind them and 245 painted pixels where the model has no face. feathering is a
repaint: the plume was rebuilt from a one-unit carved blade into a seven-cube crest.

Every painter now asserts its cube table against the shipped geometry, and
`sync_decoration_masters.py` checks every master against its geometry on install.

Also ships the standalone datapack and resource pack zips as build outputs, raises the Fabric API
baseline to 0.159.0+26.2, and restricts the license: redistribution requires permission.

## 0.1.0

First release. Nineteen parts across twelve sockets, applied at a smithing table like trims and
coloured by the same vanilla trim materials. Geometry, textures and behaviour are all data. Includes
the authoring tools, the grayscale masters that are the source of truth for every part's art, and
the generated store pages.
