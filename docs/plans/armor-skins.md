# Plan: armor skins

A third kind of template, beside the socket templates and the fitting templates. The three then say
three different things about one piece of armor, and none of them is in the others' way:

- a **piece** is geometry hung on the body — the mod as it stands, eighty-four of them;
- a **trim** is vanilla's accent over the armor's texture, untouched and still worth wearing;
- a **skin** is *the armor's own texture* — what the plate is, rather than what is bolted to it or
  painted over it.

Nothing here changes a silhouette. A skin is a 64×32 sheet on the same grid vanilla's armor uses, so
the model, the trims and every existing part carry on exactly as they do now.

## Where we stand

The mod has never touched the armor's own texture. Every screenshot is stock iron, gold or diamond
with parts bolted on, and the base is the one thing a player cannot change.

It also happens that vanilla's own sets are uneven, and netherite is the good one. Two differences,
both visible at texel level:

- **It wraps the cheeks.** Iron and diamond stop at the brow. Netherite's helmet runs down both sides
  of the face and leaves the face itself *open* — transparent, not painted. That is the shape.
- **It is sculpted.** Iron, chainmail and copper are close to flat; netherite has form in the chest,
  layered pauldrons and segmented legs.

The second is what a skin can carry to every other material. The first is why netherite is a good
model to draw from at all: an open face is exactly what the `brow` socket needs, and it is the reason
for the rule that **a skin never paints a visor**. Visors are parts. A skin that painted one would be
arguing with seven of them.

## What a skin is

One greyscale master pair — `humanoid` and `humanoid_leggings`, 64×32 each, on the vanilla grid.
That is the whole art cost. Two files, not eighteen.

One net on the helmet sheet is left alone on purpose. HEAD is the only slot built with
`retainPartsAndChildren`, so a helmet is two boxes: `head` at UV 0,0 inflated 1.0, which is the
helmet everyone sees, and `hat` at UV 32,0 inflated 1.5, a slightly larger box around it that no
vanilla material paints a single texel of. A skin paints the first and leaves the second empty, as
vanilla does. Painting it would hang a second shell exactly where the `brow` parts sit, burying most
of `browband` and `laurel`; `check_skin.py` reports any texel that lands there.

**The colour comes from the armor, not from the skin.** For each armor material the sheet is
recoloured through a ramp of eight shades taken from *that material's own vanilla texture*: sort its
opaque texels by luminance, take the median of each octile, dark first. Both layers are sampled
together so the leggings sheet cannot drift from the body's.

Deriving the ramp rather than authoring it buys two things. The colours are vanilla's own, so a
skinned iron helmet still reads as iron beside an unskinned one; and a modded armor material is
skinned for free, because the only thing needed from it is a texture it already ships. No palette
file exists to fall out of date.

This is the same trade `DecorationTextureManager` already makes for parts — one greyscale master,
baked per material at load — and it should be the same class of code, with the same resolution order:
a hand-authored `<skin>/<material>.png` wins if a pack supplies one, the bake is the normal path.

Three materials are not the ordinary case, and all three are now settled.

**chainmail is excluded.** It is the one material a skin should not touch. Its whole identity is the
weave, it has no colour range to derive a ramp from, and it has no metal of its own — vanilla repairs
it with an iron ingot, so even the reforging cost would be borrowed. A chainmail piece takes no skin
and the recipe does not match it.

**turtle_scute takes skins normally**, on the helmet, which is the only piece it has. Its ramp is
sampled from one sheet and runs vivid green, which reads as the material and is wanted.

**leather takes a skin of two sheets, because its armor is two layers.** Leather's equipment asset
declares them as such:

```json
"humanoid": [
  { "texture": "minecraft:leather", "dyeable": { "color_when_undyed": -6265536 } },
  { "texture": "minecraft:leather_overlay" }
]
```

The first is multiplied by the piece's `minecraft:dyed_color` at render time; the second is not
tinted at all, and is where the stitching, the straps and the buckles live. So a leather skin is
authored as a pair with exactly that division of labour — and it is the division the mod already
makes for parts, between a master and its `_static` companion. `DecorationTextureManager` reserves
the `_static` suffix for precisely this: the layer that keeps its own colour while the master takes
the material's.

