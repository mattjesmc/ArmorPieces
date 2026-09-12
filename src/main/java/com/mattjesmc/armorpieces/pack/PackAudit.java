package com.mattjesmc.armorpieces.pack;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationLoot;
import com.mattjesmc.armorpieces.identity.Tolerant;
import com.mattjesmc.armorpieces.item.DecorationTemplateItem;
import com.mattjesmc.armorpieces.loot.LootGroup;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.Registry;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.CraftingInput;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.ShapedRecipe;
import net.minecraft.world.level.storage.loot.LootTable;

/**
 * Everything wrong with a pack that no single file's codec can see.
 *
 * <p>The codecs and {@code RegistryLoadTaskMixin} between them cover the two buckets a load can act
 * on - the field that was dropped, the element that was skipped. This is the third bucket, and the
 * only one that needs the whole world in hand at once: content that is perfectly legal, loaded
 * without complaint, and cannot do the thing it was written to do.
 *
 * <ul>
 *   <li>a part with no socket left, which nothing can ever apply;</li>
 *   <li>a {@code loot} row or a group naming a loot table no pack defines, which is a part that will
 *       never be found in the world however generous its chance;</li>
 *   <li>a recipe handing out a template for a part that is not installed, or for a socket the part
 *       does not fit - a crest template carrying a part that only goes on a belt is an item the
 *       smithing table will refuse forever;</li>
 *   <li>two crafting recipes with the same grid, where one of them is ours: whichever the game picks,
 *       the other can never be crafted, and the author of the second pack has no way to know.</li>
 * </ul>
 *
 * <p>Run at {@code SERVER_STARTING}, which is after the registries, the recipes and the loot tables
 * are all loaded and before a player can be in the world, and again at the end of every
 * {@code /reload}, because two of the four (recipes, tables) are things a reload genuinely changes.
 * Re-finding a problem that is already in the report only counts it again; nothing is logged twice.
 */
public final class PackAudit {
    private PackAudit() {}

    /** Who has already been told this session. Cleared with the server, as {@code Compatibility} does. */
    private static final java.util.Set<java.util.UUID> told = new java.util.HashSet<>();

    public static void register() {
        ServerLifecycleEvents.SERVER_STARTING.register(server -> run(server, "world load"));
        ServerLifecycleEvents.END_DATA_PACK_RELOAD.register((server, resources, success) -> {
            if (success) {
                run(server, "reload");
            }
        });
        ServerLifecycleEvents.SERVER_STOPPED.register(server -> {
            PackProblems.clear();
            told.clear();
        });
        // One line, to somebody who can act on it. The same rule the missing-content advisory
        // follows: an ordinary member of a server cannot edit a datapack, and telling them only
        // hands out a worry with no action attached to it.
        ServerPlayConnectionEvents.JOIN.register((handler, sender, server) -> advise(handler.player));
    }

    private static void advise(final ServerPlayer player) {
        if (!PackProblems.any() || !told.add(player.getUUID())) {
            return;
        }
        if (!Commands.LEVEL_GAMEMASTERS.check(player.permissions())) {
            told.remove(player.getUUID());
            return;
        }
        player.sendSystemMessage(Component.translatable("armorpieces.packs.problems",
            PackProblems.count()).withStyle(ChatFormatting.YELLOW));
        player.sendSystemMessage(Component.translatable("armorpieces.packs.advice")
            .withStyle(ChatFormatting.GRAY));
    }

    /** The whole pass. Never throws: a report that crashes a server is worse than no report. */
    public static void run(final MinecraftServer server, final String where) {
        try {
            final RegistryAccess registries = server.registryAccess();
            partsWithNoSocket(registries);
            tablesNothingDefines(server, registries);
            templatesThatCanNeverBeApplied(server);
            recipesThatShareAGrid(server);
        } catch (final RuntimeException failed) {
            ArmorPieces.LOGGER.error("[Armor Pieces] The pack audit itself failed. The world is fine; "
                + "the report below may be short.", failed);
        }
        PackProblems.summarise(where);
    }

