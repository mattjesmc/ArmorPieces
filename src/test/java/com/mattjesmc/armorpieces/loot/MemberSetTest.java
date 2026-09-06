package com.mattjesmc.armorpieces.loot;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonElement;
import com.google.gson.JsonPrimitive;
import com.mojang.serialization.Codec;
import com.mojang.serialization.JsonOps;
import java.util.List;
import java.util.Optional;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderGetter;
import net.minecraft.core.HolderSet;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import org.junit.jupiter.api.Test;

/**
 * A tag nobody installed is an empty set, not a broken loot table.
 *
 * <p>The third of the 0.4.0 traps, and the one that defeats the point of the feature rather than a
 * number in a file: {@code RegistryCodecs.homogeneousList} binds its members when the file is READ,
 * so a tag no installed pack ships is a hard parse error - and it takes the whole loot table down
 * with it. A group saying "one of the knightly parts, if that pack is here" then breaks the chest it
 * was added to. {@link MemberSet} keeps a tag as a {@link TagKey} and asks for it at the moment it
 * is used, which is the behaviour asserted here: a missing tag resolves to nothing and the caller
 * carries on.
 *
 * <p>A list of ids keeps the eager binding on purpose - a typo there should be an error - so the
 * only thing this test says about that form is that it resolves to what it holds.
 */
class MemberSetTest {
    private static final Codec<MemberSet<Item>> CODEC = MemberSet.codec(Registries.ITEM);

    /** A world where no tag exists at all - the situation the class is for, at its extreme. */
    private static final HolderGetter.Provider NOTHING_INSTALLED = new HolderGetter.Provider() {
        @Override
        public <T> Optional<HolderGetter<T>> lookup(final ResourceKey<? extends Registry<? extends T>> registry) {
            return Optional.empty();
        }
    };

    @Test
    void aTagIsReadWithoutBeingResolved() {
        final JsonElement json = new JsonPrimitive("#armorpieces:knightly");
        final MemberSet<Item> members = CODEC.parse(JsonOps.INSTANCE, json).getOrThrow();

        assertTrue(members.tag().isPresent(), "written as a tag, so it should still be a tag");
        assertEquals(TagKey.create(Registries.ITEM, Identifier.fromNamespaceAndPath("armorpieces", "knightly")),
            members.tag().get());
        assertTrue(members.named(), "the file named something");
        assertEquals(json, CODEC.encodeStart(JsonOps.INSTANCE, members).getOrThrow(),
            "a tag has to be written back as the same #id");
    }

    @Test
    void aMissingTagResolvesToNothingRatherThanThrowing() {
        final MemberSet<Item> members =
            CODEC.parse(JsonOps.INSTANCE, new JsonPrimitive("#somepack:never_installed")).getOrThrow();

        assertEquals(List.of(), members.resolve(NOTHING_INSTALLED),
            "an absent tag is an empty set - the entry drops out and the table still rolls");
        assertEquals("#somepack:never_installed", members.describe());
    }

    @Test
    void anEmptySetNamesNothing() {
        final MemberSet<Item> empty = MemberSet.empty();
        assertTrue(!empty.named(), "a field that was left out names nothing");
        assertEquals(List.of(), empty.resolve(NOTHING_INSTALLED));
    }

    @Test
    void idsWrittenOutAreTheMembers() {
        final Holder<Item> one = Holder.direct(null);
        final MemberSet<Item> direct = new MemberSet<>(Optional.empty(), HolderSet.direct(List.of(one)));

        assertTrue(direct.named());
        assertEquals(List.of(one), direct.resolve(NOTHING_INSTALLED),
            "ids bind when the file is read, so resolving asks the world nothing");
    }
}
