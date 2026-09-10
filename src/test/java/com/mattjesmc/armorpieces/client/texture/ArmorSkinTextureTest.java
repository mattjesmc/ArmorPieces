package com.mattjesmc.armorpieces.client.texture;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.mattjesmc.armorpieces.GameBootstrap;
import com.mattjesmc.armorpieces.client.texture.ArmorSkinTextureManager.Lighting;
import com.mattjesmc.armorpieces.client.texture.ArmorSkinTextureManager.Material;
import com.mattjesmc.armorpieces.data.ShippedData;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.skin.ArmorSkin;
import com.mattjesmc.armorpieces.skin.SkinBake;
import com.mojang.blaze3d.platform.NativeImage;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import javax.imageio.ImageIO;
import net.minecraft.core.Holder;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.packs.PackLocationInfo;
import net.minecraft.server.packs.PackResources;
import net.minecraft.server.packs.PackType;
import net.minecraft.server.packs.PathPackResources;
import net.minecraft.server.packs.repository.PackSource;
import net.minecraft.server.packs.resources.MultiPackResourceManager;
import net.minecraft.server.packs.resources.ResourceManager;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * The last of the three texture managers, and the one whose promise is the largest: that nothing
 * anywhere names a material.
 *
 * <p>A skin ships two greyscale PNGs and no per-material art at all, and an armor material added by
 * another mod is skinned the moment it is installed - because the only thing wanted from that mod is
 * the equipment texture it must already ship to be visible on a body. Everything that promise rests
 * on lives in this class rather than in {@link SkinBake}, which only knows how to colour pixels once
 * somebody has told it which pixels and through which ramp:
 *
 * <ul>
 *   <li><b>which material a texture belongs to</b> is its own FILE NAME, under vanilla's equipment
 *       directory and nowhere else. That one line is the whole of the compatibility story, and it
 *       has never been asked a question;</li>
 *   <li><b>where the colour comes from</b> is both of the material's sheets measured together, and
 *       the light from each of them separately - one ramp per material or the leggings drift away
 *       from the body they are worn under, but the light on a leg is not the light on a chest;</li>
 *   <li><b>what happens when there is nothing to measure</b> - a material whose texture is empty
 *       cannot be skinned, and says so once rather than every frame;</li>
 *   <li><b>where a bake is filed</b>, which carries the material's whole id, namespace and all, so
 *       two mods that each add a "steel" do not wear each other's colour.</li>
 * </ul>
 *
 * <p>{@code SkinBakeTest} holds the arithmetic to {@code tools/bake_skin.py} texel for texel, and
 * tier 3 photographs one skin on all eight vanilla materials. What is here is the part in between:
 * how the game gets from an armor texture to the ramp those two things assume it already has.
 */
class ArmorSkinTextureTest {
    /** Where vanilla keeps the armor textures a ramp is measured from - restated, not read off. */
    private static final String EQUIPMENT = "textures/entity/equipment/";

    @BeforeAll
    static void world() {
        GameBootstrap.content();
    }

    // ---- which material a texture belongs to ---------------------------------------------------

    /**
     * The material is the equipment texture's own file name, which is what vanilla and every mod
     * alike key their armor art by. This is the line that makes another mod's material work with no
     * art and no registration from anybody.
     */
    @Test
    void theMaterialIsTheEquipmentTexturesOwnFileName() {
        assertEquals("iron", ArmorSkinTextureManager.materialName(
            Identifier.parse("minecraft:" + EQUIPMENT + "humanoid/iron.png")));
        assertEquals("gold", ArmorSkinTextureManager.materialName(
            Identifier.parse("minecraft:" + EQUIPMENT + "humanoid_leggings/gold.png")));
        assertEquals("steel", ArmorSkinTextureManager.materialName(
            Identifier.parse("a_mod:" + EQUIPMENT + "humanoid/steel.png")),
            "another mod's material is named exactly the way vanilla's is");
        assertEquals("turtle_scute", ArmorSkinTextureManager.materialName(
            Identifier.parse("minecraft:" + EQUIPMENT + "humanoid/turtle_scute.png")));
    }

