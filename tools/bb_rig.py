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

A rig can also hold a whole OUTFIT rather than one socket's part: `--wear <set.json>` builds the
figure wearing every piece in a set, each at its anchor and each painted for its own trim material,
with the armor underneath wearing the set's base materials, its skin and its cloth. That rig is
locked from end to end, because it is for looking at rather than for working in - it is what the
site's wardrobe shows. An outfit may name pieces from any pack, so `--pack <dir>` names the folders
to look in; they are searched before the mod's own resources, never instead of them.

Usage:
    python tools/bb_rig.py --all
    python tools/bb_rig.py crest
    python tools/bb_rig.py crest --part src/main/resources/.../feathering.json
    python tools/bb_rig.py --wear docs/examples/set.json
    python tools/bb_rig.py --wear the_reef.json --pack packs/coral/datapack --pack packs/coral/resourcepack
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
import preview_material
from bb_geo import (PART_GROUP, RIG_DIR, assemble as bb_assemble, bone_to_group,
                    build_bbmodel, det_uuid, flip_point, make_group, num)

# Minecraft ticks per second. The walk cycle's length is a tick count; Blockbench's timeline is in
# seconds.
TICKS_PER_SECOND = 20.0

ROOT = Path(__file__).resolve().parent.parent
ANCHOR_SRC = ROOT / "src" / "main" / "java" / "com" / "mattjesmc" / "armorpieces" / "decoration" / "DecorationAnchor.java"
GEO_DIR = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "armorpieces" / "decoration"

# The body, the armor and the walk cycle all come from mc_humanoid, which transcribes them from the
# decompiled 26.2 sources. Nothing about the vanilla figure is described twice.
ASSETS = ROOT / "tools" / ".mcassets"
# The studio figure: our own player skin and the mod's plate skin baked in iron, worn when the
# game's textures are not here. Same boxes, our pixels. Written by tools/studio_figure.py.
STUDIO = ROOT / "tools" / "studio"

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


def ref_cube(box, pivot, uid, color, texture_index, locked=True):
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
        "locked": locked,
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


def build_reference(anchor_name, slim=False, texture_index=None, paint_armor=False,
                    slot_texture=None):
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

    def add(box, layer, color, locked=True):
        uid = det_uuid(f"rig/{anchor_name}/{layer}/{box['name']}")
        pivot = mc_humanoid.BONES[box["bone"]]
        elements.append(ref_cube(box, pivot, uid, color, texture_index.get(box["tex_key"], 0), locked))
        by_bone[box["bone"]].append(uid)

    for box in mc_humanoid.player_boxes(slim):
        add(dict(box, tex_key="skin"), "skin", COLOR_BODY)
    for slot, spec in mc_humanoid.ARMOR_SLOTS.items():
        # `slot_texture` lets each slot wear its own sheet, which is what a wardrobe needs: four
        # armor pieces are four items and may be four materials. Without it every slot samples the
        # one layer texture its deformation uses, which is what a part or skin rig wants.
        key = (slot_texture or {}).get(slot, spec["texture"])
        for box in mc_humanoid.armor_boxes(slot):
            # A skin rig is the one case where the armor is the thing being worked on: its cubes
            # are unlocked so the brush reaches them, and the bone groups above them have to be
            # unlocked too, since a locked group locks its subtree.
            add(dict(box, tex_key=key), slot, COLOR_ARMOR, locked=not paint_armor)

    groups, bone_uuids = [], {}
    for bone, pivot in mc_humanoid.BONES.items():
        guid = det_uuid(f"rig/{anchor_name}/bone/{bone}")
        bone_uuids[bone] = guid
        groups.append(make_group(bone, guid, flip_point(list(pivot)), [0, 0, 0], by_bone[bone],
                                 locked=not paint_armor, color=COLOR_BODY))

    groups.append(make_group("reference", det_uuid(f"rig/{anchor_name}/reference"),
                             flip_point([0.0, 0.0, 0.0]), [0, 0, 0], list(bone_uuids.values()),
                             locked=not paint_armor, color=COLOR_BODY))
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


