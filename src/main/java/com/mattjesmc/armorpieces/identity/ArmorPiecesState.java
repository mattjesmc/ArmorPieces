package com.mattjesmc.armorpieces.identity;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.Optional;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.resources.Identifier;
import net.minecraft.server.MinecraftServer;
import net.minecraft.util.datafix.DataFixTypes;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.level.saveddata.SavedDataType;
import org.jspecify.annotations.Nullable;

/**
 * What this world remembers about Armor Pieces: the version that last opened it.
 *
 * <p>One field, and it exists to make one message honest. A player whose armor has stopped showing
 * its parts needs to know two different things depending on why: that a pack is missing (which
 * {@link Rebind}'s tally can say on its own) and that the mod's contents CHANGED under them, which
 * nothing else can say - a world opened on 0.4.0 for the first time looks exactly like one that has
 * always been on it.
 *
 * <p>It deliberately does NOT drive the warning's timing. Reading a saved item is lazy: at the moment
 * the world opens, nothing has been decoded and nothing is known to be missing, so a message fired
 * here would either be noise (for the world with no decorated armor) or premature (for the chest that
 * loads an hour later). The version says <i>why</i>; the tally says <i>whether</i>. See
 * {@code docs/plans/compatibility.md} §4.4.
 */
public class ArmorPiecesState extends SavedData {
    /**
     * {@code LEVEL} because vanilla offers nothing neutral: every {@link DataFixTypes} names some
     * existing structure. Its fixes key on paths this data does not have, so they find nothing.
     */
    public static final SavedDataType<ArmorPiecesState> TYPE = new SavedDataType<>(
        Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "state"),
        ArmorPiecesState::new,
        RecordCodecBuilder.create(i -> i.group(
                Codec.STRING.optionalFieldOf("version").forGetter(state -> Optional.ofNullable(state.version))
            ).apply(i, version -> new ArmorPiecesState(version.orElse(null)))),
        DataFixTypes.LEVEL);

    /** The version that last opened this world, or null for one that predates this field. */
    private @Nullable String version;

    /** The version this world was opened on BEFORE now, if it was a different one. Not saved. */
    private @Nullable String upgradedFrom;

    private ArmorPiecesState() {
        this(null);
    }

    private ArmorPiecesState(final @Nullable String version) {
        this.version = version;
    }

    /** The running mod's version, as its own metadata gives it. */
    public static String running() {
        return FabricLoader.getInstance().getModContainer(ArmorPieces.MOD_ID)
            .map(container -> container.getMetadata().getVersion().getFriendlyString())
            .orElse("unknown");
    }

    /**
     * Reads the world's marker and stamps the running version over it.
     *
     * <p>Called once, when the server starts. A world whose marker is absent or different remembers
     * what it was, for the one line the advisory adds.
     */
    public static ArmorPiecesState open(final MinecraftServer server) {
        final ArmorPiecesState state =
            server.overworld().getDataStorage().computeIfAbsent(TYPE);
        final String running = running();
        if (!running.equals(state.version)) {
            state.upgradedFrom = state.version;
            state.version = running;
            state.setDirty();
        }
        return state;
    }

    /**
     * The version this world was last opened on, when that is not the running one - so "was last
     * played on 0.3.0" is only ever said to a world that really was.
     *
     * <p>Empty for a world that has never been opened by a version that wrote the marker, which is
     * the honest answer: it might have been 0.3.0 and it might have been created yesterday by a
     * version with no marker, and guessing between them would put a wrong sentence in front of a
     * player.
     */
    public Optional<String> upgradedFrom() {
        return Optional.ofNullable(this.upgradedFrom);
    }
}