    /** A texture that is not an equipment layer names no material, and no skin is baked for it. */
    @Test
    void aTextureThatIsNotAnEquipmentLayerNamesNoMaterial() {
        assertNull(ArmorSkinTextureManager.materialName(
            Identifier.parse("armorpieces:textures/entity/decoration/sash.png")),
            "a decoration's own sheet is not armor");
        assertNull(ArmorSkinTextureManager.materialName(
            Identifier.parse("minecraft:textures/block/stone.png")), "nor is a block");
        assertNull(ArmorSkinTextureManager.materialName(
            Identifier.parse("minecraft:" + EQUIPMENT + "humanoid/iron.mcmeta")),
            "nor is a file beside the texture");
    }

    // ---- where the colour comes from -------------------------------------------------------------

    /**
     * Both of a material's sheets are measured TOGETHER for the ramp and separately for the light.
     *
     * <p>The falsifier for the first half is that the leggings genuinely move the answer: a ramp
     * taken off the body sheet alone is a different table, and a piece of armor whose legs are
     * darker than its chest would then be worn as two different metals.
     */
    @Test
    void bothSheetsAreMeasuredTogetherForTheRampAndSeparatelyForTheLight(@TempDir final Path root)
        throws IOException {
        final int[] body = shades(0x30, 0x90);
        final int[] legs = shades(0xA0, 0xF0);
        equipment(root, "a_mod", "humanoid", "together", body);
        equipment(root, "a_mod", "humanoid_leggings", "together", legs);

        final Material material = ArmorSkinTextureManager.instance()
            .material(manager(root), Identifier.parse("a_mod:" + EQUIPMENT + "humanoid/together.png"));
        assertNotNull(material, "a material with two readable sheets has a ramp");
        assertEquals(256, material.table().length, "the table is one entry per value");

        assertArrayEquals(SkinBake.table(SkinBake.ramp(List.of(body, legs))), material.table(),
            "the ramp is measured off both sheets at once");
        assertFalse(java.util.Arrays.equals(SkinBake.table(SkinBake.ramp(List.of(body))), material.table()),
            "and the leggings really do move it - otherwise this proves nothing");

        assertEquals(Set.of("humanoid", "humanoid_leggings"), material.lighting().keySet(),
            "one lighting per sheet");
        assertArrayEquals(SkinBake.lightmap(body), material.lighting().get("humanoid").map(),
            "the body's light is the body sheet's own");
        assertArrayEquals(SkinBake.lightmap(legs), material.lighting().get("humanoid_leggings").map(),
            "and the leggings' is theirs");
    }

    /**
     * A material with only one sheet is measured from that one. The turtle scute is a helmet and
     * nothing else, and it is not a broken material.
     */
    @Test
    void aMaterialWithOnlyOneSheetIsMeasuredFromThatOne(@TempDir final Path root) throws IOException {
        equipment(root, "a_mod", "humanoid", "helmet_only", shades(0x20, 0xE0));

        final Material material = ArmorSkinTextureManager.instance()
            .material(manager(root), Identifier.parse("a_mod:" + EQUIPMENT + "humanoid/helmet_only.png"));
        assertNotNull(material, "one sheet is enough to take a colour from");
        assertEquals(Set.of("humanoid"), material.lighting().keySet(),
            "and the sheet it does not have has no light");
    }

    /**
     * An equipment texture with nothing in it has no colour to lend, so the skin is not drawn and
     * vanilla's own texture stands - rather than the piece being drawn in whatever a ramp built from
     * no pixels would have been.
     */
    @Test
    void anEquipmentTextureWithNothingInItCannotBeSkinned(@TempDir final Path root) throws IOException {
        equipment(root, "a_mod", "humanoid", "invisible", new int[64 * 32]);
        assertNull(ArmorSkinTextureManager.instance()
            .material(manager(root), Identifier.parse("a_mod:" + EQUIPMENT + "humanoid/invisible.png")),
            "a wholly transparent sheet is no material");
    }

