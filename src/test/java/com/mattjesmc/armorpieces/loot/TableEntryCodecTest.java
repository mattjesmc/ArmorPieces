package com.mattjesmc.armorpieces.loot;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonElement;
import com.mojang.serialization.JsonOps;
import java.util.List;
import java.util.Optional;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.storage.loot.LootTable;
import org.junit.jupiter.api.Test;

/**
 * A loot group's table entry survives being written back.
 *
 * <p>{@code Codec.withAlternative(A, B)} reads either form and always ENCODES with A. As
 * {@link LootGroup.TableEntry}'s A is the bare id, an entry carrying a chance of its own
 * round-tripped back to an id and the chance vanished - and nothing noticed for as long as these
 * files were only ever read. The fix is an explicit encoder that picks the form by what the entry
 * has to say, and the shape of a bug that only appears once something writes is exactly the shape a
 * test is for.
 */
class TableEntryCodecTest {
    private static final ResourceKey<LootTable> TABLE = ResourceKey.create(
        Registries.LOOT_TABLE, Identifier.fromNamespaceAndPath("minecraft", "chests/simple_dungeon"));

    private static JsonElement encode(final LootGroup.TableEntry entry) {
        return LootGroup.TableEntry.CODEC.encodeStart(JsonOps.INSTANCE, entry).getOrThrow();
    }

    private static LootGroup.TableEntry decode(final JsonElement json) {
        return LootGroup.TableEntry.CODEC.parse(JsonOps.INSTANCE, json).getOrThrow();
    }

    @Test
    void aBareEntryStaysABareId() {
        final LootGroup.TableEntry bare = new LootGroup.TableEntry(TABLE, Optional.empty());
        final JsonElement json = encode(bare);
        assertTrue(json.isJsonPrimitive(),
            () -> "an entry with nothing else to say should still be a plain id, not " + json);
        assertEquals(bare, decode(json));
    }

    @Test
    void anEntryWithItsOwnChanceKeepsIt() {
        final LootGroup.TableEntry withChance = new LootGroup.TableEntry(TABLE, Optional.of(0.3f));
        final JsonElement json = encode(withChance);
        assertTrue(json.isJsonObject(),
            () -> "an entry carrying a chance has to be written as an object, not " + json);
        assertEquals(withChance, decode(json),
            "the chance was lost on the way out - withAlternative encoded with the bare form");
        assertEquals(json, encode(decode(json)), "a second trip changed the file");
    }

    @Test
    void bothFormsReadAndSurviveTogether() {
        final List<LootGroup.TableEntry> entries = List.of(
            new LootGroup.TableEntry(TABLE, Optional.empty()),
            new LootGroup.TableEntry(TABLE, Optional.of(1.0f)),
            new LootGroup.TableEntry(TABLE, Optional.of(0.0f)));
        final JsonElement json =
            LootGroup.TableEntry.CODEC.listOf().encodeStart(JsonOps.INSTANCE, entries).getOrThrow();
        assertEquals(entries,
            LootGroup.TableEntry.CODEC.listOf().parse(JsonOps.INSTANCE, json).getOrThrow());
    }
}
