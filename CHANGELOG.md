# Changelog

## 0.3.0

**Armor skins.** A third template family beside the socket templates and the fitting templates. A
skin is the armor's *own* texture - what the plate is, rather than what is bolted to it or painted
over it - so a piece, a trim and a skin are three independent choices on one piece of armor.
Fourteen ship: plate, mail, gambeson, gothic, milanese, brigandine, scale, lamellar, then lorica,
varangian, hoplite, samurai and runic - and chainmail, the one that was not drawn. Each is one
greyscale master pair on vanilla's own armor grid, recoloured at load through eight shades taken
from *that armor material's* vanilla texture, with vanilla's own panel edges and shadows mixed back
over it - so a skinned iron helmet still reads as iron, and a modded armor material is skinned for
free from the texture it already ships. A skin is applied at the advanced smithing table with the
piece's own **reforging material** in the addition slot, asked of the armor item itself rather than
of a table the mod maintains: re-skinning is re-forging, and it costs the metal the piece is made
of. Chainmail *armor* takes no skin - its ramp is dead and its identity is the weave - and says so
through a tag a pack can disagree with; chainmail the *look* goes the other way, and every other
material can wear it. That fourteenth skin is the only one nobody drew.
`tools/convert_chainmail_skin.py` greys vanilla's own sheet, stretches the four tones it has out of
the forty-three luma levels they were compressed into, and fills the one hole in vanilla's
silhouette - a bare `boot.bottom`, the single texel in either sheet that Mojang did not put there.
The gradient is not invented but read back out of vanilla's own per-row means, per face, which is
what takes a ramp the checker calls dead to seven of the eight shades; the script re-runs in a
second, so a Minecraft bump that redraws `chainmail.png` is answered by running it again. Leather's
dyeable layer takes the skin, so dye still multiplies into it; trims are drawn
after the base layer as they always were, and are unaffected. A skin never paints a visor: the
face opening is the shape the `brow` parts are drawn to sit in. Every skin's template wears its own
icon, and the icon is the skin: the front of that skin's own chestplate, greyed and set in the
template card, so a hotbar of them says which look is which without a tooltip being read. The game
draws those icons itself, as the item atlas is built - a sprite source finds every skin sheet any
pack ships and an item model type of the mod's own picks between them - so a skin a PACK adds gets
an icon on the same terms the mod's do. `minecraft:select`, the vanilla way to do this, could never
have: its cases are one file, and a resource pack wins a file whole rather than merging it.

A skin is drawn in the same Blockbench the parts are, on a second workspace: the same figure with
the armor *unlocked* and nothing modelled, both master sheets read and written as rows of the
sixteen greys (`armorpieces_skins`, `_open_skin`, `_skin_sheet`, `_skin_paint`, `_skin_material`,
`_skin_check`, `_save_skin`), with `.claude/agents/skin-author.md` the profile for one session per
skin. `tools/skin_sheets.py` is the net every one of them shares, `tools/bake_skin.py` the bake
outside the game, `tools/check_skin.py` the check a master has to pass - unpainted texels under a
face, a silhouette with a hole in it, a ramp so narrow the material cannot show through it -
and `tools/sync_skin_masters.py` installs one - which saving in Blockbench does for you. The mod also gains its first test:
`SkinBakeTest` reproduces `docs/plans/skin-bake-reference.json` for all eight vanilla materials,
the eight shades, the sampled table and the SHA-1 of each material's lighting map, so the Java bake
and the Python one cannot drift apart unnoticed. JUnit is a build-time dependency and ships in
nothing.

**Cloth.** A fourth layer, after the part, the trim and the skin. A cloth is a garment cut out of
the humanoid armor net, painted with a banner's design and baked into the armor's own texture - so
it is not geometry, moves with the armor, clips nothing, and the plate's own rivets and edges read
*through* it. Two ship, **Tunic** and **Tabard**, chestplate only, applied at a smithing table with
a **Cloth Smithing Template** and a banner: the design is the banner's, so sixteen dyes crossed
with every pattern layer is a player's choice rather than a list the mod maintains. The template
comes from a banner pattern in a ring of paper, one item for every cloth there will ever be, and
the empty addition slot takes the garment off again.

