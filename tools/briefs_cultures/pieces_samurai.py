"""Armor Pieces: Samurai - twelve pieces, one per socket. Black lacquer (static), red odoshi lacing
(static red under an `inlay` mask, so a player re-dyes the lacing), gilt or iron hardware (material,
usually under `guard`)."""

LACQ = ("#1a1614", "#2e2724", "lacquer black - the suit's own black, with a warm brown in the light")
RED = ("#b3202a", "#d8323a", "odoshi red - the lacing cord's own red")
GOLD = ("#d4a83a", "#f1cc5a", "gilt - the maedate's gold leaf")
INDIGO = ("#2b3a6b", "#3d4f8a", "indigo cloth - the sleeve and backing cloth of a real suit")
CREAM = ("#e8dcc2", "#f4ecd8", "undyed silk - the obi's own cream")
STRAW = ("#c9b26b", "#dfcb8a", "rice straw - the waraji's own colour")

P = [
{
 "pack": "samurai", "id": "maedate", "name": "Maedate", "socket": "crest", "centre": "minecraft:sunflower",
 "short": "the gilt crescent standing up from the front of the kabuto",
 "line": "`maedate` - a gilt crescent standing up at the front of the crown - fitting `guard` - centre `sunflower`",
 "intent": "The front crest of a kabuto: a small mount plate on the front of the crown, a short stem "
           "rising from it, and a wide gilt crescent standing up on the stem - a horizontal bar with "
           "two tips curving up at its ends. Flat, thin and tall; it is a blade of gold leaf, not a "
           "horn. It faces forward and is seen edge-on from the side.",
 "cubes": [("mount", "the mount plate on the front of the crown",
            "x -1.03 .. 1.03    y 33.07 .. 33.63    z -3.97 .. -1.97"),
           ("stem", "the stem rising from the mount",
            "x -0.43 .. 0.43    y 33.63 .. 35.07    z -3.37 .. -2.57"),
           ("bar", "the crescent's horizontal bar",
            "x -3.53 .. 3.53    y 35.07 .. 35.93    z -3.27 .. -2.67"),
           ("tip_l", "the left tip curving up",
            "x -3.53 .. -2.67    y 35.93 .. 38.47    z -3.27 .. -2.67"),
           ("tip_r", "the right tip",
            "x 2.67 .. 3.53    y 35.93 .. 38.47    z -3.27 .. -2.67")],
 "neigh": [("brush_crest", "x -1.50..1.50, y 32.00..39.00, z -4.66..4.66", "the mod's crest on this socket, front-to-back where you are side-to-side"),
           ("dragon_crest", "x -0.55..0.55, y 31.88..35.60, z -3.40..3.62", "a pack crest at your stem's thinness"),
           ("coronet (brow)", "x -6.00..6.00, y 29.00..33.21, z -6.18..-2.25", "a brow piece that rises to y 33.21 at the front - your mount sits inside its box in a hull test, an OVERLAP `-`, never a `!`")],
 "fittings": ["guard"], "fit_cubes": ["bar", "tip_l", "tip_r"],
 "static": [(["bar", "tip_l", "tip_r"], *GOLD)],
 "material": "The **mount** and **stem** carry no static and no mask; they are the piece's material "
             "surface, plain metal answering the trim. The **crescent** (bar and tips) is static gold "
             "by default AND masked `guard`, so a player can make it iron or copper instead.",
 "paint": "crescent (bar, tips): base **170**, `north` **200** (the front face is the one that shines), "
          "`up` **215**. mount and stem: base **120**, `up` **150**.",
},
{
 "pack": "samurai", "id": "mempo", "name": "Mempo", "socket": "brow", "centre": "minecraft:red_dye",
 "short": "the red lacquered face mask with its moustache and hanging throat plate",
 "line": "`mempo` - a red lacquered half-mask below the eyes, moustache and throat plate - fitting `inlay` - centre `red_dye`",
 "intent": "A samurai's face mask: a red lacquered plate covering the face from just under the eyes to "
           "the chin, a nose standing out of it, a bristling grey moustache across the lip, and a "
           "laced throat plate (the yodare-kake) hanging below the chin. The eyes are open above it. "
           "It is meant to look fierce.",
 "cubes": [("face", "the lacquered plate over the lower face",
            "x -3.93 .. 3.93    y 24.37 .. 27.63    z -5.67 .. -5.07"),
           ("nose", "the nose standing out of the plate",
            "x -0.77 .. 0.77    y 26.53 .. 27.87    z -6.43 .. -5.67"),
           ("moustache", "the bristling moustache across the lip",
            "x -2.83 .. 2.83    y 25.93 .. 26.53    z -6.23 .. -5.67"),
           ("yodare", "the laced throat plate hanging below the chin",
            "x -3.37 .. 3.37    y 22.63 .. 24.37    z -5.53 .. -5.03")],
 "neigh": [("wither_mask", "x -4.10..4.10, y 25.10..31.30, z -6.45..-5.15", "a pack faceplate at your width; you sit lower and leave the eyes open"),
           ("bone_mask", "x -4.10..4.10, y 26.50..31.25, z -6.10..-5.10", "the Wild Hunt's mask - the same depth band"),
           ("barbute", "x -4.00..4.00, y 22.50..29.50, z -5.10..-4.85", "the precedent for reaching below the helmet's y 23 on this socket - your throat plate does the same")],
 "fittings": ["inlay"], "fit_cubes": ["yodare"],
 "static": [(["face", "nose"], "#8c1d1d", "#b02a2a", "mask red - the red lacquer of a real mempo"),
            (["moustache"], "#3a3431", "#55504c", "horsehair grey - the moustache")],
 "material": "The **yodare** (throat plate) carries no static. It is masked `inlay` - it is laced "
             "cord over iron - so it answers the trim until a player dyes it.",
 "paint": "face and nose: base **110**, `north` **135**, `down` **80**. moustache: base **70**. yodare: "
          "base **140**, `north` **165**, `down` **110**.\n\n**Cut nothing.** The eyes are the open "
          "space ABOVE the face plate; every face above gets paint.",
},
{
 "pack": "samurai", "id": "kuwagata", "name": "Kuwagata", "socket": "horns", "centre": "minecraft:golden_hoe",
 "short": "the flat gilt blades sweeping up from the front of the temples",
 "line": "`kuwagata` - a flat gilt blade at each temple, sweeping up and forward - fitting `guard` - centre `golden_hoe`",
 "intent": "The kabuto's antler-blades: a thin flat gilt blade standing up from the front of each temple, "
           "leaning forward as it rises, with a small iron foot where it meets the helmet. Thin in x, "
           "tall in y, so from the front it reads as two gold lines framing the maedate.",
 "cubes": [("foot", "the iron foot on the temple, where the blade is fixed",
            "x -5.57 .. -5.07    y 29.37 .. 30.43    z -3.47 .. -1.93"),
           ("blade", "the blade rising from the foot",
            "x -5.47 .. -5.07    y 30.43 .. 36.23    z -3.13 .. -2.27"),
           ("tip", "the tip, leaning forward at the top",
            "x -5.43 .. -5.11    y 36.23 .. 38.13    z -3.57 .. -2.63")],
 "neigh": [("helm_wings", "x -6.40..-5.30, y 31.14..38.37, z -0.74..6.58", "the mod's wings on this socket - the same height as you, but on the BACK half of the temple where you are on the front"),
           ("dragon_horns", "x -6.54..-4.00, y 28.20..36.93, z -1.00..2.42", "a pack horn at your height"),
           ("coronet (brow)", "x -6.00..6.00, y 29.00..33.21, z -6.18..-2.25", "a brow piece whose box your foot and blade cross in a hull test - an OVERLAP `-`, never a `!`")],
 "fittings": ["guard"], "fit_cubes": ["blade", "tip"],
 "static": [(["blade", "tip"], *GOLD)],
 "material": "The **foot** carries no static and no mask; it is the piece's material surface. The "
             "**blade** and **tip** are static gold by default AND masked `guard`.",
 "paint": "blade and tip: base **170**, `west` **200** (the outboard face), `north` **190**. foot: "
          "base **115**, `up` **145**.",
},
{
 "pack": "samurai", "id": "sode", "name": "Sode", "socket": "pauldrons", "centre": "minecraft:black_dye",
 "short": "the big flat lamellar shoulder plates hanging outboard of the shoulders",
 "line": "`sode` - a big flat lacquered plate hanging outboard of each shoulder, laced in red - fitting `inlay` - centre `black_dye`",
 "intent": "The samurai's shoulder guard: an iron cap plate lying on top of the shoulder, and a large "
           "flat rectangular plate of black lacquered lamellae hanging straight down from it on the "
           "outside of the arm, with two rows of red lacing standing proud on its outer face. It is "
           "a flat hanging slab, not a curved pauldron.",
 "cubes": [("cap", "the iron cap plate on top of the shoulder",
            "x -9.63 .. -4.37    y 25.07 .. 25.83    z -3.33 .. 3.33"),
           ("plate", "the lamellar plate hanging outboard of the arm",
            "x -10.37 .. -9.63    y 18.37 .. 25.07    z -3.33 .. 3.33"),
           ("lace_up", "the upper row of lacing on the plate's outer face",
            "x -10.57 .. -10.37    y 22.43 .. 23.07    z -3.03 .. 3.03"),
           ("lace_lo", "the lower row",
            "x -10.57 .. -10.37    y 20.03 .. 20.67    z -3.03 .. 3.03")],
 "neigh": [("lames", "x -10.85..-7.20, y 19.05..25.70, z -3.10..3.10", "the mod's own shoulder lames - the shape you are closest to, and reaching further out"),
           ("spaulders", "x -10.33..-5.75, y 20.37..25.50, z -3.50..3.50", "a plainer mod pauldron at your depth"),
           ("blaze_bracers (vambraces)", "x -9.45..-2.65, y 15.15..20.45, z -3.35..3.35", "the tallest vambrace, worn WITH you: it ends at x -9.45 and your plate starts at -9.63, so the two never meet")],
 "fittings": ["inlay"], "fit_cubes": ["lace_up", "lace_lo"],
 "static": [(["plate"], *LACQ), (["lace_up", "lace_lo"], *RED)],
 "material": "The **cap** carries no static and no mask; it is the piece's material surface, iron "
             "answering the trim. The **lacing** is static red by default AND masked `inlay`, so a "
             "player can re-dye it; the plate is static and never answers the trim.",
 "paint": "plate: base **60**, `west` **80** (the outboard face has the gloss), `down` **40**. lacing: "
          "base **150**, `west` **170**. cap: base **130**, `up` **165**.",
},
{
 "pack": "samurai", "id": "sashimono", "name": "Sashimono", "socket": "back", "centre": "minecraft:red_banner",
 "banner": True,
 "short": "a banner on a pole up the back, flying above the head - the hero piece",
 "line": "`sashimono` - a banner on a pole standing up the back, above the head - fitting `banner` + `guard` - centre `red_banner`",
 "intent": "The samurai's back banner: a laced harness across the upper back, a black lacquered pole "
           "standing straight up from it to well above the head, a short iron crossbar at the top, "
           "and the banner cloth hanging from the crossbar. It stands higher than the Village's raid "
           "banner and the cloth hangs from the bar rather than flying from the pole.",
 "cubes": [("harness", "the harness across the upper back, starting inside the chestplate and coming out through it",
            "x -1.87 .. 1.87    y 19.57 .. 22.43    z 1.73 .. 5.43"),
           ("pole", "the pole, standing straight up past the head",
            "x -0.53 .. 0.53    y 20.13 .. 39.87    z 5.23 .. 6.13"),
           ("crossbar", "the crossbar at the top, from which the cloth hangs",
            "x -3.77 .. 3.77    y 38.83 .. 39.37    z 6.23 .. 7.43"),
           ("cloth", "the banner cloth - in the bone named `banner`; 7 x 12 x 1, fixed",
            "x -3.50 .. 3.50    y 26.83 .. 38.83    z 6.33 .. 7.33")],
 "neigh": [("ominous_banner", "x -3.50..3.50, y 19.55..38.35, z 1.75..7.35", "the Village's raid banner, the precedent for a pole above the head - you go 1.5 higher, and the rig took it without complaint"),
           ("banner", "x -3.50..3.50, y 8.50..21.50, z 1.75..6.25", "the mod's own banner, mounted LOW on the back; you are its opposite"),
           ("ruff (collar)", "x -5.88..5.88, y 25.10..26.55, z -5.88..5.88", "the only bone-mate that rises above the shoulders, and it stops at y 26.55 - below your cloth")],
 "fittings": ["guard"], "fit_cubes": ["crossbar", "harness"],
 "static": [(["pole"], *LACQ)],
 "material": "The **harness** and **crossbar** carry no static; they are masked `guard` and answer "
             "the trim until a player fills the fitting. The **pole** is static black lacquer. The "
             "**cloth** is neither: plain cloth on the master, and the banner a player fits paints it.",
 "paint": "pole: base **50**, `up` **70**. harness: base **130**, `up` **170**, `down` **80**. "
          "crossbar: base **140**, `up` **175**. cloth: flat **160**, all faces.",
},
{
 "pack": "samurai", "id": "nodowa", "name": "Nodowa", "socket": "collar", "centre": "minecraft:iron_chestplate",
 "short": "the laced lamellar throat guard hanging at the collar",
 "line": "`nodowa` - a collar band with a two-tier lamellar bib hanging over the upper chest - fitting `inlay` - centre `iron_chestplate`",
 "intent": "The throat guard: an iron collar band round the base of the neck, and a bib of black "
           "lacquered lamellae in two tiers hanging from it over the upper chest, the tiers "
           "separated by a row of red lacing that stands a hair proud. Flat against the chest.",
 "cubes": [("collar", "the iron collar band at the throat",
            "x -4.63 .. 4.63    y 23.13 .. 24.57    z -3.87 .. -3.13"),
           ("bib_up", "the upper tier of the bib",
            "x -3.73 .. 3.73    y 21.03 .. 23.13    z -3.93 .. -3.17"),
           ("lace", "the row of lacing between the tiers",
            "x -3.53 .. 3.53    y 20.47 .. 21.03    z -4.03 .. -3.17"),
           ("bib_lo", "the lower tier, a little narrower",
            "x -3.23 .. 3.23    y 18.63 .. 20.47    z -3.87 .. -3.17")],
 "neigh": [("honeycomb_gorget", "x -4.73..4.73, y 17.53..24.47, z -3.93..-3.16", "the Hive's gorget - almost your envelope exactly"),
           ("wither_ribs", "x -4.28..4.28, y 17.02..23.20, z -3.95..-3.25", "the Nether's chest piece at your depth"),
           ("gorget", "x -6.50..6.50, y 19.50..25.25, z -3.75..0.75", "the mod's own gorget, which wraps the shoulders where you stay flat on the chest")],
 "fittings": ["inlay"], "fit_cubes": ["lace"],
 "static": [(["bib_up", "bib_lo"], *LACQ), (["lace"], *RED)],
 "material": "The **collar** carries no static and no mask; it is the piece's material surface. The "
             "**lace** is static red by default AND masked `inlay`; the bib tiers are static and "
             "never answer the trim.",
 "paint": "bib tiers: base **60**, `north` **80**, `down` **40**. lace: base **150**, `north` **170**. "
          "collar: base **130**, `up` **165**.",
},
{
 "pack": "samurai", "id": "kote", "name": "Kote", "socket": "vambraces", "centre": "minecraft:cyan_dye",
 "short": "the indigo armoured sleeves with a lacquered plate on the forearm",
 "line": "`kote` - an indigo cloth sleeve with a lacquered plate on the back of the forearm - fitting `guard` - centre `cyan_dye`",
 "intent": "The armoured sleeve: a tube of indigo cloth round the forearm, an iron cuff at its top just "
           "below the elbow, a black lacquered plate lying on the outside of the forearm, and a "
           "single strip of red lacing across that plate. Cloth first, metal second.",
 "cubes": [("sleeve", "the indigo cloth sleeve round the forearm",
            "x -9.23 .. -2.77    y 12.37 .. 17.73    z -3.23 .. 3.23"),
           ("cuff", "the iron cuff at the top of the sleeve",
            "x -9.33 .. -2.67    y 17.73 .. 18.27    z -3.33 .. 3.33"),
           ("plate", "the lacquered plate on the outside of the forearm",
            "x -9.53 .. -9.23    y 13.07 .. 16.63    z -2.33 .. 2.33"),
           ("lace", "the strip of lacing across the plate",
            "x -9.63 .. -9.53    y 14.57 .. 15.13    z -2.03 .. 2.03")],
 "neigh": [("chitin_bracers", "x -9.47..-2.57, y 12.43..18.67, z -3.43..3.43", "the Hive's bracer at your width and almost your height"),
           ("ravager_bracers", "x -9.55..-2.65, y 12.15..18.95, z -3.35..3.35", "a pack cuff at your width"),
           ("wing_cases (pauldrons)", "x -11.02..-7.05, y 14.07..25.85, z -2.75..2.75", "worn WITH you and reaching down to y 14.07 on the outboard side - an OVERLAP `-`, not a `!`")],
 "fittings": ["guard"], "fit_cubes": ["cuff"],
 "static": [(["sleeve"], *INDIGO), (["plate"], *LACQ), (["lace"], *RED)],
 "material": "The **cuff** carries no static. It is masked `guard` and is the piece's whole material "
             "surface; the sleeve, plate and lace never answer the trim.",
 "paint": "sleeve: base **90**, `west` **105**, `down` **70**. plate: base **60**, `west` **80**. lace: "
          "base **150**. cuff: base **130**, `up` **165**.",
},
{
 "pack": "samurai", "id": "daisho", "name": "Daisho", "socket": "belt", "centre": "minecraft:golden_sword",
 "short": "the obi sash with the long and short swords thrust through it at the left hip",
 "line": "`daisho` - an obi round the waist with the two swords thrust through it at the left hip - fitting `inlay` - centre `golden_sword`",
 "intent": "The pair of swords: a broad cream silk sash round the waist, and at the left hip two black "
           "lacquered scabbards thrust through it horizontally, pointing backwards - the long katana "
           "below, the shorter wakizashi above - with their wrapped hilts standing out forward of the "
           "hip. Seen from the front you see two hilts; from the side, two scabbards.",
 "cubes": [("obi", "the silk sash round the waist",
            "x -5.33 .. 5.33    y 12.67 .. 14.33    z -3.33 .. 3.33"),
           ("katana", "the long scabbard, along the left side pointing back",
            "x -6.13 .. -5.33    y 13.23 .. 13.87    z -3.03 .. 6.87"),
           ("wakizashi", "the short scabbard above it",
            "x -6.03 .. -5.33    y 13.97 .. 14.47    z -2.03 .. 4.07"),
           ("hilt_k", "the katana's wrapped hilt, forward of the hip",
            "x -6.07 .. -5.39    y 13.17 .. 13.93    z -5.57 .. -3.03"),
           ("hilt_w", "the wakizashi's hilt",
            "x -5.97 .. -5.39    y 13.97 .. 14.53    z -3.83 .. -2.03")],
 "neigh": [("dragon_tail", "x -5.40..5.40, y 10.45..14.90, z -2.95..6.21", "the precedent for something running off the BACK of the belt; your katana reaches 0.7 further"),
           ("sash", "x -7.25..6.00, y 5.27..16.50, z -5.00..4.00", "the mod's own sash - the precedent for reaching out to x -7 at the hip"),
           ("pinions (back)", "x -7.78..8.32, y 13.68..23.29, z 2.00..6.29", "worn WITH you; its box crosses your katana's tail in a hull test - an OVERLAP `-`, not a `!`")],
 "fittings": ["inlay"], "fit_cubes": ["obi"],
 "static": [(["obi"], *CREAM), (["katana", "wakizashi"], *LACQ)],
 "material": "The **hilts** carry no static and no mask; they are the piece's material surface (a "
             "wrapped hilt with metal fittings, answering the trim). The **obi** is static cream by "
             "default AND masked `inlay`, so a player dyes the sash; the scabbards are static black.",
 "paint": "obi: base **200**, `up` **225**, `down` **170**. scabbards: base **55**, `up` **75**, `west` "
          "**70**. hilts: base **120**, `north` **150**.\n\n**The obi is one cube right round the "
          "body.** Its inner volume is inside the chestplate; its six faces are the sash, the way "
          "`girdle` is built.",
},
{
 "pack": "samurai", "id": "kusazuri", "name": "Kusazuri", "socket": "tassets", "centre": "minecraft:red_wool",
 "short": "the laced lamellar skirt panels hanging from the waist over the hips",
 "line": "`kusazuri` - two tiers of lacquered lamellae hanging over each hip, laced in red - fitting `inlay` - centre `red_wool`",
 "intent": "The skirt of the cuirass: an iron strap over the top of the hip and, hanging from it, two "
           "tiers of black lacquered lamellae stepping outward as they go down, with a row of red "
           "lacing standing proud between the tiers and another below the lowest one. Black, red, "
           "black, red.",
 "cubes": [("strap", "the iron strap over the top of the hip",
            "x -4.47 .. 0.47    y 11.47 .. 12.13    z -2.97 .. 2.97"),
           ("tier_a", "the upper tier of lamellae",
            "x -5.07 .. 0.37    y 9.67 .. 11.47    z -3.47 .. 3.47"),
           ("lace_a", "the lacing between the tiers, standing proud",
            "x -5.23 .. 0.37    y 9.17 .. 9.67    z -3.63 .. 3.63"),
           ("tier_b", "the lower tier, a little wider",
            "x -5.17 .. 0.27    y 7.37 .. 9.17    z -3.57 .. 3.57"),
           ("lace_b", "the lowest lacing",
            "x -5.33 .. 0.27    y 6.87 .. 7.37    z -3.73 .. 3.73")],
 "neigh": [("abdomen_plates", "x -5.37..0.53, y 6.73..12.07, z -3.73..3.73", "the Hive's hip piece - the same stacked-tier idea, in the same band"),
           ("ravager_saddle", "x -5.15..-0.85, y 6.15..12.15, z -3.40..2.85", "a pack hip piece at your height band"),
           ("garters (knees)", "x -5.95..1.25, y 3.80..6.85, z -3.05..0.20", "worn WITH you, rising to y 6.85 - your lowest lacing starts at 6.87, clear by a hair")],
 "fittings": ["inlay"], "fit_cubes": ["lace_a", "lace_b"],
 "static": [(["tier_a", "tier_b"], *LACQ), (["lace_a", "lace_b"], *RED)],
 "material": "The **strap** carries no static and no mask; it is the piece's material surface. The "
             "**lacing** is static red by default AND masked `inlay`; the tiers are static and never "
             "answer the trim.",
 "paint": "tiers: base **60**, `west` **80**, `down` **40**. lacing: base **150**, `west` **170**. strap: "
          "base **130**, `up` **165**.\n\n**Each tier encloses the thigh.** Its inner face at x 0.37 / "
          "0.27 is inside the boots shell (which reaches x 1.0) and never seen.",
},
{
 "pack": "samurai", "id": "haidate", "name": "Haidate", "socket": "knees", "centre": "minecraft:leather_leggings",
 "short": "the cloth apron over the knee, set with small lacquered plates",
 "line": "`haidate` - an indigo cloth panel over each knee set with lacquered plates in a brick pattern - fitting `inlay` - centre `leather_leggings`",
 "intent": "The thigh apron's lower panel: a rectangle of indigo cloth hanging over the front of the "
           "knee, with three small black lacquered plates sewn onto it in a brick pattern - two "
           "above, one below and between them. Soft cloth with hard plates; the plates stand a "
           "little proud of the cloth.",
 "cubes": [("backing", "the indigo cloth panel over the knee",
            "x -3.77 .. -0.03    y 4.27 .. 6.73    z -3.57 .. -2.93"),
           ("plate_a", "the upper-outer plate",
            "x -3.47 .. -2.07    y 5.47 .. 6.37    z -3.87 .. -3.57"),
           ("plate_b", "the upper-inner plate",
            "x -1.73 .. -0.33    y 5.47 .. 6.37    z -3.87 .. -3.57"),
           ("plate_c", "the lower plate, between the two above",
            "x -2.63 .. -1.17    y 4.43 .. 5.33    z -3.87 .. -3.57")],
 "neigh": [("magma_cops", "x -3.55..-0.25, y 3.72..7.65, z -4.05..-2.58", "a pack knee cop at your width"),
           ("knee_studs", "x -3.15..-0.65, y 3.90..6.10, z -3.50..-3.00", "the mod's studded knee - the same idea in steel"),
           ("silverfish_greaves (greaves)", "x -5.27..0.43, y 0.24..6.13, z -4.63..-2.33", "worn WITH you and rising to y 6.13 - your panel starts at 4.27, so expect an OVERLAP note, a `-` and not a `!`")],
 "fittings": ["inlay"], "fit_cubes": ["backing"],
 "static": [(["backing"], *INDIGO), (["plate_a", "plate_b", "plate_c"], *LACQ)],
 "material": "Nothing here is bare material: the **backing** is static indigo by default AND masked "
             "`inlay`, so a player re-dyes the cloth, and the plates are static black. That is "
             "allowed because the fitting is there to change.",
 "paint": "backing: base **90**, `north` **105**. plates: base **60**, `north` **80**, `down` **40**.",
},
{
 "pack": "samurai", "id": "suneate", "name": "Suneate", "socket": "greaves", "centre": "minecraft:bamboo",
 "short": "the splinted shin guards - three iron splints on indigo cloth",
 "line": "`suneate` - three iron splints on an indigo cloth backing up each shin - fitting `guard` - centre `bamboo`",
 "intent": "The shin guard: a panel of indigo cloth wrapped over the front of the shin, with three "
           "vertical iron splints standing proud on it, evenly spaced. The splints are the hardware; "
           "the cloth is what they are sewn to. It stops below the knee.",
 "cubes": [("backing", "the cloth panel over the shin",
            "x -5.03 .. 0.23    y 0.47 .. 4.13    z -3.37 .. -2.43"),
           ("splint_a", "the outer splint",
            "x -4.43 .. -3.87    y 0.67 .. 3.93    z -3.67 .. -3.37"),
           ("splint_b", "the middle splint",
            "x -2.67 .. -2.13    y 0.67 .. 3.93    z -3.67 .. -3.37"),
           ("splint_c", "the inner splint",
            "x -0.93 .. -0.37    y 0.67 .. 3.93    z -3.67 .. -3.37")],
 "neigh": [("golem_plates", "x -3.85..0.05, y 0.35..5.45, z -3.82..-2.85", "a pack shin slab at your width; you are shorter"),
           ("puttees", "x -5.05..0.59, y -0.70..4.45, z -4.15..-1.45", "the mod's own leg wraps - deeper and wider than you"),
           ("knee_studs (knees)", "x -3.15..-0.65, y 3.90..6.10, z -3.50..-3.00", "worn WITH you and reaching down to y 3.90 - your splints end at 3.93, so expect an OVERLAP note, a `-` and not a `!`")],
 "fittings": ["guard"], "fit_cubes": ["splint_a", "splint_b", "splint_c"],
 "static": [(["backing"], *INDIGO)],
 "material": "The three **splints** carry no static. They are masked `guard` and are the piece's "
             "whole material surface; the backing is static indigo.",
 "paint": "backing: base **90**, `north` **105**, `down` **70**. splints: base **140**, `north` **175**, "
          "`up` **185**.\n\n**The backing's back face is inside the boot.** It runs z -3.37 .. -2.43 "
          "and the boots shell's front wall is at z -2.9, so its back half is buried and only the "
          "front and the two sides show.",
},
{
 "pack": "samurai", "id": "waraji", "name": "Waraji", "socket": "spurs", "centre": "minecraft:wheat",
 "short": "the straw sandal's heel cup and knotted red ties at the ankle",
 "line": "`waraji` - a straw heel cup with a cord round the ankle knotted in red at the back - fitting `inlay` - centre `wheat`",
 "intent": "The straw sandal, seen from behind: a cup of woven straw round the back of the heel, a "
           "straw loop standing off it, a cord going round the back of the ankle from the sides, "
           "and a red knot where the cord ties at the back. Straw and cord; no metal anywhere.",
 "cubes": [("heel_cup", "the woven straw cup round the back of the heel",
            "x -5.03 .. 1.23    y 0.37 .. 1.57    z 2.93 .. 3.53"),
           ("loop", "the straw loop standing off the heel cup",
            "x -2.33 .. -1.47    y 0.37 .. 0.87    z 3.53 .. 4.27"),
           ("strap", "the cord round the back of the ankle",
            "x -5.13 .. 1.33    y 2.07 .. 2.63    z 0.57 .. 3.43"),
           ("knot", "the red knot at the back",
            "x -2.53 .. -1.27    y 1.57 .. 2.67    z 3.43 .. 4.03")],
 "neigh": [("anklets", "x -5.40..1.40, y 0.95..2.20, z -3.52..3.80", "the mod's anklet - your height band, going all the way round where you stay at the back"),
           ("dragon_talons", "x -3.36..-0.49, y 0.77..2.60, z 3.00..4.66", "a pack heel piece reaching further back than you"),
           ("rowel_spurs (spurs)", "x -5.15..1.35, y 0.90..3.10, z 0.50..6.20", "the mod's spur on this same socket - never worn with you")],
 "fittings": ["inlay"], "fit_cubes": ["strap"],
 "static": [(["heel_cup", "loop"], *STRAW), (["knot"], *RED)],
 "material": "The **strap** carries no static. It is masked `inlay` (it is cord - dyed matter) and is "
             "the piece's whole material surface until a player dyes it.",
 "paint": "heel cup and loop: base **185**, `south` **200** (the back face is the one you see), `down` "
          "**150**. strap: base **140**, `south` **165**. knot: base **150**.",
},
]
