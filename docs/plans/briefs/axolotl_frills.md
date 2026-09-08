# Brief: Axolotl Frills

The first piece of **Armor Pieces: Coral**, a pack that ships outside the mod
(`docs/plans/set-packs.md`, "Pack 2"). It is also the **first part ever authored through the
toolkit's own Blockbench plugin** — read "What is new in the bridge" below before your first call,
because three things every earlier brief warned you about are no longer true.

**Part.** `armorpieces_coral:axolotl_frills`, socket `horns` only. Display name "Axolotl Frills".
**No fittings** — a frill is not hardware, and a dyed axolotl is not an axolotl. No effects, no
loot rows.

Create it with `armorpieces_new` and **name both pack folders and the namespace explicitly**, or it
will be written into the mod:

    name: axolotl_frills
    anchor: horns
    namespace: armorpieces_coral
    datapack: C:\Users\Matthijs\ArmorPieces\packs\coral\datapack
    resourcepack: C:\Users\Matthijs\ArmorPieces\packs\coral\resourcepack

## What is new in the bridge

Blockbench is driven by `mcptoolkit_bridge.js` now, not the third-party plugin the older briefs were
written against. What changed for you:

- **Your piece is BOUND to this session.** `armorpieces_new` opens it and claims it, so every call
  after that goes to *your* piece by name, whatever tab anyone clicks on. There is an unrelated
  `bedroll` project open with unsaved edits — under the old plugin that was a live hazard (a bee's
  bone once landed in a fox); now an edit aimed at it would be refused. Do not go looking for it
  anyway.
- **A bone can be renamed and re-aimed after the fact.** `element op:rename` works on a group, and
  `element op:set {origin, rotation}` moves a bone's pivot and angles. The old advice — "compute the
  pivot and the two angles before you create the bone, because nothing can change them after" — is
  dead. Build the ear upright, look at it, then rotate the bone to taste.
- **Undo is clean.** Undoing a `place_cube` used to leave the cube behind as a ghost outside every
  group. It does not any more.
- **Paint can be cleared.** `texture op:rects` with `c: null` on a rectangle clears those texels and
  says how many it cleared — that is how stray paint from a layout you have since changed goes away.
  `armorpieces_paint` with `value: null` still works too.
- **`inspect` with `faces`** prints the current face rectangles of every cube. After any resize,
  that is the cheapest way to see what the sheet layout now is.
- **One picture, several angles.** `capture_screenshot` takes `fit` to frame the model and a `views`
  list that composes several presets into a single contact sheet — one call and one picture instead
  of an angle and a capture each. Your budget is about six pictures; a contact sheet is one of them.

Please note in the Lessons section whether each of these actually held. That is half of why this
piece is being built now.

## Shape

`horns` is a **mirrored** socket: model ONE side and the pair is made for you.

An axolotl's frills are three feathery gill stalks sweeping back and up from behind the eye — not
horns, not ears, not a fan. They are soft, they taper, and they read at a distance as *three of
something* rather than as a single shape. Suggested build, in Blockbench coordinates, adjusted from
what you see:

- A root bone at the temple, the base sitting **half a texel inside the helmet shell** (the helmet
  reference is the head box inflated by 1), so no face is coplanar with the shell.
- Three stalks from one bone, splayed: the middle one longest and nearly horizontal, one above it
  angled up, one below angled down and shorter. About 4–5 units long each, 1 thick, 1–2 tall,
  tapering to 1×1 at the tip. Fanned across roughly 40° in Z.
- Each stalk is two cubes — a thicker root and a thinner tip — rather than one, so the taper is real
  in silhouette. The feathering itself is **paint**, not geometry: rows of alternating value along
  the stalk's top and bottom faces read as filaments at this scale.
- Rotate the **bone**, never the cubes. If three separate splay angles are wanted, that is three
  child bones under one root bone — and now that `element op:set` can re-aim a bone, place them
  straight first and fan them afterwards while looking at the viewport.
- Stay under the `head_fins`, `aerials` and `ears` envelopes — the reply to `armorpieces_new` lists
  every other `horns` part's envelope in both frames, so place against those numbers rather than
  measuring anything yourself.

## Sheets

A piece has three layers; this one uses two:

- `axolotl_frills.png` — the **master**, greyscale. Its value is a position on the *wearer's trim
  material ramp*, so anything drawn here turns iron, gold or netherite with the armor. Its alpha is
  the silhouette and it is the single source of truth: a static pixel where the master is
  transparent is not drawn.
- `axolotl_frills_static.png` — **RGBA, keeps its own colour**, shaded by the master's value
  underneath. Created by `armorpieces_set_part {static: true}`, which you must call **before**
  painting it.

So: **draw the axolotl in the static layer**, and paint the master with the same shapes in the
greys listed below so shading and colour agree. There is no hardware on this piece, so nothing stays
metal.

The **lucy** (pale pink) axolotl's palette, from `python tools/mob_reference.py axolotl_lucy`:

| hex | share | value | what it is |
|---|---|---|---|
| `#fbc1e3` | 30.2% | 214 | the pale body pink — the lit top of a stalk |
| `#f3add6` | 11.7% | 199 | one step down, for the second row |
| `#e384bc` | 16.8% | 167 | the mid pink — the body of the frills |
| `#c8629e` | 18.8% | 135 | the deep pink — the roots and the underside |
| `#b14283` | 6.7% | 107 | the darkest pink — edges and the filament lines only |
| `#a62d74` | 2.1% | 89 | one accent at most |

