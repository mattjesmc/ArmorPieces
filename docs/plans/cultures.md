# The culture packs

> **Where this stands (2026-09-14, 03:00).** **All four packs are BUILT: 48/48 pieces, every outfit
> 12 sockets and 0 borrowed** (`pack_manifest.py`). One evening on qwen3.8-flash: 47 sessions
> straight through (23:25–02:20, ~3 min and ~$0.75 a piece, ~$36) plus one rerun — `daisho`, whose
> session found the window closed between two pieces and stopped honestly; nothing to delete, run
> again, built. **Zero `!` lines, zero forced saves, zero nudges across all 48**, and every envelope
> inside its brief's check-frame budget to the hundredth. Repo half done: lang lines, the four
> loot tags, 48 uids, sets files, `StageCommand` transcriptions; `check_authoring`, `check_lang`,
> `check_pack_line`, `check_additive`, `check_surfaces` clean (100% fitting, 100% static on all
> four). Legends is dissolved into Samurai, Norse and Antiquity. Nothing seen in game; the plugin's
> pack list carries the four (registered by the driver). The mod split ran the same night — see
> `main-pack-split.md`, "Finishing the split — as built".

`docs/plans/pack-line.md` organises packs by **place** (a boss at the centre, the dimension as the
body). This line organises them by **culture** - the armor a people wore, every piece a thing with
a real name. Both follow the same rule: **a pack's outfit uses only its own pieces**, twelve
sockets, no borrowing.

## Why these four

| pack | namespace | folder | skins moved in | the look |
|---|---|---|---|---|
| **Samurai** | `armorpieces_samurai` | `packs/samurai` | `samurai` | black lacquer, red odoshi lacing, gilt fittings |
| **Norse** | `armorpieces_norse` | `packs/norse` | `varangian`, `runic` | riveted iron, wolf fur, painted lime wood, a little gold |
| **Antiquity** | `armorpieces_antiquity` | `packs/antiquity` | `lorica`, `hoplite` | bronze and red leather, Greece and Rome together |
| **Tournament** | `armorpieces_tourney` | `packs/tourney` | - | bright steel and heraldry, azure and gold |

**Legends split naturally.** It was the only skins-led pack - five cultural skins and no pieces -
and each skin already named one of these cultures. The namespace `armorpieces_legends` was never
published, so the move costs nothing in saves; each moved skin keeps its `uid`, gains
`armorpieces_legends:<skin>` in `former_ids` (a dev world, `run/saves/Crossing`, has it), and
`uids.lock` carries the new ids. `packs/legends` is gone; `tools/sync_skin_masters.py` installs
the five into their new packs.

**Tournament is the weakest of the four on paper** - the mod's own knightly set is medieval plate
already - so its pieces are the ones the mod does *not* have: the joust's reinforces (grandguard,
lance rest, tilting grille, ecranche), the heraldry (lion crest, torse, mantling, a favour), and
the fashion (rondels, cuisses, poulaine sabatons). Its hardware is meant to take the trim the way
the mod's knightly pieces do; the heraldic colours are the static identity.

## The three surfaces, planned from the start

