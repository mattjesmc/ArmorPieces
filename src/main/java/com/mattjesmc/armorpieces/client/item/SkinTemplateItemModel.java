package com.mattjesmc.armorpieces.client.item;

import com.google.common.base.Suppliers;
import com.mattjesmc.armorpieces.ArmorPieces;
import com.mattjesmc.armorpieces.registry.ModDataComponents;
import com.mattjesmc.armorpieces.skin.ArmorSkinValue;
import com.mojang.serialization.MapCodec;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Supplier;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.block.dispatch.BlockModelRotation;
import net.minecraft.client.renderer.item.CuboidItemModelWrapper;
import net.minecraft.client.renderer.item.ItemModel;
import net.minecraft.client.renderer.item.ItemModelResolver;
import net.minecraft.client.renderer.item.ItemStackRenderState;
import net.minecraft.client.renderer.item.ModelRenderProperties;
import net.minecraft.client.resources.model.ModelBaker;
import net.minecraft.client.resources.model.ResolvableModel;
import net.minecraft.client.resources.model.ResolvedModel;
import net.minecraft.client.resources.model.geometry.BakedQuad;
import net.minecraft.client.resources.model.geometry.QuadCollection;
import net.minecraft.client.resources.model.sprite.Material;
import net.minecraft.client.resources.model.sprite.TextureSlots;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.ItemOwner;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import org.joml.Matrix4fc;
import org.joml.Vector3fc;
import org.jspecify.annotations.Nullable;

/**
 * The skin template's item model: one item that wears whichever skin it carries.
 *
 * <p>This exists because {@code minecraft:select} - the vanilla way to give one item many looks -
 * cannot be added to from another pack. Its cases live in one file, resource packs resolve a file by
 * winning it outright rather than by merging it, and so a select listing the mod's own skins is a
 * select a pack's skin can never join: it would have to copy every case the mod ships into its own
 * override, go stale the moment the mod ships another, and lose to the next pack that does the same.
 *
 * <p>So the choice is made here instead, off the same {@code armorpieces:skin} component the select
 * read, against art that {@link SkinTemplateIconSource} draws from the skins that exist. Nothing is
 * enumerated in JSON, nothing is generated into the resources, and a skin - the mod's or a pack's -
 * gets its icon by existing. A skin with no art of its own falls back to the generic card, which is
 * what an unknown skin should look like.
 *
 * <p>The geometry is the generic model's, baked once per skin against that skin's own sprite: an
 * item model built from {@code minecraft:item/generated} takes its shape from the texture it is
 * given, so one model and fifteen sprites are fifteen icons.
 */
