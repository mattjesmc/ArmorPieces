"""
Paint the grayscale master for the "puttees" part, and the mask for its `inlay` fitting.

Like the greaves, tassets, sash and spurs painters this does not merely claim that CUBES matches the
shipped geometry, it reads assets/armorpieces/armorpieces/decoration/puttees.json at run time and
asserts it (check_geometry) - here down to the origins, the pivots and the three bone rotations,
because on this part the rotations ARE the design and a master painted for an untilted stack would
stay perfectly self-consistent while describing a different object. Output goes to
tools/decoration_masters/puttees.png and puttees_inlay.png, which sync_decoration_masters.py
installs for the game to colour per trim material and per dye.

Master convention: luminance carries shading, alpha carries silhouette.

This master is 100% opaque, for the greave's reason. Cloth wound round a shin has no fringe to fray
and no gullet to punch, and because parts draw with armorCutoutNoCull a hole cut in a winding would
show the inside of that winding rather than the boot behind it. Everything here is value.

What this part is, and what that costs the painter:

  * Three windings and a tie knot. Each winding is one 5 x 2 x 2 box on its own bone, and each bone
    carries a small NEGATIVE z rotation - -4, -6, -5 degrees - which raises its outboard end. That is
    the whole of the diagonal: a helix wound up a leg shows, from the front, as a stack of bands all
    leaning the same way, and the mod's cubes cannot rotate, so a leaning band has to be a leaning
    BONE. The three angles differ by a degree or two on purpose. Three parallel bands read as machine
    tape; three nearly-parallel ones read as cloth wound by hand, and the gap between two windings
    then widens across the leg instead of staying a constant stripe.

  * `greaves` is a MIRRORED pair - Attachment.of(LEFT_LEG, 0, 8, -2) plus Attachment.mirrored on the
    right - so the layer's scale(-1, 1, 1) runs on the right-hand copy and ONE master serves both.
    `west` is geo +x, outboard on both legs; `east` is geo -x, inboard on both. The outboard-lit /
    inboard-shadowed split therefore survives the flip, and it has to be painted rather than left to
    the engine, because vanilla's diffuse term gives +x and -x faces the same shade, as it does +z
    and -z. The pair MEETS at the midline exactly as the shipped greaves' ankle band does: a winding
    reaches geo x = -2.49, which is world x = -0.59 on the left leg, so the two copies overlap over
    1.18 units of world x and their `north` faces are one plane there. No master can separate two
    coincident faces, so the windings' inboard column is painted as the seam it has become - held at
    the foot of the lateral profile, far under the rest of the band - and the eye is given the lit
    outboard columns to read
    instead. The alternative was tested on paper and rejected: shifting both windings outboard until
    they clear the midline leaves 1.2 units of bare boot on the inboard edge of each leg the moment
    the legs separate in a walk cycle, which is a defect that shows every step rather than one that
    shows only when the legs are together.

  * The hero face is `north`, the front of the shin, and RELIEF BUYS NOTHING HEAD ON: a raised face
    parallel to the face behind it is lit identically to it, because vanilla's diffuse term shades by
    normal alone (up 1.0, down 0.5, +-z 0.8, +-x 0.6). The greaves painter records it on this same
    socket, against a rib and the plate behind it. So the overlap - the thing
    that makes a puttee a puttee - is a VALUE pattern, not a depth pattern. Each winding's `north`
    face is two texel rows: row 0 is the top of the turn, which the turn above laps, and row 1 is its
    free lower edge. Row 1 is the brightest cloth on the part and row 0 the darkest, so at the peak of
    the lateral profile the values run 96, 226 | 68, 208 | 56, 190 - and read down the shin that is
    dark, light, dark, light, dark, light at three different spacings. The depth stagger below is
    still worth having, but it is for the three-quarter view and the profile, not for the render a
    player sees first.

  * The windings do lap in depth as well, and in the direction a puttee is actually wound: from the
    ankle upward, each turn laid over the top edge of the one below it. So the UPPER winding is the
    more proud one - geo z -3.75, -3.60, -3.45 going down - and each one's underside overhangs the
    turn beneath. That overhang is 0.15 of a unit, which is the front tenth of one texel of `down`;
    it is painted as the shadow line it is, and it is the reason the value pattern above is arranged
    dark-under-light rather than the other way round.

  * The pitch is deliberately uneven, and it is what decides whether the lap is legible at all. The
    bone pivots are geo y 8.73, 10.17, 11.49, so a winding's exposed height is 2.00 for the top one
    (nothing laps it), 1.44 for the middle and 1.32 for the bottom - which means row 1 of each is
    whole and row 0 survives as 1.00, 0.44 and 0.32 of a texel. That sliver IS the shadow of the lap,
    so the pitch is not a free choice: at the 1.34 and 1.15 this part was first cut with, the two
    slivers came out at 0.34 and 0.15 and the front view read as three bright bars ruled apart by
    hairlines. Widening the pitch by a tenth each cost the top of the part 0.19 of clearance under
    the knee and bought the overlap back. A wrap also tightens as it comes down to the ankle, so the
    uneven pitch is the honest shape as well as the legible one; three identical exposures would have
    read as a barcode however they were shaded.

  * The whole stack fits between two hard limits and is squeezed by both. Above: the shipped poleyns
    hang to geo y 7.10 on this same leg bone, and `knees` is the tightest socket in the mod, so
    wrap1's highest corner stops at 7.55 - 0.45 clear, where the shipped greaves leaves 0.35. Below:
    the boots shell's sole is at 12.9 and wrap3's lowest corner stops at 12.70. Five units of shin,
    at one texel to the unit, is what there was to spend, and it is why this part has three windings
    and not five: a fourth turn would have had to come out of the pitch, and the pitch is the part.

  * It rides the LEG bone, and so does the boots shell over it, so burial down here is permanent -
    part and shell share the bone and no INNER pixel ever uncovers. The 1.0 boots shell, with
    mc_humanoid's LEG_TRIM of -0.1, is geo x -2.9..2.9, y -0.9..12.9, z -2.9..2.9. Unlike the shipped
    greaves, NO cube of this part hides inside it: the three windings stand 0.85, 0.70 and 0.55 proud
    of its front wall and the tie knot 1.25, which is still well under the poleyn's 1.75. What is
    buried is the back of each winding - 1.15, 1.30 and 1.45 units of it, past the shell wall and on
    into the naked leg box at z = -2 - and that is what a winding is anchored by.

  * The tie knot is the one place on this part where relief buys something. It is unrotated, 2 x 2 x 1
    at geo x 1.15..3.15, y 8.35..10.35, z -4.15..-3.15, so it stands 0.40 in front of the top winding
    and 0.25 past the boots shell's outboard wall - the only thing here that breaks the silhouette,
    and the only marker of which side is outboard when the part is seen head on. Because it is proud
    on three sides at once, its `up`, `north` and `west` faces are all reachable, which is why it and
    not a winding carries the part's brightest ledge - and why its `north` is the one lit face here
    painted DOWN the scale rather than up. A knot of tape is not brighter than the cloth it is tied
    over; it is a darker shape on top of it, lit only along its top edge and its outboard flank. It
    sinks 0.60 into the top winding, so its `south` face and the back of its flanks are INNER.

  * There are no studs, rivets or eyelets on this part. A bolt only reads against a plainly darker
    neighbour on both sides - the brooch's lesson, learned at three by three - and the widest face
    left in the light here is a winding's five texels on a single row. The value that would have gone
    into hardware goes into the lateral profile instead, which is the one thing that says "wrapped
    round a cylinder" rather than "nailed to a plank": across the five columns the master multiplies
    each row by 0.40, 0.74, 0.92, 1.00, 0.88, so the highlight sits one column in from the outboard
    edge and rolls off again at the edge itself. It is a multiplier and not an offset on purpose - an
    offset sized for the 226 of a lit row flattens the 56 of a shadowed one into the buried faces,
    and a cylinder's shading is proportional anyway.

The fitting. `armorpieces:inlay` is a dye, and it takes the three windings whole - every face of
them, so no cube boundary can show a colour seam - while the tie knot keeps the trim material. That
split is the part's whole variety argument: dyed leg wraps in sixteen colours over hardware that
still turns gold, and the material choice still means something because something is still made of
it. No static layer ships. Nothing on a puttee has a colour it must keep against the player's
choice; a leather-brown layer under the knot would only fight the dye it sits next to, and the
shipped greaves' own static sheet is an empty file that proves the point.

The face rectangles come from paint_circlet_master.faces(), copied verbatim: row one (v .. v+d)
holds up then down, each w wide, starting at u+d; row two (v+d .. v+d+h) holds east, north, west,
south with widths d, w, d, w.

Orientation inside each rectangle is the table the greaves painter records as measured, not
recalled:

    face            geo direction        column 0 is        row 0 is
    up              -y  (the top)        min x              max z
    down            +y  (underside)      min x              max z
    west            +x  (outboard)       min z  (front)     min y (top)
    east            -x  (inboard)        max z  (back)      min y (top)
    north           -z  (front)          min x  (inboard)   min y (top)
    south           +z  (back)           max x  (outboard)  min y (top)

The two `up`/`down` rows on every winding run BACK to front, which is what decides burial: the boots
shell's front wall is geo z = -2.9, and on all three windings it falls inside row 1. Row 0 is always
inside the boot; row 1 is the row the wall crosses - 0.85 of it proud on the top winding, 0.70 on the
middle, 0.55 on the bottom. The tie knot is only one unit deep, so it has a single row, and all of it
is in front of that wall.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image

from fitting_mask import write_mask

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration" / "puttees.json"
OUT = ROOT / "tools" / "decoration_masters" / "puttees.png"
INLAY = OUT.with_name("puttees_inlay.png")

TEX_W, TEX_H = 64, 32

# size (w, h, d) and uv (u, v), mirroring puttees.json in that file's own walk order - the root bone
# `puttee` carries no cubes, so the order is its four children. Geo extents at rest (left-hand copy;
# the right one is the mirror image in the body midline x = 0), with the bone rotation applied:
#   wrap1 - the top turn, bone pivot y 8.73 rotated -4 deg about z; geo x -2.46..2.66, y 7.55..9.89,
#           z -3.75..-1.75. Nothing laps it, so all 2.00 of its height is exposed. Its top corner,
#           the outboard one, is the highest point of the whole part and the number the knee lives
#           on: 0.45 under the shipped poleyns' lowest cube at y 7.10.
#   wrap2 - the middle turn, pivot y 10.17, -6 deg; geo x -2.49..2.69, y 8.90..11.42, z -3.60..-1.60.
#           wrap1 laps 0.56 of it, leaving 1.44 exposed - row 1 whole and 0.44 of row 0.
#   wrap3 - the bottom turn, pivot y 11.49, -5 deg; geo x -2.48..2.68, y 10.27..12.70, z -3.45..-1.45.
#           wrap2 laps 0.68 of it, leaving 1.32 exposed - row 1 whole and 0.32 of row 0. Its lower
#           edge stops 0.20 above the boots shell's sole at y 12.9: the last turn into the boot.
#   tie   - the knot, unrotated on the root bone's frame; geo x 1.15..3.15, y 8.35..10.35,
#           z -4.15..-3.15. Proud of everything: 0.40 in front of wrap1 and 0.25 outboard of the
#           boots shell.
# Shared planes with area in common, from a pairwise face scan over the part, the mirrored twin, the
# naked body and all four armor shells: each winding shares its `north` plane and its `east` face
# with the twin's matching winding across the midline, and nothing else on the figure shares a plane
# with anything here - trace_geometry reports no COPLANAR and no OVERLAP on this part, and every
# bone-mate on the leg (poleyns, tassets, spurs, heel_wings) clears it. The midline pair is the seam
# the docstring answers above.
CUBES = {
    "wrap1": ((5, 2, 2), (0, 0)),
    "wrap2": ((5, 2, 2), (14, 0)),
    "wrap3": ((5, 2, 2), (28, 0)),
    "tie":   ((2, 2, 1), (42, 0)),
}

# origin, and the pivot + z rotation of the bone the cube hangs from. On this part the rotations are
# the design, so they are asserted alongside the cube list rather than trusted.
PLACEMENT = {
    "wrap1": ((-2.4, -1, -1.75), (0, 0.73, 0), -4),
    "wrap2": ((-2.4, -1, -1.6), (0, 2.17, 0), -6),
    "wrap3": ((-2.4, -1, -1.45), (0, 3.49, 0), -5),
    "tie":   ((1.15, 0.35, -2.15), (0, 0, 0), 0),
}

random.seed(53)  # deterministic output - regenerating must not churn the PNG

# Calibrated against the ramp, not guessed. The material ramp interpolates dark -> mid over master
# values 0..127 and mid -> light over 128..255, so a master confined to one half only ever uses half
# of a material's ramp. Of this master's 160 texels about seventy are ever reachable by a camera -
# thirty of `north` on the windings, the knot's twelve, and the slivers of ledge, hem and flank that
# clear the boot - and those run from a lapped winding at 56, and its seam column at the SEAM floor
# of 44, up to a lit knot ledge at 236. That is the whole ramp, and it has to be: the overlap read is
# made of nothing but the distance between LAP and EDGE.
LEDGE = 236     # a top ledge that clears the boot's front wall - the brightest thing here
EDGE = 226      # a winding's free lower edge, at the peak of the lateral profile
FLANK = 178     # the front sliver of an outboard face
TIE = 150       # `north` on the tie knot - deliberately UNDER the cloth it is tied over
CLOTH = 96      # the top winding's upper row, where the wrap runs out under the knee
IN = 92         # the knot's inboard face, looking across at the other leg
LAP = 68        # a winding's upper row, in the shadow of the turn that laps it
SEAM = 44       # the floor for column 0, where the pair's two windings lie in one plane
DOWN = 44       # an underside
INNER = 34      # buried - in the boot, in the leg, behind a winding, or in the mirrored twin

FALL = 18       # per-winding falloff going down the shin, away from the light
JITTER = 3
WEAVE = 5       # the extra jitter a winding's `north` row gets - cloth, not sheet metal

# The lateral profile across a winding's five `north` columns, inboard to outboard. It is a
# MULTIPLIER rather than an offset, so that the dark rows keep their own shape instead of being
# flattened into INNER by a subtraction sized for the light ones - the shading of a cylinder is
# proportional, not additive. The peak sits at column 3 rather than column 4 so that the cloth is
# seen to turn round the side of the leg instead of ending flat, and column 0 is the midline seam,
# floored at SEAM so a dark row's seam does not sink below the buried faces.
PROFILE = (0.40, 0.74, 0.92, 1.00, 0.88)


def faces(size, uv):
    """Per-face pixel rectangles (x, y, w, h) for one box-UV cube. See the module docstring."""
    w, h, d = size
    u, v = uv
    return {
        "up":    (u + d, v, w, d),
        "down":  (u + d + w, v, w, d),
        "east":  (u, v + d, d, h),
        "north": (u + d, v + d, w, h),
        "west":  (u + d + w, v + d, d, h),
        "south": (u + d + w + d, v + d, w, h),
    }


def put(img, x: int, y: int, lum: int, alpha: int = 255) -> None:
    if 0 <= x < TEX_W and 0 <= y < TEX_H:
        img.putpixel((x, y), (max(0, min(255, lum)), alpha))


def fill(img, rect, lum: int, jitter: int = JITTER) -> None:
    x0, y0, w, h = rect
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            put(img, x, y, lum + random.randint(-jitter, jitter))


def ramp(i: int, n: int) -> float:
    """Position along a face axis, 0.0 at column/row 0 and 1.0 at the far end."""
    return 0.0 if n <= 1 else i / (n - 1)


def paint_winding(img, key: str, top: int, bottom: int, flank: int) -> None:
    """One turn of cloth: 5 wide, 2 tall, 2 deep, on a bone tilted a few degrees about z.

    `top` is the value of `north` row 0 - the upper half of the turn, which the turn above laps - and
    `bottom` the value of row 1, its free lower edge. Those two numbers are the part. Everything a
    player reads as "wound cloth" rather than "three bars on a boot" is the distance between them
    repeated at three different spacings, because the geometry cannot help: the three windings' front
    faces are parallel to each other and to the boot behind them, and vanilla lights parallel faces
    identically however far apart they are.

    Column 0 is the bottom of the lateral profile, at 0.40 of the row, and floored at SEAM so a
    shadowed row cannot sink under the buried faces. It is the seam - the unit of world x where this
    winding and the mirrored twin's occupy the same plane at the midline - and it is kept dark so
    that the pair reads as two wraps meeting between the legs rather than as one apron with a flaw
    down the middle. It doubles as the honest shading of an inboard face, which is looking across at
    the other leg and would be the darkest column here anyway.

    Of the two depth units only the leading 0.85, 0.70 or 0.55 clears the boots shell's front wall,
    so `up`, `down` and `west` each spend their back row or column on INNER. `up` is worth painting
    only on wrap1: on the other two it is under the turn above, which is both higher and more proud,
    and hidden for good. `down` is worth painting on all three, but for different reasons - on wrap1
    and wrap2 it is the 0.15-unit overhang over the turn below, which is the one real shadow line the
    lap has, and on wrap3 it is the hem of the whole part where it meets the boot.

    `east` is INNER throughout. At geo x -2.49 that face is inside the twin's own winding, which is
    the one place on this part where the occluder is the other copy of itself rather than a shell."""
    size, uv = CUBES[key]
    f = faces(size, uv)

    x0, y0, fw, fh = f["north"]          # 5 wide x 2 tall, col 0 = midline seam, col 4 = outboard
    for j in range(fh):
        base = top if j == 0 else bottom
        for i in range(fw):
            lum = round(base * PROFILE[i])
            put(img, x0 + i, y0 + j, max(SEAM, lum) + random.randint(-WEAVE, WEAVE))

    x0, y0, fw, fh = f["up"]             # 5 wide x 2 deep, rows run BACK to front
    for j in range(fh):
        for i in range(fw):
            lit = j == 1 and key == "wrap1"
            lum = round(LEDGE * PROFILE[i]) if lit else INNER
            put(img, x0 + i, y0 + j, lum + random.randint(-JITTER, JITTER))

    x0, y0, fw, fh = f["down"]           # 5 wide x 2 deep, rows run back to front; the shadow lip
    for j in range(fh):
        for i in range(fw):
            lum = INNER if j == 0 else DOWN + (0 if i else -8)
            put(img, x0 + i, y0 + j, lum + random.randint(-JITTER, JITTER))

    x0, y0, fw, fh = f["west"]           # 2 deep x 2 tall, col 0 = front (the part that clears)
    for j in range(fh):
        for i in range(fw):
            lum = (flank - round(FALL * ramp(j, fh))) if i == 0 else INNER
            put(img, x0 + i, y0 + j, lum + random.randint(-JITTER, JITTER))

    fill(img, f["east"], INNER)          # inside the twin's winding across the midline
    fill(img, f["south"], INNER)         # the back cap, inside the leg box at z = -2


def paint_tie(img) -> None:
    """The knot that finishes the wrap: 2 wide, 2 tall, 1 deep, unrotated, on the outboard shin.

    It is the only cube here that stands proud on three sides at once - 0.40 in front of the top
    winding, 0.25 outboard of the boots shell, and with a full unit of depth that never enters the
    shell at all - so it is the only place on the part where a shape is described by light rather
    than by paint. That earns it the brightest ledge in the file on `up` - which is the face a player
    looking down at their own shins actually sees, and the one vanilla's diffuse term lights at 1.0 -
    against the darkest underside on `down`, with `west` between them and `north` well under both.

    It is also the only asymmetry. Three leaning bands are the same object seen from either side;
    a knot on the outboard shin says which leg is which, and it is what stops the front view from
    reading as a ladder. It keeps the trim material while the windings take the dye, so on a
    dyed part it is also the only thing left of the material the player chose.

    Its `south` face and the back of both flanks are inside wrap1 and wrap2 - it sinks 0.60 into the
    cloth, which is what a tape tied over a wrap does - so those are INNER."""
    size, uv = CUBES["tie"]
    f = faces(size, uv)

    x0, y0, fw, fh = f["north"]          # 2 wide x 2 tall, col 0 = inboard, row 0 = the knot
    for j in range(fh):
        for i in range(fw):
            lum = round((TIE + (18 if j == 0 else -42)) * (1.0 if i else 0.82))
            put(img, x0 + i, y0 + j, lum + random.randint(-JITTER, JITTER))

    fill(img, f["up"], LEDGE)            # 2 wide x 1 deep, all of it in front of the shell wall
    fill(img, f["down"], DOWN + 6)       # the knot's lower lip, over the middle winding
    fill(img, f["west"], FLANK + 14)     # 1 deep x 2 tall, outboard and fully clear
    fill(img, f["east"], IN)             # inboard, and only its front 0.40 is not inside the cloth
    fill(img, f["south"], INNER)         # sunk into wrap1


def check_geometry() -> None:
    """CUBES and PLACEMENT must be the cube list, the origins and the bone frames of the shipped
    geometry, in order. Painting a texture for a shape the model no longer has is invisible to every
    other check in this pipeline: both halves stay internally consistent while the rectangles slide
    off the faces they were drawn for. The rotations are asserted with the rest because on this part
    a lost tilt would turn a wrapped leg back into a stack of bars without moving one texel."""
    doc = json.loads(GEO.read_text(encoding="utf-8"))
    found = []

    def walk(bone):
        pivot = tuple(bone.get("pivot", [0, 0, 0]))
        rot = bone.get("rotation", [0, 0, 0])
        for c in bone.get("cubes", []):
            found.append(((tuple(c["size"]), tuple(c["uv"])), (tuple(c["origin"]), pivot, rot[2])))
        for child in bone.get("children", []):
            walk(child)

    for bone in doc["bones"]:
        walk(bone)

    assert (doc["texture_width"], doc["texture_height"]) == (TEX_W, TEX_H), \
        f"{GEO.name} is {doc['texture_width']}x{doc['texture_height']}, this master is {TEX_W}x{TEX_H}"
    assert [c for c, _ in found] == list(CUBES.values()), \
        f"CUBES disagrees with {GEO.name}: {[c for c, _ in found]} vs {list(CUBES.values())}"
    assert [p for _, p in found] == list(PLACEMENT.values()), \
        f"PLACEMENT disagrees with {GEO.name}: {[p for _, p in found]} vs {list(PLACEMENT.values())}"


def check_layout() -> dict:
    """Every face rectangle must sit inside the texture and no two may overlap - a silent overlap
    would paint one cube's shading onto another's face and only show up on a model in game."""
    claimed = {}
    for name, (size, uv) in CUBES.items():
        for face, (x, y, w, h) in faces(size, uv).items():
            assert 0 <= x and x + w <= TEX_W, f"{name}.{face} runs off the texture in u"
            assert 0 <= y and y + h <= TEX_H, f"{name}.{face} runs off the texture in v"
            for py in range(y, y + h):
                for px in range(x, x + w):
                    prev = claimed.get((px, py))
                    assert prev is None, f"{name}.{face} overlaps {prev} at {(px, py)}"
                    claimed[(px, py)] = f"{name}.{face}"
    return claimed


def main() -> None:
    check_geometry()
    claimed = check_layout()
    img = Image.new("LA", (TEX_W, TEX_H), (0, 0))
    # Top turn first, then down the shin: each one a little darker than the one above it, because
    # the light is above and the ankle sits in the boot's own shadow.
    paint_winding(img, "wrap1", CLOTH, EDGE, FLANK)
    paint_winding(img, "wrap2", LAP, EDGE - FALL, FLANK - 14)
    paint_winding(img, "wrap3", LAP - 12, EDGE - 2 * FALL, FLANK - 26)
    paint_tie(img)

    opaque = {(x, y) for y in range(TEX_H) for x in range(TEX_W) if img.getpixel((x, y))[1]}
    assert opaque == set(claimed), "the opaque set is not exactly the UV rectangles"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    lums = [img.getpixel(p)[0] for p in sorted(opaque)]
    print(f"wrote {OUT} ({len(opaque)} opaque px, values {min(lums)}-{max(lums)})")

    # The dye takes the three windings whole - every face, so no cube boundary can show a colour
    # seam - and leaves the tie knot on the trim material.
    cloth = [r for key in ("wrap1", "wrap2", "wrap3") for r in faces(*CUBES[key]).values()]
    write_mask(img, cloth, INLAY)


if __name__ == "__main__":
    main()
