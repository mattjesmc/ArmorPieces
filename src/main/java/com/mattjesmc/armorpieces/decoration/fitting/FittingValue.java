package com.mattjesmc.armorpieces.decoration.fitting;

import net.minecraft.network.chat.Component;

/**
 * What a filled {@link Fitting} holds: the gem in the gemstone, the dye in the inlay, the banner on
 * the cloth.
 *
 * <p>Deliberately the thinnest possible contract. A value is whatever its fitting type says it is -
 * a trim material holder, a dye colour, a banner's base and layers - and only the fitting that owns
 * it ever looks inside. Everything else in the mod (the entry that stores it, the tooltip that lists
 * it, the recipe that writes it) treats it as opaque, which is what lets a mod add a fitting type
 * with a value shape this mod has never heard of: the value's codec comes from the fitting, see
 * {@link Fitting#valueCodec()}, so the entry never has to know how to read it.
 *
 * <p>Implementations are records, and their {@code equals} is what decides whether re-applying the
 * same item to the same fitting is a no-op at the smithing table.
 */
public interface FittingValue {
    /** The value's name for a tooltip - "Emerald", "Red", "Red Banner" - styled with its colour. */
    Component name();
}
