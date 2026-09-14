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

**11a. When a piece DOES need single texels (rivets, studs, a one-pixel border), use
`armorpieces_paint`'s own `pixels` list rather than reaching for `texture op:rects`.** It takes
`{x, y, value}` sheet addresses directly, in the SAME call as the whole-face `faces` map, on the
same sheet — one undo entry for the whole piece's master (or mask), not a separate tool and a
separate call. Get the addresses from the face rectangle the placing call already returned (a
face's texel count is exact, so "the middle row" or "spaced two pixels apart, centred" is
arithmetic on that rectangle, not a guess) — `brute_belt`'s studs never touched `texture op:rects`.

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

**FIXED IN THE LAUNCHER, 2026-09-09 — read 17-18a as diagnosis, not as a standing condition.**
The cause was named correctly by the session that wrote item 17: the toolkit shim's **Blockbench**
adapter pins on `MCPTK_BLOCKBENCH`, while `MCPTK_URL` is its *Minecraft* upstream (default 25599).
`tools/run_briefs.ps1` was setting the latter, so every session's shim range-scanned 25801-25816 and
claimed a window of its own. The runner now exports `MCPTK_BLOCKBENCH`, and `.mcp.json` interpolates
it (`${MCPTK_BLOCKBENCH:-}`) so it actually reaches the server — a variable the config does not name
never arrives, whatever the launcher exported. If you see `no project is open` again, check those two
places first, then fall back to 18a.

**17. `mcp__mcptoolkit__*` answering `no project is open` on every call, right after a working
`armorpieces_open`, is a launcher wiring bug, not a workspace problem.** `tools/mcp/server.mjs` (the
`armorpieces_*` proxy) can be pinned to this session's own Blockbench window via `ARMORPIECES_BB_URL`;
the `mcp-toolkit` shim's separate Blockbench adapter needs its own matching pin, `MCPTK_BLOCKBENCH`,
or it range-scans 25801-25816 and claims whatever unreserved window is left — which is never the
pinned, human-reserved one, so it ends up in a different, empty window under the same session id.
Diagnose it the same way every time: `curl http://127.0.0.1:<port>/hello` across 25801-25816 (the
`armorpieces_*` tools work throughout, so `armorpieces_pieces`/`armorpieces_check` already say which
piece is yours) to find the port whose `active` is your piece, then read that port's
`claimed_by.session` — the session id both your processes actually share. From there, `POST
http://127.0.0.1:<port>/cmd` with `{"tool", "args", "session": {"id": "<that id>", "client":
"armorpieces", "profile": "kit"}}` and header `X-MCPTK-Session: <that id>` reaches the SAME plugin
the broken shim would have, with the SAME argument shape as the `mcp__mcptoolkit__*` tools document
(`place_cube`, `add_group`, `element`, `capture_screenshot`, `inspect`, …) — it is not
`risky_eval`, it is the documented protocol, addressed directly because the proxy that should carry
it is pointed at the wrong window. Keep using `armorpieces_check` after every raw call to confirm it
landed, exactly as the working proxy would want.

**18. If every `mcptoolkit` call — `get_project_info`, `list_outline`, `risky_eval`, anything —
answers `no project is open ... (open: (none open))` right after a normal `armorpieces_open`/`_new`
that itself succeeded and shows your piece, that is not a naming problem to retry through: it means
the `mcptoolkit` server in this session cannot see the Blockbench window the `armorpieces` server is
using at all (two disconnected bridges, not one tab race). Confirm with two calls
(`get_project_info` with no argument, then `risky_eval` with a one-line body) rather than trying every
name variant — a session lost an entire turn budget to this before concluding the connection itself
was broken. There is no tool-level fix; place_cube/add_group/element all need `mcptoolkit`; a piece
with no geometry beyond the starter cube cannot be built until this is repaired, so discard, close and
report it rather than forcing a save of the starter piece.