Two consequences for the bake. The dyeable sheet is **not** run through a material ramp — it is
tinted, so it must be authored light, near the top of the range, or the dye multiplies into mud. And
the rule generalises past leather: any armor whose equipment asset declares a `dyeable` layer takes
the two-sheet form, so modded dyed armor is handled by asking the asset rather than by naming
leather.

Trims are unaffected on all three. `#minecraft:trimmable_armor` resolves to the four armor-slot tags,
which list every leather and chainmail piece, and the trim is drawn after every base layer with its
colour coming from the trim material's palette — so dye and trim have always been independent, and a
skin does not come between them.

## How a skin is applied

A third template family, built the way the other two are:

- **Registry** `armorpieces:armor_skin`, datapack-loaded and synced, from
  `data/<ns>/armorpieces/armor_skin/<name>.json`: an `asset_id`, a `description`, and the same
  optional `loot` list parts carry.
- **One item**, `armorpieces:skin_template`, carrying the skin as an `armorpieces:skin` component on
  the *template stack*. Exactly the trade `ModDataComponents.DECORATION` and `FITTING` already make
  and for the same reason — the item is the kind, the component is the choice, and the choice is
  datapack-driven, so a pack's new skin gets a template from a recipe with no Java.
- **A smithing recipe** of the mod's own type: the template, the armor, and in the addition slot the
  piece's own **reforging material** — an iron ingot for iron, a diamond for diamond, a turtle scute
  for the turtle helmet. Re-skinning is re-forging, and it costs the metal the piece is made of. The
  colour never needed a second material, so the slot is free to mean this instead.

  The rule is not a table the mod maintains. Every armor item carries `minecraft:repairable`, a
  `HolderSet<Item>` with `isValidRepairItem` on it, backed by vanilla's `repairs_<material>_armor`
  tags. So `matches` asks the *base stack itself* what reforges it, and the answer is right for armor
  this mod has never heard of — the same property the render layer has, got the same way. Two
  consequences worth stating: chainmail reforges with an iron ingot, because vanilla says that is what
  repairs it; and an armor item carrying no `repairable` component cannot be skinned at all, which is
  an honest refusal rather than a guess.

  The `addition` ingredient declared in the file is a tag of its own,
  `armorpieces:reforging_materials`, listing the vanilla repair items so the recipe book shows a cycle
  of them. The real constraint — that it repairs *this* piece — is enforced in `matches`, the way
  `SmithingDecorationRecipe` already puts its two extra checks there rather than in `assemble`.

**Skins are found as well as made.** A skin names its own loot tables in its data file exactly as a
part does, and that costs no new code: 0.3.0's loot work already walks every entry in a registry on
loot-table load and adds one pool per named table, with a `set_components` function putting the skin
onto its template. The same `loot` list, the same `weight` and required `chance`, the same
`/armorpieces stage loot` to judge a weight. What it buys is better here than it is for parts — a
skin template in a chest is a whole look for a whole suit, so the weights should be lower than a
part's and the tables fewer.

## Rendering it, and the one real fork

`Equippable` is a per-stack data component holding `Optional<ResourceKey<EquipmentAsset>> assetId`,
and `HumanoidArmorLayer.renderArmorPiece` reads it straight off the stack. So the texture a piece
draws with is per-item state already, and there are two ways to change it.

**(a) Rewrite the component.** The recipe copies the piece's `Equippable` and swaps `assetId` for
`armorpieces:<skin>/<material>`. No mixin, no render code, and vanilla then draws base texture and
then trim in the right order with no help. Two costs, and both are real:

- A skinned piece renders wrong with the mod removed. That breaks the invariant
  `ModDataComponents.DECORATIONS` is explicit about — *"strip this mod and the armor is still a
  valid, still trimmed item"* — which is a promise the mod has kept so far.
- The trim's `_darker` override is keyed on the equipment asset. `MaterialAssetGroup.assetId` is
  consulted with whatever asset the piece names, so a gold trim on gold armor stops darkening the
  moment the asset id is ours. Fixing it means overriding vanilla's `trim_material` files, which is
  worse than the problem.

**(b) Substitute at render time.** The piece carries `armorpieces:skin` and nothing else; a mixin on
`HumanoidArmorLayer` swaps the asset id used for the *texture* lookup only. The trim keeps the
original asset id, so the darker override survives untouched, and a piece stripped of the mod is
plain vanilla armor again. The cost is that this would be the mod's first mixin — there are none
today, and that is worth something.

