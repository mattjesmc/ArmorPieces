"""Armor Pieces: Norse - twelve pieces. Hair, fur and wood are static; iron and gold are material,
mostly under `guard`; cloth and webbing take `inlay`."""

BLONDE = ("#c9a24a", "#e0bd63", "flaxen hair - the beard and braids' own blonde")
FUR = ("#7d7873", "#9a938c", "wolf-grey fur - the pelt's own grey, and `down` #5c5751, its shadow")
WOOD = ("#a37a48", "#bf9460", "lime wood - the shield board and the axe haft")
RAVEN = ("#141416", "#2a2b33", "raven black - with a blue sheen in the light")
LEATHER = ("#5a3d28", "#75523a", "oiled leather - the straps and the belt")
REDPAINT = ("#9b2226", "#b8353a", "shield red - the painted board's own red")
CREAMPAINT = ("#e6dccb", "#f3ece0", "shield cream - the unpainted quarters, whitewashed lime")
BONE = ("#e6dfcf", "#f2ede2", "bone - the antler hilt and the bead")

P = [
{
 "pack": "norse", "id": "boar_crest", "name": "Boar Crest", "socket": "crest", "centre": "minecraft:cooked_porkchop",
 "short": "a small gilt boar standing on the crest ridge of the helm",
 "line": "`boar_crest` - a gilt boar figure standing on the crown ridge - fitting `guard` - centre `cooked_porkchop`",
 "intent": "The boar-crested helm: an iron ridge running front to back over the crown, and a small "
           "gilt boar standing on it facing forward - a squat body, a lower head thrust forward, and "
           "a row of bristles standing up along its back. It is a figure, not a spike: blocky, "
           "stout, and unmistakably a pig.",
 "cubes": [("ridge", "the iron crest ridge over the crown",
            "x -0.57 .. 0.57    y 33.07 .. 33.63    z -3.63 .. 3.63"),
           ("body", "the boar's body, standing on the ridge",
            "x -1.07 .. 1.07    y 33.63 .. 35.33    z -2.57 .. 1.63"),
           ("head", "the head, thrust forward and a little lower",
            "x -0.87 .. 0.87    y 33.87 .. 35.57    z -3.93 .. -2.57"),
           ("bristles", "the bristles standing up along its back",
            "x -0.33 .. 0.33    y 35.33 .. 36.13    z -2.37 .. 1.23")],
 "neigh": [("comb", "x -0.75..0.75, y 32.50..34.60, z -2.10..5.60", "the mod's steel comb - a plain ridge where yours carries a figure"),
           ("hoglin_hair", "x -0.55..0.55, y 32.03..34.65, z -3.03..4.33", "a pack crest at your ridge's thinness"),
           ("coronet (brow)", "x -6.00..6.00, y 29.00..33.21, z -6.18..-2.25", "a brow piece whose box your ridge's front end crosses in a hull test - an OVERLAP `-`, never a `!`")],
 "fittings": ["guard"], "fit_cubes": ["ridge"],
 "static": [(["body", "head"], "#c8962e", "#e0b04a", "gilt bronze - the boar's own gold"),
            (["bristles"], "#8a6a2a", "#a3823a", "darker bronze - the bristles")],
 "material": "The **ridge** carries no static. It is masked `guard` and is the piece's whole material "
             "surface; the boar is static gilt and never answers the trim.",
 "paint": "body and head: base **160**, `up` **195**, `north` **180**. bristles: base **120**. ridge: "
          "base **130**, `up` **165**.",
},
{
 "pack": "norse", "id": "braided_beard", "name": "Braided Beard", "socket": "brow", "centre": "minecraft:shears",
 "short": "a great blonde beard with two braids hanging over the chest, beaded in metal",
 "line": "`braided_beard` - a great blonde beard on the face, two braids hanging below the chin with metal beads - fitting `guard` - centre `shears`",
 "intent": "A jarl's beard: a thick block of blonde hair over the lower face from under the nose to "
           "below the chin, and two plaited braids hanging down from it in front of the chest, each "
           "ending in a metal bead. It is worn on the helmet's face, so it turns with the head. The "
           "eyes are open above it.",
 "cubes": [("beard", "the beard over the lower face",
            "x -3.27 .. 3.27    y 23.37 .. 26.37    z -5.63 .. -5.13"),
           ("braid_l", "the left braid hanging below the chin",
            "x -2.37 .. -1.23    y 19.57 .. 23.37    z -4.93 .. -4.23"),
           ("braid_r", "the right braid",
            "x 1.23 .. 2.37    y 19.57 .. 23.37    z -4.93 .. -4.23"),
           ("bead_l", "the bead at the end of the left braid",
            "x -2.27 .. -1.33    y 18.87 .. 19.57    z -4.83 .. -4.33"),
           ("bead_r", "the right bead",
            "x 1.33 .. 2.27    y 18.87 .. 19.57    z -4.83 .. -4.33")],
 "neigh": [("barbute", "x -4.00..4.00, y 22.50..29.50, z -5.10..-4.85", "the precedent for a brow piece reaching below the helmet's y 23; yours goes to 18.87"),
           ("mempo", "x -3.93..3.93, y 22.63..27.87, z -6.43..-5.03", "the Samurai's face mask, built in this batch - the same band of the face, never worn with you"),
           ("ruff (collar)", "x -5.88..5.88, y 25.10..26.55, z -5.88..5.88", "on the BODY bone, so the check never compares you with it, but the braids would hang through it - a player's problem, not yours")],
 "fittings": ["guard"], "fit_cubes": ["bead_l", "bead_r"],
 "static": [(["beard", "braid_l", "braid_r"], *BLONDE)],
 "material": "The two **beads** carry no static. They are masked `guard` and are the piece's whole "
             "material surface; the hair is static and never answers the trim.",
 "paint": "beard and braids: base **150**, `north` **170**, `down` **115**. beads: base **140**, `north` "
          "**175**.\n\n**Cut nothing.** The eyes are the open space ABOVE the beard.",
},
{
 "pack": "norse", "id": "war_braids", "name": "War Braids", "socket": "horns", "centre": "minecraft:bone",
 "short": "a long braid hanging from each temple in front of the shoulder, ringed in metal",
 "line": "`war_braids` - a blonde braid from each temple hanging in front of the shoulder, with a metal ring - fitting `guard` - centre `bone`",
 "intent": "A warrior's braids: a root of hair at the front of each temple, a thick plait hanging "
           "straight down beside the face and past the chin, a metal ring binding it below the jaw, "
           "and a loose tail hanging from the ring in front of the shoulder. The plait runs down "
           "the FRONT-side of the head so it clears the shoulder below.",
 "cubes": [("root", "the hair at the front of the temple",
            "x -5.57 .. -5.07    y 28.37 .. 30.43    z -2.63 .. -1.47"),
           ("braid", "the plait hanging beside the face and past the chin",
            "x -5.53 .. -5.07    y 23.07 .. 28.37    z -3.83 .. -3.17"),
           ("ring", "the metal ring binding the plait below the jaw",
            "x -5.63 .. -4.97    y 22.27 .. 23.07    z -3.93 .. -3.07"),
           ("tail", "the loose tail below the ring, in front of the shoulder",
            "x -5.47 .. -5.13    y 20.07 .. 22.27    z -3.77 .. -3.23")],
 "neigh": [("strider_hair", "x -7.25..-4.16, y 25.32..31.66, z -1.60..1.60", "the Nether's temple tufts - the precedent for hair on this socket"),
           ("axolotl_frills", "x -9.35..-3.91, y 23.69..29.05, z -0.24..3.38", "a pack piece that reaches below the helmet's y 23.69 here; you go lower, in front"),
           ("mempo (brow)", "x -3.93..3.93, y 22.63..27.87, z -6.43..-5.03", "built in this batch on the face; your braid at z -3.83..-3.17 sits BEHIND its plane, and the two never meet")],
 "fittings": ["guard"], "fit_cubes": ["ring"],
 "static": [(["root", "braid", "tail"], *BLONDE)],
 "material": "The **ring** carries no static. It is masked `guard` and is the piece's whole material "
             "surface.",
 "paint": "root, braid and tail: base **150**, `west` **170** (the outboard face), `north` **165**. ring: "
          "base **140**, `west` **175**.",
},
{
 "pack": "norse", "id": "ravens", "name": "Ravens", "socket": "pauldrons", "centre": "minecraft:ink_sac",
 "short": "a raven perched on each shoulder, Huginn and Muninn",
 "line": "`ravens` - a raven perched on an iron shoulder plate - fitting `guard` - centre `ink_sac`",
 "intent": "Thought and Memory: a black raven perched on each shoulder, on a small iron plate. A "
           "squat body, a head thrust forward with a dark beak, and a tail sticking out behind. It "
           "faces forward, the way the wearer does, and it is blockier than a real bird.",
 "cubes": [("perch", "the iron shoulder plate the bird stands on",
            "x -9.13 .. -4.87    y 25.07 .. 25.63    z -2.33 .. 2.33"),
           ("body", "the raven's body",
            "x -8.83 .. -6.37    y 25.63 .. 27.43    z -1.83 .. 1.37"),
           ("head", "the head, thrust forward",
            "x -8.33 .. -6.87    y 27.43 .. 28.73    z -2.87 .. -1.33"),
           ("beak", "the beak",
            "x -7.93 .. -7.27    y 27.73 .. 28.33    z -3.93 .. -2.87"),
           ("tail", "the tail, sticking out behind",
            "x -8.13 .. -7.07    y 25.93 .. 26.63    z 1.37 .. 3.33")],
 "neigh": [("wither_heads", "x -9.45..-4.55, y 23.55..28.15, z -2.55..2.55", "the Nether's shoulder skulls - a figure on the shoulder at exactly your height"),
           ("beast_head", "x -10.00..-5.90, y 23.80..29.97, z -4.78..2.90", "the Wild Hunt's, reaching further forward than your beak"),
           ("blaze_bracers (vambraces)", "x -9.45..-2.65, y 15.15..20.45, z -3.35..3.35", "the tallest vambrace, worn WITH you, stopping at y 20.45 - well below your perch")],
 "fittings": ["guard"], "fit_cubes": ["perch"],
 "static": [(["body", "head", "tail"], *RAVEN), (["beak"], "#3a3a3a", "#4c4c4c", "beak grey")],
 "material": "The **perch** carries no static. It is masked `guard` and is the piece's whole material "
             "surface; the bird is static and never answers the trim.",
 "paint": "body, head, tail: base **35**, `up` **60** (the sheen is on top), `down` **25**. beak: base "
          "**50**. perch: base **130**, `up` **165**.",
},
{
 "pack": "norse", "id": "round_shield", "name": "Round Shield", "socket": "back", "centre": "minecraft:oak_boat",
 "short": "a painted round shield slung on the back, with an iron boss",
 "line": "`round_shield` - a painted round shield slung flat on the back, iron boss at its centre - fitting `guard` - centre `oak_boat`",
 "intent": "A lime-wood round shield carried on the back: a big board painted in quarters - red left "
           "and right, cream top and bottom - built from a square with two side wings and a top and "
           "bottom tab so it reads as round, and a domed iron boss at the centre. It covers the "
           "whole back from the waist to the shoulders.",
 "cubes": [("board", "the main board",
            "x -5.43 .. 5.43    y 12.57 .. 23.43    z 3.67 .. 4.27"),
           ("wing_l", "the left side of the round",
            "x -6.93 .. -5.43    y 15.07 .. 20.93    z 3.73 .. 4.23"),
           ("wing_r", "the right side",
            "x 5.43 .. 6.93    y 15.07 .. 20.93    z 3.73 .. 4.23"),
           ("top", "the top of the round",
            "x -3.43 .. 3.43    y 23.43 .. 24.93    z 3.73 .. 4.23"),
           ("bottom", "the bottom of the round",
            "x -3.43 .. 3.43    y 11.07 .. 12.57    z 3.73 .. 4.23"),
           ("boss", "the domed iron boss at the centre",
            "x -1.53 .. 1.53    y 16.47 .. 19.53    z 4.27 .. 5.37")],
 "neigh": [("turtle_shell", "x -6.00..6.00, y 15.75..24.90, z 3.10..5.60", "the Animals' shell - a big flat thing on the back at your width"),
           ("cloak", "x -5.45..5.45, y 9.63..24.85, z 2.90..4.63", "the mod's cloak - your height band, and closer to the body than you"),
           ("girdle (belt)", "x -5.86..5.86, y 11.75..14.25, z -4.00..3.86", "worn WITH you, its back face at z 3.86 crosses your board's z 3.67 in a hull test - an OVERLAP `-`, not a `!`")],
 "fittings": ["guard"], "fit_cubes": ["boss"],
 "static": [(["board", "wing_l", "wing_r"], *REDPAINT), (["top", "bottom"], *CREAMPAINT)],
 "material": "The **boss** carries no static. It is masked `guard` and is the piece's whole material "
             "surface; the painted board is static and never answers the trim.",
 "paint": "board and wings: base **120**, `south` **140** (the back face is the one you see). top and "
          "bottom: base **200**, `south` **220**. boss: base **140**, `south` **180**, `up` **170**.",
},
{
 "pack": "norse", "id": "torc", "name": "Torc", "socket": "collar", "centre": "minecraft:raw_gold",
 "short": "a twisted gold neck ring, open at the front with two knob terminals",
 "line": "`torc` - a twisted neck ring lying on the upper chest, open at the front between two knobs - fitting `guard` - centre `raw_gold`",
 "intent": "A torc: a thick twisted ring lying on the upper chest at the base of the neck, open at the "
           "front where its two ends finish in round knobs a little apart. Two arms, two knobs; it "
           "sits flat against the chest and reads as one heavy ring of gold.",
 "cubes": [("arm_l", "the left arm of the ring, across the upper chest",
            "x -4.37 .. -1.07    y 22.93 .. 23.97    z -3.77 .. -3.13"),
           ("arm_r", "the right arm",
            "x 1.07 .. 4.37    y 22.93 .. 23.97    z -3.77 .. -3.13"),
           ("knob_l", "the left terminal knob",
            "x -1.37 .. -0.23    y 22.63 .. 24.27    z -3.97 .. -3.05"),
           ("knob_r", "the right knob",
            "x 0.23 .. 1.37    y 22.63 .. 24.27    z -3.97 .. -3.05")],
 "neigh": [("fang_necklace", "x -3.20..3.20, y 21.10..24.30, z -3.90..-3.05", "the Wild Hunt's necklace - your height band exactly"),
           ("pendant", "x -3.39..3.39, y 19.00..24.46, z -3.85..-3.10", "the mod's pendant, hanging lower than you"),
           ("gorget", "x -6.50..6.50, y 19.50..25.25, z -3.75..0.75", "wider than you and wrapping the shoulders; you stay on the chest")],
 "fittings": ["guard"], "fit_cubes": ["arm_l", "arm_r", "knob_l", "knob_r"],
 "static": [(["knob_l", "knob_r"], "#d9a441", "#f0c460", "torc gold - the terminals' own gold")],
 "material": "The two **arms** carry no static; they are masked `guard` and answer the trim until a "
             "player fills the fitting. The **knobs** are static gold by default AND masked `guard`.",
 "paint": "arms: base **150**, `north` **185**, and alternate `pixels` of 150 / 190 along the length "
          "if the tool lets you, so the ring reads as twisted. knobs: base **170**, `north` **210**.",
},
{
 "pack": "norse", "id": "oath_rings", "name": "Oath Rings", "socket": "vambraces", "centre": "minecraft:raw_copper",
 "short": "three heavy arm rings stacked up the forearm over a leather wrap",
 "line": "`oath_rings` - three heavy arm rings up each forearm, the middle one a double spiral - fitting `guard` - centre `raw_copper`",
 "intent": "A warrior's arm rings: a leather wrap at the wrist, and three thick metal rings round the "
           "forearm above it with gaps between them - the middle one thicker, a spiral of two turns. "
           "The rings are the piece; the mod's `bangles` are thin and many, these are heavy and few.",
 "cubes": [("wrap", "the leather wrap at the wrist",
            "x -9.13 .. -2.87    y 11.67 .. 12.53    z -3.13 .. 3.13"),
           ("ring_lo", "the lowest ring",
            "x -9.37 .. -2.63    y 12.57 .. 13.37    z -3.37 .. 3.37"),
           ("ring_mid", "the middle ring, a double spiral, thicker",
            "x -9.47 .. -2.53    y 14.17 .. 15.13    z -3.47 .. 3.47"),
           ("ring_up", "the top ring",
            "x -9.37 .. -2.63    y 15.97 .. 16.73    z -3.37 .. 3.37")],
 "neigh": [("bangles", "x -9.85..-2.55, y 11.40..13.50, z -3.45..3.45", "the mod's bangles - thin rings low on the wrist; yours are heavy and climb the forearm"),
           ("cuffs", "x -10.07..-1.93, y 12.60..16.97, z -4.07..4.07", "wider and deeper than you"),
           ("wing_cases (pauldrons)", "x -11.02..-7.05, y 14.07..25.85, z -2.75..2.75", "worn WITH you, reaching down to y 14.07 on the outboard side - an OVERLAP `-`, not a `!`")],
 "fittings": ["guard"], "fit_cubes": ["ring_lo", "ring_mid", "ring_up"],
 "static": [(["wrap"], *LEATHER)],
 "material": "The three **rings** carry no static. They are masked `guard` and are the piece's whole "
             "material surface; the wrap is static leather.",
 "paint": "rings: base **150**, `up` **190**, `down` **110**; the middle ring `west` **175** with two "
          "`pixels` rows of 150 / 185 if the tool lets you, so it reads as two turns. wrap: base **90**.",
},
{
 "pack": "norse", "id": "seax_belt", "name": "Seax Belt", "socket": "belt", "centre": "minecraft:stone_sword",
 "short": "a leather belt with a seax hanging horizontally across the front",
 "line": "`seax_belt` - a leather belt with a sheathed seax hung horizontally across the front - fitting `guard` - centre `stone_sword`",
 "intent": "A belt with a seax: a plain leather belt round the waist with an iron buckle at the front, "
           "and a sheathed seax hanging horizontally below it across the front of the body, hilt to "
           "the right, held by two short straps from the belt. The antler hilt is pale; the sheath "
           "is dark leather.",
 "cubes": [("belt", "the leather belt round the waist",
            "x -5.33 .. 5.33    y 12.87 .. 14.13    z -3.33 .. 3.33"),
           ("buckle", "the iron buckle at the front",
            "x -0.87 .. 0.87    y 12.67 .. 14.33    z -3.73 .. -3.33"),
           ("sheath", "the seax's sheath, horizontal across the front below the belt",
            "x -4.53 .. 2.07    y 11.47 .. 12.43    z -4.03 .. -3.33"),
           ("hilt", "the antler hilt, out of the right end of the sheath",
            "x 2.07 .. 3.87    y 11.57 .. 12.33    z -3.93 .. -3.43"),
           ("strap_a", "the left strap hanging the sheath from the belt",
            "x -3.47 .. -2.83    y 12.43 .. 12.87    z -3.83 .. -3.33"),
           ("strap_b", "the right strap",
            "x 1.03 .. 1.67    y 12.43 .. 12.87    z -3.83 .. -3.33")],
 "neigh": [("pillager_belt", "x -5.35..5.35, y 12.05..15.35, z -4.35..3.85", "a pack belt at your width with something hung on it"),
           ("buckled_belt", "x -5.50..5.50, y 12.50..15.50, z -4.50..3.50", "the mod's buckled belt - the precedent for the buckle standing proud"),
           ("round_shield (back)", "x -6.93..6.93, y 11.07..24.93, z 3.67..5.37", "your own pack's shield, built in this batch, starting at z 3.67 - your belt ends at 3.33, clear")],
 "fittings": ["guard"], "fit_cubes": ["buckle"],
 "static": [(["belt", "strap_a", "strap_b"], *LEATHER), (["sheath"], "#3b2a1c", "#4f3a28", "dark leather - the sheath"),
            (["hilt"], *BONE)],
 "material": "The **buckle** carries no static. It is masked `guard` and is the piece's whole material "
             "surface.",
 "paint": "belt and straps: base **90**, `up` **110**. sheath: base **60**, `north` **75**. hilt: base "
          "**200**. buckle: base **140**, `north` **175**.\n\n**The belt is one cube right round the "
          "body.** Its inner volume is inside the chestplate; its six faces are the belt.",
},
{
 "pack": "norse", "id": "hip_axes", "name": "Hip Axes", "socket": "tassets", "centre": "minecraft:stone_axe",
 "short": "a bearded axe hanging head-up from a loop at each hip",
 "line": "`hip_axes` - a bearded axe hanging from a loop at each hip, haft down, blade back - fitting `guard` - centre `stone_axe`",
 "intent": "An axe at the hip: a leather loop at the top of the thigh, a wooden haft hanging straight "
           "down from it along the outside of the leg, and the iron head at the top of the haft "
           "with its blade pointing BACKWARDS and its beard hanging down below the blade. The "
           "head is up, the haft is down - it hangs the way an axe is carried.",
 "cubes": [("loop", "the leather loop at the top of the hip",
            "x -4.97 .. -4.37    y 11.27 .. 12.03    z -0.53 .. 0.53"),
           ("haft", "the wooden haft, hanging down the outside of the thigh",
            "x -4.87 .. -4.37    y 4.87 .. 11.27    z -0.33 .. 0.33"),
           ("head", "the iron axe head at the top of the haft, blade pointing back",
            "x -5.17 .. -4.07    y 8.27 .. 10.43    z 0.33 .. 2.63"),
           ("beard", "the beard of the axe, hanging below the blade",
            "x -5.07 .. -4.17    y 6.87 .. 8.27    z 1.77 .. 2.63")],
 "neigh": [("wing_tatters", "x -4.70..-4.40, y 6.45..10.09, z -2.29..2.35", "the Dragonslayer's strips - a thin thing hanging on the outside of the thigh, like your haft"),
           ("thigh_sheath", "x -5.35..0.85, y 3.53..11.94, z -2.80..2.80", "the mod's thigh sheath - the precedent for a weapon carried on this socket"),
           ("garters (knees)", "x -5.95..1.25, y 3.80..6.85, z -3.05..0.20", "worn WITH you; your haft crosses its box between y 4.87 and 6.85 in a hull test - an OVERLAP `-`, not a `!`")],
 "fittings": ["guard"], "fit_cubes": ["head", "beard"],
 "static": [(["haft"], *WOOD), (["loop"], *LEATHER)],
 "material": "The **head** and **beard** carry no static. They are masked `guard` and are the piece's "
             "material surface; the haft and loop are static.",
 "paint": "haft: base **110**, `west` **125**. loop: base **90**. head and beard: base **140**, `west` "
          "**170**, `south` **185** (the blade's edge faces back).",
},
{
 "pack": "norse", "id": "fur_cops", "name": "Fur Cops", "socket": "knees", "centre": "minecraft:mutton",
 "short": "an iron knee cop trimmed with a roll of wolf fur",
 "line": "`fur_cops` - an iron knee cop with a roll of grey fur over its top and a tuft above - fitting `guard` - centre `mutton`",
 "intent": "A knee cop for the cold: a plain iron cop over the front of the knee, a thick roll of "
           "wolf-grey fur lying over its top edge and standing proud of it, and a ragged tuft of fur "
           "sticking up above the roll. Iron below, fur above.",
 "cubes": [("cop", "the iron cop over the front of the knee",
            "x -3.53 .. -0.27    y 4.37 .. 6.53    z -3.73 .. -2.93"),
           ("fur", "the roll of fur over the top of the cop",
            "x -3.83 .. 0.03    y 6.53 .. 7.73    z -4.07 .. -2.93"),
           ("tuft", "the tuft standing up above the roll",
            "x -3.33 .. -0.47    y 7.73 .. 8.33    z -3.83 .. -3.13")],
 "neigh": [("poleyns", "x -4.55..-1.55, y 4.90..8.30, z -4.65..-2.65", "the mod's poleyn - your height band, and deeper"),
           ("padding", "x -4.70..0.85, y 4.40..7.60, z -3.45..-0.50", "the wayfarer's padded knee - soft where you are half fur"),
           ("hip_axes (tassets)", "x -4.73..-3.17, y 4.87..12.03, z -0.53..2.33", "your own pack's axe, built in this batch, hanging BEHIND your plane (z > -0.53) - the two never meet")],
 "fittings": ["guard"], "fit_cubes": ["cop"],
 "static": [(["fur", "tuft"], *FUR)],
 "material": "The **cop** carries no static. It is masked `guard` and is the piece's whole material "
             "surface; the fur is static.",
 "paint": "cop: base **140**, `up` **175**, `down` **100**. fur and tuft: base **130**, `north` **150**, "
          "`down` **95**.",
},
{
 "pack": "norse", "id": "winingas", "name": "Winingas", "socket": "greaves", "centre": "minecraft:brown_wool",
 "short": "wool leg wraps up the shin, held by two leather straps",
 "line": "`winingas` - three bands of wool wound up each shin, held by two vertical leather straps - fitting `inlay` - centre `brown_wool`",
 "intent": "The leg wraps of the north: three bands of undyed wool wound round the shin from the ankle "
           "to below the knee, each a hair narrower than the one below, and two leather straps "
           "running straight down over them at the front to hold them. The wool takes the trim "
           "until a player dyes it; the straps stay leather.",
 "cubes": [("wrap_lo", "the lowest band, at the ankle",
            "x -5.13 .. 0.33    y 0.37 .. 1.57    z -3.43 .. -2.33"),
           ("wrap_mid", "the middle band",
            "x -5.07 .. 0.27    y 1.77 .. 2.97    z -3.37 .. -2.43"),
           ("wrap_up", "the top band, below the knee",
            "x -4.97 .. 0.17    y 3.17 .. 4.13    z -3.27 .. -2.53"),
           ("strap_a", "the outer strap, straight down over the bands",
            "x -4.13 .. -3.47    y 0.47 .. 4.03    z -3.67 .. -3.43"),
           ("strap_b", "the inner strap",
            "x -1.03 .. -0.37    y 0.47 .. 4.03    z -3.67 .. -3.43")],
 "neigh": [("puttees", "x -5.05..0.59, y -0.70..4.45, z -4.15..-1.45", "the mod's own puttees - your closest relative; you are shallower and carry straps"),
           ("llama_wraps", "x -5.37..0.53, y 0.14..5.67, z -3.47..-2.27", "the Animals' wraps - the same three-band idea in wool"),
           ("fur_cops (knees)", "x -3.83..0.03, y 4.37..8.33, z -4.07..-2.93", "your own pack's knee, built in this batch, starting at y 4.37 - your top band ends at 4.13, clear")],
 "fittings": ["inlay"], "fit_cubes": ["wrap_lo", "wrap_mid", "wrap_up"],
 "static": [(["strap_a", "strap_b"], *LEATHER)],
 "material": "The three **wraps** carry no static. They are masked `inlay` (wool - dyed matter) and "
             "answer the trim until a player dyes them; the straps are static leather.",
 "paint": "wraps: base **190**, `north` **205**, `down` **160**. straps: base **90**.\n\n**Each wrap's "
          "back face is inside the boot.** The bands run to z -2.33 / -2.43 / -2.53 and the boots "
          "shell's front wall is at z -2.9, so the back of every band is buried and only the front "
          "and the two sides show.",
},
{
 "pack": "norse", "id": "snowshoes", "name": "Snowshoes", "socket": "spurs", "centre": "minecraft:stick",
 "short": "a snowshoe's wooden frame and webbing trailing flat behind each heel",
 "line": "`snowshoes` - a wooden snowshoe frame with rawhide webbing lying flat behind each heel - fitting `inlay` - centre `stick`",
 "intent": "A snowshoe, seen as its tail: a leather binding round the back of the heel, and from it "
           "two long wooden rails lying flat on the ground straight back from the heel, joined by "
           "two rawhide cross-cords and closed by a rounded tail piece at the end. It lies FLAT - "
           "everything is a hair above the ground.",
 "cubes": [("binding", "the leather binding round the back of the heel",
            "x -5.03 .. 1.23    y 0.67 .. 1.33    z 2.93 .. 3.43"),
           ("rail_l", "the outer wooden rail, flat on the ground going back",
            "x -3.33 .. -2.67    y 0.07 .. 0.53    z 3.43 .. 7.03"),
           ("rail_r", "the inner rail",
            "x -1.13 .. -0.47    y 0.07 .. 0.53    z 3.43 .. 7.03"),
           ("cross_a", "the front rawhide cross-cord",
            "x -2.67 .. -1.13    y 0.13 .. 0.47    z 3.67 .. 4.13"),
           ("cross_b", "the rear cross-cord",
            "x -2.67 .. -1.13    y 0.13 .. 0.47    z 5.47 .. 5.93"),
           ("tail", "the rounded tail piece closing the frame",
            "x -2.77 .. -1.03    y 0.07 .. 0.53    z 7.03 .. 7.93")],
 "neigh": [("spurs", "x -5.75..-1.50, y 2.24..7.83, z 1.50..9.76", "the mod's spur reaches further back than your tail; you lie on the ground where it stands up"),
           ("streamers", "x -5.55..0.60, y 0.28..3.55, z 0.85..7.98", "the precedent for something trailing to z 8 behind the heel"),
           ("winingas (greaves)", "x -4.13..0.33, y 0.37..4.13, z -3.67..-2.33", "your own pack's leg wraps, built in this batch, all in FRONT of the leg where you are all behind - never near")],
 "fittings": ["inlay"], "fit_cubes": ["cross_a", "cross_b"],
 "static": [(["rail_l", "rail_r", "tail"], *WOOD), (["binding"], *LEATHER)],
 "material": "The two **cross-cords** carry no static. They are masked `inlay` (rawhide - dyed matter) "
             "and are the piece's material surface until a player dyes them; the frame is static wood.",
 "paint": "rails and tail: base **120**, `up` **145**. binding: base **90**. cross-cords: base **190**, "
          "`up` **210**.",
},
]