**Look at the axolotl once before modelling**: `python tools/mob_reference.py axolotl_lucy --extract`
writes `tools/.mcassets/reference/entity/axolotl/axolotl_lucy@8x.png`, the real texture at eight
times, nearest-neighbour. The gills are on the head net and they show exactly how the game does a
feathered edge in two pixels. That look is your cheapest picture of the session — take it first.

Lucy is the axolotl people picture, and pink is what makes this read as an axolotl rather than as a
generic fin. Five pinks over a taper is the whole job. **Do not** use the blue variant's palette;
`axolotl` with no variant resolves to blue and that is the wrong one.

## Recipe

Centre item `minecraft:axolotl_bucket` — unused by any template in the mod or in either pack. Paper
ring, craftable. The result is the `horns` template.

`armorpieces_new` does **not** write a recipe; it is `armorpieces_set_part` that does, in the same
call as the name and the static layer:

    armorpieces_set_part { name: "Axolotl Frills", static: true,
                           recipe: { centre: "minecraft:axolotl_bucket", craftable: true } }

## Done means

`armorpieces_save` accepted **without** `force`;
`python tools/check_authoring.py packs/coral/datapack packs/coral/resourcepack` clean; the Lessons
section below filled in, including the bridge notes asked for above. Do **not** run the modpage
build — this pack is not on the mod's page. `tools/check_part.py` does not work for an out-of-pack
piece; the bridge's own check, printed after every call, is the check for these.

## Lessons from the session

Built as: one `base` bone at the temple (x=-4.5, half a unit inside the inflate-1 helmet
shell), three child bones `stalk_top` / `stalk_mid` / `stalk_bottom`, each two cubes (root +
tip, tapering 1.8→1.0 tall, 1 thick throughout). Modelled straight (pointing outward on -X, no
rotation) first, then fanned by setting each stalk bone's rotation directly (`Y≈28°` shared,
sweeping all three back toward +Z; `Z` from -25° to +15°, a 40° vertical fan) — no cube was ever
rotated. First pass put the whole cluster at eye height and it hulled deep into `circlet`,
`browband` and `laurel` (brow-socket pieces worn on the same bone); dropping the cluster 2.5
units lower (cheek/jaw height, matching `cheek_guards`/`tusks`) cut that to four small edge
touches, all `-` notes, not `!` problems — accepted as-is, gill stalks brushing a crown's band
is a reasonable trade for a socket that stacks with `brow`. Painted the master in the five
brief-given greys (`*.*` mid pink 167, `up` 214, `down` 135, root north/south a [199,135]
gradient, tip north/south [214,167]), the static layer in the matching hexes, then twelve single
pixels at 107 / `#b14283` on the root segments' north/south faces (alternating columns, bottom
row) for the filament fringe. Checked clean without `force` on the first save.

**The six bridge claims, checked against this session:**

1. *"Your piece is BOUND to this session."* Held. `armorpieces_new` bound it immediately and
   every following call (including plain `mcptoolkit` tools like `place_cube`/`element`) acted on
   `axolotl_frills` with no need to name the project. Never touched the `bedroll` tab.
2. *"A bone can be renamed and re-aimed after the fact."* Held, and was the backbone of the whole
   session. `element op:rename` turned the starter `main` into `base` with no geometry loss;
   `element op:set {origin}`/`{rotation}` was used repeatedly — first to place the four bones,
   then to fan the three stalks, then again to drop the whole cluster 2.5 units when it clashed
   with brow pieces. The "build straight, rotate after, while looking at the numbers" workflow
   the brief describes is real and is a large win over precomputing sines and cosines by hand.
   One nuance worth recording: moving a bone's `origin` alone does **not** move the cubes inside
   it (it only moves the pivot), so repositioning the cluster meant editing all four bone origins
   *and* all six cubes' `from`/`to` by the same delta in one pass — that part is still on the
   author, not the bridge.
3. *"Undo is clean."* Not exercised — nothing in this session needed an undo, so this claim is
   unverified rather than confirmed.
4. *"Paint can be cleared."* Not exercised either — no stray paint ever needed clearing, since
   every resize happened before any painting pass. Also unverified, not refuted.
5. *"`inspect` with `faces` prints the current face rectangles."* Not called directly, but
   equivalent information (the sheet layout, current at all times) rides along on every
   `armorpieces_check` and every `element`/`modify_cube`/`place_cube` reply, which made a
   separate `inspect faces` call unnecessary in practice — the face rectangles used for both
   paint calls came straight from those replies.
6. *"One picture, several angles."* Held. Two `capture_screenshot` calls with a `views` list (one
   after the master paint, one after the static paint) covered every angle needed for this
   session at the cost of two pictures instead of up to six.

Other things worth passing on: the check's "past helmet"/"past body" numbers are per-axis reach
past the shell, not a single clearance figure, and aren't a substitute for reading the actual
`envelope` line and the OVERLAP notes against same-bone, different-socket parts — those overlap
notes are hull tests against a part's full bounding box (e.g. `circlet`'s whole band, `laurel`'s
whole ring), so a small piece near a crown will always show *some* overlap; judge by the numbers
(here, at most ~2×1×2 units against a hull, and only two of the three stalks) rather than
treating any OVERLAP line as disqualifying. The 3D view genuinely is empty (well, showing bare
grey shell) until the master has alpha; do the paint pass before spending a screenshot.
