"""
Trace a decoration geometry into its anchor's bone-local frame and report what it clears.

Every part in this mod is judged by arithmetic against the vanilla body before it is judged by eye,
because until the four in-game passes are run there is nothing else to judge it by - and because the
Blockbench rig shows you a shape but will not tell you that a face landed exactly on the boots
shell's back wall. This does the second half: it composes the bone chain the way the renderer does,
then measures the result against the body box and every armor shell that covers the same bone.

It is what caught the thing the `horns` rework existed to fix. The old part's envelope spanned 7.8
units of depth against 4.5 units of lateral travel, and a number like that is the difference between
"this reads as a wing" as an opinion and as a measurement.

    python tools/trace_geometry.py <geometry.json> [anchor]
    python tools/trace_geometry.py --all

The anchor is inferred from the part's `armor_decoration` entry when it is not given. Anchor offsets
and the vanilla body numbers both come from bb_rig - the enum is parsed, never copied, so a tuned
offset moves this report with it.

Reading the output:

  * **envelope / reach** are in the parent bone's local frame, the same space the geometry JSON is
    authored in. +Y is DOWN.
  * **clearance** is how far the part protrudes past each surface. Negative means it stays inside.
  * **COPLANAR** is the one line that is a defect rather than a datum, and it is reported only for
    the outermost shell covering the bone - the surface a player can actually see a part fight with.
    The fix is always to move the face, never to accept it. A face lying on the naked body box or on
    an inner layer is printed as a *note* instead: it is buried under that outer shell, which is the
    burial trick working rather than a defect, and the circlet and the horns both do it on purpose.
    The check is per-face and per-plane, which is the form the rule has to take - a cube can straddle
    one wall safely and still put its *other* face on a different one.
  * Only unrotated cubes in unrotated chains are checked for coplanarity against a shell, because
    only those have axis-aligned faces that could lie in a shell wall in the first place.
  * **shares <bone> with** is the cross-part pass. A part is measured against every OTHER part that
    draws on the same bone and can be worn at the same time - which means a different socket, since
    one socket holds one part, and includes sockets on a different armor piece: the greaves and the
    tassets ride the same leg bone from the boots and the leggings. Boxes there are axis-aligned
    hulls of possibly-rotated cubes, so an `OVERLAP` is an upper bound and a reason to look rather
    than proof of a clash; a `COPLANAR` between two parts is the real finding, because neither of
    them is hiding the other.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from bb_rig import ARMOR_LAYERS, BODY, GEO_DIR, ROOT, parse_anchors

DEC_DIR = ROOT / "src" / "main" / "resources" / "data" / "armorpieces" / "armorpieces" / "armor_decoration"

EPS = 1e-6
AXES = ("x", "y", "z")


def rotate(vec, deg):
    """Apply one bone's rotation to a vector.

    Order matters and it is not the order the name suggests. ModelPart.rotate calls JOML's
    rotateZYX(z, y, x), which post-multiplies - the composed matrix is Rz * Ry * Rx, so the vector
    meets **X first** and Z last. Applying them in the written order instead is a silent error: it
    agrees with the correct answer whenever only one axis is non-zero, which is most parts, and
    disagrees by a fraction of a unit exactly on the chained multi-axis bones where it matters."""
    rx, ry, rz = (math.radians(d) for d in deg)
    x, y, z = vec
    y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
    x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
    x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
    return (x, y, z)


def compose(outer, inner):
    """The rotation of a child bone in its grandparent's frame. Bones compose by rotating the child's
    basis by the parent's, which is what applying the parent to each of the child's images does."""
    return tuple(outer(inner(e)) for e in ((1, 0, 0), (0, 1, 0), (0, 0, 1)))


def walk(bone, origin, basis, out, depth=0, log=None):
    """Emit every cube's eight corners, plus the plane each of its six faces lies in."""
    def apply(v):
        return tuple(sum(basis[i][a] * v[i] for i in range(3)) for a in range(3))

    pivot = bone.get("pivot", [0, 0, 0])
    here = tuple(origin[a] + apply(pivot)[a] for a in range(3))
    rot = bone.get("rotation", [0, 0, 0])
    child_basis = compose(apply, lambda v: rotate(v, rot))
    axis_aligned = all(abs(r) < EPS for r in rot) and all(
        sum(1 for c in row if abs(c) > EPS) == 1 for row in basis)

    for cube in bone.get("cubes", []):
        o, s = cube["origin"], cube["size"]
        infl = cube.get("inflate", 0.0)
        lo = [o[a] - infl for a in range(3)]
        hi = [o[a] + s[a] + infl for a in range(3)]
        corners = []
        for i in (0, 1):
            for j in (0, 1):
                for k in (0, 1):
                    v = ((hi if i else lo)[0], (hi if j else lo)[1], (hi if k else lo)[2])
                    w = tuple(sum(child_basis[t][a] * v[t] for t in range(3)) for a in range(3))
                    corners.append(tuple(here[a] + w[a] for a in range(3)))
        # Only an unrotated cube in an unrotated chain has axis-aligned faces, and only those can be
        # coplanar with an axis-aligned shell wall in the first place.
        planes = []
        if axis_aligned:
            for a in range(3):
                planes += [(a, min(c[a] for c in corners)), (a, max(c[a] for c in corners))]
        out.append((bone.get("name", "?"), corners, planes))

    if log is not None:
        log.append("  " * depth + f"{bone.get('name', '?'):12s} at "
                   f"({here[0]:6.2f}, {here[1]:6.2f}, {here[2]:6.2f})")
    for child in bone.get("children", []):
        walk(child, here, child_basis, out, depth + 1, log)


