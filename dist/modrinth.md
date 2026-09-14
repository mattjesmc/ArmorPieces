<p align="center">
  <img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/banners/header.png" alt="Armor Pieces">
</p>

<p align="center"><i>Pieces, skins and cloth for armor — because someone else at spawn is wearing your diamond set.</i></p>

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

You know the one. You walk into spawn in your best diamond and the first person you see is
wearing the same helmet, the same chestplate, the same Sentry trim in the same netherite. Vanilla
can build 1,568,239,201 armor sets, which sounds like plenty right up until it happens to you
twice in a week.

Armor Pieces takes that number to **1.3 × 10⁶³** — about a million times the number of atoms in
the Sun, and that is diamond alone, one of seven armor materials.

It gives each item of armor **four layers of decoration, each an independent choice**:
a **piece** hung on a socket, a **skin** that changes what the plate itself is made of, a **cloth**
worn over the chest, and vanilla's own **trim** underneath them all. Every one of them is applied
at a smithing table, and none of them replaces another - a helmet can carry a skin, a trim, a
crest, a browband and a pair of horns at once.

**Pieces, over twelve sockets.** A plume on the helmet, spaulders on the shoulders, a sash on
the belt, spurs on the heels - the table below is every socket and how many pieces it has to
choose from. Pieces are real geometry hung on the body, not paint on the texture. A socket holds
one piece, so the choice is the expressive act. Each is applied with a trim material and takes
that material's colour.

**Armor skins.** A skin is the armor's *own* texture - what the plate is, rather than what is
bolted to it: plate, gothic, milanese, mail, chainmail, gambeson, brigandine, scale and
lamellar. Each is recoloured through the armor material's own palette, so a skinned iron helmet
still reads as iron and a modded armor material is skinned for free from the texture it already
ships. A skin is paid for in the metal the armor is made of: re-skinning is re-forging.

**Cloth.** A tunic or a tabard over a chestplate, carrying the design of any banner you make
at a loom - so the heraldry is yours rather than a list the mod maintains. It is baked into the
armor's texture rather than hung off it, so it clips nothing and the plate's own rivets and edges
read through it.

**Fittings.** Some pieces have a second colour, set separately: a gem in the circlet, a metal
buckle and a dyed strap on the sash, a dyed inlay on the greaves, a banner on the back banner.
One more smithing step, one template per fitting, and the item decides where it goes.

Most of it is **found rather than made**. A minority of pieces have a crafting recipe - the ones
where the item is plainly the piece or what it is made of; the rest turn up in the chests that
suit them, each theme in its own kind of structure, with the skins and the fitting templates
alongside. An
**advanced smithing table** shows a whole set worn by a stand and takes a piece, a fitting, a
trim, a skin or a cloth off again, which the smithing table cannot.

Every piece, skin and cloth is a datapack entry, a model and a texture, no code - and a pack adds
its own the same way, from Blockbench, in folders of its own. Packs are how the mod grows -
even its own three themes, knightly, court and wayfarer, are packs the jar carries, on by
default and switchable off - and the rest - the Wild Hunt, the Coral, the Hive, the Samurai,
the Norse and the packs after them - is content you install because you want that look. Armor
wearing a piece from a pack you do not have keeps it, says so, and shows it again the moment
the pack is installed.

---
<a id="whats-new"></a>

## New in 0.4.0

The release that made the mod safe to grow around: packs beside it, servers over it, and
nothing you saved ever lost.

- **Everything is a pack, the mod's own three themes included.** Twenty-five pieces and five
  skins left the mod for content packs — the tidal pieces to **Coral**, the beast pieces to
  **The Wild Hunt**, the carapace to **The Hive**, the cultural skins to **Samurai**, **Norse**
  and **Antiquity** — and eight more packs were built beside them: **Animals**, **Dragonslayer**,
  **Nether**, **Hero of the Village**, **Samurai**, **Norse**, **Antiquity** and **Tournament**.
  What the mod could always dress on its own — **knightly**, **court** and **wayfarer**, 66
  pieces and the nine skins that say how armor is *made* rather than who wore it — ships inside
  the jar as three built-in packs, on by default and switchable off like any other. You install
  the looks you want instead of ninety-one pieces to wear twelve.
