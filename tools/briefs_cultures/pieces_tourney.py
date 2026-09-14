"""Armor Pieces: Tournament - twelve pieces. Steel is material under `guard` (the joust's hardware
is meant to take the trim, like the mod's own knightly set); the heraldry - azure, gold, a rose -
is static, and cloth takes `inlay`."""

AZURE = ("#2244aa", "#3560c8", "heraldic azure - the field of the arms")
OR = ("#e0b13a", "#f3cb5c", "heraldic or - the gold of the arms")
ROSE = ("#c8395e", "#e0577a", "the favour's rose - a lady's colours")
LEATHER = ("#5a3d28", "#75523a", "oiled leather")

P = [
{
 "pack": "tourney", "id": "lion_crest", "name": "Lion Crest", "socket": "crest", "centre": "minecraft:yellow_dye",
 "short": "a golden lion rampant standing on a twisted torse over the helm",
 "line": "`lion_crest` - a gold lion standing on a twisted azure-and-gold wreath on the crown - fitting `inlay` - centre `yellow_dye`",
 "intent": "A heraldic crest: a twisted wreath (the torse) lying on the crown, and on it a golden lion "
           "standing up on its hind legs facing forward - a body, a head thrust forward, a forepaw "
           "raised in front, and a tail curling up behind. Blocky and gold; the wreath is azure and "
           "a player can re-dye it.",
 "cubes": [("torse", "the twisted wreath on the crown",
            "x -2.03 .. 2.03    y 33.07 .. 33.83    z -2.03 .. 2.03"),
           ("body", "the lion's body, standing on the wreath",
            "x -0.93 .. 0.93    y 33.83 .. 36.03    z -1.63 .. 1.77"),
           ("head", "the head, thrust forward",
            "x -0.83 .. 0.83    y 36.03 .. 37.53    z -2.37 .. -0.83"),
           ("paw", "the raised forepaw in front",
            "x -0.63 .. 0.63    y 35.33 .. 36.43    z -2.97 .. -1.63"),
           ("tail", "the tail curling up behind",
            "x -0.33 .. 0.33    y 34.63 .. 37.03    z 1.77 .. 2.47")],
 "neigh": [("spire", "x -2.50..2.50, y 32.50..40.00, z -2.50..2.50", "the mod's spire - a crest at your wreath's width, going higher"),
           ("boar_crest", "x -1.07..1.07, y 33.07..36.13, z -3.93..3.63", "the Norse boar, built in this batch - a figure on the crown like yours, never worn with you"),
           ("coronet (brow)", "x -6.00..6.00, y 29.00..33.21, z -6.18..-2.25", "a brow piece rising to y 33.21 at the front; your wreath's front edge crosses its box in a hull test - an OVERLAP `-`, never a `!`")],
 "fittings": ["inlay"], "fit_cubes": ["torse"],
 "static": [(["torse"], *AZURE), (["body", "head", "paw", "tail"], *OR)],
 "material": "Nothing here is bare material: the **torse** is static azure by default AND masked "
             "`inlay`, so a player re-dyes the wreath, and the lion is static gold. That is allowed "
             "because the fitting is there to change.",
 "paint": "torse: base **130**, `up` **160**, and alternate `pixels` of 130 / 200 round its sides if the "
          "tool lets you, for the twist. lion (body, head, paw, tail): base **170**, `up` **205**, `north` "
          "**190**, `down` **135**.",
},
{
 "pack": "tourney", "id": "tilting_grille", "name": "Tilting Grille", "socket": "brow", "centre": "minecraft:iron_trapdoor",
 "short": "a barred jousting visor - four horizontal steel bars between two posts",
 "line": "`tilting_grille` - a barred visor of four horizontal steel bars between two posts - fitting `guard` - centre `iron_trapdoor`",
 "intent": "A tournament grille: two vertical steel posts at the sides of the face and four horizontal "
           "bars running between them, evenly spaced from the brow to the chin. You look out between "
           "the bars. It is a cage for the face, all steel, and it takes the trim.",
 "cubes": [("post_l", "the left post",
            "x -4.13 .. -3.53    y 25.57 .. 30.03    z -5.63 .. -5.13"),
           ("post_r", "the right post",
            "x 3.53 .. 4.13    y 25.57 .. 30.03    z -5.63 .. -5.13"),
           ("bar_a", "the top bar, at the brow",
            "x -3.53 .. 3.53    y 29.43 .. 30.03    z -5.73 .. -5.13"),
           ("bar_b", "the second bar, at the eyes",
            "x -3.53 .. 3.53    y 28.13 .. 28.73    z -5.73 .. -5.13"),
           ("bar_c", "the third bar",
            "x -3.53 .. 3.53    y 26.83 .. 27.43    z -5.73 .. -5.13"),
           ("bar_d", "the bottom bar, at the chin",
            "x -3.53 .. 3.53    y 25.57 .. 26.13    z -5.73 .. -5.13")],
 "neigh": [("coral_visor", "x -4.13..4.13, y 25.93..30.07, z -5.83..-5.07", "the Coral's barred visor - the same grille idea in coral; yours is all steel"),
           ("frog_mouth", "x -4.00..4.00, y 24.00..31.00, z -5.60..-5.10", "the mod's own jousting helm face - the piece yours sits beside in the picker"),
           ("sallet_slit", "x -4.00..4.00, y 26.00..31.00, z -5.60..-5.10", "a mod visor at your depth")],
 "fittings": ["guard"], "fit_cubes": ["post_l", "post_r", "bar_a", "bar_b", "bar_c", "bar_d"],
 "static": [(["bar_a"], *OR)],
 "material": "Everything here is masked `guard` and answers the trim until a player fills the fitting; "
             "the **top bar** alone is static gold by default under its mask, the gilt brow-band of "
             "a tournament helm.",
 "paint": "posts and bars: base **150**, `north` **185**, `up` **195**, `down` **110**. top bar: base "
          "**175**, `north` **210**.\n\n**Cut nothing.** The gaps between the bars are the eye slots; "
          "every face above gets paint.",
},
{
 "pack": "tourney", "id": "mantling", "name": "Mantling", "socket": "horns", "centre": "minecraft:blue_dye",
 "short": "the cloth lambrequins flowing back from the helm at the temples",
 "line": "`mantling` - a cloth lambrequin at each temple flowing back and down behind the head - fitting `inlay` - centre `blue_dye`",
 "intent": "The mantling of a heraldic helm: a piece of azure cloth fixed at each temple, swagging "
           "back over the side of the helmet, trailing down behind the head and ending in a "
           "hanging tip. Four cubes stepping back and down make the flow; no rotation. Azure "
           "outside, gold lining underneath.",
 "cubes": [("root", "the cloth fixed at the temple",
            "x -5.67 .. -5.07    y 29.37 .. 31.83    z -0.63 .. 1.37"),
           ("swag", "the swag flowing back over the side of the helm",
            "x -5.77 .. -5.07    y 28.07 .. 30.57    z 1.37 .. 4.37"),
           ("trail", "the trail hanging down behind the head",
            "x -5.67 .. -5.13    y 26.67 .. 29.07    z 4.37 .. 6.57"),
           ("tip", "the hanging tip",
            "x -5.57 .. -5.23    y 25.57 .. 27.27    z 6.57 .. 7.77")],
 "neigh": [("helm_wings", "x -6.40..-5.30, y 31.14..38.37, z -0.74..6.58", "the mod's wings - on the same back half of the temple, going UP where you go back and down"),
           ("head_fins", "x -8.75..-4.66, y 26.31..31.87, z -1.40..7.71", "the Coral's fins - the precedent for trailing to z 7.7 behind the head on this socket"),
           ("browband (brow)", "x -6.48..5.50, y 26.60..30.10, z -5.45..5.45", "worn WITH you; its box crosses your root and swag in a hull test - an OVERLAP `-`, not a `!`")],
 "fittings": ["inlay"], "fit_cubes": ["root", "swag", "trail", "tip"],
 "static": [(["root", "swag", "trail", "tip"], *AZURE)],
 "material": "Nothing here is bare material: the cloth is static azure by default AND masked `inlay`, "
             "so a player re-dyes the whole mantling. Paint the `down` faces gold on the static "
             "sheet (`#e0b13a`) for the lining.",
 "paint": "all four cubes: base **120**, `west` **140** (the outboard face), `down` **170** (the lining "
          "is the light one).",
},
{
 "pack": "tourney", "id": "grandguard", "name": "Grandguard", "socket": "pauldrons", "centre": "minecraft:copper_chestplate",
 "short": "the jousting reinforce - a domed shoulder plate with an upstanding haute-piece",
 "line": "`grandguard` - a big domed shoulder plate with an upstanding neck guard and one lower lame - fitting `guard` - centre `copper_chestplate`",
 "intent": "The tilt reinforce: a big domed steel plate over the whole shoulder, an upstanding "
           "haute-piece rising from its inner edge beside the neck to catch a lance, one lower lame "
           "under the plate's outer edge, and a small azure lozenge painted on the outboard face. "
           "Heavy, smooth steel; it takes the trim.",
 "cubes": [("plate", "the domed plate over the shoulder",
            "x -10.03 .. -4.47    y 22.37 .. 25.83    z -3.53 .. 2.87"),
           ("haute", "the haute-piece standing up beside the neck",
            "x -6.53 .. -4.47    y 25.83 .. 28.33    z -2.43 .. 1.47"),
           ("lame", "the lower lame under the plate's outer edge",
            "x -9.83 .. -6.07    y 20.57 .. 22.37    z -3.03 .. 2.57"),
           ("lozenge", "the azure lozenge painted on the outboard face",
            "x -10.23 .. -10.03    y 23.07 .. 24.87    z -1.33 .. 0.87")],
 "neigh": [("spiked_pauldrons", "x -9.85..-7.20, y 22.40..28.53, z -3.10..3.10", "the mod's spiked pauldron - your height band, rising as high as your haute-piece"),
           ("spaulders", "x -10.33..-5.75, y 20.37..25.50, z -3.50..3.50", "the mod's spaulders - the plain plate you are the tournament version of"),
           ("blaze_bracers (vambraces)", "x -9.45..-2.65, y 15.15..20.45, z -3.35..3.35", "the tallest vambrace, worn WITH you, ending at y 20.45 - your lame starts at 20.57, clear")],
 "fittings": ["guard"], "fit_cubes": ["plate", "haute", "lame"],
 "static": [(["lozenge"], *AZURE)],
 "material": "The **plate**, **haute-piece** and **lame** carry no static. They are masked `guard` and "
             "are the piece's material surface; the lozenge is static azure.",
 "paint": "plate: base **150**, `up` **195**, `west` **170**, `down` **105**. haute-piece: base **150**, "
          "`up` **190**. lame: base **140**, `down` **100**. lozenge: base **130**.",
},
{
 "pack": "tourney", "id": "ecranche", "name": "Ecranche", "socket": "back", "centre": "minecraft:blue_banner",
 "short": "the small jousting shield with its lance notch, slung on the back",
 "line": "`ecranche` - a small azure jousting shield with the lance notch cut from its top corner, slung on the back - fitting `inlay` - centre `blue_banner`",
 "intent": "The jouster's little shield carried on the back: an azure board on the upper back, its "
           "top-right corner missing where the lance notch (the bouche) is cut, so the top edge is "
           "one shorter cube on the left only, and a leather guige strap across the shoulders "
           "above it. Azure by default; a player re-dyes the field.",
 "cubes": [("board", "the main board",
            "x -3.93 .. 3.93    y 13.57 .. 21.43    z 3.47 .. 4.07"),
           ("upper", "the top of the board, left side only - the notch is the missing right side",
            "x -3.93 .. -0.57    y 21.43 .. 23.03    z 3.47 .. 4.07"),
           ("guige", "the leather guige strap across the shoulders",
            "x -4.33 .. 4.33    y 23.03 .. 23.73    z 3.07 .. 3.57")],
 "neigh": [("banner", "x -3.50..3.50, y 8.50..21.50, z 1.75..6.25", "the mod's banner - a flat thing on the back at your width, hanging lower"),
           ("carapace", "x -4.75..4.75, y 15.60..24.60, z 3.10..5.25", "the Hive's back plate - your height band"),
           ("pouch_belt (belt)", "x -7.10..6.55, y 11.05..13.60, z -3.40..5.00", "worn WITH you; its back pouches reach z 5.00 and y 13.60, crossing your board's bottom in a hull test - an OVERLAP `-`, not a `!`")],
 "fittings": ["inlay"], "fit_cubes": ["board", "upper"],
 "static": [(["board", "upper"], *AZURE), (["guige"], *LEATHER)],
 "material": "Nothing here is bare material: the **board** is static azure by default AND masked "
             "`inlay`, so a player re-dyes the field; the guige is static leather. Paint a gold "
             "bend on the board's `south` face on the static sheet if the tool lets you (`#e0b13a`).",
 "paint": "board and upper: base **130**, `south` **150** (the back face is the one you see). guige: base "
          "**90**.",
},
{
 "pack": "tourney", "id": "lance_rest", "name": "Lance Rest", "socket": "collar", "centre": "minecraft:tripwire_hook",
 "short": "the steel bracket bolted to the right breast that takes the lance",
 "line": "`lance_rest` - a steel bracket on the right breast with a hook and lip projecting forward - fitting `guard` - centre `tripwire_hook`",
 "intent": "The arret: a small steel plate bolted to the RIGHT side of the upper chest, a hook "
           "projecting straight forward from it and an upturned lip at the hook's end, with a gilt "
           "bolt head on the plate. It is on one side only - the right, the lance side - and this "
           "socket is not mirrored, so build it there.",
 "cubes": [("plate", "the mount plate on the right breast",
            "x 1.07 .. 4.03    y 19.57 .. 21.83    z -3.57 .. -3.07"),
           ("hook", "the hook projecting forward",
            "x 2.37 .. 3.93    y 19.87 .. 20.63    z -5.13 .. -3.57"),
           ("lip", "the upturned lip at the end of the hook",
            "x 2.37 .. 3.93    y 20.63 .. 21.53    z -5.13 .. -4.53"),
           ("bolt", "the gilt bolt head on the plate",
            "x 1.37 .. 1.97    y 20.27 .. 20.87    z -3.77 .. -3.57")],
 "neigh": [("brooch", "x -3.50..-0.50, y 16.56..19.50, z -4.75..-1.00", "the mod's brooch - a thing on ONE side of the chest, the left; you are its opposite"),
           ("flower_brooch", "x -4.74..0.74, y 17.02..23.33, z -5.04..-3.15", "the Animals' brooch, also on the left, reaching as far forward as your lip"),
           ("bandolier", "x -5.47..5.47, y 15.66..25.20, z -3.65..-2.35", "the wayfarer's strap at your depth")],
 "fittings": ["guard"], "fit_cubes": ["plate", "hook", "lip"],
 "static": [(["bolt"], *OR)],
 "material": "The **plate**, **hook** and **lip** carry no static. They are masked `guard` and are the "
             "piece's material surface; the bolt is static gold.",
 "paint": "plate: base **150**, `north` **180**. hook and lip: base **145**, `up` **185**, `north` **175**. "
          "bolt: base **180**.",
},
{
 "pack": "tourney", "id": "favour", "name": "Favour", "socket": "vambraces", "centre": "minecraft:rose_bush",
 "short": "a lady's favour - a rose-coloured scarf knotted round the upper forearm with trailing ends",
 "line": "`favour` - a rose scarf knotted round the forearm with two ends trailing down the outside - fitting `inlay` - centre `rose_bush`",
 "intent": "A lady's favour worn into the lists: a band of rose-coloured silk tied round the forearm "
           "below the elbow, a knot standing off its outboard side, and two loose ends trailing "
           "down the outside of the arm from the knot, one longer than the other. All silk; a "
           "player re-dyes it to their own lady's colours.",
 "cubes": [("band", "the silk band round the forearm",
            "x -9.33 .. -2.67    y 15.37 .. 16.83    z -3.33 .. 3.33"),
           ("knot", "the knot on the outboard side",
            "x -9.93 .. -9.33    y 15.57 .. 16.63    z -1.03 .. 0.37"),
           ("tail_a", "the long trailing end",
            "x -9.73 .. -9.33    y 11.57 .. 15.57    z -1.53 .. -0.43"),
           ("tail_b", "the short trailing end",
            "x -9.63 .. -9.33    y 12.37 .. 15.57    z 0.37 .. 1.37")],
 "neigh": [("wraps", "x -9.56..-3.75, y 12.10..18.25, z -3.95..3.49", "the wayfarer's cloth wraps - the closest thing to you on this socket"),
           ("blaze_bracers", "x -9.45..-2.65, y 15.15..20.45, z -3.35..3.35", "a pack bracer at your band's height"),
           ("wing_cases (pauldrons)", "x -11.02..-7.05, y 14.07..25.85, z -2.75..2.75", "worn WITH you, reaching down to y 14.07 on the outboard side - an OVERLAP `-`, not a `!`")],
 "fittings": ["inlay"], "fit_cubes": ["band", "knot", "tail_a", "tail_b"],
 "static": [(["band", "knot", "tail_a", "tail_b"], *ROSE)],
 "material": "Nothing here is bare material: the whole favour is static rose by default AND masked "
             "`inlay`, so a player re-dyes it. That is allowed because the fitting is there to change.",
 "paint": "band: base **160**, `up` **185**, `down` **130**. knot: base **170**, `west` **195**. tails: base "
          "**155**, `west` **175**, `down` **125**.",
},
{
 "pack": "tourney", "id": "sword_belt", "name": "Sword Belt", "socket": "belt", "centre": "minecraft:wooden_sword",
 "short": "a leather belt with a longsword hanging vertically at the left hip",
 "line": "`sword_belt` - a leather belt with a sheathed longsword hanging straight down at the left hip - fitting `guard` - centre `wooden_sword`",
 "intent": "A knight's sword belt: a leather belt round the waist and, at the LEFT hip, a longsword in "
           "its azure scabbard hanging straight down beside the thigh, with the cross-guard lying "
           "on the belt line, the wrapped grip standing up above it and a round pommel on top. This "
           "socket is not mirrored, so the sword is on one side only.",
 "cubes": [("belt", "the leather belt round the waist",
            "x -5.33 .. 5.33    y 12.77 .. 14.33    z -3.33 .. 3.33"),
           ("scabbard", "the scabbard hanging down beside the left thigh",
            "x -6.23 .. -5.33    y 5.27 .. 12.77    z -0.83 .. 0.37"),
           ("cross", "the cross-guard, lying across the belt line",
            "x -6.03 .. -5.53    y 14.33 .. 14.87    z -2.03 .. 1.57"),
           ("grip", "the wrapped grip above the cross",
            "x -6.13 .. -5.43    y 14.87 .. 16.87    z -0.73 .. 0.27"),
           ("pommel", "the round pommel on top",
            "x -6.23 .. -5.33    y 16.87 .. 17.67    z -0.83 .. 0.37")],
 "neigh": [("thigh_sheath (tassets)", "x -5.35..0.85, y 3.53..11.94, z -2.80..2.80", "the mod's dagger at the thigh - on the LEG bone, so the check never compares you; the precedent for a weapon at the hip"),
           ("sash", "x -7.25..6.00, y 5.27..16.50, z -5.00..4.00", "the mod's sash - the precedent for a belt piece reaching x -7 and y 5"),
           ("gorget (collar)", "x -6.50..6.50, y 19.50..25.25, z -3.75..0.75", "worn WITH you, its bottom at y 19.50 - your pommel ends at 17.67, clear")],
 "fittings": ["guard"], "fit_cubes": ["cross", "pommel"],
 "static": [(["belt"], *LEATHER), (["scabbard"], *AZURE), (["grip"], "#3b2a1c", "#4f3a28", "dark leather - the wrapped grip")],
 "material": "The **cross** and **pommel** carry no static. They are masked `guard` and are the piece's "
             "material surface; the belt, scabbard and grip are static.",
 "paint": "belt: base **90**, `up` **110**. scabbard: base **120**, `west` **140**. grip: base **60**. "
          "cross and pommel: base **150**, `up` **190**.\n\n**The belt is one cube right round the "
          "body.** Its inner volume is inside the chestplate; its six faces are the belt.",
},
{
 "pack": "tourney", "id": "cuisses", "name": "Cuisses", "socket": "tassets", "centre": "minecraft:iron_leggings",
 "short": "plate thigh guards - a ridged plate over the front and outside of the thigh, one lame below",
 "line": "`cuisses` - a steel thigh plate with a raised rib and one articulated lame below it - fitting `guard` - centre `iron_leggings`",
 "intent": "Plate cuisses: a steel plate wrapping the front and outside of the thigh from the hip to "
           "above the knee, a raised rib running down its front, and one narrower lame hanging "
           "under its bottom edge. Smooth tournament steel that takes the trim, with a small gold "
           "stud at the top of the rib.",
 "cubes": [("plate", "the thigh plate, front and outside",
            "x -4.83 .. 0.37    y 6.87 .. 11.73    z -3.53 .. 1.57"),
           ("rib", "the raised rib down the front",
            "x -3.37 .. -1.03    y 7.37 .. 11.23    z -3.83 .. -3.53"),
           ("lame", "the lame under the bottom edge",
            "x -4.73 .. 0.27    y 6.07 .. 6.87    z -3.43 .. 1.47"),
           ("stud", "the gold stud at the top of the rib",
            "x -2.53 .. -1.87    y 10.57 .. 11.13    z -4.03 .. -3.83")],
 "neigh": [("tassets", "x -4.60..-1.25, y 5.18..12.25, z -4.68..-0.90", "the mod's own tassets - your height band, hanging where you wrap"),
           ("ravager_saddle", "x -5.15..-0.85, y 6.15..12.15, z -3.40..2.85", "a pack hip piece wrapping the thigh like you"),
           ("boot_cuffs (greaves)", "x -5.51..1.66, y 8.50..9.82, z -3.56..3.61", "worn WITH you; its cuff crosses your plate in a hull test - an OVERLAP `-`, not a `!`")],
 "fittings": ["guard"], "fit_cubes": ["plate", "rib", "lame"],
 "static": [(["stud"], *OR)],
 "material": "The **plate**, **rib** and **lame** carry no static. They are masked `guard` and are the "
             "piece's material surface; the stud is static gold.",
 "paint": "plate: base **150**, `north` **175**, `west` **165**, `down` **110**. rib: base **165**, `north` "
          "**200**. lame: base **140**, `down` **100**. stud: base **180**.\n\n**The plate's inner face "
          "at x 0.37 is inside the leggings shell** (which reaches x 0.5) and never seen.",
},
{
 "pack": "tourney", "id": "rondel_cops", "name": "Rondel Cops", "socket": "knees", "centre": "minecraft:iron_horse_armor",
 "short": "a knee cop with a big round rondel plate standing off its outer side",
 "line": "`rondel_cops` - a steel knee cop with a round rondel standing off its outer side, gilt boss at its centre - fitting `guard` - centre `iron_horse_armor`",
 "intent": "A knee cop with its rondel: a steel cop over the front of the knee, a flat round plate "
           "standing off the outer side of the knee to guard the joint, and a gold boss at the "
           "centre of that plate. Cop and rondel take the trim; the boss is gold.",
 "cubes": [("cop", "the cop over the front of the knee",
            "x -3.53 .. -0.27    y 3.37 .. 5.93    z -3.73 .. -2.93"),
           ("rondel", "the round plate standing off the outer side of the knee",
            "x -5.13 .. -4.83    y 3.57 .. 5.77    z -3.33 .. -1.13"),
           ("boss", "the gold boss at the rondel's centre",
            "x -5.63 .. -5.13    y 4.27 .. 5.07    z -2.63 .. -1.83")],
 "neigh": [("winged_cops", "x -5.99..-0.45, y 4.50..7.60, z -3.87..-1.53", "the mod's winged cops - the precedent for a plate standing off the side of the knee"),
           ("poleyns", "x -4.55..-1.55, y 4.90..8.30, z -4.65..-2.65", "the mod's poleyns - higher on the knee than you"),
           ("soul_greaves (greaves)", "x -4.06..-0.15, y 0.35..8.37, z -3.12..-2.62", "worn WITH you and rising to y 8.37 - your cop crosses it in a hull test, an OVERLAP `-`, not a `!`")],
 "fittings": ["guard"], "fit_cubes": ["cop", "rondel"],
 "static": [(["boss"], *OR)],
 "material": "The **cop** and **rondel** carry no static. They are masked `guard` and are the piece's "
             "material surface; the boss is static gold.",
 "paint": "cop: base **150**, `up` **190**, `down` **105**. rondel: base **150**, `west` **185**. boss: "
          "base **180**, `west` **210**.",
},
{
 "pack": "tourney", "id": "schynbalds", "name": "Schynbalds", "socket": "greaves", "centre": "minecraft:chainmail_leggings",
 "short": "shin plates strapped over the mail - a front plate, an outer wing and a top rim",
 "line": "`schynbalds` - a steel shin plate over the front of the shin with an outer wing and a rimmed top - fitting `guard` - centre `chainmail_leggings`",
 "intent": "The early plate greave: a steel plate over the front of the shin from the ankle to below "
           "the knee, a narrower wing plate down the outside of the shin, and a rolled rim across "
           "the top edge of both. Steel that takes the trim; the rim is gilt.",
 "cubes": [("plate", "the front shin plate",
            "x -4.93 .. 0.17    y 1.07 .. 2.93    z -3.53 .. -2.93"),
           ("wing", "the wing plate down the outside of the shin",
            "x -5.33 .. -4.83    y 1.07 .. 2.93    z -2.93 .. 1.37"),
           ("rim", "the rolled rim across the top",
            "x -5.23 .. 0.27    y 2.93 .. 3.23    z -3.63 .. 1.47")],
 "neigh": [("greaves", "x -4.50..0.50, y -0.20..4.80, z -3.65..-0.75", "the mod's own greaves - taller than you, wrapping the same way"),
           ("dragon_scales", "x -3.50..-0.30, y 0.78..4.38, z -3.52..-3.05", "a pack shin plate at your depth"),
           ("knee_studs (knees)", "x -3.15..-0.65, y 3.90..6.10, z -3.50..-3.00", "worn WITH you, starting at y 3.90 - your rim ends at 3.23, clear")],
 "fittings": ["guard"], "fit_cubes": ["plate", "wing"],
 "static": [(["rim"], *OR)],
 "material": "The **plate** and **wing** carry no static. They are masked `guard` and are the piece's "
             "material surface; the rim is static gold.",
 "paint": "plate: base **150**, `north` **180**, `down` **110**. wing: base **145**, `west` **175**. rim: "
          "base **180**, `up` **215**.",
},
{
 "pack": "tourney", "id": "sabatons", "name": "Sabatons", "socket": "spurs", "centre": "minecraft:golden_boots",
 "short": "plate foot armor with a long pointed poulaine toe and a heel plate",
 "line": "`sabatons` - a plate over the toes drawn out into a long point, and a heel plate behind - fitting `guard` - centre `golden_boots`",
 "intent": "Plate sabatons with the fashionable toe: a steel plate over the front of the foot, a long "
           "narrow point running forward from it well past the toes, and a steel plate cupping the "
           "back of the heel with a gilt strap-buckle on it. The point is the joke and the "
           "silhouette; it is longer than the foot.",
 "cubes": [("toe", "the plate over the front of the foot",
            "x -4.93 .. 0.23    y 0.07 .. 0.97    z -5.03 .. -2.93"),
           ("point", "the long pointed toe running forward",
            "x -2.57 .. -1.23    y 0.17 .. 0.87    z -7.03 .. -5.03"),
           ("heel", "the plate cupping the back of the heel",
            "x -4.93 .. 0.23    y 0.17 .. 1.63    z 2.93 .. 3.47"),
           ("buckle", "the gilt buckle on the heel plate",
            "x -2.47 .. -1.33    y 0.57 .. 1.23    z 3.47 .. 3.77")],
 "neigh": [("hoglin_hooves", "x -5.12..1.32, y 0.12..3.72, z -3.18..4.32", "the Nether's hooves - the precedent for a spurs piece that wraps the whole foot, front and back"),
           ("shin_spikes (greaves)", "x -2.90..-0.90, y 0.90..3.75, z -5.51..-2.95", "the Wild Hunt's spikes reach z -5.51 in front of the shin; your point goes to -7.03, lower down"),
           ("puttees (greaves)", "x -5.05..0.59, y -0.70..4.45, z -4.15..-1.45", "worn WITH you; your toe plate crosses its box in a hull test - an OVERLAP `-`, not a `!`")],
 "fittings": ["guard"], "fit_cubes": ["toe", "point", "heel"],
 "static": [(["buckle"], *OR)],
 "material": "The **toe**, **point** and **heel** carry no static. They are masked `guard` and are the "
             "piece's material surface; the buckle is static gold.",
 "paint": "toe and heel: base **150**, `up` **190**, `north` **175**, `south` **175**. point: base **155**, "
          "`up` **195**, and a `pixels` gradient along its length from 195 at the foot to 150 at the "
          "tip if the tool lets you. buckle: base **180**.",
},
]
