"""
The vanilla player, its armor, and its walk cycle - transcribed from the 26.2 sources, not recalled.

`bb_rig.py` used to hardcode six cubes lifted from `HumanoidModel.createMesh`. That is the base
humanoid, which is not what a player looks like and not what armor is shaped like, so a piece fitted
against it was being judged against the wrong silhouette. This module carries the real thing.

Every number below was read out of Loom's decompiled 26.2 sources. The four files that matter:

    net.minecraft.client.model.HumanoidModel          createMesh, createBaseArmorMesh,
                                                      createArmorMeshSet, ADULT_ARMOR_PARTS_PER_SLOT
    net.minecraft.client.model.player.PlayerModel     createMesh(scale, slim), createArmorMeshSet
    net.minecraft.client.model.geom.LayerDefinitions  OUTER/INNER_ARMOR_DEFORMATION
    net.minecraft.client.animation.AnimationUtils     bobModelPart

Three things the old table got wrong, all of them the kind of tenth-of-a-unit that decides whether a
spur clips a boot:

  * Boots are not the leg at the outer deformation. `createBaseArmorMesh` re-adds both legs at
    `g.extend(-0.1F)`, so boots are 0.9 and leggings' legs are 0.4, not 1.0 and 0.5.
  * A helmet is not one box. The HEAD slot uses `retainPartsAndChildren`, which keeps `head`'s child
    `hat`, and `hat` is `g.extend(0.5F)` - so a helmet is a 1.0 shell with a 1.5 shell over it.
  * The player is not the humanoid. Five overlay layers (hat, jacket, two sleeves, two pants) sit
    0.25 proud of the base body, and the player's own left arm and left leg use different UV regions
    than the humanoid's mirrored ones.

And one thing worth knowing before fitting a vambrace: armor geometry is always the WIDE arm.
`PlayerModel.createArmorMeshSet` only adds empty placeholder children to the humanoid armor mesh -
`CubeListBuilder.create()` with no boxes - so a slim player still wears 4-wide armor sleeves.

Coordinates are Minecraft entity-model space: +Y points DOWN from the neck, units are 1/16 block.
`bb_geo.flip_point` converts to Blockbench space. Nothing here knows about Blockbench.
"""

from __future__ import annotations

import math

# ---- deformations ------------------------------------------------------------------------------

# LayerDefinitions: OUTER_ARMOR_DEFORMATION = 1.0F, INNER_ARMOR_DEFORMATION = 0.5F.
OUTER, INNER = 1.0, 0.5

# createBaseArmorMesh re-adds both legs at g.extend(-0.1F), for every slot that keeps a leg.
LEG_TRIM = -0.1

# HumanoidModel.createMesh: hat is g.extend(0.5F). PlayerModel.createMesh: overlayScale = 0.25F.
HAT_EXTEND, OVERLAY = 0.5, 0.25


# ---- the bone tree -----------------------------------------------------------------------------

# name -> pivot, in entity space. These six are the parts HumanoidModel.setupAnim actually poses, so
# they are exactly the groups a Blockbench rig needs if the armor is to move with the limb.
BONES = {
    "head":      (0.0, 0.0, 0.0),
    "body":      (0.0, 0.0, 0.0),
    "right_arm": (-5.0, 2.0, 0.0),
    "left_arm":  (5.0, 2.0, 0.0),
    "right_leg": (-1.9, 12.0, 0.0),
    "left_leg":  (1.9, 12.0, 0.0),
}


def _box(bone, name, origin, size, tex, inflate=0.0, mirror=False):
    return {"bone": bone, "name": name, "origin": origin, "size": size,
            "tex": tex, "inflate": inflate, "mirror": mirror}


