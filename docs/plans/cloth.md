# Plan: cloth

A tunic. Cloth worn over the armor's surface, dyed and patterned at a loom, shaded by the armor
underneath it — the fourth thing that can be said about one piece of armor, after the part, the trim
and the skin.

## Where we stand

Three layers exist and each is closed against this:

- a **part** is geometry hung on the body, drawn by an appended render layer. Appended means *after*
  the whole equipment stack, so a part is always on top of the armor and can never be under
  anything. It also has no access to the armor's own texture, so nothing about the plate can show
  through it.
- a **trim** is one sprite in one palette. Sixteen dyes crossed with six pattern layers has nowhere
  to live in that, and the trim slot is spoken for.
- a **skin** is the armor's own texture, recoloured through a ramp *derived from the material*.
  `ArmorSkin` has no material list, no palette and no player choice by design — "the colour comes
  from the armor, not from the skin". A garment whose whole point is a colour the player picked
  contradicts it at the root.

The `cloak` part already wears a banner through `armorpieces:banner`, and that is the closest thing
shipped. It is also a demonstration of the gap: `BannerFittingRenderer` submits one pass per layer
as *sprite x flat tint*, with no shading anywhere in it. Acceptable on a one-deep flag, a decal on a
torso.

## What cloth is

A **cloth** is a garment cut out of the humanoid armor net, painted with a banner's design and baked
into the armor's own texture.

Not new geometry: it *is* the armor model, so it moves with the armor, clips nothing, and needs no
rig. Not a replacement for the armor's texture either — it is composited over whatever the armor
draws with, so what is underneath still shows in the shading.

Three properties fall out of the placement and none of them cost anything:

- **over the skin**, because the skin is the shell texture and the cloth is composited on top of the
  pixels the skin baked;
- **under every part**, because parts are an appended render layer and draw after the whole
  equipment stack unconditionally;
- **under the trim**, because the trim is a later pass in `EquipmentLayerRenderer.renderLayers` than
  the layer the cloth rides on. A surcoat covering the breastplate would in life cover its trim too,
  but the trim's edge line reading on top of the cloth is what keeps the mod's premise — the trim
  stays visible — and it is also the placement that needs no injection point of its own.

Like a skin, a cloth ships **no per-material art**: one greyscale sheet and nothing else, and an
armor material this mod has never heard of wears it the moment it is installed.

## The registry

`armorpieces:cloth`, a synced dynamic registry, loaded from `data/<ns>/armorpieces/cloth/<name>.json`:

```json
{ "asset_id": "armorpieces:tunic",
  "sheet": "shield",
  "description": { "translate": "cloth.armorpieces.tunic" },
  "loot": [{ "table": "minecraft:chests/village/village_armorer", "weight": 3, "chance": 0.15 }] }
```

- `asset_id` names the **cut mask**: `assets/<ns>/textures/entity/cloth/<path>/humanoid.png`. A
  `.../humanoid_leggings.png` beside it is read as well and is a hem; see *It stops at the waist*
  under **What this is not** for why the mod ships none. A cloth with no mask for a sheet has
  nothing to say about that sheet.
- `sheet` — `banner` or `shield`, the same choice `armorpieces:banner` offers and for the same
  reason: a design painted for a 20x40 flag and one painted for a 12x22 plate do not read the same
  stretched over an 8x12 torso panel. `shield` is the default and is the closer proportion.
- `loot` is `DecorationLoot`, read by the code that already reads a part's and a skin's.

Synced because the client bakes it, exactly as with a skin.

## The cut mask

One greyscale sheet on the vanilla armor grid, and it does three things at once:

- **alpha is how far the garment reaches.** Where it is transparent there is no cloth and the armor
  is untouched. Reach generously — the armor is what trims it; see *The armor cuts the garment*.
- **value is the cloth's own form** — the folds, the shadow under a belt, the crease at the hem.
- **the two torso panels are where the design goes.** `chest.front` (20,20 8x12) and `chest.back`
  (32,20 8x12) take the banner's pattern. Everywhere else the mask covers takes the base colour
  alone.

