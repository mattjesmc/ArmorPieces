# Brief: Dragon Horns — the surface pass

**This is a RETROFIT, not a build.** `armorpieces_dragon:dragon_horns` is finished: its geometry is correct, its
master is painted, its check is clean and it is saved in the pack. You are adding static colour **and** a fitting to it, and
changing nothing else.

A piece of **Armor Pieces: Dragonslayer** (`armorpieces_dragon`) — netherite plate with amethyst hardware - black hide and purple light.

## Why this piece is being touched

**This piece has no static colour today, and neither does any of its pack.** Measured 2026-09-10: Animals ships static on 100% of its pieces, the Wild Hunt 40%, Coral 40%, Nether 33% — and **Dragonslayer 0 of 12**. Every Dragonslayer master is painted right across the ramp, so her black hide and the purple membrane exist nowhere in the art: worn on iron with an iron trim, the whole outfit renders grey. `docs/plans/pack-line.md` promises "black plate and purple light" and the art has never said it.
**It also has no fitting.** The mod carries one on 51 of 66 pieces (77%), the Hive 100%, Coral 90%, Animals 87%, the Wild Hunt 86% — and this pack on **2 of 12, 16%**. The cause was upstream of every session: `pack-line.md` had an em dash in the fitting column and every brief copied it.

## The three surfaces, and which cube gets which

A piece is drawn from three sheets and **they stack** — `recolour(master, static, palette)`, then
one `applyMask` per fitting:

    MATERIAL   `part`            greyscale master, recoloured through the TRIM material's ramp
    STATIC     `part_static`     real colour, painted OVER the recoloured master
    FITTING    `part_<fitting>`  greyscale mask over both, filled by the PLAYER at the smithing table

Two things follow and both decide what you do here. **Static hides material** — a static cube stops
answering the trim forever. And **an empty fitting costs nothing**: its mask is not read until a
player fills it, so a masked cube still answers the trim until then.

So the split on this piece is:

- **the creature's own body → static.** Her hide, the membrane, bone, magma, fire. Fixed identity.
- **the hardware → the fitting, and no static.** Mount, band, plate, ring, frame. It answers the
  trim while the fitting is empty and the player fills it when they choose.

Every cube is one or the other. Do not static a cube you are also told to mask, and do not mask one
you are told to static, unless this brief explicitly says both.

**The pack's palette.** Use these and no others:

```
    hide, deep        #26222c      her scale in shadow - near-black, faintly violet
    hide, lit         #3a3444      the same scale catching light
    membrane, deep    #3b3046      wing skin, stretched and dark
    membrane, lit     #5a4a70      the purple that gives the pack its name
    claw, deep        #141220      the blackest thing on the piece
    claw, lit         #2c2838
    crystal           #e070e0      end-crystal magenta
    crystal, hot      #f6c2f6
```

## What NOT to do

- **Do not touch the geometry.** No `place_cube`, no `modify_cube`, no `add_group`, no rotation.
  Not one coordinate moves. If you think a cube is wrong, say so in your report and leave it alone.
- **Do not repaint the master.** `dragon_horns.png` is finished and it is the silhouette everything else
  is clipped to. Painting sheet `part` would undo a session's work.
- **Do not change the name, recipe, loot, effects or anchors.** `armorpieces_set_part` keeps every
  field you leave out.
- **Do not build a second piece.** One session, one piece.

## Order of work

**1. Open it.**

    armorpieces_open { piece: "armorpieces_dragon:dragon_horns" }

No pack paths — this piece exists and `armorpieces_open` finds it by name. If it answers
`no piece armorpieces_dragon:dragon_horns`, **stop and tell me**: this Blockbench window's pack list has not been given
`packs/dragon`, and that is mine to fix, not yours to work around.

**2. Confirm the cube names.** `list_outline { detail: "boxes" }`

A reopened piece names every cube `<bone>_<index>`, so the names below are what you should see.
**If any name below is not in the outline, stop and tell me** rather than painting a guess.

**3. Create the sheets.** This must come before painting — it is what creates them:

    armorpieces_set_part { fittings: ["armorpieces:guard"], static: true }

**4. Paint the static layer.** Sheet `part_static`, real colour:

    armorpieces_paint { sheet: "part_static",
                       faces: { "horn1_0.*": "#26222c",
                                 "horn2_0.*": "#26222c",
                                 "horn3_0.*": "#26222c",
                                 "horn1_0.up": "#3a3444",
                                 "horn2_0.up": "#3a3444",
                                 "horn3_0.up": "#3a3444" } }

| cubes | what it is | base | lit |
|---|---|---|---|
| `horn1_0`, `horn2_0`, `horn3_0` | the three horn segments | `#26222c` | `#3a3444` on `up` |

Static is **real colour**, not greyscale — a `#rrggbb` on this sheet stays that colour. It is
painted **over** the recoloured master, so these cubes stop answering the trim, which is the point:
they are the creature, not the armor.

**5. Paint the fitting mask.** Sheet `part_guard`, flat **140**:

    armorpieces_paint { sheet: "part_guard", faces: { "base_0.*": 140 } }

140 is the value every mask in this project uses. A mask is greyscale: the value is a position on
the *fitting material's* ramp, not a colour.

The mount `base_0` stays master greyscale under its new `guard` mask.

**6. Check.** `armorpieces_check`. Static and mask texels must land **inside the master's
silhouette** — every cube above is already painted on the master, so they will. If the check
reports texels outside it, stop and tell me.

**7. Save**, then **8. close the tab**.

## Done when

- [ ] Every sheet `set_part` created is painted. `list_textures` is the list; an empty sheet is a
      defect, not a subtlety.
- [ ] The master is untouched and the geometry is byte-for-byte what you opened.
- [ ] The check is clean. Nothing is forced.
- [ ] Saved, and the tab closed.

**Allowed to force:** nothing. If a `!` stands, stop and ask me.

## Lessons

<!-- Filled in after the session, from its report. -->
