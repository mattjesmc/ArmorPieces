package com.mattjesmc.armorpieces.decoration.effect;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.mattjesmc.armorpieces.GameBootstrap;
import com.mattjesmc.armorpieces.data.ShippedData;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mattjesmc.armorpieces.decoration.effect.builtin.AttributeEffect;
import com.mattjesmc.armorpieces.decoration.effect.builtin.BlinkEffect;
import com.mattjesmc.armorpieces.decoration.effect.builtin.ConditionalEffect;
import com.mattjesmc.armorpieces.decoration.effect.builtin.WearerConditionEffect;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.decoration.fitting.FittingPredicate;
import com.mattjesmc.armorpieces.decoration.fitting.builtin.MaterialFitting;
import com.google.gson.JsonParser;
import com.mojang.serialization.JsonOps;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import net.minecraft.core.Holder;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * What a decorated piece does to the numbers on its wearer, and what happens to those numbers when it
 * comes off again.
 *
 * <p>Attribute modifiers are the one thing this mod puts on an entity rather than on an item, and the
 * only thing it does that outlives the moment: everything else - a tick, a dodge, a glide - happens
 * and is over, while a modifier sits on the wearer until something takes it off. So the rule that
 * matters is not what is added but what is REMOVED, and the dispatcher's answer is unusual enough to
 * be worth pinning: it removes by {@code collectPossibleAttributes} - what the effect COULD give -
 * rather than by what it is giving, because a gate that has just stopped applying no longer offers
 * the modifier it granted a moment ago and an add-only pass would leave it on the entity for ever.
 *
 * <p>All of this is a pure function of an attribute map and two item stacks, so
 * {@link DecorationEffectDispatcher#equipmentChanged} runs here with no server under it. The
 * {@link ServerLevel} check that guards it in play stays at the event, where it belongs; see
 * {@link Wearer} for what an entity with no world can and cannot be asked.
 *
 * <p>The ids are written out in full rather than derived from the code that makes them - a test that
 * asks the dispatcher to spell its own scoping proves nothing about it.
 */
class WornAttributesTest {
    /** The mod's own jumping part, and the material case it ships. */
    private static final String HEEL_WINGS = "heel_wings";

    /** Where {@code heel_wings} rides. */
    private static final DecorationAnchor FOOT_SOCKET = DecorationAnchor.SPURS;

    @BeforeAll
    static void world() {
        GameBootstrap.content();
    }

    // ---- the number the material gets --------------------------------------------------------

    /**
     * {@code heel_wings} gives a tenth more jump, and netherite gives half again as much. The case
     * exists in the shipped file; what is asserted here is that the lookup answers with it - the same
     * {@link MaterialValue} every effect's numbers go through.
     */
    @Test
    void aMaterialCaseIsWhatThatMaterialGets() {
        final AttributeEffect jump = only(Wearer.shipped(HEEL_WINGS), AttributeEffect.class);
        assertEquals(0.1, jump.amount().get(Wearer.material("minecraft:iron")), 1.0e-9,
            "iron heel wings no longer give the part's default amount");
        assertEquals(0.15, jump.amount().get(Wearer.material("minecraft:netherite")), 1.0e-9,
            "the netherite case of heel_wings is not what netherite gets");
        assertEquals(Attributes.JUMP_STRENGTH, jump.attribute(), "heel_wings stopped being about jumping");
        assertEquals(AttributeModifier.Operation.ADD_MULTIPLIED_BASE, jump.operation(),
            "heel_wings' amount is a fraction of the base, not a flat number");
    }

    /**
     * A case may name a TAG of materials, and the exact case still wins over it: the cloak dodges a
     * quarter of the time in amethyst, which is both the exact case and a member of the tag the other
     * case names.
     */
    @Test
    void anExactCaseBeatsATagThatAlsoMatches() {
        final BlinkEffect blink = only(Wearer.shipped("cloak"), BlinkEffect.class);
        assertEquals(0.25F, blink.chance().get(Wearer.material("minecraft:amethyst")), 1.0e-6F,
            "amethyst no longer gets the cloak's own amethyst case");
        assertEquals(0.15F, blink.chance().get(Wearer.material("minecraft:diamond")), 1.0e-6F,
            "diamond is in the gemstones tag and did not get the tag's case");
        assertEquals(0.1F, blink.chance().get(Wearer.material("minecraft:iron")), 1.0e-6F,
            "a material no case names did not fall back to the default");
    }

    // ---- putting it on -----------------------------------------------------------------------

    /**
     * Equipping the part puts its modifier on the wearer, under an id scoped to the SOCKET, with the
     * amount its material gets.
     */
    @Test
    void equippingAddsTheModifierUnderTheSocketsOwnId() {
        final Wearer wearer = Wearer.zombie();
        final double before = wearer.value(Attributes.JUMP_STRENGTH);
        final ItemStack boots = shippedPiece(HEEL_WINGS, "minecraft:iron");

        equip(wearer, EquipmentSlot.FEET, boots);

        final AttributeModifier modifier = wearer.modifier(Attributes.JUMP_STRENGTH, "armorpieces:spurs/heel_wings_jump");
        assertNotNull(modifier, "heel wings put nothing on their wearer; ids present: "
            + wearer.modifierIds(Attributes.JUMP_STRENGTH));
        assertEquals(0.1, modifier.amount(), 1.0e-9, "the modifier was not the amount iron gets");
        assertEquals(AttributeModifier.Operation.ADD_MULTIPLIED_BASE, modifier.operation(),
            "the modifier was applied with the wrong operation");
        assertEquals(before * 1.1, wearer.value(Attributes.JUMP_STRENGTH), 1.0e-9,
            "the wearer does not actually jump any higher");
    }

    /** The same part in a different material is a different number, from the same file. */
    @Test
    void theMaterialOfThePartIsTheNumberOnTheWearer() {
        final Wearer wearer = Wearer.zombie();
        equip(wearer, EquipmentSlot.FEET, shippedPiece(HEEL_WINGS, "minecraft:netherite"));

        assertEquals(0.15,
            wearer.modifier(Attributes.JUMP_STRENGTH, "armorpieces:spurs/heel_wings_jump").amount(), 1.0e-9,
            "netherite heel wings gave the iron number");
    }

    // ---- the two shapes an author copies -----------------------------------------------------

    /**
     * Speed is a FRACTION of a small base, and the shipped {@code puttees} are the example of it.
     *
     * <p>What is worth pinning is not 0.05 but what 0.05 means: movement speed's base is 0.1, so the
     * same figure written as a flat {@code add_value} would be half again as fast rather than a
     * twentieth faster. The operation is what keeps a readable number readable, and it is the thing
     * an author copying this file has to have noticed.
     */
    @Test
    void aSpeedPartIsAFractionOfTheBaseRatherThanAFlatNumber() {
        final Wearer wearer = Wearer.zombie();
        final double before = wearer.value(Attributes.MOVEMENT_SPEED);
        equip(wearer, EquipmentSlot.FEET, shippedPiece(DecorationAnchor.GREAVES, "puttees", "minecraft:iron"));

        final AttributeModifier modifier =
            wearer.modifier(Attributes.MOVEMENT_SPEED, "armorpieces:greaves/puttees_speed");
        assertNotNull(modifier, "the puttees put nothing on their wearer; ids present: "
            + wearer.modifierIds(Attributes.MOVEMENT_SPEED));
        assertEquals(AttributeModifier.Operation.ADD_MULTIPLIED_BASE, modifier.operation(),
            "the puttees' amount stopped being a fraction of the base");
        assertEquals(before * 1.05, wearer.value(Attributes.MOVEMENT_SPEED), 1.0e-9,
            "a twentieth faster is not what the wearer ended up with");
    }

    /**
     * Hearts are the other shape: a flat number, counted in half-hearts, and the shipped
     * {@code gorget} gives one heart in iron and two in netherite.
     *
     * <p>What the wearer gets is a MAXIMUM. The health they are actually at is vanilla's business and
     * is not touched here - {@code LivingEntity.tick} refreshes the attributes a change marked dirty,
     * and {@code onAttributeUpdated} answers a lowered {@code MAX_HEALTH} by capping current health at
     * it. So the tick after this gorget comes off, a wearer who was full is back at their own maximum,
     * and no effect has to do that itself.
     */
    @Test
    void heartsAreAFlatNumberAndGoAgainWithThePiece() {
        final AttributeEffect hearts = only(Wearer.shipped("gorget"), AttributeEffect.class);
        assertEquals(AttributeModifier.Operation.ADD_VALUE, hearts.operation(),
            "the gorget's hearts stopped being a flat number");
        assertEquals(2.0, hearts.amount().get(Wearer.material("minecraft:iron")), 1.0e-9,
            "an iron gorget no longer gives one heart");
        assertEquals(4.0, hearts.amount().get(Wearer.material("minecraft:netherite")), 1.0e-9,
            "the netherite case of the gorget is not two hearts");

        final Wearer wearer = Wearer.zombie();
        final float bare = wearer.entity().getMaxHealth();
        final ItemStack chestplate = shippedPiece(DecorationAnchor.COLLAR, "gorget", "minecraft:netherite");

        equip(wearer, EquipmentSlot.CHEST, chestplate);
        assertNotNull(wearer.modifier(Attributes.MAX_HEALTH, "armorpieces:collar/gorget_health"),
            "the gorget put nothing on its wearer; ids present: " + wearer.modifierIds(Attributes.MAX_HEALTH));
        assertEquals(bare + 4.0F, wearer.entity().getMaxHealth(), 1.0e-5F,
            "a netherite gorget did not add two hearts to the maximum");

        unequip(wearer, EquipmentSlot.CHEST, chestplate);
        assertEquals(bare, wearer.entity().getMaxHealth(), 1.0e-5F,
            "the wearer kept the hearts of a gorget they are not wearing");
    }

    /**
     * Nothing this mod adds is ever written to disk: a crash between the equip and the unequip cannot
     * leave a player permanently buffed by a part they no longer own.
     */
    @Test
    void everyModifierIsTransient() {
        final Wearer wearer = Wearer.zombie();
        equip(wearer, EquipmentSlot.FEET, shippedPiece(HEEL_WINGS, "minecraft:iron"));

        final AttributeInstance jump = wearer.attribute(Attributes.JUMP_STRENGTH);
        assertNotNull(jump, "a zombie has no jump strength any more");
        assertEquals(Set.of(), jump.getPermanentModifiers(),
            "a decoration's modifier was saved to the entity");
    }

    /**
     * One part worn in two sockets contributes twice, because the id it lands under is the socket's.
     *
     * <p>Attribute modifiers are keyed by id, so without the scoping this part would contribute one
     * modifier that silently replaced itself - and the reading of "a spike on both the crest and the
     * brow" would quietly be "a spike".
     */
    @Test
    void theSamePartInTwoSocketsStacks() {
        final Holder<ArmorDecoration> spike = Wearer.part(
            Set.of(DecorationAnchor.CREST, DecorationAnchor.BROW), List.of(), armor(1.0));
        final ItemStack helmet = Wearer.piece(EquipmentSlot.HEAD, Map.of(
            DecorationAnchor.CREST, new DecorationEntry(Wearer.material("minecraft:iron"), spike),
            DecorationAnchor.BROW, new DecorationEntry(Wearer.material("minecraft:iron"), spike)));

        final Wearer wearer = Wearer.zombie();
        final double before = wearer.value(Attributes.ARMOR);
        equip(wearer, EquipmentSlot.HEAD, helmet);

        assertEquals(
            Set.of(Identifier.parse("armorpieces:crest/spike"), Identifier.parse("armorpieces:brow/spike")),
            wearer.modifierIds(Attributes.ARMOR),
            "one part in two sockets did not contribute two modifiers");
        assertEquals(before + 2.0, wearer.value(Attributes.ARMOR), 1.0e-9,
            "the two sockets did not add up");
    }

    // ---- taking it off -----------------------------------------------------------------------

    @Test
    void takingThePieceOffTakesTheModifierWithIt() {
        final Wearer wearer = Wearer.zombie();
        final ItemStack boots = shippedPiece(HEEL_WINGS, "minecraft:iron");
        equip(wearer, EquipmentSlot.FEET, boots);

        unequip(wearer, EquipmentSlot.FEET, boots);

        assertEquals(Set.of(), wearer.modifierIds(Attributes.JUMP_STRENGTH),
            "the wearer kept the jump of a pair of boots they are not wearing");
    }

    /**
     * The rule the whole reconcile is built around: a gate takes back exactly what it COULD have
     * given.
     *
     * <p>The part's modifier applies while its fitting holds a gem. Swap the gem out and the gate no
     * longer offers the modifier at all - so a removal that asked what the effect is giving would
     * have nothing to name, and the wearer would keep the armor for ever. It is removed because the
     * gate answers the other question honestly.
     */
    @Test
    void aGateTakesBackWhatItCouldHaveGiven() {
        final Holder<Fitting> gemstone = Wearer.fitting("gemstone");
        final Holder<ArmorDecoration> circlet = Wearer.part(
            Set.of(DecorationAnchor.BROW),
            List.of(gemstone),
            new ConditionalEffect(new FittingPredicate(gemstone, Optional.empty(), Optional.empty()), armor(2.0)));

        final DecorationEntry set = new DecorationEntry(Wearer.material("minecraft:gold"), circlet)
            .withFitting(gemstone, new MaterialFitting.Value(Wearer.material("minecraft:emerald")));
        final DecorationEntry empty = new DecorationEntry(Wearer.material("minecraft:gold"), circlet);
        final ItemStack withGem = Wearer.piece(EquipmentSlot.HEAD, Map.of(DecorationAnchor.BROW, set));
        final ItemStack withoutGem = Wearer.piece(EquipmentSlot.HEAD, Map.of(DecorationAnchor.BROW, empty));

        final Wearer wearer = Wearer.zombie();
        final double bare = wearer.value(Attributes.ARMOR);
        equip(wearer, EquipmentSlot.HEAD, withGem);
        assertEquals(bare + 2.0, wearer.value(Attributes.ARMOR), 1.0e-9,
            "the gem in the fitting did not switch the modifier on");

        wearer.wearing(EquipmentSlot.HEAD, withoutGem);
        DecorationEffectDispatcher.equipmentChanged(wearer.entity(), EquipmentSlot.HEAD, withGem, withoutGem);

        assertEquals(Set.of(), wearer.modifierIds(Attributes.ARMOR),
            "the gem was taken out and the wearer kept the armor it granted");
    }

    /**
     * A condition that stops holding while the piece stays on is taken back at the next reconcile.
     *
     * <p>This is the case the whole rule exists for, and the only one nothing else could catch: the
     * item did not change, so there is no "previous" to remove from - the wearer simply picked
     * something up, and the claws stopped biting. The removal finds the modifier because the effect
     * still says what it COULD grant.
     */
    @Test
    void aConditionThatStopsHoldingIsTakenBackWithoutTheItemChanging() {
        final Spy.Gated gate = new Spy.Gated(4.0);
        final ItemStack helmet = Wearer.piece(DecorationAnchor.BROW,
            Wearer.entry(Wearer.part(DecorationAnchor.BROW, gate), "minecraft:iron"));
        final Wearer wearer = Wearer.zombie();
        equip(wearer, EquipmentSlot.HEAD, helmet);
        assertEquals(Set.of(Identifier.parse("armorpieces:brow/gated")), wearer.modifierIds(Attributes.ARMOR),
            "the condition held and its modifier was not applied");

        gate.granting = false;
        DecorationEffectDispatcher.equipmentChanged(
            wearer.entity(), EquipmentSlot.MAINHAND, ItemStack.EMPTY, Wearer.plain(Items.IRON_SWORD));

        assertEquals(Set.of(), wearer.modifierIds(Attributes.ARMOR),
            "the condition stopped holding and the modifier stayed on the wearer for ever");
    }

    /**
     * And the same when the piece comes off after the condition stopped holding: the removal is over
     * what the piece COULD have granted, so a modifier granted an hour ago still goes with it.
     */
    @Test
    void aPieceComingOffTakesBackWhatItsConditionCouldHaveGranted() {
        final Spy.Gated gate = new Spy.Gated(4.0);
        final ItemStack helmet = Wearer.piece(DecorationAnchor.BROW,
            Wearer.entry(Wearer.part(DecorationAnchor.BROW, gate), "minecraft:iron"));
        final Wearer wearer = Wearer.zombie();
        equip(wearer, EquipmentSlot.HEAD, helmet);

        gate.granting = false;
        unequip(wearer, EquipmentSlot.HEAD, helmet);

        assertEquals(Set.of(), wearer.modifierIds(Attributes.ARMOR),
            "the piece was taken off and left its modifier behind");
    }

    /**
     * The same, in the one case where the gate cannot even be evaluated: a wearer condition is false
     * off the server (vanilla's entity predicate needs a level), so the modifier is never granted -
     * and it is still offered to the removal, which is what keeps it from becoming permanent the day
     * a server DOES grant it.
     */
    @Test
    void aWearerGateGrantsNothingHereAndIsStillTakenBack() {
        final AttributeEffect armor = armor(3.0);
        final WearerConditionEffect gate = new WearerConditionEffect(
            wearerPredicate("{\"equipment\": {\"mainhand\": {\"items\": \"minecraft:air\"}}}"), armor);
        final DecorationEffectContext context = contextFor(gate);

        assertFalse(gate.applies(context),
            "a condition about the wearer answered yes with no server to answer it");
        assertEquals(List.of(), collect(gate::collectAttributes, context),
            "a wearer condition granted a modifier with no server to evaluate it");
        assertEquals(List.of(armor.id()), collect(gate::collectPossibleAttributes, context),
            "a wearer condition did not offer what it could have granted to the removal");
    }

    // ---- the moments a reconcile happens -----------------------------------------------------

    /**
     * A hand change reconciles the ARMOR slots, though no socket rides on a hand.
     *
     * <p>That is what buys {@code if_wearer} its equipment tier: a modifier that depends on what the
     * wearer is holding is recomputed at every moment that can change, and so never goes stale. Here
     * the boots are already on and no equip has been run for them; the hand change alone is what puts
     * their modifier on.
     */
    @Test
    void aHandChangeRecomputesTheArmorSlots() {
        final Wearer wearer = Wearer.zombie().wearing(EquipmentSlot.FEET, shippedPiece(HEEL_WINGS, "minecraft:iron"));
        assertEquals(Set.of(), wearer.modifierIds(Attributes.JUMP_STRENGTH),
            "the fixture put the boots on through the dispatcher, which this test is about");

        DecorationEffectDispatcher.equipmentChanged(
            wearer.entity(), EquipmentSlot.MAINHAND, ItemStack.EMPTY, Wearer.plain(Items.STICK));

        assertEquals(Set.of(Identifier.parse("armorpieces:spurs/heel_wings_jump")),
            wearer.modifierIds(Attributes.JUMP_STRENGTH),
            "a hand change did not reconcile the armor slots");
    }

    /** A slot that is neither armor nor a hand - the body of a horse, a saddle - reconciles nothing. */
    @Test
    void aBodySlotChangeIsNotAReconcile() {
        final Wearer wearer = Wearer.zombie().wearing(EquipmentSlot.FEET, shippedPiece(HEEL_WINGS, "minecraft:iron"));

        DecorationEffectDispatcher.equipmentChanged(
            wearer.entity(), EquipmentSlot.BODY, ItemStack.EMPTY, Wearer.plain(Items.SADDLE));

        assertEquals(Set.of(), wearer.modifierIds(Attributes.JUMP_STRENGTH),
            "a body slot change reconciled the armor slots");
    }

    // ---- helpers -----------------------------------------------------------------------------

    private static void equip(final Wearer wearer, final EquipmentSlot slot, final ItemStack piece) {
        wearer.wearing(slot, piece);
        DecorationEffectDispatcher.equipmentChanged(wearer.entity(), slot, ItemStack.EMPTY, piece);
    }

    private static void unequip(final Wearer wearer, final EquipmentSlot slot, final ItemStack piece) {
        wearer.wearing(slot, ItemStack.EMPTY);
        DecorationEffectDispatcher.equipmentChanged(wearer.entity(), slot, piece, ItemStack.EMPTY);
    }

    /** One of the mod's own parts, in one material, on the piece its socket belongs to. */
    private static ItemStack shippedPiece(final String path, final String material) {
        return shippedPiece(FOOT_SOCKET, path, material);
    }

    /** The same, for a part that rides somewhere other than the foot socket this file mostly uses. */
    private static ItemStack shippedPiece(
        final DecorationAnchor socket,
        final String path,
        final String material
    ) {
        final Holder<ArmorDecoration> part = Wearer.shipped(path);
        return Wearer.piece(socket, new DecorationEntry(Wearer.material(material), part));
    }

    /** The one effect of that kind a shipped part carries. */
    private static <T extends DecorationEffect> T only(final Holder<ArmorDecoration> part, final Class<T> type) {
        final List<DecorationEffect> found = part.value().effects().stream().filter(type::isInstance).toList();
        assertEquals(1, found.size(),
            () -> part.value().assetId() + " no longer carries exactly one " + type.getSimpleName());
        return type.cast(found.getFirst());
    }

    /** A flat armor modifier, the simplest thing an effect can contribute. */
    private static AttributeEffect armor(final double amount) {
        return new AttributeEffect(
            Identifier.fromNamespaceAndPath("armorpieces", "spike"),
            Attributes.ARMOR,
            MaterialValue.of(amount),
            AttributeModifier.Operation.ADD_VALUE);
    }

    /**
     * Vanilla's entity predicate, written the way a part file writes it.
     *
     * <p>Through the LOAD's ops rather than plain {@code JsonOps}: {@code {"items": "minecraft:air"}}
     * is a holder set of one, and a holder set only reads a bare id when the ops can reach the
     * registry to resolve it. With plain ops the same line a shipped part carries is refused as "not
     * a json array".
     */
    private static WearerPredicate wearerPredicate(final String json) {
        return WearerPredicate.CODEC
            .parse(ShippedData.mod().full().createSerializationContext(JsonOps.INSTANCE), JsonParser.parseString(json))
            .getOrThrow();
    }

    /** The occasion one effect is running on, with a wearer wearing the part that carries it. */
    private static DecorationEffectContext contextFor(final DecorationEffect effect) {
        final Holder<ArmorDecoration> part = Wearer.part(DecorationAnchor.BROW, effect);
        final DecorationEntry entry = new DecorationEntry(Wearer.material("minecraft:iron"), part);
        final ItemStack helmet = Wearer.piece(DecorationAnchor.BROW, entry);
        final Wearer wearer = Wearer.zombie().wearing(EquipmentSlot.HEAD, helmet);
        return new DecorationEffectContext(wearer.entity(), DecorationAnchor.BROW, helmet, entry);
    }

    private static List<Identifier> collect(
        final java.util.function.BiConsumer<DecorationEffectContext, java.util.function.BiConsumer<Holder<Attribute>, AttributeModifier>> call,
        final DecorationEffectContext context
    ) {
        final List<Identifier> ids = new ArrayList<>();
        call.accept(context, (attribute, modifier) -> ids.add(modifier.id()));
        return ids;
    }
}
