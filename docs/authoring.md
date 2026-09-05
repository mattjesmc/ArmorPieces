# Authoring parts

A part is two files and a PNG, plus a line in your language file for the name. None of it is code.
Namespace them however you like; every namespace is scanned. [Skins](#skins) — the armor's own
texture rather than something worn on it — are authored the same way and are two PNGs and a file.

There are two ways to make them:

- **[In Blockbench](#in-blockbench)** with the mod's plugin, which opens a part on the vanilla player
  wearing real armor, paints the textures in place, previews any trim material, and writes every file
  on Save.
- **[By hand](#by-hand)**, writing the three files yourself. This section is also the reference for
  what the plugin writes.

Either way, [giving a part behaviour](#giving-a-part-behaviour) is one more field in the same file.

## In Blockbench

`tools/blockbench_plugin/armorpieces.js` turns Blockbench into an editor for parts. A piece opens
on the vanilla player wearing real armor, its master, static layer and fitting masks are painted
in place, any trim material can be previewed live with the fittings filled or empty, and Save
puts everything back where it came from. The plugin has no geometry or colour maths of its own: it
drives the repo's Python tools, so the editor and the command line cannot disagree.

**Your own pack.** The repository is the toolkit, not the workspace: the plugin needs a clone of
it, because the rigs, the preview and the game-asset extraction are its Python, but your content
never has to live inside it. A player's part is two folders — a resource pack under
`.minecraft/resourcepacks/<name>` for the model, textures and names, and a datapack under
`.minecraft/saves/<world>/datapacks/<name>` for the part file, its recipe and any fittings — and
the plugin knows both. *Tools › Armor Pieces › New Pack…* makes either kind, with a `pack.mcmeta`
at the format the game this mod is built for wants, and adds it to your list; *Packs…* is that
list, any folder holding `data/` or `assets/`, added with a folder picker. Pieces are looked for
in your list, then the repository's own places, then the game's `resourcepacks/` and every world's
`datapacks/`, and the two halves of a `namespace:name` are paired wherever they sit, so the piece
list shows `mypack:visor  (.minecraft/saves/Home/datapacks/mine + .minecraft/resourcepacks/mine)`
and every write goes to the right half. *Export Pack…* zips a folder for handing round, contents
at the root the way the game wants them. Three settings: *Armor Pieces repository* (the clone),
*Armor Pieces Python* (the interpreter, `python` by default) and *Armor Pieces packs* (your list,
edited through *Packs…*). Only the mod's own namespace has masters in `tools/decoration_masters`;
a pack's `circlet` is its own file.

**Install.** Blockbench 5.1 or later, and Python 3 with Pillow on `PATH` (the same requirement
as every tool in the repository). In Blockbench: *File › Plugins › Load Plugin from File*, and pick
the file. It finds the repository from its own location; if the file was copied elsewhere, set
*Armor Pieces repository* in Settings to the repo root. The first piece opened extracts the
vanilla textures the rig needs from the game jar.

**Open a piece.** *Tools › Armor Pieces › Open Armor Piece…* lists every part in your packs, in
`src/main/resources` and under `run/`, and in the game's own folders, and opens it as its own
tab. *New Armor Piece…* asks for a datapack and a resource pack — the same folder is fine, and is
the default — and writes the datapack entry to the one, a starter model, a blank texture and the
language line to the other, then opens that. A piece tab shows only what a part needs: Edit
and Paint modes, the outliner, transform, the UV editor, colour and palette, and one
**Armor Piece** panel with every control:

| Control | What it does |
| --- | --- |
| Piece, Anchor | Which part is open and which socket it is rigged on. Changing the anchor rebuilds the rig, which reloads the model from disk, so save modelling first; what *Part…* changed carries across. |
| New…, Part…, Save, Rebuild | Create a piece; edit its name, anchors and fittings; write everything back to the pack; reload the open one from disk. A line under the buttons says what the part is: name, anchors, fittings. |
| Editing: Master / Static / Mask | Which sheet the brush paints. The master is greyscale by definition — the palette turns grey and any colour painted on it folds to its value under the brush. The static layer keeps real colour and is created the first time it is selected. |
| Fitting | With Mask selected: which of the part's masked fittings the brush paints. A mask is greyscale like the master — its values are the fitting's shading — and is created blank the first time it is selected. |
| Material preview | Shows the part through a trim material's palette. Strokes still land on the sheet being edited, the UV editor keeps showing the greyscale, and the preview follows the brush. |
| one row per fitting | With the preview on: what each fitting holds — a gem, a metal, a dye, a banner, or empty. The preview bakes the masks exactly as the game does, in the part's order. A banner fitting is shown as a flat fill of the banner's base colour over its bone, standing in for the pattern layers the game draws there. |
| Pose, Phase | The walk or sprint cycle, frozen at any point, without leaving Edit or Paint mode. |
| Show player, Show armor, Outliner: part only | Hide the reference figure, the armor layers, or everything but the part in the outliner. |
| Recipe centre, Recipe ring | The template recipe: one item in the middle of a ring of four, paper unless there is a reason. Item ids autocomplete from the game's own list. Written on Save as `data/<ns>/recipe/template_<part>.json`. |
| Craftable | Whether that recipe works. Off, Save writes the same file with its type swapped to `armorpieces:disabled` — it loads, matches nothing and is absent from the recipe book — and the two items kept, so switching it back on is the reverse swap. The summary line says *not craftable* while it is off. For a part that is found rather than made. |

**The part itself.** *Part…* opens the datapack half as a dialog: the name a player reads,
the sockets the part may occupy, ticked by armor piece, and its fittings as an ordered list
picked from every fitting definition in the pack and the mod — each shown with its kind, a
mask to paint or a bone to draw on. The panel follows at once: the Anchor list, the Fitting
list, the preview rows and the summary line. *New…* beside that list defines a fitting the
pack does not have yet: a material fitting over a trim-material tag or over ticked materials,
which are written as a tag in the pack so another pack can add to it; a dye fitting; or a
banner fitting on one of the part's own bones, with its pattern sheet and front face. The
definition, its language line and any tag are written the moment the dialog confirms, and
the fitting joins the part's list. The same dialog takes the "Ingredients:" words for the
fitting's template and the two items of its recipe, and writes
`recipe/fitting_template_<name>.json` beside the definition when a centre item is given. Effects are rows on the same dialog: pick a built-in
type and its fields appear, with the ranges, defaults and descriptions read out of the Java
that defines it, and attribute, mob-effect and damage-tag ids autocompleting from the game.
Any row can be switched to run *only while* one of the part's fittings holds a chosen
material or dye, which is `armorpieces:if_fitting` written for you. An effect the dialog
cannot show — a type from another mod — is kept as it is and shown read-only. *Loot* is rows
of table, weight and chance, the table id autocompleting from the game's own list with the
chests first; the summary line says where the part is found. An empty list is no field.

**Modelling.** Model inside the `part` group; everything else is the locked reference. The
mod's format is box UV only, so the plugin keeps it that way: a cube added, converted or
resized is laid out in free space on the texture, the paint on its faces moves with them, and
the texture grows when it is full. All of that lands in the same undo step as the edit. Cubes
do not rotate — the mod's cube has no rotation — so a tilt is a rotated bone. A cube's size
may be fractional; its unwrap is always whole texels, rounded up, in the plugin, the checks and
the game alike, so a 2.1 × 11.4 × 0.9 cube paints as 3 × 12 × 1 and no two faces share a texel.

**Saving.** Save exports the geometry through `bb_geo.py`, writes the master, static layer and
masks back to their files, writes the template recipe, and — for a part whose master lives in
`tools/decoration_masters/` — runs `sync_decoration_masters.py`, which installs the sheets and
checks them against the geometry. When *Part…* changed something it also writes the data file
and the language line, and nothing else: a field the dialog has no control for, an effect say,
is written back exactly as it was read, a file nothing changed is not touched, and the recipe
keeps a `group` or any other field the two item choices do not decide — including, when it is
switched off, the pattern and items the disabled file still holds.
`tools/check_authoring.py` runs the round trip over every shipped part, recipes included; given
a pack folder it checks that pack, and given two — `check_authoring.py <datapack> <resourcepack>` —
a piece split over both.

**A skin, not a part.** *Open Armor Skin…* opens the other kind of thing this plugin edits — see
[Skins](#skins) — as a workspace of its own: the same figure, but the armor is unlocked and painted
by the skin's two greyscale sheets, and nothing is modelled, because a skin *is* the armor. It gets
an **Armor Skin** panel with the same shape as the piece one, and the palette becomes the sixteen
levels a skin is written in — `0`–`f`, seventeen apart — so a colour picked off it is a value the
sheets really use.

| Control | What it does |
| --- | --- |
| Skin | Which skin is open. The list is every master pair under `tools/skin_masters/`, labelled with the pack half it belongs to, or *masters only* when it has none yet. |
| New…, Skin…, Save, Rebuild | Start a skin — its master pair, blank or seeded on a vanilla material's own silhouette, its `armor_skin` file, its sheets and its name, into a datapack and a resource pack you pick; edit the name a player reads and where its template is found; write everything back; reload the sheets from disk. |
| Showing: Master / On a material / Vanilla's light | The greyscale you are painting, the bake as the game performs it, or vanilla's own lighting for that material *on its own* — mid grey where it changes nothing, and brighter or darker by exactly what it adds. Strokes always land on the greyscale master, whichever is shown. |
| Material | Which armor material the bake is shown on. Look at a skin on iron, gold and netherite: the light, the saturated and the dark end of the range. |
| Vanilla light | How much of that material's own texture is mixed over the master before the ramp is read. `0.35` is what the game does; `0` is the pattern with none of it, and the two pictures either side say which shapes are yours. |
| Pose, Phase | The walk or sprint cycle, frozen, as a piece's. |
| Show player, Helmet, Chestplate, Leggings, Boots | The figure and the four shells, one at a time. A boot drawn over the leggings and a helmet that swallows the face are only visible with the shell above taken off. |
| Recipe centre, Recipe ring, Craftable | The skin template's recipe, exactly as a part's, written on Save as `data/<ns>/recipe/skin_template_<skin>.json`. |

Save writes both sheets back to `tools/skin_masters/<skin>/`, installs the pair where the client
loads it, and — when the skin has a datapack half — writes the data file, the language line and the
recipe. The masters stay in the repository even when the content does not, because the rig and the
checks are built from them: *authoring* a skin needs the clone, shipping one does not.

**Starting from a rig.** Outside the plugin, authoring a part starts from a rig: each one holds
the vanilla body and all four armor layers at their real inflate, animated with the game's own walk
and sprint cycles, with an empty group sitting exactly where the layer will draw.
`python tools/bb_rig.py --all` regenerates them; the skin, armor and palette textures they
reference are extracted from the game jar by `tools/vanilla_assets.py` on first use and are never
committed. `bb_geo.py` converts `.bbmodel` to the mod's geometry and back.

**From an agent.** The same editor drives from an MCP client through `tools/mcp`, a small server
in front of Blockbench's own MCP plugin: it serves the tools a part author uses (an *authoring*
profile of the plugin's ninety-odd), adds `armorpieces_open`, `_new`, `_check`, `_save`, `_part`,
`_set_part`, `_pieces` and `_close`, and after every editing call appends the check every shipped
part passes - clearance and shared planes from `trace_geometry.py`, unpainted faces and stray or
coloured paint from `sync_decoration_masters.py`, together in `tools/check_part.py` - so the reply
that placed a cube on the helmet shell says so. Save refuses while problems stand unless told
otherwise. `tools/mcp/README.md` has the setup and what the model is told; `check_part.py` runs
the same report by hand over a shipped part (`check_part.py antlers`, `--all`), a pack piece, or
the piece open in Blockbench (`--status`).

## By hand

**1. The part** — `data/<ns>/armorpieces/armor_decoration/dragon_crest.json`

```json
{
  "asset_id": "<ns>:dragon_crest",
  "description": { "translate": "decoration.<ns>.dragon_crest" },
  "anchors": ["crest"]
}
```

`anchors` lists every socket the part may occupy; a smithing attempt anywhere else will not craft.
The sockets are a closed list — they are places on the humanoid model, not data:

| Piece | Anchors |
| --- | --- |
| Helmet | `crest`, `brow`, `horns` |
| Chestplate | `pauldrons`, `back`, `collar`, `vambraces` |
| Leggings | `belt`, `tassets`, `knees` |
| Boots | `spurs`, `greaves` |

**2. The shape** — `assets/<ns>/armorpieces/decoration/dragon_crest.json`

Bones and cubes in Blockbench's vocabulary, baked through vanilla's own `MeshDefinition` path, so
UVs, per-bone pivots and rotations and cube inflation all behave as they do for any entity model.
Coordinates are entity-model units (1/16 block) and **+Y points down**, which is why something
standing on top of a head has a negative Y origin.

```json
{
  "texture_width": 64,
  "texture_height": 32,
  "bones": [
    {
      "name": "spine",
      "pivot": [0, 0, 0],
      "cubes": [ { "origin": [-1, -6, -4], "size": [2, 6, 8], "uv": [0, 0] } ],
      "children": []
    }
  ]
}
```

**3. The texture** — `assets/<ns>/textures/entity/decoration/dragon_crest.png`

One grayscale master: **value is shading, alpha is the silhouette**. The game maps it onto each
trim material's own palette at load time, so every material — including ones a pack adds
tomorrow — is free.

Not everything is metal. An optional RGBA companion named `dragon_crest_static.png` keeps its own
colour instead of taking the material's, so a horn stays ivory and a sash stays cloth while the
hardware still turns gold. The master remains the single source of truth for the silhouette. If a
part needs bespoke art in one material, `dragon_crest_<suffix>.png` beside the master wins.

**3b. Fittings, if the part has any.** A fitting is a region of the part that takes a second
material. Declare it on the part, in the order the smithing table should offer an item to them:

```json
"fittings": ["armorpieces:gemstone", "armorpieces:guard"]
```

and paint the region as a grayscale mask beside the master, named after the fitting:
`dragon_crest_gemstone.png`. While the fitting is empty the mask is ignored; while it holds a gem,
every opaque mask pixel takes the mask's own value through the gem's palette. Four fittings ship —
`gemstone` and `guard` take trim materials (gems and metals, by tag), `inlay` takes a dye, and
`banner` takes a banner made at a loom onto a bone of the geometry named `banner`. A fitting is a
datapack file too, `data/<ns>/armorpieces/fitting/<name>.json`, so a pack can add a `pommel` that
takes any metal:

```json
{ "type": "armorpieces:material",
  "description": { "translate": "fitting.<ns>.pommel" },
  "materials": "#armorpieces:guard_metals",
  "ingredients": { "translate": "fitting.<ns>.pommel.ingredients" } }
```

`ingredients` is optional: the "Ingredients:" line of the pommel's own template (see 4 below),
and without it the type answers — *Trim Materials* for a material fitting, *Any Dye* for a dye
fitting, *A Banner* for a banner fitting.

A new fitting *type* — one that reads an item the three built-in types cannot, or draws its own
geometry instead of colouring a mask — is Java, the way a new effect type is: implement
`Fitting` (or `Fitting.Masked`) and register its codec with `Fittings.register`, plus a
`FittingRenderer` through `FittingRenderers.register` if it draws. Whatever item fills it must
also be in `#armorpieces:fitting_additions`; that tag is what the one fitting recipe accepts, so
an item outside it never lights the table up, however willing the fitting.

**4. Handing it out.** There is no recipe to write. The mod ships one smithing recipe per socket
and the part travels on the *template stack*, so a pack only has to give out a template carrying
the `armorpieces:decoration` component:

```json
{
  "type": "minecraft:crafting_shaped",
  "pattern": [" # ", "#F#", " # "],
  "key": { "#": "minecraft:paper", "F": "minecraft:dragon_breath" },
  "result": {
    "id": "armorpieces:crest_template",
    "components": { "armorpieces:decoration": "<ns>:dragon_crest" }
  }
}
```

A loot table with `minecraft:set_components` does the same, and so does nothing at all: the
creative tab is built by walking the registry, so a new part appears there the moment the pack
loads. The twelve socket templates are `<socket>_template` — `crest_template`, `brow_template`,
and so on — and `fitting_template` is the thirteenth, one item for every fitting the same way:
the fitting it is for rides on the stack as `armorpieces:fitting`, so a pack's `pommel` gets a
pommel template from a recipe whose result carries `"armorpieces:fitting": "<ns>:pommel"`, and
the item model picks its look by the same component — a texture each for the four shipped
fittings, the plain card for any other. A named template offers the third-slot item to that
fitting alone on each part; the bare template, with no component, still offers it to every
fitting in turn, and with an empty third slot empties every fitting where a named one empties
only its own. The four shipped recipes are `recipe/fitting_template_<fitting>.json`, an amethyst
block, a copper ingot, any dye and a loom in a ring of paper.

**4b. Found rather than made.** A pack can write a loot table of its own, but it cannot add to a
vanilla one — only replace it whole, and two packs replacing `chests/ancient_city` cannot both
win. So the mod does the adding, as each table loads, and there are two ways to tell it what.

*The one that scales* is a **loot group**: a category of loot tables, and the parts found in it.

```json
// data/<ns>/armorpieces/loot_group/tomb.json
{ "chance": 0.12,
  "tables": [ "minecraft:chests/desert_pyramid",
              { "table": "minecraft:chests/ancient_city", "chance": 0.2 } ],
  "parts": "#<ns>:tomb",
  "skins": [ "<ns>:sarcophagus" ],
  "fittings": "#armorpieces:common" }
```

Membership is a **tag**, `data/<ns>/tags/armorpieces/armor_decoration/tomb.json`, so a part joins
by being tagged and nothing about the part's own file changes. That is what makes it worth having:
one file says where a whole look is found, and adding the fortieth part to it is one line in a tag
rather than a fortieth edit. It also runs both ways — your part joins one of the mod's groups by
being tagged into `#armorpieces:knightly`, without overriding a file of ours. `weight` sets what
every member of the group is worth against the other groups sharing a table.

All four template families ride in the same pool. `skins` and `cloths` are the same field for those
registries; `fittings` is the same field again, and is the **only** route into the world for a
fitting template, since a `Fitting` is a dispatched codec — one record per type — and a `loot`
field on it would have to be added to every type, including a pack's own. That asymmetry is also
the right shape: a fitting template is not a look but the second step of one the player already
has, so the mod's six groups all name `#armorpieces:common` and the four fitting templates are
found everywhere. The skins divide by theme instead, because a skin *is* a look.

*The exact one* is the `loot` list on the part's own file, for a part that belongs in one named
place and nowhere else:

```json
"loot": [
  { "table": "minecraft:chests/ancient_city", "weight": 2, "chance": 0.15 },
  { "table": "minecraft:chests/desert_pyramid", "weight": 1, "chance": 0.1 }
]
```

**The chance belongs to the table, not to the part.** However many groups and rows feed one table,
the mod adds it ONE pool, rolled once, with a single `random_chance` on the pool — so `0.12` means
"a chest of this kind holds one of ours about one time in eight", and it goes on meaning that as
parts are added. What another part changes is *which* one is found. (The obvious alternative, a
chance per part, does not survive contact with ninety of them: the table's real odds are
`1-∏(1-c)`, which climbs until every chest holds something.) Where several sources name one table
the highest chance wins and the members pool together, and a part offered twice is one entry, not
two. `weight` is optional, 1 by default, and only decides which member is placed once the pool has
fired. Any table will do, a mob's or a fishing pool's as much as a chest's.

A part with no recipe and no route into the world cannot be had in survival at all, so
`check_authoring.py` fails on it; a part that means to be creative-only says so with an empty
`"loot": []`. The mod ships six groups over the six themes its parts are drawn in — `knightly`,
`court`, `beast`, `wayfarer`, `tidal`, `carapace` — holding all ninety-one parts, the fourteen
skins divided between them, and the four fitting templates in every one. Craftable recipes are kept
only where the centre item genuinely is the part or what it is made of; everything else is found.

For decorated armor rather than a template — a helmet already wearing a circlet with an emerald
in it — a table uses the mod's loot function on an armor entry:

```json
{ "function": "armorpieces:set_decoration",
  "socket": "brow", "part": "<ns>:dragon_crest", "material": "minecraft:gold",
  "fittings": { "armorpieces:gemstone": "minecraft:emerald" } }
```

The stack has to be armor for the socket's slot and the part has to fit the socket, the same two
rules the smithing table applies; a mismatch is reported when the table loads, and the armor
passes through plain. `fittings` is optional and written as it is in `/give`.

**Overriding what this mod ships.** Same ids, your pack. A resource pack can restyle any part's
geometry or texture and a datapack can change where it may be worn.

**Turning a recipe off.** A datapack cannot delete a file the mod ships, so the mod ships a recipe
type that loads and does nothing. Override the recipe's file with it:

```json
{ "type": "armorpieces:disabled" }
```

It has no fields, matches nothing, and has no display, so it is absent from the recipe book and
from any recipe viewer that reads displays. That is how a part becomes loot-only
(`recipe/template_circlet.json`), how a server does without fittings (`recipe/apply_fitting.json`
and `recipe/clear_fitting.json`), or how a socket is closed to smithing altogether
(`recipe/apply_horns.json`) — any recipe the mod has, and any other mod's just the same. Every
other field in the file is ignored, which is why the Blockbench plugin's *Craftable* switch can
leave the pattern and items in place under the swapped type.

## Giving a part behaviour

Parts are cosmetic by default. A part that should do something while it is worn carries `effects`
— one more field on the file you were already writing, or a row on the plugin's *Part…* dialog:

```json
"effects": [
  { "type": "armorpieces:blink", "chance": 0.2, "damage_types": "minecraft:is_projectile" }
]
```

Four built-in behaviours reach four of the five hooks from JSON alone, and a fifth type gates
them:

| `type` | Hooks | Fields |
| --- | --- | --- |
| `armorpieces:attribute` | Attributes | `id`, `attribute`, `amount`, `operation` |
| `armorpieces:mob_effect` | Ticking | `effect`, `amplifier`, `ambient`, `show_particles`, `show_icon` |
| `armorpieces:blink` | Damage | `chance`, `radius`, `damage_types`, `attempts` |
| `armorpieces:glide` | Gliding + Ticking | `sink`, `wear_interval` |
| `armorpieces:if_fitting` | all, forwarded | `if` (a fitting, and optionally `material` or `dye`), `then` (any effect) |

The last is what makes a gem more than paint: `{ "type": "armorpieces:if_fitting",
"if": { "fitting": "armorpieces:gemstone", "material": "minecraft:emerald" }, "then": { ... } }`
runs its effect only while an emerald is set. `material` and `dye` are alternatives — one narrows
a material fitting, the other a dye fitting, and a condition naming both is refused at load.
Naming neither is the shortest form: while there is anything in the fitting at all.

The five hooks are `Ticking` (every server tick worn), `Damage` (a veto — `allowDamage` false
cancels the hit outright), `Attributes` (equip/unequip), `Gliding` (vanilla's own `canGlide`
check) and `Lifecycle` (put on and taken off, for state that lives outside the item — the one
hook no built-in behaviour reaches, so putting anything there means Java). A part has no
durability of its own, so an effect that costs something spends the *decorated piece's*
durability — `pinions` wears the chestplate it is bolted to.

**A new effect type is the one thing that needs Java**, because behaviour is code. Implement a
hook, register the codec, and add nothing else:

```java
public record BlinkAway(float chance) implements DecorationEffect.Damage {
    public static final MapCodec<BlinkAway> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
        Codec.FLOAT.fieldOf("chance").forGetter(BlinkAway::chance)
    ).apply(i, BlinkAway::new));

    public MapCodec<? extends DecorationEffect> codec() { return CODEC; }

    public boolean allowDamage(DecorationEffectContext ctx, DamageSource src, float amount) { ... }
}

// in onInitialize
DecorationEffects.register(Identifier.fromNamespaceAndPath("examplemod", "blink_away"), BlinkAway.CODEC);
```

From then on `"type": "examplemod:blink_away"` works on any part in anybody's datapack. The
context carries the whole entry, so an effect can scale with the material it was applied in.
Effects are synced to the client, because `canGlide` runs on both sides.

## Skins

A skin is the third kind of template, and it says a different thing about a piece of armor than a
part does. A part is geometry hung on the body; a trim is vanilla's accent painted over the armor's
texture; a **skin is the armor's own texture** — what the plate *is*, rather than what is bolted to
it or painted over it. Nothing about a skin changes a silhouette, so every part, every trim and
every socket carries on exactly as it did.

A skin is **two greyscale sheets, one data file and a recipe**:

    assets/<ns>/textures/entity/skin/<skin>/humanoid.png            64x32, on vanilla's armor grid
    assets/<ns>/textures/entity/skin/<skin>/humanoid_leggings.png   64x32, the leggings twin
    data/<ns>/armorpieces/armor_skin/<skin>.json                    asset_id, description, loot
    data/<ns>/recipe/skin_template_<skin>.json                      the ring of paper, as a part's is

```json
{
  "asset_id": "examplemod:carapace",
  "description": { "translate": "skin.examplemod.carapace" },
  "loot": [ { "table": "minecraft:chests/jungle_temple", "weight": 1, "chance": 0.05 } ]
}
```

Two files, not two per material. **The colour comes from the armor, not from the skin**: the sheets
are drawn in the sixteen greys, and the client recolours them through eight shades taken from that
armor material's own vanilla texture, deepened so the master's form has somewhere to live, with
vanilla's own lighting mixed back over the top. So a skinned iron helmet still reads as iron beside
an unskinned one, and an armor material added by another mod is skinned the moment it is installed —
the only thing wanted from it is the equipment texture it already ships. `SkinBake` is the
arithmetic and `python tools/bake_skin.py --report` prints what each material gives you.

Three consequences worth knowing before you draw:

- **Shade in bands four to five levels apart.** A level is a position on an eight-stop ramp and most
  materials repeat stops, so a step of one or two levels can bake to the same colour on iron.
  `python tools/bake_skin.py --levels` prints what every level buys on every material, and
  `--pair 6 a` checks the pair you fancy.
- **You are not drawing on bare armor.** Vanilla's own texture for the material — its panel edges,
  the rim along the top of a plate, the shadow under an overhang — is added to your texel's *value*
  before the ramp is read. That is what keeps a skinned plate reading as metal, and it runs ±45:
  two and a half of your sixteen levels, with up to five levels between two texels side by side. So
  the band above is a floor against the ramp, not against the light, and a shape placed along a
  seam vanilla already shades will not be seen. `python tools/bake_skin.py --lighting` has the
  numbers; `check_skin.py` counts the steps it actually overrules on the worst material (the skins
  that ship lose 2–11%); and in Blockbench the Armor Skin panel's **Showing** switch draws that
  offset on its own, mid grey where it changes nothing.
- **A skin never paints a visor, and never paints the raised helmet shell.** The face window is what
  the `brow` sockets need, and the `hat` net at UV 32,0 sits exactly where those parts do — vanilla
  paints neither, and a skin that did would bury seven parts.

A pack may ship `<sheet>_<material>.png` beside the pair — `humanoid_netherite.png` — and that art
is used as it is for that one material, which is the same escape hatch a part has.

**The template's own icon draws itself, and yours does too.** One item carries every skin and picks
its look at render time, off the `armorpieces:skin` component. The art is not drawn by hand and is
not a file anywhere: it is the top ten rows of your skin's own chest front, lifted off
`humanoid.png`, greyed and levelled into the template card's range, drawn by the game as the item
atlas is built. So the icon is a swatch of the armor rather than a symbol for it, it cannot drift
from what the player will wear, and **a skin a pack ships gets an icon on exactly the same terms as
one the mod ships** — draw the sheet, and the icon is there.

That last part is why this is in the mod rather than in a script. `minecraft:select`, the vanilla way
to give one item many looks, keeps its cases in one file, and resource packs resolve a file by
winning it outright rather than by merging it — so a select listing the mod's own skins is a select
your skin could never join. The mod registers a sprite source (`armorpieces:skin_template_icons`,
declared in `assets/minecraft/atlases/items.json`) and an item model type
(`armorpieces:skin_template`) instead; between them they find every skin with a sheet, in any pack,
and give it its own icon. A skin whose art is missing falls back to the generic card.

Two escape hatches. Ship `textures/item/skin_template_<skin>.png` in your own namespace and that file
wins — a sprite source loses to a real texture of the same name — so a skin whose chest is a poor
summary of it can be given a hand-drawn icon. And the generic card itself is still authored:
`python tools/gen_template_icons.py` draws it with the twelve socket icons and the cloths, and
`--sheet` writes a magnified contact sheet of the lot.

Authoring is the same loop parts have, with its own tools: `python tools/skin_sheets.py <skin>`
prints a sheet as ASCII to work from (`--vanilla netherite` prints vanilla's own),
`python tools/bb_rig.py --skin <skin>` builds the Blockbench rig, the plugin's skin workspace paints
it on the real figure with a live material preview, `python tools/check_skin.py <skin>` is the check
every shipped skin passes, and `python tools/sync_skin_masters.py <skin> [--as <name>]` installs the
pair into the resources — which **the plugin's Save already does**, the way saving a part installs
its master, so this one is for a skin installed under another name or for reinstalling the lot.

**Wearing one.** Skin template + the armor + *the armor's own reforging material* — an iron ingot
for iron, a diamond for diamond, a turtle scute for the turtle helmet. Re-skinning is re-forging, so
it costs the metal the piece is made of; the mod does not keep a table of that, it asks the piece
what repairs it, which is right for armor it has never heard of. Leave the third slot empty and the
skin comes off. Armor listed in `#armorpieces:unskinnable_armor` refuses skins outright — vanilla
chainmail is in it, because the weave is its whole identity and it has no metal of its own.

## Cloths

A cloth is the fourth kind of template, and the last thing that can be said about one piece of
armor. A part is geometry hung on the body, a trim is vanilla's accent painted over the armor's
texture, a skin is the armor's own texture — and a **cloth is a garment worn over that texture**,
dyed and patterned at a loom.

It sits between the skin and the parts, which is where it sits on the body: over the plate, under
the trim's edge line, and under every part. That layering costs nothing, because a cloth is not a
new pass — it is *composited into the armor's own texture*, so it is the armor model. Which is also
why it moves correctly, clips nothing, and needs no rig.

What it cannot do is hang. A cloth is tight to the torso box: no hem past it, no flare, no side
slits that swing. A garment that hangs is geometry, which is a part — and a part cannot be under
anything or take the armor's shading. They are different features.

A cloth is **one greyscale mask, one data file and a recipe**:

    assets/<ns>/textures/entity/cloth/<cloth>/humanoid.png            64x32, on vanilla's armor grid
    data/<ns>/armorpieces/cloth/<cloth>.json                          asset_id, sheet, description, loot
    data/<ns>/recipe/cloth_template_<cloth>.json                      the ring of paper, as a part's is

```json
{
  "asset_id": "examplemod:surcoat",
  "sheet": "shield",
  "description": { "translate": "cloth.examplemod.surcoat" },
  "loot": [ { "table": "minecraft:chests/pillager_outpost", "weight": 2, "chance": 0.1 } ]
}
```

**It stops at the waist, and that is the model's word not the design's.** A chestplate's layer draws
three boxes - the torso and the two arms - and a texture can only paint texels that some box of its
own item samples. There is no geometry over the thigh in that layer, so there is nothing to paint: a
chestplate's garment ends where the chestplate ends.

A hem on the LEGGINGS' leg boxes was built and looked right - three to five rows read cleanly as
cloth hanging past the breastplate - and was cut, because it is not the chestplate's to draw. It
needs the garment applied to the leggings as well, which is a second smithing operation on a second
item for a few rows of cloth, and it makes "a piece half-wearing a garment" a thing a player can
have. The capability is still there for a pack that wants it: ship a `humanoid_leggings.png` mask,
add `#minecraft:leg_armor` to `armorpieces:clothable_armor`, and no code changes. Anything longer
than a few rows should not go there anyway - a leg box inflates 0.4 where the chest box inflates 1.0,
so the hem is thinner than the garment above it, and the legs are two boxes that swing apart, so a
long one splits down the middle at every step.

`check_authoring.py` refuses a cloth with no mask at all, which would be a garment the game puts on
a piece of armor and then draws nothing for.

### What the mask says

One sheet, three jobs at once:

- **Alpha is how far the garment reaches.** Where it is transparent, the armor is untouched. Reach
  generously: how far it *can* reach is the armor's to say — see below.
**The armor cuts the garment.** The mask says how far a cloth reaches; the armor says how far it
can. Where the piece being worn paints nothing, neither does the cloth — so the neck's notch, the
hem's taper and the bare shoulders come out of the piece itself rather than out of rows counted by
hand into a mask, and they are right on a skin's cut as readily as on vanilla's. Cut the mask
generously and let the armor trim it. It is the same image the lighting is measured from: the thing
the cloth is worn on.

The exception is a face the armor uses *nowhere*, which is not a hole to respect but room to use —
and on the torso box that means the top and the underside, since a breastplate has no lid. The
**top** is worth using: only its outer column each side is ever seen, the head covering the rest, and
that column is the shoulder line a tunic hangs from and a tabard'''s straps cross. The **underside** is
not: it is a horizontal plate at the waist, the full width of a box inflated past the body, and it
cuts straight through the legs at every step. Leave it empty, as vanilla does.

- **Value is the cloth's own form** — the folds, the shadow where it turns a corner, the dark band
  at the hem. 127 is the dye exactly; below goes toward black and above toward white, on the same
  three-stop ramp a dye fitting and a horn's ivory already use.
- **The two torso panels are where the design lands.** `chest.front` (20,20 8x12) and `chest.back`
  (32,20 8x12). Everywhere else the mask covers takes the base colour alone — the sides, the
  shoulders and the hem underside, which are four texels wide at most and could not carry a charge
  anyway.

Both panels get the design **the right way round**. A banner's back is mirrored because a banner is
one sheet of cloth read from behind; a tabard is two panels, each read from outside.

`sheet` chooses which of vanilla's two pattern sprite sets the panels sample — `shield` (12x22) or
`banner` (20x40) — the same choice `armorpieces:banner` offers. `shield` is the closer proportion to
an 8x12 panel and is the default.

**The colour comes from a banner, not from the cloth.** Nothing in your art is coloured. What the
armor supplies is neither the silhouette nor the colour but the **light**: the material's own
deviation from the middle of its range is added to your mask's value before the ramp is read, so
iron's studs and diamond's facets show *through* the garment, and a skinned piece's own form shows
instead when there is a skin. The bake runs at 256x128 so a charge has room, upsampling the armor's
own texels nearest so the plate still reads at vanilla resolution.

`python tools/preview_cloth.py` is the reference implementation of all of that and writes a contact
sheet of your garment in three designs on five materials — `--light 0` to see the pattern alone,
`--light 0.45` to see it overdone. `python tools/paint_cloth_masks.py` is how the two shipped masks
are cut, and reads its rectangles out of `skin_sheets.py` so a cut and a bake cannot disagree.

**The template's own icon draws itself**, as a skin's does, but from a different half of the art: a
skin is a surface, so its icon is a swatch of that surface; a cloth is a *shape*, so its icon is the
cut read off the same mask that ships, with the armor grey showing where the garment is not. A
tunic's collar gap and a tabard's open flanks are the whole difference between them and both are
visible at eight texels wide. `python tools/gen_template_icons.py` writes the icon, the item model
and the select for every cloth with art in the resources.

**Wearing one.** Cloth template + the armor + **a banner**. The addition slot names a material on
every other recipe in this mod; a cloth's colour is not a material, so here it means the design —
base colour and up to six layers, made at a loom, which is already the best pattern editor the game
has. The banner is consumed, as it is for a shield. Leave the third slot empty and the garment comes
off. What may wear one is `#armorpieces:clothable_armor`, which ships chest armor and nothing else.

## Judging the result in game

`/armorpieces stage` (permission level 2) puts a part next to the others on armor stands, read from
the registries, so a pack's parts appear alongside the shipped ones: `parts [<part>]` puts one stand
per part × material, `bases [<armor item>]` repeats that for every base armor set, `full` dresses
complete sets with every socket filled, `fittings [<part>]` shows every fitting filled with
everything it takes, one block per fitting with the part's materials down the rows,
`skins [<skin>]` puts every skin down the rows and every armor material across the columns — the
one view whose columns are the armor rather than the trim, because that is the axis a skin's colour
comes from — and `clear` removes them. `loot <table> [rolls]` is numbers rather than stands: it rolls the table, a
thousand times unless told otherwise, and counts what the mod put in it — templates by part,
decorated armor by what it wears — against everything else the table dropped, so a chance and a
weight can be judged without opening a thousand chests.

The loop between the editor and the game has one thing every author trips on once. Textures and
geometry are resources: F3+T reloads them, and the change is on the stand a moment after Save.
A change to the part's data file — its anchors, its fittings, its loot, a new part — is a change
to a dynamic registry, which the game reads once as a world opens, so it needs the world left and
re-entered; `/reload` is not enough. Recipes and loot tables do reload with `/reload`.
