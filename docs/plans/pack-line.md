# The pack line

> **Where this stands (2026-09-07).** Design only. **Nothing here is built.** Animals is complete in
> the working copy and published nowhere; Coral is complete and holds one outfit (*The Reef*). This
> document is the packs that come after them, and it exists because the "Boss pack" in
> `set-packs.md` dissolved once we tried to fill twelve sockets with it.
>
> Read `set-packs.md` first — the seam, the checks, the release and publishing sections there are
> still the machinery. This document says **what to build, and why it is one pack rather than
> another**.

---

## The rule

**A pack's outfit uses only that pack's own pieces.** A pack that shows an outfit half made of
somebody else's work is advertising somebody else. Every outfit below is drawn from its own pack and
nothing else.

**The outfit is not the pack.** It is one showcase arrangement — the library page's picture and the
wardrobe's row. A pack may hold more pieces than its outfit uses, and a player's own outfit will
cross packs constantly, which is what the wardrobe is for.

**How many pieces a pack must have is not settled here.** A *minimum content spec* comes **after**
the default pack is divided across the sub-packs and the new packs, which is being explored in its
own session and will change what every pack contains. Until that lands, the twelves below are
designs, not a quota.

---

## The dissolve

The roadmap's Boss pack was "Warden, Wither, Ender Dragon, Elder Guardian, Breeze — every piece a
drop from its own mob". It fails on its own terms: five bosses cannot produce a pack's worth of
pieces that agree about anything. A warden's cyan-on-black and an elder guardian's prismarine green share no
palette, no material and no place. Each boss already belongs somewhere with more in it.

So it becomes **four new packs organised by place**, each with a boss at its centre, plus one that
already exists:

| pack | namespace | centre | what else is in it |
|---|---|---|---|
| **Dragonslayer** | `armorpieces_dragon` | the Ender Dragon | her own body, and the End around her |
| **Nether** | `armorpieces_nether` | the Wither | strider, hoglin, piglin brute, blaze, ghast |
| **Caves** | `armorpieces_caves` | the Warden | sculk, the ancient city, and the lush and dripstone caves |
| **Hero of the Village** | `armorpieces_village` | the raid | ravager, evoker, vex, pillager, witch, golem, allay |
| **Ocean** | `armorpieces_coral` | the Elder Guardian | Coral, already begun, grown to twelve |

Packs are named for **places**, not bosses, so each can grow. A namespace is permanent the moment
somebody wears a piece.

---

## The socket map

Every outfit below fills these twelve with its own pieces. `DecorationAnchor.java` binds each socket
to the armor piece that carries it:

| armor | socket | where it sits |
|---|---|---|
| **helmet** | `crest` | the top of the helm |
| | `brow` | the face |
| | `horns` | the temples, mirrored |
| **chestplate** | `pauldrons` | the shoulders, mirrored |
| | `back` | the upper back |
| | `collar` | the throat |
| | `vambraces` | the forearms, mirrored |
| **leggings** | `belt` | the waist |
| | `tassets` | the hips, mirrored |
| | `knees` | the knees, mirrored |
| **boots** | `greaves` | the shins, mirrored |
| | `spurs` | the heels, mirrored |

**There is no chest socket** — the nearest are `collar` and `back`. **`greaves` is shins on the boots;
`vambraces` is forearms on the chestplate**, so a hand piece is a `vambraces` piece and must not be
called greaves.

---

## Rules the line follows

**Names.** A pack piece may shadow one of the mod's 91 in the same socket when the qualifier is the
subject and the result reads as a named thing — `nautilus_gorget` beside `gorget` is the precedent.
It may never reuse a *generic* name outright: no pack piece called `horns`, `claws` or `mantle`.

**How pieces are had.** Two routes, chosen per piece:

- **An exact `loot` row** on the piece's own data file, for a boss that genuinely drops it. Not a
  group — a group is one member set over a set of tables, so a group naming four entity tables would
  let a warden drop the guardian's spikes.
- **A group** naming the pack's own tag over the *chest* tables of its place. Anything tagged joins
  automatically, so a later piece is had by adding one line to a tag file.

Craft where neither fits. Every recipe centre must be free: two recipes sharing a centre is one
silently unobtainable piece.

