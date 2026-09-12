package com.mattjesmc.armorpieces.pack;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import java.util.List;
import java.util.Map;
import net.fabricmc.fabric.api.resource.ResourceManagerHelper;
import net.fabricmc.fabric.api.resource.SimpleSynchronousResourceReloadListener;
import net.minecraft.core.Registry;
import net.minecraft.resources.FileToIdConverter;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.packs.PackType;
import net.minecraft.server.packs.resources.Resource;
import net.minecraft.server.packs.resources.ResourceManager;

/**
 * Two packs that define the same piece, said out loud.
 *
 * <p>Overriding is how packs work and is often exactly what somebody meant - a pack that restyles the
 * mod's own plume writes a file at the mod's own id, and the topmost pack wins. What makes it worth a
 * line in the report is the case where nobody meant it: two packs from two authors, installed
 * together, that happen to have named a piece the same thing. Then one author's work is simply not in
 * the game, with nothing anywhere to say so, and the player who reports "the coral crown looks wrong"
 * is describing a file that never loaded.
 *
 * <p>{@code tools/check_additive.py} answers this for the packs THIS repository ships. It cannot
 * answer it for a player's pack folder, which is a set of packs nothing in this repository has ever
 * seen - and that is the only set where a third party's collision can happen.
 *
 * <p>A resource reload listener rather than a hook in the registry loader, because the loader sees one
 * resource per id: {@code getResource} answers with the topmost, and the pack underneath it leaves no
 * trace. {@code getResourceStack} is what remembers there was one. This runs on the data reload, which
 * is every world load and every {@code /reload}, and is a walk of five directories.
 */
public final class PackOverrides implements SimpleSynchronousResourceReloadListener {
    private static final Identifier ID =
        Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "pack_overrides");

    private PackOverrides() {}

    public static void register() {
        ResourceManagerHelper.get(PackType.SERVER_DATA).registerReloadListener(new PackOverrides());
    }

    @Override
    public Identifier getFabricId() {
        return ID;
    }

    @Override
    public void onResourceManagerReload(final ResourceManager resources) {
        for (final ResourceKey<? extends Registry<?>> registry : ArmorPiecesRegistries.datapackRegistries()) {
            final FileToIdConverter files = FileToIdConverter.registry(registry);
            for (final Map.Entry<Identifier, List<Resource>> entry
                : files.listMatchingResourceStacks(resources).entrySet()) {
                if (entry.getValue().size() < 2) {
                    continue;
                }
                // Top of the stack is the one that won; the rest are what a player installed and
                // will never see. Both ends are named, because which of them is the mistake is the
                // authors' business and not the mod's.
                final List<Resource> stack = entry.getValue();
                final Resource winner = stack.getLast();
                PackProblems.reported(files.fileToId(entry.getKey()).toString(),
                    "is defined by " + stack.size() + " packs (" + names(stack) + "). Only "
                        + winner.sourcePackId() + " is in the game; the others are overridden, "
                        + "which is intended when a pack restyles another's piece and is a name "
                        + "collision when it is not.");
            }
        }
    }

    private static String names(final List<Resource> stack) {
        return stack.stream().map(Resource::sourcePackId).reduce((a, b) -> a + ", then " + b).orElse("");
    }
}
