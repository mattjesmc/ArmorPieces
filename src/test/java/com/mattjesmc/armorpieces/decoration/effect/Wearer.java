package com.mattjesmc.armorpieces.decoration.effect;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.data.ShippedData;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorDecorations;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.DecorationAnchor;
import com.mattjesmc.armorpieces.decoration.DecorationEntry;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import java.lang.reflect.Field;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntityEquipment;
import net.minecraft.world.entity.EntityTypes;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeMap;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.DefaultAttributes;
import net.minecraft.world.entity.monster.zombie.Zombie;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.equipment.trim.TrimMaterial;
import org.jspecify.annotations.Nullable;

/**
 * Somebody wearing decorated armor, with no world for them to stand in.
 *
 * <p>Every effect this mod has runs off one traversal - {@link DecorationEffectDispatcher} walks a
 * living entity's four armor slots, reads the {@code armorpieces:decorations} on each piece and
 * builds a {@link DecorationEffectContext} per socket - and that traversal was, until this fixture,
 * only ever exercised by driving a real server (the gate's tier 2). It does not need one. It reads
 * two things off the entity, its equipment and its attribute map, and neither is a game.
 *
 * <p><b>So the wearer here is built without running a constructor.</b> {@code new Zombie(type, level)}
 * is unreachable in a test JVM - vanilla's {@code Entity} constructor asks the level for an entity id
 * on its first line, and a {@code Level} needs a server or a client. An instance allocated straight
 * from the class has every field null, which is exactly right: this fixture then fills in the three
 * the traversal actually touches, and any fourth one a future change reads is a
 * {@link NullPointerException} in a test rather than a silent pass. The wearer's {@code level()} is
 * null on purpose - that is the honest reading of "no server", and
 * {@link WearerPredicate#test(DecorationEffectContext)} is written to answer false there.
 *
 * <p>What it can therefore be asked: which sockets are visited and in what order, what the context
 * carries, and every attribute modifier the dispatcher adds, scopes, and takes back off. What it
 * cannot: anything an effect does to the WORLD - a mob effect applied to the wearer, a blink's
 * teleport, durability - which stays the gate's tier 2, where there is a world to do it in.
 *
 * <p>The parts are built here rather than found, except where a test is about the mod's own content:
 * a part with one ticking effect and nothing else is a shape no pack ships and every rule is about.
 */
final class Wearer {
    /** Fixed, so an effect that rolls does the same thing on every run. */
    private static final long SEED = 0x9E3779B97F4A7C15L;

    private final LivingEntity entity;
    private final EntityEquipment equipment;

    private Wearer(final LivingEntity entity, final EntityEquipment equipment) {
        this.entity = entity;
        this.equipment = equipment;
    }

    /**
     * A zombie: a real armor-wearing mob whose own attribute supplier has everything the shipped
     * effects name (armor, jump strength, movement speed, attack damage), and not a player, because
     * nothing here is about a player and vanilla's player carries a connection.
     */
    static Wearer zombie() {
        content();
        final LivingEntity wearer = allocate(Zombie.class);
        final EntityEquipment equipment = new EntityEquipment();
        inject(wearer, "equipment", equipment);
        inject(wearer, "attributes", new AttributeMap(DefaultAttributes.getSupplier(EntityTypes.ZOMBIE)));
        inject(wearer, "random", RandomSource.create(SEED));
        return new Wearer(wearer, equipment);
    }

    /** The entity itself, which is what every dispatcher call takes. */
    LivingEntity entity() {
        return this.entity;
    }

    /**
     * Puts a piece on, straight into the equipment.
     *
     * <p>Not {@code setItemSlot}: vanilla's setter fires the equip sound and the equipment-change
     * event, which are the parts of putting armor on that need a world. What the dispatcher reads is
     * the equipment, and that is what this writes.
     */
    Wearer wearing(final EquipmentSlot slot, final ItemStack piece) {
        this.equipment.set(slot, piece);
        return this;
    }

    /** What is in one slot right now - the same object the dispatcher will hand to an effect. */
    ItemStack worn(final EquipmentSlot slot) {
        return this.equipment.get(slot);
    }

    /** The wearer's instance of one attribute, or null if their kind of entity has no such attribute. */
    @Nullable AttributeInstance attribute(final Holder<Attribute> attribute) {
        return this.entity.getAttribute(attribute);
    }

    /** One modifier on one attribute by the id it was applied under, or null if it is not there. */
    @Nullable AttributeModifier modifier(final Holder<Attribute> attribute, final String id) {
        final AttributeInstance instance = this.attribute(attribute);
        return instance == null ? null : instance.getModifier(Identifier.parse(id));
    }

    /** Every id currently modifying one attribute, which is what a reconcile is judged by. */
    Set<Identifier> modifierIds(final Holder<Attribute> attribute) {
        final AttributeInstance instance = this.attribute(attribute);
        return instance == null
            ? Set.of()
            : instance.getModifiers().stream().map(AttributeModifier::id)
                .collect(java.util.stream.Collectors.toCollection(java.util.LinkedHashSet::new));
    }

    /** The attribute's value with everything worn taken into account. */
    double value(final Holder<Attribute> attribute) {
        return this.entity.getAttributeValue(attribute);
    }

    // ---- what they wear ----------------------------------------------------------------------

