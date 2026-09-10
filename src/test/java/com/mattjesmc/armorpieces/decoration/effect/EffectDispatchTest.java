package com.mattjesmc.armorpieces.decoration.effect;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.mattjesmc.armorpieces.GameBootstrap;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import net.minecraft.core.Holder;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * The walk from a living entity to the effects it is wearing: which sockets are reached, which are
 * skipped, and what the effect is told when it is.
 *
 * <p>{@link DecorationEffectDispatcher#anyWorn} and {@code forEachWorn} are the single entry point to
 * everything this mod does in play - every hook, every event, and any other mod that wants to ask
 * what an entity is wearing that does X - and until now the only thing that had ever run them was a
 * real server with a real player in it. Nothing in the walk needs one: it reads an entity's four
 * armor slots and the component on each piece. {@link Wearer} is that entity with the world left out.
 *
 * <p>The rules here are the ones a reader of the dispatcher would otherwise have to take on trust:
 * hands are not armor, a socket riding on the wrong piece is skipped rather than honoured, an effect
 * is only visited for the hook it implements, the first refusal ends the question, and one context is
 * built per socket rather than per effect.
 *
 * <p>What is deliberately NOT asserted is the order sockets on one piece are visited in. The
 * component's map is a {@code Map.copyOf}, so it has no order; the tooltip is what sorts by anchor,
 * and the dispatcher has no reason to. Slots, on the other hand, are a list, and head-to-toe is
 * asserted below.
 */
class EffectDispatchTest {
    @BeforeAll
    static void world() {
        GameBootstrap.content();
    }

    // ---- who is visited ----------------------------------------------------------------------

    @Test
    void anEntityWearingNothingIsAskedNothing() {
        final Wearer wearer = Wearer.zombie();
        assertEquals(List.of(), ticked(wearer), "an effect was reached on a naked zombie");
        assertFalse(
            DecorationEffectDispatcher.anyWorn(wearer.entity(), DecorationEffect.Gliding.class,
                (effect, context) -> true),
            "something worn answered for an entity wearing nothing");
    }

    @Test
    void plainArmorIsNotVisited() {
        final Wearer wearer = Wearer.zombie().wearing(EquipmentSlot.HEAD, Wearer.plain(Items.IRON_HELMET));
        assertEquals(List.of(), ticked(wearer), "an undecorated helmet reached an effect");
    }

    @Test
    void aPieceWhoseComponentIsEmptyIsNotVisited() {
        final ItemStack helmet = Wearer.plain(Items.IRON_HELMET);
        helmet.set(ModDataComponents.DECORATIONS, ArmorDecorations.EMPTY);
        final Wearer wearer = Wearer.zombie().wearing(EquipmentSlot.HEAD, helmet);
        assertEquals(List.of(), ticked(wearer), "a piece decorated with nothing reached an effect");
    }

    @Test
    void aPartThatDoesNothingIsNotVisited() {
        final Spy.Tick spy = new Spy.Tick();
        final Wearer wearer = Wearer.zombie().wearing(EquipmentSlot.HEAD, Wearer.piece(
            EquipmentSlot.HEAD,
            Map.of(
                DecorationAnchor.CREST, Wearer.entry(Wearer.part(DecorationAnchor.CREST, spy), "minecraft:iron"),
                DecorationAnchor.BROW, Wearer.entry(Wearer.part(DecorationAnchor.BROW), "minecraft:iron"))));

        assertEquals(List.of(spy), ticked(wearer),
            "the effectless part in the other socket cost something a visit");
    }

    /**
     * Every socket on a piece is reached, and a piece in every armor slot is - in the dispatcher's own
     * head-to-toe order, which is the one thing about ordering that IS fixed.
     */
    @Test
    void everySocketOnEveryArmorSlotIsReachedHeadToToe() {
        final Spy.Tick head = new Spy.Tick();
        final Spy.Tick brow = new Spy.Tick();
        final Spy.Tick chest = new Spy.Tick();
        final Spy.Tick legs = new Spy.Tick();
        final Spy.Tick feet = new Spy.Tick();
        final Wearer wearer = Wearer.zombie()
            .wearing(EquipmentSlot.FEET, Wearer.piece(DecorationAnchor.SPURS, socket(DecorationAnchor.SPURS, feet)))
            .wearing(EquipmentSlot.LEGS, Wearer.piece(DecorationAnchor.BELT, socket(DecorationAnchor.BELT, legs)))
            .wearing(EquipmentSlot.CHEST, Wearer.piece(DecorationAnchor.BACK, socket(DecorationAnchor.BACK, chest)))
            .wearing(EquipmentSlot.HEAD, Wearer.piece(EquipmentSlot.HEAD, Map.of(
                DecorationAnchor.CREST, socket(DecorationAnchor.CREST, head),
                DecorationAnchor.BROW, socket(DecorationAnchor.BROW, brow))));

        final List<Spy> reached = ticked(wearer);
        assertEquals(5, reached.size(), "not every worn socket was reached: " + reached);
        assertEquals(Set.of(head, brow), Set.copyOf(reached.subList(0, 2)),
            "the head's two sockets were not the first two reached");
        assertEquals(List.of(chest, legs, feet), reached.subList(2, 5),
            "the pieces were not walked head to toe");
    }

    /**
     * A socket that does not belong to the piece it is written on is skipped.
     *
     * <p>Not hypothetical: the component can be written by a command, and the render layer keeps the
     * same guard. A crest in a boot draws nothing, and by the same token it does nothing.
     */
    @Test
    void aSocketRidingOnTheWrongPieceIsSkipped() {
        final Spy.Tick spy = new Spy.Tick();
        final ItemStack boots = Wearer.decorated(Items.IRON_BOOTS,
            Map.of(DecorationAnchor.CREST, socket(DecorationAnchor.CREST, spy)));

        assertEquals(List.of(), ticked(Wearer.zombie().wearing(EquipmentSlot.FEET, boots)),
            "a crest written into a pair of boots was honoured");
    }

    /** No socket rides on a hand, so a decorated piece held in one does nothing. */
    @Test
    void aDecoratedPieceInAHandIsNotWorn() {
        final Spy.Tick spy = new Spy.Tick();
        final ItemStack helmet = Wearer.piece(DecorationAnchor.CREST, socket(DecorationAnchor.CREST, spy));

        assertEquals(List.of(), ticked(Wearer.zombie().wearing(EquipmentSlot.MAINHAND, helmet)),
            "a decorated helmet in the main hand reached its effect");
    }

    // ---- which hook, and how many times ------------------------------------------------------

    @Test
    void anEffectIsOnlyReachedForTheHookItImplements() {
        final Spy.Tick ticking = new Spy.Tick();
        final Spy.Hit damage = new Spy.Hit(true);
        final Wearer wearer = Wearer.zombie().wearing(EquipmentSlot.HEAD,
            Wearer.piece(DecorationAnchor.CREST,
                Wearer.entry(Wearer.part(DecorationAnchor.CREST, ticking, damage), "minecraft:iron")));

        assertEquals(List.of(ticking), ticked(wearer), "the damage effect was reached on the tick path");

        final List<Spy> hit = new ArrayList<>();
        DecorationEffectDispatcher.forEachWorn(wearer.entity(), DecorationEffect.Damage.class,
            (effect, context) -> hit.add((Spy) effect));
        assertEquals(List.of(damage), hit, "the ticking effect was reached on the damage path");
    }

    /** The first effect to answer yes settles the question, and the rest are not asked. */
    @Test
    void anyWornStopsAtTheFirstYes() {
        final Spy.Wings first = new Spy.Wings(true);
        final Spy.Wings second = new Spy.Wings(true);
        final Wearer wearer = Wearer.zombie().wearing(EquipmentSlot.CHEST,
            Wearer.piece(DecorationAnchor.BACK,
                Wearer.entry(Wearer.part(DecorationAnchor.BACK, first, second), "minecraft:iron")));

        assertTrue(
            DecorationEffectDispatcher.anyWorn(wearer.entity(), DecorationEffect.Gliding.class,
                (effect, context) -> effect.allowsGliding(context)),
            "a part granting gliding was not heard");
        assertEquals(1, first.count(), "the first gliding effect was not asked exactly once");
        assertEquals(0, second.count(), "the question was settled and the second effect was asked anyway");
    }

    @Test
    void forEachWornAsksEveryOne() {
        final Spy.Wings first = new Spy.Wings(true);
        final Spy.Wings second = new Spy.Wings(true);
        final Wearer wearer = Wearer.zombie().wearing(EquipmentSlot.CHEST,
            Wearer.piece(DecorationAnchor.BACK,
                Wearer.entry(Wearer.part(DecorationAnchor.BACK, first, second), "minecraft:iron")));

        DecorationEffectDispatcher.forEachWorn(wearer.entity(), DecorationEffect.Gliding.class,
            (effect, context) -> effect.allowsGliding(context));
        assertEquals(1, first.count(), "the first effect was not visited once");
        assertEquals(1, second.count(), "forEachWorn stopped early");
    }

    // ---- what the effect is told -------------------------------------------------------------

    /**
     * One context per socket, not one per effect: two effects on the same part are handed the same
     * object, which is the allocation the dispatcher's own note promises.
     */
    @Test
    void oneContextIsBuiltPerSocket() {
        final Spy.Tick first = new Spy.Tick();
        final Spy.Tick second = new Spy.Tick();
        final Wearer wearer = Wearer.zombie().wearing(EquipmentSlot.HEAD,
            Wearer.piece(DecorationAnchor.CREST,
                Wearer.entry(Wearer.part(DecorationAnchor.CREST, first, second), "minecraft:iron")));

        ticked(wearer);
        assertSame(first.last(), second.last(),
            "two effects on one part were handed two different contexts");
    }

    /**
     * The context is the occasion, and every part of it: the live stack rather than a copy - an
     * effect that damages the piece has to write to what the wearer has on - the socket, the slot the
     * socket fixes, the wearer, the entry and the material it is made in.
     */
    @Test
    void theContextIsTheOccasionItself() {
        final Spy.Tick spy = new Spy.Tick();
        final Holder<ArmorDecoration> part = Wearer.part(DecorationAnchor.SPURS, spy);
        final DecorationEntry entry = Wearer.entry(part, "minecraft:gold");
        final Wearer wearer = Wearer.zombie()
            .wearing(EquipmentSlot.FEET, Wearer.piece(DecorationAnchor.SPURS, entry));

        ticked(wearer);
        final DecorationEffectContext context = spy.last();
        assertSame(wearer.entity(), context.wearer(), "the context named somebody else as the wearer");
        assertSame(wearer.worn(EquipmentSlot.FEET), context.stack(),
            "the context carried a copy of the piece rather than the piece being worn");
        assertEquals(DecorationAnchor.SPURS, context.anchor(), "the context named the wrong socket");
        assertEquals(EquipmentSlot.FEET, context.slot(), "the slot did not follow from the socket");
        assertSame(entry, context.entry(), "the context carried a different entry");
        assertSame(part, context.decoration(), "the context named a different part");
        assertEquals(Wearer.material("minecraft:gold"), context.material(),
            "the part was reported in the wrong material");
    }

    /** Off a server there is no server level, and the context says so rather than pretending. */
    @Test
    void thereIsNoServerLevelWithoutAServer() {
        final Spy.Tick spy = new Spy.Tick();
        final Wearer wearer = Wearer.zombie().wearing(EquipmentSlot.HEAD,
            Wearer.piece(DecorationAnchor.CREST, socket(DecorationAnchor.CREST, spy)));

        ticked(wearer);
        assertNull(spy.last().serverLevel(),
            "a context with no world claimed a server level");
    }

    // ---- put on and taken off ----------------------------------------------------------------

    /**
     * Equipping and unequipping reach {@code Lifecycle} in that order, and a swap is both: the piece
     * coming off is told first, over ITS own decorations, and then the piece going on.
     */
    @Test
    void aSwapTellsThePieceComingOffBeforeThePieceGoingOn() {
        final Spy.Worn off = new Spy.Worn();
        final Spy.Worn on = new Spy.Worn();
        final ItemStack previous = Wearer.piece(DecorationAnchor.CREST, socket(DecorationAnchor.CREST, off));
        final ItemStack current = Wearer.piece(DecorationAnchor.CREST, socket(DecorationAnchor.CREST, on));
        final Wearer wearer = Wearer.zombie().wearing(EquipmentSlot.HEAD, current);

        DecorationEffectDispatcher.equipmentChanged(wearer.entity(), EquipmentSlot.HEAD, previous, current);

        assertEquals(List.of("unequip"), off.calls, "the piece taken off was not told, or was told twice");
        assertEquals(List.of("equip"), on.calls, "the piece put on was not told, or was told twice");
        assertSame(previous, off.last().stack(), "the unequip was told about the wrong piece");
        assertSame(current, on.last().stack(), "the equip was told about the wrong piece");
    }

    /** Taking a piece off and putting nothing on is an unequip and nothing else. */
    @Test
    void takingAPieceOffTellsItAndNobodyElse() {
        final Spy.Worn off = new Spy.Worn();
        final ItemStack previous = Wearer.piece(DecorationAnchor.CREST, socket(DecorationAnchor.CREST, off));
        final Wearer wearer = Wearer.zombie();

        DecorationEffectDispatcher.equipmentChanged(
            wearer.entity(), EquipmentSlot.HEAD, previous, ItemStack.EMPTY);

        assertEquals(List.of("unequip"), off.calls, "the piece taken off was not told exactly once");
        assertSame(previous, off.last().stack(), "the unequip was told about a different piece");
    }

    // ---- helpers -----------------------------------------------------------------------------

    /** An entry holding a part that fits {@code anchor} and carries {@code effects}. */
    private static DecorationEntry socket(final DecorationAnchor anchor, final DecorationEffect... effects) {
        return Wearer.entry(Wearer.part(anchor, effects), "minecraft:iron");
    }

    /** Every effect the tick path reaches, in the order it reaches them. */
    private static List<Spy> ticked(final Wearer wearer) {
        final List<Spy> reached = new ArrayList<>();
        DecorationEffectDispatcher.forEachWorn(wearer.entity(), DecorationEffect.Ticking.class,
            (effect, context) -> {
                effect.tick(context);
                reached.add((Spy) effect);
            });
        return reached;
    }
}
