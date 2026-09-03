![Armor Pieces](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/banners/header.png)

*Decorative parts for armor — applied at a smithing table like trims, coloured by the same trim materials.*

[![GitHub release](https://img.shields.io/github/v/release/mattjesmc/ArmorPieces?style=for-the-badge&logo=github&logoColor=white&label=Release&color=5b21b6)](https://github.com/mattjesmc/ArmorPieces/releases/latest) ![Loaders](https://img.shields.io/badge/Loader-Fabric-5b21b6?style=for-the-badge) ![Minecraft versions](https://img.shields.io/badge/Minecraft-26.2-5b21b6?style=for-the-badge) [![License](https://img.shields.io/badge/License-All_Rights_Reserved-5b21b6?style=for-the-badge)](https://github.com/mattjesmc/ArmorPieces/blob/main/LICENSE)

**Loaders:** Fabric • **Minecraft:** 26.2 • **Side:** Client & Server

[GitHub](https://github.com/mattjesmc/ArmorPieces) • [Issues](https://github.com/mattjesmc/ArmorPieces/issues) • [Changelog](https://github.com/mattjesmc/ArmorPieces/blob/main/CHANGELOG.md)

---

## About

Armor Pieces adds **modular 3D pieces** to armor. A full set has twelve sockets - crest, brow,
horns, pauldrons, back, collar, vambraces, belt, tassets, knees, spurs, greaves - and each socket
holds one part: a plume on the helmet, spaulders on the shoulders, a sash on the belt, spurs on
the heels. Parts are real geometry hung on the body, not paint on the texture, and any combination
of them makes a set.

A part is applied at a smithing table like a trim, with a template and a trim material, and takes
that material's colour. It sits on top of whatever vanilla trim the armor has; neither replaces
the other.

Some parts have a **fitting** that is coloured separately: a gem set into the circlet, a metal
buckle and a dyed strap on the sash, a dyed inlay on the greaves, a banner's design on the back
banner. One more smithing step, with a template per fitting, and the item decides where it goes.

Parts are crafted, or found: every one ships in a few of the world's chests. An **advanced
smithing table** shows a whole set on a stand and takes a part off again, which the smithing
table cannot.

This version ships forty-one parts across the twelve sockets. Each is a datapack entry, a model and
a texture, no code, and a pack can add its own the same way - from Blockbench, in folders of its
own.

---

## Features

- **Twelve sockets, one part at a time** — `crest`, `brow`, `horns`, `pauldrons`, `back`, `collar`, `vambraces`, `belt`, `tassets`, `knees`, `spurs`, `greaves`. A socket holds one part, so a new crest replaces the crest — and with forty-one parts every socket has at least two to choose from. Seven of the sockets are mirrored pairs, so spaulders means both shoulders.
- **Coloured by vanilla trim materials** — One grayscale master per part is mapped onto each material's own palette at load time. A new trim material costs a part no new art at all.
- **Fittings** — A part can declare places for a second material — `gemstone`, `guard`, `inlay`, `banner` — and a fitting template sets one: gems and metals by trim material, inlays by dye, banners from a banner made at a loom. There is a template per fitting, each with its own look and recipe, and the template with the third slot empty takes its fitting out again. Fittings are data too — a pack's new fitting gets its template from a recipe — and an effect can be gated on one.
- **Found in the world** — Every shipped part turns up in a few of the world's chests — wings in end cities, horns in bastions, the circlet in ancient cities — and a part names its own tables in its data file, which the mod adds it to as they load, the one thing a datapack cannot do for itself. A loot function puts a part on a piece of armor a table drops, gem and all.
- **Taking parts off** — The advanced smithing table, crafted from a smithing table, an armor stand and two iron ingots, holds a whole set worn by a stand at once, lists each piece's sockets, and empties one with a click — the one way a part ever comes off. Its own template and material slots run the smithing table's recipes, with the result on the stand before it is paid for.
- **One smithing recipe per socket, forever** — The part rides on the template item as a component, so a pack hands out a template and needs no recipe of its own. And any recipe the mod ships can be switched off by overriding its file with `{"type": "armorpieces:disabled"}` — a part that is found rather than made, a server without fittings.
- **Optional behaviour** — A part may carry effects — attributes, mob effects, a projectile dodge, gliding — configured in the same JSON file. `pinions` is a cut-down elytra that actually flies.
- **A Blockbench plugin for making parts** — Opens a part on the vanilla player wearing real armor, walk cycle and all. Master, static layer and fitting masks are painted in place, any trim material previews live with its fittings filled or empty, the name, sockets, fittings, effects and loot are a dialog, and Save writes every file the pack needs — into your own datapack and resource pack, which it makes, finds and zips for you.

---

## Gallery

![Every socket filled — three sets, one per row, in all eleven trim materials](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/gallery/sets.png)

*Every socket filled — three sets, one per row, in all eleven trim materials*

![The front row up close; the horns keep their ivory through every material](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/gallery/row.png)

*The front row up close; the horns keep their ivory through every material*

![The same three rows from behind — wing roots, banner and pinions on the back socket](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/gallery/back.png)

*The same three rows from behind — wing roots, banner and pinions on the back socket*

![One circlet, seven gems — the fitting takes a second material](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/gallery/fittings.png)

*One circlet, seven gems — the fitting takes a second material*

---

## Recipes

| ![Crafting recipe for Advanced Smithing Table](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__advanced_smithing_table.png) | ![Smithing Decoration recipe for Apply Back](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_back.gif) | ![Smithing Decoration recipe for Apply Belt](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_belt.gif) |
| :---: | :---: | :---: |
| Advanced Smithing Table | Apply Back *(Smithing Decoration)* | Apply Belt *(Smithing Decoration)* |
| ![Smithing Decoration recipe for Apply Brow](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_brow.gif) | ![Smithing Decoration recipe for Apply Collar](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_collar.gif) | ![Smithing Decoration recipe for Apply Crest](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_crest.gif) |
| Apply Brow *(Smithing Decoration)* | Apply Collar *(Smithing Decoration)* | Apply Crest *(Smithing Decoration)* |
| ![Smithing Fitting recipe for Apply Fitting](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_fitting.gif) | ![Smithing Decoration recipe for Apply Greaves](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_greaves.gif) | ![Smithing Decoration recipe for Apply Horns](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_horns.gif) |
| Apply Fitting *(Smithing Fitting)* | Apply Greaves *(Smithing Decoration)* | Apply Horns *(Smithing Decoration)* |
| ![Smithing Decoration recipe for Apply Knees](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_knees.gif) | ![Smithing Decoration recipe for Apply Pauldrons](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_pauldrons.gif) | ![Smithing Decoration recipe for Apply Spurs](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_spurs.gif) |
| Apply Knees *(Smithing Decoration)* | Apply Pauldrons *(Smithing Decoration)* | Apply Spurs *(Smithing Decoration)* |
| ![Smithing Decoration recipe for Apply Tassets](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_tassets.gif) | ![Smithing Decoration recipe for Apply Vambraces](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_vambraces.gif) | ![Smithing Fitting recipe for Clear Fitting](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__clear_fitting.gif) |
| Apply Tassets *(Smithing Decoration)* | Apply Vambraces *(Smithing Decoration)* | Clear Fitting *(Smithing Fitting)* |
| ![Crafting recipe for Fitting Template Banner](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__fitting_template_banner.png) | ![Crafting recipe for Fitting Template Gemstone](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__fitting_template_gemstone.png) | ![Crafting recipe for Fitting Template Guard](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__fitting_template_guard.png) |
| Fitting Template Banner | Fitting Template Gemstone | Fitting Template Guard |
| ![Crafting recipe for Fitting Template Inlay](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__fitting_template_inlay.gif) | ![Crafting recipe for Template Antennae](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_antennae.png) | ![Crafting recipe for Template Antlers](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_antlers.png) |
| Fitting Template Inlay | Template Antennae | Template Antlers |
| ![Crafting recipe for Template Bandolier](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_bandolier.png) | ![Crafting recipe for Template Banner](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_banner.png) | ![Crafting recipe for Template Beast Head](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_beast_head.png) |
| Template Bandolier | Template Banner | Template Beast Head |
| ![Crafting recipe for Template Brooch](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_brooch.png) | ![Crafting recipe for Template Brush Crest](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_brush_crest.png) | ![Crafting recipe for Template Buckled Belt](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_buckled_belt.png) |
| Template Brooch | Template Brush Crest | Template Buckled Belt |
| ![Crafting recipe for Template Chain Of Office](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_chain_of_office.png) | ![Crafting recipe for Template Circlet](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_circlet.png) | ![Crafting recipe for Template Claws](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_claws.png) |
| Template Chain Of Office | Template Circlet | Template Claws |
| ![Crafting recipe for Template Coronet](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_coronet.png) | ![Crafting recipe for Template Feathering](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_feathering.png) | ![Crafting recipe for Template Garters](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_garters.png) |
| Template Coronet | Template Feathering | Template Garters |
| ![Crafting recipe for Template Gorget](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_gorget.png) | ![Crafting recipe for Template Greaves](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_greaves.png) | ![Crafting recipe for Template Head Fins](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_head_fins.png) |
| Template Gorget | Template Greaves | Template Head Fins |
| ![Crafting recipe for Template Heel Wings](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_heel_wings.png) | ![Crafting recipe for Template Helm Wings](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_helm_wings.png) | ![Crafting recipe for Template Horns](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_horns.png) |
| Template Heel Wings | Template Helm Wings | Template Horns |
| ![Crafting recipe for Template Horsetail](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_horsetail.png) | ![Crafting recipe for Template Mantle](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_mantle.png) | ![Crafting recipe for Template Mittens](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_mittens.png) |
| Template Horsetail | Template Mantle | Template Mittens |
| ![Crafting recipe for Template Nasal](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_nasal.png) | ![Crafting recipe for Template Pelt](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_pelt.png) | ![Crafting recipe for Template Pinions](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_pinions.png) |
| Template Nasal | Template Pelt | Template Pinions |
| ![Crafting recipe for Template Poleyns](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_poleyns.png) | ![Crafting recipe for Template Puttees](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_puttees.png) | ![Crafting recipe for Template Quiver](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_quiver.png) |
| Template Poleyns | Template Puttees | Template Quiver |
| ![Crafting recipe for Template Sash](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_sash.png) | ![Crafting recipe for Template Scale Shins](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_scale_shins.png) | ![Crafting recipe for Template Scale Skirt](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_scale_skirt.png) |
| Template Sash | Template Scale Shins | Template Scale Skirt |
| ![Crafting recipe for Template Spaulders](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_spaulders.png) | ![Crafting recipe for Template Spire](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_spire.png) | ![Crafting recipe for Template Spurs](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_spurs.png) |
| Template Spaulders | Template Spire | Template Spurs |
| ![Crafting recipe for Template Streamers](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_streamers.png) | ![Crafting recipe for Template Tassets](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_tassets.png) | ![Crafting recipe for Template Vambraces](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_vambraces.png) |
| Template Streamers | Template Tassets | Template Vambraces |
| ![Crafting recipe for Template Visor](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_visor.png) | ![Crafting recipe for Template Wing Roots](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_wing_roots.png) | ![Crafting recipe for Template Wraps](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_wraps.png) |
| Template Visor | Template Wing Roots | Template Wraps |

---

## Dependencies

**Required**

| Mod | Version | Notes |
| --- | --- | --- |
| [Fabric API](https://modrinth.com/mod/fabric-api) | — | Dynamic registries, resource reload, render layers |

---

## Incompatibilities

**None known.** No conflicts have been reported.

---

## Installation

1. Install [Fabric Loader](https://fabricmc.net/use/) 0.19.3+ on Minecraft 26.2 (Java 25).
2. Drop this mod and Fabric API into `mods/`.
3. Install it on both sides — the client draws the parts, the server owns their behaviour.

---

## Adding a part

A part is two files and a PNG, plus a line in your language file for the name — none of it
code, and any namespace will do. Two ways to make them:

- **In Blockbench**, with the [Armor Pieces plugin](https://github.com/mattjesmc/ArmorPieces/blob/main/tools/blockbench_plugin/armorpieces.js). It opens a part on the vanilla
  player wearing real armor, paints the textures in place, previews any trim material, and
  writes every file on Save.
- **By hand**, writing the datapack entry, the geometry and the grayscale master yourself.

The [authoring guide](https://github.com/mattjesmc/ArmorPieces/blob/main/docs/authoring.md) covers both, along with fittings, handing a part out, and giving
it behaviour — attributes, mob effects, a dodge, gliding — from the same JSON file.

---

## Working on it

`./gradlew build`, `./gradlew runClient`, `./gradlew runServer`.

| Where | What |
| --- | --- |
| `decoration/` | anchors, the datapack registry entry, the item component, the effect hooks |
| `client/` | the render layer, the geometry loader and bake cache, the per-material palette |
| `recipe/`, `item/`, `registry/`, `command/` | smithing, the twelve socket templates and the fitting template, the creative tab, `/armorpieces stage` |
| `loot/`, `block/`, `menu/` | parts in loot tables and the `set_decoration` function; the advanced smithing table and its menu |
| `tools/` | Blockbench rigs (`bb_rig.py`, with the vanilla figure and walk cycle from `mc_humanoid.py`), `.bbmodel` ↔ geometry (`bb_geo.py`), master and mask painting and install (`paint_<part>_master.py`, `fitting_mask.py`, `sync_decoration_masters.py`), a material and fitting preview outside the game (`preview_material.py`), template and recipe icons, `export_pack.py` for zipping a pack, `trace_geometry.py` for measuring a part against the body |
| `tools/blockbench_plugin/` | the Blockbench plugin — see the [authoring guide](https://github.com/mattjesmc/ArmorPieces/blob/main/docs/authoring.md) |
| `tools/decoration_masters/` | the grayscale masters — the source of truth for every part's art |

The rigs, the `/armorpieces stage` command and the plugin's Save path are described in the
[authoring guide](https://github.com/mattjesmc/ArmorPieces/blob/main/docs/authoring.md); `tools/check_authoring.py` runs the plugin's round trip over every
shipped part.

---

## FAQ

**Does a part replace the armor trim?**

No. A piece carries its trim and its parts at once.

**How do I put a gem in the circlet?**

Craft a gemstone fitting template (an amethyst block in a ring of paper), then smithing table: template, the decorated helmet, and the gem. Every part on the piece is offered the item, so one gem fills the stone of each part that has one. The same template with the third slot empty takes the gem out again. A guard template does the same for metals, an inlay template for dyes, a banner template for banners. Re-applying a part at its own socket template keeps what is set in it, so changing a circlet's metal does not cost the gem.

**How do I take a part off?**

At the advanced smithing table. Put the piece in one of its four slots, pick the socket in the list and click the cross. What was in the part's fittings goes with it.

**Can two parts share a socket?**

No — applying a new crest replaces the crest. Several parts may be *available* for one socket (`horns` and `helm_wings` both fit `horns`); the choice is the expressive act.

**Do I need the mod to add parts?**

You need the mod installed, but adding a part takes no Java — a datapack and a resource pack. Only a brand-new *effect* type needs code. The [authoring guide](https://github.com/mattjesmc/ArmorPieces/blob/main/docs/authoring.md) walks through it.

---

## License

Released under a custom license — see
[LICENSE](https://github.com/mattjesmc/ArmorPieces/blob/main/LICENSE).

Use it, play with it, and modify it for yourself: no permission needed, no fee. **Redistribution
needs written permission first.** That covers re-uploading the jar or the pack zips, mirroring
them, and bundling the mod in a modpack, server pack or launcher — paid or not — as well as
publishing a fork. Linking to an official download page never needs permission.

Ask on the [issue tracker](https://github.com/mattjesmc/ArmorPieces/issues); permission is given
in writing and covers the distribution it describes.

---

Every part in this mod is the same two files and a PNG a pack of your own would write.