def player_boxes(slim: bool = False) -> list[dict]:
    """The player's own body: HumanoidModel.createMesh overridden by PlayerModel.createMesh.

    The overlays are children of their base part at PartPose.ZERO, which means they share the bone's
    pivot exactly - so they are emitted into the same bone here rather than as nested groups. Same
    transform, one less level of outliner to scroll past."""
    arm_w = 3.0 if slim else 4.0
    # PlayerModel.createMesh: the slim branch moves the right arm's box in by one, and leaves the
    # left arm's box where it is. Both branches keep the pivots the humanoid gave them.
    right_arm_x = -2.0 if slim else -3.0

    return [
        # HumanoidModel.createMesh - head and its hat.
        _box("head", "head", (-4.0, -8.0, -4.0), (8.0, 8.0, 8.0), (0, 0)),
        _box("head", "hat", (-4.0, -8.0, -4.0), (8.0, 8.0, 8.0), (32, 0), HAT_EXTEND),

        # HumanoidModel.createMesh - body; PlayerModel adds the jacket over it.
        _box("body", "body", (-4.0, 0.0, -2.0), (8.0, 12.0, 4.0), (16, 16)),
        _box("body", "jacket", (-4.0, 0.0, -2.0), (8.0, 12.0, 4.0), (16, 32), OVERLAY),

        # Arms. The right arm is the humanoid's; PlayerModel replaces the left with its own UVs.
        _box("right_arm", "right_arm", (right_arm_x, -2.0, -2.0), (arm_w, 12.0, 4.0), (40, 16)),
        _box("right_arm", "right_sleeve", (right_arm_x, -2.0, -2.0), (arm_w, 12.0, 4.0), (40, 32),
             OVERLAY),
        _box("left_arm", "left_arm", (-1.0, -2.0, -2.0), (arm_w, 12.0, 4.0), (32, 48)),
        _box("left_arm", "left_sleeve", (-1.0, -2.0, -2.0), (arm_w, 12.0, 4.0), (48, 48), OVERLAY),

        # Legs. Same story: the right is the humanoid's, the left is PlayerModel's own.
        _box("right_leg", "right_leg", (-2.0, 0.0, -2.0), (4.0, 12.0, 4.0), (0, 16)),
        _box("right_leg", "right_pants", (-2.0, 0.0, -2.0), (4.0, 12.0, 4.0), (0, 32), OVERLAY),
        _box("left_leg", "left_leg", (-2.0, 0.0, -2.0), (4.0, 12.0, 4.0), (16, 48)),
        _box("left_leg", "left_pants", (-2.0, 0.0, -2.0), (4.0, 12.0, 4.0), (0, 48), OVERLAY),
    ]


# ADULT_ARMOR_PARTS_PER_SLOT, verbatim. HEAD uses retainPartsAndChildren (so `hat` survives);
# the other three use retainExactParts (so no children survive, which is why a chestplate has no
# jacket shell over it).
ARMOR_SLOTS = {
    "helmet":     {"parts": ("head",), "deformation": OUTER, "keep_children": True,
                   "texture": "armor"},
    "chestplate": {"parts": ("body", "left_arm", "right_arm"), "deformation": OUTER,
                   "keep_children": False, "texture": "armor"},
    "leggings":   {"parts": ("left_leg", "right_leg", "body"), "deformation": INNER,
                   "keep_children": False, "texture": "armor_leggings"},
    "boots":      {"parts": ("left_leg", "right_leg"), "deformation": OUTER,
                   "keep_children": False, "texture": "armor"},
}


def armor_boxes(slot: str) -> list[dict]:
    """One armor slot's geometry: createBaseArmorMesh(deformation), reduced to that slot's parts.

    Armor is built from the HUMANOID mesh, never the player one - so the arms are the humanoid's
    mirrored 4-wide pair and the legs are the humanoid's, regardless of the body underneath."""
    spec = ARMOR_SLOTS[slot]
    g = spec["deformation"]
    leg = g + LEG_TRIM  # createBaseArmorMesh's re-added legs
    out = []

    for part in spec["parts"]:
        if part == "head":
            out.append(_box("head", f"head_{slot}", (-4.0, -8.0, -4.0), (8.0, 8.0, 8.0), (0, 0), g))
            if spec["keep_children"]:
                out.append(_box("head", f"hat_{slot}", (-4.0, -8.0, -4.0), (8.0, 8.0, 8.0),
                                (32, 0), g + HAT_EXTEND))
        elif part == "body":
            out.append(_box("body", f"body_{slot}", (-4.0, 0.0, -2.0), (8.0, 12.0, 4.0), (16, 16), g))
        elif part == "right_arm":
            out.append(_box("right_arm", f"right_arm_{slot}", (-3.0, -2.0, -2.0), (4.0, 12.0, 4.0),
                            (40, 16), g))
        elif part == "left_arm":
            out.append(_box("left_arm", f"left_arm_{slot}", (-1.0, -2.0, -2.0), (4.0, 12.0, 4.0),
                            (40, 16), g, mirror=True))
        elif part == "right_leg":
            out.append(_box("right_leg", f"right_leg_{slot}", (-2.0, 0.0, -2.0), (4.0, 12.0, 4.0),
                            (0, 16), leg))
        elif part == "left_leg":
            out.append(_box("left_leg", f"left_leg_{slot}", (-2.0, 0.0, -2.0), (4.0, 12.0, 4.0),
                            (0, 16), leg, mirror=True))
    return out


