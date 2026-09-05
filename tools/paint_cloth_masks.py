"""
Cut and shade the mask for every cloth the mod ships.

A cloth's art is ONE greyscale sheet, and it says three things at once:

  * alpha is the garment.  Where it is transparent the armor is untouched, and that is what makes a
    tunic a tunic rather than a paint job: it starts below the collar, leaves the arms bare, and has
    a hem.
  * value is the cloth's own form - the vertical folds, the shadow where it turns a corner, the dark
    band at the hem.  127 is the dye exactly; below is toward black and above is toward white, which
    is the three-stop ramp `DecorationPalette.ofStaticColour` builds and the same one a dye fitting
    and a horn's ivory already go through.
  * the two torso panels are where the banner's design lands.  `chest.front` and `chest.back`, read
    out of `skin_sheets` here for the same reason `ClothTextureManager` states them as constants:
    the cut and the bake have to agree on the same rectangles or a design lands off the cloth.

Written as a generator rather than drawn by hand, unlike a part's master.  A garment at this size is
flat colour with a fold rule over it - there is no silhouette to draw, because the silhouette is the
armor's - so the interesting content is exactly the numbers below, and those are better read than
eyedroppered.

Usage:
    python tools/paint_cloth_masks.py            # write the PNGs
    python tools/paint_cloth_masks.py --sheet    # also write a magnified contact sheet
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

import skin_sheets

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "textures" / "entity" / "cloth"

# The sheet a cloth is cut from, and the region of it a garment occupies.
#
# ONE sheet, and the reason is worth writing down because the net invites the opposite conclusion.
# A chestplate's layer draws three boxes - the torso and the two arms - and a texture can only paint
# texels that some box samples, so nothing a chestplate wears can reach past its own waist. The
# leggings sheet is not the way round that either: its `waist` box is the WHOLE torso again, the same
# box the chestplate's is at a smaller inflate, so a garment painted there is a garment painted under
# the chestplate and never seen. The one thing on it that is genuinely new is the two `leg` boxes.
#
# A hem on those was built and looked right - three to five rows read cleanly as cloth hanging past
# the breastplate - and was cut, because it is not the chestplate's to draw: it needs the component
# on the LEGGINGS as well, which is a second smithing operation on a second item for a few rows of
# cloth, and a piece half-wearing a garment is a worse thing to be able to make than no hem at all.
# To bring it back: paint the `leg` region's top few rows here, and add `#minecraft:leg_armor` to
# `data/armorpieces/tags/item/clothable_armor.json`. Nothing in the Java changes - the bake reads a
# `humanoid_leggings` mask whenever one is there. Anything longer than a few rows wants geometry,
# which is a part: a leg box inflates 0.4 where the chest box inflates 1.0, and the legs are two
# boxes that swing apart, so a long hem is both thinner than the garment above it and split down the
# middle at every step.
SHEETS = {"humanoid": "chest"}

# The cloth's own values. Everything is stated against 127, which is the dye undarkened.
FIELD = 150   # the flat of the cloth
FOLD = 118    # a crease running down it
LIT = 182     # the ridge beside a crease, catching the light
EDGE = 108    # where the garment turns a corner and the light does not reach
HEM = 96      # the band of shadow at the bottom edge, and the underside of it

# Which columns of an 8-wide panel carry a crease and which carry the ridge beside it. Asymmetric on
# purpose: a symmetric fold pattern reads as corduroy rather than as cloth.
FOLDS = {1: FOLD, 3: LIT, 4: FOLD, 6: LIT}


def panel(top: int, bottom: int, left: int, right: int, shoulder: bool = False) -> dict:
    """One face's texels, keyed by (col, row).

    `top`/`bottom` are the rows the garment occupies and `left`/`right` the columns; a texel outside
    them is not painted at all, so the armor shows. The last row is the hem's own shadow, and
    `shoulder` lights the first, which is right where the garment hangs from one.
    """
    out = {}
    for row in range(top, bottom):
        for col in range(left, right):
            value = FOLDS.get(col, FIELD)
            if row == bottom - 1:
                value = HEM
            elif shoulder and row == top:
                value = min(255, value + 20)
            out[(col, row)] = value
    return out


def side(top: int, bottom: int) -> dict:
    """A four-wide side face: no folds to speak of, and darker, because it is turned away."""
    return {(col, row): (HEM if row == bottom - 1 else EDGE)
            for row in range(top, bottom) for col in range(4)}


def flat(width: int, height: int, value: int) -> dict:
    return {(col, row): value for row in range(height) for col in range(width)}


# ---------------------------------------------------------------------------
# The two garments. Each names what each face of the torso box gets.

def tunic() -> dict:
    """A sleeveless garment closed all the way round, hemmed at the waist.

    Starts two rows below the collar so a gorget, a brooch or the armor's own neckline still reads,
    and is closed at the sides - which is what separates it from the tabard.
    """
    return {
        "front": panel(2, 12, 0, 8, shoulder=True),
        "back": panel(2, 12, 0, 8, shoulder=True),
        "left": side(2, 12),
        "right": side(2, 12),
        "top": flat(8, 4, FIELD + 20),
        "bottom": flat(8, 4, HEM),
    }


def tabard() -> dict:
    """Two panels front and back, open at the sides, joined over the shoulders.

    Narrower than the box by a column each side, so the armor's own edge reads down the flanks and
    the two panels are seen as separate cloth rather than as a tube. Nothing on the sides at all,
    and it starts at the shoulder where the tunic starts below the collar.
    """
    return {
        "front": panel(0, 12, 1, 7),
        "back": panel(0, 12, 1, 7),
        # Two shoulder straps joining the panels, and nothing between them.
        "top": {(col, row): FIELD + 20 for row in range(4) for col in (1, 2, 5, 6)},
    }


CLOTHS = {"tunic": tunic, "tabard": tabard}


def render(cut, sheet: str) -> Image.Image:
    """One 64x32 mask: the cut placed on the net, and nothing anywhere else."""
    img = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    px = img.load()
    region = SHEETS[sheet]
    for face, texels in cut().items():
        x, y, width, height = skin_sheets.rect_of(region, face)
        if not width or not height:
            continue
        for (col, row), value in texels.items():
            if 0 <= col < width and 0 <= row < height:
                px[x + col, y + row] = (value, value, value, 255)
    return img


def main() -> None:
    written = []
    for name, cut in CLOTHS.items():
        for sheet in SHEETS:
            img = render(cut, sheet)
            if not img.getbbox():
                # A garment that does not reach this sheet ships no file for it, which is what the
                # bake reads as "nothing to say about that layer".
                continue
            path = OUT / name / f"{sheet}.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            img.save(path)
            written.append((f"{name}/{sheet}", img))
    print(f"wrote {len(written)} cut masks to {OUT}")
    for label, _ in written:
        print(f"  {label}")

    if "--sheet" in sys.argv:
        scale = 8
        sheet_img = Image.new("RGBA", (64 * scale, 32 * scale * len(written)), (24, 24, 28, 255))
        for i, (_, img) in enumerate(written):
            big = img.resize((64 * scale, 32 * scale), Image.NEAREST)
            sheet_img.paste(big, (0, i * 32 * scale), big)
        path = ROOT / "tools" / "cloth_masks_preview.png"
        sheet_img.save(path)
        print(f"sheet: {path}")


if __name__ == "__main__":
    main()
