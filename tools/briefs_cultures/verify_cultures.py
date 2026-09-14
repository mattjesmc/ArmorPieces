"""Falsify the 48 briefs' own arithmetic before a session sees them (verify_finish.py, extended):

  1. every cube inside the stated Blockbench budget
  2. the check-frame budget is the exact conversion of the Blockbench one
  3. head-bone mirrored pair span under 18
  4. no cube face on a round number
  5. no cube face on any plane a BONE-MATE's cube puts on the same bone - on disk OR a sibling of
     this batch on another socket of the same bone (they will all be on disk by the end)
  6. no cube face on the outermost armor shell plane of the bone
  7. cube names unique; every fit_cube / static cube exists; no cube is both bare and in two lists
  8. same-facing faces within 0.03 inside a piece (a z-fight the check would call `!`)
  9. every piece has at least one static cube (no empty static sheet) and one fitting
 10. sibling hulls of the SAME pack on the same bone do not intersect (the outfit shows them together)
 11. recipe centres unique across the 48 and free against every recipe on disk
"""
import sys, os, re, glob, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "tools")
import gen_cultures as g
from gen_cultures import P, nums, disk_planes, OUTER, CONV, TOL

bad = 0


def hull(p):
    lo = [min(nums(co)[2*a] for _, _, co in p["cubes"]) for a in range(3)]
    hi = [max(nums(co)[2*a+1] for _, _, co in p["cubes"]) for a in range(3)]
    return lo, hi


def overlap(a, b):
    return all(a[0][k] < b[1][k] - 1e-9 and b[0][k] < a[1][k] - 1e-9 for k in range(3))


for p in P:
    ox, py = CONV[p["bone"]]
    names = [nm for nm, _, _ in p["cubes"]]
    if len(set(names)) != len(names):
        print(f"  {p['id']}: duplicate cube names"); bad += 1
    static_cubes = [c for cubes, *_ in p["static"] for c in cubes]
    for c in p["fit_cubes"] + static_cubes:
        if c not in names:
            print(f"  {p['id']}: names cube {c!r} that does not exist"); bad += 1
    if not static_cubes:
        print(f"  {p['id']}: no static cube - the sheet would be empty"); bad += 1
    if not p["fittings"] or not p["fit_cubes"]:
        print(f"  {p['id']}: no fitting / no masked cube"); bad += 1
    planes = [set(s) for s in disk_planes(p["socket"], p["bone"])]
    who = {}
    for q in P:
        if q is p or q["bone"] != p["bone"] or q["socket"] == p["socket"]:
            continue
        for _, _, co in q["cubes"]:
            v = nums(co)
            for ax in range(3):
                planes[ax].add(v[2*ax]); planes[ax].add(v[2*ax+1])
                who[(ax, v[2*ax])] = q["id"]; who[(ax, v[2*ax+1])] = q["id"]
    xs, ys, zs = [], [], []
    for nm, what, co in p["cubes"]:
        v = nums(co)
        xs += v[0:2]; ys += v[2:4]; zs += v[4:6]
        for ax, pair in enumerate((v[0:2], v[2:4], v[4:6])):
            for val in pair:
                if abs(val - round(val)) < 1e-9 and nm != "cloth":
                    print(f"  {p['id']}/{nm}: face on the round number {val}"); bad += 1
                for pv in planes[ax]:
                    if abs(pv - val) < TOL and nm != "cloth":
                        print(f"  {p['id']}/{nm}: {'xyz'[ax]}={val} is on plane {pv} of {who.get((ax, pv), 'a disk piece')}"); bad += 1
                for wall in OUTER[p["bone"]][ax]:
                    if abs(wall - val) < TOL:
                        print(f"  {p['id']}/{nm}: {'xyz'[ax]}={val} is on the outer shell wall {wall}"); bad += 1
    lo = (min(xs), min(ys), min(zs)); hi = (max(xs), max(ys), max(zs))
    b = nums(p["budget_bb"])
    bx, by, bz = (b[0], b[1]), (b[2], b[3]), (b[4], b[5])
    for axis, (a, z), (blo, bhi) in (("x", (lo[0], hi[0]), bx), ("y", (lo[1], hi[1]), by), ("z", (lo[2], hi[2]), bz)):
        if a < blo - 1e-9 or z > bhi + 1e-9:
            print(f"  {p['id']}: cubes span {axis} {a}..{z} but budget says {blo}..{bhi}"); bad += 1
    cx = sorted([ox - bx[0], ox - bx[1]]); cy = sorted([py - by[0], py - by[1]])
    want = [round(v, 2) for v in cx + cy + list(bz)]
    got = [round(v, 2) for v in nums(p["budget_check"])]
    if want != got:
        print(f"  {p['id']}: check budget says {got} but converts to {want}"); bad += 1
    if p["mirrored"] and p["bone"] == "head":
        span = round(2 * max(abs(lo[0]), abs(hi[0])), 2)
        if span > 18:
            print(f"  {p['id']}: pair span {span} exceeds 18"); bad += 1
    cubes = [(nm, nums(co)) for nm, _, co in p["cubes"]]
    for i in range(len(cubes)):
        for j in range(i + 1, len(cubes)):
            a, b_ = cubes[i][1], cubes[j][1]
            for ax in range(3):
                o = [k for k in range(3) if k != ax]
                over = all(a[2*k] < b_[2*k+1] - 1e-9 and b_[2*k] < a[2*k+1] - 1e-9 for k in o)
                if not over:
                    continue
                for side in (0, 1):
                    if abs(a[2*ax+side] - b_[2*ax+side]) < 0.03:
                        print(f"  NOTE {p['id']}: {cubes[i][0]} and {cubes[j][0]} share a same-facing (within 0.03) "
                              f"{'xyz'[ax]}={a[2*ax+side]} face while overlapping")
    print(f"{p['id']:<18} bb x {lo[0]:>7.2f}..{hi[0]:<7.2f} y {lo[1]:>6.2f}..{hi[1]:<6.2f} "
          f"z {lo[2]:>6.2f}..{hi[2]:<6.2f}  {len(p['cubes'])} cubes" +
          (f"   pair {2*max(abs(lo[0]),abs(hi[0])):.2f}" if p["mirrored"] else ""))

