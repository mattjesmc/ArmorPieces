package com.mattjesmc.armorpieces.decoration;

import com.mattjesmc.armorpieces.decoration.effect.DecorationEffect;
import com.mattjesmc.armorpieces.identity.Moved;
import com.mattjesmc.armorpieces.identity.Rebind;
import com.mattjesmc.armorpieces.identity.Tolerant;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.decoration.fitting.FittingValue;
import com.mojang.datafixers.util.Pair;
import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.Dynamic;
import com.mojang.serialization.DynamicOps;
import com.mojang.serialization.MapLike;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Consumer;
import net.minecraft.ChatFormatting;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponentGetter;
import net.minecraft.nbt.NbtOps;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.CommonComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipProvider;
import org.jspecify.annotations.Nullable;

/**
 * Every decorative part on one armor piece, keyed by the socket it occupies. The item component
 * payload, stored under {@code armorpieces:decorations}.
 *
 * <p>A map rather than a list because the socket is the identity: applying a new crest replaces the
 * crest and leaves the brow alone, which is both what a player expects and the reason two parts can
 * never fight over the same space. It is a separate component from vanilla's {@code minecraft:trim},
 * so a piece carries its trim and its decorations at once and neither erases the other.
 *
 * <p>Immutable, like every component payload - {@link #with} and {@link #without} return new values.
 */
