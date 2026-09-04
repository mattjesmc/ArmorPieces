package com.mattjesmc.armorpieces.client.texture;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.skin.ArmorSkin;
import com.mattjesmc.armorpieces.skin.SkinBake;
import com.mojang.blaze3d.platform.NativeImage;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.fabricmc.fabric.api.resource.SimpleSynchronousResourceReloadListener;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.texture.DynamicTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.server.packs.resources.Resource;
import net.minecraft.server.packs.resources.ResourceManager;
import org.jspecify.annotations.Nullable;

/**
 * Resolves the texture a piece of skinned armor draws with: the skin's greyscale master, coloured
 * for that armor's own material, baked on first use and cached until the next resource reload.
 *
 * <p>The counterpart to {@link DecorationTextureManager}, and deliberately its twin - one greyscale
 * master, recoloured per material at load, with a hand-authored override still winning if a pack
 * ships one. What differs is where the colour comes from. A part inherits a TRIM MATERIAL's palette,
 * which is a file vanilla ships; a skin has no palette to read, because the thing it must look like
 * is the armor it is painted onto. So the ramp is derived from that armor's own vanilla texture -
 * see {@link SkinBake} for the arithmetic, which is held to
 * {@code docs/plans/skin-bake-reference.json} along with the tool the skins were drawn against.
 *
 * <p>What it buys is worth restating: nothing anywhere names a material. The mod ships two PNGs per
 * skin and no per-material art at all, and an armor material added by another mod is skinned the
 * moment it is installed, because the only thing wanted from it is the equipment texture it must
 * already ship to be visible on a body.
 *
 * <p>Resolution order for one skin on one of an armor's layers:
 *
 * <ol>
 *   <li>{@code <skin>/<sheet>_<material>.png}, if a pack supplies one - a skin that genuinely needs
 *       bespoke art on one material can have it, and it is used as it is;</li>
 *   <li>{@code <skin>/<sheet>.png} baked through that material's ramp and lighting - the normal
 *       path;</li>
 *   <li>nothing, and the caller draws vanilla's own texture. A skin with no sheet for a layer is not
 *       an error: it is a skin that has nothing to say about that layer.</li>
 * </ol>
 *
 * <p>Which LAYER a skin replaces is decided by the caller - see
 * {@code com.mattjesmc.armorpieces.client.mixin.EquipmentLayerRendererMixin}. This class only ever
 * answers "what would this skin look like in place of that texture".
 */