def figure(material, slim):
    """What the reference figure wears: the game's own skin and armor when they have been extracted,
    else the studio set. Returns (skin, armor, leggings, description); the leggings path may not
    exist, which the caller already handles for materials that have no leggings layer."""
    skin = ASSETS / "skin" / ("slim_steve.png" if slim else "wide_steve.png")
    armor = ASSETS / "armor" / f"{material}.png"
    if skin.is_file() and armor.is_file():
        return (skin, armor, ASSETS / "armor_leggings" / f"{material}.png",
                {"figure": "vanilla", "material": material, "label": f"vanilla {material}"})
    return (STUDIO / ("skin_slim.png" if slim else "skin.png"), STUDIO / "armor.png",
            STUDIO / "armor_leggings.png",
            {"figure": "studio", "material": "iron", "label": "studio figure, plate in iron"})


def build_textures(anchor_name, material, slim, out_dir, master=None):
    """The rig's textures, and the index each geometry layer samples.

    Three for the figure - the skin, the armor layer and the leggings layer, which really is a
    second file rather than a second region of the first - plus the part's own greyscale master
    when there is one, so the piece shows up painted rather than as a blank shell."""
    skin, armor, leggings, _ = figure(material, slim)

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


def build_skin_textures(skin_dir, slim, out_dir):
    """A skin rig's three textures: the player's skin, and the skin's own two authored sheets.

    The armor cubes sample the sheets being painted rather than Mojang's - that is the whole
    difference between this and a part rig. The ids are the names the game gives the folders those
    sheets end up in, `humanoid` and `humanoid_leggings`, which is also what skin_sheets.py calls
    them; `skin` stays the player's own."""
    skin_dir = Path(skin_dir)
    specs = [
        ("skin", figure("iron", slim)[0], (64, 64), "skin"),
        ("humanoid", skin_dir / "humanoid.png", (64, 32), "armor"),
        ("humanoid_leggings", skin_dir / "humanoid_leggings.png", (64, 32), "armor_leggings"),
    ]
    textures, index = [], {}
    for i, (name, path, uv, key) in enumerate(specs):
        index[key] = i
        textures.append(texture_entry(name, path, det_uuid(f"skin/{skin_dir.name}/texture/{name}"),
                                      uv, out_dir))
    return textures, index


def build_skin_rig(skin_dir, out_dir=RIG_DIR, slim=False, animate=True):
    """The player wearing all four armor slots, with the armor unlocked and painted by a skin.

    There is no `part` group and no anchor: a skin is not hung anywhere, it IS the armor. What the
    rig buys is the same thing it buys a part author - the sheets are seen on the body, at the real
    inflate of all four slots at once, so a boot drawn over the leggings or a helmet that swallows
    the face is visible while it is being drawn rather than in game afterwards."""
    skin_dir = Path(skin_dir)
    out_dir = Path(out_dir)
    textures, index = build_skin_textures(skin_dir, slim, out_dir)
    elements, groups, bone_uuids = build_reference(f"skin_{skin_dir.name}", slim, index,
                                                   paint_armor=True)

    animations = None
    if animate:
        animations = [
            build_animation(f"skin_{skin_dir.name}", "walk", mc_humanoid.WALK_AMPLITUDE, bone_uuids),
            build_animation(f"skin_{skin_dir.name}", "sprint", mc_humanoid.SPRINT_AMPLITUDE, bone_uuids),
        ]

    model = build_bbmodel({"bones": [], "texture_width": 64, "texture_height": 32},
                          f"skin_{skin_dir.name}", (0.0, 0.0, 0.0), (elements, groups),
                          textures=textures, animations=animations, model_format="free")

    # build_bbmodel always emits the part group; a skin has no part, so it goes rather than sitting
    # in the outliner as an empty thing to wonder about.
    part_uuid = det_uuid(f"skin_{skin_dir.name}/{PART_GROUP}")
    model["groups"] = [g for g in model["groups"] if g["uuid"] != part_uuid]
    model["outliner"] = [n for n in model["outliner"]
                         if not (isinstance(n, dict) and n.get("uuid") == part_uuid)]
    # The skin's own sheets are the armor here, so only the player's skin says which figure it is.
    model["armorpieces_figure"] = dict(figure("iron", slim)[3], armor="the skin being drawn")
    return model


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