# ---- the walk cycle ----------------------------------------------------------------------------

# HumanoidModel.setupAnim, the four lines that swing the limbs:
#
#     rightArm.xRot = cos(pos * 0.6662 + PI) * 2.0 * speed * 0.5 / speedValue
#     leftArm.xRot  = cos(pos * 0.6662)      * 2.0 * speed * 0.5 / speedValue
#     rightLeg.xRot = cos(pos * 0.6662)      * 1.4 * speed / speedValue
#     leftLeg.xRot  = cos(pos * 0.6662 + PI) * 1.4 * speed / speedValue
#
# speedValue is 1.0 for anything that does not override it, players included, so it drops out.
SWING = 0.6662

# The constant yaw/roll splay setupAnim gives the legs unconditionally. Tiny, but it is the reason
# the legs are not perfectly coplanar, and a greave sitting flush against one will show it.
LEG_SPLAY_Y, LEG_SPLAY_Z = 0.005, 0.005

# WalkAnimationState: position += speed each tick, so one full cycle is 2*pi/SWING ticks of position.
CYCLE_POSITION = 2.0 * math.pi / SWING  # 9.4315...

# LivingEntity.updateWalkAnimation: targetSpeed = min(distance * 4.0, 1.0), where distance is blocks
# travelled this tick. Sprinting saturates that clamp, so SPRINT's amplitude of 1.0 is read straight
# off the source. WALK's is the one number here that is NOT read: it is min(0.2158 * 4, 1.0) for a
# player's ~0.2158 blocks/tick ground speed. Tune it with --walk-amplitude if it reads wrong.
WALK_AMPLITUDE, SPRINT_AMPLITUDE = 0.863, 1.0

# AnimationUtils.bobModelPart, applied to both arms every frame with scale +1 and -1:
#     zRot += scale * (cos(age * 0.09) * 0.05 + 0.05)
#     xRot += scale * (sin(age * 0.067) * 0.05)
BOB_Z_RATE, BOB_X_RATE, BOB_AMPLITUDE = 0.09, 0.067, 0.05


def limb_pose(position: float, amplitude: float, age: float) -> dict[str, tuple[float, float, float]]:
    """Every posed bone's Euler rotation in radians, for one instant of the cycle.

    `position` is WalkAnimationState.position, `amplitude` is its speed, `age` is ageInTicks. The
    return is keyed by bone name and ordered (x, y, z), matching ModelPart's xRot/yRot/zRot."""
    phase = position * SWING
    arm_swing = 2.0 * amplitude * 0.5
    leg_swing = 1.4 * amplitude

    right_arm_x = math.cos(phase + math.pi) * arm_swing
    left_arm_x = math.cos(phase) * arm_swing

    # The arm bob is added on top of the swing, once per arm, with opposite scale.
    bob_z = math.cos(age * BOB_Z_RATE) * BOB_AMPLITUDE + BOB_AMPLITUDE
    bob_x = math.sin(age * BOB_X_RATE) * BOB_AMPLITUDE

    return {
        "head": (0.0, 0.0, 0.0),
        "body": (0.0, 0.0, 0.0),
        "right_arm": (right_arm_x + bob_x, 0.0, bob_z),
        "left_arm": (left_arm_x - bob_x, 0.0, -bob_z),
        "right_leg": (math.cos(phase) * leg_swing, LEG_SPLAY_Y, LEG_SPLAY_Z),
        "left_leg": (math.cos(phase + math.pi) * leg_swing, -LEG_SPLAY_Y, -LEG_SPLAY_Z),
    }


def cycle_ticks(amplitude: float) -> float:
    """How many ticks one full swing takes at this amplitude, since position advances by speed."""
    return CYCLE_POSITION / amplitude
