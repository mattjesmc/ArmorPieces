package com.mattjesmc.armorpieces.recipe;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.decoration.fitting.builtin.DyeFitting;
import com.mattjesmc.armorpieces.decoration.fitting.builtin.MaterialFitting;
import com.mattjesmc.armorpieces.registry.ModItems;
import net.minecraft.core.Holder;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * The second smithing step: setting a material into the parts a piece already wears, and taking it
 * out again.
 *
 * <p>Nothing about a fitting is named in {@code apply_fitting} - one file covers every fitting there
 * will ever be - so all of the behaviour is routing, and routing is what this asks about. The rules,
 * in the order the recipe applies them: every part on the piece is offered the item, in the part's own
 * fitting order, and the first fitting that accepts it gets it; a template that names a fitting
 * narrows the offer to that one; an item nothing takes is no recipe at all; and an empty third slot
 * means the opposite operation, because the item is what names a fitting and its absence names them
 * all.
 *
 * <p>The parts are found by shape rather than named - a collar part whose guard is offered an item
 * before its inlay - because the order is the thing under test and a part id is the thing that moves.
 */
class SmithingFittingRecipeTest {
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

    private static SmithingFittingRecipe applyFitting() {
        return Bench.recipe("apply_fitting", SmithingFittingRecipe.class);
    }

    private static SmithingFittingRecipe clearFitting() {
        return Bench.recipe("clear_fitting", SmithingFittingRecipe.class);
    }

    private static Holder<Fitting> guard() {
        return Bench.fitting("guard");
    }

    private static Holder<Fitting> inlay() {
        return Bench.fitting("inlay");
    }

    private static Holder<Fitting> gemstone() {
        return Bench.fitting("gemstone");
    }

    /** An iron ingot: a guard metal, and no gemstone. */
    private static ItemStack ingot() {
        return Bench.providing(Items.IRON_INGOT, "minecraft:iron");
    }

    /** An emerald: a gemstone, and no guard metal. */
    private static ItemStack gem() {
        return Bench.providing(Items.EMERALD, "minecraft:emerald");
    }

    /** A chestplate wearing one part on {@code anchor}, decorated the way the table decorates. */
    private static ItemStack wearing(final DecorationAnchor anchor, final String... fittings) {
        return wearing(Bench.stack(Items.IRON_CHESTPLATE), anchor, fittings);
    }

    private static ItemStack wearing(
        final ItemStack chestplate, final DecorationAnchor anchor, final String... fittings
    ) {
        final Holder<ArmorDecoration> part = Bench.part(anchor, fittings);
        final ItemStack decorated = Bench
            .recipe("apply_" + anchor.getSerializedName(), SmithingDecorationRecipe.class)
            .assemble(Bench.input(ModItems.templateFor(anchor, part), chestplate, ingot()));
        assertFalse(decorated.isEmpty(), () -> "could not decorate a chestplate with " + part.unwrapKey());
        return decorated;
    }

    /** The bare fitting template - no fitting named, so everything is offered the item. */
    private static ItemStack bareTemplate() {
        return Bench.stack(ModItems.fittingTemplate());
    }

    // ---- the routing ------------------------------------------------------------------------

    /**
     * The item decides. A bandolier-shaped part takes a metal in its guard and a dye in its inlay,
     * from the same template and the same slot, and neither ever lands in the other.
     */
    @Test
    void theItemDecidesWhichFittingTakesIt() {
        final ItemStack collared = wearing(DecorationAnchor.COLLAR, "guard", "inlay");

        final ItemStack metal = applyFitting().assemble(Bench.input(bareTemplate(), collared, ingot()));
        assertEquals(new MaterialFitting.Value(Bench.material("minecraft:iron")),
            Bench.entry(metal, DecorationAnchor.COLLAR).fitting(guard()), "the ingot did not land in the guard");
        assertNull(Bench.entry(metal, DecorationAnchor.COLLAR).fitting(inlay()),
            "the ingot also went into the inlay");

        final ItemStack dyed = applyFitting().assemble(
            Bench.input(bareTemplate(), collared, Bench.stack(Items.DYE.pick(DyeColor.RED))));
        assertEquals(new DyeFitting.Value(DyeColor.RED),
            Bench.entry(dyed, DecorationAnchor.COLLAR).fitting(inlay()), "the dye did not land in the inlay");
        assertNull(Bench.entry(dyed, DecorationAnchor.COLLAR).fitting(guard()),
            "the dye also went into the guard");
    }

    /** One gem, and every part on the piece that has a place for it gets it - one smithing step. */
    @Test
    void oneGemReachesEveryPartThatTakesOne() {
        final ItemStack twice = wearing(
            wearing(DecorationAnchor.COLLAR, "gemstone"), DecorationAnchor.VAMBRACES, "gemstone");

        final ItemStack set = applyFitting().assemble(Bench.input(bareTemplate(), twice, gem()));

        final MaterialFitting.Value emerald = new MaterialFitting.Value(Bench.material("minecraft:emerald"));
        assertEquals(emerald, Bench.entry(set, DecorationAnchor.COLLAR).fitting(gemstone()),
            "the collar's stone is empty");
        assertEquals(emerald, Bench.entry(set, DecorationAnchor.VAMBRACES).fitting(gemstone()),
            "the vambraces' stone is empty");
    }