**Never put a piece on a farmable mob.** The chance belongs to the table, so a piece on a
raid-farmed ravager or a trial-spawner breeze is not rare, it is a tax on a farm.

**Effects.** `armorpieces:glide`, `attribute`, `mob_effect`, `blink` and the `if_wearer` /
`if_fitting` conditionals are plain data — the mod's `pinions`, `claws`, `head_fins`, `heel_wings`,
`cloak` and `circlet` already use them. **No pack has ever shipped one.** At most one piece per pack
carries an effect until that seam is proven.

---

## The finding that changes the End

**The Ender Dragon cannot drop anything through a loot table.** Verified against the 26.2 jar:

- `data/minecraft/loot_table/entities/ender_dragon.json` exists but has **no pools**.
- `EnderDragon.handleKillingBlow()` sets health to 1 and switches the phase manager to `DYING`. It
  never calls `super`, never calls `die()`, so `dropAllDeathLoot` never runs and the table is never
  rolled.

An empty table is not itself proof — `entities/wither.json` is also empty, but `WitherBoss` overrides
`dropCustomDeathLoot`, a method only `dropAllDeathLoot` calls, which proves the wither's table **is**
rolled. So: **wither yes, dragon no.** A `loot` row on `minecraft:entities/ender_dragon` is dead data.

`warden`, `elder_guardian`, `breeze`, `ravager`, `evoker`, `shulker` and `creaking` all have real,
rolled tables. Consequence: the Dragonslayer pack is **found in the End**, and what gates it is that
end cities are past her.

---

## Light and particles: the one mod change the line asks for

Everything else here is data a pack may already ship. This is not, and it is worth it because two of
the five packs are dark places whose identity is a light inside them.

### What exists today

- **One draw per piece.** `ArmorDecorationLayer` resolves a single render type,
  `RenderTypes.armorCutoutNoCull(...)`, and submits the geometry with the **entity's own**
  `lightCoords`. A decoration is lit exactly as the armor under it, always.
- **Three sheets.** `<part>.png` (greyscale master, its value a position on the trim ramp),
  `<part>_static.png` (RGBA, keeps its own colour), `<part>_<fitting>.png` (one greyscale mask per
  masked fitting). Nothing is fullbright and nothing can be made so from data.
- **Particles already work from an effect.** `BlinkEffect` calls
  `level.sendParticles(ParticleTypes.PORTAL, ...)` server-side, so every viewer sees them. Its hook,
  `DecorationEffect.Ticking`, is handed the wearer, the level and a random source.

### Glow — a fourth sheet

`<part>_glow.png`, RGBA like the static layer, drawn in a **second submit** over the same geometry at
full-bright light coordinates. Colour, not ramp: a glowing thing does not change colour with the
armor it happens to sit on. `DecorationTextureManager`'s resolution order gains one entry and
`ArmorDecorationLayer` gains one submit; the Blockbench kit's sheet list, `check_part.py` and
`check_authoring.py` all enumerate sheets by name and would reject an unknown one.

**A fullbright texture is not a light source.** The piece looks lit in the dark; it does not light the
floor, because vanilla has no dynamic entity lighting and faking one means placing light blocks,
which a decoration should not do. Everywhere this document says "glow", it means the first thing.

**Open:** whether glow pulses. Sculk that breathes is far better than sculk that is simply on, and the
cheap version is a per-tick alpha off a sine — but that is animation, which the mod does not have.

### Particles — a new built-in effect

`armorpieces:particles`, alongside the six that exist:

```json
{ "type": "armorpieces:particles",
  "particle": "minecraft:spore_blossom_air",
  "chance": 0.15,
  "count": 1,
  "offset": [0.3, 0.2, 0.3] }
```

`Ticking`, server-side, gated by `chance`. The honest first version spawns around the wearer's
bounding box: the context knows which **socket** a piece is in but not where that anchor lands in
world space, and inventing that is a far larger change. This generalises `BlinkEffect`'s two lines
into something data-driven.

### Who needs it

