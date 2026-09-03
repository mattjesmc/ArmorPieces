<p align="center">
  <img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/banners/header.png" alt="Armor Pieces">
</p>

<p align="center"><i>Decorative parts for armor — applied at a smithing table like trims, coloured by the same trim materials.</i></p>

<p align="center">
  <a href="https://github.com/mattjesmc/ArmorPieces/releases/latest"><img alt="GitHub release" src="https://img.shields.io/github/v/release/mattjesmc/ArmorPieces?style=for-the-badge&logo=github&logoColor=white&label=Release&color=5b21b6"></a>
  <img alt="Loaders" src="https://img.shields.io/badge/Loader-Fabric-5b21b6?style=for-the-badge">
  <img alt="Minecraft versions" src="https://img.shields.io/badge/Minecraft-26.2-5b21b6?style=for-the-badge">
  <a href="https://github.com/mattjesmc/ArmorPieces/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/License-All_Rights_Reserved-5b21b6?style=for-the-badge"></a>
</p>

<p align="center">
<b>Loaders:</b> Fabric &nbsp;•&nbsp; <b>Minecraft:</b> 26.2 &nbsp;•&nbsp; <b>Side:</b> Client & Server
</p>

---
<a id="about"></a>

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
<a id="features"></a>

## Features

- **Twelve sockets, one part at a time** — `crest`, `brow`, `horns`, `pauldrons`, `back`, `collar`, `vambraces`, `belt`, `tassets`, `knees`, `spurs`, `greaves`. A socket holds one part, so a new crest replaces the crest — and with forty-one parts every socket has at least two to choose from. Seven of the sockets are mirrored pairs, so spaulders means both shoulders.
- **Coloured by vanilla trim materials** — One grayscale master per part is mapped onto each material's own palette at load time. A new trim material costs a part no new art at all.
- **Fittings** — A part can declare places for a second material — `gemstone`, `guard`, `inlay`, `banner` — and a fitting template sets one: gems and metals by trim material, inlays by dye, banners from a banner made at a loom. There is a template per fitting, each with its own look and recipe, and the template with the third slot empty takes its fitting out again. Fittings are data too — a pack's new fitting gets its template from a recipe — and an effect can be gated on one.
- **Found in the world** — Every shipped part turns up in a few of the world's chests — wings in end cities, horns in bastions, the circlet in ancient cities — and a part names its own tables in its data file, which the mod adds it to as they load, the one thing a datapack cannot do for itself. A loot function puts a part on a piece of armor a table drops, gem and all.
- **Taking parts off** — The advanced smithing table, crafted from a smithing table, an armor stand and two iron ingots, holds a whole set worn by a stand at once and lists each piece's sockets, its fittings and its trim as rows of icons. Pick one and Remove empties it — the one way a part, a fitting or a trim ever comes off. Its own template and material slots run the smithing table's recipes, with the result on the stand before it is paid for, and a fitting goes into the socket that is picked rather than into every part that takes one.
- **One smithing recipe per socket, forever** — The part rides on the template item as a component, so a pack hands out a template and needs no recipe of its own. And any recipe the mod ships can be switched off by overriding its file with `{"type": "armorpieces:disabled"}` — a part that is found rather than made, a server without fittings.
- **Optional behaviour** — A part may carry effects — attributes, mob effects, a projectile dodge, gliding — configured in the same JSON file. `pinions` is a cut-down elytra that actually flies.
- **A Blockbench plugin for making parts** — Opens a part on the vanilla player wearing real armor, walk cycle and all. Master, static layer and fitting masks are painted in place, any trim material previews live with its fittings filled or empty, the name, sockets, fittings, effects and loot are a dialog, and Save writes every file the pack needs — into your own datapack and resource pack, which it makes, finds and zips for you.

---
<a id="gallery"></a>

## Gallery

<p align="center">
  <img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/gallery/sets.png" alt="Every socket filled — three sets, one per row, in all eleven trim materials">
  <br><sub><i>Every socket filled — three sets, one per row, in all eleven trim materials</i></sub>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/gallery/row.png" alt="The front row up close; the horns keep their ivory through every material">
  <br><sub><i>The front row up close; the horns keep their ivory through every material</i></sub>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/gallery/back.png" alt="The same three rows from behind — wing roots, banner and pinions on the back socket">
  <br><sub><i>The same three rows from behind — wing roots, banner and pinions on the back socket</i></sub>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/gallery/fittings.png" alt="One circlet, seven gems — the fitting takes a second material">
  <br><sub><i>One circlet, seven gems — the fitting takes a second material</i></sub>
</p>

---
<a id="recipes"></a>

