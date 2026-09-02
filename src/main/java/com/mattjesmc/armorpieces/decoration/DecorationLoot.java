package com.mattjesmc.armorpieces.decoration;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import io.netty.buffer.ByteBuf;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.ResourceKey;
import net.minecraft.util.ExtraCodecs;
import net.minecraft.world.level.storage.loot.LootTable;

/**
 * One place in the world a part's template can be found: a loot table the mod adds the part to when
 * that table loads. The {@code loot} list on a part's data file is a list of these.
 *
 * <p>The mod adds ONE POOL PER TABLE, rolled once, holding an entry for every part that names the
 * table - see {@link com.mattjesmc.armorpieces.loot.DecorationLootTables}. That shape is what the
 * two numbers mean. {@code chance} is the entry's own {@code random_chance} condition: how often
 * this part is on offer at all when the chest is filled, and the only thing keeping a part out of
 * every chest, which is why it is required rather than defaulted. {@code weight} is the ordinary
 * loot weight, and only matters between parts that name the same table: two parts at chance 0.2
 * are each offered a fifth of the time, and when both happen to be offered the weights decide
 * which one is placed. A pool of one roll never puts two parts in one chest.
 *
 * <p>A datapack cannot add to a vanilla table on its own - it can only replace the file whole, and
 * two packs replacing the same file fight - which is the reason this is a field on the part rather
 * than a loot table file beside it. The mod is the one place that can add a pool, and it does so
 * for every part in the registry, its own and any pack's alike.
 *
 * @param table  the loot table to add the part to, by id. Any table: a chest, a mob, a fishing pool.
 * @param weight the entry's weight among the parts that share the table. Positive; one is the norm.
 * @param chance how often the entry is offered, 0 to 1. Required, since 1 means every chest.
 */
public record DecorationLoot(ResourceKey<LootTable> table, int weight, float chance) {
    public static final Codec<DecorationLoot> CODEC = RecordCodecBuilder.create(
        i -> i.group(
                ResourceKey.codec(Registries.LOOT_TABLE).fieldOf("table").forGetter(DecorationLoot::table),
                ExtraCodecs.POSITIVE_INT.optionalFieldOf("weight", 1).forGetter(DecorationLoot::weight),
                Codec.floatRange(0.0f, 1.0f).fieldOf("chance").forGetter(DecorationLoot::chance)
            )
            .apply(i, DecorationLoot::new)
    );
    public static final Codec<java.util.List<DecorationLoot>> LIST_CODEC = CODEC.listOf();

    public static final StreamCodec<ByteBuf, DecorationLoot> STREAM_CODEC = StreamCodec.composite(
        ResourceKey.streamCodec(Registries.LOOT_TABLE), DecorationLoot::table,
        ByteBufCodecs.VAR_INT, DecorationLoot::weight,
        ByteBufCodecs.FLOAT, DecorationLoot::chance,
        DecorationLoot::new
    );
}
