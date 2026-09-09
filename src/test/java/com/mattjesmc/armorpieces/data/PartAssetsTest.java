package com.mattjesmc.armorpieces.data;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.mattjesmc.armorpieces.client.geometry.DecorationGeometry;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mojang.serialization.JsonOps;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.Reader;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import net.minecraft.core.Holder;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.packs.resources.Resource;
import org.junit.jupiter.api.Test;

/**
 * A part is a datapack file AND a picture, and the file is the half nobody forgets.
 *
 * <p>What the registry load next door proves is that every part is readable. What it cannot say is
 * that any of them can be DRAWN: the geometry lives in the resource pack under a path derived from
 * {@code asset_id}, the texture beside it, and a mask sheet per fitting beside that. Every one of
 * those is a string built at render time out of an id, so a renamed file is not a compile error, not
 * a load error, and not a warning - it is a part that is silently invisible on a player who crafted
 * it, and the only way it has ever been found is by wearing one.
 *
 * <p>The geometry is not merely parsed here but BAKED, through vanilla's own
 * {@link net.minecraft.client.model.geom.builders.LayerDefinition} - which is where a bone that
 * names itself twice or a cube vanilla refuses actually fails. No GL: baking a model is arithmetic.
 */
class PartAssetsTest {
    private static final String GEOMETRY = "armorpieces/decoration";
    private static final String TEXTURES = "textures/entity/decoration";

    /** Every part, from the mod and from every pack beside it. */
    private static Map<ResourceKey<ArmorDecoration>, ArmorDecoration> parts() {
        return Map.copyOf(ShippedData.everything()
            .<ArmorDecoration>registry(ArmorPiecesRegistries.ARMOR_DECORATION)
            .entrySet().stream()
            .collect(java.util.stream.Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue)));
    }

    @Test
    void everyPartsGeometryParsesAndBakes() {
        final List<String> broken = new ArrayList<>();
        parts().forEach((key, part) -> {
            final Identifier file = part.assetId().withPath(path -> GEOMETRY + "/" + path + ".json");
            final Optional<Resource> resource = ShippedData.clientResources().getResource(file);
            if (resource.isEmpty()) {
                broken.add(key.identifier() + " has no geometry: " + file);
                return;
            }
            try (Reader reader = new InputStreamReader(resource.get().open())) {
                final JsonElement json = JsonParser.parseReader(reader);
                final DecorationGeometry geometry = DecorationGeometry.CODEC.parse(JsonOps.INSTANCE, json)
                    .getOrThrow(message -> new AssertionError(message));
                assertNotNull(geometry.bake(), () -> key.identifier() + " baked to nothing");
            } catch (final IOException | RuntimeException | AssertionError failed) {
                broken.add(key.identifier() + " (" + file + "): " + failed.getMessage());
            }
        });
        assertTrue(broken.isEmpty(), () -> "parts that cannot be drawn:\n  " + String.join("\n  ", broken));
    }

    /**
     * The greyscale master, which every material's texture is coloured from. A part without one
     * draws as a hole - the render layer asks for a texture that is not there and gets the missing
     * texture, on a model the player is wearing.
     */
    @Test
    void everyPartHasItsMasterSheet() {
        final List<String> missing = new ArrayList<>();
        parts().forEach((key, part) -> {
            final Identifier master = sheet(part, "");
            if (ShippedData.clientResources().getResource(master).isEmpty()) {
                missing.add(key.identifier() + " -> " + master);
            }
        });
        assertTrue(missing.isEmpty(), () -> "parts with no master sheet:\n  " + String.join("\n  ", missing));
    }

    /**
     * A masked fitting is a second greyscale sheet named after the fitting, and the ONLY thing that
     * makes a fitting visible. A part that lists {@code armorpieces:gemstone} and ships no
     * {@code <part>_gemstone.png} takes the gem, spends the material, and looks identical.
     *
     * <p>The name is the fitting's registry path, which is what
     * {@link com.mattjesmc.armorpieces.client.ArmorDecorationLayer} builds the mask out of.
     */
    @Test
    void everyMaskedFittingOnAPartHasItsSheet() {
        final List<String> missing = new ArrayList<>();
        parts().forEach((key, part) -> {
            for (final Holder<Fitting> holder : part.fittings()) {
                if (!(holder.value() instanceof Fitting.Masked)) {
                    continue;
                }
                final String name = holder.unwrapKey().orElseThrow().identifier().getPath();
                final Identifier mask = sheet(part, "_" + name);
                if (ShippedData.clientResources().getResource(mask).isEmpty()) {
                    missing.add(key.identifier() + " wears " + name + " but ships no " + mask);
                }
            }
        });
        assertTrue(missing.isEmpty(), () -> "fittings that cannot be seen:\n  " + String.join("\n  ", missing));
    }

    /**
     * A fitting that REPLACES a bone (the banner one does) names that bone by string, and the part's
     * own geometry has to have it. A misspelling here hides nothing and draws nothing: the bone
     * stays, the banner is drawn over it, and the two z-fight.
     */
    @Test
    void everyReplacedBoneExistsInThePartsGeometry() {
        final List<String> missing = new ArrayList<>();
        parts().forEach((key, part) -> {
            final Set<String> replaced = new HashSet<>();
            part.fittings().forEach(holder -> replaced.addAll(holder.value().replacedBones()));
            if (replaced.isEmpty()) {
                return;
            }
            final Set<String> bones = bones(part);
            replaced.removeAll(bones);
            replaced.forEach(bone ->
                missing.add(key.identifier() + " replaces the bone '" + bone + "', which its geometry "
                    + "does not have; it has " + bones));
        });
        assertTrue(missing.isEmpty(), () -> String.join("\n  ", missing));
    }

    private static Set<String> bones(final ArmorDecoration part) {
        final Identifier file = part.assetId().withPath(path -> GEOMETRY + "/" + path + ".json");
        final Resource resource = ShippedData.clientResources().getResource(file)
            .orElseGet(() -> fail("no geometry for " + part.assetId()));
        try (Reader reader = new InputStreamReader(resource.open())) {
            final DecorationGeometry geometry = DecorationGeometry.CODEC
                .parse(JsonOps.INSTANCE, JsonParser.parseReader(reader))
                .getOrThrow(message -> new AssertionError(message));
            final Set<String> names = new HashSet<>();
            collect(geometry.bones(), names);
            return names;
        } catch (final IOException failed) {
            return fail(failed);
        }
    }

    private static void collect(final List<DecorationGeometry.Bone> bones, final Set<String> into) {
        for (final DecorationGeometry.Bone bone : bones) {
            into.add(bone.name());
            collect(bone.children(), into);
        }
    }

    private static Identifier sheet(final ArmorDecoration part, final String suffix) {
        return part.assetId().withPath(path -> TEXTURES + "/" + path + suffix + ".png");
    }
}
