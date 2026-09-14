package com.mattjesmc.armorpieces.config;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonParser;
import com.mattjesmc.armorpieces.GameBootstrap;
import com.mattjesmc.armorpieces.data.ShippedData;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mojang.serialization.JsonOps;
import java.util.List;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderSet;
import net.minecraft.core.Registry;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.TagKey;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * The switch's one question, {@link PartsSwitch#offers}, asked over the content this repository
 * ships: by id, by tag, by namespace, and across the four registries one {@code disabled} list
 * serves.
 */
class PartsSwitchTest {
    private static ShippedData.Loaded loaded;

    @BeforeAll
    static void world() {
        GameBootstrap.content();
        loaded = ShippedData.mod();
        ShippedData.bindTags(loaded);
    }

    private static PartsSwitch parsed(final String json) {
        return PartsSwitch.CODEC.parse(JsonOps.INSTANCE, JsonParser.parseString(json))
            .getOrThrow(message -> new AssertionError(message + "\n" + json));
    }

    private static Holder<ArmorDecoration> part(final String path) {
        return element(ArmorPiecesRegistries.ARMOR_DECORATION, path);
    }

    private static <T> Holder<T> element(final ResourceKey<? extends Registry<T>> key, final String path) {
        return loaded.registry(key).get(ShippedData.shipped(key, path))
            .<Holder<T>>map(holder -> holder)
            .orElseThrow(() -> new AssertionError("this jar no longer ships " + path));
    }

    /** A member of a shipped part tag, so the tag tests are about a tag that really has members. */
    private static Holder<ArmorDecoration> firstIn(final String tag) {
        // The theme tags moved with their themes: #armorpieces:knightly is #armorpieces_knightly:knightly.
        final TagKey<ArmorDecoration> key = TagKey.create(ArmorPiecesRegistries.ARMOR_DECORATION,
            Identifier.fromNamespaceAndPath("armorpieces_" + tag, tag));
        final HolderSet.Named<ArmorDecoration> set = loaded.registry(ArmorPiecesRegistries.ARMOR_DECORATION)
            .get(key).orElseThrow(() -> new AssertionError("no shipped tag #armorpieces:" + tag));
        assertTrue(set.size() > 0, "#armorpieces:" + tag + " is empty");
        return set.get(0);
    }

    @Test
    void theDefaultOffersEverythingAndSaysSo() {
        assertFalse(PartsSwitch.DEFAULT.restricts());
        assertTrue(PartsSwitch.DEFAULT.offers(part("circlet"), loaded.full()));
        assertEquals(PartsSwitch.DEFAULT, parsed("{}"), "an empty section is the default");
    }

    @Test
    void anIdIsWrittenBareAndATagWithAHash() {
        final PartsSwitch written = parsed("""
            { "disabled": ["armorpieces_court:circlet", "#armorpieces_knightly:knightly"] }
            """);
        assertEquals(List.of(
            new PartsSwitch.Member(Identifier.fromNamespaceAndPath("armorpieces_court", "circlet"), false),
            new PartsSwitch.Member(Identifier.fromNamespaceAndPath("armorpieces_knightly", "knightly"), true)),
            written.disabled());
        assertEquals("[\"armorpieces_court:circlet\",\"#armorpieces_knightly:knightly\"]",
            PartsSwitch.Member.CODEC.listOf().encodeStart(JsonOps.INSTANCE, written.disabled())
                .getOrThrow().toString(),
            "a line has to come back as it was typed");
    }

    @Test
    void anIdSwitchesOffThatOneAndNothingElse() {
        final PartsSwitch switched = parsed("""
            { "disabled": ["armorpieces_court:circlet"] }
            """);
        assertTrue(switched.restricts());
        assertFalse(switched.offers(part("circlet"), loaded.full()));
        assertTrue(switched.offers(part("visor"), loaded.full()));
    }

    @Test
    void aTagSwitchesOffItsMembersAsTheyAreNow() {
        final Holder<ArmorDecoration> knight = firstIn("knightly");
        final PartsSwitch switched = parsed("""
            { "disabled": ["#armorpieces_knightly:knightly"] }
            """);
        assertFalse(switched.offers(knight, loaded.full()), knight + " is knightly and was offered");
        final Holder<ArmorDecoration> other = loaded.registry(ArmorPiecesRegistries.ARMOR_DECORATION)
            .listElements()
            .filter(candidate -> !candidate.is(TagKey.create(ArmorPiecesRegistries.ARMOR_DECORATION,
                Identifier.fromNamespaceAndPath("armorpieces_knightly", "knightly"))))
            .findFirst().orElseThrow();
        assertTrue(switched.offers(other, loaded.full()), other + " is not knightly and was refused");
    }

    /**
     * One list serves the four registries, and a tag is looked up in the MEMBER's registry: a
     * fitting tag switches off fittings, and a part that happens to share the tag's name with
     * nothing in its own registry is untouched.
     */
    @Test
    void aTagIsLookedUpInTheMembersOwnRegistry() {
        final Holder<Fitting> fitting = element(ArmorPiecesRegistries.FITTING, "gemstone");
        final TagKey<Fitting> common = TagKey.create(ArmorPiecesRegistries.FITTING,
            Identifier.fromNamespaceAndPath("armorpieces", "common"));
        assertTrue(fitting.is(common), "the fitting picked for this test is not in #armorpieces:common");

        final PartsSwitch switched = parsed("""
            { "disabled": ["#armorpieces:common"] }
            """);
        assertFalse(switched.offers(fitting, loaded.full()), "a fitting in the tag was offered");
        assertTrue(switched.offers(part("circlet"), loaded.full()),
            "a part was refused for a tag that exists only among the fittings");
    }

    @Test
    void modPartsOffIsTheWholeNamespaceAndNothingOutsideIt() {
        final PartsSwitch switched = parsed("""
            { "mod_parts": false }
            """);
        assertTrue(switched.restricts());
        assertFalse(switched.offers(part("circlet"), loaded.full()));
        assertFalse(switched.offers(element(ArmorPiecesRegistries.FITTING, "gemstone"), loaded.full()),
            "the mod's own fittings are the mod's own");
        final Holder<ArmorDecoration> inline = Holder.direct(part("circlet").value());
        assertTrue(switched.offers(inline, loaded.full()),
            "a holder with no key names nothing a file could switch off");
    }

    @Test
    void aLineThatIsNotAnIdIsRefusedAsTheFileIsRead() {
        final var result = PartsSwitch.CODEC.parse(JsonOps.INSTANCE,
            JsonParser.parseString("{ \"disabled\": [\"Not An Id\"] }"));
        assertTrue(result.isError(), "a line that cannot name anything has to be an error, not a silent nothing");
    }
}
