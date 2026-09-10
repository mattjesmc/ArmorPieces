# Template: a brief a weaker model can build from

> **Not a brief. The shape of one.** Copy this to `<piece>.md` and fill every field. The
> `part-author-qwen` agent is forbidden from opening plans, other briefs or the candidate tables, so
> **anything left implicit here is simply absent** from the session that builds the piece. The older
> briefs in this folder assume a reader that can go and look things up; this one assumes a reader
> that cannot.
>
> The rule while filling it in: **no sentence may require a lookup.** "Sit it above the circlet"
> fails. "Its underside starts at `y = 30.15`; the circlet's top is `30.0`" passes.
>
> Delete this block and every `<!-- -->` note when the brief is real.

# Brief: <Display Name>

A piece of **<pack display name>** (`<namespace>`), <one sentence on the pack's look — the material
and the light, not its history>.

<!-- One short paragraph, and no more, on where this piece sits among its pack siblings. Name them
     only if this piece has to clear them; if so, give their numbers here rather than the name of a
     file that holds them. -->

## What to create

    name:          <part_id>
    anchor:        <socket>
    namespace:     <namespace>
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\<pack>\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\<pack>\resourcepack

<!-- Always absolute, always both pack paths. Omitting them writes the piece into the mod itself. -->

Then, before painting:

    armorpieces_set_part { name: "<Display Name>",
                           recipe: { centre: "<minecraft:item>", craftable: <true|false> } }

**Fittings:** <the list, with which are masked, AND the substance each one is — or "none", with the
one-line reason this piece is a single substance all through>.
**Static layer:** <no — one sheet, the greyscale master | yes, for: what keeps its own colour, AND
which faces it does NOT cover, so the material surface below is named rather than left to chance>.
**Effects / loot:** <none | exactly what>.

<!-- State the negatives explicitly. "No fittings, no static layer, no effects, no loot" stops a
     session inventing one. Say what the reply will look like when it is right, e.g.
     "The reply will say static_created: false and sheets_created: [] - that is correct." -->

<!-- THREE SURFACES, AND THEY STACK. A piece is not "a texture"; it is up to three:

       MATERIAL  `part`            greyscale, recoloured through the TRIM material's ramp
       STATIC    `part_static`     real colour, painted OVER the recoloured master
       FITTING   `part_<fitting>`  a greyscale mask over both, filled by the PLAYER

     The bake is recolour(master, static, palette) then applyMask per fitting. So static HIDES
     material, and an EMPTY fitting costs nothing - its mask is not read until a player fills it,
     which makes a static layer under a mask the piece's default look and the fitting an override.

     THE RULE: every piece must leave the player at least one surface to change - master showing,
     or a fitting. Static over the whole silhouette AND no fitting is INERT: identical on netherite
     and leather, under every trim, forever. `tools/check_surfaces.py` fails on it. Five pieces
     shipped that way before it existed - ghast_tendrils, hoglin_hair, strider_hair, fox_ears and
     axolotl_frills.

     So decide the two together, and write both down: if the static covers everything, the piece
     needs a fitting; if there is no fitting, the static must leave material showing. -->

<!-- FITTINGS ARE THE NORMAL CASE AND "none" IS THE ONE THAT NEEDS DEFENDING. A fitting is the part
     of the piece made of a DIFFERENT SUBSTANCE from the rest, and it is the piece's only
     customisable surface - the player fills it at the advanced smithing table. Four exist and a
     pack may not invent a fifth:

       guard     metals   hardware: bands, clasps, buckles, rims, ferrules, studs, caps, mounts
       gemstone  gems     a set stone: a jewel, an eye, a pommel, a glowing core
       inlay     any dye  dyed matter: cloth, leather, cord, ribbon, quilting, membrane
       banner    a banner an actual flying banner; needs its own `banner` bone, nothing else

     Measured 2026-09-10: the mod carries a fitting on 51 of 66 pieces (77%), Coral 90%, Animals
     87%, the Wild Hunt 86%, the Hive 100% - and DRAGONSLAYER 2 of 12 (16%) and NETHER 3 of 12
     (25%). The two outliers are exactly the two packs built from briefs, and the cause was this
     field: `pack-line.md`'s piece tables carry an em dash in the fitting column, the briefs copied
     it, and the sessions obeyed. Ten Dragonslayer pieces shipped as one flat greyscale master with
     no hardware and nothing for a player to fill.

     So: before you write "none" here, name the piece's substances out loud. A strap, a rim, a
     buckle, a mount, a cord, a set stone or a membrane is a fitting, and almost every piece has
     one. "none" is right only for a thing that is genuinely one material all through - a plain
     steel plate, a bare feather, a solid horn - and if you write it, write why.

     Then say which faces the mask covers, down in ## Paint. A fitting declared and never painted
     is worse than no fitting: it creates an empty sheet the game will render as nothing. -->

