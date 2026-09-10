package com.mattjesmc.armorpieces.config;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.loot.LootGroup;
import com.mojang.serialization.Codec;
import com.mojang.serialization.JsonOps;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.util.ExtraCodecs;
import net.minecraft.world.level.storage.loot.LootTable;
import org.jspecify.annotations.Nullable;

/**
 * The settings a SERVER OWNER edits - {@code config/armorpieces-server.json}. Today it is one
 * subject: how much of this mod the world hands out.
 *
 * <p>This is the file {@link ArmorPiecesConfig} says in its own javadoc a server-side setting would
 * need. The two are deliberately separate rather than one file with a server section: that one is
 * read on the client and only ever moves pixels, this one is read on the logical server and changes
 * what a chest contains, and mixing them would put a setting that must not desync in a file a
 * client is free to edit.
 *
 * <h2>What it is for</h2>
 *
 * <p>Loot content is pack data - a {@link LootGroup} says a stronghold offers a knightly part one
 * time in eight, and that is a content decision belonging to whoever wrote the parts. But "parts are
 * too common on my server" is not a content decision, and before this file the only way to say it
 * was to author a datapack overriding somebody else's group. So a pack author still authors; a
 * server owner OVERRIDES, keyed by the group's id, and neither has to edit the other's files.
 *
 * <h2>Shape on disk</h2>
 *
 * <pre>{@code
 * { "enabled": true,
 *   "chance_multiplier": 1.0,
 *   "groups": {
 *     "armorpieces:knightly": {
 *       "chance": 0.05,
 *       "weight": 2,
 *       "add": [ "somemod:chests/vault", { "table": "somemod:chests/deep_vault", "chance": 0.3 } ],
 *       "remove": [ "minecraft:chests/desert_pyramid" ]
 *     },
 *     "armorpieces:court": { "enabled": false }
 *   } }
 * }</pre>
 *
 * <p>As with the client file, every field is optional and the file is rewritten after a successful
 * parse, so a key added by a later version appears in an existing server's file rather than only in
 * a fresh one. A file that does not parse is left exactly as it is and the defaults are used: a
 * typo costs a log line, never the rest of the settings.
 *
 * <h2>When it is read</h2>
 *
 * <p>At mod initialization, and again at the START of every datapack reload - which is the only
 * moment that matters, because loot tables are built as the datapacks load and
 * {@link com.mattjesmc.armorpieces.loot.DecorationLootTables} reads these numbers as it does so. So
 * {@code /reload} picks up an edit to this file and there is no second command that has to be
 * remembered.
 *
 * @param groups           the overrides, by loot group id. A group not named here is used exactly as
 *                         its pack wrote it.
 * @param chanceMultiplier scales every chance the mod ends up putting on a table, groups and the
 *                         parts' own {@code loot} rows alike. The one knob for "half as much of this
 *                         mod" without naming a single group; 0 turns the mod's loot off as surely
 *                         as {@code enabled} does, and 1 changes nothing.
 * @param enabled          whether the mod adds anything to any loot table at all. The off switch,
 *                         for a server that wants parts crafted and never found.
 */
