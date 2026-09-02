package com.mattjesmc.armorpieces.client.fitting;

import com.mattjesmc.armorpieces.decoration.fitting.builtin.BannerFitting;
import com.mojang.blaze3d.vertex.PoseStack;
import java.util.ArrayList;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.WeakHashMap;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.Sheets;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.resources.model.sprite.SpriteGetter;
import net.minecraft.client.resources.model.sprite.SpriteId;
import net.minecraft.core.Direction;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.block.entity.BannerPatternLayers;
import org.joml.Vector3fc;

/**
 * Draws a banner's design on a bone of a part, the way a shield wears one.
 *
 * <p>Vanilla draws a banner as passes: the base sprite in the base colour, then one pass per layer
 * with that pattern's sprite in that layer's colour, all over the same model. This does the same,
 * through the same {@code submitModelPart}-with-a-sprite call the shield renderer uses, with two
 * differences that are the whole reason it is not simply {@code BannerRenderer.submitPatterns}:
 *
 * <ul>
 *   <li><b>The geometry is the part's own bone</b>, not a flag. The bone is found by name in the
 *       part's full geometry and its cubes are read with the transforms of every bone above it, so
 *       a cloth on a rotated child bone draws where the part's pass would have drawn it.</li>
 *   <li><b>The UVs are remapped.</b> The pattern sprites are painted for one specific box - a 20x40x1
 *       flag, or a 12x22x1 shield plate - and a cloth of any other size sampling them by its own UV
 *       would show a corner of the design. So each face of each cube is stretched over the whole of
 *       the matching face of that box: the cloth's front gets the flag's front, edge to edge,
 *       whatever size the cloth is. The remapped cube is built once per bone cube and cached.</li>
 * </ul>
 *
 * <p>Which face is "front" is the fitting's business ({@link BannerFitting#front()}): a banner on
 * the back is read from behind, so its outward face is the one that should carry the design the
 * right way round. The faces are rotated so that face lands on the box's front, and the box's back
 * - which vanilla paints mirrored, as a real flag's back is - lands opposite.
 */
@Environment(EnvType.CLIENT)
public final class BannerFittingRenderer implements FittingRenderer {
    /** Both of vanilla's pattern sheets are 64x64. */
    private static final float SHEET = 64.0F;
    /** The flag every banner pattern is painted for: 20 wide, 40 tall, 1 deep, net at (0, 0). */
    private static final Box FLAG = new Box(20, 40, 1);
    /** The plate every shield pattern is painted for. */
    private static final Box PLATE = new Box(12, 22, 1);

    /**
     * Remapped cubes, by the baked cube they were made from and the mapping applied to it. There are
     * a handful of banner-bearing cubes in the world at once, so within one set of geometry nothing
     * here is ever worth evicting.
     *
     * <p>The cube is the WEAK key, because a resource reload rebuilds every part's geometry and the
     * cubes cached against the old one are then unreachable art. Held strongly they would accumulate
     * one generation per reload for the life of the client; held weakly an entry dies with the
     * geometry it was made from, which is the lifetime it was always meant to have. Sound because a
     * remapped part shares nothing that leads back to the cube: its vertices are new, and a normal is
     * a bare vector.
     */
    private final Map<ModelPart.Cube, Map<Remap, ModelPart>> remapped = new WeakHashMap<>();