    /** A texture that names no material is not looked for on disk at all. */
    @Test
    void aTextureThatNamesNoMaterialIsNotLookedFor(@TempDir final Path root) throws IOException {
        Files.createDirectories(root.resolve("assets"));
        assertNull(ArmorSkinTextureManager.instance()
            .material(manager(root), Identifier.parse("minecraft:textures/block/stone.png")));
    }

    /**
     * A material is measured once and remembered, keyed by the material rather than by the texture
     * path - so a body and a pair of leggings of one material do not measure the same thing twice.
     */
    @Test
    void aMaterialIsMeasuredOnceForBothOfItsSheets(@TempDir final Path root) throws IOException {
        equipment(root, "a_mod", "humanoid", "measured_once", shades(0x20, 0xE0));
        equipment(root, "a_mod", "humanoid_leggings", "measured_once", shades(0x40, 0xC0));
        final ResourceManager manager = manager(root);
        final ArmorSkinTextureManager textures = ArmorSkinTextureManager.instance();

        final Material fromBody = textures.material(
            manager, Identifier.parse("a_mod:" + EQUIPMENT + "humanoid/measured_once.png"));
        final Material fromLegs = textures.material(
            manager, Identifier.parse("a_mod:" + EQUIPMENT + "humanoid_leggings/measured_once.png"));
        assertNotNull(fromBody);
        assertSame(fromBody, fromLegs, "the ramp is the material's, not the sheet's");
    }

    // ---- the light and the master ------------------------------------------------------------------

    /**
     * A pack whose skin sheet is not the size of the armor texture it is worn over gets the pattern
     * without the light, rather than light applied to the wrong texels. The colour is per-texel and
     * does not care about size, so the skin still works.
     */
    @Test
    void aSkinSheetTheWrongSizeForTheArmorGetsThePatternWithoutTheLight() {
        final int[] armor = shades(0x20, 0xE0);
        final Material material = new Material(
            SkinBake.table(SkinBake.ramp(List.of(armor))),
            Map.of("humanoid", new Lighting(SkinBake.lightmap(armor), 64, 32)));

        // Half the height, so its texels index into rows of the armor's lightmap that DO carry
        // light: over a transparent corner the guard could be dropped and nothing would show.
        try (NativeImage sized = master(64, 32); NativeImage odd = master(64, 16)) {
            final byte[] light = material.lighting().get("humanoid").map();
            boolean lightsTheOddOne = false;
            for (int i = 0; i < odd.getWidth() * odd.getHeight(); i++) {
                lightsTheOddOne |= light[i] != 0;
            }
            assertTrue(lightsTheOddOne,
                "the wrongly sized sheet has to reach lit texels, or this proves nothing");

            final int[] lit = ArmorSkinTextureManager.colour(sized, material, "humanoid");
            assertArrayEquals(SkinBake.bake(pixels(sized), material.table(), light), lit,
                "a sheet the right size is lit");
            assertFalse(java.util.Arrays.equals(
                SkinBake.bake(pixels(sized), material.table(), null), lit),
                "and the light really does change it - otherwise this proves nothing");

            assertArrayEquals(SkinBake.bake(pixels(odd), material.table(), null),
                ArmorSkinTextureManager.colour(odd, material, "humanoid"),
                "a sheet of another size keeps its pattern and loses the light");
        }
    }

    /** A sheet the material has no lighting for is coloured without light, not refused. */
    @Test
    void aSheetWithNoLightingOfItsOwnIsColouredWithoutLight() {
        final int[] armor = shades(0x20, 0xE0);
        final Material material = new Material(
            SkinBake.table(SkinBake.ramp(List.of(armor))),
            Map.of("humanoid", new Lighting(SkinBake.lightmap(armor), 64, 32)));
        try (NativeImage sheet = master(64, 32)) {
            assertArrayEquals(SkinBake.bake(pixels(sheet), material.table(), null),
                ArmorSkinTextureManager.colour(sheet, material, "humanoid_leggings"),
                "the leggings of a helmet-only material still take its colour");
        }
    }

