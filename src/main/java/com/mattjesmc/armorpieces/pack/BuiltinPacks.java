package com.mattjesmc.armorpieces.pack;

import com.mattjesmc.armorpieces.ArmorPieces;
import java.util.List;
import net.fabricmc.fabric.api.resource.v1.ResourceLoader;
import net.fabricmc.fabric.api.resource.v1.pack.PackActivationType;
import net.fabricmc.loader.api.FabricLoader;
import net.fabricmc.loader.api.ModContainer;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;

/**
 * The mod's own content, shipped as packs the jar carries rather than as resources of the jar.
 *
 * <p>{@code docs/plans/compatibility.md} section 5.3: the mod is the engine and every piece of content
 * is a pack, its own included. The three that used to be {@code src/main/resources} - knightly, court,
 * wayfarer, cut along the theme tags by {@code tools/split_mod.py} - live in {@code packs/} beside the
 * others and are copied into the jar at {@code resourcepacks/<theme>/} by {@code build.gradle}. They
 * are registered here as built-in packs, <b>on by default and switchable off</b>: a fresh install has
 * content, a server that wants none of it turns the pack off like any other (or names its ids in the
 * {@code parts} switch), and the pack's {@code former_ids} rebind every 0.3.0 save with nothing
 * downloaded.
 *
 * <p>One registration serves both halves: a built-in pack is one tree with {@code data/} and
 * {@code assets/} side by side, and no {@code pack.mcmeta} of its own, so the loader describes it for
 * whichever side is reading.
 */
public final class BuiltinPacks {
    /** The three themes, in the order they are listed to a player. */
    public static final List<String> THEMES = List.of("knightly", "court", "wayfarer");

    private BuiltinPacks() {
    }

    /** The namespace one of the three declares its content under. */
    public static String namespace(final String theme) {
        return ArmorPieces.MOD_ID + "_" + theme;
    }

    /**
     * Whether a namespace is the mod's own content - {@code armorpieces} itself (the engine's
     * fittings and cloths) or one of the three built-in packs. What {@code parts.mod_parts} in the
     * server owner's file switches off as one thing.
     */
    public static boolean isModContent(final String namespace) {
        if (namespace.equals(ArmorPieces.MOD_ID)) {
            return true;
        }
        for (final String theme : THEMES) {
            if (namespace.equals(namespace(theme))) {
                return true;
            }
        }
        return false;
    }

    /**
     * Registers the three, both halves at once: the loader's built-in pack is one tree with
     * {@code data/} and {@code assets/} side by side, served to whichever side is reading. Called from
     * the main entrypoint, before anything reads a pack.
     */
    public static void register() {
        final ModContainer container = FabricLoader.getInstance().getModContainer(ArmorPieces.MOD_ID).orElse(null);
        if (container == null) {
            return;
        }
        for (final String theme : THEMES) {
            final boolean found = ResourceLoader.registerBuiltinPack(
                Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, theme),  // -> resourcepacks/<theme>
                container,
                Component.translatable("pack.armorpieces_" + theme),
                PackActivationType.DEFAULT_ENABLED);
            if (!found) {
                ArmorPieces.LOGGER.warn("[Armor Pieces] built-in pack {} is not in this jar", theme);
            }
        }
    }
}
