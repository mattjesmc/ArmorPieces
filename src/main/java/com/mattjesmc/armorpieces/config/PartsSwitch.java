package com.mattjesmc.armorpieces.config;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.pack.BuiltinPacks;
import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.List;
import java.util.Optional;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderGetter;
import net.minecraft.core.HolderSet;
import net.minecraft.core.Registry;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.Level;
import org.jspecify.annotations.Nullable;

/**
 * The {@code parts} section of the server owner's file: which of the installed content this world
 * OFFERS. The switch of {@code docs/plans/additive-packs.md}.
 *
 * <p>Every pack is additive - a pack may only define ids that nothing else defines - and the other
 * half of that rule is that removing content is never a pack. A server that does not want the mod's
 * own knightly parts, or one pack's dragon, says so here, by id or by tag, and the pieces stop being
 * OFFERED: not in a chest, not on the creative tab, not at either smithing table, and the template
 * that would craft one is not a recipe.
 *
 * <p><b>Disabled is not uninstalled.</b> A piece already on a player's helmet is still decoded and
 * still drawn, and its data file still loads. The moment disabling stopped a worn piece from
 * rendering, the 0.4.0 split's break - a part a world can no longer read - would have been rebuilt as
 * a setting, and everything {@code docs/plans/compatibility.md} did to make a read that cannot fail
 * would be undone by a line in a config file. So this class answers exactly one question,
 * {@link #offers}, and nothing on the read or render path asks it.
 *
 * <h2>Shape on disk</h2>
 *
 * <pre>{@code
 * "parts": {
 *   "mod_parts": true,
 *   "disabled": [ "armorpieces:visor", "#armorpieces:knightly", "armorpieces_dragon:dragon_wings" ]
 * }
 * }</pre>
 *
 * <p>{@code disabled} takes an id or a {@code #tag} of ANY of the four content registries - parts,
 * skins, cloths and fittings - so one list serves all of them and a server owner never has to know
 * which registry a name is in. A tag is resolved when it is asked, against the registries of the
 * moment (a loot table being built, a recipe being kept, a player's smithing table), so a tag whose
 * members change on {@code /reload} disables what it holds now.
 *
 * <p><b>Reaching the client.</b> This is a server setting, and the creative tab is built on the
 * client out of the client's own copy of the registries. So the server tells each player its
 * {@code parts} section as they join and again after every datapack reload
 * ({@link com.mattjesmc.armorpieces.network.PartsSwitchPayload}), and {@link #shown()} is what the
 * tab reads: the server's word while connected, this JVM's own file otherwise.
 *
 * @param modParts whether the mod's own content - the {@code armorpieces} namespace and the three
 *                 built-in packs' ({@link BuiltinPacks#isModContent}) - is offered at all.
 *                 {@code false} is the one-line way to run a server on other packs alone.
 * @param disabled ids and tags, in any of the four content registries, that are not offered.
 */
public record PartsSwitch(boolean modParts, List<Member> disabled) {
    public static final PartsSwitch DEFAULT = new PartsSwitch(true, List.of());

    public static final Codec<PartsSwitch> CODEC = RecordCodecBuilder.create(i ->
        i.group(
            Codec.BOOL.optionalFieldOf("mod_parts", DEFAULT.modParts()).forGetter(PartsSwitch::modParts),
            Member.CODEC.listOf().optionalFieldOf("disabled", List.of()).forGetter(PartsSwitch::disabled)
        ).apply(i, PartsSwitch::new));

    /** Every field mandatory, for the same reason {@code ArmorPiecesServerConfig.WRITE_CODEC} is. */
    static final Codec<PartsSwitch> WRITE_CODEC = RecordCodecBuilder.create(i ->
        i.group(
            Codec.BOOL.fieldOf("mod_parts").forGetter(PartsSwitch::modParts),
            Member.CODEC.listOf().fieldOf("disabled").forGetter(PartsSwitch::disabled)
        ).apply(i, PartsSwitch::new));

    public static final StreamCodec<RegistryFriendlyByteBuf, PartsSwitch> STREAM_CODEC =
        ByteBufCodecs.fromCodecWithRegistries(CODEC);

