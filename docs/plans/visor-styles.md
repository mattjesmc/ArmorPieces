# Visor styles — a flat family on `brow`

The mod ships one visor. `armorpieces:visor` is four cubes reaching z −7.75, a snouted bascinet
built the way every other part in the mod is built: in geometry. It is good, and it is the *only*
answer the socket gives to the question every player asks first, which is what the front of my
helmet looks like.

Seven more, and none of them modelled. A historical visor is a plate with holes in it — a cross, a
T, an ocularium, a row of breaths — and holes are the one thing this mod gets for free. Flat
plates, the shape and the depth painted, the openings **cut**. No new systems, no code: the 0.2.x
content line, like `part-variety.md`.

Because two brow parts are never worn together, this family does not clash with the shipped
`visor` — it competes with it. So none of these repeats its snout, and the pig-faced hounskull is
deliberately absent: the mod already has it, in cubes.

## Why flat works here, in detail

Four facts, checked against the current tree.

**The renderer cuts on alpha.** `ArmorDecorationLayer` draws decorations with
`RenderTypes.armorCutoutNoCull` (`ArmorDecorationLayer.java:169`). An unpainted texel is not a
transparent texel — it is *absent*. And what makes a cut read as a hole is not its size but the
player's own skin behind it, in a warm hue no trim material produces, with a dark jamb texel
beside it for depth — the Great Helm session established that on a *one-texel* breath, and the
Savoyard session sharpened it: at eye height the cut shows the skin's own eye texel, sclera and
iris, so it reads as a face looking *through* the visor. A sight slot cut in a faceplate is a real
hole with the player behind it, which is exactly what an ocularium is. Every part in this family
gets its character from what has been removed. And `NoCull` means a plate a quarter of
a unit thick reads from both sides, so the inside of the visor is there when the head turns.

**One texel per unit, and that is exactly a face.** All 84 shipped parts use a 64×32 sheet, and the
plugin's box UV lays a cube out at one texel per unit. A plate spanning the face is **8 texels
wide** — the density Mojang draws the player's own face at on a 64×64 skin. Keep the plate's x and
y bounds on integers and the visor's texel grid falls on the head's own, so a slot cut on the
second row sits exactly over the skin's eyes. Raising a visor to a 128×64 sheet is possible
(`texture_width` is read per part) and should not be done: it would be the only part in the mod at
double density and would read as a sticker from another game.

**The master takes the armour's material.** A greyscale master is shaded through the trim ramp, so
a plate painted on the master is *steel* on an iron suit and gold on a gold one. That matters more
for visors than it did for anything else in the mod: a faceplate that ignored the armour's
material would look like a mask tied over the helmet instead of part of it. **Every part in this
family stays on the master.** No static layers. Colour, where a part wants it, is an `inlay`
fitting — one dyeable region, sixteen versions.

**Thin plates are already the house idiom.** `bangles`, `bells`, `cuffs`, `boot_cuffs` and
`dorsal_fin` all ship 0.2–0.25-unit cubes. Nothing new is being risked.

## The rules the family shares

| Rule | Why |
| --- | --- |
| Integer bounds in x and y; only thickness fractional (0.25). | A fractional size lands the face on part-texels and the paint stops lining up with the shape; a fractional *position* costs the grid it shares with the skin. |
| At most two depth steps: a face plate at z −5.35..−5.10, proud detail at −5.60..−5.30. A two-unit proud band reads as a separate piece at three metres with no fitting applied (Sallet Slit), but only if its values sit clearly outside the plate's range, and only with a lit `up` face and a dark `down` face — a flat-painted rim reads as a gap, not an overhang. | The whole point is flatness. A third step is modelling, and the shipped `visor`, at −7.75, already occupies that idea. |
| Proud cubes lap what they sit on by a whole texel row and 0.05 in z, and no two cubes of one part share a plane. | Two coincident faces of *one part* are not flagged by the checker and z-fight anyway — `browband`'s session lost a cube to exactly this, and the Bellows Visor session confirmed the silence is total: three ribs sharing two planes drew no line at all, not even a note. This rule is enforced by the author, never by the tool. The buried face underneath is a `-` note and correct. Where two proud cubes cross (the Great Helm's reinforce), step one 0.05 in front of the other. |
| **The face is empty — there is nothing to dodge.** | Measured over every part on the bone: the furthest forward any of them reaches is `brush_crest` at z −3.5, then `feathering` −3.0, `cheek_guards` −2.4, `comb` −2.1, `horns` and `helm_wings` −2.0, `antlers` −1.7, `head_fins` −1.4. Anything in front of z −4 is free at any height and any width. What is left to dodge is the shell plane (z −5), the head box's own (x ±4, y 24, y 32) and your own cubes. |
| Stay below y 32. | `comb`, `spire` and `dorsal_fin` all put their bottom face on that plane, and a cross-part `COPLANAR` is a `!`, not a note. |
| Watch `ruff` if the plate reaches below y 26. | It is the one part in the mod that reaches into this volume — Blockbench y 24.4..26.0, z −7.5..3.5, x ±5.5. A faceplate in front of a ruff is fine and should be accepted the way `laurel` accepted the horn roots; a shared plane with it is not. |
| Every face gets paint, or the cut is declared — and check the cut yourself, with Pillow. | `check_part` raises a `!` for any face with nothing behind it ("render as holes unless cut on purpose"). A *partly* painted face is only a note — which is precisely how an ocularium is made, and also means **no check can tell you the opening landed on the right row**: dump the saved master with Pillow instead (the Savoyard session). So: cut inside the front face — and cut the **same pattern in the south face**, because `NoCull` draws back faces and an opening cut only in front is filled by the inside of the back one (the Barbute session found this). Paint the four rim strips. |
| Cutting through a *proud* cube takes four rectangles, not two. | The bar's north and south **and** the plate's north and south, at matching columns — cut the bar alone and the plate shows through 0.25 behind it; cut the plate alone and the bar plugs it (the Spectacle Visor session). A full-width `down` strip under the opening is free: edge-on to the sight line. |
| The rim strips are a quarter texel. | At 0.25 thick each strip samples whatever texel it lands in. Paint the master's edge row deliberately and the rim follows, the way the shipped 0.25 parts do. |
| x ±4.0 and y 24 are worth their notes. | An 8-wide plate puts its side faces on the head's own x = ±4 plane, and a full faceplate its bottom on y 24 — the same `-` notes `bone_mask`'s cheek ridges accepted. They cannot z-fight: the plate lives 1.35 units in front of the head's front face, where those planes have no geometry. |

