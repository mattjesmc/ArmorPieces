package com.mattjesmc.armorpieces.identity;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.mattjesmc.armorpieces.GameBootstrap;
import com.mattjesmc.armorpieces.cloth.Cloth;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.skin.ArmorSkin;
import com.mattjesmc.armorpieces.skin.ArmorSkinValue;
import com.mojang.serialization.JsonOps;
import com.mojang.serialization.Lifecycle;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Stream;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.component.DataComponentPatch;
import net.minecraft.core.MappedRegistry;
import net.minecraft.core.registries.Registries;
import net.minecraft.core.Registry;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.RegistryOps;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.equipment.trim.MaterialAssetGroup;
import net.minecraft.world.item.equipment.trim.TrimMaterial;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * The one thing this whole mechanism exists for: <b>a saved item is never destroyed by content it
 * cannot name.</b>
 *
 * <p>Before it, a helmet whose crest named a part the installed packs no longer defined did not lose
 * the crest - it lost the helmet. {@code ItemStack.CODEC.parse} returned an error with no partial at
 * all, and every caller that loads a saved stack turns that into a logged line and empty air. The
 * first test here is that measurement, inverted into an assertion; everything after it is the
 * behaviour built on top.
 *
 * <p>The world these run in is vanilla's registries plus three of ours, hand-built: {@code visor} is
 * a part that is installed, {@code armorpieces_hunt:tusks} is one that MOVED and says so, and
 * {@code armorpieces:tusks} is the id a 0.3.0 save would have written. No game, no server, no world.
 */
class IdentityCodecTest {
    private static final Identifier VISOR = Identifier.fromNamespaceAndPath("armorpieces", "visor");
    private static final Identifier MOVED = Identifier.fromNamespaceAndPath("armorpieces_hunt", "tusks");
    private static final Identifier OLD = Identifier.fromNamespaceAndPath("armorpieces", "tusks");
    private static final Identifier SKIN_MOVED =
        Identifier.fromNamespaceAndPath("armorpieces_legends", "varangian");
    private static final Identifier SKIN_OLD =
        Identifier.fromNamespaceAndPath("armorpieces", "varangian");

    private static final String MOVED_UID = "ap1testtusks";
    private static final String VISOR_UID = "ap1testvisor";
    private static final String SKIN_UID = "ap1testvarangian";

    private static HolderLookup.Provider registries;
    private static RegistryOps<JsonElement> ops;

    @BeforeAll
    static void world() {
        GameBootstrap.once();
        GameBootstrap.components();

        final MappedRegistry<ArmorDecoration> parts =
            new MappedRegistry<>(ArmorPiecesRegistries.ARMOR_DECORATION, Lifecycle.stable());
        Registry.register(parts, VISOR, part(VISOR, List.of(), VISOR_UID));
        // The piece the split moved: a new id, saying what it used to answer to.
        Registry.register(parts, MOVED, part(MOVED, List.of(OLD), MOVED_UID));

        final MappedRegistry<ArmorSkin> skins =
            new MappedRegistry<>(ArmorPiecesRegistries.ARMOR_SKIN, Lifecycle.stable());
        Registry.register(skins, SKIN_MOVED, new ArmorSkin(
            SKIN_MOVED, Component.literal("Varangian"), List.of(), List.of(SKIN_OLD),
            Optional.of(SKIN_UID)));

        final MappedRegistry<Cloth> cloths =
            new MappedRegistry<>(ArmorPiecesRegistries.CLOTH, Lifecycle.stable());

        // Vanilla's trim materials, but built HERE rather than taken from VanillaRegistries: a
        // holder from that builder's lookups fails canSerializeIn against the RegistryOps made from
        // the same provider, so it decodes and then refuses to encode. Four hand-built registries
        // are both simpler and the only shape that round trips.
        final MappedRegistry<TrimMaterial> materials =
            new MappedRegistry<>(Registries.TRIM_MATERIAL, Lifecycle.stable());
        Registry.register(materials, Identifier.withDefaultNamespace("iron"),
            new TrimMaterial(MaterialAssetGroup.IRON, Component.literal("Iron")));
        Registry.register(materials, Identifier.withDefaultNamespace("gold"),
            new TrimMaterial(MaterialAssetGroup.GOLD, Component.literal("Gold")));

        final Map<ResourceKey<? extends Registry<?>>, Registry<?>> world = Map.of(
            Registries.TRIM_MATERIAL, materials.freeze(),
            ArmorPiecesRegistries.ARMOR_DECORATION, parts.freeze(),
            ArmorPiecesRegistries.ARMOR_SKIN, skins.freeze(),
            ArmorPiecesRegistries.CLOTH, cloths.freeze());
        registries = new HolderLookup.Provider() {
            @Override
            public Stream<ResourceKey<? extends Registry<?>>> listRegistryKeys() {
                return world.keySet().stream();
            }

            @Override
            @SuppressWarnings("unchecked")
            public <T> Optional<? extends HolderLookup.RegistryLookup<T>> lookup(
                final ResourceKey<? extends Registry<? extends T>> key
            ) {
                return Optional.ofNullable((HolderLookup.RegistryLookup<T>) world.get(key));
            }
        };
        ops = registries.createSerializationContext(JsonOps.INSTANCE);
    }

