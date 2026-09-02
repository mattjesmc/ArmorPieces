# Changelog

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