def shells_for(bone_name):
    """The body box and every armor shell that covers this bone, as (label, lo, hi) in bone space."""
    _, origin, size = BODY[bone_name]
    out = [("body", list(origin), [origin[a] + size[a] for a in range(3)])]
    for layer, (bones, inflate) in ARMOR_LAYERS.items():
        if bone_name in bones:
            out.append((layer.replace("armor_", ""),
                        [origin[a] - inflate for a in range(3)],
                        [origin[a] + size[a] + inflate for a in range(3)]))
    return out


IDENT = ((1, 0, 0), (0, 1, 0), (0, 0, 1))


def placed_cubes(geo, attachment):
    """Every cube of a geometry, as (bone name, lo, hi) boxes in its parent bone's local frame.

    The renderer translates by the attachment offset and only then applies scale(-1, 1, 1), so a
    mirrored attachment negates the GEOMETRY and not the offset - which is why the offset is added
    after the flip here and not before. Getting that backwards puts a mirrored part on the wrong side
    of its own anchor, and on the two anchors whose halves sit at x = 0 it looks correct anyway.
    """
    raw = []
    for b in geo["bones"]:
        walk(b, (0.0, 0.0, 0.0), IDENT, raw)
    out = []
    for name, corners, _ in raw:
        pts = [((-c[0] if attachment["mirror"] else c[0]), c[1], c[2]) for c in corners]
        pts = [tuple(attachment["offset"][a] + q[a] for a in range(3)) for q in pts]
        out.append((name,
                    [min(q[a] for q in pts) for a in range(3)],
                    [max(q[a] for q in pts) for a in range(3)]))
    return out


def neighbours(subject_stem, subject_anchor, bone, anchors):
    """Every OTHER part that can be worn at the same time and draws on the same bone.

    Same-socket parts are excluded because one socket holds one part: a crest and a second crest can
    never be on a body together, so measuring them against each other would only produce noise. Parts
    on different sockets can always coexist, including across armor pieces - the greaves and the
    tassets ride the same leg bone from different pieces, which is the case that has already caught a
    session out once.
    """
    out = []
    for dec in sorted(DEC_DIR.glob("*.json")):
        if dec.stem == subject_stem:
            continue
        entry = json.loads(dec.read_text(encoding="utf-8"))
        for name in entry["anchors"]:
            if name == subject_anchor or name not in anchors:
                continue
            if not any(att["part"] == bone for att in anchors[name]["attachments"]):
                continue
            geo_path = GEO_DIR / f"{dec.stem}.json"
            if not geo_path.is_file():
                continue
            geo = json.loads(geo_path.read_text(encoding="utf-8"))
            for att in anchors[name]["attachments"]:
                if att["part"] != bone:
                    continue
                for cube, lo, hi in placed_cubes(geo, att):
                    out.append((f"{dec.stem}:{name}", cube, lo, hi))
    return out