Sheet budget: an 8×7×0.25 plate nets 16.5 × 7.25 texels on the 64×32 sheet, a full-width rib
16.5 × 1.25. A plate and three ribs fit with room over.

## The visors

Seven — six planned, and a seventh the last session argued for and then built. The honest note
first: they are **all Knightly**. This family deepens one theme instead of spreading across six,
which is the opposite of what `part-variety.md` asked for and is right here anyway — the plan's own reckoning was that Knightly and Beast are the two complete looks, and
the front of a helmet is where Knightly is most looked at.

| Part | What it is | Opening | Fitting | Recipe centre |
| --- | --- | --- | --- | --- |
| **Barbute** | The Italian one: a smooth plate with a T cut through it, no hinge, no relief. | A T — an eye band with a slot running down to the mouth | `inlay` (border round the opening) | `minecraft:raw_copper` |
| **Sallet Slit** | The single narrow ocularium under a jutting brow, the plainest sight a helmet has. | One slot, full width | `guard` (the brow reinforce) | `minecraft:shears` |
| **Bellows Visor** | The fluted close-helm face: horizontal ribs stepping out, air between them. | Two slots between three proud ribs | `inlay` (the flutes) | `minecraft:blaze_rod` |
| **Great Helm** | The crusader front: a reinforce cross riveted over a flat plate, breaths drilled on the sword side only. | Two sights over a field of drilled breaths | `guard` (the cross) | `minecraft:netherite_ingot` |
| **Savoyard** | The death's-head visor: round eyes and a grinning row of teeth, a stone set in the brow. | Two eyes, a nose, a toothed grin | `gemstone` (the brow stone) | `minecraft:skull_banner_pattern` |
| **Frog-Mouth** | The jousting helm: one slot right at the top and a huge blank face jutting below it, so it only sees when the head is bowed. | One slot at the brow | `guard` (the lip) | `minecraft:trident` |
| **Spectacle Visor** | The *brille*: a reinforce bar across the eyes with the sights cut straight through it. The only one that cuts the raised part. | Two spectacle eyes, through the bar | `guard` (the bar) | `minecraft:spyglass` |

Recipe centres have to be checked against **three** sets, which took two sessions to establish:
the `template_*.json` (87 now), the four `fitting_template_*.json` and the fourteen
`skin_template_*.json`. `copper_ingot` was the guard fitting's, and `iron_door` the gothic
skin's, so Barbute ships `minecraft:raw_copper` and Sallet Slit `minecraft:shears`. All seven are
flat **items** — a block centre has no inventory sprite and costs a hand-drawn icon in
`tools/gen_recipe_icons.py`, which the Horsetail session paid about fifteen turns for. A block centre has no inventory sprite and costs a hand-drawn icon in
`tools/gen_recipe_icons.py`; the Horsetail session paid about fifteen turns for one.

**Geometry, shared starting point.** A `mask` bone at the anchor (0, 28, −4) holding a face plate
**x −4..4, y 24..31, z −5.35..−5.10** for a full visor, or **y 25..31 / 26..30** where the part
only covers the upper face: a quarter thick, a tenth off the shell, eight texels across. A part
that wants relief adds one proud cube per bone at **z −5.60..−5.30**, lapping the plate by a whole
texel row — a brow band (x −3..3 or ±4, y 29..31), a rib (full width, one row), a lip.