# ---- a whole outfit: the wardrobe --------------------------------------------------------------
#
# A SET is what the site's wardrobe saves: per socket a piece with its trim material and its
# fittings' values, per armor slot a base material, and a skin or a cloth over the lot. `--wear`
# builds ONE project holding the figure and every piece in the set, each at its anchor, each
# painted the way the game would paint it - so a set can be looked at before it is owned.
#
# Nothing here is a second renderer. The armor sheets come from bake_skin.py and preview_cloth.py,
# which are the ports of SkinBake and ClothTextureManager; each piece's sheet comes from
# preview_material.py, which is the port of DecorationTextureManager. This file only decides where
# things hang, which is the one thing it has always known.

SET_SLOTS = ("helmet", "chestplate", "leggings", "boots")


def pack_dirs(packs=None) -> list[Path]:
    """Where a worn piece's files are looked for: the given pack folders first, the mod's own
    resources last. A set of shipped pieces needs no arguments; an outfit that borrows from two
    packs names them both and still finds the mod's pieces underneath, which is what an outfit
    mixing the two looks like."""
    return [Path(p) for p in (packs or [])] + [ROOT / "src" / "main" / "resources"]


def _find(dirs: list[Path], relative: str) -> Path | None:
    for d in dirs:
        candidate = d / relative
        if candidate.exists():
            return candidate
    return None


def _split(piece_id: str) -> tuple[str, str]:
    namespace, _, name = str(piece_id).rpartition(":")
    return (namespace or "armorpieces"), name


def resolve_worn(piece_id: str, dirs: list[Path]) -> dict:
    """One worn piece's files: its geometry, its data (which says what socket it goes in and what
    fittings it has), its greyscale master and the sheets beside it."""
    namespace, name = _split(piece_id)
    geo_path = _find(dirs, f"assets/{namespace}/armorpieces/decoration/{name}.json")
    data_path = _find(dirs, f"data/{namespace}/armorpieces/armor_decoration/{name}.json")
    if geo_path is None:
        raise SystemExit(f"error: {piece_id}: no geometry at "
                         f"assets/{namespace}/armorpieces/decoration/{name}.json in {dirs[0]}")
    master = _find(dirs, f"assets/{namespace}/textures/entity/decoration/{name}.png")
    data = json.loads(data_path.read_text(encoding="utf-8")) if data_path else {}
    masks = {}
    for fitting in data.get("fittings", []) or []:
        _, fname = _split(fitting)
        found = _find(dirs, f"assets/{namespace}/textures/entity/decoration/{name}_{fname}.png")
        if found is not None:
            masks[fname] = found
    return {
        "id": piece_id, "namespace": namespace, "name": name,
        "geo": json.loads(geo_path.read_text(encoding="utf-8")),
        "master": master,
        "static": _find(dirs, f"assets/{namespace}/textures/entity/decoration/{name}_static.png"),
        "masks": masks,
        "anchors": [a for a in (data.get("anchors") or []) if isinstance(a, str)],
    }


def mirror_geo(bone: dict) -> dict:
    """One bone, mirrored across the X = 0 plane of its anchor.

    This is what `poseStack.scale(-1, 1, 1)` does to the second half of a mirrored pair, done to
    the geometry instead - because a Blockbench group has no negative scale, and half a pair of
    pauldrons in a wardrobe would be a worse lie than no pauldrons at all. A pivot's X flips; a
    cube spans from its far edge back; rotations about Y and Z flip and the one about X does not;
    and the box's own UV mirror flips, which is what a negative scale does to which texel lands on
    which side."""
    out = dict(bone)
    px, py, pz = bone.get("pivot", [0, 0, 0])
    out["pivot"] = [-px, py, pz]
    if bone.get("rotation"):
        rx, ry, rz = bone["rotation"]
        out["rotation"] = [rx, -ry, -rz]
    cubes = []
    for cube in bone.get("cubes", []) or []:
        ox, oy, oz = cube["origin"]
        sx, sy, sz = cube["size"]
        cubes.append(dict(cube, origin=[-(ox + sx), oy, oz], mirror=not cube.get("mirror", False)))
    if cubes:
        out["cubes"] = cubes
    if bone.get("children"):
        out["children"] = [mirror_geo(child) for child in bone["children"]]
    return out


