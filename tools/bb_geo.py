"""
Convert between Blockbench .bbmodel projects and this mod's decoration geometry JSON.

Why this exists: our geometry format is a literal mirror of the Java entity-model path
(DecorationGeometry.Bone -> PartDefinition.addOrReplaceChild, Cube -> texOffs().addBox()), and
Blockbench's `modded_entity` format targets that same path. So the two are the same model in two
coordinate conventions, and the conversion is exactly the convention change:

    java = (-x, 24 - y, z)        for an absolute point (a pivot)
    java = (-x, -y, +z)           for a pivot-relative offset (cube origin, child pivot)
    java = (-rx, -ry, +rz)        for a rotation, degrees -> radians

That is a 180-degree rotation about Z plus a 24 lift, which is precisely the
`poseStack.scale(-1, -1, 1)` LivingEntityRenderer applies before drawing a model. Note that X flips
too - treating this as a plain Y-flip mirrors every asymmetric part, silently.

These rules were not assumed. They were measured against Blockbench 5.1.6's own
`Codecs.modded_entity.compile()` output, including the nested case where a parent bone is rotated
(a child's offset is the plain difference of absolute origins; the parent's rotation does not enter).

Usage:
    python tools/bb_geo.py export tools/rigs/crest.bbmodel --out <geometry.json>
    python tools/bb_geo.py import <geometry.json> --out tools/rigs/feathering.bbmodel
    python tools/bb_geo.py roundtrip <geometry.json>
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEO_DIR = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration"
RIG_DIR = ROOT / "tools" / "rigs"

# The lift between Blockbench's feet-at-zero space and entity-model space. Blockbench writes this as
# the per-project `modded_entity_flip_y` flag; every rig this toolchain emits sets it true, and a
# project with it disabled would need a different constant here - hence the guard in export().
BB_Y = 24.0

# Fixed namespace so re-importing the same model produces the same uuids and the file diffs cleanly.
UUID_NS = uuid.UUID("1b7a4f2e-0000-4000-8000-a12c0de54321")

# The group a rig reserves for the part being authored. Everything outside it is locked reference
# geometry - the vanilla body and armor - and never exports.
PART_GROUP = "part"


# ---- the coordinate change -------------------------------------------------------------------

def flip_point(p):
    """Absolute point, geo <-> bb. Self-inverse, which is why one function serves both directions."""
    return [-p[0], BB_Y - p[1], p[2]]


def flip_delta(d):
    """Pivot-relative offset, geo <-> bb. Self-inverse."""
    return [-d[0], -d[1], d[2]]


def flip_rot(r):
    """Rotation in degrees, geo <-> bb. Self-inverse."""
    return [-r[0], -r[1], r[2]]


def num(v):
    """Trim float noise, and keep whole numbers whole so the JSON reads like hand-authored JSON."""
    r = round(float(v), 4)
    return int(r) if abs(r - round(r)) < 1e-9 else r


def sub(a, b):
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


# ---- Blockbench project reading ---------------------------------------------------------------

def read_bbmodel(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    cubes = {e["uuid"]: e for e in data.get("elements", []) if e.get("type", "cube") == "cube"}
    groups = {g["uuid"]: g for g in data.get("groups", [])}
    return data, cubes, groups


def group_props(node, groups):
    """Blockbench 5.x keeps group data in a top-level `groups` array and only the tree in `outliner`.
    Older files inline it. Accept both - a human's saved file may be either."""
    if isinstance(node, dict) and "origin" in node:
        return node
    return groups.get(node.get("uuid"), {})


def find_group(nodes, name, groups):
    for node in nodes:
        if not isinstance(node, dict):
            continue
        if group_props(node, groups).get("name") == name:
            return node
        hit = find_group(node.get("children", []), name, groups)
        if hit is not None:
            return hit
    return None


# ---- export: .bbmodel -> geometry JSON --------------------------------------------------------

def cube_to_geo(cube, pivot_abs_geo):
    """A Blockbench box, as an addBox() relative to its bone's pivot.

    Blockbench stores from/to as absolute corners; the Java path wants the minimum corner relative to
    the pivot. Under the X and Y flips the Blockbench *maximum* corner becomes the geo minimum, which
    is the one asymmetry in this function worth reading twice."""
    frm, to = cube["from"], cube["to"]
    origin = [
        -to[0] - pivot_abs_geo[0],
        (BB_Y - to[1]) - pivot_abs_geo[1],
        frm[2] - pivot_abs_geo[2],
    ]
    size = [to[0] - frm[0], to[1] - frm[1], to[2] - frm[2]]
    out = {
        "origin": [num(v) for v in origin],
        "size": [num(v) for v in size],
        "uv": [int(v) for v in cube.get("uv_offset", [0, 0])],
    }
    if cube.get("inflate"):
        out["inflate"] = num(cube["inflate"])
    if cube.get("mirror_uv"):
        out["mirror"] = True
    return out