Sides, shoulders and hem underside are deliberately not patterned. A four-texel strip cannot carry
a charge, the shield net has nothing to sample there, and a real tabard is open at the sides anyway.

**Both panels get the design the right way round.** A banner's back is mirrored because a banner is
one sheet of cloth seen from behind; a tabard is two panels, each read from outside. So both sample
the pattern box's *north* face rather than front-and-mirrored-back.

## The bake

`ClothTextureManager`, the third of its kind and deliberately the twin of the other two. One texture
per cloth per design per material per sheet, baked on first use, cached until the next reload.

For each output texel:

1. the **base** is the texture the layer was about to draw with, upsampled — so the armor is exactly
   what it was where the cloth is not;
2. where the mask is transparent, stop — and where the ARMOR is transparent, stop as well. That
   texel is the armor, or the air the armor leaves;
3. the **colour** is the banner's — the pattern layers composited in order in pattern space, sampled
   through the panel's own rect, or the base dye where the texel is not on a panel;
4. the **value** is the mask's, plus the armor's own lighting at that texel;
5. the colour and the value go through `DecorationPalette.ofStaticColour`, which is the same
   three-stop ramp a dye fitting and a horn's ivory already use — so a dyed cloth and a dyed inlay
   beside it shade identically.

**The armor cuts the garment.** The mask says how far a cloth reaches; the armor says how far it
can. Where the piece being worn paints nothing, neither does the cloth — so the neck's notch, the
hem's taper and the bare shoulders come out of the piece itself rather than out of rows counted by
hand into a mask, and they are right on a skin's cut as readily as on vanilla's. Cut the mask
generously and let the armor trim it. It is the same image the lighting is measured from: the thing
the cloth is worn on.

### The shading, which is the whole point

Step 4 is what the feature exists for, and it is already written. `SkinBake.lightmap` measures a
texture's deviation from the middle of its own range, normalised by that range, as a signed per-texel
offset: it was written so a skin's flat pattern would pick up vanilla's rivets, edges and overhangs,
and it does the same for a flat banner. Iron's studs and diamond's facets read through the cloth;
gold's bright sheet and netherite's dark one contribute the same amount of *shape* rather than their
own contrast.

The one knob is the mix. Skins use 0.35; cloth uses **0.30**, slightly less, because a garment sits
further off the plate than a repaint of it does.

**Where the lighting is measured from** is the armor's form as the player actually sees it:

- a **skinned** piece: the skin's own greyscale master, which *is* the form;
- otherwise: the material's vanilla equipment texture.

Both are plain resources, so nothing has to be shared between the two managers for this.

### Which layer it goes on

The **last** layer of the equipment asset, which is the untinted one.

Not the shell, and the reason is leather. Leather declares a dyed shell plus an untinted overlay
carrying the stitching; the shell is multiplied by the leather's dye at draw time, so a cloth
composited into it would come out brown on undyed leather and purple on blue. The last layer is the
overlay there and the sole layer everywhere else, and it is drawn untinted in both cases. The
shading still comes from the shell — the overlay is mostly transparent and has no form to give.

This is the exact counterpart of the `isShell` rule the skin substitution already keeps, and it goes
in the same place: `EquipmentLayerRendererMixin`, still the mod's only mixin, still substituting a
texture and nothing else.

### Resolution

The cut mask is authored at 64x32 like everything else in the mod, but the bake runs at **4x**
(256x128) and the pattern is sampled at that resolution.

This matters more than it sounds. A shield pattern is painted for 12x22; the chest front is 8x12.
Composited on the vanilla grid, a bordure survives and a creeper charge turns to mush. The armor's
own texels are upsampled nearest, so the plate still reads as vanilla armor at vanilla resolution,
while the design gets 32x48 to land on. Because the cloth is a texture on a model whose UVs are
normalised, nothing else in the pipeline has an opinion about the size.

### The cache

Keyed on cloth, sheet, the texture being composited onto, and the design — base colour plus every
layer's pattern and colour, hashed. Unlike a part or a skin the key space is unbounded, because a
player can wear any banner, so this one is an **LRU of 64** and releases the texture it evicts. A
crowd in one livery is one bake; a crowd in thirty is thirty.

