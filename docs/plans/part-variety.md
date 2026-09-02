# Part variety — filling out the twelve sockets

Branch `part-variety`, cut from `main` (0.2.0). This is the 0.2.x content line: no new systems,
only new parts on the sockets the mod already has. `next-templates` carries the 0.3.0 mechanics
work in parallel; nothing here should need code.

## Where we stand

Twenty parts over twelve sockets, but they are not spread evenly. The five sockets with a single
part are, awkwardly, the five most ordinary places on a suit of armour — the ones a player looks
at first and finds one answer.

| Socket | Piece | Parts today | Count |
| --- | --- | --- | --- |
| `crest` | helmet | Brush Crest, Feathering | 2 |
| `brow` | helmet | Circlet, Visor | 2 |
| `horns` | helmet | Horns, Helm Wings | 2 |
| `pauldrons` | chestplate | Spaulders | **1** |
| `back` | chestplate | Banner, Pinions, Wing Roots | 3 |
| `collar` | chestplate | Brooch, Gorget | 2 |
| `vambraces` | chestplate | Vambraces, Mittens | 2 |
| `belt` | leggings | Sash | **1** |
| `tassets` | leggings | Tassets | **1** |
| `knees` | leggings | Poleyns | **1** |
| `spurs` | boots | Spurs, Heel Wings | 2 |
| `greaves` | boots | Greaves | **1** |

The existing twenty also lean one way: they are almost all *knightly plate*. Feathering, Horns and
Pinions are the only parts that read as anything else. A second part on a socket is worth much more
when it is a different idea than when it is the same idea in another silhouette.

## Themes, so that variety is choosable rather than random

A part is worth more if it belongs to a look a player can complete. Six themes, each meant to reach
across most of the twelve sockets, so "I am wearing the Beast set" is a thing you can actually be:

- **Knightly** — plate, lames, rivets, heraldry. What the mod ships now; keep it as the baseline.
- **Beast** — fur, horn, tooth, claw, pelt. Hunter and druid.
- **Tidal** — fins, scale, shell, coral. The set for a drowned world.
- **Court** — silk, chain, gem, laurel. Regal and light, more worn than fought in.
- **Wayfarer** — straps, pouches, rope, bedroll, lantern. The traveller who is not a soldier.
- **Carapace** — chitin plate, antennae, wing cases. Insectile, alien, the odd one out.

Themes are a naming and design discipline, not a mechanic — nothing in the data models a "set".
If a set bonus is ever wanted, `armorpieces:if_fitting`-style gating is where it would live, and
that is 0.3.x territory, not this branch.

## The candidates

Each entry is: what it looks like, which theme it serves, and which of the four fittings
(`gemstone`, `guard`, `inlay`, `banner`) it would take. Fittings are cheap variety — a part with a
dye inlay is effectively sixteen parts — so most candidates should take at least one.

### `crest` — top of the skull, pointing up

Today: Brush Crest (transverse brush), Feathering (soft plumes).

| Candidate | What it is | Theme | Fittings |
| --- | --- | --- | --- |
| **Spire** | A single tapering finial rising from the crown, gothic and severe, a stone set at the tip. | Knightly | `gemstone` |
| **Comb** | A low fluted ridge running front to back, hugging the skull — the burgonet answer to the brush's height. | Knightly | `guard` |
| **Horsetail** | A socket tube at the crown with a long tail falling backward down the neck. Reads as motion where the brush reads as bulk. | Beast | `inlay` (the hair) |
| **Dorsal Fin** | A scalloped fin along the midline of the skull, webbing between the rays. | Tidal | `inlay` |
| **Antennae** | Two thin stalks rising and curling forward from the crown, bulbed at the tips. | Carapace | `gemstone` (the bulbs) |

### `brow` — across the forehead

Today: Circlet (band + stone), Visor (face slit).

| Candidate | What it is | Theme | Fittings |
| --- | --- | --- | --- |
| **Coronet** | A band with points rising from it — the crown the circlet deliberately is not. | Court | `gemstone` |
| **Nasal** | A T-bar down the bridge of the nose off a plain brow band. Cheap, iconic, very Norman. | Knightly | `guard` |
| **Laurel** | A wreath of leaves across the brow, meeting at the back. | Court | `inlay` |
| **Browband** | A cloth wrap knotted at one temple with a short tail. The un-armoured brow. | Wayfarer | `inlay` |
| **Bone Mask** | A jawless skull-front covering the upper face, eye sockets dark. | Beast | `gemstone` (the eyes) |

### `horns` — both temples, mirrored

Today: Horns (curled), Helm Wings.