| pack | glow | particles |
|---|---|---|
| **Caves** | **yes** — the sculk pulse and every lush berry. Both halves are about light | yes, the spore drip |
| **Dragonslayer** | wants it — `crystal_pendant`, her eyes | maybe, a portal shimmer |
| **Nether** | wants it — `blaze_halo`, `soul_greaves`, `magma_cops` | smoke |
| **Ocean** | wants it — the guardian's eye, the sea pickles | no |
| **Hero of the Village** | wants it — `allay_wisps` | no |

**Only Caves is gated on it.** The rest read without it. The strongest argument for building it early
is the **retro-fit**: the mod's `spire` (amethyst), `bells`, `circlet` with a gemstone fitting, and
Coral's `coral_crown` all want a glow sheet, and adding one to an existing piece is a texture rather
than a redesign.

---

## Pack: Dragonslayer

`armorpieces_dragon`. Netherite armor with amethyst hardware — black plate and purple light.

### Twelve pieces, one per socket

| socket | piece | what it is | fitting | centre |
|---|---|---|---|---|
| `crest` | `dragon_crest` | the ridge of small horns down the crown | — | `dragon_breath` |
| `brow` | `dragon_mask` | her eyes and snout, built into the visor | — | chest |
| `horns` | `dragon_horns` | the two long back-swept head horns | — | chest |
| `pauldrons` | `dragon_spines` | the spine ridge, broken across both shoulders | — | chest |
| `back` | `dragon_wings` | folded membrane wings — **the glide piece** | — | chest |
| `collar` | `crystal_pendant` | a caged end crystal at the throat | `gemstone` | `end_crystal` |
| `vambraces` | `dragon_claws` | the wing claws laid along the forearms | `guard` | chest |
| `belt` | `dragon_tail` | the tail base ringing the waist, hanging behind | — | chest |
| `tassets` | `wing_tatters` | torn membrane strips hanging from the hips | — | `chorus_fruit` |
| `knees` | `dragon_knuckles` | the wing's knuckle joints as knee cops | — | `end_rod` |
| `greaves` | `dragon_scales` | scaled plates up the shins | — | `purpur_block` |
| `spurs` | `dragon_talons` | the hind claws at the heels | — | `chorus_flower` |

`dragon_claws` and `dragon_talons` shadow the mod's `claws` and `talons` — allowed, both qualified by
their subject. `dragon_scales` is the shin piece; the hand piece is `dragon_claws` and is never
called greaves.

### The effect

`dragon_wings` carries `armorpieces:glide`. The mod's `pinions` is the reference — `{"sink": 0.03,
"wear_interval": 4}`, deliberately a worse elytra. Hers are the reward for the hardest fight in the
game and should be the better of the two, still worse than a real elytra:

```json
{ "type": "armorpieces:glide", "sink": 0.02, "wear_interval": 6 }
```

The wear is spent on the **chestplate** carrying them. This is the first effect any pack has shipped.

### How they are had

Group `loot_group/end.json`, tag `#armorpieces_dragon:dragonslayer`, over
`minecraft:chests/end_city_treasure` at 0.15 — plus the six recipes above for the pieces that have a
centre. That one table is **already claimed by the mod's `court` and `carapace` groups, both at
0.15**, so this is a three-group overlap: they must resolve to one pool, rolled once, at a single
0.15. `/armorpieces loot explain minecraft:chests/end_city_treasure` should say exactly that.

---

## Pack: Nether

`armorpieces_nether`. **Absorbs the roadmap's separate Nether pack** — the wither is its boss and the
dimension is its body. Netherite with gold hardware.

### Twelve pieces, one per socket

| socket | piece | what it is | fitting | centre |
|---|---|---|---|---|
| `crest` | `hoglin_hair` | the bristled tuft over the crown | — | `porkchop` |
| `brow` | `wither_mask` | the skull's face over your own | — | drop |
| `horns` | `strider_hair` | the long red side-tufts at the temples | — | `warped_fungus` |
| `pauldrons` | `wither_heads` | two wither skulls, one per shoulder | `guard` | drop |
| `back` | `blaze_halo` | a static ring of rods standing behind the shoulders | — | `blaze_powder` |
| `collar` | `wither_ribs` | the ribcage worn high at the chest | — | drop |
| `vambraces` | `blaze_bracers` | two short rods banded to each forearm | `guard` | `magma_cream` |
| `belt` | `brute_belt` | the piglin brute's gold-studded belt | `inlay` | `golden_axe` |
| `tassets` | `ghast_tendrils` | nine pale tentacles hanging from the hips | — | `ghast_tear` |
| `knees` | `magma_cops` | cracked magma cops, glowing in the seams | — | `magma_block` |
| `greaves` | `soul_greaves` | soul fire licking up the shins | — | `soul_lantern` |
| `spurs` | `hoglin_hooves` | cloven hooves at the heels | — | `crimson_fungus` |