Where it sits falls out of where it is drawn and costs nothing: over the skin, because the skin is
the shell texture the cloth composites onto; under every part, because parts are an appended render
layer; under the trim, because the trim is a later pass - a surcoat would cover its trim in life,
but the trim staying visible is the mod's premise. Like a skin it ships no per-material art: one
greyscale cut mask, where alpha is the garment, value is the cloth's own folds, and the two torso
panels are where the banner's pattern goes. Both panels read from outside rather than
front-and-mirrored-back, because a tabard is two panels and not one sheet seen from behind. The
bake runs at 4x so a charge painted for a shield still lands on an 8x12 chest, mixes the armor's
own lighting in at 0.30 where a skin uses 0.35, and caches on an LRU of 64, because the key space
is unbounded - a player can wear any banner. It goes on the last, untinted layer of the equipment
asset, which is the counterpart of the skin's `isShell` rule and for the same reason: leather's
shell is multiplied by its dye, and a cloth composited into it would come out brown on undyed
leather and purple on blue. `#armorpieces:clothable_armor` ships chest armor and nothing else; the
recipe still accepts leg armor, so a pack that wants a hem ships a `humanoid_leggings.png` mask and
edits the tag, with no code changed. Head and foot armor are refused outright, because a helmet
draws on the humanoid sheet but its model does not sample the torso's UVs. There is no drape - a
garment that hangs is geometry, which is a part, and this is deliberately the other thing - and a
cloth is not on the advanced smithing table yet; taking one off works there through the empty
addition, as a skin's does.

**Found in the world.** Most parts are found rather than crafted, and the mod puts them into
vanilla's tables as those load - the one thing a datapack cannot do for itself, since it can only
replace a table whole. A **loot group**, `data/<ns>/armorpieces/loot_group/<name>.json`, is a
category of loot tables and the templates found in it: the tables, a chance, and a TAG of parts.
Six ship, over the six themes the parts are drawn in - `knightly` in strongholds, dungeons, trial
chamber rewards and the mansion; `court` in the mansion, ancient cities, end city treasure, the
desert pyramid and a village temple; `beast` in the bastions, the nether bridge, the jungle temple
and mineshafts; `wayfarer` in village houses, igloos, shipwreck supplies and ruined portals;
`tidal` in ocean ruins, shipwreck treasure and buried treasure; `carapace` in end city treasure,
the jungle temple and mineshafts - and all ninety-one parts are in one. A part joins a group by
being TAGGED, so a pack puts a whole look into the world in one file, and adds its own part to one
of ours without overriding a file of ours. The `loot` list on a part's own data file is unchanged
and stays the exact route, for a part that belongs in one named place: the twenty parts this mod
shipped before 0.3.0 keep theirs - wings in end cities, horns in bastions, the circlet in ancient
cities, mittens in igloos - on top of their group.

**The chance now belongs to the table, not to the part**, which is what makes the above possible.
One pool per table, rolled once, with a single `random_chance` on the POOL: 0.12 means a chest of
that kind holds one of ours about one time in eight, and goes on meaning that as parts are added -
another part changes WHICH one is found, never how often. Under the old shape, a chance per entry,
a table's real odds were `1-∏(1-c)`: 0.28 over the four entries already on `pillager_outpost`, and
climbing to near-certainty once a theme's worth of parts named one table. Where several groups and
rows name one table the highest chance wins and their members pool together, so a chest still never
holds two of ours, and a part offered twice is one entry rather than two.

