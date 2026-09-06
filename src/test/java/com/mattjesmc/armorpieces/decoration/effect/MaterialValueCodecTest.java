package com.mattjesmc.armorpieces.decoration.effect;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonElement;
import com.mojang.datafixers.util.Either;
import com.mojang.serialization.Codec;
import com.mojang.serialization.JsonOps;
import java.util.List;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.equipment.trim.TrimMaterial;
import org.junit.jupiter.api.Test;

/**
 * A per-material number is written back in the form it was read in.
 *
 * <p>The same encode-side trap as {@code LootGroup.TableEntry}, avoided differently:
 * {@link MaterialValue} is built on {@code Codec.either}, which encodes on the side it holds,
 * rather than on {@code withAlternative}, which always encodes with the first. What that buys is
 * that a file saying {@code 1.0} still says {@code 1.0} after an editor has opened and saved it,
 * and a file with cases keeps them - which matters because the Blockbench dialog writes these
 * fields back on every Save.
 */
class MaterialValueCodecTest {
    private static final Codec<MaterialValue<Double>> CODEC = MaterialValue.codec(Codec.DOUBLE);

    private static final ResourceKey<TrimMaterial> AMETHYST = ResourceKey.create(
        Registries.TRIM_MATERIAL, Identifier.fromNamespaceAndPath("minecraft", "amethyst"));
    private static final TagKey<TrimMaterial> GEMSTONES = TagKey.create(
        Registries.TRIM_MATERIAL, Identifier.fromNamespaceAndPath("armorpieces", "gemstones"));

    private static JsonElement encode(final MaterialValue<Double> value) {
        return CODEC.encodeStart(JsonOps.INSTANCE, value).getOrThrow();
    }

    private static MaterialValue<Double> decode(final JsonElement json) {
        return CODEC.parse(JsonOps.INSTANCE, json).getOrThrow();
    }

    @Test
    void aPlainNumberStaysAPlainNumber() {
        final MaterialValue<Double> flat = MaterialValue.of(2.0);
        final JsonElement json = encode(flat);
        assertTrue(json.isJsonPrimitive(),
            () -> "a value with no cases has to be written bare, not as " + json);
        assertEquals(flat, decode(json));
    }

    @Test
    void theCasesAndTheirOrderSurvive() {
        final MaterialValue<Double> scaled = new MaterialValue<>(0.1, List.of(
            new MaterialValue.Case<>(Either.right(AMETHYST), 0.25),
            new MaterialValue.Case<>(Either.left(GEMSTONES), 0.15)));

        final JsonElement json = encode(scaled);
        assertTrue(json.isJsonObject(),
            () -> "a value with cases has to be written as an object, not " + json);

        final MaterialValue<Double> back = decode(json);
        assertEquals(scaled, back, "the cases did not survive the round trip");
        assertEquals(scaled.cases(), back.cases(),
            "first match wins, so the ORDER of the cases is part of the meaning");
        assertEquals(json, encode(back), "a second trip changed the file");
    }

    @Test
    void anExactMaterialAndATagAreNotTheSameCase() {
        final JsonElement byId = encode(new MaterialValue<>(0.0,
            List.of(new MaterialValue.Case<>(Either.right(AMETHYST), 1.0))));
        final JsonElement byTag = encode(new MaterialValue<>(0.0,
            List.of(new MaterialValue.Case<>(Either.left(GEMSTONES), 1.0))));
        assertTrue(byTag.toString().contains("#"),
            () -> "a tag has to be written with its # or it reads back as an id: " + byTag);
        assertEquals(false, byId.toString().equals(byTag.toString()));
    }
}
