"""Mechanical checks over the proposed pack line: centres free+unique, sockets unique per outfit,
no generic name shadowing, loot tables real."""
import json, glob, zipfile, collections

JAR = 'C:/Users/Matthijs/.gradle/caches/fabric-loom/26.2/minecraft-merged.jar'

# --- what is already in use --------------------------------------------------------------------
used = {}
for f in glob.glob('src/main/resources/data/armorpieces/recipe/*.json') + \
         glob.glob('packs/*/datapack/data/*/recipe/*.json'):
    j = json.load(open(f, encoding='utf-8'))
    if j.get('pattern') == [' # ', '#F#', ' # ']:
        used[j['key']['F']] = f.replace('\\', '/').split('/')[-1][:-5]

mod = {}
for f in glob.glob('src/main/resources/data/armorpieces/armorpieces/armor_decoration/*.json'):
    j = json.load(open(f, encoding='utf-8'))
    mod[f.replace('\\', '/').split('/')[-1][:-5]] = j['anchors'][0]

# --- the proposal ------------------------------------------------------------------------------
# pack: { socket: (piece, centre or None) }
PLAN = {
 'dragon': {
   'crest':('dragon_crest','BUILT'), 'brow':('dragon_mask',None),
   'horns':('dragon_horns',None), 'pauldrons':('dragon_spines',None),
   'back':('dragon_wings',None), 'collar':('crystal_pendant','BUILT'),
   'vambraces':('dragon_claws',None), 'belt':('dragon_tail',None),
   'tassets':('wing_tatters','BUILT'), 'knees':('dragon_knuckles','BUILT'),
   'greaves':('dragon_scales','BUILT'), 'spurs':('dragon_talons','BUILT')},
 'nether': {
   'crest':('hoglin_hair','BUILT'), 'brow':('wither_mask',None),
   'horns':('strider_hair','BUILT'), 'pauldrons':('wither_heads',None),
   'back':('blaze_halo','BUILT'), 'collar':('wither_ribs',None),
   'vambraces':('blaze_bracers','BUILT'), 'belt':('brute_belt','BUILT'),
   'tassets':('ghast_tendrils','BUILT'), 'knees':('magma_cops','BUILT'),
   'greaves':('soul_greaves','BUILT'), 'spurs':('hoglin_hooves','BUILT')},
 'caves': {
   'crest':('shrieker_crown','minecraft:sculk_shrieker'), 'brow':('warden_mask',None),
   'horns':('warden_antennae',None), 'pauldrons':('catalyst_bloom','minecraft:sculk_catalyst'),
   'back':('sculk_growth','minecraft:sculk'), 'collar':('echo_pendant',None),
   'vambraces':('sculk_veins','minecraft:sculk_vein'), 'belt':('ancient_candles','minecraft:candle'),
   'tassets':('deepslate_lames','minecraft:polished_deepslate'), 'knees':('sculk_cops','minecraft:deepslate_tiles'),
   'greaves':('sculk_shins','minecraft:deepslate_bricks'), 'spurs':('sensor_tendrils','minecraft:sculk_sensor')},
 'caves_lush': {
   'crest':('spore_blossom','minecraft:spore_blossom'), 'brow':('lichen_mask','minecraft:glow_lichen'),
   'horns':('azalea_sprigs','minecraft:flowering_azalea'), 'pauldrons':('dripstone_spikes','minecraft:pointed_dripstone'),
   'back':('glow_berry_vines','minecraft:glow_berries'), 'collar':('glow_squid_ink','minecraft:glow_ink_sac'),
   'vambraces':('vine_wraps','minecraft:vine'), 'belt':('root_girdle','minecraft:rooted_dirt'),
   'tassets':('hanging_roots','minecraft:hanging_roots'), 'knees':('dripstone_cops','minecraft:dripstone_block'),
   'greaves':('moss_greaves','minecraft:moss_block'), 'spurs':('dripstone_spurs','minecraft:calcite')},
 'village': {
   'crest':('witch_hat','BUILT'), 'brow':('illager_mask','BUILT'),
   'horns':('ravager_horns','BUILT'), 'pauldrons':('vex_wings','BUILT'),
   'back':('ominous_banner','BUILT'), 'collar':('totem_pendant','BUILT'),
   'vambraces':('ravager_bracers','BUILT'), 'belt':('pillager_belt','BUILT'),
   'tassets':('ravager_saddle','BUILT'), 'knees':('evoker_fangs','BUILT'),
   'greaves':('golem_plates','BUILT'), 'spurs':('allay_wisps','BUILT')},
 'coral': {
   'crest':('coral_crown','BUILT'), 'brow':('coral_visor','minecraft:tube_coral_block'),
   'horns':('axolotl_frills','BUILT'), 'pauldrons':('kelp_mantle','BUILT'),
   'back':('anemone_bloom','minecraft:fire_coral_block'), 'collar':('nautilus_gorget','BUILT'),
   'vambraces':('starfish_bracers','minecraft:bubble_coral_block'), 'belt':('sea_pickle_belt','minecraft:sea_pickle'),
   'tassets':('seagrass_skirt','minecraft:seagrass'), 'knees':('barnacle_cops','minecraft:prismarine_shard'),
   'greaves':('urchin_greaves','minecraft:prismarine_crystals'), 'spurs':('dolphin_flukes','minecraft:salmon')},
 # The Hive's eight, designed 2026-09-12 to finish the pack the split created (main-pack-split.md
 # "Is armorpieces_hive a pack or a merger?" - answered: a pack). `honeycomb` is bee_wings' and
 # `string` is garters', which is why the gorget takes the block and the belt takes the cobweb.
 'hive': {
   'crest':('antennae','BUILT'), 'brow':('compound_eyes','minecraft:spider_eye'),
   'horns':('aerials','BUILT'), 'pauldrons':('wing_cases','BUILT'),
   'back':('carapace','BUILT'), 'collar':('honeycomb_gorget','minecraft:honeycomb_block'),
   'vambraces':('chitin_bracers','minecraft:beehive'), 'belt':('spinneret_belt','minecraft:cobweb'),
   'tassets':('abdomen_plates','minecraft:honey_bottle'), 'knees':('spider_cops','minecraft:fermented_spider_eye'),
   'greaves':('silverfish_greaves','minecraft:stone_bricks'), 'spurs':('stinger_spurs','minecraft:bee_nest')},
 'animals': {
   'crest':('rooster_comb','minecraft:egg'), 'brow':('frog_mask','BUILT'),
   'horns':('fox_ears','BUILT'), 'pauldrons':('bee_wings','BUILT'),
   'back':('turtle_shell','BUILT'), 'collar':('flower_brooch','BUILT'),
   'vambraces':('cat_paws','minecraft:cod'), 'belt':('donkey_tail','BUILT'),
   'tassets':('sheep_fleece','minecraft:white_wool'), 'knees':('armadillo_shell','BUILT'),
   'greaves':('llama_wraps','minecraft:white_carpet'), 'spurs':('rabbit_feet','BUILT')},
 # The four culture packs, designed 2026-09-13 (docs/plans/cultures.md): Samurai, Norse, Antiquity,
 # Tournament. Every piece has a centre; the plan and the briefs come from one generator.
 'samurai': {
   'crest':('maedate','minecraft:sunflower'), 'brow':('mempo','minecraft:red_dye'),
   'horns':('kuwagata','minecraft:golden_hoe'), 'pauldrons':('sode','minecraft:black_dye'),
   'back':('sashimono','minecraft:red_banner'), 'collar':('nodowa','minecraft:iron_chestplate'),
   'vambraces':('kote','minecraft:cyan_dye'), 'belt':('daisho','minecraft:golden_sword'),
   'tassets':('kusazuri','minecraft:red_wool'), 'knees':('haidate','minecraft:leather_leggings'),
   'greaves':('suneate','minecraft:bamboo'), 'spurs':('waraji','minecraft:wheat')},
 'norse': {
   'crest':('boar_crest','minecraft:cooked_porkchop'), 'brow':('braided_beard','minecraft:shears'),
   'horns':('war_braids','minecraft:bone'), 'pauldrons':('ravens','minecraft:ink_sac'),
   'back':('round_shield','minecraft:oak_boat'), 'collar':('torc','minecraft:raw_gold'),
   'vambraces':('oath_rings','minecraft:raw_copper'), 'belt':('seax_belt','minecraft:stone_sword'),
   'tassets':('hip_axes','minecraft:stone_axe'), 'knees':('fur_cops','minecraft:mutton'),
   'greaves':('winingas','minecraft:brown_wool'), 'spurs':('snowshoes','minecraft:stick')},
 'antiquity': {
   'crest':('transverse_crest','minecraft:leather_horse_armor'), 'brow':('corinthian_face','minecraft:copper_helmet'),
   'horns':('ammon_horns','minecraft:cooked_mutton'), 'pauldrons':('epomides','minecraft:leather_helmet'),
   'back':('scutum','minecraft:painting'), 'collar':('phalerae','minecraft:golden_apple'),
   'vambraces':('manica','minecraft:chainmail_chestplate'), 'belt':('cingulum','minecraft:copper_nugget'),
   'tassets':('pteruges','minecraft:brown_dye'), 'knees':('gorgon_cops','minecraft:ender_eye'),
   'greaves':('ocreae','minecraft:copper_boots'), 'spurs':('caligae','minecraft:leather_boots')},
 'tourney': {
   'crest':('lion_crest','minecraft:yellow_dye'), 'brow':('tilting_grille','minecraft:iron_trapdoor'),
   'horns':('mantling','minecraft:blue_dye'), 'pauldrons':('grandguard','minecraft:copper_chestplate'),
   'back':('ecranche','minecraft:blue_banner'), 'collar':('lance_rest','minecraft:tripwire_hook'),
   'vambraces':('favour','minecraft:rose_bush'), 'belt':('sword_belt','minecraft:wooden_sword'),
   'tassets':('cuisses','minecraft:iron_leggings'), 'knees':('rondel_cops','minecraft:iron_horse_armor'),
   'greaves':('schynbalds','minecraft:chainmail_leggings'), 'spurs':('sabatons','minecraft:golden_boots')},
}

