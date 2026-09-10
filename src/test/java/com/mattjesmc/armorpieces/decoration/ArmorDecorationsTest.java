package com.mattjesmc.armorpieces.decoration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonElement;
import com.mattjesmc.armorpieces.data.ShippedData;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.decoration.fitting.builtin.MaterialFitting;
import com.mojang.serialization.Dynamic;
import com.mojang.serialization.JsonOps;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import net.minecraft.core.Holder;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtOps;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.contents.PlainTextContents;
import net.minecraft.network.chat.contents.TranslatableContents;
import net.minecraft.resources.Identifier;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.equipment.trim.TrimMaterial;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * The component every decorated piece of armor carries: the lines it draws, and the map underneath
 * them.
 *
 * <p>The tooltip is the one thing this mod says to a player in words, and until now the only check on
 * it was the gate's tier 3, which reads a real stack's tooltip out of a running client and compares it
 * with {@code description()}. That answers "does the line appear"; it cannot cheaply answer the
 * questions that are decisions - one heading and not one per socket, anchor order rather than map
 * order so the list reads down the body and does not reshuffle when a part is replaced, an effect line
 * only for a part that does something, a fitting line only for a fitting that holds something, and the
 * missing-parts block last, its count above the ids it is counting - on the face of the tooltip rather
 * than behind F3+H, because the id is what a player acts on.
 *
 * <p>Lines are asserted by their TRANSLATION KEYS rather than by their text: no language is loaded in
 * a test JVM, so {@code getString()} would flatten every line to its key and lose the arguments -
 * which fitting, which material - that half of these assertions are about.
 *
 * <p>The map half ({@code with}, {@code without}, {@code pruned}) is asserted here too, because the
 * one thing it is for is the promise that a player is never stuck with a hole: a socket holding a part
 * an uninstalled pack defines can always be written over, and only {@code /armorpieces prune} ever
 * destroys one.
 */
class ArmorDecorationsTest {
    /** A part this installation cannot name - what the raw half of the component holds. */
    private static final String MISSING = "somepack:antlers";

    /** The socket {@link #raw} puts its first hole in: the enum's first, whatever that is. */
    private static final DecorationAnchor HOLE = DecorationAnchor.values()[0];

    /**
     * The load, and its tags: a material fitting's own set of materials is a tag, and this test fills
     * a fitting with a material that fitting would really take.
     */
    @BeforeAll
    static void world() {
        ShippedData.bindTags(ShippedData.mod());
    }

    // ---- the tooltip ------------------------------------------------------------------------

    @Test
    void nothingIsSaidAboutAnEmptyComponent() {
        assertTrue(ArmorDecorations.EMPTY.isEmpty(), "the empty value is not empty");
        assertEquals(List.of(), lines(ArmorDecorations.EMPTY, TooltipFlag.NORMAL),
            "an undecorated piece was given a tooltip line");
    }

    /** One heading, then the sockets in the enum's own order whatever order they were filled in. */
    @Test
    void theListIsHeadedOnceAndReadsDownTheBody() {
        final Holder<ArmorDecoration> brow = plainPart(DecorationAnchor.BROW);
        final Holder<ArmorDecoration> spurs = plainPart(DecorationAnchor.SPURS);
        // Filled bottom-up: the tooltip must not be the order they went in.
        final ArmorDecorations worn = decorations(Map.of(
            DecorationAnchor.SPURS, entry(spurs), DecorationAnchor.BROW, entry(brow)));

        final List<List<String>> lines = lines(worn, TooltipFlag.NORMAL);

        assertEquals(3, lines.size(), () -> "a heading and two parts is three lines, not " + lines);
        assertEquals(List.of("item.armorpieces.decorated"), lines.getFirst(), "the heading is not first");
        assertEquals(key(brow), lines.get(1).getFirst(), "the brow is not above the spurs");
        assertEquals(key(spurs), lines.get(2).getFirst(), "the spurs are not below the brow");
    }

    /** What a part DOES is a line of its own, under it, and a part that does nothing adds none. */
    @Test
    void whatAPartDoesIsListedUnderIt() {
        final Holder<ArmorDecoration> doing = partWithEffects();
        final ArmorDecorations worn = decorations(Map.of(doing.value().primaryAnchor(), entry(doing)));

        final List<List<String>> lines = lines(worn, TooltipFlag.NORMAL);

        assertEquals(2 + doing.value().effects().size(), lines.size(),
            () -> "a heading, the part and one line per effect is what " + key(doing) + " should say: " + lines);
        for (int i = 0; i < doing.value().effects().size(); i++) {
            final Component described = doing.value().effects().get(i).description(iron());
            assertEquals(keys(described), lines.get(2 + i),
                "an effect's line is not the effect's own description");
        }
    }