## The rig, in Blockbench coordinates

    <body box>              x .. ..      y .. ..      z .. ..
    <shell (+1.0)>          x .. ..      y .. ..      z .. ..
    the <socket> anchor     (x, y, z)

Front is **negative z**. <Mirrored socket: model the negative-x side only; the game mirrors it.>

<!-- Give the anchor as a literal triple. Say what the anchor sitting on a body face implies:
     whether the first cube is expected to start inside the shell and come out of it. -->

## Shape

<Two or three sentences of intent — what a player sees, and what this piece is deliberately NOT.>

- One bone `base` at the anchor (rename the starter `main`; never call a bone `root`; remove the
  starter cube).
- <Each bone: its name, its parent, its purpose, and a literal coordinate range for its cube(s).>
- <Cube budget: "N cubes in total is the budget; N+1 if <specific thing> earns its own.">

<!-- TAPER THE AXIS YOU ROTATE ABOUT. A rotation about Z preserves every z, so two segments given the
     same z lane keep their north/south faces coplanar no matter what angles you set, and they
     z-fight where they overlap. Same for X and x. ghast_tendrils shipped with this defect because
     the brief tapered only x; the check cannot catch it (no planes are emitted for a rotated chain,
     and a part is never compared with itself - docs/plans/coplanar-check.md), so the brief is the
     only place it can be prevented. Give each segment its own inset on EVERY axis. -->

**Signs, worked out once.** <For every rotation the piece needs, state the axis, the sign, and what
that sign does in words — "a positive θ about X swings the tip toward +z, which is backward". Getting
a sign wrong is the failure that costs a rebuild, and the session must not have to derive it.>

**Envelope budget.** Stay inside `x .. ..`, `y .. ..`, `z .. ..`.

**The same budget in the check's own frame** — always give both. The brief speaks Blockbench world
coordinates; the check answers **bone-local, +Y down, from the BONE'S PIVOT**, which is not the top
of the bone's box: the arm's pivot is at Blockbench `y = 22`, the head's at `24`. Make the session
compare like with like rather than convert:

    x  .. ..      y  .. ..      z  .. ..

<!-- Derive the conversion from the check's own neighbour table, which prints both frames side by
     side - a neighbour's two y ranges sum to twice the pivot height. Do not assume the box top.
     Getting this wrong makes a conformant piece look two units out; it has already happened once. -->

<!-- BEFORE SHIPPING THIS BRIEF, COMPUTE THE WORST CORNER AND CHECK IT AGAINST THIS BUDGET.
     Not by eye - actually run the numbers, for every rotated bone, at the END of every chain:

       chain the pivots:   each child's pivot moves by its parent's rotation
       then the corner:    Dx' = Dx*cos(t) - Dy*sin(t),  Dy' = Dx*sin(t) + Dy*cos(t)
                           about X:  Dy' = Dy*cos(t) - Dz*sin(t),  Dz' = Dy*sin(t) + Dz*cos(t)
       t is CUMULATIVE down a compounded chain, and the last segment's outboard far corner is
       almost always the extreme.

     A budget that the brief's own coordinates and angles cannot meet is the worst thing a brief can
     contain: it is a contradiction the session cannot resolve, and a careful one will stop and ask
     while a careless one will silently pick a side. This has already happened TWICE - ghast_tendrils
     (caught mid-build by the session, brief corrected) and hoglin_hair (shipped, built, and only
     found afterwards, where a lane was outside the wall before any rotation at all). -->


<!-- For a mirrored socket also give the pair span and its ceiling: "the pair spans 2 × |x|, and the
     check compares it against the 18 the shoulders span; at x = -8.9 the pair spans 17.8." -->

**Neighbours you must clear.** <Piece name — its envelope — the wall it puts on you, and how much
slack that leaves. Numbers, not names of files.>

## Paint

<The master's greys as a plan: base value, which faces are lighter or darker, where a
[top, bottom] gradient runs. Values are positions on the trim ramp, so describe them as light/mid/
dark with actual numbers, not as colours.>

<Static layer, if any: the actual colours and which faces.>
<Each mask, if any: which faces, which grey.>

## Done when

- [ ] The check is clean, or every `!` left standing is one this brief allows.
- [ ] Envelope inside the budget above; pair span reported.
- [ ] **Every sheet `set_part` created is painted** — master, static if asked for, and one mask per
      masked fitting. `list_textures` is the list; an unpainted sheet is a defect, not a subtlety.
- [ ] Saved, and the tab closed.

**Allowed to force:** <the specific `!` lines that are acceptable for this piece, and why — or
"nothing; if a `!` stands, stop and ask">.

## Lessons

<!-- Left EMPTY for the building session's report to be written into afterwards by the follow-up
     pass. The qwen agent has no Write tool and cannot fill this in itself. -->