**`wither_mask` and `wither_heads` worn together are the wither's three heads, with yours in the
middle.** That is the pack's hero idea and should be the library page's picture.

Ribs go on `collar`, not `crest`: a ribcage on a helmet top reads as nothing. `minecraft:blaze_rod` is
**taken** — it is the `bellows_visor` centre — hence `blaze_powder` and `magma_cream`.

### The one that waits

A real blaze's rods orbit it. The mod has no animation, so `blaze_halo` is a **static** ring, which is
honest and still reads. The animated version belongs to the roadmap's animation section and must not
hold the pack.

### How they are had

| piece | route |
|---|---|
| `wither_heads`, `wither_mask`, `wither_ribs` | exact `loot` rows on `minecraft:entities/wither` |
| the other nine | recipes above, plus group `loot_group/nether.json` |

The group's tables — `chests/bastion_treasure`, `bastion_other`, `bastion_hoglin_stable`,
`nether_bridge` — are **all four already claimed by the mod's `beast` group** at 0.1/0.2. This is the
widest overlap in the line and the best test of the one-pool invariant.

---

## Pack: Caves

`armorpieces_caves` — not `armorpieces_deep`. The underground is one place with three moods in it and
the warden is only the loudest; a namespace named for the warden could never hold a glow berry.

Each outfit is drawn wholly from the pack, so this one ships in two versions: the deep dark first,
the lush caves second. Both twelves are designed below so the namespace and pack name are
chosen knowing what is coming.

### v1 — the deep dark (12)

Netherite with lapis hardware. Nine of the twelve want a glow sheet, which is what gates this pack.

| socket | piece | what it is | glow | centre |
|---|---|---|---|---|
| `crest` | `shrieker_crown` | a shrieker's ribbed cone on the helm | the throat | `sculk_shrieker` |
| `brow` | `warden_mask` | the eyeless face | the cheek pulse-lines | drop |
| `horns` | `warden_antennae` | the two sensor tendrils | the tips | chest |
| `pauldrons` | `catalyst_bloom` | a catalyst's pale bone-growth over one shoulder | the bloom | `sculk_catalyst` |
| `back` | `sculk_growth` | veins spreading from a bloom between the shoulders | the veins | `sculk` |
| `collar` | `echo_pendant` | an echo shard on a cord | the shard | chest |
| `vambraces` | `sculk_veins` | veins crawling up the forearms | the veins | `sculk_vein` |
| `belt` | `ancient_candles` | the city's candles ringing the waist | the flames | `candle` |
| `tassets` | `deepslate_lames` | deepslate plates over the hips | — | `polished_deepslate` |
| `knees` | `sculk_cops` | knee cops crusted over | the crust | `deepslate_tiles` |
| `greaves` | `sculk_shins` | veins climbing the shins | the veins | `deepslate_bricks` |
| `spurs` | `sensor_tendrils` | sculk sensor whiskers at the heels | the tips | `sculk_sensor` |

`minecraft:echo_shard` is **taken** — the `runic` skin's centre — so `echo_pendant` is chest-only.

### v2 — the lush caves and the dripstone (12)

Iron with copper hardware. Written now, built later.

