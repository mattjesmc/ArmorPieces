package com.mattjesmc.armorpieces.command;

import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.decoration.fitting.FittingValue;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;
import net.minecraft.commands.CommandBuildContext;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.ResourceArgument;
import net.minecraft.commands.arguments.item.ItemArgument;
import net.minecraft.commands.arguments.item.ItemInput;
import net.minecraft.core.Direction;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.equipment.ArmorType;
import net.minecraft.world.item.equipment.EquipmentAsset;
import net.minecraft.world.item.equipment.EquipmentAssets;
import net.minecraft.world.item.equipment.Equippable;
import net.minecraft.world.item.equipment.trim.TrimMaterial;
import net.minecraft.world.level.entity.EntityTypeTest;
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
 * <p>Five modes, four of them a different slice of the same cross product:
 *
 * <ul>
 *   <li>{@code parts} - one stand per (socketed part x material). The default view: every part in
 *       every colour, each on the single armor piece that owns its socket.</li>
 *   <li>{@code bases} - that same block repeated for every base armor set, because the base's
 *       equipment asset is what selects a material's darker variant (gold on gold), and that
 *       resolution is invisible until the two stand side by side.</li>
 *   <li>{@code full} - one stand per (material x variant) wearing a complete set with every socket
 *       filled, which is where parts that overlap at the joints show themselves.</li>
 *   <li>{@code fittings} - one block per (socketed part x fitting): the part's materials down the
 *       rows, everything the fitting takes across the columns, that fitting filled. The other three
 *       modes leave every fitting empty, which is the part as the socket recipe first makes it; this
 *       is where the masks and the cloth are judged.</li>
 *   <li>{@code clear} - removes what the other four placed, by tag.</li>
 * </ul>
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
                .then(Commands.literal("parts")
                    .executes(ctx -> stageParts(ctx.getSource(), null))
                    .then(Commands.argument("decoration",
                            ResourceArgument.resource(context, ArmorPiecesRegistries.ARMOR_DECORATION))
                        .executes(ctx -> stageParts(ctx.getSource(), decorationArgument(ctx)))))
                .then(Commands.literal("bases")
                    .executes(ctx -> stageBases(ctx.getSource(), null))
                    .then(Commands.argument("base", ItemArgument.item(context))
                        .executes(ctx -> stageBases(ctx.getSource(), ItemArgument.getItem(ctx, "base")))))
                .then(Commands.literal("full")
                    .executes(ctx -> stageFull(ctx.getSource())))
                .then(Commands.literal("fittings")
                    .executes(ctx -> stageFittings(ctx.getSource(), null))
                    .then(Commands.argument("decoration",
                            ResourceArgument.resource(context, ArmorPiecesRegistries.ARMOR_DECORATION))
                        .executes(ctx -> stageFittings(ctx.getSource(), decorationArgument(ctx)))))
                .then(Commands.literal("clear")
                    .executes(ctx -> clear(ctx.getSource())))));
    }

    private static Holder<ArmorDecoration> decorationArgument(final CommandContext<CommandSourceStack> ctx)
        throws CommandSyntaxException {
        return ResourceArgument.getResource(ctx, "decoration", ArmorPiecesRegistries.ARMOR_DECORATION);
    }

    // ---- modes ----------------------------------------------------------------------------------

    /**
     * Every (part, socket) pair down the rows, every trim material across the columns, each stand
     * wearing only the one piece that owns the socket.
     *
     * <p>Rows are pairs rather than parts because a part may declare several sockets, and a spike
     * that sits in both the crest and the heels looks like two different objects depending on which
     * one it is in. Listing it twice is the honest count of what the data can produce.
     */
    private static int stageParts(final CommandSourceStack source, final @Nullable Holder<ArmorDecoration> only) {
        final List<Slot> rows = slots(source, only);
        final List<Holder.Reference<TrimMaterial>> materials = materials(source);
        final BaseArmor base = defaultBase();
        if (rows.isEmpty() || materials.isEmpty() || base == null) {
            return nothingToStage(source);
        }
        if (tooMany(source, rows.size() * materials.size())) {
            return 0;
        }

        final Layout layout = Layout.inFrontOf(source);
        return finish(source, placeBlock(layout, 0.0, rows, materials, base));
    }

    /**
     * The {@code parts} block, repeated once per base armor set.
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
     * One fully decorated set per (material, variant) - every socket on all four pieces filled at
     * once, which is the only view in which parts can be seen to collide.
     *
     * <p>"Variant" exists because sockets hold a different number of parts: the crest has two and the
     * belt one, so a single fully-decorated stand can never show them all. Variant <i>n</i> takes the
     * <i>n</i>th part in every socket, wrapping where a socket has run out, so the row count is the
     * largest socket's part count and every part appears on at least one stand.
     */
    private static int stageFull(final CommandSourceStack source) {
        final Map<DecorationAnchor, List<Holder.Reference<ArmorDecoration>>> parts = partsByAnchor(source);
        final List<Holder.Reference<TrimMaterial>> materials = materials(source);
        final BaseArmor base = defaultBase();
        if (parts.isEmpty() || materials.isEmpty() || base == null) {
            return nothingToStage(source);
        }
        final int variants = parts.values().stream().mapToInt(List::size).max().orElse(0);
        if (tooMany(source, variants * materials.size())) {
            return 0;
        }

        final Layout layout = Layout.inFrontOf(source);
        for (int column = 0; column < materials.size(); column++) {
            layout.label(column, -1.0, materials.get(column).value().description());
        }

        int placed = 0;
        for (int variant = 0; variant < variants; variant++) {
            layout.label(-1.0, variant, Component.translatable("commands.armorpieces.stage.variant", variant + 1));
            for (int column = 0; column < materials.size(); column++) {
                final Holder.Reference<TrimMaterial> material = materials.get(column);
                final Map<ArmorType, ItemStack> worn = new EnumMap<>(ArmorType.class);
                for (final ArmorType type : ARMOR_TYPES) {
                    final ItemStack piece = base.piece(type);
                    if (!piece.isEmpty()) {
                        worn.put(type, piece);
                    }
                }
                for (final var socket : parts.entrySet()) {
                    final ItemStack piece = worn.get(socket.getKey().armorType());
                    if (piece != null) {
                        // Wrapping: a socket with fewer parts than the widest one repeats its own
                        // list rather than sitting empty, so no stand is left half dressed.
                        final List<Holder.Reference<ArmorDecoration>> fitting = socket.getValue();
                        decorate(piece, socket.getKey(), fitting.get(variant % fitting.size()), material);
                    }
                }
                layout.stand(column, variant, worn, material.value().description());
                placed++;
            }
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
    private static int clear(final CommandSourceStack source) {
        final List<? extends Entity> staged = source.getLevel().getEntities(
            EntityTypeTest.<Entity, Entity>forClass(Entity.class),
            entity -> entity.entityTags().contains(STAGE_TAG));
        staged.forEach(Entity::discard);
        source.sendSuccess(() -> Component.translatable("commands.armorpieces.stage.cleared", staged.size()), true);
        return staged.size();
    }

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
}
