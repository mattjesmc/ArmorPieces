# Brief: Ghast Tendrils

A piece of **Armor Pieces: Nether** (`armorpieces_nether`) — netherite with gold hardware, the
dimension worn as a body. Other pieces of the pack exist on the forearms, temples and crown; none is
on your bone and none concerns you.

From the `tassets` row of the Nether table:

> `ghast_tendrils` — pale tentacles hanging from the hips — no fitting — centre `ghast_tear`.

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          ghast_tendrils
    anchor:        tassets
    namespace:     armorpieces_nether
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\nether\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\nether\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

Then, before you paint anything:

    armorpieces_set_part { name: "Ghast Tendrils",
                           static: true,
                           recipe: { centre: "minecraft:ghast_tear", craftable: true } }

`minecraft:ghast_tear` is confirmed free — no other template recipe uses it.

**Fittings:** none. **Effects:** none. **Loot:** none — recipe only.
**Static layer: yes.** A ghast's tentacles are their own dead pale white and do not take the armor's
trim colour, so this piece has **two sheets**: the greyscale master `part`, and `part_static` which
keeps real colour. The reply to `set_part` will say `static_created: true` and `sheets_created: []`.

## The rig, in Blockbench coordinates

`tassets` is a **mirrored** socket on the hips, riding on the legs: model **one** side — the
**negative x** side — and the game mirrors it to the other hip.

    left leg box            x −4 .. 0     y 0 .. 12     z −2 .. 2
    leggings shell (+1.0)   x −5 .. 1     y 0 .. 13     z −3 .. 3
    the tassets anchor      (−1.9, 10, 0)

**Check the anchor before you build.** The reply to `armorpieces_new` prints it. It should read
`(−1.9, 10, 0)` in Blockbench coordinates — the leg's own pivot, which is at `x = −1.9`, **not** the
centre of the leg box. **If it prints anything else, stop and tell me.**

Front is **negative z**. On this side **`west` is the outboard face** and `north` is the front.

A face lying exactly in a shell plane — `x = −5`, `z = ±3` — z-fights. The numbers below are off the
round value on purpose; keep them.

## Shape

Three long tentacles hanging down the outside of the thigh, the way a ghast's trail below it. **They
hang, taper and curl slightly outward — they do not branch.** Limp and heavy, not stiff.

- One bone `base` at the anchor (rename the starter `main`; never call a bone `root`; remove the
  starter cube).
- **Three tentacles, each of two segments**, so six bones and six cubes. Each tentacle's lower
  segment is a **child of its own upper segment**, and each upper segment is a child of `base`.
  Build every segment straight down and unrotated first, then aim them.

  Unrotated, the segments sit at these coordinates. All three tentacles share the same `x` and `y`;
  only `z` differs, which is what sets them side by side along the thigh:

        upper segments    x −4.55 .. −3.45      y 7.25 .. 9.65
        lower segments    x −4.45 .. −3.55      y 4.85 .. 7.45

  and the `z` lanes, front to back — **the lower segments are 0.10 narrower per side than the
  uppers, and that inset is not cosmetic**: these bones rotate about Z, a Z rotation preserves `z`,
  so segments sharing a z range would keep their north and south faces in the same planes at any
  angle and z-fight where they overlap. Taper the axis you rotate about.

        tendril_f    upper z −2.30 .. −1.15     lower z −2.20 .. −1.25
        tendril_m    upper z −0.55 ..  0.60     lower z −0.45 ..  0.50
        tendril_b    upper z  1.20 ..  2.35     lower z  1.30 ..  2.25

  The lower segments overlap their uppers by 0.2 in y, which the ranges above already do. Name the
  bones `tendril_f_up` / `tendril_f_lo` and so on.

- **Six cubes is the budget.** No seventh.

**Then aim it.** Each bone's pivot goes at its **top** edge (the near end), at its own x and z
centre — rotating moves everything except the pivot, so a pivot at the bottom would swing the root
instead of the tip. Set, about **Z**:

        tendril_f_up  −7°     tendril_f_lo  −10°
        tendril_m_up  −5°     tendril_m_lo  −8°
        tendril_b_up  −7°     tendril_b_lo  −10°

Each is a **local** rotation and the lower is a child of the upper, so the two **compound** — the
lower segment ends up at roughly the sum of the two angles from vertical. That is what makes the
tentacle curl rather than kink.

**The signs, worked out once — and they are NEGATIVE here.** These segments point **down**, so a tip
sits at `Δy = −L` from its pivot. About Z, `Δx' = Δx·cosθ − Δy·sinθ`, which for `Δx = 0` and
`Δy = −L` gives `Δx' = +L·sinθ`. Outboard on this side is **−x**, so you need `Δx'` negative, so you
need **sinθ negative — a negative angle.** A positive angle swings the tentacle *into the wearer's
other leg*.

**Budget for the corner, not the centreline.** Each segment's own half-width, rotated by the same
angle, adds `halfwidth × sin θ` beyond where the centreline lands, and on a compounded chain the
lower segment's corner is the one that reaches furthest. Check all four corners of a lower segment
against the outboard wall before you commit.

