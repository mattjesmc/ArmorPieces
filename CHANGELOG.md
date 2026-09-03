# Changelog

## 0.3.0

**Found in the world.** A part can name the loot tables it turns up in, and the mod adds it to
them as they load - the one thing a datapack cannot do for itself, since it can only replace a
vanilla table whole. The `loot` list on the part's data file is rows of table, weight and chance:
one pool per table, rolled once, with the part's socket template as the entry, so a chest never
holds two parts and the table's own pools are untouched. `chance` is the part's own odds of being
offered and is required, because 1 means every chest; `weight` only splits a table between the
parts that share it. Every shipped part is now found somewhere that suits it - wings in end
cities, horns in bastions, the circlet in ancient cities, mittens in igloos - at chances between
one in twenty and one in three. A second loot function, `armorpieces:set_decoration`, puts a part
on a piece of armor a table hands out, with a socket, a part, a material and optionally its
fittings, so a chest can hold a helmet already wearing a gold circlet with an emerald in it.
`/armorpieces stage loot <table> [rolls]` rolls a table and counts what the mod put in it.

**One template per fitting.** The fitting template now names the fitting it is for, the way a
socket template names its part: one item, and an `armorpieces:fitting` component on the stack,
with its own look and name - *Gemstone Fitting Smithing Template*, made from an amethyst block,
*Guard* from a copper ingot, *Inlay* from any dye, *Banner* from a loom, each in a ring of paper -
and a tooltip that says what it goes on and what goes in. A named template offers the third-slot
item to that fitting alone on each part, so a gemstone template and a ruby fill a circlet's stone
and do nothing to a sash; with the third slot empty it takes out that fitting and nothing else.
The bare template, with no fitting named, is unchanged: it still routes anything to the first
fitting that takes it and empties every fitting at once, so a world holding one keeps working; it
just has no recipe any more. Because the fitting is a component, a pack's own fitting gets its
template from a recipe alone, and `ingredients` on a fitting file supplies the tooltip's words,
with a default per type. The apply and clear recipes stay one file each.

**Your own pack, in Blockbench.** The plugin no longer assumes content lives in this repository.
The repository is the toolkit - still required, for the rigs, the preview and the game-asset
extraction, and the settings and the first-run message now say so - but a piece can sit anywhere:
*Packs...* is a list of folders the author owns, added with a folder picker; *New Pack...* makes a
datapack or resource pack folder with its `pack.mcmeta` at the format the game this mod is built
for wants; *Export Pack...* zips one for handing round. Pieces are found in that list, in the
repository's own places, and in the installed game's `resourcepacks/` and every world's
`datapacks/`, and a piece has two packs: the halves of a `namespace:name` are paired across every
folder, the list shows both when they differ, *New Armor Piece...* asks for both, and every write
goes to the right one - the part file, fittings, recipes and tags to the datapack, the geometry,
textures and the language file to the resource pack. Only the mod's own namespace has masters in
`tools/decoration_masters`; anyone else's `circlet` edits its own file.

**Disabling recipes.** A recipe type that loads and does nothing, `armorpieces:disabled`. A
datapack cannot delete a file the mod ships, so it overrides the file with
`{"type": "armorpieces:disabled"}` instead: the recipe has no fields, matches nothing, and has no
display, so it is out of the recipe book and out of any recipe viewer that reads displays. That
makes a part loot-only (`recipe/template_circlet.json`), a server fitting-free
(`recipe/apply_fitting.json` and `recipe/clear_fitting.json`), or a socket closed to smithing
(`recipe/apply_horns.json`) - any recipe the mod has, and any other mod's just the same. Every
field but the type is ignored.

**The advanced smithing table.** A block, crafted from a smithing table, an armor stand and two
iron ingots, that shows a set of armor and lets a part come off again. Four display slots hold a
helmet, a chestplate, leggings and boots, all worn at once by an armor stand that can be turned by
dragging; an arrow beside each slot picks the piece to work on, and the picked one steps out of the
column to stand against the list of what it wears. That list is a row per socket, head to toe, with
the piece's trim under them: a filled row shows its part as the template that put it there, wearing
a half-size icon of the material it is made of, and beside it one place per fitting that part
declares. An empty place wears the grey hint of the template that would fill it, as the smithing
table shows a faint template in its own empty slot, and the table's template slot wears the hint of
whatever is picked, so what to go and find is named in the slot it has to be dropped into. Clicking
a part or a fitting works on it - its row lights up and a frame closes around it - and Remove
empties whatever is picked, a part, one fitting of it, or the trim: the one way any of the three is
ever taken off, since the smithing table has no ingredient that means "nothing". Below the list
sit the smithing table's own template and material slots with the selected piece standing in for
the base: Apply runs the ordinary smithing recipe lookup and writes the result back into the
display slot, so a socket template puts a part on, a fitting template sets a stone, and a vanilla
trim template trims, while a recipe a pack has turned off stays off, and a fitting goes into the
socket that is picked rather than into every part that takes one - and the stand wears the
result before Apply is pressed, as the smithing table's stand does. Nothing is kept in the block;
everything goes back to the player when the menu closes, whether it was opened at the block or by
`/armorpieces table`.