    /** A circlet without its stone is still just a circlet: an empty fitting is not listed. */
    @Test
    void aFittingIsListedOnlyWhileItHoldsSomething() {
        final Holder<ArmorDecoration> fitted = partWithAFitting();
        final Holder<Fitting> fitting = fitted.value().fittings().getFirst();
        final DecorationAnchor anchor = fitted.value().primaryAnchor();

        final List<List<String>> bare = lines(
            decorations(Map.of(anchor, entry(fitted))), TooltipFlag.NORMAL);
        final MaterialFitting.Value gem = new MaterialFitting.Value(
            ((MaterialFitting) fitting.value()).materials().stream().findFirst()
                .orElseThrow(() -> new AssertionError(fitting.unwrapKey() + " takes no material at all")));
        final List<List<String>> set = lines(decorations(Map.of(anchor,
            entry(fitted).withFitting(fitting, gem))), TooltipFlag.NORMAL);

        assertEquals(set.size() - 1, bare.size(),
            () -> "filling a fitting should add exactly one line; empty said " + bare + " and full " + set);
        final List<String> line = set.getLast();
        assertEquals("item.armorpieces.fitting", line.getFirst(),
            () -> "the last line is not a fitting line: " + line);
        assertTrue(line.containsAll(keys(fitting.value().description())),
            () -> "the fitting line does not name the fitting: " + line);
    }

    /**
     * The count, and then the id - on the face of the tooltip, not behind F3+H.
     *
     * <p>{@code docs/plans/compatibility.md} §5.1: the count is the difference between a player
     * thinking the mod is broken and one knowing something is absent; the id is the difference
     * between knowing that and being able to act. A part is three JSON files and a PNG, so an id is a
     * complete instruction even to a player who cannot get the pack at all.
     */
    @Test
    void aMissingPartIsCountedAndThenNamed() {
        final ArmorDecorations worn = new ArmorDecorations(
            Map.of(DecorationAnchor.BROW, entry(plainPart(DecorationAnchor.BROW))), raw(MISSING));

        final List<List<String>> normal = lines(worn, TooltipFlag.NORMAL);
        assertEquals(List.of("item.armorpieces.missing_parts"), normal.get(normal.size() - 2),
            () -> "the missing-parts count should sit above the ids: " + normal);
        assertEquals(List.of(MISSING), normal.getLast(),
            () -> "the id is not on the face of the tooltip: " + normal);

        assertEquals(normal, lines(worn, TooltipFlag.ADVANCED),
            "with one missing part the advanced tooltip has nothing left to add");
    }

    /**
     * Twelve sockets can all be missing at once and twelve lines is a wall, so an ordinary tooltip
     * names four and counts the rest. The advanced flag is what the remainder is for.
     */
    @Test
    void aWallOfMissingPartsIsCappedButNotUnderTheAdvancedFlag() {
        final ArmorDecorations worn = new ArmorDecorations(Map.of(), raw(
            "somepack:a", "somepack:b", "somepack:c", "somepack:d", "somepack:e", "somepack:f"));

        final List<List<String>> normal = lines(worn, TooltipFlag.NORMAL);
        assertEquals(List.of("item.armorpieces.missing_more"), normal.getLast(),
            () -> "six missing parts should end in a count of what was not shown: " + normal);
        assertEquals(7, normal.size(),
            () -> "the title, the count, four ids and the remainder: " + normal);

        final List<List<String>> advanced = lines(worn, TooltipFlag.ADVANCED);
        assertEquals(8, advanced.size(), () -> "an advanced tooltip names all six: " + advanced);
        assertEquals(List.of("somepack:f"), advanced.getLast());
    }

    // ---- the map ----------------------------------------------------------------------------

