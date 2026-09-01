package com.mattjesmc.armorpieces.decoration;

import com.mojang.serialization.Codec;
import java.util.Map;
import java.util.Optional;
import java.util.function.Consumer;
import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponentGetter;
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
public record ArmorDecorations(Map<DecorationAnchor, DecorationEntry> entries) implements TooltipProvider {
    public static final ArmorDecorations EMPTY = new ArmorDecorations(Map.of());

    public static final Codec<ArmorDecorations> CODEC =
        Codec.unboundedMap(DecorationAnchor.CODEC, DecorationEntry.CODEC)
            .xmap(ArmorDecorations::new, ArmorDecorations::entries);
    // The type witness pins M to Map rather than letting inference settle on LinkedHashMap, which
    // would force entries() to return the concrete type just to satisfy the encoder.
    public static final StreamCodec<RegistryFriendlyByteBuf, ArmorDecorations> STREAM_CODEC =
        ByteBufCodecs.<RegistryFriendlyByteBuf, DecorationAnchor, DecorationEntry, Map<DecorationAnchor, DecorationEntry>>map(
                java.util.LinkedHashMap::new, DecorationAnchor.STREAM_CODEC, DecorationEntry.STREAM_CODEC)
            .map(ArmorDecorations::new, ArmorDecorations::entries);

    private static final Component DECORATED_TITLE =
        Component.translatable("item.armorpieces.decorated").withStyle(ChatFormatting.GRAY);

    public ArmorDecorations {
        entries = Map.copyOf(entries);
    }

    public boolean isEmpty() {
        return this.entries.isEmpty();
    }

    public @Nullable DecorationEntry get(final DecorationAnchor anchor) {
        return this.entries.get(anchor);
    }

    /** This value with {@code anchor} set to {@code entry}, replacing whatever occupied it. */
    public ArmorDecorations with(final DecorationAnchor anchor, final DecorationEntry entry) {
        final var copy = new java.util.LinkedHashMap<>(this.entries);
        copy.put(anchor, entry);
        return new ArmorDecorations(copy);
    }

    /** This value with {@code anchor} emptied. {@link Optional#empty()} if it was already empty. */
    public Optional<ArmorDecorations> without(final DecorationAnchor anchor) {
        if (!this.entries.containsKey(anchor)) {
            return Optional.empty();
        }
        final var copy = new java.util.LinkedHashMap<>(this.entries);
        copy.remove(anchor);
        return Optional.of(new ArmorDecorations(copy));
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
        if (this.entries.isEmpty()) {
            return;
        }
        consumer.accept(DECORATED_TITLE);
        for (final DecorationAnchor anchor : DecorationAnchor.values()) {
            final DecorationEntry entry = this.entries.get(anchor);
            if (entry != null) {
                consumer.accept(CommonComponents.space()
                    .append(entry.decoration().value().copyWithStyle(entry.material())));
            }
        }
    }
}