| socket | piece | centre |
|---|---|---|
| `crest` | `spore_blossom` — the hanging blossom, **dripping particles** | `spore_blossom` |
| `brow` | `lichen_mask` — glow lichen creeping over the visor | `glow_lichen` |
| `horns` | `azalea_sprigs` | `flowering_azalea` |
| `pauldrons` | `dripstone_spikes` | `pointed_dripstone` |
| `back` | `glow_berry_vines` | `glow_berries` |
| `collar` | `glow_squid_ink` — a stoppered vial of glowing ink | `glow_ink_sac` |
| `vambraces` | `vine_wraps` | `vine` |
| `belt` | `root_girdle` | `rooted_dirt` |
| `tassets` | `hanging_roots` | `hanging_roots` |
| `knees` | `dripstone_cops` | `dripstone_block` |
| `greaves` | `moss_greaves` | `moss_block` |
| `spurs` | `dripstone_spurs` — the weakest of the twelve; open to a better idea | `calcite` |

### The effect

`warden_mask` is the natural carrier — the warden is blind, so a mask that trades sight for something
else writes itself. Two candidates:

- `armorpieces:mob_effect` granting darkness immunity — **needs checking**, the mod may only have an
  "apply" shape and no "immunity" one
- an `if_wearer` on crouching granting a small movement attribute — the ancient city's own Swift
  Sneak, worn instead of enchanted

**The least resolved thing in the line.** Prove the condition flag exists before writing it into a
piece.

### How they are had

`warden_mask` by an exact `loot` row on `minecraft:entities/warden` — a warden is not farmable in any
sense that matters. The rest by the recipes above plus a group over `chests/ancient_city` and
`chests/ancient_city_ice_box`. `ancient_city` is already claimed by the mod's `court` group at 0.15.

---

## Pack: Hero of the Village

`armorpieces_village`. The raid, worn by the person who won it. Iron armor with emerald hardware.

### Twelve pieces, one per socket

| socket | piece | what it is | fitting | centre |
|---|---|---|---|---|
| `crest` | `witch_hat` | the pointed brim | — | `glass_bottle` |
| `brow` | `illager_mask` | the long grey nose and heavy brow | — | chest |
| `horns` | `ravager_horns` | the two chipped, down-curved horns | — | chest |
| `pauldrons` | `vex_wings` | two small grey wings at the shoulder blades | — | chest |
| `back` | `ominous_banner` | **a pole rising behind the head, banner flying above it** | `banner` | chest |
| `collar` | `totem_pendant` | the totem's face hung at the throat | `gemstone` | `totem_of_undying` |
| `vambraces` | `ravager_bracers` | the ravager's hide banded over the forearms | `guard` | chest |
| `belt` | `pillager_belt` | the crossbow belt with its quarrel loops | — | `crossbow` |
| `tassets` | `ravager_saddle` | the leather saddle skirt over the hips | — | chest |
| `knees` | `evoker_fangs` | fangs erupting from under each kneecap | — | `ominous_bottle` |
| `greaves` | `golem_plates` | the iron golem's slab legs, cut down | — | `iron_helmet` |
| `spurs` | `allay_wisps` | two small blue wisps trailing at the ankles | — | `amethyst_shard` |

The allay is the piece that makes the pack's name true: you free it from a cage at the outpost or the
mansion, which is exactly what a hero of the village does. It is also the pack's one glow piece.

### The banner is the hero piece, and the risk

The mod's `banner` is a **mounted** back banner. `ominous_banner` is the raid captain's: **a pole
standing well above the head with the cloth flying from it.** It shadows `banner` in the same socket,
which is allowed because the qualifier is the subject and it is a visibly different object. Carrying
the `banner` fitting means a player can still pattern and dye it.

**Nothing in the mod's 91 stands that far above the head.** Build this piece first in the pack, to
find out what the rig tolerates before eleven others depend on the answer.

### The effect, and the tie-in already in the mod

`armorpieces:circlet` already grants `minecraft:hero_of_the_village` from an emerald gemstone fitting.
The pack is named for that effect and must **not** duplicate it — `totem_pendant` granting the same
thing would make the mod's own piece pointless. If this pack carries an effect it should be
`evoker_fangs` with a small conditional `attack_damage`, shaped like the mod's `claws`.

### How they are had

Nothing here drops: ravagers, evokers, vexes and pillagers are all raid-farmable and the chance
belongs to the table. Group `loot_group/raid.json` over `chests/pillager_outpost` and
`chests/woodland_mansion`, plus the six recipes above. Both tables are already claimed —
`pillager_outpost` by `knightly` at 0.1, `woodland_mansion` by `knightly` at 0.15 and `court` at 0.18.