**18a. There IS a fallback, found the next time this happened (`wither_ribs`): call the bridge
directly.** The `mcptoolkit` MCP *tool* being unreachable does not mean the underlying HTTP bridge
is down — `env | grep MCPTK_URL` gives the exact port your session is meant to be using (it was
correct and pointed at the window holding the piece); `curl http://127.0.0.1:<port>/hello` showed
the piece open and active; a `curl -X POST .../cmd -d '{"tool":"place_cube","args":{...},"session":
"<MCPTK_SESSION>"}'` for every geometry tool (`list_outline`, `place_cube`, `add_group`, `element`,
`capture_screenshot`) worked exactly as the wrapped tool would have — same tool names, same
argument shapes (`curl .../tools` lists them and their declared args). A whole piece was built this
way with no `risky_eval` involved — it is the same declared tools over their own native transport,
not a bypass of them. **Diagnose before giving up**: eight `mcptoolkit_bridge` windows can be
listening on `25801`-`25808` at once (one per concurrent session); confirm your OWN port from
`MCPTK_URL`/`ARMORPIECES_BB_URL` and hit `/hello` on it directly before concluding the piece is
unbuildable.

**18b. The direct-bridge fallback's `element` tool wants `id` (or `ids`), not `name`, for `remove`.**
`{"op":"remove","name":"x"}` errors `give id or ids`; `{"op":"remove","id":"x"}` (a bone or cube name
works fine as the id, not just a uuid) is what the schema actually takes. `set`/`rename` accept
`id` the same way.

**19a. Over the raw bridge (18a), `element {op: remove}` (and similarly `rename`) wants the
element addressed by `id`, not `name` — `{"name": "main_0"}` answers `"give id or ids"` even
though `name` is a valid field on the tool (it's for *setting* a new name, not addressing the
target). Pass the element's current name string as `id`; it resolves by name just as well as by
uuid.**

**19. `[top, bottom]` shades the face's HEIGHT axis, not its length.** On a thin, elongated cube
(a rib, a spike, a wire) box-UV maps a face's texture HEIGHT to whichever physical axis is
shortest on that face, which is often not the axis you want to grade. A face that is 1 texel tall
has no "top" and "bottom" to shade between — `[top, bottom]` there paints one flat row, not a
gradient. Grade the LENGTH instead with `pixels`, one texel per column, and get the column order
from the cube's own `from`→`to` on that axis: box-UV lays out column 0 at `from`, the last column
at `to`, regardless of which one is world-near or world-far — so two mirrored cubes (`from`/`to`
swapped by sign) need the gradient's values written in opposite order to read the same in-game.

**20. When several sessions build sibling pieces at once, `armorpieces_check`/`_paint` can answer for
the WRONG piece.** Three concurrent sessions on the Nether pack (`wither_mask`, `wither_heads`,
`wither_ribs`) shared one Blockbench window; a bare `armorpieces_check` right after a clean
`armorpieces_open` sometimes printed a sibling's report instead of mine, because whichever session's
tab call landed last on the shared window is what "check" reads. `armorpieces_open` on your own piece
name reliably snaps the active tab back before your next call — call it again immediately before
anything that reads state, and read the piece name in the reply's first line every time, not just
once.

**20a. That mismatch is in `armorpieces_check`'s status-file publish, not in your actual edits.**
`crystal_pendant`, built alongside `dragon_claws` in a shared window, saw the same wrong-piece report
from the very first `armorpieces_check` — but `mcp__mcptoolkit__get_project_info` (no arguments) showed
`"project":{"bound":true}` on the correct piece the whole time, and every `place_cube`/`element` call
landed correctly throughout. The mcptoolkit tools bind to your session's project; `armorpieces_check`
narrates whatever tab last went active in the real UI. These are different failure modes: a check
*reporting* the wrong piece does not mean your last edit *landed* on the wrong piece. If a check looks
wrong, call `get_project_info` (cheap, one line) before distrusting the edits you just made — then
re-`armorpieces_open` your own piece to fix the narration for the next read.

**21. The check only measures YOUR OWN armor shell.** `ominous_banner` (2026-09-10) ran a pole from
the `back` socket up past the head, and the clearance block printed `past body / past chestplate /
past leggings` and **no `past helmet` line at all** — because a helmet is not a `back` piece's shell.
So the check will happily let you drive a piece straight through a shell that belongs to a different
armor slot, and stay silent about it. Whenever a piece leaves the neighbourhood of its own armor
piece, clear the other shell **by arithmetic in the brief**, not by waiting for a flag. The helmet
shell is `x -5..5, y 23..33, z -5..5`; anything on `back` that rises past `y = 23` therefore has to
sit at `z >= 5.25`.

