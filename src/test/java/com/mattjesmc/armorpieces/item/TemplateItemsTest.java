package com.mattjesmc.armorpieces.item;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.mattjesmc.armorpieces.GameBootstrap;
import com.mattjesmc.armorpieces.cloth.Cloth;
import com.mattjesmc.armorpieces.data.ShippedData;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.identity.Tolerant;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.registry.ModItems;
import com.mattjesmc.armorpieces.skin.ArmorSkin;
import com.mojang.serialization.Dynamic;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.nbt.NbtOps;
import net.minecraft.nbt.StringTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.contents.PlainTextContents;
import net.minecraft.network.chat.contents.TranslatableContents;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * The four smithing templates: what they are called, and what they promise before a player has spent
 * anything.
 *
 * <p>These are the items the whole mod is reached through - the thing found in a chest, the thing
 * laid in the first slot - and all four are the same trick: one item, with the part, fitting, skin or
 * cloth carried as a COMPONENT, so that a datapack adding content adds a template variant with no
 * item registration and no model. Which puts two player-facing strings on every one of them, both
 * built rather than looked up: the name, which composes the content's own description with the
 * item's, and a five-line tooltip in vanilla's smithing-template shape - what it goes on, and what
 * goes in.
 *
 * <p>Neither had a test. Tier 3 photographs the item models, and tier 2 never opens an inventory; the
 * name of a template holding a datapack's part, and the line that says which socket a template is
 * for, had only ever been read by a person looking at a screen.
 *
 * <p>Lines are asserted by TRANSLATION KEY, as everywhere else in this suite: no language is loaded,
 * so {@code getString()} would flatten a line to its key and lose the arguments - and here the
 * arguments are the whole point, since they are what the part contributes to its own template's name.
 *
 * <p>The last test is the one that matters most and looks least like a test: a template naming a part
 * this installation does not have keeps its name, its tooltip and its existence. That is
 * {@link Tolerant}'s rule seen from the item a player is holding.
 */
class TemplateItemsTest {
    @BeforeAll
    static void world() {
        GameBootstrap.content();
        // Bakes the default components, without which no ItemStack can be built at all.
        ShippedData.bakeItemComponents(ShippedData.mod());
    }

    // ---- one template per socket -------------------------------------------------------------

    /**
     * Every socket has its own template item and no two share one.
     *
     * <p>The coverage rule of the item half: a socket added to {@link DecorationAnchor} without an
     * item is a part that can be loaded, drawn and worn, and never obtained.
     */
    @Test
    void everySocketHasATemplateOfItsOwn() {
        final Set<Item> seen = new HashSet<>();
        for (final DecorationAnchor anchor : DecorationAnchor.values()) {
            final DecorationTemplateItem template = ModItems.template(anchor);
            assertNotNull(template, () -> "no template item exists for the " + anchor.getSerializedName() + " socket");
            assertEquals(anchor, template.anchor(),
                () -> "the " + anchor.getSerializedName() + " template is for another socket");
            assertTrue(seen.add(template),
                () -> "two sockets share one template item at " + anchor.getSerializedName());
        }
    }

    @Test
    void theFactoryBuildsTheSocketsOwnTemplateCarryingThePart() {
        final Holder<ArmorDecoration> part = shipped(ArmorPiecesRegistries.ARMOR_DECORATION);
        final ItemStack template = ModItems.templateFor(DecorationAnchor.CREST, part);

        assertSame(ModItems.template(DecorationAnchor.CREST), template.getItem(),
            "a crest template was built out of some other item");
        assertSame(part, Tolerant.get(template, ModDataComponents.DECORATION),
            "the part was not put on the stack");
    }

    // ---- what a template is called -----------------------------------------------------------

    @Test
    void aBareTemplateIsCalledWhatTheItemIsCalled() {
        final ItemStack bare = new ItemStack(ModItems.template(DecorationAnchor.CREST));

        assertEquals(List.of(bare.getItem().getDescriptionId()), keys(bare.getItem().getName(bare)),
            "a template carrying nothing invented a name");
    }

