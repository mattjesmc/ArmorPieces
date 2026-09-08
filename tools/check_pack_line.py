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
        used[j['key']['F']] = f.split('/')[-1][:-5]

mod = {}
for f in glob.glob('src/main/resources/data/armorpieces/armorpieces/armor_decoration/*.json'):
    j = json.load(open(f, encoding='utf-8'))
    mod[f.replace('\\', '/').split('/')[-1][:-5]] = j['anchors'][0]

# --- the proposal ------------------------------------------------------------------------------
# pack: { socket: (piece, centre or None) }
PLAN = {
 'dragon': {
   'crest':('dragon_crest','minecraft:dragon_breath'), 'brow':('dragon_mask',None),
   'horns':('dragon_horns',None), 'pauldrons':('dragon_spines',None),
   'back':('dragon_wings',None), 'collar':('crystal_pendant','minecraft:end_crystal'),
   'vambraces':('dragon_claws',None), 'belt':('dragon_tail',None),
   'tassets':('wing_tatters','minecraft:chorus_fruit'), 'knees':('dragon_knuckles','minecraft:end_rod'),
   'greaves':('dragon_scales','minecraft:purpur_block'), 'spurs':('dragon_talons','minecraft:chorus_flower')},
 'nether': {
   'crest':('hoglin_hair','minecraft:porkchop'), 'brow':('wither_mask',None),
   'horns':('strider_hair','minecraft:warped_fungus'), 'pauldrons':('wither_heads',None),
   'back':('blaze_halo','minecraft:blaze_powder'), 'collar':('wither_ribs',None),
   'vambraces':('blaze_bracers','minecraft:magma_cream'), 'belt':('brute_belt','minecraft:golden_axe'),
   'tassets':('ghast_tendrils','minecraft:ghast_tear'), 'knees':('magma_cops','minecraft:magma_block'),
   'greaves':('soul_greaves','minecraft:soul_lantern'), 'spurs':('hoglin_hooves','minecraft:crimson_fungus')},
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
   'crest':('witch_hat','minecraft:glass_bottle'), 'brow':('illager_mask',None),
   'horns':('ravager_horns',None), 'pauldrons':('vex_wings',None),
   'back':('ominous_banner',None), 'collar':('totem_pendant','minecraft:totem_of_undying'),
   'vambraces':('ravager_bracers',None), 'belt':('pillager_belt','minecraft:crossbow'),
   'tassets':('ravager_saddle',None), 'knees':('evoker_fangs','minecraft:ominous_bottle'),
   'greaves':('golem_plates','minecraft:iron_helmet'), 'spurs':('allay_wisps','minecraft:amethyst_shard')},
 'coral': {
   'crest':('coral_crown','BUILT'), 'brow':('coral_visor','minecraft:tube_coral_block'),
   'horns':('axolotl_frills','BUILT'), 'pauldrons':('kelp_mantle','BUILT'),
   'back':('anemone_bloom','minecraft:fire_coral_block'), 'collar':('nautilus_gorget','BUILT'),
   'vambraces':('starfish_bracers','minecraft:bubble_coral_block'), 'belt':('sea_pickle_belt','minecraft:sea_pickle'),
   'tassets':('seagrass_skirt','minecraft:seagrass'), 'knees':('barnacle_cops','minecraft:prismarine_shard'),
   'greaves':('urchin_greaves','minecraft:prismarine_crystals'), 'spurs':('dolphin_flukes','minecraft:salmon')},
 'animals': {
   'crest':('rooster_comb','minecraft:egg'), 'brow':('frog_mask','BUILT'),
   'horns':('fox_ears','BUILT'), 'pauldrons':('bee_wings','BUILT'),
   'back':('turtle_shell','BUILT'), 'collar':('flower_brooch','BUILT'),
   'vambraces':('cat_paws','minecraft:cod'), 'belt':('donkey_tail','BUILT'),
   'tassets':('sheep_fleece','minecraft:white_wool'), 'knees':('armadillo_shell','BUILT'),
   'greaves':('llama_wraps','minecraft:white_carpet'), 'spurs':('rabbit_feet','BUILT')},
}

SOCKETS = {'crest','brow','horns','pauldrons','back','collar','vambraces','belt','tassets','knees','greaves','spurs'}

print('=== outfits: twelve own sockets, none borrowed ===')
for pack, o in PLAN.items():
    miss = SOCKETS - set(o)
    print(f'  {pack:12} {len(o):2} sockets' + (f'  MISSING {sorted(miss)}' if miss else '  ok'))

print('\n=== recipe centres: free and unique ===')
seen = collections.defaultdict(list)
for pack, o in PLAN.items():
    for sock, (piece, centre) in o.items():
        if centre and centre != 'BUILT':
            seen[centre].append(f'{pack}:{piece}')
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
