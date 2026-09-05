package com.mattjesmc.armorpieces.client.item;

import com.mattjesmc.armorpieces.ArmorPieces;
import com.mojang.blaze3d.platform.NativeImage;
import com.mojang.serialization.MapCodec;
import java.io.IOException;
import java.io.InputStream;
import java.util.Map;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.minecraft.client.renderer.texture.SpriteContents;
import net.minecraft.client.renderer.texture.atlas.SpriteResourceLoader;
import net.minecraft.client.renderer.texture.atlas.SpriteSource;
import net.minecraft.client.resources.metadata.animation.FrameSize;
import net.minecraft.resources.Identifier;
import net.minecraft.server.packs.resources.Resource;
import net.minecraft.server.packs.resources.ResourceManager;
import org.jspecify.annotations.Nullable;

/**
 * The sprite source that puts one icon on the item atlas for every skin that exists.
 *
 * <p>Declared in {@code assets/minecraft/atlases/items.json}, which is the item atlas's own
 * definition: those files stack across packs rather than replacing one another, so this appends to
 * vanilla's list instead of overriding it.
 *
 * <p>It takes no configuration on purpose. What it stitches is "every skin with a body sheet in the
 * resources", which is a thing to be discovered and not a list to be maintained - a pack that ships
 * a skin gets its icon here, on the same terms as the mod's own, and neither has to say so.
 *
 * <p>A sprite this produces loses to a real texture of the same name, so a pack that would rather
 * hand-draw its icon ships {@code textures/item/skin_template_<skin>.png} and is obeyed.
 */
@Environment(EnvType.CLIENT)
public record SkinTemplateIconSource() implements SpriteSource {
    public static final Identifier ID =
        Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "skin_template_icons");
    public static final MapCodec<SkinTemplateIconSource> MAP_CODEC =
        MapCodec.unit(new SkinTemplateIconSource());

    @Override
    public void run(final ResourceManager manager, final SpriteSource.Output output) {
        final Map<Identifier, Resource> sheets = SkinTemplateIcon.sheets(manager);
        SkinTemplateIcon.stitched(sheets.keySet());
        sheets.forEach(
            (assetId, sheet) -> output.add(SkinTemplateIcon.sprite(assetId), new Loader(assetId, sheet)));
        ArmorPieces.LOGGER.info("[Armor Pieces] {} skin template icon(s) on the item atlas: {}",
            sheets.size(), sheets.keySet());
    }

    @Override
    public MapCodec<SkinTemplateIconSource> codec() {
        return MAP_CODEC;
    }

    /**
     * One icon, drawn when the stitcher asks for it and not before - the atlas discards the sources
     * it does not need, and a skin's sheet should not be read for an icon that will be thrown away.
     */
    @Environment(EnvType.CLIENT)
    private record Loader(Identifier assetId, Resource sheet) implements SpriteSource.DiscardableLoader {
        @Override
        public @Nullable SpriteContents get(final SpriteResourceLoader loader) {
            try (InputStream stream = this.sheet.open(); NativeImage master = NativeImage.read(stream)) {
                final NativeImage icon = SkinTemplateIcon.draw(master);
                return new SpriteContents(
                    SkinTemplateIcon.sprite(this.assetId),
                    new FrameSize(icon.getWidth(), icon.getHeight()),
                    icon);
            } catch (final IOException e) {
                ArmorPieces.LOGGER.error("[Armor Pieces] Could not draw the icon for skin {}", this.assetId, e);
                return null;
            }
        }

        @Override
        public void discard() {}
    }
}
