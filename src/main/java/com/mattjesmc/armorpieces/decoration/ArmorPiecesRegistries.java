package com.mattjesmc.armorpieces.decoration;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.decoration.effect.DecorationEffect;
import com.mojang.serialization.MapCodec;
import net.fabricmc.fabric.api.event.registry.DynamicRegistries;
import net.fabricmc.fabric.api.event.registry.FabricRegistryBuilder;
import net.minecraft.core.Registry;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;

/** The mod's registries: one loaded from datapacks, one filled in by code. */
public final class ArmorPiecesRegistries {
    /**
     * Decorative parts, loaded from {@code data/<ns>/armorpieces/armor_decoration/}.
     *
     * <p>Registered as SYNCED because the client has to draw these: the render layer resolves a
     * {@code Holder<ArmorDecoration>} straight off an item component to find its geometry and
     * texture. An unsynced registry would leave a client that joined a server with parts it cannot
     * name or draw.
     */
    public static final ResourceKey<Registry<ArmorDecoration>> ARMOR_DECORATION =
        ResourceKey.createRegistryKey(Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "armor_decoration"));

    /**
     * Effect types - the kinds of behaviour a part is allowed to have.
     *
     * <p>The one registry here that is STATIC rather than datapack-loaded, and the reason is the same
     * one vanilla has for {@code BuiltInRegistries.ENCHANTMENT_ENTITY_EFFECT_TYPE}: its values are
     * {@link MapCodec}s, which is to say code, and code does not come out of a zip file. A pack picks
     * an effect and configures it; a mod is what puts the effect on the shelf.
     *
     * <p>Created here as a field rather than inside {@link #register()} so that it exists before any
     * codec that dispatches through it is built - {@link DecorationEffect#CODEC} reads it during its
     * own class initialisation, which happens the first time a part is decoded.
     */
    public static final Registry<MapCodec<? extends DecorationEffect>> DECORATION_EFFECT_TYPES =
        FabricRegistryBuilder.<MapCodec<? extends DecorationEffect>>create(
                ResourceKey.createRegistryKey(
                    Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "decoration_effect_type")))
            .buildAndRegister();

    private ArmorPiecesRegistries() {}

    public static void register() {
        DynamicRegistries.registerSynced(ARMOR_DECORATION, ArmorDecoration.DIRECT_CODEC);
    }
}
