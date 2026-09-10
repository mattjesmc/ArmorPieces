# Brief: Dragon Claws — the surface pass

**This is a RETROFIT, not a build.** `armorpieces_dragon:dragon_claws` is finished: its geometry is correct, its
master is painted, its check is clean and it is saved in the pack. You are adding static colour to it, and
changing nothing else.

A piece of **Armor Pieces: Dragonslayer** (`armorpieces_dragon`) — netherite plate with amethyst hardware - black hide and purple light.

## Why this piece is being touched

**This piece has no static colour today, and neither does any of its pack.** Measured 2026-09-10: Animals ships static on 100% of its pieces, the Wild Hunt 40%, Coral 40%, Nether 33% — and **Dragonslayer 0 of 12**. Every Dragonslayer master is painted right across the ramp, so her black hide and the purple membrane exist nowhere in the art: worn on iron with an iron trim, the whole outfit renders grey. `docs/plans/pack-line.md` promises "black plate and purple light" and the art has never said it.

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
- **Do not repaint the master.** `dragon_claws.png` is finished and it is the silhouette everything else
  is clipped to. Painting sheet `part` would undo a session's work.
- **Do not change the name, recipe, loot, effects or anchors.** `armorpieces_set_part` keeps every
  field you leave out.
- **Do not build a second piece.** One session, one piece.

## Order of work

**1. Open it.**

    armorpieces_open { piece: "armorpieces_dragon:dragon_claws" }

No pack paths — this piece exists and `armorpieces_open` finds it by name. If it answers
`no piece armorpieces_dragon:dragon_claws`, **stop and tell me**: this Blockbench window's pack list has not been given
`packs/dragon`, and that is mine to fix, not yours to work around.

**2. Confirm the cube names.** `list_outline { detail: "boxes" }`

A reopened piece names every cube `<bone>_<index>`, so the names below are what you should see.
**If any name below is not in the outline, stop and tell me** rather than painting a guess.

**3. Create the sheets.** This must come before painting — it is what creates them:

    armorpieces_set_part { static: true }

This piece already carries `armorpieces:guard` and that stays. Leave it out of the call and `set_part` keeps it; its mask sheet is already painted and is not yours to change.

**4. Paint the static layer.** Sheet `part_static`, real colour:

    armorpieces_paint { sheet: "part_static",
                       faces: { "base_1.*": "#141220",
                                 "claw_front_0.*": "#141220",
                                 "claw_back_0.*": "#141220",
                                 "base_1.up": "#2c2838",
                                 "claw_front_0.up": "#2c2838",
                                 "claw_back_0.up": "#2c2838" } }

| cubes | what it is | base | lit |
|---|---|---|---|
| `base_1`, `claw_front_0`, `claw_back_0` | the three wing claws | `#141220` | `#2c2838` on `up` |

Static is **real colour**, not greyscale — a `#rrggbb` on this sheet stays that colour. It is
painted **over** the recoloured master, so these cubes stop answering the trim, which is the point:
they are the creature, not the armor.

The band `base_0` stays master greyscale and keeps its `guard` mask - it is the hardware.

**5. Check.** `armorpieces_check`. Static and mask texels must land **inside the master's
silhouette** — every cube above is already painted on the master, so they will. If the check
reports texels outside it, stop and tell me.

**6. Save**, then **7. close the tab**.

## Done when

- [ ] Every sheet `set_part` created is painted. `list_textures` is the list; an empty sheet is a
      defect, not a subtlety.
- [ ] The master is untouched and the geometry is byte-for-byte what you opened.
- [ ] The check is clean. Nothing is forced.
- [ ] Saved, and the tab closed.

**Allowed to force:** nothing. If a `!` stands, stop and ask me.

## Lessons

<!-- Filled in after the session, from its report. -->