**22. A `!` COPLANAR against a piece on a DIFFERENT socket is a stop, and it is common.** Two of the
first four Hero of the Village sessions (`witch_hat`, `golem_plates`) built cleanly, stayed inside
budget, painted every sheet — and then stopped without saving, because a brief that says "allowed to
force: nothing" makes a plane coincidence with a piece you are worn *with* into a blocker. Both were
the brief's fault, not the session's: `x = -6.15` is an internal face of `helm_wings`, `z = -3.95`
is `fanged_cop`'s front face. Two fixes, and you want both. In the brief, pick coordinates that sit
**outside** a neighbour's whole printed envelope rather than merely inside your budget. And give the
session standing permission to nudge its own face by 0.1 and repaint it, because a shared plane
z-fights in game and moving is always right — it is only the size of the move that ever needed
asking. Without that permission the session burns its whole turn budget and saves nothing.

**23. A weak model sometimes ends its turn on prose instead of a tool call, and a headless run
then simply stops.** Two of nineteen qwen3.8-flash sessions on 2026-09-12 (`compound_eyes`,
`honeycomb_gorget`) read the brief, created the piece, set the part data, and then wrote "Now
removing the starter cube and placing the three cubes" - and stopped, at 1.0 and 0.3 minutes,
`is_error: false`. Nothing in the brief caused it; both built cleanly on a rerun. So a batch's
"ok" column is not the verdict: count the cubes on disk (`dump_piece.py` or `check_part.py`) for
every piece before calling the batch done, and expect roughly one in ten to need a rerun. A rerun
needs the skeleton `armorpieces_new` left behind deleted first (data, geometry, sheets, recipe) -
the plugin refuses to create a piece that is already in the pack - and the dead session's tab
closed in its window.

**24. Bone-mate planes can be avoided BEFORE the session, mechanically.** The seventeen briefs of
2026-09-12 were generated with every face snapped off every plane a bone-mate's cube puts on the
bone (`check_part.references` + `trace_geometry.neighbours` give them offline, in both frames)
and off the outer shell's walls, at 0.012 clearance; the two budgets were then derived from the
snapped cubes rather than typed. Seventeen sessions, zero COPLANAR stops, zero forced saves. On
the leg bone the planes sit every few hundredths, so hand-picked coordinates land on one about
half the time - snap, do not guess.


**25. Snap the siblings against each other, and a whole pack line goes through clean.** The 48
culture briefs of 2026-09-13 were generated with every face snapped off every bone-mate plane on
disk AND off every sibling designed in the same batch, in build order (a later piece on the same
bone finds the earlier one on disk by the time it runs), with a buried-cube check (a crest mount
inside the helmet shell at y 32 is never seen; start at 33.07), same-pack cube intersections
refused, and every piece given at least one static cube and one masked fitting from the start.
Result: 48 sessions, zero `!` lines, zero forced saves, zero nudges, every envelope inside its
budget to the hundredth, and no surface retrofit owed afterwards. The one rerun was not the
brief's: the agent window closed itself in the gap between two sessions and the next one found no
bridge - it said so and stopped, which is the right answer, and the driver now asks for a window
by session id (RUNNING.md). `tools/briefs_cultures/` is the generator, kept.