    /**
     * A part whose {@code anchors} is empty once the unreadable ones are gone.
     *
     * <p>It is a legal element and it loads - which is deliberate, because the id still resolves, so
     * an item wearing it keeps working and the part comes back whole the day the file is fixed. What
     * it cannot do is be applied to anything, since every route in goes through
     * {@link ArmorDecoration#fits}.
     */
    private static void partsWithNoSocket(final RegistryAccess registries) {
        final Registry<ArmorDecoration> parts = registries.lookupOrThrow(ArmorPiecesRegistries.ARMOR_DECORATION);
        parts.listElements().forEach(part -> {
            if (part.value().anchors().isEmpty()) {
                PackProblems.reported(part.key().identifier().toString(),
                    "names no socket, so nothing can ever apply it. `anchors` has to hold at least "
                        + "one of: " + anchorNames() + ".");
            }
        });
    }

    /**
     * A loot table named by a part or a group that no installed pack defines.
     *
     * <p>Silent until now, and the quietest way to author a part nobody will ever find: the row is
     * legal, the chance is honoured, and the table it names is simply never loaded - a typo in
     * {@code minecraft:chests/simple_dungeon} costs nothing at load and everything in play.
     */
    private static void tablesNothingDefines(final MinecraftServer server, final RegistryAccess registries) {
        final HolderLookup.RegistryLookup<LootTable> loaded =
            server.reloadableRegistries().lookup().lookup(Registries.LOOT_TABLE).orElse(null);
        if (loaded == null) {
            return;
        }
        final Map<ResourceKey<LootTable>, List<String>> wanted = new LinkedHashMap<>();
        registries.lookupOrThrow(ArmorPiecesRegistries.ARMOR_DECORATION).listElements().forEach(part -> {
            for (final DecorationLoot row : part.value().loot()) {
                wanted.computeIfAbsent(row.table(), key -> new ArrayList<>())
                    .add(part.key().identifier().toString());
            }
        });
        registries.lookupOrThrow(ArmorPiecesRegistries.LOOT_GROUP).listElements().forEach(group -> {
            for (final LootGroup.TableEntry entry : group.value().tables()) {
                wanted.computeIfAbsent(entry.table(), key -> new ArrayList<>())
                    .add(group.key().identifier().toString());
            }
        });
        wanted.forEach((table, namedBy) -> {
            if (loaded.get(table).isPresent()) {
                return;
            }
            PackProblems.reported(table.identifier().toString(),
                "is named by " + named(namedBy) + ", and no installed pack defines a loot table with "
                    + "that id. Nothing will ever be added to it - check the spelling, or install the "
                    + "pack that provides the table.");
        });
    }

    /**
     * A crafting recipe that hands out a template nothing can use.
     *
     * <p>Two ways to write one, and a pack author sees neither until they craft it: the template
     * carries a part id that is not installed (a moved part, a pack that is not there, a typo), or it
     * carries a part that does not fit the socket the template ITEM is for - and the socket is fixed
     * by the item, so {@code armorpieces:crest_template} holding a belt part is an item the smithing
     * table will refuse forever.
     */
    private static void templatesThatCanNeverBeApplied(final MinecraftServer server) {
        forEachShaped(server, (id, recipe, result) -> {
            if (!(result.getItem() instanceof DecorationTemplateItem template)) {
                return;
            }
            final Tolerant<Holder<ArmorDecoration>> carried = result.get(ModDataComponents.DECORATION);
            if (carried == null) {
                // A blank template is legal - a loot table fills one in with set_components, and the
                // creative tab hands them out - so this is not a mistake to report.
                return;
            }
            if (!carried.isResolved()) {
                PackProblems.reported(id.toString(),
                    "hands out a template for a part no installed pack defines. The template can be "
                        + "crafted and can never be applied; install the pack that provides the part, "
                        + "or correct the `armorpieces:decoration` component on the result.");
                return;
            }
            final ArmorDecoration part = carried.value().orElseThrow().value();
            if (part.anchors().isEmpty()) {
                // A part that fits nowhere is its own line in the report already, and "use the
                // armorpieces:no_template item" would be worse than saying nothing.
                return;
            }
            if (!part.fits(template.anchor())) {
                PackProblems.reported(id.toString(),
                    "hands out a " + template.anchor().getSerializedName() + " template carrying a "
                        + "part that only fits " + sockets(part) + ". A template's socket is fixed by "
                        + "its item, so the smithing table will always refuse it - use the "
                        + "armorpieces:" + sockets(part).split(",")[0].trim() + "_template item, or "
                        + "add the socket to the part's `anchors`.");
            }
        });
    }

