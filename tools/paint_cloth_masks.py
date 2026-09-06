"""
Cut and shade the mask for every cloth the mod ships.

A cloth's art is a greyscale sheet PER SHEET OF THE ARMOR - the chestplate's torso and arms, and
the leggings' two legs, which is where the hem past the waist lives - and each says three things at
once:

  * alpha is HOW FAR the garment reaches - which faces of a box it covers, and how wide.
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

# The boxes a cloth is cut from, by the sheet each is on.
#
# THREE of them over two sheets, and which three is the whole of why a garment reaches where it does.
# A texture can only paint texels that some box of its own item samples. The chestplate's layer draws
# the torso and the two arms, so nothing painted for it reaches past the waist. The leggings' layer
# draws two more: the two `leg` boxes, which are the hem, and a `waist` box which is the WHOLE torso
# again at a smaller inflate - the belt, and the only rows of it vanilla paints anything on.
#
# The waist box is worth cutting even though it lives inside the chestplate, because the chestplate
# does not close: every vanilla material scallops the bottom row or two of its torso away, and what
# shows through that scallop is the belt. Cloth on the chest box stops there - correctly, the armor
# is what ends it - and without cloth on the belt behind it a garment reads as two bands with the
# armor's own metal between them. Cut it and the seam closes.
#
# The hem is not the leggings' garment, though - it is the chestplate's, reaching down. The renderer
# reads `armorpieces:cloth` off the CHEST slot when it paints the leggings sheet, so one component
# and one smithing operation buy all of it and a piece cannot half-wear a garment. What the leggings
# supply is the geometry and the light: no leggings, no hem, the same rule the neck notch already
# follows a layer up.
#
# Two things the hem has to live with, and both are answered in the numbers below rather than in
# code. A leg box inflates 0.4 where the chest box inflates 1.0, so the garment above OVERHANGS the
# hem by half a texel - which is why the hem's top row is its darkest, reading as cloth tucked under
# cloth rather than as a ledge. And the legs are two boxes that swing apart, so a hem is capped at
# the rows that still read at a full stride; anything that genuinely HANGS is geometry, which is a
# part rather than a cloth.
SHEETS = {"humanoid": ("chest",), "humanoid_leggings": ("waist", "leg")}

# The cloth's own values. Everything is stated against 127, which is the dye undarkened.
FIELD = 150   # the flat of the cloth
FOLD = 118    # a crease running down it
LIT = 182     # the ridge beside a crease, catching the light
EDGE = 108    # where the garment turns a corner and the light does not reach

# Which columns of an 8-wide panel carry a crease and which carry the ridge beside it. Asymmetric on
# purpose: a symmetric fold pattern reads as corduroy rather than as cloth.
FOLDS = {1: FOLD, 3: LIT, 4: FOLD, 6: LIT}

# The same, four wide, for a leg. Symmetric whether it likes it or not: the left leg is the right
# one's cube mirrored at the same UV, so the pair is always a mirror about the body's centre line -
# which is the one place symmetry is right anyway, since that is where a real hem's centre fold is.
LEG_FOLDS = {1: FOLD, 3: LIT}

# The hem's own two edges, which the chest panel has neither of. Its top is overhung by the garment
# above (see the SHEETS note) and its bottom is where the cloth simply ends - the armor does not end
# there, so unlike the chest panel nothing else darkens it.
TUCK = 96     # the row the garment above overhangs
HEM = 112     # the last row, the weight of the cloth's own edge


def panel(left: int, right: int) -> dict:
    """One 8-wide face of a torso box, full height, in columns `left`..`right`.

    Both torso boxes, the chestplate's `chest` and the leggings' `waist`, because they are the same
    rectangle at the same height on their own nets and the garment on them is the same garment.

    Full height because the armor is what ends it - see the module note. On `chest` that is the
    scalloped bottom, on `waist` it is everything above the belt. The top row is lit, which is right
    wherever a garment hangs from a shoulder and invisible on the waist, whose top rows the
    chestplate covers whatever they say; there is no hem row, because where a torso box's cloth ends
    is the armor's business and vanilla already darkens its own bottom edge, which the armor light
    carries through.
    """
    return {(col, row): (FOLDS.get(col, FIELD) + (20 if row == 0 else 0))
            for row in range(12) for col in range(left, right)}


def side() -> dict:
    """A four-wide flank of a torso box: no folds to speak of, and darker, because it is turned away."""
    return {(col, row): EDGE for row in range(12) for col in range(4)}


def flat(width: int, height: int, value: int) -> dict:
    """A whole face at one value - for the top and the underside, which have no form to speak of."""
    return {(col, row): value for row in range(height) for col in range(width)}


def hem(rows: int, folds: dict | None = None, field: int = FIELD) -> dict:
    """The top `rows` of a four-wide leg face: the garment continuing past the waist.

    Three bands, and the outer two are the whole of what makes it read as a hem rather than as a
    painted stripe. The first row is TUCKed under the garment above, which genuinely overhangs it -
    the chest box inflates 1.0 and this one 0.4. The last is the cloth's own edge, and it needs its
    own weight because nothing else supplies one: the armor does not stop here, so the bake's clip
    against the armor's silhouette - the thing that shapes every other edge of a garment - has
    nothing to say about where a hem ends.
    """
    folds = LEG_FOLDS if folds is None else folds
    out = {}
    for row in range(rows):
        for col in range(4):
            if row == 0:
                value = TUCK
            elif row == rows - 1:
                value = HEM
            else:
                value = folds.get(col, field)
            out[(col, row)] = value
    return out


# ---------------------------------------------------------------------------
# The two garments. Each names what each face of each box it reaches gets, by sheet.

def tunic(sheet: str) -> dict:
    """A sleeveless garment closed all the way round, hanging to the top of the thigh.

    Closed at the sides, which is the whole of what separates it from the tabard. It does not stop
    short of the collar on purpose any more: the armor's own neck notch is what leaves the throat
    bare, and it does so on a skin's cut as readily as on vanilla's.

    The longer of the two hems, and closed there as well: each leg carries its own sleeve of cloth,
    so the legs swinging apart opens a gap between two hemmed garments rather than tearing one in
    half, and five rows still read at a full stride.
    """
    if sheet == "humanoid_leggings":
        return {
            # The belt, behind the chestplate's scalloped bottom. Full height and trimmed by the
            # armor, which is the module note's rule doing exactly the work it was written for: the
            # rows vanilla leaves empty here - everything above the belt - are cut away for free, and
            # a material that scallops more of its chestplate away simply shows more belt and gets
            # more cloth to cover it.
            "waist": {"front": panel(0, 8), "back": panel(0, 8), "left": side(), "right": side()},
            "leg": {
                "front": hem(5),
                "back": hem(5),
                # The flanks are the point of a closed hem, and the INNER one especially: it is the
                # face a walking player shows the world, and an unpainted face is a hole rather than
                # a shadow. Darker than the panels because it is turned away, exactly as the flanks
                # of the garment above are - and it carries the base colour alone, never the design,
                # which is the bake's own rule for anything off the two torso panels.
                "left": hem(5, folds={}, field=EDGE),
                "right": hem(5, folds={}, field=EDGE),
            },
        }
    return {"chest": {
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
        # a box inflated past the body, and it cuts straight through the legs at every step. The hem
        # on the sheet above is what covers that ground, on geometry that actually hangs there.
        "top": flat(8, 4, FIELD + 20),
    }}


def tabard(sheet: str) -> dict:
    """Two panels front and back, open at the sides, joined over the shoulders.

    Narrower than the box by a column each side, so the armor's own edge reads down the flanks and
    the two panels are seen as separate cloth rather than as a tube. Nothing on the sides at all.

    The shorter of the two hems, and that is the same difference one box further down. Two flat
    panels split down the middle when the legs part, and there is no bake that fixes it - so the
    tabard stops at three rows where the tunic goes to five, and the two garments make the limit
    visible instead of implying it.
    """
    if sheet == "humanoid_leggings":
        return {
            # The belt, inset to the same columns as the panels above so the flanks read down the
            # whole garment rather than closing up at the waist.
            "waist": {"front": panel(1, 7), "back": panel(1, 7)},
            # Front and back only, and full width: the inset that gives the panels above their edge
            # is against the torso's own flanks, and down here the flanks are bare leg already.
            "leg": {"front": hem(3), "back": hem(3)},
        }
    return {"chest": {
        "front": panel(1, 7),
        "back": panel(1, 7),
        # Two straps over the shoulders joining the panels, with the neck open between them. Without
        # these the two panels hang off nothing, which is what a tabard famously does not do.
        #
        # Out to the outermost columns on purpose. The top face is eight texels stretched over a box
        # inflated to ten units wide, and the head covers all but the outer one on each side - a
        # strap that stopped short of column 0 would be a strap nobody ever sees.
        "top": {(col, row): FIELD + 20 for row in range(4) for col in (0, 1, 2, 5, 6, 7)},
    }}


CLOTHS = {"tunic": tunic, "tabard": tabard}


def render(cut, sheet: str) -> Image.Image:
    """One 64x32 mask: the cut placed on the net, and nothing anywhere else."""
    img = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    px = img.load()
    for region, faces in cut(sheet).items():
        for face, texels in faces.items():
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