    @Override
    public void submit(final Context context) {
        final BannerFitting fitting = (BannerFitting) context.fitting();
        final BannerFitting.Value value = (BannerFitting.Value) context.value();

        // Every cube of the named bone, with the pose it would be drawn at. The visit runs now, while
        // the pose stack is in the part's frame; the poses are copied because the stack's own are
        // reused as it unwinds.
        final boolean banner = fitting.sheet() == BannerFitting.Sheet.BANNER;
        final Box box = banner ? FLAG : PLATE;
        final Direction front = fitting.front();
        final List<Placed> cubes = new ArrayList<>();
        context.geometry().visit(context.poseStack(), (pose, path, index, cube) -> {
            if (isBone(path, fitting.bone())) {
                cubes.add(new Placed(pose.copy(), this.remap(cube, box, front)));
            }
        });
        if (cubes.isEmpty()) {
            return;
        }

        final SpriteGetter sprites = Minecraft.getInstance().getAtlasManager();
        submitLayer(context, cubes, sprites,
            banner ? Sheets.BANNER_PATTERN_BASE : Sheets.SHIELD_PATTERN_BASE, value.base(), 0);
        final BannerPatternLayers layers = value.layers();
        for (int i = 0; i < layers.layers().size(); i++) {
            final BannerPatternLayers.Layer layer = layers.layers().get(i);
            submitLayer(context, cubes, sprites,
                banner ? Sheets.getBannerSprite(layer.pattern()) : Sheets.getShieldSprite(layer.pattern()),
                layer.color(), i + 1);
        }
    }

    /**
     * One pass: every cloth cube in one sprite and one colour. Layers are coplanar, so they are
     * ordered rather than left to the depth test - the same {@code order()} vanilla's own banner
     * passes use.
     */
    private static void submitLayer(
        final Context context,
        final List<Placed> cubes,
        final SpriteGetter sprites,
        final SpriteId spriteId,
        final DyeColor colour,
        final int order
    ) {
        final TextureAtlasSprite sprite = sprites.get(spriteId);
        final RenderType renderType = spriteId.renderType(RenderTypes::bannerPattern);
        final int argb = colour.getTextureDiffuseColor();
        final PoseStack poseStack = context.poseStack();
        for (final Placed placed : cubes) {
            poseStack.pushPose();
            poseStack.last().set(placed.pose());
            context.collector().order(order).submitModelPart(
                placed.part(), poseStack, renderType, context.lightCoords(), context.overlayCoords(),
                sprite, argb, null, context.outlineColor());
            poseStack.popPose();
        }
    }

    /** The cube as a one-cube part whose faces sample the box's faces, built once and cached. */
    private ModelPart remap(final ModelPart.Cube cube, final Box box, final Direction front) {
        return this.remapped
            .computeIfAbsent(cube, c -> new HashMap<>())
            .computeIfAbsent(new Remap(box, front), key -> {
                // A fresh cube of the same extents, every face present, whose polygons are then replaced
                // one for one with the original's - same corners, same normal, new UVs. The constructor's
                // own UVs are irrelevant; it exists to give ModelPart something with the right bounds.
                final ModelPart.Cube copy = new ModelPart.Cube(
                    0, 0, cube.minX, cube.minY, cube.minZ,
                    cube.maxX - cube.minX, cube.maxY - cube.minY, cube.maxZ - cube.minZ,
                    0.0F, 0.0F, 0.0F, false, SHEET, SHEET, EnumSet.allOf(Direction.class));
                final int count = Math.min(copy.polygons.length, cube.polygons.length);
                for (int i = 0; i < count; i++) {
                    final ModelPart.Polygon polygon = cube.polygons[i];
                    copy.polygons[i] = new ModelPart.Polygon(
                        remapVertices(polygon, box.face(rotate(facing(polygon.normal()), front))),
                        polygon.normal());
                }
                return new ModelPart(List.of(copy), Map.of());
            });
    }

