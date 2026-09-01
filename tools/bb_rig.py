"""
Generate a Blockbench reference rig for one decoration anchor.

A rig is an ordinary Blockbench project containing the vanilla humanoid body, the four armor layers
over it at their real inflate, all locked, and one empty group named `part` placed exactly where
ArmorDecorationLayer will draw. Model inside `part` and what you see is what the game renders - the
rig is not an approximation of the render path, it is the same three steps the layer performs:

    resolvePart(model, attachment.part()).translateAndRotate(poseStack)
    poseStack.translate(attachment.x() / 16, attachment.y() / 16, attachment.z() / 16)
    [scale(-1, 1, 1) for the mirrored half of a pair]

so the `part` group's origin is just (parent bone pivot + anchor offset), converted to Blockbench
space by bb_geo.

The anchor offsets are PARSED OUT OF DecorationAnchor.java rather than copied here. Copying them
would create a second source of truth that drifts the first time an offset is tuned in game, and the
whole point of these rigs is that they agree with the code.

The body numbers below are the one thing this file does hardcode, and they were read out of the
compiled HumanoidModel.createMesh / LayerDefinitions rather than remembered.

Usage:
    python tools/bb_rig.py --all
    python tools/bb_rig.py crest
    python tools/bb_rig.py crest --part src/main/resources/.../feathering.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from bb_geo import PART_GROUP, RIG_DIR, build_bbmodel, det_uuid, flip_point, make_group, num

ROOT = Path(__file__).resolve().parent.parent
ANCHOR_SRC = ROOT / "src" / "main" / "java" / "com" / "mattjesmc" / "armorpieces" / "decoration" / "DecorationAnchor.java"
GEO_DIR = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration"

# net.minecraft.client.model.HumanoidModel.createMesh - pivot, then the box relative to it.
# Verified against the disassembled 26.2 class, not recalled.
BODY = {
    "head":      ((0.0, 0.0, 0.0),    (-4.0, -8.0, -4.0), (8.0, 8.0, 8.0)),
    "body":      ((0.0, 0.0, 0.0),    (-4.0, 0.0, -2.0),  (8.0, 12.0, 4.0)),
    "left_arm":  ((5.0, 2.0, 0.0),    (-1.0, -2.0, -2.0), (4.0, 12.0, 4.0)),
    "right_arm": ((-5.0, 2.0, 0.0),   (-3.0, -2.0, -2.0), (4.0, 12.0, 4.0)),
    "left_leg":  ((1.9, 12.0, 0.0),   (-2.0, 0.0, -2.0),  (4.0, 12.0, 4.0)),
    "right_leg": ((-1.9, 12.0, 0.0),  (-2.0, 0.0, -2.0),  (4.0, 12.0, 4.0)),
}

# LayerDefinitions: OUTER_ARMOR_DEFORMATION = 1.0F, INNER_ARMOR_DEFORMATION = 0.5F. Leggings are the
# inner layer; everything else is the outer one.
ARMOR_LAYERS = {
    "armor_helmet":     (["head"], 1.0),
    "armor_chestplate": (["body", "left_arm", "right_arm"], 1.0),
    "armor_leggings":   (["body", "left_leg", "right_leg"], 0.5),
    "armor_boots":      (["left_leg", "right_leg"], 1.0),
}

# Outliner colours, so the locked reference reads apart from the part at a glance.
COLOR_BODY, COLOR_ARMOR = 7, 3


def parse_anchors(path=ANCHOR_SRC):
    """Read the anchor table out of the enum.

    Attachments only ever appear inside an enum constant's argument list, so associating each
    Attachment.of/mirrored with the nearest preceding constant header is enough - no brace matching,
    and nothing in the javadoc or the record's own factory methods matches the call shape."""
    text = Path(path).read_text(encoding="utf-8")
    header = re.compile(r'^ {4}([A-Z][A-Z_]*)\("([a-z_]+)",\s*ArmorType\.([A-Z_]+),', re.MULTILINE)
    attach = re.compile(
        r'Attachment\.(of|mirrored)\(HumanoidPart\.([A-Z_]+),\s*'
        r'(-?[\d.]+)F,\s*(-?[\d.]+)F,\s*(-?[\d.]+)F\)')

    anchors, current = {}, None
    for m in re.finditer(f'(?:{header.pattern})|(?:{attach.pattern})', text, re.MULTILINE):
        if m.group(1):
            current = m.group(2)
            anchors[current] = {"armor_type": m.group(3), "attachments": []}
        elif current is not None:
            anchors[current]["attachments"].append({
                "mirror": m.group(4) == "mirrored",
                "part": m.group(5).lower(),
                "offset": (float(m.group(6)), float(m.group(7)), float(m.group(8))),
            })

    if not anchors:
        sys.exit(f"error: parsed no anchors out of {path}; the enum's shape must have changed")
    for name, a in anchors.items():
        if not a["attachments"]:
            sys.exit(f"error: anchor {name!r} parsed with no attachments")
    return anchors