def compare_neighbours(subject_boxes, others, shell=None):
    """Interpenetrations and shared planes between this part and its bone-mates.

    Boxes are axis-aligned hulls of possibly-rotated cubes, so an overlap here is an upper bound: it
    is a reason to look, not proof of a clash. A shared plane is the stronger finding - two
    decorations whose faces lie in the same plane z-fight exactly as a decoration and a shell do, and
    neither one is hiding the other.
    """
    lines = []
    for sname, slo, shi in subject_boxes:
        for label, oname, olo, ohi in others:
            gap = [max(slo[a] - ohi[a], olo[a] - shi[a]) for a in range(3)]
            worst = max(gap)
            if worst < -EPS:
                over = [min(shi[a], ohi[a]) - max(slo[a], olo[a]) for a in range(3)]
                lines.append((worst, f"  OVERLAP: {sname} into {label}'s {oname} by "
                                     + " x ".join(f"{o:.2f}" for o in over)
                                     + " (hull test - check whether the real cubes meet)"))
            # Shared planes are checked whenever the boxes overlap OR merely touch. Running this only
            # inside the overlap branch missed the worst case there is: two parts flush against each
            # other have a gap of exactly 0, so they scored as a clean near-miss while sharing a face
            # with real area - which is a z-fight between two decorations, neither hiding the other.
            if worst < EPS:
                for a in range(3):
                    for sv in (slo[a], shi[a]):
                        for ov in (olo[a], ohi[a]):
                            if abs(sv - ov) >= EPS:
                                continue
                            # A shared plane strictly inside the piece's own shell is behind an
                            # opaque wall, and two surfaces nobody can see do not fight. This is what
                            # makes the circlet's temple bar and the horn boss meeting at x = 4 a
                            # curiosity rather than the defect the same numbers would be outside.
                            buried_here = shell is not None and shell[0][a] < sv < shell[1][a]
                            lines.append((worst, f"  {'note:    ' if buried_here else 'COPLANAR:'} "
                                                 f"{sname} and {label}'s {oname} share the plane "
                                                 f"{AXES[a]} = {sv:g}"
                                                 + (" (inside the shell, so occluded)" if buried_here
                                                    else "")))
            if EPS <= worst < 0.5:
                lines.append((worst, f"  near:    {sname} clears {label}'s {oname} by "
                                     f"{worst:.2f} in {AXES[gap.index(worst)]}"))
    return [t for _, t in sorted(set(lines))]