---

## Pack: Ocean — Coral, grown to twelve

`armorpieces_coral`, **unchanged**, because four pieces are already built under it and a namespace is
permanent. Only the pack's title and description widen from "Coral" to the sea.

Four pieces are built. Eight more give the pack one per socket, and *The Reef* becomes an outfit
drawn wholly from it.

| socket | piece | state | centre |
|---|---|---|---|
| `crest` | `coral_crown` | **built** | `brain_coral_block` |
| `brow` | `coral_visor` — a lattice of tube coral across the eyes | new | `tube_coral_block` |
| `horns` | `axolotl_frills` | **built** | `axolotl_bucket` |
| `pauldrons` | `kelp_mantle` | **built** | `kelp` |
| `back` | `anemone_bloom` — an anemone opening between the shoulders | new | `fire_coral_block` |
| `collar` | `nautilus_gorget` | **built** | `nautilus_shell` |
| `vambraces` | `starfish_bracers` | new | `bubble_coral_block` |
| `belt` | `sea_pickle_belt` — glowing pickles ringing the waist | new | `sea_pickle` |
| `tassets` | `seagrass_skirt` | new | `seagrass` |
| `knees` | `barnacle_cops` | new | `prismarine_shard` |
| `greaves` | `urchin_greaves` — urchin spines up the shins | new | `prismarine_crystals` |
| `spurs` | `dolphin_flukes` | new | `salmon` |

### The elder guardian, as extras

The monument gives three or four pieces, not twelve, so it does **not** get an outfit. It gets
alternates in sockets The Reef already fills, which a player can swap in themselves:

`guardian_eye` (`brow`), `guardian_spikes` (`back`), `prismarine_lames` (`tassets`),
`pufferfish_bracers` (`vambraces`) — four pieces, an exact `loot` row on
`minecraft:entities/elder_guardian` for the first two (three per monument, never respawning), the
pack's existing `loot_group/ocean.json` for the rest.

`guardian_spikes` is deliberately not `guardian_spines`, which would shadow the mod's `spine_ridge` in
the same socket. Vanilla calls them spikes anyway.

---

## When the minimum content spec lands

Not now, and not before the default pack is divided — but designed, so the cost is known.

**Animals** has eight pieces and no piece on four sockets (`crest`, `vambraces`, `tassets`,
`greaves`). Four would close it:

| socket | piece | centre |
|---|---|---|
| `crest` | `rooster_comb` | `egg` |
| `vambraces` | `cat_paws` | `cod` |
| `tassets` | `sheep_fleece` | `white_wool` |
| `greaves` | `llama_wraps` | `white_carpet` |

**Coral**'s eight are above, in its own section.

---

## The main pack — **split, 2026-09-07**

**It happened.** `docs/plans/main-pack-split.md` is the record; read it before building anything
here, because it changes what two packs in this document contain and it re-orders the build list.

The mod went from 91 pieces and 14 skins to **66 and 9**, keeping the three themes it could dress on
its own — knightly, court, wayfarer. Twenty-five pieces and five skins moved:

| destination | from the mod |
|---|---|
| **Coral** (`armorpieces_coral`) | the 6 tidal pieces |
| **The Wild Hunt** (`armorpieces_hunt`), new | the 15 beast pieces |
| **The Hive** (`armorpieces_hive`), new | the 4 carapace pieces |
| **Legends** (`armorpieces_legends`), new | `lorica`, `hoplite`, `samurai`, `varangian`, `runic` |

**Two things in this document are now out of date.**

- **Ocean needs five new pieces, not eight.** Coral owns ten pieces over seven sockets and is short
  brow, vambraces, belt, knees and spurs. Its Reef outfit borrows five instead of eight, and it has
  a second outfit, Deep Tide, it did not have.
- **The build order's cheapest item is no longer Coral's eight.** The Wild Hunt is **two pieces**
  from satisfying rule 1 — a back and a belt — which makes it the first pack in the project that
  can, and the least work to get there.