public record ArmorDecorations(
    Map<DecorationAnchor, DecorationEntry> entries,
    Map<String, Dynamic<?>> unresolved
) implements TooltipProvider {
    public static final ArmorDecorations EMPTY = new ArmorDecorations(Map.of(), Map.of());

    /**
     * One unresolved socket on the wire: its raw data as NBT. {@code Dynamic} is kept rather than a
     * bare {@code Tag} so that a value read in one format is written back in the same one.
     */
    private static final StreamCodec<RegistryFriendlyByteBuf, Dynamic<?>> RAW_STREAM_CODEC =
        ByteBufCodecs.TAG.<RegistryFriendlyByteBuf>cast()
            .map(tag -> new Dynamic<>(NbtOps.INSTANCE, tag), Tolerant::toTag);

    /**
     * Hand-written rather than {@code unboundedMap}, and it cannot fail.
     *
     * <p>The reason is measured and is the whole of {@code docs/plans/compatibility.md} §0: a
     * component that returns a failed {@code DataResult} does not lose the component, it loses the
     * ITEM. A strict map codec here meant that a helmet whose crest named a part the installed packs
     * no longer defined decoded to nothing at all, and the helmet - enchantments, name and history -
     * became empty air the first time the world was opened.
     *
     * <p>So each socket is read on its own, and a socket that cannot be read is kept as the raw data
     * it was written from. Both halves of the pair are tolerated, and the key half matters as much as
     * the value: {@link DecorationAnchor} is a closed enum, so a socket added by a later version and
     * read by an earlier one has no name here, and an enum-keyed map would silently drop it. Hence
     * {@link #unresolved} keyed by the raw string.
     *
     * <p>A socket that fails is offered to {@link DecorationEntry#rebind} first, which is where a
     * moved part is recovered and where the upgrade to the new save format happens - see
     * {@link com.mattjesmc.armorpieces.identity.Tolerant}.
     */
    public static final Codec<ArmorDecorations> CODEC = new Codec<>() {
        @Override
        public <U> DataResult<Pair<ArmorDecorations, U>> decode(final DynamicOps<U> ops, final U input) {
            final Optional<MapLike<U>> map = ops.getMap(input).result();
            if (map.isEmpty()) {
                // Not a map at all, which means something outside this mod corrupted it. Nothing can
                // be keyed, so nothing can be kept - but the ITEM still survives, which is the point.
                return DataResult.success(Pair.of(ArmorDecorations.EMPTY, ops.empty()));
            }
            final Map<DecorationAnchor, DecorationEntry> entries = new LinkedHashMap<>();
            final Map<String, Dynamic<?>> unresolved = new LinkedHashMap<>();
            map.get().entries().forEach(pair -> {
                final Dynamic<U> raw = new Dynamic<>(ops, pair.getSecond());
                final Optional<DecorationAnchor> anchor =
                    DecorationAnchor.CODEC.parse(ops, pair.getFirst()).result();
                final Optional<DecorationEntry> entry = DecorationEntry.CODEC.parse(raw).result()
                    .or(() -> DecorationEntry.rebind(raw));
                if (anchor.isPresent() && entry.isPresent()) {
                    entries.put(anchor.get(), entry.get());
                    return;
                }
                final String key = ops.getStringValue(pair.getFirst()).result()
                    .orElse(UNNAMED_SOCKET);
                unresolved.put(key, raw);
                Rebind.miss(ArmorPiecesRegistries.ARMOR_DECORATION, named(raw, anchor.isPresent()));
            });
            return DataResult.success(
                Pair.of(new ArmorDecorations(entries, unresolved), ops.empty()));
        }

        @Override
        public <U> DataResult<U> encode(
            final ArmorDecorations value, final DynamicOps<U> ops, final U prefix
        ) {
            final Map<U, U> out = new LinkedHashMap<>();
            // Anchor order, not map order, so an item's saved form does not reshuffle when a part is
            // replaced - the same reason the tooltip reads top-down the body.
            for (final DecorationAnchor anchor : DecorationAnchor.values()) {
                final DecorationEntry entry = value.entries.get(anchor);
                if (entry == null) {
                    continue;
                }
                final DataResult<U> encoded = DecorationEntry.CODEC.encodeStart(ops, entry);
                if (encoded.result().isEmpty()) {
                    return DataResult.error(() -> "could not write the " + anchor.getSerializedName()
                        + " socket: " + encoded.error().map(Object::toString).orElse("unknown"));
                }
                out.put(ops.createString(anchor.getSerializedName()), encoded.result().get());
            }
            // Verbatim, through whatever ops is in play - so a socket this installation cannot draw
            // is written back exactly as it was read and comes back the day its pack is installed.
            value.unresolved.forEach((key, raw) ->
                out.put(ops.createString(key), raw.convert(ops).getValue()));
            return ops.mergeToMap(prefix, out);
        }
    };

    /**
     * Both halves travel. The unresolved sockets are sent as raw NBT rather than dropped, because the
     * tooltip that tells a player a part is missing is drawn on the CLIENT, and because a creative
     * client hands stacks back to the server - one that had been sent a hole would write one.
     */
    public static final StreamCodec<RegistryFriendlyByteBuf, ArmorDecorations> STREAM_CODEC =
        StreamCodec.composite(
            ByteBufCodecs.<RegistryFriendlyByteBuf, DecorationAnchor, DecorationEntry, Map<DecorationAnchor, DecorationEntry>>map(
                LinkedHashMap::new, DecorationAnchor.STREAM_CODEC, DecorationEntry.STREAM_CODEC),
            ArmorDecorations::entries,
            ByteBufCodecs.<RegistryFriendlyByteBuf, String, Dynamic<?>, Map<String, Dynamic<?>>>map(
                LinkedHashMap::new, ByteBufCodecs.STRING_UTF8, RAW_STREAM_CODEC),
            ArmorDecorations::unresolved,
            ArmorDecorations::new);

    private static final Component DECORATED_TITLE =
        Component.translatable("item.armorpieces.decorated").withStyle(ChatFormatting.GRAY);

    /** The key an unresolved socket is filed under when even its name could not be read as a string. */
    private static final String UNNAMED_SOCKET = "?";

    public ArmorDecorations {
        entries = Map.copyOf(entries);
        unresolved = Map.copyOf(unresolved);
    }

    /** Decorations with nothing missing - what every caller inside this mod builds. */
    public ArmorDecorations(final Map<DecorationAnchor, DecorationEntry> entries) {
        this(entries, Map.of());
    }

    /** What the raw socket named, for the log and the tally. */
    private static String named(final Dynamic<?> raw, final boolean anchorKnown) {
        return raw.get("decoration").asString().result()
            .orElse(anchorKnown ? "an unreadable part" : "a socket this version has no name for");
    }

    public boolean isEmpty() {
        return this.entries.isEmpty() && this.unresolved.isEmpty();
    }

    /** How many sockets hold something this installation cannot name. */
    public int unresolvedCount() {
        return this.unresolved.size();
    }

    /** What those sockets named, for the tooltip's advanced line and for {@code /armorpieces missing}. */
    public List<String> unresolvedNames() {
        return this.unresolved.values().stream().map(raw -> named(raw, true)).sorted().toList();
    }

    /**
     * This value with every unresolved socket dropped - the only thing in the mod that destroys one,
     * and it is reachable exclusively from {@code /armorpieces prune}, by an operator, after being
     * shown what it would drop.
     */
    public ArmorDecorations pruned() {
        return this.unresolved.isEmpty() ? this : new ArmorDecorations(this.entries, Map.of());
    }

    public @Nullable DecorationEntry get(final DecorationAnchor anchor) {
        return this.entries.get(anchor);
    }

    /**
     * This value with {@code anchor} set to {@code entry}, replacing whatever occupied it - including
     * an unresolved socket, which is what makes "wait for the pack, or just apply a new part" a real
     * choice rather than a dead end. A player is never stuck with a hole.
     */
    public ArmorDecorations with(final DecorationAnchor anchor, final DecorationEntry entry) {
        final var copy = new LinkedHashMap<>(this.entries);
        copy.put(anchor, entry);
        return new ArmorDecorations(copy, without(this.unresolved, anchor));
    }

    /** This value with {@code anchor} emptied. {@link Optional#empty()} if it was already empty. */
    public Optional<ArmorDecorations> without(final DecorationAnchor anchor) {
        final boolean held = this.entries.containsKey(anchor);
        final Map<String, Dynamic<?>> raw = without(this.unresolved, anchor);
        if (!held && raw.size() == this.unresolved.size()) {
            return Optional.empty();
        }
        final var copy = new LinkedHashMap<>(this.entries);
        copy.remove(anchor);
        return Optional.of(new ArmorDecorations(copy, raw));
    }

    private static Map<String, Dynamic<?>> without(
        final Map<String, Dynamic<?>> raw, final DecorationAnchor anchor
    ) {
        if (!raw.containsKey(anchor.getSerializedName())) {
            return raw;
        }
        final var copy = new LinkedHashMap<>(raw);
        copy.remove(anchor.getSerializedName());
        return copy;
    }

    /**
     * Tooltip lines, shaped to sit directly under a trim's without looking like a different feature:
     * one heading, then an indented "<material> <part>" line per socket. Anchor order is the enum's
     * declaration order (crest, brow, horns...) rather than map order, so the list reads top-down the
     * body and does not reshuffle when a part is replaced.
     */
    @Override
    public void addToTooltip(
        final Item.TooltipContext context,
        final Consumer<Component> consumer,
        final TooltipFlag flag,
        final DataComponentGetter components
    ) {
        if (this.isEmpty()) {
            return;
        }
        consumer.accept(DECORATED_TITLE);
        for (final DecorationAnchor anchor : DecorationAnchor.values()) {
            final DecorationEntry entry = this.entries.get(anchor);
            if (entry == null) {
                continue;
            }
            consumer.accept(CommonComponents.space()
                .append(entry.decoration().value().copyWithStyle(entry.material())));
            // What the part DOES, one line each, above what is set in it - a wearer cares more about
            // the armor point than about the gem that grants it. The numbers are the ones this part
            // in this material actually gives, since a value may scale with the material. Nearly
            // every part contributes nothing and adds no line at all.
            for (final DecorationEffect effect : entry.decoration().value().effects()) {
                consumer.accept(CommonComponents.space().append(CommonComponents.space())
                    .append(effect.description(entry.material()).copy().withStyle(ChatFormatting.BLUE)));
            }
            // What is set in the part's fittings, one line each under the part, in the part's own
            // order rather than the map's so the list is stable across re-fittings. An empty fitting
            // is not listed: a circlet without its stone is still just a circlet.
            for (final Holder<Fitting> fitting : entry.decoration().value().fittings()) {
                final FittingValue value = entry.fitting(fitting);
                if (value != null) {
                    consumer.accept(CommonComponents.space().append(CommonComponents.space())
                        .append(Component.translatable(
                            "item.armorpieces.fitting", fitting.value().description(), value.name())
                            .withStyle(ChatFormatting.GRAY)));
                }
            }
        }
        // Last, and only when there is something to say. The count is the difference between a player
        // thinking the mod is broken and a player knowing something is absent; the ids under it are
        // the difference between knowing that and being able to do anything about it, which is why
        // they are on the face of the tooltip and not behind F3+H - see docs/plans/compatibility.md
        // section 5.1. A part is three JSON files and a PNG, so an id is a complete instruction even
        // to a player who cannot get the pack.
        if (!this.unresolved.isEmpty()) {
            consumer.accept(CommonComponents.space()
                .append(Component.translatable("item.armorpieces.missing_parts", this.unresolved.size())
                    .withStyle(ChatFormatting.DARK_GRAY)));
            final List<String> names = this.unresolvedNames();
            // Twelve sockets can all be missing at once, and twelve lines is a wall. Four covers
            // every case anyone actually meets; the advanced tooltip is where the rest belongs.
            final int shown = flag.isAdvanced() ? names.size() : Math.min(names.size(), MISSING_SHOWN);
            for (int index = 0; index < shown; index++) {
                consumer.accept(CommonComponents.space().append(CommonComponents.space())
                    .append(Moved.describe(names.get(index)).copy().withStyle(ChatFormatting.DARK_GRAY)));
            }
            if (shown < names.size()) {
                consumer.accept(CommonComponents.space().append(CommonComponents.space())
                    .append(Component.translatable("item.armorpieces.missing_more", names.size() - shown)
                        .withStyle(ChatFormatting.DARK_GRAY)));
            }
        }
    }

    /** How many missing ids an ordinary tooltip names before it says "+n more". */
    private static final int MISSING_SHOWN = 4;
}