- **Nothing you saved is ever lost.** Armor wearing a piece from a pack that is not installed
  keeps it exactly as saved, shows nothing in that socket, names the id and the pack in its
  tooltip, and shows it again the moment the pack is installed — no migration, no command, no
  deadline. Every piece that moved declares the ids it used to answer to, so a 0.3.0 save opens
  on 0.4.0 with nothing installed and keeps every item. `/armorpieces missing` lists what a
  world is waiting for; `packs/legacy` brings all thirty back under their old names at once.
- **A mistake in a pack costs that mistake, not the world.** A misplaced comma in one of a pack's
  files used to stop the world from opening and take every other pack's content with it. Now the
  bad file is left out, a bad socket or effect is dropped from its piece, the rest loads, and
  `/armorpieces packs` names the pack, the file and what was wrong.
- **Loot answers to the server.** `config/armorpieces-server.json` overrides the loot groups by
  id — a theme off, a chance or weight replaced, a modded chest added — with one
  `chance_multiplier` over everything, and `/reload` picks it up. `/armorpieces loot` lists the
  tables the mod touched, explains what it added to one and why, and rolls a table to check the
  theory against a measurement. A loot table of any other mod can hand out a random piece of
  ours from a tag, and a pack you did not install costs it an entry rather than the table.
- **Removing content is a setting, never a pack.** `parts.disabled` in the same file names the
  pieces, skins, garments and fittings — by id or by `#tag` — that a server does not offer, and
  `parts.mod_parts: false` switches off everything the mod ships itself. Switched off is not
  found, not listed, not crafted; it is still worn, because a setting must never break a save.
- **Cloth past the waist.** A tunic or a tabard reaches the legs now: the tunic closes five rows
  round each leg, the tabard hangs three, and the belt behind the chestplate's scalloped bottom
  is clothed too, so it reads as one garment. Still one template and one smithing operation.
- **Effects an author can shape.** Every number can be one per material, so a netherite claw
  bites harder than an iron one from one line. `if_wearer` gates an effect on vanilla's own
  entity predicate — what is in the hands, what else is worn, where the wearer is — beside
  `if_fitting`, which asks about the piece. The tooltip lists what each piece gives, and
  `/armorpieces effects` says which of them are contributing right now. Six pieces carry an
  effect, one per mechanism: `heel_wings` jump, `puttees` walk faster, `gorget` is worth a
  heart, `circlet` set with an emerald makes a hero of the village, `cloak` blinks out of an
  arrow's path, `pinions` fly.
- **A pack says what its pieces are for.** `armorpieces-sets.json` at a pack's root declares the
  outfits its pieces are meant to be worn in, borrowing from any other pack to fill the sockets
  it cannot, and they reach the wardrobe on armorpieces.com beside the mod's own three.
- **Blockbench, for your library.** `Packs...` is a manager: install a pack from a zip or from
  the public library, offer yours to it, work in one pack at a time, and — signed in to the
  site — check a piece out of your library and save it straight back. `New Armor Piece...` asks
  where the piece goes, not which folder. The plugin runs on the desktop and in a browser, and
  needs nothing from the game: the figure wears a studio set drawn by us, and *Use my game...*
  extracts the real textures onto your machine and nowhere else.
- **One command before a release.** `python tools/gate.py` runs everything in the repository that
  can fail, from the authoring round trip to a dedicated server asked every question and a client
  whose frames are diffed against blessed goldens. It is why this release could move thirty
  pieces and break no save.

---
<a id="contents"></a>

## What is in it

| How many | What |
| --- | --- |
| 66 | the pieces, over every socket |
| 9 | the armor skins |
| 2 | the cloths |
| 4 | the fittings |
| 12 | the sockets a piece can hang on |
| 3 | the loot groups |
| 6 | the effect types a piece may carry |
| 29 | the pieces with a template recipe; the rest are found |
| 2 | the fewest pieces any socket has to choose from |

---
<a id="sockets"></a>

## The twelve sockets