def group_to_bone(node, groups, cubes, parent_origin_bb):
    props = group_props(node, groups)
    origin_bb = props.get("origin", [0, 0, 0])
    pivot_abs_geo = flip_point(origin_bb)

    bone = {
        "name": props.get("name", "bone"),
        "pivot": [num(v) for v in flip_delta(sub(origin_bb, parent_origin_bb))],
    }
    rotation = props.get("rotation", [0, 0, 0])
    if any(rotation):
        bone["rotation"] = [num(v) for v in flip_rot(rotation)]
    if props.get("mirror_uv"):
        bone["mirror"] = True

    bone_cubes, children = [], []
    for child in node.get("children", []):
        if isinstance(child, str):
            cube = cubes.get(child)
            if cube is not None and not cube.get("locked"):
                bone_cubes.append(cube_to_geo(cube, pivot_abs_geo))
        elif isinstance(child, dict):
            if group_props(child, groups).get("locked"):
                continue
            children.append(group_to_bone(child, groups, cubes, origin_bb))

    if bone_cubes:
        bone["cubes"] = bone_cubes
    if children:
        bone["children"] = children
    return bone


def count_bones(bones):
    return sum(1 + count_bones(b.get("children", [])) for b in bones)


def count_cubes(bones):
    return sum(len(b.get("cubes", [])) + count_cubes(b.get("children", [])) for b in bones)


def export(bb_path, out_path, group_name=PART_GROUP, quiet=False):
    bb_path, out_path = Path(bb_path), Path(out_path)
    data, cubes, groups = read_bbmodel(bb_path)

    # 'modded_entity' is what a bare part project is; 'free' is what a rig is, because a rig needs
    # several textures at different sizes; 'armorpieces' is the Blockbench plugin's own format,
    # which is 'free' with the workspace trimmed down. All store geometry identically, so all
    # export the same.
    fmt = data.get("meta", {}).get("model_format")
    if fmt not in ("modded_entity", "free", "armorpieces"):
        print(f"warning: {bb_path.name} is format {fmt!r}, expected 'modded_entity', 'free' or "
              f"'armorpieces'", file=sys.stderr)
    if data.get("modded_entity_flip_y") is False:
        sys.exit("error: project has modded_entity_flip_y disabled; the 24-unit lift would be wrong")

    part = find_group(data.get("outliner", []), group_name, groups)
    if part is None:
        sys.exit(f"error: no group named {group_name!r} in {bb_path.name}. Model inside that group - "
                 f"everything outside it is locked reference geometry.")

    part_origin = group_props(part, groups).get("origin", [0, 0, 0])
    bones = []
    for child in part.get("children", []):
        if isinstance(child, dict):
            if not group_props(child, groups).get("locked"):
                bones.append(group_to_bone(child, groups, cubes, part_origin))
        elif isinstance(child, str):
            name = cubes.get(child, {}).get("name", child)
            sys.exit(f"error: cube {name!r} sits directly in {group_name!r}. Every cube must live in "
                     f"a bone group - that group becomes the ModelPart the part hangs from.")

    if not bones:
        sys.exit(f"error: group {group_name!r} has no bone groups in it; nothing to export")

    res = data.get("resolution", {})
    geo = {
        "texture_width": int(res.get("width", 64)),
        "texture_height": int(res.get("height", 32)),
        "bones": bones,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(geo, indent=2) + "\n", encoding="utf-8")
    if not quiet:
        print(f"exported {count_cubes(bones)} cubes in {count_bones(bones)} bones -> {out_path}")
    return geo


# ---- import: geometry JSON -> .bbmodel --------------------------------------------------------

def det_uuid(path):
    return str(uuid.uuid5(UUID_NS, path))


