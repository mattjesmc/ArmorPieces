package com.mattjesmc.armorpieces.identity;

import com.mattjesmc.armorpieces.ArmorPieces;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import org.jspecify.annotations.Nullable;

/**
 * Wires the identity system into the server's life, and says the one thing a player needs told.
 *
 * <p>Three jobs, and they are separate on purpose.
 *
 * <ul>
 *   <li><b>The index.</b> {@link Rebind} is rebuilt whenever the registries are - world load and
 *       every {@code /reload} - because a saved item can only be read after one of those, and a part
 *       that arrives with a newly installed pack has to become findable without a restart.</li>
 *   <li><b>The marker.</b> {@link ArmorPiecesState} stamps the running version over the world's, so
 *       the advisory can say the world CHANGED rather than just that something is absent.</li>
 *   <li><b>The advisory.</b> Sent when something is actually missing, not when the world opens.</li>
 * </ul>
 *
 * <p><b>Why the message is not a first-launch warning.</b> Reading a saved item is lazy: at the moment
 * a world opens, nothing has been decoded, so nothing is yet known to be missing. A message fired
 * there would be noise for the world with no decorated armor and premature for the chest that loads an
 * hour later. So the trigger is the first real miss, and the version marker only decides whether the
 * message can add "this world was last played on 0.3.0".
 *
 * <p><b>And why it is advisory rather than a deadline.</b> Nothing is lost by ignoring it. The armor
 * keeps its parts, they come back the day the pack is installed, and no world is refused - a mod that
 * will not open a world is a mod that gets a world deleted.
 */
public final class Compatibility {
    private static @Nullable MinecraftServer server;
    private static @Nullable ArmorPiecesState state;

    /** Who has already been told this session. Cleared with the server. */
    private static final Set<UUID> told = new HashSet<>();

    private Compatibility() {}

    /** Registers everything. Called once, from the mod initializer. */
    public static void register() {
        // STARTING, not STARTED: the registries exist by now and the levels do not, so the index is
        // built before the first chunk or player file can be read.
        ServerLifecycleEvents.SERVER_STARTING.register(starting -> {
            server = starting;
            Rebind.rebuild(starting.registryAccess());
        });
        // STARTED, because the marker lives in the overworld's data storage and the overworld is
        // what STARTING does not have yet.
        ServerLifecycleEvents.SERVER_STARTED.register(started -> state = ArmorPiecesState.open(started));
        // A pack installed into a running server, or removed from one. END rather than START: the
        // new registries are what the index has to be built from.
        ServerLifecycleEvents.END_DATA_PACK_RELOAD.register((reloaded, resources, success) -> {
            if (success) {
                Rebind.rebuild(reloaded.registryAccess());
            }
        });
        ServerLifecycleEvents.SERVER_STOPPED.register(stopped -> {
            server = null;
            state = null;
            told.clear();
            Rebind.clear();
            Rebind.forgetMisses();
        });
        // Somebody joining a world that is already short of a pack, and somebody standing in it when
        // the first affected chunk loads. Both, because either can be the one who notices.
        ServerPlayConnectionEvents.JOIN.register((handler, sender, joined) -> advise(handler.player));
        Rebind.onNewMiss(miss -> {
            final MinecraftServer running = server;
            if (running == null) {
                return;
            }
            // A miss is recorded on whatever thread loaded the chunk. Chat is the server thread's.
            running.execute(() -> running.getPlayerList().getPlayers().forEach(Compatibility::advise));
        });
    }

    /**
     * Tells one player, once per session, that this world names content they do not have.
     *
     * <p>Only players who could do something about it: a server's ordinary members cannot install a
     * datapack, and telling them would be handing out a worry with no action attached to it.
     */
    private static void advise(final ServerPlayer player) {
        if (!Rebind.anyMissing() || !told.add(player.getUUID())) {
            return;
        }
        if (!Commands.LEVEL_GAMEMASTERS.check(player.permissions())) {
            told.remove(player.getUUID());
            return;
        }
        final ArmorPiecesState opened = state;
        if (opened != null) {
            opened.upgradedFrom().ifPresent(previous -> player.sendSystemMessage(
                Component.translatable("armorpieces.compat.upgraded", previous, ArmorPiecesState.running())
                    .withStyle(ChatFormatting.GRAY)));
        }
        player.sendSystemMessage(Component.translatable(
            "armorpieces.compat.missing", Rebind.misses().size()).withStyle(ChatFormatting.YELLOW));
        player.sendSystemMessage(
            Component.translatable("armorpieces.compat.advice").withStyle(ChatFormatting.GRAY));
        ArmorPieces.LOGGER.info("[Armor Pieces] Told {} that {} piece ids are not installed.",
            player.getGameProfile().name(), Rebind.misses().size());
    }
}
