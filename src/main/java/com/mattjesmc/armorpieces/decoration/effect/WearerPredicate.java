package com.mattjesmc.armorpieces.decoration.effect;

import com.mojang.datafixers.util.Pair;
import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.Decoder;
import com.mojang.serialization.DynamicOps;
import com.mojang.serialization.Encoder;
import java.util.LinkedHashSet;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import net.minecraft.advancements.predicates.entity.EntityPredicate;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;

/**
 * A question about the WEARER, asked with vanilla's own entity predicate.
 *
 * <pre>{@code
 * { "equipment": { "mainhand": { "items": "minecraft:air" } } }
 * { "flags": { "is_swimming": true } }
 * { "location": { "dimension": "minecraft:the_nether" } }
 * }</pre>
 *
 * <p>The one condition effects had before this asked about the part - {@code if_fitting}, the gem in
 * the circlet. Nothing could ask about the person carrying it: what they hold, what else they wear,
 * where they are, what they are doing. Rather than invent a condition language, this is
 * {@link EntityPredicate} exactly as it appears in an advancement or a loot table, so an author
 * already knows the syntax and a field vanilla adds next version is available the day it lands.
 *
 * <h2>Why the tests are counted</h2>
 *
 * <p>{@link #tests} is the set of sub-predicate names the file actually wrote - {@code equipment},
 * {@code flags}, {@code location} and the rest. It is captured while decoding because the predicate
 * itself does not say afterwards what it was built from, and
 * {@link com.mattjesmc.armorpieces.decoration.effect.builtin.WearerConditionEffect} has to know: a
 * condition legal on a ticking effect can be silently wrong on an attribute one, and the difference
 * is exactly which of these names appear. It is also what the refusal message quotes back, which is
 * the difference between "this condition is not allowed here" and "location is not allowed here".
 *
 * @param predicate vanilla's predicate, evaluated as vanilla evaluates it.
 * @param tests     the sub-predicate names present, in the order the file wrote them.
 */
public record WearerPredicate(EntityPredicate predicate, Set<String> tests) {
    /**
     * The one test that is a pure function of the wearer's EQUIPMENT, and so the only one legal on
     * {@link DecorationEffect.Attributes} - see the dispatcher, which re-reconciles the armor slots
     * when a hand changes precisely so that this stays true.
     *
     * <p>Held as a full id because that is what the names are: a file writes {@code equipment} and
     * vanilla's own encoder writes {@code minecraft:equipment}, and a part that survived being
     * written but not being read back would be the worst of both. Which is not hypothetical - it
     * cost a client, once: a part in a WORLD datapack travels to the client through the registry
     * sync, which re-encodes it, so the two spellings met at the far end and the second one was
     * refused.
     */
    public static final String EQUIPMENT = "minecraft:equipment";

    /**
     * Vanilla's predicate, plus a note of which fields it was written with.
     *
     * <p>Spelled out as an {@link Encoder} and a {@link Decoder} rather than derived from
     * {@code EntityPredicate.CODEC} with {@code xmap}, because the extra thing being carried - the
     * field names - is not in the decoded value and cannot be recovered from it. Anonymous classes
     * rather than lambdas: both methods are generic in the ops type, which a lambda cannot be.
     */
    public static final Codec<WearerPredicate> CODEC = Codec.of(
        new Encoder<WearerPredicate>() {
            @Override
            public <T> DataResult<T> encode(final WearerPredicate input, final DynamicOps<T> ops, final T prefix) {
                return EntityPredicate.CODEC.encode(input.predicate(), ops, prefix);
            }
        },
        new Decoder<WearerPredicate>() {
            @Override
            public <T> DataResult<Pair<WearerPredicate, T>> decode(final DynamicOps<T> ops, final T input) {
                return EntityPredicate.CODEC.decode(ops, input).flatMap(
                    decoded -> namesOf(ops, input).map(
                        names -> decoded.mapFirst(predicate -> new WearerPredicate(predicate, names))));
            }
        },
        "WearerPredicate");

    public WearerPredicate {
        tests = Set.copyOf(tests);
    }

    /** The keys of the object the predicate was written as, which are its sub-predicates' names. */
    private static <T> DataResult<Set<String>> namesOf(final DynamicOps<T> ops, final T input) {
        return ops.getMap(input).map(map -> map.entries()
            .map(entry -> ops.getStringValue(entry.getFirst()).result())
            .filter(Optional::isPresent)
            .map(name -> full(name.get()))
            .collect(Collectors.toCollection(LinkedHashSet::new)));
    }

    /** A name as a full id, since a file may leave the {@code minecraft} namespace off and an encoder may not. */
    private static String full(final String name) {
        return name.indexOf(':') < 0 ? "minecraft:" + name : name;
    }

    /** Whether every test this asks is about the wearer's equipment and nothing else. */
    public boolean isEquipmentOnly() {
        return this.tests.stream().allMatch(EQUIPMENT::equals);
    }

    /**
     * The tests that are not about equipment, for a message that says which ones were the problem.
     *
     * <p>Printed the short way a file would have written them - a reader who typed {@code location}
     * should be told about {@code location}.
     */
    public Set<String> beyondEquipment() {
        return this.tests.stream()
            .filter(test -> !EQUIPMENT.equals(test))
            .map(test -> test.startsWith("minecraft:") ? test.substring("minecraft:".length()) : test)
            .collect(Collectors.toCollection(LinkedHashSet::new));
    }

    /**
     * Whether the wearer answers the question right now.
     *
     * <p>False off the server: vanilla's predicate needs a {@link ServerLevel} to evaluate, which is
     * why an effect gated on one of these may not reach
     * {@link DecorationEffect.Gliding} - the only hook the client also asks - and is refused at load
     * if it does.
     */
    public boolean test(final DecorationEffectContext context) {
        final ServerLevel level = context.serverLevel();
        if (level == null) {
            return false;
        }
        final LivingEntity wearer = context.wearer();
        return this.predicate.matches(level, wearer.position(), wearer);
    }
}
