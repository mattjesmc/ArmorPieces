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
import math
import os
import re
import sys
from pathlib import Path

from PIL import Image

import mc_humanoid
import vanilla_assets
from bb_geo import PART_GROUP, RIG_DIR, build_bbmodel, det_uuid, flip_point, make_group, num

# Minecraft ticks per second. The walk cycle's length is a tick count; Blockbench's timeline is in
# seconds.
TICKS_PER_SECOND = 20.0

ROOT = Path(__file__).resolve().parent.parent
ANCHOR_SRC = ROOT / "src" / "main" / "java" / "com" / "mattjesmc" / "armorpieces" / "decoration" / "DecorationAnchor.java"
GEO_DIR = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration"

# The body, the armor and the walk cycle all come from mc_humanoid, which transcribes them from the
# decompiled 26.2 sources. Nothing about the vanilla figure is described twice.
ASSETS = ROOT / "tools" / ".mcassets"

# Outliner colours, so the locked reference reads apart from the part at a glance.
COLOR_BODY, COLOR_ARMOR = 7, 3

# The slot whose armor a given anchor sits on. DecorationAnchor already declares this per anchor as
# an ArmorType; this maps that vocabulary onto mc_humanoid's slot names.
ARMOR_TYPE_TO_SLOT = {
    "HELMET": "helmet", "CHESTPLATE": "chestplate", "LEGGINGS": "leggings", "BOOTS": "boots",
}


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


def ref_cube(box, pivot, uid, color, texture_index):
    """One locked reference box, in absolute Blockbench coordinates.

    `box` is an mc_humanoid box dict; `pivot` is its bone's pivot in entity space. Box UV is driven
    by `uv_offset`, exactly as it is for the part geometry - the per-face `faces` entries exist only
    to say WHICH texture the face samples, which is the one thing uv_offset cannot express and the
    whole reason a rig needs a multi-texture format."""
    origin, size = box["origin"], box["size"]
    lo = [pivot[i] + origin[i] for i in range(3)]
    hi = [lo[i] + size[i] for i in range(3)]
    faces = {d: {"uv": [0, 0, 0, 0], "texture": texture_index}
             for d in ("north", "east", "south", "west", "up", "down")}
    return {
        "name": box["name"],
        "box_uv": True,
        "rescale": False,
        "locked": True,
        "render_order": "default",
        "allow_mirror_modeling": False,
        "from": [num(-hi[0]), num(24.0 - hi[1]), num(lo[2])],
        "to": [num(-lo[0]), num(24.0 - lo[1]), num(hi[2])],
        "autouv": 0,
        "color": color,
        "inflate": num(box["inflate"]),
        "mirror_uv": bool(box["mirror"]),
        "origin": [num(v) for v in flip_point(list(pivot))],
        "uv_offset": [int(box["tex"][0]), int(box["tex"][1])],
        "faces": faces,
        "type": "cube",
        "uuid": uid,
    }


def build_reference(anchor_name, slim=False, texture_index=None):
    """The locked player wearing all four armor slots, as (elements, groups, bone_uuids).

    One group per posed bone, not one group per layer. That is the change that makes the rig worth
    animating: `right_arm` holds the arm, its sleeve, and the chestplate sleeve over it, so when the
    walk cycle rotates that group the armor swings with the limb - and so does the part, once
    build_bbmodel hangs it under the same group.

    All four armor slots are included rather than just the anchor's own, because a part is worn on a
    figure that may be wearing the rest - a crest is judged against a chestplate's shoulder line as
    much as against the helmet. Every cube is named `<part>_<slot>`, so hiding one slot is a matter
    of selecting by name; they are no longer separable by group, which is the price of grouping by
    bone instead of by layer."""
    texture_index = texture_index or {}
    elements = []
    by_bone: dict[str, list[str]] = {bone: [] for bone in mc_humanoid.BONES}

    def add(box, layer, color):
        uid = det_uuid(f"rig/{anchor_name}/{layer}/{box['name']}")
        pivot = mc_humanoid.BONES[box["bone"]]
        elements.append(ref_cube(box, pivot, uid, color, texture_index.get(box["tex_key"], 0)))
        by_bone[box["bone"]].append(uid)

    for box in mc_humanoid.player_boxes(slim):
        add(dict(box, tex_key="skin"), "skin", COLOR_BODY)
    for slot, spec in mc_humanoid.ARMOR_SLOTS.items():
        for box in mc_humanoid.armor_boxes(slot):
            add(dict(box, tex_key=spec["texture"]), slot, COLOR_ARMOR)

    groups, bone_uuids = [], {}
    for bone, pivot in mc_humanoid.BONES.items():
        guid = det_uuid(f"rig/{anchor_name}/bone/{bone}")
        bone_uuids[bone] = guid
        groups.append(make_group(bone, guid, flip_point(list(pivot)), [0, 0, 0], by_bone[bone],
                                 locked=True, color=COLOR_BODY))

    groups.append(make_group("reference", det_uuid(f"rig/{anchor_name}/reference"),
                             flip_point([0.0, 0.0, 0.0]), [0, 0, 0], list(bone_uuids.values()),
                             locked=True, color=COLOR_BODY))
    return elements, groups, bone_uuids