## Recipes

<details>
<summary><b>Every recipe in the mod</b></summary>

<table>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__advanced_smithing_table.png" alt="Crafting recipe for Advanced Smithing Table"><br><sub>Advanced Smithing Table</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_back.gif" alt="Smithing Decoration recipe for Apply Back"><br><sub>Apply Back <i>(Smithing Decoration)</i></sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_belt.gif" alt="Smithing Decoration recipe for Apply Belt"><br><sub>Apply Belt <i>(Smithing Decoration)</i></sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_brow.gif" alt="Smithing Decoration recipe for Apply Brow"><br><sub>Apply Brow <i>(Smithing Decoration)</i></sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_collar.gif" alt="Smithing Decoration recipe for Apply Collar"><br><sub>Apply Collar <i>(Smithing Decoration)</i></sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_crest.gif" alt="Smithing Decoration recipe for Apply Crest"><br><sub>Apply Crest <i>(Smithing Decoration)</i></sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_fitting.gif" alt="Smithing Fitting recipe for Apply Fitting"><br><sub>Apply Fitting <i>(Smithing Fitting)</i></sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_greaves.gif" alt="Smithing Decoration recipe for Apply Greaves"><br><sub>Apply Greaves <i>(Smithing Decoration)</i></sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_horns.gif" alt="Smithing Decoration recipe for Apply Horns"><br><sub>Apply Horns <i>(Smithing Decoration)</i></sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_knees.gif" alt="Smithing Decoration recipe for Apply Knees"><br><sub>Apply Knees <i>(Smithing Decoration)</i></sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_pauldrons.gif" alt="Smithing Decoration recipe for Apply Pauldrons"><br><sub>Apply Pauldrons <i>(Smithing Decoration)</i></sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_spurs.gif" alt="Smithing Decoration recipe for Apply Spurs"><br><sub>Apply Spurs <i>(Smithing Decoration)</i></sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_tassets.gif" alt="Smithing Decoration recipe for Apply Tassets"><br><sub>Apply Tassets <i>(Smithing Decoration)</i></sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_vambraces.gif" alt="Smithing Decoration recipe for Apply Vambraces"><br><sub>Apply Vambraces <i>(Smithing Decoration)</i></sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__clear_fitting.gif" alt="Smithing Fitting recipe for Clear Fitting"><br><sub>Clear Fitting <i>(Smithing Fitting)</i></sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__fitting_template_banner.png" alt="Crafting recipe for Fitting Template Banner"><br><sub>Fitting Template Banner</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__fitting_template_gemstone.png" alt="Crafting recipe for Fitting Template Gemstone"><br><sub>Fitting Template Gemstone</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__fitting_template_guard.png" alt="Crafting recipe for Fitting Template Guard"><br><sub>Fitting Template Guard</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__fitting_template_inlay.gif" alt="Crafting recipe for Fitting Template Inlay"><br><sub>Fitting Template Inlay</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_aerials.png" alt="Crafting recipe for Template Aerials"><br><sub>Template Aerials</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_anklets.png" alt="Crafting recipe for Template Anklets"><br><sub>Template Anklets</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_antennae.png" alt="Crafting recipe for Template Antennae"><br><sub>Template Antennae</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_antlers.png" alt="Crafting recipe for Template Antlers"><br><sub>Template Antlers</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_bandolier.png" alt="Crafting recipe for Template Bandolier"><br><sub>Template Bandolier</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_bangles.png" alt="Crafting recipe for Template Bangles"><br><sub>Template Bangles</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_banner.png" alt="Crafting recipe for Template Banner"><br><sub>Template Banner</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_beast_head.png" alt="Crafting recipe for Template Beast Head"><br><sub>Template Beast Head</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_bedroll.png" alt="Crafting recipe for Template Bedroll"><br><sub>Template Bedroll</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_bells.png" alt="Crafting recipe for Template Bells"><br><sub>Template Bells</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_bone_mask.png" alt="Crafting recipe for Template Bone Mask"><br><sub>Template Bone Mask</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_boot_cuffs.png" alt="Crafting recipe for Template Boot Cuffs"><br><sub>Template Boot Cuffs</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_brooch.png" alt="Crafting recipe for Template Brooch"><br><sub>Template Brooch</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_browband.png" alt="Crafting recipe for Template Browband"><br><sub>Template Browband</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_brush_crest.png" alt="Crafting recipe for Template Brush Crest"><br><sub>Template Brush Crest</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_buckled_belt.png" alt="Crafting recipe for Template Buckled Belt"><br><sub>Template Buckled Belt</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_buckler.png" alt="Crafting recipe for Template Buckler"><br><sub>Template Buckler</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_carapace.png" alt="Crafting recipe for Template Carapace"><br><sub>Template Carapace</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_chain_belt.png" alt="Crafting recipe for Template Chain Belt"><br><sub>Template Chain Belt</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_chain_of_office.png" alt="Crafting recipe for Template Chain Of Office"><br><sub>Template Chain Of Office</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_cheek_guards.png" alt="Crafting recipe for Template Cheek Guards"><br><sub>Template Cheek Guards</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_circlet.png" alt="Crafting recipe for Template Circlet"><br><sub>Template Circlet</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_claws.png" alt="Crafting recipe for Template Claws"><br><sub>Template Claws</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_cloak.png" alt="Crafting recipe for Template Cloak"><br><sub>Template Cloak</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_comb.png" alt="Crafting recipe for Template Comb"><br><sub>Template Comb</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_cord.png" alt="Crafting recipe for Template Cord"><br><sub>Template Cord</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_coronet.png" alt="Crafting recipe for Template Coronet"><br><sub>Template Coronet</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_cuffs.png" alt="Crafting recipe for Template Cuffs"><br><sub>Template Cuffs</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_dorsal_fin.png" alt="Crafting recipe for Template Dorsal Fin"><br><sub>Template Dorsal Fin</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_ears.png" alt="Crafting recipe for Template Ears"><br><sub>Template Ears</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_epaulettes.png" alt="Crafting recipe for Template Epaulettes"><br><sub>Template Epaulettes</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_fang_necklace.png" alt="Crafting recipe for Template Fang Necklace"><br><sub>Template Fang Necklace</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_fanged_cop.png" alt="Crafting recipe for Template Fanged Cop"><br><sub>Template Fanged Cop</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_fauld.png" alt="Crafting recipe for Template Fauld"><br><sub>Template Fauld</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_feathering.png" alt="Crafting recipe for Template Feathering"><br><sub>Template Feathering</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_garters.png" alt="Crafting recipe for Template Garters"><br><sub>Template Garters</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_girdle.png" alt="Crafting recipe for Template Girdle"><br><sub>Template Girdle</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_gorget.png" alt="Crafting recipe for Template Gorget"><br><sub>Template Gorget</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_greaves.png" alt="Crafting recipe for Template Greaves"><br><sub>Template Greaves</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_head_fins.png" alt="Crafting recipe for Template Head Fins"><br><sub>Template Head Fins</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_heel_wings.png" alt="Crafting recipe for Template Heel Wings"><br><sub>Template Heel Wings</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_helm_wings.png" alt="Crafting recipe for Template Helm Wings"><br><sub>Template Helm Wings</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_horns.png" alt="Crafting recipe for Template Horns"><br><sub>Template Horns</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_horsetail.png" alt="Crafting recipe for Template Horsetail"><br><sub>Template Horsetail</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_knee_studs.png" alt="Crafting recipe for Template Knee Studs"><br><sub>Template Knee Studs</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_lames.png" alt="Crafting recipe for Template Lames"><br><sub>Template Lames</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_laurel.png" alt="Crafting recipe for Template Laurel"><br><sub>Template Laurel</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_loin_panels.png" alt="Crafting recipe for Template Loin Panels"><br><sub>Template Loin Panels</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_mail_fringe.png" alt="Crafting recipe for Template Mail Fringe"><br><sub>Template Mail Fringe</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_mantle.png" alt="Crafting recipe for Template Mantle"><br><sub>Template Mantle</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_mittens.png" alt="Crafting recipe for Template Mittens"><br><sub>Template Mittens</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_nasal.png" alt="Crafting recipe for Template Nasal"><br><sub>Template Nasal</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_padding.png" alt="Crafting recipe for Template Padding"><br><sub>Template Padding</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_pelt.png" alt="Crafting recipe for Template Pelt"><br><sub>Template Pelt</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_pendant.png" alt="Crafting recipe for Template Pendant"><br><sub>Template Pendant</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_pinions.png" alt="Crafting recipe for Template Pinions"><br><sub>Template Pinions</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_poleyns.png" alt="Crafting recipe for Template Poleyns"><br><sub>Template Poleyns</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_pouch_belt.png" alt="Crafting recipe for Template Pouch Belt"><br><sub>Template Pouch Belt</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_puttees.png" alt="Crafting recipe for Template Puttees"><br><sub>Template Puttees</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_quiver.png" alt="Crafting recipe for Template Quiver"><br><sub>Template Quiver</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_rowel_spurs.png" alt="Crafting recipe for Template Rowel Spurs"><br><sub>Template Rowel Spurs</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_ruff.png" alt="Crafting recipe for Template Ruff"><br><sub>Template Ruff</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_sash.png" alt="Crafting recipe for Template Sash"><br><sub>Template Sash</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_scale_shins.png" alt="Crafting recipe for Template Scale Shins"><br><sub>Template Scale Shins</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_scale_skirt.png" alt="Crafting recipe for Template Scale Skirt"><br><sub>Template Scale Skirt</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_scarf.png" alt="Crafting recipe for Template Scarf"><br><sub>Template Scarf</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_shin_spikes.png" alt="Crafting recipe for Template Shin Spikes"><br><sub>Template Shin Spikes</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_spaulders.png" alt="Crafting recipe for Template Spaulders"><br><sub>Template Spaulders</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_spiked_pauldrons.png" alt="Crafting recipe for Template Spiked Pauldrons"><br><sub>Template Spiked Pauldrons</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_spine_ridge.png" alt="Crafting recipe for Template Spine Ridge"><br><sub>Template Spine Ridge</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_spire.png" alt="Crafting recipe for Template Spire"><br><sub>Template Spire</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_spurs.png" alt="Crafting recipe for Template Spurs"><br><sub>Template Spurs</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_streamers.png" alt="Crafting recipe for Template Streamers"><br><sub>Template Streamers</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_swim_fins.png" alt="Crafting recipe for Template Swim Fins"><br><sub>Template Swim Fins</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_talons.png" alt="Crafting recipe for Template Talons"><br><sub>Template Talons</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_tassets.png" alt="Crafting recipe for Template Tassets"><br><sub>Template Tassets</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_thigh_sheath.png" alt="Crafting recipe for Template Thigh Sheath"><br><sub>Template Thigh Sheath</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_tusks.png" alt="Crafting recipe for Template Tusks"><br><sub>Template Tusks</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_vambraces.png" alt="Crafting recipe for Template Vambraces"><br><sub>Template Vambraces</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_visor.png" alt="Crafting recipe for Template Visor"><br><sub>Template Visor</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_wing_cases.png" alt="Crafting recipe for Template Wing Cases"><br><sub>Template Wing Cases</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_wing_roots.png" alt="Crafting recipe for Template Wing Roots"><br><sub>Template Wing Roots</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_winged_cops.png" alt="Crafting recipe for Template Winged Cops"><br><sub>Template Winged Cops</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_wraps.png" alt="Crafting recipe for Template Wraps"><br><sub>Template Wraps</sub></td>
</tr>
</table>