**Recommendation: (b).** It keeps both invariants the codebase has been careful about, and it keeps
them for free; one mixin on one method is a smaller price than losing graceful degradation and the
trim override together.

There may be a third route with neither cost — our own render layer drawing the skin before
vanilla's trim, using `SubmitNodeCollector.order`. Whether orders compose across layers within one
entity submit is not something I have verified, so it is a thing to check, not a thing to plan on.

## The generated half

- `assets/<ns>/equipment/<skin>/<material>.json` — six lines each, one per skin × material. Generated
  by a tool, the way `gen_template_icons.py` and the recipe icons already are.
- The baked textures are registered as dynamic textures at
  `<ns>:textures/entity/equipment/humanoid/<skin>/<material>.png` and the leggings twin, by an
  `ArmorSkinTextureManager` modelled closely on `DecorationTextureManager`.

## The advanced smithing table

A skin row beside the socket rows and the trim row, in the same box. Remove clears the skin and the
piece is vanilla again — the same one-way-door problem the table exists to solve, and the same
answer.

## Which skins

Nine to begin with, mostly medieval, drawn in three batches of poles-first so that the range is
fixed by the extremes before the middle is filled in — then a second range of five once the method
was cheap enough to spend on breadth instead of on proving the ramp. Each is one greyscale master
pair; none of them changes a silhouette.

| batch | skin | what it is, and what the ramp has to carry |
|---|---|---|
| 1 | **plate** | the reference. A cheek-wrapping bascinet with the face open, a one-piece breastplate with a raised centre ridge, layered pauldrons, sabatons — netherite's silhouette redrawn deliberately across the whole range rather than netherite's sheet reused |
| 1 | **chainmail** | vanilla's own chainmail, converted rather than drawn — its sheet reduced to the sixteen greys and used as a master. Nearly free, and it is the one that turns chainmail from a material into a *look* |
| 1 | **mail** | riveted mail over a padded gambeson: a two-texel weave, a coif, a mail skirt. The hand-drawn harness `chainmail` is not — a coarser gauge, and cloth under and over the metal |
| 1 | **gambeson** | a quilted textile jack, no metal at all. Vertical quilted channels, soft edges, the least-armored pole, and the proof that the ramp is not only for steel |
| 2 | **gothic** | fluted German plate: vertical flutes on breast, pauldrons and cuisses, cusped edges. Hard light/dark striping — the most sculpted of the eight and the heaviest user of the ramp's ends |
| 2 | **milanese** | smooth rounded Italian plate, polished, almost no line work, one big besagew. The opposite pole to gothic and the test of the ramp's smooth middle |
| 3 | **brigandine** | small plates riveted inside a cloth cover: a grid of rivet heads, leather straps, a fabric field that is flatter than the hardware on it |
| 3 | **scale** | staggered overlapping scales from the collar to the skirt, one scale about two texels |
| 3 | **lamellar** | laced rectangular plates in horizontal bands, with the lacing visible between them |

**`chainmail` is what makes excluding chainmail armor cost nothing.** The material takes no skin —
its ramp is dead and it has no metal of its own — but the weave, which was that one armor's only
trick, is now on the shelf for every other material. Nothing is lost and something is gained: a gold
or diamond piece in chainmail was not previously a thing that could exist. It is also the cheapest
skin in the list, because vanilla drew it already; the work is a conversion to the sixteen greys, not
a drawing.

That does put it next to `mail`, and the two should not be allowed to converge. `chainmail` is
vanilla's weave made portable and has a job that depends on staying faithful to it; `mail` is the
harness — coarser links, a coif, a gambeson under and a skirt over. If they start to look alike,
`mail` is the one to push further.

Two others are drawn against each other on purpose: `gothic` and `milanese` are the same armor with
opposite surfaces, and if a skin can carry that difference at sixteen texels then the feature works.
The asymmetric details a real harness has — one besagew, one buckled strap — can only live on the
torso or the helmet, because the limbs share one net between left and right.

Non-medieval skins (carapace, bone, something volcanic for netherite) are deliberately not in this
list. They are easy to add once the eight are drawn, and they would not test anything the eight do
not.

### The second range: five cultures, drawn on a seeded silhouette

Once `gothic_strict` had shown that pre-seeding vanilla's own outline turns the job from "model this
armor" into "light this armor", the expensive risk in a skin — getting the shape wrong — stopped
being a risk. So the second range is not chosen to test the ramp; it is chosen for what a player
would actually pick off a smithing table, and every one of the five is **seeded from netherite**,
the only vanilla set that wraps the cheeks and runs the sleeve to row 6.

