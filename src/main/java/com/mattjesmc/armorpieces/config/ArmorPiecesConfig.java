package com.mattjesmc.armorpieces.config;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.mattjesmc.armorpieces.ArmorPieces;
import com.mojang.serialization.Codec;
import com.mojang.serialization.JsonOps;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import net.fabricmc.loader.api.FabricLoader;

/**
 * The mod's settings, as a player edits them - {@code config/armorpieces.json}.
 *
 * <p>Everything a datapack or a resource pack decides is NOT here. Which parts exist, what they are
 * made of, where they hang and how they are crafted are all pack data, because they are content and
 * they belong to the world, not to the player reading the screen. This file is for the handful of
 * choices that are genuinely the player's own and cannot break anyone else's game: taste, and
 * whether a piece of drawing happens at all.
 *
 * <p>Which is why the file is read on the CLIENT and by the client alone. A setting that changed
 * what an item does would have to be synchronised or it would desync a server, and no such setting
 * is in here; every option below moves pixels and nothing else. Should a server-side one ever be
 * wanted it needs its own file and its own load point in {@link ArmorPieces}, not a new field in
 * this record.
 *
 * <h2>Shape on disk</h2>
 *
 * <p>Every field is an {@code optionalFieldOf}, so a file missing a key is not an error - it takes
 * the default and gets the key written back on the next launch. That is what lets a new option
 * appear in an existing player's file instead of only in a fresh one, and it is why {@link #load()}
 * rewrites the file after a successful parse. A file that does NOT parse is left exactly as it is:
 * a typo should cost the player a log line, not the rest of their settings.
 *
 * @param firstPersonParts whether parts on the arm - pauldrons and vambraces - are drawn on the
 *                         first-person hand as well as on the body. They sit close to the camera and
 *                         fill a real share of the screen, which is the whole point for some players
 *                         and unbearable for others.
 */
public record ArmorPiecesConfig(boolean firstPersonParts) {
    public static final ArmorPiecesConfig DEFAULT = new ArmorPiecesConfig(true);

    public static final Codec<ArmorPiecesConfig> CODEC = RecordCodecBuilder.create(instance ->
        instance.group(
            Codec.BOOL.optionalFieldOf("first_person_parts", DEFAULT.firstPersonParts())
                .forGetter(ArmorPiecesConfig::firstPersonParts)
        ).apply(instance, ArmorPiecesConfig::new));

    /**
     * The codec the file is WRITTEN with, mandatory where {@link #CODEC} is optional. An optional
     * field is omitted on encode when it holds its default, so a player who has changed nothing was
     * being handed an empty {@code {}} - a settings file with no settings visible in it, which is
     * the opposite of what the round-trip below is for.
     *
     * <p>Package-private rather than private so {@code ConfigCodecTest} can hold it to the rule
     * that costs nothing to break: a field added to {@link #CODEC} has to be added here too.
     */
    static final Codec<ArmorPiecesConfig> WRITE_CODEC = RecordCodecBuilder.create(instance ->
        instance.group(
            Codec.BOOL.fieldOf("first_person_parts").forGetter(ArmorPiecesConfig::firstPersonParts)
        ).apply(instance, ArmorPiecesConfig::new));

    private static final String FILE_NAME = ArmorPieces.MOD_ID + ".json";
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();

    private static ArmorPiecesConfig current = DEFAULT;

    /**
     * The settings in force.
     *
     * <p>Returns the defaults until {@link #load()} has run, so a caller that somehow renders before
     * the client initializer gets the shipped behaviour rather than a null.
     */
    public static ArmorPiecesConfig get() {
        return current;
    }

    /**
     * Reads the file, or writes one if there is none. Called once, from the client initializer.
     *
     * <p>Never throws. A config file is the one input a player edits by hand, so every way it can be
     * wrong - absent, malformed, unreadable, a directory - ends in the defaults and a log line rather
     * than a crash on a mod that would otherwise have worked.
     */
    public static void load() {
        final Path path = FabricLoader.getInstance().getConfigDir().resolve(FILE_NAME);
        if (!Files.isRegularFile(path)) {
            current = DEFAULT;
            write(path, current);
            return;
        }

        final ArmorPiecesConfig parsed;
        try {
            final JsonElement json = JsonParser.parseString(Files.readString(path, StandardCharsets.UTF_8));
            parsed = CODEC.parse(JsonOps.INSTANCE, json).getOrThrow();
        } catch (final IOException | RuntimeException failure) {
            // Left on disk untouched - see the class doc. The player gets their own file back the
            // moment they fix the typo.
            ArmorPieces.LOGGER.warn("[Armor Pieces] {} could not be read ({}); using defaults.",
                path, failure.getMessage());
            current = DEFAULT;
            return;
        }

        current = parsed;
        // Round-trips the parsed settings so a key the player's file predates appears in it.
        write(path, current);
    }

    private static void write(final Path path, final ArmorPiecesConfig config) {
        try {
            final JsonElement json = WRITE_CODEC.encodeStart(JsonOps.INSTANCE, config).getOrThrow();
            Files.createDirectories(path.getParent());
            Files.writeString(path, GSON.toJson(json) + "\n", StandardCharsets.UTF_8);
        } catch (final IOException | RuntimeException failure) {
            // A read-only config directory is a real thing on a locked-down machine. The settings in
            // memory are still good; only the player's ability to edit them is lost.
            ArmorPieces.LOGGER.warn("[Armor Pieces] {} could not be written ({}); "
                + "settings are in effect but will not persist.", path, failure.getMessage());
        }
    }
}