SOCKETS = {'crest','brow','horns','pauldrons','back','collar','vambraces','belt','tassets','knees','greaves','spurs'}

print('=== outfits: twelve own sockets, none borrowed ===')
for pack, o in PLAN.items():
    miss = SOCKETS - set(o)
    print(f'  {pack:12} {len(o):2} sockets' + (f'  MISSING {sorted(miss)}' if miss else '  ok'))

print('\n=== recipe centres: free and unique ===')
seen = collections.defaultdict(list)
built_now = 0
for pack, o in PLAN.items():
    for sock, (piece, centre) in o.items():
        # A planned piece whose own template recipe is on disk has been built: its centre is in
        # `used` under its own name, and that is not a collision (2026-09-12, the seventeen).
        if centre and centre != 'BUILT' and used.get(centre) == f'template_{piece}':
            built_now += 1
            continue
        if centre and centre != 'BUILT':
            seen[centre].append(f'{pack}:{piece}')
if built_now:
    print(f'  {built_now} planned piece(s) already built (own recipe on disk), not counted as new')
bad = 0
for centre, who in sorted(seen.items()):
    if centre in used:
        print(f'  COLLIDES with mod/pack recipe {used[centre]:22} {centre}  <- {who}'); bad += 1
    if len(who) > 1:
        print(f'  DUPLICATE inside the plan          {centre}  <- {who}'); bad += 1
