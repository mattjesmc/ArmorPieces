# Brief: Beast Head

A **re-author**. Beast Head shipped in the part-variety batch and is being built again from
nothing, because the shipped one is the widest part on its socket and reads as a lump rather than a
head. The previous files have been removed; `armorpieces_new` makes it fresh.

This session is also the measurement the mcp-toolkit loop kit is owed (`LOOP_KIT_DESIGN.md` §7
step 6): the first part authored through the kit split rather than through `tools/mcp/server.mjs`
alone, at the model the published per-part figures were taken at. Nothing about the job changes;
the numbers on the way out are the point.

From the `pauldrons` row of `docs/plans/part-variety.md`:

> **Beast Head** — A snarling animal head over each shoulder, jaw forward. Theme: Beast.
> Fitting: `gemstone` (the eyes).

**Part.** `armorpieces:beast_head`, socket `pauldrons` only, in the mod's own pack
(`src/main/resources`, namespace `armorpieces`; `armorpieces_new` puts the master in
`tools/decoration_masters`). Display name "Beast Head". Fittings: `armorpieces:gemstone`, one mask,
the **eyes only** — two small faces, not the whole skull. A static layer if the muzzle or the teeth
want a colour off the material's ramp. No effects, no loot, no recipe: this part is loot-only like
the rest of its batch, so do not set one.

`pauldrons` is a MIRRORED socket. Model ONE side; the game mirrors it.

**Shape.** A snarling head, jaw forward and slightly down, over the shoulder. Bones under `part`:
the skull, a jaw hinged below it, and whatever the look needs — the shipped one used ears and a
scruff and those are worth keeping if they earn their cubes. Under five bones.

**The size is the brief.** The shipped Beast Head reached `x 2.80 .. 6.80` in arm-bone space and
the check said `pair spans 23.60 across the figure (over the 18 the shoulders span)` — nearly three
units proud of the shoulder on each side, wider than every other part on the socket. The others,
from the envelope table `armorpieces_new` prints for you: spaulders `x 0.75 .. 5.33`, lames
`x 2.20 .. 5.85`, spiked_pauldrons `x 2.20 .. 4.85`, wing_cases `x 2.05 .. 6.02`. **Stay inside
about `x 5.5`**, and buy the head's presence in LENGTH and depth (the muzzle forward, the jaw down)
rather than in width. A silhouette that reads at three metres is the test; a wide one just clips
the arm swing.

**Sheets.** Master (greyscale, the ramp): a dark skull with a lighter brow ridge and cheekbone, the
muzzle darker again, the teeth near-white, the inside of the mouth at the bottom of the ramp. Static
layer only if a real colour is needed. Gemstone mask: the two eye faces and nothing else.

**Budget.** Two or three `armorpieces_paint` calls — one per sheet — and no more than six pictures.
Take the first picture where it can still change what you draw and none after the last edit; every
reply that carries one prices it for you.

**Done means.** `armorpieces_save` accepted without `force`; `python tools/check_part.py beast_head`
and `python tools/check_authoring.py` clean from the repository root; the lessons section below
filled in. There is no `modpage.yml` entry and no recipe for this part — leave both alone.

## Lessons from the session

**The shell planes are numbers you can read off the first COPLANAR line.** The very first cube pass
put the cranium's bottom at Blockbench y 25.0 and the check answered `skull's y face at -3 lies on
the chestplate shell`. That one line fixes the whole gauge for a `pauldrons` part: the arm's
chestplate shell is the arm cube inflated by 1, so its planes are Blockbench y 25.0 (top),
x -9.0 (outer) and z ±3.0 (front/back), and bone-local x = -(bb_x) - 5, y = 22 - bb_y. Everything
after that was placed against those four numbers without a second guess — the outer faces went to
-9.85/-10.0 (just past the shell, never on it), the cranium and scruff bottoms to 24.9/24.8 (just
inside it, so the head has no gap under it and no fighting face), and nothing was ever put at
x -9.0. Worth checking the first coplanar report deliberately rather than nudging away from it.

**Width is bought back in the jaw, not the skull.** The shipped part reached local x 6.80 and spanned
23.60. This one reaches x 5.00 and spans 20.00 — narrower than `spaulders` (5.33) and `lames` (5.85)
— while going to z -4.78, a full 1.3 further forward than any other part on the socket, and
Blockbench y 23.80..29.97 (the jaw hangs below the shoulder line, the ears rise above it). The
presence is entirely in the rotated `muzzle` (-8°) and `jaw` (-30°) chain hanging off the front of a
skull that is only 3.5 wide. A rotated bone reaching forward costs nothing on the socket's width
budget, which is the only budget the other pauldrons parts compete for.

**Rotated chains landed to the hundredth from arithmetic alone.** Every bone angle was resolved on
paper first (pivot + length·cos/sin), and the check's `past chestplate z +1.78` matched the
predicted snout tip of z -4.78 exactly. No nudging pass was needed on any of the four bones.

**Teeth are a pixel row, not cubes.** A fang cube at this scale is under half a texel and invisible.
The snarl comes from the master alone: the mouth interior at the bottom of the ramp (30), the muzzle
darker than the skull, and a one-texel light row along the lower edge of `snout.east/west` and the
upper edge of `lower_jaw.east/west`. To taper that row into fangs you need to know which way box UV
runs on a side face: **an east face's u starts at the cube's back (z max) and an west face's u starts
at its front (z min)** — they run in opposite directions, so the front-of-mouth pixel is the last
column on east and the first column on west. Same rule made the nose wrap over `snout.up`, whose v
starts at the back (v = 0) and ends at the front edge.

**A 1×1 face is the right size for a gem eye.** The gemstone mask is four texels total: the outward
side face and the north face of each of two 1×1×0.85 eye bosses that stand 0.15 proud of the skull
and sit under a 0.1 slot of shadow left by the overhanging brow. Fittings do not render in the
Blockbench preview, so the eyes look like dark sockets there and only the mask sheet proves them —
trust the paint report, not the picture.

**Pictures were the expensive part, and three of the five were wasted.** The first two were framed
too wide and too far and told me nothing the check had not; only the straight side profile and the
close three-quarter were worth their tokens, and the head-on view earned its place by showing the
tooth rows reading as a barcode from the front, which is what the final paint pass fixed. Frame the
piece itself (camera ~14 units out, targeted at the part's own centre), not the figure.

**No recipe, and the loot was already there.** `check_authoring.py` reported
`reach beast_head.json: ok (found)` straight after the save with no loot rows on the part: the
`beast` loot group still names it from the previous life of the part, and the group survives the
part's files being deleted. A re-author of a loot-only part needs nothing done about reachability —
but do read that line rather than assuming it.
