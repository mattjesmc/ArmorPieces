"""Armor Pieces: Antiquity - twelve pieces. Red leather and horsehair are static; bronze is either
material under `guard` or static bronze under `guard` (the default look, overridable)."""

BRONZE = ("#b8783a", "#d99a5a", "bronze - the polished bronze of a real greave, warm and orange")
REDLEATHER = ("#8e2a24", "#ad3a32", "red leather - the legion's own dyed leather, and `down` #6e1f1a, its shadow")
DARKLEATHER = ("#4a2f1e", "#5f3f2a", "dark leather - the straps")
HORSEHAIR = ("#b3202a", "#d8323a", "crest red - the horsehair's own red")
HORN = ("#cfc2a0", "#e3d8bb", "horn - a ram's horn, ridged cream")
VERDIGRIS = ("#5f8f7a", "#7aa892", "verdigris - old bronze gone green")

P = [
{
 "pack": "antiquity", "id": "transverse_crest", "name": "Transverse Crest", "socket": "crest", "centre": "minecraft:leather_horse_armor",
 "short": "the centurion's horsehair crest, running ear to ear across the helm",
 "line": "`transverse_crest` - a red horsehair crest running side to side across the crown - fitting `guard` - centre `leather_horse_armor`",
 "intent": "A centurion's crest: a small bronze crest-box on the crown and a thick brush of red "
           "horsehair standing up from it and running SIDE TO SIDE, ear to ear, wider than the "
           "helmet, with the ends a little lower than the middle. The mod's `brush_crest` runs "
           "front to back; this one is its opposite and marks an officer.",
 "cubes": [("holder", "the bronze crest-box on the crown",
            "x -0.87 .. 0.87    y 33.07 .. 33.83    z -0.87 .. 0.87"),
           ("crest", "the horsehair brush, side to side",
            "x -5.93 .. 5.93    y 33.83 .. 37.47    z -0.73 .. 0.73"),
           ("end_l", "the left end, a little lower",
            "x -7.13 .. -5.93    y 34.27 .. 36.83    z -0.57 .. 0.57"),
           ("end_r", "the right end",
            "x 5.93 .. 7.13    y 34.27 .. 36.83    z -0.57 .. 0.57")],
 "neigh": [("brush_crest", "x -1.50..1.50, y 32.00..39.00, z -4.66..4.66", "the mod's crest, front to back - the piece you are the sideways answer to"),
           ("witch_hat", "x -6.45..6.45, y 32.15..39.95, z -6.15..6.15", "the widest crest piece; you reach 0.7 further at the ends"),
           ("helm_wings (horns)", "x -6.40..-5.30, y 31.14..38.37, z -0.74..6.58", "worn WITH you; your crest crosses its box between x -6.40 and -5.30 in a hull test - an OVERLAP `-`, not a `!`")],
 "fittings": ["guard"], "fit_cubes": ["holder"],
 "static": [(["crest", "end_l", "end_r"], *HORSEHAIR)],
 "material": "The **holder** carries no static. It is masked `guard` and is the piece's whole material "
             "surface; the horsehair is static and never answers the trim.",
 "paint": "crest and ends: base **120**, `up` **150**, `north` **135**, `down` **90**. holder: base **140**, "
          "`up` **175**.",
},
{
 "pack": "antiquity", "id": "corinthian_face", "name": "Corinthian Face", "socket": "brow", "centre": "minecraft:copper_helmet",
 "short": "the Corinthian helmet's bronze face with its T-shaped opening",
 "line": "`corinthian_face` - the Corinthian helmet's bronze face plate: two cheek pieces, a nasal and a brow bar - fitting `guard` - centre `copper_helmet`",
 "intent": "The face of a Corinthian helmet: two big bronze cheek pieces covering the lower face, a "
           "narrow nasal running down between the eyes, and a brow bar across the top - leaving the "
           "T-shaped opening of eyes and nose-slot. Bronze by default; the fitting can make it "
           "iron or gold.",
 "cubes": [("cheek_l", "the left cheek piece",
            "x -4.13 .. -0.77    y 24.37 .. 27.43    z -5.63 .. -5.07"),
           ("cheek_r", "the right cheek piece",
            "x 0.77 .. 4.13    y 24.37 .. 27.43    z -5.63 .. -5.07"),
           ("nasal", "the nasal, down between the eyes",
            "x -0.53 .. 0.53    y 25.57 .. 29.63    z -5.83 .. -5.07"),
           ("brow_bar", "the brow bar across the top",
            "x -4.13 .. 4.13    y 29.63 .. 30.83    z -5.63 .. -5.07")],
 "neigh": [("nasal", "x -4.50..4.50, y 26.00..30.00, z -5.75..-4.50", "the mod's nasal helm - your brow bar and nasal, without the cheeks"),
           ("great_helm", "x -4.00..4.00, y 23.25..30.25, z -5.35..-4.50", "the mod's great helm face, which covers everything where you leave the T open"),
           ("wither_mask", "x -4.10..4.10, y 25.10..31.30, z -6.45..-5.15", "a pack faceplate at your width")],
 "fittings": ["guard"], "fit_cubes": ["cheek_l", "cheek_r", "brow_bar"],
 "static": [(["cheek_l", "cheek_r", "brow_bar"], *BRONZE)],
 "material": "The **nasal** carries no static and no mask; it is the piece's material surface. The "
             "cheeks and brow bar are static bronze by default AND masked `guard`, so a player can "
             "make the face iron instead.",
 "paint": "cheeks and brow bar: base **150**, `north` **185**, `down` **110**. nasal: base **140**, `north` "
          "**175**.\n\n**Cut nothing.** The eye holes and the nose slot are the gaps between the cubes; "
          "every face above gets paint.",
},
{
 "pack": "antiquity", "id": "ammon_horns", "name": "Ammon Horns", "socket": "horns", "centre": "minecraft:cooked_mutton",
 "short": "a ram's horn curling at each temple - the horns of Ammon",
 "line": "`ammon_horns` - a ram's horn curling round each temple in a C, opening forward - fitting `guard` - centre `cooked_mutton`",
 "intent": "The horns of Ammon that Alexander wore on his coins: a ram's horn on each temple, curling "
           "in a C - from the temple up and back, down the back of the ear, forward along the jaw, "
           "and the tip curling up at the front. Four straight cubes make the curl; no rotation. "
           "Ridged horn, cream, with a small bronze base plate where it meets the helmet.",
 "cubes": [("base", "the bronze base plate on the temple",
            "x -5.47 .. -5.07    y 28.47 .. 30.83    z -1.03 .. 1.33"),
           ("seg_a", "the top of the curl, going back from the temple",
            "x -6.07 .. -5.13    y 30.07 .. 31.37    z -0.53 .. 2.67"),
           ("seg_b", "the back of the curl, coming down behind the ear",
            "x -6.13 .. -5.07    y 27.37 .. 30.07    z 1.77 .. 2.97"),
           ("seg_c", "the bottom of the curl, coming forward along the jaw",
            "x -6.07 .. -5.13    y 26.57 .. 27.37    z -0.83 .. 2.67"),
           ("tip", "the tip, curling up at the front",
            "x -5.97 .. -5.23    y 27.37 .. 28.73    z -1.43 .. -0.53")],
 "neigh": [("horns", "x -8.96..-3.61, y 29.00..38.36, z -2.00..2.00", "the Wild Hunt's horns - straight and tall where yours curl tight to the head"),
           ("dragon_horns", "x -6.54..-4.00, y 28.20..36.93, z -1.00..2.42", "a pack horn at your depth, going up where you go round"),
           ("transverse_crest (crest)", "x -7.13..7.13, y 33.07..37.47, z -0.87..0.87", "your own pack's crest, built in this batch, starting at y 33.07 - your curl tops out at 31.37, clear")],
 "fittings": ["guard"], "fit_cubes": ["base"],
 "static": [(["seg_a", "seg_b", "seg_c", "tip"], *HORN)],
 "material": "The **base** carries no static. It is masked `guard` and is the piece's whole material "
             "surface; the horn is static.",
 "paint": "horn (segments and tip): base **175**, `west` **195**, `down` **140**. base: base **140**, "
          "`west` **175**.",
},
{
 "pack": "antiquity", "id": "epomides", "name": "Epomides", "socket": "pauldrons", "centre": "minecraft:leather_helmet",
 "short": "the linothorax's shoulder flaps - a bronze yoke with red leather strips hanging outboard",
 "line": "`epomides` - a bronze yoke plate on the shoulder with three red leather strips hanging down the outer arm - fitting `guard` - centre `leather_helmet`",
 "intent": "The shoulder flaps of a hoplite's cuirass: a bronze yoke plate lying over the top of the "
           "shoulder, and three strips of stiff red leather hanging straight down from its outer "
           "edge over the upper arm, a gap between each. Bronze on top, leather down the side.",
 "cubes": [("yoke", "the bronze yoke plate over the shoulder",
            "x -9.33 .. -4.67    y 25.07 .. 25.83    z -2.83 .. 2.83"),
           ("strip_a", "the front strip hanging down the outer arm",
            "x -9.73 .. -9.33    y 20.67 .. 25.07    z -2.73 .. -1.37"),
           ("strip_b", "the middle strip, a little longer",
            "x -9.73 .. -9.33    y 20.57 .. 25.07    z -0.63 .. 0.63"),
           ("strip_c", "the back strip",
            "x -9.73 .. -9.33    y 20.67 .. 25.07    z 1.37 .. 2.73")],
 "neigh": [("epaulettes", "x -9.85..-7.20, y 22.00..25.95, z -2.60..2.60", "the mod's epaulettes - a shoulder plate at your depth"),
           ("lames", "x -10.85..-7.20, y 19.05..25.70, z -3.10..3.10", "the mod's lames reach lower and further out than your strips"),
           ("blaze_bracers (vambraces)", "x -9.45..-2.65, y 15.15..20.45, z -3.35..3.35", "the tallest vambrace, worn WITH you, ending at y 20.45 - your strips end at 20.57, clear")],
 "fittings": ["guard"], "fit_cubes": ["yoke"],
 "static": [(["strip_a", "strip_b", "strip_c"], *REDLEATHER)],
 "material": "The **yoke** carries no static. It is masked `guard` and is the piece's whole material "
             "surface; the strips are static leather.",
 "paint": "strips: base **100**, `west` **120**, `down` **70**, and a `pixels` row of 200 near the bottom "
          "of each `west` face if the tool lets you, for the bronze stud. yoke: base **145**, `up` **185**.",
},
{
 "pack": "antiquity", "id": "scutum", "name": "Scutum", "socket": "back", "centre": "minecraft:painting",
 "short": "the legionary's tall red shield slung on the back, bronze boss and spine",
 "line": "`scutum` - a tall red rectangular shield on the back with a bronze spine and boss - fitting `guard` - centre `painting`",
 "intent": "A legionary's scutum carried on the back: a tall red board covering the back from the "
           "waist to the shoulders, two side panels set a little closer to the body so the shield "
           "reads as curved, a bronze spine running down the middle and a bronze boss at its centre. "
           "Red, with the wings of the legion painted in gold on the board.",
 "cubes": [("board", "the main board",
            "x -4.43 .. 4.43    y 10.07 .. 24.43    z 3.87 .. 4.47"),
           ("wing_l", "the left side panel, set closer to the body",
            "x -6.03 .. -4.43    y 10.57 .. 23.93    z 3.37 .. 3.97"),
           ("wing_r", "the right side panel",
            "x 4.43 .. 6.03    y 10.57 .. 23.93    z 3.37 .. 3.97"),
           ("spine", "the bronze spine down the middle",
            "x -0.53 .. 0.53    y 10.07 .. 24.43    z 4.47 .. 4.77"),
           ("boss", "the bronze boss at the centre",
            "x -1.37 .. 1.37    y 15.87 .. 18.63    z 4.41 .. 5.47")],
 "neigh": [("turtle_shell", "x -6.00..6.00, y 15.75..24.90, z 3.10..5.60", "the Animals' shell - a broad thing on the back at your width"),
           ("cloak", "x -5.45..5.45, y 9.63..24.85, z 2.90..4.63", "the mod's cloak - your height band exactly"),
           ("pouch_belt (belt)", "x -7.10..6.55, y 11.05..13.60, z -3.40..5.00", "worn WITH you; its back pouches reach z 5.00 and cross your board in a hull test - an OVERLAP `-`, not a `!`")],
 "fittings": ["guard"], "fit_cubes": ["spine", "boss"],
 "static": [(["board", "wing_l", "wing_r"], *REDLEATHER)],
 "material": "The **spine** and **boss** carry no static. They are masked `guard` and are the piece's "
             "material surface; the board is static red.",
 "paint": "board and wings: base **110**, `south` **130** (the back face is the one you see), and if "
          "the tool lets you a `pixels` block of 200 on the board's `south` face either side of the "
          "spine, for the gold wings. spine and boss: base **145**, `south` **185**.",
},
{
 "pack": "antiquity", "id": "phalerae", "name": "Phalerae", "socket": "collar", "centre": "minecraft:golden_apple",
 "short": "the harness of bronze medal discs worn on the chest",
 "line": "`phalerae` - a leather harness on the chest hung with three bronze discs - fitting `guard` - centre `golden_apple`",
 "intent": "A decorated soldier's phalerae: a leather harness of one horizontal and two vertical straps "
           "on the upper chest, and three bronze discs on it - a big one at the centre, a smaller "
           "one at each side lower down. The discs stand proud of the straps. Medals, worn as armor.",
 "cubes": [("strap_h", "the horizontal strap across the chest",
            "x -4.03 .. 4.03    y 20.97 .. 21.63    z -3.61 .. -3.07"),
           ("strap_l", "the left vertical strap",
            "x -3.37 .. -2.63    y 17.47 .. 23.43    z -3.53 .. -3.13"),
           ("strap_r", "the right vertical strap",
            "x 2.63 .. 3.37    y 17.47 .. 23.43    z -3.53 .. -3.13"),
           ("disc_c", "the big central disc",
            "x -1.33 .. 1.33    y 20.07 .. 22.53    z -3.93 .. -3.53"),
           ("disc_l", "the left disc, lower",
            "x -3.87 .. -2.13    y 18.37 .. 19.83    z -3.83 .. -3.53"),
           ("disc_r", "the right disc",
            "x 2.13 .. 3.87    y 18.37 .. 19.83    z -3.83 .. -3.53")],
 "neigh": [("chain_of_office", "x -4.22..4.22, y 16.80..23.44, z -4.60..-2.60", "the mod's chain of office - the same idea, a harness with things hung on it"),
           ("bandolier", "x -5.47..5.47, y 15.66..25.20, z -3.65..-2.35", "the wayfarer's bandolier - straps on the chest at your depth"),
           ("scutum (back)", "x -6.03..6.03, y 10.07..24.43, z 3.37..5.47", "your own pack's shield, built in this batch, all BEHIND the body where you are all in front")],
 "fittings": ["guard"], "fit_cubes": ["disc_c", "disc_l", "disc_r"],
 "static": [(["strap_h", "strap_l", "strap_r"], *DARKLEATHER)],
 "material": "The three **discs** carry no static. They are masked `guard` and are the piece's whole "
             "material surface; the straps are static leather.",
 "paint": "straps: base **70**, `north` **85**. discs: base **150**, `north` **195** (the face of a "
          "medal), `up` **175**.",
},
{
 "pack": "antiquity", "id": "manica", "name": "Manica", "socket": "vambraces", "centre": "minecraft:chainmail_chestplate",
 "short": "the segmented bronze arm guard - overlapping lames down the forearm",
 "line": "`manica` - four overlapping bronze lames down each forearm on a leather strap - fitting `guard` - centre `chainmail_chestplate`",
 "intent": "The gladiator's arm guard: four bronze lames round the forearm, each a hair wider than the "
           "one above so they step outward toward the wrist, and a leather strap at the wrist below "
           "them. Metal that answers the trim; the strap is the only leather.",
 "cubes": [("lame_a", "the top lame, the narrowest",
            "x -9.13 .. -2.87    y 17.07 .. 18.23    z -3.13 .. 3.13"),
           ("lame_b", "the second lame",
            "x -9.23 .. -2.77    y 15.67 .. 17.07    z -3.23 .. 3.23"),
           ("lame_c", "the third lame",
            "x -9.33 .. -2.67    y 14.27 .. 15.67    z -3.33 .. 3.33"),
           ("lame_d", "the lowest and widest lame",
            "x -9.43 .. -2.57    y 12.87 .. 14.27    z -3.43 .. 3.43"),
           ("strap", "the leather strap at the wrist",
            "x -9.03 .. -2.97    y 12.07 .. 12.87    z -3.03 .. 3.03")],
 "neigh": [("chitin_bracers", "x -9.47..-2.57, y 12.43..18.67, z -3.43..3.43", "the Hive's bracer - the same stepped plates, in chitin"),
           ("vambraces", "x -10.00..-5.50, y 12.00..18.00, z -4.00..4.00", "the mod's own vambrace - a plate on the outside where you go all round"),
           ("epomides (pauldrons)", "x -9.73..-4.67, y 20.57..25.83, z -2.83..2.83", "your own pack's shoulder flaps, built in this batch, ending at y 20.57 - your top lame ends at 18.23, clear")],
 "fittings": ["guard"], "fit_cubes": ["lame_a", "lame_b", "lame_c", "lame_d"],
 "static": [(["strap"], *DARKLEATHER)],
 "material": "The four **lames** carry no static. They are masked `guard` and are the piece's whole "
             "material surface; the strap is static leather.",
 "paint": "lames: base **150**, `up` **190** (each lame's top edge catches light), `down` **110**. strap: "
          "base **70**.",
},
{
 "pack": "antiquity", "id": "cingulum", "name": "Cingulum", "socket": "belt", "centre": "minecraft:copper_nugget",
 "short": "the legionary's plated belt with its apron of hanging studded straps",
 "line": "`cingulum` - a plated military belt with a bronze buckle and four studded straps hanging at the front - fitting `guard` - centre `copper_nugget`",
 "intent": "The soldier's belt: a leather belt round the waist faced with bronze plates, a bronze "
           "buckle at the front, and hanging from it the apron - four narrow leather straps with "
           "bronze studs down their length and a weight at each end, swinging in front of the "
           "groin. The apron is what makes it a cingulum.",
 "cubes": [("belt", "the plated belt round the waist",
            "x -5.33 .. 5.33    y 12.97 .. 14.23    z -3.33 .. 3.33"),
           ("buckle", "the bronze buckle at the front",
            "x -0.93 .. 0.93    y 13.07 .. 14.43    z -3.73 .. -3.33"),
           ("strap_a", "the outer-left apron strap",
            "x -2.93 .. -2.27    y 8.67 .. 12.97    z -3.83 .. -3.33"),
           ("strap_b", "the inner-left strap, a little longer",
            "x -1.33 .. -0.67    y 8.37 .. 12.97    z -3.83 .. -3.33"),
           ("strap_c", "the inner-right strap",
            "x 0.67 .. 1.33    y 8.37 .. 12.97    z -3.83 .. -3.33"),
           ("strap_d", "the outer-right strap",
            "x 2.27 .. 2.93    y 8.67 .. 12.97    z -3.83 .. -3.33")],
 "neigh": [("fauld", "x -5.35..5.35, y 9.40..13.50, z -4.02..4.02", "the mod's fauld - the precedent for plates hanging below the belt line"),
           ("chain_belt", "x -5.50..5.50, y 8.60..12.80, z -3.80..3.50", "the court's chain belt, hanging to y 8.60 like your apron"),
           ("scutum (back)", "x -6.03..6.03, y 10.07..24.43, z 3.07..5.17", "your own pack's shield, built in this batch; its side panels start at z 3.37 and your belt ends at 3.33 - clear")],
 "fittings": ["guard"], "fit_cubes": ["buckle"],
 "static": [(["belt", "strap_a", "strap_b", "strap_c", "strap_d"], *REDLEATHER)],
 "material": "The **buckle** carries no static. It is masked `guard` and is the piece's whole material "
             "surface; the belt and straps are static leather (the belt's bronze plates are painted "
             "on its master as light squares, but the colour underneath is leather).",
 "paint": "belt: base **100**, `north` **120**, and alternate `pixels` of 100 / 200 along the `north` "
          "face if the tool lets you, for the bronze plates. straps: base **95**, `north` **115**, `down` "
          "**200** (the weight at the end). buckle: base **150**, `north` **190**.\n\n**The belt is one "
          "cube right round the body.** Its inner volume is inside the chestplate; its six faces are "
          "the belt.",
},
{
 "pack": "antiquity", "id": "pteruges", "name": "Pteruges", "socket": "tassets", "centre": "minecraft:brown_dye",
 "short": "the strips of red leather hanging from the waist over the thighs",
 "line": "`pteruges` - a waistband with four strips of red leather hanging over each thigh - fitting `inlay` - centre `brown_dye`",
 "intent": "The skirt of a cuirass: a cloth waistband over the top of each hip, and hanging from it "
           "four strips of stiff red leather - three down the outside of the thigh, one down the "
           "front - with a gap between each so they swing. The strips are the piece; the band is "
           "what holds them.",
 "cubes": [("band", "the waistband over the top of the hip",
            "x -4.43 .. 0.47    y 11.37 .. 12.07    z -2.93 .. 2.93"),
           ("strip_a", "the front-outer strip, down the outside of the thigh",
            "x -4.97 .. -4.37    y 6.57 .. 11.37    z -2.63 .. -1.47"),
           ("strip_b", "the middle strip, a little longer",
            "x -4.97 .. -4.37    y 6.27 .. 11.37    z -0.53 .. 0.53"),
           ("strip_c", "the back strip",
            "x -4.97 .. -4.37    y 6.57 .. 11.37    z 1.47 .. 2.63"),
           ("strip_f", "the strip down the front of the thigh",
            "x -3.73 .. -2.47    y 7.37 .. 11.37    z -3.47 .. -2.93")],
 "neigh": [("wing_tatters", "x -4.70..-4.40, y 6.45..10.09, z -2.29..2.35", "the Dragonslayer's strips - the same thing in membrane"),
           ("loin_panels", "x -3.40..-0.40, y 5.44..11.96, z -3.60..3.60", "the court's loin panels - the precedent for a panel hanging down the front"),
           ("poleyns (knees)", "x -4.55..-1.55, y 4.90..8.30, z -4.65..-2.65", "worn WITH you, rising to y 8.30 - your front strip ends at 7.37 and crosses its box in a hull test, an OVERLAP `-`, not a `!`")],
 "fittings": ["inlay"], "fit_cubes": ["band"],
 "static": [(["strip_a", "strip_b", "strip_c", "strip_f"], *REDLEATHER)],
 "material": "The **band** carries no static. It is masked `inlay` (cloth - dyed matter) and is the "
             "piece's whole material surface until a player dyes it; the strips are static leather.",
 "paint": "strips: base **100**, `west` **120** (the outboard face), `north` **115** on the front strip, "
          "`down` **200** (a bronze tip). band: base **140**, `up` **165**.\n\n**The band encloses the "
          "thigh.** Its inner face at x 0.47 is inside the boots shell (which reaches x 1.0) and "
          "never seen.",
},
{
 "pack": "antiquity", "id": "gorgon_cops", "name": "Gorgon Cops", "socket": "knees", "centre": "minecraft:ender_eye",
 "short": "a bronze knee cop bearing a gorgon's face with snakes at its sides",
 "line": "`gorgon_cops` - a bronze knee cop with a gorgoneion on it, two green snakes at the sides - fitting `guard` - centre `ender_eye`",
 "intent": "A knee cop that wards off harm: a bronze cop over the front of the knee, a gorgon's face "
           "standing proud at its centre - a flat bronze mask - and a green snake rearing at each "
           "side of the face. Bronze cop, bronze face, green snakes.",
 "cubes": [("cop", "the bronze cop over the front of the knee",
            "x -3.53 .. -0.27    y 4.37 .. 7.23    z -3.73 .. -2.93"),
           ("face", "the gorgon's face, standing proud of the cop",
            "x -2.83 .. -0.97    y 5.17 .. 6.63    z -4.13 .. -3.73"),
           ("snake_l", "the snake rearing at the outer side of the face",
            "x -3.33 .. -2.83    y 5.57 .. 6.93    z -4.03 .. -3.73"),
           ("snake_r", "the snake at the inner side",
            "x -0.97 .. -0.47    y 5.57 .. 6.93    z -4.03 .. -3.73")],
 "neigh": [("spider_cops", "x -5.63..-0.27, y 4.13..7.23, z -4.13..-2.93", "the Hive's cop - a cop with things standing off it, at your depth"),
           ("magma_cops", "x -3.55..-0.25, y 3.72..7.65, z -4.05..-2.58", "a pack knee cop at your width"),
           ("pteruges (tassets)", "x -4.97..0.47, y 6.27..12.07, z -3.47..2.93", "your own pack's strips, built in this batch: the FRONT strip starts at y 7.37, above your snakes' 6.93; the outboard strips at x -4.97..-4.37 are outside your x -3.53 - clear")],
 "fittings": ["guard"], "fit_cubes": ["cop"],
 "static": [(["face"], *BRONZE), (["snake_l", "snake_r"], *VERDIGRIS)],
 "material": "The **cop** carries no static. It is masked `guard` and is the piece's whole material "
             "surface; the face is static bronze and the snakes static green.",
 "paint": "cop: base **145**, `up` **180**, `down` **105**. face: base **160**, `north` **195**. snakes: "
          "base **120**, `north` **140**.",
},
{
 "pack": "antiquity", "id": "ocreae", "name": "Ocreae", "socket": "greaves", "centre": "minecraft:copper_boots",
 "short": "the muscled bronze greaves, a raised shin ridge between two rims",
 "line": "`ocreae` - a bronze shin plate with a raised muscle ridge, rimmed top and bottom - fitting `guard` - centre `copper_boots`",
 "intent": "The hoplite's greaves: a bronze plate over the front of the shin, sculpted with a raised "
           "ridge down its middle like the shin muscle beneath it, and a plain rim across its top "
           "and bottom edges. Bronze by default; the fitting can make it iron.",
 "cubes": [("plate", "the shin plate",
            "x -5.03 .. 0.23    y 0.67 .. 3.87    z -3.53 .. -2.47"),
           ("ridge", "the raised muscle ridge down the middle",
            "x -3.07 .. -1.73    y 0.97 .. 3.57    z -3.83 .. -3.53"),
           ("rim_up", "the top rim",
            "x -5.13 .. 0.33    y 3.87 .. 4.13    z -3.63 .. -2.37"),
           ("rim_lo", "the bottom rim",
            "x -5.13 .. 0.33    y 0.37 .. 0.67    z -3.63 .. -2.37")],
 "neigh": [("greaves", "x -4.50..0.50, y -0.20..4.80, z -3.65..-0.75", "the mod's own greaves - taller and wrapping the sides where you stay on the front"),
           ("golem_plates", "x -3.85..0.05, y 0.35..5.45, z -3.82..-2.85", "a pack shin slab at your width"),
           ("gorgon_cops (knees)", "x -3.53..-0.27, y 4.37..7.23, z -4.13..-2.93", "your own pack's knee, built in this batch, starting at y 4.37 - your top rim ends at 4.13, clear")],
 "fittings": ["guard"], "fit_cubes": ["plate", "ridge"],
 "static": [(["plate", "ridge"], *BRONZE)],
 "material": "The two **rims** carry no static and no mask; they are the piece's material surface. "
             "The plate and ridge are static bronze by default AND masked `guard`.",
 "paint": "plate: base **150**, `north` **180**. ridge: base **165**, `north` **205**. rims: base **140**, "
          "`up` **175**.\n\n**The plate's back face is inside the boot.** It runs z -3.53 .. -2.47 and "
          "the boots shell's front wall is at z -2.9, so its back half is buried.",
},
{
 "pack": "antiquity", "id": "caligae", "name": "Caligae", "socket": "spurs", "centre": "minecraft:leather_boots",
 "short": "the legionary's sandal straps - a heel cup, two ankle straps and a side lace",
 "line": "`caligae` - a leather heel cup with two straps round the ankle and a lace up the outside - fitting `inlay` - centre `leather_boots`",
 "intent": "The soldier's sandals, seen at the heel: a leather cup round the back of the heel, two "
           "narrow straps going round the back of the ankle one above the other, a lace running "
           "up the outside of the ankle over them, and a knot at the back where the top strap "
           "ties. All leather.",
 "cubes": [("heel", "the leather cup round the back of the heel",
            "x -5.03 .. 1.23    y 0.37 .. 1.73    z 2.93 .. 3.47"),
           ("strap_a", "the lower ankle strap, round the back",
            "x -5.13 .. 1.33    y 1.77 .. 2.33    z 0.37 .. 3.37"),
           ("strap_b", "the upper strap",
            "x -5.13 .. 1.33    y 2.87 .. 3.43    z 0.37 .. 3.37"),
           ("lace", "the lace up the outside of the ankle",
            "x -5.43 .. -5.13    y 0.37 .. 3.63    z 1.17 .. 1.83"),
           ("knot", "the knot at the back",
            "x -2.43 .. -1.37    y 3.43 .. 4.03    z 3.37 .. 3.97")],
 "neigh": [("anklets", "x -5.40..1.40, y 0.95..2.20, z -3.52..3.80", "the mod's anklet - a strap round the ankle at your height"),
           ("waraji", "x -5.13..1.33, y 0.37..3.87, z 0.57..4.27", "the Samurai's sandal, built in this batch - the same idea in straw, never worn with you"),
           ("ocreae (greaves)", "x -5.13..0.33, y 0.37..4.13, z -3.83..-2.37", "your own pack's greaves, built in this batch, all in FRONT of the leg where you are all behind and beside")],
 "fittings": ["inlay"], "fit_cubes": ["strap_a", "strap_b"],
 "static": [(["heel", "lace", "knot"], *DARKLEATHER)],
 "material": "The two **straps** carry no static. They are masked `inlay` (leather - dyed matter) and "
             "are the piece's material surface until a player dyes them; the rest is static leather.",
 "paint": "heel, lace and knot: base **70**, `south` **85**. straps: base **130**, `south` **155**, `up` "
          "**145**.",
},
]
