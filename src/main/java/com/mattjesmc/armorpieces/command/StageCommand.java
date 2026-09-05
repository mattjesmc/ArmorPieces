package com.mattjesmc.armorpieces.command;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.cloth.Cloth;
import com.mattjesmc.armorpieces.cloth.ClothValue;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.MaterialIcons;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.decoration.fitting.FittingValue;
import com.mattjesmc.armorpieces.menu.AdvancedSmithingMenu;
import com.mattjesmc.armorpieces.recipe.SmithingClothRecipe;
import com.mattjesmc.armorpieces.recipe.SmithingSkinRecipe;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.skin.ArmorSkin;
import com.mattjesmc.armorpieces.skin.ArmorSkinValue;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.LongArgumentType;
import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Stream;
import net.minecraft.commands.CommandBuildContext;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.ResourceArgument;
import net.minecraft.commands.arguments.ResourceOrIdArgument;
import net.minecraft.commands.arguments.item.ItemArgument;
import net.minecraft.commands.arguments.item.ItemInput;
import net.minecraft.core.Direction;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.equipment.ArmorType;
import net.minecraft.world.item.equipment.EquipmentAsset;
import net.minecraft.world.item.equipment.EquipmentAssets;
import net.minecraft.world.item.equipment.Equippable;
import net.minecraft.world.item.equipment.trim.TrimMaterial;
import net.minecraft.world.item.equipment.trim.TrimMaterials;
import net.minecraft.world.level.block.entity.BannerPatternLayers;
import net.minecraft.world.level.entity.EntityTypeTest;
import net.minecraft.world.level.storage.loot.LootParams;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.level.storage.loot.parameters.LootContextParamSets;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * {@code /armorpieces stage} - lays out a grid of armor stands wearing every combination the loaded
 * data can produce, so a change to a model, a texture or an anchor offset can be judged against all
 * of it at once instead of one smithing operation at a time.
 *
 * <p>Every axis is READ FROM THE REGISTRIES, never from a list here: parts come from
 * {@code armorpieces:armor_decoration}, colours from vanilla's {@code minecraft:trim_material}, and
 * the base armor from every item in the game that declares an {@link EquipmentAsset} for a humanoid
 * armor slot. A datapack part, a datapack trim material and a modded armor set therefore all appear
 * on the stage the moment they load, which is the only way a preview of a data-driven system can
 * avoid lying about what the system contains.
 *
 * <p>The modes fall into two halves. The <b>grids</b> are each a different slice of one cross
 * product, and answer a question about the data:
 *
 * <ul>
 *   <li>{@code bases} - every (socketed part x material), that block repeated for every base armor
 *       set, because the base's equipment asset is what selects a material's darker variant (gold on
 *       gold), and that resolution is invisible until the two stand side by side.</li>
 *   <li>{@code fittings} - one block per (socketed part x fitting): the part's materials down the
 *       rows, everything the fitting takes across the columns, that fitting filled. One fitting at a
 *       time, so a stand shows exactly one thing that was not there before; this is where the masks
 *       and the cloth are judged.</li>
 *   <li>{@code skins} - one stand per (skin x base armor set): every skin down the rows, every
 *       armor material across the columns, each suit wearing the skin. The only grid whose columns
 *       are the ARMOR rather than the trim, because a skin takes its colours from the armor's own
 *       texture and has no trim material of its own.</li>
 * </ul>
 *
 * <p>The <b>gallery</b> modes are for the picture rather than the check. A grid holds everything
 * still but one axis, which is what makes it readable and what makes it drab: eleven identical
 * stands in eleven colours, on plain iron, with every fitting empty. A gallery stand is instead
 * dressed the way a player would dress it - a skinned suit, a part in some colour, something in
 * every fitting - and the variety is the point.
 *
 * <ul>
 *   <li>{@code pieces} - every part in the game exactly once, a row per socket, each on its own
 *       randomly dressed suit. The one shot that shows the whole catalogue.</li>
 *   <li>{@code random} - complete sets, every socket filled, nothing about them chosen: base armor,
 *       skin, cloth, part, material and every fitting all rolled.</li>
 *   <li>{@code set} - one of {@link #SETS}, the hand-built thematic sets, exactly as written.
 *       Unlike everything else here it is not a query over the data but a picture of it, and it is
 *       the same picture every time, which is what a page's screenshot needs.</li>
 * </ul>
 *
 * <p>{@code clear} removes what any of them placed, by tag, and {@code loot} rolls a table rather
 * than placing anything.
 *
 * <p>Every gallery mode takes a {@code seed} and reports the one it used, so a shot worth keeping
 * can be taken again after a texture is fixed. Nothing else about a stage is remembered.
 *
 * <p>Nothing here goes through {@link com.mattjesmc.armorpieces.recipe.SmithingDecorationRecipe}'s
 * ingredient rules - a stage is not a crafting shortcut - but it does honour the one rule that
 * matters for rendering: a part is only ever placed in a socket it declares, on the armor piece that
 * socket belongs to.
 */
public final class StageCommand {
    /**
     * The scoreboard tag every placed entity carries, and the whole of {@code clear}'s memory.
     *
     * <p>A tag rather than a list of UUIDs held in this class: the stands outlive the command, the
     * session and the server process, so a stage placed yesterday is still clearable today, and a
     * stand a player adds to the grid by hand with the same tag is swept up with the rest.
     */
    private static final String STAGE_TAG = "armorpieces_stage";

    /** Blocks between stands across a row. Wide enough that neighbouring captions do not collide. */
    private static final double COLUMN_SPACING = 2.0;
    /** Blocks between rows. */
    private static final double ROW_SPACING = 2.0;
    /** Extra rows of clear ground between one base's block and the next, in {@code bases}. */
    private static final double BLOCK_GAP = 2.0;

    /**
     * The most stands one invocation will place.
     *
     * <p>{@code bases} is a triple cross product, and a heavily modded item registry can push it into
     * the tens of thousands - enough entities to stall the server that was asked for a preview. The
     * cap refuses rather than truncates, because a stage silently missing its last few bases is a
     * worse answer than being told to narrow the query.
     */
    private static final int MAX_STANDS = 4000;
    /** Rolls of a loot table when no count is given: enough for a chance of 0.05 to show up. */
    private static final int DEFAULT_ROLLS = 1000;
    /** Rolling is cheap, but a million rolls of a table with functions is a noticeable pause. */
    private static final int MAX_ROLLS = 100_000;

    /** Humanoid armor slots, head to toe. Excludes {@link ArmorType#BODY} - no anchor names it. */
    private static final List<ArmorType> ARMOR_TYPES =
        List.of(ArmorType.HELMET, ArmorType.CHESTPLATE, ArmorType.LEGGINGS, ArmorType.BOOTS);

    private StageCommand() {}

    public static void register(
        final CommandDispatcher<CommandSourceStack> dispatcher,
        final CommandBuildContext context
    ) {
        dispatcher.register(Commands.literal("armorpieces")
            .requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
            .then(Commands.literal("stage")
                // The gallery modes. Each takes an optional seed as its LAST argument, so the
                // shortest form is always the interesting one and the seed is what you add once a
                // roll came out worth keeping.
                .then(Commands.literal("pieces")
                    .executes(ctx -> stagePieces(ctx.getSource(), freshSeed(ctx.getSource())))
                    .then(Commands.argument("seed", LongArgumentType.longArg())
                        .executes(ctx -> stagePieces(ctx.getSource(), LongArgumentType.getLong(ctx, "seed")))))
                .then(Commands.literal("random")
                    .executes(ctx -> stageRandom(ctx.getSource(), 1, freshSeed(ctx.getSource())))
                    .then(Commands.argument("count", IntegerArgumentType.integer(1, MAX_STANDS))
                        .executes(ctx -> stageRandom(ctx.getSource(),
                            IntegerArgumentType.getInteger(ctx, "count"), freshSeed(ctx.getSource())))
                        .then(Commands.argument("seed", LongArgumentType.longArg())
                            .executes(ctx -> stageRandom(ctx.getSource(),
                                IntegerArgumentType.getInteger(ctx, "count"),
                                LongArgumentType.getLong(ctx, "seed"))))))
                .then(setNode())
                .then(Commands.literal("bases")
                    .executes(ctx -> stageBases(ctx.getSource(), null))
                    .then(Commands.argument("base", ItemArgument.item(context))
                        .executes(ctx -> stageBases(ctx.getSource(), ItemArgument.getItem(ctx, "base")))))
                .then(Commands.literal("fittings")
                    .executes(ctx -> stageFittings(ctx.getSource(), null))
                    .then(Commands.argument("decoration",
                            ResourceArgument.resource(context, ArmorPiecesRegistries.ARMOR_DECORATION))
                        .executes(ctx -> stageFittings(ctx.getSource(), decorationArgument(ctx)))))
                .then(Commands.literal("skins")
                    .executes(c -> stageSkins(c.getSource(), null))
                    .then(Commands.argument("skin",
                            ResourceArgument.resource(context, ArmorPiecesRegistries.ARMOR_SKIN))
                        .executes(c -> stageSkins(c.getSource(),
                            ResourceArgument.getResource(c, "skin", ArmorPiecesRegistries.ARMOR_SKIN)))))
                .then(Commands.literal("clear")
                    .executes(ctx -> clear(ctx.getSource())))
                // Not stands but numbers: rolls a loot table and counts what the mod put in it, so
                // a part's chance and weight can be judged without opening a thousand chests.
                .then(Commands.literal("loot")
                    .then(Commands.argument("table", ResourceOrIdArgument.lootTable(context))
                        .executes(ctx -> stageLoot(ctx.getSource(),
                            ResourceOrIdArgument.getLootTable(ctx, "table"), DEFAULT_ROLLS))
                        .then(Commands.argument("rolls", IntegerArgumentType.integer(1, MAX_ROLLS))
                            .executes(ctx -> stageLoot(ctx.getSource(),
                                ResourceOrIdArgument.getLootTable(ctx, "table"),
                                IntegerArgumentType.getInteger(ctx, "rolls")))))))
            // The advanced smithing table without the block: the same menu, opened for the caller
            // wherever they stand. A preview aid in the spirit of `stage` - a set is dressed on the
            // stand and taken apart again without a table being placed - and so behind the same
            // permission level, not a survival shortcut.
            .then(Commands.literal("table")
                .executes(ctx -> openTable(ctx.getSource()))));
    }

    private static int openTable(final CommandSourceStack source) throws CommandSyntaxException {
        final ServerPlayer player = source.getPlayerOrException();
        player.openMenu(new SimpleMenuProvider(
            (containerId, inventory, p) -> new AdvancedSmithingMenu(containerId, inventory),
            Component.translatable("container.armorpieces.advanced_smithing")));
        return 1;
    }

    private static Holder<ArmorDecoration> decorationArgument(final CommandContext<CommandSourceStack> ctx)
        throws CommandSyntaxException {
        return ResourceArgument.getResource(ctx, "decoration", ArmorPiecesRegistries.ARMOR_DECORATION);
    }

    // ---- modes ----------------------------------------------------------------------------------

    /**
     * Every (part, socket) pair down the rows, every trim material across the columns, one block per
     * base armor set.
     *
     * <p>The third axis is the point rather than thoroughness for its own sake: a material's texture
     * suffix is resolved against the ARMOR's equipment asset (see {@link DecorationEntry#texture}),
     * so gold parts on gold armor draw from {@code gold_darker} and the same part on iron does not.
     * None of that is visible on a single base.
     */
    private static int stageBases(final CommandSourceStack source, final @Nullable ItemInput only) {
        final List<Slot> rows = slots(source, null);
        final List<Holder.Reference<TrimMaterial>> materials = materials(source);
        final List<BaseArmor> bases = only == null ? baseArmors() : baseArmorsFor(only.item().value());
        if (rows.isEmpty() || materials.isEmpty() || bases.isEmpty()) {
            return nothingToStage(source);
        }

        int planned = 0;
        for (final BaseArmor base : bases) {
            planned += (int) rows.stream().filter(slot -> base.has(slot.armorType())).count() * materials.size();
        }
        if (tooMany(source, planned)) {
            return 0;
        }

        final Layout layout = Layout.inFrontOf(source);
        int placed = 0;
        double row = 0.0;
        for (final BaseArmor base : bases) {
            // A base that covers only some slots - a turtle shell is a helmet and nothing else -
            // stages the rows it can wear rather than being skipped or leaving gaps in the block.
            final List<Slot> fitting = rows.stream().filter(slot -> base.has(slot.armorType())).toList();
            if (fitting.isEmpty()) {
                continue;
            }
            layout.label(-2.0, row - 1.0, base.name());
            placed += placeBlock(layout, row, fitting, materials, base);
            row += fitting.size() + BLOCK_GAP;
        }
        return finish(source, placed);
    }

    /**
     * One block per (socket, part, fitting), each block the part's materials down the rows and every
     * value the fitting takes across the columns, with that one fitting filled and the part's others
     * left empty.
     *
     * <p>Both axes matter and neither can stand in for the other: a gem's colour is read against the
     * band it sits in, so an emerald in a gold circlet and the same emerald in an iron one are two
     * different pictures, and a mask that reads well under one is not thereby right under the rest.
     * One fitting at a time, rather than all of a part's at once, so a stand shows exactly one thing
     * that was not there before.
     *
     * <p>The columns are READ FROM THE ITEM REGISTRY, not from the fitting's own tag: every item in
     * the game is offered to the fitting through the same {@link Fitting#accept} the smithing table
     * runs, and what it takes is what is staged. That is the only list that cannot disagree with the
     * table, and it is how a modded dye or a datapack trim material shows up here unasked.
     */
    private static int stageFittings(final CommandSourceStack source, final @Nullable Holder<ArmorDecoration> only) {
        final List<FittedSlot> blocks = fittedSlots(source, only);
        final List<Holder.Reference<TrimMaterial>> materials = materials(source);
        final BaseArmor base = defaultBase();
        if (blocks.isEmpty()) {
            source.sendFailure(Component.translatable("commands.armorpieces.stage.no_fittings"));
            return 0;
        }
        if (materials.isEmpty() || base == null) {
            return nothingToStage(source);
        }

        int planned = 0;
        for (final FittedSlot block : blocks) {
            planned += materials.size() * block.values().size();
        }
        if (tooMany(source, planned)) {
            return 0;
        }

        final Layout layout = Layout.inFrontOf(source);
        int placed = 0;
        double row = 0.0;
        for (final FittedSlot block : blocks) {
            final List<FittingValue> values = block.values();
            layout.label(-2.0, row - 1.0, block.label());
            for (int column = 0; column < values.size(); column++) {
                layout.label(column, row - 1.0, values.get(column).name());
            }
            for (int line = 0; line < materials.size(); line++) {
                final Holder.Reference<TrimMaterial> material = materials.get(line);
                layout.label(-1.0, row + line, material.value().description());
                for (int column = 0; column < values.size(); column++) {
                    final ItemStack piece = base.piece(block.slot().armorType());
                    if (piece.isEmpty()) {
                        continue;
                    }
                    decorate(piece, block.slot().anchor(), block.slot().decoration(), material);
                    fit(piece, block.slot().anchor(), block.fitting(), values.get(column));
                    layout.stand(
                        column,
                        row + line,
                        Map.of(block.slot().armorType(), piece),
                        block.slot().decoration().value().copyWithStyle(material));
                    placed++;
                }
            }
            row += materials.size() + BLOCK_GAP;
        }
        return finish(source, placed);
    }

    /**
     * Removes every entity in this level carrying {@link #STAGE_TAG}.
     *
     * <p>Loaded chunks only, which is what an entity query can see and is the same reach a vanilla
     * selector has. In practice that is the stage you are standing in front of; a grid left in a far
     * corner of the world clears when you go back to it.
     */
    /**
     * One stand per (skin x base armor set), wearing that skin on a whole suit of that armor.
     *
     * <p>The one view the other modes cannot give, because every one of them varies the TRIM
     * material and holds the armor still. A skin has no trim material: its colours are taken from
     * the armor's own texture, so the axis that matters is the armor, and the question this answers
     * is the one the feature stands or falls on - does a skinned iron helmet still read as iron
     * beside a skinned gold one, and does the pattern survive a material whose own texture is nearly
     * flat.
     *
     * <p>Armor that refuses a skin is staged unskinned rather than skipped, because seeing chainmail
     * standing plain in the row is the answer to "why is nothing happening to my chainmail".
     */
    private static int stageSkins(final CommandSourceStack source, final @Nullable Holder<ArmorSkin> only) {
        final List<Holder<ArmorSkin>> rows = only != null
            ? List.of(only)
            : source.registryAccess().lookupOrThrow(ArmorPiecesRegistries.ARMOR_SKIN)
                .listElements()
                .<Holder<ArmorSkin>>map(holder -> holder)
                .toList();
        final List<BaseArmor> bases = baseArmors();
        if (rows.isEmpty() || bases.isEmpty()) {
            return nothingToStage(source);
        }
        if (tooMany(source, rows.size() * bases.size())) {
            return 0;
        }

        final Layout layout = Layout.inFrontOf(source);
        for (int column = 0; column < bases.size(); column++) {
            layout.label(column, -1.0, bases.get(column).name());
        }

        int placed = 0;
        for (int row = 0; row < rows.size(); row++) {
            final Holder<ArmorSkin> skin = rows.get(row);
            layout.label(-1.0, row, skin.value().description());
            for (int column = 0; column < bases.size(); column++) {
                final BaseArmor base = bases.get(column);
                final Map<ArmorType, ItemStack> worn = new EnumMap<>(ArmorType.class);
                for (final ArmorType type : ARMOR_TYPES) {
                    final ItemStack piece = base.piece(type);
                    if (piece.isEmpty()) {
                        continue;
                    }
                    // The recipe's own rule, not a second one: a piece it refuses is worn plain.
                    if (SmithingSkinRecipe.isSkinnable(piece)) {
                        piece.set(ModDataComponents.SKIN, new ArmorSkinValue(skin));
                    }
                    worn.put(type, piece);
                }
                if (worn.isEmpty()) {
                    continue;
                }
                layout.stand(column, row, worn, skin.value().description());
                placed++;
            }
        }
        return finish(source, placed);
    }

    private static int clear(final CommandSourceStack source) {
        final List<? extends Entity> staged = source.getLevel().getEntities(
            EntityTypeTest.<Entity, Entity>forClass(Entity.class),
            entity -> entity.entityTags().contains(STAGE_TAG));
        staged.forEach(Entity::discard);
        source.sendSuccess(() -> Component.translatable("commands.armorpieces.stage.cleared", staged.size()), true);
        return staged.size();
    }

    // ---- gallery --------------------------------------------------------------------------------

    /**
     * Every part in the game exactly once, a row per socket, each on its own randomly dressed suit.
     *
     * <p>The grid modes each hold everything still but one axis; this one holds nothing still but
     * the part. A stand is a whole skinned suit of some armor, in some colour, with something in
     * every fitting the part declares - the way a player would actually be wearing it - and the only
     * thing the row and column say is which part it is showing. That makes it useless for comparing
     * two parts and exactly right for a picture of all of them.
     *
     * <p>A row is a SOCKET rather than a part, so the twelve rows are the twelve sockets and a part
     * that declared two would appear in both. None does today; the layout does not assume it.
     */
    private static int stagePieces(final CommandSourceStack source, final long seed) {
        final Wardrobe wardrobe = new Wardrobe(source, seed);
        if (wardrobe.isEmpty()) {
            return nothingToStage(source);
        }
        if (tooMany(source, wardrobe.parts.values().stream().mapToInt(List::size).sum())) {
            return 0;
        }

        final Layout layout = Layout.inFrontOf(source);
        int placed = 0;
        int row = 0;
        for (final var socket : wardrobe.parts.entrySet()) {
            layout.label(-1.0, row, socketName(socket.getKey()));
            final List<Holder.Reference<ArmorDecoration>> parts = socket.getValue();
            for (int column = 0; column < parts.size(); column++) {
                final Map<ArmorType, ItemStack> worn = wardrobe.suit(false);
                wardrobe.dress(worn, socket.getKey(), parts.get(column));
                layout.stand(column, row, worn, parts.get(column).value().description());
                placed++;
            }
            row++;
        }
        return finish(source, placed, seed);
    }

    /**
     * Complete sets with nothing about them chosen: base armor, skin, cloth, and in every socket a
     * part, its material and each of its fittings, all rolled.
     *
     * <p>What {@code pieces} is for the catalogue this is for the system - the question it answers is
     * not "does this part look right" but "does a set of this mod, assembled the way the game will
     * assemble it out of a chest, hold together". Most of the failures it finds are collisions: two
     * parts that each read well and cannot be worn at once.
     */
    private static int stageRandom(final CommandSourceStack source, final int count, final long seed) {
        final Wardrobe wardrobe = new Wardrobe(source, seed);
        if (wardrobe.isEmpty()) {
            return nothingToStage(source);
        }
        if (tooMany(source, count)) {
            return 0;
        }

        final Layout layout = Layout.inFrontOf(source);
        for (int column = 0; column < count; column++) {
            final Map<ArmorType, ItemStack> worn = wardrobe.suit(true);
            for (final var socket : wardrobe.parts.entrySet()) {
                wardrobe.dress(worn, socket.getKey(), wardrobe.pick(socket.getValue()));
            }
            layout.stand(column, 0.0, worn, Component.translatable("commands.armorpieces.stage.random.name", column + 1));
        }
        return finish(source, count, seed);
    }

    /**
     * One stand per hand-built set, in a row, each captioned with its name.
     *
     * <p>No randomness anywhere: the same command gives the same picture on any world, which is what
     * a page's screenshots are for. A set naming a part, skin or cloth the loaded data does not have
     * says so and is staged without it, rather than refusing - a pack that disables a part should not
     * take a gallery command down with it.
     */
    private static int stageSets(final CommandSourceStack source, final List<GallerySet> sets) {
        final Layout layout = Layout.inFrontOf(source);
        int placed = 0;
        for (int column = 0; column < sets.size(); column++) {
            final GallerySet set = sets.get(column);
            final Map<ArmorType, ItemStack> worn = set.wear(source);
            if (worn.isEmpty()) {
                continue;
            }
            layout.label(column, -1.0, set.title());
            layout.stand(column, 0.0, worn, set.title());
            placed++;
        }
        if (placed == 0) {
            return nothingToStage(source);
        }
        return finish(source, placed);
    }

    /** {@code set} with a child literal per {@link #SETS} entry, and no argument for all of them. */
    private static LiteralArgumentBuilder<CommandSourceStack> setNode() {
        final LiteralArgumentBuilder<CommandSourceStack> node = Commands.literal("set")
            .executes(ctx -> stageSets(ctx.getSource(), SETS));
        for (final GallerySet set : SETS) {
            node.then(Commands.literal(set.name()).executes(ctx -> stageSets(ctx.getSource(), List.of(set))));
        }
        return node;
    }

    /** A seed for a roll nobody asked to reproduce - reported back, so it can be asked for later. */
    private static long freshSeed(final CommandSourceStack source) {
        return source.getLevel().getRandom().nextLong();
    }

    private static Component socketName(final DecorationAnchor anchor) {
        return Component.translatable("anchor.armorpieces." + anchor.getSerializedName());
    }

    /**
     * Everything a randomly dressed stand is drawn from, and the one {@link RandomSource} behind all
     * of it.
     *
     * <p>One instance per command, so a seed reproduces a whole grid and not merely one stand: the
     * rolls are consumed in layout order, and the same seed against the same loaded data gives the
     * same ninety-one stands. Adding a part shifts everything after it, which is the honest
     * behaviour - the picture is of the data, and the data changed.
     *
     * <p>Pools are read from the registries for the reason the grids' axes are (see the class
     * documentation), and a fitting's values are found by offering it every item in the game, which
     * is expensive enough to be worth remembering across the ninety-one stands that ask for it.
     */
    private static final class Wardrobe {
        private final RandomSource random;
        private final List<Holder.Reference<TrimMaterial>> materials;
        private final List<BaseArmor> bases;
        private final List<Holder.Reference<ArmorSkin>> skins;
        private final List<Holder.Reference<Cloth>> cloths;
        private final Map<DecorationAnchor, List<Holder.Reference<ArmorDecoration>>> parts;
        private final Map<Holder<Fitting>, List<FittingValue>> values = new HashMap<>();

        Wardrobe(final CommandSourceStack source, final long seed) {
            this.random = RandomSource.create(seed);
            this.materials = materials(source);
            // Full sets only. A base that covers three slots would leave a stand bare-legged, and
            // the point of a gallery stand is that it looks like something someone is wearing.
            this.bases = baseArmors().stream()
                .filter(base -> ARMOR_TYPES.stream().allMatch(base::has))
                .toList();
            this.skins = source.registryAccess().lookupOrThrow(ArmorPiecesRegistries.ARMOR_SKIN).listElements().toList();
            this.cloths = source.registryAccess().lookupOrThrow(ArmorPiecesRegistries.CLOTH).listElements().toList();
            this.parts = partsByAnchor(source);
        }

        boolean isEmpty() {
            return this.materials.isEmpty() || this.bases.isEmpty() || this.parts.isEmpty();
        }

        /**
         * A whole suit of one random armor set, skinned, with every socket still empty.
         *
         * <p>{@code clothed} is a permission rather than an instruction, and only about a third of
         * the suits given it take one up: a tabard is a big flat shape over the torso, and every
         * stand wearing one would hide the three chest sockets in exactly the mode meant to show
         * them. Armor that refuses a skin or a cloth is worn plain, by the recipes' own tests
         * rather than a second set of rules here.
         */
        Map<ArmorType, ItemStack> suit(final boolean clothed) {
            final BaseArmor base = pick(this.bases);
            final Holder<ArmorSkin> skin = this.skins.isEmpty() ? null : pick(this.skins);
            final ClothValue cloth = !clothed || this.cloths.isEmpty() || this.random.nextInt(3) != 0
                ? null
                : new ClothValue(pick(this.cloths), pickDye(), BannerPatternLayers.EMPTY);

            final Map<ArmorType, ItemStack> worn = new EnumMap<>(ArmorType.class);
            for (final ArmorType type : ARMOR_TYPES) {
                final ItemStack piece = base.piece(type);
                if (piece.isEmpty()) {
                    continue;
                }
                if (skin != null && SmithingSkinRecipe.isSkinnable(piece)) {
                    piece.set(ModDataComponents.SKIN, new ArmorSkinValue(skin));
                }
                if (cloth != null && SmithingClothRecipe.isClothable(piece)) {
                    piece.set(ModDataComponents.CLOTH, cloth);
                }
                worn.put(type, piece);
            }
            return worn;
        }

        /** One part into one socket of a suit, in a random material, with every fitting filled. */
        void dress(
            final Map<ArmorType, ItemStack> worn,
            final DecorationAnchor anchor,
            final Holder.Reference<ArmorDecoration> part
        ) {
            final ItemStack piece = worn.get(anchor.armorType());
            if (piece == null) {
                return;
            }
            decorate(piece, anchor, part, pick(this.materials));
            for (final Holder<Fitting> fitting : part.value().fittings()) {
                final List<FittingValue> options =
                    this.values.computeIfAbsent(fitting, held -> fittingValues(held.value()));
                if (!options.isEmpty()) {
                    fit(piece, anchor, fitting, pick(options));
                }
            }
        }

        <T> T pick(final List<T> from) {
            return from.get(this.random.nextInt(from.size()));
        }

        private DyeColor pickDye() {
            final DyeColor[] colours = DyeColor.values();
            return colours[this.random.nextInt(colours.length)];
        }
    }

    // ---- the thematic sets ----------------------------------------------------------------------

    /**
     * A set written out rather than queried: the armor to wear it on, the skin over that, an
     * optional cloth, and a part with its material and its fittings in every socket.
     *
     * <p>Deliberately in Java and not in a datapack, which is the opposite of every other list in
     * this class. A datapack entry is for what the GAME contains, and these are not part of the
     * game - nothing hands one out, nothing crafts one, no player will ever see the name. They are
     * six screenshots, whose only job is to keep looking like themselves while the parts around them
     * change, and a registry for them would be a public surface that has to be kept, documented and
     * synced for the sake of an author's private furniture.
     */
    private record GallerySet(
        String name,
        ResourceKey<EquipmentAsset> base,
        ResourceKey<ArmorSkin> skin,
        @Nullable SetCloth cloth,
        List<SetSocket> sockets
    ) {
        Component title() {
            return Component.translatable("commands.armorpieces.stage.set." + this.name);
        }

        /**
         * The four dressed stacks, or an empty map if the base armor itself is gone.
         *
         * <p>Every other lookup is allowed to miss: a part, a skin or a cloth this set names and the
         * loaded data has not got is reported and skipped, and the rest of the set is still worth
         * looking at. The base is not, because without it there is nothing to hang anything on.
         */
        Map<ArmorType, ItemStack> wear(final CommandSourceStack source) {
            final BaseArmor armor = baseArmors().stream()
                .filter(candidate -> candidate.asset().equals(this.base))
                .findFirst()
                .orElse(null);
            if (armor == null) {
                missing(source, this.base.identifier());
                return Map.of();
            }
            final Holder<ArmorSkin> worn = find(source, ArmorPiecesRegistries.ARMOR_SKIN, this.skin);
            final ClothValue cloth = this.cloth == null ? null : this.cloth.resolve(source);

            final Map<ArmorType, ItemStack> suit = new EnumMap<>(ArmorType.class);
            for (final ArmorType type : ARMOR_TYPES) {
                final ItemStack piece = armor.piece(type);
                if (piece.isEmpty()) {
                    continue;
                }
                if (worn != null && SmithingSkinRecipe.isSkinnable(piece)) {
                    piece.set(ModDataComponents.SKIN, new ArmorSkinValue(worn));
                }
                if (cloth != null && SmithingClothRecipe.isClothable(piece)) {
                    piece.set(ModDataComponents.CLOTH, cloth);
                }
                suit.put(type, piece);
            }
            this.sockets.forEach(socket -> socket.dress(source, suit));
            return suit;
        }
    }

    /** A garment in one flat colour. No patterns: a set's colour is its own, not a banner's. */
    private record SetCloth(ResourceKey<Cloth> cloth, DyeColor colour) {
        @Nullable ClothValue resolve(final CommandSourceStack source) {
            final Holder<Cloth> found = find(source, ArmorPiecesRegistries.CLOTH, this.cloth);
            return found == null ? null : new ClothValue(found, this.colour, BannerPatternLayers.EMPTY);
        }
    }

    /**
     * One socket of a set: the part, its material, and the ITEMS that fill its fittings.
     *
     * <p>Items rather than fitting values, and offered through {@link Fitting#accept} in the part's
     * own fitting order - which is precisely what
     * {@link com.mattjesmc.armorpieces.recipe.SmithingFittingRecipe} does with a bare template. A set
     * therefore says "an emerald and a gold ingot" the way a player would hand them over, and never
     * has to name a fitting or know the shape of the value it stores, so a part whose fittings are
     * reordered or retyped keeps working here.
     */
    private record SetSocket(
        DecorationAnchor anchor,
        ResourceKey<ArmorDecoration> part,
        ResourceKey<TrimMaterial> material,
        List<SetItem> fittings
    ) {
        void dress(final CommandSourceStack source, final Map<ArmorType, ItemStack> suit) {
            final ItemStack piece = suit.get(this.anchor.armorType());
            final Holder<ArmorDecoration> decoration =
                find(source, ArmorPiecesRegistries.ARMOR_DECORATION, this.part);
            final Holder<TrimMaterial> trim = find(source, Registries.TRIM_MATERIAL, this.material);
            if (piece == null || decoration == null || trim == null) {
                return;
            }
            decorate(piece, this.anchor, decoration, trim);
            for (final SetItem filler : this.fittings) {
                final ItemStack offered = filler.stack(source);
                for (final Holder<Fitting> fitting : decoration.value().fittings()) {
                    final Optional<FittingValue> value = fitting.value().accept(offered);
                    if (value.isPresent()) {
                        fit(piece, this.anchor, fitting, value.get());
                        break;
                    }
                }
            }
        }
    }

    /**
     * One item a set hands to a part's fittings, named by what it IS rather than by an item field.
     *
     * <p>There is no {@code dyed(DyeColor.RED)} to point at: a dye, a banner and the thing that provides a
     * trim material are all found by walking the item registry, which is exactly what
     * {@link MaterialIcons} does - and cannot be done while this class is still being initialised,
     * which is when {@link #SETS} is built. So a set says "purple dye" and the item is looked up when
     * the set is staged. An item nothing in the game provides comes back empty, no fitting accepts
     * it, and the part is simply staged unfitted.
     */
    private sealed interface SetItem {
        ItemStack stack(CommandSourceStack source);

        /** For a {@code gemstone} or a {@code guard}: the ingot or the gem the material comes in. */
        record Material(ResourceKey<TrimMaterial> material) implements SetItem {
            @Override
            public ItemStack stack(final CommandSourceStack source) {
                final Holder<TrimMaterial> found = find(source, Registries.TRIM_MATERIAL, this.material);
                return found == null ? ItemStack.EMPTY : MaterialIcons.forTrimMaterial(found);
            }
        }

        /** For an {@code inlay}. */
        record Dye(DyeColor colour) implements SetItem {
            @Override
            public ItemStack stack(final CommandSourceStack source) {
                return MaterialIcons.forDye(this.colour);
            }
        }

        /** For a {@code banner}: a plain banner, so the cloth takes the colour and no design. */
        record Banner(DyeColor colour) implements SetItem {
            @Override
            public ItemStack stack(final CommandSourceStack source) {
                return MaterialIcons.forBanner(this.colour);
            }
        }
    }

    /** A registry entry a set names, or null with a message saying which one is not loaded. */
    private static <T> @Nullable Holder<T> find(
        final CommandSourceStack source,
        final ResourceKey<Registry<T>> registry,
        final ResourceKey<T> key
    ) {
        final Holder<T> found = source.registryAccess().lookupOrThrow(registry).get(key).orElse(null);
        if (found == null) {
            missing(source, key.identifier());
        }
        return found;
    }

    private static void missing(final CommandSourceStack source, final Identifier what) {
        source.sendSuccess(
            () -> Component.translatable("commands.armorpieces.stage.set.missing", what.toString()), false);
    }

    private static ResourceKey<ArmorDecoration> part(final String name) {
        return ResourceKey.create(ArmorPiecesRegistries.ARMOR_DECORATION, id(name));
    }

    private static ResourceKey<ArmorSkin> skin(final String name) {
        return ResourceKey.create(ArmorPiecesRegistries.ARMOR_SKIN, id(name));
    }

    private static Identifier id(final String name) {
        return Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, name);
    }

    private static SetCloth cloth(final String name, final DyeColor colour) {
        return new SetCloth(ResourceKey.create(ArmorPiecesRegistries.CLOTH, id(name)), colour);
    }

    /** A socket of a set. The varargs are the items handed to the part's fittings, in order. */
    private static SetSocket on(
        final DecorationAnchor anchor,
        final String name,
        final ResourceKey<TrimMaterial> material,
        final SetItem... fittings
    ) {
        return new SetSocket(anchor, part(name), material, List.of(fittings));
    }

    private static SetItem metal(final ResourceKey<TrimMaterial> material) {
        return new SetItem.Material(material);
    }

    private static SetItem dyed(final DyeColor colour) {
        return new SetItem.Dye(colour);
    }

    private static SetItem flag(final DyeColor colour) {
        return new SetItem.Banner(colour);
    }

    /**
     * Six sets, one per theme the parts were authored in - knightly, court, beast, wayfarer, tidal,
     * carapace - each filling all twelve sockets.
     *
     * <p>The themes are the loot groups' (see {@code data/armorpieces/armorpieces/loot_group}), but
     * the parts are NOT confined to a theme's tag: no theme covers all twelve sockets, and a set with
     * a bare waist is not a picture of anything. Where a theme has nothing for a socket the nearest
     * neutral part stands in, which is what a player with that theme's chest loot would end up
     * wearing anyway.
     */
    private static final List<GallerySet> SETS = List.of(
        // Knightly: iron on iron, so every plate part takes the darker variant and reads as one
        // suit, with gold on the guards and one loud red for the crest, the banner and the inlay.
        new GallerySet("knight_errant", EquipmentAssets.IRON, skin("plate"),
            cloth("tabard", DyeColor.WHITE), List.of(
                on(DecorationAnchor.CREST, "brush_crest", TrimMaterials.REDSTONE),
                on(DecorationAnchor.BROW, "great_helm", TrimMaterials.IRON, metal(TrimMaterials.GOLD)),
                on(DecorationAnchor.HORNS, "cheek_guards", TrimMaterials.IRON, metal(TrimMaterials.GOLD)),
                on(DecorationAnchor.PAULDRONS, "spaulders", TrimMaterials.IRON),
                on(DecorationAnchor.BACK, "banner", TrimMaterials.IRON, flag(DyeColor.RED)),
                on(DecorationAnchor.COLLAR, "gorget", TrimMaterials.IRON),
                on(DecorationAnchor.VAMBRACES, "vambraces", TrimMaterials.IRON),
                on(DecorationAnchor.BELT, "girdle", TrimMaterials.IRON, metal(TrimMaterials.GOLD), metal(TrimMaterials.REDSTONE)),
                on(DecorationAnchor.TASSETS, "tassets", TrimMaterials.IRON),
                on(DecorationAnchor.KNEES, "poleyns", TrimMaterials.IRON),
                on(DecorationAnchor.SPURS, "rowel_spurs", TrimMaterials.IRON, metal(TrimMaterials.GOLD)),
                on(DecorationAnchor.GREAVES, "greaves", TrimMaterials.IRON, dyed(DyeColor.RED)))),

        // Court: gold and amethyst throughout, purple everywhere a dye is taken. Greaves has no
        // court part, so the wayfarer's boot cuffs stand in - the only socket the theme cannot fill.
        new GallerySet("high_court", EquipmentAssets.GOLD, skin("runic"),
            cloth("tabard", DyeColor.PURPLE), List.of(
                on(DecorationAnchor.CREST, "feathering", TrimMaterials.QUARTZ),
                on(DecorationAnchor.BROW, "coronet", TrimMaterials.GOLD, metal(TrimMaterials.AMETHYST)),
                on(DecorationAnchor.HORNS, "helm_wings", TrimMaterials.GOLD),
                on(DecorationAnchor.PAULDRONS, "epaulettes", TrimMaterials.GOLD, dyed(DyeColor.PURPLE)),
                on(DecorationAnchor.BACK, "cloak", TrimMaterials.GOLD, flag(DyeColor.PURPLE), metal(TrimMaterials.GOLD)),
                on(DecorationAnchor.COLLAR, "chain_of_office", TrimMaterials.GOLD, metal(TrimMaterials.GOLD), metal(TrimMaterials.AMETHYST)),
                on(DecorationAnchor.VAMBRACES, "bangles", TrimMaterials.GOLD, metal(TrimMaterials.AMETHYST)),
                on(DecorationAnchor.BELT, "sash", TrimMaterials.GOLD, dyed(DyeColor.PURPLE), metal(TrimMaterials.GOLD)),
                on(DecorationAnchor.TASSETS, "loin_panels", TrimMaterials.GOLD, dyed(DyeColor.PURPLE)),
                on(DecorationAnchor.KNEES, "garters", TrimMaterials.GOLD, dyed(DyeColor.PURPLE)),
                on(DecorationAnchor.SPURS, "anklets", TrimMaterials.GOLD, metal(TrimMaterials.AMETHYST)),
                on(DecorationAnchor.GREAVES, "boot_cuffs", TrimMaterials.GOLD, dyed(DyeColor.PURPLE)))),

        // Beast: copper hide and quartz bone, the two of them alternating socket by socket, over the
        // varangian skin. Belt and back have no beast part; a cord and a pair of pinions carry them.
        new GallerySet("wild_hunt", EquipmentAssets.COPPER, skin("varangian"), null, List.of(
            on(DecorationAnchor.CREST, "horsetail", TrimMaterials.COPPER, dyed(DyeColor.BROWN)),
            on(DecorationAnchor.BROW, "bone_mask", TrimMaterials.QUARTZ, metal(TrimMaterials.REDSTONE)),
            on(DecorationAnchor.HORNS, "antlers", TrimMaterials.COPPER),
            on(DecorationAnchor.PAULDRONS, "beast_head", TrimMaterials.COPPER, metal(TrimMaterials.REDSTONE)),
            on(DecorationAnchor.BACK, "pinions", TrimMaterials.COPPER),
            on(DecorationAnchor.COLLAR, "fang_necklace", TrimMaterials.QUARTZ, metal(TrimMaterials.REDSTONE)),
            on(DecorationAnchor.VAMBRACES, "claws", TrimMaterials.QUARTZ, metal(TrimMaterials.COPPER)),
            on(DecorationAnchor.BELT, "cord", TrimMaterials.COPPER, dyed(DyeColor.BROWN)),
            on(DecorationAnchor.TASSETS, "pelt", TrimMaterials.COPPER, dyed(DyeColor.BROWN)),
            on(DecorationAnchor.KNEES, "fanged_cop", TrimMaterials.COPPER, metal(TrimMaterials.REDSTONE)),
            on(DecorationAnchor.SPURS, "talons", TrimMaterials.QUARTZ, metal(TrimMaterials.COPPER)),
            on(DecorationAnchor.GREAVES, "shin_spikes", TrimMaterials.QUARTZ, metal(TrimMaterials.COPPER)))),

        // Wayfarer: leather under a gambeson, everything copper and brown, iron only where a buckle
        // or a spur has to be metal. The crest and the temples have no wayfarer part.
        new GallerySet("far_road", EquipmentAssets.LEATHER, skin("gambeson"),
            cloth("tunic", DyeColor.BROWN), List.of(
                on(DecorationAnchor.CREST, "feathering", TrimMaterials.COPPER),
                on(DecorationAnchor.BROW, "browband", TrimMaterials.COPPER, dyed(DyeColor.BROWN)),
                on(DecorationAnchor.HORNS, "cheek_guards", TrimMaterials.COPPER, metal(TrimMaterials.IRON)),
                on(DecorationAnchor.PAULDRONS, "mantle", TrimMaterials.COPPER, dyed(DyeColor.BROWN)),
                on(DecorationAnchor.BACK, "bedroll", TrimMaterials.COPPER, dyed(DyeColor.BROWN)),
                on(DecorationAnchor.COLLAR, "bandolier", TrimMaterials.COPPER, metal(TrimMaterials.IRON), dyed(DyeColor.BROWN)),
                on(DecorationAnchor.VAMBRACES, "wraps", TrimMaterials.QUARTZ, dyed(DyeColor.BROWN)),
                on(DecorationAnchor.BELT, "pouch_belt", TrimMaterials.COPPER, dyed(DyeColor.BROWN)),
                on(DecorationAnchor.TASSETS, "thigh_sheath", TrimMaterials.COPPER, metal(TrimMaterials.IRON)),
                on(DecorationAnchor.KNEES, "padding", TrimMaterials.COPPER, dyed(DyeColor.BROWN)),
                on(DecorationAnchor.SPURS, "spurs", TrimMaterials.IRON),
                on(DecorationAnchor.GREAVES, "puttees", TrimMaterials.QUARTZ, dyed(DyeColor.BROWN)))),

        // Tidal: diamond and lapis on the scale skin, light blue in every dye. Six sockets have no
        // tidal part at all, which is why this one leans hardest on neutral plate.
        new GallerySet("deep_tide", EquipmentAssets.DIAMOND, skin("scale"), null, List.of(
            on(DecorationAnchor.CREST, "dorsal_fin", TrimMaterials.DIAMOND, dyed(DyeColor.LIGHT_BLUE)),
            on(DecorationAnchor.BROW, "visor", TrimMaterials.DIAMOND),
            on(DecorationAnchor.HORNS, "head_fins", TrimMaterials.DIAMOND, dyed(DyeColor.LIGHT_BLUE)),
            on(DecorationAnchor.PAULDRONS, "lames", TrimMaterials.DIAMOND, metal(TrimMaterials.COPPER)),
            on(DecorationAnchor.BACK, "spine_ridge", TrimMaterials.DIAMOND, metal(TrimMaterials.COPPER)),
            on(DecorationAnchor.COLLAR, "gorget", TrimMaterials.DIAMOND),
            on(DecorationAnchor.VAMBRACES, "bangles", TrimMaterials.DIAMOND, metal(TrimMaterials.LAPIS)),
            on(DecorationAnchor.BELT, "sash", TrimMaterials.LAPIS, dyed(DyeColor.LIGHT_BLUE), metal(TrimMaterials.COPPER)),
            on(DecorationAnchor.TASSETS, "scale_skirt", TrimMaterials.DIAMOND, metal(TrimMaterials.COPPER)),
            on(DecorationAnchor.KNEES, "garters", TrimMaterials.DIAMOND, dyed(DyeColor.LIGHT_BLUE)),
            on(DecorationAnchor.SPURS, "streamers", TrimMaterials.DIAMOND, dyed(DyeColor.LIGHT_BLUE)),
            on(DecorationAnchor.GREAVES, "swim_fins", TrimMaterials.DIAMOND, dyed(DyeColor.LIGHT_BLUE)))),

        // Carapace: netherite and lime over lamellar - the theme has five parts and they are all
        // here, with the beast's claws and talons and a few dark plates filling the other seven.
        new GallerySet("chitin", EquipmentAssets.NETHERITE, skin("lamellar"), null, List.of(
            on(DecorationAnchor.CREST, "antennae", TrimMaterials.NETHERITE, metal(TrimMaterials.EMERALD)),
            on(DecorationAnchor.BROW, "bone_mask", TrimMaterials.NETHERITE, metal(TrimMaterials.EMERALD)),
            on(DecorationAnchor.HORNS, "aerials", TrimMaterials.NETHERITE, dyed(DyeColor.LIME)),
            on(DecorationAnchor.PAULDRONS, "wing_cases", TrimMaterials.NETHERITE, dyed(DyeColor.LIME)),
            on(DecorationAnchor.BACK, "carapace", TrimMaterials.NETHERITE, dyed(DyeColor.LIME)),
            on(DecorationAnchor.COLLAR, "ruff", TrimMaterials.NETHERITE, dyed(DyeColor.LIME)),
            on(DecorationAnchor.VAMBRACES, "claws", TrimMaterials.NETHERITE, metal(TrimMaterials.NETHERITE)),
            on(DecorationAnchor.BELT, "chain_belt", TrimMaterials.NETHERITE, metal(TrimMaterials.NETHERITE)),
            on(DecorationAnchor.TASSETS, "mail_fringe", TrimMaterials.NETHERITE, metal(TrimMaterials.NETHERITE)),
            on(DecorationAnchor.KNEES, "fanged_cop", TrimMaterials.NETHERITE, metal(TrimMaterials.EMERALD)),
            on(DecorationAnchor.SPURS, "talons", TrimMaterials.NETHERITE, metal(TrimMaterials.NETHERITE)),
            on(DecorationAnchor.GREAVES, "shin_spikes", TrimMaterials.NETHERITE, metal(TrimMaterials.NETHERITE)))));

    // ---- layout ---------------------------------------------------------------------------------

    /**
     * One block of the grid: a row per {@link Slot}, a column per material, each stand wearing the
     * single armor piece that owns the row's socket.
     */
    private static int placeBlock(
        final Layout layout,
        final double rowOffset,
        final List<Slot> rows,
        final List<Holder.Reference<TrimMaterial>> materials,
        final BaseArmor base
    ) {
        for (int column = 0; column < materials.size(); column++) {
            layout.label(column, rowOffset - 1.0, materials.get(column).value().description());
        }

        int placed = 0;
        for (int row = 0; row < rows.size(); row++) {
            final Slot slot = rows.get(row);
            layout.label(-1.0, rowOffset + row, slot.label());
            for (int column = 0; column < materials.size(); column++) {
                final Holder.Reference<TrimMaterial> material = materials.get(column);
                final ItemStack piece = base.piece(slot.armorType());
                if (piece.isEmpty()) {
                    continue;
                }
                decorate(piece, slot.anchor(), slot.decoration(), material);
                layout.stand(
                    column,
                    rowOffset + row,
                    Map.of(slot.armorType(), piece),
                    slot.decoration().value().copyWithStyle(material));
                placed++;
            }
        }
        return placed;
    }

    /**
     * Where the stage is built and which way it runs: forward from the caller, columns to their
     * right, every stand turned to face back at them.
     *
     * <p>Snapped to the caller's facing rather than to world axes so the grid always unfolds away
     * from where they are standing and reads left to right from where they asked for it, whichever
     * way they happen to be pointing.
     */
    private record Layout(ServerLevel level, Vec3 origin, Direction right, Direction forward, float yRot) {
        static Layout inFrontOf(final CommandSourceStack source) {
            final Direction forward = Direction.fromYRot(source.getRotation().y);
            return new Layout(
                source.getLevel(),
                source.getPosition().add(forward.getStepX() * ROW_SPACING, 0.0, forward.getStepZ() * ROW_SPACING),
                forward.getClockWise(),
                forward,
                forward.getOpposite().toYRot());
        }

        Vec3 at(final double column, final double row) {
            final double acrossX = this.right.getStepX() * column * COLUMN_SPACING;
            final double acrossZ = this.right.getStepZ() * column * COLUMN_SPACING;
            final double alongX = this.forward.getStepX() * row * ROW_SPACING;
            final double alongZ = this.forward.getStepZ() * row * ROW_SPACING;
            return this.origin.add(acrossX + alongX, 0.0, acrossZ + alongZ);
        }

        /**
         * A dressed stand. Its name is set but NOT shown: two hundred floating captions hide the
         * thing they label, and the row and column headers already say what any stand in the grid is.
         */
        void stand(final double column, final double row, final Map<ArmorType, ItemStack> worn, final Component name) {
            final ArmorStand stand = blank(column, row);
            stand.setCustomName(name);
            worn.forEach((type, piece) -> stand.setItemSlot(type.getSlot(), piece));
            this.level.addFreshEntity(stand);
        }

        /** An invisible stand carrying a floating caption - the stage's row and column headings. */
        void label(final double column, final double row, final Component text) {
            final ArmorStand marker = blank(column, row);
            marker.setInvisible(true);
            marker.setCustomName(text);
            marker.setCustomNameVisible(true);
            this.level.addFreshEntity(marker);
        }

        private ArmorStand blank(final double column, final double row) {
            final Vec3 pos = this.at(column, row);
            final ArmorStand stand = new ArmorStand(this.level, pos.x, pos.y, pos.z);
            stand.absSnapTo(pos.x, pos.y, pos.z, this.yRot, 0.0F);
            stand.setYBodyRot(this.yRot);
            stand.setYHeadRot(this.yRot);
            // No gravity keeps the grid a flat plane over broken ground; with it, the rows scatter
            // down whatever slope they were placed on and the side-by-side reading is lost.
            stand.setNoGravity(true);
            stand.setInvulnerable(true);
            // Arms out: the pauldron and vambrace sockets hang off the arm parts, and a stand with
            // its arms hidden shows those parts floating beside a body that has no arm under them.
            stand.setShowArms(true);
            stand.setNoBasePlate(true);
            stand.addTag(STAGE_TAG);
            return stand;
        }
    }

    // ---- what there is to stage -----------------------------------------------------------------

    /** One row of a block: a part, the socket it is shown in, and so the piece that carries it. */
    private record Slot(DecorationAnchor anchor, Holder.Reference<ArmorDecoration> decoration) {
        ArmorType armorType() {
            return this.anchor.armorType();
        }

        Component label() {
            return this.decoration.value().description().copy()
                .append(Component.literal(" (" + this.anchor.getSerializedName() + ")"));
        }
    }

    /**
     * One block of {@code fittings}: a socketed part, one of its fittings, and everything in the item
     * registry that fills it, in registry order.
     */
    private record FittedSlot(Slot slot, Holder<Fitting> fitting, List<FittingValue> values) {
        Component label() {
            return this.slot.label().copy()
                .append(Component.literal(" - "))
                .append(this.fitting.value().description());
        }
    }

    /**
     * Every (socket, part, fitting) triple the loaded data allows, in {@link #slots} order and then
     * the part's own fitting order - the order the smithing table offers an item to them.
     *
     * <p>A fitting that no item in the registry fills is left out rather than staged as an empty
     * block: the stage shows what the game can produce, and a fitting nothing fills produces nothing.
     */
    private static List<FittedSlot> fittedSlots(final CommandSourceStack source, final @Nullable Holder<ArmorDecoration> only) {
        final List<FittedSlot> blocks = new ArrayList<>();
        for (final Slot slot : slots(source, only)) {
            for (final Holder<Fitting> fitting : slot.decoration().value().fittings()) {
                final List<FittingValue> values = fittingValues(fitting.value());
                if (!values.isEmpty()) {
                    blocks.add(new FittedSlot(slot, fitting, values));
                }
            }
        }
        return blocks;
    }

    /**
     * Every distinct value a fitting takes from some item in the game, found by offering it every
     * item there is. Two items that yield the same value - two stacks of the same dye - count once.
     */
    private static List<FittingValue> fittingValues(final Fitting fitting) {
        final List<FittingValue> values = new ArrayList<>();
        for (final Item item : BuiltInRegistries.ITEM) {
            fitting.accept(new ItemStack(item))
                .filter(value -> !values.contains(value))
                .ifPresent(values::add);
        }
        return values;
    }

    /**
     * Every (socket, part) pair the loaded data allows, head to toe.
     *
     * <p>Anchor order is the enum's, matching the creative tab and the tooltip, so the stage reads
     * down the body in the same order everything else in the mod does.
     */
    private static List<Slot> slots(final CommandSourceStack source, final @Nullable Holder<ArmorDecoration> only) {
        final List<Slot> slots = new ArrayList<>();
        for (final DecorationAnchor anchor : DecorationAnchor.values()) {
            decorations(source)
                .filter(decoration -> only == null || only.value().equals(decoration.value()))
                .filter(decoration -> decoration.value().fits(anchor))
                .forEach(decoration -> slots.add(new Slot(anchor, decoration)));
        }
        return slots;
    }

    /** The parts available in each socket, in anchor order. Sockets no part fits are absent. */
    private static Map<DecorationAnchor, List<Holder.Reference<ArmorDecoration>>> partsByAnchor(
        final CommandSourceStack source
    ) {
        final Map<DecorationAnchor, List<Holder.Reference<ArmorDecoration>>> parts =
            new EnumMap<>(DecorationAnchor.class);
        for (final DecorationAnchor anchor : DecorationAnchor.values()) {
            final List<Holder.Reference<ArmorDecoration>> fitting =
                decorations(source).filter(decoration -> decoration.value().fits(anchor)).toList();
            if (!fitting.isEmpty()) {
                parts.put(anchor, fitting);
            }
        }
        return parts;
    }

    private static Stream<Holder.Reference<ArmorDecoration>> decorations(final CommandSourceStack source) {
        final Registry<ArmorDecoration> registry =
            source.registryAccess().lookupOrThrow(ArmorPiecesRegistries.ARMOR_DECORATION);
        return registry.listElements();
    }

    private static List<Holder.Reference<TrimMaterial>> materials(final CommandSourceStack source) {
        final Registry<TrimMaterial> registry = source.registryAccess().lookupOrThrow(Registries.TRIM_MATERIAL);
        return registry.listElements().toList();
    }

    /**
     * A set of armor sharing one equipment asset - the third axis of {@code bases}.
     *
     * <p>Keyed by ASSET rather than by material name because the asset is what the texture lookup
     * actually consults; two items that share an asset are one base as far as a decoration is
     * concerned, and there is nothing to see in staging both.
     */
    private record BaseArmor(ResourceKey<EquipmentAsset> asset, Map<ArmorType, Item> pieces) {
        boolean has(final ArmorType type) {
            return this.pieces.containsKey(type);
        }

        /** A fresh, undecorated stack for one slot, or empty where this base has no such piece. */
        ItemStack piece(final ArmorType type) {
            final Item item = this.pieces.get(type);
            return item == null ? ItemStack.EMPTY : new ItemStack(item);
        }

        Component name() {
            return Component.literal(this.asset.identifier().toString());
        }
    }

    /**
     * Every base armor set in the game, discovered by walking the item registry for equippables that
     * declare an asset for a humanoid armor slot.
     *
     * <p>Walking rather than listing means modded armor is staged too, and means this does not have
     * to be revisited when vanilla adds a set - the same reason the creative tab walks the decoration
     * registry. Slots outside the four humanoid ones are skipped because no anchor can reach them:
     * horse and wolf armor occupy {@link ArmorType#BODY}, which no socket names.
     */
    private static List<BaseArmor> baseArmors() {
        final Map<ResourceKey<EquipmentAsset>, Map<ArmorType, Item>> found = new LinkedHashMap<>();
        for (final Item item : BuiltInRegistries.ITEM) {
            final Equippable equippable = item.components().get(DataComponents.EQUIPPABLE);
            if (equippable == null) {
                continue;
            }
            final ResourceKey<EquipmentAsset> asset = equippable.assetId().orElse(null);
            final ArmorType type = armorType(equippable.slot());
            if (asset == null || type == null) {
                continue;
            }
            // First item wins: where two items share an asset and a slot, either would render the
            // same, so the registry's own order settles it.
            found.computeIfAbsent(asset, key -> new EnumMap<>(ArmorType.class)).putIfAbsent(type, item);
        }
        return found.entrySet().stream()
            .map(entry -> new BaseArmor(entry.getKey(), entry.getValue()))
            .toList();
    }

    /** The one base an item belongs to, for {@code bases <item>}. Empty if it is not humanoid armor. */
    private static List<BaseArmor> baseArmorsFor(final Item item) {
        final Equippable equippable = item.components().get(DataComponents.EQUIPPABLE);
        final ResourceKey<EquipmentAsset> asset = equippable == null ? null : equippable.assetId().orElse(null);
        if (asset == null) {
            return List.of();
        }
        return baseArmors().stream().filter(base -> base.asset().equals(asset)).toList();
    }

    /**
     * The base worn in the modes that do not vary it. Iron, because no trim material declares a
     * darker variant against it, so every part on it reads at its plain colour.
     */
    private static @Nullable BaseArmor defaultBase() {
        final List<BaseArmor> bases = baseArmors();
        if (bases.isEmpty()) {
            return null;
        }
        return bases.stream()
            .filter(base -> base.asset().equals(EquipmentAssets.IRON))
            .findFirst()
            .orElseGet(() -> bases.stream()
                .filter(base -> ARMOR_TYPES.stream().allMatch(base::has))
                .findFirst()
                .orElse(bases.getFirst()));
    }

    private static @Nullable ArmorType armorType(final EquipmentSlot slot) {
        for (final ArmorType type : ARMOR_TYPES) {
            if (type.getSlot() == slot) {
                return type;
            }
        }
        return null;
    }

    /**
     * Writes one part into one socket of a stack, in place.
     *
     * <p>Goes straight to the component rather than through
     * {@link com.mattjesmc.armorpieces.recipe.SmithingDecorationRecipe#applyDecoration} because that
     * method is the CRAFTING path: it demands a material ingredient item and refuses a no-op, both of
     * which are rules about the smithing table rather than about what a decorated stack looks like.
     * The two invariants that do matter here - the part must declare the socket, and the socket must
     * belong to the piece - hold by construction, since rows are built from {@link
     * ArmorDecoration#fits} and the piece is chosen by {@link DecorationAnchor#armorType}.
     */
    private static void decorate(
        final ItemStack piece,
        final DecorationAnchor anchor,
        final Holder<ArmorDecoration> decoration,
        final Holder<TrimMaterial> material
    ) {
        final ArmorDecorations existing = piece.getOrDefault(ModDataComponents.DECORATIONS, ArmorDecorations.EMPTY);
        piece.set(ModDataComponents.DECORATIONS, existing.with(anchor, new DecorationEntry(material, decoration)));
    }

    /**
     * Sets one fitting of the part in {@code anchor}, in place. Straight to the component for the
     * reason {@link #decorate} gives: {@link com.mattjesmc.armorpieces.recipe.SmithingFittingRecipe}
     * routes by item and refuses a no-op, and a stage wants neither.
     */
    private static void fit(
        final ItemStack piece,
        final DecorationAnchor anchor,
        final Holder<Fitting> fitting,
        final FittingValue value
    ) {
        final ArmorDecorations existing = piece.getOrDefault(ModDataComponents.DECORATIONS, ArmorDecorations.EMPTY);
        final DecorationEntry entry = existing.get(anchor);
        if (entry != null) {
            piece.set(ModDataComponents.DECORATIONS, existing.with(anchor, entry.withFitting(fitting, value)));
        }
    }

    // ---- loot -----------------------------------------------------------------------------------

    /**
     * Rolls {@code table} {@code rolls} times as a chest at the caller's feet and counts what came
     * out of this mod: templates by the part they carry, decorated armor by its item and parts.
     * Everything else the table drops is one line, so the part's share of the chest is visible too.
     *
     * <p>The chest parameter set, because the shipped parts live in chests and it is the set a
     * table needs least; a table wanting more (a mob's, say) has its conditions fail and drops
     * nothing, which the count then shows.
     */
    private static int stageLoot(final CommandSourceStack source, final Holder<LootTable> table, final int rolls) {
        final LootParams params = new LootParams.Builder(source.getLevel())
            .withParameter(LootContextParams.ORIGIN, source.getPosition())
            .create(LootContextParamSets.CHEST);
        final Map<Component, Integer> counts = new LinkedHashMap<>();
        int fromMod = 0;
        int other = 0;
        for (int i = 0; i < rolls; i++) {
            for (final ItemStack stack : table.value().getRandomItems(params)) {
                final Component key = lootKey(stack);
                if (key == null) {
                    other += stack.getCount();
                    continue;
                }
                counts.merge(key, stack.getCount(), Integer::sum);
                fromMod += stack.getCount();
            }
        }

        final String name = table.unwrapKey().map(key -> key.identifier().toString()).orElse("<inline>");
        final int total = fromMod;
        source.sendSuccess(() -> Component.translatable("commands.armorpieces.stage.loot.header", name, rolls, total), false);
        counts.entrySet().stream()
            .sorted(Map.Entry.<Component, Integer>comparingByValue(Comparator.reverseOrder()))
            .forEach(entry -> source.sendSuccess(() -> Component.translatable(
                "commands.armorpieces.stage.loot.line",
                entry.getKey(), entry.getValue(), String.format("%.1f", 100.0 * entry.getValue() / rolls)), false));
        final int rest = other;
        source.sendSuccess(() -> Component.translatable("commands.armorpieces.stage.loot.other", rest), false);
        return fromMod;
    }

    /** What to count a dropped stack as, or null if it is nothing of this mod's. */
    private static @Nullable Component lootKey(final ItemStack stack) {
        if (stack.has(ModDataComponents.DECORATION)) {
            // A template's name already says which part it carries: "Circlet Brow Smithing Template".
            return stack.getHoverName();
        }
        final ArmorDecorations worn = stack.get(ModDataComponents.DECORATIONS);
        if (worn != null && !worn.isEmpty()) {
            final Component parts = worn.entries().values().stream()
                .map(entry -> entry.decoration().value().copyWithStyle(entry.material()))
                .reduce((a, b) -> Component.empty().append(a).append(Component.literal(", ")).append(b))
                .orElse(Component.empty());
            return Component.empty()
                .append(stack.getHoverName())
                .append(Component.literal(" wearing "))
                .append(parts);
        }
        return null;
    }

    // ---- feedback -------------------------------------------------------------------------------

    private static boolean tooMany(final CommandSourceStack source, final int planned) {
        if (planned <= MAX_STANDS) {
            return false;
        }
        source.sendFailure(Component.translatable("commands.armorpieces.stage.too_many", planned, MAX_STANDS));
        return true;
    }

    private static int nothingToStage(final CommandSourceStack source) {
        source.sendFailure(Component.translatable("commands.armorpieces.stage.nothing"));
        return 0;
    }

    private static int finish(final CommandSourceStack source, final int placed) {
        source.sendSuccess(() -> Component.translatable("commands.armorpieces.stage.placed", placed), true);
        return placed;
    }

    /**
     * As {@link #finish}, and says which seed produced it - the only way back to a stage that came
     * out well, since nothing else about a roll is kept.
     */
    private static int finish(final CommandSourceStack source, final int placed, final long seed) {
        source.sendSuccess(
            () -> Component.translatable("commands.armorpieces.stage.placed.seeded", placed, seed), true);
        return placed;
    }
}