| Candidate | What it is | Theme | Fittings |
| --- | --- | --- | --- |
| **Antlers** | Branching stag antlers sweeping up and back. The big silhouette this socket is missing. | Beast | — |
| **Ears** | Upright animal ears, tufted inside. | Beast | `inlay` (the inner ear) |
| **Cheek Guards** | Hinged plates hanging beside the jaw off a temple rivet. Armour where everything else here is ornament. | Knightly | `guard` |
| **Tusks** | Short thick tusks curving up from the jawline. | Beast | — |
| **Head Fins** | Swept side fins, webbed, angled back like they are cutting water. | Tidal | `inlay` |
| **Aerials** | Segmented insect antennae, angled out and down. | Carapace | — |

### `pauldrons` — both shoulders, riding on the arms

Today: Spaulders. **One part.** The highest-value socket to fill: it is the most visible ornament
on the whole suit and it has exactly one answer.

| Candidate | What it is | Theme | Fittings |
| --- | --- | --- | --- |
| **Mantle** | A thick fur ruff sitting over both shoulders. The single best-value part in this document — it changes the whole silhouette. | Beast | `inlay` |
| **Spiked Pauldrons** | Heavy domes with three spikes each, brutal. | Knightly | `guard` |
| **Epaulettes** | Flat boards with a fringe of cords hanging off the outer edge. | Court | `inlay` |
| **Beast Head** | A snarling animal head over each shoulder, jaw forward. | Beast | `gemstone` (the eyes) |
| **Lames** | Three overlapping curved plates stepping down the arm — the articulated answer to the spaulder's single shell. | Knightly | `guard` |
| **Wing Cases** | Hard elytra-style shells folded along the upper arm. | Carapace | `inlay` |

Watch: this anchor rides the arm and swings. Anything that would visually connect the two shoulders
(a chain, a draped cloak, a yoke) tears apart the moment the player walks. Those ideas belong on
`back` or `collar`.

### `back` — upper back

Today: Banner, Pinions (glide), Wing Roots. The best-served socket; add sparingly.

| Candidate | What it is | Theme | Fittings |
| --- | --- | --- | --- |
| **Cloak** | A cape falling from the shoulders to mid-thigh. The obvious hole. Wider and longer than the banner's hanging cloth, and it should take a banner's design the same way. | Court | `banner`, `guard` (the clasp) |
| **Quiver** | Arrows in a quiver slung diagonally across the back. | Wayfarer | `guard` |
| **Bedroll** | A rolled blanket and straps across the shoulders. | Wayfarer | `inlay` |
| **Carapace** | A domed beetle back, segmented and glossy. | Carapace | `inlay` |
| **Spine Ridge** | A row of dorsal plates stepping down the spine, tallest at the shoulders. | Tidal / Beast | `guard` |

### `collar` — base of the throat

Today: Brooch, Gorget.

| Candidate | What it is | Theme | Fittings |
| --- | --- | --- | --- |
| **Pendant** | A cord with a single hanging stone at the sternum. | Court | `gemstone` |
| **Fang Necklace** | A string of teeth and beads. | Beast | — |
| **Bandolier** | Straps crossing the chest with small pouches and stoppered vials. | Wayfarer | `guard` |
| **Ruff** | A pleated cloth collar standing around the neck. | Court | `inlay` |
| **Chain of Office** | Heavy square links lying across both collarbones, a plate at the front. | Court | `guard`, `gemstone` |
| **Scarf** | A wrapped neck cloth with two tails down the chest. | Wayfarer | `inlay` |

### `vambraces` — both forearms, mirrored

Today: Vambraces, Mittens.

| Candidate | What it is | Theme | Fittings |
| --- | --- | --- | --- |
| **Buckler** | A small round shield strapped over the forearm — the one part outside `back` that could carry a real banner design. | Knightly | `banner`, `guard` |
| **Wraps** | Cloth strips wound from wrist to elbow, ends tucked. | Wayfarer | `inlay` |
| **Claws** | Three blades projecting past the back of the hand. | Beast | `guard` |
| **Bangles** | A stack of loose rings at each wrist. | Court | `gemstone` |
| **Cuffs** | Wide flared bracers, bell-mouthed at the elbow. | Court | `inlay` |

### `belt` — waistline

Today: Sash. **One part.**

| Candidate | What it is | Theme | Fittings |
| --- | --- | --- | --- |
| **Belt** | A plain leather strap and a square buckle. Unglamorous and badly missed — the sash is a statement, and there is nothing quiet here. | Wayfarer | `guard` (buckle), `inlay` (strap) |
| **Fauld** | A short skirt of hanging panels, front and back, below the plate. | Knightly | `banner`, `guard` |
| **Pouch Belt** | Two or three pouches and a coil of rope at the hips. | Wayfarer | `inlay` |
| **Girdle** | Overlapping metal plates ringing the waist. | Knightly | `guard`, `gemstone` |
| **Cord** | A rope belt with a knot and a tassel falling at one hip. | Court | `inlay` |
| **Chain Belt** | A draped loop of chain slung across the hips. | Court | `guard` |

