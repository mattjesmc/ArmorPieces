package com.mattjesmc.armorpieces.recipe;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.mattjesmc.armorpieces.identity.Tolerant;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.registry.ModItems;
import com.mattjesmc.armorpieces.skin.ArmorSkin;
import com.mattjesmc.armorpieces.skin.ArmorSkinValue;
import net.minecraft.core.Holder;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * Reskinning a piece of armor, and taking the skin off again.
 *
 * <p>Almost none of this recipe's rule is in its own file. What may be skinned and what it costs are
 * read off the BASE STACK - {@code minecraft:equippable} for the slot, {@code minecraft:repairable}
 * for the price - so the answer is right for armor this mod has never heard of, and the
 * {@code addition} ingredient in the file is only there to give the recipe book a cycle of items to
 * show. That is exactly the kind of claim a test should hold onto: it is invisible in the data, and it
 * is what a reader of the file would get wrong.
 *
 * <p>The one exclusion that IS data is {@code #armorpieces:unskinnable_armor}, which the mod fills
 * with vanilla chainmail: the weave is chainmail's whole identity and it has no metal of its own.
 */
class SmithingSkinRecipeTest {
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

    private static SmithingSkinRecipe applySkin() {
        return Bench.recipe("apply_skin", SmithingSkinRecipe.class);
    }

    private static SmithingSkinRecipe clearSkin() {
        return Bench.recipe("clear_skin", SmithingSkinRecipe.class);
    }

    private static Holder<ArmorSkin> plate() {
        return Bench.skin("plate");
    }

    private static ItemStack template(final Holder<ArmorSkin> skin) {
        return ModItems.skinTemplateFor(skin);
    }

    /** What a stack wears under {@code armorpieces:skin}, or null. */
    private static ArmorSkinValue skinOn(final ItemStack stack) {
        return Tolerant.get(stack, ModDataComponents.SKIN);
    }

    // ---- what crafts ------------------------------------------------------------------------

    /** Re-skinning is re-forging: an iron helmet is re-skinned with the ingot that repairs it. */
    @Test
    void aSkinIsAppliedAtTheCostOfThePiecesOwnMaterial() {
        final var input = Bench.input(template(plate()), Bench.stack(Items.IRON_HELMET),
            Bench.stack(Items.IRON_INGOT));

        assertTrue(applySkin().matches(input, Bench.NO_LEVEL), "iron armor and an iron ingot did not match");
        final ItemStack skinned = applySkin().assemble(input);

        assertEquals(Items.IRON_HELMET, skinned.getItem(), "the craft changed the armor item");
        assertEquals(new ArmorSkinValue(plate()), skinOn(skinned), "the piece is not wearing the skin");
        assertTrue(skinned.has(net.minecraft.core.component.DataComponents.EQUIPPABLE),
            "vanilla's own equippable was taken off; a skinned piece must degrade to plain armor");
    }

    /** The price is the piece's own: a turtle helmet is reforged with a scute, and it is asked. */
    @Test
    void everyMaterialIsThePiecesOwn() {
        assertTrue(applySkin().matches(Bench.input(template(plate()),
            Bench.stack(Items.DIAMOND_CHESTPLATE), Bench.stack(Items.DIAMOND)), Bench.NO_LEVEL),
            "a diamond did not reforge a diamond chestplate");
        assertTrue(applySkin().matches(Bench.input(template(plate()),
            Bench.stack(Items.TURTLE_HELMET), Bench.stack(Items.TURTLE_SCUTE)), Bench.NO_LEVEL),
            "a scute did not reforge a turtle helmet");
    }

    // ---- what is refused --------------------------------------------------------------------

    /** An iron ingot held against a diamond helmet shows an empty result slot. */
    @Test
    void aMaterialThatDoesNotReforgeThisPieceIsRefused() {
        final var input = Bench.input(template(plate()), Bench.stack(Items.DIAMOND_HELMET),
            Bench.stack(Items.IRON_INGOT));

        assertFalse(applySkin().matches(input, Bench.NO_LEVEL), "iron reforged diamond");
        assertTrue(applySkin().assemble(input).isEmpty(), "and it produced something");
    }

    /** Chainmail refuses a skin, by the tag rather than by name. */
    @Test
    void chainmailRefusesASkin() {
        assertFalse(SmithingSkinRecipe.isSkinnable(Bench.stack(Items.CHAINMAIL_CHESTPLATE)),
            "chainmail is no longer in #armorpieces:unskinnable_armor");
        assertFalse(applySkin().matches(Bench.input(template(plate()),
            Bench.stack(Items.CHAINMAIL_CHESTPLATE), Bench.stack(Items.IRON_INGOT)), Bench.NO_LEVEL),
            "chainmail was skinned with the iron that repairs it");
    }

    /**
     * Equippable and repairable is not enough: a saddle is both, and there is no humanoid sheet to
     * skin on it.
     */
    @Test
    void onlyTheFourArmorSlotsAreSkinnable() {
        assertFalse(SmithingSkinRecipe.isSkinnable(Bench.stack(Items.SADDLE)), "a saddle was skinnable");
        assertTrue(SmithingSkinRecipe.isSkinnable(Bench.stack(Items.IRON_BOOTS)), "iron boots were not");
    }

    /** A template conjured without the component has no skin to apply. */
    @Test
    void aTemplateWithNoSkinOnItMatchesNothing() {
        final ItemStack bare = Bench.stack(ModItems.skinTemplate());
        assertNull(skinOn(bare), "the skin template item carries a skin by default now");

        assertFalse(applySkin().matches(
            Bench.input(bare, Bench.stack(Items.IRON_HELMET), Bench.stack(Items.IRON_INGOT)), Bench.NO_LEVEL),
            "an empty skin template matched");
    }

    /** The same skin again would cost an ingot and a template for nothing. */
    @Test
    void theSameSkinAgainIsRefused() {
        final ItemStack skinned = applySkin().assemble(Bench.input(
            template(plate()), Bench.stack(Items.IRON_HELMET), Bench.stack(Items.IRON_INGOT)));

        assertFalse(applySkin().matches(
            Bench.input(template(plate()), skinned, Bench.stack(Items.IRON_INGOT)), Bench.NO_LEVEL),
            "the same skin was applied twice");
        assertTrue(applySkin().matches(
            Bench.input(template(Bench.skin("mail")), skinned, Bench.stack(Items.IRON_INGOT)), Bench.NO_LEVEL),
            "and a different skin cannot be applied over it");
    }

    // ---- taking it off again ----------------------------------------------------------------

    /** An empty third slot is the instruction, and it costs the template. */
    @Test
    void anEmptyAdditionTakesTheSkinOff() {
        final ItemStack skinned = applySkin().assemble(Bench.input(
            template(plate()), Bench.stack(Items.IRON_HELMET), Bench.stack(Items.IRON_INGOT)));
        final var input = Bench.input(template(plate()), skinned, Bench.nothing());

        assertTrue(clearSkin().matches(input, Bench.NO_LEVEL), "a skinned piece could not be unskinned");
        final ItemStack stripped = clearSkin().assemble(input);

        assertNull(skinOn(stripped), "the skin is still on it");
        assertEquals(Items.IRON_HELMET, stripped.getItem(), "the armor did not survive");
    }

    /** Nothing to take off. */
    @Test
    void strippingAnUnskinnedPieceIsRefused() {
        assertFalse(clearSkin().matches(
            Bench.input(template(plate()), Bench.stack(Items.IRON_HELMET), Bench.nothing()), Bench.NO_LEVEL),
            "a plain piece was unskinned");
    }

    /**
     * Taking a skin off is never asked whether the piece may WEAR one. A pack that changes its mind
     * about what may be skinned - or the mod, the day chainmail went into the tag - must not strand
     * what was already skinned.
     */
    @Test
    void aPieceThatMayNoLongerBeSkinnedCanStillBeStripped() {
        final ItemStack chainmail = Bench.stack(Items.CHAINMAIL_CHESTPLATE);
        chainmail.set(ModDataComponents.SKIN, Tolerant.of(new ArmorSkinValue(plate())));
        assertFalse(SmithingSkinRecipe.isSkinnable(chainmail), "the piece under test is skinnable after all");

        final ItemStack stripped = SmithingSkinRecipe.applySkin(chainmail, Bench.nothing(), null);

        assertFalse(stripped.isEmpty(), "a piece that may not be skinned could not be unskinned either");
        assertNull(skinOn(stripped), "the skin is still on it");
    }
}
