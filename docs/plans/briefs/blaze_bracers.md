# Brief: Blaze Bracers

A piece of **Armor Pieces: Nether** (`armorpieces_nether`) — netherite with gold hardware, the
dimension worn as a body. This is the **first piece of the pack**: nothing else exists in it yet, so
there are no pack siblings to clear and no house style to match beyond the two sentences below.

From the `vambraces` row of the Nether table:

> `blaze_bracers` — two short rods banded to each forearm — fitting `guard` — centre `magma_cream`.

Everything you need is in this brief. Do not open other briefs, plans or tables.

## What to create

    name:          blaze_bracers
    anchor:        vambraces
    namespace:     armorpieces_nether
    datapack:      C:\Users\Matthijs\ArmorPieces\packs\nether\datapack
    resourcepack:  C:\Users\Matthijs\ArmorPieces\packs\nether\resourcepack

Both pack paths are required. Leaving either out writes the piece into the mod itself, which is
wrong and is not something you can undo from inside Blockbench.

**The piece may already exist.** An earlier run created it and got no further than the empty
starter stub — one bone `main`, one starter cube, nothing painted, no fittings and no recipe. If
`armorpieces_new` says the piece already exists, use **`armorpieces_open`** instead and carry on
from step 3; the stub is exactly what `armorpieces_new` would have given you. Do not treat this as
a problem to report.

Then, before you paint anything:

    armorpieces_set_part { name: "Blaze Bracers",
                           fittings: { guard: { masked: true } },
                           recipe: { centre: "minecraft:magma_cream", craftable: true } }

`minecraft:magma_cream` is confirmed free — no other template recipe uses it.

**Fittings:** one, `guard`, masked. The reply will say a `part_guard` sheet was created; that is
what you paint the mask onto later, and it is why this call comes before painting.
**Static layer:** none. `static_created: false` is correct.
**Effects:** none. **Loot:** none — this piece is had by its recipe only.

So this piece has **two sheets**: the greyscale master `part`, and the greyscale mask `part_guard`.

## The rig, in Blockbench coordinates

`vambraces` is a **mirrored** socket on the forearms: model **one** side — the **negative x** side —
and the game mirrors it to the other arm.

    left arm box            x −8 .. −4    y 12 .. 24    z −2 .. 2
    sleeve shell (+1.0)     x −9 .. −3    y 11 .. 25    z −3 .. 3
    the vambraces anchor    (−6, 16, 0)   ← corrected 2026-09-09; this brief said 18

**Check the anchor before you build.** The reply to `armorpieces_new` prints it. It should read
`(−6, 16, 0)` in Blockbench coordinates — the arm's own x centre, six units below the arm bone's
pivot at `y = 22`. **This brief originally said `18` and was wrong**; the cube coordinates below were
always derived from 16 and are what the piece was built to, which is why the pilot came out correct.
**If it prints anything else, stop and tell me.** Every coordinate below is measured from that
point, and they would all be wrong.

Front is **negative z**. On this side, **`west` is the outboard face** and `north` is the front.

The anchor sits inside the arm, so the band below starts inside the sleeve and comes out through it.
That is correct and expected. What is not correct is a face lying exactly *in* a shell plane —
`x = −9`, `x = −3`, `z = ±3` — because a face in that plane z-fights. Every number below is
deliberately off the round value for that reason; keep them.

## Shape

Two short blaze rods strapped to the outside of the forearm by a single band. The rods are the
piece; the band is what holds them on. It should read as scavenged hardware, not as a gauntlet —
`vambraces` and `buckler` are the armored pieces on this socket and this is deliberately not those.

**This piece has no rotations.** Every bone stays at rotation `0`. Blaze rods stand straight, and
the band lies flat around the arm. If you find yourself computing a sine, you have misread the
brief — stop and re-read it.

- One bone `base` at the anchor. Rename the starter bone `main` to `base`; never name a bone `root`;
  remove the starter cube. If the bone and a cube end up sharing a name, call `list_outline` for the
  uuid rather than addressing by name.
- **The band**, one cube in `base` — the strap around the forearm, standing a little proud of the
  sleeve all the way round:

        x −9.35 .. −2.65     y 16.85 .. 18.15     z −3.35 .. 3.35

  It encloses the arm; the inboard part of it is inside the sleeve and never seen, which is how
  every band on this socket is built.

- **Two rods**, each its own cube, both in `base`, lying along the **outboard** face — one forward,
  one back, with the band crossing them:

        rod_front    x −9.45 .. −8.65     y 15.15 .. 20.45     z −2.35 .. −0.85
        rod_back     x −9.45 .. −8.65     y 15.15 .. 20.45     z  0.85 ..  2.35

  Both rods are the same size. The gap between them at `z −0.85 .. 0.85` is deliberate: it is where
  the arm shows through.

**Three cubes in total is the budget.** A fourth only if you want a small cap on the rods, and only
if it stays inside the envelope below.