### `tassets` — both hips, riding on the legs

Today: Tassets. **One part.**

| Candidate | What it is | Theme | Fittings |
| --- | --- | --- | --- |
| **Pelt** | A fur hide hanging over each hip, ragged at the hem. | Beast | `inlay` |
| **Loin Panels** | Two long cloth strips falling to the knee. | Court | `banner`, `inlay` |
| **Scale Skirt** | Overlapping scales over the upper thigh. | Tidal | `guard` |
| **Thigh Sheath** | A strapped-down knife on the outside of each thigh. | Wayfarer | `guard` |
| **Mail Fringe** | A short curtain of chain hanging off the belt line. | Knightly | — |

### `knees` — both knees, front

Today: Poleyns. **One part**, and the tightest socket in the mod: `DecorationAnchor.KNEES` warns
that the shipped tassets and greaves leave 0.13 units between them, and that a knee part sits
*inside* the tassets' third lame. New parts here should be either flat and small, or deliberately
lapping over one neighbour.

| Candidate | What it is | Theme | Fittings |
| --- | --- | --- | --- |
| **Garters** | A narrow band with a small bow on the outer side. Flat enough to be safe. | Court | `inlay` |
| **Knee Studs** | Three rivets in a triangle, barely proud of the leg. The safest possible geometry. | Knightly | `guard` |
| **Winged Cops** | A poleyn with a fin flaring off the outer side — lapping the tassets deliberately. | Knightly | `guard` |
| **Padding** | Quilted pads, stitched in a diamond grid. | Wayfarer | `inlay` |
| **Fanged Cop** | A small beast face over each knee, mouth open downward. | Beast | `gemstone` |

### `spurs` — both heels, at the back

Today: Spurs, Heel Wings.

| Candidate | What it is | Theme | Fittings |
| --- | --- | --- | --- |
| **Rowel Spurs** | A spiked star wheel on a yoke — the cavalry spur to the shipped prick spur. | Knightly | `guard` |
| **Bells** | Small bells on ankle straps. | Court | `guard` |
| **Streamers** | Two ribbons trailing from each ankle. | Court | `inlay` |
| **Talons** | A backward-pointing bird claw off the heel. | Beast | — |
| **Anklets** | Beaded rings at the ankle. | Court | `gemstone` |

### `greaves` — both shins, front

Today: Greaves. **One part.**

| Candidate | What it is | Theme | Fittings |
| --- | --- | --- | --- |
| **Puttees** | Cloth wound up the shin from the ankle. The soft counterpart to the plate. | Wayfarer | `inlay` |
| **Boot Cuffs** | A folded-over cuff at the top of the boot, flaring out. | Wayfarer | `inlay` |
| **Scale Shins** | Overlapping scales down the front of the leg. | Tidal | `guard` |
| **Shin Spikes** | Two forward spikes off a narrow plate. | Beast | `guard` |
| **Swim Fins** | Broad fins flaring off the outer shin, webbed. A candidate for a small effect. | Tidal | `inlay` |

## Cross-cutting notes

**Coverage after all of this.** Sixty-four candidates over twenty existing parts; every socket would
reach at least six. Theme reach, counted in sockets: Beast 11, Knightly 10, Wayfarer 9, Court 8,
Tidal 5, Carapace 4. Beast and Knightly are complete looks; Tidal and Carapace are not, and each
either needs filling out or should be dropped to a handful of oddities rather than sold as a set.

**Sockets the ideas keep reaching for and not finding.** Two silhouettes came up repeatedly and have
nowhere to go: a *sabaton point* over the toe, and anything *in the hand*. `greaves` sits on the
shin front and cannot reach the foot. That is a `DecorationAnchor` change, so it is 0.3.x at the
earliest, and the enum's own comment argues sockets should stay closed — worth raising with the
`next-templates` work rather than deciding here.

**Effects.** Only Pinions carries one today, and that restraint is right: an ornament that changes
the numbers stops being an ornament. If any candidate here gets behaviour, Swim Fins is the one that
earns it, and it should be as small as the glide's `sink: 0.03`.

**Cost per part.** Geometry in Blockbench, a texture master, the data JSON, the recipe template, the
lang lines, a `modpage.yml` entry and a regenerated recipe image. `tools/check_authoring.py` must
stay clean over the whole set. Per the working convention, this is one fresh session per part, run
sequentially — the Blockbench MCP holds one project at a time.

**Suggested first batch**, if the whole list is too much at once: the five starved sockets, one part
each, picked to be the most different from what is already there — **Mantle** (pauldrons),
**Belt** (belt), **Pelt** (tassets), **Garters** (knees), **Puttees** (greaves). Five parts, five
sockets that double their content, and between them they carry four of the six themes.