public record ArmorPiecesServerConfig(
    boolean enabled,
    float chanceMultiplier,
    Map<ResourceKey<LootGroup>, ArmorPiecesServerConfig.GroupOverride> groups
) {
    public static final ArmorPiecesServerConfig DEFAULT = new ArmorPiecesServerConfig(true, 1.0f, Map.of());

    public static final Codec<ArmorPiecesServerConfig> CODEC = RecordCodecBuilder.create(i ->
        i.group(
            Codec.BOOL.optionalFieldOf("enabled", DEFAULT.enabled())
                .forGetter(ArmorPiecesServerConfig::enabled),
            // Above 1 is allowed on purpose: a server that wants parts twice as common has as much
            // right to say so as one that wants them halved, and the product is clamped to 1 where
            // it is used rather than refused here.
            Codec.floatRange(0.0f, 100.0f).optionalFieldOf("chance_multiplier", DEFAULT.chanceMultiplier())
                .forGetter(ArmorPiecesServerConfig::chanceMultiplier),
            Codec.unboundedMap(ResourceKey.codec(ArmorPiecesRegistries.LOOT_GROUP), GroupOverride.CODEC)
                .optionalFieldOf("groups", Map.of())
                .forGetter(ArmorPiecesServerConfig::groups)
        ).apply(i, ArmorPiecesServerConfig::new));

    /**
     * The codec the file is WRITTEN with. Every field is mandatory here, which is the whole point:
     * {@link #CODEC}'s optional fields are omitted on encode when they hold the default, so a server
     * that has changed nothing would be handed an empty {@code {}} and no way to discover a single
     * knob. Reading stays forgiving; writing shows the whole dashboard at the values in force.
     *
     * <p>Package-private rather than private so {@code ConfigCodecTest} can hold it to the rule
     * that costs nothing to break: a field added to {@link #CODEC} has to be added here too.
     */
    static final Codec<ArmorPiecesServerConfig> WRITE_CODEC = RecordCodecBuilder.create(i ->
        i.group(
            Codec.BOOL.fieldOf("enabled").forGetter(ArmorPiecesServerConfig::enabled),
            Codec.floatRange(0.0f, 100.0f).fieldOf("chance_multiplier")
                .forGetter(ArmorPiecesServerConfig::chanceMultiplier),
            Codec.unboundedMap(ResourceKey.codec(ArmorPiecesRegistries.LOOT_GROUP), GroupOverride.CODEC)
                .fieldOf("groups").forGetter(ArmorPiecesServerConfig::groups)
        ).apply(i, ArmorPiecesServerConfig::new));

    private static final String FILE_NAME = ArmorPieces.MOD_ID + "-server.json";
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();

    private static ArmorPiecesServerConfig current = DEFAULT;

    /** The settings in force. Defaults until {@link #register()} has run. */
    public static ArmorPiecesServerConfig get() {
        return current;
    }

    /**
     * The settings in force, replaced. Package-private, like {@link #WRITE_CODEC}, and for the same
     * kind of reason: {@code ServerConfigFixture} in the tests is the only caller.
     *
     * <p>A loot table is assembled against whatever {@link #get()} holds at that moment, so a test
     * that cannot say "on a server whose owner halved the multiplier" cannot ask the question at
     * all - and the alternative, writing {@code config/armorpieces-server.json} into whatever
     * directory the test JVM calls home and reading it back, tests the file rather than the rule.
     * Nothing in the game calls this: {@link #load()} is how the value moves in a running server.
     */
    static void apply(final ArmorPiecesServerConfig config) {
        current = config;
    }

    /**
     * Reads the file now and again at the start of every datapack reload.
     *
     * <p>The reload hook is what makes the file live. Loot tables are assembled as the packs load,
     * so a config read after the reload would be a config that takes effect one reload late - the
     * classic way for a knob to look broken.
     */
    public static void register() {
        load();
        ServerLifecycleEvents.START_DATA_PACK_RELOAD.register((server, resources) -> load());
    }

    /**
     * The override for one group, or null if the server has nothing to say about it.
     *
     * @param group the group's registry key, which is its file's id.
     */
    public @Nullable GroupOverride override(final ResourceKey<LootGroup> group) {
        return this.groups.get(group);
    }

    /**
     * {@code chance} after {@link #chanceMultiplier}, clamped into 0..1.
     *
     * <p>Clamped rather than refused because the multiplier is a wish about the whole mod and a
     * table that was already generous is not an error - it just cannot be more than certain.
     */
    public float scale(final float chance) {
        if (!this.enabled) {
            return 0.0f;
        }
        return Math.clamp(chance * this.chanceMultiplier, 0.0f, 1.0f);
    }

    /**
     * What a server owner may say about one loot group.
     *
     * <p>Everything here is optional and everything absent means "as the pack wrote it", so the
     * smallest useful override is one key. The parts, skins, cloths and fittings a group offers are
     * NOT overridable, on purpose: those are the group's content and a server that wants different
     * members wants a different group, which is a datapack. What is overridable is the dial - how
     * often, how strongly, and in which tables.
     *
     * @param enabled whether the group contributes at all. {@code false} is how a server drops one
     *                theme without touching the other five.
     * @param chance  replaces the group's chance for EVERY table it names, including the ones its
     *                file gave a chance of their own. The server owner's number is the last word;
     *                a table that should keep a number of its own is named again in {@link #add}.
     * @param weight  replaces the group's weight - what its members are worth against the other
     *                groups sharing a table.
     * @param add     tables this group also reaches. The same entry shape a group file uses, so a
     *                bare id takes the group's chance and an object may carry its own. This is how
     *                a modded container joins a theme with no datapack at all.
     * @param remove  tables this group stops reaching. Applied after {@link #add}, so a table in
     *                both is removed.
     */
    public record GroupOverride(
        boolean enabled,
        Optional<Float> chance,
        Optional<Integer> weight,
        List<LootGroup.TableEntry> add,
        List<ResourceKey<LootTable>> remove
    ) {
        public static final Codec<GroupOverride> CODEC = RecordCodecBuilder.create(i ->
            i.group(
                Codec.BOOL.optionalFieldOf("enabled", true).forGetter(GroupOverride::enabled),
                Codec.floatRange(0.0f, 1.0f).optionalFieldOf("chance").forGetter(GroupOverride::chance),
                ExtraCodecs.POSITIVE_INT.optionalFieldOf("weight").forGetter(GroupOverride::weight),
                LootGroup.TableEntry.CODEC.listOf().optionalFieldOf("add", List.of()).forGetter(GroupOverride::add),
                ResourceKey.codec(Registries.LOOT_TABLE).listOf().optionalFieldOf("remove", List.of())
                    .forGetter(GroupOverride::remove)
            ).apply(i, GroupOverride::new));

        public GroupOverride {
            add = List.copyOf(add);
            remove = List.copyOf(remove);
        }

        /** Whether this override says anything at all beyond the defaults. */
        public boolean isTrivial() {
            return this.enabled
                && this.chance.isEmpty()
                && this.weight.isEmpty()
                && this.add.isEmpty()
                && this.remove.isEmpty();
        }
    }

    private static void load() {
        final Path path = FabricLoader.getInstance().getConfigDir().resolve(FILE_NAME);
        if (!Files.isRegularFile(path)) {
            current = DEFAULT;
            write(path, current);
            return;
        }

        final ArmorPiecesServerConfig parsed;
        try {
            final JsonElement json = JsonParser.parseString(Files.readString(path, StandardCharsets.UTF_8));
            parsed = CODEC.parse(JsonOps.INSTANCE, json).getOrThrow();
        } catch (final IOException | RuntimeException failure) {
            // Left on disk untouched - the owner gets their file back the moment they fix the typo.
            ArmorPieces.LOGGER.warn("[Armor Pieces] {} could not be read ({}); using defaults.",
                path, failure.getMessage());
            current = DEFAULT;
            return;
        }

        current = parsed;
        write(path, current);
    }

    private static void write(final Path path, final ArmorPiecesServerConfig config) {
        try {
            final JsonElement json = WRITE_CODEC.encodeStart(JsonOps.INSTANCE, config).getOrThrow();
            Files.createDirectories(path.getParent());
            Files.writeString(path, GSON.toJson(json) + "\n", StandardCharsets.UTF_8);
        } catch (final IOException | RuntimeException failure) {
            ArmorPieces.LOGGER.warn("[Armor Pieces] {} could not be written ({}); "
                + "settings are in effect but will not persist.", path, failure.getMessage());
        }
    }
}