    /**
     * The advanced table's narrowing, which is the one caller that has a socket to name: the rule is
     * the same, run over one socket.
     */
    @Test
    void oneSocketAtATimeIsTheAdvancedTablesNarrowing() {
        final ItemStack twice = wearing(
            wearing(DecorationAnchor.COLLAR, "gemstone"), DecorationAnchor.VAMBRACES, "gemstone");

        final ItemStack set = SmithingFittingRecipe.applyFitting(twice, gem(), null, DecorationAnchor.COLLAR);

        assertNotNull(Bench.entry(set, DecorationAnchor.COLLAR).fitting(gemstone()), "the named socket is empty");
        assertNull(Bench.entry(set, DecorationAnchor.VAMBRACES).fitting(gemstone()),
            "a socket the caller did not name was fitted too");
    }

    /** A named template offers the item to its own fitting and to no other. */
    @Test
    void aNamedTemplateOffersItsOwnFittingAlone() {
        final ItemStack collared = wearing(DecorationAnchor.COLLAR, "guard", "inlay");

        assertTrue(applyFitting().assemble(
            Bench.input(ModItems.fittingTemplateFor(inlay()), collared, ingot())).isEmpty(),
            "an inlay template put an ingot somewhere");

        final ItemStack metal = applyFitting().assemble(
            Bench.input(ModItems.fittingTemplateFor(guard()), collared, ingot()));
        assertNotNull(Bench.entry(metal, DecorationAnchor.COLLAR).fitting(guard()),
            "a guard template did not fill the guard");
    }

    // ---- what is refused --------------------------------------------------------------------

    /** An item that fits nothing on the piece is not a recipe: the result slot stays empty. */
    @Test
    void anItemNoFittingOnThePieceTakesIsRefused() {
        final var input = Bench.input(bareTemplate(), wearing(DecorationAnchor.COLLAR, "guard", "inlay"), gem());

        assertFalse(applyFitting().matches(input, Bench.NO_LEVEL),
            "a gem was accepted by a part with only a guard and an inlay");
        assertTrue(applyFitting().assemble(input).isEmpty(), "and something came out of it");
    }

    /** Nothing to fit: an undecorated piece has no fittings at all, whatever is laid beside it. */
    @Test
    void anUndecoratedPieceHasNothingToFit() {
        assertFalse(applyFitting().matches(
            Bench.input(bareTemplate(), Bench.stack(Items.IRON_CHESTPLATE), ingot()), Bench.NO_LEVEL),
            "a plain chestplate matched the fitting recipe");
    }

    /** The same metal into the same guard again would consume the template for nothing. */
    @Test
    void theSameItemInTheSameFittingAgainIsRefused() {
        final ItemStack set = applyFitting().assemble(
            Bench.input(bareTemplate(), wearing(DecorationAnchor.COLLAR, "guard", "inlay"), ingot()));

        assertFalse(applyFitting().matches(Bench.input(bareTemplate(), set, ingot()), Bench.NO_LEVEL),
            "the same ingot was set into the same guard twice");
    }

    // ---- taking it out again ----------------------------------------------------------------

    /** With nothing in the third slot there is nothing to route by, so the absence names them all. */
    @Test
    void theBareTemplateEmptiesEveryFittingAtOnce() {
        final ItemStack both = applyFitting().assemble(Bench.input(bareTemplate(),
            applyFitting().assemble(Bench.input(bareTemplate(),
                wearing(DecorationAnchor.COLLAR, "guard", "inlay"), ingot())),
            Bench.stack(Items.DYE.pick(DyeColor.RED))));
        assertNotNull(Bench.entry(both, DecorationAnchor.COLLAR).fitting(guard()), "nothing was set to clear");
        assertNotNull(Bench.entry(both, DecorationAnchor.COLLAR).fitting(inlay()), "only one thing was set");

        final var input = Bench.input(bareTemplate(), both, Bench.nothing());
        assertTrue(clearFitting().matches(input, Bench.NO_LEVEL), "a fitted piece could not be cleared");
        final ItemStack cleared = clearFitting().assemble(input);

        assertTrue(Bench.entry(cleared, DecorationAnchor.COLLAR).fittings().isEmpty(),
            "the piece still holds something");
        assertNotNull(Bench.entry(cleared, DecorationAnchor.COLLAR).decoration(),
            "clearing the fittings took the part with it");
    }

    /** A named template has said which, and takes out only that. */
    @Test
    void aNamedTemplateEmptiesOnlyItsOwnFitting() {
        final ItemStack both = applyFitting().assemble(Bench.input(bareTemplate(),
            applyFitting().assemble(Bench.input(bareTemplate(),
                wearing(DecorationAnchor.COLLAR, "guard", "inlay"), ingot())),
            Bench.stack(Items.DYE.pick(DyeColor.RED))));

        final ItemStack cleared = clearFitting().assemble(
            Bench.input(ModItems.fittingTemplateFor(inlay()), both, Bench.nothing()));

        assertNull(Bench.entry(cleared, DecorationAnchor.COLLAR).fitting(inlay()), "the inlay was not emptied");
        assertNotNull(Bench.entry(cleared, DecorationAnchor.COLLAR).fitting(guard()),
            "the guard was emptied by a template that named the inlay");
    }

    /** Nothing set, nothing to take out. */
    @Test
    void emptyingAPieceWithNothingSetIsRefused() {
        assertFalse(clearFitting().matches(
            Bench.input(bareTemplate(), wearing(DecorationAnchor.COLLAR, "guard", "inlay"), Bench.nothing()),
            Bench.NO_LEVEL),
            "a piece with empty fittings could be emptied again");
    }
}