**Build order** as it ran, easiest first, each answering something for the next: **Barbute** (one cube, one
cut — the family's proof), **Sallet Slit** (adds the proud band), **Bellows Visor** (three ribs and
cut slots between them), **Great Helm** (two crossing proud cubes, and asymmetric breaths),
**Savoyard** (a gemstone on a flat family), **Frog-Mouth** (the boldest silhouette, judged last).
Briefs: `barbute.md`, `sallet_slit.md`, `bellows_visor.md`, `great_helm.md`, `savoyard.md`,
`frog_mouth.md`.

## Built — 2026-09-05

All six, one fresh `part-author` session per part on Opus, run sequentially through the bridge.
Every one saved without `force`, with **no `!` accepted on any part**; `check_part.py` clean on all
six, and each session rebuilt the mod page.

| Part | Cubes | Turns | Time | Cost | Centre shipped |
| --- | --- | --- | --- | --- | --- |
| Barbute | 1 | 31 | 5.9 min | $2.21 | `minecraft:raw_copper` |
| Sallet Slit | 2 | 32 | 4.9 min | $1.86 | `minecraft:shears` |
| Bellows Visor | 4 | 35 | 4.9 min | $1.92 | `minecraft:blaze_rod` |
| Great Helm | 3 | 29 | 6.9 min | $2.05 | `minecraft:netherite_ingot` |
| Savoyard | 3 | 30 | 7.1 min | $2.20 | `minecraft:skull_banner_pattern` |
| Frog-Mouth | 2 | 34 | 6.3 min | $2.43 | `minecraft:trident` |
| Spectacle Visor | 2 | 26 | 3.6 min | $1.42 | `minecraft:spyglass` |

Two paint calls per part, every time — no shape tool, brush or eraser was needed anywhere in the
family, because `armorpieces_paint` applies `faces` then `pixels` and `pixels` accepts `null`, so
the shading and *the cuts* go in one call. $12.67 and about 36 minutes for six parts, the cheapest
family the mod has built.

**The verdict, from the Frog-Mouth session that closed the batch.** Flat plates earned their place.
They do not compete with the cubic `visor`; they answer a different question — a face head-on
rather than a shape in profile — and the cut, showing the player's own skin at a hue no trim
material makes, is something geometry cannot do at all. Frog-Mouth is the proof rather than the
exception: it has the least detail of the six and is the most readable at three metres. **The rule
that falls out is silhouette and value break, never texel detail** — the only weak things across
all six are Savoyard's two teeth and its 1×1 gem, both small detail.

**The seventh, built the same day, and the family is closed.** Frog-Mouth's recommendation was the
**spectacle visor**, for a reason this plan did not have: a *brille* is a hole cut through the
**raised** part, and all six before it cut the plate and never the band. It was built to find out
what that costs, and the answer is *four rectangles and nothing else* — `bar.north`, `bar.south`,
`plate.north`, `plate.south` at matching columns. Cut the bar alone and you see the plate 0.25
behind it; cut the plate alone and the bar plugs the hole. **A cut proud cube is not a new
mechanism, it is the Barbute north/south rule written twice**, and the only real cost is
bookkeeping. One caveat for anyone who tries it asymmetrically: this pattern was symmetric about
the centre line, so box UV's north/south mirror could be ignored — an asymmetric cut through a
proud cube has to resolve the mirror on four faces, not two.

Two things it settled that the family did not know. **A hole through a proud cube reads *better*
than one through a flat plate**: the lit `up` face sits a texel above each opening and the dark
`down` face a texel below, so every eye gets a brow and a shadow before the jamb — three depth cues
instead of one, and that step is what makes a brille rather than two holes. And **a full-width
`down` strip directly beneath an opening is free**: it is edge-on to a −z line of sight, invisible
straight on, and reads as a shadow line under the eyes in three-quarter.

That closes it at seven. The socket now has thirteen brow parts and an eighth visor would be
repetition. The klappvisier stays dead — Sallet Slit *is* it, once flattened.

And the better 0.3.x move in this space is not a part at all: a **north-facing `banner` fitting**
turns the heraldic tournament helm from "a part we cannot build" into a fitting on the Frog-Mouth
that now exists.

## Also considered

**Hounskull / pig-face** — the mod already ships it as `visor`, in cubes, and a snout is the one
visor form that flatness cannot fake. **Klappvisier** — a small round hinged plate; too close to
Sallet Slit once flattened. **Spectacle visor** — the eye-shaped *brille*; a good later addition,
cut only to keep the batch to six. **A heraldic tournament helm**, the frog-mouth carrying real
arms, was the best idea in the set and does not fit: the shipped `armorpieces:banner` fitting is
fixed at `front: south`, so a faceplate would need a north-facing variant, and that is a new
fitting in the mod's roster rather than a new part. Worth raising for 0.3.x.

## Cost

The usual per part — geometry, master, the data JSON, the template recipe, the lang lines, a
`modpage.yml` entry, a regenerated recipe image, `check_authoring.py` clean over the set — with
one fresh session per part, run sequentially. These should be **cheaper than average**: one or two
cubes each, and the entire part is a painting job. Expect the paint calls, not the modelling, to
be where the session goes.