**Tools.** The Blockbench panel gains a *Craftable* switch beside the two recipe items: off, Save
writes the recipe with its type swapped and the pattern and items kept, so the choices survive
until it is switched back on, and the summary line says *not craftable*. The Part dialog gains a
*Loot* group - rows of table, weight and chance, the table id autocompleting from the game jar
(`vanilla_assets.py --list-loot-tables`) - and the summary line says where the part is found.
The New Fitting dialog takes the template's "Ingredients:" words and its two recipe items, and
writes the fitting's template recipe with the definition. `check_authoring.py` round-trips every
part's template recipe, switched on or off, the way it does the data files, checks every loot row
is in the shape the dialog writes, and checks every fitting's template recipe; given two folders it
checks a piece split over a datapack and a resource pack. `gen_template_icons.py` draws the four
fitting template icons beside the bare one. `export_pack.py` zips a pack folder with its contents
at the root, and is what the plugin's *Export Pack...* runs. `preview_material.py` takes `--pack`
more than once, for a piece whose two halves are two folders.

**Forty-one parts.** Twenty-one new parts, so every socket has at least two answers and six
themes reach across the suit: antlers, bandolier, beast head, buckled belt, chain of office,
claws, coronet, garters, head fins, mantle, pelt, puttees, quiver, scale shins, scale skirt,
streamers and wraps by hand, then nasal, spire, antennae and horsetail through the bridge below.
`docs/plans/part-variety.md` is the candidate list they came from.

**Authoring from an agent.** `tools/mcp` is an MCP server in front of Blockbench's own MCP
plugin: an *authoring* profile of its tools, piece-level tools (`armorpieces_open`, `_new`,
`_check`, `_paint`, `_save`, `_part`, `_set_part`, `_pieces`, `_close`), and after every editing
call the same check every shipped part passes, appended to the reply - clearance and shared
planes from `trace_geometry.py`, unpainted faces and stray paint from the sheet checks, together
in the new `tools/check_part.py`, which also runs by hand over a shipped part, a pack piece or
the piece open in Blockbench. `armorpieces_paint` paints whole faces by name, shaded, in one call.
The plugin publishes the open piece after each edit for that check, drops the bridge's empty undo
entries, and gained a scripting surface for it. `.claude/agents/part-author.md` is the profile
for one session per part; `docs/plans/briefs/` holds the briefs and each session's lessons.

**Whole-texel nets.** A box's UV net is whole texels, rounded up, everywhere: the mod hands
vanilla the rounded size and shrinks each axis back with a per-axis deformation, so a 2.1-wide
face no longer shares a texel column with its neighbour in game, and the plugin lays cubes out
the same way. Whole sizes plus inflate remain the cleaner way to a sub-texel thickness.

## 0.2.0

**Fittings.** A part can take a second material. A fitting names a region of the part - a mask
beside the master, or a bone of the geometry - and the kind of item that fills it, and the smithing
table offers an item to every part on the piece, filling the first fitting on each that accepts it: a
gem to the `gemstone`, an ingot to the `guard`, a dye to the `inlay`, a banner made at a loom to the
`banner`. One fitting template covers all of them, and the template with nothing in the third slot
takes every fitting out again. The circlet takes a gem in its stone, the sash takes a dye on its
strap and a metal on its buckle, the greaves take a dye in their inlay, and the back banner wears a real banner's design, drawn in pattern
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

**Blockbench, the datapack half.** *Part...* on the panel edits the name, the anchors and the
fittings list - picked from every fitting definition in the pack and the mod - and the panel
follows at once: the Anchor list, the Fitting list, the preview rows and a summary line under the
buttons. *New...* beside the list defines a fitting the pack lacks: material (over a tag, or over
ticked materials written as a tag in the pack), dye, or banner on one of the part's bones; the
file, its language line and any tag are written when the dialog confirms. A banner fitting gets a
preview row like the masked ones, and fills its bone with the chosen banner's base colour, a stand-in
for the pattern layers the game draws there. Effects are rows on the same dialog, their fields,
ranges, defaults and descriptions parsed out of the built-in records by `tools/effect_schema.py`
so that Java stays the one source of truth; ids autocomplete from the game jar
(`vanilla_assets.py --list-ids`); any row can be gated on a fitting, which writes
`armorpieces:if_fitting`; a type from another mod is kept as read. Save writes the data
file and the language line, and writes back any field the dialog has no control for exactly as it
read it; a data file is never reformatted for being opened, and the template recipe keeps a
`group` or any other field the two item choices do not decide. Cube rotation is off in the
workspace format, since the mod's cube has none and the exporter dropped it silently.
`preview_material.py --fittings` takes `--pack` for a file outside one, `--list-fittings <pack>`
lists every definition a part there could declare and `--fitting-choices <pack>` the materials and
tags a new one could take; `vanilla_assets.py` now also extracts the trim-material registry and
tags, from a jar that carries `data/`; `tools/check_authoring.py` runs the round trip over every
shipped part. The mod page's example fitting named `#minecraft:trim_materials`, which is an item
tag and would not have loaded; it names `#armorpieces:guard_metals` now.

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