| Socket | Worn on | Pieces | What hangs there |
| --- | --- | --- | --- |
| crest | helmet | 4 | Top of the skull, pointing up |
| brow | helmet | 12 | Across the forehead, on the front face of the head |
| horns | helmet | 2 | Both temples, mirrored |
| pauldrons | chestplate | 4 | Both shoulders, mirrored, riding on the arms so they swing with them |
| back | chestplate | 6 | Upper back |
| collar | chestplate | 7 | Base of the throat, on the front of the chest |
| vambraces | chestplate | 6 | Both forearms, mirrored, riding on the arms |
| belt | leggings | 7 | Waistline, at the bottom of the torso |
| tassets | leggings | 4 | Both hips, mirrored, riding on the legs |
| knees | leggings | 5 | Both knees, mirrored, on the front of the legs |
| spurs | boots | 6 | Both heels, mirrored, at the back of the ankle |
| greaves | boots | 3 | Both shins, mirrored, on the front of the lower leg |

---
<a id="features"></a>

## Features

- **Twelve sockets, one piece at a time** — `crest`, `brow`, `horns`, `pauldrons`, `back`, `collar`, `vambraces`, `belt`, `tassets`, `knees`, `spurs`, `greaves`. A socket holds one piece, so a new crest replaces the crest — and every socket has several to choose from. Seven of the sockets are mirrored pairs, so spaulders means both shoulders.
- **Coloured by vanilla trim materials** — One grayscale master per piece is mapped onto each material's own palette at load time. A new trim material costs a piece no new art at all.
- **On your own hands, in first person** — Vanilla draws a bare sleeve on the first-person hand and nothing else — not armor, not a trim — so the one view you spend the whole game in is the one that never showed what you were wearing. Pauldrons and vambraces show there now, on the same player model the world sees, swinging with the arm through every animation the hand already has. They are close to the camera and they are meant to be — and there is a setting to turn them off, if you would rather keep the view clear.
- **Armor skins** — The one thing here that changes the armor itself rather than adding to it — plate, gothic, milanese, mail, chainmail, gambeson, brigandine, scale, lamellar: the nine that say how armor is *made*, with the ones that say who wore it in the culture packs (Samurai, Norse, Antiquity). One greyscale master pair on vanilla's own armor grid, recoloured at load through eight shades taken from *that armor material's* vanilla texture, with vanilla's own panel edges and shadows mixed back over it. A skinned iron helmet still reads as iron, gold still reads as gold, and a modded armor material is skinned for free from the texture it already ships. Applied at the advanced smithing table with the armor's own reforging material — re-skinning is re-forging, and it costs the metal the armor is made of.
- **Cloth over the chest** — A **Tunic** or a **Tabard**, applied with a cloth template and a banner, and the design is the banner's — sixteen dyes crossed with every pattern layer, made at a loom, so the heraldry is a player's choice rather than a list the mod keeps. It is painted into the armor's own texture rather than hung off it, so it moves with the armor, clips nothing, and the plate's rivets and edges read *through* it. It sits over the skin, under every piece and under the trim. One greyscale cut mask ships the whole feature; there is no per-material art and no per-banner art.
- **Fittings** — A piece can declare places for a second material — `gemstone`, `guard`, `inlay`, `banner` — and a fitting template sets one: gems and metals by trim material, inlays by dye, banners from a banner made at a loom. There is a template per fitting, each with its own look and recipe, and the template with the third slot empty takes its fitting out again. Fittings are data too — a pack's new fitting gets its template from a recipe — and an effect can be gated on one.
- **Found in the world** — Most pieces are found rather than crafted, each theme in the structures that suit it — knightly gear in strongholds and trial chambers, court jewellery in mansions and ancient cities, a wayfarer's kit on the roads and in the villages. A **loot group** is one file naming a category of tables and the tag of pieces found in them, so a pack adds a whole look to the world at once, or drops one piece into one chest from its own data file — the one thing a datapack cannot do for itself, since it can only replace a vanilla table whole. Armor **skins** are found the same way, divided over the same groups, and a **fitting template** turns up in every one of them. The odds belong to the table, so a chest's chance of holding something stays put however many pieces are added. A loot function puts a piece on the armor a table drops, gem and all. A server owner tunes all of it from one file — a theme off, a chance halved, a modded chest added — and `/armorpieces loot` says which tables the mod touched and why; a loot table of any other mod can hand out a random piece of ours from a tag, and an absent pack costs it an entry rather than the table.
- **Taking pieces off** — The advanced smithing table, crafted from a smithing table, an armor stand and two iron ingots, holds a whole set worn by a stand at once and lists each piece's sockets and their fittings as rows of icons, with the armor's own row under them — its trim, its skin and, on a chestplate, its cloth. Pick one and Remove empties it — the one way a piece, a fitting, a trim, a skin or a cloth ever comes off. An empty place shows a hint of the template that would fill it. Its own template and material slots run the smithing table's recipes, with the result on the stand before it is paid for, and a fitting goes into the socket that is picked rather than into every piece that takes one.
- **One smithing recipe per socket, forever** — The piece rides on the template item as a component, so a pack hands out a template and needs no recipe of its own. And any recipe the mod ships can be switched off by overriding its file with `{"type": "armorpieces:disabled"}` — a piece that is found rather than made, a server without fittings.
- **Optional behaviour** — A piece may carry effects — attributes, mob effects, a projectile dodge, gliding — configured in the same JSON file, and every number can be one per material, so a netherite claw bites harder than an iron one from one line. An effect can ask about the piece (which fitting is set) or about the wearer, with vanilla's own entity predicate — what is in the hands, what else is worn, where they are. The tooltip lists what each piece gives in that material, and `/armorpieces effects` says which of them are contributing right now. `pinions` is a cut-down elytra that actually flies; six pieces carry an effect, one per mechanism, as worked examples for a pack to copy.
- **Nothing you saved is ever lost** — A piece from a pack that is not installed stays on the armor exactly as it was saved, renders nothing, and comes back the moment the pack is — the tooltip names the id and the pack it went to. A piece that moves between packs declares the ids it used to answer to, so a save written before the move finds it with no migration and no command. A mistake in a pack's file costs that file, never the world: the game opens, the rest of the pack loads, and `/armorpieces packs` names the pack, the file and what was wrong.
- **A Blockbench plugin for making pieces** — Opens a piece on the vanilla player wearing real armor, walk cycle and all. Master, static layer and fitting masks are painted in place, any trim material previews live with its fittings filled or empty, the name, sockets, fittings, effects and loot are a dialog, and Save writes every file the pack needs — into your own datapack and resource pack, which it makes, finds and zips for you. `Packs...` installs a pack from a zip or from the public library, offers yours to it, and — signed in to armorpieces.com — checks a piece out of your library and saves it back. It runs on the desktop and in a browser, and it needs nothing from the game to do any of it.

