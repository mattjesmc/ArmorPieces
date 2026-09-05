# Brief: Chainmail

From `docs/plans/armor-skins.md`:

> **chainmail** — vanilla's own chainmail, converted rather than drawn — its sheet reduced to the
> sixteen greys and used as a master. Nearly free, and it is the one that turns chainmail from a
> material into a *look*.

**No session drew this one.** It is the only skin in `tools/skin_masters` that was not painted
through the Blockbench bridge, because there was nothing to invent: Mojang drew the weave, the
silhouette and the shading, and the whole job was to requantise them. It is
`tools/convert_chainmail_skin.py`, it runs in under a second, and it is re-runnable — the master is
an output, not a drawing, so a Minecraft bump that changes `chainmail.png` is answered by running
the script again.

    python tools/convert_chainmail_skin.py --ascii
    python tools/sync_skin_masters.py chainmail

## What the conversion does, and the one thing it adds

Three steps, described at length in the script's own docstring:

1. **Grey.** Vanilla's chainmail is faintly tinted — (164, 165, 164), (148, 145, 148) — and a
   master's texel is a ramp position, not a colour.
2. **The range.** Chainmail's 526 texels live in luma 146..189: four tones inside forty-three
   levels, which is exactly why `bake_skin.py --report` calls its ramp dead. They are stretched onto
   levels `2`..`e`.
3. **The sole.** `boot.bottom` is bare on vanilla chainmail — the one hole in its silhouette, which
   `check_skin.ALWAYS_FILLED` rightly calls a problem. Filled flat at the value the boot's own hem
   carries. **It is the only texel in either sheet that vanilla did not put there.**

The step that needed a decision is inside (2). A plain per-texel stretch of a four-tone texture
gives four values and reaches **four** of the eight ramp shades, and `check_skin` rejects that —
correctly, because four values is a flat master. But four tones is not what vanilla actually drew.
It shades every net top-bright to bottom-dark — the crown at 189, the brow rim at 180, the sides at
164, the last two rows at 148 — and had to quantise that gradient into three or four steps because
its palette has four colours in it. Sixteen greys do not have that problem, so the conversion
**restores the gradient at full resolution**: per face, vanilla's own per-row mean is smoothed with
a `[1, 2, 1]` kernel and becomes the row's base value, and each texel keeps its own deviation from
its raw row mean on top of it. The direction of the gradient, its shape and both its endpoints are
read out of the texture. Nothing is drawn.

That is what takes it to 7 of 8 shades and a master that reads on gold and diamond.

`DEVIATION_GAIN = 0.66` is the second knob. At 1.0 the stretch is uniform, and vanilla's alternating
164/180 rim texels — sixteen luma apart, invisible in game — come out five levels apart and the brow
rim becomes a dotted line shouting over the gradient it sits on. Two thirds keeps the glint.

## Why levels `2`..`e` and not `0`..`f`

The first pass mapped vanilla's range onto the ramp's own extremes, and it was wrong in a way worth
recording, because the number that showed it is reusable.

Chainmail's brightest texel is its **crown**, and chainmail's range is so narrow that the crown sits
at the very top of it: normalised into its own range, `helmet.top` is at level 15.0 while
`helmet.right` is at 5.9. On iron the same measurement gives 4.5 and 3.3; on gold 6.2 and 4.6; on
netherite 7.8 and 7.7. **Every uncompressed vanilla set puts its top faces about one level above its
sides. Chainmail appears to put them ten levels above, and that is an artefact of the compression,
not a statement about mail.** Stretched to `0`..`f` it became a solid white cap eight levels above
the field — mail's "man in a marshmallow", arrived at by arithmetic rather than by brush.

Measured across the thirteen drawn skins, `helmet.top` runs 9.1 to 13.0 and the whole-sheet mean
runs 6.8 to 8.9. At `2`..`e` this master is 6.8 overall with `helmet.top` at 14.0 — the field is in
family and the crown is still one level above the brightest drawn skin, which is left there on
purpose: it is vanilla's own claim that the crown of a mail coif is the brightest thing on it, and
the crown is only ever seen from above.

`e` rather than `f` costs nothing besides: mail's session measured `e` and `f` baking within two
luma of each other on iron *and* on chainmail.

## What is deliberately not done

The sleeve is not lengthened, the coif does not wrap the cheeks, the skirt stays three rows, and
`chest.top` stays empty. **That outline is chainmail's, and keeping it is what stops this skin from
converging with `mail`** — the plan's one explicit warning about this pair. `mail` is the harness:
1104 texels, a coif, a haubergeon a row longer, a gambeson under it, a belt. `chainmail` is 542
texels of open mesh. Side by side they do not read as the same skin, and the difference is mostly
silhouette rather than value.

There is no `silhouette` marker file. Pinning it to `chainmail` would be exactly right for every
texel but the sole, which the pin would then report as growing past vanilla's outline; the pin is
for a session that has to be held to a shape, and this one cannot leave it.

## Numbers

    542 opaque texels          (vanilla's 526, plus the 16-texel sole)
    values 34..238             levels 2..e, 7 of 8 ramp shades
    vanilla range 146..189     stretched, gain 5.535 -> 4.744 after the retune

## Done means

`python tools/check_skin.py chainmail` clean — it is; `python tools/check_authoring.py` clean — it
is; installed with `sync_skin_masters.py`, a data file, a template recipe
(`minecraft:chainmail_helmet` in a ring of paper) and a lang line. Looked at baked on iron, gold,
netherite and on chainmail itself as flat sheets. **Not yet looked at in 3D**: the skin half of
the Blockbench bridge was not exposed to the session that made this, so the one check still owed
is a look at it on the figure — most of all the crown, which is the one value in the master that
argues with the family.
