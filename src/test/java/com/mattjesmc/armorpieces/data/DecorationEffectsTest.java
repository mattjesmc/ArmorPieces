package com.mattjesmc.armorpieces.data;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.effect.DecorationEffect;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.JsonOps;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.RegistryOps;
import org.junit.jupiter.api.Test;

/**
 * What a part is allowed to DO, held to its own file format.
 *
 * <p>Effects are the one field on a part that is behaviour rather than paint, and the only one a
 * datapack can get wrong in a way that costs a player something. Two of the six entries in
 * {@code armorpieces:decoration_effect_type} are not behaviours at all but GATES over the other
 * four, and the gates carry rules that are enforced when the file is read - a wearer condition may
 * not gate gliding, because gliding is asked on the client where an entity predicate cannot be
 * evaluated, and may not gate an attribute over anything but equipment, because attribute modifiers
 * are reconciled on equipment change and would otherwise go stale. Neither rule has any effect that
 * is visible until it is broken, and a broken one is a part that quietly does nothing (or, worse,
 * does something and never stops).
 *
 * <p>One sample per registered type, and the registry itself is the checklist: a seventh effect
 * added without a sample here fails {@link #everyRegisteredTypeIsCoveredBySample}.
 */
class DecorationEffectsTest {
    /** One legal file per type, written the way a pack author writes it. */
    private static Map<Identifier, String> samples() {
        final Map<Identifier, String> samples = new LinkedHashMap<>();
        samples.put(id("attribute"), """
            {"type": "armorpieces:attribute", "id": "armorpieces:test",
             "attribute": "minecraft:armor", "amount": 2.0, "operation": "add_value"}""");
        samples.put(id("mob_effect"), """
            {"type": "armorpieces:mob_effect", "effect": "minecraft:water_breathing",
             "amplifier": 1, "ambient": true, "show_particles": false, "show_icon": true}""");
        samples.put(id("blink"), """
            {"type": "armorpieces:blink", "chance": 0.25, "radius": 8.0,
             "damage_types": "minecraft:is_projectile", "attempts": 16}""");
        samples.put(id("glide"), """
            {"type": "armorpieces:glide", "sink": 0.03, "wear_interval": 4}""");
        samples.put(id("if_fitting"), """
            {"type": "armorpieces:if_fitting",
             "if": {"fitting": "armorpieces:gemstone", "material": "#armorpieces:gemstones"},
             "then": {"type": "armorpieces:glide", "sink": 0.02}}""");
        samples.put(id("if_wearer"), """
            {"type": "armorpieces:if_wearer",
             "if": {"equipment": {"mainhand": {}}},
             "then": {"type": "armorpieces:attribute", "id": "armorpieces:test",
                      "attribute": "minecraft:armor", "amount": 1.0}}""");
        return samples;
    }

    @Test
    void everyRegisteredTypeIsCoveredBySample() {
        ShippedData.everything();  // registers the types
        final Set<Identifier> registered = ArmorPiecesRegistries.DECORATION_EFFECT_TYPES.keySet();
        assertEquals(registered, samples().keySet(),
            "every effect type needs a sample here, or nothing in this file tests it");
    }

    @Test
    void everyEffectTypeSurvivesItsOwnCodec() {
        samples().forEach((id, json) -> {
            final DecorationEffect effect = parse(json);
            final JsonElement written = DecorationEffect.CODEC.encodeStart(ops(), effect)
                .getOrThrow(message -> new AssertionError(id + " cannot be written: " + message));
            final DecorationEffect back = DecorationEffect.CODEC.parse(ops(), written)
                .getOrThrow(message -> new AssertionError(id + " wrote something unreadable: " + message));
            assertEquals(effect, back, () -> id + " is not what it was after a trip through its own "
                + "codec; it wrote " + written);
        });
    }