---
<a id="gallery"></a>

## Gallery

<p align="center">
  <img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/gallery/sets.png" alt="Themed sets, every socket filled — the mod's knightly, court and wayfarer, and the pack sets beside them">
  <br><sub><i>Themed sets, every socket filled — the mod's knightly, court and wayfarer, and the pack sets beside them</i></sub>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/gallery/skins.png" alt="Every armor skin on one diamond suit — the plate itself changed, not something hung on it">
  <br><sub><i>Every armor skin on one diamond suit — the plate itself changed, not something hung on it</i></sub>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/gallery/wardrobe.png" alt="Sixty sets with nothing about them chosen — armor, skin, cloth, piece, material and every fitting rolled">
  <br><sub><i>Sixty sets with nothing about them chosen — armor, skin, cloth, piece, material and every fitting rolled</i></sub>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/gallery/fittings.png" alt="One circlet, seven gems — the fitting takes a second material">
  <br><sub><i>One circlet, seven gems — the fitting takes a second material</i></sub>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/gallery/table.png" alt="The advanced smithing table, holding the whole court suit beside it — the chestplate's sockets and their fittings as rows of icons, its own trim, skin and cloth under them, and Remove, the one way any of it comes off again">
  <br><sub><i>The advanced smithing table, holding the whole court suit beside it — the chestplate's sockets and their fittings as rows of icons, its own trim, skin and cloth under them, and Remove, the one way any of it comes off again</i></sub>
</p>

---
<a id="how-many-sets"></a>

## How many sets is that?