**Envelope budget.** Stay inside `x −5.5 .. −3.2`, `y 4.6 .. 9.8`, `z −2.5 .. 2.7`.

> **Corrected 2026-09-09, mid-build.** This wall was `−5.2`, which the angles above cannot meet: the
> session doing the corner check found the front/back lower segment's outboard bottom corner at
> `−5.459` and the middle's at `−5.215`. It was right and the brief was wrong. `−5.5` is the honest
> wall — `thigh_sheath` already reaches `−5.35` on this socket, so this is 0.11 beyond the widest
> piece here, and the angles are what make the tentacle curl rather than hang like a stick.

**The same budget in the check's own frame**, so you never have to convert: the check prints the
envelope **bone-local, +Y down, from the BONE'S PIVOT**. This bone is the leg, whose pivot is at
Blockbench `y = 12` and `x = −1.9`, so bone-local `x = −(Blockbench x) − 1.9` — a negation **and** a
shift, not just a sign flip. In that frame your budget is

    x  1.3 .. 3.6      y  2.2 .. 7.4      z  −2.5 .. 2.7

Compare the check's envelope line against **those** numbers.

**Pair span.** This is a mirrored socket, so the pair spans `2 × |x|` across the figure. At
`x = −5.2` that is 10.4, far inside the 18 the shoulders span, so it will not be flagged — but
report it.

**Neighbours you must clear**, measured, in Blockbench coordinates on this side:

| piece | reaches | what it means for you |
|---|---|---|
| `scale_skirt` | x −4.90 .. −1.00, y 7.10 .. 12.50 | your upper segments share its height band; you sit outboard of it |
| `pelt` | x −4.90 .. −2.44, y 7.28 .. 12.30 | the same story, and the widest of the hanging pieces here |
| `thigh_sheath` | x −5.35 .. 0.85, y 3.53 .. 11.94 | reaches furthest out and down; your `x ≥ −5.2` stays inside it |
| `loin_panels` | x −3.40 .. −0.40, y 5.44 .. 11.96 | inboard of you; no conflict |

These are the same socket and are **never worn together**, so the check never compares them — they
are heights and depths to place against, not walls.

## Paint

Master sheet `part`, greyscale — a value is a position on the trim material's ramp. One
`armorpieces_paint` call. Give every segment's four side faces a `[top, bottom]` pair running from
mid at the top to dark at the bottom, and make each lower segment a little darker than its upper, so
the tentacle reads as receding into shadow. The bottom faces of the lower segments are the darkest
value on the piece.

Static sheet `part_static`, real colour, one call. A ghast's dead pale white on **every face of
every segment** — around `#D8D4D0` at the top fading to `#A8A29C` at the bottom, using
`[top, bottom]` pairs the same way. This layer carries the colour; the master only carries shading.

## Done when

- [ ] The check is clean, or every `!` still standing is one this brief allows.
- [ ] Envelope inside the budget, in the check's frame, and reported.
- [ ] Pair span reported.
- [ ] Six cubes, three tentacles of two compounded segments each.
- [ ] Both sheets painted: master greyscale, static in colour, same faces.
- [ ] Saved, and the tab closed.

**Allowed to force:** nothing. If a `!` stands, stop and ask me.

## Lessons

Built 2026-09-09 on `qwen3.8-flash`, the cheapest model tried and the best value of the five runs.
It conformed to every stated number, and it caught a contradiction in this brief's own budget by
doing the corner check and stopping to ask rather than picking a side — see the correction note
above. The two defects that reached the saved piece were both mine.

1. **Taper the axis you rotate about.** This brief gave both segments of a tendril the same z lane
   and tapered only x. The bones rotate about Z, which preserves z, so every tendril's upper and
   lower north/south faces sat in identical planes and z-fought across the joint. Fixed by insetting
   the lowers 0.10 per side. Now a rule in `TEMPLATE-qwen.md` and the agent prompt.

2. **A clean check is not evidence of a clean piece.** The report said `ok: nothing needs a
   decision` while three joints were visibly glitching. `trace_geometry.py` emits no face planes at
   all for a cube in a **rotated** chain, and never compares a part against **itself** — so the
   coplanar test switches off exactly when a piece is aimed. Scoped in
   `docs/plans/coplanar-check.md`. The session's "aiming breaks those planes" was true of the
   report, not the geometry.

3. **Volume of interpenetration is the wrong metric.** Hidden overlap is invisible and harmless;
   this piece has 32 OVERLAP lines against knees, greaves and spurs and the mod's own `tassets` has
   76. What players see is *same-facing surfaces in the same plane*, which is a different test.

4. **A repair session needs the target state given absolutely, not as a delta.** Told to "shrink the
   lower cubes in z", one pass also translated the upper cubes and moved the lower bone pivots by
   0.25 — the envelope drifted from `y 7.18` to `7.43` and the joints stepped. Re-specifying all six
   bone origins and all six cubes as absolute coordinates fixed it in one pass with nothing to
   infer. Say what the piece must *be*, not what to change.
