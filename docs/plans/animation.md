# Animation: a piece that moves

> **Status (2026-09-14): PLAN ONLY. Nothing here is built.** Written the day the Dragonslayer pack
> was reviewed, when the owner asked for the crystal pendant to be the first animated piece. It
> takes the decision `0.4.0.md` section 6 already made (pose-driven tracks authored in Blockbench,
> a physics chain later and client-only) and turns it into a data format, an engine, the plugin and
> check work, and a first piece. Read section 6 first; this does not repeat its reasons.

## What is asked for

Two kinds of motion, in the owner's words:

1. **Tick-animated objects.** Something on the piece that moves on its own, all the time - the
   worked case is **the End Crystal in the crystal pendant**: the game's crystal is two nested
   cubes spinning about their vertical axis (opposite ways) and bobbing, over a bedrock-and-fire
   core. The pendant should carry a tiny one that does exactly that.
2. **Movement-induced animation.** A cape that flows out behind a running wearer, a tail that
   bounces with the stride, wings that spread when the wearer flies (elytra / glide) and fold back
   when walking, and settle when standing still.

Both are **secondary motion on top of the socket's own frame**: every part already rides the
head/body/limb it is anchored to, and nothing here changes that. A bone's authored pose is the
rest pose; animation adds to it.

## The engineering fact that decides the shape

`ArmorDecorationLayer` draws a part with `collector.submitModelPart(geometry, poseStack, ...)`, and
the geometry is one shared `ModelPart` tree per part, cached by `DecorationGeometryManager`. The
26.x renderer is **deferred**: a submit is recorded and drawn later in the frame. A raw
`ModelPart` submit records the *reference*, so mutating bone rotations before the submit would
give every wearer on screen the last wearer's pose. Vanilla animates through
`submitModel(Model<S>, S state, ...)`: the collector stores the model and the render state and
calls **`model.setupAnim(state)` at flush time** (`ModelFeatureRenderer.prepareModel`, read from
the 26.2 client jar), so each submit re-poses the shared tree just before it draws it.

So: **an animated part is submitted as a `Model<DecorationPose>`**, where `DecorationPose` is an
immutable per-wearer snapshot taken in the layer, and `setupAnim` is where the maths runs. A part
with no animation keeps the raw `submitModelPart` path (nothing changes for the 300 shipped
pieces); a part with any track gets a `DecorationModel` wrapper around the same baked tree.
`Model.resetPose()` exists and restores the authored rest pose - `setupAnim` calls it first, then
applies tracks, and there is no per-frame state to leak.

## The data

Animation lives **on the bone, in the geometry file** (the resource-pack half), because it is a
property of the model, authored in Blockbench, and `bb_geo` already round-trips bones. Nothing on
the datapack half changes; a pack with animated parts loads on a mod that does not know the field
(the codec ignores it) and simply stands still.

```json
{ "name": "crystal_outer", "pivot": [0, 3, -4.5], "rotation": [60, 45, 0],
  "cubes": [ ... ],
  "animation": [
    { "type": "spin", "axis": "y", "period": 60 },
    { "type": "bob",  "axis": "y", "amplitude": 0.35, "period": 40 }
  ] }
```

A bone carries a list of **tracks**; tracks on one bone add. Every track is one of a small set of
**primitives**, each a pure function of the pose snapshot - not keyframes. Primitives are what a
check can reason about (an amplitude is an envelope), what a plugin can preview with the same
formula in JavaScript, and what a JUnit test can hold to a number. Keyframed timelines are
deliberately *not* v1: they are the largest plugin change on the roadmap (section 6 says so) and
neither the pendant nor the dragon needs them.

| type | driven by | fields | rotation / offset it adds |
|---|---|---|---|
| `spin` | time | `axis`, `period` (ticks per turn), `reverse` | rotation about `axis` of `360 * t / period` |
| `bob` | time | `axis`, `amplitude` (units), `period`, `phase` | offset along `axis` of `amplitude * sin(2pi (t/period + phase))` |
| `sway` | time | `axis`, `amplitude` (degrees), `period`, `phase` | rotation about `axis` of `amplitude * sin(...)` - an idle breathe |
| `swing` | wearer | `axis`, `amplitude` (degrees), `phase`, `driver` = `walk` | rotation of `amplitude * sin(walkAnimationPos + phase) * walkAnimationSpeed` - the stride, the tail bounce |
| `lean` | wearer | `axis`, `amount` (degrees), `driver` = `speed` \| `fly` \| `sneak` \| `swim` \| `fall` | rotation of `amount * driver` - the cape lifting with speed, wings spreading in flight |
| `move` | wearer | `axis`, `amount` (units), `driver` | offset of `amount * driver` |

