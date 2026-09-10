package com.mattjesmc.armorpieces.recipe;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.mattjesmc.armorpieces.cloth.Cloth;
import com.mattjesmc.armorpieces.cloth.ClothValue;
import com.mattjesmc.armorpieces.identity.Tolerant;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.registry.ModItems;
import java.util.List;
import java.util.Optional;
import net.minecraft.core.Holder;
import net.minecraft.resources.Identifier;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.entity.BannerPattern;
import net.minecraft.world.level.block.entity.BannerPatternLayers;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * Putting a garment over a piece of armor, and taking it off again.
 *
 * <p>The garment comes off the TEMPLATE and the design comes off the BANNER, and that split is the
 * whole of this recipe: a cloth template carries a bare {@code {"cloth": "..."}} with no colour on
 * it, and the colour and the pattern layers are read from the banner in the addition slot because
 * that is where the player put them. A test can hold that where a file cannot show it.
 *
 * <p>Only the chest is clothable, and by data ({@code #armorpieces:clothable_armor}) as well as by
 * slot, so a pack can shrink the set without touching Java.
 */
class SmithingClothRecipeTest {
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

    private static SmithingClothRecipe applyCloth() {
        return Bench.recipe("apply_cloth", SmithingClothRecipe.class);
    }

    private static SmithingClothRecipe clearCloth() {
        return Bench.recipe("clear_cloth", SmithingClothRecipe.class);
    }

    private static Holder<Cloth> tunic() {
        return Bench.cloth("tunic");
    }

    private static ItemStack template(final Holder<Cloth> cloth) {
        return ModItems.clothTemplateFor(cloth);
    }

    /** What a stack wears under {@code armorpieces:cloth}, or null. */
    private static ClothValue clothOn(final ItemStack stack) {
        return Tolerant.get(stack, ModDataComponents.CLOTH);
    }

    /**
     * A design a player would have sewn onto a banner. The pattern is a direct holder rather than a
     * registry one: {@code minecraft:banner_pattern} is a datapack registry no test here loads, and
     * what is under test is that the layers travel VERBATIM, whatever they are.
     */
    private static BannerPatternLayers design() {
        return new BannerPatternLayers(List.of(new BannerPatternLayers.Layer(
            Holder.direct(new BannerPattern(Identifier.parse("minecraft:cross"), "block.minecraft.banner.cross")),
            DyeColor.WHITE)));
    }

    // ---- what crafts ------------------------------------------------------------------------

    @Test
    void theTemplateBringsTheGarmentAndTheBannerBringsTheDesign() {
        final ItemStack banner = Bench.banner(DyeColor.RED, Optional.of(design()));
        assertEquals(ClothValue.of(tunic()), clothOn(template(tunic())),
            "a cloth template no longer carries a bare garment; the rest of this test is about that");
        final var input = Bench.input(template(tunic()), Bench.stack(Items.IRON_CHESTPLATE), banner);

        assertTrue(applyCloth().matches(input, Bench.NO_LEVEL), "a chestplate and a banner did not match");
        final ItemStack clothed = applyCloth().assemble(input);

        assertEquals(new ClothValue(tunic(), DyeColor.RED, design()), clothOn(clothed),
            "the garment is not the template's, or the design is not the banner's");
        assertEquals(Items.IRON_CHESTPLATE, clothed.getItem(), "the craft changed the armor item");
    }

    /** A banner with nothing on it is a plain field, and that is a design too. */
    @Test
    void aPlainBannerIsAPlainGarment() {
        final ItemStack clothed = applyCloth().assemble(Bench.input(template(tunic()),
            Bench.stack(Items.IRON_CHESTPLATE), Bench.banner(DyeColor.BLUE, Optional.empty())));

        assertEquals(new ClothValue(tunic(), DyeColor.BLUE, BannerPatternLayers.EMPTY), clothOn(clothed),
            "a plain banner did not make a plain garment in its own colour");
    }

    /** Another banner over the same garment is a re-dye, not a refusal. */
    @Test
    void anotherBannerChangesTheDesign() {
        final ItemStack red = applyCloth().assemble(Bench.input(template(tunic()),
            Bench.stack(Items.IRON_CHESTPLATE), Bench.banner(DyeColor.RED, Optional.empty())));

        final ItemStack blue = applyCloth().assemble(Bench.input(
            template(tunic()), red, Bench.banner(DyeColor.BLUE, Optional.empty())));

        assertEquals(DyeColor.BLUE, clothOn(blue).base(), "the garment kept its old colour");
    }

    // ---- what is refused --------------------------------------------------------------------

    /** Only the chest wears cloth: there is nowhere on a legging to composite a garment. */
    @Test
    void onlyTheChestSlotIsClothable() {
        assertFalse(SmithingClothRecipe.isClothable(Bench.stack(Items.IRON_LEGGINGS)), "leggings were clothable");
        assertTrue(SmithingClothRecipe.isClothable(Bench.stack(Items.IRON_CHESTPLATE)),
            "a chestplate was not clothable");
        assertFalse(applyCloth().matches(Bench.input(template(tunic()), Bench.stack(Items.IRON_LEGGINGS),
            Bench.banner(DyeColor.RED, Optional.empty())), Bench.NO_LEVEL),
            "the recipe accepted leggings");
    }

    /** The same garment in the same design again would consume the banner for nothing. */
    @Test
    void theSameGarmentInTheSameDesignAgainIsRefused() {
        final ItemStack clothed = applyCloth().assemble(Bench.input(template(tunic()),
            Bench.stack(Items.IRON_CHESTPLATE), Bench.banner(DyeColor.RED, Optional.of(design()))));
        final var again = Bench.input(template(tunic()), clothed,
            Bench.banner(DyeColor.RED, Optional.of(design())));

        assertFalse(applyCloth().matches(again, Bench.NO_LEVEL), "the identical garment was sewn twice");
        assertTrue(applyCloth().assemble(again).isEmpty(), "and something came out of it");
    }

    /** A template conjured without the component has no garment to put on. */
    @Test
    void aTemplateWithNoGarmentMatchesNothing() {
        final ItemStack bare = Bench.stack(ModItems.clothTemplate());
        assertNull(clothOn(bare), "the cloth template item carries a garment by default now");

        assertFalse(applyCloth().matches(Bench.input(bare, Bench.stack(Items.IRON_CHESTPLATE),
            Bench.banner(DyeColor.RED, Optional.empty())), Bench.NO_LEVEL),
            "an empty cloth template matched");
    }

    /**
     * The colour and the layers are a banner's, so the addition has to be one - asked of the static
     * rule, since the shipped file's {@code #minecraft:banners} never offers anything else.
     */
    @Test
    void anAdditionThatIsNotABannerIsRefused() {
        assertTrue(SmithingClothRecipe.applyCloth(Bench.stack(Items.IRON_CHESTPLATE),
            Bench.stack(Items.WOOL.pick(DyeColor.RED)), ClothValue.of(tunic())).isEmpty(),
            "a bolt of wool became a garment");
    }

    // ---- taking it off again ----------------------------------------------------------------

    @Test
    void anEmptyAdditionStripsTheGarment() {
        final ItemStack clothed = applyCloth().assemble(Bench.input(template(tunic()),
            Bench.stack(Items.IRON_CHESTPLATE), Bench.banner(DyeColor.RED, Optional.empty())));
        final var input = Bench.input(template(tunic()), clothed, Bench.nothing());

        assertTrue(clearCloth().matches(input, Bench.NO_LEVEL), "a clothed piece could not be stripped");
        final ItemStack stripped = clearCloth().assemble(input);

        assertNull(clothOn(stripped), "the garment is still on it");
        assertEquals(Items.IRON_CHESTPLATE, stripped.getItem(), "the armor did not survive");
    }

    @Test
    void strippingABarePieceIsRefused() {
        assertFalse(clearCloth().matches(Bench.input(template(tunic()),
            Bench.stack(Items.IRON_CHESTPLATE), Bench.nothing()), Bench.NO_LEVEL),
            "a piece with no garment was stripped");
    }

    /**
     * Stripping is never asked whether the piece may WEAR cloth, for the reason the skin recipe gives:
     * a pack that shrinks {@code #armorpieces:clothable_armor} must not strand what it already clothed.
     */
    @Test
    void aPieceThatMayNoLongerWearClothCanStillBeStripped() {
        final ItemStack leggings = Bench.stack(Items.IRON_LEGGINGS);
        leggings.set(ModDataComponents.CLOTH, Tolerant.of(ClothValue.of(tunic())));
        assertFalse(SmithingClothRecipe.isClothable(leggings), "the piece under test is clothable after all");

        final ItemStack stripped = SmithingClothRecipe.applyCloth(leggings, Bench.nothing(), null);

        assertFalse(stripped.isEmpty(), "a piece that may not be clothed could not be stripped either");
        assertNull(clothOn(stripped), "the garment is still on it");
    }
}