</details>

---
<a id="dependencies"></a>

## Dependencies

**Required**

| Mod | Version | Notes |
| --- | --- | --- |
| [Fabric API](https://modrinth.com/mod/fabric-api) | — | Dynamic registries, resource reload, render layers |

---
<a id="incompatibilities"></a>

## Incompatibilities

**None known.** No conflicts have been reported.

---
<a id="installation"></a>

## Installation

1. Install [Fabric Loader](https://fabricmc.net/use/) 0.19.3+ on Minecraft 26.2 (Java 25).
2. Drop this mod and Fabric API into `mods/`.
3. Install it on both sides — the client draws the parts, the server owns their behaviour.

---
<a id="adding-a-part"></a>

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
<a id="working-on-it"></a>

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
<a id="faq"></a>

## FAQ

**Does a part replace the armor trim?**

No. A piece carries its trim and its parts at once.

**How do I put a gem in the circlet?**

Craft a gemstone fitting template (an amethyst block in a ring of paper), then smithing table: template, the decorated helmet, and the gem. Every part on the piece is offered the item, so one gem fills the stone of each part that has one — or of the one socket picked, at the advanced smithing table. The same template with the third slot empty takes the gem out again. A guard template does the same for metals, an inlay template for dyes, a banner template for banners. Re-applying a part at its own socket template keeps what is set in it, so changing a circlet's metal does not cost the gem.

**How do I take a part off?**

At the advanced smithing table. Put the piece in one of its four slots, pick the socket's row and click Remove. What was in the part's fittings goes with it. Picking one of the fitting icons beside the part takes just that fitting out, and the trim row under the sockets takes the trim off.

**Can two parts share a socket?**

No — applying a new crest replaces the crest. Several parts may be *available* for one socket (`horns` and `helm_wings` both fit `horns`); the choice is the expressive act.

**Do I need the mod to add parts?**

You need the mod installed, but adding a part takes no Java — a datapack and a resource pack. Only a brand-new *effect* type needs code. The [authoring guide](https://github.com/mattjesmc/ArmorPieces/blob/main/docs/authoring.md) walks through it.

---
<a id="license"></a>

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