    private static ArmorDecoration part(
        final Identifier id, final List<Identifier> formerIds, final String uid
    ) {
        return new ArmorDecoration(id, Component.literal(id.getPath()), Set.of(DecorationAnchor.BROW),
            List.of(), List.of(), List.of(), formerIds, Optional.of(uid));
    }

    @BeforeEach
    void freshIndex() {
        Rebind.forgetMisses();
        Rebind.rebuild(registries);
    }

    private static JsonElement json(final String text) {
        return JsonParser.parseString(text);
    }

    /**
     * The measurement of {@code docs/plans/compatibility.md} §0, inverted.
     *
     * <p>{@code ItemStack}'s codec reads its components through
     * {@code Codec.optionalFieldOf("components", DataComponentPatch.EMPTY)} - <b>not</b> the lenient
     * variant it uses elsewhere - so a {@code DataComponentPatch} that fails to decode fails the whole
     * stack, and every caller that loads a saved item turns that into a logged line and empty air.
     * The patch is therefore the layer to test, and the assertion is simply that it survives.
     *
     * <p>The full {@code ItemStack.CODEC} cannot be exercised here: its {@code id} field resolves
     * through {@code Item.CODEC_WITH_BOUND_COMPONENTS}, and an item's default components come from a
     * datapack, which a unit test has no server to load. That is the gate's tier 2, not this.
     */
    @Test
    void anUnknownPartDoesNotFailTheComponentPatch() {
        // No index at all - the harshest case, and the one a player upgrading with no pack installed
        // is actually in.
        Rebind.clear();
        final DataComponentPatch patch = DataComponentPatch.CODEC.parse(ops, json("""
            {
              "minecraft:custom_name": "'Grandfather'",
              "armorpieces:decorations": {
                "crest": {"material": "minecraft:gold", "decoration": "armorpieces:nonesuch"},
                "brow": {"material": "minecraft:iron", "decoration": "armorpieces:visor"}
              }
            }
            """)).getOrThrow();

        assertEquals(2, patch.size(), "the patch survives, and so does everything else on the item");

        final ArmorDecorations worn = (ArmorDecorations) patch.entrySet().stream()
            .filter(entry -> entry.getKey() == ModDataComponents.DECORATIONS)
            .findFirst().orElseThrow().getValue().orElseThrow();
        assertNotNull(worn);
        assertEquals(1, worn.entries().size(), "the socket that could be read is read");
        assertEquals(1, worn.unresolvedCount(), "the one that could not is kept, not dropped");
        assertEquals(List.of("armorpieces:nonesuch"), worn.unresolvedNames(),
            "and it still knows what it was waiting for");
        assertTrue(Rebind.anyMissing(), "which is what /armorpieces missing reports");
    }

    /** What cannot be read is written back exactly as it came in. */
    @Test
    void anUnresolvedSocketRoundTrips() {
        Rebind.clear();
        final JsonElement written = json("""
            {"crest": {"material": "minecraft:gold", "decoration": "armorpieces:nonesuch",
                       "fittings": {"armorpieces:gemstone": "minecraft:emerald"}}}
            """);
        final ArmorDecorations worn = ArmorDecorations.CODEC.parse(ops, written).getOrThrow();
        assertEquals(1, worn.unresolvedCount());
        assertEquals(written, ArmorDecorations.CODEC.encodeStart(ops, worn).getOrThrow(),
            "verbatim: the day the pack is installed, this has to still be exactly what was saved");
    }

