package com.mattjesmc.armorpieces.identity;

import com.mojang.datafixers.util.Pair;
import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.Dynamic;
import com.mojang.serialization.DynamicOps;
import java.util.List;
import java.util.Optional;
import java.util.function.Consumer;
import java.util.function.Function;
import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponentGetter;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.network.chat.Component;
import net.minecraft.nbt.NbtOps;
import net.minecraft.nbt.Tag;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipProvider;
import org.jspecify.annotations.Nullable;

/**
 * A value, or the raw data of one this installation cannot make sense of.
 *
 * <p>The one rule this type exists to keep: <b>no component of this mod may ever fail to decode.</b>
 *
 * <p>That rule is not tidiness. A component's codec is run inside {@code DataComponentPatch}'s, which
 * is strict, which is run inside {@code ItemStack}'s - so a component that returns a failed
 * {@code DataResult} does not lose the component, it loses <i>the item</i>. Measured, with a diamond
 * helmet and one part id that nothing defined: {@code ItemStack.CODEC.parse} returned an error and no
 * partial at all. Every caller that loads a saved stack turns that into a logged line and empty air,
 * so a player who wore a decorated helmet through a version that dropped the part loses the helmet,
 * its enchantments and its name. See {@code docs/plans/compatibility.md} §0.
 *
 * <p>So a tolerant codec never fails. It tries the real codec; if that misses, it asks {@link Rebind}
 * whether the thing has merely moved; and if that misses too it keeps the bytes exactly as they were
 * read, hands back a value that renders nothing and does nothing, and writes the same bytes out again
 * on save. Install the pack a month later and the piece comes back, because resolution is attempted
 * on every decode rather than once at a migration.
 *
 * <p><b>The upgrade rides on this.</b> {@code DataComponentPatch} re-encodes from the DECODED value,
 * not from the bytes it read - so an entry that was rebound here is written back in its new form the
 * next time the item is saved. That is the whole of "port to the new save format": no world sweep, no
 * data version to track, no conversion step that can half-finish.
 *
 * @param value the thing, if this installation could name it
 * @param raw   the data it was read from, if it could not. Exactly one of the two is present.
 */
public record Tolerant<T>(Optional<T> value, Optional<Dynamic<?>> raw) implements TooltipProvider {
    public Tolerant {
        if (value.isPresent() == raw.isPresent()) {
            throw new IllegalArgumentException("a Tolerant is either resolved or raw, never both or neither");
        }
    }

    /** The ordinary case: something this installation knows. */
    public static <T> Tolerant<T> of(final T value) {
        return new Tolerant<>(Optional.of(value), Optional.empty());
    }

    /** Something it does not, kept verbatim so that installing the pack later brings it back. */
    public static <T> Tolerant<T> unresolved(final Dynamic<?> raw) {
        return new Tolerant<>(Optional.empty(), Optional.of(raw));
    }

    /** Whether this is a value rather than a hole. */
    public boolean isResolved() {
        return this.value.isPresent();
    }

    /** The value, or {@code null} if this installation cannot name it. */
    public @Nullable T orNull() {
        return this.value.orElse(null);
    }

    /**
     * What the raw data called itself, for the warning and the tally - the whole string if it is one
     * (a bare holder is written as its id), otherwise the {@code field} of the object it is.
     */
    public Optional<String> rawName(final String field) {
        return this.raw.flatMap(dynamic -> dynamic.asString().result()
            .or(() -> dynamic.get(field).asString().result()));
    }

    /**
     * Wraps {@code inner} so that it cannot fail.
     *
     * @param inner    the real codec, tried first
     * @param rebinder asked when {@code inner} misses: given the raw data, it returns the value the
     *                 piece has moved to, or empty. Pass {@code d -> Optional.empty()} for a type
     *                 that is kept but never rebound.
     */
    public static <T> Codec<Tolerant<T>> codec(
        final Codec<T> inner,
        final Function<Dynamic<?>, Optional<T>> rebinder
    ) {
        return new Codec<>() {
            @Override
            public <U> DataResult<Pair<Tolerant<T>, U>> decode(final DynamicOps<U> ops, final U input) {
                // result(), not resultOrPartial(): a half-decoded value is a value we do not trust,
                // and keeping the raw is always recoverable where guessing is not.
                final Optional<Pair<T, U>> direct = inner.decode(ops, input).result();
                if (direct.isPresent()) {
                    return DataResult.success(direct.get().mapFirst(Tolerant::of));
                }
                final Dynamic<U> raw = new Dynamic<>(ops, input);
                return DataResult.success(Pair.of(
                    rebinder.apply(raw).map(Tolerant::of).orElseGet(() -> Tolerant.unresolved(raw)),
                    ops.empty()));
            }

            @Override
            public <U> DataResult<U> encode(final Tolerant<T> value, final DynamicOps<U> ops, final U prefix) {
                if (value.value.isPresent()) {
                    return inner.encode(value.value.get(), ops, prefix);
                }
                // convert() walks the raw through whatever ops is in play - NBT on save, JSON in a
                // command - so an unresolved value survives being written in a format it was not
                // read in.
                return DataResult.success(value.raw.orElseThrow().convert(ops).getValue());
            }

            @Override
            public String toString() {
                return "Tolerant[" + inner + "]";
            }
        };
    }

