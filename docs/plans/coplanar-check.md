# The coplanar check has two blind spots

> **Status 2026-09-09.** Scoped, not built. Found by looking at `ghast_tendrils` in the editor: it
> z-fought visibly while the check reported `ok: nothing needs a decision`.

## What happened

`ghast_tendrils` has three tendrils of two segments each. Every segment's bone is rotated **about Z
only**, and a Z rotation preserves `z`. The brief gave both segments of a tendril the same z lane, so
each tendril's upper and lower cubes had **identical z extents** — their north and south faces sat in
exactly the same two planes, facing the same way, overlapping across the 0.2 joint. Three tendrils,
six fighting face pairs, and the report said nothing.

The fix to the piece was to inset the lower segments 0.10 per side in z. The fix to the *check* is
this document.

## Blind spot 1 — a rotated bone emits no planes at all

`trace_geometry.py`, in the function that emits each cube's corners and face planes:

```python
axis_aligned = all(abs(r) < EPS for r in rot) and all(
    sum(1 for c in row if abs(c) > EPS) == 1 for row in basis)
...
planes = []
if axis_aligned:
    for a in range(3):
        planes += [(a, min(c[a] for c in corners)), (a, max(c[a] for c in corners))]
```

A cube in a rotated chain contributes an **empty** plane list, so every coplanar test — against a
shell and against another part — is silently skipped for it. The docstring states the reasoning:

> Only unrotated cubes in unrotated chains are checked for coplanarity against a shell, because only
> those have axis-aligned faces that could lie in a shell wall in the first place.

That reasoning is **correct for shells**, which are axis-aligned boxes. It is **wrong for
part-against-part**, where two rotated faces can share a plane perfectly well — and wrong in the
specific case above, where a rotation about one axis leaves the faces perpendicular to that axis
exactly as axis-aligned as they were.

The practical consequence is worse than "some cases are missed": **the check goes quiet precisely
when a piece is aimed**, which is the last thing that happens before it is saved. A session sees
COPLANAR lines during blockout, aims the piece, watches them disappear, and reasonably concludes it
fixed them. `ghast_tendrils`' session said exactly that, and was wrong through no fault of its own.

## Blind spot 2 — a part is never compared against itself

The cross-part pass is documented as *"Interpenetrations and shared planes between this part and its
**bone-mates**"* — every OTHER part on the bone. A part's own cubes are never compared with each
other, so a piece can z-fight against itself with nothing to report it. That is what
`ghast_tendrils` did, and it needs no rotation to happen.

## What to build

Replace the axis-value plane test with an **oriented face test**.

1. **Emit six oriented faces per cube**, always, rotated or not: a centre point, an outward unit
   normal, and the four corners.
2. **Two faces fight** when all of:
   - their normals are parallel and point the **same** way (`n1 · n2 > cos(tol_angle)`); opposed
     normals are two surfaces back to back, which is fine;
   - the perpendicular distance between their planes is under `tol_dist`;
   - their projections onto the shared plane **overlap in area**. Coplanar but disjoint is the
     common, harmless case and must not fire — `hoglin_hair`'s five bristles all share
     `x ±0.55`, and `blaze_halo`'s eight rods all share `z ±0.25`, and neither has ever glitched.
3. **Run it three ways**: part vs its own outer shell (today's behaviour, kept), part vs each
   bone-mate, and **part vs itself**.

### Tolerances

Exact equality is not the bar — two surfaces 0.01 apart still fight at distance, and a rotated face
will rarely be exactly parallel to anything. Suggested starting points, to be calibrated against the
existing library rather than guessed:

- `tol_dist` 0.02 → hard problem, 0.02–0.10 → note. Below 0.02 is certain z-fighting; the band above
  it is "will fight at some camera distances".
- `tol_angle` 2°. Two faces 2° apart still fight along the line where they cross.
- Minimum overlap area 0.05 sq units, to drop corner-touching pairs.

### The migration problem

Turning this on will light up pieces that ship today — 60+ parts, many of them jointed. Before it
can gate a save it needs a triage pass: run it over `--all`, sort by overlap area × closeness, and
decide per case. Expect a large tail of harmless near-coplanar pairs inside a single piece where one
face is fully buried inside another cube — **a buried face cannot fight**, so occlusion has to be
part of the test or the report will be unusable.

That is the real cost of this change, and it is why it is scoped rather than written: the test is
half a day, the calibration is the work.

### Regression cases

| case | expected |
|---|---|
| `ghast_tendrils` as built 2026-09-09 (lower z ±0.57) | **fires** — 6 pairs, ~0.2 × 0.9 each |
| `ghast_tendrils` as fixed (lower z ±0.47) | silent |
| `hoglin_hair` — 5 bristles sharing `x ±0.55` | silent (coplanar, no overlap) |
| `blaze_halo` — 8 rods sharing `z ±0.25` | silent (coplanar, no overlap) |
| `blaze_bracers` band face on the sleeve | unchanged from today |

## Until then

Briefs carry the rule instead, in `TEMPLATE-qwen.md` and the `part-author-qwen` prompt: **a rotation
about an axis preserves that axis, so a chain rotated about Z must taper in z, and a chain rotated
about X must taper in x.** That is a workaround for brief-writing, not a fix — it does nothing for a
piece authored without a brief.