The break the earlier draft of this section called impossible was accepted rather than avoided: a
moved piece is silently lost by armor wearing it unless the pack is installed. `ArmorDecoration.CODEC`
is a `RegistryFileCodec`, so an alias table can carry the rename for a player who installs the pack;
nothing carries the player who does not, and that is the point of the split. The alias is unbuilt.

Still free, and still true: **the mod's showcase sets are `StageCommand.java` furniture**, not player
data, and **a pack's specific piece stands beside a generic one** rather than replacing it, the way
`nautilus_gorget` sits next to `gorget` in the picker.

---

## Checks run (2026-09-07)

Mechanically, against the 26.2 jar and the repository:

| check | result |
|---|---|
| every outfit is drawn wholly from its own pack, one piece per socket | **7/7 ok** — dragon, nether, caves v1, caves v2, village, coral, animals |
| recipe centres free against the 63 already in use | **54 new centres, 0 collisions** |
| recipe centres unique within the plan | **0 duplicates** |
| every centre is a real item or block in 26.2 | **all 54 resolve** |
| no pack piece reuses a mod piece's exact name | **0 clashes** |
| every loot table named exists | **13/13 present** |
| the Ender Dragon's table is rolled | **no** — the plan names no entity row for her |

What the checks do **not** cover, and what would find it: whether a piece reads at sixteen pixels
(only drawing it does), whether the banner's height fits the rig (build it first), and whether the
three-group overlap on `end_city_treasure` really resolves to one pool (`/armorpieces loot explain`,
in game, which has never been done across packs).

---

## What the line looks like finished

| pack | pieces | outfits | boss route | needs glow |
|---|---|---|---|---|
| Dragonslayer | 12 | 1 | chest only — her table is never rolled | wants |
| Nether | 12 | 1 | `entities/wither` ×3 | wants |
| Caves | 12 + 12 later | 2 | `entities/warden` | **yes** |
| Hero of the Village | 12 | 1 | none — everything is farmable | wants |
| Ocean | 8 new + 4 built, + 4 guardian extras | 1 | `entities/elder_guardian` ×2 | wants |

**48 pieces for the four new packs' first releases**, plus 12 for Caves v2, 8 finishing Coral and 4
guardian extras — **72**, before anything the default-pack division adds or moves. That is a year of
releases, and nothing here argues for doing it in one go.

## Order

Nothing starts until the default-pack division lands, because it changes what each pack holds. After
that:

1. **Dragonslayer.** Twelve pieces, a clean socket map, an obvious hero piece, and the pack that
   proves a pack can ship an **effect**.
2. **Coral's eight.** Cheapest useful work — the pack, namespace, library entry and four pieces
   already exist.
3. **Nether.** The widest overlap test (four chest tables) and the best single idea in the line.
4. **Hero of the Village.** Build `ominous_banner` first; eleven pieces depend on what it finds.
5. **Caves**, and only after glow ships.

**Glow and particles** slot in wherever there is appetite; landed before 3 they improve Nether and
Ocean as they are built.

## Open

- **The default-pack division**, which is another session's and which everything here waits on.
- **The minimum content spec** — how many pieces a pack must hold — which comes after that.
- **Whether Caves is one pack or two.** One is the recommendation; two would only be right if a player
  who wants moss should be able to refuse to download sculk.
- **Whether glow pulses**, which is animation, and which the floating blaze rods also want.
- **Where a particle spawns** — around the wearer, or at the socket, which is a much larger change.
- **The Caves effect** — whether an immunity shape exists, and whether a crouching wearer flag does.
- **`dripstone_spurs`**, the weakest piece in the line, open to a better idea.
- **Whether Breeze survives anywhere.** Trial-chamber farmable, and none of the five places is the
  trial chambers. It may simply have no home.

## What this is not

- **One mod change, named and bounded**: the glow sheet and the particle effect. Everything else —
  every piece, effect, loot row and outfit — is data a pack may ship today.
- **No animation.** `blaze_halo` is static on purpose, glow does not pulse, the floating rods wait.
- **No light sources.** Glow is a fullbright texture; nothing here lights a floor.
- **No new sockets, anchors or template items.** The twelve that exist.
- **No skins or cloths** in any first release, though Caves wants a sculk skin later and the Nether a
  tattered cloth.
