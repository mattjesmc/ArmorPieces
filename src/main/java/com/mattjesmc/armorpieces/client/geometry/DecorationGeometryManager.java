package com.mattjesmc.armorpieces.client.geometry;

import com.mattjesmc.armorpieces.ArmorPieces;
import java.util.HashMap;
import java.util.Map;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.fabricmc.fabric.api.resource.IdentifiableResourceReloadListener;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.resources.FileToIdConverter;
import net.minecraft.resources.Identifier;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.SimpleJsonResourceReloadListener;
import net.minecraft.util.profiling.ProfilerFiller;
import org.jspecify.annotations.Nullable;

/**
 * Loads and bakes every decorative part's geometry from resource packs.
 *
 * <p>Scans {@code assets/<any namespace>/armorpieces/decoration/*.json}, so a resource pack adds a
 * shape by dropping a file and overrides one of ours by using the same id - the ordinary pack
 * stack, no registration step. Baking happens once per reload and the resulting {@link ModelPart}
 * trees are cached here; the render layer only ever does a map lookup.
 *
 * <p>A part whose JSON is malformed is logged and skipped rather than being allowed to fail the
 * reload. One broken third-party pack should cost that part, not the player's resource pack.
 */
@Environment(EnvType.CLIENT)
public class DecorationGeometryManager
    extends SimpleJsonResourceReloadListener<DecorationGeometry>
    implements IdentifiableResourceReloadListener {

    private static final Identifier ID =
        Identifier.fromNamespaceAndPath(ArmorPieces.MOD_ID, "decoration_geometry");
    private static final FileToIdConverter LISTER = FileToIdConverter.json("armorpieces/decoration");

    /** The single client-side instance, held so the render layer can reach it without plumbing. */
    private static final DecorationGeometryManager INSTANCE = new DecorationGeometryManager();

    // Written on the reload's apply stage and read while rendering. Those are the same thread today,
    // but volatile costs nothing here and keeps the handoff correct if that ever stops being true.
    private volatile Map<Identifier, ModelPart> baked = Map.of();

    private DecorationGeometryManager() {
        super(DecorationGeometry.CODEC, LISTER);
    }

    public static DecorationGeometryManager instance() {
        return INSTANCE;
    }

    /**
     * The baked shape for a part's asset id, or {@code null} if no pack supplies one.
     *
     * <p>Null is a legitimate answer, not an error: a part may be overlay-only, and a datapack may
     * name a part whose resource pack half is not installed. Callers draw what they have.
     */
    public @Nullable ModelPart get(final Identifier assetId) {
        return this.baked.get(assetId);
    }

    @Override
    protected void apply(
        final Map<Identifier, DecorationGeometry> preparations,
        final ResourceManager manager,
        final ProfilerFiller profiler
    ) {
        final Map<Identifier, ModelPart> result = new HashMap<>(preparations.size());
        for (final var entry : preparations.entrySet()) {
            try {
                result.put(entry.getKey(), entry.getValue().bake());
            } catch (final RuntimeException e) {
                // Bad geometry means bad numbers - a zero-size box, a UV off the texture. Losing one
                // part is recoverable; aborting the reload is not.
                ArmorPieces.LOGGER.error("[Armor Pieces] Could not bake decoration geometry {}", entry.getKey(), e);
            }
        }
        this.baked = Map.copyOf(result);
        ArmorPieces.LOGGER.info("[Armor Pieces] Baked {} decoration geometries.", this.baked.size());
    }

    @Override
    public Identifier getFabricId() {
        return ID;
    }
}
