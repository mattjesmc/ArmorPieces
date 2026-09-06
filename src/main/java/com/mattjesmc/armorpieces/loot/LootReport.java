package com.mattjesmc.armorpieces.loot;

import java.util.List;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.storage.loot.LootTable;

/**
 * What the mod did to ONE loot table, kept so that {@code /armorpieces loot explain} can say it.
 *
 * <p>This exists because the result of {@link DecorationLootTables} is otherwise unknowable from
 * inside the game. The pool it adds is buried in a built loot table; the reasons for the number on
 * it are spread over the groups, the parts' own {@code loot} rows and the server config; and for a
 * modded pack the table ids are unguessable in the first place. A player could open two hundred
 * chests and still not learn which group put a part in them or at what odds. So the decision is
 * recorded as it is made, in the one place that knows all of it.
 *
 * <p>It is a record of a decision, not a cache: nothing reads it back to build anything. Rebuilding
 * the pool from it would be the bug this shape exists to avoid, because a report that could not
 * disagree with the table would also never catch the day it does.
 *
 * @param table   the table this is about.
 * @param sources everything that offered a member, in the order they were considered.
 * @param members how many entries the pool ended up with - one per distinct member, never two.
 * @param packChance the chance the packs asked for: the highest any source wanted, before the
 *                   server config's multiplier.
 * @param chance  the chance actually written onto the pool, after the multiplier and the clamp.
 *                Equal to {@code packChance} on a server that has not touched the config.
 */
public record LootReport(
    ResourceKey<LootTable> table,
    List<LootReport.Source> sources,
    int members,
    float packChance,
    float chance
) {
    public LootReport {
        sources = List.copyOf(sources);
    }

    /** Whether the server config changed the odds this table ended up with. */
    public boolean scaled() {
        return this.packChance != this.chance;
    }

    /**
     * One reason members reached this table.
     *
     * @param name       the group's id, or {@link #DIRECT} for the parts, skins and cloths that
     *                   named the table on their own data file.
     * @param chance     the chance this source asked for. Only the highest wins - see
     *                   {@link DecorationLootTables} - so a source below the final number is one
     *                   whose members ride along on a more generous one.
     * @param weight     the weight this source's members carry against the other sources here.
     * @param members    how many members this source offered.
     * @param overridden whether the server config had something to say about this source.
     */
    public record Source(String name, float chance, int weight, int members, boolean overridden) {}

    /** The name a {@link Source} carries when it is the {@code loot} list on a thing's own file. */
    public static final String DIRECT = "part files";
}
