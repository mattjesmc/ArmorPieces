# What the part sessions have learned

**Read this instead of skimming other briefs.** Every brief here ends in a Lessons section written by
the session that built it, and those sections are the record of what each piece cost — but they were
written against whatever bridge existed on the day, and the bridge has been replaced twice. **52 of
the 77 briefs teach tools that no longer exist** (`remove_element`, `rename_element`,
`draw_shape_tool`, `paint_with_brush`, `activate_texture`, `save_checkpoint`), and at least one makes
a claim that is now false. Their Lessons are still worth reading *about a specific piece you are
building next to*; they are not worth reading for technique.

This file is the technique, distilled from the sessions that ran on the current bridge
(`docs/measurements/blockbench-plugins.md` eras C, D and E — the Coral and Dragonslayer packs). It is
short on purpose: it is carried on every turn of your session, and reading a 3,600-token sibling
brief instead was measured as **48% of everything a session carries**
(`CONCURRENCY_AB.md`, round 2).

Add to it when you learn something that generalises. Leave what only applies to your piece in your
own brief's Lessons.

---

## Building

**1. Build it straight, then aim it.** Place every bone unrotated, stacked along one axis. Let the
coplanar check fire on flat geometry and fix it there. *Then* set each bone's rotation with
`element set {rotation}`. Fixing a coincidence through a rotation is much harder than fixing it
before one, and `dragon_horns` caught three that way — two shell planes and a sibling's cube — with
no rebuild.

**2. Rotation write order does not matter.** Each bone stores its own local rotation and Blockbench
composes the chain, so you can set them innermost-first, outermost-first, or in any order.

**3. Budget for the CORNER, not the centreline.** The envelope maximum comes from a cube corner, not
the axis. A tip cube's own half-width, rotated by the same angle, adds `halfwidth × sin θ` on top of
the centreline reach — which is what put `dragon_talons` 0.06–0.08 past its wall on the first pass.
Check **all four corners** of a bone's cubes against the nearest wall before placing.

The three formulas, for a point at `(Δx, Δy, Δz)` from the bone's pivot:

    about X:   Δy' = Δy·cosθ − Δz·sinθ      Δz' = Δy·sinθ + Δz·cosθ
    about Z:   Δx' = Δx·cosθ − Δy·sinθ      Δy' = Δx·sinθ + Δy·cosθ

**4. A rotated bone moves its BASE too.** Leaning a bone one way sinks the opposite base corner by
`−Δz·sinθ` (or `−Δx·sinθ`) — small, a few hundredths up to ~0.1, but it goes *into* the shell rather
than away from it. Check the clearance line (`past helmet`, `past chestplate`), not just your budget
box, whenever a bone leans hard or starts close to a shell.

**5. `inspect bounds` measures a rotated cube by its UNROTATED box.** It will not show your rotation
overshoot. The check's own envelope and its `pair spans` line, in the game frame, are what confirm a
rotated build.

**6. Do not land a face on a round number.** Shell planes and other pieces' cubes sit on them. Nudge
0.05–0.15 and the coplanar flag does not come back. `dragon_scales` moved a whole z-range by 0.05
before placing anything and never saw the warning again.

**7. Your brief's specific coordinates beat its summary budget box.** When the two disagree — and
they have, by 0.1–0.2 — the more specific instruction is the one to follow. Say in your report that
you noticed and which you took.

**7a. Pivot placement decides which end moves.** "Tip the far end down" needs the pivot at the
*near* end, not the far one — rotating about a pivot moves everything except the pivot itself, so
the end you want to move is the end that is NOT at the pivot. Check which end the brief means
before picking which edge of a cube to put a bone's origin on.

**7b. A bone and a cube sharing a name breaks addressing by name.** It is the `base`/starter-cube
pattern the plugin itself sets up, and once there are two of them `element set` / `element rename`
refuse with "names N elements". Call `list_outline` for the uuid the moment a bone and a cube share
a name.

## Reading the check

**8. `!` needs a decision; `-` is advisory.** OVERLAP and `near` lines are hull tests
("check whether the real cubes meet"), and on a crowded bone — the head especially — a piece will
always graze other sockets' ornaments in a hull test. Leave them standing and say so. Only `!` lines
block a save, and `armorpieces_save` refuses while one stands unless you `force` it with a reason.

**9. The envelopes you need are already in the reply.** `armorpieces_open` / `armorpieces_new` list
every other part on your bone with its envelope in **both frames** — same-socket pieces first, which
are exactly "the height the circlet uses". Do not open another piece's tab or read its geometry file
to find a number that is already in front of you.

**10. Face rectangles ride on the call that moved them.** Every `place_cube` / `modify_cube` reply
carries the sheet layout, so place a bone's cubes in ONE call and paint from that reply. An extra
`armorpieces_check` to find out where to paint is a wasted turn. After a rework, `inspect faces`
gives the current rectangles — stray paint is whatever falls outside them.

## Painting

**11. One `armorpieces_paint` call for the whole piece.** Use a `*` wildcard per cube for a base,
then per-face overrides, and a `[top, bottom]` pair where you want a gradient down a face. Five of
the last six pieces needed no `texture op:rects` and no pixel work at all.

**12. On the negative-x side, `west` is the outboard face** — the leading edge of anything sweeping
away from the body. `north` is the front (`−z`).

**13. Greyscale is not a suggestion.** The master's value is a position on the trim material's ramp;
`armorpieces_paint` folds a colour to its luminance, and a generic painter would write colour onto it
and the check would report it. Only `part_static` keeps real colour.

## Tooling

**14. If `armorpieces_check` returns `FileNotFoundError` on `part.bbmodel`, it is not a real
problem.** Make any trivial no-op edit (`element set {visibility: true}` on an already-visible cube)
to force a fresh status write, then check again. `dragon_horns` lost three retries to this before
finding it.

**15. Pictures are re-sent on every later turn.** Six is the budget for a part. Take one only where
it can still change what you draw; `capture_screenshot {views}` composes several angles into one
contact sheet, so it costs one picture rather than one per angle.

**16. Two names for one sheet.** `armorpieces_paint` takes the sheet ID (`part`, `part_static`,
`part_<fitting>`); the Blockbench texture tools take the name Blockbench holds, which for everything
but the master is the file name. `list_textures` prints the names they want.