## How it is applied

`armorpieces:cloth` on the item, `ClothValue` — the garment, a base colour and the pattern layers,
which is `BannerFitting.Value` plus the garment. One component for the template and the armor both,
as with a skin: on a template the colour fields sit at their defaults and the serialised form is
`{"cloth": "armorpieces:tunic"}`, which is what the item model's `minecraft:select` matches on.

One item, `armorpieces:cloth_template`, for every cloth there will ever be — the same trade the skin
template makes, for the same reason.

`SmithingClothRecipe`, modelled on `SmithingSkinRecipe`:

```
cloth template + armor + a banner  ->  armor wearing that banner's design
cloth template + armor + (nothing) ->  the cloth taken off
```

The banner is consumed, as it is for a shield. **No fourth slot**: the addition slot names a
material on every other recipe in this mod, and a cloth's colour is not a material, so the slot is
free to mean this.

What may wear cloth is `#armorpieces:clothable_armor`, which ships **chest armor and nothing else**.
The recipe still accepts leg armor, so a pack that wants a hem can have one by editing the tag; head
and foot armor are refused outright, because a helmet renders on the humanoid sheet but its model
does not use the torso's UVs, and refusing is more honest than baking a texture nothing samples.

## What ships

Two cloths, one mask each:

| Cloth | What it is |
| --- | --- |
| **Tunic** | A sleeveless garment closed all the way round, hemmed at the waist. |
| **Tabard** | Two panels front and back, open at the sides, joined over the shoulders. |

Both are cut and shaded by `tools/paint_cloth_masks.py`, which reads the net out of
`tools/skin_sheets.py` so the panels cannot drift from the rects the bake samples.

## What this is not

**No drape.** The cloth is the armor's own surface, so it is tight to the torso box: no hem hanging
past it, no flare, no side slits that move. That is the price of sitting under the parts and taking
the armor's shading, and it is not recoverable within this design — a garment that *hangs* is
geometry, which is a part, and a part can have neither. The two are different features and could
one day ship as both.

**It stops at the waist, and that is the model's word not the design's.** A chestplate's layer draws
three boxes - the torso and the two arms - and a texture can only paint texels that some box of its
own item samples. There is no geometry over the thigh in that layer, so there is nothing to paint: a
chestplate's garment ends where the chestplate ends.

A hem on the LEGGINGS' leg boxes was built and looked right - three to five rows read cleanly as
cloth hanging past the breastplate - and was cut, because it is not the chestplate's to draw. It
needs the garment applied to the leggings as well, which is a second smithing operation on a second
item for a few rows of cloth, and it makes "a piece half-wearing a garment" a thing a player can
have. The capability is still there for a pack that wants it: ship a `humanoid_leggings.png` mask,
add `#minecraft:leg_armor` to `armorpieces:clothable_armor`, and no code changes. Anything longer
than a few rows should not go there anyway - a leg box inflates 0.4 where the chest box inflates 1.0,
so the hem is thinner than the garment above it, and the legs are two boxes that swing apart, so a
long one splits down the middle at every step.

**Not on the advanced smithing table yet.** Taking a cloth off works at a normal smithing table
through the empty-addition recipe, the same as a skin. Adding it there is a follow-up, and it wants
no new row: the table's last row is already the PIECE's own row, holding the two things that belong
to the piece rather than to anything worn in a socket - what is painted over its texture (the trim,
column 0) and what its texture is (the skin, column 1). A cloth is the third of that kind, what is
worn over it, so it is place 1 of that row and the box does not change size - `MAX_FITTINGS` is
already 3, which is the stride the select-fitting button ids are encoded with, and the widest socket
row already draws three columns.

## Check

- a tunic on iron, gold, diamond, netherite and leather, dyed and undyed, with a plain banner and
  with a six-layer one; the design reads and the material still reads as itself;
- the same piece skinned: the skin's form comes through the cloth, not the vanilla plate's;
- a trim over a cloth still shows its edge line;
- a part over a cloth still draws on top;
- `/reload` twice with a cloth worn, to see the bakes released and rebuilt;
- strip the mod: the armor is plain, trimmed armor again.