def bone_to_group(bone, parent_origin_bb, path, elements, groups, texture_index=None):
    delta = flip_delta(bone.get("pivot", [0, 0, 0]))
    origin_bb = [parent_origin_bb[i] + delta[i] for i in range(3)]
    guid = det_uuid(path)
    pivot_abs_geo = flip_point(origin_bb)

    children = []
    for i, cube in enumerate(bone.get("cubes", [])):
        cuid = det_uuid(f"{path}/cube{i}")
        origin, size = cube["origin"], cube["size"]
        lo_geo = [pivot_abs_geo[j] + origin[j] for j in range(3)]
        hi_geo = [lo_geo[j] + size[j] for j in range(3)]
        # Both flips invert the ordering on X and Y, so the geo maximum is the Blockbench minimum.
        frm = [num(-hi_geo[0]), num(BB_Y - hi_geo[1]), num(lo_geo[2])]
        to = [num(-lo_geo[0]), num(BB_Y - lo_geo[1]), num(hi_geo[2])]
        # In a single-texture project every face samples the only texture there is, so `faces` is
        # left off entirely; in a rig it is the only way to say "this cube wears the part's master
        # and not the player's skin".
        faces = None if texture_index is None else {
            d: {"uv": [0, 0, 0, 0], "texture": texture_index}
            for d in ("north", "east", "south", "west", "up", "down")}
        elements.append({
            "name": f"{bone.get('name', 'bone')}_{i}",
            "box_uv": True,
            "rescale": False,
            "locked": False,
            "render_order": "default",
            "allow_mirror_modeling": True,
            "from": frm,
            "to": to,
            "autouv": 0,
            "color": 0,
            "inflate": cube.get("inflate", 0),
            "mirror_uv": bool(cube.get("mirror", False)),
            "origin": [num(v) for v in origin_bb],
            "uv_offset": [int(v) for v in cube.get("uv", [0, 0])],
            **({"faces": faces} if faces else {}),
            "type": "cube",
            "uuid": cuid,
        })
        children.append(cuid)

    for i, child in enumerate(bone.get("children", [])):
        children.append(bone_to_group(
            child, origin_bb, f"{path}/{child.get('name', i)}", elements, groups, texture_index))

    groups.append(make_group(bone.get("name", "bone"), guid, origin_bb,
                             flip_rot(bone.get("rotation", [0, 0, 0])),
                             children, locked=False, color=0,
                             mirror_uv=bool(bone.get("mirror", False))))
    return guid


def make_group(name, guid, origin_bb, rotation_bb, children, locked=False, color=0, mirror_uv=False):
    """One Blockbench group. `_tree` is stripped by build_bbmodel once the outliner is assembled."""
    return {
        "name": name,
        "uuid": guid,
        "export": True,
        "locked": locked,
        "origin": [num(v) for v in origin_bb],
        "rotation": [num(v) for v in rotation_bb],
        "color": color,
        "mirror_uv": mirror_uv,
        "visibility": True,
        "autouv": 0,
        "isOpen": True,
        "_tree": {"uuid": guid, "isOpen": True, "children": children},
    }


def build_bbmodel(geo, name, anchor_geo=(0.0, 0.0, 0.0), reference=None, textures=None,
                  animations=None, model_format="modded_entity", part_parent=None,
                  part_texture=None):
    """Assemble a Blockbench project.

    `reference` is an optional (elements, groups) pair of locked geometry - the vanilla body and
    armor - that bb_rig.py supplies. The part being authored always lives in a group named `part`,
    placed at the anchor so that what you see in Blockbench is what ArmorDecorationLayer will draw.

    `part_parent` is the uuid of a reference group the part should hang under, which is what makes
    the part swing with the limb it is attached to instead of standing still while the arm moves.
    Group origins are absolute in Blockbench, so this is purely an outliner change - no coordinate
    anywhere is affected by where the part sits in the tree.

    `model_format` is 'modded_entity' for the plain part projects and 'free' for the rigs. The rigs
    need 'free' for one reason: 'modded_entity' is single_texture, and a rig has to show the skin
    (64x64), the armor layers (64x32) and the part's own master at the same time. 'free' is the only
    animation-capable format with both multiple textures and per-texture UV sizes."""
    elements, groups = [], []
    part_origin_bb = flip_point(list(anchor_geo))

    part_children = []
    for i, bone in enumerate(geo.get("bones", [])):
        part_children.append(bone_to_group(
            bone, part_origin_bb, f"{name}/{bone.get('name', i)}", elements, groups, part_texture))

    part_uuid = det_uuid(f"{name}/{PART_GROUP}")
    groups.append(make_group(PART_GROUP, part_uuid, part_origin_bb, [0, 0, 0],
                             part_children, locked=False, color=4))

    ref_elements, ref_groups = reference if reference is not None else ([], [])
    all_groups = ref_groups + groups

    tree_by_uuid = {g["uuid"]: g.pop("_tree") for g in all_groups}

    # Hanging the part off a bone is just re-parenting it in the tree; the loop below then sees the
    # part uuid as claimed and stops emitting it at the top of the outliner.
    if part_parent is not None:
        if part_parent not in tree_by_uuid:
            raise KeyError(f"part_parent {part_parent} is not one of the reference groups")
        tree_by_uuid[part_parent]["children"].append(part_uuid)
    # Only groups nothing else claims as a child sit at the top of the outliner.
    claimed = {c for t in tree_by_uuid.values() for c in t["children"] if c in tree_by_uuid}

    def nest(node):
        node["children"] = [nest(tree_by_uuid[c]) if c in tree_by_uuid else c
                            for c in node["children"]]
        return node

    outliner = [nest(tree_by_uuid[g["uuid"]]) for g in all_groups if g["uuid"] not in claimed]

    model = {
        "meta": {"format_version": "5.0", "model_format": model_format, "box_uv": True},
        "name": name,
        "model_identifier": name,
        "modded_entity_flip_y": True,
        "resolution": {
            "width": int(geo.get("texture_width", 64)),
            "height": int(geo.get("texture_height", 32)),
        },
        "elements": ref_elements + elements,
        "groups": all_groups,
        "outliner": outliner,
        "textures": textures or [],
    }
    if animations:
        model["animations"] = animations
    return model


