package com.mattjesmc.armorpieces.loot;

import com.mattjesmc.armorpieces.cloth.Cloth;
import com.mattjesmc.armorpieces.decoration.ArmorDecoration;
import com.mattjesmc.armorpieces.decoration.ArmorPiecesRegistries;
import com.mattjesmc.armorpieces.decoration.fitting.Fitting;
import com.mattjesmc.armorpieces.skin.ArmorSkin;
import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.DynamicOps;
import com.mojang.serialization.Encoder;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.List;
import java.util.Optional;
import net.minecraft.core.HolderGetter;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.util.ExtraCodecs;
import net.minecraft.world.level.storage.loot.LootTable;

/**
 * A CATEGORY OF LOOT TABLES and the templates that are found in it, loaded from
 * {@code data/<ns>/armorpieces/loot_group/<name>.json}.
 *
 * <pre>{@code
 * { "chance": 0.10,
 *   "tables": [ "minecraft:chests/stronghold_corridor",
 *               { "table": "minecraft:chests/woodland_mansion", "chance": 0.18 } ],
 *   "parts": "#armorpieces:knightly" }
 * }</pre>
 *
 * <p>This exists because the other way round does not scale. A part naming its own tables is exact
 * and stays as the escape hatch (see {@link com.mattjesmc.armorpieces.decoration.DecorationLoot}),
 * but it is one edit per part per table, and at ninety parts nobody can see the shape of the result
 * from ninety files. A group is the shape: one file says "a stronghold chest offers a knightly part
 * one time in eight", and which parts those are is a TAG - so a part joins by being tagged, and a
 * pack joins ours by writing one line into {@code data/<ns>/tags/armorpieces/armor_decoration/
 * knightly.json} rather than by overriding a file of ours.
 *
 * <p><b>The chance belongs to the table, not to the member.</b> That is the whole reason this shape
 * was chosen over a chance per part. The mod adds ONE POOL PER TABLE, rolled once, with a single
 * {@code random_chance} on the pool; every part, skin and cloth that reaches the table is an entry
 * in it, and the weights decide which one is placed. So the odds of a chest holding SOMETHING are
 * the number written here and stay there for ever: adding a ninety-first part changes which part is
 * found, never how often. Under a chance per entry it would be {@code 1-∏(1-c)}, which climbs with
 * every part added until every chest holds one.
 *
 * <p>Groups may overlap. A table named by two groups gets one pool holding both groups' members, at
 * the highest chance either asked for - so a table can be "knightly, and occasionally courtly"
 * without either file knowing about the other.
 *
 * @param chance  how often a table in this group offers one of its members, 0 to 1. A table entry
 *                may override it, which is how one treasure chest is generous and the corridor
 *                chests around it are not.
 * @param weight  the loot weight every member of this group gets, which only matters against the
 *                other groups sharing a table: a group at weight 1 beside one at weight 3 supplies
 *                a quarter of what that table offers.
 * @param tables  the category itself - the loot tables these members are found in.
 * <p><b>The members are named, not bound.</b> All four are a {@link MemberSet}, which keeps a tag as
 * a tag and asks for it at the moment the group is used. That is not a detail: the ordinary
 * {@code RegistryCodecs.homogeneousList} resolves a tag when the FILE IS READ, and a tag no
 * installed pack defines is then an unbound tag, which does not make a smaller group - it takes the
 * whole registry down with {@code Unbound tags in registry armorpieces:armor_decoration} and the
 * world will not open. A player who installs one pack of the line and not another meets that on
 * every group either pack ships, so late resolution is the only shape this field can have. The
 * gate's {@code missing-tag} boot check is that case, and it is what found this.
 *
 * @param parts    the parts in the group, normally a tag.
 * @param skins    the armor skins in the group.
 * @param cloths   the cloths in the group.
 * @param fittings the fittings whose templates are found here. A group is the ONLY route into the
 *                 world for a fitting template: unlike the other three, a {@link Fitting} is a
 *                 dispatched codec - one record per type - so a {@code loot} field on it would have
 *                 to be added to every type and to every type a pack ever writes. A category of
 *                 tables naming a tag of fittings says the same thing from the other side and costs
 *                 nothing.
 */
