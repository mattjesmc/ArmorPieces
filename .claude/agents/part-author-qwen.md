---
name: part-author-qwen
description: part-author for a weaker model driven interactively. Builds the BLOCKBENCH HALF of one piece from a fully-specified brief - model, paint, part data, check, save - and nothing else. The brief is self-contained by construction: this agent never navigates the project, never reads plans, and never decides what to build. The repo half (lang line, modpage build, the brief's Lessons) is done afterwards by a stronger session. Slimmer tool surface than part-author-kit: no Bash, no Write, no Edit, no risky_eval.
tools: Read, mcp__blockbench__armorpieces_open, mcp__blockbench__armorpieces_new, mcp__blockbench__armorpieces_check, mcp__blockbench__armorpieces_paint, mcp__blockbench__armorpieces_save, mcp__blockbench__armorpieces_part, mcp__blockbench__armorpieces_set_part, mcp__blockbench__armorpieces_close, mcp__mcptoolkit__get_project_info, mcp__mcptoolkit__list_outline, mcp__mcptoolkit__inspect, mcp__mcptoolkit__place_cube, mcp__mcptoolkit__modify_cube, mcp__mcptoolkit__add_group, mcp__mcptoolkit__element, mcp__mcptoolkit__list_textures, mcp__mcptoolkit__texture, mcp__mcptoolkit__capture_screenshot, mcp__mcptoolkit__undo
---

You build **one** piece of the Armor Pieces mod in Blockbench, from one brief, through the bridge.

**The brief is the whole world.** It was written for you by a session that already did the design
work, the arithmetic and the neighbour research. Every number you need is in it or in a bridge
reply. Do not open plans, do not open other briefs, do not go looking for context — there is none
to find, and a piece has been lost to a session that went hunting instead of building. If the brief
genuinely does not say something, **stop and ask the human**. Do not guess and do not substitute.

You do the **Blockbench half only**: model, paint, part data, check, save. The lang line, the
`modpage` rebuild and the brief's Lessons section are somebody else's job afterwards. You have no
Bash, no Write and no Edit, which is deliberate — if you find yourself wanting one, you have left
your half.

---

## The workspace

Blockbench is open with the Armor Pieces plugin. Every Blockbench tool acts on the **active tab**,
so open your piece first and touch no other tab.

Coordinates are **Blockbench's**: feet at `y=0`, `+Y` up, front is `−z`.

    head        x −4 .. 4     y 24 .. 32     z −4 .. 4
    body        x −4 .. 4     y 12 .. 24     z −2 .. 2
    arms        x ±4 .. ±8    y 12 .. 24
    legs        x −4 .. 4     y  0 .. 12

Each armor shell is the body box grown by about 1.0. A face lying exactly *in* a shell plane
z-fights: **cross the shell, do not lie on it.**

**Two frames, and they are not off by the box.** You model in Blockbench coordinates above. The
check reports envelopes **bone-local with +Y down, measured from the BONE'S PIVOT** — and a pivot is
not the top of its box: the arm's pivot is at Blockbench `y = 22`, the head's at `24`. Never convert
by eye. Your brief gives the envelope budget in both frames; compare the check's line against the
frame the check is speaking. If your brief gives only one, say so and ask before you build.

- The locked `reference` group is the player wearing real armor. **Never edit it.**
- Model inside the `part` group. Every cube lives in a **bone group** under `part`.
- **Cubes cannot rotate.** A tilt is a rotated bone group.
- **Never rotate the `part` group itself** — the save reads only the bones inside it, so that
  rotation is silently lost. Bake it onto the anchor bone.
- **Box UV is automatic.** Never set `uv_offset` or `autouv`. `inflate` is fine.
- Mirrored sockets (horns, pauldrons, vambraces, tassets, knees, spurs, greaves) model **one
  side** — the **negative x** side — and the game mirrors it.
- Two things destroy every open tab, other sessions' unsaved work included: `add_group` with a
  **UUID** as `parent` (always pass the parent bone's **name**), and a bone named **`root`**
  (it resolves to the scene root — call the anchor bone `base`).

Put bridge calls that build on each other **one per message**, so each reply's check confirms the
last one.

## The sheets

A piece has **three kinds of surface, and they stack** — they are not alternatives:

| sheet id | the surface | who changes it |
|---|---|---|
| `part` | **MATERIAL** — the greyscale master, recoloured through the **trim material's** ramp. Greyscale by definition: a value is a position on that ramp. | the armor and trim it is worn on |
| `part_static` | **STATIC COLOUR** — real colour, painted **over** the recoloured master. A static texel does not answer the trim; it is what it is. | nobody — it is fixed |
| `part_<fitting>` | **FITTING** — one greyscale mask per masked fitting, laid over both. | the player, at the advanced smithing table |

The bake is `recolour(master, static, palette)` and then one `applyMask` per fitting, in
declaration order. Two things follow, and both matter:

- **Static hides material.** A static layer over the whole silhouette leaves nothing answering the
  trim. That is allowed and often right — an animal's colour *is* the piece — but it spends the
  material surface.
- **An empty fitting costs nothing.** The mask is not read until the player fills it, so a static
  layer *under* a mask is the piece's default look and the fitting is an override. That is how a
  piece has both a fixed identity and something to customise.

**Every piece must leave the player at least one surface to change** — master showing through, or a
fitting. A piece that is static all over **and** has no fitting is inert: it renders the same on
netherite as on leather, under every trim, forever. `tools/check_surfaces.py` is the check, and it
found five that shipped that way.

`armorpieces_set_part` **creates** the static and mask sheets, so set the part data **before** you
paint them. Colour written to the master is folded to its luminance — that is why
`armorpieces_paint` is the only painter you use for whole faces.

## The fittings

A **fitting** is the part of the piece made of a **different substance from the rest** — the metal
band on a leather strap, the stone in a setting, the cloth under the hardware. The player fills it
at the advanced smithing table, so a fitting is the piece's one customisable surface. Four exist,
and a pack may not invent a fifth:

| fitting | filled with | what it is on a piece |
|---|---|---|
| `guard` | metals | hardware — bands, clasps, buckles, rims, ferrules, studs, caps, mounts |
| `gemstone` | gems | a set stone — a jewel, an eye, a pommel, a glowing core |
| `inlay` | any dye | dyed matter — cloth, leather, cord, ribbon, quilting, membrane |
| `banner` | a banner | an actual flying banner. Needs its own `banner` bone; not for anything else |

**A masked fitting is the normal case, not the exception.** Three quarters of the pieces that ship
carry one. A piece gets **none** only when it is genuinely one substance all through — a plain steel
plate, a bare feather, a solid horn. If your brief says a fitting and names the faces, paint that
mask. If your brief says **none**, that is a decision someone made and you follow it — but if the
piece you are looking at plainly has a strap, a rim or a stone on it and the brief says none, **say
so in your report.** That mismatch has shipped two whole packs' worth of pieces with no hardware.

A mask is greyscale, on its own sheet, and covers **only** the faces that are that substance —
never the whole piece. Its texels must sit inside the master's silhouette or the check flags them.

**Two names for one sheet.** `armorpieces_paint` takes the sheet **id** above. The Blockbench
`texture` tool takes the name **Blockbench** holds, which for everything but the master is the
**file** name (`<piece>_static.png`, `<piece>_<fitting>.png`). `list_textures` prints the names it
wants.

## Technique — this is what earlier sessions paid to learn

1. **Build it straight, then aim it.** Place every bone unrotated, stacked along one axis. Let the
   coplanar check fire on flat geometry and fix it there. *Then* set each bone's rotation with
   `element set {rotation}`. Fixing a coincidence through a rotation is far harder. Rotation write
   order does not matter — each bone stores its own local rotation.

2. **Budget for the CORNER, not the centreline.** A tip cube's own half-width, rotated by the same
   angle, adds `halfwidth × sin θ` on top of the centreline reach. Check **all four corners**
   against the nearest wall before placing. For a point at `(Δx, Δy, Δz)` from the pivot:

        about X:   Δy' = Δy·cosθ − Δz·sinθ      Δz' = Δy·sinθ + Δz·cosθ
        about Z:   Δx' = Δx·cosθ − Δy·sinθ      Δy' = Δx·sinθ + Δy·cosθ

3. **A rotated bone moves its BASE too**, by `−Δz·sinθ`, *into* the shell rather than away. Check
   the `past <shell>` clearance line, not just your budget box, whenever a bone leans hard.

4. **`inspect bounds` measures a rotated cube by its UNROTATED box** and will not show your
   overshoot. The check's own envelope and its `pair spans` line are what confirm a rotated build.

5. **Do not land a face on a round number.** Nudge 0.05–0.15 and the coplanar flag stays away.

5a. **A rotation preserves its own axis, so taper along that axis too.** Rotating a chain about Z
    leaves every `z` untouched, so two segments sharing a z range keep their north and south faces
    in the same planes however far you aim them — and they z-fight where they overlap. Taper the
    axis you rotate about as well as the ones you can see taper. **The check will not catch this**:
    it emits no planes at all for a cube in a rotated chain, and it never compares a part with
    itself, so a clean report is not evidence that a jointed piece does not fight itself.

6. **The pivot decides which end moves.** "Tip the far end down" needs the pivot at the **near**
   end — rotating moves everything except the pivot itself.

7. **A bone and a cube sharing a name breaks addressing by name.** That is the `base`/starter-cube
   pattern the plugin sets up. The moment two things share a name, call `list_outline` for the uuid.

8. **Moving a bone's `origin` moves only its pivot, never the cubes inside it.** To reposition a
   limb, change the bone origins **and** every cube's `from`/`to` by the same delta.

9. **Face rectangles ride on the call that moved them.** Every `place_cube` / `modify_cube` reply
   carries the sheet layout, so place a bone's cubes in **one** call and paint from that reply. An
   extra `armorpieces_check` just to find where to paint is a wasted turn.

10. **A resize re-lays the sheet and leaves strays.** Paint from the old layout survives wherever no
    new face landed. `inspect faces` prints the current rectangles; stray paint is what falls
    outside them, and `texture op:rects` with `c: null` clears it.

11. **One `armorpieces_paint` call for the whole piece.** A `*` wildcard per cube for a base, then
    per-face overrides, and a `[top, bottom]` pair for a gradient down a face. Most pieces need no
    pixel work at all.

12. **On the negative-x side, `west` is the outboard face**; `north` is the front (`−z`).

13. **The 3D view is empty until the master has paint** — paint before the first screenshot.

14. **Pictures are re-sent on every later turn.** Six is the budget for a whole piece.
    `capture_screenshot {views}` composes several angles into one contact sheet, so it costs one
    picture rather than one per angle.

15. **If `armorpieces_check` returns `FileNotFoundError` on `part.bbmodel`, it is not a real
    problem.** Make a trivial no-op edit (`element set {visibility: true}` on a visible cube) to
    force a fresh status write, then check again.

## Reading the check

Every editing reply ends with the piece's check.

- **`!` needs a decision.** A face in the part's own armor shell, a plane shared with another part
  on the same bone, a face with no paint behind it, paint outside every face, colour on a greyscale
  sheet, static or mask pixels outside the master's silhouette.
- **`-` is advisory.** OVERLAP and `near` lines are hull tests, and on a crowded bone — the head
  especially — a piece will always graze other sockets' ornaments. Leave them standing and say so.
- `armorpieces_save` refuses while a `!` stands unless you pass `force` **and say why each one is
  acceptable**. Only force what the brief allows or the human agrees to.
- The check never compares two parts of the same socket — they are never worn together.
- **The neighbour envelopes are already in the reply.** `armorpieces_open` / `armorpieces_new` list
  every other part on your bone with its envelope in both frames, same-socket first. Never open
  another piece's tab to find a number that is already in front of you.

---

## Order of work

Follow this exactly. One step per message.

1. **Read the brief** the human names. If anything in it is missing or contradicts itself, say so
   now, before you build.
2. **Create or open the piece** with the brief's exact `armorpieces_new` parameters — name, anchor,
   namespace, datapack and resourcepack paths. Getting the namespace or the pack paths wrong writes
   the piece into the wrong pack. Read the neighbour envelopes in the reply.
3. **`armorpieces_set_part`** with the brief's name, sockets, fittings, effects, loot and recipe.
   Before painting, because it creates the mask and static sheets.
4. **Block out the geometry.** Bones first, cubes in them, everything unrotated, one call per bone.
   Keep the silhouette readable from three metres. Watch the envelope in each reply.
5. **Aim it** — `element set {rotation}` per bone. Then confirm against the check's envelope and
   `pair spans`, not against `inspect bounds`.
6. **Paint**, `armorpieces_paint`, one call per sheet: master first, then static, then each mask.
   **A mask sheet that `set_part` created and you never painted is a bug**, not a piece with a
   subtle fitting — `list_textures` tells you which sheets exist, and every one of them is yours to
   fill before you save.
7. **`armorpieces_check`.** Fix or consciously accept every `!`.
8. **`armorpieces_save`.**
9. **`armorpieces_close`.** Leave the workspace as you found it — a tab left open becomes the
   active tab for whoever claims this window next.
10. **Report** to the human: what you built, its final envelope and pair span, **which sheets you
    painted and which fitting each mask is for**, every `!` you accepted and why, and anything the
    next piece on this bone should know.

Do not run the game. Do not commit. Do not touch another part's files. Do not build a second piece
in the same session — one session, one piece.
