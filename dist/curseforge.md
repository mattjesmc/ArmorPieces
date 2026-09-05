![Armor Pieces](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/banners/header.png)

*Parts, skins and cloth for armor — because someone else at spawn is wearing your diamond set.*

[![GitHub release](https://img.shields.io/github/v/release/mattjesmc/ArmorPieces?style=for-the-badge&logo=github&logoColor=white&label=Release&color=5b21b6)](https://github.com/mattjesmc/ArmorPieces/releases/latest) ![Loaders](https://img.shields.io/badge/Loader-Fabric-5b21b6?style=for-the-badge) ![Minecraft versions](https://img.shields.io/badge/Minecraft-26.2-5b21b6?style=for-the-badge) [![License](https://img.shields.io/badge/License-All_Rights_Reserved-5b21b6?style=for-the-badge)](https://github.com/mattjesmc/ArmorPieces/blob/main/LICENSE)

**Loaders:** Fabric • **Minecraft:** 26.2 • **Side:** Client & Server

[GitHub](https://github.com/mattjesmc/ArmorPieces) • [Issues](https://github.com/mattjesmc/ArmorPieces/issues) • [Changelog](https://github.com/mattjesmc/ArmorPieces/blob/main/CHANGELOG.md)

---

## About

You know the one. You walk into spawn in your best diamond and the first person you see is
wearing the same helmet, the same chestplate, the same Sentry trim in the same netherite. Vanilla
can build 1,568,239,201 armor sets, which sounds like plenty right up until it happens to you
twice in a week.

Armor Pieces takes that number to **3 × 10⁸⁴** — more than thirty thousand unique diamond sets
for every atom in the observable universe. Diamond is one of seven armor materials.

It gives one piece of armor **four layers of decoration, each an independent choice**:
a **part** hung on a socket, a **skin** that changes what the plate itself is made of, a **cloth**
worn over the chest, and vanilla's own **trim** underneath them all. Every one of them is applied
at a smithing table, and none of them replaces another - a helmet can carry a skin, a trim, a
crest, a browband and a pair of horns at once.

**Ninety-one parts, over twelve sockets.** `crest`, `brow`, `horns`, `pauldrons`, `back`,
`collar`, `vambraces`, `belt`, `tassets`, `knees`, `spurs`, `greaves` - a plume on the helmet,
spaulders on the shoulders, a sash on the belt, spurs on the heels. Parts are real geometry hung
on the body, not paint on the texture. A socket holds one part and every socket has at least six
to choose from, so the choice is the expressive act. Each part is applied with a trim material and
takes that material's colour.

**Fourteen armor skins.** A skin is the armor's *own* texture - what the plate is, rather than
what is bolted to it. Plate, gothic, milanese, mail, chainmail, lorica, runic, hoplite, samurai,
gambeson, brigandine, varangian, scale and lamellar. Each is recoloured through the armor
material's own palette, so a skinned iron helmet still reads as iron and a modded armor material
is skinned for free from the texture it already ships. A skin is paid for in the metal the piece
is made of: re-skinning is re-forging.

**Two cloths.** A tunic or a tabard over a chestplate, carrying the design of any banner you make
at a loom - so the heraldry is yours rather than a list the mod maintains. It is baked into the
armor's texture rather than hung off it, so it clips nothing and the plate's own rivets and edges
read through it.

**Fittings.** Some parts have a second colour, set separately: a gem in the circlet, a metal
buckle and a dyed strap on the sash, a dyed inlay on the greaves, a banner on the back banner.
One more smithing step, one template per fitting, and the item decides where it goes.

Most of it is **found rather than made**. Thirty parts have a crafting recipe, the ones where
the item is plainly the part or what it is made of; the rest turn up in the chests that suit them,
each theme in its own kind of structure, with the skins and the fitting templates alongside. An
**advanced smithing table** shows a whole set worn by a stand and takes a part, a fitting or a
trim off again, which the smithing table cannot.

Every part, skin and cloth is a datapack entry, a model and a texture, no code - and a pack adds
its own the same way, from Blockbench, in folders of its own.

---

## New in 0.3.0

The release that turned a set of parts into a wardrobe.

- **Seventy-one new parts — ninety-one in total.** Every one of the twelve sockets now has at
  least six answers, and the six themes reach across the whole suit. Among them a family of
  seven flat **visor styles** on the `brow` socket, whose sights are real openings with your
  own face behind them rather than paint.
- **Armor skins.** A third template family, and the first thing in the mod that changes the
  armor itself instead of adding to it. Fourteen ship, each recoloured through the armor
  material's own vanilla palette, so a skin costs no per-material art and a modded material
  gets one free.
- **Cloth.** A fourth layer: a **Tunic** or a **Tabard** over a chestplate, wearing the design
  of any banner you make at a loom, painted into the armor's texture rather than hung off it.
- **Most parts are now found rather than crafted.** A **loot group** is one file naming a
  category of vanilla tables and a tag of parts found in them; six ship, one per theme —
  knightly gear in strongholds and trial chambers, beast trophies in bastions, court jewellery
  in mansions and ancient cities, tidal parts in shipwrecks and ocean ruins, and so on. Skins
  are divided over the same six, and a fitting template turns up in all of them.
- **The chance belongs to the table, not to the part.** One pool per table, rolled once: a
  chest's odds of holding something of ours stay put however many parts are added. Another part
  changes *which* one you find, never how often.
- **The advanced smithing table.** Crafted from a smithing table, an armor stand and two iron
  ingots. It holds a whole set worn by a stand and lists each piece's sockets, fittings and trim
  as rows of icons — and Remove is the one way a part, a fitting or a trim ever comes off.
- **Thirty recipes, not ninety-one.** A template recipe now ships only where the centre
  item is plainly the part or what it is made of — a bell for the bells, a goat horn for the
  horns. The rest are found.
- **One template per fitting.** *Gemstone*, *Guard*, *Inlay* and *Banner*, each with its own
  look, name and recipe, instead of one template that guessed.
- **Any recipe the mod ships can be switched off** by overriding its file with
  `{"type": "armorpieces:disabled"}`.
- **Parts on the first-person hand.** Vanilla shows a bare sleeve there and no armor at all;
  pauldrons and vambraces now ride the hand you actually spend the game looking at.
  `first_person_parts` in `config/armorpieces.json` turns it off — the mod's first setting.
- **Blockbench, for your pack.** The plugin no longer assumes content lives in this repository:
  it opens a part on the vanilla player wearing real armor, paints master, static layer and
  fitting masks in place, previews any trim material live, and on Save writes every file into
  *your* datapack and resource pack — which it makes, finds and zips for you.

---

## Features

- **Twelve sockets, one part at a time** — `crest`, `brow`, `horns`, `pauldrons`, `back`, `collar`, `vambraces`, `belt`, `tassets`, `knees`, `spurs`, `greaves`. A socket holds one part, so a new crest replaces the crest — and with ninety-one parts every socket has at least six to choose from. Seven of the sockets are mirrored pairs, so spaulders means both shoulders.
- **Coloured by vanilla trim materials** — One grayscale master per part is mapped onto each material's own palette at load time. A new trim material costs a part no new art at all.
- **On your own hands, in first person** — Vanilla draws a bare sleeve on the first-person hand and nothing else — not armor, not a trim — so the one view you spend the whole game in is the one that never showed what you were wearing. Pauldrons and vambraces show there now, on the same player model the world sees, swinging with the arm through every animation the hand already has. They are close to the camera and they are meant to be: set `first_person_parts` to `false` in `config/armorpieces.json` if you would rather keep the view clear.
- **Fourteen armor skins** — The one thing here that changes the armor itself rather than adding to it — plate, gothic, milanese, mail, chainmail, lorica, runic, hoplite, samurai, gambeson, brigandine, varangian, scale, lamellar. One greyscale master pair on vanilla's own armor grid, recoloured at load through eight shades taken from *that armor material's* vanilla texture, with vanilla's own panel edges and shadows mixed back over it. A skinned iron helmet still reads as iron, gold still reads as gold, and a modded armor material is skinned for free from the texture it already ships. Applied at the advanced smithing table with the piece's own reforging material — re-skinning is re-forging, and it costs the metal the piece is made of.
- **Cloth over the chest** — A **Tunic** or a **Tabard**, applied with a cloth template and a banner, and the design is the banner's — sixteen dyes crossed with every pattern layer, made at a loom, so the heraldry is a player's choice rather than a list the mod keeps. It is painted into the armor's own texture rather than hung off it, so it moves with the armor, clips nothing, and the plate's rivets and edges read *through* it. It sits over the skin, under every part and under the trim. One greyscale cut mask ships the whole feature; there is no per-material art and no per-banner art.
- **Fittings** — A part can declare places for a second material — `gemstone`, `guard`, `inlay`, `banner` — and a fitting template sets one: gems and metals by trim material, inlays by dye, banners from a banner made at a loom. There is a template per fitting, each with its own look and recipe, and the template with the third slot empty takes its fitting out again. Fittings are data too — a pack's new fitting gets its template from a recipe — and an effect can be gated on one.
- **Found in the world** — Most parts are found rather than crafted, each theme in the structures that suit it — knightly gear in strongholds and trial chambers, beast trophies in bastions, court jewellery in mansions and ancient cities, tidal parts in shipwrecks and ocean ruins. A **loot group** is one file naming a category of tables and the tag of parts found in them, so a pack adds a whole look to the world at once, or drops one part into one chest from its own data file — the one thing a datapack cannot do for itself, since it can only replace a vanilla table whole. Armor **skins** are found the same way, divided over the same groups, and a **fitting template** turns up in every one of them. The odds belong to the table, so a chest's chance of holding something stays put however many parts are added. A loot function puts a part on a piece of armor a table drops, gem and all.
- **Taking parts off** — The advanced smithing table, crafted from a smithing table, an armor stand and two iron ingots, holds a whole set worn by a stand at once and lists each piece's sockets, its fittings and its trim as rows of icons. Pick one and Remove empties it — the one way a part, a fitting or a trim ever comes off. Its own template and material slots run the smithing table's recipes, with the result on the stand before it is paid for, and a fitting goes into the socket that is picked rather than into every part that takes one.
- **One smithing recipe per socket, forever** — The part rides on the template item as a component, so a pack hands out a template and needs no recipe of its own. And any recipe the mod ships can be switched off by overriding its file with `{"type": "armorpieces:disabled"}` — a part that is found rather than made, a server without fittings.
- **Optional behaviour** — A part may carry effects — attributes, mob effects, a projectile dodge, gliding — configured in the same JSON file. `pinions` is a cut-down elytra that actually flies.
- **A Blockbench plugin for making parts** — Opens a part on the vanilla player wearing real armor, walk cycle and all. Master, static layer and fitting masks are painted in place, any trim material previews live with its fittings filled or empty, the name, sockets, fittings, effects and loot are a dialog, and Save writes every file the pack needs — into your own datapack and resource pack, which it makes, finds and zips for you.

---

## Gallery

![The six themed sets, every socket filled — knightly, court, beast, wayfarer, tidal, carapace](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/gallery/sets.png)

*The six themed sets, every socket filled — knightly, court, beast, wayfarer, tidal, carapace*

![Sixty sets with nothing about them chosen — armor, skin, cloth, part, material and every fitting rolled](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/gallery/wardrobe.png)

*Sixty sets with nothing about them chosen — armor, skin, cloth, part, material and every fitting rolled*

![Fourteen armor skins on one diamond suit — the plate itself changed, not something hung on it](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/gallery/skins.png)

*Fourteen armor skins on one diamond suit — the plate itself changed, not something hung on it*

![One circlet, seven gems — the fitting takes a second material](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/gallery/fittings.png)

*One circlet, seven gems — the fitting takes a second material*

---

## How many sets is that?

A diamond set in vanilla is one look plus a trim. Eighteen patterns times eleven materials,
plus untrimmed, is **199** states per piece — and **1,568,239,201** for a set of four.

Now count that same diamond set with this mod installed. Each piece keeps all 199 of its trims
and gains a skin
(fourteen, or bare), a part in each of its sockets, each part in one of eleven materials, each
part's fittings filled or left empty — a gem from seven, a metal from four, an inlay from
sixteen dyes — and the chestplate a tunic or a tabard on top.

| | Vanilla diamond | With Armor Pieces |
| --- | ---: | ---: |
| Helmet | 199 | 1,833,029,934,300 |
| Chestplate | 199 | 5,113,599,898,358,700 |
| Leggings | 199 | 1,839,405,834,600 |
| Boots | 199 | 1,187,185,245 |
| **Full set** | **1,568,239,201** | **20,468,798,559,625,822,847,874,604,407,037,697,665,836,570,000,000** |

That is **2 × 10⁴⁹** — about 10⁴⁰ times the whole of vanilla, and roughly a sixth of the atoms
in the Earth. Some smaller ways to hold it:

- **The boots alone** come to 1,187,185,245 arrangements: three quarters of every trimmed
  diamond set vanilla can build, on your feet.
- **The helmet alone** is 1,169 times vanilla's entire four-piece space.
- **Shape alone**, before a single colour is chosen — which part sits in which socket, and
  nothing else — is 368,709,304,320 distinct silhouettes. 235 times vanilla's fully trimmed
  space, in pure geometry.
- Pick a set a second and you exhaust vanilla in fifty years. You exhaust this one in
  4.7 × 10³¹ times the age of the universe.

And all of that **counts a banner as a single design**, which it is not. A banner is sixteen
base colours and up to six layers of forty-two patterns in sixteen dyes:
**1,475,646,641,940,097,552** banners, any of which can go on the back banner, the cloak, the
tunic or the tabard. Count them properly and the chestplate alone reaches 7.7 × 10⁵⁰, and a
full set:

**3.07 × 10⁸⁴** — over thirty thousand distinct diamond sets for every atom in the observable
universe. (There are about 7.3 × 10⁷⁹ of those, if you take Planck's numbers and the baryons
they imply.)

And every number on this page is **diamond alone**, because that is what vanilla is being
compared against. Diamond is one of seven armor materials, six of which take a skin — which
multiplies the whole table by about thirteen hundred again, before leather has been dyed.

Nobody at spawn is wearing yours.

---

## Recipes

| ![Crafting recipe for Advanced Smithing Table](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__advanced_smithing_table.png) | ![Smithing Decoration recipe for Apply Back](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_back.gif) | ![Smithing Decoration recipe for Apply Belt](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_belt.gif) |
| :---: | :---: | :---: |
| Advanced Smithing Table | Apply Back *(Smithing Decoration)* | Apply Belt *(Smithing Decoration)* |
| ![Smithing Decoration recipe for Apply Brow](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_brow.gif) | ![Smithing Cloth recipe for Apply Cloth](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_cloth.gif) | ![Smithing Decoration recipe for Apply Collar](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_collar.gif) |
| Apply Brow *(Smithing Decoration)* | Apply Cloth *(Smithing Cloth)* | Apply Collar *(Smithing Decoration)* |
| ![Smithing Decoration recipe for Apply Crest](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_crest.gif) | ![Smithing Fitting recipe for Apply Fitting](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_fitting.gif) | ![Smithing Decoration recipe for Apply Greaves](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_greaves.gif) |
| Apply Crest *(Smithing Decoration)* | Apply Fitting *(Smithing Fitting)* | Apply Greaves *(Smithing Decoration)* |
| ![Smithing Decoration recipe for Apply Horns](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_horns.gif) | ![Smithing Decoration recipe for Apply Knees](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_knees.gif) | ![Smithing Decoration recipe for Apply Pauldrons](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_pauldrons.gif) |
| Apply Horns *(Smithing Decoration)* | Apply Knees *(Smithing Decoration)* | Apply Pauldrons *(Smithing Decoration)* |
| ![Smithing Skin recipe for Apply Skin](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_skin.gif) | ![Smithing Decoration recipe for Apply Spurs](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_spurs.gif) | ![Smithing Decoration recipe for Apply Tassets](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_tassets.gif) |
| Apply Skin *(Smithing Skin)* | Apply Spurs *(Smithing Decoration)* | Apply Tassets *(Smithing Decoration)* |
| ![Smithing Decoration recipe for Apply Vambraces](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_vambraces.gif) | ![Smithing Cloth recipe for Clear Cloth](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__clear_cloth.gif) | ![Smithing Fitting recipe for Clear Fitting](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__clear_fitting.gif) |
| Apply Vambraces *(Smithing Decoration)* | Clear Cloth *(Smithing Cloth)* | Clear Fitting *(Smithing Fitting)* |
| ![Smithing Skin recipe for Clear Skin](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__clear_skin.gif) | ![Crafting recipe for Cloth Template Tabard](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__cloth_template_tabard.png) | ![Crafting recipe for Cloth Template Tunic](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__cloth_template_tunic.png) |
| Clear Skin *(Smithing Skin)* | Cloth Template Tabard | Cloth Template Tunic |
| ![Crafting recipe for Fitting Template Banner](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__fitting_template_banner.png) | ![Crafting recipe for Fitting Template Gemstone](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__fitting_template_gemstone.png) | ![Crafting recipe for Fitting Template Guard](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__fitting_template_guard.png) |
| Fitting Template Banner | Fitting Template Gemstone | Fitting Template Guard |
| ![Crafting recipe for Fitting Template Inlay](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__fitting_template_inlay.gif) | ![Crafting recipe for Skin Template Brigandine](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__skin_template_brigandine.png) | ![Crafting recipe for Skin Template Chainmail](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__skin_template_chainmail.png) |
| Fitting Template Inlay | Skin Template Brigandine | Skin Template Chainmail |
| ![Crafting recipe for Skin Template Gambeson](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__skin_template_gambeson.png) | ![Crafting recipe for Skin Template Gothic](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__skin_template_gothic.png) | ![Crafting recipe for Skin Template Hoplite](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__skin_template_hoplite.png) |
| Skin Template Gambeson | Skin Template Gothic | Skin Template Hoplite |
| ![Crafting recipe for Skin Template Lamellar](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__skin_template_lamellar.png) | ![Crafting recipe for Skin Template Lorica](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__skin_template_lorica.png) | ![Crafting recipe for Skin Template Mail](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__skin_template_mail.png) |
| Skin Template Lamellar | Skin Template Lorica | Skin Template Mail |
| ![Crafting recipe for Skin Template Milanese](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__skin_template_milanese.png) | ![Crafting recipe for Skin Template Plate](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__skin_template_plate.png) | ![Crafting recipe for Skin Template Runic](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__skin_template_runic.png) |
| Skin Template Milanese | Skin Template Plate | Skin Template Runic |
| ![Crafting recipe for Skin Template Samurai](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__skin_template_samurai.png) | ![Crafting recipe for Skin Template Scale](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__skin_template_scale.png) | ![Crafting recipe for Skin Template Varangian](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__skin_template_varangian.png) |
| Skin Template Samurai | Skin Template Scale | Skin Template Varangian |
| ![Crafting recipe for Template Bandolier](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_bandolier.png) | ![Crafting recipe for Template Banner](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_banner.png) | ![Crafting recipe for Template Bells](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_bells.png) |
| Template Bandolier | Template Banner | Template Bells |
| ![Crafting recipe for Template Brush Crest](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_brush_crest.png) | ![Crafting recipe for Template Chain Of Office](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_chain_of_office.png) | ![Crafting recipe for Template Circlet](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_circlet.png) |
| Template Brush Crest | Template Chain Of Office | Template Circlet |
| ![Crafting recipe for Template Coronet](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_coronet.png) | ![Crafting recipe for Template Feathering](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_feathering.png) | ![Crafting recipe for Template Garters](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_garters.png) |
| Template Coronet | Template Feathering | Template Garters |
| ![Crafting recipe for Template Gorget](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_gorget.png) | ![Crafting recipe for Template Great Helm](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_great_helm.png) | ![Crafting recipe for Template Greaves](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_greaves.png) |
| Template Gorget | Template Great Helm | Template Greaves |
| ![Crafting recipe for Template Horns](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_horns.png) | ![Crafting recipe for Template Laurel](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_laurel.png) | ![Crafting recipe for Template Mittens](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_mittens.png) |
| Template Horns | Template Laurel | Template Mittens |
| ![Crafting recipe for Template Nasal](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_nasal.png) | ![Crafting recipe for Template Pendant](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_pendant.png) | ![Crafting recipe for Template Pinions](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_pinions.png) |
| Template Nasal | Template Pendant | Template Pinions |
| ![Crafting recipe for Template Poleyns](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_poleyns.png) | ![Crafting recipe for Template Quiver](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_quiver.png) | ![Crafting recipe for Template Sash](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_sash.png) |
| Template Poleyns | Template Quiver | Template Sash |
| ![Crafting recipe for Template Spaulders](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_spaulders.png) | ![Crafting recipe for Template Spectacle Visor](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_spectacle_visor.png) | ![Crafting recipe for Template Spire](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_spire.png) |
| Template Spaulders | Template Spectacle Visor | Template Spire |
| ![Crafting recipe for Template Spurs](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_spurs.png) | ![Crafting recipe for Template Tassets](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_tassets.png) | ![Crafting recipe for Template Thigh Sheath](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_thigh_sheath.png) |
| Template Spurs | Template Tassets | Template Thigh Sheath |
| ![Crafting recipe for Template Visor](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_visor.png) | ![Crafting recipe for Template Wing Cases](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_wing_cases.png) | ![Crafting recipe for Template Wing Roots](https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__template_wing_roots.png) |
| Template Visor | Template Wing Cases | Template Wing Roots |

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

Craft a gemstone fitting template (an amethyst block in a ring of paper), then smithing table: template, the decorated helmet, and the gem. Every part on the piece is offered the item, so one gem fills the stone of each part that has one — or of the one socket picked, at the advanced smithing table. The same template with the third slot empty takes the gem out again. A guard template does the same for metals, an inlay template for dyes, a banner template for banners. Re-applying a part at its own socket template keeps what is set in it, so changing a circlet's metal does not cost the gem.

**How do I take a part off?**

At the advanced smithing table. Put the piece in one of its four slots, pick the socket's row and click Remove. What was in the part's fittings goes with it. Picking one of the fitting icons beside the part takes just that fitting out, and the trim row under the sockets takes the trim off.

**Can two parts share a socket?**

No — applying a new crest replaces the crest. Several parts may be *available* for one socket (`horns` and `helm_wings` both fit `horns`); the choice is the expressive act.

**The parts on my hands are in the way. Can I turn them off?**

Yes. Set `"first_person_parts": false` in `config/armorpieces.json` and restart the game — the file writes itself on first launch. Only the first-person hand is affected; your parts are still on your body, and still on everyone else's. It is the mod's only setting, and deliberately so: everything else about a part is pack data rather than a preference, and nothing in that file changes what an item *does*, so it never has to match the server's.

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
