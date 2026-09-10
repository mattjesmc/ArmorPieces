package com.mattjesmc.armorpieces.client.geometry;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.mattjesmc.armorpieces.GameBootstrap;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.JsonOps;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import net.minecraft.client.model.geom.ModelPart;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * The shape a part is drawn as: {@link DecorationGeometry} the file, and {@link
 * DecorationGeometry#bake} the walk from it into vanilla's own model builders.
 *
 * <p>This format is the whole of "a pack can add a piece without writing Java". Everything else a
 * part has - its registry file, its master sheet, its fittings - is already asked a question
 * somewhere in this suite; the geometry was only ever asked whether it PARSES ({@code PartAssetsTest}
 * bakes all 66 of them and asserts nothing about what came out). What a part looks like on a body was
 * therefore held by nothing but a person looking at a frame, and a frame is tier 3 - minutes, a
 * client, and a golden that says "different" rather than "wrong".
 *
 * <p>The rules below are each one promise the format makes to an author, and each has a way of being
 * quietly wrong - quietly, because a bake that is off by half a texel still bakes, still renders, and
 * looks like the author's own mistake:
 *
 * <ul>
 *   <li><b>A bone is a place, and a child rides on its parent.</b> The hierarchy is what will carry
 *       animation later; today it is what lets a plume's tip be authored relative to its base.</li>
 *   <li><b>Rotations are degrees in the file and radians in the model.</b> Every modelling tool
 *       writes degrees; {@link net.minecraft.client.model.geom.PartPose} wants radians, and a missing
 *       conversion is a part lying flat on a head at what looks like a plausible angle.</li>
 *   <li><b>A box is drawn at its true size and unwrapped on WHOLE texels.</b> This is the one piece
 *       of arithmetic in the class that is not vanilla's, and the reason it exists is in
 *       {@code Cube.addTo}: vanilla maps a box's UV from its float size, so a 2.1-wide face samples
 *       2.1 texels and shares its edge column with the face beside it. The unwrap is rounded up and
 *       the box shrunk back by the difference, so the picture is the net every authoring tool paints
 *       and the model is the size the author asked for. Both halves are asserted separately here,
 *       because either alone passes half the tests.</li>
 *   <li><b>{@code inflate} grows the box and leaves the UV alone</b> - it is a fitting allowance, not
 *       a bigger box to paint.</li>
 *   <li><b>A cube's {@code mirror} belongs to that cube.</b> {@code CubeListBuilder.mirror()} is
 *       sticky - no {@code addBox} overload clears it - so the flag is stated for every box rather
 *       than only for the box that wants it, which is what stops it running down the rest of the
 *       bone.</li>
 *   <li><b>{@code without} takes a bone and everything under it out of the bake.</b> That is how a
 *       filled fitting draws a bone itself - the banner takes over the cloth - and it has to be a
 *       BAKE rather than a {@code visible} flag, which deferred rendering would read back long after
 *       it was reset.</li>
 * </ul>
 *
 * <p>Nothing here needs GL. Baking a model is arithmetic over floats, and a baked {@link ModelPart}
 * can be read back through {@link ModelPart#visit}, which hands out every cube with the transform it
 * would be drawn under - which is how the tests below measure a box: by its VERTICES, not by its
 * {@code minX..maxZ} fields. Those fields are the box vanilla was given before the deformation is
 * applied, so for a fractional box they read 3 wide where the drawn box is 2.1.
 */
class DecorationGeometryTest {

    /**
     * Nothing here is a registry, but everything here is a class beside one.
     *
     * <p>Fabric's loot API mixes into {@code SimpleJsonResourceReloadListener.scanDirectory}, so a
     * reload initialises {@code LootDataType} - and an un-bootstrapped game fails that initialiser
     * once and then answers every later question with a {@code NoClassDefFoundError} naming whatever
     * innocent class asked next. One line, and it is the difference between this suite and 25 failures
     * that name the wrong thing.
     */
    @BeforeAll
    static void game() {
        GameBootstrap.once();
    }

    // ---- the file ----------------------------------------------------------------------------------

    @Test
    void everyBoneInTheFileIsAChildOfTheRoot() {
        final ModelPart root = bake("""
            {"bones": [{"name": "left"}, {"name": "right"}]}
            """);
        assertTrue(root.hasChild("left"), "the first bone");
        assertTrue(root.hasChild("right"), "the second bone");
        assertFalse(root.hasChild("neither"), "a bone the file does not have");
    }

    @Test
    void aChildBoneHangsUnderItsParentAndCarriesItsPlace() {
        final ModelPart root = bake("""
            {"bones": [{"name": "parent", "pivot": [1, 2, 3],
                        "cubes": [{"origin": [0, 0, 0], "size": [1, 1, 1]}],
                        "children": [{"name": "child", "pivot": [4, 0, 0],
                                      "cubes": [{"origin": [0, 0, 0], "size": [1, 1, 1]}]}]}]}
            """);
        assertTrue(root.getChild("parent").hasChild("child"), "the child is under the parent");
        assertFalse(root.hasChild("child"), "and not under the root as well");

        // Model space is 1/16 of a block, so a pivot of 1 is 0.0625 once the tree is walked. The
        // child's own 4 is on top of its parent's 1: 5/16. That sum is the whole point of a hierarchy.
        final Map<String, float[]> places = places(root);
        assertEquals(1.0F / 16.0F, places.get("/parent")[0], 1.0E-5F, "the parent's own place");
        assertEquals(5.0F / 16.0F, places.get("/parent/child")[0], 1.0E-5F,
            "the child's place is its parent's plus its own");
    }

    @Test
    void aPivotIsWhereTheBoneSitsAndARotationIsDegrees() {
        final ModelPart bone = bake("""
            {"bones": [{"name": "a", "pivot": [1, -2, 3], "rotation": [0, 90, -45]}]}
            """).getChild("a");
        assertEquals(1.0F, bone.x, "pivot x, in model units and not divided by anything");
        assertEquals(-2.0F, bone.y, "pivot y - and +Y is DOWN in this space");
        assertEquals(3.0F, bone.z, "pivot z");
        // Degrees are what every modelling tool writes and radians are what PartPose wants. A part
        // whose rotation was passed through unconverted stands at 90 radians, which is some angle.
        assertEquals(0.0F, bone.xRot, 1.0E-6F, "no rotation asked for");
        assertEquals((float) Math.PI / 2.0F, bone.yRot, 1.0E-6F, "90 degrees is a quarter turn");
        assertEquals((float) -Math.PI / 4.0F, bone.zRot, 1.0E-6F, "and a negative one turns back");
    }

    @Test
    void whatAnAuthorLeavesOutHasADefault() {
        final DecorationGeometry geometry = parse("""
            {"bones": [{"name": "a", "cubes": [{"origin": [0, 0, 0], "size": [1, 1, 1]}]}]}
            """);
        assertEquals(32, geometry.textureWidth(), "an omitted sheet is 32 wide");
        assertEquals(32, geometry.textureHeight(), "and 32 tall");

        final DecorationGeometry.Bone bone = geometry.bones().getFirst();
        assertEquals(DecorationGeometry.Vec3f.ZERO, bone.pivot(), "a bone with no pivot sits at the origin");
        assertEquals(DecorationGeometry.Vec3f.ZERO, bone.rotation(), "and is not turned");
        assertFalse(bone.mirror(), "and is not mirrored");
        assertEquals(List.of(), bone.children(), "and has no children");

        final DecorationGeometry.Cube cube = bone.cubes().getFirst();
        assertEquals(0, cube.u(), "a box with no uv is painted from the corner of the sheet");
        assertEquals(0, cube.v(), "on both axes");
        assertEquals(0.0F, cube.inflate(), "and is not inflated");
        assertFalse(cube.mirror(), "and is not mirrored");
    }

    @Test
    void aFileThatCouldNotBeDrawnIsRefusedRatherThanBaked() {
        assertRefused("""
            {"bones": []}
            """, "a geometry with no bones - a part that would draw nothing at all");
        assertRefused("""
            {"bones": [{"name": "a", "cubes": [{"origin": [0, 0, 0], "size": [1, 1, 1], "uv": [1, 2, 3]}]}]}
            """, "a uv that is not exactly two numbers");
        assertRefused("""
            {"bones": [{"name": "a", "cubes": [{"origin": [0, 0], "size": [1, 1, 1]}]}]}
            """, "a coordinate that is not exactly three numbers");
        assertRefused("""
            {"texture_width": 0, "bones": [{"name": "a"}]}
            """, "a sheet with no width, which every uv would divide by");
        assertRefused("""
            {"bones": [{"cubes": []}]}
            """, "a bone with no name - nothing could ask for it, and no fitting could replace it");
        assertRefused("""
            {"bones": [{"name": "a", "cubes": [{"size": [1, 1, 1]}]}]}
            """, "a box with no origin: unlike uv and inflate, a place is not guessable");
    }

    @Test
    void theFileSurvivesItsOwnCodecBothWays() {
        final String json = """
            {"texture_width": 64, "texture_height": 16,
             "bones": [{"name": "base", "pivot": [0, -1, 2], "rotation": [10, 20, 30], "mirror": true,
                        "cubes": [{"origin": [-1, -2, -3], "size": [2, 3.5, 4], "uv": [8, 9],
                                   "inflate": 0.25, "mirror": true}],
                        "children": [{"name": "tip", "pivot": [0, -4, 0],
                                      "cubes": [{"origin": [0, 0, 0], "size": [1, 1, 1]}]}]}]}
            """;
        final DecorationGeometry geometry = parse(json);
        final JsonElement written = DecorationGeometry.CODEC
            .encodeStart(JsonOps.INSTANCE, geometry)
            .getOrThrow(message -> new AssertionError("could not be written back: " + message));
        assertEquals(geometry, parse(written.toString()),
            "a geometry written back and read again is the same geometry");
    }

    // ---- the bake ----------------------------------------------------------------------------------

    @Test
    void aBoxSitsWhereItsOriginSaysAndIsAsBigAsItsSize() {
        final Box box = onlyBox("""
            {"bones": [{"name": "a", "cubes": [{"origin": [-3, 1, 2], "size": [2, 3, 4]}]}]}
            """);
        assertEquals(-3.0F, box.minX, 1.0E-4F, "left face");
        assertEquals(-1.0F, box.maxX, 1.0E-4F, "and two units to the right of it");
        assertEquals(1.0F, box.minY, 1.0E-4F, "top face - +Y is down");
        assertEquals(4.0F, box.maxY, 1.0E-4F, "three units below");
        assertEquals(2.0F, box.minZ, 1.0E-4F, "front face");
        assertEquals(6.0F, box.maxZ, 1.0E-4F, "four units behind");
    }

    @Test
    void aBoxOfFractionalSizeIsDrawnAtItsTrueSize() {
        // The half of the unwrap that a naive "round the box up" would fail: a 2.1-wide horn would
        // come out 3 wide, which is a part that no longer touches the body it was fitted to.
        final Box box = onlyBox("""
            {"bones": [{"name": "a", "cubes": [{"origin": [3, 0, 0], "size": [2.1, 1, 0.5]}]}]}
            """);
        assertEquals(3.0F, box.minX, 1.0E-4F, "the box starts where the author put it");
        assertEquals(5.1F, box.maxX, 1.0E-4F, "and is exactly as wide as asked, not rounded up");
        assertEquals(0.0F, box.minZ, 1.0E-4F, "and the same on an axis rounded up by a half");
        assertEquals(0.5F, box.maxZ, 1.0E-4F, "half a texel deep, drawn half a texel deep");
    }

    @Test
    void aBoxOfFractionalSizeIsUnwrappedOnWholeTexels() {
        // The other half. Vanilla maps UV off the float size, so without the rounding this box's
        // faces would end mid-texel and sample the column belonging to the face beside them - the
        // seam that reads as a smear along one edge of a part and nothing else.
        final Box box = onlyBox("""
            {"bones": [{"name": "a", "cubes": [{"origin": [3, 0, 0], "size": [2.1, 1, 0.5], "uv": [4, 5]}]}]}
            """);
        box.everyVertexIsOnAWholeTexel(32, 32);
        // Rounded up: 3 wide, 1 tall, 1 deep. The net vanilla lays out is 2*(depth + width) across
        // and depth + height down, from the author's own corner.
        assertEquals(4, box.minU, "the net starts at the uv the author wrote");
        assertEquals(4 + 2 * (1 + 3), box.maxU, "and is as wide as the ROUNDED box");
        assertEquals(5, box.minV, "the same on the other axis");
        assertEquals(5 + 1 + 1, box.maxV, "depth plus height, both rounded");
    }

    @Test
    void inflateGrowsTheBoxAndLeavesTheUvAlone() {
        final Box plain = onlyBox("""
            {"bones": [{"name": "a", "cubes": [{"origin": [0, 0, 0], "size": [2, 1, 1], "uv": [0, 0]}]}]}
            """);
        final Box grown = onlyBox("""
            {"bones": [{"name": "a", "cubes": [{"origin": [0, 0, 0], "size": [2, 1, 1], "uv": [0, 0],
                                                "inflate": 0.25}]}]}
            """);
        assertEquals(-0.25F, grown.minX, 1.0E-4F, "inflate grows the box on every side");
        assertEquals(2.25F, grown.maxX, 1.0E-4F, "including the far one");
        assertEquals(-0.25F, grown.minY, 1.0E-4F, "on every axis");
        assertEquals(1.25F, grown.maxY, 1.0E-4F, "and both ways along it");
        // A fitting allowance, not a bigger box to paint: an inflated cube samples the same net, and
        // a bake that grew the UV with the box would hand the author a picture they cannot paint.
        assertEquals(plain.minU, grown.minU, "and the picture does not move");
        assertEquals(plain.maxU, grown.maxU, "or grow with it");
        assertEquals(plain.minV, grown.minV, "on either axis");
        assertEquals(plain.maxV, grown.maxV, "or either edge");
    }

    @Test
    void theSheetTheFileDeclaresIsTheOneTheUvIsMeasuredAgainst() {
        final String cube = """
            {"texture_width": %d, "texture_height": %d,
             "bones": [{"name": "a", "cubes": [{"origin": [0, 0, 0], "size": [2, 2, 2], "uv": [4, 4]}]}]}
            """;
        final Box small = onlyBox(cube.formatted(32, 32));
        final Box large = onlyBox(cube.formatted(64, 64));
        small.everyVertexIsOnAWholeTexel(32, 32);
        large.everyVertexIsOnAWholeTexel(64, 64);
        // The same box on a sheet twice the size covers the same TEXELS and half the picture. A bake
        // that ignored the declared size would put a 64-wide part's faces at double their coordinates.
        assertEquals(small.minU, large.minU, "the same texel column, whatever the sheet");
        assertEquals(small.maxU, large.maxU, "at both edges");
        assertEquals(small.rawMaxU / 2.0F, large.rawMaxU, 1.0E-5F,
            "which is half as far along a sheet twice as wide");
    }

    @Test
    void aCubesMirrorIsClearedForTheCubeAfterIt() {
        // CubeListBuilder.mirror() is sticky: no addBox overload clears it. What keeps a flag from
        // running down the rest of the bone is that EVERY cube states the one it wants on the way in
        // - the clear afterwards is belt and braces, and removing it alone changes no bake. Write the
        // natural version instead (turn it on for the box that asked, leave it) and this fails: the
        // symptom is a neighbouring box painted back to front, which reads as a texture mistake.
        final List<String> mirroredFirst = fingerprint(bake("""
            {"bones": [{"name": "a", "cubes": [
                {"origin": [0, 0, 0], "size": [2, 2, 2], "uv": [0, 0], "mirror": true},
                {"origin": [4, 0, 0], "size": [2, 2, 2], "uv": [0, 0]}]}]}
            """));
        final List<String> neither = fingerprint(bake("""
            {"bones": [{"name": "a", "cubes": [
                {"origin": [0, 0, 0], "size": [2, 2, 2], "uv": [0, 0]},
                {"origin": [4, 0, 0], "size": [2, 2, 2], "uv": [0, 0]}]}]}
            """));
        assertNotEquals(neither.get(0), mirroredFirst.get(0), "the cube that asked for it is mirrored");
        assertEquals(neither.get(1), mirroredFirst.get(1), "the one after it is not");
    }

    /**
     * A bone's own {@code mirror} does nothing, and this pins that rather than blessing it.
     *
     * <p>{@code Bone.addTo} opens the builder with the bone's flag and {@code Cube.addTo} then sets
     * the builder's flag from the CUBE's own - false unless that box asked - and clears it again
     * afterwards, so the bone's is overwritten before the first box is added. No geometry in this
     * repository or in any pack beside it writes {@code mirror} on a bone (or on a cube), and the
     * authoring tools emit neither, so nothing shipped depends on either answer; if it is ever
     * wanted, the fix is for a cube with no flag of its own to inherit the bone's, and this test is
     * where it would be turned around.
     */
    @Test
    void aBonesOwnMirrorDoesNotReachItsCubes() {
        final List<String> mirroredBone = fingerprint(bake("""
            {"bones": [{"name": "a", "mirror": true, "cubes": [
                {"origin": [0, 0, 0], "size": [2, 2, 2], "uv": [0, 0]}]}]}
            """));
        final List<String> plainBone = fingerprint(bake("""
            {"bones": [{"name": "a", "cubes": [
                {"origin": [0, 0, 0], "size": [2, 2, 2], "uv": [0, 0]}]}]}
            """));
        final List<String> mirroredCube = fingerprint(bake("""
            {"bones": [{"name": "a", "cubes": [
                {"origin": [0, 0, 0], "size": [2, 2, 2], "uv": [0, 0], "mirror": true}]}]}
            """));
        assertEquals(plainBone, mirroredBone, "a bone's flag does not reach the boxes in it");
        assertNotEquals(plainBone, mirroredCube, "a box's own flag does");
    }

    // ---- what a filled fitting leaves out ----------------------------------------------------------

    @Test
    void aBoneLeftOutTakesItsChildrenWithIt() {
        final DecorationGeometry geometry = parse(TREE);
        final ModelPart without = geometry.bake(Set.of("cloth"));
        assertFalse(without.hasChild("cloth"), "the bone the fitting draws itself");
        assertTrue(without.hasChild("pole"), "and nothing else");
        assertEquals(
            List.of("/pole"),
            fingerprint(without).stream().map(line -> line.substring(0, line.indexOf(' '))).distinct().toList(),
            "a bone left out takes the bones under it with it - a half-drawn banner is worse than none");
    }

    @Test
    void aChildLeftOutLeavesItsParentStanding() {
        final ModelPart without = parse(TREE).bake(Set.of("fringe"));
        assertTrue(without.hasChild("cloth"), "the parent stays");
        assertFalse(without.getChild("cloth").hasChild("fringe"), "and only the named child goes");
    }

    @Test
    void leavingOutNothingIsThePartItself() {
        final DecorationGeometry geometry = parse(TREE);
        assertEquals(fingerprint(geometry.bake()), fingerprint(geometry.bake(Set.of())),
            "an empty set is the whole part");
        assertEquals(fingerprint(geometry.bake()), fingerprint(geometry.bake(Set.of("nothing_here"))),
            "and so is a name this part does not have - a fitting on another part costs this one nothing");
    }

    /** A part with a bone a fitting can take over, and a bone under it that goes with it. */
    private static final String TREE = """
        {"bones": [{"name": "pole", "pivot": [0, 0, 0],
                    "cubes": [{"origin": [0, 0, 0], "size": [1, 8, 1]}]},
                   {"name": "cloth", "pivot": [0, 0, 1],
                    "cubes": [{"origin": [0, 0, 0], "size": [6, 6, 1], "uv": [4, 0]}],
                    "children": [{"name": "fringe", "pivot": [0, 6, 0],
                                  "cubes": [{"origin": [0, 0, 0], "size": [6, 1, 1], "uv": [4, 8]}]}]}]}
        """;

    // ---- reading a baked model back ----------------------------------------------------------------

    private static DecorationGeometry parse(final String json) {
        return DecorationGeometry.CODEC.parse(JsonOps.INSTANCE, JsonParser.parseString(json))
            .getOrThrow(message -> new AssertionError("could not be read: " + message));
    }

    private static ModelPart bake(final String json) {
        return parse(json).bake();
    }

    private static void assertRefused(final String json, final String why) {
        final DataResult<DecorationGeometry> result =
            DecorationGeometry.CODEC.parse(JsonOps.INSTANCE, JsonParser.parseString(json));
        assertTrue(result.error().isPresent(), () -> why + " was accepted: " + result.result());
    }

    /** The one box of a one-box geometry, measured as it would be drawn. */
    private static Box onlyBox(final String json) {
        final List<Box> boxes = boxes(bake(json));
        assertEquals(1, boxes.size(), "this fixture is meant to have exactly one box");
        return boxes.getFirst();
    }

    /**
     * A box as it reaches the screen: its VERTICES, not the {@code minX..maxZ} vanilla was handed.
     *
     * <p>Those fields are the box before its deformation is applied, so the fractional unwrap - which
     * hands vanilla a rounded box and shrinks it back through the deformation - reads there as the
     * rounded size. Everything a player sees is the vertices.
     */
    private record Box(
        float minX, float maxX, float minY, float maxY, float minZ, float maxZ,
        int minU, int maxU, int minV, int maxV, float rawMaxU, List<float[]> uvs
    ) {
        void everyVertexIsOnAWholeTexel(final int textureWidth, final int textureHeight) {
            for (final float[] uv : this.uvs) {
                assertEquals(Math.round(uv[0] * textureWidth), uv[0] * textureWidth, 1.0E-3F,
                    "a vertex off the texel grid across");
                assertEquals(Math.round(uv[1] * textureHeight), uv[1] * textureHeight, 1.0E-3F,
                    "a vertex off the texel grid down");
            }
        }
    }

    private static List<Box> boxes(final ModelPart root) {
        final List<Box> found = new ArrayList<>();
        root.visit(new PoseStack(), (pose, path, index, cube) -> {
            float minX = Float.MAX_VALUE;
            float maxX = -Float.MAX_VALUE;
            float minY = Float.MAX_VALUE;
            float maxY = -Float.MAX_VALUE;
            float minZ = Float.MAX_VALUE;
            float maxZ = -Float.MAX_VALUE;
            float minU = Float.MAX_VALUE;
            float maxU = -Float.MAX_VALUE;
            float minV = Float.MAX_VALUE;
            float maxV = -Float.MAX_VALUE;
            final List<float[]> uvs = new ArrayList<>();
            for (final ModelPart.Polygon polygon : cube.polygons) {
                for (final ModelPart.Vertex vertex : polygon.vertices()) {
                    minX = Math.min(minX, vertex.x());
                    maxX = Math.max(maxX, vertex.x());
                    minY = Math.min(minY, vertex.y());
                    maxY = Math.max(maxY, vertex.y());
                    minZ = Math.min(minZ, vertex.z());
                    maxZ = Math.max(maxZ, vertex.z());
                    minU = Math.min(minU, vertex.u());
                    maxU = Math.max(maxU, vertex.u());
                    minV = Math.min(minV, vertex.v());
                    maxV = Math.max(maxV, vertex.v());
                    uvs.add(new float[] {vertex.u(), vertex.v()});
                }
            }
            // The uv extents are wanted in texels, which is what an author counts in; the sheet's own
            // size is recoverable from any vertex, since the net is measured on it.
            final int width = Math.round(1.0F / step(uvs, 0));
            final int height = Math.round(1.0F / step(uvs, 1));
            found.add(new Box(minX, maxX, minY, maxY, minZ, maxZ,
                Math.round(minU * width), Math.round(maxU * width),
                Math.round(minV * height), Math.round(maxV * height), maxU, uvs));
        });
        return found;
    }

    /**
     * The size of one texel on the sheet this box was unwrapped against, read out of the box itself.
     *
     * <p>A vertex carries a fraction of the sheet, not a texel, so a test that wants to say "column
     * 4" has to know the sheet's width - and asking the geometry would let a bake that ignores the
     * declared width agree with a test that also ignores it. The smallest non-zero gap between two
     * vertex coordinates is one texel, because a box's faces are whole texels by the rule above and
     * the smallest of them is one deep.
     */
    private static float step(final List<float[]> uvs, final int axis) {
        float smallest = Float.MAX_VALUE;
        for (final float[] one : uvs) {
            for (final float[] other : uvs) {
                final float gap = Math.abs(one[axis] - other[axis]);
                if (gap > 1.0E-6F) {
                    smallest = Math.min(smallest, gap);
                }
            }
        }
        return smallest;
    }

    /**
     * A structural print of a baked tree: every cube, under the bone path it hangs from, with the
     * transform it is drawn under and the order its corners are painted in.
     *
     * <p>The vertex ORDER is in it on purpose - mirroring a box moves no corner, it reverses which
     * corner takes which texel, and a fingerprint that only measured extents would call a mirrored
     * box identical to a plain one.
     */
    private static List<String> fingerprint(final ModelPart root) {
        final List<String> lines = new ArrayList<>();
        root.visit(new PoseStack(), (pose, path, index, cube) -> {
            final StringBuilder line = new StringBuilder(path).append(' ').append(index);
            line.append(String.format(" at(%.4f,%.4f,%.4f)",
                pose.pose().m30(), pose.pose().m31(), pose.pose().m32()));
            for (final ModelPart.Polygon polygon : cube.polygons) {
                for (final ModelPart.Vertex vertex : polygon.vertices()) {
                    line.append(String.format(" %.4f,%.4f,%.4f/%.4f,%.4f",
                        vertex.x(), vertex.y(), vertex.z(), vertex.u(), vertex.v()));
                }
            }
            lines.add(line.toString());
        });
        return lines;
    }

    /** Where each bone that holds a box is drawn, by the path {@link ModelPart#visit} reports. */
    private static Map<String, float[]> places(final ModelPart root) {
        final Map<String, float[]> places = new LinkedHashMap<>();
        root.visit(new PoseStack(), (pose, path, index, cube) -> places.putIfAbsent(
            path, new float[] {pose.pose().m30(), pose.pose().m31(), pose.pose().m32()}));
        return places;
    }
}