    /**
     * The wire form: a flag, then either the value or its raw NBT.
     *
     * <p>The raw travels rather than being dropped, for two reasons. The tooltip that tells a player
     * a part is missing is drawn on the CLIENT, from the synced component; and a creative-mode client
     * hands stacks back to the server, so a client that had been sent a hole would write one.
     */
    public static <B extends RegistryFriendlyByteBuf, T> StreamCodec<B, Tolerant<T>> stream(
        final StreamCodec<? super B, T> inner
    ) {
        return new StreamCodec<>() {
            @Override
            public Tolerant<T> decode(final B buffer) {
                if (buffer.readBoolean()) {
                    return Tolerant.of(inner.decode(buffer));
                }
                return Tolerant.unresolved(new Dynamic<>(NbtOps.INSTANCE, ByteBufCodecs.TAG.decode(buffer)));
            }

            @Override
            public void encode(final B buffer, final Tolerant<T> value) {
                buffer.writeBoolean(value.isResolved());
                if (value.value.isPresent()) {
                    inner.encode(buffer, value.value.get());
                } else {
                    ByteBufCodecs.TAG.encode(buffer, toTag(value.raw.orElseThrow()));
                }
            }
        };
    }

    /**
     * What a stack holds under a tolerant component, resolved - or {@code null}.
     *
     * <p>One null for two situations on purpose: the component is absent, or it is present and names
     * something this installation cannot make sense of. Every reader in the mod wants the same answer
     * to both - draw nothing, name nothing, offer nothing - and the ONE place that must tell them
     * apart is the tooltip, which reads the wrapper itself and says a pack is missing.
     */
    public static <T> @Nullable T get(
        final DataComponentGetter components,
        final DataComponentType<Tolerant<T>> type
    ) {
        final Tolerant<T> value = components.get(type);
        return value == null ? null : value.orNull();
    }

    /** The raw as NBT, for the wire and for the map that keeps unresolved sockets. */
    public static Tag toTag(final Dynamic<?> raw) {
        return raw.convert(NbtOps.INSTANCE).getValue();
    }

    /**
     * Delegates to the value when there is one, and otherwise names what is missing in one grey line.
     *
     * <p>A component that wraps a {@link TooltipProvider} keeps its tooltip - a skinned chestplate
     * still says which skin - and one that cannot be resolved says the two useful things there are to
     * say: the id it holds, and the pack that id belongs to where {@link Moved} can place it. Without
     * the line a player sees plain armor and concludes the mod is broken; without the id they know it
     * is broken and still cannot act.
     */
    @Override
    public void addToTooltip(
        final Item.TooltipContext context,
        final Consumer<Component> consumer,
        final TooltipFlag flag,
        final DataComponentGetter components
    ) {
        if (this.value.isPresent()) {
            if (this.value.get() instanceof TooltipProvider provider) {
                provider.addToTooltip(context, consumer, flag, components);
            }
            return;
        }
        consumer.accept(this.rawId()
            .<Component>map(id -> Component
                .translatable("item.armorpieces.not_installed_named", Moved.describe(id))
                .withStyle(ChatFormatting.DARK_GRAY))
            .orElse(NOT_INSTALLED));
    }

    /**
     * The id the raw data names, however this component happens to write one.
     *
     * <p>Three of the four tolerant components are a bare holder, which is written as its id and needs
     * no field at all; {@code cloth} is an object, because a garment carries a dye and banner layers
     * beside its id. Hence the short list rather than a parameter: {@link #addToTooltip} is handed no
     * clue which component it belongs to, and this is a label, so guessing wrong costs a grey line
     * that says "Not installed" instead of naming an id.
     */
    public Optional<String> rawId() {
        return this.raw.flatMap(dynamic -> dynamic.asString().result()
            .or(() -> ID_FIELDS.stream()
                .flatMap(field -> dynamic.get(field).asString().result().stream())
                .findFirst()));
    }

    /** The id-bearing field of every tolerant component that is not a bare holder. */
    private static final List<String> ID_FIELDS = List.of("cloth", "decoration", "skin", "fitting");

    private static final Component NOT_INSTALLED =
        Component.translatable("item.armorpieces.not_installed").withStyle(ChatFormatting.DARK_GRAY);
}