    public PartsSwitch {
        disabled = List.copyOf(disabled);
    }

    /** Whether this switch turns anything off at all. The fast path everything asks first. */
    public boolean restricts() {
        return !this.modParts || !this.disabled.isEmpty();
    }

    /**
     * Whether {@code member} is offered - found, crafted, listed - on this server.
     *
     * <p>An inline holder (one with no registry key) is always offered: it is not a thing a file
     * could name. A tag is looked up in the member's own registry through {@code registries}, which
     * is the caller's view of the moment - the loading provider while loot tables are built, the
     * level's while a recipe runs - and compared by key rather than by holder, because two lookups
     * over one registry do not promise the same {@link Holder} instances.
     */
    public boolean offers(final Holder<?> member, final HolderGetter.Provider registries) {
        if (!this.restricts()) {
            return true;
        }
        final Optional<? extends ResourceKey<?>> unwrapped = member.unwrapKey();
        if (unwrapped.isEmpty()) {
            return true;
        }
        final ResourceKey<?> key = unwrapped.get();
        if (!this.modParts && BuiltinPacks.isModContent(key.identifier().getNamespace())) {
            return false;
        }
        for (final Member rule : this.disabled) {
            if (rule.disables(key, registries)) {
                return false;
            }
        }
        return true;
    }

    /**
     * {@link #offers}, asked of the switch in force on whichever side this is, for the code that
     * runs on both: a recipe's {@code matches}, the creative tab. The level is not touched unless
     * the switch has something to say, so a recipe test with no level to give still runs.
     */
    public static boolean offeredIn(final Holder<?> member, final Level level) {
        final PartsSwitch shown = shown();
        return !shown.restricts() || shown.offers(member, level.registryAccess());
    }

    // ---- the client's copy ------------------------------------------------------------------

    private static @Nullable PartsSwitch synced;

    /**
     * The switch a client should show: what the server it is on last said, or - off any server, or
     * before it has said anything - the settings in force in this JVM, which on the integrated
     * server are the same file.
     */
    public static PartsSwitch shown() {
        final PartsSwitch told = synced;
        return told != null ? told : ArmorPiecesServerConfig.get().parts();
    }

    /** What the server just said, or null on leaving it. Called by the client's packet handler. */
    public static void told(final @Nullable PartsSwitch switch_) {
        synced = switch_;
    }

    /**
     * One line of {@code disabled}: {@code "ns:name"} or {@code "#ns:tag"}, in whichever of the four
     * content registries holds it. Kept as it was written; nothing is bound until it is asked.
     *
     * @param id  the id, or the tag's id.
     * @param tag whether the line began with {@code #}.
     */
    public record Member(Identifier id, boolean tag) {
        public static final Codec<Member> CODEC = Codec.STRING.comapFlatMap(Member::parse, Member::toString);

        static DataResult<Member> parse(final String written) {
            final boolean tag = written.startsWith("#");
            return Identifier.read(tag ? written.substring(1) : written)
                .map(id -> new Member(id, tag));
        }

        @Override
        public String toString() {
            return (this.tag ? "#" : "") + this.id;
        }

        /** Whether this line names {@code key}: the id itself, or a tag it is in right now. */
        boolean disables(final ResourceKey<?> key, final HolderGetter.Provider registries) {
            if (!this.tag) {
                return this.id.equals(key.identifier());
            }
            return inTag(key, registries);
        }

        @SuppressWarnings({"unchecked", "rawtypes"})
        private boolean inTag(final ResourceKey<?> key, final HolderGetter.Provider registries) {
            // The tag is in the member's own registry, whichever that is: a rule written once
            // serves parts, skins, cloths and fittings alike, and a tag no pack defines in that
            // registry is simply not one the member is in.
            final ResourceKey<? extends Registry<?>> registry = key.registryKey();
            final Optional<HolderSet.Named<Object>> named = registries
                .lookup((ResourceKey) registry)
                .flatMap(getter -> ((HolderGetter<Object>) getter).get(TagKey.create((ResourceKey) registry, this.id)));
            return named.isPresent() && named.get().stream()
                .anyMatch(holder -> holder.unwrapKey().filter(key::equals).isPresent());
        }
    }
}