def report(geo_path, anchor_name, anchors):
    geo = json.loads(Path(geo_path).read_text(encoding="utf-8"))
    spec = anchors[anchor_name]
    primary = spec["attachments"][0]
    bone = primary["part"]
    offset = primary["offset"]

    log, cubes = [], []
    for b in geo["bones"]:
        walk(b, offset, ((1, 0, 0), (0, 1, 0), (0, 0, 1)), cubes, 0, log)

    print(f"{Path(geo_path).stem}  ->  anchor {anchor_name} on {bone} at {offset}")
    print("\n".join(log))

    pts = [c for _, corners, _ in cubes for c in corners]
    lo = [min(p[a] for p in pts) for a in range(3)]
    hi = [max(p[a] for p in pts) for a in range(3)]
    print("  envelope  " + "  ".join(f"{AXES[a]} {lo[a]:6.2f} ..{hi[a]:6.2f}" for a in range(3)))
    reach = max(math.dist(p, offset) for p in pts)
    print(f"  reach from the anchor: {reach:.2f}")

    for label, slo, shi in shells_for(bone):
        out = [max(slo[a] - lo[a], hi[a] - shi[a]) for a in range(3)]
        print(f"  past {label:11s} " + "  ".join(f"{AXES[a]} {out[a]:+6.2f}" for a in range(3)))

    if len(spec["attachments"]) == 2 and spec["attachments"][1]["mirror"]:
        # The pair is antisymmetric about the FIGURE's centreline, not about the bone's own origin,
        # and for a limb those are not the same place: the arm bones sit at world x = +-5 and the leg
        # bones at +-1.9. Doubling the bone-local extent reports a spaulder as spanning 11 when it
        # spans 21. Adding the bone pivot first is the whole fix, and it is invisible on the head and
        # torso parts whose bones sit at x = 0 - which is why it survived being written.
        pivot_x = BODY[bone][0][0]
        span = 2 * max(abs(pivot_x + lo[0]), abs(pivot_x + hi[0]))
        print(f"  pair spans {span:.2f} across the figure "
              f"({'over' if span > 18 else 'within'} the 18 the shoulders span)")

    # The shell that matters is the part's OWN piece's, because that is the only one guaranteed to be
    # there: a decoration renders exactly when its armor piece is worn, and any other layer may be
    # absent. A face on that shell is the case to answer for. A face on the naked body box or on some
    # other layer is printed as a note - usually it is the burial trick working, which is why the
    # circlet and the horns both put faces on the head box on purpose.
    own = spec["armor_type"].lower()
    shells = shells_for(bone)
    flagged, buried = set(), set()
    for label, slo, shi in shells:
        for a in range(3):
            for wall in (slo[a], shi[a]):
                for name, _, planes in cubes:
                    for pa, pv in planes:
                        if pa == a and abs(pv - wall) < EPS:
                            if label == own:
                                flagged.add(f"  COPLANAR: {name}'s {AXES[a]} face at {pv:g} lies on "
                                            f"the {label} shell, which is always worn when this part "
                                            f"draws - move the face, or say why it cannot fight")
                            else:
                                buried.add(f"  note: {name}'s {AXES[a]} face at {pv:g} lies on the "
                                           f"{label} surface")
    for h in sorted(buried) + sorted(flagged):
        print(h)

    subject_boxes = [(n, [min(c[a] for c in corners) for a in range(3)],
                         [max(c[a] for c in corners) for a in range(3)])
                     for n, corners, _ in cubes]
    others = neighbours(Path(geo_path).stem, anchor_name, bone, anchors)
    own_shell = next(((slo, shi) for lbl, slo, shi in shells if lbl == own), None)
    clash = compare_neighbours(subject_boxes, others, own_shell)
    if others:
        mates = sorted({label for label, _, _, _ in others})
        print(f"  shares {bone} with: {', '.join(mates)}")
        for line in clash:
            print(line)
        if not clash:
            print("    all clear by more than half a unit")
    return not flagged


def anchor_of(stem):
    """A part's declared anchor, from its registry entry. Parts legal in several sockets have to be
    traced against each one, so the first is only a default."""
    path = DEC_DIR / f"{stem}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))["anchors"][0]


def main():
    args = [a for a in sys.argv[1:] if a != "--all"]
    anchors = parse_anchors()
    targets = sorted(GEO_DIR.glob("*.json")) if "--all" in sys.argv else [Path(args[0])]
    if not targets:
        sys.exit("usage: trace_geometry.py <geometry.json> [anchor] | --all")

    clean = True
    for i, geo in enumerate(targets):
        name = args[1] if len(args) > 1 else anchor_of(geo.stem)
        if name is None:
            sys.exit(f"{geo.stem}: no armor_decoration entry, so pass the anchor explicitly")
        if name not in anchors:
            sys.exit(f"unknown anchor {name!r}; have {', '.join(sorted(anchors))}")
        if i:
            print()
        clean &= report(geo, name, anchors)
    if not clean:
        print("\nOne or more COPLANAR lines above. Each one needs a decision, not necessarily a"
              " change: move the face, or record why that face cannot be seen fighting.")


if __name__ == "__main__":
    main()