**26. `check_part.py <name>` reads the master from `tools/decoration_masters/`, and the plugin's
save writes only the pack's texture folder.** After a clean `armorpieces_save` of a piece that has
a master in that directory (the built-in packs: knightly, court, wayfarer - the pieces that were
the mod's own), the by-name check still reports the OLD sheet: dozens of unpainted faces and
"opaque px outside every face" on a piece the plugin itself passed. It is not a paint problem.
Run `check_part.py <geometry.json> --name <part> --master <pack png> --mask <fit>=<pack png>` to
check the sheets the plugin actually wrote, then copy those same files into
`tools/decoration_masters/` so the by-name check (and the gate's `parts` tier) reads them too.
`heel_wings` lost a turn to this on 2026-09-14.

**27. When a fan's angles run from steep to flat, shift each plate's chord along its length axis
rather than centring it on the pivot.** The chord (the unrotated z depth) rotates with the plate,
so on a 75-degree plate a 1.5 rear offset drops the root corner by `1.5*sin(75)` - straight into
the floor - while on a 36-degree plate a 0.7 front offset pushes the root corner in front of the
shell plane. Give the steep plates their chord mostly behind the pivot and the flat ones mostly in
front (`heel_wings` used front/back 0.5/1.5 -> 1.4/0.6 across four plates at one chord of 2.0),
and check the closure as `b_i + f_(i+1) >= L*dtheta + step*cos(theta_i)` with the shifted offsets.
Every root corner then stays inside the budget with no change to the angles.

**28. The `pixels` list of `armorpieces_paint` is applied AFTER its `faces` map.** That is what
makes a per-texel highlight in the same call work (11a) - and it means a `value: null` sweep to
clear an old layout's strays has to be its OWN call, before the face paint, or it erases the faces
it shares a call with. One 400-entry null list over the old sheet's whole rectangle, then one
faces call: zero strays on a rework.


**29. A fan of plates rotated about one axis must STEP along that axis, or every plate shares two
planes and the whole fan z-fights.** Rotation about X preserves x, so four plates all at
`x -0.2..0.2` under pivots at one x keep their east and west faces on exactly the same two planes
however they are angled - and a fan that closes (each chord lapping the next) overlaps in y-z
everywhere, so every lap fights. `heel_wings` shipped like that on 2026-09-14 and the check said
`all clear`: a rotated cube contributes NO planes to the coplanar pass (`trace_geometry.py`, the
`axis_aligned` guard) and a part is never compared with itself, so plate-against-plate is
examined by nothing. `helm_wings` avoids it by stepping each plate's pivot 0.2 in x
(5.55 / 5.75 / 5.95 / 6.15); the heel_wings brief copied the fan and dropped the step. The rule
was already in the qwen template ("taper the axis you rotate about") and it is every session's: when the
brief gives one x for all plates, take it as the FIRST plate's and step the rest 0.2 outboard.
The person fixing it staggered the quills and vanes in x by hand; that is the shape to copy.

**30. Box UV puts a `down` face's FIRST sheet row at the cube's SOUTH (+z) edge, and its `up`
face's first row at north.** Anything front/back-asymmetric painted by `pixels` on a `down` face
(a paw's toe beans, a sole's tread, a heel stud) lands at the BACK if you assume row 0 is the
front - `cat_paws` put its three small beans on row 0 and the view from below showed them behind
the big pad. Row `face_y + h - 1` is the front edge of a `down` face. Left/right-symmetric
patterns (stripes at columns 1 and 3 of 5) are immune, so plan asymmetric detail on `down`
faces with this rule and check it with one perspective shot aimed up at the cube
(`position` below and in front, `target` on the cube) - the 3-view `fit` contact sheet is too
small to read a piece the size of a hand.

**31. A rework's null sweep is one `texture op:rects` per sheet over the whole 64x32 with
`c: null`**, three calls in all, not a long `pixels` list: nothing of the old layout survives, so
there is nothing to subtract, and the `armorpieces_paint` calls that follow paint every current
face. Expect #14's `part.bbmodel` FileNotFoundError on the replies right after the sweep; one
`element set {visibility: true}` clears it.

**32. A chain's tip target and its link lengths fix the curl before any angle is chosen.** The
chord from root to tip over the summed link lengths is the whole story: `dragon_claws` had links
3.0/2.5/2.0 (7.0 total) and a brief tip at (y 8, z -8) from a root at (11.6, -2.5) - a 6.5 chord -
so the tip can only reach 64-75 degrees cumulative however the increments are split, and "curl
harder" would have put the tip under the y floor. Compute `chord / total` first: near 1.0 is a
nearly straight talon, ~0.8 a hook, ~0.6 a curl. If a brief asks for more curl than the chord
allows, the fix is longer links (each 0.5 buys ~15 degrees at the same tip), not steeper angles,
and it is worth a line in the report.

**33. A pack piece's sheets are under `textures/entity/decoration/`, not
`textures/armorpieces/decoration/`.** The `--master/--static/--mask` paths of a by-file
`check_part.py` run go there; `find packs/<pack> -name "<part>*"` gives all five files in one
call. (7b, addendum: when a bone and its cube share a name, the bone's uuid is already in the
`add_group` reply - no `list_outline` needed. Naming the cube `<bone>_cube` avoids it entirely.)

**34. On a link built upright and then leaned back, the "top" surface is its `north` face, not
`up`.** A horn, spine or talon segment is modelled vertical and rotated about X; at 40-65 degrees
its unrotated front (`north`, -z) is what faces up-and-forward, its `south` is the underside, and
`up` is only the tip end. A brief's "ridge along the top of each link" is a `north` paint,
"underside" is `south` (`dragon_horns` rework). On a link leaned FORWARD the roles swap. And a
rework of a whole piece is: `element remove id:<anchor bone>` (takes every cube and child bone
with it), three `texture op:rects c:null` sweeps (#31), rebuild straight, aim, one paint per sheet
- 20 calls for a three-cube piece, no `armorpieces_set_part`, the part file's uid untouched.

**35. Bone rotations compose X first, then Y, then Z (Blockbench's `ZYX` order).** An upright bar
given `[X, 0, Z]` is tilted back by X and THEN swung out by Z in that tilted plane: its direction is
`(-cosX sinZ, cosX cosZ, sinX)`, and positive X tilts it BACK (+z). A child bone's own Z rotation adds
to the parent's Z inside the parent's tilted plane. `dragon_wings` predicted its elbow and tips to
0.01 from this; a brief's rotation signs are a suggestion, the reply's envelope is the arbiter.

**36. A `back` piece rising past `y 23` must clear the helmet CORNER, and the check will not say
so.** The bite is not the centreline: a bar swung outward from a pivot inside `x +-5` keeps its
inboard cube corners inside `x +-5.15` for several units of length while already above `y 23` and
at `z < 5.25`. Push the four corners `(+-w, s, +-w)` through `Rz(Rx(v))`, find the `s` where the
`+x,-z` corner (left wing) reaches `|x| = 5.15`, and require its `y < 23` there - `dragon_wings`
moved its pivot from the brief's `x -3.5` to `-4.75` and down 0.5 for that.

**37. Radial plates pivoted at one point make a hub unless each starts out along its radial and
carries its chord on ONE side.** Start plate k a few units from the pivot and put the whole chord
toward the leading bar / previous plate (local `+x` of a `+delta`-rotated plate points toward
smaller delta); its root corner then lands inside the bar or under the previous plate. Test the
corner's `(t, c)` in the previous plate's frame. The fan is closed to `r = chord / sin(step)` and
scalloped beyond.

**38. `north` column 0 is the cube's `+x` edge; `south` column 0 is `-x`.** A line along a plate's
long edge painted with `pixels` goes on `north` column 0 and `south` last column for the `+x` edge,
the reverse for `-x` - and a mirrored pair swaps them. (Companion to #30's row rule.)

**39. A resize that re-lays the sheet can GROW it (64x32 -> 64x64); a second full sweep needs the
new size from `list_textures`.** Two sweeps and two full paints per sheet are still cheaper than
subtracting old rectangles.

**40. `armorpieces_save` that narrates a DIFFERENT piece and refuses on its problems has written
nothing.** Another tab went active in the window (#20). `armorpieces_open` your own piece, then
save again.

**41. For a head-sized piece, skip `fit: true` and aim one perspective shot at it.** `fit` frames
the whole player, and a 2-view contact sheet of that shows a mask as a grey smudge. One
`capture_screenshot {position: [-14, 26, -22], target: [0, 28, -8]}` read `dragon_mask`'s muzzle,
nostril, jaw gap and teeth strip in one picture; scale the offset to the socket. The viewport
renders the master preview (flat grey), not the static colours, so a screenshot judges shape only -
read the saved PNGs with Pillow for the paint. A mask-only `armorpieces_paint` with `pixels` and no
`faces` is accepted, which is what an eye-slit fitting wants.
