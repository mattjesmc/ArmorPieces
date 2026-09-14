package com.mattjesmc.armorpieces.client;

import com.mattjesmc.armorpieces.client.mixin.CreativeModeTabsAccessor;
import com.mattjesmc.armorpieces.config.PartsSwitch;
import com.mattjesmc.armorpieces.network.PartsSwitchPayload;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;

/**
 * The client's half of {@link PartsSwitchPayload}: keeps what the server said, forgets it on the
 * way out, and has the creative tab rebuilt against it.
 */
@Environment(EnvType.CLIENT)
public final class ClientPartsSwitch {
    private ClientPartsSwitch() {
    }

    public static void register() {
        ClientPlayNetworking.registerGlobalReceiver(PartsSwitchPayload.TYPE, (payload, context) -> {
            PartsSwitch.told(payload.parts());
            // The tab was built for the last switch, or before this one arrived; the next look at
            // the creative screen builds it again. Nothing else on the client caches the answer.
            CreativeModeTabsAccessor.armorpieces$setCachedParameters(null);
        });
        ClientPlayConnectionEvents.DISCONNECT.register((handler, client) -> {
            PartsSwitch.told(null);
            CreativeModeTabsAccessor.armorpieces$setCachedParameters(null);
        });
    }
}