def armor_material(value) -> str:
    """The sheet name for an armor slot's material. A set says what the item says - `golden`
    for a golden_helmet - and the game's armor sheet for it is `gold`; nothing else differs."""
    name = str(value or "iron").strip().lower().removeprefix("minecraft:")
    return "gold" if name == "golden" else name


def armor_sheets(spec: dict, slim: bool, out_dir: Path) -> tuple[dict, dict]:
    """The four slots' armor textures for a set, as ({key: path}, {slot: key}).

    Plain, a slot wears its material's own vanilla sheet. A SKIN replaces that sheet with the
    skin's master baked through the material's own eight shades (bake_skin.py). A CLOTH is
    composited on top of whatever the sheet is by then (preview_cloth.py), which is the order the
    game draws them in - the skin decides what the plate is, the cloth is laid over it."""
    import bake_skin
    import preview_cloth

    out_dir.mkdir(parents=True, exist_ok=True)
    slots = spec.get("slots") or {}
    skin_id = spec.get("skin")
    cloth = spec.get("cloth") or {}
    cloth_id = cloth.get("cloth") if isinstance(cloth, dict) else cloth

    paths: dict[str, Path] = {}
    slot_texture: dict[str, str] = {}
    for slot in SET_SLOTS:
        material = armor_material((slots.get(slot) or {}).get("material") or spec.get("material"))
        sheet = "humanoid_leggings" if slot == "leggings" else "humanoid"
        key = f"armor_{slot}"
        slot_texture[slot] = key
        target = out_dir / f"{key}.png"
        image = None
        if skin_id:
            _, skin_name = _split(skin_id)
            try:
                written = bake_skin.bake_skin(skin_name, material, out_dir / "baked")
                baked = next((p for p in written if p.stem == sheet), None)
                if baked is not None:
                    image = Image.open(baked).convert("RGBA")
            except (SystemExit, OSError, KeyError, ValueError) as err:
                print(f"note: {skin_id} on {material} did not bake ({err}); "
                      f"the plain material is worn", file=sys.stderr)
        # A cloth is the CHEST slot's component in the game, and it reaches both the chest sheet
        # and the leggings one, which is where the hem is. Nothing else wears it.
        if cloth_id and slot in ("chestplate", "leggings"):
            _, cloth_name = _split(cloth_id)
            try:
                worn = preview_cloth.bake(
                    cloth_name, material, str(cloth.get("base") or "white"),
                    [tuple(layer) for layer in (cloth.get("patterns") or [])],
                    sheet=str(cloth.get("sheet") or "shield"), armor_sheet=sheet,
                    armor_override=image)
                if worn is not None:
                    image = worn
            except (SystemExit, OSError, KeyError, ValueError) as err:
                print(f"note: {cloth_id} on {material} did not bake ({err}); "
                      f"nothing is worn over the armor", file=sys.stderr)
        if image is None:
            _, armor, leggings, desc = figure(material, slim)
            source = leggings if sheet == "humanoid_leggings" and leggings.is_file() else armor
            if desc["figure"] != "vanilla":
                # No game sheet for this material - the web bundle has none at all - so the
                # studio figure would wear iron whatever the set says. The studio figure is the
                # mod's own `plate` skin baked in iron; bake it in THIS material instead, through
                # the ramps tools/.webcache carries, and the armor keeps its colour.
                try:
                    written = bake_skin.bake_skin("plate", material, out_dir / "baked")
                    baked = next((p for p in written if p.stem == sheet), None)
                    if baked is not None:
                        source = baked
                except (SystemExit, OSError, KeyError, ValueError) as err:
                    print(f"note: plate on {material} did not bake ({err}); "
                          f"the studio figure's own sheet is worn", file=sys.stderr)
            if not source.is_file():
                # No sheet for this material at all: wear what the figure has.
                _, source, _l, _d = figure("iron", slim)
            paths[key] = source
            continue
        image.save(target)
        paths[key] = target
    return paths, slot_texture