    // ---- the resolution order -------------------------------------------------------------------------

    /**
     * A pack that genuinely needs bespoke art on one material can ship it, and it is used AS IT IS -
     * ahead of the bake, which is the whole point of there being an override at all.
     */
    @Test
    void aPacksOwnArtForOneMaterialBeatsTheBake(@TempDir final Path root) throws IOException {
        final ArmorSkin skin = skins().getFirst().value();
        sheet(root, skin.sheet("humanoid", ""));
        sheet(root, skin.sheet("humanoid", "_iron"));

        final ArmorSkinTextureManager textures = ArmorSkinTextureManager.instance();
        textures.onResourceManagerReload(manager(root));
        assertEquals(skin.sheet("humanoid", "_iron"), textures.resolve(skin, "humanoid", IRON),
            "the hand-drawn sheet for this material, not a bake of the master");
        assertNotEquals(skin.sheet("humanoid", "_gold"), textures.resolve(skin, "humanoid", IRON),
            "and only for the material it was drawn for");
    }

    /**
     * A skin with no sheet for a layer is not an error: it is a skin that has nothing to say about
     * that layer, and vanilla's own texture is drawn.
     */
    @Test
    void aSkinWithNothingToSayAboutALayerLeavesVanillasTextureAlone(@TempDir final Path root)
        throws IOException {
        final ArmorSkin skin = skins().getFirst().value();
        sheet(root, skin.sheet("humanoid", ""));

        final ArmorSkinTextureManager textures = ArmorSkinTextureManager.instance();
        textures.onResourceManagerReload(manager(root));
        assertNull(textures.resolve(skin, "humanoid_leggings", IRON),
            "a skin with no leggings sheet draws no leggings");
    }

    /**
     * A skin is drawn on the humanoid grid and has nothing to say about any other, so a baby's
     * sheet, a wolf's or a horse's is refused before anything is read.
     */
    @Test
    void aSheetThatIsNotTheHumanoidGridIsNotASkinsBusiness(@TempDir final Path root) throws IOException {
        final ArmorSkin skin = skins().getFirst().value();
        sheet(root, skin.sheet("wolf_body", ""));

        final ArmorSkinTextureManager textures = ArmorSkinTextureManager.instance();
        textures.onResourceManagerReload(manager(root));
        assertNull(textures.resolve(skin, "wolf_body", IRON),
            "even with a sheet of that name sitting right there");
    }

    // ---- where a bake is filed -----------------------------------------------------------------------

    /**
     * The baked id is the cache key, so two bakes sharing one would put one material's colour on
     * another's armor - and it is also a resource location, which refuses most punctuation. The
     * material's whole id is in the path, namespace and all, which is the case the class note
     * promises: two mods that each add a "steel" do not collide.
     */
    @Test
    void everyBakeIsFiledSomewhereLegalAndSomewhereOfItsOwn() {
        final List<Identifier> materials = List.of(
            Identifier.parse("minecraft:" + EQUIPMENT + "humanoid/iron.png"),
            Identifier.parse("minecraft:" + EQUIPMENT + "humanoid/steel.png"),
            Identifier.parse("a_mod:" + EQUIPMENT + "humanoid/steel.png"),
            Identifier.parse("b_mod:" + EQUIPMENT + "humanoid/steel.png"));

        final Set<Identifier> seen = new HashSet<>();
        final List<String> collisions = new ArrayList<>();
        for (final Holder.Reference<ArmorSkin> skin : skins()) {
            for (final String sheet : List.of("humanoid", "humanoid_leggings")) {
                for (final Identifier material : materials) {
                    // Illegal punctuation throws out of here rather than asserting.
                    final Identifier baked =
                        ArmorSkinTextureManager.bakedId(skin.value(), sheet, material);
                    if (!seen.add(baked)) {
                        collisions.add(baked + " is claimed twice");
                    }
                }
            }
        }
        assertTrue(collisions.isEmpty(), () -> String.join("\n  ", collisions));
        assertTrue(seen.size() >= skins().size() * 2 * materials.size(), "every combination is its own");

        final ArmorSkin skin = skins().getFirst().value();
        final Identifier iron = materials.getFirst();
        assertEquals(
            ArmorSkinTextureManager.bakedId(skin, "humanoid", iron),
            ArmorSkinTextureManager.bakedId(skin, "humanoid", iron),
            "the same bake is filed in the same place, or nothing is ever cached");
    }