**Envelope budget.** Stay inside `x −9.6 .. −2.5`, `y 15.0 .. 20.6`, `z −3.5 .. 3.5`.

**The same budget in the check's own frame**, so you never have to convert: the check prints the
envelope **bone-local, +Y down, measured from the BONE'S PIVOT** — and the arm's pivot is at
Blockbench `y = 22`, *not* the top of the arm box at 24. In that frame your budget is

    x  −2.5 ..  4.6      y  1.4 .. 7.0      z  −3.5 .. 3.5

Compare the check's envelope line against **those** numbers. Converting the Blockbench ones by hand
is where this goes wrong, and using 24 instead of 22 makes a correct piece look two units out.

That is 0.6 proud of the sleeve at the outboard face and 0.5 at the sides — deliberately modest.
Measured against the six pieces that already occupy this socket, in the anchor's own frame, you are
inside all of them:

| piece | reaches (anchor frame) |
|---|---|
| `vambraces` | x −0.50 .. 4.00, y −2.00 .. 4.00, z −4.00 .. 4.00 |
| `buckler` | x −2.90 .. 3.20, y −2.75 .. 2.75, z −3.35 .. 3.35 |
| `cuffs` | x −3.45 .. 3.45, y −2.40 .. 2.00, z −3.45 .. 3.45 |
| `wraps` | x −2.15 .. 3.49, y −2.20 .. 2.70, z −3.95 .. 3.49 |
| `bangles` | x −3.45 .. 3.45, y −0.38 .. 0.38, z −3.45 .. 3.45 |
| `mittens` | x −2.50 .. 2.50, y 1.25 .. 4.25, z −2.50 .. 2.50 |

**The pair-span rule does not apply on this socket.** On `horns` the check compares the mirrored
pair against the shoulders; the arms are already outboard of the shoulders, so here that comparison
means nothing. Report your envelope; do not try to bring a pair span under 18.

## Paint

Master sheet `part`, greyscale — a value is a position on the trim material's ramp, so think
light/mid/dark, not colour. One `armorpieces_paint` call for the whole sheet.

- **The rods**: banded light and dark down their length, the way a blaze rod is. Give each rod's
  four side faces a `[top, bottom]` pair running from light at the top to mid at the bottom, and
  make the two end faces the lightest value on the piece — those are the hot ends.
- **The band**: flat mid-dark, no gradient, on every face. It is leather; it should sit back and let
  the rods read.

Mask sheet `part_guard`, greyscale — **the band only**. Every face of the band, one flat mid value;
nothing on the rods. That is the whole point of the fitting: the strap takes the player's chosen
guard material and the rods do not.

The 3D view is empty until the master has paint, so paint before your first screenshot.

## Done when

- [ ] The check is clean, or every `!` still standing is one this brief allows.
- [ ] Envelope inside `x −9.6 .. −2.5`, `y 15.0 .. 20.6`, `z −3.5 .. 3.5`, and reported.
- [ ] Both sheets painted: master on everything, `part_guard` on the band only.
- [ ] Saved, and the tab closed.

**Allowed to force:** the band's inboard faces being inside the sleeve, if the check calls them out
as buried or unpainted — that is what a band around an arm is. **Nothing else.** If any other `!`
stands, stop and ask me rather than forcing it.

## Lessons

Built 2026-09-09, on `qwen3.6-flash` at medium effort — the first piece authored by a model other
than Claude, through `qwen -Brief`. It conformed exactly: both cubes' spans, all three cube sizes,
x and z placement, no rotations, and a mask that is the band's 154 texels and nothing else. It saved
with no `!` standing and closed its tab. Two sessions were lost first, both to the bridge and
neither to the brief — see the bridge note below.

1. **A rotation-free first brief was the right pilot.** It isolated "can the format carry a piece
   without the model navigating the project" from "can the model do trigonometry". The first
   question is now answered yes; the second is still open and the next brief should ask it.

2. **The frames are the sharp edge, not the numbers.** This brief gave Blockbench-world
   coordinates; the check answers bone-local from the bone's pivot, and the arm's pivot is at
   `y = 22` rather than the arm box's top at 24. Converting with 24 makes a correct piece look two
   units high — it briefly fooled the reviewer of this very piece. Every brief from here gives the
   envelope budget in **both** frames.

3. **The check validates legality, not conformance.** It has no idea what the brief asked for, so a
   clean check is not evidence the right piece was built. Reading the geometry against the brief is
   a separate step, and it belongs to the follow-up pass.

4. **The bridge, not the model, is what costs sessions.** Both halves of a session must share
   `MCPTK_SESSION`: `tools/mcp/server.mjs` falls back to `mcptk-<parent pid>` while the toolkit's
   `index.mjs` lets the bridge assign it one, so they bind in different windows and the toolkit
   truthfully reports "no project is open". Port pinning alone does not fix it.