def texture_entry(name, path, uid, uv_size, out_dir):
    """One linked texture.

    Linked, never embedded: these are Mojang's PNGs, the rigs are committed, and a base64 copy in a
    tracked file would be redistributing them. The cost is that a fresh clone shows an untextured
    rig until `python tools/vanilla_assets.py` has run, which is the same bargain `.modpage/`'s
    texture cache already makes. The path is relative so the rigs diff cleanly across machines."""
    relative = os.path.relpath(path, out_dir).replace("\\", "/")
    return {
        "path": relative,
        "relative_path": relative,
        "name": name,
        "folder": "",
        "namespace": "",
        "id": name,
        "group": "",
        "width": uv_size[0],
        "height": uv_size[1],
        "uv_width": uv_size[0],
        "uv_height": uv_size[1],
        "particle": False,
        "use_as_default": False,
        "layers_enabled": False,
        "sync_to_project": "",
        "render_mode": "default",
        "render_sides": "auto",
        "frame_time": 1,
        "frame_order_type": "loop",
        "frame_order": "",
        "frame_interpolate": False,
        "visible": True,
        "internal": False,
        "saved": True,
        "uuid": uid,
    }


def build_textures(anchor_name, material, slim, out_dir, master=None):
    """The rig's textures, and the index each geometry layer samples.

    Three vanilla ones - the skin, the armor layer and the leggings layer, which really is a second
    file rather than a second region of the first - plus the part's own greyscale master when there
    is one, so the piece shows up painted rather than as a blank shell."""
    skin = ASSETS / "skin" / ("slim_steve.png" if slim else "wide_steve.png")
    armor = ASSETS / "armor" / f"{material}.png"
    leggings = ASSETS / "armor_leggings" / f"{material}.png"

    specs = [("skin", skin, (64, 64)), ("armor", armor, (64, 32))]
    # Not every material has a leggings layer - turtle scute is a helmet and nothing else - so the
    # leggings geometry falls back to the layer that does exist rather than to nothing.
    if leggings.is_file():
        specs.append(("armor_leggings", leggings, (64, 32)))

    textures, index = [], {}
    for i, (key, path, uv) in enumerate(specs):
        index[key] = i
        textures.append(texture_entry(
            key, path, det_uuid(f"rig/{anchor_name}/texture/{key}"), uv, out_dir))
    index.setdefault("armor_leggings", index["armor"])

    part_texture = None
    if master is not None and Path(master).is_file():
        master = Path(master)
        with Image.open(master) as image:
            uv = image.size
        part_texture = len(textures)
        textures.append(texture_entry(
            "part", master, det_uuid(f"rig/{anchor_name}/texture/part"), uv, out_dir))

        # The companion sheets, when the part has any: the static layer, `<part>_static.png`, and
        # one fitting mask per `<part>_<fitting>.png` - the same set sync_decoration_masters.py
        # installs. They are loaded but nothing samples them: a cube face reads exactly one
        # texture, and the sheets are composited by the game (and by preview_material.py), not by
        # stacking them in the viewport. Having them in the project is what makes them paintable
        # at all - switch the part onto one to edit it. Each is the texture `part_<suffix>`, which
        # is how the plugin finds them.
        for companion in sorted(master.parent.glob(f"{master.stem}_*.png")):
            suffix = companion.stem[len(master.stem):]
            key = f"part{suffix}"
            with Image.open(companion) as image:
                companion_uv = image.size
            index[key] = len(textures)
            textures.append(texture_entry(
                key, companion, det_uuid(f"rig/{anchor_name}/texture/{key}"), companion_uv, out_dir))

    return textures, index, part_texture


def keyframe(uid, time, rotation):
    """One rotation keyframe. Blockbench stores rotations in degrees, and its X and Y are flipped
    relative to the game's for the same reason every coordinate here is - see bb_geo.flip_rot."""
    x, y, z = (math.degrees(v) for v in rotation)
    return {
        "channel": "rotation",
        "data_points": [{"x": num(-x), "y": num(-y), "z": num(z)}],
        "uuid": uid,
        "time": num(time),
        "color": -1,
        "interpolation": "linear",
    }


