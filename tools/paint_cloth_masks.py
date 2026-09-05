"""
Cut and shade the mask for every cloth the mod ships.

A cloth's art is ONE greyscale sheet, and it says three things at once:

  * alpha is HOW FAR the garment reaches - which faces of the torso box it covers, and how wide.
    How far it CAN reach is the armor's to say on any face the armor USES: the bake clips the cloth
    to the armor's own silhouette there, so the neck's notch and the hem's taper come from the piece
    being worn rather than from rows counted by hand here.  Cut generously; the armor trims it.
    The box's TOP and UNDERSIDE are the exception, because vanilla paints neither - a breastplate has
    no lid - and a face the armor never uses is not a hole to respect but room to use: a tunic's
    shoulders and a tabard's straps live there and are never trimmed.
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

# Which columns of an 8-wide panel carry a crease and which carry the ridge beside it. Asymmetric on
# purpose: a symmetric fold pattern reads as corduroy rather than as cloth.
FOLDS = {1: FOLD, 3: LIT, 4: FOLD, 6: LIT}


def panel(left: int, right: int) -> dict:
    """One 8-wide face of the torso box, full height, in columns `left`..`right`.

    Full height because the armor is what ends it - see the module note. The top row is lit, which is
    right wherever a garment hangs from a shoulder; there is no hem row, because where the hem falls
    is the armor's business and vanilla already darkens its own bottom edge, which the armor light
    carries through.
    """
    return {(col, row): (FOLDS.get(col, FIELD) + (20 if row == 0 else 0))
            for row in range(12) for col in range(left, right)}


def side() -> dict:
    """A four-wide side face: no folds to speak of, and darker, because it is turned away."""
    return {(col, row): EDGE for row in range(12) for col in range(4)}


def flat(width: int, height: int, value: int) -> dict:
    """A whole face at one value - for the top and the underside, which have no form to speak of."""
    return {(col, row): value for row in range(height) for col in range(width)}


# ---------------------------------------------------------------------------
# The two garments. Each names what each face of the torso box gets.

def tunic() -> dict:
    """A sleeveless garment closed all the way round, hemmed at the waist.

    Closed at the sides, which is the whole of what separates it from the tabard. It does not stop
    short of the collar on purpose any more: the armor's own neck notch is what leaves the throat
    bare, and it does so on a skin's cut as readily as on vanilla's.
    """
    return {
        "front": panel(0, 8),
        "back": panel(0, 8),
        "left": side(),
        "right": side(),
        # The shoulders. Vanilla paints nothing here - a breastplate has no lid - so the face is the
        # garment's alone, and the bake leaves a face the armor never uses uncut. Only the outer
        # column each side is ever seen, the head covering the rest, and that is the shoulder line.
        #
        # The box's UNDERSIDE is the other face vanilla leaves empty and it is deliberately left
        # empty here too. It is not a hem: it is a horizontal plate at the waist, the full width of
        # a box inflated past the body, and it cuts straight through the legs at every step.
        "top": flat(8, 4, FIELD + 20),
    }


def tabard() -> dict:
    """Two panels front and back, open at the sides, joined over the shoulders.

    Narrower than the box by a column each side, so the armor's own edge reads down the flanks and
    the two panels are seen as separate cloth rather than as a tube. Nothing on the sides at all.
    """
    return {
        "front": panel(1, 7),
        "back": panel(1, 7),
        # Two straps over the shoulders joining the panels, with the neck open between them. Without
        # these the two panels hang off nothing, which is what a tabard famously does not do.
        #
        # Out to the outermost columns on purpose. The top face is eight texels stretched over a box
        # inflated to ten units wide, and the head covers all but the outer one on each side - a
        # strap that stopped short of column 0 would be a strap nobody ever sees.
        "top": {(col, row): FIELD + 20 for row in range(4) for col in (0, 1, 2, 5, 6, 7)},
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