def do_import(geo_path, out_path, anchor_geo=(0.0, 0.0, 0.0), quiet=False):
    geo_path, out_path = Path(geo_path), Path(out_path)
    geo = json.loads(geo_path.read_text(encoding="utf-8"))
    model = build_bbmodel(geo, geo_path.stem, anchor_geo)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")
    if not quiet:
        print(f"imported {count_cubes(geo['bones'])} cubes -> {out_path}")
    return model


# ---- roundtrip verification -------------------------------------------------------------------

def canonical(geo):
    """Normalise away the optional fields the format lets an author omit, so 'the same model' can be
    compared as equality. A hand-written file may spell out "rotation": [0,0,0] where a generated one
    omits it; that is not a difference in the model."""
    def bone(b):
        return {
            "name": b["name"],
            "pivot": [num(v) for v in b.get("pivot", [0, 0, 0])],
            "rotation": [num(v) for v in b.get("rotation", [0, 0, 0])],
            "mirror": bool(b.get("mirror", False)),
            "cubes": [{
                "origin": [num(v) for v in c["origin"]],
                "size": [num(v) for v in c["size"]],
                "uv": [int(v) for v in c.get("uv", [0, 0])],
                "inflate": num(c.get("inflate", 0)),
                "mirror": bool(c.get("mirror", False)),
            } for c in b.get("cubes", [])],
            "children": [bone(c) for c in b.get("children", [])],
        }
    return {
        "texture_width": int(geo.get("texture_width", 64)),
        "texture_height": int(geo.get("texture_height", 32)),
        "bones": [bone(b) for b in geo["bones"]],
    }


def roundtrip(geo_path):
    """geo -> bb -> geo, twice.

    Two claims are checked, and they are different claims. Semantic equality says the conversion
    loses nothing. Idempotence - pass two byte-identical to pass one - says the writer is stable,
    which is what makes the diff of a regenerated part readable. Byte-identity against the *original*
    is deliberately not claimed: a hand-authored file may carry redundant optional fields, and
    demanding it match byte for byte would be testing the author's typing, not the conversion."""
    geo_path = Path(geo_path)
    original = json.loads(geo_path.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        source, passes = geo_path, []
        for i in range(2):
            bb = tmp / f"pass{i}.bbmodel"
            geo_out = tmp / f"pass{i}.json"
            model = build_bbmodel(json.loads(source.read_text(encoding="utf-8")), geo_path.stem)
            bb.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")
            export(bb, geo_out, quiet=True)
            passes.append(geo_out)
            source = geo_out

        after = json.loads(passes[0].read_text(encoding="utf-8"))
        semantic = canonical(original) == canonical(after)
        stable = passes[0].read_bytes() == passes[1].read_bytes()

    print(f"roundtrip {geo_path.name}: {count_cubes(original['bones'])} cubes, "
          f"{count_bones(original['bones'])} bones")
    print(f"  semantic equality (nothing lost) : {'PASS' if semantic else 'FAIL'}")
    print(f"  idempotent (writer is stable)    : {'PASS' if stable else 'FAIL'}")
    if not semantic:
        print("\n  original  :", json.dumps(canonical(original), indent=2)[:1200])
        print("\n  roundtrip :", json.dumps(canonical(after), indent=2)[:1200])
    return semantic and stable


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("export", help="Blockbench project -> decoration geometry JSON")
    e.add_argument("bbmodel", type=Path)
    e.add_argument("--out", type=Path)
    e.add_argument("--group", default=PART_GROUP)

    i = sub.add_parser("import", help="decoration geometry JSON -> Blockbench project")
    i.add_argument("geometry", type=Path)
    i.add_argument("--out", type=Path)

    r = sub.add_parser("roundtrip", help="verify the conversion loses nothing")
    r.add_argument("geometry", type=Path)

    args = ap.parse_args()
    if args.cmd == "export":
        export(args.bbmodel, args.out or GEO_DIR / f"{args.bbmodel.stem}.json", args.group)
    elif args.cmd == "import":
        do_import(args.geometry, args.out or RIG_DIR / f"{args.geometry.stem}.bbmodel")
    else:
        sys.exit(0 if roundtrip(args.geometry) else 1)


if __name__ == "__main__":
    main()
