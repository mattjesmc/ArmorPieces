package com.mattjesmc.armorpieces;

import com.mattjesmc.armorpieces.command.StageCommand;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.effect.DecorationEffectDispatcher;
import com.mattjesmc.armorpieces.decoration.effect.DecorationEffects;
import com.mattjesmc.armorpieces.registry.ModCreativeTabs;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.registry.ModItems;
import com.mattjesmc.armorpieces.registry.ModRecipeSerializers;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Decorative armor parts, applied at a smithing table the way trims are, and coloured by the same
 * trim materials.
 *
 * <p>The mod is a SYSTEM first and a set of parts second. Nothing about a specific part - its shape,
 * its texture, its name, where it may be worn, or how it is crafted - lives in Java. A part is:
 *
 * <ul>
 *   <li>{@code data/<ns>/armorpieces/armor_decoration/<name>.json} - the registry entry, naming its
 *       asset, its display name and the sockets it fits;</li>
 *   <li>{@code assets/<ns>/armorpieces/decoration/<name>.json} - its geometry, in a Blockbench-shaped
 *       bones-and-cubes format;</li>
 *   <li>{@code assets/<ns>/textures/entity/decoration/<name>_<material>.png} - one texture per trim
 *       material;</li>
 *   <li>{@code data/<ns>/recipe/<name>.json} - a crafting recipe handing out the smithing template
 *       that carries it (or a loot table entry, or nothing at all if creative is enough).</li>
 * </ul>
 *
 * <p>Note what is NOT in that list: the smithing recipe that applies the part. Ten of those ship, one
 * per socket, and they cover every part that will ever exist - the part rides on the template stack as
 * {@code armorpieces:decoration} rather than being named in the recipe. See {@link
 * com.mattjesmc.armorpieces.item.DecorationTemplateItem}.
 *
 * <p>All four are pack-loadable, so a datapack plus a resource pack can add parts to this mod without
 * touching it - and can override the ones it ships, since both halves resolve through the vanilla
 * pack stack. The one closed piece is the socket list itself ({@link
 * com.mattjesmc.armorpieces.decoration.DecorationAnchor}), because a socket is a place on the body
 * rather than data.
 */
public class ArmorPieces implements ModInitializer {
    public static final String MOD_ID = "armorpieces";
    public static final Logger LOGGER = LoggerFactory.getLogger("Armor Pieces");

    @Override
    public void onInitialize() {
        ArmorPiecesRegistries.register();
        // Effect types must exist before any datapack is read, since a part names one by id.
        DecorationEffects.register();
        ModDataComponents.register();
        ModItems.register();          // templates read the DECORATION component, so components come first
        ModCreativeTabs.register();   // the tab builds stacks of those items
        ModRecipeSerializers.register();
        // A preview of the whole cross product, for judging parts against each other rather than
        // one smithing operation at a time. See StageCommand.
        CommandRegistrationCallback.EVENT.register(
            (dispatcher, buildContext, environment) -> StageCommand.register(dispatcher, buildContext));
        // Subscribes the game events every effect hook is dispatched from. Registered unconditionally
        // even though no part this mod ships has an effect - a datapack or another mod may add one.
        DecorationEffectDispatcher.register();
        LOGGER.info("[Armor Pieces] Decoration system ready.");
    }
}