A diamond set in vanilla is one look plus a trim. Eighteen patterns times eleven materials,
plus untrimmed, is **199** states per piece — and **1,568,239,201** for a set of four.

Now count that same diamond set with this mod installed. Each piece keeps all 199 of its trims
and gains a skin
(nine, or bare), a piece in each of its sockets, each piece in one of eleven materials, each
piece's fittings filled or left empty — a gem from seven, a metal from four, an inlay from
sixteen dyes — and the chestplate a tunic or a tabard on top.

| | Vanilla diamond | With Armor Pieces |
| --- | ---: | ---: |
| Helmet | 199 | 26,802,796,580 |
| Chestplate | 199 | 735,580,184,364,000 |
| Leggings | 199 | 584,066,114,400 |
| Boots | 199 | 456,299,040 |
| **Full set** | **1,568,239,201** | **5,254,382,653,471,233,625,936,048,378,064,626,821,120,000,000** |

That is **5.3 × 10⁴⁵** — about 3 × 10³⁶ times the whole of vanilla. Some smaller ways to hold
it:

- **The boots alone** come to 456,299,040 arrangements: more than a quarter of every trimmed
  diamond set vanilla can build, on your feet.
- **The helmet alone** is 17 times vanilla's entire four-piece space.
- **Shape alone**, before a single colour is chosen — which piece sits in which socket, empty
  included, and nothing else — is 2,568,384,000 distinct silhouettes. Still more than vanilla's
  fully trimmed space, in pure geometry.
- Pick a set a second and you exhaust vanilla in fifty years. You exhaust this one in
  1.2 × 10²⁸ times the age of the universe.

And all of that **counts a banner as a single design**, which it is not. A banner is sixteen
base colours and up to six layers of forty-two patterns in sixteen dyes:
**1,475,646,641,940,097,552** banners, any of which can go on the back banner, the cloak, the
tunic or the tabard. Count them properly and the chestplate alone reaches 1.8 × 10³², and a
full set:

**1.3 × 10⁶³** — about a million times the number of atoms in the Sun.

These are the numbers for the **mod alone**. Every content pack adds pieces to sockets that
are already multiplying, so the count does not creep upward — it jumps.

And every number on this page is **diamond alone**, because that is what vanilla is being
compared against. Diamond is one of seven armor materials, six of which take a skin — which
multiplies the whole table by about thirteen hundred again, before leather has been dyed.

Nobody at spawn is wearing yours.

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
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_cloth.gif" alt="Smithing Cloth recipe for Apply Cloth"><br><sub>Apply Cloth <i>(Smithing Cloth)</i></sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_collar.gif" alt="Smithing Decoration recipe for Apply Collar"><br><sub>Apply Collar <i>(Smithing Decoration)</i></sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_crest.gif" alt="Smithing Decoration recipe for Apply Crest"><br><sub>Apply Crest <i>(Smithing Decoration)</i></sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_fitting.gif" alt="Smithing Fitting recipe for Apply Fitting"><br><sub>Apply Fitting <i>(Smithing Fitting)</i></sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_greaves.gif" alt="Smithing Decoration recipe for Apply Greaves"><br><sub>Apply Greaves <i>(Smithing Decoration)</i></sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_horns.gif" alt="Smithing Decoration recipe for Apply Horns"><br><sub>Apply Horns <i>(Smithing Decoration)</i></sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_knees.gif" alt="Smithing Decoration recipe for Apply Knees"><br><sub>Apply Knees <i>(Smithing Decoration)</i></sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_pauldrons.gif" alt="Smithing Decoration recipe for Apply Pauldrons"><br><sub>Apply Pauldrons <i>(Smithing Decoration)</i></sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_skin.gif" alt="Smithing Skin recipe for Apply Skin"><br><sub>Apply Skin <i>(Smithing Skin)</i></sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_spurs.gif" alt="Smithing Decoration recipe for Apply Spurs"><br><sub>Apply Spurs <i>(Smithing Decoration)</i></sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_tassets.gif" alt="Smithing Decoration recipe for Apply Tassets"><br><sub>Apply Tassets <i>(Smithing Decoration)</i></sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__apply_vambraces.gif" alt="Smithing Decoration recipe for Apply Vambraces"><br><sub>Apply Vambraces <i>(Smithing Decoration)</i></sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__clear_cloth.gif" alt="Smithing Cloth recipe for Clear Cloth"><br><sub>Clear Cloth <i>(Smithing Cloth)</i></sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__clear_fitting.gif" alt="Smithing Fitting recipe for Clear Fitting"><br><sub>Clear Fitting <i>(Smithing Fitting)</i></sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__clear_skin.gif" alt="Smithing Skin recipe for Clear Skin"><br><sub>Clear Skin <i>(Smithing Skin)</i></sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__cloth_template_tabard.png" alt="Crafting recipe for Cloth Template Tabard"><br><sub>Cloth Template Tabard</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__cloth_template_tunic.png" alt="Crafting recipe for Cloth Template Tunic"><br><sub>Cloth Template Tunic</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__fitting_template_banner.png" alt="Crafting recipe for Fitting Template Banner"><br><sub>Fitting Template Banner</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__fitting_template_gemstone.png" alt="Crafting recipe for Fitting Template Gemstone"><br><sub>Fitting Template Gemstone</sub></td>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__fitting_template_guard.png" alt="Crafting recipe for Fitting Template Guard"><br><sub>Fitting Template Guard</sub></td>
</tr>
<tr>
<td align="center" width="33%"><img src="https://raw.githubusercontent.com/mattjesmc/ArmorPieces/main/docs/assets/recipes/armorpieces__fitting_template_inlay.gif" alt="Crafting recipe for Fitting Template Inlay"><br><sub>Fitting Template Inlay</sub></td>
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
3. Install it on both sides — the client draws the pieces, the server owns their behaviour.

