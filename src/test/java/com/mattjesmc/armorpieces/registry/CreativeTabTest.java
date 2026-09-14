package com.mattjesmc.armorpieces.registry;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.mattjesmc.armorpieces.GameBootstrap;
import com.mattjesmc.armorpieces.config.PartsSwitch;
import com.mattjesmc.armorpieces.config.ServerConfigFixture;
import com.mattjesmc.armorpieces.data.ShippedData;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.identity.Tolerant;
import com.mojang.serialization.JsonOps;
import com.google.gson.JsonParser;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.flag.FeatureFlags;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * The creative tab, built the way the client builds it, with the server's {@code parts} switch in
 * force: a switched-off member has no template on the tab, and the rest stand.
 *
 * <p>The tab is the one place the switch is read on the CLIENT, through {@link PartsSwitch#shown()}
 * - what the server told it, or this JVM's own file. Here there is no server, so what the fixture
 * puts in force is what "shown" returns, which is the single-player case exactly.
 */
class CreativeTabTest {
    private static ShippedData.Loaded loaded;

    @BeforeAll
    static void world() {
        GameBootstrap.content();
        loaded = ShippedData.mod();
        ShippedData.bakeItemComponents(loaded);
    }

    @AfterEach
    void reset() {
        ServerConfigFixture.reset();
        PartsSwitch.told(null);
    }

    private static List<ItemStack> tab() {
        final CreativeModeTab tab = BuiltInRegistries.CREATIVE_MODE_TAB.getValue(ModCreativeTabs.DECORATIONS);
        tab.buildContents(new CreativeModeTab.ItemDisplayParameters(FeatureFlags.DEFAULT_FLAGS, false, loaded.full()));
        return List.copyOf(tab.getDisplayItems());
    }

    private static Set<String> partsOn(final List<ItemStack> stacks) {
        return stacks.stream()
            .map(stack -> Tolerant.get(stack, ModDataComponents.DECORATION))
            .filter(part -> part != null)
            .map(part -> part.unwrapKey().orElseThrow().identifier().toString())
            .collect(Collectors.toSet());
    }

    private static Set<String> fittingsOn(final List<ItemStack> stacks) {
        return stacks.stream()
            .map(stack -> Tolerant.get(stack, ModDataComponents.FITTING))
            .filter(fitting -> fitting != null)
            .map(fitting -> fitting.unwrapKey().orElseThrow().identifier().toString())
            .collect(Collectors.toSet());
    }

    @Test
    void everyPartHasATemplateOnTheTabWhenNothingIsSwitchedOff() {
        final Set<String> shown = partsOn(tab());
        final Set<String> shipped = loaded.registry(com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries.ARMOR_DECORATION)
            .listElements().map(h -> h.key().identifier().toString()).collect(Collectors.toSet());
        assertEquals(shipped, shown, "the tab does not list exactly the parts the mod ships");
    }

    @Test
    void aSwitchedOffPartHasNoTemplateOnTheTab() {
        ServerConfigFixture.configure("""
            { "parts": { "disabled": ["armorpieces_knightly:visor", "#armorpieces:common"] } }
            """);
        final List<ItemStack> stacks = tab();
        final Set<String> parts = partsOn(stacks);
        assertFalse(parts.contains("armorpieces_knightly:visor"), "the visor is on the tab with its switch off");
        assertTrue(parts.contains("armorpieces_court:circlet"), "and a part nobody switched off went with it");
        assertTrue(fittingsOn(stacks).isEmpty(), "#armorpieces:common is every fitting the mod ships, and one stayed on the tab");
    }

    /** What the server said outranks this JVM's own file, which is the dedicated-server case. */
    @Test
    void theServersWordOutranksTheLocalFile() {
        ServerConfigFixture.configure("{}");
        PartsSwitch.told(PartsSwitch.CODEC.parse(JsonOps.INSTANCE,
            JsonParser.parseString("{ \"mod_parts\": false }")).getOrThrow());
        final List<ItemStack> stacks = tab();
        assertTrue(partsOn(stacks).isEmpty(), "the server said mod_parts: false and the tab listed the mod's parts");
        assertEquals(2, stacks.size(), "the advanced table and the bare fitting template are all that is left");
    }
}
