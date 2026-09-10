package com.mattjesmc.armorpieces.loot;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.mattjesmc.armorpieces.data.ShippedData;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * A pack whose loot group names a tag NOBODY INSTALLED still loads, and the group is simply empty.
 *
 * <p>This is the gate's own finding, brought down a tier. The tier-2 `missing-tag` boot check is
 * where it was first seen and it cost a whole server boot to see: a group binding its members with
 * {@code RegistryCodecs.homogeneousList} resolves the tag when the FILE IS READ, and a tag no
 * installed pack defines does not make a smaller group - it takes the entire registry down with
 * {@code Unbound tags in registry armorpieces:armor_decoration}, and the world will not open at all.
 * A player who installs one pack of the line and not another meets that on the first launch.
 *
 * <p>{@link MemberSetTest} says the same thing about the codec in isolation; what this class adds is
 * the only part that ever went wrong, which is a REAL DATAPACK LOAD - the loader a dedicated server
 * runs, over a pack written here, stacked on the mod's own data. Nothing else in the suite loads a
 * pack this repository does not ship, and the failure mode lives in the loader rather than in any
 * codec's own result.
 */
class AbsentTagGroupTest {
    private static final String NAMESPACE = "absent_tag_test";

    /**
     * Two groups, because half the claim is that late resolution still FINDS what is there: a group
     * naming a tag nothing defines, and one naming the mod's own {@code knightly} tag.
     */
    private static Path writePack(final Path dir) throws IOException {
        final Path groups = dir.resolve("data").resolve(NAMESPACE).resolve("armorpieces").resolve("loot_group");
        Files.createDirectories(groups);
        write(groups.resolve("absent.json"), """
            { "chance": 0.5,
              "tables": ["minecraft:chests/simple_dungeon"],
              "parts": "#%s:nothing_defines_this" }
            """.formatted(NAMESPACE));
        write(groups.resolve("present.json"), """
            { "chance": 0.5,
              "tables": ["minecraft:chests/simple_dungeon"],
              "parts": "#armorpieces:knightly" }
            """);
        return dir;
    }

    private static void write(final Path file, final String json) throws IOException {
        Files.writeString(file, json, StandardCharsets.UTF_8);
    }

    private static ResourceKey<LootGroup> key(final String name) {
        return ResourceKey.create(ArmorPiecesRegistries.LOOT_GROUP,
            Identifier.fromNamespaceAndPath(NAMESPACE, name));
    }

    @Test
    void aGroupNamingATagNobodyInstalledLoads(@TempDir final Path dir) throws IOException {
        // The load is the assertion: with an eagerly bound member set this line throws before any
        // question can be asked of the result, and it takes the mod's own groups with it.
        final ShippedData.Loaded loaded = ShippedData.withPack(writePack(dir));
        ShippedData.bindTags(loaded);

        final LootGroup absent = loaded.registry(ArmorPiecesRegistries.LOOT_GROUP).getValue(key("absent"));
        assertNotNull(absent, "the group naming an absent tag did not load");
        assertEquals(0, absent.memberCount(loaded.full()),
            "a tag no pack defines is an empty set, so the group offers nothing and the table still rolls");
        assertTrue(absent.parts().tag().isPresent(),
            "the tag has to still BE a tag - resolved at read time is the bug this test is about");


        final LootGroup present = loaded.registry(ArmorPiecesRegistries.LOOT_GROUP).getValue(key("present"));
        assertNotNull(present, "the group naming a tag the mod does define did not load");
        assertTrue(present.memberCount(loaded.full()) > 0,
            "late resolution still has to FIND the members of a tag that is installed, or the "
                + "empty answer above means nothing");
    }
}