---
<a id="adding-a-piece"></a>

## Adding a piece

A piece is two files and a PNG, plus a line in your language file for the name — none of it
code, and any namespace will do. Two ways to make them:

- **In Blockbench**, with the [Armor Pieces plugin](https://github.com/mattjesmc/ArmorPieces/blob/main/tools/blockbench_plugin/armorpieces.js). It opens a piece on the vanilla
  player wearing real armor, paints the textures in place, previews any trim material, and
  writes every file on Save — into a pack of your own, or into your library on
  [armorpieces.com](https://armorpieces.com), where it is checked out and checked back in.
- **By hand**, writing the datapack entry, the geometry and the grayscale master yourself.

The [authoring guide](https://github.com/mattjesmc/ArmorPieces/blob/main/docs/authoring.md) covers both, along with fittings, handing a piece out, giving
it behaviour — attributes, mob effects, a dodge, gliding — from the same JSON file, declaring
the sets a pack's pieces are meant to be worn in, and what happens when a pack is wrong.

---
<a id="working-on-it"></a>

## Working on it

`./gradlew build`, `./gradlew runClient`, `./gradlew runServer`.

| Where | What |
| --- | --- |
| `decoration/` | anchors, the datapack registry entry, the item component, the effect hooks |
| `identity/` | the tolerant decode, `former_ids` and the uid rebind, the missing-piece report and `/armorpieces missing`, `prune` and `upgrade` |
| `pack/` | what happens when a pack is wrong: the lenient list codec, the skipped-file rule, the stand-in fittings, the audit and `/armorpieces packs` |
| `config/` | the client file and the server file |
| `client/` | the render layer, the geometry loader and bake cache, the per-material palette, the skin and cloth bakes, the advanced table's screen |
| `skin/`, `cloth/` | the datapack registries behind an armor skin and a cloth, and the components a piece carries them in |
| `recipe/`, `item/`, `registry/`, `command/` | smithing, the twelve socket templates and the fitting, skin and cloth templates, the creative tab, `/armorpieces stage` |
| `loot/`, `block/`, `menu/` | pieces in loot tables, the loot groups and the server's overrides, the `armorpieces:template` entry and the `set_decoration` function, `/armorpieces loot`; the advanced smithing table and its menu |
| `tools/` | Blockbench rigs (`bb_rig.py`, with the vanilla figure and walk cycle from `mc_humanoid.py`), `.bbmodel` ↔ geometry (`bb_geo.py`), master and mask painting and install (`paint_<part>_master.py`, `fitting_mask.py`, `sync_decoration_masters.py`), a material and fitting preview outside the game (`preview_material.py`), template and recipe icons, `export_pack.py` for zipping a pack, `trace_geometry.py` for measuring a piece against the body, the skin masters and their bake, check and install (`skin_sheets.py`, `bake_skin.py`, `check_skin.py`, `sync_skin_masters.py`), the checks a shipped piece and skin pass (`check_part.py`, `check_authoring.py`), `pack_manifest.py`, `pick_pieces.py`, `import_pack.py` and `sanitize_pack.py` for what a pack holds and moving pieces between packs, and `gate.py`, the one command that has to pass before a release |
| `tools/blockbench_plugin/` | the Blockbench plugin — see the [authoring guide](https://github.com/mattjesmc/ArmorPieces/blob/main/docs/authoring.md) |
| `tools/decoration_masters/` | the grayscale masters — the source of truth for every piece's art |
| `packs/` | the content packs built beside the mod — the four the split made and the four after them — and `legacy`, generated from their `former_ids` |
| `src/test/` | the unit tests: every shipped file decoded and encoded back, a piece worn by an entity with no world, the four traps of 0.4.0 |

The rigs, the `/armorpieces stage` command and the plugin's Save path are described in the
[authoring guide](https://github.com/mattjesmc/ArmorPieces/blob/main/docs/authoring.md); `tools/check_authoring.py` runs the plugin's round trip over every
shipped piece. `python tools/gate.py` runs every check in the repository that can fail — the
tree, the JVM, a dedicated server and a client — and is what a release waits on; the tiers
are in `docs/plans/testing.md`.

---
<a id="configuration"></a>

## Configuration

Two files, each written for you on first launch, and each read by one side only.

**`config/armorpieces.json`** is read on the client and by the client alone — every setting in it
moves pixels and nothing else, so it never has to match the server's.

| Key | Default | What it does |
| --- | --- | --- |
| `first_person_parts` | `true` | Draws the pieces on your arms — pauldrons and vambraces — on the first-person hand as well as on your body. Vanilla shows a bare sleeve there and no armor at all. They sit close to the camera; `false` keeps the view clear. |

A change takes effect on the next launch.

**`config/armorpieces-server.json`** is the server's, and it is about what the world hands out:
how much of it, and which of it. Loot content is pack data, but *how much of it* is not, and a
server owner should not have to write a datapack to say so. The file overrides the loot groups
rather than replacing them, keyed by group id, and is re-read at the start of every datapack
reload, so `/reload` picks up an edit.

| Key | Default | What it does |
| --- | --- | --- |
| `enabled` | `true` | The off switch: `false` and the mod adds nothing to any loot table. |
| `chance_multiplier` | `1.0` | Scales every chance the mod puts on a table — groups and a piece's own `loot` rows alike. `0.5` is "half as much of this mod" without naming a group. |
| `groups.<id>.enabled` | `true` | Drops one theme from the world. |
| `groups.<id>.chance`, `.weight` | the group's own | Replace the group's chance per table and the weight of its members. |
| `groups.<id>.add`, `.remove` | `[]` | Tables to join — a modded container needs no datapack at all — and tables to leave. |
| `parts.mod_parts` | `true` | `false` switches off everything the mod ships itself — every piece, skin, garment and fitting in the `armorpieces` namespace — in one line, for a server that runs on packs alone. |
| `parts.disabled` | `[]` | Ids and `#tags` — parts, skins, garments or fittings, one list for all four — that this server does not offer. `["#armorpieces:knightly", "armorpieces_dragon:dragon_wings"]` takes a whole theme and one pack's piece out. |

What a group *contains* is deliberately not overridable: different members are a different group,
which is content, which is a datapack. `/armorpieces loot groups` shows the groups with the file
applied, and `/armorpieces loot explain <table>` says what ended up on a table and why.

Switched off means **not offered**: not in any chest, not on the creative tab, not craftable as a
template, and refused at both smithing tables. It does not mean uninstalled. A piece a player is
already wearing is still read and still drawn — removing content is a setting and never a pack,
and the setting never breaks a save. Loot and recipes move on `/reload`; the creative tab is
rebuilt on the next join.

In both files a key you leave out takes its default and is written back, so a setting added by a
later version turns up in the file you already have — and a file that does not parse is left
alone and the defaults used, so a typo costs a log line and nothing else.

---
<a id="faq"></a>

## FAQ

**Does a piece replace the armor trim?**

No. Armor carries its trim and its pieces at once.

**How do I put a gem in the circlet?**

Craft a gemstone fitting template (an amethyst block in a ring of paper), then smithing table: template, the decorated helmet, and the gem. Every piece on the armor is offered the item, so one gem fills the stone of each piece that has one — or of the one socket picked, at the advanced smithing table. The same template with the third slot empty takes the gem out again. A guard template does the same for metals, an inlay template for dyes, a banner template for banners. Re-applying a piece at its own socket template keeps what is set in it, so changing a circlet's metal does not cost the gem.

**How do I take a piece off?**

At the advanced smithing table. Put the armor in one of its four slots, pick the socket's row and click Remove. What was in the piece's fittings goes with it. Picking one of the fitting icons beside the piece takes just that fitting out, and the armor's own row under the sockets holds its trim, its skin and — on a chestplate — its cloth, each taken off the same way.

**Can two pieces share a socket?**

No — applying a new crest replaces the crest. Several pieces may be *available* for one socket (`horns` and `helm_wings` both fit `horns`); the choice is the expressive act.

**The pieces on my hands are in the way. Can I turn them off?**

Yes. Set `"first_person_parts": false` in `config/armorpieces.json` and restart the game — the file writes itself on first launch. Only the first-person hand is affected; your pieces are still on your body, and still on everyone else's. It is the client file's only setting, and deliberately so: everything else about a piece is pack data rather than a preference, and nothing in that file changes what an item *does*, so it never has to match the server's.

**Do I need the mod to add pieces?**

You need the mod installed, but adding a piece takes no Java — a datapack and a resource pack. Only a brand-new *effect* type needs code. The [authoring guide](https://github.com/mattjesmc/ArmorPieces/blob/main/docs/authoring.md) walks through it.

**I uninstalled a pack. What happens to the armor that was wearing its pieces?**

Nothing is lost. The armor keeps the piece exactly as it was saved, shows nothing in that socket, and names the missing id and its pack in the tooltip; install the pack again and it is back. `/armorpieces missing` lists what a world is waiting for, and `/armorpieces prune` is the one way a missing piece is ever dropped — on purpose, by an operator.

**A pack I installed has a mistake in it. Will the world still open?**

Yes. A mistake costs that mistake: a piece with an unknown socket loses the socket, a file that cannot be read is left out, and everything else in the pack and every other pack loads. `/armorpieces packs` names the pack, the file and what was wrong, and operators see a line on join while the report is not empty.

**Pieces are too common on my server. Can I change that without a datapack?**

Yes — `config/armorpieces-server.json`. `chance_multiplier` scales everything the mod puts in a table, a group can be turned off or re-tuned by id, and a table can be added to or taken from a group; `/reload` picks up the edit. See Configuration.

**Can I turn a piece off on my server without uninstalling the pack?**

Yes — `parts.disabled` in the same file takes ids and `#tags` of parts, skins, garments and fittings, and `parts.mod_parts: false` switches off everything the mod ships itself. A switched-off piece is not found, listed or crafted, but one already worn is still drawn: the setting never breaks a save. Removing content is always a setting, never a pack.

---
<a id="bugs"></a>

## Bugs and issues

Something broken, something clipping, a piece that sits wrong on a body it should fit — the
[issue tracker](https://github.com/mattjesmc/ArmorPieces/issues) is the place for it. So is a
request: a socket, a piece, a skin or a fitting that is not there yet.

No GitHub account, and would rather not make one? The comment section on the CurseForge or
Modrinth page reaches me just as well.

For a bug, the three things that make it fixable are your Minecraft and mod versions, the
other mods you are running, and `logs/latest.log` from the run it happened in. A screenshot
settles most questions about how something *looks* on its own. If a pack is involved, the
output of `/armorpieces packs` says what the mod made of it.

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

Every piece in this mod is the same two files and a PNG a pack of your own would write.