| batch | skin | what it is, and what it must not become |
|---|---|---|
| 4 | **lorica** | the Roman legionary harness. Wide continuous horizontal hoops, three values in a fixed vertical rhythm; a galea with a neck flange and cheek plates; an apron of hanging strips; a hobnailed sole. Must not become `lamellar`, whose bands are small laced plates |
| 4 | **varangian** | the Norse harness. A spangenhelm — four panels, four bright ribs, a nasal bar, a mail curtain by the face — a fur collar, and *winingas* spiralling down the leg. Must not become `mail`: the weave is the quiet field, not the subject |
| 4 | **hoplite** | the Greek bronze. A muscled cuirass with **no line work at all** — the only skin in the set whose entire vocabulary is where the light falls on a curved body. `milanese` is smooth and blank; this is smooth and anatomical |
| 4 | **samurai** | the ō-yoroi. A **grid**: plate courses crossed by vertical silk lacing, one big flat *sode*, a *kusazuri* split into hanging panels, *fukigaeshi* flaring beside the face. Must not become `lamellar` — the difference is lacing direction and the scale of the parts |
| 4 | **runic** | not history: the deep-forge harness. The set's only skin to use `0` and `f`, so a groove is genuinely black and a bevel genuinely white, with hand-composed rune bands that must never fall into a repeating tile |

Three of the five reuse the same two islands the netherite silhouette hands them, and spend them
differently — which is a fair summary of what a seeded skin is. `helmet.front` cols 3..4 at rows
3..4 is a nasal bar on `varangian` and a nose guard on `runic`, but a *shadow* on `lorica`,
`hoplite` and `samurai`, whose helmets have none. `helmet.back` row 6 is a galea's flange, a
kabuto's lowest shikoro tier, and a dwarven neck plate.

## How a skin is authored

Built 2026-09-04, alongside this plan, so the eight above can be drawn before the Java half exists.
A skin is authored the way a part is — in Blockbench, on the real figure, through the MCP bridge —
because the one thing that cannot be judged from a flat sheet is armor.

- **`tools/skin_sheets.py`** is the model of the two sheets: the seven box-UV nets, their face
  rectangles and their anatomical names, read out of `mc_humanoid` rather than written down again.
  It also carries the ASCII form a sheet is edited in — `.` transparent, `0`-`9` and `a`-`f` the
  sixteen greys, a space for "leave this texel alone" — and prints any sheet, vanilla's included,
  as a drawing to work from (`--vanilla netherite`).
- **`tools/bb_rig.py --skin <dir>`** builds the skin rig: the same player wearing all four slots at
  their real inflate, with the ARMOR cubes unlocked and their two sheets linked to
  `tools/skin_masters/<name>/`.
- **The Blockbench plugin** gained a skin workspace beside the piece one — open, paint, save, close,
  a live material preview, and a status folder the bridge checks. Tools > Armor Pieces > Open Armor
  Skin... opens one by hand.
- **The bridge** (`tools/mcp`) serves `armorpieces_skins`, `_open_skin`, `_skin_sheet`, `_skin_paint`,
  `_skin_material`, `_skin_check`, `_save_skin`, `_close_skin`. Painting is addressed by net and
  face, so a stamp that would run off a face is refused rather than landing somewhere wrong.
- **`tools/check_skin.py`** is the check, run after every editing call and again from the command
  line: paint outside every net, colour on a greyscale sheet, a slot with nothing on it, a painted
  visor, and the value range against the eight shades.
- **`.claude/agents/skin-author.md`** is one session per skin, with the vanilla coverage table in it.

What the plugin still owes is the datapack half. Painting works; writing does not. A **New Skin**
dialog should do for a skin what the Part dialog does for a part — write the `armor_skin` data file,
its template recipe with the two item fields and the Craftable switch, its loot rows, and the lang
line into the right half of the right pack — so that a skin is authored end to end in Blockbench and
never by hand. That is the same code path the Part and New Fitting dialogs already are, pointed at a
third registry.

The masters stay in `tools/skin_masters/` for now. Where they are installed into the resources is
the Java half's call; `tools/sync_decoration_masters.py` is the shape to copy, and
`assets/armorpieces/textures/entity/skin/<skin>/{humanoid,humanoid_leggings}.png` is the obvious
place.