print(f'  {len(seen)} new centres, {bad} problems')

print('\n=== centres exist as items ===')
z = zipfile.ZipFile(JAR)
lang = json.loads(z.read('assets/minecraft/lang/en_us.json').decode('utf-8'))
for centre in sorted(seen):
    i = centre.split(':')[1]
    if not (lang.get('item.minecraft.' + i) or lang.get('block.minecraft.' + i)):
        print(f'  NOT AN ITEM: {centre}')

print('\n=== name shadowing: a pack piece may not reuse a GENERIC mod name in the same socket ===')
for pack, o in PLAN.items():
    for sock, (piece, _) in o.items():
        if piece in mod:
            print(f'  EXACT NAME CLASH {pack}:{piece} vs armorpieces:{piece} (mod socket {mod[piece]})')

print('\n=== loot tables named by the plan ===')
tables = ['entities/wither','entities/warden','entities/elder_guardian','entities/ender_dragon',
          'chests/end_city_treasure','chests/ancient_city','chests/ancient_city_ice_box',
          'chests/bastion_treasure','chests/bastion_other','chests/bastion_hoglin_stable',
          'chests/nether_bridge','chests/pillager_outpost','chests/woodland_mansion']
names = set(z.namelist())
for t in tables:
    ok = f'data/minecraft/loot_table/{t}.json' in names
    print(f'  {"ok " if ok else "MISSING"} minecraft:{t}')