    /**
     * A piece of iron armor for the slot this socket rides on, with the socket filled.
     *
     * <p>Iron rather than anything else because the base item is never what a test here is about;
     * the material a part is made IN is the entry's, not the armor's.
     */
    static ItemStack piece(final DecorationAnchor anchor, final DecorationEntry entry) {
        return decorated(armorFor(anchor.slot()), Map.of(anchor, entry));
    }

    /** A piece with several sockets filled, for the rules about a piece rather than a socket. */
    static ItemStack piece(final EquipmentSlot slot, final Map<DecorationAnchor, DecorationEntry> entries) {
        return decorated(armorFor(slot), entries);
    }

    /**
     * Any item carrying any decorations, however wrong - the shape a command can write, and the one
     * the dispatcher's own guard is about.
     */
    static ItemStack decorated(final Item item, final Map<DecorationAnchor, DecorationEntry> entries) {
        final ItemStack stack = plain(item);
        stack.set(ModDataComponents.DECORATIONS, new ArmorDecorations(new LinkedHashMap<>(entries)));
        return stack;
    }

    /** An undecorated stack, with the default components a server would have baked onto it. */
    static ItemStack plain(final Item item) {
        content();
        return new ItemStack(item);
    }

    /** The iron piece that goes in a slot. */
    static Item armorFor(final EquipmentSlot slot) {
        return switch (slot) {
            case HEAD -> Items.IRON_HELMET;
            case CHEST -> Items.IRON_CHESTPLATE;
            case LEGS -> Items.IRON_LEGGINGS;
            case FEET -> Items.IRON_BOOTS;
            default -> throw new IllegalArgumentException("no armor goes in " + slot);
        };
    }

    // ---- the content -------------------------------------------------------------------------

    /** A part that fits one socket and carries these effects, with no fittings and no lineage. */
    static Holder<ArmorDecoration> part(final DecorationAnchor anchor, final DecorationEffect... effects) {
        return part(Set.of(anchor), List.of(), effects);
    }

    /** A part in full: the sockets it fits, the fittings it declares, and what it does. */
    static Holder<ArmorDecoration> part(
        final Set<DecorationAnchor> anchors,
        final List<Holder<Fitting>> fittings,
        final DecorationEffect... effects
    ) {
        return Holder.direct(new ArmorDecoration(
            Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "test_part"),
            Component.literal("Test Part"),
            anchors,
            fittings,
            List.of(effects),
            List.of()));
    }

    /** One of the mod's own parts, by path - for the tests that are about shipped content. */
    static Holder<ArmorDecoration> shipped(final String path) {
        return element(ArmorPiecesRegistries.ARMOR_DECORATION, Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, path));
    }

    /** One of the mod's own fittings, by path. */
    static Holder<Fitting> fitting(final String path) {
        return element(ArmorPiecesRegistries.FITTING, Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, path));
    }

    /**
     * A trim material out of the load - the registry a part's own material was resolved against, so
     * a {@link MaterialValue} case and the material an entry wears are comparable at all.
     */
    static Holder<TrimMaterial> material(final String id) {
        return element(Registries.TRIM_MATERIAL, Identifier.parse(id));
    }

    /** This part, in this material, with nothing in its fittings. */
    static DecorationEntry entry(final Holder<ArmorDecoration> part, final String material) {
        return new DecorationEntry(material(material), part);
    }

    private static <T> Holder<T> element(final ResourceKey<? extends Registry<T>> key, final Identifier id) {
        final Registry<T> registry = load().registry(key);
        return registry.get(id)
            .<Holder<T>>map(holder -> holder)
            .orElseThrow(() -> new AssertionError("nothing this repository ships is called " + id));
    }

    /** The mod's own data, loaded the way a server loads it. */
    private static ShippedData.Loaded load() {
        return ShippedData.mod();
    }

    /** The load, plus the baked item components a stack cannot be built without. Binds the tags too. */
    private static void content() {
        ShippedData.bakeItemComponents(load());
    }

    // ---- an entity that was never constructed ------------------------------------------------

    /**
     * An instance of {@code type} with every field null and no constructor run.
     *
     * <p>The classic serialization trick, done through {@code sun.misc.Unsafe} reflectively so that
     * nothing here compiles against it. It is doing what a save file does when it reads an entity
     * back: allocate first, fill in after.
     */
    private static <T> T allocate(final Class<T> type) {
        try {
            final Class<?> unsafeClass = Class.forName("sun.misc.Unsafe");
            final Field held = unsafeClass.getDeclaredField("theUnsafe");
            held.setAccessible(true);
            final Object unsafe = held.get(null);
            return type.cast(unsafeClass.getMethod("allocateInstance", Class.class).invoke(unsafe, type));
        } catch (final ReflectiveOperationException failed) {
            throw new AssertionError("a " + type.getSimpleName() + " could not be allocated", failed);
        }
    }

    /** Sets one field, wherever in the hierarchy it is declared. Final instance fields included. */
    private static void inject(final Object target, final String name, final Object value) {
        for (Class<?> type = target.getClass(); type != null; type = type.getSuperclass()) {
            try {
                final Field field = type.getDeclaredField(name);
                field.setAccessible(true);
                field.set(target, value);
                return;
            } catch (final NoSuchFieldException notHere) {
                // Declared further up, or nowhere.
            } catch (final IllegalAccessException refused) {
                throw new AssertionError("could not set " + name, refused);
            }
        }
        throw new AssertionError(
            "no field called " + name + " on " + target.getClass().getName()
                + " - vanilla has renamed what this fixture fills in");
    }
}