    @Test
    void unresolvedSocketsAreCountedAndNamedInOrder() {
        final ArmorDecorations worn = new ArmorDecorations(Map.of(), raw("somepack:wings", MISSING));

        assertFalse(worn.isEmpty(), "a piece holding nothing but holes reads as undecorated");
        assertEquals(2, worn.unresolvedCount(), "the holes were not counted");
        assertEquals(List.of(MISSING, "somepack:wings"), worn.unresolvedNames(),
            "the names are not sorted, so /armorpieces missing would reshuffle between calls");
    }

    /**
     * A player is never stuck with a hole: a new part applied to that very socket writes over it,
     * which is what makes "wait for the pack, or just apply a new part" a real choice.
     */
    @Test
    void aNewPartReplacesAHole() {
        final Holder<ArmorDecoration> part = plainPart(HOLE);
        final ArmorDecorations hole = new ArmorDecorations(Map.of(), raw(MISSING));
        assertEquals(1, hole.unresolvedCount(), "the fixture holds no hole");

        final ArmorDecorations filled = hole.with(HOLE, entry(part));

        assertSame(part, filled.get(HOLE).decoration(), "the part was not applied");
        assertEquals(0, filled.unresolvedCount(),
            () -> "the hole outlived the part put over it: " + filled.unresolvedNames());
        assertEquals(1, hole.unresolvedCount(), "the value that went in was modified");
    }

    @Test
    void withoutSaysWhenThereWasNothingToTakeOut() {
        final ArmorDecorations worn = decorations(
            Map.of(DecorationAnchor.BROW, entry(plainPart(DecorationAnchor.BROW))));

        assertEquals(Optional.empty(), worn.without(DecorationAnchor.CREST),
            "emptying a socket that was already empty reported a change");
        final Optional<ArmorDecorations> emptied = worn.without(DecorationAnchor.BROW);
        assertTrue(emptied.isPresent(), "the filled socket could not be emptied");
        assertTrue(emptied.get().isEmpty(), "something was left behind");

        // And the raw half is reachable the same way: a hole is keyed by its socket's serialized name.
        final ArmorDecorations hole = new ArmorDecorations(Map.of(), raw(MISSING));
        assertEquals(Optional.empty(), hole.without(other(HOLE)),
            "a hole was emptied out of a socket it is not in");
        assertTrue(hole.without(HOLE).orElseThrow().isEmpty(),
            "a hole could not be emptied out of its own socket");
    }

    /** Pruning is the only thing in the mod that destroys a hole, and it destroys nothing else. */
    @Test
    void pruningDropsTheHolesAndKeepsThePieces() {
        final Holder<ArmorDecoration> part = plainPart(DecorationAnchor.BROW);
        final ArmorDecorations worn = new ArmorDecorations(
            Map.of(DecorationAnchor.BROW, entry(part)), raw(MISSING));

        final ArmorDecorations pruned = worn.pruned();

        assertEquals(0, pruned.unresolvedCount(), "the hole survived a prune");
        assertSame(part, pruned.get(DecorationAnchor.BROW).decoration(), "the prune took a real part with it");
        final ArmorDecorations clean = pruned.pruned();
        assertSame(pruned, clean, "pruning a piece with nothing to prune copied it anyway");
    }

    /**
     * The saved form is written in anchor order, not map order, so replacing a part does not reshuffle
     * an item's NBT - the same reason the tooltip reads down the body.
     */
    @Test
    void theSavedFormIsInAnchorOrder() {
        final ArmorDecorations worn = decorations(Map.of(
            DecorationAnchor.SPURS, entry(plainPart(DecorationAnchor.SPURS)),
            DecorationAnchor.BROW, entry(plainPart(DecorationAnchor.BROW))));

        final JsonElement written = ArmorDecorations.CODEC
            .encodeStart(ShippedData.mod().full().createSerializationContext(JsonOps.INSTANCE), worn)
            .getOrThrow(message -> new AssertionError("the component could not be written: " + message));

        assertEquals(List.of("brow", "spurs"),
            List.copyOf(written.getAsJsonObject().keySet()),
            "the sockets were not written in the order DecorationAnchor declares them");
    }

    // ---- the fixture ------------------------------------------------------------------------

    /** Decorations with nothing missing, as everything inside the mod builds them. */
    private static ArmorDecorations decorations(final Map<DecorationAnchor, DecorationEntry> entries) {
        return new ArmorDecorations(entries);
    }

    private static DecorationEntry entry(final Holder<ArmorDecoration> part) {
        return new DecorationEntry(iron(), part);
    }