    @Test
    void aTemplateIsNamedAfterWhatItCarries() {
        final Holder<ArmorDecoration> part = shipped(ArmorPiecesRegistries.ARMOR_DECORATION);
        final ItemStack template = ModItems.templateFor(DecorationAnchor.CREST, part);

        assertEquals(
            List.of("item.armorpieces.decoration_template",
                key(part.value().description()),
                template.getItem().getDescriptionId()),
            keys(template.getItem().getName(template)),
            "a template holding a part is not named after it");
    }

    @Test
    void theOtherThreeTemplatesAreNamedTheSameWay() {
        final Holder<Fitting> fitting = shipped(ArmorPiecesRegistries.FITTING);
        final Holder<ArmorSkin> skin = shipped(ArmorPiecesRegistries.ARMOR_SKIN);
        final Holder<Cloth> cloth = shipped(ArmorPiecesRegistries.CLOTH);

        assertEquals(key(fitting.value().description()), carried(ModItems.fittingTemplateFor(fitting)),
            "the fitting template is not named after its fitting");
        assertEquals(key(skin.value().description()), carried(ModItems.skinTemplateFor(skin)),
            "the skin template is not named after its skin");
        assertEquals(key(cloth.value().description()), carried(ModItems.clothTemplateFor(cloth)),
            "the cloth template is not named after its cloth");
    }

    // ---- what a template promises ------------------------------------------------------------

    /**
     * The socket template's tooltip: a blank line, then vanilla's two headings, each with one blue
     * line under it - and the socket's own line is what tells a player a crest goes on a helmet.
     */
    @Test
    void aSocketTemplateSaysWhereItGoesAndWhatColoursIt() {
        final ItemStack template = ModItems.templateFor(
            DecorationAnchor.CREST, shipped(ArmorPiecesRegistries.ARMOR_DECORATION));

        assertEquals(
            List.of(
                List.of(),
                List.of("item.armorpieces.template.applies_to"),
                List.of("anchor.armorpieces.crest.applies_to"),
                List.of("item.armorpieces.template.ingredients"),
                List.of("item.armorpieces.template.trim_materials")),
            hoverLines(template),
            "the crest template no longer says where it goes and what colours it");
    }

    /** Every socket's template quotes its OWN socket, which is the line that differs between them. */
    @Test
    void everySocketTemplateQuotesItsOwnSocket() {
        for (final DecorationAnchor anchor : DecorationAnchor.values()) {
            final ItemStack template = new ItemStack(ModItems.template(anchor));
            assertEquals(List.of("anchor.armorpieces." + anchor.getSerializedName() + ".applies_to"),
                hoverLines(template).get(2),
                () -> "the " + anchor.getSerializedName() + " template quotes another socket");
        }
    }

    /**
     * The fitting template is the one of the four that changes what it promises: bare, it takes
     * anything any fitting takes; named, it says its own fitting and that fitting's own ingredients.
     */
    @Test
    void aFittingTemplateNarrowsItsPromiseWhenItNamesAFitting() {
        final Holder<Fitting> fitting = shipped(ArmorPiecesRegistries.FITTING);
        final ItemStack bare = new ItemStack(ModItems.fittingTemplate());
        final ItemStack named = ModItems.fittingTemplateFor(fitting);

        assertEquals(List.of("item.armorpieces.fitting_template.applies_to"), hoverLines(bare).get(2),
            "the bare fitting template stopped offering itself to every fitting");
        assertEquals(List.of("item.armorpieces.fitting_template.ingredients"), hoverLines(bare).get(4),
            "the bare fitting template stopped naming every kind of ingredient");

        assertEquals(
            List.of("item.armorpieces.fitting_template.applies_to.named", key(fitting.value().description())),
            hoverLines(named).get(2),
            "a named fitting template does not say which fitting it is for");
        assertEquals(keys(fitting.value().ingredients()), hoverLines(named).get(4),
            "a named fitting template does not say what its own fitting takes");
    }