## What the bake turned out to need

The rule as first written above — sort the material's texels by luminance, take the median of each
octile — does not survive contact with the textures. Measured over the eight materials:

    material     texels  vanilla luma  eight shades span
    leather         940     153..224      60
    chainmail       526     146..189      43
    iron            928     183..255      46
    gold            928     157..255      82
    diamond         912     147..255      81
    netherite       971      10..111      78
    turtle_scute    216      58..142      75
    copper          928     104..210      76

Two corrections came out of that, both in `tools/bake_skin.py`, and the Java bake should make the
same ones:

1. **The stops are spaced along the material's range, not by octile.** An armor texture spends most
   of its texels on one or two values, so four of the eight octiles came back the same colour and
   half the ramp was flat. The stops now run from the 5th to the 95th percentile of luminance, each
   taking the median colour of the texels nearest it — still a colour the material really uses, but
   eight different ones.
2. **A ramp narrower than 100 luma is deepened.** Iron's own eight shades span forty-six levels: bake
   a master straight through them and the master's form is flattened back down to iron's, which is
   the very thing the feature exists to fix. So the lightest shade stays exactly where the material
   put it and the darker ones are pushed down, in place, until the eight span 100. Each keeps its
   hue and saturation, so the material still reads as itself. Netherite, the one vanilla set with
   real form, spans 78 unaided and is barely touched; chainmail, which spans 43, gets a ramp its
   weave can be seen in — which is most of that open question answered.