    /**
     * Two crafting recipes with the same grid, one of them ours.
     *
     * <p>The case that matters is two packs installed together, which is exactly the case no static
     * check in this repository can see: {@code tools/check_authoring.py} compares the packs it is
     * given, and a player's pack folder is not that set. Whichever recipe the game picks, the other
     * is dead - so both are named, and neither is called the wrong one, because which of them is
     * wrong is the author's business and not the mod's.
     */
    private static void recipesThatShareAGrid(final MinecraftServer server) {
        final Map<Grid, List<Identifier>> byGrid = new LinkedHashMap<>();
        final Map<Grid, Boolean> ours = new LinkedHashMap<>();
        forEachShaped(server, (id, recipe, result) -> {
            final Grid grid = new Grid(recipe.getWidth(), recipe.getHeight(), recipe.getIngredients());
            byGrid.computeIfAbsent(grid, key -> new ArrayList<>()).add(id);
            ours.merge(grid, isOurs(result), Boolean::logicalOr);
        });
        byGrid.forEach((grid, ids) -> {
            if (ids.size() < 2 || !Boolean.TRUE.equals(ours.get(grid))) {
                return;
            }
            PackProblems.reported(ids.getFirst().toString(),
                "shares its crafting grid with " + named(ids.subList(1, ids.size()).stream()
                    .map(Identifier::toString).toList()) + ". Only one of them can ever be crafted, "
                    + "and which one is not something a pack can decide - give each recipe a grid of "
                    + "its own.");
        });
    }

    /** One shaped recipe, its id and what it makes. Failure to assemble is not a mistake to report. */
    private interface ShapedVisitor {
        void accept(Identifier id, ShapedRecipe recipe, ItemStack result);
    }

    private static void forEachShaped(final MinecraftServer server, final ShapedVisitor visitor) {
        for (final RecipeHolder<?> holder : server.getRecipeManager().getRecipes()) {
            if (!(holder.value() instanceof ShapedRecipe shaped)) {
                continue;
            }
            final ItemStack result;
            try {
                result = shaped.assemble(CraftingInput.EMPTY);
            } catch (final RuntimeException notAssemblable) {
                // Another mod's recipe that needs its input to know its output. Not ours to judge.
                continue;
            }
            if (result.isEmpty()) {
                continue;
            }
            visitor.accept(holder.id().identifier(), shaped, result);
        }
    }

    /** The grid a recipe occupies: its shape and its ingredients, which is what two recipes collide on. */
    private record Grid(int width, int height, List<Optional<Ingredient>> ingredients) {}

    private static boolean isOurs(final ItemStack result) {
        final Identifier id = BuiltInRegistries.ITEM.getKey(result.getItem());
        return id != null && ArmorPieces.MOD_ID.equals(id.getNamespace());
    }

    private static String sockets(final ArmorDecoration part) {
        return part.anchors().stream().map(DecorationAnchor::getSerializedName).sorted()
            .reduce((a, b) -> a + ", " + b).orElse("no socket at all");
    }

    private static String anchorNames() {
        return java.util.Arrays.stream(DecorationAnchor.values())
            .map(DecorationAnchor::getSerializedName).reduce((a, b) -> a + ", " + b).orElse("");
    }

    /** "x", "x and y", "x, y and 3 more" - a list in a sentence, never a list that fills the log. */
    private static String named(final List<String> names) {
        return switch (names.size()) {
            case 0 -> "nothing";
            case 1 -> names.getFirst();
            case 2 -> names.get(0) + " and " + names.get(1);
            default -> names.get(0) + ", " + names.get(1) + " and " + (names.size() - 2) + " more";
        };
    }
}