`piece-three-surfaces` (LESSONS #23-24, `tools/check_surfaces.py`): every piece has MATERIAL,
STATIC and FITTINGS, and the retrofit of Dragonslayer and Nether cost 22 sessions because the
briefs had not said which cube was which. Here every brief says it:

- **Samurai** - lacquer plates static black; lacing static red **under an `inlay` mask**, so the
  default is red and a player re-dyes it; iron/gilt hardware material, under `guard`.
- **Norse** - hair, fur, wood and paint static; iron and gold material under `guard`; wool and
  rawhide material under `inlay`.
- **Antiquity** - red leather and horsehair static; bronze either material under `guard` or
  **static bronze under `guard`** (bronze by default, overridable), so an iron trim does not turn a
  Corinthian helmet grey.
- **Tournament** - steel material under `guard`; azure, gold and the rose static; cloth under `inlay`.

Every piece has at least one static cube and one fitting - `verify_cultures.py` refuses a brief
without both - so nothing here is inert and nothing is an empty static sheet.

## The pieces

Centres are all free against the 101 recipes on disk and unique across the 48
(`tools/check_pack_line.py`, which now carries the four packs). Every centre resolves in 26.2.

### Armor Pieces: Samurai

| socket | piece | what it is | fitting | centre |
|---|---|---|---|---|
| `crest` | `maedate` | the gilt crescent standing up from the front of the kabuto | `guard` | `sunflower` |
| `brow` | `mempo` | the red lacquered face mask with its moustache and hanging throat plate | `inlay` | `red_dye` |
| `horns` | `kuwagata` | the flat gilt blades sweeping up from the front of the temples | `guard` | `golden_hoe` |
| `pauldrons` | `sode` | the big flat lamellar shoulder plates hanging outboard of the shoulders | `inlay` | `black_dye` |
| `back` | `sashimono` | a banner on a pole up the back, flying above the head - the hero piece | `guard` | `red_banner` |
| `collar` | `nodowa` | the laced lamellar throat guard hanging at the collar | `inlay` | `iron_chestplate` |
| `vambraces` | `kote` | the indigo armoured sleeves with a lacquered plate on the forearm | `guard` | `cyan_dye` |
| `belt` | `daisho` | the obi sash with the long and short swords thrust through it at the left hip | `inlay` | `golden_sword` |
| `tassets` | `kusazuri` | the laced lamellar skirt panels hanging from the waist over the hips | `inlay` | `red_wool` |
| `knees` | `haidate` | the cloth apron over the knee, set with small lacquered plates | `inlay` | `leather_leggings` |
| `greaves` | `suneate` | the splinted shin guards - three iron splints on indigo cloth | `guard` | `bamboo` |
| `spurs` | `waraji` | the straw sandal's heel cup and knotted red ties at the ankle | `inlay` | `wheat` |

### Armor Pieces: Norse

| socket | piece | what it is | fitting | centre |
|---|---|---|---|---|
| `crest` | `boar_crest` | a small gilt boar standing on the crest ridge of the helm | `guard` | `cooked_porkchop` |
| `brow` | `braided_beard` | a great blonde beard with two braids hanging over the chest, beaded in metal | `guard` | `shears` |
| `horns` | `war_braids` | a long braid hanging from each temple in front of the shoulder, ringed in metal | `guard` | `bone` |
| `pauldrons` | `ravens` | a raven perched on each shoulder, Huginn and Muninn | `guard` | `ink_sac` |
| `back` | `round_shield` | a painted round shield slung on the back, with an iron boss | `guard` | `oak_boat` |
| `collar` | `torc` | a twisted gold neck ring, open at the front with two knob terminals | `guard` | `raw_gold` |
| `vambraces` | `oath_rings` | three heavy arm rings stacked up the forearm over a leather wrap | `guard` | `raw_copper` |
| `belt` | `seax_belt` | a leather belt with a seax hanging horizontally across the front | `guard` | `stone_sword` |
| `tassets` | `hip_axes` | a bearded axe hanging head-up from a loop at each hip | `guard` | `stone_axe` |
| `knees` | `fur_cops` | an iron knee cop trimmed with a roll of wolf fur | `guard` | `mutton` |
| `greaves` | `winingas` | wool leg wraps up the shin, held by two leather straps | `inlay` | `brown_wool` |
| `spurs` | `snowshoes` | a snowshoe's wooden frame and webbing trailing flat behind each heel | `inlay` | `stick` |

### Armor Pieces: Antiquity

| socket | piece | what it is | fitting | centre |
|---|---|---|---|---|
| `crest` | `transverse_crest` | the centurion's horsehair crest, running ear to ear across the helm | `guard` | `leather_horse_armor` |
| `brow` | `corinthian_face` | the Corinthian helmet's bronze face with its T-shaped opening | `guard` | `copper_helmet` |
| `horns` | `ammon_horns` | a ram's horn curling at each temple - the horns of Ammon | `guard` | `cooked_mutton` |
| `pauldrons` | `epomides` | the linothorax's shoulder flaps - a bronze yoke with red leather strips hanging outboard | `guard` | `leather_helmet` |
| `back` | `scutum` | the legionary's tall red shield slung on the back, bronze boss and spine | `guard` | `painting` |
| `collar` | `phalerae` | the harness of bronze medal discs worn on the chest | `guard` | `golden_apple` |
| `vambraces` | `manica` | the segmented bronze arm guard - overlapping lames down the forearm | `guard` | `chainmail_chestplate` |
| `belt` | `cingulum` | the legionary's plated belt with its apron of hanging studded straps | `guard` | `copper_nugget` |
| `tassets` | `pteruges` | the strips of red leather hanging from the waist over the thighs | `inlay` | `brown_dye` |
| `knees` | `gorgon_cops` | a bronze knee cop bearing a gorgon's face with snakes at its sides | `guard` | `ender_eye` |
| `greaves` | `ocreae` | the muscled bronze greaves, a raised shin ridge between two rims | `guard` | `copper_boots` |
| `spurs` | `caligae` | the legionary's sandal straps - a heel cup, two ankle straps and a side lace | `inlay` | `leather_boots` |

### Armor Pieces: Tournament

| socket | piece | what it is | fitting | centre |
|---|---|---|---|---|
| `crest` | `lion_crest` | a golden lion rampant standing on a twisted torse over the helm | `inlay` | `yellow_dye` |
| `brow` | `tilting_grille` | a barred jousting visor - four horizontal steel bars between two posts | `guard` | `iron_trapdoor` |
| `horns` | `mantling` | the cloth lambrequins flowing back from the helm at the temples | `inlay` | `blue_dye` |
| `pauldrons` | `grandguard` | the jousting reinforce - a domed shoulder plate with an upstanding haute-piece | `guard` | `copper_chestplate` |
| `back` | `ecranche` | the small jousting shield with its lance notch, slung on the back | `inlay` | `blue_banner` |
| `collar` | `lance_rest` | the steel bracket bolted to the right breast that takes the lance | `guard` | `tripwire_hook` |
| `vambraces` | `favour` | a lady's favour - a rose-coloured scarf knotted round the upper forearm with trailing ends | `inlay` | `rose_bush` |
| `belt` | `sword_belt` | a leather belt with a longsword hanging vertically at the left hip | `guard` | `wooden_sword` |
| `tassets` | `cuisses` | plate thigh guards - a ridged plate over the front and outside of the thigh, one lame below | `guard` | `iron_leggings` |
| `knees` | `rondel_cops` | a knee cop with a big round rondel plate standing off its outer side | `guard` | `iron_horse_armor` |
| `greaves` | `schynbalds` | shin plates strapped over the mail - a front plate, an outer wing and a top rim | `guard` | `chainmail_leggings` |
| `spurs` | `sabatons` | plate foot armor with a long pointed poulaine toe and a heel plate | `guard` | `golden_boots` |

The `sashimono` follows `ominous_banner`: bone `mount`, bone `banner` holding the fixed 7x12x1
cloth, fittings `banner` + `guard`. It stands to `y 39.87`, 1.5 above the raid banner, and the
cloth hangs from a crossbar rather than flying from the pole.

`lance_rest` and `sword_belt` are one-sided on purpose - the lance side and the sword side - which
`collar` and `belt` allow because neither socket is mirrored. `braided_beard` and `war_braids`
hang below the helmet's `y 23`; `barbute` (22.5) and `axolotl_frills` (23.69) are the precedents.

## How the briefs were made

`gen_cultures.py` + `pieces_<pack>.py` + `verify_cultures.py` (this session's scratchpad; the
briefs are at `docs/plans/briefs/<piece>.md`). The 2026-09-12 pattern, extended:

1. **Every face snapped off every bone-mate plane on disk AND off every sibling designed in the
   same batch** (a later piece on the same bone will find the earlier one on disk), at 0.012, and
   off the shell walls. Snapping is sequential in build order. 351 faces moved.
2. **Nothing buried.** A cube entirely inside its armor shell is refused; a mount on the crown
   sits at `y 33.07`, not 32 (the helmet shell reaches 33), a pauldron cap at `y 25.07` (the
   sleeve shell reaches 25), a greave's sides at `x -5.03` (the boots shell reaches -4.8).
3. **Same-pack pieces on one bone do not intersect** cube-for-cube - the outfit shows them
   together, so the Samurai leg stacks kusazuri / haidate / suneate / waraji with gaps, not
   overlaps.
4. **No same-facing faces within 0.03 inside a piece** (a z-fight the check would call `!`).
5. Budgets derived from the snapped cubes; the check-frame budget an exact conversion; head-bone
   pair spans under 18.
6. The neighbour table names three real pieces per brief plus every same-pack sibling on the
   bone with its snapped envelope.

Rotation-free by design, all 48: rotation is where these sessions fail and none of these shapes
needed one. The ram's horn is four straight cubes in a C; the mantling four cubes stepping back
and down.

## How they are had

One loot group per pack over the chest tables of its culture's places, tag filled in the repo
half as each piece lands; every piece also craftable at its centre.

| pack | group | tables |
|---|---|---|
| Samurai | `daimyo` 0.12 | `chests/jungle_temple`, `chests/trial_chambers/reward_rare` (0.1) |
| Norse | `jarl` 0.12 | `chests/igloo_chest`, `chests/shipwreck_treasure`, `chests/village/village_taiga_house` (0.05) |
| Antiquity | `legion` 0.12 | `chests/desert_pyramid`, `chests/stronghold_library`, `chests/underwater_ruin_big` (0.1) |
| Tournament | `tilt` 0.1 | `chests/village/village_weaponsmith`, `chests/village/village_armorer`, `chests/woodland_mansion` (0.12) |

`woodland_mansion` is already the mod's `knightly` (0.15) and the Village's `raid` (0.15): a
three-group overlap that must resolve to one pool, like `end_city_treasure` in the pack line.

## The outfits

One per pack, in `armorpieces-sets.json` and transcribed into `StageCommand.java`:

| pack | outfit | armor | skin | trim |
|---|---|---|---|---|
| Samurai | **The Daimyo** | iron | `armorpieces_samurai:samurai` | redstone, guard gold, inlay red |
| Norse | **The Jarl** | iron | `armorpieces_norse:varangian` | iron, guard gold, inlay white |
| Antiquity | **The Triumph** | gold | `armorpieces_antiquity:lorica` | copper, guard copper, inlay red |
| Tournament | **The Tilt** | iron | `armorpieces:milanese` | iron, guard gold, inlay blue |

## Running it

`tools/run_surface_pass.ps1` (the qwen driver), launched detached by
`.mcptoolkit/runs/launch_cultures.ps1`. Two things it learned today:

- **With no dock open, ask for a window through `POST /window`.** The dock is a window a person
  opens from the menu and there was none; both agent windows were held by live sessions. The
  driver now asks any bridge window for one under the batch's own session id (`Get-AskedWindow`):
  a rejoin of its own, else an empty unheld agent window, else a new one pre-claimed for it.
- **The plugin's pack list is registered by the driver itself** (`tools/register_packs.py`, once
  per batch, on its own window under its own session id), because a window held by a live session
  refuses every other id, so it could not be done from outside beforehand.

## Still owed

- The batch, and the ~1-in-10 reruns (LESSONS #23); count cubes on disk, do not trust "ok".
- The repo half: lang lines, tag entries, uids, the four sets files, `StageCommand.java`,
  `check_authoring` / `check_surfaces` / `check_lang` / `check_pack_line` / `check_additive`.
- Lessons promoted from the briefs' reports into `LESSONS.md`.
- Nothing seen in game. The moved skins have never been seen in their new packs either.
- `CHANGELOG.md` and `docs/plans/main-pack-split.md` still say Legends holds the five skins.