**All four template families are found, and the split between them is what each one means.** A
skin *is* a look, so the fourteen **divide** across the six groups the way the parts do - plate,
gothic, milanese, mail, chainmail and lorica are knightly; runic, hoplite and samurai are court;
gambeson and brigandine wayfarer; varangian beast; scale tidal; lamellar carapace - on top of the
one signature chest each already had, chainmail in a mineshaft, runic in an ancient city, hoplite
in buried treasure. A **fitting template is not a look** but the second step of one the player
already has, and wanting a gem for the circlet in your hand is theme-blind: all six groups name
`#armorpieces:common` and the four are found **everywhere**, which is also the only route they
have. A `Fitting` is a dispatched codec, one record per type, so a `loot` field on it would have to
be added to every type including a pack's own, where a group naming a tag of fittings says the same
thing from the outside and costs nothing. Cloths keep their two hand-placed chests, the tunic in a
village armorer's and the tabard in a woodland mansion. In a full pool that lands at roughly three
quarters parts, a tenth skins and a tenth fitting templates. A second loot function,
`armorpieces:set_decoration`, puts
a part on a piece of armor a table hands out, with a socket, a part, a material and optionally its
fittings, so a chest can hold a helmet already wearing a gold circlet with an emerald in it.
`/armorpieces stage loot <table> [rolls]` rolls a table and counts what the mod put in it.

**Thirty recipes, not ninety-one.** A template recipe now ships only where the centre item is
plainly the part or what it is made of - a bell for the bells, a saddle for the spurs, a goat horn
for the horns, an ingot for the circlet. The sixty-one reached for because the grid happened to be
free - wolf armor for the mantle, a porkchop for the tusks, a golden chestplate for the cuffs - are
gone, and those parts are found instead. Nothing is *disabled*: they are recipes the mod no longer
has, and a pack that wants one writes it. `check_authoring.py` fails on a part with no recipe, no
`loot` row and no group's tag - a part that ships complete and cannot be had in survival, which no
other check could see; one that means to be creative-only says so with `"loot": []`.

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
dragging; a button beside each slot selects the piece to work on, and the selected piece's sockets
are listed head to toe, each filled one showing its part as the template that put it there, with
the part's material and fittings on hover, and a cross that empties the socket - the one way a part
is ever taken off, since the smithing table has no ingredient that means "nothing". Below the list
sit the smithing table's own template and material slots with the selected piece standing in for
the base: Apply runs the ordinary smithing recipe lookup and writes the result back into the
display slot, so a socket template puts a part on, a fitting template sets a stone, and a vanilla
trim template trims, while a recipe a pack has turned off stays off - and the stand wears the
result before Apply is pressed, as the smithing table's stand does. Nothing is kept in the block;
everything goes back to the player when the menu closes, whether it was opened at the block or by
`/armorpieces table`.

**A gallery on the stage.** `/armorpieces stage` gains three modes that are for the picture rather
than the check. Its older modes are each a cross product with one axis free, which is what makes
them readable and what makes them drab - a row of identical stands in eleven colours, on plain iron,
with every fitting empty - and there is no longer a shot of the mod in them. `stage pieces` puts
every part in the game down exactly once, a row per socket, each on its own randomly dressed suit:
some armor, some skin over it, some colour, and something in every fitting the part declares.
`stage random [count]` builds whole sets the same way, nothing about them chosen - base, skin,
cloth, part, material and fittings all rolled - which is also the fastest way to find two parts that
cannot be worn at once. Both report the seed they used and take it back, so a stage worth
photographing can be built again after a texture is fixed. `stage set [<name>]` is the opposite:
six sets written out by hand, one per theme the parts were authored in - Knight Errant, High Court,
Wild Hunt, Far Road, Deep Tide, Chitin - each filling all twelve sockets, staged the same way every
time. `stage parts` and `stage full` are gone, being what the first two replace; `bases`, `fittings`,
`skins`, `loot` and `clear` are unchanged.

