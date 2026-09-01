package com.mattjesmc.armorpieces.client.geometry;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.List;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.util.ExtraCodecs;

/**
 * A decorative part's shape, as authored in a resource pack.
 *
 * <p>Entity geometry is normally compiled into Java as a {@code LayerDefinition}, which would make
 * every part's shape a code change and put "expandable through resource packs" out of reach. So the
 * same structure is expressed as JSON and built at load time instead: this record is a literal
 * mirror of {@link MeshDefinition} / {@link PartDefinition} / {@link CubeListBuilder}, and {@link
 * #bake} does nothing but walk it into those builders. Vanilla's own baker does the rest, so parts
 * get correct UVs, per-bone pivots and rotations, and cube inflation with no geometry code of ours.
 *
 * <p>The field names deliberately match Blockbench's Bedrock-style vocabulary - {@code bones},
 * {@code pivot}, {@code cubes}, {@code origin}, {@code size}, {@code uv}, {@code inflate} - so the
 * format reads as familiar to anyone who has modelled for Minecraft before, even though it is
 * ultimately baked through the Java entity-model path.
 *
 * <p>Coordinates are entity-model space: units are 1/16 of a block and <b>+Y points DOWN</b>, which
 * is why a plume standing on top of a head has a negative Y origin.
 */
@Environment(EnvType.CLIENT)
public record DecorationGeometry(int textureWidth, int textureHeight, List<Bone> bones) {
    public static final Codec<DecorationGeometry> CODEC = RecordCodecBuilder.create(
        i -> i.group(
                ExtraCodecs.POSITIVE_INT.optionalFieldOf("texture_width", 32).forGetter(DecorationGeometry::textureWidth),
                ExtraCodecs.POSITIVE_INT.optionalFieldOf("texture_height", 32).forGetter(DecorationGeometry::textureHeight),
                ExtraCodecs.nonEmptyList(Bone.CODEC.listOf()).fieldOf("bones").forGetter(DecorationGeometry::bones)
            )
            .apply(i, DecorationGeometry::new)
    );

    /**
     * Builds a real {@link ModelPart} tree from this description.
     *
     * <p>Called once per part per resource reload, off the loader thread, and the result is cached -
     * see {@link DecorationGeometryManager}. Never call it per frame.
     */
    public ModelPart bake() {
        final MeshDefinition mesh = new MeshDefinition();
        final PartDefinition root = mesh.getRoot();
        for (final Bone bone : this.bones) {
            bone.addTo(root);
        }
        return LayerDefinition.create(mesh, this.textureWidth, this.textureHeight).bakeRoot();
    }

    /**
     * One bone: a named pivot with its own rotation, some boxes, and optional children that inherit
     * its transform. Children are what let a part animate as a hierarchy later (a plume whose tip
     * lags its base) without the format changing.
     */
    @Environment(EnvType.CLIENT)
    public record Bone(
        String name,
        Vec3f pivot,
        Vec3f rotation,
        boolean mirror,
        List<Cube> cubes,
        List<Bone> children
    ) {
        public static final Codec<Bone> CODEC = Codec.recursive(
            "armorpieces:decoration_bone",
            self -> RecordCodecBuilder.create(
                i -> i.group(
                        Codec.STRING.fieldOf("name").forGetter(Bone::name),
                        Vec3f.CODEC.optionalFieldOf("pivot", Vec3f.ZERO).forGetter(Bone::pivot),
                        Vec3f.CODEC.optionalFieldOf("rotation", Vec3f.ZERO).forGetter(Bone::rotation),
                        Codec.BOOL.optionalFieldOf("mirror", false).forGetter(Bone::mirror),
                        Cube.CODEC.listOf().optionalFieldOf("cubes", List.of()).forGetter(Bone::cubes),
                        self.listOf().optionalFieldOf("children", List.of()).forGetter(Bone::children)
                    )
                    .apply(i, Bone::new)
            )
        );

        private void addTo(final PartDefinition parent) {
            final CubeListBuilder builder = CubeListBuilder.create().mirror(this.mirror);
            for (final Cube cube : this.cubes) {
                cube.addTo(builder);
            }
            // Rotations are authored in degrees, as every modelling tool writes them, and converted
            // here - PartPose wants radians.
            final PartDefinition self = parent.addOrReplaceChild(
                this.name,
                builder,
                PartPose.offsetAndRotation(
                    this.pivot.x(), this.pivot.y(), this.pivot.z(),
                    this.rotation.x() * ((float) Math.PI / 180.0F),
                    this.rotation.y() * ((float) Math.PI / 180.0F),
                    this.rotation.z() * ((float) Math.PI / 180.0F)
                )
            );
            for (final Bone child : this.children) {
                child.addTo(self);
            }
        }
    }

    /** One box, positioned relative to its bone's pivot, with its top-left UV on the part texture. */
    @Environment(EnvType.CLIENT)
    public record Cube(Vec3f origin, Vec3f size, int u, int v, float inflate, boolean mirror) {
        public static final Codec<Cube> CODEC = RecordCodecBuilder.create(
            i -> i.group(
                    Vec3f.CODEC.fieldOf("origin").forGetter(Cube::origin),
                    Vec3f.CODEC.fieldOf("size").forGetter(Cube::size),
                    Codec.INT.listOf().comapFlatMap(
                        list -> list.size() == 2
                            ? com.mojang.serialization.DataResult.success(list)
                            : com.mojang.serialization.DataResult.error(() -> "uv must have exactly 2 elements"),
                        list -> list
                    ).optionalFieldOf("uv", List.of(0, 0)).forGetter(c -> List.of(c.u(), c.v())),
                    Codec.FLOAT.optionalFieldOf("inflate", 0.0F).forGetter(Cube::inflate),
                    Codec.BOOL.optionalFieldOf("mirror", false).forGetter(Cube::mirror)
                )
                .apply(i, (origin, size, uv, inflate, mirror) ->
                    new Cube(origin, size, uv.get(0), uv.get(1), inflate, mirror))
        );

        private void addTo(final CubeListBuilder builder) {
            // mirror() is sticky on the builder, so a per-cube flag has to be set and cleared around
            // the box it belongs to rather than left on for whatever follows.
            builder.mirror(this.mirror);
            builder.texOffs(this.u, this.v)
                .addBox(
                    this.origin.x(), this.origin.y(), this.origin.z(),
                    this.size.x(), this.size.y(), this.size.z(),
                    new CubeDeformation(this.inflate)
                );
            builder.mirror(false);
        }
    }

    /** A three-float array, the shape every coordinate in this format takes. */
    @Environment(EnvType.CLIENT)
    public record Vec3f(float x, float y, float z) {
        public static final Vec3f ZERO = new Vec3f(0.0F, 0.0F, 0.0F);
        public static final Codec<Vec3f> CODEC = Codec.FLOAT.listOf().comapFlatMap(
            list -> list.size() == 3
                ? com.mojang.serialization.DataResult.success(new Vec3f(list.get(0), list.get(1), list.get(2)))
                : com.mojang.serialization.DataResult.error(() -> "Expected 3 elements, got " + list.size()),
            v -> List.of(v.x(), v.y(), v.z())
        );
    }
}
