package com.mattjesmc.armorpieces.loot;

import com.mojang.datafixers.util.Either;
import com.mojang.serialization.Codec;
import java.util.List;
import java.util.Optional;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderGetter;
import net.minecraft.core.HolderSet;
import net.minecraft.core.Registry;
import net.minecraft.core.RegistryCodecs;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.TagKey;

/**
 * A set of registry members named by a loot file: a TAG, resolved when it is used, or a list of ids
 * bound when the file is read.
 *
 * <p>This exists for one reason, and it is the difference between a modpack's loot table working and
 * failing to parse. The ordinary way to write a set of members is {@link RegistryCodecs#homogeneousList},
 * which binds everything at read time - and a tag that no installed pack ships is then a MISSING TAG
 * and a hard error, taking the whole loot table with it. That is exactly backwards for the thing
 * these entries are for: a table saying "one of the knightly parts, if that pack is here". So a tag
 * written here is kept as a {@link TagKey} and looked up at the moment it is needed, where an absent
 * tag is simply an empty set and the entry that named it drops out.
 *
 * <p>A list of ids keeps the ordinary binding behaviour, because a file naming an exact id means it:
 * a typo there should be an error, not a silent nothing.
 *
 * @param tag    the tag, if that is how it was written. Never resolved here.
 * @param direct the members, if they were written as ids. Empty when {@link #tag} is present.
 */
public record MemberSet<T>(Optional<TagKey<T>> tag, HolderSet<T> direct) {
    /** Names nothing, which is what an absent field means. */
    public static <T> MemberSet<T> empty() {
        return new MemberSet<>(Optional.empty(), HolderSet.direct(List.of()));
    }

    /**
     * {@code "#ns:tag"}, {@code "ns:member"} or a list of ids - the same three forms every other
     * member field in this mod takes, so nothing about how a file is written changes.
     */
    public static <T> Codec<MemberSet<T>> codec(final ResourceKey<Registry<T>> registry) {
        return Codec.either(TagKey.hashedCodec(registry), RegistryCodecs.homogeneousList(registry))
            .xmap(
                either -> either.map(
                    tag -> new MemberSet<T>(Optional.of(tag), HolderSet.direct(List.of())),
                    set -> new MemberSet<T>(Optional.empty(), set)),
                members -> members.tag()
                    .<Either<TagKey<T>, HolderSet<T>>>map(Either::left)
                    .orElseGet(() -> Either.right(members.direct())));
    }

    /** Whether the file named anything at all - as opposed to leaving the field out. */
    public boolean named() {
        return this.tag.isPresent() || this.direct.size() > 0;
    }

    /**
     * The members, now. An empty list where a tag was named that no pack ships, or that is itself
     * empty - the two cases this class exists to make survivable.
     */
    public List<Holder<T>> resolve(final HolderGetter.Provider registries) {
        if (this.tag.isEmpty()) {
            return this.direct.stream().toList();
        }
        return registries.get(this.tag.get())
            .<List<Holder<T>>>map(set -> set.stream().toList())
            .orElse(List.of());
    }

    /** How it was written, for a log line or a command's output. */
    public String describe() {
        return this.tag
            .map(tag -> "#" + tag.location())
            .orElseGet(() -> this.direct.stream()
                .map(holder -> holder.unwrapKey().map(key -> key.identifier().toString()).orElse("<inline>"))
                .toList()
                .toString());
    }
}