    /**
     * One face's vertices, their UVs stretched over {@code rect} - the matching face of the box the
     * sprite was painted for.
     *
     * <p>Normalising each vertex within the polygon's own UV extent and then placing it in the target
     * rect keeps the vertex-to-corner assignment vanilla's box net gave it, which is what makes an
     * up face still read as an up face and a mirrored cube still mirror. Only the extent changes.
     */
    private static ModelPart.Vertex[] remapVertices(final ModelPart.Polygon polygon, final float[] rect) {
        final ModelPart.Vertex[] vertices = polygon.vertices();
        float minU = Float.MAX_VALUE;
        float maxU = -Float.MAX_VALUE;
        float minV = Float.MAX_VALUE;
        float maxV = -Float.MAX_VALUE;
        for (final ModelPart.Vertex vertex : vertices) {
            minU = Math.min(minU, vertex.u());
            maxU = Math.max(maxU, vertex.u());
            minV = Math.min(minV, vertex.v());
            maxV = Math.max(maxV, vertex.v());
        }
        final float spanU = Math.max(maxU - minU, 1.0E-6F);
        final float spanV = Math.max(maxV - minV, 1.0E-6F);
        final ModelPart.Vertex[] out = new ModelPart.Vertex[vertices.length];
        for (int i = 0; i < vertices.length; i++) {
            final ModelPart.Vertex vertex = vertices[i];
            out[i] = vertex.remap(
                rect[0] + (vertex.u() - minU) / spanU * (rect[2] - rect[0]),
                rect[1] + (vertex.v() - minV) / spanV * (rect[3] - rect[1]));
        }
        return out;
    }

    /** The box-net face a polygon is, from its normal - the same convention the net was built with. */
    private static Direction facing(final Vector3fc normal) {
        final float ax = Math.abs(normal.x());
        final float ay = Math.abs(normal.y());
        final float az = Math.abs(normal.z());
        if (ax >= ay && ax >= az) {
            return normal.x() < 0 ? Direction.WEST : Direction.EAST;
        }
        if (ay >= az) {
            return normal.y() < 0 ? Direction.DOWN : Direction.UP;
        }
        return normal.z() < 0 ? Direction.NORTH : Direction.SOUTH;
    }

    /**
     * Turns the cloth so that its {@code front} face lands on the box's north face, which is the one
     * the design is painted for. Vertical faces are unaffected; the four sides rotate together so the
     * net stays a net.
     */
    private static Direction rotate(final Direction face, final Direction front) {
        if (face.getAxis().isVertical() || front.getAxis().isVertical() || front == Direction.NORTH) {
            return face;
        }
        Direction from = front;
        Direction result = face;
        while (from != Direction.NORTH) {
            from = from.getClockWise();
            result = result.getClockWise();
        }
        return result;
    }

    /** Whether a visit path names the bone: {@code visit} builds paths as {@code /parent/child}. */
    private static boolean isBone(final String path, final String bone) {
        return path.equals(bone) || path.endsWith("/" + bone);
    }

    private record Placed(PoseStack.Pose pose, ModelPart part) {}

    /** Inner cache key: the mapping. The cube it applies to is the outer key, matched by identity. */
    private record Remap(Box box, Direction front) {}

    /**
     * The face rectangles of one box's UV net at (0, 0), as fractions of the 64x64 sheet: the same
     * layout {@code CubeListBuilder.addBox} produces, so a face here is where vanilla's own model
     * samples that face of that pattern.
     */
    private record Box(int w, int h, int d) {
        float[] face(final Direction direction) {
            final int u1 = this.d;
            final int u2 = this.d + this.w;
            final int u3 = this.d + this.w + this.d;
            final int u4 = this.d + this.w + this.d + this.w;
            final int v1 = this.d;
            final int v2 = this.d + this.h;
            return switch (direction) {
                case DOWN -> rect(u1, 0, u2, v1);
                case UP -> rect(u2, 0, u3, v1);
                case WEST -> rect(0, v1, u1, v2);
                case NORTH -> rect(u1, v1, u2, v2);
                case EAST -> rect(u2, v1, u3, v2);
                case SOUTH -> rect(u3, v1, u4, v2);
            };
        }

        private static float[] rect(final int u0, final int v0, final int u1, final int v1) {
            return new float[] {u0 / SHEET, v0 / SHEET, u1 / SHEET, v1 / SHEET};
        }
    }
}
