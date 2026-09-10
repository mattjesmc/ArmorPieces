package com.mattjesmc.armorpieces.config;

import com.google.gson.JsonParser;
import com.mojang.serialization.JsonOps;

/**
 * The server owner's file, as a test can hand it over: {@code config/armorpieces-server.json}
 * written as a string and put in force without a disk or a server.
 *
 * <p>This lives in the config package because {@link ArmorPiecesServerConfig#apply} is
 * package-private and stays that way - the value moves through {@code load()} in a running game and
 * nowhere else. What a test needs is the other half of that: the settings in force are a static, so
 * anything reading them ({@link com.mattjesmc.armorpieces.loot.DecorationLootTables} is the whole
 * list today) cannot be asked a question about a configured server unless something can set them.
 *
 * <p>The file is handed over as JSON rather than as a record on purpose. It is the shape a server
 * owner actually types, it goes through the same {@link ArmorPiecesServerConfig#CODEC} their file
 * does - so a test asking about an override also proves the override could be written down - and it
 * reads, in the test that uses it, as the thing it is meant to be.
 */
public final class ServerConfigFixture {
    private ServerConfigFixture() {
    }

    /**
     * Puts {@code json} in force, exactly as if it were the file on disk.
     *
     * @param json the whole file, e.g. {@code {"chance_multiplier": 0.5}}. Every field is optional,
     *             as it is on disk.
     */
    public static void configure(final String json) {
        ArmorPiecesServerConfig.apply(
            ArmorPiecesServerConfig.CODEC.parse(JsonOps.INSTANCE, JsonParser.parseString(json))
                .getOrThrow(message -> new AssertionError("the fixture's own config is unreadable: "
                    + message + "\n" + json)));
    }

    /** Back to a server whose owner has touched nothing. Belongs in an {@code @AfterEach}. */
    public static void reset() {
        ArmorPiecesServerConfig.apply(ArmorPiecesServerConfig.DEFAULT);
    }
}