3. **Vanilla's own lighting is mixed back over the master.** A master is a pattern: it says where
   the flutes and the scales and the quilting are. What it cannot say is that the top of a shoulder
   catches the light, that a plate has an edge, that there is shadow under an overhang - and vanilla's
   textures carry all of it. Replacing every value with the pattern threw it away, and the skins came
   out looking like painted paper. So the bake now adds vanilla's own deviation back on top of the
   master's value, *before* the table lookup:

       centre  = (p5 + p95) / 2 of that material's luminance      # NOT the median: an armor texture
       spread  = p95 - p5                                          # sits at one end of its own range
       delta   = clamp((luma(vanilla texel) - centre) / spread, -0.5, +0.5)
       value'  = clamp(master value + LIGHT_MIX * 255 * delta, 0, 255)
       colour  = table[value']

   with `LIGHT_MIX = 0.35`. Normalising by each material's own spread is what makes this fair: iron,
   gold and netherite then contribute the same amount of SHAPE (+-45 of 255, about two and a half
   levels) rather than their own contrast. A texel vanilla does not paint contributes nothing.

`python tools/bake_skin.py --report` prints the ramp table, `--contrast` and `--levels` what a value
step buys, and `--faithful` bakes the medians as they come. `--light 0` bakes without the mix, which
is the honest before-and-after.

## What the Java half has to match

The bake is now three things stacked, and the mod has to do all three or a skin looks one way in
Blockbench and another in game: the percentile ramp, the deepening to `MIN_SPAN`, and the lighting
mix above. Two consequences for how the Java is organised:

- **The mod needs vanilla's armor textures at bake time**, not just its own masters - the lightmap
  comes out of `minecraft:textures/entity/equipment/humanoid/<material>.png`. That is a resource it
  already has, but it means the bake belongs where resources are available (a resource-reload
  listener building one lightmap per material, then one baked pair per skin per material), not in a
  static initialiser.
- **The whole bake is per-texel and stateless**: `colour = table[clamp(master + light)]`. A 256-entry
  table and a 64x32 signed byte map per material is the entire state, so it can be computed once on
  reload and reused for every skin.

`docs/plans/skin-bake-reference.json` (regenerate with `python tools/bake_skin.py --reference`) holds
the eight shades, samples down each 256-entry table, and a SHA-1 of each material's whole lightmap. A
Java test that reads that file and disagrees with it has found a real difference, which is the point:
the two implementations are held to the same numbers rather than to the same prose.

## What was built

The Java half, 2026-09-04. Eight skins ship — `plate`, `mail`, `gambeson`, `gothic`, `milanese`,
`brigandine`, `scale`, `lamellar`. The ninth, `chainmail`, is not drawn yet; `gothic` ships from the
freehand redraw rather than from the silhouette-pinned `gothic_strict`, which stays in `tools/`.

Settled differently from the plan above, or settled where it was left open:

- **The fork went to (b), the mixin, and it is one mixin on one method.** Not on
  `HumanoidArmorLayer` though: on `EquipmentLayerRenderer.renderLayers`, where the layer's own
  texture is looked up — so the asset id vanilla was handed is still the one the trim sprite is keyed
  on a few lines further down the same method. `SubmitNodeCollector.order` was never tested, and does
  not need to be: substituting the texture rather than the asset keeps both invariants at no cost,
  and the third route would have bought nothing this does not.
- **No equipment asset files are generated, and none are needed.** The plan's "generated half"
  belonged to route (a): with the texture substituted at render time there is no second asset to
  declare, so the whole `assets/<ns>/equipment/<skin>/<material>.json` cross product — and the tool
  that would have written it — is gone. What a skin ships is two PNGs and a data file.
- **Which layer a skin replaces is asked of the ASSET, not of a material list.** The shell is the
  dyeable layer where the asset declares one and the only layer where it does not, so leather's
  tinted shell takes the skin and its stitching overlay stays vanilla's, and a modded two-layer set
  is handled without being named. A leather skin is therefore one sheet after all rather than a
  master-and-`_static` pair: the dyeable layer is baked through leather's own ramp, which runs light,
  and the dye multiplies into it as it always did.
- **Chainmail is excluded by a tag**, `#armorpieces:unskinnable_armor`, rather than by a name in
  Java — so a pack can add its own unskinnable armor, or disagree and take chainmail out.
- **The advanced table gained a skin PLACE, not a skin row.** The row box is exactly five rows tall
  and a chestplate already fills it, so the last row became the piece's own: the trim in column 0 and
  the skin beside it in column 1, which is the column model a part's fittings already use. No art
  changed and the screen did not grow.
- **The bake lives in `SkinBake`**, over plain `int[]` pixels with no client class in sight, so the
  test below can hold it to the reference file without a game.
- **`/armorpieces stage skins`** is the sixth stage mode: every skin down the rows, every base armor
  set across the columns. The only mode whose columns are the armor rather than the trim, because
  that is the axis a skin's colour comes from.

- **Every skin has its own template icon, and the icon is the skin.** Not an emblem for it: the top
  ten rows of the skin's own chest front, lifted off the sheet that ships, greyed and levelled into
  the card's range, set in the same 10x10 recess the socket and fitting templates use. Nothing is
  resampled — the face is 8x12 and ten of the twelve rows are taken, because a scaled sheet is a
  blurred sheet and at sixteen pixels blur is the one thing a swatch cannot afford.

  Hand-drawn emblems were tried first, twice, and thrown out. Thirteen of them in one palette at
  10x10 came out as thirteen grey lattices, and the ones whose identity is a *culture* rather than a
  construction could not be drawn at that size at all — a spangenhelm needs more texels than the
  recess has. Giving the skins a bigger frame of their own fixed the helmets and cost the family
  resemblance, and the swatch turned out to need neither: it is legible, it is the armor itself, and
  it cannot drift from it.

  It also makes the set self-maintaining. `gen_template_icons.py` walks every skin with art in the
  resources and writes the icon, the item model and the `minecraft:select` case together, so a skin
  drawn later gets all three by existing and there is no JSON to write. A pack's own skin cannot add
  a case (select does not merge) and falls back to the generic icon; `check_authoring.py` fails if a
  case and its texture ever stop naming each other.


## Check

`./gradlew test` — `SkinBakeTest` reproduces `docs/plans/skin-bake-reference.json` for all eight
materials: the eight shades, the sampled 256-entry table, and the SHA-1 of each material's whole
lighting map. It reads vanilla's textures off the test classpath, so it needs no asset cache.
PASSES.

`python tools/check_authoring.py` round-trips every skin's data file and its template recipe, checks
that both master sheets are really in the resource pack, and that no two shaped recipes share a
crafting grid. PASSES.

`python tools/check_skin.py <skin>` is clean for all eight. `milanese` was not when it was installed:
its thigh top was unpainted, which is a hole seen from above. Filled at the value its front face
uses, and that is the only change made to any master.

Still to do in game: `/armorpieces stage skins` and read the eight columns — does each skin still
read as the material it is on; put a vanilla trim over a skinned piece and confirm it is unmoved and
still darkens on matching material; wear a brow part over a skinned helmet and confirm the face is
still open behind it; remove the skin at the advanced table and get vanilla armor back.
