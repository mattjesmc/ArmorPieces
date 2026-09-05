package com.mattjesmc.armorpieces.decoration;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.cloth.Cloth;
import com.mattjesmc.armorpieces.decoration.effect.DecorationEffect;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.skin.ArmorSkin;
import com.mojang.serialization.MapCodec;
import net.fabricmc.fabric.api.event.registry.DynamicRegistries;
import net.fabricmc.fabric.api.event.registry.FabricRegistryBuilder;
import net.minecraft.core.Registry;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;

/** The mod's registries: four loaded from datapacks, two filled in by code. */
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
     * Fittings - the places on a part that take a second material - loaded from
     * {@code data/<ns>/armorpieces/fitting/}. Synced for the same reason parts are: an item carries
     * its fittings by id, and the client colours and draws from them.
     */
    public static final ResourceKey<Registry<Fitting>> FITTING =
        ResourceKey.createRegistryKey(Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "fitting"));

    /**
     * Armor skins - the armor's own texture, loaded from {@code data/<ns>/armorpieces/armor_skin/}.
     *
     * <p>Synced, and for a reason of its own: a skin is nothing but art, and it is the CLIENT that
     * bakes it. The render layer reads the skin off the worn stack and looks its master sheets up by
     * the id this registry gives, so a client that could not name the skin would draw plain armor
     * where the server thinks there is a fluted harness.
     */
    public static final ResourceKey<Registry<ArmorSkin>> ARMOR_SKIN =
        ResourceKey.createRegistryKey(Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "armor_skin"));

    /**
     * Cloths - a garment worn over the armor's texture, loaded from
     * {@code data/<ns>/armorpieces/cloth/}. Synced for the reason skins are: the art is a cut mask
     * the CLIENT composites, found by the id this registry gives, and a client that could not name
     * the garment would draw bare armor where the server thinks there is a tabard.
     */
    public static final ResourceKey<Registry<Cloth>> CLOTH =
        ResourceKey.createRegistryKey(Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "cloth"));

    /**
     * Effect types - the kinds of behaviour a part is allowed to have.
     *
     * <p>The registries here that are STATIC rather than datapack-loaded exist for the reason vanilla
     * has for {@code BuiltInRegistries.ENCHANTMENT_ENTITY_EFFECT_TYPE}: their values are
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

    /**
     * Fitting types - the kinds of second material a fitting can be. Static, as effect types are,
     * and for the same reason; {@link Fitting#DIRECT_CODEC} dispatches through it.
     */
    public static final Registry<MapCodec<? extends Fitting>> FITTING_TYPES =
        FabricRegistryBuilder.<MapCodec<? extends Fitting>>create(
                ResourceKey.createRegistryKey(
                    Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "fitting_type")))
            .buildAndRegister();

    private ArmorPiecesRegistries() {}

    public static void register() {
        // Fittings first: a part refers to fittings by id, and although the loader resolves
        // cross-registry references whatever the order, reading the dependency before the dependant
        // is the order a reader expects.
        DynamicRegistries.registerSynced(FITTING, Fitting.DIRECT_CODEC);
        DynamicRegistries.registerSynced(ARMOR_DECORATION, ArmorDecoration.DIRECT_CODEC);
        // Skins depend on nothing and nothing depends on them: a skin is the armor's own texture,
        // and neither a part nor a fitting has an opinion about it. Last, therefore.
        DynamicRegistries.registerSynced(ARMOR_SKIN, ArmorSkin.DIRECT_CODEC);
        // Cloths, likewise, depend on nothing - a garment is cut out of the armor's own net and
        // has no opinion about what it is worn over.
        DynamicRegistries.registerSynced(CLOTH, Cloth.DIRECT_CODEC);
    }
}
