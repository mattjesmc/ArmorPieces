package com.mattjesmc.armorpieces.network;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.config.ArmorPiecesServerConfig;
import com.mattjesmc.armorpieces.config.PartsSwitch;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.Identifier;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;

/**
 * The server's {@link PartsSwitch}, told to a client: on join, and again to everyone after a
 * datapack reload, which is when the file is re-read.
 *
 * <p>The one packet this mod sends. It exists because the creative tab is built on the client from
 * the client's own registries, and a server-side setting about what is offered has to reach it or
 * the tab would offer everything. The client keeps what it was told in {@link PartsSwitch#told} and
 * forgets it on disconnect; nothing else about the config travels, because nothing else is shown.
 *
 * <p>Only sent to a client that has registered the channel - one running this mod, which every
 * client on a server with it is.
 */
public record PartsSwitchPayload(PartsSwitch parts) implements CustomPacketPayload {
    public static final Type<PartsSwitchPayload> TYPE =
        new Type<>(Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "parts_switch"));

    public static final StreamCodec<RegistryFriendlyByteBuf, PartsSwitchPayload> STREAM_CODEC =
        PartsSwitch.STREAM_CODEC.map(PartsSwitchPayload::new, PartsSwitchPayload::parts);

    @Override
    public Type<PartsSwitchPayload> type() {
        return TYPE;
    }

    /** Registers the payload and the two moments it is sent. Server side; the client has its own. */
    public static void register() {
        PayloadTypeRegistry.clientboundPlay().register(TYPE, STREAM_CODEC);
        ServerPlayConnectionEvents.JOIN.register((handler, sender, server) -> tell(handler.getPlayer()));
        ServerLifecycleEvents.END_DATA_PACK_RELOAD.register((server, resources, success) -> tellAll(server));
    }

    private static void tell(final ServerPlayer player) {
        if (ServerPlayNetworking.canSend(player, TYPE)) {
            ServerPlayNetworking.send(player, new PartsSwitchPayload(ArmorPiecesServerConfig.get().parts()));
        }
    }

    private static void tellAll(final MinecraftServer server) {
        for (final ServerPlayer player : server.getPlayerList().getPlayers()) {
            tell(player);
        }
    }
}