@Environment(EnvType.CLIENT)
public class SkinTemplateItemModel implements ItemModel {
    /** The type name a pack writes in {@code items/skin_template.json}. */
    public static final Identifier ID =
        Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "skin_template");

    /**
     * The model every icon is baked from, and the sprite an unknown skin falls back to: the template
     * card with the generic skin emblem on it, which is the one piece of this that is still drawn by
     * hand (by {@code tools/gen_template_icons.py}, with the other twelve template icons).
     */
    private static final Identifier BASE_MODEL =
        Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "item/skin_template");
    private static final Identifier FALLBACK_SPRITE =
        Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "item/skin_template");

    /** By the skin's asset id - what {@link SkinTemplateIcon#sheets} keys its findings by. */
    private final Map<Identifier, Icon> icons;
    private final Icon fallback;
    private final Matrix4fc transformation;

    private SkinTemplateItemModel(
        final Map<Identifier, Icon> icons,
        final Icon fallback,
        final Matrix4fc transformation
    ) {
        this.icons = icons;
        this.fallback = fallback;
        this.transformation = transformation;
    }

    @Override
    public void update(
        final ItemStackRenderState output,
        final ItemStack item,
        final ItemModelResolver resolver,
        final ItemDisplayContext displayContext,
        final @Nullable ClientLevel level,
        final @Nullable ItemOwner owner,
        final int seed
    ) {
        final Icon icon = iconFor(item);
        output.appendModelIdentityElement(this);
        // Which skin this stack wears is the whole difference between two of these, so it has to be
        // part of the identity the render state is cached under.
        output.appendModelIdentityElement(icon.sprite());
        final ItemStackRenderState.LayerRenderState layer = output.newLayer();
        if (item.hasFoil()) {
            layer.setFoilType(ItemStackRenderState.FoilType.STANDARD);
            output.setAnimated();
            output.appendModelIdentityElement(ItemStackRenderState.FoilType.STANDARD);
        }
        layer.setExtents(icon.extents());
        layer.setLocalTransform(this.transformation);
        icon.properties().applyToLayer(layer, displayContext);
        layer.prepareQuadList().addAll(icon.quads().getAll());
        if (icon.quads().hasMaterialFlag(BakedQuad.FLAG_ANIMATED)) {
            // Never true of a sprite this mod drew, but a pack may hand-draw its icon and animate it.
            output.setAnimated();
        }
    }

    private Icon iconFor(final ItemStack item) {
        final ArmorSkinValue skin = item.get(ModDataComponents.SKIN);
        if (skin == null) {
            return this.fallback;
        }
        return this.icons.getOrDefault(skin.skin().value().assetId(), this.fallback);
    }

    /** One skin's icon as the renderer needs it. */
    private record Icon(
        Identifier sprite,
        QuadCollection quads,
        Supplier<Vector3fc[]> extents,
        ModelRenderProperties properties
    ) {}

    private static Icon bakeIcon(
        final ModelBaker baker,
        final ResolvedModel base,
        final Identifier sprite
    ) {
        // The slots are handed to the bake rather than read off the model, which is the seam this
        // whole class turns on: `minecraft:item/generated` builds its quads from whatever layer0 it
        // is given, so the same model baked against fifteen sprites is fifteen icons. `particle` is
        // pointed at layer0 the way the generated model points it at its own.
        final TextureSlots slots = new TextureSlots.Resolver()
            .addLast(new TextureSlots.Data.Builder()
                .addTexture("layer0", new Material(sprite))
                .addReference("particle", "layer0")
                .build())
            .resolve(base);
        // NOT base.bakeTopGeometry(...), which is the obvious call and is a trap here: a resolved
        // model caches its baked geometry in a map keyed by the ModelState ALONE (ModelDiscovery's
        // ModelWrapper.modelBakeCache), on the assumption that a model is baked once with its own
        // slots. Baking it fifteen times with fifteen different layer0s therefore hands back the
        // FIRST bake fifteen times - fourteen skins wearing whichever icon was drawn first. Going to
        // the geometry directly skips that cache and lands on the generated item model's own, which
        // is keyed by the sprite and so gives each skin its own quads.
        final QuadCollection quads =
            base.getTopGeometry().bake(slots, baker, BlockModelRotation.IDENTITY, base);
        return new Icon(
            sprite,
            quads,
            Suppliers.memoize(() -> CuboidItemModelWrapper.computeExtents(quads.getAll())),
            ModelRenderProperties.fromResolvedModel(baker, base, slots));
    }

    /**
     * What {@code items/skin_template.json} says, which is now only its own name: everything this
     * model needs it finds for itself.
     */
    @Environment(EnvType.CLIENT)
    public record Unbaked() implements ItemModel.Unbaked {
        public static final MapCodec<Unbaked> MAP_CODEC = MapCodec.unit(new Unbaked());

        @Override
        public void resolveDependencies(final ResolvableModel.Resolver resolver) {
            resolver.markDependency(BASE_MODEL);
        }

        @Override
        public ItemModel bake(final ItemModel.BakingContext context, final Matrix4fc transformation) {
            final ModelBaker baker = context.blockModelBaker();
            final ResolvedModel base = baker.getModel(BASE_MODEL);
            final Map<Identifier, Icon> icons = new HashMap<>();
            // Only the skins whose sprites were actually stitched: baking against a sprite that is
            // not on the atlas would draw the missing-texture chequer, where falling back to the
            // generic card says the honest thing.
            for (final Identifier assetId : SkinTemplateIcon.stitched()) {
                icons.put(assetId, bakeIcon(baker, base, SkinTemplateIcon.sprite(assetId)));
            }
            ArmorPieces.LOGGER.debug("[Armor Pieces] baked {} skin template icon(s): {}",
                icons.size(), icons.keySet());
            return new SkinTemplateItemModel(
                Map.copyOf(icons), bakeIcon(baker, base, FALLBACK_SPRITE), transformation);
        }

        @Override
        public MapCodec<Unbaked> type() {
            return MAP_CODEC;
        }
    }
}
