package com.mattjesmc.armorpieces.client;

import com.mattjesmc.armorpieces.client.geometry.DecorationGeometryManager;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.pack.PackProblems;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents;
import net.minecraft.core.Registry;
import net.minecraft.core.RegistryAccess;

/**
 * The half of the pack report that only a client can see: a part with no art.
 *
 * <p>A part is two halves in two different packs - the datapack file that says it exists, and the
 * resource pack file that says what it looks like - and the halves are joined by
 * {@code asset_id}, a plain string nothing checks. Mistype it, or ship the datapack without the
 * resource pack, and the result is a part that can be crafted, applied, worn and seen by the server,
 * and draws nothing at all. That has always been silent: {@code DecorationGeometryManager.get}
 * answers null, the layer draws nothing, and the player concludes the mod is broken.
 *
 * <p>Run when the client joins a world, which is the first moment both halves are in hand: the
 * resource packs were read at startup, and the registry arrives with the join. Sweeping the whole
 * registry rather than warning as parts are drawn is deliberate - a pack author wants to hear about
 * the part nobody is wearing, and hear it once, rather than on the frame somebody finally wears it.
 */
public final class ClientPackAudit {
    private ClientPackAudit() {}

    public static void register() {
        ClientPlayConnectionEvents.JOIN.register((handler, sender, client) ->
            run(handler.registryAccess()));
        // A client's report is its own: it is about the resource packs THIS player has, and the
        // server's answer about datapacks has nothing to do with them. Leaving the world clears it,
        // so a second world does not inherit the first one's.
        ClientPlayConnectionEvents.DISCONNECT.register((handler, client) -> PackProblems.clear());
    }

    private static void run(final RegistryAccess registries) {
        final Registry<ArmorDecoration> parts =
            registries.lookupOrThrow(ArmorPiecesRegistries.ARMOR_DECORATION);
        final DecorationGeometryManager geometry = DecorationGeometryManager.instance();
        int missing = 0;
        for (final var part : parts.listElements().toList()) {
            if (geometry.get(part.value().assetId()) != null) {
                continue;
            }
            missing++;
            PackProblems.reported(part.key().identifier().toString(),
                "has no geometry: nothing supplies assets/" + part.value().assetId().getNamespace()
                    + "/armorpieces/decoration/" + part.value().assetId().getPath() + ".json, so the "
                    + "part can be applied and worn and draws nothing. Install the pack's resource "
                    + "pack half, or correct `asset_id`.");
        }
        if (missing > 0) {
            PackProblems.summarise("this client's resource packs");
        }
    }
}