def build_animation(anchor_name, label, amplitude, bone_uuids, samples=8):
    """One baked limb-swing cycle.

    Baked rather than hand-authored: every pose comes from mc_humanoid.limb_pose, which is
    HumanoidModel.setupAnim's own arithmetic, so the preview cannot drift from what the game does
    the way an eyeballed keyframe would. Eight samples per cycle with linear interpolation, because
    the curve is a cosine and eight points carry one to well under a degree of error.

    The arm bob is sampled along with the swing. It is driven by ageInTicks rather than by the swing
    position, so it does not truly share this loop's period - but it is a 3-degree wobble, and
    pinning it to the cycle is what lets the whole thing loop seamlessly."""
    length = mc_humanoid.cycle_ticks(amplitude) / TICKS_PER_SECOND
    animators = {}

    for step in range(samples + 1):
        fraction = step / samples
        position = fraction * mc_humanoid.cycle_ticks(amplitude)
        pose = mc_humanoid.limb_pose(position, amplitude, position)
        for bone, rotation in pose.items():
            if bone not in bone_uuids:
                continue
            animator = animators.setdefault(
                bone_uuids[bone], {"name": bone, "type": "bone", "keyframes": []})
            animator["keyframes"].append(keyframe(
                det_uuid(f"rig/{anchor_name}/anim/{label}/{bone}/{step}"),
                fraction * length, rotation))

    return {
        "uuid": det_uuid(f"rig/{anchor_name}/anim/{label}"),
        "name": label,
        "loop": "loop",
        "override": False,
        "length": num(length),
        "snapping": 24,
        "selected": False,
        "anim_time_update": "",
        "blend_weight": "",
        "start_delay": "",
        "loop_delay": "",
        "animators": animators,
    }


def build_rig(anchor_name, anchors, part_geo=None, resolution=None, out_dir=RIG_DIR,
              slim=False, material="iron", master=None, animate=True):
    anchor = anchors[anchor_name]
    attachment = anchor["attachments"][0]
    pivot = mc_humanoid.BONES[attachment["part"]]
    anchor_geo = tuple(pivot[i] + attachment["offset"][i] for i in range(3))

    geo = part_geo or {"bones": []}
    if resolution:
        geo = dict(geo, texture_width=resolution[0], texture_height=resolution[1])
    geo.setdefault("texture_width", 64)
    geo.setdefault("texture_height", 32)

    textures, index, part_texture = build_textures(
        anchor_name, material, slim, Path(out_dir), master)
    elements, groups, bone_uuids = build_reference(anchor_name, slim, index)

    animations = None
    if animate:
        animations = [
            build_animation(anchor_name, "walk", mc_humanoid.WALK_AMPLITUDE, bone_uuids),
            build_animation(anchor_name, "sprint", mc_humanoid.SPRINT_AMPLITUDE, bone_uuids),
        ]

    model = build_bbmodel(
        geo, f"rig_{anchor_name}", anchor_geo, (elements, groups),
        textures=textures, animations=animations, model_format="free",
        # The part hangs off the bone it is attached to, so it swings with the limb and with the
        # armor over it. That is the whole point of animating the rig.
        part_parent=bone_uuids[attachment["part"]], part_texture=part_texture)

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
    ap.add_argument("--slim", action="store_true",
                    help="use the 3-wide (Alex) body. The armor is 4-wide either way.")
    ap.add_argument("--material", default="iron",
                    help="armor material to show the figure wearing (default: iron)")
    ap.add_argument("--master", type=Path,
                    help="the part's greyscale master, so the part renders painted "
                         "(default: tools/decoration_masters/<part>.png when --part is given)")
    ap.add_argument("--no-animation", action="store_true",
                    help="omit the walk and sprint cycles")
    ap.add_argument("--list-anchors", action="store_true",
                    help="print the anchor table as JSON and exit, for tooling to read")
    args = ap.parse_args()

    if args.list_anchors:
        # The Blockbench plugin needs the same anchor list this script parses out of the enum, and
        # a second parser in another language is exactly the drift this file exists to avoid.
        print(json.dumps({
            name: {"armor_type": a["armor_type"],
                   "part": a["attachments"][0]["part"],
                   "mirrored": len(a["attachments"]) > 1}
            for name, a in parse_anchors().items()
        }, indent=2))
        return

    if not (ASSETS / "skin").is_dir():
        print("no vanilla asset cache; extracting it first")
        vanilla_assets.extract(vanilla_assets.find_jar(vanilla_assets.minecraft_version()))

    anchors = parse_anchors()
    names = list(anchors) if args.all else args.anchors
    if not names:
        sys.exit(f"error: name an anchor or pass --all. Known: {', '.join(anchors)}")
    for n in names:
        if n not in anchors:
            sys.exit(f"error: unknown anchor {n!r}. Known: {', '.join(anchors)}")

    part_geo = json.loads(args.part.read_text(encoding="utf-8")) if args.part else None
    resolution = tuple(int(v) for v in args.res.lower().split("x")) if args.res else None

    master = args.master
    if master is None and args.part is not None:
        candidate = ROOT / "tools" / "decoration_masters" / f"{args.part.stem}.png"
        master = candidate if candidate.is_file() else None

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name in names:
        model, anchor_geo, attachment = build_rig(
            name, anchors, part_geo, resolution, out_dir=args.out_dir, slim=args.slim,
            material=args.material, master=master, animate=not args.no_animation)
        out = args.out_dir / f"{name}.bbmodel"
        out.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")
        pair = " (mirrored pair)" if len(anchors[name]["attachments"]) > 1 else ""
        print(f"{name:10s} on {attachment['part']:10s} at geo "
              f"{tuple(num(v) for v in anchor_geo)}{pair} -> {out}")


if __name__ == "__main__":
    main()