`t` is `ageInTicks` (already on every `EntityRenderState`, partial-tick smoothed). The wearer
drivers are all normalised `0..1` and come from `HumanoidRenderState`, which the layer already
holds: `walkAnimationSpeed` (walk), `isFallFlying` / `fallFlyingScale` (fly, smoothed), `isCrouching`
(sneak), `swimAmount` (swim), and **`speed`, which the state does not carry**: horizontal velocity
needs one mixin into `LivingEntityRenderer.extractRenderState` writing a float onto our own
`ArmorPiecesRenderState` extension (the same kind of thing `EquipmentLayerRendererMixin` does for
cloth). `fall` is vertical velocity, the same way. Drivers get a per-driver **smoothing** (a lerp
toward the target over ~5 ticks, kept per wearer in the extension, not in the model) so a cape
does not snap.

Two rules the format enforces:
- **Mirrored sockets.** Horns, pauldrons, vambraces, tassets, knees, spurs, greaves are modelled
  once and drawn with `scale(-1, 1, 1)`. Under that mirror a rotation about **Y or Z flips sign**
  and a rotation about X does not; an offset along X flips. `setupAnim` gets the attachment's
  `mirror` flag in the snapshot and applies the sign - authors never think about it.
- **A track's extremes are part of the envelope.** `amplitude` and `amount` are bounded so the
  check can sweep them (below).

## The engine

- `client/geometry/DecorationGeometry.Bone` gains `List<Track> animation` (codec: a dispatch on
  `type`, unknown types rejected with the file named, `Lenient` list so one bad track costs one
  track). `bake()` unchanged.
- `client/animation/Track` (sealed interface, one record per primitive), `DecorationPose` (the
  snapshot: `t`, `walkPos`, `walk`, `speed`, `fly`, `sneak`, `swim`, `fall`, `mirror`),
  `DecorationModel extends Model<DecorationPose>` holding the baked root and a flat list of
  `(ModelPart, List<Track>)` resolved once by bone name at bake.
- `ArmorDecorationLayer.submitDecoration`: if the geometry has any track, build the snapshot once
  per submit (cheap) and `submitModel(model, pose, ...)` instead of `submitModelPart`. The fitting
  renderers that draw over replaced bones already receive `full`; they get the model's root so a
  gemstone on a spinning bone spins with it.
- `DecorationGeometryManager` caches `DecorationModel` beside the `ModelPart` per (asset,
  without-set); a `/reload` rebuilds both.
- The first-person hand: arm parts draw there behind a config with their own pose stack; the
  snapshot is built the same way from the player's own state, so a `swing` on a vambrace moves in
  first person too. Nothing special.

Cost: one `setupAnim` per animated part per wearer per frame, a handful of sin/cos. Zero for parts
without tracks.

## The toolchain

- **`bb_geo.py`**: `animation` round-trips per bone (`bone_to_group` / `group_to_bone`), stored on
  the Blockbench group as `armorpieces_animation` and untouched by anything else in the file.
- **The plugin**: an **Animation** section in the part panel for the selected bone - a list of
  tracks with a type picker and the fields of the table - plus a **Play** toggle that runs the
  same six formulas in JS on the viewport (`t` from a timer, drivers from four sliders: walk,
  speed, fly, sneak), so an author sees the crystal spin and the tail bounce without a game. The
  bridge gets one tool, `armorpieces_animate {bone, tracks}` (set/clear), and `armorpieces_part`
  reports the tracks a piece carries.
- **`check_part.py`**: reads the tracks and **sweeps them** - `spin` is a full turn, `bob`/`move`
  are `+-amplitude`, `sway`/`swing`/`lean` are `+-amplitude` degrees - and reports the envelope,
  reach and shell clearance at the extremes as well as at rest (`animated envelope ...`, `at the
  extreme of tail_3's swing: past leggings ...`). A track on a bone that does not exist, an
  unknown driver, a `period` of 0, an amplitude past the budget (`bob`/`move` 1.0, rotations 45)
  are `!` lines. The coplanar pass stays at rest (moving faces cannot z-fight steadily).
