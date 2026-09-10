# Brief: Wither Ribs — the surface pass

**This is a RETROFIT, not a build.** `armorpieces_nether:wither_ribs` is finished: its geometry is correct, its
master is painted, its check is clean and it is saved in the pack. You are adding static colour **and** a fitting to it, and
changing nothing else.

A piece of **Armor Pieces: Nether** (`armorpieces_nether`) — netherite with gold hardware, the dimension worn as a body.

## Why this piece is being touched

**This piece has no static colour today.** Measured 2026-09-10: eight of the Nether pack's twelve pieces are master-only, so a wither's charcoal bone, the soul fire and the magma all render as whatever trim the wearer happens to have on. A thing whose colour IS its identity must not answer the trim.
**It also has no fitting.** The mod carries one on 51 of 66 pieces (77%), the Hive 100%, Coral 90%, Animals 87%, the Wild Hunt 86% — and this pack on **3 of 12, 25%**. The cause was upstream of every session: `pack-line.md` had an em dash in the fitting column and every brief copied it.

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
    bone, deep        #332f2b      wither bone is CHARCOAL, not ivory - it is a black skeleton
    bone, lit         #4d4841
    magma, crust      #3a1f14      the cooled shell
    magma, body       #d1440f
    magma, seam       #ff8f30      the crack that glows
    soul fire, deep   #2f8f9c      soul fire is cyan, never orange
    soul fire, lit    #5fe0ea
    blaze rod, deep   #c98d10
    blaze rod, lit    #f2cd4e
    keratin, deep     #42342a      hoof and hide
    keratin, lit      #63513f
    leather, deep     #5d4026
    leather, lit      #7d5a38
```

## What NOT to do

- **Do not touch the geometry.** No `place_cube`, no `modify_cube`, no `add_group`, no rotation.
  Not one coordinate moves. If you think a cube is wrong, say so in your report and leave it alone.
- **Do not repaint the master.** `wither_ribs.png` is finished and it is the silhouette everything else
  is clipped to. Painting sheet `part` would undo a session's work.
- **Do not change the name, recipe, loot, effects or anchors.** `armorpieces_set_part` keeps every
  field you leave out.
- **Do not build a second piece.** One session, one piece.

## Order of work

**1. Open it.**

    armorpieces_open { piece: "armorpieces_nether:wither_ribs" }

No pack paths — this piece exists and `armorpieces_open` finds it by name. If it answers
`no piece armorpieces_nether:wither_ribs`, **stop and tell me**: this Blockbench window's pack list has not been given
`packs/nether`, and that is mine to fix, not yours to work around.

**2. Confirm the cube names.** `list_outline { detail: "boxes" }`

A reopened piece names every cube `<bone>_<index>`, so the names below are what you should see.
**If any name below is not in the outline, stop and tell me** rather than painting a guess.

**3. Create the sheets.** This must come before painting — it is what creates them:

    armorpieces_set_part { fittings: ["armorpieces:guard"], static: true }

**4. Paint the static layer.** Sheet `part_static`, real colour:

    armorpieces_paint { sheet: "part_static",
                       faces: { "rib_r1_0.*": "#332f2b",
                                 "rib_r2_0.*": "#332f2b",
                                 "rib_r3_0.*": "#332f2b",
                                 "rib_l1_0.*": "#332f2b",
                                 "rib_l2_0.*": "#332f2b",
                                 "rib_l3_0.*": "#332f2b",
                                 "rib_r1_0.up": "#4d4841",
                                 "rib_r2_0.up": "#4d4841",
                                 "rib_r3_0.up": "#4d4841",
                                 "rib_l1_0.up": "#4d4841",
                                 "rib_l2_0.up": "#4d4841",
                                 "rib_l3_0.up": "#4d4841" } }

| cubes | what it is | base | lit |
|---|---|---|---|
| `rib_r1_0`, `rib_r2_0`, `rib_r3_0`, `rib_l1_0`, `rib_l2_0`, `rib_l3_0` | the six ribs | `#332f2b` | `#4d4841` on `up` |

Static is **real colour**, not greyscale — a `#rrggbb` on this sheet stays that colour. It is
painted **over** the recoloured master, so these cubes stop answering the trim, which is the point:
they are the creature, not the armor.

**5. Paint the fitting mask.** Sheet `part_guard`, flat **140**:

    armorpieces_paint { sheet: "part_guard", faces: { "base_0.*": 140 } }

140 is the value every mask in this project uses. A mask is greyscale: the value is a position on
the *fitting material's* ramp, not a colour.

The sternum plate `base_0` stays master greyscale under its new `guard` mask.

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