public record LootGroup(
    float chance,
    int weight,
    List<LootGroup.TableEntry> tables,
    MemberSet<ArmorDecoration> parts,
    MemberSet<ArmorSkin> skins,
    MemberSet<Cloth> cloths,
    MemberSet<Fitting> fittings
) {
    public static final Codec<LootGroup> DIRECT_CODEC = RecordCodecBuilder.create(
        i -> i.group(
                Codec.floatRange(0.0f, 1.0f).fieldOf("chance").forGetter(LootGroup::chance),
                ExtraCodecs.POSITIVE_INT.optionalFieldOf("weight", 1).forGetter(LootGroup::weight),
                TableEntry.CODEC.listOf().fieldOf("tables").forGetter(LootGroup::tables),
                MemberSet.<ArmorDecoration>codec(ArmorPiecesRegistries.ARMOR_DECORATION)
                    .optionalFieldOf("parts", MemberSet.empty())
                    .forGetter(LootGroup::parts),
                MemberSet.<ArmorSkin>codec(ArmorPiecesRegistries.ARMOR_SKIN)
                    .optionalFieldOf("skins", MemberSet.empty())
                    .forGetter(LootGroup::skins),
                MemberSet.<Cloth>codec(ArmorPiecesRegistries.CLOTH)
                    .optionalFieldOf("cloths", MemberSet.empty())
                    .forGetter(LootGroup::cloths),
                MemberSet.<Fitting>codec(ArmorPiecesRegistries.FITTING)
                    .optionalFieldOf("fittings", MemberSet.empty())
                    .forGetter(LootGroup::fittings)
            )
            .apply(i, LootGroup::new)
    );

    public LootGroup {
        tables = List.copyOf(tables);
    }

    /**
     * How many members the group has right now - which is a question only the loaded packs can
     * answer, since a tag naming nothing is a group of nothing. What {@code /armorpieces loot
     * groups} prints.
     */
    public int memberCount(final HolderGetter.Provider registries) {
        return this.parts.resolve(registries).size()
            + this.skins.resolve(registries).size()
            + this.cloths.resolve(registries).size()
            + this.fittings.resolve(registries).size();
    }

    /**
     * How often {@code table} offers a member of this group, or empty if the group does not name it.
     * The table's own chance wins over the group's; that is the only reason a table entry is ever
     * written the long way.
     */
    public Optional<Float> chanceFor(final ResourceKey<LootTable> table) {
        for (final TableEntry entry : this.tables) {
            if (entry.table().equals(table)) {
                return Optional.of(entry.chance().orElse(this.chance));
            }
        }
        return Optional.empty();
    }

    /**
     * One loot table in the category. Written as a bare id, or as an object when it wants a chance
     * of its own.
     *
     * @param table  the loot table. Any table: a chest, a mob, a fishing pool.
     * @param chance overrides the group's, 0 to 1.
     */
    public record TableEntry(ResourceKey<LootTable> table, Optional<Float> chance) {
        private static final Codec<TableEntry> FULL = RecordCodecBuilder.create(
            i -> i.group(
                    ResourceKey.codec(Registries.LOOT_TABLE).fieldOf("table").forGetter(TableEntry::table),
                    Codec.floatRange(0.0f, 1.0f).optionalFieldOf("chance").forGetter(TableEntry::chance)
                )
                .apply(i, TableEntry::new)
        );
        private static final Codec<TableEntry> BARE = ResourceKey.codec(Registries.LOOT_TABLE)
            .xmap(table -> new TableEntry(table, Optional.empty()), TableEntry::table);

        /**
         * Reads either form; writes the SHORT one only when there is nothing else to say.
         *
         * <p>{@code Codec.withAlternative} would do the reading on its own, but it encodes with its
         * first codec always - so a table carrying a chance of its own would be written back as a
         * bare id and the chance lost. Nothing encoded a table entry while these files were only
         * ever read; {@link com.mattjesmc.armorpieces.config.ArmorPiecesServerConfig} writes its own
         * file back, and does.
         */
        public static final Codec<TableEntry> CODEC = Codec.of(
            new Encoder<TableEntry>() {
                @Override
                public <T> DataResult<T> encode(
                    final TableEntry input, final DynamicOps<T> ops, final T prefix
                ) {
                    return (input.chance().isEmpty() ? BARE : FULL).encode(input, ops, prefix);
                }
            },
            Codec.withAlternative(BARE, FULL));
    }
}