    /**
     * A gate implements every hook, so asking it directly what it is would say yes to all of them.
     * {@code reaches} is what the load-time rules and the dispatcher both ask instead, and the
     * answer has to come from what is INSIDE the gate.
     */
    @Test
    void aGateReachesWhatItWrapsAndNothingElse() {
        final DecorationEffect glide = parse(samples().get(id("glide")));
        final DecorationEffect gatedGlide = parse(samples().get(id("if_fitting")));
        final DecorationEffect status = parse(samples().get(id("mob_effect")));

        assertTrue(glide.reaches(DecorationEffect.Gliding.class));
        assertTrue(gatedGlide.reaches(DecorationEffect.Gliding.class),
            "a fitting gate over a glider still glides - that is the point of the gate");
        assertFalse(gatedGlide.reaches(DecorationEffect.Damage.class),
            "a gate that answered yes to every hook would have every hook dispatched into it");
        assertTrue(status.reaches(DecorationEffect.Ticking.class));
        assertFalse(status.reaches(DecorationEffect.Gliding.class));
    }

    /**
     * The first of the two load-time rules, and the reason it exists: gliding is asked on the
     * client too, and an entity predicate cannot be evaluated there. A file that got past this
     * would glide on the server and refuse to take off on the client, which is not a bug anyone
     * would find by looking.
     */
    @Test
    void aWearerConditionMayNotGateAGlider() {
        final DataResult<DecorationEffect> refused = DecorationEffect.CODEC.parse(ops(),
            json("""
                {"type": "armorpieces:if_wearer", "if": {"equipment": {"mainhand": {}}},
                 "then": {"type": "armorpieces:glide", "sink": 0.02}}"""));

        assertTrue(refused.isError(), "a wearer condition over a glider has to be refused at load");
        assertTrue(refused.error().orElseThrow().message().contains("armorpieces:if_fitting"),
            () -> "the refusal has to name the gate an author should use instead; it said: "
                + refused.error().orElseThrow().message());
    }

    /**
     * The second: an attribute modifier is reconciled when equipment changes, so a condition that
     * can turn false without any equipment changing leaves the modifier on for ever.
     */
    @Test
    void aWearerConditionOverAnAttributeMayOnlyTestEquipment() {
        final DataResult<DecorationEffect> refused = DecorationEffect.CODEC.parse(ops(),
            json("""
                {"type": "armorpieces:if_wearer", "if": {"location": {}},
                 "then": {"type": "armorpieces:attribute", "id": "armorpieces:test",
                          "attribute": "minecraft:armor", "amount": 1.0}}"""));
        assertTrue(refused.isError(), "a location test over an attribute effect has to be refused");
        assertTrue(refused.error().orElseThrow().message().contains("location"),
            () -> "the refusal has to name the test that broke the rule; it said: "
                + refused.error().orElseThrow().message());

        // And the same shape with an equipment test is legal - the rule is a narrowing, not a ban.
        assertTrue(DecorationEffect.CODEC.parse(ops(), json(samples().get(id("if_wearer")))).isSuccess());
    }

    /** A gate that can never be true is a file nobody meant to write. */
    @Test
    void aFittingConditionTakesEitherMaterialOrDyeButNotBoth() {
        final DataResult<DecorationEffect> refused = DecorationEffect.CODEC.parse(ops(),
            json("""
                {"type": "armorpieces:if_fitting",
                 "if": {"fitting": "armorpieces:gemstone", "material": "#armorpieces:gemstones",
                        "dye": "red"},
                 "then": {"type": "armorpieces:glide"}}"""));
        assertTrue(refused.isError(), "material and dye at once can never hold");
    }

    /** Every effect can name itself for a tooltip; a type with no language key falls back to its id. */
    @Test
    void everyEffectDescribesItself() {
        final var material = ShippedData.everything()
            .registry(net.minecraft.core.registries.Registries.TRIM_MATERIAL)
            .getAny().orElseThrow();
        final String named = samples().values().stream()
            .map(DecorationEffectsTest::parse)
            .map(effect -> effect.description(material).getString())
            .collect(Collectors.joining(", "));
        assertFalse(named.contains("?"),
            () -> "an effect that cannot name itself shows a question mark in a tooltip: " + named);
    }

    // ---- plumbing --------------------------------------------------------------------------

    private static Identifier id(final String path) {
        return Identifier.fromNamespaceAndPath("armorpieces", path);
    }

    private static RegistryOps<JsonElement> ops() {
        return ShippedData.everything().full().createSerializationContext(JsonOps.INSTANCE);
    }

    private static JsonElement json(final String text) {
        return JsonParser.parseString(text);
    }

    private static DecorationEffect parse(final String text) {
        return DecorationEffect.CODEC.parse(ops(), json(text))
            .getOrThrow(message -> new AssertionError(message + "\n" + text));
    }
}
