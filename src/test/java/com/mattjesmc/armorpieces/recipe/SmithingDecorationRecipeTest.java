package com.mattjesmc.armorpieces.recipe;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.decoration.fitting.builtin.MaterialFitting;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.registry.ModItems;
import net.minecraft.core.Holder;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * The first smithing step, asked as the table asks it: what {@code apply_crest} accepts, what it
 * refuses, and what it writes onto the armor.
 *
 * <p>The four ways a decoration craft can be wrong are all here, and every one of them was a
 * decision rather than an accident - see the javadoc on {@link SmithingDecorationRecipe}. A part must
 * declare the socket it is being put in; the socket must belong to the slot the armor is worn in; the
 * refusals live in {@code matches} so a player sees an empty result slot rather than a table that
 * takes the ingredients and makes nothing; and re-applying a part carries over whatever was set in
 * its fittings, which is the rule the no-op guard rests on.
 *
 * <p>{@code apply_crest} in particular because it is the recipe with the most content behind it -
 * four crest parts ship, fitted and unfitted - and because the twelve socket recipes are the same
 * file with a different anchor, so what holds for one holds for all. That the OTHER eleven exist and
 * decode is {@code ShippedRecipesTest}'s question.
 */
class SmithingDecorationRecipeTest {
    /**
     * The game, before anything else. A bare {@code Items.IRON_HELMET} in an argument is evaluated
     * BEFORE the call it is passed to, so a fixture method cannot bootstrap on its way past: the
     * first touch of {@link net.minecraft.core.registries.BuiltInRegistries} in a JVM that has not
     * been bootstrapped fails its class initialiser, and every later test in that JVM then fails
     * with a {@link NoClassDefFoundError} about a class that is not the problem.
     */
    @BeforeAll
    static void world() {
        Bench.data();
    }

    private static SmithingDecorationRecipe applyCrest() {
        return Bench.recipe("apply_crest", SmithingDecorationRecipe.class);
    }

    /** A part that fits the crest and has nothing set into it. */
    private static Holder<ArmorDecoration> crestPart() {
        return Bench.part(DecorationAnchor.CREST);
    }

    private static ItemStack template(final Holder<ArmorDecoration> part) {
        return ModItems.templateFor(DecorationAnchor.CREST, part);
    }

    /** An iron ingot, providing the iron trim material, as the addition slot takes it. */
    private static ItemStack iron() {
        return Bench.providing(Items.IRON_INGOT, "minecraft:iron");
    }

    // ---- what crafts ------------------------------------------------------------------------

    @Test
    void aTemplateAnArmorAndAMaterialPutThePartInItsSocket() {
        final Holder<ArmorDecoration> part = crestPart();
        final var input = Bench.input(template(part), Bench.stack(Items.IRON_HELMET), iron());

        assertTrue(applyCrest().matches(input, Bench.NO_LEVEL), "the three right stacks did not match");
        final ItemStack crafted = applyCrest().assemble(input);

        assertEquals(Items.IRON_HELMET, crafted.getItem(), "the craft changed the armor item");
        assertEquals(1, crafted.getCount(), "a smithing craft makes one");
        final DecorationEntry entry = Bench.entry(crafted, DecorationAnchor.CREST);
        assertSame(part, entry.decoration(), "the socket holds a different part than the template carried");
        assertSame(Bench.material("minecraft:iron"), entry.material(),
            "the part was not coloured by the material in the addition slot");
        assertEquals(1, Bench.decorations(crafted).entries().size(), "more than the crest was filled");
    }

    /**
     * The other sockets are left exactly as they were - the reason the component is a map keyed by
     * socket rather than a list.
     */
    @Test
    void aSecondPartLeavesTheFirstSocketAlone() {
        final Holder<ArmorDecoration> crest = crestPart();
        final Holder<ArmorDecoration> brow = Bench.part(DecorationAnchor.BROW);
        final ItemStack helmet = applyCrest().assemble(
            Bench.input(template(crest), Bench.stack(Items.IRON_HELMET), iron()));

        final ItemStack both = Bench.recipe("apply_brow", SmithingDecorationRecipe.class).assemble(
            Bench.input(ModItems.templateFor(DecorationAnchor.BROW, brow), helmet, iron()));

        assertSame(crest, Bench.entry(both, DecorationAnchor.CREST).decoration(), "the crest was lost");
        assertSame(brow, Bench.entry(both, DecorationAnchor.BROW).decoration(), "the brow was not set");
        assertEquals(1, Bench.decorations(helmet).entries().size(),
            "the stack that went in was modified; a component payload is immutable");
    }

    // ---- what is refused --------------------------------------------------------------------

    /**
     * The datapack guard rail: a pack may hand out a crest template carrying a part meant for the
     * heels, and it simply will not craft.
     */
    @Test
    void aPartIsRefusedInASocketItDoesNotDeclare() {
        final Holder<ArmorDecoration> belt = Bench.part(DecorationAnchor.BELT, "guard");
        assertFalse(belt.value().fits(DecorationAnchor.CREST), "the part picked for this test fits the crest");
        final var input = Bench.input(template(belt), Bench.stack(Items.IRON_HELMET), iron());

        assertFalse(applyCrest().matches(input, Bench.NO_LEVEL),
            "a part that does not declare the crest was accepted into it");
        assertTrue(applyCrest().assemble(input).isEmpty(), "and it produced something");
    }

    /** A template conjured by {@code /give} without the component: there is no part to apply. */
    @Test
    void aTemplateWithNoPartOnItMatchesNothing() {
        final ItemStack bare = Bench.stack(ModItems.template(DecorationAnchor.CREST));
        assertNull(bare.get(ModDataComponents.DECORATION), "the template item carries a part by default now");
        final var input = Bench.input(bare, Bench.stack(Items.IRON_HELMET), iron());

        assertFalse(applyCrest().matches(input, Bench.NO_LEVEL), "an empty template matched");
        assertTrue(applyCrest().assemble(input).isEmpty(), "an empty template produced something");
    }