    /**
     * The upgrade, in one round trip. A 0.3.0 entry naming a part that has since moved comes back as
     * the part's NEW id with the lineage stamped beside it - which is what the next save writes.
     */
    @Test
    void aMovedPartIsReboundAndStamped() {
        final ArmorDecorations worn = ArmorDecorations.CODEC.parse(ops, json("""
            {"brow": {"material": "minecraft:iron", "decoration": "armorpieces:tusks"}}
            """)).getOrThrow();

        assertEquals(0, worn.unresolvedCount(), "former_ids found it");
        assertEquals(MOVED, worn.get(DecorationAnchor.BROW).decoration().unwrapKey().orElseThrow()
            .identifier());
        assertFalse(Rebind.anyMissing(), "and nothing was reported missing");

        assertEquals(json("""
            {"brow": {"material": "minecraft:iron", "decoration": "armorpieces_hunt:tusks",
                      "uid": "ap1testtusks"}}
            """), ArmorDecorations.CODEC.encodeStart(ops, worn).getOrThrow(),
            "written back in the new form, which is the whole of the port");
    }

    /** A part found only by its lineage, when nobody declared the move. */
    @Test
    void aUidFindsAPartNoFormerIdNames() {
        final ArmorDecorations worn = ArmorDecorations.CODEC.parse(ops, json("""
            {"brow": {"material": "minecraft:iron", "decoration": "armorpieces:renamed_by_nobody",
                      "uid": "ap1testtusks"}}
            """)).getOrThrow();

        assertEquals(0, worn.unresolvedCount());
        assertEquals(MOVED, worn.get(DecorationAnchor.BROW).decoration().unwrapKey().orElseThrow()
            .identifier());
    }

    /**
     * The id is authoritative. A pack that redefines an id on purpose - which is exactly what a
     * restore pack does - must win over a lineage that says otherwise.
     */
    @Test
    void theIdBeatsAStaleUid() {
        final ArmorDecorations worn = ArmorDecorations.CODEC.parse(ops, json("""
            {"brow": {"material": "minecraft:iron", "decoration": "armorpieces:visor",
                      "uid": "ap1testtusks"}}
            """)).getOrThrow();

        assertEquals(VISOR, worn.get(DecorationAnchor.BROW).decoration().unwrapKey().orElseThrow()
            .identifier());
    }

    /** A socket named by a version this one has never heard of is kept, key and all. */
    @Test
    void anUnknownSocketIsKept() {
        Rebind.clear();
        final JsonElement written = json("""
            {"epaulette": {"material": "minecraft:gold", "decoration": "armorpieces:visor"}}
            """);
        final ArmorDecorations worn = ArmorDecorations.CODEC.parse(ops, written).getOrThrow();
        assertEquals(0, worn.entries().size(), "this version has no such socket");
        assertEquals(1, worn.unresolvedCount());
        assertEquals(written, ArmorDecorations.CODEC.encodeStart(ops, worn).getOrThrow(),
            "and a version that does will read it back");
    }

    /** A skin that moved packs comes back too, by the same declaration. */
    @Test
    void aMovedSkinIsRebound() {
        final Tolerant<ArmorSkinValue> skin =
            ArmorSkinValue.TOLERANT_CODEC.parse(ops, json("\"armorpieces:varangian\"")).getOrThrow();
        assertTrue(skin.isResolved(), "former_ids on the skin found it");
        assertEquals(SKIN_MOVED,
            skin.value().orElseThrow().skin().unwrapKey().orElseThrow().identifier());
    }

    /** And a skin nothing can find is kept rather than taking the chestplate with it. */
    @Test
    void anUnknownSkinIsKept() {
        Rebind.clear();
        final JsonElement written = json("\"armorpieces:nonesuch\"");
        final Tolerant<ArmorSkinValue> skin =
            ArmorSkinValue.TOLERANT_CODEC.parse(ops, written).getOrThrow();
        assertFalse(skin.isResolved());
        assertNull(skin.orNull(),
            "an absent component and an unreadable one look the same to every reader");
        assertEquals(written, ArmorSkinValue.TOLERANT_CODEC.encodeStart(ops, skin).getOrThrow());
    }

    /** A skin that is simply installed still writes back as the bare id the item model expects. */
    @Test
    void aResolvedSkinKeepsItsBareForm() {
        final JsonElement written = json("\"armorpieces_legends:varangian\"");
        final Tolerant<ArmorSkinValue> skin =
            ArmorSkinValue.TOLERANT_CODEC.parse(ops, written).getOrThrow();
        assertTrue(skin.isResolved());
        assertEquals(written, ArmorSkinValue.TOLERANT_CODEC.encodeStart(ops, skin).getOrThrow(),
            "no wrapper field may appear beside a resolved value - item models select on this");
    }
}