    /** One raw socket per name, keyed by socket, as a component read from a save holds them. */
    private static Map<String, Dynamic<?>> raw(final String... parts) {
        final Map<String, Dynamic<?>> holes = new LinkedHashMap<>();
        final List<DecorationAnchor> anchors = List.of(DecorationAnchor.values());
        for (int i = 0; i < parts.length; i++) {
            final CompoundTag tag = new CompoundTag();
            tag.putString("decoration", parts[i]);
            holes.put(anchors.get(i).getSerializedName(), new Dynamic<>(NbtOps.INSTANCE, tag));
        }
        return holes;
    }

    /** Any socket but this one. */
    private static DecorationAnchor other(final DecorationAnchor anchor) {
        return java.util.Arrays.stream(DecorationAnchor.values())
            .filter(candidate -> candidate != anchor)
            .findFirst()
            .orElseThrow();
    }

    private static Holder<TrimMaterial> iron() {
        return ShippedData.mod().registry(net.minecraft.core.registries.Registries.TRIM_MATERIAL)
            .get(Identifier.withDefaultNamespace("iron"))
            .<Holder<TrimMaterial>>map(holder -> holder)
            .orElseThrow(() -> new AssertionError("vanilla's iron trim material was not loaded"));
    }

    /** A part with no effects and no fittings: one tooltip line, and nothing under it. */
    private static Holder<ArmorDecoration> plainPart(final DecorationAnchor anchor) {
        return parts()
            .filter(part -> part.value().fits(anchor))
            .filter(part -> part.value().effects().isEmpty() && !part.value().hasFittings())
            .findFirst()
            .orElseThrow(() -> new AssertionError(
                "no shipped part sits in " + anchor.getSerializedName() + " and does nothing"));
    }

    private static Holder<ArmorDecoration> partWithEffects() {
        return parts()
            .filter(part -> !part.value().effects().isEmpty() && !part.value().hasFittings())
            .findFirst()
            .orElseThrow(() -> new AssertionError("no shipped part has an effect and no fittings"));
    }

    private static Holder<ArmorDecoration> partWithAFitting() {
        return parts()
            .filter(part -> part.value().effects().isEmpty() && part.value().fittings().size() == 1)
            .filter(part -> part.value().fittings().getFirst().value() instanceof MaterialFitting)
            .findFirst()
            .orElseThrow(() -> new AssertionError("no shipped part has one material fitting and no effects"));
    }

    /** Every part the mod ships, in id order, so a test always picks the same one. */
    private static java.util.stream.Stream<Holder<ArmorDecoration>> parts() {
        return ShippedData.mod().registry(ArmorPiecesRegistries.ARMOR_DECORATION).listElements()
            .sorted(java.util.Comparator.comparing(part -> part.key().identifier().toString()))
            .<Holder<ArmorDecoration>>map(part -> part);
    }

    private static String key(final Holder<ArmorDecoration> part) {
        return keys(part.value().description()).getFirst();
    }

    // ---- reading a tooltip ------------------------------------------------------------------

    /** The lines this component would draw, each as the translation keys and literals in it. */
    private static List<List<String>> lines(final ArmorDecorations worn, final TooltipFlag flag) {
        final List<List<String>> lines = new ArrayList<>();
        worn.addToTooltip(
            Item.TooltipContext.of(ShippedData.mod().full()),
            line -> lines.add(keys(line)),
            flag,
            ItemStack.EMPTY);
        return lines;
    }

    /**
     * The translation keys and literal text in one line, in order, with the indentation dropped.
     *
     * <p>Keys rather than text because no language is loaded here: a translatable with arguments
     * flattens to its own key and the arguments are lost, and the arguments are what say which
     * fitting holds which material.
     */
    private static List<String> keys(final Component line) {
        final List<String> found = new ArrayList<>();
        collect(line, found);
        return found.stream().filter(text -> !text.isBlank()).toList();
    }

    private static void collect(final Component component, final List<String> into) {
        if (component.getContents() instanceof TranslatableContents translatable) {
            into.add(translatable.getKey());
            for (final Object argument : translatable.getArgs()) {
                if (argument instanceof Component nested) {
                    collect(nested, into);
                }
            }
        } else if (component.getContents() instanceof PlainTextContents text) {
            into.add(text.text());
        }
        component.getSiblings().forEach(sibling -> collect(sibling, into));
    }
}