- **`check_authoring.py`**: the geometry codec round-trip already covers the field once the
  Python and Java codecs agree; the bake reference gains one animated case.
- **Tests**: `TrackTest` holds each primitive to numbers (a `spin` at `t = period/4` is 90
  degrees; mirror flips Y/Z and not X); `DecorationModelTest` bakes a two-bone geometry with a
  track and asserts `setupAnim` moved the right `ModelPart` and `resetPose` restored it; a
  tier-2 scenario wears the pendant, takes two screenshots 10 ticks apart and asserts they differ
  in the pendant's rectangle; tier 3 adds a still of each animated piece at rest and one mid-stride.

## The first piece: the crystal pendant

`armorpieces_dragon:crystal_pendant`, `collar`, `gemstone` fitting, currently a flat plate with a
gem (`x -3.25..3.25 y 0.85..4.95 z -4.05..-3.05` bone-local, reach 4.62). It becomes:

- a **chain** of three or four small links from the collar down the chest (static, or the master
  as the material - the pendant's metal answers the trim), ending in
- a **setting**: a bedrock-grey cradle cube (static, the crystal's base) and a small fire-orange
  texel or two on the cradle's top (static), then
- the **crystal**: bone `crystal_outer`, one cube `1.6^3` centred above the cradle with rest
  rotation `[60, 45, 0]` (the crystal's diamond pose), tracks `spin y 60` and `bob y 0.3 40`; a
  child bone `crystal_inner`, a cube `0.9^3` with the same rest rotation, tracks `spin y 60
  reverse` - the two counter-rotate exactly as the End Crystal's do. Both static: the glass is
  `#e8d8ff`-ish with a purple `#a060e0` core; the outer cube's static leaves texel-sized holes so
  the inner shows through. The bob keeps the crystal off the chest: rest at `z -4.6`, with the
  bob along y only.
- the **gemstone** fitting stays and moves to the crystal's core face - a player's gem tints the
  heart of the crystal; until set, the purple default shows.

Sizes are small on purpose - the crystal is a locket, not the block - and the animated envelope
(one turn of a `1.6` cube on the diagonal is a `2.77` sphere; a `0.3` bob) fits inside the
collar's lane (`y 0.5..5.5`, `z -6..-3.1`, `|x| <= 3.5`) with the chest shell at `z -3` clear.

It is a **glow candidate**: the End Crystal is fullbright. `pack-line.md` asks for a `<part>_glow`
fourth sheet as the line's one mod change; the pendant would be its second user after Caves. Not
part of this plan - listed so the sheet layout leaves room for it.

## Order of work

1. **Engine + data** (`Track`, `DecorationPose`, `DecorationModel`, the codec field, the layer
   branch, `speed`/`fall` in a render-state extension): one session, JUnit-tested, proved on a
   hand-edited geometry file of the pendant with a `spin` - the game is the test of the flush-time
   `setupAnim` claim above.
2. **`bb_geo` + `check_part` sweep** and the plugin's Animation section with Play: one session;
   `check_kit.mjs` asserts the round trip.
3. **The pendant**, built through the bridge from a brief like today's reworks, with
   `armorpieces_animate`; screenshots from the Play toggle in the brief's Lessons.
4. **Wearer drivers on the dragon**: `dragon_tail` (`swing x` on `tail_2..tail_6`, growing
   amplitude down the chain, phases stepped so it whips), `dragon_wings` (`lean` on `wing_l`/
   `wing_r` about Z by `fly` to spread, a small `sway` idle, `swing` folded when walking) and
   `cloak` (`lean x` by `speed`). Those bones were named for this in today's rework briefs.
5. **Later, client-only**: a `spring` track (a damped follow of the parent's motion) for the tail
   and the cape - section 6's "physics chain", still per-bone data, still swept by the check at
   its stiffness limit.

## Open

- **Blending** when two wearer drivers move one bone (walk + fly): tracks add, and `lean` by `fly`
  is meant to dominate by having `walk` fade with `walkAnimationSpeed`, which is ~0 in flight.
  Confirm on the wings before adding a weight rule.
- **Sync**: none needed - every driver is client-side render state, as vanilla's own cape is.
- **Old clients / packs**: a geometry with tracks on a mod without the field: silent still
  pieces. The pack floor (`requires`) would say `0.5.0` for a pack that relies on motion.
- **The site's thumbnails** render at rest; a short looping preview is a separate wish.
