# Brief: Aerials

Authored through the bridge (`tools/mcp`) by one `part-author` session on Opus, in the second
batch of four (after girdle, knee_studs, wing_cases and talons - skim their lessons, especially
the rig frame in knee_studs and the rotation signs in wing_cases and talons). From the `horns`
row of `docs/plans/part-variety.md`:

> **Aerials** - Segmented insect antennae, angled out and down. Theme: Carapace. Fittings: none.

The plan lists no fitting; this brief gives the segments an `inlay` mask so the aerials take the
same dye as the Wing Cases and the two read as one beetle. The root socket stays the helmet's
metal.

**Part.** `armorpieces:aerials`, socket `horns` only, in the mod's own pack. Display name
"Aerials". Fittings: `armorpieces:inlay`, one mask, covering the three segments and not the root
socket. No effects, no loot, no static layer.

**Shape.** `horns` is a mirrored socket on the head bone: model ONE side, the LEFT, which in this
rig is at NEGATIVE x. The head box is x -4..4, y 24..32, z -4..4 (pivot 0, 24, 0); the helmet
shell is that box inflated a full unit, x -5..5, y 23..33, z -5..5; the left temple anchor is at
Blockbench (-4, 29, 0), on the head's side face. "Outboard" is more negative x, and anything with
x above -5 is inside the helmet. Read the envelopes in the `armorpieces_new` reply: the brow
parts (circlet, coronet, nasal, visor) ride the same bone and their bands wrap round to the
temples at about y 28..30.5, so put the root socket a little above them (its base half a texel
inside the shell, like the spire's plate, at about y 30..31.5) or say by how much it laps. Build:
a `root` bone with a 1.5x1.5x1.5 socket cube straddling the shell plane at x -5.5..-4.5, and
under it a chain of three bones, each with one cube modelled straight OUT along -X from its
pivot (so its length runs in x), each rotated a little further than the last about Z so the
chain angles out and then down: cumulative angles of about 20, 45 and 70 degrees (for a segment
modelled along -X a POSITIVE Z rotation tips it down - check the first one in the reply before
placing the rest), sections 1.0 / 0.8 / 0.6 square, lengths 2.25 / 2.0 / 1.75, each starting a
quarter unit before its parent's end. Compute the chain (pivot + L x (-cos θ, -sin θ) in x, y)
before placing; the tip should land near x -10, y 25.7 - outboard of the chestplate's arm shell
(x -9) and ABOVE y 25.5 so it clears the pauldron zone. A slight outward splay in z is not
needed; keep everything at z -0.5..0.5.

**Sheets.** Master: root socket mid-grey with a lighter top; segments dark chitin `[top, bottom]`
lighter toward the tip, each segment a step lighter than the last, one bright texel at the tip,
and a single dark texel ring where each joint meets (the `pixels` list) so the segmentation
reads. Inlay mask: the three segments' faces only, the same gradient.

**Recipe.** Centre item `minecraft:fermented_spider_eye` (a flat item, unused by any template),
paper ring.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py aerials`
and `python tools/check_authoring.py` clean; the mod page rebuilt; the lessons paragraph below
filled in. Count your paint calls and say what the painter did and did not cover.

## Lessons from the session

Built 2026-09-03. Bridge calls that stuck: 2 `armorpieces_pieces`, 3 `armorpieces_open`
(two of them after Blockbench threw the whole workspace away, see below), 1 `armorpieces_new`,
1 `list_outline`, 4 `add_group`, 4 `place_cube`, 3 `remove_element`, 1 `armorpieces_check`,
1 `armorpieces_set_part`, **2 `armorpieces_paint`**, 2 `set_camera_angle`, 1 `armorpieces_save`.
No `risky_eval`, no `modify_cube`, no nudging, nothing hand-edited, and the save went through
first time without `force`.

**What I built.** A `base` bone (pivot -5, 31.75, 0, unrotated) with the socket boss
`boss` x -5.5..-4.5, y 31..32.5, z -0.75..0.75 - straddling the helmet shell's x -5 plane half
in, half out - and under it three bones, each cube modelled straight out along **-X** from its
own pivot in the unrotated pose: `seg1` (pivot -5.25, 31.75, rotation Z **+20**) cube
x -7.5..-5.25 1.0 square; `seg2` (pivot -7.25, local **+25**, cumulative 45) cube x -9.25..-7.25
0.8 square; `seg3` (pivot -9.0, local **+25**, cumulative 70) cube x -10.75..-9.0 0.6 square,
each starting a quarter unit before its parent's end. **Sign:** for a segment modelled along -X,
a POSITIVE Z rotation tips it down and outboard, exactly as the brief predicted; end =
pivot + L x (-cos θ, -sin θ) with θ cumulative. The check confirmed every pivot to a hundredth
(`seg2 at (7.13, -7.07)` = Blockbench -7.13, 31.07 against a predicted -7.129 / 31.066), so
nothing was moved after placing.

**The brief's tip target is not reachable with the brief's own numbers, and the arithmetic says
so before the first cube.** With lengths 2.25 / 2.0 / 1.75 and cumulative 20/45/70, the chain
only spends 2.0 cos20 + 1.75 cos45 + 1.75 cos70 = 3.71 of x and 0.68 + 1.24 + 1.64 = 3.57 of
drop from the first pivot. From the root that is a tip **axis** at Blockbench (-8.97, 28.18),
envelope corner x **-9.25**, not the brief's "x -10, y 25.7" - reaching y 25.7 would need 5.3 of
drop out of a 5.5-unit path, i.e. a nearly vertical last two segments. I kept the brief's
sections, lengths and angles (they make a clean insect taper) and let the tip land high: the two
constraints behind the target are still met, since the envelope corner is 0.25 **outboard** of
the chestplate arm shell's x -9 and the whole part stays **2.5 above** the pauldron zone's
y 25.5. Rule of thumb for a chain off the temple: usable drop with a 70-degree final angle is
about 0.6x the path length.

**Where the root sits relative to the brow band.** The brief offered y 30..31.5 "or say by how
much it laps"; I used **y 31..32.5** instead, which clears `circlet`'s top plane (Blockbench
30.75) by 0.25 and laps nothing - 30..31.5 would have buried 0.75 of the boss in the circlet and
put its own bottom face 0.25 under a wrapping band. Because the rest of the part is outboard of
x -6.53 wherever it is below y 30.75, and the brow parts stop at x +-6, the check reports **"all
clear by more than half a unit"** from all nine parts on the head bone. Half the boss (x -5..-4.5)
is inside the helmet shell on purpose; the buried east face is painted anyway, as antennae warned.

**`!` lines accepted: none.** The finished part reports zero problems and one `-` note: *"pair
spans 18.49 across the figure, over the 18 the shoulders span"*. That is the point of antennae -
mirrored, they reach a quarter unit wider than the shoulders each side, which is what makes the
silhouette read from three metres, and it is well under `antlers` (24.8) on the same socket.

**Two `armorpieces_paint` calls, 24 master faces + 12 pixels and 12 mask faces + 12 pixels, and
they covered everything.** Master: `*.*` 100, then the boss (145 base, 205 up, `[170,120]` on the
outboard `west` face, `[150,100]` front/back, 78 down, 92 on the buried inboard `east`) and a flat
per-face set per segment stepping lighter root to tip (78 / 112 / 152 on the sides, 100 / 140 /
186 up, 60 / 86 / 118 down), with **255 on `shaft3.west`** - the tip end cap is exactly one texel,
so that face *is* the brief's bright tip. Zero unpainted faces, no stray paint, greyscale
confirmed by Pillow (master 50 texels, 42..255; inlay 34 texels, 42..255, all inside the
silhouette). What the painter did **not** cover: `[top, bottom]` pairs are useless on the
segments - a 2.25x1.0 cube unwraps to faces one texel tall - so the whole segment story is carried
by the per-segment step, and the joint rings had to go in as the `pixels` list. Deriving which
texel column is the *inboard* end of a face is not printed anywhere: the box-UV strip runs
east -> north -> west -> south, so `north` runs +x to -x (inboard column = the face's first x) and
`south` runs back the other way (inboard column = its LAST x); `up` shares north's direction,
`down` follows it. That gave the 12 ring texels (x 19/22/25 on seg1, 27/29/31 on seg2, 33/35/37 on
seg3), and the front screenshot confirmed the dark bands sit on the joints. The inlay mask mirrors
the master's segment values and rings and leaves the boss unpainted, so the socket keeps the
helmet's metal while the three segments take the dye - as every shipped mask does, shaded rather
than flat.

**Two ways to lose the entire workspace, both hit in this session.** All eight open tabs (including
another session's unsaved `nasal`) vanished twice, `armorpieces_pieces` reporting `open: none`,
after these calls:
- `add_group` with a **UUID** as `parent` throws `Cannot read properties of undefined (reading
  'initEdit')` and takes the project with it. Pass the parent bone's **name**.
- naming a bone `root`: `parent: "root"` and `place_cube`'s `group: "root"` both resolve to the
  scene root, not to your bone, so the cube lands outside `part` ("1 cube(s) outside the part
  group") and the group lands beside `reference`; cleaning that up is what led to the crash above.
  **`root` is a reserved name - call the anchor bone `base`.**
By name, both `add_group parent:` and `place_cube group:` work fine, and the piece re-opens from
disk with the starter cube back, so nothing was lost but time. Also: `list_outline` returning
`counts: 0` and `armorpieces_check` answering "No piece is open" is the signal that the workspace
died, not that your part is empty.

**For the next part.** `minecraft:fermented_spider_eye` is now taken as a template centre item;
`python -m modpage build --offline` warned it had never been cached, one plain
`python -m modpage build` fetched it and the pages came back `unchanged`, exactly as the last four
sessions found. Do the bridge calls **one per message** when a chain of bones is going in - the
two crashes both followed messages with parallel calls, and a single call gives you the check line
that confirms the previous one. And on `horns`, the brow band is the only neighbour that matters:
everything else on the head bone lives at |x| < 6 or above y 32, so a temple part that starts
above y 30.75 is clear before it is drawn.