print("\n== cubes buried inside the armor shell (never seen) ==")
SHELL = {"head": ((-5, 5), (23, 33), (-5, 5)), "body": ((-5, 5), (11, 25), (-3, 3)),
         "left_arm": ((-9, -3), (11, 25), (-3, 3)),
         "tassets": ((-4.3, 0.5), (-0.4, 12.4), (-2.4, 2.4)), "knees": ((-4.3, 0.5), (-0.4, 12.4), (-2.4, 2.4)),
         "greaves": ((-4.8, 1.0), (-0.9, 12.9), (-2.9, 2.9)), "spurs": ((-4.8, 1.0), (-0.9, 12.9), (-2.9, 2.9))}
for p in P:
    sh = SHELL.get(p["socket"]) or SHELL[p["bone"]]
    for nm, _, co in p["cubes"]:
        v = nums(co)
        if all(sh[a][0] - 1e-9 <= v[2*a] and v[2*a+1] <= sh[a][1] + 1e-9 for a in range(3)):
            print(f"  {p['id']}/{nm} is entirely inside the shell"); bad += 1
        inside = [max(0.0, min(v[2*a+1], sh[a][1]) - max(v[2*a], sh[a][0])) for a in range(3)]
        vol = (v[1]-v[0])*(v[3]-v[2])*(v[5]-v[4])
        if vol and inside[0]*inside[1]*inside[2] / vol > 0.85:
            print(f"  NOTE {p['id']}/{nm}: {inside[0]*inside[1]*inside[2]/vol:.0%} of it is inside the shell")

print("\n== same-pack hull intersections on one bone (the outfit shows these together) ==")
for i, p in enumerate(P):
    for q in P[i+1:]:
        if q["pack"] == p["pack"] and q["bone"] == p["bone"] and q["socket"] != p["socket"]:
            # cube-level, not hull-level: a hull can enclose a gap
            hit = [(a, b) for a, _, ca in p["cubes"] for b, _, cb in q["cubes"]
                   if overlap((nums(ca)[0::2], nums(ca)[1::2]), (nums(cb)[0::2], nums(cb)[1::2]))]
            if hit:
                print(f"  {p['id']} x {q['id']}: {hit}")
                bad += 1

print("\n== recipe centres ==")
used = {}
for f in glob.glob('src/main/resources/data/armorpieces/recipe/*.json') + glob.glob('packs/*/datapack/data/*/recipe/*.json'):
    j = json.load(open(f, encoding='utf-8'))
    if j.get('pattern') == [' # ', '#F#', ' # ']:
        used[j['key']['F']] = os.path.basename(f)[:-5]
seen = collections.defaultdict(list)
for p in P:
    seen[p["centre"]].append(p["id"])
for c, ids in seen.items():
    if len(ids) > 1:
        print(f"  DUPLICATE {c}: {ids}"); bad += 1
    if c in used and used[c] != f"template_{ids[0]}":
        print(f"  COLLIDES {c}: {ids} vs {used[c]}"); bad += 1
print(f"  {len(seen)} centres")

print(f"\n{bad} problem(s)")
sys.exit(1 if bad else 0)