    @Test
    void theSkinAndClothTemplatesSayWhatTheyGoOn() {
        assertEquals(
            List.of("item.armorpieces.skin_template.applies_to"),
            hoverLines(new ItemStack(ModItems.skinTemplate())).get(2),
            "the skin template stopped saying what it goes on");
        assertEquals(
            List.of("item.armorpieces.cloth_template.applies_to"),
            hoverLines(new ItemStack(ModItems.clothTemplate())).get(2),
            "the cloth template stopped saying what it goes on");
    }

    // ---- a template for a part nobody has ----------------------------------------------------

    /**
     * A template naming a part this installation cannot resolve is still an item: it keeps the item's
     * own name, it still draws its tooltip, and the component says in one grey line what is missing -
     * naming the id, so the player can fetch the pack or write the piece. The alternative - which is
     * what a strict component would do - is that the stack fails to decode and the player loses the
     * template.
     */
    @Test
    void aTemplateForAPartNobodyHasIsStillATemplate() {
        final ItemStack template = new ItemStack(ModItems.template(DecorationAnchor.CREST));
        template.set(ModDataComponents.DECORATION, Tolerant.unresolved(
            new Dynamic<>(NbtOps.INSTANCE, StringTag.valueOf("somepack:antlers"))));

        assertNull(Tolerant.get(template, ModDataComponents.DECORATION),
            "an unresolved part read as a part");
        assertEquals(List.of(template.getItem().getDescriptionId()), keys(template.getItem().getName(template)),
            "a template whose part is missing lost the item's own name");
        assertEquals(List.of("item.armorpieces.template.applies_to"), hoverLines(template).get(1),
            "a template whose part is missing stopped saying where it goes");

        final List<List<String>> said = new ArrayList<>();
        template.get(ModDataComponents.DECORATION)
            .addToTooltip(Item.TooltipContext.of(ShippedData.mod().full()), line -> said.add(keys(line)),
                TooltipFlag.NORMAL, template);
        assertEquals(List.of(List.of("item.armorpieces.not_installed_named", "somepack:antlers")), said,
            "the line should say a pack is missing AND which id it is waiting for");
    }

    // ---- helpers -----------------------------------------------------------------------------

    /** The first element of a registry in id order, so a test always picks the same one. */
    private static <T> Holder<T> shipped(final ResourceKey<? extends Registry<T>> key) {
        final Registry<T> registry = ShippedData.mod().registry(key);
        return registry.listElements()
            .sorted(Comparator.comparing(element -> element.key().identifier().toString()))
            .<Holder<T>>map(element -> element)
            .findFirst()
            .orElseThrow(() -> new AssertionError("this repository ships nothing in " + key.identifier()));
    }

    /** The description key a template composed into its name, from the middle of the composed line. */
    private static String carried(final ItemStack template) {
        final List<String> parts = keys(template.getItem().getName(template));
        assertEquals(3, parts.size(), () -> "the name is not a composed one: " + parts);
        assertEquals("item.armorpieces.decoration_template", parts.getFirst(),
            "a template's name is no longer built from the shared key");
        return parts.get(1);
    }

    /** The lines this stack's item adds to a tooltip, each as the keys and literals in it. */
    private static List<List<String>> hoverLines(final ItemStack stack) {
        final List<List<String>> lines = new ArrayList<>();
        stack.getItem().appendHoverText(
            stack,
            Item.TooltipContext.of(ShippedData.mod().full()),
            TooltipDisplay.DEFAULT,
            line -> lines.add(keys(line)),
            TooltipFlag.NORMAL);
        return lines;
    }

    private static String key(final Component component) {
        return keys(component).getFirst();
    }

    /** The translation keys and literal text in one line, in order, with the indentation dropped. */
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