def build_worn_rig(spec: dict, out_dir=RIG_DIR, slim=False, packs=None, animate=True):
    """The figure wearing a whole set: every piece at its anchor, painted, everything locked.

    Locked because this is a VIEWER, not a workspace. A wardrobe is for looking at a set from every
    side before owning it; the moment something in it can be dragged, the picture stops being what
    the game would draw. Returns (model, what is worn)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    dirs = pack_dirs(packs)
    anchors = parse_anchors()
    name = str(spec.get("name") or "set")
    label = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_").lower() or "set"

    # The figure, then the four slots' sheets - each a texture of its own, so four materials, a
    # skin and a cloth can all be seen at once.
    head_material = armor_material((spec.get("slots", {}).get("helmet") or {}).get("material")
                                   or spec.get("material"))
    skin_path, _armor, _leggings, description = figure(head_material, slim)
    sheets, slot_texture = armor_sheets(spec, slim, out_dir)

    textures, index = [], {}
    index["skin"] = 0
    textures.append(texture_entry("skin", skin_path, det_uuid(f"wear/{label}/texture/skin"),
                                  (64, 64), out_dir))
    for key, path in sheets.items():
        index[key] = len(textures)
        textures.append(texture_entry(key, path, det_uuid(f"wear/{label}/texture/{key}"),
                                      (64, 32), out_dir))
    # build_reference falls back to these two keys for anything not named per slot.
    index.setdefault("armor", index["armor_chestplate"])
    index.setdefault("armor_leggings", index["armor_leggings"])

    elements, groups, bone_uuids = build_reference(
        f"wear_{label}", slim, index, slot_texture=slot_texture)

    # One group per worn piece per attachment: exactly the frames ArmorDecorationLayer enters.
    parenting: dict[str, str] = {}
    worn_report = []
    for socket, entry in sorted((spec.get("pieces") or {}).items()):
        if not entry:
            continue
        piece_id = entry if isinstance(entry, str) else entry.get("id")
        if not piece_id:
            continue
        options = entry if isinstance(entry, dict) else {}
        if socket not in anchors:
            print(f"note: no socket called {socket}; {piece_id} is not worn", file=sys.stderr)
            continue
        piece = resolve_worn(piece_id, dirs)
        material = str(options.get("material") or "iron")
        # A set carries the game's own values, which are namespaced ids (`minecraft:emerald`);
        # preview_material speaks the bare vocabulary the command line does. A hex colour has no
        # namespace to drop.
        # The key is namespaced too (`armorpieces:gemstone`), and the masks resolve_worn found
        # are keyed by the bare name, which is how the file on disk is called.
        fittings = [(_split(str(k))[1], str(v) if str(v).startswith("#") else _split(str(v))[1])
                    for k, v in (options.get("fittings") or {}).items()]

        texture_key = None
        if piece["master"] is not None:
            painted = out_dir / f"{label}_{socket}.png"
            preview_material.preview(
                piece["name"], material, painted,
                master_override=piece["master"], static_override=piece["static"],
                fittings=fittings, mask_overrides=piece["masks"])
            with Image.open(painted) as image:
                uv = image.size
            texture_key = len(textures)
            index[f"piece_{socket}"] = texture_key
            textures.append(texture_entry(
                f"piece_{socket}", painted, det_uuid(f"wear/{label}/texture/{socket}"), uv, out_dir))

        for half, attachment in enumerate(anchors[socket]["attachments"]):
            pivot = mc_humanoid.BONES[attachment["part"]]
            anchor_geo = tuple(pivot[i] + attachment["offset"][i] for i in range(3))
            origin_bb = flip_point(list(anchor_geo))
            bones = piece["geo"].get("bones", [])
            if attachment.get("mirror"):
                bones = [mirror_geo(bone) for bone in bones]
            children = []
            for i, bone in enumerate(bones):
                children.append(bone_to_group(
                    bone, origin_bb, f"wear/{label}/{socket}/{half}/{bone.get('name', i)}",
                    elements, groups, texture_key))
            guid = det_uuid(f"wear/{label}/{socket}/{half}")
            groups.append(make_group(f"{socket}_{half}" if half else socket, guid, origin_bb,
                                     [0, 0, 0], children, locked=True, color=4))
            parenting[guid] = bone_uuids[attachment["part"]]
        worn_report.append({"socket": socket, "id": piece_id, "material": material,
                            "halves": len(anchors[socket]["attachments"])})

    animations = None
    if animate:
        animations = [
            build_animation(f"wear_{label}", "walk", mc_humanoid.WALK_AMPLITUDE, bone_uuids),
            build_animation(f"wear_{label}", "sprint", mc_humanoid.SPRINT_AMPLITUDE, bone_uuids),
        ]

    model = bb_assemble(f"wear_{label}", (64, 32), elements, groups, parenting=parenting,
                        textures=textures, animations=animations, model_format="free")
    model["armorpieces_figure"] = dict(description, worn=[w["id"] for w in worn_report])
    model["armorpieces_set"] = spec
    return model, worn_report


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

    # Which set the figure is wearing, for the editor to say. Blockbench ignores keys it does not
    # know, so this rides in the project file rather than in a second one beside it.
    model["armorpieces_figure"] = figure(material, slim)[3]
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
    ap.add_argument("--skin", type=Path,
                    help="build a SKIN rig instead: the figure wearing the master pair in this "
                         "folder (tools/skin_masters/<name>), armor unlocked and paintable")
    ap.add_argument("--wear", type=Path, metavar="SET.JSON",
                    help="build a WARDROBE rig instead: the figure wearing a whole set - a piece "
                         "in each socket with its material and its fittings, a base material per "
                         "armor slot, a skin and a cloth. Everything locked; it is for looking at")
    ap.add_argument("--pack", type=Path, action="append", metavar="DIR",
                    help="a pack folder a worn piece may come from, searched before the mod's own "
                         "src/main/resources; repeat for more")
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
        # The game's textures are extracted when a jar is here to extract them from; without one
        # the figure wears the studio set, which needs nothing. Either way the rig is built.
        jar = vanilla_assets.find_jar(vanilla_assets.minecraft_version())
        if jar is not None:
            print("no vanilla asset cache; extracting it first", file=sys.stderr)
            source = vanilla_assets.Source(jar)
            vanilla_assets.extract(source)
            vanilla_assets.bake(source)
            source.close()
        elif not (STUDIO / "skin.png").is_file():
            sys.exit(f"error: neither the game's textures ({ASSETS}) nor the studio figure "
                     f"({STUDIO}) is here. Run python tools/studio_figure.py, or "
                     f"python tools/vanilla_assets.py with a jar.")

    if args.wear:
        spec = json.loads(args.wear.read_text(encoding="utf-8"))
        args.out_dir.mkdir(parents=True, exist_ok=True)
        model, worn = build_worn_rig(spec, out_dir=args.out_dir, slim=args.slim,
                                     packs=args.pack, animate=not args.no_animation)
        label = model["name"]
        out = args.out_dir / f"{label}.bbmodel"
        out.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")
        for entry in worn:
            pair = " (a pair)" if entry["halves"] > 1 else ""
            print(f"{entry['socket']:10s} {entry['id']:32s} in {entry['material']}{pair}")
        print(f"{len(worn)} worn -> {out}")
        return

    if args.skin:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        model = build_skin_rig(args.skin, out_dir=args.out_dir, slim=args.slim,
                               animate=not args.no_animation)
        out = args.out_dir / f"skin_{args.skin.name}.bbmodel"
        out.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")
        print(f"skin {args.skin.name} -> {out}")
        return

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