    // ---- the fixture ------------------------------------------------------------------------------

    /** The texture a piece of iron armor would otherwise draw with. */
    private static final Identifier IRON =
        Identifier.parse("minecraft:" + EQUIPMENT + "humanoid/iron.png");

    /** One skin sheet, painted with anything at all - these tests only ask which one is chosen. */
    private static void sheet(final Path root, final Identifier id) throws IOException {
        final Path file = root.resolve("assets/" + id.getNamespace() + "/" + id.getPath());
        Files.createDirectories(file.getParent());
        ImageIO.write(new BufferedImage(64, 32, BufferedImage.TYPE_INT_ARGB), "png", file.toFile());
    }

    private static List<Holder.Reference<ArmorSkin>> skins() {
        return ShippedData.mod().registry(ArmorPiecesRegistries.ARMOR_SKIN).listElements().toList();
    }

    /** A 64x32 sheet whose opaque texels sweep a range of greys, so a ramp has something to read. */
    private static int[] shades(final int darkest, final int lightest) {
        final int[] pixels = new int[64 * 32];
        for (int y = 8; y < 24; y++) {
            for (int x = 8; x < 56; x++) {
                final int grey = darkest + (lightest - darkest) * (x - 8) / 47;
                pixels[y * 64 + x] = 0xFF000000 | (grey << 16) | (grey << 8) | grey;
            }
        }
        return pixels;
    }

    /** A skin's greyscale master: a pattern with no relation to the armor it is worn over. */
    private static NativeImage master(final int width, final int height) {
        final NativeImage image = new NativeImage(width, height, false);
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                final int grey = (x * 5 + y * 11) % 256;
                image.setPixel(x, y, 0xFF000000 | (grey << 16) | (grey << 8) | grey);
            }
        }
        return image;
    }

    private static int[] pixels(final NativeImage image) {
        final int[] out = new int[image.getWidth() * image.getHeight()];
        for (int y = 0; y < image.getHeight(); y++) {
            for (int x = 0; x < image.getWidth(); x++) {
                out[y * image.getWidth() + x] = image.getPixel(x, y);
            }
        }
        return out;
    }

    /** One material's equipment texture, where the game would look for it. */
    private static void equipment(
        final Path root, final String namespace, final String sheet, final String material,
        final int[] pixels
    ) throws IOException {
        final Path file = root.resolve(
            "assets/" + namespace + "/" + EQUIPMENT + sheet + "/" + material + ".png");
        Files.createDirectories(file.getParent());
        final BufferedImage image = new BufferedImage(64, 32, BufferedImage.TYPE_INT_ARGB);
        for (int y = 0; y < 32; y++) {
            for (int x = 0; x < 64; x++) {
                image.setRGB(x, y, pixels[y * 64 + x]);
            }
        }
        ImageIO.write(image, "png", file.toFile());
    }

    private static ResourceManager manager(final Path root) {
        return new MultiPackResourceManager(PackType.CLIENT_RESOURCES, List.of(pack(root)));
    }

    private static PackResources pack(final Path root) {
        final String name = root.getFileName().toString();
        return new PathPackResources(
            new PackLocationInfo(name, Component.literal(name), PackSource.BUILT_IN, Optional.empty()),
            root);
    }
}