@Environment(EnvType.CLIENT)
public final class ArmorSkinTextureManager implements SimpleSynchronousResourceReloadListener {
    private static final Identifier ID =
        Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "armor_skin_textures");

    /** Where a skin's own sheets live, and the only directory this class indexes. */
    private static final String DIRECTORY = "textures/entity/skin";
    /** Where vanilla keeps the armor textures a ramp is measured from. */
    private static final String EQUIPMENT_DIRECTORY = "textures/entity/equipment/";
    /** The two sheets a skin is drawn as, and the two layer types it therefore knows about. */
    private static final String BODY_SHEET = "humanoid";
    private static final String LEGGINGS_SHEET = "humanoid_leggings";

    private static final ArmorSkinTextureManager INSTANCE = new ArmorSkinTextureManager();

    /** Every skin sheet any pack supplies. Membership only - the bytes are read on demand. */
    private volatile Set<Identifier> available = Set.of();

    /**
     * One material's ramp and lighting, measured once and shared by every skin worn on it - and by
     * both of its sheets, since the ramp is the material's and not the sheet's. Keyed by the
     * material's own id ({@code minecraft:iron}) rather than by a texture path, so the body and the
     * leggings do not measure the same thing twice.
     */
    private final Map<Identifier, Optional<Material>> materials = new HashMap<>();
    /** Baked texture id to the id actually rendered with; also negative-caches a failed bake. */
    private final Map<Identifier, Optional<Identifier>> resolved = new HashMap<>();
    /** What we handed to the texture manager, so a reload can hand it back. */
    private final List<Identifier> registered = new ArrayList<>();

    private ArmorSkinTextureManager() {}

    public static ArmorSkinTextureManager instance() {
        return INSTANCE;
    }

    /**
     * One material as the bake needs it: the 256-entry colour table taken from its own texture, and
     * vanilla's lighting for each of its two sheets.
     *
     * <p>Both sheets are measured TOGETHER for the table and separately for the lighting, which is
     * the split the arithmetic asks for: one ramp per material or the leggings would drift away from
     * the body they are worn under, but the light on a leg is not the light on a chest.
     */
    private record Material(int[] table, Map<String, Lighting> lighting) {}

    /** Vanilla's lighting for one sheet, with the size it was measured at. */
    private record Lighting(byte[] map, int width, int height) {}

    /**
     * The texture to draw {@code skin} with in place of {@code vanillaTexture}, or null to leave
     * vanilla's own texture alone.
     *
     * <p>Called from the render layer, so everything expensive is cached: a bake happens once per
     * skin per material per sheet per resource reload, and every later frame is a map lookup.
     *
     * @param sheet          {@code humanoid} or {@code humanoid_leggings} - the layer type's own
     *                       name, which is also the name of the master sheet to use.
     * @param vanillaTexture the texture the armor would otherwise draw with, which is both what the
     *                       ramp is measured from and what names the material.
     */
    public @Nullable Identifier resolve(final ArmorSkin skin, final String sheet, final Identifier vanillaTexture) {
        if (!BODY_SHEET.equals(sheet) && !LEGGINGS_SHEET.equals(sheet)) {
            // A baby's sheet, a wolf's, a horse's. A skin is drawn on the humanoid grid and has
            // nothing to say about any other, so vanilla's texture stands.
            return null;
        }
        final String material = materialName(vanillaTexture);
        if (material == null) {
            return null;
        }
        final Identifier override = skin.sheet(sheet, "_" + material);
        if (this.available.contains(override)) {
            return override;
        }
        if (!this.available.contains(skin.sheet(sheet, ""))) {
            return null;
        }
        final Identifier baked = bakedId(skin, sheet, vanillaTexture);
        final Optional<Identifier> cached = this.resolved.get(baked);
        if (cached != null) {
            return cached.orElse(null);
        }
        final Optional<Identifier> result =
            bake(skin, sheet, vanillaTexture, baked) ? Optional.of(baked) : Optional.empty();
        this.resolved.put(baked, result);
        return result.orElse(null);
    }

    @Override
    public void onResourceManagerReload(final ResourceManager manager) {
        releaseBaked();
        this.materials.clear();
        this.available = Set.copyOf(
            manager.listResources(DIRECTORY, path -> path.getPath().endsWith(".png")).keySet());
    }

    @Override
    public Identifier getFabricId() {
        return ID;
    }

    // ---- baking ---------------------------------------------------------------------------------

    private boolean bake(
        final ArmorSkin skin,
        final String sheet,
        final Identifier vanillaTexture,
        final Identifier target
    ) {
        final ResourceManager manager = Minecraft.getInstance().getResourceManager();
        NativeImage master = null;
        try {
            master = readImage(manager, skin.sheet(sheet, ""));
            if (master == null) {
                return false;
            }
            final Material material = material(manager, vanillaTexture);
            if (material == null) {
                return false;
            }
            final int width = master.getWidth();
            final int height = master.getHeight();
            final Lighting lighting = material.lighting().get(sheet);
            // A pack whose skin sheet is not the size of the armor texture it is worn over gets the
            // pattern without the light rather than light applied to the wrong texels. The colour is
            // per-texel and does not care about size, so the skin still works.
            final byte[] light = lighting != null && lighting.width() == width && lighting.height() == height
                ? lighting.map()
                : null;
            final int[] baked = SkinBake.bake(pixels(master), material.table(), light);

            final NativeImage out = new NativeImage(width, height, false);
            for (int y = 0; y < height; y++) {
                for (int x = 0; x < width; x++) {
                    out.setPixel(x, y, baked[y * width + x]);
                }
            }
            final Minecraft client = Minecraft.getInstance();
            client.getTextureManager().release(target);
            client.getTextureManager().register(target, new DynamicTexture(target::toString, out));
            this.registered.add(target);
            return true;
        } catch (final RuntimeException e) {
            ArmorPieces.LOGGER.error(
                "[Armor Pieces] Could not colour skin {} for {}", skin.assetId(), vanillaTexture, e);
            return false;
        } finally {
            close(master);
        }
    }

    /**
     * One material's ramp and lighting, measured from its own vanilla textures.
     *
     * <p>Both sheets are read here whichever one is being baked, because the ramp is the material's
     * and not the sheet's. A material with only one sheet - the turtle scute is a helmet and nothing
     * else - is measured from that one.
     */
    private @Nullable Material material(final ResourceManager manager, final Identifier vanillaTexture) {
        final String name = materialName(vanillaTexture);
        if (name == null) {
            return null;
        }
        return this.materials
            .computeIfAbsent(vanillaTexture.withPath(ignored -> name),
                id -> Optional.ofNullable(loadMaterial(manager, id)))
            .orElse(null);
    }

    /** @param id the material's own id - {@code minecraft:iron} - which names both of its sheets. */
    private @Nullable Material loadMaterial(final ResourceManager manager, final Identifier id) {
        final String material = id.getPath();
        final List<int[]> sheets = new ArrayList<>(2);
        final Map<String, Lighting> lighting = new HashMap<>(2);
        for (final String sheet : List.of(BODY_SHEET, LEGGINGS_SHEET)) {
            final Identifier path = id.withPath(
                ignored -> EQUIPMENT_DIRECTORY + sheet + "/" + material + ".png");
            NativeImage image = null;
            try {
                image = readImage(manager, path);
                if (image == null) {
                    continue;
                }
                final int[] pixels = pixels(image);
                sheets.add(pixels);
                lighting.put(sheet, new Lighting(
                    SkinBake.lightmap(pixels), image.getWidth(), image.getHeight()));
            } finally {
                close(image);
            }
        }
        final int[] shades = SkinBake.ramp(sheets);
        if (shades == null) {
            // An equipment texture that is entirely transparent, or one we could not read at all.
            // Nothing to derive a colour from, so the skin is not drawn and vanilla's texture stands.
            ArmorPieces.LOGGER.warn(
                "[Armor Pieces] No colour to take from {}; armor of that material cannot be skinned.", id);
            return null;
        }
        return new Material(SkinBake.table(shades), Map.copyOf(lighting));
    }

    // ---- plumbing -------------------------------------------------------------------------------

    /**
     * The material an equipment texture names: the file's own name, which is what vanilla and every
     * mod alike key their armor art by. Null for a texture that is not an equipment layer at all.
     */
    private static @Nullable String materialName(final Identifier texture) {
        final String path = texture.getPath();
        if (!path.startsWith(EQUIPMENT_DIRECTORY) || !path.endsWith(".png")) {
            return null;
        }
        final int slash = path.lastIndexOf('/');
        return slash < 0 ? null : path.substring(slash + 1, path.length() - ".png".length());
    }

    /**
     * Where the baked pair is registered. The material's whole id is in the path, namespace and all,
     * so two mods' materials of the same name cannot collide in the cache.
     */
    private static Identifier bakedId(final ArmorSkin skin, final String sheet, final Identifier vanillaTexture) {
        return Identifier.fromNamespaceAndPath(
            ArmorPieces.MOD_ID,
            EQUIPMENT_DIRECTORY + sheet + "/" + skin.assetId().getNamespace() + "/" + skin.assetId().getPath()
                + "/" + vanillaTexture.getNamespace() + "/" + materialName(vanillaTexture) + ".png");
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

    private static @Nullable NativeImage readImage(final ResourceManager manager, final Identifier id) {
        final Optional<Resource> resource = manager.getResource(id);
        if (resource.isEmpty()) {
            return null;
        }
        try (InputStream stream = resource.get().open()) {
            return NativeImage.read(stream);
        } catch (final IOException e) {
            ArmorPieces.LOGGER.error("[Armor Pieces] Could not read {}", id, e);
            return null;
        }
    }

    private static void close(final @Nullable NativeImage image) {
        if (image != null) {
            image.close();
        }
    }

    private void releaseBaked() {
        final Minecraft client = Minecraft.getInstance();
        for (final Identifier id : this.registered) {
            client.getTextureManager().release(id);
        }
        this.registered.clear();
        this.resolved.clear();
    }
}
