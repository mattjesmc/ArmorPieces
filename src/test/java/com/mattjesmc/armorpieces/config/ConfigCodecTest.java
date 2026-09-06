package com.mattjesmc.armorpieces.config;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.mattjesmc.armorpieces.GameBootstrap;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.loot.LootGroup;
import com.mojang.serialization.Codec;
import com.mojang.serialization.JsonOps;
import java.lang.reflect.RecordComponent;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.storage.loot.LootTable;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * Holds both settings files to the rule that they show every knob they have.
 *
 * <p>This is the trap that cost the 0.4.0 loot work a game cycle to find, and it is invisible from
 * the code: {@code optionalFieldOf(name, default)} OMITS its field on ENCODE when the value equals
 * the default, so a config whose every field is optional writes itself as {@code {}} - a settings
 * file with no settings in it - while every round trip through it still passes. Both configs
 * therefore carry a second, mandatory {@code WRITE_CODEC}, and the cost of that answer is that a
 * field added to one codec and forgotten in the other is silently unwritable.
 *
 * <p>So the assertion here is not a fixed list of keys, which would need editing in step with the
 * thing it guards. It is the record's own component count: one key written per component, or the
 * write codec has fallen behind the record.
 */
class ConfigCodecTest {
    @BeforeAll
    static void bootstrap() {
        GameBootstrap.once();  // the server config's codec names a registry
    }

    private static <T extends Record> JsonObject written(final Codec<T> writeCodec, final T value) {
        final JsonElement json = writeCodec.encodeStart(JsonOps.INSTANCE, value).getOrThrow();
        assertTrue(json.isJsonObject(), "a settings file has to be an object");
        return json.getAsJsonObject();
    }

    private static void writesEveryComponent(final Class<? extends Record> type, final JsonObject json) {
        final List<String> components = List.of(type.getRecordComponents()).stream()
            .map(RecordComponent::getName).toList();
        assertEquals(components.size(), json.keySet().size(),
            () -> type.getSimpleName() + " has " + components.size() + " field(s) " + components
                + " and its WRITE_CODEC wrote " + json.keySet().size() + " " + json.keySet()
                + " - a field was added to CODEC and not to WRITE_CODEC, so it is unwritable");
    }

    @Test
    void clientConfigWritesEveryKnobAtItsDefaults() {
        final JsonObject json = written(ArmorPiecesConfig.WRITE_CODEC, ArmorPiecesConfig.DEFAULT);
        writesEveryComponent(ArmorPiecesConfig.class, json);
        assertEquals(ArmorPiecesConfig.DEFAULT,
            ArmorPiecesConfig.CODEC.parse(JsonOps.INSTANCE, json).getOrThrow());
    }

    @Test
    void serverConfigWritesEveryKnobAtItsDefaults() {
        final JsonObject json =
            written(ArmorPiecesServerConfig.WRITE_CODEC, ArmorPiecesServerConfig.DEFAULT);
        writesEveryComponent(ArmorPiecesServerConfig.class, json);
        assertEquals(ArmorPiecesServerConfig.DEFAULT,
            ArmorPiecesServerConfig.CODEC.parse(JsonOps.INSTANCE, json).getOrThrow());
    }

    /**
     * The second trap, met where it actually bites: an override that adds a table with a chance of
     * its own is written back by the same file, and a table entry that encodes as a bare id loses
     * that number in silence.
     */
    @Test
    void serverConfigKeepsATablesOwnChanceThroughAWrite() {
        final ResourceKey<LootTable> table =
            ResourceKey.create(Registries.LOOT_TABLE, Identifier.fromNamespaceAndPath("somemod", "chests/vault"));
        final ArmorPiecesServerConfig config = new ArmorPiecesServerConfig(true, 0.5f, Map.of(
            ResourceKey.create(ArmorPiecesRegistries.LOOT_GROUP,
                Identifier.fromNamespaceAndPath("armorpieces", "knightly")),
            new ArmorPiecesServerConfig.GroupOverride(
                true, Optional.of(0.25f), Optional.of(2),
                List.of(new LootGroup.TableEntry(table, Optional.of(0.3f))),
                List.of())));

        final JsonObject json = written(ArmorPiecesServerConfig.WRITE_CODEC, config);
        assertTrue(json.toString().contains("0.3"),
            () -> "the added table's own chance is not in the file it was written to: " + json);
        assertEquals(config, ArmorPiecesServerConfig.CODEC.parse(JsonOps.INSTANCE, json).getOrThrow());
    }
}