def ref_cube(name, pivot, origin, size, inflate, uid, color):
    """One locked reference box, in absolute Blockbench coordinates."""
    lo = [pivot[i] + origin[i] for i in range(3)]
    hi = [lo[i] + size[i] for i in range(3)]
    return {
        "name": name,
        "box_uv": True,
        "rescale": False,
        "locked": True,
        "render_order": "default",
        "allow_mirror_modeling": False,
        "from": [num(-hi[0]), num(24.0 - hi[1]), num(lo[2])],
        "to": [num(-lo[0]), num(24.0 - lo[1]), num(hi[2])],
        "autouv": 0,
        "color": color,
        "inflate": inflate,
        "mirror_uv": False,
        "origin": [num(v) for v in flip_point(list(pivot))],
        "uv_offset": [0, 0],
        "type": "cube",
        "uuid": uid,
    }


def build_reference(anchor_name):
    """The locked vanilla body plus all four armor layers, as (elements, groups).

    All four layers are included rather than just the anchor's own, because a part is worn on a
    figure that may be wearing the rest - a crest is judged against a chestplate's shoulder line as
    much as against the helmet. Each layer is its own group so the ones in the way can be hidden."""
    elements, groups = [], []

    body_children = []
    for part, (pivot, origin, size) in BODY.items():
        uid = det_uuid(f"rig/{anchor_name}/body/{part}")
        elements.append(ref_cube(part, pivot, origin, size, 0, uid, COLOR_BODY))
        body_children.append(uid)
    groups.append(make_group("body_base", det_uuid(f"rig/{anchor_name}/body"),
                             flip_point([0.0, 0.0, 0.0]), [0, 0, 0], body_children,
                             locked=True, color=COLOR_BODY))

    layer_uuids = [det_uuid(f"rig/{anchor_name}/body")]
    for layer, (parts, inflate) in ARMOR_LAYERS.items():
        children = []
        for part in parts:
            pivot, origin, size = BODY[part]
            uid = det_uuid(f"rig/{anchor_name}/{layer}/{part}")
            elements.append(ref_cube(f"{part}_armor", pivot, origin, size, inflate, uid, COLOR_ARMOR))
            children.append(uid)
        guid = det_uuid(f"rig/{anchor_name}/{layer}")
        groups.append(make_group(layer, guid, flip_point([0.0, 0.0, 0.0]), [0, 0, 0], children,
                                 locked=True, color=COLOR_ARMOR))
        layer_uuids.append(guid)

    groups.append(make_group("reference", det_uuid(f"rig/{anchor_name}/reference"),
                             flip_point([0.0, 0.0, 0.0]), [0, 0, 0], layer_uuids,
                             locked=True, color=COLOR_BODY))
    return elements, groups


def build_rig(anchor_name, anchors, part_geo=None, resolution=None):
    anchor = anchors[anchor_name]
    attachment = anchor["attachments"][0]
    pivot = BODY[attachment["part"]][0]
    anchor_geo = tuple(pivot[i] + attachment["offset"][i] for i in range(3))

    geo = part_geo or {"bones": []}
    if resolution:
        geo = dict(geo, texture_width=resolution[0], texture_height=resolution[1])
    geo.setdefault("texture_width", 64)
    geo.setdefault("texture_height", 32)

    model = build_bbmodel(geo, f"rig_{anchor_name}", anchor_geo, build_reference(anchor_name))

    # build_bbmodel only emits a `part` group when there are bones to put in it.
    if not geo["bones"]:
        part_uuid = det_uuid(f"rig_{anchor_name}/{PART_GROUP}")
        assert any(g["uuid"] == part_uuid for g in model["groups"]), "part group missing"

    return model, anchor_geo, attachment


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("anchors", nargs="*", help="anchor ids, e.g. crest brow horns")
    ap.add_argument("--all", action="store_true", help="generate a rig for every anchor")
    ap.add_argument("--part", type=Path, help="seed the rig with an existing geometry JSON")
    ap.add_argument("--res", help="texture resolution as WxH (default: the part's, or 64x32)")
    ap.add_argument("--out-dir", type=Path, default=RIG_DIR)
    args = ap.parse_args()

    anchors = parse_anchors()
    names = list(anchors) if args.all else args.anchors
    if not names:
        sys.exit(f"error: name an anchor or pass --all. Known: {', '.join(anchors)}")
    for n in names:
        if n not in anchors:
            sys.exit(f"error: unknown anchor {n!r}. Known: {', '.join(anchors)}")

    part_geo = json.loads(args.part.read_text(encoding="utf-8")) if args.part else None
    resolution = tuple(int(v) for v in args.res.lower().split("x")) if args.res else None

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name in names:
        model, anchor_geo, attachment = build_rig(name, anchors, part_geo, resolution)
        out = args.out_dir / f"{name}.bbmodel"
        out.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")
        pair = " (mirrored pair)" if len(anchors[name]["attachments"]) > 1 else ""
        print(f"{name:10s} on {attachment['part']:10s} at geo "
              f"{tuple(num(v) for v in anchor_geo)}{pair} -> {out}")


if __name__ == "__main__":
    main()