**Tools.** The Blockbench panel gains a *Craftable* switch beside the two recipe items: off, Save
writes the recipe with its type swapped and the pattern and items kept, so the choices survive
until it is switched back on, and the summary line says *not craftable*. The Part dialog gains a
*Loot* group - rows of table, weight and chance, the table id autocompleting from the game jar
(`vanilla_assets.py --list-loot-tables`) - and the summary line says where the part is found.
The New Fitting dialog takes the template's "Ingredients:" words and its two recipe items, and
writes the fitting's template recipe with the definition. `check_authoring.py` round-trips every
part's template recipe, switched on or off, the way it does the data files, checks every loot row
is in the shape the dialog writes, and checks every fitting's template recipe; given two folders it
checks a piece split over a datapack and a resource pack, and it checks that a skin's select
case and its icon name each other, since a case with no texture draws the missing-texture chequer
and a texture with no case is art nothing can show. `gen_template_icons.py` draws the four
fitting template icons beside the bare one, and cuts every skin template's icon out of that skin's
own sheet - writing the icon, the item model and the `minecraft:select` case together, so a skin
drawn later gets all three by existing and there is no JSON to write by hand. It does the same for
the cloths, except that a cloth's icon is its *cut* rather than a swatch of it - read off the mask
that ships, because a tunic's collar gap and a tabard's open flanks are the whole difference
between them and both are visible at 8x10. `export_pack.py` zips a pack folder with its contents
at the root, and is what the plugin's *Export Pack...* runs. `preview_material.py` takes `--pack`
more than once, for a piece whose two halves are two folders.

`check_authoring.py` grew four more checks over the year's features: every cloth's data file, the
sheet it names, its cut masks and its template recipe; the cloth icons on the skins' terms, where
the case is an object and the garment has to be read out of it; every loot group's shape and the
existence of the tag it names, since a group naming a tag nobody wrote loads without complaint and
fills no chest; and no two shaped recipes sharing a crafting grid, which is not a theoretical risk
when every template in the mod is the same ring of paper - two parts given one centre item is one
part the game silently never hands out. `paint_cloth_masks.py` cuts and shades both garments,
reading the net out of `skin_sheets.py` so the panels cannot drift from the rects the bake samples,
and `preview_cloth.py` composites one outside the game. `shrink_shot.py` crops a Blockbench
screenshot to the figure before resizing it, which is the difference between 1290 tokens of mostly
background and 113 tokens of armor, re-sent for the rest of a session either way.

**Ninety-one parts.** Seventy-one new parts. Sixty-four of them are every candidate in
`docs/plans/part-variety.md`, so each of the twelve sockets has at least six answers and the six
themes reach across the whole suit. Antlers, bandolier, beast head, buckled belt, chain of
office, claws, coronet, garters, head fins, mantle, pelt, puttees, quiver, scale shins, scale
skirt, streamers and wraps were authored by hand; nasal, spire, antennae, horsetail, girdle,
knee studs, wing cases, talons, aerials, carapace, pendant, dorsal fin, swim fins, bangles, bone
mask, epaulettes, pouch belt, thigh sheath, padding, bedroll, ears, fang necklace, shin spikes,
spine ridge, cord, loin panels, winged cops, rowel spurs, comb, cheek guards, spiked pauldrons,
buckler, laurel, scarf, cuffs, boot cuffs, browband, tusks, fanged cop, bells, lames, ruff,
chain belt, anklets, cloak, fauld and mail fringe came through the bridge below, one session per
part. Cloak is the first part after Banner to carry a real banner design: the `banner` fitting
is geometry rather than a mask, so its cloth is a single cube in a bone named `banner`.

The other seven are a family of their own: **visor styles**, flat faceplates on the `brow` socket,
which takes it from seven parts to fourteen. The mod shipped one visor, a snouted bascinet built
the way every other part is built. These are the flat answer to the same question - a plate a
quarter of a unit thick whose whole character is what has been *cut out* of it. A historical visor
is a plate with holes in it, and a hole is the one thing `armorCutoutNoCull` gives away: an
unpainted texel is absent rather than transparent, so a sight is a real opening with the player's
own face behind it, at a hue no trim material produces. Barbute is a T cut through a smooth plate
with no relief at all; Sallet Slit one ocularium under a jutting brow reinforce; Bellows Visor two
slots between three proud ribs; Great Helm a riveted reinforce cross with breaths on the sword
side; Savoyard the death's-head, a stone set in its brow; Frog-Mouth one slot at the very top over
a blank jutting face; Spectacle Visor a brille, the only one that cuts the raised bar. All seven
stay on the master, so a faceplate takes the armor's own material and a gold suit makes a gold
visor - colour is an inlay, a guard or a gemstone where the part wants one. Two paint calls each,
and no shape or brush tool anywhere in the family.

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