    /**
     * The socket has to belong to the slot the base is worn in. Asked of the static rule rather than
     * the recipe, because the shipped files never offer the wrong pair - {@code apply_belt} names
     * {@code #minecraft:leg_armor} - and this is the check that keeps that true for a pack's file too.
     */
    @Test
    void theSocketMustBelongToTheSlotTheArmorEquips() {
        final Holder<ArmorDecoration> belt = Bench.part(DecorationAnchor.BELT, "guard");
        assertTrue(SmithingDecorationRecipe.applyDecoration(
            Bench.stack(Items.IRON_HELMET), iron(), belt, DecorationAnchor.BELT).isEmpty(),
            "a belt was put on a helmet");
        assertFalse(SmithingDecorationRecipe.applyDecoration(
            Bench.stack(Items.IRON_LEGGINGS), iron(), belt, DecorationAnchor.BELT).isEmpty(),
            "and the same part is refused on the leggings it belongs on");
    }

    /** A crest recipe does not reach boots: the base ingredient of the shipped file says so. */
    @Test
    void aCrestNeverReachesTheBoots() {
        assertFalse(applyCrest().matches(
            Bench.input(template(crestPart()), Bench.stack(Items.IRON_BOOTS), iron()), Bench.NO_LEVEL),
            "the crest recipe accepted boots");
    }

    /** No material in the addition slot, nothing to colour the part with. */
    @Test
    void anAdditionThatProvidesNoMaterialIsRefused() {
        assertTrue(SmithingDecorationRecipe.applyDecoration(
            Bench.stack(Items.IRON_HELMET), Bench.stack(Items.STICK), crestPart(), DecorationAnchor.CREST).isEmpty(),
            "a stick coloured a part");
    }

    // ---- the no-op guard, and what it protects ----------------------------------------------

    /**
     * Vanilla trimming refuses to re-apply an identical trim, and so does this - in {@code assemble},
     * where vanilla's own trim recipe keeps the same refusal, rather than in {@code matches}.
     *
     * <p>Worth stating, because the other three recipes of this mod fold their no-op check INTO
     * {@code matches} ({@code !assemble(input).isEmpty()}) and this one does not. It makes no
     * difference to a player: an empty result is what both tables show, since the advanced table
     * filters an empty result out of its preview and vanilla's has nothing to put in the slot. It
     * does make a difference to a caller that asks {@code matches} and then trusts it.
     */
    @Test
    void theSamePartInTheSameMaterialAgainProducesNothing() {
        final Holder<ArmorDecoration> part = crestPart();
        final ItemStack decorated = applyCrest().assemble(
            Bench.input(template(part), Bench.stack(Items.IRON_HELMET), iron()));

        final var again = Bench.input(template(part), decorated, iron());
        assertTrue(applyCrest().assemble(again).isEmpty(),
            "the ingredients would have been consumed for nothing");
        assertTrue(applyCrest().matches(again, Bench.NO_LEVEL),
            "the ingredient shape is still right, and this recipe says so; if that has changed,"
                + " it is this test's note that is out of date");
    }

    /**
     * Re-applying a part is how a player changes its metal, and what is set in its fittings survives
     * that - the trap being that a step which quietly ate the gem would still have looked like a
     * successful craft.
     */
    @Test
    void anotherMaterialKeepsWhatWasSetInTheFittings() {
        final Holder<ArmorDecoration> fitted = Bench.part(DecorationAnchor.CREST, "gemstone");
        final Holder<Fitting> gemstone = Bench.fitting("gemstone");
        final ItemStack decorated = applyCrest().assemble(
            Bench.input(template(fitted), Bench.stack(Items.IRON_HELMET), iron()));
        final ItemStack set = SmithingFittingRecipe.applyFitting(
            decorated, Bench.providing(Items.EMERALD, "minecraft:emerald"));
        assertEquals(new MaterialFitting.Value(Bench.material("minecraft:emerald")),
            Bench.entry(set, DecorationAnchor.CREST).fitting(gemstone),
            "the emerald was not set into the gemstone; the rest of this test would be vacuous");

        final ItemStack gold = applyCrest().assemble(Bench.input(
            template(fitted), set, Bench.providing(Items.GOLD_INGOT, "minecraft:gold")));

        final DecorationEntry entry = Bench.entry(gold, DecorationAnchor.CREST);
        assertSame(Bench.material("minecraft:gold"), entry.material(), "the metal did not change");
        assertEquals(new MaterialFitting.Value(Bench.material("minecraft:emerald")), entry.fitting(gemstone),
            "the emerald was eaten by the re-application");
    }

    /**
     * And with the fittings carried over, the no-op guard covers a fitted part too. Before they were,
     * an entry rebuilt empty always differed from the fitted one it replaced, so the craft went
     * through and the fittings were the price.
     */
    @Test
    void aFittedPartReAppliedIdenticallyIsStillRefused() {
        final Holder<ArmorDecoration> fitted = Bench.part(DecorationAnchor.CREST, "gemstone");
        final ItemStack set = SmithingFittingRecipe.applyFitting(
            applyCrest().assemble(Bench.input(template(fitted), Bench.stack(Items.IRON_HELMET), iron())),
            Bench.providing(Items.EMERALD, "minecraft:emerald"));

        assertTrue(applyCrest().assemble(Bench.input(template(fitted), set, iron())).isEmpty(),
            "the same fitted part in the same material was crafted again, and the emerald was the price");
    }
}
