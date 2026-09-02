# Authoring parts

A part is two files and a PNG, plus a line in your language file for the name. None of it is code.
Namespace them however you like; every namespace is scanned.

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

**Install.** Blockbench 5.1 or later, and Python 3 with Pillow on `PATH` (the same requirement
as every tool in the repository). In Blockbench: *File › Plugins › Load Plugin from File*, and pick
the file. It finds the repository from its own location; if the file was copied elsewhere, set
*Armor Pieces repository* in Settings to the repo root. The first piece opened extracts the
vanilla textures the rig needs from the game jar.

**Open a piece.** *Tools › Armor Pieces › Open Armor Piece…* lists every part in
`src/main/resources` and under `run/` — resource packs and world datapacks included — and opens
it as its own tab. *New Armor Piece…* writes the datapack entry, a starter model, a blank
texture and the language line, then opens that. A piece tab shows only what a part needs: Edit
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

**The part itself.** *Part…* opens the datapack half as a dialog: the name a player reads,
the sockets the part may occupy, ticked by armor piece, and its fittings as an ordered list
picked from every fitting definition in the pack and the mod — each shown with its kind, a
mask to paint or a bone to draw on. The panel follows at once: the Anchor list, the Fitting
list, the preview rows and the summary line. *New…* beside that list defines a fitting the
pack does not have yet: a material fitting over a trim-material tag or over ticked materials,
which are written as a tag in the pack so another pack can add to it; a dye fitting; or a
banner fitting on one of the part's own bones, with its pattern sheet and front face. The
definition, its language line and any tag are written the moment the dialog confirms, and
the fitting joins the part's list. Effects are rows on the same dialog: pick a built-in
type and its fields appear, with the ranges, defaults and descriptions read out of the Java
that defines it, and attribute, mob-effect and damage-tag ids autocompleting from the game.
Any row can be switched to run *only while* one of the part's fittings holds a chosen
material or dye, which is `armorpieces:if_fitting` written for you. An effect the dialog
cannot show — a type from another mod — is kept as it is and shown read-only.

**Modelling.** Model inside the `part` group; everything else is the locked reference. The
mod's format is box UV only, so the plugin keeps it that way: a cube added, converted or
resized is laid out in free space on the texture, the paint on its faces moves with them, and
the texture grows when it is full. All of that lands in the same undo step as the edit. Cubes
do not rotate — the mod's cube has no rotation — so a tilt is a rotated bone.

**Saving.** Save exports the geometry through `bb_geo.py`, writes the master, static layer and
masks back to their files, writes the template recipe, and — for a part whose master lives in
`tools/decoration_masters/` — runs `sync_decoration_masters.py`, which installs the sheets and
checks them against the geometry. When *Part…* changed something it also writes the data file
and the language line, and nothing else: a field the dialog has no control for, an effect say,
is written back exactly as it was read, a file nothing changed is not touched, and the recipe
keeps a `group` or any other field the two item choices do not decide.
`tools/check_authoring.py` runs the round trip over every shipped part.

**Starting from a rig.** Outside the plugin, authoring a part starts from a rig: each one holds
the vanilla body and all four armor layers at their real inflate, animated with the game's own walk
and sprint cycles, with an empty group sitting exactly where the layer will draw.
`python tools/bb_rig.py --all` regenerates them; the skin, armor and palette textures they
reference are extracted from the game jar by `tools/vanilla_assets.py` on first use and are never
committed. `bb_geo.py` converts `.bbmodel` to the mod's geometry and back.

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
  "materials": "#armorpieces:guard_metals" }
```

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
and so on — and `fitting_template` is the thirteenth, shared by every fitting.

**Overriding what this mod ships.** Same ids, your pack. A resource pack can restyle any part's
geometry or texture and a datapack can change where it may be worn.

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

## Judging the result in game

`/armorpieces stage` (permission level 2) puts a part next to the others on armor stands, read from
the registries, so a pack's parts appear alongside the shipped ones: `parts [<part>]` puts one stand
per part × material, `bases [<armor item>]` repeats that for every base armor set, `full` dresses
complete sets with every socket filled, `fittings [<part>]` shows every fitting filled with
everything it takes, one block per fitting with the part's materials down the rows, and `clear`
removes them.
